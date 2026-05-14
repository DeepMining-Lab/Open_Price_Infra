# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH

import pandas as pd
from web3 import Web3
from datetime import datetime, timezone
from mpmath import mp
import os
import sys
import glob
import pytz
import uuid
import hashlib

mp.dps = 50

RPC_URL = os.environ.get("RPC", "")
if not RPC_URL:
    print("ERREUR: la variable d'environnement 'RPC' n'est pas définie.", file=sys.stderr)
    sys.exit(1)

# Uniswap V2 Swap event: Swap(address indexed sender, uint256 amount0In, uint256 amount1In,
#                              uint256 amount0Out, uint256 amount1Out, address indexed to)
EXPECTED_TOPIC0 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"

POOL_ADDRESS    = "0x0d4a11d5EEaaC28EC3F61d100dAF4d40471f1852"
TOKEN0_ADDRESS  = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"  # WETH
TOKEN1_ADDRESS  = "0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT
TOKEN0_DECIMALS = 18  # WETH
TOKEN1_DECIMALS = 6   # USDT
POOL_FEE_TIER   = 3000

SCHEMA_VERSION          = "dex_uniswap_v2_v1"
DEX_PROTOCOL            = "uniswap"
DEX_VERSION             = "v2"
NETWORK_NAME            = "ethereum_mainnet"
RPC_METHOD_USED         = "eth_getLogs+eth_getBlockByNumber+eth_call"
POOL_TVL_THRESHOLD_USED = 10000
BASE_TOKEN_ADDRESS      = TOKEN0_ADDRESS   # WETH
QUOTE_TOKEN_ADDRESS     = TOKEN1_ADDRESS   # USDT
BASE_TOKEN_SYMBOL       = "WETH"
QUOTE_TOKEN_SYMBOL      = "USDT"
PRICE_SOURCE_FIELD      = "amount_ratio"
EVENT_SIGNATURE         = EXPECTED_TOPIC0
SWAP_EVENT_ABI          = '[{"anonymous":false,"inputs":[{"indexed":true,"name":"sender","type":"address"},{"indexed":false,"name":"amount0In","type":"uint256"},{"indexed":false,"name":"amount1In","type":"uint256"},{"indexed":false,"name":"amount0Out","type":"uint256"},{"indexed":false,"name":"amount1Out","type":"uint256"},{"indexed":true,"name":"to","type":"address"}],"name":"Swap","type":"event"}]'
ERC20_SYMBOL_ABI        = [{"name":"symbol","type":"function","inputs":[],"outputs":[{"name":"","type":"string"}],"stateMutability":"view"}]

extraction_run_id        = str(uuid.uuid4())
extraction_timestamp_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S+00:00')
abi_hash                 = hashlib.sha256(SWAP_EVENT_ABI.encode()).hexdigest()
with open(__file__, 'rb') as _f:
    extraction_script_hash = hashlib.sha256(_f.read()).hexdigest()

here = os.path.dirname(__file__)
data_dir = os.path.normpath(os.path.join(here, os.pardir, 'data', 'output'))
pattern = os.path.join(data_dir, '*.csv')
csv_files = glob.glob(pattern)


def get_token_symbol(web3, token_address):
    try:
        c = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_SYMBOL_ABI)
        return c.functions.symbol().call()
    except Exception:
        return "unknown"

def decode_address_topic(topic_hex):
    if not topic_hex or str(topic_hex).lower() in ('', 'nan', 'none'):
        return None
    h = str(topic_hex).replace('0x', '').replace('0X', '')
    return ('0x' + h[-40:]) if len(h) >= 40 else None

def compute_quality_flags(pool_tvl, amount0_raw, amount1_raw, slip_1k, threshold):
    flags = []
    if pool_tvl is not None and pool_tvl < threshold:
        flags.append("low_liquidity")
    if amount0_raw == 0 or amount1_raw == 0:
        flags.append("zero_amount")
    if slip_1k is not None and abs(slip_1k) > 0.05:
        flags.append("extreme_slippage")
    return '|'.join(flags) if flags else "ok"


def decode_swap_event(data_hex):
    try:
        data = data_hex.replace('0x', '')
        amount0In  = int(data[0:64],    16)
        amount1In  = int(data[64:128],  16)
        amount0Out = int(data[128:192], 16)
        amount1Out = int(data[192:256], 16)
        amount0_raw_int = amount0In - amount0Out   # flux net brut token0
        amount1_raw_int = amount1In - amount1Out   # flux net brut token1
        # Signed net flows (positive = into pool)
        net0 = mp.mpf(amount0_raw_int) / 10**TOKEN0_DECIMALS  # WETH
        net1 = mp.mpf(amount1_raw_int) / 10**TOKEN1_DECIMALS  # USDT
        return net0, net1, amount0_raw_int, amount1_raw_int
    except Exception as e:
        print(f"Erreur dans decode_swap_event: {e}")
        print(f"Data hex reçue: {data_hex}")
        raise


def calculate_price(net0_weth, net1_usdt):
    try:
        # token0=WETH, token1=USDT → price = |USDT| / |WETH|
        if net0_weth == 0:
            raise ValueError("WETH amount est zéro")
        price_usdt_per_eth = abs(net1_usdt) / abs(net0_weth)
        volume_usdt = abs(net1_usdt)
        return price_usdt_per_eth, volume_usdt
    except Exception as e:
        print(f"Erreur dans calculate_price: {e}")
        raise


def get_reserves(web3, block_number):
    result = web3.eth.call({'to': POOL_ADDRESS, 'data': '0x0902f1ac'}, block_number)
    h = result.hex()
    reserve0 = int(h[0:64],  16)
    reserve1 = int(h[64:128], 16)
    return reserve0, reserve1


def get_tvl_at_block(web3, block_number, price_usdt_per_eth):
    try:
        reserve0, reserve1 = get_reserves(web3, block_number)
        bal0 = mp.mpf(reserve0) / 10**TOKEN0_DECIMALS  # WETH
        bal1 = mp.mpf(reserve1) / 10**TOKEN1_DECIMALS  # USDT
        return float(bal1 + bal0 * price_usdt_per_eth)
    except Exception as e:
        print(f"Erreur TVL au bloc {block_number}: {e}")
        return None


def get_slip_1k(web3, block_number, price_usdt_per_eth):
    try:
        reserve0, reserve1 = get_reserves(web3, block_number)
        # Simulation: 1 000 USDT → WETH (tokenIn=USDT=token1, tokenOut=WETH=token0)
        amount_in = mp.mpf(1000) * 10**TOKEN1_DECIMALS
        amount_out = (997 * amount_in * reserve0) / (1000 * reserve1 + 997 * amount_in)
        eth_received  = amount_out / 10**TOKEN0_DECIMALS
        expected_eth  = mp.mpf(1000) / price_usdt_per_eth
        return float(1 - eth_received / expected_eth)
    except Exception as e:
        print(f"Erreur slip_1k au bloc {block_number}: {e}")
        return None


def get_slip_10k(web3, block_number, price_usdt_per_eth):
    try:
        reserve0, reserve1 = get_reserves(web3, block_number)
        # Simulation: 10 000 USDT → WETH (tokenIn=USDT=token1, tokenOut=WETH=token0)
        amount_in = mp.mpf(10000) * 10**TOKEN1_DECIMALS
        amount_out = (997 * amount_in * reserve0) / (1000 * reserve1 + 997 * amount_in)
        eth_received  = amount_out / 10**TOKEN0_DECIMALS
        expected_eth  = mp.mpf(10000) / price_usdt_per_eth
        return float(1 - eth_received / expected_eth)
    except Exception as e:
        print(f"Erreur slip_10k au bloc {block_number}: {e}")
        return None


def process_swap_logs(csv_path, web3):
    try:
        print(f"Lecture du fichier: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"Nombre de lignes: {len(df)}")
        if 'data' not in df.columns:
            print("Erreur: colonne 'data' absente du CSV")
            return pd.DataFrame()

        df = df.sort_values(["block_number", "log_index"], ignore_index=True)
        chain_id_rpc = web3.eth.chain_id

        node_head_block_at_extraction = web3.eth.block_number
        sync_status = web3.eth.syncing
        node_sync_completion_block = node_head_block_at_extraction if sync_status is False else sync_status.get('currentBlock', node_head_block_at_extraction)
        try:
            _cv = web3.client_version.split('/')
            client_name = _cv[0]
            client_version_str = _cv[1] if len(_cv) > 1 else "unknown"
        except Exception:
            client_name = "unknown"
            client_version_str = "unknown"
        token0_symbol = get_token_symbol(web3, TOKEN0_ADDRESS)
        token1_symbol = get_token_symbol(web3, TOKEN1_ADDRESS)

        block_numbers = list(set(df['block_number'].tolist()))
        blocks = {}
        for bn in block_numbers:
            try:
                block = web3.eth.get_block(bn)
                blocks[bn] = (datetime.fromtimestamp(block['timestamp'], tz=pytz.UTC), block['hash'].hex())
            except Exception as e:
                print(f"Erreur bloc {bn}: {e}")
                blocks[bn] = (None, None)

        rows = []
        block_last_price = {}
        total_rows = len(df)
        for index, row in df.iterrows():
            try:
                print(f"Traitement ligne {index + 1}/{total_rows}")
                if row['topic0'] != EXPECTED_TOPIC0:
                    continue
                log_address = str(row.get("address", "")).lower()
                if log_address and log_address != POOL_ADDRESS.lower():
                    continue
                net0_weth, net1_usdt, amount0_raw, amount1_raw = decode_swap_event(row['data'])
                price, volume = calculate_price(net0_weth, net1_usdt)
                block_info = blocks.get(row['block_number'])
                if not block_info or not block_info[0]:
                    continue
                timestamp, block_hash = block_info
                bn = row['block_number']
                block_last_price[bn] = price

                swap_direction = "token0_to_token1" if amount0_raw > 0 else "token1_to_token0"
                swap_sender    = decode_address_topic(row.get('topic1'))
                swap_recipient = decode_address_topic(row.get('topic2'))

                rows.append({
                    'timestamp':           timestamp,
                    'price_usdt_per_eth':  price,
                    'eth_amount':          net0_weth,
                    'usdt_amount':         net1_usdt,
                    'volume_usdt':         volume,
                    'block_number':        bn,
                    'transaction_hash':    row['transaction_hash'],
                    'log_index':           row.get('log_index'),
                    'pool_address':        row.get('address', POOL_ADDRESS),
                    'pool_fee_tier':       POOL_FEE_TIER,
                    'chain_id':            row.get('chain_id', chain_id_rpc),
                    # --- Nouveaux champs metadata extraction ---
                    'extraction_run_id':              extraction_run_id,
                    'schema_version':                 SCHEMA_VERSION,
                    'extraction_timestamp_utc':       extraction_timestamp_utc,
                    'client_name':                    client_name,
                    'client_version':                 client_version_str,
                    'node_chain_id':                  chain_id_rpc,
                    'node_head_block_at_extraction':  node_head_block_at_extraction,
                    'node_sync_completion_block':     node_sync_completion_block,
                    'rpc_method_used':                RPC_METHOD_USED,
                    'extraction_script_hash':         extraction_script_hash,
                    'abi_hash':                       abi_hash,
                    'network_name':                   NETWORK_NAME,
                    # --- Nouveaux champs bloc/transaction ---
                    'block_timestamp_utc':            str(timestamp),
                    'block_hash':                     block_hash,
                    'transaction_index':              row.get('transaction_index'),
                    'event_signature':                EVENT_SIGNATURE,
                    # --- Nouveaux champs DEX ---
                    'dex_protocol':                   DEX_PROTOCOL,
                    'dex_version':                    DEX_VERSION,
                    'token0_address':                 TOKEN0_ADDRESS,
                    'token1_address':                 TOKEN1_ADDRESS,
                    'token0_symbol':                  token0_symbol,
                    'token1_symbol':                  token1_symbol,
                    'token0_decimals':                TOKEN0_DECIMALS,
                    'token1_decimals':                TOKEN1_DECIMALS,
                    'amount0_raw':                    amount0_raw,
                    'amount1_raw':                    amount1_raw,
                    'amount0_normalized':             float(mp.mpf(amount0_raw) / 10**TOKEN0_DECIMALS),
                    'amount1_normalized':             float(mp.mpf(amount1_raw) / 10**TOKEN1_DECIMALS),
                    'swap_sender':                    swap_sender,
                    'swap_recipient':                 swap_recipient,
                    'swap_direction':                 swap_direction,
                    'base_token_address':             BASE_TOKEN_ADDRESS,
                    'quote_token_address':            QUOTE_TOKEN_ADDRESS,
                    'base_token_symbol':              BASE_TOKEN_SYMBOL,
                    'quote_token_symbol':             QUOTE_TOKEN_SYMBOL,
                    'price_source_field':             PRICE_SOURCE_FIELD,
                    'pool_tvl_threshold_used':        POOL_TVL_THRESHOLD_USED,
                })
            except Exception as e:
                print(f"Erreur ligne {index}: {e}")
                continue

        if not rows:
            print("Aucun prix valide collecté")
            return pd.DataFrame()

        unique_blocks = list(block_last_price.keys())
        print(f"\nCal réserves, TVL et slip_1k pour {len(unique_blocks)} blocs uniques...")
        reserve_cache = {}
        tvl_cache     = {}
        slip_cache    = {}
        slip10k_cache = {}
        for bn in unique_blocks:
            price_ref = block_last_price[bn]
            try:
                r0, r1 = get_reserves(web3, bn)
                reserve_cache[bn] = (r0, r1)
            except Exception as e:
                print(f"Erreur réserves bloc {bn}: {e}")
                reserve_cache[bn] = (None, None)
            tvl_cache[bn]     = get_tvl_at_block(web3, bn, price_ref)
            slip_cache[bn]    = get_slip_1k(web3, bn, price_ref)
            slip10k_cache[bn] = get_slip_10k(web3, bn, price_ref)
        for r in rows:
            bn = r['block_number']
            r0, r1 = reserve_cache.get(bn, (None, None))
            r['reserve0']          = r0
            r['reserve1']          = r1
            r['pool_tvl_at_block'] = tvl_cache.get(bn)
            r['slip_1k']           = slip_cache.get(bn)
            r['slip_10k']          = slip10k_cache.get(bn)
            r['quality_flags']     = compute_quality_flags(
                r['pool_tvl_at_block'], r['amount0_raw'], r['amount1_raw'],
                r['slip_1k'], POOL_TVL_THRESHOLD_USED
            )

        result_df = pd.DataFrame(rows)
        print(f"\nDataFrame créé avec {len(result_df)} lignes")
        print(result_df['price_usdt_per_eth'].describe())
        return result_df
    except Exception as e:
        print(f"Erreur générale: {e}")
        return pd.DataFrame()


def main(output_filename='weth_usdt_uniswap_v2_03_last.csv'):
    if not csv_files:
        print("Aucun fichier CSV trouvé dans le dossier 'output'")
        return None
    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not web3.is_connected():
        print(f"ERREUR: impossible de se connecter à '{RPC_URL}'", file=sys.stderr)
        sys.exit(1)
    all_prices = pd.DataFrame()
    for csv_file in csv_files:
        prices = process_swap_logs(csv_file, web3)
        if not prices.empty:
            all_prices = pd.concat([all_prices, prices])
    if all_prices.empty:
        print("Aucune donnée traitée.")
        return None
    here2 = os.path.dirname(__file__)
    data_dir2 = os.path.normpath(os.path.join(here2, os.pardir, 'data'))
    output_path = os.path.join(data_dir2, output_filename)
    all_prices = all_prices.sort_values("timestamp").reset_index(drop=True)
    all_prices.to_csv(output_path, index=False)
    print(f"\nFichier CSV créé: {output_path}")
    return all_prices


if __name__ == "__main__":
    main()

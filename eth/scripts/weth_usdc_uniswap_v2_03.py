# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH

import gc
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
from concurrent.futures import ThreadPoolExecutor, as_completed

mp.dps = 50

MAX_WORKERS = 32

RPC_URL = os.environ.get("RPC", "")
if not RPC_URL:
    print("ERREUR: la variable d'environnement 'RPC' n'est pas définie.", file=sys.stderr)
    sys.exit(1)

# Uniswap V2 Swap event: Swap(address indexed sender, uint256 amount0In, uint256 amount1In,
#                              uint256 amount0Out, uint256 amount1Out, address indexed to)
EXPECTED_TOPIC0 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"

POOL_ADDRESS    = "0xb4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"
TOKEN0_ADDRESS  = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  # USDC
TOKEN1_ADDRESS  = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"  # WETH
TOKEN0_DECIMALS = 6   # USDC
TOKEN1_DECIMALS = 18  # WETH
POOL_FEE_TIER   = 3000

SCHEMA_VERSION          = "dex_uniswap_v2_v1"
DEX_PROTOCOL            = "uniswap"
DEX_VERSION             = "v2"
NETWORK_NAME            = "ethereum_mainnet"
RPC_METHOD_USED         = "eth_getLogs+eth_getBlockByNumber+eth_call"
POOL_TVL_THRESHOLD_USED = 10000
BASE_TOKEN_ADDRESS      = TOKEN1_ADDRESS   # WETH
QUOTE_TOKEN_ADDRESS     = TOKEN0_ADDRESS   # USDC
BASE_TOKEN_SYMBOL       = "WETH"
QUOTE_TOKEN_SYMBOL      = "USDC"
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
        amount0_raw_int = amount0In - amount0Out
        amount1_raw_int = amount1In - amount1Out
        net0 = mp.mpf(amount0_raw_int) / 10**TOKEN0_DECIMALS  # USDC
        net1 = mp.mpf(amount1_raw_int) / 10**TOKEN1_DECIMALS  # WETH
        return net0, net1, amount0_raw_int, amount1_raw_int
    except Exception as e:
        print(f"Erreur dans decode_swap_event: {e}")
        print(f"Data hex reçue: {data_hex}")
        raise


def calculate_price(net0_usdc, net1_weth):
    try:
        # token0=USDC, token1=WETH → price = |USDC| / |WETH|
        if net1_weth == 0:
            raise ValueError("WETH amount est zéro")
        price_usdc_per_eth = abs(net0_usdc) / abs(net1_weth)
        volume_usdc = abs(net0_usdc)
        return price_usdc_per_eth, volume_usdc
    except Exception as e:
        print(f"Erreur dans calculate_price: {e}")
        raise


def get_reserves(web3, block_number):
    result = web3.eth.call({'to': POOL_ADDRESS, 'data': '0x0902f1ac'}, block_number)
    h = result.hex()
    reserve0 = int(h[0:64],  16)
    reserve1 = int(h[64:128], 16)
    return reserve0, reserve1


def fetch_block(web3, bn):
    try:
        block = web3.eth.get_block(bn)
        return bn, (datetime.fromtimestamp(block['timestamp'], tz=pytz.UTC), block['hash'].hex())
    except Exception as e:
        print(f"Erreur bloc {bn}: {e}")
        return bn, (None, None)


def get_all_metrics(web3, bn, price_ref):
    # Un seul appel get_reserves pour TVL + slip_1k + slip_10k
    try:
        r0, r1 = get_reserves(web3, bn)  # r0=USDC, r1=WETH

        bal0 = mp.mpf(r0) / 10**TOKEN0_DECIMALS  # USDC
        bal1 = mp.mpf(r1) / 10**TOKEN1_DECIMALS  # WETH
        tvl = float(bal0 + bal1 * price_ref)

        # slip_1k: 1 000 USDC → WETH (tokenIn=USDC=token0, tokenOut=WETH=token1)
        ain_1k  = mp.mpf(1000)  * 10**TOKEN0_DECIMALS
        aout_1k = (997 * ain_1k * r1) / (1000 * r0 + 997 * ain_1k)
        slip1k  = float(1 - (aout_1k / 10**TOKEN1_DECIMALS) / (mp.mpf(1000)  / price_ref))

        # slip_10k: 10 000 USDC → WETH
        ain_10k  = mp.mpf(10000) * 10**TOKEN0_DECIMALS
        aout_10k = (997 * ain_10k * r1) / (1000 * r0 + 997 * ain_10k)
        slip10k  = float(1 - (aout_10k / 10**TOKEN1_DECIMALS) / (mp.mpf(10000) / price_ref))

        return bn, (r0, r1), tvl, slip1k, slip10k
    except Exception as e:
        print(f"Erreur métriques bloc {bn}: {e}")
        return bn, (None, None), None, None, None


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

        # Récupération des blocs en parallèle
        block_numbers = list(set(df['block_number'].tolist()))
        blocks = {}
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(fetch_block, web3, bn): bn for bn in block_numbers}
            for future in as_completed(futures):
                bn, result = future.result()
                blocks[bn] = result

        rows = []
        block_last_price = {}
        for index, row in df.iterrows():
            try:
                if row['topic0'] != EXPECTED_TOPIC0:
                    continue
                log_address = str(row.get("address", "")).lower()
                if log_address and log_address != POOL_ADDRESS.lower():
                    continue
                net0_usdc, net1_weth, amount0_raw, amount1_raw = decode_swap_event(row['data'])
                price, volume = calculate_price(net0_usdc, net1_weth)
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
                    'price_usdc_per_eth':  price,
                    'usdc_amount':         net0_usdc,
                    'eth_amount':          net1_weth,
                    'volume_usdc':         volume,
                    'block_number':        bn,
                    'transaction_hash':    row['transaction_hash'],
                    'log_index':           row.get('log_index'),
                    'pool_address':        row.get('address', POOL_ADDRESS),
                    'pool_fee_tier':       POOL_FEE_TIER,
                    'chain_id':            row.get('chain_id', chain_id_rpc),
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
                    'block_timestamp_utc':            str(timestamp),
                    'block_hash':                     block_hash,
                    'transaction_index':              row.get('transaction_index'),
                    'event_signature':                EVENT_SIGNATURE,
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

        # Calcul réserves + TVL + slip en parallèle (1 seul appel get_reserves par bloc)
        unique_blocks = list(block_last_price.keys())
        print(f"Cal réserves, TVL et slip pour {len(unique_blocks)} blocs uniques (parallèle)...")
        reserve_cache = {}
        tvl_cache     = {}
        slip_cache    = {}
        slip10k_cache = {}
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(get_all_metrics, web3, bn, block_last_price[bn]): bn
                for bn in unique_blocks
            }
            for future in as_completed(futures):
                bn, reserves, tvl, slip1k, slip10k = future.result()
                reserve_cache[bn] = reserves
                tvl_cache[bn]     = tvl
                slip_cache[bn]    = slip1k
                slip10k_cache[bn] = slip10k

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
        print(f"DataFrame créé avec {len(result_df)} lignes")
        print(result_df['price_usdc_per_eth'].describe())
        return result_df
    except Exception as e:
        print(f"Erreur générale: {e}")
        return pd.DataFrame()


def main(output_filename='weth_usdc_uniswap_v2_03_last.csv'):
    if not csv_files:
        print("Aucun fichier CSV trouvé dans le dossier 'output'")
        return None
    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not web3.is_connected():
        print(f"ERREUR: impossible de se connecter à '{RPC_URL}'", file=sys.stderr)
        sys.exit(1)

    here2 = os.path.dirname(__file__)
    data_dir2 = os.path.normpath(os.path.join(here2, os.pardir, 'data'))
    output_path = os.path.join(data_dir2, output_filename)

    total_rows = 0
    first_write = True
    for csv_file in csv_files:
        prices = process_swap_logs(csv_file, web3)
        if not prices.empty:
            prices = prices.sort_values("timestamp").reset_index(drop=True)
            prices.to_csv(output_path, mode='a', header=first_write, index=False)
            total_rows += len(prices)
            first_write = False
        del prices
        gc.collect()

    if total_rows == 0:
        print("Aucune donnée traitée.")
        return None

    print(f"\nFichier CSV créé: {output_path}")
    print(f"Nombre total d'événements traités: {total_rows}")
    return True


if __name__ == "__main__":
    main()

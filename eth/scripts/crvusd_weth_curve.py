# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH
#
# Curve pool crvUSD/WETH — 0x6e5492f8Ea2370844eE098a56dD88e1717E4A9C2
# coin0 = crvUSD (18 dec), coin1 = WETH (18 dec)
# TVL exprimé en crvUSD (≈ USD) : crvUSD_balance + WETH_balance / price_weth_per_crvusd
# slip_1k : achat de WETH avec 1 000 crvUSD via get_dy

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

# Curve TokenExchange(address indexed buyer, int128 sold_id, uint256 tokens_sold,
#                     int128 bought_id, uint256 tokens_bought)
EXPECTED_TOPIC0 = "0x8b3e96f2b889fa771c53c981b40daf005f63f637f1869f707052d15a3dd97140"

POOL_ADDRESS    = "0x6e5492f8Ea2370844eE098a56dD88e1717E4A9C2"
TOKEN0_ADDRESS  = "0xf939E0A03FB07F59A73314E73794Be0E57ac1b4E"  # crvUSD
TOKEN1_ADDRESS  = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"  # WETH
TOKEN0_DECIMALS = 18  # crvUSD
TOKEN1_DECIMALS = 18  # WETH

GET_DY_ABI = [
    {
        "name": "get_dy",
        "type": "function",
        "inputs": [
            {"name": "i", "type": "int128"},
            {"name": "j", "type": "int128"},
            {"name": "dx", "type": "uint256"},
        ],
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
    }
]

SCHEMA_VERSION          = "dex_curve_v1"
DEX_PROTOCOL            = "curve"
DEX_VERSION             = ""
NETWORK_NAME            = "ethereum_mainnet"
RPC_METHOD_USED         = "eth_getLogs+eth_getBlockByNumber+eth_call"
POOL_TVL_THRESHOLD_USED = 10000
BASE_TOKEN_ADDRESS      = TOKEN0_ADDRESS   # crvUSD
QUOTE_TOKEN_ADDRESS     = TOKEN1_ADDRESS   # WETH
BASE_TOKEN_SYMBOL       = "crvUSD"
QUOTE_TOKEN_SYMBOL      = "WETH"
PRICE_SOURCE_FIELD      = "amount_ratio"
EVENT_SIGNATURE         = EXPECTED_TOPIC0
SWAP_EVENT_ABI          = '[{"name":"TokenExchange","inputs":[{"name":"buyer","type":"address","indexed":true},{"name":"sold_id","type":"int128","indexed":false},{"name":"tokens_sold","type":"uint256","indexed":false},{"name":"bought_id","type":"int128","indexed":false},{"name":"tokens_bought","type":"uint256","indexed":false}],"anonymous":false,"type":"event"}]'
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
        sold_id       = int.from_bytes(bytes.fromhex(data[0:64]),   byteorder='big', signed=True)
        tokens_sold   = int(data[64:128],  16)
        bought_id     = int.from_bytes(bytes.fromhex(data[128:192]), byteorder='big', signed=True)
        tokens_bought = int(data[192:256], 16)

        sold_dec  = mp.mpf(tokens_sold)   / 10**TOKEN0_DECIMALS
        bought_dec = mp.mpf(tokens_bought) / 10**TOKEN1_DECIMALS

        if sold_id == 0:
            # crvUSD sold → WETH bought
            crvusd_amount   = sold_dec
            weth_amount     = -bought_dec
            amount0_raw_int =  int(tokens_sold)
            amount1_raw_int = -int(tokens_bought)
        else:
            # WETH sold → crvUSD bought
            crvusd_amount   = -bought_dec
            weth_amount     =  sold_dec
            amount0_raw_int = -int(tokens_bought)
            amount1_raw_int =  int(tokens_sold)

        return crvusd_amount, weth_amount, sold_id, tokens_sold, tokens_bought, amount0_raw_int, amount1_raw_int
    except Exception as e:
        print(f"Erreur dans decode_swap_event: {e}")
        print(f"Data hex reçue: {data_hex}")
        raise


def calculate_price(crvusd_amount, weth_amount):
    try:
        if weth_amount == 0:
            raise ValueError("WETH amount est zéro")
        price_weth_per_crvusd = abs(weth_amount) / abs(crvusd_amount)
        volume_crvusd = abs(crvusd_amount)
        return price_weth_per_crvusd, volume_crvusd
    except Exception as e:
        print(f"Erreur dans calculate_price: {e}")
        raise


def get_balance_of(web3, token_address, holder_address, block_number):
    selector = "0x70a08231"
    padded   = holder_address[2:].lower().zfill(64)
    result   = web3.eth.call({'to': token_address, 'data': selector + padded}, block_number)
    return int(result.hex(), 16)


def fetch_block(web3, bn):
    try:
        block = web3.eth.get_block(bn)
        return bn, (datetime.fromtimestamp(block['timestamp'], tz=pytz.UTC), block['hash'].hex())
    except Exception as e:
        print(f"Erreur bloc {bn}: {e}")
        return bn, (None, None)


def get_all_metrics(web3, bn, price_ref, pool_contract):
    # TVL: 2 balanceOf calls
    try:
        raw0 = get_balance_of(web3, TOKEN0_ADDRESS, POOL_ADDRESS, bn)
        raw1 = get_balance_of(web3, TOKEN1_ADDRESS, POOL_ADDRESS, bn)
        bal0 = mp.mpf(raw0) / 10**TOKEN0_DECIMALS  # crvUSD
        bal1 = mp.mpf(raw1) / 10**TOKEN1_DECIMALS  # WETH
        tvl = float(bal0 + bal1 / price_ref)
    except Exception as e:
        print(f"Erreur TVL bloc {bn}: {e}")
        tvl = None

    # slip_1k: 1 000 crvUSD → WETH via get_dy
    try:
        weth_out_1k = pool_contract.functions.get_dy(0, 1, 1000 * 10**TOKEN0_DECIMALS).call(block_identifier=bn)
        weth_received_1k = mp.mpf(weth_out_1k) / 10**TOKEN1_DECIMALS
        expected_weth_1k = mp.mpf(1000) * price_ref
        slip1k = float(1 - weth_received_1k / expected_weth_1k)
    except Exception as e:
        print(f"Erreur slip_1k bloc {bn}: {e}")
        slip1k = None

    # slip_10k: 10 000 crvUSD → WETH via get_dy
    try:
        weth_out_10k = pool_contract.functions.get_dy(0, 1, 10000 * 10**TOKEN0_DECIMALS).call(block_identifier=bn)
        weth_received_10k = mp.mpf(weth_out_10k) / 10**TOKEN1_DECIMALS
        expected_weth_10k = mp.mpf(10000) * price_ref
        slip10k = float(1 - weth_received_10k / expected_weth_10k)
    except Exception as e:
        print(f"Erreur slip_10k bloc {bn}: {e}")
        slip10k = None

    return bn, tvl, slip1k, slip10k


def process_curve_logs(csv_path, web3, pool_contract):
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
                crvusd_amount, weth_amount, sold_id, tokens_sold, tokens_bought, amount0_raw, amount1_raw = decode_swap_event(row['data'])
                price, volume = calculate_price(crvusd_amount, weth_amount)
                block_info = blocks.get(row['block_number'])
                if not block_info or not block_info[0]:
                    continue
                timestamp, block_hash = block_info
                bn = row['block_number']
                block_last_price[bn] = price

                swap_direction = "token0_to_token1" if sold_id == 0 else "token1_to_token0"
                swap_sender    = decode_address_topic(row.get('topic1'))
                swap_recipient = None  # Curve n'a pas de recipient dans le log

                rows.append({
                    'timestamp':              timestamp,
                    'price_weth_per_crvusd':  price,
                    'crvusd_amount':           crvusd_amount,
                    'weth_amount':             weth_amount,
                    'volume_crvusd':           volume,
                    'block_number':            bn,
                    'transaction_hash':        row['transaction_hash'],
                    'log_index':               row.get('log_index'),
                    'pool_address':            row.get('address', POOL_ADDRESS),
                    'chain_id':                row.get('chain_id', chain_id_rpc),
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

        # Calcul TVL + slip en parallèle (contrat pool réutilisé)
        unique_blocks = list(block_last_price.keys())
        print(f"Cal TVL et slip pour {len(unique_blocks)} blocs uniques (parallèle)...")
        tvl_cache     = {}
        slip_cache    = {}
        slip10k_cache = {}
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(get_all_metrics, web3, bn, block_last_price[bn], pool_contract): bn
                for bn in unique_blocks
            }
            for future in as_completed(futures):
                bn, tvl, slip1k, slip10k = future.result()
                tvl_cache[bn]     = tvl
                slip_cache[bn]    = slip1k
                slip10k_cache[bn] = slip10k

        for r in rows:
            r['pool_tvl_at_block'] = tvl_cache.get(r['block_number'])
            r['slip_1k']           = slip_cache.get(r['block_number'])
            r['slip_10k']          = slip10k_cache.get(r['block_number'])
            r['quality_flags']     = compute_quality_flags(
                r['pool_tvl_at_block'], r['amount0_raw'], r['amount1_raw'],
                r['slip_1k'], POOL_TVL_THRESHOLD_USED
            )

        result_df = pd.DataFrame(rows)
        print(f"DataFrame créé avec {len(result_df)} lignes")
        print(result_df['price_weth_per_crvusd'].describe())
        return result_df
    except Exception as e:
        print(f"Erreur générale: {e}")
        return pd.DataFrame()


def main(output_filename='crvusd_weth_curve_last.csv'):
    if not csv_files:
        print("Aucun fichier CSV trouvé dans le dossier 'output'")
        return None
    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not web3.is_connected():
        print(f"ERREUR: impossible de se connecter à '{RPC_URL}'", file=sys.stderr)
        sys.exit(1)

    # Contrat pool créé une seule fois et réutilisé pour tous les batchs
    pool_contract = web3.eth.contract(
        address=Web3.to_checksum_address(POOL_ADDRESS),
        abi=GET_DY_ABI,
    )

    here2 = os.path.dirname(__file__)
    data_dir2 = os.path.normpath(os.path.join(here2, os.pardir, 'data'))
    output_path = os.path.join(data_dir2, output_filename)

    total_rows = 0
    first_write = True
    for csv_file in csv_files:
        prices = process_curve_logs(csv_file, web3, pool_contract)
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

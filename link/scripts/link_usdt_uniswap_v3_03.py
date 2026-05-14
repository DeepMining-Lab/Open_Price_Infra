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

EXPECTED_TOPIC0 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"

POOL_ADDRESS    = "0xac5A2c404EbBa22A869998089Ac7893fF4E1F0A7"
TOKEN0_ADDRESS  = "0x514910771AF9Ca656af840dff83E8264EcF986CA"  # LINK
TOKEN1_ADDRESS  = "0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT
TOKEN0_DECIMALS = 18  # LINK
TOKEN1_DECIMALS = 6   # USDT
POOL_FEE_TIER   = 3000

QUOTER_V2_ADDRESS = "0x61fFE014bA17989E743c5F6cB21bF9697530B21e"
QUOTER_V2_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"name": "tokenIn",          "type": "address"},
                    {"name": "tokenOut",         "type": "address"},
                    {"name": "amountIn",         "type": "uint256"},
                    {"name": "fee",              "type": "uint24"},
                    {"name": "sqrtPriceLimitX96","type": "uint160"},
                ],
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "quoteExactInputSingle",
        "outputs": [
            {"name": "amountOut",               "type": "uint256"},
            {"name": "sqrtPriceX96After",       "type": "uint160"},
            {"name": "initializedTicksCrossed", "type": "uint32"},
            {"name": "gasEstimate",             "type": "uint256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]

SWAP_EVENT_ABI = '[{"anonymous":false,"inputs":[{"indexed":true,"name":"sender","type":"address"},{"indexed":true,"name":"recipient","type":"address"},{"indexed":false,"name":"amount0","type":"int256"},{"indexed":false,"name":"amount1","type":"int256"},{"indexed":false,"name":"sqrtPriceX96","type":"uint160"},{"indexed":false,"name":"liquidity","type":"uint128"},{"indexed":false,"name":"tick","type":"int24"}],"name":"Swap","type":"event"}]'

SCHEMA_VERSION          = "dex_uniswap_v3_v1"
DEX_PROTOCOL            = "uniswap"
DEX_VERSION             = "v3"
BASE_TOKEN_ADDRESS      = TOKEN0_ADDRESS
QUOTE_TOKEN_ADDRESS     = TOKEN1_ADDRESS
BASE_TOKEN_SYMBOL       = "LINK"
QUOTE_TOKEN_SYMBOL      = "USDT"
PRICE_SOURCE_FIELD      = "sqrt_price_x96"

NETWORK_NAME            = "ethereum_mainnet"
RPC_METHOD_USED         = "eth_getLogs+eth_getBlockByNumber+eth_call"
POOL_TVL_THRESHOLD_USED = 10000
EVENT_SIGNATURE         = EXPECTED_TOPIC0
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
        amount0      = int.from_bytes(bytes.fromhex(data[0:64]),    byteorder='big', signed=True)
        amount1      = int.from_bytes(bytes.fromhex(data[64:128]),  byteorder='big', signed=True)
        sqrtPriceX96 = int(data[128:192], 16)
        liquidity    = int(data[192:256], 16)
        tick         = int.from_bytes(bytes.fromhex(data[256:320]), byteorder='big', signed=True)
        link_amount  = mp.mpf(amount0) / 10**TOKEN0_DECIMALS
        usdt_amount  = mp.mpf(amount1) / 10**TOKEN1_DECIMALS
        return usdt_amount, link_amount, sqrtPriceX96, liquidity, tick, amount0, amount1
    except Exception as e:
        print(f"Erreur dans decode_swap_event: {e}")
        print(f"Data hex reçue: {data_hex}")
        raise


def calculate_price(sqrtPriceX96, link_amount, usdt_amount):
    try:
        sqrt_price = mp.mpf(sqrtPriceX96) / (2 ** 96)
        # LINK est token0, USDT est token1 → prix = sqrtP² × 1e12
        price_usdt_per_link = sqrt_price ** 2 * mp.mpf("1e12")
        volume_usdt = abs(usdt_amount)
        return price_usdt_per_link, volume_usdt
    except Exception as e:
        print(f"Erreur dans calculate_price: {e}")
        raise


def get_balance_of(web3, token_address, holder_address, block_number):
    selector = "0x70a08231"
    padded   = holder_address[2:].lower().zfill(64)
    result   = web3.eth.call({'to': token_address, 'data': selector + padded}, block_number)
    return int(result.hex(), 16)


def get_tvl_at_block(web3, block_number, price_usdt_per_link):
    try:
        raw0 = get_balance_of(web3, TOKEN0_ADDRESS, POOL_ADDRESS, block_number)
        raw1 = get_balance_of(web3, TOKEN1_ADDRESS, POOL_ADDRESS, block_number)
        bal0 = mp.mpf(raw0) / 10**TOKEN0_DECIMALS  # LINK, valorisé en USD
        bal1 = mp.mpf(raw1) / 10**TOKEN1_DECIMALS  # USDT ≈ 1 USD
        return float(bal1 + bal0 * price_usdt_per_link)
    except Exception as e:
        print(f"Erreur TVL au bloc {block_number}: {e}")
        return None


def get_slip_1k(web3, block_number, price_usdt_per_link):
    try:
        quoter    = web3.eth.contract(address=Web3.to_checksum_address(QUOTER_V2_ADDRESS), abi=QUOTER_V2_ABI)
        amount_in = 1000 * 10**TOKEN1_DECIMALS
        result    = quoter.functions.quoteExactInputSingle({
            'tokenIn':           Web3.to_checksum_address(TOKEN1_ADDRESS),
            'tokenOut':          Web3.to_checksum_address(TOKEN0_ADDRESS),
            'amountIn':          amount_in,
            'fee':               POOL_FEE_TIER,
            'sqrtPriceLimitX96': 0,
        }).call(block_identifier=block_number)
        link_received = mp.mpf(result[0]) / 10**TOKEN0_DECIMALS
        expected_link = mp.mpf(1000) / price_usdt_per_link
        return float(1 - link_received / expected_link)
    except Exception as e:
        print(f"Erreur slip_1k au bloc {block_number}: {e}")
        return None


def get_slip_10k(web3, block_number, price_usdt_per_link):
    try:
        quoter    = web3.eth.contract(address=Web3.to_checksum_address(QUOTER_V2_ADDRESS), abi=QUOTER_V2_ABI)
        amount_in = 10000 * 10**TOKEN1_DECIMALS  # 10 000 USDT en unités brutes
        result    = quoter.functions.quoteExactInputSingle({
            'tokenIn':           Web3.to_checksum_address(TOKEN1_ADDRESS),
            'tokenOut':          Web3.to_checksum_address(TOKEN0_ADDRESS),
            'amountIn':          amount_in,
            'fee':               POOL_FEE_TIER,
            'sqrtPriceLimitX96': 0,
        }).call(block_identifier=block_number)
        link_received = mp.mpf(result[0]) / 10**TOKEN0_DECIMALS
        expected_link = mp.mpf(10000) / price_usdt_per_link
        return float(1 - link_received / expected_link)
    except Exception as e:
        print(f"Erreur slip_10k au bloc {block_number}: {e}")
        return None


def process_uniswap_logs(csv_path, web3):
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
                usdt_amount, link_amount, sqrtPriceX96, liquidity, tick, amount0_raw, amount1_raw = decode_swap_event(row['data'])
                price, volume = calculate_price(sqrtPriceX96, link_amount, usdt_amount)

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
                    'price_usdt_per_link': price,
                    'usdt_amount':         usdt_amount,
                    'link_amount':         link_amount,
                    'volume_usdt':         volume,
                    'block_number':        bn,
                    'transaction_hash':    row['transaction_hash'],
                    'log_index':           row.get('log_index'),
                    'pool_address':        row.get('address', POOL_ADDRESS),
                    'pool_fee_tier':       POOL_FEE_TIER,
                    'chain_id':            row.get('chain_id', chain_id_rpc),
                    'sqrt_price_x96':      sqrtPriceX96,
                    'liquidity':           liquidity,
                    'tick':                tick,
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

        unique_blocks = list(block_last_price.keys())
        print(f"\nCal TVL, slip_1k et slip_10k pour {len(unique_blocks)} blocs uniques...")
        tvl_cache     = {}
        slip_cache    = {}
        slip10k_cache = {}
        for bn in unique_blocks:
            price_ref = block_last_price[bn]
            tvl_cache[bn]     = get_tvl_at_block(web3, bn, price_ref)
            slip_cache[bn]    = get_slip_1k(web3, bn, price_ref)
            slip10k_cache[bn] = get_slip_10k(web3, bn, price_ref)
        for r in rows:
            r['pool_tvl_at_block'] = tvl_cache.get(r['block_number'])
            r['slip_1k']           = slip_cache.get(r['block_number'])
            r['slip_10k']          = slip10k_cache.get(r['block_number'])
            r['quality_flags']     = compute_quality_flags(
                r['pool_tvl_at_block'], r['amount0_raw'], r['amount1_raw'],
                r['slip_1k'], POOL_TVL_THRESHOLD_USED
            )

        result_df = pd.DataFrame(rows)
        print(f"\nDataFrame créé avec {len(result_df)} lignes")
        print(result_df['price_usdt_per_link'].describe())
        return result_df
    except Exception as e:
        print(f"Erreur générale: {e}")
        return pd.DataFrame()


def main(output_filename='link_usdt_uniswap_v3_03_last.csv'):
    if not csv_files:
        print("Aucun fichier CSV trouvé dans le dossier 'output'")
        return None
    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not web3.is_connected():
        print(f"ERREUR: impossible de se connecter à '{RPC_URL}'", file=sys.stderr)
        sys.exit(1)
    all_prices = pd.DataFrame()
    for csv_file in csv_files:
        prices = process_uniswap_logs(csv_file, web3)
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

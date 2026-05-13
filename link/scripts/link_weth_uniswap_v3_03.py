# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH

import pandas as pd
from web3 import Web3
from datetime import datetime
from mpmath import mp
import os
import sys
import glob
import pytz

mp.dps = 50

RPC_URL = os.environ.get("RPC", "")
if not RPC_URL:
    print("ERREUR: la variable d'environnement 'RPC' n'est pas définie.", file=sys.stderr)
    sys.exit(1)

EXPECTED_TOPIC0 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"

POOL_ADDRESS    = "0xa6CC3C2531Fdaa6Ae1A3CA84c2855806728693e8"
TOKEN0_ADDRESS  = "0x514910771AF9Ca656af840dff83E8264EcF986CA"  # LINK
TOKEN1_ADDRESS  = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"  # WETH
TOKEN0_DECIMALS = 18  # LINK
TOKEN1_DECIMALS = 18  # WETH
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

here = os.path.dirname(__file__)
data_dir = os.path.normpath(os.path.join(here, os.pardir, 'data', 'output'))
pattern = os.path.join(data_dir, '*.csv')
csv_files = glob.glob(pattern)


def decode_swap_event(data_hex):
    try:
        data = data_hex.replace('0x', '')
        amount0      = int.from_bytes(bytes.fromhex(data[0:64]),    byteorder='big', signed=True)
        amount1      = int.from_bytes(bytes.fromhex(data[64:128]),  byteorder='big', signed=True)
        sqrtPriceX96 = int(data[128:192], 16)
        liquidity    = int(data[192:256], 16)
        tick         = int.from_bytes(bytes.fromhex(data[256:320]), byteorder='big', signed=True)
        link_amount  = mp.mpf(amount0) / 10**TOKEN0_DECIMALS
        weth_amount  = mp.mpf(amount1) / 10**TOKEN1_DECIMALS
        return weth_amount, link_amount, sqrtPriceX96, liquidity, tick
    except Exception as e:
        print(f"Erreur dans decode_swap_event: {e}")
        print(f"Data hex reçue: {data_hex}")
        raise


def calculate_price(sqrtPriceX96, link_amount, weth_amount):
    try:
        sqrt_price = mp.mpf(sqrtPriceX96) / (2 ** 96)
        # LINK est token0, WETH est token1 → prix = sqrtP² (les deux à 18 dec)
        price_weth_per_link = sqrt_price ** 2
        volume_weth = abs(weth_amount)
        return price_weth_per_link, volume_weth
    except Exception as e:
        print(f"Erreur dans calculate_price: {e}")
        raise


def get_balance_of(web3, token_address, holder_address, block_number):
    selector = "0x70a08231"
    padded   = holder_address[2:].lower().zfill(64)
    result   = web3.eth.call({'to': token_address, 'data': selector + padded}, block_number)
    return int(result.hex(), 16)


def get_tvl_at_block(web3, block_number, price_weth_per_link):
    try:
        raw0 = get_balance_of(web3, TOKEN0_ADDRESS, POOL_ADDRESS, block_number)
        raw1 = get_balance_of(web3, TOKEN1_ADDRESS, POOL_ADDRESS, block_number)
        bal0 = mp.mpf(raw0) / 10**TOKEN0_DECIMALS  # LINK
        bal1 = mp.mpf(raw1) / 10**TOKEN1_DECIMALS  # WETH
        # TVL exprimé en WETH
        return float(bal1 + bal0 * price_weth_per_link)
    except Exception as e:
        print(f"Erreur TVL au bloc {block_number}: {e}")
        return None


def get_slip_1k(web3, block_number, price_weth_per_link):
    try:
        quoter    = web3.eth.contract(address=Web3.to_checksum_address(QUOTER_V2_ADDRESS), abi=QUOTER_V2_ABI)
        # Simulation d'un achat de LINK avec 1 WETH
        amount_in = 1 * 10**TOKEN1_DECIMALS
        result    = quoter.functions.quoteExactInputSingle({
            'tokenIn':           Web3.to_checksum_address(TOKEN1_ADDRESS),
            'tokenOut':          Web3.to_checksum_address(TOKEN0_ADDRESS),
            'amountIn':          amount_in,
            'fee':               POOL_FEE_TIER,
            'sqrtPriceLimitX96': 0,
        }).call(block_identifier=block_number)
        link_received = mp.mpf(result[0]) / 10**TOKEN0_DECIMALS
        expected_link = mp.mpf(1) / price_weth_per_link
        return float(1 - link_received / expected_link)
    except Exception as e:
        print(f"Erreur slip_1k au bloc {block_number}: {e}")
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
        block_numbers = list(set(df['block_number'].tolist()))
        blocks = {}
        for bn in block_numbers:
            try:
                block = web3.eth.get_block(bn)
                blocks[bn] = datetime.fromtimestamp(block['timestamp'], tz=pytz.UTC)
            except Exception as e:
                print(f"Erreur bloc {bn}: {e}")
                blocks[bn] = None

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
                weth_amount, link_amount, sqrtPriceX96, liquidity, tick = decode_swap_event(row['data'])
                price, volume = calculate_price(sqrtPriceX96, link_amount, weth_amount)
                timestamp = blocks.get(row['block_number'])
                if not timestamp:
                    continue
                bn = row['block_number']
                block_last_price[bn] = price
                rows.append({
                    'timestamp':          timestamp,
                    'price_weth_per_link': price,
                    'weth_amount':         weth_amount,
                    'link_amount':         link_amount,
                    'volume_weth':         volume,
                    'block_number':        bn,
                    'transaction_hash':    row['transaction_hash'],
                    'log_index':           row.get('log_index'),
                    'pool_address':        row.get('address', POOL_ADDRESS),
                    'pool_fee_tier':       POOL_FEE_TIER,
                    'chain_id':            row.get('chain_id', chain_id_rpc),
                    'sqrt_price_x96':      sqrtPriceX96,
                    'liquidity':           liquidity,
                    'tick':                tick,
                })
            except Exception as e:
                print(f"Erreur ligne {index}: {e}")
                continue

        if not rows:
            print("Aucun prix valide collecté")
            return pd.DataFrame()

        unique_blocks = list(block_last_price.keys())
        print(f"\nCal TVL et slip_1k pour {len(unique_blocks)} blocs uniques...")
        tvl_cache  = {}
        slip_cache = {}
        for bn in unique_blocks:
            price_ref = block_last_price[bn]
            tvl_cache[bn]  = get_tvl_at_block(web3, bn, price_ref)
            slip_cache[bn] = get_slip_1k(web3, bn, price_ref)
        for r in rows:
            r['pool_tvl_at_block'] = tvl_cache.get(r['block_number'])
            r['slip_1k']           = slip_cache.get(r['block_number'])

        result_df = pd.DataFrame(rows)
        print(f"\nDataFrame créé avec {len(result_df)} lignes")
        print(result_df['price_weth_per_link'].describe())
        return result_df
    except Exception as e:
        print(f"Erreur générale: {e}")
        return pd.DataFrame()


def main(output_filename='link_weth_uniswap_v3_03_last.csv'):
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

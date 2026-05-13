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

# Uniswap V2 Swap event: Swap(address indexed sender, uint256 amount0In, uint256 amount1In,
#                              uint256 amount0Out, uint256 amount1Out, address indexed to)
EXPECTED_TOPIC0 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"

POOL_ADDRESS    = "0xb4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"
TOKEN0_ADDRESS  = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  # USDC
TOKEN1_ADDRESS  = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"  # WETH
TOKEN0_DECIMALS = 6   # USDC
TOKEN1_DECIMALS = 18  # WETH
POOL_FEE_TIER   = 3000

here = os.path.dirname(__file__)
data_dir = os.path.normpath(os.path.join(here, os.pardir, 'data', 'output'))
pattern = os.path.join(data_dir, '*.csv')
csv_files = glob.glob(pattern)


def decode_swap_event(data_hex):
    try:
        data = data_hex.replace('0x', '')
        amount0In  = int(data[0:64],    16)
        amount1In  = int(data[64:128],  16)
        amount0Out = int(data[128:192], 16)
        amount1Out = int(data[192:256], 16)
        # Signed net flows (positive = into pool)
        net0 = mp.mpf(amount0In - amount0Out) / 10**TOKEN0_DECIMALS  # USDC
        net1 = mp.mpf(amount1In - amount1Out) / 10**TOKEN1_DECIMALS  # WETH
        return net0, net1
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


def get_tvl_at_block(web3, block_number, price_usdc_per_eth):
    try:
        reserve0, reserve1 = get_reserves(web3, block_number)
        bal0 = mp.mpf(reserve0) / 10**TOKEN0_DECIMALS  # USDC
        bal1 = mp.mpf(reserve1) / 10**TOKEN1_DECIMALS  # WETH
        return float(bal0 + bal1 * price_usdc_per_eth)
    except Exception as e:
        print(f"Erreur TVL au bloc {block_number}: {e}")
        return None


def get_slip_1k(web3, block_number, price_usdc_per_eth):
    try:
        reserve0, reserve1 = get_reserves(web3, block_number)
        # Simulation: 1 000 USDC → WETH (tokenIn=USDC=token0, tokenOut=WETH=token1)
        amount_in = mp.mpf(1000) * 10**TOKEN0_DECIMALS
        amount_out = (997 * amount_in * reserve1) / (1000 * reserve0 + 997 * amount_in)
        eth_received  = amount_out / 10**TOKEN1_DECIMALS
        expected_eth  = mp.mpf(1000) / price_usdc_per_eth
        return float(1 - eth_received / expected_eth)
    except Exception as e:
        print(f"Erreur slip_1k au bloc {block_number}: {e}")
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
                net0_usdc, net1_weth = decode_swap_event(row['data'])
                price, volume = calculate_price(net0_usdc, net1_weth)
                timestamp = blocks.get(row['block_number'])
                if not timestamp:
                    continue
                bn = row['block_number']
                block_last_price[bn] = price
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
        for bn in unique_blocks:
            price_ref = block_last_price[bn]
            try:
                r0, r1 = get_reserves(web3, bn)
                reserve_cache[bn] = (r0, r1)
            except Exception as e:
                print(f"Erreur réserves bloc {bn}: {e}")
                reserve_cache[bn] = (None, None)
            tvl_cache[bn]  = get_tvl_at_block(web3, bn, price_ref)
            slip_cache[bn] = get_slip_1k(web3, bn, price_ref)
        for r in rows:
            bn = r['block_number']
            r0, r1 = reserve_cache.get(bn, (None, None))
            r['reserve0']          = r0
            r['reserve1']          = r1
            r['pool_tvl_at_block'] = tvl_cache.get(bn)
            r['slip_1k']           = slip_cache.get(bn)

        result_df = pd.DataFrame(rows)
        print(f"\nDataFrame créé avec {len(result_df)} lignes")
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

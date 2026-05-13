# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH
#
# Curve pool crvUSD/WETH — 0x6e5492f8Ea2370844eE098a56dD88e1717E4A9C2
# coin0 = crvUSD (18 dec), coin1 = WETH (18 dec)
# TVL exprimé en crvUSD (≈ USD) : crvUSD_balance + WETH_balance / price_weth_per_crvusd
# slip_1k : achat de WETH avec 1 000 crvUSD via get_dy

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

here = os.path.dirname(__file__)
data_dir = os.path.normpath(os.path.join(here, os.pardir, 'data', 'output'))
pattern = os.path.join(data_dir, '*.csv')
csv_files = glob.glob(pattern)


def decode_swap_event(data_hex):
    try:
        # data layout: sold_id (32 bytes), tokens_sold (32 bytes),
        #              bought_id (32 bytes), tokens_bought (32 bytes)
        data = data_hex.replace('0x', '')
        sold_id      = int.from_bytes(bytes.fromhex(data[0:64]),   byteorder='big', signed=True)
        tokens_sold  = int(data[64:128],  16)
        bought_id    = int.from_bytes(bytes.fromhex(data[128:192]), byteorder='big', signed=True)
        tokens_bought = int(data[192:256], 16)

        sold_dec  = mp.mpf(tokens_sold)  / 10**TOKEN0_DECIMALS
        bought_dec = mp.mpf(tokens_bought) / 10**TOKEN1_DECIMALS

        if sold_id == 0:
            # crvUSD sold → WETH bought
            crvusd_amount = sold_dec
            weth_amount   = -bought_dec
        else:
            # WETH sold → crvUSD bought
            crvusd_amount = -bought_dec
            weth_amount   = sold_dec

        return crvusd_amount, weth_amount, sold_id, tokens_sold, tokens_bought
    except Exception as e:
        print(f"Erreur dans decode_swap_event: {e}")
        print(f"Data hex reçue: {data_hex}")
        raise


def calculate_price(crvusd_amount, weth_amount):
    try:
        if weth_amount == 0:
            raise ValueError("WETH amount est zéro")
        # price_weth_per_crvusd = WETH out / crvUSD in (ou inverse selon le sens)
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


def get_tvl_at_block(web3, block_number, price_weth_per_crvusd):
    try:
        raw0 = get_balance_of(web3, TOKEN0_ADDRESS, POOL_ADDRESS, block_number)
        raw1 = get_balance_of(web3, TOKEN1_ADDRESS, POOL_ADDRESS, block_number)
        bal0 = mp.mpf(raw0) / 10**TOKEN0_DECIMALS  # crvUSD
        bal1 = mp.mpf(raw1) / 10**TOKEN1_DECIMALS  # WETH
        # TVL en crvUSD (≈ USD) : WETH converti via le prix
        return float(bal0 + bal1 / price_weth_per_crvusd)
    except Exception as e:
        print(f"Erreur TVL au bloc {block_number}: {e}")
        return None


def get_slip_1k(web3, block_number, price_weth_per_crvusd):
    try:
        pool = web3.eth.contract(
            address=Web3.to_checksum_address(POOL_ADDRESS), abi=GET_DY_ABI
        )
        # Simulation: 1 000 crvUSD → WETH (i=0 → j=1)
        amount_in = 1000 * 10**TOKEN0_DECIMALS
        weth_out_raw = pool.functions.get_dy(0, 1, amount_in).call(
            block_identifier=block_number
        )
        weth_received = mp.mpf(weth_out_raw) / 10**TOKEN1_DECIMALS
        expected_weth = mp.mpf(1000) * price_weth_per_crvusd
        return float(1 - weth_received / expected_weth)
    except Exception as e:
        print(f"Erreur slip_1k au bloc {block_number}: {e}")
        return None


def process_curve_logs(csv_path, web3):
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
                crvusd_amount, weth_amount, sold_id, tokens_sold, tokens_bought = decode_swap_event(row['data'])
                price, volume = calculate_price(crvusd_amount, weth_amount)
                timestamp = blocks.get(row['block_number'])
                if not timestamp:
                    continue
                bn = row['block_number']
                block_last_price[bn] = price
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
    all_prices = pd.DataFrame()
    for csv_file in csv_files:
        prices = process_curve_logs(csv_file, web3)
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

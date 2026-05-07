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

here = os.path.dirname(__file__)
data_dir = os.path.normpath(os.path.join(here, os.pardir, 'data', 'output'))
pattern = os.path.join(data_dir, '*.csv')
csv_files = glob.glob(pattern)


def decode_swap_event(data_hex):
    try:
        data = data_hex.replace('0x', '')
        amount0_hex    = data[0:64]
        amount1_hex    = data[64:128]
        sqrtPriceX96_hex = data[128:192]
        amount0 = int.from_bytes(bytes.fromhex(amount0_hex), byteorder='big', signed=True)
        amount1 = int.from_bytes(bytes.fromhex(amount1_hex), byteorder='big', signed=True)
        sqrtPriceX96 = int(sqrtPriceX96_hex, 16)
                link_amount = mp.mpf(amount0) / 10**18   # LINK a 18 décimales (token0)
        usdc_amount  = mp.mpf(amount1) / 10**6    # USDC a 6 décimales (token1)
        return usdc_amount, link_amount, sqrtPriceX96
    except Exception as e:
        print(f"Erreur dans decode_swap_event: {e}")
        print(f"Data hex reçue: {data_hex}")
        raise


def calculate_price(sqrtPriceX96, link_amount, usdc_amount):
    try:
                sqrtPriceX96 = mp.mpf(sqrtPriceX96)
        sqrt_price = sqrtPriceX96 / (2 ** 96)
        # sqrtP = sqrt(USDC_raw / LINK_raw) → price_usdc_per_link_raw = sqrt_price²
        # Ajustement décimales : LINK=18 dec, USDC=6 dec → ×1e12
        price_usdc_per_link = sqrt_price ** 2 * mp.mpf("1e12")
        volume_usdc = abs(usdc_amount) + abs(link_amount * price_usdc_per_link)
        return price_usdc_per_link, volume_usdc
    except Exception as e:
        print(f"Erreur dans calculate_price: {e}")
        raise


def process_uniswap_logs(csv_path, web3):
    try:
        print(f"Lecture du fichier: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"Nombre de lignes dans le CSV: {len(df)}")
        print("Colonnes disponibles:", df.columns.tolist())

        if 'data' not in df.columns:
            print("Erreur: La colonne 'data' n'existe pas dans le CSV")
            return pd.DataFrame()

        usdc_amounts = []
        link_amounts = []
        timestamps = []
        prices = []
        volumes = []
        processed_block_numbers = []
        tx_hashes = []

        block_numbers = list(set(df['block_number'].tolist()))
        print(f"Nombre de blocs uniques à récupérer : {len(block_numbers)}")

        blocks = {}
        for bn in block_numbers:
            try:
                block = web3.eth.get_block(bn)
                blocks[bn] = datetime.fromtimestamp(block['timestamp'], tz=pytz.UTC)
            except Exception as e:
                print(f"Erreur sur le bloc {bn} : {e}")
                blocks[bn] = None

        total_rows = len(df)
        for index, row in df.iterrows():
            try:
                print(f"\nTraitement de la ligne {index + 1}/{total_rows}")
                if row['topic0'] != EXPECTED_TOPIC0:
                    print("Signature ne correspond pas à un event Swap.")
                    continue
                usdc_amount, link_amount, sqrtPriceX96 = decode_swap_event(row['data'])
                price, volume = calculate_price(sqrtPriceX96, link_amount, usdc_amount)
                timestamp = blocks.get(row['block_number'])
                if timestamp:
                    usdc_amounts.append(usdc_amount)
                    link_amounts.append(link_amount)
                    volumes.append(volume)
                    timestamps.append(timestamp)
                    prices.append(price)
                    processed_block_numbers.append(row['block_number'])
                    tx_hashes.append(row['transaction_hash'])
            except Exception as e:
                print(f"Erreur ligne {index}: {e}")
                continue

        print(f"\nNombre de prix valides collectés: {len(prices)}")
        if len(prices) == 0:
            print("Aucun prix valide collecté")
            return pd.DataFrame()

        result_df = pd.DataFrame({
            'timestamp':             timestamps,
            'price_usdc_per_link':  prices,
            'usdc_amount':           usdc_amounts,
            'link_amount':          link_amounts,
            'volume_usdc':           volumes,
            'block_number':          processed_block_numbers,
            'transaction_hash':      tx_hashes
        })

        print(f"DataFrame créé avec {len(result_df)} lignes")
        print("\nAperçu des prix:")
        print(result_df['price_usdc_per_link'].describe())
        return result_df

    except Exception as e:
        print(f"Erreur générale dans process_uniswap_logs: {e}")
        return pd.DataFrame()


def main(output_filename='uniswap_link_usd_last.csv'):
    if not csv_files:
        print("Aucun fichier CSV trouvé dans le dossier 'output'")
        return None

    print(f"Fichiers CSV trouvés: {len(csv_files)}")
    for f in csv_files:
        print(f"- {f}")

    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not web3.is_connected():
        print(f"ERREUR: impossible de se connecter à '{RPC_URL}'", file=sys.stderr)
        sys.exit(1)
    print(f"Connexion au réseau établie: {web3.is_connected()}")

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

    all_prices.to_csv(output_path, index=False)
    print(f"\nFichier CSV créé: {output_path}")
    print(f"Nombre total d'événements traités: {len(all_prices)}")
    return all_prices


if __name__ == "__main__":
    main()

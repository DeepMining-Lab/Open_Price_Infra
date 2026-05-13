# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH

import csv
import time
import argparse
import os
import sys
from web3 import Web3
from datetime import datetime, timezone

parser = argparse.ArgumentParser(description="Timestamp de début.")
parser.add_argument(
    "--debut",
    type=int,
    required=True,
    help="Timestamp UNIX de début (ex. 1744610424)."
)
args = parser.parse_args()

RPC_URL = os.environ.get("RPC", "")
if not RPC_URL:
    print("ERREUR: la variable d'environnement 'RPC' n'est pas définie.", file=sys.stderr)
    sys.exit(1)

CONTRACT_ADDRESS = '0x3E7d1eAB13ad0104d2750B8863b489D65364e32D'  # Chainlink USDT/USD
FILENAME = "data/chainlink_usdt_usd_last.csv"

TIMESTAMP_DEBUT = args.debut
TIMESTAMP_FIN   = int(time.time())

if TIMESTAMP_DEBUT > TIMESTAMP_FIN:
    parser.error("Le paramètre --debut doit être inférieur ou égal au timestamp actuel !")

def convertir_timestamp(ts: int) -> str:
    if ts == 0:
        return "Invalid round (ts=0)"
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S+00:00')

def to_round_id(phase: int, aggregator_id: int) -> int:
    return (phase << 64) | aggregator_id

def parse_round_id(round_id: int) -> (int, int):
    phase_id = round_id >> 64
    aggregator_id = round_id & 0xFFFFFFFFFFFFFFFF
    return phase_id, aggregator_id

def find_max_aggregator_id(phase: int) -> int:
    low = 1
    high = 1
    while True:
        round_id = to_round_id(phase, high)
        try:
            rd = contract.functions.getRoundData(round_id).call()
            if rd[3] != 0:
                low = high
                high *= 2
            else:
                break
        except:
            break
    max_agg = 0
    while low <= high:
        mid = (low + high) // 2
        round_id = to_round_id(phase, mid)
        try:
            rd = contract.functions.getRoundData(round_id).call()
            if rd[3] != 0:
                max_agg = mid
                low = mid + 1
            else:
                high = mid - 1
        except:
            high = mid - 1
    return max_agg

def find_first_aggregator_id(phase: int, max_agg_id: int, target_ts: int) -> int:
    low, high, result = 1, max_agg_id, None
    while low <= high:
        mid = (low + high) // 2
        round_id = to_round_id(phase, mid)
        try:
            rd = contract.functions.getRoundData(round_id).call()
            updated_at = rd[3]
            if updated_at >= target_ts:
                result = mid
                high = mid - 1
            else:
                low = mid + 1
        except:
            high = mid - 1
    return result

def find_last_aggregator_id(phase: int, max_agg_id: int, target_ts: int) -> int:
    low, high, result = 1, max_agg_id, None
    while low <= high:
        mid = (low + high) // 2
        round_id = to_round_id(phase, mid)
        try:
            rd = contract.functions.getRoundData(round_id).call()
            updated_at = rd[3]
            if updated_at <= target_ts:
                result = mid
                low = mid + 1
            else:
                high = mid - 1
        except:
            high = mid - 1
    return result

web3 = Web3(Web3.HTTPProvider(RPC_URL))

if not web3.is_connected():
    print(f"ERREUR: impossible de se connecter à l'endpoint RPC '{RPC_URL}'", file=sys.stderr)
    sys.exit(1)

print(f"Connexion au réseau établie: {web3.is_connected()}")

checksum_addr = Web3.to_checksum_address(CONTRACT_ADDRESS)

abi = '''[
  {"inputs":[],"name":"latestRoundData","outputs":[
    {"internalType":"uint80","name":"roundId","type":"uint80"},
    {"internalType":"int256","name":"answer","type":"int256"},
    {"internalType":"uint256","name":"startedAt","type":"uint256"},
    {"internalType":"uint256","name":"updatedAt","type":"uint256"},
    {"internalType":"uint80","name":"answeredInRound","type":"uint80"}
  ],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],
   "name":"getRoundData","outputs":[
     {"internalType":"uint80","name":"roundId","type":"uint80"},
     {"internalType":"int256","name":"answer","type":"int256"},
     {"internalType":"uint256","name":"startedAt","type":"uint256"},
     {"internalType":"uint256","name":"updatedAt","type":"uint256"},
     {"internalType":"uint80","name":"answeredInRound","type":"uint80"}
   ],"stateMutability":"view","type":"function"}
]'''

contract = web3.eth.contract(address=checksum_addr, abi=abi)

def is_in_range(ts: int, start_ts, end_ts) -> bool:
    if ts == 0:
        return False
    if start_ts is not None and ts < start_ts:
        return False
    if end_ts is not None and ts > end_ts:
        return False
    return True

latest_data = contract.functions.latestRoundData().call()
latest_round_id = latest_data[0]
latest_phase, latest_aggregator_id = parse_round_id(latest_round_id)

print(f"Latest Round ID global: {latest_round_id}")
print(f" - phaseId = {latest_phase}")
print(f" - aggregatorRoundId = {latest_aggregator_id}")

all_results = []

for phase in range(1, latest_phase + 1):
    max_agg_id = find_max_aggregator_id(phase)

    if max_agg_id == 0:
        print(f"Phase {phase} ignorée (aucun round valide)")
        continue

    first_agg = find_first_aggregator_id(phase, max_agg_id, TIMESTAMP_DEBUT)
    last_agg = find_last_aggregator_id(phase, max_agg_id, TIMESTAMP_FIN)

    if not first_agg or not last_agg or first_agg > last_agg:
        print(f"Phase {phase} hors plage temporelle")
        continue

    aggregator_id = first_agg
    while aggregator_id <= last_agg:
        round_id_global = to_round_id(phase, aggregator_id)
        try:
            rd = contract.functions.getRoundData(round_id_global).call()
            answer = rd[1]
            updated_at = rd[3]
            if is_in_range(updated_at, TIMESTAMP_DEBUT, TIMESTAMP_FIN):
                date_str = convertir_timestamp(updated_at)
                price = float(answer) / 1e8
                all_results.append({
                    "round_id_global": round_id_global,
                    "phase_id": phase,
                    "aggregator_round_id": aggregator_id,
                    "price": price,
                    "timestamp": updated_at,
                    "date_str": date_str
                })
                aggregator_id += 1
        except Exception as e:
            print(f"Erreur sur {round_id_global}: {str(e)}")
            break

    print(f"Fin de la phase {phase}, aggregator_round_id max = {aggregator_id - 1}")

all_results.sort(key=lambda x: x["timestamp"])

with open(FILENAME, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["global_round_id", "phase", "aggregator_round", "datetime_utc", "price"])
    for item in all_results:
        writer.writerow([
            item["round_id_global"],
            item["phase_id"],
            item["aggregator_round_id"],
            item["date_str"],
            item["price"]
        ])

print(f"\nTerminé. {len(all_results)} lignes écrites dans {FILENAME}.")

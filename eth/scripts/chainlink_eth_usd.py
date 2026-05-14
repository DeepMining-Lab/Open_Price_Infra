# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH

import csv
import hashlib
import uuid
import time
import argparse
import os
import sys
from web3 import Web3
from datetime import datetime, timezone

parser = argparse.ArgumentParser(description="Timestamp de début.")
parser.add_argument("--debut", type=int, required=True, help="Timestamp UNIX de début.")
args = parser.parse_args()

RPC_URL = os.environ.get("RPC", "")
if not RPC_URL:
    print("ERREUR: la variable d'environnement 'RPC' n'est pas définie.", file=sys.stderr)
    sys.exit(1)

CONTRACT_ADDRESS        = '0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419'
FILENAME                = "data/chainlink_eth_usd_last.csv"
BASE_ASSET              = "ETH"
QUOTE_ASSET             = "USD"
NETWORK_NAME            = "ethereum_mainnet"
HEARTBEAT_SECONDS       = 3600
DEVIATION_THRESHOLD_BPS = 50
SCHEMA_VERSION          = "chainlink_price_feed_v1"
RPC_METHOD_USED         = "eth_call:getRoundData"

TIMESTAMP_DEBUT = args.debut
TIMESTAMP_FIN   = int(time.time())

if TIMESTAMP_DEBUT > TIMESTAMP_FIN:
    parser.error("Le paramètre --debut doit être inférieur ou égal au timestamp actuel !")

extraction_run_id        = str(uuid.uuid4())
extraction_timestamp_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S+00:00')

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

def compute_answer_status(answer_raw: int, answered_in_round: int, round_id_global: int) -> str:
    if answer_raw == 0:
        return "zero_answer"
    if answer_raw < 0:
        return "negative_answer"
    if answered_in_round < round_id_global:
        return "answered_in_old_round"
    return "ok"

web3 = Web3(Web3.HTTPProvider(RPC_URL))
if not web3.is_connected():
    print(f"ERREUR: impossible de se connecter à '{RPC_URL}'", file=sys.stderr)
    sys.exit(1)
print(f"Connexion au réseau établie: {web3.is_connected()}")

node_chain_id              = web3.eth.chain_id
node_head_block_at_extraction = web3.eth.block_number
sync_status                = web3.eth.syncing
node_sync_completion_block = node_head_block_at_extraction if sync_status is False else sync_status.get('currentBlock', node_head_block_at_extraction)

try:
    client_version_raw = web3.client_version
    parts = client_version_raw.split('/')
    client_name    = parts[0] if parts else client_version_raw
    client_version = parts[1] if len(parts) > 1 else "unknown"
except Exception:
    client_name    = "unknown"
    client_version = "unknown"

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
   ],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"uint16","name":"phaseId","type":"uint16"}],"name":"phaseAggregators","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}
]'''

abi_hash = hashlib.sha256(abi.encode()).hexdigest()

with open(__file__, 'rb') as _f:
    extraction_script_hash = hashlib.sha256(_f.read()).hexdigest()

contract = web3.eth.contract(address=checksum_addr, abi=abi)

try:
    feed_decimals = contract.functions.decimals().call()
except Exception:
    feed_decimals = 8

try:
    feed_description = contract.functions.description().call()
except Exception:
    feed_description = "N/A"

try:
    chainlink_version = contract.functions.version().call()
except Exception:
    chainlink_version = "N/A"

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

try:
    aggregator_address = contract.functions.phaseAggregators(latest_phase).call()
except Exception:
    aggregator_address = "N/A"

all_results = []

for phase in range(1, latest_phase + 1):
    max_agg_id = find_max_aggregator_id(phase)
    if max_agg_id == 0:
        print(f"Phase {phase} ignorée (aucun round valide)")
        continue
    first_agg = find_first_aggregator_id(phase, max_agg_id, TIMESTAMP_DEBUT)
    last_agg  = find_last_aggregator_id(phase, max_agg_id, TIMESTAMP_FIN)
    if not first_agg or not last_agg or first_agg > last_agg:
        print(f"Phase {phase} hors plage temporelle")
        continue
    aggregator_id = first_agg
    while aggregator_id <= last_agg:
        round_id_global = to_round_id(phase, aggregator_id)
        try:
            rd = contract.functions.getRoundData(round_id_global).call()
            answer_raw        = rd[1]
            started_at        = rd[2]
            updated_at        = rd[3]
            answered_in_round = rd[4]
            if is_in_range(updated_at, TIMESTAMP_DEBUT, TIMESTAMP_FIN):
                answer_normalized = float(answer_raw) / (10 ** feed_decimals)
                all_results.append({
                    "round_id_global":      round_id_global,
                    "phase_id":             phase,
                    "aggregator_round_id":  aggregator_id,
                    "round_updated_at_utc": convertir_timestamp(updated_at),
                    "answer_normalized":    answer_normalized,
                    "answer_raw":           answer_raw,
                    "answered_in_round":    answered_in_round,
                    "round_started_at_utc": convertir_timestamp(started_at),
                    "answer_status":        compute_answer_status(answer_raw, answered_in_round, round_id_global),
                    "timestamp":            updated_at,
                })
                aggregator_id += 1
        except Exception as e:
            print(f"Erreur sur {round_id_global}: {str(e)}")
            break
    print(f"Fin de la phase {phase}, aggregator_round_id max = {aggregator_id - 1}")

all_results.sort(key=lambda x: x["timestamp"])

COLUMNS = [
    "global_round_id", "phase", "aggregator_round",
    "round_updated_at_utc", "answer_normalized",
    "answer_raw", "answered_in_round", "round_started_at_utc", "answer_status",
    "extraction_run_id", "schema_version", "extraction_timestamp_utc",
    "client_name", "client_version", "node_chain_id", "chain_id",
    "node_head_block_at_extraction", "node_sync_completion_block",
    "rpc_method_used", "extraction_script_hash", "abi_hash",
    "network_name", "feed_proxy_address", "aggregator_address",
    "feed_description", "base_asset", "quote_asset", "feed_decimals",
    "chainlink_version", "heartbeat_seconds", "deviation_threshold_bps",
]

with open(FILENAME, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(COLUMNS)
    for item in all_results:
        writer.writerow([
            item["round_id_global"],
            item["phase_id"],
            item["aggregator_round_id"],
            item["round_updated_at_utc"],
            item["answer_normalized"],
            item["answer_raw"],
            item["answered_in_round"],
            item["round_started_at_utc"],
            item["answer_status"],
            extraction_run_id,
            SCHEMA_VERSION,
            extraction_timestamp_utc,
            client_name,
            client_version,
            node_chain_id,
            node_chain_id,
            node_head_block_at_extraction,
            node_sync_completion_block,
            RPC_METHOD_USED,
            extraction_script_hash,
            abi_hash,
            NETWORK_NAME,
            CONTRACT_ADDRESS,
            aggregator_address,
            feed_description,
            BASE_ASSET,
            QUOTE_ASSET,
            feed_decimals,
            chainlink_version,
            HEARTBEAT_SECONDS,
            DEVIATION_THRESHOLD_BPS,
        ])

print(f"\nTerminé. {len(all_results)} lignes écrites dans {FILENAME}.")

# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH

import csv
import hashlib
import uuid
import time
import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from eth_abi.exceptions import InsufficientDataBytes
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput, ContractLogicError
from datetime import datetime, timezone

parser = argparse.ArgumentParser(description="Timestamp de début.")
parser.add_argument("--debut", type=int, required=True, help="Timestamp UNIX de début.")
args = parser.parse_args()

RPC_URL = os.environ.get("RPC", "")
if not RPC_URL:
    print("ERREUR: la variable d'environnement 'RPC' n'est pas définie.", file=sys.stderr)
    sys.exit(1)

CONTRACT_ADDRESS        = '0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6'
FILENAME                = "data/chainlink_usdc_usd_last.csv"
BASE_ASSET              = "USDC"
QUOTE_ASSET             = "USD"
NETWORK_NAME            = "ethereum_mainnet"
HEARTBEAT_SECONDS       = 86400
DEVIATION_THRESHOLD_BPS = 25
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

# Nombre d'appels getRoundData en parallèle
MAX_WORKERS = 16

# Réponses « pas de donnée » d'un contrat : revert, ou rien à décoder (contrat détruit, fonction absente)
NO_DATA_ERRORS = (ContractLogicError, BadFunctionCallOutput, InsufficientDataBytes)

def call_or_none(fn, block="latest", retries=3):
    """eth_call au bloc `block`. None si le contrat n'a pas de donnée ; les erreurs réseau sont réessayées puis levées."""
    for attempt in range(retries):
        try:
            return fn.call(block_identifier=block)
        except NO_DATA_ERRORS:
            return None
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)

def round_data(phase: int, aggregator_id: int, block="latest"):
    """getRoundData via le proxy ; None si le round n'a pas de donnée (revert ou updatedAt = 0)."""
    rd = call_or_none(contract.functions.getRoundData(to_round_id(phase, aggregator_id)), block)
    return rd if rd is not None and rd[3] != 0 else None

def next_valid_round(phase: int, start: int, stop: int, block):
    """Premier round avec donnée dans [start, stop] : (aggregator_id, données) ou (None, None)."""
    for aggregator_id in range(start, stop + 1):
        rd = round_data(phase, aggregator_id, block)
        if rd is not None:
            return aggregator_id, rd
    return None, None

def find_first_aggregator_id(phase: int, max_agg_id: int, target_ts: int, block) -> int:
    """Plus petit round avec donnée et updatedAt >= target_ts.

    Recherche binaire qui tolère les rounds sans donnée : les premiers rounds d'un agrégateur peuvent
    n'avoir jamais reçu de réponse, donc le round 1 ne dit pas si une phase existe."""
    low, high, result = 1, max_agg_id, None
    while low <= high:
        mid = (low + high) // 2
        agg_id, rd = next_valid_round(phase, mid, high, block)
        if rd is None:
            high = mid - 1
        elif rd[3] >= target_ts:
            result = agg_id
            high = mid - 1
        else:
            low = agg_id + 1
    return result

def aggregator_latest(aggregator_address: str, block="latest"):
    """latestRoundData() de l'agrégateur d'une phase ; None s'il ne répond pas (détruit, jamais alimenté...)."""
    if aggregator_address.lower() == CONTRACT_ADDRESS.lower() or int(aggregator_address, 16) == 0:
        return None  # phase pointée sur le proxy lui-même ou sur l'adresse nulle
    aggregator = web3.eth.contract(address=Web3.to_checksum_address(aggregator_address), abi=AGGREGATOR_ABI)
    rd = call_or_none(aggregator.functions.latestRoundData(), block)
    if rd is None or rd[3] == 0 or not 0 < rd[0] < 2**64:
        return None
    return rd

def first_block_of_phase(phase: int, head: int) -> int:
    """Premier bloc où le proxy sert une phase >= `phase` (recherche binaire sur phaseId())."""
    low, high = 0, head
    while low < high:
        mid = (low + high) // 2
        if (call_or_none(contract.functions.phaseId(), mid) or 0) >= phase:
            high = mid
        else:
            low = mid + 1
    return low

def last_answering_block(aggregator_address: str, low: int, high: int) -> int:
    """Dernier bloc de [low, high] où l'agrégateur répond encore (il répond en `low`)."""
    while low < high:
        mid = (low + high + 1) // 2
        if aggregator_latest(aggregator_address, mid) is not None:
            low = mid
        else:
            high = mid - 1
    return low

def phase_read_block(phase: int, aggregator_address: str, head: int):
    """Bloc auquel lire les rounds d'une ancienne phase.

    'latest' si son agrégateur répond encore. Sinon (agrégateur détruit depuis, ou façade vers un agrégateur
    détruit), le dernier bloc où il répondait : le nœud archive sert l'état passé. None si l'agrégateur ne
    répond même pas à la fin de sa phase (ancien agrégateur sans getRoundData, jamais alimenté...)."""
    if aggregator_latest(aggregator_address) is not None:
        return "latest"
    end = first_block_of_phase(phase + 1, head)
    if end == 0 or aggregator_latest(aggregator_address, end - 1) is None:
        return None
    return last_answering_block(aggregator_address, end - 1, head)

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
  {"inputs":[{"internalType":"uint16","name":"phaseId","type":"uint16"}],"name":"phaseAggregators","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"phaseId","outputs":[{"internalType":"uint16","name":"","type":"uint16"}],"stateMutability":"view","type":"function"}
]'''

# Agrégateur d'une phase, lu directement pour connaître son dernier round
AGGREGATOR_ABI = '''[
  {"inputs":[],"name":"latestRoundData","outputs":[
    {"internalType":"uint80","name":"roundId","type":"uint80"},
    {"internalType":"int256","name":"answer","type":"int256"},
    {"internalType":"uint256","name":"startedAt","type":"uint256"},
    {"internalType":"uint256","name":"updatedAt","type":"uint256"},
    {"internalType":"uint80","name":"answeredInRound","type":"uint80"}
  ],"stateMutability":"view","type":"function"}
]'''

abi_hash = hashlib.sha256((abi + AGGREGATOR_ABI).encode()).hexdigest()

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

all_results = []

for phase in range(1, latest_phase + 1):
    aggregator_address = call_or_none(contract.functions.phaseAggregators(phase)) or "N/A"
    if phase == latest_phase:
        block, max_agg_id = "latest", latest_aggregator_id
    else:
        block = phase_read_block(phase, aggregator_address, node_head_block_at_extraction) if aggregator_address != "N/A" else None
        if block is None:
            print(f"Phase {phase} ignorée (agrégateur {aggregator_address} illisible, même dans le passé)")
            continue
        max_agg_id = aggregator_latest(aggregator_address, block)[0]
    # Rounds après le dernier round répondu : rounds expirés, qui reprennent la réponse d'un round précédent
    while round_data(phase, max_agg_id + 1, block) is not None:
        max_agg_id += 1
    last_rd = round_data(phase, max_agg_id, block)
    first_agg = None
    if last_rd is not None and last_rd[3] >= TIMESTAMP_DEBUT:
        first_agg = find_first_aggregator_id(phase, max_agg_id, TIMESTAMP_DEBUT, block)
    if first_agg is None:
        print(f"Phase {phase} hors plage temporelle")
        continue
    rpc_method_used = RPC_METHOD_USED if block == "latest" else f"{RPC_METHOD_USED}@block:{block}"
    aggregator_ids = range(first_agg, max_agg_id + 1)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        rounds = list(executor.map(lambda a: round_data(phase, a, block), aggregator_ids))
    n_empty = 0
    for aggregator_id, rd in zip(aggregator_ids, rounds):
        if rd is None:
            n_empty += 1
            continue
        answer_raw        = rd[1]
        started_at        = rd[2]
        updated_at        = rd[3]
        answered_in_round = rd[4]
        if not is_in_range(updated_at, TIMESTAMP_DEBUT, TIMESTAMP_FIN):
            continue
        round_id_global = to_round_id(phase, aggregator_id)
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
            "aggregator_address":   aggregator_address,
            "rpc_method_used":      rpc_method_used,
        })
    where = "au dernier bloc" if block == "latest" else f"au bloc {block}"
    print(f"Fin de la phase {phase}: rounds {first_agg}..{max_agg_id} lus {where}, {n_empty} round(s) sans donnée")

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
            item["rpc_method_used"],
            extraction_script_hash,
            abi_hash,
            NETWORK_NAME,
            CONTRACT_ADDRESS,
            item["aggregator_address"],
            feed_description,
            BASE_ASSET,
            QUOTE_ASSET,
            feed_decimals,
            chainlink_version,
            HEARTBEAT_SECONDS,
            DEVIATION_THRESHOLD_BPS,
        ])

print(f"\nTerminé. {len(all_results)} lignes écrites dans {FILENAME}.")

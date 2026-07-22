# Open Price Stablecoins Data Repository
Open Price Stablecoins is an open-data initiative providing standardized, continuously updated historical datasets of USDC/USD and USDT/USD prices from Chainlink on-chain oracles. Fully compliant with FAIR principles, it empowers researchers and developers with transparent, reproducible insights into stablecoin price dynamics.

---

## 📅 Available Datasets

| Dataset                     | End Date Available          | CSV File                          |
|-----------------------------|-----------------------------|-----------------------------------|
| **Chainlink USDC/USD**      | 2026-07-22 08:00:11 UTC       | `data/chainlink_usdc_usd.csv`     |
| **Chainlink USDT/USD**      | 2026-07-21 19:16:35 UTC       | `data/chainlink_usdt_usd.csv`     |

---

## 🗂 CSV Structure: `chainlink_usdc_usd.csv`

**Round identification**

| Column              | Type    | Description                                                    | Method       |
|---------------------|---------|----------------------------------------------------------------|--------------|
| `global_round_id`   | uint80  | Global round identifier (`phase << 64 | aggregator_round_id`) | script-local |
| `phase`             | int     | Chainlink proxy contract phase identifier                      | script-local |
| `aggregator_round`  | int     | Round identifier within the current phase                      | script-local |

**Round data**

| Column                  | Type    | Description                                                                      | Method                                      |
|-------------------------|---------|----------------------------------------------------------------------------------|---------------------------------------------|
| `round_updated_at_utc`  | string  | UTC timestamp when the round was updated (`YYYY-MM-DD HH:MM:SS+00:00`)          | `eth_call:getRoundData` → `updatedAt`       |
| `answer_normalized`     | float   | Price in quote asset: `answer_raw / 10^feed_decimals`                            | computed                                    |
| `answer_raw`            | int256  | Raw answer returned by the Chainlink contract                                    | `eth_call:getRoundData` → `answer`          |
| `answered_in_round`     | uint80  | Round in which the answer was definitively committed                             | `eth_call:getRoundData` → `answeredInRound` |
| `round_started_at_utc`  | string  | UTC timestamp when the round was started (`YYYY-MM-DD HH:MM:SS+00:00`)          | `eth_call:getRoundData` → `startedAt`       |
| `answer_status`         | string  | Computed status: `ok`, `zero_answer`, `negative_answer`, `answered_in_old_round` | computed                                    |

**Extraction metadata**

| Column                           | Type    | Description                                                      | Method                                  |
|----------------------------------|---------|------------------------------------------------------------------|-----------------------------------------|
| `extraction_run_id`              | string  | UUID identifying this extraction run                             | script-local (`uuid4`)                  |
| `schema_version`                 | string  | CSV schema version (e.g. `chainlink_price_feed_v1`)              | config                                  |
| `extraction_timestamp_utc`       | string  | UTC timestamp of extraction start                                | script-local                            |
| `client_name`                    | string  | Ethereum client name of the RPC node                             | `web3_clientVersion` (before first `/`) |
| `client_version`                 | string  | Ethereum client version                                          | `web3_clientVersion` (after first `/`)  |
| `node_chain_id`                  | int     | Chain ID reported by the node                                    | `eth_chainId`                           |
| `chain_id`                       | int     | Same as `node_chain_id` (duplicated for standalone file reading) | `eth_chainId`                           |
| `node_head_block_at_extraction`  | int     | Latest block number known at extraction time                     | `eth_blockNumber`                        |
| `node_sync_completion_block`     | int     | Current sync block (= head if node is fully synced)              | `eth_syncing` or `eth_blockNumber`      |
| `rpc_method_used`                | string  | Primary RPC method used to fetch price data                      | config (`eth_call:getRoundData`)        |
| `extraction_script_hash`         | string  | SHA-256 of the Python script that produced this CSV              | `hashlib.sha256(open(__file__).read())` |
| `abi_hash`                       | string  | SHA-256 of the Chainlink ABI string used                         | `hashlib.sha256(abi.encode())`          |

**Feed configuration**

| Column                     | Type    | Description                                                            | Method                             |
|----------------------------|---------|------------------------------------------------------------------------|------------------------------------|
| `network_name`             | string  | Human-readable blockchain network name                                 | config                             |
| `feed_proxy_address`       | string  | Chainlink proxy contract address used as the entry point               | config                             |
| `aggregator_address`       | string  | Active aggregator address for the current phase (`N/A` if unavailable) | `eth_call:phaseAggregators(phase)` |
| `feed_description`         | string  | Official feed description returned by the contract                     | `eth_call:description()`           |
| `base_asset`               | string  | Base asset of the price pair                                           | config                             |
| `quote_asset`              | string  | Quote asset of the price pair                                          | config                             |
| `feed_decimals`            | int     | Number of decimals used by the feed (8 for standard USD feeds)         | `eth_call:decimals()`              |
| `chainlink_version`        | int     | Version of the `AggregatorV3Interface` contract                        | `eth_call:version()`               |
| `heartbeat_seconds`        | int     | Maximum update interval in seconds (from Chainlink documentation)      | config                             |
| `deviation_threshold_bps`  | int     | Price deviation threshold that triggers an update (in basis points)    | config                             |

## 🗂 CSV Structure: `chainlink_usdt_usd.csv`

**Round identification**

| Column              | Type    | Description                                                    | Method       |
|---------------------|---------|----------------------------------------------------------------|--------------|
| `global_round_id`   | uint80  | Global round identifier (`phase << 64 | aggregator_round_id`) | script-local |
| `phase`             | int     | Chainlink proxy contract phase identifier                      | script-local |
| `aggregator_round`  | int     | Round identifier within the current phase                      | script-local |

**Round data**

| Column                  | Type    | Description                                                                      | Method                                      |
|-------------------------|---------|----------------------------------------------------------------------------------|---------------------------------------------|
| `round_updated_at_utc`  | string  | UTC timestamp when the round was updated (`YYYY-MM-DD HH:MM:SS+00:00`)          | `eth_call:getRoundData` → `updatedAt`       |
| `answer_normalized`     | float   | Price in quote asset: `answer_raw / 10^feed_decimals`                            | computed                                    |
| `answer_raw`            | int256  | Raw answer returned by the Chainlink contract                                    | `eth_call:getRoundData` → `answer`          |
| `answered_in_round`     | uint80  | Round in which the answer was definitively committed                             | `eth_call:getRoundData` → `answeredInRound` |
| `round_started_at_utc`  | string  | UTC timestamp when the round was started (`YYYY-MM-DD HH:MM:SS+00:00`)          | `eth_call:getRoundData` → `startedAt`       |
| `answer_status`         | string  | Computed status: `ok`, `zero_answer`, `negative_answer`, `answered_in_old_round` | computed                                    |

**Extraction metadata**

| Column                           | Type    | Description                                                      | Method                                  |
|----------------------------------|---------|------------------------------------------------------------------|-----------------------------------------|
| `extraction_run_id`              | string  | UUID identifying this extraction run                             | script-local (`uuid4`)                  |
| `schema_version`                 | string  | CSV schema version (e.g. `chainlink_price_feed_v1`)              | config                                  |
| `extraction_timestamp_utc`       | string  | UTC timestamp of extraction start                                | script-local                            |
| `client_name`                    | string  | Ethereum client name of the RPC node                             | `web3_clientVersion` (before first `/`) |
| `client_version`                 | string  | Ethereum client version                                          | `web3_clientVersion` (after first `/`)  |
| `node_chain_id`                  | int     | Chain ID reported by the node                                    | `eth_chainId`                           |
| `chain_id`                       | int     | Same as `node_chain_id` (duplicated for standalone file reading) | `eth_chainId`                           |
| `node_head_block_at_extraction`  | int     | Latest block number known at extraction time                     | `eth_blockNumber`                        |
| `node_sync_completion_block`     | int     | Current sync block (= head if node is fully synced)              | `eth_syncing` or `eth_blockNumber`      |
| `rpc_method_used`                | string  | Primary RPC method used to fetch price data                      | config (`eth_call:getRoundData`)        |
| `extraction_script_hash`         | string  | SHA-256 of the Python script that produced this CSV              | `hashlib.sha256(open(__file__).read())` |
| `abi_hash`                       | string  | SHA-256 of the Chainlink ABI string used                         | `hashlib.sha256(abi.encode())`          |

**Feed configuration**

| Column                     | Type    | Description                                                            | Method                             |
|----------------------------|---------|------------------------------------------------------------------------|------------------------------------|
| `network_name`             | string  | Human-readable blockchain network name                                 | config                             |
| `feed_proxy_address`       | string  | Chainlink proxy contract address used as the entry point               | config                             |
| `aggregator_address`       | string  | Active aggregator address for the current phase (`N/A` if unavailable) | `eth_call:phaseAggregators(phase)` |
| `feed_description`         | string  | Official feed description returned by the contract                     | `eth_call:description()`           |
| `base_asset`               | string  | Base asset of the price pair                                           | config                             |
| `quote_asset`              | string  | Quote asset of the price pair                                          | config                             |
| `feed_decimals`            | int     | Number of decimals used by the feed (8 for standard USD feeds)         | `eth_call:decimals()`              |
| `chainlink_version`        | int     | Version of the `AggregatorV3Interface` contract                        | `eth_call:version()`               |
| `heartbeat_seconds`        | int     | Maximum update interval in seconds (from Chainlink documentation)      | config                             |
| `deviation_threshold_bps`  | int     | Price deviation threshold that triggers an update (in basis points)    | config                             |

---

## 🧾 License

All contents of this repository (data, code, and documentation) are licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH**

# Open Price AAVE Data Repository
Open Price AAVE is an open-data initiative providing a standardized, continuously updated historical dataset of AAVE/USD prices from on-chain sources (Chainlink and Uniswap V3). Fully compliant with FAIR principles, it empowers researchers and developers with transparent, reproducible insights into AAVE price dynamics.

---

## 📅 Available Datasets

| Dataset                          | End Date Available              | CSV File                                      |
|----------------------------------|---------------------------------|-----------------------------------------------|
| **Chainlink AAVE/USD**        | 2026-05-26 13:21:35 UTC      | `data/chainlink_aave_usd.csv`                |
| **Uniswap V3 AAVE/USDC**     | 2026-05-26 14:01:47 UTC        | `data/aave_usdc_uniswap_v3_03.csv`           |
| **Uniswap V3 AAVE/USDT**     | 2026-05-26 14:01:59 UTC           | `data/aave_usdt_uniswap_v3_03.csv`           |
| **Uniswap V3 AAVE/WETH**     | 2026-05-26 14:01:47 UTC        | `data/aave_weth_uniswap_v3_03.csv`           |
| **SushiSwap V2 AAVE/ETH**    | 2026-05-26 13:30:35 UTC       | `data/aave_eth_sushiswap_v2_03.csv`          |

---

## 🗂 CSV Structure: `chainlink_aave_usd.csv`

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

## 🗂 CSV Structure: `aave_usdc_uniswap_v3_03.csv`

**Core price data**

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block, e.g. `2024-04-19 23:59:59+00:00`                                |
| `price_usdc_per_aave` | float   | AAVE price in USDC derived from `sqrtPriceX96` (AAVE=token0 formula: `sqrtP²×1e12`)         |
| `usdc_amount`         | float   | USDC leg of the swap (signed: positive = USDC into pool, negative = USDC out of pool)       |
| `aave_amount`         | float   | AAVE leg of the swap (signed)                                                                |
| `volume_usdc`         | float   | Trade notional in USDC — `abs(usdc_amount)`                                                  |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block                                                                   |
| `pool_address`        | string  | Uniswap V3 pool contract address                                                             |
| `pool_fee_tier`       | int     | Pool fee tier in hundredths of a basis point (3000 = 0.3%)                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `sqrt_price_x96`      | uint160 | Raw `sqrtPriceX96` value from the Swap event                                                 |
| `liquidity`           | uint128 | Active in-range liquidity of the pool at the time of the swap                               |
| `tick`                | int24   | Current tick of the pool at the time of the swap                                             |
| `pool_tvl_at_block`   | float   | Total Value Locked in USD at the swap block (USDC balance + AAVE balance × price)           |
| `slip_1k`             | float   | Simulated cost of a 1 000 USDC→AAVE swap: price impact + fee tier (via QuoterV2). `None` for pre-2022 blocks (QuoterV2 not yet deployed). |

**Extraction metadata**

| Column | Type | Description | Method |
|--------|------|-------------|--------|
| `extraction_run_id` | string | UUID v4 unique identifier for this extraction run | `uuid.uuid4()` at script load |
| `schema_version` | string | Schema version string identifying the CSV format | constant defined in script |
| `extraction_timestamp_utc` | string | UTC timestamp when the extraction was executed | `datetime.now(timezone.utc)` at script load |
| `client_name` | string | Ethereum node client name | `web3_clientVersion` RPC call, first segment before `/` |
| `client_version` | string | Ethereum node client version | `web3_clientVersion` RPC call, second segment |
| `node_chain_id` | int | Chain ID reported by the connected node | `eth_chainId` RPC call |
| `node_head_block_at_extraction` | int | Block number at the head of the chain at extraction time | `eth_blockNumber` RPC call |
| `node_sync_completion_block` | int | Last synced block; equals head block if fully synced | `eth_syncing` RPC call |
| `rpc_method_used` | string | RPC methods used during extraction | constant defined in script |
| `extraction_script_hash` | string | SHA-256 hash of the extraction script for reproducibility | `hashlib.sha256` on the script file bytes |
| `abi_hash` | string | SHA-256 hash of the event ABI used | `hashlib.sha256` on the ABI string |
| `network_name` | string | Blockchain network name | constant defined in script |

**Block and transaction metadata**

| Column | Type | Description | Method |
|--------|------|-------------|--------|
| `block_timestamp_utc` | string | UTC timestamp of the block containing the swap | `eth_getBlockByNumber`, `timestamp` field |
| `block_hash` | string | Hash of the block containing the swap | `eth_getBlockByNumber`, `hash` field |
| `transaction_index` | int | Index of the transaction within its block | included in cryo CSV output |
| `event_signature` | string | Keccak-256 topic0 of the Swap event | constant (matches `topic0` in cryo CSV) |

**DEX and token metadata**

| Column | Type | Description | Method |
|--------|------|-------------|--------|
| `dex_protocol` | string | DEX protocol name | constant defined in script |
| `dex_version` | string | DEX protocol version | constant defined in script |
| `token0_address` | string | On-chain address of token0 | constant defined in script |
| `token1_address` | string | On-chain address of token1 | constant defined in script |
| `token0_symbol` | string | Symbol of token0 | ERC-20 `symbol()` call |
| `token1_symbol` | string | Symbol of token1 | ERC-20 `symbol()` call |
| `token0_decimals` | int | Decimal places for token0 | constant defined in script |
| `token1_decimals` | int | Decimal places for token1 | constant defined in script |
| `amount0_raw` | int | Raw signed integer amount for token0 in the swap (positive = in, negative = out) | decoded from swap event data |
| `amount1_raw` | int | Raw signed integer amount for token1 in the swap | decoded from swap event data |
| `amount0_normalized` | float | `amount0_raw` divided by `10^token0_decimals` | high-precision arithmetic via `mpmath` |
| `amount1_normalized` | float | `amount1_raw` divided by `10^token1_decimals` | high-precision arithmetic via `mpmath` |
| `swap_sender` | string | Address that initiated the swap (msg.sender) | decoded from indexed topic1 in cryo CSV |
| `swap_recipient` | string | Address that received the output tokens | decoded from indexed topic2 in cryo CSV |
| `swap_direction` | string | Direction: `token0_to_token1` if `amount0_raw > 0`, else `token1_to_token0` | sign of `amount0_raw` |
| `base_token_address` | string | On-chain address of the base token | constant defined in script |
| `quote_token_address` | string | On-chain address of the quote token | constant defined in script |
| `base_token_symbol` | string | Symbol of the base token | constant defined in script |
| `quote_token_symbol` | string | Symbol of the quote token | constant defined in script |
| `price_source_field` | string | Field used to derive the price | constant defined in script |
| `pool_tvl_threshold_used` | int | Minimum TVL threshold (in USD) for quality flagging | constant (10000) |
| `slip_10k` | float | Simulated slippage for a swap 10× the `slip_1k` amount (10 000 USDC→AAVE via QuoterV2) | computed |
| `quality_flags` | string | Pipe-separated quality flags: `low_liquidity`, `zero_amount`, `extreme_slippage`, or `ok` | computed |

## 🗂 CSV Structure: `aave_usdt_uniswap_v3_03.csv`

Same structure as `aave_usdc_uniswap_v3_03.csv` with USDT replacing USDC (`price_usdt_per_aave`, `usdt_amount`, `volume_usdt`, `slip_1k` = 1 000 USDT→AAVE, `slip_10k` = 10 000 USDT→AAVE). All extraction metadata, block/transaction metadata, and DEX/token metadata columns are identical.

## 🗂 CSV Structure: `aave_weth_uniswap_v3_03.csv`

Uniswap V3 AAVE/WETH pool. TVL and volume expressed in WETH. `slip_1k` simulates buying AAVE with 1 WETH; `slip_10k` with 10 WETH.

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block                                                                   |
| `price_weth_per_aave` | float   | AAVE price in WETH derived from `sqrtPriceX96` (AAVE=token0: `sqrtP²`)                      |
| `weth_amount`         | float   | WETH leg of the swap (signed)                                                                |
| `aave_amount`         | float   | AAVE leg of the swap (signed)                                                                |
| `volume_weth`         | float   | Trade notional in WETH — `abs(weth_amount)`                                                  |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block                                                                   |
| `pool_address`        | string  | Pool contract address                                                                        |
| `pool_fee_tier`       | int     | Pool fee tier (3000 = 0.3%)                                                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `sqrt_price_x96`      | uint160 | Raw `sqrtPriceX96` value from the Swap event                                                 |
| `liquidity`           | uint128 | Active in-range liquidity at the time of the swap                                            |
| `tick`                | int24   | Current tick at the time of the swap                                                         |
| `pool_tvl_at_block`   | float   | Total Value Locked in WETH (WETH balance + AAVE balance × price)                             |
| `slip_1k`             | float   | Simulated cost of a 1 WETH→AAVE swap (via QuoterV2)                                         |

All extraction metadata, block/transaction metadata, and DEX/token metadata columns are identical to those described for `aave_usdc_uniswap_v3_03.csv` above. Additionally: `slip_10k` (10 WETH→AAVE), `quality_flags`.

## 🗂 CSV Structure: `aave_eth_sushiswap_v2_03.csv`

SushiSwap V2 AAVE/ETH pool. Price derived from swap amounts; reserves from `getReserves()`. `slip_1k` uses the V2 analytical formula. Note: `swap_recipient` is `None` for V2 (topic2 is the `to` address but encoded differently from V3).

**Core price data**

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block                                                                   |
| `price_eth_per_aave`  | float   | Effective AAVE price in ETH from swap amounts (`\|ETH_net\| / \|AAVE_net\|`)                 |
| `eth_amount`          | float   | ETH (WETH) net flow (positive = into pool)                                                   |
| `aave_amount`         | float   | AAVE net flow (positive = into pool)                                                         |
| `volume_eth`          | float   | Trade notional in ETH — `abs(eth_amount)`                                                    |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block                                                                   |
| `pool_address`        | string  | Pool contract address                                                                        |
| `pool_fee_tier`       | int     | Pool fee tier (3000 = 0.3%)                                                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `reserve0`            | uint112 | Raw token0 (AAVE) reserve at the swap block                                                  |
| `reserve1`            | uint112 | Raw token1 (WETH) reserve at the swap block                                                  |
| `pool_tvl_at_block`   | float   | Total Value Locked in ETH (ETH reserve + AAVE reserve × price)                               |
| `slip_1k`             | float   | Simulated cost of a 1 ETH→AAVE swap using the V2 analytical formula                         |

All extraction metadata, block/transaction metadata, and DEX/token metadata columns are identical to those described for `aave_usdc_uniswap_v3_03.csv` above. Additionally: `quality_flags`. Note: `slip_10k` is not present in this dataset (V2 script does not compute it).

---

## 🧾 License

All contents of this repository (data, code, and documentation) are licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH**

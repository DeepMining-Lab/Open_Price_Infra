# Open Price COMP Data Repository
Open Price COMP is an open-data initiative providing a standardized, continuously updated historical dataset of COMP/USD prices from on-chain sources (Chainlink and Uniswap V3). Fully compliant with FAIR principles, it empowers researchers and developers with transparent, reproducible insights into COMP price dynamics.

---

## 📅 Available Datasets

| Dataset                          | End Date Available              | CSV File                                      |
|----------------------------------|---------------------------------|-----------------------------------------------|
| **Chainlink COMP/USD**        | 2026-06-09 16:58:11 UTC      | `data/chainlink_comp_usd.csv`                |
| **Uniswap V3 COMP/USDC**     | 2026-02-12 21:49:11 UTC        | `data/comp_usdc_uniswap_v3_03.csv`           |
| **Uniswap V3 COMP/USDT**     | 2021-10-06 09:21:30 UTC           | `data/comp_usdt_uniswap_v3_03.csv`           |
| **Uniswap V3 COMP/WETH**     | 2026-06-09 17:23:59 UTC        | `data/comp_weth_uniswap_v3_03.csv`           |
| **Uniswap V2 COMP/WETH**     | 2026-06-09 17:24:23 UTC        | `data/comp_weth_uniswap_v2_03.csv`           |
| **SushiSwap V2 COMP/ETH**    | 2026-06-09 17:26:35 UTC       | `data/comp_eth_sushiswap_v2_03.csv`          |

---

## 🗂 CSV Structure: `chainlink_comp_usd.csv`

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

## 🗂 CSV Structure: `comp_usdc_uniswap_v3_03.csv`

**Core price data**

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block, e.g. `2024-04-19 23:59:59+00:00`                                |
| `price_usdc_per_comp` | float   | COMP price in USDC derived from `sqrtPriceX96` (USDC=token0 formula: `1/(sqrtP²×1e-12)`)   |
| `usdc_amount`         | float   | USDC leg of the swap (signed: positive = USDC into pool, negative = USDC out of pool)       |
| `comp_amount`         | float   | COMP leg of the swap (signed)                                                                |
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
| `pool_tvl_at_block`   | float   | Total Value Locked in USD at the swap block (USDC balance + COMP balance × price)           |
| `slip_1k`             | float   | Simulated cost of a 1 000 USDC→COMP swap: price impact + fee tier (via QuoterV2). `None` for pre-2022 blocks (QuoterV2 not yet deployed). |

**Extraction metadata**

| Column | Type | Description | Method |
|--------|------|-------------|--------|
| `extraction_run_id` | string | UUID identifying this extraction run | script-local (`uuid4`) |
| `schema_version` | string | CSV schema version (e.g. `dex_uniswap_v3_v1`) | config |
| `extraction_timestamp_utc` | string | UTC timestamp of extraction start | script-local |
| `client_name` | string | Ethereum client name of the RPC node | `web3_clientVersion` (before first `/`) |
| `client_version` | string | Ethereum client version | `web3_clientVersion` (after first `/`) |
| `node_chain_id` | int | Chain ID reported by the node | `eth_chainId` |
| `node_head_block_at_extraction` | int | Latest block number known at extraction time | `eth_blockNumber` |
| `node_sync_completion_block` | int | Current sync block (= head if node is fully synced) | `eth_syncing` or `eth_blockNumber` |
| `rpc_method_used` | string | RPC methods used | config |
| `extraction_script_hash` | string | SHA-256 of the Python script that produced this CSV | `hashlib.sha256(open(__file__,'rb').read())` |
| `abi_hash` | string | SHA-256 of the Swap event ABI string | `hashlib.sha256(SWAP_EVENT_ABI.encode())` |
| `network_name` | string | Blockchain network name | config |

**Block and transaction metadata**

| Column | Type | Description | Method |
|--------|------|-------------|--------|
| `block_timestamp_utc` | string | UTC timestamp of the block | `eth_getBlockByNumber` → `timestamp` |
| `block_hash` | string | Block hash | `eth_getBlockByNumber` → `hash` |
| `transaction_index` | int | Transaction index within the block | from cryo CSV |
| `event_signature` | string | Keccak-256 of the Swap event signature (= `topic0`) | config |

**DEX and token metadata**

| Column | Type | Description | Method |
|--------|------|-------------|--------|
| `dex_protocol` | string | DEX protocol (`uniswap` or `sushiswap`) | config |
| `dex_version` | string | Protocol version (`v3` or `v2`) | config |
| `token0_address` | string | token0 contract address | config |
| `token1_address` | string | token1 contract address | config |
| `token0_symbol` | string | token0 symbol | `eth_call:symbol()` ERC-20 |
| `token1_symbol` | string | token1 symbol | `eth_call:symbol()` ERC-20 |
| `token0_decimals` | int | token0 decimals | config |
| `token1_decimals` | int | token1 decimals | config |
| `amount0_raw` | int | Net token0 flow in raw units (positive = into pool) | ABI decoding |
| `amount1_raw` | int | Net token1 flow in raw units | ABI decoding |
| `amount0_normalized` | float | `amount0_raw / 10^token0_decimals` | computed |
| `amount1_normalized` | float | `amount1_raw / 10^token1_decimals` | computed |
| `swap_sender` | string | Swap sender address | `topic1` of log |
| `swap_recipient` | string | Swap recipient address | `topic2` of log |
| `swap_direction` | string | `token0_to_token1` or `token1_to_token0` | computed from `amount0_raw` |
| `base_token_address` | string | Base token address (COMP) | config |
| `quote_token_address` | string | Quote token address | config |
| `base_token_symbol` | string | Base token symbol | config |
| `quote_token_symbol` | string | Quote token symbol | config |
| `price_source_field` | string | Price computation method | config |
| `pool_tvl_threshold_used` | int | TVL threshold for `low_liquidity` flag | config |
| `slip_10k` | float | Simulated slippage for a swap 10× the `slip_1k` amount (10 000 USDC→COMP via QuoterV2) | computed |
| `quality_flags` | string | Quality flags (`low_liquidity`, `zero_amount`, `extreme_slippage`, or `ok`) | computed |

## 🗂 CSV Structure: `comp_usdt_uniswap_v3_03.csv`

Same structure as `comp_usdc_uniswap_v3_03.csv` with USDT replacing USDC. Note: COMP=token0, USDT=token1, so price formula is `sqrtP²×1e12` (unlike the USDC pool where USDC=token0).

Core columns: `price_usdt_per_comp`, `usdt_amount`, `comp_amount`, `volume_usdt` — all metadata columns identical to the USDC dataset. `slip_1k` and `slip_10k` simulate buying COMP with 1 000 and 10 000 USDT respectively.

## 🗂 CSV Structure: `comp_weth_uniswap_v3_03.csv`

Uniswap V3 COMP/WETH pool. TVL and volume expressed in WETH. `slip_1k` simulates buying COMP with 1 WETH; `slip_10k` with 10 WETH.

**Core price data**

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block                                                                   |
| `price_weth_per_comp` | float   | COMP price in WETH derived from `sqrtPriceX96` (COMP=token0: `sqrtP²`)                      |
| `weth_amount`         | float   | WETH leg of the swap (signed)                                                                |
| `comp_amount`         | float   | COMP leg of the swap (signed)                                                                |
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
| `pool_tvl_at_block`   | float   | Total Value Locked in WETH (WETH balance + COMP balance × price)                             |
| `slip_1k`             | float   | Simulated cost of a 1 WETH→COMP swap (via QuoterV2)                                         |

All extraction metadata, block/transaction metadata, and DEX/token metadata columns are identical to those described for `comp_usdc_uniswap_v3_03.csv` above. Additionally: `slip_10k` (10 WETH→COMP), `quality_flags`.

## 🗂 CSV Structure: `comp_weth_uniswap_v2_03.csv` and `comp_eth_sushiswap_v2_03.csv`

Uniswap V2 and SushiSwap V2 COMP/WETH pools. Price from swap amounts; reserves from `getReserves()`. `slip_1k` and `slip_10k` use the V2 analytical AMM formula.

**Core price data**

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block                                                                   |
| `price_weth_per_comp` | float   | Effective COMP price in WETH. Named `price_eth_per_comp` in SushiSwap variant.               |
| `weth_amount`         | float   | WETH net flow (positive = into pool). Named `eth_amount` in SushiSwap variant.               |
| `comp_amount`         | float   | COMP net flow (positive = into pool)                                                         |
| `volume_weth`         | float   | Trade notional in WETH. Named `volume_eth` in SushiSwap variant.                             |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block                                                                   |
| `pool_address`        | string  | Pool contract address                                                                        |
| `pool_fee_tier`       | int     | Pool fee tier (3000 = 0.3%)                                                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `reserve0`            | uint112 | Raw token0 (COMP) reserve at the swap block                                                  |
| `reserve1`            | uint112 | Raw token1 (WETH) reserve at the swap block                                                  |
| `pool_tvl_at_block`   | float   | Total Value Locked in WETH (WETH reserve + COMP reserve × price)                             |
| `slip_1k`             | float   | Simulated cost of a 1 WETH→COMP swap using the V2 analytical formula                        |

All extraction metadata, block/transaction metadata, and DEX/token metadata columns are identical to those described for `comp_usdc_uniswap_v3_03.csv` above. Additionally: `slip_10k` (10 WETH/ETH→COMP, V2 AMM formula), `quality_flags`.

---

## 🧾 License

All contents of this repository (data, code, and documentation) are licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH**

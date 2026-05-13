# Open Price LINK Data Repository
Open Price LINK is an open-data initiative providing a standardized, continuously updated historical dataset of LINK/USD prices from on-chain sources (Chainlink and Uniswap V3). Fully compliant with FAIR principles, it empowers researchers and developers with transparent, reproducible insights into LINK price dynamics.

---

## 📅 Available Datasets

| Dataset                          | End Date Available              | CSV File                                      |
|----------------------------------|---------------------------------|-----------------------------------------------|
| **Chainlink LINK/USD**        | 2026-05-13 22:45:59 UTC      | `data/chainlink_link_usd.csv`                |
| **Uniswap V3 LINK/USDC**     | 2026-05-13 19:07:11 UTC        | `data/link_usdc_uniswap_v3_03.csv`           |
| **Uniswap V3 LINK/USDT**     | N/A                             | `data/link_usdt_uniswap_v3_03.csv`           |
| **Uniswap V3 LINK/WETH**     | N/A                             | `data/link_weth_uniswap_v3_03.csv`           |
| **SushiSwap V3 LINK/ETH**    | N/A                             | `data/link_eth_sushiswap_v3_03.csv`          |
| **Uniswap V2 LINK/WETH**     | N/A                             | `data/link_weth_uniswap_v2_03.csv`           |
| **SushiSwap V2 LINK/ETH**    | N/A                             | `data/link_eth_sushiswap_v2_03.csv`          |

---

## 🗂 CSV Structure: `chainlink_link_usd.csv`

| Column             | Type    | Description                                                              |
|--------------------|---------|--------------------------------------------------------------------------|
| `global_round_id`  | uint80  | Global round identifier (`phase << 64 | aggregator_round_id`)            |
| `phase`            | int     | Chainlink contract phase identifier                                      |
| `aggregator_round` | int     | Round identifier within the given phase                                  |
| `datetime_utc`     | string  | Update timestamp in `YYYY-MM-DD HH:MM:SS` format (UTC)                   |
| `price`            | float   | LINK/USD price (scaled by 10⁸ in the contract)                           |

## 🗂 CSV Structure: `link_usdc_uniswap_v3_03.csv`

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block, e.g. `2024-04-19 23:59:59+00:00`                                |
| `price_usdc_per_link` | float   | LINK price in USDC derived from `sqrtPriceX96` (LINK=token0 formula: `sqrtP²×1e12`)         |
| `usdc_amount`         | float   | USDC leg of the swap (signed: positive = USDC into pool, negative = USDC out of pool)       |
| `link_amount`         | float   | LINK leg of the swap (signed: positive = LINK into pool, negative = LINK out of pool)       |
| `volume_usdc`         | float   | Trade notional in USDC — absolute value of the USDC leg (`abs(usdc_amount)`)                |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block (ordering within multi-log transactions)                          |
| `pool_address`        | string  | Uniswap V3 pool contract address                                                             |
| `pool_fee_tier`       | int     | Pool fee tier in hundredths of a basis point (3000 = 0.3%)                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `sqrt_price_x96`      | uint160 | Raw `sqrtPriceX96` value from the Swap event                                                 |
| `liquidity`           | uint128 | Active in-range liquidity of the pool at the time of the swap                               |
| `tick`                | int24   | Current tick of the pool at the time of the swap                                             |
| `pool_tvl_at_block`   | float   | Total Value Locked in USD at the swap block (USDC balance + LINK balance × price)           |
| `slip_1k`             | float   | Simulated cost of a 1 000 USDC→LINK swap: price impact + fee tier (via QuoterV2). `None` for pre-2022 blocks (QuoterV2 not yet deployed). |

## 🗂 CSV Structure: `link_usdt_uniswap_v3_03.csv`

Same structure as `link_usdc_uniswap_v3_03.csv` with USDT replacing USDC.

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block, e.g. `2024-04-19 23:59:59+00:00`                                |
| `price_usdt_per_link` | float   | LINK price in USDT derived from `sqrtPriceX96` (LINK=token0 formula: `sqrtP²×1e12`)         |
| `usdt_amount`         | float   | USDT leg of the swap (signed)                                                                |
| `link_amount`         | float   | LINK leg of the swap (signed)                                                                |
| `volume_usdt`         | float   | Trade notional in USDT — `abs(usdt_amount)`                                                  |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block                                                                   |
| `pool_address`        | string  | Uniswap V3 pool contract address                                                             |
| `pool_fee_tier`       | int     | Pool fee tier (3000 = 0.3%)                                                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `sqrt_price_x96`      | uint160 | Raw `sqrtPriceX96` value from the Swap event                                                 |
| `liquidity`           | uint128 | Active in-range liquidity at the time of the swap                                            |
| `tick`                | int24   | Current tick at the time of the swap                                                         |
| `pool_tvl_at_block`   | float   | Total Value Locked in USD (USDT balance + LINK balance × price)                              |
| `slip_1k`             | float   | Simulated cost of a 1 000 USDT→LINK swap (via QuoterV2)                                     |

## 🗂 CSV Structure: `link_weth_uniswap_v3_03.csv` and `link_eth_sushiswap_v3_03.csv`

Uniswap V3 and SushiSwap V3 LINK/WETH pools. TVL and volume are expressed in WETH. `slip_1k` simulates buying LINK with 1 WETH.

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block                                                                   |
| `price_weth_per_link` | float   | LINK price in WETH derived from `sqrtPriceX96` (LINK=token0, WETH=token1: `sqrtP²`)         |
| `price_eth_per_link`  | float   | (SushiSwap variant) Same formula, column renamed to `price_eth_per_link`                     |
| `weth_amount`         | float   | WETH leg of the swap (signed)                                                                |
| `eth_amount`          | float   | (SushiSwap variant) Same field, renamed to `eth_amount`                                      |
| `link_amount`         | float   | LINK leg of the swap (signed)                                                                |
| `volume_weth`         | float   | Trade notional in WETH — `abs(weth_amount)`                                                  |
| `volume_eth`          | float   | (SushiSwap variant)                                                                          |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block                                                                   |
| `pool_address`        | string  | Pool contract address                                                                        |
| `pool_fee_tier`       | int     | Pool fee tier (3000 = 0.3%)                                                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `sqrt_price_x96`      | uint160 | Raw `sqrtPriceX96` value from the Swap event                                                 |
| `liquidity`           | uint128 | Active in-range liquidity at the time of the swap                                            |
| `tick`                | int24   | Current tick at the time of the swap                                                         |
| `pool_tvl_at_block`   | float   | Total Value Locked in WETH (WETH balance + LINK balance × price)                             |
| `slip_1k`             | float   | Simulated cost of a 1 WETH→LINK swap (via QuoterV2 for V3, N/A for pre-deployment blocks)   |

## 🗂 CSV Structure: `link_weth_uniswap_v2_03.csv` and `link_eth_sushiswap_v2_03.csv`

Uniswap V2 and SushiSwap V2 LINK/WETH pools. Price derived from swap amounts; reserves fetched via `getReserves()`. TVL and volume in WETH. `slip_1k` uses the analytical V2 formula.

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block                                                                   |
| `price_weth_per_link` | float   | Effective LINK price in WETH from swap amounts (`\|WETH_net\| / \|LINK_net\|`)               |
| `price_eth_per_link`  | float   | (SushiSwap variant)                                                                          |
| `weth_amount`         | float   | WETH net flow (positive = into pool, negative = out of pool)                                 |
| `eth_amount`          | float   | (SushiSwap variant)                                                                          |
| `link_amount`         | float   | LINK net flow (signed)                                                                       |
| `volume_weth`         | float   | Trade notional in WETH — `abs(weth_amount)`                                                  |
| `volume_eth`          | float   | (SushiSwap variant)                                                                          |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block                                                                   |
| `pool_address`        | string  | Pool contract address                                                                        |
| `pool_fee_tier`       | int     | Pool fee tier (3000 = 0.3%)                                                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `reserve0`            | uint112 | Raw token0 (LINK) reserve at the swap block                                                  |
| `reserve1`            | uint112 | Raw token1 (WETH) reserve at the swap block                                                  |
| `pool_tvl_at_block`   | float   | Total Value Locked in WETH (WETH reserve + LINK reserve × price)                             |
| `slip_1k`             | float   | Simulated cost of a 1 WETH→LINK swap using the V2 analytical formula                        |

---

## 🧾 License

All contents of this repository (data, code, and documentation) are licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH**

# Open Price COMP Data Repository
Open Price COMP is an open-data initiative providing a standardized, continuously updated historical dataset of COMP/USD prices from on-chain sources (Chainlink and Uniswap V3). Fully compliant with FAIR principles, it empowers researchers and developers with transparent, reproducible insights into COMP price dynamics.

---

## 📅 Available Datasets

| Dataset                          | End Date Available              | CSV File                                      |
|----------------------------------|---------------------------------|-----------------------------------------------|
| **Chainlink COMP/USD**        | 2026-05-13 18:33:47 UTC      | `data/chainlink_comp_usd.csv`                |
| **Uniswap V3 COMP/USDC**     | 2026-02-12 21:49:11 UTC        | `data/comp_usdc_uniswap_v3_03.csv`           |
| **Uniswap V3 COMP/USDT**     | N/A                             | `data/comp_usdt_uniswap_v3_03.csv`           |
| **Uniswap V3 COMP/WETH**     | N/A                             | `data/comp_weth_uniswap_v3_03.csv`           |
| **Uniswap V2 COMP/WETH**     | N/A                             | `data/comp_weth_uniswap_v2_03.csv`           |
| **SushiSwap V2 COMP/ETH**    | N/A                             | `data/comp_eth_sushiswap_v2_03.csv`          |

---

## 🗂 CSV Structure: `chainlink_comp_usd.csv`

| Column             | Type    | Description                                                              |
|--------------------|---------|--------------------------------------------------------------------------|
| `global_round_id`  | uint80  | Global round identifier (`phase << 64 | aggregator_round_id`)            |
| `phase`            | int     | Chainlink contract phase identifier                                      |
| `aggregator_round` | int     | Round identifier within the given phase                                  |
| `datetime_utc`     | string  | Update timestamp in `YYYY-MM-DD HH:MM:SS` format (UTC)                   |
| `price`            | float   | COMP/USD price (scaled by 10⁸ in the contract)                           |

## 🗂 CSV Structure: `comp_usdc_uniswap_v3_03.csv`

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

## 🗂 CSV Structure: `comp_usdt_uniswap_v3_03.csv`

Same structure as `comp_usdc_uniswap_v3_03.csv` with USDT replacing USDC. Note: COMP=token0, USDT=token1, so price formula is `sqrtP²×1e12` (unlike the USDC pool where USDC=token0).

Columns: `price_usdt_per_comp`, `usdt_amount`, `comp_amount`, `volume_usdt` — rest identical.

## 🗂 CSV Structure: `comp_weth_uniswap_v3_03.csv`

Uniswap V3 COMP/WETH pool. TVL and volume expressed in WETH. `slip_1k` simulates buying COMP with 1 WETH.

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

## 🗂 CSV Structure: `comp_weth_uniswap_v2_03.csv` and `comp_eth_sushiswap_v2_03.csv`

Uniswap V2 and SushiSwap V2 COMP/WETH pools. Price from swap amounts; reserves from `getReserves()`. `slip_1k` uses the V2 analytical formula.

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

---

## 🧾 License

All contents of this repository (data, code, and documentation) are licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH**

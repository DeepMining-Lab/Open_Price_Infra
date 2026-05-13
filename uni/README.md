# Open Price UNI Data Repository
Open Price UNI is an open-data initiative providing a standardized, continuously updated historical dataset of UNI/USD prices from on-chain sources (Chainlink and Uniswap V3). Fully compliant with FAIR principles, it empowers researchers and developers with transparent, reproducible insights into UNI price dynamics.

---

## 📅 Available Datasets

| Dataset                          | End Date Available              | CSV File                                      |
|----------------------------------|---------------------------------|-----------------------------------------------|
| **Chainlink UNI/USD**         | 2026-05-13 21:53:59 UTC      | `data/chainlink_uni_usd.csv`                 |
| **Uniswap V3 UNI/USDC**      | 2026-05-13 18:46:23 UTC        | `data/uni_usdc_uniswap_v3_03.csv`            |
| **Uniswap V3 UNI/USDT**      | N/A                             | `data/uni_usdt_uniswap_v3_03.csv`            |
| **Uniswap V3 UNI/WETH**      | N/A                             | `data/uni_weth_uniswap_v3_03.csv`            |
| **SushiSwap V3 UNI/ETH**     | N/A                             | `data/uni_eth_sushiswap_v3_03.csv`           |
| **Uniswap V2 UNI/WETH**      | N/A                             | `data/uni_weth_uniswap_v2_03.csv`            |

---

## 🗂 CSV Structure: `chainlink_uni_usd.csv`

| Column             | Type    | Description                                                              |
|--------------------|---------|--------------------------------------------------------------------------|
| `global_round_id`  | uint80  | Global round identifier (`phase << 64 | aggregator_round_id`)            |
| `phase`            | int     | Chainlink contract phase identifier                                      |
| `aggregator_round` | int     | Round identifier within the given phase                                  |
| `datetime_utc`     | string  | Update timestamp in `YYYY-MM-DD HH:MM:SS` format (UTC)                   |
| `price`            | float   | UNI/USD price (scaled by 10⁸ in the contract)                            |

## 🗂 CSV Structure: `uni_usdc_uniswap_v3_03.csv`

| Column               | Type    | Description                                                                                  |
|----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`          | string  | UTC timestamp of the block, e.g. `2024-04-19 23:59:59+00:00`                                |
| `price_usdc_per_uni` | float   | UNI price in USDC derived from `sqrtPriceX96` (UNI=token0 formula: `sqrtP²×1e12`)           |
| `usdc_amount`        | float   | USDC leg of the swap (signed: positive = USDC into pool, negative = USDC out of pool)       |
| `uni_amount`         | float   | UNI leg of the swap (signed)                                                                 |
| `volume_usdc`        | float   | Trade notional in USDC — `abs(usdc_amount)`                                                  |
| `block_number`       | int     | Ethereum block number                                                                        |
| `transaction_hash`   | string  | Transaction hash                                                                             |
| `log_index`          | int     | Log index within the block                                                                   |
| `pool_address`       | string  | Uniswap V3 pool contract address                                                             |
| `pool_fee_tier`      | int     | Pool fee tier in hundredths of a basis point (3000 = 0.3%)                                  |
| `chain_id`           | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `sqrt_price_x96`     | uint160 | Raw `sqrtPriceX96` value from the Swap event                                                 |
| `liquidity`          | uint128 | Active in-range liquidity of the pool at the time of the swap                               |
| `tick`               | int24   | Current tick of the pool at the time of the swap                                             |
| `pool_tvl_at_block`  | float   | Total Value Locked in USD at the swap block (USDC balance + UNI balance × price)            |
| `slip_1k`            | float   | Simulated cost of a 1 000 USDC→UNI swap: price impact + fee tier (via QuoterV2). `None` for pre-2022 blocks (QuoterV2 not yet deployed). |

## 🗂 CSV Structure: `uni_usdt_uniswap_v3_03.csv`

Same structure as `uni_usdc_uniswap_v3_03.csv` with USDT replacing USDC (`price_usdt_per_uni`, `usdt_amount`, `volume_usdt`, `slip_1k` = 1 000 USDT→UNI).

## 🗂 CSV Structure: `uni_weth_uniswap_v3_03.csv` and `uni_eth_sushiswap_v3_03.csv`

Uniswap V3 and SushiSwap V3 UNI/WETH pools. TVL and volume expressed in WETH. `slip_1k` simulates buying UNI with 1 WETH.

| Column               | Type    | Description                                                                                  |
|----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`          | string  | UTC timestamp of the block                                                                   |
| `price_weth_per_uni` | float   | UNI price in WETH (`sqrtP²`, both tokens at 18 dec). Column named `price_eth_per_uni` in the SushiSwap variant. |
| `weth_amount`        | float   | WETH leg of the swap (signed). Named `eth_amount` in SushiSwap variant.                      |
| `uni_amount`         | float   | UNI leg of the swap (signed)                                                                 |
| `volume_weth`        | float   | Trade notional in WETH. Named `volume_eth` in SushiSwap variant.                             |
| `block_number`       | int     | Ethereum block number                                                                        |
| `transaction_hash`   | string  | Transaction hash                                                                             |
| `log_index`          | int     | Log index within the block                                                                   |
| `pool_address`       | string  | Pool contract address                                                                        |
| `pool_fee_tier`      | int     | Pool fee tier (3000 = 0.3%)                                                                  |
| `chain_id`           | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `sqrt_price_x96`     | uint160 | Raw `sqrtPriceX96` value from the Swap event                                                 |
| `liquidity`          | uint128 | Active in-range liquidity at the time of the swap                                            |
| `tick`               | int24   | Current tick at the time of the swap                                                         |
| `pool_tvl_at_block`  | float   | Total Value Locked in WETH (WETH balance + UNI balance × price)                              |
| `slip_1k`            | float   | Simulated cost of a 1 WETH→UNI swap (via QuoterV2)                                          |

## 🗂 CSV Structure: `uni_weth_uniswap_v2_03.csv`

Uniswap V2 UNI/WETH pool. Price derived from swap amounts; reserves from `getReserves()`. `slip_1k` uses the V2 analytical formula.

| Column               | Type    | Description                                                                                  |
|----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`          | string  | UTC timestamp of the block                                                                   |
| `price_weth_per_uni` | float   | Effective UNI price in WETH from swap amounts (`\|WETH_net\| / \|UNI_net\|`)                 |
| `weth_amount`        | float   | WETH net flow (positive = into pool)                                                         |
| `uni_amount`         | float   | UNI net flow (positive = into pool)                                                          |
| `volume_weth`        | float   | Trade notional in WETH — `abs(weth_amount)`                                                  |
| `block_number`       | int     | Ethereum block number                                                                        |
| `transaction_hash`   | string  | Transaction hash                                                                             |
| `log_index`          | int     | Log index within the block                                                                   |
| `pool_address`       | string  | Pool contract address                                                                        |
| `pool_fee_tier`      | int     | Pool fee tier (3000 = 0.3%)                                                                  |
| `chain_id`           | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `reserve0`           | uint112 | Raw token0 (UNI) reserve at the swap block                                                   |
| `reserve1`           | uint112 | Raw token1 (WETH) reserve at the swap block                                                  |
| `pool_tvl_at_block`  | float   | Total Value Locked in WETH (WETH reserve + UNI reserve × price)                              |
| `slip_1k`            | float   | Simulated cost of a 1 WETH→UNI swap using the V2 analytical formula                         |

---

## 🧾 License

All contents of this repository (data, code, and documentation) are licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH**

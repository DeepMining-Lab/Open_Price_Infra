# Open Price AAVE Data Repository
Open Price AAVE is an open-data initiative providing a standardized, continuously updated historical dataset of AAVE/USD prices from on-chain sources (Chainlink and Uniswap V3). Fully compliant with FAIR principles, it empowers researchers and developers with transparent, reproducible insights into AAVE price dynamics.

---

## 📅 Available Datasets

| Dataset                    | End Date Available              | CSV File                                      |
|----------------------------|---------------------------------|-----------------------------------------------|
| **Chainlink AAVE/USD**  | {{ chainlink.extraction }}      | `data/chainlink_aave_usd.csv`                |
| **Uniswap V3 AAVE/USDC**| {{ uniswap.extraction }}        | `data/aave_usdc_uniswap_v3_03.csv`           |

---

## 🗂 CSV Structure: `chainlink_aave_usd.csv`

| Column             | Type    | Description                                                              |
|--------------------|---------|--------------------------------------------------------------------------|
| `global_round_id`  | uint80  | Global round identifier (`phase << 64 | aggregator_round_id`)            |
| `phase`            | int     | Chainlink contract phase identifier                                      |
| `aggregator_round` | int     | Round identifier within the given phase                                  |
| `datetime_utc`     | string  | Update timestamp in `YYYY-MM-DD HH:MM:SS` format (UTC)                   |
| `price`            | float   | AAVE/USD price (scaled by 10⁸ in the contract)                           |

## 🗂 CSV Structure: `aave_usdc_uniswap_v3_03.csv`

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block, e.g. `2024-04-19 23:59:59+00:00`                                |
| `price_usdc_per_aave` | float   | AAVE price in USDC derived from `sqrtPriceX96` (AAVE=token0 formula: `sqrtP²×1e12`)         |
| `usdc_amount`         | float   | USDC leg of the swap (signed: positive = USDC into pool, negative = USDC out of pool)       |
| `aave_amount`         | float   | AAVE leg of the swap (signed: positive = AAVE into pool, negative = AAVE out of pool)       |
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
| `pool_tvl_at_block`   | float   | Total Value Locked in USD at the swap block (USDC balance + AAVE balance × price)           |
| `slip_1k`             | float   | Simulated cost of a 1 000 USDC→AAVE swap: price impact + fee tier (via QuoterV2). `None` for pre-2022 blocks (QuoterV2 not yet deployed). |

---

## 🧾 License

All contents of this repository (data, code, and documentation) are licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH**

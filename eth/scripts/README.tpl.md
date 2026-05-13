# Open Price ETH Data Repository
Open Price ETH is an open-data initiative providing a standardized, continuously updated historical dataset of ETH/USD prices from on-chain sources (Chainlink and Uniswap V3). Fully compliant with FAIR principles, it empowers researchers and developers with transparent, reproducible insights into Ethereum price dynamics.

---

## 📅 Available Datasets

| Dataset                          | End Date Available              | CSV File                                      |
|----------------------------------|---------------------------------|-----------------------------------------------|
| **Chainlink ETH/USD**         | {{ chainlink.extraction }}      | `data/chainlink_eth_usd.csv`                  |
| **Uniswap V3 ETH/USDC**      | {{ uniswap.extraction }}        | `data/eth_usdc_uniswap_v3_005.csv`            |
| **Uniswap V2 WETH/USDC**     | N/A                             | `data/weth_usdc_uniswap_v2_03.csv`            |
| **Uniswap V2 WETH/USDT**     | N/A                             | `data/weth_usdt_uniswap_v2_03.csv`            |
| **Curve crvUSD/WETH**        | N/A                             | `data/crvusd_weth_curve.csv`                  |

---

## 🗂 CSV Structure: `chainlink_eth_usd.csv`

| Column             | Type    | Description                                                              |
|--------------------|---------|--------------------------------------------------------------------------|
| `global_round_id`  | uint80  | Global round identifier (`phase << 64 | aggregator_round_id`)            |
| `phase`            | int     | Chainlink contract phase identifier                                      |
| `aggregator_round` | int     | Round identifier within the given phase                                  |
| `datetime_utc`     | string  | Update timestamp in `YYYY-MM-DD HH:MM:SS` format (UTC)                   |
| `price`            | float   | ETH/USD price (scaled by 10⁸ in the contract)                            |

## 🗂 CSV Structure: `eth_usdc_uniswap_v3_005.csv`

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block, e.g. `2024-04-19 23:59:59+00:00`                                |
| `price_usdc_per_eth`  | float   | ETH price in USDC derived from `sqrtPriceX96` (USDC=token0 formula: `1/(sqrtP²×1e-12)`)    |
| `usdc_amount`         | float   | USDC leg of the swap (signed: positive = USDC into pool, negative = USDC out of pool)       |
| `eth_amount`          | float   | WETH leg of the swap (signed: positive = WETH into pool, negative = WETH out of pool)       |
| `volume_usdc`         | float   | Trade notional in USDC — absolute value of the USDC leg (`abs(usdc_amount)`)                |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block (ordering within multi-log transactions)                          |
| `pool_address`        | string  | Uniswap V3 pool contract address                                                             |
| `pool_fee_tier`       | int     | Pool fee tier in hundredths of a basis point (500 = 0.05%)                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `sqrt_price_x96`      | uint160 | Raw `sqrtPriceX96` value from the Swap event                                                 |
| `liquidity`           | uint128 | Active in-range liquidity of the pool at the time of the swap                               |
| `tick`                | int24   | Current tick of the pool at the time of the swap                                             |
| `pool_tvl_at_block`   | float   | Total Value Locked in USD at the swap block (USDC balance + WETH balance × price)           |
| `slip_1k`             | float   | Simulated cost of a 1 000 USDC→WETH swap: price impact + fee tier (via QuoterV2). `None` for pre-2022 blocks (QuoterV2 not yet deployed). |

## 🗂 CSV Structure: `weth_usdc_uniswap_v2_03.csv`

Uniswap V2 WETH/USDC pool (USDC=token0, WETH=token1). Price from swap amounts; reserves from `getReserves()`. `slip_1k` simulates buying WETH with 1 000 USDC.

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block                                                                   |
| `price_usdc_per_eth`  | float   | Effective ETH price in USDC from swap amounts (`\|USDC_net\| / \|WETH_net\|`)                |
| `usdc_amount`         | float   | USDC net flow (positive = into pool)                                                         |
| `eth_amount`          | float   | WETH net flow (positive = into pool)                                                         |
| `volume_usdc`         | float   | Trade notional in USDC — `abs(usdc_amount)`                                                  |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block                                                                   |
| `pool_address`        | string  | Pool contract address                                                                        |
| `pool_fee_tier`       | int     | Pool fee tier (3000 = 0.3%)                                                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `reserve0`            | uint112 | Raw token0 (USDC) reserve at the swap block                                                  |
| `reserve1`            | uint112 | Raw token1 (WETH) reserve at the swap block                                                  |
| `pool_tvl_at_block`   | float   | Total Value Locked in USD (USDC reserve + WETH reserve × price)                              |
| `slip_1k`             | float   | Simulated cost of a 1 000 USDC→WETH swap using the V2 analytical formula                    |

## 🗂 CSV Structure: `weth_usdt_uniswap_v2_03.csv`

Uniswap V2 WETH/USDT pool (WETH=token0, USDT=token1). `slip_1k` simulates buying WETH with 1 000 USDT.

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block                                                                   |
| `price_usdt_per_eth`  | float   | Effective ETH price in USDT from swap amounts (`\|USDT_net\| / \|WETH_net\|`)                |
| `eth_amount`          | float   | WETH net flow (positive = into pool)                                                         |
| `usdt_amount`         | float   | USDT net flow (positive = into pool)                                                         |
| `volume_usdt`         | float   | Trade notional in USDT — `abs(usdt_amount)`                                                  |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block                                                                   |
| `pool_address`        | string  | Pool contract address                                                                        |
| `pool_fee_tier`       | int     | Pool fee tier (3000 = 0.3%)                                                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `reserve0`            | uint112 | Raw token0 (WETH) reserve at the swap block                                                  |
| `reserve1`            | uint112 | Raw token1 (USDT) reserve at the swap block                                                  |
| `pool_tvl_at_block`   | float   | Total Value Locked in USD (USDT reserve + WETH reserve × price)                              |
| `slip_1k`             | float   | Simulated cost of a 1 000 USDT→WETH swap using the V2 analytical formula                    |

---

## 🗂 CSV Structure: `crvusd_weth_curve.csv`

Curve pool `0x6e5492f8Ea2370844eE098a56dD88e1717E4A9C2` — coin0=crvUSD (18 dec), coin1=WETH (18 dec).
Price derived from `TokenExchange` event amounts. TVL in crvUSD (≈ USD). `slip_1k` simulates buying WETH with 1 000 crvUSD via `get_dy()`.

| Column                   | Type   | Description                                                                                |
|--------------------------|--------|--------------------------------------------------------------------------------------------|
| `timestamp`              | string | UTC timestamp of the block, e.g. `2024-04-19 23:59:59+00:00`                              |
| `price_weth_per_crvusd`  | float  | crvUSD price in WETH from swap amounts (`\|WETH_net\| / \|crvUSD_net\|`)                   |
| `crvusd_amount`          | float  | crvUSD net flow (positive = into pool, negative = out of pool)                             |
| `weth_amount`            | float  | WETH net flow (positive = into pool, negative = out of pool)                               |
| `volume_crvusd`          | float  | Trade notional in crvUSD — `abs(crvusd_amount)`                                            |
| `block_number`           | int    | Ethereum block number                                                                      |
| `transaction_hash`       | string | Transaction hash                                                                           |
| `log_index`              | int    | Log index within the block                                                                 |
| `pool_address`           | string | Curve pool contract address                                                                |
| `chain_id`               | int    | Ethereum chain ID (1 = mainnet)                                                            |
| `pool_tvl_at_block`      | float  | Total Value Locked in crvUSD (≈ USD): crvUSD balance + WETH balance / price               |
| `slip_1k`                | float  | Simulated cost of a 1 000 crvUSD→WETH swap via Curve `get_dy(0, 1, dx)`                   |

---

## 🧾 License

All contents of this repository (data, code, and documentation) are licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH**

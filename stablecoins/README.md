# Open Price Stablecoins Data Repository
Open Price Stablecoins is an open-data initiative providing standardized, continuously updated historical datasets of USDC/USD and USDT/USD prices from Chainlink on-chain oracles. Fully compliant with FAIR principles, it empowers researchers and developers with transparent, reproducible insights into stablecoin price dynamics.

---

## 📅 Available Datasets

| Dataset                     | End Date Available          | CSV File                          |
|-----------------------------|-----------------------------|-----------------------------------|
| **Chainlink USDC/USD**      | 2026-05-13 08:00:35 UTC       | `data/chainlink_usdc_usd.csv`     |
| **Chainlink USDT/USD**      | 2026-05-12 19:04:23 UTC       | `data/chainlink_usdt_usd.csv`     |

---

## 🗂 CSV Structure: `chainlink_usdc_usd.csv`

| Column             | Type    | Description                                                              |
|--------------------|---------|--------------------------------------------------------------------------|
| `global_round_id`  | uint80  | Global round identifier (`phase << 64 | aggregator_round_id`)            |
| `phase`            | int     | Chainlink contract phase identifier                                      |
| `aggregator_round` | int     | Round identifier within the given phase                                  |
| `datetime_utc`     | string  | Update timestamp in `YYYY-MM-DD HH:MM:SS` format (UTC)                   |
| `price`            | float   | USDC/USD price (scaled by 10⁸ in the contract)                          |

## 🗂 CSV Structure: `chainlink_usdt_usd.csv`

| Column             | Type    | Description                                                              |
|--------------------|---------|--------------------------------------------------------------------------|
| `global_round_id`  | uint80  | Global round identifier (`phase << 64 | aggregator_round_id`)            |
| `phase`            | int     | Chainlink contract phase identifier                                      |
| `aggregator_round` | int     | Round identifier within the given phase                                  |
| `datetime_utc`     | string  | Update timestamp in `YYYY-MM-DD HH:MM:SS` format (UTC)                   |
| `price`            | float   | USDT/USD price (scaled by 10⁸ in the contract)                          |

---

## 🧾 License

All contents of this repository (data, code, and documentation) are licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH**

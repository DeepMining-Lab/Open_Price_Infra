# Open Price UNI Data Repository
Open Price UNI is an open-data initiative providing a standardized, continuously updated historical dataset of UNI/USD prices from on-chain sources (Chainlink and Uniswap V3). Fully compliant with FAIR principles, it empowers researchers and developers with transparent, reproducible insights into UNI price dynamics.

---

## 📅 Available Datasets

| Dataset                    | End Date Available              | CSV File                                      |
|----------------------------|---------------------------------|-----------------------------------------------|
| **Chainlink UNI/USD**  | 2026-05-11 06:43:59 UTC      | `data/chainlink_uni_usd.csv`                |
| **Uniswap V3 UNI/USDC**| 2026-04-26 05:19:23 UTC        | `data/uniswap_uni_usd.csv`                  |

---

## 🗂 CSV Structure: `chainlink_uni_usd.csv`

| Column             | Type    | Description                                                              |
|--------------------|---------|--------------------------------------------------------------------------|
| `global_round_id`  | uint80  | Global round identifier (`phase << 64 | aggregator_round_id`)            |
| `phase`            | int     | Chainlink contract phase identifier                                      |
| `aggregator_round` | int     | Round identifier within the given phase                                  |
| `datetime_utc`     | string  | Update timestamp in `YYYY-MM-DD HH:MM:SS` format (UTC)                   |
| `price`            | float   | UNI/USD price (scaled by 10⁸ in the contract)                       |

## 🗂 CSV Structure: `uniswap_uni_usd.csv`

| Column                     | Type    | Description                                        |
|----------------------------|---------|----------------------------------------------------|
| `timestamp`                | string  | UTC timestamp, e.g. `2024-04-19 23:59:59+00:00`   |
| `price_usdc_per_uni`     | float   | Price in USDC per UNI                          |
| `usdc_amount`              | float   | USDC amount transferred                            |
| `uni_amount`             | float   | UNI amount transferred                         |
| `volume_usdc`              | float   | Total volume in USDC                               |
| `block_number`             | int     | Ethereum block number                              |
| `transaction_hash`         | string  | Transaction hash                                   |

---

## 🧾 License

All contents of this repository (data, code, and documentation) are licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH**

# Open Price COMP Data Repository
Open Price COMP is an open-data initiative providing a standardized, continuously updated historical dataset of COMP/USD prices from on-chain sources (Chainlink and Uniswap V3). Fully compliant with FAIR principles, it empowers researchers and developers with transparent, reproducible insights into COMP price dynamics.

---

## 📅 Available Datasets

| Dataset                    | End Date Available              | CSV File                                      |
|----------------------------|---------------------------------|-----------------------------------------------|
| **Chainlink COMP/USD**  | 2026-05-13 14:28:35 UTC      | `data/chainlink_comp_usd.csv`                |
| **Uniswap V3 COMP/USDC**| 2024-03-01 12:51:23 UTC        | `data/comp_usdc_uniswap_v3_03.csv`                  |

---

## 🗂 CSV Structure: `chainlink_comp_usd.csv`

| Column             | Type    | Description                                                              |
|--------------------|---------|--------------------------------------------------------------------------|
| `global_round_id`  | uint80  | Global round identifier (`phase << 64 | aggregator_round_id`)            |
| `phase`            | int     | Chainlink contract phase identifier                                      |
| `aggregator_round` | int     | Round identifier within the given phase                                  |
| `datetime_utc`     | string  | Update timestamp in `YYYY-MM-DD HH:MM:SS` format (UTC)                   |
| `price`            | float   | COMP/USD price (scaled by 10⁸ in the contract)                       |

## 🗂 CSV Structure: `comp_usdc_uniswap_v3_03.csv`

| Column                     | Type    | Description                                        |
|----------------------------|---------|----------------------------------------------------|
| `timestamp`                | string  | UTC timestamp, e.g. `2024-04-19 23:59:59+00:00`   |
| `price_usdc_per_comp`     | float   | Price in USDC per COMP                          |
| `usdc_amount`              | float   | USDC amount transferred                            |
| `comp_amount`             | float   | COMP amount transferred                         |
| `volume_usdc`              | float   | Total volume in USDC                               |
| `block_number`             | int     | Ethereum block number                              |
| `transaction_hash`         | string  | Transaction hash                                   |

---

## 🧾 License

All contents of this repository (data, code, and documentation) are licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH**

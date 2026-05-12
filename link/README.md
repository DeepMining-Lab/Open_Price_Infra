# Open Price LINK Data Repository
Open Price LINK is an open-data initiative providing a standardized, continuously updated historical dataset of LINK/USD prices from on-chain sources (Chainlink and Uniswap V3). Fully compliant with FAIR principles, it empowers researchers and developers with transparent, reproducible insights into LINK price dynamics.

---

## 📅 Available Datasets

| Dataset                    | End Date Available              | CSV File                                      |
|----------------------------|---------------------------------|-----------------------------------------------|
| **Chainlink LINK/USD**  | 2026-05-12 07:03:11 UTC      | `data/chainlink_link_usd.csv`                |
| **Uniswap V3 LINK/USDC**| 2026-05-06 15:46:47 UTC        | `data/link_usdc_uniswap_v3_03.csv`                  |

---

## 🗂 CSV Structure: `chainlink_link_usd.csv`

| Column             | Type    | Description                                                              |
|--------------------|---------|--------------------------------------------------------------------------|
| `global_round_id`  | uint80  | Global round identifier (`phase << 64 | aggregator_round_id`)            |
| `phase`            | int     | Chainlink contract phase identifier                                      |
| `aggregator_round` | int     | Round identifier within the given phase                                  |
| `datetime_utc`     | string  | Update timestamp in `YYYY-MM-DD HH:MM:SS` format (UTC)                   |
| `price`            | float   | LINK/USD price (scaled by 10⁸ in the contract)                       |

## 🗂 CSV Structure: `link_usdc_uniswap_v3_03.csv`

| Column                     | Type    | Description                                        |
|----------------------------|---------|----------------------------------------------------|
| `timestamp`                | string  | UTC timestamp, e.g. `2024-04-19 23:59:59+00:00`   |
| `price_usdc_per_link`     | float   | Price in USDC per LINK                          |
| `usdc_amount`              | float   | USDC amount transferred                            |
| `link_amount`             | float   | LINK amount transferred                         |
| `volume_usdc`              | float   | Total volume in USDC                               |
| `block_number`             | int     | Ethereum block number                              |
| `transaction_hash`         | string  | Transaction hash                                   |

---

## 🧾 License

All contents of this repository (data, code, and documentation) are licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH**

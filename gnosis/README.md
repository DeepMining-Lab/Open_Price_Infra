# Open Price GNOSIS Data Repository

---

## 📅 Available Datasets

| Dataset                | Start Date Available       | End Date Available     | CSV File                                          |
|------------------------|----------------------------|------------------------|---------------------------------------------------|
| **Chainlink GNO/USD**  | 2022-01-06 14:26:05 UTC    | N/A| `data/chainlink_gno_usd.csv`                      |    

Extraction date and time are taken from the CSV file’s last modification timestamp.

*(More datasets coming soon: Uniswap V2, etc.)*

---

## 🗂 CSV Structure: `chainlink_gno_usd.csv`

This file contains hourly Ether prices in USD from the Chainlink oracle on the Ethereum Mainnet.

| Column             | Type    | Description                                                                                     |
|--------------------|---------|-------------------------------------------------------------------------------------------------|
| `global_round_id`  | uint80  | Global round identifier (`phase << 64 | aggregator_round_id`)                                   |
| `phase`            | int     | Chainlink contract phase identifier                                                             |
| `aggregator_round` | int     | Round identifier within the given phase                                                         |
| `datetime_utc`     | string  | Update timestamp in `YYYY-MM-DD HH:MM:SS` format (UTC)                                          |
| `price`            | float   | GNO/USD price (converted from the integer returned by Chainlink, which is scaled by 10⁸)        |


---

## 🛠️ Auto-Generating the README

We use a Jinja2 template plus a Python script to inject the extraction date automatically based on the CSV’s last-modified timestamp

---

## 🧾 License

All contents of this repository (data, code, and documentation) are licensed under the  
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).  

You are free to use, adapt, and share, **as long as you credit the original authors**:  
**HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH**
# 🧭 Open Price is an open-data initiative providing a standardized, continuously updated historical dataset of crypto-asset prices from on-chain sources (e.g., Chainlink, Uniswap V3). Fully compliant with FAIR principles, it empowers researchers and developers with transparent, reproducible insights into the price dynamics of various blockchain ecosystems.

## 🧾 Repository Explanations

In the folders corresponding to each blockchain (e.g., "eth"), you will find the various scripts used to extract the data, as well as the script that generated the README.md file from the README.tpl.md template.
The docs folder contains information related to the web pages for each blockchain.


## 📂 Accessing CSV Data by Blockchain

You can visit the following portal, which redirects to each individual blockchain’s data repository for downloading CSV files:  
🔗 [https://fair.deepmining.ch/](https://fair.deepmining.ch/)

In each blockchain folder (e.g., `eth`), you will find the scripts used to extract the data, as well as the script used to generate the `README.md` from the `README.tpl.md` template.

The file `README.md` provides:  
- **Available date ranges** for which price data is provided  
- **Extraction methods** and on-chain data sources (e.g., Chainlink, Uniswap V3)  
- **File structure** and naming conventions (e.g., `protocol_token1_token2.csv`)  
- **Update frequency** (hourly, daily, or real-time feeds) and any known data caveats  


In the `docs` folder, you will find information related to the web pages for each blockchain.

---

### 📈 About Open Price

- 🔍 **FAIR Compliance**  
  - **Findable**: Clear folder hierarchy, metadata tags in CSV headers  
  - **Accessible**: Public HTTPS endpoints, no authentication required  
  - **Interoperable**: Uniform CSV schema across all blockchains  
  - **Reusable**: Detailed provenance and extraction scripts provided  

- 🌐 **Data Sources & Coverage**  
  - **Oracles**: Chainlink feeds for major assets 
  - **DEX Pools**: Uniswap V3 for on-chain liquidity-based pricing  

- 💡 **Use Cases**  
  - Backtesting quantitative trading strategies  
  - Academic research on price formation and volatility  
  - Building dashboards or analytics tools with up-to-the-minute and historical data  

Feel free to clone or fork any of the extraction scripts, contribute improvements, or integrate the datasets directly into your workflows for a transparent, reproducible view of blockchain price dynamics.  


### 🌐 About Website

## Jekyll Installation

If you don't have Jekyll installed yet, follow these steps:

### On Ubuntu (or Windows WSL)

```bash
sudo apt update
sudo apt install ruby-full build-essential zlib1g-dev
gem install jekyll bundler

jekyll new my-site
cd my-site
bundle exec jekyll serve
```

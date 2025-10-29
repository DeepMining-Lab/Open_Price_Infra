---
layout: page
title: Open Prices — Ethereum
menu: Ethereum
permalink: /ethereum
subtitle: Ethereum Datasets
page_class: ethereum-page
---

- {% raw %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "@id": "{{ page.url | absolute_url }}#dataset",
  "name": "Open Prices — Ethereum Datasets",
  "description": "Daily refreshed on-chain Ethereum price datasets combining Chainlink oracle feeds and Uniswap V3 swap data.",
  "url": "{{ page.url | absolute_url }}",
  "keywords": ["Ethereum", "ETH", "Chainlink", "Uniswap V3", "On-chain price", "Crypto dataset"],
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "creator": {
    "@type": "Organization",
    "name": "FairOnChain",
    "url": "https://www.faironchain.org"
  },
  "publisher": {
    "@type": "Organization",
    "name": "FairOnChain",
    "url": "https://www.faironchain.org"
  },
  "isAccessibleForFree": true,
  "distribution": [
    {
      "@type": "DataDownload",
      "name": "Chainlink ETH/USD CSV",
      "contentUrl": "https://files.deepmining.ch/files/ethereum/prices/chainlink_eth_usd.csv",
      "encodingFormat": "text/csv",
      "description": "Historical ETH/USD prices sourced from the Chainlink oracle on Ethereum Mainnet."
    },
    {
      "@type": "DataDownload",
      "name": "Uniswap V3 ETH/USDC CSV",
      "contentUrl": "https://files.deepmining.ch/files/ethereum/prices/uniswap_eth_usd.csv",
      "encodingFormat": "text/csv",
      "description": "Historical ETH/USDC swap data from the Uniswap V3 WETH/USDC pool on Ethereum."
    }
  ]
}
</script>
{% endraw %}

- The datasets below provide open, reproducible market data for research and engineering on Ethereum.

<div class="dataset-description">
<p>The datasets are updated daily and you will always have access to the latest available version. The dataset named <code>chainlink_eth_usd.csv</code> contains the complete price history from the Chainlink contract on Ethereum Mainnet, while the CSV <code>uniswap_eth_usd.csv</code> contains all swap events recorded on the Uniswap V3 WETH/USDC contract.</p>
</div>

<div class="dataset-download">
  <h3 class="dataset-download__headline">Download datasets</h3>
  <a class="dataset-download__link" href="https://files.deepmining.ch/files/ethereum/prices/" target="_blank" rel="noopener">
    files.deepmining.ch — Ethereum prices
  </a>
  <p class="dataset-download__note">Daily-updated CSV exports of prices extracted from Chainlink and Uniswap.</p>
</div>

<div class="readme-info">
<h4>The file README.md provides:</h4>
<ul>
<li>Available date ranges for which price data is provided</li>
<li>Extraction methods and on-chain data sources (e.g., Chainlink, Uniswap V3)</li>
<li>File structure and naming conventions</li>
</ul>
<p class="readme-info__link"><strong>Dataset reference:</strong> <a href="https://github.com/DeepMining-Lab/Open_Price_Infra/blob/main/eth/README.md" target="_blank" rel="noopener">README.md</a></p>
</div>

_More datasets coming soon (e.g., Uniswap V2)._ 

---

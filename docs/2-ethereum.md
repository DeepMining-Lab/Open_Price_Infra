---
layout: page
# title:
menu: Ethereum
permalink: /ethereum
# subtitle: Ethereum Datasets
page_class: ethereum-page
---

{% raw %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "@id": "https://fair.deepmining.ch/ethereum#dataset",
  "name": "Open Prices — Ethereum Datasets",
  "description": "Daily refreshed on-chain Ethereum price datasets combining Chainlink oracle feeds and Uniswap V3 swap data.",
  "url": "https://fair.deepmining.ch/ethereum",
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
      "name": "Folder containing all datasets on Ethereum prices",
      "url": "https://files.deepmining.ch/files/ethereum/prices/",
      "encodingFormat": "text/html",
      "description": "Page containing CSV files with Ethereum prices extracted from Chainlink and Uniswap V3."
    },
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

<style>
.ethereum-page {
  --surface-hero: radial-gradient(1200px circle at 10% 15%, rgba(74, 222, 128, 0.45), transparent 58%),
                  radial-gradient(1200px circle at 85% 10%, rgba(45, 212, 191, 0.4), transparent 55%),
                  linear-gradient(135deg, #022c22, #064e3b 55%, #0f172a);
  --surface-dark-card: radial-gradient(900px circle at 15% 15%, rgba(74, 222, 128, 0.45), transparent 55%),
                       radial-gradient(900px circle at 85% -10%, rgba(45, 212, 191, 0.42), transparent 50%),
                       linear-gradient(135deg, #022c22, #064e3b 55%, #0f172a);
  --surface-light-card: linear-gradient(150deg, rgba(241, 245, 249, 0.95), rgba(226, 232, 240, 0.8));
  --color-text-body: #0f172a;
  --color-text-strong: #1e293b;
  --color-text-muted: #475569;
  --color-text-light: #ecfeff;
  --color-accent: #0f766e;
  --color-border-subtle: rgba(148, 163, 184, 0.25);
  --color-border-dark: rgba(45, 212, 191, 0.35);
}
.home-page {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--color-text-body);
}
.home-hero {
  background: var(--surface-hero);
  border-radius: 28px;
  padding: 4rem min(7vw, 5rem);
  position: relative;
  overflow: hidden;
  margin: 3rem auto 4rem;
  max-width: 1100px;
  color: var(--color-text-light);
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.45);
}
.home-hero h1 {
  font-size: clamp(2.4rem, 4vw, 3.5rem);
  margin-bottom: 1rem;
}
.home-hero .eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  border-radius: 999px;
  background: rgba(248, 250, 252, 0.1);
  padding: 0.35rem 1rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-weight: 600;
  font-size: 0.75rem;
}
.home-hero p {
  max-width: 620px;
  line-height: 1.6;
  font-size: 1.05rem;
  color: rgba(236, 254, 255, 0.84);
  text-align: center;
  margin: 0.9rem auto 0;
}
.home-hero .hero-copy {
  text-align: center;
  margin: 1rem auto 0;
}
.home-hero .cta-group {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 2.5rem;
}
.home-hero .cta-primary {
  border-radius: 999px;
  padding: 0.85rem 1.8rem;
  font-weight: 600;
  text-decoration: none;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  background: linear-gradient(135deg, #4ade80, #22d3ee);
  color: #022c22;
  box-shadow: 0 12px 30px rgba(34, 211, 238, 0.3);
}
.home-hero .cta-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 36px rgba(34, 211, 238, 0.4);
}
.home-hero .hero-note {
  font-size: 0.92rem;
  color: rgba(226, 232, 240, 0.8);
  margin-top: 2.2rem;
}
.section {
  max-width: 1100px;
  margin: 0 auto 4rem;
  padding: 0 min(7vw, 5rem);
}
.section h2 {
  font-size: clamp(1.8rem, 3vw, 2.4rem);
  margin-bottom: 2rem;
  color: #f8fafc;
}

.daily-grid {
  display: flex;
  justify-content: center;
  gap: 1.2rem;
  flex-wrap: wrap;
}
.daily-card {
  border-radius: 18px;
  padding: 1.6rem;
  background: var(--surface-light-card);
  border: 1px solid var(--color-border-subtle);
  box-shadow: 0 20px 35px rgba(15, 23, 42, 0.1);
  width: 100%;
  max-width: 220px;
  flex: 1 1 210px;
  text-align: center;
  color: var(--color-text-muted);
}
.daily-card h3 {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  font-size: 1rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-strong);
}
.daily-card p {
  margin-top: 0.8rem;
  color: var(--color-text-muted);
  line-height: 1.55;
  font-size: 0.98rem;
  text-align: center;
}



.documentation-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.6rem;
  justify-items: center;
}
.documentation-card {
  border-radius: 18px;
  padding: 1.6rem;
  background: var(--surface-dark-card);
  border: 1px solid var(--color-border-subtle);
  box-shadow: 0 20px 35px rgba(15, 23, 42, 0.1);
  width: 100%;
  max-width: 340px;
  text-align: center;
  color: var(--color-text-muted);
  justify-self: stretch;
}
.documentation-card h3 {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 1rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-weight: 600;
  color: var(--color-text-light);
  text-align: center;
}
.documentation-card h3 .emoji {
  font-size: 1.6rem;
}
.documentation-card p {
  margin-top: 0.8rem;
  /* color: #334155 !important; */
  color: rgba(236, 254, 255, 0.84);
  line-height: 1.55;
  font-size: 0.98rem;
  text-align: center !important;
}
.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.6rem;
}
.dataset-grid {
  display: flex;
  justify-content: center;
  gap: 1.4rem;
  flex-wrap: wrap;
}
.dataset-card {
  max-width: 360px;
  flex: 1 1 360px;
  color: var(--color-text-muted);
}
.data-card {
  border-radius: 18px;
  padding: 1.8rem;
  background: var(--surface-dark-card);
  color: var(--color-text-light);
  box-shadow: 0 18px 40px rgba(4, 120, 87, 0.35);
  border: 1px solid var(--color-border-dark);
}
.data-card h3 {
  margin-bottom: 0.8rem;
  font-size: 1.15rem;
  color: var(--color-text-light);
}
.data-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.data-card li {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.45rem 0;
  border-bottom: 1px solid rgba(236, 254, 255, 0.25);
}
.data-card li:last-child {
  border-bottom: none;
}
.data-card span {
  font-weight: 700;
  color: inherit;
}
.usecase-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.4rem;
}
.usecase-card {
  border-radius: 16px;
  background: var(--surface-light-card);
  border: 1px solid var(--color-border-subtle);
  padding: 1.6rem;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
  color: var(--color-text-strong);
  text-align: center;
}
.usecase-card h3 {
  font-size: 1.1rem;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-weight: 600;
  color: #1e293b !important;
  margin-bottom: 0.7rem;
}
.usecase-card p {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #334155 !important;
  line-height: 1.6;
  font-size: 0.98rem;
  text-align: center;
}
.usecase-card a {
  color: var(--color-accent);
  font-weight: 600;
  text-decoration: underline;
}
.dataset-reference {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #1e293b;
  margin-top: 1rem;
}
.dataset-reference strong {
  color: #1e293b;
  font-weight: 600;
}
.dataset-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.35rem 0.9rem;
  border-radius: 999px;
  background: var(--surface-dark-card);
  border: 1px solid var(--color-border-subtle);
  box-shadow: 0 10px 20px rgba(15, 23, 42, 0.12);
  color: #1e293b !important;
  font-weight: 600;
  font-size: 0.85rem;
  text-decoration: none;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.dataset-button:hover {
  transform: translateY(-1px);
  text-decoration: none;
  box-shadow: 0 12px 26px rgba(15, 23, 42, 0.18);
}
.dataset-button:focus-visible {
  outline: 3px solid rgba(34, 211, 238, 0.55);
  outline-offset: 3px;
  text-decoration: none;
}
.dataset-card {
  max-width: 320px;
  flex: 1 1 320px;
  color: var(--color-text-muted);
}
.dataset-logo {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: calc(2rem - 5cm) auto 2rem;
  position: relative;
  isolation: isolate;
}
.dataset-logo::before {
  content: "";
  position: absolute;
  inset: -1.8rem;
  border-radius: 50%;
  background: radial-gradient(circle at 50% 30%, rgba(2, 44, 34, 0.6), rgba(2, 44, 34, 0.22) 55%, transparent 72%);
  filter: blur(6px);
  opacity: 0.8;
  z-index: -1;
  transition: transform 0.4s ease, opacity 0.4s ease;
}
.eth-logo {
  width: 80px;
  height: auto;
  filter: drop-shadow(0 14px 32px rgba(2, 44, 34, 0.45));
  animation: floatLogo 5s ease-in-out infinite;
  will-change: transform;
  transition: transform 0.35s ease, filter 0.35s ease;
}
.dataset-logo:hover .eth-logo {
  animation: none;
  transform: translateY(-12px) scale(1.08);
  filter: drop-shadow(0 20px 42px rgba(2, 44, 34, 0.65));
}
.dataset-logo:hover::before {
  opacity: 1;
  transform: scale(1.08);
}
@keyframes floatLogo {
  0%,
  100% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  50% {
    transform: translate3d(0, -14px, 0) scale(1.05);
  }
}
.dataset-card h3 {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  font-size: 1rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-weight: 600;
  color: #1e293b !important;
}
.dataset-card h3 span {
  color: #1e293b !important;
  font-weight: 600;
  letter-spacing: inherit;
  text-transform: inherit;
}
.dataset-card p {
  text-align: center;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #334155 !important;
}
.dataset-card p strong {
  display: block;
  color: #1e293b !important;
  font-weight: 600;
}
.dataset-file-name,
.dataset-file-name-inline {
  font-weight: 600;
  color: inherit;
}
.dataset-file-name-inline {
  display: inline-block;
  margin-left: 0.35rem;
}
.dataset-icon {
  font-size: 1.1rem;
}
@media (max-width: 720px) {
  .home-hero {
    padding: 3.2rem 2.2rem;
    border-radius: 22px;
  }
  .home-hero .cta-group {
    flex-direction: column;
  }
  .home-hero .cta-primary {
    width: 100%;
    justify-content: center;
    text-align: center;
  }
  .fair-card,
  .data-card,
  .dataset-card,
  .usecase-card {
    max-width: 100%;
  }
  .dataset-logo {
    margin: 0 auto 2rem;
  }
  .dataset-logo::before {
    inset: -1.2rem;
  }
  .documentation-grid {
    grid-template-columns: 1fr;
  }
  .section {
    padding: 0 1.2rem;
  }
}
</style>

<div class="home-page ethereum-page">
  <div class="dataset-logo" aria-hidden="true">
    <svg class="eth-logo" viewBox="0 0 256 417" role="img">
      <title>Ethereum Logo</title>
      <polygon fill="#343434" points="127.6,0 125.4,7.2 125.4,277.4 127.6,279.6 255.1,212.5"/>
      <polygon fill="#8C8C8C" points="127.6,0 0.1,212.5 127.6,279.6"/>
      <polygon fill="#3C3C3B" points="127.6,305 127.6,416.8 255.2,236.3"/>
      <polygon fill="#8C8C8C" points="127.6,416.8 0,236.3 127.6,305"/>
      <polygon fill="#141414" points="127.6,279.6 255.1,212.5 127.6,159.1"/>
      <polygon fill="#393939" points="0.1,212.5 127.6,279.6 127.6,159.1"/>
    </svg>
  </div>
  <section class="home-hero">
    <span class="eyebrow">Ethereum datasets</span>
    <h1>Open Prices — Ethereum</h1>
    <p class="hero-copy">The datasets below provide open, reproducible market data for research and engineering on Ethereum.</p>
    <p class="hero-copy">The datasets are updated daily and you will always have access to the latest available version. The dataset named <span class="dataset-file-name">chainlink_eth_usd.csv</span> contains the complete price history from the Chainlink contract on Ethereum Mainnet, while the CSV <span class="dataset-file-name">uniswap_eth_usd.csv</span> contains all swap events recorded on the Uniswap V3 WETH/USDC contract.</p>
    <div class="cta-group">
      <a class="cta-primary" href="https://files.deepmining.ch/files/ethereum/prices/" target="_blank" rel="noopener">
        Download Ethereum price CSVs
      </a>
    </div>
    <p class="hero-note">Daily-updated CSV exports of prices extracted from Chainlink and Uniswap.</p>
  </section>

  <section class="section">
    <h2>Daily refreshed price feeds</h2>
    <div class="daily-grid dataset-grid">
      <div class="daily-card dataset-card">
        <h3><span class="dataset-icon" aria-hidden="true">🔷</span><span>Chainlink ETH/USD</span></h3>
        <p>Complete history from the Chainlink price feed on Ethereum Mainnet.</p>
        <p>Daily updates keep the dataset aligned with the latest on-chain observations.</p>
        <p><strong>File name :</strong><span class="dataset-file-name-inline">chainlink_eth_usd.csv</span></p>
      </div>
      <div class="daily-card dataset-card">
        <h3><span class="dataset-icon" aria-hidden="true">🦄</span><span>Uniswap V3 ETH/USDC</span></h3>
        <p>Swap events captured from the Uniswap V3 WETH/USDC pool on Ethereum.</p>
        <p>Market microstructure preserved for volatility and slippage studies.</p>
        <p><strong>File name :</strong><span class="dataset-file-name-inline">uniswap_eth_usd.csv</span></p>
      </div>
    </div>
  </section>

  <section class="section">
    <h2>Documentation at a glance</h2>
    <div class="documentation-grid">
      <div class="documentation-card">
        <h3><span class="emoji" aria-hidden="true">📁</span>Folder structure</h3>
        <p>Structured folder hierarchy and descriptive metadata inside each CSV make discovery and filtering straightforward.</p>
      </div>
      <div class="documentation-card">
        <h3><span class="emoji" aria-hidden="true">📅</span>Coverage</h3>
        <p>Available date ranges for which price data is provided are clearly stated so you know the historical span.</p>
      </div>
      <div class="documentation-card">
        <h3><span class="emoji" aria-hidden="true">⚙️</span>Extraction</h3>
        <p>Extraction methods and on-chain data sources, including Chainlink and Uniswap V3, are documented for full transparency.</p>
      </div>
      <div class="documentation-card">
        <h3><span class="emoji" aria-hidden="true">🔤</span>Naming</h3>
        <p>File structure and naming conventions are explained to streamline notebook loading and pipeline integration.</p>
      </div>
    </div>
  </section>

  <section class="section">
    <h2>Resources</h2>
    <div class="usecase-grid">
      <div class="usecase-card">
        <h3>Dataset reference</h3>
        <p>The repository README catalogues the dataset reference for Ethereum price files.</p>
        <div class="dataset-reference">
          <strong>Dataset reference:</strong>
          <a class="dataset-button" href="https://github.com/DeepMining-Lab/Open_Price_Infra/blob/main/eth/README.md" target="_blank" rel="noopener">README.md</a>
        </div>
      </div>
      <div class="usecase-card">
        <h3>More datasets coming</h3>
        <p>More datasets are coming soon (e.g., Uniswap V2).</p>
      </div>
    </div>
  </section>
</div>

---
layout: page
# title:
menu: Ethereum
permalink: /ethereum
# subtitle: Ethereum Datasets
page_class: ethereum-page
---

{%- assign data = site.data.ethereum_datasets -%}
{%- assign dataset_count = 0 -%}
{%- assign sources = "" -%}
{%- assign since_dates = "" -%}
{%- for asset in data.assets -%}
  {%- assign dataset_count = dataset_count | plus: asset.datasets.size -%}
  {%- for d in asset.datasets -%}
    {%- assign sources = sources | append: d.source | append: "|" -%}
    {%- assign since_dates = since_dates | append: d.since | append: "|" -%}
  {%- endfor -%}
{%- endfor -%}
{%- assign source_count = sources | split: "|" | uniq | size -%}
{%- assign coverage_start = since_dates | split: "|" | sort | first -%}

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "@id": "https://fair.deepmining.ch/ethereum#dataset",
  "name": "Open Prices — Ethereum Datasets",
  "description": "Daily refreshed on-chain price datasets extracted from Ethereum Mainnet: Chainlink oracle feeds and swap events from Uniswap V2, Uniswap V3, SushiSwap V2 and SushiSwap V3 pools, for ETH, LINK, UNI, AAVE, COMP and the USDC and USDT stablecoins.",
  "url": "https://fair.deepmining.ch/ethereum",
  "temporalCoverage": {{ coverage_start | append: "/.." | jsonify }},
  "keywords": ["Ethereum", "ETH", "LINK", "UNI", "AAVE", "COMP", "USDC", "USDT", "Chainlink", "Uniswap V2", "Uniswap V3", "SushiSwap", "On-chain price", "Crypto dataset"],
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
      "url": {{ data.download_url | jsonify }},
      "encodingFormat": "text/html",
      "description": "Page containing the CSV files of prices extracted from Ethereum Mainnet."
    }
    {%- for asset in data.assets -%}
    {%- for d in asset.datasets -%}
    {%- if d.source == "Chainlink" -%}
      {%- capture d_description -%}Every price round of the Chainlink {{ d.pair }} feed on Ethereum Mainnet.{%- endcapture -%}
    {%- else -%}
      {%- capture d_description -%}Every swap event of the {{ d.source }} {{ d.pair }} {{ d.fee }} pool on Ethereum Mainnet.{%- endcapture -%}
    {%- endif %},
    {
      "@type": "DataDownload",
      "name": {{ d.source | append: " " | append: d.pair | append: " CSV" | jsonify }},
      "contentUrl": {{ data.download_url | append: d.file | jsonify }},
      "encodingFormat": "text/csv",
      "temporalCoverage": {{ d.since | append: "/.." | jsonify }},
      "description": {{ d_description | jsonify }}
    }
    {%- endfor -%}
    {%- endfor %}
  ]
}
</script>

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
.dataset-grid {
  display: flex;
  justify-content: center;
  gap: 1.4rem;
  flex-wrap: wrap;
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
  max-width: 280px;
  flex: 1 1 220px;
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
    box-sizing: border-box;
    justify-content: center;
    text-align: center;
  }
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
  .documentation-card {
    box-sizing: border-box;
    max-width: 100%;
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
    <p class="hero-copy">Every price below is read directly from Ethereum Mainnet: the rounds of Chainlink oracle feeds and the swap events of Uniswap and SushiSwap pools. Each CSV holds the complete history of its source and is updated daily.</p>
    <ul class="hero-stats">
      <li><strong>{{ dataset_count }}</strong><span>CSV datasets</span></li>
      <li><strong>{{ source_count }}</strong><span>on-chain sources</span></li>
      <li><strong>Daily</strong><span>updates</span></li>
    </ul>
    <div class="cta-group">
      <a class="cta-primary" href="{{ data.download_url }}" target="_blank" rel="noopener">
        Download Ethereum price CSVs
      </a>
    </div>
    <p class="hero-note">All files sit in a single public folder, no authentication required.</p>
  </section>

  <nav class="asset-nav" aria-label="Datasets by asset">
    {%- for asset in data.assets %}
    <a href="#{{ asset.id }}">{{ asset.name }}</a>
    {%- endfor %}
  </nav>

  <section class="section">
    <h2>Where the prices come from</h2>
    <div class="daily-grid dataset-grid">
      <div class="daily-card dataset-card">
        <h3><span class="dataset-icon" aria-hidden="true">🔷</span><span>Chainlink</span></h3>
        <p>Oracle price feeds. One row per price round: round id, phase, answer and update time, as returned by the feed contract.</p>
      </div>
      <div class="daily-card dataset-card">
        <h3><span class="dataset-icon" aria-hidden="true">🦄</span><span>Uniswap V2 &amp; V3</span></h3>
        <p>Liquidity pools. One row per swap event, with the swapped amounts, the resulting price and the pool liquidity at that block.</p>
      </div>
      <div class="daily-card dataset-card">
        <h3><span class="dataset-icon" aria-hidden="true">🍣</span><span>SushiSwap V2 &amp; V3</span></h3>
        <p>The same swap-level schema as Uniswap, for the SushiSwap pools that pair each asset with ETH.</p>
      </div>
    </div>
  </section>

  <section class="section">
    <h2>Datasets by asset</h2>
    <p class="section-intro">DEX files are named <code>tokenA_tokenB_dex_version_fee.csv</code>, with the fee tier written without its dot (0.3% becomes <code>03</code>). Oracle files are named <code>chainlink_base_quote.csv</code>. The Since column gives the UTC date of the first swap or oracle round in each file.</p>
    {%- for asset in data.assets %}
    <div class="asset-block" id="{{ asset.id }}">
      <div class="asset-heading">
        <h3>{{ asset.name }}</h3>
        <span class="asset-label">{{ asset.label }}</span>
        <a class="dataset-button" href="{{ data.repo_url }}/blob/main/{{ asset.readme }}" target="_blank" rel="noopener">README · column reference</a>
      </div>
      <table class="dataset-table">
        <thead>
          <tr><th scope="col">Pair</th><th scope="col">Source</th><th scope="col">Fee tier</th><th scope="col">Since</th><th scope="col">Contract</th><th scope="col">CSV file</th></tr>
        </thead>
        <tbody>
          {%- for d in asset.datasets %}
          <tr>
            <td data-label="Pair">
              <strong>{{ d.pair }}</strong>
              {%- if d.status == "inactive" %}
              <span class="status-badge">Inactive pool</span>
              <span class="status-note">{{ d.note }}</span>
              {%- endif %}
            </td>
            <td data-label="Source">{{ d.source }}</td>
            <td data-label="Fee tier">{{ d.fee | default: "—" }}</td>
            <td data-label="Since"><time datetime="{{ d.since }}">{{ d.since }}</time></td>
            <td data-label="Contract"><a href="https://etherscan.io/address/{{ d.contract }}" target="_blank" rel="noopener" title="{{ d.contract }}"><code>{{ d.contract | slice: 0, 6 }}…{{ d.contract | slice: -4, 4 }}</code></a></td>
            <td data-label="CSV file"><a href="{{ data.download_url }}{{ d.file }}" target="_blank" rel="noopener"><code>{{ d.file | replace: "_", "_<wbr>" }}</code></a></td>
          </tr>
          {%- endfor %}
        </tbody>
      </table>
    </div>
    {%- endfor %}
  </section>

  <section class="section">
    <h2>Provenance in every row</h2>
    <div class="documentation-grid">
      <div class="documentation-card">
        <h3><span class="emoji" aria-hidden="true">🧾</span>Extraction fingerprint</h3>
        <p>Each row carries its extraction run id, the schema version and the SHA-256 hashes of the extraction script and of the contract ABI used.</p>
      </div>
      <div class="documentation-card">
        <h3><span class="emoji" aria-hidden="true">⛓️</span>Node &amp; block anchoring</h3>
        <p>The RPC client and version, the chain id and the node head block at extraction time are recorded, plus the block hash and transaction index of every swap.</p>
      </div>
      <div class="documentation-card">
        <h3><span class="emoji" aria-hidden="true">💧</span>Liquidity context</h3>
        <p>DEX rows include the pool TVL at the swap block and the simulated slippage of a 1k and a 10k swap, to judge how representative each price is.</p>
      </div>
      <div class="documentation-card">
        <h3><span class="emoji" aria-hidden="true">🚩</span>Quality flags</h3>
        <p>Swaps are flagged <code>low_liquidity</code>, <code>zero_amount</code> or <code>extreme_slippage</code>. Chainlink rounds carry an answer status such as <code>answered_in_old_round</code>.</p>
      </div>
    </div>
  </section>

  <section class="section">
    <h2>Resources</h2>
    <div class="usecase-grid">
      <div class="usecase-card">
        <h3>Extraction code</h3>
        <p>The Python extraction scripts, the Docker setup and the README of every asset, with the full column reference and the latest date available per file.</p>
        <div class="dataset-reference">
          <a class="dataset-button" href="{{ data.repo_url }}" target="_blank" rel="noopener">Open_Price_Infra on GitHub</a>
        </div>
      </div>
      <div class="usecase-card">
        <h3>Query prices through the API</h3>
        <p>The OpenPrice API reads these CSV files and returns the price of an asset at any timestamp, with its source, a confidence score and its full provenance.</p>
        <div class="dataset-reference">
          <a class="dataset-button" href="{{ data.api_url }}" target="_blank" rel="noopener">openprice-api on GitHub</a>
        </div>
      </div>
      <div class="usecase-card">
        <h3>Open Price Explorer</h3>
        <p>Query the API from your browser, with nothing to install: pick a token, a date and a granularity, and see the price with its confidence score and provenance. Test API keys are available on request.</p>
        <div class="dataset-reference">
          <a class="dataset-button" href="{{ data.explorer_url }}" target="_blank" rel="noopener">Open the Explorer ↗</a>
          <a class="dataset-button" href="/contact?subject=api-key">Request a test key</a>
        </div>
      </div>
    </div>
  </section>
</div>

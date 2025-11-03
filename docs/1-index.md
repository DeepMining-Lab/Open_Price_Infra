---
layout: page
title: Open prices
menu: Home
permalink: /
subtitle: Open-data initiative providing a standardized, continuously updated historical dataset of prices
#hero_video: "https://media.githubusercontent.com/media/FairOnChain/faironchain.github.io/main/assets/video/home.mp4"
#hero_video: "assets/video/home.mp4"
hero_video: "assets/video/home_h264.mp4"
logo_img: /assets/img/faironchain-white.png
---


<style>
.home-page {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #0f172a;
}
.home-hero {
  background:
    radial-gradient(1200px circle at 10% 15%, rgba(74, 222, 128, 0.45), transparent 58%),
    radial-gradient(1200px circle at 85% 10%, rgba(45, 212, 191, 0.4), transparent 55%),
    linear-gradient(135deg, #022c22, #064e3b 55%, #0f172a);
  border-radius: 28px;
  padding: 4rem min(7vw, 5rem);
  position: relative;
  overflow: hidden;
  margin: 3rem auto 4rem;
  max-width: 1100px;
  color: #f8fafc;
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
  color: rgba(241, 245, 249, 0.86);
  text-align: center;
  margin: 0 auto;
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
.fair-grid {
  display: flex;
  justify-content: center;
  gap: 1.2rem;
  flex-wrap: wrap;
}
.fair-card {
  border-radius: 18px;
  padding: 1.6rem;
  background: linear-gradient(150deg, rgba(241, 245, 249, 0.95), rgba(226, 232, 240, 0.8));
  border: 1px solid rgba(148, 163, 184, 0.25);
  box-shadow: 0 20px 35px rgba(15, 23, 42, 0.1);
  width: 100%;
  max-width: 220px;
  flex: 1 1 210px;
  text-align: center;
}
.fair-card h3 {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  font-size: 1rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #1e293b;
}
.fair-card p {
  margin-top: 0.8rem;
  color: #334155;
  line-height: 1.55;
  font-size: 0.98rem;
  text-align: center;
}
.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.6rem;
}
.data-card {
  border-radius: 18px;
  padding: 1.8rem;
  background:
    radial-gradient(900px circle at 15% 15%, rgba(74, 222, 128, 0.45), transparent 55%),
    radial-gradient(900px circle at 85% -10%, rgba(45, 212, 191, 0.42), transparent 50%),
    linear-gradient(135deg, #022c22, #064e3b 55%, #0f172a);
  color: #ecfeff;
  box-shadow: 0 18px 40px rgba(4, 120, 87, 0.35);
}
.data-card h3 {
  margin-bottom: 0.8rem;
  font-size: 1.15rem;
  color: #f8fafc;
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
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
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
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.4rem;
}
.usecase-card {
  border-radius: 16px;
  background: linear-gradient(150deg, rgba(241, 245, 249, 0.95), rgba(226, 232, 240, 0.8));
  border: 1px solid rgba(148, 163, 184, 0.25);
  padding: 1.6rem;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
}
.usecase-card h3 {
  font-size: 1.1rem;
  color: #1e293b;
  margin-bottom: 0.7rem;
}
.usecase-card p {
  color: #475569;
  line-height: 1.6;
  font-size: 0.98rem;
  text-align: center;
}
.footer-card {
  max-width: 900px;
  margin: 0 auto 5rem;
  padding: 2.2rem 3rem;
  border-radius: 20px;
  background:
    radial-gradient(900px circle at 15% 15%, rgba(74, 222, 128, 0.45), transparent 55%),
    radial-gradient(900px circle at 85% -10%, rgba(45, 212, 191, 0.42), transparent 50%),
    linear-gradient(135deg, #022c22, #064e3b 55%, #0f172a);
  border: 1px solid rgba(45, 212, 191, 0.35);
  text-align: center;
  color: #ecfeff;
  box-shadow: 0 18px 40px rgba(4, 120, 87, 0.35);
}
.footer-card a {
  color: inherit;
  font-weight: 700;
  text-decoration: none;
  border-bottom: 1px solid rgba(236, 254, 255, 0.4);
}
.footer-card a:hover {
  border-color: rgba(236, 254, 255, 0.65);
}
@media (max-width: 720px) {
  .home-hero {
    padding: 3.2rem 2.2rem;
    border-radius: 22px;
  }
  .home-hero .cta-group {
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }
  .fair-grid {
    flex-wrap: wrap;
  }
  .fair-card {
    max-width: 260px;
    flex: 1 1 220px;
  }
  .section {
    padding: 0 1.2rem;
  }
}
</style>

<div class="home-page">
  <section class="home-hero">
    <span class="eyebrow">Open data, On-chain trust</span>
    <h1>Continuously updated, research-grade crypto price history</h1>
    <p>
      Open Price brings together on-chain oracle and DEX pool observations into a unified, transparent archive.
      The dataset is standardized, reproducible, and fully aligned with the
      <strong>FAIR</strong> principles so researchers and builders can move from question to insight without friction.
    </p>
    <div class="cta-group">
      <a class="cta-primary" href="https://github.com/DeepMining-Lab/Open_Price_Infra" target="_blank" rel="noopener">Explore the GitHub repository</a>
    </div>
  </section>

  <section class="section" id="fair-principles">
    <h2>FAIR by construction</h2>
    <div class="fair-grid">
      <div class="fair-card">
        <h3>🔍 Findable</h3>
        <p>Structured folder hierarchy and descriptive metadata inside each CSV make discovery and filtering straightforward.</p>
      </div>
      <div class="fair-card">
        <h3>🌐 Accessible</h3>
        <p>Hosted through open HTTPS endpoints with zero authentication, enabling frictionless programmatic and human access.</p>
      </div>
      <div class="fair-card">
        <h3>🧩 Interoperable</h3>
        <p>Uniform schemas, consistent timestamping, and shared data dictionaries ensure cross-chain comparability out of the box.</p>
      </div>
      <div class="fair-card">
        <h3>♻️ Reusable</h3>
        <p>Detailed provenance, extraction scripts, and versioned releases document every assumption for reproducible research.</p>
      </div>
    </div>
  </section>

  <section class="section">
    <h2>Curated coverage across market primitives</h2>
    <div class="data-grid">
      <div class="data-card">
        <h3>Oracle feeds</h3>
        <ul>
          <li><span>Chainlink</span> price references for major assets</li>
          <li>Block-level snapshots with precise update cadence</li>
          <li>Historical backfill ready for statistical modeling</li>
        </ul>
      </div>
      <div class="data-card">
        <h3>DEX liquidity pools</h3>
        <ul>
          <li><span>Uniswap V3</span> ticks, liquidity, and swap-aware prices</li>
          <li>Covers the Ethereum blockchain and others to come</li>
          <li>Supports market microstructure and slippage studies</li>
        </ul>
      </div>
    </div>
  </section>

  <section class="section">
    <h2>Built for teams shipping faster</h2>
    <div class="usecase-grid">
      <div class="usecase-card">
        <h3>Quant & DeFi research</h3>
        <p>Load clean historical curves into notebooks or pipelines to calibrate strategies, explore volatility, and stress-test assumptions.</p>
      </div>
      <div class="usecase-card">
        <h3>Data products & dashboards</h3>
        <p>Power interactive visualizations and monitoring tools with harmonized feeds that stay in sync as new blocks arrive.</p>
      </div>
      <div class="usecase-card">
        <h3>Academic collaborations</h3>
        <p>Transparent sourcing and documented methodology enable peer review, replication, and cross-institutional knowledge sharing.</p>
      </div>
    </div>
  </section>

  <div class="footer-card">
    This project is part of the European initiative <a href="https://www.faironchain.org" target="_blank" rel="noopener">FairOnChain</a>,
    which provides open infrastructure for accessing and researching blockchain data.
  </div>
</div>

---
layout: page
# title: Open Prices — Gnosis
menu: Gnosis
permalink: /gnosis
#subtitle: Gnosis datasets
page_class: gnosis-page
---

<style>
.gnosis-page .gnosis-logo {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: calc(3rem - 5cm) auto 2rem;
  position: relative;
  isolation: isolate;
}
.gnosis-page .gnosis-logo::before {
  content: "";
  position: absolute;
  inset: -1.8rem;
  border-radius: 50%;
  background: radial-gradient(circle at 50% 30%, rgba(2, 44, 34, 0.6), rgba(2, 44, 34, 0.22) 55%, transparent 72%);
  filter: blur(6px);
  opacity: 0.82;
  z-index: -1;
  transition: transform 0.4s ease, opacity 0.4s ease;
}
.gnosis-page .gnosis-logo img {
  width: 120px;
  height: auto;
  display: block;
  filter: drop-shadow(0 14px 32px rgba(2, 44, 34, 0.45));
  animation: floatLogo 5s ease-in-out infinite;
  will-change: transform;
  transition: transform 0.35s ease, filter 0.35s ease;
}
.gnosis-page .gnosis-logo:hover img {
  animation: none;
  transform: translateY(-12px) scale(1.08);
  filter: drop-shadow(0 20px 42px rgba(2, 44, 34, 0.65));
}
.gnosis-page .gnosis-logo:hover::before {
  opacity: 1;
  transform: scale(1.08);
}
.gnosis-page .gnosis-announcement {
  text-align: center;
  font-size: 1.05rem;
  line-height: 1.6;
  margin: 0 0 3rem;
  color: #f8fafc;
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
@media (max-width: 720px) {
  .gnosis-page .gnosis-logo {
    margin: 2rem auto 1.5rem;
  }
  .gnosis-page .gnosis-logo::before {
    inset: -1.2rem;
  }
}
</style>

<div class="gnosis-logo" aria-hidden="true">
  <img src="assets/img/logo/gnosis.png" alt="Gnosis logo">
</div>

<p class="gnosis-announcement">Gnosis Chain datasets are coming soon. We are aligning the data pipelines before opening public downloads.</p>

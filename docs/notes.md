# notes

## 2026-04-18 — session that started this

Context: Norayr's 401k sat in S&P 500 which hit 7041 on 2026-04-17. He called
7000 by spring/summer 2026 back in early 2024. Correct within the season window.

### Fits tried

| method | result |
|--------|--------|
| 1-line log-linear (1871-2023) | 4.66%/yr, hides all structure |
| PWLF 3 segments | splits at 1942 (gold-std end) and 1981 (Volcker) — 1.77 / 6.70 / 7.94% |
| PWLF 5 segments | splits add 1947 (WWII fiat) and 1998 (dot-com peak) |
| PWLF 6 segments | isolates 2010-2023 at **11.20%** — key |
| PWLF 7 segments | further splits 2000-2014 (lost decade) from 2014-2023 QE |
| Line through 2011 + 2025 minima | 12.23%/yr — matches eye |
| ln(ln(P)) linear fit | post-2010 is 12.7× cleaner than full series |

### Actual vs fits as of 2026-04-17 (S&P = 7041)

- Two-minima line says we should be at **6501** → we are **8% above**
- 3-segment PWLF 1981-2023 slope says **5500** → we are **28% above**
- Post-2010 OLS log-linear says **6149** → we are **14% above**

All three say we're running hot but not euphoric. 1999 ran 60% above trend.
2021 COVID-bubble peak ran 25% above.

### Sornette LPPL connection

Post-session found: exactly what Norayr derived empirically is the framework
Didier Sornette has published since 1996 as the Log-Periodic Power Law Singularity
(LPPLS) model.

Core equation:
```
log(P(t)) = A + B(tc - t)^m + C(tc - t)^m cos(ω log(tc - t) - φ)
```
- `tc` = critical time (crash)
- `m` ∈ (0, 1) = power-law exponent → super-exp
- `ω` = log-periodic angular frequency ≈ 6-13 (empirical)
- oscillatory term = bubble/antibubble log-periodic decorations

Recent S&P applications:
- Sornette group — LPPLS bubble indicators over 2 centuries of S&P 500 (2017, ScienceDirect)
- Shu & Song 2024 — LPPLS detection 1993-2025 (SSRN 4734944)
- arXiv 2510.10878 (2025) — "Hyped LPPL" variant
- Nature HSSC 2025 — AI-augmented LPPL classifier
- Confirmed S&P was in LPPL bubble regime 2020-04 → 2021-12
- Current 2023-09+ data shows re-entry into super-exp

### What would signal regime end (from LPPL literature)

1. **Log-periodic oscillation frequency increases** as tc approaches — price
   makes progressively higher/lower swings at shrinking time intervals
2. **Volatility compression → abrupt spike** (VIX crush then crush)
3. **Credit spreads widen** while equity keeps ripping — divergence
4. **Margin debt** / brokerage leverage parabolic
5. **Capex/revenue ratio** of momentum leaders explodes (today: NVDA, AAPL, MSFT)
6. **Breadth narrows** — fewer stocks carry the index higher

### Open hypotheses

- The monotone accelerator is driven by (a) Fed balance sheet + passive flows,
  (b) AI capex concentration in 7 names, (c) global savings glut seeking US equity
- Any one breaking → regime ends. All three breaking simultaneously → LPPL crash
- Norayr's 2010 regime-start intuition corresponds to QE1-QE2 overlap
  (Nov 2008 + Nov 2010) plus post-GFC fiscal expansion

### To do

- [ ] Fit LPPLS parameters to current regime and extract `tc` estimate
- [ ] Plot log-periodic residuals from the 2-minima line
- [ ] Extend data automatically (multpl scraper, run daily)
- [ ] Compare with Nasdaq 100 and NVDA individually — are they further along?
- [ ] Backtest LPPL warnings pre-1987, pre-2000, pre-2008

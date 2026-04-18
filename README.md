# finance_sp500 — super-exponential equity regime study

Personal notebook. Started 2026-04-18, M5 Max.

## What this is

Eyeball-first analysis of the S&P 500 from 1871 to today, testing whether the
post-2010 leg is a normal exponential bull regime or something stronger —
**super-exponential**, i.e. ln(ln(price)) linear in time.

Rediscovered from scratch; later confirmed by Sornette's LPPL (Log-Periodic
Power Law) framework which has been publishing this thesis since 1996.

## Thesis

1. Long-run S&P is exponential. A 3-segment log-linear fit over 155 years
   picks the two macro inflections by itself: **1942** (gold standard end) and
   **1981** (Volcker pivot). Nothing else.
2. The 1981-2023 leg is **7.94%/yr** in the long-run fit — but that's the
   *average* across distinct sub-regimes.
3. A 6-segment fit isolates **2010→present** as its own clean monotone regime
   at **11.20%/yr** with volatility compression and no trend-breaking drawdown
   through COVID, 2022 rate shock, or 2025 pullback.
4. A straight line through the two modern local minima (Aug 2011 at 1185 and
   Mar 2025 at 5684) gives **12.23%/yr** — visually parallel to the PWLF
   segment. Eye and algorithm converge.
5. ln(ln(price)) vs time is **12.7× more linear** on post-2010 data than on
   the full series. This is the super-exponential fingerprint.
6. Sornette's LPPL calls this a **finite-time singularity** — a regime that
   cannot continue indefinitely. The ending signature is log-periodic
   oscillations near the critical time.

## Files

```
src/full_history.py    1871-2026 full series + N-segment PWLF + projection
src/minima_line.py     line through two modern local minima + 6-seg PWLF + recent dashed
src/loglog.py          ln(ln(price)) transform — test for super-exponential
data/shiller.xls       Robert Shiller monthly composite, 1871-2023
                       (recent 2023-10 → 2026-04 hardcoded from multpl.com)
html/                  rendered Plotly dashboards (cache)
docs/notes.md          running notes + Sornette reference list
old_predictions/mnorayr.github.io/
                       prior work, last updated 2025-04-08 (one year before this
                       study); contains Bokeh S&P 1931-2025 prediction chart and
                       SPY options chain snapshots from 2025-04-07
```

## Run

```bash
/opt/homebrew/bin/python3 src/full_history.py
/opt/homebrew/bin/python3 src/minima_line.py
/opt/homebrew/bin/python3 src/loglog.py
# open html/*.html
```

Deps: `xlrd<2.0`, `numpy`, `pwlf`, `ruptures`, `plotly`.

## Non-advice

This is a math-first study of a price series. It is not investment advice.
The fact that the current regime is super-exponential implies it ends —
the LPPL literature estimates `tc` (critical time) from data but the
prediction error is notoriously wide.

## Humble disclaimer

Amateur engineering project. We are not HPC or quant finance professionals
and make no competitive claims. Numbers speak, ego doesn't.

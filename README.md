# finance_sp500 — super-exponential equity regime study

### Three ways in (hosted on GitHub Pages)

| 📈 [Golden log-log &amp; fit](https://norayr-m.github.io/finance_sp500/html/sp500_loglog.html) | 🎙 [George + Emma interview](https://norayr-m.github.io/finance_sp500/html/interview.html) | 📚 [Emma technical dive](https://norayr-m.github.io/finance_sp500/html/technical_dive.html) |
| :---: | :---: | :---: |
| interactive ln(ln(P)) plot · post-2010 regime is 12× more linear than the full 155-year series | 2m 46s podcast · transcript auto-highlights speaker · chart panel swaps as they speak | 13 slides · Emma narrated · Sornette LPPLS literature with inline citations · charts embedded in 4 slides |

Landing: **[norayr-m.github.io/finance_sp500](https://norayr-m.github.io/finance_sp500/)**

---

Personal notebook.

## The story

In April 2025 I sketched this analysis in a clumsy first-pass Bokeh notebook
and pushed it to GitHub ([mnorayr.github.io](https://mnorayr.github.io)).
The notebook predicted the S&P 500 would reach 7000 in spring/summer 2026.

One year later — **April 17, 2026** — the index closed at **7041.28**.
Call landed inside the season window.

That's when I decided to make the full analysis public. This repo is the
cleaned-up version: Shiller dataset back to 1871, piecewise log-linear fits,
the two-minima trendline I drew by hand, and the ln(ln(price)) test that
isolates the super-exponential regime. The math turns out to match Didier
Sornette's **Log-Periodic Power Law Singularity (LPPLS)** framework, which has
been publishing exactly this thesis since 1996 — I just didn't know it.

## What this is

Eyeball-first analysis of the S&P 500 from 1871 to today, testing whether the
post-2010 leg is a normal exponential bull regime or something stronger —
**super-exponential**, i.e. ln(ln(price)) linear in time.

Rediscovered from scratch; later confirmed by Sornette's LPPL framework.

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
src/full_history.py          1871-2026 full series + N-segment PWLF + projection
src/minima_line.py           line through two modern local minima + 6-seg PWLF + recent dashed
src/loglog.py                ln(ln(price)) transform — test for super-exponential
build_slides.py              10-slide interactive deck with Emma narration (bf_emma MP3 per slide)
build_interview.py           George + Emma interview (~3 min) with dynamic chart switching
data/shiller.xls             Robert Shiller monthly composite, 1871-2023
                             (recent 2023-10 → 2026-04 hardcoded from multpl.com)
html/slides.html             interactive deck, 10 slides, keyboard nav
html/interview.html          podcast-style interview + synced transcript + auto-switching charts
html/interview.mp3           concatenated 2-voice narration (~2m 46s)
html/audio/slide_NN.mp3      per-slide Emma narrations
html/sp500_*.html            the three Plotly charts (embedded in the deck + interview)
docs/notes.md                running notes + Sornette LPPLS reference list
```

## Next milestone — port to Bokeh + datashader

Current charts are Plotly; prior work (2025 repo) used Bokeh. Bokeh +
datashader renders datasets 1000× larger than Plotly at comparable fidelity,
and the 2025 prediction notebook already has the Bokeh pipeline. Re-platform
once stable.

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

This is an amateur engineering project. We are not HPC or quant finance
professionals and make no competitive claims. The timing of the 7000 call
was a single correct prediction; one sample is not a track record. Errors
are likely. Numbers speak, ego doesn't.

**Nothing in this repository is investment advice.** No recommendation to buy,
sell, or hold any security. Past fits do not predict future outcomes. The
LPPL literature's own authors publish wide confidence intervals on critical
time estimates (±6 to 18 months). Do your own math.

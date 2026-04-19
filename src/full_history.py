#!/usr/bin/env python3
"""S&P 500 1871 → 2026 from Shiller xls → single interactive Plotly chart.

Clean version. No PWLF regime fits, no post-2010 forward projection, no
ln(ln P) or minima-line constructs. One honest long-run OLS log-linear fit
over the full 155 years, the monthly price series, major historical events,
and the 2026-04-17 close. That is the entire chart.

Retraction note: earlier versions claimed a super-exponential regime
post-2010 and projected it forward. Adversarial review (April 2026) showed
that construct was look-ahead biased in the sense of Brée & Joseph (2013).
The projection and the ln-ln test and the two-minima line have been
retracted and archived under `archive/2026-04-19_lppls_theory_retracted/`.
"""
import math
import pathlib
from datetime import datetime

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import xlrd

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "shiller.xls"
OUT = ROOT / "html" / "sp500_shiller_1871_2026.html"

book = xlrd.open_workbook(str(DATA))
sh = book.sheet_by_name("Data")

dates, prices = [], []
for r in range(8, sh.nrows):
    v_date = sh.cell_value(r, 0)
    v_p = sh.cell_value(r, 1)
    if not isinstance(v_date, (int, float)) or not isinstance(v_p, (int, float)):
        continue
    if v_p <= 0:
        continue
    year = int(v_date)
    month = int(round((v_date - year) * 100))
    if month < 1:
        month = 1
    if month > 12:
        month = 12
    try:
        dt = datetime(year, month, 1)
    except ValueError:
        continue
    dates.append(dt)
    prices.append(float(v_p))

print(f"loaded {len(dates)} months, range {dates[0]:%Y-%m} → {dates[-1]:%Y-%m}")
print(f"price range {min(prices):.2f} → {max(prices):.2f}")

y0 = dates[0].year
xs = np.array([(d.year + (d.month - 1) / 12) - y0 for d in dates])
log_p = np.log10(np.array(prices))

# --- ONE honest long-run OLS fit over the whole series ---
slope, intercept = np.polyfit(xs, log_p, 1)
fit_log = intercept + slope * xs
fit = 10 ** fit_log
long_run_cagr = (10 ** slope - 1) * 100
gap_today = (prices[-1] / fit[-1] - 1) * 100
print(f"long-run OLS log-linear {dates[0].year}-{dates[-1].year}: {long_run_cagr:.2f}%/yr")
print(f"today vs long-run trend: {gap_today:+.1f}%")

fig = go.Figure()

# Long-run OLS line first so the price trace overlays it
fig.add_trace(go.Scatter(
    x=dates, y=fit, mode="lines",
    name=f"long-run OLS log-linear · {long_run_cagr:.2f}%/yr",
    line=dict(color="#86efac", width=2, dash="dot"),
    hovertemplate="<b>%{x|%b %Y}</b><br>long-run trend: %{y:.2f}<extra></extra>",
))

# The series
fig.add_trace(go.Scatter(
    x=dates, y=prices, mode="lines",
    name="S&P 500 (Shiller monthly)",
    line=dict(color="#ffd76a", width=3),
    hovertemplate="<b>%{x|%b %Y}</b><br>S&P: %{y:.2f}<extra></extra>",
))

# 2026-04-17 actual close
fig.add_trace(go.Scatter(
    x=[datetime(2026, 4, 17)], y=[7041.28], mode="markers+text",
    name="2026-04-17 close",
    marker=dict(color="#4ade80", size=14, symbol="circle",
                line=dict(color="#86efac", width=2)),
    text=[" 7041 · Apr 2026"],
    textposition="top right",
    textfont=dict(color="#86efac", size=12, family="-apple-system"),
    hovertemplate="<b>actual close</b><br>2026-04-17<br>S&P: 7041.28<extra></extra>",
    showlegend=False,
))

# Major historical events
def closest_idx(target_dt):
    return min(range(len(dates)), key=lambda i: abs((dates[i] - target_dt).days))

events = [
    (datetime(1929, 9, 1), "1929 peak", "top center"),
    (datetime(1932, 6, 1), "Depression low", "bottom center"),
    (datetime(1973, 12, 1), "1973-74 bear", "top left"),
    (datetime(1987, 10, 1), "Black Monday", "bottom right"),
    (datetime(2000, 3, 1), "Dot-com peak", "top right"),
    (datetime(2009, 3, 1), "GFC bottom", "bottom left"),
    (datetime(2020, 3, 1), "COVID crash", "top center"),
]
ev_x, ev_y, ev_t, ev_pos = [], [], [], []
for dt, label, pos in events:
    i = closest_idx(dt)
    ev_x.append(dates[i])
    ev_y.append(prices[i])
    ev_t.append(label)
    ev_pos.append(pos)

fig.add_trace(go.Scatter(
    x=ev_x, y=ev_y, mode="markers+text",
    name="events",
    marker=dict(color="#ff7a1a", size=10, symbol="diamond",
                line=dict(color="#ffd76a", width=1.5)),
    text=ev_t,
    textposition=ev_pos,
    textfont=dict(color="#ffd76a", size=11, family="-apple-system"),
    hovertemplate="<b>%{text}</b><br>%{x|%b %Y}<br>S&P: %{y:.2f}<extra></extra>",
    showlegend=False,
))

fig.add_annotation(
    xref="paper", yref="paper",
    x=0.02, y=0.98, xanchor="left", yanchor="top",
    text=(f"<b>Long-run OLS log-linear fit</b><br>"
          f"{dates[0].year}–{dates[-1].year}: <b>{long_run_cagr:.2f}%/yr</b><br>"
          f"today vs trend: {gap_today:+.1f}%"),
    showarrow=False, align="left",
    bgcolor="rgba(20,14,6,0.92)", bordercolor="#86efac", borderwidth=1,
    font=dict(color="#86efac", size=11, family="-apple-system"),
)

fig.update_layout(
    title=dict(
        text="<b>S&amp;P 500 · 1871 → 2026</b><br>"
             "<span style='font-size:13px;color:#a18050'>"
             "monthly composite · Shiller dataset · log scale</span>",
        font=dict(color="#ffb94a", size=22, family="-apple-system, SF Pro Display"),
        x=0.02, xanchor="left",
    ),
    paper_bgcolor="#0d0a05",
    plot_bgcolor="#000000",
    yaxis=dict(
        type="log",
        title=dict(text="S&P 500 (log)", font=dict(color="#ffb94a")),
        gridcolor="#332a18", zerolinecolor="#332a18",
        tickfont=dict(color="#a18050"),
    ),
    xaxis=dict(
        title=dict(text="", font=dict(color="#ffb94a")),
        gridcolor="#332a18", zerolinecolor="#332a18",
        tickfont=dict(color="#a18050"),
        rangeslider=dict(visible=True, bgcolor="#1a1208", thickness=0.06),
    ),
    hoverlabel=dict(bgcolor="#1a1208", font=dict(color="#ffd76a", family="SF Mono, Menlo")),
    margin=dict(l=70, r=40, t=110, b=80),
    showlegend=True,
    legend=dict(bgcolor="rgba(20,14,6,0.85)", bordercolor="#332a18", borderwidth=1,
                font=dict(color="#ffd76a", size=11, family="-apple-system"),
                x=0.98, xanchor="right", y=0.02, yanchor="bottom"),
)

fig.add_annotation(
    text="source: Robert Shiller online data (Yale economics) · dormant since 2026-04-19",
    xref="paper", yref="paper",
    x=1.0, y=-0.22, xanchor="right", yanchor="top",
    showarrow=False,
    font=dict(color="#5a4a28", size=11),
)

pio.write_html(fig, file=str(OUT), include_plotlyjs="cdn", full_html=True,
               config={"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})
print(f"wrote {OUT}  ({len(dates)} monthly points)")

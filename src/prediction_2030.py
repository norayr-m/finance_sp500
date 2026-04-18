#!/usr/bin/env python3
"""S&P 500 · 2010 → 2030 · actual + red-dashed log-linear projection on LINEAR y-axis.

This takes the post-2010 log-linear fit (the same slope used in the red-dashed
line on sp500_minima_line.html) and projects it forward to December 2030,
plotted on a normal (non-log) y-axis for easy-to-read price targets.
"""
import xlrd, math, pathlib
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.io as pio

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "shiller.xls"
OUT  = ROOT / "html" / "prediction_2030.html"

# ── load Shiller monthly (to Sept 2023) ──
book = xlrd.open_workbook(str(DATA))
sh = book.sheet_by_name("Data")
dates, prices = [], []
for r in range(8, sh.nrows):
    vd, vp = sh.cell_value(r, 0), sh.cell_value(r, 1)
    if not isinstance(vd, (int, float)) or not isinstance(vp, (int, float)) or vp <= 0:
        continue
    y = int(vd); m = max(1, min(12, int(round((vd - y) * 100))))
    dates.append(datetime(y, m, 1)); prices.append(float(vp))

# ── append recent monthly closes (multpl.com) + daily close 2026-04-17 ──
recent = [
    (2023,10,4258.98),(2023,11,4460.06),(2023,12,4685.05),
    (2024,1,4804.49),(2024,2,5011.96),(2024,3,5170.57),(2024,4,5095.46),
    (2024,5,5235.23),(2024,6,5415.14),(2024,7,5542.89),(2024,8,5502.17),
    (2024,9,5626.12),(2024,10,5792.32),(2024,11,5929.92),(2024,12,6010.91),
    (2025,1,5979.52),(2025,2,6038.69),(2025,3,5683.98),(2025,4,5369.50),
    (2025,5,5810.92),(2025,6,6029.95),(2025,7,6296.50),(2025,8,6408.95),
    (2025,9,6584.02),(2025,10,6735.69),(2025,11,6740.89),(2025,12,6853.03),
    (2026,1,6929.12),(2026,2,6893.81),(2026,3,6654.42),(2026,4,7041.28),
]
for y, m, p in recent:
    dates.append(datetime(y, m, 1)); prices.append(p)

# ── post-2010 log-linear fit (red line) ──
mask = [i for i, d in enumerate(dates) if d.year >= 2010]
d_recent = [dates[i] for i in mask]
p_recent = [prices[i] for i in mask]
xs = np.array([d.year + (d.month - 1) / 12 for d in d_recent])
ys = np.log(np.array(p_recent))
slope, intercept = np.polyfit(xs, ys, 1)
cagr = (math.exp(slope) - 1) * 100
print(f"post-2010 log-linear slope: {slope:.5f} (CAGR {cagr:.2f}%/yr)")

# ── post-2020 log-linear fit (purple line) — AI/COVID era, steeper regime ──
mask20 = [i for i, d in enumerate(dates) if d.year >= 2020]
d_20 = [dates[i] for i in mask20]
p_20 = [prices[i] for i in mask20]
xs_20 = np.array([d.year + (d.month - 1) / 12 for d in d_20])
ys_20 = np.log(np.array(p_20))
slope_20, intercept_20 = np.polyfit(xs_20, ys_20, 1)
cagr_20 = (math.exp(slope_20) - 1) * 100
print(f"post-2020 log-linear slope: {slope_20:.5f} (CAGR {cagr_20:.2f}%/yr)")

# ── project forward from last actual point (Apr 2026) to Dec 2030 ──
last_dt = dates[-1]
last_x = last_dt.year + (last_dt.month - 1) / 12
end_x = 2030 + 11/12  # Dec 2030
future_x = np.arange(last_x, end_x + 1/12, 1/12)
future_y = np.exp(intercept + slope * future_x)
future_y_20 = np.exp(intercept_20 + slope_20 * future_x)
future_dates = []
y_, m_ = last_dt.year, last_dt.month
for _ in future_x:
    future_dates.append(datetime(y_, m_, 1))
    m_ += 1
    if m_ > 12: m_ = 1; y_ += 1

def at_year(yr):
    return float(np.exp(intercept + slope * yr))

def at_year_20(yr):
    return float(np.exp(intercept_20 + slope_20 * yr))

print()
print("  date         projected S&P")
for yr in (2026.33, 2027, 2028, 2029, 2030, 2030.92):
    print(f"  {yr:<10.2f}  {at_year(yr):>10,.0f}")

# ── plot ──
fig = go.Figure()

# Actual S&P (2010 onward)
fig.add_trace(go.Scatter(
    x=d_recent, y=p_recent, mode="lines",
    name="S&P 500 (actual)",
    line=dict(color="#ffd76a", width=2.6),
    hovertemplate="<b>%{x|%b %Y}</b><br>S&P: %{y:.2f}<extra></extra>",
))

# Solid red: the fit line evaluated OVER the historical actual data
fit_hist_y = np.exp(intercept + slope * xs)
fig.add_trace(go.Scatter(
    x=d_recent, y=fit_hist_y, mode="lines",
    name=f"fit · post-2010 log-linear · CAGR {cagr:.2f}%/yr",
    line=dict(color="#f87171", width=2.4),  # SOLID
    hovertemplate="<b>%{x|%b %Y}</b><br>fit: %{y:,.0f}<extra></extra>",
))

# Dashed red: the same fit extended forward into the projection window
fig.add_trace(go.Scatter(
    x=future_dates, y=future_y, mode="lines",
    name="projection · post-2010 fit extended",
    line=dict(color="#f87171", width=2.4, dash="dash"),
    hovertemplate="<b>%{x|%b %Y}</b><br>projected: %{y:,.0f}<extra></extra>",
))

# Solid purple: the post-2020 fit over historical (AI/COVID era)
fit_20_hist_y = np.exp(intercept_20 + slope_20 * xs_20)
fig.add_trace(go.Scatter(
    x=d_20, y=fit_20_hist_y, mode="lines",
    name=f"fit · post-2020 · CAGR {cagr_20:.2f}%/yr",
    line=dict(color="#c084fc", width=2.4),  # SOLID purple
    hovertemplate="<b>%{x|%b %Y}</b><br>fit (post-2020): %{y:,.0f}<extra></extra>",
))

# Dashed purple: post-2020 fit extended to 2030
fig.add_trace(go.Scatter(
    x=future_dates, y=future_y_20, mode="lines",
    name="projection · post-2020 fit extended",
    line=dict(color="#c084fc", width=2.4, dash="dash"),
    hovertemplate="<b>%{x|%b %Y}</b><br>projected (post-2020): %{y:,.0f}<extra></extra>",
))

# Mark key milestone: today + 2030
fig.add_trace(go.Scatter(
    x=[datetime(2026, 4, 17)], y=[7041.28], mode="markers+text",
    marker=dict(color="#4ade80", size=14, symbol="diamond", line=dict(color="#86efac", width=2)),
    text=[" Apr 2026 · 7041"], textposition="top right",
    textfont=dict(color="#86efac", size=12, family="-apple-system"),
    showlegend=False,
    hovertemplate="<b>actual</b><br>2026-04-17<br>S&P: 7041.28<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=[datetime(2030, 12, 1)], y=[at_year(2030.92)], mode="markers+text",
    marker=dict(color="#f87171", size=14, symbol="x", line=dict(color="#fca5a5", width=2)),
    text=[f"  Dec 2030 · {at_year(2030.92):,.0f}"], textposition="top left",
    textfont=dict(color="#fca5a5", size=12, family="-apple-system"),
    showlegend=False,
))

# Round-number reference lines: 7000, 10000, 15000
for target in (7000, 8000, 9000, 10000, 12000, 15000):
    fig.add_hline(y=target, line=dict(color="#8a7228", width=0.8, dash="dot"), opacity=0.3)

# Stats badge
fig.add_annotation(
    xref="paper", yref="paper",
    x=0.02, y=0.98, xanchor="left", yanchor="top",
    text=(f"<b>Two log-linear fits</b><br>"
          f"<span style='color:#fca5a5'>post-2010: CAGR <b>{cagr:.2f}%/yr</b></span><br>"
          f"<span style='color:#d8b4fe'>post-2020: CAGR <b>{cagr_20:.2f}%/yr</b></span> "
          f"<span style='color:#a18050'>(AI/COVID era)</span><br>"
          f"<br>"
          f"2026-04 actual: <b>7,041</b><br>"
          f"<br><b>2030 end projections</b><br>"
          f"<span style='color:#fca5a5'>post-2010 line: <b>{at_year(2030.92):,.0f}</b></span><br>"
          f"<span style='color:#d8b4fe'>post-2020 line: <b>{at_year_20(2030.92):,.0f}</b></span>"),
    showarrow=False, align="left",
    bgcolor="rgba(20,14,6,0.92)", bordercolor="#c084fc", borderwidth=1,
    font=dict(color="#e8e2cf", size=12, family="-apple-system"),
)

fig.update_layout(
    title=dict(
        text="<b>S&amp;P 500 · 2010 → 2030</b><br>"
             "<span style='font-size:13px;color:#a18050'>"
             "actual + red-dashed post-2010 log-linear projection · linear y-axis</span>",
        font=dict(color="#ffb94a", size=22, family="-apple-system, SF Pro Display"),
        x=0.02, xanchor="left",
    ),
    paper_bgcolor="#0d0a05",
    plot_bgcolor="#000000",
    yaxis=dict(
        type="linear",
        range=[1000, max(at_year(2030.92), at_year_20(2030.92)) * 1.08],
        title=dict(text="S&P 500 (price)", font=dict(color="#ffb94a")),
        gridcolor="#332a18", zerolinecolor="#332a18",
        tickfont=dict(color="#a18050"),
        tickformat=",d",
    ),
    xaxis=dict(
        gridcolor="#332a18", zerolinecolor="#332a18",
        tickfont=dict(color="#a18050"),
        range=[datetime(2010, 1, 1), datetime(2031, 1, 1)],
    ),
    hoverlabel=dict(bgcolor="#1a1208", font=dict(color="#ffd76a", family="SF Mono, Menlo")),
    margin=dict(l=70, r=40, t=110, b=80),
    showlegend=True,
    legend=dict(bgcolor="rgba(20,14,6,0.7)", font=dict(color="#a18050", size=11)),
)

fig.add_annotation(
    text="⬡⟐ HARI · Shiller + multpl + post-2010 log-linear projection · not advice",
    xref="paper", yref="paper",
    x=1.0, y=-0.10, xanchor="right", yanchor="top",
    showarrow=False,
    font=dict(color="#5a4a28", size=11),
)

pio.write_html(fig, file=str(OUT), include_plotlyjs="cdn", full_html=True,
               config={"displaylogo": False})
print(f"\nWROTE {OUT}")

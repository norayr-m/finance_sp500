#!/usr/bin/env python3
"""S&P 500 log-log view. Y-axis = log10(log10(price)).
If growth is exp-of-exp (super-exponential), this transform is linear in time.
"""
import xlrd, math, numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.io as pio

book = xlrd.open_workbook("/Users/norayr/000_AI_Work/0_Projects/3_Active_Doing_finance_sp500/data/shiller.xls")
sh = book.sheet_by_name("Data")
dates, prices = [], []
for r in range(8, sh.nrows):
    vd, vp = sh.cell_value(r, 0), sh.cell_value(r, 1)
    if not isinstance(vd, (int, float)) or not isinstance(vp, (int, float)) or vp <= 0:
        continue
    y = int(vd); m = max(1, min(12, int(round((vd - y) * 100))))
    dates.append(datetime(y, m, 1)); prices.append(float(vp))

# Append real recent months through 2026-04
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

# Compute log10(log10(price))
log_p = np.log(np.array(prices))
loglog_p = np.log(log_p)   # safe since price >= 2.73, log10 >= 0.43 > 0

fig = go.Figure()

# log-log trace
fig.add_trace(go.Scatter(
    x=dates, y=loglog_p, mode="lines",
    name="ln(ln(S&P))",
    line=dict(color="#ffd76a", width=2.2),
    hovertemplate="<b>%{x|%b %Y}</b><br>log(log(P)): %{y:.4f}<br>"
                  "raw P: %{customdata:.2f}<extra></extra>",
    customdata=prices,
))

# Straight-line fit on the whole series — if super-exp, this is good
xs = np.array([d.year + (d.month-1)/12 for d in dates])
slope, intercept = np.polyfit(xs, loglog_p, 1)
line = intercept + slope * xs
fig.add_trace(go.Scatter(
    x=dates, y=line, mode="lines",
    name="full-series linear fit",
    line=dict(color="#f87171", width=1.6, dash="dash"),
    hovertemplate="<b>%{x|%b %Y}</b><br>fit: %{y:.4f}<extra></extra>",
))

# Linear fit on only post-2010 data (to see if recent regime is truly linear here)
mask_recent = np.array([d.year >= 2010 for d in dates])
xr = xs[mask_recent]; yr = loglog_p[mask_recent]
rslope, rintercept = np.polyfit(xr, yr, 1)
r_line = rintercept + rslope * xs
# Only draw the extension over the recent range
draw_mask = np.array([d.year >= 2005 for d in dates])
fig.add_trace(go.Scatter(
    x=[d for d, m in zip(dates, draw_mask) if m],
    y=r_line[draw_mask],
    mode="lines",
    name="post-2010 linear fit",
    line=dict(color="#4ade80", width=2.0, dash="dot"),
    hovertemplate="<b>%{x|%b %Y}</b><br>fit: %{y:.4f}<extra></extra>",
))

# Residual between raw loglog and recent linear fit tells us if post-2010 is
# genuinely straight on this axis (super-exp) or still curving (exp-of-exp-of-exp).
recent_resid = yr - (rintercept + rslope * xr)
r_rmse = float(np.sqrt(np.mean(recent_resid**2)))
full_resid = loglog_p - line
f_rmse = float(np.sqrt(np.mean(full_resid**2)))
print(f"full-series   RMSE on log(log(P)) = {f_rmse:.5f}")
print(f"post-2010     RMSE on log(log(P)) = {r_rmse:.5f}")
print(f"ratio = {r_rmse / f_rmse:.3f}  (lower → post-2010 is MORE linear on log-log)")

fig.add_annotation(
    xref="paper", yref="paper",
    x=0.02, y=0.98, xanchor="left", yanchor="top",
    text=(f"<b>ln(ln(S&amp;P))</b> vs time<br>"
          f"if linear here ⟹ super-exponential (exp-of-exp) growth<br><br>"
          f"full-series RMSE  <b>{f_rmse:.4f}</b><br>"
          f"post-2010 RMSE   <b>{r_rmse:.4f}</b><br>"
          f"post-2010 is <b>{f_rmse/r_rmse:.1f}×</b> more linear than the long series"),
    showarrow=False, align="left",
    bgcolor="rgba(20,14,6,0.92)", bordercolor="#86efac", borderwidth=1,
    font=dict(color="#86efac", size=12, family="-apple-system"),
)

fig.update_layout(
    title=dict(
        text="<b>S&amp;P 500 · log-log transform · 1871 → 2026</b><br>"
             "<span style='font-size:13px;color:#a18050'>"
             "y = ln(ln(price)) · linear here ⟹ super-exponential</span>",
        font=dict(color="#ffb94a", size=22, family="-apple-system, SF Pro Display"),
        x=0.02, xanchor="left",
    ),
    paper_bgcolor="#0d0a05",
    plot_bgcolor="#000000",
    yaxis=dict(
        title=dict(text="ln(ln(price))", font=dict(color="#ffb94a")),
        gridcolor="#332a18", zerolinecolor="#332a18",
        tickfont=dict(color="#a18050"),
    ),
    xaxis=dict(
        gridcolor="#332a18", zerolinecolor="#332a18",
        tickfont=dict(color="#a18050"),
    ),
    hoverlabel=dict(bgcolor="#1a1208", font=dict(color="#ffd76a", family="SF Mono, Menlo")),
    margin=dict(l=70, r=40, t=110, b=80),
    showlegend=True,
    legend=dict(bgcolor="rgba(20,14,6,0.7)", font=dict(color="#a18050", size=11)),
)

fig.add_annotation(
    text="⬡⟐ HARI · log-log super-exp test · Shiller + multpl",
    xref="paper", yref="paper",
    x=1.0, y=-0.10, xanchor="right", yanchor="top",
    showarrow=False,
    font=dict(color="#5a4a28", size=11),
)

out = "/Users/norayr/000_AI_Work/0_Projects/3_Active_Doing_finance_sp500/html/sp500_loglog.html"
pio.write_html(fig, file=out, include_plotlyjs="cdn", full_html=True,
               config={"displaylogo": False})
print(f"WROTE {out}")

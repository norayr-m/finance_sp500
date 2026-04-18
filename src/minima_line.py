#!/usr/bin/env python3
"""S&P 500 2005-2035, single line through two local minima: 8/2011 and 3/2025."""
import xlrd, math, numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.io as pio
import pwlf

book = xlrd.open_workbook("/Users/norayr/000_AI_Work/0_Projects/3_Active_Doing_finance_sp500/data/shiller.xls")
sh = book.sheet_by_name("Data")
dates, prices = [], []
for r in range(8, sh.nrows):
    vd, vp = sh.cell_value(r, 0), sh.cell_value(r, 1)
    if not isinstance(vd, (int, float)) or not isinstance(vp, (int, float)) or vp <= 0:
        continue
    y = int(vd); m = max(1, min(12, int(round((vd - y) * 100))))
    dates.append(datetime(y, m, 1)); prices.append(float(vp))

# Full Shiller series, 1871 onward (no trim)

# --- two anchor minima -----------------------------------------------------
# 8/2011 ≈ debt-ceiling sell-off low; closest Shiller monthly value
# 3/2025 ≈ early-2025 pullback low (beyond Shiller; user-supplied memory)
ANCHOR_1 = (datetime(2011, 8, 1), None)   # value: pull from data
ANCHOR_2 = (datetime(2025, 3, 1), 5683.98)   # real monthly close from multpl.com

def closest(dt):
    return min(range(len(dates)), key=lambda i: abs((dates[i] - dt).days))

i1 = closest(ANCHOR_1[0])
p1 = prices[i1]
d1 = dates[i1]
d2, p2 = ANCHOR_2
print(f"anchor 1: {d1:%Y-%m}  P = {p1:.2f}")
print(f"anchor 2: {d2:%Y-%m}  P = {p2:.2f}  (user-supplied)")

# Linear time axis in years since 1871
def xyrs(dt): return dt.year + (dt.month - 1) / 12 - 1871
x1, x2 = xyrs(d1), xyrs(d2)
# Log-space straight line through the two points
log_p1, log_p2 = math.log10(p1), math.log10(p2)
slope = (log_p2 - log_p1) / (x2 - x1)
intercept = log_p1 - slope * x1
cagr = (10**slope - 1) * 100
print(f"line: log10(P) = {slope:.5f}*(year - 1871) + {intercept:.4f}  ⟹  CAGR {cagr:.2f}%/yr")

# Range 1871 → 2035
line_x = np.arange(0, 165, 1/12)
line_y = 10 ** (intercept + slope * line_x)
line_dates = []
y, m = 1871, 1
for _ in line_x:
    line_dates.append(datetime(y, m, 1))
    m += 1
    if m > 12: m = 1; y += 1

# Where line hits today (2026-04) and 2030, 2035
def at_year(yr):
    return 10 ** (intercept + slope * (yr - 1871))
projections = [(2026.33, "2026 Apr"), (2030, "2030"), (2035, "2035")]
print()
for yr, label in projections:
    print(f"  {label:<10} line ≈ {at_year(yr):,.0f}")

# ---- Plot ----------------------------------------------------------------
fig = go.Figure()

# S&P data (Shiller monthly composite, 1871-2023)
fig.add_trace(go.Scatter(
    x=dates, y=prices, mode="lines",
    name="S&P 500 (Shiller)", line=dict(color="#ffd76a", width=2.4),
    hovertemplate="<b>%{x|%b %Y}</b><br>S&P: %{y:.2f}<extra></extra>",
))

# ---- 6-segment continuous piecewise log-linear fit (PWLF) ----
full_xs = np.array([xyrs(d) for d in dates])
full_ys = np.array([math.log10(p) for p in prices])
plf = pwlf.PiecewiseLinFit(full_xs, full_ys)
bk = plf.fit(6)
pwlf_y_log = plf.predict(full_xs)
pwlf_y = 10 ** pwlf_y_log

fig.add_trace(go.Scatter(
    x=dates, y=pwlf_y, mode="lines",
    name="6-segment PWLF", line=dict(color="#86efac", width=2.0),
    hovertemplate="<b>%{x|%b %Y}</b><br>PWLF: %{y:.2f}<extra></extra>",
))

# print PWLF segment CAGRs
print("\n6-segment PWLF:")
for k in range(6):
    i0 = int(np.argmin(np.abs(full_xs - bk[k])))
    i1 = int(np.argmin(np.abs(full_xs - bk[k+1])))
    sl = (pwlf_y_log[i1] - pwlf_y_log[i0]) / (full_xs[i1] - full_xs[i0])
    c = (10**sl - 1) * 100
    print(f"  {dates[i0]:%Y-%m}  →  {dates[i1]:%Y-%m}   CAGR {c:+6.2f}%/yr")

# Recent real monthly closes from multpl.com (S&P 500 monthly history)
# plus the Apr 17 2026 daily close pulled from Yahoo via web search.
recent_monthly = [
    (datetime(2023, 10, 1), 4258.98),
    (datetime(2023, 11, 1), 4460.06),
    (datetime(2023, 12, 1), 4685.05),
    (datetime(2024,  1, 1), 4804.49),
    (datetime(2024,  2, 1), 5011.96),
    (datetime(2024,  3, 1), 5170.57),
    (datetime(2024,  4, 1), 5095.46),
    (datetime(2024,  5, 1), 5235.23),
    (datetime(2024,  6, 1), 5415.14),
    (datetime(2024,  7, 1), 5542.89),
    (datetime(2024,  8, 1), 5502.17),
    (datetime(2024,  9, 1), 5626.12),
    (datetime(2024, 10, 1), 5792.32),
    (datetime(2024, 11, 1), 5929.92),
    (datetime(2024, 12, 1), 6010.91),
    (datetime(2025,  1, 1), 5979.52),
    (datetime(2025,  2, 1), 6038.69),
    (datetime(2025,  3, 1), 5683.98),
    (datetime(2025,  4, 1), 5369.50),
    (datetime(2025,  5, 1), 5810.92),
    (datetime(2025,  6, 1), 6029.95),
    (datetime(2025,  7, 1), 6296.50),
    (datetime(2025,  8, 1), 6408.95),
    (datetime(2025,  9, 1), 6584.02),
    (datetime(2025, 10, 1), 6735.69),
    (datetime(2025, 11, 1), 6740.89),
    (datetime(2025, 12, 1), 6853.03),
    (datetime(2026,  1, 1), 6929.12),
    (datetime(2026,  2, 1), 6893.81),
    (datetime(2026,  3, 1), 6654.42),
    (datetime(2026,  4, 17), 7041.28),
]
rx = [p[0] for p in recent_monthly]
ry = [p[1] for p in recent_monthly]
fig.add_trace(go.Scatter(
    x=rx, y=ry, mode="lines+markers",
    name="S&P 500 (recent, dashed)",
    line=dict(color="#ffd76a", width=2.0, dash="dash"),
    marker=dict(size=4, color="#ffd76a"),
    hovertemplate="<b>%{x|%b %Y}</b><br>S&P: %{y:.2f}<extra></extra>",
    showlegend=False,
))

# Trend line through the two minima (extended both directions)
fig.add_trace(go.Scatter(
    x=line_dates, y=line_y, mode="lines",
    name=f"line through 2 minima · CAGR {cagr:.2f}%/yr",
    line=dict(color="#f87171", width=2.0, dash="dash"),
    hovertemplate="<b>%{x|%b %Y}</b><br>line: %{y:.2f}<extra></extra>",
))

# Mark the two anchors
fig.add_trace(go.Scatter(
    x=[d1, d2], y=[p1, p2], mode="markers+text",
    name="anchors",
    marker=dict(color="#fca5a5", size=14, symbol="circle",
                line=dict(color="#f87171", width=2)),
    text=[f"  Aug 2011 · {p1:.0f}", f"  Mar 2025 · {p2:.0f}  (user)"],
    textposition="top right",
    textfont=dict(color="#fca5a5", size=12, family="-apple-system"),
    showlegend=False,
))

# Today's actual close (2026-04-17 = 7041)
fig.add_trace(go.Scatter(
    x=[datetime(2026, 4, 17)], y=[7041.28], mode="markers+text",
    name="actual",
    marker=dict(color="#4ade80", size=14, symbol="diamond",
                line=dict(color="#86efac", width=2)),
    text=["  Apr 2026 actual · 7041"],
    textposition="bottom right",
    textfont=dict(color="#86efac", size=12, family="-apple-system"),
    hovertemplate="<b>actual</b><br>2026-04-17<br>S&P: 7041.28<extra></extra>",
    showlegend=False,
))

# Stats badge
fig.add_annotation(
    xref="paper", yref="paper",
    x=0.02, y=0.98, xanchor="left", yanchor="top",
    text=(f"<b>Trendline through two local minima</b><br>"
          f"Aug 2011 ({p1:.0f})  →  Mar 2025 ({p2:.0f})<br>"
          f"<b>slope</b>  {cagr:.2f}%/yr (log-linear)<br>"
          f"line at 2030 ≈ <b>{at_year(2030):,.0f}</b><br>"
          f"line at 2035 ≈ <b>{at_year(2035):,.0f}</b>"),
    showarrow=False, align="left",
    bgcolor="rgba(20,14,6,0.92)", bordercolor="#fca5a5", borderwidth=1,
    font=dict(color="#fca5a5", size=12, family="-apple-system"),
)

fig.update_layout(
    title=dict(
        text="<b>S&amp;P 500 · 1871 → 2035</b><br>"
             "<span style='font-size:13px;color:#a18050'>"
             "line extended from 2 modern minima · back to 1871 · log scale</span>",
        font=dict(color="#ffb94a", size=22, family="-apple-system, SF Pro Display"),
        x=0.02, xanchor="left",
    ),
    paper_bgcolor="#0d0a05",
    plot_bgcolor="#000000",
    yaxis=dict(
        type="log", range=[0.3, 4.6],
        title=dict(text="S&P 500 (log)", font=dict(color="#ffb94a")),
        gridcolor="#332a18", zerolinecolor="#332a18",
        tickfont=dict(color="#a18050"),
        autorange=False,
    ),
    xaxis=dict(
        gridcolor="#332a18", zerolinecolor="#332a18",
        tickfont=dict(color="#a18050"),
        range=[datetime(1871, 1, 1), datetime(2036, 1, 1)],
    ),
    hoverlabel=dict(bgcolor="#1a1208", font=dict(color="#ffd76a", family="SF Mono, Menlo")),
    margin=dict(l=70, r=40, t=110, b=80),
    showlegend=False,
)

fig.add_annotation(
    text="⬡⟐ HARI · two-anchor trendline · Shiller + user marker",
    xref="paper", yref="paper",
    x=1.0, y=-0.10, xanchor="right", yanchor="top",
    showarrow=False,
    font=dict(color="#5a4a28", size=11),
)

out = "/Users/norayr/000_AI_Work/0_Projects/3_Active_Doing_finance_sp500/html/sp500_minima_line.html"
pio.write_html(fig, file=out, include_plotlyjs="cdn", full_html=True,
               config={"displaylogo": False})
print(f"\nWROTE {out}")

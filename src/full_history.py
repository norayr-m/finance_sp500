#!/usr/bin/env python3
"""S&P 500 1871→2026 from Shiller xls → interactive Plotly HTML."""
import xlrd
from datetime import datetime
import plotly.graph_objects as go
import plotly.io as pio

book = xlrd.open_workbook("/Users/norayr/000_AI_Work/0_Projects/3_Active_Doing_finance_sp500/data/shiller.xls")
sh = book.sheet_by_name("Data")

# Data starts at row 8 (0-indexed); col 0 = decimal date, col 1 = P (S&P comp).
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
    if month < 1: month = 1
    if month > 12: month = 12
    try:
        dt = datetime(year, month, 1)
    except ValueError:
        continue
    dates.append(dt)
    prices.append(float(v_p))

print(f"loaded {len(dates)} months, range {dates[0]} → {dates[-1]}")
print(f"price range {min(prices):.2f} → {max(prices):.2f}")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=dates, y=prices, mode="lines",
    name="S&P 500 (Shiller monthly composite)",
    line=dict(color="#ffd76a", width=3, shape="linear"),
    hovertemplate="<b>%{x|%b %Y}</b><br>S&P: %{y:.2f}<extra></extra>",
))

# ---- Piecewise-linear fit on log(price) vs years ----
# Use ruptures PELT to find data-driven changepoints, then fit OLS on each segment.
# Every segment = its own exponential regime (different CAGR).
import math
import numpy as np
import pwlf

y0 = dates[0].year
xs = np.array([(d.year + (d.month-1)/12) - y0 for d in dates])
ys = np.array([math.log10(p) for p in prices])

# Continuous piecewise-linear fit with adaptive knot positions.
# pwlf optimises both knot LOCATIONS and slope/intercept of every segment so the
# fit is continuous (no vertical connectors).
N_SEGMENTS = 5
plf = pwlf.PiecewiseLinFit(xs, ys)
breakpoint_xs = plf.fit(N_SEGMENTS)
fit_y_log = plf.predict(xs)
fit_y = 10 ** fit_y_log

def x_to_idx(x):
    return int(np.argmin(np.abs(xs - x)))

breakpoints = [x_to_idx(b) for b in breakpoint_xs]
print(f"continuous-PWLF segments: {N_SEGMENTS}")

seg_info = []
for k in range(N_SEGMENTS):
    s, e = breakpoints[k], breakpoints[k+1]
    if e <= s:
        continue
    # slope between knots in log space
    sl = (fit_y_log[e] - fit_y_log[s]) / (xs[e] - xs[s])
    cagr = (10**sl - 1) * 100
    seg_info.append((dates[s], dates[min(e, len(dates)-1)], cagr, e - s))

print(f"\n{'segment':<28} {'months':>7} {'CAGR':>10}")
for d0, d1, cagr, n in seg_info:
    print(f"{d0:%Y-%m}  →  {d1:%Y-%m}  {n:>7d} {cagr:>9.2f}%")

last_p, last_fit = prices[-1], float(fit_y[-1])
gap_pct = (last_p / last_fit - 1) * 100

# Plot the continuous piecewise fit
fig.add_trace(go.Scatter(
    x=dates, y=fit_y, mode="lines",
    name=f"continuous piecewise log-linear · {N_SEGMENTS} segments",
    line=dict(color="#86efac", width=2.0),
    hovertemplate="<b>%{x|%b %Y}</b><br>regime fit: %{y:.2f}<extra></extra>",
))

# Subtle knot markers
knot_dates = [dates[i] for i in breakpoints]
knot_prices = [10**fit_y_log[i] for i in breakpoints]
fig.add_trace(go.Scatter(
    x=knot_dates, y=knot_prices, mode="markers",
    name="knots", showlegend=False,
    marker=dict(color="#86efac", size=8, symbol="diamond-open",
                line=dict(color="#4ade80", width=1.5)),
    hovertemplate="<b>knot · %{x|%b %Y}</b><br>fit: %{y:.2f}<extra></extra>",
))

# ---- "You in Spring 2024" forward projection (red) ----
# Norayr fit a STRAIGHT LINE on Yahoo's LINEAR-Y chart from ~2010 to spring 2024.
# Linear-Y line = constant absolute increment per year (NOT constant %).
# Refit linear (not log-linear) on post-2010 data and extrapolate forward.
recent_mask = np.array([d.year >= 2010 for d in dates])
rx = xs[recent_mask]; ry_lin = np.array(prices)[recent_mask]
recent_slope_lin, recent_intercept_lin = np.polyfit(rx, ry_lin, 1)
print(f"recent-leg (2010+) LINEAR slope = {recent_slope_lin:.2f} pts/yr  intercept @ start = {recent_intercept_lin:.2f}")

cutoff_idx = len(dates) - 1
cutoff_date = dates[cutoff_idx]
cutoff_x = xs[cutoff_idx]

# Use linear slope for projection
last_slope_lin = recent_slope_lin

# Compatibility shims for the rest of the code
last_slope = math.log10(1 + (recent_slope_lin / prices[cutoff_idx]))   # equivalent local CAGR
projected_cagr = recent_slope_lin   # we'll relabel: it's pts/yr now
cutoff_log = math.log10(prices[cutoff_idx])

# Project monthly from cutoff out to 2045-12 — LINEAR + LOG variants
future_x = np.arange(cutoff_x, cutoff_x + 22.5, 1/12)
# Linear-style projection (Norayr's straight line on linear-Y)
future_y_linear = prices[cutoff_idx] + recent_slope_lin * (future_x - cutoff_x)
# Log-style projection (post-2010 OLS slope on log scale)
recent_log_slope, recent_log_intercept = np.polyfit(rx, np.log10(ry_lin), 1)
recent_log_cagr = (10**recent_log_slope - 1) * 100
print(f"recent-leg (2010+) LOG slope = {recent_log_cagr:.2f}%/yr")
future_y_log_proj = 10 ** (math.log10(prices[cutoff_idx]) + recent_log_slope * (future_x - cutoff_x))
# Use LOG projection (visually straight on log y axis)
future_y = future_y_log_proj
future_dates = [datetime(int(cutoff_date.year + (cx - cutoff_x) // 1),
                         ((cutoff_date.month - 1 + int(round((cx - cutoff_x) * 12))) % 12) + 1, 1)
                for cx in future_x]
# Simpler: just add monthly timedelta steps
future_dates = []
d = cutoff_date
for _ in range(len(future_x)):
    future_dates.append(d)
    # advance by ~30.44 days (1 month average)
    next_month = d.month + 1
    next_year = d.year
    if next_month > 12:
        next_month = 1; next_year += 1
    d = datetime(next_year, next_month, 1)

fig.add_trace(go.Scatter(
    x=future_dates, y=future_y, mode="lines",
    name=f"forward projection (last regime CAGR)",
    line=dict(color="#f87171", width=2.4, dash="dash"),
    hovertemplate="<b>%{x|%b %Y}</b><br>projected: %{y:.2f}<extra></extra>",
))

# Where does the projection cross 7000?
cross_idx = next((i for i,p in enumerate(future_y) if p >= 7041.28), None)
projected_cagr = (10**last_slope - 1) * 100
if cross_idx is not None:
    cross_date = future_dates[cross_idx]
    fig.add_trace(go.Scatter(
        x=[cross_date], y=[future_y[cross_idx]], mode="markers+text",
        name="prediction hit",
        marker=dict(color="#f87171", size=14, symbol="x",
                    line=dict(color="#fca5a5", width=2)),
        text=[f" 7041 reached: {cross_date:%b %Y}"],
        textposition="top right",
        textfont=dict(color="#fca5a5", size=12, family="-apple-system"),
        hovertemplate="<b>projection hits 7000+</b><br>%{x|%b %Y}<extra></extra>",
        showlegend=False,
    ))
    print(f"projection crosses 7041 at {cross_date:%b %Y}")
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.98, y=0.50, xanchor="right", yanchor="top",
        text=(f"<b>Norayr's 2024 line</b><br>"
              f"straight line on linear-Y, post-2010 leg<br>"
              f"slope <b>{recent_slope_lin:+.1f} pts/yr</b><br>"
              f"reaches 7041 in <b>{cross_date:%b %Y}</b><br>"
              f"actual hit: <b>2026-04 · 7041.28</b>"),
        showarrow=False, align="left",
        bgcolor="rgba(26,12,12,0.92)", bordercolor="#f87171", borderwidth=1,
        font=dict(color="#fca5a5", size=12, family="-apple-system"),
    )

# Mark the actual 2026-04-17 close on the chart for visual reality-check
fig.add_trace(go.Scatter(
    x=[datetime(2026, 4, 17)], y=[7041.28], mode="markers+text",
    name="actual 2026-04-17",
    marker=dict(color="#4ade80", size=14, symbol="circle",
                line=dict(color="#86efac", width=2)),
    text=[" actual: 7041 · Apr 2026"],
    textposition="bottom right",
    textfont=dict(color="#86efac", size=12, family="-apple-system"),
    hovertemplate="<b>actual close</b><br>2026-04-17<br>S&P: 7041.28<extra></extra>",
    showlegend=False,
))

# Stats badge — list each regime's CAGR
def fmt_seg(d0, d1, cagr):
    return f"{d0:%Y}–{d1:%Y}  <b>{cagr:+.2f}%/yr</b>"

regime_lines = "<br>".join(fmt_seg(d0,d1,c) for d0,d1,c,_ in seg_info)
fig.add_annotation(
    xref="paper", yref="paper",
    x=0.02, y=0.98, xanchor="left", yanchor="top",
    text=(f"<b>Continuous piecewise log-linear · {len(seg_info)} regimes (PWLF)</b><br>{regime_lines}<br>"
          f"<b>Today vs current-regime trend</b>  {gap_pct:+.1f}%"),
    showarrow=False, align="left",
    bgcolor="rgba(20,14,6,0.92)", bordercolor="#86efac", borderwidth=1,
    font=dict(color="#86efac", size=11, family="-apple-system"),
)

# Today's level reference
fig.add_hline(y=7041.28, line=dict(color="#4ade80", width=1, dash="dot"),
              annotation_text="2026-04-17 · 7041",
              annotation_position="top right",
              annotation_font_color="#86efac")

# Inflection annotations
def closest_idx(target_dt):
    return min(range(len(dates)), key=lambda i: abs((dates[i] - target_dt).days))

events = [
    (datetime(1929, 9, 1), "1929 peak"),
    (datetime(1932, 6, 1), "Great Depression low"),
    (datetime(1973, 12, 1), "1973-74 bear"),
    (datetime(1987, 10, 1), "Black Monday"),
    (datetime(2000, 3, 1), "Dot-com peak"),
    (datetime(2009, 3, 1), "GFC bottom"),
    (datetime(2020, 3, 1), "COVID crash"),
    (datetime(2026, 4, 1), "today: 7041"),
]
# Add events as a second scatter trace with text labels (renders reliably with log axis + fixed range)
ev_x, ev_y, ev_t = [], [], []
positions = ["top center", "bottom center", "top left", "bottom right",
             "top right", "bottom left", "top center", "bottom center"]
ev_pos = []
for (dt, label), pos in zip(events, positions):
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
    textfont=dict(color="#ffd76a", size=12, family="-apple-system"),
    hovertemplate="<b>%{text}</b><br>%{x|%b %Y}<br>S&P: %{y:.2f}<extra></extra>",
    showlegend=False,
))

fig.update_layout(
    title=dict(
        text="<b>S&amp;P 500 · 1871 → 2026</b><br>"
             "<span style='font-size:13px;color:#a18050'>"
             "monthly composite · Shiller dataset · log scale · drag to zoom · use slider</span>",
        font=dict(color="#ffb94a", size=22, family="-apple-system, SF Pro Display"),
        x=0.02, xanchor="left",
    ),
    paper_bgcolor="#0d0a05",
    plot_bgcolor="#000000",
    yaxis=dict(
        type="log",
        range=[3.0, 5.5],   # 1000 → ~316,000  (room for 2045 extrapolation)
        title=dict(text="S&P 500 (log)", font=dict(color="#ffb94a")),
        gridcolor="#332a18", zerolinecolor="#332a18",
        tickfont=dict(color="#a18050"),
        autorange=False,
    ),
    xaxis=dict(
        title=dict(text="", font=dict(color="#ffb94a")),
        gridcolor="#332a18", zerolinecolor="#332a18",
        tickfont=dict(color="#a18050"),
        range=[datetime(2009, 1, 1), datetime(2046, 1, 1)],
        rangeslider=dict(visible=True, bgcolor="#1a1208", thickness=0.06),
    ),
    hoverlabel=dict(bgcolor="#1a1208", font=dict(color="#ffd76a", family="SF Mono, Menlo")),
    margin=dict(l=70, r=40, t=110, b=80),
    showlegend=False,
)

fig.add_annotation(
    text="⬡⟐ HARI · source: Robert Shiller online data (Yale economics)",
    xref="paper", yref="paper",
    x=1.0, y=-0.25, xanchor="right", yanchor="top",
    showarrow=False,
    font=dict(color="#5a4a28", size=11),
)

out = "/Users/norayr/000_AI_Work/0_Projects/3_Active_Doing_finance_sp500/html/sp500_shiller_1871_2026.html"
pio.write_html(fig, file=out, include_plotlyjs="cdn", full_html=True,
               config={"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})
print(f"WROTE {out}  ({len(dates)} monthly points)")

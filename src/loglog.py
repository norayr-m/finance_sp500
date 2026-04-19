#!/usr/bin/env python3
"""S&P 500 log-log view. Y-axis = ln(ln(price)).

No interpretation in the annotations. The axes are labeled; the reader
decides what the shape means.
"""
import pathlib
from datetime import datetime

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import xlrd
from scipy.signal import find_peaks
from scipy.optimize import linprog

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "shiller.xls"
OUT = ROOT / "html" / "sp500_loglog.html"

book = xlrd.open_workbook(str(DATA))
sh = book.sheet_by_name("Data")
dates, prices = [], []
for r in range(8, sh.nrows):
    vd, vp = sh.cell_value(r, 0), sh.cell_value(r, 1)
    if not isinstance(vd, (int, float)) or not isinstance(vp, (int, float)) or vp <= 0:
        continue
    y = int(vd); m = max(1, min(12, int(round((vd - y) * 100))))
    dates.append(datetime(y, m, 1)); prices.append(float(vp))

# Append real recent months through 2026-04 (Shiller xls lags ~6 months).
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

log_p = np.log(np.array(prices))
loglog_p = np.log(log_p)

xs = np.array([d.year + (d.month-1)/12 for d in dates])
slope, intercept = np.polyfit(xs, loglog_p, 1)
line = intercept + slope * xs

mask_recent = np.array([d.year >= 2010 for d in dates])
xr = xs[mask_recent]; yr = loglog_p[mask_recent]
rslope, rintercept = np.polyfit(xr, yr, 1)
r_line = rintercept + rslope * xs
draw_mask = np.array([d.year >= 2005 for d in dates])
draw_dates = [d for d, m in zip(dates, draw_mask) if m]
r_line_draw = r_line[draw_mask]

# LIN-mode fits: OLS on ln(P) vs t, rendered as exp back to prices
slope_lin, intercept_lin = np.polyfit(xs, log_p, 1)
lin_fit_full = np.exp(intercept_lin + slope_lin * xs)
rslope_lin, rintercept_lin = np.polyfit(xs[mask_recent], log_p[mask_recent], 1)
lin_fit_recent = np.exp(rintercept_lin + rslope_lin * xs[draw_mask])

print(f"full-series slope on ln(ln P) vs time: {slope:.5f}/yr")
print(f"post-2010 slope on ln(ln P) vs time:   {rslope:.5f}/yr")
print(f"full-series CAGR (exp fit on ln P):    {(np.exp(slope_lin)-1)*100:.2f}%/yr")
print(f"post-2010 CAGR (exp fit on ln P):       {(np.exp(rslope_lin)-1)*100:.2f}%/yr")

fig = go.Figure()

# LOGLOG traces (visible by default)
fig.add_trace(go.Scatter(
    x=dates, y=loglog_p, mode="lines",
    name="ln(ln(S&P))",
    line=dict(color="#ffd76a", width=2.2),
    hovertemplate="<b>%{x|%b %Y}</b><br>ln(ln(P)): %{y:.4f}<br>"
                  "raw P: %{customdata:.2f}<extra></extra>",
    customdata=prices,
    visible=True,
))
fig.add_trace(go.Scatter(
    x=dates, y=line, mode="lines",
    name="full-series linear fit",
    line=dict(color="#f87171", width=1.6, dash="dash"),
    hovertemplate="<b>%{x|%b %Y}</b><br>fit: %{y:.4f}<extra></extra>",
    visible=True,
))
fig.add_trace(go.Scatter(
    x=draw_dates, y=r_line_draw, mode="lines",
    name="post-2010 linear fit",
    line=dict(color="#4ade80", width=2.0, dash="dot"),
    hovertemplate="<b>%{x|%b %Y}</b><br>fit: %{y:.4f}<extra></extra>",
    visible=True,
))

# LIN traces (hidden by default)
fig.add_trace(go.Scatter(
    x=dates, y=prices, mode="lines",
    name="S&P 500",
    line=dict(color="#ffd76a", width=2.2),
    hovertemplate="<b>%{x|%b %Y}</b><br>S&P: %{y:.2f}<extra></extra>",
    visible=False,
))
fig.add_trace(go.Scatter(
    x=dates, y=lin_fit_full, mode="lines",
    name="full-series exp fit",
    line=dict(color="#f87171", width=1.6, dash="dash"),
    hovertemplate="<b>%{x|%b %Y}</b><br>exp fit: %{y:.2f}<extra></extra>",
    visible=False,
))
fig.add_trace(go.Scatter(
    x=draw_dates, y=lin_fit_recent, mode="lines",
    name="post-2010 exp fit",
    line=dict(color="#4ade80", width=2.0, dash="dot"),
    hovertemplate="<b>%{x|%b %Y}</b><br>exp fit: %{y:.2f}<extra></extra>",
    visible=False,
))

# ----- Draggable eyeball line: two marker anchors + a line extending beyond them -----
ANC_1 = (datetime(2011, 9, 1), 1134.51)
ANC_2 = (datetime(2024, 11, 1), 6138.52)
anc1_y = float(np.log(np.log(ANC_1[1])))
anc2_y = float(np.log(np.log(ANC_2[1])))

# Line extends from far-left to far-right through both anchors
LINE_X_MIN = datetime(1871, 1, 1)
LINE_X_MAX = datetime(2045, 1, 1)

def _line_endpoints(a1d, a1y, a2d, a2y):
    t1 = a1d.year + (a1d.month - 1) / 12
    t2 = a2d.year + (a2d.month - 1) / 12
    slope = (a2y - a1y) / (t2 - t1)
    tmin = LINE_X_MIN.year + (LINE_X_MIN.month - 1) / 12
    tmax = LINE_X_MAX.year + (LINE_X_MAX.month - 1) / 12
    return (a1y + slope * (tmin - t1), a1y + slope * (tmax - t1))

y_left, y_right = _line_endpoints(ANC_1[0], anc1_y, ANC_2[0], anc2_y)

# extended line trace (drawn before markers so markers sit on top)
fig.add_trace(go.Scatter(
    x=[LINE_X_MIN, LINE_X_MAX], y=[y_left, y_right],
    mode="lines",
    name="eyeball mk1",
    line=dict(color="#86efac", width=2.6),
    hoverinfo="skip",
))
# marker trace (anchor positions only)
fig.add_trace(go.Scatter(
    x=[ANC_1[0], ANC_2[0]], y=[anc1_y, anc2_y],
    mode="markers",
    name="anchors",
    marker=dict(size=16, color="#4ade80",
                line=dict(color="#ffffff", width=2), symbol="circle"),
    hovertemplate="<b>anchor</b><br>%{x|%b %Y}<br>ln(ln P): %{y:.4f}<extra></extra>",
    showlegend=False,
))

# ----- Detect local extrema in ln(ln P) across full era -----
ERA_START_YEAR = 1935
era_mask_all = np.array([d.year >= ERA_START_YEAR for d in dates])

llp_np = np.array(loglog_p)
peaks_max, _ = find_peaks(llp_np, distance=6, prominence=0.003)
peaks_min, _ = find_peaks(-llp_np, distance=6, prominence=0.003)
peaks_max = [i for i in peaks_max if dates[i].year >= ERA_START_YEAR]
peaks_min = [i for i in peaks_min if dates[i].year >= ERA_START_YEAR]
all_peaks = sorted(peaks_max + peaks_min)

print(f"\nlocal extrema in era {ERA_START_YEAR}+:  {len(peaks_min)} minima, {len(peaks_max)} maxima")

# ----- Norayr-pick: RANSAC with band = ±1% in price space (per-point y-tolerance) -----
# ±1% in price → dy = 0.01 / ln(P) for ln(ln P) transform
lnP = np.log(np.array(prices))
tol_per_pt = 0.01 / lnP   # per-point tolerance in ln(ln P) units
MIN_SEP_YR = 5
# anchors restricted to before 2015 for proper OOS
preoos_peaks = [i for i in all_peaks if dates[i] < datetime(2015,1,1)]
best_score = -1
best_pair = None
ap_xs = xs[all_peaks]
ap_y = llp_np[all_peaks]
ap_tol = tol_per_pt[all_peaks]
for i_a, ia in enumerate(preoos_peaks):
    for ib in preoos_peaks[i_a+1:]:
        if xs[ib] - xs[ia] < MIN_SEP_YR:
            continue
        sl = (llp_np[ib] - llp_np[ia]) / (xs[ib] - xs[ia])
        ic = llp_np[ia] - sl * xs[ia]
        pred = ic + sl * ap_xs
        score = int(np.sum(np.abs(ap_y - pred) < ap_tol))
        if score > best_score:
            best_score = score
            best_pair = (ia, ib)

na, nb = best_pair
n_slope = (llp_np[nb] - llp_np[na]) / (xs[nb] - xs[na])
n_intercept = llp_np[na] - n_slope * xs[na]
n_cagr_yr = n_slope  # ln(ln P) / yr
# Implied %/yr from the two anchor prices
n_cagr_pct = (
    (prices[nb] / prices[na]) ** (1.0 / ((xs[nb] - xs[na]))) - 1
) * 100
print(f"Norayr-pick: {dates[na]:%b %Y} ({prices[na]:.2f}) → {dates[nb]:%b %Y} ({prices[nb]:.2f})")
print(f"  slope {n_slope:.5f} ln(lnP)/yr · implied CAGR {n_cagr_pct:.2f}%/yr · score {best_score} extrema within ±1% price band")

# ----- Hari version: L1 lower-envelope via linear programming -----
# Minimize sum(y - (a*t + b)) subject to a*t_i + b <= y_i for all i in era
t_e = xs[era_mask_all]
y_e = llp_np[era_mask_all]
c_obj = np.array([-float(np.sum(t_e)), -float(len(t_e))])
A_ub = np.column_stack([t_e, np.ones_like(t_e)])
b_ub = y_e
res = linprog(c_obj, A_ub=A_ub, b_ub=b_ub,
              bounds=[(None, None), (None, None)], method="highs")
h_slope, h_intercept = float(res.x[0]), float(res.x[1])
h_cagr_pct = (np.exp(np.exp(h_slope * xs[-1] + h_intercept))
              / np.exp(np.exp(h_slope * xs[-1] - h_slope + h_intercept)) - 1) * 100
# Simpler derived CAGR: compute ratio of predicted price at two endpoints
def undo_loglog(y): return float(np.exp(np.exp(y)))
_p0_h = undo_loglog(h_intercept + h_slope * xs[0])
_p1_h = undo_loglog(h_intercept + h_slope * xs[-1])
h_yrs = xs[-1] - xs[0]
h_cagr_pct = ((_p1_h / _p0_h) ** (1 / h_yrs) - 1) * 100
print(f"Hari envelope (L1 lower): slope {h_slope:.5f} ln(lnP)/yr · implied CAGR {h_cagr_pct:.2f}%/yr")

# ----- Traces: extrema markers, Norayr-pick line, Hari envelope line -----
# Extended line coords (reuse LINE_X_MIN/LINE_X_MAX from above).
# xs here is absolute year (year + month/12), so no y0 offset.
n_tmin = LINE_X_MIN.year + (LINE_X_MIN.month-1)/12
n_tmax = LINE_X_MAX.year + (LINE_X_MAX.month-1)/12

# Detected extrema overlay (small markers)
fig.add_trace(go.Scatter(
    x=[dates[i] for i in peaks_min], y=[llp_np[i] for i in peaks_min],
    mode="markers", name="local minima",
    marker=dict(size=7, color="#fca5a5", symbol="triangle-down",
                line=dict(color="#f87171", width=1)),
    hovertemplate="<b>min · %{x|%b %Y}</b><br>ln(ln P): %{y:.4f}<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=[dates[i] for i in peaks_max], y=[llp_np[i] for i in peaks_max],
    mode="markers", name="local maxima",
    marker=dict(size=7, color="#fde047", symbol="triangle-up",
                line=dict(color="#facc15", width=1)),
    hovertemplate="<b>max · %{x|%b %Y}</b><br>ln(ln P): %{y:.4f}<extra></extra>",
))

# Norayr-pick line (bright green, dashed — to distinguish from user's solid draggable)
fig.add_trace(go.Scatter(
    x=[LINE_X_MIN, LINE_X_MAX],
    y=[n_intercept + n_slope * n_tmin,
       n_intercept + n_slope * n_tmax],
    mode="lines",
    name=f"Norayr-pick · {dates[na]:%Y-%m}↔{dates[nb]:%Y-%m} · {n_cagr_pct:.1f}%/yr",
    line=dict(color="#4ade80", width=2.0, dash="dashdot"),
    hovertemplate="<b>%{x|%b %Y}</b><br>Norayr-pick: %{y:.4f}<extra></extra>",
))

# Hari envelope (orange, solid thin)
fig.add_trace(go.Scatter(
    x=[LINE_X_MIN, LINE_X_MAX],
    y=[h_intercept + h_slope * n_tmin, h_intercept + h_slope * n_tmax],
    mode="lines",
    name=f"Hari · L¹ lower envelope · {h_cagr_pct:.1f}%/yr",
    line=dict(color="#fb923c", width=1.8, dash="dot"),
    hovertemplate="<b>%{x|%b %Y}</b><br>envelope: %{y:.4f}<extra></extra>",
))

fig.update_layout(
    autosize=True,
    title=dict(
        text="<b>S&amp;P 500 · log-log transform · 1871 → 2026</b><br>"
             "<span style='font-size:13px;color:#a18050'>"
             "y = ln(ln(price)) &nbsp;·&nbsp; "
             "drag = zoom &nbsp;·&nbsp; shift+drag = pan &nbsp;·&nbsp; double-click = reset"
             "&nbsp;&nbsp;·&nbsp;&nbsp;<b>drag green circles to re-anchor</b>"
             "</span>",
        font=dict(color="#ffb94a", size=22, family="-apple-system, SF Pro Display"),
        x=0.02, xanchor="left",
    ),
    paper_bgcolor="#0d0a05",
    plot_bgcolor="#000000",
    yaxis=dict(
        title=dict(text="ln(ln(price))", font=dict(color="#ffb94a")),
        gridcolor="#332a18", zerolinecolor="#332a18",
        tickfont=dict(color="#a18050"),
        fixedrange=False,
    ),
    xaxis=dict(
        gridcolor="#332a18", zerolinecolor="#332a18",
        tickfont=dict(color="#a18050"),
        fixedrange=False,
        range=[datetime(2000, 1, 1), datetime(2045, 12, 1)],
    ),
    yaxis_range=[1.6, 2.25],
    hoverlabel=dict(bgcolor="#1a1208", font=dict(color="#ffd76a", family="SF Mono, Menlo")),
    margin=dict(l=70, r=40, t=110, b=80),
    showlegend=True,
    legend=dict(bgcolor="rgba(20,14,6,0.7)", font=dict(color="#a18050", size=11)),
    dragmode="zoom",
    newshape=dict(line=dict(color="#86efac", width=2.2)),
    updatemenus=[dict(
        type="buttons",
        direction="right",
        x=0.98, xanchor="right",
        y=1.10, yanchor="top",
        bgcolor="#14120e",
        bordercolor="#8a7228",
        borderwidth=1,
        font=dict(color="#ffd76a", size=11, family="-apple-system"),
        buttons=[
            dict(label="LOGLOG",
                 method="update",
                 args=[{"visible": [True, True, True,
                                    False, False, False,
                                    True, True,
                                    True, True, True, True]},
                       {"yaxis.title.text": "ln(ln(price))",
                        "yaxis.type": "linear",
                        "yaxis.autorange": True}]),
            dict(label="LIN",
                 method="update",
                 args=[{"visible": [False, False, False,
                                    True, True, True,
                                    False, False,
                                    False, False, False, False]},
                       {"yaxis.title.text": "S&P 500",
                        "yaxis.type": "linear",
                        "yaxis.autorange": True}]),
        ],
    )],
)

fig.add_annotation(
    text="Shiller + multpl · 1871 → 2026-04",
    xref="paper", yref="paper",
    x=1.0, y=-0.10, xanchor="right", yanchor="top",
    showarrow=False,
    font=dict(color="#5a4a28", size=11),
)

PLOT_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    "doubleClick": "autosize",
    "scrollZoom": False,
}

# Indices of the draggable traces (line + markers) in the final figure data
LINE_TRACE_IDX = 6
MARKER_TRACE_IDX = 7

chart_div = pio.to_html(fig, include_plotlyjs="cdn", full_html=False,
                         config=PLOT_CONFIG, div_id="loglog-chart")

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>S&P 500 · log-log eyeball</title>
<style>
  html, body {{ margin: 0; padding: 0; background: #0b0a08; color: #e8e2cf;
    font-family: -apple-system, "SF Pro Display", sans-serif; }}
  #chart-wrap {{ padding: 0 2vw; height: 95vh; }}
  #chart-wrap > div {{ height: 100%; }}
  #chart-wrap .js-plotly-plot,
  #chart-wrap .plot-container,
  #chart-wrap .plotly {{ height: 100% !important; }}
  #readout {{ margin: 2vh 6vw 4vh 6vw; padding: 1.5vh 2vw; background: #14120e;
    border: 1px solid #2d5a36; border-radius: 6px; color: #86efac;
    font-family: "SF Mono", Menlo, monospace; font-size: 1.5vh; line-height: 1.7; }}
  #readout b {{ color: #bbf7d0; }}
  #readout .hint {{ color: #8a846f; font-size: 1.2vh; }}
  .js-plotly-plot .plotly .draglayer > g {{ cursor: default; }}
</style>
</head>
<body>
<div id="chart-wrap">{chart_div}</div>
<div id="readout">
  <span class="hint">
    click and drag the green circles on the log-log chart &nbsp;·&nbsp;
    axis drag: default = zoom region, shift = pan
  </span><br>
  <b>anchor 1:</b> <span id="a0">—</span> &nbsp;→&nbsp; <b>anchor 2:</b> <span id="a1">—</span><br>
  <b>slope:</b> <span id="sl">—</span>  &nbsp;·&nbsp;  <b>implied CAGR:</b> <span id="cg">—</span>
</div>
<script>
(function () {{
  const gd = document.getElementById("loglog-chart");
  if (!gd) return;

  const MARKER_TRACE = {MARKER_TRACE_IDX};
  const LINE_TRACE = {LINE_TRACE_IDX};
  let dragging = null;  // which anchor index (0 or 1) is being dragged

  function fmtDate(v) {{
    try {{ return new Date(v).toISOString().slice(0, 10); }}
    catch (e) {{ return String(v); }}
  }}
  function undoLogLog(y) {{ return Math.exp(Math.exp(y)); }}
  function pxToDataX(xa, px) {{ return xa.p2d(px - xa._offset); }}
  function pxToDataY(ya, py) {{ return ya.p2d(py - ya._offset); }}

  const LINE_TMIN = new Date("1871-01-01").getTime();
  const LINE_TMAX = new Date("2045-01-01").getTime();
  const YEAR_MS = 365.25 * 24 * 3600 * 1000;

  function extendedLinePoints(mx, my) {{
    const t0 = new Date(mx[0]).getTime();
    const t1 = new Date(mx[1]).getTime();
    const dt = (t1 - t0) / YEAR_MS;
    if (Math.abs(dt) < 1e-9) return {{ x: mx, y: my }};
    const slope = (my[1] - my[0]) / dt;
    const yL = my[0] + slope * ((LINE_TMIN - t0) / YEAR_MS);
    const yR = my[0] + slope * ((LINE_TMAX - t0) / YEAR_MS);
    return {{
      x: [new Date(LINE_TMIN).toISOString(), new Date(LINE_TMAX).toISOString()],
      y: [yL, yR],
    }};
  }}

  function updateReadout() {{
    const mx = gd.data[MARKER_TRACE].x;
    const my = gd.data[MARKER_TRACE].y;
    const d0 = fmtDate(mx[0]), d1 = fmtDate(mx[1]);
    const p0 = undoLogLog(my[0]), p1 = undoLogLog(my[1]);
    const yr0 = new Date(mx[0]).getTime() / (365.25 * 24 * 3600 * 1000) + 1970;
    const yr1 = new Date(mx[1]).getTime() / (365.25 * 24 * 3600 * 1000) + 1970;
    const dt = yr1 - yr0;
    const cagr = Math.abs(dt) < 1e-6 ? 0 :
      (Math.pow(p1 / p0, 1 / dt) - 1) * 100;
    const slopeLn = Math.abs(dt) < 1e-6 ? 0 : (my[1] - my[0]) / dt;
    const fmt = n => n.toLocaleString(undefined, {{maximumFractionDigits: 2}});

    document.getElementById("a0").innerHTML = `${{d0}} &nbsp;·&nbsp; $${{fmt(p0)}}`;
    document.getElementById("a1").innerHTML = `${{d1}} &nbsp;·&nbsp; $${{fmt(p1)}}`;
    document.getElementById("sl").innerHTML = `${{slopeLn.toFixed(5)}} (ln(ln P)/yr)`;
    document.getElementById("cg").innerHTML = `${{cagr.toFixed(2)}}%/yr`;
  }}

  function markerAtPixel(px, py) {{
    const xa = gd._fullLayout.xaxis;
    const ya = gd._fullLayout.yaxis;
    const mx = gd.data[MARKER_TRACE].x;
    const my = gd.data[MARKER_TRACE].y;
    let closest = -1, closestDist = 25;
    for (let i = 0; i < mx.length; i++) {{
      const tx = new Date(mx[i]).getTime();
      const ty = my[i];
      const cx = xa._offset + xa.d2p(tx);
      const cy = ya._offset + ya.d2p(ty);
      const d = Math.hypot(px - cx, py - cy);
      if (d < closestDist) {{ closestDist = d; closest = i; }}
    }}
    return closest;
  }}

  function onMouseDown(e) {{
    const bb = gd.getBoundingClientRect();
    const px = e.clientX - bb.left;
    const py = e.clientY - bb.top;
    const hit = markerAtPixel(px, py);
    if (hit >= 0) {{
      dragging = hit;
      e.preventDefault();
      e.stopPropagation();
    }}
  }}

  function onMouseMove(e) {{
    if (dragging === null) return;
    e.preventDefault();
    e.stopPropagation();
    const bb = gd.getBoundingClientRect();
    const px = e.clientX - bb.left;
    const py = e.clientY - bb.top;
    const xa = gd._fullLayout.xaxis;
    const ya = gd._fullLayout.yaxis;
    const newXts = pxToDataX(xa, px);
    const newY = pxToDataY(ya, py);
    const mx = gd.data[MARKER_TRACE].x.slice();
    const my = gd.data[MARKER_TRACE].y.slice();
    mx[dragging] = new Date(newXts).toISOString();
    my[dragging] = newY;
    const line = extendedLinePoints(mx, my);
    Plotly.restyle(gd, {{ x: [mx], y: [my] }}, [MARKER_TRACE]);
    Plotly.restyle(gd, {{ x: [line.x], y: [line.y] }}, [LINE_TRACE]);
    updateReadout();
  }}

  function onMouseUp() {{
    dragging = null;
  }}

  // Use capturing phase so we can intercept before Plotly's own pan/zoom.
  gd.addEventListener("mousedown", onMouseDown, true);
  document.addEventListener("mousemove", onMouseMove, true);
  document.addEventListener("mouseup", onMouseUp, true);

  // Resize chart to fill container on load and on window resize
  function resize() {{ if (window.Plotly && gd) Plotly.Plots.resize(gd); }}
  window.addEventListener("resize", resize);
  setTimeout(resize, 200);

  // initial readout
  setTimeout(updateReadout, 400);
}})();
</script>
</body>
</html>"""

OUT.write_text(page, encoding="utf-8")
print(f"wrote {OUT}")

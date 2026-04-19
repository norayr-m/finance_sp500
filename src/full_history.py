#!/usr/bin/env python3
"""S&P 500 1871→2026 from Shiller xls → interactive Plotly HTML."""
import xlrd
from datetime import datetime
import plotly.graph_objects as go
import plotly.io as pio

book = xlrd.open_workbook("/Users/norayr/000_AI_Work/0_Projects/Done_GitHub_finance_sp500/data/shiller.xls")
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

# Append monthly closes through 2026-04 (Shiller xls lags ~6 months).
RECENT = [
    (2023,10,4258.98),(2023,11,4460.06),(2023,12,4685.05),
    (2024,1,4804.49),(2024,2,5011.96),(2024,3,5170.57),(2024,4,5095.46),
    (2024,5,5235.23),(2024,6,5415.14),(2024,7,5542.89),(2024,8,5502.17),
    (2024,9,5626.12),(2024,10,5792.32),(2024,11,5929.92),(2024,12,6010.91),
    (2025,1,5979.52),(2025,2,6038.69),(2025,3,5683.98),(2025,4,5369.50),
    (2025,5,5810.92),(2025,6,6029.95),(2025,7,6296.50),(2025,8,6408.95),
    (2025,9,6584.02),(2025,10,6735.69),(2025,11,6740.89),(2025,12,6853.03),
    (2026,1,6929.12),(2026,2,6893.81),(2026,3,6654.42),(2026,4,7041.28),
]
for y_r, m_r, p_r in RECENT:
    dt_r = datetime(y_r, m_r, 1)
    if dt_r > dates[-1]:
        dates.append(dt_r); prices.append(p_r)

print(f"loaded {len(dates)} months, range {dates[0]} → {dates[-1]}")
print(f"price range {min(prices):.2f} → {max(prices):.2f}")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=dates, y=prices, mode="lines",
    name="S&P 500 (Shiller monthly composite)",
    line=dict(color="#ffd76a", width=3, shape="linear"),
    hovertemplate="<b>%{x|%b %Y}</b><br>S&P: %{y:.2f}<extra></extra>",
))

# ---- Norayr's green line: straight line through two minimas ----
# The line rests on two chosen local lows and is extended both directions.
# This is an eyeball construction, not a statistical fit; it is intentional.
import math
import numpy as np
import pwlf
from scipy.optimize import minimize

def l1_fit(x, y):
    """L1 (least-absolute-deviation) linear fit.  Minimises sum |y - (a x + b)|."""
    p0 = np.polyfit(x, y, 1)
    res = minimize(lambda p: float(np.sum(np.abs(y - (p[0] * x + p[1])))),
                   p0, method="Nelder-Mead",
                   options={"xatol": 1e-9, "fatol": 1e-9, "maxiter": 20000})
    return float(res.x[0]), float(res.x[1])

y0 = dates[0].year
xs = np.array([(d.year + (d.month-1)/12) - y0 for d in dates])

MIN_1 = (datetime(2011, 9, 1), 1134.51)   # Sep 2011
MIN_2 = (datetime(2024, 11, 1), 6138.52)  # Nov 2024

mx1 = (MIN_1[0].year + (MIN_1[0].month-1)/12) - y0
mx2 = (MIN_2[0].year + (MIN_2[0].month-1)/12) - y0
slope_log = (math.log10(MIN_2[1]) - math.log10(MIN_1[1])) / (mx2 - mx1)
intercept_log = math.log10(MIN_1[1]) - slope_log * mx1
minima_cagr = (10 ** slope_log - 1) * 100
print(f"two-minima line through {MIN_1[0]:%Y-%m} ({MIN_1[1]}) and "
      f"{MIN_2[0]:%Y-%m} ({MIN_2[1]}): {minima_cagr:.2f}%/yr")

# Build dates covering 1871 → Dec 2045
def month_iter(start_dt, end_dt):
    cur = datetime(start_dt.year, start_dt.month, 1)
    out = []
    while cur <= end_dt:
        out.append(cur)
        next_m = cur.month + 1
        next_y = cur.year + (1 if next_m > 12 else 0)
        next_m = 1 if next_m > 12 else next_m
        cur = datetime(next_y, next_m, 1)
    return out

all_dates_2045 = month_iter(dates[0], datetime(2045, 12, 1))
all_xs = np.array([(d.year + (d.month-1)/12) - y0 for d in all_dates_2045])

# Green/blue lines only draw from Jan 2009 forward; red uses full range.
VIS_START = datetime(2009, 1, 1)
vis_start_x = (VIS_START.year + (VIS_START.month-1)/12) - y0

# Two-minima green line: solid Jan 2009 → today, dashed today → 2045
split_x = xs[-1]
minima_y = 10 ** (intercept_log + slope_log * all_xs)
solid_mask = (all_xs >= vis_start_x) & (all_xs <= split_x)
dashed_mask = all_xs >= split_x

fig.add_trace(go.Scatter(
    x=[d for d, m in zip(all_dates_2045, solid_mask) if m],
    y=minima_y[solid_mask], mode="lines",
    name=f"two-minima line · {minima_cagr:.2f}%/yr",
    line=dict(color="#86efac", width=2.4),
    hovertemplate="<b>%{x|%b %Y}</b><br>minima line: %{y:.0f}<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=[d for d, m in zip(all_dates_2045, dashed_mask) if m],
    y=minima_y[dashed_mask], mode="lines",
    name="two-minima line → 2045",
    line=dict(color="#86efac", width=2.4, dash="dash"),
    hovertemplate="<b>%{x|%b %Y}</b><br>minima proj: %{y:.0f}<extra></extra>",
    showlegend=False,
))

# Anchor markers
fig.add_trace(go.Scatter(
    x=[MIN_1[0], MIN_2[0]], y=[MIN_1[1], MIN_2[1]], mode="markers",
    name="anchor minimas", showlegend=False,
    marker=dict(color="#4ade80", size=10, symbol="circle-open",
                line=dict(color="#86efac", width=2)),
    hovertemplate="<b>anchor · %{x|%b %Y}</b><br>close: %{y:.2f}<extra></extra>",
))

# Red line: continuous piecewise log-linear fit, 3 segments (1871→now)
# Fit is in log10(P) space (i.e., the "log-log plot" with price on log y).
log_p_all = np.log10(np.array(prices))
N_SEG = 3
plf = pwlf.PiecewiseLinFit(xs, log_p_all)
breakpoint_xs = plf.fit(N_SEG)
fit_log = plf.predict(xs)
fit_price = 10 ** fit_log

# Segment stats
seg_info = []
for k in range(N_SEG):
    bp_a, bp_b = breakpoint_xs[k], breakpoint_xs[k+1]
    y_a = plf.predict(np.array([bp_a]))[0]
    y_b = plf.predict(np.array([bp_b]))[0]
    sl = (y_b - y_a) / (bp_b - bp_a)
    cagr = (10 ** sl - 1) * 100
    d_a = datetime(int(y0 + bp_a), max(1, min(12, int(round((bp_a - int(bp_a)) * 12)) + 1)), 1)
    d_b = datetime(int(y0 + bp_b), max(1, min(12, int(round((bp_b - int(bp_b)) * 12)) + 1)), 1)
    seg_info.append((d_a, d_b, cagr))
    print(f"PWLF segment {k+1}: {d_a:%Y-%m} → {d_b:%Y-%m}  {cagr:+.2f}%/yr")

fig.add_trace(go.Scatter(
    x=dates, y=fit_price, mode="lines",
    name=f"1871→now · {N_SEG}-segment PWLF (log space)",
    line=dict(color="#f87171", width=2.0),
    hovertemplate="<b>%{x|%b %Y}</b><br>PWLF: %{y:.2f}<extra></extra>",
))
# knot markers on the continuous fit
knot_x_vals = list(breakpoint_xs)
knot_dates_list = [datetime(int(y0 + bx),
                            max(1, min(12, int(round((bx - int(bx)) * 12)) + 1)),
                            1) for bx in knot_x_vals]
knot_prices_list = [float(10 ** plf.predict(np.array([bx]))[0]) for bx in knot_x_vals]
fig.add_trace(go.Scatter(
    x=knot_dates_list, y=knot_prices_list, mode="markers",
    name="PWLF knots", showlegend=False,
    marker=dict(color="#fca5a5", size=8, symbol="diamond-open",
                line=dict(color="#f87171", width=1.5)),
    hovertemplate="<b>knot · %{x|%b %Y}</b><br>%{y:.2f}<extra></extra>",
))

# Blue: log-linear OLS from Feb 2009, fit on all data from that point forward.
# Solid through today, dashed to 2045.
gfc_start = datetime(2009, 2, 1)
gfc_mask_data = np.array([d >= gfc_start for d in dates])
gfc_xs = xs[gfc_mask_data]
gfc_yw = log_p_all[gfc_mask_data]
gfc_slope, gfc_intercept = l1_fit(gfc_xs, gfc_yw)
gfc_cagr = (10 ** gfc_slope - 1) * 100
gfc_fit_all = 10 ** (gfc_intercept + gfc_slope * all_xs)

gfc_solid_mask = (all_xs >= vis_start_x) & (all_xs <= split_x)
gfc_dashed_mask = all_xs >= split_x

fig.add_trace(go.Scatter(
    x=[d for d, m in zip(all_dates_2045, gfc_solid_mask) if m],
    y=gfc_fit_all[gfc_solid_mask], mode="lines",
    name=f"Feb 2009→now L¹ fit · {gfc_cagr:.2f}%/yr",
    line=dict(color="#60a5fa", width=2.2),
    hovertemplate="<b>%{x|%b %Y}</b><br>L¹-fit: %{y:.0f}<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=[d for d, m in zip(all_dates_2045, gfc_dashed_mask) if m],
    y=gfc_fit_all[gfc_dashed_mask], mode="lines",
    name="Feb 2009→now fit → 2045",
    line=dict(color="#60a5fa", width=2.2, dash="dash"),
    hovertemplate="<b>%{x|%b %Y}</b><br>L¹-fit proj: %{y:.0f}<extra></extra>",
    showlegend=False,
))
print(f"Feb 2009→now L1 log-linear: {gfc_cagr:.2f}%/yr  →  Dec 2045: {gfc_fit_all[-1]:.0f}")

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

# Top-left annotation: two lines, one stat each
fig.add_annotation(
    xref="paper", yref="paper",
    x=0.02, y=0.98, xanchor="left", yanchor="top",
    text=(f"<span style='color:#86efac'><b>green · two-minima (eyeball mk1)</b>"
          f"  {minima_cagr:.2f}%/yr</span><br>"
          f"<span style='font-size:10px;color:#a18050'>"
          f"anchors: {MIN_1[0]:%b %Y} · {MIN_1[1]:.0f}"
          f"  →  {MIN_2[0]:%b %Y} · {MIN_2[1]:.0f}</span><br>"
          f"<span style='color:#60a5fa'><b>blue · Feb 2009→now L¹ fit</b>"
          f"  {gfc_cagr:.2f}%/yr</span><br>"
          f"<span style='color:#f87171'><b>red · 3-segment PWLF (log space)</b></span><br>"
          + "<br>".join(
              f"<span style='font-size:10px;color:#fca5a5'>"
              f"&nbsp;&nbsp;{d0:%Y}–{d1:%Y}  <b>{c:+.2f}%/yr</b></span>"
              for d0, d1, c in seg_info
          )),
    showarrow=False, align="left",
    bgcolor="rgba(20,14,6,0.92)", bordercolor="#8a7228", borderwidth=1,
    font=dict(color="#e8e2cf", size=11, family="-apple-system"),
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
             "Shiller monthly composite &nbsp;·&nbsp; "
             "drag = zoom &nbsp;·&nbsp; shift+drag = pan &nbsp;·&nbsp; double-click = reset"
             "</span>",
        font=dict(color="#ffb94a", size=22, family="-apple-system, SF Pro Display"),
        x=0.02, xanchor="left",
    ),
    paper_bgcolor="#0d0a05",
    plot_bgcolor="#000000",
    yaxis=dict(
        type="log",
        range=[3.0, 5.5],
        title=dict(text="S&P 500", font=dict(color="#ffb94a")),
        gridcolor="#332a18", zerolinecolor="#332a18",
        tickfont=dict(color="#a18050"),
        autorange=False,
        fixedrange=False,
    ),
    xaxis=dict(
        title=dict(text="", font=dict(color="#ffb94a")),
        gridcolor="#332a18", zerolinecolor="#332a18",
        tickfont=dict(color="#a18050"),
        range=[datetime(dates[-1].year - 100, 1, 1), datetime(2046, 1, 1)],
        rangeslider=dict(visible=True, bgcolor="#1a1208", thickness=0.06),
        fixedrange=False,
    ),
    dragmode="zoom",
    hoverlabel=dict(bgcolor="#1a1208", font=dict(color="#ffd76a", family="SF Mono, Menlo")),
    margin=dict(l=70, r=40, t=110, b=80),
    showlegend=False,
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
            dict(label="LOG Y",
                 method="relayout",
                 args=[{"yaxis.type": "log",
                        "yaxis.range": [3.0, 5.5],
                        "yaxis.autorange": False}]),
            dict(label="LINEAR Y",
                 method="relayout",
                 args=[{"yaxis.type": "linear",
                        "yaxis.range": [0, 12000],
                        "yaxis.autorange": False}]),
        ],
    )],
)

fig.add_annotation(
    text="⬡⟐ HARI · source: Robert Shiller online data (Yale economics)",
    xref="paper", yref="paper",
    x=1.0, y=-0.25, xanchor="right", yanchor="top",
    showarrow=False,
    font=dict(color="#5a4a28", size=11),
)

out = "/Users/norayr/000_AI_Work/0_Projects/Done_GitHub_finance_sp500/html/sp500_shiller_1871_2026.html"
pio.write_html(fig, file=out, include_plotlyjs="cdn", full_html=True,
               config={"displaylogo": False,
                       "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                       "doubleClick": "autosize",
                       "scrollZoom": False})
print(f"WROTE {out}  ({len(dates)} monthly points)")

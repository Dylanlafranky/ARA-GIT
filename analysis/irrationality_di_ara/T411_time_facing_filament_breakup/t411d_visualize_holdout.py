"""Create a fully labelled static visual for the frozen T411D holdout result."""

from pathlib import Path
import json
import math

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "T411D_causal_child_prediction"
EVENTS = OUT / "T411D_HOLDOUT_EVENTS.csv"
SERIES = OUT / "T411D_HOLDOUT_TIMESERIES.csv"
RESULTS = OUT / "T411D_HOLDOUT_RESULTS.json"
TARGET = OUT / "T411D_HOLDOUT_VISUAL.png"

W, H = 1800, 1200
INK = "#20262d"
MUTED = "#66717d"
GRID = "#d8dde3"
BLUE = "#1769aa"
ORANGE = "#c47c00"
LIGHT_BLUE = "#dceaf6"
LIGHT_ORANGE = "#f7ead1"
PANEL = "#fbfcfd"


def font(size, bold=False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)
events = pd.read_csv(EVENTS)
series = pd.read_csv(SERIES)
result = json.loads(RESULTS.read_text(encoding="utf-8"))
good = events[(~events.excluded) & events.child_prediction_t_s.notna()].copy()


def panel(rect, title, subtitle):
    x0, y0, x1, y1 = rect
    d.rounded_rectangle(rect, radius=10, fill=PANEL, outline="#c8d0d8", width=2)
    d.text((x0 + 22, y0 + 18), title, font=font(23, True), fill=INK)
    d.text((x0 + 22, y0 + 51), subtitle, font=font(15), fill=MUTED)


def scale(v, lo, hi, a, b):
    return a + (v - lo) * (b - a) / max(hi - lo, 1e-12)


def event_panel(rect, fluid):
    subset = good[(good.fluid == fluid) & (good.child_issue_t_s < good.target_t_s)].copy()
    med = subset.child_abs_error_u.median()
    row = subset.iloc[(subset.child_abs_error_u - med).abs().argsort().iloc[0]]
    g = series[series.Name == row.Name].sort_values("Time_s")
    panel(rect, f"Representative {fluid} event: {row.Name}",
          "Causal ARA coordinates; orange child is one octave below blue parent")
    x0, y0, x1, y1 = rect
    left, top, right, bottom = x0 + 74, y0 + 93, x1 - 25, y1 - 62
    xmax = float(g.Time_s.max())
    for val in np.linspace(0, 2, 5):
        yy = scale(val, 0, 2, bottom, top)
        d.line((left, yy, right, yy), fill=GRID, width=1)
        d.text((left - 48, yy - 9), f"{val:.1f}", font=font(13), fill=INK)
    for val in np.linspace(0, xmax, 6):
        xx = scale(val, 0, xmax, left, right)
        d.line((xx, top, xx, bottom), fill=GRID, width=1)
        d.text((xx - 19, bottom + 9), f"{val:.2f}", font=font(12), fill=INK)
    d.line((left, top, left, bottom), fill=INK, width=2)
    d.line((left, bottom, right, bottom), fill=INK, width=2)
    ridge = scale(1, 0, 2, bottom, top)
    d.line((left, ridge, right, ridge), fill=INK, width=2)
    d.text((right - 75, ridge - 20), "ridge 1.0", font=font(13, True), fill=INK)

    def draw_series(col, color, width):
        pts = []
        for _, r in g.iterrows():
            if math.isfinite(float(r[col])):
                pts.append((scale(float(r.Time_s), 0, xmax, left, right),
                            scale(float(r[col]), 0, 2, bottom, top)))
            elif len(pts) > 1:
                d.line(pts, fill=color, width=width)
                pts = []
        if len(pts) > 1:
            d.line(pts, fill=color, width=width)

    draw_series("x_child_connection_ara", ORANGE, 3)
    draw_series("x_parent_causal_ara", BLUE, 3)
    marks = [
        (row.child_issue_t_s, ORANGE, "child issue"),
        (row.child_prediction_t_s, BLUE, "forecast"),
        (row.target_t_s, INK, "offline target"),
    ]
    for j, (value, color, label) in enumerate(marks):
        xx = scale(value, 0, xmax, left, right)
        d.line((xx, top, xx, bottom), fill=color, width=2)
        d.text((left + 4, top + 7 + j * 21), f"{label}: {value:.3f} s",
               font=font(13, True), fill=color)
    d.text((left + (right-left)//2 - 48, y1 - 34), "physical time (s)", font=font(14, True), fill=INK)
    d.text((x0 + 15, top + 105), "ARA", font=font(14, True), fill=INK)
    d.line((right - 210, top + 13, right - 170, top + 13), fill=ORANGE, width=4)
    d.text((right - 162, top + 3), "child", font=font(13), fill=INK)
    d.line((right - 100, top + 13, right - 60, top + 13), fill=BLUE, width=4)
    d.text((right - 52, top + 3), "parent", font=font(13), fill=INK)


d.text((50, 28), "T411D — sealed temporal child-to-parent forecast", font=font(36, True), fill=INK)
d.text((50, 78), "Same filament system · S2/S4 untouched holdout · all issue times use current or earlier frames only",
       font=font(19), fill=MUTED)
d.text((50, 108), "Result: temporal ordering supported; fixed-seconds timestamp calibration not supported by the frozen six-gate rule",
       font=font(18, True), fill=ORANGE)

event_panel((45, 145, 875, 585), "S2")
event_panel((925, 145, 1755, 585), "S4")

# Forecast scatter
rect = (45, 625, 875, 1155)
panel(rect, "Forecast time versus offline parent target",
      "Each point is one filament; diagonal is perfect timestamp prediction; axes are seconds")
x0, y0, x1, y1 = rect
left, top, right, bottom = x0 + 84, y0 + 94, x1 - 35, y1 - 70
vmax = float(np.nanmax(good[["target_t_s", "child_prediction_t_s"]].to_numpy()))
ticks = np.linspace(0, vmax, 6)
for val in ticks:
    xx = scale(val, 0, vmax, left, right)
    yy = scale(val, 0, vmax, bottom, top)
    d.line((xx, top, xx, bottom), fill=GRID)
    d.line((left, yy, right, yy), fill=GRID)
    d.text((xx - 18, bottom + 10), f"{val:.1f}", font=font(12), fill=INK)
    d.text((left - 52, yy - 8), f"{val:.1f}", font=font(12), fill=INK)
d.line((left, bottom, right, top), fill=INK, width=2)
for _, r in good.iterrows():
    xx = scale(float(r.target_t_s), 0, vmax, left, right)
    yy = scale(float(r.child_prediction_t_s), 0, vmax, bottom, top)
    color = BLUE if r.fluid == "S2" else ORANGE
    d.ellipse((xx-5, yy-5, xx+5, yy+5), fill=color, outline=INK)
d.line((left, top, left, bottom), fill=INK, width=2)
d.line((left, bottom, right, bottom), fill=INK, width=2)
d.text((left + 210, y1 - 37), "offline parent target (s)", font=font(14, True), fill=INK)
d.text((x0 + 13, top + 130), "forecast\n(s)", font=font(14, True), fill=INK)
d.ellipse((right-170, top+4, right-158, top+16), fill=BLUE, outline=INK)
d.text((right-151, top+1), "S2", font=font(13), fill=INK)
d.ellipse((right-100, top+4, right-88, top+16), fill=ORANGE, outline=INK)
d.text((right-81, top+1), "S4", font=font(13), fill=INK)

# Gate and identity readout
rect = (925, 625, 1755, 1155)
panel(rect, "Frozen decisions and identity split", "Five gates pass; timestamp error gate fails")
x0, y0, x1, y1 = rect
gates = [
    ("Coverage >= 0.75", result["child_coverage"], True, "0.9512"),
    ("Pre-target issues >= 0.70", result["pre_target_issue_fraction"], True, "0.8846"),
    ("Median issue lead > 0", result["median_issue_lead_s"], True, "0.136 s"),
    ("Median |error| <= 0.10 lifetime", result["median_child_abs_error_u"], False, "0.2331"),
    ("Child issues before parent-only", result["median_child_before_parent_issue_s"], True, "0.0745 s"),
    ("Circular-shift p <= 0.05", result["shift_p_le_observed"], True, "0.00599"),
]
for i, (label, _, passed, value) in enumerate(gates):
    yy = y0 + 102 + i * 43
    fill = LIGHT_BLUE if passed else LIGHT_ORANGE
    color = BLUE if passed else ORANGE
    d.rounded_rectangle((x0+28, yy-5, x1-28, yy+31), radius=6, fill=fill)
    d.text((x0+42, yy+2), "PASS" if passed else "FAIL", font=font(14, True), fill=color)
    d.text((x0+115, yy+2), label, font=font(14), fill=INK)
    d.text((x1-42, yy+2), value, anchor="ra", font=font(14, True), fill=INK)

d.text((x0+30, y0+385), "Holdout identity medians", font=font(18, True), fill=INK)
d.text((x0+30, y0+421), "Fluid", font=font(14, True), fill=MUTED)
d.text((x0+130, y0+421), "forecast n", font=font(14, True), fill=MUTED)
d.text((x0+270, y0+421), "pre-target", font=font(14, True), fill=MUTED)
d.text((x0+430, y0+421), "lead", font=font(14, True), fill=MUTED)
d.text((x0+565, y0+421), "|error| / lifetime", font=font(14, True), fill=MUTED)
for i, fluid in enumerate(["S2", "S4"]):
    q = good[good.fluid == fluid]
    yy = y0 + 455 + i * 35
    vals = [fluid, str(len(q)), f"{(q.child_issue_t_s < q.target_t_s).mean():.3f}",
            f"{(q.target_t_s-q.child_issue_t_s).median():.3f} s", f"{q.child_abs_error_u.median():.3f}"]
    xs = [x0+30, x0+145, x0+285, x0+430, x0+625]
    for xx, text in zip(xs, vals):
        d.text((xx, yy), text, font=font(15, fluid == "S4"), fill=INK)

d.text((50, 1170), "Source: T411 source-qualified filament data · Target: offline T411C centred-rate crossing · Predictor: causal one-octave child cut",
       font=font(14), fill=MUTED)
im.save(TARGET, quality=95)
print(TARGET)

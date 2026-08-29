"""Create a fully labelled static Pillow visual for frozen T411E."""

from pathlib import Path
import json
import math

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "T411E_parent_child_ridge_drop"

BLUE = "#3267B1"
ORANGE = "#DD8A27"
INK = "#252936"
PURPLE = "#7656A5"
GOLD = "#C89A2B"
LIGHT = "#E8ECF2"
GRID = "#D9DEE7"
MUTED = "#5B6370"


def font(size, bold=False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


def dashed(draw, xy, fill, width=2, dash=10, gap=7):
    x1, y1, x2, y2 = xy
    dist = math.hypot(x2-x1, y2-y1)
    if dist == 0:
        return
    ux, uy = (x2-x1)/dist, (y2-y1)/dist
    p = 0.0
    while p < dist:
        q = min(p+dash, dist)
        draw.line((x1+ux*p, y1+uy*p, x1+ux*q, y1+uy*q), fill=fill, width=width)
        p += dash+gap


def line_panel(draw, box, events, series, fluid, title):
    x0, y0, x1, y1 = box
    e = events[(events.fluid == fluid) & events.pair_prediction_t_s.notna()
               & (events.pair_prediction_t_s < events.target_t_s)].copy()
    med = e.pair_abs_error_u.median()
    row = e.iloc[(e.pair_abs_error_u-med).abs().argmin()]
    g = series[series.Name == row.Name].sort_values("Time_s")
    tau = ((g.Time_s-row.target_t_s)/row.tbrk_s).to_numpy(float)
    pad_l, pad_r, pad_t, pad_b = 82, 22, 102, 76
    px0, px1 = x0+pad_l, x1-pad_r
    py0, py1 = y0+pad_t, y1-pad_b
    xmin, xmax, ymin, ymax = -0.55, 0.25, 0.0, 2.0

    X = lambda v: px0+(v-xmin)/(xmax-xmin)*(px1-px0)
    Y = lambda v: py1-(v-ymin)/(ymax-ymin)*(py1-py0)

    draw.rounded_rectangle(box, radius=13, fill="white", outline=GRID, width=2)
    draw.text((x0+20, y0+16), f"{title}: {fluid}, {row.Name}", font=font(22, True), fill=INK)
    draw.text((x0+20, y0+44),
              f"pair lead {row.pair_issue_lead_s:.3f} s · normalised |error| {row.pair_abs_error_u:.3f}",
              font=font(15), fill=MUTED)

    for xv in [-0.5, -0.25, 0, 0.25]:
        xx = X(xv)
        draw.line((xx, py0, xx, py1), fill=GRID, width=1)
        s = f"{xv:.2f}" if xv else "0"
        draw.text((xx-17, py1+10), s, font=font(14), fill=MUTED)
    for yv in [0, .5, 1, 1.5, 2]:
        yy = Y(yv)
        draw.line((px0, yy, px1, yy), fill=GRID, width=1)
        draw.text((px0-46, yy-8), f"{yv:.1f}", font=font(14), fill=MUTED)
    draw.line((px0, py0, px0, py1), fill=INK, width=2)
    draw.line((px0, py1, px1, py1), fill=INK, width=2)
    dashed(draw, (px0, Y(1), px1, Y(1)), PURPLE, 3, 11, 7)

    mask = (tau >= xmin) & (tau <= xmax)
    def plot(vals, color, width, dash_style=False):
        vals = np.asarray(vals, float)
        ok = mask & np.isfinite(vals)
        pts = [(X(a), Y(b)) for a, b in zip(tau[ok], vals[ok])]
        if len(pts) < 2:
            return
        if not dash_style:
            draw.line(pts, fill=color, width=width, joint="curve")
        else:
            for i in range(0, len(pts)-1, 3):
                draw.line(pts[i:min(i+2, len(pts))], fill=color, width=width)

    plot(g.x_child_connection_ara, BLUE, 4)
    plot(g.x_parent_causal_ara, ORANGE, 4, True)
    plot(g.x_parent_child_coarse, INK, 5)

    markers = [
        (row.child_issue_t_s, BLUE, "child issue"),
        (row.pair_prediction_t_s, GOLD, "pair drop"),
        (row.target_t_s, INK, "target"),
    ]
    for marker_i, (t, color, label) in enumerate(markers):
        if np.isfinite(t):
            xx = X((t-row.target_t_s)/row.tbrk_s)
            dashed(draw, (xx, py0, xx, py1), color, 3, 8, 5)
            draw.text((xx+4, py0+5+marker_i*19), label, font=font(13, True), fill=color)

    draw.text(((px0+px1)//2-145, y1-35),
              "time relative to observed handover / breakup lifetime",
              font=font(15), fill=INK)
    draw.text((x0+20, y0+76), "ARA coordinate (0–2)", font=font(14, True), fill=INK)
    return row


def legend(draw, y):
    items = [
        (BLUE, "child connection ARA xC", False),
        (ORANGE, "parent ARA xP", True),
        (INK, "coarse pair RPC=(xC+xP)/2", False),
        (PURPLE, "ARA ridge = 1", True),
    ]
    x = 185
    for color, label, is_dash in items:
        if is_dash:
            dashed(draw, (x, y+9, x+42, y+9), color, 4, 9, 5)
        else:
            draw.line((x, y+9, x+42, y+9), fill=color, width=5)
        draw.text((x+50, y), label, font=font(15), fill=INK)
        x += 365


def bar_panel(draw, box, results):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=13, fill="white", outline=GRID, width=2)
    draw.text((x0+20, y0+16), "Timing precision across causal ARA landmarks",
              font=font(22, True), fill=INK)
    draw.text((x0+20, y0+47), "Median absolute timing error / breakup lifetime · lower is better",
              font=font(15), fill=MUTED)
    m = results["all"]
    labels = ["parent-only", "child-only", "pair drop", "pair rise"]
    vals = [m["median_parent_error_u"], m["median_t411d_child_error_u"],
            m["median_abs_error_u"], m["median_upward_error_u"]]
    colors = [ORANGE, BLUE, GOLD, LIGHT]
    px0, px1, py0, py1 = x0+70, x1-25, y0+88, y1-68
    vmax = 0.30
    for tick in [0, .1, .2, .3]:
        yy = py1-tick/vmax*(py1-py0)
        draw.line((px0, yy, px1, yy), fill=GRID, width=1)
        draw.text((px0-44, yy-8), f"{tick:.1f}", font=font(13), fill=MUTED)
    gap = (px1-px0)/len(vals)
    bw = gap*0.56
    for i, (lab, val, color) in enumerate(zip(labels, vals, colors)):
        cx = px0+(i+.5)*gap
        top = py1-val/vmax*(py1-py0)
        draw.rectangle((cx-bw/2, top, cx+bw/2, py1), fill=color, outline=INK, width=2)
        draw.text((cx-28, top-26), f"{val:.3f}", font=font(16, True), fill=INK)
        draw.text((cx-38, py1+14), lab, font=font(14), fill=INK)


def control_panel(draw, box, results):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=13, fill="white", outline=GRID, width=2)
    draw.text((x0+20, y0+16), "Frozen circular-shift falsification control",
              font=font(22, True), fill=INK)
    draw.text((x0+20, y0+47), "1,000 shifts · median normalised timing error · lower is better",
              font=font(15), fill=MUTED)
    rows = [("all S1–S4 (87 predictions)", results["shift_control_all"]),
            ("diagnostic S2+S4 (65 predictions)", results["shift_control_diagnostic_S2_S4"])]
    px0, px1 = x0+250, x1-35
    xmin, xmax = .15, .34
    X = lambda v: px0+(v-xmin)/(xmax-xmin)*(px1-px0)
    for tick in [.15, .20, .25, .30, .34]:
        xx = X(tick)
        draw.line((xx, y0+92, xx, y1-55), fill=GRID, width=1)
        draw.text((xx-18, y1-42), f"{tick:.2f}", font=font(13), fill=MUTED)
    for idx, (label, r) in enumerate(rows):
        yy = y0+135+idx*115
        draw.text((x0+20, yy-12), label, font=font(15, True), fill=INK)
        draw.line((X(r["null_q05"]), yy, X(r["null_median"]), yy), fill=LIGHT, width=18)
        draw.ellipse((X(r["null_median"])-8, yy-8, X(r["null_median"])+8, yy+8),
                     fill="white", outline=INK, width=3)
        xo = X(r["observed_median_abs_error_u"])
        draw.polygon([(xo, yy-10), (xo+10, yy), (xo, yy+10), (xo-10, yy)],
                     fill=GOLD, outline=INK)
        draw.text((px0, yy+24),
                  f"observed {r['observed_median_abs_error_u']:.3f} · "
                  f"shift median {r['null_median']:.3f} · p={r['p_le_observed']:.3f}",
                  font=font(14), fill=MUTED)
    draw.text((x0+20, y1-36), "gold diamond = observed  |  open circle = shift-null median",
              font=font(14), fill=INK)


def main():
    events = pd.read_csv(OUT / "T411E_EVENTS.csv")
    series = pd.read_csv(OUT / "T411E_TIMESERIES.csv")
    results = json.loads((OUT / "T411E_RESULTS.json").read_text(encoding="utf-8"))
    im = Image.new("RGB", (1900, 1470), "#F7F8FA")
    draw = ImageDraw.Draw(im)
    draw.text((70, 40), "T411E — parent–child coarse-ridge drop test",
              font=font(34, True), fill=INK)
    draw.text((70, 88),
              "113 eligible filament handovers · causal five-frame persistence · same S1–S4 identities",
              font=font(18), fill=MUTED)
    draw.text((70, 120),
              "Finding: usually early, but not a specific timing ridge; circular shifts perform similarly.",
              font=font(21, True), fill=PURPLE)

    line_panel(draw, (55, 175, 940, 800), events, series, "S4", "Best-transfer family")
    line_panel(draw, (960, 175, 1845, 800), events, series, "S2", "Weaker-transfer family")
    legend(draw, 822)
    bar_panel(draw, (55, 875, 940, 1370), results)
    control_panel(draw, (960, 875, 1845, 1370), results)
    draw.text((70, 1410),
              "Boundary: recurring pre-handover state marker, not a validated causal clock. "
              "S2/S4 were inspected before T411E.",
              font=font(16), fill=MUTED)
    im.save(OUT / "T411E_RIDGE_DROP_VISUAL.png", dpi=(180, 180))


if __name__ == "__main__":
    main()

"""Fully labelled Pillow visual for T411F probability diagnostic."""

from pathlib import Path
import json
import math

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "T411F_phase_a_probability"
INK = "#252936"
MUTED = "#5B6370"
BLUE = "#3267B1"
ORANGE = "#DD8A27"
PURPLE = "#7656A5"
GOLD = "#C89A2B"
LIGHT = "#E8ECF2"
GRID = "#D9DEE7"


def font(size, bold=False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


def dashed(draw, xy, fill, width=2, dash=9, gap=6):
    x1, y1, x2, y2 = xy
    dist = math.hypot(x2-x1, y2-y1)
    if dist <= 0:
        return
    ux, uy = (x2-x1)/dist, (y2-y1)/dist
    p = 0
    while p < dist:
        q = min(p+dash, dist)
        draw.line((x1+ux*p, y1+uy*p, x1+ux*q, y1+uy*q), fill=fill, width=width)
        p += dash+gap


def panel(draw, box, title, subtitle):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=13, fill="white", outline=GRID, width=2)
    draw.text((x0+20, y0+15), title, font=font(22, True), fill=INK)
    draw.text((x0+20, y0+46), subtitle, font=font(15), fill=MUTED)


def probability_panel(draw, box, bins):
    panel(draw, box, "Event-balanced handover probability by visible child Phase A",
          "Outcome: parent handover within one frozen child window")
    x0, y0, x1, y1 = box
    px0, px1, py0, py1 = x0+75, x1-25, y0+90, y1-70
    X = lambda v: px0+v/2*(px1-px0)
    Y = lambda v: py1-v/.25*(py1-py0)
    for xv in [0, .5, .9, 1, 1.5, 2]:
        xx = X(xv)
        draw.line((xx, py0, xx, py1), fill=GRID, width=1)
        draw.text((xx-14, py1+11), f"{xv:g}", font=font(13), fill=MUTED)
    for yv in [0, .05, .10, .15, .20, .25]:
        yy = Y(yv)
        draw.line((px0, yy, px1, yy), fill=GRID, width=1)
        draw.text((px0-50, yy-8), f"{yv:.2f}", font=font(13), fill=MUTED)
    draw.line((px0, py0, px0, py1), fill=INK, width=2)
    draw.line((px0, py1, px1, py1), fill=INK, width=2)
    dashed(draw, (X(.9), py0, X(.9), py1), GOLD, 3)
    dashed(draw, (X(1), py0, X(1), py1), PURPLE, 3)
    draw.text((X(.9)-80, py0+5), "0.9 frozen threshold", font=font(12, True), fill=GOLD)
    draw.text((X(1)+5, py0+24), "1.0 ridge", font=font(12, True), fill=PURPLE)
    for label, color, use_dash in [("development", BLUE, False), ("diagnostic", ORANGE, True)]:
        g = bins[bins.partition == label].dropna(subset=["probability"])
        pts = [(X(float(r.mid)), Y(float(r.probability))) for _, r in g.iterrows()]
        if use_dash:
            for i in range(len(pts)-1):
                if i % 2 == 0:
                    draw.line((pts[i], pts[i+1]), fill=color, width=4)
        else:
            draw.line(pts, fill=color, width=4, joint="curve")
        for xx, yy in pts:
            draw.ellipse((xx-5, yy-5, xx+5, yy+5), fill="white", outline=color, width=3)
    draw.line((px0+15, py0+50, px0+58, py0+50), fill=BLUE, width=4)
    draw.text((px0+65, py0+40), "development S1+S3", font=font(14), fill=INK)
    dashed(draw, (px0+235, py0+50, px0+278, py0+50), ORANGE, 4)
    draw.text((px0+285, py0+40), "diagnostic S2+S4", font=font(14), fill=INK)
    draw.text(((px0+px1)//2-90, y1-37), "visible child Phase A (0–2)", font=font(15), fill=INK)
    draw.text((x0+16, py0-24), "probability", font=font(14, True), fill=INK)


def fluid_panel(draw, box, results):
    panel(draw, box, "0.9 risk difference by identity",
          "Above-0.9 probability minus below-0.9 probability; positive supports the proposal")
    x0, y0, x1, y1 = box
    px0, px1, py0, py1 = x0+70, x1-25, y0+95, y1-70
    ymin, ymax = -.40, .15
    Y = lambda v: py1-(v-ymin)/(ymax-ymin)*(py1-py0)
    for yv in [-.4, -.3, -.2, -.1, 0, .1]:
        yy = Y(yv)
        draw.line((px0, yy, px1, yy), fill=INK if yv == 0 else GRID, width=2 if yv == 0 else 1)
        draw.text((px0-48, yy-8), f"{yv:+.1f}", font=font(13), fill=MUTED)
    fluids = ["S1", "S2", "S3", "S4"]
    gap = (px1-px0)/4
    for i, f in enumerate(fluids):
        cx = px0+(i+.5)*gap
        p = results["by_fluid"][f]["primary"]["risk_difference"]
        a = results["by_fluid"][f]["approaching_comparator"]["risk_difference"]
        bw = gap*.22
        for offset, val, fill, outline in [(-bw*.6, p, BLUE, INK), (bw*.6, a, "white", ORANGE)]:
            top, zero = Y(max(val, 0)), Y(0)
            bottom = Y(min(val, 0))
            draw.rectangle((cx+offset-bw/2, top, cx+offset+bw/2, bottom),
                           fill=fill, outline=outline, width=3)
        draw.text((cx-12, py1+12), f, font=font(16, True), fill=INK)
        draw.text((cx-48, py1+38), f"{results['by_fluid'][f]['primary']['event_count']} events",
                  font=font(12), fill=MUTED)
    draw.rectangle((px0+8, py0+8, px0+28, py0+28), fill=BLUE, outline=INK)
    draw.text((px0+36, py0+7), "position alone", font=font(14), fill=INK)
    draw.rectangle((px0+190, py0+8, px0+210, py0+28), fill="white", outline=ORANGE, width=3)
    draw.text((px0+218, py0+7), "approaching only", font=font(14), fill=INK)


def threshold_panel(draw, box, thresholds):
    panel(draw, box, "Fixed-threshold controls",
          "Risk difference across predeclared child Phase A thresholds")
    x0, y0, x1, y1 = box
    px0, px1, py0, py1 = x0+75, x1-25, y0+90, y1-65
    xmin, xmax, ymin, ymax = .7, 1.2, -.06, .10
    X = lambda v: px0+(v-xmin)/(xmax-xmin)*(px1-px0)
    Y = lambda v: py1-(v-ymin)/(ymax-ymin)*(py1-py0)
    for xv in [.7, .8, .9, 1, 1.1, 1.2]:
        xx = X(xv)
        draw.line((xx, py0, xx, py1), fill=GRID, width=1)
        draw.text((xx-13, py1+10), f"{xv:.1f}", font=font(13), fill=MUTED)
    for yv in [-.05, 0, .05, .10]:
        yy = Y(yv)
        draw.line((px0, yy, px1, yy), fill=INK if yv == 0 else GRID, width=2 if yv == 0 else 1)
        draw.text((px0-50, yy-8), f"{yv:+.2f}", font=font(13), fill=MUTED)
    dashed(draw, (X(.9), py0, X(.9), py1), GOLD, 3)
    for label, color, use_dash in [("development", BLUE, False), ("diagnostic", ORANGE, True)]:
        g = thresholds[thresholds.partition == label].sort_values("threshold")
        pts = [(X(float(r.threshold)), Y(float(r.risk_difference))) for _, r in g.iterrows()]
        if use_dash:
            for i in range(len(pts)-1):
                if i % 2 == 0:
                    draw.line((pts[i], pts[i+1]), fill=color, width=4)
        else:
            draw.line(pts, fill=color, width=4)
        for xx, yy in pts:
            draw.ellipse((xx-5, yy-5, xx+5, yy+5), fill="white", outline=color, width=3)
    draw.text(((px0+px1)//2-105, y1-34), "candidate Phase A threshold", font=font(15), fill=INK)
    draw.text((x0+16, py0-23), "risk difference", font=font(14, True), fill=INK)


def validation_panel(draw, box, results):
    panel(draw, box, "Transfer and falsification checks",
          "Development probabilities applied unchanged to diagnostic identities")
    x0, y0, x1, y1 = box
    cal = results["calibration"]
    shift = results["circular_shift"]
    rows = [
        ("Diagnostic Brier", cal["diagnostic_brier"], cal["diagnostic_constant_brier"], "lower is better"),
        ("Diagnostic AUC", cal["diagnostic_auc"], .5, "higher is better"),
        ("Pooled risk difference", shift["observed_risk_difference"], shift["null_q95"], "must exceed shift 95%"),
    ]
    y = y0+105
    for label, observed, reference, note in rows:
        draw.text((x0+25, y), label, font=font(17, True), fill=INK)
        draw.text((x0+300, y), f"observed {observed:.4f}", font=font(17), fill=GOLD)
        draw.text((x0+500, y), f"reference {reference:.4f}", font=font(17), fill=INK)
        draw.text((x0+25, y+27), note, font=font(13), fill=MUTED)
        y += 78
    draw.line((x0+20, y+5, x1-20, y+5), fill=GRID, width=2)
    draw.text((x0+25, y+25), f"Frozen gates passed: {results['gate_count']}",
              font=font(24, True), fill=PURPLE)
    draw.text((x0+25, y+65),
              "Position alone does not transfer. Pooled shift p = "
              f"{shift['p_ge_observed']:.3f}.", font=font(16), fill=INK)
    draw.text((x0+25, y+98),
              "The diagnostic curve peaks below the ridge, around 0.7–0.9, then falls.",
              font=font(16, True), fill=ORANGE)


def main():
    results = json.loads((OUT / "T411F_RESULTS.json").read_text(encoding="utf-8"))
    bins = pd.read_csv(OUT / "T411F_PROBABILITY_BINS.csv")
    thresholds = pd.read_csv(OUT / "T411F_THRESHOLD_CONTROLS.csv")
    im = Image.new("RGB", (1900, 1470), "#F7F8FA")
    draw = ImageDraw.Draw(im)
    draw.text((65, 38), "T411F — one-sided child Phase A probability scale",
              font=font(34, True), fill=INK)
    draw.text((65, 86),
              "123 events · 10,800 causal snapshots · 0.9 = 90% of one TE-ARA half",
              font=font(18), fill=MUTED)
    draw.text((65, 120),
              "Result: a strong development signal did not transfer across identities; position alone is insufficient.",
              font=font(20, True), fill=PURPLE)
    probability_panel(draw, (50, 170, 940, 800), bins)
    fluid_panel(draw, (960, 170, 1850, 800), results)
    threshold_panel(draw, (50, 825, 940, 1375), thresholds)
    validation_panel(draw, (960, 825, 1850, 1375), results)
    draw.text((65, 1415),
              "Boundary: post-hoc archive diagnostic. Phase B budget = 2−A is bookkeeping, not an observed second child.",
              font=font(16), fill=MUTED)
    im.save(OUT / "T411F_PHASE_A_PROBABILITY_VISUAL.png", dpi=(180, 180))


if __name__ == "__main__":
    main()

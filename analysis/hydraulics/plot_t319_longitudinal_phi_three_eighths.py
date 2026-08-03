#!/usr/bin/env python3
"""Render the seven untouched longitudinal T319 profiles on the ARA 0–2 axis."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
STATIONS = HERE / "T319_LONGITUDINAL_PHI_THREE_EIGHTHS_STATIONS.csv"
RESULTS = HERE / "T319_LONGITUDINAL_PHI_THREE_EIGHTHS_RESULTS.json"
OUTPUT = HERE / "T319_LONGITUDINAL_PHI_THREE_EIGHTHS_FIGURE.png"

W, H = 1900, 2140
BG = "#f7f9fc"
INK = "#172033"
MUTED = "#5f6b7a"
GRID = "#d8dee8"
BLUE = "#3977c3"
AMBER = "#d99425"
GREEN = "#2b9a66"
PURPLE = "#8756b3"
RED = "#c24a4a"


def font(size: int, bold: bool = False):
    options = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf"),
    ]
    for candidate in options:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


F_TITLE = font(46, True)
F_SUB = font(25)
F_HEAD = font(28, True)
F_BODY = font(22)
F_SMALL = font(18)
F_TINY = font(15)


def read_rows():
    with STATIONS.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for key in ["s_m", "x_ara", "Us_m_per_s", "depth_m", "motion_peak", "structure_peak"]:
            row[key] = float(row[key])
    return rows


def map_x(x, left, right):
    return left + x / 2 * (right - left)


def normalized_points(rows, field, left, top, right, bottom):
    values = [r[field] for r in rows]
    lo, hi = min(values), max(values)
    span = hi - lo or 1
    points = []
    for row in rows:
        xx = map_x(row["x_ara"], left, right)
        yy = bottom - (row[field] - lo) / span * (bottom - top)
        points.append((xx, yy))
    return points, lo, hi


def landmarks(draw, left, top, right, bottom, label=False):
    phi_low = (3 - math.sqrt(5)) / 2
    positions = [
        (1 / 3, MUTED, "1/3 control"),
        (3 / 8, GREEN, "3/8"),
        (phi_low, PURPLE, "2−φ"),
        (1, INK, "ridge"),
        (2 - phi_low, PURPLE, "φ"),
        (2 - 3 / 8, GREEN, "13/8"),
        (2 - 1 / 3, MUTED, "5/3 control"),
    ]
    for x, colour, text in positions:
        px = map_x(x, left, right)
        width = 3 if text in {"2−φ", "φ", "3/8", "13/8"} else 1
        draw.line((px, top, px, bottom), fill=colour, width=width)
        if label:
            draw.text((px + 4, bottom + 5), text, fill=colour, font=F_TINY)


def draw_profile(draw, rows, field, peak_key, colour, box, label):
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=10, fill="white", outline=GRID, width=2)
    plot = (left + 58, top + 32, right - 25, bottom - 38)
    landmarks(draw, *plot, label=False)
    pts, lo, hi = normalized_points(rows, field, *plot)
    draw.line(pts, fill=colour, width=5, joint="curve")
    for row, point in zip(rows, pts):
        radius = 9 if row[peak_key] == 1 else 4
        draw.ellipse((point[0] - radius, point[1] - radius, point[0] + radius, point[1] + radius), fill=colour)
    draw.text((left + 14, top + 6), label, fill=INK, font=F_BODY)
    draw.text((left + 12, bottom - 30), "0", fill=MUTED, font=F_SMALL)
    draw.text((right - 25, bottom - 30), "2", fill=MUTED, font=F_SMALL)
    draw.text((left + 12, top + 38), f"max {hi:.4g}", fill=colour, font=F_TINY)
    draw.text((left + 12, bottom - 58), f"min {lo:.4g}", fill=MUTED, font=F_TINY)


rows = read_rows()
result = json.loads(RESULTS.read_text(encoding="utf-8"))
runs = result["eligible_runs"]

image = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(image)
draw.text((70, 42), "T319 — the corrected longitudinal river cut", fill=INK, font=F_TITLE)
draw.text((70, 105), "Upstream 0 → downstream 2; each row is one untouched centreline run", fill=MUTED, font=F_SUB)

draw.rounded_rectangle((70, 150, W - 70, 285), radius=18, fill="#eef3f8", outline=GRID, width=2)
draw.text((95, 172), "Result: exact Phi versus 3/8 is unresolved at this station spacing.", fill=INK, font=F_HEAD)
draw.text((95, 216), "The closest raw stations are 0.105–0.333 ARA apart; Phi and 3/8 are only 0.00697 apart.", fill=MUTED, font=F_BODY)
draw.text((95, 250), "The visible locations are still reported below—no smoothing, interpolation, or post-result axis flip.", fill=MUTED, font=F_SMALL)

left_box = (150, 350, 930, 525)
right_box = (990, 350, W - 70, 525)
draw.text((left_box[0], 310), "Motion cut: depth-averaged streamwise speed", fill=BLUE, font=F_HEAD)
draw.text((right_box[0], 310), "Connection cut: accumulated water depth", fill=AMBER, font=F_HEAD)

row_height = 230
start_y = 360
for idx, run in enumerate(runs):
    rr = [r for r in rows if r["run"] == run]
    y0 = start_y + idx * row_height
    family = "plain bed" if run.startswith("P") else "undulating bed"
    draw.text((15, y0 + 68), run, fill=INK, font=F_BODY)
    draw.text((15, y0 + 98), family, fill=MUTED, font=F_TINY)
    draw_profile(draw, rr, "Us_m_per_s", "motion_peak", BLUE, (150, y0, 930, y0 + 180), "Us (m/s)")
    draw_profile(draw, rr, "depth_m", "structure_peak", AMBER, (990, y0, W - 70, y0 + 180), "depth (m)")

legend_y = start_y + len(runs) * row_height + 5
draw.rounded_rectangle((70, legend_y, W - 70, H - 60), radius=16, fill="white", outline=GRID, width=2)
draw.text((95, legend_y + 20), "Landmarks", fill=INK, font=F_HEAD)
items = [(BLUE, "motion profile / maximum"), (AMBER, "depth profile / maximum"), (GREEN, "3/8 and 13/8"), (PURPLE, "2−φ and φ"), (MUTED, "1/3 and 5/3 controls"), (INK, "1.0 ridge")]
x, y = 95, legend_y + 68
for colour, text in items:
    draw.line((x, y + 11, x + 38, y + 11), fill=colour, width=5)
    draw.text((x + 50, y), text, fill=INK, font=F_SMALL)
    x += 285
    if x > W - 320:
        x = 95
        y += 38

image.save(OUTPUT)
print(json.dumps({"output": str(OUTPUT), "width": W, "height": H, "runs": runs}, indent=2))

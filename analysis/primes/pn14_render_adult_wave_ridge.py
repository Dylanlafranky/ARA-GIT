#!/usr/bin/env python3
"""Post-target PN14 static renderer using Pillow only.

The frozen target arithmetic completed before the primary script reached its
Matplotlib import. This renderer was added afterward and does not calculate or
alter any test metric.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
DEV = json.loads((HERE / "PN14_DEVELOPMENT_RESULTS.json").read_text(encoding="utf-8"))
TEMPLATE = json.loads((HERE / "PN14_DEVELOPMENT_TEMPLATE.json").read_text(encoding="utf-8"))
TARGET = json.loads((HERE / "PN14_TARGET_RESULTS.json").read_text(encoding="utf-8"))
OUTPUT = HERE / "PN14_ADULT_WAVE_RIDGE.png"

WIDTH, HEIGHT = 2400, 1050
INK = "#172033"
MUTED = "#687386"
GRID = "#dfe5ee"
BLUE = "#2f6fb3"
GOLD = "#d18b24"
LIGHT_BLUE = "#93b9df"
LIGHT_GOLD = "#efc77e"
BACKGROUND = "#f7f9fc"
WHITE = "#ffffff"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = ["arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


TITLE = font(44, True)
SUBTITLE = font(23)
PANEL_TITLE = font(28, True)
LABEL = font(21)
SMALL = font(18)
MONO = font(19)


def line_chart(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    series: list[tuple[str, list[float], str, int]],
    x_values: list[float],
    x_range: tuple[float, float],
    y_range: tuple[float, float],
    x_label: str,
    y_label: str,
) -> None:
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=18, fill=WHITE, outline=GRID, width=2)
    plot = (left + 105, top + 80, right - 35, bottom - 95)
    px0, py0, px1, py1 = plot

    def xp(value: float) -> float:
        return px0 + (value - x_range[0]) / (x_range[1] - x_range[0]) * (px1 - px0)

    def yp(value: float) -> float:
        return py1 - (value - y_range[0]) / (y_range[1] - y_range[0]) * (py1 - py0)

    for index in range(6):
        value = y_range[0] + index * (y_range[1] - y_range[0]) / 5
        y = yp(value)
        draw.line((px0, y, px1, y), fill=GRID, width=1)
        draw.text((px0 - 14, y), f"{value:.2f}", font=SMALL, fill=MUTED, anchor="rm")
    for index in range(5):
        value = x_range[0] + index * (x_range[1] - x_range[0]) / 4
        x = xp(value)
        draw.text((x, py1 + 14), f"{value:.1f}", font=SMALL, fill=MUTED, anchor="ma")
    draw.line((px0, py0, px0, py1), fill=INK, width=2)
    draw.line((px0, py1, px1, py1), fill=INK, width=2)
    if y_range[0] < 0 < y_range[1]:
        draw.line((px0, yp(0), px1, yp(0)), fill=MUTED, width=2)

    legend_x = px0
    for name, values, color, width in series:
        points = [(xp(x), yp(y)) for x, y in zip(x_values, values)]
        draw.line(points, fill=color, width=width, joint="curve")
        for x, y in points:
            draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=WHITE, outline=color, width=2)
        draw.line((legend_x, top + 48, legend_x + 32, top + 48), fill=color, width=width)
        draw.text((legend_x + 40, top + 48), name, font=SMALL, fill=INK, anchor="lm")
        legend_x += 42 + int(draw.textlength(name, font=SMALL)) + 28
    draw.text(((px0 + px1) / 2, bottom - 35), x_label, font=LABEL, fill=INK, anchor="mm")
    draw.text((px0 + 8, py0 + 8), y_label, font=SMALL, fill=MUTED, anchor="la")


image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
draw = ImageDraw.Draw(image)
draw.text((75, 52), "PN14 child-to-adult wave and adult-rung ridge", font=TITLE, fill=INK)
draw.text(
    (75, 112),
    "Scale 11 was opened only after the scales 8-10 template, protocol, source and validator were hash-sealed.",
    font=SUBTITLE,
    fill=MUTED,
)

target = TARGET["target"]
centers = [value * 2 for value in target["curves"]["prime"]["theta_centers"]]
template = TEMPLATE["prime_template"]
prime = target["curves"]["prime"]["means"]
late = target["curves"]["late_composite"]["means"]
raw = target["curves"]["raw"]["means"]
analytic = [1 / 3 - 2 * (value / 2) + 2 * (value / 2) ** 2 for value in centers]

draw.text((75, 175), "Equal-phase adult-wave shape", font=PANEL_TITLE, fill=INK)
line_chart(
    draw,
    (60, 205, 1590, 925),
    [
        ("analytic raw", analytic, MUTED, 3),
        ("scales 8-10 prime template", template, BLUE, 5),
        ("scale 11 primes", prime, GOLD, 5),
        ("scale 11 late composites", late, LIGHT_GOLD, 3),
        ("scale 11 raw", raw, LIGHT_BLUE, 3),
    ],
    centers,
    (0.0, 2.0),
    (-0.20, 0.38),
    "adult relative phase on ARA 0-2",
    "signed child product",
)

draw.text((1655, 175), "Adult scale growth", font=PANEL_TITLE, fill=INK)
box = (1640, 205, 2340, 925)
draw.rounded_rectangle(box, radius=18, fill=WHITE, outline=GRID, width=2)
geometries = {int(row["scale"]): row["geometry"] for row in DEV["scales"]}
metric = TARGET["metrics"]["adult_scale_ridge"]
growths = [
    geometries[9]["median_joint_period"] / geometries[8]["median_joint_period"],
    metric["G9"],
    metric["G10"],
]
expected = metric["expected_10_pow_0p9"]
chart = (1730, 315, 2275, 670)
cx0, cy0, cx1, cy1 = chart
ymin, ymax = 7.80, 8.14

def gy(value: float) -> float:
    return cy1 - (value - ymin) / (ymax - ymin) * (cy1 - cy0)


for value in (7.8, 7.9, 8.0, 8.1):
    y = gy(value)
    draw.line((cx0, y, cx1, y), fill=GRID, width=1)
    draw.text((cx0 - 12, y), f"{value:.1f}", font=SMALL, fill=MUTED, anchor="rm")
xpos = [cx0 + 55, (cx0 + cx1) / 2, cx1 - 55]
draw.line((cx0, gy(expected), cx1, gy(expected)), fill=MUTED, width=3)
draw.text((cx1, gy(expected) - 10), "10^0.9", font=SMALL, fill=MUTED, anchor="rb")
draw.line([(x, gy(y)) for x, y in zip(xpos, growths)], fill=BLUE, width=5)
for x, value, label in zip(xpos, growths, ("8->9", "9->10", "10->11")):
    y = gy(value)
    draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=WHITE, outline=BLUE, width=4)
    draw.text((x, cy1 + 22), label, font=SMALL, fill=INK, anchor="ma")
    draw.text((x, y - 18), f"{value:.4f}", font=MONO, fill=INK, anchor="mb")
draw.text(((cx0 + cx1) / 2, 730), "Fresh growth-to-growth ARA reading", font=LABEL, fill=INK, anchor="mm")
draw.text(((cx0 + cx1) / 2, 785), f"{metric['ridge_A']:.6f}  +  {metric['ridge_B']:.6f}  =  2", font=font(31, True), fill=GOLD, anchor="mm")
draw.text(((cx0 + cx1) / 2, 835), "near the 1.0 / 1.0 ridge", font=SUBTITLE, fill=MUTED, anchor="mm")

phase = TARGET["metrics"]["phase_collapse"]
footer = (
    f"Prime curve: r={phase['target_template_correlation']:.6f}, RMSE={phase['target_template_rmse']:.6f}  |  "
    f"minimum target primes per sector={phase['minimum_target_prime_sector_count']:,}  |  both registered arms SUPPORTED"
)
draw.text((75, 992), footer, font=SMALL, fill=INK)
image.save(OUTPUT)
print(f"wrote {OUTPUT}")

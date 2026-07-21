#!/usr/bin/env python3
"""Render a static QA preview of the post-target PN15 results."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
DEV = json.loads((HERE / "PN15_DEVELOPMENT_RESULTS.json").read_text(encoding="utf-8"))
TEMPLATE = json.loads((HERE / "PN15_DEVELOPMENT_TEMPLATE.json").read_text(encoding="utf-8"))
TARGET = json.loads((HERE / "PN15_TARGET_RESULTS.json").read_text(encoding="utf-8"))
OUTPUT = HERE / "PN15_SQRT_ADULT_RIDGE.png"

WIDTH, HEIGHT = 2400, 1080
INK = "#172033"
MUTED = "#687386"
GRID = "#dfe5ee"
BLUE = "#2f6fb3"
GOLD = "#d18b24"
ORANGE = "#dd6b20"
OLIVE = "#7f8f3a"
PINK = "#b85c8a"
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


TITLE = font(43, True)
SUBTITLE = font(22)
PANEL_TITLE = font(27, True)
LABEL = font(20)
SMALL = font(17)
MONO = font(18)


def line_chart(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    series: list[tuple[str, list[float], str, int]],
    x_values: list[float],
) -> None:
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=18, fill=WHITE, outline=GRID, width=2)
    px0, py0, px1, py1 = left + 105, top + 90, right - 35, bottom - 90

    def xp(value: float) -> float:
        return px0 + value / 2.0 * (px1 - px0)

    def yp(value: float) -> float:
        return py1 - (value + 0.20) / 0.58 * (py1 - py0)

    for value in (-0.2, -0.1, 0.0, 0.1, 0.2, 0.3):
        y = yp(value)
        draw.line((px0, y, px1, y), fill=GRID, width=1)
        draw.text((px0 - 12, y), f"{value:.1f}", font=SMALL, fill=MUTED, anchor="rm")
    for value in (0.0, 0.5, 1.0, 1.5, 2.0):
        x = xp(value)
        draw.text((x, py1 + 14), f"{value:.1f}", font=SMALL, fill=MUTED, anchor="ma")
    draw.line((px0, py0, px0, py1), fill=INK, width=2)
    draw.line((px0, py1, px1, py1), fill=INK, width=2)
    draw.line((px0, yp(0), px1, yp(0)), fill=MUTED, width=2)

    legend_x = px0
    for name, values, color, width in series:
        points = [(xp(x), yp(y)) for x, y in zip(x_values, values)]
        draw.line(points, fill=color, width=width, joint="curve")
        for x, y in points:
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=WHITE, outline=color, width=2)
        draw.line((legend_x, top + 52, legend_x + 28, top + 52), fill=color, width=width)
        draw.text((legend_x + 36, top + 52), name, font=SMALL, fill=INK, anchor="lm")
        legend_x += 38 + int(draw.textlength(name, font=SMALL)) + 24
    draw.text(((px0 + px1) / 2, bottom - 30), "relative phase mapped to ARA 0-2", font=LABEL, fill=INK, anchor="mm")
    draw.text((px0 + 8, py0 + 8), "mean centered closure", font=SMALL, fill=MUTED, anchor="la")


image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
draw = ImageDraw.Draw(image)
draw.text((70, 48), "PN15 full square-root child closure and adult-rung ridge", font=TITLE, fill=INK)
draw.text(
    (70, 108),
    "Scale 12 was opened only after the scales 8-11 protocol, template, executable inputs and validator were hash-sealed.",
    font=SUBTITLE,
    fill=MUTED,
)

theta = TEMPLATE["theta_centers"]
x_values = [2 * value for value in theta]
prime = TARGET["target"]["curves"]["prime"]["means"]
composite = TARGET["target"]["curves"]["composite"]["means"]
raw = TARGET["target"]["curves"]["raw"]["means"]
template = TEMPLATE["prime_template"]
analytic = [1 / 3 - 2 * value + 2 * value**2 for value in theta]

draw.text((70, 165), "Relative-phase closure shape", font=PANEL_TITLE, fill=INK)
line_chart(
    draw,
    (55, 195, 1600, 935),
    [
        ("analytic", analytic, MUTED, 3),
        ("development", template, BLUE, 5),
        ("target primes", prime, GOLD, 5),
        ("target composites", composite, ORANGE, 3),
        ("target raw", raw, OLIVE, 3),
    ],
    x_values,
)

draw.text((1660, 165), "Adult-rung deviation", font=PANEL_TITLE, fill=INK)
box = (1645, 195, 2345, 935)
draw.rounded_rectangle(box, radius=18, fill=WHITE, outline=GRID, width=2)
periods = {
    int(item["scale"]): float(item["geometry"]["median_joint_period"])
    for item in DEV["scales"]
}
periods[12] = float(TARGET["target"]["geometry"]["median_joint_period"])
growths = [periods[scale + 1] / periods[scale] for scale in range(8, 12)]
deviations = [abs(growth / 10 - 1) * 100 for growth in growths]
labels = ["8→9", "9→10", "10→11", "11→12"]

cx0, cy0, cx1, cy1 = 1730, 300, 2280, 645
ymax = 0.16


def gy(value: float) -> float:
    return cy1 - value / ymax * (cy1 - cy0)


for value in (0.00, 0.04, 0.08, 0.12, 0.16):
    y = gy(value)
    draw.line((cx0, y, cx1, y), fill=GRID, width=1)
    draw.text((cx0 - 12, y), f"{value:.2f}%", font=SMALL, fill=MUTED, anchor="rm")
bar_width = 76
gap = (cx1 - cx0) / len(deviations)
for index, (label, growth, deviation) in enumerate(zip(labels, growths, deviations)):
    x = cx0 + gap * (index + 0.5)
    color = GOLD if index == 3 else BLUE
    draw.rectangle((x - bar_width / 2, gy(deviation), x + bar_width / 2, cy1), fill=color, outline=INK, width=1)
    draw.text((x, cy1 + 18), label, font=SMALL, fill=INK, anchor="ma")
    draw.text((x, gy(deviation) - 12), f"{deviation:.4f}%", font=MONO, fill=INK, anchor="mb")
draw.text(((cx0 + cx1) / 2, 700), "absolute deviation from registered 10× growth", font=SMALL, fill=MUTED, anchor="mm")

adult = TARGET["metrics"]["full_sqrt_adult_ridge"]
draw.text(((cx0 + cx1) / 2, 765), "Fresh scale-12 child ridge", font=LABEL, fill=INK, anchor="mm")
draw.text(
    ((cx0 + cx1) / 2, 815),
    f"{adult['representative_child_A']:.6f} + {adult['representative_child_B']:.6f}",
    font=font(29, True),
    fill=GOLD,
    anchor="mm",
)
draw.text(
    ((cx0 + cx1) / 2, 858),
    f"= {adult['representative_adult_sum']:.6f}  |  A/B = {adult['representative_child_A'] / adult['representative_child_B']:.6f}",
    font=SUBTITLE,
    fill=INK,
    anchor="mm",
)

phase = TARGET["metrics"]["phase_transfer"]
max_difference = max(abs(a - b) for a, b in zip(prime, composite))
footer = (
    f"Fresh phase transfer: r={phase['target_template_correlation']:.6f}, RMSE={phase['target_template_rmse']:.6f}  |  "
    f"max prime-composite sector difference={max_difference:.6f}  |  independent validator: PASS"
)
draw.text((70, 1005), footer, font=SMALL, fill=INK)
image.save(OUTPUT)
print(f"wrote {OUTPUT}")

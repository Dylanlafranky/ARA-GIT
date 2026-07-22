"""Render the audited PN33 result as a standalone four-panel PNG."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "PN33_SEEDED_HEXAGON_FILL_RESULTS_VALIDATED.json"
BOOTSTRAP = HERE / "PN33_SEEDED_HEXAGON_FILL_BOOTSTRAP_RATIOS_CORRECTED.npy"
OUTPUT = HERE / "PN33_SEEDED_HEXAGON_FILL_FIGURE.png"

W, H = 1800, 1280
MARGIN = 86
GAP = 62
PANEL_W = (W - 2 * MARGIN - GAP) // 2
PANEL_H = 410

NAVY = "#13233a"
BLUE = "#2b6cb0"
PALE_BLUE = "#dbeafe"
GOLD = "#c58a1b"
ORANGE = "#dd6b20"
RED = "#b8322a"
GREEN = "#2f855a"
GRAY = "#627083"
LIGHT = "#d9e0e8"
PANEL = "#f7f9fc"
WHITE = "#ffffff"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    path = Path("C:/Windows/Fonts") / name
    return ImageFont.truetype(str(path), size=size)


F_TITLE = font(42, True)
F_SUB = font(21)
F_PANEL = font(25, True)
F_LABEL = font(18)
F_SMALL = font(15)
F_NOTE = font(17)


def text(draw: ImageDraw.ImageDraw, xy: tuple[float, float], value: str, fill=NAVY, f=F_LABEL, anchor="la") -> None:
    draw.text(xy, value, fill=fill, font=f, anchor=anchor)


def panel(draw: ImageDraw.ImageDraw, x: int, y: int, title: str, subtitle: str) -> tuple[int, int, int, int]:
    draw.rounded_rectangle((x, y, x + PANEL_W, y + PANEL_H), 22, fill=PANEL, outline=LIGHT, width=2)
    text(draw, (x + 26, y + 24), title, f=F_PANEL)
    text(draw, (x + 26, y + 61), subtitle, fill=GRAY, f=F_SMALL)
    return x + 76, y + 105, x + PANEL_W - 30, y + PANEL_H - 58


def axes(draw: ImageDraw.ImageDraw, box, x_ticks, y_ticks, x_fmt=str, y_fmt=str):
    x0, y0, x1, y1 = box
    draw.line((x0, y1, x1, y1), fill=GRAY, width=2)
    draw.line((x0, y0, x0, y1), fill=GRAY, width=2)
    for value, position in y_ticks:
        yp = y1 - position * (y1 - y0)
        draw.line((x0, yp, x1, yp), fill=LIGHT, width=1)
        text(draw, (x0 - 11, yp), y_fmt(value), fill=GRAY, f=F_SMALL, anchor="ra")
    for value, position in x_ticks:
        xp = x0 + position * (x1 - x0)
        text(draw, (xp, y1 + 14), x_fmt(value), fill=GRAY, f=F_SMALL, anchor="ma")


def scale(value, lo, hi, out_lo, out_hi):
    return out_lo + (value - lo) / (hi - lo) * (out_hi - out_lo)


def draw_polyline(draw, points, fill, width=4):
    draw.line(points, fill=fill, width=width, joint="curve")


def main() -> None:
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    primary = next(item for item in data["baselines"] if item["baseline_name"] == "primary")
    ratios = np.load(BOOTSTRAP)

    image = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(image)
    text(draw, (MARGIN, 48), "PN33 - seeded fill and spacing growth", f=F_TITLE)
    text(
        draw,
        (MARGIN, 102),
        "Frozen before gap scoring | 5,894,554 primary gaps | exact prime enumeration to 102,474,157",
        fill=GRAY,
        f=F_SUB,
    )

    # Panel A: geometry coordinate and scale landmarks.
    box = panel(draw, MARGIN, 150, "A. Frozen fill coordinate", "Each baseline begins at x=0; first inverse-density doubling is x=2")
    axes(
        draw,
        box,
        [(0, 0), (0.5, 0.25), (1, 0.5), (1.5, 0.75), (2, 1)],
        [(0, 0), (0.5, 0.25), (1, 0.5), (1.5, 0.75), (2, 1)],
        x_fmt=lambda v: f"{v:g}",
        y_fmt=lambda v: f"{v:g}",
    )
    x0, y0, x1, y1 = box
    for y_value, color, label, dash in [(1.0, ORANGE, "ridge x=1", False), (2.0, RED, "completion x=2", False)]:
        yp = scale(y_value, 0, 2, y1, y0)
        draw.line((x0, yp, x1, yp), fill=color, width=3)
        text(draw, (x1 - 4, yp - 9), label, fill=color, f=F_SMALL, anchor="ra")
    phi_x = (1 + math.sqrt(5)) / 2
    yp = scale(phi_x, 0, 2, y1, y0)
    for xx in range(x0, x1, 18):
        draw.line((xx, yp, min(xx + 9, x1), yp), fill=GOLD, width=2)
    text(draw, (x1 - 4, yp - 9), "descriptive Phi landmark", fill=GOLD, f=F_SMALL, anchor="ra")
    colors = [BLUE, GOLD, GREEN]
    for item, color in zip(data["baselines"], colors):
        bx = math.log10(item["baseline_prime"])
        cx = math.log10(item["completion_prime"])
        samples = np.linspace(bx, cx, 160)
        yy = 2 * (samples - bx) / (cx - bx)
        points = [
            (scale(v, bx, cx, x0, x1), scale(u, 0, 2, y1, y0))
            for v, u in zip(samples, yy)
        ]
        draw_polyline(draw, points, color, width=4)
    text(draw, ((x0 + x1) / 2, y1 + 39), "normalized logarithmic progress within each generation", fill=GRAY, f=F_SMALL, anchor="ma")

    # Panel B: observed band medians and benchmark curves.
    box = panel(draw, MARGIN + PANEL_W + GAP, 150, "B. Prime-gap scale across fill", "Observed medians compared with no-fit ARA and established PNT curves")
    obs = np.asarray(primary["observed_normalized_band_medians"], dtype=float)
    ara = np.asarray(primary["ara_predicted_normalized"], dtype=float)
    pnt = np.asarray(primary["pnt_predicted_normalized"], dtype=float)
    xmax = 2.0
    ymax = max(obs.max(), ara.max(), pnt.max()) * 1.12
    axes(
        draw,
        box,
        [(0, 0), (0.5, .25), (1, .5), (1.5, .75), (2, 1)],
        [(1, 1 / ymax), (1.25, 1.25 / ymax), (1.5, 1.5 / ymax), (1.75, 1.75 / ymax), (2, 2 / ymax)],
        x_fmt=lambda v: f"{v:g}",
        y_fmt=lambda v: f"{v:g}x",
    )
    x0, y0, x1, y1 = box
    xx = np.asarray([row["median_x"] for row in primary["bands"]])
    def pts(series):
        return [(scale(a, 0, xmax, x0, x1), scale(b, 0, ymax, y1, y0)) for a, b in zip(xx, series)]
    draw_polyline(draw, pts(ara), GOLD, 4)
    draw_polyline(draw, pts(pnt), GREEN, 4)
    draw_polyline(draw, pts(obs), BLUE, 5)
    for xp, yp in pts(obs):
        draw.ellipse((xp - 7, yp - 7, xp + 7, yp + 7), fill=WHITE, outline=BLUE, width=4)
    text(draw, (x0 + 8, y0 + 10), "observed", fill=BLUE, f=F_SMALL)
    text(draw, (x0 + 118, y0 + 10), "ARA", fill=GOLD, f=F_SMALL)
    text(draw, (x0 + 188, y0 + 10), "PNT", fill=GREEN, f=F_SMALL)
    text(draw, ((x0 + x1) / 2, y1 + 39), "local fill coordinate x", fill=GRAY, f=F_SMALL, anchor="ma")

    # Panel C: eight raw band medians with counts.
    box = panel(draw, MARGIN, 150 + PANEL_H + GAP, "C. Raw gap medians", "Medians rise in steps; the endpoint estimate is 12 / 8 = 1.5")
    med = np.asarray([row["median_gap"] for row in primary["bands"]], dtype=float)
    counts = np.asarray([row["n"] for row in primary["bands"]], dtype=int)
    ymax = med.max() * 1.3
    axes(
        draw,
        box,
        [(i + 1, i / 7) for i in range(8)],
        [(0, 0), (4, 4 / ymax), (8, 8 / ymax), (12, 12 / ymax), (16, 16 / ymax)],
        x_fmt=lambda v: str(v),
        y_fmt=lambda v: str(v),
    )
    x0, y0, x1, y1 = box
    slot = (x1 - x0) / 8
    for i, (value, count) in enumerate(zip(med, counts)):
        left = x0 + i * slot + slot * .18
        right = x0 + (i + 1) * slot - slot * .18
        top = scale(value, 0, ymax, y1, y0)
        draw.rounded_rectangle((left, top, right, y1), 8, fill=PALE_BLUE, outline=BLUE, width=2)
        text(draw, ((left + right) / 2, top - 9), f"{value:g}", fill=BLUE, f=F_LABEL, anchor="ma")
        text(draw, ((left + right) / 2, y1 + 37), f"n={count:,}", fill=GRAY, f=font(12), anchor="ma")
    text(draw, ((x0 + x1) / 2, y1 + 62), "fill band (1 = x 0-.25; 8 = x 1.75-2)", fill=GRAY, f=F_SMALL, anchor="ma")

    # Panel D: corrected endpoint bootstrap.
    box = panel(draw, MARGIN + PANEL_W + GAP, 150 + PANEL_H + GAP, "D. Corrected moving-block bootstrap", "10,000 resamples of actual 64-gap blocks; target doubling is at ratio 2")
    hist, edges = np.histogram(ratios, bins=np.linspace(1.35, 2.35, 31))
    ymax = max(hist.max(), 1) * 1.12
    axes(
        draw,
        box,
        [(1.5, .15), (1.75, .40), (2, .65), (2.25, .90)],
        [(0, 0), (2500, 2500 / ymax), (5000, 5000 / ymax), (7500, 7500 / ymax)],
        x_fmt=lambda v: f"{v:g}",
        y_fmt=lambda v: f"{int(v):,}",
    )
    x0, y0, x1, y1 = box
    for count, left_v, right_v in zip(hist, edges[:-1], edges[1:]):
        left = scale(left_v, 1.35, 2.35, x0, x1)
        right = scale(right_v, 1.35, 2.35, x0, x1)
        top = scale(count, 0, ymax, y1, y0)
        draw.rectangle((left + 1, top, right - 1, y1), fill=PALE_BLUE, outline=BLUE)
    for value, color, label in [(1.0, GRAY, "flat 1"), (1.5, ORANGE, "point 1.5"), (2.0, RED, "target 2")]:
        if 1.35 <= value <= 2.35:
            xp = scale(value, 1.35, 2.35, x0, x1)
            draw.line((xp, y0, xp, y1), fill=color, width=4)
            text(draw, (xp + 7, y0 + 8), label, fill=color, f=F_SMALL)
    text(draw, ((x0 + x1) / 2, y1 + 39), "final-band / first-band median-gap ratio", fill=GRAY, f=F_SMALL, anchor="ma")

    # Outcome strip.
    strip_y = 1070
    draw.rounded_rectangle((MARGIN, strip_y, W - MARGIN, H - 54), 20, fill=NAVY)
    text(draw, (MARGIN + 26, strip_y + 24), "AUDITED OUTCOME", fill=WHITE, f=font(18, True))
    text(draw, (MARGIN + 26, strip_y + 60), "SUPPORTED spacing expression under the frozen rule", fill=WHITE, f=font(25, True))
    text(draw, (MARGIN + 26, strip_y + 99), "Strong ordered rise; doubling is boundary-compatible, not a point hit.", fill="#d8e5f4", f=F_NOTE)
    text(draw, (980, strip_y + 34), f"Spearman  {primary['spearman_band_median_gap']:.3f}", fill=WHITE, f=F_LABEL)
    text(draw, (980, strip_y + 67), f"ARA log-MAE  {primary['ara_log_mae']:.4f}", fill=GOLD, f=F_LABEL)
    text(draw, (980, strip_y + 100), f"PNT log-MAE  {primary['pnt_log_mae']:.4f}", fill="#86d39a", f=F_LABEL)
    text(draw, (1320, strip_y + 34), "95% CI  1.5-2.0", fill=WHITE, f=F_LABEL)
    text(draw, (1320, strip_y + 67), "ARA advantage  0.62%", fill=WHITE, f=F_LABEL)
    text(draw, (1320, strip_y + 100), "ARA-specific threshold  5%", fill="#ffb4ad", f=F_LABEL)

    image.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create a static QA preview for the T398 portable report."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
OUT = HERE / "T398_population_neutrino_wave_overlap"
OVERLAP = OUT / "T398_NATIVE_WAVE_OVERLAP.csv"
BINNED = OUT / "T398_T371_MEASURED_AND_FITTED.csv"
RESULTS = OUT / "T398_RESULTS.json"
OUTPUT = OUT / "T398_POPULATION_NEUTRINO_WAVE_OVERLAP_PREVIEW.png"

WIDTH, HEIGHT = 2400, 1800
BG = "#f7f8fa"
PANEL = "#ffffff"
INK = "#17202a"
MUTED = "#667085"
GRID = "#d9dee7"
BLUE = "#2f69a5"
GOLD = "#d99a22"
ORANGE = "#e06f2d"
OLIVE = "#728342"
MAGENTA = "#a6537a"


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)


F_TITLE = font("segoeuib.ttf", 54)
F_SUBTITLE = font("segoeui.ttf", 25)
F_PANEL = font("segoeuib.ttf", 29)
F_SMALL = font("segoeui.ttf", 20)
F_TICK = font("consola.ttf", 17)
F_LABEL = font("segoeui.ttf", 19)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def line_chart(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    subtitle: str,
    x_values: list[float],
    series: list[tuple[str, list[float], str]],
    xlabel: str,
    ylabel: str,
    y_range: tuple[float, float] | None = None,
    vertical_refs: list[tuple[float, str]] | None = None,
    horizontal_refs: list[tuple[float, str]] | None = None,
) -> None:
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=18, fill=PANEL, outline="#e4e7ec", width=2)
    draw.text((left + 28, top + 22), title, fill=INK, font=F_PANEL)
    draw.text((left + 28, top + 61), subtitle, fill=MUTED, font=F_SMALL)

    plot_left = left + 130
    plot_right = right - 30
    plot_top = top + 130
    plot_bottom = bottom - 95
    xmin, xmax = min(x_values), max(x_values)
    all_y = [value for _, values, _ in series for value in values]
    ymin, ymax = y_range if y_range else (min(all_y), max(all_y))
    if ymax <= ymin:
        ymax = ymin + 1.0
    pad = 0.02 * (ymax - ymin)
    if y_range is None:
        ymin -= pad
        ymax += pad

    def px(x: float) -> float:
        return plot_left + (x - xmin) / (xmax - xmin) * (plot_right - plot_left)

    def py(y: float) -> float:
        return plot_bottom - (y - ymin) / (ymax - ymin) * (plot_bottom - plot_top)

    label_box = draw.textbbox((0, 0), ylabel, font=F_LABEL)
    label_width = label_box[2] - label_box[0]
    label_height = label_box[3] - label_box[1]
    rotated = Image.new("RGBA", (label_width + 14, label_height + 14), (0, 0, 0, 0))
    rotated_draw = ImageDraw.Draw(rotated)
    rotated_draw.text((7, 7), ylabel, fill=INK, font=F_LABEL)
    rotated = rotated.rotate(90, expand=True)
    label_x = left + 28
    label_y = int((plot_top + plot_bottom - rotated.height) / 2)
    draw._image.paste(rotated, (label_x, label_y), rotated)

    for i in range(6):
        value = ymin + i * (ymax - ymin) / 5
        y = py(value)
        draw.line((plot_left, y, plot_right, y), fill=GRID, width=1)
        label = f"{value:.2f}"
        draw.text((plot_left - 78, y - 10), label, fill=MUTED, font=F_TICK)
    for i in range(7):
        value = xmin + i * (xmax - xmin) / 6
        x = px(value)
        draw.line((x, plot_top, x, plot_bottom), fill="#eef0f4", width=1)
        draw.text((x - 21, plot_bottom + 10), f"{value:.1f}", fill=MUTED, font=F_TICK)

    draw.line((plot_left, plot_top, plot_left, plot_bottom), fill=INK, width=2)
    draw.line((plot_left, plot_bottom, plot_right, plot_bottom), fill=INK, width=2)

    for value, label in horizontal_refs or []:
        if ymin <= value <= ymax:
            y = py(value)
            for x in range(int(plot_left), int(plot_right), 16):
                draw.line((x, y, min(x + 8, plot_right), y), fill="#7a8391", width=2)
            draw.text((plot_right - 150, y - 25), label, fill="#596170", font=F_SMALL)

    for value, label in vertical_refs or []:
        if xmin <= value <= xmax:
            x = px(value)
            for y in range(int(plot_top), int(plot_bottom), 16):
                draw.line((x, y, x, min(y + 8, plot_bottom)), fill="#3f4752", width=3)
            draw.text((x + 8, plot_top + 8), label, fill="#3f4752", font=F_SMALL)

    for label, values, color in series:
        points = [(px(x), py(y)) for x, y in zip(x_values, values)]
        draw.line(points, fill=color, width=4, joint="curve")

    legend_x = plot_left
    legend_y = top + 95
    for label, _, color in series:
        draw.line((legend_x, legend_y + 10, legend_x + 34, legend_y + 10), fill=color, width=5)
        draw.text((legend_x + 42, legend_y), label, fill=INK, font=F_SMALL)
        legend_x += 42 + int(draw.textlength(label, font=F_SMALL)) + 36

    draw.text(((plot_left + plot_right) / 2 - 80, bottom - 45), xlabel, fill=INK, font=F_LABEL)


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    handover = float(result["handover"]["reconstructed_native_equality_us"])
    overlap = read_csv(OVERLAP)[::5]
    binned = read_csv(BINNED)

    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.text((80, 45), "T398 — Population neutrino wave overlap", fill=INK, font=F_TITLE)
    draw.text(
        (82, 112),
        "Population release observed; individual neutrino birth remains unobserved",
        fill=MUTED,
        font=F_SUBTITLE,
    )

    margin = 70
    gap = 34
    top = 175
    panel_w = (WIDTH - 2 * margin - gap) // 2
    panel_h = 690
    boxes = [
        (margin, top, margin + panel_w, top + panel_h),
        (margin + panel_w + gap, top, WIDTH - margin, top + panel_h),
        (margin, top + panel_h + gap, margin + panel_w, HEIGHT - 70),
        (margin + panel_w + gap, top + panel_h + gap, WIDTH - margin, HEIGHT - 70),
    ]

    x = [float(row["time_us"]) for row in overlap]
    line_chart(
        draw,
        boxes[0],
        "Source, inferred muon population and release",
        "COHERENT 2022 CsI · normalized coordinates · dotted line = fitted equality",
        x,
        [
            ("Prompt νμ", [float(r["prompt_nu_mu_peak_normalized"]) for r in overlap], BLUE),
            ("Muon remaining (derived)", [float(r["inferred_muon_remaining_fraction"]) for r in overlap], GOLD),
            ("Delayed neutrinos", [float(r["delayed_total_release_peak_normalized"]) for r in overlap], ORANGE),
        ],
        "Time after pulse (μs)",
        "Normalized 0–1",
        y_range=(0.0, 1.05),
        vertical_refs=[(handover, f"{handover:.3f} μs")],
    )
    line_chart(
        draw,
        boxes[1],
        "Delayed neutrino child templates",
        "Flavor templates close exactly to the combined delayed branch",
        x,
        [
            ("νe", [float(r["nu_e_release_over_delayed_peak"]) for r in overlap], BLUE),
            ("anti-νμ", [float(r["anti_nu_mu_release_over_delayed_peak"]) for r in overlap], GOLD),
            ("Combined", [float(r["delayed_total_release_peak_normalized"]) for r in overlap], ORANGE),
        ],
        "Time after pulse (μs)",
        "Contribution / delayed peak",
        y_range=(0.0, 1.05),
        vertical_refs=[(handover, f"{handover:.3f} μs")],
    )
    line_chart(
        draw,
        boxes[2],
        "Cumulative ARA traversal",
        "Instantaneous branch equality occurs before the cumulative parent ridge",
        x,
        [("Prompt + delayed release", [float(r["cumulative_ara_0_to_2"]) for r in overlap], BLUE)],
        "Time after pulse (μs)",
        "ARA coordinate 0–2",
        y_range=(0.0, 2.05),
        vertical_refs=[(handover, f"{handover:.3f} μs")],
        horizontal_refs=[(0.5, "child half"), (1.0, "ridge"), (2.0, "closure")],
    )

    bx = [float(row["time_us"]) for row in binned]
    line_chart(
        draw,
        boxes[3],
        "Measured and fitted timing components",
        "COHERENT 2022 CsI · events per released 0.5 μs bin",
        bx,
        [
            ("Observed C − AC", [float(r["observed_excess_C_minus_AC"]) for r in binned], INK),
            ("Background", [float(r["fitted_background"]) for r in binned], OLIVE),
            ("Prompt νμ", [float(r["fitted_prompt_nu_mu"]) for r in binned], BLUE),
            ("Delayed neutrinos", [float(r["fitted_delayed_nu_e_plus_anti_nu_mu"]) for r in binned], ORANGE),
        ],
        "Recoil time (μs)",
        "Events / 0.5 μs",
        vertical_refs=[(handover, f"{handover:.3f} μs")],
        horizontal_refs=[(0.0, "zero")],
    )

    image.save(OUTPUT, format="PNG", optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()

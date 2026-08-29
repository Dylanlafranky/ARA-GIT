from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
OUT = HERE / "T395_information3_parent_child_lock"
RESULTS = json.loads((OUT / "T395_RESULTS.json").read_text(encoding="utf-8"))

INK = "#202124"
GRID = "#d9d9d4"
BLUE = "#376996"
ORANGE = "#e07a24"
GREY = "#a8afb7"
BG = "#f7f7f4"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size)


def read_csv(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: float(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def centered(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, fnt, fill=INK) -> None:
    box = draw.textbbox((0, 0), text, font=fnt)
    draw.text((xy[0] - (box[2] - box[0]) / 2, xy[1]), text, font=fnt, fill=fill)


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=14, fill="white", outline="#c7c9c5", width=2)
    draw.text((x0 + 28, y0 + 22), title, font=font(27, True), fill=INK)
    return x0 + 92, y0 + 85, x1 - 35, y1 - 85


def axes(draw: ImageDraw.ImageDraw, plot: tuple[int, int, int, int], x_ticks: list[float], y_ticks: list[float], x_max: float, y_max: float) -> None:
    x0, y0, x1, y1 = plot
    for value in y_ticks:
        py = y1 - value / y_max * (y1 - y0)
        draw.line((x0, py, x1, py), fill=GRID, width=1)
        draw.text((x0 - 68, py - 11), f"{value:g}", font=font(18), fill="#59636e")
    for value in x_ticks:
        px = x0 + value / x_max * (x1 - x0)
        draw.line((px, y0, px, y1), fill=GRID, width=1)
        centered(draw, (px, y1 + 8), f"{value:g}", font(18), "#59636e")
    draw.line((x0, y0, x0, y1), fill=INK, width=2)
    draw.line((x0, y1, x1, y1), fill=INK, width=2)


def main() -> None:
    sample = read_csv(OUT / "T395_HOLDOUT_SAMPLE.csv")
    curve = read_csv(OUT / "T395_PARENT_CHILD_CURVE.csv")
    models = RESULTS["holdout_models"]
    holdout_n = RESULTS["split"]["holdout"]
    gain = RESULTS["primary_information_gain_nats_per_event"]
    ci = RESULTS["primary_gain_ci95"]

    image = Image.new("RGB", (2400, 1650), BG)
    draw = ImageDraw.Draw(image, "RGBA")
    centered(draw, (1200, 34), "T395 — Information³ parent→child neutrino lock", font(43, True))
    centered(
        draw,
        (1200, 88),
        f"Frozen V-A truth crosswalk | holdout n={holdout_n:,} | information gain={gain:.4f} nats/event, 95% CI [{ci[0]:.4f}, {ci[1]:.4f}]",
        font(24),
        "#4b5563",
    )

    boxes = [
        (55, 150, 1180, 840),
        (1220, 150, 2345, 840),
        (55, 875, 1180, 1565),
        (1220, 875, 2345, 1565),
    ]

    # Panel 1: parent/child relationship.
    plot = panel(draw, boxes[0], "Parent and child cuts on untouched holdout events")
    axes(draw, plot, [0, 0.25, 0.5, 0.75, 1], [0, 0.5, 1, 1.5, 2], 1, 2)
    x0, y0, x1, y1 = plot
    for row in sample[::4]:
        px = x0 + row["parent_x_e"] * (x1 - x0)
        py = y1 - row["true_child_y_nu_e"] / 2 * (y1 - y0)
        draw.ellipse((px - 2, py - 2, px + 2, py + 2), fill=(55, 105, 150, 35))
    pts = []
    for row in curve:
        px = x0 + row["parent_x_e"] * (x1 - x0)
        py = y1 - row["predicted_child_y_nu_e"] / 2 * (y1 - y0)
        pts.append((px, py))
    draw.line(pts, fill=ORANGE, width=5)
    ridge_y = y1 - 0.5 * (y1 - y0)
    draw.line((x0, ridge_y, x1, ridge_y), fill=INK, width=2)
    centered(draw, ((x0 + x1) / 2, y1 + 39), "Parent ARA charged coordinate P = x_e (0–1)", font(21))
    draw.text((x0 + 14, y0 + 12), "Orange: calibration-only child reconstruction", font=font(19), fill=ORANGE)
    draw.text((x0 + 14, y0 + 39), "Black: child ridge = 1", font=font(19), fill=INK)

    # Panel 2: distribution NLL bars.
    plot = panel(draw, boxes[1], "Unseen child-distribution score")
    x0, y0, x1, y1 = plot
    names = ["conditional lock", "unconditional", "parent shuffled", "identity reversed", "phase space"]
    values = [
        models["conditional_information_lock"]["mean_nll"],
        models["unconditional_child"]["mean_nll"],
        models["parent_shuffled"]["mean_nll"],
        models["identity_reversed"]["mean_nll"],
        models["phase_space"]["mean_nll"],
    ]
    vmin, vmax = -0.10, 0.32
    zero_y = y1 - (0 - vmin) / (vmax - vmin) * (y1 - y0)
    for t in [-0.1, 0, 0.1, 0.2, 0.3]:
        py = y1 - (t - vmin) / (vmax - vmin) * (y1 - y0)
        draw.line((x0, py, x1, py), fill=GRID, width=1)
        draw.text((x0 - 68, py - 11), f"{t:.1f}", font=font(18), fill="#59636e")
    draw.line((x0, zero_y, x1, zero_y), fill=INK, width=2)
    slot = (x1 - x0) / len(names)
    for i, (name, value) in enumerate(zip(names, values)):
        cx = x0 + (i + 0.5) * slot
        py = y1 - (value - vmin) / (vmax - vmin) * (y1 - y0)
        top, bottom = min(py, zero_y), max(py, zero_y)
        draw.rectangle((cx - slot * 0.29, top, cx + slot * 0.29, bottom), fill=ORANGE if i == 0 else GREY, outline=INK, width=1)
        centered(draw, (cx, top - 29), f"{value:.3f}", font(18, True))
        centered(draw, (cx, y1 + 14), name, font(16))
    centered(draw, ((x0 + x1) / 2, y1 + 49), "Holdout mean negative log-likelihood (lower is better)", font(20))

    # Panel 3: true versus predicted.
    plot = panel(draw, boxes[2], "The lock is statistical, not event-deterministic")
    axes(draw, plot, [0, 0.5, 1, 1.5, 2], [0, 0.5, 1, 1.5, 2], 2, 2)
    x0, y0, x1, y1 = plot
    for row in sample[::4]:
        px = x0 + row["true_child_y_nu_e"] / 2 * (x1 - x0)
        py = y1 - row["predicted_child_y_nu_e"] / 2 * (y1 - y0)
        draw.ellipse((px - 2, py - 2, px + 2, py + 2), fill=(55, 105, 150, 35))
    draw.line((x0, y1, x1, y0), fill=INK, width=2)
    centered(draw, ((x0 + x1) / 2, y1 + 39), "True hidden child C", font(21))
    draw.text((x0 + 14, y0 + 12), "Diagonal: perfect individual reconstruction", font=font(19), fill=INK)

    # Panel 4: third-relation point error.
    plot = panel(draw, boxes[3], "Reconstructed third relation")
    x0, y0, x1, y1 = plot
    names = ["conditional lock", "unconditional", "symmetric C=1"]
    values = [
        models["conditional_information_lock"]["nu_e_absolute_mae"],
        models["unconditional_child"]["nu_e_absolute_mae"],
        models["symmetric_point"]["nu_e_absolute_mae"],
    ]
    vmax = 0.17
    for t in [0, 0.05, 0.10, 0.15]:
        py = y1 - t / vmax * (y1 - y0)
        draw.line((x0, py, x1, py), fill=GRID, width=1)
        draw.text((x0 - 68, py - 11), f"{t:.2f}", font=font(18), fill="#59636e")
    draw.line((x0, y1, x1, y1), fill=INK, width=2)
    slot = (x1 - x0) / len(names)
    for i, (name, value) in enumerate(zip(names, values)):
        cx = x0 + (i + 0.5) * slot
        py = y1 - value / vmax * (y1 - y0)
        draw.rectangle((cx - slot * 0.25, py, cx + slot * 0.25, y1), fill=ORANGE if i == 0 else GREY, outline=INK, width=1)
        centered(draw, (cx, py - 31), f"{value:.4f}", font(19, True))
        centered(draw, (cx, y1 + 14), name, font(18))
    centered(draw, ((x0 + x1) / 2, y1 + 49), "nu_e absolute-coordinate MAE (lower is better)", font(20))

    centered(
        draw,
        (1200, 1600),
        "Exact composition is forced by nested coordinates; predictive gain is the non-trivial result. Not direct neutrino observation or individual decay timing.",
        font(20),
        "#4b5563",
    )
    output = OUT / "T395_INFORMATION3_LOCK.png"
    image.save(output)
    print(output)


if __name__ == "__main__":
    main()

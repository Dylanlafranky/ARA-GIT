"""Render the PN1C target/prediction diagnostic from saved frozen outputs."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
ARCHIVE = HERE / "PN1C_TARGET_AND_PREDICTIONS.npz"
OUTPUT = HERE / "PN1C_DISTRIBUTION_DIAGNOSTIC.png"


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ("arialbd.ttf", "arial.ttf") if bold else ("arial.ttf", "calibri.ttf")
    for name in names:
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def sequential(value: float, maximum: float) -> tuple[int, int, int]:
    fraction = min(max(value / maximum, 0.0), 1.0) ** 0.45
    low = np.array([247, 249, 252], dtype=np.float64)
    high = np.array([26, 103, 153], dtype=np.float64)
    return tuple(np.rint(low + fraction * (high - low)).astype(int))


def diverging(value: float, maximum: float) -> tuple[int, int, int]:
    fraction = min(abs(value) / maximum, 1.0) ** 0.55
    neutral = np.array([248, 248, 246], dtype=np.float64)
    endpoint = (
        np.array([196, 71, 45], dtype=np.float64)
        if value > 0
        else np.array([42, 111, 151], dtype=np.float64)
    )
    return tuple(np.rint(neutral + fraction * (endpoint - neutral)).astype(int))


def main() -> None:
    with np.load(ARCHIVE) as archive:
        target = archive["target_counts"].astype(np.float64)
        target /= target.sum()
        gap_iid = archive["prediction_Gap_IID"]
        ara = archive["prediction_ARA_linear_6"]

    panels = [
        ("Held-out prime-23 target", target, "probability"),
        ("31-slot Gap-IID", gap_iid, "probability"),
        ("35-slot ARA-linear-6", ara, "probability"),
        ("ARA minus target", ara - target, "residual"),
    ]
    probability_max = float(max(target.max(), gap_iid.max(), ara.max()))
    residual_max = float(np.max(np.abs(ara - target)))
    image = Image.new("RGB", (1900, 720), "#ffffff")
    draw = ImageDraw.Draw(image)
    title_font, panel_font = font(36, True), font(24, True)
    body_font, small_font = font(20), font(17)
    ink, muted = "#202731", "#5b6675"
    draw.text((55, 30), "PN1C: what the fixed ARA grid discards", fill=ink, font=title_font)
    draw.text(
        (55, 80),
        "Common 24×24 ARA relation plane; target and predictions use one shared probability scale",
        fill=muted,
        font=body_font,
    )

    panel_width, cell = 430, 16
    for panel_index, (label, matrix, mode) in enumerate(panels):
        x0 = 70 + panel_index * 455
        y0 = 170
        draw.text((x0, 125), label, fill=ink, font=panel_font)
        for row in range(24):
            for column in range(24):
                value = float(matrix[row, column])
                color = (
                    sequential(value, probability_max)
                    if mode == "probability"
                    else diverging(value, residual_max)
                )
                x = x0 + column * cell
                y = y0 + (23 - row) * cell
                draw.rectangle((x, y, x + cell - 1, y + cell - 1), fill=color)
        draw.rectangle(
            (x0 - 1, y0 - 1, x0 + 24 * cell, y0 + 24 * cell),
            outline="#677383",
            width=2,
        )
        draw.text((x0 + 145, y0 + 400), "second relation bin", fill=muted, font=small_font)
        draw.text((x0 - 8, y0 + 384), "0", fill=muted, font=small_font, anchor="ra")
        draw.text((x0 - 8, y0 + 4), "23", fill=muted, font=small_font, anchor="ra")
        draw.text((x0, y0 + 384 + 7), "0", fill=muted, font=small_font)
        draw.text((x0 + 374, y0 + 384 + 7), "23", fill=muted, font=small_font)

    target_support = target > 0
    ara_support_mass = float(ara[target_support].sum())
    gap_support_mass = float(gap_iid[target_support].sum())
    draw.text(
        (70, 635),
        f"Mass assigned to cells that actually occur:  Gap-IID {gap_support_mass:.3f}   |   ARA-linear-6 {ara_support_mass:.3f}",
        fill=ink,
        font=body_font,
    )
    draw.text(
        (70, 673),
        "The ARA grid spreads each coarse cell uniformly. The gap model preserves much of the target's discrete support geometry.",
        fill=muted,
        font=body_font,
    )
    draw.text(
        (1450, 635),
        f"Probability max {probability_max:.4f}\nResidual |max| {residual_max:.4f}",
        fill=muted,
        font=small_font,
        spacing=7,
    )
    image.save(OUTPUT, format="PNG")


if __name__ == "__main__":
    main()

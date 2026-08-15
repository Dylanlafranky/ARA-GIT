#!/usr/bin/env python3
"""T392 frozen population spin-child / joint-neutral handover test."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTOCOL = HERE / "T392_SPIN_CHILD_NEUTRAL_HANDOVER_PROTOCOL_2026-08-15.md"
SOURCE_PDF = HERE / "source_cache" / "PmuXi_2006_PRD.pdf"
SOURCE_PAGE = ROOT / "tmp" / "pdfs" / "twist" / "page10_400.png"
OUT = HERE / "T392_spin_child_neutral_handover"
OUT.mkdir(exist_ok=True)

RESULTS = OUT / "T392_RESULTS.json"
POINTS = OUT / "T392_DIGITISED_POINTS.csv"
FIGURE = OUT / "T392_SPIN_CHILD_NEUTRAL_HANDOVER.png"
REPORT = OUT / "T392_SPIN_CHILD_NEUTRAL_HANDOVER_REPORT.html"

M_MU = 105.6583755
M_E = 0.51099895
E_MAX = 52.83
SEED = 392
N_BOOT = 20_000

# Frozen 400-DPI Figure 6 calibration.
X_LEFT = 502.0
X_RIGHT = 1633.0
P_LEFT = 17.0
P_RIGHT = 50.0
FIT_ZERO_Y = 1094.5
FIT_PIXELS_PER_UNIT = 427.0
RESIDUAL_ZERO_Y = 1726.0
RESIDUAL_PIXELS_PER_UNIT = 6400.0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def p_to_pixel(momentum: float | np.ndarray) -> float | np.ndarray:
    return X_LEFT + (np.asarray(momentum) - P_LEFT) * (X_RIGHT - X_LEFT) / (P_RIGHT - P_LEFT)


def energy_coordinate(momentum: float | np.ndarray) -> np.ndarray:
    momentum = np.asarray(momentum, dtype=float)
    return 2.0 * np.sqrt(momentum * momentum + M_E * M_E) / M_MU


def box_sum(mask: np.ndarray, width: int = 7) -> np.ndarray:
    before = width // 2
    after = width - before - 1
    padded = np.pad(mask.astype(np.int16), ((before, after), (before, after)))
    integral = np.pad(padded, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    return (
        integral[width:, width:]
        - integral[:-width, width:]
        - integral[width:, :-width]
        + integral[:-width, :-width]
    )


def digitise() -> dict[str, np.ndarray]:
    if not SOURCE_PAGE.exists():
        raise FileNotFoundError(
            f"Missing 400-DPI page render: {SOURCE_PAGE}. "
            "Render PDF page 10 with pdftoppm as specified in the protocol."
        )
    image = np.asarray(Image.open(SOURCE_PAGE).convert("RGB"), dtype=int)
    if image.shape[:2] != (4400, 3400):
        raise RuntimeError(f"Expected a 3400 x 4400 render, got {image.shape[1]} x {image.shape[0]}")

    blue = (
        (image[:, :, 2] > 140)
        & (image[:, :, 2] > image[:, :, 0] + 40)
        & (image[:, :, 2] > image[:, :, 1] + 20)
    )
    black = image.max(axis=2) < 100
    density = box_sum(blue)

    momentum = np.arange(17.25, 50.0, 0.5)
    residual = []
    residual_sigma = []
    residual_x_pixel = []
    residual_y_pixel = []
    fit_raw = []

    for p in momentum:
        x_expected = float(p_to_pixel(p))
        x_low, x_high = int(x_expected - 7), int(x_expected + 8)
        y_low, y_high = 1640, 1850
        local = density[y_low:y_high, x_low:x_high]
        dy, dx = np.unravel_index(np.argmax(local), local.shape)
        # The box-sum maximum denotes the upper-left corner of the 7-pixel square.
        x_center = x_low + int(dx) + 3
        y_center = y_low + int(dy) + 3
        residual_x_pixel.append(x_center)
        residual_y_pixel.append(y_center)
        residual.append((RESIDUAL_ZERO_Y - y_center) / RESIDUAL_PIXELS_PER_UNIT)

        error_x = int(round(x_expected))
        error_rows = np.where(blue[1550:1930, error_x - 2 : error_x + 3].any(axis=1))[0] + 1550
        local_error_rows = error_rows[(error_rows > y_center - 150) & (error_rows < y_center + 150)]
        if len(local_error_rows):
            sigma = (float(local_error_rows.max()) - float(local_error_rows.min())) / (
                2.0 * RESIDUAL_PIXELS_PER_UNIT
            )
        else:
            sigma = 0.003
        residual_sigma.append(max(sigma, 0.0008))

        # The leading Michel curve guides pixel identification only; scored values
        # come from the printed black curve and measured residuals.
        u = p / E_MAX
        guide = (u - 0.5) / (1.5 - u)
        expected_y = FIT_ZERO_Y - guide * FIT_PIXELS_PER_UNIT
        search_top = max(667, int(expected_y - 40))
        search_bottom = min(1502, int(expected_y + 41))
        curve_rows, _ = np.where(
            black[search_top:search_bottom, int(round(x_expected)) - 3 : int(round(x_expected)) + 4]
        )
        curve_rows = curve_rows + search_top
        if len(curve_rows):
            curve_y = int(curve_rows[np.argmin(np.abs(curve_rows - expected_y))])
            fit_raw.append((FIT_ZERO_Y - curve_y) / FIT_PIXELS_PER_UNIT)
        else:
            fit_raw.append(np.nan)

    momentum = np.asarray(momentum)
    residual = np.asarray(residual)
    residual_sigma = np.asarray(residual_sigma)
    fit_raw = np.asarray(fit_raw)

    trace_mask = (
        np.isfinite(fit_raw)
        & (np.abs(fit_raw) > 0.008)
        & (momentum >= 18.25)
        & (momentum <= 45.0)
    )
    fit_coefficients = np.polyfit(momentum[trace_mask], fit_raw[trace_mask], 3)
    fit_asymmetry = np.polyval(fit_coefficients, momentum)
    data_asymmetry = fit_asymmetry + residual
    x_e = energy_coordinate(momentum)

    return {
        "momentum": momentum,
        "x_e": x_e,
        "x_neutral": 2.0 - x_e,
        "fit_raw": fit_raw,
        "fit_asymmetry": fit_asymmetry,
        "residual": residual,
        "residual_sigma": residual_sigma,
        "data_asymmetry": data_asymmetry,
        "neutral_direction_asymmetry": -data_asymmetry,
        "residual_x_pixel": np.asarray(residual_x_pixel),
        "residual_y_pixel": np.asarray(residual_y_pixel),
        "fit_coefficients": fit_coefficients,
        "trace_mask": trace_mask,
    }


def local_root(momentum: np.ndarray, values: np.ndarray, sigma: np.ndarray) -> tuple[float, np.ndarray, list[float]]:
    mask = (momentum >= 21.0) & (momentum <= 32.0)
    fit_sigma = np.sqrt(sigma[mask] ** 2 + (2.0 / FIT_PIXELS_PER_UNIT) ** 2)
    weights = 1.0 / np.maximum(fit_sigma, 1e-9) ** 2
    coefficients = np.polyfit(momentum[mask], values[mask], 2, w=np.sqrt(weights))
    roots = [
        float(root.real)
        for root in np.roots(coefficients)
        if abs(root.imag) < 1e-8 and 21.0 <= root.real <= 32.0
    ]
    if len(roots) != 1:
        raise RuntimeError(f"Expected one local physical root; found {roots}")
    return roots[0], coefficients, roots


def bootstrap(data: dict[str, np.ndarray], root_reference: float) -> np.ndarray:
    momentum = data["momentum"]
    values = data["data_asymmetry"]
    sigma = data["residual_sigma"]
    mask = (momentum >= 21.0) & (momentum <= 32.0)
    fit_sigma = np.sqrt(sigma[mask] ** 2 + (2.0 / FIT_PIXELS_PER_UNIT) ** 2)
    weights = 1.0 / np.maximum(fit_sigma, 1e-9) ** 2
    rng = np.random.default_rng(SEED)
    samples = []
    for _ in range(N_BOOT):
        sampled = values[mask] + rng.normal(0.0, fit_sigma)
        coefficients = np.polyfit(momentum[mask], sampled, 2, w=np.sqrt(weights))
        roots = [
            float(root.real)
            for root in np.roots(coefficients)
            if abs(root.imag) < 1e-8 and 21.0 <= root.real <= 32.0
        ]
        if roots:
            samples.append(min(roots, key=lambda value: abs(value - root_reference)))
    if len(samples) < 0.99 * N_BOOT:
        raise RuntimeError(f"Only {len(samples)} of {N_BOOT} bootstrap roots were physical")
    return np.asarray(samples)


def write_points(data: dict[str, np.ndarray]) -> None:
    columns = [
        "momentum_mev_c",
        "charged_energy_ara_x_e",
        "joint_neutral_energy_ara_x_n",
        "fit_asymmetry_digitised",
        "data_minus_fit_digitised",
        "residual_sigma_digitised",
        "reconstructed_data_asymmetry",
        "joint_neutral_direction_asymmetry",
        "residual_square_x_pixel",
        "residual_square_y_pixel",
    ]
    with POINTS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for index in range(len(data["momentum"])):
            writer.writerow({
                "momentum_mev_c": f"{data['momentum'][index]:.6f}",
                "charged_energy_ara_x_e": f"{data['x_e'][index]:.9f}",
                "joint_neutral_energy_ara_x_n": f"{data['x_neutral'][index]:.9f}",
                "fit_asymmetry_digitised": f"{data['fit_asymmetry'][index]:.9f}",
                "data_minus_fit_digitised": f"{data['residual'][index]:.9f}",
                "residual_sigma_digitised": f"{data['residual_sigma'][index]:.9f}",
                "reconstructed_data_asymmetry": f"{data['data_asymmetry'][index]:.9f}",
                "joint_neutral_direction_asymmetry": f"{data['neutral_direction_asymmetry'][index]:.9f}",
                "residual_square_x_pixel": int(data["residual_x_pixel"][index]),
                "residual_square_y_pixel": int(data["residual_y_pixel"][index]),
            })


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


def line_plot(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], x: np.ndarray, y: np.ndarray,
              xlim: tuple[float, float], ylim: tuple[float, float], colour: str, width: int = 4) -> None:
    left, top, right, bottom = box
    px = left + (x - xlim[0]) / (xlim[1] - xlim[0]) * (right - left)
    py = bottom - (y - ylim[0]) / (ylim[1] - ylim[0]) * (bottom - top)
    draw.line([(float(a), float(b)) for a, b in zip(px, py)], fill=colour, width=width, joint="curve")


def make_figure(data: dict[str, np.ndarray], result: dict) -> None:
    image = Image.new("RGB", (1700, 1180), "#f5f7fb")
    draw = ImageDraw.Draw(image)
    navy, blue, orange, green, grey, red = "#15243b", "#2f6fb3", "#d78b1f", "#318b62", "#6a7483", "#c64b48"
    draw.text((70, 42), "T392 - spin anti-phase child at the muon decay handover", font=font(38, True), fill=navy)
    draw.text((70, 92), "Published TWIST population spectrum | exact labels retained | event-level timing not available", font=font(21), fill=grey)

    # Panel 1: measured spin asymmetry across the charged energy allocation.
    box1 = (95, 185, 800, 565)
    draw.rectangle(box1, fill="white", outline="#cbd2dc", width=2)
    draw.text((95, 145), "A. Charged daughter direction reverses near x_e = 0.5", font=font(24, True), fill=navy)
    xlim, ylim = (0.30, 0.96), (-0.22, 0.88)
    for value in [0.4, 0.5, 0.6, 0.8]:
        px = box1[0] + (value - xlim[0]) / (xlim[1] - xlim[0]) * (box1[2] - box1[0])
        draw.line((px, box1[1], px, box1[3]), fill="#e1e5eb", width=1)
        draw.text((px - 18, box1[3] + 9), f"{value:.1f}", font=font(17), fill=grey)
    for value in [-0.2, 0.0, 0.4, 0.8]:
        py = box1[3] - (value - ylim[0]) / (ylim[1] - ylim[0]) * (box1[3] - box1[1])
        draw.line((box1[0], py, box1[2], py), fill="#e1e5eb", width=1)
        draw.text((box1[0] - 62, py - 10), f"{value:+.1f}", font=font(17), fill=grey)
    band_left = box1[0] + (0.45 - xlim[0]) / (xlim[1] - xlim[0]) * (box1[2] - box1[0])
    band_right = box1[0] + (0.55 - xlim[0]) / (xlim[1] - xlim[0]) * (box1[2] - box1[0])
    draw.rectangle((band_left, box1[1], band_right, box1[3]), fill="#edf7f2")
    line_plot(draw, box1, data["x_e"], data["data_asymmetry"], xlim, ylim, blue, 4)
    for xe, value, sigma in zip(data["x_e"], data["data_asymmetry"], data["residual_sigma"]):
        px = box1[0] + (xe - xlim[0]) / (xlim[1] - xlim[0]) * (box1[2] - box1[0])
        py = box1[3] - (value - ylim[0]) / (ylim[1] - ylim[0]) * (box1[3] - box1[1])
        sy = sigma / (ylim[1] - ylim[0]) * (box1[3] - box1[1])
        draw.line((px, py - sy, px, py + sy), fill="#92afd1", width=1)
        draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill=blue)
    root_x = result["handover"]["charged_energy_ara_x_e"]
    root_px = box1[0] + (root_x - xlim[0]) / (xlim[1] - xlim[0]) * (box1[2] - box1[0])
    zero_py = box1[3] - (0.0 - ylim[0]) / (ylim[1] - ylim[0]) * (box1[3] - box1[1])
    draw.line((root_px, box1[1], root_px, box1[3]), fill=red, width=3)
    draw.ellipse((root_px - 7, zero_py - 7, root_px + 7, zero_py + 7), fill=red)
    draw.text((box1[0] + 15, box1[1] + 15), f"Measured root x_e = {root_x:.4f}", font=font(20, True), fill=red)
    draw.text((box1[0] + 15, box1[1] + 45), f"95% bootstrap CI {result['handover']['x_e_ci95'][0]:.4f} to {result['handover']['x_e_ci95'][1]:.4f}", font=font(17), fill=grey)
    draw.text((box1[0] + 220, box1[3] + 42), "charged energy ARA x_e = 2 E_e / m_mu", font=font(19, True), fill=navy)

    # Panel 2: TE-ARA allocation.
    box2 = (895, 185, 1610, 565)
    draw.rectangle(box2, fill="white", outline="#cbd2dc", width=2)
    draw.text((895, 145), "B. Same event as a TE-ARA energy allocation", font=font(24, True), fill=navy)
    yline = 370
    xstart, xend = 960, 1545
    draw.line((xstart, yline, xend, yline), fill=navy, width=5)
    for value in [0, 0.5, 1.0, 1.5, 2.0]:
        px = xstart + value / 2.0 * (xend - xstart)
        draw.line((px, yline - 16, px, yline + 16), fill=navy, width=3)
        draw.text((px - 16, yline + 24), f"{value:g}", font=font(18, value in (0, 1.0, 2.0)), fill=navy)
    xe_px = xstart + root_x / 2.0 * (xend - xstart)
    xn = result["handover"]["joint_neutral_energy_ara_x_n"]
    xn_px = xstart + xn / 2.0 * (xend - xstart)
    draw.ellipse((xe_px - 13, yline - 13, xe_px + 13, yline + 13), fill=orange)
    draw.ellipse((xn_px - 13, yline - 13, xn_px + 13, yline + 13), fill=green)
    draw.text((930, 230), "charged daughter", font=font(21, True), fill=orange)
    draw.text((930, 262), f"x_e = {root_x:.4f}", font=font(23, True), fill=orange)
    draw.text((1290, 230), "joint neutrino pair", font=font(21, True), fill=green)
    draw.text((1320, 262), f"x_N = {xn:.4f}", font=font(23, True), fill=green)
    draw.line((xe_px, yline - 25, xn_px, yline - 25), fill="#9aa4b2", width=2)
    draw.text((1060, yline - 65), f"x_e + x_N = {root_x + xn:.4f} (forced closure)", font=font(19), fill=grey)
    draw.text((940, 475), "The sign reversal is measured.", font=font(21, True), fill=navy)
    draw.text((940, 510), "The complementary sum to 2 is bookkeeping, not a second finding.", font=font(17), fill=grey)

    # Panel 3: digitised residuals.
    box3 = (95, 720, 800, 1055)
    draw.rectangle(box3, fill="white", outline="#cbd2dc", width=2)
    draw.text((95, 680), "C. Published data-minus-fit residuals used in reconstruction", font=font(23, True), fill=navy)
    rxlim, rylim = (0.32, 0.96), (-0.025, 0.025)
    for value in [-0.02, 0.0, 0.02]:
        py = box3[3] - (value - rylim[0]) / (rylim[1] - rylim[0]) * (box3[3] - box3[1])
        draw.line((box3[0], py, box3[2], py), fill="#dfe4eb", width=2 if value == 0 else 1)
        draw.text((box3[0] - 70, py - 9), f"{value:+.2f}", font=font(16), fill=grey)
    for xe, value, sigma in zip(data["x_e"], data["residual"], data["residual_sigma"]):
        px = box3[0] + (xe - rxlim[0]) / (rxlim[1] - rxlim[0]) * (box3[2] - box3[0])
        py = box3[3] - (value - rylim[0]) / (rylim[1] - rylim[0]) * (box3[3] - box3[1])
        sy = sigma / (rylim[1] - rylim[0]) * (box3[3] - box3[1])
        draw.line((px, py - sy, px, py + sy), fill="#88a9d0", width=1)
        draw.rectangle((px - 3, py - 3, px + 3, py + 3), fill=blue)
    draw.text((270, box3[3] + 23), "charged energy ARA x_e", font=font(19, True), fill=navy)
    draw.text((box3[0] + 15, box3[1] + 15), f"residual RMS = {result['quality']['residual_rms']:.5f}", font=font(18, True), fill=navy)

    # Panel 4: gates and limits.
    box4 = (895, 720, 1610, 1055)
    draw.rectangle(box4, fill="white", outline="#cbd2dc", width=2)
    draw.text((895, 680), "D. Frozen gates and claim ceiling", font=font(23, True), fill=navy)
    y = 750
    for label, gate in result["gates"].items():
        colour = green if gate["pass"] else red
        draw.ellipse((925, y + 3, 943, y + 21), fill=colour)
        draw.text((958, y), label.replace("_", " "), font=font(19, True), fill=navy)
        draw.text((1210, y), "PASS" if gate["pass"] else "FAIL", font=font(19, True), fill=colour)
        y += 45
    draw.line((925, 985, 1575, 985), fill="#dfe4eb", width=2)
    draw.text((925, 1000), "Population child allocation: supported only if every gate passes.", font=font(17, True), fill=navy)
    draw.text((925, 1028), "Individual neutrino timing: not measured by this source.", font=font(17), fill=red)

    image.save(FIGURE)


def make_report(result: dict) -> None:
    gate_rows = "".join(
        f"<tr><td>{html.escape(name.replace('_', ' '))}</td><td class={'pass' if gate['pass'] else 'fail'}>"
        f"{'PASS' if gate['pass'] else 'FAIL'}</td><td>{html.escape(gate['detail'])}</td></tr>"
        for name, gate in result["gates"].items()
    )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>T392 spin-child neutral handover</title>
<style>
body{{font-family:Arial,sans-serif;background:#f5f7fb;color:#15243b;margin:0}}main{{max-width:1250px;margin:30px auto;padding:30px;background:white}}
h1,h2{{color:#15243b}}img{{width:100%;border:1px solid #cbd2dc}}table{{border-collapse:collapse;width:100%;margin:18px 0}}th,td{{border:1px solid #d8dee7;padding:10px;text-align:left}}th{{background:#edf2f8}}.pass{{color:#23724f;font-weight:bold}}.fail{{color:#b33b38;font-weight:bold}}.boundary{{background:#fff5e8;padding:16px;border-left:5px solid #d78b1f}}
</style></head><body><main>
<h1>T392 - spin anti-phase child at the muon decay handover</h1>
<p><strong>Registered verdict:</strong> {result['verdict']}</p>
<p>The published TWIST positron spin asymmetry reverses at <strong>x_e = {result['handover']['charged_energy_ara_x_e']:.6f}</strong>
(95% bootstrap CI {result['handover']['x_e_ci95'][0]:.6f} to {result['handover']['x_e_ci95'][1]:.6f}).
The complementary joint-neutral energy coordinate is <strong>x_N = {result['handover']['joint_neutral_energy_ara_x_n']:.6f}</strong>.</p>
<img src="{FIGURE.name}" alt="T392 labelled result figure">
<h2>Exact identity read</h2>
<table><tr><th>Object</th><th>ARA role</th><th>Measured or derived?</th></tr>
<tr><td>Parent muon spin anti-phase</td><td>population parent</td><td>measured separately in T391</td></tr>
<tr><td>Positron asymmetry A(p)</td><td>visible downstream child</td><td>published TWIST fit plus measured residual</td></tr>
<tr><td>Joint two-neutrino packet</td><td>neutral downstream sibling</td><td>combined complement only</td></tr>
<tr><td>x_e + x_N = 2</td><td>TE-ARA closure</td><td>forced by energy bookkeeping</td></tr></table>
<h2>Frozen gates</h2><table><tr><th>Gate</th><th>Result</th><th>Exact read</th></tr>{gate_rows}</table>
<div class="boundary"><strong>Claim boundary.</strong> This is a population energy-allocation handover beneath the spin anti-phase. It does not predict the instant an individual muon decays and does not resolve the two neutrino siblings separately.</div>
<h2>Source and reproduction</h2>
<p>TWIST Collaboration, Figure 6 in <em>Measurement of P_mu xi in Polarized Muon Decay</em>, Phys. Rev. D 74, 072007 (2006). Official source: <a href="https://twist.triumf.ca/~e614/pubs/PmuXi_2006_PRD.pdf">TRIUMF PDF</a>.</p>
<p>Protocol SHA-256: <code>{result['provenance']['protocol_sha256']}</code><br>Source PDF SHA-256: <code>{result['provenance']['source_pdf_sha256']}</code></p>
</main></body></html>"""
    REPORT.write_text(document, encoding="utf-8")


def main() -> None:
    data = digitise()
    root_p, local_coefficients, physical_roots = local_root(
        data["momentum"], data["data_asymmetry"], data["residual_sigma"]
    )
    root_samples_p = bootstrap(data, root_p)
    root_samples_x = energy_coordinate(root_samples_p)
    root_x = float(energy_coordinate(root_p))
    root_xn = 2.0 - root_x
    ci = np.quantile(root_samples_x, [0.025, 0.5, 0.975])
    low_median = float(np.median(data["data_asymmetry"][data["x_e"] <= 0.40]))
    high_median = float(np.median(data["data_asymmetry"][data["x_e"] >= 0.70]))
    band_fraction = float(np.mean((root_samples_x >= 0.45) & (root_samples_x <= 0.55)))

    gates = {
        "directional_reversal": {
            "pass": bool(low_median < 0.0 < high_median),
            "detail": f"low median {low_median:+.6f}; high median {high_median:+.6f}",
        },
        "unique_handover": {
            "pass": len(physical_roots) == 1 and 0.35 <= root_x <= 0.65,
            "detail": f"one local root at x_e={root_x:.6f}",
        },
        "coarse_pair_band": {
            "pass": bool(0.45 <= root_x <= 0.55),
            "detail": f"x_e={root_x:.6f}; x_N={root_xn:.6f}",
        },
        "bootstrap_stability": {
            "pass": bool(band_fraction >= 0.95),
            "detail": f"{100.0 * band_fraction:.3f}% of roots inside [0.45,0.55]",
        },
        "wrong_landmark_control": {
            "pass": bool(abs(root_x - 0.5) < min(abs(root_x - 0.25), abs(root_x - 0.75))),
            "detail": f"distance to 0.5={abs(root_x-0.5):.6f}; to 0.25={abs(root_x-0.25):.6f}; to 0.75={abs(root_x-0.75):.6f}",
        },
    }
    passed = all(gate["pass"] for gate in gates.values())
    result = {
        "test": "T392 spin-child to joint-neutral handover",
        "status": "SUPPORTED_AT_POPULATION_CROSSWALK_CEILING" if passed else "NOT_SUPPORTED",
        "verdict": "SUPPORTED - POPULATION HANDOVER CHILD" if passed else "NOT SUPPORTED",
        "source_capability": "published population momentum-asymmetry spectrum; figure digitisation",
        "handover": {
            "momentum_mev_c": root_p,
            "charged_energy_ara_x_e": root_x,
            "joint_neutral_energy_ara_x_n": root_xn,
            "x_e_ci95": [float(ci[0]), float(ci[2])],
            "x_e_bootstrap_median": float(ci[1]),
            "bootstrap_roots": int(len(root_samples_x)),
        },
        "quality": {
            "digitised_points": int(len(data["momentum"])),
            "traced_fit_pixels_used": int(data["trace_mask"].sum()),
            "residual_rms": float(np.sqrt(np.mean(data["residual"] ** 2))),
            "low_allocation_median_asymmetry": low_median,
            "high_allocation_median_asymmetry": high_median,
            "bootstrap_band_fraction": band_fraction,
        },
        "gates": gates,
        "model": {
            "local_quadratic_coefficients": [float(value) for value in local_coefficients],
            "fit_trace_cubic_coefficients": [float(value) for value in data["fit_coefficients"]],
        },
        "boundaries": [
            "The directional reversal is empirical; x_e + x_N = 2 is conservation bookkeeping.",
            "The neutral packet combines both neutrinos and does not identify either sibling separately.",
            "The source is aggregate and cannot predict one muon's decay time.",
            "T392 does not revive the rejected 7.5-turn trigger claim.",
        ],
        "provenance": {
            "protocol_sha256": sha256(PROTOCOL),
            "source_pdf_sha256": sha256(SOURCE_PDF),
            "source_page_sha256": sha256(SOURCE_PAGE),
            "source_url": "https://twist.triumf.ca/~e614/pubs/PmuXi_2006_PRD.pdf",
            "source_figure": "Figure 6, PDF page 10 (one-indexed), 400-DPI render",
            "seed": SEED,
            "bootstrap_replicates": N_BOOT,
        },
    }

    write_points(data)
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    make_figure(data, result)
    make_report(result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

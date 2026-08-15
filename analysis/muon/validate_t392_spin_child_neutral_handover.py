#!/usr/bin/env python3
"""Independent validation for T392 digitisation, calculations, and artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
OUT = HERE / "T392_spin_child_neutral_handover"
PROTOCOL = HERE / "T392_SPIN_CHILD_NEUTRAL_HANDOVER_PROTOCOL_2026-08-15.md"
SOURCE_PDF = HERE / "source_cache" / "PmuXi_2006_PRD.pdf"
SOURCE_PAGE = HERE.parents[1] / "tmp" / "pdfs" / "twist" / "page10_400.png"
RESULTS = OUT / "T392_RESULTS.json"
POINTS = OUT / "T392_DIGITISED_POINTS.csv"
FIGURE = OUT / "T392_SPIN_CHILD_NEUTRAL_HANDOVER.png"
REPORT = OUT / "T392_SPIN_CHILD_NEUTRAL_HANDOVER_REPORT.html"

M_MU = 105.6583755
M_E = 0.51099895


def sha256(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest.upper()


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"PASS: {label}")


def main() -> None:
    for path in [PROTOCOL, SOURCE_PDF, SOURCE_PAGE, RESULTS, POINTS, FIGURE, REPORT]:
        check(path.exists() and path.stat().st_size > 0, f"artifact exists: {path.name}")

    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    with POINTS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    check(len(rows) == 66, "66 published half-MeV digitisation bins")

    momentum = np.asarray([float(row["momentum_mev_c"]) for row in rows])
    x_e = np.asarray([float(row["charged_energy_ara_x_e"]) for row in rows])
    x_n = np.asarray([float(row["joint_neutral_energy_ara_x_n"]) for row in rows])
    fit = np.asarray([float(row["fit_asymmetry_digitised"]) for row in rows])
    residual = np.asarray([float(row["data_minus_fit_digitised"]) for row in rows])
    sigma = np.asarray([float(row["residual_sigma_digitised"]) for row in rows])
    data = np.asarray([float(row["reconstructed_data_asymmetry"]) for row in rows])
    neutral = np.asarray([float(row["joint_neutral_direction_asymmetry"]) for row in rows])
    x_pixels = np.asarray([int(row["residual_square_x_pixel"]) for row in rows])

    check(np.allclose(np.diff(momentum), 0.5), "momentum bins are monotone half-MeV centres")
    check(np.all(np.diff(x_e) > 0), "charged energy coordinate is monotone")
    check(np.max(np.abs(x_e + x_n - 2.0)) < 2e-9, "TE-ARA complement closes to 2")
    check(np.max(np.abs(data - (fit + residual))) < 2e-9, "data reconstruction equals fit plus residual")
    check(np.max(np.abs(neutral + data)) < 2e-9, "joint-neutral direction is the stated momentum complement")
    check(np.all(sigma > 0), "all digitised uncertainty scales are positive")

    expected_x_e = 2.0 * np.sqrt(momentum * momentum + M_E * M_E) / M_MU
    check(np.max(np.abs(expected_x_e - x_e)) < 1e-8, "energy-to-ARA conversion is reproduced")
    expected_pixels = 502.0 + (momentum - 17.0) * (1633.0 - 502.0) / 33.0
    check(np.max(np.abs(x_pixels - expected_pixels)) <= 4.5, "digitised square centres follow frozen x calibration")

    local = (momentum >= 21.0) & (momentum <= 32.0)
    fit_sigma = np.sqrt(sigma[local] ** 2 + (2.0 / 427.0) ** 2)
    coefficients = np.polyfit(momentum[local], data[local], 2, w=np.sqrt(1.0 / fit_sigma**2))
    roots = [
        float(root.real)
        for root in np.roots(coefficients)
        if abs(root.imag) < 1e-8 and 21.0 <= root.real <= 32.0
    ]
    check(len(roots) == 1, "independent local fit has one physical root")
    root_p = roots[0]
    root_x = float(2.0 * np.sqrt(root_p * root_p + M_E * M_E) / M_MU)
    reported = float(result["handover"]["charged_energy_ara_x_e"])
    check(abs(root_x - reported) < 1e-8, "reported handover coordinate reproduces from CSV")
    check(0.45 <= root_x <= 0.55, "handover is inside frozen coarse-pair band")
    # The CSV is intentionally serialized to nine decimal places, so an
    # independently reconstructed root cannot be compared at float64 epsilon.
    check(abs((2.0 - root_x) - result["handover"]["joint_neutral_energy_ara_x_n"]) < 1e-8,
          "reported joint-neutral coordinate is complementary")

    low = float(np.median(data[x_e <= 0.40]))
    high = float(np.median(data[x_e >= 0.70]))
    check(low < 0.0 < high, "low/high allocations have opposite directional signs")
    check(all(gate["pass"] for gate in result["gates"].values()), "all frozen result gates pass")
    check(result["status"] == "SUPPORTED_AT_POPULATION_CROSSWALK_CEILING", "claim ceiling is population crosswalk")

    check(result["provenance"]["protocol_sha256"] == sha256(PROTOCOL), "protocol hash matches")
    check(result["provenance"]["source_pdf_sha256"] == sha256(SOURCE_PDF), "source PDF hash matches")
    check(result["provenance"]["source_page_sha256"] == sha256(SOURCE_PAGE), "rendered source-page hash matches")

    source_image = Image.open(SOURCE_PAGE)
    output_image = Image.open(FIGURE)
    check(source_image.size == (3400, 4400), "source page is frozen 400-DPI geometry")
    check(output_image.size == (1700, 1180), "result figure has expected dimensions")
    report = REPORT.read_text(encoding="utf-8")
    check(
        FIGURE.name in report and "does not predict the instant an individual muon decays" in report,
        "report embeds figure and claim boundary",
    )
    print("T392 validation complete: all checks passed.")


if __name__ == "__main__":
    main()

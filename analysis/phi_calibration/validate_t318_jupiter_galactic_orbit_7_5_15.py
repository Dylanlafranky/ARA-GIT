#!/usr/bin/env python3
"""Independent validator for T318. Does not import the analysis module."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
SUN_PATH = HERE / "data" / "t317" / "sun_vectors.csv"
JUPITER_PATH = HERE / "data" / "t317" / "jupiter_vectors.csv"
PROTOCOL_PATH = (
    HERE / "T318_JUPITER_GALACTIC_ORBIT_7_5_15_PROTOCOL_v1_REGISTERED.md"
)
RESULTS_PATH = HERE / "T318_JUPITER_GALACTIC_ORBIT_7_5_15_RESULTS.json"
CYCLE_PATH = HERE / "T318_JUPITER_GALACTIC_ORBIT_7_5_15_CYCLES.csv"
SERIES_PATH = HERE / "T318_JUPITER_GALACTIC_ORBIT_7_5_15_SERIES.csv"
FIGURE_PATH = HERE / "T318_JUPITER_GALACTIC_ORBIT_7_5_15.png"
REPORT_PATH = HERE / "T318_JUPITER_GALACTIC_ORBIT_7_5_15_REPORT_2026-07-31.md"
VALIDATION_PATH = HERE / "T318_JUPITER_GALACTIC_ORBIT_7_5_15_VALIDATION.json"

SPLIT_YEAR = 1950
TARGET_ALPHA = 7.5
TARGET_BETA = 15.0
TOL_ALPHA = 0.25
TOL_BETA = 0.5
FRAMES = {
    "rounded_t309": (
        230.27777777777777,
        np.array(
            [0.4941094278755837, -0.11099073341911324, 0.8622858750898978]
        ),
    ),
    "modern_measured": (
        248.93142028923324,
        np.array(
            [0.46129050783760756, -0.1551427763070162, 0.8735798683226815]
        ),
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def close(a: float, b: float, tolerance: float = 1e-9) -> bool:
    return bool(abs(float(a) - float(b)) <= tolerance)


def angle_to_axis(vectors: np.ndarray, axis: np.ndarray) -> np.ndarray:
    cosine = (vectors @ axis) / np.linalg.norm(vectors, axis=1)
    return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))


def angle_between(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    cosine = np.sum(a * b, axis=1) / (
        np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
    )
    return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))


def interpolate(jd: np.ndarray, values: np.ndarray, at: np.ndarray) -> np.ndarray:
    return np.column_stack(
        [np.interp(at, jd, values[:, column]) for column in range(3)]
    )


def main() -> None:
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    sun = pd.read_csv(SUN_PATH)
    jupiter = pd.read_csv(JUPITER_PATH)
    checks: list[dict[str, object]] = []

    def record(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    record("test_id", results.get("test_id") == "T318", results.get("test_id"))
    record("source_rows", len(sun) == len(jupiter) == 14683, len(sun))
    aligned = np.array_equal(
        sun["jd_tdb"].to_numpy(), jupiter["jd_tdb"].to_numpy()
    )
    record("timestamps_aligned", aligned, aligned)
    record(
        "sun_sha256",
        sha256(SUN_PATH) == results["source"]["sun_sha256"],
        sha256(SUN_PATH),
    )
    record(
        "jupiter_sha256",
        sha256(JUPITER_PATH) == results["source"]["jupiter_sha256"],
        sha256(JUPITER_PATH),
    )
    record(
        "protocol_sha256",
        sha256(PROTOCOL_PATH) == results["source"]["protocol_sha256"],
        sha256(PROTOCOL_PATH),
    )

    jd = sun["jd_tdb"].to_numpy(dtype=float)
    calendar = sun["calendar_tdb"].astype(str)
    year = calendar.str.extract(r"(\d{4})-")[0].astype(int).to_numpy()
    position = (
        jupiter[["x_km", "y_km", "z_km"]].to_numpy(dtype=float)
        - sun[["x_km", "y_km", "z_km"]].to_numpy(dtype=float)
    )
    velocity = (
        jupiter[["vx_km_s", "vy_km_s", "vz_km_s"]].to_numpy(dtype=float)
        - sun[["vx_km_s", "vy_km_s", "vz_km_s"]].to_numpy(dtype=float)
    )
    calibration = year < SPLIT_YEAR
    theta = np.unwrap(np.arctan2(position[calibration, 1], position[calibration, 0]))
    cal_jd = jd[calibration]
    slope = float(np.polyfit(cal_jd - cal_jd[0], theta, 1)[0])
    period = float(2.0 * np.pi / abs(slope))
    record(
        "period_recomputed",
        close(period, results["period_days_from_calibration"], 1e-8),
        period,
    )

    split_jd = float(jd[np.where(year >= SPLIT_YEAR)[0][0]])
    opposite_jd = jd + period / 2.0
    eligible = (jd >= split_jd) & (opposite_jd <= jd[-1])
    jd1 = jd[eligible]
    v1 = velocity[eligible]
    v2 = interpolate(jd, velocity, opposite_jd[eligible])
    expected_series = pd.read_csv(SERIES_PATH)
    expected_cycles = pd.read_csv(CYCLE_PATH)

    for frame_key, (parent_speed, parent_unit) in FRAMES.items():
        parent = parent_speed * parent_unit
        total1 = parent + v1
        total2 = parent + v2
        alpha = angle_to_axis(total1, parent_unit)
        alpha2 = angle_to_axis(total2, parent_unit)
        beta = angle_between(total1, total2)
        ara = 2.0 * alpha / (alpha + alpha2)
        saved = results["frames"][frame_key]
        record(
            f"{frame_key}_n_pairs",
            len(alpha) == saved["n_pairs"],
            len(alpha),
        )
        for metric, values in (
            ("alpha", alpha),
            ("beta", beta),
            ("ara", ara),
        ):
            saved_key = {"alpha": "alpha_deg", "beta": "beta_deg", "ara": "ara_a"}[
                metric
            ]
            record(
                f"{frame_key}_{metric}_median",
                close(float(np.median(values)), saved[saved_key]["median"]),
                float(np.median(values)),
            )
            record(
                f"{frame_key}_{metric}_maximum",
                close(float(np.max(values)), saved[saved_key]["max"]),
                float(np.max(values)),
            )

        central = bool(
            abs(float(np.median(alpha)) - TARGET_ALPHA) <= TOL_ALPHA
            and abs(float(np.median(beta)) - TARGET_BETA) <= TOL_BETA
        )
        record(
            f"{frame_key}_central_gate",
            central == saved["central_pass"],
            central,
        )

        series = expected_series.loc[expected_series["frame"] == frame_key]
        record(
            f"{frame_key}_series_rows",
            len(series) == len(alpha),
            len(series),
        )
        record(
            f"{frame_key}_series_alpha",
            bool(np.allclose(series["alpha_deg"].to_numpy(), alpha, atol=1e-10)),
            float(np.max(np.abs(series["alpha_deg"].to_numpy() - alpha))),
        )
        cycles = expected_cycles.loc[expected_cycles["frame"] == frame_key]
        cycle_passes = int(
            (cycles["alpha_max_pass"] & cycles["beta_max_pass"]).sum()
        )
        envelope = bool(not central and len(cycles) >= 12 and cycle_passes >= 9)
        record(
            f"{frame_key}_envelope_gate",
            envelope == saved["envelope_pass"],
            {
                "complete_cycles": int(len(cycles)),
                "passing_cycles": cycle_passes,
                "envelope": envelope,
            },
        )

    modern = results["frames"]["modern_measured"]
    modern_support = modern["central_pass"] or modern["envelope_pass"]
    rounded = results["frames"]["rounded_t309"]
    rounded_support = rounded["central_pass"] or rounded["envelope_pass"]
    expected_verdict = (
        "ROBUST 7.5/15 SUPPORT"
        if modern_support
        else (
            "FRAME-SENSITIVE SUPPORT; NOT ROBUST"
            if rounded_support
            else "7.5/15 NOT SUPPORTED"
        )
    )
    record(
        "robust_verdict",
        results["robust_verdict"] == expected_verdict,
        expected_verdict,
    )

    with Image.open(FIGURE_PATH) as image:
        record(
            "figure_dimensions",
            image.size == (1800, 1120),
            {"width": image.width, "height": image.height},
        )
    report_text = REPORT_PATH.read_text(encoding="utf-8")
    record(
        "report_contains_verdict",
        results["robust_verdict"] in report_text,
        results["robust_verdict"],
    )

    validation = {
        "test_id": "T318",
        "validator": "independent; does not import analysis module",
        "checks_passed": int(sum(item["passed"] for item in checks)),
        "checks_total": int(len(checks)),
        "all_passed": bool(all(item["passed"] for item in checks)),
        "checks": checks,
    }
    VALIDATION_PATH.write_text(
        json.dumps(validation, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(validation, indent=2))
    if not validation["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Independent row-level validator for T309."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "data" / "t308" / "earth_sun_vectors.csv"
RESULTS = HERE / "T309_GALACTIC_ORBIT_7_5_15_RESULTS.json"
YEARLY = HERE / "T309_GALACTIC_ORBIT_7_5_15_YEARLY.csv"
SENSITIVITY = HERE / "T309_GALACTIC_ORBIT_7_5_15_SENSITIVITY.csv"
FIGURE = HERE / "T309_GALACTIC_ORBIT_7_5_15.png"
REPORT = HERE / "T309_GALACTIC_ORBIT_7_5_15_REPORT_2026-07-31.md"
OUTPUT = HERE / "T309_GALACTIC_ORBIT_7_5_15_VALIDATION.json"

SPLIT_JD = 2456293.5
PARENT_SPEED = 829000.0 / 3600.0
ALPHA_TARGET = 7.5
BETA_TARGET = 15.0
ALPHA_TOL = 0.25
BETA_TOL = 0.5
R0_KPC = 8.178
MU_L_MAS_YR = 6.411
MU_B_MAS_YR = 0.219
U_KM_S = 11.1
K = 4.74047


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def close(actual: float, expected: float, tol: float = 1e-9) -> bool:
    return bool(abs(actual - expected) <= tol)


def main() -> None:
    recorded = json.loads(RESULTS.read_text(encoding="utf-8"))
    frame = pd.read_csv(SOURCE)
    years = frame["calendar_tdb"].astype(str).str.extract(r"(\d{4})-")[0].astype(int)
    jd = frame["jd_tdb"].to_numpy()
    position = frame[["x_km", "y_km", "z_km"]].to_numpy()
    velocity = frame[["vx_km_s", "vy_km_s", "vz_km_s"]].to_numpy()

    calibration = jd < SPLIT_JD
    phase = np.unwrap(np.arctan2(position[calibration, 1], position[calibration, 0]))
    slope = float(np.polyfit(jd[calibration] - jd[calibration][0], phase, 1)[0])
    period = 2.0 * np.pi / abs(slope)

    eq_to_gal = np.array(
        [
            [-0.0548755604162154, -0.8734370902348850, -0.4838350155487132],
            [+0.4941094278755837, -0.4448296299600112, +0.7469822444972189],
            [-0.8676661490190047, -0.1980763734312015, +0.4559837761750669],
        ]
    )
    gal_tangent = np.array([0.0, 1.0, 0.0])
    equatorial = eq_to_gal.T @ gal_tangent
    eps = math.radians(23.439291111)
    rotation = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, math.cos(eps), math.sin(eps)],
            [0.0, -math.sin(eps), math.cos(eps)],
        ]
    )
    unit = rotation @ equatorial
    unit /= np.linalg.norm(unit)

    query = jd + period / 2.0
    eligible = (jd >= SPLIT_JD) & (query <= jd[-1])
    v1 = velocity[eligible]
    v2 = np.column_stack(
        [np.interp(query[eligible], jd, velocity[:, i]) for i in range(3)]
    )
    parent = PARENT_SPEED * unit
    w1 = v1 + parent
    w2 = v2 + parent

    def axis_angle(v: np.ndarray) -> np.ndarray:
        cosine = (v @ unit) / np.linalg.norm(v, axis=1)
        return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

    alpha1 = axis_angle(w1)
    alpha2 = axis_angle(w2)
    cosine_beta = np.sum(w1 * w2, axis=1) / (
        np.linalg.norm(w1, axis=1) * np.linalg.norm(w2, axis=1)
    )
    beta = np.degrees(np.arccos(np.clip(cosine_beta, -1.0, 1.0)))
    closure = beta - (alpha1 + alpha2)
    ara_a = 2.0 * alpha1 / (alpha1 + alpha2)

    eval_years = years[eligible].to_numpy()
    complete = []
    for year in sorted(set(eval_years.tolist())):
        mask = eval_years == year
        if int(np.sum(mask)) < 350:
            continue
        alpha_max = float(np.max(alpha1[mask]))
        beta_max = float(np.max(beta[mask]))
        complete.append(
            (
                int(year),
                alpha_max,
                beta_max,
                abs(alpha_max - ALPHA_TARGET) <= ALPHA_TOL
                and abs(beta_max - BETA_TARGET) <= BETA_TOL,
            )
        )
    pass_count = sum(item[3] for item in complete)
    central = (
        abs(float(np.median(alpha1)) - ALPHA_TARGET) <= ALPHA_TOL
        and abs(float(np.median(beta)) - BETA_TARGET) <= BETA_TOL
    )
    envelope = (not central) and len(complete) >= 12 and pass_count >= 9
    verdict = (
        "CENTRAL CADENCE SUPPORTED"
        if central
        else "STABLE CREST/ENVELOPE RECURRENCE"
        if envelope
        else "NOT SUPPORTED"
    )

    measured_components = np.array(
        [U_KM_S, K * MU_L_MAS_YR * R0_KPC, K * MU_B_MAS_YR * R0_KPC]
    )
    measured_speed = float(np.linalg.norm(measured_components))
    measured_direction_gal = measured_components / measured_speed
    measured_unit = rotation @ (eq_to_gal.T @ measured_direction_gal)
    measured_unit /= np.linalg.norm(measured_unit)
    measured_parent = measured_speed * measured_unit
    measured_w1 = v1 + measured_parent
    measured_w2 = v2 + measured_parent

    def measured_axis_angle(v: np.ndarray) -> np.ndarray:
        cosine = (v @ measured_unit) / np.linalg.norm(v, axis=1)
        return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

    measured_alpha = measured_axis_angle(measured_w1)
    measured_beta_cos = np.sum(measured_w1 * measured_w2, axis=1) / (
        np.linalg.norm(measured_w1, axis=1)
        * np.linalg.norm(measured_w2, axis=1)
    )
    measured_beta = np.degrees(
        np.arccos(np.clip(measured_beta_cos, -1.0, 1.0))
    )
    measured_record = recorded["modern_measured_galactocentric_control"]

    primary = recorded["primary_galactic_frame"]
    checks = {
        "source_hash": digest(SOURCE) == recorded["source"]["sha256"],
        "source_rows": len(frame) == recorded["source"]["rows"],
        "period": close(period, recorded["period_days_from_calibration"]),
        "parent_unit": bool(
            np.allclose(unit, recorded["primary_parent"]["unit_ecliptic_j2000"], atol=1e-12)
        ),
        "pair_count": len(alpha1) == primary["n_pairs"],
        "alpha_median": close(float(np.median(alpha1)), primary["alpha_deg"]["median"]),
        "alpha_max": close(float(np.max(alpha1)), primary["alpha_deg"]["max"]),
        "beta_median": close(float(np.median(beta)), primary["beta_deg"]["median"]),
        "beta_max": close(float(np.max(beta)), primary["beta_deg"]["max"]),
        "closure_median": close(
            float(np.median(closure)), primary["closure_residual_deg"]["median"]
        ),
        "ara_median": close(float(np.median(ara_a)), primary["ara_a"]["median"]),
        "year_count": len(complete) == primary["complete_year_count"],
        "envelope_pass_count": pass_count == primary["envelope_year_pass_count"],
        "verdict": verdict == primary["verdict"],
        "year_csv_rows": len(pd.read_csv(YEARLY)) == len(complete),
        "sensitivity_rows": len(pd.read_csv(SENSITIVITY)) == 9,
        "measured_speed": close(
            measured_speed, recorded["modern_measured_parent"]["speed_km_s"]
        ),
        "measured_alpha_max": close(
            float(np.max(measured_alpha)), measured_record["alpha_deg"]["max"]
        ),
        "measured_beta_max": close(
            float(np.max(measured_beta)), measured_record["beta_deg"]["max"]
        ),
        "measured_control_fails": measured_record["verdict"] == "NOT SUPPORTED",
        "figure_exists": FIGURE.exists() and FIGURE.stat().st_size > 50000,
        "report_exists": REPORT.exists() and REPORT.stat().st_size > 3000,
    }
    payload = {
        "test_id": "T309",
        "passed": bool(all(checks.values())),
        "checks_passed": int(sum(checks.values())),
        "checks_total": int(len(checks)),
        "checks": checks,
        "independent_recalculation": {
            "period_days": float(period),
            "alpha_median_deg": float(np.median(alpha1)),
            "alpha_max_deg": float(np.max(alpha1)),
            "beta_median_deg": float(np.median(beta)),
            "beta_max_deg": float(np.max(beta)),
            "complete_years": int(len(complete)),
            "envelope_pass_years": int(pass_count),
            "verdict": verdict,
            "measured_speed_km_s": measured_speed,
            "measured_alpha_max_deg": float(np.max(measured_alpha)),
            "measured_beta_max_deg": float(np.max(measured_beta)),
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

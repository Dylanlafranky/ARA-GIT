#!/usr/bin/env python3
"""Independent row-level validator for T317.

This file deliberately does not import the analysis script.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data" / "t317"
RESULTS_PATH = HERE / "T317_SOLAR_SYSTEM_BARYCENTRIC_ARA_RESULTS.json"
SERIES_PATH = HERE / "T317_SOLAR_SYSTEM_BARYCENTRIC_ARA_SERIES.csv"
COMPOSITION_PATH = HERE / "T317_SOLAR_SYSTEM_BARYCENTRIC_ARA_COMPOSITION.csv"
FIGURE_PATH = HERE / "T317_SOLAR_SYSTEM_BARYCENTRIC_ARA.png"
REPORT_PATH = HERE / "T317_SOLAR_SYSTEM_BARYCENTRIC_ARA_REPORT_2026-07-31.md"
OUTPUT_PATH = HERE / "T317_SOLAR_SYSTEM_BARYCENTRIC_ARA_VALIDATION.json"

GM = {
    "sun": 132_712_440_041.279419,
    "mercury": 22_031.868551,
    "venus": 324_858.592000,
    "emb": 398_600.435507 + 4_902.800118,
    "mars": 42_828.375816,
    "jupiter": 126_712_764.100000,
    "saturn": 37_940_584.841800,
    "uranus": 5_794_556.400000,
    "neptune": 6_836_527.100580,
    "pluto": 975.500000,
}
KEYS = list(GM)
PRIMARY = ["mercury", "venus", "emb", "mars", "jupiter", "saturn", "uranus", "neptune"]
EXTENDED = PRIMARY + ["pluto"]

GALACTIC_TO_ICRS = np.array(
    [
        [-0.0548755604, 0.4941094279, -0.8676661490],
        [-0.8734370902, -0.4448296300, -0.1980763734],
        [-0.4838350155, 0.7469822445, 0.4559837762],
    ],
    dtype=float,
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def arrays(frame: pd.DataFrame, velocity: bool) -> np.ndarray:
    if velocity:
        columns = ["vx_km_s", "vy_km_s", "vz_km_s"]
    else:
        columns = ["x_km", "y_km", "z_km"]
    return frame[columns].to_numpy(dtype=float)


def norms(value: np.ndarray) -> np.ndarray:
    return np.linalg.norm(value, axis=1)


def metrics(a: np.ndarray, b: np.ndarray) -> dict[str, np.ndarray]:
    na = norms(a)
    nb = norms(b)
    denominator = na + nb
    angle_denominator = na * nb
    cosine = np.divide(
        np.sum(a * (-b), axis=1),
        angle_denominator,
        out=np.full(len(a), np.nan),
        where=angle_denominator > 0,
    )
    return {
        "x_a": 2.0 * na / denominator,
        "x_b": 2.0 * nb / denominator,
        "opposition_deg": np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0))),
        "other": 2.0 * norms(a + b) / denominator,
    }


def galactic_parent() -> np.ndarray:
    k = 4.74047
    galactic = np.array(
        [11.1, k * 6.411 * 8.178, k * 0.219 * 8.178],
        dtype=float,
    )
    icrs = GALACTIC_TO_ICRS @ galactic
    epsilon = math.radians(23.439291111)
    rotation = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, math.cos(epsilon), math.sin(epsilon)],
            [0.0, -math.sin(epsilon), math.cos(epsilon)],
        ]
    )
    return rotation @ icrs


def strongest_period(vector: np.ndarray, step_days: float) -> float:
    centered = vector - np.mean(vector, axis=0, keepdims=True)
    transformed = np.fft.rfft(centered * np.hanning(len(centered))[:, None], axis=0)
    power = np.sum(np.abs(transformed) ** 2, axis=1)
    frequencies = np.fft.rfftfreq(len(centered), d=step_days)
    period = np.divide(
        1.0,
        frequencies * 365.25,
        out=np.full_like(frequencies, np.inf),
        where=frequencies > 0,
    )
    eligible = (period >= 1.5) & (period <= 100.0)
    return float(period[np.flatnonzero(eligible)[np.argmax(power[eligible])]])


def close(actual: float, expected: float, tolerance: float = 1e-12) -> bool:
    return math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance)


def main() -> None:
    recorded = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    frames: dict[str, pd.DataFrame] = {}
    reference_jd = None
    for key in KEYS:
        raw = DATA_DIR / f"{key}_horizons_raw.txt"
        parsed = DATA_DIR / f"{key}_vectors.csv"
        metadata = recorded["source"]["files"][key]
        frame = pd.read_csv(parsed)
        frames[key] = frame
        checks[f"{key}_raw_hash"] = sha256(raw) == metadata["raw_sha256"]
        checks[f"{key}_parsed_hash"] = sha256(parsed) == metadata["parsed_sha256"]
        checks[f"{key}_rows"] = len(frame) == metadata["rows"] == recorded["rows"]
        jd = frame["jd_tdb"].to_numpy(dtype=float)
        if reference_jd is None:
            reference_jd = jd
        else:
            checks[f"{key}_time_grid"] = len(jd) == len(reference_jd) and np.allclose(jd, reference_jd)

    assert reference_jd is not None
    step_days = float(np.median(np.diff(reference_jd)))
    checks["step_days"] = close(step_days, recorded["step_days"])

    positions = {key: arrays(frames[key], False) for key in KEYS}
    velocities = {key: arrays(frames[key], True) for key in KEYS}
    q = {key: GM[key] * positions[key] for key in KEYS}
    p = {key: GM[key] * velocities[key] for key in KEYS}
    q_b8 = np.sum([q[key] for key in PRIMARY], axis=0)
    p_b8 = np.sum([p[key] for key in PRIMARY], axis=0)
    q_b9 = q_b8 + q["pluto"]
    p_b9 = p_b8 + p["pluto"]
    q8 = metrics(q["sun"], q_b8)
    p8 = metrics(p["sun"], p_b8)
    q9 = metrics(q["sun"], q_b9)
    p9 = metrics(p["sun"], p_b9)

    metric_sets = {
        "p8": (p8, recorded["primary_eight"]["velocity"]),
        "q8": (q8, recorded["primary_eight"]["position"]),
        "p9": (p9, recorded["extended_nine"]["velocity"]),
        "q9": (q9, recorded["extended_nine"]["position"]),
    }
    for label, (calculated, target) in metric_sets.items():
        for field in ["x_a", "x_b", "opposition_deg", "other"]:
            checks[f"{label}_{field}_median"] = close(
                float(np.median(calculated[field])),
                float(target[field]["median"]),
            )

    recalculated_gates = [
        0.995 <= float(np.median(p9["x_a"])) <= 1.005,
        0.995 <= float(np.median(p9["x_b"])) <= 1.005,
        float(np.median(p9["opposition_deg"])) < 0.05,
        float(np.median(p9["other"])) < 0.005,
        float(np.median(q9["opposition_deg"])) < 0.05,
        float(np.median(q9["other"])) < 0.005,
    ]
    checks["gate_count"] = sum(recalculated_gates) == recorded["gates"]["passed"] == 6

    combined_norm = norms(p_b9)
    unit_b = p_b9 / combined_norm[:, None]
    jupiter_projection = np.sum(p["jupiter"] * unit_b, axis=1) / combined_norm
    all_projection = np.column_stack(
        [np.sum(p[key] * unit_b, axis=1) / combined_norm for key in EXTENDED]
    )
    top = np.argmax(np.abs(all_projection), axis=1)
    jupiter_top_frequency = float(np.mean(top == EXTENDED.index("jupiter")))
    checks["jupiter_projection_median"] = close(
        float(np.median(jupiter_projection)),
        recorded["planetary_composition"]["jupiter"]["projection_share"]["median"],
    )
    checks["jupiter_top_frequency"] = close(
        jupiter_top_frequency,
        recorded["planetary_composition"]["jupiter"]["top_projection_frequency"],
    )

    peak = strongest_period(p["sun"], step_days)
    checks["strongest_period"] = close(
        peak,
        recorded["cadence"]["sun_peaks"][0]["period_years"],
    )

    total_gm = GM["sun"] + sum(GM[key] for key in EXTENDED)
    parent = galactic_parent()
    completed = parent[None, :] + (p["sun"] + p_b9) / total_gm
    deviation_m_s = norms(completed - parent[None, :]) * 1000.0
    checks["external_deviation_median"] = close(
        float(np.median(deviation_m_s)),
        recorded["external_parent"]["completed_whole_deviation_m_s"]["median"],
    )

    series = pd.read_csv(SERIES_PATH)
    composition = pd.read_csv(COMPOSITION_PATH)
    checks["series_rows"] = len(series) == recorded["rows"]
    checks["composition_years"] = composition["year"].nunique() == 201
    checks["composition_rows"] = len(composition) == 201 * 9
    checks["figure_exists"] = FIGURE_PATH.exists() and FIGURE_PATH.stat().st_size > 50_000
    checks["report_exists"] = REPORT_PATH.exists() and REPORT_PATH.stat().st_size > 3_000

    result = {
        "test_id": "T317",
        "passed": all(checks.values()),
        "checks_passed": sum(int(value) for value in checks.values()),
        "checks_total": len(checks),
        "checks": checks,
        "independent_recalculation": {
            "rows": len(reference_jd),
            "step_days": step_days,
            "velocity_x_a_median": float(np.median(p9["x_a"])),
            "velocity_x_b_median": float(np.median(p9["x_b"])),
            "velocity_opposition_median_deg": float(np.median(p9["opposition_deg"])),
            "velocity_other_median": float(np.median(p9["other"])),
            "position_opposition_median_deg": float(np.median(q9["opposition_deg"])),
            "position_other_median": float(np.median(q9["other"])),
            "jupiter_top_projection_frequency": jupiter_top_frequency,
            "strongest_period_years": peak,
            "external_deviation_median_m_s": float(np.median(deviation_m_s)),
        },
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

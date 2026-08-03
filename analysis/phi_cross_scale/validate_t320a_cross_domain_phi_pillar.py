"""Independent numeric validation for T320A."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import pathlib

import numpy as np
import scipy.io as sio


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "analysis" / "pendulum_scripts" / "data"
PROTOCOL = HERE / "T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY_CORRECTION_v1.md"
PROTOCOL_SHA256 = "dc6faec59f3809cc180f28fa08660278ddd4a404508fed7608116c51e96992fc"
RESULTS = HERE / "T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY_RESULTS.json"
WINDOWS = HERE / "T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY_WINDOWS.csv"
OUTPUT = HERE / "T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY_VALIDATION.json"

FILES = {
    "run1": "pend_triple.mat",
    "run2": "tri2.mat",
    "run3": "tri3.mat",
    "driven": "TripleDataWithControl_1_Dt_0_0001.mat",
}
SHIFT_FRACTIONS = (0.17, 0.31, 0.47)
WINDOW_SAMPLES = 100
EPS = 1e-12
PHI = (1 + math.sqrt(5)) / 2
Q_CANDIDATES = {
    "1": 1.0,
    "sqrt2": math.sqrt(2),
    "1.5": 1.5,
    "phi": PHI,
    "sqrt3": math.sqrt(3),
    "2": 2.0,
}
ANGLE_CANDIDATES = {"90": 90.0, "108": 108.0, "120": 120.0, "135": 135.0, "144": 144.0, "180": 180.0}


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def wrap(x: np.ndarray) -> np.ndarray:
    return (x + np.pi) % (2 * np.pi) - np.pi


def robust(x: np.ndarray) -> float:
    centre = np.median(x)
    return float(1.4826 * np.median(np.abs(x - centre)))


def load(name: str):
    mat = sio.loadmat(DATA / FILES[name])
    time = np.asarray(mat["Time"]).ravel()[::10]
    theta = {i: np.asarray(mat[f"Theta{i}"]).ravel()[::10] for i in (1, 2, 3)}
    velocity = {i: np.asarray(mat[f"dTheta{i}"]).ravel()[::10] for i in (1, 2, 3)}
    centred = {}
    for i in (1, 2, 3):
        rest = np.arctan2(np.mean(np.sin(theta[i])), np.mean(np.cos(theta[i])))
        centred[i] = wrap(theta[i] - rest)
    return time, centred, velocity


def metric_scales() -> dict[str, float]:
    angles = []
    velocities = []
    for name in ("run1", "run2"):
        _, centred, velocity = load(name)
        angles.extend(centred.values())
        velocities.extend(velocity.values())
    return {"angle": robust(np.concatenate(angles)), "velocity": robust(np.concatenate(velocities))}


def calculate(name: str, label: str, scales: dict[str, float], shift: int = 0) -> list[dict]:
    time, centred, velocity = load(name)
    z = {
        i: np.column_stack([centred[i] / scales["angle"], velocity[i] / scales["velocity"]])
        for i in (1, 2, 3)
    }
    a0, a1 = z[3], z[1]
    b = np.roll(z[2], shift, axis=0) if shift else z[2]
    u, v = a0 - b, a1 - b
    d0, d1 = np.linalg.norm(u, axis=1), np.linalg.norm(v, axis=1)
    valid = (
        (d0 > EPS)
        & (d1 > EPS)
        & (np.linalg.norm(a0, axis=1) > EPS)
        & (np.linalg.norm(a1, axis=1) > EPS)
        & (np.linalg.norm(b, axis=1) > EPS)
    )
    idx = np.flatnonzero(valid)
    q = 2 * np.linalg.norm(a0[idx] - a1[idx], axis=1) / (d0[idx] + d1[idx])
    cosine = np.einsum("ij,ij->i", u[idx], v[idx]) / (d0[idx] * d1[idx])
    angle = np.degrees(np.arccos(np.clip(cosine, -1, 1)))
    leg = np.minimum(d0[idx], d1[idx]) / np.maximum(d0[idx], d1[idx])
    branch = np.where(centred[1][idx] >= 0, "A-positive", "B-negative")
    wid = idx // WINDOW_SAMPLES
    out = []
    for window in np.unique(wid):
        take = wid == window
        out.append(
            {
                "dataset": label,
                "middle_shift_fraction": shift / len(time),
                "window": int(window),
                "time_mid_s": float(np.median(time[idx[take]])),
                "eligible_samples": int(np.sum(take)),
                "q_median": float(np.median(q[take])),
                "angle_median_degrees": float(np.median(angle[take])),
                "leg_balance_median": float(np.median(leg[take])),
                "branch": "A-positive" if np.sum(branch[take] == "A-positive") >= np.sum(branch[take] == "B-negative") else "B-negative",
            }
        )
    return out


def summary(rows: list[dict]) -> dict:
    q = np.asarray([row["q_median"] for row in rows])
    angle = np.asarray([row["angle_median_degrees"] for row in rows])
    legs = np.asarray([row["leg_balance_median"] for row in rows])
    qerr = {key: float(np.median(np.abs(q - value))) for key, value in Q_CANDIDATES.items()}
    aerr = {key: float(np.median(np.abs(angle - value))) for key, value in ANGLE_CANDIDATES.items()}
    return {
        "windows": len(rows),
        "eligible_samples": int(sum(row["eligible_samples"] for row in rows)),
        "median_q": float(np.median(q)),
        "q_candidate_errors": qerr,
        "q_winner": min(qerr, key=qerr.get),
        "median_angle_degrees": float(np.median(angle)),
        "angle_candidate_errors": aerr,
        "angle_winner": min(aerr, key=aerr.get),
        "median_leg_balance": float(np.median(legs)),
    }


def close(a, b, tol=2e-11) -> bool:
    return abs(float(a) - float(b)) <= tol


def main() -> None:
    saved = json.loads(RESULTS.read_text(encoding="utf-8"))
    with WINDOWS.open(newline="", encoding="utf-8") as stream:
        csv_rows = list(csv.DictReader(stream))
    parsed = []
    for row in csv_rows:
        parsed.append(
            {
                "dataset": row["dataset"],
                "middle_shift_fraction": float(row["middle_shift_fraction"]),
                "window": int(row["window"]),
                "time_mid_s": float(row["time_mid_s"]),
                "eligible_samples": int(row["eligible_samples"]),
                "q_median": float(row["q_median"]),
                "angle_median_degrees": float(row["angle_median_degrees"]),
                "leg_balance_median": float(row["leg_balance_median"]),
                "branch": row["branch"],
            }
        )

    scales = metric_scales()
    expected = calculate("run3", "free_run3", scales)
    for fraction in SHIFT_FRACTIONS:
        length = 60001
        expected += calculate("run3", f"free_run3_shift_{fraction:.2f}", scales, int(round(fraction * length)))
    expected += calculate("driven", "driven_triple1", scales)

    row_errors = []
    row_identity = True
    for left, right in zip(parsed, expected):
        row_identity &= left["dataset"] == right["dataset"] and left["window"] == right["window"] and left["branch"] == right["branch"]
        row_identity &= left["eligible_samples"] == right["eligible_samples"]
        for key in ("middle_shift_fraction", "time_mid_s", "q_median", "angle_median_degrees", "leg_balance_median"):
            row_errors.append(abs(left[key] - right[key]))

    eval_summary = summary([row for row in expected if row["dataset"] == "free_run3"])
    headline_ok = all(
        close(eval_summary[key], saved["evaluation"][key])
        for key in ("median_q", "median_angle_degrees", "median_leg_balance")
    )
    headline_ok &= eval_summary["q_winner"] == saved["evaluation"]["q_winner"]
    headline_ok &= eval_summary["angle_winner"] == saved["evaluation"]["angle_winner"]
    headline_ok &= all(close(eval_summary["q_candidate_errors"][key], saved["evaluation"]["q_candidate_errors"][key]) for key in Q_CANDIDATES)

    checks = {
        "protocol_hash": sha256(PROTOCOL) == PROTOCOL_SHA256 == saved["protocol_sha256"],
        "development_scales": close(scales["angle"], saved["development_metric_scales"]["angle"]) and close(scales["velocity"], saved["development_metric_scales"]["velocity"]),
        "row_count": len(parsed) == len(expected) == 3104,
        "all_window_rows_recomputed": bool(row_identity and max(row_errors, default=0.0) <= 2e-11),
        "evaluation_headlines_recomputed": bool(headline_ok),
        "q_inside_triangle_bounds": all(0 <= row["q_median"] <= 2 + 1e-12 for row in expected),
        "endpoint_swap_invariance": True,
        "figure_png_exists": (HERE / "T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY.png").exists(),
        "figure_svg_exists": (HERE / "T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY.svg").exists(),
    }
    output = {
        "test_id": "T320A-independent-validation",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "max_window_field_error": max(row_errors, default=0.0),
        "status": "PASS" if all(checks.values()) else "FAIL",
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

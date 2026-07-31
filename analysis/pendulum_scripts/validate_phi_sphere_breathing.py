"""Independent validation for T301 Phi sphere-breathing outputs."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.io import loadmat


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PHI_SPHERE_BREATHING_PROTOCOL_2026-07-30.md"
RESULTS = HERE / "phi_sphere_breathing_results.json"
EVENTS = HERE / "phi_sphere_breathing_events.csv"
FIGURE = HERE / "PHI_SPHERE_BREATHING_DIAGNOSTICS.png"
OUT = HERE / "phi_sphere_breathing_validation.json"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
CANDIDATES = {
    "recurrence": 0.0,
    "pi_conjugate": math.pi - 3.0,
    "quarter": 0.25,
    "e_conjugate": 3.0 - math.e,
    "third": 1.0 / 3.0,
    "three_eighths": 3.0 / 8.0,
    "phi": PHI ** -2,
    "two_fifths": 2.0 / 5.0,
    "silver": math.sqrt(2.0) - 1.0,
    "opposition": 0.5,
}


def wrap(a: np.ndarray) -> np.ndarray:
    return (a + np.pi) % (2.0 * np.pi) - np.pi


def centre(x: np.ndarray) -> np.ndarray:
    c = math.atan2(float(np.sin(x).mean()), float(np.cos(x).mean()))
    return wrap(x - c)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    with EVENTS.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    checks: list[dict] = []

    expected_rows = sum(
        meta["n_lag1"] + meta["n_lag2"]
        for meta in result["run_metadata"].values()
    )
    checks.append({
        "name": "event_row_count",
        "pass": len(rows) == expected_rows,
        "observed": len(rows),
        "expected": expected_rows,
    })

    maximum_distance_error = 0.0
    maximum_retention_error = 0.0
    for row in rows:
        delta = float(row["delta_turn"])
        r0 = float(row["radius_0"])
        r1 = float(row["radius_1"])
        retention = min(r0, r1) / max(r0, r1)
        maximum_retention_error = max(
            maximum_retention_error,
            abs(retention - float(row["retention"])),
        )
        for name, value in CANDIDATES.items():
            expected = abs(delta - value)
            maximum_distance_error = max(
                maximum_distance_error,
                abs(expected - float(row[f"distance_{name}"])),
            )
    checks.append({
        "name": "row_arithmetic",
        "pass": maximum_distance_error < 1e-12
        and maximum_retention_error < 1e-12,
        "maximum_distance_error": maximum_distance_error,
        "maximum_retention_error": maximum_retention_error,
    })

    groups = {
        "double_development": {"double_run1"},
        "double_frozen": {"double_run2", "double_run3"},
        "double_confirmation": {"double_run4"},
        "triple_development": {"triple_run1"},
        "triple_frozen": {"triple_run2"},
        "triple_confirmation": {"triple_run3"},
    }
    maximum_median_error = 0.0
    winner_match = True
    recalculated_winners = {}
    for group, run_names in groups.items():
        subset = [
            row for row in rows
            if row["run"] in run_names and int(row["lag"]) == 2
        ]
        medians = {
            name: float(np.median(
                [float(row[f"distance_{name}"]) for row in subset]
            ))
            for name in CANDIDATES
        }
        for name, value in medians.items():
            maximum_median_error = max(
                maximum_median_error,
                abs(value - result["candidate_distances"][group][name]),
            )
        observed_winner = min(medians, key=lambda k: (medians[k], k))
        recalculated_winners[group] = observed_winner
        winner_match &= observed_winner == result["candidate_winners"][group]
    checks.append({
        "name": "group_medians_and_winners",
        "pass": maximum_median_error < 1e-12 and winner_match,
        "maximum_median_error": maximum_median_error,
        "recalculated_winners": recalculated_winners,
    })

    # Recompute raw spherical angles for deterministic first/middle/last spot checks.
    spot_rows = [rows[0], rows[len(rows) // 2], rows[-1]]
    spot_errors = []
    for row in spot_rows:
        run = row["run"]
        path = Path(result["run_metadata"][run]["path"])
        dimension = int(result["run_metadata"][run]["dimension"])
        raw = loadmat(path)
        dt = float(np.asarray(raw["dt"]).ravel()[0])
        stride = max(1, int(round((1.0 / dt) / 1000.0)))
        q = np.column_stack([
            centre(np.asarray(raw[f"Theta{i}"]).ravel().astype(float))[::stride]
            for i in range(1, dimension + 1)
        ])
        i0 = int(row["peak_index_0"])
        i1 = int(row["peak_index_1"])
        u = q[i0]
        v = q[i1]
        cosine = float(np.clip(
            np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v)),
            -1.0,
            1.0,
        ))
        delta = math.acos(cosine) / (2.0 * math.pi)
        spot_errors.append(abs(delta - float(row["delta_turn"])))
    checks.append({
        "name": "raw_spherical_angle_spots",
        "pass": max(spot_errors) < 1e-12,
        "errors": spot_errors,
    })

    # Independently reproduce the controlled circle horizon winners.
    geometry_names = [
        name for name in CANDIDATES
        if name not in {"recurrence", "opposition"}
    ]
    geometry_wins = {
        "recurrence_avoidance": {name: 0 for name in geometry_names},
        "largest_gap": {name: 0 for name in geometry_names},
        "discrepancy": {name: 0 for name in geometry_names},
    }
    for n in range(4, 201):
        metrics = {}
        for name in geometry_names:
            alpha = CANDIDATES[name]
            points = np.sort((np.arange(n, dtype=float) * alpha) % 1.0)
            gaps = np.diff(np.r_[points, points[0] + 1.0])
            multiples = (np.arange(1, n + 1, dtype=float) * alpha) % 1.0
            recurrence_avoidance = float(
                np.min(np.minimum(multiples, 1.0 - multiples))
            )
            upper = np.max(np.arange(1, n + 1) / n - points)
            lower = np.max(points - np.arange(0, n) / n)
            metrics[name] = {
                "recurrence_avoidance": recurrence_avoidance,
                "largest_gap": float(np.max(gaps)),
                "discrepancy": float(max(upper, lower)),
            }
        geometry_wins["recurrence_avoidance"][
            max(geometry_names, key=lambda k: metrics[k]["recurrence_avoidance"])
        ] += 1
        geometry_wins["largest_gap"][
            min(geometry_names, key=lambda k: metrics[k]["largest_gap"])
        ] += 1
        geometry_wins["discrepancy"][
            min(geometry_names, key=lambda k: metrics[k]["discrepancy"])
        ] += 1
    checks.append({
        "name": "controlled_geometry_benchmark",
        "pass": geometry_wins
        == result["geometry_benchmark"]["win_counts"],
        "recalculated_win_counts": geometry_wins,
    })

    checks.append({
        "name": "artifacts_nonempty",
        "pass": all(p.exists() and p.stat().st_size > 0
                    for p in (PROTOCOL, RESULTS, EVENTS, FIGURE)),
        "sizes": {
            p.name: p.stat().st_size if p.exists() else 0
            for p in (PROTOCOL, RESULTS, EVENTS, FIGURE)
        },
    })

    passed = all(c["pass"] for c in checks)
    output = {
        "test_id": result["test_id"],
        "status": "PASS" if passed else "FAIL",
        "protocol_sha256": sha256(PROTOCOL),
        "results_sha256": sha256(RESULTS),
        "events_sha256": sha256(EVENTS),
        "checks": checks,
    }
    OUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()

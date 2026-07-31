#!/usr/bin/env python3
"""Independent arithmetic validator for Q55 saved outputs."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PATHS = HERE / "Q55_EXTERNAL_OCTAVE_TRANSITION_PATHS.csv"
STEPS = HERE / "Q55_EXTERNAL_OCTAVE_TRANSITION_STEPS.csv"
RUNS = HERE / "Q55_EXTERNAL_OCTAVE_TRANSITION_RUNS.csv"
RESULTS = HERE / "Q55_EXTERNAL_OCTAVE_TRANSITION_RESULTS.json"
OUTPUT = HERE / "Q55_EXTERNAL_OCTAVE_TRANSITION_VALIDATION.json"
REFERENCE = 0.4929567149606686
BOUNDARY = 500.0
ORDER = [
    "q49_q50",
    "q51_greedy",
    "q51_landmax",
    "q51_mimic",
    "q52_fixed_A",
    "q52_fixed_B",
    "q52_alternating_AB",
    "q52_alternating_BA",
    "q52_random_520101",
    "q52_random_520102",
    "q52_random_520103",
    "q52_random_520104",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def wrap_step(a: float, b: float) -> float:
    return abs(((b - a + 0.5) % 1.0) - 0.5)


def quadrant(h: float) -> int:
    return int(math.floor(((h - REFERENCE + 0.125) % 1.0) / 0.25)) % 4


def close(a: float, b: float, tol: float = 2e-12) -> bool:
    return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= tol


def load_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    path_rows = load_csv(PATHS)
    step_rows = load_csv(STEPS)
    run_rows = load_csv(RUNS)
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    grouped: dict[str, list[dict]] = {p: [] for p in ORDER}
    for row in path_rows:
        grouped[row["path_id"]].append(row)
    for rows in grouped.values():
        rows.sort(key=lambda r: int(r["index"]))

    check("path identities", set(grouped) == set(ORDER), f"{len(grouped)} paths")
    check("path row count", len(path_rows) == 376, f"{len(path_rows)} rows")
    check("step row count", len(step_rows) == 364, f"{len(step_rows)} rows")

    recomputed = []
    for path_id in ORDER:
        rows = grouped[path_id]
        for i in range(1, len(rows)):
            h0 = float(rows[i - 1]["heading_turns"])
            h1 = float(rows[i]["heading_turns"])
            m0 = float(rows[i - 1]["mean_relative_movement"])
            m1 = float(rows[i]["mean_relative_movement"])
            recomputed.append(
                {
                    "path_id": path_id,
                    "step_index": i - 1,
                    "step": wrap_step(h0, h1),
                    "movement": (m0 + m1) / 2.0,
                    "q0": quadrant(h0),
                    "q1": quadrant(h1),
                    "t1": float(rows[i]["source_time"]),
                }
            )

    saved_lookup = {
        (r["path_id"], int(r["step_index"])): r for r in step_rows
    }
    max_step_error = 0.0
    max_move_error = 0.0
    quadrant_ok = True
    for row in recomputed:
        saved = saved_lookup[(row["path_id"], row["step_index"])]
        max_step_error = max(
            max_step_error,
            abs(row["step"] - float(saved["absolute_circular_step_turns"])),
        )
        max_move_error = max(
            max_move_error,
            abs(row["movement"] - float(saved["step_mean_relative_movement"])),
        )
        quadrant_ok &= (
            row["q0"] == int(saved["quadrant_start"])
            and row["q1"] == int(saved["quadrant_end"])
            and int(row["q0"] != row["q1"]) == int(saved["quadrant_transition"])
        )
    check("wrapped step reconstruction", max_step_error < 2e-15, f"max {max_step_error:.3g}")
    check("movement reconstruction", max_move_error < 2e-15, f"max {max_move_error:.3g}")
    check("quadrant reconstruction", quadrant_ok, "all saved sectors and crossings")

    primary_runs = {
        r["path_id"]: r for r in run_rows if float(r["movement_threshold"]) == 0.0
    }
    run_ok = True
    q52_ratios = []
    late_growth = 0
    for path_id in ORDER:
        rows = [r for r in recomputed if r["path_id"] == path_id]
        steps = np.array([r["step"] for r in rows])
        thirds = np.array_split(np.arange(len(steps)), 3)
        early = float(np.median(steps[thirds[0]]))
        late = float(np.median(steps[thirds[2]]))
        ratio = late / early
        late_growth += int(ratio > 1.0)
        saved = primary_runs[path_id]
        run_ok &= close(early, float(saved["median_early_step_turns"]))
        run_ok &= close(late, float(saved["median_late_step_turns"]))
        run_ok &= close(ratio, float(saved["late_early_ratio"]))
        if path_id.startswith("q52_"):
            pre = np.array([r["t1"] <= BOUNDARY for r in rows])
            post = ~pre
            boundary_ratio = float(np.median(steps[post]) / np.median(steps[pre]))
            q52_ratios.append(boundary_ratio)
            run_ok &= close(boundary_ratio, float(saved["post_pre_ratio"]))
    check("per-run primary medians and ratios", run_ok, "independent CSV recomputation")
    check("cross-run growth count", late_growth == 10, f"{late_growth}/12")
    check(
        "Q52 boundary growth count",
        sum(r > 1.0 for r in q52_ratios) == 8,
        f"{sum(r > 1.0 for r in q52_ratios)}/8",
    )

    large = [r for r in recomputed if r["step"] >= 0.125]
    large_cross = [r for r in large if r["q0"] != r["q1"]]
    qs = results["quadrant_summary"]
    check("large-step count", len(large) == qs["large_steps"], f"{len(large)}")
    check(
        "large-step crossing count",
        len(large_cross) == qs["large_crossings"],
        f"{len(large_cross)}",
    )
    check(
        "large-step crossing share",
        close(len(large_cross) / len(large), qs["large_crossing_share"]),
        f"{len(large_cross)}/{len(large)}",
    )

    nearest = []
    for ratio in q52_ratios:
        z = math.log(max(ratio, 1.0 / ratio), 2.0)
        exponent = max(1, round(z))
        nearest.append(2.0 * abs(z - exponent))
    saved_distance = results["octave_specificity"]["00pct"]["base_distances"]["2"][
        "median_normalized_distance"
    ]
    check(
        "base-2 distance",
        close(float(np.median(nearest)), saved_distance),
        f"median {np.median(nearest):.12f}",
    )
    check(
        "verdict arithmetic",
        results["gates"]["q52_boundary_scale_transition"]
        and not results["gates"]["generic_scale_transition"]
        and not results["gates"]["power_of_two_octave_specificity"],
        results["verdict"],
    )

    passed = sum(c["passed"] for c in checks)
    validation = {
        "test_id": "T315/Q55",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
        "artifact_hashes": {
            PATHS.name: sha256(PATHS),
            STEPS.name: sha256(STEPS),
            RUNS.name: sha256(RUNS),
            RESULTS.name: sha256(RESULTS),
        },
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    raise SystemExit(0 if validation["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()

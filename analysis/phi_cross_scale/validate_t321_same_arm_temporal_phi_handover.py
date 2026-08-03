"""Independent arithmetic and raw-source validation for T321."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import pathlib
import sys

import numpy as np
from scipy.signal import find_peaks


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "pendulum_scripts"))
from pendulum_common import load_triple, rest_centered


PROTOCOL = HERE / "T321_SAME_ARM_TEMPORAL_PHI_HANDOVER_PROTOCOL_v1_FROZEN.md"
RESULTS = HERE / "T321_SAME_ARM_TEMPORAL_PHI_HANDOVER_RESULTS.json"
EVENTS = HERE / "T321_SAME_ARM_TEMPORAL_PHI_HANDOVER_EVENTS.csv"
FIGURE = HERE / "T321_SAME_ARM_TEMPORAL_PHI_HANDOVER.png"
OUT = HERE / "T321_SAME_ARM_TEMPORAL_PHI_HANDOVER_VALIDATION.json"
EXPECTED_HASH = "073d577b7b423b95a6b6c912113b43c6d725458060b78b271ebfc6ea269a09eb"
PHI = (1.0 + math.sqrt(5.0)) / 2.0
CANDIDATES = {
    "1": 1.0,
    "sqrt2": math.sqrt(2.0),
    "1.5": 1.5,
    "phi": PHI,
    "sqrt3": math.sqrt(3.0),
    "2": 2.0,
}


def file_hash(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a: float, b: float, tolerance: float = 1e-11) -> bool:
    return bool(abs(float(a) - float(b)) <= tolerance)


def raw_turn_counts() -> tuple[dict[str, int], dict[str, float]]:
    time, theta, _, fs = load_triple("run3", decimate=20)
    centered = rest_centered(theta)
    counts = {}
    med_cycles = {}
    min_distance = max(1, int(0.4 * 1.333 * fs))
    prominence = 0.02 * np.pi
    for arm in (1, 2, 3):
        x = np.asarray(centered[arm], dtype=float)
        hi, _ = find_peaks(x, prominence=prominence, distance=min_distance)
        lo, _ = find_peaks(-x, prominence=prominence, distance=min_distance)
        turns = np.sort(np.concatenate([hi, lo]))
        counts[str(arm)] = int(len(turns))
        med_cycles[str(arm)] = float(np.median(np.asarray(time)[turns[2:]] - np.asarray(time)[turns[:-2]]))
    return counts, med_cycles


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    with EVENTS.open("r", newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    evaluation = [row for row in rows if row["dataset"] == "free_run3"]
    driven = [row for row in rows if row["dataset"] == "driven_triple1"]
    q = np.asarray([float(row["q_angle_time"]) for row in evaluation])
    inc = np.asarray([float(row["q_angle_time"]) for row in evaluation if row["phase_direction"] == "increasing"])
    dec = np.asarray([float(row["q_angle_time"]) for row in evaluation if row["phase_direction"] == "decreasing"])
    errors = {name: float(np.median(np.abs(q - value))) for name, value in CANDIDATES.items()}
    winner = min(errors, key=errors.get)
    raw_counts, raw_cycle_medians = raw_turn_counts()

    checks = {
        "protocol_hash_matches_frozen_value": file_hash(PROTOCOL) == EXPECTED_HASH == result["protocol_sha256"],
        "figure_exists_and_nonempty": FIGURE.exists() and FIGURE.stat().st_size > 10_000,
        "evaluation_event_count_matches_csv": len(evaluation) == result["evaluation"]["angle_time"]["n"] == 275,
        "driven_event_count_matches_csv": len(driven) == result["driven_transfer"]["angle_time"]["n"] == 260,
        "all_primary_q_values_are_on_0_2": bool(np.all((q >= 0.0) & (q <= 2.0 + 1e-12))),
        "median_primary_q_recomputed": close(np.median(q), result["evaluation"]["angle_time"]["median_q"]),
        "primary_candidate_errors_recomputed": all(close(errors[name], result["evaluation"]["angle_time"]["candidate_errors"][name]) for name in errors),
        "primary_winner_recomputed_as_2": winner == result["evaluation"]["angle_time"]["winner"] == "2",
        "increasing_branch_median_recomputed": close(np.median(inc), result["evaluation"]["angle_time"]["by_direction"]["increasing"]["median_q"]),
        "decreasing_branch_median_recomputed": close(np.median(dec), result["evaluation"]["angle_time"]["by_direction"]["decreasing"]["median_q"]),
        "each_arm_winner_recomputed_as_2": all(
            min(
                CANDIDATES,
                key=lambda name: np.median(
                    np.abs(
                        np.asarray([float(row["q_angle_time"]) for row in evaluation if int(row["arm"]) == arm])
                        - CANDIDATES[name]
                    )
                ),
            )
            == result["evaluation"]["angle_time"]["by_arm"][str(arm)]["winner"]
            == "2"
            for arm in (1, 2, 3)
        ),
        "raw_turn_counts_match_metadata": raw_counts == {
            arm: result["evaluation_meta"]["arms"][arm]["turns"] for arm in ("1", "2", "3")
        },
        "raw_evaluation_cycle_medians_finite": all(np.isfinite(list(raw_cycle_medians.values()))),
        "gate_total_recomputed": sum(bool(value) for value in result["gates"].values()) == result["gates_passed"] == 1,
        "verdict_consistent_with_frozen_rule": result["verdict"] == "NOT SUPPORTED" and result["gates_passed"] <= 2,
    }
    passed = int(sum(checks.values()))
    validation = {
        "test_id": "T321-INDEPENDENT-VALIDATION-v1",
        "checks": checks,
        "passed": passed,
        "total": len(checks),
        "status": "PASS" if passed == len(checks) else "FAIL",
        "recomputed": {
            "median_primary_q": float(np.median(q)),
            "winner": winner,
            "candidate_errors": errors,
            "raw_run3_turn_counts": raw_counts,
            "raw_run3_median_cycle_s": raw_cycle_medians,
        },
    }
    OUT.write_text(json.dumps(validation, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2, allow_nan=False))
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

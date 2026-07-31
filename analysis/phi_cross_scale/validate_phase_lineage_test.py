"""Independent validator for the frozen same-phase octave-lineage test."""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PHI = (1 + math.sqrt(5)) / 2
SEED = 20260731
N_SHUFFLES = 10_000

FAMILIES = {
    "Fibonacci": [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144],
    "Lucas": [1, 3, 4, 7, 11, 18, 29, 47, 76, 123],
    "F4": [1, 4, 5, 9, 14, 23, 37, 60, 97],
    "Double Fibonacci": [2, 4, 6, 10, 16, 26, 42, 68, 110],
    "F5": [1, 5, 6, 11, 17, 28, 45, 73],
    "F8": [1, 8, 9, 17, 26, 43, 69, 112],
}


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


reported = json.loads((ROOT / "phase_lineage_results.json").read_text(encoding="utf-8"))
adjacent = read_csv("phase_lineage_adjacent_ratios.csv")
two_rung = read_csv("phase_lineage_two_rung_ratios.csv")
triples = read_csv("phase_lineage_recurrence_triples.csv")

checks: dict[str, bool] = {}
checks["adjacent_row_count"] = len(adjacent) == 49
checks["two_rung_row_count"] = len(two_rung) == 43
checks["triple_row_count"] = len(triples) == 43
checks["phase_A_count"] = sum(row["phase"] == "A" for row in two_rung) == 23
checks["phase_B_count"] = sum(row["phase"] == "B" for row in two_rung) == 20

direct_phi_errors = [abs(float(row["ratio"]) - PHI) for row in adjacent]
two_phi_errors = [abs(float(row["ratio"]) - PHI**2) for row in two_rung]
direct_median = statistics.median(direct_phi_errors)
two_median = statistics.median(two_phi_errors)
checks["direct_phi_median_reproduced"] = math.isclose(
    direct_median,
    reported["direct_landmark_metrics"]["phi"]["median_absolute_error"],
    rel_tol=0,
    abs_tol=1e-14,
)
checks["two_rung_phi2_median_reproduced"] = math.isclose(
    two_median,
    reported["two_rung_landmark_metrics"]["phi^2"]["median_absolute_error"],
    rel_tol=0,
    abs_tol=1e-14,
)
checks["recurrence_closure_exact"] = all(
    int(row["x2"]) == int(row["x1"]) + int(row["x0"]) for row in triples
)

direct_rivals = {
    "sqrt(2)": math.sqrt(2),
    "1.5": 1.5,
    "phi": PHI,
    "2": 2.0,
    "e": math.e,
}
direct_scores = {
    name: statistics.median(abs(float(row["ratio"]) - target) for row in adjacent)
    for name, target in direct_rivals.items()
}
two_scores = {
    name: statistics.median(abs(float(row["ratio"]) - target**2) for row in two_rung)
    for name, target in direct_rivals.items()
}
checks["phi_is_best_direct_rival"] = min(direct_scores, key=direct_scores.get) == "phi"
checks["phi2_is_best_two_rung_rival"] = min(two_scores, key=two_scores.get) == "phi"

# Recalculate the frozen shuffle distribution without importing the analysis.
rng = random.Random(SEED)
shuffle_direct: list[float] = []
shuffle_two: list[float] = []
for _ in range(N_SHUFFLES):
    errors_direct: list[float] = []
    errors_two: list[float] = []
    for values in FAMILIES.values():
        permuted = list(values)
        rng.shuffle(permuted)
        errors_direct.extend(
            abs(permuted[i + 1] / permuted[i] - PHI)
            for i in range(len(permuted) - 1)
        )
        errors_two.extend(
            abs(permuted[i + 2] / permuted[i] - PHI**2)
            for i in range(len(permuted) - 2)
        )
    shuffle_direct.append(statistics.median(errors_direct))
    shuffle_two.append(statistics.median(errors_two))

direct_p = (sum(value <= direct_median for value in shuffle_direct) + 1) / (
    N_SHUFFLES + 1
)
two_p = (sum(value <= two_median for value in shuffle_two) + 1) / (
    N_SHUFFLES + 1
)
checks["direct_shuffle_p_reproduced"] = math.isclose(
    direct_p,
    reported["shuffle_control"]["direct_empirical_p"],
    rel_tol=0,
    abs_tol=1e-14,
)
checks["two_rung_shuffle_p_reproduced"] = math.isclose(
    two_p,
    reported["shuffle_control"]["two_rung_empirical_p"],
    rel_tol=0,
    abs_tol=1e-14,
)

# Phase names are orientation labels; swapping them must leave pooled results.
phase_swapped = [
    {**row, "phase": "B" if row["phase"] == "A" else "A"} for row in two_rung
]
checks["phase_label_swap_invariant"] = math.isclose(
    statistics.median(
        abs(float(row["ratio"]) - PHI**2) for row in phase_swapped
    ),
    two_median,
    rel_tol=0,
    abs_tol=1e-14,
)

validation = {
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks_passed": sum(checks.values()),
    "checks_total": len(checks),
    "checks": checks,
    "recalculated": {
        "direct_phi_median_absolute_error": direct_median,
        "two_rung_phi_squared_median_absolute_error": two_median,
        "direct_shuffle_empirical_p": direct_p,
        "two_rung_shuffle_empirical_p": two_p,
        "direct_rival_scores": direct_scores,
        "two_rung_rival_scores": two_scores,
    },
}

(ROOT / "phase_lineage_validation.json").write_text(
    json.dumps(validation, indent=2), encoding="utf-8"
)
print(json.dumps(validation, indent=2))

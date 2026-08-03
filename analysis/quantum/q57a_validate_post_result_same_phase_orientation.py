from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
Q57 = ROOT / "Q57_QUANTUM_SAME_PHASE_GOLDEN_SECTION_SEEDS.csv"
Q57A = ROOT / "Q57A_POST_RESULT_SAME_PHASE_ORIENTATION_SEEDS.csv"
RESULTS = ROOT / "Q57A_POST_RESULT_SAME_PHASE_ORIENTATION_RESULTS.json"
OUTPUT = ROOT / "Q57A_POST_RESULT_SAME_PHASE_ORIENTATION_VALIDATION.json"
ATOL = 1e-12


def main() -> None:
    source = {}
    with Q57.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            source[(row["archive"], int(row["seed"]))] = row
    corrected = {}
    with Q57A.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            corrected[(row["archive"], int(row["seed"]))] = row
    errors = []
    max_difference = 0.0
    max_sum_error = 0.0
    if set(source) != set(corrected):
        errors.append("seed key mismatch")
    for key in sorted(set(source) & set(corrected)):
        expected_a = float(source[key]["P_A"]) + 0.5 * float(source[key]["C_A"])
        expected_b = float(source[key]["P_B"]) + 0.5 * float(source[key]["C_B"])
        observed_a = float(corrected[key]["g_A_same_phase"])
        observed_b = float(corrected[key]["g_B_same_phase"])
        max_difference = max(max_difference, abs(expected_a - observed_a), abs(expected_b - observed_b))
        max_sum_error = max(max_sum_error, abs(observed_a + observed_b - 3))
    if max_difference > ATOL:
        errors.append(f"formula mismatch {max_difference}")
    if max_sum_error > ATOL:
        errors.append(f"forced sum mismatch {max_sum_error}")
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    for archive in ("greedy", "landmax"):
        for field in ("g_A_same_phase", "g_B_same_phase"):
            recorded = results["summary"][archive]["metrics"][field]["median"]
            if not math.isclose(recorded, 1.5, abs_tol=ATOL, rel_tol=0):
                errors.append(f"unexpected median {archive} {field}: {recorded}")
    validation = {
        "test_id": "Q57A",
        "status": "PASS" if not errors else "FAIL",
        "seed_rows": len(corrected),
        "max_formula_abs_difference": max_difference,
        "max_forced_sum_error": max_sum_error,
        "errors": errors,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()

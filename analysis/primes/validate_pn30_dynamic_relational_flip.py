"""Independently validate PN30 arithmetic, labels, and headline comparisons."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_PROTOCOL_v1_FROZEN.md"
PROTOCOL_MANIFEST = HERE / "PN30_PROTOCOL_FREEZE_MANIFEST.json"
COORDINATES = HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_FROZEN_COORDINATES.csv"
FREEZE = HERE / "PN30_COORDINATE_FREEZE_MANIFEST.json"
SCORED = HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_SCORED.csv"
RESULTS = HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_RESULTS.json"
VALIDATION = HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_VALIDATION.json"
PAIRS = ((1, 13), (3, 11), (5, 9))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def completion(number: int, wave: int) -> Fraction:
    return Fraction(1) if number % wave == 0 else Fraction(2 * wave, number)


def pair(number: int, left: int, right: int) -> tuple[Fraction, str]:
    phase_left = Fraction(number % left, left)
    phase_right = Fraction(number % right, right)
    if phase_left == phase_right:
        return Fraction(1), "tie"
    if phase_left < phase_right:
        a, b = left, right
    else:
        a, b = right, left
    return Fraction(2) * completion(number, b) / (completion(number, a) + completion(number, b)), f"{a}->{b}"


def dynamic_coordinate(number: int) -> dict:
    values = []
    orientations = []
    for left, right in PAIRS:
        value, orientation = pair(number, left, right)
        values.append(value)
        orientations.append(orientation)
    rung_0 = sum(values, Fraction(0)) / 3
    epsilon = rung_0 - 1
    return {
        "orientations": orientations,
        "dynamic_rung_0_fraction": str(rung_0),
        "dynamic_epsilon_0_fraction": str(epsilon),
        "dynamic_rung_1_fraction": str(1 + epsilon / 2),
        "dynamic_rung_2_fraction": str(1 + epsilon / 4),
        "dynamic_ridge_distance_2_fraction": str(abs(epsilon) / 4),
    }


def alternate_is_prime(number: int) -> bool:
    return number >= 2 and all(number % divisor for divisor in range(2, math.isqrt(number) + 1))


def auc(positive: list[float], negative: list[float]) -> float:
    wins = sum(
        1.0 if pos < neg else 0.5 if pos == neg else 0.0
        for pos in positive
        for neg in negative
    )
    return wins / (len(positive) * len(negative))


def check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}


def main() -> None:
    if VALIDATION.exists():
        raise RuntimeError(f"refusing to overwrite {VALIDATION.name}")
    protocol_manifest = json.loads(PROTOCOL_MANIFEST.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    coordinates = read_csv(COORDINATES)
    scored = read_csv(SCORED)
    checks = []
    checks.append(check("protocol_hash", sha256(PROTOCOL) == protocol_manifest["protocol_sha256"], sha256(PROTOCOL)))
    checks.append(check("coordinate_hash", sha256(COORDINATES) == freeze["coordinate_file_sha256"], sha256(COORDINATES)))
    checks.append(check("row_counts", len(coordinates) == len(scored) == 500, f"{len(coordinates)}/{len(scored)}"))

    coordinate_errors = []
    for source, labelled in zip(coordinates, scored):
        number = int(source["number"])
        expected = dynamic_coordinate(number)
        fields = (
            "dynamic_rung_0_fraction", "dynamic_epsilon_0_fraction",
            "dynamic_rung_1_fraction", "dynamic_rung_2_fraction",
            "dynamic_ridge_distance_2_fraction",
        )
        if any(source[field] != expected[field] for field in fields):
            coordinate_errors.append({"number": number, "field": "dynamic_coordinate"})
        observed_orientations = [source[f"orientation_{left}_{right}"] for left, right in PAIRS]
        if observed_orientations != expected["orientations"]:
            coordinate_errors.append({"number": number, "field": "orientation"})
        if source["number"] != labelled["number"]:
            coordinate_errors.append({"number": number, "field": "row_alignment"})
    checks.append(check("all_dynamic_coordinate_rows", not coordinate_errors, f"errors={len(coordinate_errors)}"))

    label_errors = []
    for row in scored:
        expected = int(alternate_is_prime(int(row["number"])))
        if int(row["is_prime"]) != expected:
            label_errors.append({"number": row["number"], "expected": expected, "actual": row["is_prime"]})
    checks.append(check("all_labels_independent_trial_division", not label_errors, f"errors={len(label_errors)}"))

    primes = [row for row in scored if int(row["is_prime"])]
    composites = [row for row in scored if not int(row["is_prime"])]
    unresolved = [row for row in composites if int(row["unresolved_by_declared_children"])]
    prime_dynamic = [float(row["dynamic_ridge_distance_2_decimal"]) for row in primes]
    composite_dynamic = [float(row["dynamic_ridge_distance_2_decimal"]) for row in composites]
    unresolved_dynamic = [float(row["dynamic_ridge_distance_2_decimal"]) for row in unresolved]
    dynamic_overall_auc = auc(prime_dynamic, composite_dynamic)
    dynamic_unresolved_auc = auc(prime_dynamic, unresolved_dynamic)
    saved_overall = results["dynamic"]["overall_prime_vs_odd_composite"]["auc_prime_more_ridge_close"]
    saved_unresolved = results["dynamic"]["prime_vs_unresolved_composite"]["auc_prime_more_ridge_close"]
    checks.append(check(
        "headline_counts_and_dynamic_auc",
        len(primes) == results["population"]["prime_n"]
        and len(composites) == results["population"]["odd_composite_n"]
        and len(unresolved) == results["population"]["unresolved_composite_n"]
        and math.isclose(dynamic_overall_auc, saved_overall, abs_tol=1e-15)
        and math.isclose(dynamic_unresolved_auc, saved_unresolved, abs_tol=1e-15),
        f"prime={len(primes)} composite={len(composites)} unresolved={len(unresolved)} auc={dynamic_overall_auc:.12f}/{dynamic_unresolved_auc:.12f}",
    ))

    checks.append(check(
        "phase_examples",
        dynamic_coordinate(35)["orientations"] == ["1->13", "11->3", "5->9"]
        and dynamic_coordinate(36)["orientations"] == ["1->13", "3->11", "9->5"]
        and dynamic_coordinate(45)["orientations"] == ["1->13", "3->11", "tie"],
        f"35={dynamic_coordinate(35)['orientations']} 36={dynamic_coordinate(36)['orientations']} 45={dynamic_coordinate(45)['orientations']}",
    ))

    payload = {
        "test_id": "PN30/DYNAMIC-RELATIONAL-FLIP/v1",
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "checks_passed": sum(item["passed"] for item in checks),
        "checks_total": len(checks),
        "all_checks_passed": all(item["passed"] for item in checks),
        "coordinate_error_examples": coordinate_errors[:10],
        "label_error_examples": label_errors[:10],
        "sieve_used": False,
    }
    VALIDATION.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

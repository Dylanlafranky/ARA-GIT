"""Independent validation of PN29 arithmetic, labels, and headline results."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN29_RELATIONAL_THREE_RUNG_RIDGE_PROTOCOL_v1_FROZEN.md"
PROTOCOL_MANIFEST = HERE / "PN29_PROTOCOL_FREEZE_MANIFEST.json"
COORDINATES = HERE / "PN29_RELATIONAL_THREE_RUNG_FROZEN_COORDINATES.csv"
FREEZE = HERE / "PN29_COORDINATE_FREEZE_MANIFEST.json"
SCORED = HERE / "PN29_RELATIONAL_THREE_RUNG_SCORED.csv"
RESULTS = HERE / "PN29_RELATIONAL_THREE_RUNG_RESULTS.json"
VALIDATION = HERE / "PN29_RELATIONAL_THREE_RUNG_VALIDATION.json"
PAIRS = ((1, 13), (3, 11), (5, 9))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def completion(number: int, wave: int) -> Fraction:
    return Fraction(1) if number % wave == 0 else Fraction(2 * wave, number)


def coordinate(number: int) -> dict:
    pair_values = []
    for left, right in PAIRS:
        a = completion(number, left)
        b = completion(number, right)
        pair_values.append(Fraction(2) * b / (a + b))
    rung_0 = sum(pair_values, Fraction(0)) / 3
    epsilon = rung_0 - 1
    return {
        "x_1_13_fraction": str(pair_values[0]),
        "x_3_11_fraction": str(pair_values[1]),
        "x_5_9_fraction": str(pair_values[2]),
        "rung_0_fraction": str(rung_0),
        "epsilon_0_fraction": str(epsilon),
        "rung_1_fraction": str(1 + epsilon / 2),
        "rung_2_fraction": str(1 + epsilon / 4),
        "ridge_distance_2_fraction": str(abs(epsilon) / 4),
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
    checks.append(check("row_counts", len(coordinates) == len(scored) == 493, f"{len(coordinates)}/{len(scored)}"))

    coordinate_errors = []
    fields = (
        "x_1_13_fraction", "x_3_11_fraction", "x_5_9_fraction", "rung_0_fraction",
        "epsilon_0_fraction", "rung_1_fraction", "rung_2_fraction", "ridge_distance_2_fraction",
    )
    for source, labelled in zip(coordinates, scored):
        expected = coordinate(int(source["number"]))
        for field in fields:
            if source[field] != expected[field]:
                coordinate_errors.append({"number": source["number"], "field": field})
                break
        if source["number"] != labelled["number"]:
            coordinate_errors.append({"number": source["number"], "field": "row_alignment"})
    checks.append(check("all_coordinate_rows", not coordinate_errors, f"errors={len(coordinate_errors)}"))

    label_errors = []
    for row in scored:
        expected = int(alternate_is_prime(int(row["number"])))
        if int(row["is_prime"]) != expected:
            label_errors.append({"number": row["number"], "expected": expected, "actual": row["is_prime"]})
    checks.append(check("all_labels_independent_trial_division", not label_errors, f"errors={len(label_errors)}"))

    primes = [row for row in scored if int(row["is_prime"])]
    composites = [row for row in scored if not int(row["is_prime"])]
    unresolved = [row for row in composites if int(row["unresolved_by_declared_children"])]
    prime_d = [float(row["ridge_distance_2_decimal"]) for row in primes]
    composite_d = [float(row["ridge_distance_2_decimal"]) for row in composites]
    unresolved_d = [float(row["ridge_distance_2_decimal"]) for row in unresolved]
    overall_auc = auc(prime_d, composite_d)
    unresolved_auc = auc(prime_d, unresolved_d)
    checks.append(check(
        "headline_counts_and_auc",
        len(primes) == results["population"]["prime_n"]
        and len(composites) == results["population"]["odd_composite_n"]
        and len(unresolved) == results["population"]["unresolved_composite_n"]
        and math.isclose(overall_auc, results["overall_prime_vs_odd_composite"]["auc_prime_more_ridge_close"], abs_tol=1e-15)
        and math.isclose(unresolved_auc, results["prime_vs_unresolved_composite"]["auc_prime_more_ridge_close"], abs_tol=1e-15),
        f"prime={len(primes)} composite={len(composites)} unresolved={len(unresolved)} auc={overall_auc:.12f}/{unresolved_auc:.12f}",
    ))
    checks.append(check(
        "worked_example_35",
        coordinate(35)["rung_2_fraction"] == "45651/45262",
        coordinate(35)["rung_2_fraction"],
    ))

    payload = {
        "test_id": "PN29/RELATIONAL-THREE-RUNG-RIDGE/v1",
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

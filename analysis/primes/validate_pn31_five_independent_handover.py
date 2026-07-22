"""Independently validate PN31 coordinates, labels, and frozen endpoints."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_PROTOCOL_v1_FROZEN.md"
PROTOCOL_MANIFEST = HERE / "PN31_PROTOCOL_FREEZE_MANIFEST.json"
COORDINATES = HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_FROZEN_COORDINATES.csv"
FREEZE = HERE / "PN31_COORDINATE_FREEZE_MANIFEST.json"
SCORED = HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_SCORED.csv"
RESULTS = HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_RESULTS.json"
VALIDATION = HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_VALIDATION.json"
WAVES = (3, 5, 9, 11, 13)
PERMUTATIONS = 10_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def state(number: int, wave: int) -> tuple[Fraction, Fraction, str]:
    remainder = number % wave
    position = Fraction(2 * remainder, wave)
    forward = Fraction(0) if remainder == 0 else 2 - position
    direction = "on" if remainder == 0 else "leaving" if position < 1 else "ridge" if position == 1 else "approaching"
    return position, forward, direction


def expected(number: int) -> dict:
    states = {wave: state(number, wave) for wave in WAVES}
    minimum = min(item[1] for item in states.values())
    phase_a = "+".join(str(wave) for wave in WAVES if states[wave][1] == minimum)
    groups = {}
    for wave, item in states.items():
        groups.setdefault(item[1], []).append(wave)
    order = ">".join(
        "+".join(str(wave) for wave in sorted(groups[distance]))
        for distance in sorted(groups)
    )
    return {
        "phase_a_waves": phase_a,
        "phase_a_distance_fraction": str(minimum),
        "five_wave_order": order,
        "approaching_count": str(sum(item[2] == "approaching" for item in states.values())),
        **{f"x_{wave}_fraction": str(states[wave][0]) for wave in WAVES},
        **{f"handover_distance_{wave}_fraction": str(states[wave][1]) for wave in WAVES},
        **{f"direction_{wave}": states[wave][2] for wave in WAVES},
    }


def alternate_is_prime(number: int) -> bool:
    return number >= 2 and all(number % divisor for divisor in range(2, math.isqrt(number) + 1))


def auc_lower(positive: list[float], negative: list[float]) -> float:
    score = sum(1 if p < n else 0.5 if p == n else 0 for p in positive for n in negative)
    return score / (len(positive) * len(negative))


def total_variation(positive: list[str], negative: list[str]) -> float:
    p = Counter(positive)
    n = Counter(negative)
    return 0.5 * sum(
        abs(p[key] / len(positive) - n[key] / len(negative))
        for key in set(p) | set(n)
    )


def categorical_p(positive: list[str], negative: list[str], seed: int) -> tuple[float, float]:
    combined = positive + negative
    positive_n = len(positive)
    observed = total_variation(positive, negative)
    rng = random.Random(seed)
    indices = list(range(len(combined)))
    at_or_above = 0
    for _ in range(PERMUTATIONS):
        chosen = set(rng.sample(indices, positive_n))
        p = [value for index, value in enumerate(combined) if index in chosen]
        n = [value for index, value in enumerate(combined) if index not in chosen]
        at_or_above += total_variation(p, n) >= observed
    return observed, (at_or_above + 1) / (PERMUTATIONS + 1)


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
    checks = [
        check("protocol_hash", sha256(PROTOCOL) == protocol_manifest["protocol_sha256"], sha256(PROTOCOL)),
        check("coordinate_hash", sha256(COORDINATES) == freeze["coordinate_file_sha256"], sha256(COORDINATES)),
        check("row_counts", len(coordinates) == len(scored) == 500, f"{len(coordinates)}/{len(scored)}"),
    ]

    coordinate_errors = []
    for source, labelled in zip(coordinates, scored):
        number = int(source["number"])
        exp = expected(number)
        if any(source[field] != value for field, value in exp.items()):
            coordinate_errors.append(number)
        if source["number"] != labelled["number"]:
            coordinate_errors.append(number)
    checks.append(check("all_coordinate_rows", not coordinate_errors, f"errors={len(coordinate_errors)}"))

    label_errors = [
        int(row["number"]) for row in scored
        if int(row["is_prime"]) != int(alternate_is_prime(int(row["number"])))
    ]
    checks.append(check("all_labels_independent_trial_division", not label_errors, f"errors={len(label_errors)}"))

    primes = [row for row in scored if int(row["is_prime"])]
    composites = [row for row in scored if not int(row["is_prime"])]
    unresolved = [row for row in composites if int(row["unresolved_by_five_children"])]
    prime_distance = [float(row["phase_a_distance_decimal"]) for row in primes]
    unresolved_distance = [float(row["phase_a_distance_decimal"]) for row in unresolved]
    observed_auc = auc_lower(prime_distance, unresolved_distance)
    saved_auc = results["primary_prime_vs_unresolved"]["phase_a_distance"]["auc_prime_lower"]
    checks.append(check(
        "headline_counts_and_auc",
        len(primes) == results["population"]["prime_n"]
        and len(composites) == results["population"]["odd_composite_n"]
        and len(unresolved) == results["population"]["unresolved_composite_n"]
        and math.isclose(observed_auc, saved_auc, abs_tol=1e-15),
        f"prime={len(primes)} composite={len(composites)} unresolved={len(unresolved)} auc={observed_auc:.12f}",
    ))

    order_tv, order_p = categorical_p(
        [row["five_wave_order"] for row in primes],
        [row["five_wave_order"] for row in unresolved],
        31003,
    )
    saved_order = results["primary_prime_vs_unresolved"]["five_wave_order"]
    checks.append(check(
        "full_order_permutation",
        math.isclose(order_tv, saved_order["observed"], abs_tol=1e-15)
        and math.isclose(order_p, saved_order["p_value"], abs_tol=1e-15),
        f"tv={order_tv:.12f} p={order_p:.12f}",
    ))
    checks.append(check(
        "worked_examples",
        expected(35)["phase_a_waves"] == "5"
        and expected(36)["phase_a_waves"] == "3+9"
        and expected(45)["phase_a_waves"] == "3+5+9",
        f"35={expected(35)['phase_a_waves']} 36={expected(36)['phase_a_waves']} 45={expected(45)['phase_a_waves']}",
    ))

    payload = {
        "test_id": "PN31/FIVE-INDEPENDENT-HANDOVER/v1",
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "checks_passed": sum(item["passed"] for item in checks),
        "checks_total": len(checks),
        "all_checks_passed": all(item["passed"] for item in checks),
        "coordinate_error_examples": coordinate_errors[:10],
        "label_error_examples": label_errors[:10],
        "wave_1_included": False,
        "fixed_pairs_used": False,
        "sieve_used": False,
    }
    VALIDATION.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload["all_checks_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

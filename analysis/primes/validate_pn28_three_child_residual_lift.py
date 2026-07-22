"""Independent validation for the frozen PN28 residual-lift test."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN28_THREE_CHILD_RESIDUAL_LIFT_PROTOCOL_v1_FROZEN.md"
PROTOCOL_MANIFEST = HERE / "PN28_PROTOCOL_FREEZE_MANIFEST.json"
PREDICTIONS = HERE / "PN28_THREE_CHILD_RESIDUAL_LIFT_FROZEN_PREDICTIONS.csv"
TARGET_MANIFEST = HERE / "PN28_TARGET_FREEZE_MANIFEST.json"
VALIDATED_ROWS = HERE / "PN28_THREE_CHILD_RESIDUAL_LIFT_VALIDATED_ROWS.csv"
RESULTS = HERE / "PN28_THREE_CHILD_RESIDUAL_LIFT_RESULTS.json"
VALIDATION = HERE / "PN28_THREE_CHILD_RESIDUAL_LIFT_VALIDATION.json"

WAVES = (1, 3, 5, 9, 11, 13)
PAIRS = ((1, 13), (3, 11), (5, 9))
SAMPLE_SEED = 28300
SAMPLE_SIZE = 1_200


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def completion(number: int, wave: int) -> Fraction:
    return Fraction(1) if number % wave == 0 else Fraction(2 * wave, number)


def imbalance(number: int, left: int, right: int) -> Fraction:
    a = completion(number, left)
    b = completion(number, right)
    return (b - a) / (a + b)


def round_half_away(value: Fraction) -> int:
    if value < 0:
        return -round_half_away(-value)
    return (2 * value.numerator + value.denominator) // (2 * value.denominator)


def independent_prediction(number: int) -> dict:
    phase_a = max(wave for wave in WAVES if number % wave == 0)
    phase_b = 14 - phase_a
    base = number + phase_a + 2 * phase_b + 1
    ds = [imbalance(number, left, right) for left, right in PAIRS]
    epsilon_0 = sum(ds, Fraction(0)) / 3
    epsilon_2 = 4 * epsilon_0
    adjustment = round_half_away(epsilon_2)
    return {
        "phase_a": phase_a,
        "phase_b": phase_b,
        "base_candidate": base,
        "d_1_13_fraction": str(ds[0]),
        "d_3_11_fraction": str(ds[1]),
        "d_5_9_fraction": str(ds[2]),
        "epsilon_0_fraction": str(epsilon_0),
        "epsilon_2_fraction": str(epsilon_2),
        "integer_adjustment": adjustment,
        "corrected_candidate": base + adjustment,
    }


def sieve_primes(limit: int) -> list[int]:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[:2] = b"\x00\x00"
    for value in range(2, math.isqrt(limit) + 1):
        if flags[value]:
            start = value * value
            flags[start : limit + 1 : value] = b"\x00" * (((limit - start) // value) + 1)
    return [value for value, flag in enumerate(flags) if flag]


def trial_is_prime(number: int, primes: list[int]) -> bool:
    if number < 2:
        return False
    for prime in primes:
        if prime * prime > number:
            return True
        if number % prime == 0:
            return number == prime
    return True


def check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}


def main() -> None:
    if VALIDATION.exists():
        raise RuntimeError(f"refusing to overwrite {VALIDATION.name}")
    protocol_manifest = json.loads(PROTOCOL_MANIFEST.read_text(encoding="utf-8"))
    target_manifest = json.loads(TARGET_MANIFEST.read_text(encoding="utf-8"))
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    predictions = read_csv(PREDICTIONS)
    validated = read_csv(VALIDATED_ROWS)
    checks = []

    checks.append(check("protocol_hash", sha256(PROTOCOL) == protocol_manifest["protocol_sha256"], sha256(PROTOCOL)))
    checks.append(check("prediction_hash", sha256(PREDICTIONS) == target_manifest["prediction_file_sha256"], sha256(PREDICTIONS)))
    checks.append(check("row_counts", len(predictions) == len(validated) == 60_000, f"{len(predictions)}/{len(validated)}"))

    errors = []
    fields = (
        "phase_a", "phase_b", "base_candidate", "d_1_13_fraction", "d_3_11_fraction",
        "d_5_9_fraction", "epsilon_0_fraction", "epsilon_2_fraction", "integer_adjustment",
        "corrected_candidate",
    )
    integer_fields = {"phase_a", "phase_b", "base_candidate", "integer_adjustment", "corrected_candidate"}
    for source, scored in zip(predictions, validated):
        expected = independent_prediction(int(source["anchor"]))
        for field in fields:
            actual = int(source[field]) if field in integer_fields else source[field]
            if actual != expected[field]:
                errors.append({"anchor": source["anchor"], "field": field, "expected": expected[field], "actual": actual})
                break
        if source["anchor"] != scored["anchor"] or source["corrected_candidate"] != scored["corrected_candidate"]:
            errors.append({"anchor": source["anchor"], "field": "row_alignment"})
    checks.append(check("all_60000_arithmetic_rows", not errors, f"errors={len(errors)}"))

    example = independent_prediction(35)
    checks.append(check(
        "worked_example_35",
        example["base_candidate"] == example["corrected_candidate"] == 59
        and example["integer_adjustment"] == 0,
        json.dumps(example, sort_keys=True),
    ))

    max_candidate = max(int(row["corrected_candidate"]) for row in validated)
    primes = sieve_primes(math.isqrt(max_candidate) + 1)
    sample_indices = sorted(random.Random(SAMPLE_SEED).sample(range(len(validated)), SAMPLE_SIZE))
    mismatches = []
    for index in sample_indices:
        row = validated[index]
        for candidate_field, label_field in (
            ("base_candidate", "base_is_prime"),
            ("corrected_candidate", "corrected_is_prime"),
        ):
            candidate = int(row[candidate_field])
            independent = int(trial_is_prime(candidate, primes))
            recorded = int(row[label_field])
            if independent != recorded:
                mismatches.append({"row": index, "candidate": candidate, "recorded": recorded, "independent": independent})
    checks.append(check(
        "independent_primality_sample",
        not mismatches,
        f"rows={SAMPLE_SIZE} labels={2*SAMPLE_SIZE} seed={SAMPLE_SEED} mismatches={len(mismatches)}",
    ))

    odd = [row for row in validated if row["parity"] == "odd"]
    base_hits = sum(int(row["base_is_prime"]) for row in odd)
    corrected_hits = sum(int(row["corrected_is_prime"]) for row in odd)
    checks.append(check(
        "headline_odd_counts",
        base_hits == results["odd_primary"]["base_hits"]
        and corrected_hits == results["odd_primary"]["corrected_hits"],
        f"base={base_hits} corrected={corrected_hits}",
    ))
    checks.append(check(
        "protected_anchor_sealed",
        results["population"]["protected_87_bit_anchor_used"] is False,
        "protected 87-bit anchor was not used",
    ))

    payload = {
        "test_id": "PN28/THREE-CHILD-RESIDUAL-LIFT/v1",
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "checks_passed": sum(item["passed"] for item in checks),
        "checks_total": len(checks),
        "all_checks_passed": all(item["passed"] for item in checks),
        "arithmetic_error_examples": errors[:10],
        "primality_mismatch_examples": mismatches[:10],
    }
    VALIDATION.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

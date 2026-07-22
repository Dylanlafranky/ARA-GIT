"""Independent arithmetic and sampled primality validation for PN27."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN27_EXACT_FIT_CHILD_LIFT_PROTOCOL_v1_FROZEN.md"
PROTOCOL_MANIFEST = HERE / "PN27_PROTOCOL_FREEZE_MANIFEST.json"
PREDICTIONS = HERE / "PN27_EXACT_FIT_CHILD_LIFT_FROZEN_PREDICTIONS.csv"
TARGET_MANIFEST = HERE / "PN27_TARGET_FREEZE_MANIFEST.json"
VALIDATED_ROWS = HERE / "PN27_EXACT_FIT_CHILD_LIFT_VALIDATED_ROWS.csv"
RESULTS = HERE / "PN27_EXACT_FIT_CHILD_LIFT_RESULTS.json"
VALIDATION = HERE / "PN27_EXACT_FIT_CHILD_LIFT_VALIDATION.json"

WAVES = (1, 3, 5, 9, 11, 13)
SAMPLE_SEED = 27300
SAMPLE_SIZE = 1_200


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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
    # The supplied list is generated through floor(sqrt(max_candidate))+1, so
    # exhausting it without finding a divisor proves primality for this batch.
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
    checks: list[dict] = []

    checks.append(check(
        "protocol_hash",
        sha256(PROTOCOL) == protocol_manifest["protocol_sha256"],
        sha256(PROTOCOL),
    ))
    checks.append(check(
        "prediction_hash",
        sha256(PREDICTIONS) == target_manifest["prediction_file_sha256"],
        sha256(PREDICTIONS),
    ))
    checks.append(check(
        "row_counts",
        len(predictions) == len(validated) == 60_000,
        f"predictions={len(predictions)} validated={len(validated)}",
    ))

    arithmetic_errors = []
    for source, scored in zip(predictions, validated):
        number = int(source["anchor"])
        phase_a = max(wave for wave in WAVES if number % wave == 0)
        phase_b = 14 - phase_a
        child_identity = phase_a + 2 * phase_b
        upper_reference = number + child_identity
        candidate = upper_reference + 1
        expected = {
            "phase_a": phase_a,
            "phase_b": phase_b,
            "child_identity": child_identity,
            "upper_reference": upper_reference,
            "offset": 29 - phase_a,
            "predicted_candidate": candidate,
        }
        for field, value in expected.items():
            if int(source[field]) != value:
                arithmetic_errors.append({"anchor": number, "field": field, "expected": value, "actual": source[field]})
                break
        if source["anchor"] != scored["anchor"] or source["predicted_candidate"] != scored["predicted_candidate"]:
            arithmetic_errors.append({"anchor": number, "field": "row_alignment"})
    checks.append(check(
        "all_60000_prediction_arithmetic_rows",
        not arithmetic_errors,
        f"errors={len(arithmetic_errors)}",
    ))

    example = next((row for row in [
        {
            "anchor": 35,
            "phase_a": max(wave for wave in WAVES if 35 % wave == 0),
        }
    ]), None)
    example_a = example["phase_a"]
    example_b = 14 - example_a
    example_candidate = 35 + example_a + 2 * example_b + 1
    checks.append(check(
        "worked_example_35_to_59",
        example_candidate == 59,
        f"35+{example_a}+2*{example_b}+1={example_candidate}",
    ))

    max_candidate = max(int(row["predicted_candidate"]) for row in validated)
    primes = sieve_primes(math.isqrt(max_candidate) + 1)
    sample_indices = sorted(random.Random(SAMPLE_SEED).sample(range(len(validated)), SAMPLE_SIZE))
    label_mismatches = []
    for index in sample_indices:
        row = validated[index]
        candidate = int(row["predicted_candidate"])
        independent = int(trial_is_prime(candidate, primes))
        recorded = int(row["is_prime"])
        if independent != recorded:
            label_mismatches.append({
                "row_index": index,
                "candidate": candidate,
                "recorded": recorded,
                "independent": independent,
            })
    checks.append(check(
        "independent_trial_division_sample",
        not label_mismatches,
        f"sample={SAMPLE_SIZE} seed={SAMPLE_SEED} mismatches={len(label_mismatches)}",
    ))

    odd = [row for row in validated if row["parity"] == "odd"]
    even = [row for row in validated if row["parity"] == "even"]
    odd_hits = sum(int(row["is_prime"]) for row in odd)
    odd_rate = odd_hits / len(odd)
    uniform_rate = sum(float(row["uniform_offset_prime_rate"]) for row in odd) / len(odd)
    fixed_rate = sum(int(row["fixed_plus_2_is_prime"]) for row in odd) / len(odd)
    checks.append(check(
        "headline_aggregates",
        math.isclose(odd_rate, results["odd_primary"]["ara_hit_rate"], abs_tol=1e-15)
        and math.isclose(uniform_rate, results["odd_primary"]["uniform_allowed_offset_rate"], abs_tol=1e-15)
        and math.isclose(fixed_rate, results["odd_primary"]["fixed_plus_2_rate"], abs_tol=1e-15),
        f"hits={odd_hits}/{len(odd)} ara={odd_rate:.12f} uniform={uniform_rate:.12f} fixed={fixed_rate:.12f}",
    ))
    checks.append(check(
        "even_negative_control",
        len(even) == 30_000
        and all(int(row["predicted_candidate"]) % 2 == 0 for row in even)
        and sum(int(row["is_prime"]) for row in even) == 0,
        f"n={len(even)} hits={sum(int(row['is_prime']) for row in even)}",
    ))
    checks.append(check(
        "protected_anchor_sealed",
        results["population"]["protected_87_bit_anchor_used"] is False,
        "protected 87-bit anchor was not used",
    ))

    payload = {
        "test_id": "PN27/EXACT-FIT-CHILD-LIFT/v1",
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "checks_passed": sum(item["passed"] for item in checks),
        "checks_total": len(checks),
        "all_checks_passed": all(item["passed"] for item in checks),
        "arithmetic_error_examples": arithmetic_errors[:10],
        "independent_label_mismatch_examples": label_mismatches[:10],
        "validation_scope": (
            "All 60,000 prediction rows were independently recomputed arithmetically. "
            "A deterministic 1,200-row sample of primality labels was independently checked by trial division "
            "using a locally generated prime list."
        ),
    }
    VALIDATION.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

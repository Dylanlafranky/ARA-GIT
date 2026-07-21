#!/usr/bin/env python3
"""Independent arithmetic and artifact validator for PN11 target results."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import Counter
from pathlib import Path
from statistics import mean, median


ROOT = Path(__file__).resolve().parent
PHI = (1.0 + math.sqrt(5.0)) / 2.0
WINDOW = 0.025
WIDE = 0.05
LANDMARKS = [
    ("3/2", 1.5),
    ("8/5", 1.6),
    ("phi", PHI),
    ("13/8", 13 / 8),
    ("5/3", 5 / 3),
    ("7/4", 7 / 4),
    ("9/5", 9 / 5),
    ("2", 2.0),
]
TOL = 1e-12


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def first_missing_prime(factors: set[int]) -> int:
    candidate = 2
    while True:
        if is_prime(candidate) and candidate not in factors:
            return candidate
        candidate += 1


def locked_share(base: int, multiplier: int) -> float:
    return 2.0 * math.log(base) / math.log(base * multiplier)


def close(a: float, b: float, tolerance: float = TOL) -> bool:
    return abs(a - b) <= tolerance


def main() -> None:
    freeze = json.loads((ROOT / "PN11_TARGET_FREEZE_MANIFEST.json").read_text(encoding="utf-8"))
    result = json.loads((ROOT / "PN11_TARGET_RESULTS.json").read_text(encoding="utf-8"))
    with (ROOT / "PN11_TARGET_EVENTS.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    checks: list[dict] = []

    def add(name: str, passed: bool, detail) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    frozen_hashes = {
        name: sha256(ROOT / name) for name in freeze["files"] if name != "PN11_DEVELOPMENT_RESULTS.json"
    }
    add(
        "frozen source and protocols unchanged",
        all(frozen_hashes[name] == freeze["files"][name] for name in frozen_hashes),
        frozen_hashes,
    )
    add("target interval preserved", result["range"] == [10_000_000, 11_000_000], result["range"])
    add("target family row count", len(rows) == 45_768, len(rows))

    max_product_error = 0
    max_event_error = 0.0
    max_echo_error = 0.0
    max_pre_error = 0.0
    max_closure_error = 0.0
    bad_prime_factors = 0
    bad_q = 0
    bad_fundamental = 0
    bad_expansion = 0
    q_counts: Counter[int] = Counter()
    event_values: list[float] = []
    pre_values: list[float] = []
    bases: list[int] = []
    exposures: dict[str, int] = {label: 0 for label, _ in LANDMARKS}
    events: dict[str, int] = {label: 0 for label, _ in LANDMARKS}

    for row in rows:
        base = int(row["base"])
        factors = [int(value) for value in row["factors"].split(";")]
        factor_set = set(factors)
        q = int(row["first_missing_prime"])
        event_x = float(row["event_x_old_lock"])
        event_echo = float(row["event_x_echo"])
        pre_x = float(row["last_pure_repeat_x"])

        product = math.prod(factors)
        max_product_error = max(max_product_error, abs(product - base))
        bad_prime_factors += sum(not is_prime(p) for p in factors)
        if len(factors) < 3 or len(factor_set) != len(factors) or max(factors) ** 2 > base:
            bad_fundamental += 1
        expected_q = first_missing_prime(factor_set)
        bad_q += int(q != expected_q or q < 3)
        bad_expansion += int(q in factor_set or math.prod([*factors, q]) != q * base or q * q > q * base)

        expected_event = locked_share(base, q)
        expected_echo = 2.0 * math.log(q) / math.log(q * base)
        expected_pre = locked_share(base, q - 1)
        max_event_error = max(max_event_error, abs(event_x - expected_event))
        max_echo_error = max(max_echo_error, abs(event_echo - expected_echo))
        max_pre_error = max(max_pre_error, abs(pre_x - expected_pre))
        max_closure_error = max(max_closure_error, abs(event_x + event_echo - 2.0))

        for multiplier in range(2, q + 1):
            x = locked_share(base, multiplier)
            for label, landmark in LANDMARKS:
                if abs(x - landmark) <= WINDOW:
                    exposures[label] += 1
                    events[label] += int(multiplier == q)

        q_counts[q] += 1
        event_values.append(event_x)
        pre_values.append(pre_x)
        bases.append(base)

    add("factor products reconstruct bases", max_product_error == 0, max_product_error)
    add("all declared factors independently prime", bad_prime_factors == 0, bad_prime_factors)
    add("all bases independently satisfy fundamental rule", bad_fundamental == 0, bad_fundamental)
    add("first missing primes independently recovered", bad_q == 0, bad_q)
    add("expanded locks add exactly one new child", bad_expansion == 0, bad_expansion)
    add("event coordinates independently recovered", max_event_error <= TOL, max_event_error)
    add("echo coordinates independently recovered", max_echo_error <= TOL, max_echo_error)
    add("last-repeat coordinates independently recovered", max_pre_error <= TOL, max_pre_error)
    add("event shares close at two", max_closure_error <= TOL, max_closure_error)

    add(
        "first-missing-prime counts match",
        {str(key): value for key, value in sorted(q_counts.items())}
        == result["population"]["first_missing_prime_counts"],
        dict(sorted(q_counts.items())),
    )
    phi_crosses = sum(value <= PHI for value in pre_values)
    add(
        "zero target families cross Phi before expansion",
        phi_crosses == result["population"]["phi_crossed_before_expansion_count"] == 0,
        phi_crosses,
    )

    recomputed_landmarks = []
    for label, landmark in LANDMARKS:
        distances = [abs(value - landmark) for value in event_values]
        recomputed_landmarks.append(
            {
                "landmark": label,
                "mae": mean(distances),
                "median": median(distances),
                "within_025": sum(distance <= WINDOW for distance in distances) / len(distances),
                "within_05": sum(distance <= WIDE for distance in distances) / len(distances),
                "exposures": exposures[label],
                "events": events[label],
                "hazard": events[label] / exposures[label] if exposures[label] else None,
            }
        )

    saved_by_name = {item["landmark"]: item for item in result["landmarks"]}
    metric_mismatches = 0
    for item in recomputed_landmarks:
        saved = saved_by_name[item["landmark"]]
        comparisons = [
            close(item["mae"], saved["mean_absolute_event_distance"]),
            close(item["median"], saved["median_absolute_event_distance"]),
            close(item["within_025"], saved["event_fraction_within_0_025"]),
            close(item["within_05"], saved["event_fraction_within_0_05"]),
            item["exposures"] == saved["window_exposures"],
            item["events"] == saved["window_transition_events"],
            (item["hazard"] is None and saved["window_transition_hazard"] is None)
            or close(item["hazard"], saved["window_transition_hazard"]),
        ]
        metric_mismatches += sum(not value for value in comparisons)
    add("all landmark metrics independently replayed", metric_mismatches == 0, metric_mismatches)

    distance_order = sorted(recomputed_landmarks, key=lambda item: item["mae"])
    add("9/5 is nearest frozen landmark", distance_order[0]["landmark"] == "9/5", distance_order[0])
    phi_distance_rank = next(i for i, item in enumerate(distance_order, 1) if item["landmark"] == "phi")
    add("Phi distance rank is six", phi_distance_rank == 6, phi_distance_rank)

    eligible_hazards = sorted(
        (item for item in recomputed_landmarks if item["events"] >= 30),
        key=lambda item: item["hazard"],
        reverse=True,
    )
    add(
        "Phi hazard window has zero events and exposures",
        events["phi"] == 0 and exposures["phi"] == 0,
        {"events": events["phi"], "exposures": exposures["phi"]},
    )
    add("9/5 has highest eligible hazard", eligible_hazards[0]["landmark"] == "9/5", eligible_hazards)

    best = next(item for item in recomputed_landmarks if item["landmark"] == "9/5")
    phi_item = next(item for item in recomputed_landmarks if item["landmark"] == "phi")
    observed_advantage = best["mae"] - phi_item["mae"]
    add(
        "reported paired mean-loss difference",
        close(observed_advantage, result["bootstrap"]["observed_best_rival_minus_phi_mae"]),
        observed_advantage,
    )

    # Independent fixed-seed block bootstrap replay.
    block_count = 100
    start, end = result["range"]
    width = (end - start) / block_count
    blocks = []
    for index in range(block_count):
        low = start + index * width
        high = start + (index + 1) * width
        diffs = [
            abs(x - 1.8) - abs(x - PHI)
            for base, x in zip(bases, event_values)
            if low <= base < high
        ]
        blocks.append((sum(diffs), len(diffs)))
    rng = random.Random(23711)
    draws = []
    for _ in range(2000):
        sample = [blocks[rng.randrange(block_count)] for _ in range(block_count)]
        draws.append(sum(total for total, _ in sample) / sum(count for _, count in sample))
    draws.sort()
    ci = (draws[50], draws[1949])
    add(
        "block-bootstrap interval replayed",
        close(ci[0], result["bootstrap"]["ci95_low"])
        and close(ci[1], result["bootstrap"]["ci95_high"]),
        ci,
    )

    add("P1 passes", result["criteria"]["P1_exact_geometry"] is True, result["criteria"])
    add("P2 fails", result["criteria"]["P2_phi_event_location"] is False, result["criteria"])
    add("P3 is underpopulated", result["criteria"]["P3_phi_transition_hazard"] is None, result["criteria"])
    add("P4 fails", result["criteria"]["P4_split_half_direction"] is False, result["criteria"])
    add("registered target verdict is NOT_SUPPORTED", result["status"] == "NOT_SUPPORTED", result["status"])

    validation = {
        "artifact": "PN11 Phi vertical handover independent validation",
        "date": "2026-07-21",
        "checks_passed": sum(item["passed"] for item in checks),
        "checks_total": len(checks),
        "all_passed": all(item["passed"] for item in checks),
        "checks": checks,
    }
    (ROOT / "PN11_PHI_VERTICAL_HANDOVER_VALIDATION.json").write_text(
        json.dumps(validation, indent=2), encoding="utf-8"
    )
    print(json.dumps(validation, indent=2))
    if not validation["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()


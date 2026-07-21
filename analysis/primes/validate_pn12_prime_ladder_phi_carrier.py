#!/usr/bin/env python3
"""Independent-algorithm validation for PN12 target artifacts.

This validator deliberately avoids the primary script's sieve and growing primorial.
It generates primes by trial division and recomputes each parent residue directly as
a modular product. It validates arithmetic and reporting; it is not an independent
scientific replication.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "PN12_TARGET_RESULTS.json"
STEPS_PATH = HERE / "PN12_TARGET_STEPS.csv"
PHI = (1.0 + math.sqrt(5.0)) / 2.0
LANDMARKS = {
    "golden_angle": 1.0 / PHI**2,
    "thirty_six": 0.1,
    "reverse_golden": 1.0 / PHI,
    "one_over_e": 1.0 / math.e,
    "three_eighths": 3.0 / 8.0,
    "two_fifths": 2.0 / 5.0,
    "one_fifth": 1.0 / 5.0,
    "one_sixth": 1.0 / 6.0,
    "one_quarter": 1.0 / 4.0,
    "one_third": 1.0 / 3.0,
    "one_half": 1.0 / 2.0,
    "zero": 0.0,
}


def primes_by_trial_division(count: int) -> list[int]:
    primes: list[int] = []
    candidate = 2
    while len(primes) < count:
        root = math.isqrt(candidate)
        is_prime = True
        for prime in primes:
            if prime > root:
                break
            if candidate % prime == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
        candidate = 3 if candidate == 2 else candidate + 2
    return primes


def circular_distance(a: float, b: float) -> float:
    gap = abs((a - b) % 1.0)
    return min(gap, 1.0 - gap)


def circular_summary(values: list[float]) -> dict[str, float]:
    cosine = sum(math.cos(2.0 * math.pi * value) for value in values) / len(values)
    sine = sum(math.sin(2.0 * math.pi * value) for value in values) / len(values)
    direction = (math.atan2(sine, cosine) / (2.0 * math.pi)) % 1.0
    return {
        "mean_direction_turn": direction,
        "mean_direction_degrees": direction * 360.0,
        "resultant_length": math.hypot(cosine, sine),
    }


def direct_modular_phases(primes: list[int], start_m: int, end_m: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for m in range(start_m, end_m + 1):
        next_prime = primes[m]
        residue = 1
        for prime in primes[:m]:
            residue = (residue * prime) % next_prime
        rows.append(
            {
                "m": m,
                "current_prime": primes[m - 1],
                "next_prime": next_prime,
                "residue": residue,
                "phase_turn": residue / next_prime,
            }
        )
    return rows


def check(name: str, condition: bool, detail: str) -> dict[str, Any]:
    return {"name": name, "pass": bool(condition), "detail": detail}


def main() -> None:
    saved_result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    with STEPS_PATH.open(newline="", encoding="utf-8") as handle:
        saved_steps = list(csv.DictReader(handle))

    primes = primes_by_trial_division(5001)
    phases = direct_modular_phases(primes, 1000, 5000)
    deltas = [
        (right["phase_turn"] - left["phase_turn"]) % 1.0
        for left, right in zip(phases, phases[1:])
    ]
    circular = circular_summary(deltas)
    losses = {
        name: sum(circular_distance(value, landmark) for value in deltas) / len(deltas)
        for name, landmark in LANDMARKS.items()
    }
    ranks = {
        name: rank
        for rank, (name, _) in enumerate(sorted(losses.items(), key=lambda item: (item[1], item[0])), start=1)
    }

    checks: list[dict[str, Any]] = []
    checks.append(check("target_row_count", len(saved_steps) == 4000, f"saved={len(saved_steps)} expected=4000"))
    checks.append(check("prime_count", len(primes) == 5001, f"generated={len(primes)}"))

    residue_mismatches = 0
    phase_mismatches = 0
    delta_mismatches = 0
    for index, saved in enumerate(saved_steps):
        computed = phases[index]
        if (
            int(saved["m"]) != computed["m"]
            or int(saved["current_prime"]) != computed["current_prime"]
            or int(saved["next_prime"]) != computed["next_prime"]
            or int(saved["residue"]) != computed["residue"]
        ):
            residue_mismatches += 1
        if abs(float(saved["phase_turn"]) - computed["phase_turn"]) > 1e-15:
            phase_mismatches += 1
        if abs(float(saved["delta_turn"]) - deltas[index]) > 1e-15:
            delta_mismatches += 1
    checks.extend(
        [
            check("direct_modular_residues", residue_mismatches == 0, f"mismatches={residue_mismatches}"),
            check("direct_phase_values", phase_mismatches == 0, f"mismatches={phase_mismatches}"),
            check("direct_phase_increments", delta_mismatches == 0, f"mismatches={delta_mismatches}"),
        ]
    )

    saved_circular = saved_result["circular_increment"]
    checks.extend(
        [
            check(
                "resultant_length",
                abs(circular["resultant_length"] - saved_circular["resultant_length"]) < 1e-14,
                f"computed={circular['resultant_length']:.15g} saved={saved_circular['resultant_length']:.15g}",
            ),
            check(
                "mean_direction",
                circular_distance(circular["mean_direction_turn"], saved_circular["mean_direction_turn"]) < 1e-14,
                f"computed={circular['mean_direction_turn']:.15g} saved={saved_circular['mean_direction_turn']:.15g}",
            ),
        ]
    )

    saved_landmarks = {row["name"]: row for row in saved_result["landmarks"]}
    for name in LANDMARKS:
        checks.append(
            check(
                f"landmark_{name}",
                abs(losses[name] - saved_landmarks[name]["mean_circular_distance"]) < 1e-14
                and ranks[name] == saved_landmarks[name]["rank"],
                f"loss={losses[name]:.15g} rank={ranks[name]}",
            )
        )

    golden_saved = saved_result["primary_golden_verdict"]
    thirty_six_saved = saved_result["secondary_thirty_six_verdict"]
    checks.extend(
        [
            check(
                "golden_verdict_reconstruction",
                golden_saved["verdict"] == "NOT SUPPORTED"
                and not all(golden_saved["checks"].values())
                and ranks["golden_angle"] == 9,
                f"verdict={golden_saved['verdict']} rank={ranks['golden_angle']}",
            ),
            check(
                "thirty_six_verdict_reconstruction",
                thirty_six_saved["verdict"] == "NOT SUPPORTED"
                and not all(thirty_six_saved["checks"].values())
                and ranks["thirty_six"] == 1
                and circular["resultant_length"] < 0.10,
                (
                    f"verdict={thirty_six_saved['verdict']} rank={ranks['thirty_six']} "
                    f"R={circular['resultant_length']:.9g}"
                ),
            ),
            check(
                "near_uniform_mean_distance",
                max(abs(loss - 0.25) for loss in losses.values()) < 0.004,
                f"max_abs_from_uniform_0.25={max(abs(loss - 0.25) for loss in losses.values()):.9g}",
            ),
        ]
    )

    validation = {
        "test_id": "PN12/PRIME-LADDER-ANGULAR-CARRIER/v1",
        "validator": "trial-division primes plus direct modular products; no growing primorial",
        "scientific_replication": False,
        "checks_passed": sum(item["pass"] for item in checks),
        "checks_total": len(checks),
        "all_pass": all(item["pass"] for item in checks),
        "recomputed": {
            "increment_count": len(deltas),
            "circular": circular,
            "landmark_losses": losses,
            "landmark_ranks": ranks,
        },
        "checks": checks,
    }
    output = HERE / "PN12_PHI_CARRIER_VALIDATION.json"
    output.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PN12 validation: {validation['checks_passed']}/{validation['checks_total']} checks pass")
    print(f"wrote {output.name}")
    if not validation["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()


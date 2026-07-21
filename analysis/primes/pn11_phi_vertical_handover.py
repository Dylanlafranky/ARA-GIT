#!/usr/bin/env python3
"""PN11: registered Phi vertical-handover test on exact prime resonance families.

Protocol: PN11_PHI_VERTICAL_HANDOVER_PROTOCOL.md
Data: complete deterministic integer intervals declared in the protocol; no external files.
Development and target stages are deliberately separate. The target must not be run until this
source has been frozen and hashed after development.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from array import array
from pathlib import Path
from statistics import mean, median


ROOT = Path(__file__).resolve().parent
PHI = (1.0 + math.sqrt(5.0)) / 2.0
WINDOW = 0.025
WIDE_WINDOW = 0.05
BOOTSTRAP_DRAWS = 2000
BOOTSTRAP_SEED = 23711
BLOCK_COUNT = 100

STAGES = {
    "development": (5_000, 1_000_000),
    "target": (10_000_000, 11_000_000),
}

LANDMARKS = [
    ("3/2", 1.5),
    ("8/5", 1.6),
    ("phi", PHI),
    ("13/8", 13.0 / 8.0),
    ("5/3", 5.0 / 3.0),
    ("7/4", 1.75),
    ("9/5", 1.8),
    ("2", 2.0),
]


def build_spf(limit: int) -> array:
    """Return smallest-prime-factor array; zero entries above 1 are prime."""
    spf = array("I", [0]) * (limit + 1)
    for p in range(2, math.isqrt(limit) + 1):
        if spf[p] != 0:
            continue
        for multiple in range(p * p, limit + 1, p):
            if spf[multiple] == 0:
                spf[multiple] = p
    return spf


def factor_with_spf(n: int, spf: array) -> tuple[list[int], bool]:
    factors: list[int] = []
    squarefree = True
    value = n
    while value > 1:
        p = int(spf[value]) if spf[value] else value
        exponent = 0
        while value % p == 0:
            value //= p
            exponent += 1
        factors.append(p)
        if exponent > 1:
            squarefree = False
    return factors, squarefree


def small_primes(limit: int = 100) -> list[int]:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for p in range(2, math.isqrt(limit) + 1):
        if flags[p]:
            flags[p * p : limit + 1 : p] = b"\x00" * (((limit - p * p) // p) + 1)
    return [i for i in range(2, limit + 1) if flags[i]]


PRIMES = small_primes()


def first_missing_prime(factors: list[int]) -> int:
    factor_set = set(factors)
    for p in PRIMES:
        if p not in factor_set:
            return p
    raise RuntimeError("small-prime table exhausted")


def ara_shares(base: int, multiplier: int) -> tuple[float, float]:
    whole_log = math.log(base * multiplier)
    locked = 2.0 * math.log(base) / whole_log
    echo = 2.0 * math.log(multiplier) / whole_log
    return locked, echo


def quantiles(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    if not ordered:
        return {}

    def q(probability: float) -> float:
        pos = probability * (len(ordered) - 1)
        lo = int(math.floor(pos))
        hi = int(math.ceil(pos))
        if lo == hi:
            return ordered[lo]
        weight = pos - lo
        return ordered[lo] * (1.0 - weight) + ordered[hi] * weight

    return {
        "min": ordered[0],
        "q05": q(0.05),
        "q25": q(0.25),
        "median": q(0.50),
        "q75": q(0.75),
        "q95": q(0.95),
        "max": ordered[-1],
        "mean": mean(ordered),
    }


def enumerate_families(start: int, end: int) -> tuple[list[dict], list[dict], dict]:
    spf = build_spf(end - 1)
    primary: list[dict] = []
    all_fundamental: list[dict] = []
    max_closure_error = 0.0
    pure_repeat_failures = 0
    expansion_failures = 0

    for base in range(start, end):
        factors, squarefree = factor_with_spf(base, spf)
        if not squarefree or len(factors) < 3 or factors[-1] * factors[-1] > base:
            continue

        missing = first_missing_prime(factors)
        event_x, event_echo = ara_shares(base, missing)
        pre_x = 2.0 if missing == 2 else ara_shares(base, missing - 1)[0]
        path: list[tuple[int, float, float, int]] = []

        for multiplier in range(2, missing + 1):
            locked, echo = ara_shares(base, multiplier)
            max_closure_error = max(max_closure_error, abs(locked + echo - 2.0))
            transition = int(multiplier == missing)
            path.append((multiplier, locked, echo, transition))

            if multiplier < missing:
                # Every prime factor below the first missing prime is already in the lock.
                probe = multiplier
                for p in factors:
                    while probe % p == 0:
                        probe //= p
                if probe != 1:
                    pure_repeat_failures += 1

        # q is prime, absent from squarefree B, active at qB, and adds exactly one child.
        if missing in factors or missing * missing > missing * base:
            expansion_failures += 1

        row = {
            "base": base,
            "factors": factors,
            "voice_count": len(factors),
            "first_missing_prime": missing,
            "harmonic_repeat_count": max(0, missing - 2),
            "event_x_old_lock": event_x,
            "event_x_echo": event_echo,
            "last_pure_repeat_x": pre_x,
            "phi_crossed_before_expansion": bool(missing > 2 and pre_x <= PHI),
            "path": path,
        }
        all_fundamental.append(row)
        if missing >= 3:
            primary.append(row)

    checks = {
        "max_closure_error": max_closure_error,
        "pure_repeat_failures": pure_repeat_failures,
        "expansion_failures": expansion_failures,
    }
    return primary, all_fundamental, checks


def landmark_table(rows: list[dict]) -> list[dict]:
    event_values = [row["event_x_old_lock"] for row in rows]
    output: list[dict] = []
    for label, value in LANDMARKS:
        distances = [abs(x - value) for x in event_values]
        exposures = 0
        events = 0
        for row in rows:
            for _, locked, _, transition in row["path"]:
                if abs(locked - value) <= WINDOW:
                    exposures += 1
                    events += transition
        output.append(
            {
                "landmark": label,
                "value": value,
                "mean_absolute_event_distance": mean(distances),
                "median_absolute_event_distance": median(distances),
                "event_fraction_within_0_025": sum(d <= WINDOW for d in distances) / len(distances),
                "event_fraction_within_0_05": sum(d <= WIDE_WINDOW for d in distances) / len(distances),
                "window_exposures": exposures,
                "window_transition_events": events,
                "window_transition_hazard": events / exposures if exposures else None,
            }
        )

    by_distance = sorted(output, key=lambda item: item["mean_absolute_event_distance"])
    for rank, item in enumerate(by_distance, start=1):
        item["mean_distance_rank"] = rank
    for item in output:
        item["hazard_rank"] = None
    by_hazard = sorted(
        (item for item in output if item["window_transition_events"] >= 30),
        key=lambda item: item["window_transition_hazard"],
        reverse=True,
    )
    for rank, item in enumerate(by_hazard, start=1):
        item["hazard_rank"] = rank
    return output


def best_rival(table: list[dict]) -> dict:
    return min(
        (item for item in table if item["landmark"] != "phi"),
        key=lambda item: item["mean_absolute_event_distance"],
    )


def block_bootstrap_advantage(
    rows: list[dict], start: int, end: int, rival_value: float
) -> dict[str, float]:
    width = (end - start) / BLOCK_COUNT
    blocks: list[tuple[float, int]] = []
    for block_index in range(BLOCK_COUNT):
        low = start + block_index * width
        high = start + (block_index + 1) * width
        values = [
            abs(row["event_x_old_lock"] - rival_value) - abs(row["event_x_old_lock"] - PHI)
            for row in rows
            if low <= row["base"] < high
        ]
        blocks.append((sum(values), len(values)))

    observed = sum(total for total, _ in blocks) / sum(count for _, count in blocks)
    rng = random.Random(BOOTSTRAP_SEED)
    draws: list[float] = []
    for _ in range(BOOTSTRAP_DRAWS):
        sampled = [blocks[rng.randrange(BLOCK_COUNT)] for _ in range(BLOCK_COUNT)]
        count = sum(item[1] for item in sampled)
        draws.append(sum(item[0] for item in sampled) / count)
    draws.sort()
    return {
        "observed_best_rival_minus_phi_mae": observed,
        "ci95_low": draws[int(0.025 * BOOTSTRAP_DRAWS)],
        "ci95_high": draws[int(0.975 * BOOTSTRAP_DRAWS) - 1],
        "draws": BOOTSTRAP_DRAWS,
        "blocks": BLOCK_COUNT,
        "seed": BOOTSTRAP_SEED,
    }


def half_summary(rows: list[dict], start: int, end: int) -> dict:
    midpoint = (start + end) // 2
    result = {}
    for label, subset in (
        ("first_half", [row for row in rows if row["base"] < midpoint]),
        ("second_half", [row for row in rows if row["base"] >= midpoint]),
    ):
        table = landmark_table(subset)
        phi_row = next(item for item in table if item["landmark"] == "phi")
        rival = best_rival(table)
        eligible_hazards = [item for item in table if item["window_transition_events"] >= 30]
        result[label] = {
            "n": len(subset),
            "phi_mean_distance_rank": phi_row["mean_distance_rank"],
            "phi_hazard_rank": phi_row["hazard_rank"],
            "phi_hazard_events": phi_row["window_transition_events"],
            "eligible_hazard_windows": len(eligible_hazards),
            "best_rival": rival["landmark"],
            "best_rival_minus_phi_mae": (
                rival["mean_absolute_event_distance"] - phi_row["mean_absolute_event_distance"]
            ),
        }
    return result


def primorial_ladder(limit: int) -> list[dict]:
    result = []
    base = 1
    factors: list[int] = []
    for p in PRIMES:
        base *= p
        factors.append(p)
        if len(factors) < 3:
            continue
        if base > limit:
            break
        q = next(candidate for candidate in PRIMES if candidate not in factors)
        event_x, event_echo = ara_shares(base, q)
        pre_x = ara_shares(base, q - 1)[0]
        result.append(
            {
                "base": base,
                "factors": list(factors),
                "next_prime": q,
                "event_x_old_lock": event_x,
                "event_x_echo": event_echo,
                "last_pure_repeat_x": pre_x,
                "phi_crossed_before_expansion": pre_x <= PHI,
                "phi_event_distance": abs(event_x - PHI),
            }
        )
    return result


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name) for name in fieldnames})


def run(stage: str) -> dict:
    start, end = STAGES[stage]
    rows, all_rows, checks = enumerate_families(start, end)
    table = landmark_table(rows)
    phi_row = next(item for item in table if item["landmark"] == "phi")
    rival = best_rival(table)
    halves = half_summary(rows, start, end)
    bootstrap = block_bootstrap_advantage(rows, start, end, rival["value"])

    event_count_adequate = len(rows) >= 1_000
    eligible_hazards = [item for item in table if item["window_transition_events"] >= 30]
    window_counts_adequate = (
        phi_row["window_transition_events"] >= 30
        and sum(item["landmark"] != "phi" for item in eligible_hazards) >= 2
        and all(
            item["phi_hazard_events"] >= 30 and item["eligible_hazard_windows"] >= 3
            for item in halves.values()
        )
    )
    p1 = (
        checks["max_closure_error"] <= 1e-12
        and checks["pure_repeat_failures"] == 0
        and checks["expansion_failures"] == 0
    )
    p2 = (
        phi_row["mean_distance_rank"] == 1
        and bootstrap["ci95_low"] > 0.0
    )
    p3 = (
        window_counts_adequate
        and phi_row["hazard_rank"] == 1
        and all(item["phi_hazard_rank"] == 1 for item in halves.values())
    )
    p4 = all(item["best_rival_minus_phi_mae"] > 0.0 for item in halves.values())

    if not p1:
        rating = "IMPLEMENTATION_FAILURE"
    elif not event_count_adequate:
        rating = "INCONCLUSIVE"
    elif not p2 or not p4:
        rating = "NOT_SUPPORTED"
    elif not window_counts_adequate:
        rating = "INCONCLUSIVE"
    elif p2 and p3 and p4:
        rating = "SUPPORTED"
    else:
        rating = "NOT_SUPPORTED"

    event_values = [row["event_x_old_lock"] for row in rows]
    pre_values = [row["last_pure_repeat_x"] for row in rows]
    missing_values = [float(row["first_missing_prime"]) for row in rows]
    q_counts: dict[str, int] = {}
    for row in rows:
        key = str(row["first_missing_prime"])
        q_counts[key] = q_counts.get(key, 0) + 1

    result = {
        "test_id": "PN11/PHI-VERTICAL-HANDOVER/v1",
        "stage": stage,
        "range": [start, end],
        "status": rating,
        "constants": {
            "phi": PHI,
            "phi_mirror": 2.0 - PHI,
            "window": WINDOW,
            "wide_window": WIDE_WINDOW,
        },
        "population": {
            "eligible_primary_q_ge_3": len(rows),
            "all_fundamental_including_q_2": len(all_rows),
            "phi_crossed_before_expansion_count": sum(
                row["phi_crossed_before_expansion"] for row in rows
            ),
            "phi_crossed_before_expansion_fraction": sum(
                row["phi_crossed_before_expansion"] for row in rows
            )
            / len(rows),
            "first_missing_prime_counts": q_counts,
        },
        "geometry": {
            "event_x_distribution": quantiles(event_values),
            "last_pure_repeat_x_distribution": quantiles(pre_values),
            "first_missing_prime_distribution": quantiles(missing_values),
            "checks": checks,
            "primorial_prefix_ladder": primorial_ladder(end - 1),
        },
        "landmarks": table,
        "best_rival": rival,
        "bootstrap": bootstrap,
        "split_halves": halves,
        "criteria": {
            "P1_exact_geometry": p1,
            "P2_phi_event_location": p2,
            "P3_phi_transition_hazard": p3 if window_counts_adequate else None,
            "P3_window_counts_adequate": window_counts_adequate,
            "P4_split_half_direction": p4,
        },
    }

    prefix = "PN11_DEVELOPMENT" if stage == "development" else "PN11_TARGET"
    json_path = ROOT / f"{prefix}_RESULTS.json"
    events_path = ROOT / f"{prefix}_EVENTS.csv"
    landmarks_path = ROOT / f"{prefix}_LANDMARKS.csv"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_csv(
        events_path,
        [
            {
                **row,
                "factors": ";".join(map(str, row["factors"])),
                "path": "",
            }
            for row in rows
        ],
        [
            "base",
            "factors",
            "voice_count",
            "first_missing_prime",
            "harmonic_repeat_count",
            "event_x_old_lock",
            "event_x_echo",
            "last_pure_repeat_x",
            "phi_crossed_before_expansion",
        ],
    )
    write_csv(
        landmarks_path,
        table,
        [
            "landmark",
            "value",
            "mean_absolute_event_distance",
            "median_absolute_event_distance",
            "event_fraction_within_0_025",
            "event_fraction_within_0_05",
            "window_exposures",
            "window_transition_events",
            "window_transition_hazard",
            "mean_distance_rank",
            "hazard_rank",
        ],
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=sorted(STAGES), required=True)
    args = parser.parse_args()
    result = run(args.stage)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

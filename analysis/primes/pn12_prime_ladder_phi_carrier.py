#!/usr/bin/env python3
"""PN12: test a natural angular carrier on the canonical prime ladder.

Source data: deterministic positive integers and exact prime arithmetic; no external
dataset or download. Protocol and target ranges were frozen on 21 July 2026 before
opening the target. The target stage refuses to run unless its freeze manifest hashes
match and the explicit unlock token is supplied.

Orientation: up = add the next prime child. Circular direction = increasing
normalised phase on the next child's cycle.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
from pathlib import Path
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
PHI = (1.0 + math.sqrt(5.0)) / 2.0
GOLDEN_TURN = 1.0 / (PHI * PHI)
DEVELOPMENT_RANGE = (30, 999)
TARGET_RANGE = (1000, 5000)
TARGET_UNLOCK = "PN12_TARGET_FROZEN"
PERMUTATIONS = 500
BOOTSTRAPS = 5000
BOOTSTRAP_BLOCKS = 100
SEED = 12072126

LANDMARKS: list[tuple[str, float, str]] = [
    ("golden_angle", GOLDEN_TURN, "primary signed horse: 137.507764 degrees"),
    ("thirty_six", 1.0 / 10.0, "pre-registered secondary: 36 degrees"),
    ("reverse_golden", 1.0 / PHI, "reverse orientation: 222.492236 degrees"),
    ("one_over_e", 1.0 / math.e, "exponential null rival"),
    ("three_eighths", 3.0 / 8.0, "crowded rational rival: 135 degrees"),
    ("two_fifths", 2.0 / 5.0, "pentagram/rational rival: 144 degrees"),
    ("one_fifth", 1.0 / 5.0, "pentagon rival: 72 degrees"),
    ("one_sixth", 1.0 / 6.0, "hexagon rival: 60 degrees"),
    ("one_quarter", 1.0 / 4.0, "quadrant rival: 90 degrees"),
    ("one_third", 1.0 / 3.0, "triangle rival: 120 degrees"),
    ("one_half", 1.0 / 2.0, "anti-phase rival: 180 degrees"),
    ("zero", 0.0, "no-rotation rival"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile(sorted_values: Sequence[float], probability: float) -> float:
    if not sorted_values:
        raise ValueError("percentile requires at least one value")
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    position = probability * (len(sorted_values) - 1)
    lo = int(math.floor(position))
    hi = int(math.ceil(position))
    if lo == hi:
        return float(sorted_values[lo])
    weight = position - lo
    return float(sorted_values[lo] * (1.0 - weight) + sorted_values[hi] * weight)


def distribution(values: Sequence[float]) -> dict[str, float | int]:
    ordered = sorted(float(value) for value in values)
    return {
        "n": len(ordered),
        "min": ordered[0],
        "p05": percentile(ordered, 0.05),
        "p25": percentile(ordered, 0.25),
        "median": percentile(ordered, 0.50),
        "mean": statistics.fmean(ordered),
        "p75": percentile(ordered, 0.75),
        "p95": percentile(ordered, 0.95),
        "max": ordered[-1],
    }


def circular_distance(a: float, b: float) -> float:
    gap = abs((a - b) % 1.0)
    return min(gap, 1.0 - gap)


def circular_summary(values: Sequence[float]) -> dict[str, float]:
    if not values:
        raise ValueError("circular summary requires values")
    cosine = statistics.fmean(math.cos(2.0 * math.pi * value) for value in values)
    sine = statistics.fmean(math.sin(2.0 * math.pi * value) for value in values)
    resultant = math.hypot(cosine, sine)
    direction = (math.atan2(sine, cosine) / (2.0 * math.pi)) % 1.0
    return {
        "mean_direction_turn": direction,
        "mean_direction_degrees": 360.0 * direction,
        "resultant_length": resultant,
        "circular_variance": 1.0 - resultant,
    }


def first_n_primes(count: int) -> list[int]:
    if count < 1:
        return []
    if count < 6:
        limit = 15
    else:
        limit = int(count * (math.log(count) + math.log(math.log(count)))) + 20
    while True:
        sieve = bytearray(b"\x01") * (limit + 1)
        sieve[0:2] = b"\x00\x00"
        for number in range(2, math.isqrt(limit) + 1):
            if sieve[number]:
                start = number * number
                sieve[start : limit + 1 : number] = b"\x00" * (((limit - start) // number) + 1)
        primes = [index for index, is_prime in enumerate(sieve) if is_prime]
        if len(primes) >= count:
            return primes[:count]
        limit *= 2


def build_phases(start_m: int, end_m: int) -> list[dict[str, Any]]:
    primes = first_n_primes(end_m + 1)
    parent = 1
    rows: list[dict[str, Any]] = []
    for m in range(1, end_m + 1):
        current_prime = primes[m - 1]
        parent *= current_prime
        if m < start_m:
            continue
        next_prime = primes[m]
        residue = parent % next_prime
        phase = residue / next_prime
        rows.append(
            {
                "m": m,
                "current_prime": current_prime,
                "next_prime": next_prime,
                "residue": residue,
                "phase_turn": phase,
                "phase_degrees": 360.0 * phase,
                "ara_phase_x": 2.0 * phase,
            }
        )
    return rows


def build_steps(phases: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for left, right in zip(phases, phases[1:]):
        delta = (right["phase_turn"] - left["phase_turn"]) % 1.0
        row = dict(left)
        row.update(
            {
                "next_m": right["m"],
                "next_phase_turn": right["phase_turn"],
                "delta_turn": delta,
                "delta_degrees": 360.0 * delta,
            }
        )
        for name, value, _ in LANDMARKS:
            row[f"distance_{name}"] = circular_distance(delta, value)
        rows.append(row)
    return rows


def landmark_table(deltas: Sequence[float]) -> list[dict[str, Any]]:
    table: list[dict[str, Any]] = []
    for name, value, role in LANDMARKS:
        distances = [circular_distance(delta, value) for delta in deltas]
        table.append(
            {
                "name": name,
                "turn": value,
                "degrees": value * 360.0,
                "role": role,
                "mean_circular_distance": statistics.fmean(distances),
                "median_circular_distance": statistics.median(distances),
                "within_0_025_turn": sum(distance <= 0.025 for distance in distances),
            }
        )
    table.sort(key=lambda row: (row["mean_circular_distance"], row["name"]))
    for rank, row in enumerate(table, start=1):
        row["rank"] = rank
    return table


def fixed_half_results(deltas: Sequence[float]) -> list[dict[str, Any]]:
    midpoint = len(deltas) // 2
    halves = [("first", deltas[:midpoint]), ("second", deltas[midpoint:])]
    output: list[dict[str, Any]] = []
    for label, values in halves:
        output.append(
            {
                "half": label,
                "circular": circular_summary(values),
                "landmarks": landmark_table(values),
            }
        )
    return output


def contiguous_blocks(values: Sequence[float], block_count: int) -> list[list[float]]:
    blocks: list[list[float]] = []
    for index in range(block_count):
        lo = round(index * len(values) / block_count)
        hi = round((index + 1) * len(values) / block_count)
        if hi > lo:
            blocks.append(list(values[lo:hi]))
    return blocks


def bootstrap_landmark_difference(
    deltas: Sequence[float],
    candidate_name: str,
    candidate_value: float,
    table: Sequence[dict[str, Any]],
    seed_offset: int,
) -> dict[str, Any]:
    rival = min(
        (row for row in table if row["name"] != candidate_name),
        key=lambda row: row["mean_circular_distance"],
    )
    blocks = contiguous_blocks(deltas, BOOTSTRAP_BLOCKS)
    rng = random.Random(SEED + seed_offset)
    differences: list[float] = []
    for _ in range(BOOTSTRAPS):
        sampled: list[float] = []
        for _ in range(len(blocks)):
            sampled.extend(blocks[rng.randrange(len(blocks))])
        sampled = sampled[: len(deltas)]
        candidate_loss = statistics.fmean(circular_distance(value, candidate_value) for value in sampled)
        rival_loss = statistics.fmean(circular_distance(value, rival["turn"]) for value in sampled)
        differences.append(rival_loss - candidate_loss)
    ordered = sorted(differences)
    return {
        "candidate": candidate_name,
        "fixed_best_rival": rival["name"],
        "observed_best_rival_loss_minus_candidate_loss": (
            rival["mean_circular_distance"]
            - next(row["mean_circular_distance"] for row in table if row["name"] == candidate_name)
        ),
        "ci95": [percentile(ordered, 0.025), percentile(ordered, 0.975)],
        "bootstrap_replicates": BOOTSTRAPS,
        "blocks": len(blocks),
    }


def permuted_order_control(phases: Sequence[float]) -> dict[str, Any]:
    rng = random.Random(SEED + 300)
    values: list[float] = []
    for _ in range(PERMUTATIONS):
        shuffled = list(phases)
        rng.shuffle(shuffled)
        deltas = [(right - left) % 1.0 for left, right in zip(shuffled, shuffled[1:])]
        values.append(circular_summary(deltas)["resultant_length"])
    ordered = sorted(values)
    return {
        "permutations": PERMUTATIONS,
        "mean_resultant_length": statistics.fmean(values),
        "p95_resultant_length": percentile(ordered, 0.95),
        "p995_resultant_length": percentile(ordered, 0.995),
        "max_resultant_length": ordered[-1],
    }


def synthetic_checks(length: int) -> dict[str, Any]:
    def phase_walk(step: float) -> list[float]:
        return [(0.173 + index * step) % 1.0 for index in range(length + 1)]

    golden_phases = phase_walk(GOLDEN_TURN)
    thirty_six_phases = phase_walk(0.1)
    rng = random.Random(SEED + 400)
    uniform_phases = [rng.random() for _ in range(length + 1)]

    def summarise(phases: Sequence[float]) -> dict[str, float]:
        deltas = [(right - left) % 1.0 for left, right in zip(phases, phases[1:])]
        return circular_summary(deltas)

    return {
        "exact_golden": summarise(golden_phases),
        "exact_thirty_six": summarise(thirty_six_phases),
        "uniform_phase_negative": summarise(uniform_phases),
    }


def candidate_verdict(
    candidate_name: str,
    candidate_value: float,
    circular: dict[str, float],
    table: Sequence[dict[str, Any]],
    halves: Sequence[dict[str, Any]],
    permutation: dict[str, Any],
    bootstrap: dict[str, Any],
) -> dict[str, Any]:
    candidate_row = next(row for row in table if row["name"] == candidate_name)
    coherence = (
        circular["resultant_length"] >= 0.10
        and circular["resultant_length"] > permutation["p995_resultant_length"]
    )
    location = candidate_row["rank"] == 1 and bootstrap["ci95"][0] > 0.0
    direction = circular_distance(circular["mean_direction_turn"], candidate_value) <= 0.025
    stability_details: list[dict[str, Any]] = []
    for half in halves:
        half_candidate = next(row for row in half["landmarks"] if row["name"] == candidate_name)
        half_pass = (
            half["circular"]["resultant_length"] >= 0.075
            and half_candidate["rank"] == 1
            and circular_distance(half["circular"]["mean_direction_turn"], candidate_value) <= 0.04
        )
        stability_details.append(
            {
                "half": half["half"],
                "pass": half_pass,
                "resultant_length": half["circular"]["resultant_length"],
                "mean_direction_turn": half["circular"]["mean_direction_turn"],
                "candidate_rank": half_candidate["rank"],
            }
        )
    stability = all(item["pass"] for item in stability_details)
    checks = {
        "carrier_coherence": coherence,
        "candidate_location": location,
        "mean_direction": direction,
        "split_half_stability": stability,
    }
    return {
        "candidate": candidate_name,
        "candidate_turn": candidate_value,
        "candidate_degrees": 360.0 * candidate_value,
        "checks": checks,
        "split_halves": stability_details,
        "verdict": "SUPPORTED" if all(checks.values()) else "NOT SUPPORTED",
    }


def closest_examples(steps: Sequence[dict[str, Any]], count: int = 5) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for name, value, _ in LANDMARKS:
        ordered = sorted(steps, key=lambda row: (circular_distance(row["delta_turn"], value), row["m"]))
        output[name] = [
            {
                "m": row["m"],
                "current_prime": row["current_prime"],
                "next_prime": row["next_prime"],
                "phase_turn": row["phase_turn"],
                "next_phase_turn": row["next_phase_turn"],
                "delta_turn": row["delta_turn"],
                "delta_degrees": row["delta_degrees"],
                "distance_turn": circular_distance(row["delta_turn"], value),
            }
            for row in ordered[:count]
        ]
    return output


def arithmetic_checks(phases: Sequence[dict[str, Any]], expected_start: int, expected_end: int) -> dict[str, Any]:
    m_values = [row["m"] for row in phases]
    bounds_ok = all(0 <= row["residue"] < row["next_prime"] for row in phases)
    nonzero_ok = all(row["residue"] != 0 for row in phases)
    phase_ok = all(abs(row["phase_turn"] - row["residue"] / row["next_prime"]) < 1e-15 for row in phases)
    return {
        "row_count": len(phases),
        "expected_row_count": expected_end - expected_start + 1,
        "contiguous_m": m_values == list(range(expected_start, expected_end + 1)),
        "residue_bounds": bounds_ok,
        "next_child_absent": nonzero_ok,
        "phase_identity": phase_ok,
        "all_pass": (
            len(phases) == expected_end - expected_start + 1
            and m_values == list(range(expected_start, expected_end + 1))
            and bounds_ok
            and nonzero_ok
            and phase_ok
        ),
    }


def verify_target_freeze() -> dict[str, Any]:
    manifest_path = HERE / "PN12_TARGET_FREEZE_MANIFEST.json"
    if not manifest_path.exists():
        raise SystemExit("Target is locked: PN12_TARGET_FREEZE_MANIFEST.json is absent")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []
    for item in manifest["files"]:
        path = HERE / item["path"] if not Path(item["path"]).is_absolute() else Path(item["path"])
        actual = sha256(path)
        checks.append(
            {
                "path": str(path),
                "expected_sha256": item["sha256"],
                "actual_sha256": actual,
                "match": actual == item["sha256"],
            }
        )
    if not all(item["match"] for item in checks):
        raise SystemExit("Target is locked: freeze-manifest hash mismatch")
    return {"manifest": str(manifest_path), "checks": checks}


def write_steps_csv(path: Path, steps: Sequence[dict[str, Any]]) -> None:
    fieldnames = list(steps[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(steps)


def analyse(stage: str) -> dict[str, Any]:
    start_m, end_m = DEVELOPMENT_RANGE if stage == "development" else TARGET_RANGE
    phases = build_phases(start_m, end_m)
    steps = build_steps(phases)
    phase_values = [row["phase_turn"] for row in phases]
    deltas = [row["delta_turn"] for row in steps]
    circular = circular_summary(deltas)
    table = landmark_table(deltas)
    halves = fixed_half_results(deltas)
    permutation = permuted_order_control(phase_values)
    synthetic = synthetic_checks(len(deltas))
    golden_bootstrap = bootstrap_landmark_difference(
        deltas, "golden_angle", GOLDEN_TURN, table, seed_offset=100
    )
    thirty_six_bootstrap = bootstrap_landmark_difference(
        deltas, "thirty_six", 0.1, table, seed_offset=200
    )
    golden = candidate_verdict(
        "golden_angle", GOLDEN_TURN, circular, table, halves, permutation, golden_bootstrap
    )
    thirty_six = candidate_verdict(
        "thirty_six", 0.1, circular, table, halves, permutation, thirty_six_bootstrap
    )
    ordered_steps = sorted(steps, key=lambda row: (row["delta_turn"], row["m"]))
    return {
        "test_id": "PN12/PRIME-LADDER-ANGULAR-CARRIER/v1",
        "stage": stage,
        "orientation": "up = add next prime child; positive circle = increasing next-child phase",
        "range": {
            "phase_m_start": start_m,
            "phase_m_end": end_m,
            "increment_m_start": steps[0]["m"],
            "increment_m_end": steps[-1]["m"],
        },
        "definitions": {
            "parent": "B_m = product of first m primes",
            "next_child": "q_m = p_(m+1)",
            "phase": "u_m = (B_m mod q_m) / q_m",
            "ara_phase": "x_m = 2 u_m",
            "increment": "delta_m = (u_(m+1) - u_m) mod 1",
        },
        "arithmetic_checks": arithmetic_checks(phases, start_m, end_m),
        "phase_distribution": distribution(phase_values),
        "increment_distribution": distribution(deltas),
        "circular_increment": circular,
        "landmarks": table,
        "permuted_order_control": permutation,
        "synthetic_instrument_checks": synthetic,
        "fixed_halves": halves,
        "golden_bootstrap": golden_bootstrap,
        "thirty_six_bootstrap": thirty_six_bootstrap,
        "primary_golden_verdict": golden,
        "secondary_thirty_six_verdict": thirty_six,
        "closest_examples": closest_examples(steps),
        "smallest_steps": ordered_steps[:10],
        "largest_steps": ordered_steps[-10:][::-1],
        "provenance": {
            "script": str(Path(__file__).resolve()),
            "script_sha256": sha256(Path(__file__).resolve()),
            "protocol": str(HERE / "PN12_PHI_CARRIER_PROTOCOL_v1_FROZEN.md"),
            "protocol_sha256": sha256(HERE / "PN12_PHI_CARRIER_PROTOCOL_v1_FROZEN.md"),
            "fidelity_packet": str(HERE / "PN12_PHI_CARRIER_FIDELITY_PACKET_v1.md"),
            "fidelity_packet_sha256": sha256(HERE / "PN12_PHI_CARRIER_FIDELITY_PACKET_v1.md"),
            "seed": SEED,
        },
        "steps": steps,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("development", "target"), default="development")
    parser.add_argument("--unlock-target", default="")
    args = parser.parse_args()

    freeze: dict[str, Any] | None = None
    if args.stage == "target":
        if args.unlock_target != TARGET_UNLOCK:
            raise SystemExit(f"Target is locked: pass --unlock-target {TARGET_UNLOCK}")
        freeze = verify_target_freeze()

    result = analyse(args.stage)
    if freeze is not None:
        result["target_freeze_verification"] = freeze

    prefix = "PN12_DEVELOPMENT" if args.stage == "development" else "PN12_TARGET"
    steps = result.pop("steps")
    csv_path = HERE / f"{prefix}_STEPS.csv"
    json_path = HERE / f"{prefix}_RESULTS.json"
    write_steps_csv(csv_path, steps)
    result["artifacts"] = {"steps_csv": str(csv_path), "results_json": str(json_path)}
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    primary = result["primary_golden_verdict"]
    secondary = result["secondary_thirty_six_verdict"]
    circ = result["circular_increment"]
    print(f"PN12 {args.stage}: {len(steps):,} rung-to-rung increments")
    print(
        "circular mean="
        f"{circ['mean_direction_turn']:.9f} turns ({circ['mean_direction_degrees']:.6f} deg), "
        f"R={circ['resultant_length']:.9f}"
    )
    print(f"golden-angle verdict: {primary['verdict']}")
    print(f"36-degree verdict: {secondary['verdict']}")
    print(f"wrote {json_path.name} and {csv_path.name}")


if __name__ == "__main__":
    main()


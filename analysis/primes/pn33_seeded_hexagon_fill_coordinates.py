"""Generate PN33 fill coordinates without calculating or scoring prime gaps.

Registered source: PN33_SEEDED_HEXAGON_FILL_PROTOCOL_v1_FROZEN.md
The coordinate layer identifies prime gates and cumulative inverse-survivor
density only. Gap summaries, controls and verdicts belong to the later scorer.

Runtime dependency: NumPy. All parameters are frozen constants below.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN33_SEEDED_HEXAGON_FILL_PROTOCOL_v1_FROZEN.md"
PROTOCOL_FREEZE = HERE / "PN33_PROTOCOL_FREEZE_MANIFEST.json"
COORDINATES = HERE / "PN33_SEEDED_HEXAGON_FILL_COORDINATES.csv"
SUMMARY = HERE / "PN33_SEEDED_HEXAGON_FILL_COORDINATE_SUMMARY.json"
PRIME_BINARY = HERE / "PN33_TARGET_PRIME_GATES_UINT32.bin"

CEILING = 200_000_000
BASELINE_SPECS = (
    ("primary", 10_000),
    ("scale_check_a", 1_000),
    ("scale_check_b", 3_000),
)
BOUNDARIES = tuple(index / 4 for index in range(1, 9))
GOLDEN_PHI = (1.0 + math.sqrt(5.0)) / 2.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def primes_up_to(limit: int) -> np.ndarray:
    """Return every prime <= limit with an odd-only Eratosthenes sieve."""
    odd_count = (limit + 1) // 2
    sieve = np.ones(odd_count, dtype=np.bool_)
    sieve[0] = False  # integer 1
    for prime in range(3, math.isqrt(limit) + 1, 2):
        if sieve[prime // 2]:
            sieve[(prime * prime) // 2 :: prime] = False
    odd_indices = np.flatnonzero(sieve)
    primes = np.empty(odd_indices.size + 1, dtype=np.uint32)
    primes[0] = 2
    primes[1:] = (2 * odd_indices + 1).astype(np.uint32)
    return primes


def nearest_index(values: np.ndarray, target: float, lower: int, upper: int) -> int:
    position = int(np.searchsorted(values, target, side="left"))
    candidates = [index for index in (position - 1, position) if lower <= index <= upper]
    return min(candidates, key=lambda index: abs(float(values[index]) - target))


def main() -> None:
    for output in (COORDINATES, SUMMARY, PRIME_BINARY):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")

    protocol_freeze = json.loads(PROTOCOL_FREEZE.read_text(encoding="utf-8"))
    if sha256(PROTOCOL) != protocol_freeze["protocol_sha256"]:
        raise RuntimeError("frozen protocol hash mismatch")
    if protocol_freeze["target_coordinates_calculated"]:
        raise RuntimeError("protocol manifest says target coordinates already existed")

    primes = primes_up_to(CEILING)
    prime_float = primes.astype(np.float64)
    log_increments = np.log1p(1.0 / (prime_float - 1.0))
    cumulative_log_d = np.cumsum(log_increments)
    log_two = math.log(2.0)

    rows: list[dict] = []
    baselines: list[dict] = []
    largest_needed_index = 0

    for name, anchor in BASELINE_SPECS:
        baseline_index = int(np.searchsorted(primes, anchor, side="left"))
        baseline_prime = int(primes[baseline_index])
        baseline_log_d = float(cumulative_log_d[baseline_index])
        completion_target = baseline_log_d + log_two
        completion_index = int(np.searchsorted(cumulative_log_d, completion_target, side="left"))
        if completion_index >= len(primes):
            raise RuntimeError(f"{name} did not complete below frozen ceiling {CEILING}")
        seed_index = baseline_index + 1
        next_seed_index = completion_index + 1
        if next_seed_index >= len(primes):
            raise RuntimeError(f"{name} lacks a post-completion seed below the frozen ceiling")
        largest_needed_index = max(largest_needed_index, next_seed_index)

        def x_at(index: int) -> float:
            return 2.0 * (float(cumulative_log_d[index]) - baseline_log_d) / log_two

        completion_ratio = math.exp(float(cumulative_log_d[completion_index]) - baseline_log_d)
        seed_prime = int(primes[seed_index])
        next_seed_prime = int(primes[next_seed_index])
        next_seed_x = 2.0 * (
            float(cumulative_log_d[next_seed_index]) - float(cumulative_log_d[completion_index])
        ) / log_two
        retained_ratio = math.exp(
            float(cumulative_log_d[next_seed_index]) - baseline_log_d
        )

        common = {
            "baseline_name": name,
            "anchor": anchor,
            "baseline_prime": baseline_prime,
            "baseline_prime_index": baseline_index,
            "completion_prime": int(primes[completion_index]),
            "completion_prime_index": completion_index,
        }

        rows.append({
            **common,
            "landmark": "baseline",
            "target_x": "0",
            "landmark_integer": baseline_prime,
            "gate_prime": baseline_prime,
            "gate_prime_index": baseline_index,
            "actual_x": 0.0,
            "raw_spacing_ratio": 1.0,
        })
        rows.append({
            **common,
            "landmark": "seed",
            "target_x": "",
            "landmark_integer": seed_prime,
            "gate_prime": seed_prime,
            "gate_prime_index": seed_index,
            "actual_x": x_at(seed_index),
            "raw_spacing_ratio": math.exp(float(cumulative_log_d[seed_index]) - baseline_log_d),
        })

        boundary_records = []
        for boundary in BOUNDARIES:
            target_log = baseline_log_d + boundary * log_two / 2.0
            gate_index = int(np.searchsorted(cumulative_log_d, target_log, side="left"))
            gate_prime = int(primes[gate_index])
            record = {
                **common,
                "landmark": "completion" if boundary == 2.0 else "band_boundary",
                "target_x": f"{boundary:.2f}",
                "landmark_integer": gate_prime,
                "gate_prime": gate_prime,
                "gate_prime_index": gate_index,
                "actual_x": x_at(gate_index),
                "raw_spacing_ratio": math.exp(float(cumulative_log_d[gate_index]) - baseline_log_d),
            }
            rows.append(record)
            boundary_records.append(record)

        phi_target = baseline_log_d + GOLDEN_PHI * log_two / 2.0
        phi_index = nearest_index(cumulative_log_d, phi_target, seed_index, completion_index)
        rows.append({
            **common,
            "landmark": "nearest_golden_phi",
            "target_x": f"{GOLDEN_PHI:.15f}",
            "landmark_integer": int(primes[phi_index]),
            "gate_prime": int(primes[phi_index]),
            "gate_prime_index": phi_index,
            "actual_x": x_at(phi_index),
            "raw_spacing_ratio": math.exp(float(cumulative_log_d[phi_index]) - baseline_log_d),
        })

        child_square = seed_prime * seed_prime
        child_square_index = int(np.searchsorted(primes, child_square, side="right")) - 1
        child_square_index = min(child_square_index, completion_index)
        rows.append({
            **common,
            "landmark": "seed_child_square",
            "target_x": "",
            "landmark_integer": child_square,
            "gate_prime": int(primes[child_square_index]),
            "gate_prime_index": child_square_index,
            "actual_x": x_at(child_square_index),
            "raw_spacing_ratio": math.exp(float(cumulative_log_d[child_square_index]) - baseline_log_d),
        })

        rows.append({
            **common,
            "landmark": "next_generation_seed",
            "target_x": "local reset",
            "landmark_integer": next_seed_prime,
            "gate_prime": next_seed_prime,
            "gate_prime_index": next_seed_index,
            "actual_x": next_seed_x,
            "raw_spacing_ratio": retained_ratio,
        })

        baselines.append({
            "baseline_name": name,
            "anchor": anchor,
            "baseline_prime": baseline_prime,
            "baseline_prime_index": baseline_index,
            "baseline_log_d": baseline_log_d,
            "seed_prime": seed_prime,
            "seed_prime_index": seed_index,
            "seed_x": x_at(seed_index),
            "seed_child_square": child_square,
            "seed_child_square_last_gate": int(primes[child_square_index]),
            "seed_child_square_x": x_at(child_square_index),
            "completion_prime": int(primes[completion_index]),
            "completion_prime_index": completion_index,
            "completion_x": x_at(completion_index),
            "completion_ratio": completion_ratio,
            "completion_overshoot": completion_ratio - 2.0,
            "next_generation_seed": next_seed_prime,
            "next_generation_seed_index": next_seed_index,
            "next_generation_local_x": next_seed_x,
            "next_generation_retained_ratio": retained_ratio,
            "nearest_phi_prime": int(primes[phi_index]),
            "nearest_phi_x": x_at(phi_index),
            "boundary_records": boundary_records,
        })

    fieldnames = list(rows[0])
    with COORDINATES.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    saved_primes = primes[: largest_needed_index + 1]
    saved_primes.astype("<u4", copy=False).tofile(PRIME_BINARY)
    payload = {
        "test_id": "PN33/SEEDED-HEXAGON-FILL/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "sieve_method": "NumPy odd-only Eratosthenes; coordinate generation only",
        "sieve_ceiling": CEILING,
        "prime_count_generated_to_ceiling": int(len(primes)),
        "prime_binary_count": int(len(saved_primes)),
        "largest_saved_prime": int(saved_primes[-1]),
        "gap_summaries_calculated": False,
        "target_outcomes_scored": False,
        "baselines": baselines,
    }
    SUMMARY.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "coordinate_file": COORDINATES.name,
        "coordinate_rows": len(rows),
        "prime_binary": PRIME_BINARY.name,
        "prime_binary_count": len(saved_primes),
        "largest_saved_prime": int(saved_primes[-1]),
        "baselines": [
            {
                "name": item["baseline_name"],
                "baseline": item["baseline_prime"],
                "completion": item["completion_prime"],
                "completion_x": item["completion_x"],
                "overshoot": item["completion_overshoot"],
            }
            for item in baselines
        ],
        "gap_summaries_calculated": False,
    }, indent=2))


if __name__ == "__main__":
    main()


"""Independent validation for PN41 prime-thalweg Phi test.

This deliberately does not reuse PN41's segmented least-factor window or cascade
routine.  It reconstructs the natural-gate walk from direct divisibility tests,
then recomputes the headline target summaries from the saved event records.
"""

from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "PN41_PRIME_THALWEG_PHI_RESULTS.json"
TERRAIN = HERE / "PN41_PRIME_THALWEG_TERRAIN.json"
VALIDATION = HERE / "PN41_PRIME_THALWEG_PHI_VALIDATION.json"

PHI_MIRROR = 2.0 - (1.0 + math.sqrt(5.0)) / 2.0
LANDMARKS = {
    "phi_mirror": PHI_MIRROR,
    "quarter": 0.25,
    "third": 1.0 / 3.0,
    "two_fifths": 0.40,
    "half": 0.50,
}


def primes_through(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[:2] = b"\x00\x00"
    for value in range(2, math.isqrt(limit) + 1):
        if sieve[value]:
            start = value * value
            sieve[start::value] = b"\x00" * (((limit - start) // value) + 1)
    return [value for value, flag in enumerate(sieve) if flag]


PRIMES = primes_through(100_000)


def least_factor(value: int) -> int:
    for prime in PRIMES:
        if prime * prime > value:
            return 0
        if value % prime == 0:
            return prime
    raise AssertionError(f"prime table did not cover sqrt({value})")


def survives(value: int, frontier: int) -> bool:
    for prime in PRIMES:
        if prime > frontier:
            return True
        if value % prime == 0:
            return value == prime
    raise AssertionError("prime table did not cover frontier")


def adjacent_survivors(value: int, frontier: int) -> tuple[int, int]:
    left = value - 1
    while not survives(left, frontier):
        left -= 1
    right = value + 1
    while not survives(right, frontier):
        right += 1
    return left, right


def independent_cascade(anchor: int) -> tuple[dict[str, int], list[dict[str, float | int]]]:
    current = anchor + 1
    while not survives(current, 2):
        current += 1
    initial = current
    frontier = 2
    events: list[dict[str, float | int]] = []
    while True:
        gate = least_factor(current)
        if gate == 0:
            break
        if gate <= frontier:
            raise AssertionError("candidate did not survive its previous gate frontier")
        frontier = gate
        left, right = adjacent_survivors(current, frontier)
        split = (current - left) / (right - left)
        events.append({
            "anchor": anchor,
            "event_index": len(events) + 1,
            "gate": gate,
            "left_survivor": left,
            "killed_candidate": current,
            "right_survivor": right,
            "left_gap": current - left,
            "right_gap": right - current,
            "full_gap": right - left,
            "split": split,
            "folded_split": min(split, 1.0 - split),
        })
        current = right
    return ({
        "anchor": anchor,
        "initial_candidate": initial,
        "final_prime": current,
        "final_delta": current - anchor,
        "handover_events": len(events),
    }, events)


def close(a: float, b: float, tolerance: float = 1e-12) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tolerance)


def summarize(anchor_rows: list[dict], event_rows: list[dict]) -> dict:
    by_anchor: dict[int, list[float]] = {int(row["anchor"]): [] for row in anchor_rows}
    for event in event_rows:
        by_anchor[int(event["anchor"])].append(float(event["folded_split"]))
    eligible = [anchor for anchor, values in by_anchor.items() if values]

    distance_by_landmark: dict[str, float] = {}
    occupancy_by_landmark: dict[str, float] = {}
    for name, landmark in LANDMARKS.items():
        per_anchor_distance = [
            statistics.fmean(abs(value - landmark) for value in by_anchor[anchor])
            for anchor in eligible
        ]
        per_anchor_occupancy = [
            statistics.fmean(abs(value - landmark) <= 0.025 for value in by_anchor[anchor])
            for anchor in eligible
        ]
        distance_by_landmark[name] = statistics.fmean(per_anchor_distance)
        occupancy_by_landmark[name] = statistics.fmean(per_anchor_occupancy)

    grid = [0.05 + index * 0.001 for index in range(451)]
    grid_scores = [
        statistics.fmean(
            statistics.fmean(abs(value - landmark) for value in by_anchor[anchor])
            for anchor in eligible
        )
        for landmark in grid
    ]
    best_grid_index = min(range(len(grid)), key=grid_scores.__getitem__)
    folds = [float(event["folded_split"]) for event in event_rows]
    return {
        "anchors_with_handover": len(eligible),
        "anchors_without_handover": len(anchor_rows) - len(eligible),
        "handover_events": len(event_rows),
        "mean_handovers_per_anchor": statistics.fmean(int(row["handover_events"]) for row in anchor_rows),
        "median_handovers_per_anchor": statistics.median(int(row["handover_events"]) for row in anchor_rows),
        "folded_split_mean": statistics.fmean(folds),
        "folded_split_median": statistics.median(folds),
        "mean_absolute_distance_by_landmark": distance_by_landmark,
        "occupancy_within_0_025_by_landmark": occupancy_by_landmark,
        "grid_optimum": grid[best_grid_index],
    }


def verify_target(name: str, payload: dict) -> dict:
    saved_anchor_rows = payload["anchor_rows"]
    saved_event_rows = payload["event_rows"]
    events_by_anchor: dict[int, list[dict]] = {}
    for event in saved_event_rows:
        events_by_anchor.setdefault(int(event["anchor"]), []).append(event)

    mismatches: list[str] = []
    for saved_anchor in saved_anchor_rows:
        anchor = int(saved_anchor["anchor"])
        rebuilt_anchor, rebuilt_events = independent_cascade(anchor)
        for key, value in rebuilt_anchor.items():
            if int(saved_anchor[key]) != int(value):
                mismatches.append(f"anchor {anchor}: {key} saved={saved_anchor[key]} rebuilt={value}")
        saved_events = events_by_anchor.get(anchor, [])
        if len(saved_events) != len(rebuilt_events):
            mismatches.append(
                f"anchor {anchor}: event count saved={len(saved_events)} rebuilt={len(rebuilt_events)}"
            )
            continue
        for saved, rebuilt in zip(saved_events, rebuilt_events):
            for key in ("event_index", "gate", "left_survivor", "killed_candidate",
                        "right_survivor", "left_gap", "right_gap", "full_gap"):
                if int(saved[key]) != int(rebuilt[key]):
                    mismatches.append(f"anchor {anchor} event {saved['event_index']}: {key} mismatch")
            for key in ("split", "folded_split"):
                if not close(float(saved[key]), float(rebuilt[key])):
                    mismatches.append(f"anchor {anchor} event {saved['event_index']}: {key} mismatch")

    recomputed = summarize(saved_anchor_rows, saved_event_rows)
    saved_summary = payload["summary"]
    summary_checks: dict[str, bool] = {}
    for key in (
        "anchors_with_handover", "anchors_without_handover", "handover_events",
        "mean_handovers_per_anchor", "median_handovers_per_anchor",
        "folded_split_mean", "folded_split_median",
    ):
        summary_checks[key] = close(float(recomputed[key]), float(saved_summary[key]))
    for section in ("mean_absolute_distance_by_landmark", "occupancy_within_0_025_by_landmark"):
        for landmark in LANDMARKS:
            summary_checks[f"{section}.{landmark}"] = close(
                float(recomputed[section][landmark]),
                float(saved_summary[section][landmark]),
            )
    summary_checks["grid_optimum.landmark"] = close(
        float(recomputed["grid_optimum"]),
        float(saved_summary["grid_optimum"]["landmark"]),
    )

    first_prime_checks = []
    for row in saved_anchor_rows:
        anchor = int(row["anchor"])
        final_prime = int(row["final_prime"])
        first_prime_checks.append(
            least_factor(final_prime) == 0
            and all(least_factor(candidate) != 0 for candidate in range(anchor + 1, final_prime))
        )

    return {
        "target": name,
        "anchors_reconstructed": len(saved_anchor_rows),
        "events_reconstructed": len(saved_event_rows),
        "cascade_mismatch_count": len(mismatches),
        "first_mismatches": mismatches[:20],
        "all_final_values_are_first_primes_after_anchor": all(first_prime_checks),
        "summary_checks": summary_checks,
        "all_summary_checks_pass": all(summary_checks.values()),
        "pass": not mismatches and all(first_prime_checks) and all(summary_checks.values()),
    }


def verify_terrain(terrain: dict) -> dict:
    values = [int(value) for value in terrain["values"]]
    bins = int(terrain["ara_bins"])
    histogram_checks = []
    collision_checks = []
    prime_checks = []
    for value, histogram, collision_count, prime_flag in zip(
        values,
        terrain["phase_histograms"],
        terrain["collision_counts"],
        terrain["prime_flags"],
    ):
        gates = [prime for prime in PRIMES if prime * prime <= value]
        histogram_checks.append(len(histogram) == bins and sum(histogram) == len(gates))
        collision_checks.append(int(collision_count) == sum(value % prime == 0 for prime in gates))
        prime_checks.append(bool(prime_flag) == (least_factor(value) == 0))

    survivor_checks = []
    for frontier, row in zip(terrain["gate_frontiers"], terrain["survivor_rows"]):
        survivor_checks.append(
            all(bool(saved) == survives(value, int(frontier)) for value, saved in zip(values, row))
        )

    anchor = int(terrain["anchor"])
    rebuilt_anchor, rebuilt_events = independent_cascade(anchor)
    selected_path_matches = (
        rebuilt_anchor == terrain["selected_anchor_path"]
        and all(
            all(
                close(float(saved[key]), float(rebuilt[key]))
                if key in ("split", "folded_split")
                else int(saved[key]) == int(rebuilt[key])
                for key in rebuilt
            )
            for saved, rebuilt in zip(terrain["selected_anchor_events"], rebuilt_events)
        )
        and len(terrain["selected_anchor_events"]) == len(rebuilt_events)
    )
    return {
        "terrain_values": len(values),
        "gate_frontiers": len(terrain["gate_frontiers"]),
        "all_histogram_sums_match_gate_counts": all(histogram_checks),
        "all_collision_counts_match_direct_divisibility": all(collision_checks),
        "all_prime_flags_match_direct_primality": all(prime_checks),
        "all_survivor_cells_match_direct_gate_checks": all(survivor_checks),
        "selected_anchor_path_matches_independent_cascade": selected_path_matches,
        "pass": (
            all(histogram_checks)
            and all(collision_checks)
            and all(prime_checks)
            and all(survivor_checks)
            and selected_path_matches
        ),
    }


def main() -> None:
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    terrain = json.loads(TERRAIN.read_text(encoding="utf-8"))
    target_checks = {
        name: verify_target(name, payload)
        for name, payload in results["targets"].items()
    }
    terrain_check = verify_terrain(terrain)
    payload = {
        "validation_id": "PN41/PRIME-THALWEG-PHI/independent-validation/v1",
        "source_results": RESULTS.name,
        "source_terrain": TERRAIN.name,
        "method": (
            "Direct trial division and direct gate-survival reconstruction; does not reuse "
            "PN41's segmented least-factor window or cascade implementation."
        ),
        "target_checks": target_checks,
        "terrain_check": terrain_check,
        "all_checks_pass": all(item["pass"] for item in target_checks.values()) and terrain_check["pass"],
    }
    VALIDATION.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

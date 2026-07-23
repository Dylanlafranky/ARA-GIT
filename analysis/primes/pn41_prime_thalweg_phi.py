"""PN41: natural-sieve thalweg handovers and a frozen Phi split test."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from pn10b_child_phase_prime_ranking import base_primes, segmented_least_prime_factor


HERE = Path(__file__).resolve().parent
PROTOCOL = "PN41_PRIME_THALWEG_PHI_PROTOCOL_v1_FROZEN.md"
RESULTS = HERE / "PN41_PRIME_THALWEG_PHI_RESULTS.json"
TERRAIN = HERE / "PN41_PRIME_THALWEG_TERRAIN.json"

TARGETS = {
    "A": (4_010_000_000, 4_011_000_000, 4_100_000_000),
    "B": (4_020_000_000, 4_021_000_000, 4_020_000_000),
}
ANCHOR_OFFSET = 250
ANCHOR_STEP = 1_000
ANCHORS_PER_TARGET = 1_000
MARGIN = 1_024
BOOTSTRAPS = 5_000
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_MIRROR = 2.0 - PHI
TOLERANCE = 0.025
LANDMARKS = {
    "phi_mirror": PHI_MIRROR,
    "quarter": 0.25,
    "third": 1.0 / 3.0,
    "two_fifths": 0.40,
    "half": 0.50,
}


class LeastFactorWindow:
    def __init__(self, low: int, high: int):
        numbers, least = segmented_least_prime_factor(low, high)
        self.low = int(numbers[0])
        self.high = int(numbers[-1]) + 1
        self.least = least.astype(np.int64)

    def get(self, value: int) -> int:
        if not self.low <= value < self.high:
            raise IndexError(f"{value} outside least-factor window [{self.low},{self.high})")
        return int(self.least[value - self.low])

    def survives(self, value: int, frontier: int) -> bool:
        least = self.get(value)
        return least == 0 or least > frontier

    def previous_survivor(self, value: int, frontier: int) -> int:
        candidate = value - 1
        while not self.survives(candidate, frontier):
            candidate -= 1
        return candidate

    def next_survivor(self, value: int, frontier: int) -> int:
        candidate = value + 1
        while not self.survives(candidate, frontier):
            candidate += 1
        return candidate


def cascade(anchor: int, window: LeastFactorWindow) -> tuple[dict[str, object], list[dict[str, object]]]:
    frontier = 2
    current = window.next_survivor(anchor, frontier)
    initial = current
    events: list[dict[str, object]] = []

    while window.get(current) != 0:
        gate = window.get(current)
        if gate <= frontier:
            raise AssertionError("current candidate should have survived the previous frontier")
        frontier = gate
        left = window.previous_survivor(current, frontier)
        right = window.next_survivor(current, frontier)
        split = (current - left) / (right - left)
        folded = min(split, 1.0 - split)
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
            "folded_split": folded,
            "distance_to_phi_mirror": abs(folded - PHI_MIRROR),
        })
        current = right

    return ({
        "anchor": anchor,
        "initial_candidate": initial,
        "final_prime": current,
        "final_delta": current - anchor,
        "handover_events": len(events),
    }, events)


def percentile(values: np.ndarray, probability: float) -> float:
    return float(np.quantile(values, probability, method="linear"))


def summarize_target(
    name: str,
    anchors: list[int],
    anchor_rows: list[dict[str, object]],
    event_rows: list[dict[str, object]],
    seed: int,
) -> dict[str, object]:
    events_by_anchor: dict[int, list[float]] = {anchor: [] for anchor in anchors}
    for event in event_rows:
        events_by_anchor[int(event["anchor"])].append(float(event["folded_split"]))
    eligible_anchors = [anchor for anchor in anchors if events_by_anchor[anchor]]

    distance_rows = np.asarray([
        [
            float(np.mean(np.abs(np.asarray(events_by_anchor[anchor]) - landmark)))
            for landmark in LANDMARKS.values()
        ]
        for anchor in eligible_anchors
    ])
    occupancy_rows = np.asarray([
        [
            float(np.mean(np.abs(np.asarray(events_by_anchor[anchor]) - landmark) <= TOLERANCE))
            for landmark in LANDMARKS.values()
        ]
        for anchor in eligible_anchors
    ])

    landmark_names = list(LANDMARKS)
    mean_distances = dict(zip(landmark_names, np.mean(distance_rows, axis=0).tolist()))
    mean_occupancies = dict(zip(landmark_names, np.mean(occupancy_rows, axis=0).tolist()))
    controls = [key for key in landmark_names if key != "phi_mirror"]
    best_control = min(controls, key=lambda key: mean_distances[key])
    phi_index = landmark_names.index("phi_mirror")
    control_index = landmark_names.index(best_control)
    paired = distance_rows[:, phi_index] - distance_rows[:, control_index]

    rng = np.random.default_rng(seed)
    bootstrap = np.empty(BOOTSTRAPS, dtype=np.float64)
    for index in range(BOOTSTRAPS):
        draw = rng.integers(0, paired.size, paired.size)
        bootstrap[index] = float(np.mean(paired[draw]))

    grid = np.arange(0.05, 0.5001, 0.001)
    grid_scores = np.empty(grid.size, dtype=np.float64)
    for index, landmark in enumerate(grid):
        grid_scores[index] = float(np.mean([
            np.mean(np.abs(np.asarray(events_by_anchor[anchor]) - landmark))
            for anchor in eligible_anchors
        ]))
    grid_optimum = float(grid[int(np.argmin(grid_scores))])

    phi_best_distance = all(
        mean_distances["phi_mirror"] < mean_distances[key] for key in controls
    )
    phi_best_occupancy = all(
        mean_occupancies["phi_mirror"] > mean_occupancies[key] for key in controls
    )
    bootstrap_interval = [percentile(bootstrap, 0.025), percentile(bootstrap, 0.975)]
    bootstrap_below_zero = bootstrap_interval[1] < 0.0
    optimum_near_phi = abs(grid_optimum - PHI_MIRROR) <= 0.02
    supported = phi_best_distance and phi_best_occupancy and bootstrap_below_zero and optimum_near_phi

    folds = np.asarray([float(event["folded_split"]) for event in event_rows])
    event_distribution: dict[str, int] = {}
    for value, count in zip(*np.unique(folds, return_counts=True)):
        event_distribution[f"{float(value):.12g}"] = int(count)

    return {
        "target": name,
        "anchors": len(anchors),
        "anchors_with_handover": len(eligible_anchors),
        "anchors_without_handover": len(anchors) - len(eligible_anchors),
        "distinct_final_primes": len({int(row["final_prime"]) for row in anchor_rows}),
        "handover_events": len(event_rows),
        "mean_handovers_per_anchor": float(np.mean([int(row["handover_events"]) for row in anchor_rows])),
        "median_handovers_per_anchor": float(np.median([int(row["handover_events"]) for row in anchor_rows])),
        "folded_split_mean": float(np.mean(folds)),
        "folded_split_median": float(np.median(folds)),
        "folded_split_distribution": event_distribution,
        "mean_absolute_distance_by_landmark": mean_distances,
        "occupancy_within_0_025_by_landmark": mean_occupancies,
        "best_fixed_control": best_control,
        "phi_minus_best_control": {
            "mean_paired_difference": float(np.mean(paired)),
            "bootstrap_count": BOOTSTRAPS,
            "bootstrap_seed": seed,
            "bootstrap_95_percent_interval": bootstrap_interval,
        },
        "grid_optimum": {
            "landmark": grid_optimum,
            "mean_absolute_distance": float(np.min(grid_scores)),
            "distance_from_phi_mirror": abs(grid_optimum - PHI_MIRROR),
        },
        "frozen_gates": {
            "phi_best_distance": phi_best_distance,
            "bootstrap_interval_below_zero": bootstrap_below_zero,
            "phi_best_occupancy": phi_best_occupancy,
            "grid_optimum_within_0_02": optimum_near_phi,
            "all_pass": supported,
        },
    }


def make_terrain(window: LeastFactorWindow, low_a: int) -> dict[str, object]:
    anchor = low_a
    start = anchor - 16
    width = 129
    values = np.arange(start, start + width, dtype=np.int64)
    gates_all = base_primes(math.isqrt(int(values[-1]))).astype(np.int64)
    bins = 80
    histograms: list[list[int]] = []
    collision_counts: list[int] = []
    prime_flags: list[bool] = []

    for value in values:
        gates = gates_all[gates_all * gates_all <= value]
        remainders = int(value) % gates
        bin_index = np.minimum((remainders * bins) // gates, bins - 1)
        histogram = np.bincount(bin_index, minlength=bins)
        histograms.append([int(item) for item in histogram])
        collision_counts.append(int(np.count_nonzero(remainders == 0)))
        prime_flags.append(window.get(int(value)) == 0)

    last_index = gates_all.size - 1
    sampled_indices = np.unique(np.rint(np.geomspace(1, last_index + 1, 60)).astype(int) - 1)
    frontiers = [int(gates_all[index]) for index in sampled_indices]
    # Retain every actual visible handover gate for the selected anchor.
    anchor_row, anchor_events = cascade(anchor, window)
    frontiers = sorted(set(frontiers + [int(event["gate"]) for event in anchor_events]))

    survivor_rows: list[list[int]] = []
    thalweg_values: list[int] = []
    for frontier in frontiers:
        survivor_rows.append([
            int(window.survives(int(value), frontier)) for value in values
        ])
        thalweg_values.append(window.next_survivor(anchor, frontier))

    return {
        "test": "PN41 bounded all-integer terrain",
        "status": "descriptive explanatory view after frozen scoring",
        "anchor": anchor,
        "start": start,
        "end_inclusive": int(values[-1]),
        "values": [int(value) for value in values],
        "ara_bins": bins,
        "bin_width": 2.0 / bins,
        "phase_histograms": histograms,
        "collision_counts": collision_counts,
        "prime_flags": prime_flags,
        "gate_frontiers": frontiers,
        "survivor_rows": survivor_rows,
        "thalweg_values": thalweg_values,
        "selected_anchor_path": anchor_row,
        "selected_anchor_events": anchor_events,
    }


def main() -> None:
    target_payloads: dict[str, object] = {}
    terrain_payload: dict[str, object] | None = None

    for name, (low, high, seed) in TARGETS.items():
        window = LeastFactorWindow(low - MARGIN, high + MARGIN)
        anchors = [low + ANCHOR_OFFSET + ANCHOR_STEP * index for index in range(ANCHORS_PER_TARGET)]
        anchor_rows: list[dict[str, object]] = []
        event_rows: list[dict[str, object]] = []
        for anchor in anchors:
            row, events = cascade(anchor, window)
            anchor_rows.append(row)
            event_rows.extend(events)
        target_payloads[name] = {
            "interval": [low, high],
            "anchor_rule": f"low+{ANCHOR_OFFSET}+{ANCHOR_STEP}*i, i=0..{ANCHORS_PER_TARGET - 1}",
            "summary": summarize_target(name, anchors, anchor_rows, event_rows, seed),
            "anchor_rows": anchor_rows,
            "event_rows": event_rows,
        }
        if name == "A":
            terrain_payload = make_terrain(window, low)

    if terrain_payload is None:
        raise AssertionError("terrain was not generated")

    both_pass = all(
        bool(target_payloads[name]["summary"]["frozen_gates"]["all_pass"])
        for name in TARGETS
    )
    result = {
        "test_id": "PN41/PRIME-THALWEG-PHI/v1",
        "protocol": PROTOCOL,
        "status": "SUPPORTED" if both_pass else "NOT SUPPORTED",
        "phi": PHI,
        "phi_mirror": PHI_MIRROR,
        "targets": target_payloads,
        "decision": {
            "both_targets_pass_all_frozen_gates": both_pass,
            "interpretation": (
                "Tests the mirrored golden split at natural-sieve nearest-survivor handovers. "
                "It does not test every possible Phi role in ARA."
            ),
            "new_prime_algorithm_supported": False,
        },
    }
    RESULTS.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    TERRAIN.write_text(json.dumps(terrain_payload, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({
        "results": str(RESULTS),
        "terrain": str(TERRAIN),
        "status": result["status"],
        "target_summaries": {name: target_payloads[name]["summary"] for name in TARGETS},
    }, indent=2))


if __name__ == "__main__":
    main()

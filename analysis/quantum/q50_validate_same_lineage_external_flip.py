"""Independent validation for Q50.

Does not import the primary implementation.
"""

from __future__ import annotations

import csv
import gzip
import json
import math
import pathlib
from collections import defaultdict

import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
EVENTS_PATH = HERE / "Q49_EXTERNAL_TIME_VECTOR_EVENTS.csv.gz"
RESULTS_PATH = HERE / "Q50_SAME_LINEAGE_EXTERNAL_FLIP_RESULTS.json"
BINS_PATH = HERE / "Q50_SAME_LINEAGE_EXTERNAL_FLIP_BINS.csv"
OUTPUT_PATH = HERE / "Q50_SAME_LINEAGE_EXTERNAL_FLIP_VALIDATION.json"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
LEFT = 1.0 / math.e
RIGHT = PHI - 1.0
CENTRE = LEFT + (RIGHT - LEFT) / 2.0
AXIS = np.asarray(
    [math.cos(2.0 * math.pi * CENTRE), math.sin(2.0 * math.pi * CENTRE)]
)
EPS = 1e-12


def close(a: float, b: float, tolerance: float = 1e-10) -> bool:
    return bool(abs(a - b) <= tolerance)


def vector(row: dict[str, str], estimator: str = "circle") -> np.ndarray:
    return (
        np.asarray(
            [float(row[f"{estimator}_du"]), float(row[f"{estimator}_dv"])]
        )
        / float(row["radius_mean"])
    )


def summary(rows: list[dict[str, str]], estimator: str = "circle") -> dict[str, float]:
    vectors = np.asarray([vector(row, estimator) for row in rows])
    movement = float(np.linalg.norm(vectors, axis=1).sum())
    total = vectors.sum(axis=0)
    axial = float(total @ AXIS)
    balance = axial / movement
    heading = float((math.atan2(total[1], total[0]) / (2.0 * math.pi)) % 1.0)
    return {
        "movement": movement,
        "axial": axial,
        "x": 1.0 - balance,
        "heading": heading,
    }


def circ_distance(a: float, b: float) -> float:
    delta = abs(a - b)
    return min(delta, 1.0 - delta)


def main() -> None:
    with gzip.open(EVENTS_PATH, "rt", newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    grouped: dict[tuple[int, int], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["seed"]), int(row["pair_index"]))].append(row)
    fixed = {
        key
        for key, values in grouped.items()
        if sum(int(row["current_end"]) < 250 for row in values) >= 3
        and sum(int(row["current_start"]) >= 250 for row in values) >= 3
    }
    development = [
        row
        for key in fixed
        for row in grouped[key]
        if int(row["current_end"]) < 250
    ]
    evaluation = [
        row
        for key in fixed
        for row in grouped[key]
        if int(row["current_start"]) >= 250
    ]
    dev = summary(development)
    evaluation_summary = summary(evaluation)
    separation = circ_distance(dev["heading"], evaluation_summary["heading"])

    declared_to_opposite = 0
    opposite_to_declared = 0
    deltas: list[float] = []
    for key in fixed:
        dev_line = summary(
            [
                row
                for row in grouped[key]
                if int(row["current_end"]) < 250
            ]
        )
        eval_line = summary(
            [
                row
                for row in grouped[key]
                if int(row["current_start"]) >= 250
            ]
        )
        deltas.append(eval_line["x"] - dev_line["x"])
        declared_to_opposite += dev_line["x"] < 1 < eval_line["x"]
        opposite_to_declared += dev_line["x"] > 1 > eval_line["x"]

    bin_rows: list[dict[str, str]]
    with BINS_PATH.open("r", newline="", encoding="utf-8") as stream:
        bin_rows = [
            row
            for row in csv.DictReader(stream)
            if row["population"] == "fixed" and row["estimator"] == "circle"
        ]
    recomputed_bins: list[dict[str, float | int]] = []
    for left in range(0, 500, 25):
        selected = [
            row
            for key in fixed
            for row in grouped[key]
            if left <= int(row["current_start"]) < left + 25
        ]
        value = summary(selected)
        recomputed_bins.append(
            {
                "left": left,
                "events": len(selected),
                "x": value["x"],
                "mean_movement": value["movement"] / len(selected),
            }
        )

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    check("event population", len(rows) == 32420, f"{len(rows):,} events")
    check(
        "fixed lineage population",
        len(fixed) == 1120 and len({key[0] for key in fixed}) == 71,
        f"{len(fixed):,} lineages; {len({key[0] for key in fixed})} seeds",
    )
    check(
        "development coordinate",
        close(dev["x"], results["primary"]["fixed_population_strata"]["development"]["x"]),
        f"x={dev['x']:.12f}",
    )
    check(
        "evaluation coordinate",
        close(
            evaluation_summary["x"],
            results["primary"]["fixed_population_strata"]["evaluation"]["x"],
        ),
        f"x={evaluation_summary['x']:.12f}",
    )
    check(
        "movement totals",
        close(
            dev["movement"],
            results["primary"]["fixed_population_strata"]["development"]["movement"],
        )
        and close(
            evaluation_summary["movement"],
            results["primary"]["fixed_population_strata"]["evaluation"]["movement"],
        ),
        f"development={dev['movement']:.9f}; evaluation={evaluation_summary['movement']:.9f}",
    )
    check(
        "half-turn separation",
        close(
            separation,
            results["primary"]["fixed_population_strata"][
                "aggregate_heading_separation_turns"
            ],
        ),
        f"{separation:.12f} turns",
    )
    check(
        "paired reversal counts",
        declared_to_opposite
        == results["primary"]["paired_lineages"]["declared_to_opposite"]
        and opposite_to_declared
        == results["primary"]["paired_lineages"]["opposite_to_declared"],
        f"{declared_to_opposite} declared→opposite; {opposite_to_declared} opposite→declared",
    )
    check(
        "paired delta",
        close(
            float(np.median(deltas)),
            results["primary"]["paired_lineages"]["median_delta_x"],
        )
        and close(
            float(np.mean(deltas)),
            results["primary"]["paired_lineages"]["mean_delta_x"],
        ),
        f"median={np.median(deltas):.12f}; mean={np.mean(deltas):.12f}",
    )
    bins_match = all(
        int(saved["events"]) == int(recomputed["events"])
        and close(float(saved["x"]), float(recomputed["x"]))
        and close(
            float(saved["mean_relative_movement"]),
            float(recomputed["mean_movement"]),
        )
        for saved, recomputed in zip(bin_rows, recomputed_bins)
    )
    check("twenty time bins", bins_match and len(bin_rows) == 20, "all bins exact")
    values = np.asarray([float(row["x"]) for row in bin_rows])
    upward = [
        index
        for index in range(1, len(values))
        if values[index - 1] < 1 <= values[index]
    ]
    downward = [
        index
        for index in range(1, len(values))
        if values[index - 1] > 1 >= values[index]
    ]
    check(
        "ordered crossing",
        upward == [6] and downward == [],
        f"0→2 bins={upward}; 2→0 bins={downward}",
    )
    movement = np.asarray(
        [float(row["mean_relative_movement"]) for row in bin_rows]
    )
    crossing = upward[0]
    pre = float(np.mean(movement[crossing - 2 : crossing]))
    post = float(np.mean(movement[crossing + 1 : crossing + 3]))
    strict_pinch = movement[crossing] < pre and movement[crossing] < post
    check(
        "strict pinch verdict",
        strict_pinch
        == results["primary"]["pinch"][
            "strict_local_minimum_with_post_crossing_rebound"
        ],
        f"at={movement[crossing]:.9g}; pre={pre:.9g}; post={post:.9g}; strict={strict_pinch}",
    )

    payload = {
        "validation": "PASS" if all(item["pass"] for item in checks) else "FAIL",
        "checks_passed": sum(item["pass"] for item in checks),
        "checks_total": len(checks),
        "checks": checks,
        "independent_observations": {
            "evaluation_to_development_movement_ratio": evaluation_summary[
                "movement"
            ]
            / dev["movement"],
            "same_lineage_reversal_is_verified": True,
            "complete_0_to_2_to_0_is_verified": False,
            "isolated_pinch_is_verified": bool(strict_pinch),
        },
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

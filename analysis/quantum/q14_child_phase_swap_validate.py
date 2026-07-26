#!/usr/bin/env python3
"""Independent source-to-result validator for Q14."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "Q13_RAMSEY_HAHN_FOUR_CHILDREN.csv"
PROTOCOL = HERE / "Q14_CHILD_PHASE_SWAP_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q14_CHILD_PHASE_SWAP_PROTOCOL_v1_FROZEN.sha256"
REPORTED = HERE / "Q14_CHILD_PHASE_SWAP_RESULTS.json"
OUTPUT = HERE / "Q14_CHILD_PHASE_SWAP_VALIDATION.json"
STATES = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")
AXES = ("amplitude", "direction")
PERMUTATIONS = 9999
SEED = 27014
TOLERANCE = 1e-12


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def base_metrics(ramsey: np.ndarray, hahn: np.ndarray) -> dict[str, float | int]:
    identity_sse = float(((hahn - ramsey) ** 2).sum())
    swap_sse = float(((hahn - ramsey[:, [1, 0]]) ** 2).sum())
    difference_r = ramsey[:, 0] - ramsey[:, 1]
    difference_h = hahn[:, 0] - hahn[:, 1]
    products = difference_r * difference_h
    denominator = math.sqrt(
        float((difference_r**2).sum()) * float((difference_h**2).sum())
    )
    return {
        "identity_sse": identity_sse,
        "swap_sse": swap_sse,
        "swap_gain": 1.0 - swap_sse / identity_sse,
        "flipped_fraction": float(np.mean(products < 0)),
        "flipped_cosine": -float(products.sum()) / denominator,
        "evaluable_cells": int(len(products)),
        "sum_invariance_max_error": float(
            np.max(
                np.abs(
                    ramsey[:, [1, 0]].sum(axis=1)
                    - ramsey.sum(axis=1)
                )
            )
        ),
    }


def fit(source: np.ndarray, target: np.ndarray) -> tuple[float, float, np.ndarray]:
    source_mean = source.mean(axis=0)
    target_mean = target.mean(axis=0)
    source_centered = source - source_mean
    target_centered = target - target_mean
    raw = float((source_centered * target_centered).sum()) / float(
        (source_centered**2).sum()
    )
    scale = max(0.0, raw)
    offset = target_mean - scale * source_mean
    return scale, raw, offset


def cross_validate(
    ramsey: np.ndarray, hahn: np.ndarray, labels: np.ndarray
) -> list[dict[str, object]]:
    output = []
    for heldout in STATES:
        train = labels != heldout
        test = labels == heldout
        same_scale, same_raw, same_offset = fit(ramsey[train], hahn[train])
        swap_scale, swap_raw, swap_offset = fit(
            ramsey[train][:, [1, 0]], hahn[train]
        )
        same_prediction = same_offset + same_scale * ramsey[test]
        swap_prediction = (
            swap_offset + swap_scale * ramsey[test][:, [1, 0]]
        )
        same_sse = float(((hahn[test] - same_prediction) ** 2).sum())
        swap_sse = float(((hahn[test] - swap_prediction) ** 2).sum())
        output.append(
            {
                "heldout_state": heldout,
                "train_cells": int(train.sum()),
                "test_cells": int(test.sum()),
                "identity_scale": same_scale,
                "identity_raw_scale": same_raw,
                "swap_scale": swap_scale,
                "swap_raw_scale": swap_raw,
                "identity_sse": same_sse,
                "swap_sse": swap_sse,
                "swap_gain": 1.0 - swap_sse / same_sse,
                "swap_wins": swap_sse < same_sse,
            }
        )
    return output


def same_number(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=0.0, abs_tol=TOLERANCE)


def main() -> None:
    expected_hash = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    protocol_hash = digest(PROTOCOL)
    reported = json.loads(REPORTED.read_text(encoding="utf-8"))
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    labels = np.asarray([row["state"] for row in rows])
    arrays = {}
    metrics = {}
    folds = {}
    for axis in AXES:
        ramsey = np.asarray(
            [
                [float(row[f"R_A_{axis}"]), float(row[f"R_B_{axis}"])]
                for row in rows
            ]
        )
        hahn = np.asarray(
            [
                [float(row[f"H_A_{axis}"]), float(row[f"H_B_{axis}"])]
                for row in rows
            ]
        )
        arrays[axis] = (ramsey, hahn)
        metrics[axis] = base_metrics(ramsey, hahn)
        folds[axis] = cross_validate(ramsey, hahn, labels)

    rng = np.random.default_rng(SEED)
    state_rows = {state: np.flatnonzero(labels == state) for state in STATES}
    null_values = {axis: [] for axis in AXES}
    for _ in range(PERMUTATIONS):
        remaps = {
            state: rng.permutation(indices)
            for state, indices in state_rows.items()
        }
        for axis in AXES:
            ramsey, hahn = arrays[axis]
            shuffled = hahn.copy()
            for state, indices in state_rows.items():
                shuffled[indices] = hahn[remaps[state]]
            null_values[axis].append(
                float(base_metrics(ramsey, shuffled)["swap_gain"])
            )

    nulls = {}
    for axis in AXES:
        observed = float(metrics[axis]["swap_gain"])
        values = null_values[axis]
        nulls[axis] = {
            "permutations": PERMUTATIONS,
            "seed": SEED,
            "observed_swap_gain": observed,
            "p_value": (
                1 + sum(value >= observed for value in values)
            )
            / (len(values) + 1),
            "null_q95": float(np.quantile(values, 0.95)),
            "null_q99": float(np.quantile(values, 0.99)),
            "null_mean": float(np.mean(values)),
        }
    cv_medians = {
        axis: float(np.median([float(row["swap_gain"]) for row in folds[axis]]))
        for axis in AXES
    }
    cv_wins = {
        axis: sum(bool(row["swap_wins"]) for row in folds[axis])
        for axis in AXES
    }

    reported_summary = reported["summary"]
    checks = {
        "protocol_hash": expected_hash == protocol_hash == reported["protocol_sha256"],
        "source_shape": len(rows) == 44
        and set(labels) == set(STATES)
        and all(int((labels == state).sum()) == 11 for state in STATES),
        "finite": all(
            np.isfinite(array).all()
            for pair in arrays.values()
            for array in pair
        ),
        "metrics": all(
            same_number(
                float(metrics[axis][key]),
                float(reported_summary["metrics"][axis][key]),
            )
            for axis in AXES
            for key in metrics[axis]
        ),
        "nulls": all(
            same_number(
                float(nulls[axis][key]),
                float(reported_summary["nulls"][axis][key]),
            )
            for axis in AXES
            for key in (
                "observed_swap_gain",
                "p_value",
                "null_q95",
                "null_q99",
                "null_mean",
            )
        ),
        "cv_medians": all(
            same_number(
                cv_medians[axis],
                float(reported_summary["cv_median_swap_gain"][axis]),
            )
            for axis in AXES
        ),
        "cv_wins": cv_wins == reported_summary["cv_swap_wins"],
    }
    result = {
        "validation_id": "Q14-CHILD-PHASE-SWAP-independent-v1",
        "independent_of_main_module": True,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "recomputed": {
            "metrics": metrics,
            "nulls": nulls,
            "cv_median_swap_gain": cv_medians,
            "cv_swap_wins": cv_wins,
        },
        "boundary": (
            "This validates deterministic implementation only. It does not make "
            "Ramsey and Hahn a causal parent-child sequence."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

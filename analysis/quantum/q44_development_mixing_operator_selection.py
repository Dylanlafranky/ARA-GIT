"""Development-stage selection of a compact ARA matrix mixing operator.

This is not a target test. It compares fixed grouping variants on the
already-open Q40 greedy and Q41B landmax archives so one operator can be
frozen before an untouched archive is opened.
"""

from __future__ import annotations

import json
import pathlib
import sys
from collections import defaultdict


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / "public_data" / "_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import numpy as np

import q40_return_flow_relation_reversal_test as base
import q42_ara_dual_strand_flow_test as q42


OUTPUT = HERE / "Q44_DEVELOPMENT_MIXING_OPERATOR_SELECTION.json"
EPS = 1e-12


def components(c1, c2, c3):
    diameter = c1 - c2
    visible_step = c3 - c2
    diameter_sq = float(np.sum(diameter * diameter))
    if diameter_sq <= EPS:
        other = np.zeros_like(diameter)
    else:
        other = visible_step - (
            float(np.sum(visible_step * diameter)) / diameter_sq
        ) * diameter
    return diameter, other


def fit_coefficients(records, grouping):
    accum = defaultdict(lambda: np.zeros((2, 2), dtype=np.float64))
    rhs = defaultdict(lambda: np.zeros(2, dtype=np.float64))
    counts = defaultdict(int)
    for record in records:
        key = grouping(record)
        d, o, y = record["d"], record["o"], record["y"]
        accum[key][0, 0] += np.sum(d * d)
        accum[key][0, 1] += np.sum(d * o)
        accum[key][1, 0] += np.sum(d * o)
        accum[key][1, 1] += np.sum(o * o)
        rhs[key][0] += np.sum(d * y)
        rhs[key][1] += np.sum(o * y)
        counts[key] += 1
    coefficients = {}
    for key in accum:
        coefficients[key] = np.linalg.pinv(accum[key], rcond=1e-12) @ rhs[key]
    return coefficients, counts


def fit_affine(records, grouping):
    normal = defaultdict(lambda: np.zeros((3, 3), dtype=np.float64))
    rhs = defaultdict(lambda: np.zeros(3, dtype=np.float64))
    counts = defaultdict(int)
    for record in records:
        key = grouping(record)
        c = (record["c1"], record["c2"], record["c3"])
        for left in range(3):
            for right in range(3):
                normal[key][left, right] += np.sum(c[left] * c[right])
            rhs[key][left] += np.sum(c[left] * record["c4"])
        counts[key] += 1
    coefficients = {
        key: np.linalg.pinv(value, rcond=1e-12) @ rhs[key]
        for key, value in normal.items()
    }
    return coefficients, counts


def gather(closure, connected, first, last):
    output = []
    for seed in range(closure.shape[0]):
        for pair in range(closure.shape[2]):
            coordinate = base.coordinates(closure[seed, :, pair])
            if coordinate is None:
                continue
            u, v, labels, direction, coherence, occupancy = coordinate
            if coherence < 0.80 or occupancy < 0.05:
                continue
            family, _fit = q42.cadence_family(u, v)
            scale = float(
                np.median(
                    np.linalg.norm(connected[seed, :250, pair], axis=(1, 2))
                )
            )
            for window in base.complete_windows(labels, direction, first, last):
                c1, c2, c3, c4 = base.identities_for_window(
                    connected, seed, pair, window
                )
                d, o = components(c1, c2, c3)
                output.append(
                    {
                        "seed": seed,
                        "pair": pair,
                        "family": family,
                        "q4": int(window[3][0]),
                        "scale": scale,
                        "c1": c1,
                        "c2": c2,
                        "c3": c3,
                        "c4": c4,
                        "d": d,
                        "o": o,
                        "y": c4 - c3,
                    }
                )
    return output


GROUPINGS = {
    "pooled": lambda row: ("all",),
    "family": lambda row: (row["family"],),
    "quadrant": lambda row: (row["q4"],),
    "family_quadrant": lambda row: (row["family"], row["q4"]),
}


def metrics(predicted, actual, scale):
    error = float(np.linalg.norm(predicted - actual))
    cosine = float(
        np.sum(predicted * actual)
        / (np.linalg.norm(predicted) * np.linalg.norm(actual) + EPS)
    )
    return error / (scale + EPS), cosine


def summarize(rows):
    by_seed = defaultdict(list)
    for row in rows:
        by_seed[row["seed"]].append(row)
    seed_error = np.asarray(
        [np.mean([item["error"] for item in items]) for items in by_seed.values()]
    )
    seed_cosine = np.asarray(
        [np.mean([item["cosine"] for item in items]) for items in by_seed.values()]
    )
    return {
        "cycles": len(rows),
        "seeds": len(by_seed),
        "seed_balanced_error": float(np.mean(seed_error)),
        "seed_balanced_cosine": float(np.mean(seed_cosine)),
        "median_cycle_error": float(np.median([row["error"] for row in rows])),
        "median_cycle_cosine": float(np.median([row["cosine"] for row in rows])),
    }


def evaluate(development, evaluation):
    results = {}
    for name, grouping in GROUPINGS.items():
        coefficients, counts = fit_coefficients(development, grouping)
        affine, affine_counts = fit_affine(development, grouping)
        for variant in ("mixing", "diameter_only", "affine"):
            label = f"{name}_{variant}"
            scored = []
            for row in evaluation:
                key = grouping(row)
                if key not in coefficients:
                    continue
                if variant == "mixing":
                    alpha, beta = coefficients[key]
                    predicted = row["c3"] + alpha * row["d"] + beta * row["o"]
                elif variant == "diameter_only":
                    alpha = coefficients[key][0]
                    predicted = row["c3"] + alpha * row["d"]
                else:
                    weights = affine[key]
                    predicted = (
                        weights[0] * row["c1"]
                        + weights[1] * row["c2"]
                        + weights[2] * row["c3"]
                    )
                error, cosine = metrics(predicted, row["c4"], row["scale"])
                scored.append(
                    {
                        "seed": row["seed"],
                        "error": error,
                        "cosine": cosine,
                    }
                )
            item = summarize(scored)
            item["groups"] = len(coefficients if variant != "affine" else affine)
            item["minimum_development_cycles_per_group"] = int(
                min((counts if variant != "affine" else affine_counts).values())
            )
            item["maximum_development_cycles_per_group"] = int(
                max((counts if variant != "affine" else affine_counts).values())
            )
            if variant != "affine":
                item["coefficients"] = {
                    repr(key): [float(value) for value in coefficients[key]]
                    for key in sorted(coefficients, key=repr)
                }
            results[label] = item

    baselines = {
        "persistence": lambda row: row["c3"],
        "forward_relation": lambda row: row["c3"] + row["d"],
        "reverse_relation": lambda row: row["c3"] - row["d"],
        "local_linear": lambda row: 2 * row["c3"] - row["c2"],
    }
    for name, function in baselines.items():
        scored = []
        for row in evaluation:
            error, cosine = metrics(function(row), row["c4"], row["scale"])
            scored.append(
                {"seed": row["seed"], "error": error, "cosine": cosine}
            )
        results[name] = summarize(scored)
    return results


def main():
    output = {
        "status": "DEVELOPMENT OPERATOR SELECTION — TARGET NOT OPENED",
        "equation": "C4_hat=C3+alpha*(C1-C2)+beta*Other_visible",
        "other_visible": (
            "(C3-C2)-proj_(C1-C2)(C3-C2), fixed before target selection"
        ),
        "archives": {},
    }
    for archive, paths in q42.DATASETS.items():
        closure = np.asarray(np.load(paths["derived"])["closure"], dtype=np.float32)
        connected = np.load(paths["connected"], mmap_mode="r")
        development = gather(closure, connected, 0, 248)
        evaluation = gather(closure, connected, 250, 498)
        output["archives"][archive] = {
            "development_cycles": len(development),
            "evaluation_cycles": len(evaluation),
            "methods": evaluate(development, evaluation),
        }
    averages = {}
    method_names = output["archives"]["greedy"]["methods"]
    for method in method_names:
        averages[method] = {
            metric: float(
                np.mean(
                    [
                        output["archives"][archive]["methods"][method][metric]
                        for archive in q42.DATASETS
                    ]
                )
            )
            for metric in ("seed_balanced_error", "seed_balanced_cosine")
        }
    output["cross_archive_average"] = averages
    output["best_mixing_by_error"] = min(
        (
            (name, values["seed_balanced_error"])
            for name, values in averages.items()
            if name.endswith("_mixing")
        ),
        key=lambda item: item[1],
    )[0]
    OUTPUT.write_text(
        json.dumps(output, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "best_mixing_by_error": output["best_mixing_by_error"],
                "cross_archive_average": dict(
                    sorted(
                        averages.items(),
                        key=lambda item: item[1]["seed_balanced_error"],
                    )
                ),
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()

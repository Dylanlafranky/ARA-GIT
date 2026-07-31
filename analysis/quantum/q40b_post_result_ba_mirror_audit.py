#!/usr/bin/env python3
"""Post-result test of the simplest Q40 Ba 'upside-down' explanation.

This audit asks whether Q40 read the B-dominant Ba quadrant using the
A-leading orientation learned in Q39A.  The primary mirror candidate swaps
C1 and C2 only when the fourth quadrant is Ba, then applies the *same* Q40
operator without fitted parameters.

The audit is descriptive.  It cannot alter Q40/T295 and can only specify a
future frozen test on another untouched archive.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCAL_DEPS = HERE / "public_data" / "_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import numpy as np


DATA = HERE / "public_data" / "q40_return_flow_inhomo_v1_greedy"
CONNECTED = DATA / "q40_connected_cache.npy"
PREDICTIONS = DATA / "q40_frozen_predictions.npz"
OUTPUT = HERE / "Q40B_POST_RESULT_BA_MIRROR_RESULTS.json"

EPS = 1e-12
BOOTSTRAP_SEED = 400041
BOOTSTRAP_DRAWS = 20_000
BA_INDEX = 1
QUADRANTS = {
    0: "Ab / Q++",
    1: "Ba / Q-+",
    2: "bA / Q--",
    3: "aB / Q+-",
}
METHODS = (
    "q40_original",
    "ba_full_mirror",
    "ba_output_mirror_only",
    "ba_always_local_forward",
    "global_full_mirror",
    "affine",
)


def cosine(left: np.ndarray, right: np.ndarray) -> float:
    return float(
        np.sum(left * right)
        / (np.linalg.norm(left) * np.linalg.norm(right) + EPS)
    )


def exact_q40(c1: np.ndarray, c2: np.ndarray, c3: np.ndarray):
    """Apply Q40 exactly and return prediction, flag, flag cosine, forward."""
    delta = c1 - c2
    forward = c3 + delta
    flag_cosine = cosine(forward, c3)
    flag = flag_cosine < 0
    prediction = c3 - delta if flag else forward
    return prediction, flag, flag_cosine, forward


def bootstrap_advantage(candidate: np.ndarray, reference: np.ndarray, offset: int):
    """Positive values mean the candidate has lower seed-balanced error."""
    difference = reference - candidate
    rng = np.random.default_rng(BOOTSTRAP_SEED + offset)
    indices = rng.integers(
        0, len(difference), size=(BOOTSTRAP_DRAWS, len(difference))
    )
    boot = np.mean(difference[indices], axis=1)
    return {
        "advantage_over_reference": float(np.mean(difference)),
        "seed_cluster_ci95": [
            float(np.quantile(boot, 0.025)),
            float(np.quantile(boot, 0.975)),
        ],
        "p_no_advantage": float(
            (np.sum(boot <= 0) + 1) / (BOOTSTRAP_DRAWS + 1)
        ),
    }


def aggregate_seed_balanced(
    values: np.ndarray,
    seeds: np.ndarray,
    pairs: np.ndarray,
    mask: np.ndarray | None = None,
) -> np.ndarray:
    if mask is None:
        mask = np.ones(len(values), dtype=bool)
    lineage: dict[tuple[int, int], list[float]] = defaultdict(list)
    for index in np.flatnonzero(mask):
        lineage[(int(seeds[index]), int(pairs[index]))].append(
            float(values[index])
        )
    seed_values: dict[int, list[float]] = defaultdict(list)
    for (seed, _pair), members in lineage.items():
        seed_values[seed].append(float(np.mean(members)))
    return np.asarray(
        [
            np.mean(seed_values[seed])
            for seed in sorted(seed_values)
        ],
        dtype=np.float64,
    )


def confusion(flag: np.ndarray, target: np.ndarray):
    tp = int(np.sum(flag & target))
    fp = int(np.sum(flag & ~target))
    fn = int(np.sum(~flag & target))
    tn = int(np.sum(~flag & ~target))
    return {
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "precision": tp / max(tp + fp, 1),
        "recall": tp / max(tp + fn, 1),
        "specificity": tn / max(tn + fp, 1),
    }


def main() -> None:
    connected = np.load(CONNECTED, mmap_mode="r")
    frozen = np.load(PREDICTIONS, allow_pickle=False)

    seeds = np.asarray(frozen["seed"], dtype=np.int64)
    pairs = np.asarray(frozen["pair"], dtype=np.int64)
    q4 = np.asarray(frozen["q4"], dtype=np.int64)
    scales = np.asarray(frozen["lineage_scale"], dtype=np.float64)
    visible = np.asarray(frozen["c_visible"], dtype=np.float64)
    stored_predictions = np.asarray(frozen["predictions"], dtype=np.float64)
    n = len(seeds)

    actual = np.empty((n, 3, 3), dtype=np.float64)
    for index in range(n):
        start = int(frozen["q4_start"][index])
        end = int(frozen["q4_end"][index])
        actual[index] = np.mean(
            connected[seeds[index], start : end + 1, pairs[index]],
            axis=0,
            dtype=np.float64,
        )

    predictions = {
        method: np.empty_like(actual)
        for method in METHODS
    }
    predictions["q40_original"][:] = stored_predictions[:, 0]
    predictions["affine"][:] = stored_predictions[:, -1]
    predictions["ba_full_mirror"][:] = predictions["q40_original"]
    predictions["ba_output_mirror_only"][:] = predictions["q40_original"]
    predictions["ba_always_local_forward"][:] = predictions["q40_original"]

    original_flags = np.asarray(frozen["flag"], dtype=bool)
    mirror_flags = np.zeros(n, dtype=bool)
    original_target_negative = np.zeros(n, dtype=bool)
    mirror_target_negative = np.zeros(n, dtype=bool)

    for index, (c1, c2, c3) in enumerate(visible):
        original_prediction, original_flag, _, original_forward = exact_q40(
            c1, c2, c3
        )
        mirror_prediction, mirror_flag, _, mirror_forward = exact_q40(
            c2, c1, c3
        )
        predictions["global_full_mirror"][index] = mirror_prediction
        mirror_flags[index] = mirror_flag
        original_target_negative[index] = cosine(
            original_forward, actual[index]
        ) < 0
        mirror_target_negative[index] = cosine(
            mirror_forward, actual[index]
        ) < 0

        if q4[index] != BA_INDEX:
            continue

        delta = c1 - c2
        predictions["ba_full_mirror"][index] = mirror_prediction
        predictions["ba_output_mirror_only"][index] = (
            c3 + delta if original_flag else c3 - delta
        )
        predictions["ba_always_local_forward"][index] = c3 - delta

        if not np.allclose(
            predictions["q40_original"][index],
            original_prediction,
            atol=1e-7,
            rtol=1e-7,
        ):
            raise RuntimeError("Stored Q40 prediction differs from recomputation")

    scaled_error: dict[str, np.ndarray] = {}
    cosines: dict[str, np.ndarray] = {}
    seed_error: dict[str, np.ndarray] = {}
    ba_seed_error: dict[str, np.ndarray] = {}
    ba_mask = q4 == BA_INDEX

    for method in METHODS:
        difference = predictions[method] - actual
        absolute = np.linalg.norm(difference, axis=(1, 2))
        scaled_error[method] = absolute / (scales + EPS)
        numerator = np.sum(predictions[method] * actual, axis=(1, 2))
        denominator = (
            np.linalg.norm(predictions[method], axis=(1, 2))
            * np.linalg.norm(actual, axis=(1, 2))
            + EPS
        )
        cosines[method] = numerator / denominator
        seed_error[method] = aggregate_seed_balanced(
            scaled_error[method], seeds, pairs
        )
        ba_seed_error[method] = aggregate_seed_balanced(
            scaled_error[method], seeds, pairs, ba_mask
        )

    method_summary = {}
    for method in METHODS:
        method_summary[method] = {
            "seed_balanced_scaled_error": float(np.mean(seed_error[method])),
            "seed_balanced_cosine": float(
                np.mean(
                    aggregate_seed_balanced(cosines[method], seeds, pairs)
                )
            ),
            "ba_seed_balanced_scaled_error": float(
                np.mean(ba_seed_error[method])
            ),
            "ba_seed_balanced_cosine": float(
                np.mean(
                    aggregate_seed_balanced(
                        cosines[method], seeds, pairs, ba_mask
                    )
                )
            ),
            "ba_cycle_improvement_fraction_vs_q40": float(
                np.mean(
                    scaled_error[method][ba_mask]
                    < scaled_error["q40_original"][ba_mask]
                )
            ),
        }

    comparisons = {}
    for offset, method in enumerate(METHODS[1:], start=1):
        comparisons[f"{method}_vs_q40_global"] = bootstrap_advantage(
            seed_error[method],
            seed_error["q40_original"],
            offset,
        )
        comparisons[f"{method}_vs_q40_ba"] = bootstrap_advantage(
            ba_seed_error[method],
            ba_seed_error["q40_original"],
            offset + 100,
        )

    quadrant_summary = []
    for quadrant in sorted(QUADRANTS):
        selected = q4 == quadrant
        quadrant_summary.append(
            {
                "q4_index": quadrant,
                "quadrant": QUADRANTS[quadrant],
                "cycles": int(np.sum(selected)),
                "q40_scaled_error": float(
                    np.mean(scaled_error["q40_original"][selected])
                ),
                "ba_full_mirror_scaled_error": float(
                    np.mean(scaled_error["ba_full_mirror"][selected])
                ),
                "ba_full_mirror_improvement_fraction": float(
                    np.mean(
                        scaled_error["ba_full_mirror"][selected]
                        < scaled_error["q40_original"][selected]
                    )
                ),
            }
        )

    ba_original_confusion = confusion(
        original_flags[ba_mask],
        original_target_negative[ba_mask],
    )
    ba_mirror_confusion = confusion(
        mirror_flags[ba_mask],
        mirror_target_negative[ba_mask],
    )

    full_mirror_global = comparisons["ba_full_mirror_vs_q40_global"]
    full_mirror_ba = comparisons["ba_full_mirror_vs_q40_ba"]
    posthoc_simple_mirror_supported = (
        full_mirror_global["seed_cluster_ci95"][0] > 0
        and full_mirror_ba["seed_cluster_ci95"][0] > 0
        and method_summary["ba_full_mirror"][
            "ba_cycle_improvement_fraction_vs_q40"
        ]
        > 0.5
    )

    result = {
        "audit_id": "Q40B-POST-RESULT-BA-MIRROR-v1",
        "status": "DESCRIPTIVE POST-RESULT; Q40/T295 VERDICT UNCHANGED",
        "question": (
            "Was the B-dominant Ba quadrant read with the A-leading "
            "orientation, analogous to reading a stalagmite as a stalactite?"
        ),
        "primary_candidate": {
            "name": "ba_full_mirror",
            "definition": (
                "For q4=Ba only, swap C1 and C2 and then apply the exact "
                "unchanged Q40 flag and conditional operator."
            ),
            "has_fitted_parameters": False,
        },
        "population": {
            "cycles": n,
            "ba_cycles": int(np.sum(ba_mask)),
            "seeds": int(len(np.unique(seeds))),
            "ba_seeds": int(len(np.unique(seeds[ba_mask]))),
        },
        "method_summary": method_summary,
        "comparisons": comparisons,
        "ba_original_coordinate_confusion": ba_original_confusion,
        "ba_mirrored_coordinate_confusion": ba_mirror_confusion,
        "quadrant_summary": quadrant_summary,
        "posthoc_simple_mirror_supported": posthoc_simple_mirror_supported,
        "interpretation": (
            "If supported, the simplest explanation is that Ba uses the same "
            "operator from the opposite endpoint. This is a post-result "
            "specification only and requires an untouched archive."
            if posthoc_simple_mirror_supported
            else
            "The exact endpoint swap did not repair Ba strongly enough; a "
            "more complex mirror story should not be assumed."
        ),
        "boundary": (
            "This audit cannot rescore Q40, prove physical Phase B, or "
            "establish a universal singularity flip."
        ),
    }

    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

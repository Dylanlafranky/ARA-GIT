"""Q39A post-result audit of sign reversals, seam depth and purity scaling.

This script does not alter Q39's frozen verdict. It uses the already-open
Q39 cycle table and validated derived caches to test whether the 7.25% of
negative-cosine reconstructions cluster at the previously defined Q36
determinant-trough seam, and whether Q39's purity association survives an
absolute-error calculation.
"""

from __future__ import annotations

import csv
import gzip
import json
import math
import os
import pathlib
from collections import defaultdict


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / "public_data" / "_deps"
if LOCAL_DEPS.exists():
    import sys

    sys.path.insert(0, str(LOCAL_DEPS))
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".mplconfig"))

import matplotlib.pyplot as plt
import numpy as np


DATA = HERE / "public_data" / "q39_information3_strongmax"
DERIVED = DATA / "q39_derived_cache.npz"
CONNECTED = DATA / "q39_connected_cache.npy"
Q39_CYCLES = HERE / "Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_CYCLES.csv.gz"

RESULTS = HERE / "Q39A_POST_RESULT_SEAM_PARITY_RESULTS.json"
CYCLES = HERE / "Q39A_POST_RESULT_SEAM_PARITY_CYCLES.csv.gz"
SEAM_PNG = HERE / "Q39A_POST_RESULT_SEAM_PARITY_DIAGNOSTICS.png"
SEAM_SVG = HERE / "Q39A_POST_RESULT_SEAM_PARITY_DIAGNOSTICS.svg"
PURITY_PNG = HERE / "Q39A_POST_RESULT_PURITY_NORMALIZATION_DIAGNOSTICS.png"
PURITY_SVG = HERE / "Q39A_POST_RESULT_PURITY_NORMALIZATION_DIAGNOSTICS.svg"

EPS = 1e-12
BOOTSTRAP_DRAWS = 20_000
BOOTSTRAP_SEED = 391027
QUADRANT_NAMES = {0: "Q++", 1: "Q−+", 2: "Q−−", 3: "Q+−"}


def average_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=np.float64)
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and values[order[end]] == values[order[start]]:
            end += 1
        ranks[order[start:end]] = (start + 1 + end) / 2
        start = end
    return ranks


def spearman(x: np.ndarray, y: np.ndarray) -> dict[str, float | int]:
    finite = np.isfinite(x) & np.isfinite(y)
    x, y = np.asarray(x[finite]), np.asarray(y[finite])
    if len(x) < 3:
        return {"rho": float("nan"), "p_value": float("nan"), "n": len(x)}
    rho = float(np.corrcoef(average_ranks(x), average_ranks(y))[0, 1])
    denominator = max(1 - rho * rho, EPS)
    z = abs(rho) * math.sqrt((len(x) - 2) / denominator)
    return {
        "rho": rho,
        "p_value": float(math.erfc(z / math.sqrt(2))),
        "n": len(x),
        "p_method": "large-sample normal approximation",
    }


def partial_spearman(
    x: np.ndarray, y: np.ndarray, control: np.ndarray
) -> dict[str, float | int]:
    finite = np.isfinite(x) & np.isfinite(y) & np.isfinite(control)
    x_rank = average_ranks(np.asarray(x[finite], dtype=np.float64))
    y_rank = average_ranks(np.asarray(y[finite], dtype=np.float64))
    z_rank = average_ranks(np.asarray(control[finite], dtype=np.float64))
    design = np.column_stack((np.ones(len(z_rank)), z_rank))
    x_residual = x_rank - design @ np.linalg.lstsq(design, x_rank, rcond=None)[0]
    y_residual = y_rank - design @ np.linalg.lstsq(design, y_rank, rcond=None)[0]
    rho = float(np.corrcoef(x_residual, y_residual)[0, 1])
    denominator = max(1 - rho * rho, EPS)
    z_value = abs(rho) * math.sqrt((len(x_residual) - 3) / denominator)
    return {
        "rho": rho,
        "p_value": float(math.erfc(z_value / math.sqrt(2))),
        "n": len(x_residual),
        "control": "rank(target_norm)",
        "method": "linear residuals of ranks",
    }


def auc_binary(labels: np.ndarray, score: np.ndarray) -> float:
    finite = np.isfinite(score)
    labels = np.asarray(labels[finite], dtype=bool)
    score = np.asarray(score[finite], dtype=np.float64)
    positive = int(np.sum(labels))
    negative = int(np.sum(~labels))
    if not positive or not negative:
        return float("nan")
    ranks = average_ranks(score)
    rank_sum = float(np.sum(ranks[labels]))
    return float(
        (rank_sum - positive * (positive + 1) / 2) / (positive * negative)
    )


def development_coordinates(line: np.ndarray) -> dict[str, float]:
    development = np.asarray(line[:250], dtype=np.float64)
    q05, q20, q95 = np.quantile(development, [0.05, 0.20, 0.95])
    return {
        "q05": float(q05),
        "q20": float(q20),
        "q95": float(q95),
        "centre": float((q05 + q95) / 2),
        "radius": float((q95 - q05) / 2),
        "flow_scale": float(np.quantile(np.abs(np.diff(development)), 0.95)),
    }


def q36_troughs(line: np.ndarray, q20: float) -> list[int]:
    """Apply Q36's frozen trough rule and seven-slice separation."""
    kept: list[int] = []
    for time in range(258, 492):
        if not (
            line[time - 1] > line[time]
            and line[time] <= line[time + 1]
            and line[time] <= q20
        ):
            continue
        if kept and time - kept[-1] < 7:
            continue
        kept.append(time)
    return kept


def matrix_mean(
    connected: np.ndarray, seed: int, pair: int, start: int, end: int
) -> np.ndarray:
    return np.mean(
        connected[seed, start : end + 1, pair],
        axis=0,
        dtype=np.float64,
    )


def matrix_scores(predicted: np.ndarray, actual: np.ndarray) -> tuple[float, float]:
    target_norm = float(np.linalg.norm(actual))
    predicted_norm = float(np.linalg.norm(predicted))
    nrmse = float(np.linalg.norm(predicted - actual) / (target_norm + EPS))
    cosine = float(
        np.sum(predicted * actual)
        / (predicted_norm * target_norm + EPS)
    )
    return nrmse, cosine


def cluster_rate_difference(
    condition: np.ndarray,
    negative: np.ndarray,
    seeds: np.ndarray,
    seed: int,
) -> dict[str, object]:
    unique = np.unique(seeds)
    counts = np.zeros((len(unique), 4), dtype=np.float64)
    for index, value in enumerate(unique):
        chosen = seeds == value
        for column, flag in enumerate((condition, ~condition)):
            selected = chosen & flag
            counts[index, 2 * column] = np.sum(negative[selected])
            counts[index, 2 * column + 1] = np.sum(selected)

    def difference(block: np.ndarray) -> np.ndarray:
        yes = np.sum(block[..., 0], axis=-1) / np.maximum(
            np.sum(block[..., 1], axis=-1), 1
        )
        no = np.sum(block[..., 2], axis=-1) / np.maximum(
            np.sum(block[..., 3], axis=-1), 1
        )
        return yes - no

    observed = float(difference(counts[None, ...])[0])
    rng = np.random.default_rng(seed)
    indices = rng.integers(
        0, len(unique), size=(BOOTSTRAP_DRAWS, len(unique))
    )
    draws = difference(counts[indices])
    yes_rate = float(np.sum(counts[:, 0]) / max(np.sum(counts[:, 1]), 1))
    no_rate = float(np.sum(counts[:, 2]) / max(np.sum(counts[:, 3]), 1))
    return {
        "condition_negative_fraction": yes_rate,
        "complement_negative_fraction": no_rate,
        "difference": observed,
        "seed_cluster_bootstrap_ci95": [
            float(np.quantile(draws, 0.025)),
            float(np.quantile(draws, 0.975)),
        ],
        "bootstrap_p_difference_le_0": float(
            (np.sum(draws <= 0) + 1) / (BOOTSTRAP_DRAWS + 1)
        ),
        "represented_seeds": int(len(unique)),
    }


def lineage_method_summary(
    rows: list[dict[str, object]], method: str
) -> dict[str, float]:
    grouped: dict[tuple[int, int], list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["seed"]), int(row["pair_index"]))].append(
            (
                float(row[f"{method}_nrmse"]),
                float(row[f"{method}_cosine"]),
            )
        )
    lineage = np.asarray(
        [
            (
                np.mean([item[0] for item in values]),
                np.mean([item[1] for item in values]),
            )
            for values in grouped.values()
        ],
        dtype=np.float64,
    )
    return {
        "event_mean_nrmse": float(
            np.mean([float(row[f"{method}_nrmse"]) for row in rows])
        ),
        "event_median_nrmse": float(
            np.median([float(row[f"{method}_nrmse"]) for row in rows])
        ),
        "event_mean_cosine": float(
            np.mean([float(row[f"{method}_cosine"]) for row in rows])
        ),
        "event_median_cosine": float(
            np.median([float(row[f"{method}_cosine"]) for row in rows])
        ),
        "negative_cosine_fraction": float(
            np.mean([float(row[f"{method}_cosine"]) < 0 for row in rows])
        ),
        "lineage_mean_nrmse": float(np.mean(lineage[:, 0])),
        "lineage_mean_cosine": float(np.mean(lineage[:, 1])),
    }


def cluster_metric_advantage(
    rows: list[dict[str, object]],
    candidate: str,
    control: str,
    metric: str,
    seed: int,
) -> dict[str, object]:
    lineages: dict[tuple[int, int], list[float]] = defaultdict(list)
    for row in rows:
        difference = float(row[f"{control}_{metric}"]) - float(
            row[f"{candidate}_{metric}"]
        )
        lineages[(int(row["seed"]), int(row["pair_index"]))].append(difference)
    seeds: dict[int, list[float]] = defaultdict(list)
    for (seed_id, _pair), values in lineages.items():
        seeds[seed_id].append(float(np.mean(values)))
    seed_values = np.asarray(
        [np.mean(seeds[value]) for value in sorted(seeds)], dtype=np.float64
    )
    rng = np.random.default_rng(seed)
    indices = rng.integers(
        0, len(seed_values), size=(BOOTSTRAP_DRAWS, len(seed_values))
    )
    draws = np.mean(seed_values[indices], axis=1)
    return {
        "candidate": candidate,
        "control": control,
        "metric": metric,
        "lineage_then_seed_balanced_advantage": float(np.mean(seed_values)),
        "seed_cluster_bootstrap_ci95": [
            float(np.quantile(draws, 0.025)),
            float(np.quantile(draws, 0.975)),
        ],
        "bootstrap_p_advantage_le_0": float(
            (np.sum(draws <= 0) + 1) / (BOOTSTRAP_DRAWS + 1)
        ),
        "represented_seeds": int(len(seed_values)),
    }


def main() -> None:
    required = (DERIVED, CONNECTED, Q39_CYCLES)
    missing = [path for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing Q39 inputs: {missing}")

    with gzip.open(Q39_CYCLES, "rt", newline="", encoding="utf-8") as stream:
        source_rows = list(csv.DictReader(stream))
    derived = np.load(DERIVED, allow_pickle=False)
    closure = np.asarray(derived["closure"], dtype=np.float64)
    connected = np.load(CONNECTED, mmap_mode="r")

    lineage_geometry: dict[tuple[int, int], dict[str, object]] = {}
    for row in source_rows:
        key = (int(row["seed"]), int(row["pair_index"]))
        if key in lineage_geometry:
            continue
        seed, pair = key
        coordinates = development_coordinates(closure[seed, :, pair])
        lineage_geometry[key] = {
            **coordinates,
            "troughs": q36_troughs(
                closure[seed, :, pair], float(coordinates["q20"])
            ),
        }

    rows: list[dict[str, object]] = []
    trough_paths: dict[str, list[np.ndarray]] = {
        "same_orientation": [],
        "reversed_orientation": [],
    }

    for source in source_rows:
        seed = int(source["seed"])
        pair = int(source["pair_index"])
        geometry = lineage_geometry[(seed, pair)]
        h_line = closure[seed, :, pair]

        identities = [
            matrix_mean(
                connected,
                seed,
                pair,
                int(source[f"q{index}_start"]),
                int(source[f"q{index}_end"]),
            )
            for index in range(1, 5)
        ]
        c1, c2, c3, c4 = identities
        relation_delta = c1 - c2
        predicted = relation_delta + c3
        absolute_error = float(np.linalg.norm(predicted - c4))
        target_norm = float(np.linalg.norm(c4))
        cosine = float(source["ara_cosine"])
        negative = cosine < 0
        predicted_c3_cosine = float(
            np.sum(predicted * c3)
            / (np.linalg.norm(predicted) * np.linalg.norm(c3) + EPS)
        )
        visible_anti_to_c3 = predicted_c3_cosine < 0
        delta_c3_projection = float(
            np.sum(relation_delta * c3) / (np.sum(c3 * c3) + EPS)
        )

        cycle_start = int(source["q1_start"])
        cycle_end = int(source["q4_end"])
        q4_start = int(source["q4_start"])
        q4_end = int(source["q4_end"])
        q3_start = int(source["q3_start"])
        cycle_slice = h_line[cycle_start : cycle_end + 1]
        minimum_time = cycle_start + int(np.argmin(cycle_slice))
        local_times = np.concatenate(
            (
                np.arange(minimum_time - 7, minimum_time, dtype=int),
                np.arange(minimum_time + 1, minimum_time + 8, dtype=int),
            )
        )
        local_times = local_times[(local_times >= 0) & (local_times < 500)]
        local_baseline = float(np.median(h_line[local_times]))
        minimum_h = float(h_line[minimum_time])
        radius = max(float(geometry["radius"]), EPS)
        minimum_u = (minimum_h - float(geometry["centre"])) / radius
        target_mean_h = float(np.mean(h_line[q4_start : q4_end + 1]))
        target_mean_u = (
            target_mean_h - float(geometry["centre"])
        ) / radius
        flow_scale = max(float(geometry["flow_scale"]), EPS)
        target_mean_v = float(
            np.mean(np.diff(h_line)[q4_start : q4_end + 1]) / flow_scale
        )

        retained_troughs = list(geometry["troughs"])
        trough_in_cycle = any(
            cycle_start <= time <= cycle_end for time in retained_troughs
        )
        trough_in_target = any(
            q4_start <= time <= q4_end for time in retained_troughs
        )
        trough_in_late_half = any(
            q3_start <= time <= q4_end for time in retained_troughs
        )
        deepest_in_target = q4_start <= minimum_time <= q4_end
        deep_q05 = minimum_h <= float(geometry["q05"])
        target_low_release = int(source["q4"]) == 2

        output: dict[str, object] = {
            **source,
            "negative_cosine": int(negative),
            "absolute_error": absolute_error,
            "target_closure": float(np.cbrt(abs(np.linalg.det(c4)))),
            "predicted_closure": float(np.cbrt(abs(np.linalg.det(predicted)))),
            "cycle_minimum_time": minimum_time,
            "cycle_minimum_h": minimum_h,
            "cycle_minimum_u": float(minimum_u),
            "cycle_trough_retention": float(
                minimum_h / (local_baseline + EPS)
            ),
            "target_mean_h": target_mean_h,
            "target_mean_u": float(target_mean_u),
            "target_mean_v": target_mean_v,
            "q36_trough_in_cycle": int(trough_in_cycle),
            "q36_trough_in_target": int(trough_in_target),
            "q36_trough_in_late_half": int(trough_in_late_half),
            "deepest_trough_in_target": int(deepest_in_target),
            "cycle_below_development_q05": int(deep_q05),
            "target_low_release_qminusminus": int(target_low_release),
            "predicted_c3_cosine": predicted_c3_cosine,
            "visible_prediction_anti_to_c3": int(visible_anti_to_c3),
            "relation_delta_c3_projection": delta_c3_projection,
        }

        adjusted_predictions = {
            "no_parity": predicted,
            "q36_target_parity": -predicted if trough_in_target else predicted,
            "q36_late_half_parity": (
                -predicted if trough_in_late_half else predicted
            ),
            "deep_q05_parity": -predicted if deep_q05 else predicted,
            "low_release_parity": (
                -predicted if target_low_release else predicted
            ),
            # These three rules use only C1, C2 and C3. They never inspect C4.
            "visible_parent_parity": (
                -predicted if visible_anti_to_c3 else predicted
            ),
            "visible_relation_reversal": (
                c3 - relation_delta if visible_anti_to_c3 else predicted
            ),
            "visible_persistence_guard": (
                c3 if visible_anti_to_c3 else predicted
            ),
            # Invalid predictive ceiling: target cosine determines the flag.
            "oracle_negative_parity": -predicted if negative else predicted,
        }
        for name, adjusted in adjusted_predictions.items():
            nrmse, adjusted_cosine = matrix_scores(adjusted, c4)
            output[f"{name}_nrmse"] = nrmse
            output[f"{name}_cosine"] = adjusted_cosine

        rows.append(output)

        if 7 <= minimum_time <= 492:
            path = h_line[minimum_time - 7 : minimum_time + 8]
            normalized_path = path / (local_baseline + EPS)
            group = (
                "reversed_orientation" if negative else "same_orientation"
            )
            trough_paths[group].append(normalized_path)

    with gzip.open(CYCLES, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    negative = np.asarray([bool(int(row["negative_cosine"])) for row in rows])
    seeds = np.asarray([int(row["seed"]) for row in rows], dtype=int)
    minimum_u = np.asarray(
        [float(row["cycle_minimum_u"]) for row in rows], dtype=np.float64
    )
    trough_retention = np.asarray(
        [float(row["cycle_trough_retention"]) for row in rows],
        dtype=np.float64,
    )
    target_u = np.asarray(
        [float(row["target_mean_u"]) for row in rows], dtype=np.float64
    )
    target_v = np.asarray(
        [float(row["target_mean_v"]) for row in rows], dtype=np.float64
    )
    target_norm = np.asarray(
        [float(row["target_norm"]) for row in rows], dtype=np.float64
    )
    purity = np.asarray(
        [float(row["target_purity"]) for row in rows], dtype=np.float64
    )
    nrmse = np.asarray(
        [float(row["ara_nrmse"]) for row in rows], dtype=np.float64
    )
    absolute_error = np.asarray(
        [float(row["absolute_error"]) for row in rows], dtype=np.float64
    )
    q4 = np.asarray([int(row["q4"]) for row in rows], dtype=int)

    group_summary = {}
    for name, mask in (
        ("same_orientation", ~negative),
        ("reversed_orientation", negative),
    ):
        group_summary[name] = {
            "cycles": int(np.sum(mask)),
            "fraction": float(np.mean(mask)),
            "median_cosine": float(
                np.median(
                    [float(rows[i]["ara_cosine"]) for i in np.flatnonzero(mask)]
                )
            ),
            "median_cycle_minimum_u": float(np.median(minimum_u[mask])),
            "median_trough_retention": float(
                np.median(trough_retention[mask])
            ),
            "median_target_u": float(np.median(target_u[mask])),
            "median_target_v": float(np.median(target_v[mask])),
            "median_target_norm": float(np.median(target_norm[mask])),
            "median_purity": float(np.median(purity[mask])),
            "q36_trough_in_target_fraction": float(
                np.mean(
                    [
                        bool(int(rows[i]["q36_trough_in_target"]))
                        for i in np.flatnonzero(mask)
                    ]
                )
            ),
            "deep_q05_fraction": float(
                np.mean(
                    [
                        bool(int(rows[i]["cycle_below_development_q05"]))
                        for i in np.flatnonzero(mask)
                    ]
                )
            ),
        }

    quadrant_summary = {}
    for label in range(4):
        selected = q4 == label
        quadrant_summary[QUADRANT_NAMES[label]] = {
            "cycles": int(np.sum(selected)),
            "negative_cosine_cycles": int(np.sum(negative[selected])),
            "negative_cosine_fraction": float(np.mean(negative[selected])),
            "median_cycle_minimum_u": float(np.median(minimum_u[selected])),
            "median_target_u": float(np.median(target_u[selected])),
            "median_target_v": float(np.median(target_v[selected])),
        }

    rule_names = (
        "no_parity",
        "q36_target_parity",
        "q36_late_half_parity",
        "deep_q05_parity",
        "low_release_parity",
        "visible_parent_parity",
        "visible_relation_reversal",
        "visible_persistence_guard",
        "oracle_negative_parity",
    )
    rule_summary = {
        name: lineage_method_summary(rows, name) for name in rule_names
    }
    visible_anti = np.asarray(
        [bool(int(row["visible_prediction_anti_to_c3"])) for row in rows]
    )
    q39_baselines = ("persistence", "no_flip", "linear", "mean", "wrong_order")
    relation_reversal_nrmse = np.asarray(
        [float(row["visible_relation_reversal_nrmse"]) for row in rows]
    )
    original_nrmse = np.asarray(
        [float(row["no_parity_nrmse"]) for row in rows]
    )
    visible_rule_comparison = {
        "cycles_changed": int(np.sum(visible_anti)),
        "changed_cycles_improved": int(
            np.sum(
                visible_anti
                & (relation_reversal_nrmse < original_nrmse - 1e-15)
            )
        ),
        "changed_cycles_tied": int(
            np.sum(
                visible_anti
                & (np.abs(relation_reversal_nrmse - original_nrmse) <= 1e-15)
            )
        ),
        "changed_cycles_worsened": int(
            np.sum(
                visible_anti
                & (relation_reversal_nrmse > original_nrmse + 1e-15)
            )
        ),
        "flagged_median_original_nrmse": float(
            np.median(original_nrmse[visible_anti])
        ),
        "flagged_median_corrected_nrmse": float(
            np.median(relation_reversal_nrmse[visible_anti])
        ),
        "pairwise_win_fraction_vs_q39_baselines": {
            baseline: float(
                np.mean(
                    relation_reversal_nrmse
                    < np.asarray(
                        [float(row[f"{baseline}_nrmse"]) for row in rows]
                    )
                )
            )
            for baseline in q39_baselines
        },
        "single_best_fraction_against_all_five_q39_baselines": float(
            np.mean(
                [
                    float(row["visible_relation_reversal_nrmse"])
                    < min(
                        float(row[f"{baseline}_nrmse"])
                        for baseline in q39_baselines
                    )
                    for row in rows
                ]
            )
        ),
        "cluster_advantage_over_original_q39": cluster_metric_advantage(
            rows,
            "visible_relation_reversal",
            "no_parity",
            "nrmse",
            BOOTSTRAP_SEED + 20,
        ),
    }

    q36_target = np.asarray(
        [bool(int(row["q36_trough_in_target"])) for row in rows]
    )
    q36_late = np.asarray(
        [bool(int(row["q36_trough_in_late_half"])) for row in rows]
    )
    deep_q05 = np.asarray(
        [bool(int(row["cycle_below_development_q05"])) for row in rows]
    )
    low_release = q4 == 2

    true_positive = int(np.sum(visible_anti & negative))
    false_positive = int(np.sum(visible_anti & ~negative))
    false_negative = int(np.sum(~visible_anti & negative))
    true_negative = int(np.sum(~visible_anti & ~negative))
    visible_confusion = {
        "flagged_cycles": int(np.sum(visible_anti)),
        "flagged_fraction": float(np.mean(visible_anti)),
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "true_negative": true_negative,
        "precision_for_negative_target_cosine": float(
            true_positive / max(true_positive + false_positive, 1)
        ),
        "recall_for_negative_target_cosine": float(
            true_positive / max(true_positive + false_negative, 1)
        ),
        "specificity": float(
            true_negative / max(true_negative + false_positive, 1)
        ),
    }

    purity_q25, purity_q75 = np.quantile(purity, [0.25, 0.75])
    purity_crosscheck = {
        "nrmse_vs_purity": spearman(nrmse, purity),
        "absolute_error_vs_purity": spearman(absolute_error, purity),
        "target_norm_vs_purity": spearman(target_norm, purity),
        "nrmse_vs_target_norm": spearman(nrmse, target_norm),
        "partial_nrmse_vs_purity_controlling_target_norm": partial_spearman(
            nrmse, purity, target_norm
        ),
        "lowest_purity_quartile": {
            "cut": float(purity_q25),
            "cycles": int(np.sum(purity <= purity_q25)),
            "median_nrmse": float(np.median(nrmse[purity <= purity_q25])),
            "median_absolute_error": float(
                np.median(absolute_error[purity <= purity_q25])
            ),
            "median_target_norm": float(
                np.median(target_norm[purity <= purity_q25])
            ),
        },
        "highest_purity_quartile": {
            "cut": float(purity_q75),
            "cycles": int(np.sum(purity >= purity_q75)),
            "median_nrmse": float(np.median(nrmse[purity >= purity_q75])),
            "median_absolute_error": float(
                np.median(absolute_error[purity >= purity_q75])
            ),
            "median_target_norm": float(
                np.median(target_norm[purity >= purity_q75])
            ),
        },
    }

    summary = {
        "test_id": "Q39A-POST-RESULT-SEAM-PARITY-AUDIT-v1",
        "status": "POST-RESULT EXPLORATORY DIAGNOSTIC",
        "q39_verdict_unchanged": "INCONCLUSIVE — ELIGIBILITY",
        "population": {
            "cycles": len(rows),
            "represented_seeds": int(len(np.unique(seeds))),
            "represented_lineages": int(
                len({(int(row["seed"]), int(row["pair_index"])) for row in rows})
            ),
            "negative_cosine_cycles": int(np.sum(negative)),
            "negative_cosine_fraction": float(np.mean(negative)),
        },
        "orientation_groups": group_summary,
        "target_quadrants": quadrant_summary,
        "seam_association": {
            "auc_deeper_minimum_u_predicts_negative": auc_binary(
                negative, -minimum_u
            ),
            "auc_deeper_trough_retention_predicts_negative": auc_binary(
                negative, -trough_retention
            ),
            "q36_trough_in_target": cluster_rate_difference(
                q36_target, negative, seeds, BOOTSTRAP_SEED + 1
            ),
            "q36_trough_in_late_half": cluster_rate_difference(
                q36_late, negative, seeds, BOOTSTRAP_SEED + 2
            ),
            "below_development_q05": cluster_rate_difference(
                deep_q05, negative, seeds, BOOTSTRAP_SEED + 3
            ),
            "target_low_release_qminusminus": cluster_rate_difference(
                low_release, negative, seeds, BOOTSTRAP_SEED + 4
            ),
            "visible_prediction_anti_to_c3": {
                **cluster_rate_difference(
                    visible_anti, negative, seeds, BOOTSTRAP_SEED + 5
                ),
                **visible_confusion,
                "definition": "cos(C1-C2+C3, C3) < 0; uses no C4 value",
            },
        },
        "parity_rule_diagnostics": rule_summary,
        "visible_relation_reversal_comparison": visible_rule_comparison,
        "purity_normalization_audit": purity_crosscheck,
        "boundaries": [
            "Q39A was defined after Q39 outcomes were open and cannot rescue or alter Q39's frozen verdict.",
            "The oracle parity rule uses target cosine and is only an unattainable diagnostic ceiling.",
            "Visible C3 guards were conceived after Q39 outcomes were open and require untouched replication.",
            "The Q36 seam detector is theory-derived and previously frozen, but its use as a Q39 parity classifier is post-result.",
            "Quadrant timing still uses the observed scalar closure-flow path.",
            "Absolute matrix error removes division by target norm but remains simulator- and representation-specific.",
        ],
    }
    RESULTS.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    make_seam_figure(
        rows,
        negative,
        minimum_u,
        trough_retention,
        q4,
        trough_paths,
        rule_summary,
    )
    make_purity_figure(
        purity,
        nrmse,
        absolute_error,
        target_norm,
        purity_crosscheck,
    )
    print(json.dumps(summary, indent=2), flush=True)


def make_seam_figure(
    rows: list[dict[str, object]],
    negative: np.ndarray,
    minimum_u: np.ndarray,
    trough_retention: np.ndarray,
    q4: np.ndarray,
    trough_paths: dict[str, list[np.ndarray]],
    rule_summary: dict[str, dict[str, float]],
) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "figure.facecolor": "#f7f8fa",
            "axes.facecolor": "#fbfcfd",
            "axes.edgecolor": "#49515a",
            "text.color": "#20262e",
            "axes.labelcolor": "#20262e",
            "xtick.color": "#49515a",
            "ytick.color": "#49515a",
        }
    )
    blue, gold, grey, dark = "#4f79b7", "#d6a23e", "#cfd5dc", "#252c34"
    fig, axes = plt.subplots(2, 3, figsize=(16, 9.5))
    fig.suptitle(
        "Q39A — post-result orientation and determinant-seam diagnostics",
        fontsize=16,
        fontweight="bold",
        y=0.985,
    )
    fig.text(
        0.5,
        0.951,
        (
            f"{len(rows):,} already-open Q39 cycles · "
            f"{int(np.sum(negative)):,} negative-cosine reconstructions · "
            "Q39 verdict unchanged"
        ),
        ha="center",
        color="#58616c",
    )

    cosine = np.asarray([float(row["ara_cosine"]) for row in rows])
    ax = axes[0, 0]
    bins = np.linspace(-1, 1, 81)
    ax.hist(cosine[cosine >= 0], bins=bins, color=blue, alpha=0.85, label="same orientation")
    ax.hist(cosine[cosine < 0], bins=bins, color=gold, alpha=0.90, label="reversed orientation")
    ax.axvline(0, color=dark, lw=1)
    ax.set_yscale("log")
    ax.set(
        title="ARA reconstruction cosine distribution",
        xlabel="cosine between predicted and actual fourth quadrant",
        ylabel="cycles (log scale)",
    )
    ax.legend(frameon=False)
    ax.grid(axis="y", color="#e1e5e9", lw=0.5)

    ax = axes[0, 1]
    same = minimum_u[~negative]
    reversed_values = minimum_u[negative]
    box = ax.boxplot(
        [same, reversed_values],
        tick_labels=["same", "reversed"],
        showfliers=False,
        patch_artist=True,
    )
    box["boxes"][0].set_facecolor(blue)
    box["boxes"][1].set_facecolor(gold)
    for patch in box["boxes"]:
        patch.set_edgecolor(dark)
    ax.axhline(-1, color=dark, linestyle="--", lw=1, label="development 5% boundary")
    ax.set(
        title="Deepest closure position within each cycle",
        xlabel="reconstruction orientation",
        ylabel="minimum development-normalized closure u",
    )
    ax.legend(frameon=False)
    ax.grid(axis="y", color="#e1e5e9", lw=0.5)

    ax = axes[0, 2]
    names = [QUADRANT_NAMES[index] for index in range(4)]
    rates = [
        float(np.mean(negative[q4 == index])) if np.any(q4 == index) else 0
        for index in range(4)
    ]
    counts = [int(np.sum(q4 == index)) for index in range(4)]
    bars = ax.bar(names, rates, color=[blue, grey, gold, "#8fa1b3"], edgecolor=dark)
    for bar, rate, count in zip(bars, rates, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            rate + 0.005,
            f"{rate:.1%}\n(n={count:,})",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    ax.set_ylim(0, max(rates) * 1.25 + 0.01)
    ax.set(
        title="Negative-cosine rate by target quadrant",
        xlabel="fourth visit in closure–flow plane",
        ylabel="negative-cosine fraction",
    )
    ax.grid(axis="y", color="#e1e5e9", lw=0.5)

    ax = axes[1, 0]
    offsets = np.arange(-7, 8)
    for name, color, label in (
        ("same_orientation", blue, "same orientation"),
        ("reversed_orientation", gold, "reversed orientation"),
    ):
        paths = np.asarray(trough_paths[name], dtype=np.float64)
        median = np.median(paths, axis=0)
        q25, q75 = np.quantile(paths, [0.25, 0.75], axis=0)
        ax.plot(offsets, median, color=color, lw=2.3, label=label)
        ax.fill_between(offsets, q25, q75, color=color, alpha=0.15)
    ax.axvline(0, color=dark, linestyle="--", lw=1)
    ax.axhline(1, color="#7f8790", lw=0.8)
    ax.set(
        title="Closure path around each cycle's deepest trough",
        xlabel="slices from deepest determinant-closure point",
        ylabel="closure / local 14-slice median",
    )
    ax.legend(frameon=False)
    ax.grid(color="#e1e5e9", lw=0.5)

    ax = axes[1, 1]
    bins_u = np.asarray(
        [-np.inf, -1.01, -1.00, -0.99, -0.97, -0.94, -0.90, -0.80, np.inf]
    )
    labels_u = [
        "<−1.01",
        "−1.01…−1",
        "−1…−.99",
        "−.99…−.97",
        "−.97…−.94",
        "−.94…−.90",
        "−.90…−.80",
        "≥−.80",
    ]
    heat = np.full((4, len(labels_u)), np.nan)
    annotations = np.empty_like(heat, dtype=object)
    for quadrant in range(4):
        for index in range(len(labels_u)):
            chosen = (
                (q4 == quadrant)
                & (minimum_u > bins_u[index])
                & (minimum_u <= bins_u[index + 1])
            )
            if np.any(chosen):
                heat[quadrant, index] = np.mean(negative[chosen])
                annotations[quadrant, index] = f"{heat[quadrant, index]:.0%}\n{np.sum(chosen)}"
            else:
                annotations[quadrant, index] = "—"
    image = ax.imshow(heat, cmap="Blues", vmin=0, vmax=max(0.25, np.nanmax(heat)))
    for row_index in range(4):
        for column_index in range(len(labels_u)):
            value = heat[row_index, column_index]
            ax.text(
                column_index,
                row_index,
                annotations[row_index, column_index],
                ha="center",
                va="center",
                fontsize=7,
                color="white" if np.isfinite(value) and value > 0.16 else dark,
            )
    ax.set_xticks(range(len(labels_u)), labels=labels_u, rotation=25, ha="right")
    ax.set_yticks(range(4), labels=names)
    ax.set(
        title="Negative rate by quadrant and trough depth",
        xlabel="cycle minimum u bin",
        ylabel="target quadrant",
    )
    fig.colorbar(image, ax=ax, label="negative-cosine fraction")

    ax = axes[1, 2]
    plotted_rules = [
        "no_parity",
        "q36_target_parity",
        "deep_q05_parity",
        "visible_parent_parity",
        "visible_relation_reversal",
        "visible_persistence_guard",
        "oracle_negative_parity",
    ]
    plotted_labels = [
        "Q39 unchanged",
        "flip: Q36 trough in target",
        "flip: below dev q05",
        "visible whole-sign guard",
        "visible relation reversal",
        "visible persistence guard",
        "oracle ceiling",
    ]
    values = [rule_summary[name]["lineage_mean_nrmse"] for name in plotted_rules]
    colors = [blue, grey, grey, gold, gold, gold, "#9ca4ad"]
    bars = ax.barh(plotted_labels, values, color=colors, edgecolor=dark)
    ax.invert_yaxis()
    for bar, value in zip(bars, values):
        ax.text(
            value + 0.015,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.3f}",
            va="center",
            fontsize=8,
        )
    ax.set_xlim(0, max(values) * 1.18)
    ax.set(
        title="Post-result parity-rule diagnostics",
        xlabel="lineage-mean NRMSE (lower is better)",
    )
    ax.grid(axis="x", color="#e1e5e9", lw=0.5)

    fig.text(
        0.01,
        0.012,
        (
            "Post-result diagnostic on Q39's already-open archive. "
            "The oracle uses target labels and is not a valid predictor."
        ),
        fontsize=8,
        color="#58616c",
    )
    fig.tight_layout(rect=(0.015, 0.045, 0.985, 0.915), h_pad=2.0, w_pad=1.6)
    fig.savefig(SEAM_PNG, dpi=180, bbox_inches="tight", pad_inches=0.18)
    fig.savefig(SEAM_SVG, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)


def make_purity_figure(
    purity: np.ndarray,
    nrmse: np.ndarray,
    absolute_error: np.ndarray,
    target_norm: np.ndarray,
    audit: dict[str, object],
) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "figure.facecolor": "#f7f8fa",
            "axes.facecolor": "#fbfcfd",
            "text.color": "#20262e",
        }
    )
    blue, gold, dark = "#4f79b7", "#d6a23e", "#252c34"
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.3))
    fig.suptitle(
        "Q39A — purity and target-amplitude normalization audit",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )
    fig.text(
        0.5,
        0.925,
        "Same 17,967 Q39 target visits · absolute error removes division by ‖C₄‖",
        ha="center",
        color="#58616c",
    )

    ax = axes[0]
    hb = ax.hexbin(
        purity,
        target_norm,
        gridsize=45,
        bins="log",
        mincnt=1,
        cmap="Blues",
    )
    ax.set(
        title="Target relation magnitude by purity",
        xlabel="target-visit two-qubit purity",
        ylabel="target connected-lattice norm ‖C₄‖",
    )
    ax.set_yscale("log")
    fig.colorbar(hb, ax=ax, label="log cycle count")

    quantiles = np.quantile(purity, np.linspace(0, 1, 11))
    centres, nrmse_median, absolute_median, norm_median = [], [], [], []
    for index in range(10):
        if index == 9:
            chosen = (purity >= quantiles[index]) & (purity <= quantiles[index + 1])
        else:
            chosen = (purity >= quantiles[index]) & (purity < quantiles[index + 1])
        centres.append(float(np.median(purity[chosen])))
        nrmse_median.append(float(np.median(nrmse[chosen])))
        absolute_median.append(float(np.median(absolute_error[chosen])))
        norm_median.append(float(np.median(target_norm[chosen])))

    ax = axes[1]
    nrmse_index = np.asarray(nrmse_median) / max(np.median(nrmse), EPS)
    absolute_index = np.asarray(absolute_median) / max(
        np.median(absolute_error), EPS
    )
    norm_index = np.asarray(norm_median) / max(np.median(target_norm), EPS)
    ax.plot(centres, nrmse_index, color=gold, marker="o", lw=2, label="NRMSE")
    ax.plot(
        centres,
        absolute_index,
        color=blue,
        marker="s",
        lw=2,
        label="absolute error",
    )
    ax.plot(
        centres,
        norm_index,
        color=dark,
        marker="^",
        lw=1.6,
        linestyle="--",
        label="target norm",
    )
    ax.axhline(1, color="#89919a", lw=0.8)
    ax.set(
        title="Median quantities across purity deciles",
        xlabel="median purity in decile",
        ylabel="index to overall median (1 = overall median)",
    )
    ax.legend(frameon=False)
    ax.grid(color="#e1e5e9", lw=0.5)

    ax = axes[2]
    labels = [
        "NRMSE vs purity",
        "absolute error vs purity",
        "target norm vs purity",
        "partial NRMSE vs purity\n(controlling target norm)",
    ]
    values = [
        audit["nrmse_vs_purity"]["rho"],
        audit["absolute_error_vs_purity"]["rho"],
        audit["target_norm_vs_purity"]["rho"],
        audit["partial_nrmse_vs_purity_controlling_target_norm"]["rho"],
    ]
    colors = [gold if value > 0 else blue for value in values]
    bars = ax.barh(labels, values, color=colors, edgecolor=dark)
    ax.axvline(0, color=dark, lw=1)
    ax.invert_yaxis()
    for bar, value in zip(bars, values):
        ax.text(
            value + (0.01 if value >= 0 else -0.01),
            bar.get_y() + bar.get_height() / 2,
            f"{value:+.3f}",
            ha="left" if value >= 0 else "right",
            va="center",
            fontsize=8,
        )
    limit = max(abs(float(value)) for value in values) * 1.30
    ax.set_xlim(-limit, limit)
    ax.set(
        title="Spearman associations",
        xlabel="rank correlation ρ",
    )
    ax.grid(axis="x", color="#e1e5e9", lw=0.5)

    fig.text(
        0.01,
        0.012,
        (
            "Post-result audit. Correlation is descriptive; purity, target norm "
            "and reconstruction error are not independent physical interventions."
        ),
        fontsize=8,
        color="#58616c",
    )
    fig.tight_layout(rect=(0.015, 0.06, 0.985, 0.88), w_pad=2.0)
    fig.savefig(PURITY_PNG, dpi=180, bbox_inches="tight", pad_inches=0.18)
    fig.savefig(PURITY_SVG, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)


if __name__ == "__main__":
    main()

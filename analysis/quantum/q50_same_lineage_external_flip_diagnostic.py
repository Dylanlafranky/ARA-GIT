"""Q50 post-Q49 same-lineage external ARA flip diagnostic."""

from __future__ import annotations

import csv
import gzip
import json
import math
import pathlib
from collections import defaultdict

import numpy as np

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None


HERE = pathlib.Path(__file__).resolve().parent
EVENTS_PATH = HERE / "Q49_EXTERNAL_TIME_VECTOR_EVENTS.csv.gz"
RESULTS_PATH = HERE / "Q50_SAME_LINEAGE_EXTERNAL_FLIP_RESULTS.json"
LINEAGES_PATH = HERE / "Q50_SAME_LINEAGE_EXTERNAL_FLIP_LINEAGES.csv.gz"
BINS_PATH = HERE / "Q50_SAME_LINEAGE_EXTERNAL_FLIP_BINS.csv"
FIGURE_PATH = HERE / "Q50_SAME_LINEAGE_EXTERNAL_FLIP.png"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
LEFT = 1.0 / math.e
RIGHT = PHI - 1.0
WIDTH = RIGHT - LEFT
DECLARED_CENTRE = (LEFT + WIDTH / 2.0) % 1.0
AXIS = np.asarray(
    [math.cos(2.0 * math.pi * DECLARED_CENTRE), math.sin(2.0 * math.pi * DECLARED_CENTRE)],
    dtype=np.float64,
)
PERP = np.asarray([-AXIS[1], AXIS[0]], dtype=np.float64)
ESTIMATORS = ("circle", "centroid", "extrema")
TIME_EDGES = np.arange(0, 501, 25, dtype=np.int16)
BOOTSTRAP_DRAWS = 5_000
BOOTSTRAP_SEED = 500030
SHUFFLE_DRAWS = 5_000
SHUFFLE_SEED = 500031
EPS = 1e-15


def read_rows() -> list[dict[str, str]]:
    with gzip.open(EVENTS_PATH, "rt", newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def vector(row: dict[str, str], estimator: str) -> np.ndarray:
    raw = np.asarray(
        [float(row[f"{estimator}_du"]), float(row[f"{estimator}_dv"])],
        dtype=np.float64,
    )
    return raw / float(row["radius_mean"])


def aggregate_coordinate(
    rows: list[dict[str, str]], estimator: str
) -> dict[str, float | int]:
    if not rows:
        return {
            "events": 0,
            "movement": 0.0,
            "axial": math.nan,
            "perpendicular": math.nan,
            "balance": math.nan,
            "x": math.nan,
            "heading": math.nan,
        }
    vectors = np.asarray([vector(row, estimator) for row in rows], dtype=np.float64)
    norms = np.linalg.norm(vectors, axis=1)
    movement = float(np.sum(norms))
    summed = np.sum(vectors, axis=0)
    axial = float(np.dot(summed, AXIS))
    perpendicular = float(np.dot(summed, PERP))
    if movement <= EPS:
        balance = x = heading = math.nan
    else:
        balance = float(np.clip(axial / movement, -1.0, 1.0))
        x = 1.0 - balance
        heading = float(
            (math.atan2(float(summed[1]), float(summed[0])) / (2.0 * math.pi)) % 1.0
        )
    return {
        "events": len(rows),
        "movement": movement,
        "axial": axial,
        "perpendicular": perpendicular,
        "balance": balance,
        "x": x,
        "heading": heading,
    }


def circular_distance(a: float, b: float) -> float:
    delta = abs(a - b)
    return min(delta, 1.0 - delta)


def group_lineages(
    rows: list[dict[str, str]],
) -> dict[tuple[int, int], list[dict[str, str]]]:
    grouped: dict[tuple[int, int], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["seed"]), int(row["pair_index"]))].append(row)
    for values in grouped.values():
        values.sort(key=lambda row: int(row["current_start"]))
    return grouped


def fixed_lineages(
    grouped: dict[tuple[int, int], list[dict[str, str]]],
) -> set[tuple[int, int]]:
    selected: set[tuple[int, int]] = set()
    for key, rows in grouped.items():
        dev = sum(int(row["current_end"]) < 250 for row in rows)
        evaluation = sum(int(row["current_start"]) >= 250 for row in rows)
        if dev >= 3 and evaluation >= 3:
            selected.add(key)
    return selected


def stratum_rows(
    rows: list[dict[str, str]], stratum: str
) -> list[dict[str, str]]:
    if stratum == "development":
        return [row for row in rows if int(row["current_end"]) < 250]
    if stratum == "evaluation":
        return [row for row in rows if int(row["current_start"]) >= 250]
    raise ValueError(stratum)


def paired_lineage_summary(
    grouped: dict[tuple[int, int], list[dict[str, str]]],
    fixed: set[tuple[int, int]],
    estimator: str,
) -> tuple[list[dict[str, float | int]], dict[str, object]]:
    output: list[dict[str, float | int]] = []
    for key in sorted(fixed):
        dev = aggregate_coordinate(stratum_rows(grouped[key], "development"), estimator)
        evaluation = aggregate_coordinate(
            stratum_rows(grouped[key], "evaluation"), estimator
        )
        if not (math.isfinite(float(dev["x"])) and math.isfinite(float(evaluation["x"]))):
            continue
        output.append(
            {
                "seed": key[0],
                "pair_index": key[1],
                "dev_events": int(dev["events"]),
                "eval_events": int(evaluation["events"]),
                "dev_movement": float(dev["movement"]),
                "eval_movement": float(evaluation["movement"]),
                "dev_x": float(dev["x"]),
                "eval_x": float(evaluation["x"]),
                "delta_x": float(evaluation["x"]) - float(dev["x"]),
                "dev_heading": float(dev["heading"]),
                "eval_heading": float(evaluation["heading"]),
                "heading_separation": circular_distance(
                    float(dev["heading"]), float(evaluation["heading"])
                ),
            }
        )
    if not output:
        return output, {}
    deltas = np.asarray([row["delta_x"] for row in output], dtype=np.float64)
    declared_to_opposite = sum(
        row["dev_x"] < 1.0 and row["eval_x"] > 1.0 for row in output
    )
    opposite_to_declared = sum(
        row["dev_x"] > 1.0 and row["eval_x"] < 1.0 for row in output
    )
    return output, {
        "lineages": len(output),
        "seeds": len({int(row["seed"]) for row in output}),
        "declared_to_opposite": int(declared_to_opposite),
        "declared_to_opposite_fraction": declared_to_opposite / len(output),
        "opposite_to_declared": int(opposite_to_declared),
        "opposite_to_declared_fraction": opposite_to_declared / len(output),
        "median_delta_x": float(np.median(deltas)),
        "mean_delta_x": float(np.mean(deltas)),
        "median_heading_separation_turns": float(
            np.median([row["heading_separation"] for row in output])
        ),
    }


def seed_cluster_bootstrap(
    lineage_rows: list[dict[str, float | int]],
) -> dict[str, object]:
    by_seed: dict[int, list[float]] = defaultdict(list)
    for row in lineage_rows:
        by_seed[int(row["seed"])].append(float(row["delta_x"]))
    seeds = np.asarray(sorted(by_seed), dtype=np.int16)
    seed_means = np.asarray(
        [np.mean(by_seed[int(seed)]) for seed in seeds], dtype=np.float64
    )
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    for draw in range(BOOTSTRAP_DRAWS):
        chosen = rng.integers(0, len(seeds), size=len(seeds))
        draws[draw] = float(np.mean(seed_means[chosen]))
    return {
        "draws": BOOTSTRAP_DRAWS,
        "seed": BOOTSTRAP_SEED,
        "cluster_seeds": int(len(seeds)),
        "mean_seed_delta_x": float(np.mean(seed_means)),
        "probability_positive": float(np.mean(draws > 0.0)),
        "ci95": [float(value) for value in np.quantile(draws, [0.025, 0.975])],
    }


def bin_rows(
    grouped: dict[tuple[int, int], list[dict[str, str]]],
    fixed: set[tuple[int, int]] | None,
    estimator: str,
) -> list[dict[str, float | int | str]]:
    selected = [
        row
        for key, values in grouped.items()
        if fixed is None or key in fixed
        for row in values
    ]
    output: list[dict[str, float | int | str]] = []
    for left, right in zip(TIME_EDGES[:-1], TIME_EDGES[1:]):
        rows = [
            row
            for row in selected
            if left <= int(row["current_start"]) < right
        ]
        summary = aggregate_coordinate(rows, estimator)
        norms = np.asarray(
            [np.linalg.norm(vector(row, estimator)) for row in rows], dtype=np.float64
        )
        output.append(
            {
                "population": "fixed" if fixed is not None else "unrestricted",
                "estimator": estimator,
                "left": int(left),
                "right": int(right),
                "mid": float((left + right) / 2.0),
                **summary,
                "mean_relative_movement": float(np.mean(norms)) if norms.size else math.nan,
            }
        )
    return output


def seed_bin_bootstrap(
    grouped: dict[tuple[int, int], list[dict[str, str]]],
    fixed: set[tuple[int, int]],
    estimator: str,
) -> list[dict[str, float | int]]:
    seeds = np.asarray(sorted({key[0] for key in fixed}), dtype=np.int16)
    rng = np.random.default_rng(BOOTSTRAP_SEED + ESTIMATORS.index(estimator) + 1)
    output: list[dict[str, float | int]] = []
    for left, right in zip(TIME_EDGES[:-1], TIME_EDGES[1:]):
        by_seed: dict[int, list[dict[str, str]]] = defaultdict(list)
        for key in fixed:
            for row in grouped[key]:
                if left <= int(row["current_start"]) < right:
                    by_seed[key[0]].append(row)
        usable = np.asarray(sorted(by_seed), dtype=np.int16)
        draws = np.asarray([], dtype=np.float64)
        if usable.size:
            axial = np.empty(usable.size, dtype=np.float64)
            movement = np.empty(usable.size, dtype=np.float64)
            for index, seed in enumerate(usable):
                summary = aggregate_coordinate(by_seed[int(seed)], estimator)
                axial[index] = float(summary["axial"])
                movement[index] = float(summary["movement"])
            chosen = rng.integers(
                0, usable.size, size=(BOOTSTRAP_DRAWS, usable.size)
            )
            draw_axial = np.sum(axial[chosen], axis=1)
            draw_movement = np.sum(movement[chosen], axis=1)
            finite = draw_movement > EPS
            draws = 1.0 - draw_axial[finite] / draw_movement[finite]
        if draws.size:
            lo, hi = np.quantile(draws, [0.025, 0.975])
        else:
            lo = hi = math.nan
        output.append(
            {
                "left": int(left),
                "right": int(right),
                "seeds": int(usable.size),
                "lo95": float(lo),
                "hi95": float(hi),
            }
        )
    return output


def ordered_classification(bins: list[dict[str, float | int | str]]) -> dict[str, object]:
    values = np.asarray([float(row["x"]) for row in bins], dtype=np.float64)
    valid = np.isfinite(values)
    crossings: list[dict[str, float | int | str]] = []
    for index in range(1, len(values)):
        if not (valid[index - 1] and valid[index]):
            continue
        if values[index - 1] < 1.0 <= values[index]:
            crossings.append(
                {
                    "direction": "0_to_2",
                    "between_bins": [index - 1, index],
                    "between_slices": [
                        int(bins[index - 1]["left"]),
                        int(bins[index]["right"]),
                    ],
                }
            )
        elif values[index - 1] > 1.0 >= values[index]:
            crossings.append(
                {
                    "direction": "2_to_0",
                    "between_bins": [index - 1, index],
                    "between_slices": [
                        int(bins[index - 1]["left"]),
                        int(bins[index]["right"]),
                    ],
                }
            )
    low_indices = np.flatnonzero(values <= 0.5)
    high_indices = np.flatnonzero(values >= 1.5)
    complete = False
    witness: list[int] | None = None
    for first in low_indices:
        later_high = high_indices[high_indices > first]
        if not later_high.size:
            continue
        high = int(later_high[0])
        later_low = low_indices[low_indices > high]
        if later_low.size:
            complete = True
            witness = [int(first), high, int(later_low[0])]
            break
    passage = any(bool(np.any(high_indices > first)) for first in low_indices)
    return {
        "crossings": crossings,
        "starts_near_0_then_reaches_near_2": bool(passage),
        "complete_0_to_2_to_0": complete,
        "witness_bin_indices": witness,
        "minimum_x": float(np.nanmin(values)),
        "maximum_x": float(np.nanmax(values)),
    }


def pinch_diagnostic(
    bins: list[dict[str, float | int | str]],
    ordered: dict[str, object],
) -> dict[str, object]:
    crossing = next(
        (
            item
            for item in ordered["crossings"]
            if item["direction"] == "0_to_2"
        ),
        None,
    )
    if crossing is None:
        return {"available": False}
    index = int(crossing["between_bins"][1])
    movement = np.asarray(
        [float(row["mean_relative_movement"]) for row in bins], dtype=np.float64
    )
    pre_indices = [
        value
        for value in (index - 2, index - 1)
        if 0 <= value < len(movement) and np.isfinite(movement[value])
    ]
    post_indices = [
        value
        for value in (index + 1, index + 2)
        if 0 <= value < len(movement) and np.isfinite(movement[value])
    ]
    flank_indices = pre_indices + post_indices
    pre = float(np.mean(movement[pre_indices])) if pre_indices else math.nan
    post = float(np.mean(movement[post_indices])) if post_indices else math.nan
    flank = float(np.mean(movement[flank_indices])) if flank_indices else math.nan
    at = float(movement[index])
    strict_local_minimum = bool(at < pre and at < post)
    return {
        "available": True,
        "crossing_bin_index": index,
        "crossing_slices": [int(bins[index]["left"]), int(bins[index]["right"])],
        "crossing_mean_relative_movement": at,
        "preceding_two_bin_mean_relative_movement": pre,
        "following_two_bin_mean_relative_movement": post,
        "four_flank_mean_relative_movement": flank,
        "crossing_to_flank_ratio": at / flank if flank > EPS else math.nan,
        "below_four_flank_average": bool(at < flank),
        "strict_local_minimum_with_post_crossing_rebound": strict_local_minimum,
        "pinch_supported": strict_local_minimum,
    }


def shuffled_early_late_null(
    grouped: dict[tuple[int, int], list[dict[str, str]]],
    fixed: set[tuple[int, int]],
    estimator: str,
    observed_change: float,
) -> dict[str, object]:
    records: dict[tuple[int, int], list[tuple[np.ndarray, np.ndarray]]] = defaultdict(list)
    for key in sorted(fixed):
        rows = [
            row
            for row in grouped[key]
            if int(row["current_end"]) < 250
            or int(row["current_start"]) >= 250
        ]
        vectors = np.asarray([vector(row, estimator) for row in rows], dtype=np.float64)
        n_dev = sum(int(row["current_end"]) < 250 for row in rows)
        n_eval = sum(int(row["current_start"]) >= 250 for row in rows)
        if n_dev >= 3 and n_eval >= 3:
            axial = vectors @ AXIS
            movement = np.linalg.norm(vectors, axis=1)
            records[(len(rows), n_dev)].append((axial, movement))
    rng = np.random.default_rng(SHUFFLE_SEED + ESTIMATORS.index(estimator))
    changes = np.empty(SHUFFLE_DRAWS, dtype=np.float64)
    chunk_size = 100
    groups = {
        key: (
            np.stack([item[0] for item in values]),
            np.stack([item[1] for item in values]),
        )
        for key, values in records.items()
    }
    for start in range(0, SHUFFLE_DRAWS, chunk_size):
        count = min(chunk_size, SHUFFLE_DRAWS - start)
        dev_axial = np.zeros(count, dtype=np.float64)
        dev_movement = np.zeros(count, dtype=np.float64)
        total_axial = 0.0
        total_movement = 0.0
        for (length, n_dev), (axial, movement) in groups.items():
            scores = rng.random((count, axial.shape[0], length))
            indices = np.argpartition(scores, n_dev - 1, axis=2)[:, :, :n_dev]
            dev_axial += np.take_along_axis(
                axial[None, :, :], indices, axis=2
            ).sum(axis=(1, 2))
            dev_movement += np.take_along_axis(
                movement[None, :, :], indices, axis=2
            ).sum(axis=(1, 2))
            total_axial += float(np.sum(axial))
            total_movement += float(np.sum(movement))
        eval_axial = total_axial - dev_axial
        eval_movement = total_movement - dev_movement
        x_dev = 1.0 - dev_axial / dev_movement
        x_eval = 1.0 - eval_axial / eval_movement
        changes[start : start + count] = x_eval - x_dev
    return {
        "draws": SHUFFLE_DRAWS,
        "seed": SHUFFLE_SEED + ESTIMATORS.index(estimator),
        "mean": float(np.mean(changes)),
        "p95": float(np.quantile(changes, 0.95)),
        "p99": float(np.quantile(changes, 0.99)),
        "observed_pooled_change": observed_change,
        "one_sided_p": float((1 + np.sum(changes >= observed_change)) / (SHUFFLE_DRAWS + 1)),
    }


def write_csv_gz(path: pathlib.Path, rows: list[dict[str, object]]) -> None:
    with gzip.open(path, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_csv(path: pathlib.Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_figure(
    primary_lineages: list[dict[str, float | int]],
    bins_by_estimator: dict[str, list[dict[str, float | int | str]]],
    bootstrap_bins: list[dict[str, float | int]],
    unrestricted: list[dict[str, float | int | str]],
    results: dict[str, object],
) -> None:
    if plt is None:
        return
    plt.style.use("seaborn-v0_8-whitegrid")
    figure, axes = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)

    ax = axes[0, 0]
    dev = np.asarray([row["dev_x"] for row in primary_lineages], dtype=np.float64)
    evaluation = np.asarray([row["eval_x"] for row in primary_lineages], dtype=np.float64)
    ax.scatter(dev, evaluation, s=22, alpha=0.55, color="#4C78A8")
    ax.axvline(1.0, color="#333333", lw=1)
    ax.axhline(1.0, color="#333333", lw=1)
    ax.plot([0, 2], [0, 2], color="#999999", ls="--", lw=1)
    ax.set(xlim=(0, 2), ylim=(0, 2), xlabel="development external ARA x",
           ylabel="evaluation external ARA x",
           title="Same lineages: early versus late orientation")
    ax.text(0.05, 1.9, "declared → opposite", color="#B34D3E", va="top")

    ax = axes[0, 1]
    colours = {"circle": "#4C78A8", "centroid": "#F58518", "extrema": "#54A24B"}
    for estimator, bins in bins_by_estimator.items():
        ax.plot(
            [row["mid"] for row in bins],
            [row["x"] for row in bins],
            marker="o",
            ms=4,
            lw=1.8,
            color=colours[estimator],
            label=estimator,
        )
    mids = np.asarray([row["mid"] for row in bins_by_estimator["circle"]])
    lo = np.asarray([row["lo95"] for row in bootstrap_bins])
    hi = np.asarray([row["hi95"] for row in bootstrap_bins])
    ax.fill_between(mids, lo, hi, color="#4C78A8", alpha=0.15, label="circle seed 95% CI")
    ax.axhline(0.0, color="#577590", ls=":", lw=1)
    ax.axhline(1.0, color="#222222", lw=1.2, label="1.0 directional ridge")
    ax.axhline(2.0, color="#B56576", ls=":", lw=1)
    ax.set(ylim=(-0.05, 2.05), xlabel="source slice", ylabel="external directional ARA x",
           title="Fixed-lineage trajectory across the ARA diameter")
    ax.legend(fontsize=8, ncol=2)

    ax = axes[1, 0]
    fixed_bins = bins_by_estimator["circle"]
    ax.plot(
        [row["mid"] for row in fixed_bins],
        [row["x"] for row in fixed_bins],
        marker="o",
        color="#4C78A8",
        label="same lineages",
    )
    ax.plot(
        [row["mid"] for row in unrestricted],
        [row["x"] for row in unrestricted],
        marker="s",
        color="#E45756",
        alpha=0.75,
        label="changing population",
    )
    ax.axhline(1.0, color="#222222", lw=1)
    ax.set(ylim=(-0.05, 2.05), xlabel="source slice", ylabel="external directional ARA x",
           title="Composition check")
    ax.legend()

    ax = axes[1, 1]
    movement = [row["mean_relative_movement"] for row in fixed_bins]
    ax.plot([row["mid"] for row in fixed_bins], movement, marker="o", color="#7A5195")
    pinch = results["primary"]["pinch"]
    if pinch.get("available"):
        index = int(pinch["crossing_bin_index"])
        ax.scatter(
            [fixed_bins[index]["mid"]],
            [movement[index]],
            s=100,
            color="#D45087",
            zorder=4,
            label="first 0→2 ridge crossing bin",
        )
        ax.legend()
    ax.set(xlabel="source slice", ylabel="mean centre movement / radius",
           title="Does movement pinch at the directional ridge?")

    figure.suptitle(
        "Q50 — same-lineage external ARA reversal diagnostic\n"
        "Post-Q49 exploratory analysis; source already opened",
        fontsize=16,
        fontweight="bold",
    )
    figure.savefig(FIGURE_PATH, dpi=180)
    plt.close(figure)


def main() -> None:
    rows = read_rows()
    grouped = group_lineages(rows)
    fixed = fixed_lineages(grouped)
    all_lineage_rows: list[dict[str, object]] = []
    estimator_results: dict[str, object] = {}
    bins_by_estimator: dict[str, list[dict[str, float | int | str]]] = {}
    bootstrap_by_estimator: dict[str, list[dict[str, float | int]]] = {}
    unrestricted_by_estimator: dict[str, list[dict[str, float | int | str]]] = {}

    for estimator in ESTIMATORS:
        lineages, summary = paired_lineage_summary(grouped, fixed, estimator)
        for row in lineages:
            all_lineage_rows.append({"estimator": estimator, **row})
        bootstrap = seed_cluster_bootstrap(lineages)
        bins = bin_rows(grouped, fixed, estimator)
        bins_by_estimator[estimator] = bins
        bootstrap_bins = seed_bin_bootstrap(grouped, fixed, estimator)
        bootstrap_by_estimator[estimator] = bootstrap_bins
        unrestricted = bin_rows(grouped, None, estimator)
        unrestricted_by_estimator[estimator] = unrestricted
        ordered = ordered_classification(bins)
        pinch = pinch_diagnostic(bins, ordered)
        fixed_dev = aggregate_coordinate(
            [
                row
                for key in fixed
                for row in stratum_rows(grouped[key], "development")
            ],
            estimator,
        )
        fixed_eval = aggregate_coordinate(
            [
                row
                for key in fixed
                for row in stratum_rows(grouped[key], "evaluation")
            ],
            estimator,
        )
        observed_pooled_change = float(fixed_eval["x"]) - float(fixed_dev["x"])
        null = shuffled_early_late_null(
            grouped, fixed, estimator, observed_pooled_change
        )
        heading_separation = circular_distance(
            float(fixed_dev["heading"]), float(fixed_eval["heading"])
        )
        estimator_results[estimator] = {
            "paired_lineages": summary,
            "seed_cluster_bootstrap": bootstrap,
            "fixed_population_strata": {
                "development": fixed_dev,
                "evaluation": fixed_eval,
                "pooled_delta_x": observed_pooled_change,
                "aggregate_heading_separation_turns": heading_separation,
                "distance_to_exact_half_turn": abs(heading_separation - 0.5),
            },
            "ordered": ordered,
            "pinch": pinch,
            "within_lineage_time_shuffle": null,
        }

    primary_bins = bins_by_estimator["circle"]
    results: dict[str, object] = {
        "test": "Q50 same-lineage external ARA flip diagnostic",
        "status": "POST-Q49 EXPLORATORY; NOT CONFIRMATORY",
        "source": {
            "events_path": str(EVENTS_PATH),
            "events": len(rows),
            "all_lineages": len(grouped),
            "fixed_lineages": len(fixed),
            "fixed_seeds": len({key[0] for key in fixed}),
        },
        "coordinate": {
            "declared_arc_centre_turns": DECLARED_CENTRE,
            "declared_axis": AXIS.tolist(),
            "interpretation": {
                "0": "declared external orientation",
                "1": "directional ridge / axial cancellation",
                "2": "exact half-turn opposite orientation",
            },
        },
        "primary": {
            **estimator_results["circle"],
            "complete_0_to_2_to_0": estimator_results["circle"]["ordered"][
                "complete_0_to_2_to_0"
            ],
        },
        "estimator_sensitivity": estimator_results,
        "boundaries": [
            "The Q49 source was already opened; Q50 is diagnostic only.",
            "The directional ARA coordinate is a newly declared cut between a direction and its exact opposite.",
            "A same-lineage reversal is not by itself a physical quantum singularity.",
            "A complete 0→2→0 claim requires an ordered return inside the observed window.",
        ],
    }

    write_csv_gz(LINEAGES_PATH, all_lineage_rows)
    bin_output: list[dict[str, object]] = []
    for estimator in ESTIMATORS:
        for population_rows in (
            bins_by_estimator[estimator],
            unrestricted_by_estimator[estimator],
        ):
            bin_output.extend(population_rows)
    write_csv(BINS_PATH, bin_output)
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    primary_lineages = [
        row for row in all_lineage_rows if row["estimator"] == "circle"
    ]
    make_figure(
        primary_lineages,
        bins_by_estimator,
        bootstrap_by_estimator["circle"],
        unrestricted_by_estimator["circle"],
        results,
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

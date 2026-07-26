"""Q32: edge-child pole handover before revisiting the ARA 3.5 route.

This analysis is frozen in:
Q32_EDGE_CHILD_POLE_HANDOVER_PROTOCOL_v1_FROZEN.md

It reuses the already-open Q27/Q28 public simulator source.  The later time
half is an unchanged internal evaluation partition, not a fresh blind source.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import pathlib
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / ".q27_deps"
if LOCAL_DEPS.exists():
    import sys

    sys.path.insert(0, str(LOCAL_DEPS))

MPL_CONFIG = HERE / ".mplconfig"
MPL_CONFIG.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


TEST_ID = "Q32-EDGE-CHILD-POLE-HANDOVER-v1"
PROTOCOL = HERE / "Q32_EDGE_CHILD_POLE_HANDOVER_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA256 = "2c06d9f39476947a6d71d63d1237b5faf43745842121a48725ebab7556c712ef"
SOURCE_SHA256 = "0e10afb6e5c7bcc3b469a9bb18a9bcae9469bfae165d5da5add93eeeb1972eeb"
SOURCE_DIR = HERE / "public_data" / "q27_network_reconstruction"
CACHE = SOURCE_DIR / "q27_derived_cache.npz"

RESULTS = HERE / "Q32_EDGE_CHILD_POLE_HANDOVER_RESULTS.json"
LAG_CURVE = HERE / "Q32_EDGE_CHILD_POLE_HANDOVER_LAG_CURVE.csv"
TRIALS = HERE / "Q32_EDGE_CHILD_POLE_HANDOVER_TRIALS.csv"
EVENT_SAMPLE = HERE / "Q32_EDGE_CHILD_POLE_HANDOVER_EVENT_SAMPLE.csv"
GRADIENT = HERE / "Q32_EDGE_CHILD_POLE_HANDOVER_GRADIENT.csv"
FIGURE_PNG = HERE / "Q32_EDGE_CHILD_POLE_HANDOVER_GEOMETRY.png"
FIGURE_SVG = HERE / "Q32_EDGE_CHILD_POLE_HANDOVER_GEOMETRY.svg"

BRANCH_LABELS = ("c2", "c4")
PAIRS = tuple((i, j) for i in range(12) for j in range(i + 1, 12))
PAIR_TO_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
LAGS = tuple(range(1, 7))
SPLITS = {
    "development": range(0, 243),
    "evaluation": range(250, 493),
}
CONTROLS = ("topology", "seed", "time")
EPS = 1e-12
BOOTSTRAP_DRAWS = 2000
RNG_SEED = 32032


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sampled(
    branch: int,
    seed: int,
    time: int,
    pair_index: int,
    endpoint: int,
) -> bool:
    value = 97 * seed + 53 * time + 31 * pair_index + 17 * endpoint + 11 * branch
    return value % 16 == 0


def active_pair_indices(edge_row: np.ndarray) -> tuple[int, ...]:
    indices: list[int] = []
    for raw_u, raw_v in edge_row:
        pair = tuple(sorted((int(raw_u), int(raw_v))))
        indices.append(PAIR_TO_INDEX[pair])
    return tuple(indices)


def pole_nearest(
    candidates: tuple[int, ...] | list[int],
    x_row: np.ndarray,
) -> int | None:
    finite = [
        pair_index
        for pair_index in candidates
        if np.isfinite(float(x_row[pair_index]))
    ]
    if not finite:
        return None
    return min(finite, key=lambda pair_index: (float(x_row[pair_index]), pair_index))


def shifted_time(time: int, split: str, lag: int) -> int:
    start = 0 if split == "development" else 250
    support = 250 - lag
    return start + ((time - start + 137) % support)


def cumulative_movements(path: np.ndarray) -> tuple[float, float]:
    diffs = np.diff(np.asarray(path, dtype=np.float64))
    release = float(np.sum(np.maximum(0.0, -diffs)))
    accumulation = float(np.sum(np.maximum(0.0, diffs)))
    return release, accumulation


def child_metrics(
    source_path: np.ndarray,
    child_path: np.ndarray,
) -> dict[str, float]:
    source_release, _ = cumulative_movements(source_path)
    _, child_accumulation = cumulative_movements(child_path)
    gain = float(child_path[-1] - child_path[0])
    overlap = source_release * child_accumulation
    denominator = source_release + child_accumulation
    flow_x = (
        2.0 * child_accumulation / denominator
        if denominator > EPS
        else math.nan
    )
    return {
        "start_x": float(child_path[0]),
        "gain": gain,
        "source_release": source_release,
        "accumulation": child_accumulation,
        "overlap": overlap,
        "flow_x": float(flow_x),
    }


def enumerate_events(
    x_all: np.ndarray,
    edges_all: np.ndarray,
    split: str,
) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    starts = SPLITS[split]

    for branch in range(2):
        for seed in range(100):
            x = x_all[branch, seed]
            for time in starts:
                active = active_pair_indices(edges_all[branch, seed, time])
                for source_pair, endpoints in enumerate(PAIRS):
                    source_x = float(x[time, source_pair])
                    if not np.isfinite(source_x) or source_x < 1.5:
                        continue
                    one_step_release = source_x - float(x[time + 1, source_pair])
                    if not np.isfinite(one_step_release) or one_step_release <= 0:
                        continue
                    for endpoint in endpoints:
                        if not sampled(branch, seed, time, source_pair, endpoint):
                            continue

                        exact_candidates = tuple(
                            pair_index
                            for pair_index in active
                            if pair_index != source_pair
                            and endpoint in PAIRS[pair_index]
                        )
                        exact_child = pole_nearest(exact_candidates, x[time])
                        if exact_child is None:
                            continue

                        source_nodes = set(endpoints)
                        topology_candidates = tuple(
                            pair_index
                            for pair_index in active
                            if not source_nodes.intersection(PAIRS[pair_index])
                        )
                        topology_child = pole_nearest(topology_candidates, x[time])

                        shifted_seed = (seed + 37) % 100
                        seed_active = active_pair_indices(
                            edges_all[branch, shifted_seed, time]
                        )
                        seed_candidates = tuple(
                            pair_index
                            for pair_index in seed_active
                            if pair_index != source_pair
                            and endpoint in PAIRS[pair_index]
                        )
                        seed_child = pole_nearest(
                            seed_candidates,
                            x_all[branch, shifted_seed, time],
                        )

                        events.append(
                            {
                                "split": split,
                                "branch": branch,
                                "seed": seed,
                                "time": time,
                                "source_pair": source_pair,
                                "endpoint": endpoint,
                                "source_start_x": source_x,
                                "one_step_release": one_step_release,
                                "exact_child": exact_child,
                                "exact_candidates": exact_candidates,
                                "topology_child": topology_child,
                                "shifted_seed": shifted_seed,
                                "seed_child": seed_child,
                            }
                        )
    return events


def evaluate_events(
    events: list[dict[str, object]],
    x_all: np.ndarray,
    edges_all: np.ndarray,
    split: str,
    lag: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for event in events:
        branch = int(event["branch"])
        seed = int(event["seed"])
        time = int(event["time"])
        source_pair = int(event["source_pair"])
        endpoint = int(event["endpoint"])
        source_path = x_all[branch, seed, time : time + lag + 1, source_pair]
        if not np.all(np.isfinite(source_path)):
            continue

        exact_child = int(event["exact_child"])
        exact_path = x_all[branch, seed, time : time + lag + 1, exact_child]
        if not np.all(np.isfinite(exact_path)):
            continue

        row: dict[str, object] = {
            "split": split,
            "lag": lag,
            "branch": branch,
            "branch_label": BRANCH_LABELS[branch],
            "seed": seed,
            "time": time,
            "source_pair": source_pair,
            "source_pair_name": f"{PAIRS[source_pair][0]}-{PAIRS[source_pair][1]}",
            "endpoint": endpoint,
            "source_start_x": float(event["source_start_x"]),
            "one_step_release": float(event["one_step_release"]),
            "exact_child": exact_child,
            "exact_child_name": f"{PAIRS[exact_child][0]}-{PAIRS[exact_child][1]}",
        }
        for key, value in child_metrics(source_path, exact_path).items():
            row[f"exact_{key}"] = value

        topology_child = event["topology_child"]
        if topology_child is not None:
            topology_child = int(topology_child)
            path = x_all[
                branch, seed, time : time + lag + 1, topology_child
            ]
            if np.all(np.isfinite(path)):
                for key, value in child_metrics(source_path, path).items():
                    row[f"topology_{key}"] = value

        shifted_seed = int(event["shifted_seed"])
        seed_child = event["seed_child"]
        if seed_child is not None:
            seed_child = int(seed_child)
            path = x_all[
                branch, shifted_seed, time : time + lag + 1, seed_child
            ]
            if np.all(np.isfinite(path)):
                for key, value in child_metrics(source_path, path).items():
                    row[f"seed_{key}"] = value

        control_time = shifted_time(time, split, lag)
        time_active = active_pair_indices(edges_all[branch, seed, control_time])
        time_candidates = tuple(
            pair_index
            for pair_index in time_active
            if pair_index != source_pair and endpoint in PAIRS[pair_index]
        )
        time_child = pole_nearest(
            time_candidates,
            x_all[branch, seed, control_time],
        )
        if time_child is not None:
            path = x_all[
                branch,
                seed,
                control_time : control_time + lag + 1,
                time_child,
            ]
            if np.all(np.isfinite(path)):
                for key, value in child_metrics(source_path, path).items():
                    row[f"time_{key}"] = value
                row["time_control_time"] = control_time

        rows.append(row)
    return rows


def finite_values(rows: list[dict[str, object]], key: str) -> np.ndarray:
    values = [
        float(row[key])
        for row in rows
        if key in row and np.isfinite(float(row[key]))
    ]
    return np.asarray(values, dtype=np.float64)


def trial_means(
    rows: list[dict[str, object]],
    key: str,
    paired_key: str | None = None,
) -> dict[tuple[int, int], float]:
    grouped: dict[tuple[int, int], list[float]] = defaultdict(list)
    for row in rows:
        if key not in row:
            continue
        if paired_key is not None and paired_key not in row:
            continue
        value = float(row[key])
        if not np.isfinite(value):
            continue
        grouped[(int(row["branch"]), int(row["seed"]))].append(value)
    return {group: float(np.mean(values)) for group, values in grouped.items()}


def paired_trial_differences(
    rows: list[dict[str, object]],
    exact_key: str,
    control_key: str,
) -> np.ndarray:
    exact: dict[tuple[int, int], list[float]] = defaultdict(list)
    control: dict[tuple[int, int], list[float]] = defaultdict(list)
    for row in rows:
        if exact_key not in row or control_key not in row:
            continue
        exact_value = float(row[exact_key])
        control_value = float(row[control_key])
        if not np.isfinite(exact_value) or not np.isfinite(control_value):
            continue
        group = (int(row["branch"]), int(row["seed"]))
        exact[group].append(exact_value)
        control[group].append(control_value)
    groups = sorted(set(exact).intersection(control))
    return np.asarray(
        [
            float(np.mean(exact[group]) - np.mean(control[group]))
            for group in groups
        ],
        dtype=np.float64,
    )


def bootstrap_probability(
    differences: np.ndarray,
    rng: np.random.Generator,
) -> float:
    if differences.size == 0:
        return math.nan
    draws = rng.choice(
        differences,
        size=(BOOTSTRAP_DRAWS, differences.size),
        replace=True,
    )
    return float(np.mean(np.mean(draws, axis=1) > 0.0))


def summarize_lag(
    rows: list[dict[str, object]],
    rng: np.random.Generator | None = None,
) -> dict[str, object]:
    exact_start = finite_values(rows, "exact_start_x")
    summary: dict[str, object] = {
        "events": len(rows),
        "trial_strata": len(
            {(int(row["branch"]), int(row["seed"])) for row in rows}
        ),
        "exact_start_x_mean": float(np.mean(exact_start)),
        "exact_start_x_median": float(np.median(exact_start)),
        "exact_start_le_025_fraction": float(np.mean(exact_start <= 0.25)),
        "exact_start_le_05_fraction": float(np.mean(exact_start <= 0.5)),
    }

    for route in ("exact", *CONTROLS):
        for metric in ("start_x", "gain", "accumulation", "overlap", "flow_x"):
            values = finite_values(rows, f"{route}_{metric}")
            summary[f"{route}_{metric}_n"] = int(values.size)
            summary[f"{route}_{metric}_mean"] = (
                float(np.mean(values)) if values.size else None
            )
            summary[f"{route}_{metric}_median"] = (
                float(np.median(values)) if values.size else None
            )
        gains = finite_values(rows, f"{route}_gain")
        summary[f"{route}_positive_gain_fraction"] = (
            float(np.mean(gains > 0)) if gains.size else None
        )

    for control in CONTROLS:
        gain_diff = paired_trial_differences(
            rows,
            "exact_gain",
            f"{control}_gain",
        )
        overlap_diff = paired_trial_differences(
            rows,
            "exact_overlap",
            f"{control}_overlap",
        )
        start_diff = paired_trial_differences(
            rows,
            f"{control}_start_x",
            "exact_start_x",
        )
        summary[f"exact_minus_{control}_gain"] = (
            float(np.mean(gain_diff)) if gain_diff.size else None
        )
        summary[f"exact_minus_{control}_overlap"] = (
            float(np.mean(overlap_diff)) if overlap_diff.size else None
        )
        summary[f"{control}_minus_exact_start_x"] = (
            float(np.mean(start_diff)) if start_diff.size else None
        )
        summary[f"paired_{control}_trial_strata"] = int(gain_diff.size)

        if rng is not None:
            summary[f"bootstrap_exact_gain_gt_{control}"] = (
                bootstrap_probability(gain_diff, rng)
            )
            summary[f"bootstrap_exact_overlap_gt_{control}"] = (
                bootstrap_probability(overlap_diff, rng)
            )
            summary[f"bootstrap_exact_start_lower_{control}"] = (
                bootstrap_probability(start_diff, rng)
            )

    differences = [
        summary[f"exact_minus_{control}_gain"]
        for control in CONTROLS
        if summary[f"exact_minus_{control}_gain"] is not None
    ]
    summary["lag_selection_score"] = (
        float(np.mean(differences)) if differences else None
    )
    return summary


def gradient_rows(
    events: list[dict[str, object]],
    x_all: np.ndarray,
    lag: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for event in events:
        branch = int(event["branch"])
        seed = int(event["seed"])
        time = int(event["time"])
        for pair_index in event["exact_candidates"]:
            path = x_all[branch, seed, time : time + lag + 1, pair_index]
            if not np.all(np.isfinite(path)):
                continue
            start_x = float(path[0])
            _, accumulation = cumulative_movements(path)
            if start_x <= 0.5:
                bin_name = "pole_x_le_0.5"
            elif start_x < 1.0:
                bin_name = "lower_0.5_to_1"
            elif start_x < 1.5:
                bin_name = "upper_1_to_1.5"
            else:
                bin_name = "crest_x_ge_1.5"
            rows.append(
                {
                    "branch": branch,
                    "branch_label": BRANCH_LABELS[branch],
                    "seed": seed,
                    "time": time,
                    "source_pair": int(event["source_pair"]),
                    "child_pair": int(pair_index),
                    "bin": bin_name,
                    "start_x": start_x,
                    "gain": float(path[-1] - path[0]),
                    "accumulation": accumulation,
                }
            )
    return rows


def summarize_gradient(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    order = (
        "pole_x_le_0.5",
        "lower_0.5_to_1",
        "upper_1_to_1.5",
        "crest_x_ge_1.5",
    )
    output: list[dict[str, object]] = []
    for branch in (-1, 0, 1):
        selected_branch = rows if branch == -1 else [
            row for row in rows if int(row["branch"]) == branch
        ]
        for bin_name in order:
            selected = [row for row in selected_branch if row["bin"] == bin_name]
            gains = np.asarray([float(row["gain"]) for row in selected])
            accumulations = np.asarray(
                [float(row["accumulation"]) for row in selected]
            )
            output.append(
                {
                    "stratum": "pooled" if branch == -1 else BRANCH_LABELS[branch],
                    "bin": bin_name,
                    "n": int(gains.size),
                    "gain_mean": float(np.mean(gains)) if gains.size else None,
                    "gain_median": float(np.median(gains)) if gains.size else None,
                    "accumulation_mean": (
                        float(np.mean(accumulations))
                        if accumulations.size
                        else None
                    ),
                    "positive_gain_fraction": (
                        float(np.mean(gains > 0)) if gains.size else None
                    ),
                }
            )
    return output


def branch_gain_advantages(rows: list[dict[str, object]]) -> dict[str, float]:
    output: dict[str, float] = {}
    for branch in range(2):
        selected = [row for row in rows if int(row["branch"]) == branch]
        diffs = []
        for control in CONTROLS:
            trial_diff = paired_trial_differences(
                selected,
                "exact_gain",
                f"{control}_gain",
            )
            if trial_diff.size:
                diffs.append(float(np.mean(trial_diff)))
        output[BRANCH_LABELS[branch]] = (
            float(np.mean(diffs)) if diffs else math.nan
        )
    return output


def relative_advantage(exact: float | None, control: float | None) -> float:
    if exact is None or control is None or abs(control) <= EPS:
        return math.nan
    return float((exact - control) / abs(control))


def write_csv(path: pathlib.Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def create_figure(
    lag_summaries: list[dict[str, object]],
    evaluation_rows: list[dict[str, object]],
    gradient_summary: list[dict[str, object]],
    selected_lag: int,
) -> None:
    plt.style.use("dark_background")
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
    fig.suptitle("Q32 edge-child pole handover", fontsize=16, fontweight="bold")

    lags = np.asarray([int(row["lag"]) for row in lag_summaries])
    for route, color in (
        ("exact", "#79b8ff"),
        ("topology", "#d59a47"),
        ("seed", "#9aa4b2"),
        ("time", "#d783a6"),
    ):
        axes[0, 0].plot(
            lags,
            [float(row[f"{route}_gain_mean"]) for row in lag_summaries],
            marker="o",
            label=route,
            color=color,
        )
    axes[0, 0].axhline(0, color="#65707e", linewidth=0.8)
    axes[0, 0].axvline(selected_lag, color="#f2d675", linestyle="--")
    axes[0, 0].set(
        xlabel="lag after source release",
        ylabel="mean signed child ARA gain",
        title="Incoming child movement by lag",
    )
    axes[0, 0].legend(frameon=False)

    bins = np.linspace(0, 2.5, 51)
    for route, color in (
        ("exact", "#79b8ff"),
        ("topology", "#d59a47"),
    ):
        values = finite_values(evaluation_rows, f"{route}_start_x")
        axes[0, 1].hist(
            values,
            bins=bins,
            density=True,
            histtype="step",
            linewidth=1.8,
            label=route,
            color=color,
        )
    for landmark, label in ((0, "0 pole"), (1, "ridge"), (2, "2 pole")):
        axes[0, 1].axvline(landmark, color="#65707e", linestyle=":", linewidth=0.8)
        axes[0, 1].text(landmark, axes[0, 1].get_ylim()[1] * 0.92, label, ha="center")
    axes[0, 1].set(
        xlabel="child starting ARA x",
        ylabel="density",
        title="Where selected children begin",
    )
    axes[0, 1].legend(frameon=False)

    pooled = [row for row in gradient_summary if row["stratum"] == "pooled"]
    labels = ["pole", "lower", "upper", "crest"]
    gains = [float(row["gain_mean"]) for row in pooled]
    axes[1, 0].bar(labels, gains, color=("#4c90d9", "#73a9df", "#d0a25a", "#c97972"))
    axes[1, 0].axhline(0, color="#65707e", linewidth=0.8)
    axes[1, 0].set(
        xlabel="child starting ARA region",
        ylabel="mean signed gain",
        title="Child gradient at frozen lag",
    )

    flow = finite_values(evaluation_rows, "exact_flow_x")
    axes[1, 1].hist(flow, bins=np.linspace(0, 2, 41), color="#76b982", alpha=0.8)
    axes[1, 1].axvline(1, color="#f2d675", linestyle="--", label="equal flow ridge")
    axes[1, 1].set(
        xlabel="flow ARA = 2 × child-in / (source-out + child-in)",
        ylabel="events",
        title="Observed source-out / child-in allocation",
    )
    axes[1, 1].legend(frameon=False)

    fig.savefig(FIGURE_PNG, dpi=180)
    fig.savefig(FIGURE_SVG)
    plt.close(fig)


def main() -> None:
    if sha256(PROTOCOL) != PROTOCOL_SHA256:
        raise RuntimeError("Q32 frozen protocol hash mismatch")
    if not CACHE.exists():
        raise FileNotFoundError(
            "Q27 derived cache is absent; run q27_ara9_network_reconstruction_test.py first"
        )

    data = np.load(CACHE, allow_pickle=False)
    closure = np.asarray(data["closure"], dtype=np.float64)
    edges = np.asarray(data["edges"], dtype=np.int8)
    scales = np.quantile(closure[:, :, :250, :], 0.95, axis=2)
    x_all = np.divide(
        2.0 * closure,
        scales[:, :, None, :],
        out=np.full_like(closure, np.nan),
        where=scales[:, :, None, :] >= 1e-10,
    )

    development_events = enumerate_events(x_all, edges, "development")
    evaluation_events = enumerate_events(x_all, edges, "evaluation")

    development_summaries: list[dict[str, object]] = []
    development_rows_by_lag: dict[int, list[dict[str, object]]] = {}
    for lag in LAGS:
        rows = evaluate_events(
            development_events,
            x_all,
            edges,
            "development",
            lag,
        )
        development_rows_by_lag[lag] = rows
        summary = summarize_lag(rows)
        summary["split"] = "development"
        summary["lag"] = lag
        development_summaries.append(summary)

    selected_lag = min(
        LAGS,
        key=lambda lag: (
            -float(
                next(
                    row["lag_selection_score"]
                    for row in development_summaries
                    if int(row["lag"]) == lag
                )
            ),
            lag,
        ),
    )

    evaluation_summaries: list[dict[str, object]] = []
    evaluation_rows_by_lag: dict[int, list[dict[str, object]]] = {}
    for lag in LAGS:
        rows = evaluate_events(
            evaluation_events,
            x_all,
            edges,
            "evaluation",
            lag,
        )
        evaluation_rows_by_lag[lag] = rows
        summary = summarize_lag(rows)
        summary["split"] = "evaluation"
        summary["lag"] = lag
        evaluation_summaries.append(summary)

    rng = np.random.default_rng(RNG_SEED)
    evaluation_rows = evaluation_rows_by_lag[selected_lag]
    evaluation = summarize_lag(evaluation_rows, rng)
    evaluation["split"] = "evaluation"
    evaluation["lag"] = selected_lag

    gradient_detail = gradient_rows(
        evaluation_events,
        x_all,
        selected_lag,
    )
    gradient_summary = summarize_gradient(gradient_detail)
    pooled_gradient = {
        row["bin"]: row
        for row in gradient_summary
        if row["stratum"] == "pooled"
    }

    branch_advantages = branch_gain_advantages(evaluation_rows)
    eligibility = {
        "E1_at_least_10000_events": len(evaluation_rows) >= 10_000,
        "E2_at_least_100_trial_strata": int(evaluation["trial_strata"]) >= 100,
        "E3_at_least_2000_each_control": all(
            int(evaluation[f"{control}_gain_n"]) >= 2_000
            for control in CONTROLS
        ),
    }
    pole_gates = {
        "P1_half_begin_at_or_below_0_5": (
            float(evaluation["exact_start_le_05_fraction"]) >= 0.50
        ),
        "P2_exact_at_least_0_05_below_topology": (
            float(evaluation["topology_minus_exact_start_x"]) >= 0.05
        ),
        "P3_bootstrap_95pct": (
            float(evaluation["bootstrap_exact_start_lower_topology"]) >= 0.95
        ),
    }
    incoming_gates = {
        "I1_exact_gain_positive": float(evaluation["exact_gain_mean"]) > 0,
        "I2_exact_gain_beats_all_by_0_02": all(
            float(evaluation[f"exact_minus_{control}_gain"]) >= 0.02
            for control in CONTROLS
        ),
        "I3_bootstrap_95pct_all": all(
            float(evaluation[f"bootstrap_exact_gain_gt_{control}"]) >= 0.95
            for control in CONTROLS
        ),
    }

    overlap_advantages = {
        control: relative_advantage(
            evaluation["exact_overlap_mean"],
            evaluation[f"{control}_overlap_mean"],
        )
        for control in CONTROLS
    }
    coupling_gates = {
        "C1_overlap_beats_all_by_5pct": all(
            advantage >= 0.05 for advantage in overlap_advantages.values()
        ),
        "C2_bootstrap_95pct_all": all(
            float(evaluation[f"bootstrap_exact_overlap_gt_{control}"]) >= 0.95
            for control in CONTROLS
        ),
        "C3_same_gain_direction_c2_c4": all(
            value > 0 for value in branch_advantages.values()
        ),
    }
    pole_gain = pooled_gradient["pole_x_le_0.5"]["gain_mean"]
    crest_gain = pooled_gradient["crest_x_ge_1.5"]["gain_mean"]
    gradient_gates = {
        "G1_pole_gain_at_least_crest_gain": (
            pole_gain is not None
            and crest_gain is not None
            and float(pole_gain) >= float(crest_gain)
        )
    }

    all_pole = all(pole_gates.values())
    all_incoming = all(incoming_gates.values())
    all_coupling = all(coupling_gates.values())
    all_gradient = all(gradient_gates.values())
    all_eligibility = all(eligibility.values())

    if all_eligibility and all_pole and all_incoming and all_coupling and all_gradient:
        verdict = "SUPPORTED INSIDE THIS SIMULATOR"
    elif all_eligibility and all_incoming and all_coupling and not all_pole:
        verdict = "ORDERED CHILD TRANSFER WITHOUT POLE-ORIGIN SUPPORT"
    elif all_eligibility and all_pole and not (all_incoming and all_coupling):
        verdict = "ASYMMETRIC CHILD POSITION WITHOUT TRANSFER SUPPORT"
    else:
        verdict = "NOT SUPPORTED BY THIS IMPLEMENTATION"

    lag_rows = development_summaries + evaluation_summaries
    write_csv(LAG_CURVE, lag_rows)

    trial_rows: list[dict[str, object]] = []
    for branch in range(2):
        for seed in range(100):
            selected = [
                row
                for row in evaluation_rows
                if int(row["branch"]) == branch and int(row["seed"]) == seed
            ]
            if not selected:
                continue
            trial_row: dict[str, object] = {
                "branch": BRANCH_LABELS[branch],
                "seed": seed,
                "events": len(selected),
            }
            for route in ("exact", *CONTROLS):
                for metric in ("start_x", "gain", "overlap", "flow_x"):
                    values = finite_values(selected, f"{route}_{metric}")
                    trial_row[f"{route}_{metric}_mean"] = (
                        float(np.mean(values)) if values.size else ""
                    )
            trial_rows.append(trial_row)
    write_csv(TRIALS, trial_rows)

    sample_indices = np.linspace(
        0,
        max(0, len(evaluation_rows) - 1),
        min(500, len(evaluation_rows)),
        dtype=int,
    )
    sample_keys = (
        "branch_label",
        "seed",
        "time",
        "source_pair_name",
        "endpoint",
        "source_start_x",
        "one_step_release",
        "exact_child_name",
        "exact_start_x",
        "exact_gain",
        "exact_accumulation",
        "exact_overlap",
        "exact_flow_x",
        "topology_start_x",
        "topology_gain",
        "seed_start_x",
        "seed_gain",
        "time_start_x",
        "time_gain",
    )
    sample_rows = [
        {key: evaluation_rows[index].get(key, "") for key in sample_keys}
        for index in sample_indices
    ]
    write_csv(EVENT_SAMPLE, sample_rows)
    write_csv(GRADIENT, gradient_summary)

    create_figure(
        evaluation_summaries,
        evaluation_rows,
        gradient_summary,
        selected_lag,
    )

    result = {
        "test_id": TEST_ID,
        "date": "2026-07-26",
        "ledger": "T286",
        "protocol_sha256": PROTOCOL_SHA256,
        "source_sha256": SOURCE_SHA256,
        "source_status": (
            "already-open public simulator; later half is unchanged internal "
            "evaluation, not a fresh blind source"
        ),
        "orientation": {
            "0": "low closure / pole",
            "1": "local ridge",
            "2": "exposed connection crest / opposite pole",
        },
        "old_q30_boundary": (
            "Q30 used the triangle-closing edge as 1.5. Q32 instead tests "
            "whether a baseline-selected pole child receives ordered inflow."
        ),
        "event_counts": {
            "development_base": len(development_events),
            "evaluation_base": len(evaluation_events),
            "evaluation_selected_lag": len(evaluation_rows),
        },
        "development_lag_summaries": development_summaries,
        "selected_lag": selected_lag,
        "evaluation_lag_summaries": evaluation_summaries,
        "evaluation_selected_lag_summary": evaluation,
        "overlap_relative_advantages": overlap_advantages,
        "branch_gain_advantages": branch_advantages,
        "gradient_summary": gradient_summary,
        "gates": {
            "eligibility": eligibility,
            "pole_origin": pole_gates,
            "incoming": incoming_gates,
            "coupling": coupling_gates,
            "gradient": gradient_gates,
        },
        "verdict": verdict,
        "boundary": (
            "The result concerns an ordered edge-child relation in one exactly "
            "diagonal quantum simulator. It is not a universal flip, physical "
            "energy conservation, Phase B identification, or a completed 3.5 route."
        ),
        "artifacts": {
            "lag_curve": LAG_CURVE.name,
            "trials": TRIALS.name,
            "event_sample": EVENT_SAMPLE.name,
            "gradient": GRADIENT.name,
            "figure_png": FIGURE_PNG.name,
            "figure_svg": FIGURE_SVG.name,
        },
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(
        {
            "selected_lag": selected_lag,
            "evaluation_events": len(evaluation_rows),
            "verdict": verdict,
            "gates": result["gates"],
        },
        indent=2,
    ))
    print(f"Wrote {RESULTS}")


if __name__ == "__main__":
    main()

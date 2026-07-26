"""Q33: test the ARA two-axis 3.5 parent/child projection.

Frozen protocol:
Q33_TWO_AXIS_PARENT_CHILD_35_PROTOCOL_v1_FROZEN.md

The central distinction is between:

* local ARA position, where every relation has its own 0--2 coordinate; and
* parent-facing capacity, where source and child remain in the same raw
  connected-relation energy coordinate.

This is a retrospective test on the already-open Q27/Q28 simulator lineage.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import itertools
import json
import math
import os
import pathlib
import sys
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / ".q27_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))
MPL_CONFIG = HERE / ".mplconfig"
MPL_CONFIG.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


TEST_ID = "Q33-TWO-AXIS-PARENT-CHILD-35-v1"
PROTOCOL = HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_FIDELITY_v1.md"
PROTOCOL_SHA256 = "c91afedc4a01b763b81940a0057929644ddde1806825afcdf21a7fced48f0a23"
FIDELITY_SHA256 = "b7a306b2fa02c9048d017c77768c6b6069dbd8b82e3f9db33d072bc6529ed620"

SOURCE_DIR = HERE / "public_data" / "q27_network_reconstruction"
Q27_CACHE = SOURCE_DIR / "q27_derived_cache.npz"
Q28_CACHE = SOURCE_DIR / "q28_connected_cache.npy"
Q27_SHA256 = "660a59ff416b3938755fcde6b7c361bb46a2fe24bf8c2aaca0cfa63bbb80137c"
Q28_SHA256 = "6b73ac362d50453dad6ff76ea2a9102b04b24d5e9be596c46545cf5671ad4ef9"

RESULTS = HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_RESULTS.json"
EVENTS = HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_EVENTS.csv.gz"
TRIALS = HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_TRIALS.csv"
FIGURE_PNG = HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_GEOMETRY.png"
FIGURE_SVG = HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_GEOMETRY.svg"

BRANCH_LABELS = ("c2", "c4")
PAIRS = tuple((i, j) for i in range(12) for j in range(i + 1, 12))
PAIR_TO_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
SPLITS = {
    "development": (8, 242),
    "evaluation": (258, 492),
}
CONTROLS = ("topology", "seed", "time")
BACKWARD = 8
TIME_SHIFT = 137
SEED_SHIFT = 37
BOOTSTRAP_DRAWS = 2000
BOOTSTRAP_SEED = 33035
EPS = 1e-12


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_safe(value):
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if not np.isfinite(value) else float(value)
    return value


def active_pair_indices(edge_row: np.ndarray) -> tuple[int, ...]:
    return tuple(
        PAIR_TO_INDEX[tuple(sorted((int(raw_u), int(raw_v))))]
        for raw_u, raw_v in edge_row
    )


def endpoint_children(
    active: tuple[int, ...],
    source_pair: int,
) -> tuple[int, int] | None:
    u, v = PAIRS[source_pair]
    if source_pair in active:
        return None
    child_u = [index for index in active if u in PAIRS[index]]
    child_v = [index for index in active if v in PAIRS[index]]
    if len(child_u) != 1 or len(child_v) != 1 or child_u[0] == child_v[0]:
        return None
    return child_u[0], child_v[0]


def latest_extreme(
    values: np.ndarray,
    time: int,
    mode: str,
) -> tuple[int, float]:
    start = time - BACKWARD
    segment = np.asarray(values[start : time + 1], dtype=np.float64)
    finite = np.isfinite(segment)
    if not np.any(finite):
        return time, math.nan
    target = np.nanmax(segment) if mode == "max" else np.nanmin(segment)
    locations = np.flatnonzero(np.isclose(segment, target, rtol=0.0, atol=1e-12))
    index = int(locations[-1])
    return start + index, float(segment[index])


def angle_degrees(left: np.ndarray, right: np.ndarray) -> tuple[float, float]:
    left = np.asarray(left, dtype=np.float64).ravel()
    right = np.asarray(right, dtype=np.float64).ravel()
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denominator <= EPS:
        return math.nan, math.nan
    cosine = float(np.clip(np.dot(left, right) / denominator, -1.0, 1.0))
    angle = float(np.degrees(np.arccos(cosine)))
    axial = float(min(angle, 180.0 - angle))
    return angle, axial


def shifted_time(time: int, split: str) -> int:
    start, end = SPLITS[split]
    width = end - start + 1
    return start + ((time - start + TIME_SHIFT) % width)


def sampled(branch: int, seed: int, time: int, pair_index: int) -> bool:
    return (97 * seed + 53 * time + 31 * pair_index + 11 * branch) % 16 == 0


def choose_topology_control(
    active: tuple[int, ...],
    source_pair: int,
    exact_children: tuple[int, int],
    x_row: np.ndarray,
) -> tuple[int, int] | None:
    source_nodes = set(PAIRS[source_pair])
    candidates = tuple(
        index for index in active if not source_nodes.intersection(PAIRS[index])
    )
    if len(candidates) < 2:
        return None
    exact_x = [float(x_row[index]) for index in exact_children]
    if not np.all(np.isfinite(exact_x)):
        return None
    choices: list[tuple[float, int, int]] = []
    for first, second in itertools.permutations(candidates, 2):
        candidate_x = (float(x_row[first]), float(x_row[second]))
        if not np.all(np.isfinite(candidate_x)):
            continue
        distance = abs(candidate_x[0] - exact_x[0]) + abs(
            candidate_x[1] - exact_x[1]
        )
        choices.append((float(distance), int(first), int(second)))
    if not choices:
        return None
    _, first, second = min(choices)
    return first, second


def route_measurements(
    *,
    branch: int,
    seed: int,
    time: int,
    source_energy_capacity: float,
    source_h_capacity: float,
    source_energy_loss: float,
    source_movement: np.ndarray,
    children: tuple[int, int] | None,
    x_all: np.ndarray,
    energy_all: np.ndarray,
    connected: np.ndarray,
    energy_capacity: np.ndarray,
    h_capacity: np.ndarray,
) -> dict[str, float | int | str]:
    if children is None or not np.isfinite(source_energy_capacity):
        return {}
    child_records: list[dict[str, float | int]] = []
    child_movements: list[np.ndarray] = []
    for child_index in children:
        origin_time, origin_x = latest_extreme(
            x_all[branch, seed, :, child_index], time, "min"
        )
        child_capacity = float(energy_capacity[branch, seed, child_index])
        child_h_capacity = float(h_capacity[branch, seed, child_index])
        rho = (
            child_capacity / source_energy_capacity
            if source_energy_capacity > EPS
            else math.nan
        )
        origin_energy = float(energy_all[branch, seed, origin_time, child_index])
        final_energy = float(energy_all[branch, seed, time + 1, child_index])
        gain = max(final_energy - origin_energy, 0.0)
        transfer = (
            gain / source_energy_loss if source_energy_loss > EPS else math.nan
        )
        child_movement = (
            np.asarray(connected[branch, seed, time + 1, child_index], dtype=np.float64)
            - np.asarray(
                connected[branch, seed, origin_time, child_index],
                dtype=np.float64,
            )
        )
        angle, axial = angle_degrees(source_movement, child_movement)
        child_movements.append(child_movement)
        child_records.append(
            {
                "index": int(child_index),
                "origin_time": int(origin_time),
                "origin_x": float(origin_x),
                "capacity": float(child_capacity),
                "rho": float(rho),
                "amplitude_rho": float(math.sqrt(rho)) if rho >= 0 else math.nan,
                "closure_scale_rho": float(
                    child_h_capacity / source_h_capacity
                    if source_h_capacity > EPS
                    else math.nan
                ),
                "half_distance": float(abs(rho - 0.5)),
                "vertical": float(1.0 + rho),
                "path": float(3.0 + rho),
                "gain": float(gain),
                "transfer": float(transfer),
                "angle": float(angle),
                "axial": float(axial),
            }
        )
    combined = child_movements[0] + child_movements[1]
    combined_angle, combined_axial = angle_degrees(source_movement, combined)
    prefix: dict[str, float | int | str] = {}
    for ordinal, record in enumerate(child_records, start=1):
        for key, value in record.items():
            prefix[f"child{ordinal}_{key}"] = value
        index = int(record["index"])
        prefix[f"child{ordinal}_name"] = f"{PAIRS[index][0]}-{PAIRS[index][1]}"
    for field in (
        "origin_x",
        "rho",
        "amplitude_rho",
        "closure_scale_rho",
        "half_distance",
        "vertical",
        "path",
        "gain",
        "transfer",
        "angle",
        "axial",
    ):
        values = np.asarray([record[field] for record in child_records], dtype=float)
        prefix[f"{field}_mean"] = float(np.nanmean(values))
    prefix["origin_x_max"] = float(
        max(float(record["origin_x"]) for record in child_records)
    )
    prefix["both_origin_le_05"] = int(
        all(float(record["origin_x"]) <= 0.5 for record in child_records)
    )
    prefix["gain_sum"] = float(sum(float(record["gain"]) for record in child_records))
    prefix["transfer_sum"] = float(
        prefix["gain_sum"] / source_energy_loss
        if source_energy_loss > EPS
        else math.nan
    )
    prefix["combined_angle"] = float(combined_angle)
    prefix["combined_axial"] = float(combined_axial)
    return prefix


def enumerate_split(
    split: str,
    x_all: np.ndarray,
    h_all: np.ndarray,
    energy_all: np.ndarray,
    edges_all: np.ndarray,
    connected: np.ndarray,
    energy_capacity: np.ndarray,
    h_capacity: np.ndarray,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    start, end = SPLITS[split]
    for branch in range(2):
        for seed in range(100):
            for time in range(start, end + 1):
                active = active_pair_indices(edges_all[branch, seed, time])
                for source_pair in range(len(PAIRS)):
                    if not sampled(branch, seed, time, source_pair):
                        continue
                    source_x = float(x_all[branch, seed, time, source_pair])
                    if not np.isfinite(source_x) or source_x < 1.5:
                        continue
                    if not (
                        float(h_all[branch, seed, time, source_pair])
                        > float(h_all[branch, seed, time + 1, source_pair])
                    ):
                        continue
                    exact_children = endpoint_children(active, source_pair)
                    if exact_children is None:
                        continue
                    crest_time, crest_x = latest_extreme(
                        x_all[branch, seed, :, source_pair], time, "max"
                    )
                    source_origin_energy = float(
                        energy_all[branch, seed, crest_time, source_pair]
                    )
                    source_final_energy = float(
                        energy_all[branch, seed, time + 1, source_pair]
                    )
                    source_loss = source_origin_energy - source_final_energy
                    if not np.isfinite(source_loss) or source_loss <= 0:
                        continue
                    source_capacity = float(
                        energy_capacity[branch, seed, source_pair]
                    )
                    source_h_capacity = float(
                        h_capacity[branch, seed, source_pair]
                    )
                    source_movement = (
                        np.asarray(
                            connected[branch, seed, crest_time, source_pair],
                            dtype=np.float64,
                        )
                        - np.asarray(
                            connected[branch, seed, time + 1, source_pair],
                            dtype=np.float64,
                        )
                    )

                    contexts: dict[str, tuple[int, int, tuple[int, int] | None]] = {
                        "exact": (seed, time, exact_children),
                        "topology": (
                            seed,
                            time,
                            choose_topology_control(
                                active,
                                source_pair,
                                exact_children,
                                x_all[branch, seed, time],
                            ),
                        ),
                    }
                    control_seed = (seed + SEED_SHIFT) % 100
                    seed_active = active_pair_indices(
                        edges_all[branch, control_seed, time]
                    )
                    contexts["seed"] = (
                        control_seed,
                        time,
                        endpoint_children(seed_active, source_pair),
                    )
                    control_time = shifted_time(time, split)
                    time_active = active_pair_indices(
                        edges_all[branch, seed, control_time]
                    )
                    contexts["time"] = (
                        seed,
                        control_time,
                        endpoint_children(time_active, source_pair),
                    )

                    row: dict[str, object] = {
                        "split": split,
                        "branch": branch,
                        "branch_label": BRANCH_LABELS[branch],
                        "seed": seed,
                        "time": time,
                        "source_pair": source_pair,
                        "source_pair_name": (
                            f"{PAIRS[source_pair][0]}-{PAIRS[source_pair][1]}"
                        ),
                        "source_crest_time": crest_time,
                        "source_crest_x": crest_x,
                        "source_start_x": source_x,
                        "source_capacity": source_capacity,
                        "source_h_capacity": source_h_capacity,
                        "source_energy_loss": source_loss,
                    }
                    for label, (route_seed, route_time, children) in contexts.items():
                        row[f"{label}_seed"] = route_seed
                        row[f"{label}_time"] = route_time
                        values = route_measurements(
                            branch=branch,
                            seed=route_seed,
                            time=route_time,
                            source_energy_capacity=source_capacity,
                            source_h_capacity=source_h_capacity,
                            source_energy_loss=source_loss,
                            source_movement=source_movement,
                            children=children,
                            x_all=x_all,
                            energy_all=energy_all,
                            connected=connected,
                            energy_capacity=energy_capacity,
                            h_capacity=h_capacity,
                        )
                        for key, value in values.items():
                            row[f"{label}_{key}"] = value
                    rows.append(row)
    return rows


def finite_array(rows: list[dict[str, object]], field: str) -> np.ndarray:
    values = []
    for row in rows:
        value = row.get(field, math.nan)
        try:
            value = float(value)
        except (TypeError, ValueError):
            continue
        if np.isfinite(value):
            values.append(value)
    return np.asarray(values, dtype=np.float64)


def quantiles(values: np.ndarray) -> dict[str, float | int]:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {
            "n": 0,
            "mean": math.nan,
            "median": math.nan,
            "q05": math.nan,
            "q25": math.nan,
            "q75": math.nan,
            "q95": math.nan,
        }
    return {
        "n": int(values.size),
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "q05": float(np.quantile(values, 0.05)),
        "q25": float(np.quantile(values, 0.25)),
        "q75": float(np.quantile(values, 0.75)),
        "q95": float(np.quantile(values, 0.95)),
    }


def summarize_split(rows: list[dict[str, object]]) -> dict[str, object]:
    summary: dict[str, object] = {
        "source_events": len(rows),
        "branch_seed_strata": len(
            {
                (int(row["branch"]), int(row["seed"]))
                for row in rows
            }
        ),
        "exact_child_routes": 2 * len(rows),
        "routes": {},
        "branches": {},
    }
    for label in ("exact", *CONTROLS):
        route = {
            "paired_events": int(
                finite_array(rows, f"{label}_rho_mean").size
            ),
            "event_mean_capacity_ratio": quantiles(
                finite_array(rows, f"{label}_rho_mean")
            ),
            "event_mean_amplitude_ratio": quantiles(
                finite_array(rows, f"{label}_amplitude_rho_mean")
            ),
            "event_mean_closure_scale_ratio": quantiles(
                finite_array(rows, f"{label}_closure_scale_rho_mean")
            ),
            "event_mean_half_distance": quantiles(
                finite_array(rows, f"{label}_half_distance_mean")
            ),
            "child_origin_x": quantiles(
                np.concatenate(
                    [
                        finite_array(rows, f"{label}_child1_origin_x"),
                        finite_array(rows, f"{label}_child2_origin_x"),
                    ]
                )
            ),
            "both_children_origin_le_05_fraction": float(
                np.mean(finite_array(rows, f"{label}_both_origin_le_05"))
            )
            if finite_array(rows, f"{label}_both_origin_le_05").size
            else math.nan,
            "complete_path": quantiles(finite_array(rows, f"{label}_path_mean")),
            "transfer_sum": quantiles(
                finite_array(rows, f"{label}_transfer_sum")
            ),
            "axial_angle": quantiles(
                finite_array(rows, f"{label}_combined_axial")
            ),
        }
        summary["routes"][label] = route
    for branch, branch_label in enumerate(BRANCH_LABELS):
        branch_rows = [row for row in rows if int(row["branch"]) == branch]
        summary["branches"][branch_label] = {
            "source_events": len(branch_rows),
            "exact_event_mean_capacity_ratio": quantiles(
                finite_array(branch_rows, "exact_rho_mean")
            ),
            "exact_child_origin_x": quantiles(
                np.concatenate(
                    [
                        finite_array(branch_rows, "exact_child1_origin_x"),
                        finite_array(branch_rows, "exact_child2_origin_x"),
                    ]
                )
            ),
        }
    return summary


def cluster_bootstrap(
    rows: list[dict[str, object]],
    control: str,
) -> dict[str, float | int]:
    clusters: defaultdict[tuple[int, int], list[float]] = defaultdict(list)
    paired = 0
    for row in rows:
        exact = row.get("exact_half_distance_mean", math.nan)
        baseline = row.get(f"{control}_half_distance_mean", math.nan)
        try:
            difference = float(baseline) - float(exact)
        except (TypeError, ValueError):
            continue
        if not np.isfinite(difference):
            continue
        clusters[(int(row["branch"]), int(row["seed"]))].append(difference)
        paired += 1
    means = np.asarray(
        [np.mean(values) for values in clusters.values()], dtype=np.float64
    )
    if means.size == 0:
        return {
            "paired_events": paired,
            "clusters": 0,
            "mean_control_minus_exact": math.nan,
            "probability_exact_lower": math.nan,
            "ci_low": math.nan,
            "ci_high": math.nan,
        }
    rng = np.random.default_rng(BOOTSTRAP_SEED + CONTROLS.index(control))
    draws = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    for index in range(BOOTSTRAP_DRAWS):
        sample = rng.choice(means, size=means.size, replace=True)
        draws[index] = np.mean(sample)
    return {
        "paired_events": paired,
        "clusters": int(means.size),
        "mean_control_minus_exact": float(np.mean(means)),
        "probability_exact_lower": float(np.mean(draws > 0.0)),
        "ci_low": float(np.quantile(draws, 0.025)),
        "ci_high": float(np.quantile(draws, 0.975)),
    }


def frozen_verdict(
    summary: dict[str, object],
    bootstraps: dict[str, dict[str, float | int]],
) -> dict[str, object]:
    exact = summary["routes"]["exact"]
    exact_rho = float(exact["event_mean_capacity_ratio"]["median"])
    exact_error = float(exact["event_mean_half_distance"]["median"])
    eligibility = {
        "source_events_ge_5000": int(summary["source_events"]) >= 5000,
        "strata_ge_100": int(summary["branch_seed_strata"]) >= 100,
        "exact_routes_ge_5000": int(summary["exact_child_routes"]) >= 5000,
    }
    for control in CONTROLS:
        eligibility[f"{control}_paired_events_ge_2000"] = (
            int(summary["routes"][control]["paired_events"]) >= 2000
        )

    half_gates: dict[str, bool] = {
        "pooled_median_capacity_in_040_060": 0.40 <= exact_rho <= 0.60,
    }
    for branch in BRANCH_LABELS:
        median = float(
            summary["branches"][branch][
                "exact_event_mean_capacity_ratio"
            ]["median"]
        )
        half_gates[f"{branch}_median_capacity_in_035_065"] = (
            0.35 <= median <= 0.65
        )
    for control in CONTROLS:
        control_error = float(
            summary["routes"][control]["event_mean_half_distance"]["median"]
        )
        advantage = (
            1.0 - exact_error / control_error if control_error > EPS else -math.inf
        )
        half_gates[f"exact_error_5pct_better_than_{control}"] = advantage >= 0.05
        half_gates[f"bootstrap_probability_ge_095_vs_{control}"] = (
            float(bootstraps[control]["probability_exact_lower"]) >= 0.95
        )

    pole_gates = {
        "median_child_origin_x_le_05": float(
            exact["child_origin_x"]["median"]
        )
        <= 0.5,
        "both_child_origins_le_05_fraction_ge_050": float(
            exact["both_children_origin_le_05_fraction"]
        )
        >= 0.5,
    }
    eligible = all(eligibility.values())
    half_pass = all(half_gates.values())
    pole_pass = all(pole_gates.values())
    if not eligible:
        label = "INCONCLUSIVE"
    elif half_pass and pole_pass:
        label = "SUPPORTED INSIDE THIS SIMULATOR"
    elif not half_pass and 0.80 <= exact_rho <= 1.20:
        label = (
            "ORDERED HANDOVER, BUT Q32 CHILDREN ARE SAME-RUNG "
            "IN THIS ENERGY PROJECTION"
        )
    else:
        label = "CROSS-RUNG 3.5 PROJECTION NOT SUPPORTED BY THIS IMPLEMENTATION"
    return {
        "label": label,
        "eligibility": eligibility,
        "eligibility_pass": eligible,
        "half_capacity_gates": half_gates,
        "half_capacity_pass": half_pass,
        "backward_pole_gates": pole_gates,
        "backward_pole_pass": pole_pass,
    }


def write_rows(path: pathlib.Path, rows: list[dict[str, object]]) -> None:
    fields = sorted({key for row in rows for key in row})
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def trial_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: defaultdict[tuple[int, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["branch"]), int(row["seed"]))].append(row)
    output: list[dict[str, object]] = []
    for (branch, seed), group in sorted(grouped.items()):
        row: dict[str, object] = {
            "branch": branch,
            "branch_label": BRANCH_LABELS[branch],
            "seed": seed,
            "n_events": len(group),
        }
        for label in ("exact", *CONTROLS):
            for metric in ("rho_mean", "half_distance_mean", "origin_x_mean"):
                values = finite_array(group, f"{label}_{metric}")
                row[f"{label}_{metric}"] = (
                    float(np.mean(values)) if values.size else math.nan
                )
        output.append(row)
    return output


def plot_results(rows: list[dict[str, object]], verdict: str) -> None:
    plt.style.use("dark_background")
    colors = {
        "exact": "#f5b642",
        "topology": "#5da9e9",
        "seed": "#c58bf2",
        "time": "#72d29b",
    }
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    fig.patch.set_facecolor("#0b0f14")
    for axis in axes.ravel():
        axis.set_facecolor("#101720")
        axis.grid(alpha=0.16)

    bins = np.linspace(0.0, 2.0, 81)
    for label in ("exact", *CONTROLS):
        values = finite_array(rows, f"{label}_rho_mean")
        axes[0, 0].hist(
            values,
            bins=bins,
            density=True,
            histtype="step",
            linewidth=2.0,
            color=colors[label],
            label=f"{label} (median {np.median(values):.3f})",
        )
    axes[0, 0].axvline(0.5, color="white", linestyle="--", label="cross-rung 0.5")
    axes[0, 0].axvline(1.0, color="#ff6b6b", linestyle=":", label="same-rung 1.0")
    axes[0, 0].set(
        title="Parent-facing child capacity ratio",
        xlabel=r"$\rho=E_{\max,child}/E_{\max,source}$",
        ylabel="density",
        xlim=(0, 2),
    )
    axes[0, 0].legend(fontsize=8)

    exact_path = finite_array(rows, "exact_path_mean")
    axes[0, 1].hist(exact_path, bins=70, color=colors["exact"], alpha=0.85)
    axes[0, 1].axvline(3.5, color="white", linestyle="--", label="ARA target 3.5")
    axes[0, 1].axvline(4.0, color="#ff6b6b", linestyle=":", label="same-rung path 4.0")
    axes[0, 1].set(
        title="Complete two-axis path",
        xlabel=r"$L=3+\rho$",
        ylabel="source events",
    )
    axes[0, 1].legend(fontsize=9)

    origin_bins = np.linspace(0, 2.5, 80)
    for label in ("exact", *CONTROLS):
        values = np.concatenate(
            [
                finite_array(rows, f"{label}_child1_origin_x"),
                finite_array(rows, f"{label}_child2_origin_x"),
            ]
        )
        axes[1, 0].hist(
            values,
            bins=origin_bins,
            density=True,
            histtype="step",
            linewidth=2.0,
            color=colors[label],
            label=f"{label} (median {np.median(values):.3f})",
        )
    axes[1, 0].axvline(0.5, color="white", linestyle="--", label="frozen pole gate")
    axes[1, 0].axvline(1.0, color="#7fd3ff", linestyle=":", label="ridge")
    axes[1, 0].set(
        title="Backward-traced child origins on local ARA",
        xlabel="local child ARA coordinate",
        ylabel="density",
        xlim=(0, 2.5),
    )
    axes[1, 0].legend(fontsize=8)

    angle = finite_array(rows, "exact_combined_axial")
    transfer = finite_array(rows, "exact_transfer_sum")
    axes[1, 1].hist(
        angle,
        bins=np.linspace(0, 90, 46),
        color="#5da9e9",
        alpha=0.8,
        label=f"axial angle (median {np.median(angle):.1f}°)",
    )
    twin = axes[1, 1].twinx()
    twin.hist(
        np.clip(transfer, 0, 4),
        bins=np.linspace(0, 4, 45),
        histtype="step",
        linewidth=2,
        color="#72d29b",
        label=f"transfer ratio clipped (median {np.median(transfer):.3f})",
    )
    axes[1, 1].set(
        title="Non-verdict diagnostics",
        xlabel="axial movement angle (degrees); transfer uses right axis",
        ylabel="angle events",
        xlim=(0, 90),
    )
    twin.set_ylabel("transfer events")
    lines1, labels1 = axes[1, 1].get_legend_handles_labels()
    lines2, labels2 = twin.get_legend_handles_labels()
    axes[1, 1].legend(lines1 + lines2, labels1 + labels2, fontsize=8)

    fig.suptitle(
        "Q33 — raw endpoint/source capacity diagnostic\n"
        "Reproducible calculation · post-audit: not an ARA rung test",
        fontsize=15,
        fontweight="bold",
    )
    fig.savefig(FIGURE_PNG, dpi=180, facecolor=fig.get_facecolor())
    fig.savefig(FIGURE_SVG, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    hashes = {
        "protocol_sha256": sha256(PROTOCOL),
        "fidelity_sha256": sha256(FIDELITY),
        "q27_cache_sha256": sha256(Q27_CACHE),
        "q28_cache_sha256": sha256(Q28_CACHE),
    }
    expected = {
        "protocol_sha256": PROTOCOL_SHA256,
        "fidelity_sha256": FIDELITY_SHA256,
        "q27_cache_sha256": Q27_SHA256,
        "q28_cache_sha256": Q28_SHA256,
    }
    if hashes != expected:
        raise RuntimeError(f"Hash mismatch: observed={hashes}, expected={expected}")

    q27 = np.load(Q27_CACHE)
    h_all = np.asarray(q27["closure"], dtype=np.float32)
    edges_all = np.asarray(q27["edges"], dtype=np.int8)
    connected = np.load(Q28_CACHE, mmap_mode="r")
    if connected.shape != (2, 100, 500, 66, 3, 3):
        raise RuntimeError(f"Unexpected connected-cache shape: {connected.shape}")

    local_capacity = np.quantile(
        np.asarray(h_all[:, :, :250, :], dtype=np.float64),
        0.95,
        axis=2,
    )
    x_all = np.divide(
        2.0 * h_all,
        local_capacity[:, :, None, :],
        out=np.full(h_all.shape, np.nan, dtype=np.float32),
        where=local_capacity[:, :, None, :] > EPS,
    )
    energy_all = np.sum(
        np.asarray(connected, dtype=np.float32) ** 2,
        axis=(-2, -1),
        dtype=np.float32,
    )
    energy_capacity = np.quantile(
        np.asarray(energy_all[:, :, :250, :], dtype=np.float64),
        0.95,
        axis=2,
    )

    all_rows: list[dict[str, object]] = []
    summaries: dict[str, object] = {}
    for split in SPLITS:
        rows = enumerate_split(
            split,
            x_all,
            h_all,
            energy_all,
            edges_all,
            connected,
            energy_capacity,
            local_capacity,
        )
        all_rows.extend(rows)
        summaries[split] = summarize_split(rows)

    evaluation_rows = [
        row for row in all_rows if str(row["split"]) == "evaluation"
    ]
    bootstraps = {
        control: cluster_bootstrap(evaluation_rows, control)
        for control in CONTROLS
    }
    verdict = frozen_verdict(summaries["evaluation"], bootstraps)

    control_advantages = {}
    exact_error = float(
        summaries["evaluation"]["routes"]["exact"][
            "event_mean_half_distance"
        ]["median"]
    )
    for control in CONTROLS:
        control_error = float(
            summaries["evaluation"]["routes"][control][
                "event_mean_half_distance"
            ]["median"]
        )
        control_advantages[control] = (
            float(1.0 - exact_error / control_error)
            if control_error > EPS
            else math.nan
        )

    output = {
        "test_id": TEST_ID,
        "date": "2026-07-26",
        "status": "complete",
        "source_status": (
            "retrospective analysis of already-open public simulator lineage"
        ),
        "hashes": hashes,
        "arrays": {
            "h_shape": list(h_all.shape),
            "connected_shape": list(connected.shape),
            "energy_definition": "Frobenius norm squared of 3x3 connected matrix",
            "local_scale": "development t=0..249 Q95 of determinant closure",
            "capacity_scale": "development t=0..249 Q95 of connected energy",
        },
        "splits": summaries,
        "evaluation_bootstrap": bootstraps,
        "evaluation_control_half_distance_advantage": control_advantages,
        "frozen_verdict": verdict,
        "diagnostic_warning": (
            "Transfer ratios and angles are diagnostics only and cannot promote "
            "the frozen verdict."
        ),
        "evidence_fence": (
            "The evaluation partition is unchanged but has been used in Q27-Q32. "
            "This is not fresh blind replication or hardware quantum data."
        ),
    }
    RESULTS.write_text(
        json.dumps(json_safe(output), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_rows(EVENTS, all_rows)
    write_rows(TRIALS, trial_rows(evaluation_rows))
    plot_results(evaluation_rows, str(verdict["label"]))

    print(json.dumps(json_safe({
        "verdict": verdict["label"],
        "evaluation_source_events": summaries["evaluation"]["source_events"],
        "evaluation_strata": summaries["evaluation"]["branch_seed_strata"],
        "exact_capacity_ratio": summaries["evaluation"]["routes"]["exact"][
            "event_mean_capacity_ratio"
        ],
        "exact_origin_x": summaries["evaluation"]["routes"]["exact"][
            "child_origin_x"
        ],
        "both_origin_le_05": summaries["evaluation"]["routes"]["exact"][
            "both_children_origin_le_05_fraction"
        ],
        "bootstraps": bootstraps,
    }), indent=2))


if __name__ == "__main__":
    main()

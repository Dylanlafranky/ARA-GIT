"""Q33B: ARA-first fixed-rung boundary-child flow test.

The structural 3.5 coordinate is declared by ARA.  This script scores only its
directed flow consequence: the single endpoint child nearest the low boundary
should accumulate after its high-side source releases.
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


TEST_ID = "Q33B-ARA-FIRST-BOUNDARY-CHILD-v1"
PROTOCOL = HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_FIDELITY_v1.md"
PROTOCOL_SHA256 = "780364be62feb97afe336b9cbf16511b832a998e07581e1877fa9a17f6f21a70"
FIDELITY_SHA256 = "43a6a2090669588632f76988c1fc18394c8c2950e856ea622116775c05ebd7a3"

SOURCE_DIR = HERE / "public_data" / "q27_network_reconstruction"
Q27_CACHE = SOURCE_DIR / "q27_derived_cache.npz"
Q28_CACHE = SOURCE_DIR / "q28_connected_cache.npy"
Q27_SHA256 = "660a59ff416b3938755fcde6b7c361bb46a2fe24bf8c2aaca0cfa63bbb80137c"
Q28_SHA256 = "6b73ac362d50453dad6ff76ea2a9102b04b24d5e9be596c46545cf5671ad4ef9"

RESULTS = HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_RESULTS.json"
EVENTS = HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_EVENTS.csv.gz"
TRIALS = HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_TRIALS.csv"
FIGURE_PNG = HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_GEOMETRY.png"
FIGURE_SVG = HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_GEOMETRY.svg"
FIGURE_TITLE = "Q33B — ARA-first fixed 3.5 boundary-child route"

BRANCH_LABELS = ("c2", "c4")
PAIRS = tuple((i, j) for i in range(12) for j in range(i + 1, 12))
PAIR_TO_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
SPLITS = {
    "development": (8, 242),
    "evaluation": (258, 492),
}
COMPARATORS = ("sibling", "topology", "seed", "time")
SEED_SHIFT = 37
TIME_SHIFT = 137
BACKWARD = 8
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
        PAIR_TO_INDEX[tuple(sorted((int(u), int(v))))] for u, v in edge_row
    )


def endpoint_children(
    active: tuple[int, ...], source_pair: int
) -> tuple[int, int] | None:
    u, v = PAIRS[source_pair]
    if source_pair in active:
        return None
    child_u = [index for index in active if u in PAIRS[index]]
    child_v = [index for index in active if v in PAIRS[index]]
    if len(child_u) != 1 or len(child_v) != 1 or child_u[0] == child_v[0]:
        return None
    return child_u[0], child_v[0]


def boundary_order(
    candidates: tuple[int, int] | None,
    z_row: np.ndarray,
) -> tuple[int, int] | None:
    if candidates is None:
        return None
    first, second = candidates
    values = (
        (float(z_row[first]), int(first)),
        (float(z_row[second]), int(second)),
    )
    if not np.all(np.isfinite([values[0][0], values[1][0]])):
        return None
    ordered = sorted(values)
    return ordered[0][1], ordered[1][1]


def matched_topology_pair(
    active: tuple[int, ...],
    source_pair: int,
    exact_children: tuple[int, int],
    z_row: np.ndarray,
) -> tuple[int, int] | None:
    source_nodes = set(PAIRS[source_pair])
    candidates = tuple(
        index for index in active if not source_nodes.intersection(PAIRS[index])
    )
    if len(candidates) < 2:
        return None
    exact_z = [float(z_row[index]) for index in exact_children]
    if not np.all(np.isfinite(exact_z)):
        return None
    assignments: list[tuple[float, int, int]] = []
    for first, second in itertools.permutations(candidates, 2):
        candidate_z = (float(z_row[first]), float(z_row[second]))
        if not np.all(np.isfinite(candidate_z)):
            continue
        distance = abs(candidate_z[0] - exact_z[0]) + abs(
            candidate_z[1] - exact_z[1]
        )
        assignments.append((float(distance), int(first), int(second)))
    if not assignments:
        return None
    _, first, second = min(assignments)
    return first, second


def latest_max(values: np.ndarray, time: int) -> int:
    start = time - BACKWARD
    segment = np.asarray(values[start : time + 1], dtype=np.float64)
    maximum = np.nanmax(segment)
    positions = np.flatnonzero(np.isclose(segment, maximum, rtol=0, atol=1e-12))
    return start + int(positions[-1])


def shifted_time(time: int, split: str) -> int:
    start, end = SPLITS[split]
    width = end - start + 1
    return start + ((time - start + TIME_SHIFT) % width)


def sampled(branch: int, seed: int, time: int, source_pair: int) -> bool:
    return (97 * seed + 53 * time + 31 * source_pair + 11 * branch) % 16 == 0


def route_metrics(
    *,
    branch: int,
    seed: int,
    time: int,
    child: int | None,
    source_release: float,
    h_all: np.ndarray,
    z_all: np.ndarray,
    h_scale: np.ndarray,
    energy_all: np.ndarray,
    energy_scale: np.ndarray,
) -> dict[str, float | int | str]:
    if child is None:
        return {}
    start_h = float(h_all[branch, seed, time, child])
    next_h = float(h_all[branch, seed, time + 1, child])
    scale_h = float(h_scale[branch, seed, child])
    start_z = float(z_all[branch, seed, time, child])
    flow = (next_h - start_h) / scale_h if scale_h > EPS else math.nan
    start_energy = float(energy_all[branch, seed, time, child])
    next_energy = float(energy_all[branch, seed, time + 1, child])
    scale_energy = float(energy_scale[branch, seed, child])
    energy_flow = (
        (next_energy - start_energy) / scale_energy
        if scale_energy > EPS
        else math.nan
    )
    return {
        "child": int(child),
        "child_name": f"{PAIRS[child][0]}-{PAIRS[child][1]}",
        "start_z": start_z,
        "flow": float(flow),
        "positive": int(flow > 0),
        "overlap": float(source_release * max(flow, 0.0)),
        "energy_flow": float(energy_flow),
        "structural_child_parent_weight": 0.5,
        "structural_path": 3.5,
    }


def enumerate_split(
    split: str,
    h_all: np.ndarray,
    z_all: np.ndarray,
    h_scale: np.ndarray,
    edges_all: np.ndarray,
    energy_all: np.ndarray,
    energy_scale: np.ndarray,
) -> list[dict[str, object]]:
    start, end = SPLITS[split]
    rows: list[dict[str, object]] = []
    for branch in range(2):
        for seed in range(100):
            for time in range(start, end + 1):
                active = active_pair_indices(edges_all[branch, seed, time])
                for source_pair in range(len(PAIRS)):
                    if not sampled(branch, seed, time, source_pair):
                        continue
                    source_z = float(z_all[branch, seed, time, source_pair])
                    if not np.isfinite(source_z) or 2.0 * source_z < 1.5:
                        continue
                    source_h = float(h_all[branch, seed, time, source_pair])
                    source_next_h = float(
                        h_all[branch, seed, time + 1, source_pair]
                    )
                    if not source_h > source_next_h:
                        continue
                    exact_children = endpoint_children(active, source_pair)
                    if exact_children is None:
                        continue
                    crest_time = latest_max(
                        energy_all[branch, seed, :, source_pair], time
                    )
                    source_energy_loss = float(
                        energy_all[branch, seed, crest_time, source_pair]
                        - energy_all[branch, seed, time + 1, source_pair]
                    )
                    if not np.isfinite(source_energy_loss) or source_energy_loss <= 0:
                        continue
                    source_release = (
                        source_h - source_next_h
                    ) / float(h_scale[branch, seed, source_pair])

                    exact_order = boundary_order(
                        exact_children, z_all[branch, seed, time]
                    )
                    if exact_order is None:
                        continue
                    boundary_child, sibling_child = exact_order

                    topology_pair = matched_topology_pair(
                        active,
                        source_pair,
                        exact_children,
                        z_all[branch, seed, time],
                    )
                    topology_order = boundary_order(
                        topology_pair, z_all[branch, seed, time]
                    )

                    control_seed = (seed + SEED_SHIFT) % 100
                    seed_active = active_pair_indices(
                        edges_all[branch, control_seed, time]
                    )
                    seed_order = boundary_order(
                        endpoint_children(seed_active, source_pair),
                        z_all[branch, control_seed, time],
                    )

                    control_time = shifted_time(time, split)
                    time_active = active_pair_indices(
                        edges_all[branch, seed, control_time]
                    )
                    time_order = boundary_order(
                        endpoint_children(time_active, source_pair),
                        z_all[branch, seed, control_time],
                    )

                    contexts = {
                        "exact": (seed, time, boundary_child),
                        "sibling": (seed, time, sibling_child),
                        "topology": (
                            seed,
                            time,
                            topology_order[0] if topology_order else None,
                        ),
                        "seed": (
                            control_seed,
                            time,
                            seed_order[0] if seed_order else None,
                        ),
                        "time": (
                            seed,
                            control_time,
                            time_order[0] if time_order else None,
                        ),
                    }
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
                        "source_start_z": source_z,
                        "source_release": source_release,
                        "source_energy_loss": source_energy_loss,
                        "structural_current_rung": 1.0,
                        "structural_child_parent_weight": 0.5,
                        "structural_vertical_leg": 1.5,
                        "structural_same_rung_span": 2.0,
                        "structural_path": 3.5,
                    }
                    for label, (route_seed, route_time, child) in contexts.items():
                        row[f"{label}_seed"] = route_seed
                        row[f"{label}_time"] = route_time
                        values = route_metrics(
                            branch=branch,
                            seed=route_seed,
                            time=route_time,
                            child=child,
                            source_release=source_release,
                            h_all=h_all,
                            z_all=z_all,
                            h_scale=h_scale,
                            energy_all=energy_all,
                            energy_scale=energy_scale,
                        )
                        for key, value in values.items():
                            row[f"{label}_{key}"] = value
                    for comparator in COMPARATORS:
                        exact_flow = row.get("exact_flow", math.nan)
                        comparator_flow = row.get(
                            f"{comparator}_flow", math.nan
                        )
                        try:
                            difference = float(exact_flow) - float(comparator_flow)
                        except (TypeError, ValueError):
                            difference = math.nan
                        row[f"exact_minus_{comparator}_flow"] = difference
                    rows.append(row)
    return rows


def finite(rows: list[dict[str, object]], field: str) -> np.ndarray:
    values: list[float] = []
    for row in rows:
        try:
            value = float(row.get(field, math.nan))
        except (TypeError, ValueError):
            continue
        if np.isfinite(value):
            values.append(value)
    return np.asarray(values, dtype=np.float64)


def quantiles(values: np.ndarray) -> dict[str, float | int]:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if not values.size:
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


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    summary: dict[str, object] = {
        "source_events": len(rows),
        "branch_seed_strata": len(
            {(int(row["branch"]), int(row["seed"])) for row in rows}
        ),
        "structural_coordinate": {
            "child_parent_weight": 0.5,
            "vertical_leg": 1.5,
            "complete_path": 3.5,
            "status": "declared geometry; not an estimated outcome",
        },
        "routes": {},
        "paired_differences": {},
        "branches": {},
    }
    for route in ("exact", *COMPARATORS):
        flow = finite(rows, f"{route}_flow")
        summary["routes"][route] = {
            "paired_events": int(flow.size),
            "flow": quantiles(flow),
            "positive_fraction": float(np.mean(flow > 0))
            if flow.size
            else math.nan,
            "start_z": quantiles(finite(rows, f"{route}_start_z")),
            "overlap": quantiles(finite(rows, f"{route}_overlap")),
            "energy_flow": quantiles(finite(rows, f"{route}_energy_flow")),
        }
    for comparator in COMPARATORS:
        summary["paired_differences"][comparator] = quantiles(
            finite(rows, f"exact_minus_{comparator}_flow")
        )
    for branch, label in enumerate(BRANCH_LABELS):
        branch_rows = [row for row in rows if int(row["branch"]) == branch]
        flow = finite(branch_rows, "exact_flow")
        summary["branches"][label] = {
            "source_events": len(branch_rows),
            "exact_flow": quantiles(flow),
            "exact_positive_fraction": float(np.mean(flow > 0))
            if flow.size
            else math.nan,
        }
    return summary


def cluster_bootstrap(
    rows: list[dict[str, object]], comparator: str
) -> dict[str, float | int]:
    clusters: defaultdict[tuple[int, int], list[float]] = defaultdict(list)
    paired = 0
    field = f"exact_minus_{comparator}_flow"
    for row in rows:
        try:
            difference = float(row.get(field, math.nan))
        except (TypeError, ValueError):
            continue
        if not np.isfinite(difference):
            continue
        clusters[(int(row["branch"]), int(row["seed"]))].append(difference)
        paired += 1
    means = np.asarray(
        [np.mean(values) for values in clusters.values()], dtype=np.float64
    )
    if not means.size:
        return {
            "paired_events": paired,
            "clusters": 0,
            "mean_exact_minus_comparator": math.nan,
            "probability_exact_greater": math.nan,
            "ci_low": math.nan,
            "ci_high": math.nan,
        }
    rng = np.random.default_rng(BOOTSTRAP_SEED + COMPARATORS.index(comparator))
    draws = np.empty(BOOTSTRAP_DRAWS)
    for index in range(BOOTSTRAP_DRAWS):
        draws[index] = np.mean(rng.choice(means, size=means.size, replace=True))
    return {
        "paired_events": paired,
        "clusters": int(means.size),
        "mean_exact_minus_comparator": float(np.mean(means)),
        "probability_exact_greater": float(np.mean(draws > 0)),
        "ci_low": float(np.quantile(draws, 0.025)),
        "ci_high": float(np.quantile(draws, 0.975)),
    }


def frozen_verdict(
    summary: dict[str, object],
    bootstraps: dict[str, dict[str, float | int]],
) -> dict[str, object]:
    eligibility = {
        "source_events_ge_5000": int(summary["source_events"]) >= 5000,
        "strata_ge_100": int(summary["branch_seed_strata"]) >= 100,
    }
    for comparator in COMPARATORS:
        eligibility[f"{comparator}_paired_ge_2000"] = (
            int(summary["routes"][comparator]["paired_events"]) >= 2000
        )
    exact = summary["routes"]["exact"]
    exact_positive = float(exact["positive_fraction"])
    gates: dict[str, bool] = {
        "pooled_exact_median_flow_positive": float(
            exact["flow"]["median"]
        )
        > 0,
        "exact_positive_fraction_ge_055": exact_positive >= 0.55,
    }
    for branch in BRANCH_LABELS:
        gates[f"{branch}_median_exact_flow_positive"] = float(
            summary["branches"][branch]["exact_flow"]["median"]
        ) > 0
    for comparator in COMPARATORS:
        comparator_positive = float(
            summary["routes"][comparator]["positive_fraction"]
        )
        gates[f"positive_fraction_advantage_ge_002_vs_{comparator}"] = (
            exact_positive - comparator_positive >= 0.02
        )
        gates[f"median_paired_flow_advantage_positive_vs_{comparator}"] = (
            float(summary["paired_differences"][comparator]["median"]) > 0
        )
        gates[f"bootstrap_probability_ge_095_vs_{comparator}"] = (
            float(bootstraps[comparator]["probability_exact_greater"]) >= 0.95
        )
    eligible = all(eligibility.values())
    routing_pass = all(gates.values())
    if not eligible:
        label = "INCONCLUSIVE"
    elif routing_pass:
        label = "BOUNDARY-CHILD FLOW ROUTE SUPPORTED INSIDE THIS SIMULATOR"
    else:
        label = "BOUNDARY-CHILD FLOW ROUTE NOT SUPPORTED BY THIS IMPLEMENTATION"
    return {
        "label": label,
        "eligibility": eligibility,
        "eligibility_pass": eligible,
        "routing_gates": gates,
        "routing_pass": routing_pass,
        "interpretation": (
            "The 3.5 coordinate is declared geometry. This verdict scores only "
            "the direction of flow generated by that route."
        ),
    }


def write_rows(path: pathlib.Path, rows: list[dict[str, object]]) -> None:
    fields = sorted({field for row in rows for field in row})
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
        for route in ("exact", *COMPARATORS):
            flow = finite(group, f"{route}_flow")
            row[f"{route}_flow_mean"] = (
                float(np.mean(flow)) if flow.size else math.nan
            )
            row[f"{route}_positive_fraction"] = (
                float(np.mean(flow > 0)) if flow.size else math.nan
            )
        output.append(row)
    return output


def plot_results(
    rows: list[dict[str, object]],
    summary: dict[str, object],
    verdict: str,
) -> None:
    plt.style.use("dark_background")
    colors = {
        "exact": "#f5b642",
        "sibling": "#ff6b6b",
        "topology": "#5da9e9",
        "seed": "#c58bf2",
        "time": "#72d29b",
    }
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    fig.patch.set_facecolor("#0b0f14")
    for axis in axes.ravel():
        axis.set_facecolor("#101720")
        axis.grid(alpha=0.16)

    bins = np.linspace(-0.8, 0.8, 100)
    for route in ("exact", *COMPARATORS):
        values = finite(rows, f"{route}_flow")
        axes[0, 0].hist(
            np.clip(values, bins[0], bins[-1]),
            bins=bins,
            density=True,
            histtype="step",
            linewidth=2,
            color=colors[route],
            label=f"{route} (median {np.median(values):+.4f})",
        )
    axes[0, 0].axvline(0, color="white", linestyle="--")
    axes[0, 0].set(
        title="Flow after source release",
        xlabel=r"$g=[h(t+1)-h(t)]/Q_{.95}^{dev}(h)$",
        ylabel="density",
    )
    axes[0, 0].legend(fontsize=8)

    routes = ("exact", *COMPARATORS)
    fractions = [
        float(summary["routes"][route]["positive_fraction"]) for route in routes
    ]
    axes[0, 1].bar(
        routes,
        fractions,
        color=[colors[route] for route in routes],
    )
    axes[0, 1].axhline(0.5, color="white", linestyle="--", label="equal signs")
    axes[0, 1].set(
        title="Fraction of routes with positive next flow",
        ylabel="positive-flow fraction",
        ylim=(0, 1),
    )
    axes[0, 1].legend(fontsize=9)

    paired_bins = np.linspace(-0.5, 0.5, 90)
    for comparator in COMPARATORS:
        values = finite(rows, f"exact_minus_{comparator}_flow")
        axes[1, 0].hist(
            np.clip(values, paired_bins[0], paired_bins[-1]),
            bins=paired_bins,
            density=True,
            histtype="step",
            linewidth=2,
            color=colors[comparator],
            label=f"exact − {comparator} (median {np.median(values):+.4f})",
        )
    axes[1, 0].axvline(0, color="white", linestyle="--")
    axes[1, 0].set(
        title="Paired boundary-route advantage",
        xlabel="exact flow minus comparator flow",
        ylabel="density",
    )
    axes[1, 0].legend(fontsize=8)

    start_z = finite(rows, "exact_start_z")
    flow = finite(rows, "exact_flow")
    axes[1, 1].hexbin(
        np.clip(start_z, 0, 2),
        np.clip(flow, -0.5, 0.5),
        gridsize=45,
        mincnt=1,
        cmap="viridis",
    )
    axes[1, 1].axhline(0, color="white", linestyle="--")
    axes[1, 1].set(
        title="Boundary-nearest child: starting location and next flow",
        xlabel="development-normalized starting closure z",
        ylabel="next normalized closure flow",
        xlim=(0, 2),
        ylim=(-0.5, 0.5),
    )

    fig.suptitle(
        FIGURE_TITLE + "\n" + verdict,
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
    h_scale = np.quantile(
        np.asarray(h_all[:, :, :250, :], dtype=np.float64), 0.95, axis=2
    )
    z_all = np.divide(
        h_all,
        h_scale[:, :, None, :],
        out=np.full(h_all.shape, np.nan, dtype=np.float32),
        where=h_scale[:, :, None, :] > EPS,
    )
    energy_all = np.sum(
        np.asarray(connected, dtype=np.float32) ** 2,
        axis=(-2, -1),
        dtype=np.float32,
    )
    energy_scale = np.quantile(
        np.asarray(energy_all[:, :, :250, :], dtype=np.float64),
        0.95,
        axis=2,
    )

    all_rows: list[dict[str, object]] = []
    summaries: dict[str, object] = {}
    for split in SPLITS:
        rows = enumerate_split(
            split,
            h_all,
            z_all,
            h_scale,
            edges_all,
            energy_all,
            energy_scale,
        )
        all_rows.extend(rows)
        summaries[split] = summarize(rows)
    evaluation_rows = [
        row for row in all_rows if str(row["split"]) == "evaluation"
    ]
    bootstraps = {
        comparator: cluster_bootstrap(evaluation_rows, comparator)
        for comparator in COMPARATORS
    }
    verdict = frozen_verdict(summaries["evaluation"], bootstraps)
    output = {
        "test_id": TEST_ID,
        "date": "2026-07-26",
        "status": "complete",
        "source_status": "retrospective already-open simulator",
        "hashes": hashes,
        "geometry": {
            "generator": "ARA fixed structural route",
            "child_local_identity": 1.0,
            "octave_projection": 0.5,
            "vertical_leg": 1.5,
            "complete_path": 3.5,
            "scored_as_outcome": False,
        },
        "splits": summaries,
        "evaluation_bootstrap": bootstraps,
        "frozen_verdict": verdict,
        "evidence_fence": (
            "The structural 3.5 coordinate generates the directional test. "
            "Only subsequent flow is empirically scored. Source is already open."
        ),
    }
    RESULTS.write_text(
        json.dumps(json_safe(output), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_rows(EVENTS, all_rows)
    write_rows(TRIALS, trial_rows(evaluation_rows))
    plot_results(evaluation_rows, summaries["evaluation"], verdict["label"])
    print(
        json.dumps(
            json_safe(
                {
                    "verdict": verdict["label"],
                    "events": summaries["evaluation"]["source_events"],
                    "strata": summaries["evaluation"]["branch_seed_strata"],
                    "routes": summaries["evaluation"]["routes"],
                    "paired_differences": summaries["evaluation"][
                        "paired_differences"
                    ],
                    "bootstraps": bootstraps,
                    "gates": verdict,
                }
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

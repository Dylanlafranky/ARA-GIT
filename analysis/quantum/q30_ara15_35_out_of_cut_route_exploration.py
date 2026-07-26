"""Q30: fixed ARA 1.5 / 3.5 out-of-cut route exploration.

The already-open Q29 event population is reconstructed without changing its
samplers.  For a source edge (u,e) and its positively accumulating child
(e,v), Q30 measures the uniquely implied triangle-closing edge (u,v).

ARA route language:
  * 1.5: the perpendicular closing leg (u,v);
  * 3.5: the complete 2 + 1.5 source-to-child-to-closing route.

The numeric labels name a route through the ARA hierarchy.  They are not
fitted coefficients and are not folded modulo two.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import pathlib
import subprocess
import sys
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / ".q27_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))
MPL_CONFIG = HERE / ".mplconfig"
MPL_CONFIG.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG))
os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np

import q29_ara9_unclassified_component_surfer_exploration as q29


SOURCE_DIR = HERE / "public_data" / "q27_network_reconstruction"
Q27_CACHE = SOURCE_DIR / "q27_derived_cache.npz"
CONNECTED_CACHE = SOURCE_DIR / "q28_connected_cache.npy"
PROTOCOL = HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_PROTOCOL_v1_FROZEN.md"
RESULTS = HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_RESULTS.json"
TRIALS = HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_TRIALS.csv"
LAG_CURVE = HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_LAG_CURVE.csv"
EVENT_SAMPLE = HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_EVENT_SAMPLE.csv"
FIGURE_PNG = HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_GEOMETRY.png"
FIGURE_SVG = HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_GEOMETRY.svg"

TEST_ID = "Q30-ARA15-35-OUT-OF-CUT-ROUTE-EXPLORATION-v1"
SOURCE_SHA256 = q29.SOURCE_SHA256
LAGS = tuple(range(0, 7))
CONTROLS = ("exact_closure", "seed", "time", "open_edge", "direct_child")
BOOTSTRAP_DRAWS = 2000
RNG_SEED = 30015
EPS = 1e-12


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: pathlib.Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def other_node(pair_index: int, shared: int) -> int:
    pair = q29.PAIRS[pair_index]
    if pair[0] == shared:
        return pair[1]
    if pair[1] == shared:
        return pair[0]
    raise ValueError(f"Node {shared} is not in pair {pair}")


def closure_pair(source_pair: int, child_pair: int, shared: int) -> int:
    u = other_node(source_pair, shared)
    v = other_node(child_pair, shared)
    return q29.PAIR_TO_INDEX[tuple(sorted((u, v)))]


def open_edge_pair(
    source_pair: int,
    child_pair: int,
    shared: int,
    branch: int,
    seed: int,
    origin_time: int,
) -> int:
    """Deterministic non-closing edge with no outcome-based selection."""
    u = other_node(source_pair, shared)
    v = other_node(child_pair, shared)
    candidates = [node for node in range(12) if node not in (u, shared, v)]
    position = (
        43 * branch
        + 31 * seed
        + 17 * origin_time
        + 11 * source_pair
        + 7 * child_pair
        + 5 * shared
    ) % len(candidates)
    return q29.PAIR_TO_INDEX[tuple(sorted((u, candidates[position])))]


def fit_sources_to_target(
    sources: np.ndarray,
    target: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fit target ~= beta * proper_flip(source), beta >= 0."""
    sources = np.asarray(sources, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    target_norm_sq = float(np.dot(target, target))
    if target_norm_sq <= EPS:
        count = len(sources)
        return (
            np.ones(count, dtype=np.float64),
            np.zeros(count, dtype=np.float64),
            np.full(count, -1, dtype=np.int8),
        )
    source_norm_sq = np.einsum("ij,ij->i", sources, sources)
    transformed = sources[:, None, :] * q29.FLIP_MASKS[None, :, :]
    dots = np.einsum("mfi,i->mf", transformed, target)
    betas = np.maximum(
        0.0,
        dots / np.maximum(source_norm_sq[:, None], EPS),
    )
    errors_sq = (
        target_norm_sq
        - 2.0 * betas * dots
        + betas * betas * source_norm_sq[:, None]
    )
    errors = np.sqrt(np.maximum(0.0, errors_sq) / target_norm_sq)
    errors[source_norm_sq <= EPS, :] = 1.0
    betas[source_norm_sq <= EPS, :] = 0.0
    flips = np.argmin(errors, axis=1)
    row = np.arange(len(sources))
    return (
        errors[row, flips],
        betas[row, flips],
        flips.astype(np.int8),
    )


def shifted_origin(origin_time: int, split: str) -> int:
    return q29.state_shift(origin_time, split)


def add_aggregate(
    aggregates: dict[tuple[object, ...], np.ndarray],
    key: tuple[object, ...],
    weight: float,
    error: float,
    residual_fraction: float,
) -> None:
    # weight, weighted error, weighted recovery, weighted composite error,
    # weighted baseline Q28 residual, event count
    item = aggregates[key]
    item[0] += weight
    item[1] += weight * error
    item[2] += weight * (1.0 - error)
    item[3] += weight * error * residual_fraction
    item[4] += weight * residual_fraction
    item[5] += 1.0


def summarize_item(item: np.ndarray) -> dict[str, float | int]:
    weight = float(item[0])
    if weight <= 0:
        return {
            "events": int(item[5]),
            "weight": weight,
            "residual_error": math.nan,
            "residual_recovery": math.nan,
            "composite_error": math.nan,
            "q28_baseline_error": math.nan,
        }
    return {
        "events": int(item[5]),
        "weight": weight,
        "residual_error": float(item[1] / weight),
        "residual_recovery": float(item[2] / weight),
        "composite_error": float(item[3] / weight),
        "q28_baseline_error": float(item[4] / weight),
    }


def combine_items(items: list[np.ndarray]) -> np.ndarray:
    if not items:
        return np.zeros(6, dtype=np.float64)
    return np.sum(np.stack(items), axis=0)


def relative_advantage(exact: float, control: float) -> float:
    if not np.isfinite(control) or control <= 0:
        return math.nan
    return float((control - exact) / control)


def bootstrap_probabilities(
    trial_arrays: dict[tuple[str, int, int, str], np.ndarray],
) -> dict[str, float | int]:
    keys = sorted(
        {
            (branch, seed)
            for split, branch, seed, _ in trial_arrays
            if split == "opened_later_half"
        }
    )
    if not keys:
        return {"draws": 0}
    rng = np.random.default_rng(RNG_SEED)
    counts = {
        "lag0_exact_beats_seed": 0,
        "lag0_exact_beats_time": 0,
        "late_exact_beats_seed": 0,
        "late_exact_beats_time": 0,
        "lag0_exact_beats_both": 0,
        "late_exact_beats_both": 0,
    }

    def pooled_error(sample: np.ndarray, control: str, late: bool) -> float:
        items: list[np.ndarray] = []
        lags = (4, 5, 6) if late else (0,)
        for raw_index in sample:
            branch, seed = keys[int(raw_index)]
            for lag in lags:
                items.append(
                    trial_arrays[
                        ("opened_later_half", branch, seed, f"{lag}:{control}")
                    ]
                )
        summary = summarize_item(combine_items(items))
        return float(summary["residual_error"])

    for _ in range(BOOTSTRAP_DRAWS):
        sample = rng.integers(0, len(keys), size=len(keys))
        lag0_exact = pooled_error(sample, "exact_closure", False)
        lag0_seed = pooled_error(sample, "seed", False)
        lag0_time = pooled_error(sample, "time", False)
        late_exact = pooled_error(sample, "exact_closure", True)
        late_seed = pooled_error(sample, "seed", True)
        late_time = pooled_error(sample, "time", True)
        lag0_es = lag0_exact < lag0_seed
        lag0_et = lag0_exact < lag0_time
        late_es = late_exact < late_seed
        late_et = late_exact < late_time
        counts["lag0_exact_beats_seed"] += int(lag0_es)
        counts["lag0_exact_beats_time"] += int(lag0_et)
        counts["late_exact_beats_seed"] += int(late_es)
        counts["late_exact_beats_time"] += int(late_et)
        counts["lag0_exact_beats_both"] += int(lag0_es and lag0_et)
        counts["late_exact_beats_both"] += int(late_es and late_et)
    return {
        "draws": BOOTSTRAP_DRAWS,
        **{key: value / BOOTSTRAP_DRAWS for key, value in counts.items()},
    }


def make_figure(result: dict[str, object]) -> None:
    import matplotlib.pyplot as plt

    colors = {
        "exact_closure": "#7c3aed",
        "seed": "#64748b",
        "time": "#94a3b8",
        "open_edge": "#ef4444",
        "direct_child": "#d97706",
    }
    labels = {
        "exact_closure": "exact closing edge",
        "seed": "seed displaced",
        "time": "time displaced",
        "open_edge": "open-edge control",
        "direct_child": "direct child",
    }
    rows = result["lag_curve"]
    later = [row for row in rows if row["split"] == "opened_later_half"]
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)

    ax = axes[0, 0]
    points = {"u": (0.12, 0.18), "e": (0.50, 0.82), "v": (0.88, 0.18)}
    for name, (x, y) in points.items():
        ax.scatter([x], [y], s=850, color="#0f172a", zorder=3)
        ax.text(x, y, name, color="white", ha="center", va="center", fontsize=15)
    ax.plot([points["u"][0], points["e"][0]], [points["u"][1], points["e"][1]],
            color="#2563eb", linewidth=5)
    ax.plot([points["e"][0], points["v"][0]], [points["e"][1], points["v"][1]],
            color="#10b981", linewidth=5)
    ax.plot([points["u"][0], points["v"][0]], [points["u"][1], points["v"][1]],
            color="#7c3aed", linewidth=5)
    ax.text(0.25, 0.57, "source span", color="#2563eb", fontweight="bold")
    ax.text(0.67, 0.57, "child", color="#10b981", fontweight="bold")
    ax.text(0.50, 0.10, "1.5 closing leg", color="#7c3aed",
            ha="center", fontweight="bold")
    ax.text(0.50, 0.96, "complete route: 2 + 1.5 = 3.5",
            ha="center", va="top", fontsize=13, fontweight="bold")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Frozen ARA route — no outcome-selected edge")

    ax = axes[0, 1]
    for control in CONTROLS:
        selected = [row for row in later if row["control"] == control]
        ax.plot(
            [row["lag"] for row in selected],
            [row["residual_error"] for row in selected],
            marker="o",
            linewidth=2.4,
            color=colors[control],
            label=labels[control],
        )
    ax.axvspan(3.5, 6.5, color="#7c3aed", alpha=0.08, label="frozen late window")
    ax.set_xlabel("slices after Q29 residual origin")
    ax.set_ylabel("residual-normalized error (lower is better)")
    ax.set_title("Does the 1.5 closing leg carry the remainder?")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(alpha=0.25)

    ax = axes[1, 0]
    lag0 = {row["control"]: row for row in later if row["lag"] == 0}
    controls = list(CONTROLS)
    values = [lag0[control]["residual_recovery"] for control in controls]
    ax.bar(
        np.arange(len(controls)),
        values,
        color=[colors[control] for control in controls],
    )
    ax.axhline(0.10, color="#111827", linestyle="--", linewidth=1.5,
               label="frozen 10% gate")
    ax.set_xticks(np.arange(len(controls)))
    ax.set_xticklabels([labels[item] for item in controls], rotation=20, ha="right")
    ax.set_ylabel("fraction of Q29 remainder recovered")
    ax.set_title("Lag-0 perpendicular-leg recovery")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.25)

    ax = axes[1, 1]
    baseline = float(lag0["exact_closure"]["q28_baseline_error"])
    composite = [lag0[control]["composite_error"] for control in controls]
    x = np.arange(len(controls))
    ax.bar(x, composite, color=[colors[control] for control in controls])
    ax.axhline(
        baseline,
        color="#111827",
        linestyle="--",
        linewidth=2,
        label=f"Q28-only error {baseline:.3f}",
    )
    ax.set_xticks(x)
    ax.set_xticklabels([labels[item] for item in controls], rotation=20, ha="right")
    ax.set_ylabel("later-web-normalized error")
    ax.set_title("Complete 3.5 route: source span plus closing leg")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.25)

    fig.suptitle(
        "Q30 — ARA 1.5 / 3.5 out-of-cut route exploration",
        fontsize=17,
        fontweight="bold",
    )
    fig.savefig(FIGURE_PNG, dpi=180)
    fig.savefig(FIGURE_SVG)
    plt.close(fig)


def analyse(quiet: bool = False) -> None:
    if not Q27_CACHE.exists() or not CONNECTED_CACHE.exists():
        runner = HERE / "q28_ara9_interlocking_rotational_transport_test.py"
        subprocess.run(
            [sys.executable, str(runner), "extract", "--workers", "6"],
            cwd=HERE,
            check=True,
        )
    if not PROTOCOL.exists():
        raise FileNotFoundError(PROTOCOL)

    q27 = np.load(Q27_CACHE, allow_pickle=False)
    closure = np.asarray(q27["closure"], dtype=np.float32)
    edges = np.asarray(q27["edges"], dtype=np.int8)
    connected = np.load(CONNECTED_CACHE, mmap_mode="r")
    if connected.shape != (2, 100, 500, 66, 3, 3):
        raise RuntimeError(f"Unexpected connected cache shape {connected.shape}")

    aggregates: dict[tuple[object, ...], np.ndarray] = defaultdict(
        lambda: np.zeros(6, dtype=np.float64)
    )
    event_count: dict[tuple[str, int, int], int] = defaultdict(int)
    lag0_recoveries: dict[str, list[float]] = defaultdict(list)
    event_sample: list[dict[str, object]] = []
    total_events = 0
    triangle_unique: set[tuple[int, int, int]] = set()

    for split, starts in q29.SPLITS.items():
        for branch in range(2):
            for seed in range(100):
                connected_seed = connected[branch, seed]
                closure_seed = closure[branch, seed]
                edges_seed = edges[branch, seed]
                displaced_seed = (seed + 37) % 100
                connected_displaced = connected[branch, displaced_seed]

                for time in starts:
                    active = q29.active_pair_indices(edges_seed[time])
                    if not active:
                        continue
                    for source_pair, pair in enumerate(q29.PAIRS):
                        release = max(
                            0.0,
                            float(
                                closure_seed[time, source_pair]
                                - closure_seed[time + 1, source_pair]
                            ),
                        )
                        if release <= 0:
                            continue
                        for endpoint in pair:
                            if not q29.q28_sampled(
                                branch, seed, time, source_pair, endpoint
                            ):
                                continue
                            if not q29.q29_sampled(
                                branch, seed, time, source_pair, endpoint
                            ):
                                continue
                            local_targets = [
                                target
                                for target in active
                                if target != source_pair
                                and endpoint in q29.PAIRS[target]
                            ]
                            if not local_targets:
                                continue
                            accumulations = np.asarray(
                                [
                                    max(
                                        0.0,
                                        float(
                                            closure_seed[time + q29.Q28_LAG, target]
                                            - closure_seed[time, target]
                                        ),
                                    )
                                    for target in local_targets
                                ],
                                dtype=np.float64,
                            )
                            accumulation = float(np.sum(accumulations))
                            weight = release * accumulation
                            if weight <= 0:
                                continue

                            source = q29.relation_vector(
                                connected_seed[time, source_pair]
                            )
                            target_web = q29.build_web(
                                connected_seed,
                                time + q29.Q28_LAG,
                                local_targets,
                                accumulations,
                            )
                            fit_error, alpha, source_flip = q29.discrete_fit(
                                source, target_web
                            )
                            if not np.isfinite(fit_error):
                                continue
                            transported = (
                                alpha * q29.FLIP_MASKS[source_flip] * source
                            )
                            residual = target_web - transported
                            target_norm = float(np.linalg.norm(target_web))
                            residual_norm = float(np.linalg.norm(residual))
                            if target_norm <= 1e-8 or residual_norm <= 1e-10:
                                continue
                            residual_fraction = residual_norm / target_norm
                            child_pair = local_targets[int(np.argmax(accumulations))]
                            closing_pair = closure_pair(
                                source_pair, child_pair, endpoint
                            )
                            origin_time = time + q29.Q28_LAG
                            decoy_pair = open_edge_pair(
                                source_pair,
                                child_pair,
                                endpoint,
                                branch,
                                seed,
                                origin_time,
                            )
                            shifted = shifted_origin(origin_time, split)
                            triangle_unique.add(
                                tuple(sorted((source_pair, child_pair, closing_pair)))
                            )

                            candidate_vectors: list[np.ndarray] = []
                            candidate_keys: list[tuple[int, str]] = []
                            for lag in LAGS:
                                exact_time = origin_time + lag
                                shifted_time = shifted + lag
                                candidates = {
                                    "exact_closure": q29.relation_vector(
                                        connected_seed[exact_time, closing_pair]
                                    ),
                                    "seed": q29.relation_vector(
                                        connected_displaced[exact_time, closing_pair]
                                    ),
                                    "time": q29.relation_vector(
                                        connected_seed[shifted_time, closing_pair]
                                    ),
                                    "open_edge": q29.relation_vector(
                                        connected_seed[exact_time, decoy_pair]
                                    ),
                                    "direct_child": q29.relation_vector(
                                        connected_seed[exact_time, child_pair]
                                    ),
                                }
                                for control in CONTROLS:
                                    candidate_vectors.append(candidates[control])
                                    candidate_keys.append((lag, control))

                            errors, betas, flips = fit_sources_to_target(
                                np.asarray(candidate_vectors),
                                residual,
                            )
                            trial_key = (split, branch, seed)
                            event_count[trial_key] += 1
                            total_events += 1

                            for position, (lag, control) in enumerate(candidate_keys):
                                key = (
                                    split,
                                    branch,
                                    seed,
                                    lag,
                                    control,
                                )
                                add_aggregate(
                                    aggregates,
                                    key,
                                    weight,
                                    float(errors[position]),
                                    residual_fraction,
                                )
                                if lag == 0:
                                    lag0_recoveries[control].append(
                                        1.0 - float(errors[position])
                                    )

                            sample_hash = (
                                103 * branch
                                + 79 * seed
                                + 47 * time
                                + 31 * source_pair
                                + 17 * child_pair
                                + 11 * endpoint
                            )
                            if sample_hash % 257 == 0 and len(event_sample) < 1200:
                                first = {
                                    key: position
                                    for position, key in enumerate(candidate_keys)
                                    if key[0] == 0
                                }
                                u = other_node(source_pair, endpoint)
                                v = other_node(child_pair, endpoint)
                                event_sample.append(
                                    {
                                        "split": split,
                                        "branch": q29.BRANCH_LABELS[branch],
                                        "seed": seed,
                                        "source_time": time,
                                        "origin_time": origin_time,
                                        "shared_node": endpoint,
                                        "source_other_node": u,
                                        "child_other_node": v,
                                        "source_pair": f"{q29.PAIRS[source_pair][0]}-{q29.PAIRS[source_pair][1]}",
                                        "child_pair": f"{q29.PAIRS[child_pair][0]}-{q29.PAIRS[child_pair][1]}",
                                        "closing_pair_1p5": f"{q29.PAIRS[closing_pair][0]}-{q29.PAIRS[closing_pair][1]}",
                                        "open_edge_control": f"{q29.PAIRS[decoy_pair][0]}-{q29.PAIRS[decoy_pair][1]}",
                                        "weight": weight,
                                        "q28_residual_fraction": residual_fraction,
                                        "exact_1p5_error": float(
                                            errors[first[(0, "exact_closure")]]
                                        ),
                                        "exact_3p5_composite_error": float(
                                            errors[first[(0, "exact_closure")]]
                                            * residual_fraction
                                        ),
                                        "seed_error": float(
                                            errors[first[(0, "seed")]]
                                        ),
                                        "time_error": float(
                                            errors[first[(0, "time")]]
                                        ),
                                        "open_edge_error": float(
                                            errors[first[(0, "open_edge")]]
                                        ),
                                        "exact_beta": float(
                                            betas[first[(0, "exact_closure")]]
                                        ),
                                        "exact_flip": q29.FLIP_NAMES[
                                            int(flips[first[(0, "exact_closure")]])
                                        ],
                                    }
                                )

                if not quiet and seed % 25 == 24:
                    print(
                        f"Q30 {split} {q29.BRANCH_LABELS[branch]} "
                        f"seed {seed + 1}/100: {total_events} events",
                        flush=True,
                    )

    if total_events == 0:
        raise RuntimeError("No Q30 events survived")

    trial_arrays: dict[tuple[str, int, int, str], np.ndarray] = {}
    trial_rows: list[dict[str, object]] = []
    for split in q29.SPLITS:
        for branch in range(2):
            for seed in range(100):
                row: dict[str, object] = {
                    "split": split,
                    "branch": q29.BRANCH_LABELS[branch],
                    "branch_index": branch,
                    "seed": seed,
                    "events": event_count[(split, branch, seed)],
                }
                for lag in LAGS:
                    for control in CONTROLS:
                        item = aggregates[(split, branch, seed, lag, control)]
                        trial_arrays[(split, branch, seed, f"{lag}:{control}")] = item
                        summary = summarize_item(item)
                        prefix = f"l{lag}_{control}"
                        row[f"{prefix}_weight"] = summary["weight"]
                        row[f"{prefix}_error"] = summary["residual_error"]
                        row[f"{prefix}_recovery"] = summary["residual_recovery"]
                        row[f"{prefix}_composite_error"] = summary["composite_error"]
                trial_rows.append(row)

    lag_rows: list[dict[str, object]] = []
    summaries: dict[str, dict[str, object]] = {}
    for split in q29.SPLITS:
        split_summary: dict[str, object] = {}
        for lag in LAGS:
            lag_summary: dict[str, object] = {}
            for control in CONTROLS:
                items = [
                    aggregates[(split, branch, seed, lag, control)]
                    for branch in range(2)
                    for seed in range(100)
                ]
                summary = summarize_item(combine_items(items))
                lag_rows.append(
                    {
                        "split": split,
                        "lag": lag,
                        "control": control,
                        **summary,
                    }
                )
                lag_summary[control] = summary
            split_summary[f"lag_{lag}"] = lag_summary
        summaries[split] = split_summary

    def pooled_lag(split: str, lag: int, control: str) -> dict[str, float | int]:
        return summaries[split][f"lag_{lag}"][control]

    split = "opened_later_half"
    exact0 = pooled_lag(split, 0, "exact_closure")
    seed0 = pooled_lag(split, 0, "seed")
    time0 = pooled_lag(split, 0, "time")
    open0 = pooled_lag(split, 0, "open_edge")
    child0 = pooled_lag(split, 0, "direct_child")

    def late_summary(control: str) -> dict[str, float | int]:
        items = [
            aggregates[(split, branch, seed, lag, control)]
            for branch in range(2)
            for seed in range(100)
            for lag in (4, 5, 6)
        ]
        return summarize_item(combine_items(items))

    late = {control: late_summary(control) for control in CONTROLS}
    bootstrap = bootstrap_probabilities(trial_arrays)

    lag0_advantages = {
        "vs_seed": relative_advantage(
            float(exact0["residual_error"]), float(seed0["residual_error"])
        ),
        "vs_time": relative_advantage(
            float(exact0["residual_error"]), float(time0["residual_error"])
        ),
        "vs_open_edge": relative_advantage(
            float(exact0["residual_error"]), float(open0["residual_error"])
        ),
        "vs_direct_child": relative_advantage(
            float(exact0["residual_error"]), float(child0["residual_error"])
        ),
    }
    composite_advantages = {
        "vs_seed": relative_advantage(
            float(exact0["composite_error"]), float(seed0["composite_error"])
        ),
        "vs_time": relative_advantage(
            float(exact0["composite_error"]), float(time0["composite_error"])
        ),
    }
    late_advantages = {
        "vs_seed": relative_advantage(
            float(late["exact_closure"]["residual_error"]),
            float(late["seed"]["residual_error"]),
        ),
        "vs_time": relative_advantage(
            float(late["exact_closure"]["residual_error"]),
            float(late["time"]["residual_error"]),
        ),
        "vs_open_edge": relative_advantage(
            float(late["exact_closure"]["residual_error"]),
            float(late["open_edge"]["residual_error"]),
        ),
    }

    r1 = (
        lag0_advantages["vs_seed"] >= 0.05
        and lag0_advantages["vs_time"] >= 0.05
        and lag0_advantages["vs_open_edge"] >= 0.05
        and float(bootstrap["lag0_exact_beats_both"]) >= 0.95
    )
    r2 = (
        float(exact0["residual_recovery"]) >= 0.10
        and composite_advantages["vs_seed"] >= 0.05
        and composite_advantages["vs_time"] >= 0.05
    )
    r3 = (
        late_advantages["vs_seed"] >= 0.05
        and late_advantages["vs_time"] >= 0.05
        and float(bootstrap["late_exact_beats_both"]) >= 0.95
    )
    if r1 and r2 and r3:
        verdict = (
            "OUT-OF-CUT CONTINUATION ROUTE SUPPORTED INSIDE OPENED SOURCE; "
            "PHASE B NOT IDENTIFIED"
        )
    elif r1 and r2:
        verdict = (
            "LOCAL TRIANGLE-CLOSING HANDOVER SUPPORTED; "
            "NO CONTINUATION BEYOND Q29 DECAY"
        )
    else:
        verdict = (
            "FROZEN 1.5/3.5 TRIANGLE ROUTE NOT SUPPORTED ON THIS SOURCE"
        )

    result: dict[str, object] = {
        "test_id": TEST_ID,
        "date": "2026-07-26",
        "status": (
            "exploratory on completely opened source; not blind; "
            "does not identify Phase B"
        ),
        "verdict": verdict,
        "route_definition": {
            "one_point_five": (
                "unique triangle-closing relation between the nonshared "
                "source and child endpoints"
            ),
            "three_point_five": (
                "complete source span 2 plus the perpendicular closing "
                "leg 1.5; route history is retained rather than folded mod 2"
            ),
            "information_lock": "(u,e), (e,v), (u,v)",
        },
        "event_population": {
            "events": total_events,
            "unique_pair_index_triangles": len(triangle_unique),
            "trial_strata": len(
                [key for key, value in event_count.items() if value > 0]
            ),
        },
        "opened_later_half": {
            "lag0": {
                control: pooled_lag(split, 0, control)
                for control in CONTROLS
            },
            "late_lags_4_to_6": late,
            "lag0_relative_advantages": lag0_advantages,
            "composite_relative_advantages": composite_advantages,
            "late_relative_advantages": late_advantages,
            "lag0_unweighted_median_recovery": {
                control: float(np.median(lag0_recoveries[control]))
                for control in CONTROLS
            },
        },
        "bootstrap": bootstrap,
        "gates": {
            "R1_perpendicular_1p5_route": bool(r1),
            "R2_crossed_rung_3p5_composite": bool(r2),
            "R3_continuation_beyond_q29_cut": bool(r3),
            "R4_phase_b_identified": False,
        },
        "lag_curve": lag_rows,
        "split_summaries": summaries,
        "source": {
            "doi": "10.5281/zenodo.16753415",
            "hdf5_sha256": SOURCE_SHA256,
            "q27_cache_sha256": sha256(Q27_CACHE),
            "q28_connected_cache_sha256": sha256(CONNECTED_CACHE),
            "protocol_sha256": sha256(PROTOCOL),
            "connected_shape": list(connected.shape),
            "known_limit": (
                "all connected matrices are exactly diagonal in this "
                "simulator coordinate"
            ),
        },
        "controls": {
            "seed_displacement": "+37 mod 100",
            "time_displacement": "+137 inside same 250-slice half",
            "open_edge": (
                "deterministic source-other to unused-node edge; no outcome "
                "selection"
            ),
            "direct_child": "Q28 positively accumulating child relation",
            "fit_freedom": (
                "one relation, four proper diagonal flips, one nonnegative "
                "scale, no intercept"
            ),
        },
    }

    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_csv(TRIALS, trial_rows)
    write_csv(LAG_CURVE, lag_rows)
    write_csv(EVENT_SAMPLE, event_sample)
    make_figure(result)

    if not quiet:
        print(json.dumps({
            "events": total_events,
            "lag0_exact_error": exact0["residual_error"],
            "lag0_exact_recovery": exact0["residual_recovery"],
            "late_exact_error": late["exact_closure"]["residual_error"],
            "lag0_advantages": lag0_advantages,
            "late_advantages": late_advantages,
            "gates": result["gates"],
            "verdict": verdict,
        }, indent=2))


def main() -> None:
    analyse()


if __name__ == "__main__":
    main()

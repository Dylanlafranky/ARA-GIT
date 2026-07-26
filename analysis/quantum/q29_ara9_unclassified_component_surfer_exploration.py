"""Q29: exploratory ARA^9 unclassified-component surfer analysis.

This is a development analysis on the already-open Q28 source.  It does not
use a fresh hidden set and therefore cannot confirm a new physical entity.

Question
--------
After Q28's best positive-scale, discrete proper flip has transported a
source relation into its later accumulation web, what is the remaining
component?

The analysis deliberately keeps the remainder unclassified.  It tests three
descriptive possibilities:

* coherent counterpart: one stable partner and flip repeatedly carry it;
* local child mixture: it follows nearby active child relations;
* unstructured remainder: it has no route beyond best-of-many controls.

The public source contains exactly diagonal connected correlation matrices.
The only identifiable proper rotations are therefore the identity and the
three 180-degree two-axis sign flips.

Public source: Zenodo DOI 10.5281/zenodo.16753415.
Source HDF5 SHA-256:
0e10afb6e5c7bcc3b469a9bb18a9bcae9469bfae165d5da5add93eeeb1972eeb.
Source first extracted for this test lineage on 26 July 2026. If the Q27/Q28
derived caches are absent, this runner invokes Q28's public extraction path.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import pathlib
import subprocess
import sys
import traceback
from collections import Counter, defaultdict
from dataclasses import dataclass

LOCAL_DEPS = pathlib.Path(__file__).resolve().parent / ".q27_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))
MPL_CONFIG = pathlib.Path(__file__).resolve().parent / ".mplconfig"
MPL_CONFIG.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG))

import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
SOURCE_DIR = HERE / "public_data" / "q27_network_reconstruction"
Q27_CACHE = SOURCE_DIR / "q27_derived_cache.npz"
CONNECTED_CACHE = SOURCE_DIR / "q28_connected_cache.npy"

RESULTS = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_RESULTS.json"
TRIALS = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_TRIALS.csv"
LAG_CURVE = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_LAG_CURVE.csv"
EVENT_SAMPLE = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_EVENT_SAMPLE.csv"
ROUTE_SAMPLE = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_ROUTE_SAMPLE.csv"
MODES = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_MODES.csv"
AXIS_TRIALS = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_AXIS_SURFER_TRIALS.csv"
AXIS_LAG_CURVE = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_AXIS_SURFER_LAG_CURVE.csv"
AXIS_ROUTE_SAMPLE = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_AXIS_ROUTE_SAMPLE.csv"
FIGURE_PNG = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_GEOMETRY.png"
FIGURE_SVG = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_GEOMETRY.svg"
AXIS_FIGURE_PNG = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_AXIS_SURFER.png"
AXIS_FIGURE_SVG = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_AXIS_SURFER.svg"
ERROR_LOG = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_ERROR.log"

TEST_ID = "Q29-ARA9-UNCLASSIFIED-COMPONENT-SURFER-EXPLORATION-v1"
SOURCE_SHA256 = "0e10afb6e5c7bcc3b469a9bb18a9bcae9469bfae165d5da5add93eeeb1972eeb"
Q28_LAG = 2
SURF_LAGS = tuple(range(0, 7))
SPLITS = {
    "development": range(0, 242),
    "opened_later_half": range(250, 492),
}
BRANCH_LABELS = ("c2", "c4")
PAIRS = tuple((i, j) for i in range(12) for j in range(i + 1, 12))
PAIR_TO_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
FLIP_NAMES = ("I", "Fx", "Fy", "Fz")
FLIP_MASKS = np.asarray(
    (
        (1.0, 1.0, 1.0),
        (1.0, -1.0, -1.0),
        (-1.0, 1.0, -1.0),
        (-1.0, -1.0, 1.0),
    ),
    dtype=np.float64,
)
EPS = 1e-12
BOOTSTRAP_DRAWS = 2000
RNG_SEED = 29029


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def active_pair_indices(edge_row: np.ndarray) -> list[int]:
    active: list[int] = []
    for raw_u, raw_v in edge_row:
        pair = tuple(sorted((int(raw_u), int(raw_v))))
        if pair in PAIR_TO_INDEX:
            active.append(PAIR_TO_INDEX[pair])
    return active


def q28_sampled(
    branch: int,
    seed: int,
    time: int,
    pair_index: int,
    endpoint: int,
) -> bool:
    value = 97 * seed + 53 * time + 31 * pair_index + 17 * endpoint + 11 * branch
    return value % 16 == 0


def q29_sampled(
    branch: int,
    seed: int,
    time: int,
    pair_index: int,
    endpoint: int,
) -> bool:
    """A deterministic one-in-four development subsample of Q28 events."""
    value = 89 * seed + 47 * time + 23 * pair_index + 13 * endpoint + 7 * branch
    return value % 4 == 0


def state_shift(time: int, split: str) -> int:
    # Residual origins begin two slices into each half because Q28 uses lag 2.
    # Keep controls inside that same support instead of admitting the all-zero
    # simulator initial state at slice 0/250.
    start = 2 if split == "development" else 252
    valid_origins = 250 - Q28_LAG - max(SURF_LAGS)
    return start + ((time - start + 137) % valid_origins)


def residual_origin_shift(time: int, split: str) -> int:
    """Shift a Q28 residual origin within its 242-slice split support."""
    start = 2 if split == "development" else 252
    valid_origins = 250 - Q28_LAG
    return start + ((time - start + 137) % valid_origins)


def relation_vector(matrix: np.ndarray) -> np.ndarray:
    return np.diag(np.asarray(matrix, dtype=np.float64))


def discrete_fit(source: np.ndarray, target: np.ndarray) -> tuple[float, float, int]:
    """Fit target ~= alpha * F(source), alpha >= 0, over four proper flips."""
    source = np.asarray(source, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    source_norm_sq = float(np.dot(source, source))
    target_norm_sq = float(np.dot(target, target))
    if source_norm_sq <= EPS or target_norm_sq <= EPS:
        return math.nan, math.nan, -1
    transformed = FLIP_MASKS * source[None, :]
    dots = transformed @ target
    alphas = np.maximum(0.0, dots / source_norm_sq)
    errors_sq = (
        target_norm_sq
        - 2.0 * alphas * dots
        + alphas * alphas * source_norm_sq
    )
    errors = np.sqrt(np.maximum(0.0, errors_sq) / target_norm_sq)
    index = int(np.argmin(errors))
    return float(errors[index]), float(alphas[index]), index


def batch_discrete_fit(
    source: np.ndarray,
    targets: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Best target-normalized residual and flip for every candidate target."""
    source = np.asarray(source, dtype=np.float64)
    targets = np.asarray(targets, dtype=np.float64)
    source_norm_sq = float(np.dot(source, source))
    target_norm_sq = np.einsum("ij,ij->i", targets, targets)
    transformed = FLIP_MASKS * source[None, :]
    dots = targets @ transformed.T
    alphas = np.maximum(0.0, dots / max(source_norm_sq, EPS))
    errors_sq = (
        target_norm_sq[:, None]
        - 2.0 * alphas * dots
        + alphas * alphas * source_norm_sq
    )
    errors = np.sqrt(
        np.maximum(0.0, errors_sq)
        / np.maximum(target_norm_sq[:, None], EPS)
    )
    invalid = target_norm_sq <= EPS
    errors[invalid] = np.inf
    flip_indices = np.argmin(errors, axis=1)
    best_errors = errors[np.arange(len(targets)), flip_indices]
    return best_errors, flip_indices.astype(np.int8)


def normalized_entropy(weights: np.ndarray) -> float:
    weights = np.asarray(weights, dtype=np.float64)
    total = float(np.sum(weights))
    if total <= EPS:
        return math.nan
    probabilities = weights[weights > 0] / total
    if len(probabilities) <= 1:
        return 0.0
    return float(
        -np.sum(probabilities * np.log(probabilities)) / math.log(len(probabilities))
    )


def component_entropy(vector: np.ndarray) -> tuple[float, float, float]:
    powers = np.square(np.asarray(vector, dtype=np.float64))
    total = float(np.sum(powers))
    if total <= EPS:
        return math.nan, math.nan, math.nan
    shares = powers / total
    positive = shares[shares > 0]
    entropy = float(-np.sum(positive * np.log(positive)) / math.log(3.0))
    largest = float(np.max(shares))
    effective_dimension = float(1.0 / np.sum(shares * shares))
    return entropy, largest, effective_dimension


def weighted_mean(rows: list[dict[str, object]], field: str) -> float:
    values = np.asarray([float(row[field]) for row in rows], dtype=np.float64)
    weights = np.asarray([float(row["weight"]) for row in rows], dtype=np.float64)
    valid = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not np.any(valid):
        return math.nan
    return float(np.sum(values[valid] * weights[valid]) / np.sum(weights[valid]))


def write_csv(path: pathlib.Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def pair_shares_node(first: int, second: int) -> bool:
    return bool(set(PAIRS[first]) & set(PAIRS[second]))


def build_web(
    connected_seed: np.ndarray,
    target_time: int,
    target_indices: list[int],
    accumulations: np.ndarray,
) -> np.ndarray:
    total = float(np.sum(accumulations))
    if total <= EPS:
        return np.zeros(3, dtype=np.float64)
    child_vectors = np.asarray(
        [
            relation_vector(connected_seed[target_time, target])
            for target in target_indices
        ],
        dtype=np.float64,
    )
    return np.sum(accumulations[:, None] * child_vectors, axis=0) / total


@dataclass
class SurfPath:
    errors: list[float]
    pairs: list[int]
    flips: list[int]


def surf(
    component: np.ndarray,
    connected_seed: np.ndarray,
    origin_time: int,
) -> SurfPath:
    errors: list[float] = []
    pairs: list[int] = []
    flips: list[int] = []
    for lag in SURF_LAGS:
        candidates = np.diagonal(
            np.asarray(connected_seed[origin_time + lag], dtype=np.float64),
            axis1=1,
            axis2=2,
        )
        candidate_errors, candidate_flips = batch_discrete_fit(component, candidates)
        best_pair = int(np.argmin(candidate_errors))
        errors.append(float(candidate_errors[best_pair]))
        pairs.append(best_pair)
        flips.append(int(candidate_flips[best_pair]))
    return SurfPath(errors, pairs, flips)


def path_metrics(path: SurfPath, source_pair: int) -> dict[str, float]:
    pair_counts = Counter(path.pairs)
    flip_counts = Counter(path.flips)
    persistence = max(pair_counts.values()) / len(path.pairs)
    flip_persistence = max(flip_counts.values()) / len(path.flips)
    adjacency = np.mean(
        [
            pair_shares_node(first, second)
            for first, second in zip(path.pairs[:-1], path.pairs[1:])
        ]
    )
    returned = float(source_pair in path.pairs[1:])
    return {
        "path_partner_persistence": float(persistence),
        "path_flip_persistence": float(flip_persistence),
        "path_adjacency_share": float(adjacency),
        "path_self_return": returned,
    }


def describe_partner_concentration(
    rows: list[dict[str, object]],
    pair_field: str,
) -> dict[str, float]:
    grouped: dict[tuple[int, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["source_pair_index"]), int(row["endpoint"]))].append(row)
    total_group_weight = 0.0
    concentration_total = 0.0
    entropy_total = 0.0
    for group_rows in grouped.values():
        by_partner: dict[int, float] = defaultdict(float)
        for row in group_rows:
            by_partner[int(row[pair_field])] += float(row["weight"])
        group_weight = float(sum(by_partner.values()))
        if group_weight <= EPS:
            continue
        shares = np.asarray(list(by_partner.values()), dtype=np.float64) / group_weight
        concentration = float(np.max(shares))
        if len(shares) <= 1:
            entropy = 0.0
        else:
            entropy = float(-np.sum(shares * np.log(shares)) / math.log(len(shares)))
        total_group_weight += group_weight
        concentration_total += group_weight * concentration
        entropy_total += group_weight * entropy
    return {
        "modal_partner_concentration": concentration_total / total_group_weight,
        "partner_entropy": entropy_total / total_group_weight,
        "source_endpoint_groups": len(grouped),
    }


def summarize(rows: list[dict[str, object]]) -> dict[str, float | int]:
    metrics = (
        "q28_fit_error",
        "residual_fraction",
        "residual_component_entropy",
        "residual_largest_axis_share",
        "residual_effective_dimension",
        "child_weight_entropy",
        "strongest_child_weight_share",
        "positive_child_count",
        "origin_exact_error",
        "origin_seed_error",
        "origin_time_error",
        "origin_exact_is_local",
        "origin_seed_is_local",
        "origin_time_is_local",
        "origin_exact_is_strongest_child",
        "origin_seed_is_strongest_child",
        "origin_time_is_strongest_child",
        "origin_exact_shares_endpoint",
        "origin_seed_shares_endpoint",
        "origin_time_shares_endpoint",
        "origin_exact_is_active",
        "origin_seed_is_active",
        "origin_time_is_active",
        "optimal_exact_error",
        "optimal_seed_error",
        "optimal_time_error",
        "path_partner_persistence",
        "seed_path_partner_persistence",
        "time_path_partner_persistence",
        "path_flip_persistence",
        "seed_path_flip_persistence",
        "time_path_flip_persistence",
        "path_adjacency_share",
        "seed_path_adjacency_share",
        "time_path_adjacency_share",
        "path_self_return",
        "seed_path_self_return",
        "time_path_self_return",
    )
    result: dict[str, float | int] = {
        "events": len(rows),
        "weight": float(sum(float(row["weight"]) for row in rows)),
        "trials": len({(int(row["branch"]), int(row["seed"])) for row in rows}),
    }
    for metric in metrics:
        result[metric] = weighted_mean(rows, metric)
    result.update(describe_partner_concentration(rows, "optimal_exact_pair"))
    seed_concentration = describe_partner_concentration(rows, "optimal_seed_pair")
    time_concentration = describe_partner_concentration(rows, "optimal_time_pair")
    result["seed_modal_partner_concentration"] = seed_concentration[
        "modal_partner_concentration"
    ]
    result["seed_partner_entropy"] = seed_concentration["partner_entropy"]
    result["time_modal_partner_concentration"] = time_concentration[
        "modal_partner_concentration"
    ]
    result["time_partner_entropy"] = time_concentration["partner_entropy"]
    return result


def trial_summaries(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[int, int, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[
            (int(row["branch"]), int(row["seed"]), str(row["split"]))
        ].append(row)
    output: list[dict[str, object]] = []
    for (branch, seed, split), group_rows in sorted(grouped.items()):
        summary = summarize(group_rows)
        output.append(
            {
                "split": split,
                "branch": BRANCH_LABELS[branch],
                "branch_index": branch,
                "seed": seed,
                **summary,
            }
        )
    return output


def bootstrap(
    trial_rows: list[dict[str, object]],
) -> dict[str, float]:
    metrics = {
        "origin_exact_beats_seed": (
            "origin_seed_error",
            "origin_exact_error",
        ),
        "origin_exact_beats_time": (
            "origin_time_error",
            "origin_exact_error",
        ),
        "optimal_exact_beats_seed": (
            "optimal_seed_error",
            "optimal_exact_error",
        ),
        "optimal_exact_beats_time": (
            "optimal_time_error",
            "optimal_exact_error",
        ),
        "local_share_above_seed": (
            "origin_exact_is_local",
            "origin_seed_is_local",
        ),
        "local_share_above_time": (
            "origin_exact_is_local",
            "origin_time_is_local",
        ),
        "partner_persistence_above_seed": (
            "path_partner_persistence",
            "seed_path_partner_persistence",
        ),
        "partner_persistence_above_time": (
            "path_partner_persistence",
            "time_path_partner_persistence",
        ),
        "adjacency_above_seed": (
            "path_adjacency_share",
            "seed_path_adjacency_share",
        ),
        "adjacency_above_time": (
            "path_adjacency_share",
            "time_path_adjacency_share",
        ),
    }
    arrays = {
        name: (
            np.asarray([float(row[left]) for row in trial_rows]),
            np.asarray([float(row[right]) for row in trial_rows]),
        )
        for name, (left, right) in metrics.items()
    }
    rng = np.random.default_rng(RNG_SEED)
    wins = {name: 0 for name in metrics}
    count = len(trial_rows)
    for _ in range(BOOTSTRAP_DRAWS):
        indices = rng.integers(0, count, size=count)
        for name, (left, right) in arrays.items():
            if float(np.nanmean(left[indices] - right[indices])) > 0:
                wins[name] += 1
    return {name: wins[name] / BOOTSTRAP_DRAWS for name in metrics}


def axis_match(
    source_value: float,
    candidates: list[dict[str, object]],
) -> tuple[float, int, int]:
    """Match one signed axis value with no fitted scale.

    Returns normalized absolute error, candidate position, and whether the
    candidate had to be sign-flipped.  Direct and flipped routes are both
    tested because a singularity/anti-phase account predicts signed reversal.
    """
    values = np.asarray(
        [float(candidate["residual_z_scaled"]) for candidate in candidates],
        dtype=np.float64,
    )
    denominator = np.abs(values) + abs(source_value) + EPS
    direct = np.abs(values - source_value) / denominator
    flipped = np.abs(values + source_value) / denominator
    stacked = np.column_stack((direct, flipped))
    position, sign_flip = np.unravel_index(
        int(np.argmin(stacked)),
        stacked.shape,
    )
    return float(stacked[position, sign_flip]), int(position), int(sign_flip)


def stable_candidate_order(row: dict[str, object]) -> tuple[int, int, int]:
    """Deterministic order used to equalize candidate counts across controls."""
    pair = int(row["source_pair_index"])
    endpoint = int(row["endpoint"])
    time = int(row["origin_time"])
    return ((113 * pair + 29 * endpoint + 17 * time) % 997, pair, endpoint)


def axis_route_summary(
    route: list[dict[str, object]],
    source_pair: int,
    source_endpoint: int,
    strongest_child: int,
) -> dict[str, float]:
    if not route:
        return {
            "error": math.nan,
            "sign_flip_share": math.nan,
            "same_source_pair_share": math.nan,
            "shares_source_endpoint": math.nan,
            "strongest_child_share": math.nan,
            "partner_persistence": math.nan,
            "adjacency_share": math.nan,
            "self_return": math.nan,
            "mean_absolute_time_jitter": math.nan,
        }
    errors = np.asarray([float(item["error"]) for item in route])
    pairs = [int(item["destination_pair"]) for item in route]
    flips = [int(item["sign_flip"]) for item in route]
    pair_counts = Counter(pairs)
    adjacency = (
        float(
            np.mean(
                [
                    pair_shares_node(first, second)
                    for first, second in zip(pairs[:-1], pairs[1:])
                ]
            )
        )
        if len(pairs) > 1
        else math.nan
    )
    return {
        "error": float(np.mean(errors)),
        "sign_flip_share": float(np.mean(flips)),
        "same_source_pair_share": float(
            np.mean([pair == source_pair for pair in pairs])
        ),
        "shares_source_endpoint": float(
            np.mean([source_endpoint in PAIRS[pair] for pair in pairs])
        ),
        "strongest_child_share": float(
            np.mean([pair == strongest_child for pair in pairs])
        ),
        "partner_persistence": max(pair_counts.values()) / len(pairs),
        "adjacency_share": adjacency,
        "self_return": float(source_pair in pairs),
        "mean_absolute_time_jitter": float(
            np.mean([abs(int(item["time_jitter"])) for item in route])
        ),
    }


def axis_native_analysis(
    event_rows: list[dict[str, object]],
) -> tuple[
    dict[str, object],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
]:
    """Surf the exposed z-axis remainder as its own signed ARA coordinate."""
    axis_lags = tuple(range(1, 7))
    index: dict[tuple[str, int, int, int], list[dict[str, object]]] = defaultdict(
        list
    )
    for row in event_rows:
        index[
            (
                str(row["split"]),
                int(row["branch"]),
                int(row["seed"]),
                int(row["origin_time"]),
            )
        ].append(row)
    for candidates in index.values():
        candidates.sort(key=stable_candidate_order)

    def nearest_pool(
        split: str,
        branch: int,
        seed: int,
        requested_time: int,
        maximum_jitter: int = 3,
    ) -> tuple[list[dict[str, object]], int]:
        lower = 2 if split == "development" else 252
        upper = 243 if split == "development" else 493
        offsets = [0]
        for distance in range(1, maximum_jitter + 1):
            offsets.extend((-distance, distance))
        for offset in offsets:
            candidate_time = requested_time + offset
            if candidate_time < lower or candidate_time > upper:
                continue
            candidates = index.get(
                (split, branch, seed, candidate_time),
                [],
            )
            if candidates:
                return candidates, offset
        return [], 0

    axis_event_rows: list[dict[str, object]] = []
    lag_accumulator: dict[
        tuple[str, int], list[tuple[float, float, int]]
    ] = defaultdict(list)
    route_sample_rows: list[dict[str, object]] = []

    for row in event_rows:
        split = str(row["split"])
        branch = int(row["branch"])
        seed = int(row["seed"])
        origin_time = int(row["origin_time"])
        source_pair = int(row["source_pair_index"])
        endpoint = int(row["endpoint"])
        strongest_child = int(row["strongest_child"])
        source_value = float(row["residual_z_scaled"])
        weight = float(row["weight"])
        routes: dict[str, list[dict[str, object]]] = {
            "exact": [],
            "seed": [],
            "time": [],
        }

        for lag in axis_lags:
            exact_candidates, exact_jitter = nearest_pool(
                split,
                branch,
                seed,
                origin_time + lag,
            )
            seed_candidates, seed_jitter = nearest_pool(
                split,
                branch,
                (seed + 37) % 100,
                origin_time + lag,
            )
            split_start = 2 if split == "development" else 252
            valid_origins = 250 - Q28_LAG - lag
            shifted_base = split_start + (
                (origin_time - split_start + 137) % valid_origins
            )
            time_candidates, time_jitter = nearest_pool(
                split,
                branch,
                seed,
                shifted_base + lag,
            )
            matched_count = min(
                len(exact_candidates),
                len(seed_candidates),
                len(time_candidates),
            )
            if matched_count <= 0:
                continue
            pools = {
                "exact": (exact_candidates[:matched_count], exact_jitter),
                "seed": (seed_candidates[:matched_count], seed_jitter),
                "time": (time_candidates[:matched_count], time_jitter),
            }
            for control, (candidates, time_jitter) in pools.items():
                error, position, sign_flip = axis_match(source_value, candidates)
                destination = candidates[position]
                route_item = {
                    "lag": lag,
                    "error": error,
                    "sign_flip": sign_flip,
                    "destination_pair": int(destination["source_pair_index"]),
                    "destination_endpoint": int(destination["endpoint"]),
                    "destination_origin_time": int(destination["origin_time"]),
                    "candidate_count": matched_count,
                    "time_jitter": time_jitter,
                }
                routes[control].append(route_item)
                lag_accumulator[(control, lag)].append(
                    (weight, error, sign_flip)
                )

        if not routes["exact"]:
            continue
        summaries = {
            control: axis_route_summary(
                route,
                source_pair,
                endpoint,
                strongest_child,
            )
            for control, route in routes.items()
        }
        axis_row: dict[str, object] = {
            "split": split,
            "branch": branch,
            "branch_label": str(row["branch_label"]),
            "seed": seed,
            "origin_time": origin_time,
            "source_pair_index": source_pair,
            "endpoint": endpoint,
            "weight": weight,
            "residual_z_scaled": source_value,
            "available_lags": len(routes["exact"]),
        }
        for control, summary in summaries.items():
            for metric, value in summary.items():
                axis_row[f"{control}_{metric}"] = value
        axis_event_rows.append(axis_row)

        sample_key = (
            109 * seed
            + 71 * origin_time
            + 47 * source_pair
            + 31 * endpoint
            + 23 * branch
        )
        if sample_key % 64 == 0:
            route_id = (
                f"{BRANCH_LABELS[branch]}-{seed}-{origin_time}-"
                f"{source_pair}-{endpoint}"
            )
            for control, route in routes.items():
                for item in route:
                    destination_pair = int(item["destination_pair"])
                    route_sample_rows.append(
                        {
                            "route_id": route_id,
                            "split": split,
                            "control": control,
                            "lag": int(item["lag"]),
                            "source_pair": (
                                f"{PAIRS[source_pair][0]}-{PAIRS[source_pair][1]}"
                            ),
                            "source_endpoint": endpoint,
                            "source_z": source_value,
                            "destination_pair": (
                                f"{PAIRS[destination_pair][0]}-"
                                f"{PAIRS[destination_pair][1]}"
                            ),
                            "destination_endpoint": int(
                                item["destination_endpoint"]
                            ),
                            "destination_origin_time": int(
                                item["destination_origin_time"]
                            ),
                            "sign_flip": int(item["sign_flip"]),
                            "axis_error": float(item["error"]),
                            "matched_candidate_count": int(
                                item["candidate_count"]
                            ),
                            "time_jitter": int(item["time_jitter"]),
                            "weight": weight,
                        }
                    )

    if not axis_event_rows:
        raise RuntimeError("No matched axis-native surfer routes")

    metric_names = (
        "error",
        "sign_flip_share",
        "same_source_pair_share",
        "shares_source_endpoint",
        "strongest_child_share",
        "partner_persistence",
        "adjacency_share",
        "self_return",
        "mean_absolute_time_jitter",
    )

    def axis_summary(rows: list[dict[str, object]]) -> dict[str, float | int]:
        output: dict[str, float | int] = {
            "events": len(rows),
            "weight": float(sum(float(item["weight"]) for item in rows)),
            "trials": len(
                {
                    (int(item["branch"]), int(item["seed"]))
                    for item in rows
                }
            ),
            "mean_available_lags": weighted_mean(rows, "available_lags"),
        }
        for control in ("exact", "seed", "time"):
            for metric in metric_names:
                output[f"{control}_{metric}"] = weighted_mean(
                    rows,
                    f"{control}_{metric}",
                )
        return output

    pooled = axis_summary(axis_event_rows)
    split_summaries = {
        split: axis_summary(
            [row for row in axis_event_rows if row["split"] == split]
        )
        for split in SPLITS
    }

    grouped: dict[
        tuple[str, int, int], list[dict[str, object]]
    ] = defaultdict(list)
    for row in axis_event_rows:
        grouped[
            (str(row["split"]), int(row["branch"]), int(row["seed"]))
        ].append(row)
    trial_rows: list[dict[str, object]] = []
    for (split, branch, seed), rows in sorted(grouped.items()):
        trial_rows.append(
            {
                "split": split,
                "branch": BRANCH_LABELS[branch],
                "branch_index": branch,
                "seed": seed,
                **axis_summary(rows),
            }
        )

    opened_trials = [
        row for row in trial_rows if row["split"] == "opened_later_half"
    ]
    rng = np.random.default_rng(RNG_SEED + 1)
    bootstrap_wins = {
        "exact_error_below_seed": 0,
        "exact_error_below_time": 0,
        "exact_endpoint_share_above_seed": 0,
        "exact_endpoint_share_above_time": 0,
        "exact_partner_persistence_above_seed": 0,
        "exact_partner_persistence_above_time": 0,
    }
    count = len(opened_trials)
    for _ in range(BOOTSTRAP_DRAWS):
        chosen = rng.integers(0, count, size=count)
        sampled = [opened_trials[index] for index in chosen]
        comparisons = {
            "exact_error_below_seed": np.nanmean(
                [
                    float(item["seed_error"]) - float(item["exact_error"])
                    for item in sampled
                ]
            ),
            "exact_error_below_time": np.nanmean(
                [
                    float(item["time_error"]) - float(item["exact_error"])
                    for item in sampled
                ]
            ),
            "exact_endpoint_share_above_seed": np.nanmean(
                [
                    float(item["exact_shares_source_endpoint"])
                    - float(item["seed_shares_source_endpoint"])
                    for item in sampled
                ]
            ),
            "exact_endpoint_share_above_time": np.nanmean(
                [
                    float(item["exact_shares_source_endpoint"])
                    - float(item["time_shares_source_endpoint"])
                    for item in sampled
                ]
            ),
            "exact_partner_persistence_above_seed": np.nanmean(
                [
                    float(item["exact_partner_persistence"])
                    - float(item["seed_partner_persistence"])
                    for item in sampled
                ]
            ),
            "exact_partner_persistence_above_time": np.nanmean(
                [
                    float(item["exact_partner_persistence"])
                    - float(item["time_partner_persistence"])
                    for item in sampled
                ]
            ),
        }
        for name, difference in comparisons.items():
            if float(difference) > 0:
                bootstrap_wins[name] += 1
    bootstrap_results = {
        name: wins / BOOTSTRAP_DRAWS
        for name, wins in bootstrap_wins.items()
    }

    lag_rows: list[dict[str, object]] = []
    for control in ("exact", "seed", "time"):
        for lag in axis_lags:
            values = lag_accumulator[(control, lag)]
            weights = np.asarray([value[0] for value in values], dtype=np.float64)
            errors = np.asarray([value[1] for value in values], dtype=np.float64)
            flips = np.asarray([value[2] for value in values], dtype=np.float64)
            lag_rows.append(
                {
                    "control": control,
                    "lag": lag,
                    "events": len(values),
                    "weight": float(np.sum(weights)),
                    "axis_error": float(np.sum(weights * errors) / np.sum(weights)),
                    "sign_flip_share": float(
                        np.sum(weights * flips) / np.sum(weights)
                    ),
                }
            )

    comparisons = {
        "axis_error_advantage_vs_seed": (
            float(pooled["seed_error"]) - float(pooled["exact_error"])
        )
        / float(pooled["seed_error"]),
        "axis_error_advantage_vs_time": (
            float(pooled["time_error"]) - float(pooled["exact_error"])
        )
        / float(pooled["time_error"]),
        "endpoint_share_advantage_vs_seed": float(
            pooled["exact_shares_source_endpoint"]
        )
        - float(pooled["seed_shares_source_endpoint"]),
        "endpoint_share_advantage_vs_time": float(
            pooled["exact_shares_source_endpoint"]
        )
        - float(pooled["time_shares_source_endpoint"]),
        "partner_persistence_advantage_vs_seed": float(
            pooled["exact_partner_persistence"]
        )
        - float(pooled["seed_partner_persistence"]),
        "partner_persistence_advantage_vs_time": float(
            pooled["exact_partner_persistence"]
        )
        - float(pooled["time_partner_persistence"]),
    }
    result: dict[str, object] = {
        "method": (
            "signed z-axis residual u=r_z/||W|| (equivalently ARA "
            "x_z=1+u on 0-2); direct and sign-flipped recurrence compared "
            "without fitted scale"
        ),
        "matched_control_policy": (
            "exact, seed-displaced and time-displaced candidate pools are "
            "deterministically truncated to the same size per event and lag"
        ),
        "pooled": pooled,
        "splits": split_summaries,
        "comparisons": comparisons,
        "bootstrap_opened_later_half": bootstrap_results,
    }
    return result, trial_rows, lag_rows, route_sample_rows


def make_axis_figure(
    all_rows: list[dict[str, object]],
    axis_result: dict[str, object],
    lag_rows: list[dict[str, object]],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pooled = axis_result["pooled"]
    assert isinstance(pooled, dict)
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
    fig.suptitle(
        "Q29 axis-native check: does the narrow remainder travel?",
        fontsize=18,
        fontweight="bold",
    )

    centered_values = np.asarray(
        [float(row["residual_z_scaled"]) for row in all_rows],
        dtype=np.float64,
    )
    values = 1.0 + centered_values
    weights = np.asarray(
        [float(row["weight"]) for row in all_rows],
        dtype=np.float64,
    )
    limit = float(np.quantile(np.abs(centered_values), 0.995))
    axes[0, 0].hist(
        values,
        bins=np.linspace(1.0 - limit, 1.0 + limit, 61),
        weights=weights / np.sum(weights),
        color="#4f79a7",
        edgecolor="#293642",
        linewidth=0.3,
    )
    axes[0, 0].axvline(1.0, color="#293642", linewidth=1)
    axes[0, 0].set_title("Signed z remainder on its ARA diameter")
    axes[0, 0].set_xlabel("ARA x_z = 1 + residual z / later-web norm")
    axes[0, 0].set_ylabel("weighted event share")
    axes[0, 0].grid(axis="y", alpha=0.2)

    for control, color, style in (
        ("exact", "#4f79a7", "-"),
        ("seed", "#d49a3a", "--"),
        ("time", "#7a8793", ":"),
    ):
        selected = [row for row in lag_rows if row["control"] == control]
        axes[0, 1].plot(
            [int(row["lag"]) for row in selected],
            [float(row["axis_error"]) for row in selected],
            marker="o",
            color=color,
            linestyle=style,
            label=control,
        )
    axes[0, 1].set_title("No-scale axis recurrence against controls")
    axes[0, 1].set_xlabel("slices after the residual origin")
    axes[0, 1].set_ylabel("normalized signed-axis error")
    axes[0, 1].grid(alpha=0.2)
    axes[0, 1].legend(frameon=False)

    controls = ("exact", "seed", "time")
    colors = ("#4f79a7", "#d49a3a", "#aeb8c1")
    x = np.arange(len(controls))
    axes[1, 0].bar(
        x,
        [float(pooled[f"{control}_sign_flip_share"]) for control in controls],
        color=colors,
        edgecolor="#293642",
        linewidth=0.4,
    )
    axes[1, 0].set_title("Does the best recurrence require a sign flip?")
    axes[1, 0].set_xticks(x, controls)
    axes[1, 0].set_ylabel("weighted sign-flip share")
    axes[1, 0].set_ylim(0, 1)
    axes[1, 0].grid(axis="y", alpha=0.2)

    metrics = (
        ("shares_source_endpoint", "shares endpoint"),
        ("strongest_child_share", "original child"),
        ("partner_persistence", "partner persists"),
        ("adjacency_share", "adjacent route"),
    )
    width = 0.25
    metric_x = np.arange(len(metrics))
    for offset, control, color in zip((-width, 0.0, width), controls, colors):
        axes[1, 1].bar(
            metric_x + offset,
            [float(pooled[f"{control}_{metric}"]) for metric, _ in metrics],
            width,
            color=color,
            label=control,
        )
    axes[1, 1].set_title("Topology of the axis-native best route")
    axes[1, 1].set_xticks(
        metric_x,
        [label for _, label in metrics],
        rotation=18,
        ha="right",
    )
    axes[1, 1].set_ylim(0, 1)
    axes[1, 1].set_ylabel("weighted share")
    axes[1, 1].grid(axis="y", alpha=0.2)
    axes[1, 1].legend(frameon=False)

    fig.text(
        0.01,
        0.005,
        "DERIVED from public simulated connected relations; ARA ridge = 1.",
        fontsize=9,
        color="#40505c",
    )
    fig.savefig(AXIS_FIGURE_PNG, dpi=180)
    fig.savefig(AXIS_FIGURE_SVG)
    plt.close(fig)


def make_figure(
    all_rows: list[dict[str, object]],
    lag_rows: list[dict[str, object]],
    pooled: dict[str, float | int],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.edgecolor": "#293642",
            "axes.labelcolor": "#1f2933",
            "xtick.color": "#40505c",
            "ytick.color": "#40505c",
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    fig.suptitle(
        "Q29 unclassified component: shape and lattice route",
        fontsize=18,
        fontweight="bold",
    )

    residuals = np.asarray([float(row["residual_fraction"]) for row in all_rows])
    weights = np.asarray([float(row["weight"]) for row in all_rows])
    axes[0, 0].hist(
        residuals,
        bins=np.linspace(0, min(1.0, np.quantile(residuals, 0.995)), 45),
        weights=weights / np.sum(weights),
        color="#4f79a7",
        edgecolor="#293642",
        linewidth=0.35,
    )
    axes[0, 0].set_title("Residual fraction after the best Q28 flip")
    axes[0, 0].set_xlabel("||unclassified component|| / ||later web||")
    axes[0, 0].set_ylabel("weighted event share")
    axes[0, 0].grid(axis="y", alpha=0.2)

    for control, color, style in (
        ("exact", "#4f79a7", "-"),
        ("seed", "#d49a3a", "--"),
        ("time", "#7a8793", ":"),
    ):
        selected = [row for row in lag_rows if row["control"] == control]
        axes[0, 1].plot(
            [int(row["lag"]) for row in selected],
            [float(row["best_error"]) for row in selected],
            marker="o",
            color=color,
            linestyle=style,
            label=control,
        )
    axes[0, 1].set_title("Best-of-lattice shape match by later slice")
    axes[0, 1].set_xlabel("slices after residual origin")
    axes[0, 1].set_ylabel("target-normalized residual")
    axes[0, 1].grid(alpha=0.2)
    axes[0, 1].legend(frameon=False)

    category_labels = (
        "local child",
        "strongest child",
        "shares source endpoint",
        "active edge",
    )
    exact_values = (
        float(pooled["origin_exact_is_local"]),
        float(pooled["origin_exact_is_strongest_child"]),
        float(pooled["origin_exact_shares_endpoint"]),
        float(pooled["origin_exact_is_active"]),
    )
    seed_values = (
        float(pooled["origin_seed_is_local"]),
        float(pooled["origin_seed_is_strongest_child"]),
        float(pooled["origin_seed_shares_endpoint"]),
        float(pooled["origin_seed_is_active"]),
    )
    time_values = (
        float(pooled["origin_time_is_local"]),
        float(pooled["origin_time_is_strongest_child"]),
        float(pooled["origin_time_shares_endpoint"]),
        float(pooled["origin_time_is_active"]),
    )
    x = np.arange(len(category_labels))
    width = 0.25
    axes[1, 0].bar(x - width, exact_values, width, color="#4f79a7", label="exact")
    axes[1, 0].bar(x, seed_values, width, color="#d49a3a", label="seed displaced")
    axes[1, 0].bar(
        x + width,
        time_values,
        width,
        color="#aeb8c1",
        edgecolor="#293642",
        linewidth=0.4,
        label="time displaced",
    )
    axes[1, 0].set_title("Where the residual first lands")
    axes[1, 0].set_xticks(x, category_labels, rotation=18, ha="right")
    axes[1, 0].set_ylabel("weighted share")
    axes[1, 0].set_ylim(0, 1)
    axes[1, 0].grid(axis="y", alpha=0.2)
    axes[1, 0].legend(frameon=False)

    route_labels = ("partner persists", "flip persists", "adjacent steps", "returns")
    exact_route = (
        float(pooled["path_partner_persistence"]),
        float(pooled["path_flip_persistence"]),
        float(pooled["path_adjacency_share"]),
        float(pooled["path_self_return"]),
    )
    seed_route = (
        float(pooled["seed_path_partner_persistence"]),
        float(pooled["seed_path_flip_persistence"]),
        float(pooled["seed_path_adjacency_share"]),
        float(pooled["seed_path_self_return"]),
    )
    time_route = (
        float(pooled["time_path_partner_persistence"]),
        float(pooled["time_path_flip_persistence"]),
        float(pooled["time_path_adjacency_share"]),
        float(pooled["time_path_self_return"]),
    )
    axes[1, 1].bar(x - width, exact_route, width, color="#4f79a7", label="exact")
    axes[1, 1].bar(x, seed_route, width, color="#d49a3a", label="seed displaced")
    axes[1, 1].bar(
        x + width,
        time_route,
        width,
        color="#aeb8c1",
        edgecolor="#293642",
        linewidth=0.4,
        label="time displaced",
    )
    axes[1, 1].set_title("How the best-matching route behaves")
    axes[1, 1].set_xticks(x, route_labels, rotation=18, ha="right")
    axes[1, 1].set_ylabel("weighted share")
    axes[1, 1].set_ylim(0, 1)
    axes[1, 1].grid(axis="y", alpha=0.2)
    axes[1, 1].legend(frameon=False)

    fig.text(
        0.01,
        0.005,
        "DERIVED from the public simulated Q27/Q28 connected-relation source.",
        fontsize=9,
        color="#40505c",
    )
    fig.savefig(FIGURE_PNG, dpi=180)
    fig.savefig(FIGURE_SVG)
    plt.close(fig)


def analyse(quiet: bool = False) -> None:
    if not Q27_CACHE.exists() or not CONNECTED_CACHE.exists():
        q28_runner = HERE / "q28_ara9_interlocking_rotational_transport_test.py"
        if not q28_runner.exists():
            raise FileNotFoundError(
                "Q27/Q28 caches are absent and the Q28 extraction runner "
                "could not be found"
            )
        subprocess.run(
            [
                sys.executable,
                str(q28_runner),
                "extract",
                "--workers",
                "6",
            ],
            cwd=HERE,
            check=True,
        )
    if not Q27_CACHE.exists() or not CONNECTED_CACHE.exists():
        raise FileNotFoundError("Q28 extraction did not produce required caches")

    q27 = np.load(Q27_CACHE, allow_pickle=False)
    closure = np.asarray(q27["closure"], dtype=np.float32)
    edges = np.asarray(q27["edges"], dtype=np.int8)
    connected = np.load(CONNECTED_CACHE, mmap_mode="r")
    if connected.shape != (2, 100, 500, 66, 3, 3):
        raise RuntimeError(f"Unexpected connected cache shape {connected.shape}")

    maximum_off_diagonal = max(
        float(np.max(np.abs(connected[..., row, column])))
        for row in range(3)
        for column in range(3)
        if row != column
    )

    event_rows: list[dict[str, object]] = []
    route_sample_rows: list[dict[str, object]] = []
    mode_weights: dict[tuple[str, str, str], float] = defaultdict(float)
    lag_accumulator: dict[tuple[str, int], list[tuple[float, float]]] = defaultdict(list)

    for split, starts in SPLITS.items():
        for branch in range(2):
            for seed in range(100):
                connected_seed = connected[branch, seed]
                closure_seed = closure[branch, seed]
                edges_seed = edges[branch, seed]
                displaced_seed = (seed + 37) % 100
                connected_displaced = connected[branch, displaced_seed]

                for time in starts:
                    active = active_pair_indices(edges_seed[time])
                    if not active:
                        continue
                    for pair_index, pair in enumerate(PAIRS):
                        release = max(
                            0.0,
                            float(
                                closure_seed[time, pair_index]
                                - closure_seed[time + 1, pair_index]
                            ),
                        )
                        if release <= 0:
                            continue
                        for endpoint in pair:
                            if not q28_sampled(
                                branch, seed, time, pair_index, endpoint
                            ):
                                continue
                            if not q29_sampled(
                                branch, seed, time, pair_index, endpoint
                            ):
                                continue
                            local_targets = [
                                target
                                for target in active
                                if target != pair_index and endpoint in PAIRS[target]
                            ]
                            if not local_targets:
                                continue
                            accumulations = np.asarray(
                                [
                                    max(
                                        0.0,
                                        float(
                                            closure_seed[time + Q28_LAG, target]
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

                            source = relation_vector(
                                connected_seed[time, pair_index]
                            )
                            target_web = build_web(
                                connected_seed,
                                time + Q28_LAG,
                                local_targets,
                                accumulations,
                            )
                            fit_error, alpha, source_flip = discrete_fit(
                                source,
                                target_web,
                            )
                            if not np.isfinite(fit_error):
                                continue
                            transported = (
                                alpha * FLIP_MASKS[source_flip] * source
                            )
                            residual = target_web - transported
                            target_norm = float(np.linalg.norm(target_web))
                            residual_norm = float(np.linalg.norm(residual))
                            if target_norm <= 1e-8 or residual_norm <= 1e-10:
                                continue
                            residual_fraction = residual_norm / target_norm
                            (
                                residual_entropy,
                                residual_largest_axis,
                                residual_effective_dimension,
                            ) = component_entropy(residual)
                            child_entropy = normalized_entropy(accumulations)
                            strongest_child_position = int(np.argmax(accumulations))
                            strongest_child = local_targets[strongest_child_position]
                            strongest_child_share = (
                                float(accumulations[strongest_child_position])
                                / accumulation
                            )
                            positive_child_count = int(
                                np.count_nonzero(accumulations > 0)
                            )

                            origin_time = time + Q28_LAG
                            exact_path = surf(residual, connected_seed, origin_time)
                            seed_path = surf(
                                residual,
                                connected_displaced,
                                origin_time,
                            )
                            shifted_origin = state_shift(origin_time, split)
                            time_path = surf(
                                residual,
                                connected_seed,
                                shifted_origin,
                            )

                            exact_metrics = path_metrics(exact_path, pair_index)
                            seed_metrics = path_metrics(seed_path, pair_index)
                            time_metrics = path_metrics(time_path, pair_index)

                            exact_opt_index = int(np.argmin(exact_path.errors))
                            seed_opt_index = int(np.argmin(seed_path.errors))
                            time_opt_index = int(np.argmin(time_path.errors))
                            exact_origin_pair = exact_path.pairs[0]
                            seed_origin_pair = seed_path.pairs[0]
                            time_origin_pair = time_path.pairs[0]
                            candidate_active = set(
                                active_pair_indices(
                                    edges_seed[min(origin_time, 498)]
                                )
                            )

                            row: dict[str, object] = {
                                "split": split,
                                "branch": branch,
                                "branch_label": BRANCH_LABELS[branch],
                                "seed": seed,
                                "time": time,
                                "origin_time": origin_time,
                                "source_pair_index": pair_index,
                                "source_pair": f"{pair[0]}-{pair[1]}",
                                "endpoint": endpoint,
                                "weight": weight,
                                "release": release,
                                "accumulation": accumulation,
                                "q28_fit_error": fit_error,
                                "q28_source_flip": source_flip,
                                "residual_fraction": residual_fraction,
                                "residual_x": float(residual[0]),
                                "residual_y": float(residual[1]),
                                "residual_z": float(residual[2]),
                                "residual_z_scaled": float(
                                    residual[2] / target_norm
                                ),
                                "residual_z_ara": float(
                                    1.0 + residual[2] / target_norm
                                ),
                                "target_norm": target_norm,
                                "residual_component_entropy": residual_entropy,
                                "residual_largest_axis_share": residual_largest_axis,
                                "residual_effective_dimension": residual_effective_dimension,
                                "residual_dominant_axis": int(np.argmax(np.abs(residual))),
                                "child_weight_entropy": child_entropy,
                                "strongest_child_weight_share": strongest_child_share,
                                "positive_child_count": positive_child_count,
                                "strongest_child": strongest_child,
                                "origin_exact_error": exact_path.errors[0],
                                "origin_seed_error": seed_path.errors[0],
                                "origin_time_error": time_path.errors[0],
                                "origin_exact_pair": exact_origin_pair,
                                "origin_seed_pair": seed_origin_pair,
                                "origin_time_pair": time_origin_pair,
                                "origin_exact_flip": exact_path.flips[0],
                                "origin_seed_flip": seed_path.flips[0],
                                "origin_time_flip": time_path.flips[0],
                                "origin_exact_is_local": float(
                                    exact_origin_pair in local_targets
                                ),
                                "origin_seed_is_local": float(
                                    seed_origin_pair in local_targets
                                ),
                                "origin_time_is_local": float(
                                    time_origin_pair in local_targets
                                ),
                                "origin_exact_is_strongest_child": float(
                                    exact_origin_pair == strongest_child
                                ),
                                "origin_seed_is_strongest_child": float(
                                    seed_origin_pair == strongest_child
                                ),
                                "origin_time_is_strongest_child": float(
                                    time_origin_pair == strongest_child
                                ),
                                "origin_exact_shares_endpoint": float(
                                    endpoint in PAIRS[exact_origin_pair]
                                ),
                                "origin_seed_shares_endpoint": float(
                                    endpoint in PAIRS[seed_origin_pair]
                                ),
                                "origin_time_shares_endpoint": float(
                                    endpoint in PAIRS[time_origin_pair]
                                ),
                                "origin_exact_is_active": float(
                                    exact_origin_pair in candidate_active
                                ),
                                "origin_seed_is_active": float(
                                    seed_origin_pair in candidate_active
                                ),
                                "origin_time_is_active": float(
                                    time_origin_pair in candidate_active
                                ),
                                "optimal_exact_error": exact_path.errors[
                                    exact_opt_index
                                ],
                                "optimal_seed_error": seed_path.errors[seed_opt_index],
                                "optimal_time_error": time_path.errors[time_opt_index],
                                "optimal_exact_lag": SURF_LAGS[exact_opt_index],
                                "optimal_seed_lag": SURF_LAGS[seed_opt_index],
                                "optimal_time_lag": SURF_LAGS[time_opt_index],
                                "optimal_exact_pair": exact_path.pairs[exact_opt_index],
                                "optimal_seed_pair": seed_path.pairs[seed_opt_index],
                                "optimal_time_pair": time_path.pairs[time_opt_index],
                                "optimal_exact_flip": exact_path.flips[exact_opt_index],
                                "optimal_seed_flip": seed_path.flips[seed_opt_index],
                                "optimal_time_flip": time_path.flips[time_opt_index],
                                **exact_metrics,
                                "seed_path_partner_persistence": seed_metrics[
                                    "path_partner_persistence"
                                ],
                                "seed_path_flip_persistence": seed_metrics[
                                    "path_flip_persistence"
                                ],
                                "seed_path_adjacency_share": seed_metrics[
                                    "path_adjacency_share"
                                ],
                                "seed_path_self_return": seed_metrics[
                                    "path_self_return"
                                ],
                                "time_path_partner_persistence": time_metrics[
                                    "path_partner_persistence"
                                ],
                                "time_path_flip_persistence": time_metrics[
                                    "path_flip_persistence"
                                ],
                                "time_path_adjacency_share": time_metrics[
                                    "path_adjacency_share"
                                ],
                                "time_path_self_return": time_metrics[
                                    "path_self_return"
                                ],
                            }
                            event_rows.append(row)

                            dominant_axis = ("x", "y", "z")[
                                int(row["residual_dominant_axis"])
                            ]
                            mode_weights[
                                (
                                    split,
                                    FLIP_NAMES[source_flip],
                                    dominant_axis,
                                )
                            ] += weight

                            for control, path in (
                                ("exact", exact_path),
                                ("seed", seed_path),
                                ("time", time_path),
                            ):
                                for lag, error in zip(SURF_LAGS, path.errors):
                                    if np.isfinite(error):
                                        lag_accumulator[(control, lag)].append(
                                            (weight, error)
                                        )

                            sample_key = (
                                103 * seed
                                + 61 * time
                                + 41 * pair_index
                                + 29 * endpoint
                                + 17 * branch
                            )
                            if sample_key % 32 == 0:
                                route_id = (
                                    f"{BRANCH_LABELS[branch]}-{seed}-{time}-"
                                    f"{pair_index}-{endpoint}"
                                )
                                for control, path in (
                                    ("exact", exact_path),
                                    ("seed", seed_path),
                                    ("time", time_path),
                                ):
                                    for lag, error, destination, flip in zip(
                                        SURF_LAGS,
                                        path.errors,
                                        path.pairs,
                                        path.flips,
                                    ):
                                        route_sample_rows.append(
                                            {
                                                "route_id": route_id,
                                                "split": split,
                                                "control": control,
                                                "lag": lag,
                                                "source_pair": f"{pair[0]}-{pair[1]}",
                                                "endpoint": endpoint,
                                                "destination_pair": (
                                                    f"{PAIRS[destination][0]}-"
                                                    f"{PAIRS[destination][1]}"
                                                ),
                                                "flip": FLIP_NAMES[flip],
                                                "shape_error": error,
                                                "weight": weight,
                                            }
                                        )
                if not quiet and (seed % 10 == 9 or seed == 99):
                    print(
                        f"Q29 {split} {BRANCH_LABELS[branch]} seed {seed:02d}: "
                        f"{len(event_rows)} cumulative events",
                        flush=True,
                    )

    if not event_rows:
        raise RuntimeError("No eligible Q29 events")

    split_summaries = {
        split: summarize([row for row in event_rows if row["split"] == split])
        for split in SPLITS
    }
    branch_summaries = {
        label: summarize(
            [row for row in event_rows if row["branch_label"] == label]
        )
        for label in BRANCH_LABELS
    }
    pooled = summarize(event_rows)
    trial_rows = trial_summaries(event_rows)
    bootstrap_rows = [
        row for row in trial_rows if row["split"] == "opened_later_half"
    ]
    bootstrap_results = bootstrap(bootstrap_rows)
    (
        axis_result,
        axis_trial_rows,
        axis_lag_rows,
        axis_route_sample_rows,
    ) = axis_native_analysis(event_rows)

    lag_rows: list[dict[str, object]] = []
    for control in ("exact", "seed", "time"):
        for lag in SURF_LAGS:
            values = lag_accumulator[(control, lag)]
            weights = np.asarray([item[0] for item in values])
            errors = np.asarray([item[1] for item in values])
            lag_rows.append(
                {
                    "control": control,
                    "lag": lag,
                    "events": len(values),
                    "weight": float(np.sum(weights)),
                    "best_error": float(np.sum(weights * errors) / np.sum(weights)),
                }
            )

    mode_rows: list[dict[str, object]] = []
    for split in SPLITS:
        split_total = sum(
            weight
            for (row_split, _, _), weight in mode_weights.items()
            if row_split == split
        )
        for flip in FLIP_NAMES:
            for axis in ("x", "y", "z"):
                weight = mode_weights[(split, flip, axis)]
                mode_rows.append(
                    {
                        "split": split,
                        "q28_source_flip": flip,
                        "residual_dominant_axis": axis,
                        "weight": weight,
                        "weight_share": weight / split_total,
                    }
                )

    event_sample_fields = (
        "split",
        "branch_label",
        "seed",
        "time",
        "origin_time",
        "source_pair",
        "endpoint",
        "weight",
        "q28_fit_error",
        "residual_fraction",
        "residual_component_entropy",
        "residual_largest_axis_share",
        "residual_effective_dimension",
        "residual_z_scaled",
        "residual_z_ara",
        "residual_dominant_axis",
        "q28_source_flip",
        "child_weight_entropy",
        "strongest_child_weight_share",
        "positive_child_count",
        "origin_exact_error",
        "origin_seed_error",
        "origin_time_error",
        "origin_exact_pair",
        "origin_exact_flip",
        "origin_exact_is_local",
        "origin_exact_is_strongest_child",
        "origin_exact_shares_endpoint",
        "origin_exact_is_active",
        "optimal_exact_error",
        "optimal_exact_lag",
        "optimal_exact_pair",
        "optimal_exact_flip",
        "path_partner_persistence",
        "path_flip_persistence",
        "path_adjacency_share",
        "path_self_return",
    )
    event_sample_rows = []
    for row in event_rows:
        sample_key = (
            107 * int(row["seed"])
            + 67 * int(row["time"])
            + 43 * int(row["source_pair_index"])
            + 31 * int(row["endpoint"])
            + 19 * int(row["branch"])
        )
        if sample_key % 32 != 0:
            continue
        converted = {field: row[field] for field in event_sample_fields}
        converted["residual_dominant_axis"] = ("x", "y", "z")[
            int(converted["residual_dominant_axis"])
        ]
        converted["q28_source_flip"] = FLIP_NAMES[
            int(converted["q28_source_flip"])
        ]
        converted["origin_exact_pair"] = (
            f"{PAIRS[int(converted['origin_exact_pair'])][0]}-"
            f"{PAIRS[int(converted['origin_exact_pair'])][1]}"
        )
        converted["origin_exact_flip"] = FLIP_NAMES[
            int(converted["origin_exact_flip"])
        ]
        converted["optimal_exact_pair"] = (
            f"{PAIRS[int(converted['optimal_exact_pair'])][0]}-"
            f"{PAIRS[int(converted['optimal_exact_pair'])][1]}"
        )
        converted["optimal_exact_flip"] = FLIP_NAMES[
            int(converted["optimal_exact_flip"])
        ]
        event_sample_rows.append(converted)

    exact_origin_advantage_seed = (
        float(pooled["origin_seed_error"]) - float(pooled["origin_exact_error"])
    ) / float(pooled["origin_seed_error"])
    exact_origin_advantage_time = (
        float(pooled["origin_time_error"]) - float(pooled["origin_exact_error"])
    ) / float(pooled["origin_time_error"])
    local_advantage_seed = float(pooled["origin_exact_is_local"]) - float(
        pooled["origin_seed_is_local"]
    )
    local_advantage_time = float(pooled["origin_exact_is_local"]) - float(
        pooled["origin_time_is_local"]
    )
    partner_advantage_seed = float(
        pooled["path_partner_persistence"]
    ) - float(pooled["seed_path_partner_persistence"])
    partner_advantage_time = float(
        pooled["path_partner_persistence"]
    ) - float(pooled["time_path_partner_persistence"])
    axis_comparisons = axis_result["comparisons"]
    axis_bootstrap = axis_result["bootstrap_opened_later_half"]
    assert isinstance(axis_comparisons, dict)
    assert isinstance(axis_bootstrap, dict)
    axis_transport_supported = (
        float(axis_comparisons["axis_error_advantage_vs_seed"]) > 0.05
        and float(axis_comparisons["axis_error_advantage_vs_time"]) > 0.05
        and float(axis_bootstrap["exact_error_below_seed"]) >= 0.95
        and float(axis_bootstrap["exact_error_below_time"]) >= 0.95
        and float(
            axis_comparisons["partner_persistence_advantage_vs_seed"]
        )
        > 0.05
        and float(
            axis_comparisons["partner_persistence_advantage_vs_time"]
        )
        > 0.05
    )
    axis_local_memory_supported = (
        float(axis_comparisons["axis_error_advantage_vs_seed"]) > 0.05
        and float(axis_comparisons["axis_error_advantage_vs_time"]) > 0.05
        and float(axis_bootstrap["exact_error_below_seed"]) >= 0.95
        and float(axis_bootstrap["exact_error_below_time"]) >= 0.95
        and float(axis_comparisons["endpoint_share_advantage_vs_seed"]) > 0.05
        and float(axis_comparisons["endpoint_share_advantage_vs_time"]) > 0.05
    )

    if axis_transport_supported:
        descriptive_lean = (
            "SIGNED Z-AXIS TRANSPORT; NOT YET A PHASE-B IDENTIFICATION"
        )
    elif axis_local_memory_supported:
        descriptive_lean = (
            "LOCAL SIGNED Z-AXIS HANDOVER MEMORY; "
            "NO STABLE COUNTERPART DETECTED"
        )
    elif (
        exact_origin_advantage_seed > 0.05
        and exact_origin_advantage_time > 0.05
        and partner_advantage_seed > 0.10
        and partner_advantage_time > 0.10
        and float(pooled["modal_partner_concentration"]) > 0.50
    ):
        descriptive_lean = "COHERENT COUNTERPART"
    elif (
        float(pooled["residual_largest_axis_share"]) > 0.90
        and local_advantage_seed > 0.20
        and local_advantage_time > 0.20
        and float(pooled["positive_child_count"]) <= 1.05
    ):
        descriptive_lean = (
            "LOCAL Z-AXIS CHILD-HANDOVER CORRECTION; "
            "NO COHERENT COUNTERPART DETECTED"
        )
    else:
        descriptive_lean = "UNRESOLVED / MIXED"

    result = {
        "test_id": TEST_ID,
        "test_class": (
            "exploratory characterization on the completely opened Q28 source"
        ),
        "date": "2026-07-26",
        "classification_policy": (
            "The component is not called Phase B. Descriptive lean compares "
            "shape transport, local-child landing, partner concentration and "
            "displaced controls."
        ),
        "descriptive_lean": descriptive_lean,
        "pooled": pooled,
        "splits": split_summaries,
        "branches": branch_summaries,
        "comparisons": {
            "origin_shape_advantage_vs_seed": exact_origin_advantage_seed,
            "origin_shape_advantage_vs_time": exact_origin_advantage_time,
            "local_landing_advantage_vs_seed": local_advantage_seed,
            "local_landing_advantage_vs_time": local_advantage_time,
            "path_partner_persistence_advantage_vs_seed": partner_advantage_seed,
            "path_partner_persistence_advantage_vs_time": partner_advantage_time,
        },
        "bootstrap_opened_later_half": bootstrap_results,
        "axis_native_surfer": axis_result,
        "source_checks": {
            "connected_shape": list(connected.shape),
            "maximum_off_diagonal": maximum_off_diagonal,
            "source_hdf5_sha256_expected": SOURCE_SHA256,
            "q27_cache_sha256": sha256(Q27_CACHE),
            "q28_connected_cache_sha256": sha256(CONNECTED_CACHE),
        },
        "sampling": {
            "q28_event_sampler": (
                "(97*seed + 53*time + 31*pair + 17*endpoint + 11*branch) mod 16 = 0"
            ),
            "q29_development_subsample": (
                "(89*seed + 47*time + 23*pair + 13*endpoint + 7*branch) mod 4 = 0"
            ),
            "q28_lag": Q28_LAG,
            "surf_lags": list(SURF_LAGS),
        },
        "boundary": (
            "This source is already fully opened, simulated, and exactly "
            "diagonal. Q29 characterizes a mathematical remainder and its "
            "route through this lattice. It does not establish a hidden "
            "physical wave, Phase B, hardware behavior or universal ARA law."
        ),
    }

    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_csv(TRIALS, trial_rows)
    write_csv(LAG_CURVE, lag_rows)
    write_csv(EVENT_SAMPLE, event_sample_rows)
    write_csv(ROUTE_SAMPLE, route_sample_rows)
    write_csv(MODES, mode_rows)
    write_csv(AXIS_TRIALS, axis_trial_rows)
    write_csv(AXIS_LAG_CURVE, axis_lag_rows)
    write_csv(AXIS_ROUTE_SAMPLE, axis_route_sample_rows)
    make_figure(event_rows, lag_rows, pooled)
    make_axis_figure(event_rows, axis_result, axis_lag_rows)
    if not quiet:
        print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress progress and final JSON (useful for background runs)",
    )
    args = parser.parse_args()
    analyse(quiet=args.quiet)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        ERROR_LOG.write_text(traceback.format_exc(), encoding="utf-8")
        raise

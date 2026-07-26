"""Q28: frozen ARA^9 interlocking rotational transport test.

The source was fully opened by Q27. Q28's full-matrix rotation, lag, controls
and gates were checksum-frozen before this script calculated any Q28 outcome.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Iterable


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / ".q27_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import h5py
import numpy as np


TEST_ID = "Q28-ARA9-INTERLOCKING-ROTATIONAL-TRANSPORT-v1"
PROTOCOL_SHA256 = "400789b6ccfa22962d6860b23c379fada7ca00684346bab19daa8fbd88481d14"
SOURCE_SHA256 = "0e10afb6e5c7bcc3b469a9bb18a9bcae9469bfae165d5da5add93eeeb1972eeb"
SOURCE_DIR = HERE / "public_data" / "q27_network_reconstruction"
SOURCE = SOURCE_DIR / "unnati_submit_12_pure_random.hdf5"
Q27_CACHE = SOURCE_DIR / "q27_derived_cache.npz"
CONNECTED_CACHE = SOURCE_DIR / "q28_connected_cache.npy"

RESULTS = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_RESULTS.json"
TRIALS = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_TRIALS.csv"
LAG_CURVE = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_LAG_CURVE.csv"
EVENT_SAMPLE = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_EVENT_SAMPLE.csv"
WORKED = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_WORKED_TRAJECTORY.csv"
FIGURE_PNG = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_GEOMETRY.png"
FIGURE_SVG = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_GEOMETRY.svg"

BRANCHES = ("c2_2local connectivity", "c4_2local connectivity")
BRANCH_LABELS = ("c2", "c4")
PAIRS = tuple((i, j) for i in range(12) for j in range(i + 1, 12))
PAIR_TO_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
PAIR_NAMES = tuple(str(pair) for pair in PAIRS)

I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
PAULI = (X, Y, Z)
A_OPS = np.stack([np.kron(p, I2) for p in PAULI])
B_OPS = np.stack([np.kron(I2, p) for p in PAULI])
T_OPS = np.stack([np.kron(p, q) for p in PAULI for q in PAULI])
OPS = np.concatenate((A_OPS, B_OPS, T_OPS), axis=0)

EPS = 1e-12
BOOTSTRAP_DRAWS = 2000
RNG_SEED = 28028
DEVELOPMENT_STARTS = range(0, 242)
HIDDEN_STARTS = range(250, 492)
LAGS = tuple(range(1, 9))


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def density_batch_to_connected(rhos: np.ndarray) -> np.ndarray:
    expectations = np.einsum("nij,kji->nk", rhos, OPS, optimize=True).real
    a = expectations[:, 0:3]
    b = expectations[:, 3:6]
    tensor = expectations[:, 6:15].reshape(-1, 3, 3)
    return (tensor - a[:, :, None] * b[:, None, :]).astype(np.float32)


def process_trial(branch_index: int, seed: int) -> tuple[int, int, np.ndarray]:
    branch = BRANCHES[branch_index]
    path = (
        f"/12 qubits/{branch}/unitary energy subspace 1/"
        f"unitary seed {seed}/ordering seed random/two_qubit_dms"
    )
    connected = np.empty((500, 66, 3, 3), dtype=np.float32)
    with h5py.File(SOURCE, "r") as handle:
        root = handle[path]
        for time_index in range(500):
            group = root[str(time_index)]
            rhos = np.stack([group[name][()] for name in PAIR_NAMES])
            connected[time_index] = density_batch_to_connected(rhos)
    return branch_index, seed, connected


def extract_connected_cache(workers: int) -> None:
    if sha256(SOURCE) != SOURCE_SHA256:
        raise RuntimeError("Q28 source HDF5 SHA-256 mismatch")
    CONNECTED_CACHE.parent.mkdir(parents=True, exist_ok=True)
    cache = np.lib.format.open_memmap(
        CONNECTED_CACHE,
        mode="w+",
        dtype=np.float32,
        shape=(2, 100, 500, 66, 3, 3),
    )
    jobs = [(branch, seed) for branch in range(2) for seed in range(100)]
    completed = 0
    with ProcessPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {
            executor.submit(process_trial, branch, seed): (branch, seed)
            for branch, seed in jobs
        }
        for future in as_completed(futures):
            branch, seed, connected = future.result()
            cache[branch, seed] = connected
            completed += 1
            if completed % 10 == 0 or completed == len(jobs):
                print(f"Q28 connected matrices {completed}/{len(jobs)}", flush=True)
    cache.flush()
    print(f"wrote {CONNECTED_CACHE} ({CONNECTED_CACHE.stat().st_size} bytes)")


def orient(matrix: np.ndarray, pair_index: int, endpoint: int) -> np.ndarray:
    pair = PAIRS[pair_index]
    if pair[0] == endpoint:
        return matrix
    if pair[1] == endpoint:
        return matrix.T
    raise ValueError(f"endpoint {endpoint} is not in pair {pair}")


def other_endpoint(pair_index: int, endpoint: int) -> int:
    left, right = PAIRS[pair_index]
    if endpoint == left:
        return right
    if endpoint == right:
        return left
    raise ValueError(f"endpoint {endpoint} is not in pair {(left, right)}")


def active_pair_indices(edge_row: np.ndarray) -> list[int]:
    active: list[int] = []
    for raw_u, raw_v in edge_row:
        pair = tuple(sorted((int(raw_u), int(raw_v))))
        if pair in PAIR_TO_INDEX:
            active.append(PAIR_TO_INDEX[pair])
    return active


def sampled(branch: int, seed: int, time: int, pair_index: int, endpoint: int) -> bool:
    value = 97 * seed + 53 * time + 31 * pair_index + 17 * endpoint + 11 * branch
    return value % 16 == 0


def proper_rotation_fit(source: np.ndarray, target: np.ndarray) -> tuple[float, float, float]:
    source_norm_sq = float(np.sum(source * source))
    target_norm = float(np.linalg.norm(target))
    if source_norm_sq <= EPS or target_norm <= EPS:
        return math.nan, math.nan, math.nan

    alpha_zero = max(0.0, float(np.sum(target * source)) / source_norm_sq)
    no_rotation_error = float(
        np.linalg.norm(target - alpha_zero * source) / target_norm
    )

    cross = target @ source.T
    u, _, vh = np.linalg.svd(cross, full_matrices=False)
    correction = np.eye(3)
    correction[-1, -1] = 1.0 if np.linalg.det(u @ vh) >= 0 else -1.0
    rotation = u @ correction @ vh
    rotated_source = rotation @ source
    alpha_rotation = max(
        0.0,
        float(np.sum(target * rotated_source)) / source_norm_sq,
    )
    rotation_error = float(
        np.linalg.norm(target - alpha_rotation * rotated_source) / target_norm
    )
    angle = math.acos(
        float(np.clip((np.trace(rotation) - 1.0) / 2.0, -1.0, 1.0))
    )
    return rotation_error, no_rotation_error, angle


def spectrum_similarity(source: np.ndarray, target: np.ndarray) -> float:
    source_singular = np.linalg.svd(source, compute_uv=False)
    target_singular = np.linalg.svd(target, compute_uv=False)
    source_norm = float(np.linalg.norm(source_singular))
    target_norm = float(np.linalg.norm(target_singular))
    if source_norm <= EPS or target_norm <= EPS:
        return math.nan
    return float(
        np.dot(source_singular / source_norm, target_singular / target_norm)
    )


def shifted_state_time(time: int, lag: int, split: str) -> int:
    state_start = 0 if split == "development" else 250
    target_time = time + lag
    return state_start + ((target_time - state_start + 137) % 250)


@dataclass
class EventResult:
    branch: int
    seed: int
    time: int
    pair_index: int
    endpoint: int
    lag: int
    weight: float
    release: float
    accumulation: float
    rotation_error: float
    no_rotation_error: float
    wrong_endpoint_error: float
    seed_error: float
    time_error: float
    lag_zero_error: float
    angle: float
    spectrum_similarity: float
    seed_spectrum_similarity: float
    time_spectrum_similarity: float


def build_web(
    connected: np.ndarray,
    target_seed: int,
    target_time: int,
    target_indices: list[int],
    endpoint: int,
    accumulations: np.ndarray,
    wrong_endpoint: bool = False,
) -> np.ndarray:
    numerator = np.zeros((3, 3), dtype=np.float64)
    total = float(np.sum(accumulations))
    if total <= EPS:
        return numerator
    for target_index, amount in zip(target_indices, accumulations):
        chosen_endpoint = (
            other_endpoint(target_index, endpoint) if wrong_endpoint else endpoint
        )
        numerator += float(amount) * orient(
            connected[target_seed, target_time, target_index],
            target_index,
            chosen_endpoint,
        )
    return numerator / total


def evaluate_events(
    connected_branch: np.ndarray,
    closure_branch: np.ndarray,
    edges_branch: np.ndarray,
    branch: int,
    seed: int,
    starts: Iterable[int],
    split: str,
    lag: int,
    controls: bool,
) -> list[EventResult]:
    connected = connected_branch
    h = closure_branch[seed]
    results: list[EventResult] = []
    displaced_seed = (seed + 37) % 100

    for time in starts:
        active = active_pair_indices(edges_branch[seed, time])
        if not active:
            continue
        for pair_index, pair in enumerate(PAIRS):
            release = max(0.0, float(h[time, pair_index] - h[time + 1, pair_index]))
            if release <= 0:
                continue
            for endpoint in pair:
                if not sampled(branch, seed, time, pair_index, endpoint):
                    continue
                targets = [
                    target
                    for target in active
                    if target != pair_index and endpoint in PAIRS[target]
                ]
                if not targets:
                    continue
                accumulations = np.asarray(
                    [
                        max(
                            0.0,
                            float(h[time + lag, target] - h[time, target]),
                        )
                        for target in targets
                    ],
                    dtype=np.float64,
                )
                accumulation = float(np.sum(accumulations))
                weight = release * accumulation
                if weight <= 0:
                    continue

                source = orient(
                    connected[seed, time, pair_index],
                    pair_index,
                    endpoint,
                ).astype(np.float64)
                target = build_web(
                    connected,
                    seed,
                    time + lag,
                    targets,
                    endpoint,
                    accumulations,
                )
                if (
                    not np.all(np.isfinite(source))
                    or not np.all(np.isfinite(target))
                    or np.linalg.norm(source) <= 1e-8
                    or np.linalg.norm(target) <= 1e-8
                ):
                    continue

                rotation_error, no_rotation_error, angle = proper_rotation_fit(
                    source,
                    target,
                )
                if not controls:
                    results.append(
                        EventResult(
                            branch,
                            seed,
                            time,
                            pair_index,
                            endpoint,
                            lag,
                            weight,
                            release,
                            accumulation,
                            rotation_error,
                            no_rotation_error,
                            math.nan,
                            math.nan,
                            math.nan,
                            math.nan,
                            angle,
                            math.nan,
                            math.nan,
                            math.nan,
                        )
                    )
                    continue

                wrong_source = orient(
                    connected[seed, time, pair_index],
                    pair_index,
                    other_endpoint(pair_index, endpoint),
                ).astype(np.float64)
                wrong_target = build_web(
                    connected,
                    seed,
                    time + lag,
                    targets,
                    endpoint,
                    accumulations,
                    wrong_endpoint=True,
                )
                wrong_error = proper_rotation_fit(wrong_source, wrong_target)[0]

                seed_target = build_web(
                    connected,
                    displaced_seed,
                    time + lag,
                    targets,
                    endpoint,
                    accumulations,
                )
                seed_error = proper_rotation_fit(source, seed_target)[0]

                time_target = build_web(
                    connected,
                    seed,
                    shifted_state_time(time, lag, split),
                    targets,
                    endpoint,
                    accumulations,
                )
                time_error = proper_rotation_fit(source, time_target)[0]

                lag_zero_target = build_web(
                    connected,
                    seed,
                    time,
                    targets,
                    endpoint,
                    accumulations,
                )
                lag_zero_error = proper_rotation_fit(source, lag_zero_target)[0]

                results.append(
                    EventResult(
                        branch,
                        seed,
                        time,
                        pair_index,
                        endpoint,
                        lag,
                        weight,
                        release,
                        accumulation,
                        rotation_error,
                        no_rotation_error,
                        wrong_error,
                        seed_error,
                        time_error,
                        lag_zero_error,
                        angle,
                        spectrum_similarity(source, target),
                        spectrum_similarity(source, seed_target),
                        spectrum_similarity(source, time_target),
                    )
                )
    return results


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    finite = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not np.any(finite):
        return math.nan
    return float(np.average(values[finite], weights=weights[finite]))


def weighted_quantile(
    values: np.ndarray,
    weights: np.ndarray,
    quantiles: Iterable[float],
) -> np.ndarray:
    finite = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not np.any(finite):
        return np.full(len(tuple(quantiles)), np.nan)
    selected_values = values[finite]
    selected_weights = weights[finite]
    order = np.argsort(selected_values)
    selected_values = selected_values[order]
    selected_weights = selected_weights[order]
    cumulative = np.cumsum(selected_weights)
    cumulative /= cumulative[-1]
    return np.interp(np.asarray(tuple(quantiles), dtype=float), cumulative, selected_values)


def aggregate_events(events: list[EventResult]) -> dict[str, float | int]:
    if not events:
        return {"events": 0, "weight": 0.0}
    weights = np.asarray([event.weight for event in events])
    rotation = np.asarray([event.rotation_error for event in events])
    no_rotation = np.asarray([event.no_rotation_error for event in events])
    wrong = np.asarray([event.wrong_endpoint_error for event in events])
    seed = np.asarray([event.seed_error for event in events])
    time = np.asarray([event.time_error for event in events])
    lag_zero = np.asarray([event.lag_zero_error for event in events])
    angles = np.asarray([event.angle for event in events])
    shape = np.asarray([event.spectrum_similarity for event in events])
    seed_shape = np.asarray([event.seed_spectrum_similarity for event in events])
    time_shape = np.asarray([event.time_spectrum_similarity for event in events])
    angle_q = weighted_quantile(angles, weights, (0.25, 0.5, 0.75))
    rotation_mean = weighted_mean(rotation, weights)
    no_rotation_mean = weighted_mean(no_rotation, weights)
    return {
        "events": len(events),
        "weight": float(np.sum(weights)),
        "rotation_error": rotation_mean,
        "no_rotation_error": no_rotation_mean,
        "rotation_gain": (
            (no_rotation_mean - rotation_mean) / no_rotation_mean
            if no_rotation_mean > EPS
            else math.nan
        ),
        "wrong_endpoint_error": weighted_mean(wrong, weights),
        "seed_error": weighted_mean(seed, weights),
        "time_error": weighted_mean(time, weights),
        "lag_zero_error": weighted_mean(lag_zero, weights),
        "angle_q25_rad": float(angle_q[0]),
        "angle_median_rad": float(angle_q[1]),
        "angle_q75_rad": float(angle_q[2]),
        "spectrum_similarity": weighted_mean(shape, weights),
        "seed_spectrum_similarity": weighted_mean(seed_shape, weights),
        "time_spectrum_similarity": weighted_mean(time_shape, weights),
        "sum_rotation": float(np.nansum(weights * rotation)),
        "sum_no_rotation": float(np.nansum(weights * no_rotation)),
        "sum_wrong": float(np.nansum(weights * wrong)),
        "sum_seed": float(np.nansum(weights * seed)),
        "sum_time": float(np.nansum(weights * time)),
        "sum_lag_zero": float(np.nansum(weights * lag_zero)),
    }


def write_csv(path: pathlib.Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def pooled_trial_metric(
    rows: list[dict[str, object]],
    indices: np.ndarray,
    field: str,
) -> float:
    weight = sum(float(rows[int(index)]["weight"]) for index in indices)
    if weight <= EPS:
        return math.nan
    return sum(float(rows[int(index)][field]) for index in indices) / weight


def bootstrap_probabilities(
    trial_rows: list[dict[str, object]],
    rng: np.random.Generator,
) -> dict[str, float]:
    probabilities = {
        "rotation_beats_no_rotation": 0,
        "shared_beats_wrong_endpoint": 0,
        "exact_beats_seed_displacement": 0,
        "exact_beats_time_displacement": 0,
        "positive_lag_beats_lag_zero": 0,
    }
    count = len(trial_rows)
    for _ in range(BOOTSTRAP_DRAWS):
        sample = rng.integers(0, count, size=count)
        exact = pooled_trial_metric(trial_rows, sample, "sum_rotation")
        comparisons = {
            "rotation_beats_no_rotation": pooled_trial_metric(
                trial_rows, sample, "sum_no_rotation"
            ),
            "shared_beats_wrong_endpoint": pooled_trial_metric(
                trial_rows, sample, "sum_wrong"
            ),
            "exact_beats_seed_displacement": pooled_trial_metric(
                trial_rows, sample, "sum_seed"
            ),
            "exact_beats_time_displacement": pooled_trial_metric(
                trial_rows, sample, "sum_time"
            ),
            "positive_lag_beats_lag_zero": pooled_trial_metric(
                trial_rows, sample, "sum_lag_zero"
            ),
        }
        for name, control in comparisons.items():
            probabilities[name] += int(exact < control)
    return {name: value / BOOTSTRAP_DRAWS for name, value in probabilities.items()}


def branch_summary(
    events: list[EventResult],
    branch: int | None,
) -> dict[str, float | int]:
    selected = events if branch is None else [event for event in events if event.branch == branch]
    summary = aggregate_events(selected)
    summary["stratum"] = "pooled" if branch is None else BRANCH_LABELS[branch]
    summary["trials"] = len({(event.branch, event.seed) for event in selected})
    return summary


def trial_rows_for(
    events: list[EventResult],
    split: str,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for branch in range(2):
        for seed in range(100):
            selected = [
                event
                for event in events
                if event.branch == branch and event.seed == seed
            ]
            summary = aggregate_events(selected)
            rows.append(
                {
                    "split": split,
                    "branch": BRANCH_LABELS[branch],
                    "branch_index": branch,
                    "seed": seed,
                    **summary,
                }
            )
    return rows


def angle_histogram(events: list[EventResult]) -> dict[str, list[float]]:
    bins = np.linspace(0, math.pi, 37)
    values = np.asarray([event.angle for event in events])
    weights = np.asarray([event.weight for event in events])
    hist, _ = np.histogram(values, bins=bins, weights=weights)
    if hist.sum() > 0:
        hist = hist / hist.sum()
    return {
        "bin_edges_deg": np.degrees(bins).tolist(),
        "weight_fraction": hist.tolist(),
    }


def worked_trajectory(
    connected: np.ndarray,
    closure: np.ndarray,
    edges: np.ndarray,
    event: EventResult,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    branch = event.branch
    seed = event.seed
    pair_index = event.pair_index
    endpoint = event.endpoint
    lag = event.lag
    h = closure[branch, seed]
    for time in DEVELOPMENT_STARTS:
        active = active_pair_indices(edges[branch, seed, time])
        targets = [
            target
            for target in active
            if target != pair_index and endpoint in PAIRS[target]
        ]
        if not targets:
            continue
        accumulations = np.asarray(
            [
                max(0.0, float(h[time + lag, target] - h[time, target]))
                for target in targets
            ]
        )
        accumulation = float(np.sum(accumulations))
        release = max(0.0, float(h[time, pair_index] - h[time + 1, pair_index]))
        if accumulation <= 0:
            angle = math.nan
            rotation_error = math.nan
        else:
            source = orient(
                connected[branch, seed, time, pair_index],
                pair_index,
                endpoint,
            ).astype(np.float64)
            target = build_web(
                connected[branch],
                seed,
                time + lag,
                targets,
                endpoint,
                accumulations,
            )
            rotation_error, _, angle = proper_rotation_fit(source, target)
        rows.append(
            {
                "branch": BRANCH_LABELS[branch],
                "seed": seed,
                "source_pair": str(PAIRS[pair_index]),
                "endpoint": endpoint,
                "time": time,
                "lag": lag,
                "source_closure": float(h[time, pair_index]),
                "release": release,
                "target_accumulation": accumulation,
                "angle_deg": math.degrees(angle) if math.isfinite(angle) else "",
                "rotation_error": rotation_error if math.isfinite(rotation_error) else "",
            }
        )
    return rows


def create_figure(
    result: dict[str, object],
    event_sample: list[dict[str, object]],
    worked_rows: list[dict[str, object]],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.edgecolor": "#334155",
            "axes.labelcolor": "#1f2937",
            "xtick.color": "#475569",
            "ytick.color": "#475569",
            "axes.titleweight": "bold",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(14, 9.5), constrained_layout=True)
    fig.suptitle(
        "Q28 ARA⁹ interlocking rotational transport",
        fontsize=18,
        fontweight="bold",
    )

    hidden = result["hidden"]["pooled"]
    labels = ["shared\nrotation", "no\nrotation", "wrong\nendpoint", "seed\nshift", "time\nshift"]
    values = [
        hidden["rotation_error"],
        hidden["no_rotation_error"],
        hidden["wrong_endpoint_error"],
        hidden["seed_error"],
        hidden["time_error"],
    ]
    axes[0, 0].bar(
        np.arange(5),
        values,
        color=["#3b82f6", "#94a3b8", "#d49a3a", "#e7b96a", "#cbd5e1"],
        edgecolor="#334155",
        linewidth=0.7,
    )
    axes[0, 0].set_xticks(np.arange(5), labels)
    axes[0, 0].set_ylabel("weighted normalized residual")
    axes[0, 0].set_title("Hidden reconstruction residuals")

    lag_rows = result["lag_curve"]
    development = [row for row in lag_rows if row["split"] == "development"]
    hidden_lags = [row for row in lag_rows if row["split"] == "hidden"]
    axes[0, 1].plot(
        [row["lag"] for row in development],
        [row["rotation_error"] for row in development],
        color="#3b82f6",
        marker="o",
        label="development",
    )
    axes[0, 1].plot(
        [row["lag"] for row in hidden_lags],
        [row["rotation_error"] for row in hidden_lags],
        color="#d49a3a",
        marker="s",
        linestyle="--",
        label="hidden",
    )
    axes[0, 1].axvline(
        result["selected_lag"],
        color="#334155",
        linestyle=":",
        label=f"frozen lag {result['selected_lag']}",
    )
    axes[0, 1].set_xlabel("lag (time steps)")
    axes[0, 1].set_ylabel("weighted rotation residual")
    axes[0, 1].set_title("Rotation residual by lag")
    axes[0, 1].legend(frameon=False)

    development_angles = [
        float(row["angle_deg"])
        for row in event_sample
        if row["split"] == "development"
    ]
    hidden_angles = [
        float(row["angle_deg"])
        for row in event_sample
        if row["split"] == "hidden"
    ]
    bins = np.linspace(0, 180, 37)
    axes[1, 0].hist(
        development_angles,
        bins=bins,
        density=True,
        color="#3b82f6",
        alpha=0.45,
        edgecolor="#334155",
        label="development sample",
    )
    axes[1, 0].hist(
        hidden_angles,
        bins=bins,
        density=True,
        histtype="step",
        color="#d49a3a",
        linewidth=2,
        label="hidden sample",
    )
    axes[1, 0].set_xlabel("proper shared-point rotation angle (degrees)")
    axes[1, 0].set_ylabel("density")
    axes[1, 0].set_title("Fitted angle distributions")
    axes[1, 0].legend(frameon=False)

    worked_time = np.asarray([int(row["time"]) for row in worked_rows])
    release = np.asarray([float(row["release"]) for row in worked_rows])
    accumulation = np.asarray([float(row["target_accumulation"]) for row in worked_rows])
    angle = np.asarray(
        [
            float(row["angle_deg"]) if row["angle_deg"] != "" else np.nan
            for row in worked_rows
        ]
    )
    if np.max(release) > 0:
        release = release / np.max(release)
    if np.max(accumulation) > 0:
        accumulation = accumulation / np.max(accumulation)
    axes[1, 1].plot(worked_time, release, color="#3b82f6", label="source release")
    axes[1, 1].plot(
        worked_time,
        accumulation,
        color="#d49a3a",
        linestyle="--",
        label="neighbour accumulation",
    )
    axes[1, 1].set_xlabel("development time")
    axes[1, 1].set_ylabel("normalized radial movement")
    angle_axis = axes[1, 1].twinx()
    angle_axis.plot(
        worked_time,
        angle,
        color="#334155",
        alpha=0.55,
        linewidth=1,
        label="fitted angle",
    )
    angle_axis.set_ylabel("angle (degrees)", color="#334155")
    axes[1, 1].set_title("Worked source and active-neighbour web")
    lines, labels_left = axes[1, 1].get_legend_handles_labels()
    lines_right, labels_right = angle_axis.get_legend_handles_labels()
    axes[1, 1].legend(lines + lines_right, labels_left + labels_right, frameon=False)

    fig.savefig(FIGURE_PNG, dpi=180)
    fig.savefig(FIGURE_SVG)
    plt.close(fig)


def analyse() -> None:
    protocol = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_PROTOCOL_v1_FROZEN.md"
    if sha256(protocol) != PROTOCOL_SHA256:
        raise RuntimeError("Frozen Q28 protocol checksum mismatch")
    if sha256(SOURCE) != SOURCE_SHA256:
        raise RuntimeError("Q28 source HDF5 checksum mismatch")
    if not CONNECTED_CACHE.exists() or not Q27_CACHE.exists():
        raise FileNotFoundError("Run Q28 extract stage and retain the Q27 cache")

    connected = np.load(CONNECTED_CACHE, mmap_mode="r")
    q27 = np.load(Q27_CACHE, allow_pickle=False)
    closure = np.asarray(q27["closure"], dtype=np.float32)
    edges = np.asarray(q27["edges"], dtype=np.int8)
    qc = np.asarray(q27["qc"], dtype=np.float64)
    if connected.shape != (2, 100, 500, 66, 3, 3):
        raise RuntimeError(f"Unexpected connected cache shape: {connected.shape}")

    lag_rows: list[dict[str, object]] = []
    development_events_by_lag: dict[int, list[EventResult]] = {}
    for lag in LAGS:
        all_events: list[EventResult] = []
        for branch in range(2):
            for seed in range(100):
                all_events.extend(
                    evaluate_events(
                        connected[branch],
                        closure[branch],
                        edges[branch],
                        branch,
                        seed,
                        DEVELOPMENT_STARTS,
                        "development",
                        lag,
                        controls=False,
                    )
                )
        development_events_by_lag[lag] = all_events
        summary = aggregate_events(all_events)
        lag_rows.append(
            {
                "split": "development",
                "lag": lag,
                "events": summary["events"],
                "rotation_error": summary["rotation_error"],
            }
        )
        print(
            f"development lag {lag}: {summary['events']} events, "
            f"residual {summary['rotation_error']:.6f}",
            flush=True,
        )

    selected_lag = min(
        LAGS,
        key=lambda lag: (
            float(aggregate_events(development_events_by_lag[lag])["rotation_error"]),
            lag,
        ),
    )
    print(f"frozen development-selected lag: {selected_lag}", flush=True)

    development_events: list[EventResult] = []
    hidden_events: list[EventResult] = []
    for branch in range(2):
        for seed in range(100):
            development_events.extend(
                evaluate_events(
                    connected[branch],
                    closure[branch],
                    edges[branch],
                    branch,
                    seed,
                    DEVELOPMENT_STARTS,
                    "development",
                    selected_lag,
                    controls=True,
                )
            )
            hidden_events.extend(
                evaluate_events(
                    connected[branch],
                    closure[branch],
                    edges[branch],
                    branch,
                    seed,
                    HIDDEN_STARTS,
                    "hidden",
                    selected_lag,
                    controls=True,
                )
            )
        print(f"selected-lag controls complete for {BRANCH_LABELS[branch]}", flush=True)

    for lag in LAGS:
        hidden_lag_events: list[EventResult] = []
        for branch in range(2):
            for seed in range(100):
                hidden_lag_events.extend(
                    evaluate_events(
                        connected[branch],
                        closure[branch],
                        edges[branch],
                        branch,
                        seed,
                        HIDDEN_STARTS,
                        "hidden",
                        lag,
                        controls=False,
                    )
                )
        summary = aggregate_events(hidden_lag_events)
        lag_rows.append(
            {
                "split": "hidden",
                "lag": lag,
                "events": summary["events"],
                "rotation_error": summary["rotation_error"],
            }
        )
        print(
            f"hidden lag {lag}: {summary['events']} events, "
            f"residual {summary['rotation_error']:.6f}",
            flush=True,
        )

    development_summaries = {
        "c2": branch_summary(development_events, 0),
        "c4": branch_summary(development_events, 1),
        "pooled": branch_summary(development_events, None),
    }
    hidden_summaries = {
        "c2": branch_summary(hidden_events, 0),
        "c4": branch_summary(hidden_events, 1),
        "pooled": branch_summary(hidden_events, None),
    }

    development_angles = np.asarray([event.angle for event in development_events])
    development_weights = np.asarray([event.weight for event in development_events])
    dev_q25, dev_median, dev_q75 = weighted_quantile(
        development_angles,
        development_weights,
        (0.25, 0.5, 0.75),
    )
    hidden_angles = np.asarray([event.angle for event in hidden_events])
    hidden_weights = np.asarray([event.weight for event in hidden_events])
    hidden_median = weighted_quantile(hidden_angles, hidden_weights, (0.5,))[0]
    inside = (
        (hidden_angles >= dev_q25)
        & (hidden_angles <= dev_q75)
        & np.isfinite(hidden_angles)
    )
    hidden_inside_iqr = float(
        np.sum(hidden_weights[inside]) / np.sum(hidden_weights)
    )

    trial_rows = (
        trial_rows_for(development_events, "development")
        + trial_rows_for(hidden_events, "hidden")
    )
    hidden_trial_rows = [row for row in trial_rows if row["split"] == "hidden"]
    bootstrap = bootstrap_probabilities(
        hidden_trial_rows,
        np.random.default_rng(RNG_SEED),
    )

    pooled = hidden_summaries["pooled"]
    correct_vs_wrong = (
        (float(pooled["wrong_endpoint_error"]) - float(pooled["rotation_error"]))
        / float(pooled["wrong_endpoint_error"])
    )
    positive_vs_zero = (
        (float(pooled["lag_zero_error"]) - float(pooled["rotation_error"]))
        / float(pooled["lag_zero_error"])
    )
    branch_directions = {}
    for label in ("c2", "c4"):
        row = hidden_summaries[label]
        branch_directions[label] = {
            "I1_rotation_gain_positive": float(row["rotation_gain"]) >= 0.10,
            "I3_shared_better": float(row["rotation_error"])
            < float(row["wrong_endpoint_error"]),
            "I4_seed_better": float(row["rotation_error"]) < float(row["seed_error"]),
            "I4_time_better": float(row["rotation_error"]) < float(row["time_error"]),
            "T1_lag_better": float(row["rotation_error"])
            < float(row["lag_zero_error"]),
        }
    same_direction = all(
        all(values.values()) for values in branch_directions.values()
    )

    data_gates = {
        "D1_source_checksums": True,
        "D2_complete_branches_trials_pairs": (
            connected.shape == (2, 100, 500, 66, 3, 3)
        ),
        "D3_known_source_precision": (
            float(np.max(qc[:, :, 0])) <= 5e-5
            and float(np.max(qc[:, :, 1])) <= 1e-6
            and float(np.min(qc[:, :, 2])) >= -1e-6
        ),
        "E1_eligibility": (
            int(pooled["trials"]) >= 100 and int(pooled["events"]) >= 100_000
        ),
    }
    interlocking_gates = {
        "I1_rotation_gain_10pct": float(pooled["rotation_gain"]) >= 0.10,
        "I2_bootstrap_rotation_beats_no_rotation": (
            bootstrap["rotation_beats_no_rotation"] >= 0.95
        ),
        "I3_shared_endpoint_5pct_and_bootstrap": (
            correct_vs_wrong >= 0.05
            and bootstrap["shared_beats_wrong_endpoint"] >= 0.95
        ),
        "I4_displaced_controls": (
            bootstrap["exact_beats_seed_displacement"] >= 0.95
            and bootstrap["exact_beats_time_displacement"] >= 0.95
        ),
        "I5_shape_similarity": (
            float(pooled["spectrum_similarity"]) >= 0.90
            and float(pooled["spectrum_similarity"])
            > float(pooled["seed_spectrum_similarity"])
            and float(pooled["spectrum_similarity"])
            > float(pooled["time_spectrum_similarity"])
        ),
    }
    traveling_gates = {
        "T1_positive_lag_5pct_and_bootstrap": (
            positive_vs_zero >= 0.05
            and bootstrap["positive_lag_beats_lag_zero"] >= 0.95
        ),
        "T2_angle_within_15deg": (
            abs(math.degrees(hidden_median - dev_median)) <= 15.0
        ),
        "T3_half_weight_inside_development_iqr": hidden_inside_iqr >= 0.50,
        "T4_same_direction_both_strata": same_direction,
    }
    data_pass = all(data_gates.values())
    interlocking_supported = data_pass and all(interlocking_gates.values())
    traveling_supported = data_pass and all(traveling_gates.values())
    if not data_pass:
        verdict = "INCONCLUSIVE"
    elif interlocking_supported and traveling_supported:
        verdict = "COMBINED SUPPORTED"
    elif interlocking_supported:
        verdict = "PARTIAL - INTERLOCKING ROTATION SUPPORTED"
    elif traveling_supported:
        verdict = "PARTIAL - TRAVELING ANGLED WAVE SUPPORTED"
    else:
        verdict = "NOT SUPPORTED"

    event_sample_rows: list[dict[str, object]] = []
    for split, events in (
        ("development", development_events),
        ("hidden", hidden_events),
    ):
        for event in events:
            sample_key = (
                101 * event.seed
                + 59 * event.time
                + 37 * event.pair_index
                + 19 * event.endpoint
                + 13 * event.branch
            )
            if sample_key % 64 != 0:
                continue
            event_sample_rows.append(
                {
                    "split": split,
                    "branch": BRANCH_LABELS[event.branch],
                    "seed": event.seed,
                    "time": event.time,
                    "source_pair": str(PAIRS[event.pair_index]),
                    "endpoint": event.endpoint,
                    "lag": event.lag,
                    "weight": event.weight,
                    "release": event.release,
                    "accumulation": event.accumulation,
                    "rotation_error": event.rotation_error,
                    "no_rotation_error": event.no_rotation_error,
                    "angle_deg": math.degrees(event.angle),
                    "spectrum_similarity": event.spectrum_similarity,
                }
            )

    strongest = max(development_events, key=lambda event: event.weight)
    worked_rows = worked_trajectory(connected, closure, edges, strongest)

    result = {
        "test_id": TEST_ID,
        "ledger_id": "T284",
        "verdict": verdict,
        "selected_lag": selected_lag,
        "development": development_summaries,
        "hidden": hidden_summaries,
        "angle_transfer": {
            "development_q25_deg": math.degrees(dev_q25),
            "development_median_deg": math.degrees(dev_median),
            "development_q75_deg": math.degrees(dev_q75),
            "hidden_median_deg": math.degrees(hidden_median),
            "median_difference_deg": math.degrees(hidden_median - dev_median),
            "hidden_weight_inside_development_iqr": hidden_inside_iqr,
        },
        "bootstrap": bootstrap,
        "branch_directions": branch_directions,
        "gates": {
            **data_gates,
            **interlocking_gates,
            **traveling_gates,
        },
        "gate_components": {
            "correct_vs_wrong_relative_advantage": correct_vs_wrong,
            "positive_lag_vs_zero_relative_advantage": positive_vs_zero,
        },
        "lag_curve": lag_rows,
        "angle_histograms": {
            "development": angle_histogram(development_events),
            "hidden": angle_histogram(hidden_events),
        },
        "worked_event": {
            "branch": BRANCH_LABELS[strongest.branch],
            "seed": strongest.seed,
            "time": strongest.time,
            "source_pair": str(PAIRS[strongest.pair_index]),
            "endpoint": strongest.endpoint,
            "weight": strongest.weight,
        },
        "source_quality": {
            "maximum_trace_error": float(np.max(qc[:, :, 0])),
            "maximum_hermiticity_error": float(np.max(qc[:, :, 1])),
            "minimum_eigenvalue": float(np.min(qc[:, :, 2])),
        },
        "source": {
            "doi": "10.5281/zenodo.16753415",
            "hdf5_sha256": SOURCE_SHA256,
            "protocol_sha256": PROTOCOL_SHA256,
            "evidence_tier": "registered on fully opened source; not blind",
        },
        "evidence_boundary": (
            "Complete public simulated network data. Q28 tests a frozen "
            "full-matrix ARA transformation after Q27 opened the source; it "
            "does not establish hardware behavior, a new quantum law or "
            "universal fractality."
        ),
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_csv(TRIALS, trial_rows)
    write_csv(LAG_CURVE, lag_rows)
    write_csv(EVENT_SAMPLE, event_sample_rows)
    write_csv(WORKED, worked_rows)
    create_figure(result, event_sample_rows, worked_rows)
    print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "stage",
        choices=("extract", "analyse", "all"),
        nargs="?",
        default="all",
    )
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()

    if args.stage in {"extract", "all"}:
        if not SOURCE.exists():
            from q27_zenodo_download import download, extract

            extract(download())
        extract_connected_cache(args.workers)
    if args.stage in {"analyse", "all"}:
        analyse()


if __name__ == "__main__":
    main()

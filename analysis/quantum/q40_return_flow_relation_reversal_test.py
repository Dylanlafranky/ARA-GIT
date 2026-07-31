"""Q40 prospective conditional return-flow relation-reversal replication."""

from __future__ import annotations

import concurrent.futures
import csv
import gzip
import hashlib
import itertools
import json
import os
import pathlib
import sys
import time
import zipfile
from collections import defaultdict


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / "public_data" / "_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".mplconfig"))

import h5py
import matplotlib.pyplot as plt
import numpy as np


TEST_ID = "Q40-RETURN-FLOW-RELATION-REVERSAL-v1"
DATA = HERE / "public_data" / "q40_return_flow_inhomo_v1_greedy"
ARCHIVE_NAME = "unnati_submit_12_inhomo_v1_greedy.hdf5.zip"
HDF_NAME = "unnati_submit_12_inhomo_v1_greedy.hdf5"
ARCHIVE = DATA / ARCHIVE_NAME
SOURCE = DATA / HDF_NAME
DERIVED = DATA / "q40_derived_cache.npz"
CONNECTED = DATA / "q40_connected_cache.npy"
PREDICTIONS = DATA / "q40_frozen_predictions.npz"
PROTOCOL = HERE / "Q40_RETURN_FLOW_RELATION_REVERSAL_PROTOCOL_v1_PRETARGET_FROZEN.md"
FIDELITY = HERE / "Q40_RETURN_FLOW_RELATION_REVERSAL_FIDELITY_v1.md"
TARGET_LOCK = HERE / "Q40_TARGET_LOCK_v1_FROZEN.md"
RESULTS = HERE / "Q40_RETURN_FLOW_RELATION_REVERSAL_RESULTS.json"
EVENTS = HERE / "Q40_RETURN_FLOW_RELATION_REVERSAL_CYCLES.csv.gz"
FIGURE_PNG = HERE / "Q40_RETURN_FLOW_RELATION_REVERSAL_DIAGNOSTICS.png"
FIGURE_SVG = HERE / "Q40_RETURN_FLOW_RELATION_REVERSAL_DIAGNOSTICS.svg"

ARCHIVE_MD5 = "c04eb02b1766d9f83fb0240689d209a5"
PROTOCOL_SHA256 = "256c13c251bed401efebff8351696d22ab9a0a1d991ca8c4aa142fab620f1c0f"
FIDELITY_SHA256 = "ede891b99a6311ed10e864814389017b70d366f8e95449590e23337a1c821915"
TARGET_LOCK_SHA256 = "e6f8e58d16bfb601a877f646c875b34bfbf59de264954bff0852ce41eef8b74c"
BRANCH = "c2_2local connectivity"
PAIRS = tuple(itertools.combinations(range(12), 2))
PAIR_NAMES = tuple(str(pair) for pair in PAIRS)
METHODS = (
    "q40",
    "forward",
    "persistence",
    "old_identity",
    "linear",
    "mean",
    "wrong_order",
    "whole_sign",
    "persistence_guard",
    "inverted_flag",
    "affine",
)
METHOD_LABELS = {
    "q40": "Q40 relation reversal",
    "forward": "Forward relation",
    "persistence": "Persistence",
    "old_identity": "Old identity",
    "linear": "Linear continuation",
    "mean": "Three-state mean",
    "wrong_order": "Wrong order",
    "whole_sign": "Whole-sign guard",
    "persistence_guard": "Persistence guard",
    "inverted_flag": "Inverted flag",
    "affine": "Development affine",
}
BOOTSTRAP_SEED = 400027
BOOTSTRAP_DRAWS = 20_000
EPS = 1e-12

I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
PAULI = (X, Y, Z)
OPS = np.concatenate(
    (
        np.stack([np.kron(p, I2) for p in PAULI]),
        np.stack([np.kron(I2, p) for p in PAULI]),
        np.stack([np.kron(p, q) for p in PAULI for q in PAULI]),
    ),
    axis=0,
)


def digest(path: pathlib.Path, algorithm: str) -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def ensure_source() -> None:
    if not ARCHIVE.exists() or digest(ARCHIVE, "md5") != ARCHIVE_MD5:
        raise RuntimeError("Frozen Q40 archive is missing or fails deposited MD5")
    if SOURCE.exists():
        return
    with zipfile.ZipFile(ARCHIVE) as zipped:
        matches = [
            item
            for item in zipped.infolist()
            if not item.is_dir() and pathlib.Path(item.filename).name == HDF_NAME
        ]
        if len(matches) != 1:
            raise RuntimeError(f"Expected one {HDF_NAME}, found {len(matches)}")
        with zipped.open(matches[0]) as source, SOURCE.open("wb") as target:
            while chunk := source.read(8 * 1024 * 1024):
                target.write(chunk)


def locate_trial(handle: h5py.File, seed: int) -> str:
    root = handle[
        f"/12 qubits/{BRANCH}/unitary energy subspace 1/unitary seed {seed}"
    ]
    found: list[str] = []

    def visitor(_name: str, obj) -> None:
        if (
            isinstance(obj, h5py.Group)
            and "two_qubit_dms" in obj
            and "previous_order" in obj
        ):
            found.append(obj.name)

    root.visititems(visitor)
    if len(found) != 1:
        raise RuntimeError(f"Unexpected seed schema for {seed}: {found}")
    return found[0]


def density_batch(rhos: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    expectation = np.einsum("nij,kji->nk", rhos, OPS, optimize=True).real
    a, b = expectation[:, :3], expectation[:, 3:6]
    tensor = expectation[:, 6:15].reshape(-1, 3, 3)
    connected = tensor - a[:, :, None] * b[:, None, :]
    closure = np.cbrt(np.abs(np.linalg.det(connected)))
    return closure.astype(np.float32), connected.astype(np.float32)


def process_seed(seed: int):
    closure = np.empty((500, 66), dtype=np.float32)
    connected = np.empty((500, 66, 3, 3), dtype=np.float32)
    qc = np.zeros(4, dtype=np.float64)
    qc[2] = np.inf
    with h5py.File(SOURCE, "r") as handle:
        group = handle[locate_trial(handle, seed)]
        root = group["two_qubit_dms"]
        for time_index in range(500):
            rhos = np.stack(
                [root[str(time_index)][name][()] for name in PAIR_NAMES]
            ).astype(np.complex128)
            closure[time_index], connected[time_index] = density_batch(rhos)
            if time_index in (0, 99, 199, 249, 299, 399, 499):
                for pair in (0, 13, 26, 39, 52, 65):
                    rho = rhos[pair]
                    qc[0] = max(qc[0], float(abs(np.trace(rho) - 1)))
                    qc[1] = max(qc[1], float(np.max(abs(rho - rho.conj().T))))
                    qc[2] = min(
                        qc[2],
                        float(np.min(np.linalg.eigvalsh((rho + rho.conj().T) / 2))),
                    )
                    qc[3] += 1
    return seed, closure, connected, qc


def build_caches(workers: int = 8) -> None:
    ensure_source()
    if DERIVED.exists() and CONNECTED.exists():
        print("using existing Q40 caches", flush=True)
        return
    DATA.mkdir(parents=True, exist_ok=True)
    closure = np.empty((100, 500, 66), dtype=np.float32)
    qc = np.empty((100, 4), dtype=np.float64)
    connected = np.lib.format.open_memmap(
        CONNECTED,
        mode="w+",
        dtype=np.float32,
        shape=(100, 500, 66, 3, 3),
    )
    started = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(process_seed, seed) for seed in range(100)]
        for completed, future in enumerate(
            concurrent.futures.as_completed(futures), start=1
        ):
            seed, h, c, q = future.result()
            closure[seed], connected[seed], qc[seed] = h, c, q
            if completed % 5 == 0 or completed == 100:
                print(
                    f"cached {completed}/100 seeds ({time.time() - started:.1f}s)",
                    flush=True,
                )
    connected.flush()
    np.savez_compressed(
        DERIVED,
        closure=closure,
        qc=qc,
        pairs=np.asarray(PAIRS, dtype=np.int8),
        branch=np.asarray(BRANCH),
    )


def quadrant_labels(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    labels = np.empty(u.shape, dtype=np.int8)
    labels[(u >= 0) & (v >= 0)] = 0
    labels[(u < 0) & (v >= 0)] = 1
    labels[(u < 0) & (v < 0)] = 2
    labels[(u >= 0) & (v < 0)] = 3
    return labels


def coordinates(line: np.ndarray):
    development = np.asarray(line[:250], dtype=np.float64)
    flow = np.diff(development)
    lo, hi = np.quantile(development, [0.05, 0.95])
    centre, radius = (lo + hi) / 2, (hi - lo) / 2
    scale = float(np.quantile(np.abs(flow), 0.95))
    if (
        not np.isfinite(radius)
        or not np.isfinite(scale)
        or radius <= EPS
        or scale <= EPS
    ):
        return None
    u = (np.asarray(line[:-1], dtype=np.float64) - centre) / radius
    v = np.diff(np.asarray(line, dtype=np.float64)) / scale
    labels = quadrant_labels(u, v)
    dev_plane = u[:249] + 1j * v[:249]
    finite = np.isfinite(dev_plane.real) & np.isfinite(dev_plane.imag)
    if np.mean(finite) < 0.95:
        return None
    valid = dev_plane[finite]
    turn = np.angle(np.conj(valid[:-1]) * valid[1:])
    turn = turn[np.isfinite(turn) & (np.abs(turn) > 1e-10)]
    if not turn.size:
        return None
    signed_turn = float(np.mean(np.sign(turn)))
    direction = 1 if signed_turn >= 0 else -1
    coherence = abs(signed_turn)
    occupancy = min(float(np.mean(labels[:249] == q)) for q in range(4))
    return u, v, labels, direction, coherence, occupancy


def runs(labels: np.ndarray, first: int, last: int):
    selected = np.asarray(labels[first : last + 1], dtype=np.int8)
    output: list[tuple[int, int, int]] = []
    start = 0
    for index in range(1, len(selected) + 1):
        if index == len(selected) or selected[index] != selected[start]:
            output.append((int(selected[start]), first + start, first + index - 1))
            start = index
    return output


def complete_windows(labels: np.ndarray, direction: int, first: int, last: int):
    visits = runs(labels, first, last)
    output = []
    index = 0
    while index <= len(visits) - 4:
        window = visits[index : index + 4]
        q = [entry[0] for entry in window]
        lengths = [entry[2] - entry[1] + 1 for entry in window]
        expected = [(q[0] + direction * step) % 4 for step in range(4)]
        if min(lengths) < 2 or q != expected:
            index += 1
            continue
        output.append(window)
        index += 4
    return output


def identities_for_window(
    connected: np.ndarray, seed: int, pair: int, window, count: int = 4
):
    return [
        np.mean(
            connected[seed, start : end + 1, pair],
            axis=0,
            dtype=np.float64,
        )
        for _, start, end in window[:count]
    ]


def fit_affine(closure: np.ndarray, connected: np.ndarray):
    x_blocks, y_blocks = [], []
    eligible = np.zeros((100, 66), dtype=bool)
    coordinate_cache: dict[tuple[int, int], tuple] = {}
    development_cycles = 0
    for seed in range(100):
        for pair in range(66):
            coord = coordinates(closure[seed, :, pair])
            if coord is None:
                continue
            u, v, labels, direction, coherence, occupancy = coord
            if coherence < 0.80 or occupancy < 0.05:
                continue
            eligible[seed, pair] = True
            coordinate_cache[(seed, pair)] = coord
            for window in complete_windows(labels, direction, 0, 248):
                c1, c2, c3, c4 = identities_for_window(
                    connected, seed, pair, window
                )
                x_blocks.append(
                    np.stack((c1.ravel(), c2.ravel(), c3.ravel()), axis=1)
                )
                y_blocks.append(c4.ravel())
                development_cycles += 1
    if not x_blocks:
        raise RuntimeError("No development cycles available for affine comparator")
    design = np.concatenate(x_blocks, axis=0)
    target = np.concatenate(y_blocks, axis=0)
    normal = design.T @ design
    rhs = design.T @ target
    condition = float(np.linalg.cond(normal))
    if np.isfinite(condition) and condition <= 1e10:
        coefficients = np.linalg.solve(normal, rhs)
        fit_method = "normal-equation solve"
    else:
        coefficients = np.linalg.pinv(normal, rcond=1e-12) @ rhs
        fit_method = "Moore-Penrose pseudoinverse rcond=1e-12"
    return (
        coefficients.astype(np.float64),
        condition,
        fit_method,
        development_cycles,
        eligible,
        coordinate_cache,
    )


def predictor_stack(c1, c2, c3, flag: bool, affine: np.ndarray):
    delta = c1 - c2
    forward = c3 + delta
    q40 = c3 - delta if flag else forward
    return np.stack(
        (
            q40,
            forward,
            c3,
            c1,
            2 * c3 - c2,
            (c1 + c2 + c3) / 3,
            c3 - delta,
            -forward if flag else forward,
            c3 if flag else forward,
            forward if flag else c3 - delta,
            affine[0] * c1 + affine[1] * c2 + affine[2] * c3,
        ),
        axis=0,
    )


def prepare_predictions(closure: np.ndarray, connected: np.ndarray):
    (
        affine,
        affine_condition,
        affine_fit_method,
        development_cycles,
        eligible,
        coordinate_cache,
    ) = fit_affine(closure, connected)
    metadata: dict[str, list] = defaultdict(list)
    c_visible, prediction_blocks = [], []
    plane_sample = None
    plane_sample_cycles = -1
    for (seed, pair), coord in coordinate_cache.items():
        u, v, labels, direction, coherence, occupancy = coord
        windows = complete_windows(labels, direction, 250, 498)
        lineage_scale = float(
            np.median(np.linalg.norm(connected[seed, :250, pair], axis=(1, 2)))
        )
        if len(windows) > plane_sample_cycles:
            plane_sample_cycles = len(windows)
            plane_sample = (u[250:499], v[250:499], labels[250:499], seed, pair)
        for window in windows:
            c1, c2, c3 = identities_for_window(
                connected, seed, pair, window, count=3
            )
            delta = c1 - c2
            forward = c3 + delta
            flag_cosine = float(
                np.sum(forward * c3)
                / (np.linalg.norm(forward) * np.linalg.norm(c3) + EPS)
            )
            flag = flag_cosine < 0
            c_visible.append(np.stack((c1, c2, c3)))
            prediction_blocks.append(predictor_stack(c1, c2, c3, flag, affine))
            q = [entry[0] for entry in window]
            metadata["seed"].append(seed)
            metadata["pair"].append(pair)
            metadata["direction"].append(direction)
            metadata["coherence"].append(coherence)
            metadata["occupancy"].append(occupancy)
            metadata["q1"].append(q[0])
            metadata["q2"].append(q[1])
            metadata["q3"].append(q[2])
            metadata["q4"].append(q[3])
            for index, (_, start, end) in enumerate(window, start=1):
                metadata[f"q{index}_start"].append(start)
                metadata[f"q{index}_end"].append(end)
            metadata["lineage_scale"].append(lineage_scale)
            metadata["flag_cosine"].append(flag_cosine)
            metadata["flag"].append(int(flag))
    if not prediction_blocks:
        raise RuntimeError("Q40 produced no evaluation cycles")
    payload = {
        key: np.asarray(value)
        for key, value in metadata.items()
    }
    payload.update(
        {
            "c_visible": np.asarray(c_visible, dtype=np.float32),
            "predictions": np.asarray(prediction_blocks, dtype=np.float32),
            "methods": np.asarray(METHODS),
            "affine_coefficients": affine,
            "affine_condition": np.asarray(affine_condition),
            "affine_fit_method": np.asarray(affine_fit_method),
            "development_cycles": np.asarray(development_cycles),
            "eligible_lineages": np.asarray(int(np.sum(eligible))),
        }
    )
    np.savez_compressed(PREDICTIONS, **payload)
    prediction_sha = digest(PREDICTIONS, "sha256")
    print(f"frozen prediction SHA-256: {prediction_sha}", flush=True)
    return prediction_sha, plane_sample


def matrix_metrics(predicted: np.ndarray, actual: np.ndarray, scale: float):
    error = float(np.linalg.norm(predicted - actual))
    actual_norm = float(np.linalg.norm(actual))
    predicted_norm = float(np.linalg.norm(predicted))
    cosine = float(
        np.sum(predicted * actual)
        / (predicted_norm * actual_norm + EPS)
    )
    predicted_h = float(np.cbrt(abs(np.linalg.det(predicted))))
    actual_h = float(np.cbrt(abs(np.linalg.det(actual))))
    return {
        "scaled_error": error / (scale + EPS),
        "absolute_error": error,
        "nrmse": error / (actual_norm + EPS),
        "cosine": cosine,
        "closure_error": abs(predicted_h - actual_h) / (actual_h + EPS),
    }


def score_predictions(connected: np.ndarray):
    frozen = np.load(PREDICTIONS, allow_pickle=False)
    stored_methods = tuple(str(value) for value in frozen["methods"])
    if stored_methods != METHODS:
        raise RuntimeError(f"Frozen methods changed: {stored_methods}")
    n = len(frozen["seed"])
    rows: list[dict[str, object]] = []
    actual_matrices = []
    for index in range(n):
        seed, pair = int(frozen["seed"][index]), int(frozen["pair"][index])
        start = int(frozen["q4_start"][index])
        end = int(frozen["q4_end"][index])
        actual = np.mean(
            connected[seed, start : end + 1, pair],
            axis=0,
            dtype=np.float64,
        )
        actual_matrices.append(actual)
        c1, c2, c3 = np.asarray(frozen["c_visible"][index], dtype=np.float64)
        forward = c1 - c2 + c3
        target_orientation_cosine = float(
            np.sum(forward * actual)
            / (np.linalg.norm(forward) * np.linalg.norm(actual) + EPS)
        )
        row: dict[str, object] = {
            "cycle_id": index,
            "seed": seed,
            "pair_index": pair,
            "pair": PAIR_NAMES[pair],
            "direction": int(frozen["direction"][index]),
            "q1": int(frozen["q1"][index]),
            "q2": int(frozen["q2"][index]),
            "q3": int(frozen["q3"][index]),
            "q4": int(frozen["q4"][index]),
            "q1_start": int(frozen["q1_start"][index]),
            "q1_end": int(frozen["q1_end"][index]),
            "q2_start": int(frozen["q2_start"][index]),
            "q2_end": int(frozen["q2_end"][index]),
            "q3_start": int(frozen["q3_start"][index]),
            "q3_end": int(frozen["q3_end"][index]),
            "q4_start": start,
            "q4_end": end,
            "lineage_scale": float(frozen["lineage_scale"][index]),
            "flag_cosine": float(frozen["flag_cosine"][index]),
            "flag": int(frozen["flag"][index]),
            "target_negative_orientation": int(target_orientation_cosine < 0),
            "target_orientation_cosine": target_orientation_cosine,
            "target_norm": float(np.linalg.norm(actual)),
        }
        predictions = np.asarray(frozen["predictions"][index], dtype=np.float64)
        for method_index, method in enumerate(METHODS):
            for metric, value in matrix_metrics(
                predictions[method_index],
                actual,
                float(row["lineage_scale"]),
            ).items():
                row[f"{method}_{metric}"] = float(value)
        rows.append(row)
    return rows, np.asarray(actual_matrices), frozen


def lineage_and_seed_rows(rows):
    lineage_groups: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for row in rows:
        lineage_groups[(int(row["seed"]), int(row["pair_index"]))].append(row)
    lineage_rows = []
    metrics = (
        "scaled_error",
        "absolute_error",
        "nrmse",
        "cosine",
        "closure_error",
    )
    for (seed, pair), values in lineage_groups.items():
        item = {"seed": seed, "pair_index": pair, "cycles": len(values)}
        for method in METHODS:
            for metric in metrics:
                item[f"{method}_{metric}"] = float(
                    np.mean([row[f"{method}_{metric}"] for row in values])
                )
        lineage_rows.append(item)
    seed_groups: dict[int, list[dict]] = defaultdict(list)
    for row in lineage_rows:
        seed_groups[int(row["seed"])].append(row)
    seed_rows = []
    for seed, values in seed_groups.items():
        item = {"seed": seed, "lineages": len(values)}
        for method in METHODS:
            for metric in metrics:
                item[f"{method}_{metric}"] = float(
                    np.mean([row[f"{method}_{metric}"] for row in values])
                )
        seed_rows.append(item)
    return lineage_rows, seed_rows


def bootstrap_advantage(seed_rows, baseline: str, metric: str, higher: bool):
    q40 = np.asarray([row[f"q40_{metric}"] for row in seed_rows])
    control = np.asarray([row[f"{baseline}_{metric}"] for row in seed_rows])
    difference = q40 - control if higher else control - q40
    rng = np.random.default_rng(BOOTSTRAP_SEED + METHODS.index(baseline) * 17)
    indices = rng.integers(
        0, len(difference), size=(BOOTSTRAP_DRAWS, len(difference))
    )
    boot = np.mean(difference[indices], axis=1)
    observed = float(np.mean(difference))
    signs = rng.choice((-1.0, 1.0), size=(BOOTSTRAP_DRAWS, len(difference)))
    permuted = np.mean(signs * difference, axis=1)
    return {
        "advantage": observed,
        "ci95": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
        "p_no_advantage": float((np.sum(boot <= 0) + 1) / (BOOTSTRAP_DRAWS + 1)),
        "sign_permutation_p_two_sided": float(
            (np.sum(np.abs(permuted) >= abs(observed)) + 1)
            / (BOOTSTRAP_DRAWS + 1)
        ),
    }


def holm_adjust(p_values: dict[str, float]):
    ordered = sorted(p_values, key=p_values.get)
    output: dict[str, float] = {}
    running = 0.0
    count = len(ordered)
    for rank, name in enumerate(ordered):
        adjusted = min(1.0, (count - rank) * p_values[name])
        running = max(running, adjusted)
        output[name] = running
    return output


def confusion_summary(rows):
    flag = np.asarray([bool(row["flag"]) for row in rows])
    target = np.asarray([bool(row["target_negative_orientation"]) for row in rows])
    seeds = np.asarray([int(row["seed"]) for row in rows])

    def scores(f, t):
        tp = int(np.sum(f & t))
        fp = int(np.sum(f & ~t))
        fn = int(np.sum(~f & t))
        tn = int(np.sum(~f & ~t))
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        specificity = tn / max(tn + fp, 1)
        return np.asarray(
            [precision, recall, specificity, (recall + specificity) / 2],
            dtype=np.float64,
        ), (tp, fp, fn, tn)

    observed, counts = scores(flag, target)
    unique = np.unique(seeds)
    seed_counts = np.empty((len(unique), 4), dtype=np.int64)
    for index, seed in enumerate(unique):
        selected = seeds == seed
        _, seed_counts[index] = scores(flag[selected], target[selected])
    rng = np.random.default_rng(BOOTSTRAP_SEED + 901)
    indices = rng.integers(
        0, len(unique), size=(BOOTSTRAP_DRAWS, len(unique))
    )
    sampled = np.sum(seed_counts[indices], axis=1)
    tp, fp, fn, tn = (sampled[:, index] for index in range(4))
    precision = tp / np.maximum(tp + fp, 1)
    recall = tp / np.maximum(tp + fn, 1)
    specificity = tn / np.maximum(tn + fp, 1)
    boot = np.column_stack(
        (precision, recall, specificity, (recall + specificity) / 2)
    )
    names = ("precision", "recall", "specificity", "balanced_accuracy")
    return {
        "flagged_cycles": int(np.sum(flag)),
        "target_negative_cycles": int(np.sum(target)),
        "flagged_seeds": int(len(np.unique(seeds[flag]))),
        "target_negative_seeds": int(len(np.unique(seeds[target]))),
        "true_positive": counts[0],
        "false_positive": counts[1],
        "false_negative": counts[2],
        "true_negative": counts[3],
        **{
            name: {
                "value": float(observed[index]),
                "seed_cluster_ci95": [
                    float(np.quantile(boot[:, index], 0.025)),
                    float(np.quantile(boot[:, index], 0.975)),
                ],
            }
            for index, name in enumerate(names)
        },
    }


def flagged_improvement(rows):
    flagged = [row for row in rows if int(row["flag"]) == 1]
    if not flagged:
        return {
            "cycles": 0,
            "cycle_improvement_fraction": float("nan"),
            "mean_scaled_error_improvement": float("nan"),
            "seed_cluster_ci95": [float("nan"), float("nan")],
        }
    improved = np.asarray(
        [
            row["forward_scaled_error"] - row["q40_scaled_error"]
            for row in flagged
        ],
        dtype=np.float64,
    )
    lineage_groups: dict[tuple[int, int], list[float]] = defaultdict(list)
    for row, difference in zip(flagged, improved):
        lineage_groups[
            (int(row["seed"]), int(row["pair_index"]))
        ].append(float(difference))
    seed_groups: dict[int, list[float]] = defaultdict(list)
    for (seed, _pair), differences in lineage_groups.items():
        seed_groups[seed].append(float(np.mean(differences)))
    seed_difference = np.asarray(
        [
            np.mean(seed_groups[seed])
            for seed in sorted(seed_groups)
        ],
        dtype=np.float64,
    )
    rng = np.random.default_rng(BOOTSTRAP_SEED + 777)
    indices = rng.integers(
        0,
        len(seed_difference),
        size=(BOOTSTRAP_DRAWS, len(seed_difference)),
    )
    boot = np.mean(seed_difference[indices], axis=1)
    return {
        "cycles": len(flagged),
        "cycle_improvement_fraction": float(np.mean(improved > 0)),
        "mean_scaled_error_improvement": float(np.mean(seed_difference)),
        "seed_cluster_ci95": [
            float(np.quantile(boot, 0.025)),
            float(np.quantile(boot, 0.975)),
        ],
    }


def summaries(rows, seed_rows):
    metrics = (
        "scaled_error",
        "absolute_error",
        "nrmse",
        "cosine",
        "closure_error",
    )
    output = {}
    for method in METHODS:
        output[method] = {}
        for metric in metrics:
            event = np.asarray([row[f"{method}_{metric}"] for row in rows])
            seed = np.asarray([row[f"{method}_{metric}"] for row in seed_rows])
            output[method][metric] = {
                "event_mean": float(np.mean(event)),
                "event_median": float(np.median(event)),
                "seed_balanced_mean": float(np.mean(seed)),
                "seed_balanced_median": float(np.median(seed)),
            }
    return output


def write_cycles(rows):
    with gzip.open(EVENTS, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_figure(rows, seed_rows, plane_sample, method_summary, confusion, verdict):
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "figure.facecolor": "#f7f8fa",
            "axes.facecolor": "#fbfcfd",
            "axes.edgecolor": "#4b5560",
            "text.color": "#20262e",
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(13.2, 9.2))
    fig.suptitle(
        "Q40 — frozen return-flow relation reversal",
        fontsize=16,
        fontweight="bold",
    )
    fig.text(
        0.5,
        0.93,
        f"{len(rows):,} cycles · {len(seed_rows)} seeds · {verdict}",
        ha="center",
        color="#5b6470",
    )

    ax = axes[0, 0]
    u, v, _labels, seed, pair = plane_sample
    ax.plot(u, v, lw=0.85, color="#517ab5", alpha=0.75)
    ax.scatter(u[::5], v[::5], s=8, color="#d89b34", alpha=0.65)
    ax.axhline(0, color="#242a31", lw=1)
    ax.axvline(0, color="#242a31", lw=1)
    for x, y, text in (
        (0.96, 0.94, "Ab / Q++"),
        (0.04, 0.94, "Ba / Q-+"),
        (0.04, 0.05, "bA / Q--"),
        (0.96, 0.05, "aB / Q+-"),
    ):
        ax.text(x, y, text, transform=ax.transAxes, ha="right" if x > 0.5 else "left")
    ax.set(
        title=f"Frozen ARA cut (seed {seed}, pair {PAIR_NAMES[pair]})",
        xlabel="closure side u",
        ylabel="closure flow v",
    )
    ax.grid(color="#e0e4e8", lw=0.5)

    ax = axes[0, 1]
    display = ("q40", "forward", "persistence_guard", "whole_sign", "affine")
    values = [method_summary[name]["scaled_error"]["seed_balanced_mean"] for name in display]
    colors = ["#d89b34"] + ["#aeb6c0"] * (len(display) - 1)
    ax.bar(range(len(display)), values, color=colors, edgecolor="#424b55")
    ax.set_xticks(range(len(display)), [METHOD_LABELS[name] for name in display], rotation=22)
    ax.set(
        title="Development-scale-normalised reconstruction error",
        ylabel="seed-balanced lineage mean E_g (lower is better)",
    )
    ax.grid(axis="y", color="#e0e4e8", lw=0.5)

    ax = axes[1, 0]
    flag = np.asarray([bool(row["flag"]) for row in rows])
    original = np.asarray([row["forward_scaled_error"] for row in rows])[flag]
    corrected = np.asarray([row["q40_scaled_error"] for row in rows])[flag]
    if len(original):
        limit = float(np.quantile(np.concatenate((original, corrected)), 0.99))
        ax.scatter(original, corrected, s=9, alpha=0.35, color="#517ab5")
        ax.plot([0, limit], [0, limit], "--", color="#d45a4c", lw=1.2)
        ax.set_xlim(0, limit)
        ax.set_ylim(0, limit)
    else:
        ax.text(0.5, 0.5, "No visible return-flow flags", ha="center", va="center")
    ax.set(
        title="Visible return branch: changed cycles",
        xlabel="forward relation E_g",
        ylabel="Q40 relation-reversal E_g",
    )
    ax.grid(color="#e0e4e8", lw=0.5)

    ax = axes[1, 1]
    matrix = np.array(
        [
            [confusion["true_positive"], confusion["false_positive"]],
            [confusion["false_negative"], confusion["true_negative"]],
        ]
    )
    image = ax.imshow(matrix, cmap="Blues")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{matrix[i,j]:,}", ha="center", va="center", fontsize=12)
    ax.set_xticks((0, 1), ("target negative", "target non-negative"))
    ax.set_yticks((0, 1), ("flagged", "unflagged"))
    ax.set(
        title=(
            f"Visible flag: precision {confusion['precision']['value']:.3f}, "
            f"recall {confusion['recall']['value']:.3f}"
        )
    )
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)

    fig.text(
        0.01,
        0.012,
        "Source: Zenodo 10.5281/zenodo.16753415 · target values scored only after "
        "the prediction artifact was hashed.",
        fontsize=8,
        color="#5b6470",
    )
    fig.tight_layout(rect=(0.02, 0.05, 0.98, 0.90), h_pad=2.0, w_pad=1.8)
    fig.savefig(FIGURE_PNG, dpi=180, bbox_inches="tight", pad_inches=0.16)
    fig.savefig(FIGURE_SVG, bbox_inches="tight", pad_inches=0.16)
    plt.close(fig)


def main() -> None:
    for path, expected in (
        (PROTOCOL, PROTOCOL_SHA256),
        (FIDELITY, FIDELITY_SHA256),
        (TARGET_LOCK, TARGET_LOCK_SHA256),
    ):
        actual = digest(path, "sha256")
        if actual != expected:
            raise RuntimeError(f"Frozen file changed: {path.name}: {actual}")
    build_caches()
    derived = np.load(DERIVED, allow_pickle=False)
    closure = derived["closure"]
    qc = derived["qc"]
    connected = np.load(CONNECTED, mmap_mode="r")

    prediction_sha, plane_sample = prepare_predictions(closure, connected)
    # Scoring begins only after the prediction artifact is closed and hashed.
    rows, _actual, frozen = score_predictions(connected)
    lineage_rows, seed_rows = lineage_and_seed_rows(rows)
    method_summary = summaries(rows, seed_rows)
    confusion = confusion_summary(rows)
    flagged = flagged_improvement(rows)

    comparisons = {
        baseline: bootstrap_advantage(
            seed_rows, baseline, "scaled_error", higher=False
        )
        for baseline in METHODS
        if baseline != "q40"
    }
    holm = holm_adjust(
        {
            name: result["p_no_advantage"]
            for name, result in comparisons.items()
        }
    )
    seeds = sorted({int(row["seed"]) for row in rows})
    lineages = {(int(row["seed"]), int(row["pair_index"])) for row in rows}
    target_negative_seeds = {
        int(row["seed"]) for row in rows if row["target_negative_orientation"]
    }
    flagged_seeds = {int(row["seed"]) for row in rows if row["flag"]}
    eligibility = (
        len(rows) >= 1000
        and len(lineages) >= 300
        and len(seeds) >= 60
        and confusion["flagged_cycles"] >= 100
        and len(flagged_seeds) >= 20
        and confusion["target_negative_cycles"] >= 100
        and len(target_negative_seeds) >= 20
    )
    q40_error = method_summary["q40"]["scaled_error"]["seed_balanced_mean"]
    lower_than = {
        method: q40_error
        < method_summary[method]["scaled_error"]["seed_balanced_mean"]
        for method in METHODS
        if method != "q40"
    }
    q40_negative_fraction = float(
        np.mean([row["q40_cosine"] < 0 for row in rows])
    )
    gates = {
        "eligibility": eligibility,
        "lower_scaled_error_than_every_comparator": all(lower_than.values()),
        "holm_adjusted_p_below_0_05_every_comparator": all(
            value < 0.05 for value in holm.values()
        ),
        "flagged_improvement_fraction_over_0_70_and_ci_positive": (
            flagged["cycle_improvement_fraction"] > 0.70
            and flagged["seed_cluster_ci95"][0] > 0
        ),
        "flag_precision_recall_specificity": (
            confusion["precision"]["value"] >= 0.75
            and confusion["recall"]["value"] >= 0.75
            and confusion["specificity"]["value"] >= 0.90
        ),
        "cosine_improved_and_negative_under_0_05": (
            method_summary["q40"]["cosine"]["seed_balanced_mean"]
            > method_summary["forward"]["cosine"]["seed_balanced_mean"]
            and q40_negative_fraction < 0.05
        ),
        "beats_whole_sign_and_inverted_flag": (
            lower_than["whole_sign"] and lower_than["inverted_flag"]
        ),
    }
    mechanism_gates = all(
        gates[name]
        for name in (
            "flagged_improvement_fraction_over_0_70_and_ci_positive",
            "flag_precision_recall_specificity",
            "cosine_improved_and_negative_under_0_05",
            "beats_whole_sign_and_inverted_flag",
        )
    )
    beats_all_except_affine = all(
        value for name, value in lower_than.items() if name != "affine"
    )
    if not eligibility:
        verdict = "INCONCLUSIVE — ELIGIBILITY"
    elif all(gates.values()):
        verdict = "SUPPORTED ON UNTOUCHED SAME-FAMILY ARCHIVE"
    elif mechanism_gates and beats_all_except_affine and not lower_than["affine"]:
        verdict = "MECHANISM REPLICATED; NOT BEST PREDICTOR"
    elif not gates["flagged_improvement_fraction_over_0_70_and_ci_positive"] or not gates[
        "flag_precision_recall_specificity"
    ]:
        verdict = "NOT SUPPORTED — RETURN-FLOW RULE"
    else:
        verdict = "NOT SUPPORTED — COMPLETE Q40 OPERATOR"

    single_best = float(
        np.mean(
            [
                row["q40_scaled_error"]
                < min(
                    row[f"{method}_scaled_error"]
                    for method in METHODS
                    if method != "q40"
                )
                for row in rows
            ]
        )
    )
    summary = {
        "test_id": TEST_ID,
        "verdict": verdict,
        "design": "prospective masked fourth-visit same-family replication",
        "source": {
            "doi": "10.5281/zenodo.16753415",
            "archive": ARCHIVE_NAME,
            "archive_md5": digest(ARCHIVE, "md5"),
            "branch": BRANCH,
        },
        "frozen_files": {
            "protocol_sha256": digest(PROTOCOL, "sha256"),
            "fidelity_sha256": digest(FIDELITY, "sha256"),
            "target_lock_sha256": digest(TARGET_LOCK, "sha256"),
            "prediction_sha256": prediction_sha,
        },
        "population": {
            "complete_cycles": len(rows),
            "represented_lineages": len(lineages),
            "represented_seeds": len(seeds),
            "flagged_cycles": confusion["flagged_cycles"],
            "flagged_seeds": len(flagged_seeds),
            "target_negative_cycles": confusion["target_negative_cycles"],
            "target_negative_seeds": len(target_negative_seeds),
            "development_cycles_for_affine": int(frozen["development_cycles"]),
            "eligible_development_lineages": int(frozen["eligible_lineages"]),
        },
        "affine_comparator": {
            "coefficients": [
                float(value) for value in frozen["affine_coefficients"]
            ],
            "normal_matrix_condition": float(frozen["affine_condition"]),
            "fit_method": str(frozen["affine_fit_method"]),
        },
        "quality_control": {
            "sampled_trace_max_error": float(np.max(qc[:, 0])),
            "sampled_hermiticity_max_error": float(np.max(qc[:, 1])),
            "sampled_min_eigenvalue": float(np.min(qc[:, 2])),
            "sampled_density_matrices": int(np.sum(qc[:, 3])),
        },
        "method_summary": method_summary,
        "comparisons": comparisons,
        "holm_adjusted_primary_p": holm,
        "visible_flag": confusion,
        "flagged_branch_improvement": flagged,
        "q40_negative_cosine_fraction": q40_negative_fraction,
        "q40_single_best_fraction": single_best,
        "lower_scaled_error_than": lower_than,
        "gates": gates,
        "limitations": [
            "Same deterministic simulator family, not independent quantum hardware.",
            "Scalar closure-flow supplies visit timing; this is not blind timing.",
            "A pass does not prove a physical Phase B or literal singularity.",
            "Cross-tier fractality and entanglement remain separate tests.",
        ],
    }
    RESULTS.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_cycles(rows)
    make_figure(rows, seed_rows, plane_sample, method_summary, confusion, verdict)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()

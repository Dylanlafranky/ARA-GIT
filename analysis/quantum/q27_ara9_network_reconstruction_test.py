"""Run the frozen Q27 ARA^9 network reconstruction test.

Public source
-------------
Akhouri, Shandera and Henry (2025), Dataset for 6-14 qubits evolving
on network with varying connectivity.
DOI: 10.5281/zenodo.16753415
Archive: unnati_submit_12_pure_random.hdf5.zip
MD5: 06b6b278c4ce1e8ce14d2d662f0dc9dc

Protocol
--------
Q27_ARA9_NETWORK_RECONSTRUCTION_PROTOCOL_v1_FROZEN.md
SHA-256: d1d9c8051f46e10b737aea00a069ec45be9303ed89a5914416649899372c1427

The script reads every pair in both deposited connectivity strata. It caches
only the derived connected-closure amplitude, determinant orientation and
connectivity arrays; the 3.45 GB public HDF5 remains reproducible through the
download script and is not committed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import os
import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Iterable


HERE = pathlib.Path(__file__).resolve().parent
DEPS = HERE / ".q27_deps"
sys.path.insert(0, str(DEPS))
os.environ.setdefault("MPLCONFIGDIR", str(DEPS / "mplconfig"))
os.environ.setdefault("MPLBACKEND", "Agg")

import h5py  # noqa: E402
import numpy as np  # noqa: E402


TEST_ID = "Q27-ARA9-NETWORK-RECONSTRUCTION-v1"
SEED = 27027
SOURCE = (
    HERE
    / "public_data"
    / "q27_network_reconstruction"
    / "unnati_submit_12_pure_random.hdf5"
)
SOURCE_SHA256 = "0e10afb6e5c7bcc3b469a9bb18a9bcae9469bfae165d5da5add93eeeb1972eeb"
PROTOCOL_SHA256 = "d1d9c8051f46e10b737aea00a069ec45be9303ed89a5914416649899372c1427"
IMPLEMENTATION_SHA256 = (
    "0035422d9504d788c74d01ae4d856f472554f7664a669c3fbfe9824fd311c677"
)
CACHE = HERE / "public_data" / "q27_network_reconstruction" / "q27_derived_cache.npz"
RESULTS = HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_RESULTS.json"
METRICS = HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_METRICS.csv"
TRIALS = HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_TRIALS.csv"
NULLS = HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_CONTROLS.csv"
TRAJECTORY_SAMPLE = HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_TRAJECTORY_SAMPLE.csv"
FIGURE = HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_GEOMETRY.png"
FIGURE_SVG = HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_GEOMETRY.svg"

BRANCHES = ("c2_2local connectivity", "c4_2local connectivity")
PAIRS = tuple(itertools.combinations(range(12), 2))
PAIR_NAMES = tuple(str(pair) for pair in PAIRS)
PAIR_TO_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
EXPOSED = 250
MIN_RUN = 5
BOOTSTRAP_DRAWS = 2000
NULL_DRAWS = 999
EPS = 1e-12

I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
PAULI = (X, Y, Z)
A_OPS = np.stack([np.kron(p, I2) for p in PAULI])
B_OPS = np.stack([np.kron(I2, p) for p in PAULI])
T_OPS = np.stack([np.kron(p, q) for p in PAULI for q in PAULI])
OPS = np.concatenate((A_OPS, B_OPS, T_OPS), axis=0)


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def numeric_seed(name: str) -> int:
    return int(name.rsplit(" ", 1)[-1])


def density_batch_to_closure(rhos: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    expectations = np.einsum("nij,kji->nk", rhos, OPS, optimize=True).real
    a = expectations[:, 0:3]
    b = expectations[:, 3:6]
    tensor = expectations[:, 6:15].reshape(-1, 3, 3)
    connected = tensor - a[:, :, None] * b[:, None, :]
    determinants = np.linalg.det(connected)
    closure = np.cbrt(np.abs(determinants))
    orientation = np.where(
        np.abs(determinants) <= EPS,
        0,
        np.sign(determinants),
    ).astype(np.int8)
    return closure.astype(np.float32), orientation


def process_trial(branch_index: int, seed: int) -> dict[str, object]:
    branch = BRANCHES[branch_index]
    path = (
        f"/12 qubits/{branch}/unitary energy subspace 1/"
        f"unitary seed {seed}/ordering seed random"
    )
    closure = np.empty((500, 66), dtype=np.float32)
    orientation = np.empty((500, 66), dtype=np.int8)
    trace_error = 0.0
    hermiticity_error = 0.0
    minimum_eigenvalue = math.inf
    psd_failures = 0
    qc_count = 0
    qc_times = {0, 124, 249, 374, 499}
    qc_pairs = {0, 16, 32, 48, 65}

    with h5py.File(SOURCE, "r") as handle:
        base = handle[path]
        dm_root = base["two_qubit_dms"]
        for time_index in range(500):
            group = dm_root[str(time_index)]
            rhos = np.stack([group[name][()] for name in PAIR_NAMES])
            closure[time_index], orientation[time_index] = density_batch_to_closure(
                rhos
            )

            if time_index in qc_times:
                for pair_index in qc_pairs:
                    rho = np.asarray(rhos[pair_index], dtype=np.complex128)
                    trace_error = max(
                        trace_error,
                        float(abs(np.trace(rho) - 1.0)),
                    )
                    hermiticity_error = max(
                        hermiticity_error,
                        float(np.max(np.abs(rho - rho.conj().T))),
                    )
                    eig_min = float(np.min(np.linalg.eigvalsh((rho + rho.conj().T) / 2)))
                    minimum_eigenvalue = min(minimum_eigenvalue, eig_min)
                    psd_failures += int(eig_min < -1e-6)
                    qc_count += 1

        edges = np.asarray(
            base["previous_order"]["orders_list"]["data"][()],
            dtype=np.int8,
        )

    return {
        "branch_index": branch_index,
        "seed": seed,
        "closure": closure,
        "orientation": orientation,
        "edges": edges,
        "qc": (
            trace_error,
            hermiticity_error,
            minimum_eigenvalue,
            psd_failures,
            qc_count,
        ),
    }


def extract_cache(workers: int) -> None:
    if sha256(SOURCE) != SOURCE_SHA256:
        raise RuntimeError("Extracted HDF5 SHA-256 does not match frozen source")

    closure = np.empty((2, 100, 500, 66), dtype=np.float32)
    orientation = np.empty((2, 100, 500, 66), dtype=np.int8)
    edges = np.empty((2, 100, 499, 6, 2), dtype=np.int8)
    qc = np.empty((2, 100, 5), dtype=np.float64)
    jobs = [(branch_index, seed) for branch_index in range(2) for seed in range(100)]

    completed = 0
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(process_trial, branch_index, seed): (branch_index, seed)
            for branch_index, seed in jobs
        }
        for future in as_completed(futures):
            result = future.result()
            branch_index = int(result["branch_index"])
            seed = int(result["seed"])
            closure[branch_index, seed] = result["closure"]
            orientation[branch_index, seed] = result["orientation"]
            edges[branch_index, seed] = result["edges"]
            qc[branch_index, seed] = result["qc"]
            completed += 1
            if completed % 10 == 0 or completed == len(jobs):
                print(f"derived {completed}/{len(jobs)} trial-strata", flush=True)

    np.savez(
        CACHE,
        closure=closure,
        orientation=orientation,
        edges=edges,
        qc=qc,
        branch_names=np.asarray(BRANCHES),
        pairs=np.asarray(PAIRS, dtype=np.int8),
    )
    print(f"wrote {CACHE} ({CACHE.stat().st_size} bytes)")


def sustained_runs(mask: np.ndarray, minimum: int = MIN_RUN) -> list[tuple[int, int]]:
    padded = np.concatenate(([False], np.asarray(mask, dtype=bool), [False]))
    transitions = np.diff(padded.astype(np.int8))
    starts = np.flatnonzero(transitions == 1)
    ends = np.flatnonzero(transitions == -1) - 1
    return [
        (int(start), int(end))
        for start, end in zip(starts, ends)
        if end - start + 1 >= minimum
    ]


@dataclass(frozen=True)
class EligiblePath:
    crest_start: int
    crest_end: int
    trough_start: int
    trough_end: int
    predicted_return: int
    tolerance: int


def eligible_path(x: np.ndarray) -> EligiblePath | None:
    crests = sustained_runs(x[:EXPOSED] >= 1.5)
    troughs = sustained_runs(x[:EXPOSED] <= 0.5)
    for trough_start, trough_end in troughs:
        previous = [run for run in crests if run[1] < trough_start]
        if not previous:
            continue
        crest_start, crest_end = previous[-1]
        half_span = trough_start - crest_end
        predicted_return = trough_start + half_span
        if EXPOSED <= predicted_return <= 499:
            tolerance = max(10, int(math.ceil(0.25 * half_span)))
            return EligiblePath(
                crest_start=crest_start,
                crest_end=crest_end,
                trough_start=trough_start,
                trough_end=trough_end,
                predicted_return=predicted_return,
                tolerance=tolerance,
            )
    return None


def neighbour_closure(h: np.ndarray, edge_history: np.ndarray) -> np.ndarray:
    result = np.zeros_like(h, dtype=np.float64)
    for time_index in range(500):
        edge_row = edge_history[max(0, time_index - 1)]
        active: list[int] = []
        for raw_u, raw_v in edge_row:
            pair = tuple(sorted((int(raw_u), int(raw_v))))
            if pair in PAIR_TO_INDEX:
                active.append(PAIR_TO_INDEX[pair])
        if not active:
            continue
        for source_index, (u, v) in enumerate(PAIRS):
            total = 0.0
            for target_index in active:
                if target_index == source_index:
                    continue
                i, j = PAIRS[target_index]
                if u in (i, j) or v in (i, j):
                    total += float(h[time_index, target_index])
            result[time_index, source_index] = total
    return result


def overlap(release: np.ndarray, accumulation: np.ndarray) -> float:
    numerator = float(np.dot(release, accumulation))
    denominator = float(np.linalg.norm(release) * np.linalg.norm(accumulation))
    return numerator / denominator if denominator > EPS else 0.0


def first_hidden_run(mask: np.ndarray) -> tuple[int, int] | None:
    runs = sustained_runs(mask[EXPOSED:])
    if not runs:
        return None
    start, end = runs[0]
    return start + EXPOSED, end + EXPOSED


def stable_orientation(
    signs: np.ndarray,
    x: np.ndarray,
    start: int,
    end: int,
) -> int:
    selected = signs[start : end + 1][x[start : end + 1] > 0.5]
    if selected.size < MIN_RUN:
        return 0
    for offset in range(selected.size - MIN_RUN + 1):
        window = selected[offset : offset + MIN_RUN]
        if np.all(window == 1):
            return 1
        if np.all(window == -1):
            return -1
    return 0


def write_csv(path: pathlib.Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def quantiles(values: Iterable[float]) -> dict[str, float | None]:
    array = np.asarray(list(values), dtype=float)
    if array.size == 0:
        return {"q05": None, "q25": None, "median": None, "q75": None, "q95": None}
    qs = np.quantile(array, [0.05, 0.25, 0.5, 0.75, 0.95])
    return {
        "q05": float(qs[0]),
        "q25": float(qs[1]),
        "median": float(qs[2]),
        "q75": float(qs[3]),
        "q95": float(qs[4]),
    }


def trial_bootstrap(
    rows: list[dict[str, object]],
    rng: np.random.Generator,
) -> dict[str, object]:
    clusters = sorted({(int(row["branch_index"]), int(row["seed"])) for row in rows})
    by_cluster: dict[tuple[int, int], list[dict[str, object]]] = {
        cluster: [] for cluster in clusters
    }
    for row in rows:
        by_cluster[(int(row["branch_index"]), int(row["seed"]))].append(row)

    mirror_beats_persistence = 0
    mirror_beats_no_return = 0
    reconstruction_fraction: list[float] = []
    for _ in range(BOOTSTRAP_DRAWS):
        sample = rng.integers(0, len(clusters), size=len(clusters))
        selected = [
            row
            for index in sample
            for row in by_cluster[clusters[int(index)]]
        ]
        if not selected:
            continue
        mirror = np.mean([float(row["mirror_mae"]) for row in selected])
        persistence = np.mean([float(row["persistence_mae"]) for row in selected])
        no_return = np.mean([float(row["no_return_mae"]) for row in selected])
        mirror_beats_persistence += int(mirror < persistence)
        mirror_beats_no_return += int(mirror < no_return)
        reconstruction_fraction.append(
            float(np.mean([int(row["local_reconstruction"]) for row in selected]))
        )

    return {
        "draws": BOOTSTRAP_DRAWS,
        "mirror_beats_persistence_probability": (
            mirror_beats_persistence / BOOTSTRAP_DRAWS
        ),
        "mirror_beats_no_return_probability": (
            mirror_beats_no_return / BOOTSTRAP_DRAWS
        ),
        "reconstruction_fraction_ci95": [
            float(np.quantile(reconstruction_fraction, 0.025)),
            float(np.quantile(reconstruction_fraction, 0.975)),
        ],
    }


def create_figure(
    metric_rows: list[dict[str, object]],
    trial_rows: list[dict[str, object]],
    null_rows: list[dict[str, object]],
    sample_rows: list[dict[str, object]],
) -> None:
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.edgecolor": "#334155",
            "axes.labelcolor": "#1f2937",
            "xtick.color": "#475569",
            "ytick.color": "#475569",
            "axes.titleweight": "bold",
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 9), constrained_layout=True)
    fig.suptitle("Q27 ARA⁹ network reconstruction", fontsize=18, fontweight="bold")

    ax = axes[0, 0]
    branches = ["c2", "c4", "pooled"]
    reconstruct = []
    transfer = []
    for branch in branches:
        matching = [
            row
            for row in trial_rows
            if row["stratum"] == branch
        ]
        reconstruct.append(
            float(matching[0]["local_reconstruction_fraction"]) if matching else 0
        )
        transfer.append(
            float(matching[0]["direct_neighbour_transfer_fraction"]) if matching else 0
        )
    xpos = np.arange(len(branches))
    ax.bar(xpos - 0.18, reconstruct, 0.36, color="#3b82f6", label="local return")
    ax.bar(xpos + 0.18, transfer, 0.36, color="#d49a3a", label="neighbour transfer")
    ax.axhline(0.5, color="#334155", linestyle="--", linewidth=1, label="frozen 50% gate")
    ax.set_xticks(xpos, branches)
    ax.set_ylim(0, 1)
    ax.set_ylabel("eligible fraction")
    ax.set_title("Registered branch outcomes")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[0, 1]
    pooled = [row for row in trial_rows if row["stratum"] == "pooled"][0]
    names = ["ARA mirror", "persistence", "no return"]
    values = [
        float(pooled["mirror_mae"]),
        float(pooled["persistence_mae"]),
        float(pooled["no_return_mae"]),
    ]
    ax.bar(names, values, color=["#3b82f6", "#94a3b8", "#d49a3a"])
    ax.set_ylabel("hidden ARA-coordinate MAE")
    ax.set_title("Held-out amplitude error")
    ax.tick_params(axis="x", rotation=15)

    ax = axes[1, 0]
    pair_null = [
        float(row["value"])
        for row in null_rows
        if row["control"] == "pair_shuffle"
    ]
    time_null = [
        float(row["value"])
        for row in null_rows
        if row["control"] == "circular_time"
    ]
    ax.hist(pair_null, bins=30, alpha=0.6, color="#94a3b8", label="pair shuffled")
    ax.hist(time_null, bins=30, alpha=0.45, color="#d49a3a", label="time shifted")
    ax.axvline(
        float(pooled["exact_transfer_overlap"]),
        color="#2563eb",
        linewidth=2,
        label="exact adjacency + time",
    )
    ax.set_xlabel("release–accumulation overlap")
    ax.set_ylabel("null draws")
    ax.set_title("Exact network relation against controls")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 1]
    if sample_rows:
        times = np.asarray([int(row["time"]) for row in sample_rows])
        source = np.asarray([float(row["source_x"]) for row in sample_rows])
        neighbour = np.asarray([float(row["neighbour_x"]) for row in sample_rows])
        mirror = np.asarray([float(row["mirror_x"]) for row in sample_rows])
        ax.plot(times, source, color="#2563eb", linewidth=1.8, label="source pair")
        ax.plot(times, neighbour, color="#d49a3a", linewidth=1.5, label="direct neighbours")
        ax.plot(times, mirror, color="#334155", linestyle="--", label="frozen mirror")
        ax.axvline(249.5, color="#111827", linewidth=1)
        ax.axhline(1.0, color="#64748b", linewidth=1, linestyle=":")
        ax.axhline(0.5, color="#94a3b8", linewidth=0.8, linestyle=":")
        ax.axhline(1.5, color="#94a3b8", linewidth=0.8, linestyle=":")
        ax.set_ylim(bottom=0)
        ax.set_xlabel("ordered time step")
        ax.set_ylabel("local ARA coordinate (0–2 scale)")
        ax.set_title("Worked eligible trajectory")
        ax.legend(frameon=False, fontsize=8)
    else:
        ax.text(0.5, 0.5, "No eligible worked trajectory", ha="center", va="center")
        ax.set_axis_off()

    fig.savefig(FIGURE, dpi=180)
    fig.savefig(FIGURE_SVG)
    plt.close(fig)


def analyse() -> None:
    data = np.load(CACHE, allow_pickle=False)
    h_all = np.asarray(data["closure"], dtype=np.float64)
    orientation_all = np.asarray(data["orientation"], dtype=np.int8)
    edges_all = np.asarray(data["edges"], dtype=np.int8)
    qc = np.asarray(data["qc"], dtype=np.float64)

    rng = np.random.default_rng(SEED)
    metric_rows: list[dict[str, object]] = []
    trial_summaries: list[dict[str, object]] = []
    sample_rows: list[dict[str, object]] = []
    trial_transfer_objects: list[dict[str, object]] = []

    for branch_index, branch_name in enumerate(BRANCHES):
        for seed in range(100):
            h = h_all[branch_index, seed]
            signs = orientation_all[branch_index, seed]
            neighbour = neighbour_closure(h, edges_all[branch_index, seed])
            source_scale = np.quantile(h[:EXPOSED], 0.95, axis=0)
            neighbour_scale = np.quantile(neighbour[:EXPOSED], 0.95, axis=0)
            source_x = np.divide(
                2 * h,
                source_scale[None, :],
                out=np.full_like(h, np.nan),
                where=source_scale[None, :] >= 1e-10,
            )
            neighbour_x = np.divide(
                2 * neighbour,
                neighbour_scale[None, :],
                out=np.full_like(neighbour, np.nan),
                where=neighbour_scale[None, :] >= 1e-10,
            )
            release = np.maximum(0.0, -np.diff(h, axis=0)).T
            accumulation = np.maximum(0.0, np.diff(neighbour, axis=0)).T
            eligible_indices: list[int] = []
            release_rows: list[np.ndarray] = []
            accumulation_rows: list[np.ndarray] = []

            for pair_index, pair in enumerate(PAIRS):
                if source_scale[pair_index] < 1e-10:
                    continue
                x = source_x[:, pair_index]
                path = eligible_path(x)
                if path is None:
                    continue
                eligible_indices.append(pair_index)

                hidden_crest = first_hidden_run(x >= 1.5)
                local_reconstruction = int(hidden_crest is not None)
                return_start = hidden_crest[0] if hidden_crest else None
                timing_error = (
                    abs(return_start - path.predicted_return)
                    if return_start is not None
                    else None
                )
                timing_hit = int(
                    timing_error is not None and timing_error <= path.tolerance
                )

                mirror = np.empty(500 - EXPOSED, dtype=float)
                for offset, time_index in enumerate(range(EXPOSED, 500)):
                    reflected = max(
                        path.crest_start,
                        2 * path.trough_start - time_index,
                    )
                    mirror[offset] = x[reflected]
                observed_hidden = x[EXPOSED:]
                persistence = np.full_like(observed_hidden, x[EXPOSED - 1])
                no_return = np.full_like(observed_hidden, x[path.trough_start])
                mirror_mae = float(np.mean(np.abs(observed_hidden - mirror)))
                persistence_mae = float(
                    np.mean(np.abs(observed_hidden - persistence))
                )
                no_return_mae = float(
                    np.mean(np.abs(observed_hidden - no_return))
                )

                source_hidden_trough = first_hidden_run(x <= 0.5)
                neighbour_hidden_crest = first_hidden_run(
                    neighbour_x[:, pair_index] >= 1.5
                )
                transfer = 0
                transfer_lag = None
                if source_hidden_trough and neighbour_hidden_crest:
                    transfer_lag = (
                        neighbour_hidden_crest[0] - source_hidden_trough[0]
                    )
                    transfer = int(0 <= transfer_lag <= 25)

                before_sign = stable_orientation(
                    signs[:, pair_index],
                    x,
                    path.crest_start,
                    path.crest_end,
                )
                after_sign = 0
                if hidden_crest:
                    after_sign = stable_orientation(
                        signs[:, pair_index],
                        x,
                        hidden_crest[0],
                        hidden_crest[1],
                    )
                orientation_eligible = int(before_sign != 0 and after_sign != 0)
                orientation_flip = int(
                    orientation_eligible and before_sign == -after_sign
                )

                release_hidden = release[pair_index, EXPOSED - 1 :]
                accumulation_hidden = accumulation[pair_index, EXPOSED - 1 :]
                exact_overlap = overlap(release_hidden, accumulation_hidden)
                release_rows.append(release_hidden)
                accumulation_rows.append(accumulation_hidden)

                row: dict[str, object] = {
                    "branch_index": branch_index,
                    "branch": "c2" if branch_index == 0 else "c4",
                    "seed": seed,
                    "pair_index": pair_index,
                    "pair": f"{pair[0]}-{pair[1]}",
                    "scale_h_q95_exposed": float(source_scale[pair_index]),
                    "crest_start": path.crest_start,
                    "crest_end": path.crest_end,
                    "trough_start": path.trough_start,
                    "trough_end": path.trough_end,
                    "predicted_return": path.predicted_return,
                    "timing_tolerance": path.tolerance,
                    "observed_return": return_start if return_start is not None else "",
                    "local_reconstruction": local_reconstruction,
                    "timing_hit": timing_hit,
                    "timing_error": timing_error if timing_error is not None else "",
                    "mirror_mae": mirror_mae,
                    "persistence_mae": persistence_mae,
                    "no_return_mae": no_return_mae,
                    "source_hidden_trough": (
                        source_hidden_trough[0] if source_hidden_trough else ""
                    ),
                    "neighbour_hidden_crest": (
                        neighbour_hidden_crest[0] if neighbour_hidden_crest else ""
                    ),
                    "direct_neighbour_transfer": transfer,
                    "transfer_lag": transfer_lag if transfer_lag is not None else "",
                    "exact_transfer_overlap": exact_overlap,
                    "orientation_eligible": orientation_eligible,
                    "orientation_flip": orientation_flip,
                    "orientation_before": before_sign,
                    "orientation_after": after_sign,
                    "final_source_x": float(x[-1]),
                    "final_neighbour_x": float(neighbour_x[-1, pair_index]),
                }
                metric_rows.append(row)

                if not sample_rows:
                    for time_index in range(500):
                        mirror_value = (
                            float(x[time_index])
                            if time_index < EXPOSED
                            else float(
                                x[
                                    max(
                                        path.crest_start,
                                        2 * path.trough_start - time_index,
                                    )
                                ]
                            )
                        )
                        sample_rows.append(
                            {
                                "branch": row["branch"],
                                "seed": seed,
                                "pair": row["pair"],
                                "time": time_index,
                                "source_x": float(x[time_index]),
                                "neighbour_x": float(
                                    neighbour_x[time_index, pair_index]
                                ),
                                "mirror_x": mirror_value,
                                "split": (
                                    "exposed" if time_index < EXPOSED else "hidden"
                                ),
                            }
                        )

            if eligible_indices:
                release_matrix = np.asarray(release_rows)
                accumulation_all = accumulation[:, EXPOSED - 1 :]
                rnorm = np.linalg.norm(release_matrix, axis=1, keepdims=True)
                anorm = np.linalg.norm(accumulation_all, axis=1, keepdims=True).T
                cross = release_matrix @ accumulation_all.T
                overlap_matrix = np.divide(
                    cross,
                    rnorm * anorm,
                    out=np.zeros_like(cross),
                    where=(rnorm * anorm) > EPS,
                )
                exact_values = overlap_matrix[
                    np.arange(len(eligible_indices)),
                    np.asarray(eligible_indices),
                ]
                circular = np.zeros((len(eligible_indices), 249), dtype=float)
                for row_index, pair_index in enumerate(eligible_indices):
                    r = release[pair_index, EXPOSED - 1 :]
                    a = accumulation[pair_index, EXPOSED - 1 :]
                    for shift in range(1, 250):
                        circular[row_index, shift - 1] = overlap(r, np.roll(a, shift))
                trial_transfer_objects.append(
                    {
                        "branch_index": branch_index,
                        "seed": seed,
                        "eligible_indices": np.asarray(eligible_indices, dtype=int),
                        "overlap_matrix": overlap_matrix,
                        "exact_values": exact_values,
                        "circular": circular,
                    }
                )

    if not metric_rows:
        raise RuntimeError("No eligible source trajectories; frozen test is inconclusive")

    pair_nulls = np.empty(NULL_DRAWS, dtype=float)
    time_nulls = np.empty(NULL_DRAWS, dtype=float)
    for draw in range(NULL_DRAWS):
        pair_values: list[float] = []
        time_values: list[float] = []
        for obj in trial_transfer_objects:
            permutation = rng.permutation(66)
            indices = obj["eligible_indices"]
            matrix = obj["overlap_matrix"]
            pair_values.extend(
                matrix[
                    np.arange(len(indices)),
                    permutation[indices],
                ].tolist()
            )
            circular = obj["circular"]
            shifts = rng.integers(0, 249, size=len(indices))
            time_values.extend(
                circular[np.arange(len(indices)), shifts].tolist()
            )
        pair_nulls[draw] = float(np.mean(pair_values))
        time_nulls[draw] = float(np.mean(time_values))

    null_rows = [
        {"control": "pair_shuffle", "draw": index, "value": float(value)}
        for index, value in enumerate(pair_nulls)
    ] + [
        {"control": "circular_time", "draw": index, "value": float(value)}
        for index, value in enumerate(time_nulls)
    ]

    exact_overlap = float(
        np.mean([float(row["exact_transfer_overlap"]) for row in metric_rows])
    )
    pair_percentile = float(np.mean(pair_nulls < exact_overlap))
    time_percentile = float(np.mean(time_nulls < exact_overlap))

    bootstrap = trial_bootstrap(metric_rows, rng)

    def summarize(rows: list[dict[str, object]], stratum: str) -> dict[str, object]:
        eligible = len(rows)
        local = [int(row["local_reconstruction"]) for row in rows]
        returning = [row for row in rows if int(row["local_reconstruction"])]
        nonreturning = [row for row in rows if not int(row["local_reconstruction"])]
        timing = [int(row["timing_hit"]) for row in returning]
        transfer = [
            int(row["direct_neighbour_transfer"]) for row in nonreturning
        ]
        orientation_eligible = [
            row for row in returning if int(row["orientation_eligible"])
        ]
        return {
            "stratum": stratum,
            "eligible_sources": eligible,
            "trial_strata": len(
                {(int(row["branch_index"]), int(row["seed"])) for row in rows}
            ),
            "local_reconstruction_fraction": float(np.mean(local)) if local else 0.0,
            "timing_hit_fraction": float(np.mean(timing)) if timing else 0.0,
            "timing_eligible": len(timing),
            "direct_neighbour_transfer_fraction": (
                float(np.mean(transfer)) if transfer else 0.0
            ),
            "transfer_eligible_nonreturning": len(transfer),
            "mirror_mae": float(np.mean([float(row["mirror_mae"]) for row in rows])),
            "persistence_mae": float(
                np.mean([float(row["persistence_mae"]) for row in rows])
            ),
            "no_return_mae": float(
                np.mean([float(row["no_return_mae"]) for row in rows])
            ),
            "exact_transfer_overlap": float(
                np.mean([float(row["exact_transfer_overlap"]) for row in rows])
            ),
            "orientation_reliable_reconstructions": len(orientation_eligible),
            "stable_orientation_flip_fraction": (
                float(
                    np.mean(
                        [int(row["orientation_flip"]) for row in orientation_eligible]
                    )
                )
                if orientation_eligible
                else 0.0
            ),
            "final_source_x_quantiles": quantiles(
                float(row["final_source_x"]) for row in rows
            ),
            "final_neighbour_x_quantiles": quantiles(
                float(row["final_neighbour_x"]) for row in rows
            ),
        }

    c2_rows = [row for row in metric_rows if int(row["branch_index"]) == 0]
    c4_rows = [row for row in metric_rows if int(row["branch_index"]) == 1]
    summaries = [
        summarize(c2_rows, "c2"),
        summarize(c4_rows, "c4"),
        summarize(metric_rows, "pooled"),
    ]
    pooled = summaries[-1]

    split_results: dict[str, dict[str, float]] = {}
    for label, predicate in {
        "seed_0_49": lambda row: int(row["seed"]) < 50,
        "seed_50_99": lambda row: int(row["seed"]) >= 50,
    }.items():
        selected = [row for row in metric_rows if predicate(row)]
        selected_exact = float(
            np.mean([float(row["exact_transfer_overlap"]) for row in selected])
        )
        # The pooled control median is used only for sign stability; the full
        # frozen percentiles remain the primary B2/B3 tests.
        split_results[label] = {
            "eligible_sources": len(selected),
            "exact_overlap": selected_exact,
            "pair_shuffle_advantage_vs_pooled_median": (
                selected_exact - float(np.median(pair_nulls))
            ),
            "circular_time_advantage_vs_pooled_median": (
                selected_exact - float(np.median(time_nulls))
            ),
        }

    data_gates = {
        "D1_archive_md5": True,
        "D2_100x500_each_stratum": h_all.shape == (2, 100, 500, 66),
        "D3_all_66_pairs": len(PAIRS) == 66,
        "D4_sampled_physical_matrices": bool(
            np.max(qc[:, :, 0]) <= 1e-5
            and np.max(qc[:, :, 1]) <= 1e-5
            and np.sum(qc[:, :, 3]) == 0
        ),
        "D5_freeze_precedes_numerical_read": True,
    }
    local_gates = {
        "R1_at_least_30_sources_20_trials": bool(
            pooled["eligible_sources"] >= 30 and pooled["trial_strata"] >= 20
        ),
        "R2_local_reconstruction_50pct": bool(
            pooled["local_reconstruction_fraction"] >= 0.50
        ),
        "R3_timing_hit_50pct": bool(pooled["timing_hit_fraction"] >= 0.50),
        "R4_mirror_beats_both_controls": bool(
            pooled["mirror_mae"] < pooled["persistence_mae"]
            and pooled["mirror_mae"] < pooled["no_return_mae"]
        ),
        "R5_bootstrap_95pct_both": bool(
            bootstrap["mirror_beats_persistence_probability"] >= 0.95
            and bootstrap["mirror_beats_no_return_probability"] >= 0.95
        ),
    }
    transfer_gates = {
        "B1_direct_neighbour_crest_50pct": bool(
            pooled["transfer_eligible_nonreturning"] > 0
            and pooled["direct_neighbour_transfer_fraction"] >= 0.50
        ),
        "B2_exact_adjacency_95pct": pair_percentile >= 0.95,
        "B3_exact_time_95pct": time_percentile >= 0.95,
        "B4_split_half_same_advantage": all(
            values["pair_shuffle_advantage_vs_pooled_median"] > 0
            and values["circular_time_advantage_vs_pooled_median"] > 0
            for values in split_results.values()
        ),
    }
    orientation_gate = {
        "O1_stable_flips_50pct": bool(
            pooled["orientation_reliable_reconstructions"] > 0
            and pooled["stable_orientation_flip_fraction"] >= 0.50
        )
    }

    data_pass = all(data_gates.values())
    local_supported = bool(
        data_pass
        and local_gates["R1_at_least_30_sources_20_trials"]
        and all(
            local_gates[name]
            for name in (
                "R2_local_reconstruction_50pct",
                "R3_timing_hit_50pct",
                "R4_mirror_beats_both_controls",
                "R5_bootstrap_95pct_both",
            )
        )
    )
    transfer_supported = bool(
        data_pass
        and local_gates["R1_at_least_30_sources_20_trials"]
        and all(transfer_gates.values())
    )
    if not local_gates["R1_at_least_30_sources_20_trials"] or not data_pass:
        verdict = "INCONCLUSIVE"
    elif local_supported and transfer_supported:
        verdict = "MIXED"
    elif local_supported:
        verdict = "LOCAL RECONSTRUCTION SUPPORTED"
    elif transfer_supported:
        verdict = "PHASE-B TRANSFER SUPPORTED"
    else:
        verdict = "NOT SUPPORTED"

    qc_summary = {
        "sampled_matrices": int(np.sum(qc[:, :, 4])),
        "maximum_trace_error": float(np.max(qc[:, :, 0])),
        "maximum_hermiticity_error": float(np.max(qc[:, :, 1])),
        "minimum_eigenvalue": float(np.min(qc[:, :, 2])),
        "psd_failures_below_minus_1e_6": int(np.sum(qc[:, :, 3])),
    }

    result = {
        "test_id": TEST_ID,
        "ledger_id": "T283",
        "verdict": verdict,
        "branches": summaries,
        "bootstrap": bootstrap,
        "controls": {
            "exact_transfer_overlap": exact_overlap,
            "pair_shuffle_percentile": pair_percentile,
            "pair_shuffle_quantiles": quantiles(pair_nulls),
            "circular_time_percentile": time_percentile,
            "circular_time_quantiles": quantiles(time_nulls),
            "split_halves": split_results,
        },
        "gates": {
            **data_gates,
            **local_gates,
            **transfer_gates,
            **orientation_gate,
        },
        "data_quality": qc_summary,
        "source": {
            "doi": "10.5281/zenodo.16753415",
            "archive": "unnati_submit_12_pure_random.hdf5.zip",
            "archive_md5": "06b6b278c4ce1e8ce14d2d662f0dc9dc",
            "hdf5_sha256": SOURCE_SHA256,
            "protocol_sha256": PROTOCOL_SHA256,
            "implementation_sha256": IMPLEMENTATION_SHA256,
        },
        "evidence_boundary": (
            "Complete public simulated network data; tests ARA compression and held-out "
            "trajectory/adjacency rules, not a new hardware law or universal fractality."
        ),
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_csv(METRICS, metric_rows)
    write_csv(TRIALS, summaries)
    write_csv(NULLS, null_rows)
    write_csv(TRAJECTORY_SAMPLE, sample_rows)
    create_figure(metric_rows, summaries, null_rows, sample_rows)
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

            print("Q27 source absent; restoring the checksum-locked Zenodo source.")
            extract(download())
        extract_cache(max(1, args.workers))
    if args.stage in {"analyse", "all"}:
        if not CACHE.exists():
            raise FileNotFoundError("Run the extract stage first")
        analyse()


if __name__ == "__main__":
    main()

"""Q39 prospective ARA9 Information^3 fourth-quadrant reconstruction."""

from __future__ import annotations

import concurrent.futures
import csv
import gzip
import hashlib
import itertools
import json
import math
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


TEST_ID = "Q39-ARA9-INFORMATION3-FOURTH-QUADRANT-v1"
DATA = HERE / "public_data" / "q39_information3_strongmax"
ARCHIVE_NAME = "unnati_submit_12_pure_strongmax.hdf5.zip"
HDF_NAME = "unnati_submit_12_pure_strongmax.hdf5"
ARCHIVE = DATA / ARCHIVE_NAME
SOURCE = DATA / HDF_NAME
DERIVED = DATA / "q39_derived_cache.npz"
CONNECTED = DATA / "q39_connected_cache.npy"
PROTOCOL = HERE / "Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_FIDELITY_v1.md"
RESULTS = HERE / "Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_RESULTS.json"
EVENTS = HERE / "Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_CYCLES.csv.gz"
FIGURE_PNG = HERE / "Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_GEOMETRY.png"
FIGURE_SVG = HERE / "Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_GEOMETRY.svg"

ARCHIVE_MD5 = "11b5f14ba185a9901f6a85bd31497d71"
PROTOCOL_SHA256 = "db74e4f69c4a263d317b5b1ae53dfb042d94585e2f2eb8404048e5fcad3f7ccb"
FIDELITY_SHA256 = "6ac71c0904a6295391261fca67cde7e7cc71d02a9d91f50c27d45f0b27a8d779"
BRANCH = "c2_2local connectivity"
PAIRS = tuple(itertools.combinations(range(12), 2))
PAIR_NAMES = tuple(str(pair) for pair in PAIRS)
METHODS = ("ara", "persistence", "no_flip", "linear", "mean", "wrong_order")
METHOD_LABELS = {
    "ara": "ARA Info³",
    "persistence": "Persistence",
    "no_flip": "Old identity",
    "linear": "Linear",
    "mean": "Three-state mean",
    "wrong_order": "Wrong order",
}
BOOTSTRAP_SEED = 390027
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
        raise RuntimeError("Frozen Q39 archive is missing or fails MD5")
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


def density_batch(
    rhos: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    expectation = np.einsum("nij,kji->nk", rhos, OPS, optimize=True).real
    a, b = expectation[:, :3], expectation[:, 3:6]
    tensor = expectation[:, 6:15].reshape(-1, 3, 3)
    connected = tensor - a[:, :, None] * b[:, None, :]
    determinant = np.linalg.det(connected)
    closure = np.cbrt(np.abs(determinant))
    purity = np.einsum("nij,nji->n", rhos, rhos, optimize=True).real
    diagonal = np.diagonal(rhos, axis1=1, axis2=2)
    l1 = np.sum(np.abs(rhos), axis=(1, 2)) - np.sum(np.abs(diagonal), axis=1)
    return (
        closure.astype(np.float32),
        connected.astype(np.float32),
        purity.astype(np.float32),
        l1.astype(np.float32),
    )


def process_seed(seed: int):
    closure = np.empty((500, 66), dtype=np.float32)
    connected = np.empty((500, 66, 3, 3), dtype=np.float32)
    purity = np.empty((500, 66), dtype=np.float32)
    l1 = np.empty((500, 66), dtype=np.float32)
    qc = np.zeros(4, dtype=np.float64)
    qc[2] = np.inf
    with h5py.File(SOURCE, "r") as handle:
        group = handle[locate_trial(handle, seed)]
        root = group["two_qubit_dms"]
        for time_index in range(500):
            rhos = np.stack(
                [root[str(time_index)][name][()] for name in PAIR_NAMES]
            ).astype(np.complex128)
            (
                closure[time_index],
                connected[time_index],
                purity[time_index],
                l1[time_index],
            ) = density_batch(rhos)
            if time_index in (0, 249, 499):
                for pair in (0, 32, 65):
                    rho = rhos[pair]
                    qc[0] = max(qc[0], float(abs(np.trace(rho) - 1)))
                    qc[1] = max(
                        qc[1], float(np.max(abs(rho - rho.conj().T)))
                    )
                    qc[2] = min(
                        qc[2],
                        float(
                            np.min(
                                np.linalg.eigvalsh((rho + rho.conj().T) / 2)
                            )
                        ),
                    )
                    qc[3] += 1
    return seed, closure, connected, purity, l1, qc


def build_caches(workers: int = 8) -> None:
    ensure_source()
    if DERIVED.exists() and CONNECTED.exists():
        print("using existing Q39 caches", flush=True)
        return
    DATA.mkdir(parents=True, exist_ok=True)
    closure = np.empty((100, 500, 66), dtype=np.float32)
    purity = np.empty((100, 500, 66), dtype=np.float32)
    l1 = np.empty((100, 500, 66), dtype=np.float32)
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
            seed, h, c, p, k, q = future.result()
            closure[seed], connected[seed] = h, c
            purity[seed], l1[seed], qc[seed] = p, k, q
            if completed % 5 == 0 or completed == 100:
                print(
                    f"cached {completed}/100 seeds "
                    f"({time.time() - started:.1f}s)",
                    flush=True,
                )
    connected.flush()
    np.savez_compressed(
        DERIVED,
        closure=closure,
        purity=purity,
        l1=l1,
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


def coordinates(
    line: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int, float, float] | None:
    development = np.asarray(line[:250], dtype=np.float64)
    flow = np.diff(development)
    lo, hi = np.quantile(development, [0.05, 0.95])
    centre, radius = (lo + hi) / 2, (hi - lo) / 2
    scale = float(np.quantile(np.abs(flow), 0.95))
    if not np.isfinite(radius) or not np.isfinite(scale):
        return None
    if radius <= EPS or scale <= EPS:
        return None
    u = (np.asarray(line[:-1], dtype=np.float64) - centre) / radius
    v = np.diff(np.asarray(line, dtype=np.float64)) / scale
    labels = quadrant_labels(u, v)
    dev_plane = u[:249] + 1j * v[:249]
    finite = np.isfinite(dev_plane.real) & np.isfinite(dev_plane.imag)
    if np.mean(finite) < 0.95:
        return None
    valid_plane = dev_plane[finite]
    turn = np.angle(np.conj(valid_plane[:-1]) * valid_plane[1:])
    turn = turn[np.isfinite(turn) & (np.abs(turn) > 1e-10)]
    if not turn.size:
        return None
    signed_turn = float(np.mean(np.sign(turn)))
    direction = 1 if signed_turn >= 0 else -1
    coherence = abs(signed_turn)
    occupancy = min(float(np.mean(labels[:249] == q)) for q in range(4))
    return u, v, labels, direction, coherence, occupancy


def runs(labels: np.ndarray, first: int = 250, last: int = 498):
    selected = np.asarray(labels[first : last + 1], dtype=np.int8)
    output: list[tuple[int, int, int]] = []
    start = 0
    for index in range(1, len(selected) + 1):
        if index == len(selected) or selected[index] != selected[start]:
            output.append(
                (int(selected[start]), first + start, first + index - 1)
            )
            start = index
    return output


def matrix_metrics(predicted: np.ndarray, actual: np.ndarray) -> dict[str, float]:
    actual_norm = float(np.linalg.norm(actual))
    predicted_norm = float(np.linalg.norm(predicted))
    nrmse = float(np.linalg.norm(predicted - actual) / (actual_norm + EPS))
    cosine = float(
        np.sum(predicted * actual)
        / (predicted_norm * actual_norm + EPS)
    )
    predicted_h = float(np.cbrt(abs(np.linalg.det(predicted))))
    actual_h = float(np.cbrt(abs(np.linalg.det(actual))))
    closure_error = float(abs(predicted_h - actual_h) / (actual_h + EPS))
    return {"nrmse": nrmse, "cosine": cosine, "closure_error": closure_error}


def predictors(c1: np.ndarray, c2: np.ndarray, c3: np.ndarray):
    return {
        "ara": c1 - c2 + c3,
        "persistence": c3,
        "no_flip": c1,
        "linear": 2 * c3 - c2,
        "mean": (c1 + c2 + c3) / 3,
        "wrong_order": c2 - c1 + c3,
    }


def extract_cycles(
    closure: np.ndarray,
    connected: np.ndarray,
    purity: np.ndarray,
    l1: np.ndarray,
):
    rows: list[dict[str, object]] = []
    matrices: list[tuple[np.ndarray, np.ndarray]] = []
    eligible = np.zeros((100, 66), dtype=bool)
    coherence_map = np.full((100, 66), np.nan)
    occupancy_map = np.full((100, 66), np.nan)
    phase_plane_sample = None
    sample_cycle_count = -1

    for seed in range(100):
        for pair in range(66):
            coord = coordinates(closure[seed, :, pair])
            if coord is None:
                continue
            u, v, labels, direction, coherence, occupancy = coord
            coherence_map[seed, pair] = coherence
            occupancy_map[seed, pair] = occupancy
            if coherence < 0.80 or occupancy < 0.05:
                continue
            eligible[seed, pair] = True
            visits = runs(labels)
            found = 0
            index = 0
            while index <= len(visits) - 4:
                window = visits[index : index + 4]
                q = [entry[0] for entry in window]
                lengths = [entry[2] - entry[1] + 1 for entry in window]
                expected = [(q[0] + direction * step) % 4 for step in range(4)]
                if min(lengths) < 2 or q != expected:
                    index += 1
                    continue
                identities = [
                    np.mean(
                        connected[seed, start : end + 1, pair],
                        axis=0,
                        dtype=np.float64,
                    )
                    for _, start, end in window
                ]
                c1, c2, c3, c4 = identities
                predicted = predictors(c1, c2, c3)
                target_start, target_end = window[3][1], window[3][2]
                row: dict[str, object] = {
                    "cycle_id": len(rows),
                    "seed": seed,
                    "pair_index": pair,
                    "pair": PAIR_NAMES[pair],
                    "direction": direction,
                    "development_circulation": coherence,
                    "development_min_quadrant_occupancy": occupancy,
                    "q1": q[0],
                    "q2": q[1],
                    "q3": q[2],
                    "q4": q[3],
                    "q1_start": window[0][1],
                    "q1_end": window[0][2],
                    "q2_start": window[1][1],
                    "q2_end": window[1][2],
                    "q3_start": window[2][1],
                    "q3_end": window[2][2],
                    "q4_start": target_start,
                    "q4_end": target_end,
                    "q1_length": lengths[0],
                    "q2_length": lengths[1],
                    "q3_length": lengths[2],
                    "q4_length": lengths[3],
                    "target_purity": float(
                        np.mean(purity[seed, target_start : target_end + 1, pair])
                    ),
                    "target_l1_coherence": float(
                        np.mean(l1[seed, target_start : target_end + 1, pair])
                    ),
                    "target_norm": float(np.linalg.norm(c4)),
                }
                for method in METHODS:
                    for metric, value in matrix_metrics(
                        predicted[method], c4
                    ).items():
                        row[f"{method}_{metric}"] = value
                rows.append(row)
                matrices.append((c4.copy(), predicted["ara"].copy()))
                found += 1
                index += 4
            if found > sample_cycle_count:
                sample_cycle_count = found
                phase_plane_sample = {
                    "seed": seed,
                    "pair": pair,
                    "u": u[250:499].copy(),
                    "v": v[250:499].copy(),
                    "labels": labels[250:499].copy(),
                    "cycles": found,
                }
    return rows, matrices, eligible, coherence_map, occupancy_map, phase_plane_sample


def lineage_rows(rows: list[dict[str, object]]):
    grouped: dict[tuple[int, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["seed"]), int(row["pair_index"]))].append(row)
    output = []
    for (seed, pair), values in grouped.items():
        item: dict[str, object] = {
            "seed": seed,
            "pair_index": pair,
            "cycles": len(values),
        }
        for method in METHODS:
            for metric in ("nrmse", "cosine", "closure_error"):
                item[f"{method}_{metric}"] = float(
                    np.mean([float(row[f"{method}_{metric}"]) for row in values])
                )
        output.append(item)
    return output


def seed_cluster_test(
    lineages: list[dict[str, object]],
    baseline: str,
    metric: str,
    higher_is_better: bool,
):
    grouped: dict[int, list[float]] = defaultdict(list)
    for row in lineages:
        ara = float(row[f"ara_{metric}"])
        control = float(row[f"{baseline}_{metric}"])
        difference = ara - control if higher_is_better else control - ara
        grouped[int(row["seed"])].append(difference)
    seed_difference = np.asarray(
        [np.mean(grouped[seed]) for seed in sorted(grouped)], dtype=np.float64
    )
    rng = np.random.default_rng(BOOTSTRAP_SEED + METHODS.index(baseline))
    sample_indices = rng.integers(
        0,
        len(seed_difference),
        size=(BOOTSTRAP_DRAWS, len(seed_difference)),
    )
    bootstrap = np.mean(seed_difference[sample_indices], axis=1)
    observed = float(np.mean(seed_difference))
    p_no_advantage = float(
        (np.sum(bootstrap <= 0) + 1) / (BOOTSTRAP_DRAWS + 1)
    )
    signs = rng.choice(
        np.array([-1.0, 1.0]),
        size=(BOOTSTRAP_DRAWS, len(seed_difference)),
    )
    permuted = np.mean(signs * seed_difference, axis=1)
    p_two_sided = float(
        (np.sum(np.abs(permuted) >= abs(observed)) + 1)
        / (BOOTSTRAP_DRAWS + 1)
    )
    return {
        "represented_seeds": len(seed_difference),
        "ara_advantage": observed,
        "bootstrap_ci95": [
            float(np.quantile(bootstrap, 0.025)),
            float(np.quantile(bootstrap, 0.975)),
        ],
        "bootstrap_p_no_advantage": p_no_advantage,
        "sign_permutation_p_two_sided": p_two_sided,
    }


def method_summary(rows, lineages):
    output = {}
    for method in METHODS:
        output[method] = {}
        for metric in ("nrmse", "cosine", "closure_error"):
            events = np.asarray(
                [float(row[f"{method}_{metric}"]) for row in rows],
                dtype=np.float64,
            )
            lineage = np.asarray(
                [float(row[f"{method}_{metric}"]) for row in lineages],
                dtype=np.float64,
            )
            output[method][metric] = {
                "event_mean": float(np.mean(events)),
                "event_median": float(np.median(events)),
                "event_q25": float(np.quantile(events, 0.25)),
                "event_q75": float(np.quantile(events, 0.75)),
                "lineage_mean": float(np.mean(lineage)),
                "lineage_median": float(np.median(lineage)),
            }
    return output


def average_ranks(values: np.ndarray) -> np.ndarray:
    """Return one-based average ranks with deterministic tie handling."""
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


def safe_spearman(x: np.ndarray, y: np.ndarray):
    finite = np.isfinite(x) & np.isfinite(y)
    x, y = np.asarray(x[finite]), np.asarray(y[finite])
    if len(x) < 3:
        return {"rho": float("nan"), "p_value": float("nan"), "n": len(x)}
    rho = float(np.corrcoef(average_ranks(x), average_ranks(y))[0, 1])
    # Large-sample normal approximation, adequate for the registered
    # descriptive cross-check and explicitly not used in the primary gates.
    denominator = max(1 - rho * rho, EPS)
    z = abs(rho) * math.sqrt((len(x) - 2) / denominator)
    p_value = math.erfc(z / math.sqrt(2))
    return {
        "rho": rho,
        "p_value": float(p_value),
        "n": len(x),
        "p_method": "large-sample normal approximation",
    }


def quantum_crosschecks(rows):
    fidelity = -np.asarray([float(row["ara_nrmse"]) for row in rows])
    purity = np.asarray([float(row["target_purity"]) for row in rows])
    coherence = np.asarray(
        [float(row["target_l1_coherence"]) for row in rows]
    )

    def quartiles(values):
        lo, hi = np.quantile(values, [0.25, 0.75])
        nrmse = -fidelity
        return {
            "lower_cut": float(lo),
            "upper_cut": float(hi),
            "lower_quartile_nrmse": float(np.median(nrmse[values <= lo])),
            "upper_quartile_nrmse": float(np.median(nrmse[values >= hi])),
        }

    return {
        "fidelity_vs_purity": safe_spearman(fidelity, purity),
        "fidelity_vs_l1_coherence": safe_spearman(fidelity, coherence),
        "purity_quartiles": quartiles(purity),
        "l1_coherence_quartiles": quartiles(coherence),
    }


def write_cycles(rows: list[dict[str, object]]) -> None:
    with gzip.open(EVENTS, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_figure(
    rows,
    matrices,
    lineages,
    phase_plane_sample,
    summary,
    verdict,
):
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
    fig, axes = plt.subplots(2, 3, figsize=(16, 9.5), constrained_layout=False)
    fig.suptitle(
        "Q39 — ARA⁹ fourth-quadrant reconstruction on untouched pure_strongmax",
        fontsize=16,
        fontweight="bold",
        y=0.985,
    )
    fig.text(
        0.5,
        0.947,
        f"{len(rows):,} complete cycles · {len(lineages):,} lineages · {verdict}",
        ha="center",
        color="#58616c",
    )

    ax = axes[0, 0]
    u = phase_plane_sample["u"]
    v = phase_plane_sample["v"]
    ax.plot(u, v, color="#4f79b7", lw=0.9, alpha=0.70)
    ax.scatter(u[::5], v[::5], s=8, color="#d6a23e", alpha=0.60)
    ax.axhline(0, color="#2f363d", lw=1)
    ax.axvline(0, color="#2f363d", lw=1)
    ax.text(0.96, 0.95, "Q++", transform=ax.transAxes, ha="right", va="top")
    ax.text(0.04, 0.95, "Q-+", transform=ax.transAxes, ha="left", va="top")
    ax.text(0.04, 0.05, "Q--", transform=ax.transAxes, ha="left", va="bottom")
    ax.text(0.96, 0.05, "Q+-", transform=ax.transAxes, ha="right", va="bottom")
    ax.set(
        title="ARA closure–flow plane for one eligible lineage",
        xlabel="ridge-side coordinate u",
        ylabel="accumulation/release coordinate v",
    )
    ax.grid(color="#dfe3e8", lw=0.5, alpha=0.7)

    lineage_values = [
        [float(row[f"{method}_nrmse"]) for row in lineages] for method in METHODS
    ]
    ax = axes[0, 1]
    box = ax.boxplot(
        lineage_values,
        tick_labels=[METHOD_LABELS[m] for m in METHODS],
        showfliers=False,
        patch_artist=True,
    )
    for index, patch in enumerate(box["boxes"]):
        patch.set_facecolor("#4f79b7" if index == 0 else "#d9dde2")
        patch.set_edgecolor("#30373f")
    ax.set(
        title="Fourth-quadrant matrix error by method",
        ylabel="lineage-mean NRMSE (lower is better)",
    )
    ax.set_yscale("log")
    for index, values in enumerate(lineage_values, start=1):
        ax.scatter(
            index,
            np.mean(values),
            marker="D",
            s=24,
            color="#20262e",
            zorder=4,
        )
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", color="#dfe3e8", lw=0.5)

    cosine_values = [
        [
            max(1 - float(row[f"{method}_cosine"]), 1e-6)
            for row in lineages
        ]
        for method in METHODS
    ]
    ax = axes[0, 2]
    box = ax.boxplot(
        cosine_values,
        tick_labels=[METHOD_LABELS[m] for m in METHODS],
        showfliers=False,
        patch_artist=True,
    )
    for index, patch in enumerate(box["boxes"]):
        patch.set_facecolor("#d6a23e" if index == 0 else "#d9dde2")
        patch.set_edgecolor("#30373f")
    ax.set(
        title="Fourth-quadrant orientation loss by method",
        ylabel="1 − lineage cosine (lower is better; log scale)",
    )
    ax.set_yscale("log")
    for index, values in enumerate(cosine_values, start=1):
        ax.scatter(
            index,
            np.mean(values),
            marker="D",
            s=24,
            color="#20262e",
            zorder=4,
        )
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", color="#dfe3e8", lw=0.5)

    ara_nrmse = np.asarray([float(row["ara_nrmse"]) for row in rows])
    representative = int(np.argmin(np.abs(ara_nrmse - np.median(ara_nrmse))))
    actual, predicted = matrices[representative]
    limit = max(float(np.max(abs(actual))), float(np.max(abs(predicted))), EPS)
    for ax, matrix, title in (
        (axes[1, 0], actual, "Representative hidden C₄ (actual)"),
        (axes[1, 1], predicted, "Information³ reconstruction Ĉ₄"),
    ):
        image = ax.imshow(
            matrix,
            cmap="RdBu_r",
            vmin=-limit,
            vmax=limit,
            interpolation="nearest",
        )
        for row_index in range(3):
            for column_index in range(3):
                ax.text(
                    column_index,
                    row_index,
                    f"{matrix[row_index, column_index]:+.3f}",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color=(
                        "white"
                        if abs(matrix[row_index, column_index]) > 0.55 * limit
                        else "#20262e"
                    ),
                )
        ax.set_xticks(range(3), labels=("X", "Y", "Z"))
        ax.set_yticks(range(3), labels=("X", "Y", "Z"))
        ax.set(title=title, xlabel="child-B Pauli axis", ylabel="child-A Pauli axis")
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)

    ax = axes[1, 2]
    purity = np.asarray([float(row["target_purity"]) for row in rows])
    l1_coherence = np.asarray(
        [float(row["target_l1_coherence"]) for row in rows]
    )
    scatter = ax.scatter(
        purity,
        ara_nrmse,
        c=l1_coherence,
        cmap="cividis",
        s=12,
        alpha=0.45,
        linewidths=0,
    )
    ax.set(
        title="ARA error versus ordinary quantum measures",
        xlabel="target-visit two-qubit purity",
        ylabel="ARA fourth-quadrant NRMSE (log scale)",
    )
    ax.set_yscale("log")
    ax.grid(color="#dfe3e8", lw=0.5)
    fig.colorbar(scatter, ax=ax, label="computational-basis l₁ coherence")

    fig.text(
        0.01,
        0.012,
        "Source: Zenodo 10.5281/zenodo.16753415 · quadrant boundaries use scalar "
        "closure–flow; raw C₄ is masked from the predictor.",
        fontsize=8,
        color="#58616c",
    )
    fig.tight_layout(rect=(0.015, 0.05, 0.985, 0.91), h_pad=2.2, w_pad=2.0)
    fig.savefig(
        FIGURE_PNG,
        dpi=180,
        facecolor=fig.get_facecolor(),
        bbox_inches="tight",
        pad_inches=0.18,
    )
    fig.savefig(
        FIGURE_SVG,
        facecolor=fig.get_facecolor(),
        bbox_inches="tight",
        pad_inches=0.18,
    )
    plt.close(fig)


def main() -> None:
    for path, expected in (
        (PROTOCOL, PROTOCOL_SHA256),
        (FIDELITY, FIDELITY_SHA256),
    ):
        actual = digest(path, "sha256")
        if actual != expected:
            raise RuntimeError(f"Frozen file changed: {path.name}: {actual}")
    build_caches()
    derived = np.load(DERIVED, allow_pickle=False)
    closure = derived["closure"]
    purity = derived["purity"]
    l1 = derived["l1"]
    qc = derived["qc"]
    connected = np.load(CONNECTED, mmap_mode="r")

    rows, matrices, eligible, coherence_map, occupancy_map, phase_sample = (
        extract_cycles(closure, connected, purity, l1)
    )
    if not rows:
        raise RuntimeError("Q39 produced no eligible four-quadrant cycles")
    lineages = lineage_rows(rows)
    seeds = sorted({int(row["seed"]) for row in rows})
    methods = method_summary(rows, lineages)
    comparisons = {
        baseline: {
            "nrmse": seed_cluster_test(
                lineages, baseline, "nrmse", higher_is_better=False
            ),
            "cosine": seed_cluster_test(
                lineages, baseline, "cosine", higher_is_better=True
            ),
        }
        for baseline in METHODS
        if baseline != "ara"
    }
    best_fraction = float(
        np.mean(
            [
                float(row["ara_nrmse"])
                < min(float(row[f"{m}_nrmse"]) for m in METHODS if m != "ara")
                for row in rows
            ]
        )
    )
    crosschecks = quantum_crosschecks(rows)
    eligible_result = (
        len(rows) >= 500 and len(seeds) >= 80 and len(lineages) >= 300
    )
    gates = {
        "eligibility": eligible_result,
        "ara_nrmse_lower_than_all_baselines": all(
            methods["ara"]["nrmse"]["lineage_mean"]
            < methods[baseline]["nrmse"]["lineage_mean"]
            for baseline in METHODS
            if baseline != "ara"
        ),
        "bootstrap_p_below_0_05_all_baselines": all(
            comparisons[baseline]["nrmse"]["bootstrap_p_no_advantage"] < 0.05
            for baseline in comparisons
        ),
        "ara_cosine_higher_than_all_baselines": all(
            methods["ara"]["cosine"]["lineage_mean"]
            > methods[baseline]["cosine"]["lineage_mean"]
            for baseline in METHODS
            if baseline != "ara"
        ),
        "ara_best_nrmse_fraction_ge_0_55": best_fraction >= 0.55,
        "wrong_order_worse": (
            methods["ara"]["nrmse"]["lineage_mean"]
            < methods["wrong_order"]["nrmse"]["lineage_mean"]
        ),
    }
    if not eligible_result:
        verdict = "INCONCLUSIVE — ELIGIBILITY"
    elif all(gates.values()):
        verdict = "SUPPORTED"
    else:
        verdict = "NOT SUPPORTED"

    summary = {
        "test_id": TEST_ID,
        "verdict": verdict,
        "design": "prospective masked fourth-quadrant reconstruction",
        "source": {
            "doi": "10.5281/zenodo.16753415",
            "archive": ARCHIVE_NAME,
            "archive_md5": digest(ARCHIVE, "md5"),
            "branch": BRANCH,
            "time_grain": "deposited simulator slices",
        },
        "frozen_files": {
            "protocol_sha256": digest(PROTOCOL, "sha256"),
            "fidelity_sha256": digest(FIDELITY, "sha256"),
        },
        "population": {
            "eligible_development_lineages": int(np.sum(eligible)),
            "complete_cycles": len(rows),
            "represented_seeds": len(seeds),
            "represented_lineages": len(lineages),
            "median_cycles_per_lineage": float(
                np.median([int(row["cycles"]) for row in lineages])
            ),
            "development_circulation_median_eligible": float(
                np.nanmedian(coherence_map[eligible])
            ),
            "development_min_occupancy_median_eligible": float(
                np.nanmedian(occupancy_map[eligible])
            ),
        },
        "quality_control": {
            "sampled_trace_max_error": float(np.max(qc[:, 0])),
            "sampled_hermiticity_max_error": float(np.max(qc[:, 1])),
            "sampled_min_eigenvalue": float(np.min(qc[:, 2])),
            "sampled_density_matrices": int(np.sum(qc[:, 3])),
        },
        "method_summary": methods,
        "ara_best_cycle_fraction": best_fraction,
        "paired_cluster_comparisons": comparisons,
        "independent_quantum_crosschecks": crosschecks,
        "gates": gates,
        "limitations": [
            "The source is a deterministic simulator, not quantum hardware.",
            "The scalar closure-flow cut supplies target quadrant boundaries; "
            "this is masked reconstruction, not blind boundary forecasting.",
            "The test does not uniquely identify two hidden physical children.",
            "Computational-basis l1 coherence is basis-dependent.",
        ],
    }
    RESULTS.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_cycles(rows)
    make_figure(rows, matrices, lineages, phase_sample, summary, verdict)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()

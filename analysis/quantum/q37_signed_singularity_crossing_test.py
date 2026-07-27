"""Q37: prospective signed-singularity crossing test on pure_landmax."""

from __future__ import annotations

import csv
import gzip
import hashlib
import itertools
import json
import os
import pathlib
import sys
import zipfile
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / ".q27_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".mplconfig"))

import h5py
import matplotlib.pyplot as plt
import numpy as np


TEST_ID = "Q37-SIGNED-SINGULARITY-CROSSING-v1"
DATA = HERE / "public_data" / "q37_signed_crossing_landmax"
ARCHIVE_NAME = "unnati_submit_12_pure_landmax.hdf5.zip"
HDF_NAME = "unnati_submit_12_pure_landmax.hdf5"
ARCHIVE = DATA / ARCHIVE_NAME
SOURCE = DATA / HDF_NAME
DERIVED = DATA / "q37_derived_cache.npz"
CONNECTED = DATA / "q37_connected_cache.npy"
PROTOCOL = HERE / "Q37_SIGNED_SINGULARITY_CROSSING_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "Q37_SIGNED_SINGULARITY_CROSSING_FIDELITY_v1.md"
RESULTS = HERE / "Q37_SIGNED_SINGULARITY_CROSSING_RESULTS.json"
EVENTS = HERE / "Q37_SIGNED_SINGULARITY_CROSSING_EVENTS.csv.gz"
FIGURE_PNG = HERE / "Q37_SIGNED_SINGULARITY_CROSSING_GEOMETRY.png"
FIGURE_SVG = HERE / "Q37_SIGNED_SINGULARITY_CROSSING_GEOMETRY.svg"

ARCHIVE_MD5 = "ace64ede12cfbc9e5413326f23c306ad"
PROTOCOL_SHA256 = "05d590b14751e289796a95e9d156210d51895a21ae11bd332182524a4c4ebe9a"
FIDELITY_SHA256 = "2d42c57dea506949c760b85893905be86280055338a071d8af7972eb8e63134a"
BRANCHES = ("c2_2local connectivity", "c4_2local connectivity")
PAIRS = tuple(itertools.combinations(range(12), 2))
PAIR_NAMES = tuple(str(pair) for pair in PAIRS)
K = np.arange(1, 8, dtype=np.int16)
EVAL_FIRST, EVAL_LAST = 258, 491
TIME_SHIFT = 37
BOOTSTRAP_SEED = 371027
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
        raise RuntimeError("Frozen Q37 archive is missing or fails MD5")
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
    print(f"extracted {SOURCE} ({SOURCE.stat().st_size} bytes)", flush=True)


def locate_trial(handle: h5py.File, branch: str, seed: int) -> str:
    root = handle[
        f"/12 qubits/{branch}/unitary energy subspace 1/unitary seed {seed}"
    ]
    found: list[str] = []

    def visitor(_name: str, obj) -> None:
        if isinstance(obj, h5py.Group) and "two_qubit_dms" in obj and "previous_order" in obj:
            found.append(obj.name)

    root.visititems(visitor)
    if len(found) != 1:
        raise RuntimeError(f"Unexpected seed schema for {branch}, seed {seed}: {found}")
    return found[0]


def density_batch(rhos: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    expectation = np.einsum("nij,kji->nk", rhos, OPS, optimize=True).real
    a, b = expectation[:, :3], expectation[:, 3:6]
    tensor = expectation[:, 6:15].reshape(-1, 3, 3)
    connected = tensor - a[:, :, None] * b[:, None, :]
    determinant = np.linalg.det(connected)
    closure = np.cbrt(np.abs(determinant))
    orientation = np.where(
        np.abs(determinant) <= EPS, 0, np.sign(determinant)
    ).astype(np.int8)
    return closure.astype(np.float32), orientation, connected.astype(np.float32)


def process_trial(branch: int, seed: int):
    closure = np.empty((500, 66), dtype=np.float32)
    orientation = np.empty((500, 66), dtype=np.int8)
    connected = np.empty((500, 66, 3, 3), dtype=np.float32)
    qc = np.zeros(4, dtype=np.float64)
    qc[2] = np.inf
    with h5py.File(SOURCE, "r") as handle:
        group = handle[locate_trial(handle, BRANCHES[branch], seed)]
        root = group["two_qubit_dms"]
        for time in range(500):
            rhos = np.stack([root[str(time)][name][()] for name in PAIR_NAMES])
            closure[time], orientation[time], connected[time] = density_batch(rhos)
            if time in (0, 249, 499):
                for pair in (0, 32, 65):
                    rho = np.asarray(rhos[pair], dtype=np.complex128)
                    qc[0] = max(qc[0], float(abs(np.trace(rho) - 1)))
                    qc[1] = max(qc[1], float(np.max(abs(rho - rho.conj().T))))
                    qc[2] = min(qc[2], float(np.min(np.linalg.eigvalsh((rho + rho.conj().T) / 2))))
                    qc[3] += 1
        edges = np.asarray(
            group["previous_order"]["orders_list"]["data"][()], dtype=np.int8
        )
    return branch, seed, closure, orientation, connected, edges, qc


def build_caches(workers: int = 8) -> None:
    ensure_source()
    if DERIVED.exists() and CONNECTED.exists():
        print("using existing Q37 caches", flush=True)
        return
    closure = np.empty((2, 100, 500, 66), dtype=np.float32)
    orientation = np.empty((2, 100, 500, 66), dtype=np.int8)
    edges = np.empty((2, 100, 499, 6, 2), dtype=np.int8)
    qc = np.empty((2, 100, 4), dtype=np.float64)
    connected = np.lib.format.open_memmap(
        CONNECTED, mode="w+", dtype=np.float32, shape=(2, 100, 500, 66, 3, 3)
    )
    jobs = [(branch, seed) for branch in range(2) for seed in range(100)]
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(process_trial, *job) for job in jobs]
        for count, future in enumerate(as_completed(futures), 1):
            branch, seed, h, o, c, e, q = future.result()
            closure[branch, seed], orientation[branch, seed] = h, o
            connected[branch, seed], edges[branch, seed], qc[branch, seed] = c, e, q
            if count % 10 == 0:
                print(f"derived {count}/200 strata", flush=True)
    connected.flush()
    np.savez(
        DERIVED,
        closure=closure,
        orientation=orientation,
        edges=edges,
        qc=qc,
        branch_names=np.asarray(BRANCHES),
        pairs=np.asarray(PAIRS, dtype=np.int8),
    )


def circulation(phase: np.ndarray) -> float:
    turn = np.angle(np.conj(phase[:-1]) * phase[1:])
    turn = turn[np.isfinite(turn) & (np.abs(turn) > 1e-10)]
    return float(abs(np.mean(np.sign(turn)))) if turn.size else 0.0


def complete_loops(h: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    dev = np.asarray(h[0, :, :250], dtype=np.float64)
    flow = np.diff(dev, axis=1)
    lo, hi = np.quantile(dev, [0.05, 0.95], axis=1)
    centre, radius = (lo + hi) / 2, (hi - lo) / 2
    scale = np.quantile(abs(flow), 0.95, axis=1)
    u = (dev[:, :249] - centre[:, None]) / radius[:, None]
    v = flow / scale[:, None]
    z = u + 1j * v
    phase = z / abs(z)
    eligible = np.zeros((100, 66), dtype=bool)
    coherence = np.full((100, 66), np.nan)
    for seed in range(100):
        for pair in range(66):
            line, ph = z[seed, :, pair], phase[seed, :, pair]
            valid = np.isfinite(line.real) & np.isfinite(line.imag)
            if np.mean(valid) < 0.95:
                continue
            quadrant = 2 * (line.real[valid] >= 0) + (line.imag[valid] >= 0)
            minimum = min(np.mean(quadrant == q) for q in range(4))
            coherence[seed, pair] = circulation(ph[valid])
            eligible[seed, pair] = minimum >= 0.05 and coherence[seed, pair] >= 0.80
    return eligible, coherence


def event_times(line: np.ndarray, threshold: float) -> list[int]:
    kept: list[int] = []
    for time in range(EVAL_FIRST, EVAL_LAST + 1):
        if not (
            line[time - 1] > line[time]
            and line[time] <= line[time + 1]
            and line[time] <= threshold
        ):
            continue
        if kept and time - kept[-1] < 7:
            continue
        kept.append(time)
    return kept


def shifted_time(time: int) -> int:
    span = EVAL_LAST - EVAL_FIRST + 1
    return EVAL_FIRST + ((time - EVAL_FIRST + TIME_SHIFT) % span)


def pair_control(eligible: np.ndarray, seed: int, pair: int) -> int | None:
    candidates = [int(q) for q in np.flatnonzero(eligible[seed]) if int(q) != pair]
    return min(candidates, key=lambda q: ((q - pair) % 66, q)) if candidates else None


def metrics_at(
    branch: int,
    seed: int,
    pair: int,
    time: int,
    h: np.ndarray,
    c: np.ndarray,
    orientation: np.ndarray,
) -> dict[str, float]:
    before = np.asarray(c[branch, seed, time - K, pair], dtype=np.float64)
    after = np.asarray(c[branch, seed, time + K, pair], dtype=np.float64)
    inner = np.sum(before * after, axis=(-2, -1))
    weight = np.linalg.norm(before, axis=(-2, -1)) * np.linalg.norm(
        after, axis=(-2, -1)
    )
    signed = float(np.sum(inner) / np.sum(weight)) if np.sum(weight) > EPS else np.nan
    amplitude_before = np.linalg.norm(before, axis=(-2, -1))
    amplitude_after = np.linalg.norm(after, axis=(-2, -1))
    h_before = np.asarray(h[branch, seed, time - K, pair], dtype=np.float64)
    h_after = np.asarray(h[branch, seed, time + K, pair], dtype=np.float64)

    def coordinate(pre: np.ndarray, post: np.ndarray) -> float:
        total = float(np.sum(pre) + np.sum(post))
        return float(2 * np.sum(post) / total) if total > EPS else np.nan

    before_sign = np.asarray(
        orientation[branch, seed, time - K, pair], dtype=np.int8
    )
    after_sign = np.asarray(
        orientation[branch, seed, time + K, pair], dtype=np.int8
    )
    reliable = (before_sign != 0) & (after_sign != 0)
    parity_flip = float(np.mean(before_sign[reliable] != after_sign[reliable]))
    offset_similarity = np.divide(
        inner,
        weight,
        out=np.full(7, np.nan),
        where=weight > EPS,
    )
    return {
        "signed_orientation": signed,
        "amplitude_x": coordinate(amplitude_before, amplitude_after),
        "closure_x": coordinate(h_before, h_after),
        "determinant_parity_flip_fraction": parity_flip,
        **{
            f"signed_k{k}": float(value)
            for k, value in zip(range(1, 8), offset_similarity)
        },
    }


def probability(
    rows: list[dict[str, object]],
    exact_key: str,
    control_key: str | None,
    lower_is_better: bool,
    null_value: float = 0.0,
) -> float:
    grouped: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        exact = float(row[exact_key])
        if control_key is None:
            difference = (
                null_value - exact if lower_is_better else exact - null_value
            )
        else:
            control = float(row[control_key])
            difference = control - exact if lower_is_better else exact - control
        if np.isfinite(difference):
            grouped[int(row["seed"])].append(difference)
    clusters = np.asarray([np.mean(grouped[s]) for s in sorted(grouped)])
    rng = np.random.default_rng(
        BOOTSTRAP_SEED
        + sum(map(ord, exact_key))
        + (sum(map(ord, control_key)) if control_key else 0)
    )
    draws = rng.choice(
        clusters, size=(BOOTSTRAP_DRAWS, clusters.size), replace=True
    ).mean(axis=1)
    return float(np.mean(draws > 0))


def summarize(rows: list[dict[str, object]], variant: str) -> dict[str, object]:
    def values(metric: str) -> np.ndarray:
        return np.asarray([float(r[f"{variant}_{metric}"]) for r in rows])

    signed, amp, closure = (
        values("signed_orientation"),
        values("amplitude_x"),
        values("closure_x"),
    )
    grouped: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        grouped[(int(row["seed"]), int(row["source_pair"]))].append(index)
    lineage_amp = np.asarray([np.mean(amp[i]) for i in grouped.values()])
    lineage_closure = np.asarray([np.mean(closure[i]) for i in grouped.values()])
    return {
        "events": len(rows),
        "signed_orientation_median": float(np.median(signed)),
        "signed_orientation_mean": float(np.mean(signed)),
        "signed_negative_fraction": float(np.mean(signed < 0)),
        "amplitude_x_mean": float(np.mean(amp)),
        "amplitude_x_median": float(np.median(amp)),
        "amplitude_below_ridge_fraction": float(np.mean(amp < 1)),
        "amplitude_lineage_mean": float(np.mean(lineage_amp)),
        "amplitude_lineages_below_ridge_fraction": float(np.mean(lineage_amp < 1)),
        "closure_x_mean": float(np.mean(closure)),
        "closure_x_median": float(np.median(closure)),
        "closure_below_ridge_fraction": float(np.mean(closure < 1)),
        "closure_lineage_mean": float(np.mean(lineage_closure)),
        "closure_lineages_below_ridge_fraction": float(np.mean(lineage_closure < 1)),
        "determinant_parity_flip_fraction_mean": float(
            np.mean(values("determinant_parity_flip_fraction"))
        ),
        "offset_signed_means": [
            float(np.mean(values(f"signed_k{k}"))) for k in range(1, 8)
        ],
    }


def median_path(
    rows: list[dict[str, object]], h: np.ndarray, c: np.ndarray
) -> dict[str, list[float]]:
    offsets = np.arange(-7, 8)
    amp_paths, h_paths = [], []
    for row in rows:
        seed, pair, time = (
            int(row["seed"]),
            int(row["source_pair"]),
            int(row["time"]),
        )
        matrices = np.asarray(c[0, seed, time + offsets, pair], dtype=np.float64)
        amp_paths.append(np.linalg.norm(matrices, axis=(-2, -1)))
        h_paths.append(np.asarray(h[0, seed, time + offsets, pair]))
    return {
        "offsets": offsets.tolist(),
        "amplitude": np.median(np.asarray(amp_paths), axis=0).tolist(),
        "closure": np.median(np.asarray(h_paths), axis=0).tolist(),
    }


def make_figure(
    rows: list[dict[str, object]],
    summary: dict[str, dict[str, object]],
    path: dict[str, list[float]],
) -> None:
    variants = ("exact", "time", "pair", "network")
    labels = ("Exact", "Time", "Pair", "Network")
    colors = ("#287fb8", "#d49a24", "#9b9b9b", "#555555")
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)
    x = np.asarray(path["offsets"])
    axes[0, 0].plot(x, path["amplitude"], marker="o", label="total amplitude")
    axes[0, 0].plot(x, path["closure"], marker="s", label="determinant closure")
    axes[0, 0].axvline(0, color="#333333", linestyle="--")
    axes[0, 0].set(
        title="Median target event path",
        xlabel="slices from registered crossing",
        ylabel="raw relation coordinate",
    )
    axes[0, 0].legend(frameon=False)

    signed_mean = [summary[v]["signed_orientation_mean"] for v in variants]
    axes[0, 1].bar(labels, signed_mean, color=colors)
    axes[0, 1].axhline(0, color="#333333", linewidth=1)
    axes[0, 1].axhline(-0.25, color="#d49a24", linestyle="--", label="frozen support gate")
    axes[0, 1].set(
        title="Signed orientation across the crossing",
        ylabel="event-weighted mean (−1 anti, +1 same)",
    )
    axes[0, 1].legend(frameon=False)

    positions = np.arange(4)
    width = 0.35
    axes[1, 0].bar(
        positions - width / 2,
        [summary[v]["amplitude_x_mean"] for v in variants],
        width,
        label="amplitude",
        color="#287fb8",
    )
    axes[1, 0].bar(
        positions + width / 2,
        [summary[v]["closure_x_mean"] for v in variants],
        width,
        label="closure",
        color="#d49a24",
    )
    axes[1, 0].axhline(1, color="#333333", linewidth=1)
    axes[1, 0].axhspan(0.92, 0.98, color="#287fb8", alpha=0.08)
    axes[1, 0].set_xticks(positions, labels)
    axes[1, 0].set(
        title="Equal-window traversal coordinates",
        ylabel="0–2 ARA coordinate",
    )
    axes[1, 0].legend(frameon=False)

    for variant, label, color in zip(variants, labels, colors):
        axes[1, 1].plot(
            range(1, 8),
            summary[variant]["offset_signed_means"],
            marker="o",
            label=label,
            color=color,
        )
    axes[1, 1].axhline(0, color="#333333", linewidth=1)
    axes[1, 1].set(
        title="Signed relation by distance from crossing",
        xlabel="paired offset k",
        ylabel="mean signed similarity",
    )
    axes[1, 1].legend(frameon=False, ncol=2)
    fig.suptitle(
        f"Q37 — signed crossing and traversal on untouched pure_landmax (n={len(rows):,})",
        fontsize=18,
        fontweight="bold",
    )
    fig.savefig(FIGURE_PNG, dpi=180)
    fig.savefig(FIGURE_SVG)
    plt.close(fig)


def main() -> None:
    if digest(PROTOCOL, "sha256") != PROTOCOL_SHA256:
        raise RuntimeError("Protocol hash mismatch")
    if digest(FIDELITY, "sha256") != FIDELITY_SHA256:
        raise RuntimeError("Fidelity hash mismatch")
    build_caches()
    if digest(ARCHIVE, "md5") != ARCHIVE_MD5:
        raise RuntimeError("Archive hash mismatch after reconstruction")
    derived = np.load(DERIVED)
    h = derived["closure"]
    orientation = derived["orientation"]
    connected = np.load(CONNECTED, mmap_mode="r")
    eligible, coherence = complete_loops(h)
    rows: list[dict[str, object]] = []
    represented_seeds: set[int] = set()
    represented_lineages: set[tuple[int, int]] = set()
    for seed in range(100):
        for pair in np.flatnonzero(eligible[seed]):
            pair = int(pair)
            threshold = float(np.quantile(h[0, seed, :250, pair], 0.20))
            control_pair = pair_control(eligible, seed, pair)
            if control_pair is None:
                continue
            for time in event_times(h[0, seed, :, pair], threshold):
                row: dict[str, object] = {
                    "seed": seed,
                    "source_pair": pair,
                    "time": time,
                    "pair_control": control_pair,
                    "development_circulation": float(coherence[seed, pair]),
                    "development_q20": threshold,
                }
                variants = {
                    "exact": (0, seed, pair, time),
                    "time": (0, seed, pair, shifted_time(time)),
                    "pair": (0, seed, control_pair, time),
                    "network": (1, seed, pair, time),
                }
                for name, args in variants.items():
                    for metric, value in metrics_at(
                        *args, h, connected, orientation
                    ).items():
                        row[f"{name}_{metric}"] = value
                rows.append(row)
                represented_seeds.add(seed)
                represented_lineages.add((seed, pair))

    with gzip.open(EVENTS, "wt", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = {v: summarize(rows, v) for v in ("exact", "time", "pair", "network")}
    bootstrap: dict[str, object] = {
        "signed_below_zero": probability(rows, "exact_signed_orientation", None, True),
        "signed_vs_controls": {
            v: probability(
                rows,
                "exact_signed_orientation",
                f"{v}_signed_orientation",
                True,
            )
            for v in ("time", "pair", "network")
        },
        "amplitude_below_ridge": probability(
            rows, "exact_amplitude_x", None, True, null_value=1.0
        ),
        "closure_below_ridge": probability(
            rows, "exact_closure_x", None, True, null_value=1.0
        ),
        "amplitude_vs_controls": {
            v: probability(rows, "exact_amplitude_x", f"{v}_amplitude_x", True)
            for v in ("time", "pair", "network")
        },
        "closure_vs_controls": {
            v: probability(rows, "exact_closure_x", f"{v}_closure_x", True)
            for v in ("time", "pair", "network")
        },
    }
    exact = summary["exact"]
    eligibility = {
        "complete_c2_lineages": int(np.sum(eligible)),
        "events": len(rows),
        "represented_seeds": len(represented_seeds),
        "represented_lineages": len(represented_lineages),
    }
    eligibility_pass = (
        len(rows) >= 2000
        and len(represented_seeds) >= 80
        and len(represented_lineages) >= 500
    )
    signed_gates = {
        "median_le_minus_0_25": exact["signed_orientation_median"] <= -0.25,
        "negative_fraction_ge_0_60": exact["signed_negative_fraction"] >= 0.60,
        "bootstrap_below_zero_ge_0_99": bootstrap["signed_below_zero"] >= 0.99,
        "mean_beats_controls_by_0_10": all(
            exact["signed_orientation_mean"]
            <= summary[v]["signed_orientation_mean"] - 0.10
            for v in ("time", "pair", "network")
        ),
        "bootstrap_beats_controls_ge_0_95": all(
            bootstrap["signed_vs_controls"][v] >= 0.95
            for v in ("time", "pair", "network")
        ),
    }
    traversal_gates: dict[str, bool] = {}
    for metric in ("amplitude", "closure"):
        traversal_gates[f"{metric}_mean_in_band"] = (
            0.92 <= exact[f"{metric}_x_mean"] <= 0.98
        )
        traversal_gates[f"{metric}_events_below_ge_0_55"] = (
            exact[f"{metric}_below_ridge_fraction"] >= 0.55
        )
        traversal_gates[f"{metric}_lineages_below_ge_0_55"] = (
            exact[f"{metric}_lineages_below_ridge_fraction"] >= 0.55
        )
        traversal_gates[f"{metric}_bootstrap_below_ge_0_99"] = (
            bootstrap[f"{metric}_below_ridge"] >= 0.99
        )
        traversal_gates[f"{metric}_mean_beats_controls_by_0_02"] = all(
            exact[f"{metric}_x_mean"] <= summary[v][f"{metric}_x_mean"] - 0.02
            for v in ("time", "pair", "network")
        )
        traversal_gates[f"{metric}_bootstrap_controls_ge_0_95"] = all(
            bootstrap[f"{metric}_vs_controls"][v] >= 0.95
            for v in ("time", "pair", "network")
        )
    signed_pass = eligibility_pass and all(signed_gates.values())
    traversal_pass = eligibility_pass and all(traversal_gates.values())
    weak_anti = (
        eligibility_pass
        and signed_gates["negative_fraction_ge_0_60"]
        and signed_gates["bootstrap_below_zero_ge_0_99"]
    )
    if not eligibility_pass:
        verdict = "INCONCLUSIVE — ELIGIBILITY"
    elif signed_pass and traversal_pass:
        verdict = "SIGNED CROSSING + TRAVERSAL REPLICATED"
    elif signed_pass:
        verdict = "SIGNED CROSSING ONLY"
    elif traversal_pass:
        verdict = "TRAVERSAL ASYMMETRY ONLY"
    elif weak_anti:
        verdict = "WEAK ANTI-ORIENTATION"
    else:
        verdict = "NOT REPLICATED"
    path = median_path(rows, h, connected)
    result = {
        "test_id": TEST_ID,
        "date": "2026-07-27",
        "design": "prospective cross-archive on untouched pure_landmax",
        "source": {
            "doi": "10.5281/zenodo.16753415",
            "archive": ARCHIVE_NAME,
            "archive_md5": ARCHIVE_MD5,
            "branches": list(BRANCHES),
            "shape": list(h.shape),
        },
        "frozen_hashes": {
            "protocol_sha256": PROTOCOL_SHA256,
            "fidelity_sha256": FIDELITY_SHA256,
        },
        "eligibility": eligibility,
        "eligibility_pass": eligibility_pass,
        "summary": summary,
        "bootstrap": bootstrap,
        "signed_gates": signed_gates,
        "traversal_gates": traversal_gates,
        "signed_pass": signed_pass,
        "traversal_pass": traversal_pass,
        "weak_anti_orientation": weak_anti,
        "verdict": verdict,
        "median_event_path": path,
        "boundaries": [
            "Operational tensor anti-orientation is not automatically physical Phase B.",
            "Target is a deterministic simulator, not hardware.",
            "The archive is untouched in-project, but belongs to the already-used source family.",
        ],
    }
    RESULTS.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    make_figure(rows, summary, path)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

"""Q38: prospective fixed-anchor Phase-A -> Phase-B -> Phase-A cycle test."""

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


TEST_ID = "Q38-FIXED-ANCHOR-PHASE-CYCLE-v1"
DATA = HERE / "public_data" / "q38_fixed_anchor_mimic"
ARCHIVE_NAME = "unnati_submit_12_pure_mimic.hdf5.zip"
HDF_NAME = "unnati_submit_12_pure_mimic.hdf5"
ARCHIVE = DATA / ARCHIVE_NAME
SOURCE = DATA / HDF_NAME
DERIVED = DATA / "q38_derived_cache.npz"
CONNECTED = DATA / "q38_connected_cache.npy"
PROTOCOL = HERE / "Q38_FIXED_ANCHOR_PHASE_CYCLE_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "Q38_FIXED_ANCHOR_PHASE_CYCLE_FIDELITY_v1.md"
RESULTS = HERE / "Q38_FIXED_ANCHOR_PHASE_CYCLE_RESULTS.json"
EVENTS = HERE / "Q38_FIXED_ANCHOR_PHASE_CYCLE_EVENTS.csv.gz"
FIGURE_PNG = HERE / "Q38_FIXED_ANCHOR_PHASE_CYCLE_GEOMETRY.png"
FIGURE_SVG = HERE / "Q38_FIXED_ANCHOR_PHASE_CYCLE_GEOMETRY.svg"

ARCHIVE_MD5 = "04477abdac1849dd034576c0dbb685cb"
PROTOCOL_SHA256 = "166551802e124688acc898033435a964534c02dc2f15ded75ce4dabcba56eda6"
FIDELITY_SHA256 = "ff97db53aa769964c6178657f98c5fed356966577723b40bef05e342c259f70e"
BRANCHES = ("c2_2local connectivity", "c4_2local connectivity")
PAIRS = tuple(itertools.combinations(range(12), 2))
PAIR_NAMES = tuple(str(pair) for pair in PAIRS)
PRE_OFFSETS = np.arange(-7, -2, dtype=np.int16)
POST_OFFSETS = np.arange(1, 15, dtype=np.int16)
EVAL_FIRST, EVAL_LAST = 258, 485
TIME_SHIFT = 37
BOOTSTRAP_SEED = 381027
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
        raise RuntimeError("Frozen Q38 archive is missing or fails MD5")
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


def locate_trial(handle: h5py.File, branch: str, seed: int) -> str:
    root = handle[
        f"/12 qubits/{branch}/unitary energy subspace 1/unitary seed {seed}"
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
                    qc[2] = min(
                        qc[2],
                        float(np.min(np.linalg.eigvalsh((rho + rho.conj().T) / 2))),
                    )
                    qc[3] += 1
        edges = np.asarray(
            group["previous_order"]["orders_list"]["data"][()], dtype=np.int8
        )
    return branch, seed, closure, orientation, connected, edges, qc


def build_caches(workers: int = 8) -> None:
    ensure_source()
    if DERIVED.exists() and CONNECTED.exists():
        print("using existing Q38 caches", flush=True)
        return
    closure = np.empty((2, 100, 500, 66), dtype=np.float32)
    orientation = np.empty((2, 100, 500, 66), dtype=np.int8)
    edges = np.empty((2, 100, 499, 6, 2), dtype=np.int8)
    qc = np.empty((2, 100, 4), dtype=np.float64)
    connected = np.lib.format.open_memmap(
        CONNECTED,
        mode="w+",
        dtype=np.float32,
        shape=(2, 100, 500, 66, 3, 3),
    )
    jobs = [(branch, seed) for branch in range(2) for seed in range(100)]
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(process_trial, *job) for job in jobs]
        for count, future in enumerate(as_completed(futures), 1):
            branch, seed, h, o, c, e, q = future.result()
            closure[branch, seed], orientation[branch, seed] = h, o
            connected[branch, seed], edges[branch, seed], qc[branch, seed] = (
                c,
                e,
                q,
            )
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


def complete_loops(closure: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    development = np.asarray(closure[0, :, :250], dtype=np.float64)
    flow = np.diff(development, axis=1)
    lo, hi = np.quantile(development, [0.05, 0.95], axis=1)
    centre, radius = (lo + hi) / 2, (hi - lo) / 2
    scale = np.quantile(np.abs(flow), 0.95, axis=1)
    u = (development[:, :249] - centre[:, None]) / radius[:, None]
    v = flow / scale[:, None]
    plane = u + 1j * v
    phase = plane / np.abs(plane)
    eligible = np.zeros((100, 66), dtype=bool)
    coherence = np.full((100, 66), np.nan)
    for seed in range(100):
        for pair in range(66):
            line = plane[seed, :, pair]
            valid = np.isfinite(line.real) & np.isfinite(line.imag)
            if np.mean(valid) < 0.95:
                continue
            quadrant = 2 * (line.real[valid] >= 0) + (line.imag[valid] >= 0)
            minimum = min(np.mean(quadrant == q) for q in range(4))
            coherence[seed, pair] = circulation(phase[seed, valid, pair])
            eligible[seed, pair] = (
                minimum >= 0.05 and coherence[seed, pair] >= 0.80
            )
    return eligible, coherence


def event_times(line: np.ndarray, threshold: float) -> list[int]:
    kept: list[int] = []
    for time in range(EVAL_FIRST, EVAL_LAST + 1):
        is_event = (
            line[time - 1] > line[time]
            and line[time] <= line[time + 1]
            and line[time] <= threshold
        )
        if not is_event or (kept and time - kept[-1] < 14):
            continue
        kept.append(time)
    return kept


def shifted_time(time: int) -> int:
    width = EVAL_LAST - EVAL_FIRST + 1
    return EVAL_FIRST + ((time - EVAL_FIRST + TIME_SHIFT) % width)


def pair_control(eligible: np.ndarray, seed: int, pair: int) -> int | None:
    candidates = [
        int(candidate)
        for candidate in np.flatnonzero(eligible[seed])
        if int(candidate) != pair
    ]
    return (
        min(candidates, key=lambda candidate: ((candidate - pair) % 66, candidate))
        if candidates
        else None
    )


def cycle_metrics(
    branch: int,
    seed: int,
    pair: int,
    time: int,
    closure: np.ndarray,
    connected: np.ndarray,
) -> dict[str, float]:
    before = np.asarray(
        connected[branch, seed, time + PRE_OFFSETS, pair], dtype=np.float64
    )
    before_amplitude = np.linalg.norm(before, axis=(-2, -1))
    anchor_index = int(np.argmax(before_amplitude))
    anchor = before[anchor_index]
    anchor_amplitude = float(before_amplitude[anchor_index])
    anchor_offset = int(PRE_OFFSETS[anchor_index])
    anchor_closure = float(closure[branch, seed, time + anchor_offset, pair])

    after = np.asarray(
        connected[branch, seed, time + POST_OFFSETS, pair], dtype=np.float64
    )
    after_amplitude = np.linalg.norm(after, axis=(-2, -1))
    denominator = anchor_amplitude * after_amplitude
    similarity = np.divide(
        np.sum(anchor * after, axis=(-2, -1)),
        denominator,
        out=np.full(14, np.nan),
        where=denominator > EPS,
    )
    amplitude_ratio = np.divide(
        after_amplitude,
        anchor_amplitude,
        out=np.full(14, np.nan),
        where=anchor_amplitude > EPS,
    )
    closure_ratio = np.divide(
        np.asarray(
            closure[branch, seed, time + POST_OFFSETS, pair], dtype=np.float64
        ),
        anchor_closure,
        out=np.full(14, np.nan),
        where=anchor_closure > EPS,
    )
    reliable = (
        np.isfinite(similarity)
        & np.isfinite(amplitude_ratio)
        & (amplitude_ratio >= 0.10)
    )

    early = np.flatnonzero(reliable[:7])
    if early.size:
        early_values = similarity[early]
        b_index = int(early[int(np.argmin(early_values))])
        r_b = float(similarity[b_index])
        j_b = b_index + 1
        amp_b = float(amplitude_ratio[b_index])
        closure_b = float(closure_ratio[b_index])
    else:
        b_index, r_b, j_b, amp_b, closure_b = -1, np.nan, -1, np.nan, np.nan

    if b_index >= 0:
        later = np.flatnonzero(
            reliable
            & (np.arange(14) > b_index)
            & (amplitude_ratio >= 0.50)
        )
    else:
        later = np.empty(0, dtype=int)
    if later.size:
        later_values = similarity[later]
        best = float(np.max(later_values))
        return_index = int(later[np.flatnonzero(later_values == best)[0]])
        r_return = float(similarity[return_index])
        j_return = return_index + 1
        amp_return = float(amplitude_ratio[return_index])
        closure_return = float(closure_ratio[return_index])
    else:
        return_index, r_return, j_return = -1, np.nan, -1
        amp_return, closure_return = np.nan, np.nan

    b_entry = bool(np.isfinite(r_b) and r_b <= -0.25)
    strong_b = bool(np.isfinite(r_b) and r_b <= -0.50)
    a_return = bool(np.isfinite(r_return) and r_return >= 0.25)
    cycle = bool(b_entry and a_return)
    score = (
        float(min(-r_b, r_return))
        if np.isfinite(r_b) and np.isfinite(r_return)
        else -1.0
    )
    result: dict[str, float] = {
        "anchor_offset": float(anchor_offset),
        "anchor_amplitude": anchor_amplitude,
        "anchor_closure": anchor_closure,
        "r_b": r_b,
        "j_b": float(j_b),
        "amplitude_b": amp_b,
        "closure_b": closure_b,
        "phase_b_entry": float(b_entry),
        "strong_phase_b": float(strong_b),
        "r_return": r_return,
        "j_return": float(j_return),
        "amplitude_return": amp_return,
        "closure_return": closure_return,
        "phase_a_return": float(a_return),
        "cycle": float(cycle),
        "cycle_score": score,
    }
    for offset, value in zip(POST_OFFSETS, similarity):
        result[f"r_{int(offset)}"] = float(value)
    for offset, value in zip(POST_OFFSETS, amplitude_ratio):
        result[f"a_{int(offset)}"] = float(value)
    return result


def cluster_probability(
    rows: list[dict[str, object]],
    exact_key: str,
    control_key: str | None = None,
    null_value: float = 0.0,
) -> float:
    grouped: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        exact = float(row[exact_key])
        difference = (
            exact - null_value
            if control_key is None
            else exact - float(row[control_key])
        )
        if np.isfinite(difference):
            grouped[int(row["seed"])].append(difference)
    clusters = np.asarray(
        [np.mean(grouped[seed]) for seed in sorted(grouped)], dtype=np.float64
    )
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
        return np.asarray([float(row[f"{variant}_{metric}"]) for row in rows])

    cycle = values("cycle")
    score = values("cycle_score")
    strong = values("strong_phase_b")
    r_b = values("r_b")
    r_return = values("r_return")
    j_b = values("j_b")
    j_return = values("j_return")
    amp_b = values("amplitude_b")
    amp_return = values("amplitude_return")
    grouped: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        grouped[(int(row["seed"]), int(row["source_pair"]))].append(index)
    lineage_cycle = np.asarray([np.mean(cycle[index]) for index in grouped.values()])
    lineage_score = np.asarray([np.mean(score[index]) for index in grouped.values()])
    complete = cycle > 0.5
    return {
        "events": len(rows),
        "cycle_fraction": float(np.mean(cycle)),
        "strong_phase_b_fraction": float(np.mean(strong)),
        "cycle_score_mean": float(np.mean(score)),
        "cycle_score_median": float(np.median(score)),
        "lineages_cycle_ge_half_fraction": float(np.mean(lineage_cycle >= 0.50)),
        "lineage_cycle_mean": float(np.mean(lineage_cycle)),
        "lineage_score_mean": float(np.mean(lineage_score)),
        "r_b_mean": float(np.nanmean(r_b)),
        "r_b_median": float(np.nanmedian(r_b)),
        "r_return_mean": float(np.nanmean(r_return)),
        "r_return_median": float(np.nanmedian(r_return)),
        "j_b_median": float(np.nanmedian(j_b[j_b > 0])),
        "j_return_completed_median": float(np.median(j_return[complete]))
        if np.any(complete)
        else np.nan,
        "amplitude_b_median": float(np.nanmedian(amp_b)),
        "amplitude_return_completed_median": float(np.median(amp_return[complete]))
        if np.any(complete)
        else np.nan,
        "offset_median": [
            float(np.nanmedian(values(f"r_{offset}"))) for offset in POST_OFFSETS
        ],
        "offset_q25": [
            float(np.nanquantile(values(f"r_{offset}"), 0.25))
            for offset in POST_OFFSETS
        ],
        "offset_q75": [
            float(np.nanquantile(values(f"r_{offset}"), 0.75))
            for offset in POST_OFFSETS
        ],
        "offset_q05": [
            float(np.nanquantile(values(f"r_{offset}"), 0.05))
            for offset in POST_OFFSETS
        ],
        "offset_q95": [
            float(np.nanquantile(values(f"r_{offset}"), 0.95))
            for offset in POST_OFFSETS
        ],
    }


def make_figure(
    rows: list[dict[str, object]],
    summary: dict[str, dict[str, object]],
    verdict: str,
) -> None:
    variants = ("exact", "time", "pair", "network")
    labels = ("Exact", "Time", "Pair", "Network")
    colors = ("#2878B5", "#D39017", "#999999", "#555555")
    x = POST_OFFSETS.astype(float)
    fig, axes = plt.subplots(2, 2, figsize=(18, 13), constrained_layout=True)
    fig.suptitle(
        f"Q38 — fixed-anchor exit path on untouched pure_mimic "
        f"(n={len(rows):,}; {verdict})",
        fontsize=23,
        fontweight="bold",
    )

    exact = summary["exact"]
    median = np.asarray(exact["offset_median"])
    q25, q75 = np.asarray(exact["offset_q25"]), np.asarray(exact["offset_q75"])
    q05, q95 = np.asarray(exact["offset_q05"]), np.asarray(exact["offset_q95"])
    ax = axes[0, 0]
    ax.fill_between(x, q05, q95, color="#2878B5", alpha=0.10, label="5–95%")
    ax.fill_between(x, q25, q75, color="#2878B5", alpha=0.24, label="25–75%")
    ax.plot(x, median, marker="o", color="#2878B5", lw=2.3, label="median")
    ax.axhline(0, color="#333333", lw=1.2)
    ax.axhline(-0.25, color="#D39017", lw=1.2, ls="--", label="B-entry gate")
    ax.axhline(+0.25, color="#555555", lw=1.2, ls="--", label="A-return gate")
    ax.set(
        title="Fixed Phase-A anchor versus successive exit slices",
        xlabel="exit offset after determinant pinch",
        ylabel="signed anchor similarity",
        ylim=(-1.05, 1.05),
        xticks=POST_OFFSETS,
    )
    ax.legend(ncol=2, fontsize=9)

    ax = axes[0, 1]
    for variant, label, color in zip(variants, labels, colors):
        ax.plot(
            x,
            np.asarray(summary[variant]["offset_median"]),
            marker="o",
            lw=2,
            color=color,
            label=label,
        )
    ax.axhline(0, color="#333333", lw=1.2)
    ax.set(
        title="Median fixed-anchor exit path by registered control",
        xlabel="exit offset after target/control time",
        ylabel="median signed anchor similarity",
        ylim=(-1.05, 1.05),
        xticks=POST_OFFSETS,
    )
    ax.legend(ncol=2)

    ax = axes[1, 0]
    path = np.asarray(
        [[float(row[f"exact_r_{offset}"]) for offset in POST_OFFSETS] for row in rows]
    )
    sort_b = np.asarray([float(row["exact_j_b"]) for row in rows])
    sort_return = np.asarray([float(row["exact_j_return"]) for row in rows])
    order = np.lexsort((sort_return, sort_b))
    ordered = path[order]
    if ordered.shape[0] > 5000:
        indices = np.linspace(0, ordered.shape[0] - 1, 5000, dtype=int)
        ordered = ordered[indices]
    image = ax.imshow(
        ordered,
        aspect="auto",
        interpolation="nearest",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        origin="lower",
        extent=(0.5, 14.5, 0, ordered.shape[0]),
    )
    ax.set(
        title="Exact fixed-anchor exit paths sorted by B and return offsets",
        xlabel="exit offset",
        ylabel="sorted event sample",
        xticks=POST_OFFSETS,
    )
    fig.colorbar(image, ax=ax, label="signed anchor similarity")

    ax = axes[1, 1]
    position = np.arange(4)
    width = 0.35
    cycle_fraction = [summary[v]["cycle_fraction"] for v in variants]
    score_mean = [summary[v]["cycle_score_mean"] for v in variants]
    ax.bar(
        position - width / 2,
        cycle_fraction,
        width,
        color="#2878B5",
        label="ordered-cycle fraction",
    )
    ax.bar(
        position + width / 2,
        score_mean,
        width,
        color="#D39017",
        label="mean continuous score Q",
    )
    ax.axhline(0, color="#333333", lw=1.2)
    ax.axhline(0.50, color="#555555", lw=1.1, ls="--", label="cycle majority")
    ax.set(
        title="Ordered-cycle incidence and continuous strength",
        ylabel="registered unitless value",
        xticks=position,
        xticklabels=labels,
        ylim=(-1.05, 1.05),
    )
    ax.legend(fontsize=9)
    for target in axes.flat:
        target.grid(axis="y", color="#dddddd", lw=0.7, alpha=0.7)
        target.spines[["top", "right"]].set_visible(False)
    fig.savefig(FIGURE_PNG, dpi=180)
    fig.savefig(FIGURE_SVG)
    plt.close(fig)


def main() -> None:
    if digest(PROTOCOL, "sha256") != PROTOCOL_SHA256:
        raise RuntimeError("Q38 protocol hash changed")
    if digest(FIDELITY, "sha256") != FIDELITY_SHA256:
        raise RuntimeError("Q38 fidelity hash changed")
    build_caches()
    derived = np.load(DERIVED)
    closure = derived["closure"]
    connected = np.load(CONNECTED, mmap_mode="r")
    eligible, coherence = complete_loops(closure)

    rows: list[dict[str, object]] = []
    represented_seeds: set[int] = set()
    represented_lineages: set[tuple[int, int]] = set()
    for seed in range(100):
        for pair in np.flatnonzero(eligible[seed]):
            pair = int(pair)
            control_pair = pair_control(eligible, seed, pair)
            if control_pair is None:
                continue
            threshold = float(np.quantile(closure[0, seed, :250, pair], 0.20))
            for time in event_times(closure[0, seed, :, pair], threshold):
                specifications = {
                    "exact": (0, seed, pair, time),
                    "time": (0, seed, pair, shifted_time(time)),
                    "pair": (0, seed, control_pair, time),
                    "network": (1, seed, pair, time),
                }
                row: dict[str, object] = {
                    "seed": seed,
                    "source_pair": pair,
                    "time": time,
                    "pair_control": control_pair,
                    "development_circulation": float(coherence[seed, pair]),
                    "development_q20": threshold,
                }
                for variant, specification in specifications.items():
                    metrics = cycle_metrics(
                        *specification,
                        closure=closure,
                        connected=connected,
                    )
                    row.update(
                        {f"{variant}_{key}": value for key, value in metrics.items()}
                    )
                rows.append(row)
                represented_seeds.add(seed)
                represented_lineages.add((seed, pair))
    if not rows:
        raise RuntimeError("Q38 produced no events")

    with gzip.open(EVENTS, "wt", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    variants = ("exact", "time", "pair", "network")
    summary = {variant: summarize(rows, variant) for variant in variants}
    bootstrap: dict[str, object] = {
        "cycle_above_half": cluster_probability(
            rows, "exact_cycle", null_value=0.50
        ),
        "cycle_vs_controls": {
            variant: cluster_probability(
                rows, "exact_cycle", f"{variant}_cycle"
            )
            for variant in ("time", "pair", "network")
        },
        "score_vs_controls": {
            variant: cluster_probability(
                rows, "exact_cycle_score", f"{variant}_cycle_score"
            )
            for variant in ("time", "pair", "network")
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
    gates = {
        "events_cycle_ge_0_55": exact["cycle_fraction"] >= 0.55,
        "lineages_cycle_ge_half_ge_0_55": (
            exact["lineages_cycle_ge_half_fraction"] >= 0.55
        ),
        "bootstrap_cycle_above_half_ge_0_99": (
            bootstrap["cycle_above_half"] >= 0.99
        ),
        "median_score_ge_0_25": exact["cycle_score_median"] >= 0.25,
        "cycle_beats_controls_by_0_10": all(
            exact["cycle_fraction"] >= summary[v]["cycle_fraction"] + 0.10
            for v in ("time", "pair", "network")
        ),
        "score_beats_controls_by_0_10": all(
            exact["cycle_score_mean"] >= summary[v]["cycle_score_mean"] + 0.10
            for v in ("time", "pair", "network")
        ),
        "bootstrap_cycle_controls_ge_0_95": all(
            bootstrap["cycle_vs_controls"][v] >= 0.95
            for v in ("time", "pair", "network")
        ),
        "bootstrap_score_controls_ge_0_95": all(
            bootstrap["score_vs_controls"][v] >= 0.95
            for v in ("time", "pair", "network")
        ),
    }
    timing_support = bool(
        np.isfinite(exact["j_return_completed_median"])
        and 6 <= exact["j_return_completed_median"] <= 10
    )
    full_pass = eligibility_pass and all(gates.values())
    controlled_signal = eligibility_pass and all(
        bootstrap[f"{metric}_vs_controls"][variant] >= 0.95
        for metric in ("cycle", "score")
        for variant in ("time", "pair", "network")
    )
    if not eligibility_pass:
        verdict = "INCONCLUSIVE — ELIGIBILITY"
    elif full_pass:
        verdict = "FIXED-ANCHOR A→B→A CYCLE REPLICATED"
    elif controlled_signal:
        verdict = "ORDERED CYCLE SIGNAL, INCOMPLETE"
    else:
        verdict = "NOT REPLICATED"

    result = {
        "test_id": TEST_ID,
        "date": "2026-07-27",
        "design": "prospective cross-archive on untouched pure_mimic",
        "source": {
            "doi": "10.5281/zenodo.16753415",
            "archive": ARCHIVE_NAME,
            "archive_md5": ARCHIVE_MD5,
            "branches": list(BRANCHES),
            "shape": list(closure.shape),
        },
        "frozen_hashes": {
            "protocol_sha256": PROTOCOL_SHA256,
            "fidelity_sha256": FIDELITY_SHA256,
        },
        "eligibility": eligibility,
        "eligibility_pass": eligibility_pass,
        "summary": summary,
        "bootstrap": bootstrap,
        "gates": gates,
        "timing_support_6_to_10": timing_support,
        "full_pass": full_pass,
        "verdict": verdict,
        "boundaries": [
            "A connected-tensor orientation cycle is not automatically physical Phase B.",
            "Target is a deterministic simulator, not hardware.",
            "The archive is untouched in-project but belongs to the existing public source family.",
        ],
    }
    RESULTS.write_text(
        json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8"
    )
    make_figure(rows, summary, verdict)
    print(json.dumps(result, indent=2, allow_nan=True), flush=True)


if __name__ == "__main__":
    main()

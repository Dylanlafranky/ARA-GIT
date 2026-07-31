"""Q52 whole-sphere external ARA continuation test.

The immutable 0--499 history is retained from Q39. Slice-499 pure
single-excitation states are reconstructed from the stored pair reductions,
then continued under eight predeclared valid c2 coupling-order families.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import os
import pathlib
from collections import Counter, defaultdict

import h5py
import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".mplconfig"))
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt  # noqa: E402

import q49_external_time_vector as q49  # noqa: E402
import q50_same_lineage_external_flip_diagnostic as q50  # noqa: E402
from q27_ara9_network_reconstruction_test import (  # noqa: E402
    density_batch_to_closure,
)


TEST_ID = "Q52-WHOLE-SPHERE-CONTINUATION-v1"
DATA = HERE / "public_data" / "q39_information3_strongmax"
SOURCE = DATA / "unnati_submit_12_pure_strongmax.hdf5"
DERIVED = DATA / "q39_derived_cache.npz"
PROTOCOL = HERE / "Q52_WHOLE_SPHERE_CONTINUATION_PROTOCOL_v1_FROZEN.md"
RESULTS = HERE / "Q52_WHOLE_SPHERE_CONTINUATION_RESULTS.json"
BINS = HERE / "Q52_WHOLE_SPHERE_CONTINUATION_BINS.csv.gz"
SEED_RESULTS = HERE / "Q52_WHOLE_SPHERE_CONTINUATION_SEEDS.csv"
FIGURE = HERE / "Q52_WHOLE_SPHERE_CONTINUATION.png"

EXPECTED_PROTOCOL_SHA256 = (
    "64146a33f9ffec9df87d777e11cabdb7a095f3e0527edb9049fec6d088ed73da"
)
ARCHIVE_MD5 = "11b5f14ba185a9901f6a85bd31497d71"
GENERATOR_COMMIT = "2b49f27420b8ce8a12b4e6afac4ce5fe62664c68"

BRANCH = "c2_2local connectivity"
ORDERING = "ordering seed strongest_maximizes"
SOURCE_SEEDS = tuple(range(50))
HISTORY_SLICES = 500
EXTENSION_STEPS = 1_500
TOTAL_SLICES = HISTORY_SLICES + EXTENSION_STEPS
BIN_WIDTH = 50
TIME_EDGES = np.arange(0, TOTAL_SLICES + 1, BIN_WIDTH, dtype=np.int32)
PAIR_RECONSTRUCTION_LIMIT = 5e-6
MIN_FAMILY_SEEDS = 20
MIN_FAMILY_LINEAGES = 100
MIN_SEED_LINEAGES = 3
MIN_EXTENSION_BINS = 3
PRIMARY_RECOVERY = 0.25
BOOTSTRAP_DRAWS = 5_000
BOOTSTRAP_BASE_SEED = 520052
EPS = 1e-15

ORDER_A = np.asarray(
    [[9, 10], [1, 2], [3, 4], [0, 11], [5, 6], [7, 8]],
    dtype=np.int8,
)
ORDER_B = np.asarray(
    [[0, 1], [10, 11], [2, 3], [6, 7], [4, 5], [8, 9]],
    dtype=np.int8,
)
FAMILIES = (
    "fixed_A",
    "fixed_B",
    "alternating_AB",
    "alternating_BA",
    "random_520101",
    "random_520102",
    "random_520103",
    "random_520104",
)
ESTIMATORS = ("circle", "centroid", "extrema")


def digest(path: pathlib.Path, algorithm: str = "sha256") -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def pair_rho(amplitudes: np.ndarray, i: int, j: int) -> np.ndarray:
    total = float(np.sum(np.abs(amplitudes) ** 2))
    rho = np.zeros((4, 4), dtype=np.complex128)
    rho[0, 0] = total - abs(amplitudes[i]) ** 2 - abs(amplitudes[j]) ** 2
    rho[1, 1] = abs(amplitudes[j]) ** 2
    rho[2, 2] = abs(amplitudes[i]) ** 2
    rho[1, 2] = amplitudes[j] * np.conj(amplitudes[i])
    rho[2, 1] = np.conj(rho[1, 2])
    return rho


def reconstruct_amplitudes(
    pair_group: h5py.Group, pairs: np.ndarray
) -> tuple[np.ndarray, float]:
    populations = np.zeros(12, dtype=np.float64)
    for qubit in range(12):
        other = 1 if qubit == 0 else 0
        i, j = sorted((qubit, other))
        rho = np.asarray(pair_group[str((i, j))][()], dtype=np.complex128)
        if qubit == i:
            populations[qubit] = float((rho[2, 2] + rho[3, 3]).real)
        else:
            populations[qubit] = float((rho[1, 1] + rho[3, 3]).real)

    anchor = int(np.argmax(populations))
    amplitudes = np.zeros(12, dtype=np.complex128)
    amplitudes[anchor] = math.sqrt(max(populations[anchor], 0.0))
    for qubit in range(12):
        if qubit == anchor:
            continue
        i, j = sorted((anchor, qubit))
        rho = np.asarray(pair_group[str((i, j))][()], dtype=np.complex128)
        if anchor < qubit:
            amplitudes[qubit] = rho[1, 2] / amplitudes[anchor]
        else:
            amplitudes[qubit] = np.conj(rho[1, 2]) / amplitudes[anchor]

    maximum_error = 0.0
    for i, j in pairs:
        expected = np.asarray(pair_group[str((int(i), int(j)))][()])
        maximum_error = max(
            maximum_error,
            float(np.max(np.abs(pair_rho(amplitudes, int(i), int(j)) - expected))),
        )
    return amplitudes, maximum_error


def load_start_states(
    pairs: np.ndarray,
) -> tuple[np.ndarray, dict[str, float | int]]:
    states = np.empty((len(SOURCE_SEEDS), 12), dtype=np.complex128)
    errors = np.empty(len(SOURCE_SEEDS), dtype=np.float64)
    traces = np.empty(len(SOURCE_SEEDS), dtype=np.float64)
    with h5py.File(SOURCE, "r") as handle:
        root = handle[f"/12 qubits/{BRANCH}/unitary energy subspace 1"]
        for index, seed in enumerate(SOURCE_SEEDS):
            group = root[f"unitary seed {seed}"][ORDERING]["two_qubit_dms"]["499"]
            states[index], errors[index] = reconstruct_amplitudes(group, pairs)
            traces[index] = float(np.sum(np.abs(states[index]) ** 2))
    return states, {
        "source_seeds": len(SOURCE_SEEDS),
        "maximum_pair_reconstruction_error": float(np.max(errors)),
        "median_pair_reconstruction_error": float(np.median(errors)),
        "minimum_reconstructed_trace": float(np.min(traces)),
        "maximum_reconstructed_trace": float(np.max(traces)),
    }


def family_sequence(name: str) -> np.ndarray:
    if name == "fixed_A":
        return np.zeros(EXTENSION_STEPS, dtype=np.int8)
    if name == "fixed_B":
        return np.ones(EXTENSION_STEPS, dtype=np.int8)
    if name == "alternating_AB":
        return np.arange(EXTENSION_STEPS, dtype=np.int32).astype(np.int8) % 2
    if name == "alternating_BA":
        return 1 - np.arange(EXTENSION_STEPS, dtype=np.int32).astype(np.int8) % 2
    if name.startswith("random_"):
        seed = int(name.rsplit("_", 1)[-1])
        return np.random.default_rng(seed).integers(
            0, 2, size=EXTENSION_STEPS, dtype=np.int8
        )
    raise ValueError(name)


def continue_states(
    initial: np.ndarray, sequence: np.ndarray
) -> tuple[np.ndarray, dict[str, float]]:
    amplitudes = np.asarray(initial, dtype=np.complex128).copy()
    history = np.empty(
        (amplitudes.shape[0], EXTENSION_STEPS, amplitudes.shape[1]),
        dtype=np.complex128,
    )
    theta = math.pi / 15.0
    cosine, sine = math.cos(theta), math.sin(theta)
    initial_norm = np.sum(np.abs(amplitudes) ** 2, axis=1)
    for time_index, choice in enumerate(sequence):
        order = ORDER_A if choice == 0 else ORDER_B
        old = amplitudes.copy()
        for i, j in order:
            amplitudes[:, i] = cosine * old[:, i] + sine * old[:, j]
            amplitudes[:, j] = -sine * old[:, i] + cosine * old[:, j]
        history[:, time_index] = amplitudes
    final_norm = np.sum(np.abs(amplitudes) ** 2, axis=1)
    return history, {
        "maximum_absolute_norm_drift": float(np.max(np.abs(final_norm - initial_norm))),
        "median_absolute_norm_drift": float(np.median(np.abs(final_norm - initial_norm))),
    }


def states_to_closure(states: np.ndarray, pairs: np.ndarray) -> np.ndarray:
    output = np.empty(
        (states.shape[0], states.shape[1], len(pairs)), dtype=np.float32
    )
    pair_i = pairs[:, 0].astype(np.int64)
    pair_j = pairs[:, 1].astype(np.int64)
    chunk = 20
    for left in range(0, states.shape[1], chunk):
        right = min(states.shape[1], left + chunk)
        selected = states[:, left:right].reshape(-1, 12)
        count = selected.shape[0]
        ai = selected[:, pair_i]
        aj = selected[:, pair_j]
        rho = np.zeros((count, len(pairs), 4, 4), dtype=np.complex128)
        total = np.sum(np.abs(selected) ** 2, axis=1)[:, None]
        rho[:, :, 0, 0] = total - np.abs(ai) ** 2 - np.abs(aj) ** 2
        rho[:, :, 1, 1] = np.abs(aj) ** 2
        rho[:, :, 2, 2] = np.abs(ai) ** 2
        rho[:, :, 1, 2] = aj * np.conj(ai)
        rho[:, :, 2, 1] = np.conj(rho[:, :, 1, 2])
        closure, _ = density_batch_to_closure(rho.reshape(-1, 4, 4))
        output[:, left:right] = closure.reshape(
            states.shape[0], right - left, len(pairs)
        )
    return output


def fixed_lineages(
    events: list[dict[str, int | float | str]],
) -> tuple[set[tuple[int, int]], dict[tuple[int, int], list[dict[str, object]]]]:
    grouped: dict[tuple[int, int], list[dict[str, object]]] = defaultdict(list)
    for row in events:
        grouped[(int(row["seed"]), int(row["pair_index"]))].append(row)
    fixed: set[tuple[int, int]] = set()
    for key, rows in grouped.items():
        historical = sum(int(row["current_end"]) < 250 for row in rows)
        continuation = sum(int(row["current_start"]) >= 500 for row in rows)
        if historical >= 3 and continuation >= 3:
            fixed.add(key)
    return fixed, grouped


def binned_coordinate(
    events: list[dict[str, object]],
    estimator: str,
) -> list[dict[str, float | int]]:
    output: list[dict[str, float | int]] = []
    for left, right in zip(TIME_EDGES[:-1], TIME_EDGES[1:]):
        selected = [
            row
            for row in events
            if left <= int(row["current_start"]) < right
        ]
        summary = q50.aggregate_coordinate(selected, estimator)
        if selected:
            movement = float(
                np.mean(
                    [
                        np.linalg.norm(q50.vector(row, estimator))
                        for row in selected
                    ]
                )
            )
        else:
            movement = math.nan
        output.append(
            {
                "left": int(left),
                "right": int(right),
                "mid": float((left + right) / 2.0),
                **summary,
                "mean_relative_movement": movement,
            }
        )
    return output


def classify_bins(
    bins: list[dict[str, float | int]],
) -> dict[str, object]:
    x = np.asarray([float(row["x"]) for row in bins], dtype=np.float64)
    movement = np.asarray(
        [float(row["mean_relative_movement"]) for row in bins], dtype=np.float64
    )
    finite = np.isfinite(x) & np.isfinite(movement)
    historical = finite & np.asarray([int(row["right"]) <= 250 for row in bins])
    extension = finite & np.asarray([int(row["left"]) >= 500 for row in bins])
    baseline = (
        float(np.median(movement[historical])) if np.any(historical) else math.nan
    )
    low_history = np.flatnonzero(historical & (x <= 0.5))
    high = np.flatnonzero(finite & (x >= 1.5))
    witness: list[int] | None = None
    for low in low_history:
        later_high = high[high > low]
        if not later_high.size:
            continue
        high_index = int(later_high[0])
        later_low = np.flatnonzero(
            extension
            & (x <= 0.5)
            & (np.arange(len(bins), dtype=np.int32) > high_index)
        )
        if later_low.size:
            witness = [int(low), high_index, int(later_low[0])]
            break

    geometric_return = witness is not None
    return_ratio = math.nan
    if witness is not None and baseline > EPS:
        return_ratio = float(movement[witness[2]] / baseline)
    active_return = bool(
        geometric_return
        and math.isfinite(return_ratio)
        and return_ratio >= PRIMARY_RECOVERY
    )

    extension_indices = np.flatnonzero(extension)
    last = extension_indices[-3:] if extension_indices.size >= 3 else np.asarray([])
    final_x = float(np.median(x[last])) if last.size else math.nan
    final_ratio = (
        float(np.median(movement[last]) / baseline)
        if last.size and baseline > EPS
        else math.nan
    )
    settling = bool(
        not geometric_return
        and math.isfinite(final_x)
        and math.isfinite(final_ratio)
        and final_x >= 1.5
        and final_ratio <= 0.10
    )
    return {
        "finite_historical_bins": int(np.sum(historical)),
        "finite_extension_bins": int(np.sum(extension)),
        "baseline_movement": baseline,
        "geometric_return": geometric_return,
        "active_return": active_return,
        "return_movement_ratio": return_ratio,
        "return_at_10pct": bool(
            geometric_return and math.isfinite(return_ratio) and return_ratio >= 0.10
        ),
        "return_at_50pct": bool(
            geometric_return and math.isfinite(return_ratio) and return_ratio >= 0.50
        ),
        "witness_bin_indices": witness,
        "final_three_median_x": final_x,
        "final_three_movement_ratio": final_ratio,
        "one_way_settling": settling,
        "minimum_x": float(np.nanmin(x)) if np.any(np.isfinite(x)) else math.nan,
        "maximum_x": float(np.nanmax(x)) if np.any(np.isfinite(x)) else math.nan,
    }


def seed_classifications(
    grouped: dict[tuple[int, int], list[dict[str, object]]],
    fixed: set[tuple[int, int]],
    family: str,
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for seed in SOURCE_SEEDS:
        keys = [key for key in fixed if key[0] == seed]
        rows = [row for key in keys for row in grouped[key]]
        bins = binned_coordinate(rows, "circle")
        result = classify_bins(bins)
        eligible = bool(
            len(keys) >= MIN_SEED_LINEAGES
            and int(result["finite_extension_bins"]) >= MIN_EXTENSION_BINS
        )
        output.append(
            {
                "family": family,
                "source_seed": seed,
                "fixed_lineages": len(keys),
                "eligible": int(eligible),
                **result,
            }
        )
    return output


def proportion_bootstrap(
    rows: list[dict[str, object]], key: str, seed: int
) -> dict[str, object]:
    values = np.asarray(
        [float(bool(row[key])) for row in rows if bool(int(row["eligible"]))],
        dtype=np.float64,
    )
    if not values.size:
        return {
            "eligible_seeds": 0,
            "fraction": math.nan,
            "ci95": [math.nan, math.nan],
        }
    rng = np.random.default_rng(seed)
    chosen = rng.integers(0, values.size, size=(BOOTSTRAP_DRAWS, values.size))
    draws = np.mean(values[chosen], axis=1)
    return {
        "eligible_seeds": int(values.size),
        "fraction": float(np.mean(values)),
        "ci95": [float(value) for value in np.quantile(draws, [0.025, 0.975])],
    }


def write_csv_gz(path: pathlib.Path, rows: list[dict[str, object]]) -> None:
    with gzip.open(path, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_csv(path: pathlib.Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_figure(
    family_results: list[dict[str, object]],
    bin_rows: list[dict[str, object]],
    verdict: str,
) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    figure, axes = plt.subplots(2, 2, figsize=(16, 10), constrained_layout=True)
    colours = plt.cm.tab10(np.linspace(0, 1, len(FAMILIES)))

    ax = axes[0, 0]
    for colour, family in zip(colours, FAMILIES):
        rows = [
            row
            for row in bin_rows
            if row["family"] == family and row["estimator"] == "circle"
        ]
        ax.plot(
            [row["mid"] for row in rows],
            [row["x"] for row in rows],
            lw=1.5,
            color=colour,
            label=family,
        )
    ax.axhline(0, color="#4C78A8", ls=":")
    ax.axhline(1, color="#222222", lw=1.2, label="1.0 ridge")
    ax.axhline(2, color="#E45756", ls=":")
    ax.axvline(500, color="#555555", ls="--", label="continuation begins")
    ax.set(
        xlim=(0, TOTAL_SLICES),
        ylim=(-0.05, 2.05),
        xlabel="source / continued slice",
        ylabel="external directional ARA x",
        title="Whole-sphere external direction",
    )
    ax.legend(fontsize=7, ncol=3)

    ax = axes[0, 1]
    for colour, family in zip(colours, FAMILIES):
        rows = [
            row
            for row in bin_rows
            if row["family"] == family and row["estimator"] == "circle"
        ]
        base = next(
            (
                float(item["primary"]["baseline_movement"])
                for item in family_results
                if item["family"] == family
            ),
            math.nan,
        )
        ratios = [
            float(row["mean_relative_movement"]) / base
            if base > EPS and math.isfinite(float(row["mean_relative_movement"]))
            else math.nan
            for row in rows
        ]
        ax.plot([row["mid"] for row in rows], ratios, color=colour, lw=1.4)
    ax.axhline(0.25, color="#222222", ls="--", label="active-return floor")
    ax.axhline(0.10, color="#888888", ls=":", label="settling ceiling")
    ax.axvline(500, color="#555555", ls="--")
    ax.set(
        xlim=(0, TOTAL_SLICES),
        ylim=(0, 2),
        xlabel="source / continued slice",
        ylabel="movement / historical baseline",
        title="Does movement recover after reversal?",
    )
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    matrix = []
    for family in FAMILIES:
        rows = [
            row
            for row in bin_rows
            if row["family"] == family and row["estimator"] == "circle"
        ]
        matrix.append([float(row["x"]) for row in rows])
    image = ax.imshow(
        np.asarray(matrix),
        aspect="auto",
        origin="upper",
        vmin=0,
        vmax=2,
        cmap="coolwarm",
        extent=(0, TOTAL_SLICES, len(FAMILIES), 0),
    )
    ax.axvline(500, color="white", ls="--", lw=1.2)
    ax.set(
        yticks=np.arange(len(FAMILIES)) + 0.5,
        yticklabels=FAMILIES,
        xlabel="source / continued slice",
        title="Continuation-family ARA map",
    )
    figure.colorbar(image, ax=ax, label="external ARA x")

    ax = axes[1, 1]
    x = np.arange(len(FAMILIES))
    active = [
        float(row["seed_active_return"]["fraction"]) for row in family_results
    ]
    settle = [float(row["seed_settling"]["fraction"]) for row in family_results]
    ax.bar(x - 0.18, active, width=0.36, color="#2A9D8F", label="active return")
    ax.bar(x + 0.18, settle, width=0.36, color="#E76F51", label="one-way settling")
    ax.axhline(0.5, color="#222222", ls="--")
    ax.set(
        xticks=x,
        xticklabels=FAMILIES,
        ylim=(0, 1),
        ylabel="eligible source-seed fraction",
        title="Source-seed outcomes within each future",
    )
    ax.tick_params(axis="x", rotation=35)
    ax.legend()

    figure.suptitle(
        f"Q52 — whole-sphere 0→2→0 continuation\n{verdict}",
        fontsize=16,
        fontweight="bold",
    )
    figure.savefig(FIGURE, dpi=180)
    plt.close(figure)


def main() -> None:
    if digest(PROTOCOL) != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError("Frozen Q52 protocol hash changed")
    with np.load(DERIVED) as source_cache:
        base_closure = np.asarray(
            source_cache["closure"][list(SOURCE_SEEDS)], dtype=np.float32
        )
        pairs = np.asarray(source_cache["pairs"], dtype=np.int8)

    initial, reconstruction = load_start_states(pairs)
    if (
        float(reconstruction["maximum_pair_reconstruction_error"])
        > PAIR_RECONSTRUCTION_LIMIT
    ):
        raise RuntimeError("Slice-499 amplitude reconstruction failed")

    family_results: list[dict[str, object]] = []
    all_bins: list[dict[str, object]] = []
    all_seed_rows: list[dict[str, object]] = []
    norm_results: dict[str, dict[str, float]] = {}

    for family_index, family in enumerate(FAMILIES):
        print(f"[{family_index + 1}/{len(FAMILIES)}] {family}", flush=True)
        sequence = family_sequence(family)
        state_history, norm_qc = continue_states(initial, sequence)
        norm_results[family] = norm_qc
        extension_closure = states_to_closure(state_history, pairs)
        closure = np.concatenate((base_closure, extension_closure), axis=1)
        centres, extraction = q49.extract_centres(closure, pairs)
        events = q49.build_events(centres)
        fixed, grouped = fixed_lineages(events)
        fixed_events = [row for key in fixed for row in grouped[key]]

        estimator_payload: dict[str, object] = {}
        for estimator in ESTIMATORS:
            bins = binned_coordinate(fixed_events, estimator)
            classification = classify_bins(bins)
            estimator_payload[estimator] = classification
            for row in bins:
                all_bins.append(
                    {
                        "family": family,
                        "estimator": estimator,
                        **row,
                    }
                )

        seed_rows = seed_classifications(grouped, fixed, family)
        all_seed_rows.extend(seed_rows)
        represented = len(
            {
                int(row["seed"])
                for key in fixed
                for row in grouped[key]
            }
        )
        primary = estimator_payload["circle"]
        eligible = bool(
            represented >= MIN_FAMILY_SEEDS
            and len(fixed) >= MIN_FAMILY_LINEAGES
            and int(primary["finite_extension_bins"]) >= MIN_EXTENSION_BINS
        )
        active_boot = proportion_bootstrap(
            seed_rows, "active_return", BOOTSTRAP_BASE_SEED + family_index
        )
        settle_boot = proportion_bootstrap(
            seed_rows,
            "one_way_settling",
            BOOTSTRAP_BASE_SEED + 100 + family_index,
        )
        family_results.append(
            {
                "family": family,
                "eligible": eligible,
                "represented_source_seeds": represented,
                "fixed_lineages": len(fixed),
                "centres": len(centres),
                "events": len(events),
                "extraction": extraction,
                "primary": primary,
                "estimator_sensitivity": estimator_payload,
                "seed_active_return": active_boot,
                "seed_settling": settle_boot,
                "continuation_order_counts": {
                    "A": int(np.sum(sequence == 0)),
                    "B": int(np.sum(sequence == 1)),
                },
                "norm_qc": norm_qc,
            }
        )

    eligible_families = [row for row in family_results if bool(row["eligible"])]
    active_families = [
        row
        for row in eligible_families
        if bool(row["primary"]["active_return"])
    ]
    settling_families = [
        row
        for row in eligible_families
        if bool(row["primary"]["one_way_settling"])
    ]
    extinction_families = [
        row for row in family_results if not bool(row["eligible"])
    ]

    eligible_seed_rows = [
        row for row in all_seed_rows if bool(int(row["eligible"]))
    ]
    by_source: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in eligible_seed_rows:
        by_source[int(row["source_seed"])].append(row)

    def pooled_bootstrap(key: str, seed: int) -> dict[str, object]:
        source_values = np.asarray(
            [
                np.mean([float(bool(row[key])) for row in rows])
                for _, rows in sorted(by_source.items())
            ],
            dtype=np.float64,
        )
        if not source_values.size:
            return {
                "source_seed_clusters": 0,
                "fraction": math.nan,
                "ci95": [math.nan, math.nan],
            }
        rng = np.random.default_rng(seed)
        chosen = rng.integers(
            0,
            source_values.size,
            size=(BOOTSTRAP_DRAWS, source_values.size),
        )
        draws = np.mean(source_values[chosen], axis=1)
        return {
            "source_seed_clusters": int(source_values.size),
            "fraction": float(np.mean(source_values)),
            "ci95": [
                float(value) for value in np.quantile(draws, [0.025, 0.975])
            ],
        }

    pooled_active = pooled_bootstrap("active_return", 520152)
    pooled_settle = pooled_bootstrap("one_way_settling", 520153)
    active_types = {
        "fixed" if row["family"].startswith("fixed") else
        "alternating" if row["family"].startswith("alternating") else
        "random"
        for row in active_families
    }
    complete_supported = bool(
        len(active_families) >= 5
        and active_types == {"fixed", "alternating", "random"}
        and float(pooled_active["ci95"][0]) > 0.50
    )
    settling_supported = bool(
        len(settling_families) >= 5
        and float(pooled_settle["ci95"][0]) > 0.50
    )
    driver_dependent = bool(
        len(active_families) >= 2 and len(settling_families) >= 2
    )
    if driver_dependent:
        verdict = "DRIVER-DEPENDENT"
    elif complete_supported:
        verdict = "COMPLETE 0→2→0 RETURN SUPPORTED"
    elif settling_supported:
        verdict = "ONE-WAY SETTLING SUPPORTED"
    else:
        verdict = "UNRESOLVED / MIXED"

    results = {
        "test_id": TEST_ID,
        "verdict": verdict,
        "measured_object": (
            "external centreline direction of complete internal ARA circles"
        ),
        "target": "whole-sphere 0→2→0, not local pi/15 rotation",
        "source": {
            "archive": SOURCE.name,
            "archive_md5": ARCHIVE_MD5,
            "derived_cache": DERIVED.name,
            "derived_sha256": digest(DERIVED),
            "generator_commit": GENERATOR_COMMIT,
            "branch": BRANCH,
            "ordering_history": ORDERING,
            "source_seeds": list(SOURCE_SEEDS),
            "history_slices": HISTORY_SLICES,
            "extension_steps": EXTENSION_STEPS,
            "total_slices": TOTAL_SLICES,
        },
        "frozen_protocol": {
            "path": str(PROTOCOL),
            "sha256": digest(PROTOCOL),
        },
        "source_reconstruction": reconstruction,
        "continuation": {
            "families": list(FAMILIES),
            "valid_partitions": {
                "A": ORDER_A.tolist(),
                "B": ORDER_B.tolist(),
            },
            "local_rotation_radians": math.pi / 15.0,
            "local_rotation_degrees": 12.0,
            "local_rotation_role": "source machinery; absent from external ARA score",
            "norm_qc": norm_results,
        },
        "family_results": family_results,
        "pooled_source_seed_active_return": pooled_active,
        "pooled_source_seed_settling": pooled_settle,
        "gates": {
            "eligible_families": len(eligible_families),
            "active_return_families": len(active_families),
            "settling_families": len(settling_families),
            "cycle_extinction_families": len(extinction_families),
            "active_family_types": sorted(active_types),
            "complete_return_supported": complete_supported,
            "one_way_settling_supported": settling_supported,
            "driver_dependent": driver_dependent,
        },
        "outcome_counts": dict(
            Counter(
                "active_return"
                if bool(row["primary"]["active_return"])
                else "one_way_settling"
                if bool(row["primary"]["one_way_settling"])
                else "cycle_extinction"
                if not bool(row["eligible"])
                else "other"
                for row in family_results
            )
        ),
        "boundaries": [
            "The local pi/15 interaction is a simulator parameter, not an ARA prediction.",
            "The continuation ensemble comprises declared valid possible futures because the original Python RNG state was not deposited.",
            "The source is a deterministic quantum-network simulator, not quantum-hardware measurements.",
            "An orientation-only return is not counted as an active return.",
        ],
    }

    RESULTS.write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_csv_gz(BINS, all_bins)
    write_csv(SEED_RESULTS, all_seed_rows)
    make_figure(family_results, all_bins, verdict)
    print(json.dumps({
        "verdict": verdict,
        "gates": results["gates"],
        "pooled_active": pooled_active,
        "pooled_settle": pooled_settle,
        "reconstruction": reconstruction,
    }, indent=2))


if __name__ == "__main__":
    main()

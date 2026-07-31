"""Prospective Q41 test of the cadence-defined Ba strand reversal rule."""

from __future__ import annotations

import concurrent.futures
import csv
import gzip
import hashlib
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

import q40_return_flow_relation_reversal_test as base
from q40c_post_result_double_helix_projection_audit import fit_orbit


TEST_ID = "Q41-CADENCE-STRAND-REVERSAL-v1"
DATA = HERE / "public_data" / "q41_cadence_strand_inhomo_v1_random"
ARCHIVE_NAME = "unnati_submit_12_inhomo_v1_random.hdf5.zip"
HDF_NAME = "unnati_submit_12_inhomo_v1_random.hdf5"
ARCHIVE = DATA / ARCHIVE_NAME
SOURCE = DATA / HDF_NAME
ARCHIVE_MD5 = "f342ff3dda39915da3332db65cc7c2c8"
BRANCH = "c2_2local connectivity"

DERIVED = DATA / "q41_derived_cache.npz"
CONNECTED = DATA / "q41_connected_cache.npy"
PREDICTIONS = DATA / "q41_frozen_predictions.npz"
RESULTS = HERE / "Q41_CADENCE_STRAND_REVERSAL_RESULTS.json"
EVENTS = HERE / "Q41_CADENCE_STRAND_REVERSAL_CYCLES.csv.gz"
FIGURE_PNG = HERE / "Q41_CADENCE_STRAND_REVERSAL_DIAGNOSTICS.png"
FIGURE_SVG = HERE / "Q41_CADENCE_STRAND_REVERSAL_DIAGNOSTICS.svg"

FIDELITY = HERE / "Q41_CADENCE_STRAND_REVERSAL_FIDELITY_v1.md"
PROTOCOL = HERE / "Q41_CADENCE_STRAND_REVERSAL_PROTOCOL_v1_PRETARGET_FROZEN.md"
TARGET_LOCK = HERE / "Q41_TARGET_LOCK_v1_FROZEN.md"
EXPECTED_FIDELITY_SHA256 = (
    "fe1574a6afa6f440cb999d3fd07bf6113c674e15ee4b6e958cbc754370990646"
)
EXPECTED_PROTOCOL_SHA256 = (
    "325bc7ac959af0c5327e4d1b4566391d55806a18bf1a87516747cd021c3ef595"
)
EXPECTED_TARGET_LOCK_SHA256 = (
    "21480de729d8848a9b50e5db0c8c4e35f976a775f0df93a7d3cbdad8176460cf"
)

METHODS = ("q41", "q40", "forward", "persistence", "development_affine")
METHOD_LABELS = {
    "q41": "Q41 cadence + Ba",
    "q40": "Q40 visible rule",
    "forward": "Forward relation",
    "persistence": "Persistence",
    "development_affine": "Development affine",
}
BOOTSTRAP_SEED = 410027
BOOTSTRAP_DRAWS = 20_000
EPS = 1e-12


def digest(path: pathlib.Path, algorithm: str) -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def verify_freeze() -> dict[str, str]:
    hashes = {
        "fidelity_sha256": digest(FIDELITY, "sha256"),
        "protocol_sha256": digest(PROTOCOL, "sha256"),
        "target_lock_sha256": digest(TARGET_LOCK, "sha256"),
    }
    expected = {
        "fidelity_sha256": EXPECTED_FIDELITY_SHA256,
        "protocol_sha256": EXPECTED_PROTOCOL_SHA256,
        "target_lock_sha256": EXPECTED_TARGET_LOCK_SHA256,
    }
    if hashes != expected:
        raise RuntimeError(f"Frozen-document hash mismatch: {hashes}")
    return hashes


def ensure_source() -> None:
    if not ARCHIVE.exists():
        raise RuntimeError(f"Frozen target archive missing: {ARCHIVE}")
    archive_md5 = digest(ARCHIVE, "md5")
    if archive_md5 != ARCHIVE_MD5:
        raise RuntimeError(
            f"Archive MD5 mismatch: expected {ARCHIVE_MD5}, got {archive_md5}"
        )
    with zipfile.ZipFile(ARCHIVE) as zipped:
        matches = [
            item
            for item in zipped.infolist()
            if not item.is_dir() and pathlib.Path(item.filename).name == HDF_NAME
        ]
        if len(matches) != 1:
            raise RuntimeError(f"Expected one {HDF_NAME}, found {len(matches)}")
        expected_size = int(matches[0].file_size)
        if SOURCE.exists() and SOURCE.stat().st_size == expected_size:
            return
        if SOURCE.exists():
            SOURCE.unlink()
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
                [root[str(time_index)][name][()] for name in base.PAIR_NAMES]
            ).astype(np.complex128)
            closure[time_index], connected[time_index] = base.density_batch(rhos)
            if time_index in (0, 99, 199, 249, 299, 399, 499):
                for pair in (0, 13, 26, 39, 52, 65):
                    rho = rhos[pair]
                    qc[0] = max(qc[0], float(abs(np.trace(rho) - 1)))
                    qc[1] = max(qc[1], float(np.max(abs(rho - rho.conj().T))))
                    qc[2] = min(
                        qc[2],
                        float(
                            np.min(
                                np.linalg.eigvalsh((rho + rho.conj().T) / 2)
                            )
                        ),
                    )
                    qc[3] += 1
    return seed, closure, connected, qc


def build_caches(workers: int = 8) -> None:
    ensure_source()
    if DERIVED.exists() and CONNECTED.exists():
        print("using existing Q41 caches", flush=True)
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
                    f"cached {completed}/100 seeds "
                    f"({time.time() - started:.1f}s)",
                    flush=True,
                )
    connected.flush()
    np.savez_compressed(
        DERIVED,
        closure=closure,
        qc=qc,
        pairs=np.asarray(base.PAIRS, dtype=np.int8),
        branch=np.asarray(BRANCH),
    )


def cadence_family(u: np.ndarray, v: np.ndarray) -> tuple[str, dict]:
    fit = fit_orbit(u[250:499], v[250:499])
    if fit["posthoc_two_turn_7_5_family"]:
        family = "two_turn_7_5"
    elif fit["posthoc_one_turn_15_family"]:
        family = "one_turn_15"
    else:
        family = "other"
    clean = {
        key: value
        for key, value in fit.items()
        if key not in {"theta", "sample", "fitted"}
    }
    return family, clean


def prereveal_inventory(closure: np.ndarray) -> dict:
    counts: dict[str, int] = defaultdict(int)
    coherence_values = []
    occupancy_values = []
    development_cycles = 0
    evaluation_cycles = 0
    for seed in range(100):
        for pair in range(66):
            coord = base.coordinates(closure[seed, :, pair])
            if coord is None:
                counts["coordinate_unavailable"] += 1
                continue
            _u, _v, labels, direction, coherence, occupancy = coord
            counts["coordinate_available"] += 1
            coherence_values.append(float(coherence))
            occupancy_values.append(float(occupancy))
            if coherence < 0.80:
                counts["coherence_below_0_80"] += 1
                continue
            if occupancy < 0.05:
                counts["occupancy_below_0_05"] += 1
                continue
            counts["eligible_lineages"] += 1
            development_cycles += len(
                base.complete_windows(labels, direction, 0, 248)
            )
            evaluation_cycles += len(
                base.complete_windows(labels, direction, 250, 498)
            )
    return {
        **dict(counts),
        "development_cycles": development_cycles,
        "evaluation_cycles": evaluation_cycles,
        "coherence": {
            "minimum": float(np.min(coherence_values))
            if coherence_values
            else float("nan"),
            "median": float(np.median(coherence_values))
            if coherence_values
            else float("nan"),
            "maximum": float(np.max(coherence_values))
            if coherence_values
            else float("nan"),
        },
        "minimum_quadrant_occupancy": {
            "minimum": float(np.min(occupancy_values))
            if occupancy_values
            else float("nan"),
            "median": float(np.median(occupancy_values))
            if occupancy_values
            else float("nan"),
            "maximum": float(np.max(occupancy_values))
            if occupancy_values
            else float("nan"),
        },
    }


def prediction_stack(c1, c2, c3, q40_flag, strand_flag, affine):
    delta = c1 - c2
    forward = c3 + delta
    reverse = c3 - delta
    q41_flag = bool(q40_flag or strand_flag)
    return np.stack(
        (
            reverse if q41_flag else forward,
            reverse if q40_flag else forward,
            forward,
            c3,
            affine[0] * c1 + affine[1] * c2 + affine[2] * c3,
        ),
        axis=0,
    )


def prepare_predictions(closure: np.ndarray, connected: np.ndarray) -> str:
    if PREDICTIONS.exists():
        PREDICTIONS.unlink()
    (
        affine,
        affine_condition,
        affine_fit_method,
        development_cycles,
        _eligible,
        coordinate_cache,
    ) = base.fit_affine(closure, connected)
    metadata: dict[str, list] = defaultdict(list)
    visible_blocks, prediction_blocks = [], []
    family_counts: dict[str, int] = defaultdict(int)
    for (seed, pair), coord in coordinate_cache.items():
        u, v, labels, direction, coherence, occupancy = coord
        family, fit = cadence_family(u, v)
        family_counts[family] += 1
        for window in base.complete_windows(labels, direction, 250, 498):
            c1, c2, c3 = base.identities_for_window(
                connected, seed, pair, window, count=3
            )
            delta = c1 - c2
            forward = c3 + delta
            flag_cosine = float(
                np.sum(forward * c3)
                / (np.linalg.norm(forward) * np.linalg.norm(c3) + EPS)
            )
            q40_flag = flag_cosine < 0
            quadrants = [entry[0] for entry in window]
            q4 = int(quadrants[3])
            strand_flag = family == "two_turn_7_5" and q4 == 1
            q41_flag = bool(q40_flag or strand_flag)
            visible_blocks.append(np.stack((c1, c2, c3)))
            prediction_blocks.append(
                prediction_stack(
                    c1, c2, c3, q40_flag, strand_flag, affine
                )
            )
            metadata["seed"].append(seed)
            metadata["pair"].append(pair)
            metadata["direction"].append(direction)
            metadata["coherence"].append(coherence)
            metadata["occupancy"].append(occupancy)
            metadata["family"].append(family)
            metadata["period"].append(fit["angular_period_samples"])
            metadata["lag15_correlation"].append(
                fit["fixed_lag_15"]["coordinate_correlation"]
            )
            metadata["q40_flag"].append(int(q40_flag))
            metadata["strand_flag"].append(int(strand_flag))
            metadata["q41_flag"].append(int(q41_flag))
            metadata["flag_cosine"].append(flag_cosine)
            for index, (q, start, end) in enumerate(window, start=1):
                metadata[f"q{index}"].append(q)
                metadata[f"q{index}_start"].append(start)
                metadata[f"q{index}_end"].append(end)
            metadata["lineage_scale"].append(
                float(
                    np.median(
                        np.linalg.norm(
                            connected[seed, :250, pair], axis=(1, 2)
                        )
                    )
                )
            )
    if not prediction_blocks:
        raise RuntimeError("Q41 produced no evaluation cycles")
    payload = {key: np.asarray(value) for key, value in metadata.items()}
    payload.update(
        {
            "c_visible": np.asarray(visible_blocks, dtype=np.float32),
            "predictions": np.asarray(prediction_blocks, dtype=np.float32),
            "methods": np.asarray(METHODS),
            "affine_coefficients": affine,
            "affine_condition": np.asarray(affine_condition),
            "affine_fit_method": np.asarray(affine_fit_method),
            "development_cycles": np.asarray(development_cycles),
            "eligible_lineages": np.asarray(len(coordinate_cache)),
            "family_lineages_two_turn_7_5": np.asarray(
                family_counts["two_turn_7_5"]
            ),
            "family_lineages_one_turn_15": np.asarray(
                family_counts["one_turn_15"]
            ),
            "family_lineages_other": np.asarray(family_counts["other"]),
        }
    )
    np.savez_compressed(PREDICTIONS, **payload)
    prediction_sha = digest(PREDICTIONS, "sha256")
    print(f"frozen prediction SHA-256: {prediction_sha}", flush=True)
    return prediction_sha


def matrix_metrics(predicted: np.ndarray, actual: np.ndarray, scale: float):
    error = float(np.linalg.norm(predicted - actual))
    actual_norm = float(np.linalg.norm(actual))
    predicted_norm = float(np.linalg.norm(predicted))
    cosine = float(
        np.sum(predicted * actual) / (predicted_norm * actual_norm + EPS)
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
    if tuple(str(value) for value in frozen["methods"]) != METHODS:
        raise RuntimeError("Frozen method list changed")
    rows = []
    for index in range(len(frozen["seed"])):
        seed = int(frozen["seed"][index])
        pair = int(frozen["pair"][index])
        start = int(frozen["q4_start"][index])
        end = int(frozen["q4_end"][index])
        actual = np.mean(
            connected[seed, start : end + 1, pair],
            axis=0,
            dtype=np.float64,
        )
        c1, c2, c3 = np.asarray(
            frozen["c_visible"][index], dtype=np.float64
        )
        forward = c1 - c2 + c3
        target_orientation_cosine = float(
            np.sum(forward * actual)
            / (np.linalg.norm(forward) * np.linalg.norm(actual) + EPS)
        )
        row = {
            "cycle_id": index,
            "seed": seed,
            "pair_index": pair,
            "pair": base.PAIR_NAMES[pair],
            "family": str(frozen["family"][index]),
            "period": float(frozen["period"][index]),
            "lag15_correlation": float(frozen["lag15_correlation"][index]),
            "direction": int(frozen["direction"][index]),
            "q4": int(frozen["q4"][index]),
            "q4_start": start,
            "q4_end": end,
            "lineage_scale": float(frozen["lineage_scale"][index]),
            "q40_flag": int(frozen["q40_flag"][index]),
            "strand_flag": int(frozen["strand_flag"][index]),
            "q41_flag": int(frozen["q41_flag"][index]),
            "target_negative_orientation": int(
                target_orientation_cosine < 0
            ),
            "target_orientation_cosine": target_orientation_cosine,
            "target_norm": float(np.linalg.norm(actual)),
        }
        predictions = np.asarray(
            frozen["predictions"][index], dtype=np.float64
        )
        for method_index, method in enumerate(METHODS):
            for metric, value in matrix_metrics(
                predictions[method_index],
                actual,
                float(row["lineage_scale"]),
            ).items():
                row[f"{method}_{metric}"] = float(value)
        rows.append(row)
    return rows, frozen


def aggregate_rows(rows):
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


def bootstrap_advantage(seed_rows, baseline: str) -> dict:
    q41 = np.asarray([row["q41_scaled_error"] for row in seed_rows])
    control = np.asarray(
        [row[f"{baseline}_scaled_error"] for row in seed_rows]
    )
    difference = control - q41
    rng = np.random.default_rng(BOOTSTRAP_SEED + METHODS.index(baseline) * 31)
    indices = rng.integers(
        0, len(difference), size=(BOOTSTRAP_DRAWS, len(difference))
    )
    boot = np.mean(difference[indices], axis=1)
    return {
        "advantage": float(np.mean(difference)),
        "ci95": [
            float(np.quantile(boot, 0.025)),
            float(np.quantile(boot, 0.975)),
        ],
        "p_no_advantage": float(
            (np.sum(boot <= 0) + 1) / (BOOTSTRAP_DRAWS + 1)
        ),
        "seed_win_fraction": float(np.mean(difference > 0)),
    }


def confusion(rows, flag_name: str) -> dict:
    flag = np.asarray([bool(row[flag_name]) for row in rows])
    target = np.asarray(
        [bool(row["target_negative_orientation"]) for row in rows]
    )
    tp = int(np.sum(flag & target))
    fp = int(np.sum(flag & ~target))
    fn = int(np.sum(~flag & target))
    tn = int(np.sum(~flag & ~target))
    recall = tp / max(tp + fn, 1)
    specificity = tn / max(tn + fp, 1)
    return {
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "precision": tp / max(tp + fp, 1),
        "recall": recall,
        "specificity": specificity,
        "balanced_accuracy": (recall + specificity) / 2,
    }


def method_summary(rows, seed_rows) -> dict:
    output = {}
    for method in METHODS:
        output[method] = {}
        for metric in (
            "scaled_error",
            "absolute_error",
            "nrmse",
            "cosine",
            "closure_error",
        ):
            event = np.asarray([row[f"{method}_{metric}"] for row in rows])
            seed = np.asarray([row[f"{method}_{metric}"] for row in seed_rows])
            output[method][metric] = {
                "event_mean": float(np.mean(event)),
                "event_median": float(np.median(event)),
                "seed_balanced_mean": float(np.mean(seed)),
                "seed_balanced_median": float(np.median(seed)),
            }
    return output


def grouped_summary(rows) -> dict:
    output = {}
    for family in ("two_turn_7_5", "one_turn_15", "other"):
        output[family] = {}
        for q4 in range(4):
            selected = [
                row
                for row in rows
                if row["family"] == family and int(row["q4"]) == q4
            ]
            if not selected:
                continue
            output[family][str(q4)] = {
                "cycles": len(selected),
                "target_negative_fraction": float(
                    np.mean(
                        [
                            row["target_negative_orientation"]
                            for row in selected
                        ]
                    )
                ),
                "q40_flag_fraction": float(
                    np.mean([row["q40_flag"] for row in selected])
                ),
                "q41_flag_fraction": float(
                    np.mean([row["q41_flag"] for row in selected])
                ),
                "q41_minus_q40_scaled_error": float(
                    np.mean(
                        [
                            row["q41_scaled_error"]
                            - row["q40_scaled_error"]
                            for row in selected
                        ]
                    )
                ),
            }
    return output


def write_events(rows) -> None:
    with gzip.open(EVENTS, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_figure(
    closure: np.ndarray,
    rows,
    seed_rows,
    grouped,
    predictions,
) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(
        f"{TEST_ID} — frozen 7.5/15 cadence-defined Ba strand test",
        fontsize=18,
        fontweight="bold",
    )

    sample_seed = int(predictions["seed"][0])
    sample_pair = int(predictions["pair"][0])
    coord = base.coordinates(closure[sample_seed, :, sample_pair])
    u, v = coord[0][250:499], coord[1][250:499]
    fit = fit_orbit(u, v)
    axes[0, 0].plot(u, v, color="#4F79B8", lw=1.1, alpha=0.85)
    axes[0, 0].scatter(u[::15], v[::15], s=18, color="#D89B2B")
    axes[0, 0].axhline(0, color="#202936", lw=0.8)
    axes[0, 0].axvline(0, color="#202936", lw=0.8)
    axes[0, 0].set(
        title=(
            f"Visible closure plane; sample period "
            f"{fit['angular_period_samples']:.3f}"
        ),
        xlabel="closure side u",
        ylabel="closure flow v",
    )
    axes[0, 0].text(
        0.02,
        0.95,
        "Ba",
        transform=axes[0, 0].transAxes,
        ha="left",
        va="top",
        color="#D85C4A",
        fontweight="bold",
    )

    means = [
        np.mean([row[f"{method}_scaled_error"] for row in seed_rows])
        for method in METHODS
    ]
    colors = ["#D89B2B", "#4F79B8", "#8D99A6", "#AEB6BF", "#6A8F5B"]
    axes[0, 1].bar(
        [METHOD_LABELS[m] for m in METHODS], means, color=colors
    )
    axes[0, 1].tick_params(axis="x", rotation=24)
    axes[0, 1].set(
        title="Seed-balanced reconstruction error",
        ylabel="scaled error (lower is better)",
    )

    delta = np.asarray(
        [row["q40_scaled_error"] - row["q41_scaled_error"] for row in rows]
    )
    axes[1, 0].hist(delta, bins=80, color="#4F79B8", alpha=0.85)
    axes[1, 0].axvline(0, color="#202936", lw=1)
    axes[1, 0].set(
        title="Event-level Q41 advantage over Q40",
        xlabel="Q40 error − Q41 error (positive favours Q41)",
        ylabel="cycles",
    )

    labels, rates, counts = [], [], []
    for family in ("two_turn_7_5", "one_turn_15", "other"):
        for q4 in range(4):
            item = grouped.get(family, {}).get(str(q4))
            if item:
                labels.append(f"{family}\\nq{q4}")
                rates.append(item["target_negative_fraction"])
                counts.append(item["cycles"])
    bars = axes[1, 1].bar(
        range(len(labels)),
        rates,
        color=[
            "#D85C4A" if "two_turn_7_5" in label and "q1" in label
            else "#8D99A6"
            for label in labels
        ],
    )
    axes[1, 1].set_xticks(range(len(labels)), labels, rotation=34, ha="right")
    axes[1, 1].set(
        title="Hidden relation reversal by visible family and quadrant",
        ylabel="negative-orientation fraction",
        ylim=(0, 1),
    )
    for bar, count in zip(bars, counts):
        axes[1, 1].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f"n={count}",
            ha="center",
            va="bottom",
            fontsize=7,
            rotation=90,
        )

    for axis in axes.ravel():
        axis.grid(color="#D9DEE5", linewidth=0.7, alpha=0.7)
        axis.set_facecolor("white")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(FIGURE_PNG, dpi=190)
    fig.savefig(FIGURE_SVG)
    plt.close(fig)


def main() -> None:
    freeze_hashes = verify_freeze()
    ensure_source()
    build_caches()
    with np.load(DERIVED, allow_pickle=False) as derived:
        closure = np.asarray(derived["closure"], dtype=np.float64)
        qc = np.asarray(derived["qc"], dtype=np.float64)
    connected = np.load(CONNECTED, mmap_mode="r")

    inventory = prereveal_inventory(closure)
    if (
        inventory.get("eligible_lineages", 0) == 0
        or inventory["development_cycles"] == 0
        or inventory["evaluation_cycles"] == 0
    ):
        payload = {
            "test_id": TEST_ID,
            "verdict": "INCONCLUSIVE — PREDECLARED ADEQUACY FAILURE",
            "freeze_hashes": freeze_hashes,
            "source": {
                "doi": "10.5281/zenodo.16753415",
                "archive": ARCHIVE_NAME,
                "archive_md5": digest(ARCHIVE, "md5"),
                "hdf_sha256": digest(SOURCE, "sha256"),
                "branch": BRANCH,
            },
            "prediction_sha256_before_reveal": None,
            "target_reveal_performed": False,
            "prereveal_inventory": inventory,
            "data_quality": {
                "closure_shape": list(closure.shape),
                "connected_shape": list(connected.shape),
                "maximum_trace_error": float(np.max(qc[:, 0])),
                "maximum_hermiticity_error": float(np.max(qc[:, 1])),
                "minimum_sampled_density_eigenvalue": float(np.min(qc[:, 2])),
                "sampled_density_matrices": int(np.sum(qc[:, 3])),
                "all_derived_values_finite": bool(
                    np.isfinite(closure).all()
                    and np.isfinite(connected).all()
                ),
            },
            "adequacy": {
                "eligible_seeds_at_least_50": False,
                "eligible_lineages_at_least_500": False,
                "cycles_at_least_5000": False,
                "two_turn_ba_cycles_at_least_100": False,
            },
            "reason": (
                "Every one of the 6,600 closure lineages failed the frozen "
                "development direction-coherence threshold of 0.80. No "
                "four-quadrant development or evaluation cycles were "
                "eligible, so no Q41 prediction file was written and no C4 "
                "connected identity was revealed."
            ),
        }
        RESULTS.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))
        print(f"wrote {RESULTS}")
        return

    prediction_sha = prepare_predictions(closure, connected)
    rows, frozen = score_predictions(connected)
    lineage_rows, seed_rows = aggregate_rows(rows)
    grouped = grouped_summary(rows)
    summaries = method_summary(rows, seed_rows)
    comparisons = {
        baseline: bootstrap_advantage(seed_rows, baseline)
        for baseline in METHODS
        if baseline != "q41"
    }
    q40_confusion = confusion(rows, "q40_flag")
    q41_confusion = confusion(rows, "q41_flag")
    two_turn_ba_cycles = int(
        sum(
            row["family"] == "two_turn_7_5" and int(row["q4"]) == 1
            for row in rows
        )
    )
    adequacy = {
        "eligible_seeds_at_least_50": len(seed_rows) >= 50,
        "eligible_lineages_at_least_500": len(lineage_rows) >= 500,
        "cycles_at_least_5000": len(rows) >= 5000,
        "two_turn_ba_cycles_at_least_100": two_turn_ba_cycles >= 100,
    }
    primary = comparisons["q40"]
    strong = comparisons["development_affine"]
    gates = {
        "adequacy_pass": all(adequacy.values()),
        "primary_q41_over_q40_pass": bool(
            primary["advantage"] > 0 and primary["ci95"][0] > 0
        ),
        "strong_q41_over_development_affine_pass": bool(
            strong["advantage"] > 0 and strong["ci95"][0] > 0
        ),
    }
    if not gates["adequacy_pass"]:
        verdict = "INCONCLUSIVE — PREDECLARED ADEQUACY FAILURE"
    elif gates["primary_q41_over_q40_pass"]:
        verdict = (
            "SUPPORTED — TRANSFERRED STRAND EXTENSION"
            if gates["strong_q41_over_development_affine_pass"]
            else "SUPPORTED VS Q40; NOT STRONG VS DEVELOPMENT AFFINE"
        )
    else:
        verdict = "NOT SUPPORTED — STRAND EXTENSION"

    write_events(rows)
    make_figure(closure, rows, seed_rows, grouped, frozen)
    payload = {
        "test_id": TEST_ID,
        "verdict": verdict,
        "freeze_hashes": freeze_hashes,
        "source": {
            "doi": "10.5281/zenodo.16753415",
            "archive": ARCHIVE_NAME,
            "archive_md5": digest(ARCHIVE, "md5"),
            "hdf_sha256": digest(SOURCE, "sha256"),
            "branch": BRANCH,
        },
        "prediction_sha256_before_reveal": prediction_sha,
        "data_quality": {
            "closure_shape": list(closure.shape),
            "connected_shape": list(connected.shape),
            "maximum_trace_error": float(np.max(qc[:, 0])),
            "maximum_hermiticity_error": float(np.max(qc[:, 1])),
            "minimum_sampled_density_eigenvalue": float(np.min(qc[:, 2])),
            "sampled_density_matrices": int(np.sum(qc[:, 3])),
            "all_derived_values_finite": bool(
                np.isfinite(closure).all() and np.isfinite(connected).all()
            ),
        },
        "counts": {
            "seeds": len(seed_rows),
            "lineages": len(lineage_rows),
            "cycles": len(rows),
            "two_turn_ba_cycles": two_turn_ba_cycles,
            "family_lineages": {
                "two_turn_7_5": int(
                    frozen["family_lineages_two_turn_7_5"]
                ),
                "one_turn_15": int(
                    frozen["family_lineages_one_turn_15"]
                ),
                "other": int(frozen["family_lineages_other"]),
            },
            "development_cycles_for_affine": int(
                frozen["development_cycles"]
            ),
        },
        "frozen_rule": {
            "two_turn_period_window": [7.35, 7.65],
            "lag15_correlation_minimum": 0.95,
            "strand_quadrant": 1,
            "operator": "q40_visible_flag OR (two_turn_7_5 AND q4==1)",
        },
        "adequacy": adequacy,
        "gates": gates,
        "method_summaries": summaries,
        "comparisons_scaled_error": comparisons,
        "reversal_detection": {
            "q40": q40_confusion,
            "q41": q41_confusion,
        },
        "family_quadrant_summary": grouped,
        "artifacts": {
            "events": EVENTS.name,
            "figure_png": FIGURE_PNG.name,
            "figure_svg": FIGURE_SVG.name,
        },
    }
    RESULTS.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"verdict": verdict, "gates": gates}, indent=2))
    print(json.dumps(comparisons, indent=2))
    print(f"wrote {RESULTS}")
    print(f"wrote {EVENTS}")
    print(f"wrote {FIGURE_PNG}")


if __name__ == "__main__":
    main()

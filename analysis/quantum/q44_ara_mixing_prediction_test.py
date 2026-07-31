"""Q44 prospective compact ARA matrix-mixing prediction.

The command is deliberately split:

    --build    verify the frozen public archive and create local caches
    --prepare  fit on samples 0..249 and seal predictions without C4
    --score    reveal the held-out fourth matrices and score the seal

The scalar closure path is visible throughout because the frozen question is
conditional matrix prediction, not time-ahead quadrant-occurrence prediction.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import gzip
import hashlib
import json
import os
import pathlib
import sys
import time
from collections import defaultdict


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / "public_data" / "_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".mplconfig"))

import h5py
import numpy as np

import q40_return_flow_relation_reversal_test as base
import q42_ara_dual_strand_flow_test as q42


TEST_ID = "Q44-ARA-MIXING-PREDICTION-v1"
DATA = HERE / "public_data" / "q44_mixing_inhomo_v1_mimic"
ARCHIVE_NAME = "unnati_submit_12_inhomo_v1_mimic.hdf5.zip"
HDF_NAME = "unnati_submit_12_inhomo_v1_mimic.hdf5"
ARCHIVE = DATA / ARCHIVE_NAME
SOURCE = DATA / HDF_NAME
DERIVED = DATA / "q44_derived_cache.npz"
CONNECTED = DATA / "q44_connected_cache.npy"
PREDICTIONS = DATA / "q44_frozen_predictions.npz"
PROTOCOL = HERE / "Q44_ARA_MIXING_PREDICTION_PROTOCOL_v1_PRETARGET_FROZEN.md"
TARGET_LOCK = HERE / "Q44_TARGET_LOCK_v1_FROZEN.md"
RESULTS = HERE / "Q44_ARA_MIXING_PREDICTION_RESULTS.json"
EVENTS = HERE / "Q44_ARA_MIXING_PREDICTION_CYCLES.csv.gz"

ARCHIVE_MD5 = "08b2eaa89268952f7e197eecb2ea9610"
PROTOCOL_SHA256 = "66df56a5255fa8dfaea95441617f3483457f9c75630876148c59b918efbfd71c"
TARGET_LOCK_SHA256 = "65f12e7a86316e6c3630a22f1fe0cbbdff69d0ddf879b3fab007094aa21b7bba"
BRANCH = "c2_2local connectivity"
MIN_GROUP_CYCLES = 25
BOOTSTRAP_DRAWS = 20_000
BOOTSTRAP_SEED = 440028
EPS = 1e-12

METHODS = (
    "ara_mixing",
    "diameter_only",
    "persistence",
    "forward_relation",
    "reverse_relation",
    "local_linear",
    "pooled_affine",
    "grouped_affine",
)


def digest(path: pathlib.Path, algorithm: str) -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def verify_frozen_files() -> None:
    checks = (
        (PROTOCOL, PROTOCOL_SHA256),
        (TARGET_LOCK, TARGET_LOCK_SHA256),
    )
    for path, expected in checks:
        actual = digest(path, "sha256")
        if actual != expected:
            raise RuntimeError(
                f"Frozen file changed: {path.name}; expected {expected}, got {actual}"
            )


def ensure_source() -> None:
    verify_frozen_files()
    if not ARCHIVE.exists():
        raise RuntimeError(f"Frozen archive missing: {ARCHIVE}")
    actual = digest(ARCHIVE, "md5")
    if actual != ARCHIVE_MD5:
        raise RuntimeError(
            f"Frozen archive MD5 mismatch; expected {ARCHIVE_MD5}, got {actual}"
        )
    if not SOURCE.exists():
        raise RuntimeError(
            "Verified archive has not been extracted; run q44_zenodo_download.py"
        )


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
                [
                    root[str(time_index)][name][()]
                    for name in base.PAIR_NAMES
                ]
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


def build_caches(workers: int) -> None:
    ensure_source()
    if DERIVED.exists() and CONNECTED.exists():
        print("using existing Q44 caches", flush=True)
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
        pairs=np.asarray(base.PAIRS, dtype=np.int8),
        branch=np.asarray(BRANCH),
    )


def components(c1: np.ndarray, c2: np.ndarray, c3: np.ndarray):
    """Return visible diameter D and its perpendicular residual Other."""
    diameter = c1 - c2
    visible_step = c3 - c2
    diameter_sq = float(np.sum(diameter * diameter))
    if diameter_sq <= EPS:
        other = np.zeros_like(diameter)
    else:
        other = visible_step - (
            float(np.sum(visible_step * diameter)) / diameter_sq
        ) * diameter
    return diameter, other


def group_key(family: str, q4: int) -> tuple[str, int]:
    return family, int(q4)


def gather_development(
    closure: np.ndarray,
    connected: np.ndarray,
):
    records: list[dict] = []
    coordinate_cache: dict[tuple[int, int], tuple] = {}
    for seed in range(100):
        for pair in range(66):
            coordinate = base.coordinates(closure[seed, :, pair])
            if coordinate is None:
                continue
            u, v, labels, direction, coherence, occupancy = coordinate
            if coherence < 0.80 or occupancy < 0.05:
                continue
            family, fit = q42.cadence_family(u, v)
            coordinate_cache[(seed, pair)] = (
                coordinate,
                family,
                fit,
            )
            scale = float(
                np.median(
                    np.linalg.norm(connected[seed, :250, pair], axis=(1, 2))
                )
            )
            for window in base.complete_windows(labels, direction, 0, 248):
                c1, c2, c3, c4 = base.identities_for_window(
                    connected, seed, pair, window
                )
                diameter, other = components(c1, c2, c3)
                records.append(
                    {
                        "seed": seed,
                        "pair": pair,
                        "family": family,
                        "q4": int(window[3][0]),
                        "scale": scale,
                        "c1": c1,
                        "c2": c2,
                        "c3": c3,
                        "c4": c4,
                        "diameter": diameter,
                        "other": other,
                        "target_step": c4 - c3,
                    }
                )
    return records, coordinate_cache


def fit_mixing(records: list[dict]):
    normal = defaultdict(lambda: np.zeros((2, 2), dtype=np.float64))
    rhs = defaultdict(lambda: np.zeros(2, dtype=np.float64))
    counts = defaultdict(int)
    for row in records:
        key = group_key(row["family"], row["q4"])
        d, o, y = row["diameter"], row["other"], row["target_step"]
        normal[key][0, 0] += np.sum(d * d)
        normal[key][0, 1] += np.sum(d * o)
        normal[key][1, 0] += np.sum(d * o)
        normal[key][1, 1] += np.sum(o * o)
        rhs[key][0] += np.sum(d * y)
        rhs[key][1] += np.sum(o * y)
        counts[key] += 1
    coefficients = {
        key: np.linalg.pinv(value, rcond=1e-12) @ rhs[key]
        for key, value in normal.items()
    }
    return coefficients, dict(counts)


def fit_affine(records: list[dict], grouped: bool):
    normal = defaultdict(lambda: np.zeros((3, 3), dtype=np.float64))
    rhs = defaultdict(lambda: np.zeros(3, dtype=np.float64))
    counts = defaultdict(int)
    for row in records:
        key = (
            group_key(row["family"], row["q4"])
            if grouped
            else ("pooled",)
        )
        states = (row["c1"], row["c2"], row["c3"])
        for left in range(3):
            for right in range(3):
                normal[key][left, right] += np.sum(
                    states[left] * states[right]
                )
            rhs[key][left] += np.sum(states[left] * row["c4"])
        counts[key] += 1
    coefficients = {
        key: np.linalg.pinv(value, rcond=1e-12) @ rhs[key]
        for key, value in normal.items()
    }
    return coefficients, dict(counts)


def predictor_stack(
    c1: np.ndarray,
    c2: np.ndarray,
    c3: np.ndarray,
    mixing: np.ndarray,
    pooled_affine: np.ndarray,
    grouped_affine: np.ndarray,
):
    diameter, other = components(c1, c2, c3)
    alpha, beta = mixing
    return np.stack(
        (
            c3 + alpha * diameter + beta * other,
            c3 + alpha * diameter,
            c3,
            c3 + diameter,
            c3 - diameter,
            2 * c3 - c2,
            (
                pooled_affine[0] * c1
                + pooled_affine[1] * c2
                + pooled_affine[2] * c3
            ),
            (
                grouped_affine[0] * c1
                + grouped_affine[1] * c2
                + grouped_affine[2] * c3
            ),
        ),
        axis=0,
    )


def serializable_coefficients(values: dict) -> str:
    return json.dumps(
        {
            repr(key): [float(item) for item in value]
            for key, value in sorted(values.items(), key=lambda item: repr(item[0]))
        },
        sort_keys=True,
    )


def prepare_predictions() -> str:
    verify_frozen_files()
    if not DERIVED.exists() or not CONNECTED.exists():
        raise RuntimeError("Q44 caches are missing; run --build first")
    closure = np.asarray(np.load(DERIVED)["closure"], dtype=np.float32)
    connected = np.load(CONNECTED, mmap_mode="r")
    development, coordinate_cache = gather_development(closure, connected)
    mixing, mixing_counts = fit_mixing(development)
    pooled, pooled_counts = fit_affine(development, grouped=False)
    grouped, grouped_counts = fit_affine(development, grouped=True)
    pooled_weights = pooled[("pooled",)]

    metadata: dict[str, list] = defaultdict(list)
    visible_blocks: list[np.ndarray] = []
    prediction_blocks: list[np.ndarray] = []
    evaluation_group_counts = defaultdict(int)
    for (seed, pair), (coordinate, family, fit) in coordinate_cache.items():
        u, v, labels, direction, coherence, occupancy = coordinate
        scale = float(
            np.median(
                np.linalg.norm(connected[seed, :250, pair], axis=(1, 2))
            )
        )
        for window in base.complete_windows(labels, direction, 250, 498):
            q4 = int(window[3][0])
            key = group_key(family, q4)
            if key not in mixing or key not in grouped:
                raise RuntimeError(f"Evaluation group lacks a fitted model: {key}")
            if mixing_counts[key] < MIN_GROUP_CYCLES:
                raise RuntimeError(
                    f"Evaluation group has only {mixing_counts[key]} "
                    f"development cycles: {key}"
                )
            c1, c2, c3 = base.identities_for_window(
                connected, seed, pair, window, count=3
            )
            visible_blocks.append(np.stack((c1, c2, c3)))
            prediction_blocks.append(
                predictor_stack(
                    c1,
                    c2,
                    c3,
                    mixing[key],
                    pooled_weights,
                    grouped[key],
                )
            )
            evaluation_group_counts[key] += 1
            metadata["seed"].append(seed)
            metadata["pair"].append(pair)
            metadata["family"].append(family)
            metadata["q4"].append(q4)
            metadata["direction"].append(direction)
            metadata["coherence"].append(coherence)
            metadata["occupancy"].append(occupancy)
            metadata["lineage_scale"].append(scale)
            metadata["angular_period"].append(
                float(fit["angular_period_samples"])
            )
            for index, (quadrant, start, end) in enumerate(window, start=1):
                metadata[f"q{index}"].append(quadrant)
                metadata[f"q{index}_start"].append(start)
                metadata[f"q{index}_end"].append(end)

    if not prediction_blocks:
        raise RuntimeError("Q44 produced no evaluation predictions")
    payload = {key: np.asarray(value) for key, value in metadata.items()}
    payload.update(
        {
            "c_visible": np.asarray(visible_blocks, dtype=np.float32),
            "predictions": np.asarray(prediction_blocks, dtype=np.float32),
            "methods": np.asarray(METHODS),
            "mixing_coefficients_json": np.asarray(
                serializable_coefficients(mixing)
            ),
            "mixing_development_counts_json": np.asarray(
                json.dumps(
                    {repr(k): int(v) for k, v in mixing_counts.items()},
                    sort_keys=True,
                )
            ),
            "affine_pooled_json": np.asarray(
                serializable_coefficients(pooled)
            ),
            "affine_grouped_json": np.asarray(
                serializable_coefficients(grouped)
            ),
            "affine_pooled_counts_json": np.asarray(
                json.dumps(
                    {repr(k): int(v) for k, v in pooled_counts.items()},
                    sort_keys=True,
                )
            ),
            "affine_grouped_counts_json": np.asarray(
                json.dumps(
                    {repr(k): int(v) for k, v in grouped_counts.items()},
                    sort_keys=True,
                )
            ),
            "evaluation_group_counts_json": np.asarray(
                json.dumps(
                    {repr(k): int(v) for k, v in evaluation_group_counts.items()},
                    sort_keys=True,
                )
            ),
            "development_cycles": np.asarray(len(development)),
            "eligible_lineages": np.asarray(len(coordinate_cache)),
            "protocol_sha256": np.asarray(PROTOCOL_SHA256),
            "target_lock_sha256": np.asarray(TARGET_LOCK_SHA256),
            "archive_md5": np.asarray(ARCHIVE_MD5),
        }
    )
    np.savez_compressed(PREDICTIONS, **payload)
    prediction_hash = digest(PREDICTIONS, "sha256")
    print(
        json.dumps(
            {
                "status": "PREDICTIONS SEALED — TARGET C4 NOT READ",
                "prediction_sha256": prediction_hash,
                "development_cycles": len(development),
                "eligible_lineages": len(coordinate_cache),
                "evaluation_cycles": len(prediction_blocks),
                "minimum_development_cycles_per_evaluation_group": min(
                    mixing_counts[key] for key in evaluation_group_counts
                ),
                "groups": {
                    repr(key): {
                        "development": mixing_counts[key],
                        "evaluation": evaluation_group_counts[key],
                        "alpha": float(mixing[key][0]),
                        "beta": float(mixing[key][1]),
                    }
                    for key in sorted(evaluation_group_counts, key=repr)
                },
            },
            indent=2,
        ),
        flush=True,
    )
    return prediction_hash


def matrix_metrics(
    predicted: np.ndarray,
    actual: np.ndarray,
    scale: float,
    forward: np.ndarray,
) -> dict[str, float]:
    error = float(np.linalg.norm(predicted - actual))
    actual_norm = float(np.linalg.norm(actual))
    predicted_norm = float(np.linalg.norm(predicted))
    cosine = float(
        np.sum(predicted * actual)
        / (predicted_norm * actual_norm + EPS)
    )
    predicted_h = float(np.cbrt(abs(np.linalg.det(predicted))))
    actual_h = float(np.cbrt(abs(np.linalg.det(actual))))
    actual_orientation = float(np.sum(actual * forward))
    predicted_orientation = float(np.sum(predicted * forward))
    return {
        "scaled_error": error / (scale + EPS),
        "nrmse": error / (actual_norm + EPS),
        "cosine": cosine,
        "closure_error": abs(predicted_h - actual_h) / (actual_h + EPS),
        "orientation_correct": float(
            np.sign(predicted_orientation) == np.sign(actual_orientation)
        ),
    }


def score_cycles() -> tuple[list[dict], str]:
    verify_frozen_files()
    if not PREDICTIONS.exists():
        raise RuntimeError("Frozen predictions do not exist; run --prepare first")
    prediction_hash = digest(PREDICTIONS, "sha256")
    frozen = np.load(PREDICTIONS, allow_pickle=False)
    if tuple(str(value) for value in frozen["methods"]) != METHODS:
        raise RuntimeError("Frozen method order changed")
    connected = np.load(CONNECTED, mmap_mode="r")
    rows: list[dict] = []
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
            frozen["c_visible"][index],
            dtype=np.float64,
        )
        forward = c3 + (c1 - c2)
        row: dict[str, object] = {
            "cycle_id": index,
            "seed": seed,
            "pair_index": pair,
            "pair": base.PAIR_NAMES[pair],
            "family": str(frozen["family"][index]),
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
            "actual_norm": float(np.linalg.norm(actual)),
        }
        predictions = np.asarray(
            frozen["predictions"][index],
            dtype=np.float64,
        )
        for method_index, method in enumerate(METHODS):
            for metric, value in matrix_metrics(
                predictions[method_index],
                actual,
                float(row["lineage_scale"]),
                forward,
            ).items():
                row[f"{method}_{metric}"] = value
        rows.append(row)
    return rows, prediction_hash


METRICS = (
    "scaled_error",
    "nrmse",
    "cosine",
    "closure_error",
    "orientation_correct",
)


def aggregate(rows: list[dict]):
    lineages: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for row in rows:
        lineages[(int(row["seed"]), int(row["pair_index"]))].append(row)
    lineage_rows: list[dict] = []
    for (seed, pair), values in lineages.items():
        output: dict[str, object] = {
            "seed": seed,
            "pair_index": pair,
            "cycles": len(values),
        }
        for method in METHODS:
            for metric in METRICS:
                output[f"{method}_{metric}"] = float(
                    np.mean([row[f"{method}_{metric}"] for row in values])
                )
        lineage_rows.append(output)
    seeds: dict[int, list[dict]] = defaultdict(list)
    for row in lineage_rows:
        seeds[int(row["seed"])].append(row)
    seed_rows: list[dict] = []
    for seed, values in seeds.items():
        output = {"seed": seed, "lineages": len(values)}
        for method in METHODS:
            for metric in METRICS:
                output[f"{method}_{metric}"] = float(
                    np.mean([row[f"{method}_{metric}"] for row in values])
                )
        seed_rows.append(output)
    return lineage_rows, seed_rows


def bootstrap_advantage(
    seed_rows: list[dict],
    baseline: str,
    metric: str = "scaled_error",
) -> dict:
    ara = np.asarray(
        [row[f"ara_mixing_{metric}"] for row in seed_rows],
        dtype=np.float64,
    )
    control = np.asarray(
        [row[f"{baseline}_{metric}"] for row in seed_rows],
        dtype=np.float64,
    )
    difference = control - ara
    rng = np.random.default_rng(
        BOOTSTRAP_SEED + METHODS.index(baseline) * 101
    )
    indices = rng.integers(
        0,
        len(difference),
        size=(BOOTSTRAP_DRAWS, len(difference)),
    )
    distribution = np.mean(difference[indices], axis=1)
    return {
        "advantage": float(np.mean(difference)),
        "ci95": [
            float(np.quantile(distribution, 0.025)),
            float(np.quantile(distribution, 0.975)),
        ],
        "bootstrap_p_no_advantage": float(
            (np.sum(distribution <= 0) + 1) / (BOOTSTRAP_DRAWS + 1)
        ),
    }


def method_summary(seed_rows: list[dict]) -> dict:
    output = {}
    for method in METHODS:
        output[method] = {
            metric: float(
                np.mean([row[f"{method}_{metric}"] for row in seed_rows])
            )
            for metric in METRICS
        }
    return output


def write_events(rows: list[dict]) -> None:
    with gzip.open(EVENTS, "wt", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def score_and_report() -> dict:
    rows, prediction_hash = score_cycles()
    lineage_rows, seed_rows = aggregate(rows)
    summary = method_summary(seed_rows)
    advantages = {
        baseline: bootstrap_advantage(seed_rows, baseline)
        for baseline in METHODS
        if baseline != "ara_mixing"
    }
    frozen = np.load(PREDICTIONS, allow_pickle=False)
    development_counts = json.loads(
        str(frozen["mixing_development_counts_json"])
    )
    evaluation_counts = json.loads(
        str(frozen["evaluation_group_counts_json"])
    )
    represented_seeds = len(seed_rows)
    evaluation_cycles = len(rows)
    minimum_group = min(
        development_counts[key] for key in evaluation_counts
    )
    all_finite = all(
        np.isfinite(value)
        for method in summary.values()
        for value in method.values()
    )
    adequacy = {
        "at_least_80_seeds": represented_seeds >= 80,
        "at_least_1000_cycles": evaluation_cycles >= 1000,
        "minimum_25_development_cycles_per_evaluation_group": (
            minimum_group >= MIN_GROUP_CYCLES
        ),
        "all_summary_values_finite": all_finite,
        "prediction_artifact_hashed_before_scoring": True,
    }
    support = {
        "ara_scaled_error_at_most_0_40": (
            summary["ara_mixing"]["scaled_error"] <= 0.40
        ),
        "ara_cosine_at_least_0_85": (
            summary["ara_mixing"]["cosine"] >= 0.85
        ),
        "beats_diameter_by_0_01_with_positive_ci": (
            advantages["diameter_only"]["advantage"] >= 0.01
            and advantages["diameter_only"]["ci95"][0] > 0
        ),
        "beats_pooled_affine_with_positive_ci": (
            advantages["pooled_affine"]["advantage"] > 0
            and advantages["pooled_affine"]["ci95"][0] > 0
        ),
    }
    if not all(adequacy.values()):
        verdict = "INCONCLUSIVE — ELIGIBILITY"
    elif all(support.values()):
        verdict = "SUPPORTED — COMPACT ARA MIXING PREDICTION"
    elif (
        support["ara_scaled_error_at_most_0_40"]
        and support["ara_cosine_at_least_0_85"]
    ):
        verdict = "PARTIAL — PREDICTIVE SHAPE, NO DISTINCT MIXING ADVANTAGE"
    else:
        verdict = "NOT SUPPORTED — COMPACT ARA MIXING PREDICTION"
    result = {
        "test_id": TEST_ID,
        "verdict": verdict,
        "target": {
            "doi": "10.5281/zenodo.16753415",
            "file": ARCHIVE_NAME,
            "archive_md5": ARCHIVE_MD5,
            "branch": BRANCH,
        },
        "frozen_artifacts": {
            "protocol_sha256": PROTOCOL_SHA256,
            "target_lock_sha256": TARGET_LOCK_SHA256,
            "prediction_sha256": prediction_hash,
        },
        "sample": {
            "development_cycles": int(frozen["development_cycles"]),
            "eligible_lineages": int(frozen["eligible_lineages"]),
            "evaluation_cycles": evaluation_cycles,
            "represented_lineages": len(lineage_rows),
            "represented_seeds": represented_seeds,
            "minimum_development_cycles_per_evaluation_group": int(
                minimum_group
            ),
            "development_group_counts": development_counts,
            "evaluation_group_counts": evaluation_counts,
        },
        "equation": {
            "text": "C4_hat=C3+alpha_g*(C1-C2)+beta_g*Other",
            "other": "(C3-C2)-proj_(C1-C2)(C3-C2)",
            "group": "(cadence_family,q4)",
            "coefficients": json.loads(
                str(frozen["mixing_coefficients_json"])
            ),
        },
        "seed_balanced_methods": summary,
        "ara_scaled_error_advantages": advantages,
        "adequacy_gates": adequacy,
        "support_gates": support,
        "quality_control": {
            key: (
                float(np.max(np.load(DERIVED)["qc"][:, index]))
                if index in (0, 1)
                else float(np.min(np.load(DERIVED)["qc"][:, index]))
            )
            for index, key in enumerate(
                (
                    "maximum_trace_error",
                    "maximum_hermiticity_error",
                    "minimum_sampled_eigenvalue",
                )
            )
        },
        "claim_boundary": (
            "Conditional fourth-matrix prediction on one public simulator "
            "archive; not a universal quantum law or time-ahead forecast."
        ),
    }
    write_events(rows)
    RESULTS.write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "verdict": verdict,
                "sample": result["sample"],
                "seed_balanced_methods": summary,
                "ara_scaled_error_advantages": advantages,
                "support_gates": support,
                "results": str(RESULTS),
            },
            indent=2,
        ),
        flush=True,
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "stage",
        choices=("build", "prepare", "score"),
    )
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    if args.stage == "build":
        build_caches(max(1, args.workers))
    elif args.stage == "prepare":
        prepare_predictions()
    else:
        score_and_report()


if __name__ == "__main__":
    main()

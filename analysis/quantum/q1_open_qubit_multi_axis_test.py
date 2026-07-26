"""Q1 open-qubit multi-axis ARA benchmark.

Implements the frozen T258 protocol:
Q1_OPEN_QUBIT_MULTI_AXIS_PROTOCOL_v1_FROZEN.md

Synthetic known-referee test only. The script does not derive quantum mechanics
or test an ontological claim. It tests whether several measured ARA diameter
cuts retain distinctions hidden from one cut, under equal-information controls.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_PROTOCOL_v1_FROZEN.md"
PROTOCOL_HASH = "f51c0b44a29869f90af88ada873f1363441424dfc9e2584fcdc5b19215700a2b"

DEVELOPMENT_CSV = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_DEVELOPMENT.csv"
TRIALS_CSV = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_TRIALS.csv"
AGGREGATES_CSV = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_AGGREGATES.csv"
TRAJECTORIES_CSV = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_TRAJECTORIES.csv"
RESULTS_JSON = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_RESULTS.json"

DEV_SEED = 2026072301
TARGET_SEED = 2026072302
CONTROL_SEED = 2026072303
PRIMARY_SHOTS = 128
SHOT_LEVELS = (32, 64, 128, 256, 512, 1024)
N_DEV_BASE = 64
N_TARGET_BASE = 128
N_TIME = 65
T_MAX = 4.0
N_HELDOUT_DIRECTIONS = 16
FAMILIES = ("U", "T2", "T1", "C")
ROTATING = {"U", "C"}
RELAXING = {"T1", "C"}
RIDGE_FAMILIES = {"U", "T2"}
TIME = np.linspace(0.0, T_MAX, N_TIME)


@dataclass(frozen=True)
class Draw:
    base_id: int
    omega: float
    t1: float
    tphi: float


def protocol_sha256() -> str:
    return hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()


def generate_draws(seed: int, count: int) -> list[Draw]:
    rng = np.random.default_rng(seed)
    draws: list[Draw] = []
    for base_id in range(count):
        magnitude = float(rng.uniform(0.8, 1.6))
        sign = -1.0 if int(rng.integers(0, 2)) == 0 else 1.0
        draws.append(
            Draw(
                base_id=base_id,
                omega=sign * magnitude,
                t1=float(rng.uniform(1.5, 3.0)),
                tphi=float(rng.uniform(1.0, 2.5)),
            )
        )
    return draws


def true_state(family: str, draw: Draw, time: np.ndarray = TIME) -> np.ndarray:
    """Return shape (time, xyz) under the frozen known-referee dynamics."""
    if family == "U":
        return np.column_stack(
            (np.cos(draw.omega * time), np.sin(draw.omega * time), np.zeros_like(time))
        )
    if family == "T2":
        decay = np.exp(-time / draw.tphi)
        return np.column_stack((decay, np.zeros_like(time), np.zeros_like(time)))
    if family == "T1":
        transverse = np.exp(-time / (2.0 * draw.t1))
        longitudinal = 1.0 - np.exp(-time / draw.t1)
        return np.column_stack((transverse, np.zeros_like(time), longitudinal))
    if family == "C":
        t2_total = 1.0 / (1.0 / (2.0 * draw.t1) + 1.0 / draw.tphi)
        decay = np.exp(-time / t2_total)
        longitudinal = 1.0 - np.exp(-time / draw.t1)
        return np.column_stack(
            (
                decay * np.cos(draw.omega * time),
                decay * np.sin(draw.omega * time),
                longitudinal,
            )
        )
    raise ValueError(f"Unknown family: {family}")


def observe_axes(state: np.ndarray, shots: int, rng: np.random.Generator) -> np.ndarray:
    x_true = 1.0 - state
    counts = rng.binomial(shots, np.clip(x_true / 2.0, 0.0, 1.0))
    return 2.0 * counts.astype(float) / float(shots)


def radial_project(state: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(state, axis=1)
    scales = np.maximum(1.0, norms)
    return state / scales[:, None]


def ara_reconstruct(readings: np.ndarray, physical: bool = True) -> np.ndarray:
    raw = np.empty_like(readings, dtype=float)
    raw[:, 0] = 1.0 - readings[:, 0]
    raw[:, 1] = 1.0 - readings[:, 1]
    raw[:, 2] = 1.0 - readings[:, 2]
    return radial_project(raw) if physical else raw


def bloch_reconstruct(readings: np.ndarray) -> np.ndarray:
    """Independent same-information route through binary probabilities."""
    p_minus_x = readings[:, 0] / 2.0
    p_minus_y = readings[:, 1] / 2.0
    p_minus_z = readings[:, 2] / 2.0
    expectation = np.column_stack(
        (
            1.0 - 2.0 * p_minus_x,
            1.0 - 2.0 * p_minus_y,
            1.0 - 2.0 * p_minus_z,
        )
    )
    lengths = np.sqrt(np.sum(expectation * expectation, axis=1))
    outside = lengths > 1.0
    if np.any(outside):
        expectation[outside] = expectation[outside] / lengths[outside, None]
    return expectation


def weighted_slope(time: np.ndarray, values: np.ndarray, weights: np.ndarray) -> float:
    total = float(np.sum(weights))
    if total <= 0.0:
        return 0.0
    t_bar = float(np.sum(weights * time) / total)
    v_bar = float(np.sum(weights * values) / total)
    denom = float(np.sum(weights * (time - t_bar) ** 2))
    if denom <= 0.0:
        return 0.0
    return float(np.sum(weights * (time - t_bar) * (values - v_bar)) / denom)


def extract_features(state: np.ndarray) -> dict[str, float]:
    transverse = np.hypot(state[:, 0], state[:, 1])
    mask = transverse >= 0.20
    if int(np.sum(mask)) >= 3:
        phase = np.unwrap(np.arctan2(state[mask, 1], state[mask, 0]))
        # The protocol registered a weighted slope. Radius squared is the
        # pre-outcome implementation choice: phase confidence scales with
        # transverse signal power.
        rotation_slope = weighted_slope(TIME[mask], phase, transverse[mask] ** 2)
    else:
        rotation_slope = 0.0
    relaxation_score = float(np.mean(state[-8:, 2]) - np.mean(state[:8, 2]))
    ridge_coherence = float(np.mean(np.linalg.norm(state[-8:], axis=1)))
    return {
        "rotation_slope": rotation_slope,
        "rotation_score": abs(rotation_slope),
        "relaxation_score": relaxation_score,
        "ridge_coherence": ridge_coherence,
    }


def balanced_accuracy(labels: np.ndarray, predictions: np.ndarray) -> float:
    values = np.unique(labels)
    recalls = []
    for value in values:
        mask = labels == value
        recalls.append(float(np.mean(predictions[mask] == value)))
    return float(np.mean(recalls))


def select_midpoint_threshold(
    scores: Iterable[float], labels: Iterable[int], positive_high: bool = True
) -> tuple[float, float]:
    score = np.asarray(list(scores), dtype=float)
    label = np.asarray(list(labels), dtype=int)
    unique = np.unique(score)
    if len(unique) == 1:
        candidates = np.array([unique[0]], dtype=float)
    else:
        mids = (unique[:-1] + unique[1:]) / 2.0
        span = max(1.0, float(unique[-1] - unique[0]))
        candidates = np.concatenate(
            ([unique[0] - 1e-12 * span], mids, [unique[-1] + 1e-12 * span])
        )
    best_threshold = float(candidates[0])
    best_ba = -math.inf
    for threshold in candidates:
        pred = (score >= threshold).astype(int) if positive_high else (score <= threshold).astype(int)
        ba = balanced_accuracy(label, pred)
        if ba > best_ba + 1e-15 or (
            abs(ba - best_ba) <= 1e-15 and float(threshold) < best_threshold
        ):
            best_ba = ba
            best_threshold = float(threshold)
    return best_threshold, float(best_ba)


def classify(features: dict[str, float], rot_threshold: float, relax_threshold: float) -> str:
    rotating = features["rotation_score"] >= rot_threshold
    relaxing = features["relaxation_score"] >= relax_threshold
    if relaxing and rotating:
        return "C"
    if relaxing:
        return "T1"
    if rotating:
        return "U"
    return "T2"


def z_only_classify(relaxation_score: float, relax_threshold: float) -> str:
    return "T1" if relaxation_score >= relax_threshold else "U"


def native_templates() -> tuple[np.ndarray, np.ndarray]:
    templates: list[np.ndarray] = []
    labels: list[str] = []
    for omega in (-1.6, -1.2, -0.8, 0.8, 1.2, 1.6):
        draw = Draw(-1, omega, 2.0, 1.5)
        templates.append(1.0 - true_state("U", draw))
        labels.append("U")
    for tphi in (1.0, 1.5, 2.0, 2.5):
        draw = Draw(-1, 1.0, 2.0, tphi)
        templates.append(1.0 - true_state("T2", draw))
        labels.append("T2")
    for t1 in (1.5, 2.0, 2.5, 3.0):
        draw = Draw(-1, 1.0, t1, 1.5)
        templates.append(1.0 - true_state("T1", draw))
        labels.append("T1")
    for omega in (-1.6, -1.2, -0.8, 0.8, 1.2, 1.6):
        for t1 in (1.5, 2.0, 2.5, 3.0):
            for tphi in (1.0, 1.5, 2.0, 2.5):
                draw = Draw(-1, omega, t1, tphi)
                templates.append(1.0 - true_state("C", draw))
                labels.append("C")
    return np.asarray(templates), np.asarray(labels, dtype=object)


TEMPLATE_READINGS, TEMPLATE_LABELS = native_templates()


def native_model_classify(readings: np.ndarray) -> tuple[str, float]:
    mse = np.mean((TEMPLATE_READINGS - readings[None, :, :]) ** 2, axis=(1, 2))
    index = int(np.argmin(mse))
    return str(TEMPLATE_LABELS[index]), float(mse[index])


def uniform_directions(rng: np.random.Generator, count: int) -> np.ndarray:
    directions = rng.normal(size=(count, 3))
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    return directions


def directional_mae(state: np.ndarray, truth: np.ndarray, directions: np.ndarray) -> float:
    predicted_x = 1.0 - state @ directions.T
    true_x = 1.0 - truth @ directions.T
    return float(np.mean(np.abs(predicted_x - true_x)))


def antipodal_observation_error(
    truth: np.ndarray, directions: np.ndarray, shots: int, rng: np.random.Generator
) -> float:
    projection = truth @ directions.T
    plus_x = 1.0 - projection
    minus_x = 1.0 + projection
    plus_counts = rng.binomial(shots, np.clip(plus_x / 2.0, 0.0, 1.0))
    minus_counts = rng.binomial(shots, np.clip(minus_x / 2.0, 0.0, 1.0))
    plus_obs = 2.0 * plus_counts.astype(float) / shots
    minus_obs = 2.0 * minus_counts.astype(float) / shots
    return float(np.mean(np.abs(plus_obs + minus_obs - 2.0)))


def vector_rmse(estimate: np.ndarray, truth: np.ndarray) -> float:
    return float(np.sqrt(np.mean((estimate - truth) ** 2)))


def mean_radius_error(estimate: np.ndarray, truth: np.ndarray) -> float:
    return float(
        np.mean(np.abs(np.linalg.norm(estimate, axis=1) - np.linalg.norm(truth, axis=1)))
    )


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def make_development() -> tuple[list[dict[str, object]], dict[str, float]]:
    rng = np.random.default_rng(np.random.SeedSequence([DEV_SEED, 1]))
    rows: list[dict[str, object]] = []
    for draw in generate_draws(DEV_SEED, N_DEV_BASE):
        for family in FAMILIES:
            truth = true_state(family, draw)
            readings = observe_axes(truth, PRIMARY_SHOTS, rng)
            estimate = ara_reconstruct(readings)
            feature = extract_features(estimate)
            rows.append(
                {
                    "split": "development",
                    "base_id": f"D{draw.base_id:04d}",
                    "family": family,
                    "omega": draw.omega,
                    "t1": draw.t1,
                    "tphi": draw.tphi,
                    **feature,
                    "rotating_label": int(family in ROTATING),
                    "relaxing_label": int(family in RELAXING),
                    "ridge_u_label": int(family == "U") if family in RIDGE_FAMILIES else "",
                }
            )

    rot_threshold, rot_ba = select_midpoint_threshold(
        (float(row["rotation_score"]) for row in rows),
        (int(row["rotating_label"]) for row in rows),
    )
    relax_threshold, relax_ba = select_midpoint_threshold(
        (float(row["relaxation_score"]) for row in rows),
        (int(row["relaxing_label"]) for row in rows),
    )
    ridge_rows = [row for row in rows if row["family"] in RIDGE_FAMILIES]
    ridge_threshold, ridge_ba = select_midpoint_threshold(
        (float(row["ridge_coherence"]) for row in ridge_rows),
        (int(row["ridge_u_label"]) for row in ridge_rows),
    )
    thresholds = {
        "rotation": rot_threshold,
        "relaxation": relax_threshold,
        "ridge_coherence": ridge_threshold,
        "development_rotation_balanced_accuracy": rot_ba,
        "development_relaxation_balanced_accuracy": relax_ba,
        "development_ridge_balanced_accuracy": ridge_ba,
    }
    for row in rows:
        row["rotation_threshold"] = rot_threshold
        row["relaxation_threshold"] = relax_threshold
        row["ridge_threshold"] = ridge_threshold
        row["predicted_family"] = classify(row, rot_threshold, relax_threshold)
    return rows, thresholds


def run_targets(thresholds: dict[str, float]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    observation_rng = np.random.default_rng(np.random.SeedSequence([TARGET_SEED, 1]))
    control_rng = np.random.default_rng(np.random.SeedSequence([CONTROL_SEED, 1]))
    rows: list[dict[str, object]] = []
    trajectory_rows: list[dict[str, object]] = []
    draws = generate_draws(TARGET_SEED, N_TARGET_BASE)

    for shots in SHOT_LEVELS:
        for draw in draws:
            for family in FAMILIES:
                truth = true_state(family, draw)
                readings = observe_axes(truth, shots, observation_rng)
                estimate = ara_reconstruct(readings)
                raw_estimate = ara_reconstruct(readings, physical=False)
                bloch_estimate = bloch_reconstruct(readings)

                feature = extract_features(estimate)
                raw_feature = extract_features(raw_estimate)
                bloch_feature = extract_features(bloch_estimate)

                predicted = classify(feature, thresholds["rotation"], thresholds["relaxation"])
                bloch_predicted = classify(
                    bloch_feature, thresholds["rotation"], thresholds["relaxation"]
                )
                z_predicted = z_only_classify(
                    feature["relaxation_score"], thresholds["relaxation"]
                )
                native_predicted, native_mse = native_model_classify(readings)

                time_permutation = control_rng.permutation(N_TIME)
                time_state = ara_reconstruct(readings[time_permutation])
                time_feature = extract_features(time_state)
                time_predicted = classify(
                    time_feature, thresholds["rotation"], thresholds["relaxation"]
                )

                axis_permutation = control_rng.permutation(3)
                axis_state = ara_reconstruct(readings[:, axis_permutation])
                axis_feature = extract_features(axis_state)
                axis_predicted = classify(
                    axis_feature, thresholds["rotation"], thresholds["relaxation"]
                )

                directions = uniform_directions(control_rng, N_HELDOUT_DIRECTIONS)
                z_only_state = np.zeros_like(estimate)
                z_only_state[:, 2] = estimate[:, 2]
                heldout_mae = directional_mae(estimate, truth, directions)
                heldout_raw_mae = directional_mae(raw_estimate, truth, directions)
                heldout_z_mae = directional_mae(z_only_state, truth, directions)
                antipodal_error = antipodal_observation_error(
                    truth, directions, shots, control_rng
                )

                max_state_diff = float(np.max(np.abs(estimate - bloch_estimate)))
                max_score_diff = float(
                    max(
                        abs(feature["rotation_slope"] - bloch_feature["rotation_slope"]),
                        abs(feature["relaxation_score"] - bloch_feature["relaxation_score"]),
                        abs(feature["ridge_coherence"] - bloch_feature["ridge_coherence"]),
                    )
                )
                raw_norm = np.linalg.norm(raw_estimate, axis=1)
                row = {
                    "split": "target",
                    "base_id": f"T{draw.base_id:04d}",
                    "shots": shots,
                    "family": family,
                    "omega": draw.omega,
                    "t1": draw.t1,
                    "tphi": draw.tphi,
                    "clean_z_sum": float(np.sum(truth[:, 2])),
                    **feature,
                    "raw_rotation_score": raw_feature["rotation_score"],
                    "raw_relaxation_score": raw_feature["relaxation_score"],
                    "raw_ridge_coherence": raw_feature["ridge_coherence"],
                    "ara_prediction": predicted,
                    "bloch_prediction": bloch_predicted,
                    "z_prediction": z_predicted,
                    "native_prediction": native_predicted,
                    "time_shuffle_prediction": time_predicted,
                    "axis_shuffle_prediction": axis_predicted,
                    "ara_correct": int(predicted == family),
                    "bloch_correct": int(bloch_predicted == family),
                    "z_correct": int(z_predicted == family),
                    "native_correct": int(native_predicted == family),
                    "time_shuffle_correct": int(time_predicted == family),
                    "axis_shuffle_correct": int(axis_predicted == family),
                    "direction_correct": (
                        int(np.sign(feature["rotation_slope"]) == np.sign(draw.omega))
                        if family in ROTATING
                        else ""
                    ),
                    "ridge_correct": (
                        int(
                            (feature["ridge_coherence"] >= thresholds["ridge_coherence"])
                            == (family == "U")
                        )
                        if family in RIDGE_FAMILIES
                        else ""
                    ),
                    "heldout_mae": heldout_mae,
                    "heldout_raw_mae": heldout_raw_mae,
                    "heldout_z_mae": heldout_z_mae,
                    "antipodal_obs_mae": antipodal_error,
                    "reconstruction_rmse": vector_rmse(estimate, truth),
                    "raw_reconstruction_rmse": vector_rmse(raw_estimate, truth),
                    "radius_mae": mean_radius_error(estimate, truth),
                    "raw_radius_mae": mean_radius_error(raw_estimate, truth),
                    "raw_unphysical_fraction": float(np.mean(raw_norm > 1.0 + 1e-12)),
                    "native_template_mse": native_mse,
                    "ara_bloch_max_state_diff": max_state_diff,
                    "ara_bloch_max_score_diff": max_score_diff,
                    "ara_bloch_disagreement": int(predicted != bloch_predicted),
                    "axis_permutation": "".join(str(int(value)) for value in axis_permutation),
                }
                rows.append(row)

                if shots == PRIMARY_SHOTS and draw.base_id == 0:
                    for index, current_time in enumerate(TIME):
                        trajectory_rows.append(
                            {
                                "base_id": row["base_id"],
                                "family": family,
                                "shots": shots,
                                "time": float(current_time),
                                "true_rx": float(truth[index, 0]),
                                "true_ry": float(truth[index, 1]),
                                "true_rz": float(truth[index, 2]),
                                "observed_xx": float(readings[index, 0]),
                                "observed_xy": float(readings[index, 1]),
                                "observed_xz": float(readings[index, 2]),
                                "estimated_rx": float(estimate[index, 0]),
                                "estimated_ry": float(estimate[index, 1]),
                                "estimated_rz": float(estimate[index, 2]),
                                "true_radius": float(np.linalg.norm(truth[index])),
                                "estimated_radius": float(np.linalg.norm(estimate[index])),
                            }
                        )
    return rows, trajectory_rows


def mean_of(rows: list[dict[str, object]], field: str) -> float:
    values = [float(row[field]) for row in rows if row[field] != ""]
    return float(np.mean(values))


def wilson_interval(successes: int, total: int, z: float = 1.6448536269514722) -> tuple[float, float]:
    if total == 0:
        return math.nan, math.nan
    p = successes / total
    denom = 1.0 + z * z / total
    centre = (p + z * z / (2.0 * total)) / denom
    margin = z * math.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total)) / denom
    return centre - margin, centre + margin


def paired_bootstrap(
    primary: list[dict[str, object]], rng: np.random.Generator, repetitions: int = 5000
) -> dict[str, list[float]]:
    by_base: dict[str, list[dict[str, object]]] = {}
    for row in primary:
        by_base.setdefault(str(row["base_id"]), []).append(row)
    base_ids = sorted(by_base)
    ara_by_base = np.asarray(
        [np.mean([float(row["ara_correct"]) for row in by_base[key]]) for key in base_ids]
    )
    z_by_base = np.asarray(
        [np.mean([float(row["z_correct"]) for row in by_base[key]]) for key in base_ids]
    )
    indices = rng.integers(0, len(base_ids), size=(repetitions, len(base_ids)))
    ara_samples = np.mean(ara_by_base[indices], axis=1)
    gain_samples = np.mean((ara_by_base - z_by_base)[indices], axis=1)
    return {
        "ara_accuracy_90ci": [
            float(np.quantile(ara_samples, 0.05)),
            float(np.quantile(ara_samples, 0.95)),
        ],
        "ara_gain_over_z_90ci": [
            float(np.quantile(gain_samples, 0.05)),
            float(np.quantile(gain_samples, 0.95)),
        ],
    }


def aggregate_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    aggregates: list[dict[str, object]] = []
    for shots in SHOT_LEVELS:
        subset = [row for row in rows if int(row["shots"]) == shots]
        rotating = [row for row in subset if row["family"] in ROTATING]
        ridge = [row for row in subset if row["family"] in RIDGE_FAMILIES]
        aggregates.append(
            {
                "shots": shots,
                "n_trials": len(subset),
                "ara_accuracy": mean_of(subset, "ara_correct"),
                "bloch_accuracy": mean_of(subset, "bloch_correct"),
                "z_accuracy": mean_of(subset, "z_correct"),
                "native_accuracy": mean_of(subset, "native_correct"),
                "time_shuffle_accuracy": mean_of(subset, "time_shuffle_correct"),
                "axis_shuffle_accuracy": mean_of(subset, "axis_shuffle_correct"),
                "rotation_direction_accuracy": mean_of(rotating, "direction_correct"),
                "ridge_u_vs_t2_accuracy": mean_of(ridge, "ridge_correct"),
                "heldout_mae": mean_of(subset, "heldout_mae"),
                "heldout_raw_mae": mean_of(subset, "heldout_raw_mae"),
                "heldout_z_mae": mean_of(subset, "heldout_z_mae"),
                "antipodal_obs_mae": mean_of(subset, "antipodal_obs_mae"),
                "reconstruction_rmse": mean_of(subset, "reconstruction_rmse"),
                "raw_reconstruction_rmse": mean_of(subset, "raw_reconstruction_rmse"),
                "radius_mae": mean_of(subset, "radius_mae"),
                "raw_radius_mae": mean_of(subset, "raw_radius_mae"),
                "raw_unphysical_fraction": mean_of(subset, "raw_unphysical_fraction"),
                "ara_bloch_max_state_diff": max(
                    float(row["ara_bloch_max_state_diff"]) for row in subset
                ),
                "ara_bloch_max_score_diff": max(
                    float(row["ara_bloch_max_score_diff"]) for row in subset
                ),
                "ara_bloch_disagreements": sum(
                    int(row["ara_bloch_disagreement"]) for row in subset
                ),
            }
        )
    return aggregates


def confusion(primary: list[dict[str, object]], prediction_field: str) -> dict[str, dict[str, int]]:
    result = {family: {pred: 0 for pred in FAMILIES} for family in FAMILIES}
    for row in primary:
        result[str(row["family"])][str(row[prediction_field])] += 1
    return result


def main() -> None:
    actual_hash = protocol_sha256()
    if actual_hash != PROTOCOL_HASH:
        raise RuntimeError(
            f"Frozen protocol hash mismatch: expected {PROTOCOL_HASH}, got {actual_hash}"
        )

    development, thresholds = make_development()
    write_rows(DEVELOPMENT_CSV, development)

    trials, trajectories = run_targets(thresholds)
    write_rows(TRIALS_CSV, trials)
    write_rows(TRAJECTORIES_CSV, trajectories)

    aggregates = aggregate_rows(trials)
    write_rows(AGGREGATES_CSV, aggregates)
    primary = [row for row in trials if int(row["shots"]) == PRIMARY_SHOTS]
    primary_aggregate = next(row for row in aggregates if int(row["shots"]) == PRIMARY_SHOTS)

    ara_accuracy = float(primary_aggregate["ara_accuracy"])
    z_accuracy = float(primary_aggregate["z_accuracy"])
    rotation_accuracy = float(primary_aggregate["rotation_direction_accuracy"])
    ridge_accuracy = float(primary_aggregate["ridge_u_vs_t2_accuracy"])
    heldout_mae = float(primary_aggregate["heldout_mae"])
    max_score_diff = float(primary_aggregate["ara_bloch_max_score_diff"])
    disagreements = int(primary_aggregate["ara_bloch_disagreements"])
    time_shuffle_accuracy = float(primary_aggregate["time_shuffle_accuracy"])
    axis_shuffle_accuracy = float(primary_aggregate["axis_shuffle_accuracy"])

    gates = {
        "four_class_accuracy": {
            "value": ara_accuracy,
            "criterion": ">= 0.90",
            "passed": ara_accuracy >= 0.90,
        },
        "gain_over_z": {
            "value": ara_accuracy - z_accuracy,
            "criterion": ">= 0.30",
            "passed": ara_accuracy - z_accuracy >= 0.30,
        },
        "rotation_direction_accuracy": {
            "value": rotation_accuracy,
            "criterion": ">= 0.90",
            "passed": rotation_accuracy >= 0.90,
        },
        "u_vs_t2_ridge_accuracy": {
            "value": ridge_accuracy,
            "criterion": ">= 0.95",
            "passed": ridge_accuracy >= 0.95,
        },
        "heldout_directional_mae": {
            "value": heldout_mae,
            "criterion": "<= 0.08",
            "passed": heldout_mae <= 0.08,
        },
        "ara_bloch_max_score_difference": {
            "value": max_score_diff,
            "criterion": "<= 1e-12",
            "passed": max_score_diff <= 1e-12,
        },
        "ara_bloch_classification_disagreements": {
            "value": disagreements,
            "criterion": "== 0",
            "passed": disagreements == 0,
        },
        "time_shuffle_accuracy": {
            "value": time_shuffle_accuracy,
            "criterion": "<= 0.65",
            "passed": time_shuffle_accuracy <= 0.65,
        },
        "axis_shuffle_accuracy": {
            "value": axis_shuffle_accuracy,
            "criterion": "<= 0.65",
            "passed": axis_shuffle_accuracy <= 0.65,
        },
    }
    verdict = "SUPPORTED" if all(item["passed"] for item in gates.values()) else "NOT SUPPORTED"

    rotating_primary = [row for row in primary if row["family"] in ROTATING]
    ridge_primary = [row for row in primary if row["family"] in RIDGE_FAMILIES]
    rotation_wilson = wilson_interval(
        sum(int(row["direction_correct"]) for row in rotating_primary), len(rotating_primary)
    )
    ridge_wilson = wilson_interval(
        sum(int(row["ridge_correct"]) for row in ridge_primary), len(ridge_primary)
    )
    bootstrap = paired_bootstrap(
        primary, np.random.default_rng(CONTROL_SEED + 1), repetitions=5000
    )

    results = {
        "protocol_id": "Q1-OPEN-QUBIT-MULTI-AXIS-v1",
        "ledger_id": "T258",
        "protocol_sha256": actual_hash,
        "registered_primary_shots": PRIMARY_SHOTS,
        "seeds": {
            "development": DEV_SEED,
            "target": TARGET_SEED,
            "heldout_controls": CONTROL_SEED,
        },
        "sample_sizes": {
            "development_base_draws": N_DEV_BASE,
            "development_trials": len(development),
            "target_base_draws": N_TARGET_BASE,
            "target_trials_all_shots": len(trials),
            "primary_trials": len(primary),
            "time_points": N_TIME,
            "heldout_directions_per_trial": N_HELDOUT_DIRECTIONS,
        },
        "thresholds_selected_on_development_only": thresholds,
        "verdict": verdict,
        "primary_gates": gates,
        "primary_aggregate": primary_aggregate,
        "uncertainty_90_percent": {
            **bootstrap,
            "rotation_direction_wilson": list(rotation_wilson),
            "u_vs_t2_ridge_wilson": list(ridge_wilson),
        },
        "confusion_matrices_primary": {
            "ara": confusion(primary, "ara_prediction"),
            "z_only": confusion(primary, "z_prediction"),
            "native_model_fit": confusion(primary, "native_prediction"),
            "time_shuffle": confusion(primary, "time_shuffle_prediction"),
            "axis_shuffle": confusion(primary, "axis_shuffle_prediction"),
        },
        "analytic_invariants": {
            "all_families_initial_state": [1.0, 0.0, 0.0],
            "unitary_and_t2_z_cut_identical": True,
            "t1_and_combined_z_cut_identical_when_t1_paired": True,
            "clean_antipodal_sum": 2.0,
            "ara_bloch_same_information_equivalence_expected": True,
        },
        "interpretive_boundary": {
            "benchmark": "Frozen multi-axis instrument gates only.",
            "geometry": "Several measured diameter cuts retain distinctions hidden from one cut.",
            "not_established": [
                "derivation of quantum mechanics",
                "hidden ontological Phase B",
                "universal fractality",
                "advantage over standard tomography",
            ],
        },
        "files": {
            "development_csv": DEVELOPMENT_CSV.name,
            "trials_csv": TRIALS_CSV.name,
            "aggregates_csv": AGGREGATES_CSV.name,
            "trajectories_csv": TRAJECTORIES_CSV.name,
        },
    }
    RESULTS_JSON.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    print(f"Protocol SHA-256: {actual_hash}")
    print(f"Development thresholds: {json.dumps(thresholds, sort_keys=True)}")
    print(f"Primary ARA accuracy: {ara_accuracy:.6f}")
    print(f"Primary Z-only accuracy: {z_accuracy:.6f}")
    print(f"Primary native-model accuracy: {float(primary_aggregate['native_accuracy']):.6f}")
    print(f"Primary held-out MAE: {heldout_mae:.6f}")
    print(f"Primary verdict: {verdict}")
    print(f"Passed gates: {sum(int(item['passed']) for item in gates.values())}/{len(gates)}")


if __name__ == "__main__":
    main()

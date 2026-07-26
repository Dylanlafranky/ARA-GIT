from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Q16_ARA2_RAW_FOUR_CHILD_RECORDS.csv"
Q17_RESULTS = ROOT / "Q17_CHILD_PHASE_PAIR_RESULTS.json"
PROTOCOL = ROOT / "Q18_GROUPED_DIAMETER_RESIDUAL_PROTOCOL_v1_FROZEN.md"

RESULTS = ROOT / "Q18_GROUPED_DIAMETER_RESIDUAL_RESULTS.json"
METRICS_CSV = ROOT / "Q18_GROUPED_DIAMETER_RESIDUAL_METRICS.csv"
PROJECTIONS_CSV = ROOT / "Q18_GROUPED_DIAMETER_RESIDUAL_PROJECTIONS.csv"
CONTROLS_CSV = ROOT / "Q18_GROUPED_DIAMETER_RESIDUAL_CONTROLS.csv"

EXPECTED_SOURCE_SHA256 = "0f7e58b349e5bf3cdda0110a99627134c7a76c69bb0443be8ba1576c4f01e48b"
EXPECTED_Q17_SHA256 = "3c599b25f991d00ee190612f3c2cbd11dd76605d3924c77e351a0def4b54478a"
EXPECTED_PROTOCOL_SHA256 = "c3833446b6b78c31d48a533be7a3dc235d2e9e9100699f13aa0b7ca65be0035a"

SEED = 20260726
N_CLASS_SHUFFLES = 9_999
N_PIPELINE_SHUFFLES = 9_999
N_PSEUDO = 1_000

CHILDREN = ("C00", "C01", "C10", "C11")
AXES = ("U", "V", "J")
CODES = {
    "U": np.array([1.0, 1.0, -1.0, -1.0]),
    "V": np.array([1.0, -1.0, 1.0, -1.0]),
    "J": np.array([1.0, -1.0, -1.0, 1.0]),
}
PRIMARY_REMOVAL = "J"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator <= np.finfo(float).eps:
        return 0.0
    return float(np.dot(a, b) / denominator)


def grouped_diameter(centroids: np.ndarray, axis: str) -> np.ndarray:
    return np.sum(CODES[axis][:, None] * centroids, axis=0) / 2


def load_arrays() -> tuple[dict[str, np.ndarray], list[str]]:
    frame = pd.read_csv(SOURCE, usecols=["child", "split", "record_index", "cut", "ara_x"])
    cuts = sorted(
        frame["cut"].unique(),
        key=lambda value: (int(value.split("G")[0][1:]), int(value.split("G")[1])),
    )
    if len(cuts) != 45:
        raise RuntimeError(f"expected 45 cuts, found {len(cuts)}")
    if frame.duplicated(["child", "split", "record_index", "cut"]).any():
        raise RuntimeError("duplicate source rows")

    arrays = {}
    for split in ("development", "holdout"):
        split_frame = frame[frame["split"] == split]
        records = sorted(split_frame["record_index"].unique())
        if len(records) != 40:
            raise RuntimeError(f"expected 40 {split} records")
        child_arrays = []
        for child in CHILDREN:
            matrix = (
                split_frame[split_frame["child"] == child]
                .pivot(index="record_index", columns="cut", values="ara_x")
                .reindex(index=records, columns=cuts)
            )
            if matrix.isna().any().any():
                raise RuntimeError(f"incomplete {split}/{child} matrix")
            child_arrays.append(matrix.to_numpy())
        arrays[split] = np.stack(child_arrays)
    return arrays, cuts


def residualize(data: np.ndarray, centre: np.ndarray, unit: np.ndarray) -> np.ndarray:
    centered = data - centre[None, None, :]
    coordinates = np.einsum("irc,c->ir", centered, unit)
    return centered - coordinates[:, :, None] * unit[None, None, :]


def binary_balanced_accuracy(
    scores: np.ndarray,
    code: np.ndarray,
    threshold: float,
    plus_is_high: bool,
) -> float:
    recalls = []
    for child_index, sign in enumerate(code):
        predicted_plus = scores[child_index] >= threshold
        if not plus_is_high:
            predicted_plus = ~predicted_plus
        correct = predicted_plus if sign > 0 else ~predicted_plus
        recalls.append(float(np.mean(correct)))
    return float(np.mean(recalls))


def multiclass_balanced_accuracy(true: np.ndarray, predicted: np.ndarray) -> float:
    recalls = []
    for child_index in range(4):
        mask = true == child_index
        recalls.append(float(np.mean(predicted[mask] == child_index)))
    return float(np.mean(recalls))


def evaluate_removal(
    development: np.ndarray,
    holdout: np.ndarray,
    removed_axis: str,
    keep_records: bool = False,
) -> dict:
    dev_centroids_original = development.mean(axis=1)
    hold_centroids_original = holdout.mean(axis=1)
    development_centre = dev_centroids_original.mean(axis=0)

    original_dev = {axis: grouped_diameter(dev_centroids_original, axis) for axis in AXES}
    original_hold = {axis: grouped_diameter(hold_centroids_original, axis) for axis in AXES}
    removed_norm = float(np.linalg.norm(original_dev[removed_axis]))
    if removed_norm <= np.finfo(float).eps:
        removed_unit = np.zeros(development.shape[2])
    else:
        removed_unit = original_dev[removed_axis] / removed_norm

    dev_residual = residualize(development, development_centre, removed_unit)
    hold_residual = residualize(holdout, development_centre, removed_unit)
    dev_centroids = dev_residual.mean(axis=1)
    hold_centroids = hold_residual.mean(axis=1)

    residual_dev = {axis: grouped_diameter(dev_centroids, axis) for axis in AXES}
    residual_hold = {axis: grouped_diameter(hold_centroids, axis) for axis in AXES}

    original_hold_norm = float(np.linalg.norm(original_hold[removed_axis]))
    removed_leakage = (
        float(np.linalg.norm(residual_hold[removed_axis]) / original_hold_norm)
        if original_hold_norm > np.finfo(float).eps
        else float("inf")
    )

    remaining = [axis for axis in AXES if axis != removed_axis]
    remaining_metrics = {}
    residual_units = {}
    for axis in remaining:
        dev_original_norm = float(np.linalg.norm(original_dev[axis]))
        dev_residual_norm = float(np.linalg.norm(residual_dev[axis]))
        retention = (
            dev_residual_norm / dev_original_norm
            if dev_original_norm > np.finfo(float).eps
            else 0.0
        )
        persistence = abs(cosine(residual_dev[axis], residual_hold[axis]))
        unit = (
            residual_dev[axis] / dev_residual_norm
            if dev_residual_norm > np.finfo(float).eps
            else np.zeros(development.shape[2])
        )
        residual_units[axis] = unit

        dev_scores = np.einsum("irc,c->ir", dev_residual, unit)
        hold_scores = np.einsum("irc,c->ir", hold_residual, unit)
        plus_children = np.where(CODES[axis] > 0)[0]
        minus_children = np.where(CODES[axis] < 0)[0]
        plus_mean = float(dev_scores[plus_children].mean())
        minus_mean = float(dev_scores[minus_children].mean())
        threshold = (plus_mean + minus_mean) / 2
        accuracy = binary_balanced_accuracy(
            hold_scores,
            CODES[axis],
            threshold,
            plus_is_high=plus_mean >= minus_mean,
        )
        remaining_metrics[axis] = {
            "development_energy_retention": float(retention),
            "holdout_persistence": float(persistence),
            "holdout_phase_ab_balanced_accuracy": float(accuracy),
            "development_midpoint_threshold": float(threshold),
            "development_plus_mean": plus_mean,
            "development_minus_mean": minus_mean,
        }

    residual_axis_cosine = abs(cosine(residual_dev[remaining[0]], residual_dev[remaining[1]]))

    hold_centered_centroids = hold_centroids - hold_centroids.mean(axis=0)
    singular_values = np.linalg.svd(hold_centered_centroids, compute_uv=False)
    singular_energy = singular_values**2
    rank_two_energy_share = (
        float(singular_energy[:2].sum() / singular_energy.sum())
        if singular_energy.sum() > np.finfo(float).eps
        else 0.0
    )

    dev_coordinates = np.stack(
        [np.einsum("irc,c->ir", dev_residual, residual_units[axis]) for axis in remaining],
        axis=-1,
    )
    hold_coordinates = np.stack(
        [np.einsum("irc,c->ir", hold_residual, residual_units[axis]) for axis in remaining],
        axis=-1,
    )
    dev_child_centres_2d = dev_coordinates.mean(axis=1)
    hold_flat = hold_coordinates.reshape(-1, 2)
    distances = np.linalg.norm(
        hold_flat[:, None, :] - dev_child_centres_2d[None, :, :],
        axis=2,
    )
    predicted = distances.argmin(axis=1)
    true = np.repeat(np.arange(4), holdout.shape[1])
    four_child_accuracy = multiclass_balanced_accuracy(true, predicted)

    output = {
        "removed_axis": removed_axis,
        "remaining_axes": remaining,
        "removed_holdout_leakage": float(removed_leakage),
        "remaining": remaining_metrics,
        "remaining_axis_absolute_cosine": float(residual_axis_cosine),
        "holdout_rank_two_energy_share": rank_two_energy_share,
        "holdout_singular_values": singular_values.tolist(),
        "four_child_holdout_balanced_accuracy": float(four_child_accuracy),
        "four_child_true": true,
        "four_child_predicted": predicted,
    }
    if keep_records:
        output["development_coordinates"] = dev_coordinates
        output["holdout_coordinates"] = hold_coordinates
    return output


def deterministic_gates(result: dict, classification_q99: float) -> dict:
    remaining = result["remaining"]
    return {
        "G1_removed_holdout_leakage_at_most_0_25": result["removed_holdout_leakage"] <= 0.25,
        "G2_both_development_retentions_at_least_0_75": min(
            value["development_energy_retention"] for value in remaining.values()
        )
        >= 0.75,
        "G3_both_holdout_persistences_at_least_0_80": min(
            value["holdout_persistence"] for value in remaining.values()
        )
        >= 0.80,
        "G4_both_phase_ab_accuracies_at_least_0_80": min(
            value["holdout_phase_ab_balanced_accuracy"] for value in remaining.values()
        )
        >= 0.80,
        "G5_holdout_rank_two_energy_share_at_least_0_95": result[
            "holdout_rank_two_energy_share"
        ]
        >= 0.95,
        "G6_remaining_axis_absolute_cosine_at_most_0_80": result[
            "remaining_axis_absolute_cosine"
        ]
        <= 0.80,
        "G7_four_child_accuracy_and_shuffle": result[
            "four_child_holdout_balanced_accuracy"
        ]
        >= 0.70
        and result["four_child_holdout_balanced_accuracy"] > classification_q99,
    }


def holdout_label_null(
    true: np.ndarray,
    predicted: np.ndarray,
    rng: np.random.Generator,
) -> dict:
    values = np.empty(N_CLASS_SHUFFLES, dtype=float)
    for iteration in range(N_CLASS_SHUFFLES):
        values[iteration] = multiclass_balanced_accuracy(rng.permutation(true), predicted)
    observed = multiclass_balanced_accuracy(true, predicted)
    return {
        "iterations": N_CLASS_SHUFFLES,
        "observed": float(observed),
        "null_99th_percentile": float(np.quantile(values, 0.99)),
        "p_value": float((1 + np.sum(values >= observed)) / (N_CLASS_SHUFFLES + 1)),
        "null_mean": float(values.mean()),
    }


def balanced_shuffle(data: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    children, records, cuts = data.shape
    pooled = data.reshape(children * records, cuts)
    return pooled[rng.permutation(len(pooled))].reshape(children, records, cuts)


def pseudo_children(data: np.ndarray, source_index: int, rng: np.random.Generator) -> np.ndarray:
    source = data[source_index]
    return source[rng.permutation(len(source))].reshape(4, len(source) // 4, source.shape[1])


def clean_result(result: dict) -> dict:
    excluded = {
        "four_child_true",
        "four_child_predicted",
        "development_coordinates",
        "holdout_coordinates",
    }
    output = {}
    for key, value in result.items():
        if key in excluded:
            continue
        if isinstance(value, dict):
            output[key] = clean_result(value)
        elif isinstance(value, np.ndarray):
            output[key] = value.tolist()
        elif isinstance(value, np.generic):
            output[key] = value.item()
        else:
            output[key] = value
    return output


def projection_rows(result: dict, split: str) -> list[dict]:
    coordinates = result[
        "development_coordinates" if split == "development" else "holdout_coordinates"
    ]
    axes = result["remaining_axes"]
    rows = []
    for child_index, child in enumerate(CHILDREN):
        for record_index in range(coordinates.shape[1]):
            rows.append(
                {
                    "removed_axis": result["removed_axis"],
                    "split": split,
                    "child": child,
                    "record_index": record_index,
                    f"coordinate_{axes[0]}": coordinates[child_index, record_index, 0],
                    f"coordinate_{axes[1]}": coordinates[child_index, record_index, 1],
                }
            )
    return rows


if __name__ == "__main__":
    source_hash = sha256(SOURCE)
    q17_hash = sha256(Q17_RESULTS)
    protocol_hash = sha256(PROTOCOL)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(f"source hash mismatch: {source_hash}")
    if q17_hash != EXPECTED_Q17_SHA256:
        raise RuntimeError(f"Q17 result hash mismatch: {q17_hash}")
    if protocol_hash != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError(f"protocol hash mismatch: {protocol_hash}")

    arrays, cuts = load_arrays()
    rng = np.random.default_rng(SEED)

    removals = {}
    class_nulls = {}
    projection_output = []
    for removed_axis in ("J", "U", "V"):
        result = evaluate_removal(
            arrays["development"],
            arrays["holdout"],
            removed_axis,
            keep_records=True,
        )
        null = holdout_label_null(
            result["four_child_true"],
            result["four_child_predicted"],
            rng,
        )
        gates = deterministic_gates(result, null["null_99th_percentile"])
        result["classification_null"] = null
        result["gates_1_to_7"] = gates
        result["passes_gates_1_to_7"] = all(gates.values())
        removals[removed_axis] = result
        class_nulls[removed_axis] = null
        projection_output.extend(projection_rows(result, "development"))
        projection_output.extend(projection_rows(result, "holdout"))

    primary_q99 = class_nulls[PRIMARY_REMOVAL]["null_99th_percentile"]
    controls = []
    pipeline_passes = 0
    for iteration in range(N_PIPELINE_SHUFFLES):
        dev = balanced_shuffle(arrays["development"], rng)
        hold = balanced_shuffle(arrays["holdout"], rng)
        result = evaluate_removal(dev, hold, PRIMARY_REMOVAL)
        gates = deterministic_gates(result, primary_q99)
        passed = all(gates.values())
        pipeline_passes += int(passed)
        controls.append(
            {
                "control_type": "balanced_label_full_pipeline",
                "iteration": iteration,
                "source_child": "",
                "removed_holdout_leakage": result["removed_holdout_leakage"],
                "minimum_retention": min(
                    value["development_energy_retention"] for value in result["remaining"].values()
                ),
                "minimum_persistence": min(
                    value["holdout_persistence"] for value in result["remaining"].values()
                ),
                "minimum_phase_ab_accuracy": min(
                    value["holdout_phase_ab_balanced_accuracy"]
                    for value in result["remaining"].values()
                ),
                "rank_two_energy_share": result["holdout_rank_two_energy_share"],
                "remaining_axis_absolute_cosine": result["remaining_axis_absolute_cosine"],
                "four_child_accuracy": result["four_child_holdout_balanced_accuracy"],
                "passes_gates_1_to_7": passed,
            }
        )

    pseudo_passes = 0
    for iteration in range(N_PSEUDO):
        source_index = iteration % 4
        dev = pseudo_children(arrays["development"], source_index, rng)
        hold = pseudo_children(arrays["holdout"], source_index, rng)
        result = evaluate_removal(dev, hold, PRIMARY_REMOVAL)
        gates = deterministic_gates(result, primary_q99)
        passed = all(gates.values())
        pseudo_passes += int(passed)
        controls.append(
            {
                "control_type": "within_archive_pseudo_child",
                "iteration": iteration,
                "source_child": CHILDREN[source_index],
                "removed_holdout_leakage": result["removed_holdout_leakage"],
                "minimum_retention": min(
                    value["development_energy_retention"] for value in result["remaining"].values()
                ),
                "minimum_persistence": min(
                    value["holdout_persistence"] for value in result["remaining"].values()
                ),
                "minimum_phase_ab_accuracy": min(
                    value["holdout_phase_ab_balanced_accuracy"]
                    for value in result["remaining"].values()
                ),
                "rank_two_energy_share": result["holdout_rank_two_energy_share"],
                "remaining_axis_absolute_cosine": result["remaining_axis_absolute_cosine"],
                "four_child_accuracy": result["four_child_holdout_balanced_accuracy"],
                "passes_gates_1_to_7": passed,
            }
        )

    pipeline_rate = pipeline_passes / N_PIPELINE_SHUFFLES
    pseudo_rate = pseudo_passes / N_PSEUDO
    gate_8 = pipeline_rate <= 0.01 and pseudo_rate <= 0.05

    primary_gates = removals[PRIMARY_REMOVAL]["gates_1_to_7"]
    all_primary_gates = {**primary_gates, "G8_control_rates": gate_8}
    primary_verdict = "SUPPORTED" if all(all_primary_gates.values()) else "NOT SUPPORTED"
    symmetry_supported = all(removals[axis]["passes_gates_1_to_7"] for axis in AXES)

    metric_rows = []
    for removed_axis, result in removals.items():
        for remaining_axis, metrics in result["remaining"].items():
            metric_rows.append(
                {
                    "removed_axis": removed_axis,
                    "remaining_axis": remaining_axis,
                    "primary_removal": removed_axis == PRIMARY_REMOVAL,
                    "removed_holdout_leakage": result["removed_holdout_leakage"],
                    **metrics,
                    "remaining_axis_absolute_cosine": result["remaining_axis_absolute_cosine"],
                    "holdout_rank_two_energy_share": result["holdout_rank_two_energy_share"],
                    "four_child_holdout_balanced_accuracy": result[
                        "four_child_holdout_balanced_accuracy"
                    ],
                    "classification_null_99th": result["classification_null"][
                        "null_99th_percentile"
                    ],
                    "classification_p_value": result["classification_null"]["p_value"],
                    "passes_gates_1_to_7": result["passes_gates_1_to_7"],
                }
            )

    pd.DataFrame(metric_rows).to_csv(METRICS_CSV, index=False)
    pd.DataFrame(projection_output).to_csv(PROJECTIONS_CSV, index=False)
    pd.DataFrame(controls).to_csv(CONTROLS_CSV, index=False)

    output = {
        "claim_id": "Q18-GROUP-RESIDUAL-v1",
        "seed": SEED,
        "source": SOURCE.name,
        "source_sha256": source_hash,
        "q17_result": Q17_RESULTS.name,
        "q17_result_sha256": q17_hash,
        "protocol": PROTOCOL.name,
        "protocol_sha256": protocol_hash,
        "cuts": cuts,
        "primary_removed_axis": PRIMARY_REMOVAL,
        "removals": {axis: clean_result(result) for axis, result in removals.items()},
        "primary_all_gates": all_primary_gates,
        "primary_verdict": primary_verdict,
        "secondary_three_diameter_residual_symmetry_supported": symmetry_supported,
        "controls": {
            "balanced_label_full_pipeline_iterations": N_PIPELINE_SHUFFLES,
            "balanced_label_full_pipeline_passes": pipeline_passes,
            "balanced_label_full_pipeline_rate": pipeline_rate,
            "within_archive_pseudo_child_iterations": N_PSEUDO,
            "within_archive_pseudo_child_passes": pseudo_passes,
            "within_archive_pseudo_child_rate": pseudo_rate,
        },
        "evidence_class": "exploratory same-deposit residual test; independent replication required",
    }
    RESULTS.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "primary_removed_axis": PRIMARY_REMOVAL,
                "primary_verdict": primary_verdict,
                "primary_gates": all_primary_gates,
                "secondary_three_diameter_residual_symmetry_supported": symmetry_supported,
                "removal_summary": {
                    axis: {
                        "leakage": result["removed_holdout_leakage"],
                        "remaining_axes": result["remaining_axes"],
                        "minimum_retention": min(
                            value["development_energy_retention"]
                            for value in result["remaining"].values()
                        ),
                        "minimum_persistence": min(
                            value["holdout_persistence"] for value in result["remaining"].values()
                        ),
                        "minimum_phase_ab_accuracy": min(
                            value["holdout_phase_ab_balanced_accuracy"]
                            for value in result["remaining"].values()
                        ),
                        "rank_two_share": result["holdout_rank_two_energy_share"],
                        "axis_cosine": result["remaining_axis_absolute_cosine"],
                        "four_child_accuracy": result["four_child_holdout_balanced_accuracy"],
                        "passes_gates_1_to_7": result["passes_gates_1_to_7"],
                    }
                    for axis, result in removals.items()
                },
                "pipeline_control_rate": pipeline_rate,
                "pseudo_control_rate": pseudo_rate,
            },
            indent=2,
        )
    )

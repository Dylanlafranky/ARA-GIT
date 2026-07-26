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
PRIMARY_CODE = ROOT / "q18_grouped_diameter_residual_test.py"
RESULTS = ROOT / "Q18_GROUPED_DIAMETER_RESIDUAL_RESULTS.json"
METRICS = ROOT / "Q18_GROUPED_DIAMETER_RESIDUAL_METRICS.csv"
PROJECTIONS = ROOT / "Q18_GROUPED_DIAMETER_RESIDUAL_PROJECTIONS.csv"
CONTROLS = ROOT / "Q18_GROUPED_DIAMETER_RESIDUAL_CONTROLS.csv"
VALIDATION = ROOT / "Q18_GROUPED_DIAMETER_RESIDUAL_VALIDATION.json"

EXPECTED_SOURCE_HASH = "0f7e58b349e5bf3cdda0110a99627134c7a76c69bb0443be8ba1576c4f01e48b"
EXPECTED_Q17_HASH = "3c599b25f991d00ee190612f3c2cbd11dd76605d3924c77e351a0def4b54478a"
EXPECTED_PROTOCOL_HASH = "c3833446b6b78c31d48a533be7a3dc235d2e9e9100699f13aa0b7ca65be0035a"

CHILDREN = ("C00", "C01", "C10", "C11")
AXES = ("U", "V", "J")
CODES = {
    "U": np.array([1.0, 1.0, -1.0, -1.0]),
    "V": np.array([1.0, -1.0, 1.0, -1.0]),
    "J": np.array([1.0, -1.0, -1.0, 1.0]),
}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    return 0.0 if denominator <= np.finfo(float).eps else float(np.dot(a, b) / denominator)


def grouped(centroids: np.ndarray, axis: str) -> np.ndarray:
    return np.sum(CODES[axis][:, None] * centroids, axis=0) / 2


def load_source() -> tuple[dict[str, np.ndarray], list[str], pd.DataFrame]:
    frame = pd.read_csv(SOURCE, usecols=["child", "split", "record_index", "cut", "ara_x"])
    cuts = sorted(
        frame["cut"].unique(),
        key=lambda value: (int(value.split("G")[0][1:]), int(value.split("G")[1])),
    )
    arrays = {}
    for split in ("development", "holdout"):
        split_frame = frame[frame["split"] == split]
        records = sorted(split_frame["record_index"].unique())
        matrices = []
        for child in CHILDREN:
            matrix = (
                split_frame[split_frame["child"] == child]
                .pivot(index="record_index", columns="cut", values="ara_x")
                .reindex(index=records, columns=cuts)
            )
            matrices.append(matrix.to_numpy())
        arrays[split] = np.stack(matrices)
    return arrays, cuts, frame


def residual_geometry(development: np.ndarray, holdout: np.ndarray, removed: str) -> dict:
    dev_original_centroids = development.mean(axis=1)
    hold_original_centroids = holdout.mean(axis=1)
    centre = dev_original_centroids.mean(axis=0)
    dev_original = {axis: grouped(dev_original_centroids, axis) for axis in AXES}
    hold_original = {axis: grouped(hold_original_centroids, axis) for axis in AXES}

    removed_unit = dev_original[removed] / np.linalg.norm(dev_original[removed])

    def remove(data: np.ndarray) -> np.ndarray:
        centered = data - centre[None, None, :]
        score = np.einsum("irc,c->ir", centered, removed_unit)
        return centered - score[:, :, None] * removed_unit[None, None, :]

    dev = remove(development)
    hold = remove(holdout)
    dev_centroids = dev.mean(axis=1)
    hold_centroids = hold.mean(axis=1)
    dev_diameters = {axis: grouped(dev_centroids, axis) for axis in AXES}
    hold_diameters = {axis: grouped(hold_centroids, axis) for axis in AXES}

    remaining_axes = [axis for axis in AXES if axis != removed]
    remaining = {}
    units = {}
    for axis in remaining_axes:
        dev_norm = float(np.linalg.norm(dev_diameters[axis]))
        units[axis] = dev_diameters[axis] / dev_norm
        dev_scores = np.einsum("irc,c->ir", dev, units[axis])
        hold_scores = np.einsum("irc,c->ir", hold, units[axis])
        plus = np.where(CODES[axis] > 0)[0]
        minus = np.where(CODES[axis] < 0)[0]
        plus_mean = float(dev_scores[plus].mean())
        minus_mean = float(dev_scores[minus].mean())
        threshold = (plus_mean + minus_mean) / 2
        plus_is_high = plus_mean >= minus_mean
        recalls = []
        for child_index, sign in enumerate(CODES[axis]):
            prediction = hold_scores[child_index] >= threshold
            if not plus_is_high:
                prediction = ~prediction
            correct = prediction if sign > 0 else ~prediction
            recalls.append(float(np.mean(correct)))
        remaining[axis] = {
            "development_energy_retention": float(
                dev_norm / np.linalg.norm(dev_original[axis])
            ),
            "holdout_persistence": abs(cosine(dev_diameters[axis], hold_diameters[axis])),
            "holdout_phase_ab_balanced_accuracy": float(np.mean(recalls)),
            "development_midpoint_threshold": float(threshold),
            "development_plus_mean": plus_mean,
            "development_minus_mean": minus_mean,
        }

    centered_hold_centroids = hold_centroids - hold_centroids.mean(axis=0)
    singular_values = np.linalg.svd(centered_hold_centroids, compute_uv=False)
    singular_energy = singular_values**2

    dev_coordinates = np.stack(
        [np.einsum("irc,c->ir", dev, units[axis]) for axis in remaining_axes],
        axis=-1,
    )
    hold_coordinates = np.stack(
        [np.einsum("irc,c->ir", hold, units[axis]) for axis in remaining_axes],
        axis=-1,
    )
    child_centres = dev_coordinates.mean(axis=1)
    flat = hold_coordinates.reshape(-1, 2)
    prediction = np.linalg.norm(flat[:, None, :] - child_centres[None, :, :], axis=2).argmin(axis=1)
    truth = np.repeat(np.arange(4), holdout.shape[1])
    recalls = [float(np.mean(prediction[truth == child] == child)) for child in range(4)]

    return {
        "removed_holdout_leakage": float(
            np.linalg.norm(hold_diameters[removed]) / np.linalg.norm(hold_original[removed])
        ),
        "remaining": remaining,
        "remaining_axis_absolute_cosine": abs(
            cosine(dev_diameters[remaining_axes[0]], dev_diameters[remaining_axes[1]])
        ),
        "holdout_rank_two_energy_share": float(
            singular_energy[:2].sum() / singular_energy.sum()
        ),
        "holdout_singular_values": singular_values,
        "four_child_holdout_balanced_accuracy": float(np.mean(recalls)),
    }


def gates(result: dict, q99: float) -> dict[str, bool]:
    remaining = result["remaining"]
    return {
        "G1_removed_holdout_leakage_at_most_0_25": result["removed_holdout_leakage"] <= 0.25,
        "G2_both_development_retentions_at_least_0_75": min(
            item["development_energy_retention"] for item in remaining.values()
        )
        >= 0.75,
        "G3_both_holdout_persistences_at_least_0_80": min(
            item["holdout_persistence"] for item in remaining.values()
        )
        >= 0.80,
        "G4_both_phase_ab_accuracies_at_least_0_80": min(
            item["holdout_phase_ab_balanced_accuracy"] for item in remaining.values()
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
        and result["four_child_holdout_balanced_accuracy"] > q99,
    }


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return bool(abs(float(left) - float(right)) <= tolerance)


if __name__ == "__main__":
    saved = json.loads(RESULTS.read_text(encoding="utf-8"))
    arrays, cuts, frame = load_source()
    checks: dict[str, bool] = {
        "source_hash": file_hash(SOURCE) == EXPECTED_SOURCE_HASH == saved["source_sha256"],
        "q17_hash": file_hash(Q17_RESULTS) == EXPECTED_Q17_HASH == saved["q17_result_sha256"],
        "protocol_hash": file_hash(PROTOCOL) == EXPECTED_PROTOCOL_HASH == saved["protocol_sha256"],
        "row_count_14400": len(frame) == 14_400,
        "cut_count_45": len(cuts) == 45,
        "no_duplicate_rows": not frame.duplicated(
            ["child", "split", "record_index", "cut"]
        ).any(),
        "metrics_rows_6": len(pd.read_csv(METRICS)) == 6,
        "projection_rows_960": len(pd.read_csv(PROJECTIONS)) == 960,
    }

    computed = {}
    for removed in ("J", "U", "V"):
        result = residual_geometry(arrays["development"], arrays["holdout"], removed)
        computed[removed] = result
        expected = saved["removals"][removed]
        for field in (
            "removed_holdout_leakage",
            "remaining_axis_absolute_cosine",
            "holdout_rank_two_energy_share",
            "four_child_holdout_balanced_accuracy",
        ):
            checks[f"{removed}_{field}"] = close(result[field], expected[field])
        checks[f"{removed}_singular_values"] = bool(
            np.allclose(
                result["holdout_singular_values"],
                expected["holdout_singular_values"],
                rtol=0,
                atol=1e-12,
            )
        )
        for axis, axis_result in result["remaining"].items():
            for field, value in axis_result.items():
                checks[f"{removed}_{axis}_{field}"] = close(
                    value, expected["remaining"][axis][field]
                )
        recomputed_gates = gates(
            result, expected["classification_null"]["null_99th_percentile"]
        )
        checks[f"{removed}_gate_vector"] = recomputed_gates == expected["gates_1_to_7"]
        checks[f"{removed}_pass_consistency"] = expected["passes_gates_1_to_7"] == all(
            recomputed_gates.values()
        )

    controls = pd.read_csv(CONTROLS)
    pipeline = controls[controls["control_type"] == "balanced_label_full_pipeline"]
    pseudo = controls[controls["control_type"] == "within_archive_pseudo_child"]
    checks.update(
        {
            "pipeline_rows_9999": len(pipeline) == 9_999,
            "pseudo_rows_1000": len(pseudo) == 1_000,
            "pipeline_pass_count": int(pipeline["passes_gates_1_to_7"].sum())
            == saved["controls"]["balanced_label_full_pipeline_passes"],
            "pseudo_pass_count": int(pseudo["passes_gates_1_to_7"].sum())
            == saved["controls"]["within_archive_pseudo_child_passes"],
            "pipeline_rate": close(
                pipeline["passes_gates_1_to_7"].mean(),
                saved["controls"]["balanced_label_full_pipeline_rate"],
            ),
            "pseudo_rate": close(
                pseudo["passes_gates_1_to_7"].mean(),
                saved["controls"]["within_archive_pseudo_child_rate"],
            ),
        }
    )

    primary = computed["J"]
    primary_saved = saved["removals"]["J"]
    primary_gates = gates(
        primary, primary_saved["classification_null"]["null_99th_percentile"]
    )
    gate_8 = (
        saved["controls"]["balanced_label_full_pipeline_rate"] <= 0.01
        and saved["controls"]["within_archive_pseudo_child_rate"] <= 0.05
    )
    complete_primary = {**primary_gates, "G8_control_rates": gate_8}
    checks["primary_complete_gate_vector"] = complete_primary == saved["primary_all_gates"]
    checks["primary_verdict_consistent"] = saved["primary_verdict"] == (
        "SUPPORTED" if all(complete_primary.values()) else "NOT SUPPORTED"
    )
    checks["secondary_verdict_consistent"] = saved[
        "secondary_three_diameter_residual_symmetry_supported"
    ] == all(saved["removals"][axis]["passes_gates_1_to_7"] for axis in AXES)

    code_text = PRIMARY_CODE.read_text(encoding="utf-8").lower()
    checks["primary_code_has_no_protocol_forbidden_quantum_names"] = not any(
        token in code_text
        for token in (
            "ramsey",
            "hahn",
            "bell",
            "pauli",
            "phi-plus",
            "phi-minus",
            "psi-plus",
            "psi-minus",
        )
    )

    failures = [name for name, passed in checks.items() if not passed]
    output = {
        "validator": Path(__file__).name,
        "primary_code_imported": False,
        "checks_run": len(checks),
        "checks_passed": len(checks) - len(failures),
        "failed_checks": failures,
        "all_checks_pass": not failures,
        "validated_primary_gate_vector": complete_primary,
        "validated_primary_verdict": saved["primary_verdict"],
        "validated_secondary_three_diameter_residual_symmetry_supported": saved[
            "secondary_three_diameter_residual_symmetry_supported"
        ],
    }
    VALIDATION.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    if failures:
        raise SystemExit(1)

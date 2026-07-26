from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Q16_ARA2_RAW_FOUR_CHILD_RECORDS.csv"
Q16_RESULTS = ROOT / "Q16_ARA2_RAW_FOUR_CHILD_RESULTS.json"
Q18_RESULTS = ROOT / "Q18_GROUPED_DIAMETER_RESIDUAL_RESULTS.json"
TIER_MAP = ROOT / "ARA_QUANTUM_FRACTAL_TIER_MAP_2026-07-26.md"
PROTOCOL = ROOT / "Q19_TIER3_DOUBLE_DIAGONAL_ABLATION_PROTOCOL_v1_FROZEN.md"

RESULTS = ROOT / "Q19_TIER3_DOUBLE_DIAGONAL_ABLATION_RESULTS.json"
METRICS = ROOT / "Q19_TIER3_DOUBLE_DIAGONAL_ABLATION_METRICS.csv"
PROJECTIONS = ROOT / "Q19_TIER3_DOUBLE_DIAGONAL_ABLATION_PROJECTIONS.csv"
CONTROLS = ROOT / "Q19_TIER3_DOUBLE_DIAGONAL_ABLATION_CONTROLS.csv"

EXPECTED_HASHES = {
    SOURCE: "0f7e58b349e5bf3cdda0110a99627134c7a76c69bb0443be8ba1576c4f01e48b",
    Q16_RESULTS: "30c5b458505ffdb54c9ee1b115ca1518cf6aa8cd185a474da0df5a28bd1ad3a4",
    Q18_RESULTS: "02f18498612b67f28df46695ef054285547a0f5f43c41eb96ad6d2b8fdf59b1d",
    TIER_MAP: "92f488264def3ef2c13c9d3bf79a0d06db6f74ae90ac25fe50bb6299cd91b113",
    PROTOCOL: "7c413ff705982d1f0a42d3786e42825a24a51d6eabd744e98c0d0d5d2e7af84b",
}

SEED = 20260726
N_LABEL_CONTROLS = 9_999
N_PSEUDO_CONTROLS = 1_000

CHILDREN = ("C00", "C01", "C10", "C11")
J_CODE = np.array([1.0, -1.0, -1.0, 1.0])
BRANCHES = {
    "AA": {"pairs": ((0, 1), (0, 2)), "triple": (0, 1, 2), "survivor": 3},
    "AB": {"pairs": ((0, 1), (1, 3)), "triple": (0, 1, 3), "survivor": 2},
    "BA": {"pairs": ((2, 3), (0, 2)), "triple": (0, 2, 3), "survivor": 1},
    "BB": {"pairs": ((2, 3), (1, 3)), "triple": (1, 2, 3), "survivor": 0},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_arrays() -> tuple[dict[str, np.ndarray], list[str], pd.DataFrame]:
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
            if matrix.isna().any().any():
                raise RuntimeError(f"incomplete source matrix: {split}/{child}")
            matrices.append(matrix.to_numpy())
        arrays[split] = np.stack(matrices)
    return arrays, cuts, frame


def cosine(left: np.ndarray, right: np.ndarray) -> float:
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    return 0.0 if denominator <= np.finfo(float).eps else float(np.dot(left, right) / denominator)


def branch_basis(centroids: np.ndarray, branch: str) -> dict:
    pairs = BRANCHES[branch]["pairs"]
    diagonals = np.stack([centroids[i] - centroids[j] for i, j in pairs])
    _, singular_values, right = np.linalg.svd(diagonals, full_matrices=False)
    rank = int(np.sum(singular_values > singular_values[0] * 1e-10))
    basis = right[:rank].T
    acute_angle = float(np.degrees(np.arccos(np.clip(abs(cosine(diagonals[0], diagonals[1])), 0, 1))))
    return {
        "basis": basis,
        "diagonals": diagonals,
        "singular_values": singular_values,
        "rank": rank,
        "acute_angle_degrees": acute_angle,
    }


def remove_span(data: np.ndarray, centre: np.ndarray, basis: np.ndarray) -> np.ndarray:
    centered = data - centre[None, None, :]
    coordinates = np.einsum("irc,ck->irk", centered, basis)
    return centered - np.einsum("irk,ck->irc", coordinates, basis)


def grouped_j(centroids: np.ndarray) -> np.ndarray:
    return np.sum(J_CODE[:, None] * centroids, axis=0) / 2


def centered_energy(centroids: np.ndarray) -> float:
    centered = centroids - centroids.mean(axis=0)
    return float(np.sum(centered**2))


def balanced_four_accuracy(truth: np.ndarray, prediction: np.ndarray) -> float:
    return float(
        np.mean(
            [
                np.mean(prediction[truth == child_index] == child_index)
                for child_index in range(4)
            ]
        )
    )


def evaluate_with_basis(
    development: np.ndarray,
    holdout: np.ndarray,
    branch: str,
    basis_info: dict,
    keep_records: bool = False,
) -> dict:
    dev_original_centroids = development.mean(axis=1)
    hold_original_centroids = holdout.mean(axis=1)
    centre = dev_original_centroids.mean(axis=0)
    basis = basis_info["basis"]

    dev_residual = remove_span(development, centre, basis)
    hold_residual = remove_span(holdout, centre, basis)
    dev_centroids = dev_residual.mean(axis=1)
    hold_centroids = hold_residual.mean(axis=1)

    triple = np.array(BRANCHES[branch]["triple"])
    survivor = int(BRANCHES[branch]["survivor"])
    dev_triple_centre = dev_centroids[triple].mean(axis=0)
    hold_triple_centre = hold_centroids[triple].mean(axis=0)

    within_rms = float(
        np.sqrt(np.mean(np.sum((hold_centroids[triple] - hold_triple_centre) ** 2, axis=1)))
    )
    survivor_distance = float(np.linalg.norm(hold_centroids[survivor] - hold_triple_centre))
    merge_ratio = (
        within_rms / survivor_distance
        if survivor_distance > np.finfo(float).eps
        else float("inf")
    )

    hold_flat = hold_residual.reshape(-1, hold_residual.shape[-1])
    truth_child = np.repeat(np.arange(4), holdout.shape[1])
    distance_survivor = np.linalg.norm(hold_flat - dev_centroids[survivor], axis=1)
    distance_triple = np.linalg.norm(hold_flat - dev_triple_centre, axis=1)
    predict_survivor = distance_survivor < distance_triple
    true_survivor = truth_child == survivor
    survivor_recall = float(np.mean(predict_survivor[true_survivor]))
    triple_recall = float(np.mean(~predict_survivor[~true_survivor]))
    binary_accuracy = (survivor_recall + triple_recall) / 2

    distances_four = np.linalg.norm(
        hold_flat[:, None, :] - dev_centroids[None, :, :],
        axis=2,
    )
    prediction_four = distances_four.argmin(axis=1)
    four_accuracy = balanced_four_accuracy(truth_child, prediction_four)

    hold_centered = hold_centroids - hold_centroids.mean(axis=0)
    singular_values = np.linalg.svd(hold_centered, compute_uv=False)
    singular_energy = singular_values**2
    rank_one_share = float(singular_energy[0] / singular_energy.sum())

    original_j_norm = float(np.linalg.norm(grouped_j(hold_original_centroids)))
    residual_j_norm = float(np.linalg.norm(grouped_j(hold_centroids)))
    j_retention = residual_j_norm / original_j_norm
    energy_retention = centered_energy(hold_centroids) / centered_energy(hold_original_centroids)

    original_dev_flat = development.reshape(-1, development.shape[-1])
    original_truth = np.repeat(np.arange(4), development.shape[1])
    original_dev_centroids = development.mean(axis=1)
    original_hold_flat = holdout.reshape(-1, holdout.shape[-1])
    original_distances = np.linalg.norm(
        original_hold_flat[:, None, :] - original_dev_centroids[None, :, :],
        axis=2,
    )
    original_four_accuracy = balanced_four_accuracy(
        np.repeat(np.arange(4), holdout.shape[1]),
        original_distances.argmin(axis=1),
    )
    del original_dev_flat, original_truth

    result = {
        "branch": branch,
        "removed_pairs": [
            [CHILDREN[i], CHILDREN[j]] for i, j in BRANCHES[branch]["pairs"]
        ],
        "predicted_survivor": CHILDREN[survivor],
        "predicted_merging_triple": [CHILDREN[index] for index in triple],
        "development_diagonal_rank": int(basis_info["rank"]),
        "development_diagonal_angle_degrees": float(basis_info["acute_angle_degrees"]),
        "development_diagonal_singular_values": basis_info["singular_values"].tolist(),
        "holdout_merge_ratio": float(merge_ratio),
        "holdout_within_triple_rms": within_rms,
        "holdout_survivor_distance": survivor_distance,
        "holdout_survivor_binary_balanced_accuracy": float(binary_accuracy),
        "holdout_survivor_recall": survivor_recall,
        "holdout_triple_recall": triple_recall,
        "holdout_rank_one_energy_share": rank_one_share,
        "holdout_centroid_singular_values": singular_values.tolist(),
        "tier1_j_holdout_retention": float(j_retention),
        "holdout_between_child_energy_retention": float(energy_retention),
        "holdout_four_child_nearest_accuracy": float(four_accuracy),
        "original_holdout_four_child_nearest_accuracy": float(original_four_accuracy),
        "four_child_accuracy_loss": float(original_four_accuracy - four_accuracy),
    }
    if keep_records:
        result["development_residual"] = dev_residual
        result["holdout_residual"] = hold_residual
    return result


def evaluate_branch(
    development: np.ndarray,
    holdout: np.ndarray,
    branch: str,
    basis_source: np.ndarray | None = None,
    keep_records: bool = False,
) -> dict:
    source = development if basis_source is None else basis_source
    basis_info = branch_basis(source.mean(axis=1), branch)
    return evaluate_with_basis(development, holdout, branch, basis_info, keep_records)


def deterministic_gates(result: dict) -> dict[str, bool]:
    return {
        "G1_rank_two_and_angle_at_least_15_degrees": result[
            "development_diagonal_rank"
        ]
        == 2
        and result["development_diagonal_angle_degrees"] >= 15,
        "G2_holdout_merge_ratio_at_most_0_50": result["holdout_merge_ratio"] <= 0.50,
        "G3_survivor_binary_accuracy_at_least_0_80": result[
            "holdout_survivor_binary_balanced_accuracy"
        ]
        >= 0.80,
        "G4_holdout_rank_one_share_at_least_0_80": result[
            "holdout_rank_one_energy_share"
        ]
        >= 0.80,
        "G5_tier1_j_retention_at_most_0_75": result["tier1_j_holdout_retention"] <= 0.75,
        "G6_holdout_energy_retention_at_most_0_60": result[
            "holdout_between_child_energy_retention"
        ]
        <= 0.60,
    }


def balanced_pseudo_labels(data: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    pooled = data.reshape(-1, data.shape[-1])
    return pooled[rng.permutation(len(pooled))].reshape(data.shape)


def within_archive_pseudo(data: np.ndarray, source_index: int, rng: np.random.Generator) -> np.ndarray:
    source = data[source_index]
    return source[rng.permutation(len(source))].reshape(4, len(source) // 4, source.shape[-1])


def control_row(control_type: str, iteration: int, result: dict, source_child: str = "") -> dict:
    gates = deterministic_gates(result)
    return {
        "control_type": control_type,
        "iteration": iteration,
        "source_child": source_child,
        "diagonal_angle_degrees": result["development_diagonal_angle_degrees"],
        "merge_ratio": result["holdout_merge_ratio"],
        "survivor_binary_accuracy": result["holdout_survivor_binary_balanced_accuracy"],
        "rank_one_share": result["holdout_rank_one_energy_share"],
        "tier1_j_retention": result["tier1_j_holdout_retention"],
        "between_child_energy_retention": result["holdout_between_child_energy_retention"],
        "passes_gates_1_to_6": all(gates.values()),
    }


def projection_rows(result: dict) -> list[dict]:
    rows = []
    for split_name, key in (
        ("development", "development_residual"),
        ("holdout", "holdout_residual"),
    ):
        data = result[key]
        centroids = data.mean(axis=1)
        centered_centroids = centroids - centroids.mean(axis=0)
        _, _, right = np.linalg.svd(centered_centroids, full_matrices=False)
        axis = right[0]
        coordinates = np.einsum("irc,c->ir", data, axis)
        for child_index, child in enumerate(CHILDREN):
            for record_index in range(data.shape[1]):
                rows.append(
                    {
                        "branch": result["branch"],
                        "split": split_name,
                        "child": child,
                        "record_index": record_index,
                        "residual_axis_1": coordinates[child_index, record_index],
                        "predicted_survivor": result["predicted_survivor"],
                    }
                )
    return rows


def json_clean(result: dict) -> dict:
    excluded = {"development_residual", "holdout_residual"}
    return {
        key: value
        for key, value in result.items()
        if key not in excluded
    }


if __name__ == "__main__":
    hashes = {path.name: sha256(path) for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if hashes[path.name] != expected:
            raise RuntimeError(f"hash mismatch for {path.name}: {hashes[path.name]}")

    arrays, cuts, frame = load_arrays()
    development = arrays["development"]
    holdout = arrays["holdout"]
    rng = np.random.default_rng(SEED)

    branches = {}
    projection_output = []
    metric_rows = []
    for branch in BRANCHES:
        result = evaluate_branch(development, holdout, branch, keep_records=True)
        result["gates_1_to_6"] = deterministic_gates(result)
        result["passes_gates_1_to_6"] = all(result["gates_1_to_6"].values())
        branches[branch] = result
        projection_output.extend(projection_rows(result))
        metric_rows.append(json_clean(result))

    controls = []
    label_passes = 0
    label_binary = np.empty(N_LABEL_CONTROLS)
    label_merge = np.empty(N_LABEL_CONTROLS)
    for iteration in range(N_LABEL_CONTROLS):
        pseudo = balanced_pseudo_labels(development, rng)
        result = evaluate_branch(development, holdout, "AA", basis_source=pseudo)
        row = control_row("balanced_development_labels", iteration, result)
        label_binary[iteration] = row["survivor_binary_accuracy"]
        label_merge[iteration] = row["merge_ratio"]
        label_passes += int(row["passes_gates_1_to_6"])
        controls.append(row)

    pseudo_passes = 0
    for iteration in range(N_PSEUDO_CONTROLS):
        source_index = iteration % 4
        pseudo = within_archive_pseudo(development, source_index, rng)
        result = evaluate_branch(development, holdout, "AA", basis_source=pseudo)
        row = control_row(
            "within_archive_pseudo_diagonal",
            iteration,
            result,
            source_child=CHILDREN[source_index],
        )
        pseudo_passes += int(row["passes_gates_1_to_6"])
        controls.append(row)

    primary = branches["AA"]
    binary_q99 = float(np.quantile(label_binary, 0.99))
    merge_q01 = float(np.quantile(label_merge, 0.01))
    gate_7 = (
        primary["holdout_survivor_binary_balanced_accuracy"] > binary_q99
        and primary["holdout_merge_ratio"] < merge_q01
    )
    label_rate = label_passes / N_LABEL_CONTROLS
    pseudo_rate = pseudo_passes / N_PSEUDO_CONTROLS
    gate_8 = label_rate <= 0.01 and pseudo_rate <= 0.05
    all_primary_gates = {
        **primary["gates_1_to_6"],
        "G7_exceeds_balanced_label_control_extremes": gate_7,
        "G8_control_pass_rates": gate_8,
    }
    primary_verdict = "SUPPORTED" if all(all_primary_gates.values()) else "NOT SUPPORTED"
    reversibility = all(branches[branch]["passes_gates_1_to_6"] for branch in BRANCHES)

    pd.DataFrame(metric_rows).to_csv(METRICS, index=False)
    pd.DataFrame(projection_output).to_csv(PROJECTIONS, index=False)
    pd.DataFrame(controls).to_csv(CONTROLS, index=False)

    output = {
        "claim_id": "Q19-T3-DOUBLE-DIAGONAL-v1",
        "seed": SEED,
        "hashes": hashes,
        "cuts": cuts,
        "row_count": len(frame),
        "primary_branch": "AA",
        "branches": {branch: json_clean(result) for branch, result in branches.items()},
        "control_thresholds": {
            "balanced_label_binary_accuracy_99th": binary_q99,
            "balanced_label_merge_ratio_1st": merge_q01,
        },
        "controls": {
            "balanced_development_label_iterations": N_LABEL_CONTROLS,
            "balanced_development_label_passes_gates_1_to_6": label_passes,
            "balanced_development_label_pass_rate": label_rate,
            "within_archive_pseudo_diagonal_iterations": N_PSEUDO_CONTROLS,
            "within_archive_pseudo_diagonal_passes_gates_1_to_6": pseudo_passes,
            "within_archive_pseudo_diagonal_pass_rate": pseudo_rate,
        },
        "primary_all_gates": all_primary_gates,
        "primary_verdict": primary_verdict,
        "secondary_four_corner_reversibility_supported": reversibility,
        "evidence_class": (
            "exploratory same-deposit measurement-space ablation; "
            "development collapse is constructive; independent replication required"
        ),
    }
    RESULTS.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "primary_verdict": primary_verdict,
                "primary_all_gates": all_primary_gates,
                "primary": json_clean(primary),
                "four_corner_reversibility_supported": reversibility,
                "branch_passes": {
                    branch: result["passes_gates_1_to_6"]
                    for branch, result in branches.items()
                },
                "control_rates": {
                    "balanced_labels": label_rate,
                    "pseudo_diagonals": pseudo_rate,
                },
            },
            indent=2,
        )
    )

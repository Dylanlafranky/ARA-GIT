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
PRIMARY_CODE = ROOT / "q19_tier3_double_diagonal_ablation_test.py"
RESULTS = ROOT / "Q19_TIER3_DOUBLE_DIAGONAL_ABLATION_RESULTS.json"
METRICS = ROOT / "Q19_TIER3_DOUBLE_DIAGONAL_ABLATION_METRICS.csv"
PROJECTIONS = ROOT / "Q19_TIER3_DOUBLE_DIAGONAL_ABLATION_PROJECTIONS.csv"
CONTROLS = ROOT / "Q19_TIER3_DOUBLE_DIAGONAL_ABLATION_CONTROLS.csv"
VALIDATION = ROOT / "Q19_TIER3_DOUBLE_DIAGONAL_ABLATION_VALIDATION.json"

EXPECTED_HASHES = {
    SOURCE.name: "0f7e58b349e5bf3cdda0110a99627134c7a76c69bb0443be8ba1576c4f01e48b",
    Q16_RESULTS.name: "30c5b458505ffdb54c9ee1b115ca1518cf6aa8cd185a474da0df5a28bd1ad3a4",
    Q18_RESULTS.name: "02f18498612b67f28df46695ef054285547a0f5f43c41eb96ad6d2b8fdf59b1d",
    TIER_MAP.name: "92f488264def3ef2c13c9d3bf79a0d06db6f74ae90ac25fe50bb6299cd91b113",
    PROTOCOL.name: "7c413ff705982d1f0a42d3786e42825a24a51d6eabd744e98c0d0d5d2e7af84b",
}

CHILDREN = ("C00", "C01", "C10", "C11")
J_CODE = np.array([1.0, -1.0, -1.0, 1.0])
BRANCHES = {
    "AA": {"pairs": ((0, 1), (0, 2)), "triple": (0, 1, 2), "survivor": 3},
    "AB": {"pairs": ((0, 1), (1, 3)), "triple": (0, 1, 3), "survivor": 2},
    "BA": {"pairs": ((2, 3), (0, 2)), "triple": (0, 2, 3), "survivor": 1},
    "BB": {"pairs": ((2, 3), (1, 3)), "triple": (1, 2, 3), "survivor": 0},
}


def file_hash(path: Path) -> str:
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
        part = frame[frame["split"] == split]
        record_ids = sorted(part["record_index"].unique())
        arrays[split] = np.stack(
            [
                part[part["child"] == child]
                .pivot(index="record_index", columns="cut", values="ara_x")
                .reindex(index=record_ids, columns=cuts)
                .to_numpy()
                for child in CHILDREN
            ]
        )
    return arrays, cuts, frame


def cosine(left: np.ndarray, right: np.ndarray) -> float:
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    return 0.0 if denominator == 0 else float(np.dot(left, right) / denominator)


def projector_from_differences(centroids: np.ndarray, branch: str) -> tuple[np.ndarray, dict]:
    differences = np.stack(
        [centroids[i] - centroids[j] for i, j in BRANCHES[branch]["pairs"]]
    )
    gram = differences @ differences.T
    projector = differences.T @ np.linalg.pinv(gram) @ differences
    singular_values = np.linalg.svd(differences, compute_uv=False)
    rank = int(np.linalg.matrix_rank(differences, tol=singular_values[0] * 1e-10))
    angle = float(
        np.degrees(
            np.arccos(np.clip(abs(cosine(differences[0], differences[1])), 0, 1))
        )
    )
    return projector, {
        "rank": rank,
        "angle": angle,
        "diagonal_singular_values": singular_values,
    }


def remove(data: np.ndarray, centre: np.ndarray, projector: np.ndarray) -> np.ndarray:
    centered = data - centre[None, None, :]
    return centered - np.einsum("irc,cd->ird", centered, projector)


def j_vector(centroids: np.ndarray) -> np.ndarray:
    return np.sum(J_CODE[:, None] * centroids, axis=0) / 2


def energy(centroids: np.ndarray) -> float:
    return float(np.sum((centroids - centroids.mean(axis=0)) ** 2))


def four_accuracy(truth: np.ndarray, prediction: np.ndarray) -> float:
    return float(
        np.mean(
            [
                np.mean(prediction[truth == index] == index)
                for index in range(4)
            ]
        )
    )


def branch_metrics(development: np.ndarray, holdout: np.ndarray, branch: str) -> dict:
    dev_centroids_original = development.mean(axis=1)
    hold_centroids_original = holdout.mean(axis=1)
    centre = dev_centroids_original.mean(axis=0)
    projector, plane = projector_from_differences(dev_centroids_original, branch)
    dev = remove(development, centre, projector)
    hold = remove(holdout, centre, projector)
    dev_centroids = dev.mean(axis=1)
    hold_centroids = hold.mean(axis=1)

    triple = np.array(BRANCHES[branch]["triple"])
    survivor = int(BRANCHES[branch]["survivor"])
    dev_triple = dev_centroids[triple].mean(axis=0)
    hold_triple = hold_centroids[triple].mean(axis=0)
    within = float(
        np.sqrt(np.mean(np.sum((hold_centroids[triple] - hold_triple) ** 2, axis=1)))
    )
    separation = float(np.linalg.norm(hold_centroids[survivor] - hold_triple))

    flat = hold.reshape(-1, hold.shape[-1])
    truth = np.repeat(np.arange(4), holdout.shape[1])
    survivor_prediction = (
        np.linalg.norm(flat - dev_centroids[survivor], axis=1)
        < np.linalg.norm(flat - dev_triple, axis=1)
    )
    true_survivor = truth == survivor
    survivor_recall = float(np.mean(survivor_prediction[true_survivor]))
    triple_recall = float(np.mean(~survivor_prediction[~true_survivor]))

    four_prediction = np.linalg.norm(
        flat[:, None, :] - dev_centroids[None, :, :], axis=2
    ).argmin(axis=1)
    raw_prediction = np.linalg.norm(
        holdout.reshape(-1, holdout.shape[-1])[:, None, :]
        - dev_centroids_original[None, :, :],
        axis=2,
    ).argmin(axis=1)

    centered_hold = hold_centroids - hold_centroids.mean(axis=0)
    centroid_singular = np.linalg.svd(centered_hold, compute_uv=False)
    singular_energy = centroid_singular**2
    residual_j = np.linalg.norm(j_vector(hold_centroids))
    original_j = np.linalg.norm(j_vector(hold_centroids_original))

    return {
        "development_diagonal_rank": plane["rank"],
        "development_diagonal_angle_degrees": plane["angle"],
        "development_diagonal_singular_values": plane[
            "diagonal_singular_values"
        ],
        "holdout_merge_ratio": within / separation,
        "holdout_within_triple_rms": within,
        "holdout_survivor_distance": separation,
        "holdout_survivor_binary_balanced_accuracy": (
            survivor_recall + triple_recall
        )
        / 2,
        "holdout_survivor_recall": survivor_recall,
        "holdout_triple_recall": triple_recall,
        "holdout_rank_one_energy_share": float(
            singular_energy[0] / singular_energy.sum()
        ),
        "holdout_centroid_singular_values": centroid_singular,
        "tier1_j_holdout_retention": float(residual_j / original_j),
        "holdout_between_child_energy_retention": energy(hold_centroids)
        / energy(hold_centroids_original),
        "holdout_four_child_nearest_accuracy": four_accuracy(
            truth, four_prediction
        ),
        "original_holdout_four_child_nearest_accuracy": four_accuracy(
            truth, raw_prediction
        ),
    }


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


def close(left: float, right: float, tolerance: float = 1e-11) -> bool:
    return bool(abs(float(left) - float(right)) <= tolerance)


if __name__ == "__main__":
    saved = json.loads(RESULTS.read_text(encoding="utf-8"))
    arrays, cuts, frame = load_arrays()
    checks: dict[str, bool] = {
        "source_rows_14400": len(frame) == 14_400,
        "source_cuts_45": len(cuts) == 45,
        "source_no_duplicates": not frame.duplicated(
            ["child", "split", "record_index", "cut"]
        ).any(),
        "metric_rows_4": len(pd.read_csv(METRICS)) == 4,
        "projection_rows_1280": len(pd.read_csv(PROJECTIONS)) == 1_280,
    }
    for path in (SOURCE, Q16_RESULTS, Q18_RESULTS, TIER_MAP, PROTOCOL):
        actual = file_hash(path)
        checks[f"hash_{path.name}"] = (
            actual == EXPECTED_HASHES[path.name] == saved["hashes"][path.name]
        )

    computed = {}
    scalar_fields = (
        "development_diagonal_angle_degrees",
        "holdout_merge_ratio",
        "holdout_within_triple_rms",
        "holdout_survivor_distance",
        "holdout_survivor_binary_balanced_accuracy",
        "holdout_survivor_recall",
        "holdout_triple_recall",
        "holdout_rank_one_energy_share",
        "tier1_j_holdout_retention",
        "holdout_between_child_energy_retention",
        "original_holdout_four_child_nearest_accuracy",
    )
    for branch in BRANCHES:
        result = branch_metrics(arrays["development"], arrays["holdout"], branch)
        computed[branch] = result
        expected = saved["branches"][branch]
        checks[f"{branch}_rank"] = (
            result["development_diagonal_rank"]
            == expected["development_diagonal_rank"]
        )
        for field in scalar_fields:
            checks[f"{branch}_{field}"] = close(result[field], expected[field])
        # The selected development triple is algebraically coincident after
        # projection. Four-class nearest-centroid labels inside that triple are
        # therefore determined by floating-point tie order, not by geometry.
        checks[f"{branch}_four_child_tie_sensitive_collapse"] = (
            result["holdout_four_child_nearest_accuracy"] <= 0.55
            and expected["holdout_four_child_nearest_accuracy"] <= 0.55
        )
        checks[f"{branch}_diagonal_singular_values"] = bool(
            np.allclose(
                result["development_diagonal_singular_values"],
                expected["development_diagonal_singular_values"],
                rtol=0,
                atol=1e-11,
            )
        )
        checks[f"{branch}_centroid_singular_values"] = bool(
            np.allclose(
                result["holdout_centroid_singular_values"],
                expected["holdout_centroid_singular_values"],
                rtol=0,
                atol=1e-11,
            )
        )
        branch_gates = deterministic_gates(result)
        checks[f"{branch}_gates"] = branch_gates == expected["gates_1_to_6"]
        checks[f"{branch}_pass"] = expected["passes_gates_1_to_6"] == all(
            branch_gates.values()
        )

    controls = pd.read_csv(CONTROLS)
    label = controls[controls["control_type"] == "balanced_development_labels"]
    pseudo = controls[
        controls["control_type"] == "within_archive_pseudo_diagonal"
    ]
    label_q99 = float(np.quantile(label["survivor_binary_accuracy"], 0.99))
    label_q01 = float(np.quantile(label["merge_ratio"], 0.01))
    checks.update(
        {
            "label_control_rows_9999": len(label) == 9_999,
            "pseudo_control_rows_1000": len(pseudo) == 1_000,
            "label_control_passes": int(label["passes_gates_1_to_6"].sum())
            == saved["controls"][
                "balanced_development_label_passes_gates_1_to_6"
            ],
            "pseudo_control_passes": int(pseudo["passes_gates_1_to_6"].sum())
            == saved["controls"][
                "within_archive_pseudo_diagonal_passes_gates_1_to_6"
            ],
            "label_q99": close(
                label_q99,
                saved["control_thresholds"][
                    "balanced_label_binary_accuracy_99th"
                ],
            ),
            "label_q01": close(
                label_q01,
                saved["control_thresholds"]["balanced_label_merge_ratio_1st"],
            ),
        }
    )

    primary = computed["AA"]
    primary_gates = deterministic_gates(primary)
    gate_7 = (
        primary["holdout_survivor_binary_balanced_accuracy"] > label_q99
        and primary["holdout_merge_ratio"] < label_q01
    )
    label_rate = float(label["passes_gates_1_to_6"].mean())
    pseudo_rate = float(pseudo["passes_gates_1_to_6"].mean())
    gate_8 = label_rate <= 0.01 and pseudo_rate <= 0.05
    complete_gates = {
        **primary_gates,
        "G7_exceeds_balanced_label_control_extremes": gate_7,
        "G8_control_pass_rates": gate_8,
    }
    checks["primary_complete_gates"] = complete_gates == saved["primary_all_gates"]
    checks["primary_verdict"] = saved["primary_verdict"] == (
        "SUPPORTED" if all(complete_gates.values()) else "NOT SUPPORTED"
    )
    checks["secondary_verdict"] = saved[
        "secondary_four_corner_reversibility_supported"
    ] == all(
        saved["branches"][branch]["passes_gates_1_to_6"]
        for branch in BRANCHES
    )
    code_text = PRIMARY_CODE.read_text(encoding="utf-8").lower()
    checks["primary_code_quarantines_conventional_names"] = not any(
        token in code_text
        for token in (
            "ramsey",
            "hahn",
            "bell",
            "pauli",
            "psi-plus",
            "psi-minus",
            "phi-plus",
            "phi-minus",
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
        "validated_primary_gates": complete_gates,
        "validated_primary_verdict": saved["primary_verdict"],
        "validated_four_corner_reversibility": saved[
            "secondary_four_corner_reversibility_supported"
        ],
    }
    VALIDATION.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    if failures:
        raise SystemExit(1)

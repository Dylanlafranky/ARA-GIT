#!/usr/bin/env python3
"""Independently reproduce and validate Q13 from the frozen Q11 records."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_RECORDS.csv"
PROTOCOL = HERE / "Q13_RAMSEY_HAHN_LATENT_CHILD_PROTOCOL_v1_FROZEN.md"
PROTOCOL_HASH = HERE / "Q13_RAMSEY_HAHN_LATENT_CHILD_PROTOCOL_v1_FROZEN.sha256"
REPORTED = HERE / "Q13_RAMSEY_HAHN_LATENT_RESULTS.json"
OUTPUT = HERE / "Q13_RAMSEY_HAHN_LATENT_VALIDATION.json"

STATES = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")
CHILDREN = ("R_A", "R_B", "H_A", "H_B")
AXES = ("amplitude", "direction")
PERMUTATIONS = 999
SEED = 27013
TOLERANCE = 1e-12


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def off_diagonal_energy(matrix: np.ndarray) -> float:
    return float(
        matrix[0, 1] ** 2 + matrix[0, 2] ** 2 + matrix[1, 2] ** 2
    )


def signs_match(observed: np.ndarray, fitted: np.ndarray) -> float:
    pairs = ((0, 1), (0, 2), (1, 2))
    matches = []
    for row, column in pairs:
        left = float(observed[row, column])
        right = float(fitted[row, column])
        matches.append(
            abs(left) > 1e-15
            and abs(right) > 1e-15
            and np.sign(left) == np.sign(right)
        )
    return float(sum(matches) / len(matches))


def make_matrices() -> tuple[dict[str, np.ndarray], np.ndarray, int]:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    indexed = {
        (row["condition"], row["state"], int(row["wait_index"])): row
        for row in rows
    }
    constructed = []
    for state in STATES:
        for wait_index in range(11):
            ramsey = indexed[("Ramsey", state, wait_index)]
            hahn = indexed[("Hahn", state, wait_index)]
            constructed.append(
                {
                    "state": state,
                    "R_A_amplitude": float(ramsey["visible_x"]) - 1.0,
                    "R_A_direction": float(ramsey["visible_y"]) - 1.0,
                    "R_B_amplitude": float(ramsey["target_x"]) - 1.0,
                    "R_B_direction": float(ramsey["target_y"]) - 1.0,
                    "H_A_amplitude": float(hahn["visible_x"]) - 1.0,
                    "H_A_direction": float(hahn["visible_y"]) - 1.0,
                    "H_B_amplitude": float(hahn["target_x"]) - 1.0,
                    "H_B_direction": float(hahn["target_y"]) - 1.0,
                }
            )
    labels = np.asarray([row["state"] for row in constructed])
    matrices = {
        axis: np.asarray(
            [
                [row[f"{child}_{axis}"] for child in CHILDREN]
                for row in constructed
            ],
            dtype=float,
        )
        for axis in AXES
    }
    return matrices, labels, len(indexed)


def evaluate(
    matrix: np.ndarray,
    labels: np.ndarray,
    hidden_index: int,
    replacement_hidden: np.ndarray | None = None,
) -> list[dict[str, float | str | int]]:
    hidden = (
        matrix[:, hidden_index]
        if replacement_hidden is None
        else replacement_hidden
    )
    visible_indices = [index for index in range(4) if index != hidden_index]
    results = []
    for held_out in STATES:
        training = labels != held_out
        testing = labels == held_out
        training_design = np.stack(
            [np.ones(int(training.sum())), hidden[training]], axis=1
        )
        testing_design = np.stack(
            [np.ones(int(testing.sum())), hidden[testing]], axis=1
        )
        slopes = []
        errors = []
        for visible_index in visible_indices:
            coefficients = np.linalg.lstsq(
                training_design,
                matrix[training, visible_index],
                rcond=None,
            )[0]
            slopes.append(float(coefficients[1]))
            errors.append(
                matrix[testing, visible_index] - testing_design @ coefficients
            )
        visible = matrix[testing][:, visible_indices]
        residual = np.stack(errors, axis=1)
        covariance_before = np.cov(visible, rowvar=False, ddof=1)
        covariance_after = np.cov(residual, rowvar=False, ddof=1)
        energy_before = off_diagonal_energy(covariance_before)
        energy_after = off_diagonal_energy(covariance_after)
        reduction = (
            1.0 - energy_after / energy_before
            if energy_before > 1e-18
            else float("nan")
        )
        removed = covariance_before - covariance_after
        singular_values = np.linalg.svd(removed, compute_uv=False)
        singular_energy = singular_values**2
        rank_one_share = (
            float(singular_energy[0] / singular_energy.sum())
            if singular_energy.sum() > 0
            else 0.0
        )
        slopes_array = np.asarray(slopes)
        induced = (
            np.outer(slopes_array, slopes_array)
            * np.var(hidden[testing], ddof=1)
        )
        results.append(
            {
                "heldout_state": held_out,
                "train_rows": int(training.sum()),
                "test_rows": int(testing.sum()),
                "reduction": float(reduction),
                "rank_one_share": rank_one_share,
                "sign_agreement": signs_match(removed, induced),
            }
        )
    return results


def summarize(folds: list[dict[str, float | str | int]]) -> dict[str, float]:
    return {
        "median_reduction": float(
            np.median([float(fold["reduction"]) for fold in folds])
        ),
        "mean_reduction": float(
            np.mean([float(fold["reduction"]) for fold in folds])
        ),
        "median_rank_one_share": float(
            np.median([float(fold["rank_one_share"]) for fold in folds])
        ),
        "median_sign_agreement": float(
            np.median([float(fold["sign_agreement"]) for fold in folds])
        ),
    }


def choose(summaries: dict[str, dict[str, dict[str, float]]]) -> str:
    scores = {
        child: (
            summaries[child]["amplitude"]["median_reduction"]
            + summaries[child]["direction"]["median_reduction"]
        )
        / 2.0
        for child in CHILDREN
    }
    return sorted(CHILDREN, key=lambda child: (-scores[child], child))[0]


def close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=0.0, abs_tol=TOLERANCE)


def main() -> None:
    expected_hash = PROTOCOL_HASH.read_text(encoding="utf-8").split()[0]
    observed_hash = sha256(PROTOCOL)
    reported = json.loads(REPORTED.read_text(encoding="utf-8"))
    matrices, labels, source_cells = make_matrices()

    summaries: dict[str, dict[str, dict[str, float]]] = {
        child: {} for child in CHILDREN
    }
    folds_by_child: dict[str, dict[str, list[dict[str, float | str | int]]]] = {
        child: {} for child in CHILDREN
    }
    for hidden_index, child in enumerate(CHILDREN):
        for axis in AXES:
            folds = evaluate(matrices[axis], labels, hidden_index)
            folds_by_child[child][axis] = folds
            summaries[child][axis] = summarize(folds)
    selected = choose(summaries)

    fold_winners = {}
    for held_out in STATES:
        scores = {}
        for child in CHILDREN:
            amp = next(
                float(row["reduction"])
                for row in folds_by_child[child]["amplitude"]
                if row["heldout_state"] == held_out
            )
            direction = next(
                float(row["reduction"])
                for row in folds_by_child[child]["direction"]
                if row["heldout_state"] == held_out
            )
            scores[child] = (amp + direction) / 2.0
        fold_winners[held_out] = sorted(
            CHILDREN, key=lambda child: (-scores[child], child)
        )[0]

    selected_amp = summaries[selected]["amplitude"]["median_reduction"]
    selected_direction = summaries[selected]["direction"]["median_reduction"]
    selected_composite = (selected_amp + selected_direction) / 2.0

    rng = np.random.default_rng(SEED)
    state_rows = {
        state: np.flatnonzero(labels == state) for state in STATES
    }
    null_amplitude = []
    null_direction = []
    null_composite = []
    for _ in range(PERMUTATIONS):
        shuffled_scores = {}
        for hidden_index, child in enumerate(CHILDREN):
            remaps = {
                state: rng.permutation(indices)
                for state, indices in state_rows.items()
            }
            shuffled_scores[child] = {}
            for axis in AXES:
                original_hidden = matrices[axis][:, hidden_index]
                shuffled_hidden = original_hidden.copy()
                for state, indices in state_rows.items():
                    shuffled_hidden[indices] = original_hidden[remaps[state]]
                shuffled_scores[child][axis] = summarize(
                    evaluate(
                        matrices[axis],
                        labels,
                        hidden_index,
                        replacement_hidden=shuffled_hidden,
                    )
                )["median_reduction"]
        null_amplitude.append(
            max(shuffled_scores[child]["amplitude"] for child in CHILDREN)
        )
        null_direction.append(
            max(shuffled_scores[child]["direction"] for child in CHILDREN)
        )
        null_composite.append(
            max(
                (
                    shuffled_scores[child]["amplitude"]
                    + shuffled_scores[child]["direction"]
                )
                / 2.0
                for child in CHILDREN
            )
        )

    def permutation_p(observed: float, values: list[float]) -> float:
        return (1 + sum(value >= observed for value in values)) / (
            len(values) + 1
        )

    computed_null = {
        "p_amplitude": permutation_p(selected_amp, null_amplitude),
        "p_direction": permutation_p(selected_direction, null_direction),
        "p_composite": permutation_p(selected_composite, null_composite),
        "null_amplitude_q99": float(np.quantile(null_amplitude, 0.99)),
        "null_direction_q95": float(np.quantile(null_direction, 0.95)),
        "null_composite_q95": float(np.quantile(null_composite, 0.95)),
    }
    reported_summary = reported["summary"]
    reported_null = reported_summary["null"]
    checks = {
        "protocol_hash": expected_hash == observed_hash == reported["protocol_sha256"],
        "source_cells": source_cells == 88 and len(labels) == 44,
        "finite_matrices": all(np.isfinite(matrix).all() for matrix in matrices.values()),
        "selected_candidate": selected == reported_summary["selected_candidate"],
        "fold_winners": fold_winners == reported_summary["fold_winners"],
        "candidate_summaries": all(
            close(
                summaries[child][axis][metric],
                float(reported_summary["candidate_summaries"][child][axis][metric]),
            )
            for child in CHILDREN
            for axis in AXES
            for metric in (
                "median_reduction",
                "mean_reduction",
                "median_rank_one_share",
                "median_sign_agreement",
            )
        ),
        "permutation_null": all(
            close(computed_null[key], float(reported_null[key]))
            for key in computed_null
        ),
    }
    result = {
        "validation_id": "Q13-RAMSEY-HAHN-LATENT-CHILD-independent-v1",
        "independent_of_main_module": True,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "recomputed": {
            "selected_candidate": selected,
            "candidate_summaries": summaries,
            "fold_winners": fold_winners,
            "null": computed_null,
        },
        "boundary": (
            "This validates implementation and deterministic reproduction only. "
            "It does not turn ordinal matching into a causal temporal handoff."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

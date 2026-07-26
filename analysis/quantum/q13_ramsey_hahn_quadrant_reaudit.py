"""Post-result Ramsey/Hahn two-parent, four-child quadrant audit.

This diagnostic does not change Q13 or Q14's frozen protocols or gates.
It checks:

1. internal A/B opposition inside each proposed Ramsey/Hahn parent;
2. dimensionality of the four ARA coordinate-child trajectories;
3. output-plane angles at the four approximately common physical waits;
4. whether the apparent angular sweep depends on the correct Ramsey/Hahn
   common-wait matching, using a within-state Hahn-wait rematching control.

Run with the bundled workspace Python because this script uses NumPy.
"""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
Q13 = HERE / "Q13_RAMSEY_HAHN_FOUR_CHILDREN.csv"
Q8 = HERE / "Q8_BELL_RELATION_PLANE_RECORDS.csv"
Q11 = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_RECORDS.csv"
STATE_ORDER = ("Phi-minus", "Phi-plus", "Psi-minus", "Psi-plus")
CHILD_ORDER = ("R_A", "R_B", "H_A", "H_B")
COMMON_WAIT_RELATIVE_TOLERANCE = 0.02
MONTE_CARLO_DRAWS = 200_000
SEED = 20_260_724


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def complex_child(row: dict[str, str], name: str) -> complex:
    return complex(float(row[f"{name}_amplitude"]), float(row[f"{name}_direction"]))


def cosine(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    denominator = np.abs(a) * np.abs(b)
    result = np.full(len(a), np.nan)
    valid = denominator > 1e-12
    result[valid] = np.real(a[valid] * np.conj(b[valid])) / denominator[valid]
    return result


def oriented_angle_degrees(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.degrees(np.arccos(np.clip(cosine(a, b), -1.0, 1.0)))


def pca_energy_shares(matrix: np.ndarray) -> list[float]:
    centered = matrix - matrix.mean(axis=0)
    singular_values = np.linalg.svd(centered, compute_uv=False)
    shares = singular_values**2 / np.sum(singular_values**2)
    return [float(value) for value in shares]


def average_ranks(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values)
    order = np.argsort(values, kind="stable")
    ranks = np.empty(len(values), dtype=float)
    left = 0
    while left < len(values):
        right = left + 1
        while right < len(values) and values[order[right]] == values[order[left]]:
            right += 1
        ranks[order[left:right]] = (left + right - 1) / 2
        left = right
    return ranks


def spearman(values: np.ndarray) -> float:
    time_rank = np.arange(len(values), dtype=float)
    value_rank = average_ranks(values)
    return float(np.corrcoef(time_rank, value_rank)[0, 1])


def nearest_common_waits(
    q13_rows: list[dict[str, str]],
) -> tuple[list[np.ndarray], list[np.ndarray], list[dict[str, float | str]]]:
    ramsey: dict[str, list[tuple[float, complex]]] = {state: [] for state in STATE_ORDER}
    hahn: dict[str, list[tuple[float, complex]]] = {state: [] for state in STATE_ORDER}

    for row in q13_rows:
        state = row["state"]
        ramsey_axis = (complex_child(row, "R_A") - complex_child(row, "R_B")) / 2
        hahn_axis = (complex_child(row, "H_A") - complex_child(row, "H_B")) / 2
        ramsey[state].append((float(row["ramsey_wait_us"]), ramsey_axis))
        hahn[state].append((float(row["hahn_wait_us"]), hahn_axis))

    ramsey_axes: list[np.ndarray] = []
    hahn_axes: list[np.ndarray] = []
    matches: list[dict[str, float | str]] = []
    for state in STATE_ORDER:
        state_ramsey: list[complex] = []
        state_hahn: list[complex] = []
        for ramsey_wait, ramsey_axis in ramsey[state]:
            hahn_wait, hahn_axis = min(
                hahn[state], key=lambda item: abs(item[0] - ramsey_wait)
            )
            relative_gap = abs(hahn_wait - ramsey_wait) / (
                (hahn_wait + ramsey_wait) / 2
            )
            if relative_gap <= COMMON_WAIT_RELATIVE_TOLERANCE:
                state_ramsey.append(ramsey_axis)
                state_hahn.append(hahn_axis)
                matches.append(
                    {
                        "state": state,
                        "ramsey_wait_us": ramsey_wait,
                        "hahn_wait_us": hahn_wait,
                        "relative_wait_gap": relative_gap,
                    }
                )
        ramsey_axes.append(np.asarray(state_ramsey, dtype=complex))
        hahn_axes.append(np.asarray(state_hahn, dtype=complex))

    return ramsey_axes, hahn_axes, matches


def raw_relation_common_wait_angles(
    q8_rows: list[dict[str, str]],
) -> np.ndarray:
    by_condition: dict[str, dict[str, list[tuple[float, complex]]]] = {
        "Ramsey": {state: [] for state in STATE_ORDER},
        "Hahn": {state: [] for state in STATE_ORDER},
    }
    for row in q8_rows:
        by_condition[row["condition"]][row["state"]].append(
            (
                float(row["wait_us"]),
                complex(float(row["u"]), float(row["v"])),
            )
        )

    angles: list[float] = []
    for state in STATE_ORDER:
        for ramsey_wait, ramsey_value in by_condition["Ramsey"][state]:
            hahn_wait, hahn_value = min(
                by_condition["Hahn"][state],
                key=lambda item: abs(item[0] - ramsey_wait),
            )
            relative_gap = abs(hahn_wait - ramsey_wait) / (
                (hahn_wait + ramsey_wait) / 2
            )
            if relative_gap <= COMMON_WAIT_RELATIVE_TOLERANCE:
                angles.append(
                    float(
                        oriented_angle_degrees(
                            np.asarray([ramsey_value]),
                            np.asarray([hahn_value]),
                        )[0]
                    )
                )
    return np.asarray(angles)


def common_wait_handover_probe(
    q11_rows: list[dict[str, str]],
) -> dict[str, float | int | list[dict[str, float | str]]]:
    by_condition: dict[str, dict[str, list[dict[str, str]]]] = {
        "Ramsey": {state: [] for state in STATE_ORDER},
        "Hahn": {state: [] for state in STATE_ORDER},
    }
    for row in q11_rows:
        by_condition[row["condition"]][row["state"]].append(row)

    records: list[dict[str, float | str]] = []
    for state in STATE_ORDER:
        for ramsey in by_condition["Ramsey"][state]:
            ramsey_wait = float(ramsey["wait_us"])
            hahn = min(
                by_condition["Hahn"][state],
                key=lambda row: abs(float(row["wait_us"]) - ramsey_wait),
            )
            hahn_wait = float(hahn["wait_us"])
            relative_gap = abs(hahn_wait - ramsey_wait) / (
                (hahn_wait + ramsey_wait) / 2
            )
            if relative_gap <= COMMON_WAIT_RELATIVE_TOLERANCE:
                p_ramsey = float(ramsey["target_purity_loss"])
                p_hahn = float(hahn["target_purity_loss"])
                delta_p = p_ramsey - p_hahn
                delta_v = (
                    float(hahn["visible_value"])
                    - float(ramsey["visible_value"])
                )
                records.append(
                    {
                        "state": state,
                        "ramsey_wait_us": ramsey_wait,
                        "hahn_wait_us": hahn_wait,
                        "delta_p": delta_p,
                        "delta_v": delta_v,
                        "apparent_refocusable_share": (
                            delta_p / p_ramsey
                            if p_ramsey > 1e-12
                            else float("nan")
                        ),
                    }
                )

    delta_p = np.asarray([row["delta_p"] for row in records], dtype=float)
    delta_v = np.asarray([row["delta_v"] for row in records], dtype=float)
    positive_shares = np.asarray(
        [
            row["apparent_refocusable_share"]
            for row in records
            if row["delta_p"] > 0
        ],
        dtype=float,
    )
    return {
        "count": len(records),
        "positive_delta_p_count": int(np.count_nonzero(delta_p > 0)),
        "positive_delta_v_count": int(np.count_nonzero(delta_v > 0)),
        "median_positive_apparent_refocusable_share": float(
            np.median(positive_shares)
        ),
        "delta_p_delta_v_correlation": float(
            np.corrcoef(delta_p, delta_v)[0, 1]
        ),
        "through_origin_slope_delta_v_on_delta_p": float(
            np.dot(delta_p, delta_v) / np.dot(delta_p, delta_p)
        ),
        "mae_against_unit_handover": float(np.mean(np.abs(delta_v - delta_p))),
        "records": records,
    }


def permutation_control(
    ramsey_axes: list[np.ndarray],
    hahn_axes: list[np.ndarray],
) -> dict[str, float | int | list[float]]:
    permutations = np.asarray(list(itertools.permutations(range(4))), dtype=int)
    angle_matrices = [
        np.degrees(
            np.arccos(
                np.clip(
                    np.real(r[:, None] * np.conj(h[None, :]))
                    / (np.abs(r[:, None]) * np.abs(h[None, :])),
                    -1.0,
                    1.0,
                )
            )
        )
        for r, h in zip(ramsey_axes, hahn_axes)
    ]

    permuted_angles: list[np.ndarray] = []
    rank_scores: list[np.ndarray] = []
    for matrix in angle_matrices:
        paths = np.stack(
            [matrix[np.arange(4), permutation] for permutation in permutations]
        )
        permuted_angles.append(paths)
        rank_scores.append(np.asarray([spearman(path) for path in paths]))

    observed_state_scores = np.asarray([scores[0] for scores in rank_scores])
    observed_mean_score = float(np.mean(observed_state_scores))
    score_sums = (
        rank_scores[0][:, None, None, None]
        + rank_scores[1][None, :, None, None]
        + rank_scores[2][None, None, :, None]
        + rank_scores[3][None, None, None, :]
    )
    exact_p = float(
        np.mean(score_sums >= (4 * observed_mean_score - 1e-12))
    )

    observed_angles = np.stack([paths[0] for paths in permuted_angles])
    observed_medians = np.median(observed_angles, axis=0)
    observed_rotation = float(observed_medians[-1] - observed_medians[0])

    rng = np.random.default_rng(SEED)
    random_indices = rng.integers(
        0, len(permutations), size=(MONTE_CARLO_DRAWS, 4)
    )
    sampled = np.stack(
        [
            permuted_angles[index][random_indices[:, index]]
            for index in range(4)
        ],
        axis=1,
    )
    sampled_medians = np.median(sampled, axis=1)
    monotonic = np.all(np.diff(sampled_medians, axis=1) > 0, axis=1)
    rotation = sampled_medians[:, -1] - sampled_medians[:, 0]
    monotonic_p = float(
        (np.count_nonzero(monotonic) + 1) / (MONTE_CARLO_DRAWS + 1)
    )
    joint_p = float(
        (
            np.count_nonzero(
                monotonic & (rotation >= observed_rotation - 1e-12)
            )
            + 1
        )
        / (MONTE_CARLO_DRAWS + 1)
    )

    return {
        "observed_state_spearman": [
            float(value) for value in observed_state_scores
        ],
        "observed_mean_state_spearman": observed_mean_score,
        "exact_permutation_p_mean_state_spearman": exact_p,
        "observed_median_angles_by_wait": [
            float(value) for value in observed_medians
        ],
        "observed_median_rotation_degrees": observed_rotation,
        "monte_carlo_draws": MONTE_CARLO_DRAWS,
        "monte_carlo_p_monotonic_medians": monotonic_p,
        "monte_carlo_p_monotonic_and_rotation": joint_p,
    }


def main() -> None:
    q13_rows = read_csv(Q13)
    q8_rows = read_csv(Q8)
    q11_rows = read_csv(Q11)
    hadamard = np.asarray([[1.0, 1.0], [1.0, -1.0]]) / np.sqrt(2.0)
    children = {
        name: np.asarray(
            [complex_child(row, name) for row in q13_rows],
            dtype=complex,
        )
        for name in CHILD_ORDER
    }

    opposition: dict[str, dict[str, float]] = {}
    for prefix in ("R", "H"):
        phase_a = children[f"{prefix}_A"]
        phase_b = children[f"{prefix}_B"]
        closure_error = np.abs(phase_a + phase_b) / (
            np.abs(phase_a) + np.abs(phase_b) + 1e-12
        )
        opposition_cosine = cosine(phase_a, -phase_b)
        opposition[prefix] = {
            "median_normalized_closure_error": float(np.median(closure_error)),
            "median_opposition_cosine": float(
                np.nanmedian(opposition_cosine)
            ),
        }

    amplitude_matrix = np.column_stack(
        [
            [float(row[f"{name}_amplitude"]) for row in q13_rows]
            for name in CHILD_ORDER
        ]
    )
    direction_matrix = np.column_stack(
        [
            [float(row[f"{name}_direction"]) for row in q13_rows]
            for name in CHILD_ORDER
        ]
    )

    ramsey_axes, hahn_axes, matches = nearest_common_waits(q13_rows)
    derived_angles = np.concatenate(
        [
            oriented_angle_degrees(ramsey_axis, hahn_axis)
            for ramsey_axis, hahn_axis in zip(ramsey_axes, hahn_axes)
        ]
    )
    raw_angles = raw_relation_common_wait_angles(q8_rows)

    result = {
        "status": "post-result construct and geometry audit; frozen gates unchanged",
        "four_ara_coordinate_children": list(CHILD_ORDER),
        "independent_physical_subsystems": False,
        "ideal_control_quadrant": {
            "normalized_hadamard_gram": (
                hadamard @ hadamard.T
            ).tolist(),
            "ramsey_hahn_sensitivity_inner_product_over_T": 0.0,
            "oriented_branches": [
                "+Phi_R",
                "-Phi_R",
                "+Phi_H",
                "-Phi_H",
            ],
        },
        "internal_parent_opposition": opposition,
        "pca_energy_shares": {
            "amplitude": pca_energy_shares(amplitude_matrix),
            "direction": pca_energy_shares(direction_matrix),
        },
        "common_wait_matches": {
            "relative_tolerance": COMMON_WAIT_RELATIVE_TOLERANCE,
            "count": len(matches),
            "rows": matches,
        },
        "derived_parent_axis_output_angles": {
            "mean_degrees": float(np.mean(derived_angles)),
            "median_degrees": float(np.median(derived_angles)),
            "fraction_within_15_degrees_of_90": float(
                np.mean(np.abs(derived_angles - 90) <= 15)
            ),
        },
        "raw_uv_output_angles": {
            "mean_degrees": float(np.mean(raw_angles)),
            "median_degrees": float(np.median(raw_angles)),
            "fraction_within_15_degrees_of_90": float(
                np.mean(np.abs(raw_angles - 90) <= 15)
            ),
        },
        "unfrozen_common_wait_handover_probe": common_wait_handover_probe(
            q11_rows
        ),
        "hahn_wait_rematching_control": permutation_control(
            ramsey_axes, hahn_axes
        ),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

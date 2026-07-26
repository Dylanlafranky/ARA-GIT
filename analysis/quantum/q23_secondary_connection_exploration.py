#!/usr/bin/env python3
"""Post-result Q23 decomposition check; cannot rescue the frozen primary."""

from __future__ import annotations

import json
import pathlib

import numpy as np

from q23_connection_bit_features import (
    BASES,
    OUTCOME_ROOT,
    ROUNDS,
    bit_identities,
    connection_identities,
    load_geometry,
    rank_diameter,
    unpack_labels,
)


ROOT = pathlib.Path(__file__).parent
OUTPUT = ROOT / "Q23_WILLOW_CONNECTION_BIT_SECONDARY_EXPLORATION.json"
SEED = 20260726
PERMUTATIONS = 9999
IDENTITIES = (
    "web_stability",
    "same_child_persistence",
    "anti_child_handover",
    "web_concentration",
)


def correlation(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.corrcoef(left, right)[0, 1])


def main() -> None:
    coordinates: dict[tuple[str, str], dict[str, np.ndarray]] = {}
    bit_coordinates: dict[tuple[str, str], np.ndarray] = {}
    for basis in BASES:
        for rounds in ROUNDS:
            detectors, detector_coordinates, weights, metadata = load_geometry(
                basis, rounds
            )
            connection, _, _ = connection_identities(
                detectors, detector_coordinates, weights
            )
            labels = unpack_labels(
                OUTCOME_ROOT / basis / rounds / "obs_flips_actual.b8",
                int(metadata["shots"]),
            )
            coordinates[(basis, rounds)] = {
                name: rank_diameter(connection[name]) for name in IDENTITIES
            }
            bit_coordinates[(basis, rounds)] = rank_diameter(
                bit_identities(labels)["retention"]
            )

    rng = np.random.default_rng(SEED)
    results = {}
    for identity in IDENTITIES:
        observed = {
            f"{basis}_{rounds}": correlation(
                coordinates[(basis, rounds)][identity],
                bit_coordinates[(basis, rounds)],
            )
            for basis in BASES
            for rounds in ROUNDS
        }
        null_mean = np.empty(PERMUTATIONS)
        for permutation in range(PERMUTATIONS):
            values = []
            for basis in BASES:
                for rounds in ROUNDS:
                    values.append(
                        correlation(
                            coordinates[(basis, rounds)][identity],
                            rng.permutation(bit_coordinates[(basis, rounds)]),
                        )
                    )
            null_mean[permutation] = np.mean(values)
        observed_mean = float(np.mean(list(observed.values())))
        results[identity] = {
            "dataset_rank_correlations": observed,
            "all_four_positive": all(value > 0 for value in observed.values()),
            "mean_rank_correlation": observed_mean,
            "permutation_count": PERMUTATIONS,
            "permutation_seed": SEED,
            "null_mean_of_mean_correlation": float(null_mean.mean()),
            "null_sd_of_mean_correlation": float(null_mean.std()),
            "one_sided_p_for_mean_positive_correlation": float(
                (1 + np.sum(null_mean >= observed_mean))
                / (PERMUTATIONS + 1)
            ),
        }

    OUTPUT.write_text(
        json.dumps(
            {
                "title": "Q23 post-result connection decomposition",
                "status": "EXPLORATORY_ONLY",
                "cannot_rescue_primary": True,
                "note": (
                    "Identity-level permutation gates and pooled combination "
                    "were not frozen before outcomes. These values can only "
                    "choose a future preregistered lineage."
                ),
                "results": results,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()

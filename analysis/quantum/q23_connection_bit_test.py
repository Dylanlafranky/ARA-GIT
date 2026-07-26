#!/usr/bin/env python3
"""Run the checksum-frozen Q23 connection-web/logical-bit closure test."""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib

import numpy as np

from q23_connection_bit_features import (
    BASES,
    BLOCK_SIZE,
    GEOMETRY_ROOT,
    OUTCOME_ROOT,
    ROUNDS,
    bit_identities,
    connection_identities,
    load_geometry,
    paired_closure,
    parent_ara,
    rank_diameter,
    unpack_labels,
)


ROOT = pathlib.Path(__file__).parent
PROTOCOL = ROOT / "Q23_WILLOW_CONNECTION_BIT_PROTOCOL_v1_FROZEN.md"
CALIBRATION = ROOT / "Q23_WILLOW_CONNECTION_BIT_CALIBRATION.json"
FREEZE = ROOT / "Q23_WILLOW_CONNECTION_BIT_FREEZE_MANIFEST.json"
OUTCOME_MANIFEST = (
    ROOT / "public_data" / "q23_willow_d7_outcomes" / "SOURCE_MANIFEST.json"
)
RESULTS = ROOT / "Q23_WILLOW_CONNECTION_BIT_RESULTS.json"
METRICS = ROOT / "Q23_WILLOW_CONNECTION_BIT_METRICS.csv"
PROJECTIONS = ROOT / "Q23_WILLOW_CONNECTION_BIT_PROJECTIONS.csv"
PERMUTATIONS = 999
SEED = 20260726


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_freeze() -> dict:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if not freeze["outcome_files_absent_at_freeze"]:
        raise RuntimeError("Freeze does not assert sealed outcomes.")
    for name, expected in freeze["frozen_files_sha256"].items():
        actual = sha256(ROOT / name)
        if actual != expected:
            raise RuntimeError(f"Frozen hash mismatch for {name}")
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    if not calibration["outcome_blind"]:
        raise RuntimeError("Calibration is not outcome-blind.")
    if list(GEOMETRY_ROOT.rglob("obs_flips_actual.b8")):
        raise RuntimeError("Outcome file leaked into geometry root.")
    outcome_manifest = json.loads(
        OUTCOME_MANIFEST.read_text(encoding="utf-8")
    )
    names = [member["name"] for member in outcome_manifest["members"]]
    if len(names) != 4 or any(
        not name.endswith("/obs_flips_actual.b8") for name in names
    ):
        raise RuntimeError("Unexpected Q23 outcome manifest.")
    return freeze


def controls(
    connection_raw: np.ndarray,
    broken_raw: np.ndarray,
    bit_retention_raw: np.ndarray,
    wrong_bit_raw: np.ndarray,
) -> dict[str, dict]:
    observed = paired_closure(connection_raw, bit_retention_raw)
    shifted = paired_closure(
        connection_raw, np.roll(bit_retention_raw, len(bit_retention_raw) // 2)
    )
    wrong = paired_closure(connection_raw, wrong_bit_raw)
    broken = paired_closure(broken_raw, bit_retention_raw)
    flipped = paired_closure(connection_raw, 2.0 - bit_retention_raw)
    return {
        "paired": observed,
        "half_cycle_shift": shifted,
        "wrong_bit": wrong,
        "broken_spatial_web": broken,
        "flip_orientation": flipped,
    }


def serializable_closure(values: dict) -> dict:
    return {
        key: value
        for key, value in values.items()
        if not isinstance(value, np.ndarray)
    }


def main() -> None:
    freeze = verify_freeze()
    datasets: dict[tuple[str, str], dict] = {}
    for basis in BASES:
        for rounds in ROUNDS:
            detectors, coordinates, weights, metadata = load_geometry(
                basis, rounds
            )
            connection, broken, quality = connection_identities(
                detectors, coordinates, weights
            )
            labels = unpack_labels(
                OUTCOME_ROOT / basis / rounds / "obs_flips_actual.b8",
                int(metadata["shots"]),
            )
            bits = bit_identities(labels)
            datasets[(basis, rounds)] = {
                "connection": connection,
                "broken": broken,
                "bits": bits,
                "quality": quality,
                "metadata": metadata,
                "label_sha256": sha256(
                    OUTCOME_ROOT
                    / basis
                    / rounds
                    / "obs_flips_actual.b8"
                ),
                "flip_rate": float(labels.mean()),
            }

    rng = np.random.default_rng(SEED)
    results: dict[str, dict] = {}
    projection_rows: list[dict] = []
    metric_rows: list[dict] = []
    gates_by_dataset: dict[str, dict[str, bool]] = {}

    for basis in BASES:
        other_basis = "Z" if basis == "X" else "X"
        for rounds in ROUNDS:
            key = f"{basis}_{rounds}"
            data = datasets[(basis, rounds)]
            wrong = datasets[(other_basis, rounds)]["bits"]["retention"]
            primary_raw = data["connection"]["web_stability"]
            control_sets = controls(
                primary_raw,
                data["broken"]["web_stability"],
                data["bits"]["retention"],
                wrong,
            )
            observed = control_sets["paired"]

            null_distances = np.empty(PERMUTATIONS, dtype=np.float64)
            null_near = np.empty(PERMUTATIONS, dtype=np.float64)
            bit_coordinate = observed["bit"]
            connection_coordinate = observed["connection"]
            for index in range(PERMUTATIONS):
                permuted = rng.permutation(bit_coordinate)
                parent = parent_ara(connection_coordinate, permuted)
                distance = np.abs(parent - 1.0)
                null_distances[index] = distance.mean()
                null_near[index] = (distance <= 0.10).mean()

            permutation = {
                "count": PERMUTATIONS,
                "seed": SEED,
                "null_mean_ridge_distance": float(null_distances.mean()),
                "null_sd_ridge_distance": float(null_distances.std()),
                "null_mean_near_ridge_fraction_0_10": float(null_near.mean()),
                "observed_mean_ridge_distance": observed[
                    "mean_ridge_distance"
                ],
                "observed_near_ridge_fraction_0_10": observed[
                    "near_ridge_fraction_0_10"
                ],
                "one_sided_empirical_p": float(
                    (1 + np.sum(null_distances <= observed["mean_ridge_distance"]))
                    / (PERMUTATIONS + 1)
                ),
            }
            permutation["ridge_distance_gain"] = float(
                permutation["null_mean_ridge_distance"]
                - observed["mean_ridge_distance"]
            )
            permutation["near_ridge_fraction_gain"] = float(
                observed["near_ridge_fraction_0_10"]
                - permutation["null_mean_near_ridge_fraction_0_10"]
            )

            secondary = {}
            for name in (
                "same_child_persistence",
                "anti_child_handover",
                "web_concentration",
            ):
                secondary[name] = serializable_closure(
                    paired_closure(
                        data["connection"][name],
                        data["bits"]["retention"],
                    )
                )

            local_in_range = bool(
                np.all((observed["connection"] > 0) & (observed["connection"] < 2))
                and np.all((observed["bit"] > 0) & (observed["bit"] < 2))
                and np.all((observed["parent"] > 0) & (observed["parent"] < 2))
            )
            dataset_gates = {
                "coordinates_inside_open_0_2": local_in_range,
                "parent_median_in_0_95_1_05": bool(
                    0.95 <= observed["median_parent"] <= 1.05
                ),
                "closer_than_half_cycle_shift": bool(
                    observed["mean_ridge_distance"]
                    < control_sets["half_cycle_shift"]["mean_ridge_distance"]
                ),
                "closer_than_wrong_bit": bool(
                    observed["mean_ridge_distance"]
                    < control_sets["wrong_bit"]["mean_ridge_distance"]
                ),
                "closer_than_broken_spatial_web": bool(
                    observed["mean_ridge_distance"]
                    < control_sets["broken_spatial_web"]["mean_ridge_distance"]
                ),
                "permutation_p_at_most_0_01": bool(
                    permutation["one_sided_empirical_p"] <= 0.01
                ),
                "ridge_distance_gain_at_least_0_02": bool(
                    permutation["ridge_distance_gain"] >= 0.02
                ),
                "near_ridge_fraction_gain_at_least_0_05": bool(
                    permutation["near_ridge_fraction_gain"] >= 0.05
                ),
                "rank_correlation_at_least_0_15": bool(
                    observed["rank_correlation"] >= 0.15
                ),
            }
            gates_by_dataset[key] = dataset_gates
            results[key] = {
                "basis": basis,
                "rounds": rounds,
                "shots": int(data["metadata"]["shots"]),
                "blocks": len(primary_raw),
                "block_size": BLOCK_SIZE,
                "flip_rate": data["flip_rate"],
                "label_sha256": data["label_sha256"],
                "connection_quality": data["quality"],
                "primary": {
                    name: serializable_closure(value)
                    for name, value in control_sets.items()
                },
                "permutation": permutation,
                "secondary_connection_decompressions": secondary,
                "dataset_gates": dataset_gates,
            }

            for control_name, closure in control_sets.items():
                metric_rows.append(
                    {
                        "dataset": key,
                        "control": control_name,
                        **serializable_closure(closure),
                    }
                )
            for block in range(len(primary_raw)):
                projection_rows.append(
                    {
                        "dataset": key,
                        "basis": basis,
                        "rounds": rounds,
                        "block": block,
                        "connection_raw_web_stability": float(primary_raw[block]),
                        "bit_raw_retention": float(
                            data["bits"]["retention"][block]
                        ),
                        "connection_ara": float(observed["connection"][block]),
                        "bit_ara": float(observed["bit"][block]),
                        "parent_ara": float(observed["parent"][block]),
                        "parent_ridge_distance": float(
                            observed["ridge_distance"][block]
                        ),
                    }
                )

    integrity = bool(
        freeze["outcome_files_absent_at_freeze"]
        and all(
            d["quality"]["unused_shots"] == 0
            and d["quality"]["block_count"] == 200
            for d in datasets.values()
        )
    )
    aggregate_gates = {
        "source_and_freeze_integrity": integrity,
        "all_coordinates_inside_open_0_2": all(
            g["coordinates_inside_open_0_2"] for g in gates_by_dataset.values()
        ),
        "parent_median_near_1_all_four": all(
            g["parent_median_in_0_95_1_05"] for g in gates_by_dataset.values()
        ),
        "closer_than_half_cycle_shift_all_four": all(
            g["closer_than_half_cycle_shift"] for g in gates_by_dataset.values()
        ),
        "closer_than_wrong_bit_all_four": all(
            g["closer_than_wrong_bit"] for g in gates_by_dataset.values()
        ),
        "closer_than_broken_spatial_web_all_four": all(
            g["closer_than_broken_spatial_web"]
            for g in gates_by_dataset.values()
        ),
        "permutation_p_at_most_0_01_all_four": all(
            g["permutation_p_at_most_0_01"] for g in gates_by_dataset.values()
        ),
        "ridge_distance_gain_at_least_0_02_all_four": all(
            g["ridge_distance_gain_at_least_0_02"]
            for g in gates_by_dataset.values()
        ),
        "near_ridge_fraction_gain_at_least_0_05_all_four": all(
            g["near_ridge_fraction_gain_at_least_0_05"]
            for g in gates_by_dataset.values()
        ),
        "rank_correlation_at_least_0_15_all_four": all(
            g["rank_correlation_at_least_0_15"]
            for g in gates_by_dataset.values()
        ),
    }
    passed = sum(aggregate_gates.values())
    verdict = "SUPPORTED" if passed == len(aggregate_gates) else "NOT SUPPORTED"
    result = {
        "title": "Q23 Willow connection-web and logical-bit parent ARA",
        "test": "Q23-WILLOW-CONNECTION-WEB-BIT-CLOSURE-v1",
        "source_doi": "10.5281/zenodo.13273331",
        "patch": "d7_at_q6_7",
        "primary_connection_identity": "web_stability",
        "bit_identity": "logical_retention",
        "block_size": BLOCK_SIZE,
        "outcomes_absent_at_freeze": True,
        "freeze_manifest": freeze,
        "outcome_manifest_sha256": sha256(OUTCOME_MANIFEST),
        "results": results,
        "aggregate_gates": aggregate_gates,
        "gate_count_passed": passed,
        "gate_count_total": len(aggregate_gates),
        "overall_verdict": verdict,
        "claim_boundary": (
            "Tests block-level rank closure between one sixteen-path "
            "connection-web stability instrument and logical retention. "
            "It does not identify an external field, establish causality, "
            "or test absolute TE-ARA amplitude transfer."
        ),
    }
    RESULTS.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with METRICS.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(metric_rows[0]))
        writer.writeheader()
        writer.writerows(metric_rows)
    with PROJECTIONS.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(projection_rows[0]))
        writer.writeheader()
        writer.writerows(projection_rows)
    print(verdict, f"{passed}/{len(aggregate_gates)} gates")


if __name__ == "__main__":
    main()

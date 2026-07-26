#!/usr/bin/env python3
"""Independent recomputation of Q23 without importing its runner/features."""

from __future__ import annotations

import hashlib
import json
import pathlib

import numpy as np

from q21_willow_child_topology_calibrate import (
    frozen_spatial_shuffle,
    parse_detector_coordinates,
    recursive_features,
    spatial_weights,
    unpack_detectors,
)


ROOT = pathlib.Path(__file__).parent
GEOMETRY = ROOT / "public_data" / "q23_willow_d7_geometry" / "d7_at_q6_7"
OUTCOMES = ROOT / "public_data" / "q23_willow_d7_outcomes" / "d7_at_q6_7"
FREEZE = ROOT / "Q23_WILLOW_CONNECTION_BIT_FREEZE_MANIFEST.json"
RESULTS = ROOT / "Q23_WILLOW_CONNECTION_BIT_RESULTS.json"
OUTPUT = ROOT / "Q23_WILLOW_CONNECTION_BIT_VALIDATION.json"
BLOCK = 250
PERMUTATIONS = 999
SEED = 20260726


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    output = np.empty(len(values), dtype=np.float64)
    sorted_values = values[order]
    left = 0
    while left < len(values):
        right = left + 1
        while right < len(values) and sorted_values[right] == sorted_values[left]:
            right += 1
        output[order[left:right]] = (left + right - 1) / 2
        left = right
    return 2 * (output + 0.5) / len(values)


def stability(handovers: np.ndarray) -> np.ndarray:
    count = len(handovers) // BLOCK
    web = handovers[: count * BLOCK].reshape(count, BLOCK, 4, 4)
    first = web[:, : BLOCK // 2].mean(axis=1)
    second = web[:, BLOCK // 2 :].mean(axis=1)
    return np.clip(
        2 * (1 - np.abs(second - first).sum(axis=(1, 2)) / 4),
        0,
        2,
    )


def closure(connection_raw: np.ndarray, bit_raw: np.ndarray) -> dict:
    connection = ranks(connection_raw)
    bit = ranks(bit_raw)
    parent = 2 * bit / (connection + bit)
    distance = np.abs(parent - 1)
    return {
        "connection": connection,
        "bit": bit,
        "parent": parent,
        "distance": distance,
        "mean_ridge_distance": float(distance.mean()),
        "median_parent": float(np.median(parent)),
        "near_ridge_fraction_0_10": float((distance <= 0.10).mean()),
        "rank_correlation": float(np.corrcoef(connection, bit)[0, 1]),
    }


def almost(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return bool(abs(left - right) <= tolerance)


def main() -> None:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("freeze_asserts_outcomes_absent", freeze["outcome_files_absent_at_freeze"])
    for name, expected in freeze["frozen_files_sha256"].items():
        check(
            f"frozen_hash_{name}",
            sha256(ROOT / name) == expected,
            expected,
        )
    check(
        "geometry_contains_no_outcomes",
        not bool(list(GEOMETRY.rglob("obs_flips_actual.b8"))),
    )

    raw: dict[tuple[str, str], dict] = {}
    for basis in ("X", "Z"):
        for rounds in ("r13", "r30"):
            path = GEOMETRY / basis / rounds
            metadata = json.loads(
                (path / "metadata.json").read_text(encoding="utf-8")
            )
            shots = int(metadata["shots"])
            coordinates = parse_detector_coordinates(path / "circuit_ideal.stim")
            detectors = unpack_detectors(
                path / "detection_events.b8", shots, len(coordinates)
            )
            weights = spatial_weights(coordinates)
            native, _ = recursive_features(detectors, coordinates, weights)
            broken, _ = recursive_features(
                detectors,
                coordinates,
                frozen_spatial_shuffle(weights, coordinates),
            )
            labels = np.unpackbits(
                np.fromfile(
                    OUTCOMES / basis / rounds / "obs_flips_actual.b8",
                    dtype=np.uint8,
                ),
                bitorder="little",
            )[:shots]
            count = shots // BLOCK
            bit_retention = 2 * (
                1
                - labels[: count * BLOCK]
                .reshape(count, BLOCK)
                .mean(axis=1)
            )
            raw[(basis, rounds)] = {
                "connection": stability(native["handovers"].reshape(-1, 4, 4)),
                "broken": stability(broken["handovers"].reshape(-1, 4, 4)),
                "bit": bit_retention,
                "flip_rate": float(labels.mean()),
            }
            check(f"{basis}_{rounds}_block_count", count == 200, str(count))

    rng = np.random.default_rng(SEED)
    aggregate_components: dict[str, list[bool]] = {
        "coordinates": [],
        "median": [],
        "shift": [],
        "wrong": [],
        "broken": [],
        "p": [],
        "distance_gain": [],
        "near_gain": [],
        "correlation": [],
    }
    for basis in ("X", "Z"):
        other = "Z" if basis == "X" else "X"
        for rounds in ("r13", "r30"):
            key = f"{basis}_{rounds}"
            values = raw[(basis, rounds)]
            observed = closure(values["connection"], values["bit"])
            shifted = closure(
                values["connection"], np.roll(values["bit"], 100)
            )
            wrong = closure(values["connection"], raw[(other, rounds)]["bit"])
            broken = closure(values["broken"], values["bit"])
            saved = result["results"][key]

            for name, calculated in (
                ("paired", observed),
                ("half_cycle_shift", shifted),
                ("wrong_bit", wrong),
                ("broken_spatial_web", broken),
            ):
                for metric in (
                    "mean_ridge_distance",
                    "median_parent",
                    "near_ridge_fraction_0_10",
                    "rank_correlation",
                ):
                    check(
                        f"{key}_{name}_{metric}",
                        almost(
                            calculated[metric],
                            saved["primary"][name][metric],
                        ),
                        f"{calculated[metric]}",
                    )
            check(
                f"{key}_flip_rate",
                almost(values["flip_rate"], saved["flip_rate"]),
                str(values["flip_rate"]),
            )

            null_distance = np.empty(PERMUTATIONS)
            null_near = np.empty(PERMUTATIONS)
            for index in range(PERMUTATIONS):
                bit = rng.permutation(observed["bit"])
                parent = 2 * bit / (observed["connection"] + bit)
                distance = np.abs(parent - 1)
                null_distance[index] = distance.mean()
                null_near[index] = (distance <= 0.10).mean()
            permutation = {
                "null_mean_ridge_distance": float(null_distance.mean()),
                "null_sd_ridge_distance": float(null_distance.std()),
                "null_mean_near_ridge_fraction_0_10": float(null_near.mean()),
                "one_sided_empirical_p": float(
                    (1 + np.sum(null_distance <= observed["mean_ridge_distance"]))
                    / 1000
                ),
            }
            permutation["ridge_distance_gain"] = (
                permutation["null_mean_ridge_distance"]
                - observed["mean_ridge_distance"]
            )
            permutation["near_ridge_fraction_gain"] = (
                observed["near_ridge_fraction_0_10"]
                - permutation["null_mean_near_ridge_fraction_0_10"]
            )
            for metric, calculated in permutation.items():
                check(
                    f"{key}_permutation_{metric}",
                    almost(calculated, saved["permutation"][metric]),
                    str(calculated),
                )

            aggregate_components["coordinates"].append(
                bool(
                    np.all((observed["connection"] > 0) & (observed["connection"] < 2))
                    and np.all((observed["bit"] > 0) & (observed["bit"] < 2))
                    and np.all((observed["parent"] > 0) & (observed["parent"] < 2))
                )
            )
            aggregate_components["median"].append(
                0.95 <= observed["median_parent"] <= 1.05
            )
            aggregate_components["shift"].append(
                observed["mean_ridge_distance"] < shifted["mean_ridge_distance"]
            )
            aggregate_components["wrong"].append(
                observed["mean_ridge_distance"] < wrong["mean_ridge_distance"]
            )
            aggregate_components["broken"].append(
                observed["mean_ridge_distance"] < broken["mean_ridge_distance"]
            )
            aggregate_components["p"].append(
                permutation["one_sided_empirical_p"] <= 0.01
            )
            aggregate_components["distance_gain"].append(
                permutation["ridge_distance_gain"] >= 0.02
            )
            aggregate_components["near_gain"].append(
                permutation["near_ridge_fraction_gain"] >= 0.05
            )
            aggregate_components["correlation"].append(
                observed["rank_correlation"] >= 0.15
            )

    expected_gates = {
        "source_and_freeze_integrity": True,
        "all_coordinates_inside_open_0_2": all(
            aggregate_components["coordinates"]
        ),
        "parent_median_near_1_all_four": all(
            aggregate_components["median"]
        ),
        "closer_than_half_cycle_shift_all_four": all(
            aggregate_components["shift"]
        ),
        "closer_than_wrong_bit_all_four": all(
            aggregate_components["wrong"]
        ),
        "closer_than_broken_spatial_web_all_four": all(
            aggregate_components["broken"]
        ),
        "permutation_p_at_most_0_01_all_four": all(
            aggregate_components["p"]
        ),
        "ridge_distance_gain_at_least_0_02_all_four": all(
            aggregate_components["distance_gain"]
        ),
        "near_ridge_fraction_gain_at_least_0_05_all_four": all(
            aggregate_components["near_gain"]
        ),
        "rank_correlation_at_least_0_15_all_four": all(
            aggregate_components["correlation"]
        ),
    }
    for name, expected in expected_gates.items():
        check(
            f"aggregate_gate_{name}",
            result["aggregate_gates"][name] == expected,
            str(expected),
        )
    passed_gates = sum(expected_gates.values())
    check("gate_count", result["gate_count_passed"] == passed_gates)
    check(
        "verdict",
        result["overall_verdict"]
        == ("SUPPORTED" if passed_gates == len(expected_gates) else "NOT SUPPORTED"),
    )

    failures = [item for item in checks if not item["passed"]]
    validation = {
        "title": "Independent Q23 validation",
        "validation_status": "PASS" if not failures else "FAIL",
        "checks_passed": len(checks) - len(failures),
        "checks_total": len(checks),
        "failures": failures,
        "checks": checks,
        "independence": (
            "Rebuilt detector handovers, spatial-break control, block identities, "
            "rank diameters, parent ARA, controls, gates and all 3,996 "
            "permutations without importing q23_connection_bit_features.py "
            "or q23_connection_bit_test.py."
        ),
    }
    OUTPUT.write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        validation["validation_status"],
        f"{validation['checks_passed']}/{validation['checks_total']} checks",
    )
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

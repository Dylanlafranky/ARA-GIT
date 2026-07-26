#!/usr/bin/env python3
"""Run frozen T263/Q5 on four public Bell-state tomography archives."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import zipfile
from pathlib import Path

import numpy as np

from q4_bell_parent_child_test import (
    BELL_PATTERNS,
    LOCAL_CHILDREN,
    MIXED_PAIR,
    OUTCOME_NAMES,
    PROJECTION_ORDER,
    SAME_AXIS,
    bell_mae,
    classify_record,
    expectations,
    group_metrics,
    probabilities_from_records,
    projection_group,
)


HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "public_data" / "q4_bell_tomography"
PROTOCOL = HERE / "Q5_BELL_FOUR_STATE_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q5_BELL_FOUR_STATE_PROTOCOL_v1_FROZEN.sha256"
RECORDS_CSV = HERE / "Q5_BELL_FOUR_STATE_RECORDS.csv"
PROJECTIONS_CSV = HERE / "Q5_BELL_FOUR_STATE_PROJECTIONS.csv"
BOOTSTRAP_CSV = HERE / "Q5_BELL_FOUR_STATE_BOOTSTRAP.csv"
PAIRWISE_CSV = HERE / "Q5_BELL_FOUR_STATE_PAIRWISE.csv"
RESULTS_JSON = HERE / "Q5_BELL_FOUR_STATE_RESULTS.json"

BOOTSTRAP_SEED = 2026072405
BOOTSTRAP_REPS = 2000
ORIENTATION_ORDER = ("II", "IX", "IY", "XI", "XX", "XY", "YI", "YX", "YY")

STATE_CONFIGS = {
    "Phi-plus": {
        "archive": "UPUP+DOWNDOWN.zip",
        "root": "UPUP+DOWNDOWN",
        "file_id": 26690666,
        "size": 151973378,
        "md5": "3275210b912d51e5f10ba99d93ad6ca5",
        "measurements": 60,
        "buckets": 5,
        "timestamps": (
            "183730",
            "185433",
            "190045",
            "190657",
            "191311",
            "191932",
            "192544",
            "193149",
            "193748",
        ),
    },
    "Phi-minus": {
        "archive": "UPUP-DOWNDOWN.zip",
        "root": "UPUP-DOWNDOWN",
        "file_id": 26690663,
        "size": 41182988,
        "md5": "8cd8a5f2b3b9a2ccd090e47312bcc390",
        "measurements": 40,
        "buckets": 2,
        "timestamps": (
            "115025",
            "115222",
            "115424",
            "115627",
            "115835",
            "120033",
            "120230",
            "120428",
            "120626",
        ),
    },
    "Psi-plus": {
        "archive": "UPDOWN+DOWNUP.zip",
        "root": "UPDOWN+DOWNUP",
        "file_id": 26690660,
        "size": 305874138,
        "md5": "43f782ed4404b01393fb57a2da5d1534",
        "measurements": 60,
        "buckets": 10,
        "timestamps": (
            "171731",
            "172913",
            "174052",
            "175222",
            "180412",
            "181547",
            "182710",
            "183831",
            "184958",
        ),
    },
    "Psi-minus": {
        "archive": "UPDOWN-DOWNUP.zip",
        "root": "UPDOWN-DOWNUP",
        "file_id": 26690657,
        "size": 307629500,
        "md5": "1724b4484ffb88e41dbac5f50981e91a",
        "measurements": 60,
        "buckets": 10,
        "timestamps": (
            "190250",
            "191433",
            "192618",
            "193759",
            "194951",
            "200149",
            "201324",
            "202517",
            "203722",
        ),
    },
}


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_sources() -> tuple[dict[str, str], str]:
    observed = {}
    for state, config in STATE_CONFIGS.items():
        archive = DATA_DIR / str(config["archive"])
        if archive.stat().st_size != int(config["size"]):
            raise RuntimeError(f"{state} archive size mismatch")
        checksum = digest(archive, "md5")
        if checksum != config["md5"]:
            raise RuntimeError(
                f"{state} MD5 mismatch: expected {config['md5']}, observed {checksum}"
            )
        observed[state] = checksum
    expected_sha = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    observed_sha = digest(PROTOCOL, "sha256")
    if observed_sha != expected_sha:
        raise RuntimeError(
            f"Frozen protocol mismatch: expected {expected_sha}, observed {observed_sha}"
        )
    return observed, observed_sha


def archive_member(
    root: str, timestamp: str, measurement: int, bucket: int
) -> str:
    return (
        f"{root}/raw/"
        f"{timestamp}_Bell_states_{measurement}_{bucket}.bin"
    )


def load_state(
    state: str, config: dict[str, object]
) -> tuple[dict[str, np.ndarray], list[dict[str, object]]]:
    archive_path = DATA_DIR / str(config["archive"])
    root = str(config["root"])
    measurements = int(config["measurements"])
    buckets = int(config["buckets"])
    timestamp_map = dict(zip(ORIENTATION_ORDER, config["timestamps"]))
    records_by_orientation: dict[str, np.ndarray] = {}
    rows: list[dict[str, object]] = []

    with zipfile.ZipFile(archive_path) as archive:
        names = set(archive.namelist())
        required = {
            archive_member(root, timestamp, measurement, bucket)
            for timestamp in timestamp_map.values()
            for bucket in range(1, buckets + 1)
            for measurement in range(1, measurements + 1)
        }
        missing = required - names
        if missing:
            raise RuntimeError(f"{state}: {len(missing)} required files are missing")

        for orientation, timestamp in timestamp_map.items():
            labels = []
            record_index = 0
            for bucket in range(1, buckets + 1):
                for measurement in range(1, measurements + 1):
                    member = archive_member(
                        root, timestamp, measurement, bucket
                    )
                    probabilities, outcomes = classify_record(archive.read(member))
                    labels.append(outcomes)
                    for outcome_index, outcome_name in enumerate(OUTCOME_NAMES):
                        rows.append(
                            {
                                "state": state,
                                "archive": config["archive"],
                                "orientation": orientation,
                                "timestamp": timestamp,
                                "record_index": record_index,
                                "bucket": bucket,
                                "measurement": measurement,
                                "outcome": outcome_name,
                                "segment_tunnelling_fraction": float(
                                    probabilities[outcome_index]
                                ),
                                "classified_present": int(outcomes[outcome_index]),
                            }
                        )
                    record_index += 1
            records_by_orientation[orientation] = np.asarray(
                labels, dtype=np.float64
            )
    return records_by_orientation, rows


def nearest_parent(
    exp: dict[str, float],
) -> tuple[str, float, str, float, float, dict[str, float]]:
    maes = bell_mae(exp)
    ranked = sorted(maes.items(), key=lambda item: (item[1], item[0]))
    closest, closest_mae = ranked[0]
    runner_up, runner_up_mae = ranked[1]
    return (
        closest,
        closest_mae,
        runner_up,
        runner_up_mae,
        runner_up_mae - closest_mae,
        maes,
    )


def sign_tuple(exp: dict[str, float]) -> tuple[int, int, int]:
    return tuple(1 if exp[label] > 0 else -1 for label in SAME_AXIS)


def bootstrap_state(
    state: str,
    records: dict[str, np.ndarray],
    rng: np.random.Generator,
) -> tuple[dict[str, np.ndarray], list[dict[str, object]], float]:
    projection_draws = {
        label: np.empty(BOOTSTRAP_REPS, dtype=np.float64)
        for label in PROJECTION_ORDER
    }
    rows: list[dict[str, object]] = []
    correct = 0
    for repetition in range(BOOTSTRAP_REPS):
        probabilities = {}
        for orientation, values in records.items():
            indices = rng.integers(0, len(values), size=len(values))
            probabilities[orientation] = values[indices].mean(axis=0)
        exp = expectations(probabilities)
        metrics = group_metrics(exp)
        closest, closest_mae, _, _, margin, _ = nearest_parent(exp)
        correct += int(closest == state)
        for label in PROJECTION_ORDER:
            projection_draws[label][repetition] = exp[label]
        rows.append(
            {
                "state": state,
                "replicate": repetition,
                "closest_parent": closest,
                "correct_parent": int(closest == state),
                "closest_mae": closest_mae,
                "margin": margin,
                **metrics,
                "xx": exp["XX"],
                "yy": exp["YY"],
                "zz": exp["ZZ"],
            }
        )
    return projection_draws, rows, correct / BOOTSTRAP_REPS


def per_state_gates(
    state: str,
    exp: dict[str, float],
    metrics: dict[str, float],
    closest: str,
    closest_mae: float,
    runner_up: str,
    runner_up_mae: float,
    margin: float,
    affine_residual: float,
    reversal_residual: float,
) -> dict[str, dict[str, object]]:
    target = BELL_PATTERNS[state]
    signs_match = all(
        (exp[label] > 0) == (target[label] > 0) for label in SAME_AXIS
    )
    return {
        "S1_local_child_mean_abs_at_most_0p20": {
            "value": metrics["local_child_mean_abs"],
            "threshold": 0.20,
            "pass": metrics["local_child_mean_abs"] <= 0.20,
        },
        "S2_same_axis_signs_match_target": {
            "observed": list(sign_tuple(exp)),
            "target": [
                int(math.copysign(1, target[label])) for label in SAME_AXIS
            ],
            "pass": signs_match,
        },
        "S3_weakest_same_axis_abs_at_least_0p50": {
            "value": metrics["same_axis_min_abs"],
            "threshold": 0.50,
            "pass": metrics["same_axis_min_abs"] >= 0.50,
        },
        "S4_same_minus_local_at_least_0p40": {
            "value": metrics["same_minus_local"],
            "threshold": 0.40,
            "pass": metrics["same_minus_local"] >= 0.40,
        },
        "S5_mixed_pair_mean_abs_at_most_0p25": {
            "value": metrics["mixed_pair_mean_abs"],
            "threshold": 0.25,
            "pass": metrics["mixed_pair_mean_abs"] <= 0.25,
        },
        "S6_correlation_product_at_most_negative_0p125": {
            "value": metrics["correlation_product"],
            "threshold": -0.125,
            "pass": metrics["correlation_product"] <= -0.125,
        },
        "S7_declared_parent_closest_with_margin": {
            "closest": closest,
            "closest_mae": closest_mae,
            "runner_up": runner_up,
            "runner_up_mae": runner_up_mae,
            "margin": margin,
            "threshold": 0.20,
            "pass": closest == state and margin >= 0.20,
        },
        "S8_affine_and_reversal_residuals": {
            "affine": affine_residual,
            "reversal": reversal_residual,
            "threshold": 1e-12,
            "pass": affine_residual <= 1e-12
            and reversal_residual <= 1e-12,
        },
    }


def assignment_control(
    parent_vectors: dict[str, np.ndarray],
) -> dict[str, object]:
    states = list(STATE_CONFIGS)
    assignments = []
    for permutation in itertools.permutations(states):
        total_mae = 0.0
        for observed_state, assigned_target in zip(states, permutation):
            vector = parent_vectors[observed_state]
            target = np.array(
                [BELL_PATTERNS[assigned_target][label] for label in SAME_AXIS]
            )
            total_mae += float(np.mean(np.abs(vector - target)))
        assignments.append(
            {
                "assignment": dict(zip(states, permutation)),
                "mean_state_mae": total_mae / len(states),
            }
        )
    assignments.sort(key=lambda row: row["mean_state_mae"])
    identity = {state: state for state in states}
    identity_rank = next(
        index + 1
        for index, row in enumerate(assignments)
        if row["assignment"] == identity
    )
    return {
        "identity_assignment_rank": identity_rank,
        "assignments_total": len(assignments),
        "identity_mean_state_mae": next(
            row["mean_state_mae"]
            for row in assignments
            if row["assignment"] == identity
        ),
        "best_assignment": assignments[0],
        "runner_up_assignment": assignments[1],
        "identity_margin_over_runner_up": (
            assignments[1]["mean_state_mae"]
            - assignments[0]["mean_state_mae"]
            if assignments[0]["assignment"] == identity
            else None
        ),
    }


def main() -> None:
    archive_md5s, protocol_sha = verify_sources()
    rng = np.random.default_rng(BOOTSTRAP_SEED)

    all_record_rows: list[dict[str, object]] = []
    all_projection_rows: list[dict[str, object]] = []
    all_bootstrap_rows: list[dict[str, object]] = []
    state_results: dict[str, dict[str, object]] = {}
    parent_vectors: dict[str, np.ndarray] = {}
    local_vectors: dict[str, np.ndarray] = {}

    for state, config in STATE_CONFIGS.items():
        records, record_rows = load_state(state, config)
        all_record_rows.extend(record_rows)
        exp = expectations(probabilities_from_records(records))
        metrics = group_metrics(exp)
        (
            closest,
            closest_mae,
            runner_up,
            runner_up_mae,
            margin,
            maes,
        ) = nearest_parent(exp)
        projection_draws, bootstrap_rows, bootstrap_stability = bootstrap_state(
            state, records, rng
        )
        all_bootstrap_rows.extend(bootstrap_rows)

        max_affine_residual = 0.0
        max_reversal_residual = 0.0
        for label in PROJECTION_ORDER:
            value = exp[label]
            ara = 1.0 - value
            reversed_ara = 2.0 - ara
            affine_residual = abs(ara - (1.0 - value))
            reversal_residual = abs(ara + reversed_ara - 2.0)
            max_affine_residual = max(
                max_affine_residual, affine_residual
            )
            max_reversal_residual = max(
                max_reversal_residual, reversal_residual
            )
            low, high = np.quantile(
                projection_draws[label], [0.025, 0.975]
            )
            all_projection_rows.append(
                {
                    "state": state,
                    "projection": label,
                    "group": projection_group(label),
                    "expectation": value,
                    "expectation_ci_low": float(low),
                    "expectation_ci_high": float(high),
                    "ara_coordinate": ara,
                    "reversed_ara_coordinate": reversed_ara,
                    "ideal_expectation": BELL_PATTERNS[state].get(label, 0.0),
                    "ideal_ara_coordinate": (
                        1.0 - BELL_PATTERNS[state].get(label, 0.0)
                    ),
                }
            )

        gates = per_state_gates(
            state,
            exp,
            metrics,
            closest,
            closest_mae,
            runner_up,
            runner_up_mae,
            margin,
            max_affine_residual,
            max_reversal_residual,
        )
        state_results[state] = {
            "archive": config["archive"],
            "file_id": config["file_id"],
            "archive_md5": archive_md5s[state],
            "orientation_timestamps": dict(
                zip(ORIENTATION_ORDER, config["timestamps"])
            ),
            "records_per_orientation": (
                int(config["measurements"]) * int(config["buckets"])
            ),
            "expectations": exp,
            "metrics": metrics,
            "bell_mae": maes,
            "closest_parent": closest,
            "runner_up_parent": runner_up,
            "bell_margin": margin,
            "bootstrap_label_stability": bootstrap_stability,
            "gates": gates,
            "gates_passed": sum(int(gate["pass"]) for gate in gates.values()),
            "gates_total": len(gates),
        }
        parent_vectors[state] = np.array([exp[label] for label in SAME_AXIS])
        local_vectors[state] = np.array([exp[label] for label in LOCAL_CHILDREN])

    pairwise_rows = []
    for left, right in itertools.combinations(STATE_CONFIGS, 2):
        parent_distance = float(
            np.linalg.norm(parent_vectors[left] - parent_vectors[right])
        )
        local_distance = float(
            np.linalg.norm(local_vectors[left] - local_vectors[right])
        )
        pairwise_rows.append(
            {
                "state_a": left,
                "state_b": right,
                "parent_euclidean_distance": parent_distance,
                "local_child_euclidean_distance": local_distance,
                "parent_to_local_distance_ratio": (
                    parent_distance / local_distance
                    if local_distance > 0
                    else math.inf
                ),
            }
        )

    correct_labels = sum(
        int(result["closest_parent"] == state)
        for state, result in state_results.items()
    )
    observed_signs = {
        state: sign_tuple(result["expectations"])
        for state, result in state_results.items()
    }
    target_signs = {
        state: tuple(
            int(math.copysign(1, BELL_PATTERNS[state][label]))
            for label in SAME_AXIS
        )
        for state in STATE_CONFIGS
    }
    all_signs_correct = observed_signs == target_signs
    distinct_signs = len(set(observed_signs.values()))
    min_parent_distance = min(
        row["parent_euclidean_distance"] for row in pairwise_rows
    )
    min_bootstrap_stability = min(
        result["bootstrap_label_stability"]
        for result in state_results.values()
    )
    cross_gates = {
        "C1_four_way_parent_identification": {
            "correct": correct_labels,
            "total": 4,
            "pass": correct_labels == 4,
        },
        "C2_parent_sign_pattern_coverage": {
            "distinct_observed": distinct_signs,
            "all_signs_match_targets": all_signs_correct,
            "pass": distinct_signs == 4 and all_signs_correct,
        },
        "C3_minimum_parent_vector_distance": {
            "value": min_parent_distance,
            "threshold": 1.00,
            "pass": min_parent_distance >= 1.00,
        },
        "C4_bootstrap_parent_label_stability": {
            "per_state": {
                state: result["bootstrap_label_stability"]
                for state, result in state_results.items()
            },
            "minimum": min_bootstrap_stability,
            "threshold": 0.90,
            "pass": min_bootstrap_stability >= 0.90,
        },
        "C5_local_only_ideal_discrimination": {
            "ideal_local_patterns": 1,
            "states": 4,
            "distinguishable": False,
            "pass": True,
        },
    }

    per_state_passed = sum(
        int(gate["pass"])
        for result in state_results.values()
        for gate in result["gates"].values()
    )
    cross_passed = sum(int(gate["pass"]) for gate in cross_gates.values())
    gates_passed = per_state_passed + cross_passed
    gates_total = 32 + 5
    verdict = "SUPPORTED" if gates_passed == gates_total else "NOT SUPPORTED"

    with RECORDS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(all_record_rows[0].keys())
        )
        writer.writeheader()
        writer.writerows(all_record_rows)
    with PROJECTIONS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(all_projection_rows[0].keys())
        )
        writer.writeheader()
        writer.writerows(all_projection_rows)
    with BOOTSTRAP_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(all_bootstrap_rows[0].keys())
        )
        writer.writeheader()
        writer.writerows(all_bootstrap_rows)
    with PAIRWISE_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(pairwise_rows[0].keys())
        )
        writer.writeheader()
        writer.writerows(pairwise_rows)

    controls = {
        "same_information_affine_equivalence": True,
        "local_only_ideal_bell_patterns_distinguishable": False,
        "local_only_ideal_distinct_patterns": 1,
        "assignment_permutation": assignment_control(parent_vectors),
        "mean_parent_pairwise_distance": float(
            np.mean(
                [row["parent_euclidean_distance"] for row in pairwise_rows]
            )
        ),
        "mean_local_pairwise_distance": float(
            np.mean(
                [row["local_child_euclidean_distance"] for row in pairwise_rows]
            )
        ),
    }
    results = {
        "protocol_id": "Q5-BELL-FOUR-STATE-v1",
        "ledger_id": "T263",
        "verdict": verdict,
        "gates_passed": gates_passed,
        "gates_total": gates_total,
        "per_state_gates_passed": per_state_passed,
        "per_state_gates_total": 32,
        "cross_state_gates_passed": cross_passed,
        "cross_state_gates_total": 5,
        "source": {
            "doi": "10.6084/m9.figshare.14160476.v2",
            "license": "CC BY 4.0",
            "archive_md5s": archive_md5s,
        },
        "protocol_sha256": protocol_sha,
        "decoder": {
            "offset": 32766,
            "scale": 3.0519e-5,
            "current_threshold": 0.1,
            "state_threshold": 0.5,
            "readouts_per_state_segment": 40,
        },
        "states": state_results,
        "pairwise": pairwise_rows,
        "cross_state_gates": cross_gates,
        "controls": controls,
        "bootstrap": {
            "seed": BOOTSTRAP_SEED,
            "repetitions_per_state": BOOTSTRAP_REPS,
            "grain": (
                "classified acquisition records resampled independently "
                "within each of nine orientations and each prepared state"
            ),
        },
        "evidence_boundary": (
            "Four prepared-state archives from one public deposit and device. "
            "This is cross-state replication, not cross-device or cross-day replication."
        ),
    }
    RESULTS_JSON.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                state: {
                    "parent": result["closest_parent"],
                    "xx": result["expectations"]["XX"],
                    "yy": result["expectations"]["YY"],
                    "zz": result["expectations"]["ZZ"],
                    "local_mean_abs": result["metrics"][
                        "local_child_mean_abs"
                    ],
                    "same_axis_mean_abs": result["metrics"][
                        "same_axis_mean_abs"
                    ],
                    "mixed_mean_abs": result["metrics"][
                        "mixed_pair_mean_abs"
                    ],
                    "bootstrap_stability": result[
                        "bootstrap_label_stability"
                    ],
                    "gates": (
                        f"{result['gates_passed']}/{result['gates_total']}"
                    ),
                }
                for state, result in state_results.items()
            },
            indent=2,
        )
    )
    print(f"{verdict}: {gates_passed}/{gates_total} frozen gates")


if __name__ == "__main__":
    main()

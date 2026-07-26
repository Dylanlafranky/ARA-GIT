"""Independent validation for Q1 open-qubit multi-axis ARA outputs."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_PROTOCOL_v1_FROZEN.sha256"
DEVELOPMENT = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_DEVELOPMENT.csv"
TRIALS = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_TRIALS.csv"
AGGREGATES = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_AGGREGATES.csv"
TRAJECTORIES = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_TRAJECTORIES.csv"
RESULTS = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_RESULTS.json"
VALIDATION = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_VALIDATION.json"

EXPECTED_HASH = "f51c0b44a29869f90af88ada873f1363441424dfc9e2584fcdc5b19215700a2b"
FAMILIES = ("U", "T2", "T1", "C")
ROTATING = {"U", "C"}
RIDGE = {"U", "T2"}
PRIMARY_SHOTS = 128


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def balanced_accuracy(labels: np.ndarray, predictions: np.ndarray) -> float:
    return float(
        np.mean(
            [
                np.mean(predictions[labels == value] == value)
                for value in np.unique(labels)
            ]
        )
    )


def select_threshold(scores: list[float], labels: list[int]) -> tuple[float, float]:
    score = np.asarray(scores, dtype=float)
    label = np.asarray(labels, dtype=int)
    unique = np.unique(score)
    if len(unique) == 1:
        candidates = np.asarray([unique[0]])
    else:
        span = max(1.0, float(unique[-1] - unique[0]))
        candidates = np.concatenate(
            (
                [unique[0] - 1e-12 * span],
                (unique[:-1] + unique[1:]) / 2.0,
                [unique[-1] + 1e-12 * span],
            )
        )
    best = None
    for threshold in candidates:
        prediction = (score >= threshold).astype(int)
        ba = balanced_accuracy(label, prediction)
        candidate = (float(ba), -float(threshold), float(threshold))
        if best is None or candidate > best:
            best = candidate
    assert best is not None
    return best[2], best[0]


def close(a: float, b: float, tolerance: float = 1e-12) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tolerance)


def record(checks: list[dict[str, object]], name: str, passed: bool, detail: str) -> None:
    checks.append({"check": name, "passed": bool(passed), "detail": detail})


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    dev = rows(DEVELOPMENT)
    trial = rows(TRIALS)
    aggregate = rows(AGGREGATES)
    trajectory = rows(TRAJECTORIES)
    checks: list[dict[str, object]] = []

    actual_hash = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    sha_text = PROTOCOL_SHA.read_text(encoding="utf-8").strip().split()[0]
    record(
        checks,
        "frozen_protocol_hash",
        actual_hash == EXPECTED_HASH == sha_text == result["protocol_sha256"],
        actual_hash,
    )

    record(
        checks,
        "row_counts",
        len(dev) == 256 and len(trial) == 3072 and len(aggregate) == 6 and len(trajectory) == 260,
        f"development={len(dev)}, target={len(trial)}, aggregates={len(aggregate)}, trajectories={len(trajectory)}",
    )

    dev_ids = {row["base_id"] for row in dev}
    target_ids = {row["base_id"] for row in trial}
    record(
        checks,
        "development_target_separation",
        not dev_ids.intersection(target_ids)
        and all(value.startswith("D") for value in dev_ids)
        and all(value.startswith("T") for value in target_ids),
        f"development IDs={len(dev_ids)}, target IDs={len(target_ids)}",
    )

    rot_threshold, rot_ba = select_threshold(
        [float(row["rotation_score"]) for row in dev],
        [int(row["rotating_label"]) for row in dev],
    )
    relax_threshold, relax_ba = select_threshold(
        [float(row["relaxation_score"]) for row in dev],
        [int(row["relaxing_label"]) for row in dev],
    )
    ridge_dev = [row for row in dev if row["family"] in RIDGE]
    ridge_threshold, ridge_ba = select_threshold(
        [float(row["ridge_coherence"]) for row in ridge_dev],
        [int(row["ridge_u_label"]) for row in ridge_dev],
    )
    saved_thresholds = result["thresholds_selected_on_development_only"]
    threshold_pass = (
        close(rot_threshold, float(saved_thresholds["rotation"]))
        and close(relax_threshold, float(saved_thresholds["relaxation"]))
        and close(ridge_threshold, float(saved_thresholds["ridge_coherence"]))
        and close(rot_ba, float(saved_thresholds["development_rotation_balanced_accuracy"]))
        and close(relax_ba, float(saved_thresholds["development_relaxation_balanced_accuracy"]))
        and close(ridge_ba, float(saved_thresholds["development_ridge_balanced_accuracy"]))
    )
    record(
        checks,
        "development_threshold_reproduction",
        threshold_pass,
        f"rotation={rot_threshold:.12g}, relaxation={relax_threshold:.12g}, ridge={ridge_threshold:.12g}",
    )

    def classify(row: dict[str, str]) -> str:
        rotating = float(row["rotation_score"]) >= rot_threshold
        relaxing = float(row["relaxation_score"]) >= relax_threshold
        return "C" if rotating and relaxing else "T1" if relaxing else "U" if rotating else "T2"

    prediction_match = all(classify(row) == row["ara_prediction"] for row in trial)
    record(
        checks,
        "target_prediction_reproduction",
        prediction_match,
        "recomputed from frozen development thresholds",
    )

    paired_ok = True
    for shots in (32, 64, 128, 256, 512, 1024):
        subset = [row for row in trial if int(row["shots"]) == shots]
        by_base: dict[str, dict[str, dict[str, str]]] = {}
        for row in subset:
            by_base.setdefault(row["base_id"], {})[row["family"]] = row
        for family_rows in by_base.values():
            if set(family_rows) != set(FAMILIES):
                paired_ok = False
                break
            for parameter in ("omega", "t1", "tphi"):
                if len({family_rows[family][parameter] for family in FAMILIES}) != 1:
                    paired_ok = False
            if not close(
                float(family_rows["U"]["clean_z_sum"]),
                float(family_rows["T2"]["clean_z_sum"]),
            ):
                paired_ok = False
            if not close(
                float(family_rows["T1"]["clean_z_sum"]),
                float(family_rows["C"]["clean_z_sum"]),
            ):
                paired_ok = False
    record(
        checks,
        "paired_known_referee_identities",
        paired_ok,
        "same parameters per base; U=T2 and T1=C clean Z sums",
    )

    initial_ok = True
    for family in FAMILIES:
        first = next(
            row
            for row in trajectory
            if row["family"] == family and close(float(row["time"]), 0.0)
        )
        initial = [float(first["true_rx"]), float(first["true_ry"]), float(first["true_rz"])]
        initial_ok &= np.allclose(initial, [1.0, 0.0, 0.0], atol=1e-15, rtol=0.0)
    record(checks, "common_initial_state", initial_ok, "all four families start at (1,0,0)")

    observation_fields = ("observed_xx", "observed_xy", "observed_xz")
    bounds_ok = all(
        0.0 <= float(row[field]) <= 2.0 for row in trajectory for field in observation_fields
    )
    record(checks, "finite_shot_reading_bounds", bounds_ok, "all recorded cuts lie in [0,2]")

    analytic_rng = np.random.default_rng(90210)
    state = analytic_rng.uniform(-1.0, 1.0, size=(65, 3))
    state /= np.maximum(1.0, np.linalg.norm(state, axis=1))[:, None]
    directions = analytic_rng.normal(size=(16, 3))
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    plus = 1.0 - state @ directions.T
    minus = 1.0 + state @ directions.T
    analytic_error = float(np.max(np.abs(plus + minus - 2.0)))
    record(
        checks,
        "analytic_antipodal_complement",
        analytic_error <= 1e-15,
        f"max residual={analytic_error:.3g}",
    )

    max_state_diff = max(float(row["ara_bloch_max_state_diff"]) for row in trial)
    max_score_diff = max(float(row["ara_bloch_max_score_diff"]) for row in trial)
    disagreements = sum(int(row["ara_bloch_disagreement"]) for row in trial)
    record(
        checks,
        "same_information_ara_bloch_equivalence",
        max_state_diff <= 1e-12 and max_score_diff <= 1e-12 and disagreements == 0,
        f"state={max_state_diff:.3g}, score={max_score_diff:.3g}, disagreements={disagreements}",
    )

    primary = [row for row in trial if int(row["shots"]) == PRIMARY_SHOTS]
    primary_aggregate = next(row for row in aggregate if int(row["shots"]) == PRIMARY_SHOTS)

    def mean(field: str, subset: list[dict[str, str]] = primary) -> float:
        return float(np.mean([float(row[field]) for row in subset if row[field] != ""]))

    rotating_primary = [row for row in primary if row["family"] in ROTATING]
    ridge_primary = [row for row in primary if row["family"] in RIDGE]
    recomputed = {
        "ara_accuracy": mean("ara_correct"),
        "z_accuracy": mean("z_correct"),
        "native_accuracy": mean("native_correct"),
        "time_shuffle_accuracy": mean("time_shuffle_correct"),
        "axis_shuffle_accuracy": mean("axis_shuffle_correct"),
        "rotation_direction_accuracy": mean("direction_correct", rotating_primary),
        "ridge_u_vs_t2_accuracy": mean("ridge_correct", ridge_primary),
        "heldout_mae": mean("heldout_mae"),
    }
    aggregate_ok = all(
        close(value, float(primary_aggregate[field])) for field, value in recomputed.items()
    )
    record(
        checks,
        "primary_aggregate_reproduction",
        aggregate_ok,
        json.dumps(recomputed, sort_keys=True),
    )

    gate_values = {
        "four_class_accuracy": recomputed["ara_accuracy"],
        "gain_over_z": recomputed["ara_accuracy"] - recomputed["z_accuracy"],
        "rotation_direction_accuracy": recomputed["rotation_direction_accuracy"],
        "u_vs_t2_ridge_accuracy": recomputed["ridge_u_vs_t2_accuracy"],
        "heldout_directional_mae": recomputed["heldout_mae"],
        "ara_bloch_max_score_difference": max(
            float(row["ara_bloch_max_score_diff"]) for row in primary
        ),
        "ara_bloch_classification_disagreements": sum(
            int(row["ara_bloch_disagreement"]) for row in primary
        ),
        "time_shuffle_accuracy": recomputed["time_shuffle_accuracy"],
        "axis_shuffle_accuracy": recomputed["axis_shuffle_accuracy"],
    }
    expected_pass = {
        "four_class_accuracy": gate_values["four_class_accuracy"] >= 0.90,
        "gain_over_z": gate_values["gain_over_z"] >= 0.30,
        "rotation_direction_accuracy": gate_values["rotation_direction_accuracy"] >= 0.90,
        "u_vs_t2_ridge_accuracy": gate_values["u_vs_t2_ridge_accuracy"] >= 0.95,
        "heldout_directional_mae": gate_values["heldout_directional_mae"] <= 0.08,
        "ara_bloch_max_score_difference": gate_values[
            "ara_bloch_max_score_difference"
        ]
        <= 1e-12,
        "ara_bloch_classification_disagreements": gate_values[
            "ara_bloch_classification_disagreements"
        ]
        == 0,
        "time_shuffle_accuracy": gate_values["time_shuffle_accuracy"] <= 0.65,
        "axis_shuffle_accuracy": gate_values["axis_shuffle_accuracy"] <= 0.65,
    }
    gate_ok = True
    for name, value in gate_values.items():
        saved = result["primary_gates"][name]
        gate_ok &= close(float(saved["value"]), float(value))
        gate_ok &= bool(saved["passed"]) == expected_pass[name]
    expected_verdict = "SUPPORTED" if all(expected_pass.values()) else "NOT SUPPORTED"
    gate_ok &= result["verdict"] == expected_verdict
    record(
        checks,
        "frozen_gate_reproduction",
        gate_ok,
        f"{sum(expected_pass.values())}/{len(expected_pass)} gates; verdict={expected_verdict}",
    )

    raw_frequency = mean("raw_unphysical_fraction")
    physical_radius_max = max(
        math.sqrt(
            float(row["estimated_rx"]) ** 2
            + float(row["estimated_ry"]) ** 2
            + float(row["estimated_rz"]) ** 2
        )
        for row in trajectory
    )
    record(
        checks,
        "physical_projection_and_raw_control",
        physical_radius_max <= 1.0 + 1e-12 and raw_frequency > 0.0,
        f"max physical radius={physical_radius_max:.12g}, raw outside fraction={raw_frequency:.6g}",
    )

    shot_order = [int(row["shots"]) for row in aggregate]
    record(
        checks,
        "registered_shot_ladder",
        shot_order == [32, 64, 128, 256, 512, 1024],
        str(shot_order),
    )

    all_passed = all(bool(item["passed"]) for item in checks)
    validation = {
        "validator": "q1_open_qubit_multi_axis_validate.py",
        "all_checks_passed": all_passed,
        "passed": sum(int(bool(item["passed"])) for item in checks),
        "total": len(checks),
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(f"Independent validation: {validation['passed']}/{validation['total']}")
    for item in checks:
        print(f"[{'PASS' if item['passed'] else 'FAIL'}] {item['check']}: {item['detail']}")
    if not all_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()


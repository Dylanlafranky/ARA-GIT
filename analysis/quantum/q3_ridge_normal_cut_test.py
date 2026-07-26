#!/usr/bin/env python3
"""Post-hoc Q3 calibration of the ARA ridge-normal cut on public Q2 I/Q data."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.io import loadmat


HERE = Path(__file__).resolve().parent
SOURCE_ROOT = (
    HERE
    / "public_data"
    / "extracted"
    / "AllopticalSCQreadout_data"
    / "Fig_4a"
)
PROTOCOL = HERE / "Q3_RIDGE_NORMAL_CUT_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q3_RIDGE_NORMAL_CUT_PROTOCOL_v1_FROZEN.sha256"
FOLDS_CSV = HERE / "Q3_RIDGE_NORMAL_CUT_FOLDS.csv"
SWEEP_CSV = HERE / "Q3_RIDGE_NORMAL_CUT_SWEEP.csv"
RESULTS_JSON = HERE / "Q3_RIDGE_NORMAL_CUT_RESULTS.json"
CONDITIONS = (0, 10, 50, 250, 500, 1000)
RCOND = 1e-12


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_freeze() -> str:
    expected = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0].lower()
    observed = sha256(PROTOCOL)
    if expected != observed:
        raise RuntimeError(
            f"Frozen protocol hash mismatch: expected {expected}, observed {observed}"
        )
    return observed


def load_data() -> dict[int, dict[int, np.ndarray]]:
    out: dict[int, dict[int, np.ndarray]] = {}
    for condition in CONDITIONS:
        path = SOURCE_ROOT / f"IQblobs_{condition}Hz.mat"
        if not path.exists():
            raise FileNotFoundError(
                f"Missing {path}. Reproduce Q2 public data before running Q3."
            )
        raw = loadmat(path, variable_names=["I_g", "Q_g", "I_e", "Q_e"])
        g = np.column_stack(
            [
                np.asarray(raw["I_g"], dtype=np.float64).reshape(-1),
                np.asarray(raw["Q_g"], dtype=np.float64).reshape(-1),
            ]
        )
        e = np.column_stack(
            [
                np.asarray(raw["I_e"], dtype=np.float64).reshape(-1),
                np.asarray(raw["Q_e"], dtype=np.float64).reshape(-1),
            ]
        )
        if g.shape != (50000, 2) or e.shape != (50000, 2):
            raise RuntimeError(f"Schema mismatch in {path}: {g.shape}, {e.shape}")
        if not np.isfinite(g).all() or not np.isfinite(e).all():
            raise RuntimeError(f"Non-finite values in {path}")
        out[condition] = {0: g, 1: e}
    return out


def stack(
    data: dict[int, dict[int, np.ndarray]], conditions: list[int], label: int
) -> np.ndarray:
    return np.vstack([data[condition][label] for condition in conditions])


def pooled_covariance(x0: np.ndarray, x1: np.ndarray) -> np.ndarray:
    c0 = x0 - x0.mean(axis=0)
    c1 = x1 - x1.mean(axis=0)
    return (c0.T @ c0 + c1.T @ c1) / (len(x0) + len(x1) - 2)


def balanced_accuracy(y: np.ndarray, pred: np.ndarray) -> float:
    return float(
        0.5 * ((pred[y == 0] == 0).mean() + (pred[y == 1] == 1).mean())
    )


def fit_geometry(x0: np.ndarray, x1: np.ndarray) -> dict[str, np.ndarray | float]:
    m0 = x0.mean(axis=0)
    m1 = x1.mean(axis=0)
    midpoint = 0.5 * (m0 + m1)
    covariance = pooled_covariance(x0, x1)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    if eigenvalues.min() <= eigenvalues.max() * RCOND:
        raise RuntimeError("INCONCLUSIVE: degenerate two-cut covariance")
    whitener = (
        eigenvectors
        @ np.diag(1.0 / np.sqrt(eigenvalues))
        @ eigenvectors.T
    )
    whitened_difference = (m1 - m0) @ whitener
    magnitude = float(np.linalg.norm(whitened_difference))
    if magnitude <= 1e-15:
        raise RuntimeError("INCONCLUSIVE: zero training centroid difference")
    phase_a = whitened_difference / magnitude
    phase_b = np.array([-phase_a[1], phase_a[0]], dtype=np.float64)

    training_tangent_residual = float(abs(whitened_difference @ phase_b))
    raw_weight = np.linalg.solve(covariance, m1 - m0)
    return {
        "m0": m0,
        "m1": m1,
        "midpoint": midpoint,
        "covariance": covariance,
        "whitener": whitener,
        "phase_a": phase_a,
        "phase_b": phase_b,
        "raw_weight": raw_weight,
        "training_tangent_residual": training_tangent_residual,
    }


def whitened(
    geometry: dict[str, np.ndarray | float], x: np.ndarray
) -> np.ndarray:
    return (x - geometry["midpoint"]) @ geometry["whitener"]


def main() -> None:
    protocol_hash = verify_freeze()
    data = load_data()
    fold_rows: list[dict[str, float | int]] = []
    sweep_rows: list[dict[str, float | int]] = []
    total_disagreements = 0
    total_reversal_disagreements = 0
    max_training_tangent_residual = 0.0

    for target_condition in CONDITIONS:
        training_conditions = [
            condition for condition in CONDITIONS if condition != target_condition
        ]
        x0_train = stack(data, training_conditions, 0)
        x1_train = stack(data, training_conditions, 1)
        geometry = fit_geometry(x0_train, x1_train)

        x0_target = data[target_condition][0]
        x1_target = data[target_condition][1]
        x_target = np.vstack([x0_target, x1_target])
        y_target = np.concatenate(
            [
                np.zeros(len(x0_target), dtype=np.int8),
                np.ones(len(x1_target), dtype=np.int8),
            ]
        )
        z_target = whitened(geometry, x_target)
        score_a = z_target @ geometry["phase_a"]
        score_b = z_target @ geometry["phase_b"]
        pred_a = (score_a >= 0).astype(np.int8)
        pred_b = (score_b >= 0).astype(np.int8)

        raw_score = (x_target - geometry["midpoint"]) @ geometry["raw_weight"]
        raw_pred = (raw_score >= 0).astype(np.int8)
        disagreements = int(np.sum(pred_a != raw_pred))
        total_disagreements += disagreements

        reversed_score = (-z_target) @ (-geometry["phase_a"])
        reversed_pred = (reversed_score >= 0).astype(np.int8)
        reversal_disagreements = int(np.sum(pred_a != reversed_pred))
        total_reversal_disagreements += reversal_disagreements

        target_difference = (
            x1_target.mean(axis=0) - x0_target.mean(axis=0)
        ) @ geometry["whitener"]
        d_a = float(target_difference @ geometry["phase_a"])
        d_b = float(target_difference @ geometry["phase_b"])
        separation_total = d_a * d_a + d_b * d_b
        phase_a_share = d_a * d_a / separation_total if separation_total else 0.0
        angle_degrees = math.degrees(math.atan2(d_b, d_a))

        sweep_best_ba = -math.inf
        sweep_best_angle = -1
        for angle in range(180):
            radians = math.radians(angle)
            axis = (
                math.cos(radians) * geometry["phase_a"]
                + math.sin(radians) * geometry["phase_b"]
            )
            score = z_target @ axis
            pred = (score >= 0).astype(np.int8)
            ba = balanced_accuracy(y_target, pred)
            sweep_rows.append(
                {
                    "held_out_condition_hz": target_condition,
                    "angle_from_phase_a_degrees": angle,
                    "balanced_accuracy": ba,
                }
            )
            if ba > sweep_best_ba:
                sweep_best_ba = ba
                sweep_best_angle = angle

        tangent_residual = float(geometry["training_tangent_residual"])
        max_training_tangent_residual = max(
            max_training_tangent_residual, tangent_residual
        )
        fold_rows.append(
            {
                "held_out_condition_hz": target_condition,
                "phase_a_ba": balanced_accuracy(y_target, pred_a),
                "phase_b_control_ba": balanced_accuracy(y_target, pred_b),
                "raw_iq_lda_ba": balanced_accuracy(y_target, raw_pred),
                "phase_a_raw_disagreements": disagreements,
                "pole_reversal_disagreements": reversal_disagreements,
                "target_d_phase_a": d_a,
                "target_d_phase_b": d_b,
                "phase_a_separation_share": phase_a_share,
                "target_separation_angle_degrees": angle_degrees,
                "best_sweep_angle_degrees": sweep_best_angle,
                "best_sweep_ba": sweep_best_ba,
                "training_tangent_residual": tangent_residual,
                "phase_a_i_component": float(geometry["phase_a"][0]),
                "phase_a_q_component": float(geometry["phase_a"][1]),
            }
        )

    with FOLDS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fold_rows[0]))
        writer.writeheader()
        writer.writerows(fold_rows)

    with SWEEP_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(sweep_rows[0]))
        writer.writeheader()
        writer.writerows(sweep_rows)

    overall_phase_a_ba = float(np.mean([row["phase_a_ba"] for row in fold_rows]))
    overall_phase_b_ba = float(
        np.mean([row["phase_b_control_ba"] for row in fold_rows])
    )
    overall_raw_ba = float(np.mean([row["raw_iq_lda_ba"] for row in fold_rows]))
    mean_share = float(
        np.mean([row["phase_a_separation_share"] for row in fold_rows])
    )
    worst_share = float(
        np.min([row["phase_a_separation_share"] for row in fold_rows])
    )
    gates = {
        "C1_phase_a_equals_raw_lda": {
            "value": total_disagreements,
            "threshold": 0,
            "pass": total_disagreements == 0,
        },
        "C2_phase_a_ba_at_least_0p80": {
            "value": overall_phase_a_ba,
            "threshold": 0.80,
            "pass": overall_phase_a_ba >= 0.80,
        },
        "C3_phase_b_control_between_0p40_and_0p60": {
            "value": overall_phase_b_ba,
            "lower": 0.40,
            "upper": 0.60,
            "pass": 0.40 <= overall_phase_b_ba <= 0.60,
        },
        "C4_mean_phase_a_share_at_least_0p90": {
            "value": mean_share,
            "threshold": 0.90,
            "pass": mean_share >= 0.90,
        },
        "C5_worst_phase_a_share_at_least_0p75": {
            "value": worst_share,
            "threshold": 0.75,
            "pass": worst_share >= 0.75,
        },
        "C6_training_tangent_residual_at_most_1e_12": {
            "value": max_training_tangent_residual,
            "threshold": 1e-12,
            "pass": max_training_tangent_residual <= 1e-12,
        },
        "C7_pole_reversal_invariant": {
            "value": total_reversal_disagreements,
            "threshold": 0,
            "pass": total_reversal_disagreements == 0,
        },
    }
    gates_passed = sum(int(gate["pass"]) for gate in gates.values())
    verdict = "CALIBRATED" if gates_passed == len(gates) else "NOT CALIBRATED"
    results = {
        "protocol_id": "Q3-RIDGE-NORMAL-CUT-v1",
        "evidence_class": "post-hoc known-source calibration",
        "verdict": verdict,
        "gates_passed": gates_passed,
        "gates_total": len(gates),
        "protocol_sha256": protocol_hash,
        "source": {
            "doi": "10.5281/zenodo.14033026",
            "conditions_hz": list(CONDITIONS),
            "shots_per_class_condition": 50000,
        },
        "overall": {
            "phase_a_ba": overall_phase_a_ba,
            "phase_b_control_ba": overall_phase_b_ba,
            "raw_iq_lda_ba": overall_raw_ba,
            "phase_a_raw_disagreements": total_disagreements,
            "pole_reversal_disagreements": total_reversal_disagreements,
            "mean_phase_a_separation_share": mean_share,
            "worst_phase_a_separation_share": worst_share,
            "max_training_tangent_residual": max_training_tangent_residual,
        },
        "gates": gates,
        "folds": fold_rows,
    }
    RESULTS_JSON.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(results["overall"], indent=2))
    print(f"{verdict}: {gates_passed}/{len(gates)} calibration gates")


if __name__ == "__main__":
    main()

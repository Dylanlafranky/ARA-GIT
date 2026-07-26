"""Independent validator for Q25.

This file deliberately does not import the primary Q25 runner.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE_DIR = HERE / "public_data" / "q25_atomic_bell"
PROTOCOL = HERE / "Q25_ARA9_BLIND_MISSING_CUT_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q25_ARA9_BLIND_MISSING_CUT_PROTOCOL_v1_FROZEN.sha256"
PREDICTIONS_JSON = HERE / "Q25_ARA9_BLIND_MISSING_CUT_PREDICTIONS.json"
PREDICTIONS_SHA = HERE / "Q25_ARA9_BLIND_MISSING_CUT_PREDICTIONS.sha256"
PREDICTIONS_CSV = HERE / "Q25_ARA9_BLIND_MISSING_CUT_PREDICTIONS.csv"
RESULTS_JSON = HERE / "Q25_ARA9_BLIND_MISSING_CUT_RESULTS.json"
VALIDATION_JSON = HERE / "Q25_ARA9_BLIND_MISSING_CUT_VALIDATION.json"

AXES = "XYZ"
GRID = np.round(np.arange(-1.25, 1.2500001, 0.0005), 10)
I2 = np.eye(2, dtype=np.complex128)
PAULI = [
    np.array([[0, 1], [1, 0]], dtype=np.complex128),
    np.array([[0, -1j], [1j, 0]], dtype=np.complex128),
    np.array([[1, 0], [0, -1]], dtype=np.complex128),
]

SOURCES = {
    "Fig3a-mixed-input": ("primary", "Fig3a_dm.csv", "6d9c796a2fe5a1e28bf421ddf3854794", "computational"),
    "Fig3b-AA": ("primary", "Fig3b_dm_AA.csv", "fabd72f98052a53cddd230f5f43dcbb7", "computational"),
    "Fig3b-AD": ("primary", "Fig3b_dm_AD.csv", "098362b0cc4ea2a20c952f0f644ed3b2", "computational"),
    "Fig3b-DA": ("primary", "Fig3b_dm_DA.csv", "9b6f161cc046b92e614e7962c47904ff", "computational"),
    "Fig3b-DD": ("primary", "Fig3b_dm_DD.csv", "98b2c5070cee080eb10dc4ab413acb67", "computational"),
    "Fig4-AA": ("secondary", "figure4_dm_AA.csv", "a760fd823f7ca7413013e1edaf2a2537", "bell"),
    "Fig4-AD": ("secondary", "figure4_dm_AD.csv", "231ee28c4b140bfd12cdd85239160608", "bell"),
    "Fig4-DA": ("secondary", "figure4_dm_DA.csv", "c37febe660af215d25d5e64a68849619", "bell"),
    "Fig4-DD": ("secondary", "figure4_dm_DD.csv", "77266fe4df3be1c2792cfaa75881772c", "bell"),
}


def digest(path: Path, algorithm: str = "sha256") -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_matrix(path: Path, basis: str) -> tuple[np.ndarray, dict[str, float]]:
    rows = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            rows.append(
                [
                    complex(token.strip().strip("()").replace(" ", ""))
                    for token in line.split(",")
                ]
            )
    raw = np.asarray(rows, dtype=np.complex128)
    hermitian_residual = float(np.max(np.abs(raw - raw.conj().T)))
    matrix = (raw + raw.conj().T) / 2
    trace_before = np.trace(matrix)
    matrix = matrix / trace_before
    if basis == "bell":
        r = 1 / math.sqrt(2)
        u = np.array(
            [[r, r, 0, 0], [0, 0, r, r], [0, 0, r, -r], [r, -r, 0, 0]],
            dtype=np.complex128,
        )
        matrix = u @ matrix @ u.conj().T
        matrix = (matrix + matrix.conj().T) / 2
    quality = {
        "hermitian": hermitian_residual,
        "trace_residual": float(abs(np.trace(matrix) - 1)),
        "minimum_eigenvalue": float(np.linalg.eigvalsh(matrix)[0]),
    }
    return matrix, quality


def decompose(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    a = np.array([np.trace(matrix @ np.kron(p, I2)).real for p in PAULI])
    b = np.array([np.trace(matrix @ np.kron(I2, p)).real for p in PAULI])
    t = np.array(
        [
            [
                np.trace(matrix @ np.kron(PAULI[i], PAULI[j])).real
                for j in range(3)
            ]
            for i in range(3)
        ]
    )
    return a, b, t, t - np.outer(a, b)


def pauli_matrix(a: np.ndarray, b: np.ndarray, t: np.ndarray) -> np.ndarray:
    rho = np.kron(I2, I2)
    for i in range(3):
        rho += a[i] * np.kron(PAULI[i], I2)
        rho += b[i] * np.kron(I2, PAULI[i])
    for i in range(3):
        for j in range(3):
            rho += t[i, j] * np.kron(PAULI[i], PAULI[j])
    return rho / 4


def ara_prediction(c: np.ndarray, hidden_i: int, hidden_j: int) -> float:
    matrices = np.repeat(c[None, :, :], len(GRID), axis=0)
    matrices[:, hidden_i, hidden_j] = GRID
    right = np.einsum("nki,nkj->nij", matrices, matrices)
    left = np.einsum("nik,njk->nij", matrices, matrices)
    identity = np.eye(3)
    lr = np.trace(right, axis1=1, axis2=2) / 3
    ll = np.trace(left, axis1=1, axis2=2) / 3
    loss = np.sum((right - lr[:, None, None] * identity) ** 2, axis=(1, 2))
    loss += np.sum((left - ll[:, None, None] * identity) ** 2, axis=(1, 2))
    loss += 100 * np.maximum(np.linalg.det(matrices), 0) ** 2
    minimum = float(np.min(loss))
    candidates = np.flatnonzero(np.isclose(loss, minimum, atol=1e-14, rtol=0))
    selected = min(candidates, key=lambda k: (abs(float(GRID[k])), float(GRID[k])))
    return float(GRID[selected])


def physical_prediction(
    a: np.ndarray, b: np.ndarray, t: np.ndarray, hidden_i: int, hidden_j: int
) -> float | None:
    known = t.copy()
    known[hidden_i, hidden_j] = 0
    base = pauli_matrix(a, b, known)
    operator = np.kron(PAULI[hidden_i], PAULI[hidden_j]) / 4
    joint_candidates = GRID + a[hidden_i] * b[hidden_j]
    matrices = base[None, :, :] + joint_candidates[:, None, None] * operator
    feasible = np.linalg.eigvalsh(matrices)[:, 0] >= -1e-8
    if not np.any(feasible):
        return None
    return float(np.mean(GRID[feasible]))


def classify(value: float) -> str:
    if abs(value) <= 0.10:
        return "quiet"
    return "positive-pole" if value > 0 else "negative-pole"


def summarize(rows: list[dict[str, Any]], field: str) -> dict[str, float | int]:
    valid = [row for row in rows if row[field] is not None]
    prediction = np.array([float(row[field]) for row in valid])
    target = np.array([float(row["target_connected"]) for row in valid])
    error = np.abs(prediction - target)
    correlation = (
        float(np.corrcoef(prediction, target)[0, 1])
        if np.std(prediction) > 1e-15 and np.std(target) > 1e-15
        else 0.0
    )
    return {
        "n": len(valid),
        "mae": float(np.mean(error)),
        "median_absolute_error": float(np.median(error)),
        "rmse": float(np.sqrt(np.mean((prediction - target) ** 2))),
        "fraction_within_0p10": float(np.mean(error <= 0.10)),
        "pearson": correlation,
        "pole_quiet_accuracy": float(
            np.mean([classify(p) == classify(t) for p, t in zip(prediction, target)])
        ),
    }


def bootstrap_probability(
    rows: list[dict[str, Any]], control_field: str, seed: int
) -> float:
    rng = np.random.default_rng(seed)
    entities = sorted({row["entity"] for row in rows})
    grouped = {entity: [row for row in rows if row["entity"] == entity] for entity in entities}
    successes = 0
    for _ in range(10_000):
        sampled = rng.choice(entities, size=len(entities), replace=True)
        sample = [row for entity in sampled for row in grouped[entity]]
        ara_error = np.mean(
            [
                abs(float(row["ara_prediction_connected"]) - float(row["target_connected"]))
                for row in sample
            ]
        )
        control_values = [row for row in sample if row[control_field] is not None]
        control_error = np.mean(
            [
                abs(float(row[control_field]) - float(row["target_connected"]))
                for row in control_values
            ]
        )
        successes += ara_error < control_error
    return successes / 10_000


def close(a: float | None, b: float | None, tolerance: float = 1e-10) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return abs(float(a) - float(b)) <= tolerance


def main() -> None:
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = None) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    protocol_expected = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    check("protocol_hash", digest(PROTOCOL) == protocol_expected)
    prediction_expected = PREDICTIONS_SHA.read_text(encoding="utf-8").split()[0]
    check("prediction_hash", digest(PREDICTIONS_JSON) == prediction_expected)

    result = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    csv_rows = {
        row["case_id"]: row
        for row in csv.DictReader(PREDICTIONS_CSV.open(encoding="utf-8"))
    }
    recomputed: list[dict[str, Any]] = []
    qualities: dict[str, dict[str, float]] = {}
    entity_metrics: dict[str, dict[str, Any]] = {}

    for entity, (group, filename, expected_md5, basis) in SOURCES.items():
        path = SOURCE_DIR / filename
        check(f"md5::{entity}", digest(path, "md5") == expected_md5)
        matrix, quality = parse_matrix(path, basis)
        qualities[entity] = quality
        a, b, joint, connected = decompose(matrix)
        singular = np.linalg.svd(connected, compute_uv=False)
        determinant = float(np.linalg.det(connected))
        entity_metrics[entity] = {
            "closure_strength": float(abs(determinant) ** (1 / 3)),
            "retained": int(np.sum(singular >= 0.5)),
        }
        for i in range(3):
            for j in range(3):
                case_id = f"{group}::{entity}::{AXES[i]}{AXES[j]}"
                target = float(connected[i, j])
                c_hidden = connected.copy()
                c_hidden[i, j] = 0
                ara = ara_prediction(c_hidden, i, j)
                known_values = np.delete(connected.ravel(), i * 3 + j)
                physical = physical_prediction(a, b, joint, i, j)
                row = {
                    "case_id": case_id,
                    "group": group,
                    "entity": entity,
                    "target_connected": target,
                    "ara_prediction_connected": ara,
                    "ridge_prediction_connected": 0.0,
                    "mean8_prediction_connected": float(np.mean(known_values)),
                    "physical_midpoint_prediction_connected": physical,
                }
                recomputed.append(row)
                saved = csv_rows[case_id]
                check(f"target::{case_id}", close(target, float(saved["target_connected"])))
                check(f"ara::{case_id}", close(ara, float(saved["ara_prediction_connected"])))
                check(f"ridge::{case_id}", close(0.0, float(saved["ridge_prediction_connected"])))
                check(f"mean8::{case_id}", close(row["mean8_prediction_connected"], float(saved["mean8_prediction_connected"])))
                saved_physical = (
                    None
                    if saved["physical_midpoint_prediction_connected"] == ""
                    else float(saved["physical_midpoint_prediction_connected"])
                )
                check(f"physical::{case_id}", close(physical, saved_physical))

    fields = {
        "ara": "ara_prediction_connected",
        "ridge": "ridge_prediction_connected",
        "mean8": "mean8_prediction_connected",
        "physical_midpoint": "physical_midpoint_prediction_connected",
    }
    summaries: dict[str, dict[str, dict[str, Any]]] = {}
    for group in ["primary", "secondary"]:
        group_rows = [row for row in recomputed if row["group"] == group]
        summaries[group] = {model: summarize(group_rows, field) for model, field in fields.items()}
        for model, values in summaries[group].items():
            for key, value in values.items():
                check(
                    f"summary::{group}::{model}::{key}",
                    close(value, result["summaries"][group][model][key]),
                )

    primary_rows = [row for row in recomputed if row["group"] == "primary"]
    p_ridge = bootstrap_probability(primary_rows, "ridge_prediction_connected", 2026072625)
    p_physical = bootstrap_probability(
        primary_rows, "physical_midpoint_prediction_connected", 2026072627
    )
    check(
        "bootstrap_ridge_probability",
        close(p_ridge, result["cluster_bootstrap"]["ridge"]["probability_ara_lower_mae"]),
    )
    check(
        "bootstrap_physical_probability",
        close(
            p_physical,
            result["cluster_bootstrap"]["physical_midpoint"]["probability_ara_lower_mae"],
        ),
    )

    input_metric = entity_metrics["Fig3a-mixed-input"]
    outputs = [entity_metrics[f"Fig3b-{label}"] for label in ["AA", "AD", "DA", "DD"]]
    input_h = input_metric["closure_strength"]
    output_h = float(np.mean([item["closure_strength"] for item in outputs]))
    transition_gates = {
        "T1_input_trough": input_metric["retained"] == 0 and input_h <= 0.20,
        "T2_all_outputs_crest": all(
            item["retained"] >= 2 and item["closure_strength"] >= 0.40
            for item in outputs
        ),
        "T3_closure_gain": output_h - input_h >= 0.35,
    }
    for name, value in transition_gates.items():
        check(
            f"transition::{name}",
            value == result["larger_wave_transition_probe"]["gates"][name],
        )

    primary = summaries["primary"]
    source_md5_ok = all(
        digest(SOURCE_DIR / filename, "md5") == md5
        for _entity, (_group, filename, md5, _basis) in SOURCES.items()
    )
    quality_ok = all(
        qualities[entity]["hermitian"] <= 1e-8
        and qualities[entity]["trace_residual"] <= 1e-8
        and qualities[entity]["minimum_eigenvalue"] >= -1e-6
        for entity in SOURCES
        if SOURCES[entity][0] == "primary"
    )
    gates = {
        "S1_source_md5": source_md5_ok,
        "S2_primary_matrix_quality": quality_ok,
        "S3_exactly_45_predictions_frozen": len(primary_rows) == 45,
        "S4_ara_mae_below_ridge": primary["ara"]["mae"] < primary["ridge"]["mae"],
        "S5_ara_mae_below_mean8": primary["ara"]["mae"] < primary["mean8"]["mae"],
        "S6_ara_mae_below_physical_midpoint": primary["ara"]["mae"] < primary["physical_midpoint"]["mae"],
        "S7_ara_median_at_most_every_control": all(
            primary["ara"]["median_absolute_error"] <= primary[c]["median_absolute_error"]
            for c in ["ridge", "mean8", "physical_midpoint"]
        ),
        "S8_ara_classification_above_every_control": all(
            primary["ara"]["pole_quiet_accuracy"] > primary[c]["pole_quiet_accuracy"]
            for c in ["ridge", "mean8", "physical_midpoint"]
        ),
        "S9_ara_mae_at_most_0p15": primary["ara"]["mae"] <= 0.15,
        "S10_ara_pearson_at_least_0p75": primary["ara"]["pearson"] >= 0.75,
        "S11_bootstrap_below_ridge_at_least_0p95": p_ridge >= 0.95,
        "S12_bootstrap_below_physical_at_least_0p90": p_physical >= 0.90,
    }
    for name, value in gates.items():
        check(f"gate::{name}", value == result["gates"][name])

    expected_verdict = "SUPPORTED" if all(gates.values()) else "NOT SUPPORTED"
    check("verdict", expected_verdict == result["verdict"])
    passed = sum(item["pass"] for item in checks)
    validation = {
        "validator": Path(__file__).name,
        "independent_of_primary_runner": True,
        "checks_passed": passed,
        "checks_total": len(checks),
        "verdict": "PASS" if passed == len(checks) else "FAIL",
        "q25_verdict_reproduced": expected_verdict,
        "failed_checks": [item for item in checks if not item["pass"]],
    }
    VALIDATION_JSON.write_text(
        json.dumps(validation, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"Q25 independent validation: {validation['verdict']} — "
        f"{passed}/{len(checks)} checks"
    )


if __name__ == "__main__":
    main()

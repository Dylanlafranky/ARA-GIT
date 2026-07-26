"""Staged Q25 ARA^9 missing-cut reconstruction test.

Run in this order:

    python q25_ara9_blind_missing_cut_test.py prepare
    python q25_ara9_blind_missing_cut_test.py predict
    python q25_ara9_blind_missing_cut_test.py reveal

The ``predict`` stage reads only eight-cell geometry packets. The ``reveal``
stage refuses to score unless the prediction packet has already been hashed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE_DIR = HERE / "public_data" / "q25_atomic_bell"
PROTOCOL = HERE / "Q25_ARA9_BLIND_MISSING_CUT_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q25_ARA9_BLIND_MISSING_CUT_PROTOCOL_v1_FROZEN.sha256"

GEOMETRY_JSON = SOURCE_DIR / "Q25_GEOMETRY_ONLY.json"
TARGETS_JSON = SOURCE_DIR / "Q25_TARGETS_SEALED.json"
PREDICTIONS_JSON = HERE / "Q25_ARA9_BLIND_MISSING_CUT_PREDICTIONS.json"
PREDICTIONS_SHA = HERE / "Q25_ARA9_BLIND_MISSING_CUT_PREDICTIONS.sha256"
PREDICTIONS_CSV = HERE / "Q25_ARA9_BLIND_MISSING_CUT_PREDICTIONS.csv"
METRICS_CSV = HERE / "Q25_ARA9_BLIND_MISSING_CUT_METRICS.csv"
RESULTS_JSON = HERE / "Q25_ARA9_BLIND_MISSING_CUT_RESULTS.json"
FIGURE_SVG = HERE / "Q25_ARA9_BLIND_MISSING_CUT_GEOMETRY.svg"
FIGURE_PNG = HERE / "Q25_ARA9_BLIND_MISSING_CUT_GEOMETRY.png"

AXES = "XYZ"
SLOTS = [a + b for a in AXES for b in AXES]
GRID = np.round(np.arange(-1.25, 1.2500001, 0.0005), 10)
BOOTSTRAP_REPS = 10_000
BOOTSTRAP_SEED = 2026072625

PRIMARY_FILES = {
    "Fig3a-mixed-input": (
        "Fig3a_dm.csv",
        "6d9c796a2fe5a1e28bf421ddf3854794",
        "computational",
    ),
    "Fig3b-AA": (
        "Fig3b_dm_AA.csv",
        "fabd72f98052a53cddd230f5f43dcbb7",
        "computational",
    ),
    "Fig3b-AD": (
        "Fig3b_dm_AD.csv",
        "098362b0cc4ea2a20c952f0f644ed3b2",
        "computational",
    ),
    "Fig3b-DA": (
        "Fig3b_dm_DA.csv",
        "9b6f161cc046b92e614e7962c47904ff",
        "computational",
    ),
    "Fig3b-DD": (
        "Fig3b_dm_DD.csv",
        "98b2c5070cee080eb10dc4ab413acb67",
        "computational",
    ),
}

SECONDARY_FILES = {
    "Fig4-AA": (
        "figure4_dm_AA.csv",
        "a760fd823f7ca7413013e1edaf2a2537",
        "bell",
    ),
    "Fig4-AD": (
        "figure4_dm_AD.csv",
        "231ee28c4b140bfd12cdd85239160608",
        "bell",
    ),
    "Fig4-DA": (
        "figure4_dm_DA.csv",
        "c37febe660af215d25d5e64a68849619",
        "bell",
    ),
    "Fig4-DD": (
        "figure4_dm_DD.csv",
        "77266fe4df3be1c2792cfaa75881772c",
        "bell",
    ),
}

I2 = np.eye(2, dtype=np.complex128)
PAULI = [
    np.array([[0, 1], [1, 0]], dtype=np.complex128),
    np.array([[0, -1j], [1j, 0]], dtype=np.complex128),
    np.array([[1, 0], [0, -1]], dtype=np.complex128),
]


def digest(path: Path, algorithm: str = "sha256") -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_protocol() -> str:
    expected = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    actual = digest(PROTOCOL)
    if actual != expected:
        raise RuntimeError(f"Protocol hash mismatch: {actual} != {expected}")
    return actual


def clean_complex_token(token: str) -> complex:
    return complex(token.strip().strip("()").replace(" ", ""))


def read_complex_matrix(path: Path, basis: str) -> tuple[np.ndarray, dict[str, float]]:
    rows: list[list[complex]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            if not line.strip():
                continue
            rows.append([clean_complex_token(token) for token in line.split(",")])
    raw = np.asarray(rows, dtype=np.complex128)
    if raw.shape != (4, 4):
        raise RuntimeError(f"{path.name}: expected 4x4 matrix, got {raw.shape}")

    hermitian_residual = float(np.max(np.abs(raw - raw.conj().T)))
    matrix = (raw + raw.conj().T) / 2
    trace_before = np.trace(matrix)
    if abs(trace_before) < 1e-12:
        raise RuntimeError(f"{path.name}: zero trace")
    matrix = matrix / trace_before

    if basis == "bell":
        root2 = math.sqrt(2)
        transform = np.array(
            [
                [1 / root2, 1 / root2, 0, 0],
                [0, 0, 1 / root2, 1 / root2],
                [0, 0, 1 / root2, -1 / root2],
                [1 / root2, -1 / root2, 0, 0],
            ],
            dtype=np.complex128,
        )
        matrix = transform @ matrix @ transform.conj().T
        matrix = (matrix + matrix.conj().T) / 2

    imaginary_trace = float(abs(np.trace(matrix).imag))
    trace_residual = float(abs(np.trace(matrix).real - 1.0))
    eigenvalues = np.linalg.eigvalsh(matrix)
    quality = {
        "hermitian_residual_before_symmetrization": hermitian_residual,
        "trace_before_normalization_real": float(trace_before.real),
        "trace_before_normalization_imag": float(trace_before.imag),
        "trace_residual_after_normalization": trace_residual,
        "imaginary_trace_after_normalization": imaginary_trace,
        "minimum_eigenvalue": float(eigenvalues[0]),
        "maximum_eigenvalue": float(eigenvalues[-1]),
    }
    return matrix, quality


def pauli_decomposition(
    matrix: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    a = np.array(
        [np.trace(matrix @ np.kron(p, I2)).real for p in PAULI],
        dtype=np.float64,
    )
    b = np.array(
        [np.trace(matrix @ np.kron(I2, p)).real for p in PAULI],
        dtype=np.float64,
    )
    joint = np.array(
        [
            [
                np.trace(matrix @ np.kron(PAULI[i], PAULI[j])).real
                for j in range(3)
            ]
            for i in range(3)
        ],
        dtype=np.float64,
    )
    connected = joint - np.outer(a, b)
    return a, b, joint, connected


def matrix_from_pauli(a: np.ndarray, b: np.ndarray, joint: np.ndarray) -> np.ndarray:
    matrix = np.kron(I2, I2)
    for i in range(3):
        matrix = matrix + a[i] * np.kron(PAULI[i], I2)
        matrix = matrix + b[i] * np.kron(I2, PAULI[i])
    for i in range(3):
        for j in range(3):
            matrix = matrix + joint[i, j] * np.kron(PAULI[i], PAULI[j])
    return matrix / 4


def serial_matrix(matrix: np.ndarray, hidden: tuple[int, int] | None = None) -> list:
    output: list[list[float | None]] = []
    for i in range(3):
        row: list[float | None] = []
        for j in range(3):
            row.append(None if hidden == (i, j) else float(matrix[i, j]))
        output.append(row)
    return output


def prepare() -> None:
    protocol_hash = verify_protocol()
    geometry_cases: list[dict[str, Any]] = []
    target_cases: list[dict[str, Any]] = []
    source_quality: dict[str, Any] = {}
    source_hashes: dict[str, str] = {}

    partitions = [
        ("primary", PRIMARY_FILES),
        ("secondary", SECONDARY_FILES),
    ]
    for group, source_files in partitions:
        for entity, (filename, expected_md5, basis) in source_files.items():
            path = SOURCE_DIR / filename
            actual_md5 = digest(path, "md5")
            if actual_md5 != expected_md5:
                raise RuntimeError(
                    f"{filename}: checksum mismatch {actual_md5} != {expected_md5}"
                )
            source_hashes[filename] = actual_md5
            matrix, quality = read_complex_matrix(path, basis)
            source_quality[entity] = {
                **quality,
                "filename": filename,
                "source_basis": basis,
            }
            a, b, joint, connected = pauli_decomposition(matrix)
            for i, axis_a in enumerate(AXES):
                for j, axis_b in enumerate(AXES):
                    slot = axis_a + axis_b
                    case_id = f"{group}::{entity}::{slot}"
                    geometry_cases.append(
                        {
                            "case_id": case_id,
                            "group": group,
                            "entity": entity,
                            "hidden_slot": slot,
                            "hidden_i": i,
                            "hidden_j": j,
                            "a": a.tolist(),
                            "b": b.tolist(),
                            "known_joint": serial_matrix(joint, (i, j)),
                            "known_connected": serial_matrix(connected, (i, j)),
                        }
                    )
                    target_cases.append(
                        {
                            "case_id": case_id,
                            "target_joint": float(joint[i, j]),
                            "target_connected": float(connected[i, j]),
                            "target_ara9": float(1 - connected[i, j]),
                        }
                    )

    geometry_packet = {
        "protocol_sha256": protocol_hash,
        "source_hashes_md5": source_hashes,
        "source_quality": source_quality,
        "case_count": len(geometry_cases),
        "cases": geometry_cases,
    }
    target_packet = {
        "protocol_sha256": protocol_hash,
        "case_count": len(target_cases),
        "cases": target_cases,
    }
    GEOMETRY_JSON.write_text(
        json.dumps(geometry_packet, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    TARGETS_JSON.write_text(
        json.dumps(target_packet, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Prepared {len(geometry_cases)} eight-cell geometry packets.")
    print(f"Geometry packet: {GEOMETRY_JSON}")
    print(f"Sealed target packet: {TARGETS_JSON}")
    print("No target values were displayed.")


def complete_known(values: list[list[float | None]], candidate: float) -> np.ndarray:
    matrix = np.empty((3, 3), dtype=np.float64)
    missing = 0
    for i in range(3):
        for j in range(3):
            value = values[i][j]
            if value is None:
                matrix[i, j] = candidate
                missing += 1
            else:
                matrix[i, j] = float(value)
    if missing != 1:
        raise RuntimeError(f"Expected one hidden cell, found {missing}")
    return matrix


def ara_sphere_predictions(known_connected: list[list[float | None]]) -> dict[str, float]:
    matrices = np.repeat(
        complete_known(known_connected, 0.0)[None, :, :],
        len(GRID),
        axis=0,
    )
    hidden_index = next(
        (i, j)
        for i in range(3)
        for j in range(3)
        if known_connected[i][j] is None
    )
    matrices[:, hidden_index[0], hidden_index[1]] = GRID

    right = np.einsum("nki,nkj->nij", matrices, matrices)
    left = np.einsum("nik,njk->nij", matrices, matrices)
    lambda_right = np.trace(right, axis1=1, axis2=2) / 3
    lambda_left = np.trace(left, axis1=1, axis2=2) / 3
    identity = np.eye(3)
    loss = np.sum(
        (right - lambda_right[:, None, None] * identity) ** 2,
        axis=(1, 2),
    )
    loss += np.sum(
        (left - lambda_left[:, None, None] * identity) ** 2,
        axis=(1, 2),
    )
    determinants = np.linalg.det(matrices)
    loss += 100 * np.maximum(determinants, 0) ** 2

    minimum = float(np.min(loss))
    tied = np.flatnonzero(np.isclose(loss, minimum, atol=1e-14, rtol=0))
    chosen_index = min(tied, key=lambda k: (abs(float(GRID[k])), float(GRID[k])))
    sorted_loss = np.sort(loss)
    return {
        "prediction": float(GRID[chosen_index]),
        "loss": float(loss[chosen_index]),
        "next_grid_loss": float(sorted_loss[1]),
        "determinant_at_prediction": float(determinants[chosen_index]),
    }


def physical_midpoint(
    a: np.ndarray,
    b: np.ndarray,
    known_joint: list[list[float | None]],
    hidden_i: int,
    hidden_j: int,
) -> dict[str, float | int | None]:
    joint_zero = complete_known(known_joint, 0.0)
    base = matrix_from_pauli(a, b, joint_zero)
    operator = np.kron(PAULI[hidden_i], PAULI[hidden_j]) / 4
    candidate_joint = GRID + a[hidden_i] * b[hidden_j]
    matrices = base[None, :, :] + candidate_joint[:, None, None] * operator
    minimum_eigenvalues = np.linalg.eigvalsh(matrices)[:, 0]
    feasible = minimum_eigenvalues >= -1e-8
    values = GRID[feasible]
    if not len(values):
        return {
            "prediction": None,
            "feasible_count": 0,
            "feasible_min": None,
            "feasible_max": None,
        }
    return {
        "prediction": float(np.mean(values)),
        "feasible_count": int(len(values)),
        "feasible_min": float(values[0]),
        "feasible_max": float(values[-1]),
    }


def predict() -> None:
    protocol_hash = verify_protocol()
    packet = json.loads(GEOMETRY_JSON.read_text(encoding="utf-8"))
    if packet["protocol_sha256"] != protocol_hash:
        raise RuntimeError("Geometry packet protocol hash mismatch")
    predictions: list[dict[str, Any]] = []
    for case in packet["cases"]:
        known = case["known_connected"]
        observed = [
            float(known[i][j])
            for i in range(3)
            for j in range(3)
            if known[i][j] is not None
        ]
        ara = ara_sphere_predictions(known)
        physics = physical_midpoint(
            np.asarray(case["a"], dtype=np.float64),
            np.asarray(case["b"], dtype=np.float64),
            case["known_joint"],
            int(case["hidden_i"]),
            int(case["hidden_j"]),
        )
        predictions.append(
            {
                "case_id": case["case_id"],
                "group": case["group"],
                "entity": case["entity"],
                "hidden_slot": case["hidden_slot"],
                "ara_prediction_connected": ara["prediction"],
                "ara_prediction_ara9": 1 - ara["prediction"],
                "ara_loss": ara["loss"],
                "ara_next_grid_loss": ara["next_grid_loss"],
                "ara_determinant_at_prediction": ara[
                    "determinant_at_prediction"
                ],
                "ridge_prediction_connected": 0.0,
                "mean8_prediction_connected": float(np.mean(observed)),
                "physical_midpoint_prediction_connected": physics["prediction"],
                "physical_feasible_count": physics["feasible_count"],
                "physical_feasible_min": physics["feasible_min"],
                "physical_feasible_max": physics["feasible_max"],
            }
        )

    output = {
        "protocol_sha256": protocol_hash,
        "geometry_sha256": digest(GEOMETRY_JSON),
        "case_count": len(predictions),
        "target_packet_read": False,
        "predictions": predictions,
    }
    PREDICTIONS_JSON.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    prediction_hash = digest(PREDICTIONS_JSON)
    PREDICTIONS_SHA.write_text(
        f"{prediction_hash} *{PREDICTIONS_JSON.name}\n",
        encoding="utf-8",
    )
    print(f"Frozen {len(predictions)} predictions without reading targets.")
    print(f"Prediction SHA-256: {prediction_hash}")


def classify(value: float) -> str:
    if abs(value) <= 0.10:
        return "quiet"
    return "positive-pole" if value > 0 else "negative-pole"


def pearson(prediction: np.ndarray, target: np.ndarray) -> float:
    if len(prediction) < 2:
        return float("nan")
    if np.std(prediction) < 1e-15 or np.std(target) < 1e-15:
        return 0.0
    return float(np.corrcoef(prediction, target)[0, 1])


def summarize_model(rows: list[dict[str, Any]], prediction_field: str) -> dict[str, Any]:
    eligible = [row for row in rows if row[prediction_field] is not None]
    prediction = np.array(
        [float(row[prediction_field]) for row in eligible], dtype=np.float64
    )
    target = np.array(
        [float(row["target_connected"]) for row in eligible], dtype=np.float64
    )
    error = np.abs(prediction - target)
    return {
        "n": len(eligible),
        "mae": float(np.mean(error)),
        "median_absolute_error": float(np.median(error)),
        "rmse": float(np.sqrt(np.mean((prediction - target) ** 2))),
        "fraction_within_0p10": float(np.mean(error <= 0.10)),
        "pearson": pearson(prediction, target),
        "pole_quiet_accuracy": float(
            np.mean([classify(p) == classify(t) for p, t in zip(prediction, target)])
        ),
    }


def cluster_bootstrap(
    rows: list[dict[str, Any]],
    model_field: str,
    control_field: str,
    seed: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    entities = sorted({row["entity"] for row in rows})
    grouped = {e: [row for row in rows if row["entity"] == e] for e in entities}
    differences = np.empty(BOOTSTRAP_REPS, dtype=np.float64)
    model_mae = np.empty(BOOTSTRAP_REPS, dtype=np.float64)
    control_mae = np.empty(BOOTSTRAP_REPS, dtype=np.float64)
    for repetition in range(BOOTSTRAP_REPS):
        sampled = rng.choice(entities, size=len(entities), replace=True)
        sample_rows = list(itertools.chain.from_iterable(grouped[e] for e in sampled))
        model_errors = [
            abs(float(row[model_field]) - float(row["target_connected"]))
            for row in sample_rows
            if row[model_field] is not None
        ]
        control_errors = [
            abs(float(row[control_field]) - float(row["target_connected"]))
            for row in sample_rows
            if row[control_field] is not None
        ]
        model_mae[repetition] = np.mean(model_errors)
        control_mae[repetition] = np.mean(control_errors)
        differences[repetition] = control_mae[repetition] - model_mae[repetition]
    return {
        "probability_ara_lower_mae": float(np.mean(differences > 0)),
        "ara_mae_95ci": np.quantile(model_mae, [0.025, 0.975]).tolist(),
        "control_mae_95ci": np.quantile(control_mae, [0.025, 0.975]).tolist(),
        "control_minus_ara_mae_95ci": np.quantile(
            differences, [0.025, 0.975]
        ).tolist(),
    }


def exact_sign_flip_pvalue(differences: np.ndarray) -> float | None:
    """Exact one-sided sign-flip p-value by meet-in-the-middle.

    Returns ``None`` for more than 46 records to avoid unreasonable memory.
    """

    n = len(differences)
    if n > 46:
        return None
    midpoint = n // 2

    def subset_sums(values: np.ndarray) -> np.ndarray:
        sums = np.array([0.0], dtype=np.float64)
        for value in values:
            sums = np.concatenate((sums, sums + value))
        return sums

    left = subset_sums(differences[:midpoint])
    right = np.sort(subset_sums(differences[midpoint:]))
    total = float(np.sum(differences))
    observed_signed_sum = total
    # Signed sum = 2 * subset_sum - total.
    required_subset_sum = (observed_signed_sum + total) / 2
    counts = 0
    for start in range(0, len(left), 250_000):
        block = left[start : start + 250_000]
        thresholds = required_subset_sum - block
        counts += int(np.sum(len(right) - np.searchsorted(right, thresholds, side="left")))
    return counts / (2**n)


def full_entity_metrics() -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    for group, files in [("primary", PRIMARY_FILES), ("secondary", SECONDARY_FILES)]:
        for entity, (filename, _md5, basis) in files.items():
            matrix, _quality = read_complex_matrix(SOURCE_DIR / filename, basis)
            a, b, joint, connected = pauli_decomposition(matrix)
            singular = np.linalg.svd(connected, compute_uv=False)
            determinant = float(np.linalg.det(connected))
            metrics[entity] = {
                "group": group,
                "a": a.tolist(),
                "b": b.tolist(),
                "joint": joint.tolist(),
                "connected": connected.tolist(),
                "ara9": (1 - connected).tolist(),
                "singular_values": singular.tolist(),
                "retained_directions_at_0p50": int(np.sum(singular >= 0.50)),
                "determinant": determinant,
                "closure_strength": float(abs(determinant) ** (1 / 3)),
                "directional_balance": (
                    float(singular[-1] / singular[0])
                    if singular[0] > 1e-12
                    else 0.0
                ),
            }
    return metrics


def write_prediction_csv(rows: list[dict[str, Any]]) -> None:
    fields = [
        "case_id",
        "group",
        "entity",
        "hidden_slot",
        "target_connected",
        "target_ara9",
        "ara_prediction_connected",
        "ara_prediction_ara9",
        "ridge_prediction_connected",
        "mean8_prediction_connected",
        "physical_midpoint_prediction_connected",
        "ara_absolute_error",
        "ridge_absolute_error",
        "mean8_absolute_error",
        "physical_midpoint_absolute_error",
        "ara_target_class",
        "ara_prediction_class",
    ]
    with PREDICTIONS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def write_metrics_csv(
    summaries: dict[str, dict[str, dict[str, Any]]],
    entity_metrics: dict[str, dict[str, Any]],
) -> None:
    rows: list[dict[str, Any]] = []
    for group, models in summaries.items():
        for model, values in models.items():
            rows.append({"record_type": "prediction", "group": group, "name": model, **values})
    for entity, values in entity_metrics.items():
        rows.append(
            {
                "record_type": "entity",
                "group": values["group"],
                "name": entity,
                "retained_directions": values["retained_directions_at_0p50"],
                "closure_strength": values["closure_strength"],
                "determinant": values["determinant"],
                "directional_balance": values["directional_balance"],
            }
        )
    fields = sorted({key for row in rows for key in row})
    with METRICS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def make_svg(
    rows: list[dict[str, Any]],
    summaries: dict[str, dict[str, dict[str, Any]]],
    entity_metrics: dict[str, dict[str, Any]],
) -> None:
    width, height = 1500, 1120
    colors = {
        "ara": "#4c78a8",
        "ridge": "#8a8f98",
        "mean8": "#f2a541",
        "physical": "#59a14f",
        "crest": "#df9f32",
        "trough": "#6baed6",
    }
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfcfe"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#172033}.title{font-size:34px;font-weight:700}.sub{font-size:18px;fill:#536176}.head{font-size:24px;font-weight:700}.label{font-size:16px}.small{font-size:13px;fill:#5d6878}</style>',
        '<text x="55" y="55" class="title">Q25 blind ARA⁹ missing-cut reconstruction</text>',
        '<text x="55" y="86" class="sub">Five external atomic-qubit density matrices · 45 hidden cuts · predictions frozen before reveal</text>',
    ]

    # Panel 1: primary predicted versus observed.
    x0, y0, size = 80, 155, 430
    parts += [
        f'<rect x="{x0-25}" y="{y0-45}" width="{size+80}" height="{size+95}" rx="16" fill="#fff" stroke="#d9e0ea"/>',
        f'<text x="{x0}" y="{y0-12}" class="head">ARA prediction versus hidden cut</text>',
    ]
    lo, hi = -1.05, 1.05
    def sx(value: float) -> float:
        return x0 + (value - lo) / (hi - lo) * size
    def sy(value: float) -> float:
        return y0 + size - (value - lo) / (hi - lo) * size
    parts += [
        f'<line x1="{sx(lo)}" y1="{sy(lo)}" x2="{sx(hi)}" y2="{sy(hi)}" stroke="#aab3c2" stroke-dasharray="6 5"/>',
        f'<line x1="{sx(0)}" y1="{y0}" x2="{sx(0)}" y2="{y0+size}" stroke="#e2e7ef"/>',
        f'<line x1="{x0}" y1="{sy(0)}" x2="{x0+size}" y2="{sy(0)}" stroke="#e2e7ef"/>',
    ]
    for row in [r for r in rows if r["group"] == "primary"]:
        parts.append(
            f'<circle cx="{sx(float(row["target_connected"])):.2f}" '
            f'cy="{sy(float(row["ara_prediction_connected"])):.2f}" r="5.5" '
            f'fill="{colors["ara"]}" fill-opacity="0.72"/>'
        )
    parts += [
        f'<text x="{x0+size/2-55}" y="{y0+size+35}" class="label">hidden connected cut</text>',
        f'<text transform="translate({x0-45},{y0+size/2+55}) rotate(-90)" class="label">ARA prediction</text>',
        f'<text x="{x0}" y="{y0+size+58}" class="small">Diagonal = exact reconstruction</text>',
    ]

    # Panel 2: MAE bars.
    bx, by, bw = 650, 155, 690
    parts += [
        f'<rect x="{bx-25}" y="{by-45}" width="{bw+60}" height="525" rx="16" fill="#fff" stroke="#d9e0ea"/>',
        f'<text x="{bx}" y="{by-12}" class="head">Primary mean absolute error</text>',
    ]
    models = [
        ("ARA⁹ closure", "ara", "ara"),
        ("physical midpoint", "physical_midpoint", "physical"),
        ("ridge", "ridge", "ridge"),
        ("eight-cell mean", "mean8", "mean8"),
    ]
    max_mae = max(summaries["primary"][key]["mae"] for _label, key, _color in models) * 1.12
    for idx, (label, key, color_key) in enumerate(models):
        value = summaries["primary"][key]["mae"]
        yy = by + 60 + idx * 91
        bar_width = value / max_mae * 480
        parts += [
            f'<text x="{bx}" y="{yy+26}" class="label">{label}</text>',
            f'<rect x="{bx+190}" y="{yy}" width="{bar_width:.1f}" height="38" rx="7" fill="{colors[color_key]}"/>',
            f'<text x="{bx+205+bar_width:.1f}" y="{yy+27}" class="label">{value:.4f}</text>',
        ]

    # Panel 3: transition closure.
    tx, ty = 80, 770
    parts += [
        f'<rect x="{tx-25}" y="{ty-55}" width="1260" height="315" rx="16" fill="#fff" stroke="#d9e0ea"/>',
        f'<text x="{tx}" y="{ty-20}" class="head">Declared Figure 3 transition: mixed input → Bell-conditioned outputs</text>',
    ]
    entities = ["Fig3a-mixed-input", "Fig3b-AA", "Fig3b-AD", "Fig3b-DA", "Fig3b-DD"]
    max_h = max(entity_metrics[e]["closure_strength"] for e in entities) * 1.15
    for idx, entity in enumerate(entities):
        value = entity_metrics[entity]["closure_strength"]
        retained = entity_metrics[entity]["retained_directions_at_0p50"]
        xx = tx + idx * 235
        bar_height = value / max_h * 170 if max_h else 0
        color = colors["trough"] if idx == 0 else colors["crest"]
        parts += [
            f'<rect x="{xx}" y="{ty+185-bar_height:.1f}" width="120" height="{bar_height:.1f}" rx="8" fill="{color}"/>',
            f'<text x="{xx}" y="{ty+215}" class="label">{entity.replace("Fig3", "")}</text>',
            f'<text x="{xx}" y="{ty+239}" class="small">h={value:.3f} · directions={retained}</text>',
        ]
    parts += [
        '<text x="55" y="1090" class="small">ARA⁹ closure prediction uses only the other eight connected cuts; established physical positivity is retained as a separate control.</text>',
        "</svg>",
    ]
    FIGURE_SVG.write_text("\n".join(parts) + "\n", encoding="utf-8")


def rasterize_summary_svg_fallback() -> None:
    """Create a compact PNG companion with Pillow without external SVG tooling."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return
    image = Image.new("RGB", (1500, 1120), "#fbfcfe")
    draw = ImageDraw.Draw(image)
    try:
        title = ImageFont.truetype("arialbd.ttf", 34)
        heading = ImageFont.truetype("arialbd.ttf", 23)
        body = ImageFont.truetype("arial.ttf", 17)
        small = ImageFont.truetype("arial.ttf", 13)
    except OSError:
        title = heading = body = small = ImageFont.load_default()
    draw.text((55, 35), "Q25 blind ARA9 missing-cut reconstruction", fill="#172033", font=title)
    draw.text(
        (55, 82),
        "See the SVG companion for the full vector figure and exact plotted values.",
        fill="#536176",
        font=body,
    )
    draw.rounded_rectangle((55, 130, 1445, 1060), 18, fill="#ffffff", outline="#d9e0ea")
    draw.text((90, 170), "Q25 result visualization generated successfully", fill="#172033", font=heading)
    draw.text(
        (90, 225),
        "Open Q25_ARA9_BLIND_MISSING_CUT_GEOMETRY.svg for the complete chart.",
        fill="#536176",
        font=body,
    )
    draw.text(
        (90, 1015),
        "The PNG is a durable fallback; the SVG is the authoritative visualization.",
        fill="#5d6878",
        font=small,
    )
    image.save(FIGURE_PNG)


def reveal() -> None:
    protocol_hash = verify_protocol()
    expected_prediction_hash = PREDICTIONS_SHA.read_text(encoding="utf-8").split()[0]
    actual_prediction_hash = digest(PREDICTIONS_JSON)
    if actual_prediction_hash != expected_prediction_hash:
        raise RuntimeError("Prediction packet changed after freeze")

    prediction_packet = json.loads(PREDICTIONS_JSON.read_text(encoding="utf-8"))
    target_packet = json.loads(TARGETS_JSON.read_text(encoding="utf-8"))
    if prediction_packet["protocol_sha256"] != protocol_hash:
        raise RuntimeError("Prediction protocol hash mismatch")
    if target_packet["protocol_sha256"] != protocol_hash:
        raise RuntimeError("Target protocol hash mismatch")

    targets = {row["case_id"]: row for row in target_packet["cases"]}
    rows: list[dict[str, Any]] = []
    for prediction in prediction_packet["predictions"]:
        target = targets[prediction["case_id"]]
        row = {**prediction, **target}
        target_value = float(row["target_connected"])
        for prefix, field in [
            ("ara", "ara_prediction_connected"),
            ("ridge", "ridge_prediction_connected"),
            ("mean8", "mean8_prediction_connected"),
            ("physical_midpoint", "physical_midpoint_prediction_connected"),
        ]:
            value = row[field]
            row[f"{prefix}_absolute_error"] = (
                None if value is None else abs(float(value) - target_value)
            )
        row["ara_target_class"] = classify(target_value)
        row["ara_prediction_class"] = classify(
            float(row["ara_prediction_connected"])
        )
        rows.append(row)

    fields = {
        "ara": "ara_prediction_connected",
        "ridge": "ridge_prediction_connected",
        "mean8": "mean8_prediction_connected",
        "physical_midpoint": "physical_midpoint_prediction_connected",
    }
    summaries: dict[str, dict[str, dict[str, Any]]] = {}
    for group in ["primary", "secondary"]:
        group_rows = [row for row in rows if row["group"] == group]
        summaries[group] = {
            model: summarize_model(group_rows, field) for model, field in fields.items()
        }

    primary_rows = [row for row in rows if row["group"] == "primary"]
    bootstraps = {
        control: cluster_bootstrap(
            primary_rows,
            "ara_prediction_connected",
            field,
            BOOTSTRAP_SEED + index,
        )
        for index, (control, field) in enumerate(
            [
                ("ridge", "ridge_prediction_connected"),
                ("mean8", "mean8_prediction_connected"),
                ("physical_midpoint", "physical_midpoint_prediction_connected"),
            ]
        )
    }

    permutation: dict[str, Any] = {}
    for control, field in [
        ("ridge", "ridge_prediction_connected"),
        ("mean8", "mean8_prediction_connected"),
        ("physical_midpoint", "physical_midpoint_prediction_connected"),
    ]:
        differences = np.array(
            [
                abs(float(row[field]) - float(row["target_connected"]))
                - abs(
                    float(row["ara_prediction_connected"])
                    - float(row["target_connected"])
                )
                for row in primary_rows
                if row[field] is not None
            ],
            dtype=np.float64,
        )
        permutation[control] = {
            "n": len(differences),
            "mean_control_minus_ara_absolute_error": float(np.mean(differences)),
            "exact_one_sided_sign_flip_p": exact_sign_flip_pvalue(differences),
        }

    entity_metrics = full_entity_metrics()
    input_metric = entity_metrics["Fig3a-mixed-input"]
    output_metrics = [entity_metrics[f"Fig3b-{label}"] for label in ["AA", "AD", "DA", "DD"]]
    transition = {
        "input": {
            "closure_strength": input_metric["closure_strength"],
            "retained_directions": input_metric["retained_directions_at_0p50"],
        },
        "outputs": {
            label: {
                "closure_strength": entity_metrics[f"Fig3b-{label}"][
                    "closure_strength"
                ],
                "retained_directions": entity_metrics[f"Fig3b-{label}"][
                    "retained_directions_at_0p50"
                ],
            }
            for label in ["AA", "AD", "DA", "DD"]
        },
        "mean_output_closure_strength": float(
            np.mean([metric["closure_strength"] for metric in output_metrics])
        ),
    }
    transition["mean_output_minus_input_closure"] = (
        transition["mean_output_closure_strength"]
        - transition["input"]["closure_strength"]
    )
    transition_gates = {
        "T1_input_trough": (
            transition["input"]["retained_directions"] == 0
            and transition["input"]["closure_strength"] <= 0.20
        ),
        "T2_all_outputs_crest": all(
            metric["retained_directions_at_0p50"] >= 2
            and metric["closure_strength"] >= 0.40
            for metric in output_metrics
        ),
        "T3_closure_gain": transition["mean_output_minus_input_closure"] >= 0.35,
    }
    transition["gates"] = transition_gates
    transition["verdict"] = (
        "SUPPORTED"
        if all(transition_gates.values())
        else "NOT SUPPORTED"
    )

    geometry_packet = json.loads(GEOMETRY_JSON.read_text(encoding="utf-8"))
    quality = geometry_packet["source_quality"]
    source_md5_ok = all(
        digest(SOURCE_DIR / filename, "md5") == expected
        for _entity, (filename, expected, _basis) in {
            **PRIMARY_FILES,
            **SECONDARY_FILES,
        }.items()
    )
    primary_quality_ok = all(
        quality[entity]["hermitian_residual_before_symmetrization"] <= 1e-8
        and quality[entity]["trace_residual_after_normalization"] <= 1e-8
        and quality[entity]["minimum_eigenvalue"] >= -1e-6
        for entity in PRIMARY_FILES
    )
    primary = summaries["primary"]
    gates = {
        "S1_source_md5": source_md5_ok,
        "S2_primary_matrix_quality": primary_quality_ok,
        "S3_exactly_45_predictions_frozen": (
            len(primary_rows) == 45
            and prediction_packet["case_count"] == 81
            and prediction_packet["target_packet_read"] is False
        ),
        "S4_ara_mae_below_ridge": primary["ara"]["mae"] < primary["ridge"]["mae"],
        "S5_ara_mae_below_mean8": primary["ara"]["mae"] < primary["mean8"]["mae"],
        "S6_ara_mae_below_physical_midpoint": (
            primary["ara"]["mae"] < primary["physical_midpoint"]["mae"]
        ),
        "S7_ara_median_at_most_every_control": all(
            primary["ara"]["median_absolute_error"]
            <= primary[control]["median_absolute_error"]
            for control in ["ridge", "mean8", "physical_midpoint"]
        ),
        "S8_ara_classification_above_every_control": all(
            primary["ara"]["pole_quiet_accuracy"]
            > primary[control]["pole_quiet_accuracy"]
            for control in ["ridge", "mean8", "physical_midpoint"]
        ),
        "S9_ara_mae_at_most_0p15": primary["ara"]["mae"] <= 0.15,
        "S10_ara_pearson_at_least_0p75": primary["ara"]["pearson"] >= 0.75,
        "S11_bootstrap_below_ridge_at_least_0p95": (
            bootstraps["ridge"]["probability_ara_lower_mae"] >= 0.95
        ),
        "S12_bootstrap_below_physical_at_least_0p90": (
            bootstraps["physical_midpoint"]["probability_ara_lower_mae"] >= 0.90
        ),
    }
    verdict = "SUPPORTED" if all(gates.values()) else "NOT SUPPORTED"

    write_prediction_csv(rows)
    write_metrics_csv(summaries, entity_metrics)
    make_svg(rows, summaries, entity_metrics)
    rasterize_summary_svg_fallback()

    results = {
        "protocol_id": "Q25-ARA9-MISSING-CUT-v1",
        "ledger_id": "T281",
        "protocol_sha256": protocol_hash,
        "prediction_sha256": actual_prediction_hash,
        "test_class": "blind external missing-cut reconstruction on processed public density matrices",
        "source": {
            "doi": "10.5281/zenodo.4604775",
            "primary_platform": "two distant atomic qubits",
            "primary_matrices": len(PRIMARY_FILES),
            "primary_predictions": len(primary_rows),
            "secondary_matrices": len(SECONDARY_FILES),
            "secondary_predictions": len([r for r in rows if r["group"] == "secondary"]),
            "source_quality": quality,
        },
        "summaries": summaries,
        "cluster_bootstrap": bootstraps,
        "paired_sign_flip": permutation,
        "entity_metrics": entity_metrics,
        "larger_wave_transition_probe": transition,
        "gates": gates,
        "gates_passed": sum(gates.values()),
        "gates_total": len(gates),
        "verdict": verdict,
        "evidence_boundary": (
            "External numerical targets were untouched at protocol freeze and were read only after the "
            "81 prediction packet was hashed. The source provides reconstructed density matrices rather "
            "than raw shot records."
        ),
        "artifacts": {
            "predictions_csv": PREDICTIONS_CSV.name,
            "metrics_csv": METRICS_CSV.name,
            "figure_svg": FIGURE_SVG.name,
            "figure_png": FIGURE_PNG.name,
        },
    }
    RESULTS_JSON.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Q25 verdict: {verdict} — {sum(gates.values())}/{len(gates)} gates")
    print(
        "Primary ARA MAE: "
        f"{primary['ara']['mae']:.6f}; physical midpoint: "
        f"{primary['physical_midpoint']['mae']:.6f}; ridge: "
        f"{primary['ridge']['mae']:.6f}"
    )
    print(
        "Larger-wave trough-to-crest probe: "
        f"{transition['verdict']} — {sum(transition_gates.values())}/"
        f"{len(transition_gates)} gates"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["prepare", "predict", "reveal"])
    args = parser.parse_args()
    if args.stage == "prepare":
        prepare()
    elif args.stage == "predict":
        predict()
    else:
        reveal()


if __name__ == "__main__":
    main()

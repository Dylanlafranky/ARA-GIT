#!/usr/bin/env python3
"""Run the frozen T280/Q24 ARA^9 connected Bell-relation calibration."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from q4_bell_parent_child_test import expectations
from q5_bell_four_state_test import STATE_CONFIGS, load_state, verify_sources
from q6_chsh_coherence_ladder_test import (
    BELL_STATES,
    CLASSICAL_CONTROLS,
    CONTROL_WEIGHTS,
    ENTITY_ORDER,
    UNIFORM_CONTROL,
)


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "Q24_ARA9_BELL_RELATION_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q24_ARA9_BELL_RELATION_PROTOCOL_v1_FROZEN.sha256"
Q5_RESULTS = HERE / "Q5_BELL_FOUR_STATE_RESULTS.json"
Q6B_RESULTS = HERE / "Q6B_PHYSICAL_CHSH_COHERENCE_RESULTS.json"
Q6B_VALIDATION = HERE / "Q6B_PHYSICAL_CHSH_COHERENCE_VALIDATION.json"
MATRICES_CSV = HERE / "Q24_ARA9_BELL_RELATION_MATRICES.csv"
METRICS_CSV = HERE / "Q24_ARA9_BELL_RELATION_METRICS.csv"
BOOTSTRAP_CSV = HERE / "Q24_ARA9_BELL_RELATION_BOOTSTRAP.csv"
RESULTS_JSON = HERE / "Q24_ARA9_BELL_RELATION_RESULTS.json"
FIGURE_PNG = HERE / "Q24_ARA9_BELL_RELATION_GEOMETRY.png"
FIGURE_SVG = HERE / "Q24_ARA9_BELL_RELATION_GEOMETRY.svg"

AXES = ("X", "Y", "Z")
TENSOR_LABELS = (
    ("XX", "XY", "XZ"),
    ("YX", "YY", "YZ"),
    ("ZX", "ZY", "ZZ"),
)
BOOTSTRAP_SEED = 2026072624
BOOTSTRAP_REPS = 2000
STRONG_AXIS_THRESHOLD = 0.50
EXPECTED_RETAINED = {
    "Phi-plus": 3,
    "Phi-minus": 3,
    "Psi-plus": 3,
    "Psi-minus": 3,
    "Phi-classical": 1,
    "Psi-classical": 1,
    "Bell-uniform-mixed": 0,
}


def digest(path: Path, algorithm: str = "sha256") -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_inputs() -> dict[str, object]:
    expected_protocol_sha = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    observed_protocol_sha = digest(PROTOCOL)
    if observed_protocol_sha != expected_protocol_sha:
        raise RuntimeError(
            "Frozen Q24 protocol mismatch: "
            f"expected {expected_protocol_sha}, observed {observed_protocol_sha}"
        )

    archive_md5, q5_protocol_sha = verify_sources()
    q6b_validation = json.loads(Q6B_VALIDATION.read_text(encoding="utf-8"))
    if q6b_validation.get("verdict") != "PASS":
        raise RuntimeError("Q6B upstream validation is not PASS")

    return {
        "protocol_sha256": observed_protocol_sha,
        "q5_protocol_sha256": q5_protocol_sha,
        "q5_results_sha256": digest(Q5_RESULTS),
        "q6b_results_sha256": digest(Q6B_RESULTS),
        "q6b_validation_sha256": digest(Q6B_VALIDATION),
        "archive_md5": archive_md5,
    }


def components_from_expectations(
    exp: dict[str, float],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    a = np.asarray([exp["XI"], exp["YI"], exp["ZI"]], dtype=np.float64)
    b = np.asarray([exp["IX"], exp["IY"], exp["IZ"]], dtype=np.float64)
    tensor = np.asarray(
        [[exp[label] for label in row] for row in TENSOR_LABELS],
        dtype=np.float64,
    )
    return a, b, tensor


def mix_expectations(
    state_expectations: dict[str, dict[str, float]],
    weights: dict[str, float],
) -> dict[str, float]:
    labels = tuple(next(iter(state_expectations.values())).keys())
    return {
        label: float(
            sum(weights[state] * state_expectations[state][label] for state in weights)
        )
        for label in labels
    }


def connected_metrics(
    a: np.ndarray,
    b: np.ndarray,
    tensor: np.ndarray,
) -> dict[str, object]:
    independent = np.outer(a, b)
    connected = tensor - independent
    ara9 = 1.0 - connected
    singular = np.sort(np.linalg.svd(connected, compute_uv=False))[::-1]
    determinant = float(np.linalg.det(connected))
    closure_strength = float(abs(determinant) ** (1.0 / 3.0))
    balance = float(singular[2] / singular[0]) if singular[0] > 0 else 0.0
    relation_power = float(np.linalg.norm(connected, ord="fro") ** 2)
    local_power = float(np.dot(a, a) + np.dot(b, b))
    denominator = relation_power + local_power
    relation_dominance = relation_power / denominator if denominator > 0 else 0.0
    affine_residual = float(np.max(np.abs(connected - (1.0 - ara9))))
    lower_excursion = max(0.0, float(-np.min(ara9)))
    upper_excursion = max(0.0, float(np.max(ara9) - 2.0))
    return {
        "a": a,
        "b": b,
        "joint": tensor,
        "independent": independent,
        "connected": connected,
        "ara9": ara9,
        "singular_values": singular,
        "retained_directions_at_0p50": int(
            np.sum(singular >= STRONG_AXIS_THRESHOLD)
        ),
        "determinant": determinant,
        "closure_strength": closure_strength,
        "directional_balance": balance,
        "relation_dominance_share": relation_dominance,
        "relation_power": relation_power,
        "local_power": local_power,
        "affine_residual": affine_residual,
        "ara9_min": float(np.min(ara9)),
        "ara9_max": float(np.max(ara9)),
        "ara9_bound_excursion": max(lower_excursion, upper_excursion),
    }


def raw_point_entities() -> tuple[
    dict[str, dict[str, float]], dict[str, dict[str, object]], dict[str, object]
]:
    q5 = json.loads(Q5_RESULTS.read_text(encoding="utf-8"))
    prepared_exp = {
        state: {
            label: float(value)
            for label, value in q5["states"][state]["expectations"].items()
        }
        for state in BELL_STATES
    }
    all_exp = dict(prepared_exp)
    for control, weights in CONTROL_WEIGHTS.items():
        all_exp[control] = mix_expectations(prepared_exp, weights)
    metrics = {
        entity: connected_metrics(*components_from_expectations(all_exp[entity]))
        for entity in ENTITY_ORDER
    }
    return all_exp, metrics, q5


def physical_point_entities() -> tuple[
    dict[str, dict[str, object]], dict[str, object]
]:
    q6b = json.loads(Q6B_RESULTS.read_text(encoding="utf-8"))
    metrics: dict[str, dict[str, object]] = {}
    for entity in ENTITY_ORDER:
        source = q6b["entities"][entity]
        local = source["local_expectations"]
        a = np.asarray([local["XI"], local["YI"], local["ZI"]], dtype=np.float64)
        b = np.asarray([local["IX"], local["IY"], local["IZ"]], dtype=np.float64)
        tensor = np.asarray(source["tensor"], dtype=np.float64)
        metrics[entity] = connected_metrics(a, b, tensor)
    return metrics, q6b


def load_raw_records() -> dict[str, dict[str, np.ndarray]]:
    records: dict[str, dict[str, np.ndarray]] = {}
    for state in BELL_STATES:
        state_records, _ = load_state(state, STATE_CONFIGS[state])
        records[state] = state_records
    return records


def interval(values: np.ndarray) -> list[float]:
    low, high = np.percentile(values, [2.5, 97.5])
    return [float(low), float(high)]


def bootstrap(
    records: dict[str, dict[str, np.ndarray]],
) -> tuple[dict[str, dict[str, object]], list[dict[str, object]]]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    names = (
        "s1",
        "s2",
        "s3",
        "retained",
        "determinant",
        "closure",
        "balance",
        "relation_dominance",
    )
    draws = {
        entity: {
            name: np.empty(
                BOOTSTRAP_REPS,
                dtype=np.int8 if name == "retained" else np.float64,
            )
            for name in names
        }
        for entity in ENTITY_ORDER
    }
    rows: list[dict[str, object]] = []

    for repetition in range(BOOTSTRAP_REPS):
        prepared_exp: dict[str, dict[str, float]] = {}
        for state in BELL_STATES:
            probabilities = {}
            for orientation, values in records[state].items():
                indices = rng.integers(0, len(values), size=len(values))
                probabilities[orientation] = values[indices].mean(axis=0)
            prepared_exp[state] = expectations(probabilities)

        all_exp = dict(prepared_exp)
        for control, weights in CONTROL_WEIGHTS.items():
            all_exp[control] = mix_expectations(prepared_exp, weights)

        for entity in ENTITY_ORDER:
            metrics = connected_metrics(
                *components_from_expectations(all_exp[entity])
            )
            singular = metrics["singular_values"]
            values = {
                "s1": float(singular[0]),
                "s2": float(singular[1]),
                "s3": float(singular[2]),
                "retained": int(metrics["retained_directions_at_0p50"]),
                "determinant": float(metrics["determinant"]),
                "closure": float(metrics["closure_strength"]),
                "balance": float(metrics["directional_balance"]),
                "relation_dominance": float(
                    metrics["relation_dominance_share"]
                ),
            }
            for name, value in values.items():
                draws[entity][name][repetition] = value
            rows.append(
                {
                    "entity": entity,
                    "entity_type": (
                        "physically_prepared"
                        if entity in BELL_STATES
                        else "equal_weight_reconstruction"
                    ),
                    "replicate": repetition,
                    **values,
                }
            )

    summaries: dict[str, dict[str, object]] = {}
    for entity in ENTITY_ORDER:
        entity_draws = draws[entity]
        expected = EXPECTED_RETAINED[entity]
        summaries[entity] = {
            "expected_retained_directions": expected,
            "fraction_expected_retained": float(
                np.mean(entity_draws["retained"] == expected)
            ),
            "fraction_negative_determinant": float(
                np.mean(entity_draws["determinant"] < 0.0)
            ),
            "s1_95ci": interval(entity_draws["s1"]),
            "s2_95ci": interval(entity_draws["s2"]),
            "s3_95ci": interval(entity_draws["s3"]),
            "determinant_95ci": interval(entity_draws["determinant"]),
            "closure_95ci": interval(entity_draws["closure"]),
            "balance_95ci": interval(entity_draws["balance"]),
            "relation_dominance_95ci": interval(
                entity_draws["relation_dominance"]
            ),
        }
    return summaries, rows


def rotation(axis: str, angle: float) -> np.ndarray:
    c = math.cos(angle)
    s = math.sin(angle)
    if axis == "X":
        return np.asarray([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=float)
    if axis == "Y":
        return np.asarray([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=float)
    if axis == "Z":
        return np.asarray([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=float)
    raise ValueError(axis)


def representation_controls(
    raw_metrics: dict[str, dict[str, object]],
) -> dict[str, object]:
    rx = rotation("X", math.pi / 5.0)
    ry = rotation("Y", math.pi / 4.0)
    rz = rotation("Z", math.pi / 3.0)
    pairs = (
        (rx, ry),
        (ry, rz),
        (rz, rx),
        (rz @ ry, rx @ rz),
    )
    max_residual = 0.0
    rotation_rows = []
    for entity in ENTITY_ORDER:
        base = raw_metrics[entity]
        base_vector = np.asarray(
            [
                *base["singular_values"],
                base["closure_strength"],
                base["directional_balance"],
                base["relation_dominance_share"],
                base["determinant"],
            ],
            dtype=float,
        )
        for pair_index, (left, right) in enumerate(pairs):
            rotated = connected_metrics(
                left @ base["a"],
                right @ base["b"],
                left @ base["joint"] @ right.T,
            )
            rotated_vector = np.asarray(
                [
                    *rotated["singular_values"],
                    rotated["closure_strength"],
                    rotated["directional_balance"],
                    rotated["relation_dominance_share"],
                    rotated["determinant"],
                ],
                dtype=float,
            )
            residual = float(np.max(np.abs(base_vector - rotated_vector)))
            max_residual = max(max_residual, residual)
            rotation_rows.append(
                {
                    "entity": entity,
                    "rotation_pair": pair_index,
                    "maximum_invariant_residual": residual,
                }
            )

    rank_one_rows = []
    rank_one_pass = True
    for entity in BELL_STATES:
        connected = raw_metrics[entity]["connected"]
        u, singular, vt = np.linalg.svd(connected)
        compressed = singular[0] * np.outer(u[:, 0], vt[0, :])
        compressed_metrics = connected_metrics(
            np.zeros(3), np.zeros(3), compressed
        )
        row = {
            "entity": entity,
            "retained_directions": int(
                compressed_metrics["retained_directions_at_0p50"]
            ),
            "determinant_residual": float(
                abs(compressed_metrics["determinant"])
            ),
        }
        row["pass"] = (
            row["retained_directions"] == 1
            and row["determinant_residual"] <= 1e-12
        )
        rank_one_pass = rank_one_pass and bool(row["pass"])
        rank_one_rows.append(row)

    return {
        "fixed_proper_rotation_pairs": 4,
        "maximum_invariant_residual": max_residual,
        "rotation_rows": rotation_rows,
        "rank_one_rows": rank_one_rows,
        "rank_one_all_pass": rank_one_pass,
    }


def gate(
    value: object,
    requirement: str,
    passed: bool,
) -> dict[str, object]:
    return {"value": value, "requirement": requirement, "pass": bool(passed)}


def frozen_gates(
    raw: dict[str, dict[str, object]],
    physical: dict[str, dict[str, object]],
    bootstrap_summary: dict[str, dict[str, object]],
    controls: dict[str, object],
) -> dict[str, dict[str, object]]:
    raw_sequence = [
        int(raw[entity]["retained_directions_at_0p50"])
        for entity in ENTITY_ORDER
    ]
    physical_sequence = [
        int(physical[entity]["retained_directions_at_0p50"])
        for entity in ENTITY_ORDER
    ]
    expected_sequence = [3, 3, 3, 3, 1, 1, 0]
    raw_closure = {
        entity: float(raw[entity]["closure_strength"]) for entity in ENTITY_ORDER
    }
    raw_balance = {
        entity: float(raw[entity]["directional_balance"]) for entity in ENTITY_ORDER
    }
    raw_dominance = {
        entity: float(raw[entity]["relation_dominance_share"])
        for entity in ENTITY_ORDER
    }
    raw_det = {entity: float(raw[entity]["determinant"]) for entity in ENTITY_ORDER}

    return {
        "R1_affine_recovery": gate(
            max(float(raw[entity]["affine_residual"]) for entity in ENTITY_ORDER),
            "<= 1e-12",
            all(
                float(raw[entity]["affine_residual"]) <= 1e-12
                for entity in ENTITY_ORDER
            ),
        ),
        "R2_bell_three_retained": gate(
            raw_sequence[:4],
            "all equal 3",
            all(value == 3 for value in raw_sequence[:4]),
        ),
        "R3_bell_s3_at_least_0p50": gate(
            {
                entity: float(raw[entity]["singular_values"][2])
                for entity in BELL_STATES
            },
            "all >= 0.50",
            all(
                float(raw[entity]["singular_values"][2]) >= 0.50
                for entity in BELL_STATES
            ),
        ),
        "R4_classical_one_retained": gate(
            raw_sequence[4:6],
            "both equal 1",
            all(value == 1 for value in raw_sequence[4:6]),
        ),
        "R5_uniform_zero_retained": gate(
            raw_sequence[6],
            "equal 0",
            raw_sequence[6] == 0,
        ),
        "R6_exact_ladder": gate(
            raw_sequence,
            str(expected_sequence),
            raw_sequence == expected_sequence,
        ),
        "R7_closure_separation": gate(
            raw_closure,
            "Bell >= 0.75; controls <= 0.30",
            all(raw_closure[entity] >= 0.75 for entity in BELL_STATES)
            and all(
                raw_closure[entity] <= 0.30
                for entity in (*CLASSICAL_CONTROLS, UNIFORM_CONTROL)
            ),
        ),
        "R8_directional_balance": gate(
            raw_balance,
            "Bell >= 0.70; classical <= 0.15",
            all(raw_balance[entity] >= 0.70 for entity in BELL_STATES)
            and all(
                raw_balance[entity] <= 0.15 for entity in CLASSICAL_CONTROLS
            ),
        ),
        "R9_relation_dominance": gate(
            {entity: raw_dominance[entity] for entity in BELL_STATES},
            "all >= 0.95",
            all(raw_dominance[entity] >= 0.95 for entity in BELL_STATES),
        ),
        "R10_bell_negative_determinant": gate(
            {entity: raw_det[entity] for entity in BELL_STATES},
            "all < 0",
            all(raw_det[entity] < 0.0 for entity in BELL_STATES),
        ),
        "B1_bell_bootstrap_stability": gate(
            {
                entity: {
                    "fraction_three_retained": bootstrap_summary[entity][
                        "fraction_expected_retained"
                    ],
                    "fraction_negative_determinant": bootstrap_summary[entity][
                        "fraction_negative_determinant"
                    ],
                }
                for entity in BELL_STATES
            },
            "both fractions >= 0.95 for every Bell state",
            all(
                bootstrap_summary[entity]["fraction_expected_retained"] >= 0.95
                and bootstrap_summary[entity]["fraction_negative_determinant"]
                >= 0.95
                for entity in BELL_STATES
            ),
        ),
        "B2_control_bootstrap_stability": gate(
            {
                entity: bootstrap_summary[entity]["fraction_expected_retained"]
                for entity in (*CLASSICAL_CONTROLS, UNIFORM_CONTROL)
            },
            "all >= 0.90",
            all(
                bootstrap_summary[entity]["fraction_expected_retained"] >= 0.90
                for entity in (*CLASSICAL_CONTROLS, UNIFORM_CONTROL)
            ),
        ),
        "P1_physical_exact_ladder": gate(
            physical_sequence,
            str(expected_sequence),
            physical_sequence == expected_sequence,
        ),
        "P2_raw_physical_agreement": gate(
            {
                "raw": raw_sequence,
                "physical": physical_sequence,
            },
            "all seven classifications equal",
            raw_sequence == physical_sequence,
        ),
        "I1_rotation_invariance": gate(
            controls["maximum_invariant_residual"],
            "<= 1e-12",
            float(controls["maximum_invariant_residual"]) <= 1e-12,
        ),
        "I2_rank_one_destruction": gate(
            controls["rank_one_rows"],
            "one retained direction and |det| <= 1e-12 for every Bell compression",
            bool(controls["rank_one_all_pass"]),
        ),
    }


def serializable_metrics(metrics: dict[str, object]) -> dict[str, object]:
    return {
        "a": metrics["a"].tolist(),
        "b": metrics["b"].tolist(),
        "joint": metrics["joint"].tolist(),
        "independent": metrics["independent"].tolist(),
        "connected": metrics["connected"].tolist(),
        "ara9": metrics["ara9"].tolist(),
        "singular_values": metrics["singular_values"].tolist(),
        "retained_directions_at_0p50": metrics[
            "retained_directions_at_0p50"
        ],
        "determinant": metrics["determinant"],
        "closure_strength": metrics["closure_strength"],
        "directional_balance": metrics["directional_balance"],
        "relation_dominance_share": metrics["relation_dominance_share"],
        "relation_power": metrics["relation_power"],
        "local_power": metrics["local_power"],
        "affine_residual": metrics["affine_residual"],
        "ara9_min": metrics["ara9_min"],
        "ara9_max": metrics["ara9_max"],
        "ara9_bound_excursion": metrics["ara9_bound_excursion"],
    }


def write_tables(
    raw: dict[str, dict[str, object]],
    physical: dict[str, dict[str, object]],
    bootstrap_rows: list[dict[str, object]],
) -> None:
    matrix_rows = []
    metric_rows = []
    for layer, layer_metrics in (("raw_linear", raw), ("physical", physical)):
        for entity in ENTITY_ORDER:
            metrics = layer_metrics[entity]
            for i, left in enumerate(AXES):
                for j, right in enumerate(AXES):
                    matrix_rows.append(
                        {
                            "layer": layer,
                            "entity": entity,
                            "axis_a": left,
                            "axis_b": right,
                            "slot": left + right,
                            "joint_value": metrics["joint"][i, j],
                            "independent_child_product": metrics["independent"][
                                i, j
                            ],
                            "connected_relation": metrics["connected"][i, j],
                            "ara9_coordinate": metrics["ara9"][i, j],
                        }
                    )
            singular = metrics["singular_values"]
            metric_rows.append(
                {
                    "layer": layer,
                    "entity": entity,
                    "entity_type": (
                        "physically_prepared"
                        if entity in BELL_STATES
                        else "equal_weight_reconstruction"
                    ),
                    "s1": singular[0],
                    "s2": singular[1],
                    "s3": singular[2],
                    "retained_directions_at_0p50": metrics[
                        "retained_directions_at_0p50"
                    ],
                    "determinant": metrics["determinant"],
                    "closure_strength": metrics["closure_strength"],
                    "directional_balance": metrics["directional_balance"],
                    "relation_dominance_share": metrics[
                        "relation_dominance_share"
                    ],
                    "relation_power": metrics["relation_power"],
                    "local_power": metrics["local_power"],
                    "ara9_min": metrics["ara9_min"],
                    "ara9_max": metrics["ara9_max"],
                    "ara9_bound_excursion": metrics["ara9_bound_excursion"],
                }
            )

    with MATRICES_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(matrix_rows[0]))
        writer.writeheader()
        writer.writerows(matrix_rows)
    with METRICS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metric_rows[0]))
        writer.writeheader()
        writer.writerows(metric_rows)
    with BOOTSTRAP_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(bootstrap_rows[0]))
        writer.writeheader()
        writer.writerows(bootstrap_rows)


def plot_geometry(
    raw: dict[str, dict[str, object]],
    physical: dict[str, dict[str, object]],
) -> None:
    from html import escape

    from PIL import Image, ImageDraw, ImageFont

    width, height = 1600, 1490
    background = "#f7f9fc"
    panel_fill = "#ffffff"
    panel_border = "#cbd5e1"
    ink = "#172033"
    muted = "#526071"
    blue = (79, 130, 189)
    ridge = (246, 244, 237)
    orange = (209, 139, 71)

    def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        candidates = (
            "C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        )
        for candidate in candidates:
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                continue
        return ImageFont.load_default()

    title_font = font(30, True)
    subtitle_font = font(17)
    layer_font = font(21, True)
    panel_title_font = font(18, True)
    metric_font = font(14)
    cell_font = font(16, True)
    axis_font = font(14, True)

    def mix(left: tuple[int, int, int], right: tuple[int, int, int], t: float):
        return tuple(
            int(round((1.0 - t) * left[channel] + t * right[channel]))
            for channel in range(3)
        )

    def ara_color(value: float) -> tuple[int, int, int]:
        t = float(np.clip(value / 2.0, 0.0, 1.0))
        return mix(blue, ridge, 2.0 * t) if t <= 0.5 else mix(
            ridge, orange, 2.0 * (t - 0.5)
        )

    image = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(image)
    draw.text(
        (width // 2, 28),
        "Q24 ARA⁹ connected Bell relation",
        fill=ink,
        font=title_font,
        anchor="ma",
    )
    draw.text(
        (width // 2, 69),
        "Nine slots = 1 − (joint relation − separate-child product); 1.0 is the ARA ridge",
        fill=muted,
        font=subtitle_font,
        anchor="ma",
    )

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{background}"/>',
        '<style>text{font-family:"Segoe UI",Arial,sans-serif;fill:#172033}'
        '.muted{fill:#526071}.title{font-weight:700}.axis{font-weight:600}</style>',
        f'<text x="{width / 2}" y="48" text-anchor="middle" font-size="30" '
        'class="title">Q24 ARA⁹ connected Bell relation</text>',
        f'<text x="{width / 2}" y="78" text-anchor="middle" font-size="17" '
        'class="muted">Nine slots = 1 − (joint relation − separate-child product); '
        '1.0 is the ARA ridge</text>',
    ]

    panel_w = 355
    panel_h = 285
    left = 72
    top = 135
    gap_x = 20
    gap_y = 38
    cell = 62
    grid_dx = 82
    grid_dy = 78
    layers = (
        ("RAW ARA LAYER — current records, no physical projection", raw),
        ("ESTABLISHED-PHYSICS COMPANION — positive density states", physical),
    )

    for layer_index, (layer_label, layer_metrics) in enumerate(layers):
        layer_top = top + layer_index * (2 * panel_h + gap_y + 74)
        draw.text(
            (left, layer_top - 39),
            layer_label,
            fill=ink,
            font=layer_font,
        )
        svg.append(
            f'<text x="{left}" y="{layer_top - 16}" font-size="21" '
            f'class="title">{escape(layer_label)}</text>'
        )

        for index, entity in enumerate(ENTITY_ORDER):
            row = index // 4
            col = index % 4
            px = left + col * (panel_w + gap_x)
            py = layer_top + row * (panel_h + gap_y)
            draw.rounded_rectangle(
                (px, py, px + panel_w, py + panel_h),
                radius=12,
                fill=panel_fill,
                outline=panel_border,
                width=2,
            )
            svg.append(
                f'<rect x="{px}" y="{py}" width="{panel_w}" height="{panel_h}" '
                f'rx="12" fill="{panel_fill}" stroke="{panel_border}" stroke-width="2"/>'
            )
            metrics = layer_metrics[entity]
            singular = metrics["singular_values"]
            draw.text(
                (px + 16, py + 12),
                entity,
                fill=ink,
                font=panel_title_font,
            )
            metric_text = (
                f"r={metrics['retained_directions_at_0p50']}  "
                f"s=({singular[0]:.2f},{singular[1]:.2f},{singular[2]:.2f})  "
                f"h={metrics['closure_strength']:.2f}"
            )
            draw.text(
                (px + 16, py + 39),
                metric_text,
                fill=muted,
                font=metric_font,
            )
            svg.extend(
                [
                    f'<text x="{px + 16}" y="{py + 29}" font-size="18" '
                    f'class="title">{escape(entity)}</text>',
                    f'<text x="{px + 16}" y="{py + 53}" font-size="14" '
                    f'class="muted">{escape(metric_text)}</text>',
                ]
            )
            gx = px + grid_dx
            gy = py + grid_dy
            for axis_index, axis in enumerate(AXES):
                draw.text(
                    (gx + axis_index * cell + cell / 2, gy - 19),
                    axis,
                    fill=muted,
                    font=axis_font,
                    anchor="mm",
                )
                draw.text(
                    (gx - 22, gy + axis_index * cell + cell / 2),
                    axis,
                    fill=muted,
                    font=axis_font,
                    anchor="mm",
                )
                svg.extend(
                    [
                        f'<text x="{gx + axis_index * cell + cell / 2}" '
                        f'y="{gy - 8}" text-anchor="middle" font-size="14" '
                        f'class="axis muted">{axis}</text>',
                        f'<text x="{gx - 20}" '
                        f'y="{gy + axis_index * cell + cell / 2 + 5}" '
                        f'text-anchor="middle" font-size="14" '
                        f'class="axis muted">{axis}</text>',
                    ]
                )
            matrix = metrics["ara9"]
            for i in range(3):
                for j in range(3):
                    value = float(matrix[i, j])
                    color = ara_color(value)
                    color_hex = "#{:02x}{:02x}{:02x}".format(*color)
                    x0 = gx + j * cell
                    y0 = gy + i * cell
                    draw.rectangle(
                        (x0, y0, x0 + cell, y0 + cell),
                        fill=color,
                        outline="#d8dee8",
                        width=1,
                    )
                    draw.text(
                        (x0 + cell / 2, y0 + cell / 2),
                        f"{value:.2f}",
                        fill="#111111",
                        font=cell_font,
                        anchor="mm",
                    )
                    svg.extend(
                        [
                            f'<rect x="{x0}" y="{y0}" width="{cell}" height="{cell}" '
                            f'fill="{color_hex}" stroke="#d8dee8"/>',
                            f'<text x="{x0 + cell / 2}" y="{y0 + cell / 2 + 6}" '
                            f'text-anchor="middle" font-size="16" '
                            f'class="title">{value:.2f}</text>',
                        ]
                    )

    bar_x, bar_y, bar_w, bar_h = 300, height - 62, 1000, 20
    steps = 100
    for step in range(steps):
        value = 2.0 * step / (steps - 1)
        color = ara_color(value)
        color_hex = "#{:02x}{:02x}{:02x}".format(*color)
        x0 = bar_x + step * bar_w / steps
        x1 = bar_x + (step + 1) * bar_w / steps
        draw.rectangle((x0, bar_y, x1 + 1, bar_y + bar_h), fill=color)
        svg.append(
            f'<rect x="{x0}" y="{bar_y}" width="{x1 - x0 + 1}" '
            f'height="{bar_h}" fill="{color_hex}"/>'
        )
    for value, label in ((0, "0"), (0.382, "0.382"), (1, "1 ridge"), (1.618, "1.618"), (2, "2")):
        x = bar_x + value / 2.0 * bar_w
        draw.line((x, bar_y + bar_h, x, bar_y + bar_h + 8), fill=ink, width=1)
        draw.text(
            (x, bar_y + bar_h + 10),
            label,
            fill=muted,
            font=metric_font,
            anchor="ma",
        )
        svg.extend(
            [
                f'<line x1="{x}" y1="{bar_y + bar_h}" x2="{x}" '
                f'y2="{bar_y + bar_h + 8}" stroke="{ink}"/>',
                f'<text x="{x}" y="{bar_y + bar_h + 25}" text-anchor="middle" '
                f'font-size="14" class="muted">{escape(label)}</text>',
            ]
        )

    svg.append("</svg>")
    FIGURE_PNG.parent.mkdir(parents=True, exist_ok=True)
    image.save(FIGURE_PNG)
    FIGURE_SVG.write_text("\n".join(svg) + "\n", encoding="utf-8")


def main() -> None:
    source = verify_inputs()
    _, raw_metrics, q5 = raw_point_entities()
    physical_metrics, q6b = physical_point_entities()
    records = load_raw_records()
    bootstrap_summary, bootstrap_rows = bootstrap(records)
    controls = representation_controls(raw_metrics)
    gates = frozen_gates(
        raw_metrics,
        physical_metrics,
        bootstrap_summary,
        controls,
    )
    write_tables(raw_metrics, physical_metrics, bootstrap_rows)
    plot_geometry(raw_metrics, physical_metrics)

    gates_passed = sum(int(item["pass"]) for item in gates.values())
    verdict = "CALIBRATED" if gates_passed == len(gates) else "NOT CALIBRATED"
    results = {
        "protocol_id": "Q24-ARA9-BELL-RELATION-v1",
        "ledger_id": "T280",
        "test_class": "prior-geometry identification on already-open public data",
        "verdict": verdict,
        "gates_passed": gates_passed,
        "gates_total": len(gates),
        "source": {
            **source,
            "figshare_doi": "10.6084/m9.figshare.14160476.v2",
            "q5_verdict": q5["verdict"],
            "q6b_verdict": q6b["verdict"],
            "primary_layer": "Q5 raw-current linear expectation reconstruction",
            "companion_layer": "Q6B physical-state projection",
        },
        "ara9_definition": {
            "parent_a": ["XI", "YI", "ZI"],
            "parent_b": ["IX", "IY", "IZ"],
            "joint_slots": [label for row in TENSOR_LABELS for label in row],
            "connected_relation": "C = T - outer(a,b)",
            "ara_coordinate": "X9 = 1 - C",
            "strong_direction_threshold": STRONG_AXIS_THRESHOLD,
        },
        "raw_entities": {
            entity: serializable_metrics(raw_metrics[entity])
            for entity in ENTITY_ORDER
        },
        "physical_entities": {
            entity: serializable_metrics(physical_metrics[entity])
            for entity in ENTITY_ORDER
        },
        "bootstrap": {
            "seed": BOOTSTRAP_SEED,
            "replicates": BOOTSTRAP_REPS,
            "summary": bootstrap_summary,
        },
        "representation_controls": controls,
        "gates": gates,
        "artifacts": {
            "matrices_csv": MATRICES_CSV.name,
            "metrics_csv": METRICS_CSV.name,
            "bootstrap_csv": BOOTSTRAP_CSV.name,
            "figure_png": FIGURE_PNG.name,
            "figure_svg": FIGURE_SVG.name,
        },
        "evidence_boundary": (
            "Calibrated prior-geometry crosswalk on already-open Bell data; "
            "not a blind quantum prediction or a new entanglement result."
        ),
    }
    RESULTS_JSON.write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"Q24 verdict: {verdict}")
    print(f"Frozen gates: {gates_passed}/{len(gates)}")
    print(
        "Raw ladder:",
        [
            raw_metrics[entity]["retained_directions_at_0p50"]
            for entity in ENTITY_ORDER
        ],
    )
    print(
        "Physical ladder:",
        [
            physical_metrics[entity]["retained_directions_at_0p50"]
            for entity in ENTITY_ORDER
        ],
    )
    for entity in ENTITY_ORDER:
        metrics = raw_metrics[entity]
        print(
            f"{entity:20s} "
            f"s={tuple(round(float(v), 4) for v in metrics['singular_values'])} "
            f"h={metrics['closure_strength']:.4f} "
            f"balance={metrics['directional_balance']:.4f} "
            f"D_R={metrics['relation_dominance_share']:.4f} "
            f"det={metrics['determinant']:.4f}"
        )


if __name__ == "__main__":
    main()

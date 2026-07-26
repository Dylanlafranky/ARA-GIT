#!/usr/bin/env python3
"""Independently validate T280/Q24 without importing the primary runner."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "Q24_ARA9_BELL_RELATION_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q24_ARA9_BELL_RELATION_PROTOCOL_v1_FROZEN.sha256"
Q5_RESULTS = HERE / "Q5_BELL_FOUR_STATE_RESULTS.json"
Q5_PROJECTIONS = HERE / "Q5_BELL_FOUR_STATE_PROJECTIONS.csv"
Q6B_RESULTS = HERE / "Q6B_PHYSICAL_CHSH_COHERENCE_RESULTS.json"
MATRICES_CSV = HERE / "Q24_ARA9_BELL_RELATION_MATRICES.csv"
METRICS_CSV = HERE / "Q24_ARA9_BELL_RELATION_METRICS.csv"
BOOTSTRAP_CSV = HERE / "Q24_ARA9_BELL_RELATION_BOOTSTRAP.csv"
RESULTS_JSON = HERE / "Q24_ARA9_BELL_RELATION_RESULTS.json"
FIGURE_PNG = HERE / "Q24_ARA9_BELL_RELATION_GEOMETRY.png"
FIGURE_SVG = HERE / "Q24_ARA9_BELL_RELATION_GEOMETRY.svg"
VALIDATION_JSON = HERE / "Q24_ARA9_BELL_RELATION_VALIDATION.json"

BELL = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")
CLASSICAL = ("Phi-classical", "Psi-classical")
UNIFORM = "Bell-uniform-mixed"
ENTITIES = (*BELL, *CLASSICAL, UNIFORM)
WEIGHTS = {
    "Phi-classical": {"Phi-plus": 0.5, "Phi-minus": 0.5},
    "Psi-classical": {"Psi-plus": 0.5, "Psi-minus": 0.5},
    "Bell-uniform-mixed": {
        "Phi-plus": 0.25,
        "Phi-minus": 0.25,
        "Psi-plus": 0.25,
        "Psi-minus": 0.25,
    },
}
EXPECTED = {
    "Phi-plus": 3,
    "Phi-minus": 3,
    "Psi-plus": 3,
    "Psi-minus": 3,
    "Phi-classical": 1,
    "Psi-classical": 1,
    "Bell-uniform-mixed": 0,
}
AXES = ("X", "Y", "Z")
LABELS = (("XX", "XY", "XZ"), ("YX", "YY", "YZ"), ("ZX", "ZY", "ZZ"))
TOL = 1e-12


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def relation(a: np.ndarray, b: np.ndarray, tensor: np.ndarray) -> dict[str, object]:
    independent = np.outer(a, b)
    connected = tensor - independent
    ara = 1.0 - connected
    singular = np.sort(np.linalg.svd(connected, compute_uv=False))[::-1]
    determinant = float(np.linalg.det(connected))
    relation_power = float(np.sum(connected**2))
    local_power = float(np.sum(a**2) + np.sum(b**2))
    denominator = relation_power + local_power
    return {
        "a": a,
        "b": b,
        "joint": tensor,
        "independent": independent,
        "connected": connected,
        "ara9": ara,
        "singular": singular,
        "retained": int(np.sum(singular >= 0.5)),
        "determinant": determinant,
        "closure": float(abs(determinant) ** (1.0 / 3.0)),
        "balance": float(singular[2] / singular[0]) if singular[0] else 0.0,
        "dominance": relation_power / denominator if denominator else 0.0,
        "relation_power": relation_power,
        "local_power": local_power,
        "affine_residual": float(np.max(np.abs(connected - (1.0 - ara)))),
    }


def from_expectations(exp: dict[str, float]) -> dict[str, object]:
    a = np.asarray([exp["XI"], exp["YI"], exp["ZI"]], dtype=float)
    b = np.asarray([exp["IX"], exp["IY"], exp["IZ"]], dtype=float)
    tensor = np.asarray([[exp[label] for label in row] for row in LABELS], dtype=float)
    return relation(a, b, tensor)


def close(left: float, right: float, tolerance: float = TOL) -> bool:
    return bool(abs(float(left) - float(right)) <= tolerance)


def rotation(axis: str, angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    if axis == "X":
        return np.asarray([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=float)
    if axis == "Y":
        return np.asarray([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=float)
    return np.asarray([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=float)


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = None) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    results = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    q5 = json.loads(Q5_RESULTS.read_text(encoding="utf-8"))
    q6b = json.loads(Q6B_RESULTS.read_text(encoding="utf-8"))

    expected_protocol = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    check("protocol_sha256", digest(PROTOCOL) == expected_protocol)
    check(
        "results_protocol_sha256",
        results["source"]["protocol_sha256"] == expected_protocol,
    )
    check(
        "q5_results_sha256",
        results["source"]["q5_results_sha256"] == digest(Q5_RESULTS),
    )
    check(
        "q6b_results_sha256",
        results["source"]["q6b_results_sha256"] == digest(Q6B_RESULTS),
    )
    check("q5_upstream_supported", q5["verdict"] == "SUPPORTED")
    check("q6b_upstream_supported", q6b["verdict"] == "SUPPORTED")

    prepared: dict[str, dict[str, float]] = {state: {} for state in BELL}
    with Q5_PROJECTIONS.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            prepared[row["state"]][row["projection"]] = float(row["expectation"])
    for state in BELL:
        check(f"{state}_projection_count", len(prepared[state]) == 15)
        for label, value in prepared[state].items():
            check(
                f"{state}_{label}_q5_projection_matches_json",
                close(value, q5["states"][state]["expectations"][label]),
            )

    all_exp = dict(prepared)
    for control, weights in WEIGHTS.items():
        labels = tuple(next(iter(prepared.values())).keys())
        all_exp[control] = {
            label: sum(
                weights[state] * prepared[state][label] for state in weights
            )
            for label in labels
        }
    raw = {entity: from_expectations(all_exp[entity]) for entity in ENTITIES}

    physical = {}
    for entity in ENTITIES:
        source = q6b["entities"][entity]
        local = source["local_expectations"]
        a = np.asarray([local["XI"], local["YI"], local["ZI"]], dtype=float)
        b = np.asarray([local["IX"], local["IY"], local["IZ"]], dtype=float)
        physical[entity] = relation(a, b, np.asarray(source["tensor"], dtype=float))

    matrix_rows = {}
    with MATRICES_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            matrix_rows[
                (row["layer"], row["entity"], row["axis_a"], row["axis_b"])
            ] = row
    check("matrix_row_count", len(matrix_rows) == 126, len(matrix_rows))

    metric_rows = {}
    with METRICS_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            metric_rows[(row["layer"], row["entity"])] = row
    check("metric_row_count", len(metric_rows) == 14, len(metric_rows))

    for layer, source_metrics in (("raw_linear", raw), ("physical", physical)):
        result_key = "raw_entities" if layer == "raw_linear" else "physical_entities"
        for entity in ENTITIES:
            metrics = source_metrics[entity]
            result_entity = results[result_key][entity]
            for i, left in enumerate(AXES):
                for j, right in enumerate(AXES):
                    row = matrix_rows[(layer, entity, left, right)]
                    expected_cells = {
                        "joint_value": metrics["joint"][i, j],
                        "independent_child_product": metrics["independent"][i, j],
                        "connected_relation": metrics["connected"][i, j],
                        "ara9_coordinate": metrics["ara9"][i, j],
                    }
                    for field, expected_value in expected_cells.items():
                        check(
                            f"{layer}_{entity}_{left}{right}_{field}",
                            close(float(row[field]), expected_value),
                        )
            metric_row = metric_rows[(layer, entity)]
            scalar_pairs = {
                "s1": metrics["singular"][0],
                "s2": metrics["singular"][1],
                "s3": metrics["singular"][2],
                "determinant": metrics["determinant"],
                "closure_strength": metrics["closure"],
                "directional_balance": metrics["balance"],
                "relation_dominance_share": metrics["dominance"],
                "relation_power": metrics["relation_power"],
                "local_power": metrics["local_power"],
            }
            for field, expected_value in scalar_pairs.items():
                check(
                    f"{layer}_{entity}_{field}_csv",
                    close(float(metric_row[field]), expected_value),
                )
            check(
                f"{layer}_{entity}_retained_csv",
                int(metric_row["retained_directions_at_0p50"])
                == metrics["retained"],
            )
            check(
                f"{layer}_{entity}_connected_json",
                np.allclose(
                    np.asarray(result_entity["connected"], dtype=float),
                    metrics["connected"],
                    atol=TOL,
                    rtol=0,
                ),
            )
            check(
                f"{layer}_{entity}_ara9_json",
                np.allclose(
                    np.asarray(result_entity["ara9"], dtype=float),
                    metrics["ara9"],
                    atol=TOL,
                    rtol=0,
                ),
            )

    bootstrap_rows: dict[str, list[dict[str, float]]] = {entity: [] for entity in ENTITIES}
    with BOOTSTRAP_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            bootstrap_rows[row["entity"]].append(
                {
                    "replicate": int(row["replicate"]),
                    "retained": int(row["retained"]),
                    "determinant": float(row["determinant"]),
                    "closure": float(row["closure"]),
                    "balance": float(row["balance"]),
                    "relation_dominance": float(row["relation_dominance"]),
                    "s1": float(row["s1"]),
                    "s2": float(row["s2"]),
                    "s3": float(row["s3"]),
                }
            )
    check(
        "bootstrap_total_rows",
        sum(len(rows) for rows in bootstrap_rows.values()) == 14000,
    )
    for entity, rows in bootstrap_rows.items():
        check(f"{entity}_bootstrap_rows", len(rows) == 2000, len(rows))
        check(
            f"{entity}_bootstrap_replicates_unique",
            sorted(row["replicate"] for row in rows) == list(range(2000)),
        )
        summary = results["bootstrap"]["summary"][entity]
        retained_fraction = np.mean(
            [row["retained"] == EXPECTED[entity] for row in rows]
        )
        negative_fraction = np.mean([row["determinant"] < 0 for row in rows])
        check(
            f"{entity}_bootstrap_retained_fraction",
            close(retained_fraction, summary["fraction_expected_retained"]),
        )
        check(
            f"{entity}_bootstrap_negative_fraction",
            close(negative_fraction, summary["fraction_negative_determinant"]),
        )
        for source_name, summary_name in (
            ("s1", "s1_95ci"),
            ("s2", "s2_95ci"),
            ("s3", "s3_95ci"),
            ("determinant", "determinant_95ci"),
            ("closure", "closure_95ci"),
            ("balance", "balance_95ci"),
            ("relation_dominance", "relation_dominance_95ci"),
        ):
            observed = np.percentile([row[source_name] for row in rows], [2.5, 97.5])
            check(
                f"{entity}_{summary_name}",
                np.allclose(
                    observed,
                    np.asarray(summary[summary_name], dtype=float),
                    atol=TOL,
                    rtol=0,
                ),
            )

    raw_sequence = [raw[entity]["retained"] for entity in ENTITIES]
    physical_sequence = [physical[entity]["retained"] for entity in ENTITIES]
    expected_sequence = [3, 3, 3, 3, 1, 1, 0]
    independent_gate_pass = {
        "R1_affine_recovery": max(
            raw[entity]["affine_residual"] for entity in ENTITIES
        )
        <= TOL,
        "R2_bell_three_retained": raw_sequence[:4] == [3, 3, 3, 3],
        "R3_bell_s3_at_least_0p50": all(
            raw[entity]["singular"][2] >= 0.5 for entity in BELL
        ),
        "R4_classical_one_retained": raw_sequence[4:6] == [1, 1],
        "R5_uniform_zero_retained": raw_sequence[6] == 0,
        "R6_exact_ladder": raw_sequence == expected_sequence,
        "R7_closure_separation": all(
            raw[entity]["closure"] >= 0.75 for entity in BELL
        )
        and all(
            raw[entity]["closure"] <= 0.30 for entity in (*CLASSICAL, UNIFORM)
        ),
        "R8_directional_balance": all(
            raw[entity]["balance"] >= 0.70 for entity in BELL
        )
        and all(raw[entity]["balance"] <= 0.15 for entity in CLASSICAL),
        "R9_relation_dominance": all(
            raw[entity]["dominance"] >= 0.95 for entity in BELL
        ),
        "R10_bell_negative_determinant": all(
            raw[entity]["determinant"] < 0 for entity in BELL
        ),
        "B1_bell_bootstrap_stability": all(
            np.mean([row["retained"] == 3 for row in bootstrap_rows[entity]]) >= 0.95
            and np.mean(
                [row["determinant"] < 0 for row in bootstrap_rows[entity]]
            )
            >= 0.95
            for entity in BELL
        ),
        "B2_control_bootstrap_stability": all(
            np.mean(
                [
                    row["retained"] == EXPECTED[entity]
                    for row in bootstrap_rows[entity]
                ]
            )
            >= 0.90
            for entity in (*CLASSICAL, UNIFORM)
        ),
        "P1_physical_exact_ladder": physical_sequence == expected_sequence,
        "P2_raw_physical_agreement": raw_sequence == physical_sequence,
    }

    rx = rotation("X", math.pi / 5)
    ry = rotation("Y", math.pi / 4)
    rz = rotation("Z", math.pi / 3)
    pairs = ((rx, ry), (ry, rz), (rz, rx), (rz @ ry, rx @ rz))
    max_rotation_residual = 0.0
    for entity in ENTITIES:
        base = raw[entity]
        base_vector = np.asarray(
            [
                *base["singular"],
                base["closure"],
                base["balance"],
                base["dominance"],
                base["determinant"],
            ]
        )
        for left, right in pairs:
            rotated = relation(
                left @ base["a"],
                right @ base["b"],
                left @ base["joint"] @ right.T,
            )
            rotated_vector = np.asarray(
                [
                    *rotated["singular"],
                    rotated["closure"],
                    rotated["balance"],
                    rotated["dominance"],
                    rotated["determinant"],
                ]
            )
            max_rotation_residual = max(
                max_rotation_residual,
                float(np.max(np.abs(base_vector - rotated_vector))),
            )
    independent_gate_pass["I1_rotation_invariance"] = max_rotation_residual <= TOL

    rank_one_ok = True
    for entity in BELL:
        u, singular, vt = np.linalg.svd(raw[entity]["connected"])
        compressed = singular[0] * np.outer(u[:, 0], vt[0, :])
        compressed_metrics = relation(np.zeros(3), np.zeros(3), compressed)
        rank_one_ok = rank_one_ok and compressed_metrics["retained"] == 1
        rank_one_ok = rank_one_ok and abs(compressed_metrics["determinant"]) <= TOL
    independent_gate_pass["I2_rank_one_destruction"] = rank_one_ok

    for gate_name, passed in independent_gate_pass.items():
        check(
            f"{gate_name}_independent",
            passed,
        )
        check(
            f"{gate_name}_matches_primary",
            bool(results["gates"][gate_name]["pass"]) == bool(passed),
        )

    check("result_gate_count", results["gates_total"] == 16)
    check(
        "result_gate_passed_count",
        results["gates_passed"] == sum(independent_gate_pass.values()),
    )
    check(
        "result_verdict",
        results["verdict"]
        == (
            "CALIBRATED"
            if all(independent_gate_pass.values())
            else "NOT CALIBRATED"
        ),
    )
    check("figure_png_exists", FIGURE_PNG.exists() and FIGURE_PNG.stat().st_size > 0)
    check("figure_svg_exists", FIGURE_SVG.exists() and FIGURE_SVG.stat().st_size > 0)
    with Image.open(FIGURE_PNG) as image:
        check("figure_png_dimensions", image.size == (1600, 1490), image.size)

    failures = [item for item in checks if not item["pass"]]
    output = {
        "protocol_id": "Q24-ARA9-BELL-RELATION-v1",
        "validator": "independent CSV/JSON reconstruction; does not import primary runner",
        "verdict": "PASS" if not failures else "FAIL",
        "checks_passed": len(checks) - len(failures),
        "checks_total": len(checks),
        "failures": failures,
        "independent_result": {
            "raw_ladder": raw_sequence,
            "physical_ladder": physical_sequence,
            "bell_relation_dominance": {
                entity: raw[entity]["dominance"] for entity in BELL
            },
            "bell_closure_strength": {
                entity: raw[entity]["closure"] for entity in BELL
            },
            "maximum_rotation_invariant_residual": max_rotation_residual,
        },
    }
    VALIDATION_JSON.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"Q24 independent validation: {output['verdict']} "
        f"({output['checks_passed']}/{output['checks_total']})"
    )
    if failures:
        for failure in failures:
            print("FAIL", failure)


if __name__ == "__main__":
    main()

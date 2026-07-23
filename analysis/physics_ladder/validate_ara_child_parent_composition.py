#!/usr/bin/env python3
"""Independent validation for the frozen ARA child-to-parent composition test."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "CHILD_PARENT_COMPOSITION_PROTOCOL_2026-07-23.md"
RESULTS = HERE / "ARA_CHILD_PARENT_COMPOSITION_RESULTS.json"
SUMMARY = HERE / "ARA_CHILD_PARENT_COMPOSITION_SUMMARY.csv"
SAMPLE = HERE / "ARA_CHILD_PARENT_COMPOSITION_BOUNDED_SAMPLE.csv"
ARTIFACT = HERE / "ARA_CHILD_PARENT_COMPOSITION_REPORT_ARTIFACT.json"
VALIDATION = HERE / "ARA_CHILD_PARENT_COMPOSITION_VALIDATION.json"


def load_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def accounts(left: np.ndarray, right: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    accumulation = np.maximum(left, 0.0) + np.maximum(-right, 0.0)
    release = np.maximum(-left, 0.0) + np.maximum(right, 0.0)
    return accumulation, release


def check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}


def main() -> None:
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    summary_rows = load_csv(SUMMARY)
    sample_rows = load_csv(SAMPLE)
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    checks: list[dict] = []

    protocol_hash = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    checks.append(
        check(
            "saved result is bound to the frozen protocol",
            results["protocol_sha256"] == protocol_hash,
            f"protocol_sha256={protocol_hash}",
        )
    )

    model_names = {row["model"] for row in summary_rows}
    expected_names = {
        "Classical string energy",
        "Lossless transmission line",
        "Free Gaussian probability",
    }
    checks.append(
        check(
            "all three preregistered models are present",
            model_names == expected_names,
            f"models={sorted(model_names)}",
        )
    )

    valid_counts = [int(row["valid_samples"]) for row in summary_rows]
    checks.append(
        check(
            "all planned samples were retained",
            valid_counts == [4097, 4097, 4097],
            f"valid_counts={valid_counts}",
        )
    )

    max_errors = [float(row["max_abs_error_frozen"]) for row in summary_rows]
    checks.append(
        check(
            "frozen operator meets the preregistered tolerance",
            max(max_errors) <= 5e-12,
            f"max_error={max(max_errors):.3e}",
        )
    )

    orientation_errors = [
        float(row["max_abs_orientation_error"]) for row in summary_rows
    ]
    checks.append(
        check(
            "orientation reversal obeys x_prime = 2 - x",
            max(orientation_errors) <= 5e-12,
            f"max_orientation_error={max(orientation_errors):.3e}",
        )
    )

    control_dominance = all(
        float(row["mean_abs_error_naive"]) > float(row["mean_abs_error_frozen"])
        and float(row["mean_abs_error_no_internal"])
        > float(row["mean_abs_error_frozen"])
        for row in summary_rows
    )
    checks.append(
        check(
            "both flattening controls are worse in every model",
            control_dominance,
            "naive and unclosed activity-weighted controls compared model by model",
        )
    )

    classical_residual = float(
        next(
            row["continuity_residual_max"]
            for row in summary_rows
            if row["model"] == "Classical string energy"
        )
    )
    em_residual = float(
        next(
            row["continuity_residual_max"]
            for row in summary_rows
            if row["model"] == "Lossless transmission line"
        )
    )
    quantum_residual = float(
        next(
            row["continuity_residual_max"]
            for row in summary_rows
            if row["model"] == "Free Gaussian probability"
        )
    )
    checks.append(
        check(
            "native continuity equations meet their tolerances",
            classical_residual <= 5e-12
            and em_residual <= 5e-12
            and quantum_residual <= 1e-6,
            (
                f"classical={classical_residual:.3e}, "
                f"em={em_residual:.3e}, quantum_fd={quantum_residual:.3e}"
            ),
        )
    )

    sample_diffs = []
    field_diffs = []
    for row in sample_rows:
        left = np.array([float(row["flux_left"])])
        middle = np.array([float(row["flux_interface"])])
        right = np.array([float(row["flux_right"])])
        a1, r1 = accounts(left, middle)
        a2, r2 = accounts(middle, right)
        parent_a, parent_r = accounts(left, right)
        internal = np.abs(middle)
        predicted = 2.0 * (r1 + r2 - internal) / (
            a1 + r1 + a2 + r2 - 2.0 * internal
        )
        direct = 2.0 * parent_r / (parent_a + parent_r)
        sample_diffs.append(float(abs(predicted[0] - direct[0])))
        field_diffs.extend(
            [
                abs(float(row["child_1_accumulation"]) - a1[0]),
                abs(float(row["child_1_release"]) - r1[0]),
                abs(float(row["child_2_accumulation"]) - a2[0]),
                abs(float(row["child_2_release"]) - r2[0]),
                abs(float(row["parent_ara_frozen"]) - predicted[0]),
                abs(float(row["parent_ara_direct"]) - direct[0]),
            ]
        )
    checks.append(
        check(
            "bounded saved rows independently reconstruct",
            max(sample_diffs + field_diffs) <= 5e-12,
            f"max_saved_row_difference={max(sample_diffs + field_diffs):.3e}",
        )
    )

    rng = np.random.default_rng(20260723)
    flux_left = rng.normal(size=100_000)
    flux_middle = rng.normal(size=100_000)
    flux_right = rng.normal(size=100_000)
    a1, r1 = accounts(flux_left, flux_middle)
    a2, r2 = accounts(flux_middle, flux_right)
    pa, pr = accounts(flux_left, flux_right)
    internal = np.abs(flux_middle)
    parent_total = pa + pr
    valid = parent_total > 1e-12
    randomized_pred = 2.0 * (r1 + r2 - internal) / (
        a1 + r1 + a2 + r2 - 2.0 * internal
    )
    randomized_direct = 2.0 * pr / parent_total
    randomized_error = float(
        np.max(np.abs(randomized_pred[valid] - randomized_direct[valid]))
    )
    checks.append(
        check(
            "100,000 independent signed-flux triples satisfy the operator",
            randomized_error <= 5e-12,
            f"max_randomized_error={randomized_error:.3e}",
        )
    )

    reverse_pred = 2.0 * (a1 + a2 - internal) / (
        a1 + r1 + a2 + r2 - 2.0 * internal
    )
    reverse_error = float(
        np.max(np.abs(reverse_pred[valid] - (2.0 - randomized_pred[valid])))
    )
    checks.append(
        check(
            "randomized orientation reversal is exact",
            reverse_error <= 5e-12,
            f"max_randomized_reversal_error={reverse_error:.3e}",
        )
    )

    manifest = artifact["manifest"]
    snapshot = artifact["snapshot"]
    title = manifest["title"]
    first_block = manifest["blocks"][0]
    checks.append(
        check(
            "reader artifact has a matching visible title",
            first_block.get("type") == "markdown"
            and first_block.get("body") == f"# {title}",
            f"title={title}",
        )
    )

    dataset_sizes = {
        key: len(value) for key, value in snapshot["datasets"].items()
    }
    checks.append(
        check(
            "artifact snapshot stays within row bounds",
            all(size <= 2000 for size in dataset_sizes.values()),
            f"dataset_sizes={dataset_sizes}",
        )
    )

    chart_ids = {chart["id"] for chart in manifest.get("charts", [])}
    checks.append(
        check(
            "report includes control and holdout visuals",
            chart_ids == {"method-error-orders", "quantum-holdout-trace"},
            f"chart_ids={sorted(chart_ids)}",
        )
    )

    table_fields = {
        column["field"]
        for table in manifest.get("tables", [])
        for column in table.get("columns", [])
    }
    table_sorts_valid = all(
        table["defaultSort"]["field"]
        in {column["field"] for column in table.get("columns", [])}
        for table in manifest.get("tables", [])
    )
    checks.append(
        check(
            "table sort fields are declared visible columns",
            table_sorts_valid,
            f"visible_fields={sorted(table_fields)}",
        )
    )

    report_text = "\n".join(
        block.get("body", "")
        for block in manifest["blocks"]
        if block.get("type") == "markdown"
    ).lower()
    checks.append(
        check(
            "report preserves the universality fence",
            "does not establish new dynamics or prove universal fractality"
            in report_text
            and "cannot by itself distinguish ara from ordinary conservation accounting"
            in report_text,
            "new-dynamics and ordinary-conservation limits are both explicit",
        )
    )

    passed = sum(int(item["passed"]) for item in checks)
    output = {
        "status": "passed" if passed == len(checks) else "failed",
        "passed": passed,
        "total": len(checks),
        "confidence": (
            "Ready to share as an exact reconstruction/formalization result; "
            "not as evidence of new dynamics."
        ),
        "max_randomized_operator_error": randomized_error,
        "max_randomized_reversal_error": reverse_error,
        "checks": checks,
    }
    VALIDATION.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(output, indent=2, ensure_ascii=False))
    if output["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

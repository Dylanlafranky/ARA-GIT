#!/usr/bin/env python3
"""Build the bounded Data Analytics report payload for the hidden-Other test."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SUMMARY = ROOT / "ARA_HIDDEN_OTHER_RESIDUAL_SUMMARY.csv"
SAMPLE = ROOT / "ARA_HIDDEN_OTHER_RESIDUAL_BOUNDED_SAMPLE.csv"
OUTPUT = ROOT / "ARA_HIDDEN_OTHER_RESIDUAL_REPORT_ARTIFACT.json"


def number(row: dict[str, str], field: str) -> float:
    return float(row[field])


def main() -> None:
    with SUMMARY.open(newline="", encoding="utf-8") as handle:
        summary = list(csv.DictReader(handle))
    with SAMPLE.open(newline="", encoding="utf-8") as handle:
        sample = list(csv.DictReader(handle))

    headline = [
        {
            "models_passed": 3,
            "models_total": 3,
            "scored_samples": sum(int(row["scored_samples"]) for row in summary),
            "locations_correct": 3,
            "minimum_sign_accuracy": min(number(row, "sign_accuracy") for row in summary),
            "maximum_source_nrmse": max(number(row, "source_nrmse") for row in summary),
        }
    ]

    method_errors = []
    for row in summary:
        methods = [
            ("ARA residual", number(row, "source_nrmse"), "primary"),
            ("No Other", number(row, "no_other_control_nrmse"), "control"),
            ("Parent only", number(row, "parent_only_control_nrmse"), "control"),
            ("Wrong location", number(row, "wrong_location_control_nrmse"), "control"),
        ]
        for method, nrmse, method_class in methods:
            method_errors.append(
                {
                    "model": row["model"],
                    "domain": row["domain"],
                    "test_role": row["test_role"],
                    "method": method,
                    "method_class": method_class,
                    "source_nrmse": nrmse,
                    "accuracy_orders": -math.log10(max(nrmse, 1e-18)),
                    "native_location": row["native_hidden_location"],
                    "scored_samples": int(row["scored_samples"]),
                }
            )

    summary_table = []
    for row in summary:
        summary_table.append(
            {
                "model": row["model"],
                "role": row["test_role"],
                "hidden_location": row["native_hidden_location"],
                "location_correct": row["location_correct"],
                "sign_accuracy": number(row, "sign_accuracy"),
                "correlation": number(row, "source_correlation"),
                "source_nrmse": number(row, "source_nrmse"),
                "integrated_relative_error": number(row, "integrated_relative_error"),
                "inactive_rms_fraction": number(row, "inactive_rms_fraction"),
                "scored_samples": int(row["scored_samples"]),
            }
        )

    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in sample:
        grouped[(row["model"], row["identity"])].append(row)

    hidden_peak = {}
    hidden_mean_abs = {}
    for row in summary:
        key = (row["model"], row["native_hidden_location"])
        native = [abs(number(item, "native_other_revealed")) for item in grouped[key]]
        hidden_peak[row["model"]] = max(native)
        hidden_mean_abs[row["model"]] = sum(native) / len(native)

    locations = []
    for (model, identity), rows in grouped.items():
        mean_abs = sum(abs(number(row, "estimated_other")) for row in rows) / len(rows)
        locations.append(
            {
                "model": model,
                "identity": identity,
                "location_label": f"{model} — {identity}",
                "is_native_hidden_location": rows[0]["is_native_hidden_location"] == "True",
                "mean_absolute_residual": mean_abs,
                "relative_location_strength": mean_abs / hidden_mean_abs[model],
                "native_peak": hidden_peak[model],
                "sample_rows": len(rows),
            }
        )

    traces = []
    for row in summary:
        model = row["model"]
        location = row["native_hidden_location"]
        rows = grouped[(model, location)]
        t_min = min(number(item, "time") for item in rows)
        t_max = max(number(item, "time") for item in rows)
        peak = hidden_peak[model]
        trace_stride = max(1, len(rows) // 12)
        trace_rows = rows[::trace_stride]
        if trace_rows[-1] is not rows[-1]:
            trace_rows.append(rows[-1])
        for item in trace_rows:
            normalized_time = (number(item, "time") - t_min) / (t_max - t_min)
            for kind, field in (
                ("Recovered", "estimated_other"),
                ("Native", "native_other_revealed"),
            ):
                traces.append(
                    {
                        "model": model,
                        "domain": row["domain"],
                        "test_role": row["test_role"],
                        "hidden_location": location,
                        "source_kind": kind,
                        "series": f"{model} — {kind}",
                        "normalized_time": normalized_time,
                        "normalized_source": number(item, field) / peak,
                        "native_peak": peak,
                        "absolute_recovery_error": number(item, "absolute_recovery_error"),
                    }
                )

    source = {
        "id": "ara-hidden-other-run",
        "label": "Frozen hidden-Other residual outputs",
        "path": str(SUMMARY),
        "query": {
            "id": "ara-hidden-other-summary-v1",
            "language": "sql",
            "engine": "duckdb",
            "description": (
                "Reads the frozen summary and bounded deterministic samples produced by "
                "the preregistered residual script."
            ),
            "sql": (
                "SELECT * FROM read_csv_auto("
                "'analysis/physics_ladder/ARA_HIDDEN_OTHER_RESIDUAL_SUMMARY.csv');"
            ),
            "tables_used": [
                "analysis/physics_ladder/ARA_HIDDEN_OTHER_RESIDUAL_SUMMARY.csv",
                "analysis/physics_ladder/ARA_HIDDEN_OTHER_RESIDUAL_BOUNDED_SAMPLE.csv",
            ],
            "filters": [
                "Fourth-order derivative-supported interior samples only",
                "No smoothing, Fourier decomposition, fitted regression or learned component",
            ],
            "metric_definitions": [
                "source_nrmse = RMSE(recovered source, native source) / peak absolute native source",
                "accuracy_orders = -log10(source_nrmse)",
                "relative_location_strength = mean absolute recovered residual / mean absolute residual at the native hidden location",
                "sign_accuracy uses active native-source points above 1e-6 of native peak",
            ],
        },
    }

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "ARA Hidden Other Residual Test",
        "description": (
            "Frozen controlled test of whether a boundary-aware continuity residual can "
            "localize a concealed source, sink or relation leak."
        ),
        "generatedAt": "2026-07-23T20:30:00+10:00",
        "sources": [source],
        "cards": [
            {
                "id": "models-card",
                "description": "Models meeting every frozen location, sign and magnitude threshold.",
                "dataset": "headline",
                "sourceId": "ara-hidden-other-run",
                "metrics": [
                    {"label": "Passed", "field": "models_passed", "format": "number"},
                    {"label": "Total", "field": "models_total", "format": "number"},
                ],
            },
            {
                "id": "samples-card",
                "description": "All derivative-supported time samples across the three systems.",
                "dataset": "headline",
                "sourceId": "ara-hidden-other-run",
                "metrics": [
                    {"label": "Samples", "field": "scored_samples", "format": "number"}
                ],
            },
            {
                "id": "locations-card",
                "description": "Correct child or relation selected by integrated absolute residual.",
                "dataset": "headline",
                "sourceId": "ara-hidden-other-run",
                "metrics": [
                    {"label": "Correct", "field": "locations_correct", "format": "number"},
                    {"label": "Systems", "field": "models_total", "format": "number"},
                ],
            },
        ],
        "charts": [
            {
                "id": "method-accuracy-chart",
                "title": "Source recovery accuracy by method",
                "description": (
                    "Higher values indicate more orders of peak-normalized source accuracy."
                ),
                "type": "bar",
                "dataset": "method_errors",
                "sourceId": "ara-hidden-other-run",
                "encodings": {
                    "x": {"field": "model", "type": "nominal"},
                    "y": {"field": "accuracy_orders", "type": "quantitative"},
                    "color": {"field": "method", "type": "nominal"},
                },
                "options": {"orientation": "vertical", "grouping": "grouped"},
            },
            {
                "id": "location-chart",
                "title": "Recovered residual strength by identity",
                "description": (
                    "The true hidden child or relation is normalized to approximately one "
                    "inside each model."
                ),
                "type": "bar",
                "dataset": "locations",
                "sourceId": "ara-hidden-other-run",
                "encodings": {
                    "x": {"field": "location_label", "type": "nominal"},
                    "y": {"field": "relative_location_strength", "type": "quantitative"},
                },
                "options": {"orientation": "vertical", "grouping": "single"},
            },
            {
                "id": "waveform-chart",
                "title": "Recovered and native hidden-source waveforms",
                "description": (
                    "Time and source magnitude are normalized within each system; native "
                    "and recovered traces overlap."
                ),
                "type": "line",
                "dataset": "traces",
                "sourceId": "ara-hidden-other-run",
                "encodings": {
                    "x": {"field": "normalized_time", "type": "quantitative"},
                    "y": {"field": "normalized_source", "type": "quantitative"},
                    "color": {"field": "series", "type": "nominal"},
                },
                "options": {"points": "never"},
            },
        ],
        "tables": [
            {
                "id": "results-table",
                "title": "Frozen system results",
                "description": "Exact locations and primary recovery errors for every system.",
                "dataset": "summary",
                "sourceId": "ara-hidden-other-run",
                "columns": [
                    {"field": "model", "label": "System", "type": "text"},
                    {"field": "role", "label": "Role", "type": "text"},
                    {"field": "hidden_location", "label": "Hidden location", "type": "text"},
                    {"field": "sign_accuracy", "label": "Sign accuracy", "type": "number"},
                    {"field": "source_nrmse", "label": "Source NRMSE", "type": "number"},
                    {
                        "field": "integrated_relative_error",
                        "label": "Integral error",
                        "type": "number",
                    },
                    {"field": "scored_samples", "label": "Samples", "type": "number"},
                ],
                "defaultSort": {"field": "source_nrmse", "direction": "desc"},
            }
        ],
        "blocks": [
            {"id": "title", "type": "markdown", "body": "# ARA Hidden Other Residual Test"},
            {
                "id": "executive-summary",
                "type": "markdown",
                "sourceId": "ara-hidden-other-run",
                "body": (
                    "## Executive Summary\n\n"
                    "The frozen residual `s_hat_i = dq_i/dt - g_i` recovered the concealed "
                    "`Other` term in all three controlled systems without receiving the "
                    "native damping, resistance or quantum-decay coefficient. It found the "
                    "correct child or relation, recovered sink direction at every active "
                    "sample and matched each hidden waveform to numerical precision. This "
                    "is a strong controlled inverse diagnostic—not forward prediction of a "
                    "new law or an unseen real-world source."
                ),
            },
            {
                "id": "headline-metrics",
                "type": "metric-strip",
                "cardIds": ["models-card", "samples-card", "locations-card"],
            },
            {
                "id": "accuracy-heading",
                "type": "markdown",
                "body": (
                    "## Recovery Accuracy\n\n"
                    "The plotted score is the number of decimal orders by which the recovered "
                    "waveform approaches the native source after normalization to its peak. "
                    "It is used because the primary residual and controls differ by many orders."
                ),
            },
            {"id": "accuracy-block", "type": "chart", "chartId": "method-accuracy-chart"},
            {
                "id": "localization-heading",
                "type": "markdown",
                "body": (
                    "## Localization\n\n"
                    "A useful `Other` account must say where closure fails. The oscillator and "
                    "quantum losses stayed on a child; Joule loss stayed on the coupling relation."
                ),
            },
            {"id": "location-block", "type": "chart", "chartId": "location-chart"},
            {
                "id": "waveform-heading",
                "type": "markdown",
                "body": (
                    "## Time-resolved Recovery\n\n"
                    "The estimator recovered the changing magnitude, not only a total deficit. "
                    "Native and recovered traces lie on top of one another at this scale."
                ),
            },
            {"id": "waveform-block", "type": "chart", "chartId": "waveform-chart"},
            {
                "id": "results-heading",
                "type": "markdown",
                "body": (
                    "## System Results\n\n"
                    "All derivative-supported samples were scored; no favorable time window "
                    "was selected after the run."
                ),
            },
            {"id": "results-block", "type": "table", "tableId": "results-table"},
            {
                "id": "interpretation",
                "type": "markdown",
                "body": (
                    "## Interpretation Boundary\n\n"
                    "The result operationalizes `Other`: once storage, boundary and named "
                    "internal transfers are declared, the signed remainder stays attached to "
                    "the child or relation where the account fails to close. Exact recovery is "
                    "nevertheless expected for accurate noiseless continuity data. The test "
                    "does not discover the native loss law in advance, prove universal "
                    "fractality or establish superiority over state-estimation methods.\n\n"
                    "### Next rung\n\n"
                    "Infer a compact residual law on development systems, freeze it, and "
                    "predict a held-out `Other` waveform before observing the held-out "
                    "stored-quantity change."
                ),
            },
        ],
    }

    artifact = {
        "surface": "report",
        "manifest": manifest,
        "snapshot": {
            "version": 1,
            "status": "ready",
            "generatedAt": "2026-07-23T20:30:00+10:00",
            "datasets": {
                "headline": headline,
                "method_errors": method_errors,
                "locations": locations,
                "traces": traces,
                "summary": summary_table,
            },
        },
        "sources": [source],
    }
    OUTPUT.write_text(
        json.dumps(artifact, ensure_ascii=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()

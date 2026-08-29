#!/usr/bin/env python3
"""Build the canonical portable-report artifact for T419."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUTPUT = HERE / "artifact.json"


def read_csv(name: str) -> list[dict]:
    with (RESULTS / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def number(value) -> float:
    return float(value)


def field_effects(stage: str) -> list[dict]:
    rows = read_csv(f"T419_{stage}_SEQUENCE_METRICS.csv")
    output = []
    for arm in ("U_to_R", "R_to_U"):
        selected = [row for row in rows if row["arm"] == arm]
        for field in sorted({number(row["field_G"]) for row in selected}):
            field_rows = [row for row in selected if number(row["field_G"]) == field]
            output.append({
                "stage": stage.title(),
                "field_G": field,
                "arm": "Openness -> later closure" if arm == "U_to_R" else "Closure -> later openness",
                "effect": float(np.median([number(row["baseline_minus_transfer"]) for row in field_rows])),
                "rf_on_effect": number(next(row["baseline_minus_transfer"] for row in field_rows if row["period"] == "RF on")),
                "rf_off_effect": number(next(row["baseline_minus_transfer"] for row in field_rows if row["period"] == "RF off")),
                "run_periods": len(field_rows),
            })
    return output


def error_rows(stage: str, result: dict) -> list[dict]:
    output = []
    labels = {
        "baseline_mse": "Own-history baseline",
        "transfer_mse": "Correct transfer",
        "wrong_frequency_mse": "Wrong frequency",
        "reverse_mse": "Reversed order",
    }
    for arm, arm_label in (("U_to_R", "Openness -> later closure"), ("R_to_U", "Closure -> later openness")):
        errors = result["arms"][arm]["errors"]
        for key, label in labels.items():
            output.append({
                "stage": stage.title(),
                "arm": arm_label,
                "model": label,
                "mse": errors[key],
                "prediction_rows": result["arms"][arm]["prediction_rows"],
            })
    return output


def example_rows() -> list[dict]:
    choices = (
        ("VALIDATION", "EMU00070022", "RF on", "Validation · 284 G · RF on"),
        ("HOLDOUT", "EMU00070275", "RF on", "Holdout · 2160 G · RF on"),
    )
    output = []
    for stage, run, period, label in choices:
        rows = [
            row for row in read_csv(f"T419_{stage}_TIMELINE.csv")
            if row["run"] == run and row["period"] == period
        ]
        for index, row in enumerate(rows):
            common = {
                "example": label,
                "stage": stage.title(),
                "run": run,
                "period": period,
                "field_G": number(row["field_G"]),
                "time_us": number(row["time_us"]),
                "step": index,
                "openness_U": number(row["openness_U"]),
                "closure_R": number(row["closure_R"]),
                "parent_ARA": number(row["parent_ARA"]),
            }
            output.append({**common, "coordinate": "Openness U", "value": common["openness_U"]})
            output.append({**common, "coordinate": "Closure R", "value": common["closure_R"]})
    return output


def plane_rows() -> list[dict]:
    output = []
    for stage, run, period, label in (
        ("VALIDATION", "EMU00070022", "RF on", "Validation · 284 G"),
        ("HOLDOUT", "EMU00070275", "RF on", "Holdout · 2160 G"),
    ):
        rows = [
            row for row in read_csv(f"T419_{stage}_TIMELINE.csv")
            if row["run"] == run and row["period"] == period
        ]
        for index, row in enumerate(rows):
            output.append({
                "example": label,
                "stage": stage.title(),
                "step": index,
                "time_us": number(row["time_us"]),
                "openness_U": number(row["openness_U"]),
                "closure_R": number(row["closure_R"]),
                "parent_ARA": number(row["parent_ARA"]),
            })
    return output


def lag_rows() -> list[dict]:
    output = []
    for stage in ("VALIDATION", "HOLDOUT"):
        for row in read_csv(f"T419_{stage}_LAG_DIAGNOSTICS.csv"):
            arm_label = "Openness -> closure" if row["arm"] == "U_to_R" else "Closure -> openness"
            output.append({
                "stage": stage.title(),
                "arm": arm_label,
                "series": f"{stage.title()} · {arm_label}",
                "horizon_reads": int(row["horizon_reads"]),
                "horizon_us": number(row["horizon_us_median"]),
                "shared_native_bins": int(row["shared_native_bins"]),
                "window_relation": "Non-overlap primary" if int(row["shared_native_bins"]) == 0 else "Overlapping diagnostic",
                "relative_improvement_pct": number(row["relative_improvement_pct"]),
                "baseline_mse": number(row["baseline_mse"]),
                "transfer_mse": number(row["transfer_mse"]),
                "prediction_rows": int(row["prediction_rows"]),
            })
    return output


def gate_rows(validation: dict, holdout: dict) -> list[dict]:
    output = []
    for stage, result in (("Validation", validation), ("Holdout", holdout)):
        for gate, item in result["gates"].items():
            output.append({
                "stage": stage,
                "gate": gate.replace("G", "G", 1).replace("_", " "),
                "status": "PASS" if item["pass"] else "FAIL",
                "pass_numeric": 1 if item["pass"] else 0,
                "run_period_sequences": result["run_period_sequences"],
                "primary_prediction_rows": result["primary_prediction_rows"],
            })
    return output


def main() -> None:
    generated = datetime.now(timezone.utc).isoformat()
    development = read_json("T419_DEVELOPMENT_RESULTS.json")
    validation = read_json("T419_VALIDATION_RESULTS.json")
    holdout = read_json("T419_HOLDOUT_RESULTS.json")
    audit = read_json("T419_INDEPENDENT_VALIDATION.json")

    hold_r_to_u = holdout["arms"]["R_to_U"]
    hold_improvement = (
        hold_r_to_u["errors"]["baseline_mse"] - hold_r_to_u["errors"]["transfer_mse"]
    ) / hold_r_to_u["errors"]["baseline_mse"]
    val_r_to_u = validation["arms"]["R_to_U"]
    val_improvement = (
        val_r_to_u["errors"]["baseline_mse"] - val_r_to_u["errors"]["transfer_mse"]
    ) / val_r_to_u["errors"]["baseline_mse"]

    cards = [{
        "validation_supported": 1 if validation["stage_supported"] else 0,
        "holdout_supported": 1 if holdout["stage_supported"] else 0,
        "holdout_r_to_u_improvement": hold_improvement,
        "validation_r_to_u_improvement": val_improvement,
        "audit_pass_fraction": audit["checks"] and (audit["checks"] - audit["failed_checks"]) / audit["checks"],
        "primary_horizon_us": holdout["primary_horizon"]["median_us"],
        "shared_native_bins": holdout["primary_horizon"]["shared_native_bins"],
    }]

    errors = error_rows("VALIDATION", validation) + error_rows("HOLDOUT", holdout)
    fields_validation = field_effects("VALIDATION")
    fields_holdout = field_effects("HOLDOUT")
    examples = example_rows()
    plane = plane_rows()
    lags = lag_rows()
    gates = gate_rows(validation, holdout)

    sources = [
        {
            "id": "protocol",
            "label": "T419 frozen protocol",
            "path": "T419_FROZEN_PROTOCOL.md",
            "query": {
                "engine": "filesystem",
                "language": "sql",
                "sql": "SELECT * FROM read_text('T419_FROZEN_PROTOCOL.md')",
                "description": "Read the protocol frozen before development fitting and validation/holdout scoring.",
                "tables_used": ["T419_FROZEN_PROTOCOL.md"],
                "filters": ["Frozen 22 August 2026 before validation and holdout"],
                "metric_definitions": ["Primary horizon = 32 T416 reads = 128 native bins; shared bins = 0"],
            },
        },
        {
            "id": "results",
            "label": "T419 frozen stage results",
            "path": "results/T419_HOLDOUT_RESULTS.json",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "sql": "SELECT 'validation' AS stage, * FROM read_json_auto('results/T419_VALIDATION_RESULTS.json') UNION ALL SELECT 'holdout' AS stage, * FROM read_json_auto('results/T419_HOLDOUT_RESULTS.json')",
                "description": "Combine the separately frozen validation and holdout result summaries.",
                "tables_used": ["results/T419_VALIDATION_RESULTS.json", "results/T419_HOLDOUT_RESULTS.json"],
                "filters": ["Primary non-overlap horizon only for frozen verdicts"],
                "metric_definitions": ["Relative MSE improvement = (baseline MSE - transfer MSE) / baseline MSE"],
            },
        },
        {
            "id": "timeline",
            "label": "T419 independent U/R histories",
            "path": "results/T419_HOLDOUT_TIMELINE.csv",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "sql": "SELECT * FROM read_csv_auto('results/T419_VALIDATION_TIMELINE.csv') UNION ALL SELECT * FROM read_csv_auto('results/T419_HOLDOUT_TIMELINE.csv')",
                "description": "Combine past-only validation and holdout openness/closure histories for the labelled examples.",
                "tables_used": ["results/T419_VALIDATION_TIMELINE.csv", "results/T419_HOLDOUT_TIMELINE.csv"],
                "filters": ["Examples: EMU00070022 RF on and EMU00070275 RF on"],
                "metric_definitions": ["U = 2 L_local/(L_local+L_null)", "R = 2 median lagged phase coherence"],
            },
        },
        {
            "id": "metrics",
            "label": "T419 field-paired prediction metrics",
            "path": "results/T419_HOLDOUT_SEQUENCE_METRICS.csv",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "sql": "SELECT * FROM read_csv_auto('results/T419_VALIDATION_SEQUENCE_METRICS.csv') UNION ALL SELECT * FROM read_csv_auto('results/T419_HOLDOUT_SEQUENCE_METRICS.csv')",
                "description": "Combine run/period metrics and pair RF histories by magnetic field.",
                "tables_used": ["results/T419_VALIDATION_SEQUENCE_METRICS.csv", "results/T419_HOLDOUT_SEQUENCE_METRICS.csv"],
                "filters": ["Primary 32-read non-overlap horizon"],
                "metric_definitions": ["Added information = baseline MSE - transfer MSE; positive favours transfer"],
            },
        },
        {
            "id": "lags",
            "label": "T419 overlap and non-overlap lag diagnostics",
            "path": "results/T419_HOLDOUT_LAG_DIAGNOSTICS.csv",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "sql": "SELECT * FROM read_csv_auto('results/T419_VALIDATION_LAG_DIAGNOSTICS.csv') UNION ALL SELECT * FROM read_csv_auto('results/T419_HOLDOUT_LAG_DIAGNOSTICS.csv')",
                "description": "Compare overlapping diagnostic horizons with the primary fully separated horizon.",
                "tables_used": ["results/T419_VALIDATION_LAG_DIAGNOSTICS.csv", "results/T419_HOLDOUT_LAG_DIAGNOSTICS.csv"],
                "filters": ["Horizon reads in 1,2,4,8,16,24,32"],
                "metric_definitions": ["Shared native bins = max(0,128 - 4*horizon reads)"],
            },
        },
        {
            "id": "audit",
            "label": "T419 independent saved-artifact audit",
            "path": "results/T419_INDEPENDENT_VALIDATION.json",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "sql": "SELECT * FROM read_json_auto('results/T419_INDEPENDENT_VALIDATION.json')",
                "description": "Read independent hash, overlap, complementarity and metric-recomputation checks.",
                "tables_used": ["results/T419_INDEPENDENT_VALIDATION.json"],
                "filters": ["All saved stages"],
                "metric_definitions": ["Audit pass fraction = passed checks / 50 checks"],
            },
        },
    ]

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "T419 — Dynamic Irrationality Di-ARA Handover",
        "description": "Frozen non-overlap test of independent openness and closure histories in a public muoniated-acetone ensemble.",
        "generatedAt": generated,
        "sources": sources,
        "cards": [
            {
                "id": "card_validation",
                "dataset": "cards",
                "sourceId": "results",
                "description": "The complete frozen bidirectional gate across the interleaved 300 K validation fields.",
                "metrics": [{"label": "Validation supported", "field": "validation_supported", "format": "number"}],
            },
            {
                "id": "card_holdout",
                "dataset": "cards",
                "sourceId": "results",
                "description": "The complete frozen bidirectional gate across the 202 K high-field holdout.",
                "metrics": [{"label": "Holdout supported", "field": "holdout_supported", "format": "number"}],
            },
            {
                "id": "card_branch",
                "dataset": "cards",
                "sourceId": "results",
                "description": "Relative aggregate MSE reduction for closure predicting later openness in the high-field holdout.",
                "metrics": [
                    {"label": "Holdout R→U improvement", "field": "holdout_r_to_u_improvement", "format": "percent", "signed": True},
                    {"label": "Validation R→U improvement", "field": "validation_r_to_u_improvement", "format": "percent", "signed": True},
                ],
            },
            {
                "id": "card_audit",
                "dataset": "cards",
                "sourceId": "audit",
                "description": "Saved-artifact hash, overlap, complementarity and metric-recomputation checks passed.",
                "metrics": [{"label": "Audit checks passed", "field": "audit_pass_fraction", "format": "percent"}],
            },
        ],
        "charts": [
            {
                "id": "chart_validation_time",
                "title": "Independent openness and closure histories — validation example",
                "subtitle": "284 G, RF on; each point uses a past-only 128-bin phase history; ARA coordinates on 0–2",
                "showDescription": True,
                "intent": "trend",
                "question": "How do the independently constructed U and R coordinates evolve through ensemble time in the validation regime?",
                "rationale": "A two-series line chart preserves chronology and shows whether apparent exchange is sustained or only a local crossing.",
                "type": "line",
                "dataset": "example_validation",
                "sourceId": "timeline",
                "encodings": {
                    "x": {"field": "time_us", "type": "quantitative", "label": "Corrected ensemble time", "unit": "µs"},
                    "y": {"field": "value", "type": "quantitative", "label": "ARA coordinate", "unit": "0–2"},
                    "color": {"field": "coordinate", "type": "nominal", "label": "Independent coordinate"},
                    "tooltip": [
                        {"field": "time_us", "type": "quantitative", "label": "Time", "unit": "µs"},
                        {"field": "value", "type": "quantitative", "label": "ARA value"},
                        {"field": "parent_ARA", "type": "quantitative", "label": "Parent lifespan ARA"},
                    ],
                },
                "xAxisTitle": "Corrected ensemble time (µs)",
                "yAxisTitle": "Independent ARA coordinate (0–2)",
                "layout": "full",
            },
            {
                "id": "chart_holdout_time",
                "title": "Independent openness and closure histories — high-field example",
                "subtitle": "2160 G, RF on; same measurement construction at 202 K",
                "showDescription": True,
                "intent": "trend",
                "question": "How does the same pair evolve in the high-field regime where closure predicts later openness?",
                "rationale": "The matched line chart keeps the coordinate scale identical while exposing the regime-specific trajectory.",
                "type": "line",
                "dataset": "example_holdout",
                "sourceId": "timeline",
                "encodings": {
                    "x": {"field": "time_us", "type": "quantitative", "label": "Corrected ensemble time", "unit": "µs"},
                    "y": {"field": "value", "type": "quantitative", "label": "ARA coordinate", "unit": "0–2"},
                    "color": {"field": "coordinate", "type": "nominal", "label": "Independent coordinate"},
                    "tooltip": [
                        {"field": "time_us", "type": "quantitative", "label": "Time", "unit": "µs"},
                        {"field": "value", "type": "quantitative", "label": "ARA value"},
                        {"field": "parent_ARA", "type": "quantitative", "label": "Parent lifespan ARA"},
                    ],
                },
                "xAxisTitle": "Corrected ensemble time (µs)",
                "yAxisTitle": "Independent ARA coordinate (0–2)",
                "layout": "full",
            },
            {
                "id": "chart_plane",
                "title": "Openness–closure relation plane",
                "subtitle": "One point per past-only read; colour separates the validation and high-field examples",
                "showDescription": True,
                "intent": "relationship",
                "question": "Do the two histories occupy a repeatable two-axis relation rather than a forced diagonal?",
                "rationale": "A scatter plot preserves the independent U and R axes and reveals curved occupancy, clustering and regime displacement.",
                "type": "scatter",
                "dataset": "plane",
                "sourceId": "timeline",
                "encodings": {
                    "x": {"field": "openness_U", "type": "quantitative", "label": "Openness / traversal U", "unit": "0–2"},
                    "y": {"field": "closure_R", "type": "quantitative", "label": "Connection closure R", "unit": "0–2"},
                    "color": {"field": "example", "type": "nominal", "label": "Example sequence"},
                    "tooltip": [
                        {"field": "time_us", "type": "quantitative", "label": "Time", "unit": "µs"},
                        {"field": "step", "type": "quantitative", "label": "Chronology step"},
                        {"field": "parent_ARA", "type": "quantitative", "label": "Parent lifespan ARA"},
                    ],
                },
                "xAxisTitle": "Openness / traversal U (0–2)",
                "yAxisTitle": "Connection closure R (0–2)",
                "layout": "full",
            },
            {
                "id": "chart_errors_validation",
                "title": "Primary non-overlap prediction errors — validation",
                "subtitle": "Lower MSE is better; source and target histories share zero native bins",
                "showDescription": True,
                "intent": "comparison",
                "question": "Does the opposite history improve prediction beyond the target's own history under the frozen controls?",
                "rationale": "Grouped bars compare the correct transfer with baseline, wrong-frequency and reversed-order alternatives for both directions.",
                "type": "bar",
                "dataset": "errors_validation",
                "sourceId": "results",
                "encodings": {
                    "x": {"field": "model", "type": "nominal", "label": "Model / control"},
                    "y": {"field": "mse", "type": "quantitative", "label": "Mean squared error"},
                    "color": {"field": "arm", "type": "nominal", "label": "Direction"},
                    "tooltip": [
                        {"field": "prediction_rows", "type": "quantitative", "label": "Prediction rows"},
                        {"field": "mse", "type": "quantitative", "label": "MSE"},
                    ],
                },
                "xAxisTitle": "Model / control",
                "yAxisTitle": "Field-paired median MSE",
                "layout": "full",
            },
            {
                "id": "chart_errors_holdout",
                "title": "Primary non-overlap prediction errors — high-field holdout",
                "subtitle": "Lower MSE is better; 202 K and 1800–2484 G",
                "showDescription": True,
                "intent": "comparison",
                "question": "Does the directional effect survive the harder high-field and temperature shift?",
                "rationale": "The matched grouped bars show a strong R-to-U gain but also the wrong-frequency ambiguity that blocks the claim.",
                "type": "bar",
                "dataset": "errors_holdout",
                "sourceId": "results",
                "encodings": {
                    "x": {"field": "model", "type": "nominal", "label": "Model / control"},
                    "y": {"field": "mse", "type": "quantitative", "label": "Mean squared error"},
                    "color": {"field": "arm", "type": "nominal", "label": "Direction"},
                    "tooltip": [
                        {"field": "prediction_rows", "type": "quantitative", "label": "Prediction rows"},
                        {"field": "mse", "type": "quantitative", "label": "MSE"},
                    ],
                },
                "xAxisTitle": "Model / control",
                "yAxisTitle": "Field-paired median MSE",
                "layout": "full",
            },
            {
                "id": "chart_fields_validation",
                "title": "Per-field added information — validation",
                "subtitle": "Positive values favour the transfer model; RF-on/off are paired within each field",
                "showDescription": True,
                "intent": "relationship",
                "question": "Is any added information stable across interleaved validation fields?",
                "rationale": "A scatter plot reveals field heterogeneity and whether aggregate effects are driven by isolated resonance regions.",
                "type": "scatter",
                "dataset": "fields_validation",
                "sourceId": "metrics",
                "encodings": {
                    "x": {"field": "field_G", "type": "quantitative", "label": "Applied field", "unit": "G"},
                    "y": {"field": "effect", "type": "quantitative", "label": "Baseline MSE − transfer MSE"},
                    "color": {"field": "arm", "type": "nominal", "label": "Direction"},
                    "tooltip": [
                        {"field": "rf_on_effect", "type": "quantitative", "label": "RF-on effect"},
                        {"field": "rf_off_effect", "type": "quantitative", "label": "RF-off effect"},
                    ],
                },
                "xAxisTitle": "Applied magnetic field (G)",
                "yAxisTitle": "Baseline MSE − transfer MSE",
                "layout": "full",
            },
            {
                "id": "chart_fields_holdout",
                "title": "Per-field added information — high-field holdout",
                "subtitle": "Positive values favour the transfer model; 20 independent field settings",
                "showDescription": True,
                "intent": "relationship",
                "question": "Is the high-field R-to-U advantage broad across fields or isolated?",
                "rationale": "The scatter exposes the field distribution behind the bootstrap interval and keeps both directions visible.",
                "type": "scatter",
                "dataset": "fields_holdout",
                "sourceId": "metrics",
                "encodings": {
                    "x": {"field": "field_G", "type": "quantitative", "label": "Applied field", "unit": "G"},
                    "y": {"field": "effect", "type": "quantitative", "label": "Baseline MSE − transfer MSE"},
                    "color": {"field": "arm", "type": "nominal", "label": "Direction"},
                    "tooltip": [
                        {"field": "rf_on_effect", "type": "quantitative", "label": "RF-on effect"},
                        {"field": "rf_off_effect", "type": "quantitative", "label": "RF-off effect"},
                    ],
                },
                "xAxisTitle": "Applied magnetic field (G)",
                "yAxisTitle": "Baseline MSE − transfer MSE",
                "layout": "full",
            },
            {
                "id": "chart_lags",
                "title": "Prediction gain by source–target horizon",
                "subtitle": "Only 2.048 µs has zero shared history; all earlier points are overlap diagnostics",
                "showDescription": True,
                "intent": "trend",
                "question": "Does the apparent exchange persist as source and target histories are separated?",
                "rationale": "A multi-series line chart shows the scale dependence and makes the overlap-to-non-overlap boundary explicit in the data rows.",
                "type": "line",
                "dataset": "lags",
                "sourceId": "lags",
                "encodings": {
                    "x": {"field": "horizon_us", "type": "quantitative", "label": "Source-to-target horizon", "unit": "µs"},
                    "y": {"field": "relative_improvement_pct", "type": "quantitative", "label": "Relative MSE improvement", "unit": "%"},
                    "color": {"field": "series", "type": "nominal", "label": "Stage and direction"},
                    "tooltip": [
                        {"field": "shared_native_bins", "type": "quantitative", "label": "Shared native bins"},
                        {"field": "window_relation", "type": "nominal", "label": "Window relation"},
                        {"field": "prediction_rows", "type": "quantitative", "label": "Prediction rows"},
                    ],
                },
                "xAxisTitle": "Source-to-target horizon (µs)",
                "yAxisTitle": "Relative MSE improvement (%)",
                "layout": "full",
            },
        ],
        "tables": [
            {
                "id": "table_gates",
                "title": "Frozen stage gates",
                "subtitle": "A stage requires every gate; one passed component cannot rescue the complete claim",
                "showDescription": True,
                "dataset": "gates",
                "sourceId": "results",
                "defaultSort": {"field": "stage", "direction": "asc"},
                "density": "spacious",
                "layout": "full",
                "columns": [
                    {"field": "stage", "label": "Stage", "type": "text"},
                    {"field": "gate", "label": "Frozen gate", "type": "text"},
                    {"field": "status", "label": "Result", "type": "text"},
                    {"field": "run_period_sequences", "label": "Run/period histories", "type": "number"},
                    {"field": "primary_prediction_rows", "label": "Primary rows", "type": "number"},
                ],
            }
        ],
        "blocks": [
            {"id": "title", "type": "markdown", "body": "# T419 — Dynamic Irrationality Di-ARA Handover"},
            {
                "id": "summary",
                "type": "markdown",
                "sourceId": "results",
                "body": (
                    "## Technical summary\n\n"
                    "**The frozen bidirectional handover claim failed.** Neither validation nor holdout passed all six gates. "
                    "Openness did not reliably predict later closure once source and target histories were fully separated.\n\n"
                    "**A narrower directed branch is real enough to keep:** in the 202 K high-field holdout, closure history reduced later-openness MSE by 40.7% relative to the own-history baseline, with a field-bootstrap median effect of +0.00300 (95% CI +0.00171 to +0.00419), correct timing at p=0.001, reversed order rejected, and positive RF-on/off effects. "
                    "But it did not replicate as added information in the interleaved validation fields and did not beat the wrong-frequency reconstruction.\n\n"
                    "**ARA reading:** the present instrument recovers a regime-dependent, directed phase-history pathway, not yet a frequency-identified two-way closing/reopening exchange."
                ),
            },
            {"id": "metrics", "type": "metric-strip", "cardIds": ["card_validation", "card_holdout", "card_branch", "card_audit"]},
            {
                "id": "histories_heading",
                "type": "markdown",
                "body": "## The two coordinates are independent histories, not a manufactured TE-ARA pair\n\n`U` compares local phase-address loss with a null predictor; `R` measures lagged phase coherence. They are both placed on 0–2 ARA coordinates, but neither is calculated as `2 −` the other and their sum varies. The time views below show the actual measured relationship before any forecasting model is applied."
            },
            {"id": "validation_time", "type": "chart", "chartId": "chart_validation_time"},
            {
                "id": "validation_time_note",
                "type": "markdown",
                "body": "In the 284 G validation example, the histories move together in places but do not form a stable mirror. Local crossings are descriptive; the frozen forecast asks whether one history improves an out-of-window future value of the other."
            },
            {"id": "holdout_time", "type": "chart", "chartId": "chart_holdout_time"},
            {
                "id": "holdout_time_note",
                "type": "markdown",
                "body": "The high-field example is displaced and more tightly organized. That different regime is exactly where closure history becomes strongly useful for predicting later openness, so the effect must remain labelled as regime-specific rather than universal."
            },
            {"id": "plane", "type": "chart", "chartId": "chart_plane"},
            {
                "id": "plane_note",
                "type": "markdown",
                "body": "The relation plane shows curved occupancy rather than a forced diagonal. It is valid evidence that the coordinate boundary organizes the observations, but occupancy alone is not evidence of a temporal handover; that requires the non-overlap prediction below."
            },
            {
                "id": "prediction_heading",
                "type": "markdown",
                "body": "## Full time separation rejects the universal two-way handover\n\nThe primary forecast jumps 32 reads (128 native bins, about 2.048 µs). The future 128-bin target history begins immediately after the source history ends, so no raw bin appears on both sides. The transfer model must beat the target's own value and slope plus lifespan, field-turn and RF controls."
            },
            {"id": "errors_validation", "type": "chart", "chartId": "chart_errors_validation"},
            {
                "id": "errors_validation_note",
                "type": "markdown",
                "body": "Validation does not support either added-information arm. The closure→openness transfer has correct ordering information, but its aggregate error is worse than the own-history baseline and its field-bootstrap interval crosses zero. Openness→closure fails all substantive transfer gates."
            },
            {"id": "errors_holdout", "type": "chart", "chartId": "chart_errors_holdout"},
            {
                "id": "errors_holdout_note",
                "type": "markdown",
                "body": "In the high-field holdout, closure→openness is substantially better than baseline and reversed chronology. The nearly identical wrong-frequency error is the key failure: the predictive information is not specific to the declared muon-spin frequency, so it may be a broader phase-path or field-regime feature."
            },
            {
                "id": "fields_heading",
                "type": "markdown",
                "body": "## Field-level effects separate a broad high-field branch from unstable validation\n\nPositive values mean the transfer model improves on the own-history baseline. Field pairing prevents the two RF histories at one magnetic setting from masquerading as independent replications."
            },
            {"id": "fields_validation", "type": "chart", "chartId": "chart_fields_validation"},
            {"id": "fields_validation_note", "type": "markdown", "body": "The interleaved 68–500 G validation fields straddle zero in both directions. That instability explains why local visual coherence and correct ordering do not become a transferable added-information result."},
            {"id": "fields_holdout", "type": "chart", "chartId": "chart_fields_holdout"},
            {"id": "fields_holdout_note", "type": "markdown", "body": "The closure→openness advantage is broad across the 1800–2484 G holdout rather than confined to one resonance point. This supports a genuine high-field regime branch, while the frequency control prevents assigning it uniquely to the targeted spin identity."},
            {
                "id": "lag_heading",
                "type": "markdown",
                "body": "## Apparent exchange changes with observational separation\n\nShorter horizons share most of their underlying 128-bin histories and are therefore diagnostics, not causal evidence. Only the final 2.048 µs point has zero shared bins."
            },
            {"id": "lags_chart", "type": "chart", "chartId": "chart_lags"},
            {"id": "lags_note", "type": "markdown", "body": "High-field closure→openness strengthens from roughly 9% at 0.064 µs to 41% at the non-overlap horizon. Validation does not follow the same path and is worse than baseline at full separation. The result is therefore a regime split, not a single universal cadence."},
            {
                "id": "definitions",
                "type": "markdown",
                "sourceId": "protocol",
                "body": (
                    "## Scope, definitions and model specification\n\n"
                    "- **Who:** 13 development, 13 validation and 20 holdout magnetic-field runs; RF-on and RF-off stay separate.\n"
                    "- **Identity:** the detector-population spin relation of a muoniated-acetone radical, not one continuously observed muon.\n"
                    "- **Openness `U`:** `2 × local loss / (local loss + null loss)`. The ridge `U=1` means equal predictor losses.\n"
                    "- **Closure `R`:** twice the median lagged phase coherence across lags 1–32.\n"
                    "- **Baseline:** future target from its own current value/slope plus population-lifespan ARA, log2 spin turns per lifetime and RF condition.\n"
                    "- **Transfer:** baseline plus the other coordinate and its causal first difference.\n"
                    "- **Fitting:** development-only standardization and ordinary least squares; coefficients and gates hashed before validation/holdout."
                ),
            },
            {
                "id": "robustness",
                "type": "markdown",
                "sourceId": "audit",
                "body": "## Robustness checks and limitations\n\nAll 50 independent saved-artifact checks passed: protocol/analysis hashes, zero primary overlap, horizon size, eligibility, non-complementarity and every reported aggregate error/RF effect. The remaining limitation is substantive rather than computational: validation does not replicate the high-field branch, and wrong-frequency reconstruction is not worse there. The 202 K holdout also changes temperature and field together, so the present archive cannot identify which parent condition creates the branch."
            },
            {"id": "gates", "type": "table", "tableId": "table_gates"},
            {
                "id": "next",
                "type": "markdown",
                "body": "## Recommended next test\n\nUse a new dataset or scan with **temperature and field varied independently**, then freeze a one-direction `R → later U` test at the full non-overlap horizon. Add an off-target frequency control built from a physically distinct channel, not only nearby sidebands. That test can decide whether the high-field branch is a true connection-to-traversal handover, a temperature transition, or a generic phase-reconstruction feature."
            },
            {
                "id": "questions",
                "type": "markdown",
                "body": "## Further questions\n\n- Does the directed branch turn on continuously with field-turn budget, or at a material/temperature transition?\n- Which frequency-independent feature lets the wrong reconstruction retain the same future information?\n- Would a direct detector-space closure measure, independent of reconstructed phase, restore frequency specificity?\n- Is the missing `U → later R` arm genuinely absent, or does it live at a different rung/horizon than this population instrument can resolve?"
            },
        ],
    }

    artifact = {
        "surface": "report",
        "manifest": manifest,
        "snapshot": {
            "version": 1,
            "generatedAt": generated,
            "status": "ready",
            "datasets": {
                "cards": cards,
                "example_validation": [row for row in examples if row["stage"] == "Validation"],
                "example_holdout": [row for row in examples if row["stage"] == "Holdout"],
                "plane": plane,
                "errors_validation": [row for row in errors if row["stage"] == "Validation"],
                "errors_holdout": [row for row in errors if row["stage"] == "Holdout"],
                "fields_validation": fields_validation,
                "fields_holdout": fields_holdout,
                "lags": lags,
                "gates": gates,
            },
            "accessIssues": [],
        },
        "sources": sources,
    }
    OUTPUT.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

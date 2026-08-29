#!/usr/bin/env python3
"""Build the canonical portable technical report for T415."""

from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUTPUT = RESULTS / "T415_REPORT_ARTIFACT.json"
SQLITE_OUTPUT = RESULTS / "T415_REPORT_DATA.sqlite"
TITLE = "T415 — What predicts later muon release?"
DOI = "https://data.isis.stfc.ac.uk/doi/STUDY/103197258"


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value, digits: int = 8) -> float:
    return round(float(value), digits)


def write_sqlite_table(connection: sqlite3.Connection, name: str, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"Cannot create empty table {name}")
    fields = list(rows[0])
    types = []
    for field in fields:
        values = [row.get(field) for row in rows if row.get(field) is not None]
        types.append("REAL" if values and all(isinstance(value, (int, float, bool)) for value in values) else "TEXT")
    columns = ", ".join(f'"{field}" {kind}' for field, kind in zip(fields, types))
    connection.execute(f'CREATE TABLE "{name}" ({columns})')
    placeholders = ", ".join("?" for _ in fields)
    connection.executemany(
        f'INSERT INTO "{name}" VALUES ({placeholders})',
        [[row.get(field) for field in fields] for row in rows],
    )


def table_source(source_id: str, label: str, table: str, description: str) -> dict:
    return {
        "id": source_id,
        "label": label,
        "href": DOI,
        "query": {
            "engine": "SQLite",
            "sql": f'SELECT * FROM "{table}";',
            "description": description,
            "tables_used": [f"T415_REPORT_DATA.sqlite::{table}"],
        },
    }


def main() -> None:
    result = json.loads((RESULTS / "T415_VALIDATION_RESULTS.json").read_text(encoding="utf-8"))
    posthoc = json.loads((RESULTS / "T415_POSTHOC_PARENT_HISTORY.json").read_text(encoding="utf-8"))
    audit = json.loads((RESULTS / "T415_VALIDATION_AUDIT.json").read_text(encoding="utf-8"))
    model_summary_raw = read_csv(RESULTS / "T415_MODEL_SUMMARY.csv")
    field_raw = read_csv(RESULTS / "T415_FIELD_METRICS.csv")
    posthoc_field_raw = read_csv(RESULTS / "T415_POSTHOC_PARENT_HISTORY_FIELDS.csv")
    posthoc_summary_raw = read_csv(RESULTS / "T415_POSTHOC_PARENT_HISTORY_SUMMARY.csv")
    profile_raw = read_csv(RESULTS / "T415_EXAMPLE_284G_PROFILE.csv")
    strength_rate_raw = read_csv(RESULTS / "T415_POSTHOC_STRENGTH_RATE_DECILES.csv")

    primary = next(
        row for row in model_summary_raw
        if row["horizon_bins"] == "4" and row["model"] == "M4 full lock"
    )
    diagnostic_full = next(row for row in posthoc_summary_raw if row["model"] == "D3 full diagnostic")
    headline = [{
        "resolved_runs": 26,
        "validation_fields": 13,
        "primary_horizon_us": number(result["primary_horizon_us"], 3),
        "frozen_apparent_improvement_percent": number(100 * float(primary["median_field_improvement_fraction"]), 2),
        "posthoc_incremental_improvement_percent": number(100 * float(diagnostic_full["median_field_improvement_fraction"]), 2),
        "strength_parent_correlation": number(posthoc["strength_vs_current_log_rate_correlation"], 3),
        "frozen_gate_supported": "No",
        "independent_audit": audit["status"].title(),
    }]

    model_improvement = []
    horizon_labels = {"1": "0.016 µs", "4": "0.064 µs", "8": "0.128 µs"}
    short_names = {
        "M0 parent": "M0 parent",
        "M1 + spin": "M1 + spin",
        "M2 + strength": "M2 + strength",
        "M3 + environment": "M3 + environment",
        "M4 full lock": "M4 full array",
    }
    for row in model_summary_raw:
        model_improvement.append({
            "horizon": horizon_labels[row["horizon_bins"]],
            "horizon_bins": int(row["horizon_bins"]),
            "model": short_names[row["model"]],
            "median_improvement_percent": number(100 * float(row["median_field_improvement_fraction"]), 4),
            "field_wins": int(row["field_wins"]),
            "field_count": int(row["field_count"]),
            "lambda": number(row["lambda"]),
        })

    primary_fields = []
    for row in field_raw:
        if row["horizon_bins"] == "4" and row["model"] == "M4 full lock":
            primary_fields.append({
                "field_G": number(row["field_G"], 1),
                "analysis": "Frozen: time-only parent baseline",
                "improvement_percent": number(100 * float(row["improvement_fraction"]), 4),
                "rmse_log_rate": number(row["rmse_log_rate"]),
                "baseline_rmse_log_rate": number(row["parent_rmse_log_rate"]),
                "run": row["run"],
            })
    for row in posthoc_field_raw:
        if row["model"] == "D3 full diagnostic":
            primary_fields.append({
                "field_G": number(row["field_G"], 1),
                "analysis": "Diagnostic: parent rate + slope baseline",
                "improvement_percent": number(100 * float(row["improvement_fraction"]), 4),
                "rmse_log_rate": number(row["rmse_log_rate"]),
                "baseline_rmse_log_rate": number(row["parent_history_rmse_log_rate"]),
                "run": row["run"],
            })

    diagnostic_models = []
    for row in posthoc_summary_raw:
        diagnostic_models.append({
            "model": row["model"],
            "median_improvement_percent": number(100 * float(row["median_field_improvement_fraction"]), 4),
            "field_wins": int(row["field_wins"]),
            "field_count": int(row["field_count"]),
            "median_rmse_log_rate": number(row["median_field_rmse_log_rate"]),
            "lambda": number(row["lambda"]),
        })

    example_profile = [{
        "target_time_us": number(row["target_time_us"], 4),
        "observed_normalized_rate": number(row["observed_normalized_rate"]),
        "parent_prediction": number(row["parent_prediction"]),
        "full_array_prediction": number(row["full_array_prediction"]),
        "parent_ARA": number(row["parent_ARA"]),
        "spin_cut_A_ARA": number(row["spin_cut_A_ARA"]),
        "spin_cut_B_ARA": number(row["spin_cut_B_ARA"]),
        "share_strength": number(row["strength"]),
    } for row in profile_raw]

    strength_rate = [{
        "strength_decile": int(row["strength_decile"]),
        "mean_strength": number(row["mean_strength"]),
        "mean_current_log_rate": number(row["mean_current_log_rate"]),
        "se_current_log_rate": number(row["se_current_log_rate"]),
        "sample_bins": int(row["sample_bins"]),
    } for row in strength_rate_raw]

    controls = [{
        "control": "Correct M4 array",
        "median_improvement_percent": number(100 * float(primary["median_field_improvement_fraction"]), 4),
        "field_wins": int(primary["field_wins"]),
        "field_count": int(primary["field_count"]),
        "interpretation": "Apparent improvement against the time-only parent baseline.",
    }]
    for row in result["controls"]:
        controls.append({
            "control": row["control"].replace("_", " ").title(),
            "median_improvement_percent": number(100 * float(row["median_field_improvement_fraction"]), 4),
            "field_wins": int(row["field_wins"]),
            "field_count": int(row["field_count"]),
            "interpretation": (
                "Wrong spin frequency; should lose if spin phase is the information source."
                if row["control"] == "wrong_frequency"
                else "Lagged share-strength history circularly displaced in time."
            ),
        })

    gate_explanations = {
        "median_improvement_positive": "M4 median improvement over the time-only parent baseline is positive.",
        "at_least_10_of_13_fields_improve": "At least ten validation fields improve.",
        "beats_wrong_frequency_control": "Correct spin frequency beats the wrong-frequency control.",
        "beats_broken_history_control": "Correct temporal history beats the shifted-history control.",
        "both_rf_period_medians_positive": "RF-on and RF-off each improve in median.",
        "full_array_supported": "Every frozen primary condition passes.",
    }
    gates = [{
        "gate": key.replace("_", " ").title(),
        "status": "PASS" if value else "FAIL",
        "meaning": gate_explanations[key],
    } for key, value in result["gates"].items()]

    audit_rows = [{
        "check": key.replace("_", " ").title(),
        "status": "PASS" if value else "FAIL",
    } for key, value in audit["checks"].items()]

    datasets = {
        "headline": headline,
        "model_improvement": model_improvement,
        "primary_fields": primary_fields,
        "diagnostic_models": diagnostic_models,
        "example_profile": example_profile,
        "strength_rate": strength_rate,
        "controls": controls,
        "gates": gates,
        "audit": audit_rows,
    }

    if SQLITE_OUTPUT.exists():
        SQLITE_OUTPUT.unlink()
    with sqlite3.connect(SQLITE_OUTPUT) as connection:
        for name, rows in datasets.items():
            write_sqlite_table(connection, name, rows)
        connection.commit()

    raw_source = {
        "id": "isis-rb1620447",
        "label": "ISIS RB1620447 public RF-µSR dataset",
        "href": DOI,
        "query": {
            "engine": "ISIS DataGateway",
            "url": DOI,
            "description": "Twenty-six resolved 300 K EMU runs used for T415; 13 development and 13 interleaved validation fields.",
            "filters": [
                "Magnetic field 50–500 G",
                "Corrected time 0.25–6.00 microseconds at native 0.016-microsecond spacing",
                "RF-on and RF-off analysed separately",
                "High-field 202 K branch excluded after the frozen T414 sampling failure",
            ],
            "tables_used": ["ISIS investigation RB1620447 / raw NeXus dataset"],
        },
    }
    analysis_source = {
        "id": "t415-analysis",
        "label": "T415 frozen multichannel analysis and parent-history diagnostic",
        "href": DOI,
        "query": {
            "engine": "Python 3.12",
            "query": "python t415_multichannel_state_array.py --stage development && python t415_multichannel_state_array.py --stage validation",
            "description": "Nested ridge models, whole-run validation, wrong-frequency and broken-history controls, followed by a labelled stronger-parent-baseline diagnostic.",
            "language": "shell",
            "filters": [
                "Primary forecast horizon 0.064 microseconds",
                "Development-only model fitting and regularisation",
                "Validation replicate is the magnetic field, not the time bin",
            ],
            "metric_definitions": [
                "Improvement = 1 - model RMSE / parent-baseline RMSE",
                "Spin cuts are 1+sin(theta) and 1+cos(theta)",
                "Share strength is the lagged 96-detector share displacement from the early reference",
                "Parent-history diagnostic adds current normalized log rate and one-bin slope",
            ],
            "tables_used": [
                "T415_MODEL_SUMMARY.csv",
                "T415_FIELD_METRICS.csv",
                "T415_POSTHOC_PARENT_HISTORY_SUMMARY.csv",
                "T415_VALIDATION_AUDIT.json",
            ],
        },
    }
    sources = [
        raw_source,
        analysis_source,
        table_source("t415-headline", "T415 headline metrics", "headline", "Frozen and diagnostic headline values."),
        table_source("t415-models", "T415 nested model comparison", "model_improvement", "Median validation-field improvement by model and horizon."),
        table_source("t415-fields", "T415 field-level comparison", "primary_fields", "Primary frozen and stronger-baseline field-level improvements."),
        table_source("t415-diagnostic", "T415 parent-history diagnostic", "diagnostic_models", "Incremental value after current parent rate and slope are included."),
        table_source("t415-profile", "T415 284 G example profile", "example_profile", "Observed and predicted normalized release profiles at the primary horizon."),
        table_source("t415-strength-rate", "T415 strength/rate relation", "strength_rate", "Current parent log rate across lagged share-strength deciles."),
        table_source("t415-controls", "T415 frozen controls", "controls", "Correct, wrong-frequency and broken-history validation comparisons."),
        table_source("t415-gates", "T415 frozen gates", "gates", "Prespecified primary interpretation gates."),
        table_source("t415-audit", "T415 independent audit", "audit", "Independent provenance and arithmetic checks."),
    ]

    cards = [
        {
            "id": "frozen-gain-card",
            "description": "Frozen M4 median validation-field improvement at 0.064 microseconds.",
            "dataset": "headline",
            "sourceId": "t415-headline",
            "metrics": [{"field": "frozen_apparent_improvement_percent", "label": "Median improvement", "format": "number", "unit": "%"}],
        },
        {
            "id": "diagnostic-gain-card",
            "description": "Incremental M4-equivalent value beyond current parent rate and slope.",
            "dataset": "headline",
            "sourceId": "t415-headline",
            "metrics": [{"field": "posthoc_incremental_improvement_percent", "label": "Median improvement", "format": "number", "unit": "%"}],
        },
        {
            "id": "correlation-card",
            "description": "The near-perfect inverse relation identifies the original proxy.",
            "dataset": "headline",
            "sourceId": "t415-headline",
            "metrics": [{"field": "strength_parent_correlation", "label": "Correlation", "format": "number"}],
        },
        {
            "id": "gate-card",
            "description": "The correct array did not beat the wrong-frequency control.",
            "dataset": "headline",
            "sourceId": "t415-headline",
            "metrics": [{"field": "frozen_gate_supported", "label": "Supported", "format": "text"}],
        },
    ]

    charts = [
        {
            "id": "nested-model-chart",
            "title": "Nested model improvement over the time-only parent",
            "subtitle": "Median across 13 validation fields; three future horizons",
            "showDescription": True,
            "type": "bar",
            "intent": "comparison",
            "dataset": "model_improvement",
            "sourceId": "t415-models",
            "encodings": {
                "x": {"field": "model", "type": "nominal", "label": "Nested model"},
                "y": {"field": "median_improvement_percent", "type": "quantitative", "label": "Improvement", "unit": "%"},
                "color": {"field": "horizon", "type": "nominal", "label": "Forecast horizon"},
                "tooltip": [
                    {"field": "model", "type": "nominal"},
                    {"field": "horizon", "type": "nominal"},
                    {"field": "median_improvement_percent", "type": "quantitative", "unit": "%"},
                    {"field": "field_wins", "type": "quantitative"},
                    {"field": "field_count", "type": "quantitative"},
                ],
            },
            "xAxisTitle": "Nested ARA state array",
            "yAxisTitle": "Median improvement over M0 (%)",
            "referenceLines": [{"axis": "y", "value": 0, "label": "no improvement", "lineStyle": "dashed"}],
            "layout": "full",
        },
        {
            "id": "field-comparison-chart",
            "title": "Primary-horizon improvement by validation field",
            "subtitle": "Frozen time-only baseline versus the stronger parent-rate-and-slope baseline",
            "showDescription": True,
            "type": "scatter",
            "intent": "relationship",
            "dataset": "primary_fields",
            "sourceId": "t415-fields",
            "encodings": {
                "x": {"field": "field_G", "type": "quantitative", "label": "Magnetic field", "unit": "G"},
                "y": {"field": "improvement_percent", "type": "quantitative", "label": "Improvement", "unit": "%"},
                "color": {"field": "analysis", "type": "nominal", "label": "Baseline"},
                "tooltip": [
                    {"field": "run", "type": "nominal"},
                    {"field": "field_G", "type": "quantitative", "unit": "G"},
                    {"field": "analysis", "type": "nominal"},
                    {"field": "improvement_percent", "type": "quantitative", "unit": "%"},
                ],
            },
            "xAxisTitle": "Magnetic field (G)",
            "yAxisTitle": "Improvement over stated baseline (%)",
            "referenceLines": [{"axis": "y", "value": 0, "label": "baseline parity", "lineStyle": "dashed"}],
            "layout": "full",
        },
        {
            "id": "diagnostic-model-chart",
            "title": "Incremental value after current parent history is available",
            "subtitle": "Primary 0.064-microsecond horizon; median across 13 validation fields",
            "showDescription": True,
            "type": "bar",
            "intent": "comparison",
            "dataset": "diagnostic_models",
            "sourceId": "t415-diagnostic",
            "encodings": {
                "x": {"field": "model", "type": "nominal", "label": "Diagnostic model"},
                "y": {"field": "median_improvement_percent", "type": "quantitative", "label": "Improvement", "unit": "%"},
                "tooltip": [
                    {"field": "model", "type": "nominal"},
                    {"field": "median_improvement_percent", "type": "quantitative", "unit": "%"},
                    {"field": "field_wins", "type": "quantitative"},
                    {"field": "field_count", "type": "quantitative"},
                ],
            },
            "xAxisTitle": "Characteristics added beyond parent history",
            "yAxisTitle": "Median improvement (%)",
            "referenceLines": [{"axis": "y", "value": 0, "label": "no added value", "lineStyle": "dashed"}],
            "layout": "full",
        },
        {
            "id": "strength-rate-chart",
            "title": "Lagged share strength and the current parent rate",
            "subtitle": "Ten equal-count strength bins across validation; ρ = −0.968 before binning",
            "showDescription": True,
            "type": "line",
            "intent": "trend",
            "dataset": "strength_rate",
            "sourceId": "t415-strength-rate",
            "encodings": {
                "x": {"field": "mean_strength", "type": "quantitative", "label": "Mean share strength"},
                "y": {"field": "mean_current_log_rate", "type": "quantitative", "label": "Mean current log release rate"},
                "tooltip": [
                    {"field": "strength_decile", "type": "quantitative"},
                    {"field": "mean_strength", "type": "quantitative"},
                    {"field": "mean_current_log_rate", "type": "quantitative"},
                    {"field": "sample_bins", "type": "quantitative"},
                ],
            },
            "xAxisTitle": "Lagged detector-share strength",
            "yAxisTitle": "Current normalized log release rate",
            "layout": "full",
        },
        {
            "id": "example-profile-chart",
            "title": "Observed and predicted release profile at 284 G",
            "subtitle": "RF on; four-bin-ahead ensemble forecast",
            "showDescription": True,
            "type": "line",
            "intent": "trend",
            "dataset": "example_profile",
            "sourceId": "t415-profile",
            "encodings": {
                "x": {"field": "target_time_us", "type": "quantitative", "label": "Target time", "unit": "µs"},
                "y": {"fields": ["observed_normalized_rate", "parent_prediction", "full_array_prediction"], "type": "quantitative", "label": "Normalized release rate"},
                "tooltip": [
                    {"field": "target_time_us", "type": "quantitative", "unit": "µs"},
                    {"field": "observed_normalized_rate", "type": "quantitative"},
                    {"field": "parent_prediction", "type": "quantitative"},
                    {"field": "full_array_prediction", "type": "quantitative"},
                ],
            },
            "xAxisTitle": "Corrected target time (µs)",
            "yAxisTitle": "Release rate / early reference",
            "layout": "full",
        },
    ]

    tables = [
        {
            "id": "gate-table",
            "title": "Frozen primary interpretation gates",
            "subtitle": "The complete array is supported only if every row passes",
            "showDescription": True,
            "dataset": "gates",
            "sourceId": "t415-gates",
            "defaultSort": {"field": "gate", "direction": "asc"},
            "density": "spacious",
            "layout": "full",
            "columns": [
                {"field": "gate", "label": "Gate", "type": "text"},
                {"field": "status", "label": "Status", "type": "text"},
                {"field": "meaning", "label": "Meaning", "type": "text"},
            ],
        },
        {
            "id": "control-table",
            "title": "Correct array and frozen controls",
            "subtitle": "Primary four-bin horizon across 13 validation fields",
            "showDescription": True,
            "dataset": "controls",
            "sourceId": "t415-controls",
            "defaultSort": {"field": "median_improvement_percent", "direction": "desc"},
            "density": "spacious",
            "layout": "full",
            "columns": [
                {"field": "control", "label": "Condition", "type": "text"},
                {"field": "median_improvement_percent", "label": "Median improvement (%)", "type": "number"},
                {"field": "field_wins", "label": "Field wins", "type": "number"},
                {"field": "field_count", "label": "Fields", "type": "number"},
                {"field": "interpretation", "label": "Interpretation", "type": "text"},
            ],
        },
        {
            "id": "audit-table",
            "title": "Independent T415 audit",
            "subtitle": "Hashes, source files, split counts, rows, gates and post-hoc recomputation",
            "showDescription": True,
            "dataset": "audit",
            "sourceId": "t415-audit",
            "defaultSort": {"field": "check", "direction": "asc"},
            "density": "dense",
            "layout": "full",
            "columns": [
                {"field": "check", "label": "Check", "type": "text"},
                {"field": "status", "label": "Status", "type": "text"},
            ],
        },
    ]

    blocks = [
        {"id": "title", "type": "markdown", "body": f"# {TITLE}"},
        {
            "id": "technical-summary",
            "type": "markdown",
            "sourceId": "t415-analysis",
            "body": (
                "## Technical summary\n\n"
                "**The characteristic array did not provide spin-specific prediction of later ensemble release.** Against a time-only parent curve, the frozen full array appeared to improve the four-bin-ahead forecast by 30.5% in all 13 validation fields. It nevertheless failed its prespecified gate because a wrong spin frequency performed fractionally better.\n\n"
                "A stronger-baseline diagnostic located the apparent success: lagged detector-share strength correlated −0.968 with the parent’s current log release rate. Once current parent rate and slope were included, the complete array changed median error by −0.22% and improved only 5 of 13 fields. The array had recovered omitted parent history, not a spin-to-release handover."
            ),
        },
        {"id": "headline-strip", "type": "metric-strip", "cardIds": [card["id"] for card in cards], "dataset": "headline"},
        {
            "id": "frozen-heading",
            "type": "markdown",
            "sourceId": "t415-models",
            "body": "## The frozen array found a repeatable signal, but not in spin\n\nSpin alone stayed at baseline across all three horizons. The large improvement entered only when lagged detector-share strength was added and persisted after environmental and Information-lock terms. That made the temporal channel worth investigating, but did not identify its physical owner.",
        },
        {"id": "nested-model-block", "type": "chart", "chartId": "nested-model-chart", "layout": "full"},
        {
            "id": "control-heading",
            "type": "markdown",
            "sourceId": "t415-controls",
            "body": "## The wrong-frequency control prevents a spin-handover claim\n\nThe correct M4 array improved every validation field, yet the wrong-frequency version was fractionally better in median. Breaking temporal history destroyed performance. The predictive information was therefore time-ordered, but not locked to the calibrated spin phase.",
        },
        {"id": "control-table-block", "type": "table", "tableId": "control-table", "layout": "full"},
        {
            "id": "baseline-heading",
            "type": "markdown",
            "sourceId": "t415-fields",
            "body": "## A complete parent baseline removes the apparent 30% gain\n\nThe upper field band in the next figure is the frozen comparison against parent time alone. The near-zero band uses the parent’s observed current rate and one-bin slope as well. That second comparison answers the stricter question: do the children add information after the parent state is actually known? Here they do not.",
        },
        {"id": "field-comparison-block", "type": "chart", "chartId": "field-comparison-chart", "layout": "full"},
        {
            "id": "diagnostic-heading",
            "type": "markdown",
            "sourceId": "t415-diagnostic",
            "body": "## No characteristic adds stable value beyond current parent history\n\nSpin, share strength and the complete diagnostic array all sit slightly below parent-history parity. The differences are small, but they consistently reject the earlier interpretation that the 30% gain represented a child-driven handover.",
        },
        {"id": "diagnostic-model-block", "type": "chart", "chartId": "diagnostic-model-chart", "layout": "full"},
        {
            "id": "proxy-heading",
            "type": "markdown",
            "sourceId": "t415-strength-rate",
            "body": "## Share strength was an inverse image of the current parent rate\n\nAs release counts fall, detector-share estimates become more dispersed. The strength coordinate therefore carried a near-direct inverse encoding of the parent’s current count level. The ordered deciles make that relation visible; it is parent information wearing a child-channel label.",
        },
        {"id": "strength-rate-block", "type": "chart", "chartId": "strength-rate-chart", "layout": "full"},
        {
            "id": "profile-heading",
            "type": "markdown",
            "sourceId": "t415-profile",
            "body": "## The array tracks the profile closely for the wrong reason\n\nAt 284 G the frozen full array visually follows the observed release curve better than the time-only parent. The stronger-baseline diagnostic shows why visual agreement alone was insufficient: present parent history already contains the information used to obtain that improvement.",
        },
        {"id": "profile-block", "type": "chart", "chartId": "example-profile-chart", "layout": "full"},
        {
            "id": "definitions",
            "type": "markdown",
            "body": (
                "## Scope and definitions\n\n"
                "The replicate is one magnetic field, with RF-on and RF-off errors pooled for the primary score. The target is the future detector-summed ensemble release profile at 0.016, 0.064 or 0.128 microseconds. Parent maturity is `2(1-exp(-t/τ))`. Spin is represented by the perpendicular `1+sin(θ)` and `1+cos(θ)` cuts. Share strength is a lagged displacement of the 96-detector share vector from its early reference.\n\n"
                "This archive does not contain continuously observed individual muons. T415 therefore cannot identify an individual decay or neutrino handover."
            ),
        },
        {
            "id": "methodology",
            "type": "markdown",
            "sourceId": "t415-analysis",
            "body": (
                "## Frozen design and diagnostic sequence\n\n"
                "Thirteen development fields fixed nested ridge models and regularisation by leave-one-run-out validation. Thirteen interleaved fields were then scored once. The frozen gate required positive improvement in at least 10 fields, both RF periods, and superiority to wrong-frequency and shifted-history controls. After that gate failed, a labelled post-hoc model added current parent log rate and slope to test the omitted-parent-state explanation. No frozen result was overwritten."
            ),
        },
        {"id": "gate-table-block", "type": "table", "tableId": "gate-table", "layout": "full"},
        {
            "id": "limitations",
            "type": "markdown",
            "body": (
                "## Limitations and uncertainty\n\n"
                "The development/validation archive was reused from T414, so this is not independent external confirmation. Detector angles are unavailable, individual arrivals and decays are not linked, and the share-strength coordinate is affected by multinomial count precision. The diagnostic is post-hoc and explains the frozen failure; it is not a replacement confirmatory test. Incomplete detector acceptance can also couple directional redistribution into observed totals."
            ),
        },
        {
            "id": "next-step",
            "type": "markdown",
            "body": (
                "## Recommended next test\n\n"
                "Use event-level or finely time-tagged data with absolute detector geometry. Make current parent rate and slope part of the baseline from the beginning. Derive spin coherence from a count-noise-corrected directional estimator, then ask whether perpendicular spin phase or coherence improves untouched, whole-run forecasts beyond that parent history. The ideal target remains a calibrated probability of release in the next interval, not retrospective curve reconstruction."
            ),
        },
        {
            "id": "further-questions",
            "type": "markdown",
            "body": (
                "## Further questions\n\n"
                "- Can a detector-pair or absolute-angle coherence estimator separate physical polarization from declining count precision?\n"
                "- Does any characteristic add information at an event-level grain after current parent history is controlled?\n"
                "- Is there an external archive with matched low-field resolution that can provide a genuinely untouched replication branch?"
            ),
        },
        {"id": "audit-heading", "type": "markdown", "body": "## Independent audit\n\nAll frozen hashes, source hashes, split counts, result rows, gates and post-hoc headline calculations were recomputed successfully."},
        {"id": "audit-table-block", "type": "table", "tableId": "audit-table", "layout": "full"},
    ]

    generated = datetime.now(timezone.utc).isoformat()
    manifest = {
        "version": 1,
        "surface": "report",
        "title": TITLE,
        "description": "Frozen multichannel ARA forecast and stronger-parent-baseline diagnostic on resolved public RF-µSR data.",
        "generatedAt": generated,
        "sources": sources,
        "cards": cards,
        "charts": charts,
        "tables": tables,
        "blocks": blocks,
    }
    artifact = {
        "surface": "report",
        "manifest": manifest,
        "snapshot": {
            "version": 1,
            "generatedAt": generated,
            "status": "ready",
            "datasets": datasets,
        },
        "sources": sources,
    }
    OUTPUT.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()

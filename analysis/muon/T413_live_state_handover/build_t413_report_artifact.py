#!/usr/bin/env python3
"""Build the canonical portable-report artifact for T413."""

from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
METRICS = RESULTS / "T413_FULL_RUN_METRICS.csv"
RESULT_JSON = RESULTS / "T413_FULL_RESULTS.json"
OUTPUT = RESULTS / "T413_REPORT_ARTIFACT.json"
SQLITE_OUTPUT = RESULTS / "T413_REPORT_DATA.sqlite"

TITLE = "T413 — Live-state muonium handover"
RAW_SOURCE_ID = "isis-rb1620447"
DERIVED_SOURCE_ID = "t413-frozen-analysis"
HEADLINE_SOURCE_ID = "t413-headline-sql"
MODELS_SOURCE_ID = "t413-model-medians-sql"
FIELDS_SOURCE_ID = "t413-holdout-fields-sql"
TRAJECTORY_SOURCE_ID = "t413-example-trajectory-sql"
GATES_SOURCE_ID = "t413-gates-sql"


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def rounded(value: float, digits: int = 8) -> float:
    return round(float(value), digits)


def write_sqlite_table(connection: sqlite3.Connection, name: str, rows: list[dict]) -> None:
    """Persist the exact rows used by report widgets so their SQL provenance is runnable."""
    if not rows:
        raise ValueError(f"Cannot create empty report table: {name}")
    fields = list(rows[0])
    types = []
    for field in fields:
        values = [row.get(field) for row in rows if row.get(field) is not None]
        sql_type = "REAL" if values and all(isinstance(value, (int, float, bool)) for value in values) else "TEXT"
        types.append(sql_type)
    columns = ", ".join(f'"{field}" {sql_type}' for field, sql_type in zip(fields, types))
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
        "href": "https://data.isis.stfc.ac.uk/doi/STUDY/103197258",
        "query": {
            "engine": "SQLite",
            "sql": f'SELECT * FROM "{table}";',
            "description": description,
            "tables_used": [f"T413_REPORT_DATA.sqlite::{table}"],
        },
    }


def main() -> None:
    metrics = read_csv(METRICS)
    result = json.loads(RESULT_JSON.read_text(encoding="utf-8"))
    aggregate = result["aggregate"]
    holdout = aggregate["holdout"]
    medians = holdout["median_rmse"]
    gates = aggregate["frozen_gates"]
    holdout_rows = [row for row in metrics if row["split"] == "holdout"]

    relative_vs_ar1 = (medians["ar1"] - medians["ara_full"]) / medians["ar1"]
    relative_vs_harmonic = (medians["harmonic"] - medians["ara_full"]) / medians["harmonic"]
    relative_vs_persistence = (medians["persistence"] - medians["ara_full"]) / medians["persistence"]
    mode_fraction = float(np.median([float(row["mode_variance_fraction"]) for row in holdout_rows]))
    orientation_wins = holdout["ara_pairwise_win_fraction"]["wrong_orientation"]

    headline = [{
        "holdout_runs": 20,
        "ara_rmse": rounded(medians["ara_full"]),
        "best_simple_rmse": rounded(min(medians["ar1"], medians["diagonal"], medians["persistence"])),
        "relative_gap_vs_ar1": rounded(relative_vs_ar1),
        "relative_gain_vs_harmonic": rounded(relative_vs_harmonic),
        "relative_gain_vs_persistence": rounded(relative_vs_persistence),
        "orientation_win_share": rounded(orientation_wins),
        "median_first_mode_share": rounded(mode_fraction),
    }]

    model_labels = {
        "ara_full": "Full temporal Di-ARA",
        "persistence": "Persistence",
        "ar1": "One-coordinate AR(1)",
        "diagonal": "No cross-coupling",
        "harmonic": "Damped harmonic",
        "wrong_orientation": "Wrong orientation",
        "broken_order": "Broken time order",
    }
    model_medians = []
    for split in ("development", "validation", "holdout"):
        for model, value in aggregate[split]["median_rmse"].items():
            model_medians.append({
                "split": split.title(),
                "model": model_labels[model],
                "rmse": rounded(value),
                "delta_vs_ara": rounded(value - aggregate[split]["median_rmse"]["ara_full"]),
                "run_count": aggregate[split]["run_count"],
            })

    holdout_fields = []
    for row in holdout_rows:
        ara = float(row["rmse_ara_full"])
        ar1 = float(row["rmse_ar1"])
        diagonal = float(row["rmse_diagonal"])
        harmonic = float(row["rmse_harmonic"])
        holdout_fields.append({
            "field_G": float(row["field_G"]),
            "ara_rmse": rounded(ara),
            "ar1_rmse": rounded(ar1),
            "diagonal_rmse": rounded(diagonal),
            "harmonic_rmse": rounded(harmonic),
            "ara_advantage_vs_ar1": rounded(ar1 - ara),
            "ara_advantage_vs_diagonal": rounded(diagonal - ara),
            "mode_variance_fraction": rounded(float(row["mode_variance_fraction"])),
            "future_correlation_ara": rounded(float(row["future_correlation_ara"])),
        })

    example_run = "EMU00070275"  # F=2160 G, fixed by the central holdout-field choice.
    detail = result["run_details"][example_run]
    time = np.asarray(detail["time"], dtype=float)
    development = np.asarray(detail["development"], dtype=bool)
    score = np.asarray(detail["score"], dtype=float)
    future_indices = np.flatnonzero(~development)
    example = []
    for index, current_time in enumerate(time):
        row = {
            "time_us": rounded(current_time, 6),
            "window": "Development" if development[index] else "Untouched future",
            "observed_A": rounded(score[index]),
            "ara_prediction": None,
            "ar1_prediction": None,
            "diagonal_prediction": None,
            "harmonic_prediction": None,
            "field_G": 2160,
            "run": example_run,
        }
        if not development[index]:
            future_position = int(np.where(future_indices == index)[0][0])
            row["ara_prediction"] = rounded(detail["predictions"]["ara_full"][future_position])
            row["ar1_prediction"] = rounded(detail["predictions"]["ar1"][future_position])
            row["diagonal_prediction"] = rounded(detail["predictions"]["diagonal"][future_position])
            row["harmonic_prediction"] = rounded(detail["predictions"]["harmonic"][future_position])
        example.append(row)

    gate_rows = [
        {
            "gate": "Relational predictive support",
            "status": "NOT SUPPORTED" if not gates["relational_predictive_support"] else "SUPPORTED",
            "evidence": "Full model median RMSE 0.04684; AR(1) 0.04646; bootstrap interval versus best simple model crosses zero.",
        },
        {
            "gate": "Orientation support",
            "status": "SUPPORTED" if gates["orientation_support"] else "NOT SUPPORTED",
            "evidence": "Frozen orientation won on 60% of holdout runs and had a small positive median advantage.",
        },
        {
            "gate": "Added value beyond damped harmonic",
            "status": "SUPPORTED IN ISOLATION" if gates["added_value_beyond_harmonic"] else "NOT SUPPORTED",
            "evidence": "Full model RMSE was 18.6% lower, but this does not override failure against the simpler AR(1) comparator.",
        },
    ]

    if SQLITE_OUTPUT.exists():
        SQLITE_OUTPUT.unlink()
    with sqlite3.connect(SQLITE_OUTPUT) as connection:
        write_sqlite_table(connection, "headline", headline)
        write_sqlite_table(connection, "model_medians", model_medians)
        write_sqlite_table(connection, "holdout_fields", holdout_fields)
        write_sqlite_table(connection, "example_trajectory", example)
        write_sqlite_table(connection, "gates", gate_rows)
        connection.commit()

    raw_source = {
        "id": RAW_SOURCE_ID,
        "label": "ISIS RB1620447 public RF-µSR dataset",
        "href": "https://data.isis.stfc.ac.uk/doi/STUDY/103197258",
        "query": {
            "engine": "ISIS DataGateway",
            "url": "https://data.isis.stfc.ac.uk/doi/STUDY/103197258",
            "description": "Public EMU Nexus runs from the RF-µSR acetone experiment.",
            "filters": [
                "300 K development and validation fields: 50–500 G",
                "202 K untouched holdout fields: 1800–2496 G",
                "46 runs selected by frozen field and chronology rules",
            ],
            "tables_used": ["ISIS investigation RB1620447 / raw Nexus dataset"],
        },
    }
    derived_source = {
        "id": DERIVED_SOURCE_ID,
        "label": "T413 frozen causal analysis",
        "href": "https://data.isis.stfc.ac.uk/doi/STUDY/103197258",
        "query": {
            "engine": "Python 3.12",
            "query": "python t413_live_state_handover.py --splits development,validation,holdout --suffix FULL",
            "description": "Frozen RF-on/RF-off ARA relation, causal temporal state predictor, comparator scoring, and field bootstrap.",
            "language": "shell",
            "filters": [
                "Corrected time 0.25–6.0 microseconds",
                "Development before 2.5 microseconds",
                "Future at or after 2.5 microseconds",
                "Eight-bin rebinning",
            ],
            "metric_definitions": [
                "ARA x = 2 R_on / (R_on + R_off)",
                "Primary RMSE is count-weighted future error in the first causal spatial relation mode",
                "Relational gate requires the full model to beat persistence, AR(1), no-cross-coupling, and broken-order controls",
            ],
            "tables_used": [
                "T413_SOURCE_MANIFEST.csv",
                "T413_FULL_RUN_METRICS.csv",
                "T413_FULL_PREDICTIONS.csv",
                "T413_FULL_RESULTS.json",
            ],
        },
    }
    sources = [
        raw_source,
        derived_source,
        table_source(HEADLINE_SOURCE_ID, "T413 headline metrics", "headline", "Frozen aggregate holdout metrics."),
        table_source(MODELS_SOURCE_ID, "T413 model medians", "model_medians", "Median future RMSE by model and split."),
        table_source(FIELDS_SOURCE_ID, "T413 holdout field detail", "holdout_fields", "Per-run untouched holdout metrics."),
        table_source(
            TRAJECTORY_SOURCE_ID,
            "T413 example trajectory",
            "example_trajectory",
            "Observed and causally forecast first-mode trajectory at the fixed 2160 G example field.",
        ),
        table_source(GATES_SOURCE_ID, "T413 frozen gates", "gates", "Predeclared interpretation gates and evidence."),
    ]

    manifest = {
        "version": 1,
        "surface": "report",
        "title": TITLE,
        "description": "Frozen causal test of an RF-on/RF-off ARA relation in a coupled muon–electron spin system.",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "cards": [
            {
                "id": "holdout-card",
                "description": "Untouched 202 K high-field branch runs.",
                "dataset": "headline",
                "sourceId": HEADLINE_SOURCE_ID,
                "metrics": [{"label": "Holdout runs", "field": "holdout_runs", "format": "number"}],
            },
            {
                "id": "ara-rmse-card",
                "description": "Lower is better; count-weighted future error.",
                "dataset": "headline",
                "sourceId": HEADLINE_SOURCE_ID,
                "metrics": [
                    {"label": "Full Di-ARA RMSE", "field": "ara_rmse", "format": "number"},
                    {"label": "Gap vs AR(1)", "field": "relative_gap_vs_ar1", "format": "percent", "signed": True},
                ],
            },
            {
                "id": "harmonic-card",
                "description": "Advantage over the frozen damped-harmonic comparator.",
                "dataset": "headline",
                "sourceId": HEADLINE_SOURCE_ID,
                "metrics": [{"label": "Gain vs harmonic", "field": "relative_gain_vs_harmonic", "format": "percent", "signed": True}],
            },
        ],
        "charts": [
            {
                "id": "model-rmse-chart",
                "title": "Median future error by model and split",
                "subtitle": "Count-weighted A-mode RMSE; lower is better",
                "showDescription": True,
                "type": "bar",
                "intent": "comparison",
                "dataset": "model_medians",
                "sourceId": MODELS_SOURCE_ID,
                "encodings": {
                    "x": {"field": "model", "type": "nominal", "label": "Predictor"},
                    "y": {"field": "rmse", "type": "quantitative", "label": "Future RMSE"},
                    "color": {"field": "split", "type": "nominal", "label": "Data split"},
                    "tooltip": [
                        {"field": "split", "type": "nominal"},
                        {"field": "model", "type": "nominal"},
                        {"field": "rmse", "type": "quantitative"},
                        {"field": "run_count", "type": "quantitative"},
                    ],
                },
                "xAxisTitle": "Predictor",
                "yAxisTitle": "Future relation RMSE",
                "layout": "full",
            },
            {
                "id": "field-advantage-chart",
                "title": "Full Di-ARA advantage over one-coordinate AR(1)",
                "subtitle": "Untouched 202 K runs; positive values favour the full two-coordinate model",
                "showDescription": True,
                "type": "scatter",
                "intent": "relationship",
                "dataset": "holdout_fields",
                "sourceId": FIELDS_SOURCE_ID,
                "encodings": {
                    "x": {"field": "field_G", "type": "quantitative", "label": "Applied field", "unit": "G"},
                    "y": {"field": "ara_advantage_vs_ar1", "type": "quantitative", "label": "AR(1) RMSE − Di-ARA RMSE"},
                    "size": {"field": "mode_variance_fraction", "type": "quantitative", "label": "First-mode variance share"},
                    "tooltip": [
                        {"field": "field_G", "type": "quantitative", "unit": "G"},
                        {"field": "ara_rmse", "type": "quantitative"},
                        {"field": "ar1_rmse", "type": "quantitative"},
                        {"field": "mode_variance_fraction", "type": "quantitative"},
                    ],
                },
                "xAxisTitle": "Applied field (G)",
                "yAxisTitle": "Positive favours full Di-ARA",
                "referenceLines": [{"axis": "y", "value": 0, "label": "equal performance", "lineStyle": "dashed"}],
                "layout": "full",
            },
            {
                "id": "example-trajectory-chart",
                "title": "Example causal forecast at 2160 G",
                "subtitle": "Observed relation mode and predictions after the frozen 2.5 µs boundary",
                "showDescription": True,
                "type": "line",
                "intent": "trend",
                "dataset": "example_trajectory",
                "sourceId": TRAJECTORY_SOURCE_ID,
                "encodings": {
                    "x": {"field": "time_us", "type": "quantitative", "label": "Corrected time", "unit": "us"},
                    "y": {
                        "fields": ["observed_A", "ara_prediction", "ar1_prediction", "harmonic_prediction"],
                        "type": "quantitative",
                        "label": "Centered live ARA relation mode A(t)",
                    },
                    "tooltip": [
                        {"field": "time_us", "type": "quantitative", "unit": "us"},
                        {"field": "observed_A", "type": "quantitative"},
                        {"field": "ara_prediction", "type": "quantitative"},
                        {"field": "ar1_prediction", "type": "quantitative"},
                        {"field": "harmonic_prediction", "type": "quantitative"},
                    ],
                },
                "xAxisTitle": "Corrected time (µs)",
                "yAxisTitle": "Centered live ARA relation mode A(t)",
                "referenceLines": [
                    {"axis": "x", "value": 2.5, "label": "forecast begins", "lineStyle": "dashed"},
                    {"axis": "y", "value": 0, "label": "equal-rate ridge", "lineStyle": "dotted"},
                ],
                "layout": "full",
            },
        ],
        "tables": [
            {
                "id": "gate-table",
                "title": "Frozen interpretation gates",
                "subtitle": "The primary relational gate controls the overall verdict",
                "showDescription": True,
                "dataset": "gates",
                "sourceId": GATES_SOURCE_ID,
                "defaultSort": {"field": "gate", "direction": "asc"},
                "density": "spacious",
                "layout": "full",
                "columns": [
                    {"field": "gate", "label": "Gate", "type": "text"},
                    {"field": "status", "label": "Verdict", "type": "text"},
                    {"field": "evidence", "label": "Evidence", "type": "text"},
                ],
            },
            {
                "id": "field-table",
                "title": "Untouched holdout detail",
                "subtitle": "Twenty 202 K high-field runs, ordered by applied field",
                "showDescription": True,
                "dataset": "holdout_fields",
                "sourceId": FIELDS_SOURCE_ID,
                "defaultSort": {"field": "field_G", "direction": "asc"},
                "density": "dense",
                "layout": "full",
                "columns": [
                    {"field": "field_G", "label": "Field (G)", "format": "number"},
                    {"field": "ara_rmse", "label": "Di-ARA RMSE", "format": "number"},
                    {"field": "ar1_rmse", "label": "AR(1) RMSE", "format": "number"},
                    {"field": "ara_advantage_vs_ar1", "label": "Advantage vs AR(1)", "format": "number", "movement": True},
                    {"field": "mode_variance_fraction", "label": "First-mode share", "format": "percent"},
                ],
            },
        ],
        "blocks": [
            {"id": "title", "type": "markdown", "body": f"# {TITLE}"},
            {
                "id": "summary",
                "type": "markdown",
                "sourceId": DERIVED_SOURCE_ID,
                "body": (
                    "## Technical summary\n\n"
                    "**The frozen temporal Di-ARA predictor is not supported in this operationalisation.** "
                    "On 20 untouched 202 K runs, its median future RMSE was **0.04684**, compared with "
                    "**0.04646** for the simpler one-coordinate AR(1). The bootstrap interval for the full "
                    "model's improvement over the best simple comparator crossed zero.\n\n"
                    "The negative result is narrow rather than empty. The direct RF-on/RF-off ARA cut carried "
                    "forecastable state: both causal state models beat persistence, and the full model beat the "
                    "frozen damped-harmonic comparator by **18.6%**. What failed was the stronger claim that the "
                    "causal perpendicular change coordinate added reliable information beyond the scalar live relation."
                ),
            },
            {"id": "metrics", "type": "metric-strip", "cardIds": ["holdout-card", "ara-rmse-card", "harmonic-card"]},
            {
                "id": "finding-models",
                "type": "markdown",
                "sourceId": DERIVED_SOURCE_ID,
                "body": (
                    "## The second temporal cut did not improve the simplest state model\n\n"
                    "The ranking was stable enough to interpret: persistence was clearly worst, while AR(1), the "
                    "diagonal two-state model, and full Di-ARA clustered tightly. Full cross-coupling lost to AR(1) "
                    "on 13 of 20 holdout runs. That is the exact comparison the primary gate was designed to make."
                ),
            },
            {"id": "model-chart", "type": "chart", "chartId": "model-rmse-chart", "layout": "full"},
            {
                "id": "model-chart-note",
                "type": "markdown",
                "body": (
                    "The bars compare the same future window and denominator for every model. The full relation "
                    "model does useful smoothing relative to persistence and the harmonic fit, but the direct live "
                    "coordinate with one-step memory is enough to match or slightly exceed it."
                ),
            },
            {
                "id": "finding-fields",
                "type": "markdown",
                "sourceId": DERIVED_SOURCE_ID,
                "body": (
                    "## The field-by-field result is mixed\n\n"
                    "The full model beats AR(1) at 7 of 20 fields. Wins and losses alternate across the scan rather "
                    "than forming one decisive region. The median first relation mode contains only about **12.1%** "
                    "of development-window variance, so a weak first mode and count noise are material limitations."
                ),
            },
            {"id": "field-chart", "type": "chart", "chartId": "field-advantage-chart", "layout": "full"},
            {
                "id": "field-chart-note",
                "type": "markdown",
                "body": (
                    "Points above zero favour the full temporal Di-ARA; points below zero favour scalar AR(1). "
                    "Point size shows how much development variance the first spatial relation mode retained. "
                    "There is no visual basis here for rescuing the failed aggregate gate with a selected field."
                ),
            },
            {
                "id": "trajectory-heading",
                "type": "markdown",
                "body": (
                    "## The causal boundary is visible in the waveform\n\n"
                    "The example below was fixed at the central selected holdout field, not chosen for good model "
                    "performance. Every fit stops at 2.5 µs; only the observed line continues from measured data."
                ),
            },
            {"id": "trajectory-chart", "type": "chart", "chartId": "example-trajectory-chart", "layout": "full"},
            {
                "id": "trajectory-note",
                "type": "markdown",
                "body": (
                    "The forecast models mainly capture relaxation toward the equal-rate ridge. The full model's "
                    "extra path coordinate changes the forecast slightly, but not enough to improve the population "
                    "score reliably."
                ),
            },
            {
                "id": "scope",
                "type": "markdown",
                "sourceId": RAW_SOURCE_ID,
                "body": (
                    "## Scope and measurement\n\n"
                    "Each public Nexus run records 96 matched detector histories under independently switched RF-on "
                    "and RF-off conditions. The direct ARA coordinate is "
                    "`x = 2 R_on / (R_on + R_off)`, with `x = 1` the equal recorded-rate ridge. The first causal "
                    "spatial relation mode is `A(t)`; its strictly backward first difference is the proposed "
                    "perpendicular traversal coordinate `B(t)`. Development used 0.25–2.5 µs and scoring used "
                    "2.5–6.0 µs. The holdout changed both temperature and hyperfine branch."
                ),
            },
            {
                "id": "methods",
                "type": "markdown",
                "sourceId": DERIVED_SOURCE_ID,
                "body": (
                    "## Frozen design and validation\n\n"
                    "Runs were selected by temperature, field, and chronology before response inspection. Thirteen "
                    "300 K development runs and 13 interleaved validation runs preceded 20 untouched 202 K high-field "
                    "holdouts. The protocol and implementation were hashed before holdout execution. A separate "
                    "validator exactly recomputed all saved primary RMSE values and confirmed that no holdout split "
                    "appeared in the pre-holdout result file."
                ),
            },
            {"id": "gate-table-block", "type": "table", "tableId": "gate-table", "layout": "full"},
            {
                "id": "limitations",
                "type": "markdown",
                "body": (
                    "## What remains uncertain\n\n"
                    "This is an ensemble-state test, not an individual-muon or neutrino-timing test. RF-on/RF-off is "
                    "a clean observed relation, but the perpendicular temporal cut is derived from its causal change "
                    "rather than from an independently detected electron-spin channel. The leading mode is weak, and "
                    "the harmonic comparator is not the strongest baseline in these short, noisy development windows. "
                    "Accordingly, beating that harmonic fit does not outweigh the primary failure against AR(1)."
                ),
            },
            {
                "id": "next-steps",
                "type": "markdown",
                "body": (
                    "## Recommended next test\n\n"
                    "Keep the direct paired-state ARA cut, but replace the derived path coordinate with a genuinely "
                    "independent second observable—such as a separately measured spin quadrature or electron-sensitive "
                    "channel. Freeze that channel before forecasting. This directly tests whether Di-ARA adds information "
                    "rather than asking a noisy derivative of the first axis to do so."
                ),
            },
            {
                "id": "details-heading",
                "type": "markdown",
                "body": "## Holdout audit detail\n\nThe table preserves every untouched field result rather than showing only favorable examples.",
            },
            {"id": "field-table-block", "type": "table", "tableId": "field-table", "layout": "full"},
            {
                "id": "questions",
                "type": "markdown",
                "body": (
                    "## Further questions\n\n"
                    "- Does an independently measured second spin component turn the narrow orientation advantage into "
                    "a stable relational gain?\n\n"
                    "- Is the first-mode weakness specific to this sparse RF field subsample or intrinsic to the chosen "
                    "ensemble cut?\n\n"
                    "- Does the direct scalar ARA coordinate retain its AR(1) advantage under a wholly different muonium "
                    "sample and instrument?"
                ),
            },
        ],
    }

    artifact = {
        "surface": "report",
        "manifest": manifest,
        "snapshot": {
            "version": 1,
            "generatedAt": manifest["generatedAt"],
            "status": "ready",
            "datasets": {
                "headline": headline,
                "model_medians": model_medians,
                "holdout_fields": holdout_fields,
                "example_trajectory": example,
                "gates": gate_rows,
            },
        },
        "sources": sources,
    }
    OUTPUT.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()

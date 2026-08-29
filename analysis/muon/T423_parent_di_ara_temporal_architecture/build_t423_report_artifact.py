#!/usr/bin/env python3
"""Build the canonical portable technical report artifact for T423."""

from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
T421_RESULTS = HERE.parent / "T421_child_singularity_parent_ridge" / "results"
OUTPUT = HERE / "artifact.json"
STAGES = ("DEVELOPMENT", "VALIDATION", "HOLDOUT")


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def stage_results() -> dict[str, dict]:
    return {stage: read_json(RESULTS / f"T423_{stage}_RESULTS.json") for stage in STAGES}


def availability_rows(results: dict[str, dict], audit: dict) -> list[dict]:
    rows = []
    for stage in STAGES:
        diagnostic = audit["stage_diagnostics"][stage.lower()]
        values = (
            ("Opposite child intervals", diagnostic["opposite_crossing_intervals"]),
            ("Intervals with causal rows", diagnostic["intervals_with_causal_rows"]),
            ("Causal prediction rows", diagnostic["causal_prediction_rows"]),
            ("Q=1 parent handovers", 0),
        )
        for measure, value in values:
            rows.append({"stage": stage.title(), "measure": measure, "count": value})
    return rows


def interval_rows() -> list[dict]:
    output = []
    for stage in STAGES:
        predictions = read_csv(RESULTS / f"T423_{stage}_PREDICTIONS.csv")
        prediction_counts = {}
        for row in predictions:
            prediction_counts[row["interval_id"]] = prediction_counts.get(row["interval_id"], 0) + 1
        for row in read_csv(RESULTS / f"T423_{stage}_INTERVALS.csv"):
            native_capacity = max(
                0,
                math.floor(float(row["end_position"])) - math.ceil(float(row["start_position"])) + 1,
            )
            output.append({
                "stage": stage.title(), "run": row["run"], "period": row["period"],
                "field_G": float(row["field_G"]), "interval_index": int(row["interval_index"]),
                "interval_id": row["interval_id"],
                "direction": f"{row['start_direction'].replace('_', ' ')} → {row['end_direction'].replace('_', ' ')}",
                "start_time_us": float(row["start_time_us"]), "end_time_us": float(row["end_time_us"]),
                "duration_us": float(row["duration_us"]), "native_capacity": native_capacity,
                "causal_rows": prediction_counts.get(row["interval_id"], 0),
                "has_return_C1": "yes" if int(row["has_return_C1"]) else "no",
            })
    return output


def timeline_example(stage: str, run: str, period: str) -> list[dict]:
    source = read_csv(T421_RESULTS / f"T421_{stage}_TIMELINE.csv")
    rows = [row for row in source if row["run"] == run and row["period"] == period]
    output = []
    labels = (
        ("openness_U", "Child openness U"),
        ("closure_R", "Child closure R"),
        ("parent_H", "Candidate parent H"),
        ("signed_parent_Q", "Candidate parent Q"),
    )
    for row in rows:
        for field, label in labels:
            output.append({
                "stage": stage.title(), "run": run, "period": period,
                "field_G": float(row["field_G"]), "time_us": float(row["time_us"]),
                "series": label, "coordinate": float(row[field]),
            })
        output.append({
            "stage": stage.title(), "run": run, "period": period,
            "field_G": float(row["field_G"]), "time_us": float(row["time_us"]),
            "series": "ARA ridge", "coordinate": 1.0,
        })
    return output


def model_rows(results: dict[str, dict], freeze: dict) -> list[dict]:
    mae = results["DEVELOPMENT"]["summary"]["field_balanced_mae_us"]
    rows = []
    for model in ("M0", "M1", "M2"):
        rows.append({
            "model": model,
            "architecture": {
                "M0": "child C1 → child C2",
                "M1": "C1 → compressed H → C2",
                "M2": "C1 → PA → PB → C2",
            }[model],
            "feature_count": len(freeze["models"][model]["features"]),
            "training_rows": freeze["models"][model]["training_rows"],
            "development_MAE_us": mae[model],
            "out_of_sample_status": "UNAVAILABLE — zero validation and holdout rows",
        })
    return rows


def gate_rows(results: dict[str, dict]) -> list[dict]:
    validation = results["VALIDATION"]["summary"]
    holdout = results["HOLDOUT"]["summary"]
    return [
        {"gate": "G1", "criterion": "≥20 validation and ≥10 holdout opposite child intervals", "observed": f"validation {validation['interval_count']}; holdout {holdout['interval_count']}", "status": "FAIL — availability"},
        {"gate": "G2", "criterion": "M2 beats M0 in validation", "observed": "zero causal validation rows", "status": "UNAVAILABLE"},
        {"gate": "G3", "criterion": "M2 beats M1 in validation", "observed": "zero causal validation rows", "status": "UNAVAILABLE"},
        {"gate": "G4", "criterion": "M2 advantages remain positive in holdout", "observed": "zero causal holdout rows", "status": "UNAVAILABLE"},
        {"gate": "G5", "criterion": "≥60% expected Q=1 parent orientation", "observed": "no Q=1 events in any split", "status": "UNAVAILABLE"},
        {"gate": "G6", "criterion": "H ridge exposure at Q=1 crossing", "observed": "no Q=1 events", "status": "UNAVAILABLE"},
        {"gate": "G7", "criterion": "Correct M2 beats wrong and reversed histories", "observed": "no causal validation rows", "status": "UNAVAILABLE"},
        {"gate": "G8", "criterion": "M2 over M1 in RF-on and RF-off validation", "observed": "no causal validation rows", "status": "UNAVAILABLE"},
    ]


def bridge_rows() -> list[dict]:
    return [
        {"order": 1, "anchor": "Physical identity", "entry": "Full 96-detector muoniated-acetone ensemble spin relation; population level, not an individual muon or neutrino."},
        {"order": 2, "anchor": "Observed source", "entry": "Causal T421 timelines sampled after the fixed 2.25 µs phase-basis calibration boundary."},
        {"order": 3, "anchor": "Child ARA cut", "entry": "U and R are independent 0–2 child coordinates; opposite U=R crossing directions operationalize relational C1 and C2."},
        {"order": 4, "anchor": "Candidate parent", "entry": "H is the compressed parent ridge coordinate; Q was proposed as the internal PA/PB orientation coordinate."},
        {"order": 5, "anchor": "Discriminating test", "entry": "Compare child-only M0, compressed-parent M1 and decompressed-parent M2 while predicting remaining time to the next opposite child crossover."},
        {"order": 6, "anchor": "Actual availability", "entry": "Four development prediction rows, zero validation rows, zero holdout rows and zero Q=1 events."},
        {"order": 7, "anchor": "ARA verdict", "entry": "The archive shows successive child crossovers but cannot reveal whether traversal is direct, passes one parent state, or crosses PA→PB."},
        {"order": 8, "anchor": "Missing bridge", "entry": "A longer or finer causal timeline that resolves multiple native slices inside each child interval and crosses Q=1 before returning to C1."},
    ]


def main() -> None:
    generated = datetime.now(timezone.utc).isoformat()
    results = stage_results()
    audit = read_json(RESULTS / "T423_INDEPENDENT_VALIDATION.json")
    freeze = read_json(HERE / "T423_DEVELOPMENT_FREEZE.json")
    availability = availability_rows(results, audit)
    intervals = interval_rows()
    models = model_rows(results, freeze)
    gates = gate_rows(results)
    bridge = bridge_rows()
    development_example = timeline_example("DEVELOPMENT", "EMU00070055", "RF on")
    validation_example = timeline_example("VALIDATION", "EMU00070034", "RF on")
    holdout_example = timeline_example("HOLDOUT", "EMU00070299", "RF on")
    pivot = [{
        "order": 1,
        "from": "Frozen C1/C2, H/Q and model definitions",
        "to": "Unchanged",
        "trigger": "Archive contained insufficient temporal grain",
        "effect": "No geometry, identity, rung, axis or endpoint was moved; the result is recorded as scientifically unavailable.",
    }]
    cards = [{
        "development_rows": audit["stage_diagnostics"]["development"]["causal_prediction_rows"],
        "validation_rows": audit["stage_diagnostics"]["validation"]["causal_prediction_rows"],
        "holdout_rows": audit["stage_diagnostics"]["holdout"]["causal_prediction_rows"],
        "audit_passed": audit["passed_count"],
        "audit_total": audit["check_count"],
    }]

    availability_path = RESULTS / "T423_REPORT_AVAILABILITY.csv"
    intervals_path = RESULTS / "T423_REPORT_INTERVAL_GRAIN.csv"
    examples_path = RESULTS / "T423_REPORT_TIMELINE_EXAMPLES.csv"
    write_csv(availability_path, availability)
    write_csv(intervals_path, intervals)
    write_csv(examples_path, development_example + validation_example + holdout_example)

    sources = [
        {"id": "protocol", "label": "T423 frozen protocol", "path": "T423_FROZEN_PROTOCOL.md", "query": {"engine": "filesystem", "language": "sql", "sql": "SELECT * FROM read_text('T423_FROZEN_PROTOCOL.md')", "description": "Read the identity, temporal order, nested architectures, controls and frozen gates.", "tables_used": ["T423_FROZEN_PROTOCOL.md"], "filters": ["Frozen before development scoring"], "metric_definitions": ["C1/C2 are opposite U=R crossing directions", "H=1 parent ridge", "Q=1 proposed PA/PB handover"]}},
        {"id": "results", "label": "T423 frozen stage results", "path": "results/T423_VALIDATION_RESULTS.json", "query": {"engine": "duckdb", "language": "sql", "sql": "SELECT * FROM read_json_auto('results/T423_DEVELOPMENT_RESULTS.json') UNION ALL SELECT * FROM read_json_auto('results/T423_VALIDATION_RESULTS.json') UNION ALL SELECT * FROM read_json_auto('results/T423_HOLDOUT_RESULTS.json')", "description": "Read saved interval counts, prediction counts, model errors, controls and gates.", "tables_used": ["results/T423_DEVELOPMENT_RESULTS.json", "results/T423_VALIDATION_RESULTS.json", "results/T423_HOLDOUT_RESULTS.json"], "filters": ["Reads at or after 2.25 µs", "Development-only fitting"], "metric_definitions": ["Interval-balanced median absolute error in µs"]}},
        {"id": "intervals", "label": "T423 child intervals and native grain", "path": "results/T423_REPORT_INTERVAL_GRAIN.csv", "query": {"engine": "duckdb", "language": "sql", "sql": "SELECT * FROM read_csv_auto('results/T423_REPORT_INTERVAL_GRAIN.csv')", "description": "Show every opposite child-crossing interval and how many native samples fall inside it.", "tables_used": ["results/T423_DEVELOPMENT_INTERVALS.csv", "results/T423_VALIDATION_INTERVALS.csv", "results/T423_HOLDOUT_INTERVALS.csv"], "filters": ["Successive opposite U=R crossing directions"], "metric_definitions": ["Native capacity = floor(end position) − ceil(start position) + 1"]}},
        {"id": "timelines", "label": "T421 causal timelines used by T423", "path": "results/T423_REPORT_TIMELINE_EXAMPLES.csv", "query": {"engine": "duckdb", "language": "sql", "sql": "SELECT * FROM read_csv_auto('results/T423_REPORT_TIMELINE_EXAMPLES.csv')", "description": "Worked examples of child U/R and candidate-parent H/Q on their labeled 0–2 coordinates.", "tables_used": ["T421_DEVELOPMENT_TIMELINE.csv", "T421_VALIDATION_TIMELINE.csv", "T421_HOLDOUT_TIMELINE.csv"], "filters": ["Three preselected illustrative sequences"], "metric_definitions": ["ARA ridge = 1"]}},
        {"id": "audit", "label": "Independent T423 validation", "path": "results/T423_INDEPENDENT_VALIDATION.json", "query": {"engine": "duckdb", "language": "sql", "sql": "SELECT * FROM read_json_auto('results/T423_INDEPENDENT_VALIDATION.json')", "description": "Independently verify hashes, crossings, causality, predictions and saved counts; separately flag scientific non-identification.", "tables_used": ["results/T423_INDEPENDENT_VALIDATION.json"], "filters": ["125 registered arithmetic/provenance checks"], "metric_definitions": ["Arithmetic PASS does not imply scientific availability"]}},
    ]

    charts = [
        {"id": "chart_availability", "title": "The archive contains crossings but not a scoreable parent traversal", "subtitle": "Counts are shown separately; a crossing interval is not automatically a causal prediction interval", "showDescription": True, "intent": "comparison", "question": "Which rung of the frozen temporal architecture is actually observed?", "rationale": "Grouped counts prevent G1 crossing availability from being confused with model-row or Q-handover availability.", "type": "bar", "dataset": "availability", "sourceId": "audit", "encodings": {"x": {"field": "stage", "type": "nominal", "label": "Frozen split"}, "y": {"field": "count", "type": "quantitative", "label": "Count"}, "color": {"field": "measure", "type": "nominal", "label": "Availability measure"}, "tooltip": [{"field": "measure", "type": "nominal", "label": "Measure"}, {"field": "count", "type": "quantitative", "label": "Count"}]}, "xAxisTitle": "Frozen split", "yAxisTitle": "Intervals, rows or events", "layout": "full"},
        {"id": "chart_grain", "title": "Most child intervals are narrower than the native temporal sampling", "subtitle": "At least two interior samples were required to form a causal prediction interval", "showDescription": True, "intent": "comparison", "question": "Why can validation and holdout not score M0/M1/M2?", "rationale": "Native sample capacity directly exposes the measurement-resolution bottleneck for each registered interval.", "type": "bar", "dataset": "intervals", "sourceId": "intervals", "encodings": {"x": {"field": "interval_id", "type": "nominal", "label": "Child interval"}, "y": {"field": "native_capacity", "type": "quantitative", "label": "Interior native samples"}, "color": {"field": "stage", "type": "nominal", "label": "Frozen split"}, "tooltip": [{"field": "field_G", "type": "quantitative", "label": "Applied field", "unit": "G"}, {"field": "duration_us", "type": "quantitative", "label": "Interpolated interval duration", "unit": "µs"}, {"field": "causal_rows", "type": "quantitative", "label": "Saved causal rows"}, {"field": "direction", "type": "nominal", "label": "Child direction"}]}, "xAxisTitle": "Run, RF period and interval index", "yAxisTitle": "Native samples inside interval", "layout": "full"},
        {"id": "chart_duration", "title": "Child crossover duration changes with field and split", "subtitle": "Interpolated duration is visible even when no native sample lies inside the interval", "showDescription": True, "intent": "relationship", "question": "Is the missing forecast row a missing event or a sampling-grain problem?", "rationale": "Field versus interval duration shows that the event exists continuously but often falls between saved sample centres.", "type": "scatter", "dataset": "intervals", "sourceId": "intervals", "encodings": {"x": {"field": "field_G", "type": "quantitative", "label": "Applied magnetic field", "unit": "G"}, "y": {"field": "duration_us", "type": "quantitative", "label": "Child interval duration", "unit": "µs"}, "color": {"field": "stage", "type": "nominal", "label": "Frozen split"}, "tooltip": [{"field": "run", "type": "nominal", "label": "Run"}, {"field": "period", "type": "nominal", "label": "RF period"}, {"field": "native_capacity", "type": "quantitative", "label": "Native samples"}, {"field": "has_return_C1", "type": "nominal", "label": "Returns to C1"}]}, "xAxisTitle": "Applied magnetic field (G)", "yAxisTitle": "Interpolated child interval duration (µs)", "layout": "full"},
        {"id": "chart_development", "title": "Development example: the only source of model rows", "subtitle": "EMU00070055 · RF on · 482 G; all coordinates retain their own 0–2 identity", "showDescription": True, "intent": "trend", "question": "What chronological geometry was available during fitting?", "rationale": "The direct trace shows child U/R, candidate-parent H/Q and the fixed ARA ridge without flattening them into one budget.", "type": "line", "dataset": "development_example", "sourceId": "timelines", "encodings": {"x": {"field": "time_us", "type": "quantitative", "label": "Corrected ensemble time", "unit": "µs"}, "y": {"field": "coordinate", "type": "quantitative", "label": "ARA coordinate", "unit": "0–2"}, "color": {"field": "series", "type": "nominal", "label": "Relational coordinate"}, "tooltip": [{"field": "run", "type": "nominal", "label": "Run"}, {"field": "period", "type": "nominal", "label": "RF period"}, {"field": "field_G", "type": "quantitative", "label": "Field", "unit": "G"}]}, "xAxisTitle": "Corrected ensemble time (µs)", "yAxisTitle": "Independent ARA coordinate (0–2)", "layout": "full"},
        {"id": "chart_validation", "title": "Validation example: crossings occur between saved sample centres", "subtitle": "EMU00070034 · RF on · 356 G; no interval contains two causal native rows", "showDescription": True, "intent": "trend", "question": "Why can the registered validation comparison not be scored?", "rationale": "The chronological cut shows real U/R ordering changes while exposing the sampling gap that blocks forward evaluation.", "type": "line", "dataset": "validation_example", "sourceId": "timelines", "encodings": {"x": {"field": "time_us", "type": "quantitative", "label": "Corrected ensemble time", "unit": "µs"}, "y": {"field": "coordinate", "type": "quantitative", "label": "ARA coordinate", "unit": "0–2"}, "color": {"field": "series", "type": "nominal", "label": "Relational coordinate"}, "tooltip": [{"field": "run", "type": "nominal", "label": "Run"}, {"field": "field_G", "type": "quantitative", "label": "Field", "unit": "G"}]}, "xAxisTitle": "Corrected ensemble time (µs)", "yAxisTitle": "Independent ARA coordinate (0–2)", "layout": "full"},
        {"id": "chart_holdout", "title": "High-field holdout: a return pair exists, but still no causal slice", "subtitle": "EMU00070299 · RF on · 2448 G; two child crossings occur almost back-to-back", "showDescription": True, "intent": "trend", "question": "Does the untouched regime reveal the proposed PA→PB parent path?", "rationale": "The worked holdout keeps the child and parent coordinates visible while showing why neither prediction nor Q-order can be evaluated.", "type": "line", "dataset": "holdout_example", "sourceId": "timelines", "encodings": {"x": {"field": "time_us", "type": "quantitative", "label": "Corrected ensemble time", "unit": "µs"}, "y": {"field": "coordinate", "type": "quantitative", "label": "ARA coordinate", "unit": "0–2"}, "color": {"field": "series", "type": "nominal", "label": "Relational coordinate"}, "tooltip": [{"field": "run", "type": "nominal", "label": "Run"}, {"field": "field_G", "type": "quantitative", "label": "Field", "unit": "G"}]}, "xAxisTitle": "Corrected ensemble time (µs)", "yAxisTitle": "Independent ARA coordinate (0–2)", "layout": "full"},
    ]

    manifest = {
        "version": 1, "surface": "report", "title": "T423 — Parent Di-ARA Temporal Architecture",
        "description": "Frozen comparison of direct child alternation, a compressed parent H, and a decompressed PA→PB parent traversal.",
        "generatedAt": generated, "sources": sources,
        "cards": [
            {"id": "card_dev", "dataset": "cards", "sourceId": "audit", "description": "Causal rows used to fit every nested development model.", "metrics": [{"label": "Development rows", "field": "development_rows", "format": "number"}]},
            {"id": "card_val", "dataset": "cards", "sourceId": "audit", "description": "Untouched validation rows available for nested scoring.", "metrics": [{"label": "Validation rows", "field": "validation_rows", "format": "number"}]},
            {"id": "card_hold", "dataset": "cards", "sourceId": "audit", "description": "Untouched high-field holdout rows available for nested scoring.", "metrics": [{"label": "Holdout rows", "field": "holdout_rows", "format": "number"}]},
            {"id": "card_audit", "dataset": "cards", "sourceId": "audit", "description": "Independent arithmetic and provenance checks passed.", "metrics": [{"label": "Audit passed", "field": "audit_passed", "format": "number"}, {"label": "of", "field": "audit_total", "format": "number"}]},
        ],
        "charts": charts,
        "tables": [
            {"id": "table_models", "title": "Nested architectures and the underdetermined development fit", "subtitle": "The development MAEs are in-sample diagnostics only; four rows cannot identify 9–15 feature models", "showDescription": True, "dataset": "models", "sourceId": "results", "density": "spacious", "layout": "full", "columns": [{"field": "model", "label": "Model", "type": "text"}, {"field": "architecture", "label": "ARA traversal", "type": "text"}, {"field": "feature_count", "label": "Features", "type": "number"}, {"field": "training_rows", "label": "Training rows", "type": "number"}, {"field": "development_MAE_us", "label": "Development MAE (µs)", "type": "number"}, {"field": "out_of_sample_status", "label": "Out-of-sample status", "type": "text"}]},
            {"id": "table_gates", "title": "Frozen gates", "subtitle": "UNAVAILABLE means the required out-of-sample object did not exist; it is not a pass and not a directional reversal", "showDescription": True, "dataset": "gates", "sourceId": "protocol", "density": "spacious", "layout": "full", "columns": [{"field": "gate", "label": "Gate", "type": "text"}, {"field": "criterion", "label": "Frozen criterion", "type": "text"}, {"field": "observed", "label": "Observed", "type": "text"}, {"field": "status", "label": "Status", "type": "text"}]},
            {"id": "table_bridge", "title": "Relational Bridge Map", "subtitle": "The chain stops at temporal availability rather than assigning the nearest unobserved parent identity", "showDescription": True, "dataset": "bridge", "sourceId": "protocol", "defaultSort": {"field": "order", "direction": "asc"}, "density": "spacious", "layout": "full", "columns": [{"field": "order", "label": "Step", "type": "number"}, {"field": "anchor", "label": "Anchor", "type": "text"}, {"field": "entry", "label": "Recorded relation", "type": "text"}]},
            {"id": "table_pivot", "title": "Pivot Log", "subtitle": "No after-view change to the identity, geometry or endpoint", "showDescription": True, "dataset": "pivot", "sourceId": "protocol", "density": "spacious", "layout": "full", "columns": [{"field": "order", "label": "Step", "type": "number"}, {"field": "from", "label": "Frozen definition", "type": "text"}, {"field": "to", "label": "After scoring", "type": "text"}, {"field": "trigger", "label": "Data result", "type": "text"}, {"field": "effect", "label": "Methodological effect", "type": "text"}]},
        ],
        "blocks": [
            {"id": "title", "type": "markdown", "body": "# T423 — Parent Di-ARA Temporal Architecture"},
            {"id": "summary", "type": "markdown", "sourceId": "audit", "body": "## Outcome first\n\n**The registered architecture comparison is SCIENTIFICALLY UNAVAILABLE in this archive.** T423 found 4 development, 7 validation and 5 holdout opposite-direction child intervals, but only four total causal prediction rows—all in development. Validation and holdout contain zero scoreable rows. No split contains a `Q=1` crossing inside a selected child interval, so the proposed internal parent `PA→PB` handover is not directly observed.\n\nThis does **not** select M0, M1 or M2, and it does not overturn T421's child-singularity/parent-ridge relation. It says the current saved timeline is too coarse and too short to test how the system travels between those landmarks. The independent audit reproduced 125/125 calculations and hashes; scientific unavailability is therefore a data-grain result, not a broken file or arithmetic error."},
            {"id": "metrics", "type": "metric-strip", "cardIds": ["card_dev", "card_val", "card_hold", "card_audit"]},
            {"id": "availability_heading", "type": "markdown", "body": "## Crossings are visible; complete temporal architecture is not\n\nThe frozen G1 gate counted opposite child intervals. The causal primary needs something stricter: at least two saved sample centres inside an interval so a present-state prediction can be compared with its future endpoint. That second object vanishes out of sample. `Q=1` availability vanishes in every split."},
            {"id": "availability", "type": "chart", "chartId": "chart_availability"},
            {"id": "grain_heading", "type": "markdown", "body": "## The bottleneck is temporal resolution, not a missing U/R event\n\nInterpolated U=R crossovers occur between samples, so their start, end and duration can be located. Most intervals nevertheless contain fewer than two native readings. Widening those intervals after seeing this result would change the child identity and is therefore forbidden in T423."},
            {"id": "grain", "type": "chart", "chartId": "chart_grain"},
            {"id": "duration", "type": "chart", "chartId": "chart_duration"},
            {"id": "dev_heading", "type": "markdown", "body": "## Development shows why the numerical M2 advantage is not evidence\n\nThe only four prediction rows come from two intervals in two fields. M2 uses 15 features plus an intercept. Fixed ridge regression returns numbers, but the fit is underdetermined and essentially in-sample interpolation. Its tiny MAE and large control separation cannot be promoted to a model comparison."},
            {"id": "development", "type": "chart", "chartId": "chart_development"},
            {"id": "models", "type": "table", "tableId": "table_models"},
            {"id": "val_heading", "type": "markdown", "body": "## Validation contains child alternation but no causal slice inside it\n\nThis example preserves the actual ARA geometry: U and R exchange order, while H and Q remain separate candidate-parent coordinates. The crossing-to-crossing span falls between stored samples, so none of M0, M1 or M2 can receive a fair untouched score."},
            {"id": "validation", "type": "chart", "chartId": "chart_validation"},
            {"id": "hold_heading", "type": "markdown", "body": "## Holdout reaches a return pair without observing PA→PB\n\nThe high-field example includes two close child crossings, but no native prediction slice between them and no Q=1 crossing. T423 therefore cannot decide whether the return goes `C1→C2`, `C1→H→C2`, or `C1→PA→PB→C2`."},
            {"id": "holdout", "type": "chart", "chartId": "chart_holdout"},
            {"id": "scope", "type": "markdown", "sourceId": "protocol", "body": "## Who, what, when, where, why and how\n\n- **Who:** the full 96-detector muoniated-acetone ensemble; not an individual muon or neutrino.\n- **What:** three nested predictors—M0 direct child alternation, M1 one compressed parent H, and M2 internally traversed parent H/Q.\n- **When:** causal T421 reads after 2.25 µs; development fits, validation and high-field holdout score untouched.\n- **Where:** child U/R on one 0–2 relation; candidate-parent H/Q on their own 0–2 relation.\n- **Why:** distinguish a parent traversal from direct child alternation.\n- **How:** fixed ridge regressions, interval-balanced errors, field bootstrap, wrong-frequency, reversal, shift, RF and parent-order controls.\n\nThe operational choice that opposite U=R crossing directions represent C1/C2 was frozen for this test. Failure of temporal grain does not validate or falsify that choice."},
            {"id": "gates", "type": "table", "tableId": "table_gates"},
            {"id": "bridge_heading", "type": "markdown", "body": "## Relational Bridge Map\n\nT423 stays anchored from physical ensemble to observed timeline to ARA cut. It stops before parent-architecture identification because the required time-resolved bridge is absent."},
            {"id": "bridge", "type": "table", "tableId": "table_bridge"},
            {"id": "pivot_heading", "type": "markdown", "body": "## Pivot Log\n\nThere was no silent pivot. The data tempted a wider interval or different C1/C2 definition, but T423 retains the frozen cut and records the comparison as unavailable."},
            {"id": "pivot", "type": "table", "tableId": "table_pivot"},
            {"id": "limits", "type": "markdown", "sourceId": "audit", "body": "## Limitations and fixed verdict\n\n**Benchmark verdict:** SUGGESTIVE / INCONCLUSIVE by the frozen status vocabulary, with the stronger clarification **SCIENTIFICALLY UNAVAILABLE** because no out-of-sample causal row exists.\n\n**ARA geometry verdict:** successive child U/R handovers are present, but the route through H/Q is unresolved. The apparent development preference for M2 is not usable evidence. The current archive also never displays the proposed Q=1 PA/PB handover inside a selected child interval.\n\n**Design lesson:** future availability gates must count causal interior samples and fitted degrees of freedom, not only interpolated crossing intervals."},
            {"id": "next", "type": "markdown", "body": "## Recommended next bridge\n\nKeep the same registered geometry and obtain a timeline with finer native sampling or a longer continuous record that contains several full `C1→C2→C1` returns and crosses Q=1. Predeclare minimum development rows relative to model dimension and require nonzero validation/holdout prediction intervals before fitting. If such data are unavailable, re-card a different observable as C1/C2 rather than silently widening these intervals."},
        ],
    }

    snapshot = {
        "version": 1, "generatedAt": generated, "status": "ready",
        "datasets": {
            "cards": cards, "availability": availability, "intervals": intervals,
            "development_example": development_example, "validation_example": validation_example,
            "holdout_example": holdout_example, "models": models, "gates": gates,
            "bridge": bridge, "pivot": pivot,
        },
        "accessIssues": [],
    }
    artifact = {"surface": "report", "manifest": manifest, "snapshot": snapshot, "sources": sources}
    OUTPUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()

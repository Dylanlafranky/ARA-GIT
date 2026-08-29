#!/usr/bin/env python3
"""Build the canonical portable technical report artifact for T422."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUTPUT = HERE / "artifact.json"
STAGES = ("DEVELOPMENT", "VALIDATION", "HOLDOUT")


def read_csv(name: str) -> list[dict]:
    with (RESULTS / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def finite(value) -> bool:
    try:
        return bool(np.isfinite(float(value)))
    except (TypeError, ValueError):
        return False


def stage_results() -> dict[str, dict]:
    return {stage: read_json(f"T422_{stage}_RESULTS.json") for stage in STAGES}


def effect_rows(results: dict[str, dict]) -> list[dict]:
    rows = []
    for stage, result in results.items():
        for direction, item in result["directions"].items():
            effect = item["ridge_exposure"]
            if effect["median"] is None:
                continue
            rows.append({
                "stage": stage.title(), "direction": direction.replace("_to_", " → "),
                "series": direction.replace("_to_", " → "),
                "ridge_exposure": effect["median"], "ci_lower": effect["ci95"][0],
                "ci_upper": effect["ci95"][1], "field_count": effect["field_count"],
                "event_count": item["event_count"], "eligible_sequences": item["eligible_sequences"],
                "attempted_sequences": item["attempted_sequences"],
            })
    return rows


def control_rows(results: dict[str, dict]) -> list[dict]:
    rows = []
    for stage, result in results.items():
        for direction, item in result["directions"].items():
            if item["ridge_exposure"]["median"] is None:
                continue
            label = f"{stage.title()} · {direction.replace('_to_', ' → ')}"
            values = (
                ("Ridge exposure", item["ridge_exposure"]["median"]),
                ("Timing advantage", item["shift"]["null_median"] - item["shift"]["real_distance"]),
                ("Wrong-frequency advantage", item["wrong_frequency_effect"]["median"]),
                ("Different-field advantage", item["mismatch_lineage_effect"]["median"]),
            )
            for control, value in values:
                rows.append({
                    "stage_direction": label, "stage": stage.title(),
                    "direction": direction.replace("_to_", " → "),
                    "control": control, "advantage": value,
                    "event_count": item["event_count"], "field_count": item["field_count"],
                })
    return rows


def rf_rows(results: dict[str, dict]) -> list[dict]:
    rows = []
    for stage, result in results.items():
        for direction, item in result["directions"].items():
            for period, value in item["rf_exposure"].items():
                if value is None:
                    continue
                rows.append({
                    "stage_direction": f"{stage.title()} · {direction.replace('_to_', ' → ')}",
                    "stage": stage.title(), "direction": direction.replace("_to_", " → "),
                    "rf_period": period, "ridge_exposure": value,
                    "event_count": item["event_count"],
                })
    return rows


def event_rows() -> list[dict]:
    rows = []
    for stage in STAGES:
        for row in read_csv(f"T422_{stage}_EVENTS.csv"):
            rows.append({
                "stage": stage.title(), "run": row["run"], "period": row["period"],
                "field_G": float(row["field_G"]), "direction": row["direction"].replace("_to_", " → "),
                "crossing_time_us": float(row["crossing_time_us"]),
                "child_coordinate": float(row["crossing_U"]), "other_bank_H": float(row["parent_H"]),
                "parent_ridge_distance": float(row["parent_ridge_distance"]),
                "ridge_exposure": float(row["ridge_exposure"]),
                "same_bank_exposure": float(row["same_bank_exposure"]),
            })
    return rows


def field_balanced_centered() -> list[dict]:
    output = []
    for stage in ("DEVELOPMENT", "VALIDATION"):
        rows = read_csv(f"T422_{stage}_EVENT_CENTERED.csv")
        for direction in ("F_to_B", "B_to_F"):
            selected = [row for row in rows if row["direction"] == direction]
            offsets = sorted({int(row["offset_reads"]) for row in selected})
            for offset in offsets:
                at_offset = [row for row in selected if int(row["offset_reads"]) == offset]
                fields = sorted({float(row["field_G"]) for row in at_offset})
                for key, label in (
                    ("child_U", "Child U"), ("child_R", "Child R"),
                    ("other_bank_H", "Other-bank H"), ("same_bank_H", "Same-bank H"),
                ):
                    field_medians = [
                        float(np.median([float(row[key]) for row in at_offset if float(row["field_G"]) == field]))
                        for field in fields
                    ]
                    output.append({
                        "stage": stage.title(), "direction": direction.replace("_to_", " → "),
                        "offset_reads": offset,
                        "offset_us": float(np.median([float(row["offset_us"]) for row in at_offset])),
                        "coordinate": label,
                        "series": f"{direction.replace('_to_', ' → ')} · {label}",
                        "median_value": float(np.median(field_medians)),
                        "field_count": len(fields),
                        "aligned_events": len({row["event_id"] for row in at_offset}),
                    })
    return output


def example_rows() -> tuple[list[dict], list[dict], str, str]:
    validation_events = read_csv("T422_VALIDATION_EVENTS.csv")
    sequence = Counter((row["run"], row["period"]) for row in validation_events).most_common(1)[0][0]
    run, period = sequence
    validation = [
        row for row in read_csv("T422_VALIDATION_TIMELINE.csv")
        if row["run"] == run and row["period"] == period and row["partition"] in ("F", "B")
    ]
    validation_output = []
    for row in validation:
        label = "Forward child" if row["partition"] == "F" else "Backward candidate parent"
        fields = (
            (("openness_U", "U"), ("closure_R", "R"))
            if row["partition"] == "F" else (("parent_H", "H"),)
        )
        for field, coordinate in fields:
            validation_output.append({
                "time_us": float(row["time_us"]), "coordinate": coordinate,
                "series": f"{label} · {coordinate}", "value": float(row[field]),
                "run": run, "period": period, "field_G": float(row["field_G"]),
            })

    holdout_timeline = read_csv("T422_HOLDOUT_TIMELINE.csv")
    holdout_run = sorted({row["run"] for row in holdout_timeline})[len({row["run"] for row in holdout_timeline}) // 2]
    holdout_period = "RF on"
    holdout = [
        row for row in holdout_timeline
        if row["run"] == holdout_run and row["period"] == holdout_period and row["partition"] in ("F", "B")
    ]
    holdout_output = []
    for row in holdout:
        for field, coordinate in (("openness_U", "U"), ("closure_R", "R")):
            holdout_output.append({
                "time_us": float(row["time_us"]), "partition": row["partition"],
                "coordinate": coordinate, "series": f"{row['partition']} · {coordinate}",
                "value": float(row[field]), "difference_U_minus_R": float(row["openness_U"]) - float(row["closure_R"]),
                "run": holdout_run, "period": holdout_period, "field_G": float(row["field_G"]),
            })
    return validation_output, holdout_output, f"{run} · {period}", f"{holdout_run} · {holdout_period}"


def quantile_rows() -> list[dict]:
    output = []
    for stage in STAGES:
        rows = read_csv(f"T422_{stage}_TIMELINE.csv")
        for partition in ("F", "B"):
            selected = [row for row in rows if row["partition"] == partition]
            for field, label in (("openness_U", "U"), ("closure_R", "R"), ("parent_H", "H")):
                values = np.asarray([float(row[field]) for row in selected])
                q = np.quantile(values, (0.05, 0.25, 0.50, 0.75, 0.95))
                output.append({
                    "stage": stage.title(), "partition": partition, "coordinate": label,
                    "n_reads": len(values), "q05": float(q[0]), "q25": float(q[1]),
                    "median": float(q[2]), "q75": float(q[3]), "q95": float(q[4]),
                })
    return output


def gate_rows(results: dict[str, dict]) -> list[dict]:
    labels = {
        "G1_availability": "≥90% sequence availability",
        "G2_bidirectional_independent_ridge": "Bidirectional independent ridge",
        "G3_timing_specificity": "Circular-shift timing specificity",
        "G4_frequency_specificity": "Correct-frequency specificity",
        "G5_lineage_specificity": "Same-lineage specificity",
        "G6_RF_robustness": "RF-on/off sign robustness",
        "G7_ring_correspondence_secondary": "Axial-ring correspondence (secondary)",
    }
    output = []
    for stage, result in results.items():
        for key, item in result["gates"].items():
            unavailable = stage == "HOLDOUT" and key != "G1_availability"
            if key == "G7_ring_correspondence_secondary" and not item.get("available", False):
                unavailable = True
            output.append({
                "stage": stage.title(), "gate_order": int(key[1]), "gate": labels[key],
                "status": "UNAVAILABLE" if unavailable else ("PASS" if item["pass"] else "FAIL"),
                "pass_numeric": int(bool(item["pass"])),
            })
    return output


def ring_rows(results: dict[str, dict]) -> list[dict]:
    output = []
    for stage, result in results.items():
        for row in result["ring_eligibility"]:
            output.append({
                "stage": stage.title(), "direction": row["direction"].replace("_to_", " → "),
                "ring": row["ring"], "wrong_ring_control": row["wrong_ring"],
                "eligible_sequences": row["eligible_sequences"],
                "attempted_sequences": row["attempted_sequences"],
                "eligibility_rate_pct": 100.0 * row["eligibility_rate"],
            })
    return output


def bridge_rows() -> list[dict]:
    return [
        {"order": 1, "anchor": "Physical identity", "entry": "Muoniated-acetone detector-population spin relation recorded by ISIS EMU; bank split is an observational cut, not two microscopic particles."},
        {"order": 2, "anchor": "Raw measurement", "entry": "96 time-binned detector-count spectra per RF period, divided into disjoint forward detectors 1–48 and backward detectors 49–96."},
        {"order": 3, "anchor": "Transformation", "entry": "RECONSTRUCTED harmonic phase path per bank; DERIVED U from local/null prediction loss, R from lag-relation magnitude, and H from lag-relation angle."},
        {"order": 4, "anchor": "ARA cut", "entry": "Child bank U=R crossover on its 0–2 ARA; opposing-bank H on a separate 0–2 candidate-parent coordinate with ridge H=1."},
        {"order": 5, "anchor": "Established translation", "entry": "Opposing detector banks are independent views of the same ensemble spin asymmetry; lag magnitude and angle describe coherence and angular progression of the reconstructed phase history."},
        {"order": 6, "anchor": "Actual finding", "entry": "Validation placed other-bank H near 1 at crossings, but the bidirectional confidence, frequency, lineage, availability, and untouched high-field replication requirements did not survive."},
        {"order": 7, "anchor": "Importance", "entry": "Pre-registered construct/instrument test: NOT SUPPORTED for an independently established parent; useful negative localization of where T421's geometry does and does not transfer."},
        {"order": 8, "anchor": "Missing bridge", "entry": "A physically independent parent observable that is not another phase transform or detector projection of the same ensemble."},
    ]


def main() -> None:
    generated = datetime.now(timezone.utc).isoformat()
    results = stage_results()
    audit = read_json("T422_INDEPENDENT_VALIDATION.json")
    effects = effect_rows(results)
    controls = control_rows(results)
    rf = rf_rows(results)
    events = event_rows()
    centered = field_balanced_centered()
    validation_example, holdout_example, validation_label, holdout_label = example_rows()
    quantiles = quantile_rows()
    gates = gate_rows(results)
    rings = ring_rows(results)
    bridge = bridge_rows()
    pivot = [{
        "order": 1,
        "from": "All reconstructed reads could enter scoring",
        "to": "Only reads at or after 2.25 µs enter scoring",
        "reason": "The inherited phase basis uses the first 2.25 µs; excluding that interval implements the confirmed no-future rule.",
        "data_forced": "Code-path inspection before first run",
        "user_confirmed": "Covered by confirmed causal card; announced before execution",
        "effect": "Fewer eligible crossings; identity, direction, coordinate and claim unchanged",
    }]
    cards = [{
        "validation_F_to_B": results["VALIDATION"]["directions"]["F_to_B"]["ridge_exposure"]["median"],
        "validation_B_to_F": results["VALIDATION"]["directions"]["B_to_F"]["ridge_exposure"]["median"],
        "holdout_crossings": sum(item["event_count"] for item in results["HOLDOUT"]["directions"].values()),
        "audit_passed": audit["passed_count"], "audit_total": audit["check_count"],
    }]

    sources = [
        {"id": "protocol", "label": "T422 frozen protocol", "path": "T422_FROZEN_PROTOCOL.md", "query": {"engine": "filesystem", "language": "sql", "sql": "SELECT * FROM read_text('T422_FROZEN_PROTOCOL.md')", "description": "Read the confirmed identity, bank split, coordinates, controls and gates.", "tables_used": ["T422_FROZEN_PROTOCOL.md"], "filters": ["Frozen before development scoring"], "metric_definitions": ["Child event: U=R; candidate-parent ridge: H=1"]}},
        {"id": "results", "label": "T422 frozen stage results", "path": "results/T422_VALIDATION_RESULTS.json", "query": {"engine": "duckdb", "language": "sql", "sql": "SELECT * FROM read_json_auto('results/T422_DEVELOPMENT_RESULTS.json') UNION ALL SELECT * FROM read_json_auto('results/T422_VALIDATION_RESULTS.json') UNION ALL SELECT * FROM read_json_auto('results/T422_HOLDOUT_RESULTS.json')", "description": "Combine frozen effects, controls, sample counts and gate outcomes.", "tables_used": ["results/T422_DEVELOPMENT_RESULTS.json", "results/T422_VALIDATION_RESULTS.json", "results/T422_HOLDOUT_RESULTS.json"], "filters": ["Reads at or after 2.25 µs", "RF periods separate", "Field-balanced medians"], "metric_definitions": ["Ridge exposure = median history |H−1| minus crossing |H−1|", "Positive control advantage favours the declared other-bank parent"]}},
        {"id": "events", "label": "T422 independent-bank crossing events", "path": "results/T422_VALIDATION_EVENTS.csv", "query": {"engine": "duckdb", "language": "sql", "sql": "SELECT * FROM read_csv_auto('results/T422_DEVELOPMENT_EVENTS.csv') UNION ALL SELECT * FROM read_csv_auto('results/T422_VALIDATION_EVENTS.csv') UNION ALL SELECT * FROM read_csv_auto('results/T422_HOLDOUT_EVENTS.csv')", "description": "Read every interpolated U=R crossing and simultaneous opposing-bank H value.", "tables_used": ["results/T422_DEVELOPMENT_EVENTS.csv", "results/T422_VALIDATION_EVENTS.csv", "results/T422_HOLDOUT_EVENTS.csv"], "filters": ["Post-calibration crossings only"], "metric_definitions": ["Every event uses disjoint child and parent detector banks"]}},
        {"id": "timelines", "label": "T422 bank-separated ARA histories", "path": "results/T422_HOLDOUT_TIMELINE.csv", "query": {"engine": "duckdb", "language": "sql", "sql": "SELECT * FROM read_csv_auto('results/T422_DEVELOPMENT_TIMELINE.csv') UNION ALL SELECT * FROM read_csv_auto('results/T422_VALIDATION_TIMELINE.csv') UNION ALL SELECT * FROM read_csv_auto('results/T422_HOLDOUT_TIMELINE.csv')", "description": "Read U, R and H histories reconstructed independently for each detector partition.", "tables_used": ["results/T422_DEVELOPMENT_TIMELINE.csv", "results/T422_VALIDATION_TIMELINE.csv", "results/T422_HOLDOUT_TIMELINE.csv"], "filters": ["Forward/backward bank and ring identity preserved"], "metric_definitions": ["All coordinates normalized to 0–2; ridge at 1"]}},
        {"id": "calibration", "label": "T422 detector-partition calibration", "path": "results/T422_VALIDATION_CALIBRATION.csv", "query": {"engine": "duckdb", "language": "sql", "sql": "SELECT * FROM read_csv_auto('results/T422_DEVELOPMENT_CALIBRATION.csv') UNION ALL SELECT * FROM read_csv_auto('results/T422_VALIDATION_CALIBRATION.csv') UNION ALL SELECT * FROM read_csv_auto('results/T422_HOLDOUT_CALIBRATION.csv')", "description": "Read harmonic-fit condition and frequency-specific eligibility for every bank and axial ring.", "tables_used": ["results/T422_DEVELOPMENT_CALIBRATION.csv", "results/T422_VALIDATION_CALIBRATION.csv", "results/T422_HOLDOUT_CALIBRATION.csv"], "filters": ["No outcome-fitted signal threshold"], "metric_definitions": ["Ring eligible only when correct-frequency improvement exceeds median wrong-frequency improvement in both paired rings"]}},
        {"id": "audit", "label": "Independent T422 validation", "path": "results/T422_INDEPENDENT_VALIDATION.json", "query": {"engine": "duckdb", "language": "sql", "sql": "SELECT * FROM read_json_auto('results/T422_INDEPENDENT_VALIDATION.json')", "description": "Independently verify hashes, disjoint banks, causal boundary, crossing arithmetic, field bootstraps, controls and source files.", "tables_used": ["results/T422_INDEPENDENT_VALIDATION.json"], "filters": ["119 registered checks"], "metric_definitions": ["All checks must pass for the saved analysis to be considered internally valid"]}},
    ]

    charts = [
        {"id": "chart_effects", "title": "Other-bank ridge exposure by split and direction", "subtitle": "Positive values favour a shared parent-scale ridge; whisker values are retained in tooltips and the gate table", "showDescription": True, "intent": "comparison", "question": "Does the child crossing in either bank expose H=1 in the other?", "rationale": "Grouped bars keep both bank directions and frozen splits visible without averaging them together.", "type": "bar", "dataset": "effects", "sourceId": "results", "encodings": {"x": {"field": "stage", "type": "nominal", "label": "Frozen split"}, "y": {"field": "ridge_exposure", "type": "quantitative", "label": "Ridge exposure"}, "color": {"field": "series", "type": "nominal", "label": "Bank direction"}, "tooltip": [{"field": "ci_lower", "type": "quantitative", "label": "95% CI lower"}, {"field": "ci_upper", "type": "quantitative", "label": "95% CI upper"}, {"field": "event_count", "type": "quantitative", "label": "Crossings"}, {"field": "field_count", "type": "quantitative", "label": "Fields"}]}, "xAxisTitle": "Frozen split", "yAxisTitle": "Field-balanced ridge exposure", "layout": "full"},
        {"id": "chart_centered", "title": "Validation events centred on each child U=R crossing", "subtitle": "Offset 0 is the interpolated child crossover; each line is field-balanced before plotting", "showDescription": True, "intent": "trend", "question": "How do child U/R and same/other-bank H move around the crossing?", "rationale": "Aligned traces expose the geometry behind the validation aggregate while preserving bank ownership.", "type": "line", "dataset": "centered_validation", "sourceId": "events", "encodings": {"x": {"field": "offset_reads", "type": "quantitative", "label": "Reads from child crossing"}, "y": {"field": "median_value", "type": "quantitative", "label": "ARA coordinate", "unit": "0–2"}, "color": {"field": "series", "type": "nominal", "label": "Direction and coordinate"}, "tooltip": [{"field": "offset_us", "type": "quantitative", "label": "Median time offset", "unit": "µs"}, {"field": "field_count", "type": "quantitative", "label": "Fields"}, {"field": "aligned_events", "type": "quantitative", "label": "Events"}]}, "xAxisTitle": "Reads from child U=R crossover", "yAxisTitle": "Field-balanced ARA coordinate (0–2)", "layout": "full"},
        {"id": "chart_controls", "title": "Registered effects and specificity controls", "subtitle": "Every value is in ridge-distance units; positive favours the declared other-bank relation", "showDescription": True, "intent": "comparison", "question": "Does the independent-bank result beat its timing, frequency and lineage rivals?", "rationale": "A common signed distance scale makes the failed specificity controls visible beside the descriptive exposure.", "type": "bar", "dataset": "controls", "sourceId": "results", "encodings": {"x": {"field": "stage_direction", "type": "nominal", "label": "Split and bank direction"}, "y": {"field": "advantage", "type": "quantitative", "label": "Advantage over ordinary/control distance"}, "color": {"field": "control", "type": "nominal", "label": "Test or control"}, "tooltip": [{"field": "event_count", "type": "quantitative", "label": "Crossings"}, {"field": "field_count", "type": "quantitative", "label": "Fields"}]}, "xAxisTitle": "Frozen split and bank direction", "yAxisTitle": "Signed ridge-distance advantage", "layout": "full"},
        {"id": "chart_rf", "title": "Ridge exposure by RF condition", "subtitle": "The frozen robustness gate requires a positive sign in both periods and both bank directions", "showDescription": True, "intent": "comparison", "question": "Is the descriptive exposure confined to one RF condition?", "rationale": "Grouped bars keep RF-on and RF-off contributions separate instead of allowing cancellation.", "type": "bar", "dataset": "rf", "sourceId": "results", "encodings": {"x": {"field": "stage_direction", "type": "nominal", "label": "Split and bank direction"}, "y": {"field": "ridge_exposure", "type": "quantitative", "label": "Ridge exposure"}, "color": {"field": "rf_period", "type": "nominal", "label": "RF period"}, "tooltip": [{"field": "event_count", "type": "quantitative", "label": "Crossings"}]}, "xAxisTitle": "Frozen split and bank direction", "yAxisTitle": "Field-balanced ridge exposure", "layout": "full"},
        {"id": "chart_events", "title": "Event-level ridge exposure across magnetic field", "subtitle": "Points show heterogeneity hidden by field-balanced medians; the untouched high-field split has no post-calibration crossings", "showDescription": True, "intent": "relationship", "question": "Is the effect broad across fields or carried by selected events?", "rationale": "The scatter keeps every evaluable crossing visible and identifies the missing high-field event population.", "type": "scatter", "dataset": "events", "sourceId": "events", "encodings": {"x": {"field": "field_G", "type": "quantitative", "label": "Applied field", "unit": "G"}, "y": {"field": "ridge_exposure", "type": "quantitative", "label": "Other-bank ridge exposure"}, "color": {"field": "stage", "type": "nominal", "label": "Frozen split"}, "tooltip": [{"field": "direction", "type": "nominal", "label": "Bank direction"}, {"field": "period", "type": "nominal", "label": "RF period"}, {"field": "crossing_time_us", "type": "quantitative", "label": "Crossing time", "unit": "µs"}, {"field": "child_coordinate", "type": "quantitative", "label": "Child U=R"}, {"field": "other_bank_H", "type": "quantitative", "label": "Other-bank H"}]}, "xAxisTitle": "Applied magnetic field (G)", "yAxisTitle": "Other-bank ridge exposure", "layout": "full"},
        {"id": "chart_validation_example", "title": "Validation bank-separated example", "subtitle": validation_label + "; forward U/R is the child cut and backward H is the independent candidate-parent read", "showDescription": True, "intent": "trend", "question": "What does one evaluable independent-bank sequence look like?", "rationale": "The worked trace exposes the direct chronological inputs rather than only the crossing aggregate.", "type": "line", "dataset": "validation_example", "sourceId": "timelines", "encodings": {"x": {"field": "time_us", "type": "quantitative", "label": "Corrected ensemble time", "unit": "µs"}, "y": {"field": "value", "type": "quantitative", "label": "ARA coordinate", "unit": "0–2"}, "color": {"field": "series", "type": "nominal", "label": "Bank and coordinate"}, "tooltip": [{"field": "field_G", "type": "quantitative", "label": "Applied field", "unit": "G"}, {"field": "run", "type": "nominal", "label": "Run"}, {"field": "period", "type": "nominal", "label": "RF period"}]}, "xAxisTitle": "Corrected ensemble time (µs)", "yAxisTitle": "ARA coordinate (0–2)", "layout": "full"},
        {"id": "chart_holdout_example", "title": "High-field holdout U/R histories", "subtitle": holdout_label + "; neither bank crosses U=R after the causal calibration boundary", "showDescription": True, "intent": "trend", "question": "Why is the high-field parent test unavailable?", "rationale": "The chronological traces show that absence of events is a coordinate-regime result, not a missing file or software error.", "type": "line", "dataset": "holdout_example", "sourceId": "timelines", "encodings": {"x": {"field": "time_us", "type": "quantitative", "label": "Corrected ensemble time", "unit": "µs"}, "y": {"field": "value", "type": "quantitative", "label": "ARA coordinate", "unit": "0–2"}, "color": {"field": "series", "type": "nominal", "label": "Bank and child coordinate"}, "tooltip": [{"field": "difference_U_minus_R", "type": "quantitative", "label": "U−R"}, {"field": "field_G", "type": "quantitative", "label": "Applied field", "unit": "G"}]}, "xAxisTitle": "Corrected ensemble time (µs)", "yAxisTitle": "ARA coordinate (0–2)", "layout": "full"},
    ]

    manifest = {
        "version": 1, "surface": "report", "title": "T422 — Independent Detector-Bank Parent Test",
        "description": "Frozen test of whether a child U/R crossing in one EMU detector bank exposes H=1 in the disjoint opposing bank.",
        "generatedAt": generated, "sources": sources,
        "cards": [
            {"id": "card_f_to_b", "dataset": "cards", "sourceId": "results", "description": "Validation F→B field-balanced ridge exposure.", "metrics": [{"label": "Validation F → B", "field": "validation_F_to_B", "format": "number", "signed": True}]},
            {"id": "card_b_to_f", "dataset": "cards", "sourceId": "results", "description": "Validation B→F field-balanced ridge exposure.", "metrics": [{"label": "Validation B → F", "field": "validation_B_to_F", "format": "number", "signed": True}]},
            {"id": "card_holdout", "dataset": "cards", "sourceId": "events", "description": "Post-calibration U=R crossings available in the high-field holdout.", "metrics": [{"label": "High-field crossings", "field": "holdout_crossings", "format": "number"}]},
            {"id": "card_audit", "dataset": "cards", "sourceId": "audit", "description": "Saved-artifact checks independently recomputed and passed.", "metrics": [{"label": "Audit checks passed", "field": "audit_passed", "format": "number"}, {"label": "of", "field": "audit_total", "format": "number"}]},
        ],
        "charts": charts,
        "tables": [
            {"id": "table_gates", "title": "Frozen gates by split", "subtitle": "Holdout distinction: UNAVAILABLE means no post-calibration child crossing existed to score", "showDescription": True, "dataset": "gates", "sourceId": "results", "defaultSort": {"field": "gate_order", "direction": "asc"}, "density": "spacious", "layout": "full", "columns": [{"field": "stage", "label": "Split", "type": "text"}, {"field": "gate_order", "label": "Gate", "type": "number"}, {"field": "gate", "label": "Criterion", "type": "text"}, {"field": "status", "label": "Status", "type": "text"}]},
            {"id": "table_quantiles", "title": "Bank-coordinate distributions", "subtitle": "Every reconstructed read at or after 2.25 µs; 0–2 coordinates retain their own bank identity", "showDescription": True, "dataset": "quantiles", "sourceId": "timelines", "defaultSort": {"field": "stage", "direction": "asc"}, "density": "dense", "layout": "full", "columns": [{"field": "stage", "label": "Split", "type": "text"}, {"field": "partition", "label": "Bank", "type": "text"}, {"field": "coordinate", "label": "Coordinate", "type": "text"}, {"field": "n_reads", "label": "Reads", "type": "number"}, {"field": "q05", "label": "5%", "type": "number"}, {"field": "q25", "label": "25%", "type": "number"}, {"field": "median", "label": "Median", "type": "number"}, {"field": "q75", "label": "75%", "type": "number"}, {"field": "q95", "label": "95%", "type": "number"}]},
            {"id": "table_rings", "title": "Axial-ring calibration eligibility", "subtitle": "Correct-frequency improvement had to beat the median wrong-frequency improvement in both paired rings", "showDescription": True, "dataset": "rings", "sourceId": "calibration", "defaultSort": {"field": "stage", "direction": "asc"}, "density": "dense", "layout": "full", "columns": [{"field": "stage", "label": "Split", "type": "text"}, {"field": "direction", "label": "Direction", "type": "text"}, {"field": "ring", "label": "Matched ring", "type": "text"}, {"field": "wrong_ring_control", "label": "Control ring", "type": "text"}, {"field": "eligible_sequences", "label": "Eligible", "type": "number"}, {"field": "attempted_sequences", "label": "Attempted", "type": "number"}, {"field": "eligibility_rate_pct", "label": "Eligible %", "type": "number"}]},
            {"id": "table_bridge", "title": "Relational Bridge Map", "subtitle": "No ARA coordinate is promoted to a physical identity without the complete chain", "showDescription": True, "dataset": "bridge", "sourceId": "protocol", "defaultSort": {"field": "order", "direction": "asc"}, "density": "spacious", "layout": "full", "columns": [{"field": "order", "label": "Step", "type": "number"}, {"field": "anchor", "label": "Anchor", "type": "text"}, {"field": "entry", "label": "Recorded relation", "type": "text"}]},
            {"id": "table_pivot", "title": "Pivot Log", "subtitle": "One pre-run scoring-boundary clarification; no identity, axis, medium or claim changed after execution began", "showDescription": True, "dataset": "pivot", "sourceId": "protocol", "defaultSort": {"field": "order", "direction": "asc"}, "density": "spacious", "layout": "full", "columns": [{"field": "order", "label": "Step", "type": "number"}, {"field": "from", "label": "From", "type": "text"}, {"field": "to", "label": "To", "type": "text"}, {"field": "reason", "label": "Reason", "type": "text"}, {"field": "data_forced", "label": "Trigger", "type": "text"}, {"field": "user_confirmed", "label": "Confirmation", "type": "text"}, {"field": "effect", "label": "Effect", "type": "text"}]},
        ],
        "blocks": [
            {"id": "title", "type": "markdown", "body": "# T422 — Independent Detector-Bank Parent Test"},
            {"id": "summary", "type": "markdown", "sourceId": "results", "body": "## Technical summary\n\n**The registered independent-parent reading is NOT SUPPORTED by this instrument.** Development exposures were small and uncertain: F→B `+0.043` (95% field-bootstrap CI `−0.037` to `+0.063`) and B→F `+0.058` (`−0.060` to `+0.217`). Validation strengthened descriptively—F→B `+0.082` (`+0.017` to `+0.283`) and B→F `+0.151` (`−0.040` to `+0.285`)—but correct-frequency and same-lineage specificity both failed. The untouched 1800–2484 G holdout contained zero post-calibration U=R crossings in either bank, so it could not replicate the event-conditioned relation.\n\n**The geometry result is narrower and still useful.** In validation, both independent bank directions placed median other-bank H very near the 1.0 ridge and beat circular timing shifts (`p=0.005` and `0.009`). But wrong-frequency histories were equally close, indicating a broad angular-coordinate property rather than a uniquely identified physical parent. Splitting the 96-detector identity also made child crossings sparse: only 42–54% of development/validation sequences and 0% of holdout sequences were eligible.\n\n**The independent audit passed 119/119 checks.** The detector banks are disjoint, all scored reads occur after the 2.25 µs calibration interval, every crossing and effect was recomputed, and the timing-null populations match the real-event populations."},
            {"id": "metrics", "type": "metric-strip", "cardIds": ["card_f_to_b", "card_b_to_f", "card_holdout", "card_audit"]},
            {"id": "effect_heading", "type": "markdown", "body": "## Validation exposes a ridge, but the bidirectional claim does not clear uncertainty\n\nPositive exposure means the other bank is closer to H=1 at the child crossing than during its ordinary history. Validation F→B clears zero, while B→F does not; development clears neither. This asymmetry is evidence about the bank-split cut, not permission to average both directions into a pass."},
            {"id": "effects", "type": "chart", "chartId": "chart_effects"},
            {"id": "centered_heading", "type": "markdown", "body": "## The validation shape is visible around the child crossover\n\nOffset zero is fixed by each child bank's interpolated U=R crossing. The opposing-bank H trace approaches the ridge in the validation aggregate, but the same-bank H trace shows that ridge-like angular structure is not exclusive to the independent view. Child U/R and parent H remain different coordinates and are not added into one TE-ARA budget."},
            {"id": "centered", "type": "chart", "chartId": "chart_centered"},
            {"id": "controls_heading", "type": "markdown", "body": "## Frequency and lineage controls block the parent identification\n\nThe validation timing signal is real relative to circular shifts, but the declared frequency and neighbouring-field lineage are not special. In development, wrong-frequency H was significantly closer to the ridge than correct-frequency H in both directions. In validation the differences centre near zero. Therefore T422 cannot identify the observed H ridge as this child's unique or frequency-specific physical parent."},
            {"id": "controls", "type": "chart", "chartId": "chart_controls"},
            {"id": "rf_heading", "type": "markdown", "body": "## RF separation supports the validation sign but not the complete test\n\nAll four validation RF/direction exposures are positive, so the descriptive validation shape is not carried solely by one RF condition. Development B→F reverses under RF-off, and the stronger specificity gates remain failed."},
            {"id": "rf", "type": "chart", "chartId": "chart_rf"},
            {"id": "spread_heading", "type": "markdown", "body": "## Event heterogeneity and holdout absence are both part of the geometry verdict\n\nDevelopment and validation include positive and negative event-level exposures. The high-field archive contributes no points because neither bank crosses U=R after the causal calibration boundary—not because files were missing. That makes high-field transfer unavailable and shows that the bank-level child relation occupies a different side of its U/R cut in that regime."},
            {"id": "events", "type": "chart", "chartId": "chart_events"},
            {"id": "example_heading", "type": "markdown", "body": "## A worked validation sequence keeps the observed identities separate\n\nThe forward bank supplies child U and R, while the backward bank supplies candidate-parent H. This is the exact frozen F→B direction. It is a detector-population relation; no line is an individual muon trajectory or neutrino waveform."},
            {"id": "validation_example", "type": "chart", "chartId": "chart_validation_example"},
            {"id": "holdout_heading", "type": "markdown", "body": "## The high-field child relation never changes sides after calibration\n\nIn the worked high-field sequence, U and R remain ordered rather than crossing. The registered event-conditioned parent question therefore has no event to condition on. Calling that a failed ridge value would be wrong; it is a failed event-availability gate."},
            {"id": "holdout_example", "type": "chart", "chartId": "chart_holdout_example"},
            {"id": "scope", "type": "markdown", "sourceId": "protocol", "body": "## Scope, definitions and frozen methodology\n\n- **Who:** the muoniated-acetone detector-population spin relation in 13 development, 13 interleaved validation and 20 high-field/temperature holdout runs; RF-on and RF-off remain separate.\n- **What:** a child U=R crossing reconstructed from one bank and simultaneous candidate-parent H from the disjoint opposing bank.\n- **When:** past 128-bin histories sampled every four bins; all scored reads are at or after the completed 2.25 µs phase-basis calibration.\n- **Where:** F→B and B→F bank cuts on separate 0–2 coordinates; H=1 is the candidate-parent ridge.\n- **Why:** distinguish a shared parent-scale observation from same-cut mathematical reuse.\n- **How:** field-first medians, 10,000 field bootstraps, 1,000 circular shifts, wrong-frequency, neighbouring-field, RF and calibrated-ring controls.\n\n**Established-science side:** EMU's opposing detector banks are separate measurements of a shared ensemble spin asymmetry. **ARA side:** one bank supplies the child handover cut and the other is tested as an independent parent-ridge cut. The crosswalk does not make those labels physically identical."},
            {"id": "gates", "type": "table", "tableId": "table_gates"},
            {"id": "distribution_heading", "type": "markdown", "body": "## The full coordinate distributions explain the sparse event set\n\nMedians alone conceal whether U and R can exchange order. These quantiles show all reconstructed reads in both banks and all frozen splits. They retain the high-field geometry even though no high-field event satisfies U=R."},
            {"id": "quantiles", "type": "table", "tableId": "table_quantiles"},
            {"id": "ring_heading", "type": "markdown", "body": "## Ring-level spatial specificity is unavailable\n\nThe 16-detector axial rings rarely beat their wrong-frequency calibration controls: only one development middle-ring sequence was eligible, with none in validation or holdout. The positive single-field ring value is not interpretable as replication and cannot rescue the bank-level result."},
            {"id": "rings", "type": "table", "tableId": "table_rings"},
            {"id": "bridge_heading", "type": "markdown", "body": "## Relational Bridge Map\n\nThe test reaches a bank-independent population geometry but stops before a unique physical parent. The missing bridge is named explicitly rather than filled with the nearest familiar mechanism."},
            {"id": "bridge", "type": "table", "tableId": "table_bridge"},
            {"id": "pivot_heading", "type": "markdown", "body": "## Pivot Log\n\nNo identity, rung, axis, detector medium or physical target changed after execution began. The only pre-run clarification excluded the phase-basis calibration interval so the confirmed no-future rule was actually true in code."},
            {"id": "pivot", "type": "table", "tableId": "table_pivot"},
            {"id": "limits", "type": "markdown", "sourceId": "audit", "body": "## Limitations, uncertainty and robustness\n\nThe 119-check independent audit validates the saved calculations and confirms that the timing shifts used the same event populations as the real comparison. The main limitation is construct validity: forward/backward banks are independent detector populations but still observe one source and share reconstruction logic, electronics and normalization. Sparse crossings reduce field replication, high field has no events, and ring calibration is inadequate. The appropriate fixed rating is **NOT SUPPORTED [pre-registered]** for the independent-parent claim, not NULL for all ARA geometry and not evidence against the earlier full-detector T421 relation."},
            {"id": "next", "type": "markdown", "body": "## Recommended next step\n\nDo not subdivide the same phase observation again. The clean next bridge is a genuinely different parent observable recorded in the same runs—most plausibly the detector-total population/decay envelope or another independently measured amplitude channel—tested at the full 96-detector U/R crossover. Freeze whether that parent should approach a ridge, pole or handover before scoring. If it succeeds while phase-only wrong-frequency controls fail, the parent identity gains physical specificity; if it behaves like H across every transform, H is better treated as a generic coordinate property."},
            {"id": "questions", "type": "markdown", "body": "## Further questions\n\n- Is T421 H the parent of the combined 96-detector identity rather than independently visible in either opposing projection?\n- Which raw amplitude or detector-total observable is causally available at the full-identity U/R crossing?\n- Why does the high-field bank relation remain on one side of U=R after 2.25 µs, and does that regime transition itself supply the missing parent cut?"},
        ],
    }

    snapshot = {
        "version": 1, "generatedAt": generated, "status": "ready",
        "datasets": {
            "cards": cards, "effects": effects,
            "centered_validation": [row for row in centered if row["stage"] == "Validation"],
            "controls": controls, "rf": rf, "events": events,
            "validation_example": validation_example, "holdout_example": holdout_example,
            "quantiles": quantiles, "gates": gates, "rings": rings,
            "bridge": bridge, "pivot": pivot,
        },
        "accessIssues": [],
    }
    artifact = {"surface": "report", "manifest": manifest, "snapshot": snapshot, "sources": sources}
    OUTPUT.write_text(json.dumps(artifact, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()

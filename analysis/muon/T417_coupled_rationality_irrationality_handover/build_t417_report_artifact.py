#!/usr/bin/env python3
"""Build the canonical portable technical report for T417."""

from __future__ import annotations

import csv
import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUTPUT = RESULTS / "T417_REPORT_ARTIFACT.json"
SQLITE_OUTPUT = RESULTS / "T417_REPORT_DATA.sqlite"
TITLE = "T417 — Coupled Rationality/Irrationality handover through muon ensemble time"
DOI = "https://data.isis.stfc.ac.uk/doi/STUDY/103197258"


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value, digits: int = 8):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if result != result:
        return None
    return round(result, digits)


def write_sqlite_table(connection: sqlite3.Connection, name: str, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"Cannot create empty table {name}")
    fields = list(rows[0])
    kinds = []
    for field in fields:
        values = [row.get(field) for row in rows if row.get(field) is not None]
        kinds.append("REAL" if values and all(isinstance(value, (int, float, bool)) for value in values) else "TEXT")
    connection.execute(f'CREATE TABLE "{name}" ({", ".join(f"\"{field}\" {kind}" for field, kind in zip(fields, kinds))})')
    placeholders = ", ".join("?" for _ in fields)
    connection.executemany(
        f'INSERT INTO "{name}" VALUES ({placeholders})',
        [[row.get(field) for field in fields] for row in rows],
    )


def table_source(table: str, description: str) -> dict:
    return {
        "id": f"t417-{table.replace('_', '-')}",
        "label": f"T417 {table.replace('_', ' ')}",
        "href": DOI,
        "query": {
            "engine": "SQLite",
            "sql": f'SELECT * FROM "{table}";',
            "description": description,
            "tables_used": [f"T417_REPORT_DATA.sqlite::{table}"],
        },
    }


def chart(chart_id: str, title: str, subtitle: str, chart_type: str, dataset: str, encodings: dict, x_title: str, y_title: str, references=None) -> dict:
    item = {
        "id": chart_id,
        "title": title,
        "subtitle": subtitle,
        "showDescription": True,
        "type": chart_type,
        "intent": "trend" if chart_type == "line" else ("relationship" if chart_type == "scatter" else "comparison"),
        "dataset": dataset,
        "sourceId": f"t417-{dataset.replace('_', '-')}",
        "encodings": encodings,
        "xAxisTitle": x_title,
        "yAxisTitle": y_title,
        "layout": "full",
    }
    if references:
        item["referenceLines"] = references
    return item


def main() -> None:
    result = json.loads((RESULTS / "T417_EVALUATION_RESULTS.json").read_text(encoding="utf-8"))
    posthoc = json.loads((RESULTS / "T417_POSTHOC_DIAGNOSTICS.json").read_text(encoding="utf-8"))
    audit = json.loads((RESULTS / "T417_VALIDATION_AUDIT.json").read_text(encoding="utf-8"))
    timeline_raw = read_csv(RESULTS / "T417_EVALUATION_TIMELINE.csv")
    example_raw = read_csv(RESULTS / "T417_EVALUATION_284G_TIMELINE.csv")
    summary_raw = read_csv(RESULTS / "T417_EVALUATION_SEQUENCE_SUMMARY.csv")
    boundary_raw = read_csv(RESULTS / "T417_POSTHOC_BOUNDARY_CLASSIFICATION.csv")
    shift_raw = read_csv(RESULTS / "T417_POSTHOC_SHIFT_COUNTS.csv")

    g = result["gates"]
    headline = [{
        "full_crossings": result["eligible_sequences"],
        "run_period_sequences": result["run_period_sequences"],
        "ordered_crossings": result["ordered_sequences"],
        "median_lead_us": number(result["median_lead_us"], 3),
        "lead_ci_low_us": number(result["lead_ci95_us"][0], 3),
        "lead_ci_high_us": number(result["lead_ci95_us"][1], 3),
        "full_or_censored": posthoc["full_or_boundary_censored_crossings"],
        "shift_null_max": posthoc["shift_null_eligible_count"]["maximum"],
        "posthoc_count_p": number(posthoc["shift_null_eligible_count"]["p_null_at_least_observed_full"], 4),
        "primary_support": "No",
        "audit_status": audit["status"],
    }]

    examples = {"RF on": [], "RF off": []}
    for row in example_raw:
        x_c = float(row["state_x_C"])
        examples[row["period"]].append({
            "time_us": number(row["time_us"], 4),
            "parent_ARA": number(row["parent_ARA"]),
            "state_xL": number(row["state_x_L"]),
            "state_xC": number(x_c),
            "mirror_2_minus_xC": number(2.0 - x_c),
            "closure_R": number(row["rational_closure_R"]),
            "unresolved_I": number(row["irrational_unresolved_I"]),
            "coupled_amount_A": number(row["coupled_amount_A"]),
            "coupled_balance_B": number(row["coupled_balance_B"]),
        })

    coupled_plane = []
    for row in timeline_raw:
        parent = float(row["parent_ARA"])
        stage = "early parent" if parent < 1.5 else ("middle parent" if parent < 1.7 else "late parent")
        coupled_plane.append({
            "field_G": number(row["field_G"], 1),
            "period": row["period"],
            "parent_stage": stage,
            "time_us": number(row["time_us"], 4),
            "parent_ARA": number(parent),
            "amount_A": number(row["coupled_amount_A"]),
            "balance_B": number(row["coupled_balance_B"]),
            "closure_R": number(row["rational_closure_R"]),
            "unresolved_I": number(row["irrational_unresolved_I"]),
        })

    event_summary = []
    for row in summary_raw:
        event_summary.append({
            "field_G": number(row["field_G"], 1),
            "period": row["period"],
            "handover_time_us": number(row["handover_time_us"], 4),
            "saturation_time_us": number(row["saturation_time_us"], 4),
            "lead_us": number(row["lead_us"], 4),
            "handover_parent_ARA": number(row["handover_parent_ARA"]),
            "same_distance_us": number(row["nearest_same_distance_us"]),
            "mirror_distance_us": number(row["nearest_mirror_distance_us"]),
            "eligible": "Yes" if int(row["eligible"]) else "No",
            "ordered": "Yes" if int(row["ordered"]) else "No",
        })

    class_order = [
        "fully observed",
        "left-censored: boundary crossing",
        "left-censored: already I-leading",
        "not recovered",
    ]
    boundary_counter = Counter(row["classification"] for row in boundary_raw)
    boundary_counts = [{"classification": name, "sequences": boundary_counter.get(name, 0)} for name in class_order]

    eligible_hist = Counter(int(row["eligible_count"]) for row in shift_raw)
    shift_distribution = [{"eligible_crossings": count, "null_draws": eligible_hist[count]} for count in sorted(eligible_hist)]

    state_alignment = [
        {"relation": "same-coordinate xL=xC", "comparison": "observed", "distance_us": number(g["G5_state_alignment"]["same_observed_distance_us"], 5)},
        {"relation": "same-coordinate xL=xC", "comparison": "shift-null median", "distance_us": number(g["G5_state_alignment"]["same_null_median_distance_us"], 5)},
        {"relation": "mirror xL+xC=2", "comparison": "observed", "distance_us": number(g["G5_state_alignment"]["mirror_observed_distance_us"], 5)},
        {"relation": "mirror xL+xC=2", "comparison": "shift-null median", "distance_us": number(g["G5_state_alignment"]["mirror_null_median_distance_us"], 5)},
    ]

    gate_labels = {
        "G1_availability": "At least 20/26 complete observable crossings",
        "G2_ordering": "At least 80% precede saturation",
        "G3_positive_lead": "Field-bootstrap lead interval above zero",
        "G4_coupling_specificity": "Observed parent-position dispersion beats shifted coupling",
        "G5_state_alignment": "State same/mirror meeting aligns beyond shifted xC",
    }
    gates = []
    for key, label in gate_labels.items():
        value = g[key]
        details = value.get("threshold", "")
        if key == "G3_positive_lead":
            details = f"median {value['value']:.3f} µs; 95% CI {value['ci95'][0]:.3f}–{value['ci95'][1]:.3f} µs"
        elif key == "G4_coupling_specificity":
            details = "Null dispersion undefined because no shifted draw produced 20 comparable crossings"
        elif key == "G5_state_alignment":
            details = f"same p={value['same_p']:.3f}; mirror p={value['mirror_p']:.3f}"
        gates.append({
            "gate": key.split("_", 1)[0],
            "test": label,
            "status": "PASS" if value["pass"] else "FAIL",
            "details": details,
        })

    audit_rows = [{"check": key.replace("_", " ").title(), "status": "PASS" if passed else "FAIL"} for key, passed in audit["checks"].items()]

    datasets = {
        "headline": headline,
        "example_on": examples["RF on"],
        "example_off": examples["RF off"],
        "coupled_plane": coupled_plane,
        "event_summary": event_summary,
        "boundary_counts": boundary_counts,
        "shift_distribution": shift_distribution,
        "state_alignment": state_alignment,
        "gates": gates,
        "audit": audit_rows,
    }

    if SQLITE_OUTPUT.exists():
        SQLITE_OUTPUT.unlink()
    with sqlite3.connect(SQLITE_OUTPUT) as connection:
        for name, data in datasets.items():
            write_sqlite_table(connection, name, data)
        connection.commit()

    sources = [
        {
            "id": "isis-rb1620447",
            "label": "ISIS RB1620447 public RF-µSR dataset",
            "href": DOI,
            "query": {
                "engine": "ISIS DataGateway",
                "url": DOI,
                "description": "Thirteen locked-evaluation 300 K fields, each scored separately for RF-on and RF-off.",
                "filters": [
                    "Magnetic field 68–500 G",
                    "T416 past-only windows from approximately 2.28–6.00 microseconds",
                    "Ensemble histograms; no event-linked individual muons or neutrinos",
                ],
                "tables_used": ["ISIS investigation RB1620447 / raw NeXus dataset"],
            },
        },
        {
            "id": "t417-analysis",
            "label": "T417 frozen coupled Rationality/Irrationality analysis",
            "href": DOI,
            "query": {
                "engine": "Python 3.12",
                "query": "python t417_coupled_rationality_irrationality_handover.py --stage development && python t417_coupled_rationality_irrationality_handover.py --stage evaluation",
                "language": "shell",
                "description": "Couples independently measured closure and unresolved-history participation, then tests ridge crossing before saturation.",
                "filters": [
                    "Protocol and code frozen after development",
                    "Post-T416 locked evaluation, not a new untouched confirmation",
                    "RF-on and RF-off never joined",
                ],
                "metric_definitions": [
                    "R = 2 times median closure coherence rho",
                    "I = T416 unresolved continuation xR",
                    "A = (R+I)/2 is total coupled participation",
                    "B = 1+(I-R)/(I+R) is relational balance; B=1 iff R=I",
                    "Handover candidate = sustained upward B=1 crossing",
                    "Saturation = three consecutive I>=1.99 windows",
                ],
                "tables_used": [
                    "T417_EVALUATION_TIMELINE.csv",
                    "T417_EVALUATION_SEQUENCE_SUMMARY.csv",
                    "T417_EVALUATION_RESULTS.json",
                    "T417_POSTHOC_DIAGNOSTICS.json",
                    "T417_VALIDATION_AUDIT.json",
                ],
            },
        },
    ]
    descriptions = {
        "headline": "Locked-evaluation headline and clearly labelled post-result boundary diagnostic.",
        "example_on": "284 G RF-on timeline with no RF boundary connection.",
        "example_off": "284 G RF-off timeline with no RF boundary connection.",
        "coupled_plane": "All locked-evaluation Rationality/Irrationality amount-and-balance locations.",
        "event_summary": "Frozen handover and saturation events by field and RF period.",
        "boundary_counts": "Post-result classification of full, boundary-censored and missing crossings.",
        "shift_distribution": "Post-result circular-shift eligible-crossing counts across 1,000 draws.",
        "state_alignment": "Observed and shifted-control distances from State-wave meetings to the coupled crossing.",
        "gates": "Five predeclared T417 gates, with the State alignment gate kept separate from the four primary gates.",
        "audit": "Independent structural and arithmetic audit of saved T417 outputs.",
    }
    sources.extend(table_source(name, description) for name, description in descriptions.items())

    cards = [
        {"id": "availability-card", "description": "Fully observable coupled crossings in the frozen test.", "dataset": "headline", "sourceId": "t417-headline", "metrics": [{"field": "full_crossings", "label": "Full crossings", "format": "number", "unit": "of 26"}]},
        {"id": "ordering-card", "description": "Every fully observed crossing preceded unresolved saturation.", "dataset": "headline", "sourceId": "t417-headline", "metrics": [{"field": "ordered_crossings", "label": "Ordered crossings", "format": "number", "unit": "of 14"}]},
        {"id": "lead-card", "description": "Median time from coupled ridge crossing to unresolved saturation.", "dataset": "headline", "sourceId": "t417-headline", "metrics": [{"field": "median_lead_us", "label": "Median lead", "format": "number", "unit": "µs"}]},
        {"id": "censored-card", "description": "Post-result full plus boundary-censored crossings; not a frozen-gate replacement.", "dataset": "headline", "sourceId": "t417-headline", "metrics": [{"field": "full_or_censored", "label": "Full or censored", "format": "number", "unit": "of 26"}]},
    ]

    ridge = [{"axis": "y", "value": 1, "label": "ARA ridge", "lineStyle": "dashed"}]
    on_handover, on_saturation = 2.328338988214831, 3.562999963760376
    off_handover, off_saturation = 2.333033887682735, 4.523000240325928
    charts = [
        chart("ri-on", "284 G RF-on: coupled closure and unresolved waves", "Past-only ensemble history; crossing is boundary-censored at the first available windows", "line", "example_on", {
            "x": {"field": "time_us", "type": "quantitative", "label": "Corrected ensemble time", "unit": "µs"},
            "y": {"fields": ["closure_R", "unresolved_I", "coupled_amount_A", "coupled_balance_B"], "type": "quantitative", "label": "ARA coordinate"},
            "tooltip": [{"field": "time_us", "type": "quantitative", "unit": "µs"}, {"field": "closure_R", "type": "quantitative"}, {"field": "unresolved_I", "type": "quantitative"}, {"field": "coupled_amount_A", "type": "quantitative"}, {"field": "coupled_balance_B", "type": "quantitative"}],
        }, "Corrected ensemble time (µs)", "ARA coordinate (0–2)", ridge + [{"axis": "x", "value": on_handover, "label": "R=I boundary crossing", "lineStyle": "dashed"}, {"axis": "x", "value": on_saturation, "label": "I saturation", "lineStyle": "dotted"}]),
        chart("ri-off", "284 G RF-off: coupled closure and unresolved waves", "Separate RF-off identity; no line is joined to RF-on", "line", "example_off", {
            "x": {"field": "time_us", "type": "quantitative", "label": "Corrected ensemble time", "unit": "µs"},
            "y": {"fields": ["closure_R", "unresolved_I", "coupled_amount_A", "coupled_balance_B"], "type": "quantitative", "label": "ARA coordinate"},
            "tooltip": [{"field": "time_us", "type": "quantitative", "unit": "µs"}, {"field": "closure_R", "type": "quantitative"}, {"field": "unresolved_I", "type": "quantitative"}, {"field": "coupled_amount_A", "type": "quantitative"}, {"field": "coupled_balance_B", "type": "quantitative"}],
        }, "Corrected ensemble time (µs)", "ARA coordinate (0–2)", ridge + [{"axis": "x", "value": off_handover, "label": "R=I boundary crossing", "lineStyle": "dashed"}, {"axis": "x", "value": off_saturation, "label": "I saturation", "lineStyle": "dotted"}]),
        chart("state-on", "284 G RF-on: same and mirror State-wave relations", "xL meets xC on the same relation and 2−xC on the mirror relation; neither is a unique handover marker", "line", "example_on", {
            "x": {"field": "time_us", "type": "quantitative", "label": "Corrected ensemble time", "unit": "µs"},
            "y": {"fields": ["state_xL", "state_xC", "mirror_2_minus_xC"], "type": "quantitative", "label": "State ARA coordinate"},
            "tooltip": [{"field": "time_us", "type": "quantitative", "unit": "µs"}, {"field": "state_xL", "type": "quantitative"}, {"field": "state_xC", "type": "quantitative"}, {"field": "mirror_2_minus_xC", "type": "quantitative"}],
        }, "Corrected ensemble time (µs)", "State ARA coordinate (0–2)", ridge + [{"axis": "x", "value": on_handover, "label": "coupled R/I crossing", "lineStyle": "dashed"}]),
        chart("state-off", "284 G RF-off: same and mirror State-wave relations", "RF-off is shown independently so the original false boundary jump cannot occur", "line", "example_off", {
            "x": {"field": "time_us", "type": "quantitative", "label": "Corrected ensemble time", "unit": "µs"},
            "y": {"fields": ["state_xL", "state_xC", "mirror_2_minus_xC"], "type": "quantitative", "label": "State ARA coordinate"},
            "tooltip": [{"field": "time_us", "type": "quantitative", "unit": "µs"}, {"field": "state_xL", "type": "quantitative"}, {"field": "state_xC", "type": "quantitative"}, {"field": "mirror_2_minus_xC", "type": "quantitative"}],
        }, "Corrected ensemble time (µs)", "State ARA coordinate (0–2)", ridge + [{"axis": "x", "value": off_handover, "label": "coupled R/I crossing", "lineStyle": "dashed"}]),
        chart("coupled-plane", "Coupled Rationality/Irrationality Di-ARA plane", "All 1,534 locked-evaluation windows; amount A and balance B are independent 0–2 coordinates", "scatter", "coupled_plane", {
            "x": {"field": "amount_A", "type": "quantitative", "label": "Total coupled participation A"},
            "y": {"field": "balance_B", "type": "quantitative", "label": "Rationality ↔ irrationality balance B"},
            "color": {"field": "parent_stage", "type": "nominal", "label": "Parent stage"},
            "tooltip": [{"field": "field_G", "type": "quantitative", "unit": "G"}, {"field": "period", "type": "nominal"}, {"field": "time_us", "type": "quantitative", "unit": "µs"}, {"field": "parent_ARA", "type": "quantitative"}, {"field": "amount_A", "type": "quantitative"}, {"field": "balance_B", "type": "quantitative"}],
        }, "Coupled amount A (0–2)", "Balance B: closure 0 ← 1 → unresolved 2", [{"axis": "y", "value": 1, "label": "R=I handover ridge", "lineStyle": "dashed"}]),
        chart("lead-field", "Fully observed crossing-to-saturation lead by field", "Fourteen eligible run/period sequences; missing points are unavailable or left-censored, not zero lead", "scatter", "event_summary", {
            "x": {"field": "field_G", "type": "quantitative", "label": "Magnetic field", "unit": "G"},
            "y": {"field": "lead_us", "type": "quantitative", "label": "Crossing-to-saturation lead", "unit": "µs"},
            "color": {"field": "period", "type": "nominal", "label": "RF period"},
            "tooltip": [{"field": "field_G", "type": "quantitative", "unit": "G"}, {"field": "period", "type": "nominal"}, {"field": "handover_time_us", "type": "quantitative", "unit": "µs"}, {"field": "saturation_time_us", "type": "quantitative", "unit": "µs"}, {"field": "lead_us", "type": "quantitative", "unit": "µs"}],
        }, "Magnetic field (G)", "Lead before unresolved saturation (µs)", [{"axis": "y", "value": 0, "label": "no lead", "lineStyle": "dashed"}]),
        chart("boundary-bars", "What happened to the twelve missing full crossings", "Post-result boundary diagnostic; these counts cannot replace the frozen availability gate", "bar", "boundary_counts", {
            "x": {"field": "classification", "type": "nominal", "label": "Crossing classification"},
            "y": {"field": "sequences", "type": "quantitative", "label": "Run/period sequences"},
            "tooltip": [{"field": "classification", "type": "nominal"}, {"field": "sequences", "type": "quantitative"}],
        }, "Crossing classification", "Run/period sequences", None),
        chart("shift-bars", "Shifted R/I paths rarely reproduce the observed crossing count", "1,000 post-result circular-shift controls; frozen dispersion gate remained unscorable", "bar", "shift_distribution", {
            "x": {"field": "eligible_crossings", "type": "quantitative", "label": "Eligible crossings in one shifted draw"},
            "y": {"field": "null_draws", "type": "quantitative", "label": "Shift-control draws"},
            "tooltip": [{"field": "eligible_crossings", "type": "quantitative"}, {"field": "null_draws", "type": "quantitative"}],
        }, "Eligible shifted crossings (of 26)", "Number of null draws", [{"axis": "x", "value": 14, "label": "14 fully observed", "lineStyle": "dashed"}]),
        chart("state-alignment-bars", "State-wave meetings are not uniquely aligned to the coupled handover", "Lower is closer; observed distances are comparable to circularly shifted xC", "bar", "state_alignment", {
            "x": {"field": "relation", "type": "nominal", "label": "State relation"},
            "y": {"field": "distance_us", "type": "quantitative", "label": "Median nearest distance", "unit": "µs"},
            "color": {"field": "comparison", "type": "nominal", "label": "Observed or shift control"},
            "tooltip": [{"field": "relation", "type": "nominal"}, {"field": "comparison", "type": "nominal"}, {"field": "distance_us", "type": "quantitative", "unit": "µs"}],
        }, "State-wave relation", "Median distance to R/I crossing (µs)", None),
    ]

    tables = [
        {"id": "gates-table", "title": "Frozen T417 gates", "subtitle": "The four primary gates define the coupled handover verdict; State alignment is separate", "showDescription": True, "dataset": "gates", "sourceId": "t417-gates", "density": "spacious", "layout": "full", "columns": [{"field": "gate", "label": "Gate", "type": "text"}, {"field": "test", "label": "Test", "type": "text"}, {"field": "status", "label": "Status", "type": "text"}, {"field": "details", "label": "Result", "type": "text"}]},
        {"id": "event-table", "title": "Run/period handover summary", "subtitle": "Exact frozen events; blank handover values are unavailable, not zero", "showDescription": True, "dataset": "event_summary", "sourceId": "t417-event-summary", "density": "dense", "layout": "full", "defaultSort": {"field": "field_G", "direction": "asc"}, "columns": [{"field": "field_G", "label": "Field", "type": "number", "unit": "G"}, {"field": "period", "label": "RF period", "type": "text"}, {"field": "handover_time_us", "label": "R=I time", "type": "number", "unit": "µs"}, {"field": "saturation_time_us", "label": "I saturation", "type": "number", "unit": "µs"}, {"field": "lead_us", "label": "Lead", "type": "number", "unit": "µs"}, {"field": "handover_parent_ARA", "label": "Parent ARA at crossing", "type": "number"}, {"field": "eligible", "label": "Eligible", "type": "text"}]},
        {"id": "audit-table", "title": "Independent T417 audit", "subtitle": "Hashes, source rows, formulas, coordinate ranges and frozen verdict bookkeeping", "showDescription": True, "dataset": "audit", "sourceId": "t417-audit", "density": "dense", "layout": "full", "columns": [{"field": "check", "label": "Check", "type": "text"}, {"field": "status", "label": "Status", "type": "text"}]},
    ]

    blocks = [
        {"id": "title", "type": "markdown", "body": f"# {TITLE}"},
        {"id": "summary", "type": "markdown", "sourceId": "t417-analysis", "body": "## Technical summary\n\n**The coupled cut recovered a repeatable ordering, but the complete frozen handover claim did not pass.** Fourteen of 26 locked run/period sequences contained the fully guarded `R=I` crossing and later unresolved saturation; every one of those 14 crossed first. Median lead was **1.15 µs** with a paired-field bootstrap interval of **0.86–1.65 µs**. Availability failed the predeclared 20/26 gate, and the dispersion control was unscorable because no shifted draw generated enough crossings. The red `xL=xC` and blue `xL+xC=2` State meetings were real intersections but were no closer to the coupled handover than shifted controls."},
        {"id": "metrics", "type": "metric-strip", "cardIds": [card["id"] for card in cards], "dataset": "headline"},
        {"id": "scope", "type": "markdown", "body": "## What was coupled\n\nThis test stayed on the **same T416 population spin identity, medium, temperature, tier and past-only time cut**. Closure participation was `R=2ρ`; unresolved continuation was `I=xR`. They were not forced to sum to two. `A=(R+I)/2` measured their combined participation, while `B=1+(I−R)/(I+R)` measured which wave led. The candidate handover was the sustained upward `B=1` crossing—equivalently `R=I`—before `I` reached its 2.0 estimator ceiling."},
        {"id": "example-text", "type": "markdown", "sourceId": "t417-example-on", "body": "## At 284 G the coupled crossing sits at the left edge of observable history\n\nRF-on and RF-off are now shown in separate panels, so the former false line joining their boundaries is gone. In both periods, closure starts just above unresolved participation and is overtaken at about **2.33 µs**, parent ARA about **1.305**. The history window only becomes available at 2.283 µs, so this is a boundary-censored crossing rather than a fully guarded frozen event. Unresolved saturation follows at 3.563 µs for RF-on and 4.523 µs for RF-off."},
        {"id": "ri-on-block", "type": "chart", "chartId": "ri-on", "layout": "full"},
        {"id": "ri-off-block", "type": "chart", "chartId": "ri-off", "layout": "full"},
        {"id": "state-text", "type": "markdown", "sourceId": "t417-state-alignment", "body": "## The red and blue State-wave relations are present, but not handover-specific\n\nYour red relation is exactly `xL=xC`. Your blue/diagonal relation is `xL=2−xC`, or `xL+xC=2`. The corrected 284 G panels expose both without joining RF identities. Across all fields, however, the nearest red meeting was 0.0413 µs from the coupled crossing versus 0.0422 µs under shifted xC (`p=0.470`); the blue relation was 0.0450 versus 0.0408 µs (`p=0.682`). They remain useful State-wave geometry, but this test does not support either as the unique R/I handover marker."},
        {"id": "state-on-block", "type": "chart", "chartId": "state-on", "layout": "full"},
        {"id": "state-off-block", "type": "chart", "chartId": "state-off", "layout": "full"},
        {"id": "plane-text", "type": "markdown", "sourceId": "t417-coupled-plane", "body": "## Coupling prevents the unresolved ceiling from flattening the whole relation\n\nAlthough `I` frequently maxes at 2, `B` continues to change because closure `R` keeps falling. The amount/balance plane therefore preserves a two-dimensional trajectory that the standalone unresolved coordinate lost. This supports the measurement design: the coupled Di-ARA contains more relational information than `I` alone. It does not by itself prove that the crossing is a physical particle handover."},
        {"id": "plane-block", "type": "chart", "chartId": "coupled-plane", "layout": "full"},
        {"id": "lead-text", "type": "markdown", "sourceId": "t417-event-summary", "body": "## Every fully observed crossing preceded saturation\n\nThe ordering result is unusually clean: **14 of 14** eligible sequences had positive lead. The field-bootstrap interval stayed entirely above zero. This is the strongest frozen result. Missing points in the field plot are sequences where the guarded crossing was not observable, not zero-lead failures."},
        {"id": "lead-block", "type": "chart", "chartId": "lead-field", "layout": "full"},
        {"id": "boundary-text", "type": "markdown", "sourceId": "t417-boundary-counts", "body": "## The availability failure is largely boundary censoring—but that was learned after scoring\n\nA labelled post-result diagnostic found 14 fully observed crossings, 3 crossings inside the opening guard, 7 sequences already unresolved-leading when the first complete history window appeared, and only 2 not recovered. That places **24 of 26** on an observed-or-left-censored route. Circularly shifted closure paths produced a median of 5 eligible crossings and never more than 9 in 1,000 draws (`p=0.001` versus the 14 fully observed count). This is strong follow-up evidence, but it cannot retroactively replace the frozen availability or dispersion gates."},
        {"id": "boundary-block", "type": "chart", "chartId": "boundary-bars", "layout": "full"},
        {"id": "shift-block", "type": "chart", "chartId": "shift-bars", "layout": "full"},
        {"id": "state-align-text", "type": "markdown", "sourceId": "t417-state-alignment", "body": "## Local State crossings are abundant rather than selective\n\nThe observed red and blue nearest-distance statistics sit inside their shifted-control distributions. In plain language, oscillating ridge-centred State waves cross these relations often enough that seeing one near the history handover is not unusual. The current data therefore distinguish the slower closure/unresolved transfer from the faster local State interactions."},
        {"id": "state-align-block", "type": "chart", "chartId": "state-alignment-bars", "layout": "full"},
        {"id": "gates-text", "type": "markdown", "body": "## Frozen verdict\n\nG2 and G3 passed; G1 and G4 failed. The four-gate coupled handover claim is therefore **not supported under the frozen protocol**. G5, the separate State-alignment question, also failed. The scientifically faithful reading is narrower: the coupled balance crossing has repeatable direction and positive lead wherever it is fully visible, and the current window begins too late to observe it in many high-field sequences."},
        {"id": "gates-block", "type": "table", "tableId": "gates-table", "layout": "full"},
        {"id": "method", "type": "markdown", "sourceId": "t417-analysis", "body": "## Methodology\n\nThe T416 128-bin past-only history windows were reused without changing the reconstructed identity. A full crossing required two prior samples on the closure-leading side and three samples on the unresolved-leading side. Saturation required three consecutive `I≥1.99` windows. Magnetic fields—not time bins—were bootstrapped. Controls circularly shifted `R` relative to `I`, and separately shifted `xC` relative to `xL`, within each run/period. Development fixed every threshold before the locked-evaluation script ran."},
        {"id": "limitations", "type": "markdown", "body": "## Limitations and robustness\n\nThis remains an ensemble RF-µSR trajectory, not an event-linked individual muon or neutrino observation. T417 reuses validation records already seen in T416, so it is a locked post-T416 evaluation rather than pristine confirmation. The history estimator cannot exist before its 2.048 µs window fills, producing left censoring that worsens with field. The post-result boundary classification and count-based shift comparison explain the failure pattern but are not frozen-gate evidence. All 17 independent hash, source, formula, range and verdict checks passed."},
        {"id": "events-text", "type": "markdown", "body": "## Exact sequence results\n\nThe table preserves each field and RF identity. Blank crossing values indicate unavailable guarded crossings; they must not be read as zero."},
        {"id": "events-block", "type": "table", "tableId": "event-table", "layout": "full"},
        {"id": "next", "type": "markdown", "body": "## Recommended next test\n\nFreeze a boundary-censor-aware version before opening a new field set. Start with a shorter causal closure window, then nest the existing 128-bin window above it so the child cut becomes available earlier without discarding the parent history. Predeclare three outcomes: fully observed crossing, left-censored unresolved-leading start, or no crossing. Test whether field predicts censoring time while `R=I` still predicts later saturation. That directly targets the weakness T417 exposed instead of loosening its failed gate."},
        {"id": "questions", "type": "markdown", "body": "## Further questions\n\n- Does a nested shorter child window recover the 10 censored crossings before the 128-bin parent appears?\n- Do the two unrecovered sequences represent real alternate paths or only persistence-threshold misses?\n- Is the State Di-ARA coupled to the history handover through a phase/lag relation rather than raw same-time intersection?"},
        {"id": "audit-text", "type": "markdown", "body": "## Independent audit\n\nAll 17 saved-output checks passed, including exact recomputation of `R`, `I`, `A`, `B`, coordinate bounds, hashes, row counts and the frozen fail verdict."},
        {"id": "audit-block", "type": "table", "tableId": "audit-table", "layout": "full"},
    ]

    generated = datetime.now(timezone.utc).isoformat()
    manifest = {
        "version": 1,
        "surface": "report",
        "title": TITLE,
        "description": "Frozen coupled Rationality/Irrationality Di-ARA test with corrected RF-separated 284 G views.",
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
        "snapshot": {"version": 1, "generatedAt": generated, "status": "ready", "datasets": datasets},
        "sources": sources,
    }
    OUTPUT.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()

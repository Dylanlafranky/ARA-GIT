#!/usr/bin/env python3
"""Build the canonical portable technical report for T416."""

from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUTPUT = RESULTS / "T416_REPORT_ARTIFACT.json"
SQLITE_OUTPUT = RESULTS / "T416_REPORT_DATA.sqlite"
TITLE = "T416 — Two Irrationality Di-ARAs through muon ensemble time"
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
    kinds = []
    for field in fields:
        values = [row.get(field) for row in rows if row.get(field) is not None]
        kinds.append("REAL" if values and all(isinstance(value, (int, float, bool)) for value in values) else "TEXT")
    columns = ", ".join(f'"{field}" {kind}' for field, kind in zip(fields, kinds))
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
            "tables_used": [f"T416_REPORT_DATA.sqlite::{table}"],
        },
    }


def main() -> None:
    result = json.loads((RESULTS / "T416_VALIDATION_RESULTS.json").read_text(encoding="utf-8"))
    diagnostic = json.loads((RESULTS / "T416_POSTHOC_DIAGNOSTICS.json").read_text(encoding="utf-8"))
    audit = json.loads((RESULTS / "T416_VALIDATION_AUDIT.json").read_text(encoding="utf-8"))
    timeline_raw = read_csv(RESULTS / "T416_VALIDATION_TIMELINE.csv")
    example_raw = read_csv(RESULTS / "T416_EXAMPLE_284G_TIMELINE.csv")
    profile_raw = read_csv(RESULTS / "T416_POSTHOC_PARENT_PROFILES.csv")
    sector_raw = read_csv(RESULTS / "T416_POSTHOC_SECTOR_OCCUPANCY.csv")
    controls_raw = read_csv(RESULTS / "T416_POSTHOC_FIELD_CONTROLS.csv")

    effects = result["paired_field_effects"]
    gates_raw = result["gates"]
    gate_pass_count = sum(bool(value) for key, value in gates_raw.items() if key.startswith("G"))
    headline = [{
        "validation_fields": result["run_count"],
        "ensemble_windows": result["timeline_rows"],
        "frozen_gates_passed": gate_pass_count,
        "frozen_gates_total": 7,
        "state_magnitude_median": number(effects["state_x_L"]["median"], 4),
        "history_ceiling_percent": number(100 * diagnostic["target_x_R_ceiling_share"], 1),
        "closure_order_effect": number(effects["target_minus_shuffle_closure_rho"]["median"], 4),
        "parent_adjusted_correlation": number(result["parent_adjusted_spearman_state_x_L_history_x_R"], 4),
        "complete_support": "No",
        "audit_status": audit["status"].title(),
    }]

    example = []
    for row in example_raw:
        example.append({
            "period": row["period"],
            "time_us": number(row["time_us"], 4),
            "parent_ARA": number(row["parent_ARA"]),
            "state_x_L": number(row["state_x_L"]),
            "state_x_C": number(row["state_x_C"]),
            "history_x_P": number(row["history_x_P"]),
            "history_x_R": number(row["history_x_R"]),
            "closure_rho": number(row["median_closure_rho"]),
            "observed_phase_ARA": number(row["observed_phase_ARA"]),
            "state_sector": row["state_sector"],
            "history_sector": row["history_sector"],
        })

    state_plane = []
    history_plane = []
    for row in timeline_raw:
        parent = float(row["parent_ARA"])
        stage = "early parent" if parent < 1.5 else ("middle parent" if parent < 1.7 else "late parent")
        state_plane.append({
            "period_stage": f'{row["period"]} · {stage}',
            "period": row["period"],
            "parent_stage": stage,
            "field_G": number(row["field_G"], 1),
            "time_us": number(row["time_us"], 4),
            "parent_ARA": number(parent),
            "x_L": number(row["state_x_L"]),
            "x_C": number(row["state_x_C"]),
            "sector": row["state_sector"],
        })
        history_plane.append({
            "period_stage": f'{row["period"]} · {stage}',
            "period": row["period"],
            "parent_stage": stage,
            "field_G": number(row["field_G"], 1),
            "time_us": number(row["time_us"], 4),
            "parent_ARA": number(parent),
            "x_P": number(row["history_x_P"]),
            "x_R": number(row["history_x_R"]),
            "closure_rho": number(row["median_closure_rho"]),
            "sector": row["history_sector"],
        })

    parent_profiles = [{
        "period": row["period"],
        "parent_ARA": number(row["parent_ARA_observed_median"]),
        "state_x_L": number(row["state_x_L_median"]),
        "state_x_C": number(row["state_x_C_median"]),
        "history_x_P": number(row["history_x_P_median"]),
        "history_x_R": number(row["history_x_R_median"]),
        "closure_rho": number(row["closure_rho_median"]),
        "x_R_unsaturated_percent": number(100 * float(row["x_R_below_1_99_share"]), 2),
        "windows": int(row["rows"]),
    } for row in profile_raw]

    sector_occupancy = [{
        "cut_period": f'{row["instrument"]} · {row["period"]}',
        "instrument": row["instrument"],
        "period": row["period"],
        "sector": row["sector"],
        "windows": int(row["windows"]),
        "share_percent": number(100 * float(row["share"]), 2),
    } for row in sector_raw]

    control_effects = []
    effect_labels = {
        "shuffle_minus_target_x_R": "Shuffle − target xR",
        "wrong_minus_target_x_R": "Wrong frequency − target xR",
        "target_minus_shuffle_closure_rho": "Target − shuffle closure ρ",
    }
    for row in controls_raw:
        for field, label in effect_labels.items():
            control_effects.append({
                "run": row["run"],
                "period": row["period"],
                "field_G": number(row["field_G"], 1),
                "comparison": label,
                "effect": number(row[field]),
            })

    gate_meanings = {
        "G1_observed_state_orientation": "State orientation xC lies on the forward side in both RF periods.",
        "G2_observed_contraction": "State magnitude xL is below the ridge with its field-bootstrap interval below 1.",
        "G3_chronology_determinacy": "Correct chronology has lower unresolved-history xR than shuffled time with CI above zero.",
        "G4_support_preservation": "Shuffling chronology preserves occupied support xP within 0.10.",
        "G5_closure_history": "Correct chronology preserves more lagged closure coherence than shuffled time.",
        "G6_frequency_specificity": "Correct spin frequency has lower unresolved-history xR than nearby wrong frequencies.",
        "G7_nonredundancy_diagnostic": "State xL and history xR remain nonredundant after parent adjustment.",
    }
    gates = [{
        "gate": key.split("_", 1)[0],
        "name": key.split("_", 1)[1].replace("_", " ").title(),
        "status": "PASS" if gates_raw[key] else "FAIL",
        "meaning": gate_meanings[key],
    } for key in gate_meanings]

    audit_rows = [{
        "check": key.replace("_", " ").title(),
        "status": "PASS" if value else "FAIL",
    } for key, value in audit["checks"].items()]

    datasets = {
        "headline": headline,
        "example": example,
        "state_plane": state_plane,
        "history_plane": history_plane,
        "parent_profiles": parent_profiles,
        "sector_occupancy": sector_occupancy,
        "control_effects": control_effects,
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
            "description": "Thirteen untouched 300 K validation fields, each analysed as RF-on and RF-off ensemble time series.",
            "filters": [
                "Magnetic field 68–500 G",
                "Corrected time 0.25–6.00 microseconds at native 0.016-microsecond spacing",
                "Same source identity and medium as T414/T415",
                "Individual muon arrivals and daughter particles are not linked in this archive",
            ],
            "tables_used": ["ISIS investigation RB1620447 / raw NeXus dataset"],
        },
    }
    analysis_source = {
        "id": "t416-analysis",
        "label": "T416 frozen dual-Irrationality-Di-ARA analysis",
        "href": DOI,
        "query": {
            "engine": "Python 3.12",
            "query": "python t416_dual_irrationality_time_tracking.py --stage development && python t416_dual_irrationality_time_tracking.py --stage validation",
            "description": "Two separately defined ARA instruments applied to the same reconstructed complex spin path through ensemble time.",
            "language": "shell",
            "filters": [
                "State Di-ARA uses one field-specific spin period",
                "History Di-ARA uses a past-only 128-bin window read every four bins",
                "Development branch frozen before validation",
                "Post-result parent profiles and occupancy do not alter frozen gates",
            ],
            "metric_definitions": [
                "State xL = reciprocal/log magnitude change mapped to 0–2",
                "State xC = signed orientation change mapped to 0–2",
                "History xP = multiresolution occupied-support slope mapped to 0–2",
                "History xR = local-neighbour predictability relative to a null mapped to 0–2",
                "Closure ρ = lagged coherence retained by the path history",
                "Parent ARA = 2(1-exp(-t/2.203 microseconds))",
            ],
            "tables_used": [
                "T416_VALIDATION_TIMELINE.csv",
                "T416_VALIDATION_RUN_PERIOD_SUMMARY.csv",
                "T416_VALIDATION_RESULTS.json",
                "T416_VALIDATION_AUDIT.json",
            ],
        },
    }
    sources = [raw_source, analysis_source]
    descriptions = {
        "headline": "Frozen validation and labelled post-result headline metrics.",
        "example": "Fully labelled 284 G RF-on and RF-off dual-cut timeline.",
        "state_plane": "All validation state-Di-ARA locations on the 0–2 plane.",
        "history_plane": "All validation history-Di-ARA locations and closure coherence.",
        "parent_profiles": "Both cuts summarized by parent ARA stage.",
        "sector_occupancy": "Quadrant occupancy by Di-ARA and RF period.",
        "control_effects": "Chronology and wrong-frequency comparisons by validation field.",
        "gates": "Seven prespecified validation gates.",
        "audit": "Independent structural and arithmetic audit.",
    }
    for table, description in descriptions.items():
        sources.append(table_source(f"t416-{table.replace('_', '-')}", f"T416 {table.replace('_', ' ')}", table, description))

    cards = [
        {"id": "gate-card", "description": "Frozen gates passed without reinterpretation.", "dataset": "headline", "sourceId": "t416-headline", "metrics": [{"field": "frozen_gates_passed", "label": "Gates passed", "format": "number", "unit": "of 7"}]},
        {"id": "state-card", "description": "Pooled field-level state-magnitude coordinate.", "dataset": "headline", "sourceId": "t416-headline", "metrics": [{"field": "state_magnitude_median", "label": "Median state xL", "format": "number"}]},
        {"id": "ceiling-card", "description": "History windows where xR reached its 2.0 ceiling.", "dataset": "headline", "sourceId": "t416-headline", "metrics": [{"field": "history_ceiling_percent", "label": "xR at ceiling", "format": "number", "unit": "%"}]},
        {"id": "nonredundancy-card", "description": "Parent-adjusted relation between state xL and history xR.", "dataset": "headline", "sourceId": "t416-headline", "metrics": [{"field": "parent_adjusted_correlation", "label": "Adjusted Spearman ρ", "format": "number"}]},
    ]

    charts = [
        {
            "id": "example-state-chart", "title": "284 G: parent and State Di-ARA through ensemble time", "subtitle": "Same 0–2 ARA scale; RF-on and RF-off shown separately", "showDescription": True,
            "type": "line", "intent": "trend", "dataset": "example", "sourceId": "t416-example",
            "encodings": {
                "x": {"field": "time_us", "type": "quantitative", "label": "Corrected time", "unit": "µs"},
                "y": {"fields": ["parent_ARA", "state_x_L", "state_x_C"], "type": "quantitative", "label": "ARA coordinate"},
                "facet": {"field": "period", "type": "nominal", "label": "RF period"},
                "tooltip": [{"field": "period", "type": "nominal"}, {"field": "time_us", "type": "quantitative", "unit": "µs"}, {"field": "parent_ARA", "type": "quantitative"}, {"field": "state_x_L", "type": "quantitative"}, {"field": "state_x_C", "type": "quantitative"}],
            },
            "xAxisTitle": "Corrected ensemble time (µs)", "yAxisTitle": "ARA coordinate (0–2)",
            "referenceLines": [{"axis": "y", "value": 1, "label": "ARA ridge", "lineStyle": "dashed"}], "layout": "full",
        },
        {
            "id": "example-history-chart", "title": "284 G: parent and History Di-ARA through ensemble time", "subtitle": "xP records occupied support; xR records unresolved local continuation", "showDescription": True,
            "type": "line", "intent": "trend", "dataset": "example", "sourceId": "t416-example",
            "encodings": {
                "x": {"field": "time_us", "type": "quantitative", "label": "Corrected time", "unit": "µs"},
                "y": {"fields": ["parent_ARA", "history_x_P", "history_x_R"], "type": "quantitative", "label": "ARA coordinate"},
                "facet": {"field": "period", "type": "nominal", "label": "RF period"},
                "tooltip": [{"field": "period", "type": "nominal"}, {"field": "time_us", "type": "quantitative", "unit": "µs"}, {"field": "parent_ARA", "type": "quantitative"}, {"field": "history_x_P", "type": "quantitative"}, {"field": "history_x_R", "type": "quantitative"}, {"field": "closure_rho", "type": "quantitative"}],
            },
            "xAxisTitle": "Corrected ensemble time (µs)", "yAxisTitle": "ARA coordinate (0–2)",
            "referenceLines": [{"axis": "y", "value": 1, "label": "ARA ridge", "lineStyle": "dashed"}], "layout": "full",
        },
        {
            "id": "state-plane-chart", "title": "State Di-ARA plane", "subtitle": "Magnitude contraction/expansion versus orientation; all 1,534 validation windows", "showDescription": True,
            "type": "scatter", "intent": "relationship", "dataset": "state_plane", "sourceId": "t416-state-plane",
            "encodings": {
                "x": {"field": "x_L", "type": "quantitative", "label": "State magnitude xL"},
                "y": {"field": "x_C", "type": "quantitative", "label": "State orientation xC"},
                "color": {"field": "period_stage", "type": "nominal", "label": "RF period and parent stage"},
                "tooltip": [{"field": "field_G", "type": "quantitative", "unit": "G"}, {"field": "time_us", "type": "quantitative", "unit": "µs"}, {"field": "parent_ARA", "type": "quantitative"}, {"field": "x_L", "type": "quantitative"}, {"field": "x_C", "type": "quantitative"}, {"field": "sector", "type": "nominal"}],
            },
            "xAxisTitle": "Magnitude contraction ← 1 → expansion (xL)", "yAxisTitle": "Reverse ← 1 → forward orientation (xC)",
            "referenceLines": [{"axis": "x", "value": 1, "label": "ridge", "lineStyle": "dashed"}, {"axis": "y", "value": 1, "label": "ridge", "lineStyle": "dashed"}], "layout": "full",
        },
        {
            "id": "history-plane-chart", "title": "History Di-ARA plane", "subtitle": "Occupied support versus unresolved local continuation; all validation windows", "showDescription": True,
            "type": "scatter", "intent": "relationship", "dataset": "history_plane", "sourceId": "t416-history-plane",
            "encodings": {
                "x": {"field": "x_P", "type": "quantitative", "label": "History support xP"},
                "y": {"field": "x_R", "type": "quantitative", "label": "History determinacy xR"},
                "color": {"field": "period_stage", "type": "nominal", "label": "RF period and parent stage"},
                "tooltip": [{"field": "field_G", "type": "quantitative", "unit": "G"}, {"field": "time_us", "type": "quantitative", "unit": "µs"}, {"field": "parent_ARA", "type": "quantitative"}, {"field": "x_P", "type": "quantitative"}, {"field": "x_R", "type": "quantitative"}, {"field": "closure_rho", "type": "quantitative"}, {"field": "sector", "type": "nominal"}],
            },
            "xAxisTitle": "Repeated support ← 1 → open support (xP)", "yAxisTitle": "Determined ← 1 → unresolved continuation (xR)",
            "referenceLines": [{"axis": "x", "value": 1, "label": "ridge", "lineStyle": "dashed"}, {"axis": "y", "value": 1, "label": "ridge", "lineStyle": "dashed"}], "layout": "full",
        },
        {
            "id": "parent-profile-chart", "title": "Both cuts as the parent advances", "subtitle": "Median child coordinates within parent-ARA bins", "showDescription": True,
            "type": "line", "intent": "trend", "dataset": "parent_profiles", "sourceId": "t416-parent-profiles",
            "encodings": {
                "x": {"field": "parent_ARA", "type": "quantitative", "label": "Parent ARA"},
                "y": {"fields": ["state_x_L", "state_x_C", "history_x_P", "history_x_R"], "type": "quantitative", "label": "Median child coordinate"},
                "facet": {"field": "period", "type": "nominal", "label": "RF period"},
                "tooltip": [{"field": "period", "type": "nominal"}, {"field": "parent_ARA", "type": "quantitative"}, {"field": "state_x_L", "type": "quantitative"}, {"field": "state_x_C", "type": "quantitative"}, {"field": "history_x_P", "type": "quantitative"}, {"field": "history_x_R", "type": "quantitative"}, {"field": "windows", "type": "quantitative"}],
            },
            "xAxisTitle": "Parent release ARA (0–2)", "yAxisTitle": "Median child ARA coordinate (0–2)",
            "referenceLines": [{"axis": "x", "value": 1, "label": "parent ridge", "lineStyle": "dashed"}, {"axis": "y", "value": 1, "label": "child ridge", "lineStyle": "dashed"}], "layout": "full",
        },
        {
            "id": "closure-profile-chart", "title": "Chronological closure fades as the parent approaches release", "subtitle": "Median lagged closure coherence within parent-ARA bins", "showDescription": True,
            "type": "line", "intent": "trend", "dataset": "parent_profiles", "sourceId": "t416-parent-profiles",
            "encodings": {
                "x": {"field": "parent_ARA", "type": "quantitative", "label": "Parent ARA"},
                "y": {"field": "closure_rho", "type": "quantitative", "label": "Median closure coherence"},
                "color": {"field": "period", "type": "nominal", "label": "RF period"},
                "tooltip": [{"field": "period", "type": "nominal"}, {"field": "parent_ARA", "type": "quantitative"}, {"field": "closure_rho", "type": "quantitative"}, {"field": "x_R_unsaturated_percent", "type": "quantitative", "unit": "%"}],
            },
            "xAxisTitle": "Parent release ARA (0–2)", "yAxisTitle": "Median lagged closure coherence ρ", "layout": "full",
        },
        {
            "id": "sector-chart", "title": "The two instruments occupy different Di-ARA sectors", "subtitle": "Percentage of validation windows by cut and RF period", "showDescription": True,
            "type": "bar", "intent": "composition", "dataset": "sector_occupancy", "sourceId": "t416-sector-occupancy",
            "encodings": {
                "x": {"field": "cut_period", "type": "nominal", "label": "Instrument and RF period"},
                "y": {"field": "share_percent", "type": "quantitative", "label": "Window share", "unit": "%"},
                "color": {"field": "sector", "type": "nominal", "label": "ARA sector"},
                "tooltip": [{"field": "instrument", "type": "nominal"}, {"field": "period", "type": "nominal"}, {"field": "sector", "type": "nominal"}, {"field": "windows", "type": "quantitative"}, {"field": "share_percent", "type": "quantitative", "unit": "%"}],
            },
            "xAxisTitle": "Di-ARA instrument and RF period", "yAxisTitle": "Validation windows (%)", "layout": "full",
        },
        {
            "id": "control-chart", "title": "Frozen chronology and frequency controls by field", "subtitle": "Positive values favor the intended target for each named comparison", "showDescription": True,
            "type": "scatter", "intent": "relationship", "dataset": "control_effects", "sourceId": "t416-control-effects",
            "encodings": {
                "x": {"field": "field_G", "type": "quantitative", "label": "Magnetic field", "unit": "G"},
                "y": {"field": "effect", "type": "quantitative", "label": "Control effect"},
                "color": {"field": "comparison", "type": "nominal", "label": "Comparison"},
                "shape": {"field": "period", "type": "nominal", "label": "RF period"},
                "tooltip": [{"field": "run", "type": "nominal"}, {"field": "period", "type": "nominal"}, {"field": "field_G", "type": "quantitative", "unit": "G"}, {"field": "comparison", "type": "nominal"}, {"field": "effect", "type": "quantitative"}],
            },
            "xAxisTitle": "Magnetic field (G)", "yAxisTitle": "Signed control effect", "referenceLines": [{"axis": "y", "value": 0, "label": "control parity", "lineStyle": "dashed"}], "layout": "full",
        },
    ]

    tables = [
        {"id": "gate-table", "title": "Frozen validation gates", "subtitle": "The combined claim requires every row to pass", "showDescription": True, "dataset": "gates", "sourceId": "t416-gates", "density": "spacious", "layout": "full", "columns": [{"field": "gate", "label": "Gate", "type": "text"}, {"field": "name", "label": "Name", "type": "text"}, {"field": "status", "label": "Status", "type": "text"}, {"field": "meaning", "label": "Frozen meaning", "type": "text"}]},
        {"id": "audit-table", "title": "Independent T416 audit", "subtitle": "Source, hashes, rows, coordinate bounds, medians and gate recomputation", "showDescription": True, "dataset": "audit", "sourceId": "t416-audit", "density": "dense", "layout": "full", "columns": [{"field": "check", "label": "Check", "type": "text"}, {"field": "status", "label": "Status", "type": "text"}]},
    ]

    blocks = [
        {"id": "title", "type": "markdown", "body": f"# {TITLE}"},
        {"id": "summary", "type": "markdown", "sourceId": "t416-analysis", "body": "## Technical summary\n\n**Yes: both Irrationality Di-ARA instruments can track the same reconstructed muon spin-mode population through time, and they retain different information. The complete frozen relation was not confirmed.** Four of seven gates passed. The state cut retained a small forward orientation but its magnitude sat near/slightly above the ridge rather than contracting. The history cut preserved chronological closure coherence, yet its determinacy coordinate saturated at 2.0 in 49.0% of windows and did not distinguish the calibrated spin frequency from nearby wrong frequencies. After parent adjustment the two cuts were essentially uncorrelated (Spearman ρ = −0.009), so one is not merely a rescaled copy of the other."},
        {"id": "metrics", "type": "metric-strip", "cardIds": [card["id"] for card in cards], "dataset": "headline"},
        {"id": "scope", "type": "markdown", "body": "## What is being tracked\n\nThe identity is the detector-resolved **ensemble spin mode** in one fixed 300 K material/source family—not a continuously observed individual muon. The parent coordinate is population release maturity. The State Di-ARA asks what the local complex path is doing now: changing radius and turning. The History Di-ARA asks how the path arrived there: whether it keeps opening new support, whether local continuation is resolved, and how much lagged closure remains. All four coordinates and the parent use the same labelled 0–2 ARA scale."},
        {"id": "example-state-text", "type": "markdown", "sourceId": "t416-example", "body": "## A concrete 284 G example\n\nThe first panel overlays the parent with the two State coordinates. It shows the local path moving around the ridge while the parent progresses steadily toward 2. The second panel overlays the parent with the two History coordinates. History support stays strongly open while determinacy becomes progressively unresolved."},
        {"id": "example-state", "type": "chart", "chartId": "example-state-chart", "layout": "full"},
        {"id": "example-history", "type": "chart", "chartId": "example-history-chart", "layout": "full"},
        {"id": "planes-text", "type": "markdown", "body": "## The cuts are geometrically different\n\nState locations spread across all four mixed sectors, close to the two ridges. History locations are concentrated on the open-support side and travel upward toward the unresolved-continuation pole. This is the strongest visual evidence that the two instruments are not duplicates. It does not identify them as a parent/child pair or prove a completed Phase-A/Phase-B handover."},
        {"id": "state-plane", "type": "chart", "chartId": "state-plane-chart", "layout": "full"},
        {"id": "history-plane", "type": "chart", "chartId": "history-plane-chart", "layout": "full"},
        {"id": "sector", "type": "chart", "chartId": "sector-chart", "layout": "full"},
        {"id": "parent-text", "type": "markdown", "sourceId": "t416-parent-profiles", "body": "## How both cuts change with the parent\n\nThe rolling history window becomes available only after the parent has already passed roughly 1.29 on this cut. From there, state magnitude remains near the child ridge, history support stays near 1.85, and history determinacy rises toward its 2.0 ceiling. At the same time, lagged closure coherence falls sharply. In ARA language: the recorded history remains broadly open, but its locally recoverable continuation thins as population release advances."},
        {"id": "parent-profile", "type": "chart", "chartId": "parent-profile-chart", "layout": "full"},
        {"id": "closure-profile", "type": "chart", "chartId": "closure-profile-chart", "layout": "full"},
        {"id": "controls-text", "type": "markdown", "sourceId": "t416-control-effects", "body": "## What survived the controls\n\nChronological order preserved more lagged closure coherence than shuffled time: median target-minus-shuffle ρ was 0.0601 with a 95% field-bootstrap interval of 0.0273 to 0.1667. That is a real history result. The xR determinacy comparison was weaker: its interval touched zero for both shuffled chronology and wrong frequency. Nearly half of all target windows had already saturated at xR = 2, leaving too little headroom for those controls."},
        {"id": "controls", "type": "chart", "chartId": "control-chart", "layout": "full"},
        {"id": "gates-text", "type": "markdown", "body": "## Frozen verdict\n\nG1, G4, G5 and G7 passed. G2, G3 and G6 failed. Therefore T416 supports using both cuts descriptively and supports an order-sensitive closure-history signal, but it does **not** support the stronger statement that this implementation recovered the complete dual-Irrationality-Di-ARA spin handover."},
        {"id": "gates", "type": "table", "tableId": "gate-table", "layout": "full"},
        {"id": "method", "type": "markdown", "sourceId": "t416-analysis", "body": "## Methodology\n\nDetector shares were fit to two harmonic vectors at the field-calibrated spin frequency, yielding a complex path `w(t)=M(t) exp(iθ(t))`. State xL and xC were computed over one spin period. History xP, xR and closure ρ were computed from past-only 128-bin windows at four-bin cadence. Thirteen development fields fixed every rule before thirteen interleaved validation fields were opened. Controls shuffled chronology, reversed it and used nearby wrong frequencies. The parent was kept visible but was not used to manufacture either child coordinate."},
        {"id": "limitations", "type": "markdown", "body": "## Limitations and robustness\n\nThis is population-level RF-µSR, not event-linked particle tracking. The complex path is reconstructed from detector-share residuals; absolute detector angles are unavailable. The 128-bin history estimator spends much of the record at its 2.0 ceiling, which makes xR a blunt discriminator. The test reuses the T414/T415 archive, although the development/validation split and frozen hashes were preserved. Post-result parent profiles and sector counts are explicitly diagnostic and do not modify the primary gates."},
        {"id": "next", "type": "markdown", "body": "## Recommended next test\n\nKeep the two cuts, but replace the saturated history-determinacy estimator before claiming a handover. The cleanest route is an untouched event-level or absolute-detector-angle archive with a count-noise-corrected complex path. Freeze a longer/adaptive past-only window that preserves xR headroom, require the true spin frequency to beat nearby wrong frequencies, and retain closure ρ as the order-sensitive companion. That test would ask whether state and history jointly predict a later population change beyond parent maturity—not merely describe the same record."},
        {"id": "questions", "type": "markdown", "body": "## Further questions\n\n- Does xR regain frequency specificity with absolute detector geometry or a nonsaturating local-predictability map?\n- Does the falling closure ρ anticipate a later population feature when the target interval is frozen in advance?\n- Are the State and History planes parallel views of one identity, or a child/parent relation? T416 establishes nonredundancy, not ownership."},
        {"id": "audit-text", "type": "markdown", "body": "## Independent audit\n\nAll 20 provenance, structure, range, median and frozen-gate checks passed."},
        {"id": "audit", "type": "table", "tableId": "audit-table", "layout": "full"},
    ]

    generated = datetime.now(timezone.utc).isoformat()
    manifest = {
        "version": 1,
        "surface": "report",
        "title": TITLE,
        "description": "Frozen dual-Irrationality-Di-ARA tracking of one resolved muon ensemble spin mode through time.",
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

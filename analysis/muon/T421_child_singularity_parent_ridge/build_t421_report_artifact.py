#!/usr/bin/env python3
"""Build the portable technical report artifact for T421."""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUTPUT = HERE / "artifact.json"
sys.path.insert(0, str(HERE))
import t421_child_singularity_parent_ridge as t421  # noqa: E402


def read_csv(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def read_json(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def finite(value) -> bool:
    try:
        return bool(np.isfinite(float(value)))
    except (TypeError, ValueError):
        return False


def zero_event_material(stage: str) -> tuple[list[dict], list[dict]]:
    timeline = read_csv(f"T421_{stage}_TIMELINE.csv")
    events, centered = t421.build_events(timeline, 0, -1)
    return events, centered


def centered_rows() -> list[dict]:
    output = []
    for stage in ("DEVELOPMENT", "VALIDATION", "HOLDOUT"):
        events, centered = zero_event_material(stage)
        for offset in sorted({int(row["offset_reads"]) for row in centered}):
            sample = [row for row in centered if int(row["offset_reads"]) == offset]
            for field, label in (("child_U", "Child openness U"), ("child_R", "Child closure R"), ("parent_H", "Parent H")):
                output.append({
                    "stage": stage.title(),
                    "series": f"{stage.title()} · {label}",
                    "coordinate": label,
                    "offset_reads": offset,
                    "offset_us": float(np.median([float(row["offset_us"]) for row in sample])),
                    "median_value": float(np.median([float(row[field]) for row in sample])),
                    "aligned_events": len({row["event_id"] for row in sample}),
                    "total_events": len(events),
                })
    return output


def example_rows() -> list[dict]:
    output = []
    choices = (
        ("VALIDATION", "EMU00070022", "RF on", "Validation · 284 G · RF on"),
        ("HOLDOUT", "EMU00070275", "RF on", "Holdout · 2160 G · RF on"),
    )
    fields = (("openness_U", "Child openness U"), ("closure_R", "Child closure R"), ("parent_H", "Parent H"))
    for stage, run, period, label in choices:
        rows = [row for row in read_csv(f"T421_{stage}_TIMELINE.csv") if row["run"] == run and row["period"] == period]
        for step, row in enumerate(rows):
            for field, coordinate in fields:
                output.append({
                    "example": label, "stage": stage.title(), "step": step,
                    "time_us": float(row["time_us"]), "coordinate": coordinate,
                    "series": f"{label} · {coordinate}",
                    "value": float(row[field]), "child_distance": float(row["child_distance"]),
                    "parent_ridge_distance": float(row["parent_ridge_distance"]),
                })
    return output


def effect_rows(results: dict[str, dict]) -> list[dict]:
    output = []
    for stage, result in results.items():
        for key, label in (("zero_lag_exposure", "Literal crossover (0 reads)"), ("frozen_lag_exposure", "Development-frozen offset (−6 reads)")):
            item = result["crossing"][key]
            if finite(item["median"]):
                output.append({
                    "stage": stage.title(), "relation": label,
                    "parent_ridge_exposure": float(item["median"]),
                    "ci_lower": float(item["ci95"][0]), "ci_upper": float(item["ci95"][1]),
                    "field_count": int(item["field_count"]),
                })
    return output


def lag_rows() -> list[dict]:
    output = []
    for stage in ("DEVELOPMENT", "VALIDATION", "HOLDOUT"):
        for row in read_csv(f"T421_{stage}_LAG_PROFILE.csv"):
            if finite(row["parent_ridge_distance"]):
                output.append({
                    "stage": stage.title(), "lag_reads": int(row["lag_reads"]),
                    "lag_us": float(row["lag_us_median"]),
                    "parent_ridge_distance": float(row["parent_ridge_distance"]),
                    "event_count": int(row["event_count"]), "field_count": int(row["field_count"]),
                })
    return output


def event_rows() -> list[dict]:
    output = []
    for stage in ("DEVELOPMENT", "VALIDATION", "HOLDOUT"):
        events, _ = zero_event_material(stage)
        for row in events:
            output.append({
                "stage": stage.title(), "field_G": float(row["field_G"]),
                "period": row["period"], "direction": row["direction"].replace("R_to_U", "R → U").replace("U_to_R", "U → R"),
                "child_coordinate": float(row["crossing_U"]), "parent_H": float(row["parent_H"]),
                "parent_ridge_distance": float(row["parent_ridge_distance"]),
                "ridge_exposure": float(row["ridge_exposure"]),
            })
    return output


def gate_rows(results: dict[str, dict]) -> list[dict]:
    labels = {
        "G1_availability": "Coordinate availability",
        "G2_literal_hierarchy": "Literal child singularity / parent ridge",
        "G3_frozen_offset_hierarchy": "Development-frozen −6-read offset",
        "G4_timing_specificity": "Frozen-offset timing specificity",
        "G5_frequency_specificity": "Frequency specificity",
        "G6_lineage_specificity": "Neighbour-lineage specificity",
        "G7_signed_reversal": "Signed opening/closing reversal",
        "G8_signed_controls": "Signed reversal controls",
    }
    output = []
    for stage, result in results.items():
        for key, item in result["gates"].items():
            available = item.get("available", True)
            if key in ("G3_frozen_offset_hierarchy", "G5_frequency_specificity", "G6_lineage_specificity", "G7_signed_reversal", "G8_signed_controls") and result["event_count"] == 0:
                available = False
            output.append({
                "stage": stage.title(), "gate": labels[key],
                "status": "PASS" if item["pass"] else ("UNAVAILABLE" if not available else "FAIL"),
                "pass_numeric": int(bool(item["pass"])),
                "literal_events": int(result["zero_lag_event_count"]),
                "frozen_offset_events": int(result["event_count"]),
            })
    return output


def main() -> None:
    generated = datetime.now(timezone.utc).isoformat()
    results = {stage: read_json(f"T421_{stage.upper()}_RESULTS.json") for stage in ("development", "validation", "holdout")}
    audit = read_json("T421_INDEPENDENT_VALIDATION.json")
    centered = centered_rows()
    examples = example_rows()
    effects = effect_rows(results)
    lags = lag_rows()
    events = event_rows()
    gates = gate_rows(results)
    cards = [{
        "development_effect": results["development"]["crossing"]["zero_lag_exposure"]["median"],
        "validation_effect": results["validation"]["crossing"]["zero_lag_exposure"]["median"],
        "holdout_effect": results["holdout"]["crossing"]["zero_lag_exposure"]["median"],
        "total_literal_events": sum(item["zero_lag_event_count"] for item in results.values()),
        "audit_pass": int(bool(audit["all_checks_pass"])),
    }]

    sources = [
        {"id": "protocol", "label": "T421 frozen protocol", "path": "T421_FROZEN_PROTOCOL.md", "query": {"engine": "filesystem", "language": "sql", "sql": "SELECT * FROM read_text('T421_FROZEN_PROTOCOL.md')", "description": "Read the frozen hierarchy, lags, controls and gates.", "tables_used": ["T421_FROZEN_PROTOCOL.md"], "filters": ["Frozen before scoring validation and holdout"], "metric_definitions": ["Child singularity: interpolated U=R crossover; parent ridge: H=1"]}},
        {"id": "timelines", "label": "T421 saved ARA histories", "path": "results/T421_HOLDOUT_TIMELINE.csv", "query": {"engine": "duckdb", "language": "sql", "sql": "SELECT * FROM read_csv_auto('results/T421_DEVELOPMENT_TIMELINE.csv') UNION ALL SELECT * FROM read_csv_auto('results/T421_VALIDATION_TIMELINE.csv') UNION ALL SELECT * FROM read_csv_auto('results/T421_HOLDOUT_TIMELINE.csv')", "description": "Combine saved child U/R and parent H/Q histories for all frozen splits.", "tables_used": ["results/T421_DEVELOPMENT_TIMELINE.csv", "results/T421_VALIDATION_TIMELINE.csv", "results/T421_HOLDOUT_TIMELINE.csv"], "filters": ["RF-on and RF-off kept as separate histories"], "metric_definitions": ["Ridge exposure = history median |H−1| minus |H at child crossover−1|"]}},
        {"id": "results", "label": "T421 frozen stage results", "path": "results/T421_HOLDOUT_RESULTS.json", "query": {"engine": "duckdb", "language": "sql", "sql": "SELECT 'development' stage,* FROM read_json_auto('results/T421_DEVELOPMENT_RESULTS.json') UNION ALL SELECT 'validation' stage,* FROM read_json_auto('results/T421_VALIDATION_RESULTS.json') UNION ALL SELECT 'holdout' stage,* FROM read_json_auto('results/T421_HOLDOUT_RESULTS.json')", "description": "Combine frozen effects, controls and gate outcomes.", "tables_used": ["results/T421_DEVELOPMENT_RESULTS.json", "results/T421_VALIDATION_RESULTS.json", "results/T421_HOLDOUT_RESULTS.json"], "filters": ["Field-balanced medians; 10,000 field bootstraps"], "metric_definitions": ["Positive ridge exposure means H is nearer 1 at child crossover than in its own history"]}},
        {"id": "audit", "label": "Independent T421 recomputation", "path": "results/T421_INDEPENDENT_VALIDATION.json", "query": {"engine": "duckdb", "language": "sql", "sql": "SELECT * FROM read_json_auto('results/T421_INDEPENDENT_VALIDATION.json')", "description": "Independently reconstruct all literal crossings and confidence intervals from saved timelines.", "tables_used": ["results/T421_INDEPENDENT_VALIDATION.json"], "filters": ["Development, validation and high-field holdout"], "metric_definitions": ["Every hash, count, median, interval and literal gate must match"]}},
    ]

    charts = [
        {"id": "chart_centered", "title": "Child U/R crossover and parent H ridge", "subtitle": "Offset 0 is the child singularity; medians are aligned separately within each frozen split", "showDescription": True, "intent": "trend", "question": "Does the parent H relation approach its ridge when the child U/R identity crosses?", "rationale": "Event alignment preserves tier identity and shows the simultaneous child and parent coordinates.", "type": "line", "dataset": "centered", "sourceId": "timelines", "encodings": {"x": {"field": "offset_reads", "type": "quantitative", "label": "Reads from child singularity"}, "y": {"field": "median_value", "type": "quantitative", "label": "Median ARA coordinate", "unit": "0–2"}, "color": {"field": "series", "type": "nominal", "label": "Split and coordinate"}, "tooltip": [{"field": "offset_us", "type": "quantitative", "label": "Median time offset", "unit": "µs"}, {"field": "aligned_events", "type": "quantitative", "label": "Events at offset"}, {"field": "total_events", "type": "quantitative", "label": "Total crossings"}]}, "xAxisTitle": "Reads from child U=R singularity", "yAxisTitle": "Median ARA coordinate (0–2)", "layout": "full"},
        {"id": "chart_effect", "title": "Parent-ridge exposure at the child singularity", "subtitle": "Positive means H is nearer its ridge at the child crossover than in the surrounding history", "showDescription": True, "intent": "comparison", "question": "Does the corrected cross-tier relation survive validation and holdout?", "rationale": "Grouped bars distinguish the literal same-slice relation from the development-selected precursor.", "type": "bar", "dataset": "effects", "sourceId": "results", "encodings": {"x": {"field": "stage", "type": "nominal", "label": "Frozen split"}, "y": {"field": "parent_ridge_exposure", "type": "quantitative", "label": "Parent-ridge exposure"}, "color": {"field": "relation", "type": "nominal", "label": "Cross-tier timing"}, "tooltip": [{"field": "ci_lower", "type": "quantitative", "label": "95% CI lower"}, {"field": "ci_upper", "type": "quantitative", "label": "95% CI upper"}, {"field": "field_count", "type": "quantitative", "label": "Fields"}]}, "xAxisTitle": "Frozen split", "yAxisTitle": "Median parent-ridge exposure", "layout": "full"},
        {"id": "chart_lags", "title": "Parent-ridge distance across candidate cross-tier offsets", "subtitle": "Lower is closer to H=1; negative high-field offsets disappear because the child crossover occurs at the recorded boundary", "showDescription": True, "intent": "trend", "question": "Is the development-selected −6-read offset transferable?", "rationale": "The full frozen lag profile exposes both the development minimum and the high-field availability boundary.", "type": "line", "dataset": "lags", "sourceId": "timelines", "encodings": {"x": {"field": "lag_reads", "type": "quantitative", "label": "Parent offset from child crossover", "unit": "reads"}, "y": {"field": "parent_ridge_distance", "type": "quantitative", "label": "Field-balanced |H−1|"}, "color": {"field": "stage", "type": "nominal", "label": "Frozen split"}, "tooltip": [{"field": "lag_us", "type": "quantitative", "label": "Median offset", "unit": "µs"}, {"field": "event_count", "type": "quantitative", "label": "Eligible events"}, {"field": "field_count", "type": "quantitative", "label": "Eligible fields"}]}, "xAxisTitle": "Parent offset from child crossover (reads)", "yAxisTitle": "Field-balanced parent-ridge distance |H−1|", "layout": "full"},
        {"id": "chart_examples", "title": "Two example child/parent histories", "subtitle": "Validation and high-field holdout use the same independent 0–2 coordinates", "showDescription": True, "intent": "trend", "question": "What does the corrected hierarchy look like in ordinary chronological traces?", "rationale": "Matched examples show the raw relational shape without collapsing child and parent into one budget.", "type": "line", "dataset": "examples", "sourceId": "timelines", "encodings": {"x": {"field": "time_us", "type": "quantitative", "label": "Corrected ensemble time", "unit": "µs"}, "y": {"field": "value", "type": "quantitative", "label": "ARA coordinate", "unit": "0–2"}, "color": {"field": "series", "type": "nominal", "label": "Example and coordinate"}, "tooltip": [{"field": "example", "type": "nominal", "label": "Example"}, {"field": "coordinate", "type": "nominal", "label": "Coordinate"}, {"field": "child_distance", "type": "quantitative", "label": "Child |U−R|"}, {"field": "parent_ridge_distance", "type": "quantitative", "label": "Parent |H−1|"}]}, "xAxisTitle": "Corrected ensemble time (µs)", "yAxisTitle": "ARA coordinate (0–2)", "layout": "full"},
        {"id": "chart_events", "title": "Literal crossover events across magnetic field", "subtitle": "Each point is an interpolated U=R child singularity; positive exposure means the parent is nearer H=1", "showDescription": True, "intent": "relationship", "question": "Is the relation broad across fields or carried by one regime?", "rationale": "An event scatter reveals heterogeneity hidden by the field-balanced median.", "type": "scatter", "dataset": "events", "sourceId": "timelines", "encodings": {"x": {"field": "field_G", "type": "quantitative", "label": "Applied field", "unit": "G"}, "y": {"field": "ridge_exposure", "type": "quantitative", "label": "Parent-ridge exposure"}, "color": {"field": "stage", "type": "nominal", "label": "Frozen split"}, "tooltip": [{"field": "child_coordinate", "type": "quantitative", "label": "Child U=R coordinate"}, {"field": "parent_H", "type": "quantitative", "label": "Parent H"}, {"field": "parent_ridge_distance", "type": "quantitative", "label": "Parent |H−1|"}, {"field": "direction", "type": "nominal", "label": "Child direction"}, {"field": "period", "type": "nominal", "label": "RF period"}]}, "xAxisTitle": "Applied magnetic field (G)", "yAxisTitle": "Parent-ridge exposure at child singularity", "layout": "full"},
    ]

    manifest = {
        "version": 1, "surface": "report", "title": "T421 — Child Singularity / Parent Ridge Test", "description": "Frozen cross-tier test of whether the U/R child crossover is registered at the H parent ridge.", "generatedAt": generated, "sources": sources,
        "cards": [
            {"id": "card_effects", "dataset": "cards", "sourceId": "results", "description": "Field-balanced parent-ridge exposure at the literal child crossover.", "metrics": [{"label": "Development", "field": "development_effect", "format": "number", "signed": True}, {"label": "Validation", "field": "validation_effect", "format": "number", "signed": True}, {"label": "High-field holdout", "field": "holdout_effect", "format": "number", "signed": True}]},
            {"id": "card_events", "dataset": "cards", "sourceId": "timelines", "description": "Literal U=R child singularities across all three frozen splits.", "metrics": [{"label": "Literal crossings", "field": "total_literal_events", "format": "number"}]},
            {"id": "card_audit", "dataset": "cards", "sourceId": "audit", "description": "Independent reconstruction of hashes, event counts, effects and confidence intervals.", "metrics": [{"label": "Independent audit", "field": "audit_pass", "format": "number"}]},
        ],
        "charts": charts,
        "tables": [{"id": "table_gates", "title": "Frozen hierarchy and specificity gates", "subtitle": "PASS, FAIL and UNAVAILABLE are kept distinct", "showDescription": True, "dataset": "gates", "sourceId": "results", "defaultSort": {"field": "stage", "direction": "asc"}, "density": "spacious", "layout": "full", "columns": [{"field": "stage", "label": "Split", "type": "text"}, {"field": "gate", "label": "Frozen gate", "type": "text"}, {"field": "status", "label": "Status", "type": "text"}, {"field": "literal_events", "label": "Literal events", "type": "number"}, {"field": "frozen_offset_events", "label": "−6-read events", "type": "number"}]}],
        "blocks": [
            {"id": "title", "type": "markdown", "body": "# T421 — Child Singularity / Parent Ridge Test"},
            {"id": "summary", "type": "markdown", "sourceId": "results", "body": "## Technical summary\n\n**The corrected ARA hierarchy is supported in the narrow positional sense.** The child identity is the independently measured openness/closure pair `U↔R`; its interpolated crossover `U=R` is the child singularity. `H` is the parent relation. At the literal child crossover, the parent was nearer `H=1` than in its surrounding history in development (+0.100, 95% field-bootstrap CI +0.030 to +0.334), validation (+0.061, +0.036 to +0.171), and the 1800–2484 G holdout (+0.142, +0.014 to +0.341).\n\n**The data do not yet identify H uniquely as this child's parent.** Wrong-frequency and neighbouring-field histories were not reliably farther from their ridges. The signed opening/closing branch was positive only in development and did not reproduce in validation.\n\n**The −6-read precursor is unresolved, not failed as a measured effect.** It reproduced in validation, but all 14 high-field child crossovers occur too close to the saved history boundary to inspect H six reads earlier. The literal same-slice hierarchy remains observable and passes there. This is a detector-population spin relation, not an individual muon or neutrino event."},
            {"id": "metrics", "type": "metric-strip", "cardIds": ["card_effects", "card_events", "card_audit"]},
            {"id": "shape_heading", "type": "markdown", "body": "## The child crossover is registered at the parent ridge\n\nOffset 0 is fixed by the child `U=R` crossing. The chart keeps the child coordinates and parent coordinate separate: their shared 0–2 scale does not make them one additive budget. The evidence is not merely that H can equal 1; it is that `|H−1|` becomes smaller at child singularities than it usually is within each run/period history."},
            {"id": "centered", "type": "chart", "chartId": "chart_centered"},
            {"id": "effect_heading", "type": "markdown", "body": "## The literal relation survives every frozen split\n\nAll three confidence intervals remain above zero after reducing events to field medians and bootstrapping fields. This supports a recurring cross-tier alignment. It does not prove that every child singularity must sit at every parent ridge, or that H is the only parent capable of registering it."},
            {"id": "effect", "type": "chart", "chartId": "chart_effect"},
            {"id": "lag_heading", "type": "markdown", "body": "## The development precursor cannot be scored in the high-field archive\n\nDevelopment selected H six reads before the child crossover and validation retained the relation. In holdout, the child crossings appear at the first available part of the reconstructed history, so a six-read look-back falls outside the recorded window. Moving the event or changing the lag would silently change the frozen test; T421 therefore records that branch as unavailable."},
            {"id": "lags", "type": "chart", "chartId": "chart_lags"},
            {"id": "examples_heading", "type": "markdown", "body": "## Chronological examples preserve the two-tier view\n\nThese traces show why H should not be added to U and R as though all three were children of one identity. U and R exchange within the child relation; H supplies a separately measured parent ridge coordinate."},
            {"id": "examples", "type": "chart", "chartId": "chart_examples"},
            {"id": "spread_heading", "type": "markdown", "body": "## The effect is broad enough to survive high-field transfer, but heterogeneous\n\nThe point cloud includes positive and negative event-level exposures. The claim rests on the predeclared field-balanced aggregate, not on every event following an undistorted landmark. That matches ARA's distinction between a parent ridge and locally displaced children."},
            {"id": "events", "type": "chart", "chartId": "chart_events"},
            {"id": "scope", "type": "markdown", "sourceId": "protocol", "body": "## Scope, definitions and frozen method\n\n- **Who:** 13 development runs, 13 interleaved validation runs and 20 temperature/high-field holdout runs; RF-on and RF-off are separate histories.\n- **What:** child singularity `U=R`; parent ridge distance `|H−1|`; optional signed parent branch `Q`.\n- **When:** each coordinate uses past-only phase histories. Literal timing is zero reads; development alone selected the secondary −6-read offset.\n- **Where:** detector-population spin histories of a muoniated-acetone radical.\n- **Why:** test the correction that H is the parent and the U/R crossover is its child's singularity.\n- **How:** field-balanced medians, 10,000 field bootstraps, time-shift, wrong-frequency and neighbouring-field controls; frozen validation and high-field holdout."},
            {"id": "gates", "type": "table", "tableId": "table_gates"},
            {"id": "limits", "type": "markdown", "sourceId": "audit", "body": "## Limitations and robustness\n\nThe independent validator reproduced every literal event count, median and confidence interval exactly and verified the analysis/protocol hashes. The strongest limitation is specificity: wrong-frequency and neighbouring-lineage controls do not distinguish H, so the result may reflect a broader parent-scale angular balance rather than this unique parent-child assignment. Signed branch direction also fails to replicate. The high-field offset branch is censored by the acquisition window rather than statistically contradicted."},
            {"id": "next", "type": "markdown", "body": "## Recommended next test\n\nFreeze a dataset whose reconstructed histories extend at least eight reads before every candidate child crossover. Then test the literal event and the −6-read precursor together while adding a parent-identity control that is physically independent—not merely a nearby frequency transformation of the same detector history. Preserve `U/R` as the child and `H/Q` as the parent throughout. Success would require: literal ridge exposure, transferable precursor timing, parent-lineage specificity, and signed branch reversal on untouched holdout."},
            {"id": "questions", "type": "markdown", "body": "## Further questions\n\n- Is H a unique parent of this U/R child, or a shared ridge coordinate of several nearby angular identities?\n- Does the parent branch change sign across child crossover when the full pre-event history is recorded?\n- Is the apparent −6-read lead stable in physical time, in child-cycle fraction, or in an octave-normalized coordinate?"},
        ],
    }

    artifact = {"surface": "report", "manifest": manifest, "snapshot": {"version": 1, "generatedAt": generated, "status": "ready", "datasets": {"cards": cards, "centered": centered, "effects": effects, "lags": lags, "examples": examples, "events": events, "gates": gates}, "accessIssues": []}, "sources": sources}
    OUTPUT.write_text(json.dumps(artifact, indent=2, allow_nan=False), encoding="utf-8")
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

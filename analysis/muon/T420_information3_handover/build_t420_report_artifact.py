#!/usr/bin/env python3
"""Build the portable technical report artifact for T420."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUTPUT = HERE / "artifact.json"


def read_csv(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def num(value) -> float:
    return float(value)


def example_rows() -> list[dict]:
    choices = (
        ("VALIDATION", "EMU00070022", "RF on", "Validation · 284 G · RF on"),
        ("HOLDOUT", "EMU00070275", "RF on", "Holdout · 2160 G · RF on"),
    )
    output = []
    labels = (("openness_U", "Openness U"), ("closure_R", "Closure R"), ("handover_H", "Lag-angle H"))
    for stage, run, period, label in choices:
        rows = [
            row for row in read_csv(f"T420_{stage}_TIMELINE.csv")
            if row["run"] == run and row["period"] == period
        ]
        for step, row in enumerate(rows):
            for field, coordinate in labels:
                output.append({
                    "example": label,
                    "stage": stage.title(),
                    "run": run,
                    "period": period,
                    "field_G": num(row["field_G"]),
                    "time_us": num(row["time_us"]),
                    "step": step,
                    "coordinate": coordinate,
                    "value": num(row[field]),
                    "parent_ARA": num(row["parent_ARA"]),
                })
    return output


def plane_rows() -> list[dict]:
    output = []
    for stage, run, period, label in (
        ("VALIDATION", "EMU00070022", "RF on", "Validation · 284 G"),
        ("HOLDOUT", "EMU00070275", "RF on", "Holdout · 2160 G"),
    ):
        rows = [
            row for row in read_csv(f"T420_{stage}_TIMELINE.csv")
            if row["run"] == run and row["period"] == period
        ]
        for step, row in enumerate(rows):
            output.append({
                "example": label,
                "stage": stage.title(),
                "step": step,
                "time_us": num(row["time_us"]),
                "U": num(row["openness_U"]),
                "R": num(row["closure_R"]),
                "H": num(row["handover_H"]),
                "parent_ARA": num(row["parent_ARA"]),
            })
    return output


def event_centered_rows() -> list[dict]:
    output = []
    for stage in ("VALIDATION", "HOLDOUT"):
        rows = read_csv(f"T420_{stage}_EVENT_CENTERED.csv")
        offsets = sorted({int(row["offset_reads"]) for row in rows})
        for offset in offsets:
            selected = [row for row in rows if int(row["offset_reads"]) == offset]
            median_us = float(np.median([num(row["offset_us"]) for row in selected]))
            for field, label in (("U", "Openness U"), ("R", "Closure R"), ("H", "Lag-angle H")):
                output.append({
                    "stage": stage.title(),
                    "series": f"{stage.title()} · {label}",
                    "coordinate": label,
                    "offset_reads": offset,
                    "offset_us": median_us,
                    "median_value": float(np.median([num(row[field]) for row in selected])),
                    "events": len({row["event_id"] for row in selected}),
                })
    return output


def closure_rows(validation: dict, holdout: dict) -> list[dict]:
    labels = (
        ("median_E2", "Two-coordinate |2−U−R|"),
        ("median_E3_correct", "Direct +H |2−U−R−H|"),
        ("median_E3_shifted", "History-median H control"),
        ("median_E3_wrong", "Wrong-frequency H control"),
        ("median_E3_affine", "Development-fitted affine H (diagnostic)"),
    )
    output = []
    for stage, result in (("Validation", validation), ("Holdout", holdout)):
        for key, label in labels:
            output.append({
                "stage": stage,
                "model": label,
                "absolute_closure_error": result["crossings"][key],
                "events": result["crossings"]["event_count"],
            })
    return output


def prediction_rows(validation: dict, holdout: dict) -> list[dict]:
    labels = (
        ("baseline_mse", "Own-history baseline"),
        ("transfer_mse", "Baseline + H,dH"),
        ("wrong_frequency_mse", "Wrong-frequency H"),
        ("reverse_mse", "Reverse-order H"),
    )
    output = []
    for stage, result in (("Validation", validation), ("Holdout", holdout)):
        for target, target_label in (("future_U", "Later openness U"), ("future_R", "Later closure R")):
            for key, label in labels:
                output.append({
                    "stage": stage,
                    "target": target_label,
                    "series": f"{stage} · {target_label}",
                    "model": label,
                    "mse": result["predictions"][target]["errors"][key],
                    "prediction_rows": result["predictions"][target]["prediction_rows"],
                })
    return output


def exposure_rows() -> list[dict]:
    output = []
    for stage in ("VALIDATION", "HOLDOUT"):
        for row in read_csv(f"T420_{stage}_CROSSING_EVENTS.csv"):
            output.append({
                "stage": stage.title(),
                "field_G": num(row["field_G"]),
                "direction": row["direction"].replace("R_to_U", "R → U").replace("U_to_R", "U → R"),
                "crossing_coordinate": num(row["crossing_U"]),
                "H_at_crossing": num(row["crossing_H"]),
                "H_exposure": num(row["H_exposure"]),
                "parent_ARA": num(row["parent_ARA"]),
                "period": row["period"],
            })
    return output


def gate_rows(validation: dict, holdout: dict) -> list[dict]:
    output = []
    for stage, result in (("Validation", validation), ("Holdout", holdout)):
        for gate, item in result["gates"].items():
            output.append({
                "stage": stage,
                "gate": gate.replace("_", " "),
                "result": "PASS" if item["pass"] else "FAIL",
                "pass_numeric": int(bool(item["pass"])),
                "crossing_events": result["crossings"]["event_count"],
                "primary_rows": result["primary_prediction_rows"],
            })
    return output


def main() -> None:
    generated = datetime.now(timezone.utc).isoformat()
    development = read_json("T420_DEVELOPMENT_RESULTS.json")
    validation = read_json("T420_VALIDATION_RESULTS.json")
    holdout = read_json("T420_HOLDOUT_RESULTS.json")
    audit = read_json("T420_INDEPENDENT_VALIDATION.json")

    examples = example_rows()
    event_centered = event_centered_rows()
    plane = plane_rows()
    closure = closure_rows(validation, holdout)
    predictions = prediction_rows(validation, holdout)
    exposures = exposure_rows()
    gates = gate_rows(validation, holdout)

    cards = [{
        "validation_H_exposure": validation["crossings"]["effects"]["H_cross_minus_history"]["median"],
        "holdout_H_exposure": holdout["crossings"]["effects"]["H_cross_minus_history"]["median"],
        "validation_H_cross": validation["crossings"]["median_H"],
        "holdout_H_cross": holdout["crossings"]["median_H"],
        "validation_crossing": validation["crossings"]["median_crossing_coordinate"],
        "holdout_crossing": holdout["crossings"]["median_crossing_coordinate"],
        "audit_pass": int(bool(audit["all_recomputations_pass"])),
    }]

    sources = [
        {
            "id": "protocol", "label": "T420 frozen protocol", "path": "T420_FROZEN_PROTOCOL.md",
            "query": {"engine": "filesystem", "language": "sql", "sql": "SELECT * FROM read_text('T420_FROZEN_PROTOCOL.md')", "description": "Read the predeclared T420 identity, coordinate, gates and controls.", "tables_used": ["T420_FROZEN_PROTOCOL.md"], "filters": ["Frozen before development, validation and holdout scoring"], "metric_definitions": ["H is the median normalized absolute lag angle; it is not 2-U-R"]},
        },
        {
            "id": "results", "label": "T420 frozen stage results", "path": "results/T420_HOLDOUT_RESULTS.json",
            "query": {"engine": "duckdb", "language": "sql", "sql": "SELECT 'validation' stage,* FROM read_json_auto('results/T420_VALIDATION_RESULTS.json') UNION ALL SELECT 'holdout' stage,* FROM read_json_auto('results/T420_HOLDOUT_RESULTS.json')", "description": "Combine frozen validation and high-field holdout summaries.", "tables_used": ["results/T420_VALIDATION_RESULTS.json", "results/T420_HOLDOUT_RESULTS.json"], "filters": ["Primary causal horizon: 32 reads, zero shared bins"], "metric_definitions": ["Crossing is exact sign change of U-R; closure error E3=|2-U-R-H|"]},
        },
        {
            "id": "timeline", "label": "T420 U/R/H histories", "path": "results/T420_HOLDOUT_TIMELINE.csv",
            "query": {"engine": "duckdb", "language": "sql", "sql": "SELECT * FROM read_csv_auto('results/T420_VALIDATION_TIMELINE.csv') UNION ALL SELECT * FROM read_csv_auto('results/T420_HOLDOUT_TIMELINE.csv')", "description": "Combine independent openness, closure and lag-angle histories.", "tables_used": ["results/T420_VALIDATION_TIMELINE.csv", "results/T420_HOLDOUT_TIMELINE.csv"], "filters": ["Examples: 284 G RF on and 2160 G RF on"], "metric_definitions": ["U and R are T419 coordinates; H is angular lag structure excluded from R magnitude"]},
        },
        {
            "id": "events", "label": "T420 exact crossing events", "path": "results/T420_HOLDOUT_CROSSING_EVENTS.csv",
            "query": {"engine": "duckdb", "language": "sql", "sql": "SELECT * FROM read_csv_auto('results/T420_VALIDATION_CROSSING_EVENTS.csv') UNION ALL SELECT * FROM read_csv_auto('results/T420_HOLDOUT_CROSSING_EVENTS.csv')", "description": "Combine linearly interpolated U=R crossings and H exposure values.", "tables_used": ["results/T420_VALIDATION_CROSSING_EVENTS.csv", "results/T420_HOLDOUT_CROSSING_EVENTS.csv"], "filters": ["Adjacent-read sign changes only"], "metric_definitions": ["H exposure = H at crossing - sequence median H"]},
        },
        {
            "id": "audit", "label": "Independent saved-artifact recomputation", "path": "results/T420_INDEPENDENT_VALIDATION.json",
            "query": {"engine": "duckdb", "language": "sql", "sql": "SELECT * FROM read_json_auto('results/T420_INDEPENDENT_VALIDATION.json')", "description": "Recompute hashes, causality, coordinate sums, event formulas and field-balanced prediction aggregates.", "tables_used": ["results/T420_INDEPENDENT_VALIDATION.json"], "filters": ["All three stages"], "metric_definitions": ["All recomputations must pass"]},
        },
    ]

    charts = [
        {
            "id": "chart_validation_history", "title": "Validation example — three independent histories", "subtitle": "284 G, RF on; U and R cross while lag-angle H approaches its own ridge", "showDescription": True, "intent": "trend", "question": "What changes around the opening/closure crossing?", "rationale": "Chronology shows whether H is merely present or specifically exposed near the handover.", "type": "line", "dataset": "example_validation", "sourceId": "timeline",
            "encodings": {"x": {"field": "time_us", "type": "quantitative", "label": "Corrected ensemble time", "unit": "µs"}, "y": {"field": "value", "type": "quantitative", "label": "ARA coordinate", "unit": "0–2"}, "color": {"field": "coordinate", "type": "nominal", "label": "Coordinate"}, "tooltip": [{"field": "time_us", "type": "quantitative", "label": "Time", "unit": "µs"}, {"field": "value", "type": "quantitative", "label": "Value"}, {"field": "parent_ARA", "type": "quantitative", "label": "Parent lifespan ARA"}]},
            "xAxisTitle": "Corrected ensemble time (µs)", "yAxisTitle": "ARA coordinate (0–2)", "layout": "full",
        },
        {
            "id": "chart_holdout_history", "title": "High-field holdout example — same three histories", "subtitle": "2160 G, RF on; identical construction under the harder 202 K regime", "showDescription": True, "intent": "trend", "question": "Does the visible three-history shape survive a major regime change?", "rationale": "The matched line chart preserves scale and construction across regimes.", "type": "line", "dataset": "example_holdout", "sourceId": "timeline",
            "encodings": {"x": {"field": "time_us", "type": "quantitative", "label": "Corrected ensemble time", "unit": "µs"}, "y": {"field": "value", "type": "quantitative", "label": "ARA coordinate", "unit": "0–2"}, "color": {"field": "coordinate", "type": "nominal", "label": "Coordinate"}, "tooltip": [{"field": "time_us", "type": "quantitative", "label": "Time", "unit": "µs"}, {"field": "value", "type": "quantitative", "label": "Value"}, {"field": "parent_ARA", "type": "quantitative", "label": "Parent lifespan ARA"}]},
            "xAxisTitle": "Corrected ensemble time (µs)", "yAxisTitle": "ARA coordinate (0–2)", "layout": "full",
        },
        {
            "id": "chart_event_centered", "title": "Median shape around exact U=R crossings", "subtitle": "Offset 0 is the interpolated crossing; H is elevated there in both regimes", "showDescription": True, "intent": "trend", "question": "Does a third angular history organize itself at the crossing?", "rationale": "Event alignment separates a recurring handover shape from absolute ensemble time.", "type": "line", "dataset": "event_centered", "sourceId": "events",
            "encodings": {"x": {"field": "offset_reads", "type": "quantitative", "label": "Reads from U=R crossing"}, "y": {"field": "median_value", "type": "quantitative", "label": "Median ARA coordinate", "unit": "0–2"}, "color": {"field": "series", "type": "nominal", "label": "Stage and coordinate"}, "tooltip": [{"field": "offset_us", "type": "quantitative", "label": "Median time offset", "unit": "µs"}, {"field": "events", "type": "quantitative", "label": "Aligned events"}]},
            "xAxisTitle": "Reads from exact U=R crossing", "yAxisTitle": "Median coordinate (0–2)", "layout": "full",
        },
        {
            "id": "chart_plane", "title": "The measured U/R plane with H retained", "subtitle": "H is shown in tooltips rather than collapsed into U or R", "showDescription": True, "intent": "relationship", "question": "Is H an independently varying relation rather than a forced remainder?", "rationale": "A U/R scatter preserves the original Di-ARA plane while allowing inspection of the third angular coordinate.", "type": "scatter", "dataset": "plane", "sourceId": "timeline",
            "encodings": {"x": {"field": "U", "type": "quantitative", "label": "Openness U", "unit": "0–2"}, "y": {"field": "R", "type": "quantitative", "label": "Closure R", "unit": "0–2"}, "color": {"field": "example", "type": "nominal", "label": "Example"}, "tooltip": [{"field": "H", "type": "quantitative", "label": "Lag-angle H"}, {"field": "time_us", "type": "quantitative", "label": "Time", "unit": "µs"}, {"field": "parent_ARA", "type": "quantitative", "label": "Parent lifespan ARA"}]},
            "xAxisTitle": "Openness U (0–2)", "yAxisTitle": "Closure R (0–2)", "layout": "full",
        },
        {
            "id": "chart_closure", "title": "Does H fill the missing TE-ARA share?", "subtitle": "Lower absolute closure error is better; direct +H is worse than U+R alone", "showDescription": True, "intent": "comparison", "question": "Can H be added as a positive third amount so U+R+H=2?", "rationale": "Grouped bars compare the predeclared additive reading with timing and frequency controls.", "type": "bar", "dataset": "closure", "sourceId": "results",
            "encodings": {"x": {"field": "model", "type": "nominal", "label": "Closure construction"}, "y": {"field": "absolute_closure_error", "type": "quantitative", "label": "Absolute error from 2"}, "color": {"field": "stage", "type": "nominal", "label": "Stage"}, "tooltip": [{"field": "events", "type": "quantitative", "label": "Crossing events"}, {"field": "absolute_closure_error", "type": "quantitative", "label": "Median error"}]},
            "xAxisTitle": "Closure construction", "yAxisTitle": "Median |2 − construction|", "layout": "full",
        },
        {
            "id": "chart_predictions", "title": "Causal prediction at the zero-overlap horizon", "subtitle": "32 reads ≈2.048 µs; lower field-balanced MSE is better", "showDescription": True, "intent": "comparison", "question": "Does current H add information about later openness or closure?", "rationale": "The bars compare correct H with the own-history baseline and wrong/reversed controls.", "type": "bar", "dataset": "predictions", "sourceId": "results",
            "encodings": {"x": {"field": "model", "type": "nominal", "label": "Model or control"}, "y": {"field": "mse", "type": "quantitative", "label": "Field-balanced MSE"}, "color": {"field": "series", "type": "nominal", "label": "Stage and target"}, "tooltip": [{"field": "prediction_rows", "type": "quantitative", "label": "Prediction rows"}, {"field": "mse", "type": "quantitative", "label": "MSE"}]},
            "xAxisTitle": "Model or control", "yAxisTitle": "Field-balanced MSE", "layout": "full",
        },
        {
            "id": "chart_exposure", "title": "H exposure at each crossing by magnetic field", "subtitle": "Positive means H is higher at U=R than in that run/period's typical history", "showDescription": True, "intent": "relationship", "question": "Is the crossing exposure broad or confined to one field?", "rationale": "The event scatter shows heterogeneity that a single median would hide.", "type": "scatter", "dataset": "exposures", "sourceId": "events",
            "encodings": {"x": {"field": "field_G", "type": "quantitative", "label": "Applied field", "unit": "G"}, "y": {"field": "H_exposure", "type": "quantitative", "label": "H at crossing − history median"}, "color": {"field": "stage", "type": "nominal", "label": "Stage"}, "tooltip": [{"field": "H_at_crossing", "type": "quantitative", "label": "H at crossing"}, {"field": "crossing_coordinate", "type": "quantitative", "label": "U=R coordinate"}, {"field": "direction", "type": "nominal", "label": "Crossing direction"}, {"field": "period", "type": "nominal", "label": "RF period"}]},
            "xAxisTitle": "Applied magnetic field (G)", "yAxisTitle": "H exposure at U=R", "layout": "full",
        },
    ]

    manifest = {
        "version": 1, "surface": "report", "title": "T420 — Information³ Handover Channel at the U/R Crossing", "description": "Frozen test of whether an independent lag-angle channel marks, closes or predicts the dynamic irrationality handover.", "generatedAt": generated, "sources": sources,
        "cards": [
            {"id": "card_exposure", "dataset": "cards", "sourceId": "events", "description": "Field-balanced elevation of H at exact U=R crossings.", "metrics": [{"label": "Validation H exposure", "field": "validation_H_exposure", "format": "number", "signed": True}, {"label": "Holdout H exposure", "field": "holdout_H_exposure", "format": "number", "signed": True}]},
            {"id": "card_ridges", "dataset": "cards", "sourceId": "events", "description": "The independent angular channel sits close to its own ARA ridge at the crossing.", "metrics": [{"label": "Validation H at crossing", "field": "validation_H_cross", "format": "number"}, {"label": "Holdout H at crossing", "field": "holdout_H_cross", "format": "number"}]},
            {"id": "card_crossings", "dataset": "cards", "sourceId": "events", "description": "U and R meet below their individual ridge in both regimes.", "metrics": [{"label": "Validation U=R", "field": "validation_crossing", "format": "number"}, {"label": "Holdout U=R", "field": "holdout_crossing", "format": "number"}]},
            {"id": "card_audit", "dataset": "cards", "sourceId": "audit", "description": "Independent hashes, event formulas, coordinate sums and field-balanced prediction aggregates recomputed.", "metrics": [{"label": "Independent audit", "field": "audit_pass", "format": "number"}]},
        ],
        "charts": charts,
        "tables": [{"id": "table_gates", "title": "Frozen validation and holdout gates", "subtitle": "The narrow crossing marker passes; additive closure and prediction claims fail", "showDescription": True, "dataset": "gates", "sourceId": "results", "defaultSort": {"field": "stage", "direction": "asc"}, "density": "spacious", "layout": "full", "columns": [{"field": "stage", "label": "Stage", "type": "text"}, {"field": "gate", "label": "Frozen gate", "type": "text"}, {"field": "result", "label": "Result", "type": "text"}, {"field": "crossing_events", "label": "Crossings", "type": "number"}, {"field": "primary_rows", "label": "Causal rows", "type": "number"}]}],
        "blocks": [
            {"id": "title", "type": "markdown", "body": "# T420 — Information³ Handover Channel at the U/R Crossing"},
            {"id": "summary", "type": "markdown", "sourceId": "results", "body": "## Technical summary\n\n**An independently defined third coordinate is exposed at the crossing, but it is not the missing positive TE-ARA amount.** The lag-angle channel `H` was constructed from the angular component of the same complex lag relation whose magnitude supplies closure `R`; it was never calculated as `2−U−R`. At exact `U=R` events, `H` rose above its own history by +0.088 in validation and +0.094 in the high-field holdout. Its median crossing value was 0.998 and 1.006 respectively—almost exactly its own ARA ridge.\n\n**The stronger Information³ closure claim failed cleanly.** Directly adding `H` worsened `|2−U−R|` in development, validation and holdout, and the correct timing did not beat shifted or wrong-frequency controls. `H` also failed to improve prediction of later openness at the fully separated 2.048 µs horizon.\n\n**ARA reading:** the observations are consistent with an angular/orientational mode becoming exposed while openness and closure exchange dominance. They do not yet establish a separate identity, and they do not support treating H as an extra additive share of the same parent budget. This remains a detector-population spin relation, not an individual muon or neutrino handover."},
            {"id": "metrics", "type": "metric-strip", "cardIds": ["card_exposure", "card_ridges", "card_crossings", "card_audit"]},
            {"id": "histories_heading", "type": "markdown", "body": "## What the three histories actually do\n\n`U` is openness/traversal loss, `R` is connection-like lag coherence magnitude, and `H` is the normalized absolute lag angle. All use 0–2 coordinates but remain independent measurements."},
            {"id": "validation_history", "type": "chart", "chartId": "chart_validation_history"},
            {"id": "holdout_history", "type": "chart", "chartId": "chart_holdout_history"},
            {"id": "event_heading", "type": "markdown", "body": "## The recurring crossing geometry\n\nAligning all sign-change crossings makes the narrow result visible: U and R meet around 0.83–0.85, while H is elevated and sits near 1.0. Because the H=1 location can also be the balanced angular value of a broad phase distribution, the important evidence is its elevation relative to each history—not its closeness to 1 by itself."},
            {"id": "event_centered", "type": "chart", "chartId": "chart_event_centered"},
            {"id": "plane", "type": "chart", "chartId": "chart_plane"},
            {"id": "closure_heading", "type": "markdown", "body": "## What this does not mean\n\nIf H were literally the missing third amount in the same TE-ARA budget, `U+R+H` should land closer to 2 at the crossing and the correct H should outperform controls. It does neither. A development-fitted affine transform can force small errors, but that is a diagnostic conversion, not independent confirmation."},
            {"id": "closure", "type": "chart", "chartId": "chart_closure"},
            {"id": "prediction_heading", "type": "markdown", "body": "## Causal consequence at the parent-population scale\n\nThe primary prediction separates current and future 128-bin histories by 32 reads, leaving zero shared native bins. H does not reliably improve later U or R over the target's own history, and the controls are not consistently worse."},
            {"id": "predictions", "type": "chart", "chartId": "chart_predictions"},
            {"id": "exposure", "type": "chart", "chartId": "chart_exposure"},
            {"id": "method", "type": "markdown", "sourceId": "protocol", "body": "## Frozen method and relational boundary\n\n- **Who:** 13 development, 13 validation and 20 high-field holdout runs; RF-on/off remain separate.\n- **What:** an independent lag-angle coordinate H, exact U=R crossings, additive closure controls, and future-U/R models.\n- **When:** histories are past-only; causal prediction uses 32 reads = 128 native bins ≈2.048 µs with zero raw-bin overlap.\n- **Where:** the detector-population spin relation of a muoniated-acetone radical.\n- **Why:** test whether the visible opening at T419's crossing is a third Information³ relation, a missing TE-ARA share, and/or a leading channel.\n- **How:** development-only fitting; frozen validation and temperature/high-field holdout; shifted, wrong-frequency and reversed-order controls."},
            {"id": "gates", "type": "table", "tableId": "table_gates"},
            {"id": "audit", "type": "markdown", "sourceId": "audit", "body": "## Independent audit\n\nAll saved-artifact recomputations passed: protocol and analysis hashes, zero-overlap causal windows, non-complementarity, event interpolation and formulas, and field-balanced prediction errors. The negative result is substantive, not a bookkeeping failure."},
            {"id": "next", "type": "markdown", "body": "## Best next cut\n\nTreat H as the **ridge coordinate of a separate orthogonal identity**, not as a positive remainder. Freeze a directional-state test asking whether the *signed* lag angle changes branch as U−R changes sign. The current H takes an absolute value, so it can reveal angular spread while erasing the direction needed to distinguish opening from closing. The next test should retain signed circular orientation, compare R→U with U→R crossings separately, and require the branch sign to reverse on holdout. That directly tests your hypothesis that this is an opening/movement transition rather than another connection share."},
        ],
    }

    artifact = {"surface": "report", "manifest": manifest, "snapshot": {"version": 1, "generatedAt": generated, "status": "ready", "datasets": {"cards": cards, "example_validation": [row for row in examples if row["stage"] == "Validation"], "example_holdout": [row for row in examples if row["stage"] == "Holdout"], "event_centered": event_centered, "plane": plane, "closure": closure, "predictions": predictions, "exposures": exposures, "gates": gates}, "accessIssues": []}, "sources": sources}
    OUTPUT.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

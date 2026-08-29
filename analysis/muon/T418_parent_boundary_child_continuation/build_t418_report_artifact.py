#!/usr/bin/env python3
"""Build the canonical portable technical report artifact for T418."""

from __future__ import annotations

import csv
import json
import math
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUTPUT = RESULTS / "T418_REPORT_ARTIFACT.json"
SQLITE_OUTPUT = RESULTS / "T418_REPORT_DATA.sqlite"
TITLE = "T418 — Parent-boundary child continuation"
DOI = "https://data.isis.stfc.ac.uk/doi/STUDY/103197258"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def num(value, digits: int = 8):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(result):
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
    cols = ", ".join(f'"{field}" {kind}' for field, kind in zip(fields, kinds))
    connection.execute(f'CREATE TABLE "{name}" ({cols})')
    placeholders = ", ".join("?" for _ in fields)
    connection.executemany(
        f'INSERT INTO "{name}" VALUES ({placeholders})',
        [[row.get(field) for field in fields] for row in rows],
    )


def table_source(table: str, description: str) -> dict:
    return {
        "id": f"t418-{table.replace('_', '-')}",
        "label": f"T418 {table.replace('_', ' ')}",
        "href": DOI,
        "query": {
            "engine": "SQLite",
            "sql": f'SELECT * FROM "{table}";',
            "description": description,
            "tables_used": [f"T418_REPORT_DATA.sqlite::{table}"],
        },
    }


def chart(chart_id: str, title: str, subtitle: str, chart_type: str, dataset: str, encodings: dict, x_title: str, y_title: str, references=None) -> dict:
    result = {
        "id": chart_id,
        "title": title,
        "subtitle": subtitle,
        "showDescription": True,
        "type": chart_type,
        "intent": "trend" if chart_type == "line" else ("relationship" if chart_type == "scatter" else "comparison"),
        "dataset": dataset,
        "sourceId": f"t418-{dataset.replace('_', '-')}",
        "encodings": encodings,
        "xAxisTitle": x_title,
        "yAxisTitle": y_title,
        "layout": "full",
    }
    if references:
        result["referenceLines"] = references
    return result


def histogram(values: list[float], lo: float, hi: float, bins: int, split: str) -> list[dict]:
    width = (hi - lo) / bins
    counts = Counter()
    for value in values:
        index = min(bins - 1, max(0, int((value - lo) / width)))
        counts[index] += 1
    return [
        {
            "split": split,
            "bin_mid": round(lo + (index + 0.5) * width, 4),
            "count": counts[index],
        }
        for index in range(bins)
    ]


def stage_label(parent: float) -> str:
    if parent < 1.5:
        return "early parent"
    if parent < 1.7:
        return "middle parent"
    return "late parent"


def load_stage(stage: str) -> dict:
    return {
        "result": json.loads((RESULTS / f"T418_{stage.upper()}_RESULTS.json").read_text(encoding="utf-8")),
        "timeline": read_csv(RESULTS / f"T418_{stage.upper()}_TIMELINE.csv"),
        "predictions": read_csv(RESULTS / f"T418_{stage.upper()}_PREDICTION_ROWS.csv"),
        "sequence": read_csv(RESULTS / f"T418_{stage.upper()}_SEQUENCE_METRICS.csv"),
        "eligibility": read_csv(RESULTS / f"T418_{stage.upper()}_SEQUENCE_ELIGIBILITY.csv"),
        "shift": read_csv(RESULTS / f"T418_{stage.upper()}_SHIFT_NULL.csv"),
    }


def gate_detail(name: str, gate: dict) -> str:
    if "ci95" in gate:
        return f"effect {gate['value']:.7f}; 95% field-bootstrap CI {gate['ci95'][0]:.7f} to {gate['ci95'][1]:.7f}"
    if "empirical_p" in gate:
        return f"child MSE {gate['value']:.6f}; shifted median {gate['null_median']:.6f}; p={gate['empirical_p']:.4f}"
    if "values" in gate:
        return "; ".join(f"{key} {value:+.7f}" for key, value in gate["values"].items())
    return f"value {gate['value']:.4f}; {gate['threshold']}"


def main() -> None:
    validation = load_stage("validation")
    holdout = load_stage("holdout")
    audit = json.loads((RESULTS / "T418_VALIDATION_AUDIT.json").read_text(encoding="utf-8"))
    vr = validation["result"]
    hr = holdout["result"]

    def relative_improvement(result: dict, model_key: str) -> float:
        baseline = result["errors"]["baseline_mse"]
        return 100.0 * (baseline - result["errors"][model_key]) / baseline

    headline = [{
        "validation_child_median": num(vr["child_post_boundary"]["median"], 4),
        "validation_child_q10": num(vr["child_post_boundary"]["q10"], 4),
        "validation_child_q90": num(vr["child_post_boundary"]["q90"], 4),
        "holdout_child_median": num(hr["child_post_boundary"]["median"], 4),
        "holdout_child_q10": num(hr["child_post_boundary"]["q10"], 4),
        "holdout_child_q90": num(hr["child_post_boundary"]["q90"], 4),
        "validation_improvement_pct": num(relative_improvement(vr, "child_mse"), 3),
        "holdout_improvement_pct": num(relative_improvement(hr, "child_mse"), 3),
        "validation_timing_p": num(vr["gates"]["G3_timing_specificity"]["empirical_p"], 4),
        "holdout_timing_p": num(hr["gates"]["G3_timing_specificity"]["empirical_p"], 4),
        "validation_support": "No",
        "holdout_support": "No",
    }]

    plane = {}
    for stage_name, loaded in (("validation", validation), ("high-field holdout", holdout)):
        rows = []
        raw = loaded["timeline"]
        # Keep the portable snapshot bounded while retaining the full curve shape.
        stride = max(1, math.ceil(len(raw) / 1700))
        for row in raw[::stride]:
            rows.append({
                "amount_A": num(row["coupled_amount_A"]),
                "balance_B": num(row["coupled_balance_B"]),
                "series": stage_label(float(row["parent_ARA"])),
                "field_G": num(row["field_G"], 1),
                "period": row["period"],
                "time_us": num(row["time_us"], 4),
                "parent_ARA": num(row["parent_ARA"]),
                "child_x": num(row["child_x"]),
            })
        for index in range(61):
            amount = 1.0 + index / 60.0
            rows.append({
                "amount_A": num(amount),
                "balance_B": num(2.0 / amount),
                "series": "exact I=2 boundary",
                "field_G": None,
                "period": "geometry",
                "time_us": None,
                "parent_ARA": None,
                "child_x": 1.0,
            })
            rows.append({
                "amount_A": num(amount),
                "balance_B": num(2.0 - 2.0 / amount),
                "series": "exact R=2 boundary",
                "field_G": None,
                "period": "geometry",
                "time_us": None,
                "parent_ARA": None,
                "child_x": 1.0,
            })
        plane[stage_name] = rows

    def example_rows(loaded: dict, field: float) -> dict[str, list[dict]]:
        result = {"RF on": [], "RF off": []}
        available = sorted({float(row["field_G"]) for row in loaded["timeline"]})
        chosen = min(available, key=lambda value: abs(value - field))
        for row in loaded["timeline"]:
            if abs(float(row["field_G"]) - chosen) > 1e-6:
                continue
            result[row["period"]].append({
                "time_us": num(row["time_us"], 4),
                "parent_ARA": num(row["parent_ARA"]),
                "parent_I_clipped": num(row["irrational_parent_I"]),
                "opened_child_x": num(row["child_x"]),
                "child_anti_x": num(row["child_anti_x"]),
                "raw_ratio_q": num(row["raw_loss_ratio_q"]),
                "field_G": num(row["field_G"], 1),
            })
        return result

    validation_example = example_rows(validation, 284.0)
    holdout_example = example_rows(holdout, 1800.0)

    child_distribution = []
    for label, loaded in (("validation 68–500 G", validation), ("holdout 1800–2484 G", holdout)):
        values = [float(row["child_x"]) for row in loaded["timeline"] if float(row["raw_loss_ratio_q"]) >= 1.0]
        child_distribution.extend(histogram(values, 1.0, 1.4, 20, label))

    model_comparison = []
    model_keys = [
        ("child_mse", "correctly timed child"),
        ("wrong_frequency_mse", "wrong-frequency child"),
        ("reverse_mse", "reversed child"),
    ]
    for label, result in (("validation 68–500 G", vr), ("holdout 1800–2484 G", hr)):
        for key, model in model_keys:
            model_comparison.append({
                "split": label,
                "model": model,
                "relative_improvement_pct": num(relative_improvement(result, key), 5),
                "model_mse": num(result["errors"][key]),
                "baseline_mse": num(result["errors"]["baseline_mse"]),
            })

    sequence_improvement = {"validation": [], "holdout": []}
    for name, loaded in (("validation", validation), ("holdout", holdout)):
        for row in loaded["sequence"]:
            base = float(row["baseline_mse"])
            sequence_improvement[name].append({
                "field_G": num(row["field_G"], 1),
                "period": row["period"],
                "relative_improvement_pct": num(100.0 * float(row["baseline_minus_child"]) / base, 5),
                "scored_rows": int(row["scored_rows"]),
                "child_mse": num(row["child_mse"]),
                "baseline_mse": num(base),
            })

    shift_histograms = {}
    for name, loaded in (("validation", validation), ("holdout", holdout)):
        values = [float(row["shifted_child_mse"]) for row in loaded["shift"]]
        lo, hi = min(values), max(values)
        shift_histograms[name] = histogram(values, lo, hi, 24, name)

    gates = []
    gate_labels = {
        "G1_availability": "Post-boundary child is available",
        "G2_added_future_state_information": "Child adds future-State information",
        "G3_timing_specificity": "Correct timing beats circular shifts",
        "G4_frequency_specificity": "Correct frequency beats wrong frequency",
        "G5_direction_specificity": "Forward child beats reversed child",
        "G6_rf_robustness": "Improvement holds in RF-on and RF-off",
    }
    for split, result in (("validation 68–500 G", vr), ("holdout 1800–2484 G", hr)):
        for key, label in gate_labels.items():
            gate = result["gates"][key]
            gates.append({
                "split": split,
                "gate": key.split("_", 1)[0],
                "test": label,
                "status": "PASS" if gate["pass"] else "FAIL",
                "result": gate_detail(key, gate),
            })

    audit_rows = []
    for split, content in audit.items():
        if not isinstance(content, dict) or "checks" not in content:
            continue
        for check_name, passed in content["checks"].items():
            audit_rows.append({
                "split": split,
                "check": check_name.replace("_", " ").title(),
                "status": "PASS" if passed else "FAIL",
            })

    datasets = {
        "headline": headline,
        "validation_plane": plane["validation"],
        "holdout_plane": plane["high-field holdout"],
        "validation_example_on": validation_example["RF on"],
        "validation_example_off": validation_example["RF off"],
        "holdout_example_on": holdout_example["RF on"],
        "holdout_example_off": holdout_example["RF off"],
        "child_distribution": child_distribution,
        "model_comparison": model_comparison,
        "validation_sequence_improvement": sequence_improvement["validation"],
        "holdout_sequence_improvement": sequence_improvement["holdout"],
        "validation_shift_histogram": shift_histograms["validation"],
        "holdout_shift_histogram": shift_histograms["holdout"],
        "gates": gates,
        "audit": audit_rows,
    }

    if SQLITE_OUTPUT.exists():
        SQLITE_OUTPUT.unlink()
    with sqlite3.connect(SQLITE_OUTPUT) as connection:
        for name, rows in datasets.items():
            write_sqlite_table(connection, name, rows)
        connection.commit()

    sources = [
        {
            "id": "isis-rb1620447",
            "label": "ISIS RB1620447 public RF-µSR archive",
            "href": DOI,
            "query": {
                "engine": "ISIS DataGateway",
                "url": DOI,
                "description": "Public silver-target RF-µSR ensemble histograms used for the locked T418 analysis.",
                "filters": [
                    "300 K silver target",
                    "Validation fields 68–500 G",
                    "Hard-transfer holdout fields 1800–2484 G",
                    "RF-on and RF-off scored as separate identities",
                    "Population ensemble measurements; not event-linked individual muons or neutrinos",
                ],
                "tables_used": ["ISIS investigation RB1620447 raw NeXus records"],
            },
        },
        {
            "id": "t418-analysis",
            "label": "T418 frozen parent-boundary child-continuation analysis",
            "href": DOI,
            "query": {
                "engine": "Python 3.12",
                "description": "Frozen child-coordinate construction and causal future-State prediction with development-only fitting.",
                "filters": [
                    "T417 population spin identity and past-only history retained",
                    "Prediction horizon four T416 reads = 16 native bins, about 0.256 microseconds",
                    "Development fixes coefficients and thresholds before validation and holdout",
                    "Magnetic fields are the bootstrap unit",
                ],
                "metric_definitions": [
                    "q = local history loss divided by null-history loss",
                    "I_parent = 2 min(1,q)",
                    "x_child = 2q/(1+q)",
                    "x_child_anti = 2-x_child",
                    "Prediction error = squared Euclidean error in future State (xL,xC)",
                    "Relative improvement = 100 times (baseline MSE minus model MSE) divided by baseline MSE",
                ],
                "tables_used": [
                    "T418_*_TIMELINE.csv",
                    "T418_*_PREDICTION_ROWS.csv",
                    "T418_*_SEQUENCE_METRICS.csv",
                    "T418_*_SHIFT_NULL.csv",
                    "T418_*_RESULTS.json",
                    "T418_VALIDATION_AUDIT.json",
                ],
            },
        },
    ]
    descriptions = {
        "headline": "T418 validation and high-field holdout headline estimates.",
        "validation_plane": "Validation amount/balance plane with exact parent boundaries.",
        "holdout_plane": "High-field holdout amount/balance plane with exact parent boundaries.",
        "validation_example_on": "284 G RF-on child opening through corrected ensemble time.",
        "validation_example_off": "284 G RF-off child opening through corrected ensemble time.",
        "holdout_example_on": "1800 G RF-on child opening through corrected ensemble time.",
        "holdout_example_off": "1800 G RF-off child opening through corrected ensemble time.",
        "child_distribution": "Post-boundary opened-child distribution by field regime.",
        "model_comparison": "Relative future-State prediction performance against the parent/State baseline.",
        "validation_sequence_improvement": "Per-field and RF-period validation prediction changes.",
        "holdout_sequence_improvement": "Per-field and RF-period high-field holdout prediction changes.",
        "validation_shift_histogram": "Validation circular-shift timing null.",
        "holdout_shift_histogram": "High-field holdout circular-shift timing null.",
        "gates": "All frozen T418 validation and holdout gates.",
        "audit": "Independent T418 hash, geometry, chronology, arithmetic, and boundary audit.",
    }
    sources.extend(table_source(name, description) for name, description in descriptions.items())

    cards = [
        {
            "id": "validation-child-card",
            "description": "Opened child coordinate after the parent I=2 boundary in ordinary-field validation.",
            "dataset": "headline",
            "sourceId": "t418-headline",
            "metrics": [
                {"field": "validation_child_median", "label": "Validation child median", "format": "number"},
                {"field": "validation_child_q10", "label": "10th percentile", "format": "number"},
                {"field": "validation_child_q90", "label": "90th percentile", "format": "number"},
            ],
        },
        {
            "id": "holdout-child-card",
            "description": "Opened child coordinate after the parent boundary in the much higher-field holdout.",
            "dataset": "headline",
            "sourceId": "t418-headline",
            "metrics": [
                {"field": "holdout_child_median", "label": "High-field child median", "format": "number"},
                {"field": "holdout_child_q10", "label": "10th percentile", "format": "number"},
                {"field": "holdout_child_q90", "label": "90th percentile", "format": "number"},
            ],
        },
        {
            "id": "validation-prediction-card",
            "description": "Aggregate validation MSE change when the opened child is added to the baseline.",
            "dataset": "headline",
            "sourceId": "t418-headline",
            "metrics": [{"field": "validation_improvement_pct", "label": "Validation improvement", "format": "number", "unit": "%"}],
        },
        {
            "id": "holdout-prediction-card",
            "description": "Aggregate high-field holdout MSE change when the opened child is added.",
            "dataset": "headline",
            "sourceId": "t418-headline",
            "metrics": [{"field": "holdout_improvement_pct", "label": "High-field improvement", "format": "number", "unit": "%"}],
        },
    ]

    ridge = [{"axis": "y", "value": 1, "label": "child ridge", "lineStyle": "dashed"}]
    charts = [
        chart("validation-plane", "Validation coupled plane and exact parent shorelines", "68–500 G; observation stages and algebraic I=2/R=2 boundaries share the same A/B axes", "scatter", "validation_plane", {
            "x": {"field": "amount_A", "type": "quantitative", "label": "Coupled amount A"},
            "y": {"field": "balance_B", "type": "quantitative", "label": "Coupled balance B"},
            "color": {"field": "series", "type": "nominal", "label": "Observation stage or exact boundary"},
            "tooltip": [{"field": "series", "type": "nominal"}, {"field": "field_G", "type": "quantitative", "unit": "G"}, {"field": "period", "type": "nominal"}, {"field": "time_us", "type": "quantitative", "unit": "µs"}, {"field": "child_x", "type": "quantitative"}],
        }, "Coupled amount A (0–2)", "Balance B: R-leading 0 ← 1 → I-leading 2", [{"axis": "y", "value": 1, "label": "R=I ridge", "lineStyle": "dashed"}]),
        chart("holdout-plane", "High-field holdout coupled plane and exact shorelines", "1800–2484 G; shown separately because this is a substantially stronger magnetic-field regime", "scatter", "holdout_plane", {
            "x": {"field": "amount_A", "type": "quantitative", "label": "Coupled amount A"},
            "y": {"field": "balance_B", "type": "quantitative", "label": "Coupled balance B"},
            "color": {"field": "series", "type": "nominal", "label": "Observation stage or exact boundary"},
            "tooltip": [{"field": "series", "type": "nominal"}, {"field": "field_G", "type": "quantitative", "unit": "G"}, {"field": "period", "type": "nominal"}, {"field": "time_us", "type": "quantitative", "unit": "µs"}, {"field": "child_x", "type": "quantitative"}],
        }, "Coupled amount A (0–2)", "Balance B: R-leading 0 ← 1 → I-leading 2", [{"axis": "y", "value": 1, "label": "R=I ridge", "lineStyle": "dashed"}]),
        chart("validation-example-on", "284 G RF-on: parent ceiling opened as a child ARA", "The parent I coordinate clips at 2; the raw local/null ratio remains finite and maps through the child ridge", "line", "validation_example_on", {
            "x": {"field": "time_us", "type": "quantitative", "label": "Corrected ensemble time", "unit": "µs"},
            "y": {"fields": ["parent_I_clipped", "opened_child_x", "child_anti_x", "parent_ARA"], "type": "quantitative", "label": "ARA coordinate"},
            "tooltip": [{"field": "time_us", "type": "quantitative", "unit": "µs"}, {"field": "parent_I_clipped", "type": "quantitative"}, {"field": "opened_child_x", "type": "quantitative"}, {"field": "child_anti_x", "type": "quantitative"}, {"field": "raw_ratio_q", "type": "quantitative"}],
        }, "Corrected ensemble time (µs)", "ARA coordinate (0–2)", ridge + [{"axis": "y", "value": 2, "label": "parent I ceiling", "lineStyle": "dotted"}]),
        chart("validation-example-off", "284 G RF-off: the same opening without joining RF identities", "RF-off is a separate sequence; the child and anti-child always close to TE-ARA 2", "line", "validation_example_off", {
            "x": {"field": "time_us", "type": "quantitative", "label": "Corrected ensemble time", "unit": "µs"},
            "y": {"fields": ["parent_I_clipped", "opened_child_x", "child_anti_x", "parent_ARA"], "type": "quantitative", "label": "ARA coordinate"},
            "tooltip": [{"field": "time_us", "type": "quantitative", "unit": "µs"}, {"field": "parent_I_clipped", "type": "quantitative"}, {"field": "opened_child_x", "type": "quantitative"}, {"field": "child_anti_x", "type": "quantitative"}, {"field": "raw_ratio_q", "type": "quantitative"}],
        }, "Corrected ensemble time (µs)", "ARA coordinate (0–2)", ridge + [{"axis": "y", "value": 2, "label": "parent I ceiling", "lineStyle": "dotted"}]),
        chart("child-distribution", "Opened child coordinates after parent contact", "Counts are shown separately for ordinary-field validation and high-field holdout", "bar", "child_distribution", {
            "x": {"field": "bin_mid", "type": "quantitative", "label": "Opened child coordinate"},
            "y": {"field": "count", "type": "quantitative", "label": "Post-boundary windows"},
            "color": {"field": "split", "type": "nominal", "label": "Field regime"},
            "tooltip": [{"field": "split", "type": "nominal"}, {"field": "bin_mid", "type": "quantitative"}, {"field": "count", "type": "quantitative"}],
        }, "Opened child ARA coordinate (1–1.4)", "Post-boundary ensemble windows", [{"axis": "x", "value": 1, "label": "child ridge / parent contact", "lineStyle": "dashed"}]),
        chart("model-comparison", "Future-State prediction change versus the parent/State baseline", "Positive is better; the small validation gain reverses in the high-field holdout", "bar", "model_comparison", {
            "x": {"field": "model", "type": "nominal", "label": "Added child representation"},
            "y": {"field": "relative_improvement_pct", "type": "quantitative", "label": "MSE improvement", "unit": "%"},
            "color": {"field": "split", "type": "nominal", "label": "Field regime"},
            "tooltip": [{"field": "split", "type": "nominal"}, {"field": "model", "type": "nominal"}, {"field": "relative_improvement_pct", "type": "quantitative", "unit": "%"}, {"field": "model_mse", "type": "quantitative"}, {"field": "baseline_mse", "type": "quantitative"}],
        }, "Added child representation", "Relative MSE improvement over baseline (%)", [{"axis": "y", "value": 0, "label": "no improvement", "lineStyle": "dashed"}]),
        chart("validation-field", "Validation improvement by field and RF period", "68–500 G; positive values mean the child model improves future-State prediction", "scatter", "validation_sequence_improvement", {
            "x": {"field": "field_G", "type": "quantitative", "label": "Magnetic field", "unit": "G"},
            "y": {"field": "relative_improvement_pct", "type": "quantitative", "label": "MSE improvement", "unit": "%"},
            "color": {"field": "period", "type": "nominal", "label": "RF period"},
            "tooltip": [{"field": "field_G", "type": "quantitative", "unit": "G"}, {"field": "period", "type": "nominal"}, {"field": "relative_improvement_pct", "type": "quantitative", "unit": "%"}, {"field": "scored_rows", "type": "quantitative"}],
        }, "Magnetic field (G)", "Sequence MSE improvement (%)", [{"axis": "y", "value": 0, "label": "no improvement", "lineStyle": "dashed"}]),
        chart("holdout-field", "High-field holdout improvement by field and RF period", "1800–2484 G; this is a hard regime transfer, not a matched-field replication", "scatter", "holdout_sequence_improvement", {
            "x": {"field": "field_G", "type": "quantitative", "label": "Magnetic field", "unit": "G"},
            "y": {"field": "relative_improvement_pct", "type": "quantitative", "label": "MSE improvement", "unit": "%"},
            "color": {"field": "period", "type": "nominal", "label": "RF period"},
            "tooltip": [{"field": "field_G", "type": "quantitative", "unit": "G"}, {"field": "period", "type": "nominal"}, {"field": "relative_improvement_pct", "type": "quantitative", "unit": "%"}, {"field": "scored_rows", "type": "quantitative"}],
        }, "Magnetic field (G)", "Sequence MSE improvement (%)", [{"axis": "y", "value": 0, "label": "no improvement", "lineStyle": "dashed"}]),
        chart("validation-shifts", "Validation timing-shift null", "1,000 circular shifts; correctly timed child MSE is marked", "bar", "validation_shift_histogram", {
            "x": {"field": "bin_mid", "type": "quantitative", "label": "Shifted child MSE"},
            "y": {"field": "count", "type": "quantitative", "label": "Shift draws"},
            "tooltip": [{"field": "bin_mid", "type": "quantitative"}, {"field": "count", "type": "quantitative"}],
        }, "Shifted child future-State MSE", "Circular-shift draws", [{"axis": "x", "value": vr["errors"]["child_mse"], "label": "correctly timed child", "lineStyle": "dashed"}]),
        chart("holdout-shifts", "High-field holdout timing-shift null", "1,000 circular shifts; the correctly timed child no longer sits in the favourable tail", "bar", "holdout_shift_histogram", {
            "x": {"field": "bin_mid", "type": "quantitative", "label": "Shifted child MSE"},
            "y": {"field": "count", "type": "quantitative", "label": "Shift draws"},
            "tooltip": [{"field": "bin_mid", "type": "quantitative"}, {"field": "count", "type": "quantitative"}],
        }, "Shifted child future-State MSE", "Circular-shift draws", [{"axis": "x", "value": hr["errors"]["child_mse"], "label": "correctly timed child", "lineStyle": "dashed"}]),
    ]

    tables = [
        {
            "id": "gates-table",
            "title": "Frozen validation and holdout gates",
            "subtitle": "Every gate remains exactly as declared before the locked stages were opened",
            "showDescription": True,
            "dataset": "gates",
            "sourceId": "t418-gates",
            "density": "spacious",
            "layout": "full",
            "defaultSort": {"field": "split", "direction": "asc"},
            "columns": [
                {"field": "split", "label": "Field regime", "type": "text"},
                {"field": "gate", "label": "Gate", "type": "text"},
                {"field": "test", "label": "Frozen question", "type": "text"},
                {"field": "status", "label": "Status", "type": "text"},
                {"field": "result", "label": "Estimate and uncertainty", "type": "text"},
            ],
        },
        {
            "id": "audit-table",
            "title": "Independent saved-output audit",
            "subtitle": "Development, validation and holdout hashes, formulas, chronology and recomputed summaries",
            "showDescription": True,
            "dataset": "audit",
            "sourceId": "t418-audit",
            "density": "dense",
            "layout": "full",
            "defaultSort": {"field": "split", "direction": "asc"},
            "columns": [
                {"field": "split", "label": "Stage", "type": "text"},
                {"field": "check", "label": "Independent check", "type": "text"},
                {"field": "status", "label": "Status", "type": "text"},
            ],
        },
    ]

    blocks = [
        {"id": "title", "type": "markdown", "body": f"# {TITLE}"},
        {"id": "summary", "type": "markdown", "sourceId": "t418-headline", "body": "## The shoreline contains measured continuation, but not yet a predictive adjacent identity\n\n**T418 confirms that the curved T417 edge is not an empty plotting accident.** The clipped parent coordinate `I_parent=2` hides continued variation in the measured local/null history-loss ratio. Reopening that ratio as a child ARA places the post-boundary median at **1.068** in ordinary-field validation and **1.063** in the much higher-field holdout.\n\n**The stronger prediction did not survive.** Adding this child coordinate improved aggregate future-State MSE by only **0.86%** in validation and worsened it by **0.27%** in the high-field holdout. Validation timing specificity passed once (`p=0.041`), but the holdout result was `p=0.764`; frequency, direction and RF-period gates were not jointly satisfied. The exact ARA continuation is therefore supported as a descriptive recovery of information beneath the parent ceiling, while the claim that it identifies the next predictive State sphere is **not supported by T418**."},
        {"id": "metrics", "type": "metric-strip", "cardIds": [card["id"] for card in cards], "dataset": "headline"},
        {"id": "shoreline-text", "type": "markdown", "sourceId": "t418-validation-plane", "body": "## The curved edge is an exact parent boundary, not the end of the relation\n\nIn the T417 coupled coordinates, `I=A×B` and `R=A×(2−B)`. The upper shoreline is therefore exactly `A×B=2`, or `B=2/A`; the lower shoreline is `A×(2−B)=2`. The observation cloud approaching that curve means the unresolved parent component has reached its 2.0 coordinate ceiling. It does **not** say the underlying measured ratio stopped changing. The boundary is informative in the same sense that a coastline is informative: it tells us where the present coordinate system ends and where a new cut must begin."},
        {"id": "validation-plane-block", "type": "chart", "chartId": "validation-plane", "layout": "full"},
        {"id": "holdout-plane-text", "type": "markdown", "sourceId": "t418-holdout-plane", "body": "## The same boundary shape remains visible under much stronger field coupling\n\nThe holdout uses the same silver target, temperature and measurement architecture, but fields of **1800–2484 G** rather than **68–500 G**. It is therefore a hard regime transfer, not a like-for-like replication. The exact boundary still organizes the cloud, which supports the coordinate geometry; any forecast comparison must remain separate because the physical coupling regime changed substantially."},
        {"id": "holdout-plane-block", "type": "chart", "chartId": "holdout-plane", "layout": "full"},
        {"id": "definition-text", "type": "markdown", "sourceId": "t418-analysis", "body": "## Opening the boundary creates a child 0–2 coordinate without changing identity\n\nThe same T417 population spin identity and past-only history were retained. Let `q=L_local/L_null`. The parent view clips this as `I_parent=2 min(1,q)`, so every `q≥1` looks identical at the parent pole. T418 decompressed that hidden ratio as `x_child=2q/(1+q)` and `x_child_anti=2−x_child`. At `q=1`, parent contact is exactly the child ridge `x_child=1`; values above one continue through the child 1–2 half while preserving TE-ARA closure. This is an exact re-coordinate of the observed loss ratio—not an assumed particle or new physical object."},
        {"id": "example-text", "type": "markdown", "sourceId": "t418-validation-example-on", "body": "## At 284 G the parent pole stays flat while the child keeps moving\n\nThe parent unresolved coordinate reaches 2 and loses resolution. Beneath it, the opened child and its anti-phase continue as a complementary pair summing to 2. RF-on and RF-off are shown independently so no artificial line joins the two measurement periods. This is the direct visual answer to the shoreline question: there is measurable relational structure beneath the flattened parent edge."},
        {"id": "validation-example-on-block", "type": "chart", "chartId": "validation-example-on", "layout": "full"},
        {"id": "validation-example-off-block", "type": "chart", "chartId": "validation-example-off", "layout": "full"},
        {"id": "distribution-text", "type": "markdown", "sourceId": "t418-child-distribution", "body": "## The opened child rests just beyond its own ridge in both regimes\n\nPost-boundary values cluster near **1.06–1.07**, with validation 10th–90th percentiles of **1.014–1.157** and holdout percentiles of **1.014–1.146**. The holdout reaches farther at its extreme (`1.385` versus `1.308`) but has nearly the same central position. No null-loss denominator collapse produced this: the smallest denominators were 0.383 and 0.464, far from zero. The continuation is numerically stable; whether it is the correct physical branch requires an independent consequence."},
        {"id": "distribution-block", "type": "chart", "chartId": "child-distribution", "layout": "full"},
        {"id": "prediction-text", "type": "markdown", "sourceId": "t418-model-comparison", "body": "## The child coordinate does not robustly predict the later State Di-ARA\n\nA development-only linear model predicted later State coordinates `(xL,xC)` about **0.256 µs** ahead. The baseline already knew the parent and current State. Adding the correctly timed child gave only a small aggregate validation gain, and that gain reversed in high field. Wrong-frequency and reversed-child controls were often comparable. This means the observed continuation is not yet demonstrated as the adjacent State identity drawn beyond the shoreline. It may be descriptive, coupled to another downstream branch, or require an identity-specific transformation not captured by this target."},
        {"id": "model-comparison-block", "type": "chart", "chartId": "model-comparison", "layout": "full"},
        {"id": "field-text", "type": "markdown", "sourceId": "t418-validation-sequence-improvement", "body": "## Any predictive gain is field- and RF-dependent rather than universal\n\nThe sequence-level effects cross zero repeatedly. Validation’s aggregate improvement is therefore not a uniform result shared by both RF identities and all fields. The high-field plot is kept separate because extrapolating across that coupling jump would otherwise conceal the regime dependence."},
        {"id": "validation-field-block", "type": "chart", "chartId": "validation-field", "layout": "full"},
        {"id": "holdout-field-block", "type": "chart", "chartId": "holdout-field", "layout": "full"},
        {"id": "timing-text", "type": "markdown", "sourceId": "t418-validation-shift-histogram", "body": "## Correct timing is weakly distinctive only in ordinary-field validation\n\nIn validation, the correctly timed child beat 959 of 1,000 circular shifts (`p=0.041`). In the high-field holdout it sat well inside the shifted distribution (`p=0.764`). Because the stronger result did not replicate across the regime transfer—and the other specificity gates failed—the single validation timing pass is evidence of a local timing relation, not a universal child-handover clock."},
        {"id": "validation-shifts-block", "type": "chart", "chartId": "validation-shifts", "layout": "full"},
        {"id": "holdout-shifts-block", "type": "chart", "chartId": "holdout-shifts", "layout": "full"},
        {"id": "method-text", "type": "markdown", "sourceId": "t418-analysis", "body": "## Frozen causal design and controls\n\nAll prediction origins precede their targets. Development fixed the equations, horizon, models, controls and six gates before validation and holdout were opened. The baseline used parent ARA, closure `R`, and current State `(xL,xC)`; the child model added `x_child` and its causal first difference. Controls used 1,000 within-sequence circular shifts, the reverse coordinate `2−x_child`, and a wrong-frequency history child. Magnetic fields—not individual time windows—were bootstrapped. RF-on and RF-off were never connected across their boundary."},
        {"id": "gates-text", "type": "markdown", "body": "## Frozen verdict: descriptive continuation passes; predictive identity fails\n\nAvailability passed in both locked stages. Validation passed the timing-shift gate, while holdout passed only the direction comparison; neither stage passed the full gate set. The predeclared predictive claim is therefore **not supported**. This negative result does not erase the exact boundary or the stable continued ratio—it limits what that continuation may presently be called."},
        {"id": "gates-block", "type": "table", "tableId": "gates-table", "layout": "full"},
        {"id": "limits-text", "type": "markdown", "body": "## What T418 does and does not establish\n\n**Established within this measurement:** the parent clipping operation hides finite, stable local/null ratio variation; the exact child transform preserves that variation on a 0–2 ARA coordinate; every saved formula, chronology, RF boundary and summary recomputation passed independent audit.\n\n**Not established:** that the opened coordinate is a new physical muon constituent, an individual-muon handover, a neutrino signal, or the adjacent red/green sphere inferred from the T417 plane. These remain hypotheses because the chosen downstream consequence—later population State `(xL,xC)`—was not predicted robustly. The data are ensemble RF-µSR histograms, not event-linked particle records."},
        {"id": "next-text", "type": "markdown", "body": "## Recommended next cut\n\nKeep the shoreline result and change the downstream question, not the data after seeing the answer. Freeze the opened child’s **own** Di-ARA before opening another field set: use its amount/balance with the anti-child to predict its later reclosure, pole approach, or a lower-rung history transition. That tests whether the continuation has an internally ordered identity rather than asking it to predict a possibly different State branch. A second independent ordinary-field archive should then test the same frozen relation before another high-field transfer."},
        {"id": "questions-text", "type": "markdown", "body": "## Further questions\n\n- Does the opened child predict its own later closure better than it predicts the separate State `(xL,xC)` identity?\n- Which child or lateral branch should sit beyond the exact `I=2` shoreline under ARA ownership rules?\n- Is the high-field failure a genuine identity change, a field-dependent transform, or simple model misspecification?\n- Does a matched ordinary-field independent archive reproduce the validation timing tail?"},
        {"id": "audit-text", "type": "markdown", "sourceId": "t418-audit", "body": "## Independent audit\n\nAll development, validation and holdout checks passed: frozen protocol and code hashes, exact child/anti-child formulas, parent cap, A/B inversion, saved prediction errors, aggregate summaries, past-before-future chronology, RF separation, and denominator safety."},
        {"id": "audit-block", "type": "table", "tableId": "audit-table", "layout": "full"},
    ]

    generated = datetime.now(timezone.utc).isoformat()
    manifest = {
        "version": 1,
        "surface": "report",
        "title": TITLE,
        "description": "Frozen T418 test of the child continuation beneath the T417 parent boundary.",
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

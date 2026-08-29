#!/usr/bin/env python3
"""Build the canonical portable technical report for T414."""

from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUTPUT = RESULTS / "T414_REPORT_ARTIFACT.json"
SQLITE_OUTPUT = RESULTS / "T414_REPORT_DATA.sqlite"
TITLE = "T414 — Spin child within the muon lifespan parent"
DOI = "https://data.isis.stfc.ac.uk/doi/STUDY/103197258"


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def rounded(value: float, digits: int = 8) -> float:
    return round(float(value), digits)


def write_sqlite_table(connection: sqlite3.Connection, name: str, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"Cannot create empty report table: {name}")
    fields = list(rows[0])
    types = []
    for field in fields:
        values = [row.get(field) for row in rows if row.get(field) is not None]
        types.append("REAL" if values and all(isinstance(value, (int, float, bool)) for value in values) else "TEXT")
    columns = ", ".join(f'"{field}" {sql_type}' for field, sql_type in zip(fields, types))
    connection.execute(f'CREATE TABLE "{name}" ({columns})')
    placeholders = ", ".join("?" for _ in fields)
    connection.executemany(f'INSERT INTO "{name}" VALUES ({placeholders})', [[row.get(field) for field in fields] for row in rows])


def table_source(source_id: str, label: str, table: str, description: str) -> dict:
    return {
        "id": source_id,
        "label": label,
        "href": DOI,
        "query": {
            "engine": "SQLite",
            "sql": f'SELECT * FROM "{table}";',
            "description": description,
            "tables_used": [f"T414_REPORT_DATA.sqlite::{table}"],
        },
    }


def main() -> None:
    result = json.loads((RESULTS / "T414_FULL_RESULTS.json").read_text(encoding="utf-8"))
    audit = json.loads((RESULTS / "T414_VALIDATION_AUDIT.json").read_text(encoding="utf-8"))
    metrics = read_csv(RESULTS / "T414_FULL_RUN_PERIOD_METRICS.csv")
    profiles = read_csv(RESULTS / "T414_FULL_AGGREGATE_PHASE_PROFILES.csv")
    aggregate = result["aggregate"]

    validation_on = aggregate["validation|primary|RF on"]
    validation_off = aggregate["validation|primary|RF off"]
    holdout_on = aggregate["holdout|primary|RF on"]
    holdout_off = aggregate["holdout|primary|RF off"]

    headline = [{
        "runs": result["run_count"],
        "run_periods": result["run_period_count"],
        "tau_dev_us": rounded(result["tau_dev_us"], 3),
        "gamma_dev_MHz_per_G": rounded(result["gamma_dev_MHz_per_G"], 6),
        "validation_spin_ratio_on": rounded(validation_on["median_direction_target_sideband_ratio"], 3),
        "validation_spin_ratio_off": rounded(validation_off["median_direction_target_sideband_ratio"], 3),
        "validation_release_supported": 0,
        "validation_spin_supported": 1,
    }]

    group_order = [
        ("Development", "development|primary"),
        ("Validation", "validation|primary"),
        ("Holdout", "holdout|primary"),
        ("Aliased sensitivity", "holdout|alias_sensitivity"),
    ]
    summary_ratios = []
    summary_detail = []
    for group_label, key_prefix in group_order:
        for period in ("RF on", "RF off"):
            item = aggregate.get(f"{key_prefix}|{period}")
            if item is None:
                continue
            label = f"{group_label} · {period}"
            summary_ratios.extend([
                {
                    "group": label,
                    "series": "Spin child (detector share)",
                    "target_sideband_ratio": rounded(item["median_direction_target_sideband_ratio"], 5),
                    "run_win_fraction": rounded(item["direction_run_win_fraction"], 5),
                    "run_count": item["run_count"],
                },
                {
                    "group": label,
                    "series": "Total release",
                    "target_sideband_ratio": rounded(item["median_release_target_sideband_ratio"], 5),
                    "run_win_fraction": rounded(item["release_run_win_fraction"], 5),
                    "run_count": item["run_count"],
                },
            ])
            summary_detail.append({
                "group": group_label,
                "period": period,
                "run_count": item["run_count"],
                "spin_ratio": rounded(item["median_direction_target_sideband_ratio"], 5),
                "spin_run_wins": rounded(item["direction_run_win_fraction"], 5),
                "spin_detector_control_wins": rounded(item["direction_broken_detector_win_fraction"], 5),
                "spin_time_control_wins": rounded(item["direction_broken_time_win_fraction"], 5),
                "release_ratio": rounded(item["median_release_target_sideband_ratio"], 5),
                "release_run_wins": rounded(item["release_run_win_fraction"], 5),
                "release_time_control_wins": rounded(item["release_broken_time_win_fraction"], 5),
                "release_phase_resultant": rounded(item["release_phase_resultant"], 5),
                "release_peak_x_spin": rounded(item["release_phase_peak_x_spin"], 5),
            })

    resolution = []
    for row in metrics:
        if row["alias_class"] != "primary":
            continue
        frequency = float(row["frequency_MHz"])
        resolution.append({
            "run": row["run"],
            "split": row["split"].title(),
            "period": row["period"],
            "series": f"{row['split'].title()} · {row['period']}",
            "field_G": float(row["field_G"]),
            "frequency_MHz": rounded(frequency, 5),
            "samples_per_cycle": rounded(1.0 / (0.016 * frequency), 5),
            "spin_target_sideband_ratio": rounded(float(row["direction_target_sideband_ratio"]), 5),
            "release_target_sideband_ratio": rounded(float(row["release_target_sideband_ratio"]), 5),
        })

    validation_direction_profile = []
    release_profile = []
    for row in profiles:
        if row["alias_class"] != "primary":
            continue
        if row["split"] == "validation" and row["measure"] == "direction_cos":
            validation_direction_profile.append({
                "x_spin": float(row["x_spin_mid"]),
                "period": row["period"],
                "direction_projection": rounded(float(row["mean"]), 8),
                "se": rounded(float(row["se"]), 8),
                "run_count": int(row["run_count"]),
            })
        if row["split"] in ("validation", "holdout") and row["measure"] == "release_residual":
            release_profile.append({
                "x_spin": float(row["x_spin_mid"]),
                "series": f"{row['split'].title()} · {row['period']}",
                "split": row["split"].title(),
                "period": row["period"],
                "release_residual": rounded(float(row["mean"]), 8),
                "se": rounded(float(row["se"]), 8),
                "run_count": int(row["run_count"]),
            })

    # A fixed validation field shows the literal local child cycle nested in
    # the calibrated parent release coordinate. These are coordinates, not an
    # additional fitted result.
    example_field = 284.0
    tau = float(result["tau_dev_us"])
    frequency = float(result["gamma_dev_MHz_per_G"]) * example_field
    coordinate_path = []
    for time in np.arange(0.25, 6.0, 0.016):
        phase_fraction = (frequency * time) % 1.0
        coordinate_path.append({
            "time_us": rounded(time, 6),
            # Wrapped angular position around the spin cycle. This is not a
            # diameter projection through the cycle.
            "spin_child_ARA": rounded(2.0 * phase_fraction, 6),
            # Two mutually perpendicular diameter cuts through the same
            # frozen spin phase. Both remain on the 0--2 ARA coordinate.
            "spin_diameter_cut_A_ARA": rounded(1.0 + np.sin(2.0 * np.pi * phase_fraction), 6),
            "spin_diameter_cut_B_ARA": rounded(1.0 + np.cos(2.0 * np.pi * phase_fraction), 6),
            "parent_release_ARA": rounded(2.0 * (1.0 - np.exp(-time / tau)), 6),
            "field_G": example_field,
            "frequency_MHz": rounded(frequency, 6),
        })

    gates = [
        {
            "gate": "Resolved validation spin child",
            "status": "SUPPORTED",
            "evidence": "RF-on and RF-off median target/sideband ratios were 2.414 and 2.449; all 13 runs beat their sideband medians.",
        },
        {
            "gate": "Validation total-release phase lock",
            "status": "NOT SUPPORTED",
            "evidence": "Release ratios were only 1.082 and 1.049, control performance was inconsistent, and preferred phases differed by 0.466 ARA.",
        },
        {
            "gate": "High-field transfer of spin child",
            "status": "NOT SUPPORTED",
            "evidence": "At about 2.25 samples per cycle, holdout ratios were 0.938 and 1.013 and intact order lost to both broken controls.",
        },
        {
            "gate": "Independent audit",
            "status": audit["status"].upper(),
            "evidence": "Protocol, code, validation freeze, source hashes, channel separation, coordinates, aggregate gates, and split reproducibility all passed.",
        },
    ]

    if SQLITE_OUTPUT.exists():
        SQLITE_OUTPUT.unlink()
    with sqlite3.connect(SQLITE_OUTPUT) as connection:
        write_sqlite_table(connection, "headline", headline)
        write_sqlite_table(connection, "summary_ratios", summary_ratios)
        write_sqlite_table(connection, "summary_detail", summary_detail)
        write_sqlite_table(connection, "resolution", resolution)
        write_sqlite_table(connection, "validation_direction_profile", validation_direction_profile)
        write_sqlite_table(connection, "release_profile", release_profile)
        write_sqlite_table(connection, "coordinate_path", coordinate_path)
        write_sqlite_table(connection, "gates", gates)
        connection.commit()

    raw_source = {
        "id": "isis-rb1620447",
        "label": "ISIS RB1620447 public RF-µSR dataset",
        "href": DOI,
        "query": {
            "engine": "ISIS DataGateway",
            "url": DOI,
            "description": "Forty-six public EMU HDF4/NeXus runs from the RF-µSR acetone experiment.",
            "filters": [
                "Corrected time 0.25–6.00 microseconds at native 0.016-microsecond sampling",
                "13 development, 13 validation, and 20 holdout runs",
                "RF-on and RF-off analysed separately",
            ],
            "tables_used": ["ISIS investigation RB1620447 / raw NeXus dataset"],
        },
    }
    analysis_source = {
        "id": "t414-frozen-analysis",
        "label": "T414 frozen spin-child / lifespan-parent analysis",
        "href": DOI,
        "query": {
            "engine": "Python 3.12",
            "query": "python t414_spin_child_lifespan_parent.py --splits development,validation,holdout --suffix FULL",
            "description": "Frozen detector-share spin calibration, detector-total release test, controls, and ARA profiles.",
            "language": "shell",
            "filters": [
                "Development-only frequency slope 0.013549 MHz/G",
                "Development-only parent lifetime 2.203 microseconds",
                "Primary holdout at or below 31.25 MHz; five higher-frequency runs reported as alias sensitivity",
            ],
            "metric_definitions": [
                "Spin child x_s = 2 frac(f t)",
                "Parent release x_p = 2(1-exp(-t/tau))",
                "Spin statistic uses detector shares; release statistic uses detector sums",
                "Target/sideband ratio above 1 means the frozen frequency beats the median wrong-frequency control",
            ],
            "tables_used": [
                "T414_FULL_RUN_PERIOD_METRICS.csv",
                "T414_FULL_AGGREGATE_PHASE_PROFILES.csv",
                "T414_FULL_RESULTS.json",
                "T414_VALIDATION_AUDIT.json",
            ],
        },
    }
    sources = [
        raw_source,
        analysis_source,
        table_source("t414-headline", "T414 headline metrics", "headline", "Frozen calibration and validation headline metrics."),
        table_source("t414-summary-ratios", "T414 channel ratios", "summary_ratios", "Median target/sideband ratios by split, RF identity, and channel."),
        table_source("t414-summary-detail", "T414 gate detail", "summary_detail", "Run-win, control-win, and phase-coherence detail."),
        table_source("t414-resolution", "T414 sampling-resolution diagnostic", "resolution", "Samples per cycle and frozen spin/release ratios for every primary run-period."),
        table_source("t414-direction-profile", "T414 validation spin profile", "validation_direction_profile", "Validation detector-share projection across local spin ARA."),
        table_source("t414-release-profile", "T414 release profile", "release_profile", "Validation and holdout release residual across local spin ARA."),
        table_source("t414-coordinate-path", "T414 ARA coordinate path", "coordinate_path", "Fixed 284 G validation example of child phase inside parent release."),
        table_source("t414-gates", "T414 frozen gates", "gates", "Frozen interpretation gates and audit outcome."),
    ]

    charts = [
        {
            "id": "ratio-chart",
            "title": "Frozen frequency signal relative to wrong-frequency controls",
            "subtitle": "Median target/sideband ratio by split, RF identity, and measurement channel; 1 is parity",
            "showDescription": True,
            "type": "bar",
            "intent": "comparison",
            "dataset": "summary_ratios",
            "sourceId": "t414-summary-ratios",
            "encodings": {
                "x": {"field": "group", "type": "nominal", "label": "Split and RF identity"},
                "y": {"field": "target_sideband_ratio", "type": "quantitative", "label": "Target / sideband median"},
                "color": {"field": "series", "type": "nominal", "label": "Measurement channel"},
                "tooltip": [
                    {"field": "group", "type": "nominal"},
                    {"field": "series", "type": "nominal"},
                    {"field": "target_sideband_ratio", "type": "quantitative"},
                    {"field": "run_win_fraction", "type": "quantitative"},
                    {"field": "run_count", "type": "quantitative"},
                ],
            },
            "xAxisTitle": "Split and RF identity",
            "yAxisTitle": "Target / sideband median",
            "referenceLines": [{"axis": "y", "value": 1, "label": "sideband parity", "lineStyle": "dashed"}],
            "layout": "full",
        },
        {
            "id": "resolution-chart",
            "title": "Spin-child recovery versus temporal sampling",
            "subtitle": "Each point is one run-period; high-field holdout cycles have only about 2.25 samples per turn",
            "showDescription": True,
            "type": "scatter",
            "intent": "relationship",
            "dataset": "resolution",
            "sourceId": "t414-resolution",
            "encodings": {
                "x": {"field": "samples_per_cycle", "type": "quantitative", "label": "Native samples per frozen spin cycle"},
                "y": {"field": "spin_target_sideband_ratio", "type": "quantitative", "label": "Spin target / sideband median"},
                "color": {"field": "split", "type": "nominal", "label": "Data split"},
                "tooltip": [
                    {"field": "run", "type": "nominal"},
                    {"field": "period", "type": "nominal"},
                    {"field": "field_G", "type": "quantitative", "unit": "G"},
                    {"field": "frequency_MHz", "type": "quantitative", "unit": "MHz"},
                    {"field": "samples_per_cycle", "type": "quantitative"},
                    {"field": "spin_target_sideband_ratio", "type": "quantitative"},
                ],
            },
            "xAxisTitle": "Native samples per spin cycle",
            "yAxisTitle": "Spin target / sideband median",
            "referenceLines": [{"axis": "y", "value": 1, "label": "sideband parity", "lineStyle": "dashed"}],
            "layout": "full",
        },
        {
            "id": "direction-profile-chart",
            "title": "Resolved validation detector-share cycle on local spin ARA",
            "subtitle": "Fitted directional cosine projection; 13 independent 300 K validation runs per RF identity",
            "showDescription": True,
            "type": "line",
            "intent": "trend",
            "dataset": "validation_direction_profile",
            "sourceId": "t414-direction-profile",
            "encodings": {
                "x": {"field": "x_spin", "type": "quantitative", "label": "Local spin child ARA"},
                "y": {"field": "direction_projection", "type": "quantitative", "label": "Detector-share projection"},
                "color": {"field": "period", "type": "nominal", "label": "RF identity"},
                "tooltip": [
                    {"field": "x_spin", "type": "quantitative"},
                    {"field": "period", "type": "nominal"},
                    {"field": "direction_projection", "type": "quantitative"},
                    {"field": "se", "type": "quantitative"},
                ],
            },
            "xAxisTitle": "Local spin child ARA (0–2)",
            "yAxisTitle": "Detector-share directional projection",
            "referenceLines": [{"axis": "x", "value": 1, "label": "child ridge", "lineStyle": "dotted"}],
            "layout": "full",
        },
        {
            "id": "release-profile-chart",
            "title": "Detector-summed release residual across spin phase",
            "subtitle": "Noise-scaled residual after the 2.203 µs parent envelope; no stable common handover phase appears",
            "showDescription": True,
            "type": "line",
            "intent": "trend",
            "dataset": "release_profile",
            "sourceId": "t414-release-profile",
            "encodings": {
                "x": {"field": "x_spin", "type": "quantitative", "label": "Local spin child ARA"},
                "y": {"field": "release_residual", "type": "quantitative", "label": "Total release residual"},
                "color": {"field": "series", "type": "nominal", "label": "Split and RF identity"},
                "tooltip": [
                    {"field": "x_spin", "type": "quantitative"},
                    {"field": "series", "type": "nominal"},
                    {"field": "release_residual", "type": "quantitative"},
                    {"field": "se", "type": "quantitative"},
                ],
            },
            "xAxisTitle": "Local spin child ARA (0–2)",
            "yAxisTitle": "Noise-scaled total release residual",
            "referenceLines": [
                {"axis": "x", "value": 1, "label": "child ridge", "lineStyle": "dotted"},
                {"axis": "y", "value": 0, "label": "parent envelope", "lineStyle": "dashed"},
            ],
            "layout": "full",
        },
        {
            "id": "coordinate-path-chart",
            "title": "Spin child cycles nested inside the parent release coordinate",
            "subtitle": "Fixed 284 G validation example; wrapped angular position, not a diameter cut",
            "showDescription": True,
            "type": "line",
            "intent": "trend",
            "dataset": "coordinate_path",
            "sourceId": "t414-coordinate-path",
            "encodings": {
                "x": {"field": "time_us", "type": "quantitative", "label": "Corrected time", "unit": "us"},
                "y": {"fields": ["spin_child_ARA", "parent_release_ARA"], "type": "quantitative", "label": "ARA coordinate"},
                "tooltip": [
                    {"field": "time_us", "type": "quantitative", "unit": "us"},
                    {"field": "spin_child_ARA", "type": "quantitative"},
                    {"field": "parent_release_ARA", "type": "quantitative"},
                ],
            },
            "xAxisTitle": "Corrected time (µs)",
            "yAxisTitle": "ARA coordinate (0–2)",
            "referenceLines": [{"axis": "y", "value": 1, "label": "ridge", "lineStyle": "dotted"}],
            "layout": "full",
        },
        {
            "id": "spin-diameter-cut-a-chart",
            "title": "Spin diameter cut A against the parent release coordinate",
            "subtitle": "The same frozen 284 G spin phase projected through one diameter as 1 + sin(theta)",
            "showDescription": True,
            "type": "line",
            "intent": "trend",
            "dataset": "coordinate_path",
            "sourceId": "t414-coordinate-path",
            "encodings": {
                "x": {"field": "time_us", "type": "quantitative", "label": "Corrected time", "unit": "us"},
                "y": {"fields": ["spin_diameter_cut_A_ARA", "parent_release_ARA"], "type": "quantitative", "label": "ARA coordinate"},
                "tooltip": [
                    {"field": "time_us", "type": "quantitative", "unit": "us"},
                    {"field": "spin_diameter_cut_A_ARA", "type": "quantitative"},
                    {"field": "parent_release_ARA", "type": "quantitative"},
                ],
            },
            "xAxisTitle": "Corrected time (µs)",
            "yAxisTitle": "ARA coordinate (0–2)",
            "referenceLines": [{"axis": "y", "value": 1, "label": "ridge", "lineStyle": "dotted"}],
            "layout": "full",
        },
        {
            "id": "spin-diameter-cut-b-chart",
            "title": "Perpendicular spin diameter cut B against the parent",
            "subtitle": "The identical spin cycle rotated 90 degrees: 1 + cos(theta)",
            "showDescription": True,
            "type": "line",
            "intent": "trend",
            "dataset": "coordinate_path",
            "sourceId": "t414-coordinate-path",
            "encodings": {
                "x": {"field": "time_us", "type": "quantitative", "label": "Corrected time", "unit": "us"},
                "y": {"fields": ["spin_diameter_cut_B_ARA", "parent_release_ARA"], "type": "quantitative", "label": "ARA coordinate"},
                "tooltip": [
                    {"field": "time_us", "type": "quantitative", "unit": "us"},
                    {"field": "spin_diameter_cut_B_ARA", "type": "quantitative"},
                    {"field": "parent_release_ARA", "type": "quantitative"},
                ],
            },
            "xAxisTitle": "Corrected time (µs)",
            "yAxisTitle": "ARA coordinate (0–2)",
            "referenceLines": [{"axis": "y", "value": 1, "label": "ridge", "lineStyle": "dotted"}],
            "layout": "full",
        },
    ]

    tables = [
        {
            "id": "gate-table",
            "title": "Frozen interpretation gates",
            "subtitle": "Detector-share calibration and detector-total release are judged separately",
            "showDescription": True,
            "dataset": "gates",
            "sourceId": "t414-gates",
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
            "id": "detail-table",
            "title": "Split and RF-identity audit detail",
            "subtitle": "Run wins, broken controls, and phase coherence for every prespecified branch",
            "showDescription": True,
            "dataset": "summary_detail",
            "sourceId": "t414-summary-detail",
            "defaultSort": {"field": "group", "direction": "asc"},
            "density": "dense",
            "layout": "full",
            "columns": [
                {"field": "group", "label": "Split", "type": "text"},
                {"field": "period", "label": "RF identity", "type": "text"},
                {"field": "run_count", "label": "Runs", "format": "number"},
                {"field": "spin_ratio", "label": "Spin ratio", "format": "number"},
                {"field": "spin_run_wins", "label": "Spin run wins", "format": "percent"},
                {"field": "release_ratio", "label": "Release ratio", "format": "number"},
                {"field": "release_run_wins", "label": "Release run wins", "format": "percent"},
                {"field": "release_phase_resultant", "label": "Release phase coherence", "format": "number"},
            ],
        },
    ]

    cards = [
        {
            "id": "runs-card",
            "description": "Public runs and separately analysed RF periods.",
            "dataset": "headline",
            "sourceId": "t414-headline",
            "metrics": [
                {"label": "Public runs", "field": "runs", "format": "number"},
                {"label": "Run-periods", "field": "run_periods", "format": "number"},
            ],
        },
        {
            "id": "parent-card",
            "description": "Development-only calibration of the lifespan parent.",
            "dataset": "headline",
            "sourceId": "t414-headline",
            "metrics": [{"label": "Parent lifetime", "field": "tau_dev_us", "format": "number", "unit": "µs"}],
        },
        {
            "id": "child-card",
            "description": "Development-only field-to-spin calibration.",
            "dataset": "headline",
            "sourceId": "t414-headline",
            "metrics": [{"label": "Spin slope", "field": "gamma_dev_MHz_per_G", "format": "number", "unit": "MHz/G"}],
        },
        {
            "id": "validation-card",
            "description": "Validation target-frequency signal relative to wrong-frequency controls.",
            "dataset": "headline",
            "sourceId": "t414-headline",
            "metrics": [
                {"label": "Spin ratio · RF on", "field": "validation_spin_ratio_on", "format": "number"},
                {"label": "Spin ratio · RF off", "field": "validation_spin_ratio_off", "format": "number"},
            ],
        },
    ]

    generated = datetime.now(timezone.utc).isoformat()
    blocks = [
        {"id": "title", "type": "markdown", "body": f"# {TITLE}"},
        {
            "id": "summary",
            "type": "markdown",
            "sourceId": "t414-frozen-analysis",
            "body": (
                "## Technical summary\n\n"
                "**Actual spin cycles are recoverable as child structure inside the muon lifespan parent at resolved sampling, but this test does not support spin-phase locking of total release.** In 13 sealed validation runs, both RF identities recovered the frozen field-scaled child frequency in all runs, with median target/sideband ratios of **2.414** and **2.449**. The detector-summed release channel failed its control and phase-reproduction gates.\n\n"
                "The 202 K high-field holdout did not transfer the spin calibration. Its primary runs contain only about **2.25 native samples per cycle**, versus about **16.24** in validation. Accordingly, that branch is a failed transfer through an under-resolved measurement cut, not evidence that the resolved validation cycles were false."
            ),
        },
        {"id": "metrics", "type": "metric-strip", "cardIds": ["runs-card", "parent-card", "child-card", "validation-card"]},
        {
            "id": "finding-child",
            "type": "markdown",
            "sourceId": "t414-frozen-analysis",
            "body": (
                "## The spin child is visible when the archive resolves it\n\n"
                "The child frequency was learned only from development detector shares, then frozen as `f = 0.013549 × field`. Validation used new fields without retuning. RF-on and RF-off each beat the wrong-frequency median on **13 of 13 runs**, and intact detector/time order beat the broken controls on most runs. This supports the narrow ARA statement that repeated spin-child cycles ride inside the slower lifespan parent."
            ),
        },
        {"id": "ratio-chart-block", "type": "chart", "chartId": "ratio-chart", "layout": "full"},
        {
            "id": "ratio-chart-note",
            "type": "markdown",
            "body": "The grouped bars keep the two identities separate. The strong validation bars belong to detector-share redistribution; the much weaker and inconsistent release bars belong to detector-summed counts. A value above one alone is insufficient—the run-win and broken-order gates must also pass.",
        },
        {"id": "direction-chart-block", "type": "chart", "chartId": "direction-profile-chart", "layout": "full"},
        {
            "id": "direction-chart-note",
            "type": "markdown",
            "body": "This phase-folded profile is a fitted calibration view, not an additional prediction. Its role is visual: the 0–2 child coordinate closes repeatedly while the parent envelope changes far more slowly.",
        },
        {
            "id": "finding-release",
            "type": "markdown",
            "sourceId": "t414-frozen-analysis",
            "body": (
                "## Total release does not select one stable spin handover phase\n\n"
                "In validation, release target/sideband ratios were only **1.082** and **1.049**, just **7 of 13** runs beat sidebands in each RF identity, and the preferred phase differed by **0.466 ARA**. RF-on also lost its temporal broken-order comparison. The high-field RF-on ratio of 2.021 cannot rescue the claim because RF-off fell to 0.676, phase coherence remained weak, and the spin child itself was unresolved in that branch."
            ),
        },
        {"id": "release-chart-block", "type": "chart", "chartId": "release-profile-chart", "layout": "full"},
        {
            "id": "release-chart-note",
            "type": "markdown",
            "body": "If total release were locked to one child phase, the detector-summed curves would reproduce a stable peak or trough across new runs and RF identities. They do not. The residual shapes move with branch and sampling instead of closing at one repeatable ARA landmark.",
        },
        {
            "id": "finding-resolution",
            "type": "markdown",
            "sourceId": "t414-frozen-analysis",
            "body": (
                "## The high-field failure follows the measurement scale\n\n"
                "The post-hoc correlation between samples per cycle and log spin target/sideband ratio is **0.809**. Development and validation have median sampling of about 17.34 and 16.24 points per cycle; primary holdout has only 2.25. Five still-higher runs cross Nyquist and were kept as alias sensitivity. This diagnostic was not a rescue gate, but it explains why the high-field transfer is not an equally powered replication."
            ),
        },
        {"id": "resolution-chart-block", "type": "chart", "chartId": "resolution-chart", "layout": "full"},
        {
            "id": "resolution-chart-note",
            "type": "markdown",
            "body": "The x-axis is literal archive resolution, not an ARA score. The cluster near two samples per cycle is where the directional child signal collapses toward sideband parity, so no downstream release interpretation should be built on that branch.",
        },
        {
            "id": "scope",
            "type": "markdown",
            "sourceId": "isis-rb1620447",
            "body": (
                "## Scope and coordinate definitions\n\n"
                "Each run contains 96 RF-on and 96 RF-off detector histograms. Detector shares form the directional child channel; detector totals form the release channel. The child coordinate is `x_s = 2 frac(f t)`. The parent release coordinate is `x_p = 2(1-exp(-t/τ))`, with development-only `τ = 2.203 µs`. Both use 0–2 ARA, but they are different tiers and measurements."
            ),
        },
        {"id": "coordinate-chart-block", "type": "chart", "chartId": "coordinate-path-chart", "layout": "full"},
        {
            "id": "coordinate-chart-note",
            "type": "markdown",
            "body": "At 284 G, each sawtooth is the wrapped angular address of one complete local child cycle. It is useful for counting cycles, but it is not a physical diameter cut through the spin circle. Many such cycles occur while the parent release moves once from its early pole toward 2.",
        },
        {
            "id": "perpendicular-cuts-heading",
            "type": "markdown",
            "body": "## Rotating the spin cut by 90 degrees\n\nThe next two panels do not refit the spin or alter the parent. They project the frozen child phase onto two orthogonal diameters of its circle: `1 + sin(theta)` and `1 + cos(theta)`. Their ridge is 1 and their poles remain 0 and 2. This directly tests whether the original angular view was hiding a more parent-aligned diameter.",
        },
        {"id": "spin-cut-a-block", "type": "chart", "chartId": "spin-diameter-cut-a-chart", "layout": "full"},
        {"id": "spin-cut-b-block", "type": "chart", "chartId": "spin-diameter-cut-b-chart", "layout": "full"},
        {
            "id": "perpendicular-cuts-note",
            "type": "markdown",
            "body": "Across the complete 0.25–6 µs interval, neither diameter becomes the slowly increasing parent envelope: the correlations with the parent are approximately −0.033 for cut A and −0.005 for perpendicular cut B. Cut B is marginally closer by mean absolute distance (0.750 versus 0.762 ARA), but that small descriptive difference is not evidence of coupling. The geometric result is that the child repeatedly traverses both perpendicular diameters while the parent progresses once.",
        },
        {
            "id": "methods",
            "type": "markdown",
            "sourceId": "t414-frozen-analysis",
            "body": (
                "## Frozen design and independent validation\n\n"
                "The 13 development runs fixed the spin slope and parent lifetime. Protocol, code, manifest, development output, and validation output were hashed before the next stage. Validation and holdout used identical calculations. Wrong-frequency sidebands, independently scrambled detector labels, eight-bin temporal block permutations, RF identity separation, and a Nyquist boundary were frozen in advance. The independent validator reproduced all 92 run-period rows, aggregate gates, source hashes, ARA bounds, and exact detector-total invariance under label permutation."
            ),
        },
        {"id": "gate-table-block", "type": "table", "tableId": "gate-table", "layout": "full"},
        {
            "id": "limitations",
            "type": "markdown",
            "body": (
                "## What the result does not establish\n\n"
                "This archive contains population histograms, not event IDs for individual muons and not direct neutrino detections. Detector angles and grouping are present in the file structure but zeroed, so orientation is relative rather than an absolute spatial axis. Detector sums separate redistribution from total recorded counts exactly, but incomplete angular acceptance could still couple direction into the observed total. Finally, the high-field branch changes temperature and operates close to the instrument sampling limit."
            ),
        },
        {
            "id": "next-steps",
            "type": "markdown",
            "body": (
                "## Recommended next test\n\n"
                "Repeat the same frozen share-versus-total cut on event-mode or lower-field data with detector geometry and at least 8–12 samples per spin cycle throughout the holdout. Preserve a genuinely new field/temperature branch. That would test whether release phase-locking is absent, rather than merely unresolvable, and would allow absolute spin orientation to replace the current relative detector mode."
            ),
        },
        {"id": "detail-heading", "type": "markdown", "body": "## Audit detail\n\nThe table keeps every prespecified split and RF identity visible, including failed controls and the five aliased sensitivity runs."},
        {"id": "detail-table-block", "type": "table", "tableId": "detail-table", "layout": "full"},
        {
            "id": "questions",
            "type": "markdown",
            "body": (
                "## Further questions\n\n"
                "- Does an event-mode detector with absolute angles reproduce the validation child phase?\n\n"
                "- Does total release remain phase-independent when spin cycles are resolved in a wholly new temperature branch?\n\n"
                "- Is the RF-on/RF-off phase difference physical, or an acceptance and drive-state effect?"
            ),
        },
    ]

    manifest = {
        "version": 1,
        "surface": "report",
        "title": TITLE,
        "description": "Frozen ARA test separating spin-child detector redistribution from the muon lifespan/release parent.",
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
            "datasets": {
                "headline": headline,
                "summary_ratios": summary_ratios,
                "summary_detail": summary_detail,
                "resolution": resolution,
                "validation_direction_profile": validation_direction_profile,
                "release_profile": release_profile,
                "coordinate_path": coordinate_path,
                "gates": gates,
            },
        },
        "sources": sources,
    }
    OUTPUT.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()

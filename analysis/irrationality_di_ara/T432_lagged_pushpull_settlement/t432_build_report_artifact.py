from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

import pandas as pd


ROOT = pathlib.Path(__file__).resolve().parent
RESULTS = ROOT / "results"
OUTPUT = RESULTS / "T432_TECHNICAL_REPORT_ARTIFACT.json"


def records(frame: pd.DataFrame) -> list[dict[str, object]]:
    return json.loads(frame.to_json(orient="records"))


events = pd.read_csv(RESULTS / "T432_CONFIRMATION_EVENTS.csv")
histories = pd.read_csv(RESULTS / "T432_CONFIRMATION_HISTORIES.csv").sort_values(["event", "time_s"])
controls = pd.read_csv(RESULTS / "T432_CONFIRMATION_OFFSOURCE_CONTROLS.csv")
validation = json.loads((RESULTS / "T432_INDEPENDENT_VALIDATION.json").read_text(encoding="utf-8"))

generated_at = datetime.now(timezone.utc).isoformat()
title = "T432 — Lagged Push/Pull and Settlement in Untouched Merger Strain"

event_summary = pd.DataFrame({
    "event": events.event,
    "best_lag_ms": events.best_lag_ms.round(1),
    "opposition_rho": events.opposition_rho.round(4),
    "opposition_occupancy_pct": (100 * events.opposition_occupancy).round(1),
    "pushpull_percentile_pct": (100 * events.pushpull_percentile).round(1),
    "speed_settlement_percentile_pct": (100 * events.speed_settlement_percentile).round(1),
    "radius_settlement_percentile_pct": (100 * events.radius_settlement_percentile).round(1),
    "H1_pushpull_percentile_pct": (100 * events.H1_pushpull_percentile).round(1),
    "L1_pushpull_percentile_pct": (100 * events.L1_pushpull_percentile).round(1),
    "dynamic_p95": events.dynamic_p95.astype(bool),
    "joint_settlement_p90": events.settlement_joint_p90.astype(bool),
    "detector_replication": events.detector_replication.astype(bool),
})

metric_labels = {
    "pushpull_percentile": "Lagged push/pull",
    "speed_settlement_percentile": "Speed settlement",
    "radius_settlement_percentile": "Radius settlement",
    "corner_avoidance_percentile": "Top-left avoidance",
}
percentiles_long = []
for _, row in events.iterrows():
    for field, label in metric_labels.items():
        percentiles_long.append({
            "event": row.event,
            "metric": label,
            "percentile_pct": round(100 * float(row[field]), 1),
            "best_lag_ms": round(float(row.best_lag_ms), 1),
            "opposition_rho": round(float(row.opposition_rho), 4),
            "opposition_occupancy_pct": round(100 * float(row.opposition_occupancy), 1),
        })

trajectory = histories[[
    "event", "time_s", "movement_M", "connection_C", "unresolved_H",
    "trajectory_speed", "radius_to_late_centroid",
]].copy()
trajectory["time_s"] = trajectory.time_s.round(4)
for field in ["movement_M", "connection_C", "unresolved_H", "trajectory_speed", "radius_to_late_centroid"]:
    trajectory[field] = trajectory[field].round(4)

strongest_event = str(events.sort_values("pushpull_percentile", ascending=False).iloc[0].event)
strong = histories.loc[histories.event == strongest_event, ["time_s", "connection_C", "movement_M", "unresolved_H"]]
history_long = []
for _, row in strong.iterrows():
    for field, label in [("connection_C", "Connection C"), ("movement_M", "Movement M"), ("unresolved_H", "Unresolved H")]:
        history_long.append({
            "event": strongest_event,
            "time_s": round(float(row.time_s), 4),
            "component": label,
            "ara_coordinate": round(float(row[field]), 4),
        })

gate_summary = [
    {"order": 1, "gate": "Dynamic source specificity", "required": "4 of 6 at P95", "observed": "2 of 6", "passed": False},
    {"order": 2, "gate": "Joint speed/radius settlement", "required": "4 of 6 at P90", "observed": "0 of 6", "passed": False},
    {"order": 3, "gate": "Independent H1/L1 replication", "required": "3 of 6 at P90", "observed": "0 of 6", "passed": False},
    {"order": 4, "gate": "Top-left avoidance", "required": "4 of 6 at P90", "observed": "0 of 6; all ties", "passed": False},
]

headline = [{
    "dynamic_rate": 2 / 6,
    "settlement_rate": 0.0,
    "detector_replication_rate": 0.0,
    "validation_rate": 1.0,
}]

reviewed_source_sample = records(histories.head(10)[[
    "event", "time_s", "connection_C", "movement_M", "unresolved_H", "dC_dt", "dM_dt",
]])

events_path = RESULTS / "T432_CONFIRMATION_EVENTS.csv"
histories_path = RESULTS / "T432_CONFIRMATION_HISTORIES.csv"
controls_path = RESULTS / "T432_CONFIRMATION_OFFSOURCE_CONTROLS.csv"
qa_path = RESULTS / "T432_CONFIRMATION_SOURCE_QA.csv"

sources = [
    {
        "id": "t432_events",
        "label": "T432 untouched confirmation event metrics",
        "path": str(events_path),
        "query": {
            "engine": "duckdb",
            "language": "sql",
            "sql": f"SELECT * FROM read_csv_auto('{events_path.as_posix()}') ORDER BY event",
            "description": "Loads the six untouched confirmation-event metric rows.",
            "tables_used": [events_path.as_posix()],
            "filters": ["event window -0.50 to +0.75 s", "six frozen O3a confirmation events"],
            "metric_definitions": [
                "push/pull score = max(0, -Spearman(dC(t), dM(t+lag))) multiplied by opposing-derivative occupancy; lag optimized identically over -64 to +64 ms for event and controls",
                "percentile = within-file empirical rank versus 53 identical off-source windows",
                "settlement compares active -0.15 to +0.15 s with late +0.35 to +0.75 s",
            ],
        },
    },
    {
        "id": "t432_histories",
        "label": "T432 time-resolved ARA histories",
        "path": str(histories_path),
        "query": {
            "engine": "duckdb",
            "language": "sql",
            "sql": f"SELECT * FROM read_csv_auto('{histories_path.as_posix()}') ORDER BY event, time_s",
            "description": "Loads all time-resolved connection, movement, residual and derivative histories.",
            "tables_used": [histories_path.as_posix()],
            "filters": ["-0.50 <= time_s <= +0.75"],
        },
    },
    {
        "id": "t432_controls",
        "label": "T432 matched off-source controls",
        "path": str(controls_path),
        "query": {
            "engine": "duckdb",
            "language": "sql",
            "sql": f"SELECT * FROM read_csv_auto('{controls_path.as_posix()}') ORDER BY event, control_id",
            "description": "Loads 53 identical off-source control windows per event.",
            "tables_used": [controls_path.as_posix()],
        },
    },
    {
        "id": "t432_qa",
        "label": "T432 source quality audit",
        "path": str(qa_path),
        "query": {
            "engine": "duckdb",
            "language": "sql",
            "sql": f"SELECT * FROM read_csv_auto('{qa_path.as_posix()}') ORDER BY event, detector",
            "description": "Loads detector sampling, duration, finite-value and public data-quality checks.",
            "tables_used": [qa_path.as_posix()],
        },
    },
    {
        "id": "t432_protocol",
        "label": "Frozen T432 protocol",
        "path": str(ROOT / "T432_FROZEN_PROTOCOL.md"),
    },
    {
        "id": "t432_gates",
        "label": "Frozen T432 gate outcomes",
        "path": str(RESULTS / "T432_CONFIRMATION_GATES.json"),
        "query": {
            "engine": "duckdb",
            "language": "sql",
            "sql": "SELECT * FROM (VALUES (1, 'Dynamic source specificity', '4 of 6 at P95', '2 of 6', false), (2, 'Joint speed/radius settlement', '4 of 6 at P90', '0 of 6', false), (3, 'Independent H1/L1 replication', '3 of 6 at P90', '0 of 6', false), (4, 'Top-left avoidance', '4 of 6 at P90', '0 of 6; all ties', false)) AS gates(order_id, gate, required, observed, passed) ORDER BY order_id",
            "description": "Reconstructs the four predeclared frozen confirmation-gate outcomes.",
            "tables_used": [str(RESULTS / "T432_CONFIRMATION_GATES.json")],
        },
    },
    {
        "id": "gwosc",
        "label": "Gravitational Wave Open Science Center",
        "href": "https://gwosc.org/api/",
    },
]

manifest = {
    "version": 1,
    "surface": "report",
    "title": title,
    "description": "Frozen ARA test of lagged movement/connection opposition and post-event settlement in six untouched public merger-strain events.",
    "generatedAt": generated_at,
    "cards": [
        {
            "id": "headline_metrics",
            "dataset": "headline",
            "sourceId": "t432_events",
            "description": "Frozen confirmation-gate rates across six untouched events.",
            "metrics": [
                {"label": "Source-specific push/pull", "field": "dynamic_rate", "format": "percent"},
                {"label": "Joint settlement", "field": "settlement_rate", "format": "percent"},
                {"label": "H1/L1 replication", "field": "detector_replication_rate", "format": "percent"},
                {"label": "Validation checks", "field": "validation_rate", "format": "percent"},
            ],
        }
    ],
    "charts": [
        {
            "id": "event_percentiles",
            "title": "Frozen component percentiles against matched off-source windows",
            "type": "bar",
            "dataset": "percentiles_long",
            "sourceId": "t432_events",
            "encodings": {
                "x": {"field": "event", "type": "nominal"},
                "y": {"field": "percentile_pct", "type": "quantitative"},
                "color": {"field": "metric", "type": "nominal"},
            },
            "options": {"orientation": "vertical", "grouping": "grouped"},
        },
        {
            "id": "ara_plane",
            "title": "Fixed movement-by-connection ARA trajectories",
            "type": "scatter",
            "dataset": "trajectory",
            "sourceId": "t432_histories",
            "encodings": {
                "x": {"field": "movement_M", "type": "quantitative"},
                "y": {"field": "connection_C", "type": "quantitative"},
                "color": {"field": "event", "type": "nominal"},
            },
        },
        {
            "id": "strongest_history",
            "title": f"{strongest_event} ARA component histories",
            "type": "line",
            "dataset": "history_long",
            "sourceId": "t432_histories",
            "encodings": {
                "x": {"field": "time_s", "type": "quantitative"},
                "y": {"field": "ara_coordinate", "type": "quantitative"},
                "color": {"field": "component", "type": "nominal"},
            },
        },
    ],
    "tables": [
        {
            "id": "event_table",
            "title": "Untouched confirmation events",
            "dataset": "event_summary",
            "sourceId": "t432_events",
            "columns": [
                {"field": "event", "label": "Event"},
                {"field": "best_lag_ms", "label": "Best lag", "format": "number", "unit": "ms"},
                {"field": "opposition_rho", "label": "Opposition rho", "format": "number"},
                {"field": "opposition_occupancy_pct", "label": "Opposing steps", "format": "number", "unit": "%"},
                {"field": "pushpull_percentile_pct", "label": "Push/pull pct", "format": "number", "unit": "%"},
                {"field": "speed_settlement_percentile_pct", "label": "Speed settle pct", "format": "number", "unit": "%"},
                {"field": "radius_settlement_percentile_pct", "label": "Radius settle pct", "format": "number", "unit": "%"},
                {"field": "dynamic_p95", "label": "Dynamic P95"},
                {"field": "joint_settlement_p90", "label": "Joint settle P90"},
            ],
            "defaultSort": {"field": "pushpull_percentile_pct", "direction": "desc"},
        },
        {
            "id": "gate_table",
            "title": "Frozen gate outcomes",
            "dataset": "gate_summary",
            "sourceId": "t432_gates",
            "columns": [
                {"field": "order", "label": "#", "format": "number"},
                {"field": "gate", "label": "Gate"},
                {"field": "required", "label": "Required"},
                {"field": "observed", "label": "Observed"},
                {"field": "passed", "label": "Pass"},
            ],
            "defaultSort": {"field": "order", "direction": "asc"},
        },
        {
            "id": "source_sample_table",
            "title": "First ten deterministic history rows",
            "dataset": "reviewed_source_sample",
            "sourceId": "t432_histories",
            "columns": [
                {"field": "event", "label": "Event"},
                {"field": "time_s", "label": "Time", "format": "number", "unit": "s"},
                {"field": "connection_C", "label": "Connection C", "format": "number"},
                {"field": "movement_M", "label": "Movement M", "format": "number"},
                {"field": "unresolved_H", "label": "Residual H", "format": "number"},
                {"field": "dC_dt", "label": "dC/dt", "format": "number"},
                {"field": "dM_dt", "label": "dM/dt", "format": "number"},
            ],
            "defaultSort": {"field": "time_s", "direction": "asc"},
        },
    ],
    "sources": sources,
    "blocks": [
        {"id": "title", "type": "markdown", "body": f"# {title}"},
        {"id": "technical_summary", "type": "markdown", "sourceId": "t432_events", "body": "## Technical summary\n\n**Frozen verdict: NOT SUPPORTED as a universal rule.** Two of six untouched mergers exceeded the 95th matched off-source percentile for lagged push/pull, below the required four. No event jointly passed speed and radius settlement, and no event reproduced the P90 push/pull threshold in both H1 and L1. The ARA plane remains a useful trajectory description, but this absolute-time instrument does not establish a universal merger handover or closing-and-settling law."},
        {"id": "headline", "type": "metric-strip", "cardIds": ["headline_metrics"]},
        {"id": "percentiles_block", "type": "chart", "chartId": "event_percentiles"},
        {"id": "event_table_block", "type": "table", "tableId": "event_table"},
        {"id": "ara_result", "type": "markdown", "sourceId": "t432_events", "body": "## Two mergers carry a source-specific delayed opposition lead\n\n`GW190519_153544` reached the 100th control percentile and `GW190517_055101` reached 96.2%. Their opposition correlations were -0.381 and -0.311, with 46.1% and 41.3% of aligned derivative steps moving in opposite directions. Both selected lags lie close to the +64 ms search boundary, so the frozen result is valid but its physical interpretation requires a new lag-stability test."},
        {"id": "ara_plane_block", "type": "chart", "chartId": "ara_plane"},
        {"id": "history_block", "type": "chart", "chartId": "strongest_history"},
        {"id": "what_data_are", "type": "markdown", "sourceId": "t432_qa", "body": "## What the data are—and are not\n\nThe inputs are public, calibrated 4 kHz H1/L1 detector strain: astrophysical response plus detector noise and artifacts. They are not images of horizons, orbital separation, gravitational force or local spacetime density. `C` is the off-source-ranked mean of spectral amount, spectral concentration and inter-detector phase coherence. `M` is off-source-ranked spectral redistribution. `H=max(0,2-C-M)` is a projection residual, not hidden energy. H1 and L1 are independent views of one event, not the two black holes."},
        {"id": "methodology", "type": "markdown", "sourceId": "t432_protocol", "body": "## Frozen methodology\n\nThe lens remained unchanged from T431: off-source whitening, 30–512 Hz bandpass, 64 ms Hann time-frequency windows stepped every 4 ms, seven-frame smoothing and empirical-CDF projection to 0–2. The event path spans -0.50 to +0.75 s; active and late intervals are -0.15 to +0.15 s and +0.35 to +0.75 s. The lag search covers -64 to +64 ms and is identically maximized in every source and control window. Each event has 53 matched within-file off-source controls."},
        {"id": "gate_table_block", "type": "table", "tableId": "gate_table"},
        {"id": "empty_corner", "type": "markdown", "sourceId": "t432_events", "body": "## The empty top-left box is a boundary tie, not source evidence\n\nThe nominal `M<=0.5, C>=1.5` region was empty in every merger window and every off-source control. Every event therefore received the neutral tied percentile 0.5. The visible boundary is real in the constructed coordinate plane, but this exact occupancy test cannot tell merger signal from ordinary off-source strain."},
        {"id": "validation", "type": "markdown", "body": "## Validation and data quality\n\nAll 12 detector files contain 32 seconds at 4096 Hz, have finite fraction 1.0, zero fraction 0.0 and pass the public data-quality bits checked at the event. File hashes, freeze hashes, event separation, 53-control counts, metric percentiles, coordinates and all gate outcomes were independently recomputed. Every validation check passed."},
        {"id": "source_sample_block", "type": "table", "tableId": "source_sample_table"},
        {"id": "limits", "type": "markdown", "body": "## Limits\n\nThe 64 ms window smears shorter structure; a 4 ms hop is not 4 ms independent resolution. The fixed absolute time crop does not normalize for source mass or merger/ringdown duration. Inter-detector coherence is a processed detector relation, not direct internal merger phase. Off-source controls establish within-file specificity only. They cannot by themselves prove a universal physical mechanism."},
        {"id": "next", "type": "markdown", "body": "## Recommended next test\n\nTreat all 20 opened events as development only. Freeze a timescale-normalized lag-stability instrument that (1) widens the allowed lag range to determine whether the two peaks are interior or boundary-seeking, and (2) aligns each event by an independently estimated chirp/ringdown duration rather than absolute seconds. Test the frozen instrument on another untouched event set. This preserves the ARA identity and axes while directly addressing the two dominant measurement limits."},
        {"id": "questions", "type": "markdown", "body": "## Further questions\n\n- Do the two high-percentile events share a source timescale, mass range or detector geometry that explains the 60–64 ms relation?\n- Does the lagged opposition remain after timescale normalization?\n- Is a continuous distance-to-boundary measure more informative than the tied top-left box?\n- Which independent observable can anchor connection or movement without being built from the same strain spectrum?"},
    ],
}

snapshot = {
    "version": 1,
    "generatedAt": generated_at,
    "status": "ready",
    "datasets": {
        "headline": headline,
        "event_summary": records(event_summary),
        "percentiles_long": percentiles_long,
        "trajectory": records(trajectory),
        "history_long": history_long,
        "gate_summary": gate_summary,
        "reviewed_source_sample": reviewed_source_sample,
    },
}

artifact = {"surface": "report", "manifest": manifest, "snapshot": snapshot, "sources": sources}
OUTPUT.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
print(OUTPUT)
print({key: len(value) for key, value in snapshot["datasets"].items()})
print({"validation_status": validation["status"], "control_rows": len(controls)})

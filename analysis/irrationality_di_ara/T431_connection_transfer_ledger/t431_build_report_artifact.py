"""Build the bounded Data Analytics technical-report artifact for T431."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import quantiles


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
OUTPUT = RESULTS / "T431_TECHNICAL_REPORT_ARTIFACT.json"


def read_csv(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def as_bool(value: str) -> bool:
    return value.strip().lower() == "true"


events_raw = read_csv("T431_CONFIRMATION_EVENTS.csv")
controls_raw = read_csv("T431_CONFIRMATION_CONTROLS.csv")
histories_raw = read_csv("T431_CONFIRMATION_HISTORIES.csv")

controls_by_event: dict[str, list[float]] = {}
for row in controls_raw:
    controls_by_event.setdefault(row["event"], []).append(as_float(row, "ledger_strength"))

event_summary: list[dict[str, object]] = []
event_control: list[dict[str, object]] = []
for row in events_raw:
    event = row["event"]
    control_values = sorted(controls_by_event[event])
    p95 = quantiles(control_values, n=20, method="inclusive")[18]
    event_value = as_float(row, "ledger_strength")
    percentile = 100.0 * as_float(row, "ledger_offsource_percentile")
    event_summary.append(
        {
            "event": event,
            "connection_break": round(as_float(row, "connection_break_depth"), 4),
            "movement_excursion": round(as_float(row, "movement_excursion"), 4),
            "ledger_strength": round(event_value, 4),
            "offsource_p95": round(p95, 4),
            "offsource_percentile_pct": round(percentile, 2),
            "empirical_p": round(as_float(row, "ledger_empirical_p"), 4),
            "phase_coherence_percentile_pct": round(
                100.0 * as_float(row, "phase_coherence_offsource_percentile"), 2
            ),
            "unresolved_mobile_excess": round(as_float(row, "unresolved_mobile_excess"), 4),
            "network_shape": as_bool(row["network_shape_pass"]),
            "detector_replication": as_bool(row["detector_replication_pass"]),
        }
    )
    event_control.extend(
        [
            {"event": event, "series": "Event ledger", "value": round(event_value, 4)},
            {"event": event, "series": "Off-source 95th percentile", "value": round(p95, 4)},
        ]
    )

gate_summary = [
    {"order": 1, "gate": "Network transfer shape", "required": "3 of 4", "observed": "3 of 4", "passed": True},
    {"order": 2, "gate": "Above matched off-source 95th percentile", "required": "3 of 4", "observed": "0 of 4", "passed": False},
    {"order": 3, "gate": "Full H1/L1 component replication", "required": "2 of 4", "observed": "1 of 4", "passed": False},
    {"order": 4, "gate": "Positive unresolved mobile excess", "required": "3 of 4", "observed": "2 of 4", "passed": False},
    {"order": 5, "gate": "Phase coherence at or above off-source P90", "required": "3 of 4", "observed": "2 of 4", "passed": False},
]

headline = [
    {
        "shape_rate": 0.75,
        "source_specific_rate": 0.0,
        "detector_replication_rate": 0.25,
        "strongest_percentile": max(r["offsource_percentile_pct"] for r in event_summary) / 100.0,
    }
]

strongest_event = max(event_summary, key=lambda row: row["offsource_percentile_pct"])["event"]
history_long: list[dict[str, object]] = []
ara_plane: list[dict[str, object]] = []
for row in histories_raw:
    event = row["event"]
    time_s = round(as_float(row, "time_s"), 6)
    connection = round(as_float(row, "connection_C"), 4)
    movement = round(as_float(row, "movement_M"), 4)
    if event == strongest_event:
        for component, field in (
            ("Connection C", "connection_C"),
            ("Movement M", "movement_M"),
            ("Unresolved H", "unresolved_H"),
        ):
            history_long.append(
                {
                    "time_s": time_s,
                    "component": component,
                    "ara_coordinate": round(as_float(row, field), 4),
                }
            )
    ara_plane.append(
        {
            "event": event,
            "time_s": time_s,
            "connection_C": connection,
            "movement_M": movement,
        }
    )

reviewed_source_sample = [
    {
        "event": row["event"],
        "time_s": round(as_float(row, "time_s"), 6),
        "connection_C": round(as_float(row, "connection_C"), 4),
        "movement_M": round(as_float(row, "movement_M"), 4),
        "unresolved_H": round(as_float(row, "unresolved_H"), 4),
        "phase_coherence_ARA": round(as_float(row, "phase_coherence_ARA"), 4),
    }
    for row in histories_raw[:10]
]

title = "T431 — Connection-transfer ledger in binary-black-hole strain"
generated_at = "2026-08-25T00:00:00+10:00"

sources = [
    {
        "id": "t431_events",
        "label": "T431 untouched confirmation event ledger",
        "path": str(RESULTS / "T431_CONFIRMATION_EVENTS.csv"),
        "query": {
            "engine": "duckdb",
            "sql": f"SELECT * FROM read_csv_auto('{(RESULTS / 'T431_CONFIRMATION_EVENTS.csv').as_posix()}')",
            "description": "Loads the four untouched confirmation-event ledger rows.",
            "metric_definitions": [
                "ledger_strength = connection_break_depth + movement_excursion",
                "ledger_offsource_percentile is the fraction of matched off-source ledgers below the event ledger",
            ],
        },
    },
    {
        "id": "t431_controls",
        "label": "T431 matched off-source controls",
        "path": str(RESULTS / "T431_CONFIRMATION_CONTROLS.csv"),
        "query": {
            "engine": "duckdb",
            "sql": f"SELECT * FROM read_csv_auto('{(RESULTS / 'T431_CONFIRMATION_CONTROLS.csv').as_posix()}')",
            "description": "Loads the 82 matched off-source control windows for each confirmation event.",
        },
    },
    {
        "id": "t431_histories",
        "label": "T431 time-resolved ARA histories",
        "path": str(RESULTS / "T431_CONFIRMATION_HISTORIES.csv"),
        "query": {
            "engine": "duckdb",
            "sql": f"SELECT * FROM read_csv_auto('{(RESULTS / 'T431_CONFIRMATION_HISTORIES.csv').as_posix()}')",
            "description": "Loads the time-resolved connection, movement, unresolved and coherence ARA histories.",
        },
    },
    {
        "id": "t431_protocol",
        "label": "Frozen T431 protocol",
        "path": str(ROOT / "T431_FROZEN_PROTOCOL.md"),
    },
    {
        "id": "t431_gate_summary",
        "label": "Frozen T431 gate outcomes",
        "path": str(RESULTS / "T431_CONFIRMATION_SUMMARY.json"),
        "query": {
            "engine": "duckdb",
            "sql": "SELECT * FROM (VALUES (1, 'Network transfer shape', '3 of 4', '3 of 4', true), (2, 'Above matched off-source 95th percentile', '3 of 4', '0 of 4', false), (3, 'Full H1/L1 component replication', '2 of 4', '1 of 4', false), (4, 'Positive unresolved mobile excess', '3 of 4', '2 of 4', false), (5, 'Phase coherence at or above off-source P90', '3 of 4', '2 of 4', false)) AS gates(order_id, gate, required, observed, passed)",
            "description": "Reconstructs the five predeclared frozen gate outcomes from the confirmation summary.",
        },
    },
    {
        "id": "gwosc",
        "label": "Gravitational Wave Open Science Center event strain",
        "href": "https://gwosc.org/api/",
    },
]

manifest = {
    "version": 1,
    "surface": "report",
    "title": title,
    "description": "Frozen ARA test of old connection to mobile/unresolved transfer to new connection in four untouched gravitational-wave events.",
    "generatedAt": generated_at,
    "cards": [
        {
            "id": "headline_metrics",
            "dataset": "headline",
            "sourceId": "t431_events",
            "metrics": [
                {"label": "ARA morphology", "field": "shape_rate", "format": "percent"},
                {"label": "Source-specific gate", "field": "source_specific_rate", "format": "percent"},
                {"label": "Detector replication", "field": "detector_replication_rate", "format": "percent"},
                {"label": "Strongest event percentile", "field": "strongest_percentile", "format": "percent"},
            ],
        }
    ],
    "charts": [
        {
            "id": "event_vs_control",
            "title": "Event ledger strength and matched off-source 95th percentile",
            "type": "bar",
            "dataset": "event_control",
            "sourceId": "t431_events",
            "encodings": {
                "x": {"field": "event", "type": "nominal"},
                "y": {"field": "value", "type": "quantitative"},
                "color": {"field": "series", "type": "nominal"},
            },
            "options": {"orientation": "vertical", "grouping": "grouped"},
        },
        {
            "id": "ara_plane",
            "title": "Confirmation ARA trajectories",
            "type": "scatter",
            "dataset": "ara_plane",
            "sourceId": "t431_histories",
            "encodings": {
                "x": {"field": "connection_C", "type": "quantitative"},
                "y": {"field": "movement_M", "type": "quantitative"},
                "color": {"field": "event", "type": "nominal"},
            },
        },
        {
            "id": "strongest_history",
            "title": f"{strongest_event} component histories",
            "type": "line",
            "dataset": "history_long",
            "sourceId": "t431_histories",
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
            "sourceId": "t431_events",
            "columns": [
                {"field": "event", "label": "Event"},
                {"field": "connection_break", "label": "Connection break", "format": "number"},
                {"field": "movement_excursion", "label": "Movement excursion", "format": "number"},
                {"field": "ledger_strength", "label": "Ledger strength", "format": "number"},
                {"field": "offsource_percentile_pct", "label": "Off-source percentile", "format": "number", "unit": "%"},
                {"field": "empirical_p", "label": "Empirical p", "format": "number"},
                {"field": "network_shape", "label": "Shape"},
                {"field": "detector_replication", "label": "H1/L1 replication"},
            ],
            "defaultSort": {"field": "offsource_percentile_pct", "direction": "desc"},
        },
        {
            "id": "gate_table",
            "title": "Frozen gate outcomes",
            "dataset": "gate_summary",
            "sourceId": "t431_gate_summary",
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
            "title": "Deterministic reviewed source sample",
            "dataset": "reviewed_source_sample",
            "sourceId": "t431_histories",
            "columns": [
                {"field": "event", "label": "Event"},
                {"field": "time_s", "label": "Time", "format": "number", "unit": "s"},
                {"field": "connection_C", "label": "Connection C", "format": "number"},
                {"field": "movement_M", "label": "Movement M", "format": "number"},
                {"field": "unresolved_H", "label": "Unresolved H", "format": "number"},
                {"field": "phase_coherence_ARA", "label": "Phase coherence", "format": "number"},
            ],
            "defaultSort": {"field": "time_s", "direction": "asc"},
        },
    ],
    "sources": sources,
    "blocks": [
        {
            "id": "title",
            "type": "markdown",
            "body": f"# {title}\n\nFrozen confirmation test of the proposed ARA transfer sequence `old connection → mobile/unresolved → new connection` in four previously unseen binary-black-hole strain events.",
        },
        {"id": "headline", "type": "metric-strip", "cardIds": ["headline_metrics"]},
        {
            "id": "technical_summary",
            "type": "markdown",
            "body": "## Technical summary\n\n**Frozen verdict: NOT SUPPORTED.** The qualitative ARA transfer shape occurred in 3 of 4 untouched events, so the morphology is real enough to keep investigating. But none of the four event ledgers exceeded its own matched off-source 95th percentile, only one replicated the full component direction in both H1 and L1, and the unresolved/coherence gates each passed in only two events. The strongest event, GW190828_063405, reached the 93.90th off-source percentile—close to, but below, the frozen threshold.",
        },
        {"id": "event_vs_control_block", "type": "chart", "chartId": "event_vs_control"},
        {"id": "event_table_block", "type": "table", "tableId": "event_table"},
        {
            "id": "ara_reading",
            "type": "markdown",
            "body": "## ARA reading\n\nAt this measurement scale, each gravitational-wave event is one parent identity and H1/L1 are independent views of it—not the two black holes. Connection is the mean of network amount, spectral concentration and detector phase coherence; movement is spectral redistribution. The tested relation was a connection-heavy state, followed by a movement-facing trough, followed by reclosure into a later connection-heavy state. Three events traced that order, but the same shape was common in matched off-source strain. ARA therefore recovered a useful path description here, not yet a merger-specific transfer law.",
        },
        {"id": "ara_plane_block", "type": "chart", "chartId": "ara_plane"},
        {"id": "strongest_history_block", "type": "chart", "chartId": "strongest_history"},
        {
            "id": "methodology",
            "type": "markdown",
            "body": "## Methodology\n\nThe test retained the earlier 30–512 Hz whitening and 64 ms time-frequency construction, mapped detector features independently onto 0–2 ARA coordinates using detector-specific off-source empirical distributions, and froze three non-overlapping temporal regions before opening the new events. The old landmark maximized connection before the merger, the mobile landmark maximized movement minus connection around the handover, and the new landmark maximized connection afterward. The ledger strength was `connection break + movement excursion`. Every event was compared against 82 identically measured off-source windows. Support required all five predeclared gates.",
        },
        {"id": "gate_table_block", "type": "table", "tableId": "gate_table"},
        {
            "id": "data_quality",
            "type": "markdown",
            "body": "## Data quality and validation\n\nThe four holdouts were absent from development, each used both H1 and L1 source files, the downloaded file hashes and event GPS values matched the frozen manifest, and all event/control counts and ledger arithmetic were independently recomputed. Source, protocol and analysis hashes were frozen before confirmation scoring. The validation audit passed every integrity check. The first ten deterministic history rows are included below for inspection.",
        },
        {"id": "source_sample_block", "type": "table", "tableId": "source_sample_table"},
        {
            "id": "physics_crosswalk",
            "type": "markdown",
            "body": "## Established-physics crosswalk\n\nThe connection trough and movement excursion correspond descriptively to rapid time-frequency redistribution during the merger and ringdown. This is only a crosswalk: the ARA coordinates were constructed from strain observables and do not identify literal spacetime bonds breaking or a liquid gravitational medium. The source-specific comparison is decisive because whitening noise and instrumental transients can generate similar local morphology away from the published merger time.",
        },
        {
            "id": "limitations",
            "type": "markdown",
            "body": "## Limitations\n\nThe sample contains four confirmation events, the tested connection coordinate combines three measured relations, and the three temporal regions are fixed population windows rather than identity-specific physical boundaries. The full two-detector component direction was inconsistent in three events. The morphology should therefore remain an unresolved ARA lead, not evidence that black-hole connections literally liquefy or that the transfer mechanism is universal.",
        },
        {
            "id": "next_steps",
            "type": "markdown",
            "body": "## Next test\n\nFreeze a follow-up around GW190828_063405's distinguishing relation without reusing its outcome as confirmation: derive a candidate feature on development events, then test it on a larger untouched O3 set. The most informative direction is not another morphology-only gate. It is an independent relation—such as detector-consistent phase evolution or a source-parameter-informed timescale—that must rise specifically at the mobile landmark while remaining absent from matched off-source windows.",
        },
        {
            "id": "questions",
            "type": "markdown",
            "body": "## Further questions\n\n- Why did GW190828_063405 approach the source-specific threshold while the other events did not?\n- Is the repeated ARA shape generated by a merger relation, by a common detector/noise process, or by the coordinate construction itself?\n- Does an independently measured phase or source-timescale relation identify the same mobile landmark without being built from connection and movement?\n- Does the geometry become cleaner when events are aligned by a physically estimated merger/ringdown scale rather than absolute seconds?",
        },
    ],
}

snapshot = {
    "version": 1,
    "generatedAt": generated_at,
    "status": "ready",
    "datasets": {
        "headline": headline,
        "event_summary": event_summary,
        "event_control": event_control,
        "gate_summary": gate_summary,
        "history_long": history_long,
        "ara_plane": ara_plane,
        "reviewed_source_sample": reviewed_source_sample,
    },
}

artifact = {"surface": "report", "manifest": manifest, "snapshot": snapshot, "sources": sources}
OUTPUT.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
print(OUTPUT)
print({key: len(value) for key, value in snapshot["datasets"].items()})

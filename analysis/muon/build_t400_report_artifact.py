#!/usr/bin/env python3
"""Build the canonical portable-report artifact for T400 from saved outputs."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T400_nested_child_window_population_to_event"
RESULTS = json.loads((OUT / "T400_RESULTS.json").read_text(encoding="utf-8"))
VALIDATION = json.loads((OUT / "T400_VALIDATION.json").read_text(encoding="utf-8"))


def read_rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def f(value: str) -> float:
    return float(value)


pop = RESULTS["primary_population"]
event = RESULTS["primary_event_transfer"]
full = RESULTS["full_fit_population_reference_not_primary"]

population_curve = [
    {
        "local_child_ara": f(row["local_child_ara"]),
        "delayed_rate_peak_normalized": f(row["delayed_rate_peak_normalized"]),
    }
    for row in read_rows("T400_LOCAL_CHILD_CURVE.csv")
]
event_histogram = [
    {
        "bin_center": f(row["bin_center"]),
        "effective_delayed_weight": f(row["effective_delayed_weight"]),
    }
    for row in read_rows("T400_PRIMARY_EVENT_HISTOGRAM.csv")
]
split_rows = [row for row in read_rows("T400_REPEATED_SPLITS.csv") if row["valid"].lower() == "true"]
split_counts = Counter(f(row["holdout_weighted_mode"]) for row in split_rows)
split_modes = [{"mode": mode, "split_count": count} for mode, count in sorted(split_counts.items())]

landmarks = [
    {"landmark": "Population crest", "local_child_ara": pop["local_crest_ara"]},
    {"landmark": "Population mean", "local_child_ara": pop["local_weighted_mean"]},
    {"landmark": "Population median", "local_child_ara": pop["local_weighted_median"]},
    {"landmark": "Event mean", "local_child_ara": event["holdout_weighted_mean"]},
    {"landmark": "Event median", "local_child_ara": event["holdout_weighted_median"]},
    {"landmark": "Event mode", "local_child_ara": event["holdout_weighted_mode"]},
]

population_gates = [
    {"gate": key, "status": "PASS" if value else "FAIL"}
    for key, value in RESULTS["population_gates"].items()
]
event_gates = [
    {"gate": key, "status": "PASS" if value else "FAIL"}
    for key, value in RESULTS["event_gates"].items()
]
validation_rows = [
    {"check": key, "status": "PASS" if value else "FAIL"}
    for key, value in VALIDATION["checks"].items()
]

generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def source(source_id: str, label: str, path: str, description: str, tables: list[str]) -> dict:
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        sql = f"SELECT * FROM read_csv_auto('{path}')"
        engine = "duckdb"
    elif suffix == ".json":
        sql = f"SELECT * FROM read_json_auto('{path}', format='auto')"
        engine = "duckdb"
    else:
        sql = None
        engine = "file"
    query = {
        "engine": engine,
        "language": Path(path).suffix.lstrip(".") or "file",
        "description": description,
        "tables_used": tables,
    }
    if sql is not None:
        query["sql"] = sql
    return {
        "id": source_id,
        "label": label,
        "path": path,
        "query": query,
    }


sources = [
    source("t400_curve", "T400 local child population curve", "analysis/muon/T400_nested_child_window_population_to_event/T400_LOCAL_CHILD_CURVE.csv", "Frozen calibration-only population child coordinate and delayed-rate curve.", ["T400_LOCAL_CHILD_CURVE.csv"]),
    source("t400_events", "T400 untouched event histogram", "analysis/muon/T400_nested_child_window_population_to_event/T400_PRIMARY_EVENT_HISTOGRAM.csv", "Calibration-frozen delayed-membership weights in untouched event rows.", ["T400_PRIMARY_EVENT_HISTOGRAM.csv"]),
    source("t400_splits", "T400 deterministic split ledger", "analysis/muon/T400_nested_child_window_population_to_event/T400_REPEATED_SPLITS.csv", "Twenty deterministic population-to-event transfers.", ["T400_REPEATED_SPLITS.csv"]),
    source("t400_results", "T400 saved results", "analysis/muon/T400_nested_child_window_population_to_event/T400_RESULTS.json", "Primary values, gates, controls and evidence boundaries.", ["T400_RESULTS.json"]),
    source("t400_validation", "T400 independent validation", "analysis/muon/T400_nested_child_window_population_to_event/T400_VALIDATION.json", "Independent saved-artifact and arithmetic validation.", ["T400_VALIDATION.json"]),
    source("t400_protocol", "Frozen T400 protocol", "analysis/muon/T400_NESTED_CHILD_WINDOW_POPULATION_TO_EVENT_PROTOCOL_2026-08-17.md", "Predeclared coordinate, gates, controls and claim boundary.", ["T400 protocol"]),
    {
        "id": "coherent_2022",
        "label": "COHERENT CsI public measurement and ancillary data",
        "path": "https://arxiv.org/abs/2110.07730",
    },
]

charts = [
    {
        "id": "population_child_curve",
        "title": "Population child window",
        "subtitle": "Objective delayed-child interval expanded from its parent cut to local ARA 0–2",
        "type": "line",
        "dataset": "population_curve",
        "sourceId": "t400_curve",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [
            {"axis": "x", "value": 1.0, "label": "Local ridge 1.0", "color": "neutral", "lineStyle": "dashed"},
            {"axis": "x", "value": pop["local_crest_ara"], "label": f"Primary crest {pop['local_crest_ara']:.3f}", "color": "gold", "lineStyle": "solid"},
        ],
        "encodings": {
            "x": {"field": "local_child_ara", "type": "quantitative", "label": "Local delayed-child ARA (0–2)"},
            "y": {"field": "delayed_rate_peak_normalized", "type": "quantitative", "label": "Delayed rate / peak"},
            "tooltip": [
                {"field": "local_child_ara", "type": "quantitative", "label": "Child ARA"},
                {"field": "delayed_rate_peak_normalized", "type": "quantitative", "label": "Rate / peak"},
            ],
        },
    },
    {
        "id": "event_histogram",
        "title": "Untouched event candidates",
        "subtitle": "Effective delayed-event weight after the child mapping was frozen on calibration rows",
        "type": "bar",
        "dataset": "event_histogram",
        "sourceId": "t400_events",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [{"axis": "x", "value": 1.0, "label": "Local ridge 1.0", "color": "neutral", "lineStyle": "dashed"}],
        "encodings": {
            "x": {"field": "bin_center", "type": "quantitative", "label": "Frozen local child ARA"},
            "y": {"field": "effective_delayed_weight", "type": "quantitative", "label": "Effective delayed-event weight"},
            "tooltip": [
                {"field": "bin_center", "type": "quantitative", "label": "Bin centre"},
                {"field": "effective_delayed_weight", "type": "quantitative", "label": "Effective weight"},
            ],
        },
    },
    {
        "id": "split_modes",
        "title": "Mode stability across deterministic splits",
        "subtitle": "Twelve of twenty modes fell inside the broad 0.5–1.5 event neighbourhood",
        "type": "bar",
        "dataset": "split_modes",
        "sourceId": "t400_splits",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [{"axis": "x", "value": 1.0, "label": "Local ridge 1.0", "color": "neutral", "lineStyle": "dashed"}],
        "encodings": {
            "x": {"field": "mode", "type": "quantitative", "label": "Weighted mode on local ARA"},
            "y": {"field": "split_count", "type": "quantitative", "label": "Split count"},
            "tooltip": [
                {"field": "mode", "type": "quantitative", "label": "Mode"},
                {"field": "split_count", "type": "quantitative", "label": "Splits"},
            ],
        },
    },
    {
        "id": "landmark_comparison",
        "title": "Population and event landmarks",
        "subtitle": "Means and medians reproduce the ridge; the two modes do not",
        "type": "bar",
        "dataset": "landmarks",
        "sourceId": "t400_results",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [{"axis": "y", "value": 1.0, "label": "Local ridge 1.0", "color": "neutral", "lineStyle": "dashed"}],
        "encodings": {
            "x": {"field": "landmark", "type": "nominal", "label": "Landmark"},
            "y": {"field": "local_child_ara", "type": "quantitative", "label": "Local child ARA"},
            "tooltip": [
                {"field": "landmark", "type": "nominal", "label": "Landmark"},
                {"field": "local_child_ara", "type": "quantitative", "label": "Child ARA"},
            ],
        },
    },
]

tables = [
    {
        "id": "population_gates",
        "title": "Frozen population gates",
        "subtitle": "The primary crest gate failed even though robustness cuts were strong",
        "dataset": "population_gates",
        "sourceId": "t400_results",
        "columns": [{"field": "gate", "label": "Gate", "type": "text"}, {"field": "status", "label": "Result", "type": "text"}],
    },
    {
        "id": "event_gates",
        "title": "Frozen event-transfer gates",
        "subtitle": "Only the mean-transfer gate passed",
        "dataset": "event_gates",
        "sourceId": "t400_results",
        "columns": [{"field": "gate", "label": "Gate", "type": "text"}, {"field": "status", "label": "Result", "type": "text"}],
    },
    {
        "id": "validation",
        "title": "Independent saved-artifact validation",
        "subtitle": "Integrity and arithmetic pass; scientific gate failures remain failures",
        "dataset": "validation",
        "sourceId": "t400_validation",
        "columns": [{"field": "check", "label": "Check", "type": "text"}, {"field": "status", "label": "Status", "type": "text"}],
    },
]

blocks = [
    {
        "id": "summary",
        "type": "markdown",
        "body": f"# T400 — Nested delayed-child window: population to event\n\n## Technical summary\n\n**The parent-to-child cut worked, but the frozen mode-at-ridge prediction did not.** The objective population interval runs from **{pop['left_time_us']:.6f} to {pop['right_time_us']:.6f} µs** and expands cleanly to a local ARA 0–2. Population and event-weighted means/medians sit near the local ridge. The population crest is **{pop['local_crest_ara']:.3f}** and the untouched event mode is **{event['holdout_weighted_mode']:.3f}**, so neither density maximum supports a ridge-centred bell curve. This is a partial population-to-individual transfer, not an individual neutrino-birth clock.",
    },
    {"id": "population_text", "type": "markdown", "body": f"## Population child cut\n\nThe boundaries are objective: prompt/delayed rate equality on the left, delayed crest inside, and the first return to the left-boundary delayed height on the right. The population weighted mean is **{pop['local_weighted_mean']:.3f}** and median **{pop['local_weighted_median']:.3f}**, but the primary crest **{pop['local_crest_ara']:.3f}** misses the predeclared 0.75–1.25 gate. Sixteen of seventeen leave-one-out cuts pass that gate and the circular-shift control gives **p = {pop['phase_shift_p_upper']:.4f}**; those are robustness evidence, not permission to replace the failed primary gate."},
    {"id": "population_chart", "type": "chart", "chartId": "population_child_curve"},
    {"id": "population_gate_table", "type": "table", "tableId": "population_gates"},
    {"id": "event_text", "type": "markdown", "body": f"## Transfer to untouched detector-event rows\n\nThe primary child window contains **{event['holdout_C_events_in_window']}** beam-coincident holdout rows but only **{event['effective_delayed_holdout']:.3f}** effective delayed-event weights. Their weighted mean (**{event['holdout_weighted_mean']:.3f}**) and median (**{event['holdout_weighted_median']:.3f}**) lie near the ridge; their mode (**{event['holdout_weighted_mode']:.3f}**) lies on the upper side. The event distribution is therefore centred but not peaked at 1.0."},
    {"id": "event_chart", "type": "chart", "chartId": "event_histogram"},
    {"id": "split_text", "type": "markdown", "body": f"## Stability across calibration/holdout partitions\n\nOnly **{RESULTS['repeated_splits']['broad_ridge_mode_fraction']:.0%}** of twenty deterministic splits place the weighted mode in 0.5–1.5, below the frozen 70% gate. The bootstrap mode rate is **{RESULTS['event_bootstrap']['broad_ridge_mode_fraction']:.2%}**. In contrast, the weighted-mean bootstrap interval **[{RESULTS['event_bootstrap']['weighted_mean_ci95'][0]:.3f}, {RESULTS['event_bootstrap']['weighted_mean_ci95'][1]:.3f}]** contains 1.0."},
    {"id": "split_chart", "type": "chart", "chartId": "split_modes"},
    {"id": "landmark_chart", "type": "chart", "chartId": "landmark_comparison"},
    {"id": "event_gate_table", "type": "table", "tableId": "event_gates"},
    {"id": "scope", "type": "markdown", "body": "## Scope, data and definitions\n\n- **Parent identity:** fitted prompt plus delayed COHERENT CsI population release.\n- **Child identity:** delayed-dominant release interval nested inside that parent.\n- **Individual rows:** detector events, not neutrino-flavor tags or named parent-child links.\n- **Membership weight:** a calibration-frozen statistical delayed-branch score.\n- **Primary fit resolution:** released 0.5 µs timing components.\n\nThe saved full T398 fit gives a diagnostic crest of **%.3f**, closer to the local ridge than the T400 timing-only primary. It is not substituted for the frozen result." % full["local_crest_ara"]},
    {"id": "method", "type": "markdown", "body": "## Methodology\n\nA deterministic 70/30 split fit the five timing components on calibration rows. The calibration population alone defined the child boundaries and local mapping. The mapping was then applied without refitting to holdout coincident and anti-coincident rows. Twenty deterministic split salts, 2,000 primary-event bootstraps, seventeen registered leave-one-bin-out population fits, a circular phase-shift control, and mode sensitivity across bin counts and kernel widths were recorded."},
    {"id": "limitations", "type": "markdown", "body": "## Limitations and robustness\n\nThe event window has fewer than ten effective delayed weights, and timing-only membership scores are nearly constant within each 0.5 µs source bin. Coincident and anti-coincident median scores therefore tie. T400 cannot identify both neutral children from one muon or time their individual births. Its positive result is narrower: an objective child coordinate exists and its centres transfer; its density modes do not."},
    {"id": "validation_table", "type": "table", "tableId": "validation"},
    {"id": "next_steps", "type": "markdown", "body": "## Next step\n\nTransfer this frozen coordinate to event-linked data containing a parent muon, charged-daughter momentum or direction, and neutral-sensitive timing in the same event record. That would provide a genuine population-to-individual test rather than a statistical mixture assignment.\n\n## Further questions\n\n- Is the two-sided event shape physical child asymmetry or only coarse timing resolution?\n- Does the full event-linked child retain a centre at 1.0 while its mode moves with parent asymmetry?\n- Can the two neutral children be separated without source-template assignment?"},
]

artifact = {
    "surface": "report",
    "manifest": {
        "version": 1,
        "surface": "report",
        "title": "T400 — Nested delayed-child window: population to event",
        "description": "Frozen ARA child-window construction and transfer from a COHERENT CsI population fit to untouched detector-event candidates.",
        "generatedAt": generated,
        "cards": [],
        "charts": charts,
        "tables": tables,
        "sources": sources,
        "blocks": blocks,
    },
    "snapshot": {
        "version": 1,
        "generatedAt": generated,
        "status": "ready",
        "datasets": {
            "population_curve": population_curve,
            "event_histogram": event_histogram,
            "split_modes": split_modes,
            "landmarks": landmarks,
            "population_gates": population_gates,
            "event_gates": event_gates,
            "validation": validation_rows,
        },
    },
    "sources": [{"id": item["id"], "query": item.get("query", {"engine": "web", "description": item["label"]})} for item in sources],
    "package_info": {"originUrl": "artifact://t400-nested-child-window-population-to-event", "controls": {"edit": False, "refresh": False}},
}

(OUT / "artifact.json").write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")
print(OUT / "artifact.json")

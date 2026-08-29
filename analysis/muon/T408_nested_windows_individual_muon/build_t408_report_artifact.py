#!/usr/bin/env python3
"""Build the bounded Data Analytics report artifact for T408."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def read_csv(name: str) -> list[dict[str, object]]:
    with (HERE / name).open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for key, value in list(row.items()):
            if value is None or value == "":
                continue
            try:
                row[key] = int(value)
                continue
            except ValueError:
                pass
            try:
                row[key] = float(value)
            except ValueError:
                pass
    return rows


results = json.loads((HERE / "T408_RESULTS.json").read_text(encoding="utf-8"))
models = read_csv("T408_MODEL_SUMMARY.csv")
events = read_csv("T408_HOLDOUT_EVENT_SCORES.csv")
blocks_raw = read_csv("T408_BLOCK_DIAGNOSTICS.csv")
topology_raw = read_csv("T408_TOPOLOGY_DIAGNOSTICS.csv")
validation = json.loads((HERE / "T408_VALIDATION.json").read_text(encoding="utf-8"))

for row in events:
    row["event"] = f"{str(row['file'])[-6:]} #{row['event_index']}"
    row["pure_class"] = (
        "inside pure small window"
        if int(row["actual_in_pure_small_window"]) == 1
        else "elsewhere in parent window"
    )
    row["topology"] = (
        "both pairs"
        if int(row["present_A"]) == 1 and int(row["present_B"]) == 1
        else "A only"
        if int(row["present_A"]) == 1
        else "B only"
    )

blocks: list[dict[str, object]] = []
for row in blocks_raw:
    run = "17 Mar" if str(row["file"]).endswith("0317.0") else "18 Mar"
    sequence = int(row["block"]) + (0 if run == "17 Mar" else 6)
    for outcome, label in (("pure", "Pure 0.50–0.75"), ("observed", "Observed 0.50–0.706")):
        blocks.append(
            {
                "sequence": sequence,
                "block_label": f"{run} B{row['block']}",
                "run": run,
                "block": int(row["block"]),
                "outcome": label,
                "n": int(row["n"]),
                "positive": int(row[f"{outcome}_positive"]),
                "positive_rate": float(row[f"{outcome}_positive_rate"]),
                "parent_minus_nested_logloss": float(
                    row[f"{outcome}_parent_minus_nested_logloss"]
                ),
            }
        )

topology: list[dict[str, object]] = []
for row in topology_raw:
    for outcome, label in (("pure", "Pure 0.50–0.75"), ("observed", "Observed 0.50–0.706")):
        topology.append(
            {
                "topology": row["topology"],
                "n": int(row["n"]),
                "outcome": label,
                "positive": int(row[f"{outcome}_positive"]),
                "positive_rate": float(row[f"{outcome}_positive_rate"]),
                "mean_nested_probability": float(
                    row[f"mean_nested_probability_{outcome}"]
                ),
            }
        )

windows = [
    {
        "window": "Parent conditioning window",
        "lower_us": results["windows_us"]["parent"][0],
        "upper_us": results["windows_us"]["parent"][1],
        "width_us": results["windows_us"]["parent"][1]
        - results["windows_us"]["parent"][0],
        "holdout_events": results["parent_window_counts"]["holdout"],
        "holdout_positive": results["parent_window_counts"]["holdout"],
        "role": "Conditioning boundary",
    },
    {
        "window": "Pure small child window",
        "lower_us": results["windows_us"]["pure"][0],
        "upper_us": results["windows_us"]["pure"][1],
        "width_us": results["windows_us"]["pure"][1]
        - results["windows_us"]["pure"][0],
        "holdout_events": results["parent_window_counts"]["holdout"],
        "holdout_positive": results["pure"]["positive_holdout"],
        "role": "Frozen primary outcome",
    },
    {
        "window": "Observed small child window",
        "lower_us": results["windows_us"]["observed"][0],
        "upper_us": results["windows_us"]["observed"][1],
        "width_us": results["windows_us"]["observed"][1]
        - results["windows_us"]["observed"][0],
        "holdout_events": results["parent_window_counts"]["holdout"],
        "holdout_positive": results["observed"]["positive_holdout"],
        "role": "Secondary descriptive outcome",
    },
]

gates: list[dict[str, object]] = []
for outcome, label in (("pure", "Pure small window"), ("observed", "Observed small window")):
    for gate, passed in results[outcome]["gates"].items():
        gates.append(
            {
                "outcome": label,
                "gate": gate,
                "status": "PASS" if passed else "FAIL",
            }
        )

validation_rows = [
    {
        "test": "T408 saved-output validator",
        "status": validation.get("status", "UNKNOWN"),
        "checks": len(validation.get("checks", [])),
        "details": "; ".join(validation.get("checks", [])),
    }
]

source_base = "analysis/muon/T408_nested_windows_individual_muon"


def csv_source(source_id: str, label: str, filename: str, description: str) -> dict:
    path = f"{source_base}/{filename}"
    return {
        "id": source_id,
        "label": label,
        "path": path,
        "query": {
            "engine": "duckdb",
            "language": "sql",
            "description": description,
            "tables_used": [filename],
            "sql": f"SELECT * FROM read_csv_auto('{path}')",
            "filters": [
                "Calibration and holdout runs were fixed before model scoring.",
                "T408 event models are scored only inside the transferred parent window.",
            ],
        },
    }


sources = [
    csv_source(
        "t408_events",
        "T408 individual holdout event scores",
        "T408_HOLDOUT_EVENT_SCORES.csv",
        "The 527 held-out event-linked muons inside the transferred parent window, including incoming parent/child ARA coordinates, observed charged-daughter timing class and frozen model probabilities.",
    ),
    csv_source(
        "t408_models",
        "T408 model summary",
        "T408_MODEL_SUMMARY.csv",
        "Held-out log loss, AUC and Brier score for ordinary geometry, parent ARA, nested child ARA and wrong-lineage controls under both small-window outcomes.",
    ),
    csv_source(
        "t408_blocks",
        "T408 chronological block diagnostics",
        "T408_BLOCK_DIAGNOSTICS.csv",
        "Post-result 12-block diagnostics used to locate the source of the frozen uncertainty failure without changing its verdict.",
    ),
    csv_source(
        "t408_topology",
        "T408 channel-topology diagnostics",
        "T408_TOPOLOGY_DIAGNOSTICS.csv",
        "Observed and predicted small-window rates for both-pair, A-only and B-only incoming counter topologies.",
    ),
    {
        "id": "t408_results",
        "label": "T408 frozen results",
        "path": f"{source_base}/T408_RESULTS.json",
        "query": {
            "engine": "duckdb",
            "language": "sql",
            "description": "Frozen windows, model contrasts, uncertainty, gates, verdict and evidence boundaries.",
            "tables_used": ["T408_RESULTS.json"],
            "sql": f"SELECT * FROM read_json_auto('{source_base}/T408_RESULTS.json', format='auto')",
            "metric_definitions": {
                "MP_minus_MN": "Mean held-out log loss of the parent-only ARA model minus the nested child-ARA model. Positive values favour the nested model.",
                "pure_small_window": "Charged-daughter delay from the cumulative-ARA time corresponding to local ARA 0.50 through local ARA 0.75.",
                "observed_small_window": "Secondary charged-daughter delay from local ARA 0.50 through the previously observed crest coordinate 0.706306.",
            },
        },
    },
    {
        "id": "t408_protocol",
        "label": "T408 frozen protocol",
        "path": "analysis/muon/T408_NESTED_WINDOWS_INDIVIDUAL_MUON_PROTOCOL_2026-08-18.md",
        "query": {
            "engine": "file",
            "language": "markdown",
            "description": "Pre-run identities, windows, controls, gates and verdict rule.",
            "tables_used": ["T408_NESTED_WINDOWS_INDIVIDUAL_MUON_PROTOCOL_2026-08-18.md"],
        },
    },
    {
        "id": "t408_validation",
        "label": "T408 independent saved-output validation",
        "path": f"{source_base}/T408_VALIDATION.json",
        "query": {
            "engine": "duckdb",
            "language": "sql",
            "description": "Integrity and arithmetic checks recomputed from the saved T408 outputs.",
            "tables_used": ["T408_VALIDATION.json"],
            "sql": f"SELECT * FROM read_json_auto('{source_base}/T408_VALIDATION.json', format='auto')",
        },
    },
]

cards: list[dict[str, object]] = []

charts = [
    {
        "id": "model_logloss",
        "title": "Held-out log loss by model and child window",
        "subtitle": "Lower is better; MN is the nested same-lineage child model and MW is the crossed-lineage control.",
        "type": "bar",
        "dataset": "models",
        "sourceId": "t408_models",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "options": {"orientation": "vertical", "grouping": "grouped"},
        "encodings": {
            "x": {"field": "model", "type": "nominal", "label": "Model"},
            "y": {"field": "mean_logloss", "type": "quantitative", "label": "Mean held-out log loss"},
            "color": {"field": "outcome", "type": "nominal", "label": "Small-window outcome"},
            "tooltip": [
                {"field": "auc", "type": "quantitative", "label": "AUC"},
                {"field": "brier", "type": "quantitative", "label": "Brier score"},
            ],
        },
    },
    {
        "id": "child_geometry",
        "title": "Incoming child ARA coordinates for individual held-out muons",
        "subtitle": "The pure small-window cases are sparse within the 527 parent-conditioned events rather than confined to one fixed parent coordinate.",
        "type": "scatter",
        "dataset": "events",
        "sourceId": "t408_events",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "encodings": {
            "x": {"field": "x_A", "type": "quantitative", "label": "Incoming child A coordinate x_A"},
            "y": {"field": "x_B", "type": "quantitative", "label": "Incoming child B coordinate x_B"},
            "color": {"field": "pure_class", "type": "nominal", "label": "Observed timing class"},
            "tooltip": [
                {"field": "event", "type": "nominal", "label": "Event"},
                {"field": "delay_us", "type": "quantitative", "label": "Daughter delay (microseconds)"},
                {"field": "x_parent", "type": "quantitative", "label": "Parent ARA"},
                {"field": "topology", "type": "nominal", "label": "Incoming topology"},
            ],
        },
    },
    {
        "id": "block_improvement",
        "title": "Nested-model improvement across chronological holdout blocks",
        "subtitle": "One 18 March block reverses strongly enough to keep both bootstrap intervals across zero.",
        "type": "line",
        "dataset": "blocks",
        "sourceId": "t408_blocks",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [
            {"axis": "y", "value": 0.0, "label": "no improvement", "color": "neutral", "lineStyle": "solid"}
        ],
        "encodings": {
            "x": {"field": "sequence", "type": "quantitative", "label": "Chronological block (1–12)"},
            "y": {"field": "parent_minus_nested_logloss", "type": "quantitative", "label": "Parent minus nested log loss"},
            "color": {"field": "outcome", "type": "nominal", "label": "Small-window outcome"},
            "tooltip": [
                {"field": "block_label", "type": "nominal", "label": "Block"},
                {"field": "n", "type": "quantitative", "label": "Events"},
                {"field": "positive_rate", "type": "quantitative", "label": "Observed positive rate"},
            ],
        },
    },
    {
        "id": "topology_rates",
        "title": "Observed child-window rate by incoming counter topology",
        "subtitle": "The A-only topology is enriched, so channel availability remains a material alternative explanation.",
        "type": "bar",
        "dataset": "topology",
        "sourceId": "t408_topology",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "options": {"orientation": "vertical", "grouping": "grouped"},
        "encodings": {
            "x": {"field": "topology", "type": "nominal", "label": "Incoming topology"},
            "y": {"field": "positive_rate", "type": "quantitative", "label": "Observed small-window rate"},
            "color": {"field": "outcome", "type": "nominal", "label": "Small-window outcome"},
            "tooltip": [
                {"field": "n", "type": "quantitative", "label": "Events"},
                {"field": "mean_nested_probability", "type": "quantitative", "label": "Mean nested probability"},
            ],
        },
    },
]

tables = [
    {
        "id": "window_table",
        "title": "Transferred parent and child timing windows",
        "subtitle": "The smaller outcomes are tested only after conditioning on the larger parent window.",
        "dataset": "windows",
        "sourceId": "t408_results",
        "defaultSort": {"field": "width_us", "direction": "desc"},
        "columns": [
            {"field": "window", "label": "Window", "type": "text"},
            {"field": "lower_us", "label": "Lower (microseconds)", "type": "number"},
            {"field": "upper_us", "label": "Upper (microseconds)", "type": "number"},
            {"field": "width_us", "label": "Width (microseconds)", "type": "number"},
            {"field": "holdout_positive", "label": "Holdout cases", "type": "number"},
            {"field": "role", "label": "Role", "type": "text"},
        ],
    },
    {
        "id": "gate_table",
        "title": "Frozen confirmation gates",
        "subtitle": "The pure primary passes 3/5 gates; the observed secondary passes 4/5 but cannot replace the primary verdict.",
        "dataset": "gates",
        "sourceId": "t408_results",
        "defaultSort": {"field": "outcome", "direction": "asc"},
        "columns": [
            {"field": "outcome", "label": "Outcome", "type": "text"},
            {"field": "gate", "label": "Gate", "type": "text"},
            {"field": "status", "label": "Result", "type": "text"},
        ],
    },
    {
        "id": "validation_table",
        "title": "Independent saved-output validation",
        "subtitle": "The validator recomputed the registered windows, counts and model contrasts from the saved files.",
        "dataset": "validation",
        "sourceId": "t408_validation",
        "defaultSort": {"field": "test", "direction": "asc"},
        "columns": [
            {"field": "test", "label": "Validator", "type": "text"},
            {"field": "status", "label": "Status", "type": "text"},
            {"field": "checks", "label": "Checks", "type": "number"},
        ],
    },
]

title = "T408 — Nested parent and child windows in individual muons"
blocks_manifest = [
    {"id": "title", "type": "markdown", "body": f"# {title}"},
    {
        "id": "technical_summary",
        "type": "markdown",
        "body": "## Technical summary\n\n**The nested individual-muon cut is directionally positive but does not pass the frozen confirmation rule.** Among 527 held-out event-linked muons inside the transferred parent timing window, same-lineage child ARA geometry improved prediction of whether the later charged-daughter signal fell inside both smaller windows. The improvement appeared in both held-out runs and beat a deliberately crossed-lineage control. The frozen pure window nevertheless failed its bootstrap and permutation gates; its 95% block interval crossed zero. The narrower observed window passed the permutation check but its block interval also crossed zero. The correct verdict is **not supported**, with a localized near-support signal worth testing on fresh runs.",
        "sourceId": "t408_results",
    },
    {
        "id": "key_findings",
        "type": "markdown",
        "body": "## Key findings\n\n- The frozen pure child window contains 62 of 527 holdout events. Its nested model gains `+0.002376` log-loss units over the parent-only model, but the 95% block interval is `[-0.000991,+0.005138]` and permutation `p=0.175`.\n- The secondary observed child window contains 51 events. Its gain is larger (`+0.003866`), appears in both runs, beats the wrong-lineage control and passes permutation (`p=0.0328`), but its interval remains `[-0.001840,+0.007964]`.\n- This differs materially from T407: a fixed parent coordinate carried no event-level timing information, whereas decomposing the same conditioned events into their same-lineage children improves both runs.\n- One chronological block on 18 March reverses sharply. The present archive cannot distinguish a detector regime from an ARA relation that changes with local participation.",
        "sourceId": "t408_results",
    },
    {"id": "model_chart_block", "type": "chart", "chartId": "model_logloss"},
    {
        "id": "nested_geometry_text",
        "type": "markdown",
        "body": "## The useful information is nested inside the parent window\n\nThe large parent window is not being asked to identify an exact release point. It selects the relevant parent stage. Inside that stage, the two child pairings are decompressed separately and used to alter the probability of the smaller charged-daughter timing outcome. This matches the ARA distinction between a parent landmark and distorted individual child positions: the child events do not need to sit at one universal coordinate.",
        "sourceId": "t408_protocol",
    },
    {"id": "child_chart_block", "type": "chart", "chartId": "child_geometry"},
    {
        "id": "robustness_text",
        "type": "markdown",
        "body": "## Robustness is the unresolved boundary\n\nBoth held-out runs point in the predicted direction, so the effect is not produced by only one run. However, chronological resampling is deliberately stricter than a whole-run average. The fifth block of the 18 March run has parent-minus-nested log-loss of `-0.01228` for the pure window and `-0.02218` for the observed window. That local reversal is sufficient to keep both confidence intervals across zero and prevents confirmation.",
        "sourceId": "t408_blocks",
    },
    {"id": "block_chart_block", "type": "chart", "chartId": "block_improvement"},
    {
        "id": "topology_text",
        "type": "markdown",
        "body": "## Channel topology remains a competing explanation\n\nEvents with only the A pair present have a pure-window rate of `16.7%`, compared with `9.75%` when both pairs are present. The nested model underpredicts that A-only enrichment. The wrong-lineage control reduces the chance that any arbitrary four-counter split explains the result, but it does not eliminate detector-channel availability as an alternative source of the apparent child relation.",
        "sourceId": "t408_topology",
    },
    {"id": "topology_chart_block", "type": "chart", "chartId": "topology_rates"},
    {
        "id": "scope_definitions",
        "type": "markdown",
        "body": "## Scope, data and metric definitions\n\n- **Who:** event-linked stopped-muon candidates from held-out QuarkNet runs dated 17 and 18 March 2020.\n- **Parent window:** daughter delay `0.568858–1.382809 microseconds`, transferred from T400.\n- **Pure small window:** `0.714271–0.801804 microseconds`, corresponding to local cumulative ARA `0.50–0.75`.\n- **Observed small window:** `0.714271–0.785615 microseconds`, corresponding to local cumulative ARA `0.50–0.706306`; secondary only.\n- **Outcome:** whether the later charged-daughter candidate falls inside a small window, conditional on already being inside the parent window.\n- **Primary metric:** held-out parent-only minus nested-model mean log loss. Positive values favour the nested child relation.\n- **Observation boundary:** neither neutrino is directly detected and no individual spin trajectory is measured.",
        "sourceId": "t408_results",
    },
    {"id": "window_table_block", "type": "table", "tableId": "window_table"},
    {
        "id": "methodology",
        "type": "markdown",
        "body": "## Methodology and model specification\n\nThe protocol, windows, feature families, wrong-lineage control and verdict gates were frozen before scoring. Calibration-only gain normalization was applied to the four incoming prompt counters. `MP` adds the parent ARA coordinate to ordinary charge/multiplicity/depth features. `MN` adds the separately decompressed same-lineage child coordinates and their signed/absolute relation. `MW` applies the same calculation to deliberately crossed counter pairs. Models were trained on the calibration run and evaluated without refitting on two held-out runs. Uncertainty used a 12-block bootstrap and a within-run permutation test.",
        "sourceId": "t408_protocol",
    },
    {"id": "gate_table_block", "type": "table", "tableId": "gate_table"},
    {
        "id": "limitations",
        "type": "markdown",
        "body": "## Limitations, uncertainty and evidential boundary\n\nThis is an event-level probability test, not an exact birth-time reconstruction. The later linked pulse is a charged daughter proxy, not a neutrino measurement. The smaller windows are transferred from earlier aggregate work, but the secondary observed endpoint remains more empirically shaped than the pure endpoint. There are only 62 and 51 positive holdout cases. One local block and one detector topology materially affect the result. No model may be tuned to remove those facts after inspection.",
        "sourceId": "t408_results",
    },
    {
        "id": "recommended_next",
        "type": "markdown",
        "body": "## Recommended next step\n\nFreeze the current nested feature map and score fresh detector dates or a second event-linked archive without changing the windows. The result should be considered strengthened only if the nested same-lineage model improves both new runs, beats the crossed-lineage control and produces a positive block interval without excluding inconvenient blocks. A spin-resolved or daughter-direction dataset would be stronger still because it adds an independent Information³ relation rather than another detector proxy.",
    },
    {
        "id": "further_questions",
        "type": "markdown",
        "body": "## Further questions\n\n1. Does the 18 March block-five reversal repeat at the same detector/channel state?\n2. Does explicit topology balancing preserve the nested improvement?\n3. Is the narrower observed window genuinely more informative, or does its better score arise from the particular positive cases in this archive?\n4. Can a spin- or direction-sensitive relation predict the hidden neutral branch independently of daughter delay?",
    },
    {"id": "validation_table_block", "type": "table", "tableId": "validation_table"},
]

artifact = {
    "surface": "report",
    "manifest": {
        "version": 1,
        "surface": "report",
        "title": title,
        "description": "Frozen nested-window test of same-lineage child ARA geometry in individual event-linked stopped muons.",
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "cards": cards,
        "charts": charts,
        "tables": tables,
        "sources": sources,
        "blocks": blocks_manifest,
    },
    "snapshot": {
        "version": 1,
        "status": "ready",
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "datasets": {
            "headline_counts": [
                {
                    "value": results["parent_window_counts"]["holdout"],
                    "pure_cases": results["pure"]["positive_holdout"],
                    "observed_cases": results["observed"]["positive_holdout"],
                }
            ],
            "headline_metrics": [
                {
                    "pure_gain": results["pure"]["contrasts"]["MP_minus_MN"]["mean"],
                    "pure_p": results["pure"]["permutation"]["p_upper_add_one"],
                    "observed_gain": results["observed"]["contrasts"]["MP_minus_MN"]["mean"],
                    "observed_p": results["observed"]["permutation"]["p_upper_add_one"],
                }
            ],
            "models": models,
            "events": events,
            "blocks": blocks,
            "topology": topology,
            "windows": windows,
            "gates": gates,
            "validation": validation_rows,
        },
        "accessIssues": [],
    },
    "sources": sources,
}

(HERE / "artifact.json").write_text(
    json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
print(HERE / "artifact.json")

#!/usr/bin/env python3
"""Build the canonical MCP report artifact for T409/T409B."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read_csv(name: str) -> list[dict]:
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def num(value):
    if value in (None, "", "NaN"):
        return None
    return float(value)


def write_csv(name: str, rows: list[dict]) -> None:
    with (HERE / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    t409 = json.loads((HERE / "T409_RESULTS.json").read_text(encoding="utf-8"))
    t409b = json.loads((HERE / "T409B_RESULTS.json").read_text(encoding="utf-8"))
    validation = json.loads((HERE / "T409_VALIDATION.json").read_text(encoding="utf-8"))
    blocks = read_csv("T409_BLOCK_RIDGES.csv")
    upper = read_csv("T409B_BLOCK_CRESTS.csv")

    track = []
    for row in blocks:
        if row["population"] != "full_2109" or row["ridge"] not in ("R1", "R2") or row["resolved"] != "True":
            continue
        track.append(
            {
                "global_block": int(row["global_block"]),
                "block_label": f"{row['run'][-6:]} block {row['block']}",
                "run": row["run"],
                "ridge": row["ridge"],
                "centre": float(row["centre"]),
                "events_in_zone": int(row["count"]),
                "peak_to_median": float(row["peak_to_median"]),
                "estimator": "frozen broad-zone maximum",
            }
        )
    for row in upper:
        if row["resolved"] != "True":
            continue
        track.append(
            {
                "global_block": int(row["global_block"]),
                "block_label": f"{row['run'][-6:]} block {row['block']}",
                "run": row["run"],
                "ridge": "R3 marked",
                "centre": float(row["centre"]),
                "events_in_zone": int(row["count"]),
                "peak_to_median": float(row["peak_to_median"]),
                "estimator": "post-hoc strictly interior local maximum",
            }
        )
    track.sort(key=lambda r: (r["global_block"], r["ridge"]))

    motion = []
    for ridge in ("R1", "R2"):
        p = t409["permutations"][ridge]
        for comparison, value in (
            ("observed M", p["observed_motion_M"]),
            ("global shuffle q95", p["global_shuffle_q95"]),
            ("within-run shuffle q95", p["within_run_shuffle_q95"]),
        ):
            motion.append(
                {
                    "ridge": ridge,
                    "comparison": comparison,
                    "motion_M": value,
                    "global_p": p["global_shuffle_p_upper_add_one"],
                    "within_run_p": p["within_run_shuffle_p_upper_add_one"],
                    "resolved_blocks": t409["full"][ridge]["resolved_blocks"],
                }
            )
    p = t409b["permutation"]
    for comparison, value in (
        ("observed M", p["observed_motion_M"]),
        ("global shuffle q95", p["global_q95"]),
        ("within-run shuffle q95", p["within_run_q95"]),
    ):
        motion.append(
            {
                "ridge": "R3 marked",
                "comparison": comparison,
                "motion_M": value,
                "global_p": p["global_p_upper_add_one"],
                "within_run_p": p["within_run_p_upper_add_one"],
                "resolved_blocks": t409b["summary"]["resolved_blocks"],
            }
        )

    summaries = []
    for ridge in ("R1", "R2"):
        item = t409["full"][ridge]
        summaries.append(
            {
                "ridge": ridge,
                "zone": f"{t409['frozen']['ridges'][ridge][0]:.2f}–{t409['frozen']['ridges'][ridge][1]:.2f}",
                "centre": item["pooled"]["centre"],
                "events": item["pooled"]["count"],
                "share_nonpole": item["pooled"]["share"],
                "resolved_blocks": item["resolved_blocks"],
                "motion_M": item["motion_M"],
                "global_p": t409["permutations"][ridge]["global_shuffle_p_upper_add_one"],
                "reading": "persistent; weak chronological excess" if ridge == "R1" else "persistent; chronological displacement exceeds shuffle",
                "method_status": "frozen primary",
            }
        )
    item = t409b["summary"]
    summaries.append(
        {
            "ridge": "R3 marked",
            "zone": "1.25–1.50",
            "centre": item["pooled"]["centre"],
            "events": item["pooled"]["count"],
            "share_nonpole": item["pooled"]["share"],
            "resolved_blocks": item["resolved_blocks"],
            "motion_M": item["motion_M"],
            "global_p": t409b["permutation"]["global_p_upper_add_one"],
            "reading": "weak crest present; travel not resolved",
            "method_status": "post-hoc edge-capture repair",
        }
    )

    occupancy = [
        {
            "ridge": row["ridge"],
            "events": row["events"],
            "share_nonpole": row["share_nonpole"],
            "centre": row["centre"],
            "resolved_blocks": row["resolved_blocks"],
            "method_status": row["method_status"],
        }
        for row in summaries
    ]

    gates = [{"gate": key, "status": "PASS" if value else "FAIL"} for key, value in t409["gates"].items()]
    gates.append({"gate": "T409 broad R3 centre is strictly interior", "status": "FAIL — centre hit lower boundary 1.180"})
    gates.append({"gate": "T409B marked crest resolved in at least 8/12 blocks", "status": "PASS — 10/12"})
    gates.append({"gate": "T409B marked crest exceeds global shuffle", "status": "FAIL — p=0.745"})

    validation_rows = [
        {
            "validator": validation["test"],
            "status": validation["status"],
            "checks": validation["checks_total"],
            "passed": validation["checks_passed"],
            "boundary": "Direct Gaussian pooled centres and saved-block motion were independently recomputed; full permutation arrays were not retained.",
        }
    ]

    # Preserve the exact reviewed rows that power the report-native visuals.
    write_csv("T409_REPORT_RIDGE_TRACK.csv", track)
    write_csv("T409_REPORT_MOTION.csv", motion)
    write_csv("T409_REPORT_OCCUPANCY.csv", occupancy)
    write_csv("T409_REPORT_RIDGE_SUMMARY.csv", summaries)
    write_csv("T409_REPORT_GATES.csv", gates)
    write_csv("T409_REPORT_VALIDATION.csv", validation_rows)

    sources = [
        {
            "id": "t379_events",
            "label": "T379 event-linked held-out muon records",
            "path": "analysis/muon/T379_individual_muon_child/T379_INDIVIDUAL_MUON_CHILD_HANDOVER_EVENTS.csv",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "description": "The event-linked incoming two-pole coordinate, wrong-lineage control, charged-daughter delay and chronological event index used by T409.",
                "tables_used": ["T379_INDIVIDUAL_MUON_CHILD_HANDOVER_EVENTS.csv"],
                "sql": "SELECT * FROM read_csv_auto('analysis/muon/T379_individual_muon_child/T379_INDIVIDUAL_MUON_CHILD_HANDOVER_EVENTS.csv') WHERE split = 'holdout'",
                "filters": ["Held-out rows only.", "Exact x_mu poles 0 and 2 excluded from density-centre estimation but retained in population accounting."],
                "metric_definitions": ["x_mu = incoming charged-detector two-pole ARA coordinate on 0–2.", "Chronological block = one of six equal-count event-index blocks within each run."],
            },
        },
        {
            "id": "t409_results",
            "label": "T409 chronological ridge results",
            "path": "analysis/muon/T409_chronological_parent_ridge_tracking/T409_RESULTS.json",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "description": "Frozen-zone pooled centres, block motion, shuffled-order nulls, gates and boundaries.",
                "tables_used": ["T409_RESULTS.json", "T409_BLOCK_RIDGES.csv"],
                "sql": "SELECT * FROM read_json_auto('analysis/muon/T409_chronological_parent_ridge_tracking/T409_RESULTS.json', format='auto')",
                "filters": ["R1 0.60–0.90; R2 0.90–1.18; broad R3 1.18–1.55.", "Six chronological blocks per held-out run."],
                "metric_definitions": ["motion_M = count-weighted root-mean-square block-centre displacement from pooled centre.", "Permutation p-values are upper-tail add-one values from 5,000 shuffles."],
            },
        },
        {
            "id": "t409b_results",
            "label": "T409B marked upper-interior sensitivity",
            "path": "analysis/muon/T409_chronological_parent_ridge_tracking/T409B_RESULTS.json",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "description": "Post-hoc strictly interior local-crest repair for the marked structure near x_mu 1.35.",
                "tables_used": ["T409B_RESULTS.json", "T409B_BLOCK_CRESTS.csv"],
                "sql": "SELECT * FROM read_json_auto('analysis/muon/T409_chronological_parent_ridge_tracking/T409B_RESULTS.json', format='auto')",
                "filters": ["Search interval 1.25–1.50.", "Strictly interior local maxima only; five-event and 1.10 contrast resolution thresholds."],
                "metric_definitions": ["Marked R3 centre = highest strictly interior Gaussian-smoothed local maximum in the frozen sensitivity interval."],
            },
        },
        {
            "id": "t409_protocol",
            "label": "T409/T409B frozen method records",
            "path": "analysis/muon/T409_CHRONOLOGICAL_PARENT_RIDGE_TRACKING_PROTOCOL_2026-08-18.md",
            "query": {
                "description": "Pre-calculation T409 protocol plus the post-edge-capture T409B sensitivity protocol.",
                "tables_used": ["T409_CHRONOLOGICAL_PARENT_RIDGE_TRACKING_PROTOCOL_2026-08-18.md", "T409B_MARKED_UPPER_INTERIOR_SENSITIVITY_PROTOCOL_2026-08-18.md"],
                "filters": ["T409B is explicitly post-hoc and cannot upgrade the visual observation to confirmatory status."],
            },
        },
        {
            "id": "t409_validation",
            "label": "T409 independent validation",
            "path": "analysis/muon/T409_chronological_parent_ridge_tracking/T409_VALIDATION.json",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "description": "Independent direct-Gaussian centre checks, population/pole counts and saved-block motion recomputation.",
                "tables_used": ["T409_VALIDATION.json"],
                "sql": "SELECT * FROM read_json_auto('analysis/muon/T409_chronological_parent_ridge_tracking/T409_VALIDATION.json', format='auto')",
            },
        },
        {
            "id": "t409_report_track",
            "label": "T409 reviewed chronological ridge-track rows",
            "path": "analysis/muon/T409_chronological_parent_ridge_tracking/T409_REPORT_RIDGE_TRACK.csv",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "description": "Reviewed R1/R2 frozen block centres joined to the T409B marked-interior crest rows for one report comparison.",
                "tables_used": ["T409_REPORT_RIDGE_TRACK.csv"],
                "sql": "SELECT * FROM read_csv_auto('analysis/muon/T409_chronological_parent_ridge_tracking/T409_REPORT_RIDGE_TRACK.csv') ORDER BY global_block, ridge",
                "filters": ["Resolved block centres only.", "Marked R3 rows retain post-hoc estimator status."],
            },
        },
        {
            "id": "t409_report_motion",
            "label": "T409 reviewed motion-control rows",
            "path": "analysis/muon/T409_chronological_parent_ridge_tracking/T409_REPORT_MOTION.csv",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "description": "Observed motion and two 95th-percentile shuffle controls for each reported ridge.",
                "tables_used": ["T409_REPORT_MOTION.csv"],
                "sql": "SELECT * FROM read_csv_auto('analysis/muon/T409_chronological_parent_ridge_tracking/T409_REPORT_MOTION.csv')",
                "metric_definitions": ["motion_M is the count-weighted RMS chronological block-centre displacement from the pooled centre."],
            },
        },
        {
            "id": "t409_report_occupancy",
            "label": "T409 reviewed ridge occupancy rows",
            "path": "analysis/muon/T409_chronological_parent_ridge_tracking/T409_REPORT_OCCUPANCY.csv",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "description": "Non-pole zone event counts, shares, centres and resolution counts for R1, R2 and marked R3.",
                "tables_used": ["T409_REPORT_OCCUPANCY.csv"],
                "sql": "SELECT * FROM read_csv_auto('analysis/muon/T409_chronological_parent_ridge_tracking/T409_REPORT_OCCUPANCY.csv') ORDER BY centre",
                "filters": ["Exact x_mu poles 0 and 2 excluded from zone shares."],
            },
        },
        {
            "id": "t409_report_summary",
            "label": "T409 reviewed ridge summary rows",
            "path": "analysis/muon/T409_chronological_parent_ridge_tracking/T409_REPORT_RIDGE_SUMMARY.csv",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "description": "Reader-facing centre, occupancy, motion, permutation and method-status summary.",
                "tables_used": ["T409_REPORT_RIDGE_SUMMARY.csv"],
                "sql": "SELECT * FROM read_csv_auto('analysis/muon/T409_chronological_parent_ridge_tracking/T409_REPORT_RIDGE_SUMMARY.csv') ORDER BY centre",
            },
        },
        {
            "id": "t409_report_gates",
            "label": "T409 reviewed gates and repair status",
            "path": "analysis/muon/T409_chronological_parent_ridge_tracking/T409_REPORT_GATES.csv",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "description": "Frozen T409 gate outcomes plus explicit broad-R3 edge-capture and T409B sensitivity status.",
                "tables_used": ["T409_REPORT_GATES.csv"],
                "sql": "SELECT * FROM read_csv_auto('analysis/muon/T409_chronological_parent_ridge_tracking/T409_REPORT_GATES.csv') ORDER BY gate",
            },
        },
        {
            "id": "t409_report_validation",
            "label": "T409 reviewed validation row",
            "path": "analysis/muon/T409_chronological_parent_ridge_tracking/T409_REPORT_VALIDATION.csv",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "description": "Compact independent validation status and retained method boundary.",
                "tables_used": ["T409_REPORT_VALIDATION.csv"],
                "sql": "SELECT * FROM read_csv_auto('analysis/muon/T409_chronological_parent_ridge_tracking/T409_REPORT_VALIDATION.csv')",
            },
        },
    ]

    title = "T409 — Three parent-coordinate bands, but no travelling upper ridge"
    manifest = {
        "version": 1,
        "surface": "report",
        "title": title,
        "description": "Chronological density-ridge tracking of the three vertical structures marked in T408.",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "blocks": [
            {"id": "title", "type": "markdown", "body": f"# {title}"},
            {
                "id": "technical_summary",
                "type": "markdown",
                "sourceId": "t409_report_summary",
                "body": "## Technical summary\n\n**The vertical structure you marked is real as a population-density pattern, but the third band is not a resolved travelling branch in chronological order.** The two dominant non-pole centres are `0.761` and `1.041`. Repairing the broad-R3 edge capture recovers the marked upper-interior crest at `1.395`, present in `10/12` blocks, but its motion is smaller than shuffled-order expectation (`M=0.0406`, shuffle median `0.0465`, global `p=0.745`). R1 is persistent and only marginally more mobile than shuffled order (`p=0.070`). R2 is also persistent but does show excess block displacement (`p=0.016`). The clean reading is therefore **two strong bands, one weaker third crest, and no evidence that the third is uniquely movement-loaded in this cut**.",
            },
            {
                "id": "findings",
                "type": "markdown",
                "sourceId": "t409_report_summary",
                "body": "## The three recovered centres\n\n- **R1:** centre `0.761`, `584` non-pole events, resolved in all 12 blocks.\n- **R2:** centre `1.041`, `560` non-pole events, resolved in all 12 blocks.\n- **Marked R3:** local crest `1.395`, only `90` non-pole events, resolved in 10 blocks.\n\nThe original frozen broad R3 estimator selected `1.180`, exactly its lower boundary. That output is preserved as a failed operationalization; the `1.395` post-hoc local-crest sensitivity is the relevant description of the line drawn near `1.35`.",
            },
            {"id": "track_chart_block", "type": "chart", "chartId": "ridge_track"},
            {
                "id": "motion_text",
                "type": "markdown",
                "sourceId": "t409_report_motion",
                "body": "## Chronology does not single out the upper crest as movement\n\nThe marked R3 centre ranges from `1.302` to `1.438`, but sparse crests move that much under random event ordering. Its observed motion is below both the global and within-run shuffle medians, so the visible wobble is not evidence of a travelling branch. R2 is the only band whose block displacement exceeds its shuffle control at this resolution. That may represent a genuine regime-sensitive relation, but it is not the originally proposed moving upper line and it needs a fresh frozen replication.",
            },
            {"id": "motion_chart_block", "type": "chart", "chartId": "motion_control"},
            {
                "id": "strength_text",
                "type": "markdown",
                "sourceId": "t409_report_occupancy",
                "body": "## The third crest is structurally weaker\n\nAfter excluding exact `0` and `2` topology poles, R1 and R2 contain roughly `41.0%` and `39.3%` of the 1,425 usable coordinates. The marked R3 interval contains `6.3%`. Its lower occupancy explains why its apparent block centre is less stable and why a visual stripe can look mobile without exceeding an order-shuffled control.",
            },
            {"id": "occupancy_chart_block", "type": "chart", "chartId": "ridge_occupancy"},
            {
                "id": "scope",
                "type": "markdown",
                "sourceId": "t379_events",
                "body": "## Scope, population and metric definitions\n\n- **Population:** 2,109 held-out event-linked stopped-muon candidates from runs dated 17 and 18 March 2020.\n- **Usable non-pole coordinates:** 1,425. Exact `x_mu=0` (`576` events) and `x_mu=2` (`108` events) remain in population accounting but are excluded from density centres because they are detector/topology poles.\n- **Chronology:** six equal-count event-index blocks per run.\n- **Ridge centre:** maximum of a Gaussian-smoothed density with bandwidth `0.035 ARA`; marked R3 uses a strictly interior local maximum.\n- **Motion:** count-weighted RMS block-centre displacement from the pooled centre.\n- **Observation boundary:** the coordinate is derived from the incoming charged-detector channels; neither neutrino is directly observed.",
            },
            {"id": "summary_table_block", "type": "table", "tableId": "ridge_summary"},
            {
                "id": "methodology",
                "type": "markdown",
                "sourceId": "t409_protocol",
                "body": "## Method and repair boundary\n\nT409 froze three zones before calculation and compared chronological motion with 5,000 global-order and 5,000 within-run shuffles. The first broad R3 calculation failed to isolate the marked line because its maximum sat on the interval boundary. T409B was frozen only after that failure and searched for a strictly interior local crest in `1.25–1.50`. It is therefore a transparent sensitivity, not a new confirmatory gate.",
            },
            {"id": "gate_table_block", "type": "table", "tableId": "gate_table"},
            {
                "id": "limitations",
                "type": "markdown",
                "sourceId": "t409_validation",
                "body": "## Limitations, uncertainty and validation\n\nAll 18 independent arithmetic/source checks passed. Direct Gaussian sums reproduced the pooled centres and saved block rows reproduced every motion statistic. The full permutation arrays were not retained, so validation confirms the registered draw counts and p-values but does not independently replay every null draw. More importantly, this is a diagnostic prompted by the T408 visual: stable density bands can reflect physical relation, detector/channel response, low-multiplicity ratios, or mixtures of those effects.",
            },
            {"id": "validation_table_block", "type": "table", "tableId": "validation_table"},
            {
                "id": "next_steps",
                "type": "markdown",
                "body": "## Recommended next step\n\nFreeze the three centres on these two runs and test them unchanged on a genuinely independent event source. For the movement question, pair `x_mu` with a second incoming cut that can represent the missing anti-phase or maturity direction; chronology alone does not supply it. The present result supports a three-band parent-coordinate description, not a neutrino-release timestamp or a uniquely moving R3 branch.",
            },
            {
                "id": "questions",
                "type": "markdown",
                "body": "## Further questions\n\n- Does R2's excess chronological displacement replicate in a fresh run?\n- Does a spin/polarization-sensitive second axis convert one of these vertical bands into a coherent Di-ARA path?\n- Which part of the band structure survives detector-topology matching or calibration transfer?\n- Does the marked R3 crest strengthen when the same-scale anti-phase is observed rather than inferred?",
            },
        ],
        "charts": [
            {
                "id": "ridge_track",
                "title": "Resolved parent-coordinate ridge centres across chronological blocks",
                "subtitle": "R1 and R2 use frozen broad zones; marked R3 uses the post-hoc strictly interior crest and leaves gaps where unresolved.",
                "type": "line",
                "dataset": "ridge_track",
                "sourceId": "t409_report_track",
                "palette": {"kind": "categorical", "name": "blue-gold-pink"},
                "encodings": {
                    "x": {"field": "global_block", "type": "quantitative", "label": "Chronological block (1–12)"},
                    "y": {"field": "centre", "type": "quantitative", "label": "Resolved centre on x_mu"},
                    "color": {"field": "ridge", "type": "nominal", "label": "Ridge"},
                    "tooltip": [
                        {"field": "block_label", "type": "nominal", "label": "Block"},
                        {"field": "events_in_zone", "type": "quantitative", "label": "Events in zone"},
                        {"field": "peak_to_median", "type": "quantitative", "label": "Peak/median density"},
                        {"field": "estimator", "type": "nominal", "label": "Estimator"},
                    ],
                },
            },
            {
                "id": "motion_control",
                "title": "Chronological motion against shuffled-order controls",
                "subtitle": "Observed M must exceed shuffled movement to support chronological travel; marked R3 remains below both null thresholds.",
                "type": "bar",
                "dataset": "motion",
                "sourceId": "t409_report_motion",
                "palette": {"kind": "categorical", "name": "blue-gold"},
                "options": {"orientation": "vertical", "grouping": "grouped"},
                "encodings": {
                    "x": {"field": "ridge", "type": "nominal", "label": "Ridge"},
                    "y": {"field": "motion_M", "type": "quantitative", "label": "Motion M (ARA units)"},
                    "color": {"field": "comparison", "type": "nominal", "label": "Observed or shuffled control"},
                    "tooltip": [
                        {"field": "global_p", "type": "quantitative", "label": "Global shuffle p"},
                        {"field": "within_run_p", "type": "quantitative", "label": "Within-run shuffle p"},
                        {"field": "resolved_blocks", "type": "quantitative", "label": "Resolved blocks"},
                    ],
                },
            },
            {
                "id": "ridge_occupancy",
                "title": "Events inside each recovered non-pole coordinate zone",
                "subtitle": "The marked upper crest is present but much less populated than the two dominant bands.",
                "type": "bar",
                "dataset": "occupancy",
                "sourceId": "t409_report_occupancy",
                "palette": {"kind": "categorical", "name": "blue-gold-pink"},
                "options": {"orientation": "vertical", "grouping": "grouped"},
                "encodings": {
                    "x": {"field": "ridge", "type": "nominal", "label": "Recovered ridge"},
                    "y": {"field": "events", "type": "quantitative", "label": "Events in zone"},
                    "tooltip": [
                        {"field": "centre", "type": "quantitative", "label": "Pooled centre"},
                        {"field": "share_nonpole", "type": "quantitative", "label": "Share of non-pole coordinates"},
                        {"field": "resolved_blocks", "type": "quantitative", "label": "Resolved blocks"},
                        {"field": "method_status", "type": "nominal", "label": "Method status"},
                    ],
                },
            },
        ],
        "tables": [
            {
                "id": "ridge_summary",
                "title": "Recovered ridge summary",
                "subtitle": "Centres, occupancy, chronological motion and method status for the two frozen bands and repaired marked crest.",
                "dataset": "ridge_summary",
                "sourceId": "t409_report_summary",
                "defaultSort": {"field": "centre", "direction": "asc"},
                "columns": [
                    {"field": "ridge", "label": "Ridge", "type": "text"},
                    {"field": "zone", "label": "Search zone", "type": "text"},
                    {"field": "centre", "label": "Centre", "type": "number"},
                    {"field": "events", "label": "Events", "type": "number"},
                    {"field": "share_nonpole", "label": "Share of non-pole", "type": "percent"},
                    {"field": "resolved_blocks", "label": "Resolved blocks", "type": "number"},
                    {"field": "motion_M", "label": "Motion M", "type": "number"},
                    {"field": "global_p", "label": "Global shuffle p", "type": "number"},
                    {"field": "reading", "label": "Reading", "type": "text"},
                    {"field": "method_status", "label": "Method status", "type": "text"},
                ],
            },
            {
                "id": "gate_table",
                "title": "Frozen gates and edge-capture repair",
                "subtitle": "The broad R3 gate result is retained, but its boundary centre prevents it from answering the marked-line question.",
                "dataset": "gates",
                "sourceId": "t409_report_gates",
                "defaultSort": {"field": "gate", "direction": "asc"},
                "columns": [
                    {"field": "gate", "label": "Gate", "type": "text"},
                    {"field": "status", "label": "Status", "type": "text"},
                ],
            },
            {
                "id": "validation_table",
                "title": "Independent saved-output validation",
                "subtitle": "Direct-density and saved-block arithmetic checks all passed; permutation arrays were not independently replayed.",
                "dataset": "validation",
                "sourceId": "t409_report_validation",
                "defaultSort": {"field": "validator", "direction": "asc"},
                "columns": [
                    {"field": "validator", "label": "Validator", "type": "text"},
                    {"field": "status", "label": "Status", "type": "text"},
                    {"field": "checks", "label": "Checks", "type": "number"},
                    {"field": "passed", "label": "Passed", "type": "number"},
                    {"field": "boundary", "label": "Boundary", "type": "text"},
                ],
            },
        ],
    }

    artifact = {
        "surface": "report",
        "manifest": manifest,
        "snapshot": {
            "version": 1,
            "status": "ready",
            "generatedAt": manifest["generatedAt"],
            "datasets": {
                "ridge_track": track,
                "motion": motion,
                "occupancy": occupancy,
                "ridge_summary": summaries,
                "gates": gates,
                "validation": validation_rows,
            },
            "accessIssues": [],
        },
        "sources": sources,
        "package_info": {
            "artifact_name": "T409 chronological parent ridge tracking",
            "artifact_version": "1.0.0",
            "delivery": "mcp-app",
        },
    }
    (HERE / "artifact.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(json.dumps({"artifact": str(HERE / 'artifact.json'), "datasets": {k: len(v) for k, v in artifact['snapshot']['datasets'].items()}}, indent=2))


if __name__ == "__main__":
    main()

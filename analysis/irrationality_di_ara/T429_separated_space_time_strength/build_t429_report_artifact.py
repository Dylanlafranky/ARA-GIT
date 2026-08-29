from __future__ import annotations

import json
import pathlib
import sqlite3

import pandas as pd


ROOT = pathlib.Path(__file__).resolve().parent
RESULTS = ROOT / "results"
OUT = ROOT / "T429_REPORT_ARTIFACT.json"


def records(frame: pd.DataFrame) -> list[dict[str, object]]:
    return json.loads(frame.to_json(orient="records"))


def main() -> None:
    summary = pd.read_csv(RESULTS / "T429_HOLDOUT_SUMMARY.csv")
    histories = pd.read_csv(RESULTS / "T429_HOLDOUT_MODEL_FREE_HISTORIES.csv")
    crosswalk = pd.read_csv(RESULTS / "T429_HOLDOUT_PHYSICS_CROSSWALK.csv")
    gates = json.loads((RESULTS / "T429_HOLDOUT_GATES.json").read_text(encoding="utf-8"))

    gate_rows = [
        {"gate": "Time trend", "passes": gates["gate_1_time_trend"], "required": 4, "events": 5},
        {"gate": "Space trend", "passes": gates["gate_2_space_trend"], "required": 4, "events": 5},
        {"gate": "Late both", "passes": gates["gate_3_late_both"], "required": 4, "events": 5},
        {"gate": "Space vs binding", "passes": gates["gate_4_space_binding"], "required": 4, "events": 5},
        {"gate": "Detector agreement", "passes": gates["gate_5_matched_agreement"], "required": 4, "events": 5},
    ]
    # Deterministic thinning preserves chronological coverage and stays bounded.
    sampled = []
    for event, group in histories.sort_values(["event", "time_s"]).groupby("event"):
        part = group.iloc[::max(1, len(group)//50)].copy()
        part["event"] = event
        sampled.append(part)
    path_rows = pd.concat(sampled, ignore_index=True)
    path_rows = path_rows.merge(
        crosswalk[["event", "time_s", "binding_proxy", "separation_km", "inspiral_tau_s"]],
        on=["event", "time_s"], how="left",
    )
    summary_rows = summary.copy()
    summary_rows["time_pass"] = (summary_rows.time_rho > 0) & (summary_rows.time_shift_p <= .05)
    summary_rows["space_pass"] = (summary_rows.space_rho > 0) & (summary_rows.space_shift_p <= .05)
    summary_rows["binding_pass"] = (summary_rows.space_binding_rho > 0) & (summary_rows.space_binding_shift_p <= .05)

    con = sqlite3.connect(":memory:")
    pd.DataFrame(gate_rows).to_sql("gate_results", con, index=False)
    path_rows.to_sql("path_samples", con, index=False)
    summary_rows.to_sql("event_summary", con, index=False)
    sql_gate = "SELECT gate, passes, required, events FROM gate_results ORDER BY rowid"
    sql_path = "SELECT event, role, time_s, T_frequency, T_chirp, S_amount, S_agreement, T_A, S_B, frequency_hz, binding_proxy, separation_km, inspiral_tau_s FROM path_samples ORDER BY event, time_s"
    sql_summary = "SELECT event, time_rho, time_shift_p, space_rho, space_shift_p, late_time_off_pct, late_space_off_pct, space_binding_rho, space_binding_shift_p, lag_ms, network_snr, time_pass, space_pass, binding_pass FROM event_summary ORDER BY event"
    gate_data = pd.read_sql_query(sql_gate, con)
    path_data = pd.read_sql_query(sql_path, con)
    summary_data = pd.read_sql_query(sql_summary, con)
    con.close()

    source_analysis = {
        "id": "t429-analysis",
        "label": "T429 frozen ARA analysis",
        "path": "analysis/irrationality_di_ara/T429_separated_space_time_strength",
    }
    source_gwosc = {
        "id": "gwosc-gwtc1",
        "label": "GWOSC GWTC-1 event records",
        "href": "https://gwosc.org/GWTC-1/",
    }
    source_gate = {
        "id": "t429-gates",
        "label": "T429 frozen gate result query",
        "query": {"engine": "SQLite", "language": "sql", "sql": sql_gate, "description": "Return all five frozen holdout gates and their required replication count.", "tables_used": ["gate_results"], "metric_definitions": ["passes is the number of five untouched holdouts meeting the frozen gate; required is four."]},
    }
    source_path = {
        "id": "t429-paths",
        "label": "T429 reviewed ARA path sample query",
        "query": {"engine": "SQLite", "language": "sql", "sql": sql_path, "description": "Return a deterministic chronological sample of each holdout's separated ARA path and adjacent physics crosswalk measures.", "tables_used": ["path_samples"], "filters": ["approximately 50 evenly spaced rows per event for bounded display"]},
    }
    source_summary = {
        "id": "t429-summary",
        "label": "T429 holdout score query",
        "query": {"engine": "SQLite", "language": "sql", "sql": sql_summary, "description": "Return the frozen per-event trend, off-source, detector-agreement and binding-crosswalk scores.", "tables_used": ["event_summary"], "metric_definitions": ["rho is Spearman rank correlation.", "p is the one-sided circular block-shift control probability."]},
    }

    title = "T429 — Separated Space/Time Strain and Gravitational Strength"
    manifest = {
        "version": 1,
        "surface": "report",
        "title": title,
        "description": "Frozen ARA test on five public binary-black-hole strain holdouts.",
        "generatedAt": "2026-08-24T00:00:00+10:00",
        "sources": [source_analysis, source_gwosc, source_gate, source_path, source_summary],
        "charts": [
            {"id": "chart-gates", "title": "Frozen holdout gates", "subtitle": "Number of five holdouts passing each gate; four were required.", "type": "bar", "dataset": "gate_results", "sourceId": "t429-gates", "encodings": {"x": {"field": "gate", "type": "nominal", "label": "Gate"}, "y": {"field": "passes", "type": "quantitative", "label": "Passing holdouts", "unit": "events"}}, "layout": "full"},
            {"id": "chart-path", "title": "Separated time-facing and space-facing ARA paths", "subtitle": "Chronological samples from each holdout on independent 0–2 coordinates.", "type": "scatter", "dataset": "path_samples", "sourceId": "t429-paths", "encodings": {"x": {"field": "T_A", "type": "quantitative", "label": "T_A movement", "unit": "0–2"}, "y": {"field": "S_B", "type": "quantitative", "label": "S_B connection", "unit": "0–2"}, "color": {"field": "event", "type": "nominal", "label": "Event"}, "tooltip": [{"field": "event", "type": "text"}, {"field": "time_s", "type": "quantitative", "label": "Seconds to event"}, {"field": "frequency_hz", "type": "quantitative", "label": "Centroid frequency", "unit": "Hz"}, {"field": "binding_proxy", "type": "quantitative", "label": "Binding proxy"}]}, "layout": "full", "maxRows": 1000},
            {"id": "chart-binding", "title": "Space/connection association with the binding proxy", "subtitle": "Spearman correlation by holdout; only GW170814 passed its block-shift control.", "type": "bar", "dataset": "event_summary", "sourceId": "t429-summary", "encodings": {"x": {"field": "event", "type": "nominal", "label": "Event"}, "y": {"field": "space_binding_rho", "type": "quantitative", "label": "Spearman rho"}}, "layout": "full"},
        ],
        "tables": [
            {"id": "table-events", "title": "Holdout scorecard", "subtitle": "Frozen trend, off-source and crosswalk statistics.", "dataset": "event_summary", "sourceId": "t429-summary", "defaultSort": {"field": "event", "direction": "asc"}, "density": "dense", "layout": "full", "columns": [
                {"field": "event", "label": "Event", "type": "text"},
                {"field": "time_rho", "label": "Time rho", "format": "number"},
                {"field": "time_shift_p", "label": "Time p", "format": "number"},
                {"field": "space_rho", "label": "Space rho", "format": "number"},
                {"field": "space_shift_p", "label": "Space p", "format": "number"},
                {"field": "late_time_off_pct", "label": "Late T percentile", "format": "percent"},
                {"field": "late_space_off_pct", "label": "Late S percentile", "format": "percent"},
                {"field": "space_binding_rho", "label": "S vs binding rho", "format": "number"},
                {"field": "space_binding_shift_p", "label": "Binding p", "format": "number"},
                {"field": "lag_ms", "label": "H1/L1 lag (ms)", "format": "number"},
                {"field": "network_snr", "label": "Network SNR", "format": "number"},
            ]},
        ],
        "blocks": [
            {"id": "title", "type": "markdown", "body": f"# {title}"},
            {"id": "summary", "type": "markdown", "sourceId": "t429-analysis", "body": "## Executive Summary\n\n**The frozen separated cut failed its universal claim.** None of the five primary gates reached the required four-of-five replication threshold. Separating phase/frequency from amount/agreement was still the right methodological correction, but a broad model-free 1.25-second window did not isolate the weak source wave from detector noise.\n\n**One event remains useful:** GW170814 alone linked the independently constructed space/connection coordinate to the established-physics binding proxy (rho 0.286; circular-block p 0.0005). That is an event-specific lead, not replication."},
            {"id": "tested", "type": "markdown", "body": "## What Was Tested\n\n**Who/where:** each binary-black-hole event was kept as its own identity; H1 and L1 were independent detector views. **What:** `T_A` used centroid frequency plus positive chirp-rate only; `S_B` used received spectral amount plus H1/L1 amount agreement only. **When:** -1.25 to -0.03 seconds before the published event time. **Why:** to test whether the earlier cut had mixed two leading-side observables. **How:** every feature was separately projected to 0–2 from off-source data, with no complement or sum-to-two constraint."},
            {"id": "gate-heading", "type": "markdown", "body": "## Frozen Result"},
            {"id": "gate-chart", "type": "chart", "chartId": "chart-gates"},
            {"id": "path-heading", "type": "markdown", "body": "## ARA Reading\n\nThe holdout paths occupy structured regions of the two-axis plane, but chronology is not consistent: time-facing maturity passed 0/5 and space-facing maturity passed 0/5. Therefore this is **not** evidence of the requested universal opening/closing handover. It also means the T427 shape cannot be rescued simply by calling one mixed axis Space and the other Time."},
            {"id": "path-chart", "type": "chart", "chartId": "chart-path"},
            {"id": "strength-heading", "type": "markdown", "body": "## Gravitational Strength Crosswalk\n\n**Received strength** is calibrated strain at the detector and includes distance, orientation, antenna response and noise. **Source coupling** is inferred from GWOSC masses/redshift and the measured frequency through standard separation and binding proxies. The source parameters were loaded only after the model-free histories were written, so they could compare with—but not construct—the ARA path."},
            {"id": "binding-chart", "type": "chart", "chartId": "chart-binding"},
            {"id": "event-table", "type": "table", "tableId": "table-events"},
            {"id": "next", "type": "markdown", "body": "## Best Next Test\n\nUse GW170814 as development only and freeze a short coherent H1/L1/V1 excess-power ridge around an independent native strain landmark. Construct Time from ridge phase/frequency and Space from coherent network amplitude, then score identically placed off-source and wrong-event windows. This preserves the ARA question while moving to the scale where the source is actually visible; it must remain a new test so T429's failure stays frozen."},
            {"id": "boundary", "type": "markdown", "body": "## Claim Boundary\n\nA pass would have supported a reproducible event-locked relational instrument, not a blind merger forecast or proof that ARA generates gravity. The observed failure rejects this projection only. The event-specific GW170814 association is exploratory until an untouched event reproduces it."},
        ],
    }
    snapshot = {
        "version": 1,
        "generatedAt": "2026-08-24T00:00:00+10:00",
        "status": "ready",
        "datasets": {
            "headline": [{"gates_met": 0, "gates_total": 5, "holdouts": 5, "binding_passes": 1, "binding_required": 4}],
            "gate_results": records(gate_data),
            "path_samples": records(path_data),
            "event_summary": records(summary_data),
        },
    }
    payload = {"surface": "report", "manifest": manifest, "snapshot": snapshot, "sources": [source_analysis, source_gwosc, source_gate, source_path, source_summary]}
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(OUT)
    print(f"path rows: {len(path_rows)}")


if __name__ == "__main__":
    main()

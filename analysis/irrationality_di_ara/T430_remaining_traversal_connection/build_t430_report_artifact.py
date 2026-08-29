from __future__ import annotations

import json
import pathlib
import sqlite3

import pandas as pd


ROOT = pathlib.Path(__file__).resolve().parent
RESULTS = ROOT / "results"
OUT = ROOT / "T430_REPORT_ARTIFACT.json"


def records(frame: pd.DataFrame) -> list[dict[str, object]]:
    return json.loads(frame.to_json(orient="records"))


def main() -> None:
    summary = pd.read_csv(RESULTS / "T430_CONFIRMATION_SUMMARY.csv")
    histories = pd.read_csv(RESULTS / "T430_CONFIRMATION_HISTORIES.csv")
    controls = pd.read_csv(RESULTS / "T430_CONFIRMATION_OFFSOURCE_CONTROLS.csv")
    gates = json.loads((RESULTS / "T430_CONFIRMATION_GATES.json").read_text(encoding="utf-8"))

    gate_rows = [
        {"gate": "Inverse gradient", "passes": gates["gate_1_inverse_gradient_count"], "required": 3, "events": 4},
        {"gate": "Residual vs control", "passes": gates["gate_2_residual_control_count"], "required": 3, "events": 4},
        {"gate": "Connection growth", "passes": gates["gate_3_connection_growth_count"], "required": 3, "events": 4},
        {"gate": "Closure occupancy", "passes": gates["gate_4_closure_occupancy_count"], "required": 3, "events": 4},
        {"gate": "Detector agreement", "passes": gates["gate_5_detector_agreement_count"], "required": 3, "events": 4},
    ]
    sampled = []
    for event, group in histories.sort_values(["event", "time_s"]).groupby("event"):
        part = group.iloc[::max(1, len(group) // 40)].copy()
        part["event"] = event
        sampled.append(part)
    path_rows = pd.concat(sampled, ignore_index=True)

    comparisons = []
    for _, row in summary.iterrows():
        off = controls.loc[controls.event == row.event]
        comparisons.extend([
            {"event": row.event, "series": "event", "median_residual": row.median_te_ara_residual, "closure_occupancy": row.closure_occupancy},
            {"event": row.event, "series": "off-source median", "median_residual": off.median_te_ara_residual.median(), "closure_occupancy": off.closure_occupancy.median()},
        ])
    comparisons = pd.DataFrame(comparisons)

    summary = summary.copy()
    summary["inverse_pass"] = (summary.inverse_rho <= -.30) & (summary.inverse_shift_p <= .05)
    summary["closure_control_pass"] = summary.residual_offsource_percentile <= .10
    summary["agreement_pass"] = (summary.detector_connection_rho > 0) & (summary.detector_connection_shift_p <= .05)

    con = sqlite3.connect(":memory:")
    pd.DataFrame(gate_rows).to_sql("gate_results", con, index=False)
    path_rows.to_sql("ara_path_samples", con, index=False)
    comparisons.to_sql("control_comparison", con, index=False)
    summary.to_sql("event_summary", con, index=False)
    sql_gate = "SELECT gate, passes, required, events FROM gate_results ORDER BY rowid"
    sql_path = "SELECT event, time_s, M_rem, C_acc, TE_ARA_sum, TE_ARA_residual, C_amount, C_density, local_period_ARA, frequency_hz FROM ara_path_samples ORDER BY event, time_s"
    sql_control = "SELECT event, series, median_residual, closure_occupancy FROM control_comparison ORDER BY event, series"
    sql_summary = "SELECT event, inverse_rho, inverse_shift_p, connection_time_rho, connection_time_shift_p, median_te_ara_residual, residual_offsource_percentile, closure_occupancy, occupancy_offsource_percentile, detector_connection_rho, detector_connection_shift_p, inverse_pass, closure_control_pass, agreement_pass FROM event_summary ORDER BY event"
    gate_data = pd.read_sql_query(sql_gate, con)
    path_data = pd.read_sql_query(sql_path, con)
    control_data = pd.read_sql_query(sql_control, con)
    summary_data = pd.read_sql_query(sql_summary, con)
    con.close()

    sources = [
        {"id": "t430-analysis", "label": "T430 frozen ARA analysis", "path": "analysis/irrationality_di_ara/T430_remaining_traversal_connection"},
        {"id": "gwosc-gwtc1", "label": "GWOSC GWTC-1 public event records", "href": "https://gwosc.org/GWTC-1/"},
        {"id": "t430-gates", "label": "T430 frozen gate query", "query": {"engine": "SQLite", "language": "sql", "sql": sql_gate, "description": "Return all five frozen confirmation gates and the required three-of-four count.", "tables_used": ["gate_results"], "metric_definitions": ["passes is the number of four untouched confirmation events meeting the frozen gate; required is three."]}},
        {"id": "t430-paths", "label": "T430 reviewed path sample query", "query": {"engine": "SQLite", "language": "sql", "sql": sql_path, "description": "Return deterministic chronological samples of remaining traversal and independently measured connection-facing state.", "tables_used": ["ara_path_samples"], "filters": ["approximately 40 evenly spaced rows per event"]}},
        {"id": "t430-controls", "label": "T430 matched off-source comparison query", "query": {"engine": "SQLite", "language": "sql", "sql": sql_control, "description": "Compare event-window closure statistics with each event's matched-duration off-source median.", "tables_used": ["control_comparison"], "metric_definitions": ["median_residual is median absolute deviation of M_rem+C_acc from 2.", "closure_occupancy is the fraction with absolute residual at most 0.50."]}},
        {"id": "t430-summary", "label": "T430 exact event score query", "query": {"engine": "SQLite", "language": "sql", "sql": sql_summary, "description": "Return the frozen per-event inverse-gradient, closure and detector-agreement scores.", "tables_used": ["event_summary"], "metric_definitions": ["rho is Spearman rank correlation.", "p is a one-sided circular-shift probability."]}},
    ]

    title = "T430 — Remaining Traversal and Connection-Facing State"
    manifest = {
        "version": 1,
        "surface": "report",
        "title": title,
        "description": "Frozen inverse-gradient ARA test on four previously unseen binary-black-hole strain events.",
        "generatedAt": "2026-08-24T00:00:00+10:00",
        "sources": sources,
        "charts": [
            {"id": "chart-gates", "title": "Frozen confirmation gates", "subtitle": "Passing events out of four; three were required for every gate.", "type": "bar", "dataset": "gate_results", "sourceId": "t430-gates", "encodings": {"x": {"field": "gate", "type": "nominal", "label": "Gate"}, "y": {"field": "passes", "type": "quantitative", "label": "Passing events", "unit": "events"}}, "layout": "full"},
            {"id": "chart-path", "title": "Remaining traversal and connection-facing state", "subtitle": "Chronological samples from four untouched events; the pure TE-ARA shore would run from (2,0) to (0,2).", "type": "scatter", "dataset": "path_samples", "sourceId": "t430-paths", "encodings": {"x": {"field": "M_rem", "type": "quantitative", "label": "Remaining traversal", "unit": "0–2"}, "y": {"field": "C_acc", "type": "quantitative", "label": "Connection-facing state", "unit": "0–2"}, "color": {"field": "event", "type": "nominal", "label": "Event"}, "tooltip": [{"field": "event", "type": "text"}, {"field": "time_s", "type": "quantitative", "label": "Seconds to event"}, {"field": "TE_ARA_sum", "type": "quantitative", "label": "M+C"}, {"field": "TE_ARA_residual", "type": "quantitative", "label": "Closure residual"}]}, "layout": "full", "maxRows": 1000},
            {"id": "chart-residual", "title": "Event and off-source TE-ARA residual", "subtitle": "Event windows did not show uniquely smaller closure residuals.", "type": "bar", "dataset": "control_comparison", "sourceId": "t430-controls", "encodings": {"x": {"field": "event", "type": "nominal", "label": "Event"}, "y": {"field": "median_residual", "type": "quantitative", "label": "Median absolute residual"}, "color": {"field": "series", "type": "nominal", "label": "Window type"}}, "options": {"grouping": "grouped"}, "layout": "full"},
        ],
        "tables": [
            {"id": "table-events", "title": "Untouched event scorecard", "subtitle": "Exact frozen metrics; all event gates were false.", "dataset": "event_summary", "sourceId": "t430-summary", "defaultSort": {"field": "event", "direction": "asc"}, "density": "dense", "layout": "full", "columns": [
                {"field": "event", "label": "Event", "type": "text"},
                {"field": "inverse_rho", "label": "Inverse rho", "format": "number"},
                {"field": "inverse_shift_p", "label": "Inverse p", "format": "number"},
                {"field": "median_te_ara_residual", "label": "Median residual", "format": "number"},
                {"field": "residual_offsource_percentile", "label": "Residual control pct", "format": "percent"},
                {"field": "closure_occupancy", "label": "Closure occupancy", "format": "percent"},
                {"field": "occupancy_offsource_percentile", "label": "Occupancy control pct", "format": "percent"},
                {"field": "detector_connection_rho", "label": "H1/L1 rho", "format": "number"},
                {"field": "detector_connection_shift_p", "label": "H1/L1 p", "format": "number"},
            ]},
        ],
        "blocks": [
            {"id": "title", "type": "markdown", "body": f"# {title}"},
            {"id": "technical-summary", "type": "markdown", "body": "## Technical Summary\n\n**The frozen T430 construction was not supported.** Zero of four untouched events passed any of the five prespecified gates. The correction from T429 was conceptually necessary—remaining traversal was separated from connection-facing state—but the chosen strain features did not recover a shared, event-specific inverse gradient."},
            {"id": "findings", "type": "markdown", "body": "## Findings\n\nMedian `M_rem+C_acc` values were near 2 (1.87–2.04), but this is not independent closure evidence: `M_rem` is window-normalized around a midpoint of 1 and the empirical-CDF connection features are centered near 1. Matched off-source windows were at least as closed. The event inverse correlations ranged from −0.068 to +0.296 and none beat its temporal-shift control."},
            {"id": "gates", "type": "chart", "chartId": "chart-gates"},
            {"id": "definitions", "type": "markdown", "body": "## Definitions\n\n`M_rem` is the phase-cycle budget still present between each sample and the frozen endpoint, oriented 2→0. `C_acc` is the frozen name for the mean of spectral amount and spectral concentration, each mapped independently from off-source data. Importantly, `C_acc` is an instantaneous connection-facing state—not a cumulative integral."},
            {"id": "path", "type": "chart", "chartId": "chart-path"},
            {"id": "methodology", "type": "markdown", "body": "## Methodology\n\nEach event remained its own identity. H1 and L1 were independent observations, aligned only within ±8 ms. The primary interval was −0.50 to −0.03 s with a 64 ms STFT and 4 ms hop. Four GWTC-1 events absent from T427–T429 were held untouched until the protocol and hash were frozen. Every event comparison used 66 equal-duration off-source windows plus circular-shift controls."},
            {"id": "residual", "type": "chart", "chartId": "chart-residual"},
            {"id": "scorecard", "type": "table", "tableId": "table-events"},
            {"id": "limitations", "type": "markdown", "body": "## Limitations and Robustness\n\nTwo frozen gates are rank-redundant: because `M_rem` is strictly decreasing, rho(`M_rem`,`C_acc`) is exactly the negative of rho(time,`C_acc`). They must be treated as one underlying ordering result. H1/L1 connection histories also failed to replicate, suggesting that per-frame amount/concentration at this weak-signal scale is dominated by detector-specific structure. The official event time defines the endpoint, so the test is retrospective."},
            {"id": "next", "type": "markdown", "body": "## Next Steps\n\nDo not move the current goalposts. T430 remains failed. A new test should distinguish two alternatives before running: (1) **state gradient**—compare remaining traversal with the instantaneous connection child using a coherently reconstructed source signal; or (2) **stored accumulation**—define a genuinely causal cumulative connection budget and freeze how it is normalized. The latter is closer to the word ‘accumulation’ but is a different instrument."},
            {"id": "questions", "type": "markdown", "body": "## Open Questions\n\nIs connection meant to be the instantaneous density at each time slice, or the stored total built across prior slices? Is the relevant ARA identity the binary system, the detector-visible coherent mode, or a shorter child near merger? Those choices change the relational cut and must be named before another validation set is opened."},
        ],
    }
    snapshot = {
        "version": 1,
        "generatedAt": "2026-08-24T00:00:00+10:00",
        "status": "ready",
        "datasets": {
            "gate_results": records(gate_data),
            "path_samples": records(path_data),
            "control_comparison": records(control_data),
            "event_summary": records(summary_data),
        },
    }
    payload = {"surface": "report", "manifest": manifest, "snapshot": snapshot, "sources": sources}
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(OUT)
    print(f"path rows: {len(path_data)}")


if __name__ == "__main__":
    main()

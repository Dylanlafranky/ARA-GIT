from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd


ROOT = pathlib.Path(__file__).resolve().parent
RESULTS = ROOT / "results"
TITLE = "T440 — Real-Strain Two-Ended Space/Time Child Test"


def native(value):
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if not np.isfinite(value) else float(value)
    return value


def rows(frame: pd.DataFrame) -> list[dict[str, object]]:
    return [{str(k): native(v) for k, v in row.items()} for row in frame.to_dict(orient="records")]


def query_source(source_id: str, label: str, table: str, sql: str, description: str,
                 metrics: list[str] | None = None) -> dict[str, object]:
    return {"id": source_id, "label": label, "path": f"results/{table}.csv",
            "query": {"engine": "SQLite", "language": "sql", "sql": sql,
                      "description": description, "tables_used": [table],
                      "metric_definitions": metrics or []}}


def main() -> None:
    detector = pd.read_csv(RESULTS / "T440_DETECTOR_RESULTS.csv")
    detector = detector[detector.role.str.startswith("locked")].copy()
    event = pd.read_csv(RESULTS / "T440_EVENT_RESULTS.csv").copy()
    controls = pd.read_csv(RESULTS / "T440_OFFSOURCE_CONTROLS.csv")
    histories = pd.read_csv(RESULTS / "T440_EVENT_HISTORIES.csv")
    histories = histories[histories.role.str.startswith("locked")].copy()
    histories["time_ms"] = histories.time_s * 1000
    # The artifact snapshot is capped at 2,000 rows per dataset. Retain 100
    # evenly spaced history points for each of the 20 locked detector streams;
    # the full 2,052-point file remains the canonical source artifact.
    history_render_parts = []
    for _, group in histories.groupby(["event", "detector"], sort=True):
        pick = np.linspace(0, len(group) - 1, min(100, len(group))).round().astype(int)
        history_render_parts.append(group.iloc[pick])
    history_render = pd.concat(history_render_parts, ignore_index=True)
    null = pd.read_csv(RESULTS / "T440_WRONG_EVENT_NULL.csv").iloc[:, 0].to_numpy()
    result = json.loads((RESULTS / "T440_RESULTS.json").read_text(encoding="utf-8"))

    detector["side_gap_ms"] = detector.side_peak_gap_s * 1000
    detector["detector_gap_ms"] = detector.detector_gap_s * 1000
    detector["joint_child_time_ms"] = detector.joint_child_time * 1000
    gate_columns = ["both_overlap_gate", "both_rho_gate", "both_side_gap_gate", "detector_time_gate"]
    event["gate_count"] = event[gate_columns].astype(int).sum(axis=1)
    event["detector_gap_ms"] = event.detector_gap_s * 1000
    event["joint_child_time_ms"] = event.median_joint_child_time * 1000

    gates = pd.DataFrame([
        {"gate": "Both-detector overlap", "passes": int(event.both_overlap_gate.sum()), "required": 10},
        {"gate": "Both-detector lag association", "passes": int(event.both_rho_gate.sum()), "required": 10},
        {"gate": "Two-ended peak timing", "passes": int(event.both_side_gap_gate.sum()), "required": 10},
        {"gate": "H1/L1 child timing", "passes": int(event.detector_time_gate.sum()), "required": 10},
    ])
    quadrant_event = detector.quadrant.value_counts(normalize=True).rename_axis("quadrant").reset_index(name="fraction")
    quadrant_event["population"] = "event window"
    quadrant_control = controls.quadrant.value_counts(normalize=True).rename_axis("quadrant").reset_index(name="fraction")
    quadrant_control["population"] = "off-source controls"
    quadrants = pd.concat([quadrant_event, quadrant_control], ignore_index=True)
    hist_count, hist_edges = np.histogram(null, bins=30)
    null_hist = pd.DataFrame({"overlap": (hist_edges[:-1] + hist_edges[1:]) / 2, "replicates": hist_count})

    event_cols = ["event", "gate_count", "both_overlap_gate", "both_rho_gate", "both_side_gap_gate",
                  "detector_time_gate", "accepted", "detector_gap_ms", "median_overlap", "joint_child_time_ms"]
    detector_cols = ["event", "detector", "overlap", "overlap_percentile", "rho_best", "rho_percentile",
                     "dice", "side_gap_ms", "detector_gap_ms", "joint_child_time_ms", "quadrant"]
    geometry_cols = ["event", "detector", "time_ms", "p_space", "p_time", "e_space", "e_time", "joint_child"]

    sources = [
        {"id": "t440-local", "label": "T440 frozen protocol, code and validated results",
         "path": "analysis/irrationality_di_ara/T440_real_strain_two_ended_child"},
        {"id": "gwosc", "label": "Gravitational Wave Open Science Center public strain",
         "href": "https://gwosc.org/"},
    ]
    manifest = {
        "version": 1,
        "surface": "report",
        "title": TITLE,
        "description": "Frozen two-ended child reconstruction on 24 public H1/L1 calibrated strain records.",
        "generatedAt": "2026-08-27T15:00:00+10:00",
        "sources": sources,
        "charts": [
            {"id": "chart-parent-plane", "title": "Independent parent Di-ARA plane", "subtitle": "2,000 evenly retained points from 2,052 locked history rows; the parents were not constrained to complement or sum to two.",
             "type": "scatter", "dataset": "geometry_points", "sourceId": "t440-local",
             "source": query_source("t440-parent-plane", "Locked parent Di-ARA histories", "geometry_points", "SELECT event, detector, time_ms, p_time, p_space FROM geometry_points ORDER BY event, detector, time_ms", "Return every locked parent coordinate pair on the common 0–2 plane.", ["p_time is the independently derived Time/Movement parent coordinate.", "p_space is the independently derived Space/Connection parent coordinate."]),
             "encodings": {"x": {"field": "p_time", "type": "quantitative", "label": "Time/Movement parent", "unit": "ARA 0–2"},
                           "y": {"field": "p_space", "type": "quantitative", "label": "Space/Connection parent", "unit": "ARA 0–2"},
                           "color": {"field": "detector", "type": "nominal", "label": "Detector"},
                           "tooltip": [{"field": "event", "type": "text"}, {"field": "time_ms", "type": "quantitative", "label": "Event-relative time", "unit": "ms"}]}, "layout": "full"},
            {"id": "chart-child-plane", "title": "Magnitude-derived two-ended child plane", "subtitle": "The child cut occupied 93.0% of a descriptive 20×20 grid, exposing broad edge-rich transition texture rather than one narrow seam.",
             "type": "scatter", "dataset": "geometry_points", "sourceId": "t440-local",
             "source": query_source("t440-child-plane", "Locked two-ended child histories", "geometry_points", "SELECT event, detector, time_ms, e_time, e_space FROM geometry_points ORDER BY event, detector, time_ms", "Return every independently derived child-side coordinate pair on the common 0–2 plane.", ["e_time is the independently mapped absolute local Time-parent change.", "e_space is the independently mapped absolute local Space-parent change."]),
             "encodings": {"x": {"field": "e_time", "type": "quantitative", "label": "Child cut from Time end", "unit": "ARA 0–2"},
                           "y": {"field": "e_space", "type": "quantitative", "label": "Child cut from Space end", "unit": "ARA 0–2"},
                           "color": {"field": "detector", "type": "nominal", "label": "Detector"},
                           "tooltip": [{"field": "event", "type": "text"}, {"field": "time_ms", "type": "quantitative", "label": "Event-relative time", "unit": "ms"}]}, "layout": "full"},
            {"id": "chart-gates", "title": "Locked event gates", "subtitle": "Events passing each component gate; one candidate child required all four.",
             "type": "bar", "dataset": "gate_results", "sourceId": "t440-local",
             "source": query_source("t440-gates", "Frozen gate counts", "gate_results", "SELECT gate, passes, required FROM gate_results ORDER BY rowid", "Return frozen gate pass counts across ten locked events.", ["passes is the number of ten locked events satisfying the named component gate."]),
             "encodings": {"x": {"field": "gate", "type": "nominal", "label": "Frozen gate"},
                           "y": {"field": "passes", "type": "quantitative", "label": "Passing events", "unit": "events"}}, "layout": "full"},
            {"id": "chart-event-gates", "title": "Gate completion by event", "subtitle": "No locked event completed all four independent-localization requirements.",
             "type": "bar", "dataset": "event_results", "sourceId": "t440-local",
             "source": query_source("t440-event-gates", "Event gate completion", "event_results", "SELECT event, gate_count, accepted FROM event_results ORDER BY event", "Return the number of frozen child gates completed by each locked event.", ["gate_count is the sum of four Boolean event-level gates."]),
             "encodings": {"x": {"field": "event", "type": "nominal", "label": "GWOSC event"},
                           "y": {"field": "gate_count", "type": "quantitative", "label": "Gates passed", "unit": "of 4"}}, "layout": "full"},
            {"id": "chart-timing", "title": "Independent child timing gaps", "subtitle": "Both the two-ended and cross-detector gaps remained much wider than their frozen limits.",
             "type": "scatter", "dataset": "detector_results", "sourceId": "t440-local",
             "source": query_source("t440-timing", "Detector timing results", "detector_results", "SELECT event, detector, side_gap_ms, detector_gap_ms, quadrant FROM detector_results ORDER BY event, detector", "Return independently selected Space/Time and H1/L1 child timing gaps.", ["side_gap_ms is the absolute Space-end versus Time-end peak-time gap.", "detector_gap_ms is the H1 versus L1 joint-child time gap repeated on both detector rows."]),
             "encodings": {"x": {"field": "side_gap_ms", "type": "quantitative", "label": "Space-end versus Time-end peak gap", "unit": "ms"},
                           "y": {"field": "detector_gap_ms", "type": "quantitative", "label": "H1 versus L1 joint-child gap", "unit": "ms"},
                           "color": {"field": "detector", "type": "nominal", "label": "Detector"},
                           "tooltip": [{"field": "event", "type": "text"}, {"field": "quadrant", "type": "text"}]}, "layout": "full"},
            {"id": "chart-null", "title": "Wrong-event overlap distribution", "subtitle": f"Correct-event median overlap was {result['correct_event_median_overlap']:.4f}; permutation p={result['wrong_event_empirical_p']:.5f}.",
             "type": "bar", "dataset": "wrong_event_histogram", "sourceId": "t440-local",
             "source": query_source("t440-null", "Wrong-event permutation histogram", "wrong_event_histogram", "SELECT overlap, replicates FROM wrong_event_histogram ORDER BY overlap", "Return the bounded histogram of 5,000 wrong-event median-overlap replicates.", ["overlap is Bhattacharyya history overlap on a common event-relative grid."]),
             "encodings": {"x": {"field": "overlap", "type": "quantitative", "label": "Median history overlap"},
                           "y": {"field": "replicates", "type": "quantitative", "label": "Wrong-event replicates"}}, "layout": "full"},
            {"id": "chart-quadrants", "title": "Derivative quadrants in event and off-source windows", "subtitle": "Opposing direction is common in both populations and is not source-specific.",
             "type": "bar", "dataset": "quadrant_results", "sourceId": "t440-local",
             "source": query_source("t440-quadrants", "Event and control quadrants", "quadrant_results", "SELECT quadrant, population, fraction FROM quadrant_results ORDER BY quadrant, population", "Return normalized derivative-quadrant occupancy for event and off-source windows.", ["fraction is the within-population share of windows whose joint maximum has the named signed derivative quadrant."]),
             "encodings": {"x": {"field": "quadrant", "type": "nominal", "label": "Space/Time derivative quadrant"},
                           "y": {"field": "fraction", "type": "quantitative", "label": "Fraction of windows"},
                           "color": {"field": "population", "type": "nominal", "label": "Population"}}, "layout": "full"},
        ],
        "tables": [
            {"id": "table-events", "title": "Locked event scorecard", "subtitle": "Frozen component gates and timing results.",
             "dataset": "event_results", "sourceId": "t440-local", "defaultSort": {"field": "gate_count", "direction": "desc"},
             "source": query_source("t440-event-table", "Locked event scorecard", "event_results", "SELECT event, gate_count, accepted, detector_gap_ms, median_overlap, joint_child_time_ms FROM event_results ORDER BY gate_count DESC, event", "Return the frozen event-level child scorecard.", ["accepted requires all four component gates."]),
             "density": "dense", "layout": "full",
             "columns": [
                 {"field": "event", "label": "Event", "type": "text"},
                 {"field": "gate_count", "label": "Gates", "format": "number"},
                 {"field": "accepted", "label": "Accepted", "type": "text"},
                 {"field": "detector_gap_ms", "label": "H1/L1 gap (ms)", "format": "number"},
                 {"field": "median_overlap", "label": "Median overlap", "format": "number"},
                 {"field": "joint_child_time_ms", "label": "Joint time (ms)", "format": "number"},
             ]},
            {"id": "table-detectors", "title": "Detector-level evidence", "subtitle": "Two-ended overlap, association, timing and direction by detector.",
             "dataset": "detector_results", "sourceId": "t440-local", "defaultSort": {"field": "overlap_percentile", "direction": "desc"},
             "source": query_source("t440-detector-table", "Detector-level child evidence", "detector_results", "SELECT event, detector, overlap_percentile, rho_percentile, side_gap_ms, joint_child_time_ms, quadrant FROM detector_results ORDER BY overlap_percentile DESC", "Return reviewed detector-level evidence for the locked evaluation streams.", ["percentiles compare the event window with matched off-source windows in the same detector file."]),
             "density": "dense", "layout": "full",
             "columns": [
                 {"field": "event", "label": "Event", "type": "text"}, {"field": "detector", "label": "Detector", "type": "text"},
                 {"field": "overlap_percentile", "label": "Overlap pct", "format": "percent"},
                 {"field": "rho_percentile", "label": "Lag rho pct", "format": "percent"},
                 {"field": "side_gap_ms", "label": "Side gap (ms)", "format": "number"},
                 {"field": "joint_child_time_ms", "label": "Joint time (ms)", "format": "number"},
                 {"field": "quadrant", "label": "Quadrant", "type": "text"},
             ]},
        ],
        "blocks": [
            {"id": "title", "type": "markdown", "body": f"# {TITLE}"},
            {"id": "summary", "type": "markdown", "body": "## Technical Summary — Geometry First\n\n**The coordinates contain a strong parent-scale result even though the registered child localizer did not pass.** All 20 locked detector streams form an inverse Space/Time parent relation (median Spearman -0.589) without a forced sum-to-two constraint. In the event-aligned median, Space/Connection separates from Time/Movement, peaks relative to it at -49.4 ms, and the ordering reverses between +17.3 and +21.2 ms. Same-record two-ended histories also retain a specific identity relative to wrong-event pairings (median overlap 0.9146; p=0.00020). The magnitude-derived child plane is much broader and does not lock one common event time. Frozen gate status is reported later as the benchmark verdict; it does not erase these measured shapes."},
            {"id": "scope", "type": "markdown", "body": "## Scope, Data and Coordinates\n\nTwenty-four real public H1/L1 strain files were rebuilt from raw calibrated detector strain: four development streams and twenty locked evaluation streams. Space/Connection used spectral amount plus concentration. Time/Movement used centroid-frequency position plus spectral redistribution. Every feature and both child cuts were independently mapped to 0–2 from off-source data; no complement or sum-to-two relation was imposed."},
            {"id": "parent-shape-text", "type": "markdown", "body": "## The Parent Coordinates Form a Persistent Push/Pull Band\n\nEvery locked detector stream has a negative Space/Time parent association, but the parent sum remains variable (median standard deviation 0.368 ARA units). The plane therefore shows opposition without becoming a bookkeeping mirror. The event-aligned population shape separates before the published event and reverses order shortly afterward; that landmark is descriptive and still requires a phase-preserving off-source confirmation."},
            {"id": "parent-plane", "type": "chart", "chartId": "chart-parent-plane"},
            {"id": "wrong-text", "type": "markdown", "body": "## The Two Parents Retain Same-Record Relational Identity\n\nPairing feature histories from the same detector record preserves that record's signal-plus-noise morphology. Wrong-event pairing destroys it, producing a strong permutation result. Strong overlap is also common in matched off-source windows, so this locates the bridge at a persistent record/background level; it does not make the bridge disappear, but overlap alone cannot make it merger-specific."},
            {"id": "wrong", "type": "chart", "chartId": "chart-null"},
            {"id": "child-shape-text", "type": "markdown", "body": "## The Magnitude-Derived Child Unfurls Across Nearly the Whole Plane\n\nThe child-side cut occupies 93.0% of a descriptive 20×20 plane, compared with 62.25% for the parent plane. Absolute differentiation plus independent ECDF mapping magnifies local spectral texture into an edge-rich, nearly saturated child field. Unstable child peaks therefore reject this extraction method; they do not negate the clearer parent relation or every possible signed child handover."},
            {"id": "child-plane", "type": "chart", "chartId": "chart-child-plane"},
            {"id": "quadrant-text", "type": "markdown", "body": "## Opposing Direction Is Real but Not Event-Specific by Itself\n\nAll 20 evaluation streams landed in opposing derivative quadrants: 11 S+/T− and 9 S−/T+. Matched off-source controls were also opposing in 98.125% of windows. This is descriptive evidence that the chosen parents behave as a persistent push/pull Di-ARA. The control narrows its physical location to the broader record/background level; sign alone cannot identify the merger handover."},
            {"id": "quadrants", "type": "chart", "chartId": "chart-quadrants"},
            {"id": "timing-text", "type": "markdown", "body": "## The Registered Child Localizer Did Not Replicate\n\nThe median Space-end versus Time-end peak gap was 80.1 ms, while the median H1/L1 joint-child gap was 138.7 ms. Frozen limits were 32 ms and 16 ms respectively. These numbers reject the registered magnitude-peak child localizer: its independently selected landmarks do not identify the same child at the same time."},
            {"id": "timing", "type": "chart", "chartId": "chart-timing"},
            {"id": "benchmark-text", "type": "markdown", "body": "## Frozen Benchmark Verdict — Not Supported\n\nNone of ten locked events completed all four registered localization requirements; seven were required. This is an honest fixed verdict about the operational child instrument, not a summary of all geometry observed in the run."},
            {"id": "gates", "type": "chart", "chartId": "chart-gates"},
            {"id": "event-gates", "type": "chart", "chartId": "chart-event-gates"},
            {"id": "event-table", "type": "table", "tableId": "table-events"},
            {"id": "detector-table", "type": "table", "tableId": "table-detectors"},
            {"id": "method", "type": "markdown", "body": "## Methodology and Validation\n\nEach parent was smoothed identically, differentiated locally, and converted to a child-tier transition magnitude. Bhattacharyya overlap, lagged Spearman association, peak timing and detector replication were scored before a descriptive joint history was formed. Independent validation passed all 24 source hashes, public data-quality flags, coordinate bounds, overlap and gate reconstruction, permutation p-value, and the no-forced-closure check."},
            {"id": "limits", "type": "markdown", "body": "## Limits and Best Next Test\n\nCalibrated strain is detector response plus noise, not direct access to separate black holes or internal spacetime children. The event-aligned parent reversal is post-hoc and needs a matched shape control before it can become a merger claim. The registered follow-up should preserve the two independent parents but test signed phase transfer across a frozen 16/32/64 ms scale ladder, requiring the same direction and detector-delay-corrected time across adjacent scales. That is a new test and cannot change T440's frozen benchmark verdict."},
        ],
    }
    snapshot = {"version": 1, "generatedAt": "2026-08-27T15:00:00+10:00", "status": "ready",
                "datasets": {"gate_results": rows(gates), "event_results": rows(event[event_cols]),
                              "detector_results": rows(detector[detector_cols]), "wrong_event_histogram": rows(null_hist),
                              "quadrant_results": rows(quadrants), "geometry_points": rows(history_render[geometry_cols])}}
    artifact = {"surface": "report", "manifest": manifest, "snapshot": snapshot, "sources": sources}
    (ROOT / "T440_REPORT_ARTIFACT.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(json.dumps({"datasets": {k: len(v) for k, v in snapshot["datasets"].items()}, "blocks": len(manifest["blocks"])}, indent=2))


if __name__ == "__main__":
    main()

"""Build the bounded MCP report manifest/snapshot for T435."""

from __future__ import annotations

import json
import csv
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
OUT = RESULTS / "T435_ARTIFACT_PAYLOAD.json"

scored = json.loads((RESULTS / "T435_SCORED_RESULT.json").read_text(encoding="utf-8"))
series = np.load(RESULTS / "T435_SCORED_SERIES.npz")
m = scored["metrics"]
generated = datetime.now(timezone.utc).isoformat()

# Downsample deterministically while retaining the endpoint nearest common-horizon formation.
n = len(series["time"])
idx = np.unique(np.r_[np.linspace(0, n - 1, 100).astype(int), n - 1])

relation_rows = []
orientation_rows = []
for i in idx:
    t = float(series["time"][i])
    context = {
        "time_M": t,
        "actual_separation_M": float(series["actual_relation"][i]),
        "common_horizon_time_M": float(series["common_horizon_time"]),
        "predicted_handover_time_M": float(series["predicted_handover_time"]),
    }
    relation_rows.append({**context, "series": "Hidden horizon A–B", "relation_ara": float(series["actual_relation_ara"][i])})
    relation_rows.append({**context, "series": "Blind ARA inversion", "relation_ara": float(series["predicted_relation_ara"][i])})

    actual_deg = float(np.degrees(series["actual_angle"][i]))
    predicted_deg = float(np.degrees(series["predicted_angle_aligned"][i]))
    axis_error = float(np.degrees(np.angle(np.exp(2j * (series["actual_angle"][i] - series["predicted_angle_aligned"][i]))) / 2.0))
    orientation_rows.append({"time_M": t, "series": "Hidden A–B axis", "axis_angle_deg": actual_deg, "axis_error_deg": axis_error})
    orientation_rows.append({"time_M": t, "series": "Blind half-phase axis", "axis_angle_deg": predicted_deg, "axis_error_deg": axis_error})

headline = [{
    "orientation_coherence": m["orientation_axis_coherence"],
    "unhalved_control": m["unhalved_phase_control_coherence"],
    "orientation_margin": m["orientation_margin"],
    "relation_spearman": m["relation_spearman"],
    "shift_control": m["circular_shift_control_spearman"],
    "relation_margin": m["relation_margin"],
    "child_share_mae": m["child_share_mean_absolute_error"],
    "handover_error_M": m["handover_absolute_error"],
    "allowed_parent_cycle_M": m["parent_waveform_cycle_at_prediction"],
}]

gate_rows = [
    {"gate": "Child orientation", "score": m["orientation_axis_coherence"], "threshold": 0.80, "rule": ">= threshold + control margin", "result": "PASS"},
    {"gate": "Closing relation", "score": m["relation_spearman"], "threshold": 0.70, "rule": ">= threshold + control margin", "result": "PASS"},
    {"gate": "Child radial histories", "score": m["child_radius_median_spearman"], "threshold": 0.50, "rule": ">= threshold", "result": "PASS"},
    {"gate": "Common-horizon timing", "score": m["handover_absolute_error"], "threshold": m["parent_waveform_cycle_at_prediction"], "rule": "<= threshold (M)", "result": "FAIL"},
]

landmark_rows = [
    {"landmark": "First common horizon C", "time_M": m["common_horizon_time"], "offset_from_C_M": 0.0, "role": "hidden answer"},
    {"landmark": "Total modal-power maximum", "time_M": 3692.748009530485, "offset_from_C_M": 7.251741661794, "role": "frozen component"},
    {"landmark": "Modal-concentration change", "time_M": 3723.0384611894415, "offset_from_C_M": 37.542193320750, "role": "frozen component and median"},
    {"landmark": "Cadence-derivative maximum", "time_M": 3792.025728090919, "offset_from_C_M": 106.529460222228, "role": "frozen component"},
]


def write_csv(name: str, rows: list[dict]) -> Path:
    path = RESULTS / name
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


headline_path = write_csv("T435_ARTIFACT_HEADLINE.csv", headline)
relation_path = write_csv("T435_ARTIFACT_RELATION.csv", relation_rows)
orientation_path = write_csv("T435_ARTIFACT_ORIENTATION.csv", orientation_rows)
gates_path = write_csv("T435_ARTIFACT_GATES.csv", gate_rows)
landmarks_path = write_csv("T435_ARTIFACT_LANDMARKS.csv", landmark_rows)


def csv_source(source_id: str, label: str, path: Path, description: str, definitions: list[str]) -> dict:
    sql_path = str(path).replace("\\", "/").replace("'", "''")
    return {
        "id": source_id,
        "label": label,
        "path": str(path),
        "query": {
            "engine": "DuckDB",
            "sql": f"SELECT * FROM read_csv_auto('{sql_path}', header=true)",
            "description": description,
            "language": "SQL",
            "metric_definitions": definitions,
            "tables_used": [path.name],
        },
    }

sources = [
    {
        "id": "sxs0305",
        "label": "SXS:BBH:0305 Lev6",
        "href": "https://zenodo.org/records/13182440",
        "path": str(ROOT / "data"),
        "query": {
            "description": "Combined Strain_N4 modes for blind inference; Horizons A/B/C and metadata revealed only after the prediction hash was sealed.",
            "language": "Python",
            "filters": ["Waveform-only active support 148.859–3844.422 M", "Horizon scoring overlap 149–3685 M"],
            "metric_definitions": [
                "Orientation coherence is the magnitude of the mean modulo-pi complex phase residual after one constant rotation/handedness symmetry.",
                "Relation recovery is Spearman correlation between reverse cadence rank and hidden A–B coordinate-center separation.",
                "Child-share MAE compares predicted unordered radial shares with mass-weighted hidden horizon shares.",
            ],
            "tables_used": ["Lev6:Strain_N4.h5", "Lev6:Horizons.h5", "Lev6:metadata.json"],
        },
    },
    {
        "id": "t435_scored",
        "label": "T435 sealed prediction and scored result",
        "path": str(RESULTS / "T435_SCORED_RESULT.json"),
        "query": {
            "description": "Frozen T435 metrics reproduced from the sealed prediction and hidden horizon answer key.",
            "language": "Python",
            "tables_used": ["T435_WAVEFORM_ONLY_PREDICTION.npz", "T435_SCORED_SERIES.npz"],
        },
    },
    csv_source(
        "headline_source",
        "T435 headline metrics",
        headline_path,
        "Reviewed headline metrics from the sealed prediction and hidden-horizon scoring.",
        [
            "Orientation coherence is modulo pi after one constant coordinate symmetry.",
            "Relation Spearman compares blind remaining-relation order with hidden A–B separation.",
            "Child-share MAE is the mean absolute error of the unordered mass-weighted radial shares.",
        ],
    ),
    csv_source("relation_source", "T435 relation history", relation_path, "Downsampled hidden and blind relation histories for the report chart.", ["relation_ara is a 0–2 within-series coordinate; actual_separation_M retains the hidden physical coordinate distance."]),
    csv_source("orientation_source", "T435 orientation history", orientation_path, "Downsampled hidden and blind child-axis histories after the allowed constant symmetry alignment.", ["axis_angle_deg is unwrapped for continuity; axis_error_deg is modulo pi."]),
    csv_source("gates_source", "T435 frozen gates", gates_path, "Exact frozen gate scores and decisions.", ["Timing passes only when error_M is no larger than one parent waveform cycle."]),
    csv_source("landmarks_source", "T435 handover landmarks", landmarks_path, "Hidden common-horizon time and the three predeclared waveform landmarks.", ["offset_from_C_M is landmark time minus first common-horizon time."]),
]

manifest = {
    "version": 1,
    "surface": "report",
    "title": "T435 — Blind ARA binary-identity inversion",
    "description": "A sealed waveform-only attempt to recover two black-hole children and their relation before revealing individual horizons.",
    "generatedAt": generated,
    "sources": sources,
    "cards": [
        {"id": "orientation_card", "dataset": "headline", "sourceId": "headline_source", "description": "Modulo-pi child-axis coherence; full parent phase is the frozen control.", "metrics": [{"label": "Orientation coherence", "field": "orientation_coherence", "format": "number"}, {"label": "Unhalved control", "field": "unhalved_control", "format": "number"}, {"label": "Margin", "field": "orientation_margin", "format": "number", "signed": True}]},
        {"id": "relation_card", "dataset": "headline", "sourceId": "headline_source", "description": "Rank recovery of the hidden A–B closing relation.", "metrics": [{"label": "Relation Spearman", "field": "relation_spearman", "format": "number"}, {"label": "Shift control", "field": "shift_control", "format": "number"}, {"label": "Margin", "field": "relation_margin", "format": "number", "signed": True}]},
        {"id": "share_card", "dataset": "headline", "sourceId": "headline_source", "description": "Independent child-identity diagnostic; lower is better.", "metrics": [{"label": "Child-share MAE", "field": "child_share_mae", "format": "number"}]},
        {"id": "timing_card", "dataset": "headline", "sourceId": "headline_source", "description": "Blind handover was late; lower than one parent cycle was required.", "metrics": [{"label": "Handover error, M", "field": "handover_error_M", "format": "number"}, {"label": "Allowed parent cycle, M", "field": "allowed_parent_cycle_M", "format": "number"}]},
    ],
    "charts": [
        {
            "id": "relation_chart",
            "title": "Hidden and reconstructed closing relation",
            "subtitle": "The blind ARA coordinate preserves closing order but is not an absolute distance.",
            "type": "line",
            "intent": "trend",
            "dataset": "relation_history",
            "sourceId": "relation_source",
            "encodings": {
                "x": {"field": "time_M", "type": "quantitative", "label": "Simulation time", "unit": "M"},
                "y": {"field": "relation_ara", "type": "quantitative", "label": "Remaining relation", "unit": "ARA 0–2"},
                "color": {"field": "series", "type": "nominal", "label": "Series"},
                "tooltip": [{"field": "actual_separation_M", "type": "quantitative", "label": "Hidden A–B separation", "unit": "M"}, {"field": "common_horizon_time_M", "type": "quantitative", "label": "Common horizon time", "unit": "M"}],
            },
            "xAxisTitle": "Simulation time / M",
            "yAxisTitle": "Remaining relation / ARA 0–2",
            "layout": "full",
            "maxRows": 600,
        },
        {
            "id": "orientation_chart",
            "title": "Hidden and reconstructed child axis",
            "subtitle": "One global handedness and rotation symmetry is removed for scoring.",
            "type": "line",
            "intent": "trend",
            "dataset": "orientation_history",
            "sourceId": "orientation_source",
            "encodings": {
                "x": {"field": "time_M", "type": "quantitative", "label": "Simulation time", "unit": "M"},
                "y": {"field": "axis_angle_deg", "type": "quantitative", "label": "Unwrapped axis angle", "unit": "degrees"},
                "color": {"field": "series", "type": "nominal", "label": "Series"},
                "tooltip": [{"field": "axis_error_deg", "type": "quantitative", "label": "Modulo-pi error", "unit": "degrees"}],
            },
            "xAxisTitle": "Simulation time / M",
            "yAxisTitle": "Unwrapped child-axis angle / degrees",
            "layout": "full",
            "maxRows": 600,
        },
    ],
    "tables": [
        {"id": "gates_table", "title": "Frozen gates", "subtitle": "Three geometry gates passed; the predeclared handover clock failed.", "dataset": "gates", "sourceId": "gates_source", "defaultSort": {"field": "gate", "direction": "asc"}, "density": "spacious", "columns": [{"field": "gate", "label": "Gate", "type": "text"}, {"field": "score", "label": "Score", "format": "number"}, {"field": "threshold", "label": "Threshold", "format": "number"}, {"field": "rule", "label": "Rule", "type": "text"}, {"field": "result", "label": "Result", "type": "text"}]},
        {"id": "landmarks_table", "title": "Common-horizon timing landmarks", "subtitle": "The frozen median was later than first common-horizon formation.", "dataset": "landmarks", "sourceId": "landmarks_source", "defaultSort": {"field": "time_M", "direction": "asc"}, "density": "spacious", "columns": [{"field": "landmark", "label": "Landmark", "type": "text"}, {"field": "time_M", "label": "Time / M", "format": "number"}, {"field": "offset_from_C_M", "label": "Offset from C / M", "format": "number", "movement": True}, {"field": "role", "label": "Role", "type": "text"}]},
    ],
    "blocks": [
        {"id": "title", "type": "markdown", "body": "# T435 — Blind ARA binary-identity inversion"},
        {"id": "summary", "type": "markdown", "body": "## Executive Summary\n\n**Frozen verdict: PARTIAL.** The combined waveform recovered the unordered two-child axis and the common closing relation before the individual horizons were revealed. The child radial histories followed the same closing trajectory, but their independent shares remained inaccurate, and the frozen common-horizon clock arrived 37.54 M late."},
        {"id": "headline_metrics", "type": "metric-strip", "cardIds": ["orientation_card", "relation_card", "share_card", "timing_card"]},
        {"id": "findings", "type": "markdown", "body": "## Key Findings\n\nThe half-phase operation was decisive: orientation coherence was 0.994 versus 0.006 for the unhalved parent phase. Cadence ordering recovered the hidden A–B separation rank at 0.9996, but this is an ordering bridge rather than an absolute-distance measurement. The large child-radius correlations share that common closing signal; the 0.0858 share error prevents a claim that both full identities were recovered."},
        {"id": "relation_block", "type": "chart", "chartId": "relation_chart"},
        {"id": "relation_reading", "type": "markdown", "body": "## Relation Recovery\n\nThe reconstructed relation and the hidden horizon separation descend together across inspiral. This supports the ARA cut from parent cadence to child relation, while the equally strong conventional omega^(-2/3) crosswalk shows that T435 is recovering established binary dynamics rather than an independent new gravitational law."},
        {"id": "orientation_block", "type": "chart", "chartId": "orientation_chart"},
        {"id": "gate_block", "type": "table", "tableId": "gates_table"},
        {"id": "handover", "type": "markdown", "body": "## Handover Timing\n\nFirst common-horizon formation occurred before the later waveform redistribution landmarks finished. The total-power peak alone was close, but the frozen rule used the median of three landmarks; changing it after reveal would be post hoc."},
        {"id": "landmark_block", "type": "table", "tableId": "landmarks_table"},
        {"id": "method", "type": "markdown", "body": "## Scope, Data and Method\n\nInference used only SXS:BBH:0305 Lev6 Strain_N4. The prediction was written and SHA-256 sealed before metadata and horizons A/B/C were opened. The primary ARA construction used phase(h22)/2 for child orientation, odd/even mode imbalance for child asymmetry, and reverse cadence rank for remaining relation. Scoring allowed only a constant rotation, handedness reversal and A/B label swap."},
        {"id": "limits", "type": "markdown", "body": "## Limitations and Robustness\n\nThis is one GR simulation, not detector evidence. Horizon coordinate centres are gauge-sensitive, the relation metric is rank-based, and the child-radius gate is dominated by the shared closing trend. Orientation and relation beat their frozen controls strongly; full child identity and timing did not."},
        {"id": "next", "type": "markdown", "body": "## Next Step\n\nFreeze one waveform-only child-share mapping on a development set of SXS binaries spanning mass ratio and spin, then predict hidden mass contrast on untouched simulations. That is the decisive test of whether the processed parent can be separated into two distinct identities rather than only a two-child axis plus common relation."},
    ],
}

snapshot = {
    "version": 1,
    "generatedAt": generated,
    "status": "ready",
    "datasets": {
        "headline": headline,
        "relation_history": relation_rows,
        "orientation_history": orientation_rows,
        "gates": gate_rows,
        "landmarks": landmark_rows,
    },
}

OUT.write_text(json.dumps({"surface": "report", "manifest": manifest, "snapshot": snapshot, "sources": sources}, separators=(",", ":")), encoding="utf-8")
print(OUT)

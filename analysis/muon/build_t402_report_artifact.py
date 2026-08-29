#!/usr/bin/env python3
"""Build the canonical T402 portable technical-report artifact."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T402_whole_shape_child_relation"
RESULTS = json.loads((OUT / "T402_RESULTS.json").read_text(encoding="utf-8"))
VALIDATION = json.loads((OUT / "T402_VALIDATION.json").read_text(encoding="utf-8"))


def read_rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def source(source_id: str, label: str, path: str, description: str, tables: list[str]) -> dict:
    suffix = Path(path).suffix.lower()
    query = {
        "engine": "duckdb" if suffix in {".csv", ".json"} else "file",
        "language": suffix.lstrip(".") or "file",
        "description": description,
        "tables_used": tables,
    }
    if suffix == ".csv":
        query["sql"] = f"SELECT * FROM read_csv_auto('{path}')"
    elif suffix == ".json":
        query["sql"] = f"SELECT * FROM read_json_auto('{path}', format='auto')"
    return {"id": source_id, "label": label, "path": path, "query": query}


bin_summary = read_rows("T402_BIN_SUMMARY.csv")
occupancy = [
    {
        "source": row["source"],
        "bin_center": float(row["bin_center"]),
        "mean_occupancy": float(row["mean_occupancy"]),
    }
    for row in bin_summary
]
differential = []
for row in bin_summary:
    if row["source"] != "C":
        continue
    value = float(row["mean_C_minus_AC"])
    differential.append(
        {
            "bin_center": float(row["bin_center"]),
            "mean_C_minus_AC": value,
            "side": "C excess" if value >= 0 else "C deficit",
        }
    )

topology_rows = read_rows("T402_KDE_TOPOLOGY.csv")
topology_landmarks = [
    {
        "bandwidth": float(row["bandwidth"]),
        "positive_crest_x": float(row["positive_crest_x"]),
        "ridge_crossing_x": float(row["crossing_nearest_ridge_x"]),
        "negative_trough_x": float(row["negative_trough_x"]),
        "status": "PASS" if row["passes_registered_windows"].lower() == "true" else "FAIL",
    }
    for row in topology_rows
]

sensitivity = [
    {
        "bin_count": int(row["bin_count"]),
        "reflected_cosine": float(row["reflected_cosine"]),
        "lower_positive_bins": int(row["lower_positive_bins"]),
        "upper_negative_bins": int(row["upper_negative_bins"]),
        "status": "PASS" if row["passes_cosine_0_65"].lower() == "true" else "FAIL",
    }
    for row in read_rows("T402_BIN_SENSITIVITY.csv")
]

alignment = [
    {
        "AC_shift_bins": int(row["AC_cyclic_shift_bins"]),
        "shift_ara_units": float(row["shift_ara_units"]),
        "reflection_error": float(row["normalized_reflection_error"]),
        "error_rank": int(row["error_rank_lower_is_better"]),
        "is_unshifted": row["is_unshifted"].lower() == "true",
    }
    for row in read_rows("T402_ALIGNMENT_CONTROLS.csv")
]

gate_reasons = {
    "G1_raw_whole_shape": "Upper C lobe interval crossed zero and was positive in only 55.5% of valid partitions.",
    "G2_source_specific_two_sided_difference": "3/4 lower bins were positive, 4/4 upper bins negative; split stability was 73.6% on both sides.",
    "G3_continuous_topology": "All four bandwidths retained the registered crest, ridge crossing, and upper trough.",
    "G4_exact_static_reflection": "Reflected cosine 0.204, exact reverse rank 19/24, no bin sensitivity passed.",
    "G5_correct_source_alignment": "Unshifted pairing ranked 3/8 and C lower-contrast advantage occurred in 62.9% of splits.",
}
gates = [
    {
        "gate": key,
        "status": "PASS" if value else "FAIL",
        "reason": gate_reasons[key],
    }
    for key, value in RESULTS["gates"].items()
]
validation_rows = [
    {"check": key, "status": "PASS" if value else "FAIL"}
    for key, value in VALIDATION["checks"].items()
]

generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
raw = RESULTS["raw_C_shape"]
source_difference = RESULTS["source_difference"]
reflection = RESULTS["reflection"]
splits = RESULTS["splits"]

sources = [
    source("t402_bins", "T402 bin summary", "analysis/muon/T402_whole_shape_child_relation/T402_BIN_SUMMARY.csv", "C and AC mean occupancy and C-minus-AC difference on the frozen child coordinate.", ["T402_BIN_SUMMARY.csv"]),
    source("t402_splits", "T402 split ledger", "analysis/muon/T402_whole_shape_child_relation/T402_SPLITS.csv", "Fresh-partition lobe contrasts and source-difference stability measurements.", ["T402_SPLITS.csv"]),
    source("t402_topology", "T402 continuous topology", "analysis/muon/T402_whole_shape_child_relation/T402_KDE_TOPOLOGY.csv", "C-minus-AC crest, ridge crossing, and trough at four frozen bandwidths.", ["T402_KDE_TOPOLOGY.csv"]),
    source("t402_sensitivity", "T402 reflection sensitivity", "analysis/muon/T402_whole_shape_child_relation/T402_BIN_SENSITIVITY.csv", "Static reflection metrics at 6, 8, 10, and 12 bins.", ["T402_BIN_SENSITIVITY.csv"]),
    source("t402_alignment", "T402 cyclic alignment controls", "analysis/muon/T402_whole_shape_child_relation/T402_ALIGNMENT_CONTROLS.csv", "Unshifted source pairing compared with all cyclic AC shifts.", ["T402_ALIGNMENT_CONTROLS.csv"]),
    source("t402_results", "T402 saved result", "analysis/muon/T402_whole_shape_child_relation/T402_RESULTS.json", "Frozen gates, verdict, metrics, identity, and claim boundaries.", ["T402_RESULTS.json"]),
    source("t402_validation", "T402 independent validation", "analysis/muon/T402_whole_shape_child_relation/T402_VALIDATION.json", "Independent integrity and arithmetic validation of saved outputs.", ["T402_VALIDATION.json"]),
    source("t402_protocol", "Frozen T402 protocol", "analysis/muon/T402_WHOLE_SHAPE_CHILD_RELATION_PROTOCOL_2026-08-17.md", "Predeclared identity, coordinate, shape regions, gates, controls, and verdict ladder.", ["T402 protocol"]),
    {"id": "coherent_2022", "label": "COHERENT CsI public measurement and ancillary data", "path": "https://arxiv.org/abs/2110.07730"},
]

charts = [
    {
        "id": "occupancy",
        "title": "Complete C and AC child distributions",
        "subtitle": f"{splits['valid']} valid fresh transfers; each source is normalized within each split",
        "type": "bar",
        "dataset": "occupancy",
        "sourceId": "t402_bins",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [{"axis": "x", "value": 1.0, "label": "Local ridge 1.0", "color": "neutral", "lineStyle": "dashed"}],
        "encodings": {
            "x": {"field": "bin_center", "type": "quantitative", "label": "Local child ARA bin"},
            "y": {"field": "mean_occupancy", "type": "quantitative", "label": "Mean share of split weight"},
            "color": {"field": "source", "type": "nominal", "label": "Source"},
            "tooltip": [
                {"field": "source", "type": "nominal", "label": "Source"},
                {"field": "bin_center", "type": "quantitative", "label": "ARA bin"},
                {"field": "mean_occupancy", "type": "quantitative", "label": "Mean occupancy"},
            ],
        },
    },
    {
        "id": "differential",
        "title": "Source-specific child axis",
        "subtitle": "C-minus-AC changes from lower-side excess to upper-side deficit near the local ridge",
        "type": "bar",
        "dataset": "differential",
        "sourceId": "t402_bins",
        "palette": {"kind": "categorical", "name": "green-red"},
        "referenceLines": [
            {"axis": "x", "value": 1.0, "label": "Local ridge 1.0", "color": "neutral", "lineStyle": "dashed"},
            {"axis": "y", "value": 0.0, "label": "Equal C and AC", "color": "neutral", "lineStyle": "solid"},
        ],
        "encodings": {
            "x": {"field": "bin_center", "type": "quantitative", "label": "Local child ARA bin"},
            "y": {"field": "mean_C_minus_AC", "type": "quantitative", "label": "Mean C−AC occupancy"},
            "color": {"field": "side", "type": "nominal", "label": "Relation"},
            "tooltip": [
                {"field": "bin_center", "type": "quantitative", "label": "ARA bin"},
                {"field": "mean_C_minus_AC", "type": "quantitative", "label": "C−AC"},
                {"field": "side", "type": "nominal", "label": "Relation"},
            ],
        },
    },
    {
        "id": "topology",
        "title": "Continuous topology landmarks",
        "subtitle": "All four bandwidths keep the lower crest, ridge-nearest crossing, and upper trough in their frozen windows",
        "type": "line",
        "dataset": "topology_long",
        "sourceId": "t402_topology",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [{"axis": "y", "value": 1.0, "label": "Local ridge 1.0", "color": "neutral", "lineStyle": "dashed"}],
        "encodings": {
            "x": {"field": "bandwidth", "type": "quantitative", "label": "KDE bandwidth"},
            "y": {"field": "ara_location", "type": "quantitative", "label": "Local child ARA location"},
            "color": {"field": "landmark", "type": "nominal", "label": "Landmark"},
            "tooltip": [
                {"field": "bandwidth", "type": "quantitative", "label": "Bandwidth"},
                {"field": "landmark", "type": "nominal", "label": "Landmark"},
                {"field": "ara_location", "type": "quantitative", "label": "ARA location"},
            ],
        },
    },
    {
        "id": "alignment",
        "title": "Cyclic source-alignment controls",
        "subtitle": "Lower reflection error is better; the real unshifted pairing ranks third of eight",
        "type": "bar",
        "dataset": "alignment",
        "sourceId": "t402_alignment",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "encodings": {
            "x": {"field": "shift_ara_units", "type": "quantitative", "label": "Artificial AC shift, ARA units"},
            "y": {"field": "reflection_error", "type": "quantitative", "label": "Normalized reflection error"},
            "tooltip": [
                {"field": "shift_ara_units", "type": "quantitative", "label": "AC shift"},
                {"field": "reflection_error", "type": "quantitative", "label": "Reflection error"},
                {"field": "error_rank", "type": "quantitative", "label": "Rank"},
            ],
        },
    },
]

tables = [
    {
        "id": "gates",
        "title": "Frozen scientific gates",
        "subtitle": "The source-difference and continuous-topology gates pass; raw two-lobe and exact reflection gates fail",
        "dataset": "gates",
        "sourceId": "t402_results",
        "defaultSort": {"field": "gate", "direction": "asc"},
        "columns": [
            {"field": "gate", "label": "Gate", "type": "text"},
            {"field": "status", "label": "Result", "type": "text"},
            {"field": "reason", "label": "Reason", "type": "text"},
        ],
    },
    {
        "id": "topology_table",
        "title": "Continuous topology by bandwidth",
        "subtitle": "ARA locations on the mean C-minus-AC density difference",
        "dataset": "topology_landmarks",
        "sourceId": "t402_topology",
        "defaultSort": {"field": "bandwidth", "direction": "asc"},
        "columns": [
            {"field": "bandwidth", "label": "Bandwidth", "type": "number"},
            {"field": "positive_crest_x", "label": "Positive crest", "type": "number"},
            {"field": "ridge_crossing_x", "label": "Ridge crossing", "type": "number"},
            {"field": "negative_trough_x", "label": "Negative trough", "type": "number"},
            {"field": "status", "label": "Frozen window", "type": "text"},
        ],
    },
    {
        "id": "validation",
        "title": "Independent saved-output validation",
        "subtitle": "All integrity, arithmetic, gate, and verdict checks passed",
        "dataset": "validation",
        "sourceId": "t402_validation",
        "defaultSort": {"field": "check", "direction": "asc"},
        "columns": [
            {"field": "check", "label": "Check", "type": "text"},
            {"field": "status", "label": "Status", "type": "text"},
        ],
    },
]

blocks = [
    {
        "id": "summary",
        "type": "markdown",
        "body": f"# T402 — Whole-shape child relation\n\n## Technical summary\n\n**The raw C distribution did not replicate as a stable two-lobe whole shape, so the registered verdict is `{RESULTS['verdict']}`.** Its lower lobe was stable, but the upper lobe's 95% resampling interval crossed zero and was positive in only {raw['fraction_splits_upper_positive']:.1%} of {splits['valid']} valid fresh partitions. A narrower relation did replicate: C-minus-AC was positive in 3/4 lower bins and negative in 4/4 upper bins, and all four continuous bandwidths crossed near the local ridge. Exact reflected anti-phase was not selected (cosine {reflection['primary_eight_bin_cosine']:.3f}, rank {reflection['exact_mapping_rank_of_24']}/24).",
        "sourceId": "t402_results",
    },
    {
        "id": "raw_text",
        "type": "markdown",
        "body": f"## The visible raw upper lobe does not replicate\n\nThe C lower-lobe-minus-saddle contrast averaged **{raw['mean_lower_minus_saddle']:+.4f}** with a fully positive resampling interval. The upper contrast averaged only **{raw['mean_upper_minus_saddle']:+.4f}**, with interval **[{raw['upper_resampling_interval_95'][0]:+.4f}, {raw['upper_resampling_interval_95'][1]:+.4f}]**. The complete chart therefore contains a stable lower crest and a variable upper side, not two independently stable C lobes.",
        "sourceId": "t402_results",
    },
    {"id": "occupancy_chart", "type": "chart", "chartId": "occupancy"},
    {
        "id": "source_text",
        "type": "markdown",
        "body": f"## The stable relation is C relative to AC across the ridge\n\nThe source-specific axis passed its frozen gate. Lower-side C-minus-AC was positive in **{source_difference['fraction_splits_mean_lower_positive']:.1%}** of valid partitions; upper-side C-minus-AC was negative in **{source_difference['fraction_splits_mean_upper_negative']:.1%}**. This preserves the visual's direction but changes its identity: the robust whole relation belongs to the **difference between the two measured source records**, not to raw C occupancy alone.",
        "sourceId": "t402_results",
    },
    {"id": "differential_chart", "type": "chart", "chartId": "differential"},
    {
        "id": "topology_text",
        "type": "markdown",
        "body": "## The source difference crosses continuously near the child ridge\n\nAcross KDE bandwidths 0.10–0.25, the positive crest remains at 0.50–0.57, the nearest sign crossing moves only from 0.936 to 1.051, and the negative trough remains at 1.88–1.91. All four frozen topology checks pass. This is the strongest replicated T402 feature, but probability closure means location and robustness—not the mere presence of opposite signs—carry the evidence.",
        "sourceId": "t402_topology",
    },
    {"id": "topology_chart", "type": "chart", "chartId": "topology"},
    {"id": "topology_table_block", "type": "table", "tableId": "topology_table"},
    {
        "id": "reflection_text",
        "type": "markdown",
        "body": f"## The handover is asymmetric rather than mirror-exact\n\nThe exact static reflection gives cosine **{reflection['primary_eight_bin_cosine']:.3f}** and ranks **{reflection['exact_mapping_rank_of_24']}/24**. No bin-count sensitivity reaches the registered 0.65 cosine, and the unshifted C/AC pairing ranks {RESULTS['alignment']['unshifted_rank_of_8']}/8 against cyclic shifts. T402 therefore does not identify the upper side as an exact recovered anti-phase waveform.",
        "sourceId": "t402_results",
    },
    {"id": "alignment_chart", "type": "chart", "chartId": "alignment"},
    {"id": "gates_table", "type": "table", "tableId": "gates"},
    {
        "id": "scope",
        "type": "markdown",
        "body": f"## Scope, data, and metric definitions\n\n- **Identity and rung:** unchanged COHERENT CsI delayed-child identity on the T400 local child ARA 0–2 cut.\n- **Fresh partitions:** salts 600–999; {splits['valid']}/{splits['requested']} formed ordered calibration-only child windows.\n- **Raw lobe contrast:** mean occupancy in a flank minus the 1.0–1.5 saddle.\n- **Source-specific axis:** normalized C occupancy minus normalized AC occupancy in the same frozen child bin.\n- **Continuous topology:** crest, ridge-nearest zero crossing, and trough of the mean KDE density difference.\n\nThe partitions overlap and measure resampling stability, not {splits['valid']} independent experiments.",
        "sourceId": "t402_results",
    },
    {
        "id": "method",
        "type": "markdown",
        "body": "## Methodology\n\nThe protocol and gates were hashed before execution. Every split used 70% calibration records to fit the population model and define the local child boundaries; the resulting coordinate and scoring rule were transferred unchanged to the untouched 30%. The analysis retained every bin, compared C with AC under one denominator, tested KDE bandwidths 0.10–0.25, ranked exact reflection against all 24 upper-bin assignments, repeated reflection at 6/8/10/12 bins, and compared the true source alignment with every cyclic AC shift.",
    },
    {
        "id": "limitations",
        "type": "markdown",
        "body": "## Limitations and robustness\n\nThe broad shape was selected after viewing T401 and is a registered follow-up, not a new discovery sample. C and AC differ in acquisition context, so their difference is diagnostic but not a pure physical-component isolation. Closure forces each differential to sum to zero. The stable result is therefore the predeclared location and continuous topology of the handover, not generic positive/negative mass. This remains population/event-weight evidence and does not time an individual neutrino birth.",
    },
    {"id": "validation_table", "type": "table", "tableId": "validation"},
    {
        "id": "next",
        "type": "markdown",
        "body": "## Recommended next step\n\nFollow the replicated source-difference axis rather than searching for another empty raw bin. Freeze the lower crest, ridge crossing, and upper deficit on one dataset, then test whether those landmarks predict a held-out event-level observable or reproduce in an independent detector/source archive. Keep exact reflection rejected unless independent data restore it.\n\n## Further questions\n\n- Which measured source or acquisition component produces the strong 1.88–1.91 upper deficit?\n- Does the ridge-nearest crossing survive in an independent detector with a directly observed daughter relation?\n- Can the three landmarks improve held-out event ordering without relabelling population timing as individual creation?",
    },
]

topology_long = []
for row in topology_landmarks:
    for landmark, field in (("positive crest", "positive_crest_x"), ("ridge crossing", "ridge_crossing_x"), ("negative trough", "negative_trough_x")):
        topology_long.append({"bandwidth": row["bandwidth"], "landmark": landmark, "ara_location": row[field]})

artifact = {
    "surface": "report",
    "manifest": {
        "version": 1,
        "surface": "report",
        "title": "T402 — Whole-shape child relation",
        "description": "Frozen fresh-partition test of the raw and source-specific two-sided relation on the COHERENT CsI local child ARA coordinate.",
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
            "occupancy": occupancy,
            "differential": differential,
            "topology_long": topology_long,
            "topology_landmarks": topology_landmarks,
            "sensitivity": sensitivity,
            "alignment": alignment,
            "gates": gates,
            "validation": validation_rows,
        },
    },
    "sources": [{"id": item["id"], "query": item.get("query", {"engine": "web", "description": item["label"]})} for item in sources],
    "package_info": {"originUrl": "artifact://t402-whole-shape-child-relation", "controls": {"edit": False, "refresh": False}},
}

(OUT / "artifact.json").write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")
print(OUT / "artifact.json")

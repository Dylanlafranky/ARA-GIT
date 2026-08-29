#!/usr/bin/env python3
"""Build the canonical T403 portable technical-report artifact."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T403_reverse_component_lineage"
RESULTS = json.loads((OUT / "T403_RESULTS.json").read_text(encoding="utf-8"))
VALIDATION = json.loads((OUT / "T403_VALIDATION.json").read_text(encoding="utf-8"))


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


profile_raw = read_rows("T403_COMPONENT_PROFILES.csv")
profiles = [
    {
        "ara_x": float(row["ara_x"]),
        "time_us": float(row["time_us"]),
        "series": row["series"],
        "centered_maxabs": float(row["centered_maxabs"]),
        "evidence_class": row["evidence_class"],
    }
    for row in profile_raw
]

source_series = {
    "T402 detector C-AC",
    "delayed total release",
    "nu_e release",
    "anti_nu_mu release",
}
source_overlay = [row for row in profiles if row["series"] in source_series]

profile_map = {}
for row in profiles:
    profile_map.setdefault(row["series"], []).append(row)
for rows in profile_map.values():
    rows.sort(key=lambda r: r["ara_x"])

reverse_components = []
for series, label, reverse in (
    ("T402 detector C-AC", "T402 detector C-AC", False),
    ("release gradient", "release gradient viewed upstream", True),
    ("remaining-muon curvature", "remaining-parent curvature viewed upstream", True),
    ("remaining muon", "remaining muon", False),
):
    rows = list(profile_map[series])
    values = [r["centered_maxabs"] for r in rows]
    if reverse:
        values = values[::-1]
    for row, value in zip(rows, values):
        reverse_components.append(
            {
                "ara_x": row["ara_x"],
                "series": label,
                "centered_maxabs": value,
            }
        )

scores_raw = read_rows("T403_COMPONENT_SCORES.csv")
best_by_candidate = {}
for row in scores_raw:
    candidate = row["candidate"]
    parsed = {
        "candidate": candidate,
        "orientation": row["orientation"],
        "absolute_cosine": float(row["absolute_cosine"]),
        "registered_rank": int(row["registered_shift_rank_of_8"]),
    }
    if candidate not in best_by_candidate or parsed["absolute_cosine"] > best_by_candidate[candidate]["absolute_cosine"]:
        best_by_candidate[candidate] = parsed
score_rows = sorted(best_by_candidate.values(), key=lambda r: r["absolute_cosine"], reverse=True)
for row in score_rows:
    row["candidate_orientation"] = f"{row['candidate']} [{row['orientation']}]"

split_raw = read_rows("T403_SPLIT_ROBUSTNESS.csv")
split_values = [float(row["cosine"]) for row in split_raw]
edges = [-1.0 + i * 0.1 for i in range(21)]
split_hist = []
for lo, hi in zip(edges[:-1], edges[1:]):
    count = sum((v >= lo and (v < hi or (hi == 1.0 and v <= hi))) for v in split_values)
    split_hist.append({"bin_center": (lo + hi) / 2, "count": count})

t397_raw = read_rows("T403_T397_PHASE_PROFILES.csv")
t397 = [
    {
        "ara_x": float(row["ara_x"]),
        "series": row["series"],
        "field_g": float(row["field_g"]),
        "centered_maxabs": float(row["centered_maxabs"]),
    }
    for row in t397_raw
    if float(row["field_g"]) == 160.0
]
for row in profiles:
    if row["series"] == "T402 detector C-AC":
        t397.append(
            {
                "ara_x": row["ara_x"],
                "series": "T402 detector shape",
                "field_g": 0.0,
                "centered_maxabs": row["centered_maxabs"],
            }
        )

gate_reasons = {
    "G1_detector_integrity": "The eight-bin detector vector and all four saved topology windows reproduce T402.",
    "G2_component_selection": "At least one same-archive candidate exceeds the frozen 0.65 cosine threshold.",
    "G3_alignment_control": "The selected unshifted orientation ranks first of eight circular shifts.",
    "G4_derivative_specificity": "Failed: derivative/curvature candidates do not beat the whole delayed-release rates by 0.10.",
    "G5_evidence_boundary": "T397 remains separate and individual-neutrino birth is not claimed.",
}
gates = [
    {
        "gate": key,
        "status": "PASS" if value else "FAIL",
        "reason": gate_reasons[key],
    }
    for key, value in RESULTS["gates"].items()
]

evidence = [
    {"cut": "T402 detector footprint", "class": "Measured diagnostic", "meaning": "C-minus-AC detector response contrast; not a flavor tag"},
    {"cut": "T398/T400 delayed branch", "class": "Fitted source waveform", "meaning": "Joint delayed release plus official nu_e and anti_nu_mu template children"},
    {"cut": "Remaining parent and gradients", "class": "Derived", "meaning": "Calculated from the same delayed template; not independent evidence"},
    {"cut": "T397 silver phase", "class": "Independent but unlinked", "meaning": "Different medium, detector and experiment; shape comparison only"},
    {"cut": "T395/T396 locks", "class": "Truth-model crosswalk", "meaning": "Statistical parent/child relations, not observed time waveforms"},
]

validation_rows = [
    {"check": key, "status": "PASS" if value else "FAIL"}
    for key, value in VALIDATION["checks"].items()
]

generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
selected = RESULTS["selected_same_archive_candidate"]
robust = RESULTS["split_robustness"]
flavor = RESULTS["post_frozen_flavor_identifiability"]
t397_best = RESULTS["t397_exploratory_best"]

sources = [
    source("t403_profiles", "T403 component profiles", "analysis/muon/T403_reverse_component_lineage/T403_COMPONENT_PROFILES.csv", "Eight-bin detector, fitted-source, and derived-parent component profiles on the frozen local ARA coordinate.", ["T403_COMPONENT_PROFILES.csv"]),
    source("t403_scores", "T403 component scores", "analysis/muon/T403_reverse_component_lineage/T403_COMPONENT_SCORES.csv", "Fixed direct/reversed cosine scores and circular-shift alignment ranks.", ["T403_COMPONENT_SCORES.csv"]),
    source("t403_splits", "T403 split robustness", "analysis/muon/T403_reverse_component_lineage/T403_SPLIT_ROBUSTNESS.csv", "Selected-component cosine across 326 saved T402 resampling probes.", ["T403_SPLIT_ROBUSTNESS.csv"]),
    source("t403_t397", "T403 T397 phase comparison", "analysis/muon/T403_reverse_component_lineage/T403_T397_PHASE_PROFILES.csv", "Eight-bin silver W phase profiles retained as a separate shape comparison.", ["T403_T397_PHASE_PROFILES.csv"]),
    source("t403_results", "T403 saved result", "analysis/muon/T403_reverse_component_lineage/T403_RESULTS.json", "Frozen gates, verdict, selected candidate, diagnostics, and evidence boundaries.", ["T403_RESULTS.json"]),
    source("t403_validation", "T403 independent validation", "analysis/muon/T403_reverse_component_lineage/T403_VALIDATION.json", "Independent recomputation of scores, split summaries, flavor identifiability, and verdict logic.", ["T403_VALIDATION.json"]),
    source("t403_protocol", "Frozen T403 protocol", "analysis/muon/T403_REVERSE_COMPONENT_LINEAGE_PROTOCOL_2026-08-18.md", "Predeclared reverse-lineage coordinate, candidates, alignment controls, gates, and claim boundary.", ["T403 protocol"]),
    source("t402_bins", "T402 detector footprint", "analysis/muon/T402_whole_shape_child_relation/T402_BIN_SUMMARY.csv", "Measured C and AC detector-source occupancies and the signed C-minus-AC footprint.", ["T402_BIN_SUMMARY.csv"]),
    source("t398_native", "T398 native neutrino release waveforms", "analysis/muon/T398_population_neutrino_wave_overlap/T398_NATIVE_WAVE_OVERLAP.csv", "Fitted prompt/delayed source templates, flavor children, and derived remaining-parent curve.", ["T398_NATIVE_WAVE_OVERLAP.csv"]),
    source("t397_phase", "T397 RAL Silver phase profiles", "analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_PHASE_PROFILES.csv", "Observed and fitted silver common-mode W phase profiles.", ["T397_PHASE_PROFILES.csv"]),
    {"id": "coherent_2022", "label": "COHERENT CsI public measurement and ancillary data", "path": "https://arxiv.org/abs/2110.07730"},
    {"id": "ral_silver", "label": "ISIS EMU RAL Silver public source", "path": "https://doi.org/10.5286/ISIS.E.RB1620201"},
]

charts = [
    {
        "id": "source_overlay",
        "title": "Detector footprint and delayed-neutrino source children",
        "subtitle": "T402/T398/T400; eight fixed local-ARA bins; each curve centred and max-absolute normalized",
        "type": "line",
        "dataset": "source_overlay",
        "sourceId": "t403_profiles",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [
            {"axis": "x", "value": 1.0, "label": "Local ARA ridge", "color": "neutral", "lineStyle": "dashed"},
            {"axis": "y", "value": 0.0, "label": "Within-window mean", "color": "neutral", "lineStyle": "solid"},
        ],
        "encodings": {
            "x": {"field": "ara_x", "type": "quantitative", "label": "Local child ARA (0–2)"},
            "y": {"field": "centered_maxabs", "type": "quantitative", "label": "Centred component (max |value| = 1)"},
            "color": {"field": "series", "type": "nominal", "label": "Wave component"},
            "tooltip": [
                {"field": "series", "type": "nominal", "label": "Component"},
                {"field": "ara_x", "type": "quantitative", "label": "ARA"},
                {"field": "time_us", "type": "quantitative", "label": "Source time (microseconds)"},
                {"field": "centered_maxabs", "type": "quantitative", "label": "Centred value"},
            ],
        },
    },
    {
        "id": "parent_components",
        "title": "Reverse parent-component comparison",
        "subtitle": "Upstream-facing derivatives are reversed explicitly; remaining parent stays in native direction",
        "type": "line",
        "dataset": "reverse_components",
        "sourceId": "t403_profiles",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [
            {"axis": "x", "value": 1.0, "label": "Local ARA ridge", "color": "neutral", "lineStyle": "dashed"},
            {"axis": "y", "value": 0.0, "label": "Within-window mean", "color": "neutral", "lineStyle": "solid"},
        ],
        "encodings": {
            "x": {"field": "ara_x", "type": "quantitative", "label": "Local child ARA (0–2)"},
            "y": {"field": "centered_maxabs", "type": "quantitative", "label": "Centred component (max |value| = 1)"},
            "color": {"field": "series", "type": "nominal", "label": "Parent relation"},
            "tooltip": [
                {"field": "series", "type": "nominal", "label": "Component"},
                {"field": "ara_x", "type": "quantitative", "label": "ARA"},
                {"field": "centered_maxabs", "type": "quantitative", "label": "Centred value"},
            ],
        },
    },
    {
        "id": "score_bars",
        "title": "Best fixed orientation by candidate",
        "subtitle": "Absolute centred cosine against T402; 1.0 is identical shape after centring",
        "type": "bar",
        "dataset": "score_rows",
        "sourceId": "t403_scores",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [{"axis": "y", "value": 0.65, "label": "Frozen component threshold", "color": "neutral", "lineStyle": "dashed"}],
        "encodings": {
            "x": {"field": "candidate_orientation", "type": "nominal", "label": "Candidate and orientation"},
            "y": {"field": "absolute_cosine", "type": "quantitative", "label": "Absolute cosine"},
            "tooltip": [
                {"field": "candidate", "type": "nominal", "label": "Candidate"},
                {"field": "orientation", "type": "nominal", "label": "Orientation"},
                {"field": "absolute_cosine", "type": "quantitative", "label": "Absolute cosine"},
                {"field": "registered_rank", "type": "quantitative", "label": "Alignment rank of 8"},
            ],
        },
    },
    {
        "id": "split_hist",
        "title": "Selected relation across saved T402 splits",
        "subtitle": "326 overlapping deterministic resampling probes; not independent experiments",
        "type": "bar",
        "dataset": "split_hist",
        "sourceId": "t403_splits",
        "palette": {"kind": "single", "name": "blue"},
        "referenceLines": [
            {"axis": "x", "value": 0.0, "label": "No relation", "color": "neutral", "lineStyle": "solid"},
            {"axis": "x", "value": 0.65, "label": "+0.65 threshold", "color": "neutral", "lineStyle": "dashed"},
        ],
        "encodings": {
            "x": {"field": "bin_center", "type": "quantitative", "label": "Cosine with selected source component"},
            "y": {"field": "count", "type": "quantitative", "label": "Split count"},
            "tooltip": [
                {"field": "bin_center", "type": "quantitative", "label": "Cosine bin centre"},
                {"field": "count", "type": "quantitative", "label": "Splits"},
            ],
        },
    },
    {
        "id": "silver_phase",
        "title": "Separate silver muon phase comparison",
        "subtitle": "160 G T397 W phase beside T402; normalized shape only, with no shared event or time origin",
        "type": "line",
        "dataset": "t397",
        "sourceId": "t403_t397",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [
            {"axis": "x", "value": 1.0, "label": "Native phase midpoint", "color": "neutral", "lineStyle": "dashed"},
            {"axis": "y", "value": 0.0, "label": "Phase mean", "color": "neutral", "lineStyle": "solid"},
        ],
        "encodings": {
            "x": {"field": "ara_x", "type": "quantitative", "label": "Native phase mapped to 0–2"},
            "y": {"field": "centered_maxabs", "type": "quantitative", "label": "Centred component (max |value| = 1)"},
            "color": {"field": "series", "type": "nominal", "label": "Separate trace"},
            "tooltip": [
                {"field": "series", "type": "nominal", "label": "Trace"},
                {"field": "ara_x", "type": "quantitative", "label": "Native phase"},
                {"field": "centered_maxabs", "type": "quantitative", "label": "Centred value"},
            ],
        },
    },
]

tables = [
    {
        "id": "gates",
        "title": "Frozen T403 gates",
        "subtitle": "A same-archive component is present, but derivative specificity fails",
        "dataset": "gates",
        "sourceId": "t403_results",
        "columns": [
            {"field": "gate", "label": "Gate", "type": "text"},
            {"field": "status", "label": "Result", "type": "text"},
            {"field": "reason", "label": "Reason", "type": "text"},
        ],
    },
    {
        "id": "evidence",
        "title": "Evidence classes stay separate",
        "subtitle": "Measured, fitted, derived, independent-unlinked, and truth-model cuts",
        "dataset": "evidence",
        "sourceId": "t403_results",
        "columns": [
            {"field": "cut", "label": "Cut", "type": "text"},
            {"field": "class", "label": "Evidence class", "type": "text"},
            {"field": "meaning", "label": "What it can establish", "type": "text"},
        ],
    },
    {
        "id": "validation",
        "title": "Independent saved-output validation",
        "subtitle": "Protocol, arithmetic, split summaries, flavor diagnostic, and verdict logic",
        "dataset": "validation",
        "sourceId": "t403_validation",
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
        "body": f"# T403 — Reverse component lineage\n\n## Technical summary\n\n**Yes: the detector contains a strong projection of the joint delayed-neutrino release branch. No: this cut does not yet isolate one neutrino flavor or an individual birth event.** The registered verdict is `{RESULTS['verdict']}`. On the unchanged local ARA coordinate, the best aggregate match is `{selected['candidate']}` in `{selected['orientation']}` orientation (cosine **{selected['cosine']:.3f}**, alignment rank **{selected['registered_shift_rank_of_8']}/8**). But the fitted `nu_e`, `anti_nu_mu`, and total delayed curves all score 0.950–0.957, so the detector is recovering their shared release shape rather than uniquely naming one child.",
        "sourceId": "t403_results",
    },
    {
        "id": "source_text",
        "type": "markdown",
        "body": "## The detector footprint is the common delayed-release component\n\nThe T402 detector contrast is positive on the early side, crosses near the local ridge, and becomes negative late. Sampling the T398 source templates at the same eight T400 bins reproduces that shape without a circular shift. Because every curve is centred first, the negative side means **below its own within-window average**, not negative neutrino intensity.",
        "sourceId": "t403_profiles",
    },
    {"id": "source_chart", "type": "chart", "chartId": "source_overlay"},
    {
        "id": "flavor_text",
        "type": "markdown",
        "body": f"## Timing alone does not decompress the two neutral children\n\nThe fitted `nu_e` and `anti_nu_mu` shapes are almost collinear in this window (centred cosine **{flavor['nu_e_vs_anti_nu_mu_centered_cosine']:.5f}**). Removing their unequal fitted weights leaves a flavor-specific shape contrast with detector cosine only **{flavor['area_normalized_flavor_shape_contrast_direct_cosine']:.3f}**, ranked **{flavor['area_normalized_flavor_shape_contrast_direct_rank_of_8']}/8**. The tiny aggregate lead of `anti_nu_mu` is therefore not enough to identify that flavor as the recovered child.",
        "sourceId": "t403_results",
    },
    {
        "id": "parent_text",
        "type": "markdown",
        "body": "## Reverse traversal finds a release projection, not a derivative-only child\n\nThe upstream-facing release-gradient and remaining-parent-curvature components have absolute cosine about 0.769 and correct unshifted alignment, while the whole delayed-release rates remain stronger at about 0.95. This fails the frozen derivative-specificity gate. In plain language: the detector retains the broad release branch more clearly than a uniquely separated rate-change or parent-curvature component.",
        "sourceId": "t403_scores",
    },
    {"id": "parent_chart", "type": "chart", "chartId": "parent_components"},
    {
        "id": "score_text",
        "type": "markdown",
        "body": "## Candidate ranking confirms a shared branch rather than one special waveform\n\nThe four delayed-rate candidates cluster tightly at the top. That crowding is the diagnostic result: the detector contrast locates the delayed branch, but the available timing cut is insufficient to tell its tightly coupled template children apart.",
        "sourceId": "t403_scores",
    },
    {"id": "score_chart", "type": "chart", "chartId": "score_bars"},
    {
        "id": "robust_text",
        "type": "markdown",
        "body": f"## The aggregate relation is not yet an event-level waveform\n\nAcross {robust['n']} saved T402 resampling probes, median cosine is **{robust['median_cosine']:.3f}** with 95% resampling interval **[{robust['resampling_interval_95'][0]:.3f}, {robust['resampling_interval_95'][1]:.3f}]**. Only **{robust['fraction_absolute_cosine_at_least_0p65']:.1%}** reach absolute cosine 0.65, although **{robust['fraction_same_sign_as_primary']:.1%}** retain the aggregate orientation. This supports a population-average projection and rejects an individual or split-stable reconstruction claim.",
        "sourceId": "t403_splits",
    },
    {"id": "split_chart", "type": "chart", "chartId": "split_hist"},
    {
        "id": "silver_text",
        "type": "markdown",
        "body": f"## The earlier silver spin trace is not the missing linked parent\n\nThe strongest T397 comparison is the fitted 160 G W phase with absolute cosine **{float(t397_best['absolute_cosine']):.3f}**, but its registered alignment ranks **{int(t397_best['registered_shift_rank_of_8'])}/8** and a different circular phase is better. The observed trace is weaker. More importantly, T397 uses different muons, silver, and a different detector; its phase can be compared as geometry but cannot be inserted into the COHERENT lineage.",
        "sourceId": "t403_results",
    },
    {"id": "silver_chart", "type": "chart", "chartId": "silver_phase"},
    {
        "id": "scope",
        "type": "markdown",
        "body": "## Scope, data, and metric definitions\n\n- **Detector component:** T402 mean `C-AC` occupancy in eight local-child bins.\n- **Source components:** T398 fitted delayed total, `nu_e`, and `anti_nu_mu` templates sampled between T400's frozen boundaries.\n- **Parent components:** remaining-muon complement and its derivatives, all derived from the delayed template.\n- **Similarity:** centred cosine; offset and amplitude are removed, while order and shape are retained.\n- **Alignment control:** the registered zero shift ranked against all eight circular shifts.\n\nT395/T396 are omitted from waveform scores because they are truth-model statistical locks rather than observed temporal profiles.",
        "sourceId": "t403_results",
    },
    {"id": "evidence_table", "type": "table", "tableId": "evidence"},
    {
        "id": "method",
        "type": "markdown",
        "body": "## Methodology\n\nThe protocol was hashed before execution. T402's saved detector vector was reproduced, T400's frozen linear map converted its bin centres to source time, and T398 curves were interpolated without fitted shifts or smoothing parameters. Direct and reversed orientations were scored separately; each registered alignment was checked against non-zero circular shifts. A post-frozen diagnostic removed flavor-weight differences to test whether the aggregate match was flavor-specific. Independent validation recomputed the headline scores, split interval, flavor diagnostic, and verdict logic.",
    },
    {"id": "gates_table", "type": "table", "tableId": "gates"},
    {
        "id": "limits",
        "type": "markdown",
        "body": "## Limitations, uncertainty, and robustness\n\nThe T402 curve is a detector response contrast, not a pristine neutrino field waveform. Its coordinate and the T398 source profiles come from the same COHERENT archive, so the aggregate match is not an independent replication. Derived remaining-parent and derivative curves reuse the same delayed template. The two fitted flavor children are not event tags. The resampling probes overlap and are not independent experiments. No result here measures the birth time of one neutrino from one named muon.",
    },
    {"id": "validation_table", "type": "table", "tableId": "validation"},
    {
        "id": "next",
        "type": "markdown",
        "body": "## Recommended next step\n\nFreeze the detector crest, ridge crossing, and late deficit on an independent detector/source archive, then test them against that archive's independently supplied delayed-release template. To separate `nu_e` from `anti_nu_mu`, require flavor-sensitive information or an independently observed charged-daughter relation; timing alone leaves the child shapes almost identical here.\n\n## Further questions\n\n- Does the same centred delayed-release projection reproduce outside the COHERENT CsI archive?\n- Which detector or source variable generates the T402 C-minus-AC contrast?\n- Can charged-daughter direction or missing momentum separate the two neutral children event by event?",
    },
]

artifact = {
    "surface": "report",
    "manifest": {
        "version": 1,
        "surface": "report",
        "title": "T403 — Reverse component lineage",
        "description": "Detector-to-source audit of the delayed-neutrino child components and their relation to the stopped-muon parent.",
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
            "source_overlay": source_overlay,
            "reverse_components": reverse_components,
            "score_rows": score_rows,
            "split_hist": split_hist,
            "t397": t397,
            "gates": gates,
            "evidence": evidence,
            "validation": validation_rows,
        },
    },
    "sources": [
        {"id": item["id"], "query": item.get("query", {"engine": "web", "description": item["label"]})}
        for item in sources
    ],
    "package_info": {
        "originUrl": "artifact://t403-reverse-component-lineage",
        "controls": {"edit": False, "refresh": False},
    },
}

(OUT / "artifact.json").write_text(
    json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(OUT / "artifact.json")

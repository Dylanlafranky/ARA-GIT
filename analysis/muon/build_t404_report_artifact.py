#!/usr/bin/env python3
"""Build the canonical portable T404 technical report artifact."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T404_corrected_child_release_diara"
RESULTS = json.loads((OUT / "T404_RESULTS.json").read_text(encoding="utf-8"))
VALIDATION = json.loads((OUT / "T404_VALIDATION.json").read_text(encoding="utf-8"))
P405 = HERE / "T405_parent_landmark_child_distortion"
R405 = json.loads((P405 / "T405_RESULTS.json").read_text(encoding="utf-8"))
V405 = json.loads((P405 / "T405_VALIDATION.json").read_text(encoding="utf-8"))


def read_rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def source(source_id: str, label: str, path: str, description: str) -> dict:
    suffix = Path(path).suffix.lower()
    query = {
        "engine": "duckdb" if suffix in {".csv", ".json"} else "file",
        "language": suffix.lstrip(".") or "file",
        "description": description,
        "tables_used": [Path(path).name],
    }
    if suffix == ".csv":
        query["sql"] = f"SELECT * FROM read_csv_auto('{path}')"
    elif suffix == ".json":
        query["sql"] = f"SELECT * FROM read_json_auto('{path}', format='auto')"
    return {"id": source_id, "label": label, "path": path, "query": query}


mapping_raw = read_rows("T404_COORDINATE_MAPPING.csv")
mapping = []
for row in mapping_raw:
    for series, field in (
        ("Correct cumulative-ARA inverse", "correct_time_us"),
        ("T403 linear assumption", "t403_linear_time_us"),
    ):
        mapping.append(
            {
                "ara_x": float(row["local_child_ara"]),
                "time_us": float(row[field]),
                "series": series,
            }
        )

landmark_raw = read_rows("T404_REGISTERED_LANDMARKS.csv")
landmark_rows = []
for row in landmark_raw:
    bandwidth = float(row["bandwidth"])
    for order, label, field in (
        (1, "Detector turn", "detector_crest_x"),
        (2, "Child release maximum", "source_release_crest_x"),
        (3, "Detector handover", "detector_ridge_x"),
    ):
        landmark_rows.append(
            {
                "stage_order": order,
                "stage": label,
                "ara_x": float(row[field]),
                "bandwidth": f"h={bandwidth:.2f}",
            }
        )

bootstrap_raw = read_rows("T404_BOOTSTRAP.csv")
bootstrap_values = [
    float(row["detector_octave_residual"])
    for row in bootstrap_raw
    if row["valid"].lower() == "true"
]
lo, hi = min(bootstrap_values), max(bootstrap_values)
bin_count = 42
width = (hi - lo) / bin_count
bootstrap_hist = []
for index in range(bin_count):
    left = lo + index * width
    right = left + width
    count = sum(
        value >= left and (value < right or (index == bin_count - 1 and value <= right))
        for value in bootstrap_values
    )
    bootstrap_hist.append({"residual": (left + right) / 2, "count": count})

diara_raw = read_rows("T404_STORAGE_FLOW_DIARA.csv")
diara = [
    {
        "storage_ara": float(row["storage_ara"]),
        "release_flow_ara": float(row["release_flow_ara"]),
        "local_child_ara": float(row["local_child_ara"]),
        "stage": row["stage"],
        "quadrant": row["quadrant"],
    }
    for index, row in enumerate(diara_raw)
    if index % 5 == 0 or index == len(diara_raw) - 1
]

profiles_raw = read_rows("T404_CORRECTED_PROFILES.csv")
profiles = [
    {
        "ara_x": float(row["ara_x"]),
        "time_us": float(row["time_us"]),
        "series": row["series"],
        "centered_maxabs": float(row["centered_maxabs"]),
        "evidence_class": row["evidence_class"],
    }
    for row in profiles_raw
]

gates = [
    {
        "gate": key,
        "status": "PASS" if value else "FAIL",
        "meaning": {
            "G1_correct_inverse_map_reproduces_T400_crest": "Correct inverse recovers the registered T400 source crest.",
            "G2_three_stage_all_registered_bandwidths": "Turn < release maximum < handover for all four KDE bandwidths.",
            "G3_three_stage_bootstrap_at_least_90pct": "At least 90% of saved-split bootstraps retain the order.",
            "G4_exact_detector_octave": "Broad binned bootstrap interval contains zero and circular-shift control is <= 0.05.",
            "G5_exact_source_octave_across_bandwidths": "Ridge minus twice the source release crest crosses zero across bandwidths.",
            "G6_independent_prompt_before_delayed_chronology": "T378 independently retains prompt-before-delayed chronology.",
            "G7_individual_spinning_muon_event_link_available": "Current inputs event-link one spin trajectory to its daughters.",
        }[key],
    }
    for key, value in RESULTS["gates"].items()
]

validation_rows = [
    {"check": f"T404: {key}", "status": "PASS" if value else "FAIL"}
    for key, value in VALIDATION["checks"].items()
] + [
    {"check": f"T405: {key}", "status": "PASS" if value else "FAIL"}
    for key, value in V405["checks"].items()
]

distortion_raw = []
with (P405 / "T405_SPLIT_PARTICIPATION.csv").open("r", encoding="utf-8-sig", newline="") as handle:
    distortion_raw = list(csv.DictReader(handle))
distortion = sorted(
    [
        {
            "prompt_participation": float(row["prompt_participation"]),
            "child_crest": float(row["population_local_mode"]),
            "child_displacement": float(row["child_displacement_from_0p5"]),
            "salt": int(row["salt"]),
        }
        for row in distortion_raw
    ],
    key=lambda row: row["prompt_participation"],
)

evidence = [
    {"cut": "T402 detector turn and handover", "class": "Measured diagnostic", "boundary": "C-minus-AC detector relation; not a pristine neutrino waveform."},
    {"cut": "T398/T400 child release", "class": "Fitted source", "boundary": "Population delayed-release template on the corrected cumulative-ARA coordinate."},
    {"cut": "Storage-flow Di-ARA", "class": "Derived", "boundary": "Remaining fraction and release rate derive from the same delayed template."},
    {"cut": "Saved T402 split bootstrap", "class": "Overlapping robustness probes", "boundary": "Not independent experiments or a raw-event confidence interval."},
    {"cut": "T378 COHERENT 2017", "class": "Independent coarse archive", "boundary": "Supports chronology only; bins are too coarse for the nested coordinate."},
    {"cut": "T397 RAL Silver", "class": "Independent aggregate spin data", "boundary": "Population muSR phase, not an event-linked individual decay."},
]

sources = [
    source("t404_mapping", "T404 corrected coordinate mapping", "analysis/muon/T404_corrected_child_release_diara/T404_COORDINATE_MAPPING.csv", "Correct and linear source-time maps for the eight fixed local-child bins."),
    source("t404_landmarks", "T404 registered landmarks", "analysis/muon/T404_corrected_child_release_diara/T404_REGISTERED_LANDMARKS.csv", "Detector turn, child release maximum, handover, ratios, and octave residuals for four registered KDE bandwidths."),
    source("t404_bootstrap", "T404 bootstrap", "analysis/muon/T404_corrected_child_release_diara/T404_BOOTSTRAP.csv", "Five thousand resamples of the saved overlapping T402 split histograms."),
    source("t404_diara", "T404 storage-flow Di-ARA", "analysis/muon/T404_corrected_child_release_diara/T404_STORAGE_FLOW_DIARA.csv", "Candidate remaining-parent storage versus delayed-child release-flow phase portrait."),
    source("t404_profiles", "T404 corrected profiles", "analysis/muon/T404_corrected_child_release_diara/T404_CORRECTED_PROFILES.csv", "Detector and fitted-source curves sampled with the corrected inverse coordinate."),
    source("t404_results", "T404 saved results", "analysis/muon/T404_corrected_child_release_diara/T404_RESULTS.json", "Verdict, gates, audit metrics, evidence boundaries, and individual-event requirements."),
    source("t404_validation", "T404 independent validation", "analysis/muon/T404_corrected_child_release_diara/T404_VALIDATION.json", "Independent recomputation of mapping, landmark, bootstrap, Di-ARA, and scope checks."),
    source("t404_protocol", "T404 frozen correction protocol", "analysis/muon/T404_CORRECTED_CHILD_RELEASE_DIARA_PROTOCOL_2026-08-18.md", "Pre-run audit identities, evaluations, gates, and claim boundary."),
    source("t400_curve", "T400 local child curve", "analysis/muon/T400_nested_child_window_population_to_event/T400_LOCAL_CHILD_CURVE.csv", "Registered cumulative parent-ARA child coordinate and delayed-release curve."),
    source("t402_topology", "T402 KDE topology", "analysis/muon/T402_whole_shape_child_relation/T402_KDE_TOPOLOGY.csv", "Four pre-existing detector topology bandwidths."),
    source("t378_holdout", "T378 independent holdout", "analysis/muon/T398_population_neutrino_wave_overlap/T398_T378_INDEPENDENT_HOLDOUT.csv", "Independent coarse COHERENT timing chronology."),
    source("t405_distortion", "T405 split participation", "analysis/muon/T405_parent_landmark_child_distortion/T405_SPLIT_PARTICIPATION.csv", "Prompt participation and child-crest displacement across the valid T400 repeated splits."),
    source("t405_results", "T405 distortion-aware results", "analysis/muon/T405_parent_landmark_child_distortion/T405_RESULTS.json", "Participation relation, equality-boundary diagnostic, gates, and structural evidence boundary."),
    source("t405_validation", "T405 independent validation", "analysis/muon/T405_parent_landmark_child_distortion/T405_VALIDATION.json", "Independent recomputation and structural-encoding audit."),
    {"id": "coherent_csi", "label": "COHERENT CsI measurement", "path": "https://arxiv.org/abs/2110.07730"},
    {"id": "ral_silver", "label": "RAL Silver muSR source", "path": "https://doi.org/10.5286/ISIS.E.RB1620201"},
]

charts = [
    {
        "id": "coordinate_map",
        "title": "T403 used the wrong inverse coordinate",
        "subtitle": "The registered T400 child coordinate is cumulative parent ARA, not linear time",
        "type": "line",
        "dataset": "mapping",
        "sourceId": "t404_mapping",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [{"axis": "x", "value": RESULTS["coordinate_audit"]["saved_T400_local_crest"], "label": "True release crest 0.706", "color": "neutral", "lineStyle": "dashed"}],
        "encodings": {
            "x": {"field": "ara_x", "type": "quantitative", "label": "Local child ARA (0-2)"},
            "y": {"field": "time_us", "type": "quantitative", "label": "Source time (microseconds)"},
            "color": {"field": "series", "type": "nominal", "label": "Mapping"},
            "tooltip": [
                {"field": "series", "type": "nominal", "label": "Map"},
                {"field": "ara_x", "type": "quantitative", "label": "Child ARA"},
                {"field": "time_us", "type": "quantitative", "label": "Time (us)"},
            ],
        },
    },
    {
        "id": "landmark_sequence",
        "title": "The corrected relation is three-stage",
        "subtitle": "All four registered detector bandwidths place release maximum between turn and handover",
        "type": "line",
        "dataset": "landmarks",
        "sourceId": "t404_landmarks",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [{"axis": "y", "value": 1.0, "label": "ARA ridge 1.0", "color": "neutral", "lineStyle": "dashed"}],
        "encodings": {
            "x": {"field": "stage_order", "type": "quantitative", "label": "Ordered stage: 1 turn, 2 release, 3 handover"},
            "y": {"field": "ara_x", "type": "quantitative", "label": "Local child ARA (0-2)"},
            "color": {"field": "bandwidth", "type": "nominal", "label": "KDE bandwidth"},
            "tooltip": [
                {"field": "stage", "type": "nominal", "label": "Stage"},
                {"field": "bandwidth", "type": "nominal", "label": "Bandwidth"},
                {"field": "ara_x", "type": "quantitative", "label": "ARA"},
            ],
        },
    },
    {
        "id": "octave_residual",
        "title": "Detector-turn octave is broad, not an exact point estimate",
        "subtitle": "Saved overlapping split bootstrap; exact doubling is residual 0",
        "type": "bar",
        "dataset": "bootstrap_hist",
        "sourceId": "t404_bootstrap",
        "palette": {"kind": "single", "name": "blue"},
        "referenceLines": [{"axis": "x", "value": 0.0, "label": "Exact octave", "color": "neutral", "lineStyle": "dashed"}],
        "encodings": {
            "x": {"field": "residual", "type": "quantitative", "label": "Handover - 2 x detector turn"},
            "y": {"field": "count", "type": "quantitative", "label": "Bootstrap count"},
            "tooltip": [
                {"field": "residual", "type": "quantitative", "label": "Residual"},
                {"field": "count", "type": "quantitative", "label": "Count"},
            ],
        },
    },
    {
        "id": "storage_flow_diara",
        "title": "Candidate storage-flow Di-ARA",
        "subtitle": "Derived remaining-parent storage versus delayed-child release flow; each axis mapped separately to 0-2",
        "type": "line",
        "dataset": "diara",
        "sourceId": "t404_diara",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [
            {"axis": "x", "value": 1.0, "label": "Storage ridge", "color": "neutral", "lineStyle": "solid"},
            {"axis": "y", "value": 1.0, "label": "Flow ridge", "color": "neutral", "lineStyle": "solid"},
        ],
        "encodings": {
            "x": {"field": "storage_ara", "type": "quantitative", "label": "Remaining-parent storage (0-2)"},
            "y": {"field": "release_flow_ara", "type": "quantitative", "label": "Delayed-child release flow (0-2)"},
            "color": {"field": "stage", "type": "nominal", "label": "Ordered stage"},
            "tooltip": [
                {"field": "stage", "type": "nominal", "label": "Stage"},
                {"field": "local_child_ara", "type": "quantitative", "label": "Local child ARA"},
                {"field": "quadrant", "type": "nominal", "label": "Quadrant"},
            ],
        },
    },
    {
        "id": "corrected_profiles",
        "title": "Detector and source components on the corrected map",
        "subtitle": "Centred, max-absolute normalized shapes; amplitude and offset are intentionally removed",
        "type": "line",
        "dataset": "profiles",
        "sourceId": "t404_profiles",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [
            {"axis": "x", "value": 1.0, "label": "Local ridge", "color": "neutral", "lineStyle": "dashed"},
            {"axis": "y", "value": 0.0, "label": "Within-window mean", "color": "neutral", "lineStyle": "solid"},
        ],
        "encodings": {
            "x": {"field": "ara_x", "type": "quantitative", "label": "Local child ARA (0-2)"},
            "y": {"field": "centered_maxabs", "type": "quantitative", "label": "Centred component (max |value| = 1)"},
            "color": {"field": "series", "type": "nominal", "label": "Component"},
            "tooltip": [
                {"field": "series", "type": "nominal", "label": "Component"},
                {"field": "ara_x", "type": "quantitative", "label": "ARA"},
                {"field": "time_us", "type": "quantitative", "label": "Time (us)"},
            ],
        },
    },
    {
        "id": "distortion_relation",
        "title": "Parent landmark, child expression",
        "subtitle": "Greater prompt participation moves the equality boundary and displaces the child crest; rho = 1.000 inside T400",
        "type": "line",
        "dataset": "distortion",
        "sourceId": "t405_distortion",
        "palette": {"kind": "single", "name": "blue"},
        "referenceLines": [{"axis": "y", "value": 0.5, "label": "Pure parent landmark 0.5", "color": "neutral", "lineStyle": "dashed"}],
        "encodings": {
            "x": {"field": "prompt_participation", "type": "quantitative", "label": "Prompt participation q"},
            "y": {"field": "child_crest", "type": "quantitative", "label": "Child release crest on local ARA"},
            "tooltip": [
                {"field": "salt", "type": "quantitative", "label": "Split salt"},
                {"field": "prompt_participation", "type": "quantitative", "label": "Prompt participation"},
                {"field": "child_crest", "type": "quantitative", "label": "Child crest"},
                {"field": "child_displacement", "type": "quantitative", "label": "Displacement from 0.5"},
            ],
        },
    },
]

tables = [
    {
        "id": "gates",
        "title": "T404 interpretation gates",
        "subtitle": "Exact source-release doubling fails; the three-stage relation survives",
        "dataset": "gates",
        "sourceId": "t404_results",
        "columns": [
            {"field": "gate", "label": "Gate", "type": "text"},
            {"field": "status", "label": "Result", "type": "text"},
            {"field": "meaning", "label": "Meaning", "type": "text"},
        ],
    },
    {
        "id": "evidence",
        "title": "Evidence classes and boundaries",
        "subtitle": "Measured, fitted, derived, robustness, and independent cuts are not interchangeable",
        "dataset": "evidence",
        "sourceId": "t404_results",
        "columns": [
            {"field": "cut", "label": "Cut", "type": "text"},
            {"field": "class", "label": "Evidence class", "type": "text"},
            {"field": "boundary", "label": "What it cannot establish", "type": "text"},
        ],
    },
    {
        "id": "validation",
        "title": "Independent saved-output validation",
        "subtitle": "All coordinate, landmark, bootstrap, Di-ARA, and scope checks passed",
        "dataset": "validation",
        "sourceId": "t404_validation",
        "columns": [
            {"field": "check", "label": "Check", "type": "text"},
            {"field": "status", "label": "Status", "type": "text"},
        ],
    },
]

c = RESULTS["coordinate_audit"]
b = RESULTS["bootstrap"]
s = RESULTS["registered_bandwidth_summary"]
d = RESULTS["diara"]

blocks = [
    {
        "id": "summary",
        "type": "markdown",
        "body": f"# T404/T405 — Corrected child release and distortion-aware Di-ARA audit\n\n## Answer first\n\n**The three-stage handover replicates, and the difference between its parent landmark and child expression is participation-dependent.** T403's apparent source crest at `0.532` came from an invalid linear time conversion. The correct cumulative-ARA child crest is **{c['saved_T400_local_crest']:.6f}**. Across every registered detector bandwidth, the order is parent/aggregate detector turn **0.50–0.57** → displaced child release maximum **0.706** → parent handover **0.936–1.051**. It survives **{b['three_stage_fraction']:.2%}** of 5,000 saved-split bootstrap means. T405 then shows that child displacement from the pure `0.5` reference varies monotonically with branch participation (rho **{R405['primary']['spearman_rho']:.3f}**).",
        "sourceId": "t404_results",
    },
    {
        "id": "coordinate_text",
        "type": "markdown",
        "body": f"## The coordinate correction changes the interpretation\n\nT400 defines local position by cumulative parent ARA. T403 instead spread eight bins uniformly through time, moving the source crest by **{abs(c['T403_apparent_displacement']):.3f} ARA units** and creating the attractive `0.532 -> 1.032` appearance. The corrected inverse reproduces the saved T400 crest to machine precision; the maximum eight-bin time discrepancy is **{c['maximum_eight_bin_time_error_us']:.3f} microseconds**.",
        "sourceId": "t404_mapping",
    },
    {"id": "coordinate_chart", "type": "chart", "chartId": "coordinate_map"},
    {
        "id": "sequence_text",
        "type": "markdown",
        "body": "## What remains is a stable three-stage sequence\n\nThe detector relation starts turning first, the inferred delayed child reaches its maximum next, and the detector relation crosses its local handover last. This is compatible with an early accumulation/turn signal, a release maximum, and a later coarse parent handover. It is not the same claim as saying the release maximum doubles into the ridge.",
        "sourceId": "t404_landmarks",
    },
    {"id": "sequence_chart", "type": "chart", "chartId": "landmark_sequence"},
    {
        "id": "octave_text",
        "type": "markdown",
        "body": f"## Pure landmarks and distorted child coordinates must stay separate\n\n- **Parent/aggregate turn to handover:** registered point ratios are **{s['detector_to_ridge_ratio_range'][0]:.3f}–{s['detector_to_ridge_ratio_range'][1]:.3f}**, close to but systematically short of the pure 2:1 limit. The broad binned bootstrap interval for the residual is **[{b['detector_octave_residual_95_interval'][0]:.3f}, {b['detector_octave_residual_95_interval'][1]:.3f}]**, so the pure limit remains statistically compatible at this coarse robustness level.\n- **Observed child release maximum to parent handover:** ratios are **{s['source_to_ridge_ratio_range'][0]:.3f}–{s['source_to_ridge_ratio_range'][1]:.3f}**. This rejects exact equality for the observed child time slice, not the existence of a parent `0.5` reference. T405 tests the missing condition—participation-dependent displacement—directly.\n\nThe bootstrap is broad because it resamples overlapping saved splits and uses an eight-bin estimator. The continuous point estimates should be read as a parent landmark plus a displaced child expression, not as every car being forced to travel at the speed limit.",
        "sourceId": "t404_bootstrap",
    },
    {"id": "octave_chart", "type": "chart", "chartId": "octave_residual"},
    {
        "id": "diara_text",
        "type": "markdown",
        "body": f"## The candidate Di-ARA is storage versus release flow\n\nThe cleanest two-axis reconstruction is **remaining-parent storage** against **delayed-child release flow**. In the frozen child window the path rises into maximum flow, turns, crosses the release/handover interval, and then exits while storage continues falling. The detector turn at **{d['mean_detector_turn']:.3f}**, release maximum at **{d['child_release_maximum']:.3f}**, and detector handover at **{d['mean_detector_handover']:.3f}** label positions along this path.\n\nThis is a useful ARA phase portrait, not independent proof: remaining storage is the cumulative complement of the same fitted delayed template whose rate supplies the flow axis.",
        "sourceId": "t404_diara",
    },
    {"id": "diara_chart", "type": "chart", "chartId": "storage_flow_diara"},
    {
        "id": "distortion_text",
        "type": "markdown",
        "body": f"## T405 recovers the parent-versus-child rule\n\nAcross 20 valid T400 repeated splits, the parent reference remains `0.5` while child crests range **{R405['primary']['child_crest_range'][0]:.3f}–{R405['primary']['child_crest_range'][1]:.3f}**. Prompt participation and child displacement have Spearman rho **{R405['primary']['spearman_rho']:.3f}**; every leave-one-out rho is also 1.000.\n\nThat perfection is structurally informative but not independent physics. Prompt participation moves the equality boundary used to construct the local child coordinate, and the three quantities have identical ranks. T405 therefore validates that the ARA cut translates one parent landmark into participation-dependent child positions. A different measurement is still required to show that a particular external physical energy channel causes the displacement.",
        "sourceId": "t405_results",
    },
    {"id": "distortion_chart", "type": "chart", "chartId": "distortion_relation"},
    {
        "id": "profiles_text",
        "type": "markdown",
        "body": "## Corrected component shapes retain a broad relation\n\nSampling the fitted source components at the correct times still leaves a structured detector/source relation, but the source maximum no longer occupies the detector's early half-scale landmark. The measured detector diagnostic and fitted source wave must therefore remain distinct components of the candidate Di-ARA.",
        "sourceId": "t404_profiles",
    },
    {"id": "profiles_chart", "type": "chart", "chartId": "corrected_profiles"},
    {
        "id": "individual",
        "type": "markdown",
        "body": "## Can we see this in one spinning muon?\n\n**Not with the current files.** T397 measures aggregate muSR asymmetry in silver. T398–T404 measure population source timing and detector distributions. None links one muon's spin trajectory and decay time to its charged daughter plus the two neutral children. The individual test is now well specified, but the data must contain event-linked spin/polarization, decay time, charged-daughter direction and energy, and neutral-sensitive timing or independently reconstructed missing momentum.",
        "sourceId": "t404_results",
    },
    {"id": "gates_table", "type": "table", "tableId": "gates"},
    {"id": "evidence_table", "type": "table", "tableId": "evidence"},
    {
        "id": "method",
        "type": "markdown",
        "body": "## Method and robustness\n\nThe protocol was written before executing T404, while explicitly recording that this is a post-discovery coordinate audit. The exact T400 cumulative coordinate was rebuilt from its saved primary fit and native prompt/delayed templates. All four pre-existing T402 KDE bandwidths were reported. Five thousand fixed-seed bootstrap means resampled the 326 saved split identities; a frozen quadratic crest and linear zero crossing produced binned landmarks. Seven non-zero circular shifts per bootstrap were controls. T378 was restricted to independent chronology because its twelve coarse bins cannot reproduce the nested coordinate.",
        "sourceId": "t404_protocol",
    },
    {"id": "validation_table", "type": "table", "tableId": "validation"},
    {
        "id": "next",
        "type": "markdown",
        "body": "## Recommended next test\n\nUse an event-level decay archive, or a detector with independently linked polarization and charged-daughter kinematics, to test whether independently measured participation predicts the child displacement before the outcome is read. Freeze the parent landmark, participation variable, child crest, and handover definitions in advance. Until that dataset is available, the supported result is a distortion-aware population geometry—not an individual neutrino birth predictor.",
    },
]

generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
artifact = {
    "surface": "report",
    "manifest": {
        "version": 1,
        "surface": "report",
        "title": "T404/T405 — Corrected child release and distortion-aware Di-ARA audit",
        "description": "Coordinate correction, three-stage handover replication, parent-versus-child landmark displacement, and storage-flow Di-ARA reconstruction.",
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
            "mapping": mapping,
            "landmarks": landmark_rows,
            "bootstrap_hist": bootstrap_hist,
            "diara": diara,
            "profiles": profiles,
            "distortion": distortion,
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
        "originUrl": "artifact://t404-corrected-child-release-diara",
        "controls": {"edit": False, "refresh": False},
    },
}

(OUT / "artifact.json").write_text(
    json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(OUT / "artifact.json")

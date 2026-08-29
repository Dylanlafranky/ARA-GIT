#!/usr/bin/env python3
"""Build the canonical T401 technical-report artifact from validated outputs."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T401_winner_projection_child_antiphase"
RESULTS = json.loads((OUT / "T401_RESULTS.json").read_text(encoding="utf-8"))
VALIDATION = json.loads((OUT / "T401_VALIDATION.json").read_text(encoding="utf-8"))


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


bin_summary = [
    {
        "source": row["source"],
        "bin_center": float(row["bin_center"]),
        "mean_occupancy": float(row["mean_occupancy"]),
        "occupancy_cv": float(row["occupancy_cv"]),
        "binned_mode_fraction": float(row["binned_mode_fraction"]),
        "kde_mode_fraction_in_bin": float(row["kde_mode_fraction_in_bin"]),
    }
    for row in read_rows("T401_BIN_SUMMARY.csv")
]
occupancy = [
    {"source": row["source"], "bin_center": row["bin_center"], "mean_occupancy": row["mean_occupancy"]}
    for row in bin_summary
]
winners = []
for row in bin_summary:
    if row["source"] != "C":
        continue
    winners.append({"method": "8-bin mode", "bin_center": row["bin_center"], "winner_fraction": row["binned_mode_fraction"]})
    winners.append({"method": "KDE mode h=0.15", "bin_center": row["bin_center"], "winner_fraction": row["kde_mode_fraction_in_bin"]})

mirror = [
    {
        "source": row["source"],
        "reflected_pair": f"{float(row['lower_center']):.3f}↔{float(row['reflected_upper_center']):.3f}",
        "spearman_rho": float(row["spearman_rho_clr_across_splits"]),
    }
    for row in read_rows("T401_MIRROR_RELATIONS.csv")
]
null_rows = []
for row in read_rows("T401_SAMPLING_NULL.csv"):
    center = float(row["bin_center"])
    null_rows.append({"series": "Observed", "bin_center": center, "winner_fraction": float(row["observed_binned_mode_fraction"])})
    null_rows.append({"series": "Sampling-only null", "bin_center": center, "winner_fraction": float(row["sampling_null_mode_fraction"])})

gate_explanations = {
    "G1_occupied_but_nondominant": "Band won 7.93%, above the 1% missing-winner ceiling.",
    "G2_continuous_missing_winner_persists": "KDE modes entered the band in 10.37%, above the 5% ceiling.",
    "G3_beyond_sampling_argmax_null": "Observed 13 winners; their rate matches the sampling null (p=0.767).",
    "G4_reflected_exchange": "C score 0.0467, 2/4 negative pairs, exact reflection rank 13/24.",
    "G5_C_exceeds_AC_control": "C score advantage 0.0973 and poorer exact-reflection rank.",
}
gates = [
    {"gate": key, "status": "PASS" if value else "FAIL", "reason": gate_explanations[key]}
    for key, value in RESULTS["gates"].items()
]
validation_rows = [
    {"check": key, "status": "PASS" if value else "FAIL"}
    for key, value in VALIDATION["checks"].items()
]

generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
candidate = RESULTS["candidate_band"]
null = RESULTS["sampling_null"]
reflection = RESULTS["reflection"]
splits = RESULTS["splits"]

sources = [
    source("t401_bins", "T401 per-bin distribution summary", "analysis/muon/T401_winner_projection_child_antiphase/T401_BIN_SUMMARY.csv", "Mean occupancy, variability and winner fractions for C and AC across valid splits.", ["T401_BIN_SUMMARY.csv"]),
    source("t401_modes", "T401 split-mode ledger", "analysis/muon/T401_winner_projection_child_antiphase/T401_SPLIT_MODES.csv", "Binned and weighted-KDE modes for every valid split and source.", ["T401_SPLIT_MODES.csv"]),
    source("t401_mirror", "T401 reflected-pair relations", "analysis/muon/T401_winner_projection_child_antiphase/T401_MIRROR_RELATIONS.csv", "CLR Spearman relations for the four predeclared ARA reflection pairs.", ["T401_MIRROR_RELATIONS.csv"]),
    source("t401_null", "T401 sampling-only winner null", "analysis/muon/T401_winner_projection_child_antiphase/T401_SAMPLING_NULL.csv", "Pooled occupancy, observed dominance and simulated winner frequencies.", ["T401_SAMPLING_NULL.csv"]),
    source("t401_results", "T401 saved result", "analysis/muon/T401_winner_projection_child_antiphase/T401_RESULTS.json", "Frozen gates, verdict, metrics and evidence boundaries.", ["T401_RESULTS.json"]),
    source("t401_validation", "T401 independent validation", "analysis/muon/T401_winner_projection_child_antiphase/T401_VALIDATION.json", "Independent saved-output integrity and arithmetic validation.", ["T401_VALIDATION.json"]),
    source("t401_protocol", "Frozen T401 protocol", "analysis/muon/T401_WINNER_PROJECTION_CHILD_ANTIPHASE_PROTOCOL_2026-08-17.md", "Predeclared identity, coordinate, measurements, controls and verdict ladder.", ["T401 protocol"]),
    {"id": "coherent_2022", "label": "COHERENT CsI public measurement and ancillary data", "path": "https://arxiv.org/abs/2110.07730"},
]

charts = [
    {
        "id": "occupancy",
        "title": "Full-distribution occupancy",
        "subtitle": f"{splits['valid']} valid calibration-to-holdout transfers; each source sums to one within each split",
        "type": "bar",
        "dataset": "occupancy",
        "sourceId": "t401_bins",
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
        "id": "winners",
        "title": "Binned and continuous winner locations",
        "subtitle": "The candidate 1.25–1.50 band is selected by both methods",
        "type": "bar",
        "dataset": "winners",
        "sourceId": "t401_modes",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [{"axis": "x", "value": 1.0, "label": "Local ridge 1.0", "color": "neutral", "lineStyle": "dashed"}],
        "encodings": {
            "x": {"field": "bin_center", "type": "quantitative", "label": "Local child ARA mode region"},
            "y": {"field": "winner_fraction", "type": "quantitative", "label": "Fraction of valid C splits"},
            "color": {"field": "method", "type": "nominal", "label": "Mode method"},
            "tooltip": [
                {"field": "method", "type": "nominal", "label": "Method"},
                {"field": "bin_center", "type": "quantitative", "label": "ARA region"},
                {"field": "winner_fraction", "type": "quantitative", "label": "Winner fraction"},
            ],
        },
    },
    {
        "id": "mirror",
        "title": "Reflected-pair exchange across splits",
        "subtitle": "Centred-log-ratio Spearman relations; negative values indicate exchange",
        "type": "bar",
        "dataset": "mirror",
        "sourceId": "t401_mirror",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "referenceLines": [{"axis": "y", "value": 0.0, "label": "No relation", "color": "neutral", "lineStyle": "solid"}],
        "encodings": {
            "x": {"field": "reflected_pair", "type": "nominal", "label": "Predeclared reflected ARA pair"},
            "y": {"field": "spearman_rho", "type": "quantitative", "label": "Spearman ρ after CLR"},
            "color": {"field": "source", "type": "nominal", "label": "Source"},
            "tooltip": [
                {"field": "source", "type": "nominal", "label": "Source"},
                {"field": "reflected_pair", "type": "nominal", "label": "Pair"},
                {"field": "spearman_rho", "type": "quantitative", "label": "Spearman ρ"},
            ],
        },
    },
    {
        "id": "null",
        "title": "Observed winners versus sampling-only null",
        "subtitle": f"Multinomial effective sample size {null['pooled_effective_sample_size_rounded']}; candidate observed-versus-null p={null['observed_vs_null_two_sided_binomial_p']:.3f}",
        "type": "bar",
        "dataset": "null",
        "sourceId": "t401_null",
        "palette": {"kind": "categorical", "name": "blue-gold"},
        "encodings": {
            "x": {"field": "bin_center", "type": "quantitative", "label": "Local child ARA winning bin"},
            "y": {"field": "winner_fraction", "type": "quantitative", "label": "Fraction of winners"},
            "color": {"field": "series", "type": "nominal", "label": "Series"},
            "tooltip": [
                {"field": "series", "type": "nominal", "label": "Series"},
                {"field": "bin_center", "type": "quantitative", "label": "ARA bin"},
                {"field": "winner_fraction", "type": "quantitative", "label": "Winner fraction"},
            ],
        },
    },
]

tables = [
    {
        "id": "gates",
        "title": "Frozen scientific gates",
        "subtitle": "All five gates failed without threshold changes",
        "dataset": "gates",
        "sourceId": "t401_results",
        "defaultSort": {"field": "gate", "direction": "asc"},
        "columns": [
            {"field": "gate", "label": "Gate", "type": "text"},
            {"field": "status", "label": "Result", "type": "text"},
            {"field": "reason", "label": "Reason", "type": "text"},
        ],
    },
    {
        "id": "validation",
        "title": "Independent saved-output validation",
        "subtitle": "Integrity and arithmetic passed; scientific failures remain failures",
        "dataset": "validation",
        "sourceId": "t401_validation",
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
        "body": f"# T401 — Winner projection and candidate child anti-phase\n\n## Technical summary\n\n**The apparent missing band was a winner-only projection artifact, not a stable child anti-phase shadow.** The `1.25–1.50` band retained **{candidate['mean_occupancy_C']:.2%}** of C weight, almost exactly its neighbour average, and became the binned winner in **{candidate['binned_mode_fraction_C']:.2%}** and KDE winner in **{candidate['kde_mode_fraction_C']:.2%}** of {splits['valid']} valid transfers. Its observed winner rate matches the sampling-only null (`p={null['observed_vs_null_two_sided_binomial_p']:.3f}`). The exact reflection was weak and ranked 13th of 24 pairings. All frozen gates failed.",
        "sourceId": "t401_results",
    },
    {
        "id": "occupancy_text",
        "type": "markdown",
        "body": f"## Restoring the omitted distribution fills the visual hole\n\nT400 retained only each split's largest bin. T401 keeps all eight bins. The candidate's occupancy ratio to its immediate neighbours is **{candidate['occupancy_ratio_to_C_neighbours']:.3f}** and its volatility is **{candidate['volatility_ratio_to_C_median']:.3f}** times the median bin, classified **{candidate['volatility_class']}**. It is therefore an ordinary occupied part of this child coordinate, not a quiet null or unusually turbulent seam.",
        "sourceId": "t401_results",
    },
    {"id": "occupancy_chart", "type": "chart", "chartId": "occupancy"},
    {
        "id": "winner_text",
        "type": "markdown",
        "body": f"## The gap disappears under both discrete and continuous modes\n\nThe candidate won **{null['observed_candidate_winners']}** of {splits['valid']} binned splits and 17 KDE splits. A sampling-only model expected a **{null['single_split_candidate_mode_probability']:.2%}** winner rate, nearly identical to the observed **{candidate['binned_mode_fraction_C']:.2%}**. The original zero among twenty splits should not be promoted into a physical child identity.",
        "sourceId": "t401_results",
    },
    {"id": "winner_chart", "type": "chart", "chartId": "winners"},
    {"id": "null_chart", "type": "chart", "chartId": "null"},
    {
        "id": "reflection_text",
        "type": "markdown",
        "body": f"## The exact reflected pairing is not selected\n\nC gives an exchange score of **{reflection['C']['exchange_score']:.4f}**, only **{reflection['C']['negative_pair_count']}/4** negative reflected relations and exact-reflection rank **{reflection['C']['reflection_rank_of_24']}/24**. AC gives score **{reflection['AC']['exchange_score']:.4f}** and rank **{reflection['AC']['reflection_rank_of_24']}/24**; its rank does not indicate exchange because the score has the wrong sign. This cut does not identify a reflected child Phase B.",
        "sourceId": "t401_results",
    },
    {"id": "mirror_chart", "type": "chart", "chartId": "mirror"},
    {"id": "gates_table", "type": "table", "tableId": "gates"},
    {
        "id": "scope",
        "type": "markdown",
        "body": f"## Scope, data and metric definitions\n\n- **Identity:** the same COHERENT CsI delayed-child window used by T400; no medium or rung was changed.\n- **Coordinate:** local child ARA `0–2`, bounded by calibration-only branch equality and delayed-rate return.\n- **Occupancy:** a bin's mean share of delayed-membership weight across valid holdouts.\n- **Dominance:** the fraction of splits in which that bin is the largest.\n- **Valid transfers:** {splits['valid']}/{splits['requested']} ({splits['valid_fraction']:.0%}); 36 calibration partitions did not form an ordered child interval.\n- **Control:** AC records use the same frozen scoring denominator as C.\n\nThe partitions overlap heavily. They measure resampling stability, not {splits['valid']} independent physical experiments.",
        "sourceId": "t401_results",
    },
    {
        "id": "method",
        "type": "markdown",
        "body": "## Methodology\n\nThe protocol was hashed before execution. Salts 400–599 independently froze a 70% calibration fit and transferred it to the untouched 30%. T401 saved each complete weighted distribution, calculated a fixed-bandwidth `h=0.15` KDE mode, compared CLR-transformed reflected pairs with all 24 assignments, and simulated 50,000 200-draw winner experiments using the actual valid split count. Total lower-versus-upper anticorrelation was excluded because probability closure forces it.",
    },
    {
        "id": "limitations",
        "type": "markdown",
        "body": "## Limitations and robustness\n\nThe candidate interval was selected after T400 and is not an independent discovery interval. The multinomial null approximates weighted records using an effective sample size. Thirty-six invalid windows show sensitivity to calibration resolution. Most importantly, this source still contains statistical detector-event weights rather than a named muon linked to both named neutral daughters. A failed shadow test cannot prove that the physical identity lacks anti-phase; it only rejects this visual gap as its locator.",
    },
    {"id": "validation_table", "type": "table", "tableId": "validation"},
    {
        "id": "next",
        "type": "markdown",
        "body": "## Recommended next step\n\nStop extracting new identities from this winner histogram. Transfer the frozen child coordinate to a finer-time or event-linked source with an independently observed parent phase and charged-daughter relation, reconstruct the anti-phase before revealing the target handover, and test it on untouched events.\n\n## Further questions\n\n- Do invalid calibration windows share a measurable source-resolution condition?\n- Does a finer-time event record retain ridge-centred balance without coarse-bin mode instability?\n- Can an independently measured second relation turn the existing population lock into an individual Information³ test?",
    },
]

artifact = {
    "surface": "report",
    "manifest": {
        "version": 1,
        "surface": "report",
        "title": "T401 — Winner projection and candidate child anti-phase",
        "description": "Frozen full-distribution audit of the apparent missing winner band in the COHERENT CsI delayed-child ARA coordinate.",
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
            "winners": winners,
            "mirror": mirror,
            "null": null_rows,
            "gates": gates,
            "validation": validation_rows,
        },
    },
    "sources": [{"id": item["id"], "query": item.get("query", {"engine": "web", "description": item["label"]})} for item in sources],
    "package_info": {"originUrl": "artifact://t401-winner-projection-child-antiphase", "controls": {"edit": False, "refresh": False}},
}

(OUT / "artifact.json").write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")
print(OUT / "artifact.json")

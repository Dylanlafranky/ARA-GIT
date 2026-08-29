#!/usr/bin/env python3
"""Build the canonical portable HTML artifact for T398."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T398_population_neutrino_wave_overlap"
RESULTS_PATH = OUT / "T398_RESULTS.json"
VALIDATION_PATH = OUT / "T398_VALIDATION.json"
OVERLAP_PATH = OUT / "T398_NATIVE_WAVE_OVERLAP.csv"
BINNED_PATH = OUT / "T398_T371_MEASURED_AND_FITTED.csv"
HOLDOUT_PATH = OUT / "T398_T378_INDEPENDENT_HOLDOUT.csv"
PHASE_PATH = OUT / "T398_T397_SEPARATE_PHASE_COMPARISON.csv"
ARTIFACT_PATH = OUT / "artifact.json"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))
    handover = float(results["handover"]["reconstructed_native_equality_us"])

    native_source: list[dict[str, object]] = []
    delayed_children: list[dict[str, object]] = []
    ara_traversal: list[dict[str, object]] = []
    full_overlap_rows = rows(OVERLAP_PATH)
    # Keep the portable chart light while preserving 25 ns sampling. The full
    # 5 ns ledger remains in the source CSV and is used by the validator.
    display_rows = full_overlap_rows[::5]
    for row in display_rows:
        time_us = float(row["time_us"])
        for series, field in (
            ("Prompt νμ rate (peak = 1)", "prompt_nu_mu_peak_normalized"),
            ("Inferred muon remaining", "inferred_muon_remaining_fraction"),
            ("Delayed νe + anti-νμ rate (peak = 1)", "delayed_total_release_peak_normalized"),
        ):
            native_source.append(
                {"time_us": time_us, "value": float(row[field]), "series": series}
            )
        for series, field in (
            ("νe template contribution", "nu_e_release_over_delayed_peak"),
            ("anti-νμ template contribution", "anti_nu_mu_release_over_delayed_peak"),
            ("Combined delayed branch", "delayed_total_release_peak_normalized"),
        ):
            delayed_children.append(
                {"time_us": time_us, "value": float(row[field]), "series": series}
            )
        ara_traversal.append(
            {"time_us": time_us, "cumulative_ara": float(row["cumulative_ara_0_to_2"])}
        )

    def component_rows(path: Path) -> list[dict[str, object]]:
        prepared: list[dict[str, object]] = []
        for row in rows(path):
            time_us = float(row["time_us"])
            for series, field in (
                ("Observed C − AC", "observed_excess_C_minus_AC"),
                ("Fitted background", "fitted_background"),
                ("Fitted prompt νμ", "fitted_prompt_nu_mu"),
                ("Fitted delayed νe + anti-νμ", "fitted_delayed_nu_e_plus_anti_nu_mu"),
            ):
                prepared.append(
                    {"time_us": time_us, "events": float(row[field]), "series": series}
                )
        return prepared

    t371_components = component_rows(BINNED_PATH)
    t378_components = component_rows(HOLDOUT_PATH)
    phase_rows = [
        {
            "phase_turn": float(row["phase_turn"]),
            "residual_pct": float(row["residual_pct"]),
            "series": row["series"],
            "source_identity": row["source_identity"],
        }
        for row in rows(PHASE_PATH)
    ]

    key_numbers = [
        {
            "source": "T371 2022 CsI",
            "prompt_yield": results["T371_population_fit"]["prompt_nu_mu"],
            "delayed_yield": results["T371_population_fit"]["delayed_nu_e_plus_anti_nu_mu"],
            "prompt_peak_us": results["T371_population_fit"]["prompt_peak_us_binned"],
            "delayed_peak_us": results["T371_population_fit"]["delayed_peak_us_binned"],
            "handover_us": handover,
            "replication_status": "All T398 gates pass",
        },
        {
            "source": "T378 2017 CsI holdout",
            "prompt_yield": results["T378_independent_holdout"]["prompt_nu_mu"],
            "delayed_yield": results["T378_independent_holdout"]["delayed_nu_e_plus_anti_nu_mu"],
            "prompt_peak_us": results["T378_independent_holdout"]["prompt_peak_us"],
            "delayed_peak_us": results["T378_independent_holdout"]["delayed_peak_us"],
            "handover_us": results["T378_independent_holdout"]["handover_us"],
            "replication_status": "Two populations; strict handover verdict partial",
        },
    ]
    evidence_classes = [
        {
            "curve": "Beam-coincident and anti-coincident event counts",
            "evidence_class": "Measured",
            "claim_allowed": "Population timing observed in CsI",
        },
        {
            "curve": "Prompt and delayed component curves",
            "evidence_class": "Fitted from measured counts",
            "claim_allowed": "Two source populations required by the fit",
        },
        {
            "curve": "Separate νe and anti-νμ children",
            "evidence_class": "Official source templates",
            "claim_allowed": "Flavor-resolved expected shapes, not event flavor tags",
        },
        {
            "curve": "Remaining-muon and cumulative-release shares",
            "evidence_class": "Derived bookkeeping",
            "claim_allowed": "Visual complement of the delayed template",
        },
        {
            "curve": "T397 160 G common-mode spin phase",
            "evidence_class": "Separate experiment",
            "claim_allowed": "Comparison only; no event linkage to COHERENT",
        },
    ]
    gate_rows = [
        {
            "gate": name.replace("_", " "),
            "status": "PASS" if passed else "FAIL",
        }
        for name, passed in results["gates"].items()
    ]
    validation_rows = [
        {
            "check": name.replace("_", " "),
            "status": "PASS" if passed else "FAIL",
        }
        for name, passed in validation["checks"].items()
    ]

    primary = results["T371_population_fit"]
    holdout = results["T378_independent_holdout"]
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    summary = f"""# T398 — Can we see the neutrino release waveform?

## Technical summary

**Yes at the population level; no at the individual-particle level.** The official COHERENT timing data require a delayed neutrino branch after the prompt stopped-pion branch. T398 reconstructs the precursor and release curves on one native time axis and marks their fitted equality at **{handover:.6f} μs**.

- T371 fits **{primary['prompt_nu_mu']:.2f}** prompt νμ events and **{primary['delayed_nu_e_plus_anti_nu_mu']:.2f}** delayed νe + anti-νμ events. Removing the delayed branch costs **{primary['delta_aic_vs_prompt_only']:.2f} AIC units**.
- The delayed child templates divide the fitted branch into **{100*primary['nu_e_template_share_of_delayed']:.2f}% νe** and **{100*primary['anti_nu_mu_template_share_of_delayed']:.2f}% anti-νμ**, and close exactly back to the combined delayed curve.
- The earlier T378 source independently recovers positive prompt and delayed populations in the same order, but retains its published T378 boundary: its highest-stringency frozen handover suite did not fully pass.

The dotted line is therefore a **population branch-equality landmark**, not a timestamp at which one named muon was seen to create two named neutrinos.
"""

    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": "T398 — Population neutrino wave overlap",
            "description": "Evidence-graded overlap of the stopped-pion source, inferred stopped-muon population and delayed neutrino release in COHERENT CsI timing data.",
            "generatedAt": generated_at,
            "cards": [],
            "charts": [
                {
                    "id": "native_stage_overlap",
                    "title": "Native source, inferred muon population and delayed release",
                    "subtitle": "COHERENT 2022 CsI; 25 ns display sample of the 5 ns saved ledger; normalized coordinates",
                    "type": "line",
                    "dataset": "native_source",
                    "sourceId": "t398_native_source",
                    "palette": {"kind": "categorical", "name": "blue-gold"},
                    "referenceLines": [
                        {"axis": "x", "value": handover, "label": f"Branch equality {handover:.3f} μs", "color": "neutral", "lineStyle": "dashed"}
                    ],
                    "encodings": {
                        "x": {"field": "time_us", "type": "quantitative", "label": "Time after SNS pulse (μs)"},
                        "y": {"field": "value", "type": "quantitative", "label": "Normalized wave coordinate (0–1)"},
                        "color": {"field": "series", "type": "nominal", "label": "Evidence curve"},
                        "tooltip": [
                            {"field": "series", "type": "nominal", "label": "Curve"},
                            {"field": "time_us", "type": "quantitative", "label": "Time (μs)"},
                            {"field": "value", "type": "quantitative", "label": "Value"},
                        ],
                    },
                },
                {
                    "id": "delayed_child_templates",
                    "title": "Delayed neutrino child templates",
                    "subtitle": "Official νe and anti-νμ source templates scaled by the T371 fitted delayed yield",
                    "type": "line",
                    "dataset": "delayed_children",
                    "sourceId": "t398_delayed_children",
                    "palette": {"kind": "categorical", "name": "blue-gold"},
                    "referenceLines": [
                        {"axis": "x", "value": handover, "label": f"Branch equality {handover:.3f} μs", "color": "neutral", "lineStyle": "dashed"}
                    ],
                    "encodings": {
                        "x": {"field": "time_us", "type": "quantitative", "label": "Time after SNS pulse (μs)"},
                        "y": {"field": "value", "type": "quantitative", "label": "Contribution / delayed peak"},
                        "color": {"field": "series", "type": "nominal", "label": "Delayed branch"},
                        "tooltip": [
                            {"field": "series", "type": "nominal", "label": "Curve"},
                            {"field": "time_us", "type": "quantitative", "label": "Time (μs)"},
                            {"field": "value", "type": "quantitative", "label": "Value"},
                        ],
                    },
                },
                {
                    "id": "ara_traversal",
                    "title": "Cumulative 0–2 ARA traversal",
                    "subtitle": "Prompt plus delayed fitted release accumulated across the native timing window",
                    "type": "line",
                    "dataset": "ara_traversal",
                    "sourceId": "t398_ara_traversal",
                    "palette": {"kind": "categorical", "name": "blue-gold"},
                    "referenceLines": [
                        {"axis": "x", "value": handover, "label": f"Equality {handover:.3f} μs", "color": "neutral", "lineStyle": "dashed"},
                        {"axis": "y", "value": 0.5, "label": "Child half", "color": "gold", "lineStyle": "dashed"},
                        {"axis": "y", "value": 1.0, "label": "Parent ridge", "color": "neutral", "lineStyle": "solid"},
                        {"axis": "y", "value": 2.0, "label": "Window closure", "color": "neutral", "lineStyle": "dashed"},
                    ],
                    "encodings": {
                        "x": {"field": "time_us", "type": "quantitative", "label": "Time after SNS pulse (μs)"},
                        "y": {"field": "cumulative_ara", "type": "quantitative", "label": "Cumulative ARA coordinate (0–2)"},
                        "tooltip": [
                            {"field": "time_us", "type": "quantitative", "label": "Time (μs)"},
                            {"field": "cumulative_ara", "type": "quantitative", "label": "ARA"},
                        ],
                    },
                },
                {
                    "id": "t371_components",
                    "title": "T371 measured and fitted timing components",
                    "subtitle": "COHERENT 2022 CsI; observed excess and fitted components per 0.5 μs bin",
                    "type": "line",
                    "dataset": "t371_components",
                    "sourceId": "t398_t371_components",
                    "palette": {"kind": "categorical", "name": "blue-gold"},
                    "referenceLines": [
                        {"axis": "x", "value": handover, "label": f"Native equality {handover:.3f} μs", "color": "neutral", "lineStyle": "dashed"},
                        {"axis": "y", "value": 0, "label": "Zero excess", "color": "neutral", "lineStyle": "dashed"},
                    ],
                    "encodings": {
                        "x": {"field": "time_us", "type": "quantitative", "label": "Recoil time (μs)"},
                        "y": {"field": "events", "type": "quantitative", "label": "Events per 0.5 μs bin"},
                        "color": {"field": "series", "type": "nominal", "label": "Measured or fitted component"},
                        "tooltip": [
                            {"field": "series", "type": "nominal", "label": "Component"},
                            {"field": "events", "type": "quantitative", "label": "Events"},
                        ],
                    },
                },
                {
                    "id": "t378_components",
                    "title": "T378 independent holdout timing components",
                    "subtitle": "Earlier COHERENT 2017 CsI release; same event-count units and 0.5 μs bins",
                    "type": "line",
                    "dataset": "t378_components",
                    "sourceId": "t398_t378_components",
                    "palette": {"kind": "categorical", "name": "blue-gold"},
                    "referenceLines": [
                        {"axis": "x", "value": float(holdout["handover_us"]), "label": f"Holdout equality {holdout['handover_us']:.3f} μs", "color": "neutral", "lineStyle": "dashed"},
                        {"axis": "y", "value": 0, "label": "Zero excess", "color": "neutral", "lineStyle": "dashed"},
                    ],
                    "encodings": {
                        "x": {"field": "time_us", "type": "quantitative", "label": "Arrival time (μs)"},
                        "y": {"field": "events", "type": "quantitative", "label": "Events per 0.5 μs bin"},
                        "color": {"field": "series", "type": "nominal", "label": "Measured or fitted component"},
                        "tooltip": [
                            {"field": "series", "type": "nominal", "label": "Component"},
                            {"field": "events", "type": "quantitative", "label": "Events"},
                        ],
                    },
                },
                {
                    "id": "t397_phase",
                    "title": "T397 separate RAL Silver common-mode spin phase",
                    "subtitle": "160 G detector-normalized W residual; separate medium and experiment, shown only for comparison",
                    "type": "line",
                    "dataset": "phase_rows",
                    "sourceId": "t398_t397_phase",
                    "palette": {"kind": "categorical", "name": "blue-gold"},
                    "referenceLines": [
                        {"axis": "y", "value": 0, "label": "Parent envelope", "color": "neutral", "lineStyle": "dashed"}
                    ],
                    "encodings": {
                        "x": {"field": "phase_turn", "type": "quantitative", "label": "Muon spin phase (turns)"},
                        "y": {"field": "residual_pct", "type": "quantitative", "label": "Fractional residual (%)"},
                        "color": {"field": "series", "type": "nominal", "label": "Silver phase trace"},
                        "tooltip": [
                            {"field": "series", "type": "nominal", "label": "Trace"},
                            {"field": "residual_pct", "type": "quantitative", "label": "Residual (%)"},
                        ],
                    },
                },
            ],
            "tables": [
                {
                    "id": "key_numbers",
                    "title": "Population timing comparison",
                    "subtitle": "Primary 2022 source and independent 2017 source; fitted yields and timing landmarks",
                    "dataset": "key_numbers",
                    "sourceId": "t398_results",
                    "columns": [
                        {"field": "source", "label": "Source", "type": "text"},
                        {"field": "prompt_yield", "label": "Prompt yield", "format": "number"},
                        {"field": "delayed_yield", "label": "Delayed yield", "format": "number"},
                        {"field": "prompt_peak_us", "label": "Prompt peak (μs)", "format": "number"},
                        {"field": "delayed_peak_us", "label": "Delayed peak (μs)", "format": "number"},
                        {"field": "handover_us", "label": "Equality (μs)", "format": "number"},
                        {"field": "replication_status", "label": "Boundary", "type": "text"},
                    ],
                },
                {
                    "id": "evidence_classes",
                    "title": "What each visible curve can support",
                    "subtitle": "Measured, fitted, template-resolved, derived and separate-source layers are kept distinct",
                    "dataset": "evidence_classes",
                    "sourceId": "t398_evidence_classes",
                    "columns": [
                        {"field": "curve", "label": "Visible curve", "type": "text"},
                        {"field": "evidence_class", "label": "Evidence class", "type": "text"},
                        {"field": "claim_allowed", "label": "Permitted interpretation", "type": "text"},
                    ],
                },
                {
                    "id": "gate_table",
                    "title": "Frozen T398 gates",
                    "subtitle": "All eight population-waveform and boundary gates passed",
                    "dataset": "gates",
                    "sourceId": "t398_gates",
                    "columns": [
                        {"field": "gate", "label": "Gate", "type": "text"},
                        {"field": "status", "label": "Result", "type": "text"},
                    ],
                },
                {
                    "id": "validation_table",
                    "title": "Independent saved-artifact validation",
                    "subtitle": "A separate script recomputed timing, closure, source separation and claim-boundary checks",
                    "dataset": "validation",
                    "sourceId": "t398_validation",
                    "columns": [
                        {"field": "check", "label": "Check", "type": "text"},
                        {"field": "status", "label": "Status", "type": "text"},
                    ],
                },
            ],
            "sources": [
                {
                    "id": "t398_native_source",
                    "label": "T398 native source and release overlap",
                    "path": "analysis/muon/T398_population_neutrino_wave_overlap/T398_NATIVE_WAVE_OVERLAP.csv",
                    "query": {
                        "engine": "duckdb",
                        "sql": "WITH b AS (SELECT * FROM read_csv_auto('analysis/muon/T398_population_neutrino_wave_overlap/T398_NATIVE_WAVE_OVERLAP.csv')) SELECT time_us, 'Prompt νμ rate (peak = 1)' AS series, prompt_nu_mu_peak_normalized AS value FROM b UNION ALL SELECT time_us, 'Inferred muon remaining', inferred_muon_remaining_fraction FROM b UNION ALL SELECT time_us, 'Delayed νe + anti-νμ rate (peak = 1)', delayed_total_release_peak_normalized FROM b ORDER BY series, time_us",
                        "description": "Prompt rate, derived remaining-muon fraction and delayed rate on the saved T372 native display axis.",
                        "tables_used": ["T398_NATIVE_WAVE_OVERLAP.csv"],
                    },
                },
                {
                    "id": "t398_delayed_children",
                    "label": "T398 delayed neutrino child templates",
                    "path": "analysis/muon/T398_population_neutrino_wave_overlap/T398_NATIVE_WAVE_OVERLAP.csv",
                    "query": {
                        "engine": "duckdb",
                        "sql": "WITH b AS (SELECT * FROM read_csv_auto('analysis/muon/T398_population_neutrino_wave_overlap/T398_NATIVE_WAVE_OVERLAP.csv')) SELECT time_us, 'νe template contribution' AS series, nu_e_release_over_delayed_peak AS value FROM b UNION ALL SELECT time_us, 'anti-νμ template contribution', anti_nu_mu_release_over_delayed_peak FROM b UNION ALL SELECT time_us, 'Combined delayed branch', delayed_total_release_peak_normalized FROM b ORDER BY series, time_us",
                        "description": "Flavor-resolved official source-template components scaled to the fitted combined delayed yield.",
                        "tables_used": ["T398_NATIVE_WAVE_OVERLAP.csv", "snsFlux2D.root"],
                    },
                },
                {
                    "id": "t398_ara_traversal",
                    "label": "T398 cumulative ARA traversal",
                    "path": "analysis/muon/T398_population_neutrino_wave_overlap/T398_NATIVE_WAVE_OVERLAP.csv",
                    "query": {
                        "engine": "duckdb",
                        "sql": "SELECT time_us, cumulative_ara_0_to_2 AS cumulative_ara FROM read_csv_auto('analysis/muon/T398_population_neutrino_wave_overlap/T398_NATIVE_WAVE_OVERLAP.csv') ORDER BY time_us",
                        "description": "Cumulative fitted prompt-plus-delayed release normalized to the ARA 0–2 interval.",
                        "tables_used": ["T398_NATIVE_WAVE_OVERLAP.csv"],
                    },
                },
                {
                    "id": "t398_t371_components",
                    "label": "T371 measured and fitted timing components",
                    "path": "analysis/muon/T398_population_neutrino_wave_overlap/T398_T371_MEASURED_AND_FITTED.csv",
                    "query": {
                        "engine": "duckdb",
                        "sql": "WITH b AS (SELECT * FROM read_csv_auto('analysis/muon/T398_population_neutrino_wave_overlap/T398_T371_MEASURED_AND_FITTED.csv')) SELECT time_us, 'Observed C − AC' AS series, observed_excess_C_minus_AC AS events FROM b UNION ALL SELECT time_us, 'Fitted background', fitted_background FROM b UNION ALL SELECT time_us, 'Fitted prompt νμ', fitted_prompt_nu_mu FROM b UNION ALL SELECT time_us, 'Fitted delayed νe + anti-νμ', fitted_delayed_nu_e_plus_anti_nu_mu FROM b ORDER BY series, time_us",
                        "description": "Measured beam-coincident minus anti-coincident timing and fitted T371 components.",
                        "tables_used": ["T398_T371_MEASURED_AND_FITTED.csv"],
                    },
                },
                {
                    "id": "t398_t378_components",
                    "label": "T378 independent holdout timing components",
                    "path": "analysis/muon/T398_population_neutrino_wave_overlap/T398_T378_INDEPENDENT_HOLDOUT.csv",
                    "query": {
                        "engine": "duckdb",
                        "sql": "WITH b AS (SELECT * FROM read_csv_auto('analysis/muon/T398_population_neutrino_wave_overlap/T398_T378_INDEPENDENT_HOLDOUT.csv')) SELECT time_us, 'Observed C − AC' AS series, observed_excess_C_minus_AC AS events FROM b UNION ALL SELECT time_us, 'Fitted background', fitted_background FROM b UNION ALL SELECT time_us, 'Fitted prompt νμ', fitted_prompt_nu_mu FROM b UNION ALL SELECT time_us, 'Fitted delayed νe + anti-νμ', fitted_delayed_nu_e_plus_anti_nu_mu FROM b ORDER BY series, time_us",
                        "description": "Earlier COHERENT CsI timing release transformed with the frozen T378 fit.",
                        "tables_used": ["T398_T378_INDEPENDENT_HOLDOUT.csv"],
                    },
                },
                {
                    "id": "t398_t397_phase",
                    "label": "T397 separate RAL Silver phase comparison",
                    "path": "analysis/muon/T398_population_neutrino_wave_overlap/T398_T397_SEPARATE_PHASE_COMPARISON.csv",
                    "query": {
                        "engine": "duckdb",
                        "sql": "SELECT phase_turn, residual_pct, series, source_identity FROM read_csv_auto('analysis/muon/T398_population_neutrino_wave_overlap/T398_T397_SEPARATE_PHASE_COMPARISON.csv') ORDER BY series, phase_turn",
                        "description": "The 160 G detector-normalized common-mode phase profile from T397, retained as a visibly separate source.",
                        "tables_used": ["T398_T397_SEPARATE_PHASE_COMPARISON.csv"],
                    },
                },
                {
                    "id": "t398_results",
                    "label": "T398 saved results",
                    "path": "analysis/muon/T398_population_neutrino_wave_overlap/T398_RESULTS.json",
                    "query": {
                        "engine": "duckdb",
                        "sql": "SELECT * FROM read_json_auto('analysis/muon/T398_population_neutrino_wave_overlap/T398_RESULTS.json', format='auto')",
                        "description": "Saved T398 timing, yields, verdict and evidence boundaries.",
                        "tables_used": ["T398_RESULTS.json"],
                    },
                },
                {
                    "id": "t398_protocol",
                    "label": "Frozen T398 protocol",
                    "path": "analysis/muon/T398_POPULATION_NEUTRINO_WAVE_OVERLAP_PROTOCOL_2026-08-17.md",
                    "query": {"engine": "file", "language": "markdown", "description": "Predeclared evidence classes, gates and falsifiers."},
                },
                {
                    "id": "t398_evidence_classes",
                    "label": "T398 evidence-class ledger",
                    "path": "analysis/muon/T398_POPULATION_NEUTRINO_WAVE_OVERLAP_PROTOCOL_2026-08-17.md",
                    "query": {
                        "engine": "duckdb",
                        "sql": "SELECT * FROM (VALUES ('Beam-coincident and anti-coincident event counts','Measured','Population timing observed in CsI'),('Prompt and delayed component curves','Fitted from measured counts','Two source populations required by the fit'),('Separate νe and anti-νμ children','Official source templates','Flavor-resolved expected shapes, not event flavor tags'),('Remaining-muon and cumulative-release shares','Derived bookkeeping','Visual complement of the delayed template'),('T397 160 G common-mode spin phase','Separate experiment','Comparison only; no event linkage to COHERENT')) AS t(curve, evidence_class, claim_allowed)",
                        "description": "The five frozen evidence classes and their permitted interpretations.",
                        "tables_used": ["T398 protocol evidence-class ledger"],
                    },
                },
                {
                    "id": "t398_gates",
                    "label": "T398 frozen gate outcomes",
                    "path": "analysis/muon/T398_population_neutrino_wave_overlap/T398_RESULTS.json",
                    "query": {
                        "engine": "duckdb",
                        "sql": "SELECT replace(j.key, '_', ' ') AS gate, CASE WHEN CAST(j.value AS BOOLEAN) THEN 'PASS' ELSE 'FAIL' END AS status FROM read_json_auto('analysis/muon/T398_population_neutrino_wave_overlap/T398_RESULTS.json', format='auto') AS t, json_each(to_json(t.gates)) AS j ORDER BY j.key",
                        "description": "All predeclared T398 gate outcomes.",
                        "tables_used": ["T398_RESULTS.json"],
                    },
                },
                {
                    "id": "t398_validation",
                    "label": "Independent T398 validation",
                    "path": "analysis/muon/T398_population_neutrino_wave_overlap/T398_VALIDATION.json",
                    "query": {
                        "engine": "duckdb",
                        "sql": "SELECT replace(j.key, '_', ' ') AS check, CASE WHEN CAST(j.value AS BOOLEAN) THEN 'PASS' ELSE 'FAIL' END AS status FROM read_json_auto('analysis/muon/T398_population_neutrino_wave_overlap/T398_VALIDATION.json', format='auto') AS t, json_each(to_json(t.checks)) AS j ORDER BY j.key",
                        "description": "Independent saved-artifact checks.",
                        "tables_used": ["T398_VALIDATION.json"],
                    },
                },
                {"id": "coherent_2022", "label": "COHERENT 2022 CsI measurement and ancillary data", "path": "https://arxiv.org/abs/2110.07730"},
                {"id": "coherent_2017", "label": "COHERENT 2017 CsI public data release", "path": "https://zenodo.org/records/1228631"},
            ],
            "blocks": [
                {"id": "summary", "type": "markdown", "body": summary},
                {
                    "id": "finding_primary",
                    "type": "markdown",
                    "body": "## Key finding 1 — the population handover is visible\n\nThe prompt source branch rises first, while the fitted delayed neutrino branch takes over at the dotted line. The muon-remaining curve is included to make the ARA transfer readable, but it is **derived from the unreleased tail of the delayed template**. It is therefore bookkeeping attached to the observed delayed population, not a second detector measurement.",
                },
                {"id": "native_chart", "type": "chart", "chartId": "native_stage_overlap"},
                {
                    "id": "finding_children",
                    "type": "markdown",
                    "body": "## Key finding 2 — the delayed branch contains two template-resolved children\n\nThe official source file contains separate νe and anti-νμ distributions. After the T371 detector response and delayed-yield normalisation are applied, anti-νμ contributes 61.28% and νe contributes 38.72% of the detector-weighted delayed template. Their pointwise sum is exactly the combined delayed branch. CsI does not label the flavor of each observed event, so these are expected component waves rather than event-by-event tags.",
                },
                {"id": "children_chart", "type": "chart", "chartId": "delayed_child_templates"},
                {
                    "id": "ara_text",
                    "type": "markdown",
                    "body": f"## Key finding 3 — branch equality occurs before parent-ridge accumulation\n\nAt **{handover:.6f} μs**, the instantaneous prompt and delayed fitted rates are equal. The cumulative ARA coordinate is only **{results['handover']['cumulative_ara_at_handover']:.4f}** there. In ARA language, the two flowing branches have handed dominance across while most of the total 0–2 release remains ahead; the equality line is not the same operation as the cumulative 1.0 parent ridge.",
                },
                {"id": "ara_chart", "type": "chart", "chartId": "ara_traversal"},
                {
                    "id": "measured_text",
                    "type": "markdown",
                    "body": f"## The measured counts require the delayed population\n\nThe event-count fit contains backgrounds, a prompt νμ component and a delayed νe + anti-νμ component. The delayed fitted yield is **{primary['delayed_nu_e_plus_anti_nu_mu']:.2f}**, with 95% interval **[{primary['delayed_ci95'][0]:.2f}, {primary['delayed_ci95'][1]:.2f}]**; removing it worsens AIC by **{primary['delta_aic_vs_prompt_only']:.2f}**. This is the empirical layer underneath the smooth native template view.",
                },
                {"id": "measured_chart", "type": "chart", "chartId": "t371_components"},
                {
                    "id": "replication_text",
                    "type": "markdown",
                    "body": f"## The earlier CsI release repeats the ordering, with a weaker strict verdict\n\nThe independent 2017 release again fits a positive prompt population (**{holdout['prompt_nu_mu']:.2f}**) and positive delayed population (**{holdout['delayed_nu_e_plus_anti_nu_mu']:.2f}**), with the delayed peak after the prompt peak. It did not pass every predeclared high-stringency T378 handover gate, so it is supporting replication of the two-stage order rather than a second exact confirmation of the 0.636 μs landmark.",
                },
                {"id": "replication_chart", "type": "chart", "chartId": "t378_components"},
                {"id": "numbers_table", "type": "table", "tableId": "key_numbers"},
                {
                    "id": "separate_source_text",
                    "type": "markdown",
                    "body": "## The silver spin wave remains a separate cut\n\nT397 found a coherent but very small detector-normalized common-mode spin residue. It is shown because it is one of the precursor-like waves already recovered in the muon programme. It is **not** overlaid on the COHERENT time axis: silver μSR and CsI CEvNS do not share muons, events, detector responses or event keys. The current archive therefore cannot test whether this phase trace predicts the delayed COHERENT neutrino branch.",
                },
                {"id": "phase_chart", "type": "chart", "chartId": "t397_phase"},
                {
                    "id": "scope",
                    "type": "markdown",
                    "body": "## Scope, data and definitions\n\n- **Primary identity and medium:** stopped-pion and stopped-muon populations measured through CEvNS in COHERENT CsI[Na].\n- **Prompt branch:** νμ from stopped-pion decay.\n- **Delayed branch:** νe + anti-νμ from stopped-muon decay.\n- **Handover:** instantaneous equality of the fitted prompt and delayed population rates.\n- **Population observation:** many events form a timing distribution.\n- **Individual birth observation:** one parent muon is linked to its own charged daughter and both neutral children. No source used here provides that linkage.\n\nThe report uses 0–6 μs after the SNS pulse. The smooth primary view is displayed at 25 ns spacing from a saved 5 ns ledger reconstructed from 1 ns official templates; event counts remain in the released 0.5 μs bins.",
                },
                {"id": "evidence_table", "type": "table", "tableId": "evidence_classes"},
                {
                    "id": "method",
                    "type": "markdown",
                    "body": "## Methodology\n\nT398 reused the frozen T371 detector response and fitted normalisations, then reopened the official COHERENT source file to keep νe and anti-νμ templates separate. It reconstructed native prompt and delayed rates, verified them against T372 to numerical precision, derived the remaining-muon tail integral, and retained the previously frozen T372 equality solution. The earlier T378 timing components were transformed independently. No T397 value entered the COHERENT reconstruction.",
                },
                {"id": "gates_table", "type": "table", "tableId": "gate_table"},
                {
                    "id": "limitations",
                    "type": "markdown",
                    "body": "## Limitations and robustness\n\n**Supported:** a prompt source population is followed by a statistically required delayed neutrino population; the expected νe and anti-νμ templates form that delayed branch; the ordering repeats in an earlier public source.\n\n**Derived rather than independently observed:** the remaining-muon curve and its complement.\n\n**Not observed:** the exact birth time of an individual neutrino, the two neutral children of one named muon, or a causal link between the RAL Silver spin phase and a COHERENT event.\n\nThe equality time is fit- and detector-dependent. Its T372 bootstrap interval is **[0.5197, 0.7026] μs**. The independent source supports the order but not the same exact coordinate.",
                },
                {"id": "validation_block", "type": "table", "tableId": "validation_table"},
                {
                    "id": "next_steps",
                    "type": "markdown",
                    "body": "## Next step\n\nThe missing experiment is now precise: obtain an event-linked source with parent-muon spin or direction, charged-daughter momentum, and neutral-sensitive timing in the same event record. Apply the same ARA cuts without borrowing a phase curve from another detector. That would test whether a precursor waveform forecasts individual release rather than merely reconstructing the population distribution after many decays.\n\n## Further questions\n\n- Does an event-linked source expose a child traversal wave before the neutral pair appears?\n- Does the equality coordinate move predictably with medium, parent polarisation or detector threshold?\n- Can the neutral pair be resolved independently rather than through source templates?\n- Does the weak T397 common mode replicate in untouched silver data before it is used as a precursor candidate?",
                },
            ],
        },
        "snapshot": {
            "version": 1,
            "generatedAt": generated_at,
            "status": "ready",
            "datasets": {
                "native_source": native_source,
                "delayed_children": delayed_children,
                "ara_traversal": ara_traversal,
                "t371_components": t371_components,
                "t378_components": t378_components,
                "phase_rows": phase_rows,
                "key_numbers": key_numbers,
                "evidence_classes": evidence_classes,
                "gates": gate_rows,
                "validation": validation_rows,
            },
        },
        "sources": [
            {"id": "t398_results", "query": {"engine": "file", "language": "json", "description": "Saved T398 population overlap results."}},
            {"id": "t398_validation", "query": {"engine": "file", "language": "json", "description": "Independent T398 saved-artifact validation."}},
            {"id": "t398_protocol", "query": {"engine": "file", "language": "markdown", "description": "Frozen T398 protocol and claim boundaries."}},
            {"id": "coherent_2022", "query": {"engine": "web", "language": "paper-and-data", "description": "COHERENT 2022 CsI measurement and ancillary release."}},
            {"id": "coherent_2017", "query": {"engine": "web", "language": "dataset", "description": "Independent 2017 COHERENT CsI public data release."}},
        ],
        "package_info": {
            "originUrl": "artifact://t398-population-neutrino-wave-overlap",
            "controls": {"edit": False, "refresh": False},
        },
    }
    ARTIFACT_PATH.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(ARTIFACT_PATH)


if __name__ == "__main__":
    main()

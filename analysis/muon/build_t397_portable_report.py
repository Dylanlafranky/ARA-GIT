#!/usr/bin/env python3
"""Assemble the canonical portable-report artifact for frozen test T397.

The Data Analytics portable artifact builder renders the final HTML. This
script only prepares the reviewed datasets, chart definitions and narrative.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T397_spin_phase_maturity_vs_orientation"
RESULTS_PATH = OUT / "T397_RESULTS.json"
VALIDATION_PATH = OUT / "T397_VALIDATION.json"
RUN_SCORES_PATH = OUT / "T397_RUN_SCORES.csv"
CONTROLS_PATH = OUT / "T397_WRONG_CADENCE_CONTROLS.csv"
PROFILES_PATH = OUT / "T397_PHASE_PROFILES.csv"
SOURCE_PATH = OUT / "T397_SOURCE_MANIFEST.csv"
ARTIFACT_PATH = OUT / "artifact.json"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value: str | float | int | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def main() -> None:
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))

    labels = {
        "O": "Orientation contrast O",
        "U": "Raw total U",
        "V": "Bank-balanced total V",
        "W": "Detector-normalized common mode W",
    }

    field_gains: list[dict[str, object]] = []
    amplitude_rows: list[dict[str, object]] = []
    for channel in ("O", "U", "V", "W"):
        for entry in results["per_field"][channel]:
            field_gains.append(
                {
                    "field_g": entry["field_g"],
                    "channel": labels[channel],
                    "gain_pct": 100.0 * entry["gain"],
                    "run": entry["run"],
                }
            )
            amplitude_rows.append(
                {
                    "field_g": entry["field_g"],
                    "channel": labels[channel],
                    "amplitude_pct": 100.0 * entry["phase_amplitude_fraction"],
                    "run": entry["run"],
                }
            )

    profiles: list[dict[str, object]] = []
    for entry in rows(PROFILES_PATH):
        field = int(float(entry["field_g"]))
        profiles.extend(
            [
                {
                    "phase_turn": float(entry["phase_turn"]),
                    "residual_pct": 100.0 * float(entry["observed_fractional_residual"]),
                    "series": f"{field} G observed",
                    "field_g": field,
                },
                {
                    "phase_turn": float(entry["phase_turn"]),
                    "residual_pct": 100.0 * float(entry["predicted_fractional_residual"]),
                    "series": f"{field} G fitted phase",
                    "field_g": field,
                },
            ]
        )

    cadence: list[dict[str, object]] = []
    for entry in rows(CONTROLS_PATH):
        if entry["run"] != "POOLED" or entry["channel"] not in {"O", "W"}:
            continue
        if not entry["control"].startswith("multiplier_"):
            continue
        multiplier = float(entry["control"].replace("multiplier_", ""))
        cadence.append(
            {
                "cadence_multiplier": multiplier,
                "gain_pct": 100.0 * float(entry["gain"]),
                "channel": labels[entry["channel"]],
                "status": "wrong cadence",
            }
        )
    for channel in ("O", "W"):
        cadence.append(
            {
                "cadence_multiplier": 1.0,
                "gain_pct": 100.0 * results["primary_pooled_gain"][channel],
                "channel": labels[channel],
                "status": "physical cadence",
            }
        )
    cadence.sort(key=lambda entry: (str(entry["channel"]), float(entry["cadence_multiplier"])))

    gate_rows: list[dict[str, str]] = []
    for family, components in (
        ("Orientation", results["gates"]["orientation_components"]),
        ("Maturity", results["gates"]["maturity_components"]),
    ):
        for name, passed in components.items():
            gate_rows.append(
                {
                    "family": family,
                    "gate": name.replace("_", " ").capitalize(),
                    "status": "PASS" if passed else "FAIL",
                }
            )

    validation_rows = [
        {
            "check": name.replace("_", " ").capitalize(),
            "status": "PASS" if passed else "FAIL",
        }
        for name, passed in validation["checks"].items()
    ]

    source_rows: list[dict[str, object]] = []
    for entry in rows(SOURCE_PATH):
        source_rows.append(
            {
                "run": entry["run"],
                "split": entry["split"],
                "field_g": float(entry["field_g"]),
                "temperature_k": float(entry["temperature_k"]),
                "detectors": int(entry["detectors"]),
                "native_bins": int(entry["native_bins"]),
                "quality": "PASS" if entry["all_quality_gates_pass"].lower() == "true" else "FAIL",
            }
        )

    primary = results["primary_pooled_gain"]
    ci = results["bootstrap_95_gain"]
    w = results["w_common_mode"]
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    summary = f"""# T397 - Spin phase: maturity clock or orientation organiser?

## Technical summary

The frozen detector-level test returned **ORIENTATION SUPPORTED; MATURITY NOT SUPPORTED**.

- The full 96-detector orientation field reduced held-out weighted squared error by **{100*primary['O']:.2f}%**, with hierarchical 95% interval **[{100*ci['O'][0]:.2f}%, {100*ci['O'][1]:.2f}%]**.
- The strict detector-normalized common mode reduced error by only **{100*primary['W']:.3f}%**, with interval **[{100*ci['W'][0]:.3f}%, {100*ci['W'][1]:.3f}%]**. Its fitted phase amplitude was **{100*w['mean_phase_amplitude_fraction']:.4f}%** of the parent envelope.
- The common-mode phase was coherent across fields (resultant length **{w['phase_resultant_length']:.3f}**) and beat the wrong-cadence envelope, but it changed sign at 400 G and failed the reverse-parity field-consistency gate.

Within this 300 K RAL Silver population, spin phase therefore behaves as a strong **orientation organiser** for the charged daughter. A weak population-wide release residue remains a lead, not a confirmed neutrino-creation clock.
"""

    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": "T397 - Spin phase maturity versus orientation",
            "description": "Frozen ARA-first detector-level test of whether muon spin phase marks population release maturity or only daughter orientation.",
            "generatedAt": generated_at,
            "cards": [],
            "charts": [
                {
                    "id": "field_gains",
                    "title": "Orientation generalises; parent totals do not",
                    "subtitle": "Held-out relative weighted-SSE gain by magnetic field. Positive is better than the no-phase baseline.",
                    "type": "line",
                    "dataset": "field_gains",
                    "sourceId": "t397_run_scores_field_gain",
                    "palette": {"kind": "categorical", "name": "blue-gold"},
                    "referenceLines": [
                        {"axis": "y", "value": 0, "label": "No phase gain", "color": "neutral", "lineStyle": "dashed"}
                    ],
                    "encodings": {
                        "x": {"field": "field_g", "type": "quantitative", "label": "Applied magnetic field (G)"},
                        "y": {"field": "gain_pct", "type": "quantitative", "label": "Held-out SSE gain (%)"},
                        "color": {"field": "channel", "type": "nominal", "label": "ARA cut"},
                        "tooltip": [
                            {"field": "run", "type": "nominal", "label": "EMU run"},
                            {"field": "gain_pct", "type": "quantitative", "label": "Gain (%)"},
                        ],
                    },
                },
                {
                    "id": "w_phase_profiles",
                    "title": "The strict common mode contains only a tiny phase-shaped residue",
                    "subtitle": "Phase-folded W residuals after the exponential parent envelope was removed; one turn equals 2*pi spin phase.",
                    "type": "line",
                    "dataset": "w_phase_profiles",
                    "sourceId": "t397_phase_profiles",
                    "palette": {"kind": "categorical", "name": "blue-gold"},
                    "referenceLines": [
                        {"axis": "y", "value": 0, "label": "Parent envelope", "color": "neutral", "lineStyle": "dashed"}
                    ],
                    "encodings": {
                        "x": {"field": "phase_turn", "type": "quantitative", "label": "Muon spin phase (turns)"},
                        "y": {"field": "residual_pct", "type": "quantitative", "label": "Fractional residual (%)"},
                        "color": {"field": "series", "type": "nominal", "label": "Field and trace"},
                        "tooltip": [
                            {"field": "field_g", "type": "quantitative", "label": "Field (G)"},
                            {"field": "residual_pct", "type": "quantitative", "label": "Residual (%)"},
                        ],
                    },
                },
                {
                    "id": "cadence_controls",
                    "title": "The physical spin cadence is the strongest tested cadence",
                    "subtitle": "Pooled held-out gain for the physical frequency (1.0) and predeclared wrong-frequency multipliers.",
                    "type": "line",
                    "dataset": "cadence_controls",
                    "sourceId": "t397_cadence_controls",
                    "palette": {"kind": "categorical", "name": "blue-gold"},
                    "referenceLines": [
                        {"axis": "x", "value": 1, "label": "Physical cadence", "color": "gold", "lineStyle": "solid"},
                        {"axis": "y", "value": 0, "label": "No phase gain", "color": "neutral", "lineStyle": "dashed"},
                    ],
                    "encodings": {
                        "x": {"field": "cadence_multiplier", "type": "quantitative", "label": "Frequency multiplier"},
                        "y": {"field": "gain_pct", "type": "quantitative", "label": "Held-out SSE gain (%)"},
                        "color": {"field": "channel", "type": "nominal", "label": "ARA cut"},
                        "tooltip": [
                            {"field": "status", "type": "nominal", "label": "Cadence class"},
                            {"field": "gain_pct", "type": "quantitative", "label": "Gain (%)"},
                        ],
                    },
                },
                {
                    "id": "phase_amplitudes",
                    "title": "Orientation is much larger than the common-mode residue",
                    "subtitle": "Fitted phase amplitude as a percentage of each parent envelope.",
                    "type": "line",
                    "dataset": "phase_amplitudes",
                    "sourceId": "t397_run_scores_phase_amplitude",
                    "palette": {"kind": "categorical", "name": "blue-gold"},
                    "encodings": {
                        "x": {"field": "field_g", "type": "quantitative", "label": "Applied magnetic field (G)"},
                        "y": {"field": "amplitude_pct", "type": "quantitative", "label": "Phase amplitude / parent envelope (%)"},
                        "color": {"field": "channel", "type": "nominal", "label": "ARA cut"},
                        "tooltip": [
                            {"field": "run", "type": "nominal", "label": "EMU run"},
                            {"field": "amplitude_pct", "type": "quantitative", "label": "Amplitude (%)"},
                        ],
                    },
                },
            ],
            "tables": [
                {
                    "id": "gate_table",
                    "title": "Frozen decision gates",
                    "subtitle": "The orientation family passed; the stronger maturity family did not.",
                    "dataset": "gates",
                    "sourceId": "t397_gate_results",
                    "columns": [
                        {"field": "family", "label": "Claim family", "type": "text"},
                        {"field": "gate", "label": "Frozen gate", "type": "text"},
                        {"field": "status", "label": "Result", "type": "text"},
                    ],
                },
                {
                    "id": "source_table",
                    "title": "Source partition",
                    "subtitle": "All runs used the same RAL Silver medium at 300 K and the same 96-detector EMU geometry.",
                    "dataset": "source_runs",
                    "sourceId": "t397_source_manifest",
                    "columns": [
                        {"field": "run", "label": "EMU run", "type": "text"},
                        {"field": "split", "label": "Split", "type": "text"},
                        {"field": "field_g", "label": "Field (G)", "format": "number"},
                        {"field": "temperature_k", "label": "Temperature (K)", "format": "number"},
                        {"field": "detectors", "label": "Detectors", "format": "number"},
                        {"field": "native_bins", "label": "Native bins", "format": "number"},
                        {"field": "quality", "label": "Source QA", "type": "text"},
                    ],
                },
                {
                    "id": "validation_table",
                    "title": "Independent artifact validation",
                    "subtitle": "A separate script reconstructed principal numbers and gates from saved outputs.",
                    "dataset": "validation_checks",
                    "sourceId": "t397_validation_checks",
                    "columns": [
                        {"field": "check", "label": "Check", "type": "text"},
                        {"field": "status", "label": "Status", "type": "text"},
                    ],
                },
            ],
            "sources": [
                {
                    "id": "t397_run_scores_field_gain",
                    "label": "T397 held-out field gains",
                    "path": "analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_RUN_SCORES.csv",
                    "query": {
                        "engine": "duckdb",
                        "sql": "SELECT CAST(field_g AS DOUBLE) AS field_g, CASE channel WHEN 'O' THEN 'Orientation contrast O' WHEN 'U' THEN 'Raw total U' WHEN 'V' THEN 'Bank-balanced total V' ELSE 'Detector-normalized common mode W' END AS channel, 100 * CAST(gain AS DOUBLE) AS gain_pct, run FROM read_csv_auto('analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_RUN_SCORES.csv') WHERE score_family = 'primary' AND run <> 'POOLED' AND channel IN ('O','U','V','W') ORDER BY channel, field_g",
                        "description": "Primary per-field held-out weighted-SSE gains for the four frozen ARA cuts.",
                        "tables_used": ["T397_RUN_SCORES.csv"],
                        "filters": ["score_family = primary", "exclude pooled rows"],
                        "metric_definitions": {"gain_pct": "100 * (null_sse - phase_sse) / null_sse"},
                    },
                },
                {
                    "id": "t397_run_scores_phase_amplitude",
                    "label": "T397 phase amplitude by field",
                    "path": "analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_RUN_SCORES.csv",
                    "query": {
                        "engine": "duckdb",
                        "sql": "SELECT CAST(field_g AS DOUBLE) AS field_g, CASE channel WHEN 'O' THEN 'Orientation contrast O' WHEN 'U' THEN 'Raw total U' WHEN 'V' THEN 'Bank-balanced total V' ELSE 'Detector-normalized common mode W' END AS channel, 100 * CAST(phase_amplitude_fraction AS DOUBLE) AS amplitude_pct, run FROM read_csv_auto('analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_RUN_SCORES.csv') WHERE score_family = 'primary' AND run <> 'POOLED' AND channel IN ('O','U','V','W') ORDER BY channel, field_g",
                        "description": "Fitted phase amplitude relative to each channel's parent envelope.",
                        "tables_used": ["T397_RUN_SCORES.csv"],
                        "filters": ["score_family = primary", "exclude pooled rows"],
                        "metric_definitions": {"amplitude_pct": "100 * phase_amplitude_fraction"},
                    },
                },
                {
                    "id": "t397_phase_profiles",
                    "label": "T397 strict common-mode phase profiles",
                    "path": "analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_PHASE_PROFILES.csv",
                    "query": {
                        "engine": "duckdb",
                        "sql": "SELECT CAST(phase_turn AS DOUBLE) AS phase_turn, 100 * CAST(observed_fractional_residual AS DOUBLE) AS residual_pct, CAST(CAST(field_g AS INTEGER) AS VARCHAR) || ' G observed' AS series, CAST(field_g AS INTEGER) AS field_g FROM read_csv_auto('analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_PHASE_PROFILES.csv') UNION ALL SELECT CAST(phase_turn AS DOUBLE), 100 * CAST(predicted_fractional_residual AS DOUBLE), CAST(CAST(field_g AS INTEGER) AS VARCHAR) || ' G fitted phase', CAST(field_g AS INTEGER) FROM read_csv_auto('analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_PHASE_PROFILES.csv') ORDER BY field_g, series, phase_turn",
                        "description": "Observed and odd-cycle-trained W phase profiles at each held-out field.",
                        "tables_used": ["T397_PHASE_PROFILES.csv"],
                        "metric_definitions": {"residual_pct": "100 * fractional residual after the exponential parent envelope"},
                    },
                },
                {
                    "id": "t397_cadence_controls",
                    "label": "T397 cadence controls",
                    "path": "analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_WRONG_CADENCE_CONTROLS.csv",
                    "query": {
                        "engine": "duckdb",
                        "sql": "WITH wrong AS (SELECT CAST(replace(control,'multiplier_','') AS DOUBLE) AS cadence_multiplier, 100 * CAST(gain AS DOUBLE) AS gain_pct, CASE channel WHEN 'O' THEN 'Orientation contrast O' ELSE 'Detector-normalized common mode W' END AS channel, 'wrong cadence' AS status FROM read_csv_auto('analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_WRONG_CADENCE_CONTROLS.csv') WHERE run = 'POOLED' AND channel IN ('O','W') AND control LIKE 'multiplier_%'), physical AS (SELECT 1.0 AS cadence_multiplier, 100 * CAST(gain AS DOUBLE) AS gain_pct, CASE channel WHEN 'O' THEN 'Orientation contrast O' ELSE 'Detector-normalized common mode W' END AS channel, 'physical cadence' AS status FROM read_csv_auto('analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_RUN_SCORES.csv') WHERE score_family = 'primary' AND run = 'POOLED' AND channel IN ('O','W')) SELECT * FROM wrong UNION ALL SELECT * FROM physical ORDER BY channel, cadence_multiplier",
                        "description": "Pooled physical-cadence score compared with all predeclared wrong-frequency multipliers.",
                        "tables_used": ["T397_WRONG_CADENCE_CONTROLS.csv", "T397_RUN_SCORES.csv"],
                        "metric_definitions": {"gain_pct": "100 * held-out relative weighted-SSE gain"},
                    },
                },
                {
                    "id": "t397_gate_results",
                    "label": "T397 frozen gate results",
                    "path": "analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_RESULTS.json",
                    "query": {
                        "engine": "duckdb",
                        "sql": "SELECT * FROM (VALUES ('Orientation','Positive each field','PASS'),('Orientation','Bootstrap lower above zero','PASS'),('Orientation','Beats every wrong cadence','PASS'),('Maturity','Orientation recovered','PASS'),('Maturity','W positive each field','FAIL'),('Maturity','W bootstrap lower above zero','FAIL'),('Maturity','W beats wrong cadence 97.5','PASS'),('Maturity','W phase resultant at least 0.70','PASS'),('Maturity','W survives acceptance ladder','PASS'),('Maturity','Reverse W nonnegative each field','FAIL')) AS t(family, gate, status)",
                        "description": "Verbatim frozen gate outcomes saved in T397_RESULTS.json.",
                        "tables_used": ["T397_RESULTS.json"],
                    },
                },
                {
                    "id": "t397_source_manifest",
                    "label": "T397 source partition",
                    "path": "analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_SOURCE_MANIFEST.csv",
                    "query": {
                        "engine": "duckdb",
                        "sql": "SELECT run, split, CAST(field_g AS DOUBLE) AS field_g, CAST(temperature_k AS DOUBLE) AS temperature_k, CAST(detectors AS INTEGER) AS detectors, CAST(native_bins AS INTEGER) AS native_bins, CASE WHEN lower(CAST(all_quality_gates_pass AS VARCHAR)) = 'true' THEN 'PASS' ELSE 'FAIL' END AS quality FROM read_csv_auto('analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_SOURCE_MANIFEST.csv') ORDER BY CASE split WHEN 'calibration' THEN 1 WHEN 'validation' THEN 2 ELSE 3 END, run",
                        "description": "Run split, field, medium temperature, detector count, native bins and quality gate.",
                        "tables_used": ["T397_SOURCE_MANIFEST.csv"],
                    },
                },
                {
                    "id": "t397_validation_checks",
                    "label": "T397 independent validation checks",
                    "path": "analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_VALIDATION.json",
                    "query": {
                        "engine": "duckdb",
                        "sql": "SELECT initcap(replace(j.key, '_', ' ')) AS check, CASE WHEN CAST(j.value AS BOOLEAN) THEN 'PASS' ELSE 'FAIL' END AS status FROM read_json_auto('analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_VALIDATION.json', format='auto') AS t, json_each(to_json(t.checks)) AS j ORDER BY j.key",
                        "description": "Independent recomputation checks from the saved T397 validation artifact.",
                        "tables_used": ["T397_VALIDATION.json"],
                    },
                },
                {"id": "ral_silver_source", "label": "ISIS experiment RB1620201", "path": "https://doi.org/10.5286/ISIS.E.RB1620201"},
                {"id": "emu_manual", "label": "Official ISIS EMU user guide", "path": "https://www.isis.stfc.ac.uk/Pages/emu-manual15431.pdf"},
            ],
            "blocks": [
                {"id": "summary", "type": "markdown", "body": summary},
                {
                    "id": "finding_one_text",
                    "type": "markdown",
                    "body": "## Key finding 1 - spin phase carries direction\n\nThe signed detector contrast O stayed positive at 63, 160 and 400 G and its hierarchical confidence interval excluded zero. This is the expected pattern if the spin waveform organises **where** the charged daughter appears. The percentage is an error-reduction score, not a decay probability or released-energy share.",
                },
                {"id": "field_gains_chart", "type": "chart", "chartId": "field_gains"},
                {
                    "id": "finding_two_text",
                    "type": "markdown",
                    "body": "## Key finding 2 - the population release residue is small and unstable\n\nAcceptance equalisation exposes a coherent W-phase trace, but its magnitude is about six hundredths of one percent of the parent envelope. The pooled gain is positive and cadence-specific, yet the field-level sign change and confidence interval spanning zero prevent promotion to a release clock. The visible trace is a candidate residual coupling, not evidence that an individual neutrino creation time was measured.",
                },
                {"id": "profiles_chart", "type": "chart", "chartId": "w_phase_profiles"},
                {
                    "id": "controls_text",
                    "type": "markdown",
                    "body": "## Key finding 3 - the physical cadence matters, but cadence alone is insufficient\n\nBoth the orientation field and strict common mode scored best at the independently known spin frequency. That rejects a generic smooth-wave explanation within the tested multiplier family. It does not repair the failed maturity gates: a cadence-specific residual can arise from imperfect detector cancellation or another weak coupling without being a population release clock.",
                },
                {"id": "cadence_chart", "type": "chart", "chartId": "cadence_controls"},
                {"id": "amplitudes_chart", "type": "chart", "chartId": "phase_amplitudes"},
                {
                    "id": "scope",
                    "type": "markdown",
                    "body": "## Scope, identities and ARA cuts\n\n- **Identity:** positive-muon populations in 300 K RAL Silver.\n- **Parent envelope:** exponential population survival over 0.25-8.00 microseconds.\n- **Orientation child O:** signed structure across all 96 detectors.\n- **Raw parent total U:** forward plus backward counts.\n- **Bank-balanced total V:** forward plus calibration-only alpha times backward.\n- **Strict common mode W:** all detectors normalized by calibration-only detector shares, then summed.\n- **ARA question:** does the muon waveform only orient the released charged child, or does a same-phase trace survive in an acceptance-balanced parent total strongly enough to act as a population maturity coordinate?\n\nThe archive contains population histograms, not named parent-daughter events. T397 therefore cannot directly observe either neutrino or predict one muon's exact decay time.",
                },
                {
                    "id": "method",
                    "type": "markdown",
                    "body": "## Frozen method\n\nThe protocol fixed the muon lifetime at 2.1928 microseconds and the spin-frequency conversion at 0.01382 MHz/G. Calibration runs learned only detector acceptance and forward/backward balance. For each held-out field, odd spin cycles fitted cosine and sine coefficients and even cycles were scored; parity was reversed as a sensitivity test. The null was the same exponential parent without a phase term. Wrong-cadence multipliers, field permutation, the U-to-V-to-W acceptance ladder and a hierarchical cycle-plus-field bootstrap were frozen before final scoring.",
                },
                {"id": "gate_table_block", "type": "table", "tableId": "gate_table"},
                {"id": "source_table_block", "type": "table", "tableId": "source_table"},
                {
                    "id": "limitations",
                    "type": "markdown",
                    "body": "## Robustness and limitations\n\n**Supported:** spin phase generalises as a detector-orientation organiser across all three held-out fields.\n\n**Unresolved lead:** W is phase-coherent and narrowly cadence-specific, but its pooled 95% interval crosses zero, 400 G reverses sign and reverse parity fails field consistency.\n\n**Not supported:** a universal spin-phase maturity clock, an individual neutrino-creation timestamp, a restored 7.5-turn trigger or new particle physics.\n\nThe source was used in earlier muon analyses. T397 is a locked new question on an already inspected source, not a source-blind replication. The result may still contain detector-acceptance leakage. Independent validation classifies it as ready to share only with these caveats.",
                },
                {"id": "validation_table_block", "type": "table", "tableId": "validation_table"},
                {
                    "id": "next_steps",
                    "type": "markdown",
                    "body": "## Next test\n\nFreeze the same O/U/V/W construction on an untouched same-medium EMU silver series, preserving 96-detector data and using calibration runs from that series only. The decisive replication asks whether W remains positive at each field, keeps a non-zero hierarchical interval and survives reverse parity while O again passes. If W fails, spin should remain classified as an orientation organiser. If W passes, the next rung is an event-linked archive with independently observed charged-daughter direction and a neutral-sensitive target.\n\n## Further questions\n\n- Is the small W residue physical or residual detector acceptance?\n- Why does its sign change at 400 G?\n- Does the phase angle transfer across independent silver campaigns?\n- Can event-linked data separate population maturity from individual decay timing?",
                },
            ],
        },
        "snapshot": {
            "version": 1,
            "generatedAt": generated_at,
            "status": "ready",
            "datasets": {
                "field_gains": field_gains,
                "phase_amplitudes": amplitude_rows,
                "w_phase_profiles": profiles,
                "cadence_controls": cadence,
                "gates": gate_rows,
                "source_runs": source_rows,
                "validation_checks": validation_rows,
            },
        },
        "sources": [
            {"id": "t397_results", "query": {"engine": "file", "language": "json", "description": "Saved frozen T397 results."}},
            {"id": "t397_validation", "query": {"engine": "file", "language": "json", "description": "Independent T397 result and gate validation."}},
            {"id": "t397_protocol", "query": {"engine": "file", "language": "markdown", "description": "Predeclared T397 protocol."}},
            {"id": "ral_silver_source", "query": {"engine": "web", "language": "dataset", "description": "Official ISIS experiment DOI and data record."}},
            {"id": "emu_manual", "query": {"engine": "web", "language": "documentation", "description": "Official EMU detector geometry and instrument guide."}},
        ],
        "package_info": {
            "originUrl": "artifact://t397-spin-phase-maturity-vs-orientation",
            "controls": {"edit": False, "refresh": False},
        },
    }

    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(ARTIFACT_PATH)


if __name__ == "__main__":
    main()

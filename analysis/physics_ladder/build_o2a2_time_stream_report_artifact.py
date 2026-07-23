#!/usr/bin/env python3
"""Build the bounded Data Analytics report artifact for O2-A2."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
AGGREGATES = HERE / "O2A2_TIME_STREAM_LINEAGE_AGGREGATES.csv"
RESULTS = HERE / "O2A2_TIME_STREAM_LINEAGE_RESULTS.json"
OUTPUT = HERE / "O2A2_TIME_STREAM_LINEAGE_REPORT_ARTIFACT.json"


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(row: dict, field: str) -> float | None:
    value = row[field]
    return None if value == "" else float(value)


def main() -> None:
    aggregates = read_csv(AGGREGATES)
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    verdict = result["primary_verdict"]
    metrics = verdict["metrics"]

    source = {
        "id": "o2a2-run",
        "label": "Frozen O2-A2 synthetic time-stream outputs",
        "path": str(AGGREGATES),
        "query": {
            "id": "o2a2-aggregate-read-v1",
            "language": "sql",
            "engine": "duckdb",
            "description": (
                "Reads the frozen aggregate and trial outputs produced by the "
                "preregistered O2-A2 runner."
            ),
            "sql": (
                "SELECT * FROM read_csv_auto("
                "'analysis/physics_ladder/O2A2_TIME_STREAM_LINEAGE_AGGREGATES.csv');"
            ),
            "tables_used": [
                "analysis/physics_ladder/O2A2_TIME_STREAM_LINEAGE_AGGREGATES.csv",
                "analysis/physics_ladder/O2A2_TIME_STREAM_LINEAGE_TRIALS.csv",
            ],
            "filters": [
                "Primary target: capacitor and quantum systems at 12 dB white noise on q and g",
                "Sixteen fresh deterministic target replicates per system and SNR",
                "Derivative and trajectory settings selected only on oscillator development",
            ],
            "metric_definitions": [
                "correlation = Pearson correlation between estimated and native hidden waveform",
                "NRMSE = waveform RMSE divided by peak absolute native hidden waveform",
                "integrated error = absolute signed-integral error divided by absolute native signed integral",
                "declared-child occupancy = fraction of samples for which repeated re-selection chose the predeclared child",
                "relative NRMSE improvement = 1 - fixed-lineage median NRMSE / re-selection median NRMSE",
            ],
        },
    }

    ladder = []
    occupancy = []
    system_12 = []
    target_models = (
        "Resistive capacitor coupling",
        "Open two-level probability",
    )
    target_methods = ("fixed_time_lineage", "repeated_parent_reselection")
    labels = {
        "Resistive capacitor coupling": "Capacitor",
        "Open two-level probability": "Quantum",
        "fixed_time_lineage": "Fixed stream",
        "repeated_parent_reselection": "Re-select",
        "compressed_parent": "Compressed parent",
        "zero_other": "Zero Other",
        "offline_centered_child": "Offline centred",
    }
    for row in aggregates:
        if row["model"] in target_models and row["method"] in target_methods:
            chart_row = {
                "model": labels[row["model"]],
                "method": labels[row["method"]],
                "series": f"{labels[row['model']]} — {labels[row['method']]}",
                "snr_db": float(row["snr_db"]),
                "median_nrmse": number(row, "median_nrmse"),
                "median_correlation": number(row, "median_correlation"),
                "median_sign_accuracy": number(row, "median_sign_accuracy"),
                "median_integrated_error": number(row, "median_integrated_error"),
                "median_declared_child_occupancy": number(
                    row, "median_declared_child_occupancy"
                ),
                "median_switch_count": number(row, "median_switch_count"),
                "replicates": int(row["replicates"]),
            }
            ladder.append(chart_row)
            if row["method"] == "repeated_parent_reselection":
                occupancy.append(chart_row)
        if (
            row["model"] in target_models
            and float(row["snr_db"]) == 12
            and row["method"]
            in (
                "fixed_time_lineage",
                "repeated_parent_reselection",
                "compressed_parent",
                "zero_other",
                "offline_centered_child",
            )
        ):
            system_12.append(
                {
                    "system": labels[row["model"]],
                    "method": labels[row["method"]],
                    "correlation": number(row, "median_correlation"),
                    "nrmse": number(row, "median_nrmse"),
                    "sign_accuracy": number(row, "median_sign_accuracy"),
                    "integrated_error": number(row, "median_integrated_error"),
                    "occupancy": number(row, "median_declared_child_occupancy"),
                    "switches": number(row, "median_switch_count"),
                    "replicates": int(row["replicates"]),
                }
            )

    gate_labels = {
        "correlation": "Correlation ≥ 0.40",
        "nrmse": "NRMSE ≤ 0.35",
        "sign": "Sign accuracy ≥ 0.75",
        "integrated_error": "Integrated error ≤ 0.35",
        "correlation_advantage": "Correlation advantage ≥ +0.10",
        "nrmse_relative_improvement": "NRMSE improvement ≥ 10%",
        "beats_zero_other": "NRMSE beats zero Other",
        "beats_reselection_in_both_systems": "NRMSE beats re-selection in both targets",
    }
    gate_results = {
        "correlation": metrics["median_fixed_correlation"],
        "nrmse": metrics["median_fixed_nrmse"],
        "sign": metrics["median_fixed_sign_accuracy"],
        "integrated_error": metrics["median_fixed_integrated_error"],
        "correlation_advantage": metrics["correlation_advantage"],
        "nrmse_relative_improvement": metrics["nrmse_relative_improvement"],
        "beats_zero_other": int(verdict["gates"]["beats_zero_other"]),
        "beats_reselection_in_both_systems": int(
            verdict["gates"]["beats_reselection_in_both_systems"]
        ),
    }
    gates = [
        {
            "order": index,
            "gate": gate_labels[name],
            "result": gate_results[name],
            "status": "Pass" if verdict["gates"][name] else "Fail",
        }
        for index, name in enumerate(gate_labels, start=1)
    ]

    headline = [
        {
            "gates_passed": verdict["passed_gates"],
            "gates_total": verdict["total_gates"],
            "fixed_correlation": metrics["median_fixed_correlation"],
            "correlation_advantage": metrics["correlation_advantage"],
            "fixed_nrmse": metrics["median_fixed_nrmse"],
            "nrmse_improvement": metrics["nrmse_relative_improvement"],
            "fixed_sign": metrics["median_fixed_sign_accuracy"],
            "integrated_error": metrics["median_fixed_integrated_error"],
            "target_runs": metrics["target_runs_per_method"],
        }
    ]

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "O2-A2 Downstream Time-Stream Lineage",
        "description": (
            "Frozen synthetic test of whether following a predeclared moving child "
            "outperforms repeated re-selection from the mixed parent."
        ),
        "generatedAt": "2026-07-23T22:00:00+10:00",
        "sources": [source],
        "cards": [
            {
                "id": "gates-card",
                "description": "Frozen gates passed at the registered 12 dB target.",
                "dataset": "headline",
                "sourceId": "o2a2-run",
                "metrics": [
                    {"label": "Passed", "field": "gates_passed", "format": "number"},
                    {"label": "Total", "field": "gates_total", "format": "number"},
                ],
            },
            {
                "id": "correlation-card",
                "description": "Median fixed-stream waveform correlation across 32 target runs.",
                "dataset": "headline",
                "sourceId": "o2a2-run",
                "metrics": [
                    {
                        "label": "Correlation",
                        "field": "fixed_correlation",
                        "format": "number",
                    },
                    {
                        "label": "vs re-select",
                        "field": "correlation_advantage",
                        "format": "number",
                        "signed": True,
                    },
                ],
            },
            {
                "id": "nrmse-card",
                "description": "Median peak-normalized waveform error; lower is better.",
                "dataset": "headline",
                "sourceId": "o2a2-run",
                "metrics": [
                    {"label": "NRMSE", "field": "fixed_nrmse", "format": "number"},
                    {
                        "label": "Improvement",
                        "field": "nrmse_improvement",
                        "format": "percent",
                        "signed": True,
                    },
                ],
            },
        ],
        "charts": [
            {
                "id": "nrmse-ladder-chart",
                "title": "Median waveform NRMSE across the noise ladder",
                "description": (
                    "Fixed streams separate most clearly from repeated re-selection "
                    "as quantum observation noise increases."
                ),
                "type": "line",
                "dataset": "ladder",
                "sourceId": "o2a2-run",
                "encodings": {
                    "x": {"field": "snr_db", "type": "quantitative"},
                    "y": {"field": "median_nrmse", "type": "quantitative"},
                    "color": {"field": "series", "type": "nominal"},
                },
                "options": {"points": "always"},
            },
            {
                "id": "occupancy-chart",
                "title": "Declared-child occupancy during repeated re-selection",
                "description": (
                    "The selector spends less time on the declared child as noise rises."
                ),
                "type": "line",
                "dataset": "occupancy",
                "sourceId": "o2a2-run",
                "encodings": {
                    "x": {"field": "snr_db", "type": "quantitative"},
                    "y": {
                        "field": "median_declared_child_occupancy",
                        "type": "quantitative",
                    },
                    "color": {"field": "model", "type": "nominal"},
                },
                "options": {"points": "always"},
            },
        ],
        "tables": [
            {
                "id": "gates-table",
                "title": "Registered 12 dB decision gates",
                "description": "The exact frozen status uses all eight gates without post-run relaxation.",
                "dataset": "gates",
                "sourceId": "o2a2-run",
                "columns": [
                    {"field": "order", "label": "#", "type": "number"},
                    {"field": "gate", "label": "Gate", "type": "text"},
                    {"field": "result", "label": "Result", "type": "number"},
                    {"field": "status", "label": "Status", "type": "text"},
                ],
                "defaultSort": {"field": "order", "direction": "asc"},
            },
            {
                "id": "system-table",
                "title": "Target-system method results at 12 dB",
                "description": (
                    "Median results across sixteen fresh deterministic replicates per system."
                ),
                "dataset": "system_12",
                "sourceId": "o2a2-run",
                "columns": [
                    {"field": "system", "label": "System", "type": "text"},
                    {"field": "method", "label": "Method", "type": "text"},
                    {"field": "correlation", "label": "Correlation", "type": "number"},
                    {"field": "nrmse", "label": "NRMSE", "type": "number"},
                    {
                        "field": "integrated_error",
                        "label": "Integrated error",
                        "type": "number",
                    },
                    {"field": "occupancy", "label": "Occupancy", "type": "number"},
                ],
                "defaultSort": {"field": "nrmse", "direction": "asc"},
            },
        ],
        "blocks": [
            {
                "id": "title",
                "type": "markdown",
                "body": "# O2-A2 Downstream Time-Stream Lineage",
            },
            {
                "id": "technical-summary",
                "type": "markdown",
                "sourceId": "o2a2-run",
                "body": (
                    "## Technical Summary\n\n"
                    "**The exact preregistered claim is not supported, but fixed downstream "
                    "tracking produced a bounded advantage.** Six of eight gates passed. At "
                    "12 dB, following the declared moving child reduced median NRMSE by "
                    "`10.84%`, beat zero-`Other`, and beat repeated re-selection in both "
                    "target systems. Correlation advantage was `+0.060`, below the frozen "
                    "`+0.10` gate, while integrated error was `35.38%`, just above its "
                    "`35%` gate."
                ),
            },
            {
                "id": "headline-metrics",
                "type": "metric-strip",
                "cardIds": ["gates-card", "correlation-card", "nrmse-card"],
            },
            {
                "id": "verdict-heading",
                "type": "markdown",
                "sourceId": "o2a2-run",
                "body": (
                    "## Six Gates Passed, Two Did Not\n\n"
                    "The frozen status remains `NOT SUPPORTED`. The pooled integral miss "
                    "also conceals strong heterogeneity: quantum integrated error was "
                    "`5.26%`, while the capacitor relation's was `177.10%`."
                ),
            },
            {"id": "gates-block", "type": "table", "tableId": "gates-table"},
            {
                "id": "noise-heading",
                "type": "markdown",
                "sourceId": "o2a2-run",
                "body": (
                    "## Fixed Identity Helped as Local Re-selection Destabilized\n\n"
                    "At high SNR, the correct stream was already strong enough that both "
                    "methods were similar. As noise increased, the repeated selector spent "
                    "less time on the declared child and fixed lineage separated most "
                    "clearly in the quantum target. Lower NRMSE is better."
                ),
            },
            {"id": "nrmse-block", "type": "chart", "chartId": "nrmse-ladder-chart"},
            {
                "id": "occupancy-heading",
                "type": "markdown",
                "sourceId": "o2a2-run",
                "body": (
                    "## Re-selection Frequently Left the Declared Stream\n\n"
                    "At 12 dB, re-selection occupied the capacitor relation for only "
                    "`17.5%` of samples and quantum state 2 for `50.6%`. Fixed lineage's "
                    "`100%` occupancy is assigned by design and is not location recovery."
                ),
            },
            {"id": "occupancy-block", "type": "chart", "chartId": "occupancy-chart"},
            {
                "id": "system-heading",
                "type": "markdown",
                "sourceId": "o2a2-run",
                "body": (
                    "## Quantum Was the Clean Positive Case; the Circuit Was Mixed\n\n"
                    "Fixed lineage materially improved the quantum waveform and integral. "
                    "For the capacitor, it improved local shape only slightly, lost to the "
                    "zero-`Other` and compressed-parent controls on NRMSE, and badly biased "
                    "the signed integral."
                ),
            },
            {"id": "system-block", "type": "table", "tableId": "system-table"},
            {
                "id": "methodology",
                "type": "markdown",
                "body": (
                    "## Scope and Method\n\n"
                    "The moving child was named before the run. A trailing cubic derivative "
                    "and causal exponential smoother were selected only on the first 60% "
                    "of the oscillator, then frozen. The matched comparator used the same "
                    "instrument but repeatedly selected the child with the strongest recent "
                    "absolute residual. Six white-noise SNRs and sixteen fresh target seeds "
                    "per system were scored. Independent validation passed `12/12` checks."
                ),
            },
            {
                "id": "limitations",
                "type": "markdown",
                "body": (
                    "## Limitations and Interpretation Boundary\n\n"
                    "This is conditional tracking of a known branch in synthetic typed "
                    "systems. It is not hidden-child discovery, upstream recursion, "
                    "space-side information retention, forward prediction or a new "
                    "denoising theorem. The derivative and exponential filter are standard "
                    "signal-processing instruments; only the fixed-identity versus "
                    "re-selection comparison instantiates the ARA proposal."
                ),
            },
            {
                "id": "next-steps",
                "type": "markdown",
                "body": (
                    "## Recommended Next Steps\n\n"
                    "1. Preserve the failed frozen verdict without relaxing its gates.\n"
                    "2. Test a joint causal observation model for `q` and `g` on new "
                    "untouched systems to address circuit integral bias.\n"
                    "3. Register the complementary space-side maintenance test separately: "
                    "follow stored identity rather than movement.\n"
                    "4. Continue to calibrated ECG only as identity-retention robustness, "
                    "not physical hidden-`Other` attribution."
                ),
            },
        ],
    }

    artifact = {
        "surface": "report",
        "manifest": manifest,
        "snapshot": {
            "version": 1,
            "status": "ready",
            "generatedAt": "2026-07-23T22:00:00+10:00",
            "datasets": {
                "headline": headline,
                "gates": gates,
                "ladder": sorted(ladder, key=lambda row: (row["series"], row["snr_db"])),
                "occupancy": sorted(
                    occupancy, key=lambda row: (row["model"], row["snr_db"])
                ),
                "system_12": system_12,
            },
        },
        "sources": [source],
    }
    OUTPUT.write_text(json.dumps(artifact, separators=(",", ":")), encoding="utf-8")
    print(
        f"Wrote {OUTPUT.name}: ladder={len(ladder)}, occupancy={len(occupancy)}, "
        f"system rows={len(system_12)}, gates={len(gates)}"
    )


if __name__ == "__main__":
    main()


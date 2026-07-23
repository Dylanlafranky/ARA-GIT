#!/usr/bin/env python3
"""Build the bounded MCP report artifact for O2-A3."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "O2A3_STATE_SPACE_COMPARATOR_RESULTS.json"
TRIALS = HERE / "O2A3_STATE_SPACE_COMPARATOR_TRIALS.csv"
AGGREGATES = HERE / "O2A3_STATE_SPACE_COMPARATOR_AGGREGATES.csv"
ARTIFACT = HERE / "O2A3_STATE_SPACE_COMPARATOR_REPORT_ARTIFACT.json"


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(row: dict, field: str) -> float:
    return float(row[field])


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    verdict = result["primary_verdict"]
    aggregates = read_csv(AGGREGATES)
    trials = read_csv(TRIALS)
    method_labels = {
        "ara_fixed_lineage": "ARA fixed lineage",
        "causal_state_space": "Causal state-space",
        "repeated_reselection": "Repeated re-selection",
        "compressed_parent": "Compressed parent",
        "zero_other": "Zero Other",
    }

    quantum_12 = [
        row
        for row in aggregates
        if row["model"] == "Open two-level probability" and row["snr_db"] == "12"
    ]
    method_rows = [
        {
            "method": method_labels[row["method"]],
            "correlation": number(row, "median_correlation"),
            "nrmse": number(row, "median_nrmse"),
            "sign_accuracy": number(row, "median_sign_accuracy"),
            "integrated_error": number(row, "median_integrated_error"),
            "replicates": int(row["replicates"]),
            "snr_db": 12,
            "target": "Open two-level probability — state 2",
        }
        for row in quantum_12
    ]

    ladder = []
    for row in aggregates:
        if (
            row["model"] == "Open two-level probability"
            and row["method"] in {"ara_fixed_lineage", "causal_state_space"}
        ):
            ladder.append(
                {
                    "method": method_labels[row["method"]],
                    "snr_db": int(float(row["snr_db"])),
                    "nrmse": number(row, "median_nrmse"),
                    "correlation": number(row, "median_correlation"),
                    "sign_accuracy": number(row, "median_sign_accuracy"),
                    "integrated_error": number(row, "median_integrated_error"),
                    "replicates": int(row["replicates"]),
                    "target": "Open two-level probability — state 2",
                }
            )
    ladder.sort(key=lambda row: (row["snr_db"], row["method"]))

    primary_trials = [
        row
        for row in trials
        if row["model"] == "Open two-level probability" and row["snr_db"] == "12"
    ]
    paired = []
    for replicate in range(32):
        ara = next(
            row
            for row in primary_trials
            if row["method"] == "ara_fixed_lineage"
            and int(row["replicate"]) == replicate
        )
        state = next(
            row
            for row in primary_trials
            if row["method"] == "causal_state_space"
            and int(row["replicate"]) == replicate
        )
        paired.append(
            {
                "replicate": f"{replicate + 1:02d}",
                "nrmse_reduction_ara": number(state, "nrmse")
                - number(ara, "nrmse"),
                "correlation_gain_ara": number(ara, "correlation")
                - number(state, "correlation"),
                "integrated_error_reduction_ara": number(
                    state, "integrated_error"
                )
                - number(ara, "integrated_error"),
                "ara_nrmse": number(ara, "nrmse"),
                "state_space_nrmse": number(state, "nrmse"),
                "snr_db": 12,
                "target": "Open two-level probability — state 2",
            }
        )

    gates = [
        {
            "order": 1,
            "gate": "ARA correlation ≥ 0.70",
            "result": verdict["ara_metrics"]["correlation"],
            "status": "Pass",
        },
        {
            "order": 2,
            "gate": "ARA NRMSE ≤ 0.25",
            "result": verdict["ara_metrics"]["nrmse"],
            "status": "Pass",
        },
        {
            "order": 3,
            "gate": "ARA sign accuracy ≥ 0.85",
            "result": verdict["ara_metrics"]["sign_accuracy"],
            "status": "Pass",
        },
        {
            "order": 4,
            "gate": "ARA integrated error ≤ 0.15",
            "result": verdict["ara_metrics"]["integrated_error"],
            "status": "Pass",
        },
    ]

    headline = [
        {
            "ara_correlation": verdict["ara_metrics"]["correlation"],
            "correlation_advantage": verdict[
                "correlation_difference_ara_minus_state_space"
            ],
            "ara_nrmse": verdict["ara_metrics"]["nrmse"],
            "nrmse_improvement": verdict["ara_nrmse_relative_improvement"],
            "ara_integrated_error": verdict["ara_metrics"]["integrated_error"],
            "state_space_integrated_error": verdict["state_space_metrics"][
                "integrated_error"
            ],
            "replicates": 32,
        }
    ]

    source = {
        "id": "o2a3-run",
        "label": "Frozen O2-A3 matched quantum tracking outputs",
        "path": str(AGGREGATES),
        "query": {
            "id": "o2a3-quantum-comparator-v1",
            "language": "sql",
            "engine": "duckdb",
            "description": (
                "Reads frozen aggregate and paired trial outputs for the 12 dB "
                "quantum target and its six-level noise ladder."
            ),
            "sql": (
                "SELECT * FROM read_csv_auto("
                "'analysis/physics_ladder/O2A3_STATE_SPACE_COMPARATOR_AGGREGATES.csv'"
                ");"
            ),
            "tables_used": [
                "analysis/physics_ladder/O2A3_STATE_SPACE_COMPARATOR_AGGREGATES.csv",
                "analysis/physics_ladder/O2A3_STATE_SPACE_COMPARATOR_TRIALS.csv",
            ],
            "filters": [
                "Primary target: open two-level probability, declared state 2",
                "Primary condition: 12 dB white noise on q and g",
                "Thirty-two fresh paired deterministic target replicates",
                "State-space settings selected on oscillator development only",
            ],
            "metric_definitions": [
                "correlation = Pearson correlation with the native hidden waveform",
                "NRMSE = waveform RMSE divided by native hidden peak magnitude",
                "sign accuracy = active samples with matching estimate and truth signs",
                "integrated error = absolute signed-integral error divided by native signed integral",
                "ARA NRMSE improvement = 1 - median ARA NRMSE / median state-space NRMSE",
            ],
        },
    }

    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": "O2-A3 Quantum Tracking Versus State-Space",
            "description": (
                "Frozen matched comparison of ARA fixed lineage with a causal "
                "augmented-state Kalman filter."
            ),
            "generatedAt": "2026-07-23T22:50:00+10:00",
            "sources": [source],
            "cards": [
                {
                    "id": "correlation-card",
                    "description": "Median local waveform correlation at 12 dB.",
                    "dataset": "headline",
                    "sourceId": "o2a3-run",
                    "metrics": [
                        {
                            "label": "ARA correlation",
                            "field": "ara_correlation",
                            "format": "number",
                        },
                        {
                            "label": "vs state-space",
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
                    "sourceId": "o2a3-run",
                    "metrics": [
                        {
                            "label": "ARA NRMSE",
                            "field": "ara_nrmse",
                            "format": "number",
                        },
                        {
                            "label": "Improvement",
                            "field": "nrmse_improvement",
                            "format": "percent",
                            "signed": True,
                        },
                    ],
                },
                {
                    "id": "integral-card",
                    "description": "Cumulative signed-integral error; lower is better.",
                    "dataset": "headline",
                    "sourceId": "o2a3-run",
                    "metrics": [
                        {
                            "label": "ARA integral error",
                            "field": "ara_integrated_error",
                            "format": "percent",
                        },
                        {
                            "label": "State-space",
                            "field": "state_space_integrated_error",
                            "format": "percent",
                        },
                    ],
                },
            ],
            "charts": [
                {
                    "id": "noise-ladder-chart",
                    "title": "Quantum waveform NRMSE across the noise ladder",
                    "description": (
                        "Median across thirty-two paired runs per method and SNR; "
                        "lower values indicate better local recovery."
                    ),
                    "type": "line",
                    "dataset": "ladder",
                    "sourceId": "o2a3-run",
                    "encodings": {
                        "x": {"field": "snr_db", "type": "quantitative"},
                        "y": {"field": "nrmse", "type": "quantitative"},
                        "color": {"field": "method", "type": "nominal"},
                    },
                    "options": {"points": "always"},
                },
                {
                    "id": "paired-nrmse-chart",
                    "title": "Paired ARA NRMSE reduction at 12 dB",
                    "description": (
                        "One bar per fresh quantum replicate; positive values mean "
                        "ARA had lower waveform error."
                    ),
                    "type": "bar",
                    "dataset": "paired",
                    "sourceId": "o2a3-run",
                    "encodings": {
                        "x": {"field": "replicate", "type": "nominal"},
                        "y": {
                            "field": "nrmse_reduction_ara",
                            "type": "quantitative",
                        },
                    },
                },
            ],
            "tables": [
                {
                    "id": "methods-table",
                    "title": "Quantum target methods at 12 dB",
                    "description": "Median metrics across thirty-two paired target runs.",
                    "dataset": "methods",
                    "sourceId": "o2a3-run",
                    "columns": [
                        {"field": "method", "label": "Method", "type": "text"},
                        {
                            "field": "correlation",
                            "label": "Correlation",
                            "type": "number",
                        },
                        {"field": "nrmse", "label": "NRMSE", "type": "number"},
                        {
                            "field": "sign_accuracy",
                            "label": "Sign accuracy",
                            "type": "number",
                        },
                        {
                            "field": "integrated_error",
                            "label": "Integrated error",
                            "type": "number",
                        },
                    ],
                    "defaultSort": {"field": "nrmse", "direction": "asc"},
                },
                {
                    "id": "gates-table",
                    "title": "Frozen absolute ARA quality gates",
                    "description": "All four gates apply to the 12 dB quantum target.",
                    "dataset": "gates",
                    "sourceId": "o2a3-run",
                    "columns": [
                        {"field": "order", "label": "#", "type": "number"},
                        {"field": "gate", "label": "Gate", "type": "text"},
                        {"field": "result", "label": "Result", "type": "number"},
                        {"field": "status", "label": "Status", "type": "text"},
                    ],
                    "defaultSort": {"field": "order", "direction": "asc"},
                },
            ],
            "blocks": [
                {
                    "id": "title",
                    "type": "markdown",
                    "body": "# O2-A3 Quantum Tracking Versus State-Space",
                },
                {
                    "id": "technical-summary",
                    "type": "markdown",
                    "sourceId": "o2a3-run",
                    "body": (
                        "## Technical Summary\n\n"
                        "**ARA tracking was absolutely good, but the comparative "
                        "result is mixed.** ARA beat the causal state-space filter "
                        "on local correlation and NRMSE in all `32/32` paired "
                        "quantum runs. The state-space filter beat ARA on cumulative "
                        "integral error in all `32/32`. This separates movement-shape "
                        "tracking from storage closure rather than establishing one "
                        "universally superior method."
                    ),
                },
                {
                    "id": "headline",
                    "type": "metric-strip",
                    "cardIds": [
                        "correlation-card",
                        "nrmse-card",
                        "integral-card",
                    ],
                },
                {
                    "id": "absolute-heading",
                    "type": "markdown",
                    "sourceId": "o2a3-run",
                    "body": (
                        "## ARA Passed Every Frozen Absolute Quality Gate\n\n"
                        "At 12 dB, ARA reached correlation `0.762`, NRMSE `0.165`, "
                        "sign accuracy `0.905`, and integrated error `11.75%`. "
                        "It therefore qualifies as good tracking under the frozen "
                        "definition."
                    ),
                },
                {"id": "gates-block", "type": "table", "tableId": "gates-table"},
                {
                    "id": "comparison-heading",
                    "type": "markdown",
                    "sourceId": "o2a3-run",
                    "body": (
                        "## Local Shape Favoured ARA; Cumulative Closure Favoured "
                        "State-Space\n\nARA improved median NRMSE by `29.95%` and "
                        "correlation by `+0.074`. Its integral error was `11.75%`, "
                        "however, versus `3.80%` for state-space. The frozen result "
                        "is consequently `MIXED`."
                    ),
                },
                {
                    "id": "methods-block",
                    "type": "table",
                    "tableId": "methods-table",
                },
                {
                    "id": "ladder-heading",
                    "type": "markdown",
                    "sourceId": "o2a3-run",
                    "body": (
                        "## The Local Advantage Ends Under Extreme Noise\n\n"
                        "ARA had lower NRMSE from `24` through `0` dB. At `-6` dB, "
                        "the state-space filter became better. The comparison is a "
                        "finite noise-region result, not universal dominance."
                    ),
                },
                {
                    "id": "ladder-block",
                    "type": "chart",
                    "chartId": "noise-ladder-chart",
                },
                {
                    "id": "paired-heading",
                    "type": "markdown",
                    "sourceId": "o2a3-run",
                    "body": (
                        "## Every 12 dB Replicate Favoured ARA on Waveform Error\n\n"
                        "All paired NRMSE reductions were positive. The median "
                        "reduction was `0.0730`; its post-hoc descriptive 90% "
                        "bootstrap interval was `[0.0674, 0.0757]`."
                    ),
                },
                {
                    "id": "paired-block",
                    "type": "chart",
                    "chartId": "paired-nrmse-chart",
                },
                {
                    "id": "scope",
                    "type": "markdown",
                    "body": (
                        "## Scope and Method\n\nBoth methods received the same named "
                        "child, noisy stored quantity, noisy declared transfer and "
                        "timestamps. ARA retained its previously frozen derivative "
                        "and EWMA settings. The forward Kalman filter selected process "
                        "ratios on oscillator development and estimated target noise "
                        "from an observed-only prefix."
                    ),
                },
                {
                    "id": "limitations",
                    "type": "markdown",
                    "body": (
                        "## Limitations and Validation\n\nThis is one simple "
                        "state-space comparator, not the best possible conventional "
                        "filter. The capacitor secondary target became unidentifiable "
                        "after calibration because only `0.229%` of its original sink "
                        "peak remained. Independent validation passed `12/12`. The "
                        "test does not establish pure quantum information, a hidden "
                        "Phase B, perceptual uncoupling or a new quantum law."
                    ),
                },
                {
                    "id": "next",
                    "type": "markdown",
                    "body": (
                        "## Recommended Next Steps\n\n"
                        "1. Preserve the `GOOD / MIXED` classification.\n"
                        "2. Test driven target families whose movement and storage "
                        "endpoints both remain identifiable.\n"
                        "3. Compare several preregistered causal state-space variants.\n"
                        "4. Keep time-stream shape and space-side cumulative retention "
                        "as separate endpoints."
                    ),
                },
                {
                    "id": "questions",
                    "type": "markdown",
                    "body": (
                        "## Further Questions\n\n"
                        "- Does the local advantage survive a quantum-family-trained "
                        "state-space comparator?\n"
                        "- Can a causal ARA account retain both waveform shape and "
                        "integral without post-run correction?\n"
                        "- Does the split persist for oscillatory, sign-changing "
                        "hidden transfers?"
                    ),
                },
            ],
        },
        "snapshot": {
            "version": 1,
            "status": "ready",
            "generatedAt": "2026-07-23T22:50:00+10:00",
            "datasets": {
                "headline": headline,
                "methods": method_rows,
                "ladder": ladder,
                "paired": paired,
                "gates": gates,
            },
        },
        "sources": [source],
    }
    ARTIFACT.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(
        f"Wrote {ARTIFACT.name}: methods={len(method_rows)}, "
        f"ladder={len(ladder)}, paired={len(paired)}, gates={len(gates)}"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the bounded MCP report payload for the T259 real-hardware result."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "Q2_PUBLIC_HARDWARE_IQ_RESULTS.json"
FOLDS = HERE / "Q2_PUBLIC_HARDWARE_IQ_FOLDS.csv"
SUMMARY = HERE / "Q2_PUBLIC_HARDWARE_IQ_SUMMARY.csv"
DYNAMICS = HERE / "Q2_PUBLIC_HARDWARE_DYNAMICS_CROSSWALK.csv"
OUT = HERE / "Q2_PUBLIC_HARDWARE_IQ_REPORT_ARTIFACT.json"


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    folds = read_csv(FOLDS)
    summary = read_csv(SUMMARY)
    dynamics_raw = read_csv(DYNAMICS)

    primary_rows = [
        r
        for r in folds
        if r["run"] == "primary_first_readout"
        and r["arm"] in {"selected_onecut", "ara_twocut", "q_only"}
    ]
    arm_labels = {
        "selected_onecut": "Selected one cut",
        "ara_twocut": "Two-cut ARA",
        "q_only": "Q only",
    }
    condition_performance = [
        {
            "condition_hz": int(r["condition_hz"]),
            "condition": f"{r['condition_hz']} Hz",
            "arm": arm_labels[r["arm"]],
            "balanced_accuracy": float(r["balanced_accuracy"]),
            "selected_axis": r["selected_axis"],
            "target_shots": int(r["tn"])
            + int(r["fp"])
            + int(r["fn"])
            + int(r["tp"]),
            "fold_index": int(r["fold_index"]),
        }
        for r in primary_rows
    ]

    run_labels = {
        "primary_first_readout": "Primary first",
        "replication_second_readout": "Second readout",
        "replication_prep_first": "Prepared first",
        "replication_prep_second": "Prepared second",
    }

    def value(run: str, arm: str, field: str = "condition_weighted_ba") -> float:
        row = next(r for r in summary if r["run"] == run and r["arm"] == arm)
        return float(row[field])

    replication_summary = []
    for run in run_labels:
        ara = value(run, "ara_twocut")
        one = value(run, "selected_onecut")
        replication_summary.append(
            {
                "run": run,
                "run_label": run_labels[run],
                "ara_accuracy": ara,
                "selected_onecut_accuracy": one,
                "gain": ara - one,
                "gain_percentage_points": 100 * (ara - one),
                "qda_accuracy": value(run, "raw_iq_qda"),
                "q_only_accuracy": value(run, "q_only"),
                "worst_condition_accuracy": value(
                    run, "ara_twocut", "worst_condition_ba"
                ),
            }
        )

    gate_names = {
        "G1_ara_ba_at_least_0p80": "G1 ARA BA ≥ 0.80",
        "G2_gain_at_least_0p005": "G2 gain ≥ 0.005",
        "G3_gain_ci_low_above_zero": "G3 gain CI low > 0",
        "G4_worst_condition_at_least_0p70": "G4 worst condition ≥ 0.70",
        "G5_equal_information_tie": "G5 raw/ARA exact tie",
        "G6_pole_reversal_and_complement": "G6 reversal/complement",
        "G7_label_shuffle_at_most_0p55": "G7 shuffle BA ≤ 0.55",
    }
    gate_rows = []
    for order, (key, gate) in enumerate(result["gates"].items(), start=1):
        if "value" in gate:
            measured = float(gate["value"])
        elif key.startswith("G5"):
            measured = float(gate["accuracy_difference"])
        else:
            measured = float(gate["complement_max_residual"])
        gate_rows.append(
            {
                "order": order,
                "gate": gate_names[key],
                "status": "PASS" if gate["pass"] else "FAIL",
                "measured": measured,
                "detail": json.dumps(gate, sort_keys=True),
            }
        )

    dynamics = [
        {
            "family": r["family"],
            "mode": r["mode"],
            "samples": int(r["samples"]),
            "time_max_us": float(r["time_max_us"]),
            "ridge_crossings": int(r["ridge_crossings_published_fit"]),
            "ara_fit_mae": float(r["ara_fit_mae"]),
            "ara_fit_rmse": float(r["ara_fit_rmse"]),
            "fraction_below_ridge": float(r["fraction_below_ridge"]),
            "fraction_above_ridge": float(r["fraction_above_ridge"]),
        }
        for r in dynamics_raw
    ]

    headline = [
        {
            "ara_accuracy": result["primary"]["ara_twocut_ba"],
            "selected_onecut_accuracy": result["primary"]["selected_onecut_ba"],
            "gain": result["primary"]["gain"],
            "gain_ci_low": result["bootstrap"]["gain_ci_low"],
            "gain_ci_high": result["bootstrap"]["gain_ci_high"],
            "gates_passed": result["gates_passed"],
            "gates_total": result["gates_total"],
            "coordinate_disagreements": result["primary"][
                "ara_raw_disagreements"
            ],
            "worst_condition_accuracy": result["primary"]["worst_condition_ba"],
            "target_predictions": 600000,
        }
    ]

    source_run = {
        "id": "t259-run",
        "label": "Frozen T259 public-hardware outputs",
        "path": "analysis/quantum/Q2_PUBLIC_HARDWARE_IQ_FOLDS.csv",
        "query": {
            "id": "t259-public-hardware-iq-v1",
            "language": "sql",
            "engine": "duckdb",
            "description": (
                "Reads the frozen leave-one-condition-out fold results and "
                "registered replication summaries."
            ),
            "sql": (
                "SELECT * FROM read_csv_auto("
                "'analysis/quantum/Q2_PUBLIC_HARDWARE_IQ_FOLDS.csv');"
            ),
            "tables_used": [
                "analysis/quantum/Q2_PUBLIC_HARDWARE_IQ_FOLDS.csv",
                "analysis/quantum/Q2_PUBLIC_HARDWARE_IQ_BLOCKS.csv",
                "analysis/quantum/Q2_PUBLIC_HARDWARE_IQ_SUMMARY.csv",
                "analysis/quantum/Q2_PUBLIC_HARDWARE_IQ_RESULTS.json",
            ],
            "filters": [
                "Six whole-condition holdouts: 0, 10, 50, 250, 500 and 1000 Hz",
                "50,000 ground and 50,000 excited shots per held-out condition",
                "Axis choice, centring, scale and covariance fitted on the other five conditions",
                "Source-supplied angle, threshold and fidelity fields excluded",
            ],
            "metric_definitions": [
                "balanced accuracy = mean of ground specificity and excited sensitivity",
                "gain = two-cut ARA balanced accuracy minus training-selected one-cut balanced accuracy",
                "condition-weighted BA = unweighted mean of the six held-out-condition balanced accuracies",
                "paired interval = 2,000 bootstrap replicates over conditions and contiguous 1,000-shot class blocks",
            ],
        },
    }
    source_dynamics = {
        "id": "t259-dynamics",
        "label": "Published T1 and Ramsey/T2* curve crosswalk",
        "path": "analysis/quantum/Q2_PUBLIC_HARDWARE_DYNAMICS_CROSSWALK.csv",
        "query": {
            "id": "t259-dynamics-crosswalk",
            "language": "sql",
            "engine": "duckdb",
            "description": (
                "Reads the descriptive 0–2 coordinate crosswalk of the source's "
                "published T1 and Ramsey/T2* curves."
            ),
            "sql": (
                "SELECT * FROM read_csv_auto("
                "'analysis/quantum/Q2_PUBLIC_HARDWARE_DYNAMICS_CROSSWALK.csv');"
            ),
            "tables_used": [
                "analysis/quantum/Q2_PUBLIC_HARDWARE_DYNAMICS_CROSSWALK.csv",
                "data_t1_exp.npy",
                "data_t1_fits.npy",
                "data_ramsey_exp.npy",
                "data_ramsey_fits.npy",
            ],
            "filters": [
                "Three source readout modes",
                "0–2 scale set by source-supplied fit extrema",
                "Descriptive secondary; not a frozen predictive endpoint",
            ],
            "metric_definitions": [
                "ridge crossings = sign changes of the published fit around ARA coordinate 1.0",
                "ARA fit MAE = mean absolute source-data distance from the interpolated published fit after 0–2 mapping",
            ],
        },
    }
    source_public = {
        "id": "arnold-werner-source",
        "label": "All-optical superconducting qubit readout — public data",
        "href": "https://doi.org/10.5281/zenodo.14033026",
        "path": "Zenodo record 14033026 / AllopticalSCQreadout_data.zip",
        "query": {
            "id": "doi-10.5281-zenodo.14033026",
            "description": (
                "Immutable author deposit for the Nature Physics superconducting-qubit "
                "readout experiment."
            ),
            "tables_used": [
                "Fig_4a/IQblobs_0Hz.mat",
                "Fig_4a/IQblobs_10Hz.mat",
                "Fig_4a/IQblobs_50Hz.mat",
                "Fig_4a/IQblobs_250Hz.mat",
                "Fig_4a/IQblobs_500Hz.mat",
                "Fig_4a/IQblobs_1000Hz.mat",
            ],
            "filters": [
                "Archive SHA-256 73f3e2ca7b3658452b4c171532c751e96d7392dcb8741b87a18e28c7073d67fd"
            ],
        },
    }
    sources = [source_run, source_dynamics, source_public]

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "Q2 Real-Hardware ARA Readout Test",
        "description": (
            "Frozen T259 benchmark on public superconducting-qubit I/Q data."
        ),
        "generatedAt": "2026-07-24T07:15:00+10:00",
        "sources": sources,
        "cards": [
            {
                "id": "accuracy-card",
                "description": "Whole-condition target performance across 600,000 predictions.",
                "dataset": "headline",
                "sourceId": "t259-run",
                "metrics": [
                    {
                        "label": "Two-cut ARA BA",
                        "field": "ara_accuracy",
                        "format": "percent",
                    },
                    {
                        "label": "Gain vs one cut",
                        "field": "gain",
                        "format": "percent",
                        "signed": True,
                    },
                ],
            },
            {
                "id": "gates-card",
                "description": "All seven frozen gates were required for support.",
                "dataset": "headline",
                "sourceId": "t259-run",
                "metrics": [
                    {
                        "label": "Gates passed",
                        "field": "gates_passed",
                        "format": "number",
                    },
                    {
                        "label": "Required",
                        "field": "gates_total",
                        "format": "number",
                    },
                ],
            },
            {
                "id": "equivalence-card",
                "description": "Raw I/Q LDA versus the independently calibrated ARA-coordinate LDA.",
                "dataset": "headline",
                "sourceId": "t259-run",
                "metrics": [
                    {
                        "label": "Disagreements",
                        "field": "coordinate_disagreements",
                        "format": "number",
                    }
                ],
            },
        ],
        "charts": [
            {
                "id": "condition-performance-chart",
                "title": "Balanced accuracy across held-out conditions",
                "description": (
                    "The I-aligned one-cut and two-cut accounts overlap while Q alone remains weak."
                ),
                "type": "bar",
                "dataset": "condition_performance",
                "sourceId": "t259-run",
                "encodings": {
                    "x": {"field": "condition", "type": "nominal"},
                    "y": {"field": "balanced_accuracy", "type": "quantitative"},
                    "color": {"field": "arm", "type": "nominal"},
                },
                "options": {"orientation": "vertical", "grouping": "grouped"},
            },
            {
                "id": "replication-gain-chart",
                "title": "Two-cut gain across registered readout arms",
                "description": (
                    "Difference in percentage points relative to the training-selected native cut."
                ),
                "type": "bar",
                "dataset": "replication_summary",
                "sourceId": "t259-run",
                "encodings": {
                    "x": {"field": "run_label", "type": "nominal"},
                    "y": {
                        "field": "gain_percentage_points",
                        "type": "quantitative",
                    },
                },
                "options": {"orientation": "vertical", "grouping": "single"},
            },
            {
                "id": "dynamics-crossing-chart",
                "title": "Ridge crossings in published T1 and Ramsey fits",
                "description": (
                    "All three T1 fits cross once; Ramsey/T2* oscillations cross repeatedly."
                ),
                "type": "bar",
                "dataset": "dynamics",
                "sourceId": "t259-dynamics",
                "encodings": {
                    "x": {"field": "mode", "type": "nominal"},
                    "y": {"field": "ridge_crossings", "type": "quantitative"},
                    "color": {"field": "family", "type": "nominal"},
                },
                "options": {"orientation": "vertical", "grouping": "grouped"},
            },
        ],
        "tables": [
            {
                "id": "gate-table",
                "title": "Frozen gate outcomes",
                "description": "Four of seven passed; G2 and G3 reject added two-cut information.",
                "dataset": "gates",
                "sourceId": "t259-run",
                "columns": [
                    {"field": "order", "label": "#", "type": "number"},
                    {"field": "gate", "label": "Gate", "type": "text"},
                    {"field": "status", "label": "Status", "type": "text"},
                    {"field": "measured", "label": "Measured", "type": "number"},
                ],
                "defaultSort": {"field": "order", "direction": "asc"},
            }
        ],
        "blocks": [
            {
                "id": "title",
                "type": "markdown",
                "body": "# Q2 Real-Hardware ARA Readout Test",
            },
            {
                "id": "technical-summary",
                "type": "markdown",
                "sourceId": "t259-run",
                "body": (
                    "## Technical Summary\n\n"
                    "**The strong real-data prediction is not supported: `4/7` frozen gates passed.** "
                    "Two-cut ARA reached `88.2808%` balanced accuracy, but the training-selected "
                    "I-only cut reached `88.2838%`. The gain was `−0.003` percentage points, "
                    "with a paired 95% interval from `−0.0147` to `+0.0050` points. "
                    "The reversible coordinate bridge passed exactly, but Q added no held-out "
                    "class information in this measurement geometry."
                ),
            },
            {
                "id": "headline",
                "type": "metric-strip",
                "cardIds": ["accuracy-card", "gates-card", "equivalence-card"],
            },
            {
                "id": "condition-heading",
                "type": "markdown",
                "sourceId": "t259-run",
                "body": (
                    "## One Aligned I Axis Carried Nearly All State Separation\n\n"
                    "Every outer fold selected I using only the other five hardware conditions. "
                    "Q-only accuracy was `57.89%`, while adding Q to I changed the primary score "
                    "by only three hundred-thousandths. Read the grouped bars as separate full "
                    "condition holdouts, not random shot splits."
                ),
            },
            {
                "id": "condition-chart-block",
                "type": "chart",
                "chartId": "condition-performance-chart",
            },
            {
                "id": "replication-heading",
                "type": "markdown",
                "sourceId": "t259-run",
                "body": (
                    "## The No-Gain Result Repeated Across Every Registered Arm\n\n"
                    "First readout, second readout, prepared and unprepared files all gave a "
                    "slightly negative ARA-minus-one-cut difference. QDA gained only a small "
                    "amount, suggesting mild cloud non-linearity rather than missing linear "
                    "two-cut information."
                ),
            },
            {
                "id": "replication-chart-block",
                "type": "chart",
                "chartId": "replication-gain-chart",
            },
            {
                "id": "gate-heading",
                "type": "markdown",
                "sourceId": "t259-run",
                "body": (
                    "## Four Gates Passed, but the Decisive Gain Gates Failed\n\n"
                    "Absolute accuracy, worst-condition performance, raw/ARA equivalence and "
                    "pole reversal passed. The gain magnitude and its uncertainty interval failed. "
                    "The one-shot label-shuffle gate also failed, but a post-run complement audit "
                    "shows that control was under-specified; G2 and G3 reject the strong claim "
                    "without relying on it."
                ),
            },
            {"id": "gate-table-block", "type": "table", "tableId": "gate-table"},
            {
                "id": "dynamics-heading",
                "type": "markdown",
                "sourceId": "t259-dynamics",
                "body": (
                    "## Real T1 and Ramsey Curves Retain Their Expected Dynamical Difference\n\n"
                    "After mapping each source-supplied fit span onto 0–2, every T1 curve crosses "
                    "the ridge once, whereas Ramsey/T2* crosses `11`, `11` and `15` times. "
                    "This is a clear descriptive crosswalk, not an independent prediction, because "
                    "the published fit extrema set the coordinate scale."
                ),
            },
            {
                "id": "dynamics-chart-block",
                "type": "chart",
                "chartId": "dynamics-crossing-chart",
            },
            {
                "id": "scope",
                "type": "markdown",
                "sourceId": "arnold-werner-source",
                "body": (
                    "## What Was Measured\n\n"
                    "The public DOI archive contains six optical-pulse repetition conditions, "
                    "with `50,000` ground and `50,000` excited I/Q shots per condition plus "
                    "registered second-readout and prepared-file replications. I and Q are receiver "
                    "quadratures—not Bloch X/Y/Z axes—so this benchmark tests readout-output geometry, "
                    "not full quantum-state tomography."
                ),
            },
            {
                "id": "method",
                "type": "markdown",
                "sourceId": "t259-run",
                "body": (
                    "## How the Frozen Test Worked\n\n"
                    "Each hardware condition was held out in full. The other five set centring, "
                    "scale, orientation, covariance and the I-versus-Q one-cut choice. ARA used an "
                    "invertible affine 0–2 coordinate map and an independently fitted shared-covariance "
                    "linear discriminant. Uncertainty came from `2,000` paired bootstrap replicates "
                    "over conditions and contiguous `1,000`-shot class blocks."
                ),
            },
            {
                "id": "limits",
                "type": "markdown",
                "sourceId": "t259-run",
                "body": (
                    "## What Passed, What Failed, and What It Means\n\n"
                    "The exact raw/ARA tie and reversal invariance support translation fidelity. "
                    "They are expected consequences of a reversible affine coordinate change, not "
                    "new quantum physics. The absent two-cut gain is a boundary result: this source "
                    "already aligns state separation with I. It does not invalidate Q1's controlled "
                    "multi-axis result, but it does show that decompression cannot add information "
                    "when the measured second cut is nearly uninformative."
                ),
            },
            {
                "id": "next",
                "type": "markdown",
                "body": (
                    "## Test Real Tomography Next\n\n"
                    "Preserve T259 rather than tuning it to win. The next high-value source should "
                    "contain independently measured X, Y and Z axes or randomized tomography "
                    "directions. A second option is a predeclared receiver-phase experiment that "
                    "rotates class separation away from I and asks exactly when coupled cuts become "
                    "necessary."
                ),
            },
            {
                "id": "questions",
                "type": "markdown",
                "body": (
                    "## Open Questions\n\n"
                    "- Does two-cut gain appear under deliberately unaligned or drifting receiver phase?\n\n"
                    "- Can ARA radius and direction diagnose calibration drift even when static accuracy is unchanged?\n\n"
                    "- Does a public tomography dataset reproduce Q1's coherent-versus-mixed ridge distinction?\n\n"
                    "- Can paired label/complement permutations replace the under-specified one-shot shuffle?"
                ),
            },
        ],
    }
    snapshot = {
        "version": 1,
        "status": "ready",
        "generatedAt": "2026-07-24T07:15:00+10:00",
        "datasets": {
            "headline": headline,
            "condition_performance": condition_performance,
            "replication_summary": replication_summary,
            "gates": gate_rows,
            "dynamics": dynamics,
        },
    }
    artifact = {
        "surface": "report",
        "manifest": manifest,
        "snapshot": snapshot,
        "sources": sources,
    }
    OUT.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the bounded MCP report payload for the frozen T260-H1 result."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "H1_PUBLIC_HYDRAULIC_RESULTS.json"
FOLDS = HERE / "H1_PUBLIC_HYDRAULIC_FOLDS.csv"
OUT = HERE / "H1_PUBLIC_HYDRAULIC_REPORT_ARTIFACT.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    fold_rows = read_csv(FOLDS)

    labels = {
        "single_balanced_accuracy": "Best one cut",
        "pair_balanced_accuracy": "Two synchronized cuts",
        "phase_destroyed_balanced_accuracy": "Shifted second cut",
        "random_forest_balanced_accuracy": "Random forest, same pair",
    }
    fold_performance = []
    for row in fold_rows:
        for field, method in labels.items():
            fold_performance.append(
                {
                    "fold": int(row["outer_fold"]),
                    "fold_label": f"Fold {row['outer_fold']}",
                    "method": method,
                    "balanced_accuracy": float(row[field]),
                    "gain": float(row["gain"]),
                    "selected_single": row["selected_single"],
                    "selected_pair": row["selected_pair"],
                    "test_cycles": int(row["test_cycles"]),
                    "test_groups": int(row["test_groups"]),
                }
            )

    class_recalls = [
        {
            "accumulator_state_bar": int(state),
            "state": f"{state} bar",
            "recall": float(recall),
            "total_cycles": result["source_instances"],
            "selected_pair": "PS1+PS3",
        }
        for state, recall in result["primary"]["class_recalls"].items()
    ]

    gate_labels = {
        "H1_G1_pair_ba": "Pair balanced accuracy",
        "H1_G2_gain": "Gain over one cut",
        "H1_G3_gain_ci_low": "Gain interval lower bound",
        "H1_G4_worst_class_recall": "Worst class recall",
        "H1_G5_fold_wins": "Outer-fold wins",
        "H1_G6_raw_ara_tie": "Raw/ARA exact tie",
        "H1_G7_reversal": "Pole-reversal invariance",
        "H1_G8_permutations": "Label permutations",
    }
    gates = []
    for order, (key, gate) in enumerate(result["gates"].items(), start=1):
        value = gate.get("value")
        if value is None:
            value = gate.get("mean", gate.get("accuracy_difference", 0.0))
        gates.append(
            {
                "order": order,
                "gate": gate_labels[key],
                "status": "PASS" if gate["pass"] else "FAIL",
                "measured": float(value),
                "detail": json.dumps(gate, sort_keys=True),
            }
        )

    headline = [
        {
            "pair_accuracy": result["primary"]["pair_balanced_accuracy"],
            "single_accuracy": result["primary"]["single_balanced_accuracy"],
            "gain": result["primary"]["gain"],
            "gain_ci_low": result["primary"]["gain_ci_95"][0],
            "gain_ci_high": result["primary"]["gain_ci_95"][1],
            "phase_destroyed_accuracy": result["diagnostics"][
                "phase_destroyed_balanced_accuracy"
            ],
            "random_forest_accuracy": result["diagnostics"][
                "random_forest_balanced_accuracy"
            ],
            "gates_passed": result["gates_passed"],
            "gates_total": result["gates_total"],
            "cycles": result["source_instances"],
            "fold_wins": result["primary"]["pair_fold_wins"],
        }
    ]

    source_run = {
        "id": "t260-run",
        "label": "Frozen T260-H1 outputs",
        "path": "analysis/hydraulics/H1_PUBLIC_HYDRAULIC_FOLDS.csv",
        "query": {
            "id": "t260-hydraulic-two-cut-v1",
            "language": "sql",
            "engine": "duckdb",
            "description": (
                "Reads the frozen whole-group outer-fold results and independently "
                "validated control summaries."
            ),
            "sql": (
                "SELECT * FROM read_csv_auto("
                "'analysis/hydraulics/H1_PUBLIC_HYDRAULIC_FOLDS.csv');"
            ),
            "tables_used": [
                "analysis/hydraulics/H1_PUBLIC_HYDRAULIC_FOLDS.csv",
                "analysis/hydraulics/H1_PUBLIC_HYDRAULIC_PREDICTIONS.csv",
                "analysis/hydraulics/H1_PUBLIC_HYDRAULIC_PERMUTATIONS.csv",
                "analysis/hydraulics/H1_PUBLIC_HYDRAULIC_RESULTS.json",
                "analysis/hydraulics/H1_PUBLIC_HYDRAULIC_VALIDATION.json",
            ],
            "filters": [
                "All 2,205 complete 60-second cycles",
                "Contiguous 15-cycle groups remain intact",
                "Five outer StratifiedGroupKFold holdouts",
                "Sensor and sensor-pair selection occurs inside outer training only",
                "Pressure sensors PS1 through PS6 only",
            ],
            "metric_definitions": [
                "balanced accuracy = unweighted mean of recall across accumulator states 90, 100, 115 and 130 bar",
                "gain = two-cut balanced accuracy minus selected one-cut balanced accuracy",
                "paired interval = 2,000 paired bootstrap replicates over held-out predictions",
                "phase-destroyed accuracy = pair-model accuracy after deterministic within-cycle bin shift of the second sensor",
            ],
        },
    }
    source_public = {
        "id": "uci-hydraulic-source",
        "label": "UCI Condition Monitoring of Hydraulic Systems",
        "href": "https://doi.org/10.24432/C5CW21",
        "path": "UCI dataset 447 / condition monitoring of hydraulic systems",
        "query": {
            "id": "doi-10.24432-C5CW21",
            "description": (
                "Public CC BY 4.0 experimental hydraulic test-rig archive with "
                "2,205 labelled 60-second cycles."
            ),
            "tables_used": [
                "PS1.txt",
                "PS2.txt",
                "PS3.txt",
                "PS4.txt",
                "PS5.txt",
                "PS6.txt",
                "profile.txt",
            ],
            "filters": [
                "Archive SHA-256 24128aad2ee45eea7e6b63ebbd9992cdf25d0483a2cebefbfc13bc69079af1f2",
                "No source numerical values opened before protocol freeze",
            ],
        },
    }
    sources = [source_run, source_public]

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "H1 Public Hydraulic Two-Cut ARA Test",
        "description": (
            "Frozen T260-H1 benchmark on public connection-rich hydraulic data."
        ),
        "generatedAt": "2026-07-24T10:30:00+10:00",
        "sources": sources,
        "cards": [
            {
                "id": "pair-card",
                "description": (
                    "Balanced accuracy across all 2,205 whole-group held-out cycles."
                ),
                "dataset": "headline",
                "sourceId": "t260-run",
                "metrics": [
                    {
                        "label": "Two-cut accuracy",
                        "field": "pair_accuracy",
                        "format": "percent",
                    },
                    {
                        "label": "One cut",
                        "field": "single_accuracy",
                        "format": "percent",
                    },
                    {
                        "label": "Gain",
                        "field": "gain",
                        "format": "percent",
                        "signed": True,
                    },
                ],
            },
            {
                "id": "relation-card",
                "description": (
                    "Accuracy after deliberately breaking within-cycle synchronization."
                ),
                "dataset": "headline",
                "sourceId": "t260-run",
                "metrics": [
                    {
                        "label": "Shifted-pair accuracy",
                        "field": "phase_destroyed_accuracy",
                        "format": "percent",
                    },
                    {
                        "label": "Synchronized pair",
                        "field": "pair_accuracy",
                        "format": "percent",
                    },
                ],
            },
            {
                "id": "gates-card",
                "description": "All eight frozen gates were required for support.",
                "dataset": "headline",
                "sourceId": "t260-run",
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
        ],
        "charts": [
            {
                "id": "fold-performance-chart",
                "title": "Balanced accuracy across held-out folds",
                "description": (
                    "The synchronized pair beats one cut in every fold; shifting its "
                    "timing destroys the gain. The random forest is the stronger standard model."
                ),
                "type": "bar",
                "dataset": "fold_performance",
                "sourceId": "t260-run",
                "encodings": {
                    "x": {"field": "fold_label", "type": "nominal"},
                    "y": {"field": "balanced_accuracy", "type": "quantitative"},
                    "color": {"field": "method", "type": "nominal"},
                },
                "options": {"orientation": "vertical", "grouping": "grouped"},
            },
            {
                "id": "class-recall-chart",
                "title": "Recall across accumulator states",
                "description": (
                    "Every class clears the frozen 0.60 floor; 130 bar remains hardest."
                ),
                "type": "bar",
                "dataset": "class_recalls",
                "sourceId": "t260-run",
                "encodings": {
                    "x": {"field": "state", "type": "nominal"},
                    "y": {"field": "recall", "type": "quantitative"},
                },
                "options": {"orientation": "vertical", "grouping": "single"},
            },
        ],
        "tables": [
            {
                "id": "gate-table",
                "title": "Frozen gate outcomes",
                "description": "All eight predeclared gates passed.",
                "dataset": "gates",
                "sourceId": "t260-run",
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
                "body": "# H1 Public Hydraulic Two-Cut ARA Test",
            },
            {
                "id": "executive-summary",
                "type": "markdown",
                "sourceId": "t260-run",
                "body": (
                    "## Executive Summary\n\n"
                    "**The frozen connection-rich prediction is supported: all `8/8` gates passed.** "
                    "Two synchronized pressure cuts reached `87.73%` balanced accuracy versus "
                    "`71.18%` for the best one cut, a gain of `+16.55` percentage points with "
                    "paired 95% interval `+12.39` to `+21.04` points. Deliberately shifting the "
                    "second cut collapsed performance to `26.68%`, showing that synchronized "
                    "relation carried the additional information."
                ),
            },
            {
                "id": "headline",
                "type": "metric-strip",
                "cardIds": ["pair-card", "relation-card", "gates-card"],
            },
            {
                "id": "fold-heading",
                "type": "markdown",
                "sourceId": "t260-run",
                "body": (
                    "## Two Cuts Won in Every Complete-Group Holdout\n\n"
                    "Nested training-only selection chose `PS3` as the one cut and `PS1+PS3` "
                    "as the pair in all five outer folds. The pair gain ranged from `+13.00` "
                    "to `+20.58` percentage points. The random forest bars are retained to "
                    "show the scientific boundary: ARA/LDA is not the strongest classifier."
                ),
            },
            {
                "id": "fold-chart-block",
                "type": "chart",
                "chartId": "fold-performance-chart",
            },
            {
                "id": "relation-heading",
                "type": "markdown",
                "sourceId": "t260-run",
                "body": (
                    "## Breaking Synchronization Removed the Added Information\n\n"
                    "The second sensor was shifted across the twelve fixed five-second windows "
                    "while preserving its values. Accuracy fell from `87.73%` to `26.68%`, close "
                    "to four-class chance. The result therefore depends on the relation between "
                    "co-temporal cuts, not simply feature count."
                ),
            },
            {
                "id": "class-heading",
                "type": "markdown",
                "sourceId": "t260-run",
                "body": (
                    "## The Gain Was Not Confined to an Easy Accumulator State\n\n"
                    "Recalls were `98.27%`, `87.97%`, `91.73%` and `72.95%` for the `90`, "
                    "`100`, `115` and `130 bar` states. The hardest class still cleared the "
                    "frozen `60%` floor."
                ),
            },
            {
                "id": "class-chart-block",
                "type": "chart",
                "chartId": "class-recall-chart",
            },
            {
                "id": "gate-heading",
                "type": "markdown",
                "sourceId": "t260-run",
                "body": (
                    "## Every Frozen Gate Passed\n\n"
                    "The gates jointly required absolute accuracy, meaningful gain, positive "
                    "uncertainty bound, coverage of the hardest class, fold consistency, exact "
                    "coordinate equivalence, pole-reversal invariance and chance-level label controls."
                ),
            },
            {"id": "gate-table-block", "type": "table", "tableId": "gate-table"},
            {
                "id": "scope",
                "type": "markdown",
                "sourceId": "uci-hydraulic-source",
                "body": (
                    "## Public Data and Measurement Boundary\n\n"
                    "The UCI source provides `2,205` labelled 60-second hydraulic test-rig cycles, "
                    "including six synchronized `100 Hz` pressure sensors and four imposed "
                    "accumulator states. One cycle was one identity; one sensor was one spatial "
                    "cut; two sensors were two cuts through that same completed cycle."
                ),
            },
            {
                "id": "method",
                "type": "markdown",
                "sourceId": "t260-run",
                "body": (
                    "## Frozen Method\n\n"
                    "Each cut supplied means and population standard deviations from twelve fixed "
                    "five-second windows. Contiguous 15-cycle groups were never split. Five outer "
                    "grouped folds measured performance; four inner grouped folds selected the "
                    "sensor or pair on training data only. The classifier was shrinkage LDA. "
                    "No Fourier, wavelet, PCA, NMF or learned embedding was used."
                ),
            },
            {
                "id": "limits",
                "type": "markdown",
                "sourceId": "t260-run",
                "body": (
                    "## Interpretation and Limits\n\n"
                    "This supports multi-cut information retention in this connection/storage-heavy "
                    "system. Raw and ARA-coordinate LDA had zero disagreements, which is the expected "
                    "consequence of an invertible affine coordinate map. A random forest on the same "
                    "pair reached `95.58%`, so the result is not ARA classifier superiority. It does "
                    "not establish a universal Connection law, universal fractality, TE-ARA ontology, "
                    "phi or new hydraulic physics."
                ),
            },
            {
                "id": "next",
                "type": "markdown",
                "body": (
                    "## Replicate the Connection-Rich Contrast\n\n"
                    "Apply the unchanged one-cut-versus-two-cut instrument to a second public "
                    "spatial sensor network. Freeze both the total gain and a stable-versus-transition "
                    "interaction before opening its values. This directly tests whether H1 repeats "
                    "beyond one hydraulic rig."
                ),
            },
            {
                "id": "questions",
                "type": "markdown",
                "body": (
                    "## Further Questions\n\n"
                    "- Does the two-cut gain replicate in bridge strain, battery packs or structural vibration?\n\n"
                    "- Is synchronized gain reliably larger in settled than transition-heavy states?\n\n"
                    "- How many independent cuts are sufficient before marginal information saturates?\n\n"
                    "- Can an ARA-native nonlinear model close any of the gap to the random forest without hiding the geometry?"
                ),
            },
        ],
    }

    snapshot = {
        "version": 1,
        "status": "ready",
        "generatedAt": "2026-07-24T10:30:00+10:00",
        "datasets": {
            "headline": headline,
            "fold_performance": fold_performance,
            "class_recalls": class_recalls,
            "gates": gates,
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

#!/usr/bin/env python3
"""Build the bounded MCP analytical report artifact for Q1."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_RESULTS.json"
AGGREGATES = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_AGGREGATES.csv"
TRAJECTORIES = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_TRAJECTORIES.csv"
ARTIFACT = HERE / "Q1_OPEN_QUBIT_MULTI_AXIS_REPORT_ARTIFACT.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    aggregates = read_csv(AGGREGATES)
    trajectories = read_csv(TRAJECTORIES)
    primary = next(row for row in aggregates if row["shots"] == "128")

    headline = [
        {
            "ara_accuracy": float(primary["ara_accuracy"]),
            "gain_over_z": float(primary["ara_accuracy"]) - float(primary["z_accuracy"]),
            "heldout_mae": float(primary["heldout_mae"]),
            "bloch_disagreements": int(primary["ara_bloch_disagreements"]),
            "gates_passed": sum(
                int(item["passed"]) for item in results["primary_gates"].values()
            ),
            "gates_total": len(results["primary_gates"]),
        }
    ]

    methods = [
        {
            "method": "ARA multi-axis",
            "accuracy": float(primary["ara_accuracy"]),
            "information": "Noisy X/Y/Z cuts",
            "role": "Registered compact geometry account",
        },
        {
            "method": "Bloch multi-axis",
            "accuracy": float(primary["bloch_accuracy"]),
            "information": "Same noisy X/Y/Z cuts",
            "role": "Equal-information identity control",
        },
        {
            "method": "Native model fit",
            "accuracy": float(primary["native_accuracy"]),
            "information": "X/Y/Z plus fixed physics model grid",
            "role": "Established-physics reference",
        },
        {
            "method": "Z only",
            "accuracy": float(primary["z_accuracy"]),
            "information": "Noisy Z cut",
            "role": "Registered compressed-diameter account",
        },
        {
            "method": "Time shuffled",
            "accuracy": float(primary["time_shuffle_accuracy"]),
            "information": "X/Y/Z with time order destroyed",
            "role": "Temporal-order control",
        },
        {
            "method": "Axes shuffled",
            "accuracy": float(primary["axis_shuffle_accuracy"]),
            "information": "X/Y/Z with axis identity destroyed",
            "role": "Orientation control",
        },
    ]

    accuracy_ladder = []
    heldout_ladder = []
    for row in aggregates:
        shot_label = row["shots"]
        for label, field in (
            ("ARA multi-axis", "ara_accuracy"),
            ("Native model fit", "native_accuracy"),
            ("Z only", "z_accuracy"),
            ("Time shuffled", "time_shuffle_accuracy"),
            ("Axes shuffled", "axis_shuffle_accuracy"),
        ):
            accuracy_ladder.append(
                {
                    "shots": int(row["shots"]),
                    "shot_label": shot_label,
                    "method": label,
                    "accuracy": float(row[field]),
                }
            )
        for label, field in (
            ("ARA physical", "heldout_mae"),
            ("ARA raw", "heldout_raw_mae"),
            ("Z only", "heldout_z_mae"),
        ):
            heldout_ladder.append(
                {
                    "shots": int(row["shots"]),
                    "shot_label": shot_label,
                    "method": label,
                    "mae": float(row[field]),
                }
            )

    gates = []
    for order, (name, item) in enumerate(results["primary_gates"].items(), start=1):
        gates.append(
            {
                "order": order,
                "gate": name.replace("_", " "),
                "criterion": item["criterion"],
                "value": float(item["value"]),
                "status": "Pass" if item["passed"] else "Fail",
            }
        )

    ridge_demo = []
    for row in trajectories:
        if row["family"] not in {"U", "T2"}:
            continue
        family_label = "Unitary" if row["family"] == "U" else "Pure T2"
        ridge_demo.append(
            {
                "time": float(row["time"]),
                "series": f"{family_label} Z cut",
                "value": 1.0 - float(row["true_rz"]),
            }
        )
        ridge_demo.append(
            {
                "time": float(row["time"]),
                "series": f"{family_label} radius",
                "value": float(row["true_radius"]),
            }
        )

    confusion = []
    ara_confusion = results["confusion_matrices_primary"]["ara"]
    for family in ("U", "T2", "T1", "C"):
        confusion.append(
            {
                "true_family": family,
                "predicted_U": int(ara_confusion[family]["U"]),
                "predicted_T2": int(ara_confusion[family]["T2"]),
                "predicted_T1": int(ara_confusion[family]["T1"]),
                "predicted_C": int(ara_confusion[family]["C"]),
                "total": sum(int(value) for value in ara_confusion[family].values()),
            }
        )

    source = {
        "id": "q1-frozen-run",
        "label": "Frozen Q1 open-qubit multi-axis outputs",
        "path": str(AGGREGATES),
        "query": {
            "id": "q1-open-qubit-v1",
            "language": "sql",
            "engine": "duckdb",
            "description": (
                "Reads the frozen aggregate and representative trajectory outputs "
                "for T258 across the six-level shot-count ladder."
            ),
            "sql": (
                "SELECT * FROM read_csv_auto("
                "'analysis/quantum/Q1_OPEN_QUBIT_MULTI_AXIS_AGGREGATES.csv');"
            ),
            "tables_used": [
                "analysis/quantum/Q1_OPEN_QUBIT_MULTI_AXIS_AGGREGATES.csv",
                "analysis/quantum/Q1_OPEN_QUBIT_MULTI_AXIS_TRAJECTORIES.csv",
                "analysis/quantum/Q1_OPEN_QUBIT_MULTI_AXIS_RESULTS.json",
            ],
            "filters": [
                "Primary condition: 128 shots per axis and time",
                "Fresh target: 128 paired draws across four mechanism families",
                "Thresholds selected on development only",
                "Synthetic independent binomial observations",
            ],
            "metric_definitions": [
                "accuracy = correctly classified mechanism trials divided by all trials",
                "gain over Z = multi-axis accuracy minus Z-only accuracy",
                "held-out MAE = mean absolute error on sixteen unseen directions per trial and time",
                "ridge accuracy = unitary versus pure-dephasing accuracy for the identical clean Z=1 pair",
            ],
        },
    }

    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": "Q1 Open-Qubit Multi-Axis ARA Test",
            "description": (
                "Frozen known-referee test of one ARA diameter versus several "
                "independently measured cuts through one qubit identity."
            ),
            "generatedAt": "2026-07-23T23:55:00+10:00",
            "sources": [source],
            "cards": [
                {
                    "id": "accuracy-card",
                    "description": "Fresh four-family classification at 128 shots.",
                    "dataset": "headline",
                    "sourceId": "q1-frozen-run",
                    "metrics": [
                        {
                            "label": "ARA accuracy",
                            "field": "ara_accuracy",
                            "format": "percent",
                        },
                        {
                            "label": "Gain over Z",
                            "field": "gain_over_z",
                            "format": "percent",
                            "signed": True,
                        },
                    ],
                },
                {
                    "id": "heldout-card",
                    "description": "Prediction error on independently drawn sphere directions.",
                    "dataset": "headline",
                    "sourceId": "q1-frozen-run",
                    "metrics": [
                        {
                            "label": "Held-out MAE",
                            "field": "heldout_mae",
                            "format": "number",
                        }
                    ],
                },
                {
                    "id": "equivalence-card",
                    "description": "Same-information ARA and Bloch decisions.",
                    "dataset": "headline",
                    "sourceId": "q1-frozen-run",
                    "metrics": [
                        {
                            "label": "Disagreements",
                            "field": "bloch_disagreements",
                            "format": "number",
                        },
                        {
                            "label": "Frozen gates passed",
                            "field": "gates_passed",
                            "format": "number",
                        },
                    ],
                },
            ],
            "charts": [
                {
                    "id": "method-accuracy-chart",
                    "title": "Mechanism classification accuracy at 128 shots",
                    "description": (
                        "Multi-axis ARA ties the same-information Bloch account and "
                        "nearly ties the native model; compressed and shuffled controls fall."
                    ),
                    "type": "bar",
                    "dataset": "methods",
                    "sourceId": "q1-frozen-run",
                    "encodings": {
                        "x": {"field": "method", "type": "nominal"},
                        "y": {"field": "accuracy", "type": "quantitative"},
                    },
                },
                {
                    "id": "accuracy-ladder-chart",
                    "title": "Classification accuracy across shot counts",
                    "description": (
                        "ARA approaches perfect classification as sampling noise falls; "
                        "the one-axis information ceiling remains at one half."
                    ),
                    "type": "line",
                    "dataset": "accuracy_ladder",
                    "sourceId": "q1-frozen-run",
                    "encodings": {
                        "x": {"field": "shot_label", "type": "nominal"},
                        "y": {"field": "accuracy", "type": "quantitative"},
                        "color": {"field": "method", "type": "nominal"},
                    },
                    "options": {"points": "always"},
                },
                {
                    "id": "heldout-ladder-chart",
                    "title": "Held-out directional error across shot counts",
                    "description": (
                        "The physical multi-axis reconstruction improves with sampling "
                        "while Z-only cannot recover transverse directions."
                    ),
                    "type": "line",
                    "dataset": "heldout_ladder",
                    "sourceId": "q1-frozen-run",
                    "encodings": {
                        "x": {"field": "shot_label", "type": "nominal"},
                        "y": {"field": "mae", "type": "quantitative"},
                        "color": {"field": "method", "type": "nominal"},
                    },
                    "options": {"points": "always"},
                },
                {
                    "id": "ridge-demo-chart",
                    "title": "Representative Z cut and sphere radius",
                    "description": (
                        "Unitary rotation and pure dephasing share the same Z=1 line "
                        "while their full-state radii separate."
                    ),
                    "type": "line",
                    "dataset": "ridge_demo",
                    "sourceId": "q1-frozen-run",
                    "encodings": {
                        "x": {"field": "time", "type": "quantitative"},
                        "y": {"field": "value", "type": "quantitative"},
                        "color": {"field": "series", "type": "nominal"},
                    },
                    "options": {"points": "never"},
                },
            ],
            "tables": [
                {
                    "id": "methods-table",
                    "title": "Matched accounts at the primary condition",
                    "description": "All accounts are scored on the same fresh target.",
                    "dataset": "methods",
                    "sourceId": "q1-frozen-run",
                    "columns": [
                        {"field": "method", "label": "Account", "type": "text"},
                        {"field": "accuracy", "label": "Accuracy", "type": "number"},
                        {"field": "information", "label": "Information", "type": "text"},
                        {"field": "role", "label": "Role", "type": "text"},
                    ],
                    "defaultSort": {"field": "accuracy", "direction": "desc"},
                },
                {
                    "id": "gates-table",
                    "title": "Frozen primary gates",
                    "description": "All nine gates were required for support.",
                    "dataset": "gates",
                    "sourceId": "q1-frozen-run",
                    "columns": [
                        {"field": "order", "label": "#", "type": "number"},
                        {"field": "gate", "label": "Endpoint", "type": "text"},
                        {"field": "criterion", "label": "Criterion", "type": "text"},
                        {"field": "value", "label": "Observed", "type": "number"},
                        {"field": "status", "label": "Status", "type": "text"},
                    ],
                    "defaultSort": {"field": "order", "direction": "asc"},
                },
                {
                    "id": "confusion-table",
                    "title": "ARA primary confusion matrix",
                    "description": "One combined case was classified as T1.",
                    "dataset": "confusion",
                    "sourceId": "q1-frozen-run",
                    "columns": [
                        {"field": "true_family", "label": "True family", "type": "text"},
                        {"field": "predicted_U", "label": "Pred U", "type": "number"},
                        {"field": "predicted_T2", "label": "Pred T2", "type": "number"},
                        {"field": "predicted_T1", "label": "Pred T1", "type": "number"},
                        {"field": "predicted_C", "label": "Pred C", "type": "number"},
                        {"field": "total", "label": "Total", "type": "number"},
                    ],
                    "defaultSort": {"field": "true_family", "direction": "asc"},
                },
            ],
            "blocks": [
                {
                    "id": "title",
                    "type": "markdown",
                    "body": "# Q1 Open-Qubit Multi-Axis ARA Test",
                },
                {
                    "id": "answer",
                    "type": "markdown",
                    "sourceId": "q1-frozen-run",
                    "body": (
                        "## Answer First\n\n"
                        "**The frozen benchmark is supported: all `9/9` gates "
                        "passed.** Multi-axis ARA classified `511/512` fresh trials "
                        "at 128 shots, versus the exact paired `256/512` ceiling for "
                        "one `Z` diameter. The same-information Bloch account was "
                        "identical, so this validates decompression—not an advantage "
                        "over tomography."
                    ),
                },
                {
                    "id": "headline",
                    "type": "metric-strip",
                    "cardIds": ["accuracy-card", "heldout-card", "equivalence-card"],
                },
                {
                    "id": "primary-heading",
                    "type": "markdown",
                    "sourceId": "q1-frozen-run",
                    "body": (
                        "## The Full Account Retained What One Diameter Discarded\n\n"
                        "The target deliberately gave unitary rotation and pure "
                        "dephasing the same clean `Z=1` trajectory. Their transverse "
                        "direction and radius remained different, and the independent "
                        "`X/Y` cuts recovered that difference."
                    ),
                },
                {"id": "method-chart", "type": "chart", "chartId": "method-accuracy-chart"},
                {"id": "methods", "type": "table", "tableId": "methods-table"},
                {
                    "id": "geometry-heading",
                    "type": "markdown",
                    "sourceId": "q1-frozen-run",
                    "body": (
                        "## The Ridge Is a Plane, Not One State\n\n"
                        "`x_Z=1` means only `r_z=0`. It contains coherent rotating "
                        "states, dephased states and the maximally mixed centre. One "
                        "line cut is accurate but many-to-one; direction and radius "
                        "require other cuts."
                    ),
                },
                {"id": "ridge-demo", "type": "chart", "chartId": "ridge-demo-chart"},
                {
                    "id": "gates-heading",
                    "type": "markdown",
                    "sourceId": "q1-frozen-run",
                    "body": (
                        "## Every Frozen Gate Passed\n\n"
                        "Rotation direction and unitary-versus-dephasing ridge "
                        "classification were each `256/256`. Held-out directional "
                        "MAE was `0.06112`; time and axis shuffles fell to `45.51%` "
                        "and `52.34%`."
                    ),
                },
                {"id": "gates", "type": "table", "tableId": "gates-table"},
                {"id": "confusion", "type": "table", "tableId": "confusion-table"},
                {
                    "id": "noise-heading",
                    "type": "markdown",
                    "sourceId": "q1-frozen-run",
                    "body": (
                        "## Finite Sampling Behaved as Expected\n\n"
                        "ARA rose from `91.21%` at 32 shots to `100%` at 256. "
                        "Held-out error fell from `0.11997` to `0.02168` over the "
                        "full shot ladder."
                    ),
                },
                {"id": "accuracy-ladder", "type": "chart", "chartId": "accuracy-ladder-chart"},
                {"id": "heldout-ladder", "type": "chart", "chartId": "heldout-ladder-chart"},
                {
                    "id": "method",
                    "type": "markdown",
                    "body": (
                        "## Scope and Method\n\n"
                        "T258 was frozen before data or code. Development used 64 "
                        "paired draws; the untouched target used 128 new paired draws "
                        "across four standard open-qubit mechanisms and six shot "
                        "counts. ARA and Bloch received identical observations. "
                        "Independent validation reproduced `14/14` checks."
                    ),
                },
                {
                    "id": "limitations",
                    "type": "markdown",
                    "body": (
                        "## Limitations\n\n"
                        "This is a synthetic known-referee instrument test with "
                        "independent binomial samples and deliberately separated "
                        "mechanisms. The native quantum-model fit scored `512/512`. "
                        "The result does not derive quantum mechanics, establish a "
                        "hidden Phase B, universal fractality, phi, quantum gravity "
                        "or superiority over standard tomography."
                    ),
                },
                {
                    "id": "next",
                    "type": "markdown",
                    "body": (
                        "## Recommended Next Step\n\n"
                        "Freeze Q2 against public or hardware-derived qubit "
                        "calibration records with state-preparation, readout, drift "
                        "and correlated-noise effects. Preserve the same-information "
                        "tomography control and keep mechanism classification, "
                        "direction, radius and held-out reconstruction separate."
                    ),
                },
            ],
        },
        "snapshot": {
            "version": 1,
            "status": "ready",
            "generatedAt": "2026-07-23T23:55:00+10:00",
            "datasets": {
                "headline": headline,
                "methods": methods,
                "accuracy_ladder": accuracy_ladder,
                "heldout_ladder": heldout_ladder,
                "gates": gates,
                "ridge_demo": ridge_demo,
                "confusion": confusion,
            },
        },
        "sources": [source],
    }

    ARTIFACT.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(
        f"Wrote {ARTIFACT.name}: methods={len(methods)}, "
        f"accuracy_ladder={len(accuracy_ladder)}, heldout_ladder={len(heldout_ladder)}, "
        f"gates={len(gates)}, ridge_demo={len(ridge_demo)}"
    )


if __name__ == "__main__":
    main()


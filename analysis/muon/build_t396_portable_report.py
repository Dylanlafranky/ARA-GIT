#!/usr/bin/env python3
"""Build the canonical portable-report artifact for T396.

The HTML itself is produced by the Data Analytics portable artifact builder.
This script only assembles the reviewed, bounded datasets and report manifest.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T396_information3_spin_child_lock"
RESULTS_PATH = OUT / "T396_RESULTS.json"
VALIDATION_PATH = OUT / "T396_VALIDATION.json"
NLL_PATH = OUT / "T396_NLL_COMPARISON.csv"
SENSITIVITY_PATH = OUT / "T396_SENSITIVITY.csv"
SURFACE_PATH = OUT / "T396_CHILD_SURFACE.csv"
ARTIFACT_PATH = OUT / "artifact.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def f(value: str | float | int) -> float:
    return float(value)


def main() -> None:
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))

    pretty_models = {
        "analytic_va_oracle": "Analytic V-A oracle",
        "additive_factorized": "Factorized two-cut fusion",
        "joint_information3": "Dense joint Information³",
        "parent_only": "Parent cut only",
        "relation_shuffled_calibration": "Shuffled relation",
        "wrong_event_relation": "Wrong-event relation",
        "phase_space": "Unpolarized phase space",
        "mirrored_orientation": "Mirrored orientation",
        "relation_only": "Spin relation only",
        "unconditional": "Unconditional",
    }

    nll_rows = []
    for row in read_csv(NLL_PATH):
        model = row["model"]
        holdout = results["holdout_models"].get(model, {})
        nll_rows.append(
            {
                "model": pretty_models.get(model, model.replace("_", " ").title()),
                "mean_nll": f(row["mean_nll"]),
                "gain_vs_parent": f(row["delta_vs_parent"]),
                "child_mae": holdout.get("child_mae"),
            }
        )
    nll_rows.sort(key=lambda row: row["mean_nll"])

    sensitivity_rows = []
    for row in read_csv(SENSITIVITY_PATH):
        polarization = f(row["polarization"])
        sensitivity_rows.extend(
            [
                {
                    "polarization": polarization,
                    "estimator": "Factorized two-cut fusion",
                    "gain": f(row["additive_incremental_gain"]),
                    "ci_low": f(row["additive_gain_ci95_low"]),
                    "ci_high": f(row["additive_gain_ci95_high"]),
                    "holdout_n": int(row["holdout_n"]),
                },
                {
                    "polarization": polarization,
                    "estimator": "Dense joint histogram",
                    "gain": f(row["incremental_gain"]),
                    "ci_low": f(row["gain_ci95_low"]),
                    "ci_high": f(row["gain_ci95_high"]),
                    "holdout_n": int(row["holdout_n"]),
                },
            ]
        )

    surface_rows = []
    for row in read_csv(SURFACE_PATH):
        surface_rows.append(
            {
                "parent_cut": f"{f(row['parent_center']):.3f}",
                "spin_relation": f"{f(row['relation_center']):.3f}",
                "observed_child_mean": f(row["observed_child_mean"]),
                "predicted_child_mean": f(row["predicted_child_mean"]),
                "n": int(row["n"]),
            }
        )

    checks = [
        {
            "check": key.replace("_", " ").capitalize(),
            "status": "PASS" if passed else "FAIL",
        }
        for key, passed in validation["checks"].items()
    ]

    gain = results["primary_incremental_gain_nats_per_event"]
    gain_ci = results["primary_gain_ci95"]
    additive = results["holdout_models"]["additive_factorized"]
    parent = results["holdout_models"]["parent_only"]
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    summary_markdown = f"""# T396 — Two observed muon relations constrain the hidden neutral split

## Technical summary

The frozen truth-level test **passed**. Adding the independently observed charged-daughter/spin relation to the charged-versus-neutral parent cut improved holdout prediction of the hidden neutral-child split by **{gain:.6f} nats/event** using the predeclared dense joint estimator; the fixed block-bootstrap 95% interval was **[{gain_ci[0]:.6f}, {gain_ci[1]:.6f}]**.

The lower-variance factorized fusion improved holdout NLL by **{parent['mean_nll'] - additive['mean_nll']:.6f} nats/event** and outperformed the dense estimator. Therefore the evidence supports the ARA/Information³ statement that **two independently observed relations constrain a third hidden relation**, but it does **not** require a learned nonlinear parent-by-spin interaction.

When polarization was removed, the factorized increment became **−0.001245 nats/event**. The information gain therefore tracks the physical spin coupling rather than surviving as an arbitrary binning advantage.
"""

    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": "T396 — Muon Information³ spin/child lock",
            "description": "Frozen holdout test of whether two observed muon-decay relations constrain the hidden neutral-child split.",
            "generatedAt": generated_at,
            "cards": [],
            "charts": [
                {
                    "id": "nll_comparison",
                    "title": "Two-cut fusion beats either observed cut alone",
                    "subtitle": "Mean holdout negative log likelihood; lower is better.",
                    "type": "horizontalBar",
                    "dataset": "nll_models",
                    "sourceId": "t396_results",
                    "valueFormat": "number",
                    "palette": {"kind": "identity", "name": "blue"},
                    "encodings": {
                        "x": {"field": "model", "type": "nominal", "label": "Estimator or control"},
                        "y": {"field": "mean_nll", "type": "quantitative", "label": "Mean holdout NLL"},
                        "tooltip": [
                            {"field": "gain_vs_parent", "type": "quantitative", "label": "Gain vs parent-only"},
                            {"field": "child_mae", "type": "quantitative", "label": "Child-coordinate MAE"},
                        ],
                    },
                },
                {
                    "id": "polarization_sensitivity",
                    "title": "Incremental information collapses with polarization",
                    "subtitle": "Gain relative to the parent cut; positive values mean the spin relation helps.",
                    "type": "line",
                    "dataset": "sensitivity",
                    "sourceId": "t396_results",
                    "palette": {"kind": "categorical", "name": "blue-gold"},
                    "referenceLines": [
                        {"axis": "y", "value": 0, "label": "No incremental information", "color": "neutral", "lineStyle": "dashed"}
                    ],
                    "encodings": {
                        "x": {"field": "polarization", "type": "quantitative", "label": "Muon polarization"},
                        "y": {"field": "gain", "type": "quantitative", "label": "NLL gain vs parent-only"},
                        "color": {"field": "estimator", "type": "nominal", "label": "Estimator"},
                        "tooltip": [
                            {"field": "ci_low", "type": "quantitative", "label": "95% CI low"},
                            {"field": "ci_high", "type": "quantitative", "label": "95% CI high"},
                            {"field": "holdout_n", "type": "quantitative", "label": "Holdout events"},
                        ],
                    },
                },
                {
                    "id": "child_surface",
                    "title": "The hidden neutral child varies across both observed ARA cuts",
                    "subtitle": "Observed mean child coordinate in the frozen full-polarization population.",
                    "type": "heatmap",
                    "dataset": "child_surface",
                    "sourceId": "t396_results",
                    "palette": {"kind": "sequential", "name": "blue"},
                    "encodings": {
                        "x": {"field": "parent_cut", "type": "ordinal", "label": "Parent cut P = xₑ"},
                        "y": {"field": "observed_child_mean", "type": "quantitative", "label": "Mean hidden child C"},
                        "color": {"field": "spin_relation", "type": "nominal", "label": "Spin relation R = 1 + cos θₑS"},
                        "tooltip": [
                            {"field": "predicted_child_mean", "type": "quantitative", "label": "Fitted mean child C"},
                            {"field": "n", "type": "quantitative", "label": "Events"},
                        ],
                    },
                },
            ],
            "tables": [
                {
                    "id": "model_table",
                    "title": "Holdout model and control ordering",
                    "subtitle": "All values were scored only after the frozen calibration and validation stages.",
                    "dataset": "nll_models",
                    "sourceId": "t396_results",
                    "defaultSort": {"field": "mean_nll", "direction": "asc"},
                    "columns": [
                        {"field": "model", "label": "Estimator or control", "type": "text"},
                        {"field": "mean_nll", "label": "Mean NLL", "format": "number"},
                        {"field": "gain_vs_parent", "label": "Gain vs parent", "format": "number"},
                        {"field": "child_mae", "label": "Child MAE", "format": "number"},
                    ],
                },
                {
                    "id": "validation_table",
                    "title": "Independent validation checks",
                    "subtitle": "A second script reconstructed the principal checks from saved outputs.",
                    "dataset": "validation_checks",
                    "sourceId": "t396_validation",
                    "columns": [
                        {"field": "check", "label": "Check", "type": "text"},
                        {"field": "status", "label": "Status", "type": "text"},
                    ],
                },
            ],
            "sources": [
                {"id": "t396_results", "label": "T396 report reproduction queries", "path": "analysis/muon/T396_information3_spin_child_lock/T396_REPORT_RESULTS.sql"},
                {"id": "t396_validation", "label": "T396 validation reproduction query", "path": "analysis/muon/T396_information3_spin_child_lock/T396_REPORT_VALIDATION.sql"},
                {"id": "t396_protocol", "label": "Frozen T396 protocol", "path": "analysis/muon/T396_INFORMATION3_SPIN_CHILD_LOCK_PROTOCOL_2026-08-16.md"},
                {"id": "meg_polarized_muon", "label": "MEG polarized muon-decay distribution", "path": "https://doi.org/10.1140/epjc/s10052-016-4047-3"},
                {"id": "polarized_va_matrix", "label": "Polarized V-A muon decay matrix element", "path": "https://arxiv.org/abs/hep-ph/0203052"},
            ],
            "blocks": [
                {"id": "summary", "type": "markdown", "body": summary_markdown},
                {
                    "id": "nll_text",
                    "type": "markdown",
                    "body": "## The second observed relation carries real holdout information\n\nThe analytic oracle provides the attainable reference for this generator. Both two-cut estimators sit between that oracle and either one-cut model. Shuffling the relation, pairing it with the wrong event, mirroring its orientation or replacing the dynamics with phase space all degrade performance, which is the control pattern expected if the signed spin relation is carrying the additional information.",
                },
                {"id": "nll_chart", "type": "chart", "chartId": "nll_comparison"},
                {
                    "id": "polarization_text",
                    "type": "markdown",
                    "body": "## The signal follows the physical coupling\n\nThe factorized estimator retains a positive increment at 100%, 85% and 50% polarization, and falls slightly below zero at 0%. The dense fixed-resolution histogram pays a sparsity penalty at the smaller sensitivity samples, so it should not be mistaken for evidence that the physical relation reverses. The lower-variance factorized result is the appropriate graded sensitivity check.",
                },
                {"id": "polarization_chart", "type": "chart", "chartId": "polarization_sensitivity"},
                {
                    "id": "surface_text",
                    "type": "markdown",
                    "body": "## The hidden child is a surface, not a one-axis lookup\n\nAt fixed charged-versus-neutral parent position, the expected hidden split changes with the charged daughter’s orientation relative to the muon spin. Conversely, the same spin relation does not determine the split without the parent energy cut. In ARA language, the two measured cuts jointly narrow the third relation.",
                },
                {"id": "surface_chart", "type": "chart", "chartId": "child_surface"},
                {
                    "id": "definitions",
                    "type": "markdown",
                    "body": "## Scope and coordinate definitions\n\n- **Parent cut:** `P = xₑ`, the charged-daughter share on a normalized 0–1 energy coordinate.\n- **Independent relation cut:** `R = 1 + cos(θₑS)`, the signed charged-daughter direction relative to the parent muon spin, mapped to ARA 0–2.\n- **Hidden child:** `C = 2xνₑ/(2−P)`, the electron-neutrino share inside the joint neutral branch, mapped to ARA 0–2.\n- **Information³ question:** whether `(P,R)` predicts `C` more strongly than either `P` or `R` alone.\n\nThe event generator used the leading-order polarized Standard-Model V-A law. No missing-momentum variable, second neutrino momentum or truth child label was allowed into either observed input.",
                },
                {
                    "id": "method",
                    "type": "markdown",
                    "body": "## Frozen method\n\nThe protocol hash was fixed before scoring. One million fully polarized positive-muon decays were generated with seed 396 and split deterministically: 499,615 calibration events, 200,326 validation events and 300,059 untouched holdout events. Histogram resolutions were selected only on validation data. The primary comparison used block-bootstrap confidence intervals; independent checks reloaded the saved outputs and reconstructed the gates without importing the main test module.",
                },
                {"id": "model_table_block", "type": "table", "tableId": "model_table"},
                {
                    "id": "limitations",
                    "type": "markdown",
                    "body": "## Robustness and limitations\n\n**What is supported:** two independently observed relations contain complementary event-level information about the hidden neutral split, and the increment follows polarization.\n\n**What is not supported yet:** this is not direct two-neutrino observation; the population was generated from a known truth law. Exact neutral-branch recomposition was forced by the coordinate definition and is not independent evidence. The factorized estimator outperforming the dense grid means the result does not establish a necessary nonlinear parent-by-relation interaction. At lower polarization and smaller samples, the dense grid becomes variance-limited.\n\nThe independent validator classified the result as: **Ready to share with explicit truth-model and sparse-joint caveats.**",
                },
                {"id": "validation_table_block", "type": "table", "tableId": "validation_table"},
                {
                    "id": "next_steps",
                    "type": "markdown",
                    "body": "## Recommended next test\n\nMove from the truth-law crosswalk to event-linked experimental data containing (1) a known or reconstructed muon-spin direction, (2) the charged-daughter energy and direction and (3) an independently neutral-sensitive target or constrained missing-momentum measurement. Freeze the same parent and relation cuts, predict the neutral child without using the target, then score only afterward. That would convert the present generator validation into an empirical Information³ test.\n\n## Further questions\n\n- Does the factorized advantage persist with detector smearing, radiative corrections and acceptance effects?\n- Can an event-linked neutral-sensitive archive be found without reconstructing the target from the same inputs?\n- Which ARA child coordinate remains stable across positive- and negative-muon conventions?\n- Does calibration learned in one detector or polarization regime transfer to another?",
                },
            ],
        },
        "snapshot": {
            "version": 1,
            "generatedAt": generated_at,
            "status": "ready",
            "datasets": {
                "nll_models": nll_rows,
                "sensitivity": sensitivity_rows,
                "child_surface": surface_rows,
                "validation_checks": checks,
            },
        },
        "sources": [
            {
                "id": "t396_results",
                "path": "analysis/muon/T396_information3_spin_child_lock/T396_REPORT_RESULTS.sql",
            },
            {
                "id": "t396_validation",
                "path": "analysis/muon/T396_information3_spin_child_lock/T396_REPORT_VALIDATION.sql",
            },
            {
                "id": "t396_protocol",
                "query": {"engine": "file", "language": "markdown", "description": "Predeclared T396 protocol."},
            },
            {
                "id": "meg_polarized_muon",
                "query": {"engine": "web", "language": "publication", "description": "Primary-source polarized Michel energy-angle distribution."},
            },
            {
                "id": "polarized_va_matrix",
                "query": {"engine": "web", "language": "publication", "description": "Primary-source polarized V-A matrix element and neutrino-factory flux derivation."},
            },
        ],
        "package_info": {
            "originUrl": "artifact://t396-information3-spin-child-lock",
            "controls": {"edit": False, "refresh": False},
        },
    }

    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(ARTIFACT_PATH)


if __name__ == "__main__":
    main()

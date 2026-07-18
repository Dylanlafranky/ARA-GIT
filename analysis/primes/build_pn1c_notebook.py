#!/usr/bin/env python3
"""Build and execute the PN1C reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK_PATH = HERE / "PN1C_COMPRESSION_REPRODUCIBILITY.ipynb"
VALIDATION_PATH = HERE / "PN1C_NOTEBOOK_EXECUTION_VALIDATION.json"


def markdown(source: str) -> dict[str, object]:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str) -> dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def execute_cells(cells: list[dict[str, object]]) -> dict[str, object]:
    namespace: dict[str, object] = {"__name__": "__pn1c_notebook__"}
    original_cwd = Path.cwd()
    execution_count = 0
    executed = 0
    errors: list[str] = []
    try:
        os.chdir(HERE)
        for index, cell in enumerate(cells):
            if cell["cell_type"] != "code":
                continue
            execution_count += 1
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exec(
                        compile("".join(cell["source"]), f"PN1C-cell-{index + 1}", "exec"),
                        namespace,
                        namespace,
                    )
                cell["execution_count"] = execution_count
                output = stdout.getvalue()
                if output:
                    cell["outputs"] = [
                        {
                            "name": "stdout",
                            "output_type": "stream",
                            "text": output.splitlines(keepends=True),
                        }
                    ]
                executed += 1
            except Exception as exc:
                errors.append(f"cell {index + 1}: {type(exc).__name__}: {exc}")
                raise
    finally:
        os.chdir(original_cwd)
    return {
        "all_code_cells_executed": executed
        == sum(cell["cell_type"] == "code" for cell in cells),
        "executed_code_cells": executed,
        "errors": errors,
    }


def main() -> None:
    cells = [
        markdown(
            """# PN1C parameter-matched sieve-rung compression competition

## TL;DR

The frozen claim was **not supported**. On the held-out prime-19 to prime-23 transition, the 35-slot fixed 6×6 ARA grid scored **0.470280 bits** of Jensen–Shannon divergence. The 31-slot gap-IID rival won at **0.230999 bits** and won separately in both child halves. Every exact check and the independent reconstruction passed.

This falsifies the narrow claim that this fixed ARA grid and uniform decoder is the best ≤36-slot compressor. It does not falsify the ARA coordinate or PN1's result that local order survives sieve rungs.
"""
        ),
        markdown(
            r"""## 1. Setup and frozen test

For adjacent circular gaps, the bounded coordinate is

\[x_i=\frac{2g_{i+1}}{g_i+g_{i+1}}\in(0,2),\qquad Z_i=(x_i,x_{i+1}).\]

The target is the prime-23 wheel's 24×24 distribution of \(Z_i\). The parent is the complete prime-19 wheel. Six frozen competitors receive no more than 36 declared scalar slots. The primary prediction requires ARA to have strictly smallest JSD and beat the best rival by at least 1% relative.

Frozen protocol SHA-256: `7DAA061BA790B12461ED60136FD9C50F3A36C10BED472819CFCC08B4B3462DBF`.
"""
        ),
        code(
            """from pathlib import Path
import json
import numpy as np
import pandas as pd

from pn1c_compression_test import run_analysis

HERE = Path.cwd()
results = run_analysis(HERE)
print("\\nReproduced frozen summary:")
print(json.dumps(results["summary"], indent=2))
"""
        ),
        markdown(
            """## 2. Primary comparison

Lower Jensen–Shannon divergence means the compressed parent predicts the held-out child more closely. High-budget and exact-parent models are displayed as reference ceilings but are not eligible for the primary ≤36-slot contest.
"""
        ),
        code(
            """scores = pd.read_csv(HERE / "PN1C_MODEL_SCORES.csv")
columns = ["model", "slots", "eligible_primary", "jsd_bits", "pair_jsd_mean_bits", "gain_over_uniform_per_slot"]
print(scores[columns].to_string(index=False, float_format=lambda value: f"{value:.6f}"))

eligible = scores[scores["eligible_primary"]].sort_values("jsd_bits")
ara = float(eligible.loc[eligible["model"] == "ARA-linear-6", "jsd_bits"].iloc[0])
winner = eligible.iloc[0]
print(f"\\nEligible winner: {winner['model']} at {winner['jsd_bits']:.6f} bits")
print(f"ARA / winner divergence ratio: {ara / float(winner['jsd_bits']):.3f}x")
"""
        ),
        markdown(
            """![Frozen PN1C scores and budget frontier](PN1C_COMPRESSION_FIGURE.png)

The ARA grid improves on uniform, but its divergence is 2.036 times the winning gap-IID divergence. The 1% superiority threshold is therefore missed decisively rather than narrowly.
"""
        ),
        markdown(
            """## 3. Robustness, target geometry and diagnosis

The target is a discrete web rather than a smooth field. Uniform decompression spreads each ARA coarse-cell mass over all 16 fine cells inside it. A gap marginal keeps the allowed gap identities and projects their combinations into the same ARA plane.
"""
        ),
        code(
            """split = pd.read_csv(HERE / "PN1C_SPLIT_HALF.csv")
frontier = pd.read_csv(HERE / "PN1C_BUDGET_FRONTIER.csv")
checks = pd.read_csv(HERE / "PN1C_CALIBRATION_CHECKS.csv")
print("Split halves:")
print(split.to_string(index=False, float_format=lambda value: f"{value:.6f}"))
print("\\nFixed-coordinate budget frontier:")
print(frontier.to_string(index=False, float_format=lambda value: f"{value:.6f}"))
print(f"\\nExact checks passing: {int(checks['passes'].sum())}/{len(checks)}")

with np.load(HERE / "PN1C_TARGET_AND_PREDICTIONS.npz") as archive:
    target = archive["target_counts"].astype(float)
    target /= target.sum()
    ara_prediction = archive["prediction_ARA_linear_6"]
    gap_prediction = archive["prediction_Gap_IID"]
    support = target > 0
    print(f"Target-support mass — ARA: {ara_prediction[support].sum():.6f}")
    print(f"Target-support mass — Gap-IID: {gap_prediction[support].sum():.6f}")
"""
        ),
        markdown(
            """![PN1C target and decompression diagnostic](PN1C_DISTRIBUTION_DIAGNOSTIC.png)

The gap model assigns 99.28% of its probability to cells that occur in the child; ARA assigns 84.80%. This locates the loss in the frozen coarse-graining/decompression rule, not in absence of a parent-to-child relation.
"""
        ),
        markdown(
            """## 4. Independent reconstruction

The audit below does not import the primary analysis. It generates residues through repeated modulus filtering, materializes all 36,495,360 child gaps, counts circular triples through indexed chunks, and independently rebuilds every model and metric.
"""
        ),
        code(
            """import pn1c_independent_validator as validator

validator.main()
with (HERE / "PN1C_INDEPENDENT_VALIDATION.json").open(encoding="utf-8") as handle:
    validation = json.load(handle)
print("\\nIndependent validation summary:")
print(json.dumps({
    "all_checks_pass": validation["all_checks_pass"],
    "target_gap_sha256": validation["target_gap_sha256"],
    "max_prediction_abs_error": validation["max_prediction_abs_error"],
    "max_metric_abs_error": validation["max_metric_abs_error"],
    "independent_primary_winner": validation["independent_primary_winner"],
}, indent=2))
"""
        ),
        markdown(
            """## 5. Conclusion and next clean test

PN1C rejects the fixed-grid compression advantage. The result suggests that a future ARA state needs a predeclared support-, identity- or transition-aware decompression law if it is to preserve this arithmetic web under strong compression.

Prime 23 is now development data. Any revised model must be chosen using rungs only through 23, frozen, and then tested on an unopened prime-29 wheel. A stronger comparison should use literal fixed-bit or minimum-description-length budgets because scalar-slot counts do not charge all labels, probabilities and fixed algorithms by their true encoding cost.

The post-open repair was serialization-only: pandas changed the Uniform reference's undefined gain-per-slot from `None` to `NaN`, which strict JSON rejected. The writer now maps that display value to JSON `null`; no mathematical object or result changed.
"""
        ),
        markdown(
            """## Provenance

- Test ID: `T228 / PN1C/v1`
- Protocol: `PN1C_COMPRESSION_PROTOCOL_v1_FROZEN.md`
- Primary analysis: `pn1c_compression_test.py`
- Independent audit: `pn1c_independent_validator.py`
- Canonical result: `PN1C_COMPRESSION_RESULTS.json`
- Full written interpretation: `PN1C_COMPRESSION_RESULT.md`
"""
        ),
    ]

    execution = execute_cells(cells)
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK_PATH.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")

    with (HERE / "PN1C_INDEPENDENT_VALIDATION.json").open(encoding="utf-8") as handle:
        independent_validation = json.load(handle)
    code_cells = [cell for cell in cells if cell["cell_type"] == "code"]
    structural_checks = {
        "nbformat_is_4": notebook["nbformat"] == 4,
        "first_cell_is_markdown_title": cells[0]["cell_type"] == "markdown"
        and "".join(cells[0]["source"]).startswith("# "),
        "all_code_cells_have_execution_count": all(
            cell["execution_count"] is not None for cell in code_cells
        ),
        "no_code_cell_errors": not execution["errors"],
        "all_code_cells_executed": execution["all_code_cells_executed"],
        "independent_validation_passed": bool(independent_validation["all_checks_pass"]),
    }
    record = {
        "notebook": NOTEBOOK_PATH.name,
        "execution": execution,
        "structural_checks": structural_checks,
        "all_checks_pass": all(structural_checks.values()),
    }
    VALIDATION_PATH.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()

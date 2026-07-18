#!/usr/bin/env python3
"""Build and execute the PN1 reproducibility notebook without Jupyter dependencies."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK_PATH = HERE / "PN1_SIEVE_RUNG_REPRODUCIBILITY.ipynb"
VALIDATION_PATH = HERE / "PN1_NOTEBOOK_EXECUTION_VALIDATION.json"


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
    namespace: dict[str, object] = {"__name__": "__pn1_notebook__"}
    original_cwd = Path.cwd()
    execution_count = 0
    executed_code_cells = 0
    errors: list[str] = []
    try:
        os.chdir(HERE)
        for index, cell in enumerate(cells):
            if cell["cell_type"] != "code":
                continue
            execution_count += 1
            source = "".join(cell["source"])
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exec(compile(source, f"PN1-cell-{index + 1}", "exec"), namespace, namespace)
                cell["execution_count"] = execution_count
                output = stdout.getvalue()
                if output:
                    cell["outputs"] = [
                        {"name": "stdout", "output_type": "stream", "text": output.splitlines(keepends=True)}
                    ]
                executed_code_cells += 1
            except Exception as exc:  # recorded before re-raising to prevent silent partial notebooks
                errors.append(f"cell {index + 1}: {type(exc).__name__}: {exc}")
                raise
    finally:
        os.chdir(original_cwd)
    return {
        "all_code_cells_executed": executed_code_cells
        == sum(cell["cell_type"] == "code" for cell in cells),
        "executed_code_cells": executed_code_cells,
        "errors": errors,
    }


def main() -> None:
    cells = [
        markdown(
            """# PN1 primorial sieve-rung relational inheritance\n
\n
## TL;DR\n
\n
The frozen held-out claim passed **4/4** comparisons. Across both unseen sieve transitions, the ordered parent wheel was much closer to the child than order-destroyed parents with the same gap multiset. Every one-sided permutation value was the minimum possible with 200 shuffles, **p = 1/201 = 0.004975**. Exact sieve checks passed, as did all split-half and bin-sensitivity checks.\n
\n
**Rating:** `SUPPORTED [pre-registered, arithmetic, unreplicated]`. This is a finite arithmetic result about retained cyclic order. It is not evidence for the Riemann Hypothesis or physical universality, and the bounded ARA coordinate is exactly equivalent to a conventional log-gap-ratio coordinate.\n
"""
        ),
        markdown(
            """## Scope, frozen protocol and metric\n
\n
The development rungs end at prime 13. The held-out transitions are 13→17 and 17→19. For adjacent circular wheel gaps \\(g_i,g_{i+1}>0\\), the bounded coordinate is\n
\n
\\[x_i=\\frac{2g_{i+1}}{g_i+g_{i+1}}\\in(0,2).\\]\n
\n
The pair histogram uses \\(x_i\\); the overlapping triple histogram uses \\((x_i,x_{i+1})\\). Jensen–Shannon divergence measures parent-to-child distribution change. The null independently shuffles each parent circular gap list 200 times, preserving every gap and destroying only order. The frozen prediction requires all four ordered distances to beat their shuffle median with one-sided \\(p\\le0.05\\).\n
\n
Protocol SHA-256: `EE14829EEA0D2BAAE05C37FAE2AA558F015EFC649FBFA54F0A563A7CE277DF9D`.\n
"""
        ),
        code(
            """from pathlib import Path
import json
import pandas as pd

from pn1_sieve_rung_test import run_analysis

HERE = Path.cwd()
results = run_analysis(HERE)
print("\\nReproduced summary:")
print(json.dumps(results["summary"], indent=2))
"""
        ),
        markdown("""## Held-out primary result\n
\n
Smaller Jensen–Shannon divergence means the parent representation transfers more faithfully to the child. The comparison below is the pre-registered ordered parent against the median of the matched, order-destroyed null.\n
"""),
        code(
            """primary = pd.read_csv(HERE / "PN1_PRIMARY_DISTANCES.csv")
primary["null_to_ordered_ratio"] = primary["shuffle_median_jsd_bits"] / primary["ordered_jsd_bits"]
columns = [
    "transition", "observable", "bins", "ordered_jsd_bits",
    "shuffle_median_jsd_bits", "null_to_ordered_ratio",
    "permutation_p_one_sided", "passes_frozen_primary",
]
print(primary[columns].to_string(index=False, float_format=lambda value: f"{value:.6f}"))
"""
        ),
        markdown(
            """![PN1 ordered versus shuffled result](PN1_SIEVE_RUNG_FIGURE.png)\n
\n
The ordered-to-child distance is about **23–37 times smaller** than the shuffled-parent median. The later held-out rung is not weaker; its contrast is larger. The two transitions are sequential, however, so this is robustness across two rungs rather than two independent replications.\n
"""
        ),
        markdown("""## Exact calibration and robustness\n
\n
The exact checks verify the implementation and the full-state sieve ceiling: release fraction \\(1/q\\), survivor/shed disjointness and reconstruction, child equality, modular phase, and zero information about which lifted copy is released from geometry alone. They are reconstruction, not new evidence.\n
"""),
        code(
            """calibration = pd.read_csv(HERE / "PN1_CALIBRATION_CHECKS.csv")
calibration_columns = [
    "transition", "release_fraction_measured", "release_fraction_exact",
    "reconstructs_lifted_parent", "survivors_match_child", "phase_rule_exact",
    "geometry_mutual_information_bits", "all_exact_checks_pass",
]
print(calibration[calibration_columns].to_string(index=False))

split_halves = pd.read_csv(HERE / "PN1_SPLIT_HALF_CHECKS.csv")
sensitivity = pd.read_csv(HERE / "PN1_BIN_SENSITIVITY.csv")
print(f"\\nSplit-half checks passing: {split_halves['passes_same_direction'].sum()}/{len(split_halves)}")
print(f"Bin-sensitivity checks in the same direction: {sensitivity['ordered_beats_shuffle_median'].sum()}/{len(sensitivity)}")
"""
        ),
        markdown(
            """## Interpretation, limitations and next test\n
\n
The supported claim is precise: **local cyclic relation carries across these nested primorial sieve rungs, and the bounded 0–2 coordinate preserves enough of that relation to distinguish the real parent from a full-marginal order shuffle.** The result demonstrates that flattening the wheel to its gap inventory loses substantial structure.\n
\n
It does not show that the ARA coordinate is uniquely superior. The conventional coordinate \\(r=\\log(g_{i+1}/g_i)\\) is related by a one-to-one transform, \\(x=2/(1+e^{-r})\\), and produced exactly the same pair-histogram divergence in the frozen bin mapping. Nor does this deterministic finite test support RH, phi, a universal leak constant, or a physical claim.\n
\n
The clean next step is a separately frozen **compression competition**: compare parameter-matched ARA, ordinary Markov, moments, run-length/constellation, and learned categorical summaries on later unseen sieve rungs. PN2 residue races and PN3 prime/zero representations remain separate parked branches.\n
"""
        ),
        markdown(
            """## Provenance\n
\n
- Frozen protocol: `PN1_SIEVE_RUNG_PROTOCOL_v1_FROZEN.md`\n
- Analysis: `pn1_sieve_rung_test.py`\n
- Independent audit: `pn1_validate_outputs.py` and `PN1_VALIDATION.json`\n
- Canonical result: `PN1_SIEVE_RUNG_RESULTS.json`\n
- Test ID: `T227 / PN1/v1`\n
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

    structural_checks = {
        "nbformat_is_4": notebook["nbformat"] == 4,
        "first_cell_is_markdown_title": cells[0]["cell_type"] == "markdown"
        and "".join(cells[0]["source"]).startswith("# "),
        "all_code_cells_have_execution_count": all(
            cell["execution_count"] is not None for cell in cells if cell["cell_type"] == "code"
        ),
        "no_code_cell_errors": not execution["errors"],
        "all_code_cells_executed": execution["all_code_cells_executed"],
    }
    validation = {
        "notebook": NOTEBOOK_PATH.name,
        "execution": execution,
        "structural_checks": structural_checks,
        "all_checks_pass": all(structural_checks.values()),
    }
    VALIDATION_PATH.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build and execute the PN1E reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN1E_THIRD_MEMORY_EFFECTIVENESS_REPRODUCIBILITY.ipynb"
VALIDATION = HERE / "PN1E_NOTEBOOK_EXECUTION_VALIDATION.json"


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


def execute(cells: list[dict[str, object]]) -> dict[str, object]:
    namespace: dict[str, object] = {"__name__": "__pn1e_notebook__"}
    original_cwd = Path.cwd()
    executed = 0
    errors: list[str] = []
    try:
        os.chdir(HERE)
        for cell_index, cell in enumerate(cells):
            if cell["cell_type"] != "code":
                continue
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exec(
                        compile("".join(cell["source"]), f"PN1E-cell-{cell_index + 1}", "exec"),
                        namespace,
                        namespace,
                    )
                executed += 1
                cell["execution_count"] = executed
                captured = stdout.getvalue()
                if captured:
                    cell["outputs"] = [{"name": "stdout", "output_type": "stream", "text": captured.splitlines(keepends=True)}]
            except Exception as exc:
                errors.append(f"cell {cell_index + 1}: {type(exc).__name__}: {exc}")
                raise
    finally:
        os.chdir(original_cwd)
    code_cells = sum(cell["cell_type"] == "code" for cell in cells)
    return {
        "all_code_cells_executed": executed == code_cells,
        "executed_code_cells": executed,
        "total_code_cells": code_cells,
        "errors": errors,
    }


def main() -> None:
    cells = [
        markdown(
            """# PN1E: practical effectiveness of the informative third

## TL;DR

On prime-23 development data, using two prior ARA readings instead of one reduces held-out next-reading cross-entropy by `0.4742` bits, or `18.55%`. Exact-bin accuracy rises from `31.70%` to `41.71%`, and top-three accuracy from `69.46%` to `83.90%`.

An exact first-order raw-gap Markov projection produces `0.2738` bits of the `0.4742`-bit gross effect. The remaining `0.20048` bits are ordered structure beyond that control. This is a strong practical development result, not proof of exactly three waves. Prime 29 remains unopened.
"""
        ),
        markdown(
            r"""## 1. Context and frozen method

For consecutive prime-wheel gaps,

\[x_i=\frac{2g_{i+1}}{g_i+g_{i+1}}\in(0,2).\]

The primary task predicts the next of 12 equal ARA bins. `ARA-Markov-1` uses the current ARA bin; `ARA-Markov-2` uses the previous and current bins. Models are trained on one consecutive half of the prime-23 cycle and scored on the other, then reversed.

Protocol SHA-256: `484B45190DCDC3823CDF6B2F644FCC87FCD925DA22B45321D2C334E56B8C77EB`.
"""
        ),
        markdown("""## 2. Reproduce the primary analysis

This reconstructs all 36,495,360 circular prime-23 gaps, runs both cross-fit directions at 8, 12 and 16 bins, computes exact control entropies and contribution tables, and rewrites the canonical machine outputs.
"""),
        code(
            """import json
from pathlib import Path
import pandas as pd

import pn1e_third_memory_effectiveness as primary

HERE = Path.cwd()
primary.main()
results = json.loads((HERE / "PN1E_RESULTS.json").read_text(encoding="utf-8"))
print("\\nPrimary classification:", results["primary_effectiveness"]["classification"])
print("Prime 29 opened:", results["data"]["prime29_opened"])
"""
        ),
        markdown("""## 3. Held-out predictive effectiveness

All metrics operate on the same next-ARA-reading task. Lower cross-entropy, perplexity and Brier score are better; higher top-one and top-three accuracy are better.
"""),
        code(
            """scores = pd.read_csv(HERE / "PN1E_EFFECTIVENESS_SCORES.csv")
primary_scores = scores[(scores["bins"] == 12) & (scores["direction"] == "mean")]
print(primary_scores.to_string(index=False, float_format=lambda value: f"{value:.9f}"))

m1 = primary_scores.loc[primary_scores["model"] == "ARA-Markov-1"].iloc[0]
m2 = primary_scores.loc[primary_scores["model"] == "ARA-Markov-2"].iloc[0]
print(f"\\nCross-entropy gain: {m1['cross_entropy_bits_per_reading'] - m2['cross_entropy_bits_per_reading']:.9f} bits/read")
print(f"Relative uncertainty reduction: {(1 - m2['cross_entropy_bits_per_reading'] / m1['cross_entropy_bits_per_reading']):.4%}")
print(f"Exact-bin improvement: {(m2['top1_accuracy'] - m1['top1_accuracy']):.4%} points")
print(f"Top-three improvement: {(m2['top3_accuracy'] - m1['top3_accuracy']):.4%} points")
"""
        ),
        markdown("""![PN1E practical-effect diagnostics](PN1E_EFFECTIVENESS_DIAGNOSTIC.png)

The two-memory model wins in both held-out directions and at every predeclared resolution.
"""),
        markdown("""## 4. Relational scale of the controls

The raw-gap Markov control is not the one-memory ARA predictor. It is a hypothetical raw-gap generator that retains only immediate `current gap -> next gap` tendencies, then projects those sequences onto the same three-reading, 12-bin ARA task.
"""),
        code(
            """scale = pd.read_csv(HERE / "PN1E_ENTROPY_SCALE.csv")
print(scale.to_string(index=False, float_format=lambda value: f"{value:.9f}"))

empirical = scale.loc[scale["model"] == "Empirical p23"].iloc[0]
control = scale.loc[scale["model"] == "First-order gap Markov"].iloc[0]
excess = empirical["memory_gain_bits"] - control["memory_gain_bits"]
print(f"\\nExcess above raw-gap Markov control: {excess:.9f} bits/read")
print(f"Fraction of gross gain above control: {excess / empirical['memory_gain_bits']:.4%}")
"""
        ),
        markdown("""## 5. Attribution

The third-reading benefit is distributed across a nonlinear web. The top five ARA contexts account for only `22.53%` of total conditional information and the top twenty for `57.83%`.
"""),
        code(
            """contexts = pd.read_csv(HERE / "PN1E_CONTEXT_ATTRIBUTION.csv")
raw_top = pd.read_csv(HERE / "PN1E_TOP30_GAP_QUADRUPLES.csv")
print("Top ten ARA contexts:")
print(contexts.head(10).to_string(index=False, float_format=lambda value: f"{value:.9f}"))
print("\\nTop ten raw four-gap constellations:")
print(raw_top.head(10).to_string(index=False, float_format=lambda value: f"{value:.9f}"))
"""
        ),
        markdown("""## 6. Independent validation

The standalone validator independently reconstructs the gap cycle, relation encoding, cross-fit scores, entropy controls and contribution sums. It does not import the primary PN1E module.
"""),
        code(
            """import pn1e_independent_validator as validator

validator.main()
audit = json.loads((HERE / "PN1E_INDEPENDENT_VALIDATION.json").read_text(encoding="utf-8"))
print("\\nAll independent checks pass:", audit["all_checks_pass"])
print("Maximum primary-score absolute error:", audit["maximum_primary_score_absolute_error"])
"""
        ),
        markdown("""## 7. Takeaways

The informative third is operationally useful: arrival path materially improves prediction of the next ARA position. About `57.7%` of the gross information gain is reproduced by a first-order raw-gap transition world, while `42.3%` remains above that control.

The next development branch should decompose the full two-reading state into direction, distance and raw child identity before freezing a transfer model for unopened prime 29.

## Provenance

- Protocol: `PN1E_THIRD_MEMORY_EFFECTIVENESS_PROTOCOL.md`
- Primary analysis: `pn1e_third_memory_effectiveness.py`
- Independent audit: `pn1e_independent_validator.py`
- Full report: `PN1E_THIRD_MEMORY_EFFECTIVENESS_REPORT.md`
"""),
    ]

    execution = execute(cells)
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    result = {
        **execution,
        "notebook": NOTEBOOK.name,
        "notebook_exists": NOTEBOOK.exists(),
        "notebook_bytes": NOTEBOOK.stat().st_size,
    }
    VALIDATION.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

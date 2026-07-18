#!/usr/bin/env python3
"""Build and execute the PN1D reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN1D_THIRD_COMPONENT_REPRODUCIBILITY.ipynb"
VALIDATION = HERE / "PN1D_NOTEBOOK_EXECUTION_VALIDATION.json"


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
    namespace: dict[str, object] = {"__name__": "__pn1d_notebook__"}
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
                        compile("".join(cell["source"]), f"PN1D-cell-{cell_index + 1}", "exec"),
                        namespace,
                        namespace,
                    )
                executed += 1
                cell["execution_count"] = executed
                captured = stdout.getvalue()
                if captured:
                    cell["outputs"] = [
                        {
                            "name": "stdout",
                            "output_type": "stream",
                            "text": captured.splitlines(keepends=True),
                        }
                    ]
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
            """# PN1D: is there evidence of a third component?

## TL;DR

Yes, in a narrow development-data sense. A rank-3 nonnegative description cross-predicts the other half of the prime-23 relation plane much better than rank 2, and three successive ARA readings retain `0.200480` bits of conditional dependence beyond an exact first-order Markov gap projection.

The result is **not** evidence of exactly three waves: ranks 4 and 5 also improve. It establishes at least a stable third representational component and third-step structure. Prime 29 remains unopened.
"""
        ),
        markdown(
            r"""## 1. Frozen development protocol

The local coordinate is

\[x_i=\frac{2g_{i+1}}{g_i+g_{i+1}}\in(0,2).\]

The spatial test cross-fits nonnegative ranks 1 through 6 between the two halves of the complete prime-23 relation plane. The sequential test evaluates (I(X_i;X_{i+2}\mid X_{i+1})) against exact IID-gap and first-order Markov-gap projections. Scale strata test whether three components merely reproduce three local span bands.

Protocol SHA-256: `9D6F2EFC3774B84F04AFBCCEBD0782F3B02F62A53A783712408112F5642A60DF`.
"""
        ),
        markdown(
            """## 2. Reproduce the primary analysis

This reconstructs all 36,495,360 circular prime-23 gaps, fits every declared NMF rank, recomputes the information controls and rewrites the canonical machine outputs.
"""
        ),
        code(
            """import json
from pathlib import Path
import pandas as pd

import pn1d_third_component_development as primary

HERE = Path.cwd()
primary.main()
results = json.loads((HERE / "PN1D_RESULTS.json").read_text(encoding="utf-8"))
print("\\nPrimary classification:", results["plane_mode"]["classification"])
print("Prime 29 opened:", results["prime29_opened"])
"""
        ),
        markdown("""## 3. Spatial cross-fit

Lower Jensen-Shannon divergence is better. Stability is assessed by matching separately fitted nonnegative components across the two halves.
"""),
        code(
            """nmf = pd.read_csv(HERE / "PN1D_NMF_CROSSFIT.csv")
print(nmf.to_string(index=False, float_format=lambda value: f"{value:.9f}"))

r2 = nmf.loc[nmf["rank"] == 2].iloc[0]
r3 = nmf.loc[nmf["rank"] == 3].iloc[0]
print(f"\\nRank 2 -> 3 held-out gain: {r2['mean_heldout_jsd_bits'] - r3['mean_heldout_jsd_bits']:.9f} bits")
print(f"Rank-3 minimum component cosine: {r3['min_component_cosine']:.9f}")
"""
        ),
        markdown(
            """![PN1D third-component diagnostics](PN1D_THIRD_COMPONENT_DIAGNOSTIC.png)

Rank 3 is stable and materially better than rank 2. Continued gains at ranks 4 and 5 mean the plane is a multimode web rather than an exactly three-mode object.
"""
        ),
        markdown("""## 4. Third-step dependence

The IID projection controls for dependence manufactured by consecutive ratios sharing a gap. The Markov projection additionally preserves observed one-step gap transitions.
"""),
        code(
            """third = pd.read_csv(HERE / "PN1D_THIRD_STEP_MODELS.csv")
print(third.to_string(index=False, float_format=lambda value: f"{value:.9f}"))
summary = results["third_step"]
print(f"\\nExcess over IID overlap: {summary['empirical_excess_over_iid_bits']:.9f} bits")
print(f"Excess over first-order Markov overlap: {summary['empirical_excess_over_markov_bits']:.9f} bits")
"""
        ),
        markdown("""## 5. Scale-stratum check

Three local span bands do not explain the three NMF components cleanly; their best component-to-stratum cosine similarities are low.
"""),
        code(
            """scale = pd.read_csv(HERE / "PN1D_SCALE_STRATA.csv")
print(scale.to_string(index=False, float_format=lambda value: f"{value:.9f}"))
print("\\nMean component-to-scale cosine:", f"{results['scale_strata']['mean_rank3_to_scale_cosine']:.9f}")
"""
        ),
        markdown("""## 6. Independent reconstruction

The audit uses standalone residue and child-gap construction, independently recreates every saved tensor and stratum, then uses held-out truncated SVD as a methodologically different spatial cross-check.
"""),
        code(
            """import pn1d_independent_validator as validator

validator.main()
audit = json.loads((HERE / "PN1D_INDEPENDENT_VALIDATION.json").read_text(encoding="utf-8"))
print("\\nAll independent checks pass:", audit["all_checks_pass"])
print(json.dumps(audit["independent_svd"], indent=2))
"""
        ),
        markdown(
            """## 7. Conclusion

Prime-23 development data support **at least one stable component beyond a two-component description** and **dependence extending beyond a first-order pair model**. In ARA language, the visible pair plus its handover carries an informative third, but this analysis does not decide whether that third is an independent wave, a relation generated by two waves, or one layer of a richer recursive web.

The next confirmatory model must distinguish rank 2, rank 3 and richer-web alternatives, include an honest complexity penalty, and be frozen before prime 29 is opened.

## Provenance

- Protocol: `PN1D_THIRD_COMPONENT_DEVELOPMENT_PROTOCOL.md`
- Primary analysis: `pn1d_third_component_development.py`
- Independent audit: `pn1d_independent_validator.py`
- Full report: `PN1D_THIRD_COMPONENT_DEVELOPMENT_REPORT.md`
"""
        ),
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

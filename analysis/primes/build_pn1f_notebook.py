#!/usr/bin/env python3
"""Build and execute the PN1F bidirectional-landscape notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN1F_BIDIRECTIONAL_LANDSCAPE_REPRODUCIBILITY.ipynb"
VALIDATION = HERE / "PN1F_NOTEBOOK_EXECUTION_VALIDATION.json"


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
    namespace: dict[str, object] = {"__name__": "__pn1f_notebook__"}
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
                        compile("".join(cell["source"]), f"PN1F-cell-{cell_index + 1}", "exec"),
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
            """# PN1F: bidirectional prime-wheel landscape

## tl;dr

Across the opened core sieve rungs `11 -> 13 -> 17 -> 19 -> 23`, the non-Markov part of the ARA relation plane retains nearly the same shape while contracting. Consecutive residual-shape cosines rise from `0.9892` to `0.9981`; consecutive signed deformation fields have cosines `0.9794`, `0.9905`, and `0.9924`; one deformation mode contains `98.01%` of 12-bin deformation energy (`99.05%` at 24 bins). This is a coherent one-direction parent-scale progression, not yet a completed wave.

Drilling down inside the already-open prime-23 wheel shows that arrival direction recovers `0.1031` bits/read, arrival distance `0.2025`, their compressed signed interaction `0.2818`, and the full previous/current ARA pair `0.4742`. The exact shared raw gap recovers `0.8187`, showing that substantial child identity is flattened by the position-only projection.

Prime 29 remains unopened. These are development maps to be oriented before a transferable next-rung prediction is frozen.
"""
        ),
        markdown(
            r"""## Context & Methods

### Question

Does a larger relational pattern appear across opened primorial sieve rungs, and which child/path variables explain the extra memory inside the prime-23 slice?

### Shared coordinate

For circular gaps,

\[x_i=\frac{2g_{i+1}}{g_i+g_{i+1}},\qquad Z_i=(x_i,x_{i+1}).\]

The upward map compares the exact ordered plane with projections generated from the same rung's independent-gap marginal and first-order raw-gap transition matrix. Its signed parent-scale field is the change in `ordered - Gap-Markov-1` residual between rungs.

The downward map uses eight guarded contiguous folds on prime 23 and compares current position, direction, distance, signed step, shared raw-gap identity, full previous/current position, and a raw-gap Markov predictor.

### Key assumptions and fences

- Rung order is a static scale coordinate, not physical time.
- Statistical modes retain neutral names until Dylan supplies ARA orientation.
- The ordinary log-ratio is an exact coordinate rival.
- Four core transitions cannot establish periodicity.
- Protocol SHA-256: `4ABCCB50E62780E41D9FF48455C1DC413926B9E5E527654E2B4F7108CAF004D7`.
- Prime 29 is a protected unopened target.
"""
        ),
        markdown(
            """## Data

All data are exact reduced-residue wheels generated locally. Context rungs end at 5, 7, 11, 13, 17, 19, and 23. The comparable 12×12 upward core is 11 through 23; 24×24 sensitivity uses 13 through 23. Prime 23 contains 36,495,360 circular gaps and must reproduce the PN1C/PN1D hash.
"""
        ),
        markdown("""## Results

### 1. Reproduce the complete analysis

This cell rebuilds every opened wheel through 23, rewrites the machine artifacts, and leaves the protected next prime untouched.
"""),
        code(
            """import json
from pathlib import Path
import pandas as pd

import pn1f_bidirectional_landscape as primary

HERE = Path.cwd()
primary.main()
results = json.loads((HERE / "PN1F_RESULTS.json").read_text(encoding="utf-8"))
print("\\nMaximum generated prime:", results["maximum_generated_prime"])
print("Prime 29 opened:", results["prime29_opened"])
print("Status:", results["status"])
"""
        ),
        markdown("""### 2. Upward cross-rung landscape

The ordered relation plane retains visible structure beyond an ordinary first-order raw-gap process. The residual shape persists while its magnitude contracts.
"""),
        code(
            """rungs = pd.read_csv(HERE / "PN1F_RUNG_METRICS.csv")
transitions = pd.read_csv(HERE / "PN1F_TRANSITION_METRICS.csv")
modes = pd.read_csv(HERE / "PN1F_DEFORMATION_MODE_SCORES.csv")

print("Core rung metrics:")
print(rungs[rungs["rung_prime"].isin([11,13,17,19,23])][[
    "rung_prime", "slot_count", "ordered_adjacent_mi_bits",
    "ordered_vs_gap_iid_jsd_bits", "ordered_vs_gap_markov1_jsd_bits",
    "markov_residual_l2", "mean_absolute_child_step",
    "rising_share", "equal_share", "falling_share"
]].to_string(index=False, float_format=lambda value: f"{value:.9f}"))

print("\\nTransition geometry:")
print(transitions.to_string(index=False, float_format=lambda value: f"{value:.9f}"))

mode_energy = modes.drop_duplicates("mode")[["mode", "energy_fraction"]]
print("\\nDeformation energy by mode:")
print(mode_energy.to_string(index=False, float_format=lambda value: f"{value:.9f}"))
"""
        ),
        markdown("""![PN1F upward landscape](PN1F_UPWARD_LANDSCAPE.png)

The top row is the ordered relation plane. The middle row subtracts the fitted first-order raw-gap projection. The bottom-right panel shows neutral signed coordinates of the change between rungs; its leading score keeps one sign while declining in magnitude.
"""),
        markdown("""### 3. Downward path decomposition

Each model predicts the same next 12-bin ARA reading. Lower cross-entropy is better. Gains are measured relative to using the current ARA position alone.
"""),
        code(
            """down = pd.read_csv(HERE / "PN1F_DOWNWARD_MODEL_SUMMARY.csv")
print(down.to_string(index=False, float_format=lambda value: f"{value:.9f}"))

base = down.set_index("model").loc["current_B", "mean_cross_entropy_bits"]
print(f"\\nCurrent-position uncertainty: {base:.9f} bits/read")
for name in ["B_plus_direction", "B_plus_distance", "B_plus_signed_step", "full_A_B", "raw_gap_markov1", "B_plus_shared_gap"]:
    row = down.set_index("model").loc[name]
    print(f"{name}: {row['gain_vs_current_B_bits']:+.9f} bits/read; {row['mean_active_context_rows']:.0f} active rows")
"""
        ),
        markdown("""![PN1F downward decomposition](PN1F_DOWNWARD_DECOMPOSITION.png)

Direction and distance each carry real information, and their signed combination recovers more than either alone. The exact shared raw gap outperforms both the compressed path and full two-position ARA history, locating important child identity below the projection.
"""),
        markdown("""### 4. Independent validation

The independent validator does not import the primary implementation. It checks the source prime ceiling, saved probability identities, SVD reconstruction, cross-rung cosines, fold summaries, PN1E reconciliation, figure dimensions, and 24-bin sensitivity.
"""),
        code(
            """import pn1f_validate_outputs as validator

validator.main()
validation = json.loads((HERE / "PN1F_VALIDATION.json").read_text(encoding="utf-8"))
print("\\nAll checks pass:", validation["all_checks_pass"])
print("24-bin residual cosines:", validation["recomputed"]["adjacent_residual_cosines_24"])
print("24-bin deformation energy:", validation["recomputed"]["deformation_energy_fractions_24"])
"""
        ),
        markdown(
            """## Takeaways

1. **Upward:** the opened rungs expose a strongly persistent residual shape with contracting amplitude and almost collinear deformation. This is compatible with observing one branch of a larger parent-scale ARA progression, but there is no observed turn, flip, or return yet.
2. **Downward:** the arrival path is genuinely informative, with distance contributing more than direction and their signed interaction contributing more than either separately.
3. **Child identity:** the shared raw gap contains substantially more predictive information than the full two-position ARA history. The 0–2 projection is therefore useful but visibly lossy at this grain.
4. **Next scientific action:** Dylan must orient the neutral upward maps. Then a low-parameter cross-rung amplitude/shape rule and a selected downward state representation can be frozen before prime 29 is generated.

## Provenance

- Protocol: `PN1F_BIDIRECTIONAL_LANDSCAPE_DEVELOPMENT_PROTOCOL.md`
- Primary implementation: `pn1f_bidirectional_landscape.py`
- Independent validator: `pn1f_validate_outputs.py`
- Machine result: `PN1F_RESULTS.json`
- Full written report: `PN1F_BIDIRECTIONAL_LANDSCAPE_REPORT.md`
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
        "maximum_generated_prime": 23,
        "prime29_opened": False,
    }
    VALIDATION.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

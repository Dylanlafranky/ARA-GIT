#!/usr/bin/env python3
"""Build and execute the PN1G saved-inventory reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN1G_PRIME29_TRANSFER_REPRODUCIBILITY.ipynb"
VALIDATION = HERE / "PN1G_NOTEBOOK_EXECUTION_VALIDATION.json"


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
    namespace: dict[str, object] = {"__name__": "__pn1g_notebook__"}
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
                        compile("".join(cell["source"]), f"PN1G-cell-{cell_index + 1}", "exec"),
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
            """# PN1G: prime-29 frozen transfer

## tl;dr

Prime 29 was unopened when protocol `PN1G/TRANSFER/v1` was frozen. All six registered checks passed. The prime-29 residual inherited the prime-23 shape at cosine `0.999006`, contracted from L2 `0.050042` to `0.046090`, and continued the preceding deformation direction at cosine `0.995225`. The leading cross-rung deformation mode retained `97.66%` of energy. The complete seven-model downward ordering also transferred exactly with Kendall `tau=1.0`, and every non-base representation gained in all eight folds.

This notebook replays the saved exact aggregate inventories and independent validator. The exhaustive billion-slot stream is intentionally not rerun inside the notebook; its deterministic command is shown below and was executed twice with identical results.
"""
        ),
        markdown(
            r"""## Context & Methods

For circular gaps,

\[x_i=\frac{2g_{i+1}}{g_i+g_{i+1}},\qquad Z_i=(x_i,x_{i+1}).\]

The ordered relation plane is compared with exact Gap-IID and first-order raw-gap Markov projections. The frozen transfer tests the shape, amplitude and direction of `ordered - Gap-Markov-1`, then repeats the prime-23 downward decomposition on prime 29.

### Key assumptions and fences

- Protocol SHA-256: `FC568F2D1913F163A81146A089F0D1F42981F7E9EFB5FAFBA5C097D92387732B`.
- Prime 29 was untouched at declaration and is now open development data.
- Statistical orientation remains neutral; Dylan controls ARA phase naming.
- A successful wheel transfer is not evidence for RH, prime prediction, physical waves or universal ARA geometry.
- Full deterministic generation command: `python pn1g_prime29_transfer.py`.
"""
        ),
        markdown("""## Data

The prime-29 reduced-residue wheel has period `6,469,693,230` and `1,021,870,080` circular gaps. The primary implementation streamed it from the exact prime-23 residues without storing the target cycle. `PN1G_PRIME29_COUNTS_AND_MATRICES.npz` retains sufficient aggregate counts for an independent replay of every registered calculation.
"""),
        markdown("""## Results

### 1. Load the frozen result and audit packet
"""),
        code(
            """import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path.cwd()
result = json.loads((HERE / "PN1G_RESULTS.json").read_text(encoding="utf-8"))
arrays = np.load(HERE / "PN1G_PRIME29_COUNTS_AND_MATRICES.npz")
print("Status:", result["status"])
print("Protocol:", result["protocol_sha256"])
print("Target slots:", f'{result["target_metrics"]["slot_count"]:,}')
print("Frozen checks:", result["frozen_check_pass_count"], "/", result["frozen_check_total"])
print("Saved audit arrays:", len(arrays.files))
"""
        ),
        markdown("""### 2. Recompute the four upward verdicts from saved matrices

This cell does not read the stored pass/fail booleans. It derives the cosines, contraction and singular-value energy directly from the saved p23 and p29 fields.
"""),
        code(
            """pn1f = np.load(HERE / "PN1F_BIDIRECTIONAL_MATRICES.npz")
p23_index = int(np.where(pn1f["core_primes"] == 23)[0][0])
p23_residual = pn1f["markov_residual_12"][p23_index]
p29_residual = arrays["residual_12"]
new_deformation = p29_residual - p23_residual
previous_deformation = pn1f["deformation_12"][-1]

def cosine(a, b):
    return float(np.sum(a*b) / (np.linalg.norm(a)*np.linalg.norm(b)))

stack = np.concatenate((pn1f["deformation_12"], new_deformation[None]), axis=0)
singular = np.linalg.svd(stack.reshape(len(stack), -1), compute_uv=False)
energy = singular**2 / np.sum(singular**2)

metrics = {
    "residual cosine": cosine(p23_residual, p29_residual),
    "p23 residual L2": float(np.linalg.norm(p23_residual)),
    "p29 residual L2": float(np.linalg.norm(p29_residual)),
    "deformation cosine": cosine(previous_deformation, new_deformation),
    "leading mode energy": float(energy[0]),
}
for name, value in metrics.items():
    print(f"{name}: {value:.12f}")
assert metrics["residual cosine"] >= 0.98
assert 0 < metrics["p29 residual L2"] < metrics["p23 residual L2"]
assert metrics["deformation cosine"] >= 0.98
assert metrics["leading mode energy"] >= 0.95
"""
        ),
        markdown("""![Prime-29 transfer](PN1G_PRIME29_TRANSFER_FIGURE.png)

The first two panels use the same signed scale. The third is the new deformation. The bar chart shows the frozen downward comparison; lower cross-entropy is better.
"""),
        markdown("""### 3. Verify the transferred downward hierarchy
"""),
        code(
            """down = pd.read_csv(HERE / "PN1G_DOWNWARD_MODEL_SUMMARY.csv").sort_values("mean_cross_entropy_bits")
expected = [
    "B_plus_shared_gap", "raw_gap_markov1", "full_A_B",
    "B_plus_signed_step", "B_plus_distance", "B_plus_direction", "current_B"
]
print(down[["model", "mean_cross_entropy_bits", "gain_vs_current_B_bits", "min_fold_gain_vs_current_B_bits", "mean_active_conditional_df"]].to_string(index=False, float_format=lambda x: f"{x:.9f}"))
actual = down.model.tolist()
print("\\nExact frozen order:", actual == expected)
assert actual == expected
assert np.all(down[down.model != "current_B"].min_fold_gain_vs_current_B_bits > 0)
"""
        ),
        markdown("""### 4. Run the independently coded replay

The validator reconstructs projected controls, residuals, SVD energy, fold models and complexity from saved counts rather than trusting `PN1G_RESULTS.json`.
"""),
        code(
            """import pn1g_independent_validator as validator

validator.main()
validation = json.loads((HERE / "PN1G_INDEPENDENT_VALIDATION.json").read_text(encoding="utf-8"))
print("\\nIndependent validation:", validation["overall"])
print("Checks:", validation["passed_check_count"], "/", validation["check_count"])
assert validation["overall"] == "PASS"
"""
        ),
        markdown("""## Takeaways

1. The previously observed neutral parent-scale shape and signed direction transferred prospectively to prime 29.
2. The downward child-information hierarchy transferred exactly: precise child identity remains more informative than bounded position history.
3. The result strengthens a narrow ARA claim about stable relation geometry and recursive decompression in this nested arithmetic hierarchy.
4. The trajectory still looks like a contracting branch or convergence path; no wave reversal, flip or return has been observed.
5. The raw-gap models remain stronger than compressed ARA position and are mandatory controls.

## Provenance

- Frozen protocol: `PN1G_PRIME29_TRANSFER_PROTOCOL_v1_FROZEN.md`
- Stream implementation: `pn1g_prime29_transfer.py`
- Independent validator: `pn1g_independent_validator.py`
- Full report: `PN1G_PRIME29_TRANSFER_REPORT.md`
- Machine result: `PN1G_RESULTS.json`
- Saved inventories: `PN1G_PRIME29_COUNTS_AND_MATRICES.npz`
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
    outcome = {
        **execution,
        "notebook": NOTEBOOK.name,
        "notebook_exists": NOTEBOOK.exists(),
        "notebook_bytes": NOTEBOOK.stat().st_size,
        "target_prime": 29,
        "prime29_opened": True,
        "stream_reexecuted_inside_notebook": False,
        "saved_inventory_replay": True,
        "independent_validation": "PASS",
    }
    VALIDATION.write_text(json.dumps(outcome, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(outcome, indent=2))


if __name__ == "__main__":
    main()

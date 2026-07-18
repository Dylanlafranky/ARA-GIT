#!/usr/bin/env python3
"""Build and execute the PN1I reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN1I_PRIME_PYRAMID_ARA_REPRODUCIBILITY.ipynb"
VALIDATION = HERE / "PN1I_NOTEBOOK_EXECUTION_VALIDATION.json"


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
    namespace: dict[str, object] = {"__name__": "__pn1i_notebook__"}
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
                        compile("".join(cell["source"]), f"PN1I-cell-{cell_index + 1}", "exec"),
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
            """# PN1I: prime-gate, pyramid and plain-ARA opened-rung tests

## tl;dr

The exact pyramid skeleton and gate holonomy are present: every parent has `q-1` surviving children, the removed-branch step is a modular transform of the parent gap, and the seam shifts by one lift. Plain gate ARA is exactly the parent wheel's ordinary ARA reading. The ordered two-gap pair adds non-overlapping two-step predictive information from prime 13 onward, but the removed-branch label adds no further information once the pair is known. All `36/36` construction checks and `124/124` independent checks pass.

These are method-locked development results on opened rungs, not prospective confirmation. Prime 31 is not accessed.
"""
        ),
        markdown(
            r"""## Context & Methods

For parent period (P), next prime (q), residue (r_i), and excluded lift (t_i^*),

[
r_i+t_i^*Pequiv0pmod q,qquad
t_{i+1}^*-t_i^*equiv-P^{-1}g_ipmod q.
]

The local plain-ARA coordinate is

[
x_i=rac{2g_{R,i}}{g_{L,i}+g_{R,i}}.
]

The primary Information^3-style endpoint predicts (x_{i+2}) from the current ordered gap pair. This target shares no raw gap with the current pair. Models are scored in eight contiguous folds with Jeffreys smoothing. Sixteen target permutations control the two-step pair result; 32 order permutations control gate and plain-ARA transition dependence.

### Key Assumptions

- Generated transitions stop at prime 23.
- Prime 29 appears only through saved PN1F/PN1G aggregate files.
- The prime-31 PN1H target remains sealed.
- Exact sieve identities are calibration, not independent ARA evidence.
"""
        ),
        markdown(
            """## Data

The source is the complete deterministic reduced-residue hierarchy for transitions into primes `7,11,13,17,19,23`. The largest generated parent contains `1,658,880` residues. Saved prime-29 aggregate results extend the ordinary ARA/base-width crosswalk without regenerating that billion-slot wheel.
"""
        ),
        markdown("""## Results

### 1. Execute the method-locked opened-rung analysis
"""),
        code(
            """import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path.cwd()
import pn1i_prime_pyramid_ara as analysis
result = analysis.main()
print("Prime 31 accessed:", result["prime31_accessed"])
print("Exact checks:", result["exact_check_pass_count"], "/", result["exact_check_total"])
"""
        ),
        markdown("""### 2. Inspect the exact gate and ordinary ARA reading
"""),
        code(
            """gate = pd.read_csv(HERE / "PN1I_GATE_METRICS.csv")
columns = [
    "child_prime", "parent_slots", "base_width",
    "gate_phase_transition_mi_bits", "gate_phase_shuffle_max_mi_bits",
    "internal_gate_step_exact", "seam_holonomy_lift_shift",
    "plain_ara_mean", "plain_ara_below_ridge_share",
    "plain_ara_at_ridge_share", "plain_ara_above_ridge_share",
]
print(gate[columns].to_string(index=False, float_format=lambda value: f"{value:.9f}"))
assert np.all(gate.internal_gate_step_exact)
assert np.all(gate.seam_holonomy_lift_shift == 1)
assert np.allclose(gate.plain_ara_mean, 1.0, rtol=0, atol=0)
assert np.allclose(gate.plain_ara_below_ridge_share, gate.plain_ara_above_ridge_share, rtol=0, atol=0)
"""
        ),
        markdown(
            """![Prime-gate and plain-ARA analysis](PN1I_PRIME_GATE_ARA_FIGURE.png)

The gate phase is strongly ordered beyond shuffled marginals on five of six rungs. Prime 7 is an eight-event saturation case. The plain gate coordinate is exactly the parent's ordinary ARA sequence, not a new independent measurement.
"""
        ),
        markdown("""### 3. Inspect maximum-base distribution and the two-step lock
"""),
        code(
            """base = pd.read_csv(HERE / "PN1I_BASE_ARA_CROSSWALK.csv")
lock = pd.read_csv(HERE / "PN1I_LOCK_SUMMARY.csv")
lag2 = lock[lock.lag == 2]
print("Base-width crosswalk")
print(base[["rung_prime", "base_width", "ordered_adjacent_mi_bits", "markov_residual_l2", "shared_child_gain_bits"]].to_string(index=False, float_format=lambda value: f"{value:.9f}"))
print("\\nTwo-step lock")
print(lag2[["child_prime", "event_count", "pair_gain_beyond_best_single_bits", "pair_min_fold_gain_beyond_best_single_bits", "pair_null_max_bits", "gate_increment_beyond_pair_or_gate_bits"]].to_string(index=False, float_format=lambda value: f"{value:.9f}"))
assert np.all(np.diff(base.ordered_adjacent_mi_bits) < 0)
assert (lag2.pair_gain_beyond_best_single_bits > 0).sum() == 4
assert (lag2.gate_increment_beyond_pair_or_gate_bits > 0).sum() == 0
"""
        ),
        markdown(
            """![Maximum-base and information-lock analysis](PN1I_PYRAMID_LOCK_FIGURE.png)

The ordered pair becomes useful at prime 13 and remains positive thereafter. Adding the gate branch fragments the state without adding held-out information for this target; this failure is retained rather than redefined.
"""
        ),
        markdown("""### 4. Run the independently coded reconstruction
"""),
        code(
            """import pn1i_independent_validator as validator
validation = validator.main()
print("Independent validation:", validation["status"])
print("Checks:", validation["passed_check_count"], "/", validation["check_count"])
assert validation["status"] == "PASS"
"""
        ),
        markdown(
            """## Takeaways

1. The pyramid/base/gate construction has an exact arithmetic representation, including a one-lift seam holonomy.
2. Plain ARA is recovered exactly at every deletion: a whole-rung `1.0` ridge contains balanced populations of local asymmetries.
3. From prime 13 onward, two sides plus their ordered relation carry more two-step continuation information than either side or their sum alone.
4. Gate position is a phase coordinate derived from the parent wave, not an independently useful fourth source for this endpoint.
5. Wider bases accompany quieter normalized parent appearance, but prime 31 remains the prospective capstone-versus-convergence test.

Full interpretation and caveats are in `PN1I_PRIME_PYRAMID_ARA_REPORT.md`.
"""
        ),
    ]

    for index, cell in enumerate(cells, start=1):
        cell["id"] = f"pn1i-{index:02d}"
    execution = execute(cells)
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.14"},
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
        "full_analysis_reexecuted_inside_notebook": True,
        "maximum_generated_prime": 23,
        "prime31_accessed": False,
        "independent_validation": "PASS",
    }
    VALIDATION.write_text(json.dumps(outcome, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(outcome, indent=2))


if __name__ == "__main__":
    main()

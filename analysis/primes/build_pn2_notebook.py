#!/usr/bin/env python3
"""Build and execute the PN2 prime-survival reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN2_PRIME_SURVIVAL_BRIDGE_REPRODUCIBILITY.ipynb"
VALIDATION = HERE / "PN2_NOTEBOOK_EXECUTION_VALIDATION.json"


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
    namespace: dict[str, object] = {"__name__": "__pn2_notebook__"}
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
                        compile("".join(cell["source"]), f"PN2-cell-{cell_index + 1}", "exec"),
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
            """# PN2: fixed-budget prime-survival bridge

## tl;dr

ARA did **not** beat the established probabilistic baselines on the untouched `100,000,000-110,000,000` target. The primary Information^3 candidate model lost to the p29-conditioned prime-number-theorem baseline by `0.000160973` bits/candidate. The primary ARA edge model lost to the p29-conditioned Hardy-Littlewood baseline by `0.000036725` bits/edge. Both 95% block-bootstrap intervals are wholly negative. An independent reconstruction passed `476/476` checks.

The result establishes a useful boundary: ARA maps the deterministic primorial-wheel geometry, but the tested local ARA coordinates do not yet add prime-survival information beyond established analytic baselines.
"""
        ),
        markdown(
            r"""## Context & Methods

The predictor receives only candidates that survive sieving through prime 29. It must estimate which of those candidates are genuinely prime in a later, untouched interval. The p31 PN1H wheel target is not generated or inspected.

For a candidate at location (n), the analytic candidate baseline is

\[
p_{\mathrm{PNT29}}(n)=\frac{1}{\log n\prod_{q\leq29}(1-1/q)}.
\]

For an adjacent p29-wheel edge of gap (g), the pair baseline uses the corresponding conditional Hardy-Littlewood probability. Competing fitted models use raw local gaps, a four-gap stencil, plain ARA, an Information^3-style ARA stencil, and a decompressed ARA representation.

All models were fitted only on `[10,000,000,20,000,000)`. The primary bin count (`12`), shrinkage (`64`), endpoints, baselines and 40-block bootstrap were frozen before the target was opened. Lower log loss is better; reported deltas are `baseline loss - ARA loss`, so positive values favour ARA.
"""
        ),
        markdown(
            """## Data

- Development interval: `[10,000,000,20,000,000)`
- Untouched target: `[100,000,000,110,000,000)`
- Sieve budget: primes through `29`
- Target p29-wheel candidates: `1,579,479`
- Surviving primes: `541,854` (`34.3059%`)
- Adjacent candidate edges: `1,579,478`
- Edges with two prime endpoints: `184,913` (`11.7072%`)
"""
        ),
        markdown("""## Results

### 1. Rerun the frozen target analysis
"""),
        code(
            """import json
from pathlib import Path
import pandas as pd

HERE = Path.cwd()
import pn2_prime_survival_bridge as analysis
analysis.run_target()
results = json.loads((HERE / "PN2_RESULTS.json").read_text(encoding="utf-8"))
print("Status:", results["status"])
print("Prime-31 wheel accessed:", results["pn1h_p31_wheel_accessed"])
print("Candidate endpoint:", results["primary_candidate_endpoint"])
print("Edge endpoint:", results["primary_edge_endpoint"])
"""
        ),
        markdown(
            """![Primary model and block comparisons](PN2_SURVIVAL_MODEL_COMPARISON.png)

Both primary ARA deltas are negative in most target blocks, and both bootstrap intervals exclude zero in the direction favouring the analytic baseline.
"""
        ),
        markdown("""### 2. Inspect the primary scores and the small plain-ARA sensitivity
"""),
        code(
            """scores = pd.read_csv(HERE / "PN2_MODEL_SCORES.csv")
selected = [
    "candidate_pnt29", "raw_local_l64", "raw_stencil_l64",
    "ara_plain_b12_l64", "ara_i3_b12_l64", "ara_decompressed_b12_l64",
    "edge_hl29", "raw_edge_l64", "ara_edge_b12_l64",
    "ara_edge_decompressed_b12_l64",
]
view = scores[scores.model.isin(selected)][
    ["task", "model", "log_loss_bits", "gain_vs_analytic_bits", "calibration_error"]
].copy()
print(view.to_string(index=False, float_format=lambda value: f"{value:.12f}"))

plain = scores[(scores.task == "candidate") & scores.model.str.startswith("ara_plain_b") & scores.model.str.endswith("_l64")]
print("\\nPlain-ARA bin sensitivity")
print(plain[["model", "log_loss_bits", "gain_vs_analytic_bits"]].to_string(index=False, float_format=lambda value: f"{value:.12f}"))
assert (plain.gain_vs_analytic_bits > 0).sum() == 1
"""
        ),
        markdown(
            """The 12-bin plain ARA candidate model gains only `0.000000772` bits/candidate over PNT29, about `1.2` bits across the entire target. The same representation loses with 8, 16 and 24 bins, and the frozen Information^3 primary loses clearly. This isolated sensitivity is therefore not treated as support.
"""
        ),
        markdown("""### 3. Check gap-class frequency and location calibration
"""),
        code(
            """print("Gap-class summaries")
for model, metrics in results["gap_class_frequency"].items():
    if isinstance(metrics, dict):
        print(model, metrics)
print("\\nLocation summaries")
for model, metrics in results["location_calibration"].items():
    print(model, metrics)
"""
        ),
        markdown(
            """![Gap-class residuals](PN2_GAP_CLASS_RESIDUALS.png)

Hardy-Littlewood has the lowest gap-class Poisson deviance (`20.714`) and weighted absolute relative error (`0.7356%`). PNT29 also has the best 20-block location MAPE (`0.2088%`). The local fitted models track the broad pattern but do not improve it.
"""
        ),
        markdown("""### 4. Run the independent full-target reconstruction
"""),
        code(
            """import pn2_independent_validator as validator
validator.main()
validation = json.loads((HERE / "PN2_INDEPENDENT_VALIDATION.json").read_text(encoding="utf-8"))
print("Independent validation:", validation["status"])
print("Checks:", validation["passed_check_count"], "/", validation["check_count"])
assert validation["status"] == "PASS"
assert validation["passed_check_count"] == validation["check_count"] == 476
assert validation["pn1h_p31_wheel_accessed"] is False
"""
        ),
        markdown(
            """## Takeaways

1. This first direct prime-survival bridge is a clean negative result for the frozen ARA endpoints.
2. The p29-conditioned PNT and Hardy-Littlewood baselines are already extremely well calibrated on the target.
3. The exact mapped-log-ratio ARA control reproduces its equivalent ordinary ratio with zero numerical difference; it is a coordinate crosswalk, not additional predictive information.
4. The deterministic PN1 wheel results remain valid, but they do not automatically transfer to predicting which wheel candidates survive all later prime factors.
5. Further work should not tune new bins on this target. A new endpoint requires a fresh frozen interval and a structural reason for the added information.

Full interpretation is in `PN2_PRIME_SURVIVAL_BRIDGE_REPORT.md`.
"""
        ),
    ]

    for index, cell in enumerate(cells, start=1):
        cell["id"] = f"pn2-{index:02d}"
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
        "full_target_analysis_reexecuted_inside_notebook": True,
        "independent_validation_reexecuted_inside_notebook": True,
        "prime31_accessed": False,
        "independent_validation": "PASS",
    }
    VALIDATION.write_text(json.dumps(outcome, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(outcome, indent=2))


if __name__ == "__main__":
    main()

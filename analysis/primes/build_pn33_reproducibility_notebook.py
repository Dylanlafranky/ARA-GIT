"""Build and execute PN33's lightweight artifact-reproduction notebook."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN33_SEEDED_HEXAGON_FILL_REPRODUCIBILITY.ipynb"
VALIDATION = HERE / "PN33_NOTEBOOK_EXECUTION_VALIDATION.json"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    for output in (NOTEBOOK, VALIDATION):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")

    cells = [
        markdown(
            """# PN33 seeded-hexagon fill: reproducibility notebook

## tl;dr

The frozen coordinate organized a strong rise in prime-gap medians. The endpoint point estimate was **1.5** and
the corrected 95% moving-block interval was **[1.5, 2.0]**. This passes the registered spacing-expression rule,
but ARA improved on the established PNT curve by only **0.62%**, below the frozen 5% ARA-specific threshold.
"""
        ),
        markdown(
            """## Context & Methods

The coordinate is `x_b(p) = 2 log(D(p)/D(b))/log(2)`, where
`D(p) = product_{r<=p} r/(r-1)`. Coordinates were frozen before target prime gaps were summarized. Raw gaps were
assigned to the newly added prime gate and grouped into eight fixed `x` bands. See the frozen protocol for the
complete controls and decision rule.
"""
        ),
        code(
            """from pathlib import Path
import json
import numpy as np

HERE = Path.cwd() / "analysis" / "primes"
results = json.loads((HERE / "PN33_SEEDED_HEXAGON_FILL_RESULTS_VALIDATED.json").read_text())
validation = json.loads((HERE / "PN33_SEEDED_HEXAGON_FILL_VALIDATION.json").read_text())
primary = next(row for row in results["baselines"] if row["baseline_name"] == "primary")
print("status:", results["status"])
print("independent validation:", validation["all_checks_pass"])
print("ARA-specific residual support:", results["decision"]["ara_specific_residual_support"])
"""
        ),
        markdown("""## Data

The exact prime list was independently regenerated through the primary completion ceiling. The table below reports
the three predeclared baselines and their first inverse-density doubling.
"""),
        code(
            """for row in results["baselines"]:
    print(
        f"{row['baseline_name']:14s} baseline={row['baseline_prime']:>8,} "
        f"completion={row['completion_prime']:>11,} gaps={row['gap_count']:>9,} "
        f"rho={row['spearman_band_median_gap']:.4f}"
    )
"""
        ),
        markdown("""## Results

Primary band medians, normalized observations, and the two benchmark curves:
"""),
        code(
            """print("band  n          median  observed  ARA      PNT")
for i, band in enumerate(primary["bands"]):
    print(
        f"{i+1:>4d}  {band['n']:>9,}  {band['median_gap']:>6.1f}  "
        f"{primary['observed_normalized_band_medians'][i]:>8.4f}  "
        f"{primary['ara_predicted_normalized'][i]:>7.4f}  "
        f"{primary['pnt_predicted_normalized'][i]:>7.4f}"
    )
print()
print("endpoint point ratio:", primary["endpoint_final_first_median_ratio"])
print("corrected 95% CI:", primary["endpoint_bootstrap_95_ci"])
print("ARA log-MAE:", primary["ara_log_mae"])
print("PNT log-MAE:", primary["pnt_log_mae"])
print("ARA improvement (%):", 100 * (1 - primary["ara_log_mae"] / primary["pnt_log_mae"]))
"""
        ),
        markdown("""![Audited PN33 result](PN33_SEEDED_HEXAGON_FILL_FIGURE.png)"""),
        markdown(
            """## Takeaways

- The frozen coordinate captures the expected direction of prime-gap growth and resets coherently after its
  density-doubling completion.
- The doubling target is compatible only at the upper boundary of the interval; the observed point ratio is 1.5.
- ARA and PNT are effectively tied on this test, so PN33 is a crosswalk result rather than new prime mathematics.
- PN33 does not test a fixed-step prime generator, literal spatial hexagon, causal Phi landmark, or universal leak.
"""
        ),
    ]

    namespace: dict = {}
    execution_count = 0
    errors = []
    for cell in cells:
        if cell["cell_type"] != "code":
            continue
        execution_count += 1
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer):
                exec("".join(cell["source"]), namespace)
            cell["execution_count"] = execution_count
            cell["outputs"] = [{
                "name": "stdout",
                "output_type": "stream",
                "text": buffer.getvalue().splitlines(keepends=True),
            }]
        except Exception as exc:  # pragma: no cover - failure is recorded durably
            errors.append({"cell": execution_count, "type": type(exc).__name__, "message": str(exc)})
            cell["execution_count"] = execution_count
            cell["outputs"] = [{
                "output_type": "error",
                "ename": type(exc).__name__,
                "evalue": str(exc),
                "traceback": [],
            }]

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
            "pn33": {"test_id": "PN33/SEEDED-HEXAGON-FILL/v1", "executed_by_builder": True},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    payload = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "notebook": NOTEBOOK.name,
        "notebook_sha256": sha256(NOTEBOOK),
        "code_cells_executed": execution_count,
        "errors": errors,
        "all_cells_pass": not errors,
    }
    VALIDATION.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

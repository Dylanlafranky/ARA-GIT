"""Build and execute the dependency-free PN25 reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN25_PAIR_RIDGE_COMPRESSION_REPRODUCIBILITY.ipynb"
RECEIPT = HERE / "PN25_NOTEBOOK_EXECUTION_VALIDATION.json"


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


def main() -> None:
    for output in (NOTEBOOK, RECEIPT):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")

    cells = [
        markdown(
            """# PN25 — corrected pair-ridge compression

## TL;DR

The corrected odds-to-ARA coordinate is exact, and three reversible pair classes preserve essentially all tested
information in the six mod-14 lanes. On 6,000 prospective anchors across three scales, however, ridge-closeness did
not predict fewer handovers, immediate prime closure, three-state closure, or upward path movement. Status:
**geometric-only support / dynamic null**.
"""
        ),
        markdown(
            """## Context & Methods

For mod-14 anti-pair `(a,14-a)`, directional odds `q=a/(14-a)` convert to TE-ARA share
`x_A=2q/(1+q)=a/7`, with `x_B=2-x_A`. Pair-closeness is
`c=min(r,14-r)/7`; orientation is the sign of `r-7`.

The PN24 opened sample supplies frozen model rates. Three new 2,000-anchor ranges are scored without refitting.
The protected 87-bit anchor is absent.
"""
        ),
        code(
            """import csv
import json
from pathlib import Path

HERE = Path.cwd()
results = json.loads((HERE / 'PN25_PAIR_RIDGE_COMPRESSION_RESULTS.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN25_PAIR_RIDGE_COMPRESSION_VALIDATION.json').read_text(encoding='utf-8'))
with (HERE / 'PN25_PAIR_RIDGE_COMPRESSION_TARGETS.csv').open(encoding='utf-8', newline='') as handle:
    targets = list(csv.DictReader(handle))
print(results['status'])
print('validation:', validation['status'], validation['checks_passed'], '/', validation['checks_total'])
assert results['status'] == 'GEOMETRIC-ONLY SUPPORT / DYNAMIC NULL'
assert validation['status'] == 'PASS'
assert len(targets) == 6000
"""
        ),
        markdown("""## Data"""),
        code(
            """print(results['data'])
for scale in ('low', 'middle', 'high'):
    assert sum(row['scale'] == scale for row in targets) == 2000
assert results['data']['protected_87_bit_anchor_used'] is False
"""
        ),
        markdown("""## Results — exact coordinate"""),
        code(
            """for row in results['exact_coordinate_checks']:
    print(row['pair'], row['odds'], '->', row['converted_A'], '+', row['converted_B'])
    assert row['conversion_exact'] is True
    assert row['te_ara_sum_exact'] is True
assert results['exact_coordinate_pass'] is True
"""
        ),
        markdown("""## Results — prospective handover predictions"""),
        code(
            """print('scale | mean H by 1/7,3/7,5/7 | Y0 rates | Y3 rates')
for scale, row in results['ordering_checks'].items():
    print(scale, row['mean_handovers'], row['Y0_rates'], row['Y3_rates'])
print('scale correlations:', results['scale_correlations_c_vs_H'])
print('permutation:', results['permutation_test'])
print('path progression:', results['path_progression'])
print('prediction verdicts:', results['predictions'])
assert results['predictions']['dynamic_predictions_passed'] == 0
"""
        ),
        markdown("""## Results — pair compression versus six lanes"""),
        code(
            """for outcome, scores in results['compression_scores'].items():
    print(outcome, scores)
    assert scores['pair_within_2_percent_of_lane'] is True
    assert scores['pair_beats_global'] is False
    assert scores['lane_beats_global'] is False
assert results['compression_fidelity_pass'] is True
"""
        ),
        markdown(
            """## Takeaways

1. `(1,13)`, `(3,11)` and `(5,9)` are three complete pair identities at different lateral compositions; they are
   not three allocations to add.
2. Odds convert exactly to the bounded total-2 ARA coordinate: `1/13 -> 1/7`, `3/11 -> 3/7`, `5/9 -> 5/7`,
   with the excluded `7/7 -> 1` ridge.
3. Pair-closeness plus orientation reconstructs all six mod-14 lanes exactly. Discarding orientation preserved the
   tested outcome scores to much better than the frozen 2% tolerance.
4. Pair-closeness did not order future prime handovers. The pooled correlation was `+0.003335`, with one-sided
   permutation `p=0.6110` for the predicted negative relation.
5. The pair coordinate is therefore lateral wheel geometry. Higher prime gates form a separate vertical state that
   remains necessary for next-prime completion.
"""
        ),
    ]

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    namespace = {"__name__": "__pn25_notebook__"}
    failures = []
    executed = 0
    old_cwd = Path.cwd()
    os.chdir(HERE)
    try:
        for index, cell in enumerate(cells):
            if cell["cell_type"] != "code":
                continue
            executed += 1
            cell["execution_count"] = executed
            stream = io.StringIO()
            try:
                with contextlib.redirect_stdout(stream):
                    exec("".join(cell["source"]), namespace)
                if stream.getvalue():
                    cell["outputs"] = [{
                        "name": "stdout",
                        "output_type": "stream",
                        "text": stream.getvalue().splitlines(keepends=True),
                    }]
            except Exception as exc:
                failures.append({
                    "cell_index": index,
                    "error": repr(exc),
                    "traceback": traceback.format_exc(),
                })
                cell["outputs"] = [{
                    "ename": type(exc).__name__,
                    "evalue": str(exc),
                    "output_type": "error",
                    "traceback": traceback.format_exc().splitlines(),
                }]
                break
    finally:
        os.chdir(old_cwd)

    NOTEBOOK.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    receipt = {
        "validation_id": "PN25/NOTEBOOK-EXECUTION/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "code_cells_executed": executed,
        "code_cells_total": sum(cell["cell_type"] == "code" for cell in cells),
        "failures": failures,
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

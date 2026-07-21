"""Build and execute PN21 analytical notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN21_RIDGE_STRADDLING_TWO_CHILD_REPRODUCIBILITY.ipynb"
RECEIPT = HERE / "PN21_NOTEBOOK_EXECUTION_VALIDATION.json"


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
    for path in (NOTEBOOK, RECEIPT):
        if path.exists():
            raise RuntimeError(f"refusing to overwrite {path.name}")
    cells = [
        markdown(
            """# PN21 — ridge-straddling two-child retention

## tl;dr

The last prime gate below `sqrt(n)` and first above it retained effectively **0%** of the exact parent factor-progress coordinate on the held-out half (`R²=-0.0000292`). Prime-ridge AUCs were `0.4997` and `0.4991`. This is a development null for that child definition; the sealed 87-bit target was not opened.
"""
        ),
        markdown(
            """## Context & Methods

PN21 asks whether a genuinely ridge-straddling immediate pair provides a TheFormula-like dominant component. The full parent is `1` for primes and `2 log(lpf(n))/log(n)` for composites. The two children are raw residue phases at the nearest prime gates immediately below and above `sqrt(n)`.

### Key Assumptions

- The square-root boundary is the candidate rung boundary.
- A fixed 32×32 raw-phase grid can detect information retained by the pair without claiming that the grid is an ARA formula.
- The first half of the opened interval trains the grid; the second half tests retention.
"""
        ),
        code(
            """import json
import math
from pathlib import Path
import numpy as np
from pn21_ridge_straddling_two_child import (
    LOW, HIGH, MID, prime_table, segmented_least_prime_factor,
    phase_pair, pair_diagnostics,
)

HERE = Path.cwd()
saved = json.loads((HERE / 'PN21_RIDGE_STRADDLING_TWO_CHILD_RESULTS.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN21_RIDGE_STRADDLING_TWO_CHILD_VALIDATION.json').read_text(encoding='utf-8'))
print('Loaded frozen PN21 outputs and independent validation.')
"""
        ),
        markdown("""## Data

The complete opened interval contains one million raw integers. Analysis is restricted to its 500,000 odd candidates. The parent coordinate is reconstructed exactly from a segmented least-factor sieve.
"""),
        code(
            """primes = prime_table(math.isqrt(HIGH - 1) + 200)
least_all = segmented_least_prime_factor(LOW, HIGH, primes)
all_numbers = np.arange(LOW, HIGH, dtype=np.int64)
odd = (all_numbers & 1) == 1
numbers = all_numbers[odd]
least = least_all[odd]
labels = least == 0
parent = np.ones(numbers.size, dtype=np.float64)
composite = ~labels
parent[composite] = 2.0 * np.log(least[composite]) / np.log(numbers[composite])
print('odd candidates:', numbers.size)
print('primes:', int(labels.sum()), 'composites:', int(composite.sum()))
assert numbers.size == 500_000
assert int(labels.sum()) == 45_166
"""
        ),
        markdown("""## Results

The same computation is run for the ridge-straddling pair and the two-below-ridge control.
"""),
        code(
            """root = np.floor(np.sqrt(numbers)).astype(np.int64)
position = np.searchsorted(primes, root, side='right')
q_minus = primes[position - 1]
q_plus = primes[position]
q_second_minus = primes[position - 2]
straddle_a, straddle_b = phase_pair(numbers, q_minus, q_plus)
same_a, same_b = phase_pair(numbers, q_minus, q_second_minus)
train = numbers < MID
test = ~train
straddling = pair_diagnostics('straddling', numbers, parent, labels, straddle_a, straddle_b, train, test)
same_side = pair_diagnostics('same-side', numbers, parent, labels, same_a, same_b, train, test)
for result in (straddling, same_side):
    print(result['name'])
    print('  held-out R2:', result['retention']['heldout_retained_r2'])
    print('  parent correlation:', result['closure_summary']['pearson_with_full_parent'])
    print('  joint AUC:', result['prime_diagnostics']['joint_ridge_auc'])
    print('  closure AUC:', result['prime_diagnostics']['closure_ridge_auc'])
"""
        ),
        code(
            """assert abs(straddling['retention']['heldout_retained_r2'] - saved['straddling_pair']['retention']['heldout_retained_r2']) < 1e-12
assert abs(same_side['retention']['heldout_retained_r2'] - saved['same_side_control']['retention']['heldout_retained_r2']) < 1e-12
assert straddling['retention']['heldout_retained_r2'] < 0.90
assert straddling['retention']['heldout_retained_r2'] <= same_side['retention']['heldout_retained_r2']
print('Frozen threshold: FAIL')
print('Independent validation:', validation['status'], validation['checks_passed'], '/', validation['checks_total'])
assert validation['status'] == 'PASS'
"""
        ),
        markdown(
            """## Takeaways

1. Straddling the square-root ridge fixes orientation but does not make the gates endogenous children of the integer.
2. The pair retained none of the full parent variance out of sample and did not rank primes above chance.
3. The next candidate decomposition should follow actual collision/survival state through the sieve web, potentially including temporal change across neighboring integers.
4. No blind prime-location test is justified from PN21; the 87-bit anchor remains sealed.
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
    namespace = {"__name__": "__pn21_notebook__"}
    failures = []
    count = 0
    old_cwd = Path.cwd()
    os.chdir(HERE)
    try:
        for index, cell in enumerate(cells):
            if cell["cell_type"] != "code":
                continue
            count += 1
            cell["execution_count"] = count
            stream = io.StringIO()
            try:
                with contextlib.redirect_stdout(stream):
                    exec("".join(cell["source"]), namespace)
                output = stream.getvalue()
                if output:
                    cell["outputs"] = [{"name": "stdout", "output_type": "stream", "text": output.splitlines(keepends=True)}]
            except Exception as exc:
                failures.append({"cell_index": index, "error": repr(exc), "traceback": traceback.format_exc()})
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
        "validation_id": "PN21/NOTEBOOK-EXECUTION/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "code_cells_executed": count,
        "code_cells_total": sum(cell["cell_type"] == "code" for cell in cells),
        "failures": failures,
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

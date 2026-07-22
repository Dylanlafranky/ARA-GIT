"""Build and execute the dependency-free PN28 reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN28_THREE_CHILD_RESIDUAL_LIFT_REPRODUCIBILITY.ipynb"
RECEIPT = HERE / "PN28_NOTEBOOK_EXECUTION_VALIDATION.json"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source.splitlines(keepends=True)}


def main() -> None:
    for output in (NOTEBOOK, RECEIPT):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")

    cells = [
        markdown(
            """# PN28 — three-child residual lift

## tl;dr

The literal two-rung residual correction was a clear negative result. On 30,000 fresh odd anchors, the PN27 base
hit **9.197%**, while the three-child correction hit **4.580%**. Odd corrections broke parity, and the common `-2`
correction moved multiples of 3 back onto multiples of 3. The 35 example remained `59`, but that successful local
case did not generalise.
"""
        ),
        markdown(
            """## Context & Methods

For each pair `(1,13)`, `(3,11)`, `(5,9)`, compute the declared signed completion imbalance. Average the three,
double its ridge displacement twice, and round once. Add that integer residual to the frozen PN27 base candidate.

### Key assumptions

- Exact divisibility gives child completion 1; otherwise completion is `2w/N`.
- Pair orientation is fixed from the lower to higher label.
- Two upward rungs multiply the signed displacement by four.
- Half cases round away from zero.
- No parity repair or retry is allowed.
"""
        ),
        code(
            """import csv
import json
from pathlib import Path

HERE = Path.cwd()
results = json.loads((HERE / 'PN28_THREE_CHILD_RESIDUAL_LIFT_RESULTS.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN28_THREE_CHILD_RESIDUAL_LIFT_VALIDATION.json').read_text(encoding='utf-8'))
with (HERE / 'PN28_THREE_CHILD_RESIDUAL_LIFT_VALIDATED_ROWS.csv').open(encoding='utf-8', newline='') as handle:
    rows = list(csv.DictReader(handle))
print('status:', results['status'])
print('validation:', validation['checks_passed'], '/', validation['checks_total'])
assert results['status'] == 'NEGATIVE RESULT'
assert validation['all_checks_passed'] is True
assert len(rows) == 60000
"""
        ),
        markdown("""## Data"""),
        code(
            """print(results['population'])
assert results['population']['odd_primary_rows'] == 30000
assert results['population']['even_secondary_rows'] == 30000
assert results['population']['protected_87_bit_anchor_used'] is False
"""
        ),
        markdown("""## Results — worked example"""),
        code(
            """print(results['worked_example_35'])
assert results['worked_example_35']['base_candidate'] == 59
assert results['worked_example_35']['integer_adjustment'] == 0
assert results['worked_example_35']['corrected_candidate'] == 59
assert results['worked_example_35']['is_prime'] is True
"""
        ),
        markdown("""## Results — primary odd-anchor comparison"""),
        code(
            """primary = results['odd_primary']
print(primary)
assert primary['base_hits'] == 2759
assert primary['corrected_hits'] == 1374
assert primary['difference'] < 0
for scale, summary in results['odd_by_scale'].items():
    print(scale, summary['base_hit_rate'], summary['corrected_hit_rate'], summary['difference'])
    assert summary['difference'] < 0
"""
        ),
        markdown("""## Results — failure mechanisms"""),
        code(
            """for group in results['odd_group_results']:
    if group['dimension'] == 'integer_adjustment':
        print('k=', group['value'], 'n=', group['n'], 'base=', group['base_hit_rate'],
              'corrected=', group['corrected_hit_rate'])
print('relation-broken control:', results['relation_broken_permutation'])
assert results['relation_broken_permutation']['one_sided_p_pooled'] == 1.0
"""
        ),
        markdown("""## Results — even anchors"""),
        code(
            """print(results['even_secondary'])
assert results['even_secondary']['base_hits'] == 0
assert results['even_secondary']['corrected_hits'] == 548
"""
        ),
        markdown(
            """## Takeaways

1. `35 -> 59` remains arithmetically correct under the declared residual rule.
2. The rule does not generalise: it approximately halves one-shot accuracy on fresh odd anchors.
3. Odd residual adjustments turn eligible odd candidates into even composites.
4. The `-2` adjustment reverses the PN27 base's useful escape from divisibility by 3.
5. The three-child vector may remain descriptive, but its signed mean is not a valid integer transport law under
   two simple doublings and nearest-integer collapse.
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
    namespace = {"__name__": "__pn28_notebook__"}
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
                    cell["outputs"] = [{"name": "stdout", "output_type": "stream", "text": stream.getvalue().splitlines(keepends=True)}]
            except Exception as exc:
                failures.append({"cell_index": index, "error": repr(exc), "traceback": traceback.format_exc()})
                cell["outputs"] = [{"ename": type(exc).__name__, "evalue": str(exc), "output_type": "error", "traceback": traceback.format_exc().splitlines()}]
                break
    finally:
        os.chdir(old_cwd)

    NOTEBOOK.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    receipt = {
        "validation_id": "PN28/NOTEBOOK-EXECUTION/v1",
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

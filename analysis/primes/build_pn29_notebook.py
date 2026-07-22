"""Build and execute the dependency-free PN29 reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN29_RELATIONAL_THREE_RUNG_RIDGE_REPRODUCIBILITY.ipynb"
RECEIPT = HERE / "PN29_NOTEBOOK_EXECUTION_VALIDATION.json"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source.splitlines(keepends=True)}


def main() -> None:
    if RECEIPT.exists():
        prior = json.loads(RECEIPT.read_text(encoding="utf-8"))
        if prior.get("status") != "FAIL":
            raise RuntimeError(f"refusing to overwrite successful {RECEIPT.name}")
    elif NOTEBOOK.exists():
        raise RuntimeError(f"refusing to overwrite unreceipted {NOTEBOOK.name}")
    cells = [
        markdown(
            """# PN29 — relational three-rung ridge

## tl;dr

On 493 odd integers below 1,000, primes were much closer to the three-child ridge than all odd composites
(`AUC=0.8635`). The advantage vanished against composites that also evade the declared child factors
(`AUC=0.4442`). The coordinate detects the finite child-factor web, not primality beyond it.
"""
        ),
        markdown(
            """## Context & Methods

Every child pair is normalised onto a total-2 ARA coordinate. Their mean is the child rung `R0`. Upward transport
halves ridge displacement at each rung: `R1=1+(R0-1)/2`, `R2=1+(R0-1)/4`.

### Key assumptions

- Exact divisibility gives local completion 1; otherwise completion is `2w/N`.
- Child pairs have fixed orientation `(1,13)`, `(3,11)`, `(5,9)`.
- No coordinate is converted to an integer prediction in this diagnostic.
- Prime labels are attached only after coordinate freeze, by direct trial division; no sieve is used.
"""
        ),
        code(
            """import csv
import json
from pathlib import Path

HERE = Path.cwd()
results = json.loads((HERE / 'PN29_RELATIONAL_THREE_RUNG_RESULTS.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN29_RELATIONAL_THREE_RUNG_VALIDATION.json').read_text(encoding='utf-8'))
with (HERE / 'PN29_RELATIONAL_THREE_RUNG_SCORED.csv').open(encoding='utf-8', newline='') as handle:
    rows = list(csv.DictReader(handle))
print('status:', results['status'])
print('validation:', validation['checks_passed'], '/', validation['checks_total'])
assert results['status'] == 'PARTIAL / CHILD-FILTER SUPPORT'
assert validation['all_checks_passed'] is True
assert len(rows) == 493
"""
        ),
        markdown("""## Data"""),
        code(
            """print(results['population'])
assert results['population']['sieve_used'] is False
assert results['population']['prime_n'] == 162
assert results['population']['odd_composite_n'] == 331
assert results['population']['unresolved_composite_n'] == 59
"""
        ),
        markdown("""## Results — worked example"""),
        code(
            """row = results['worked_example_35']
print('35:', row['rung_0_decimal'], '->', row['rung_1_decimal'], '->', row['rung_2_decimal'])
assert row['rung_2_fraction'] == '45651/45262'
"""
        ),
        markdown("""## Results — primes versus all odd composites"""),
        code(
            """overall = results['overall_prime_vs_odd_composite']
print(overall)
assert overall['auc_prime_more_ridge_close'] > 0.86
assert overall['permutation']['one_sided_p'] < 0.01
"""
        ),
        markdown("""## Results — unresolved-composite control"""),
        code(
            """control = results['prime_vs_unresolved_composite']
print(control)
assert control['auc_prime_more_ridge_close'] < 0.5
assert control['permutation']['one_sided_p'] > 0.99
"""
        ),
        markdown(
            """## Takeaways

1. Upward `/2` then `/2` transport remains entirely in ARA coordinate space and reproduces the 35 path.
2. The coordinate strongly separates primes from composites divisible by the declared child labels.
3. It does not separate primes from composites that evade those same labels.
4. The supported structure is a finite child-factor web; prime-specific ridge closure remains unresolved.
5. Because upper-rung distance is exactly one quarter of child-rung distance, transport preserves rather than adds
   the available information.
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
    namespace = {"__name__": "__pn29_notebook__"}
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
        "validation_id": "PN29/NOTEBOOK-EXECUTION/v1",
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

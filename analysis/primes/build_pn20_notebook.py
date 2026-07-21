"""Build and execute the PN20 reproducibility notebook without third-party APIs."""

from __future__ import annotations

import contextlib
import io
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN20_ONE_RUNG_TWO_CHILD_REPRODUCIBILITY.ipynb"
RECEIPT = HERE / "PN20_NOTEBOOK_EXECUTION_VALIDATION.json"


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
            """# PN20 — one-rung, two-child prime-location development audit

This notebook reproduces the three development translations and the final branch-aware table. The supplied 87-bit anchor remains sealed and is not present in the notebook. All target labels below had already been opened before PN20.
"""
        ),
        code(
            """import json
from pathlib import Path

HERE = Path.cwd()
numeric = json.loads((HERE / 'PN20_ONE_RUNG_DEVELOPMENT.json').read_text(encoding='utf-8'))
directional = json.loads((HERE / 'PN20_DIRECTIONAL_TWO_CHILD_DEVELOPMENT.json').read_text(encoding='utf-8'))
branch = json.loads((HERE / 'PN20_BRANCH_TWO_CHILD_DEVELOPMENT.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN20_ONE_RUNG_TWO_CHILD_VALIDATION.json').read_text(encoding='utf-8'))
print('Loaded three development artifacts and independent validation.')
"""
        ),
        markdown(
            """## Outcome

The important number is the exact next-prime count, not visual closeness to the normalized ridge. A method intended to find the next prime must return its integer location.
"""
        ),
        code(
            """print('numerical-largest formulas:')
for name, summary in numeric['formula_summary'].items():
    print(f\"  {name}: exact {summary['exact_count']}/{summary['anchor_count']}\")
print('unrestricted directional:', directional['summary'])
print('branch-aware:', branch['summary'])
assert directional['summary']['exact_next_primes'] == 0
assert branch['summary']['exact_next_primes'] == 0
"""
        ),
        markdown(
            """## Branch-aware two-child states

The retained A child is the immediate child furthest toward the ridge from 0. The retained B child is the immediate child furthest toward the ridge from 2. `AB` is their mean progress; `BA=2-AB`.
"""
        ),
        code(
            """header = ('anchor', 'AB(N)', 'AB(2N)', 'prediction', 'actual next prime', 'exact')
print(' | '.join(header))
for row in branch['rows']:
    values = (
        str(row['anchor']),
        f\"{row['landmark_1']['phase_ab']:.9f}\",
        f\"{row['landmark_2']['phase_ab']:.9f}\",
        str(row['predicted_integer']),
        str(row['true_next_prime']),
        str(row['exact_next_prime']),
    )
    print(' | '.join(values))
    assert abs(row['landmark_1']['phase_ab'] + row['landmark_1']['phase_ba'] - 2.0) < 1e-12
"""
        ),
        markdown(
            """## Algebraic collapse of the proposed confirmation expression

Under ordinary precedence, `2*AB/2 - AB + 1` is identically one. It verifies normalization but cannot carry a large integer location.
"""
        ),
        code(
            """for ab in (0.1, 0.5, 1.0, 1.5, 1.9):
    value = 2.0 * ab / 2.0 - ab + 1.0
    print(ab, value)
    assert abs(value - 1.0) < 1e-12
"""
        ),
        markdown(
            """## Independent validation

The validator uses its own bytearray sieve and trial-division prime check. It independently recomputes the immediate children, the next-prime truth labels and all declared exact counts.
"""
        ),
        code(
            """print(validation['status'], validation['checks_passed'], '/', validation['checks_total'])
for item in validation['checks']:
    print('PASS' if item['passed'] else 'FAIL', '-', item['label'])
assert validation['status'] == 'PASS'
assert validation['checks_passed'] == validation['checks_total']
"""
        ),
        markdown(
            """## Interpretation

This is a null for the literal two-scalar location decoder, not for ARA generally. The two children may describe a local identity, but compressing them to `1` and `1` removes scale and produces a many-to-one map. A future one-rung sufficient statistic must retain a non-collapsing location coordinate and must count the cost of selecting its two children.
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

    namespace = {"__name__": "__pn20_notebook__"}
    execution_count = 0
    failures = []
    old_cwd = Path.cwd()
    os.chdir(HERE)
    try:
        for index, cell in enumerate(cells):
            if cell["cell_type"] != "code":
                continue
            execution_count += 1
            cell["execution_count"] = execution_count
            stream = io.StringIO()
            try:
                with contextlib.redirect_stdout(stream):
                    exec("".join(cell["source"]), namespace)
                output = stream.getvalue()
                if output:
                    cell["outputs"] = [{"name": "stdout", "output_type": "stream", "text": output.splitlines(keepends=True)}]
            except Exception as exc:  # pragma: no cover - recorded for artifact QA
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
        "validation_id": "PN20/NOTEBOOK-EXECUTION/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "code_cells_executed": execution_count,
        "code_cells_total": sum(cell["cell_type"] == "code" for cell in cells),
        "failures": failures,
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

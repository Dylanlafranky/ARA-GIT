"""Build an executed, reviewable PN32 notebook from the frozen artifacts."""

from __future__ import annotations

import contextlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "PN32_DOUBLE_INFORMATION_LOCK_REPRODUCIBILITY.ipynb"
RECEIPT = HERE / "PN32_NOTEBOOK_EXECUTION_VALIDATION.json"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str, namespace: dict, count: int) -> dict:
    output = io.StringIO()
    error = None
    try:
        with contextlib.redirect_stdout(output):
            exec(compile(source, f"<PN32 notebook cell {count}>", "exec"), namespace)
    except Exception as exc:
        error = exc
    outputs = []
    text = output.getvalue()
    if text:
        outputs.append({"name": "stdout", "output_type": "stream", "text": text.splitlines(keepends=True)})
    if error is not None:
        outputs.append({
            "ename": type(error).__name__,
            "evalue": str(error),
            "output_type": "error",
            "traceback": [f"{type(error).__name__}: {error}"],
        })
    return {
        "cell_type": "code",
        "execution_count": count,
        "metadata": {},
        "outputs": outputs,
        "source": source.splitlines(keepends=True),
    }


intro = r"""# PN32 double Information³ lock

This executed notebook reads the frozen PN32 artifacts. It does not regenerate or alter the registered test.

The child lock is `(nearest wave, farthest wave, complete five-wave order)` at `N`. The parent lock is the same
object at `2N`. Their closure projection records how the complete child order rearranges on doubling.
"""

sources = [
    """from pathlib import Path
import csv, hashlib, json

HERE = Path(r'F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\primes')
def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

protocol_freeze = json.loads((HERE / 'PN32_PROTOCOL_FREEZE_MANIFEST.json').read_text(encoding='utf-8'))
coordinate_freeze = json.loads((HERE / 'PN32_COORDINATE_FREEZE_MANIFEST.json').read_text(encoding='utf-8'))
results = json.loads((HERE / 'PN32_DOUBLE_INFORMATION_LOCK_RESULTS.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN32_DOUBLE_INFORMATION_LOCK_VALIDATION.json').read_text(encoding='utf-8'))
print('Protocol hash valid:', sha256(HERE / 'PN32_DOUBLE_INFORMATION_LOCK_PROTOCOL_v1_FROZEN.md') == protocol_freeze['protocol_sha256'])
print('Coordinate hash valid:', sha256(HERE / 'PN32_DOUBLE_INFORMATION_LOCK_FROZEN_COORDINATES.csv') == coordinate_freeze['coordinate_file_sha256'])
print('Decision:', results['status'])
""",
    """population = results['population']
print('Rows:', population['n'])
print('Primes:', population['prime_n'])
print('Unresolved composites:', population['unresolved_composite_n'])
print('Hard comparison:', population['hard_comparison_n'])
print('Parent transform:', population['parent_transform'])
""",
    """endpoints = results['primary_prime_vs_unresolved']
for label, key in [
    ('Child-order replication', 'pn31_child_order_replication'),
    ('Parent-order control', 'parent_order_control'),
    ('Child-parent closure', 'double_lock_closure_relation'),
]:
    item = endpoints[key]
    print(f"{label}: TV={item['observed']:.6f}, null mean={item['null_mean']:.6f}, p={item['p_value']:.6f}")
""",
    """broken = endpoints['relation_broken_control']
caveat = validation['methodological_caveat']
print('Broken-control raw-TV p:', broken['p_value'])
print('Intact closure categories:', caveat['intact_closure_category_count'])
print('Mean broken categories:', caveat['mean_broken_closure_category_count'])
print('Support matched:', caveat['raw_tv_control_support_matched'])
print('Interpretation:', caveat['impact'])
""",
    """exact = results['descriptive']['exact_child_parent_order_pair']
assert results['status'] == 'NULL'
assert validation['all_checks_passed']
assert endpoints['pn31_child_order_replication']['p_value'] > 0.05
assert endpoints['double_lock_closure_relation']['p_value'] > 0.05
assert exact['inferential_endpoint'] is False
print('Independent validation:', f"{validation['checks_passed']}/{validation['checks_total']} PASS")
print('Exact-pair sparsity:', exact['combined_category_count'], 'categories among', population['hard_comparison_n'], 'hard rows')
""",
]

namespace: dict = {}
cells = [markdown(intro)]
for number, source in enumerate(sources, 1):
    cells.append(code(source, namespace, number))
cells.append(markdown(r"""## Plain-language result

The five-wave order seen in PN31 did not repeat on the next untouched interval. Doubling each chosen number produced
a real, tightly constrained rearrangement of its child waves, but primes and difficult composites followed the same
rearrangement classes. This `N -> 2N` double-lock representation is therefore a null for prime identity.
"""))

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
if OUT.exists() or RECEIPT.exists():
    raise RuntimeError("refusing to overwrite an existing PN32 notebook artifact")
OUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
errors = [
    output for cell in cells if cell.get("cell_type") == "code"
    for output in cell["outputs"] if output["output_type"] == "error"
]
receipt = {
    "validation_id": "PN32/NOTEBOOK-EXECUTION/v1",
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "status": "PASS" if not errors else "FAIL",
    "code_cells_executed": len(sources),
    "code_cells_total": len(sources),
    "failures": errors,
}
RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(OUT)
print(json.dumps(receipt, indent=2))
if errors:
    raise SystemExit(1)

"""Build and execute the PN23 reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN23_ANTI_PAIR_FRACTAL_LIFT_REPRODUCIBILITY.ipynb"
RECEIPT = HERE / "PN23_NOTEBOOK_EXECUTION_VALIDATION.json"


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
            """# PN23 — anti-pair fractal lift

## tl;dr

One stored representative per reversible wheel-residue pair reconstructed both child directions exactly through five recursive lifts. The untouched `p=17` rung reconstructed all **92,160** residues modulo **510,510** from **46,080** stored pair representatives, with zero mismatches. Independent validation passed **40/40** checks. This is a lossless `2:1` state compression and exact ARA ridge crosswalk to wheel/CRT symmetry, not a constant-cost next-prime locator.
"""
        ),
        markdown(
            """## Context & Methods

The test starts from the modulo-14 anti-pairs `(1,13)`, `(3,11)` and `(5,9)`. It carries only the lower member of each pair. For each new prime gate `p`, it locates the one killed copy on the carried side, reflects that location to predict the opposite collision, and builds the next-rung pair representatives from the carried side alone.

Development gates are `3,5,11,13`; `17` is held out.

### Key Assumptions

- Residue reversal is `r ↔ M-r` for even wheel modulus `M`.
- A pair's ARA child-copy coordinate is normalized to `[0,2]`.
- Passing means exact equality with direct coprimality enumeration, not visual similarity.
- The sealed 87-bit prime anchor is outside this structural test.
"""
        ),
        code(
            """import json
import math
from pathlib import Path

HERE = Path.cwd()
results = json.loads((HERE / 'PN23_ANTI_PAIR_FRACTAL_LIFT_RESULTS.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN23_ANTI_PAIR_FRACTAL_LIFT_VALIDATION.json').read_text(encoding='utf-8'))
print(results['status'])
print('independent validation:', validation['status'], validation['checks_passed'], '/', validation['checks_total'])
assert results['decision']['all_rungs_pass'] is True
assert validation['status'] == 'PASS'
"""
        ),
        markdown(
            """## Data

The data are exact integer residue sets at each frozen wheel rung. No probabilistic prime sample or fitted parameter is used.
"""
        ),
        code(
            """print('phase | lift | parent pairs | child pairs | residues | direct ridges | max error')
for row in results['rungs']:
    print(
        row['phase'],
        f\"{row['parent_modulus']}x{row['gate']}->{row['new_modulus']}\",
        row['parent_pair_count'],
        row['child_pair_count'],
        row['child_residue_count'],
        row['direct_ridge_count'],
        row['max_ridge_error'],
    )
"""
        ),
        markdown(
            """## Results

First verify exact rung growth, reconstruction and the fixed `2:1` lane compression.
"""
        ),
        code(
            """for row in results['rungs']:
    assert row['pass'] is True
    assert row['child_pair_count'] == row['parent_pair_count'] * (row['gate'] - 1)
    assert row['child_residue_count'] == 2 * row['child_pair_count']
    assert row['child_residue_count'] == row['direct_residue_count']
    assert row['missing_residue_count'] == 0
    assert row['extra_residue_count'] == 0
    assert row['collision_failure_count'] == 0
    assert row['integer_ridge_failure_count'] == 0
    assert row['max_ridge_error'] == 0.0
    assert row['stored_lane_compression_ratio'] == 2.0
print('All frozen rung identities verified.')
"""
        ),
        code(
            """smallest = [
    row for row in results['worked_paths']
    if row['parent_modulus'] == 14 and row['gate'] == 3
]
for row in smallest:
    print(
        f\"A/B={row['parent_representative_A']}/{row['reconstructed_parent_B']}\",
        f\"k=({row['killed_copy_A']},{row['predicted_killed_copy_B']})\",
        f\"x=({row['x_A']:.1f},{row['x_B']:.1f})\",
        f\"mean={row['ridge_mean']:.1f}\",
        'children=', row['next_pair_representatives_from_A_only'],
    )
    assert row['ridge_mean'] == 1.0
"""
        ),
        code(
            """held_out = [row for row in results['rungs'] if row['phase'] == 'held_out'][0]
print('held-out gate:', held_out['gate'])
print('stored pair representatives:', held_out['child_pair_count'])
print('full residues reconstructed:', held_out['child_residue_count'])
print('missing / extra:', held_out['missing_residue_count'], held_out['extra_residue_count'])
assert held_out['gate'] == 17
assert held_out['child_pair_count'] == 46080
assert held_out['child_residue_count'] == 92160
"""
        ),
        markdown(
            """## Takeaways

1. One anti-pair adult representative is sufficient to reconstruct the opposite direction and all next-rung pair children exactly.
2. Child asymmetry can close to an exact adult `1.0` ridge: direct `(1,1)` and coarse `(0,2)/(2,0)` cases are distinct but share the same pair mean.
3. The compression is exactly `2:1`; it removes the redundant reflected half of the state.
4. The number of distinct child identities still grows by `p-1` at each new prime gate. Therefore PN23 validates the recursive ARA coordinate but not a two-number or constant-cost prime predictor.
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
    namespace = {"__name__": "__pn23_notebook__"}
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
                    cell["outputs"] = [{
                        "name": "stdout",
                        "output_type": "stream",
                        "text": output.splitlines(keepends=True),
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
        "validation_id": "PN23/NOTEBOOK-EXECUTION/v1",
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

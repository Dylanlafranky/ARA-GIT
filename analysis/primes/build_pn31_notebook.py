"""Build and execute the dependency-free PN31 reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_REPRODUCIBILITY.ipynb"
RECEIPT = HERE / "PN31_NOTEBOOK_EXECUTION_VALIDATION.json"


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
            """# PN31 - five independent child-wave handovers

## tl;dr

With wave 1 removed and the five remaining children kept separate, neither the nearest child's distance nor its identity distinguished primes from hard unresolved composites. The complete five-wave ordering did (`TV=0.6728`, permutation `p=0.00390`). No single wave or post-hoc pairwise ordering explained that result after correction, so it is an ordered joint-configuration result requiring replication.
"""
        ),
        markdown(
            """## Context & Methods

For each wave in `{3,5,9,11,13}`, calculate its 0-2 position and directed forward distance to the next handover. The smallest distance defines Phase A, but all five distances and their full closest-to-farthest order are retained.

### Key assumptions

- Wave 1 is excluded completely.
- No fixed child pairs or averaged child coordinate are used.
- Coordinates for odd integers 2001-2999 were frozen before labels.
- Prime labels use direct trial division after freeze; no sieve is used.
- Pairwise order decomposition is post-hoc and not a frozen endpoint.
"""
        ),
        code(
            """import csv
import json
from pathlib import Path

HERE = Path.cwd()
results = json.loads((HERE / 'PN31_FIVE_INDEPENDENT_HANDOVER_RESULTS.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN31_FIVE_INDEPENDENT_HANDOVER_VALIDATION.json').read_text(encoding='utf-8'))
posthoc = json.loads((HERE / 'PN31_FIVE_INDEPENDENT_HANDOVER_POSTHOC.json').read_text(encoding='utf-8'))
with (HERE / 'PN31_FIVE_INDEPENDENT_HANDOVER_SCORED.csv').open(encoding='utf-8', newline='') as handle:
    rows = list(csv.DictReader(handle))
print('status:', results['status'])
print('validation:', validation['checks_passed'], '/', validation['checks_total'])
assert validation['all_checks_passed'] is True
assert len(rows) == 500
"""
        ),
        markdown("""## Data"""),
        code(
            """print(results['population'])
assert results['population']['waves'] == [3, 5, 9, 11, 13]
assert results['population']['wave_1_included'] is False
assert results['population']['fixed_pairs_used'] is False
assert results['population']['sieve_used'] is False
"""
        ),
        markdown("""## Results - nearest child and identity"""),
        code(
            """primary = results['primary_prime_vs_unresolved']
print('Phase A distance:', primary['phase_a_distance'])
print('Phase A identity:', primary['phase_a_identity'])
assert primary['phase_a_distance']['permutation']['p_value'] > 0.29
assert primary['phase_a_identity']['p_value'] > 0.88
"""
        ),
        markdown("""## Results - complete five-wave order"""),
        code(
            """order = primary['five_wave_order']
print('full order:', order['observed'], order['p_value'])
assert order['observed'] > 0.67
assert order['p_value'] < 0.01
"""
        ),
        markdown("""## Results - component and post-hoc checks"""),
        code(
            """print('individual waves:', primary['individual_waves'])
print('post-hoc pairwise order:', posthoc['pairwise_order_relations'])
assert all(item['holm_adjusted_p'] > 0.98 for item in primary['individual_waves'].values())
assert all(item['holm_adjusted_p'] == 1.0 for item in posthoc['pairwise_order_relations'].values())
"""
        ),
        markdown(
            """## Takeaways

1. Ditching wave 1 removes the permanently exact, non-informative child.
2. One closest child is insufficient: its distance and identity were null.
3. The complete five-child ordering passed the frozen order-distribution test (`p=0.00390`).
4. No individual child or pairwise relation explained the result after multiplicity correction.
5. The joint ordering must replicate unchanged before it is treated as a stable prime-specific ARA structure.
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
    namespace = {"__name__": "__pn31_notebook__"}
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
        "validation_id": "PN31/NOTEBOOK-EXECUTION/v1",
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

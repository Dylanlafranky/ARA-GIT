"""Build and execute the dependency-free PN30 reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_REPRODUCIBILITY.ipynb"
RECEIPT = HERE / "PN30_NOTEBOOK_EXECUTION_VALIDATION.json"


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
    if RECEIPT.exists():
        prior = json.loads(RECEIPT.read_text(encoding="utf-8"))
        if prior.get("status") != "FAIL":
            raise RuntimeError(f"refusing to overwrite successful {RECEIPT.name}")
    elif NOTEBOOK.exists():
        raise RuntimeError(f"refusing to overwrite unreceipted {NOTEBOOK.name}")

    cells = [
        markdown(
            """# PN30 - dynamic relational flip ridge

## tl;dr

On a fresh 500-number odd interval, restoring singularity-driven AB/BA flips raised the difficult unresolved-composite AUC from `0.5301` to `0.5663`. The frozen one-sided result was `p=0.06199`, so the direction is suggestive but not statistically reliable. Post-hoc decomposition shows that the possible gain came from stronger cancellation among signed child orientations, not from different individual pair magnitudes.
"""
        ),
        markdown(
            """## Context & Methods

For each child wave, normalized phase is `theta=(N mod w)/w`. In each unordered pair, the smaller theta becomes Phase A. The dynamically oriented pair coordinate is reflected around 1.0 whenever orientation flips. Three signed pair coordinates are averaged, and their displacement is halved at each of two upward rungs.

### Key assumptions

- Child pairs are `{1,13}`, `{3,11}`, `{5,9}`.
- PN29's completion function is retained unchanged.
- Coordinates for odd integers 1001-1999 were frozen before labels.
- Prime labels use direct trial division after freeze; no sieve is used.
- Post-hoc cancellation diagnostics are descriptive and not frozen endpoints.
"""
        ),
        code(
            """import csv
import json
from pathlib import Path

HERE = Path.cwd()
results = json.loads((HERE / 'PN30_DYNAMIC_RELATIONAL_FLIP_RESULTS.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN30_DYNAMIC_RELATIONAL_FLIP_VALIDATION.json').read_text(encoding='utf-8'))
posthoc = json.loads((HERE / 'PN30_DYNAMIC_RELATIONAL_FLIP_POSTHOC.json').read_text(encoding='utf-8'))
with (HERE / 'PN30_DYNAMIC_RELATIONAL_FLIP_SCORED.csv').open(encoding='utf-8', newline='') as handle:
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
print('orientation counts:', results['orientation_counts'])
assert results['population']['sieve_used'] is False
assert results['population']['prime_n'] == 135
assert results['population']['odd_composite_n'] == 365
assert results['population']['unresolved_composite_n'] == 90
"""
        ),
        markdown("""## Results - dynamic coordinate"""),
        code(
            """overall = results['dynamic']['overall_prime_vs_odd_composite']
unresolved = results['dynamic']['prime_vs_unresolved_composite']
print('overall:', overall)
print('unresolved:', unresolved)
assert overall['auc_prime_more_ridge_close'] > 0.78
assert overall['permutation']['one_sided_p'] < 0.01
assert 0.56 < unresolved['auc_prime_more_ridge_close'] < 0.57
assert unresolved['permutation']['one_sided_p'] > 0.05
"""
        ),
        markdown("""## Results - same-interval static comparator"""),
        code(
            """static = results['static_same_interval_control']
delta = results['dynamic_minus_static_auc']
print('static:', static)
print('dynamic minus static AUC:', delta)
assert delta['overall'] < 0
assert delta['unresolved'] > 0.03
"""
        ),
        markdown("""## Results - post-hoc signed cancellation mechanism"""),
        code(
            """print('prime:', posthoc['prime'])
print('unresolved composite:', posthoc['unresolved_composite'])
assert posthoc['status'].startswith('POST-HOC')
assert posthoc['prime']['mean_signed_cancellation_fraction'] > posthoc['unresolved_composite']['mean_signed_cancellation_fraction']
"""
        ),
        markdown(
            """## Takeaways

1. PN30 restores the singularity flip that PN29 omitted.
2. Dynamic orientation weakened the easy overall child-divisor screen but improved the hard unresolved comparison by `+0.0361` AUC.
3. The improvement missed the frozen significance threshold (`p=0.06199`) and requires replication.
4. Pair magnitudes were nearly identical; the descriptive difference appeared in how their signed orientations cancelled.
5. This is a reversible ARA coordinate diagnostic, not a prime generator or certification method.
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

    namespace = {"__name__": "__pn30_notebook__"}
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
        "validation_id": "PN30/NOTEBOOK-EXECUTION/v1",
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

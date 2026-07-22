"""Build and execute the dependency-free PN26 reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN26_DOMINANT_PARENT_RIDGE_LOCATOR_REPRODUCIBILITY.ipynb"
RECEIPT = HERE / "PN26_NOTEBOOK_EXECUTION_VALIDATION.json"


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
            """# PN26 — dominant-parent ridge locator

## TL;DR

One complete lower Phase A parent located the exact next prime on **93.983%** of 6,000 prospectively frozen
anchors. The next prime was in its first two quiet states on **99.650%** and first three on **99.967%**. Three ARA
thresholds passed; a deliberately severe 50-point control-margin failed, so the frozen status is **partial
dominant-parent support**. The fixed `3.5` route is an exact scale frame with zero predictive variance.
"""
        ),
        markdown(
            """## Context & Methods

For each narrow scale cohort, children through `sqrt(2S)` are split at the cumulative-log half. Phase A retains
the smaller, frequent gates and Phase B retains the larger, sparse gates. The primary script—without a primality
test—sealed the first three Phase A quiet candidates at each arbitrary anchor. An independent full segmented-prime
mask then revealed the true next-prime rank.

### Key assumptions

- The cohort lower boundary `S` declares the local rung `S -> 2S`.
- The log-half split is frozen from PN19 and is not refitted on target results.
- Visible ranked states are not arithmetic-operation counts; Phase A still contains many prime children.
- Validator v1.1 changes only a documented prime-table ceiling bug. The sealed predictions are unchanged.
"""
        ),
        code(
            """import csv
import json
from pathlib import Path

HERE = Path.cwd()
primary = json.loads((HERE / 'PN26_DOMINANT_PARENT_RIDGE_PRIMARY.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN26_DOMINANT_PARENT_RIDGE_VALIDATION_V1_1.json').read_text(encoding='utf-8'))
failed_v1 = json.loads((HERE / 'PN26_DOMINANT_PARENT_RIDGE_VALIDATION.json').read_text(encoding='utf-8'))
with (HERE / 'PN26_DOMINANT_PARENT_RIDGE_VALIDATED_ROWS_V1_1.csv').open(encoding='utf-8', newline='') as handle:
    rows = list(csv.DictReader(handle))
print(primary['status'])
print(validation['status'], validation['checks_passed'], '/', validation['checks_total'])
print('preserved v1 status:', failed_v1['status'])
assert primary['row_count'] == 6000
assert len(rows) == 6000
assert validation['checks_passed'] == validation['checks_total'] == 16
"""
        ),
        markdown("""## Data"""),
        code(
            """for metadata in primary['scale_metadata']:
    print(metadata)
assert primary['protected_87_bit_anchor_used'] is False
assert validation['protected_87_bit_anchor_used'] is False
assert all(sum(row['cohort'] == cohort for row in rows) == 2000 for cohort in ('low','middle','high'))
"""
        ),
        markdown("""## Results — prospective ranked locator"""),
        code(
            """for summary in validation['summaries']:
    print(
        summary['cohort'],
        'top1=', round(summary['phase_a_top1_rate'], 6),
        'top2=', round(summary['phase_a_top2_rate'], 6),
        'top3=', round(summary['phase_a_top3_rate'], 6),
        'p29 top3=', round(summary['p29_top3_rate'], 6),
        'ranks=', summary['rank_counts'],
    )
pooled = next(row for row in validation['summaries'] if row['cohort'] == 'pooled')
assert pooled['phase_a_top1_rate'] == 5639/6000
assert pooled['phase_a_top2_rate'] == 5979/6000
assert pooled['phase_a_top3_rate'] == 5998/6000
"""
        ),
        markdown("""## Results — frozen decisions and controls"""),
        code(
            """print(validation['registered_predictions'])
assert validation['registered_predictions']['P1_top1_at_least_90_percent'] is True
assert validation['registered_predictions']['P2_top2_at_least_99_percent'] is True
assert validation['registered_predictions']['P3_top3_at_least_99_9_percent'] is True
assert validation['registered_predictions']['P4_top3_beats_p29_by_50pp'] is False
assert validation['registered_predictions']['P5_frame_exact_zero_variance'] is True
assert validation['registered_predictions']['P6_reconstruction_and_truth_checks'] is True
print('Phase A top3 advantage over p29:', pooled['phase_a_top3_rate'] - pooled['p29_top3_rate'])
print('Phase A top3 advantage over odd scan:', pooled['phase_a_top3_rate'] - pooled['odd_top3_rate'])
"""
        ),
        markdown("""## Results — edge cases and frame"""),
        code(
            """misses = [row for row in rows if int(row['phase_a_rank_of_prime']) > 3]
for row in misses:
    print(row['anchor'], '->', row['actual_next_prime'], 'rank', row['phase_a_rank_of_prime'])
assert len(misses) == 2
print(validation['cross_rung_frame'])
assert validation['cross_rung_frame']['value'] == 3.5
assert validation['cross_rung_frame']['variance'] == 0.0
"""
        ),
        markdown(
            """## Takeaways

1. The corrected object is a complete child parent, not two individual factor labels.
2. Its first quiet state prospectively recovered 93.983% of next primes; two and three ranked states reached
   99.650% and 99.967%.
3. The result transferred across 71 million, 71 billion and 710 billion scales without target refitting.
4. The fixed `3.5` cross-rung route is an exact contextual frame, but its zero variance means it does not supply the
   changing prime correction.
5. Phase A remains a large partial sieve (780–48,817 children here). This is strong visible-state compression, not
   a three-operation or exact constant-cost prime algorithm.
6. The original validator failure remains recorded; v1.1 repaired only the child-table ceiling and reproduced all
   sealed predictions with 16/16 checks.
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
    namespace = {"__name__": "__pn26_notebook__"}
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
        "validation_id": "PN26/NOTEBOOK-EXECUTION/v1",
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

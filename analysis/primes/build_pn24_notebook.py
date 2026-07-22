"""Build and execute the dependency-free PN24 reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN24_NEAREST_HANDOVER_CASCADE_REPRODUCIBILITY.ipynb"
RECEIPT = HERE / "PN24_NOTEBOOK_EXECUTION_VALIDATION.json"


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
            """# PN24 — nearest-child handover cascade

## TL;DR

The nearest-child cascade exactly recovered every next prime after retaining all factor gates, but the compact
90% criterion failed. On 2,000 deterministic opened anchors, 63.65% closed within three candidate states and
83.85% within three handovers. The median visible path had two handovers, while the median proof crossed 6,336
non-base prime gates. This is partial structural support for the ARA handover representation, not a constant-cost
prime locator.
"""
        ),
        markdown(
            """## Context and methods

The base rung keeps integers surviving gates 2 and 7. For each anchor, the nearest surviving lanes below and above
form the local pair. The upper lane is the first candidate. When a later prime gate divides it, the next upper
survivor becomes the candidate. The path terminates after all gates through the candidate's square root have been
cleared.

The protected 87-bit anchor is not present. The development sample and thresholds are defined in the frozen PN24
protocol.
"""
        ),
        code(
            """import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path.cwd()
results = json.loads((HERE / 'PN24_NEAREST_HANDOVER_CASCADE_RESULTS.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN24_NEAREST_HANDOVER_CASCADE_VALIDATION.json').read_text(encoding='utf-8'))
with (HERE / 'PN24_NEAREST_HANDOVER_CASCADE_ANCHORS.csv').open(encoding='utf-8', newline='') as handle:
    anchors = list(csv.DictReader(handle))
with (HERE / 'PN24_NEAREST_HANDOVER_CASCADE_EVENTS.csv').open(encoding='utf-8', newline='') as handle:
    events = list(csv.DictReader(handle))
print(results['status'])
print('validation:', validation['status'], validation['checks_passed'], '/', validation['checks_total'])
assert validation['status'] == 'PASS'
assert len(anchors) == 2007
assert all(row['final_matches_truth'] == 'True' for row in anchors)
"""
        ),
        markdown(
            """## Data

Seven previously opened scale anchors are combined with 2,000 deterministic anchors sampled from the opened PN19
interval. The sample contains overlapping next-prime labels and is descriptive rather than an independent-event
sample.
"""
        ),
        code(
            """print(results['data'])
sample = [row for row in anchors if row['cohort'] == 'sample']
scale = [row for row in anchors if row['cohort'] == 'scale']
assert len(sample) == 2000 and len(scale) == 7
"""
        ),
        markdown("""## Results — visible handover lineage"""),
        code(
            """summary = results['cascade_sample']
for key in (
    'zero_handover_rate',
    'within_two_candidate_states_rate',
    'within_three_candidate_states_rate',
    'within_three_handover_events_rate',
    'mean_handover_events',
    'median_handover_events',
    'max_handover_events',
):
    print(key, summary[key])
print('distribution', summary['handover_event_distribution'])
assert summary['within_three_candidate_states_rate'] == 0.6365
assert summary['within_three_handover_events_rate'] == 0.8385
assert results['decision']['compact_three_candidate_threshold_passed'] is False
"""
        ),
        markdown("""## Results — fixed rungs"""),
        code(
            """print('rung | exact rate | mean surviving candidates through prime')
for row in results['fixed_rungs_all_anchors']:
    print(row['rung'], f"{row['exact_rate']:.4f}", f"{row['mean_survivor_candidates_through_prime']:.3f}")
"""
        ),
        markdown("""## Results — visible events versus hidden gate work"""),
        code(
            """for key in (
    'median_handover_events',
    'median_total_nonbase_gate_crossings',
    'median_silent_gate_crossings',
    'median_initial_to_final_delta_ratio',
):
    print(key, summary[key])
assert summary['median_handover_events'] == 2.0
assert summary['median_total_nonbase_gate_crossings'] == 6336.0
assert summary['median_silent_gate_crossings'] == 6334.0
"""
        ),
        code(
            """print('anchor | base delta | handover gates | final delta | states')
events_by_anchor = {}
for event in events:
    events_by_anchor.setdefault(int(event['anchor']), []).append(int(event['gate']))
for row in scale:
    anchor = int(row['anchor'])
    print(
        anchor,
        int(row['initial_forward_delta']),
        events_by_anchor.get(anchor, []),
        int(row['final_delta']),
        int(row['candidate_states']),
    )
"""
        ),
        markdown(
            """## Takeaways

1. The nearest lower/upper pair and each releasing-gate handover are exact, reproducible integer objects.
2. The cascade gives a short visible candidate genealogy: median two handovers, maximum nine in this sample.
3. The first child captured only 11.11% of the final correction at the median, and only 63.65% of anchors closed
   within three candidate states. The frozen 90% compact criterion failed.
4. Thousands of silent gates remain necessary to identify the releasing gates and prove the final candidate.
5. PN24 is therefore an exact incremental wheel/trial-division crosswalk and useful ARA event representation, not
   a new constant-operation prime algorithm.
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

    namespace = {"__name__": "__pn24_notebook__"}
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
        "validation_id": "PN24/NOTEBOOK-EXECUTION/v1",
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

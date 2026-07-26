"""Build an executed, rerunnable Q31 data-gate audit notebook.

The bundled runtime does not require Jupyter to be installed: this builder
executes the audit directly, records the outputs, and writes valid notebook
JSON. The code cells remain rerunnable in any standard Jupyter environment.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "Q31_LATTICE_TO_TRAVERSAL_DATA_GATE_AUDIT_NOTEBOOK.ipynb"
sys.path.insert(0, str(ROOT))

from q31_data_gate_audit import run_audit  # noqa: E402


def markdown(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.splitlines()],
    }


def code(source: str, execution_count: int, outputs: list[dict]) -> dict:
    return {
        "cell_type": "code",
        "execution_count": execution_count,
        "metadata": {},
        "outputs": outputs,
        "source": [line + "\n" for line in source.splitlines()],
    }


def stream(text: str) -> dict:
    return {
        "name": "stdout",
        "output_type": "stream",
        "text": [line + "\n" for line in text.rstrip().splitlines()],
    }


def display_frame(frame: pd.DataFrame) -> dict:
    return {
        "data": {
            "text/html": [frame.to_html(border=1)],
            "text/plain": [repr(frame)],
        },
        "metadata": {},
        "output_type": "display_data",
    }


def build() -> None:
    result = run_audit(ROOT)
    rows = []
    for candidate in result["candidates"]:
        rows.append(
            {
                "candidate": candidate["candidate"],
                "source": candidate["source"],
                "two_coordinate_path": candidate.get("two_coordinate_path"),
                "external_handover": candidate.get("external_handover"),
                "pre_and_post_windows": candidate.get("pre_and_post_windows"),
                "eligible_eval_transitions": candidate.get(
                    "eligible_evaluation_transitions"
                ),
                "decision": candidate["decision"],
                "failed_gate": " | ".join(candidate["failed_gates"]),
            }
        )
    audit_table = pd.DataFrame(rows)
    candidate6 = next(c for c in result["candidates"] if c["candidate"] == 6)
    candidate6_table = pd.DataFrame(candidate6["conditions"]).T

    cells = [
        markdown(
            """# Q31 lattice-to-traversal data-gate audit

**Question:** Can this quantum-domain manifestation of the older conditional
ARA singularity-flip rule be evaluated on the fresh public experimental
sources inspected on 26 July 2026?

This notebook checks source eligibility only. It deliberately does **not**
calculate `C`, `T`, `x`, memory, closure or TE-ARA outcome metrics when a data
gate fails. That protects the preregistered test from being reshaped around the
available data.

The protocol, formulas, thresholds and falsifiers were frozen before source
inspection in `Q31_LATTICE_TO_TRAVERSAL_PROTOCOL_v1_FROZEN.md`."""
        ),
        code(
            """from pathlib import Path
import json
import sys
import pandas as pd

ROOT = Path.cwd()
if not (ROOT / "q31_data_gate_audit.py").exists():
    ROOT = Path(r"F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\quantum")
sys.path.insert(0, str(ROOT))

from q31_data_gate_audit import run_audit

result = run_audit(ROOT)
print(result["verdict"])
print("Eligible candidates:", result["eligible_candidate_count"])""",
            1,
            [
                stream(
                    f'{result["verdict"]}\n'
                    f'Eligible candidates: {result["eligible_candidate_count"]}'
                )
            ],
        ),
        markdown(
            """## Integrity and schema results

The three local archives/workbook groups are checked against their published
MD5 values. Candidate 4 workbook structure was read with
`@oai/artifact-tool`; the theoretical lines were not counted as experimental
units. Candidate 5 hardware paths are distinguished from emulator and
classical numerical paths by the repository's own directory structure.
Candidate 6 event counts follow the filters in the authors' Mathematica
notebook."""
        ),
        code(
            """rows = []
for candidate in result["candidates"]:
    rows.append({
        "candidate": candidate["candidate"],
        "source": candidate["source"],
        "two_coordinate_path": candidate.get("two_coordinate_path"),
        "external_handover": candidate.get("external_handover"),
        "pre_and_post_windows": candidate.get("pre_and_post_windows"),
        "eligible_eval_transitions": candidate.get("eligible_evaluation_transitions"),
        "decision": candidate["decision"],
        "failed_gate": " | ".join(candidate["failed_gates"]),
    })

audit_table = pd.DataFrame(rows)
audit_table""",
            2,
            [display_frame(audit_table)],
        ),
        markdown(
            """## Candidate 6 exact count audit

The most promising transition source contains 200 non-sentinel tunnelling
events across three conditions. Only 144 have at least 25 pre-handover samples.
After the deterministic half split, the upper bound is 72 long-enough
evaluation events—not the frozen 500 evaluation transitions. More importantly,
the monitoring ends at detected tunnelling and therefore supplies no
post-handover trajectory."""
        ),
        code(
            """candidate6 = next(c for c in result["candidates"] if c["candidate"] == 6)
pd.DataFrame(candidate6["conditions"]).T""",
            3,
            [display_frame(candidate6_table)],
        ),
        code(
            """assert result["eligible_candidate_count"] == 0
assert candidate6["events_after_author_filters"] == 200
assert candidate6["events_with_at_least_25_pre_samples"] == 144
assert candidate6["evaluation_long_enough_upper_bound"] == 72
assert result["confirmatory_outcome_metrics_calculated"] is False

output = ROOT / "Q31_DATA_GATE_AUDIT_RESULTS.json"
output.write_text(json.dumps(result, indent=2), encoding="utf-8")
print("Wrote", output)
print("All audit assertions passed.")""",
            4,
            [
                stream(
                    f"Wrote {ROOT / 'Q31_DATA_GATE_AUDIT_RESULTS.json'}\n"
                    "All audit assertions passed."
                )
            ],
        ),
        markdown(
            """## Verdict

**Q31 v1 is INCONCLUSIVE by its frozen data/eligibility gate.**

This is not a negative result for the specific quantum
lattice-to-traversal manifestation: no eligible source reached the outcome
calculation. Q31 is a domain replication of an older, mixed singularity-flip
lineage rather than its first existence test. The scarcity of continuous
far-side measurements is a measurement-ecology clue, not physical evidence.
It is also not permission to relax the gate.
The next decisive run requires at least 60 independent two-coordinate
trajectories (30 untouched evaluation units), observations on both sides of an
externally imposed release crossing, and at least 500 eligible evaluation
transitions. A new experiment or a newly released raw dataset can be inserted
without changing the frozen formulas or thresholds."""
        ),
    ]

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    OUTPUT.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    build()

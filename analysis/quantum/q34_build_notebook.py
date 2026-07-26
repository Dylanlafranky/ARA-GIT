"""Build an executed, reader-facing notebook from the sealed Q34 artifacts."""

from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / ".q27_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import pandas as pd


OUTPUT = HERE / "Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_NOTEBOOK.ipynb"


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


def stream(value: str) -> dict:
    return {
        "name": "stdout",
        "output_type": "stream",
        "text": [line + "\n" for line in value.rstrip().splitlines()],
    }


def display_frame(frame: pd.DataFrame) -> dict:
    return {
        "data": {
            "text/html": [frame.to_html(border=1, index=False)],
            "text/plain": [frame.to_string(index=False)],
        },
        "metadata": {},
        "output_type": "display_data",
    }


def build() -> None:
    result = json.loads(
        (HERE / "Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_RESULTS.json").read_text(
            encoding="utf-8"
        )
    )
    validation = json.loads(
        (HERE / "Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_VALIDATION.json").read_text(
            encoding="utf-8"
        )
    )
    evaluation = result["splits"]["evaluation"]
    routes = pd.DataFrame(
        [
            {
                "route": route,
                "events": evaluation["routes"][route]["paired_events"],
                "median flow": evaluation["routes"][route]["flow"]["median"],
                "mean flow": evaluation["routes"][route]["flow"]["mean"],
                "positive fraction": evaluation["routes"][route][
                    "positive_fraction"
                ],
                "median starting z": evaluation["routes"][route]["start_z"][
                    "median"
                ],
            }
            for route in ("exact", "sibling", "topology", "seed", "time")
        ]
    )
    paired = pd.DataFrame(
        [
            {
                "comparator": comparator,
                "paired median difference": evaluation["paired_differences"][
                    comparator
                ]["median"],
                "cluster mean difference": result["evaluation_bootstrap"][
                    comparator
                ]["mean_exact_minus_comparator"],
                "bootstrap P(exact greater)": result["evaluation_bootstrap"][
                    comparator
                ]["probability_exact_greater"],
            }
            for comparator in ("sibling", "topology", "seed", "time")
        ]
    )
    branches = pd.DataFrame(
        [
            {
                "branch": branch,
                "events": evaluation["branches"][branch]["source_events"],
                "median exact flow": evaluation["branches"][branch][
                    "exact_flow"
                ]["median"],
                "positive fraction": evaluation["branches"][branch][
                    "exact_positive_fraction"
                ],
            }
            for branch in ("c2", "c4")
        ]
    )
    comparison = pd.DataFrame(
        [
            {
                "quantity": "exact median flow",
                "Q33B random": result["q33b_comparison"][
                    "q33b_median_flow"
                ],
                "Q34 greedy": result["q33b_comparison"][
                    "q34_median_flow"
                ],
                "change": result["q33b_comparison"]["median_flow_delta"],
            },
            {
                "quantity": "exact positive fraction",
                "Q33B random": result["q33b_comparison"][
                    "q33b_positive_fraction"
                ],
                "Q34 greedy": result["q33b_comparison"][
                    "q34_positive_fraction"
                ],
                "change": result["q33b_comparison"][
                    "positive_fraction_delta"
                ],
            },
        ]
    )
    failed_gates = [
        gate
        for gate, passed in result["frozen_verdict"]["routing_gates"].items()
        if not passed
    ]
    verdict = result["frozen_verdict"]["label"]

    cells = [
        markdown(
            f"""# Q34 — untouched cross-archive boundary-child replication

## tl;dr

Q34 transferred Q33B's frozen ARA route from a random network ordering to the
previously untouched public `pure_greedy` archive.

The exact route retained a positive median in both branches, but its positive
fraction fell from 63.64% to 54.21% and it did not reliably beat all
same-rule controls.

Frozen verdict: **{verdict}**

Independent raw-HDF5 validation: **{validation["status"]}**."""
        ),
        markdown(
            r"""## Context & Methods

The invariant geometry remained:

\[
2+\left(1+\frac12\right)=3.5.
\]

`0.5` is a declared adjacent-rung projection, not a coefficient fitted to the
target. Starting normalized closure selects the lower endpoint child; its
unseen next-slice closure change is scored.

Development scales, source conditions, event sample, controls and every
pass/fail threshold are identical to Q33B and were sealed before download."""
        ),
        code(
            """from pathlib import Path
import json

ROOT = Path.cwd()
if not (ROOT / "Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_RESULTS.json").exists():
    ROOT = Path(r"F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\quantum")

result = json.loads((ROOT / "Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_RESULTS.json").read_text())
validation = json.loads((ROOT / "Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_VALIDATION.json").read_text())
evaluation = result["splits"]["evaluation"]
print("Structural path:", result["geometry"]["complete_path"])
print("Evaluation events:", evaluation["source_events"])
print("Verdict:", result["frozen_verdict"]["label"])
print("Independent validation:", validation["status"])""",
            1,
            [
                stream(
                    "Structural path: 3.5\n"
                    f'Evaluation events: {evaluation["source_events"]}\n'
                    f"Verdict: {verdict}\n"
                    f'Independent validation: {validation["status"]}'
                )
            ],
        ),
        markdown("## Results\n\n### Route flow"),
        code(
            """routes = pd.DataFrame([
    {
        "route": route,
        "events": evaluation["routes"][route]["paired_events"],
        "median flow": evaluation["routes"][route]["flow"]["median"],
        "mean flow": evaluation["routes"][route]["flow"]["mean"],
        "positive fraction": evaluation["routes"][route]["positive_fraction"],
        "median starting z": evaluation["routes"][route]["start_z"]["median"],
    }
    for route in ("exact", "sibling", "topology", "seed", "time")
])
routes""",
            2,
            [display_frame(routes)],
        ),
        markdown(
            """The exact route remains mildly positive. It exceeds the sibling
by 2.27 percentage points in positive frequency, but the sibling has a larger
marginal median and the seed/time controls are more often positive."""
        ),
        markdown("### Paired comparisons"),
        code(
            """paired = pd.DataFrame([
    {
        "comparator": comparator,
        "paired median difference": evaluation["paired_differences"][comparator]["median"],
        "cluster mean difference": result["evaluation_bootstrap"][comparator]["mean_exact_minus_comparator"],
        "bootstrap P(exact greater)": result["evaluation_bootstrap"][comparator]["probability_exact_greater"],
    }
    for comparator in ("sibling", "topology", "seed", "time")
])
paired""",
            3,
            [display_frame(paired)],
        ),
        markdown("### Branches"),
        code(
            """branches = pd.DataFrame([
    {
        "branch": branch,
        "events": evaluation["branches"][branch]["source_events"],
        "median exact flow": evaluation["branches"][branch]["exact_flow"]["median"],
        "positive fraction": evaluation["branches"][branch]["exact_positive_fraction"],
    }
    for branch in ("c2", "c4")
])
branches""",
            4,
            [display_frame(branches)],
        ),
        markdown("### Cross-archive attenuation"),
        code(
            """comparison = pd.DataFrame([
    {
        "quantity": "exact median flow",
        "Q33B random": result["q33b_comparison"]["q33b_median_flow"],
        "Q34 greedy": result["q33b_comparison"]["q34_median_flow"],
        "change": result["q33b_comparison"]["median_flow_delta"],
    },
    {
        "quantity": "exact positive fraction",
        "Q33B random": result["q33b_comparison"]["q33b_positive_fraction"],
        "Q34 greedy": result["q33b_comparison"]["q34_positive_fraction"],
        "change": result["q33b_comparison"]["positive_fraction_delta"],
    },
])
comparison""",
            5,
            [display_frame(comparison)],
        ),
        markdown(
            """### Frozen-gate result

![Q34 geometry](Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_GEOMETRY.png)

Failed frozen gates:

"""
            + "\n".join(f"- `{gate}`" for gate in failed_gates)
        ),
        markdown(
            """## Takeaways

1. The untouched target gives a valid negative replication result.
2. A weak inward tendency survives, but Q33B's stronger routing advantage
   does not.
3. The unchanged rule is not invariant to random → greedy network ordering.
4. A network-identity or orientation-aware revision is now a new hypothesis
   requiring a newly frozen test; it cannot rescue Q34 retrospectively.
5. Q34 tests one local ARA route, not universal ARA, physical hardware,
   entanglement, Phase B or the dark sector.

## Data and validation caveats

The target is simulated and exactly diagonal in its sampled connected
correlations. Raw density-matrix reconstruction passed, but the validator
gate-checks saved cluster-bootstrap probabilities rather than redrawing them.
Event-weighted and equal-stratum effects are different estimands."""
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

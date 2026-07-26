"""Build an executed, reader-facing Q33B notebook from sealed artifacts."""

from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / ".q27_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import pandas as pd


OUTPUT = HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_NOTEBOOK.ipynb"


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
        (HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_RESULTS.json").read_text(
            encoding="utf-8"
        )
    )
    validation = json.loads(
        (HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_VALIDATION.json").read_text(
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
                "median exact minus comparator": evaluation[
                    "paired_differences"
                ][comparator]["median"],
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
    verdict = result["frozen_verdict"]["label"]

    cells = [
        markdown(
            f"""# Q33B — ARA-first boundary-child flow route

## tl;dr

Q33B keeps the ARA geometry fixed:

`2 + (1 + boundary child projected 1→0.5) = 3.5`.

It does not estimate `0.5` from energy. Instead, the geometry selects the one
endpoint child nearest the low boundary and predicts that relation closure
will rise after the high-side source releases.

Across 11,543 evaluation events, exact boundary flow was positive in 63.64%,
versus 55.83% for the sibling and 50.79–56.38% for controls. Every
trial-cluster bootstrap comparison gave probability 1.000.

Frozen verdict: **{verdict}**

Independent validation: **{validation["status"]}**."""
        ),
        markdown(
            r"""## Context & Methods

### Key assumptions

- ARA supplies invariant geometry; measured closure and energy are variable
  flows over it.
- The child singularity and parent ridge are the same adjacent-rung boundary.
- A complete boundary child projects from `1` locally to `0.5` in the parent.
- The source releases from high to low, so the endpoint child with smaller
  starting normalized closure is the directed recipient.

For each endpoint relation:

\[
z_c(t)=\frac{h_c(t)}{Q_{.95}^{dev}(h_c)},\qquad
g_c(t)=\frac{h_c(t+1)-h_c(t)}{Q_{.95}^{dev}(h_c)},
\quad h=|\det C|^{1/3}.
\]

Starting `z` selects the route without future values. Next `g` is the scored
flow. Sibling, topology, seed and time controls all apply the same lower-of-two
rule."""
        ),
        code(
            """from pathlib import Path
import json
import pandas as pd

ROOT = Path.cwd()
if not (ROOT / "Q33B_ARA_FIRST_BOUNDARY_CHILD_RESULTS.json").exists():
    ROOT = Path(r"F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\quantum")

result = json.loads((ROOT / "Q33B_ARA_FIRST_BOUNDARY_CHILD_RESULTS.json").read_text())
validation = json.loads((ROOT / "Q33B_ARA_FIRST_BOUNDARY_CHILD_VALIDATION.json").read_text())
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
            """The exact route is more reliably positive. The sibling has a
similar marginal median but a wider distribution, lower mean and lower
positive fraction."""
        ),
        markdown("### Paired comparisons"),
        code(
            """paired = pd.DataFrame([
    {
        "comparator": comparator,
        "median exact minus comparator": evaluation["paired_differences"][comparator]["median"],
        "cluster mean difference": result["evaluation_bootstrap"][comparator]["mean_exact_minus_comparator"],
        "bootstrap P(exact greater)": result["evaluation_bootstrap"][comparator]["probability_exact_greater"],
    }
    for comparator in ("sibling", "topology", "seed", "time")
])
paired""",
            3,
            [display_frame(paired)],
        ),
        markdown("### Branch replication"),
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
        markdown(
            """### Geometry

![Q33B geometry](Q33B_ARA_FIRST_BOUNDARY_CHILD_GEOMETRY.png)

All frozen routing gates passed. Controls confirm some generic lower-of-two
mean reversion, but the endpoint-specific boundary route retains an additional
7.26–12.85 percentage-point positive-flow advantage."""
        ),
        markdown(
            """## Takeaways

1. Keeping `0.5` structural rather than estimating it corrected Q33's
   coordinate error.
2. The fixed route successfully selects the more reliable closure-flow
   recipient inside this simulator.
3. The result is stable across `c2`, `c4`, development and evaluation.
4. It supports the directed boundary-child consequence, not a numerical
   derivation or independent test of `3.5`.
5. Raw energy flow does not show the same clean sibling ordering; the supported
   observable is relation closure.

## Caveats

This source is already-open, simulated and exactly diagonal. Lower-of-two
selection creates generic headroom, so same-rule controls are essential.
Starting distributions are not perfectly identical. This is not hardware
quantum evidence, universal ARA, Phase B or a dark-sector validation."""
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

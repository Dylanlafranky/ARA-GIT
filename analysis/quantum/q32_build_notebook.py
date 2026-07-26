"""Build an executed, rerunnable Q32 analysis notebook without Jupyter."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "Q32_EDGE_CHILD_POLE_HANDOVER_NOTEBOOK.ipynb"


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
        (ROOT / "Q32_EDGE_CHILD_POLE_HANDOVER_RESULTS.json").read_text(
            encoding="utf-8"
        )
    )
    validation = json.loads(
        (ROOT / "Q32_EDGE_CHILD_POLE_HANDOVER_VALIDATION.json").read_text(
            encoding="utf-8"
        )
    )
    lag_curve = pd.read_csv(ROOT / "Q32_EDGE_CHILD_POLE_HANDOVER_LAG_CURVE.csv")
    gradient = pd.read_csv(ROOT / "Q32_EDGE_CHILD_POLE_HANDOVER_GRADIENT.csv")
    evaluation_lags = lag_curve[lag_curve["split"] == "evaluation"][
        [
            "lag",
            "exact_gain_mean",
            "topology_gain_mean",
            "seed_gain_mean",
            "time_gain_mean",
        ]
    ]
    pooled_gradient = gradient[gradient["stratum"] == "pooled"][
        [
            "bin",
            "n",
            "gain_mean",
            "gain_median",
            "accumulation_mean",
            "positive_gain_fraction",
        ]
    ]

    summary = result["evaluation_selected_lag_summary"]
    primary = pd.DataFrame(
        [
            {
                "route": route,
                "starting_x_mean": summary[f"{route}_start_x_mean"],
                "signed_gain_mean": summary[f"{route}_gain_mean"],
                "overlap_mean": summary[f"{route}_overlap_mean"],
                "positive_gain_fraction": summary[
                    f"{route}_positive_gain_fraction"
                ],
            }
            for route in ("exact", "topology", "seed", "time")
        ]
    )

    cells = [
        markdown(
            """# Q32 edge-child pole handover

## tl;dr

The exact active child sharing the releasing source's named endpoint gained
more ARA relation amplitude at lag 1 than topology-, seed- and time-displaced
controls on 23,591 evaluation events. All incoming and coupling gates passed.

The child was not generally still at the low pole when source release was
observed: median starting `x=0.631` and 43.52% were at `x<=0.5`. Pole-near
children nevertheless gained most strongly, while crest-near children
released. Verdict: **ordered child transfer without pole-origin support**.

This is retrospective evidence inside one exactly diagonal public simulator,
not a fresh hardware confirmation or a completed 3.5 route."""
        ),
        markdown(
            """## Context & Methods

Q30 treated the triangle-closing relation as the ARA `1.5` leg. Q32 instead
tests the prerequisite Dylan identified: does an actual source-out/child-in
handover exist, and where does the child begin on its own `0–2`?

The child is selected only from its starting coordinate among active endpoint
relations. Development chooses the lag; evaluation keeps it unchanged.
Matched topology, seed and time routes use no future child outcome.

### Key assumptions

- Q27's determinant-closure coordinate is a useful local connection cut.
- Normalized movement can compare relation identities descriptively but is not
  literal conserved energy.
- The later half is an internal replication partition; the source was already
  opened in Q27–Q31."""
        ),
        code(
            """from pathlib import Path
import json
import pandas as pd

ROOT = Path.cwd()
if not (ROOT / "Q32_EDGE_CHILD_POLE_HANDOVER_RESULTS.json").exists():
    ROOT = Path(r"F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\quantum")

result = json.loads((ROOT / "Q32_EDGE_CHILD_POLE_HANDOVER_RESULTS.json").read_text())
validation = json.loads((ROOT / "Q32_EDGE_CHILD_POLE_HANDOVER_VALIDATION.json").read_text())
print("Selected lag:", result["selected_lag"])
print("Evaluation events:", result["event_counts"]["evaluation_selected_lag"])
print("Verdict:", result["verdict"])
print("Independent validation:", validation["validation"])""",
            1,
            [
                stream(
                    f'Selected lag: {result["selected_lag"]}\n'
                    f'Evaluation events: {result["event_counts"]["evaluation_selected_lag"]}\n'
                    f'Verdict: {result["verdict"]}\n'
                    f'Independent validation: {validation["validation"]}'
                )
            ],
        ),
        markdown("## Results\n\n### Route comparison at the frozen lag"),
        code(
            """summary = result["evaluation_selected_lag_summary"]
primary = pd.DataFrame([
    {
        "route": route,
        "starting_x_mean": summary[f"{route}_start_x_mean"],
        "signed_gain_mean": summary[f"{route}_gain_mean"],
        "overlap_mean": summary[f"{route}_overlap_mean"],
        "positive_gain_fraction": summary[f"{route}_positive_gain_fraction"],
    }
    for route in ("exact", "topology", "seed", "time")
])
primary""",
            2,
            [display_frame(primary)],
        ),
        markdown(
            """### Lag and starting-position geometry

![Q32 edge-child geometry](Q32_EDGE_CHILD_POLE_HANDOVER_GEOMETRY.png)

The exact route peaks at lag 1, then decays and reverses. The topology control
starts much nearer zero because it takes the minimum of several candidates;
that unequal order-statistic pressure is a disclosed protocol caveat. Exact
still beats both one-candidate seed/time controls and beats topology at lag 1."""
        ),
        code(
            """lag_curve = pd.read_csv(ROOT / "Q32_EDGE_CHILD_POLE_HANDOVER_LAG_CURVE.csv")
evaluation_lags = lag_curve[lag_curve["split"] == "evaluation"][[
    "lag", "exact_gain_mean", "topology_gain_mean",
    "seed_gain_mean", "time_gain_mean"
]]
evaluation_lags""",
            3,
            [display_frame(evaluation_lags)],
        ),
        markdown("### Children opened along their starting ARA gradient"),
        code(
            """gradient = pd.read_csv(ROOT / "Q32_EDGE_CHILD_POLE_HANDOVER_GRADIENT.csv")
pooled_gradient = gradient[gradient["stratum"] == "pooled"][[
    "bin", "n", "gain_mean", "gain_median",
    "accumulation_mean", "positive_gain_fraction"
]]
pooled_gradient""",
            4,
            [display_frame(pooled_gradient)],
        ),
        markdown(
            """## Takeaways

1. An immediate, endpoint-specific source-out/child-in relation is supported
   inside this simulator.
2. The measured child is commonly already beyond the pole at the source
   release slice, so this slice is probably late relative to the child's true
   origin.
3. Starting ARA position strongly orders the next movement: pole-side children
   gain; crest-side children release.
4. The next test should trace the same child backward before defining a revised
   1.5/3.5 path.
5. The result does not identify Phase B or a universal singularity flip."""
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

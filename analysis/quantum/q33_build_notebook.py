"""Build an executed, reader-facing Q33 notebook from sealed artifacts."""

from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / ".q27_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import pandas as pd


OUTPUT = HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_NOTEBOOK.ipynb"


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
        (HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_RESULTS.json").read_text(
            encoding="utf-8"
        )
    )
    validation = json.loads(
        (HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_VALIDATION.json").read_text(
            encoding="utf-8"
        )
    )
    trials = pd.read_csv(HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_TRIALS.csv")
    evaluation = result["splits"]["evaluation"]
    exact = evaluation["routes"]["exact"]

    headline = pd.DataFrame(
        [
            {
                "reading": "energy capacity",
                "median": exact["event_mean_capacity_ratio"]["median"],
                "ARA target": 0.5,
            },
            {
                "reading": "amplitude",
                "median": exact["event_mean_amplitude_ratio"]["median"],
                "ARA target": 0.5,
            },
            {
                "reading": "determinant closure scale",
                "median": exact["event_mean_closure_scale_ratio"]["median"],
                "ARA target": 0.5,
            },
            {
                "reading": "complete path",
                "median": exact["complete_path"]["median"],
                "ARA target": 3.5,
            },
            {
                "reading": "child origin local x",
                "median": exact["child_origin_x"]["median"],
                "ARA target": 0.5,
            },
            {
                "reading": "summed realised transfer",
                "median": exact["transfer_sum"]["median"],
                "ARA target": float("nan"),
            },
        ]
    )
    controls = pd.DataFrame(
        [
            {
                "control": control,
                "paired events": evaluation["routes"][control]["paired_events"],
                "median capacity ratio": evaluation["routes"][control][
                    "event_mean_capacity_ratio"
                ]["median"],
                "exact median-error advantage": result[
                    "evaluation_control_half_distance_advantage"
                ][control],
                "bootstrap P(exact better)": result["evaluation_bootstrap"][
                    control
                ]["probability_exact_lower"],
            }
            for control in ("topology", "seed", "time")
        ]
    )
    branch = pd.DataFrame(
        [
            {
                "branch": label,
                "events": evaluation["branches"][label]["source_events"],
                "median capacity ratio": evaluation["branches"][label][
                    "exact_event_mean_capacity_ratio"
                ]["median"],
                "median child-origin x": evaluation["branches"][label][
                    "exact_child_origin_x"
                ]["median"],
            }
            for label in ("c2", "c4")
        ]
    )
    trial_preview = trials[
        [
            "branch_label",
            "seed",
            "n_events",
            "exact_rho_mean",
            "topology_rho_mean",
            "seed_rho_mean",
            "time_rho_mean",
        ]
    ].head(12)

    verdict = result["frozen_verdict"]["label"]
    cells = [
        markdown(
            f"""# Q33 — Two-axis parent/child 3.5 projection

## tl;dr — post-result correction

Q33 attempted to operationalize the ARA path as
`2 + (1 + half-capacity child) = 3.5`, but a post-result audit found a
coordinate error.

The endpoint relations from Q32 did **not** have half the source's raw capacity in
the common parent-facing coordinate. Their median energy-capacity ratio was
`1.27349`, producing a median path of `4.27349`.

Backward tracing did recover a strong child-pole origin: median local
`x=0.04137`, with both children at `x<=0.5` in 81.50% of source events. Their
summed realised gain/source-loss ratio had median `1.03265`.

That raw result is reproducible, but raw capacity is variable flow over ARA,
not the fixed ARA rung coordinate. Q33 also averaged two endpoint recipients
where the declared route uses one boundary-nearest child. Therefore its frozen
negative verdict is **invalid as a pure ARA 3.5 test**.

Frozen implementation verdict: **{verdict}**

Independent validation: **{validation["status"]}**."""
        ),
        markdown(
            """## Context

Q30 tested a different `1.5` proxy. Q32 independently normalized every
relation onto its own local `0–2`, which was suitable for finding ordered
handover but erased cross-rung size.

Q33 preserves both:

- local ARA position for tracing the source crest and child pole;
- one common connected-relation energy unit for testing whether a recipient
  is actually half-sized in the source frame.

The source is the already-open Q27/Q28 public simulator cache. The later time
partition remains unchanged but is not fresh blind data."""
        ),
        markdown(
            r"""## Methods

For connected relation matrix \(C_p(t)\):

\[
h_p=|\det C_p|^{1/3},\qquad
x_p=\frac{2h_p}{Q_{.95}^{dev}(h_p)},
\]

\[
E_p=\lVert C_p\rVert_F^2,\qquad
\rho_{c\mid p}=
\frac{Q_{.95}^{dev}(E_c)}{Q_{.95}^{dev}(E_p)},
\qquad
L=3+\rho.
\]

Sources begin at `x>=1.5`, release on the next slice, and lose energy from a
backward-traced crest. The two active endpoint relations are traced backward
eight slices to their latest local minima.

Frozen controls:

- two topology-matched non-endpoint relations;
- endpoint relations at seed `+37`;
- endpoint relations at time `+137` inside the same split."""
        ),
        code(
            """from pathlib import Path
import json
import pandas as pd

ROOT = Path.cwd()
if not (ROOT / "Q33_TWO_AXIS_PARENT_CHILD_35_RESULTS.json").exists():
    ROOT = Path(r"F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\quantum")

result = json.loads((ROOT / "Q33_TWO_AXIS_PARENT_CHILD_35_RESULTS.json").read_text())
validation = json.loads((ROOT / "Q33_TWO_AXIS_PARENT_CHILD_35_VALIDATION.json").read_text())
evaluation = result["splits"]["evaluation"]
print("Evaluation source events:", evaluation["source_events"])
print("Exact child routes:", evaluation["exact_child_routes"])
print("Verdict:", result["frozen_verdict"]["label"])
print("Independent validation:", validation["status"])""",
            1,
            [
                stream(
                    f'Evaluation source events: {evaluation["source_events"]}\n'
                    f'Exact child routes: {evaluation["exact_child_routes"]}\n'
                    f"Verdict: {verdict}\n"
                    f'Independent validation: {validation["status"]}'
                )
            ],
        ),
        markdown("## Results\n\n### Capacity, path and pole readings"),
        code(
            """exact = evaluation["routes"]["exact"]
headline = pd.DataFrame([
    {"reading": "energy capacity", "median": exact["event_mean_capacity_ratio"]["median"], "ARA target": 0.5},
    {"reading": "amplitude", "median": exact["event_mean_amplitude_ratio"]["median"], "ARA target": 0.5},
    {"reading": "determinant closure scale", "median": exact["event_mean_closure_scale_ratio"]["median"], "ARA target": 0.5},
    {"reading": "complete path", "median": exact["complete_path"]["median"], "ARA target": 3.5},
    {"reading": "child origin local x", "median": exact["child_origin_x"]["median"], "ARA target": 0.5},
    {"reading": "summed realised transfer", "median": exact["transfer_sum"]["median"], "ARA target": float("nan")},
])
headline""",
            2,
            [display_frame(headline)],
        ),
        markdown(
            """The half-capacity reading fails under energy, amplitude and
determinant-closure scale. The pole-origin result succeeds strongly. The
transfer ratio is descriptive only because the simulator does not promise
local energy conservation."""
        ),
        markdown("### Branch stability"),
        code(
            """branch = pd.DataFrame([
    {
        "branch": label,
        "events": evaluation["branches"][label]["source_events"],
        "median capacity ratio": evaluation["branches"][label]["exact_event_mean_capacity_ratio"]["median"],
        "median child-origin x": evaluation["branches"][label]["exact_child_origin_x"]["median"],
    }
    for label in ("c2", "c4")
])
branch""",
            3,
            [display_frame(branch)],
        ),
        markdown("### Relation-broken controls"),
        code(
            """controls = pd.DataFrame([
    {
        "control": control,
        "paired events": evaluation["routes"][control]["paired_events"],
        "median capacity ratio": evaluation["routes"][control]["event_mean_capacity_ratio"]["median"],
        "exact median-error advantage": result["evaluation_control_half_distance_advantage"][control],
        "bootstrap P(exact better)": result["evaluation_bootstrap"][control]["probability_exact_lower"],
    }
    for control in ("topology", "seed", "time")
])
controls""",
            4,
            [display_frame(controls)],
        ),
        markdown(
            """Exact is more half-like than topology and seed controls, but
only 1.01% better than the time control with bootstrap probability 0.9395.
Both miss the frozen 5% and 0.95 gates."""
        ),
        markdown(
            """### Geometry

![Q33 geometry](Q33_TWO_AXIS_PARENT_CHILD_35_GEOMETRY.png)

The upper panels show that the capacity distribution centers beyond a
same-sized ratio of `1`, not at half capacity. The lower-left panel shows that
backward child origins are nevertheless concentrated near the local `0` pole."""
        ),
        markdown("### Trial-level preview"),
        code(
            """trials = pd.read_csv(ROOT / "Q33_TWO_AXIS_PARENT_CHILD_35_TRIALS.csv")
trial_preview = trials[[
    "branch_label", "seed", "n_events", "exact_rho_mean",
    "topology_rho_mean", "seed_rho_mean", "time_rho_mean"
]].head(12)
trial_preview""",
            5,
            [display_frame(trial_preview)],
        ),
        markdown(
            """## Takeaways

1. The corrected quantum `3.5` construction has now been tested directly.
2. Q32's endpoint relations are valid ordered recipients but are not shown to
   be one rung below the source.
3. Temporal child order and octave child size are separate empirical claims.
4. The near-pole origin and near-unity median summed transfer survive and
   sharpen the handover account.
5. A future `3.5` test must choose the single boundary-nearest child, apply the
   fixed `1 -> 0.5` octave projection and test a consequence of that route.

## Reproduction and assumptions

Run `q33_two_axis_parent_child_35_test.py`, then
`q33_validate_two_axis_parent_child_35.py`. All development scales are frozen
from `t=0..249`. No future child value selects a route.

This simulator is exactly diagonal and is not hardware quantum data. The
result validates a computational crosswalk inside this source, not universal
quantum mechanics or the dark-sector ratio."""
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

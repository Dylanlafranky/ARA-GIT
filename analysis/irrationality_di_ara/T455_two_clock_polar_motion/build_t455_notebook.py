"""Build and sequentially validate the reproducible T455 companion notebook.

The bundled analysis Python includes pandas/matplotlib but not nbformat or a
Jupyter kernel.  This writes the stable nbformat v4 JSON directly, then runs
every code cell in one shared namespace so the notebook is still tested from
top to bottom without adding an environment-only dependency.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
NOTEBOOK = ROOT / "T455_ANALYSIS.ipynb"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str, execution_count: int) -> dict:
    return {
        "cell_type": "code",
        "execution_count": execution_count,
        "metadata": {"validated_sequentially": True},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def main() -> None:
    raw_cells: list[tuple[str, str]] = [
        ("markdown",
            "# T455 — Two clocks and geographic polar motion\n\n"
            "## tl;dr\n\n"
            "The exact atomic/Earth-rotation clock relation remains almost exactly on the ARA ridge. "
            "The geographic-pole traversal child recovers a stable approximately annual wave at 30- and 90-day grains. "
            "The full frozen predictive claim passes only 3/6 gates. A Di-ARA-only child helps longer-horizon forecasts, "
            "but a one-year-shifted child performs similarly, so most of that structure belongs to an annual parent carrier."
        ),
        ("markdown",
            "## Context & methods\n\n"
            "**Who:** Earth. **What:** SI atomic day versus observed Earth-rotation day, plus geographic polar motion. "
            "**When:** daily IERS EOP C04 observations from 1984-01-01 through 2026-07-29. "
            "**Where:** parent two-clock ridge → geographic-pole amount/traversal child. "
            "**Why:** ask whether the same relational child supplies timing information at 1, 7, 30 and 90 days. "
            "**How:** frozen chronological splits, exact 0–2 clock relation, typed pole Irrationality Di-ARA, causal forecasts, "
            "false-time controls and moving-block bootstrap. The same-season audit is explicitly post-result."
        ),
        ("code",
            "from pathlib import Path\n"
            "import json\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n\n"
            f"ROOT = Path(r'{ROOT}')\n"
            "RESULTS = ROOT / 'results'\n"
            "windows = pd.read_csv(RESULTS/'T455_SCALE_WINDOWS.csv', parse_dates=['start_date','end_date'])\n"
            "metrics = pd.read_csv(RESULTS/'T455_FORECAST_METRICS.csv')\n"
            "controls = pd.read_csv(RESULTS/'T455_FALSE_TIME_CONTROLS.csv')\n"
            "geometry = pd.read_csv(RESULTS/'T455_SCALE_GEOMETRY.csv')\n"
            "quadrants = pd.read_csv(RESULTS/'T455_QUADRANT_OCCUPANCY.csv')\n"
            "seasonal = pd.read_csv(RESULTS/'T455_POSTHOC_SEASONAL_AUDIT.csv')\n"
            "result = json.loads((RESULTS/'T455_RESULT.json').read_text())\n"
            "print(result)"
        ),
        ("markdown", "## Data\n\nThe exact clock coordinate is shown without rescaling; the magnified panel reports only its nanounit distance from the ARA ridge."),
        ("code",
            "fig, ax = plt.subplots(2, 1, figsize=(12, 7), sharex=True)\n"
            "daily = windows[windows.scale_days.eq(1)]\n"
            "ax[0].plot(daily.end_date, daily.clock_ara, lw=.7, color='#4ea3ff')\n"
            "ax[0].axhline(1, color='white', ls='--', lw=1)\n"
            "ax[0].set_ylabel('Exact two-clock ARA (0–2)')\n"
            "ax[0].set_title('Earth-clock relation remains on the ARA ridge')\n"
            "ax[1].plot(daily.end_date, daily.clock_ridge_nano, lw=.7, color='#ff9f43')\n"
            "ax[1].axhline(0, color='white', ls='--', lw=1)\n"
            "ax[1].set_ylabel('(ARA − 1) × 10⁹')\n"
            "ax[1].set_xlabel('Observation date')\n"
            "plt.tight_layout(); plt.show()"
        ),
        ("markdown", "## Results\n\nThe child geometry becomes more coherent as the observational grain grows. This is a scale relation, not a universal landmark forced at every grain."),
        ("code",
            "fig, axes = plt.subplots(1, 2, figsize=(13, 5))\n"
            "for scale, color in [(30, '#4ea3ff'), (90, '#ff9f43')]:\n"
            "    d = windows[windows.scale_days.eq(scale)].dropna(subset=['pole_amount_ara','pole_traversal_ara'])\n"
            "    axes[0].scatter(d.pole_amount_ara, d.pole_traversal_ara, s=11, alpha=.45, label=f'{scale}-day')\n"
            "axes[0].axvline(1, color='grey', ls='--'); axes[0].axhline(1, color='grey', ls='--')\n"
            "axes[0].set(xlabel='Pole amount ARA (0–2)', ylabel='Pole traversal ARA (0–2)', title='Coarse-grain Irrationality Di-ARA')\n"
            "axes[0].legend()\n"
            "for split, g in geometry.groupby('split'):\n"
            "    axes[1].plot(g.scale_days, g.median_traversal_ara, marker='o', label=split)\n"
            "axes[1].axhline(1, color='grey', ls='--')\n"
            "axes[1].set(xscale='log', xlabel='Grain (days, log scale)', ylabel='Median traversal ARA', title='Traversal orientation by grain')\n"
            "axes[1].legend()\n"
            "plt.tight_layout(); plt.show()"
        ),
        ("code",
            "hold = metrics[metrics.split.eq('holdout')]\n"
            "clock = hold[hold.model.eq('clock_only')][['scale_days','horizon_windows','mae']].rename(columns={'mae':'clock_mae'})\n"
            "cand = hold[hold.model.isin(['clock_pole_diara','full_child'])].merge(clock, on=['scale_days','horizon_windows'])\n"
            "cand['improvement_pct'] = 100*(cand.clock_mae-cand.mae)/cand.clock_mae\n"
            "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n"
            "for (model, horizon), g in cand.groupby(['model','horizon_windows']):\n"
            "    axes[0].plot(g.scale_days, g.improvement_pct, marker='o', label=f'{model}, h={horizon}')\n"
            "axes[0].axhline(0, color='grey', ls='--'); axes[0].set_xscale('log')\n"
            "axes[0].set(xlabel='Grain (days)', ylabel='Holdout MAE improvement over clock-only (%)', title='Frozen prospective result')\n"
            "axes[0].legend(fontsize=8)\n"
            "c = controls[(controls.candidate_model.eq('clock_pole_diara')) & controls.horizon_windows.eq(4)]\n"
            "for name, g in c.groupby('control'):\n"
            "    axes[1].plot(g.scale_days, g.improvement_vs_clock_pct, marker='o', label=name)\n"
            "axes[1].axhline(0, color='grey', ls='--'); axes[1].set_xscale('log')\n"
            "axes[1].set(xlabel='Grain (days)', ylabel='Improvement over clock-only (%)', title='Four-window false-time controls')\n"
            "axes[1].legend(fontsize=8)\n"
            "plt.tight_layout(); plt.show()"
        ),
        ("code",
            "fig, ax = plt.subplots(figsize=(10, 5))\n"
            "for horizon, g in seasonal.groupby('horizon_windows'):\n"
            "    ax.plot(g.scale_days, g.diara_improvement_over_season_pct, marker='o', label=f'{horizon} window(s)')\n"
            "ax.axhline(0, color='grey', ls='--'); ax.set_xscale('log')\n"
            "ax.set(xlabel='Grain (days)', ylabel='Live Di-ARA improvement over same-season baseline (%)', title='Post-result seasonal-parent diagnostic')\n"
            "ax.legend(); plt.tight_layout(); plt.show()"
        ),
        ("markdown",
            "## Takeaways\n\n"
            "1. The exact two-clock parent is a genuine ridge-level relation.\n"
            "2. The pole child reconstructs an annual directional wave at 30–90 day grains.\n"
            "3. The full frozen prospective claim does not transfer across grains.\n"
            "4. The relational Di-ARA child is more useful than raw pole position, especially over longer horizons.\n"
            "5. A one-year-shifted control carries nearly the same broad signal, so the annual parent must be removed before claiming a live timing handover.\n"
            "6. The next confirmation should freeze live-minus-same-season prediction and preserve signed traversal orientation."
        ),
    ]

    namespace: dict = {}
    execution_count = 0
    cells: list[dict] = []
    for kind, source in raw_cells:
        if kind == "markdown":
            cells.append(markdown(source))
            continue
        execution_count += 1
        exec(compile(source, f"T455_ANALYSIS cell {execution_count}", "exec"), namespace)
        cells.append(code(source, execution_count))

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
            "t455_validation": {
                "method": "all code cells executed sequentially in the bundled analysis Python",
                "code_cells": execution_count,
                "passed": True,
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
    print(NOTEBOOK)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the dependency-light T382 reproducibility notebook."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT = HERE / "T382_ral_silver_detector_share" / "T382_DETECTOR_SHARE_RESULTS.json"
OUT = HERE / "T382_RAL_SILVER_DETECTOR_SHARE_REPRODUCTION.ipynb"


def markdown(text: str):
    return {"cell_type": "markdown", "metadata": {}, "source": [line + "\n" for line in text.splitlines()]}


def code(text: str):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": [line + "\n" for line in text.splitlines()]}


result = json.loads(RESULT.read_text(encoding="utf-8"))
notebook = {
    "cells": [
        markdown(f"""# T382 — RAL Silver ARA-native detector-share test

## TL;DR

**Frozen verdict:** `{result['status']}`.

The detector-summed population parent passed at τ = {result['parent']['tau_us']:.6f} μs. The
calibration-frozen 96-detector child did not pass its validation/holdout and
detector-map controls, so C06 is not interpreted as child-mediated decay
timing. C16 is unavailable because the archive contains aggregate histograms,
not individually linked muons and daughters.

This notebook is the reviewable companion to the executed Python module. It
keeps ARA parent, native child, projected child, and established-physics
crosswalks separate."""),
        markdown("""## Who / what / when / where / why / how

- **Who/where:** untouched RAL Silver runs from ISIS EMU study 10.5286/ISIS.E.RB1620201.
- **What:** population parent and a calibration-frozen 96-detector traversal child.
- **When:** native 0.016 μs bins in the frozen 0.25–8.00 μs analysis window.
- **Why:** test child-native `0→2→0`, projection to the parent ridge, and advance information without relabelling detector amplitudes as individual muons.
- **How:** calibration/validation/holdout field ladder, no-phase/reverse/detector-shift controls, bootstrap and bin sensitivity.
"""),
        code("""from pathlib import Path
import json
import pandas as pd
import sys

HERE = Path.cwd() / 'analysis' / 'muon'
sys.path.insert(0, str(HERE))
SCRIPT = HERE / 't382_ral_silver_detector_share.py'
OUT = HERE / 'T382_ral_silver_detector_share'
SEED = 382
CALIBRATION = {'EMU00066572':20, 'EMU00066573':25, 'EMU00066574':20,
               'EMU00066575':25, 'EMU00066576':20, 'EMU00066577':25}
VALIDATION = {'EMU00066571':25, 'EMU00066584':20}
HOLDOUT = {'EMU00066578':63, 'EMU00066579':160, 'EMU00066580':400}
DIAGNOSTIC = {'EMU00066581':1000, 'EMU00066582':2000, 'EMU00066583':4000}
"""),
        markdown("""## Reproduce the frozen execution

The next cell deliberately runs the versioned module rather than duplicating
analysis code inside the notebook. It takes roughly 15–45 seconds with the
bundled Python runtime."""),
        code("""import runpy
runpy.run_path(str(SCRIPT), run_name='__main__')
"""),
        code("""result = json.loads((OUT / 'T382_DETECTOR_SHARE_RESULTS.json').read_text())
validation = json.loads((OUT / 'T382_DETECTOR_SHARE_VALIDATION.json').read_text())
runs = pd.read_csv(OUT / 'T382_DETECTOR_SHARE_RUNS.csv')
bins = pd.read_csv(OUT / 'T382_DETECTOR_SHARE_BIN_SENSITIVITY.csv')
result['status'], result['gates']
"""),
        markdown("""## Data-quality and construct checks

File hashes, native-bin checks, nonnegative/integer count checks and detector
coverage are in the validation JSON. The source is Class P: population
histograms. This supports population and detector-relation cuts but not an
individual-muon prediction claim."""),
        code("""assert validation['all_data_quality_pass']
assert validation['individual_prediction_available'] is False
pd.DataFrame(validation['data_quality_by_run']).T
"""),
        markdown("""## ARA and physics views side by side

- ARA parent: `xP(t)=2(1-exp(-t/tau))`; its ridge is `tau*ln(2)`.
- ARA child: `xC(t)=1-cos(theta)`; the projected child is `xC/2`.
- Physics crosswalk: `theta=2*pi*gamma*B*t+phi0` from the detector-share phase relation.

The golden-ratio or any other irrationality coordinate is not inserted into
this test."""),
        code("""runs[['run','split','field_g','detector_child_gain','reverse_gain',
      'free_gamma_mhz_per_g','phase_at_parent_ridge_rad']]
"""),
        code("""bins.groupby('factor', as_index=False)['improvement'].mean()
"""),
        markdown("""## Takeaway

The parent cut is strong and reproducible. The candidate child cadence is
numerically close to the later-revealed muon reference, but the frozen spatial
relation does not generalize: it loses to the no-phase model on primary
holdouts and does not beat detector-map controls. That combination is a useful
source qualification result, not a neutrino-timing result."""),
    ],
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
OUT.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
print(OUT)

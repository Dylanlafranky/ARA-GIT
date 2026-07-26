"""Build and execute the durable Q28 analytical notebook.

The notebook reads frozen Q28 outputs only. Raw extraction and numerical
analysis remain in q28_ara9_interlocking_rotational_transport_test.py.
"""

from __future__ import annotations

import asyncio
import json
import os
import pathlib
import sys


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / ".q27_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

RUNTIME = HERE / ".q28_jupyter"
IPYTHON_DIR = RUNTIME / "ipython"
JUPYTER_DATA = RUNTIME / "data"
JUPYTER_CONFIG = RUNTIME / "config"
for directory in (IPYTHON_DIR, JUPYTER_DATA, JUPYTER_CONFIG):
    directory.mkdir(parents=True, exist_ok=True)
os.environ["IPYTHONDIR"] = str(IPYTHON_DIR)
os.environ["JUPYTER_DATA_DIR"] = str(JUPYTER_DATA)
os.environ["JUPYTER_CONFIG_DIR"] = str(JUPYTER_CONFIG)

kernel_dir = JUPYTER_DATA / "kernels" / "python3"
kernel_dir.mkdir(parents=True, exist_ok=True)
(kernel_dir / "kernel.json").write_text(
    json.dumps(
        {
            "argv": [
                sys.executable,
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}",
            ],
            "display_name": "Python 3 (Q28 isolated)",
            "language": "python",
        },
        indent=2,
    ),
    encoding="utf-8",
)

import nbformat
from nbclient import NotebookClient


OUTPUT = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_NOTEBOOK.ipynb"


def code(source: str):
    return nbformat.v4.new_code_cell(source.strip())


def markdown(source: str):
    return nbformat.v4.new_markdown_cell(source.strip())


def main() -> None:
    notebook = nbformat.v4.new_notebook()
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook["metadata"]["language_info"] = {"name": "python", "version": "3"}
    notebook["cells"] = [
        markdown(
            """
# Q28 — ARA^9 Interlocking Rotational Transport

## TL;DR

The checksum-frozen result is **INCONCLUSIVE**, not a confirmation of an
angled rotational pivot.

What survived on the hidden time half:

- the full oriented relation fitted its later neighbour web much better after
  an allowed 0°/180° reorientation than with positive scaling alone:
  residual `0.1016` versus `0.5462`, an `81.39%` reduction;
- the exact trajectory beat displaced-seed and displaced-time controls in all
  2,000 paired trial bootstraps;
- development selected lag 2, and the hidden half independently reached its
  minimum at lag 2;
- singular-value shape retention was `0.9918`.

Why the claim is not supported:

- only 76,393 hidden events survived, below the frozen 100,000-event gate;
- every source relation is exactly diagonal and symmetric in this simulator;
- endpoint reversal therefore changes nothing, so the mandatory
  shared-endpoint control fails exactly;
- fitted angles are only 0° or 180°, not a continuous angled rotational point.
"""
        ),
        markdown(
            """
## Context & Methods

Q27 found a weaker ordered release-to-neighbour accumulation relation but no
stable determinant-orientation flip. Q28 tested the user's ARA hypothesis that
the larger pattern may instead be an interlocking web travelling around a
rotational point.

For each two-qubit pair, Q28 retains the complete connected 3×3 relation
`C = T - a bᵀ`. A source release at time `t` is compared with the
accumulation-weighted web of active pairs sharing one endpoint at time
`t + lag`. The only fitted transformation is one proper SO(3) rotation plus a
positive scale. Development times 0–241 selected one lag from 1–8; hidden
times 250–491 evaluated that frozen lag.

Controls use no rotation, the opposite endpoint, a seed displacement, a time
displacement, and zero lag. This source was already opened by Q27, so Q28 is
registered but not blind.
"""
        ),
        code(
            """
from pathlib import Path
from IPython.display import Image, display
import csv
import json

HERE = Path.cwd()
if not (HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_RESULTS.json").exists():
    HERE = Path(r"F:/SystemFormulaFolder/GIT/ARA-GIT/analysis/quantum")

results = json.loads(
    (HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_RESULTS.json").read_text(
        encoding="utf-8"
    )
)
validation = json.loads(
    (HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_VALIDATION.json").read_text(
        encoding="utf-8"
    )
)
assert validation["status"] == "PASS"
assert validation["checks_passed"] == validation["checks_total"] == 38
assert results["verdict"] == "INCONCLUSIVE"
print("Independent validation:", validation["status"], "38/38")
print("Frozen verdict:", results["verdict"])
print("Development-selected lag:", results["selected_lag"])
"""
        ),
        markdown("## Data"),
        code(
            """
print("DOI:", results["source"]["doi"])
print("HDF5 SHA-256:", results["source"]["hdf5_sha256"])
print("Protocol SHA-256:", results["source"]["protocol_sha256"])
print("Evidence tier:", results["source"]["evidence_tier"])
print("Connected matrices:", 2 * 100 * 500 * 66)
print("Hidden eligible events:", results["hidden"]["pooled"]["events"])
for key, value in results["source_quality"].items():
    print(f"{key}: {value}")
"""
        ),
        markdown("## Results"),
        code(
            """
h = results["hidden"]["pooled"]
summary = {
    "rotation residual": h["rotation_error"],
    "no-rotation residual": h["no_rotation_error"],
    "rotation gain": h["rotation_gain"],
    "wrong-endpoint residual": h["wrong_endpoint_error"],
    "seed-displaced residual": h["seed_error"],
    "time-displaced residual": h["time_error"],
    "zero-lag residual": h["lag_zero_error"],
    "shape similarity": h["spectrum_similarity"],
}
for label, value in summary.items():
    print(f"{label:28s} {value:.6f}")
"""
        ),
        code(
            """
display(
    Image(
        filename=str(
            HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_GEOMETRY.png"
        )
    )
)
"""
        ),
        markdown(
            """
### What the figure says

The top-left panel shows a strong relation that is lost if the sign-oriented
state is flattened into positive scaling only. Exact time and seed identity
matter. But the correct- and wrong-endpoint bars coincide because the complete
source matrices are diagonal and symmetric.

The top-right panel is the cleanest travelling result: development selects lag
2 and the independently evaluated hidden half has the same minimum. The
bottom-left panel shows why this is not evidence for an oblique pivot: the
allowed rotations collapse to 0° and 180°. The worked trajectory shows
release and neighbour accumulation recurring through time, with the fitted
binary orientation overlaid.
"""
        ),
        code(
            """
for gate, passed in results["gates"].items():
    print(f"{gate:48s} {'PASS' if passed else 'FAIL'}")
"""
        ),
        markdown(
            """
## ARA and established-physics readings

| ARA reading | Established quantum/data reading |
|---|---|
| The larger web retains a recurring phase/flip relation that a scalar closure cut discarded. | Keeping the full connected-correlation block retains sign structure lost by `abs(det C)`. |
| Release is followed most cleanly by neighbour-web accumulation two slices later. | A development-selected lag-2 association replicates on the hidden half and beats zero lag. |
| The observed movement is a 0↔2-style singularity flip, not yet the proposed angled interlock. | This simulator's connected blocks are diagonal; proper fits therefore reduce to 0°/180° sign reorientations. |
| Interlocking through a named shared endpoint remains unresolved. | Matrix transpose is identical here, making the correct- versus wrong-endpoint test non-identifiable. |

The geometry verdict is therefore narrower than the frozen claim: **binary
phase-flip transport survives; continuous angled interlocking is not tested by
this source**.
"""
        ),
        markdown(
            """
## Evidence boundary and next test

This is complete public simulated data and an independently validated frozen
analysis, but the source had already been opened by Q27. It does not establish
hardware behaviour, a new quantum law, or universal fractality.

The next decisive dataset must expose non-zero off-diagonal connected
correlations in a fixed shared coordinate frame. Only then can endpoint
reversal differ from the intended shared endpoint, and only then can a
continuous rotation angle be measured rather than forced into 0°/180°.
"""
        ),
        markdown(
            """
## Reproduction

From `analysis/quantum`, using the bundled Python environment with
`.q27_deps` on `PYTHONPATH`:

```powershell
python q28_ara9_interlocking_rotational_transport_test.py extract --workers 6
python q28_ara9_interlocking_rotational_transport_test.py analyse
python q28_ara9_interlocking_rotational_transport_validate.py
python q28_build_notebook.py
```

The 237.6 MB derived matrix cache is excluded from Git and recreated from the
checksum-locked Q27 public source.
"""
        ),
    ]

    client = NotebookClient(
        notebook,
        timeout=300,
        startup_timeout=180,
        kernel_name="python3",
        resources={"metadata": {"path": str(HERE)}},
    )
    executed = client.execute()
    nbformat.write(executed, OUTPUT)
    print(f"Executed notebook written: {OUTPUT}")


if __name__ == "__main__":
    main()

"""Build and execute the durable Q29 analytical notebook."""

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
NOTEBOOK_DEPS = HERE / ".q27_notebook_deps"
if NOTEBOOK_DEPS.exists():
    # Keep the CPython-3.12 notebook stack ahead of the mixed scientific cache.
    sys.path.insert(0, str(NOTEBOOK_DEPS))
os.environ["PYTHONPATH"] = os.pathsep.join(
    str(path)
    # The kernel needs the complete IPython/Pygments copies in LOCAL_DEPS;
    # the builder itself keeps NOTEBOOK_DEPS first for CPython-3.12 rpds.
    for path in (LOCAL_DEPS, NOTEBOOK_DEPS)
    if path.exists()
)

RUNTIME = HERE / ".q29_jupyter"
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
            "display_name": "Python 3 (Q29 isolated)",
            "language": "python",
        },
        indent=2,
    ),
    encoding="utf-8",
)

import nbformat
from nbclient import NotebookClient

OUTPUT = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_NOTEBOOK.ipynb"


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
# Q29 — Nature of the ARA^9 Unclassified Component

## Answer first

The Q28 remainder is **not identified as Phase B** and is not an
independently coherent travelling counterpart.

The validated descriptive result is:

> **Local signed z-axis handover memory; no stable counterpart detected.**

The remainder is strongly one-dimensional, remembers the exact trajectory for
roughly one to three slices, and stays unusually attached to the source
endpoint neighbourhood. Its complete vector shape and partner identity do not
persist.
"""
        ),
        markdown(
            """
## Question and controls

Q29 distinguishes three possibilities:

1. a coherent counterpart with complete-shape recurrence and one stable partner;
2. a child-mediated local correction attached to nearby endpoint relations;
3. an unstructured residual that does not beat displaced controls.

The source was already open. Exact, seed-displaced, and time-displaced searches
receive equal candidate counts. The axis-native check uses the signed
`z / target norm` remainder, permits direct or sign-flipped recurrence, and
fits no scale.
"""
        ),
        code(
            """
from pathlib import Path
from IPython.display import Image, display
import csv
import json

HERE = Path.cwd()
if not (HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_RESULTS.json").exists():
    HERE = Path(r"F:/SystemFormulaFolder/GIT/ARA-GIT/analysis/quantum")

results = json.loads(
    (HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_RESULTS.json").read_text(
        encoding="utf-8"
    )
)
validation = json.loads(
    (HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_VALIDATION.json").read_text(
        encoding="utf-8"
    )
)
assert validation["status"] == "PASS"
assert validation["checks_passed"] == validation["checks_total"] == 38
assert "PHASE-B" not in results["descriptive_lean"].upper()
print("Independent validation:", validation["status"], "38/38")
print("Descriptive result:", results["descriptive_lean"])
"""
        ),
        markdown("## Core measurements"),
        code(
            """
p = results["pooled"]
a = results["axis_native_surfer"]["pooled"]
summary = {
    "eligible events": p["events"],
    "Q28 unexplained fraction": p["residual_fraction"],
    "largest-axis energy share": p["residual_largest_axis_share"],
    "positive accumulating children/event": p["positive_child_count"],
    "full-shape exact error": p["origin_exact_error"],
    "full-shape seed error": p["origin_seed_error"],
    "axis exact error, pooled": a["exact_error"],
    "axis seed error, pooled": a["seed_error"],
    "axis time error, pooled": a["time_error"],
    "exact endpoint share": a["exact_shares_source_endpoint"],
    "seed endpoint share": a["seed_shares_source_endpoint"],
    "time endpoint share": a["time_shares_source_endpoint"],
    "exact partner persistence": a["exact_partner_persistence"],
    "seed partner persistence": a["seed_partner_persistence"],
    "time partner persistence": a["time_partner_persistence"],
}
for label, value in summary.items():
    if isinstance(value, float):
        print(f"{label:40s} {value:.6f}")
    else:
        print(f"{label:40s} {value}")
"""
        ),
        markdown("## Complete-shape and lattice view"),
        code(
            """
display(
    Image(
        filename=str(
            HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_GEOMETRY.png"
        )
    )
)
"""
        ),
        markdown(
            """
The complete three-coordinate remainder is a poor travelling match: exact
shape error is slightly worse than the displaced controls. Its first match is
nevertheless much more likely to share the original endpoint. Route partner
persistence is control-like. This rejects the strong “whole coherent
counterpart” reading on this source.
"""
        ),
        markdown("## Axis-native view"),
        code(
            """
display(
    Image(
        filename=str(
            HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_AXIS_SURFER.png"
        )
    )
)
"""
        ),
        code(
            """
with (HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_AXIS_SURFER_LAG_CURVE.csv").open(
    "r", encoding="utf-8", newline=""
) as stream:
    lag_rows = list(csv.DictReader(stream))

by_key = {(row["control"], int(row["lag"])): row for row in lag_rows}
print("lag | exact    seed     time")
for lag in range(1, 7):
    values = [
        float(by_key[(control, lag)]["axis_error"])
        for control in ("exact", "seed", "time")
    ]
    print(f"{lag:3d} | {values[0]:.6f} {values[1]:.6f} {values[2]:.6f}")
"""
        ),
        markdown(
            """
The signed coordinate has a strong lag-1 echo: error `0.1865` versus roughly
`0.469` for both controls. The advantage weakens at lags 2–3 and is gone by
lags 4–6. Endpoint association remains enriched, but no one partner persists
above both controls.

This supports a **short-lived local handover memory**, not a full Phase-B
identity.
"""
        ),
        markdown(
            """
## ARA and established-data crosswalk

| ARA reading | Established mathematical/data reading |
|---|---|
| A narrow directional remainder survives the Q28 handover. | 94.6% of residual squared magnitude occupies z. |
| It remembers one child step. | Exact signed-axis recurrence strongly beats controls at lag 1. |
| It stays near the same local coupling boundary. | Exact routes share the source endpoint more often than controls. |
| A complete Phase B has not been isolated. | Full-vector recurrence and stable-partner persistence fail. |

The `z` label is a simulator coordinate, not a claimed universal physical
direction.
"""
        ),
        markdown(
            """
## Evidence boundary and next test

This source is public and fully reproducible, but it is simulated, already
opened, and exactly diagonal. Q29 does not establish a hidden physical wave or
new quantum entity.

The decisive next source must contain non-zero off-diagonal connected
relations in a fixed shared coordinate frame. A Phase-B interpretation should
be frozen to require complete-shape recurrence, stable partner identity,
endpoint-route persistence, signed return, and independent TE-ARA closure.
"""
        ),
        markdown(
            """
## Reproduction

```powershell
python q29_ara9_unclassified_component_surfer_exploration.py
python q29_validate_unclassified_component_surfer.py
python q29_build_notebook.py
```

The first command reconstructs all result tables and both figures from the
Q27/Q28 derived public-source caches. The second independently recomputes raw
events and validates 38 checks. This notebook reads only those frozen outputs.
"""
        ),
    ]

    client = NotebookClient(
        notebook,
        timeout=120,
        kernel_name="python3",
        resources={"metadata": {"path": str(HERE)}},
    )
    executed = client.execute(cwd=str(HERE))
    nbformat.write(executed, OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()

"""Build and execute the durable Q30 analytical notebook."""

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
NOTEBOOK_DEPS = HERE / ".q27_notebook_deps"
for path in (LOCAL_DEPS, NOTEBOOK_DEPS):
    if path.exists():
        sys.path.insert(0, str(path))
os.environ["PYTHONPATH"] = os.pathsep.join(
    str(path) for path in (LOCAL_DEPS, NOTEBOOK_DEPS) if path.exists()
)
runtime = HERE / ".q29_jupyter"
for name in ("ipython", "data", "config"):
    (runtime / name).mkdir(parents=True, exist_ok=True)
os.environ["IPYTHONDIR"] = str(runtime / "ipython")
os.environ["JUPYTER_DATA_DIR"] = str(runtime / "data")
os.environ["JUPYTER_CONFIG_DIR"] = str(runtime / "config")
kernel_dir = runtime / "data" / "kernels" / "python3"
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
            "display_name": "Python 3 (Q30 isolated)",
            "language": "python",
        },
        indent=2,
    ),
    encoding="utf-8",
)

import nbformat
from nbclient import NotebookClient

OUTPUT = HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_NOTEBOOK.ipynb"


def markdown(source: str):
    return nbformat.v4.new_markdown_cell(source.strip())


def code(source: str):
    return nbformat.v4.new_code_cell(source.strip())


def main() -> None:
    notebook = nbformat.v4.new_notebook()
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook["cells"] = [
        markdown(
            """
# Q30 — ARA 1.5 / 3.5 Out-of-Cut Route

## Answer first

The frozen triangle-closing interpretation of the ARA `1.5` and `3.5` routes
was **not supported** on the opened Q29 simulator source.

At the handover, the exact closing edge recovered only about 2.5% of the
unresolved component and performed slightly worse than seed- and
time-displaced closing edges. At lags 4–6 it gained a small but stable
0.28–0.29% advantage, far below the frozen 5% continuation gate.

This rejects this route implementation on this source; it does not reject the
general ARA 1.5/3.5 concept or establish that no out-of-cut route exists.
"""
        ),
        markdown(
            """
## Frozen translation

For source `(u,e)` and child `(e,v)`, the test used the unique third
Information³ relation `(u,v)`.

- `1.5`: the perpendicular closing leg `(u,v)`;
- `3.5 = 2 + 1.5`: the complete source span followed by that closing leg.

The route was specified before Q30 outcomes and was never folded modulo two.
Every control received one relation, four proper sign flips, and one
non-negative scale.
"""
        ),
        code(
            """
from pathlib import Path
from IPython.display import Image, display
import csv
import json

HERE = Path.cwd()
if not (HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_RESULTS.json").exists():
    HERE = Path(r"F:/SystemFormulaFolder/GIT/ARA-GIT/analysis/quantum")

results = json.loads(
    (HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_RESULTS.json").read_text(
        encoding="utf-8"
    )
)
validation = json.loads(
    (HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_VALIDATION.json").read_text(
        encoding="utf-8"
    )
)
assert validation["status"] == "PASS"
assert validation["passed"] == validation["total"] == 213
print("Independent validation: PASS 213/213")
print("Verdict:", results["verdict"])
"""
        ),
        markdown("## Main geometry and results"),
        code(
            """
display(
    Image(
        filename=str(
            HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_GEOMETRY.png"
        )
    )
)
"""
        ),
        code(
            """
later = results["opened_later_half"]
lag0 = later["lag0"]
late = later["late_lags_4_to_6"]
print("Lag-0 exact 1.5 error:", lag0["exact_closure"]["residual_error"])
print("Lag-0 exact recovery:", lag0["exact_closure"]["residual_recovery"])
print("Lag-0 seed error:", lag0["seed"]["residual_error"])
print("Lag-0 time error:", lag0["time"]["residual_error"])
print("Late exact error:", late["exact_closure"]["residual_error"])
print("Late seed error:", late["seed"]["residual_error"])
print("Late time error:", late["time"]["residual_error"])
print("Frozen gates:", results["gates"])
"""
        ),
        markdown(
            """
## Interpretation

The exact closing edge is not the missing component at its proposed handover:
it recovers less than the displaced relations and less than the direct child.
The late exact edge is consistently but only minutely better than the
displaced controls. That weak delayed association is recorded as an
exploratory trace, not promoted to the 1.5/3.5 route.

The strongest remaining source limitation is exact diagonality. A source with
nonzero off-diagonal relations is still required to test a genuine
perpendicular continuation and stable Phase-B identity.
"""
        ),
        markdown(
            """
## Reproduction

```powershell
python q30_ara15_35_out_of_cut_route_exploration.py
python q30_validate_ara15_35_out_of_cut_route.py
python q30_build_notebook.py
```

Use the repository's Python 3.12 environment because the local Q27 scientific
cache contains CPython-3.12 binary packages.
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

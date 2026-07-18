"""Execute every MX5 notebook code cell sequentially for audit validation."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import nbformat


matplotlib.use("Agg")
HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "MX5_CHILD_ARA_TEARA_CLOSURE_NOTEBOOK.ipynb"

notebook = nbformat.read(NOTEBOOK, as_version=4)
nbformat.validate(notebook)
namespace: dict = {"__name__": "__mx5_notebook_validation__"}
executed = 0
for index, cell in enumerate(notebook.cells):
    if cell.cell_type != "code":
        continue
    exec(compile(cell.source, f"{NOTEBOOK.name}:cell-{index}", "exec"), namespace)
    executed += 1

record = {
    "notebook": str(NOTEBOOK),
    "cell_count": len(notebook.cells),
    "code_cells_executed": executed,
    "execution_pass": True,
    "execution_method": (
        "sequential single-process validation because a registered Jupyter kernel is unavailable"
    ),
}
(HERE / "MX5_NOTEBOOK_EXECUTION_VALIDATION.json").write_text(
    json.dumps(record, indent=2), encoding="utf-8"
)
print(json.dumps(record, indent=2))


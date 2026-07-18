"""Execute every MX4 notebook code cell sequentially for CI-style validation."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import nbformat


matplotlib.use("Agg")
HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "MX4_LORENTZ_ARA_AUDIT_NOTEBOOK.ipynb"

notebook = nbformat.read(NOTEBOOK, as_version=4)
nbformat.validate(notebook)
namespace: dict = {"__name__": "__mx4_notebook_validation__"}
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
    "execution_method": "sequential single-process validation because no Jupyter kernel is required",
}
(HERE / "MX4_NOTEBOOK_EXECUTION_VALIDATION.json").write_text(
    json.dumps(record, indent=2), encoding="utf-8"
)
print(json.dumps(record, indent=2))

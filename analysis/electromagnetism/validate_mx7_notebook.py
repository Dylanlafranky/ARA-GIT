"""Execute and validate the MX7 notebook top to bottom."""

import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
JUPYTER_RUNTIME = Path(r"F:\SystemFormulaFolder\work_tmp\ara_mx7_jupyter")
JUPYTER_RUNTIME.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("IPYTHONDIR", str(JUPYTER_RUNTIME / "ipython"))
os.environ.setdefault("JUPYTER_CONFIG_DIR", str(JUPYTER_RUNTIME / "config"))
os.environ.setdefault("JUPYTER_DATA_DIR", str(JUPYTER_RUNTIME / "data"))
os.environ.setdefault("JUPYTER_RUNTIME_DIR", str(JUPYTER_RUNTIME / "runtime"))

import nbformat
from nbclient import NotebookClient


NOTEBOOK = HERE / "MX7_PHASE_FIRST_INFORMATION3_PYRAMID_NOTEBOOK.ipynb"
notebook = nbformat.read(NOTEBOOK, as_version=4)
client = NotebookClient(
    notebook,
    timeout=180,
    kernel_name="python3",
    resources={"metadata": {"path": str(HERE)}},
)
client.execute()
nbformat.write(notebook, NOTEBOOK)

code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
errors = [
    output
    for cell in code_cells
    for output in cell.get("outputs", [])
    if output.get("output_type") == "error"
]
validation = {
    "notebook": str(NOTEBOOK),
    "code_cell_count": len(code_cells),
    "executed_code_cell_count": sum(cell.get("execution_count") is not None for cell in code_cells),
    "error_output_count": len(errors),
    "validation_pass": bool(
        all(cell.get("execution_count") is not None for cell in code_cells) and not errors
    ),
}
(HERE / "MX7_NOTEBOOK_EXECUTION_VALIDATION.json").write_text(
    json.dumps(validation, indent=2), encoding="utf-8"
)
print(json.dumps(validation, indent=2))

from __future__ import annotations

import contextlib
import io
import json
import os
import traceback
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN5_MULTIPLICATIVE_RUNG_TRANSFER.ipynb"
VALIDATION = HERE / "PN5_NOTEBOOK_EXECUTION_VALIDATION.json"


def main() -> None:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    namespace: dict[str, object] = {"__name__": "__notebook__"}
    count = 0
    errors: list[dict[str, object]] = []
    original = Path.cwd()
    os.chdir(HERE)
    try:
        for index, cell in enumerate(notebook["cells"]):
            if cell.get("cell_type") != "code":
                continue
            count += 1
            cell["execution_count"] = count
            cell["outputs"] = []
            stream = io.StringIO()
            try:
                with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
                    exec(compile("".join(cell.get("source", [])), f"{NOTEBOOK.name}:cell-{index}", "exec"), namespace)
                if stream.getvalue():
                    cell["outputs"].append({"name": "stdout", "output_type": "stream", "text": stream.getvalue()})
            except Exception as error:  # noqa: BLE001
                cell["outputs"].append({
                    "ename": type(error).__name__, "evalue": str(error), "output_type": "error",
                    "traceback": traceback.format_exc().splitlines(),
                })
                errors.append({"cell_index": index, "error": type(error).__name__, "message": str(error)})
                break
    finally:
        os.chdir(original)
    NOTEBOOK.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    code_cells = [cell for cell in notebook["cells"] if cell.get("cell_type") == "code"]
    result = {
        "executor": "standard-library fallback because nbformat and nbclient are unavailable",
        "code_cells": len(code_cells),
        "executed_code_cells": sum(cell.get("execution_count") is not None for cell in code_cells),
        "error_outputs": sum(output.get("output_type") == "error" for cell in code_cells for output in cell.get("outputs", [])),
        "errors": errors,
        "all_passed": not errors and all(cell.get("execution_count") is not None for cell in code_cells),
    }
    VALIDATION.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

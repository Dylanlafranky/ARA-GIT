from __future__ import annotations

import contextlib
import io
import json
import os
import traceback
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN4_DIRECT_SIEVE_STATE_ARA.ipynb"
VALIDATION = HERE / "PN4_NOTEBOOK_EXECUTION_VALIDATION.json"


def main() -> None:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    namespace: dict[str, object] = {"__name__": "__notebook__"}
    execution_count = 0
    errors: list[dict[str, object]] = []
    original_cwd = Path.cwd()
    os.chdir(HERE)
    try:
        for index, cell in enumerate(notebook["cells"]):
            if cell.get("cell_type") != "code":
                continue
            execution_count += 1
            cell["execution_count"] = execution_count
            cell["outputs"] = []
            source = "".join(cell.get("source", []))
            stream = io.StringIO()
            try:
                with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
                    exec(compile(source, f"{NOTEBOOK.name}:cell-{index}", "exec"), namespace)
                text = stream.getvalue()
                if text:
                    cell["outputs"].append({"name": "stdout", "output_type": "stream", "text": text})
            except Exception as error:  # noqa: BLE001 - artifact must retain exact execution failure
                captured = stream.getvalue()
                if captured:
                    cell["outputs"].append({"name": "stdout", "output_type": "stream", "text": captured})
                trace = traceback.format_exc().splitlines()
                cell["outputs"].append({
                    "ename": type(error).__name__,
                    "evalue": str(error),
                    "output_type": "error",
                    "traceback": trace,
                })
                errors.append({"cell_index": index, "error": type(error).__name__, "message": str(error)})
                break
    finally:
        os.chdir(original_cwd)

    NOTEBOOK.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    code_cells = [cell for cell in notebook["cells"] if cell.get("cell_type") == "code"]
    validation = {
        "executor": "standard-library fallback because nbformat and nbclient were unavailable",
        "code_cells": len(code_cells),
        "executed_code_cells": sum(cell.get("execution_count") is not None for cell in code_cells),
        "error_outputs": sum(
            output.get("output_type") == "error"
            for cell in code_cells
            for output in cell.get("outputs", [])
        ),
        "errors": errors,
        "all_passed": not errors and all(cell.get("execution_count") is not None for cell in code_cells),
    }
    VALIDATION.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if not validation["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

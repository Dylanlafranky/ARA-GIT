from __future__ import annotations

import contextlib
import hashlib
import io
import json
import traceback
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN6_NATIVE_ARA_CIRCUMFERENCE.ipynb"
VALIDATION = HERE / "PN6_NOTEBOOK_EXECUTION_VALIDATION.json"


def sha256(path: Path) -> str:
    state = hashlib.sha256()
    state.update(path.read_bytes())
    return state.hexdigest().upper()


def main() -> None:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    namespace = {"__name__": "__main__"}
    executed = 0
    errors = []
    old_cwd = Path.cwd()
    try:
        import os
        os.chdir(HERE)
        for cell in notebook["cells"]:
            if cell["cell_type"] != "code":
                continue
            executed += 1
            cell["execution_count"] = executed
            cell["outputs"] = []
            source = "".join(cell["source"])
            output = io.StringIO()
            try:
                with contextlib.redirect_stdout(output):
                    exec(compile(source, f"<notebook-cell-{executed}>", "exec"), namespace)
                text = output.getvalue()
                if text:
                    cell["outputs"].append({"name": "stdout", "output_type": "stream", "text": text.splitlines(keepends=True)})
            except Exception as exc:
                error = {
                    "cell": executed,
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc().splitlines(),
                }
                errors.append(error)
                cell["outputs"].append({
                    "output_type": "error",
                    "ename": error["type"],
                    "evalue": error["message"],
                    "traceback": error["traceback"],
                })
                break
    finally:
        import os
        os.chdir(old_cwd)

    notebook["metadata"]["pn6_execution"] = {
        "executor": "transparent standard-library fallback because nbformat/nbclient are unavailable",
        "code_cells_executed": executed,
        "errors": len(errors),
    }
    NOTEBOOK.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    validation = {
        "notebook": NOTEBOOK.name,
        "executor": Path(__file__).name,
        "limitation": "nbformat and nbclient unavailable in bundled runtime; cells executed sequentially in a shared namespace",
        "code_cells_executed": executed,
        "code_cells_total": sum(cell["cell_type"] == "code" for cell in notebook["cells"]),
        "errors": errors,
        "complete": not errors and executed == sum(cell["cell_type"] == "code" for cell in notebook["cells"]),
        "notebook_sha256": sha256(NOTEBOOK),
    }
    VALIDATION.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

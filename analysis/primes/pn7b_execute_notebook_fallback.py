from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import traceback
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP.ipynb"
VALIDATION = HERE / "PN7B_NOTEBOOK_EXECUTION_VALIDATION.json"


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
        os.chdir(HERE)
        for cell in notebook["cells"]:
            if cell["cell_type"] != "code":
                continue
            executed += 1
            cell["execution_count"] = executed
            cell["outputs"] = []
            output = io.StringIO()
            try:
                with contextlib.redirect_stdout(output):
                    exec(compile("".join(cell["source"]), f"<notebook-cell-{executed}>", "exec"), namespace)
                text = output.getvalue()
                if text:
                    cell["outputs"].append({"name": "stdout", "output_type": "stream", "text": text.splitlines(keepends=True)})
            except Exception as exc:
                err = {
                    "cell": executed, "type": type(exc).__name__, "message": str(exc),
                    "traceback": traceback.format_exc().splitlines(),
                }
                errors.append(err)
                cell["outputs"].append({
                    "output_type": "error", "ename": err["type"], "evalue": err["message"],
                    "traceback": err["traceback"],
                })
                break
    finally:
        os.chdir(old_cwd)

    code_total = sum(cell["cell_type"] == "code" for cell in notebook["cells"])
    notebook["metadata"]["pn7b_execution"] = {
        "executor": "transparent standard-library fallback because nbformat/nbclient are unavailable",
        "code_cells_executed": executed,
        "errors": len(errors),
    }
    NOTEBOOK.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    report = {
        "notebook": NOTEBOOK.name,
        "executor": Path(__file__).name,
        "limitation": "nbformat and nbclient unavailable; cells executed sequentially in a shared namespace",
        "code_cells_executed": executed,
        "code_cells_total": code_total,
        "errors": errors,
        "complete": not errors and executed == code_total,
        "notebook_sha256": sha256(NOTEBOOK),
    }
    VALIDATION.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

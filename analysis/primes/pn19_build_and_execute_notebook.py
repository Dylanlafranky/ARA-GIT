"""Build and execute the reproducible PN19 analysis notebook.

The bundled analytics runtime has NumPy, pandas and Pillow but no Jupyter
package. This builder writes standard nbformat-4 JSON and executes every code
cell sequentially in one shared Python namespace, recording outputs and errors.
"""

from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import json
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN19_TWO_PARENT_INFORMATION_LOCK.ipynb"
VALIDATION = HERE / "PN19_NOTEBOOK_EXECUTION_VALIDATION.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "id": uuid.uuid4().hex[:8], "metadata": {}, "source": source}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": uuid.uuid4().hex[:8],
        "metadata": {},
        "outputs": [],
        "source": source,
    }


def execute_cell(cell: dict, namespace: dict, execution_count: int) -> None:
    source = cell["source"]
    tree = ast.parse(source, filename=f"PN19-cell-{execution_count}", mode="exec")
    final_expression = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
    stdout = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout):
            if tree.body:
                exec(compile(tree, f"PN19-cell-{execution_count}", "exec"), namespace)
            value = None
            if final_expression is not None:
                value = eval(compile(ast.Expression(final_expression.value), f"PN19-cell-{execution_count}", "eval"), namespace)
        outputs: list[dict] = []
        if stdout.getvalue():
            outputs.append({"name": "stdout", "output_type": "stream", "text": stdout.getvalue()})
        if value is not None:
            outputs.append({
                "data": {"text/plain": repr(value)},
                "execution_count": execution_count,
                "metadata": {},
                "output_type": "execute_result",
            })
        cell["outputs"] = outputs
        cell["execution_count"] = execution_count
    except Exception as exc:
        cell["execution_count"] = execution_count
        cell["outputs"] = [{
            "ename": type(exc).__name__,
            "evalue": str(exc),
            "output_type": "error",
            "traceback": traceback.format_exc().splitlines(),
        }]
        raise


def main() -> None:
    cells = [
        markdown(
            "# PN19 — Two-parent information lock\n\n"
            "## TL;DR\n\n"
            "A fresh, sealed ARA split predicted **900,000,000,013** from the unused anchor "
            "**900,000,000,000** before primality was opened. Independent validation passed **38/38** checks. "
            "Phase A alone gave the exact `+13` correction; the A∩B information lock made the result definitive. "
            "A post-target 1,000-anchor audit found Phase A exact **93.2%** of the time versus **28.0%** for the "
            "p29-wheel control. The exact method remains a two-mask decomposition of an established segmented sieve."
        ),
        markdown(
            "## Context & Methods\n\n"
            "**Question.** Can all lower prime children be folded into two complete ARA parent waves, with their "
            "relation acting as an Information³ lock?\n\n"
            "**Frozen split.** Generate every prime child through `floor(sqrt(2N))`. Split the ordered children at "
            "the cumulative-log-weight midpoint. Phase A contains the smaller frequent gates; Phase B contains the "
            "larger sparse gates. A candidate survives only when both masks are one.\n\n"
            "**Key assumptions and controls.** The target and scripts were hash-frozen. The primary did not contain a "
            "target primality function. The A∩B result must equal a complete segmented sieve; exactness is therefore "
            "a crosswalk result, not a new primality theorem. The 1,000-anchor robustness run is explicitly "
            "post-target and exploratory."
        ),
        code(
            "from pathlib import Path\n"
            "import json\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "from PIL import Image, ImageDraw\n\n"
            "HERE = Path.cwd()\n"
            "prediction = json.loads((HERE / 'PN19_TWO_PARENT_INFORMATION_LOCK_PREDICTION.json').read_text())\n"
            "validation = json.loads((HERE / 'PN19_TWO_PARENT_INFORMATION_LOCK_VALIDATION.json').read_text())\n"
            "robustness = json.loads((HERE / 'PN19_POST_TARGET_SECOND_GO_ROBUSTNESS.json').read_text())\n"
            "target = prediction['target']\n"
            "assert validation['all_passed'] and validation['candidate_is_first_prime_above_anchor']\n"
            "print('Loaded sealed prediction, independent validation, and exploratory robustness data.')"
        ),
        markdown("## Data"),
        code(
            "target_summary = pd.DataFrame([{\n"
            "    'anchor': target['anchor'],\n"
            "    'Phase A first': target['phase_a_first_survivor_offset'],\n"
            "    'Phase B first': target['phase_b_first_survivor_offset'],\n"
            "    'A∩B lock': target['information_lock_offset'],\n"
            "    'sealed candidate': target['predicted_integer'],\n"
            "    'E_A': target['split']['teara_phase_a'],\n"
            "    'E_B': target['split']['teara_phase_b'],\n"
            "    'children': target['child_count'],\n"
            "}])\n"
            "target_summary"
        ),
        code(
            "development = pd.DataFrame(prediction['development'])[[\n"
            "    'anchor', 'phase_a_first_survivor_offset', 'phase_b_first_survivor_offset',\n"
            "    'information_lock_offset', 'either_parent_is_second_go_success'\n"
            "]]\n"
            "by_scale = pd.DataFrame(robustness['by_scale'])\n"
            "development"
        ),
        markdown("## Results"),
        code(
            "phase_a = np.fromfile(HERE / target['phase_a_mask_file'], dtype=np.uint8)\n"
            "phase_b = np.fromfile(HERE / target['phase_b_mask_file'], dtype=np.uint8)\n"
            "lock = np.fromfile(HERE / target['information_lock_mask_file'], dtype=np.uint8)\n\n"
            "canvas = Image.new('RGB', (1400, 780), 'white')\n"
            "draw = ImageDraw.Draw(canvas)\n"
            "draw.text((30, 20), 'PN19 two-parent information lock', fill='#111827')\n"
            "draw.text((30, 45), 'Fresh target masks: yellow survives, blue collides', fill='#374151')\n"
            "left, top, cell_w, cell_h = 165, 90, 18, 55\n"
            "for row_index, (name, values) in enumerate([('Phase A', phase_a), ('Phase B', phase_b), ('A AND B', lock)]):\n"
            "    y = top + row_index * (cell_h + 18)\n"
            "    draw.text((30, y + 18), name, fill='#111827')\n"
            "    for offset in range(1, 65):\n"
            "        x = left + (offset - 1) * cell_w\n"
            "        colour = '#f4c95d' if values[offset] else '#3f6c9e'\n"
            "        draw.rectangle((x, y, x + cell_w - 2, y + cell_h), fill=colour)\n"
            "        if offset % 4 == 1:\n"
            "            draw.text((x, y + cell_h + 2), str(offset), fill='#4b5563')\n"
            "lock_x = left + (target['information_lock_offset'] - 1) * cell_w\n"
            "draw.line((lock_x, top - 8, lock_x, top + 3*(cell_h+18)-15), fill='#dc2626', width=3)\n"
            "draw.text((lock_x + 5, top - 8), 'first lock +13', fill='#dc2626')\n\n"
            "chart_left, chart_top, chart_right, chart_bottom = 120, 410, 1340, 735\n"
            "draw.text((30, 370), 'Post-target second-go robustness (200 anchors per scale)', fill='#111827')\n"
            "draw.line((chart_left, chart_top, chart_left, chart_bottom), fill='#111827', width=2)\n"
            "draw.line((chart_left, chart_bottom, chart_right, chart_bottom), fill='#111827', width=2)\n"
            "for percent in range(0, 101, 20):\n"
            "    y = chart_bottom - (chart_bottom-chart_top)*percent/100\n"
            "    draw.line((chart_left, y, chart_right, y), fill='#e5e7eb')\n"
            "    draw.text((70, y-7), f'{percent}%', fill='#4b5563')\n"
            "xs = np.linspace(chart_left+40, chart_right-40, len(by_scale))\n"
            "series = [('Phase A', 'phase_a_success_rate', '#b45309'), ('Phase B', 'phase_b_success_rate', '#2563eb'), ('p29 control', 'p29_success_rate', '#6b7280')]\n"
            "for series_index, (label, column, colour) in enumerate(series):\n"
            "    points = []\n"
            "    for x, value in zip(xs, by_scale[column]):\n"
            "        y = chart_bottom - (chart_bottom-chart_top)*float(value)\n"
            "        points.append((float(x), float(y)))\n"
            "    draw.line(points, fill=colour, width=4)\n"
            "    for x, y in points:\n"
            "        draw.ellipse((x-5, y-5, x+5, y+5), fill=colour)\n"
            "    draw.text((chart_left + 250*series_index, chart_top-24), label, fill=colour)\n"
            "for x, scale in zip(xs, by_scale['scale']):\n"
            "    draw.text((x-18, chart_bottom+8), f\"10^{int(np.log10(scale))}\", fill='#4b5563')\n"
            "figure_path = HERE / 'PN19_TWO_PARENT_INFORMATION_LOCK_FIGURE.png'\n"
            "canvas.save(figure_path)\n"
            "figure_path.name"
        ),
        code(
            "metrics = pd.DataFrame({\n"
            "    'measure': ['TE-ARA share', 'survivor density', 'first survivor'],\n"
            "    'Phase A': [target['split']['teara_phase_a'], target['phase_a_survivor_density'], target['phase_a_first_survivor_offset']],\n"
            "    'Phase B': [target['split']['teara_phase_b'], target['phase_b_survivor_density'], target['phase_b_first_survivor_offset']],\n"
            "    'A∩B': [2.0, target['joint_survivor_density'], target['information_lock_offset']],\n"
            "})\n"
            "metrics"
        ),
        markdown(
            "## Takeaways\n\n"
            "1. The q-free two-parent lock recovered the first prime at a fresh 900-billion anchor.\n"
            "2. `E_A≈E_B≈1` but local action is highly asymmetric: Phase A survivor density is about 3.88%, "
            "while Phase B survivor density is about 95.01%.\n"
            "3. Phase A's first survivor was exact on 93.2% of the post-target grid, making the proposed second-go "
            "behavior quantitatively real.\n"
            "4. Exactness still requires the relation because Phase A occasionally admits composites made from two "
            "larger children.\n"
            "5. The method retains all lower-child information inside two masks and is mathematically equivalent to "
            "an established segmented sieve. It is a useful ARA decomposition, not yet information or speed compression."
        ),
        markdown("## Reproducibility & QA"),
        code(
            "assert len(phase_a) == len(phase_b) == len(lock) == 65_536\n"
            "assert np.array_equal(lock, phase_a & phase_b)\n"
            "assert abs(target['split']['teara_total'] - 2.0) < 1e-15\n"
            "assert target['information_lock_offset'] == 13\n"
            "assert robustness['overall']['anchor_count'] == 1000\n"
            "assert robustness['overall']['phase_a_success_rate'] == 0.932\n"
            "assert validation['passed_count'] == validation['check_count'] == 38\n"
            "qa = {\n"
            "    'sealed_candidate': validation['candidate'],\n"
            "    'first_prime_confirmed': validation['candidate_is_first_prime_above_anchor'],\n"
            "    'independent_checks': f\"{validation['passed_count']}/{validation['check_count']}\",\n"
            "    'mask_identity': 'A AND B equals stored lock',\n"
            "    'post_target_anchor_count': robustness['overall']['anchor_count'],\n"
            "}\n"
            "qa"
        ),
    ]

    original_cwd = Path.cwd()
    execution_count = 0
    errors: list[str] = []
    namespace = {"__name__": "__pn19_notebook__"}
    try:
        import os
        os.chdir(HERE)
        for cell in cells:
            if cell["cell_type"] != "code":
                continue
            execution_count += 1
            try:
                execute_cell(cell, namespace, execution_count)
            except Exception as exc:
                errors.append(f"cell {execution_count}: {type(exc).__name__}: {exc}")
                break
    finally:
        os.chdir(original_cwd)

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
            "execution": {"engine": "sequential shared-namespace fallback; no nbformat package available"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    code_cells = [cell for cell in cells if cell["cell_type"] == "code"]
    receipt = {
        "test_id": "PN19/NOTEBOOK-EXECUTION-VALIDATION/v1",
        "executed_utc": datetime.now(timezone.utc).isoformat(),
        "notebook": NOTEBOOK.name,
        "notebook_sha256": sha256(NOTEBOOK),
        "execution_engine": "sequential shared Python namespace fallback",
        "environment_note": "Bundled runtime lacked nbformat/Jupyter; standard nbformat-4 JSON was written directly.",
        "code_cell_count": len(code_cells),
        "executed_code_cell_count": sum(cell.get("execution_count") is not None for cell in code_cells),
        "error_output_count": len(errors),
        "errors": errors,
        "all_code_cells_executed": all(cell.get("execution_count") is not None for cell in code_cells),
        "figure_exists": (HERE / "PN19_TWO_PARENT_INFORMATION_LOCK_FIGURE.png").exists(),
        "validation_passed": not errors and all(cell.get("execution_count") is not None for cell in code_cells),
    }
    VALIDATION.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if errors:
        raise RuntimeError(errors[0])


if __name__ == "__main__":
    main()

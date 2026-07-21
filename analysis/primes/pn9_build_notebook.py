"""Build a standards-compliant executed PN9 notebook without nbformat.

The local runtime does not ship nbformat/nbclient, so this fallback executes
plain print-oriented cells in one namespace and serializes notebook v4 JSON.
"""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "PN9_TANGENT_SPHERE_RIDGE_SCALE.ipynb"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str, namespace: dict, count: int) -> dict:
    output = io.StringIO()
    error = None
    try:
        with contextlib.redirect_stdout(output):
            exec(compile(source, f"<PN9 notebook cell {count}>", "exec"), namespace)
    except Exception as exc:  # preserve an honest executed-notebook error if one occurs
        error = exc
    outputs = []
    text = output.getvalue()
    if text:
        outputs.append({"name": "stdout", "output_type": "stream", "text": text.splitlines(keepends=True)})
    if error is not None:
        outputs.append({
            "ename": type(error).__name__,
            "evalue": str(error),
            "output_type": "error",
            "traceback": [f"{type(error).__name__}: {error}"],
        })
    return {
        "cell_type": "code",
        "execution_count": count,
        "metadata": {},
        "outputs": outputs,
        "source": source.splitlines(keepends=True),
    }


intro = r"""# PN9 tangent-sphere ridge / scale review

This executed companion reviews the frozen PN9 outputs. The full 39.5-million-gap calculation is implemented in
`pn9_tangent_sphere_ridge_scale.py`.

At an internal prime, the frozen coordinates are

\[
x=\frac{2g^+}{g^-+g^+},\quad L=\frac{g^-+g^+}{2},\quad
y=\frac{2L}{L+\ln p}.
\]

`x` is tangent/contact balance. `y` is local sphere scale compared with the logarithmic prime-gap home.
"""

sources = [
    """from pathlib import Path
import csv, hashlib, json

HERE = Path(r'F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\primes')
def sha256(path):
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest().upper()

protocol_hash = sha256(HERE / 'PN9_TANGENT_SPHERE_RIDGE_SCALE_PROTOCOL.md')
result = json.loads((HERE / 'PN9_TANGENT_SPHERE_RIDGE_SCALE_RESULTS.json').read_text(encoding='utf-8'))
print('Protocol hash:', protocol_hash)
print('Evidence class:', result['evidence_class'])
print('Protected:', result['protected_material'])
""",
    """print('Registered P1-P5 core:', result['ridge_plus_scale_core_P1_P5'])
for gate, record in result['criteria'].items():
    print(f\"{gate}: {'PASS' if record['passed'] else 'FAIL'}\")
print('24-bin R11 scale gain:', result['cross_entropy_gains_bits']['R11']['24'])
print('12-bin R11 scale gain:', result['cross_entropy_gains_bits']['R11']['12'])
print('Observed conditional scale information:', result['criteria']['P6']['observed_bits'])
print('Residual over maximum shuffle:', result['criteria']['P6']['residual_bits'])
""",
    """rows = list(csv.DictReader((HERE / 'PN9_TANGENT_SPHERE_RIDGE_SCALE_SCORES.csv').open(encoding='utf-8')))
print('R11 score summary')
print('bins | model       | CE bits  | Brier    | top-3')
for row in rows:
    if row['target'] == 'R11':
        print(f\"{int(row['bins']):>4} | {row['model']:<11} | {float(row['cross_entropy_bits']):.6f} | {float(row['brier_score']):.6f} | {float(row['top3_accuracy']):.6f}\")
""",
    """validation = json.loads((HERE / 'PN9_TANGENT_SPHERE_RIDGE_SCALE_VALIDATION.json').read_text(encoding='utf-8'))
print('Independent validation:', 'PASS' if validation['all_checks_passed'] else 'FAIL')
print('Maximum headline difference:', max(v['absolute_difference'] for v in validation['headline_checks'].values()))
print('Figure:', HERE / 'PN9_TANGENT_SPHERE_RIDGE_SCALE_FIGURE.png')
""",
]

namespace: dict = {}
cells = [markdown(intro)]
for number, source in enumerate(sources, 1):
    cells.append(code(source, namespace, number))
cells.append(markdown("""## Reading the result

The unbinned sphere map is exact, and local scale contains ordered information. The registered 24-bin transfer core
fails because the detailed scale bands do not remain aligned across logarithmic rungs. The predeclared 12-bin
sensitivity is strongly positive on both transfers, which generates—but does not confirm—the hypothesis that the
adult coordinate requires a coarser grain than the child contact coordinate. Exact raw-gap prediction remains best.
"""))

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
OUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
errors = [output for cell in cells if cell.get("cell_type") == "code" for output in cell["outputs"] if output["output_type"] == "error"]
if errors:
    raise RuntimeError(errors)
print(OUT)

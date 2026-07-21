"""Build and execute the PN10B review notebook using the standard-library fallback."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "PN10B_CHILD_PHASE_PRIME_RANKING.ipynb"
VALIDATION = HERE / "PN10B_NOTEBOOK_EXECUTION_VALIDATION.json"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def execute_cell(source: str, namespace: dict, count: int) -> dict:
    output = io.StringIO()
    error = None
    try:
        with contextlib.redirect_stdout(output):
            exec(compile(source, f"<PN10B notebook cell {count}>", "exec"), namespace)
    except Exception as exc:  # recorded in notebook output, then rejected below
        error = exc
    outputs = []
    if output.getvalue():
        outputs.append({"name": "stdout", "output_type": "stream", "text": output.getvalue().splitlines(keepends=True)})
    if error is not None:
        outputs.append(
            {
                "ename": type(error).__name__,
                "evalue": str(error),
                "output_type": "error",
                "traceback": [f"{type(error).__name__}: {error}"],
            }
        )
    return {
        "cell_type": "code",
        "execution_count": count,
        "metadata": {},
        "outputs": outputs,
        "source": source.splitlines(keepends=True),
    }


intro = r"""# PN10B child phase inside the pre-ridge factor sphere

## tl;dr

The registered child decomposition closed exactly but produced a **NULL** prime-ranking result. On the fresh
interval, ARA full scored `0.652923909` bits per survivor versus `0.652816910` for the parent-only forecast, with
ROC AUC `0.500307`. The 95% paired interval included zero. An independent implementation passed 79/79 checks.

## Context & Methods

PN10B used only the nine largest divisor gates already tested at parent cutoff `c=0.90`. For each gate,

\[
A_j=2(n\bmod q_j)/q_j,\quad B_j=2-A_j,\quad s_j=A_j-1,\quad h_j=s_js_{j+1}.
\]

The primary model used nine ordered child orientations and eight adjacent couplings. It was frozen before opening
the fresh target `[4,000,000,000,4,001,000,000)`.

### Key Assumptions

- `A` and `B` are two directions of one child axis, not independent features.
- No gate above `n^0.45` may be inspected.
- Positive performance would mean useful organisation of existing information, not new Shannon information.
"""

sources = [
    """from pathlib import Path
import csv, hashlib, json

HERE = Path(r'F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\primes')
freeze = json.loads((HERE / 'PN10B_FREEZE_MANIFEST.json').read_text(encoding='utf-8'))
result = json.loads((HERE / 'PN10B_CHILD_PHASE_RESULTS.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN10B_CHILD_PHASE_VALIDATION.json').read_text(encoding='utf-8'))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest().upper()
print('Protocol hash matches:', sha(HERE / freeze['protocol_file']) == freeze['protocol_sha256'])
print('Source hash matches:  ', sha(HERE / freeze['source_file']) == freeze['source_sha256'])
print('Fresh target:', freeze['intervals']['F'])
print('Protected:', result['protected_material'])
""",
    """print('## Data')
for name, interval in result['intervals'].items():
    print(name, 'survivors=', interval['survivor_count'], 'primes=', interval['prime_count'],
          'composites=', interval['composite_count'], 'purity=', round(interval['prime_prevalence'], 9))
    print('  guards:', interval['guards'])
""",
    """print('## Results')
metrics = [row for row in result['metrics'] if row['stage'] == 'pooled_D_E_to_fresh_F']
print('model | log loss bits | Brier | AUC | top-decile lift')
for row in metrics:
    print(f"{row['model']:<23} {row['log_loss_bits']:.9f} {row['brier']:.9f} {row['auc']:.6f} {row['top_decile_lift']:.6f}")
""",
    """print('Fresh paired comparisons:')
for name, row in result['fresh_comparisons'].items():
    print(f"{name:<42} gain={row['gain_bits_per_event']:+.9f} "
          f"CI=[{row['ci95_low']:+.9f},{row['ci95_high']:+.9f}] blocks+={row['positive_blocks']}/100")
print('Criteria:', result['criteria'])
print('Verdict:', result['verdict'])
""",
    """print('## Validation')
print('Independent checks:', validation['checks_passed'], '/', validation['checks_total'])
print('All passed:', validation['all_passed'])
print('Maximum fitted gradient:', validation['max_fitted_gradient'])
print('Maximum metric disagreement:', validation['max_metric_error'])
print('Static figure:', HERE / 'PN10B_CHILD_PHASE_FIGURE.png')
""",
]

namespace: dict = {}
cells = [markdown(intro)]
for number, source in enumerate(sources, 1):
    cells.append(execute_cell(source, namespace, number))
cells.append(
    markdown(
        r"""## Takeaways

1. The child A/B axes are mathematically valid and leak-free at the registered gate budget.
2. Their ordered coupling did not rank fresh primes above remaining composites; ARA full was effectively chance.
3. Buchstab's constant parent probability calibrated best but, as a constant, also did not rank individuals.
4. The immediate hypothesis is closed as a clean null. A different child identity would require a new registration.
"""
    )
)

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
errors = [
    output
    for cell in cells
    if cell.get("cell_type") == "code"
    for output in cell["outputs"]
    if output["output_type"] == "error"
]
if errors:
    raise RuntimeError(errors)
VALIDATION.write_text(
    json.dumps(
        {
            "status": "PASS",
            "notebook": OUT.name,
            "total_cells": len(cells),
            "code_cells": sum(cell.get("cell_type") == "code" for cell in cells),
            "error_outputs": 0,
            "execution_method": "standard-library notebook-v4 fallback because nbformat/nbclient are unavailable",
        },
        indent=2,
    ),
    encoding="utf-8",
)
print(OUT)

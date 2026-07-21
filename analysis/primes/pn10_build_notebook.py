"""Build an executed PN10 review notebook without nbformat/nbclient."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "PN10_FACTOR_SPHERE_PRIME_RECOVERY.ipynb"
VALIDATION = HERE / "PN10_NOTEBOOK_EXECUTION_VALIDATION.json"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str, namespace: dict, count: int) -> dict:
    output = io.StringIO()
    error = None
    try:
        with contextlib.redirect_stdout(output):
            exec(compile(source, f"<PN10 notebook cell {count}>", "exec"), namespace)
    except Exception as exc:
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


intro = r"""# PN10 factor-sphere prime recovery

This executed companion reviews the frozen PN10 artifacts. The complete deterministic calculation lives in
`pn10_factor_sphere_prime_recovery.py`; an independent implementation lives in
`pn10_validate_factor_sphere.py`.

For integer `n` and factor candidate `d`,

\[
x_n(d)=\frac{2\log d}{\log n},\qquad x_n(d)+x_n(n/d)=2.
\]

The endpoints are `1` and `n`; the `1.0` ridge is `sqrt(n)`. A divisor collision at or before the ridge means
composite. A quiet walk through the ridge means prime.
"""

sources = [
    """from pathlib import Path
import csv, hashlib, json, math

HERE = Path(r'F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\primes')
def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

freeze = json.loads((HERE / 'PN10_FREEZE_MANIFEST.json').read_text(encoding='utf-8'))
result = json.loads((HERE / 'PN10_FACTOR_SPHERE_RESULTS.json').read_text(encoding='utf-8'))
print('Protocol hash:', sha256(HERE / 'PN10_FACTOR_SPHERE_PRIME_RECOVERY_PROTOCOL.md'))
print('Frozen hash:  ', freeze['protocol_sha256'])
print('Evidence:', result['evidence_class'])
print('Protected:', result['protected_material'])
""",
    """def x(n, d):
    return 2 * math.log(d) / math.log(n)

for n in [77, 79, 121]:
    factors = [d for d in range(1, n + 1) if n % d == 0]
    print(n, [(d, round(x(n, d), 6)) for d in factors])
print('77 factor-pair closure:', x(77, 7) + x(77, 11))
print('121 square ridge:', x(121, 11))
""",
    """print('Development primes:', result['intervals']['development']['primes'])
print('Fresh evaluation primes:', result['intervals']['evaluation']['primes'])
print('First 25 fresh primes:')
print(result['exact_recovery']['first_25_evaluation_primes'])
print('\\nRegistered criteria')
for name, record in result['criteria'].items():
    state = record.get('pass', record.get('all_primary_cutoffs_retain_composites'))
    print(name, 'PASS' if state else 'FAIL')
""",
    """rows = list(csv.DictReader((HERE / 'PN10_FACTOR_SPHERE_TRANSFER.csv').open(encoding='utf-8')))
print('cutoff | method     | development purity | evaluation purity | transfer error | Brier | composites left')
for row in rows:
    print(f"{float(row['cutoff']):>6.2f} | {row['method']:<10} | {float(row['development_purity']):>18.6f} | {float(row['evaluation_purity']):>17.6f} | {float(row['purity_transfer_error']):>14.6f} | {float(row['evaluation_brier']):.6f} | {int(row['evaluation_remaining_composites']):>15,}")
""",
    """validation = json.loads((HERE / 'PN10_FACTOR_SPHERE_VALIDATION.json').read_text(encoding='utf-8'))
print('Independent validation:', validation['status'])
print('Checks:', validation['passed_checks'], '/', validation['total_checks'])
print('Static figure:', HERE / 'PN10_FACTOR_SPHERE_FIGURE.png')
print('To reconstruct everything, run:')
print('  python pn10_factor_sphere_prime_recovery.py')
print('  python pn10_validate_factor_sphere.py')
""",
]

namespace: dict = {}
cells = [markdown(intro)]
for number, source in enumerate(sources, 1):
    cells.append(code(source, namespace, number))
cells.append(markdown(r"""## Reading the result

The full ridge walk is an exact prime test because it is the classical `sqrt(n)` completeness condition in a
reversible ARA coordinate. The partial walk is not exact: at `c=0.90`, 9,249 composites remain among 56,152 fresh
survivors. Its strong result is cross-scale calibration: survivor purity transfers from the development interval to
the much larger fresh interval far better than a fixed absolute divisor cutoff.

That supports the factor-sphere coordinate as a useful representation. It does not establish a faster prime
algorithm or distinguish ARA from established relative-logarithmic factor theory by itself.
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
VALIDATION.write_text(json.dumps({
    "status": "PASS",
    "notebook": OUT.name,
    "total_cells": len(cells),
    "code_cells": sum(cell.get("cell_type") == "code" for cell in cells),
    "error_outputs": 0,
    "execution_method": "standard-library notebook-v4 fallback because nbformat/nbclient are unavailable",
}, indent=2), encoding="utf-8")
print(OUT)

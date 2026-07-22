"""Build and execute the dependency-free PN27 reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN27_EXACT_FIT_CHILD_LIFT_REPRODUCIBILITY.ipynb"
RECEIPT = HERE / "PN27_NOTEBOOK_EXECUTION_VALIDATION.json"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def main() -> None:
    if RECEIPT.exists():
        prior = json.loads(RECEIPT.read_text(encoding="utf-8"))
        if prior.get("status") != "FAIL":
            raise RuntimeError(f"refusing to overwrite successful {RECEIPT.name}")
    elif NOTEBOOK.exists():
        raise RuntimeError(f"refusing to overwrite unreceipted {NOTEBOOK.name}")

    cells = [
        markdown(
            """# PN27 — exact-fit child lift

## tl;dr

The frozen one-shot rule `P_hat=N+a+2b+1`, where `a` is the largest exact-fitting wave in
`{1,3,5,9,11,13}` and `b=14-a`, hit primes on **9.010%** of 30,000 fresh odd anchors. The equal-weight matched
offset rate was **8.777%**. A relation-broken offset permutation gave `p=0.0144`, missing the frozen `p<0.01`
strong threshold. Status: **partial predictive support**, not a prime formula.
"""
        ),
        markdown(
            """## Context & Methods

The predictor contains no sieve state, nearby-prime label, prime gap, retry, or fitted parameter. Predictions were
written and SHA-256 frozen before a separate scoring script attached primality labels.

### Key assumptions

- "Fits exactly" means integer divisibility.
- "Largest" means the numerically largest declared wave that divides the anchor.
- Odd anchors are primary because the rule adds an even offset; even anchors are a negative control.
- A hit requires the single frozen candidate itself to be prime.
"""
        ),
        code(
            """import csv
import json
from pathlib import Path

HERE = Path.cwd()
results = json.loads((HERE / 'PN27_EXACT_FIT_CHILD_LIFT_RESULTS.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN27_EXACT_FIT_CHILD_LIFT_VALIDATION.json').read_text(encoding='utf-8'))
with (HERE / 'PN27_EXACT_FIT_CHILD_LIFT_VALIDATED_ROWS.csv').open(encoding='utf-8', newline='') as handle:
    rows = list(csv.DictReader(handle))
print('status:', results['status'])
print('validation:', validation['checks_passed'], '/', validation['checks_total'])
assert results['status'] == 'PARTIAL PREDICTIVE SUPPORT'
assert validation['all_checks_passed'] is True
assert len(rows) == 60000
"""
        ),
        markdown("""## Data"""),
        code(
            """print(results['population'])
assert results['population']['odd_primary_rows'] == 30000
assert results['population']['even_control_rows'] == 30000
assert results['population']['protected_87_bit_anchor_used'] is False
"""
        ),
        markdown("""## Results — worked geometry"""),
        code(
            """N = 35
a = max(w for w in (1,3,5,9,11,13) if N % w == 0)
b = 14 - a
C = a + 2*b
U = N + C
P_hat = U + 1
print({'N': N, 'a': a, 'b': b, 'C': C, 'U': U, 'P_hat': P_hat})
assert (a, b, C, U, P_hat) == (5, 9, 23, 58, 59)
assert results['worked_example_35']['is_prime'] is True
"""
        ),
        markdown("""## Results — fresh one-shot test"""),
        code(
            """headline = results['odd_primary']
print(headline)
print('permutation:', results['offset_permutation_control'])
assert headline['ara_hit_rate'] == 0.0901
assert headline['uniform_allowed_offset_rate'] < headline['ara_hit_rate']
assert results['offset_permutation_control']['one_sided_p_pooled'] >= 0.01
"""
        ),
        markdown("""## Results — scale and child-pair detail"""),
        code(
            """print('scale | ARA | uniform | difference')
for scale, values in results['by_scale'].items():
    print(scale, values['ara_hit_rate'], values['uniform_allowed_offset_rate'], values['difference_vs_uniform'])

print()
print('phase A | phase B | n | ARA | uniform | difference')
for group in results['by_child_pair']:
    if group['scale'] == 'pooled':
        print(group['phase_a'], group['phase_b'], group['n'], group['prime_hit_rate'],
              group['uniform_offset_prime_rate'], group['difference_vs_uniform'])
"""
        ),
        markdown("""## Results — even negative control"""),
        code(
            """print(results['even_negative_control'])
assert results['even_negative_control']['all_candidates_even'] is True
assert results['even_negative_control']['prime_hits'] == 0
"""
        ),
        markdown(
            """## Takeaways

1. The exact `35 -> 59` construction is reproduced by the frozen general rule.
2. The rule retained a small positive amount of prime-survival information on fresh odd anchors.
3. The result is suggestive but not decisive: its frozen permutation threshold failed, and the paired 95% interval
   against the equal-weight offset control includes zero.
4. Positive performance is concentrated in the `9↔5`, `5↔9`, and `3↔11` branches. The `1↔13` fallback covers
   almost 45% of anchors and performs poorly.
5. Much of the gain has a direct small-divisor interpretation. PN27 therefore records a useful one-child-layer
   rule, not a new general prime algorithm.
"""
        ),
    ]

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    namespace = {"__name__": "__pn27_notebook__"}
    failures = []
    executed = 0
    old_cwd = Path.cwd()
    os.chdir(HERE)
    try:
        for index, cell in enumerate(cells):
            if cell["cell_type"] != "code":
                continue
            executed += 1
            cell["execution_count"] = executed
            stream = io.StringIO()
            try:
                with contextlib.redirect_stdout(stream):
                    exec("".join(cell["source"]), namespace)
                if stream.getvalue():
                    cell["outputs"] = [{
                        "name": "stdout",
                        "output_type": "stream",
                        "text": stream.getvalue().splitlines(keepends=True),
                    }]
            except Exception as exc:
                failures.append({
                    "cell_index": index,
                    "error": repr(exc),
                    "traceback": traceback.format_exc(),
                })
                cell["outputs"] = [{
                    "ename": type(exc).__name__,
                    "evalue": str(exc),
                    "output_type": "error",
                    "traceback": traceback.format_exc().splitlines(),
                }]
                break
    finally:
        os.chdir(old_cwd)

    NOTEBOOK.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    receipt = {
        "validation_id": "PN27/NOTEBOOK-EXECUTION/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "code_cells_executed": executed,
        "code_cells_total": sum(cell["cell_type"] == "code" for cell in cells),
        "failures": failures,
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

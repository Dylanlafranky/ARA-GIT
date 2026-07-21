"""Build and execute the PN22 reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN22_ODD_LATTICE_ARA_CANDIDATE_REPRODUCIBILITY.ipynb"
RECEIPT = HERE / "PN22_NOTEBOOK_EXECUTION_VALIDATION.json"


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
    for path in (NOTEBOOK, RECEIPT):
        if path.exists():
            raise RuntimeError(f"refusing to overwrite {path.name}")
    cells = [
        markdown(
            """# PN22 — odd-lattice ARA candidate test

## tl;dr

`T(A)=oddceil(7A/2+1)` is a coherent odd-compatible construction. Across one million inputs it produced a `16.6740%` prime rate versus `14.2942%` for raw odds, but its candidates exactly equal four fixed residue lanes `{1,5,9,13} mod 14`. Its matched-control lift is exactly `1.0`: an exact wheel-sieve crosswalk, not a new prime locator.
"""
        ),
        markdown(
            """## Context & Methods

The continuous ARA identity uses `A`, `B=2A`, ridge offset `A/2`, and a closing `+1`. `oddceil` projects upward to the first allowed odd integer. Inputs are every `A=1,...,1,000,000`; exact prime labels come from Eratosthenes.

### Key Assumptions

- Upward projection is fixed before outcomes are observed.
- Raw odd, coprime-to-14 and exact-residue controls separate lattice filtering from prime-specific information.
- Perfect powers are a predeclared secondary subgroup because 27 and 32 are both perfect powers.
"""
        ),
        code(
            """import json
from pathlib import Path
import numpy as np
from pn22_odd_lattice_ara_candidate import oddceil_transform, prime_flags, MAX_A

HERE = Path.cwd()
saved = json.loads((HERE / 'PN22_ODD_LATTICE_ARA_CANDIDATE_RESULTS.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN22_ODD_LATTICE_ARA_CANDIDATE_VALIDATION.json').read_text(encoding='utf-8'))
print('Loaded frozen result and independent validation.')
"""
        ),
        markdown("""## Data

Generate the integer inputs, projected candidates and exact prime table.
"""),
        code(
            """A = np.arange(1, MAX_A + 1, dtype=np.int64)
T = oddceil_transform(A)
flags = prime_flags(int(T.max()) + 140)
print('inputs:', A.size)
print('output range:', int(T.min()), 'to', int(T.max()))
print('unique outputs:', np.unique(T).size)
assert np.unique(T).size == A.size
"""
        ),
        markdown("""## Results

First verify the four piecewise branches and their exact residue lanes.
"""),
        code(
            """for remainder in range(4):
    sample = A[A % 4 == remainder][:3]
    print('A mod 4 =', remainder, 'samples:', list(zip(sample.tolist(), oddceil_transform(sample).tolist())))
residues = sorted(set((T % 14).tolist()))
print('output residues mod 14:', residues)
assert residues == [1, 5, 9, 13]
"""
        ),
        code(
            """low, high = int(T.min()), int(T.max())
output_range = np.arange(low, high + 1, dtype=np.int64)
odd = output_range[(output_range & 1) == 1]
coprime14 = output_range[np.gcd(output_range, 14) == 1]
matched = output_range[np.isin(output_range % 14, [1, 5, 9, 13])]
rates = {
    'ARA candidates': float(flags[T].mean()),
    'raw odds': float(flags[odd].mean()),
    'coprime to 14': float(flags[coprime14].mean()),
    'exact matched lanes': float(flags[matched].mean()),
}
for name, rate in rates.items():
    print(name, f'{100*rate:.6f}%')
assert np.array_equal(T, matched)
assert rates['ARA candidates'] == rates['exact matched lanes']
"""
        ),
        code(
            """print('worked examples')
for row in saved['examples']:
    print(row['A'], '->', row['T_A'], 'prime' if row['T_A_is_prime'] else 'composite')
print('perfect-power candidate rate:', saved['subgroups']['all_unique_perfect_powers']['candidate_prime_rate'])
print('perfect-power matched control:', saved['subgroups']['all_unique_perfect_powers']['matched_local_control_prime_rate'])
assert saved['decision']['wheel_crosswalk'] is True
assert saved['decision']['blind_target_authorized'] is False
print('independent validation:', validation['status'], validation['checks_passed'], '/', validation['checks_total'])
assert validation['status'] == 'PASS'
"""
        ),
        markdown(
            """## Takeaways

1. Half-integer ridges from odd inputs are handled coherently by a predeclared upward odd-lattice projection.
2. The transformation exactly avoids the factor-2 and factor-7 schedules, giving a real 16.65% lift over raw odds.
3. It contains no enrichment beyond its exact modulo-14 lanes, and perfect-power inputs underperformed same-lane local controls.
4. An additional independently defined ARA term would be required to handle remaining factor collisions before any fresh prime prediction.
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
    namespace = {"__name__": "__pn22_notebook__"}
    failures = []
    count = 0
    old_cwd = Path.cwd()
    os.chdir(HERE)
    try:
        for index, cell in enumerate(cells):
            if cell["cell_type"] != "code":
                continue
            count += 1
            cell["execution_count"] = count
            stream = io.StringIO()
            try:
                with contextlib.redirect_stdout(stream):
                    exec("".join(cell["source"]), namespace)
                output = stream.getvalue()
                if output:
                    cell["outputs"] = [{"name": "stdout", "output_type": "stream", "text": output.splitlines(keepends=True)}]
            except Exception as exc:
                failures.append({"cell_index": index, "error": repr(exc), "traceback": traceback.format_exc()})
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
        "validation_id": "PN22/NOTEBOOK-EXECUTION/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "code_cells_executed": count,
        "code_cells_total": sum(cell["cell_type"] == "code" for cell in cells),
        "failures": failures,
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

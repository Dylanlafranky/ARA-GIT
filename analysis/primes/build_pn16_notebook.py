"""Build and execute the PN16 reproducibility notebook without nbformat/nbclient."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "PN16_ORDERED_WHOLE_WAVE_LIFT.ipynb"
VALIDATION = HERE / "PN16_NOTEBOOK_EXECUTION_VALIDATION.json"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str, namespace: dict, number: int) -> dict:
    stream = io.StringIO()
    error = None
    try:
        with contextlib.redirect_stdout(stream):
            exec(compile(source, f"<PN16 notebook cell {number}>", "exec"), namespace)
    except Exception as exc:  # surfaced into the notebook and build failure below
        error = exc
    outputs = []
    if stream.getvalue():
        outputs.append({
            "name": "stdout",
            "output_type": "stream",
            "text": stream.getvalue().splitlines(keepends=True),
        })
    if error is not None:
        outputs.append({
            "ename": type(error).__name__,
            "evalue": str(error),
            "output_type": "error",
            "traceback": [f"{type(error).__name__}: {error}"],
        })
    return {
        "cell_type": "code",
        "execution_count": number,
        "metadata": {},
        "outputs": outputs,
        "source": source.splitlines(keepends=True),
    }


sections = [
    (
        "markdown",
        r"""# tl;dr

PN16 tests the ordered whole-wave rule `A+B -> AB`, `AB+BA -> next rung` on exact prime-wheel sieving.

The result is precise: forward `AB` and reverse `BA` have different partial histories, but their completed masks are
identical. Recombining that completed identity with its reversal is idempotent and does **not** make the next rung.
The completed p17 web instead locates `19` as its first quiet node; retaining 19 as the new relation removes exactly
one lift of every p17 survivor and constructs the p19 wheel exactly. Independent validation passed 71/71 checks.
""",
    ),
    (
        "code",
        """from pathlib import Path
import csv, hashlib, json, math

HERE = Path(r'F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\primes')
def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

result = json.loads((HERE / 'PN16_ORDERED_WHOLE_WAVE_LIFT_RESULTS.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN16_ORDERED_WHOLE_WAVE_LIFT_VALIDATION.json').read_text(encoding='utf-8'))
print(result['status'])
print('Protocol hash:', result['protocol_sha256'])
print('Independent validation:', validation['passed_count'], '/', validation['check_count'])
""",
    ),
    (
        "markdown",
        r"""# Context & Methods

For the first `k` prime gates, `AB` applies the gates in ascending order and `BA` applies the same gates in
descending order. Each intermediate survivor mask is retained. The completed masks are then compared with the
direct coprimality identity.

For the vertical lift, the first integer above the terminal prime that survives the complete parent web is recovered
without supplying the next prime to the builder. That quiet node becomes the new gate.

This is an exact deterministic structural test. It is not statistical estimation and has no sampling uncertainty.
It is also not historically blind: code isolation checks the translation and implementation, not the established
prime sequence's novelty.
""",
    ),
    (
        "code",
        """print('terminal | period | phi(parent) | max AB/BA partial disagreement | completed disagreement | quiet node')
for row in result['materialized_rungs']:
    print(f"{row['terminal_prime']:>8} | {row['period']:>7,} | {row['expected_totient']:>11,} | "
          f"{row['max_partial_hamming_fraction']:.6f} | {row['final_hamming_count']:>22} | "
          f"{row['first_quiet_node']}")
""",
    ),
    (
        "markdown",
        r"""# Data

The data are exact integer survivor masks over complete primorial periods. Development parents end at
`5, 7, 11, 13`; the code-isolated target parent ends at `17`. The target lift has period
`17# * 19 = 9,699,690`. A separate lightweight check repeats the quiet-node identity for every consecutive prime
pair through terminal prime 997.
""",
    ),
    (
        "code",
        """paths = list(csv.DictReader((HERE / 'PN16_ORDERED_WHOLE_WAVE_LIFT_PATHS.csv').open(encoding='utf-8')))
target_paths = [row for row in paths if int(row['terminal_prime']) == 17]
print('p17 ordered path')
print('depth | forward gate | reverse gate | forward survivors | reverse survivors | disagreement')
for row in target_paths:
    print(f"{int(row['depth']):>5} | {int(row['forward_gate']):>12} | {int(row['reverse_gate']):>12} | "
          f"{int(row['forward_survivors']):>17,} | {int(row['reverse_survivors']):>17,} | "
          f"{float(row['hamming_fraction']):.6f}")
""",
    ),
    (
        "markdown",
        r"""# Results

The decisive distinction is between a **path relation** and a **completed identity**. Order is strongly visible
during the path, yet the final projection commutes. The next rung is created only after the parent web identifies
the new quiet node and that new gate is retained.
""",
    ),
    (
        "code",
        """lift = result['target_lift']
print('Recovered quiet node:', lift['recovered_quiet_node'])
print('Parent period:', f"{lift['parent_period']:,}")
print('Child period:', f"{lift['child_period']:,}")
print('Parent survivors repeated 19 times:', f"{lift['tiled_parent_survivors']:,}")
print('Newly released by gate 19:', f"{lift['newly_released']:,}")
print('Child survivors:', f"{lift['child_survivors']:,}")
print('Missing relation among parent survivors:', f"{lift['missing_relation_fraction_given_parent_survival']:.9f}")
print('Same identity + reversal equals child:', lift['same_identity_recombination_equals_child'])
print('New gate lift equals direct child:', lift['lifted_equals_direct_child'])
print('Quiet-node theorem-scale checks:', result['theorem_scale_quiet_nodes']['pair_count'], 'all pass =', result['theorem_scale_quiet_nodes']['all_pass'])
""",
    ),
    (
        "markdown",
        r"""# Takeaways

1. The user's ordered-coupling intuition survives: `AB` and `BA` are distinguishable while the process is open.
2. A completed sieve whole and its simple reversal are not independent next-rung poles; they coarse-grain to one
   identical parent identity.
3. The current parent nevertheless contains an exact bottom-up next-prime rule: its first quiet node is the next
   prime.
4. The most faithful Information³ reading at this grain is therefore **parent whole + next survivor + their new gate
   relation**, not **parent whole + reversed copy alone**.
5. This is an exact ARA crosswalk of the recursive wheel sieve, not a faster prime algorithm or a new prime theorem.
""",
    ),
]

namespace: dict = {}
cells = []
execution_count = 0
for kind, source in sections:
    if kind == "markdown":
        cells.append(markdown(source))
    else:
        execution_count += 1
        cells.append(code(source, namespace, execution_count))

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
errors = [
    output
    for cell in cells
    if cell.get("cell_type") == "code"
    for output in cell.get("outputs", [])
    if output.get("output_type") == "error"
]
if errors:
    raise RuntimeError(errors)
OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
VALIDATION.write_text(
    json.dumps(
        {
            "status": "PASS",
            "notebook": OUTPUT.name,
            "total_cells": len(cells),
            "code_cells": execution_count,
            "executed_code_cells": execution_count,
            "error_outputs": 0,
            "execution_method": "standard-library notebook-v4 fallback because nbformat/nbclient are unavailable",
            "required_sections": ["tl;dr", "Context & Methods", "Data", "Results", "Takeaways"],
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
print(OUTPUT)

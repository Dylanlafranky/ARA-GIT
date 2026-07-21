"""Build and execute the PN18 reproducibility notebook with the standard library."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "PN18_RECURSIVE_TEARA_PRODUCT_TREE.ipynb"
VALIDATION = HERE / "PN18_NOTEBOOK_EXECUTION_VALIDATION.json"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def execute(source: str, namespace: dict, number: int) -> dict:
    stream = io.StringIO()
    error = None
    try:
        with contextlib.redirect_stdout(stream):
            exec(compile(source, f"<PN18 notebook cell {number}>", "exec"), namespace)
    except Exception as exc:
        error = exc
    outputs = []
    if stream.getvalue():
        outputs.append({"name": "stdout", "output_type": "stream", "text": stream.getvalue().splitlines(keepends=True)})
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
    ("markdown", r"""## tl;dr

PN18 recursively paired every lower prime child into one product parent, paired local p29-wheel candidates into a
second tree, and used GCD as their relation. At the fresh anchor `700,000,000,000`, it sealed `+9` before target
primality was checked. Independent validation confirmed `700,000,000,009` as the first prime above the anchor and
passed `36/36` checks.

The recursion is exact but not a genuine compression or speed improvement. The child root is a 1,205,845-bit
integer, and the full construction was slower and larger than efficient established controls.
"""),
    ("code", """from pathlib import Path
import hashlib, json

HERE = Path(r'F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\primes')
prediction = json.loads((HERE / 'PN18_RECURSIVE_TEARA_PRODUCT_TREE_PREDICTION.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN18_RECURSIVE_TEARA_PRODUCT_TREE_VALIDATION.json').read_text(encoding='utf-8'))
cost = json.loads((HERE / 'PN18_COST_AUDIT.json').read_text(encoding='utf-8'))
target = prediction['target']
print('Sealed candidate:', f"{target['predicted_integer']:,}")
print('Correction:', target['correction'])
print('Independent first-prime validation:', validation['candidate_is_first_prime_above_anchor'])
print('Checks:', validation['passed_count'], '/', validation['check_count'])
"""),
    ("markdown", r"""## Context & Methods

### Key Assumptions

- The exact prime ridge is the absence of every prime-factor child through the square-root boundary.
- Multiplying distinct lower prime children is mathematically lossless by unique factorization, although decoding the
  factors from the product is not cheap.
- A branch GCD greater than one proves that at least one candidate collides; it cannot certify that every leaf is
  composite, so unresolved branches must be descended.
- The mathematics is established primorial/product-tree/batch-GCD arithmetic expressed as recursive ARA parents.

For lower children `q`, candidate branch `I`, anchor `N` and fixed window `W`, PN18 uses

`G = product(q <= sqrt(N+W-1))`, `M_I = product(N+t for t in I)`, and `R_I = gcd(G,M_I)`.
At a leaf, `R=1` is the exact quiet factor ridge.
"""),
    ("code", """print('Development integrity')
print('anchor | children | correction | prediction | exact')
for row in prediction['development']:
    print(f"{row['anchor']:>15,} | {row['child_count']:>8,} | {row['correction']:>10} | "
          f"{row['predicted_integer']:>15,} | {row['matches_development_control']}")
"""),
    ("markdown", r"""## Data

The source is exact integer arithmetic. The fresh block contains 65,536 offsets. Its complete square-root inventory
contains 66,650 prime children through gate 836,657. The primary prediction packet and child-product root were
hashed before independent target validation.
"""),
    ("code", """fields = [
    ('anchor', target['anchor']),
    ('block end', target['block_end']),
    ('sqrt boundary', target['sqrt_block_end_floor']),
    ('child count', target['child_count']),
    ('child root bits', target['child_root_bit_length']),
    ('p29 candidates in window', target['candidate_count_in_window_after_p29']),
    ('candidate tree nodes', target['candidate_tree_nodes']),
    ('GCD nodes visited', target['query']['gcd_nodes_visited']),
    ('explicit leaves queried', target['query']['explicit_candidate_leaves_queried']),
]
for label, value in fields:
    print(f'{label}: {value:,}' if isinstance(value, int) else f'{label}: {value}')
print('Child-root SHA-256:', target['child_root_sha256'])
"""),
    ("markdown", r"""## Results

The first two p29-wheel leaves, offsets `+1` and `+3`, shared lower-prime factors with the child parent. Offset `+9`
had GCD one and was sealed. Direct root-GCD, independent segmented sieve, deterministic Miller-Rabin and full trial
division all returned the same answer.
"""),
    ("code", """print('Result')
print('correction:', target['correction'])
print('candidate:', f"{target['predicted_integer']:,}")
print('p29 rank:', target['p29_candidate_rank_through_prediction'])
print('odd candidates through answer:', target['odd_scan_candidates_through_prediction'])
print('direct GCD reconstruction:', validation['independent_direct_root_gcd_correction'])
print('segmented-sieve reconstruction:', validation['independent_segmented_sieve_correction'])
print('first prime:', validation['candidate_is_first_prime_above_anchor'])

print('\\nInformation sizes (bytes)')
for label, value in [
    ('child product root', target['child_root_byte_length']),
    ('uint32 child list', target['child_list_uint32_bytes']),
    ('one-bit odd sieve', target['one_bit_odd_sieve_bytes']),
    ('PN17-sized collision field', target['pn17_collision_field_bytes']),
    ('candidate-tree ideal payload', target['candidate_tree_transient_payload_bytes_ceil']),
]:
    print(f'{label:32s} {value:>10,}')

print('\\nPost-target median implementation seconds')
for name, record in cost['results'].items():
    print(f"{name:48s} {record['median_seconds']:.9f}")
"""),
    ("markdown", r"""## Takeaways

1. Recursive child-to-parent pairing preserved the exact PN17 quiet ridge on five opened anchors and one fresh
   anchor.
2. The fresh `+9` result was sealed before target primality and independently validated.
3. The child product is a reusable operational parent, and GCD is an exact informative relation between that parent
   and a candidate identity.
4. “One integer” is not a low-dimensional state here: the root contains 1,205,845 bits, is larger than a one-bit
   sieve and PN17's collision field, and the candidate tree adds about 735 KB of ideal payload.
5. The present construction is an exact ARA crosswalk of established product-tree/batch-GCD primality mathematics,
   not a new prime theorem or faster search algorithm.
6. The original frozen validator had a receipt-only JSON failure on the giant integer. The unchanged prediction was
   validated under a hashed v1.1 serialization amendment, passing 36/36 checks.
"""),
]


namespace: dict = {}
cells = []
execution_count = 0
for kind, source in sections:
    if kind == "markdown":
        cells.append(markdown(source))
    else:
        execution_count += 1
        cells.append(execute(source, namespace, execution_count))

errors = [
    output
    for cell in cells
    if cell.get("cell_type") == "code"
    for output in cell.get("outputs", [])
    if output.get("output_type") == "error"
]
if errors:
    raise RuntimeError(errors)

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
VALIDATION.write_text(json.dumps({
    "status": "PASS",
    "notebook": OUTPUT.name,
    "total_cells": len(cells),
    "code_cells": execution_count,
    "executed_code_cells": execution_count,
    "error_outputs": 0,
    "execution_method": "standard-library notebook-v4 fallback because nbformat/nbclient are unavailable",
    "required_sections": ["tl;dr", "Context & Methods", "Data", "Results", "Takeaways"],
}, indent=2) + "\n", encoding="utf-8")
print(OUTPUT)

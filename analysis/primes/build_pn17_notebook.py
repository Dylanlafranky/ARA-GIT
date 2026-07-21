"""Build and execute the PN17 reproducibility notebook without nbformat/nbclient."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "PN17_ONE_SHOT_LOCAL_RIDGE.ipynb"
VALIDATION = HERE / "PN17_NOTEBOOK_EXECUTION_VALIDATION.json"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def execute(source: str, namespace: dict, number: int) -> dict:
    stream = io.StringIO()
    error = None
    try:
        with contextlib.redirect_stdout(stream):
            exec(compile(source, f"<PN17 notebook cell {number}>", "exec"), namespace)
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

PN17 placed one arbitrary anchor at `400,000,000,000`, decompressed the complete lower-child phase field once, and
sealed `+19` as the first quiet factor ridge before checking a target prime label. Independent validation confirmed
that `400,000,000,019` is prime and that every intervening integer is composite (`26/26` checks).

The full child vector works exactly because it is the standard segmented-sieve collision mask in ARA coordinates.
Three simple scalar A/B averages did not select +19. The remaining new-theory problem is therefore compression of
the child web without erasing its periods and phases.
"""),
    ("code", """from pathlib import Path
import hashlib, json

HERE = Path(r'F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\primes')
prediction = json.loads((HERE / 'PN17_ONE_SHOT_LOCAL_RIDGE_PREDICTION.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'PN17_ONE_SHOT_LOCAL_RIDGE_VALIDATION.json').read_text(encoding='utf-8'))
diagnostic = json.loads((HERE / 'PN17_SCALAR_RIDGE_DIAGNOSTIC.json').read_text(encoding='utf-8'))
print('Sealed candidate:', prediction['target']['predicted_integer'])
print('Correction:', prediction['target']['correction'])
print('Independent first-prime validation:', validation['candidate_is_first_prime_above_anchor'])
print('Checks:', validation['passed_count'], '/', validation['check_count'])
"""),
    ("markdown", r"""## Context & Methods

### Key Assumptions

- “Prime ridge” is operationalized as a quiet factor ridge: no lower prime child collides through `sqrt(n)`.
- The complete child vector is permitted; no scalar TE-ARA aggregation law is assumed.
- The target builder may generate lower prime children but may not call a target primality function or read nearby
  target prime labels.
- The result is compared with a standard segmented sieve, which is mathematically the same collision field.

For each offset `t`, the calculation counts lower-child collisions. The correction is the first positive offset with
count zero.
"""),
    ("code", """print('Development anchors')
print('anchor | correction | prediction | lower children | pass')
for row in prediction['development']:
    print(f"{row['anchor']:>12,} | {row['correction']:>10} | {row['predicted_integer']:>12,} | "
          f"{row['child_count']:>14,} | {row['matches_development_control']}")
"""),
    ("markdown", r"""## Data

The source is exact integer arithmetic. The target block contains 65,536 offsets and 51,526 lower prime children,
ending at gate 632,447. The binary collision field was sealed with the prediction and reconstructed independently.
The equal-gap control uses the already-opened PN7C R11 actual-prime gap packet.
"""),
    ("code", """target = prediction['target']
print('Target anchor:', f"{target['anchor']:,}")
print('Child count:', f"{target['child_count']:,}")
print('Child ceiling:', f"{target['child_ceiling']:,}")
print('First quiet offset:', target['correction'])
print('Sealed integer:', f"{target['predicted_integer']:,}")
print('Quiet offsets in full block:', f"{target['quiet_offsets_in_block']:,}")
print('Collision-field SHA-256:', target['collision_field_sha256'])
"""),
    ("markdown", r"""## Results

The target passed both independent deterministic Miller-Rabin and full trial division, and no earlier integer was
prime. Baselines are reported honestly: odd scanning would inspect 10 odd candidates; a p29 wheel would retain five;
the complete ARA calculation used 51,526 child phases and is identical to a local segmented sieve.
"""),
    ("code", """print('Baselines:', prediction['baselines'])
print('Equal-gap control:', prediction['equal_gap_falsification_control'])
print('\\nSimple scalar ridge diagnostics')
for name, record in diagnostic['methods'].items():
    print(name, {
        'best_offset': record['best_scalar_ridge_offset_in_opened_range'],
        'best_is_quiet': record['best_scalar_ridge_is_quiet'],
        'prime_rank': record['sealed_prime_rank_by_scalar_ridge_error'],
        'anchor_error': record['anchor_ridge_error'],
    })
"""),
    ("markdown", r"""## Takeaways

1. Dylan's intended local direction is executable: begin at the desired scale, decompress the child web once, and
   solve for the nearest quiet ridge.
2. The result is exact and cleanly sealed, but its current implementation is a segmented sieve crosswalk rather than
   a faster prime algorithm.
3. A prime node is not generally raw incoming-gap equals outgoing-gap; that control hits only about 2.09% on R11.
4. Averaging the child A/B states erases the modular locations. The successful step is recursively retaining the
   identities inside “Other.”
5. The next test needs a predeclared low-dimensional coupling law that predicts the correction without rebuilding all
   51,526 collision lanes.
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

"""Build and execute the PN10B event-geometry notebook without nbformat."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "PN10B_EVENT_GEOMETRY_DIAGNOSTIC.ipynb"
VALIDATION = ROOT / "PN10B_EVENT_NOTEBOOK_VALIDATION.json"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def execute_cell(source: str, namespace: dict, count: int) -> dict:
    stream = io.StringIO()
    error = None
    try:
        with contextlib.redirect_stdout(stream):
            exec(compile(source, f"<PN10B event notebook cell {count}>", "exec"), namespace)
    except Exception as exc:
        error = exc
    outputs = []
    if stream.getvalue():
        outputs.append({"name": "stdout", "output_type": "stream", "text": stream.getvalue().splitlines(keepends=True)})
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


INTRO = r"""# PN10B event-centred geometry diagnostic

## tl;dr

The frozen PN10B predictive verdict remains **NULL**, but that verdict does not mean the geometry was empty. At a prime node the parent factor-survival coordinate reaches an exact **1.0 ridge**, with immediate odd offsets dropping to the even-number trough near **0.062701**. Inside the node, the nine paid-gate children remain strongly asymmetric: their individual A readings span almost the full 0–2 line, and the first prime's vector runs from **0.071972** to **1.435762**. Across 45,166 primes those child readings aggregate to **0.999861**, but survivor composites aggregate to **0.998614**, so the child geometry is real while its prime-specific separation is negligible in this representation.

This notebook is a **post-hoc descriptive disclosure**, not a fresh prediction test.

## Context & Methods

The fresh interval is `[4,000,000,000, 4,001,000,000)`. PN10B had already defined nine paid-gate children using the largest nine prime gates `q <= n^0.45`:

- `A_j(n) = 2 (n mod q_j) / q_j`
- `B_j(n) = 2 - A_j(n)`
- child centroid: mean of the nine A readings
- child dispersion: mean absolute distance from the 1.0 ridge
- adjacent coupling: mean `(A_j-1)(A_{j+1}-1)`
- parent factor progress: `1` for a prime, otherwise `2 log(LPF(n)) / log(n)`

### Key Assumptions

The parent coordinate is a factor-survival description, not an advance forecast: a prime receives 1.0 only after surviving every required divisor test through its square root. The child coordinate is the paid-gate proxy tested in PN10B; it may not be the final internal child definition intended by the full ARA ontology.
"""


SOURCES = [
    r"""from pathlib import Path
import csv, json

ROOT = Path(r'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\primes')
results = json.loads((ROOT / 'PN10B_EVENT_GEOMETRY_RESULTS.json').read_text(encoding='utf-8'))
validation = json.loads((ROOT / 'PN10B_EVENT_GEOMETRY_VALIDATION.json').read_text(encoding='utf-8'))
with (ROOT / 'PN10B_EVENT_CENTERED_TRACES.csv').open(newline='', encoding='utf-8') as handle:
    traces = list(csv.DictReader(handle))
with (ROOT / 'PN10B_CHILD_LANDMARK_COUNTS.csv').open(newline='', encoding='utf-8') as handle:
    landmarks = list(csv.DictReader(handle))
with (ROOT / 'PN10B_PRIME_CHILD_EXAMPLES.csv').open(newline='', encoding='utf-8') as handle:
    examples = list(csv.DictReader(handle))
print('## Data')
print(json.dumps(results['scope'], indent=2))
print('Independent validation:', validation['checks_passed'], '/', validation['checks_total'], 'passed=', validation['passed'])
""",
    r"""print('## Results — population geometry')
for population in ('prime', 'survivor_composite'):
    node = results['node_distributions'][population]
    print(population)
    for metric in ('child_centroid', 'child_dispersion', 'child_coupling', 'child_flip_count', 'pooled_child_phase_a'):
        row = node[metric]
        print(f"  {metric:<22} mean={row['mean']:.9f} sd={row['sd']:.9f} median={row['median']:.9f} range=[{row['min']:.9f},{row['max']:.9f}]")
print('standardized prime-minus-composite differences')
for metric, row in results['population_contrasts'].items():
    print(f"  {metric:<22} raw={row['prime_minus_survivor_composite_mean']:+.9f} standardized={row['standardized_mean_difference']:+.6f}")
""",
    r"""print('## Results — event-centred lead / at / lag')
selected = {-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10}
print('offset | prime rate | parent progress | child centroid | dispersion | coupling | flips')
for row in traces:
    if row['event'] == 'prime_center' and int(row['offset']) in selected:
        print(f"{int(row['offset']):>+3} {float(row['prime_rate']):11.6f} {float(row['parent_progress_mean']):16.9f} "
              f"{float(row['child_centroid_mean']):16.9f} {float(row['child_dispersion_mean']):11.9f} "
              f"{float(row['child_coupling_mean']):+11.9f} {float(row['child_flip_count_mean']):7.4f}")
""",
    r"""print('## Results — exact first-prime child vector')
print('rank q remainder A B signed_A_minus_1 coupling_to_next')
for row in examples:
    if row['example'] == 'first_prime':
        print(row['gate_rank'], row['gate_q'], row['remainder'], row['phase_a'], row['phase_b'],
              row['signed_orientation'], row['coupling_to_next_rank'])
""",
    r"""print('## Results — landmark occupancy shares')
for row in landmarks:
    print(f"{row['population']:<20} {row['landmark_region']:<27} {float(row['share']):.9f}")
print('Static figure:', ROOT / 'PN10B_EVENT_GEOMETRY_FIGURE.png')
""",
]


TAKEAWAYS = r"""## Takeaways

1. **The prime event is a sharp parent ridge.** The parent factor-progress coordinate is 1.0 at the prime and falls into the parity-driven trough on every odd offset around an odd prime.
2. **The internal paid-gate children are not quiet.** A single prime can contain large A/B asymmetries and several sign flips even when population aggregation sits near 1.0.
3. **The population ridge is cancellation across nodes.** Pooled prime child A is 0.999861, yet individual prime centroids range from 0.499789 to 1.426639.
4. **That child pattern is not prime-specific here.** Survivor composites have almost the same centroid, dispersion, coupling, flip-count and landmark distributions. All standardized mean differences are below 0.015.
5. **Therefore both statements must be reported.** PN10B is NULL as a prime-ranking test, while its post-hoc geometry shows an exact parent event ridge and rich but non-discriminating child waves.

The next confirmatory step, if pursued, must freeze what counts as the prime node's *internal* Phase A and Phase B before opening a new interval.
"""


def main() -> None:
    namespace: dict = {}
    cells = [markdown(INTRO)]
    for number, source in enumerate(SOURCES, 1):
        cells.append(execute_cell(source, namespace, number))
    cells.append(markdown(TAKEAWAYS))
    errors = [
        output
        for cell in cells
        if cell.get("cell_type") == "code"
        for output in cell["outputs"]
        if output["output_type"] == "error"
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
    OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
    if errors:
        raise RuntimeError(errors)
    VALIDATION.write_text(
        json.dumps(
            {
                "status": "PASS",
                "notebook": OUTPUT.name,
                "total_cells": len(cells),
                "code_cells": len(SOURCES),
                "error_outputs": 0,
                "execution_method": "standard-library notebook-v4 fallback because nbformat/nbclient are unavailable",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()

"""Build and execute the PN10C diagnostic notebook without nbformat."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "PN10C_MOD6_THREE_LANE_DIAGNOSTIC.ipynb"
VALIDATION = ROOT / "PN10C_NOTEBOOK_EXECUTION_VALIDATION.json"


def markdown(source: str) -> dict:
    return {"cell_type":"markdown","metadata":{},"source":source.splitlines(keepends=True)}


def execute_cell(source: str, namespace: dict, count: int) -> dict:
    stream=io.StringIO(); error=None
    try:
        with contextlib.redirect_stdout(stream):
            exec(compile(source,f"<PN10C notebook cell {count}>","exec"),namespace)
    except Exception as exc:
        error=exc
    outputs=[]
    if stream.getvalue():
        outputs.append({"name":"stdout","output_type":"stream","text":stream.getvalue().splitlines(keepends=True)})
    if error:
        outputs.append({"ename":type(error).__name__,"evalue":str(error),"output_type":"error","traceback":[f"{type(error).__name__}: {error}"]})
    return {"cell_type":"code","execution_count":count,"metadata":{},"outputs":outputs,"source":source.splitlines(keepends=True)}


INTRO=r"""# PN10C mod-6 three-lane coupling diagnostic

## tl;dr

The three lane families marked in the PN10B parent trace are reproducible. Red and blue exchange roles when a prime centre changes from `1 mod 6` to `5 mod 6`: the swap is **+0.323729**, and reflecting the traces reduces their mismatch by **99.52%**. Black is invariant between the two orientations, but it is not an independently stronger third lane after conditioning; it is **0.004060 lower** than the currently admissible coloured branch. Black is therefore the shared mod-6 route at this grain. It then decomposes into a rotating factor-5 child trough in the mod-30 wheel.

The result is a **post-hoc structural diagnostic**. It does not alter PN10B's registered `NULL` verdict and does not claim a new theorem about primes.

## Context & Methods

The frozen protocol uses the already-open interval `[4,000,000,000, 4,001,000,000)`, all 45,156 interior prime centres, a `+-150` window, and a matched control of composite centres coprime to 6. Parent factor progress is `1` for a prime and `2 log(LPF(n))/log(n)` for a composite.

### Key assumptions

The modular mechanism is established arithmetic. The diagnostic tests whether the ARA decomposition correctly identifies the conditional orientation, common lane and child hierarchy; it is not an independent discovery of divisibility laws.
"""


SOURCES=[
r"""from pathlib import Path
import csv, json
ROOT=Path(r'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\primes')
results=json.loads((ROOT/'PN10C_MOD6_THREE_LANE_RESULTS.json').read_text(encoding='utf-8'))
validation=json.loads((ROOT/'PN10C_MOD6_THREE_LANE_VALIDATION.json').read_text(encoding='utf-8'))
def read_csv(name):
    with (ROOT/name).open(newline='',encoding='utf-8') as handle: return list(csv.DictReader(handle))
lanes=read_csv('PN10C_MOD6_LANE_SUMMARY.csv')
matrix=read_csv('PN10C_MOD30_BLACK_CHILD_MATRIX.csv')
offsets=read_csv('PN10C_MOD6_OFFSET_PROFILE.csv')
examples=read_csv('PN10C_MOD6_WORKED_EXAMPLES.csv')
print('## Data')
print(json.dumps(results['scope'],indent=2))
print('Independent validation:',validation['checks_passed'],'/',validation['checks_total'],validation['status'])
""",
r"""print('## Results — frozen contrasts')
for name,row in results['headline_contrasts'].items():
    print(f"{name:<37} estimate={row['estimate']:+.9f} 95%CI=[{row['ci95_low']:+.9f},{row['ci95_high']:+.9f}]")
print('reflection:',json.dumps(results['reflection_test'],indent=2))
""",
r"""print('## Results — prime lane means')
print('centre lane direction parent_progress prime_rate survivor_rate div3 div5')
for row in lanes:
    if row['center_group']=='prime' and row['direction']=='all':
        print(row['center_mod6'],row['offset_lane_mod6'],row['direction'],
              f"{float(row['parent_progress_mean']):.9f}",f"{float(row['prime_rate']):.9f}",
              f"{float(row['survivor_rate']):.9f}",row['divisible_by_3_rate'],row['divisible_by_5_rate'])
""",
r"""print('## Results — black child matrix')
print('p_mod5 m_mod5 collision parent_progress prime_rate div5')
for row in matrix:
    if row['center_group']=='prime':
        print(row['center_mod5'],row['black_child_m_mod5'],row['predicted_factor5_collision'],
              f"{float(row['parent_progress_mean']):.9f}",f"{float(row['prime_rate']):.9f}",row['divisible_by_5_rate'])
""",
r"""print('## Results — matched composite control')
print(json.dumps(results['matched_composite_control'],indent=2))
print('Mechanism checks:',json.dumps(results['mechanism_checks'],indent=2))
""",
r"""print('## Worked event example')
center=examples[0]['center_prime']
print('centre prime:',center)
print('offset n lpf prime progress div3 div5')
for row in examples:
    if row['center_prime']==center and -12<=int(row['offset'])<=12:
        print(row['offset'],row['n'],row['least_prime_factor'],row['is_prime'],
              f"{float(row['parent_progress']):.9f}",row['divisible_by_3'],row['divisible_by_5'])
print('Static figure:',ROOT/'PN10C_MOD6_THREE_LANE_FIGURE.png')
""",
]


TAKEAWAYS=r"""## Takeaways

1. **Red and blue are a conditional anti-phase pair.** Their identities are not fixed; the centre's mod-6 orientation determines which becomes the factor-3 trough.
2. **Black is the invariant common route.** It preserves both prime-admissible mod-6 orientations and does not remain stronger than the eligible coloured branch after conditioning.
3. **The common route has children.** Conditioning black by the centre's mod-5 orientation exposes the rotating factor-5 trough of the mod-30 wheel.
4. **The surrounding pattern is not prime-specific.** Matched coprime composites show the same swap. The prime's special feature here is the exact 1.0 event-centre ridge.
5. **The ARA decomposition is useful but the mechanism is established.** It recovered the correct hierarchical relation; this result alone is not a novel prime predictor or proof of universal fractality.

The next rigorous step is to freeze a `6 -> 30 -> 210` transformation and a nontrivial eligible-lane statistic, then test both on a new unopened interval.
"""


def main() -> None:
    namespace={}; cells=[markdown(INTRO)]
    for number,source in enumerate(SOURCES,1): cells.append(execute_cell(source,namespace,number))
    cells.append(markdown(TAKEAWAYS))
    errors=[o for c in cells if c.get('cell_type')=='code' for o in c['outputs'] if o['output_type']=='error']
    notebook={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3"}},"nbformat":4,"nbformat_minor":5}
    OUTPUT.write_text(json.dumps(notebook,indent=1,ensure_ascii=False),encoding='utf-8')
    if errors: raise RuntimeError(errors)
    VALIDATION.write_text(json.dumps({"status":"PASS","notebook":OUTPUT.name,"total_cells":len(cells),"code_cells":len(SOURCES),"error_outputs":0,"execution_method":"standard-library notebook-v4 fallback because nbformat/nbclient are unavailable"},indent=2)+'\n',encoding='utf-8')
    print(OUTPUT)


if __name__=='__main__': main()

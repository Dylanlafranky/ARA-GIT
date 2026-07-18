#!/usr/bin/env python3
"""Build and execute the PN3A adult-sieve reproducibility notebook."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN3A_ADULT_SIEVE_PATH_REPRODUCIBILITY.ipynb"
VALIDATION = HERE / "PN3A_NOTEBOOK_EXECUTION_VALIDATION.json"


def markdown(source: str) -> dict[str, object]:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str) -> dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def execute(cells: list[dict[str, object]]) -> dict[str, object]:
    namespace: dict[str, object] = {"__name__": "__pn3a_notebook__"}
    original_cwd = Path.cwd()
    executed = 0
    errors: list[str] = []
    try:
        os.chdir(HERE)
        for cell_index, cell in enumerate(cells):
            if cell["cell_type"] != "code":
                continue
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    exec(compile("".join(cell["source"]), f"PN3A-cell-{cell_index + 1}", "exec"), namespace, namespace)
                executed += 1
                cell["execution_count"] = executed
                captured = stdout.getvalue()
                if captured:
                    cell["outputs"] = [{"name": "stdout", "output_type": "stream", "text": captured.splitlines(keepends=True)}]
            except Exception as exc:
                errors.append(f"cell {cell_index + 1}: {type(exc).__name__}: {exc}")
                raise
    finally:
        os.chdir(original_cwd)
    code_cells = sum(cell["cell_type"] == "code" for cell in cells)
    return {
        "all_code_cells_executed": executed == code_cells,
        "executed_code_cells": executed,
        "total_code_cells": code_cells,
        "errors": errors,
    }


def main() -> None:
    cells = [
        markdown(
            """# PN3A: the adult sieve path behind the terminal prime reading

## tl;dr

The earlier PN3 target recorded only the terminal survivor/dead state. PN3A reconstructs the larger process: the exact prime at which each p29-wheel candidate, and each adjacent candidate pair, is first removed. That **adult survival/release path is real and measurable**. However, the local diagonal coordinate `U=(x+y)/2` does not predict death stage across the two primary scale transfers; every U, V and joint UV model worsens held-out log loss. The missing adult aspect is therefore not recovered as another ordinary local-gap wave.

At the billion scale, exact candidate survival is `0.305450510` versus the independent-sieve product's `0.342769498`. Their ratio is `0.891125`, within `0.0661%` of the established Mertens/PNT factor `exp(gamma)/2 = 0.890536`. The exact path follows the product closely through most of the sieve and separates mainly near the terminal boundary. This is an established-number-theory crosswalk, not new ARA predictive evidence. Independent validation passes `118/118`; the reserved p31 wheel remains unopened.
"""
        ),
        markdown(
            r"""## Context & Methods

For every number already coprime to primes through 29, define its first later divisor (d(n)), or zero if the number is prime. For a sieve threshold (q),

\[
\underbrace{S(q)}_{\substack{\text{fraction still connected}\text{to the survivor population}}}
=
\frac{\#\{n:d(n)=0\;\text{or}\;d(n)>q\}}{\#\{n\}},
\qquad
\underbrace{R(q)}_{\substack{\text{cumulative release}\text{by threshold }q}}
=1-S(q).
\]

This exact conservation pair is the neutral adult ARA path. Dylan retains the right to orient its Phase A/Phase B, Space/Time and up/down meanings.

The ordinary independent-sieve control is

\[
\underbrace{M(q)}_{\text{independent survival control}}
=\prod_{29<p\le q}\left(1-\frac1p\right),
\]

with (M(q)^2) for two independently surviving endpoints. The local child plane is rotated into the common diagonal (U=(x+y)/2) and its perpendicular difference (V=(y-x)/2). Twelve-bin U, V and UV lookups are trained on one opened decimal rung and tested on the next, with fixed Dirichlet shrinkage 64 and 100 within-location-block permutations.

This is an **opened-data diagnostic**, not a blind prediction and not a rescue of PN3. The method was written before this final run, but the same rungs were already known. The p31 PN1H wheel is prohibited.
"""
        ),
        markdown("""## Data

- Decimal windows: `[10^6,1.01*10^6)`, `[10^7,1.01*10^7)`, `[10^8,1.01*10^8)`, `[10^9,1.01*10^9)`.
- Candidate population: numbers surviving the p29 wheel.
- Adult event: first divisor above 29; zero is terminal survival.
- Edge event: earliest endpoint death; zero only when both endpoints survive.
- Primary transfers: R7 to R8 and R8 to R9.
- The sealed PN3 R9 packet is used only to verify exact terminal labels and local geometry.
"""),
        markdown("## Results\n\n### 1. Rebuild the complete adult path"),
        code(
            """import json
from pathlib import Path
import pn3a_adult_sieve_path as analysis

HERE = Path.cwd()
results = analysis.run()
print("Test:", results["test_id"])
print("Evidence class:", results["evidence_class"])
print("p31 accessed:", results["p31_accessed"])
print("Adult diagonal supported:", results["diagonal_rule_supported_on_both_edge_transfers"])
"""
        ),
        markdown("""![Exact adult survival and release](PN3A_ADULT_SIEVE_SURVIVAL_RELEASE.png)

The exact adult path is monotone: each later prime removes part of the remaining population. The independent product captures most of the slow envelope, while the exact prime-counting correction becomes most visible late in the path.
"""),
        markdown("### 2. Inspect survival, the established correction and divergence onset"),
        code(
            """print("rung  candidate   pair        candidate/product  pair/product^2  q at 10% candidate deviation")
for rung, row in results["rung_summaries"].items():
    cross = row["post_result_established_crosswalk"]
    onset = row["divergence_onset"]["candidate"]["relative_10pct"]
    onset_q = "none" if onset is None else str(onset["q"])
    print(f"{rung:>3}  {row['candidate_terminal_survival']:.9f}  {row['edge_terminal_survival']:.9f}  "
          f"{cross['candidate_actual_over_product']:.9f}        "
          f"{cross['edge_actual_over_product_squared']:.9f}       {onset_q}")

r9 = results["rung_summaries"]["r9"]
cross = r9["post_result_established_crosswalk"]
print("\\nR9 exp(gamma)/2:", cross["euler_mertens_factor_exp_gamma_over_2"])
print("R9 relative difference:", cross["candidate_relative_difference_from_euler_mertens"])
print("R9 1%, 5%, 10% divergence onsets:", r9["divergence_onset"])
"""
        ),
        markdown("""At R8 and R9, `actual/product` is nearly the known `exp(gamma)/2` correction. That agreement explains why the terminal mismatch is stable: an independent-factor sieve and prime density have different asymptotic normalisations. The pair ratio is close to, but not identical with, the square of that factor because adjacent prime survival contains additional dependence.
"""),
        markdown("### 3. Test whether the red diagonal is the adult coordinate"),
        code(
            """print("transfer          entity     U gain       V gain       UV gain  (bits/event; positive is useful)")
for train, test in (("r7", "r8"), ("r8", "r9")):
    for entity in ("candidate", "edge"):
        values = [results["primary_transfer"][f"{train}_to_{test}__{entity}__{model}"]["gain_bits_per_event"] for model in ("u", "v", "uv")]
        print(f"{train}->{test:2}          {entity:9}  {values[0]: .9f}  {values[1]: .9f}  {values[2]: .9f}")
"""
        ),
        markdown("""![Adult-child coupling diagnostic](PN3A_ADULT_CHILD_COUPLING.png)

Every transfer gain is negative. The U and V results also sit inside their shuffled-location null distributions. The heatmaps show local redistribution, but it does not remain stable enough across rungs to forecast where the adult path removes an event.
"""),
        markdown("### 4. Run the independent reconstruction"),
        code(
            """import pn3a_independent_validation as validator
validator.main()
validation = json.loads((HERE / "PN3A_INDEPENDENT_VALIDATION.json").read_text(encoding="utf-8"))
print("Independent validation:", validation["all_passed"])
print("Checks:", validation["passed"], "/", validation["total"])
assert validation["all_passed"]
assert validation["passed"] == validation["total"] == 118
assert results["p31_accessed"] is False
"""
        ),
        markdown(
            """## Takeaways

1. The prior terminal label really was a compressed cross-section of a larger adult survival/release process.
2. The adult process is smooth, scale-spanning and connection-heavy in Dylan's descriptive language. It is not recovered by the red U diagonal or its V perpendicular.
3. The late mismatch is quantitatively explained, for single candidates, by the established Mertens/PNT normalisation. Recovering that relation is a sound crosswalk but not unique support for ARA.
4. The unresolved candidate is now narrower: a large-scale number-line/counting coordinate, or a survivor-release relation near the terminal boundary, rather than another local gap child.
5. Any next predictive claim must be frozen on a genuinely fresh interval. PN3 remains a negative result and p31 remains reserved.

Full interpretation: `PN3A_ADULT_SIEVE_PATH_DIAGNOSTIC_REPORT.md`.
"""
        ),
    ]

    for index, cell in enumerate(cells, start=1):
        cell["id"] = f"pn3a-{index:02d}"
    execution = execute(cells)
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.14"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    validation = json.loads((HERE / "PN3A_INDEPENDENT_VALIDATION.json").read_text(encoding="utf-8"))
    outcome = {
        **execution,
        "notebook": NOTEBOOK.name,
        "notebook_exists": NOTEBOOK.exists(),
        "notebook_bytes": NOTEBOOK.stat().st_size,
        "full_analysis_reexecuted_inside_notebook": True,
        "independent_validation_reexecuted_inside_notebook": True,
        "independent_validation_checks": validation["total"],
        "p31_accessed": False,
    }
    VALIDATION.write_text(json.dumps(outcome, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(outcome, indent=2))


if __name__ == "__main__":
    main()

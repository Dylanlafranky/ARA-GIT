"""Build an executed, dependency-free notebook for the ARA probability audit.

The bundled runtime does not ship Jupyter's Python packages, so this builder
uses the public .ipynb JSON format directly.  It executes every code cell in a
shared namespace, captures stdout, and stores the resulting outputs in order.
"""

from __future__ import annotations

import contextlib
import io
import json
import traceback
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "ARA_PRETEST_CONSTRAINT_PROBABILITY_RESULTS.json"
OUTPUT = HERE / "ARA_PRETEST_CONSTRAINT_PROBABILITY_AUDIT.ipynb"


def markdown(source: str) -> dict[str, object]:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def code(source: str) -> dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


cells = [
    markdown(
        """# ARA pre-test constraint probability audit

## TL;DR

This notebook does **not** estimate the probability that ARA is true. It tests
how surprising the provisional historical ledger count would be under several
assumed background match rates, then sizes a prospective decoy-controlled
battery that can measure that missing rate directly.

The historical ledger records 15 clean hits and 31 misses/refutations. That
count is statistically unusual only if the chance that a flexible structural
statement is judged a match is below about 21.3%. The ledger does not yet
measure that background rate, so the historical result is sensitivity evidence,
not a global p-value.
"""
    ),
    markdown(
        """## Context and methods

**Question.** How unlikely is the recorded repetition of ARA-compatible
geometry if the declarations were made before lookup?

**Historical unit.** The strict binary tally in `FableConvo/PROVENANCE_LEDGER.md`:
clean A-tier hits versus recorded misses/refutations. Partial and contaminated
entries are excluded from the binary count.

**Sensitivity model.** If `p0` is the unknown background chance that one
eligible statement is judged a clean match, then

`X ~ Binomial(n = 46, p0)` and the reported quantity is `P(X >= 15)`.

This is intentionally conservative and incomplete: the statements are not
guaranteed independent, verdicts are provisional/self-scored, and `p0` is not
identified. Those limitations are the reason for the prospective decoy design.
"""
    ),
    code(
        """import json
from pathlib import Path

results_path = Path('ARA_PRETEST_CONSTRAINT_PROBABILITY_RESULTS.json')
results = json.loads(results_path.read_text(encoding='utf-8'))
profile = results['ledger_profile']
print('Clean hits:', profile['clean_hits'])
print('Misses/refutations:', profile['misses_or_refutations'])
print('Strict total:', profile['strict_binary_total'])
print('Observed hit rate: {:.2%}'.format(profile['strict_observed_hit_rate']))
print('Formal frozen protocols:', profile['formal_frozen_protocols']['count'])
print('Protocol domains:', profile['formal_frozen_protocols']['by_domain'])
"""
    ),
    markdown(
        """## Historical sensitivity result

The table below varies the unmeasured chance-match rate. A small tail
probability means 15 or more hits would be surprising under that particular
assumption. It does not choose the assumption for us.
"""
    ),
    code(
        """rows = results['historical_sensitivity']['rows']
print(f"{'assumed p0':>12}  {'P(X>=15)':>14}  {'reject at 5%':>13}")
for row in rows:
    print(f"{row['null_match_rate']:12.3f}  {row['tail_probability']:14.8g}  {str(row['reject_at_0_05']):>13}")
critical = results['historical_sensitivity']['critical_null_rate_at_alpha_0_05']
print()
print('Critical background match rate at alpha=0.05: {:.3%}'.format(critical))
"""
    ),
    markdown(
        """## Prospective decoy-controlled design

For each independent domain, hide one real target among nine matched decoys.
Freeze the ARA mapping and score before revealing which target is real. The
primary outcome is whether the real target receives the highest score. Under
exchangeability the null success rate is exactly 1/10, avoiding an invented
background rate.
"""
    ),
    code(
        """designs = results['prospective_decoy_design']['rows']
print(f"{'domains':>8}  {'critical wins':>13}  {'actual alpha':>12}  {'power if p=.4':>15}")
for row in designs:
    print(f"{row['independent_domains']:8d}  {row['critical_top_rank_wins']:13d}  {row['actual_alpha']:12.5f}  {row['power_if_true_rate_0_40']:15.3f}")
"""
    ),
    markdown(
        """## Data-quality findings

- The provenance ledger is explicit that its running tally is provisional and
  self-scored.
- Hits, rediscoveries, exact identities, exploratory probes and failures are
  not yet a single exchangeable class.
- Frozen protocols are currently concentrated in prime and electromagnetic
  work, so counting each protocol as an independent domain would inflate the
  apparent sample size.
- A blinded decoy audit of transcript statements can estimate historical
  matchability; a prospective cross-domain battery can test new mappings.
"""
    ),
    markdown(
        """## Takeaways

1. The record is worth testing: 15 clean hits among 46 strict outcomes is not a
   trivial observation.
2. Its statistical force cannot be stated without the missing chance-match
   rate and dependence structure.
3. The recommended first battery is 12 independent domains with nine decoys
   each. Four or more real-target top ranks has an exact null probability of
   about 0.0256.
4. This would test whether the declared geometry repeatedly discriminates real
   structures from matched alternatives. It would still not, by itself, prove
   that ARA is the universe's bedrock geometry.
"""
    ),
]


namespace: dict[str, object] = {}
execution_count = 0
for cell in cells:
    if cell["cell_type"] != "code":
        continue
    execution_count += 1
    cell["execution_count"] = execution_count
    source = "".join(cell["source"])
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            exec(compile(source, f"<cell {execution_count}>", "exec"), namespace)
        output_text = buffer.getvalue()
        if output_text:
            cell["outputs"] = [
                {
                    "name": "stdout",
                    "output_type": "stream",
                    "text": output_text.splitlines(keepends=True),
                }
            ]
    except Exception as error:  # pragma: no cover - builder must surface failure
        cell["outputs"] = [
            {
                "ename": type(error).__name__,
                "evalue": str(error),
                "output_type": "error",
                "traceback": traceback.format_exc().splitlines(),
            }
        ]
        raise


notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.12"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUTPUT.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
print(f"Built and executed {OUTPUT.name} with {execution_count} code cells.")

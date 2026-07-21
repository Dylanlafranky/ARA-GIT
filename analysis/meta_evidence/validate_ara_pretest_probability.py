"""Independent validation checks for the ARA pre-test probability pilot."""

from __future__ import annotations

import json
import math
import re
from decimal import Decimal, getcontext
from pathlib import Path


getcontext().prec = 60
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RESULTS = HERE / "ARA_PRETEST_CONSTRAINT_PROBABILITY_RESULTS.json"
NOTEBOOK = HERE / "ARA_PRETEST_CONSTRAINT_PROBABILITY_AUDIT.ipynb"
LEDGER = ROOT / "FableConvo" / "PROVENANCE_LEDGER.md"


def decimal_tail(n: int, k: int, probability: str) -> Decimal:
    p = Decimal(probability)
    one = Decimal(1)
    return sum(
        Decimal(math.comb(n, successes))
        * p**successes
        * (one - p) ** (n - successes)
        for successes in range(k, n + 1)
    )


payload = json.loads(RESULTS.read_text(encoding="utf-8"))
ledger_text = LEDGER.read_text(encoding="utf-8")
notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
checks: dict[str, bool] = {}

clean_match = re.search(r"A-tier clean hits:\s*(\d+)", ledger_text)
miss_match = re.search(r"Misses/refuted:\s*(\d+)", ledger_text)
checks["ledger_counts_found"] = clean_match is not None and miss_match is not None
checks["ledger_counts_match_results"] = (
    int(clean_match.group(1)) == payload["ledger_profile"]["clean_hits"] == 15
    and int(miss_match.group(1)) == payload["ledger_profile"]["misses_or_refutations"] == 31
)
checks["strict_total_is_46"] = payload["ledger_profile"]["strict_binary_total"] == 46
checks["observed_rate_exact"] = math.isclose(
    payload["ledger_profile"]["strict_observed_hit_rate"], 15 / 46, abs_tol=1e-15
)

rows = payload["historical_sensitivity"]["rows"]
checks["sensitivity_tail_recomputed"] = all(
    math.isclose(
        float(decimal_tail(46, 15, str(row["null_match_rate"]))),
        row["tail_probability"],
        rel_tol=1e-8,
        abs_tol=1e-14,
    )
    for row in rows
)
checks["tail_monotonic_in_null_rate"] = all(
    left["tail_probability"] < right["tail_probability"]
    for left, right in zip(rows, rows[1:])
)

critical = payload["historical_sensitivity"]["critical_null_rate_at_alpha_0_05"]
checks["critical_rate_brackets_alpha"] = (
    float(decimal_tail(46, 15, str(critical - 1e-8))) < 0.05
    and float(decimal_tail(46, 15, str(critical + 1e-8))) > 0.05
)

recommended = payload["prospective_decoy_design"]["recommended_initial_battery"]
alpha = float(decimal_tail(12, 4, "0.1"))
checks["decoy_alpha_recomputed"] = math.isclose(
    recommended["actual_alpha"], alpha, abs_tol=1e-15
)
checks["four_wins_is_first_5pct_gate"] = (
    float(decimal_tail(12, 3, "0.1")) > 0.05
    and float(decimal_tail(12, 4, "0.1")) <= 0.05
)

code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
checks["notebook_has_expected_cells"] = len(notebook["cells"]) == 9 and len(code_cells) == 3
checks["notebook_all_code_executed"] = all(
    isinstance(cell.get("execution_count"), int) for cell in code_cells
)
checks["notebook_has_no_error_outputs"] = not any(
    output.get("output_type") == "error"
    for cell in code_cells
    for output in cell.get("outputs", [])
)

failed = [name for name, passed in checks.items() if not passed]
result = {
    "status": "PASS" if not failed else "FAIL",
    "checks_passed": sum(checks.values()),
    "checks_total": len(checks),
    "checks": checks,
    "failed": failed,
}
(HERE / "ARA_PRETEST_CONSTRAINT_PROBABILITY_VALIDATION.json").write_text(
    json.dumps(result, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(result, indent=2))
if failed:
    raise SystemExit(1)

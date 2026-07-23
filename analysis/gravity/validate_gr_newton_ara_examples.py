#!/usr/bin/env python3
"""Independent validation for GR_NEWTON_ARA_EXAMPLES_RESULTS.json."""

from __future__ import annotations

from decimal import Decimal, getcontext
import json
from pathlib import Path
import random


getcontext().prec = 50

HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "GR_NEWTON_ARA_EXAMPLES_RESULTS.json"
VALIDATION_PATH = HERE / "GR_NEWTON_ARA_EXAMPLES_VALIDATION.json"


def rel_error(actual: Decimal, expected: Decimal) -> Decimal:
    if expected == 0:
        return abs(actual - expected)
    return abs(actual - expected) / abs(expected)


def main() -> None:
    data = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    c = Decimal(str(data["constants"]["c_m_s_exact"]))
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    for row in data["compactness_examples"]:
        mu = Decimal(str(row["mu_m3_s2"]))
        radius = Decimal(str(row["radius_m"]))
        reported_u = Decimal(str(row["compactness_u"]))
        expected_u = Decimal(2) * mu / (radius * c * c)
        err_u = rel_error(reported_u, expected_u)
        check(
            f"{row['name']}: compactness",
            err_u < Decimal("1e-14"),
            f"relative error={err_u}",
        )

        allocation_total = Decimal(str(row["allocation_total"]))
        check(
            f"{row['name']}: proposed allocation closure",
            abs(allocation_total - Decimal(2)) < Decimal("1e-14"),
            f"total={allocation_total}",
        )

        lapse = Decimal(str(row["schwarzschild_lapse_exact"]))
        lapse_identity_error = abs(lapse * lapse - (Decimal(1) - expected_u))
        check(
            f"{row['name']}: lapse squared identity",
            lapse_identity_error < Decimal("1e-14"),
            f"absolute error={lapse_identity_error}",
        )

        weak = Decimal(str(row["weak_field_lapse_first_order"]))
        check(
            f"{row['name']}: first-order weak lapse",
            abs(weak - (Decimal(1) - expected_u / Decimal(2))) < Decimal("1e-14"),
            f"reported={weak}",
        )
        reported_weak_error = Decimal(str(row["weak_lapse_absolute_error"]))
        expected_weak_error = (
            expected_u * expected_u / Decimal(4)
        ) / (weak + lapse)
        check(
            f"{row['name']}: cancellation-safe weak-lapse error",
            rel_error(reported_weak_error, expected_weak_error) < Decimal("1e-14"),
            f"relative error={rel_error(reported_weak_error, expected_weak_error)}",
        )

    ridge = data["sun_earth_newton_III_active_ridge"]
    force_a = Decimal(str(ridge["force_on_earth_by_sun_N"]))
    force_b = Decimal(str(ridge["force_on_sun_by_earth_N"]))
    check(
        "Sun-Earth Newton III force equality",
        rel_error(force_a, force_b) < Decimal("1e-14"),
        f"relative mismatch={rel_error(force_a, force_b)}",
    )
    check(
        "Sun-Earth enclosing ARA ridge",
        abs(Decimal(str(ridge["enclosing_pair_ara_x"])) - Decimal(1)) < Decimal("1e-14"),
        f"x={ridge['enclosing_pair_ara_x']}",
    )
    check(
        "Sun-Earth equal force but unequal acceleration",
        Decimal(str(ridge["acceleration_ratio"])) > Decimal("100000"),
        f"acceleration ratio={ridge['acceleration_ratio']}",
    )

    for row in data["newton_II_ara_force_identity_examples"]:
        direct = Decimal(str(row["net_force_direct_N"]))
        recovered = Decimal(str(row["net_force_from_ara_identity_N"]))
        check(
            f"Newton II identity: {row['label']}",
            abs(direct - recovered) < Decimal("1e-14"),
            f"absolute error={abs(direct - recovered)}",
        )

    # Independent randomized property check of
    # (B-A) = (A+B) * (2B/(A+B)-1).
    rng = random.Random(20260723)
    max_identity_error = Decimal(0)
    for _ in range(10_000):
        a = Decimal(rng.randrange(1, 10**9)) / Decimal(10**4)
        b = Decimal(rng.randrange(1, 10**9)) / Decimal(10**4)
        x = Decimal(2) * b / (a + b)
        recovered = (a + b) * (x - Decimal(1))
        max_identity_error = max(max_identity_error, abs((b - a) - recovered))
    check(
        "10,000-case Decimal ARA force identity property test",
        max_identity_error < Decimal("1e-40"),
        f"maximum absolute Decimal error={max_identity_error}",
    )

    passed = sum(item["passed"] for item in checks)
    result = {
        "analysis_id": data["analysis_id"],
        "validator": "independent Decimal recomputation plus seeded property tests",
        "checks_passed": passed,
        "checks_total": len(checks),
        "all_passed": passed == len(checks),
        "checks": checks,
    }
    VALIDATION_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(checks)} checks passed")
    print(f"Wrote {VALIDATION_PATH}")
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

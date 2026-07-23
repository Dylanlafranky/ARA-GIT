"""Independent checks for the Landau-Zener ARA crosswalk."""

from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path


HERE = Path(__file__).resolve().parent
PATH_CSV = HERE / "LANDAU_ZENER_ARA_PATH.csv"
OUTCOME_CSV = HERE / "LANDAU_ZENER_ARA_OUTCOMES.csv"
VALIDATION_JSON = HERE / "LANDAU_ZENER_ARA_VALIDATION.json"
TOLERANCE = 2e-11


def check(name: str, passed: bool, detail: str) -> dict[str, str | bool]:
    return {"name": name, "passed": bool(passed), "detail": detail}


def lower_eigenvector_probability_b(
    detuning: float, coupling: float
) -> tuple[float, float, float]:
    """Solve the 2x2 eigenproblem without using the ARA path formula."""
    a = detuning / 2.0
    root = math.sqrt(a * a + coupling * coupling)
    lower = -root
    upper = root

    # (a-lower)c_A + g c_B = 0.  With c_A=1:
    ratio_b_to_a = -(a - lower) / coupling
    norm = math.sqrt(1.0 + ratio_b_to_a * ratio_b_to_a)
    c_b = ratio_b_to_a / norm
    return c_b * c_b, lower, upper


def main() -> None:
    with PATH_CSV.open("r", encoding="utf-8", newline="") as csv_file:
        path_rows = list(csv.DictReader(csv_file))
    with OUTCOME_CSV.open("r", encoding="utf-8", newline="") as csv_file:
        outcome_rows = list(csv.DictReader(csv_file))

    checks: list[dict[str, str | bool]] = [
        check("path row count", len(path_rows) == 11, f"rows={len(path_rows)}"),
        check(
            "outcome row count",
            len(outcome_rows) == 9,
            f"rows={len(outcome_rows)}",
        ),
    ]

    path_x = [float(row["ara_structural_path"]) for row in path_rows]
    checks.extend(
        [
            check(
                "structural path bounded",
                all(-TOLERANCE <= value <= 2.0 + TOLERANCE for value in path_x),
                f"min={min(path_x):.12f}; max={max(path_x):.12f}",
            ),
            check(
                "structural path monotone",
                all(left < right for left, right in zip(path_x, path_x[1:])),
                "strictly increasing for v>0 and g>0",
            ),
            check(
                "bare-energy ridge",
                abs(float(path_rows[5]["ara_structural_path"]) - 1.0)
                <= TOLERANCE,
                f"x(0)={path_rows[5]['ara_structural_path']}",
            ),
            check(
                "minimum gap",
                abs(float(path_rows[5]["instantaneous_gap"]) - 1.0)
                <= TOLERANCE,
                "g=0.5 gives min gap 2g=1",
            ),
        ]
    )

    max_mirror_error = 0.0
    for left, right in zip(path_rows[:5], reversed(path_rows[6:])):
        max_mirror_error = max(
            max_mirror_error,
            abs(
                float(left["ara_structural_path"])
                + float(right["ara_structural_path"])
                - 2.0
            ),
        )
    checks.append(
        check(
            "pole-reversal mirror symmetry",
            max_mirror_error <= TOLERANCE,
            f"max_abs_error={max_mirror_error:.3e}",
        )
    )

    # Independent 2x2 eigenvector checks.
    rng = random.Random(20260723)
    eigen_trials = 10_000
    eigen_failures = 0
    max_eigen_error = 0.0
    max_gap_error = 0.0
    max_derivative_error = 0.0
    for _ in range(eigen_trials):
        coupling = 10.0 ** rng.uniform(-5.0, 3.0)
        sweep = 10.0 ** rng.uniform(-4.0, 4.0)
        time = rng.uniform(-20.0, 20.0) * coupling / sweep
        detuning = sweep * time

        p_b, lower, upper = lower_eigenvector_probability_b(detuning, coupling)
        x_from_eigenvector = 2.0 * p_b
        gap = math.sqrt(detuning * detuning + 4.0 * coupling * coupling)
        x_formula = 1.0 + detuning / gap
        eigen_error = abs(x_from_eigenvector - x_formula)
        gap_error = abs((upper - lower) - gap) / max(1.0, gap)

        # Central finite difference in the dimensionless crossing coordinate
        # u=Delta/(2g), avoiding artificial scale-conditioning failures.
        u = detuning / (2.0 * coupling)
        step_u = 1e-5 * max(1.0, abs(u))
        u_plus = u + step_u
        u_minus = u - step_u
        x_plus = 1.0 + u_plus / math.sqrt(1.0 + u_plus * u_plus)
        x_minus = 1.0 + u_minus / math.sqrt(1.0 + u_minus * u_minus)
        numerical_derivative = (x_plus - x_minus) / (2.0 * step_u)
        analytic_derivative = 1.0 / ((1.0 + u * u) ** 1.5)
        derivative_error = abs(numerical_derivative - analytic_derivative)

        max_eigen_error = max(max_eigen_error, eigen_error)
        max_gap_error = max(max_gap_error, gap_error)
        max_derivative_error = max(max_derivative_error, derivative_error)
        if eigen_error > TOLERANCE or gap_error > TOLERANCE or derivative_error > 2e-9:
            eigen_failures += 1

    checks.append(
        check(
            "10,000 independent eigenstate/path trials",
            eigen_failures == 0,
            (
                f"failures={eigen_failures}; eigen_error={max_eigen_error:.3e}; "
                f"gap_error={max_gap_error:.3e}; derivative_error={max_derivative_error:.3e}"
            ),
        )
    )

    # Transition outcome properties.
    outcome_x = [float(row["ara_handover_outcome"]) for row in outcome_rows]
    checks.extend(
        [
            check(
                "outcome path bounded and monotone",
                all(-TOLERANCE <= value <= 2.0 + TOLERANCE for value in outcome_x)
                and all(
                    left < right for left, right in zip(outcome_x, outcome_x[1:])
                ),
                f"min={min(outcome_x):.12f}; max={max(outcome_x):.12f}",
            ),
            check(
                "outcome ridge gamma",
                abs(outcome_x[3] - 1.0) <= TOLERANCE,
                f"gamma=ln2/(2pi); x={outcome_x[3]:.16f}",
            ),
        ]
    )

    probability_trials = 10_000
    probability_failures = 0
    max_probability_error = 0.0
    for _ in range(probability_trials):
        hbar = 10.0 ** rng.uniform(-4.0, 4.0)
        coupling = 10.0 ** rng.uniform(-5.0, 3.0)
        sweep = 10.0 ** rng.uniform(-5.0, 5.0)
        gamma = coupling * coupling / (hbar * sweep)
        exponent = -2.0 * math.pi * gamma
        p_stay = 0.0 if exponent < -745.0 else math.exp(exponent)
        p_handover = 1.0 - p_stay
        x_handover = 2.0 * p_handover
        local_error = max(
            abs(p_stay + p_handover - 1.0),
            abs(x_handover - 2.0 * (1.0 - p_stay)),
            max(0.0, -p_stay, -p_handover, p_stay - 1.0, p_handover - 1.0),
        )
        max_probability_error = max(max_probability_error, local_error)
        if local_error > TOLERANCE:
            probability_failures += 1

    checks.append(
        check(
            "10,000 random handover-probability trials",
            probability_failures == 0,
            f"failures={probability_failures}; max_error={max_probability_error:.3e}",
        )
    )

    # The sharp-coupling limit away from t=0.
    small_g = 1e-12
    x_before = 1.0 - 1.0 / math.sqrt(1.0 + 4.0 * small_g * small_g)
    x_after = 1.0 + 1.0 / math.sqrt(1.0 + 4.0 * small_g * small_g)
    checks.append(
        check(
            "zero-coupling one-sided flip",
            abs(x_before) <= TOLERANCE and abs(x_after - 2.0) <= TOLERANCE,
            f"x(-1)={x_before:.3e}; x(+1)={x_after:.16f}",
        )
    )

    passed = sum(1 for item in checks if item["passed"])
    validation = {
        "assessment": "ready to share" if passed == len(checks) else "needs revision",
        "passed": passed,
        "total": len(checks),
        "tolerance": TOLERANCE,
        "checks": checks,
        "required_caveats": [
            "The structural coordinate describes the instantaneous lower eigenstate, not necessarily the finite-speed evolving state.",
            "The Landau-Zener probability assumes the ideal infinite linear sweep and this Hamiltonian convention.",
            "The ARA forms are exact reparameterizations, not a new quantum prediction.",
        ],
    }

    with VALIDATION_JSON.open("w", encoding="utf-8") as json_file:
        json.dump(validation, json_file, indent=2)
        json_file.write("\n")

    print(json.dumps(validation, indent=2))
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

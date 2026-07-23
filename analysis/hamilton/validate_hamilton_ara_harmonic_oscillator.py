"""Independent checks for the Hamiltonian-to-ARA oscillator crosswalk."""

from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path


HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "HAMILTON_ARA_HARMONIC_OSCILLATOR_POINTS.csv"
OUTPUT_PATH = HERE / "HAMILTON_ARA_HARMONIC_OSCILLATOR_VALIDATION.json"
TOLERANCE = 1e-11


def check(name: str, condition: bool, detail: str) -> dict[str, str | bool]:
    return {"name": name, "passed": bool(condition), "detail": detail}


def main() -> None:
    with CSV_PATH.open("r", encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    checks: list[dict[str, str | bool]] = []
    checks.append(check("expected row count", len(rows) == 17, f"rows={len(rows)}"))

    max_h_error = 0.0
    max_circle_error = 0.0
    max_total_error = 0.0
    max_x_error = 0.0
    for row in rows:
        qn = float(row["Q_sqrt_joule"])
        pn = float(row["P_sqrt_joule"])
        potential = float(row["potential_energy_j"])
        kinetic = float(row["kinetic_energy_j"])
        hamiltonian = float(row["hamiltonian_j"])
        t_q = float(row["ara_configuration_allocation"])
        t_p = float(row["ara_traversal_allocation"])
        x_h = float(row["ara_x_traversal"])

        max_h_error = max(max_h_error, abs(potential + kinetic - hamiltonian))
        max_circle_error = max(
            max_circle_error, abs(qn * qn + pn * pn - 2.0 * hamiltonian)
        )
        max_total_error = max(max_total_error, abs(t_q + t_p - 2.0))
        max_x_error = max(max_x_error, abs(x_h - 2.0 * kinetic / hamiltonian))

    checks.extend(
        [
            check(
                "Hamiltonian reconstruction",
                max_h_error <= TOLERANCE,
                f"max_abs_error={max_h_error:.3e}",
            ),
            check(
                "normalized circle",
                max_circle_error <= TOLERANCE,
                f"max_abs_error={max_circle_error:.3e}",
            ),
            check(
                "fixed total-2 allocation",
                max_total_error <= TOLERANCE,
                f"max_abs_error={max_total_error:.3e}",
            ),
            check(
                "ARA coordinate equals kinetic-energy allocation",
                max_x_error <= TOLERANCE,
                f"max_abs_error={max_x_error:.3e}",
            ),
        ]
    )

    # Named boundary and ridge cases.
    x_at_phase_0 = float(rows[0]["ara_x_traversal"])
    x_at_phase_pi_over_4 = float(rows[2]["ara_x_traversal"])
    x_at_phase_pi_over_2 = float(rows[4]["ara_x_traversal"])
    checks.extend(
        [
            check("configuration pole x=0", abs(x_at_phase_0) <= TOLERANCE, str(x_at_phase_0)),
            check(
                "equal-energy ridge x=1",
                abs(x_at_phase_pi_over_4 - 1.0) <= TOLERANCE,
                str(x_at_phase_pi_over_4),
            ),
            check(
                "traversal pole x=2",
                abs(x_at_phase_pi_over_2 - 2.0) <= TOLERANCE,
                str(x_at_phase_pi_over_2),
            ),
        ]
    )

    # The same diameter reading occurs at phase-space points with different
    # signs.  This proves why the compressed coordinate needs a direction or
    # quadrant field.
    projection_pairs = [(1, 7), (2, 6), (3, 5), (9, 15)]
    projection_check = all(
        abs(
            float(rows[left]["ara_x_traversal"])
            - float(rows[right]["ara_x_traversal"])
        )
        <= TOLERANCE
        and rows[left]["phase_quadrant"] != rows[right]["phase_quadrant"]
        for left, right in projection_pairs
    )
    checks.append(
        check(
            "diameter projection is many-to-one",
            projection_check,
            "equal x_H values occur in distinct signed quadrants",
        )
    )

    # Independent randomized property checks over many masses, stiffnesses,
    # energies and phases.
    rng = random.Random(20260723)
    property_trials = 10_000
    property_failures = 0
    max_property_error = 0.0
    for _ in range(property_trials):
        mass = 10.0 ** rng.uniform(-4.0, 4.0)
        stiffness = 10.0 ** rng.uniform(-4.0, 4.0)
        energy = 10.0 ** rng.uniform(-8.0, 8.0)
        theta = rng.uniform(-20.0 * math.pi, 20.0 * math.pi)
        omega = math.sqrt(stiffness / mass)
        radius = math.sqrt(2.0 * energy)
        qn = radius * math.cos(theta)
        pn = -radius * math.sin(theta)

        q = qn / math.sqrt(stiffness)
        p = pn * math.sqrt(mass)
        potential = stiffness * q * q / 2.0
        kinetic = p * p / (2.0 * mass)
        total = potential + kinetic
        t_q = 2.0 * potential / total
        t_p = 2.0 * kinetic / total

        q_dot_a = omega * pn
        p_dot_a = -omega * qn
        q_dot_b = -radius * omega * math.sin(theta)
        p_dot_b = -radius * omega * math.cos(theta)

        scale = max(1.0, abs(energy), abs(q_dot_a), abs(p_dot_a))
        errors = (
            abs(total - energy) / max(1.0, abs(energy)),
            abs(qn * qn + pn * pn - 2.0 * energy)
            / max(1.0, abs(2.0 * energy)),
            abs(t_q + t_p - 2.0),
            abs((2.0 - t_p) - t_q),
            abs(q_dot_a - q_dot_b) / scale,
            abs(p_dot_a - p_dot_b) / scale,
        )
        local_error = max(errors)
        max_property_error = max(max_property_error, local_error)
        if local_error > 2e-11:
            property_failures += 1

    checks.append(
        check(
            "10,000 randomized property trials",
            property_failures == 0,
            f"failures={property_failures}; max_relative_or_absolute_error={max_property_error:.3e}",
        )
    )

    passed = sum(1 for item in checks if item["passed"])
    result = {
        "assessment": "ready to share" if passed == len(checks) else "needs revision",
        "passed": passed,
        "total": len(checks),
        "tolerance": TOLERANCE,
        "checks": checks,
        "required_caveats": [
            "The total-2 result follows from the declared normalization.",
            "The equal-energy ridge is not a force-cancellation result.",
            "The crosswalk does not test universal ARA recurrence across domains.",
        ],
    }

    with OUTPUT_PATH.open("w", encoding="utf-8") as output_file:
        json.dump(result, output_file, indent=2)
        output_file.write("\n")

    print(json.dumps(result, indent=2))
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

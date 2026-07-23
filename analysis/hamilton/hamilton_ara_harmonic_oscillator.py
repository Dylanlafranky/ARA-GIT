"""Exact Hamiltonian-to-ARA crosswalk for a simple harmonic oscillator.

This script does not fit data and does not search for an ARA landmark.  It
starts from the textbook Hamiltonian

    H = p^2/(2m) + k q^2/2

and derives a bounded total-2 allocation between configuration energy and
momentum energy.  The output is a compact worked example suitable for audit.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "HAMILTON_ARA_HARMONIC_OSCILLATOR_POINTS.csv"
JSON_PATH = HERE / "HAMILTON_ARA_HARMONIC_OSCILLATOR_RESULTS.json"


def signed_state(value: float, tolerance: float = 1e-12) -> str:
    if abs(value) <= tolerance:
        return "0"
    return "+" if value > 0.0 else "-"


def main() -> None:
    # A deliberately simple exact example.
    mass_kg = 2.0
    spring_constant_n_per_m = 8.0
    total_energy_j = 10.0
    omega_rad_per_s = math.sqrt(spring_constant_n_per_m / mass_kg)
    radius_sqrt_j = math.sqrt(2.0 * total_energy_j)

    rows: list[dict[str, float | str | int]] = []
    max_hamilton_error = 0.0
    max_circle_error = 0.0
    max_total_2_error = 0.0
    max_q_equation_error = 0.0
    max_p_equation_error = 0.0

    # Sixteen equal phase steps plus the repeated endpoint.
    for index in range(17):
        theta = index * math.pi / 8.0
        time_s = theta / omega_rad_per_s

        # Energy-normalized phase-space coordinates.
        q_normalized = radius_sqrt_j * math.cos(theta)
        p_normalized = -radius_sqrt_j * math.sin(theta)

        # Physical coordinates: Q=sqrt(k)q and P=p/sqrt(m).
        position_m = q_normalized / math.sqrt(spring_constant_n_per_m)
        momentum_kg_m_per_s = p_normalized * math.sqrt(mass_kg)

        potential_energy_j = (
            spring_constant_n_per_m * position_m * position_m / 2.0
        )
        kinetic_energy_j = (
            momentum_kg_m_per_s * momentum_kg_m_per_s / (2.0 * mass_kg)
        )
        reconstructed_hamiltonian_j = potential_energy_j + kinetic_energy_j

        # Same ARA geometry read as a fixed total-2 energy allocation.
        configuration_allocation = 2.0 * potential_energy_j / total_energy_j
        traversal_allocation = 2.0 * kinetic_energy_j / total_energy_j
        hamilton_ara_x = traversal_allocation

        # Hamilton's equations in normalized coordinates.
        q_dot_normalized = omega_rad_per_s * p_normalized
        p_dot_normalized = -omega_rad_per_s * q_normalized
        q_dot_from_solution = (
            -radius_sqrt_j * omega_rad_per_s * math.sin(theta)
        )
        p_dot_from_solution = (
            -radius_sqrt_j * omega_rad_per_s * math.cos(theta)
        )

        # The compressed diameter needs a direction field to distinguish the
        # two passes through the same allocation.
        ara_velocity_per_s = (
            -4.0
            * omega_rad_per_s
            * p_normalized
            * q_normalized
            / (radius_sqrt_j * radius_sqrt_j)
        )
        if abs(ara_velocity_per_s) <= 1e-12:
            allocation_direction = "handover"
        elif ara_velocity_per_s > 0.0:
            allocation_direction = "toward traversal"
        else:
            allocation_direction = "toward configuration"

        max_hamilton_error = max(
            max_hamilton_error,
            abs(reconstructed_hamiltonian_j - total_energy_j),
        )
        max_circle_error = max(
            max_circle_error,
            abs(
                q_normalized * q_normalized
                + p_normalized * p_normalized
                - 2.0 * total_energy_j
            ),
        )
        max_total_2_error = max(
            max_total_2_error,
            abs(configuration_allocation + traversal_allocation - 2.0),
        )
        max_q_equation_error = max(
            max_q_equation_error,
            abs(q_dot_normalized - q_dot_from_solution),
        )
        max_p_equation_error = max(
            max_p_equation_error,
            abs(p_dot_normalized - p_dot_from_solution),
        )

        rows.append(
            {
                "phase_index": index,
                "theta_radians": theta,
                "time_seconds": time_s,
                "Q_sqrt_joule": q_normalized,
                "P_sqrt_joule": p_normalized,
                "q_position_m": position_m,
                "p_momentum_kg_m_per_s": momentum_kg_m_per_s,
                "potential_energy_j": potential_energy_j,
                "kinetic_energy_j": kinetic_energy_j,
                "hamiltonian_j": reconstructed_hamiltonian_j,
                "ara_configuration_allocation": configuration_allocation,
                "ara_traversal_allocation": traversal_allocation,
                "ara_x_traversal": hamilton_ara_x,
                "ara_dx_dt_per_s": ara_velocity_per_s,
                "Q_sign": signed_state(q_normalized),
                "P_sign": signed_state(p_normalized),
                "phase_quadrant": f"({signed_state(q_normalized)}Q,"
                f"{signed_state(p_normalized)}P)",
                "allocation_direction": allocation_direction,
            }
        )

    fieldnames = list(rows[0].keys())
    with CSV_PATH.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    result = {
        "analysis": "Exact Hamiltonian harmonic-oscillator to ARA allocation crosswalk",
        "status": {
            "hamiltonian_circle": "exact after the declared coordinate rescaling",
            "total_2_allocation": "exact normalized accounting identity",
            "ara_interpretation": "candidate typed appearance of the ARA geometry",
            "universal_fractal_claim": "not tested by this calculation",
        },
        "parameters": {
            "mass_kg": mass_kg,
            "spring_constant_n_per_m": spring_constant_n_per_m,
            "total_energy_j": total_energy_j,
            "omega_rad_per_s": omega_rad_per_s,
            "period_seconds": 2.0 * math.pi / omega_rad_per_s,
            "phase_space_radius_sqrt_joule": radius_sqrt_j,
        },
        "definitions": {
            "Q": "sqrt(k) * q",
            "P": "p / sqrt(m)",
            "circle": "Q^2 + P^2 = 2H",
            "configuration_allocation": "t_Q = 2V/H = 2Q^2/(Q^2+P^2)",
            "traversal_allocation": "t_P = 2K/H = 2P^2/(Q^2+P^2)",
            "ara_coordinate": "x_H = t_P",
            "orientation_reversal": "x_H' = 2 - x_H = t_Q",
            "direction_field": "dx_H/dt = -4 omega P Q/(Q^2+P^2)",
        },
        "maximum_absolute_errors": {
            "hamiltonian_j": max_hamilton_error,
            "circle_j": max_circle_error,
            "total_2": max_total_2_error,
            "hamilton_q_equation": max_q_equation_error,
            "hamilton_p_equation": max_p_equation_error,
        },
        "important_interpretive_limits": [
            "x_H is an energy-allocation projection, not the earlier rise/fall-duration statistic.",
            "x_H=1 means equal kinetic and potential energy; it is not force cancellation.",
            "x_H=0 and x_H=2 are regular oscillator handovers, not mathematical divergences.",
            "The 0-2 diameter loses the signs of Q and P, so quadrant or direction must be retained.",
            "The calculation establishes a crosswalk, not universal ARA fractality or quantum gravity.",
        ],
        "row_count": len(rows),
        "csv": CSV_PATH.name,
    }

    with JSON_PATH.open("w", encoding="utf-8") as json_file:
        json.dump(result, json_file, indent=2)
        json_file.write("\n")

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

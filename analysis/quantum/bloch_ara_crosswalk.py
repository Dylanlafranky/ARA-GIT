"""Exact ARA coordinate crosswalk for a quantum two-level Bloch state.

The script uses only textbook two-level-state identities.  It treats ARA as
the primary 0-2 population coordinate and mentions total-2 closure only as
the same geometry's secondary normalization perspective.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "BLOCH_ARA_EXAMPLE_STATES.csv"
JSON_PATH = HERE / "BLOCH_ARA_RESULTS.json"


def state_row(
    label: str,
    rx: float,
    ry: float,
    rz: float,
    *,
    note: str,
) -> dict[str, float | str]:
    radius = math.sqrt(rx * rx + ry * ry + rz * rz)
    p_a = (1.0 + rz) / 2.0
    p_b = (1.0 - rz) / 2.0
    ara_x = 2.0 * p_b
    return {
        "label": label,
        "bloch_x": rx,
        "bloch_y": ry,
        "bloch_z": rz,
        "bloch_radius": radius,
        "probability_A": p_a,
        "probability_B": p_b,
        "ara_x_B_oriented": ara_x,
        "centered_ara_x_minus_1": ara_x - 1.0,
        "bloch_z_plus_centered_ara": rz + ara_x - 1.0,
        "note": note,
    }


def main() -> None:
    root_half = math.sqrt(0.5)
    rows = [
        state_row(
            "pure_A_north_pole",
            0.0,
            0.0,
            1.0,
            note="ARA 0; pure basis state A",
        ),
        state_row(
            "coherent_equal_phase_0",
            1.0,
            0.0,
            0.0,
            note="ARA 1; pure coherent equatorial state",
        ),
        state_row(
            "coherent_equal_phase_pi_over_2",
            0.0,
            1.0,
            0.0,
            note="ARA 1; same populations, different relative phase",
        ),
        state_row(
            "fully_mixed_center",
            0.0,
            0.0,
            0.0,
            note="ARA 1; incoherent maximally mixed state",
        ),
        state_row(
            "pure_B_south_pole",
            0.0,
            0.0,
            -1.0,
            note="ARA 2; pure basis state B",
        ),
        state_row(
            "partially_mixed_off_axis",
            0.3,
            -0.4,
            0.5,
            note="Interior Bloch-ball state; ARA depends on selected diameter",
        ),
        state_row(
            "pure_equal_amplitudes_check",
            2.0 * root_half * root_half,
            0.0,
            root_half * root_half - root_half * root_half,
            note="Constructed from alpha=beta=1/sqrt(2)",
        ),
    ]

    with CSV_PATH.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    result = {
        "analysis": "Exact two-level Bloch-state to ARA diameter crosswalk",
        "status": {
            "selected_axis_crosswalk": "exact",
            "rabi_cycle_crosswalk": "exact under the ideal resonant two-level model",
            "universal_ara_sphere": "not established by this reparameterization",
            "gr_quantum_unification": "not established",
        },
        "definitions": {
            "state": "|psi> = alpha|A> + beta|B>",
            "normalization": "|alpha|^2 + |beta|^2 = 1",
            "bloch_z": "r_z = |alpha|^2 - |beta|^2",
            "ara_coordinate": "x_Q = 2|beta|^2 = 1 - r_z",
            "centered_relation": "x_Q - 1 = -r_z",
            "arbitrary_axis": "x_n = 1 - r dot n",
            "rabi": "x_Q(t) = 1 - cos(Omega t)",
            "density_matrix": "rho = (I + r dot sigma)/2; |r| <= 1",
        },
        "landmarks": {
            "ara_0": "north pole / pure A / r_z=+1",
            "ara_1": "equal A/B populations / r_z=0 plane",
            "ara_2": "south pole / pure B / r_z=-1",
        },
        "important_limits": [
            "ARA 1 is the full r_z=0 plane, not only the Bloch-ball centre.",
            "Population ARA alone loses relative phase and purity.",
            "TE-ARA is only the secondary total-allocation perspective here; the primary result is plain ARA.",
            "The mapping is an affine reparameterization of the standard Bloch coordinate.",
        ],
        "example_count": len(rows),
        "csv": CSV_PATH.name,
    }

    with JSON_PATH.open("w", encoding="utf-8") as json_file:
        json.dump(result, json_file, indent=2)
        json_file.write("\n")

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

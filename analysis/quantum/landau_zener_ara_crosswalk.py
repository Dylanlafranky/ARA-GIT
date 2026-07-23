"""Exact structural and outcome ARA coordinates for Landau-Zener crossing.

Convention:

    H(t) = [[v t / 2, g],
            [g,      -v t / 2]]

For positive v and g, the lower instantaneous eigenstate changes from basis
state A at t -> -infinity to basis state B at t -> +infinity.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
PATH_CSV = HERE / "LANDAU_ZENER_ARA_PATH.csv"
OUTCOME_CSV = HERE / "LANDAU_ZENER_ARA_OUTCOMES.csv"
RESULTS_JSON = HERE / "LANDAU_ZENER_ARA_RESULTS.json"


def structural_row(t: float, coupling_g: float, sweep_v: float) -> dict[str, float]:
    detuning = sweep_v * t
    gap = math.sqrt(detuning * detuning + 4.0 * coupling_g * coupling_g)
    x_path = 1.0 + detuning / gap
    probability_a = 1.0 - x_path / 2.0
    probability_b = x_path / 2.0
    dx_dt = (
        4.0
        * coupling_g
        * coupling_g
        * sweep_v
        / (gap * gap * gap)
    )
    return {
        "time": t,
        "detuning_vt": detuning,
        "coupling_g": coupling_g,
        "instantaneous_gap": gap,
        "probability_A_lower_eigenstate": probability_a,
        "probability_B_lower_eigenstate": probability_b,
        "ara_structural_path": x_path,
        "ara_dx_dt": dx_dt,
    }


def outcome_row(gamma: float) -> dict[str, float]:
    probability_stay = math.exp(-2.0 * math.pi * gamma)
    probability_handover = 1.0 - probability_stay
    return {
        "gamma_g2_over_hbar_v": gamma,
        "probability_stay_diabatic": probability_stay,
        "probability_handover_adiabatic": probability_handover,
        "ara_handover_outcome": 2.0 * probability_handover,
    }


def main() -> None:
    # Dimensionless worked convention: hbar=1, g=0.5, v=1.
    hbar = 1.0
    coupling_g = 0.5
    sweep_v = 1.0
    gamma = coupling_g * coupling_g / (hbar * abs(sweep_v))

    path_rows = [
        structural_row(t, coupling_g, sweep_v)
        for t in (-8.0, -4.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 4.0, 8.0)
    ]
    with PATH_CSV.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(path_rows[0].keys()))
        writer.writeheader()
        writer.writerows(path_rows)

    ridge_gamma = math.log(2.0) / (2.0 * math.pi)
    outcome_rows = [
        outcome_row(value)
        for value in (0.0, 0.01, 0.05, ridge_gamma, 0.25, 0.5, 1.0, 2.0, 5.0)
    ]
    with OUTCOME_CSV.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(outcome_rows[0].keys()))
        writer.writeheader()
        writer.writerows(outcome_rows)

    example_outcome = outcome_row(gamma)
    results = {
        "analysis": "Landau-Zener structural-path and final-handover ARA crosswalk",
        "hamiltonian_convention": "H=[[vt/2,g],[g,-vt/2]]",
        "worked_parameters": {
            "hbar": hbar,
            "coupling_g": coupling_g,
            "sweep_v": sweep_v,
            "gamma": gamma,
            "minimum_gap_2g": 2.0 * abs(coupling_g),
            **example_outcome,
        },
        "definitions": {
            "detuning": "Delta(t)=v*t",
            "instantaneous_gap": "sqrt((v*t)^2+4*g^2)",
            "structural_ara": "x_path=1+(v*t)/sqrt((v*t)^2+4*g^2)",
            "connection_time_control": "gamma=g^2/(hbar*|v|)",
            "stay_probability": "P_D=exp(-2*pi*gamma)",
            "handover_probability": "P_H=1-P_D",
            "outcome_ara": "x_handover=2*(1-exp(-2*pi*gamma))",
            "outcome_ridge_gamma": "ln(2)/(2*pi)",
        },
        "status": {
            "structural_path": "exact instantaneous lower-eigenstate coordinate",
            "outcome_probability": "exact Landau-Zener asymptotic result under its ideal assumptions",
            "ara_interpretation": "exact reparameterization plus proposed Connection/Traversal language",
            "universal_handover_law": "not established",
        },
        "important_limits": [
            "x_path describes an instantaneous eigenstate; the actual evolving state follows it only in the adiabatic limit.",
            "t=0 is the equal bare-energy ridge, while nonzero g keeps the coupled eigenvalues separated.",
            "g is a coupling energy, not itself an ARA ratio; gamma is the dimensionless competition.",
            "At g=0 the gap closes and the x_path formula is undefined exactly at t=0.",
            "TE-ARA is only the secondary closure perspective; both moving coordinates are primarily plain ARA.",
        ],
        "path_csv": PATH_CSV.name,
        "outcome_csv": OUTCOME_CSV.name,
    }

    with RESULTS_JSON.open("w", encoding="utf-8") as json_file:
        json.dump(results, json_file, indent=2)
        json_file.write("\n")

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

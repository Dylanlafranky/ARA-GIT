#!/usr/bin/env python3
"""
Galactic rotation phi diagnostic.

Purpose:
    Test whether the atlas entry "Galactic rotation MW = phi" is supported
    by actual Milky Way rotation-curve quantities, rather than by an archived
    hand-assigned scaffold value.

Data:
    Rotation-curve table from the open MNRAS paper:
    "The rotation curve of the Milky Way measured by classical Cepheids
    from Gaia DR3", Table 1. The table gives Galactocentric radius R,
    circular velocity Vc, and bootstrap uncertainty.

What this test can and cannot do:
    - It can support the rough galactic-year period near the Sun.
    - It can test dimensionless local geometry from the rotation curve.
    - It cannot directly observe a full 230 Myr orbit through time.
    - It cannot prove or disprove every possible ARA definition for a galaxy.

The two strict diagnostic quantities are:
    1. Pure circular carrier ARA:
       A circular orbit has no observed build/release asymmetry by itself,
       so its neutral ARA is 1.0.

    2. Epicyclic coupling ratio:
       For a local power-law rotation curve V ~ R^beta, the near-circular
       radial/azimuthal frequency ratio is kappa/Omega = sqrt(2 * (1 + beta)).
       This is a measurable local geometry proxy. Phi would require
       beta = phi^2 / 2 - 1 ~= 0.309, meaning a distinctly rising rotation
       curve. A flat curve gives sqrt(2).

Outputs:
    Mapping/galactic_rotation_phi_test_result.json
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import mean, median


HERE = Path(__file__).resolve().parent
OUT = HERE / "galactic_rotation_phi_test_result.json"

PHI = (1.0 + 5.0**0.5) / 2.0
SQRT2 = 2.0**0.5
KPC_KM = 3.0856775814913673e16
MYR_SECONDS = 365.25 * 86400.0 * 1.0e6


ROTATION_CURVE = [
    {"R_kpc": 6.58, "Vc_km_s": 242.92, "sigma_Vc_km_s": 1.25},
    {"R_kpc": 7.49, "Vc_km_s": 239.31, "sigma_Vc_km_s": 1.33},
    {"R_kpc": 8.48, "Vc_km_s": 236.54, "sigma_Vc_km_s": 0.86},
    {"R_kpc": 9.50, "Vc_km_s": 232.36, "sigma_Vc_km_s": 1.32},
    {"R_kpc": 10.52, "Vc_km_s": 229.97, "sigma_Vc_km_s": 1.13},
    {"R_kpc": 11.42, "Vc_km_s": 233.57, "sigma_Vc_km_s": 1.39},
    {"R_kpc": 12.50, "Vc_km_s": 233.38, "sigma_Vc_km_s": 1.30},
    {"R_kpc": 13.50, "Vc_km_s": 237.05, "sigma_Vc_km_s": 1.53},
    {"R_kpc": 14.46, "Vc_km_s": 237.11, "sigma_Vc_km_s": 1.31},
    {"R_kpc": 15.21, "Vc_km_s": 237.00, "sigma_Vc_km_s": 2.22},
    {"R_kpc": 15.88, "Vc_km_s": 231.03, "sigma_Vc_km_s": 1.95},
    {"R_kpc": 17.58, "Vc_km_s": 224.03, "sigma_Vc_km_s": 1.91},
]


def orbital_period_myr(radius_kpc: float, velocity_km_s: float) -> float:
    circumference_km = 2.0 * math.pi * radius_kpc * KPC_KM
    return circumference_km / velocity_km_s / MYR_SECONDS


def log_slope(left: dict, right: dict) -> float:
    return (
        math.log(right["Vc_km_s"]) - math.log(left["Vc_km_s"])
    ) / (
        math.log(right["R_kpc"]) - math.log(left["R_kpc"])
    )


def linear_log_slope(rows: list[dict]) -> float:
    xs = [math.log(row["R_kpc"]) for row in rows]
    ys = [math.log(row["Vc_km_s"]) for row in rows]
    xbar = mean(xs)
    ybar = mean(ys)
    numerator = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys))
    denominator = sum((x - xbar) ** 2 for x in xs)
    return numerator / denominator


def closest_candidate(value: float) -> dict:
    candidates = {
        "balance_1": 1.0,
        "sqrt2_flat_curve": SQRT2,
        "phi": PHI,
        "resonance_2": 2.0,
    }
    name, target = min(candidates.items(), key=lambda item: abs(value - item[1]))
    return {
        "name": name,
        "target": target,
        "abs_error": abs(value - target),
    }


def main() -> None:
    rows = []
    for i, row in enumerate(ROTATION_CURVE):
        if i == 0:
            beta = log_slope(ROTATION_CURVE[0], ROTATION_CURVE[1])
            beta_method = "forward_difference"
        elif i == len(ROTATION_CURVE) - 1:
            beta = log_slope(ROTATION_CURVE[-2], ROTATION_CURVE[-1])
            beta_method = "backward_difference"
        else:
            beta = log_slope(ROTATION_CURVE[i - 1], ROTATION_CURVE[i + 1])
            beta_method = "central_difference"

        kappa_over_omega = math.sqrt(max(0.0, 2.0 * (1.0 + beta)))
        period_slope = 1.0 - beta
        rows.append(
            {
                **row,
                "orbital_period_myr": orbital_period_myr(row["R_kpc"], row["Vc_km_s"]),
                "beta_dlnV_dlnR": beta,
                "beta_method": beta_method,
                "kappa_over_omega": kappa_over_omega,
                "period_slope_dlnT_dlnR": period_slope,
                "kappa_distance_to_phi": abs(kappa_over_omega - PHI),
                "period_slope_distance_to_phi": abs(period_slope - PHI),
            }
        )

    global_beta = linear_log_slope(ROTATION_CURVE)
    global_kappa = math.sqrt(max(0.0, 2.0 * (1.0 + global_beta)))
    global_period_slope = 1.0 - global_beta

    solar_row = min(rows, key=lambda row: abs(row["R_kpc"] - 8.2))
    phi_beta_required_for_kappa = PHI**2 / 2.0 - 1.0
    phi_beta_required_for_period_slope = 1.0 - PHI

    result = {
        "date": "2026-05-24",
        "source": {
            "title": "The rotation curve of the Milky Way measured by classical Cepheids from Gaia DR3",
            "table": "Table 1",
            "url": "https://academic.oup.com/mnras/article/546/2/stag011/8416425",
            "notes": "12 binned circular velocities from 6.58 to 17.58 kpc; source sample is 903 Gaia DR3 classical Cepheids.",
        },
        "constants": {
            "phi": PHI,
            "sqrt2": SQRT2,
        },
        "summary": {
            "solar_nearest_radius_kpc": solar_row["R_kpc"],
            "solar_nearest_vc_km_s": solar_row["Vc_km_s"],
            "solar_nearest_orbital_period_myr": solar_row["orbital_period_myr"],
            "atlas_period_myr": 230.0,
            "atlas_period_error_fraction": abs(solar_row["orbital_period_myr"] - 230.0) / 230.0,
            "pure_circular_carrier_ara": 1.0,
            "global_beta_dlnV_dlnR": global_beta,
            "global_kappa_over_omega": global_kappa,
            "global_period_slope_dlnT_dlnR": global_period_slope,
            "median_beta_dlnV_dlnR": median(row["beta_dlnV_dlnR"] for row in rows),
            "median_kappa_over_omega": median(row["kappa_over_omega"] for row in rows),
            "median_period_slope_dlnT_dlnR": median(row["period_slope_dlnT_dlnR"] for row in rows),
            "mean_kappa_over_omega": mean(row["kappa_over_omega"] for row in rows),
            "mean_period_slope_dlnT_dlnR": mean(row["period_slope_dlnT_dlnR"] for row in rows),
            "local_kappa_points_within_0_05_phi": sum(row["kappa_distance_to_phi"] <= 0.05 for row in rows),
            "local_kappa_points_within_0_10_phi": sum(row["kappa_distance_to_phi"] <= 0.10 for row in rows),
            "local_period_slope_points_within_0_05_phi": sum(row["period_slope_distance_to_phi"] <= 0.05 for row in rows),
            "local_period_slope_points_within_0_10_phi": sum(row["period_slope_distance_to_phi"] <= 0.10 for row in rows),
            "phi_required_beta_for_kappa_over_omega": phi_beta_required_for_kappa,
            "phi_required_beta_for_period_slope": phi_beta_required_for_period_slope,
            "closest_candidate_for_global_kappa": closest_candidate(global_kappa),
            "closest_candidate_for_median_kappa": closest_candidate(median(row["kappa_over_omega"] for row in rows)),
            "closest_candidate_for_global_period_slope": closest_candidate(global_period_slope),
            "closest_candidate_for_median_period_slope": closest_candidate(median(row["period_slope_dlnT_dlnR"] for row in rows)),
        },
        "interpretation": {
            "period_anchor_supported": True,
            "phi_ara_supported_by_this_test": False,
            "short_read": (
                "The rough 230 Myr galactic-year period is supported near the solar radius, "
                "but the measured rotation-curve geometry is not phi. The pure orbit is "
                "balanced at ARA=1.0; the local epicyclic coupling is closer to sqrt(2), "
                "the flat-rotation-curve value, than to phi."
            ),
            "atlas_action": (
                "Do not keep Galactic Rotation MW as a measured phi node. If shown in the "
                "atlas, mark the phi value as archived hypothesis or replace the carrier "
                "ARA with 1.0 and keep epicyclic/shear geometry as a separate measured diagnostic."
            ),
        },
        "rows": rows,
    }

    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("Galactic rotation phi diagnostic")
    print(f"  solar-radius orbital period: {solar_row['orbital_period_myr']:.2f} Myr")
    print(f"  atlas 230 Myr period error: {result['summary']['atlas_period_error_fraction']:.3%}")
    print(f"  pure circular carrier ARA: {result['summary']['pure_circular_carrier_ara']:.3f}")
    print(f"  global beta dlnV/dlnR: {global_beta:.3f}")
    print(f"  global kappa/Omega: {global_kappa:.3f}")
    print(f"  median kappa/Omega: {result['summary']['median_kappa_over_omega']:.3f}")
    print(f"  global period slope dlnT/dlnR: {global_period_slope:.3f}")
    print(f"  median period slope dlnT/dlnR: {result['summary']['median_period_slope_dlnT_dlnR']:.3f}")
    print(f"  phi-supported as ARA: {result['interpretation']['phi_ara_supported_by_this_test']}")
    print(f"  wrote: {OUT}")


if __name__ == "__main__":
    main()

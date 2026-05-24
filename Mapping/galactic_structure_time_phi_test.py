#!/usr/bin/env python3
"""
Galactic structure-time phi diagnostic.

This is the follow-up to the galactic carrier test.

Carrier result:
    The Milky Way circular rotation carrier is balanced, ARA ~= 1.0.

New question:
    Does the layer that travels through, or co-rotates with, galactic
    structure show a phi-like temporal relation?

We test two structure clocks against the measured local circular carrier:

1. Bar pattern rotation:
   The bar is a coherent rotating structure. If it were phi-locked to the
   local circular carrier, its pattern speed would be phi * Omega_sun.

2. Spiral-arm crossing:
   For an m-armed spiral pattern with speed Omega_p, the next-arm passage
   period at the Sun is:

       P_cross = 2pi / (m * abs(Omega_sun - Omega_p))

   For a four-arm Milky Way, a crossing period equal to P_orb / phi requires:

       Omega_p = Omega_sun * (1 - phi / 4)

   That is the "phi-through-structure" condition for a slower spiral pattern.

The test deliberately keeps these as geometry diagnostics, not predictions.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROTATION_RESULT = HERE / "galactic_rotation_phi_test_result.json"
OUT = HERE / "galactic_structure_time_phi_test_result.json"

PHI = (1.0 + 5.0**0.5) / 2.0
INV_PHI = 1.0 / PHI
KM_S_KPC_TO_MYR_INV = 365.25 * 86400.0 * 1.0e6 / 3.0856775814913673e16


SPIRAL_PATTERN_CANDIDATES = [
    {
        "name": "slow_density_wave_low",
        "omega_km_s_kpc": 12.0,
        "source": "Vallee 2021/2022 low density-wave estimate range",
        "notes": "Low spiral-pattern-speed density-wave end.",
    },
    {
        "name": "slow_density_wave_upper",
        "omega_km_s_kpc": 15.0,
        "source": "Vallee 2021 MNRAS discussion",
        "notes": "Text reports density-wave speed appears <=15 km/s/kpc.",
    },
    {
        "name": "slow_density_wave_broad_upper",
        "omega_km_s_kpc": 17.0,
        "source": "Vallee 2021/2022 abstracted range",
        "notes": "Published abstract/range reports density-wave speed near 12-17 km/s/kpc.",
    },
    {
        "name": "phi_target_four_arm",
        "omega_km_s_kpc": None,
        "source": "derived from P_cross/P_orb = 1/phi for m=4",
        "notes": "This is the exact four-arm phi-through-structure target, not a measurement.",
    },
    {
        "name": "gaia_ridge_arm",
        "omega_km_s_kpc": 20.0,
        "sigma_km_s_kpc": 3.0,
        "source": "Hunt et al. 2018 Gaia ridge spiral-arm crossing model",
        "notes": "Estimated pattern speed for one inferred arm from Gaia velocity ridges.",
    },
    {
        "name": "open_cluster_apogee",
        "omega_km_s_kpc": 23.0,
        "source": "Martinez-Barbosa et al. open-cluster/APOGEE estimate",
        "notes": "Open-cluster/giant-star pattern-speed estimate.",
    },
    {
        "name": "local_arm_corotating",
        "omega_km_s_kpc": 29.0,
        "source": "Hunt et al. 2018 local-arm near-LSR pattern-speed note",
        "notes": "Local-arm/spur-like structure with pattern speed similar to the local standard of rest.",
    },
]

BAR_PATTERN_CANDIDATES = [
    {
        "name": "far_side_all_bar",
        "omega_km_s_kpc": 31.0,
        "sigma_km_s_kpc": 1.0,
        "source": "Sanders et al. 2019 all-region bar fit",
        "notes": "Authors report this fit has an inconsistent Galactic-centre position/velocity.",
    },
    {
        "name": "review_low",
        "omega_km_s_kpc": 35.0,
        "source": "Shen & Zheng 2020 review low end",
        "notes": "Review range for bar pattern rotation speed.",
    },
    {
        "name": "review_high",
        "omega_km_s_kpc": 40.0,
        "source": "Shen & Zheng 2020 review high end",
        "notes": "Review range for bar pattern rotation speed.",
    },
    {
        "name": "near_side_gaia_vvv",
        "omega_km_s_kpc": 41.0,
        "sigma_km_s_kpc": 3.0,
        "source": "Sanders et al. 2019 near-side Gaia DR2/VVV fit",
        "notes": "More reliable near-side bar measurement in the paper; systematics dominate at about 5-10 km/s/kpc.",
    },
    {
        "name": "phi_target_bar",
        "omega_km_s_kpc": None,
        "source": "derived from Omega_bar/Omega_sun = phi",
        "notes": "Exact phi bar-speed target, not a measurement.",
    },
]


def period_myr_from_omega(omega_km_s_kpc: float) -> float:
    return 2.0 * math.pi / (omega_km_s_kpc * KM_S_KPC_TO_MYR_INV)


def nearest_phi_family(value: float) -> dict:
    candidates = {
        "1/phi": INV_PHI,
        "1": 1.0,
        "sqrt2": 2.0**0.5,
        "phi": PHI,
        "2": 2.0,
    }
    name, target = min(candidates.items(), key=lambda item: abs(value - item[1]))
    return {"name": name, "target": target, "abs_error": abs(value - target)}


def spiral_metrics(candidate: dict, omega_sun: float, p_orb_myr: float, arms: int) -> dict:
    omega = candidate["omega_km_s_kpc"]
    if omega is None:
        omega = omega_sun * (1.0 - PHI / arms)
    relative = abs(omega_sun - omega)
    if relative == 0:
        crossing = math.inf
    else:
        crossing = 2.0 * math.pi / (arms * relative * KM_S_KPC_TO_MYR_INV)
    p_pattern = period_myr_from_omega(omega)
    cross_over_orbit = crossing / p_orb_myr
    orbit_over_cross = p_orb_myr / crossing if math.isfinite(crossing) else 0.0
    return {
        **candidate,
        "omega_km_s_kpc": omega,
        "arms": arms,
        "pattern_period_myr": p_pattern,
        "crossing_period_myr": crossing,
        "crossing_over_orbit": cross_over_orbit,
        "orbit_over_crossing": orbit_over_cross,
        "distance_crossing_over_orbit_to_inv_phi": abs(cross_over_orbit - INV_PHI),
        "distance_orbit_over_crossing_to_phi": abs(orbit_over_cross - PHI),
        "nearest_for_crossing_over_orbit": nearest_phi_family(cross_over_orbit),
        "nearest_for_orbit_over_crossing": nearest_phi_family(orbit_over_cross),
    }


def bar_metrics(candidate: dict, omega_sun: float, p_orb_myr: float) -> dict:
    omega = candidate["omega_km_s_kpc"]
    if omega is None:
        omega = PHI * omega_sun
    p_pattern = period_myr_from_omega(omega)
    speed_ratio = omega / omega_sun
    period_ratio = p_pattern / p_orb_myr
    return {
        **candidate,
        "omega_km_s_kpc": omega,
        "pattern_period_myr": p_pattern,
        "omega_over_solar": speed_ratio,
        "pattern_period_over_orbit": period_ratio,
        "distance_omega_ratio_to_phi": abs(speed_ratio - PHI),
        "distance_period_ratio_to_inv_phi": abs(period_ratio - INV_PHI),
        "nearest_for_omega_ratio": nearest_phi_family(speed_ratio),
        "nearest_for_period_ratio": nearest_phi_family(period_ratio),
    }


def main() -> None:
    rotation = json.loads(ROTATION_RESULT.read_text(encoding="utf-8"))
    solar = rotation["summary"]
    radius = solar["solar_nearest_radius_kpc"]
    velocity = solar["solar_nearest_vc_km_s"]
    p_orb = solar["solar_nearest_orbital_period_myr"]
    omega_sun = velocity / radius

    spiral_four = [spiral_metrics(c, omega_sun, p_orb, 4) for c in SPIRAL_PATTERN_CANDIDATES]
    spiral_two = [spiral_metrics(c, omega_sun, p_orb, 2) for c in SPIRAL_PATTERN_CANDIDATES]
    bar = [bar_metrics(c, omega_sun, p_orb) for c in BAR_PATTERN_CANDIDATES]

    measured_spiral_four = [row for row in spiral_four if "target" not in row["name"]]
    measured_bar = [row for row in bar if "target" not in row["name"]]
    best_spiral = min(measured_spiral_four, key=lambda row: row["distance_crossing_over_orbit_to_inv_phi"])
    best_bar = min(measured_bar, key=lambda row: row["distance_omega_ratio_to_phi"])

    result = {
        "date": "2026-05-24",
        "question": "Is galactic time-through-structure phi-like while the rotation carrier remains ARA 1.0?",
        "carrier": {
            "radius_kpc": radius,
            "velocity_km_s": velocity,
            "omega_sun_km_s_kpc": omega_sun,
            "orbital_period_myr": p_orb,
            "carrier_ara": 1.0,
        },
        "phi_targets": {
            "bar_omega_for_phi_ratio_km_s_kpc": PHI * omega_sun,
            "four_arm_spiral_omega_for_crossing_1_over_phi_km_s_kpc": omega_sun * (1.0 - PHI / 4.0),
            "four_arm_spiral_crossing_period_target_myr": p_orb / PHI,
            "two_arm_spiral_omega_for_crossing_1_over_phi_km_s_kpc": omega_sun * (1.0 - PHI / 2.0),
            "two_arm_spiral_crossing_period_target_myr": p_orb / PHI,
        },
        "summary": {
            "best_measured_four_arm_spiral": {
                "name": best_spiral["name"],
                "omega_km_s_kpc": best_spiral["omega_km_s_kpc"],
                "crossing_period_myr": best_spiral["crossing_period_myr"],
                "crossing_over_orbit": best_spiral["crossing_over_orbit"],
                "distance_to_1_over_phi": best_spiral["distance_crossing_over_orbit_to_inv_phi"],
            },
            "best_measured_bar": {
                "name": best_bar["name"],
                "omega_km_s_kpc": best_bar["omega_km_s_kpc"],
                "omega_over_solar": best_bar["omega_over_solar"],
                "pattern_period_myr": best_bar["pattern_period_myr"],
                "pattern_period_over_orbit": best_bar["pattern_period_over_orbit"],
                "distance_to_phi_speed_ratio": best_bar["distance_omega_ratio_to_phi"],
            },
            "four_arm_spiral_phi_target_inside_literature_band": True,
            "bar_phi_target_inside_broad_systematic_band": True,
            "strict_central_values_support_phi": False,
        },
        "interpretation": {
            "short_read": (
                "The structure layer is more phi-plausible than the circular carrier, "
                "but this is not a clean hit. A four-arm spiral crossing becomes exactly "
                "P_orb/phi if the spiral pattern speed is about 16.6 km/s/kpc; that sits "
                "near the slow-density-wave literature band. The measured bar central "
                "value is sub-phi, though its broad systematic range can overlap the "
                "phi target. The strict result is: carrier=1.0 confirmed; structure-time "
                "phi remains plausible but unproven."
            ),
            "leakage_guard": (
                "The exact phi-target rows are included as derived targets only and are "
                "excluded from best-measured summaries."
            ),
        },
        "sources": [
            {
                "name": "Gaia DR3 Cepheid rotation curve",
                "url": "https://academic.oup.com/mnras/article/546/2/stag011/8416425",
                "used_for": "local circular carrier period and omega_sun",
            },
            {
                "name": "Vallee 2021 low density-wave spiral pattern speed",
                "url": "https://academic.oup.com/mnras/article/506/1/523/6296651",
                "used_for": "slow spiral pattern speed estimates and arm passage framing",
            },
            {
                "name": "Hunt et al. 2018 Gaia spiral arm crossings",
                "url": "https://academic.oup.com/mnras/article/480/3/3132/5063587",
                "used_for": "20 +/- 3 km/s/kpc inferred arm and local-arm near-LSR note",
            },
            {
                "name": "Sanders et al. 2019 Milky Way bar pattern speed",
                "url": "https://academic.oup.com/mnras/article/488/4/4552/5533338",
                "used_for": "31 and 41 km/s/kpc bar pattern speed candidates",
            },
            {
                "name": "Shen & Zheng 2020 bar and spiral review",
                "url": "https://arxiv.org/abs/2012.10130",
                "used_for": "35-40 km/s/kpc bar pattern speed review range",
            },
        ],
        "spiral_four_arm": spiral_four,
        "spiral_two_arm": spiral_two,
        "bar": bar,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("Galactic structure-time phi diagnostic")
    print(f"  omega_sun: {omega_sun:.3f} km/s/kpc")
    print(f"  carrier period: {p_orb:.2f} Myr, carrier ARA: 1.0")
    print(
        "  four-arm phi crossing target: "
        f"omega_p={result['phi_targets']['four_arm_spiral_omega_for_crossing_1_over_phi_km_s_kpc']:.3f} km/s/kpc, "
        f"P_cross={result['phi_targets']['four_arm_spiral_crossing_period_target_myr']:.2f} Myr"
    )
    print(
        "  best measured four-arm candidate: "
        f"{best_spiral['name']} omega_p={best_spiral['omega_km_s_kpc']:.3f}, "
        f"P_cross={best_spiral['crossing_period_myr']:.2f} Myr, "
        f"P_cross/P_orb={best_spiral['crossing_over_orbit']:.3f}"
    )
    print(
        "  bar phi target: "
        f"omega_bar={result['phi_targets']['bar_omega_for_phi_ratio_km_s_kpc']:.3f} km/s/kpc"
    )
    print(
        "  best measured bar candidate: "
        f"{best_bar['name']} omega_bar={best_bar['omega_km_s_kpc']:.3f}, "
        f"omega_bar/omega_sun={best_bar['omega_over_solar']:.3f}, "
        f"P_bar={best_bar['pattern_period_myr']:.2f} Myr"
    )
    print("  strict central values support phi: False")
    print(f"  wrote: {OUT}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Reproducible examples for the GR -> Newton -> ARA rung crossing.

The established-physics calculations use:
  * the exterior Schwarzschild metric for a spherical, non-rotating source;
  * the weak-field Newtonian limit;
  * Newton's third-law Sun--Earth force pair.

The proposed ARA compactness coordinate is explicitly separated from those
established calculations.  It is a normalization, not an additional GR law.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT_JSON = HERE / "GR_NEWTON_ARA_EXAMPLES_RESULTS.json"
RESULT_CSV = HERE / "GR_NEWTON_ARA_COMPACTNESS_EXAMPLES.csv"

# Exact SI definition.
C = 299_792_458.0

# 2022 CODATA recommended value.  The uncertainty is irrelevant at the
# displayed precision for the examples, and astronomical GM values are used
# directly where available.
G = 6.67430e-11

# IAU 2015 Resolution B3 nominal conversion constants (exact conversions).
MU_SUN = 1.327_124_4e20
R_SUN = 6.957e8
MU_EARTH = 3.986_004e14
R_EARTH_EQUATOR = 6.3781e6
MU_JUPITER = 1.266_865_3e17
R_JUPITER_EQUATOR = 7.1492e7
AU = 149_597_870_700.0  # IAU 2012 exact definition.

# PSR J0740+6620: Dittmann et al. (2024), central values.  The gravitational
# mass is expressed in nominal solar masses, so its GM is the mass ratio times
# the nominal solar mass parameter.
PSR_MASS_SOLAR = 2.08
PSR_MASS_SOLAR_MINUS = 0.07
PSR_MASS_SOLAR_PLUS = 0.07
PSR_RADIUS_M = 12.92e3
PSR_RADIUS_MINUS_M = 1.13e3
PSR_RADIUS_PLUS_M = 2.09e3


def spherical_exterior_row(name: str, mu: float, radius_m: float) -> dict:
    """Calculate exact Schwarzschild and weak-field surface quantities."""

    u = 2.0 * mu / (radius_m * C**2)
    if not 0.0 <= u < 1.0:
        raise ValueError(f"{name}: exterior row requires 0 <= compactness < 1")

    lapse_exact = math.sqrt(1.0 - u)
    lapse_weak = 1.0 - 0.5 * u
    # Directly subtracting these nearly equal numbers loses the Earth-scale
    # correction in binary64.  Rationalizing the difference gives the same
    # quantity without catastrophic cancellation:
    # (1-u/2)-sqrt(1-u) = (u^2/4)/[(1-u/2)+sqrt(1-u)].
    weak_lapse_absolute_error = (0.25 * u * u) / (lapse_weak + lapse_exact)
    newton_acceleration = mu / radius_m**2
    static_proper_acceleration = newton_acceleration / lapse_exact

    # Proposed ARA normalization of the exact compactness.  The Time/Traversal
    # allocation is tied to the squared Schwarzschild lapse; the complementary
    # Connection allocation is defined so the normalized account totals two.
    time_allocation = 2.0 * (1.0 - u)
    connection_allocation = 2.0 * u

    return {
        "name": name,
        "mu_m3_s2": mu,
        "radius_m": radius_m,
        "compactness_u": u,
        "time_allocation_proposed": time_allocation,
        "connection_allocation_proposed": connection_allocation,
        "allocation_total": time_allocation + connection_allocation,
        "ara_signed_distance_from_ridge": time_allocation - 1.0,
        "schwarzschild_lapse_exact": lapse_exact,
        "weak_field_lapse_first_order": lapse_weak,
        "weak_lapse_absolute_error": weak_lapse_absolute_error,
        "weak_lapse_relative_error": weak_lapse_absolute_error / lapse_exact,
        "newton_surface_acceleration_m_s2": newton_acceleration,
        "schwarzschild_static_proper_acceleration_m_s2": static_proper_acceleration,
        "proper_acceleration_fractional_GR_correction": (
            static_proper_acceleration / newton_acceleration - 1.0
        ),
        "surface_gravitational_redshift": 1.0 / lapse_exact - 1.0,
    }


def psr_compactness_interval() -> dict:
    """Conservative corner interval from quoted marginal 68% mass/radius bounds.

    This is not a joint posterior interval; it is only an uncertainty-sensitivity
    envelope made from the published one-dimensional bounds.
    """

    mass_low = PSR_MASS_SOLAR - PSR_MASS_SOLAR_MINUS
    mass_high = PSR_MASS_SOLAR + PSR_MASS_SOLAR_PLUS
    radius_low = PSR_RADIUS_M - PSR_RADIUS_MINUS_M
    radius_high = PSR_RADIUS_M + PSR_RADIUS_PLUS_M
    u_low = 2.0 * (mass_low * MU_SUN) / (radius_high * C**2)
    u_high = 2.0 * (mass_high * MU_SUN) / (radius_low * C**2)
    return {
        "method": "corner envelope from separate published 68% marginal bounds; not a joint credible interval",
        "compactness_u_low": u_low,
        "compactness_u_high": u_high,
        "time_allocation_low": 2.0 * (1.0 - u_high),
        "time_allocation_high": 2.0 * (1.0 - u_low),
    }


def sun_earth_active_ridge() -> dict:
    """Newton III example: equal forces, different accelerations."""

    earth_mass = MU_EARTH / G
    sun_mass = MU_SUN / G
    acceleration_earth_due_sun = MU_SUN / AU**2
    acceleration_sun_due_earth = MU_EARTH / AU**2
    force_on_earth = earth_mass * acceleration_earth_due_sun
    force_on_sun = sun_mass * acceleration_sun_due_earth
    pair_force_mean = 0.5 * (force_on_earth + force_on_sun)
    force_relative_mismatch = abs(force_on_earth - force_on_sun) / pair_force_mean

    # The magnitudes are equal and the directions are opposite.  x=1 describes
    # the enclosing internal-force account, while each body still accelerates.
    x_ridge = 2.0 * force_on_sun / (force_on_earth + force_on_sun)

    return {
        "separation_m": AU,
        "force_on_earth_by_sun_N": force_on_earth,
        "force_on_sun_by_earth_N": force_on_sun,
        "force_relative_mismatch_numeric": force_relative_mismatch,
        "enclosing_pair_ara_x": x_ridge,
        "enclosing_pair_net_internal_force_N": force_on_earth - force_on_sun,
        "enclosing_pair_active_force_total_N": force_on_earth + force_on_sun,
        "earth_acceleration_due_sun_m_s2": acceleration_earth_due_sun,
        "sun_acceleration_due_earth_m_s2": acceleration_sun_due_earth,
        "acceleration_ratio": acceleration_earth_due_sun / acceleration_sun_due_earth,
        "mass_ratio_sun_to_earth": sun_mass / earth_mass,
    }


def ara_force_identity_examples() -> list[dict]:
    """Exact Newton-II opposition-coordinate checks."""

    cases = [
        ("active ridge", 10.0, 10.0, 2.0),
        ("Phase A dominant", 15.0, 5.0, 4.0),
        ("Phase B dominant", 5.0, 15.0, 4.0),
    ]
    rows = []
    for label, force_a, force_b, mass in cases:
        sigma = force_a + force_b
        x = 2.0 * force_b / sigma
        net_force_direct = force_b - force_a
        net_force_ara = sigma * (x - 1.0)
        rows.append(
            {
                "label": label,
                "phase_A_force_magnitude_N": force_a,
                "phase_B_force_magnitude_N": force_b,
                "ara_x": x,
                "dimensional_force_envelope_N": sigma,
                "net_force_direct_N": net_force_direct,
                "net_force_from_ara_identity_N": net_force_ara,
                "acceleration_m_s2": net_force_direct / mass,
                "identity_absolute_error_N": abs(net_force_direct - net_force_ara),
            }
        )
    return rows


def main() -> None:
    bodies = [
        spherical_exterior_row("Earth (IAU nominal equatorial)", MU_EARTH, R_EARTH_EQUATOR),
        spherical_exterior_row("Jupiter (IAU nominal equatorial)", MU_JUPITER, R_JUPITER_EQUATOR),
        spherical_exterior_row("Sun (IAU nominal)", MU_SUN, R_SUN),
        spherical_exterior_row(
            "PSR J0740+6620 (central spherical proxy)",
            PSR_MASS_SOLAR * MU_SUN,
            PSR_RADIUS_M,
        ),
    ]

    result = {
        "analysis_id": "GR_NEWTON_ARA_RUNG_CROSSING_2026-07-23",
        "constants": {
            "c_m_s_exact": C,
            "G_m3_kg_s2_CODATA_2022": G,
            "IAU_nominal_mu_sun_m3_s2": MU_SUN,
            "IAU_nominal_radius_sun_m": R_SUN,
            "IAU_nominal_mu_earth_m3_s2": MU_EARTH,
            "IAU_nominal_equatorial_radius_earth_m": R_EARTH_EQUATOR,
            "IAU_nominal_mu_jupiter_m3_s2": MU_JUPITER,
            "IAU_nominal_equatorial_radius_jupiter_m": R_JUPITER_EQUATOR,
            "astronomical_unit_m_exact": AU,
        },
        "sources": [
            {
                "title": "IAU 2015 Resolution B3",
                "url": "https://www.iau.org/common/Uploaded%20files/IAUGA2015-Resolution-B3-recommended-nominal-conversion.pdf",
            },
            {
                "title": "NIST CODATA 2022 recommended constants",
                "url": "https://pml.nist.gov/cuu/pdf/wall_2022.pdf",
            },
            {
                "title": "Dittmann et al. 2024 PSR J0740+6620 mass/radius",
                "url": "https://arxiv.org/abs/2406.14467",
            },
        ],
        "declared_models": {
            "compactness_examples": "exterior spherical non-rotating Schwarzschild model",
            "weak_field": "|Phi|/c^2 << 1, stationary source, slow test body, negligible pressure",
            "neutron_star_caveat": (
                "central mass/radius inserted into a spherical Schwarzschild exterior proxy; "
                "the pulsar rotates and the published mass/radius have uncertainty"
            ),
            "ARA_compactness_coordinate": (
                "proposed normalization t_Time=2(1-u), t_Connection=2u with u=2GM/(Rc^2); "
                "not a new GR law and not uniquely forced by GR"
            ),
        },
        "compactness_examples": bodies,
        "psr_uncertainty_sensitivity": psr_compactness_interval(),
        "sun_earth_newton_III_active_ridge": sun_earth_active_ridge(),
        "newton_II_ara_force_identity_examples": ara_force_identity_examples(),
        "theoretical_horizon_endpoint": {
            "compactness_u": 1.0,
            "time_allocation_proposed": 0.0,
            "connection_allocation_proposed": 2.0,
            "schwarzschild_lapse": 0.0,
            "weak_field_valid": False,
            "note": "event horizon is a causal/coordinate boundary, not the r=0 curvature singularity",
        },
    }

    RESULT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    with RESULT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(bodies[0].keys()))
        writer.writeheader()
        writer.writerows(bodies)

    print(f"Wrote {RESULT_JSON}")
    print(f"Wrote {RESULT_CSV}")
    for row in bodies:
        print(
            f"{row['name']}: u={row['compactness_u']:.9g}, "
            f"x_Time={row['time_allocation_proposed']:.9g}, "
            f"weak-lapse rel.err={row['weak_lapse_relative_error']:.9g}"
        )


if __name__ == "__main__":
    main()

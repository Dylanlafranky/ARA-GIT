"""Independent checks for the virial/ARA cross-scale ladder."""

from __future__ import annotations

import json
import math
from pathlib import Path

from virial_cross_scale_ladder import (
    AU,
    BOHR_RADIUS,
    EARTH_ORBIT_ECCENTRICITY,
    HARTREE_EV,
    ara_virial_coordinate,
    build_earth_orbit_curve,
    build_ladder,
    raw_te_allocations,
)


HERE = Path(__file__).resolve().parent
TOL = 5e-13


def close(a: float, b: float, tol: float = TOL) -> bool:
    return math.isclose(a, b, rel_tol=tol, abs_tol=tol)


def main() -> None:
    ladder = build_ladder()
    orbit_wide, _ = build_earth_orbit_curve()
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("four declared rungs", len(ladder) == 4, f"rows={len(ladder)}")

    max_virial_error = max(
        abs(row.traversal_channel - row.connection_channel) for row in ladder
    )
    relative_virial_error = max(
        abs(row.traversal_channel - row.connection_channel)
        / row.connection_channel
        for row in ladder
    )
    check(
        "inverse-distance virial equality",
        relative_virial_error < TOL,
        f"max relative error={relative_virial_error:.3e}",
    )

    max_x_error = max(abs(row.virial_ara_coordinate - 1.0) for row in ladder)
    check(
        "virial ARA ridge on every rung",
        max_x_error < TOL,
        f"max |x-1|={max_x_error:.3e}",
    )

    max_te_error = max(abs(row.te_ara_total - 2.0) for row in ladder)
    check(
        "raw TE-ARA closure",
        max_te_error < TOL,
        f"max |total-2|={max_te_error:.3e}",
    )

    max_raw_t_error = max(
        abs(row.raw_traversal_allocation - 2.0 / 3.0) for row in ladder
    )
    max_raw_c_error = max(
        abs(row.raw_connection_allocation - 4.0 / 3.0) for row in ladder
    )
    check(
        "raw allocation remains asymmetric",
        max(max_raw_t_error, max_raw_c_error) < TOL,
        (
            f"max traversal error={max_raw_t_error:.3e}; "
            f"max connection error={max_raw_c_error:.3e}"
        ),
    )

    classical = ladder[2]
    quantum = ladder[3]
    check(
        "classical and quantum Coulomb energy magnitudes agree in the ideal model",
        close(classical.mean_kinetic, quantum.mean_kinetic)
        and close(abs(classical.mean_potential), abs(quantum.mean_potential))
        and close(classical.mean_kinetic, HARTREE_EV / 2.0),
        (
            f"T_classical={classical.mean_kinetic:.12f} eV; "
            f"T_quantum={quantum.mean_kinetic:.12f} eV"
        ),
    )

    span = math.log10(AU / BOHR_RADIUS)
    check(
        "cross-scale span exceeds 21 orders of magnitude",
        span > 21.0,
        f"log10(AU/a0)={span:.9f}",
    )

    instantaneous = [row["instantaneous_ara"] for row in orbit_wide[:-1]]
    check(
        "elliptical child readings straddle the ridge",
        min(instantaneous) < 1.0 < max(instantaneous),
        f"range=[{min(instantaneous):.12f}, {max(instantaneous):.12f}]",
    )

    # The exact endpoint formulas provide an independent check of the orbit code.
    expected_peri = 2.0 * (1.0 + EARTH_ORBIT_ECCENTRICITY) / (
        2.0 + EARTH_ORBIT_ECCENTRICITY
    )
    expected_aphe = 2.0 * (1.0 - EARTH_ORBIT_ECCENTRICITY) / (
        2.0 - EARTH_ORBIT_ECCENTRICITY
    )
    check(
        "perihelion and aphelion ARA endpoints",
        close(max(instantaneous), expected_peri, 1e-11)
        and close(min(instantaneous), expected_aphe, 1e-11),
        f"expected=[{expected_aphe:.12f}, {expected_peri:.12f}]",
    )

    completed = orbit_wide[-1]["cumulative_channel_ara"]
    check(
        "completed Earth channel account reaches parent ridge",
        close(completed, 1.0, 1e-12),
        f"completed x={completed:.15f}",
    )

    # Random positive energy scales verify that the normalized result is
    # independent of native magnitude when |V|=2T.
    max_scale_invariance_error = 0.0
    for exponent in range(-30, 31):
        kinetic = 10.0**exponent
        potential = -2.0 * kinetic
        x = ara_virial_coordinate(kinetic, potential)
        raw_t, raw_c = raw_te_allocations(kinetic, potential)
        max_scale_invariance_error = max(
            max_scale_invariance_error,
            abs(x - 1.0),
            abs(raw_t - 2.0 / 3.0),
            abs(raw_c - 4.0 / 3.0),
        )
    check(
        "normalization is invariant over 60 decades",
        max_scale_invariance_error < TOL,
        f"max error={max_scale_invariance_error:.3e}",
    )

    # Algebraic identity check for arbitrary positive channels.
    max_identity_error = 0.0
    for i in range(1, 10_001):
        kinetic = 0.001 + (i * 0.6180339887498949) % 19.0
        connection = 0.001 + (i * 0.4142135623730950) % 23.0
        expected = 4.0 * kinetic / (2.0 * kinetic + connection)
        observed = ara_virial_coordinate(kinetic, -connection)
        max_identity_error = max(max_identity_error, abs(expected - observed))
    check(
        "10,000 independent coordinate identities",
        max_identity_error < TOL,
        f"max error={max_identity_error:.3e}",
    )

    # Distinguish the two declared measurements.
    check(
        "raw allocation and virial comparison are not flattened together",
        all(
            not close(row.raw_traversal_allocation, row.virial_ara_coordinate)
            and not close(row.raw_connection_allocation, row.virial_ara_coordinate)
            for row in ladder
        ),
        "raw markers=2/3 and 4/3; virial marker=1",
    )

    passed = sum(item["passed"] for item in checks)
    result = {
        "status": "passed" if passed == len(checks) else "failed",
        "passed": passed,
        "total": len(checks),
        "max_native_virial_absolute_error": max_virial_error,
        "max_relative_virial_error": relative_virial_error,
        "max_ara_ridge_error": max_x_error,
        "max_te_ara_closure_error": max_te_error,
        "checks": checks,
    }
    (HERE / "VIRIAL_CROSS_SCALE_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

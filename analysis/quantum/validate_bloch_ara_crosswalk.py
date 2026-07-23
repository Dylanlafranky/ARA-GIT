"""Independent numerical property checks for the Bloch–ARA crosswalk."""

from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path


HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "BLOCH_ARA_EXAMPLE_STATES.csv"
OUTPUT_PATH = HERE / "BLOCH_ARA_VALIDATION.json"
TOLERANCE = 2e-12


def result(name: str, passed: bool, detail: str) -> dict[str, str | bool]:
    return {"name": name, "passed": bool(passed), "detail": detail}


def random_unit_vector(rng: random.Random) -> tuple[float, float, float]:
    z = rng.uniform(-1.0, 1.0)
    phi = rng.uniform(-math.pi, math.pi)
    radial = math.sqrt(max(0.0, 1.0 - z * z))
    return radial * math.cos(phi), radial * math.sin(phi), z


def main() -> None:
    with CSV_PATH.open("r", encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    checks: list[dict[str, str | bool]] = []
    checks.append(result("example row count", len(rows) == 7, f"rows={len(rows)}"))

    max_probability_error = 0.0
    max_affine_error = 0.0
    valid_ball = True
    for row in rows:
        radius = float(row["bloch_radius"])
        p_a = float(row["probability_A"])
        p_b = float(row["probability_B"])
        rz = float(row["bloch_z"])
        x_q = float(row["ara_x_B_oriented"])
        max_probability_error = max(max_probability_error, abs(p_a + p_b - 1.0))
        max_affine_error = max(max_affine_error, abs(x_q - (1.0 - rz)))
        valid_ball = valid_ball and radius <= 1.0 + TOLERANCE

    checks.extend(
        [
            result(
                "example probability closure",
                max_probability_error <= TOLERANCE,
                f"max_abs_error={max_probability_error:.3e}",
            ),
            result(
                "example affine ARA relation",
                max_affine_error <= TOLERANCE,
                f"max_abs_error={max_affine_error:.3e}",
            ),
            result("example states lie in Bloch ball", valid_ball, "all |r|<=1"),
        ]
    )

    by_label = {row["label"]: row for row in rows}
    checks.extend(
        [
            result(
                "ARA north/ridge/south landmarks",
                abs(float(by_label["pure_A_north_pole"]["ara_x_B_oriented"])) <= TOLERANCE
                and abs(
                    float(by_label["coherent_equal_phase_0"]["ara_x_B_oriented"]) - 1.0
                )
                <= TOLERANCE
                and abs(
                    float(by_label["pure_B_south_pole"]["ara_x_B_oriented"]) - 2.0
                )
                <= TOLERANCE,
                "x_Q=0,1,2",
            ),
            result(
                "ridge degeneracy: coherence and mixture",
                abs(
                    float(by_label["coherent_equal_phase_0"]["ara_x_B_oriented"])
                    - float(by_label["fully_mixed_center"]["ara_x_B_oriented"])
                )
                <= TOLERANCE
                and abs(
                    float(by_label["coherent_equal_phase_0"]["bloch_radius"]) - 1.0
                )
                <= TOLERANCE
                and abs(float(by_label["fully_mixed_center"]["bloch_radius"]))
                <= TOLERANCE,
                "same x_Q=1; radii 1 and 0",
            ),
            result(
                "relative-phase degeneracy on ARA diameter",
                abs(
                    float(by_label["coherent_equal_phase_0"]["ara_x_B_oriented"])
                    - float(
                        by_label["coherent_equal_phase_pi_over_2"][
                            "ara_x_B_oriented"
                        ]
                    )
                )
                <= TOLERANCE
                and by_label["coherent_equal_phase_0"]["bloch_x"]
                != by_label["coherent_equal_phase_pi_over_2"]["bloch_x"],
                "same populations; distinct equatorial directions",
            ),
        ]
    )

    rng = random.Random(20260723)
    pure_trials = 10_000
    mixed_axis_trials = 10_000
    max_pure_error = 0.0
    max_mixed_error = 0.0
    pure_failures = 0
    mixed_failures = 0

    # Pure states built independently from complex amplitudes.
    for _ in range(pure_trials):
        theta = rng.uniform(0.0, math.pi)
        phi = rng.uniform(-math.pi, math.pi)
        alpha = complex(math.cos(theta / 2.0), 0.0)
        beta = complex(
            math.cos(phi) * math.sin(theta / 2.0),
            math.sin(phi) * math.sin(theta / 2.0),
        )
        p_a = abs(alpha) ** 2
        p_b = abs(beta) ** 2
        product = alpha.conjugate() * beta
        rx = 2.0 * product.real
        ry = 2.0 * product.imag
        rz = p_a - p_b
        radius = math.sqrt(rx * rx + ry * ry + rz * rz)
        x_q = 2.0 * p_b
        errors = (
            abs(p_a + p_b - 1.0),
            abs(radius - 1.0),
            abs(x_q - (1.0 - rz)),
            abs((x_q - 1.0) + rz),
        )
        local = max(errors)
        max_pure_error = max(max_pure_error, local)
        if local > TOLERANCE:
            pure_failures += 1

    # Mixed Bloch-ball states and arbitrary measurement diameters.
    for _ in range(mixed_axis_trials):
        ux, uy, uz = random_unit_vector(rng)
        radius = rng.random()
        rx, ry, rz = radius * ux, radius * uy, radius * uz
        nx, ny, nz = random_unit_vector(rng)
        projection = rx * nx + ry * ny + rz * nz
        p_plus = (1.0 + projection) / 2.0
        p_minus = (1.0 - projection) / 2.0
        x_n = 2.0 * p_minus
        eigen_plus = (1.0 + radius) / 2.0
        eigen_minus = (1.0 - radius) / 2.0
        errors = (
            abs(p_plus + p_minus - 1.0),
            abs(x_n - (1.0 - projection)),
            max(0.0, -p_plus, -p_minus, p_plus - 1.0, p_minus - 1.0),
            max(0.0, -eigen_plus, -eigen_minus),
        )
        local = max(errors)
        max_mixed_error = max(max_mixed_error, local)
        if local > TOLERANCE:
            mixed_failures += 1

    checks.extend(
        [
            result(
                "10,000 random pure states",
                pure_failures == 0,
                f"failures={pure_failures}; max_error={max_pure_error:.3e}",
            ),
            result(
                "10,000 random mixed states and axes",
                mixed_failures == 0,
                f"failures={mixed_failures}; max_error={max_mixed_error:.3e}",
            ),
        ]
    )

    # Ideal resonant Rabi motion beginning at A.
    rabi_trials = 4097
    max_rabi_error = 0.0
    for index in range(rabi_trials):
        phase = 8.0 * math.pi * index / (rabi_trials - 1)
        rz = math.cos(phase)
        p_b = math.sin(phase / 2.0) ** 2
        x_from_probability = 2.0 * p_b
        x_from_bloch = 1.0 - rz
        max_rabi_error = max(
            max_rabi_error, abs(x_from_probability - x_from_bloch)
        )
    checks.append(
        result(
            "ideal Rabi ARA cycle",
            max_rabi_error <= TOLERANCE,
            f"max_abs_error={max_rabi_error:.3e}",
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
            "The result is an affine reparameterization of established Bloch coordinates.",
            "ARA x=1 fixes one projection only; phase and purity remain unresolved.",
            "The validation does not establish universal ARA geometry or quantum gravity.",
        ],
    }

    with OUTPUT_PATH.open("w", encoding="utf-8") as output_file:
        json.dump(validation, output_file, indent=2)
        output_file.write("\n")

    print(json.dumps(validation, indent=2))
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

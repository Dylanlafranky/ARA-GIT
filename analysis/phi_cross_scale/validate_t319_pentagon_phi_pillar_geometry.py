"""Independent validator for T319.

This script deliberately does not import the analysis implementation. It
reconstructs the regular pentagon, its pentagram intersections, the two
offset triangles, and the polygon controls from first principles, then
compares those values with the saved T319 result.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS_PATH = ROOT / "T319_PENTAGON_PHI_PILLAR_GEOMETRY_RESULTS.json"
TOL = 1e-11
PHI = (1.0 + math.sqrt(5.0)) / 2.0


def close(a: float, b: float, tolerance: float = TOL) -> bool:
    return abs(a - b) <= tolerance


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def cross(a: tuple[float, float], b: tuple[float, float]) -> float:
    return a[0] * b[1] - a[1] * b[0]


def intersect(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
    d: tuple[float, float],
) -> tuple[tuple[float, float], float, float] | None:
    r = (b[0] - a[0], b[1] - a[1])
    s = (d[0] - c[0], d[1] - c[1])
    denominator = cross(r, s)
    if abs(denominator) < 1e-15:
        return None
    ca = (c[0] - a[0], c[1] - a[1])
    t = cross(ca, s) / denominator
    u = cross(ca, r) / denominator
    if TOL < t < 1.0 - TOL and TOL < u < 1.0 - TOL:
        return ((a[0] + t * r[0], a[1] + t * r[1]), t, u)
    return None


saved = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))

# Independent side-one pentagon construction.
radius = 1.0 / (2.0 * math.sin(math.pi / 5.0))
vertices = [
    (
        radius * math.cos(math.pi / 2.0 + 2.0 * math.pi * index / 5.0),
        radius * math.sin(math.pi / 2.0 + 2.0 * math.pi * index / 5.0),
    )
    for index in range(5)
]
sides = [distance(vertices[i], vertices[(i + 1) % 5]) for i in range(5)]
diagonals = sorted({tuple(sorted((i, (i + 2) % 5))) for i in range(5)})
diagonal_lengths = [distance(vertices[i], vertices[j]) for i, j in diagonals]

raw_intersections: list[tuple[float, float]] = []
division_ratios: list[float] = []
for position, (i, j) in enumerate(diagonals):
    for k, ell in diagonals[position + 1 :]:
        if len({i, j, k, ell}) != 4:
            continue
        crossing = intersect(vertices[i], vertices[j], vertices[k], vertices[ell])
        if crossing is None:
            continue
        point, t, u = crossing
        raw_intersections.append(point)
        division_ratios.extend(
            (
                max(t, 1.0 - t) / min(t, 1.0 - t),
                max(u, 1.0 - u) / min(u, 1.0 - u),
            )
        )

inner: list[tuple[float, float]] = []
for point in raw_intersections:
    if not any(distance(point, previous) < TOL for previous in inner):
        inner.append(point)
inner.sort(key=lambda point: math.atan2(point[1], point[0]))
inner_sides = [distance(inner[i], inner[(i + 1) % 5]) for i in range(5)]

side = sum(sides) / len(sides)
diagonal = sum(diagonal_lengths) / len(diagonal_lengths)
inner_side = sum(inner_sides) / len(inner_sides)
seam = 2.0 * side - diagonal
inner_scale = inner_side / side
diagonal_central_angle = math.degrees(2.0 * math.asin(diagonal / (2.0 * radius)))

triangle_a = [0.0, 120.0, 240.0]
triangle_b = [60.0, 180.0, 300.0]
hex_angles = sorted(triangle_a + triangle_b)
hex_gaps = [
    (hex_angles[(index + 1) % 6] - hex_angles[index]) % 360.0
    for index in range(6)
]

controls = {n: 2.0 * math.cos(math.pi / n) for n in range(3, 13)}
phi_hits = [n for n, shortcut in controls.items() if close(shortcut, PHI)]

independent_checks = {
    "five_outer_sides_are_unit": len(sides) == 5 and all(close(value, 1.0) for value in sides),
    "five_equal_diagonals": len(diagonal_lengths) == 5
    and all(close(value, PHI) for value in diagonal_lengths),
    "two_edge_path_is_2": close(2.0 * side, 2.0),
    "direct_same_phase_path_is_phi": close(diagonal, PHI),
    "remaining_seam_is_phi_inverse_squared": close(seam, PHI ** -2),
    "five_unique_inner_vertices": len(inner) == 5,
    "all_pentagram_splits_are_golden": len(division_ratios) == 10
    and all(close(value, PHI) for value in division_ratios),
    "inner_pentagon_scale_is_phi_inverse_squared": close(inner_scale, PHI ** -2),
    "pentagon_step_is_72_degrees": close(360.0 / 5.0, 72.0),
    "pentagon_interior_is_108_degrees": close(180.0 * 3.0 / 5.0, 108.0),
    "pentagon_diagonal_spans_144_degrees": close(diagonal_central_angle, 144.0),
    "two_triangles_make_six_directions": len(set(hex_angles)) == 6,
    "hexagonal_direction_gaps_are_60_degrees": all(close(gap, 60.0) for gap in hex_gaps),
    "pentagon_is_unique_phi_control_n3_to_n12": phi_hits == [5],
    "square_control_is_sqrt2": close(controls[4], math.sqrt(2.0)),
    "hexagon_control_is_sqrt3": close(controls[6], math.sqrt(3.0)),
}

saved_pentagon = saved["pentagon"]
saved_checks = {
    "saved_side_matches": close(saved_pentagon["side"], side),
    "saved_two_side_path_matches": close(saved_pentagon["two_side_path"], 2.0 * side),
    "saved_diagonal_matches": close(saved_pentagon["diagonal"], diagonal),
    "saved_seam_matches": close(saved_pentagon["path_minus_diagonal_seam"], seam),
    "saved_inner_scale_matches": close(saved_pentagon["inner_to_outer_side_ratio"], inner_scale),
    "saved_diagonal_angle_matches": close(
        saved_pentagon["diagonal_central_angle_degrees"], diagonal_central_angle
    ),
    "saved_claims_all_passed": saved["checks_passed"] == saved["checks_total"] == 13,
}

all_checks = {**independent_checks, **saved_checks}
validation = {
    "validation_id": "T319-INDEPENDENT-VALIDATION-v1",
    "analysis_imported": False,
    "status": "VALIDATED" if all(all_checks.values()) else "VALIDATION FAILED",
    "checks_passed": sum(all_checks.values()),
    "checks_total": len(all_checks),
    "checks": all_checks,
    "recomputed": {
        "phi": PHI,
        "two_edge_path": 2.0 * side,
        "same_phase_diagonal": diagonal,
        "seam": seam,
        "inner_scale": inner_scale,
        "diagonal_central_angle_degrees": diagonal_central_angle,
        "division_ratios": division_ratios,
        "hexagonal_gaps_degrees": hex_gaps,
        "polygon_shortcuts": controls,
    },
    "scope_boundary": (
        "This validates the exact geometric construction and saved calculations only; "
        "it does not validate a physical Phi-pillar mechanism."
    ),
}

(ROOT / "T319_PENTAGON_PHI_PILLAR_GEOMETRY_VALIDATION.json").write_text(
    json.dumps(validation, indent=2), encoding="utf-8"
)
print(json.dumps(validation, indent=2))
raise SystemExit(0 if validation["status"] == "VALIDATED" else 1)

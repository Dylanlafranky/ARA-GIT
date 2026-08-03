"""T319: exact two-ARA Hexagon / Pentagon Phi-pillar construction."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TOL = 1e-12
PHI = (1 + math.sqrt(5)) / 2
Point = tuple[float, float]


def add(a: Point, b: Point) -> Point:
    return a[0] + b[0], a[1] + b[1]


def sub(a: Point, b: Point) -> Point:
    return a[0] - b[0], a[1] - b[1]


def mul(a: Point, scalar: float) -> Point:
    return a[0] * scalar, a[1] * scalar


def cross(a: Point, b: Point) -> float:
    return a[0] * b[1] - a[1] * b[0]


def distance(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def segment_intersection(
    p: Point, p2: Point, q: Point, q2: Point
) -> tuple[Point, float, float] | None:
    r = sub(p2, p)
    s = sub(q2, q)
    denominator = cross(r, s)
    if abs(denominator) < 1e-15:
        return None
    qp = sub(q, p)
    t = cross(qp, s) / denominator
    u = cross(qp, r) / denominator
    if TOL < t < 1 - TOL and TOL < u < 1 - TOL:
        return add(p, mul(r, t)), t, u
    return None


def regular_polygon(n: int, side: float = 1.0, start_angle: float = math.pi / 2) -> list[Point]:
    radius = side / (2 * math.sin(math.pi / n))
    return [
        (
            radius * math.cos(start_angle + 2 * math.pi * i / n),
            radius * math.sin(start_angle + 2 * math.pi * i / n),
        )
        for i in range(n)
    ]


pentagon = regular_polygon(5)
side_lengths = [distance(pentagon[i], pentagon[(i + 1) % 5]) for i in range(5)]
diagonal_pairs = sorted({tuple(sorted((i, (i + 2) % 5))) for i in range(5)})
diagonal_lengths = [distance(pentagon[i], pentagon[j]) for i, j in diagonal_pairs]

intersections: list[Point] = []
division_ratios: list[float] = []
for index, (i, j) in enumerate(diagonal_pairs):
    for k, ell in diagonal_pairs[index + 1 :]:
        if len({i, j, k, ell}) < 4:
            continue
        result = segment_intersection(pentagon[i], pentagon[j], pentagon[k], pentagon[ell])
        if result is None:
            continue
        point, t, u = result
        intersections.append(point)
        division_ratios.extend(
            [max(t, 1 - t) / min(t, 1 - t), max(u, 1 - u) / min(u, 1 - u)]
        )


def unique_points(points: list[Point]) -> list[Point]:
    unique: list[Point] = []
    for point in points:
        if not any(distance(point, existing) < 1e-10 for existing in unique):
            unique.append(point)
    return unique


inner_pentagon = sorted(unique_points(intersections), key=lambda p: math.atan2(p[1], p[0]))
inner_side_lengths = [
    distance(inner_pentagon[i], inner_pentagon[(i + 1) % 5]) for i in range(5)
]

side = sum(side_lengths) / len(side_lengths)
diagonal = sum(diagonal_lengths) / len(diagonal_lengths)
inner_side = sum(inner_side_lengths) / len(inner_side_lengths)
two_side_path = 2 * side
seam = two_side_path - diagonal
inner_scale = inner_side / side

# Pentagon geometry angles.
circumradius = distance((0.0, 0.0), pentagon[0])
diagonal_central_angle = math.degrees(2 * math.asin(diagonal / (2 * circumradius)))
interior_angle = 180 * (5 - 2) / 5
central_step = 360 / 5

# Two equilateral Information³ triangles offset by 60 degrees.
tri_a_angles = [0.0, 120.0, 240.0]
tri_b_angles = [60.0, 180.0, 300.0]
hex_angles = sorted(tri_a_angles + tri_b_angles)
hex_gaps = [
    (hex_angles[(i + 1) % 6] - hex_angles[i]) % 360 for i in range(6)
]

polygon_controls = []
for n in range(3, 13):
    shortcut = 2 * math.cos(math.pi / n)
    polygon_controls.append(
        {
            "n": n,
            "two_edge_shortcut": shortcut,
            "absolute_error_from_phi": abs(shortcut - PHI),
        }
    )

recursive_scales = [inner_scale**level for level in range(6)]
expected_recursive_scales = [PHI ** (-2 * level) for level in range(6)]

gates = {
    "two_side_path_is_2": abs(two_side_path - 2) <= TOL,
    "diagonal_over_side_is_phi": abs(diagonal / side - PHI) <= TOL,
    "seam_is_phi_inverse_squared": abs(seam - PHI**-2) <= TOL,
    "diagonal_central_angle_is_144_degrees": abs(diagonal_central_angle - 144) <= TOL,
    "pentagon_interior_angle_is_108_degrees": abs(interior_angle - 108) <= TOL,
    "all_diagonal_divisions_are_golden": all(abs(ratio - PHI) <= TOL for ratio in division_ratios),
    "inner_pentagon_scale_is_phi_inverse_squared": abs(inner_scale - PHI**-2) <= TOL,
    "recursive_scales_follow_phi_inverse_even_powers": all(
        abs(actual - expected) <= TOL
        for actual, expected in zip(recursive_scales, expected_recursive_scales)
    ),
    "two_triangles_supply_six_outer_directions": len(set(hex_angles)) == 6,
    "hexagonal_steps_are_60_degrees": all(abs(gap - 60) <= TOL for gap in hex_gaps),
    "pentagon_unique_phi_shortcut_in_n3_to_n12": [
        row["n"]
        for row in polygon_controls
        if row["absolute_error_from_phi"] <= TOL
    ]
    == [5],
    "hexagon_shortcut_is_sqrt3": abs(polygon_controls[3]["two_edge_shortcut"] - math.sqrt(3)) <= TOL,
    "square_shortcut_is_sqrt2": abs(polygon_controls[1]["two_edge_shortcut"] - math.sqrt(2)) <= TOL,
}

results = {
    "test_id": "T319-PENTAGON-PHI-PILLAR-GEOMETRY-v1",
    "status": "EXACT PENTAGON PILLAR SUPPORTED" if all(gates.values()) else "PARTIAL OR NOT SUPPORTED",
    "evidence_class": "exact geometry / internal consistency; not empirical",
    "constants": {"phi": PHI, "phi_inverse_squared": PHI**-2},
    "pentagon": {
        "side": side,
        "two_side_path": two_side_path,
        "diagonal": diagonal,
        "diagonal_over_side": diagonal / side,
        "path_minus_diagonal_seam": seam,
        "circumradius_when_side_is_1": circumradius,
        "central_step_degrees": central_step,
        "interior_angle_degrees": interior_angle,
        "diagonal_central_angle_degrees": diagonal_central_angle,
        "inner_pentagon_side": inner_side,
        "inner_to_outer_side_ratio": inner_scale,
        "diagonal_intersection_ratios": division_ratios,
        "recursive_inner_scales": recursive_scales,
    },
    "hexagon": {
        "triangle_A_angles_degrees": tri_a_angles,
        "triangle_B_angles_degrees": tri_b_angles,
        "union_angles_degrees": hex_angles,
        "successive_angle_gaps_degrees": hex_gaps,
    },
    "polygon_controls": polygon_controls,
    "gates": gates,
    "checks_passed": sum(gates.values()),
    "checks_total": len(gates),
    "interpretation_boundary": (
        "The exact construction supports the ARA geometric crosswalk. It does not show that a physical system uses the pillar."
    ),
}

(ROOT / "T319_PENTAGON_PHI_PILLAR_GEOMETRY_RESULTS.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)


def svg_visual() -> str:
    width, height = 1500, 900

    def screen(point: Point, cx: float, cy: float, scale: float) -> Point:
        return cx + point[0] * scale, cy - point[1] * scale

    def points_attr(points: list[Point], cx: float, cy: float, scale: float) -> str:
        return " ".join(f"{x:.2f},{y:.2f}" for x, y in (screen(p, cx, cy, scale) for p in points))

    chunks = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>"
        ".title{font:700 28px system-ui;fill:#edf5ff}.sub{font:15px system-ui;fill:#aebbd0}"
        ".panel{fill:#131a26;stroke:#344155;stroke-width:1.5}.pt{stroke:#fff;stroke-width:1.2}"
        ".label{font:14px system-ui;fill:#dce7f5}.small{font:12px system-ui;fill:#9fb0c7}"
        ".metric{font:700 17px system-ui;fill:#f4d27b}.head{font:700 20px system-ui;fill:#edf5ff}"
        "</style>",
        '<rect width="1500" height="900" fill="#0b1018"/>',
        '<text x="60" y="52" class="title">T319 — Two-ARA Hexagon and Pentagon Phi pillars</text>',
        '<text x="60" y="80" class="sub">Exact construction: two unit legs close through B; the same-phase A→A diagonal is φ</text>',
        '<rect class="panel" x="45" y="110" width="640" height="590" rx="16"/>',
        '<rect class="panel" x="715" y="110" width="740" height="590" rx="16"/>',
        '<rect class="panel" x="45" y="730" width="1410" height="125" rx="16"/>',
        '<text x="70" y="145" class="head">Hexagon: two Information³ triangles</text>',
        '<text x="740" y="145" class="head">Pentagon: five recursive same-phase pillars</text>',
    ]

    # Hexagram / six-node parent.
    hcx, hcy, hr = 365, 415, 225
    hex_points = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in hex_angles]
    tri_a = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in tri_a_angles]
    tri_b = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in tri_b_angles]
    chunks.append(f'<circle cx="{hcx}" cy="{hcy}" r="{hr}" fill="none" stroke="#314158" stroke-width="2"/>')
    chunks.append(f'<polygon points="{points_attr(tri_a, hcx, hcy, hr)}" fill="#3d72b833" stroke="#67a7ff" stroke-width="4"/>')
    chunks.append(f'<polygon points="{points_attr(tri_b, hcx, hcy, hr)}" fill="#d38a3833" stroke="#f2ad58" stroke-width="4"/>')
    chunks.append(f'<polygon points="{points_attr(hex_points, hcx, hcy, hr)}" fill="none" stroke="#e6edf7" stroke-width="2" stroke-dasharray="8 7"/>')
    for index, point in enumerate(hex_points):
        x, y = screen(point, hcx, hcy, hr)
        color = "#67a7ff" if index % 2 == 0 else "#f2ad58"
        chunks.append(f'<circle class="pt" cx="{x:.2f}" cy="{y:.2f}" r="8" fill="{color}"/>')
        chunks.append(f'<text x="{x:.2f}" y="{y-15:.2f}" class="small" text-anchor="middle">{index}</text>')
    chunks.append('<text x="365" y="670" class="label" text-anchor="middle">3 A-relations + 3 B-relations → six outer directions at 60°</text>')

    # Pentagon / pentagram.
    pcx, pcy, pr = 1085, 410, 250 / circumradius
    chunks.append(f'<polygon points="{points_attr(pentagon, pcx, pcy, pr)}" fill="#1d2838" stroke="#dce7f5" stroke-width="3"/>')
    for i, j in diagonal_pairs:
        x1, y1 = screen(pentagon[i], pcx, pcy, pr)
        x2, y2 = screen(pentagon[j], pcx, pcy, pr)
        chunks.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#f4c95d" stroke-width="2.5" opacity="0.9"/>')
    chunks.append(f'<polygon points="{points_attr(inner_pentagon, pcx, pcy, pr)}" fill="#61c8a055" stroke="#61c8a0" stroke-width="3"/>')

    # Highlight A0-B-A1 as vertices 0,1,2.
    selected = [pentagon[0], pentagon[1], pentagon[2]]
    route = points_attr(selected, pcx, pcy, pr)
    chunks.append(f'<polyline points="{route}" fill="none" stroke="#68a8ff" stroke-width="7" stroke-linecap="round"/>')
    a0x, a0y = screen(pentagon[0], pcx, pcy, pr)
    bx, by = screen(pentagon[1], pcx, pcy, pr)
    a1x, a1y = screen(pentagon[2], pcx, pcy, pr)
    chunks.append(f'<line x1="{a0x:.2f}" y1="{a0y:.2f}" x2="{a1x:.2f}" y2="{a1y:.2f}" stroke="#ff6f91" stroke-width="7" stroke-linecap="round"/>')
    for label, (x, y), color in (("A₀", (a0x, a0y), "#ff6f91"), ("B", (bx, by), "#68a8ff"), ("A₁", (a1x, a1y), "#ff6f91")):
        chunks.append(f'<circle class="pt" cx="{x:.2f}" cy="{y:.2f}" r="10" fill="{color}"/>')
        chunks.append(f'<text x="{x:.2f}" y="{y-18:.2f}" class="label" text-anchor="middle">{label}</text>')
    chunks.append('<text x="1085" y="665" class="label" text-anchor="middle">blue route: 1 + 1 = 2 · pink pillar: φ · green inner rung: φ⁻²</text>')

    chunks.extend(
        [
            '<text x="75" y="770" class="metric">A₀→B→A₁ = 2</text>',
            f'<text x="330" y="770" class="metric">A₀→A₁ = φ = {PHI:.9f}</text>',
            f'<text x="690" y="770" class="metric">seam = 2−φ = φ⁻² = {PHI**-2:.9f}</text>',
            '<text x="1135" y="770" class="metric">angles: 72° · 108° · 144°</text>',
            '<text x="75" y="812" class="small">The five yellow diagonals are the Phi pillars. Their intersections generate the next inner pentagon automatically.</text>',
            '<text x="75" y="836" class="small">Geometry pass is exact; whether physical ARA systems use this scaffold remains an empirical question.</text>',
            "</svg>",
        ]
    )
    return "\n".join(chunks)


svg = svg_visual()
(ROOT / "T319_PENTAGON_PHI_PILLAR_GEOMETRY.svg").write_text(svg, encoding="utf-8")
(ROOT / "T319_PENTAGON_PHI_PILLAR_GEOMETRY.html").write_text(
    """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>T319 Pentagon Phi pillars</title><style>
html,body{margin:0;background:#080c12}main{min-height:100vh;display:grid;place-items:center;padding:18px}
svg{width:min(98vw,1500px);height:auto;box-shadow:0 20px 70px #000b;border-radius:16px}
</style></head><body><main>"""
    + svg
    + "</main></body></html>",
    encoding="utf-8",
)

print(json.dumps(results, indent=2))

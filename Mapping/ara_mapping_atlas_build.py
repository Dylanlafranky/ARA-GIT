#!/usr/bin/env python3
"""
Build a mapping-first ARA atlas for the 3D temporal coordinate visualiser.

This script intentionally does not score forecasts. It gathers:
  - the original temporal_coordinates_3d catalogue nodes
  - current measured subsystem rungs from systems_map_v3_data.js
  - current ARA state-geometry rungs from ara_state_geometry_data.js

and derives geometry-only coordinates: phi rung, ARA class, nearest boundary,
scale domain, and candidate same-rung / vertical-ARA matches.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FORMULA = ROOT / "TheFormula"
OLD_HTML = ROOT / "archive" / "early_visualizations" / "temporal_coordinates_3d.html"
SYSTEMS_V3 = FORMULA / "systems_map_v3_data.js"
STATE_GEOMETRY = FORMULA / "ara_state_geometry_data.js"
OUT_JSON = HERE / "ara_mapping_atlas_data.json"
OUT_JS = HERE / "ara_mapping_atlas_data.js"

PHI = (1.0 + 5.0**0.5) / 2.0
SECONDS_PER_DAY = 86400.0
SECONDS_PER_MONTH = 365.25 * SECONDS_PER_DAY / 12.0
SECONDS_PER_YEAR = 365.25 * SECONDS_PER_DAY
EPS = 1e-30

ARA_BOUNDARIES = [
    {"name": "space", "value": 0.0},
    {"name": "lower_wall", "value": 0.25},
    {"name": "balance", "value": 1.0},
    {"name": "phi", "value": PHI},
    {"name": "upper_wall", "value": 1.75},
    {"name": "time", "value": 2.0},
]


def safe_slug(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", str(value).strip().lower())
    return text.strip("_") or "item"


def fix_text(value: str) -> str:
    replacements = {
        "â€”": "-",
        "â€“": "-",
        "â†’": "->",
        "Ï†": "phi",
        "Î¸": "theta",
        "Ã©": "e",
        "Ã¡": "a",
        "Ã¡": "a",
        "Ã¡": "a",
        "Ã©": "e",
        "Ã¡": "a",
        "Ã¶": "o",
        "Ã¼": "u",
        "Â°": " deg",
        "Âµ": "u",
        "Â·": ".",
        "â‰ˆ": "~",
    }
    out = str(value)
    for src, dst in replacements.items():
        out = out.replace(src, dst)
    return out


def strip_js_comments(text: str) -> str:
    out_lines = []
    for line in text.splitlines():
        in_single = False
        in_double = False
        escaped = False
        cut = len(line)
        for i, ch in enumerate(line):
            if escaped:
                escaped = False
                continue
            if ch == "\\":
                escaped = True
                continue
            if ch == "'" and not in_double:
                in_single = not in_single
            elif ch == '"' and not in_single:
                in_double = not in_double
            elif ch == "/" and i + 1 < len(line) and line[i + 1] == "/" and not in_single and not in_double:
                cut = i
                break
        out_lines.append(line[:cut])
    return "\n".join(out_lines)


def extract_balanced_after(text: str, marker: str, opener: str, closer: str) -> str:
    start = text.index(marker) + len(marker)
    while start < len(text) and text[start].isspace():
        start += 1
    if text[start] != opener:
        start = text.index(opener, start)
    depth = 0
    in_single = False
    in_double = False
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            continue
        if in_single or in_double:
            continue
        if ch == opener:
            depth += 1
        elif ch == closer:
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    raise ValueError(f"Could not balance {marker}")


def js_to_python_literal(js: str):
    cleaned = strip_js_comments(js)
    cleaned = re.sub(r"([{\[,]\s*)([A-Za-z_]\w*)\s*:", r"\1'\2':", cleaned)
    return eval(cleaned, {"__builtins__": {}}, {"PI": math.pi})


def js_assignment_to_json(path: Path, assignment: str):
    text = path.read_text(encoding="utf-8")
    body = text.split(assignment, 1)[1].strip()
    if body.endswith(";"):
        body = body[:-1]
    return json.loads(body)


def classify_ara(ara: float | None) -> str:
    if ara is None or not math.isfinite(ara):
        return "unknown"
    if ara < 0.20:
        return "snap"
    if ara < 0.70:
        return "consumer"
    if ara < 1.25:
        return "balance_clock"
    if ara < 1.55:
        return "shock_absorber"
    if ara < 1.72:
        return "engine_phi"
    if ara < 1.90:
        return "donor_wall"
    if ara < 2.20:
        return "resonant_pair"
    if ara < 5.0:
        return "coupled_extreme"
    return "overflow"


def scale_domain(period_seconds: float) -> str:
    if period_seconds < 1e-9:
        return "quantum_atomic"
    if period_seconds < 1e-3:
        return "micro_fast"
    if period_seconds < 60:
        return "human_fast"
    if period_seconds < SECONDS_PER_DAY:
        return "daily_biological"
    if period_seconds < SECONDS_PER_YEAR * 20:
        return "earth_climate"
    if period_seconds < SECONDS_PER_YEAR * 1e6:
        return "geological"
    return "cosmic"


def nearest_boundary(ara: float | None):
    if ara is None or not math.isfinite(ara):
        return {"name": "unknown", "value": None, "distance": None}
    nearest = min(ARA_BOUNDARIES, key=lambda b: abs(ara - b["value"]))
    return {
        "name": nearest["name"],
        "value": nearest["value"],
        "distance": abs(ara - nearest["value"]),
    }


def ara_position_status(ara: float | None):
    if ara is None or not math.isfinite(ara):
        return {
            "status": "unknown",
            "note": "ARA is missing or non-finite.",
        }
    if ara < 0:
        return {
            "status": "below_zero_invalid",
            "note": "ARA is below the bounded geometry range and should be rechecked.",
        }
    if ara <= 2.0:
        return {
            "status": "bounded_position",
            "note": "ARA sits inside the clean 0-2 geometry band.",
        }
    return {
        "status": "above_two_diagnostic",
        "note": "ARA is above 2. Treat this as a compound-system or rung-mismatch candidate, not a clean bounded position.",
    }


def theta_from_ara(ara: float | None) -> float | None:
    if ara is None or ara <= 0 or not math.isfinite(ara):
        return None
    if ara >= 1e6:
        return 0.01
    val = math.pi * (ara - 1.0) / (2.0 * (1.0 + ara))
    if abs(val) > math.pi / 2.0:
        return 0.1
    c = math.sin(val)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def base_node(
    *,
    node_id: str,
    name: str,
    system: str,
    system_label: str,
    period_seconds: float,
    ara: float | None,
    energy_j: float | None = None,
    weight_value: float | None = None,
    weight_label: str = "Action/pi",
    source: str,
    layer: str,
    notes: str = "",
    extra: dict | None = None,
):
    if period_seconds <= 0 or not math.isfinite(period_seconds):
        raise ValueError(f"Bad period for {node_id}: {period_seconds}")
    ara_value = float(ara) if ara is not None and math.isfinite(float(ara)) else None
    action_pi = None
    if energy_j is not None and math.isfinite(float(energy_j)):
        action_pi = float(period_seconds) * float(energy_j) / math.pi
    if weight_value is None:
        weight_value = action_pi if action_pi is not None else 1.0
    phi_rung = math.log(period_seconds) / math.log(PHI)
    log_period = math.log10(max(period_seconds, EPS))
    log_weight = math.log10(max(abs(float(weight_value)), EPS))
    boundary = nearest_boundary(ara_value)
    ara_status = ara_position_status(ara_value)
    payload = {
        "id": safe_slug(node_id),
        "name": fix_text(name),
        "system": safe_slug(system),
        "system_label": fix_text(system_label),
        "period_seconds": float(period_seconds),
        "period_phi_rung": float(phi_rung),
        "period_log10": float(log_period),
        "ara": ara_value,
        "ara_class": classify_ara(ara_value),
        "theta_deg": theta_from_ara(ara_value),
        "energy_j": float(energy_j) if energy_j is not None and math.isfinite(float(energy_j)) else None,
        "action_pi": action_pi,
        "weight_value": float(weight_value),
        "weight_log10": float(log_weight),
        "weight_label": weight_label,
        "scale_domain": scale_domain(period_seconds),
        "nearest_boundary": boundary,
        "ara_position_status": ara_status["status"],
        "ara_position_note": ara_status["note"],
        "distance_to_phi": abs(ara_value - PHI) if ara_value is not None else None,
        "source": source,
        "layer": layer,
        "notes": fix_text(notes),
    }
    if extra:
        payload.update(extra)
    return payload


def load_original_catalogue():
    text = OLD_HTML.read_text(encoding="utf-8")
    nodes_literal = extract_balanced_after(text, "const nodes =", "[", "]")
    couplings_literal = extract_balanced_after(text, "const couplings =", "[", "]")
    sys_names_literal = extract_balanced_after(text, "const sysNames =", "{", "}")
    raw_nodes = js_to_python_literal(nodes_literal)
    raw_couplings = js_to_python_literal(couplings_literal)
    sys_names = js_to_python_literal(sys_names_literal)

    nodes = []
    for item in raw_nodes:
        sys_key = item["sys"]
        node = base_node(
            node_id=f"catalog_{item['id']}",
            name=item["name"],
            system=f"catalog_{sys_key}",
            system_label=sys_names.get(sys_key, sys_key),
            period_seconds=float(item["T"]),
            energy_j=float(item["E"]),
            ara=float(item["ara"]),
            source="archive/early_visualizations/temporal_coordinates_3d.html",
            layer="catalog",
            notes="Original hand-curated temporal coordinate catalogue.",
            extra={"original_id": item["id"]},
        )
        nodes.append(node)

    relations = []
    type_names = {1: "handoff", 2: "feeder", 3: "counter_pair"}
    for c in raw_couplings:
        relations.append(
            {
                "id": f"catalog_link_{c['from']}_{c['to']}",
                "from": safe_slug(f"catalog_{c['from']}"),
                "to": safe_slug(f"catalog_{c['to']}"),
                "type": type_names.get(int(c.get("type", 0)), "catalog_link"),
                "source": "original_catalogue",
                "score": 1.0,
            }
        )
    return nodes, relations


def load_systems_v3_nodes():
    if not SYSTEMS_V3.exists():
        return []
    data = js_assignment_to_json(SYSTEMS_V3, "window.SYSTEMS_DATA_V3 =")
    unit_seconds = {
        "solar": SECONDS_PER_YEAR,
        "enso": SECONDS_PER_YEAR,
        "eq": SECONDS_PER_YEAR,
        "ecg": 1.0,
    }
    nodes = []
    for key, system in data.items():
        factor = unit_seconds.get(key, 1.0)
        for sub in system.get("fits", {}).get("full_ladder", {}).get("subsystems", []):
            period_seconds = float(sub["period"]) * factor
            amp = abs(float(sub.get("amp", 0.0)))
            nodes.append(
                base_node(
                    node_id=f"measured_v3_{key}_r{sub.get('rung')}_{len(nodes)}",
                    name=f"{system.get('name', key)} rung {sub.get('rung')} c{sub.get('ctype')}",
                    system=f"measured_{key}",
                    system_label=f"Measured {system.get('name', key)}",
                    period_seconds=period_seconds,
                    ara=float(sub.get("ara")),
                    weight_value=max(amp, EPS),
                    weight_label="Fitted amplitude",
                    source="TheFormula/systems_map_v3_data.js",
                    layer="measured_fit",
                    notes="Fitted subsystem from map_systems_v3 full_ladder. Mapping-only diagnostic.",
                    extra={
                        "model_rung": sub.get("rung"),
                        "ctype": sub.get("ctype"),
                        "fit_corr": sub.get("corr"),
                        "fit_mae": sub.get("mae"),
                        "amp": sub.get("amp"),
                    },
                )
            )
    return nodes


def period_to_seconds(rung: dict) -> float | None:
    if "period_ms" in rung:
        return float(rung["period_ms"]) / 1000.0
    period = rung.get("period")
    unit = str(rung.get("period_unit", "")).lower()
    if period is None:
        return None
    p = float(period)
    if "month" in unit:
        return p * SECONDS_PER_MONTH
    if "year" in unit:
        return p * SECONDS_PER_YEAR
    if "day" in unit:
        return p * SECONDS_PER_DAY
    if "second" in unit or unit == "s":
        return p
    return None


def load_state_geometry_nodes():
    if not STATE_GEOMETRY.exists():
        return []
    data = js_assignment_to_json(STATE_GEOMETRY, "window.ARA_STATE_GEOMETRY =")
    nodes = []
    for sys_key, system in data.get("systems", {}).items():
        for subsystem in system.get("subsystems", []):
            sub_name = subsystem.get("name", "subsystem")
            for rung in subsystem.get("rungs", []):
                period_seconds = period_to_seconds(rung)
                if period_seconds is None:
                    continue
                label = rung.get("label", f"k{rung.get('k', '')}")
                amp = abs(float(rung.get("amp", 0.0)))
                energy = rung.get("energy")
                nodes.append(
                    base_node(
                        node_id=f"state_{sys_key}_{sub_name}_{label}",
                        name=f"{sys_key} {sub_name} {label}",
                        system=f"state_{sys_key}_{sub_name}",
                        system_label=f"{sys_key} {sub_name}",
                        period_seconds=period_seconds,
                        ara=float(rung.get("ara")),
                        weight_value=max(float(energy) if energy is not None else amp, EPS),
                        weight_label="State energy",
                        source="TheFormula/ara_state_geometry_data.js",
                        layer="state_geometry",
                        notes=f"{system.get('family', '')}; anchor-state rung.",
                        extra={
                            "system_key": sys_key,
                            "subsystem_name": sub_name,
                            "rung_label": label,
                            "rung_k": rung.get("k"),
                            "state": rung.get("state"),
                            "phase": rung.get("phase"),
                            "occupancy": rung.get("occupancy"),
                            "position": rung.get("position"),
                            "home_distance": rung.get("home_distance"),
                            "amp": rung.get("amp"),
                            "energy": rung.get("energy"),
                        },
                    )
                )
    return nodes


def candidate_relations(nodes):
    relations = []
    by_id = {n["id"]: n for n in nodes}

    def add_relation(kind, a, b, score, detail):
        if a["id"] == b["id"]:
            return
        relations.append(
            {
                "id": f"{kind}_{a['id']}_{b['id']}",
                "from": a["id"],
                "to": b["id"],
                "type": kind,
                "source": "derived_geometry_scan",
                "score": float(score),
                "detail": detail,
            }
        )

    finite_ara = [n for n in nodes if n.get("ara") is not None and math.isfinite(n["ara"])]
    same_rung = []
    vertical = []
    boundary_pairs = []
    for i, a in enumerate(finite_ara):
        for b in finite_ara[i + 1 :]:
            if a["system"] == b["system"]:
                continue
            rung_gap = abs(a["period_phi_rung"] - b["period_phi_rung"])
            ara_gap = abs(a["ara"] - b["ara"])
            if rung_gap <= 0.20 and ara_gap <= 0.16:
                score = 1.0 / (1.0 + 8.0 * rung_gap + 4.0 * ara_gap)
                same_rung.append((score, a, b, rung_gap, ara_gap))
            if rung_gap >= 6.0 and ara_gap <= 0.05:
                score = 1.0 / (1.0 + ara_gap * 20.0) * min(1.0, rung_gap / 20.0)
                vertical.append((score, a, b, rung_gap, ara_gap))
            ba = a.get("nearest_boundary", {})
            bb = b.get("nearest_boundary", {})
            if ba.get("name") == bb.get("name") and ba.get("distance") is not None and bb.get("distance") is not None:
                if max(ba["distance"], bb["distance"]) <= 0.035 and rung_gap >= 2.0:
                    score = 1.0 / (1.0 + ba["distance"] + bb["distance"])
                    boundary_pairs.append((score, a, b, rung_gap, ba["name"]))

    for score, a, b, rung_gap, ara_gap in sorted(same_rung, key=lambda x: -x[0])[:90]:
        add_relation(
            "same_rung_match",
            a,
            b,
            score,
            {"rung_gap": rung_gap, "ara_gap": ara_gap},
        )
    for score, a, b, rung_gap, ara_gap in sorted(vertical, key=lambda x: -x[0])[:90]:
        add_relation(
            "vertical_ara_match",
            a,
            b,
            score,
            {"rung_gap": rung_gap, "ara_gap": ara_gap},
        )
    for score, a, b, rung_gap, boundary in sorted(boundary_pairs, key=lambda x: -x[0])[:60]:
        add_relation(
            "boundary_match",
            a,
            b,
            score,
            {"rung_gap": rung_gap, "boundary": boundary},
        )
    return [r for r in relations if r["from"] in by_id and r["to"] in by_id]


def measured_root(system: str) -> str | None:
    if not system.startswith("measured_"):
        return None
    return system.replace("measured_", "", 1)


def state_root(system: str) -> str | None:
    if not system.startswith("state_"):
        return None
    parts = system.split("_")
    if len(parts) < 2:
        return None
    if parts[1] == "raw" and len(parts) >= 4:
        return parts[3]
    return parts[1]


def state_scale_key(node: dict) -> int:
    return int(round(node["period_phi_rung"] * 1000.0))


def candidate_triangles(nodes):
    """Find candidate triangle faces in the mapped geometry.

    A triangle candidate is not a same-node match. The first pass finds:

        fitted low-ARA pressure/event node
        + strongest two named state-rung sides at nearby scale

    The second pass finds:

        K2 endpoint + K3 bridge/gate + K4 endpoint

    This is meant for visual diagnosis of boundary/gate geometry.
    """
    state_nodes = [
        n for n in nodes
        if n.get("layer") == "state_geometry"
        and n.get("ara") is not None
        and math.isfinite(n["ara"])
    ]
    state_by_root_and_scale = {}
    for n in state_nodes:
        root = state_root(n["system"])
        if not root:
            continue
        state_by_root_and_scale.setdefault(root, {}).setdefault(state_scale_key(n), []).append(n)

    triangles = []
    measured = [
        n for n in nodes
        if n.get("layer") == "measured_fit"
        and n.get("ara") is not None
        and math.isfinite(n["ara"])
        and n["ara"] <= 0.35
    ]
    for fit in measured:
        root = measured_root(fit["system"])
        groups = state_by_root_and_scale.get(root, {})
        if not groups:
            continue
        candidates = []
        for scale, group in groups.items():
            if len(group) < 2:
                continue
            center = sum(n["period_phi_rung"] for n in group) / len(group)
            rung_gap = abs(fit["period_phi_rung"] - center)
            if rung_gap > 0.75:
                continue
            strongest = sorted(
                group,
                key=lambda n: abs(float(n.get("weight_value", 0.0))),
                reverse=True,
            )[:2]
            mean_ara = sum(n["ara"] for n in strongest) / len(strongest)
            ara_contrast = abs(mean_ara - fit["ara"])
            period_score = max(0.0, 1.0 - rung_gap / 0.75)
            contrast_score = min(1.0, ara_contrast / 1.2)
            score = 0.68 * period_score + 0.32 * contrast_score
            candidates.append((score, rung_gap, ara_contrast, strongest, center))
        if not candidates:
            continue
        score, rung_gap, ara_contrast, strongest, center = max(candidates, key=lambda x: x[0])
        triangle_nodes = [fit["id"]] + [n["id"] for n in strongest]
        label = " / ".join([fit["name"]] + [n["name"] for n in strongest])
        triangles.append(
            {
                "id": f"triangle_{fit['id']}_{strongest[0]['id']}_{strongest[1]['id']}",
                "nodes": triangle_nodes,
                "type": "low_ara_state_face",
                "source": "derived_geometry_scan",
                "score": float(score),
                "label": fix_text(label),
                "detail": {
                    "root": root,
                    "fit_node": fit["id"],
                    "state_nodes": [n["id"] for n in strongest],
                    "period_phi_rung_gap": float(rung_gap),
                    "state_scale_center": float(center),
                    "ara_contrast": float(ara_contrast),
                    "interpretation": "Low-ARA fitted event node sits on the same period band as a named state-rung face.",
                },
            }
        )

    by_state_subsystem = {}
    for n in state_nodes:
        k = n.get("rung_k")
        if k is None:
            continue
        try:
            k_int = int(k)
        except (TypeError, ValueError):
            continue
        by_state_subsystem.setdefault(n["system"], {})[k_int] = n

    for system_id, by_k in by_state_subsystem.items():
        if not all(k in by_k for k in (2, 3, 4)):
            continue
        left = by_k[2]
        bridge = by_k[3]
        right = by_k[4]
        period_mid = (left["period_phi_rung"] + right["period_phi_rung"]) / 2.0
        ara_mid = (left["ara"] + right["ara"]) / 2.0
        period_bridge_error = abs(bridge["period_phi_rung"] - period_mid)
        ara_bridge_error = abs(bridge["ara"] - ara_mid)
        phase_left = left.get("phase")
        phase_bridge = bridge.get("phase")
        phase_right = right.get("phase")
        phase_mid_error = None
        if (
            phase_left is not None
            and phase_bridge is not None
            and phase_right is not None
            and math.isfinite(float(phase_left))
            and math.isfinite(float(phase_bridge))
            and math.isfinite(float(phase_right))
        ):
            phase_mid = (float(phase_left) + float(phase_right)) / 2.0
            phase_mid_error = abs(float(phase_bridge) - phase_mid)
        score = 1.0 / (1.0 + 3.0 * period_bridge_error + 2.0 * ara_bridge_error)
        label = f"{left['system_label']} k2 / k3 bridge / k4"
        triangles.append(
            {
                "id": f"triangle_bridge_{left['id']}_{bridge['id']}_{right['id']}",
                "nodes": [left["id"], bridge["id"], right["id"]],
                "type": "state_bridge_face",
                "source": "derived_geometry_scan",
                "score": float(score),
                "label": fix_text(label),
                "detail": {
                    "root": state_root(system_id),
                    "subsystem": bridge.get("subsystem_name"),
                    "end_nodes": [left["id"], right["id"]],
                    "bridge_node": bridge["id"],
                    "period_bridge_error": float(period_bridge_error),
                    "ara_bridge_error": float(ara_bridge_error),
                    "phase_mid_error": float(phase_mid_error) if phase_mid_error is not None else None,
                    "interpretation": "K3 sits as the bridge/gate between the K2 and K4 endpoint rungs.",
                },
            }
        )
    return sorted(triangles, key=lambda t: -t["score"])


def summarize(nodes, relations, triangles):
    def counts(key):
        out = {}
        for n in nodes:
            out[n.get(key, "unknown")] = out.get(n.get(key, "unknown"), 0) + 1
        return dict(sorted(out.items()))

    return {
        "node_count": len(nodes),
        "relation_count": len(relations),
        "triangle_count": len(triangles),
        "layers": counts("layer"),
        "ara_classes": counts("ara_class"),
        "scale_domains": counts("scale_domain"),
        "ara_position_statuses": counts("ara_position_status"),
        "systems": counts("system"),
        "period_phi_rung_range": [
            min(n["period_phi_rung"] for n in nodes),
            max(n["period_phi_rung"] for n in nodes),
        ],
        "ara_range": [
            min(n["ara"] for n in nodes if n.get("ara") is not None),
            max(n["ara"] for n in nodes if n.get("ara") is not None),
        ],
    }


def main():
    catalog_nodes, catalog_relations = load_original_catalogue()
    measured_nodes = load_systems_v3_nodes()
    state_nodes = load_state_geometry_nodes()
    nodes = catalog_nodes + measured_nodes + state_nodes
    relations = catalog_relations + candidate_relations(nodes)
    triangles = candidate_triangles(nodes)
    payload = {
        "date": "2026-05-24",
        "purpose": "Mapping-first ARA temporal coordinate atlas. No prediction scores are produced here.",
        "phi": PHI,
        "ara_boundaries": ARA_BOUNDARIES,
        "sources": [
            str(OLD_HTML.relative_to(ROOT)),
            str(SYSTEMS_V3.relative_to(ROOT)) if SYSTEMS_V3.exists() else None,
            str(STATE_GEOMETRY.relative_to(ROOT)) if STATE_GEOMETRY.exists() else None,
        ],
        "summary": summarize(nodes, relations, triangles),
        "nodes": nodes,
        "relations": relations,
        "triangles": triangles,
    }
    payload["sources"] = [s for s in payload["sources"] if s]
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_MAPPING_ATLAS = " + json.dumps(payload, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"nodes={len(nodes)} relations={len(relations)} triangles={len(triangles)}")
    print(f"saved {OUT_JSON}")
    print(f"saved {OUT_JS}")


if __name__ == "__main__":
    main()

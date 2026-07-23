"""Independent checks for the ARA cosmic-to-quantum physics ladder."""

from __future__ import annotations

import json
import math
import random
from pathlib import Path


HERE = Path(__file__).resolve().parent


def check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}


def main() -> None:
    artifact = json.loads(
        (HERE / "ARA_PHYSICS_COSMIC_QUANTUM_REPORT_ARTIFACT.json").read_text(
            encoding="utf-8"
        )
    )
    datasets = artifact["snapshot"]["datasets"]
    law_rows = datasets["law_ladder"]
    landmarks = datasets["ara_landmarks"]
    traversal = datasets["traversal_path"]
    continuity = datasets["continuity_spine"]
    virial = datasets["virial_scale"]

    checks: list[dict] = []

    required_laws = {
        "Einstein",
        "Newton",
        "Hamilton",
        "Noether",
        "Virial",
        "Gauss electric",
        "Gauss magnetic",
        "Faraday",
        "Ampere-Maxwell",
        "Poynting",
        "Lorentz",
        "Schrodinger",
        "Quantum hydrogen",
    }
    joined_laws = " | ".join(row["law"] for row in law_rows)
    missing = sorted(name for name in required_laws if name not in joined_laws)
    checks.append(
        check(
            "all requested laws are present",
            not missing,
            f"missing={missing or 'none'}",
        )
    )

    crosswalk_table = next(
        table
        for table in artifact["manifest"]["tables"]
        if table["id"] == "two-column-law-crosswalk"
    )
    checks.append(
        check(
            "main crosswalk has exactly two visible columns",
            len(crosswalk_table["columns"]) == 2,
            f"columns={len(crosswalk_table['columns'])}",
        )
    )

    edge_classes = {row["edge_class"] for row in traversal}
    required_edges = {
        "exact limit",
        "exact reformulation",
        "exact theorem consequence",
        "sibling bridge, not derivation",
        "exact conservation consequence",
        "quantisation/model transition",
    }
    checks.append(
        check(
            "scientifically different bridge classes are explicit",
            required_edges.issubset(edge_classes),
            f"edge_classes={sorted(edge_classes)}",
        )
    )

    no_direct_claim = (
        "no direct GR-to-quantum derivation"
        in json.loads(
            (HERE / "ARA_PHYSICS_COSMIC_QUANTUM_LADDER_RESULTS.json").read_text(
                encoding="utf-8"
            )
        )["interpretation"]
    )
    checks.append(
        check(
            "GR-to-quantum direct derivation is explicitly fenced",
            no_direct_claim,
            "typed reconstruction, not one derivation",
        )
    )

    all_rows_typed = all(
        row["map_type"] and row["status"] and row["bridge_role"] for row in law_rows
    )
    checks.append(
        check(
            "every law row has transformation and evidence metadata",
            all_rows_typed,
            f"rows={len(law_rows)}",
        )
    )

    landmark_laws = {row["law"] for row in landmarks}
    checks.append(
        check(
            "ARA landmark diagram contains classical, field and quantum appearances",
            {
                "Newton force axis",
                "Faraday induction",
                "Quantum Bloch diameter",
                "Quantum hydrogen virial",
            }.issubset(landmark_laws),
            f"landmark_rows={len(landmarks)}",
        )
    )

    rng = random.Random(20260723)
    max_force_error = 0.0
    max_gauss_error = 0.0
    max_poynting_error = 0.0
    max_hamilton_error = 0.0
    max_bloch_error = 0.0

    for _ in range(10_000):
        a = 10 ** rng.uniform(-12, 12)
        b = 10 ** rng.uniform(-12, 12)
        total = a + b

        x_force = 2 * b / total
        force_reconstructed = total * (x_force - 1)
        max_force_error = max(max_force_error, abs(force_reconstructed - (b - a)) / total)

        q_minus = a
        q_plus = b
        x_charge = 2 * q_plus / (q_plus + q_minus)
        charge_reconstructed = (q_plus + q_minus) * (x_charge - 1)
        max_gauss_error = max(
            max_gauss_error,
            abs(charge_reconstructed - (q_plus - q_minus)) / total,
        )

        p_in = a
        p_out = b
        x_p = 2 * p_out / (p_in + p_out)
        du = (p_in + p_out) * (1 - x_p)
        max_poynting_error = max(
            max_poynting_error,
            abs(du - (p_in - p_out)) / total,
        )

        v = a
        k = b
        h = v + k
        t_v = 2 * v / h
        t_k = 2 * k / h
        max_hamilton_error = max(max_hamilton_error, abs((t_v + t_k) - 2))

        p_b = rng.random()
        r_z = 1 - 2 * p_b
        x_bloch = 2 * p_b
        max_bloch_error = max(max_bloch_error, abs(x_bloch - (1 - r_z)))

    checks.append(
        check(
            "Newton force ARA reconstructs signed resultant",
            max_force_error < 1e-12,
            f"max normalized error={max_force_error:.3e}",
        )
    )
    checks.append(
        check(
            "Gauss signed-pair ARA reconstructs net source",
            max_gauss_error < 1e-12,
            f"max normalized error={max_gauss_error:.3e}",
        )
    )
    checks.append(
        check(
            "Poynting input/output ARA reconstructs stored-energy change",
            max_poynting_error < 1e-12,
            f"max normalized error={max_poynting_error:.3e}",
        )
    )
    checks.append(
        check(
            "Hamilton allocations close to TE-ARA 2",
            max_hamilton_error < 1e-12,
            f"max absolute error={max_hamilton_error:.3e}",
        )
    )
    checks.append(
        check(
            "Bloch ARA equals the opposite-direction conventional coordinate",
            max_bloch_error < 1e-12,
            f"max absolute error={max_bloch_error:.3e}",
        )
    )

    checks.append(
        check(
            "virial sub-ladder remains at the weighted 1.0 ridge",
            all(abs(row["ara_coordinate"] - 1) < 1e-15 for row in virial),
            f"points={len(virial)}",
        )
    )

    span = max(row["log10_scale_m"] for row in virial) - min(
        row["log10_scale_m"] for row in virial
    )
    checks.append(
        check(
            "virial numerical thread spans more than 21 orders",
            span > 21,
            f"span={span:.12f}",
        )
    )

    required_continuity_domains = {
        "General relativity",
        "Electromagnetic charge",
        "Electromagnetic energy",
        "Quantum probability",
    }
    checks.append(
        check(
            "continuity spine crosses four physical domains",
            {row["domain"] for row in continuity} == required_continuity_domains,
            f"domains={sorted(row['domain'] for row in continuity)}",
        )
    )

    one_meanings = {row["ara_1"] for row in landmarks}
    checks.append(
        check(
            "the report does not flatten every 1.0 into one physical state",
            len(one_meanings) >= 10,
            f"distinct 1.0/relation meanings={len(one_meanings)}",
        )
    )

    result = {
        "status": "passed" if all(item["passed"] for item in checks) else "failed",
        "passed": sum(item["passed"] for item in checks),
        "total": len(checks),
        "max_force_normalized_error": max_force_error,
        "max_gauss_normalized_error": max_gauss_error,
        "max_poynting_normalized_error": max_poynting_error,
        "max_hamilton_closure_error": max_hamilton_error,
        "max_bloch_coordinate_error": max_bloch_error,
        "checks": checks,
    }

    (HERE / "ARA_PHYSICS_COSMIC_QUANTUM_LADDER_VALIDATION.json").write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))

    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

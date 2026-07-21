"""Independent brute-force validation of PN23 without modular inverses."""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "PN23_ANTI_PAIR_FRACTAL_LIFT_RESULTS.json"
OUTPUT = HERE / "PN23_ANTI_PAIR_FRACTAL_LIFT_VALIDATION.json"


def direct_units(modulus: int) -> list[int]:
    return [value for value in range(1, modulus) if math.gcd(value, modulus) == 1]


def lower_half(units: list[int], modulus: int) -> list[int]:
    return [value for value in units if value < modulus - value]


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT.name}")
    saved = json.loads(RESULTS.read_text(encoding="utf-8"))
    modulus = saved["starting_state"]["modulus"]
    checks: list[dict] = []
    rung_validation: list[dict] = []

    for saved_rung in saved["rungs"]:
        gate = saved_rung["gate"]
        phase = saved_rung["phase"]
        parent_units = direct_units(modulus)
        parents = lower_half(parent_units, modulus)
        new_modulus = modulus * gate
        reconstructed_children: set[int] = set()
        collision_pairs: list[tuple[int, int, int]] = []
        unique_collision_failures = 0

        for representative in parents:
            opposite = modulus - representative
            killed_a = [
                copy for copy in range(gate)
                if (representative + copy * modulus) % gate == 0
            ]
            killed_b = [
                copy for copy in range(gate)
                if (opposite + copy * modulus) % gate == 0
            ]
            if len(killed_a) != 1 or len(killed_b) != 1:
                unique_collision_failures += 1
                continue
            collision_pairs.append((representative, killed_a[0], killed_b[0]))
            for copy in range(gate):
                if copy == killed_a[0]:
                    continue
                survivor = representative + copy * modulus
                reconstructed_children.add(min(survivor, new_modulus - survivor))

        direct_children = direct_units(new_modulus)
        direct_child_representatives = lower_half(direct_children, new_modulus)
        reconstructed_list = sorted(reconstructed_children)
        integer_ridge_failures = sum(
            killed_a + killed_b != gate - 1
            for _, killed_a, killed_b in collision_pairs
        )
        direct_ridge_count = sum(
            killed_a == killed_b
            for _, killed_a, killed_b in collision_pairs
        )
        local_checks = {
            "parent_representatives_match_saved_count": len(parents) == saved_rung["parent_pair_count"],
            "unique_collisions": unique_collision_failures == 0,
            "anti_collision_sum_exact": integer_ridge_failures == 0,
            "A_only_reconstruction_matches_direct_lower_half": reconstructed_list == direct_child_representatives,
            "reconstructed_full_count_matches_direct": 2 * len(reconstructed_list) == len(direct_children),
            "child_pair_count_matches_saved": len(reconstructed_list) == saved_rung["child_pair_count"],
            "direct_ridge_count_matches_saved": direct_ridge_count == saved_rung["direct_ridge_count"],
            "new_modulus_matches_saved": new_modulus == saved_rung["new_modulus"],
        }
        for name, passed in local_checks.items():
            checks.append({
                "rung": f"{modulus}x{gate}->{new_modulus}",
                "phase": phase,
                "check": name,
                "pass": bool(passed),
            })
        rung_validation.append({
            "phase": phase,
            "parent_modulus": modulus,
            "gate": gate,
            "new_modulus": new_modulus,
            "parent_pair_count": len(parents),
            "child_pair_count": len(reconstructed_list),
            "direct_residue_count": len(direct_children),
            "unique_collision_failures": unique_collision_failures,
            "integer_ridge_failures": integer_ridge_failures,
            "direct_ridge_count": direct_ridge_count,
            "missing_representatives": sorted(set(direct_child_representatives) - reconstructed_children)[:20],
            "extra_representatives": sorted(reconstructed_children - set(direct_child_representatives))[:20],
            "pass": all(local_checks.values()),
        })
        modulus = new_modulus

    passed = sum(check["pass"] for check in checks)
    payload = {
        "validation_id": "PN23/ANTI-PAIR-FRACTAL-LIFT/INDEPENDENT-BRUTE-FORCE/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if passed == len(checks) else "FAIL",
        "method": (
            "Re-enumerate every wheel residue by gcd, locate killed copies by direct trial rather than modular inverse, "
            "and reconstruct each next lower-half state using only surviving A-side copies."
        ),
        "checks_passed": passed,
        "checks_total": len(checks),
        "rungs": rung_validation,
        "checks": checks,
        "claim_assessment": {
            "lossless_recursive_pair_compression": all(row["pass"] for row in rung_validation),
            "held_out_rung_pass": rung_validation[-1]["phase"] == "held_out" and rung_validation[-1]["pass"],
            "prime_locator": "not tested and not implied",
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "checks": f"{passed}/{len(checks)}",
        "rungs": rung_validation,
    }, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

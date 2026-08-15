from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = (
    HERE
    / "T393_joint_neutrino_pair_projection"
    / "T393_RESULTS.json"
)


def primitive_weight(z: float) -> float:
    return z * z / 2.0 - z**3 / 3.0


def primitive_first(z: float) -> float:
    return z**3 / 3.0 - z**4 / 4.0


def main() -> None:
    payload = json.loads(RESULTS.read_text(encoding="utf-8"))
    star = payload["at_frozen_handover"]
    gates = payload["gates"]
    x_e = payload["frozen_t392"]["x_e_star"]
    lower = 1.0 - x_e
    norm = primitive_weight(1.0) - primitive_weight(lower)
    independently_recomputed_nu_e = (
        primitive_first(1.0) - primitive_first(lower)
    ) / norm
    independently_recomputed_anti_nu_mu = (
        2.0 - x_e - independently_recomputed_nu_e
    )

    checks = {
        "three_distinct_decay_children": (
            star["charged_parent"] > 0
            and star["nu_e_parent"] > 0
            and star["anti_nu_mu_parent"] > 0
        ),
        "parent_energy_closure": abs(
            star["charged_parent"]
            + star["nu_e_parent"]
            + star["anti_nu_mu_parent"]
            - 1.0
        )
        < 1e-12,
        "neutral_internal_closure": abs(
            star["nu_e_internal_ara"]
            + star["anti_nu_mu_internal_ara"]
            - 2.0
        )
        < 1e-12,
        "analytic_nu_e_mean_recomputed": abs(
            star["mean_nu_e_child"] - independently_recomputed_nu_e
        )
        < 1e-12,
        "analytic_anti_nu_mu_mean_recomputed": abs(
            star["mean_anti_nu_mu_child"]
            - independently_recomputed_anti_nu_mu
        )
        < 1e-12,
        "forced_closure_label_present": (
            gates["G3_parent_energy_closure_bookkeeping"]["evidential_weight"]
            == "none; forced by energy conservation"
        ),
        "nontrivial_gates_pass": all(
            gates[key]["pass"]
            for key in (
                "G1_approx_charged_quarter",
                "G4_distinct_neutral_siblings",
                "G5_directional_neutral_ordering",
                "G6_control_separation",
                "G7_monte_carlo_reproduction",
            )
        ),
        "exact_landmark_gate_fails_honestly": not gates[
            "G2_exact_half_inside_t392_interval"
        ]["pass"],
        "individual_timing_not_claimed": "does not" in payload[
            "claim_boundary"
        ].lower(),
    }
    passed = all(checks.values())
    output = {"passed": passed, "checks": checks}
    out_path = RESULTS.with_name("T393_VALIDATION.json")
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()

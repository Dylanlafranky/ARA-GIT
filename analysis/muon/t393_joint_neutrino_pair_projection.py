from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
OUT = HERE / "T393_joint_neutrino_pair_projection"
OUT.mkdir(exist_ok=True)

X_STAR = 0.49019
X_LOW = 0.48612
X_HIGH = 0.49446
SEED = 393
N_ACCEPTED = 400_000


def primitive_weight(z: float | np.ndarray) -> float | np.ndarray:
    """Integral primitive for z(1-z)."""
    return z * z / 2.0 - z * z * z / 3.0


def primitive_first(z: float | np.ndarray) -> float | np.ndarray:
    """Integral primitive for z*z(1-z)."""
    return z**3 / 3.0 - z**4 / 4.0


def primitive_second(z: float | np.ndarray) -> float | np.ndarray:
    """Integral primitive for z*z*z(1-z)."""
    return z**4 / 4.0 - z**5 / 5.0


def conditional_metrics(x_e: float) -> dict[str, float]:
    """Analytic V-A metrics at fixed charged-daughter energy coordinate."""
    lower = 1.0 - x_e
    pair_total = 2.0 - x_e
    norm = float(primitive_weight(1.0) - primitive_weight(lower))
    mean_nue = float((primitive_first(1.0) - primitive_first(lower)) / norm)
    second_nue = float((primitive_second(1.0) - primitive_second(lower)) / norm)
    mean_anti_numu = pair_total - mean_nue
    pair_midpoint = pair_total / 2.0
    probability_anti_numu_heavier = float(
        (primitive_weight(pair_midpoint) - primitive_weight(lower)) / norm
    )
    return {
        "x_e": x_e,
        "pair_total_child": pair_total,
        "mean_nu_e_child": mean_nue,
        "mean_anti_nu_mu_child": mean_anti_numu,
        "sd_nu_e_child": math.sqrt(max(0.0, second_nue - mean_nue**2)),
        "charged_parent": x_e / 2.0,
        "nu_e_parent": mean_nue / 2.0,
        "anti_nu_mu_parent": mean_anti_numu / 2.0,
        "joint_neutral_parent": pair_total / 2.0,
        "pair_mass_coordinate_child": 1.0 - x_e,
        "pair_mass_coordinate_parent": (1.0 - x_e) / 2.0,
        "nu_e_internal_ara": 2.0 * mean_nue / pair_total,
        "anti_nu_mu_internal_ara": 2.0 * mean_anti_numu / pair_total,
        "probability_anti_nu_mu_heavier": probability_anti_numu_heavier,
    }


def sample_conditional(x_e: float, n: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Fixed-seed rejection sample from z(1-z) on [1-x_e, 1]."""
    rng = np.random.default_rng(seed)
    lower = 1.0 - x_e
    accepted: list[np.ndarray] = []
    count = 0
    while count < n:
        batch_n = max(10_000, int((n - count) * 3.0))
        z = rng.uniform(lower, 1.0, batch_n)
        keep = rng.random(batch_n) < (z * (1.0 - z) / 0.25)
        chunk = z[keep]
        accepted.append(chunk)
        count += len(chunk)
    nu_e = np.concatenate(accepted)[:n]
    anti_nu_mu = (2.0 - x_e) - nu_e
    return nu_e, anti_nu_mu


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    star = conditional_metrics(X_STAR)
    low = conditional_metrics(X_LOW)
    high = conditional_metrics(X_HIGH)
    exact = conditional_metrics(0.5)

    nu_e_mc, anti_nu_mu_mc = sample_conditional(X_STAR, N_ACCEPTED, SEED)
    mc = {
        "seed": SEED,
        "n_accepted": N_ACCEPTED,
        "mean_nu_e_child": float(nu_e_mc.mean()),
        "mean_anti_nu_mu_child": float(anti_nu_mu_mc.mean()),
        "probability_anti_nu_mu_heavier": float(np.mean(anti_nu_mu_mc > nu_e_mc)),
    }

    parent_closure = (
        star["charged_parent"]
        + star["nu_e_parent"]
        + star["anti_nu_mu_parent"]
    )
    mean_gap_parent = star["anti_nu_mu_parent"] - star["nu_e_parent"]
    exact_interval_pass = X_LOW <= 0.5 <= X_HIGH
    gates = {
        "G1_approx_charged_quarter": {
            "pass": abs(star["charged_parent"] - 0.25) <= 0.01,
            "value": star["charged_parent"],
            "target": 0.25,
            "tolerance": 0.01,
        },
        "G2_exact_half_inside_t392_interval": {
            "pass": exact_interval_pass,
            "interval": [X_LOW, X_HIGH],
            "target": 0.5,
        },
        "G3_parent_energy_closure_bookkeeping": {
            "pass": abs(parent_closure - 1.0) < 1e-12,
            "value": parent_closure,
            "residual": parent_closure - 1.0,
            "evidential_weight": "none; forced by energy conservation",
        },
        "G4_distinct_neutral_siblings": {
            "pass": mean_gap_parent > 0.05,
            "value": mean_gap_parent,
            "threshold": 0.05,
        },
        "G5_directional_neutral_ordering": {
            "pass": star["probability_anti_nu_mu_heavier"] > 0.60,
            "value": star["probability_anti_nu_mu_heavier"],
            "threshold": 0.60,
        },
        "G6_control_separation": {
            "pass": abs(star["nu_e_internal_ara"] - 1.0) > 0.05,
            "v_minus_a": [
                star["nu_e_internal_ara"],
                star["anti_nu_mu_internal_ara"],
            ],
            "identity_shuffled_control": [1.0, 1.0],
        },
        "G7_monte_carlo_reproduction": {
            "pass": (
                abs(mc["mean_nu_e_child"] - star["mean_nu_e_child"]) < 0.0015
                and abs(
                    mc["mean_anti_nu_mu_child"]
                    - star["mean_anti_nu_mu_child"]
                )
                < 0.0015
            ),
            "nu_e_abs_error": abs(mc["mean_nu_e_child"] - star["mean_nu_e_child"]),
            "anti_nu_mu_abs_error": abs(
                mc["mean_anti_nu_mu_child"] - star["mean_anti_nu_mu_child"]
            ),
            "tolerance": 0.0015,
        },
    }

    curve_rows: list[dict[str, object]] = []
    for x_e in np.linspace(0.05, 0.95, 181):
        m = conditional_metrics(float(x_e))
        curve_rows.append(
            {
                "x_e_child": m["x_e"],
                "charged_parent": m["charged_parent"],
                "joint_neutral_parent": m["joint_neutral_parent"],
                "nu_e_parent_mean": m["nu_e_parent"],
                "anti_nu_mu_parent_mean": m["anti_nu_mu_parent"],
                "pair_mass_parent": m["pair_mass_coordinate_parent"],
                "nu_e_internal_ara": m["nu_e_internal_ara"],
                "anti_nu_mu_internal_ara": m["anti_nu_mu_internal_ara"],
                "probability_anti_nu_mu_heavier": m[
                    "probability_anti_nu_mu_heavier"
                ],
            }
        )

    component_rows = [
        {
            "component": "charged daughter e+",
            "child_coordinate_or_mean": star["x_e"],
            "parent_energy_share": star["charged_parent"],
            "internal_neutral_ara": "",
            "role": "charged child",
        },
        {
            "component": "electron neutrino nu_e",
            "child_coordinate_or_mean": star["mean_nu_e_child"],
            "parent_energy_share": star["nu_e_parent"],
            "internal_neutral_ara": star["nu_e_internal_ara"],
            "role": "neutral child 1",
        },
        {
            "component": "anti-muon neutrino anti_nu_mu",
            "child_coordinate_or_mean": star["mean_anti_nu_mu_child"],
            "parent_energy_share": star["anti_nu_mu_parent"],
            "internal_neutral_ara": star["anti_nu_mu_internal_ara"],
            "role": "neutral child 2",
        },
        {
            "component": "joint neutrino pair",
            "child_coordinate_or_mean": star["pair_total_child"],
            "parent_energy_share": star["joint_neutral_parent"],
            "internal_neutral_ara": 2.0,
            "role": "paired neutral branch",
        },
    ]

    summary = {
        "test_id": "T393",
        "status": "KINEMATIC_CROSSWALK_SUPPORTED_EXACT_LANDMARK_NOT_IN_T392_INTERVAL",
        "claim_boundary": (
            "Tests the three-child decay decomposition and rung projection; does not "
            "predict an individual muon's decay time."
        ),
        "frozen_t392": {
            "x_e_star": X_STAR,
            "interval": [X_LOW, X_HIGH],
            "distance_to_exact_half_child": X_STAR - 0.5,
            "distance_to_exact_quarter_parent": star["charged_parent"] - 0.25,
        },
        "at_frozen_handover": star,
        "at_exact_half": exact,
        "interval_endpoints": {"low": low, "high": high},
        "monte_carlo": mc,
        "gates": gates,
        "interpretation": {
            "forced": [
                "three-child energy sum equals 2",
                "parent energy shares sum to 1",
                "joint neutral momentum is opposite the charged daughter in the muon rest frame",
            ],
            "informative": [
                "the T392 directional reversal is within 0.01 parent units of the quarter landmark",
                "V-A gives two distinct neutral-child means rather than a duplicated joint packet",
                "the muon-flavour neutral child is heavier in about 69% of handover-slice decays",
            ],
            "not_supported": [
                "the exact 0.5 child landmark lies inside the digitised T392 interval",
                "0.25 is an individual-muon pre-decay clock",
            ],
        },
        "sources": [
            "https://pdg.lbl.gov/2025/reviews/rpp2025-rev-muon-decay-params.pdf",
            "https://arxiv.org/abs/1010.4998",
        ],
    }

    write_csv(OUT / "T393_COMPONENTS.csv", component_rows)
    write_csv(OUT / "T393_CURVE.csv", curve_rows)
    (OUT / "T393_RESULTS.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()


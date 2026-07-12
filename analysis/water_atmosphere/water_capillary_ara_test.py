#!/usr/bin/env python3
"""Frozen analysis for ARA water/liquid capillary-gravity test v0.1.

Input CSV columns:
    fluid_id,k_m_inv,omega_rad_s,rho_liquid_kg_m3,rho_gas_kg_m3,
    gamma_N_m,dynamic_viscosity_Pa_s,depth_m,temperature_C

The script does not fit or move the ARA center. It estimates group velocity from
measured omega(k), evaluates the fixed prediction, and writes a complete
per-point table plus summary JSON.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


G = 9.80665
REQUIRED = {
    "fluid_id",
    "k_m_inv",
    "omega_rad_s",
    "rho_liquid_kg_m3",
    "rho_gas_kg_m3",
    "gamma_N_m",
    "dynamic_viscosity_Pa_s",
    "depth_m",
    "temperature_C",
}


def validate(df: pd.DataFrame) -> None:
    missing = REQUIRED.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df[list(REQUIRED - {"fluid_id"})].isna().any().any():
        raise ValueError("Required numeric columns contain missing values")
    if (df["k_m_inv"] <= 0).any() or (df["omega_rad_s"] <= 0).any():
        raise ValueError("k and omega must be positive")
    if (df["rho_liquid_kg_m3"] <= df["rho_gas_kg_m3"]).any():
        raise ValueError("This protocol requires liquid density > gas density")
    if (df["gamma_N_m"] <= 0).any():
        raise ValueError("Surface tension must be positive")
    if (df["dynamic_viscosity_Pa_s"] <= 0).any():
        raise ValueError("Dynamic viscosity must be positive")
    if (df["k_m_inv"] * df["depth_m"] < 3.0).any():
        raise ValueError("Frozen deep-water eligibility rule requires k*depth >= 3")
    nu = df["dynamic_viscosity_Pa_s"] / df["rho_liquid_kg_m3"]
    damping_ratio = 2.0 * nu * df["k_m_inv"] ** 2 / df["omega_rad_s"]
    if (damping_ratio > 0.10).any():
        raise ValueError(
            "Frozen weak-damping rule requires 2*nu*k^2/omega <= 0.10"
        )


def analyze_group(group: pd.DataFrame) -> pd.DataFrame:
    g = group.sort_values("k_m_inv").copy()
    k = g["k_m_inv"].to_numpy(float)
    omega = g["omega_rad_s"].to_numpy(float)
    delta_rho = (
        g["rho_liquid_kg_m3"].to_numpy(float)
        - g["rho_gas_kg_m3"].to_numpy(float)
    )
    gamma = g["gamma_N_m"].to_numpy(float)
    nu = (
        g["dynamic_viscosity_Pa_s"].to_numpy(float)
        / g["rho_liquid_kg_m3"].to_numpy(float)
    )

    # Independently calculated competition coordinate. No fitted center/width.
    q = gamma * k**2 / (delta_rho * G)
    x_ara = 2.0 * q / (1.0 + q)

    phase_speed = omega / k
    group_speed = np.gradient(omega, k, edge_order=2)
    observed_ratio = group_speed / phase_speed
    predicted_ratio = 0.5 + 0.5 * x_ara

    # Full inviscid, deep-water mechanics. This is an equivalence benchmark,
    # not an independent ARA competitor.
    rho_sum = (
        g["rho_liquid_kg_m3"].to_numpy(float)
        + g["rho_gas_kg_m3"].to_numpy(float)
    )
    omega_theory = np.sqrt((delta_rho * G * k + gamma * k**3) / rho_sum)

    g["q_capillary_over_gravity"] = q
    g["ara_x_0_2"] = x_ara
    g["kh"] = k * g["depth_m"].to_numpy(float)
    g["weak_damping_ratio"] = 2.0 * nu * k**2 / omega
    g["phase_speed_m_s"] = phase_speed
    g["group_speed_m_s"] = group_speed
    g["observed_cg_over_cp"] = observed_ratio
    g["ara_predicted_cg_over_cp"] = predicted_ratio
    g["abs_error_ratio"] = np.abs(observed_ratio - predicted_ratio)
    g["omega_full_mechanics_rad_s"] = omega_theory
    g["abs_error_omega_full_mechanics"] = np.abs(omega - omega_theory)
    return g


def crossing_q(group: pd.DataFrame) -> float | None:
    g = group.sort_values("q_capillary_over_gravity")
    q = g["q_capillary_over_gravity"].to_numpy(float)
    y = g["observed_cg_over_cp"].to_numpy(float) - 1.0
    changes = np.where(np.signbit(y[:-1]) != np.signbit(y[1:]))[0]
    if changes.size == 0:
        return None
    i = int(changes[np.argmin(np.abs(np.log(q[changes])))])
    # Linear interpolation in log(q), because the competition is multiplicative.
    lq0, lq1 = np.log(q[i]), np.log(q[i + 1])
    if y[i + 1] == y[i]:
        return float(np.exp((lq0 + lq1) / 2.0))
    fraction = -y[i] / (y[i + 1] - y[i])
    return float(np.exp(lq0 + fraction * (lq1 - lq0)))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("water_ara_results"))
    args = parser.parse_args()

    raw = pd.read_csv(args.input_csv)
    validate(raw)

    counts = raw.groupby("fluid_id").size()
    if (counts < 20).any():
        too_short = counts[counts < 20].to_dict()
        raise ValueError(f"Protocol requires >=20 points per fluid: {too_short}")

    analyzed = pd.concat(
        [analyze_group(group) for _, group in raw.groupby("fluid_id", sort=False)],
        ignore_index=True,
    )

    per_fluid = []
    for fluid_id, group in analyzed.groupby("fluid_id", sort=False):
        q_min = float(group["q_capillary_over_gravity"].min())
        q_max = float(group["q_capillary_over_gravity"].max())
        if not (q_min < 1.0 < q_max):
            raise ValueError(f"{fluid_id!r} does not bracket the frozen q=1 crossing")
        cross = crossing_q(group)
        per_fluid.append(
            {
                "fluid_id": str(fluid_id),
                "n": int(len(group)),
                "mae_cg_over_cp": float(group["abs_error_ratio"].mean()),
                "rmse_cg_over_cp": float(
                    np.sqrt(
                        np.mean(
                            (
                                group["observed_cg_over_cp"]
                                - group["ara_predicted_cg_over_cp"]
                            )
                            ** 2
                        )
                    )
                ),
                "observed_crossing_q": cross,
                "crossing_in_frozen_interval": bool(
                    cross is not None and 0.67 <= cross <= 1.50
                ),
            }
        )

    pooled_mae = float(analyzed["abs_error_ratio"].mean())
    summary = {
        "protocol_version": "0.1",
        "n_fluids": int(analyzed["fluid_id"].nunique()),
        "n_points": int(len(analyzed)),
        "pooled_mae_cg_over_cp": pooled_mae,
        "frozen_mae_threshold": 0.10,
        "pooled_mae_pass": bool(pooled_mae <= 0.10),
        "per_fluid": per_fluid,
        "note": (
            "The fixed ARA ratio is algebraically equivalent to ideal "
            "capillary-gravity mechanics. Empirical success is a coordinate "
            "validation, not by itself a new-law result."
        ),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    analyzed.to_csv(args.output_dir / "water_ara_point_results.csv", index=False)
    with (args.output_dir / "water_ara_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

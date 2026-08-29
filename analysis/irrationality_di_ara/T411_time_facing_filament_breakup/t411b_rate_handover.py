"""T411B current-rate parent/residual handover instrument."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from scipy.stats import spearmanr

import t411_time_facing_filament_breakup as base


HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
PARAMS = HERE / "T411B_FROZEN_PARAMETERS.json"


def odd_window(n: int, target: int) -> int:
    cap = max(11, int(np.floor(0.31 * n)))
    if cap % 2 == 0:
        cap -= 1
    w = max(11, target)
    if w % 2 == 0:
        w += 1
    return min(w, cap)


def analyse_rate_run(group: pd.DataFrame, meta: pd.Series) -> tuple[pd.DataFrame, dict[str, object]]:
    reliable = group[np.isfinite(group.D_mm) & (group.D_px >= 5)].copy().sort_values("Time_s")
    if len(reliable) < 40:
        return pd.DataFrame(), {"Name": meta.Name, "excluded": True, "reason": "fewer_than_40_reliable_samples"}

    fluid = str(meta.Fluid)
    mu, rho, sigma = base.fluid_properties(fluid, float(meta.T_C))
    d0 = float(meta.D0_mm)
    h0 = d0 * float(meta.H0_D0)
    v = float(meta.v_mm_s)
    tbrk = float(meta.tbrk_s)
    t = reliable.Time_s.to_numpy(float)
    d_raw = reliable.D_mm.to_numpy(float)
    dt = float(np.median(np.diff(t)))
    r_cap = 2.0 * base.ALPHA * sigma / mu * 1000.0
    target_frames = int(np.ceil((2.0 / float(meta.px_per_mm)) / max(r_cap, 1e-12) / dt))
    window = odd_window(len(reliable), target_frames)
    d_smooth = savgol_filter(d_raw, window_length=window, polyorder=2, mode="interp")
    derivative = savgol_filter(d_raw, window_length=window, polyorder=2, deriv=1, delta=dt, mode="interp")
    r_obs = -derivative

    d_mech = d0 * np.power(1.0 + v * t / h0, -0.75)
    r_mech = 0.75 * (v / h0) * d0 * np.power(1.0 + v * t / h0, -1.75)
    r_i = r_obs - r_mech
    valid = (t / tbrk >= 0.05) & (r_mech >= 0) & (r_i >= 0) & (r_obs > 0)
    x = np.full(len(t), np.nan)
    x[valid] = 2.0 * r_i[valid] / r_obs[valid]
    u = t / tbrk
    cross_u = base.persistent_up_cross(u, x, persistence=5)
    finite = np.isfinite(x)
    rho_time = float(spearmanr(u[finite], x[finite]).statistic) if np.sum(finite) >= 5 else float("nan")

    d0_m = d0 / 1000.0
    d_obs_m = d_smooth / 1000.0
    h_m = (h0 + v * t) / 1000.0
    bo0 = rho * base.G * (d0_m / 2.0) ** 2 / sigma
    bo_local = rho * base.G * (d_obs_m / 2.0) ** 2 / sigma
    gh = rho * base.G * h_m * d_obs_m / (2.0 * sigma)
    if np.isfinite(cross_u):
        k = int(np.nanargmin(np.abs(u - cross_u)))
    else:
        k = -1

    reliable["D_smooth_mm"] = d_smooth
    reliable["u_breakup"] = u
    reliable["D_mechanical_mm"] = d_mech
    reliable["r_observed_mm_s"] = r_obs
    reliable["r_mechanical_mm_s"] = r_mech
    reliable["r_unresolved_mm_s"] = r_i
    reliable["x_rate_ara"] = x
    reliable["Bo_local"] = bo_local
    reliable["G_height_proxy"] = gh
    reliable["fluid"] = fluid
    reliable["D0_mm"] = d0
    reliable["tbrk_s"] = tbrk
    reliable["derivative_window_frames"] = window
    reliable["split"] = "development" if fluid in base.DEVELOPMENT_FLUIDS else "holdout"

    summary = {
        "Name": str(meta.Name),
        "fluid": fluid,
        "split": "development" if fluid in base.DEVELOPMENT_FLUIDS else "holdout",
        "D0_mm": d0,
        "v_mm_s": v,
        "H0_D0": float(meta.H0_D0),
        "tbrk_s": tbrk,
        "n_reliable": int(len(reliable)),
        "window_frames": int(window),
        "window_ms": float(window * dt * 1000.0),
        "unmeasured_tail_ms": float((tbrk - t[-1]) * 1000.0),
        "cross_u": cross_u,
        "cross_t_s": float(t[k]) if k >= 0 else float("nan"),
        "cross_D_mm": float(d_smooth[k]) if k >= 0 else float("nan"),
        "cross_r_mechanical": float(r_mech[k]) if k >= 0 else float("nan"),
        "cross_r_unresolved": float(r_i[k]) if k >= 0 else float("nan"),
        "rho_time_x": rho_time,
        "Bo0": float(bo0),
        "Bo_cross": float(bo_local[k]) if k >= 0 else float("nan"),
        "G_height_cross": float(gh[k]) if k >= 0 else float("nan"),
        "capillary_rate_mm_s": float(r_cap),
        "late_unresolved_to_capillary": float(np.nanmedian(r_i[u >= 0.70]) / r_cap) if np.any(u >= 0.70) else float("nan"),
        "excluded": False,
        "reason": "",
    }
    return reliable, summary


def shift_control(series: pd.DataFrame, summary: pd.DataFrame, seed: int, reps: int = 1000) -> dict[str, float]:
    observed = float(np.nanmedian(summary.rho_time_x))
    groups = [g.sort_values("Time_s") for _, g in series.groupby("Name")]
    rng = np.random.default_rng(seed)
    null = np.full(reps, np.nan)
    for rep in range(reps):
        vals = []
        for g in groups:
            rm = g.r_mechanical_mm_s.to_numpy(float)
            ri = g.r_unresolved_mm_s.to_numpy(float)
            u = g.u_breakup.to_numpy(float)
            shift = int(rng.integers(1, len(g)))
            ris = np.roll(ri, shift)
            total = rm + ris
            valid = (u >= 0.05) & (rm >= 0) & (ris >= 0) & (total > 0)
            if np.sum(valid) >= 5:
                vals.append(float(spearmanr(u[valid], 2.0 * ris[valid] / total[valid]).statistic))
        null[rep] = np.nanmedian(vals) if vals else np.nan
    null = null[np.isfinite(null)]
    return {
        "observed_median_rho": observed,
        "null_median": float(np.median(null)),
        "null_q95": float(np.quantile(null, 0.95)),
        "p_ge_observed": float((1 + np.sum(null >= observed)) / (1 + len(null))),
        "reps": int(len(null)),
    }


def plot(series: pd.DataFrame, summary: pd.DataFrame, mode: str) -> None:
    palette = {"S1": "#d95f02", "S2": "#1b9e77", "S3": "#7570b3", "S4": "#e7298a"}
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)
    examples = []
    for fluid in sorted(summary.fluid.unique()):
        g = summary[(summary.fluid == fluid) & summary.cross_u.notna()].sort_values("cross_u")
        if len(g):
            examples.append(str(g.iloc[len(g) // 2].Name))
    for name in examples:
        g = series[series.Name == name]
        axes[0, 0].plot(g.u_breakup, g.x_rate_ara, lw=1.8, label=f"{name} ({g.fluid.iloc[0]})")
    axes[0, 0].axhline(1, color="#222", ls="--", label="rate ridge x=1")
    axes[0, 0].axvline(1, color="#b2182b", ls=":", label="direct breakup u=1")
    axes[0, 0].set(xlabel="fraction of direct breakup time u=t/t_break", ylabel="current-rate ARA x_rate (0-2)", title="Child/movement ARA trajectories", xlim=(0, 1.02), ylim=(-0.03, 2.03))
    axes[0, 0].legend(fontsize=8)

    for fluid, g in summary.groupby("fluid"):
        axes[0, 1].scatter(g.Bo0, g.cross_u, s=38, alpha=0.75, color=palette[fluid], label=f"{fluid}, n={len(g)}")
    axes[0, 1].set(xlabel="initial local Bond number Bo0", ylabel="rate-ridge crossing u", title="Gravity rival")
    axes[0, 1].legend(fontsize=8)

    bins = np.linspace(0, 1, 21)
    for fluid, g in summary[summary.cross_u.notna()].groupby("fluid"):
        axes[1, 0].hist(g.cross_u, bins=bins, alpha=0.55, color=palette[fluid], label=fluid)
    axes[1, 0].set(xlabel="rate-ridge crossing u", ylabel="experiment count", title="Inferred handover distribution")
    axes[1, 0].legend()

    for fluid, g in summary.groupby("fluid"):
        axes[1, 1].scatter(g.capillary_rate_mm_s, g.late_unresolved_to_capillary * g.capillary_rate_mm_s, s=36, alpha=0.7, color=palette[fluid], label=fluid)
    lim = max(float(summary.capillary_rate_mm_s.max()), float((summary.late_unresolved_to_capillary * summary.capillary_rate_mm_s).max()))
    axes[1, 1].plot([0, lim], [0, lim], color="#222", ls="--", label="unresolved = capillary theory")
    axes[1, 1].set(xlabel="theoretical capillary rate (mm/s)", ylabel="median late unresolved rate (mm/s)", title="What is the unresolved rate?")
    axes[1, 1].legend(fontsize=8)
    fig.suptitle(f"T411B {mode}: current movement, not whole history", fontsize=16, fontweight="bold")
    fig.savefig(OUT / f"T411B_{mode.upper()}_OVERVIEW.png", dpi=180)
    plt.close(fig)


def run(mode: str) -> None:
    if mode == "holdout" and not PARAMS.exists():
        raise RuntimeError("Holdout locked until T411B_FROZEN_PARAMETERS.json exists")
    meta = base.load_metadata()
    raw = base.load_raw()
    fluids = base.DEVELOPMENT_FLUIDS if mode == "development" else base.HOLDOUT_FLUIDS
    meta = meta[meta.Fluid.isin(fluids)]
    all_series, summaries = [], []
    for _, m in meta.iterrows():
        ts, sm = analyse_rate_run(raw[raw.Name == m.Name], m)
        summaries.append(sm)
        if len(ts):
            all_series.append(ts)
    series = pd.concat(all_series, ignore_index=True)
    summary = pd.DataFrame(summaries)
    active = summary[~summary.excluded].copy()
    control = shift_control(series, active, seed=41122026 if mode == "development" else 41122027)
    OUT.mkdir(parents=True, exist_ok=True)
    series.to_csv(OUT / f"T411B_{mode.upper()}_TIMESERIES.csv", index=False)
    summary.to_csv(OUT / f"T411B_{mode.upper()}_EVENT_SUMMARY.csv", index=False)
    with (OUT / f"T411B_{mode.upper()}_CONTROL.json").open("w", encoding="utf-8") as f:
        json.dump(control, f, indent=2)
    plot(series, active, mode)
    result = {
        "mode": mode,
        "experiments": int(len(active)),
        "crossings": int(active.cross_u.notna().sum()),
        "crossing_fraction": float(active.cross_u.notna().mean()),
        "median_cross_u": float(active.cross_u.median()),
        "q10_cross_u": float(active.cross_u.quantile(0.10)),
        "q90_cross_u": float(active.cross_u.quantile(0.90)),
        "median_rho_time_x": float(active.rho_time_x.median()),
        "median_window_ms": float(active.window_ms.median()),
        "median_unmeasured_tail_ms": float(active.unmeasured_tail_ms.median()),
        "median_late_unresolved_to_capillary": float(active.late_unresolved_to_capillary.median()),
        "plate_size_cross_medians": {str(k): float(v) for k, v in active.groupby("D0_mm").cross_u.median().items()},
        "bo_cross_spearman": float(spearmanr(active.Bo0, active.cross_u, nan_policy="omit").statistic),
        "temporal_shift_control": control,
    }
    with (OUT / f"T411B_{mode.upper()}_RESULTS.json").open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["development", "holdout"], required=True)
    run(p.parse_args().mode)

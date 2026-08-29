"""T411 time-facing Irrationality Di-ARA in stretched filament breakup.

Development (S1/S3) is runnable immediately. Holdout (S2/S4) is locked until
T411_FROZEN_PARAMETERS.json exists beside this file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pdfplumber
from scipy.stats import spearmanr


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
OUT = HERE / "results"
RAW = SOURCE / "ThinningData.txt"
SUPPLEMENT = SOURCE / "rsos252527_si_001.pdf"
PARAMS = HERE / "T411_FROZEN_PARAMETERS.json"

ALPHA = 0.0709
G = 9.81
DEVELOPMENT_FLUIDS = {"S1", "S3"}
HOLDOUT_FLUIDS = {"S2", "S4"}

SURFACE_TENSION = {"S1": 30.76e-3, "S2": 28.65e-3, "S3": 27.24e-3, "S4": 16.61e-3}
VISCOSITY = {
    "S1": (-18.381, 5340.0),
    "S2": (-17.522, 5706.0),
    "S3": (-21.827, 7619.5),
    "S4": (-2.7863, 1582.4),
}
DENSITY = {
    "S1": (838.64, -0.00081978),
    "S2": (842.20, -0.0010956),
    "S3": (908.40, -0.0028823),
    "S4": (976.04, -0.0012792),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def load_metadata() -> pd.DataFrame:
    rows: list[list[str]] = []
    with pdfplumber.open(SUPPLEMENT) as pdf:
        for page_index in range(3, 7):
            tables = pdf.pages[page_index].extract_tables()
            if len(tables) != 1:
                raise RuntimeError(f"Expected one table on supplement page {page_index + 1}")
            table = tables[0]
            if page_index == 3:
                table = table[1:]
            rows.extend(table)
    columns = ["Name", "Fluid", "D0_mm", "T_C", "v_aim_mm_s", "v_mm_s", "H0_D0", "tbrk_s", "px_per_mm"]
    meta = pd.DataFrame(rows, columns=columns)
    # The final row label is clipped at the page edge in the published PDF's
    # extractable text. The visible Table A1 and raw source both identify it as
    # 250822 u, so repair that single source-layout omission explicitly.
    if meta["Name"].isna().sum() == 1 and meta.iloc[-1].Fluid == "S4":
        meta.loc[meta.index[-1], "Name"] = "250822 u"
    meta["Name"] = meta["Name"].str.replace(" ", "", regex=False)
    for c in columns[2:]:
        meta[c] = pd.to_numeric(meta[c], errors="raise")
    if len(meta) != 176 or meta.Name.nunique() != 176:
        raise RuntimeError(f"Metadata parse produced {len(meta)} rows / {meta.Name.nunique()} names")
    return meta


def load_raw() -> pd.DataFrame:
    raw = pd.read_csv(RAW)
    raw["Name"] = raw["Name"].ffill().astype(str).str.replace(" ", "", regex=False)
    separator = (raw.Time_s == 0) & (raw.D_px == 0) & (raw.D_mm == 0)
    raw = raw.loc[~separator].copy()
    return raw


def fluid_properties(fluid: str, temp_c: float) -> tuple[float, float, float]:
    temp_k = temp_c + 273.15
    a, b = VISCOSITY[fluid]
    mu = float(np.exp(a + b / temp_k))
    rho0, expansion = DENSITY[fluid]
    rho = float(rho0 * (1.0 + expansion * (temp_k - 293.15)))
    return mu, rho, SURFACE_TENSION[fluid]


def persistent_up_cross(u: np.ndarray, x: np.ndarray, persistence: int = 5) -> float:
    finite = np.isfinite(x)
    for j in range(1, len(x)):
        if not (finite[j - 1] and finite[j]):
            continue
        if x[j - 1] < 1.0 <= x[j]:
            tail = x[j : min(len(x), j + persistence)]
            if len(tail) == persistence and np.all(np.isfinite(tail)) and np.all(tail >= 1.0):
                denom = x[j] - x[j - 1]
                frac = 0.0 if denom == 0 else (1.0 - x[j - 1]) / denom
                return float(u[j - 1] + frac * (u[j] - u[j - 1]))
    return float("nan")


def analyse_run(group: pd.DataFrame, meta: pd.Series) -> tuple[pd.DataFrame, dict[str, object]]:
    reliable = group[np.isfinite(group.D_mm) & (group.D_px >= 5)].copy()
    if len(reliable) < 20:
        return pd.DataFrame(), {"Name": meta.Name, "excluded": True, "reason": "fewer_than_20_reliable_samples"}
    reliable = reliable.sort_values("Time_s")
    reliable["D_smooth_mm"] = reliable.D_mm.rolling(5, center=True, min_periods=1).median()

    fluid = str(meta.Fluid)
    mu, rho, sigma = fluid_properties(fluid, float(meta.T_C))
    d0 = float(meta.D0_mm)
    h0 = d0 * float(meta.H0_D0)
    v = float(meta.v_mm_s)
    t = reliable.Time_s.to_numpy(float)
    d_obs = reliable.D_smooth_mm.to_numpy(float)
    d_mech = d0 * np.power(1.0 + v * t / h0, -0.75)
    r = d0 - d_mech
    i = d_mech - d_obs
    total = r + i
    eligible = (total >= 0.10 * d0) & (r >= 0) & (i >= 0)
    x_ri = np.full(len(t), np.nan)
    x_ri[eligible] = 2.0 * i[eligible] / total[eligible]
    u = t / float(meta.tbrk_s)
    cross_u = persistent_up_cross(u, x_ri, persistence=5)

    if np.sum(np.isfinite(x_ri)) >= 5:
        rho_time = float(spearmanr(u[np.isfinite(x_ri)], x_ri[np.isfinite(x_ri)]).statistic)
    else:
        rho_time = float("nan")

    d0_m = d0 / 1000.0
    d_obs_m = d_obs / 1000.0
    h_m = (h0 + v * t) / 1000.0
    bo0 = rho * G * (d0_m / 2.0) ** 2 / sigma
    bo_local = rho * G * (d_obs_m / 2.0) ** 2 / sigma
    gh = rho * G * h_m * d_obs_m / (2.0 * sigma)
    r_cap_mm_s = 2.0 * ALPHA * sigma / mu * 1000.0

    late = u >= max(0.70, float(np.quantile(u, 0.70)))
    if np.sum(late) >= 8:
        slope = np.polyfit(t[late], d_obs[late], 1)[0]
        late_rate = float(max(-slope, 0.0))
    else:
        late_rate = float("nan")

    reliable["u_breakup"] = u
    reliable["D_mechanical_mm"] = d_mech
    reliable["R_parent_mm"] = r
    reliable["I_unresolved_mm"] = i
    reliable["total_observed_loss_mm"] = total
    reliable["x_RI_ara"] = x_ri
    reliable["Bo_local"] = bo_local
    reliable["G_height_proxy"] = gh
    reliable["fluid"] = fluid
    reliable["D0_mm"] = d0
    reliable["tbrk_s"] = float(meta.tbrk_s)
    reliable["split"] = "development" if fluid in DEVELOPMENT_FLUIDS else "holdout"

    if np.isfinite(cross_u):
        k = int(np.nanargmin(np.abs(u - cross_u)))
        cross_d = float(d_obs[k])
        cross_bo = float(bo_local[k])
        cross_gh = float(gh[k])
        cross_t = float(t[k])
    else:
        cross_d = cross_bo = cross_gh = cross_t = float("nan")

    summary = {
        "Name": str(meta.Name),
        "fluid": fluid,
        "split": "development" if fluid in DEVELOPMENT_FLUIDS else "holdout",
        "D0_mm": d0,
        "T_C": float(meta.T_C),
        "v_mm_s": v,
        "H0_D0": float(meta.H0_D0),
        "tbrk_s": float(meta.tbrk_s),
        "n_reliable": int(len(reliable)),
        "last_reliable_s": float(t[-1]),
        "unmeasured_tail_ms": float(1000.0 * (float(meta.tbrk_s) - t[-1])),
        "cross_u": cross_u,
        "cross_t_s": cross_t,
        "cross_D_mm": cross_d,
        "rho_time_x": rho_time,
        "Bo0": float(bo0),
        "Bo_cross": cross_bo,
        "G_height_cross": cross_gh,
        "capillary_rate_mm_s": float(r_cap_mm_s),
        "late_observed_rate_mm_s": late_rate,
        "late_to_capillary_rate": float(late_rate / r_cap_mm_s) if r_cap_mm_s > 0 else float("nan"),
        "excluded": False,
        "reason": "",
    }
    return reliable, summary


def circular_shift_control(timeseries: pd.DataFrame, summary: pd.DataFrame, seed: int, reps: int = 2000) -> dict[str, float]:
    observed = float(np.nanmedian(summary.rho_time_x))
    by_name = {n: g.sort_values("Time_s") for n, g in timeseries.groupby("Name")}
    rng = np.random.default_rng(seed)
    null = np.empty(reps)
    for rep in range(reps):
        vals = []
        for g in by_name.values():
            r = g.R_parent_mm.to_numpy(float)
            i = g.I_unresolved_mm.to_numpy(float)
            total_loss = g.total_observed_loss_mm.to_numpy(float)
            u = g.u_breakup.to_numpy(float)
            if len(g) < 20:
                continue
            shift = int(rng.integers(1, len(g)))
            ish = np.roll(i, shift)
            denom = r + ish
            valid = (total_loss >= 0.10 * float(g.D0_mm.iloc[0])) & (r >= 0) & (ish >= 0) & (denom > 0)
            if np.sum(valid) >= 5:
                vals.append(float(spearmanr(u[valid], 2.0 * ish[valid] / denom[valid]).statistic))
        null[rep] = np.nanmedian(vals) if vals else np.nan
    valid_null = null[np.isfinite(null)]
    p = float((1 + np.sum(valid_null >= observed)) / (1 + len(valid_null)))
    return {
        "observed_median_rho": observed,
        "null_median": float(np.nanmedian(valid_null)),
        "null_q95": float(np.nanquantile(valid_null, 0.95)),
        "p_ge_observed": p,
        "reps": int(len(valid_null)),
    }


def plot_results(timeseries: pd.DataFrame, summary: pd.DataFrame, mode: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    palette = {"S1": "#d95f02", "S2": "#1b9e77", "S3": "#7570b3", "S4": "#e7298a"}
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)

    examples = []
    for fluid in sorted(summary.fluid.unique()):
        s = summary[(summary.fluid == fluid) & summary.cross_u.notna()]
        if len(s):
            examples.append(str(s.iloc[len(s) // 2].Name))
    for name in examples:
        g = timeseries[timeseries.Name == name]
        axes[0, 0].plot(g.u_breakup, g.x_RI_ara, lw=1.6, label=f"{name} ({g.fluid.iloc[0]})")
    axes[0, 0].axhline(1, color="#222", ls="--", label="equal-participation ridge x=1")
    axes[0, 0].axvline(1, color="#b2182b", ls=":", label="direct breakup u=1")
    axes[0, 0].set(xlabel="fraction of direct breakup time u=t/t_break", ylabel="parent/residual ARA x_RI (0-2)", title="Time-facing ARA trajectories (representative runs)", xlim=(0, 1.02), ylim=(-0.03, 2.03))
    axes[0, 0].legend(fontsize=8)

    for fluid, g in summary.groupby("fluid"):
        axes[0, 1].scatter(g.Bo0, g.cross_u, s=34, alpha=0.75, color=palette[fluid], label=f"{fluid}, n={len(g)}")
    axes[0, 1].set(xlabel="initial local Bond number Bo0 (gravity/capillarity)", ylabel="inferred ridge-crossing u", title="Gravity rival: does crossing follow Bo0?")
    axes[0, 1].legend(fontsize=8)

    good = summary.cross_u.notna()
    bins = np.linspace(0, 1, 21)
    for fluid, g in summary[good].groupby("fluid"):
        axes[1, 0].hist(g.cross_u, bins=bins, alpha=0.55, color=palette[fluid], label=fluid)
    axes[1, 0].set(xlabel="inferred ridge-crossing u", ylabel="experiment count", title="Distribution of inferred handover times")
    axes[1, 0].legend()

    for d0, marker in [(1.0, "o"), (2.0, "^")]:
        g = summary[np.isclose(summary.D0_mm, d0)]
        axes[1, 1].scatter(g.capillary_rate_mm_s, g.late_observed_rate_mm_s, s=36, alpha=0.7, marker=marker, label=f"{d0:g} mm plates")
    lim = max(float(summary.capillary_rate_mm_s.max()), float(summary.late_observed_rate_mm_s.max()))
    axes[1, 1].plot([0, lim], [0, lim], color="#222", ls="--", label="observed = capillary theory")
    axes[1, 1].set(xlabel="theoretical capillary thinning rate (mm/s)", ylabel="late observed thinning rate (mm/s)", title="Capillary interpretation of unresolved branch")
    axes[1, 1].legend(fontsize=8)

    fig.suptitle(f"T411 {mode}: same filament through time", fontsize=16, fontweight="bold")
    fig.savefig(OUT / f"T411_{mode.upper()}_OVERVIEW.png", dpi=180)
    plt.close(fig)


def run(mode: str) -> None:
    if mode == "holdout" and not PARAMS.exists():
        raise RuntimeError("Holdout is locked: freeze T411_FROZEN_PARAMETERS.json first")
    meta = load_metadata()
    raw = load_raw()
    fluids = DEVELOPMENT_FLUIDS if mode == "development" else HOLDOUT_FLUIDS
    meta = meta[meta.Fluid.isin(fluids)].copy()

    series = []
    summaries = []
    for _, m in meta.iterrows():
        g = raw[raw.Name == m.Name]
        ts, sm = analyse_run(g, m)
        summaries.append(sm)
        if len(ts):
            series.append(ts)
    timeseries = pd.concat(series, ignore_index=True)
    summary = pd.DataFrame(summaries)
    active = summary[~summary.excluded].copy()
    control = circular_shift_control(timeseries, active, seed=4112026 if mode == "development" else 4112027)

    OUT.mkdir(parents=True, exist_ok=True)
    timeseries.to_csv(OUT / f"T411_{mode.upper()}_TIMESERIES.csv", index=False)
    summary.to_csv(OUT / f"T411_{mode.upper()}_EVENT_SUMMARY.csv", index=False)
    with (OUT / f"T411_{mode.upper()}_CONTROL.json").open("w", encoding="utf-8") as f:
        json.dump(control, f, indent=2)
    plot_results(timeseries, active, mode)

    result = {
        "mode": mode,
        "source_md5": hashlib.md5(RAW.read_bytes()).hexdigest(),
        "source_sha256": sha256(RAW),
        "supplement_sha256": sha256(SUPPLEMENT),
        "experiments": int(len(active)),
        "crossings": int(active.cross_u.notna().sum()),
        "crossing_fraction": float(active.cross_u.notna().mean()),
        "median_cross_u": float(active.cross_u.median()),
        "q10_cross_u": float(active.cross_u.quantile(0.10)),
        "q90_cross_u": float(active.cross_u.quantile(0.90)),
        "median_rho_time_x": float(active.rho_time_x.median()),
        "median_unmeasured_tail_ms": float(active.unmeasured_tail_ms.median()),
        "median_late_to_capillary_rate": float(active.late_to_capillary_rate.median()),
        "plate_size_cross_medians": {str(k): float(v) for k, v in active.groupby("D0_mm").cross_u.median().items()},
        "bo_cross_spearman": float(spearmanr(active.Bo0, active.cross_u, nan_policy="omit").statistic),
        "temporal_shift_control": control,
    }
    with (OUT / f"T411_{mode.upper()}_RESULTS.json").open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["development", "holdout"], required=True)
    args = parser.parse_args()
    run(args.mode)

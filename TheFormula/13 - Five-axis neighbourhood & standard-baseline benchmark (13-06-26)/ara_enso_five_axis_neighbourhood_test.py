#!/usr/bin/env python3
"""
ENSO five-axis neighbourhood test.

This is a first ablation of the 31-sphere local environment idea:

    home sphere + 5 axes * 2 directions * 3 depths = 31 local spheres.

It uses real ENSO local data where available (NINO3.4, SOI, WWV west/east) and
terrain defaults for contacts that are not yet measured.

The test is strict-causal in the same sense as the current framework:
features at forecast origin t use observed values at or before t; the readout is
fit on the 1/phi training span and scored on the held-out shed span.
"""

from __future__ import annotations

import json
import math
import os
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import ara_framework as F
from ara_five_axis_neighbourhood import (
    AXES,
    PHI,
    ContactAddress,
    build_contact_addresses,
    depth_weight,
    parity,
    recursive_ara_terrain,
)
import ara_forecast_standard_baseline_comparison as B


OUT_JSON = os.path.join(HERE, "ara_enso_five_axis_neighbourhood_result.json")
OUT_MD = os.path.join(HERE, "ARA_ENSO_FIVE_AXIS_NEIGHBOURHOOD_RESULT.md")


@dataclass(frozen=True)
class ContactSpec:
    series_key: str | None
    period: float
    window: int
    sign: float = 1.0
    role: str = ""


def train_standardize(x: np.ndarray, cutoff: int) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    tr = x[:cutoff]
    tr = tr[np.isfinite(tr)]
    mu = float(np.mean(tr))
    sd = float(np.std(tr))
    if not np.isfinite(sd) or sd < 1e-12:
        sd = 1.0
    return (x - mu) / sd


def shifted(x: np.ndarray, lag: int) -> np.ndarray:
    out = np.full_like(x, np.nan, dtype=float)
    if lag == 0:
        out[:] = x
    elif lag < len(x):
        out[lag:] = x[:-lag]
    return out


def trailing_mean(x: np.ndarray, window: int) -> np.ndarray:
    out = np.full_like(x, np.nan, dtype=float)
    w = max(2, int(window))
    for i in range(w - 1, len(x)):
        block = x[i - w + 1 : i + 1]
        if np.all(np.isfinite(block)):
            out[i] = float(np.mean(block))
    return out


def contact_plan() -> Dict[str, ContactSpec]:
    """
    Map available ENSO measurements into the five-axis contact lattice.

    Missing entries are not treated as empty; they are filled by recursive terrain
    defaults in `contact_row()`.
    """
    return {
        # X: ARA mapping pressure. Directly measured from home and partner sides.
        "x_mapping_ara:minus:1": ContactSpec("nino", 48, 12, -1, "home space-side current"),
        "x_mapping_ara:plus:1": ContactSpec("nino", 48, 12, 1, "home time-side current"),
        "x_mapping_ara:minus:2": ContactSpec("soi", 48, 12, 1, "partner map pressure"),
        "x_mapping_ara:plus:2": ContactSpec("soi", 48, 12, -1, "partner mirror pressure"),
        # Y: rung/scale. Lower side is WWV feeder; upper side is slow reservoir.
        "y_rung:minus:1": ContactSpec("wwv_w", 6, 6, 1, "lower west WWV feeder"),
        "y_rung:minus:2": ContactSpec("wwv_e", 6, 6, 1, "lower east WWV feeder"),
        "y_rung:minus:3": ContactSpec("wwv_total", 12, 12, 1, "lower combined WWV background"),
        "y_rung:plus:1": ContactSpec("wwv_total", 60, 60, 1, "upper slow WWV reservoir"),
        "y_rung:plus:2": ContactSpec("nino", 96, 48, 1, "upper home slow envelope"),
        # Z: coupling/contact and traversal.
        "z_coupling:minus:1": ContactSpec("soi", 3, 3, 1, "SOI direct contact"),
        "z_coupling:plus:1": ContactSpec("soi", 12, 12, -1, "SOI traversal mirror"),
        "z_coupling:minus:2": ContactSpec("wwv_total", 24, 24, 1, "subsurface contact background"),
        # Phi/anti-phi: efficient route and counter-route.
        "phi_line:plus:1": ContactSpec("wwv_total", 6, 6, 1, "feeder into phi route"),
        "phi_line:minus:1": ContactSpec("soi", 6, 6, -1, "counter into phi route"),
        "phi_line:plus:2": ContactSpec("nino", 48, 24, 1, "home route memory"),
        "anti_phi_line:plus:1": ContactSpec("soi", 6, 6, 1, "anti-phase route"),
        "anti_phi_line:minus:1": ContactSpec("wwv_total", 6, 6, -1, "anti-feeder route"),
        "anti_phi_line:plus:2": ContactSpec("nino", 48, 24, -1, "home mirror route"),
    }


def observed_contact_arrays(
    data: Dict[str, np.ndarray],
    cutoff: int,
    plan: Dict[str, ContactSpec],
) -> Dict[str, Dict[str, np.ndarray]]:
    out: Dict[str, Dict[str, np.ndarray]] = {}
    for key, spec in plan.items():
        if spec.series_key is None:
            continue
        z = train_standardize(spec.sign * data[spec.series_key], cutoff)
        slow = trailing_mean(z, spec.window)
        fast = z - slow
        spin = fast - shifted(fast, 1)
        pressure = fast
        envelope = slow
        ara = 1.0 + np.tanh(z / 2.0)
        terrain_slope = np.zeros_like(z)
        ridge_pressure = np.zeros_like(z)
        for i, v in enumerate(ara):
            if np.isfinite(v):
                trn = recursive_ara_terrain(float(v), depth=5)
                terrain_slope[i] = trn["terrain_slope"]
                ridge_pressure[i] = trn["ridge_pressure"]
            else:
                terrain_slope[i] = np.nan
                ridge_pressure[i] = np.nan
        out[key] = {
            "z": z,
            "spin": spin,
            "pressure": pressure,
            "envelope": envelope,
            "ara": ara,
            "terrain_slope": terrain_slope,
            "ridge_pressure": ridge_pressure,
        }
    return out


def default_contact_values(home_ara: float, address: ContactAddress) -> Dict[str, float]:
    # No blank space: unobserved contacts still have recursive ARA terrain.
    coord = float(np.clip(home_ara + address.direction * 0.12 * depth_weight(address.depth), 0.0, 2.0))
    trn = recursive_ara_terrain(coord, depth=5)
    spin = address.direction * parity(address.depth) * depth_weight(address.depth)
    pressure = abs(trn["terrain_slope"]) * depth_weight(address.depth)
    return {
        "ara": coord,
        "spin": spin,
        "pressure": pressure,
        "envelope": 0.0,
        "terrain_slope": trn["terrain_slope"],
        "ridge_pressure": trn["ridge_pressure"],
    }


def contact_force_scalar(address: ContactAddress, vals: Dict[str, float]) -> float:
    brake = 1.0 + max(0.0, vals["ridge_pressure"])
    drive = vals["spin"] + 0.6 * vals["pressure"] + 0.4 * vals["terrain_slope"] + 0.25 * vals["envelope"]
    return address.direction * parity(address.depth) * depth_weight(address.depth) * drive / brake


def build_rows(
    data: Dict[str, np.ndarray],
    cutoff: int,
    origins: Iterable[int],
    max_depth: int,
    axes: Tuple[str, ...],
    include_individual: bool = True,
) -> np.ndarray:
    home_z = train_standardize(data["nino"], cutoff)
    home_ara = 1.0 + np.tanh(home_z / 2.0)
    plan = contact_plan()
    observed = observed_contact_arrays(data, cutoff, plan)
    addresses = [a for a in build_contact_addresses(3) if a.depth <= max_depth and a.axis in axes]
    axis_names = list(AXES)
    rows: List[List[float]] = []
    for t in origins:
        row: List[float] = []
        summed = {axis: 0.0 for axis in axis_names}
        abs_summed = {axis: 0.0 for axis in axis_names}
        observed_count = 0.0
        default_count = 0.0
        individual: List[float] = []
        for address in addresses:
            key = address.key
            if key in observed:
                arrs = observed[key]
                vals = {k: float(arrs[k][t]) for k in ("ara", "spin", "pressure", "envelope", "terrain_slope", "ridge_pressure")}
                if not all(np.isfinite(v) for v in vals.values()):
                    vals = default_contact_values(float(home_ara[t]), address)
                    default_count += 1.0
                else:
                    observed_count += 1.0
            else:
                vals = default_contact_values(float(home_ara[t]), address)
                default_count += 1.0
            force = contact_force_scalar(address, vals)
            summed[address.axis] += force
            abs_summed[address.axis] += abs(force)
            if include_individual:
                individual.extend([
                    force,
                    vals["ara"] - float(home_ara[t]),
                    vals["spin"],
                    vals["terrain_slope"],
                    vals["ridge_pressure"],
                ])
        row.extend([summed[a] for a in axis_names])
        row.extend([abs_summed[a] for a in axis_names])
        row.extend([
            sum(summed.values()),
            sum(abs_summed.values()),
            observed_count,
            default_count,
            float(home_ara[t]),
            float(home_z[t]),
            float(home_z[t] - home_z[t - 1]) if t > 0 and np.isfinite(home_z[t - 1]) else 0.0,
        ])
        row.extend([
            summed["x_mapping_ara"] * summed["y_rung"],
            summed["z_coupling"] * summed["phi_line"],
            summed["phi_line"] - summed["anti_phi_line"],
            abs_summed["y_rung"] / (1.0 + abs_summed["z_coupling"]),
        ])
        row.extend(individual)
        rows.append(row)
    return np.nan_to_num(np.asarray(rows, dtype=float))


def ridge_readout(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray, penalty: float) -> np.ndarray:
    mu = np.nanmean(x_train, axis=0)
    sd = np.nanstd(x_train, axis=0)
    sd[~np.isfinite(sd) | (sd < 1e-12)] = 1.0
    a = np.nan_to_num((x_train - mu) / sd)
    b = np.nan_to_num((x_test - mu) / sd)
    a = np.column_stack([np.ones(len(a)), a])
    b = np.column_stack([np.ones(len(b)), b])
    reg = np.eye(a.shape[1]) * penalty
    reg[0, 0] = 0.0
    beta = np.linalg.solve(a.T @ a + reg, a.T @ y_train)
    return b @ beta


def choose_penalty(
    xtr: np.ndarray,
    delta_tr: np.ndarray,
    current_tr: np.ndarray,
    truth_tr: np.ndarray,
) -> float:
    """Choose regularization using only the training span."""
    penalties = (0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0)
    split = max(30, int(len(xtr) * 0.78))
    if split >= len(xtr) - 10:
        return 1.0
    best = None
    for p in penalties:
        pred_delta = ridge_readout(xtr[:split], delta_tr[:split], xtr[split:], penalty=p)
        pred = current_tr[split:] + pred_delta
        met = metrics(truth_tr[split:], pred, current_tr[split:])
        score = (met["corr"], -met["mae"])
        if best is None or score > best[0]:
            best = (score, p)
    return float(best[1])


def corr(a: np.ndarray, b: np.ndarray) -> float:
    v = np.isfinite(a) & np.isfinite(b)
    if int(np.sum(v)) < 3:
        return float("nan")
    return float(np.corrcoef(a[v], b[v])[0, 1])


def metrics(truth: np.ndarray, pred: np.ndarray, current: np.ndarray) -> Dict[str, float]:
    v = np.isfinite(truth) & np.isfinite(pred) & np.isfinite(current)
    truth = truth[v]
    pred = pred[v]
    current = current[v]
    if len(truth) < 3:
        return {"n": int(len(truth)), "corr": float("nan"), "mae": float("nan"), "turn": float("nan")}
    return {
        "n": int(len(truth)),
        "corr": float(np.corrcoef(truth, pred)[0, 1]),
        "mae": float(np.mean(np.abs(truth - pred))),
        "turn": float(np.mean(np.sign(truth - current) == np.sign(pred - current))),
    }


def run_model(
    y: np.ndarray,
    data: Dict[str, np.ndarray],
    cutoff: int,
    horizon: int,
    lags: Tuple[int, ...],
    max_depth: int,
    axes: Tuple[str, ...],
    include_home: bool,
    include_individual: bool,
    label: str,
) -> Tuple[str, Dict[str, float], List[float]]:
    start = max(max(lags), 97)
    tr = np.arange(start, cutoff - horizon)
    te = np.arange(cutoff, len(y) - horizon)
    truth_tr = y[tr + horizon]
    current_tr = y[tr]
    delta_tr = truth_tr - current_tr
    truth_te = y[te + horizon]
    current_te = y[te]
    xtr = build_rows(data, cutoff, tr, max_depth=max_depth, axes=axes, include_individual=include_individual)
    xte = build_rows(data, cutoff, te, max_depth=max_depth, axes=axes, include_individual=include_individual)
    if include_home:
        htr = np.asarray([[y[t - lag] for lag in lags] for t in tr], dtype=float)
        hte = np.asarray([[y[t - lag] for lag in lags] for t in te], dtype=float)
        xtr = np.column_stack([htr, xtr])
        xte = np.column_stack([hte, xte])
    penalty = choose_penalty(xtr, delta_tr, current_tr, truth_tr)
    pred = current_te + ridge_readout(xtr, delta_tr, xte, penalty=penalty)
    met = metrics(truth_te, pred, current_te)
    met["penalty"] = penalty
    met["feature_count"] = int(xtr.shape[1])
    return label, met, pred.astype(float).tolist()


def load_enso() -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    nino = B.load_nino()
    soi = B.load_soi()
    west = B.load_wwv("west")
    east = B.load_wwv("east")
    common = nino.index.intersection(soi.index).intersection(west.index).intersection(east.index).sort_values()
    data = {
        "nino": nino.reindex(common).values.astype(float),
        "soi": soi.reindex(common).values.astype(float),
        "wwv_w": west.reindex(common).values.astype(float),
        "wwv_e": east.reindex(common).values.astype(float),
    }
    data["wwv_total"] = data["wwv_w"] + data["wwv_e"]
    return common.values.astype("datetime64[M]").astype(str), data


def run():
    dates, data = load_enso()
    y = B.clean(data["nino"])
    for key in list(data):
        data[key] = B.clean(data[key])[: len(y)]
    period = 48
    horizons = (3, 6, 12, 18, 24)
    lags = B.default_lags(len(y), period)

    system = F.build_system(
        y,
        (("SOI", data["soi"], 3, 3), ("WWV_W", data["wwv_w"], 6, 6), ("WWV_E", data["wwv_e"], 6, 6)),
        (("WWV_TOTAL_SLOW", data["wwv_total"], 60, 60),),
        period,
        horizons,
        lags,
        name="enso_nino34_five_axis",
        unit="month",
    )
    base_ara = F.run_forecast(system)
    cutoff = base_ara["cutoff_index"]
    proxy = B.proxy_baselines(y, period, horizons, cutoff, lags)

    axes_3 = ("x_mapping_ara", "y_rung", "z_coupling")
    axes_5 = tuple(AXES.keys())
    results = {
        "name": "enso_nino34_five_axis_neighbourhood",
        "n": int(len(y)),
        "cutoff_index": int(cutoff),
        "cutoff_date": str(dates[cutoff]) if cutoff < len(dates) else None,
        "period": period,
        "lags": list(lags),
        "contact_count_depth3": len(build_contact_addresses(3)),
        "horizons": {},
    }

    for h in horizons:
        key = str(h)
        te = np.arange(cutoff, len(y) - h)
        truth = y[te + h]
        current = y[te]
        rows: Dict[str, Dict[str, float]] = {}
        series: Dict[str, List[float]] = {}

        # Existing framework metrics.
        for model_name, m in base_ara["horizons"][key].items():
            rows[model_name] = m

        # Local proxy baselines.
        if proxy[key] is not None:
            rows.update(proxy[key])

        model_specs = [
            (1, axes_5, False, False, "five_axis_depth1_summary_no_home"),
            (2, axes_5, False, False, "five_axis_depth2_summary_no_home"),
            (3, axes_5, False, False, "five_axis_depth3_summary_no_home"),
            (1, axes_5, False, True, "five_axis_depth1_full_no_home"),
            (2, axes_5, False, True, "five_axis_depth2_full_no_home"),
            (3, axes_5, False, True, "five_axis_depth3_full_no_home"),
            (3, axes_3, False, False, "three_axis_depth3_summary_no_home"),
            (3, axes_5, True, False, "home_plus_five_axis_depth3_summary"),
            (2, axes_5, True, False, "home_plus_five_axis_depth2_summary"),
            (3, axes_5, True, True, "home_plus_five_axis_depth3_full"),
        ]
        for depth, axes, include_home, include_individual, label in model_specs:
            name, met, pred = run_model(y, data, cutoff, h, lags, depth, axes, include_home, include_individual, label)
            rows[name] = met
            series[name] = pred

        non_ara_candidates = ["persistence", "seasonal_naive", "harmonic_clock", "lag_harmonic_ridge", "home_ar"]
        best_corr = max((rows[m] for m in non_ara_candidates if m in rows), key=lambda r: r["corr"])
        best_corr_model = next(m for m in non_ara_candidates if m in rows and rows[m] is best_corr)
        best_mae = min((rows[m] for m in non_ara_candidates if m in rows), key=lambda r: r["mae"])
        best_mae_model = next(m for m in non_ara_candidates if m in rows and rows[m] is best_mae)
        best_five_corr_model = max(
            [m for m in rows if "five_axis" in m or "three_axis" in m],
            key=lambda m: rows[m]["corr"],
        )
        best_five_mae_model = min(
            [m for m in rows if "five_axis" in m or "three_axis" in m],
            key=lambda m: rows[m]["mae"],
        )

        results["horizons"][key] = {
            "models": rows,
            "best_non_ara_corr": {"model": best_corr_model, **best_corr},
            "best_non_ara_mae": {"model": best_mae_model, **best_mae},
            "best_five_axis_corr": {"model": best_five_corr_model, **rows[best_five_corr_model]},
            "best_five_axis_mae": {"model": best_five_mae_model, **rows[best_five_mae_model]},
            "series": {
                "origin_index": te.astype(int).tolist(),
                "origin_date": [str(dates[i]) for i in te],
                "truth": truth.astype(float).tolist(),
                "current": current.astype(float).tolist(),
                **series,
            },
        }
    return results


def fmt(v: float) -> str:
    if v is None or not np.isfinite(v):
        return "n/a"
    return f"{v:+.3f}"


def write_md(result: Dict[str, object]) -> None:
    lines: List[str] = []
    lines.append("# ENSO Five-Axis Neighbourhood Test")
    lines.append("")
    lines.append("This tests the 31-sphere local environment idea on ENSO/NINO3.4:")
    lines.append("")
    lines.append("- home sphere: NINO3.4")
    lines.append("- measured contacts: SOI, WWV west, WWV east, combined WWV reservoir")
    lines.append("- unmeasured contacts: recursive ARA terrain defaults")
    lines.append("- contact lattice: 5 axes x 2 directions x 3 depths = 30 surrounding contacts")
    lines.append("- readout: strict-causal ridge delta readout fit on the 1/phi training span")
    lines.append("")
    lines.append("Important fence: this is a first ablation of the full surroundings, not a final operational ENSO forecast.")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append("| h | best five-axis corr | best non-ARA corr | existing home+ARA corr | best five-axis MAE | best non-ARA MAE | existing home+ARA MAE | read |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---|")
    five_corr_wins = 0
    five_mae_wins = 0
    home_ara_corr_wins = 0
    for h, row in result["horizons"].items():
        bf = row["best_five_axis_corr"]
        bm5 = row["best_five_axis_mae"]
        bc = row["best_non_ara_corr"]
        bm = row["best_non_ara_mae"]
        hp = row["models"]["home_plus_ara"]
        if bf["corr"] > bc["corr"]:
            five_corr_wins += 1
        if bm5["mae"] < bm["mae"]:
            five_mae_wins += 1
        if hp["corr"] > bc["corr"]:
            home_ara_corr_wins += 1
        read = []
        read.append("five corr win" if bf["corr"] > bc["corr"] else "baseline corr win")
        if bm5["mae"] < bm["mae"]:
            read.append("five MAE win")
        lines.append(
            f"| {h} | {bf['model']} {fmt(bf['corr'])} | {bc['model']} {fmt(bc['corr'])} | "
            f"{fmt(hp['corr'])} | {bm5['model']} {bm5['mae']:.3f} | "
            f"{bm['model']} {bm['mae']:.3f} | {hp['mae']:.3f} | {'; '.join(read)} |"
        )
    total = len(result["horizons"])
    lines.append("")
    lines.append(f"Best five-axis variant beat the best non-ARA correlation baseline at **{five_corr_wins}/{total}** horizons.")
    lines.append(f"Best five-axis variant beat the best non-ARA MAE baseline at **{five_mae_wins}/{total}** horizons.")
    lines.append(f"Existing `home_plus_ara` beat the best non-ARA correlation baseline at **{home_ara_corr_wins}/{total}** horizons.")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- If five-axis no-home wins, the surroundings are carrying standalone geometry signal.")
    lines.append("- If home-plus-five-axis wins, the surroundings are useful as calibration around home wave memory.")
    lines.append("- If ordinary `home_ar` still wins, the current five-axis wiring is not yet adding enough over causal memory.")
    lines.append("- If depth 2/3 helps over depth 1, the three-deep environment is earning its keep.")
    lines.append("")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    result = run()
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    write_md(result)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    for h, row in result["horizons"].items():
        bf = row["best_five_axis_corr"]
        bc = row["best_non_ara_corr"]
        hp = row["models"]["home_plus_ara"]
        print(
            f"h={h:>2} five={bf['model']} corr={bf['corr']:+.3f} "
            f"nonARA={bc['model']} corr={bc['corr']:+.3f} "
            f"home+ARA={hp['corr']:+.3f}"
        )


if __name__ == "__main__":
    main()

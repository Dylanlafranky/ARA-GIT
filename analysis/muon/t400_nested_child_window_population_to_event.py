#!/usr/bin/env python3
"""T400: nested delayed-child window and population-to-event transfer.

The population cut is defined on calibration-only prompt/delayed rates.  Its
parent ARA interval is expanded to a local 0-2 child coordinate, then applied
unchanged to untouched unbinned COHERENT detector events.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDOR = HERE / "_vendor"
EXTRA = Path(r"F:\SystemFormulaFolder\.codex_python_packages")
for entry in (EXTRA, VENDOR):
    if entry.exists():
        sys.path.insert(0, str(entry))

os.environ.setdefault("MPLCONFIGDIR", str(HERE / "_mplconfig"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize


OUT = HERE / "T400_nested_child_window_population_to_event"
PROTOCOL = HERE / "T400_NESTED_CHILD_WINDOW_POPULATION_TO_EVENT_PROTOCOL_2026-08-17.md"
T399_LOO = HERE / "T399_child_half_precrest_sequence" / "T399_LEAVE_ONE_OUT_LANDMARKS.csv"
T371_COMPONENTS = HERE / "T371_COHERENT_PION_MUON_DIARA_COMPONENTS.csv"
T398_OVERLAP = HERE / "T398_population_neutrino_wave_overlap" / "T398_NATIVE_WAVE_OVERLAP.csv"
DATA = Path(r"F:\SystemFormulaFolder\external_data\coherent_csi_2110_07730\anc")
SEED = 400
CAL_FRACTION = 0.70
N_SPLITS = 20
N_BOOT = 2000
N_SHIFT = 1199
HIST_EDGES = np.linspace(0.0, 2.0, 9)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def event_split(events: np.ndarray, label: str, salt: int) -> np.ndarray:
    """Deterministic, content-bound calibration mask."""
    out = np.zeros(len(events), dtype=bool)
    threshold = int(CAL_FRACTION * 10_000)
    for i, (pe, time_us) in enumerate(events[:, :2]):
        token = f"T400|{salt}|{label}|{i}|{pe:.9f}|{time_us:.9f}".encode()
        value = int.from_bytes(hashlib.blake2b(token, digest_size=8).digest(), "big") % 10_000
        out[i] = value < threshold
    return out


def normalize(values: np.ndarray) -> np.ndarray:
    total = float(np.sum(values))
    if not total > 0:
        raise ValueError("Cannot normalize a non-positive template")
    return np.asarray(values, dtype=float) / total


def hist_time(events: np.ndarray) -> np.ndarray:
    keep = (events[:, 1] >= 0.0) & (events[:, 1] < 6.0)
    return np.histogram(events[keep, 1], bins=np.arange(0.0, 6.0 + 0.5, 0.5))[0].astype(float)


def fit_calibration(
    y_c: np.ndarray,
    y_ac: np.ndarray,
    templates: list[np.ndarray],
    exposure_fraction: float,
) -> dict[str, object]:
    ss, brn, nin, prompt, delayed = templates
    prior_brn = 18.4 * exposure_fraction
    prior_nin = 5.6 * exposure_fraction
    sigma_brn = max(4.6 * exposure_fraction, 1e-9)
    sigma_nin = max(2.0 * exposure_fraction, 1e-9)

    def objective(params: np.ndarray) -> tuple[float, np.ndarray]:
        n_ss, n_brn, n_nin, n_prompt, n_delayed = params
        mu_c = n_ss * ss + n_brn * brn + n_nin * nin + n_prompt * prompt + n_delayed * delayed
        mu_ac = n_ss * ss
        mu_c = np.maximum(mu_c, 1e-12)
        mu_ac = np.maximum(mu_ac, 1e-12)
        value = float(np.sum(mu_c - y_c * np.log(mu_c)) + np.sum(mu_ac - y_ac * np.log(mu_ac)))
        value += 0.5 * ((n_brn - prior_brn) / sigma_brn) ** 2
        value += 0.5 * ((n_nin - prior_nin) / sigma_nin) ** 2
        rc = 1.0 - y_c / mu_c
        ra = 1.0 - y_ac / mu_ac
        grad = np.array(
            [
                np.sum(ss * rc) + np.sum(ss * ra),
                np.sum(brn * rc) + (n_brn - prior_brn) / sigma_brn**2,
                np.sum(nin * rc) + (n_nin - prior_nin) / sigma_nin**2,
                np.sum(prompt * rc),
                np.sum(delayed * rc),
            ],
            dtype=float,
        )
        return value, grad

    start = np.array([1286.0, 18.4, 5.6, 100.0, 200.0]) * exposure_fraction
    result = minimize(
        lambda p: objective(p)[0],
        start,
        jac=lambda p: objective(p)[1],
        bounds=[(0.0, None)] * 5,
        method="L-BFGS-B",
        options={"maxiter": 5000, "ftol": 1e-12, "gtol": 1e-8},
    )
    return {
        "success": bool(result.success),
        "message": str(result.message),
        "nll": float(result.fun),
        "params": np.asarray(result.x, dtype=float),
    }


def crossing(time: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
    diff = a - b
    peak = int(np.argmax(a))
    for i in range(peak, len(diff) - 1):
        if diff[i] >= 0.0 and diff[i + 1] <= 0.0:
            return float(time[i] - diff[i] * (time[i + 1] - time[i]) / (diff[i + 1] - diff[i]))
    return float("nan")


def descending_return(time: np.ndarray, curve: np.ndarray, peak: int, height: float) -> float:
    for i in range(peak, len(curve) - 1):
        if curve[i] >= height and curve[i + 1] <= height:
            if curve[i + 1] == curve[i]:
                return float(time[i])
            return float(time[i] + (height - curve[i]) * (time[i + 1] - time[i]) / (curve[i + 1] - curve[i]))
    return float("nan")


def weighted_quantile(values: np.ndarray, weights: np.ndarray, probability: float) -> float:
    order = np.argsort(values)
    x = values[order]
    w = weights[order]
    total = float(w.sum())
    if total <= 0:
        return float("nan")
    cdf = np.cumsum(w) / total
    return float(np.interp(probability, cdf, x))


def child_window(
    time: np.ndarray,
    prompt_shape: np.ndarray,
    delayed_shape: np.ndarray,
    n_prompt: float,
    n_delayed: float,
) -> dict[str, object]:
    p = n_prompt * prompt_shape / prompt_shape.sum()
    d = n_delayed * delayed_shape / delayed_shape.sum()
    total = p + d
    parent_x = 2.0 * np.cumsum(total) / total.sum()
    left = crossing(time, p, d)
    mode_index = int(np.argmax(d))
    mode_time = float(time[mode_index])
    left_height = float(np.interp(left, time, d)) if math.isfinite(left) else float("nan")
    right = descending_return(time, d, mode_index, left_height) if math.isfinite(left) else float("nan")
    if not (math.isfinite(left) and math.isfinite(right) and left < mode_time < right):
        return {"valid": False, "left_time_us": left, "mode_time_us": mode_time, "right_time_us": right}
    x_left = float(np.interp(left, time, parent_x))
    x_right = float(np.interp(right, time, parent_x))
    x_mode_parent = float(parent_x[mode_index])
    local_x = 2.0 * (parent_x - x_left) / (x_right - x_left)
    local_mode = float(2.0 * (x_mode_parent - x_left) / (x_right - x_left))
    mask = (time >= left) & (time <= right)
    weights = d[mask]
    local = local_x[mask]
    mean = float(np.average(local, weights=weights))
    median = weighted_quantile(local, weights, 0.5)
    variance = float(np.average((local - mean) ** 2, weights=weights))
    skew = float(np.average((local - mean) ** 3, weights=weights) / variance**1.5) if variance > 0 else 0.0
    return {
        "valid": True,
        "left_time_us": left,
        "mode_time_us": mode_time,
        "right_time_us": right,
        "left_parent_ara": x_left,
        "mode_parent_ara": x_mode_parent,
        "right_parent_ara": x_right,
        "local_mode_ara": local_mode,
        "local_weighted_mean": mean,
        "local_weighted_median": median,
        "local_weighted_skewness": skew,
        "window_delayed_mass_fraction": float(weights.sum() / d.sum()),
        "parent_x": parent_x,
        "local_x": local_x,
        "prompt_rate": p,
        "delayed_rate": d,
    }


def event_membership(
    events: np.ndarray,
    params: np.ndarray,
    templates: list[np.ndarray],
    window: dict[str, object],
    native_time: np.ndarray,
    coincident: bool,
) -> dict[str, np.ndarray | float]:
    pe = events[:, 0]
    time_us = events[:, 1]
    tidx = np.floor(time_us / 0.5).astype(int)
    valid = (pe >= 0.0) & (pe < 60.0) & (tidx >= 0) & (tidx < 12)
    pe, time_us, tidx = pe[valid], time_us[valid], tidx[valid]
    n_ss, n_brn, n_nin, n_prompt, n_delayed = params
    ss, brn, nin, prompt, delayed = templates
    delayed_term = n_delayed * delayed[tidx]
    # Apply one calibration-frozen scoring rule to both C and AC records.
    # `coincident` is retained in the signature to keep the two source
    # identities explicit, but it must not change the classifier denominator:
    # otherwise the negative control would be scored by a different model.
    total = (
        n_ss * ss[tidx]
        + n_brn * brn[tidx]
        + n_nin * nin[tidx]
        + n_prompt * prompt[tidx]
        + delayed_term
    )
    probability = np.divide(delayed_term, np.maximum(total, 1e-12))
    left = float(window["left_time_us"])
    right = float(window["right_time_us"])
    in_window = (time_us >= left) & (time_us <= right)
    parent_x = np.asarray(window["parent_x"], dtype=float)
    x_left = float(window["left_parent_ara"])
    x_right = float(window["right_parent_ara"])
    event_parent_x = np.interp(time_us[in_window], native_time, parent_x)
    local_x = 2.0 * (event_parent_x - x_left) / (x_right - x_left)
    return {
        "pe": pe[in_window],
        "time_us": time_us[in_window],
        "local_x": local_x,
        "weight": probability[in_window],
        "mean_weight": float(probability[in_window].mean()) if np.any(in_window) else float("nan"),
        "median_weight": float(np.median(probability[in_window])) if np.any(in_window) else float("nan"),
    }


def histogram_metrics(local_x: np.ndarray, weights: np.ndarray) -> dict[str, object]:
    counts, _ = np.histogram(local_x, bins=HIST_EDGES, weights=weights)
    centers = (HIST_EDGES[:-1] + HIST_EDGES[1:]) / 2.0
    total = float(counts.sum())
    if total <= 0:
        return {"effective_count": 0.0, "mode": float("nan"), "mean": float("nan"), "median": float("nan"), "counts": counts}
    return {
        "effective_count": total,
        "mode": float(centers[int(np.argmax(counts))]),
        "mean": float(np.average(local_x, weights=weights)),
        "median": weighted_quantile(local_x, weights, 0.5),
        "counts": counts,
    }


def build_templates() -> tuple[list[np.ndarray], np.ndarray, np.ndarray, np.ndarray]:
    """Recover the frozen timing-only mixture and native source shapes.

    T371's saved component ledger contains each fitted 0.5-us timing
    component. Dividing by its own sum restores the registered timing shape,
    avoiding any new detector-response or ROOT reconstruction in T400.
    """
    component_rows = read_csv(T371_COMPONENTS)
    ss = normalize(np.array([float(row["steady"]) for row in component_rows]))
    brn = normalize(np.array([float(row["BRN"]) for row in component_rows]))
    nin = normalize(np.array([float(row["NIN"]) for row in component_rows]))
    prompt = normalize(np.array([float(row["prompt_nu_mu"]) for row in component_rows]))
    delayed = normalize(np.array([float(row["delayed_nu_e_plus_anti_nu_mu"]) for row in component_rows]))

    native_rows = read_csv(T398_OVERLAP)
    native_time = np.array([float(row["time_us"]) for row in native_rows])
    native_prompt = np.array([float(row["prompt_fitted_events_per_native_ns"]) for row in native_rows])
    native_delayed = np.array([float(row["delayed_total_fitted_events_per_native_ns"]) for row in native_rows])
    return [ss, brn, nin, prompt, delayed], native_time, native_prompt, native_delayed


def run_split(
    c_events: np.ndarray,
    ac_events: np.ndarray,
    templates_static: tuple[list[np.ndarray], np.ndarray, np.ndarray, np.ndarray],
    salt: int,
    save_events: bool = False,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    base_templates, native_time, native_prompt, native_delayed = templates_static
    c_cal_mask = event_split(c_events, "C", salt)
    ac_cal_mask = event_split(ac_events, "AC", salt)
    c_cal, c_hold = c_events[c_cal_mask], c_events[~c_cal_mask]
    ac_cal, ac_hold = ac_events[ac_cal_mask], ac_events[~ac_cal_mask]
    templates = list(base_templates)
    fit = fit_calibration(hist_time(c_cal), hist_time(ac_cal), templates, CAL_FRACTION)
    params = np.asarray(fit["params"], dtype=float)
    window = child_window(native_time, native_prompt, native_delayed, float(params[3]), float(params[4]))
    if not bool(window.get("valid", False)):
        return ({"salt": salt, "valid": False, "fit_success": bool(fit["success"])}, [], [])
    c_view = event_membership(c_hold, params, templates, window, native_time, True)
    ac_view = event_membership(ac_hold, params, templates, window, native_time, False)
    c_metrics = histogram_metrics(np.asarray(c_view["local_x"]), np.asarray(c_view["weight"]))
    ac_weights = np.asarray(ac_view["weight"])
    result = {
        "salt": salt,
        "valid": True,
        "fit_success": bool(fit["success"]),
        "n_calibration_C": int(len(c_cal)),
        "n_holdout_C": int(len(c_hold)),
        "n_calibration_AC": int(len(ac_cal)),
        "n_holdout_AC": int(len(ac_hold)),
        "n_prompt": float(params[3]),
        "n_delayed": float(params[4]),
        "left_time_us": float(window["left_time_us"]),
        "mode_time_us": float(window["mode_time_us"]),
        "right_time_us": float(window["right_time_us"]),
        "population_local_mode": float(window["local_mode_ara"]),
        "population_local_mean": float(window["local_weighted_mean"]),
        "population_local_median": float(window["local_weighted_median"]),
        "population_skewness": float(window["local_weighted_skewness"]),
        "holdout_C_events_in_window": int(len(np.asarray(c_view["local_x"]))),
        "holdout_AC_events_in_window": int(len(np.asarray(ac_view["local_x"]))),
        "effective_delayed_holdout": float(c_metrics["effective_count"]),
        "holdout_weighted_mode": float(c_metrics["mode"]),
        "holdout_weighted_mean": float(c_metrics["mean"]),
        "holdout_weighted_median": float(c_metrics["median"]),
        "mean_delayed_weight_C": float(c_view["mean_weight"]),
        "mean_delayed_weight_AC": float(ac_view["mean_weight"]),
        "median_delayed_weight_C": float(c_view["median_weight"]),
        "median_delayed_weight_AC": float(ac_view["median_weight"]),
        "C_median_weight_greater_than_AC": bool(float(c_view["median_weight"]) > float(ac_view["median_weight"])),
    }
    hist_rows = []
    counts = np.asarray(c_metrics["counts"], dtype=float)
    for i in range(len(counts)):
        hist_rows.append(
            {
                "salt": salt,
                "bin_low": float(HIST_EDGES[i]),
                "bin_high": float(HIST_EDGES[i + 1]),
                "bin_center": float((HIST_EDGES[i] + HIST_EDGES[i + 1]) / 2.0),
                "effective_delayed_weight": float(counts[i]),
            }
        )
    event_rows: list[dict[str, object]] = []
    if save_events:
        pe = np.asarray(c_view["pe"])
        time_us = np.asarray(c_view["time_us"])
        local_x = np.asarray(c_view["local_x"])
        weight = np.asarray(c_view["weight"])
        order = np.argsort(-weight)
        for rank, idx in enumerate(order[:250], start=1):
            event_rows.append(
                {
                    "rank_by_delayed_weight": rank,
                    "recoil_pe": float(pe[idx]),
                    "recoil_time_us": float(time_us[idx]),
                    "local_child_ara": float(local_x[idx]),
                    "delayed_membership_weight": float(weight[idx]),
                }
            )
    return result, hist_rows, event_rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    c_events = np.loadtxt(DATA / "dataBeamOnC.txt")
    ac_events = np.loadtxt(DATA / "dataBeamOnAC.txt")
    primary_c_mask = event_split(c_events, "C", SEED)
    primary_ac_mask = event_split(ac_events, "AC", SEED)
    static = build_templates()
    base_templates, native_time, native_prompt, native_delayed = static

    primary, primary_hist, event_sample = run_split(c_events, ac_events, static, SEED, True)
    split_rows: list[dict[str, object]] = []
    for salt in range(SEED, SEED + N_SPLITS):
        result, _, _ = run_split(c_events, ac_events, static, salt, False)
        split_rows.append(result)

    if not bool(primary["valid"]):
        raise RuntimeError("Primary child window is invalid")

    # Rebuild the primary calibration population curve for saved visual rows.
    c_cal = c_events[primary_c_mask]
    ac_cal = ac_events[primary_ac_mask]
    primary_templates = list(base_templates)
    primary_fit = fit_calibration(hist_time(c_cal), hist_time(ac_cal), primary_templates, CAL_FRACTION)
    params = np.asarray(primary_fit["params"], dtype=float)
    window = child_window(native_time, native_prompt, native_delayed, float(params[3]), float(params[4]))
    local_curve_rows: list[dict[str, object]] = []
    mask = (native_time >= float(window["left_time_us"])) & (native_time <= float(window["right_time_us"]))
    sample_idx = np.flatnonzero(mask)[::5]
    delayed_rate = np.asarray(window["delayed_rate"])
    for i in sample_idx:
        local_curve_rows.append(
            {
                "time_us": float(native_time[i]),
                "parent_ara": float(np.asarray(window["parent_x"])[i]),
                "local_child_ara": float(np.asarray(window["local_x"])[i]),
                "delayed_rate_peak_normalized": float(delayed_rate[i] / delayed_rate.max()),
            }
        )

    # Registered leave-one-bin-out yield robustness from T399.
    loo_rows: list[dict[str, object]] = []
    for row in read_csv(T399_LOO):
        p = float(row["prompt_yield"])
        d = float(row["delayed_yield"])
        cut = child_window(native_time, native_prompt, native_delayed, p, d)
        loo_rows.append(
            {
                "axis": row["axis"],
                "removed_bin": int(row["removed_bin"]),
                "valid": bool(cut.get("valid", False)),
                "local_mode_ara": float(cut.get("local_mode_ara", float("nan"))),
                "in_population_ridge_gate": bool(cut.get("valid", False) and 0.75 <= float(cut["local_mode_ara"]) <= 1.25),
            }
        )

    valid_loo = [row for row in loo_rows if bool(row["valid"])]
    loo_ridge_fraction = float(np.mean([bool(row["in_population_ridge_gate"]) for row in valid_loo])) if valid_loo else 0.0

    # Relative-phase control: shift prompt timing while retaining all amplitudes.
    real_error = abs(float(window["local_mode_ara"]) - 1.0)
    shift_rows: list[dict[str, object]] = []
    controls_as_good = 0
    max_shift = min(N_SHIFT, len(native_prompt) - 1)
    for shift in range(1, max_shift + 1):
        shifted = np.roll(native_prompt, shift)
        cut = child_window(native_time, shifted, native_delayed, float(params[3]), float(params[4]))
        error = abs(float(cut.get("local_mode_ara", float("nan"))) - 1.0) if bool(cut.get("valid", False)) else float("nan")
        as_good = bool(math.isfinite(error) and error <= real_error + 1e-12)
        controls_as_good += int(as_good)
        shift_rows.append({"shift_native_ns": shift, "valid": bool(cut.get("valid", False)), "ridge_error": error, "as_good_as_real": as_good})
    shift_p_upper = float((controls_as_good + 1) / (max_shift + 1))

    valid_splits = [row for row in split_rows if bool(row.get("valid", False))]
    repeated_mode_fraction = float(np.mean([0.5 <= float(row["holdout_weighted_mode"]) <= 1.5 for row in valid_splits])) if valid_splits else 0.0

    # Primary event bootstrap, holding the window and calibration fit fixed.
    c_hold = c_events[~primary_c_mask]
    c_view = event_membership(c_hold, params, primary_templates, window, native_time, True)
    local_x = np.asarray(c_view["local_x"])
    weights = np.asarray(c_view["weight"])
    bin_sensitivity_rows: list[dict[str, object]] = []
    for bin_count in (4, 6, 8, 10, 12, 16):
        edges = np.linspace(0.0, 2.0, bin_count + 1)
        values, _ = np.histogram(local_x, bins=edges, weights=weights)
        centers = (edges[:-1] + edges[1:]) / 2.0
        bin_sensitivity_rows.append(
            {
                "bin_count": bin_count,
                "weighted_mode": float(centers[int(np.argmax(values))]),
                "mode_in_broad_ridge": bool(0.5 <= float(centers[int(np.argmax(values))]) <= 1.5),
            }
        )
    grid = np.linspace(0.0, 2.0, 2001)
    for bandwidth in (0.08, 0.12, 0.16, 0.20, 0.25, 0.30):
        density = np.sum(weights[:, None] * np.exp(-0.5 * ((grid[None, :] - local_x[:, None]) / bandwidth) ** 2), axis=0)
        bin_sensitivity_rows.append(
            {
                "bin_count": f"kde_bw_{bandwidth:.2f}",
                "weighted_mode": float(grid[int(np.argmax(density))]),
                "mode_in_broad_ridge": bool(0.5 <= float(grid[int(np.argmax(density))]) <= 1.5),
            }
        )
    rng = np.random.default_rng(SEED)
    boot_rows: list[dict[str, object]] = []
    for i in range(N_BOOT):
        indices = rng.integers(0, len(local_x), len(local_x))
        metric = histogram_metrics(local_x[indices], weights[indices])
        boot_rows.append({"replicate": i, "mode": float(metric["mode"]), "mean": float(metric["mean"]), "median": float(metric["median"])})
    boot_mode_fraction = float(np.mean([0.5 <= float(row["mode"]) <= 1.5 for row in boot_rows]))
    boot_mean_ci = np.quantile([float(row["mean"]) for row in boot_rows], [0.025, 0.975]).tolist()

    population_gates = {
        "P1_ordered_objective_window": bool(float(window["left_time_us"]) < float(window["mode_time_us"]) < float(window["right_time_us"])),
        "P2_crest_near_local_ridge": bool(0.75 <= float(window["local_mode_ara"]) <= 1.25),
        "P3_leave_one_out_ridge_fraction_ge_0p80": bool(loo_ridge_fraction >= 0.80),
    }
    event_gates = {
        "I1_effective_delayed_count_ge_10": bool(float(primary["effective_delayed_holdout"]) >= 10.0),
        "I2_holdout_mode_in_broad_ridge": bool(0.5 <= float(primary["holdout_weighted_mode"]) <= 1.5),
        "I3_holdout_mean_within_0p30_of_population": bool(abs(float(primary["holdout_weighted_mean"]) - float(primary["population_local_mean"])) <= 0.30),
        "I4_repeated_split_mode_fraction_ge_0p70": bool(repeated_mode_fraction >= 0.70),
        "I5_C_median_membership_weight_gt_AC": bool(primary["C_median_weight_greater_than_AC"]),
    }
    full_reference = child_window(
        native_time,
        native_prompt,
        native_delayed,
        float(np.sum(native_prompt)),
        float(np.sum(native_delayed)),
    )
    population_supported = all(population_gates.values())
    event_supported = all(event_gates.values())
    if population_supported and event_supported:
        verdict = "NESTED POPULATION CHILD RECOVERED AND TRANSFERRED TO EVENT CANDIDATES"
    elif population_supported:
        verdict = "NESTED POPULATION CHILD RECOVERED; EVENT TRANSFER PARTIAL"
    else:
        verdict = "NESTED CHILD RIDGE NOT SUPPORTED"

    results = {
        "test": "T400",
        "date": "2026-08-17",
        "verdict": verdict,
        "protocol_sha256": sha256(PROTOCOL),
        "source": {
            "identity": "COHERENT 2022 CsI public unbinned beam-coincident/anti-coincident events and official source templates",
            "data_dir": str(DATA),
            "beam_C_sha256": sha256(DATA / "dataBeamOnC.txt"),
            "beam_AC_sha256": sha256(DATA / "dataBeamOnAC.txt"),
        },
        "coordinate": "x_C=2*(x_P-x_P(L))/(x_P(R)-x_P(L)); L is branch equality; R is delayed-rate return to D(L)",
        "primary_population": {
            "left_time_us": float(window["left_time_us"]),
            "delayed_crest_time_us": float(window["mode_time_us"]),
            "right_time_us": float(window["right_time_us"]),
            "left_parent_ara": float(window["left_parent_ara"]),
            "crest_parent_ara": float(window["mode_parent_ara"]),
            "right_parent_ara": float(window["right_parent_ara"]),
            "local_crest_ara": float(window["local_mode_ara"]),
            "local_weighted_mean": float(window["local_weighted_mean"]),
            "local_weighted_median": float(window["local_weighted_median"]),
            "local_weighted_skewness": float(window["local_weighted_skewness"]),
            "window_delayed_mass_fraction": float(window["window_delayed_mass_fraction"]),
            "loo_valid": len(valid_loo),
            "loo_ridge_fraction": loo_ridge_fraction,
            "phase_shift_controls": max_shift,
            "phase_shift_as_good": controls_as_good,
            "phase_shift_p_upper": shift_p_upper,
        },
        "full_fit_population_reference_not_primary": {
            "local_crest_ara": float(full_reference["local_mode_ara"]),
            "local_weighted_mean": float(full_reference["local_weighted_mean"]),
            "local_weighted_median": float(full_reference["local_weighted_median"]),
            "note": "Uses the saved full T398 fit and is reported only as a post-primary source-resolution comparison.",
        },
        "primary_event_transfer": primary,
        "repeated_splits": {
            "requested": N_SPLITS,
            "valid": len(valid_splits),
            "broad_ridge_mode_fraction": repeated_mode_fraction,
        },
        "event_bootstrap": {
            "replicates": N_BOOT,
            "broad_ridge_mode_fraction": boot_mode_fraction,
            "weighted_mean_ci95": [float(v) for v in boot_mean_ci],
        },
        "population_gates": population_gates,
        "event_gates": event_gates,
        "boundaries": [
            "The holdout rows are individual detector events, not neutrino flavor tags.",
            "Delayed membership is a calibration-frozen statistical weight.",
            "The result cannot identify both neutrinos from one named muon or time their birth independently.",
            "The population curve and event transfer use the same physical source; repeated deterministic splits limit but do not create a new experiment.",
        ],
    }

    write_csv(OUT / "T400_LOCAL_CHILD_CURVE.csv", local_curve_rows)
    write_csv(OUT / "T400_PRIMARY_EVENT_HISTOGRAM.csv", primary_hist)
    write_csv(OUT / "T400_PRIMARY_EVENT_SAMPLE.csv", event_sample)
    write_csv(OUT / "T400_REPEATED_SPLITS.csv", split_rows)
    write_csv(OUT / "T400_LEAVE_ONE_OUT_CHILD_WINDOWS.csv", loo_rows)
    write_csv(OUT / "T400_PHASE_SHIFT_CONTROLS.csv", shift_rows)
    write_csv(OUT / "T400_EVENT_BOOTSTRAP.csv", boot_rows)
    write_csv(OUT / "T400_EVENT_MODE_SENSITIVITY.csv", bin_sensitivity_rows)
    (OUT / "T400_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    # Static figure for the repository and visual QA.
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    ax = axes[0, 0]
    curve_x = np.array([row["local_child_ara"] for row in local_curve_rows])
    curve_y = np.array([row["delayed_rate_peak_normalized"] for row in local_curve_rows])
    ax.plot(curve_x, curve_y, color="#3267a8", lw=2.6)
    ax.axvline(1.0, color="#172033", ls="--", lw=1.5, label="local ridge 1.0")
    ax.axvline(float(window["local_mode_ara"]), color="#d97824", lw=1.8, label=f"population crest {float(window['local_mode_ara']):.3f}")
    ax.set(xlim=(0, 2), xlabel="local delayed-child ARA (0–2)", ylabel="delayed rate / peak", title="Population child window")
    ax.legend(frameon=False)

    ax = axes[0, 1]
    centers = np.array([row["bin_center"] for row in primary_hist])
    values = np.array([row["effective_delayed_weight"] for row in primary_hist])
    ax.bar(centers, values, width=0.22, color="#d7a128", edgecolor="#172033", linewidth=0.8)
    ax.axvline(1.0, color="#172033", ls="--", lw=1.5)
    ax.set(xlim=(0, 2), xlabel="frozen local child ARA", ylabel="effective delayed-event weight", title="Untouched holdout event candidates")

    ax = axes[1, 0]
    modes = [float(row["holdout_weighted_mode"]) for row in valid_splits]
    ax.hist(modes, bins=HIST_EDGES, color="#3f8c69", edgecolor="#172033", linewidth=0.8)
    ax.axvspan(0.5, 1.5, color="#d7a128", alpha=0.15, label="broad event ridge gate")
    ax.axvline(1.0, color="#172033", ls="--", lw=1.5)
    ax.set(xlim=(0, 2), xlabel="holdout mode across deterministic splits", ylabel="split count", title="Population-to-event transfer robustness")
    ax.legend(frameon=False)

    ax = axes[1, 1]
    labels = ["Population crest", "Holdout mode", "Holdout mean", "Holdout median"]
    vals = [float(window["local_mode_ara"]), float(primary["holdout_weighted_mode"]), float(primary["holdout_weighted_mean"]), float(primary["holdout_weighted_median"])]
    ax.barh(labels, vals, color=["#3267a8", "#d97824", "#d7a128", "#3f8c69"], edgecolor="#172033", linewidth=0.8)
    ax.axvline(1.0, color="#172033", ls="--", lw=1.5)
    ax.set(xlim=(0, 2), xlabel="local child ARA", title="Population and event landmarks")
    for y, value in enumerate(vals):
        ax.text(value + 0.03, y, f"{value:.3f}", va="center", fontsize=9)

    fig.suptitle("T400 — Nested delayed-child window: population to event", fontsize=18, fontweight="bold")
    fig.savefig(OUT / "T400_NESTED_CHILD_WINDOW.png", dpi=180)
    plt.close(fig)

    print(json.dumps({
        "verdict": verdict,
        "population": results["primary_population"],
        "event": primary,
        "repeated_splits": results["repeated_splits"],
        "event_bootstrap": results["event_bootstrap"],
        "population_gates": population_gates,
        "event_gates": event_gates,
    }, indent=2))


if __name__ == "__main__":
    main()

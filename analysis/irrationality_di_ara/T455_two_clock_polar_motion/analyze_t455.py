"""T455: scale-invariant two-clock / geographic-polar-motion test.

The protocol in FROZEN_PROTOCOL.md was written before this program was run.
All prediction rows are causal and all splits are chronological.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "eopc04_20u24.1962-now.csv"
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

SCALES = (1, 7, 30, 90)
HORIZONS = (1, 2, 4)
RIDGE_ALPHA = 1.0
RNG = np.random.default_rng(455)
N_BOOT = 1000

CLOCK_FEATURES = ["lod", "lod_lag1", "lod_lag2", "lod_slope", "u_clock"]
RAW_POLE_FEATURES = ["pole_x", "pole_y", "dpx", "dpy", "pole_radius"]
DIARA_FEATURES = [
    "pole_amount_ara",
    "pole_traversal_ara",
    "pole_log_ratio",
    "pole_turn_rad",
    "pole_displacement",
]
POLE_FEATURES = RAW_POLE_FEATURES + DIARA_FEATURES
MODEL_FEATURES = {
    "clock_only": CLOCK_FEATURES,
    "clock_raw_pole": CLOCK_FEATURES + RAW_POLE_FEATURES,
    "clock_pole_diara": CLOCK_FEATURES + DIARA_FEATURES,
    "full_child": CLOCK_FEATURES + RAW_POLE_FEATURES + DIARA_FEATURES,
}


@dataclass
class RidgeModel:
    features: list[str]
    mean: np.ndarray
    std: np.ndarray
    y_mean: float
    y_std: float
    coef: np.ndarray

    def predict_frame(self, frame: pd.DataFrame) -> np.ndarray:
        x = frame[self.features].to_numpy(float)
        return self.y_mean + ((x - self.mean) / self.std) @ self.coef


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_daily() -> pd.DataFrame:
    data = pd.read_csv(SOURCE, sep=";")
    data["date"] = pd.to_datetime(
        {"year": data["Year"], "month": data["Month"], "day": data["Day"]}
    )
    data = data.rename(
        columns={
            "x_pole": "pole_x",
            "y_pole": "pole_y",
            "x_rate": "pole_x_rate",
            "y_rate": "pole_y_rate",
            "UT1-UTC": "ut1_utc",
            "LOD": "lod",
        }
    )
    keep = [
        "date",
        "MJD",
        "pole_x",
        "pole_y",
        "pole_x_rate",
        "pole_y_rate",
        "ut1_utc",
        "lod",
        "sigma_x_pole",
        "sigma_y_pole",
        "sigma_UT1-UTC",
        "sigma_LOD",
    ]
    data = data[keep].copy()
    data = data[data.date >= "1984-01-01"].sort_values("date").reset_index(drop=True)
    required = ["pole_x", "pole_y", "lod"]
    data = data.dropna(subset=required).reset_index(drop=True)
    return data


def wrap_pi(angle: np.ndarray) -> np.ndarray:
    return (angle + np.pi) % (2 * np.pi) - np.pi


def split_from_target_date(date: pd.Series) -> pd.Series:
    out = pd.Series(index=date.index, dtype="object")
    out[date <= pd.Timestamp("2008-12-31")] = "development"
    out[(date >= pd.Timestamp("2009-01-01")) & (date <= pd.Timestamp("2016-12-31"))] = "validation"
    out[date >= pd.Timestamp("2017-01-01")] = "holdout"
    return out


def build_scale(daily: pd.DataFrame, scale_days: int) -> pd.DataFrame:
    origin = pd.Timestamp("1984-01-01")
    work = daily.copy()
    work["window_id"] = ((work.date - origin).dt.days // scale_days).astype(int)
    grouped = work.groupby("window_id", sort=True)
    windows = grouped.agg(
        start_date=("date", "min"),
        end_date=("date", "max"),
        n_days=("date", "size"),
        lod=("lod", "mean"),
        ut1_utc=("ut1_utc", "mean"),
        pole_x=("pole_x", "mean"),
        pole_y=("pole_y", "mean"),
        pole_x_rate=("pole_x_rate", "mean"),
        pole_y_rate=("pole_y_rate", "mean"),
        sigma_lod=("sigma_LOD", "mean"),
        sigma_pole_x=("sigma_x_pole", "mean"),
        sigma_pole_y=("sigma_y_pole", "mean"),
    ).reset_index()
    windows = windows[windows.n_days == scale_days].copy().reset_index(drop=True)
    windows["scale_days"] = scale_days
    windows["year"] = windows.end_date.dt.year

    # Exact two-clock relation: Earth rotation-day length divided by SI atomic day.
    windows["s_clock"] = (86400.0 + windows.lod) / 86400.0
    windows["u_clock"] = np.log(windows.s_clock)
    windows["clock_ara"] = 2.0 * windows.s_clock / (1.0 + windows.s_clock)
    windows["clock_ridge_nano"] = (windows.clock_ara - 1.0) * 1e9

    windows["lod_lag1"] = windows.lod.shift(1)
    windows["lod_lag2"] = windows.lod.shift(2)
    windows["lod_slope"] = windows.lod - windows.lod_lag1
    windows["dpx"] = windows.pole_x.diff()
    windows["dpy"] = windows.pole_y.diff()
    windows["pole_radius"] = np.hypot(windows.pole_x, windows.pole_y)
    windows["pole_displacement"] = np.hypot(windows.dpx, windows.dpy)
    windows["pole_heading"] = np.arctan2(windows.dpy, windows.dpx)
    eps = 1e-15
    windows["pole_log_ratio"] = np.log(
        np.maximum(windows.pole_displacement, eps)
        / np.maximum(windows.pole_displacement.shift(1), eps)
    )
    windows["pole_amount_ara"] = 1.0 + np.tanh(windows.pole_log_ratio / 2.0)
    windows["pole_turn_rad"] = wrap_pi(
        (windows.pole_heading - windows.pole_heading.shift(1)).to_numpy(float)
    )
    windows["pole_traversal_ara"] = 1.0 + windows.pole_turn_rad / np.pi
    return windows


def fit_ridge(frame: pd.DataFrame, features: list[str], target: str) -> RidgeModel:
    x = frame[features].to_numpy(float)
    y = frame[target].to_numpy(float)
    mean = x.mean(axis=0)
    std = x.std(axis=0, ddof=0)
    std[std < 1e-15] = 1.0
    xs = (x - mean) / std
    y_mean = float(y.mean())
    y_std = float(y.std(ddof=0)) or 1.0
    coef = np.linalg.solve(xs.T @ xs + RIDGE_ALPHA * np.eye(xs.shape[1]), xs.T @ (y - y_mean))
    return RidgeModel(features, mean, std, y_mean, y_std, coef)


def metric_row(actual: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    err = pred - actual
    denom = np.sum((actual - actual.mean()) ** 2)
    return {
        "n": int(len(actual)),
        "mae": float(np.mean(np.abs(err))),
        "rmse": float(np.sqrt(np.mean(err**2))),
        "bias": float(np.mean(err)),
        "r2": float(1.0 - np.sum(err**2) / denom) if denom > 0 else np.nan,
    }


def year_block_permutation(frame: pd.DataFrame, columns: list[str], seed: int) -> pd.DataFrame:
    result = frame.copy()
    years = list(dict.fromkeys(frame.end_date.dt.year.tolist()))
    shuffled = years.copy()
    np.random.default_rng(seed).shuffle(shuffled)
    blocks = [frame.loc[frame.end_date.dt.year == year, columns].to_numpy(float) for year in shuffled]
    values = np.concatenate(blocks, axis=0)
    # Leap years make source and destination block lengths differ. The concatenated
    # record still has exactly the same row count and preserves within-year order.
    result.loc[:, columns] = values[: len(result)]
    return result


def block_bootstrap_gain(gain: np.ndarray, block_size: int) -> tuple[float, float, float]:
    gain = np.asarray(gain, float)
    blocks = [gain[i : i + block_size] for i in range(0, len(gain), block_size)]
    draws = []
    for _ in range(N_BOOT):
        chosen = RNG.integers(0, len(blocks), len(blocks))
        sample = np.concatenate([blocks[i] for i in chosen])[: len(gain)]
        draws.append(float(np.mean(sample)))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975)), float(np.mean(np.asarray(draws) > 0))


def run_scale_models(windows_by_scale: dict[int, pd.DataFrame]):
    metrics: list[dict] = []
    predictions: list[pd.DataFrame] = []
    coefficients: list[dict] = []
    controls: list[dict] = []
    bootstraps: list[dict] = []
    fitted: dict[tuple[int, int, str], RidgeModel] = {}

    for scale, base in windows_by_scale.items():
        for horizon in HORIZONS:
            frame = base.copy()
            frame["target_lod"] = frame.lod.shift(-horizon)
            frame["target_end_date"] = frame.end_date.shift(-horizon)
            frame["split"] = split_from_target_date(frame.target_end_date)
            required = sorted(set(CLOCK_FEATURES + POLE_FEATURES + ["target_lod"]))
            frame = frame.dropna(subset=required).reset_index(drop=True)
            dev = frame[frame.split == "development"]
            if len(dev) < 20:
                continue

            out = frame[["end_date", "target_end_date", "split", "scale_days", "lod", "target_lod"]].copy()
            out["horizon_windows"] = horizon
            out["pred_persistence"] = frame.lod.to_numpy(float)
            for model_name, features in MODEL_FEATURES.items():
                model = fit_ridge(dev, features, "target_lod")
                fitted[(scale, horizon, model_name)] = model
                out[f"pred_{model_name}"] = model.predict_frame(frame)
                for feature, beta in zip(features, model.coef / model.y_std):
                    coefficients.append(
                        {
                            "scale_days": scale,
                            "horizon_windows": horizon,
                            "model": model_name,
                            "feature": feature,
                            "standardized_beta": float(beta),
                        }
                    )

            for split in ("development", "validation", "holdout"):
                mask = out.split == split
                actual = out.loc[mask, "target_lod"].to_numpy(float)
                if len(actual) == 0:
                    continue
                for model_name in ["persistence", *MODEL_FEATURES.keys()]:
                    pred = out.loc[mask, f"pred_{model_name}"].to_numpy(float)
                    row = metric_row(actual, pred)
                    row.update(
                        {
                            "scale_days": scale,
                            "horizon_windows": horizon,
                            "horizon_days": scale * horizon,
                            "split": split,
                            "model": model_name,
                        }
                    )
                    metrics.append(row)

            # Frozen false-time controls use each real fitted child model's
            # coefficients. The full-child gate remains separately identified.
            control_frames: dict[str, pd.DataFrame] = {}
            shifted = frame.copy()
            shifted.loc[:, POLE_FEATURES] = shifted[POLE_FEATURES].shift(max(1, round(365 / scale)))
            control_frames["pole_shift_365d"] = shifted
            reversed_pole = frame.copy()
            reversed_pole.loc[:, POLE_FEATURES] = reversed_pole[POLE_FEATURES].iloc[::-1].to_numpy()
            control_frames["pole_reversed_chronology"] = reversed_pole
            reflected = frame.copy()
            reflected["pole_traversal_ara"] = 2.0 - reflected.pole_traversal_ara
            reflected["pole_turn_rad"] = -reflected.pole_turn_rad
            control_frames["traversal_reflected"] = reflected
            control_frames["pole_year_blocks_permuted"] = year_block_permutation(frame, POLE_FEATURES, 455 + scale + horizon)

            hold_mask = frame.split == "holdout"
            clock_pred = out.loc[hold_mask, "pred_clock_only"].to_numpy(float)
            actual = out.loc[hold_mask, "target_lod"].to_numpy(float)
            clock_metric = metric_row(actual, clock_pred)
            for candidate in ("clock_raw_pole", "clock_pole_diara", "full_child"):
                candidate_model = fitted[(scale, horizon, candidate)]
                real_pred = out.loc[hold_mask, f"pred_{candidate}"].to_numpy(float)
                real_metric = metric_row(actual, real_pred)
                controls.append(
                    {
                        "scale_days": scale,
                        "horizon_windows": horizon,
                        "candidate_model": candidate,
                        "control": "real_pole_child",
                        **real_metric,
                        "improvement_vs_clock_pct": 100 * (clock_metric["mae"] - real_metric["mae"]) / clock_metric["mae"],
                    }
                )
                for control_name, cf in control_frames.items():
                    valid = hold_mask.to_numpy() & cf[candidate_model.features].notna().all(axis=1).to_numpy()
                    ctrl_actual = frame.loc[valid, "target_lod"].to_numpy(float)
                    ctrl_pred = candidate_model.predict_frame(cf.loc[valid])
                    ctrl_clock = fitted[(scale, horizon, "clock_only")].predict_frame(frame.loc[valid])
                    ctrl_metric = metric_row(ctrl_actual, ctrl_pred)
                    clock_same = metric_row(ctrl_actual, ctrl_clock)
                    controls.append(
                        {
                            "scale_days": scale,
                            "horizon_windows": horizon,
                            "candidate_model": candidate,
                            "control": control_name,
                            **ctrl_metric,
                            "improvement_vs_clock_pct": 100 * (clock_same["mae"] - ctrl_metric["mae"]) / clock_same["mae"],
                        }
                    )

            for candidate in ("clock_raw_pole", "clock_pole_diara", "full_child"):
                candidate_pred = out.loc[hold_mask, f"pred_{candidate}"].to_numpy(float)
                gain = np.abs(actual - clock_pred) - np.abs(actual - candidate_pred)
                lo, hi, p = block_bootstrap_gain(gain, max(1, round(365 / scale)))
                bootstraps.append(
                    {
                        "scale_days": scale,
                        "horizon_windows": horizon,
                        "candidate_model": candidate,
                        "mean_mae_gain_seconds": float(np.mean(gain)),
                        "ci_low": lo,
                        "ci_high": hi,
                        "p_gain_positive": p,
                        "block_windows": max(1, round(365 / scale)),
                        "resamples": N_BOOT,
                    }
                )
            predictions.append(out)

    return (
        pd.DataFrame(metrics),
        pd.concat(predictions, ignore_index=True),
        pd.DataFrame(coefficients),
        pd.DataFrame(controls),
        pd.DataFrame(bootstraps),
        fitted,
    )


def coefficient_similarity(coefficients: pd.DataFrame) -> pd.DataFrame:
    sub = coefficients[
        (coefficients.horizon_windows == 1)
        & (coefficients.model == "full_child")
        & coefficients.feature.isin(POLE_FEATURES)
    ]
    vectors = {
        scale: group.set_index("feature").reindex(POLE_FEATURES).standardized_beta.to_numpy(float)
        for scale, group in sub.groupby("scale_days")
    }
    rows = []
    for a in SCALES:
        for b in SCALES:
            va, vb = vectors[a], vectors[b]
            denom = np.linalg.norm(va) * np.linalg.norm(vb)
            rows.append({"scale_a": a, "scale_b": b, "cosine_similarity": float(va @ vb / denom) if denom else np.nan})
    return pd.DataFrame(rows)


def quadrant_occupancy(windows_by_scale: dict[int, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for scale, frame in windows_by_scale.items():
        work = frame.dropna(subset=["pole_amount_ara", "pole_traversal_ara"]).copy()
        work["split"] = split_from_target_date(work.end_date)
        work["quadrant"] = np.select(
            [
                (work.pole_amount_ara < 1) & (work.pole_traversal_ara >= 1),
                (work.pole_amount_ara >= 1) & (work.pole_traversal_ara >= 1),
                (work.pole_amount_ara < 1) & (work.pole_traversal_ara < 1),
            ],
            ["Ba", "Ab", "bA"],
            default="aB",
        )
        for (split, quadrant), group in work.groupby(["split", "quadrant"]):
            total = int((work.split == split).sum())
            rows.append(
                {
                    "scale_days": scale,
                    "split": split,
                    "quadrant": quadrant,
                    "count": int(len(group)),
                    "fraction": float(len(group) / total),
                }
            )
    return pd.DataFrame(rows)


def geometry_summary(windows_by_scale: dict[int, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for scale, frame in windows_by_scale.items():
        work = frame.dropna(subset=["pole_amount_ara", "pole_traversal_ara", "pole_turn_rad"]).copy()
        work["split"] = split_from_target_date(work.end_date)
        for split, group in work.groupby("split"):
            median_turn = float(group.pole_turn_rad.median())
            rows.append(
                {
                    "scale_days": scale,
                    "split": split,
                    "n": int(len(group)),
                    "median_amount_ara": float(group.pole_amount_ara.median()),
                    "median_traversal_ara": float(group.pole_traversal_ara.median()),
                    "median_turn_rad": median_turn,
                    "negative_turn_fraction": float((group.pole_turn_rad < 0).mean()),
                    "implied_cycle_days_from_median_turn": float(2 * np.pi * scale / abs(median_turn)) if abs(median_turn) > 1e-12 else np.nan,
                    "median_clock_ara": float(group.clock_ara.median()),
                    "median_clock_ridge_nano": float(group.clock_ridge_nano.median()),
                }
            )
    return pd.DataFrame(rows)


def polar_spectrum(daily: pd.DataFrame) -> pd.DataFrame:
    """Model-free periodogram of the complex geographic-pole path."""
    t = np.arange(len(daily), dtype=float)
    x = daily.pole_x.to_numpy(float)
    y = daily.pole_y.to_numpy(float)
    x = x - np.polyval(np.polyfit(t, x, 1), t)
    y = y - np.polyval(np.polyfit(t, y, 1), t)
    z = x + 1j * y
    freq = np.fft.fftfreq(len(z), d=1.0)
    power = np.abs(np.fft.fft(z)) ** 2
    positive = freq > 0
    periods = np.full(freq.shape, np.inf, dtype=float)
    periods[positive] = 1.0 / freq[positive]
    mask = positive & (periods >= 100) & (periods <= 1000)
    candidates = pd.DataFrame({"period_days": periods[mask], "power": power[mask]}).sort_values("power", ascending=False)
    selected = []
    for _, row in candidates.iterrows():
        if all(abs(row.period_days - item["period_days"]) >= 20 for item in selected):
            selected.append({"rank": len(selected) + 1, "period_days": float(row.period_days), "relative_power": float(row.power / candidates.power.max())})
        if len(selected) == 6:
            break
    return pd.DataFrame(selected)


def leave_one_scale_out(windows_by_scale: dict[int, pd.DataFrame]) -> pd.DataFrame:
    prepared: dict[int, dict[str, tuple[np.ndarray, np.ndarray, float]]] = {}
    for scale, base in windows_by_scale.items():
        frame = base.copy()
        frame["target_lod"] = frame.lod.shift(-1)
        frame["target_end_date"] = frame.end_date.shift(-1)
        frame["split"] = split_from_target_date(frame.target_end_date)
        frame = frame.dropna(subset=sorted(set(CLOCK_FEATURES + POLE_FEATURES + ["target_lod"]))).reset_index(drop=True)
        prepared[scale] = {"frame": frame}

    rows = []
    for omitted in SCALES:
        for model_name in ("clock_only", "full_child"):
            features = MODEL_FEATURES[model_name]
            train_x, train_y = [], []
            omitted_hold = None
            omitted_scaler = None
            for scale, item in prepared.items():
                frame = item["frame"]
                dev = frame[frame.split == "development"]
                mean = dev[features].mean().to_numpy(float)
                std = dev[features].std(ddof=0).to_numpy(float).copy()
                std[std < 1e-15] = 1.0
                y_mean = float(dev.target_lod.mean())
                y_std = float(dev.target_lod.std(ddof=0)) or 1.0
                if scale == omitted:
                    hold = frame[frame.split == "holdout"]
                    omitted_hold = ((hold[features].to_numpy(float) - mean) / std, (hold.target_lod.to_numpy(float) - y_mean) / y_std)
                    omitted_scaler = (y_mean, y_std)
                else:
                    train_x.append((dev[features].to_numpy(float) - mean) / std)
                    train_y.append((dev.target_lod.to_numpy(float) - y_mean) / y_std)
            x = np.concatenate(train_x)
            y = np.concatenate(train_y)
            coef = np.linalg.solve(x.T @ x + RIDGE_ALPHA * np.eye(x.shape[1]), x.T @ y)
            xh, yh = omitted_hold
            pred = xh @ coef
            row = metric_row(yh, pred)
            row.update({"omitted_scale_days": omitted, "model": model_name, "target_unit": "omitted-scale development SD"})
            rows.append(row)
    return pd.DataFrame(rows)


def posthoc_seasonal_audit(windows_by_scale: dict[int, pd.DataFrame]) -> pd.DataFrame:
    """Post-result diagnostic: does Di-ARA add beyond calendar seasonality?"""
    rows = []
    seasonal = ["season_sin1", "season_cos1", "season_sin2", "season_cos2"]
    for scale, base in windows_by_scale.items():
        for horizon in HORIZONS:
            frame = base.copy()
            day = frame.end_date.dt.dayofyear.to_numpy(float)
            phase = 2 * np.pi * (day - 1.0) / 365.2425
            frame["season_sin1"] = np.sin(phase)
            frame["season_cos1"] = np.cos(phase)
            frame["season_sin2"] = np.sin(2 * phase)
            frame["season_cos2"] = np.cos(2 * phase)
            frame["target_lod"] = frame.lod.shift(-horizon)
            frame["target_end_date"] = frame.end_date.shift(-horizon)
            frame["split"] = split_from_target_date(frame.target_end_date)
            baseline_features = CLOCK_FEATURES + seasonal
            candidate_features = baseline_features + DIARA_FEATURES
            frame = frame.dropna(subset=sorted(set(candidate_features + ["target_lod"]))).reset_index(drop=True)
            dev = frame[frame.split == "development"]
            hold = frame[frame.split == "holdout"]
            baseline = fit_ridge(dev, baseline_features, "target_lod")
            candidate = fit_ridge(dev, candidate_features, "target_lod")
            actual = hold.target_lod.to_numpy(float)
            pred_base = baseline.predict_frame(hold)
            pred_candidate = candidate.predict_frame(hold)
            base_metric = metric_row(actual, pred_base)
            candidate_metric = metric_row(actual, pred_candidate)
            gain = np.abs(actual - pred_base) - np.abs(actual - pred_candidate)
            lo, hi, p = block_bootstrap_gain(gain, max(1, round(365 / scale)))
            rows.append(
                {
                    "scale_days": scale,
                    "horizon_windows": horizon,
                    "horizon_days": scale * horizon,
                    "clock_season_mae": base_metric["mae"],
                    "clock_season_diara_mae": candidate_metric["mae"],
                    "diara_improvement_over_season_pct": 100 * (base_metric["mae"] - candidate_metric["mae"]) / base_metric["mae"],
                    "mean_mae_gain_seconds": float(np.mean(gain)),
                    "ci_low": lo,
                    "ci_high": hi,
                    "p_gain_positive": p,
                    "n": int(len(hold)),
                    "status": "post-result diagnostic; not a frozen gate",
                }
            )
    return pd.DataFrame(rows)


def create_gates(metrics: pd.DataFrame, controls: pd.DataFrame, transfer: pd.DataFrame, windows: pd.DataFrame) -> pd.DataFrame:
    hold = metrics[(metrics.split == "holdout") & (metrics.horizon_windows == 1)]
    pivot = hold.pivot(index="scale_days", columns="model", values="mae")
    improvement = 100 * (pivot.clock_only - pivot.full_child) / pivot.clock_only
    g1_count = int((improvement > 0).sum())
    g2_value = float(improvement.median())
    child_models = ["clock_raw_pole", "clock_pole_diara", "full_child"]
    g3_count = int((pivot[child_models].min(axis=1) < pivot.persistence).sum())

    c = controls[
        (controls.horizon_windows == 1) & (controls.candidate_model == "full_child")
    ].pivot(index="scale_days", columns="control", values="improvement_vs_clock_pct")
    real_median = float(c.real_pole_child.median())
    false_max_median = float(c.drop(columns="real_pole_child").median().max())

    t = transfer.pivot(index="omitted_scale_days", columns="model", values="mae")
    transfer_improvement = 100 * (t.clock_only - t.full_child) / t.clock_only
    g5_count = int((transfer_improvement > 0).sum())
    max_ridge = float(np.max(np.abs(windows.clock_ara - 1.0)))
    rows = [
        ("G1", "Full child improves one-window holdout MAE at >=3/4 grains", g1_count, ">=3", g1_count >= 3),
        ("G2", "Median one-window improvement across grains is positive", g2_value, ">0%", g2_value > 0),
        ("G3", "At least one child model beats persistence at every grain", g3_count, "4/4", g3_count == 4),
        ("G4", "Real child median gain exceeds every false-time/control median", real_median - false_max_median, ">0 percentage points", real_median > false_max_median),
        ("G5", "Leave-one-grain-out full child improves at >=3/4 omitted grains", g5_count, ">=3", g5_count >= 3),
        ("G6", "Exact clock ARA remains physically near ridge without display rescaling", max_ridge, "<1e-6 from ridge", max_ridge < 1e-6),
    ]
    return pd.DataFrame(rows, columns=["gate", "statement", "observed", "threshold", "passed"])


def main() -> None:
    daily = load_daily()
    windows_by_scale = {scale: build_scale(daily, scale) for scale in SCALES}
    all_windows = pd.concat(windows_by_scale.values(), ignore_index=True)
    metrics, predictions, coefficients, controls, bootstraps, _ = run_scale_models(windows_by_scale)
    similarities = coefficient_similarity(coefficients)
    quadrants = quadrant_occupancy(windows_by_scale)
    geometry = geometry_summary(windows_by_scale)
    spectrum = polar_spectrum(daily)
    transfer = leave_one_scale_out(windows_by_scale)
    seasonal_audit = posthoc_seasonal_audit(windows_by_scale)
    gates = create_gates(metrics, controls, transfer, all_windows)

    hold = metrics[(metrics.split == "holdout") & (metrics.horizon_windows == 1)]
    pivot = hold.pivot(index="scale_days", columns="model", values="mae")
    improvements = 100 * (pivot.clock_only - pivot.full_child) / pivot.clock_only
    transfer_pivot = transfer.pivot(index="omitted_scale_days", columns="model", values="mae")
    transfer_improvements = 100 * (transfer_pivot.clock_only - transfer_pivot.full_child) / transfer_pivot.clock_only
    result = {
        "test": "T455",
        "frozen_before_results": True,
        "source_sha256": sha256(SOURCE),
        "source_rows_1984_onward": int(len(daily)),
        "source_start": str(daily.date.min().date()),
        "source_end": str(daily.date.max().date()),
        "scales_days": list(SCALES),
        "horizons_windows": list(HORIZONS),
        "one_window_holdout_full_vs_clock_improvement_pct": {str(int(k)): float(v) for k, v in improvements.items()},
        "median_one_window_improvement_pct": float(improvements.median()),
        "positive_scales": int((improvements > 0).sum()),
        "leave_one_scale_out_improvement_pct": {str(int(k)): float(v) for k, v in transfer_improvements.items()},
        "positive_transfer_scales": int((transfer_improvements > 0).sum()),
        "max_abs_exact_clock_ara_from_ridge": float(np.max(np.abs(all_windows.clock_ara - 1.0))),
        "clock_ara_min": float(all_windows.clock_ara.min()),
        "clock_ara_max": float(all_windows.clock_ara.max()),
        "gates_passed": int(gates.passed.sum()),
        "gates_total": int(len(gates)),
    }
    if result["positive_scales"] >= 3 and result["median_one_window_improvement_pct"] > 0:
        result["assessment"] = "The geographic-pole child adds prospective Earth-clock information across most declared grains. Control and transfer results determine whether that structure is scale-transportable rather than local correlation."
    else:
        result["assessment"] = "The geographic-pole child does not add stable prospective Earth-clock information across the declared grains, even if descriptive geometry is visible."

    daily.to_csv(RESULTS / "T455_DAILY_IERS_1984_NOW.csv", index=False)
    all_windows.to_csv(RESULTS / "T455_SCALE_WINDOWS.csv", index=False)
    metrics.to_csv(RESULTS / "T455_FORECAST_METRICS.csv", index=False)
    predictions.to_csv(RESULTS / "T455_FORECAST_LEDGER.csv", index=False)
    coefficients.to_csv(RESULTS / "T455_STANDARDIZED_COEFFICIENTS.csv", index=False)
    similarities.to_csv(RESULTS / "T455_COEFFICIENT_SIMILARITY.csv", index=False)
    controls.to_csv(RESULTS / "T455_FALSE_TIME_CONTROLS.csv", index=False)
    bootstraps.to_csv(RESULTS / "T455_BLOCK_BOOTSTRAP.csv", index=False)
    quadrants.to_csv(RESULTS / "T455_QUADRANT_OCCUPANCY.csv", index=False)
    geometry.to_csv(RESULTS / "T455_SCALE_GEOMETRY.csv", index=False)
    spectrum.to_csv(RESULTS / "T455_POLAR_SPECTRUM.csv", index=False)
    transfer.to_csv(RESULTS / "T455_LEAVE_ONE_SCALE_OUT.csv", index=False)
    seasonal_audit.to_csv(RESULTS / "T455_POSTHOC_SEASONAL_AUDIT.csv", index=False)
    gates.to_csv(RESULTS / "T455_FROZEN_GATES.csv", index=False)
    (RESULTS / "T455_RESULT.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

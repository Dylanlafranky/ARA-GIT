#!/usr/bin/env python3
"""
Strict-causal ARA forecast comparison against stronger local proxy baselines.

This is NOT an operational archive benchmark. It compares the repo's current
ARA layered operator against:
  - persistence
  - period/seasonal naive
  - harmonic clock regression
  - causal lag+harmonic ridge
  - home_ar from ara_framework.run_forecast

Operational standards such as SWPC, IRI/NMME, Sea Ice Outlook, FluSight, and
clinical ECG/CGM benchmarks need archived forecast submissions or task-specific
data. This script marks those separately in the result markdown.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd
import requests
import urllib3

import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import ara_framework as F  # noqa: E402

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OUT_JSON = os.path.join(HERE, "ara_forecast_standard_baseline_comparison_result.json")
OUT_MD = os.path.join(HERE, "ARA_FORECAST_STANDARD_BASELINE_COMPARISON_RESULT.md")
OUT_VIZ_JS = os.path.join(HERE, "ara_vs_standard_forecast_viz_data.js")
PHI = F.PHI

INPUT_COST_COMPARISON = [
    {
        "system": "Solar / sunspots",
        "ara_inputs": "Monthly sunspot number only in this local stack.",
        "ara_input_count": "1 observed monthly index.",
        "standard_method": "NOAA/SWPC solar-cycle progression: statistical/cycle-curve product plus expert/panel forecasting, not a deep ML model.",
        "standard_inputs": "Sunspot number, F10.7, solar-cycle progression, expert/panel curve forecasts and uncertainty bands.",
        "standard_input_count": "2 core public indices plus historical cycle archive, cycle-fit machinery, uncertainty bands, and panel/expert maintenance.",
        "standard_compute": "Low direct compute; moderate operational burden because the product is maintained, validated, and expert-reviewed.",
        "standard_cost": "Public data/products are free to consume; producing the official product is an institutional/moderate staff burden rather than a large HPC burden.",
        "comparison_status": "Local proxy only. SWPC/panel archive benchmark still pending.",
    },
    {
        "system": "ENSO / NINO3.4",
        "ara_inputs": "NINO3.4 alone, or NINO3.4 + SOI + east/west WWV feeder series.",
        "ara_input_count": "1 index for self-run, 4 observed indices for feeder-run.",
        "standard_method": "IRI/CPC plume and NMME/CFSv2-style seasonal forecasting: coupled dynamical ensembles plus statistical models; some ML exists but is not the core operational baseline.",
        "standard_inputs": "SST fields, subsurface ocean heat, winds, pressure, coupled ocean-atmosphere initial states, ensemble dynamical/statistical models.",
        "standard_input_count": "Hundreds to millions of gridded state variables depending on model: ocean/atmosphere/land fields, multiple ensemble members, and many variables at daily/6-hourly/monthly cadence.",
        "standard_compute": "High. Coupled climate ensembles and data assimilation require institutional HPC; statistical plume members are cheaper.",
        "standard_cost": "Public forecast products are free to view; producing NMME/CFSv2-class forecasts is high-cost institutional modelling/HPC.",
        "comparison_status": "Local proxy only. IRI/NMME/CFSv2 hindcast archive comparison still pending.",
    },
    {
        "system": "QBO 30mb",
        "ara_inputs": "Monthly QBO 30mb wind index only in the self-forecast stack.",
        "ara_input_count": "1 observed monthly index.",
        "standard_method": "Seasonal/dynamical atmospheric models plus oscillator/statistical baselines; not usually a single public ML leaderboard.",
        "standard_inputs": "Vertical wind profiles, stratospheric state, tropical wave forcing, seasonal/dynamical forecast models, level-specific hindcast scoring.",
        "standard_input_count": "Many pressure levels and global atmospheric state fields if using seasonal models; 1 index if using a simple oscillator baseline.",
        "standard_compute": "Low for oscillator/statistical baselines; moderate-high for seasonal Earth-system models.",
        "standard_cost": "Public index data are free; operational dynamical model production is institutional/moderate-high.",
        "comparison_status": "Local proxy only. Published/operational QBO hindcast comparison still pending.",
    },
    {
        "system": "Arctic sea ice",
        "ara_inputs": "Monthly Arctic sea-ice extent only.",
        "ara_input_count": "1 observed monthly index.",
        "standard_method": "Sea Ice Outlook style ensemble of dynamical, statistical, heuristic, and some ML methods.",
        "standard_inputs": "Satellite extent/concentration, ocean/ice state, weather/climate forcing, statistical and dynamical ensemble submissions.",
        "standard_input_count": "1 index for simple statistical methods; gridded satellite concentration/extent plus ocean-atmosphere-ice fields for dynamical/ML systems.",
        "standard_compute": "Low for extent trend/statistical models; moderate-high for coupled sea-ice/ocean/atmosphere models; ML training can be moderate-high but inference cheap.",
        "standard_cost": "Public data are free; operational/dynamical modelling cost is moderate-high and multi-team.",
        "comparison_status": "Local proxy only. Sea Ice Outlook September-submission comparison still pending.",
    },
    {
        "system": "Influenza / ILINet",
        "ara_inputs": "National weekly ILINet/WILI series only.",
        "ara_input_count": "1 observed weekly national surveillance series.",
        "standard_method": "CDC FluSight forecast-hub ensemble of many submitted statistical, mechanistic, ensemble, and ML models.",
        "standard_inputs": "FluSight-style targets, hospital/ED/ILI surveillance, jurisdictional data, probabilistic quantiles/intervals, ensemble evaluation.",
        "standard_input_count": "At minimum weekly target by jurisdiction; many teams add ED, hospitalization, lab, mobility, weather, demographics, or mechanistic state variables.",
        "standard_compute": "Low for ARIMA/trend models; moderate for mechanistic and ensemble systems; some submitted ML/deep models have higher training cost.",
        "standard_cost": "Public surveillance data are free; production model cost is moderate, with forecast-hub maintenance and WIS/relative-WIS scoring.",
        "comparison_status": "Local proxy only. FluSight forecast-hub WIS/relative-WIS benchmark still pending.",
    },
    {
        "system": "Retail holiday cycle",
        "ara_inputs": "FRED RSXFSN not-seasonally-adjusted retail sales transformed into a causal trailing-12-month cycle index.",
        "ara_input_count": "1 monthly retail series after local cycle transform.",
        "standard_method": "X-13ARIMA-SEATS / ARIMA / ETS style statistical seasonal adjustment and demand forecasting; business systems often add ML/covariates.",
        "standard_inputs": "Retail sales plus seasonal adjustment, revisions, ARIMA/ETS/X-13, often promotions, prices, inventory and macro covariates.",
        "standard_input_count": "1 official series for X-13-style adjustment; tens to thousands of product/location/promo/covariate fields in business demand forecasting.",
        "standard_compute": "Low for official X-13/ARIMA on one series; moderate-high for SKU/store-scale ML demand systems.",
        "standard_cost": "Public macro data are free; business-grade demand forecasts can be moderate-high depending on covariate systems.",
        "comparison_status": "Local proxy only. Full X-13/ARIMA/ETS raw-sales comparison still pending.",
    },
    {
        "system": "CGM glucose",
        "ara_inputs": "CGM series only in the current self-forecast.",
        "ara_input_count": "1 glucose time series in the self-run.",
        "standard_method": "Subject-specific physiological/statistical/ML glucose prediction; clinical products use validated medical workflows.",
        "standard_inputs": "CGM plus meals/carbs, insulin, activity, sleep/stress context, subject-level splits, RMSE/MAE and event/clinical-grid metrics.",
        "standard_input_count": "Often 4-8 core streams: CGM, insulin, carbs/meals, activity, sleep/stress/illness context, demographics, and device state.",
        "standard_compute": "Low-moderate for per-subject statistical models; moderate for ML; high cost comes from clinical validation, safety, and regulatory process.",
        "standard_cost": "Benchmark data may require agreements; clinical/pump-grade validation is high cost and regulatory/medical, not just compute.",
        "comparison_status": "Not a clinical benchmark. OhioT1DM/D1namo/Tidepool-style driver benchmark pending.",
    },
    {
        "system": "Heart / ECG",
        "ara_inputs": "ECG/RR and optional morphology features in prior local tests.",
        "ara_input_count": "1 ECG/RR stream in the simplest run; optional morphology features if enabled.",
        "standard_method": "Signal-processing plus ML/deep-learning classification/forecasting on PhysioNet-style patient splits; clinical standard is validation-heavy.",
        "standard_inputs": "PhysioNet-style patient splits, RR/morphology/arrhythmia targets, AR/ML/deep baselines, clinical event scoring.",
        "standard_input_count": "1-12 ECG leads sampled at high frequency, beat annotations, patient splits, labels, and often morphology/RR features.",
        "standard_compute": "Low for classic signal processing and AR baselines; moderate for CNN/RNN/transformer training; inference is usually cheap.",
        "standard_cost": "Public data are often free; clinical-grade validation is high cost because it needs patient-level task design and safety metrics.",
        "comparison_status": "Research signal only. PhysioNet task benchmark pending.",
    },
]


@dataclass
class SeriesSpec:
    name: str
    values: np.ndarray
    period: float
    horizons: tuple[int, ...]
    notes: str
    lower: tuple = ()
    upper: tuple = ()


def clean(v):
    a = np.asarray(v, dtype=float)
    return a[np.isfinite(a)]


def metric(truth, pred, current):
    truth = np.asarray(truth, dtype=float)
    pred = np.asarray(pred, dtype=float)
    current = np.asarray(current, dtype=float)
    ok = np.isfinite(truth) & np.isfinite(pred) & np.isfinite(current)
    truth, pred, current = truth[ok], pred[ok], current[ok]
    if len(truth) < 3:
        return {"n": int(len(truth)), "corr": None, "mae": None, "turn": None}
    corr = float(np.corrcoef(truth, pred)[0, 1])
    return {
        "n": int(len(truth)),
        "corr": corr if np.isfinite(corr) else None,
        "mae": float(np.mean(np.abs(truth - pred))),
        "turn": float(np.mean(np.sign(truth - current) == np.sign(pred - current))),
    }


def ridge_predict(xtr, ytr, xte, penalty=1.0):
    xtr = np.asarray(xtr, dtype=float)
    xte = np.asarray(xte, dtype=float)
    ytr = np.asarray(ytr, dtype=float)
    mu = np.nanmean(xtr, axis=0)
    sd = np.nanstd(xtr, axis=0)
    sd[~np.isfinite(sd) | (sd < 1e-12)] = 1.0
    a = np.nan_to_num((xtr - mu) / sd)
    b = np.nan_to_num((xte - mu) / sd)
    a = np.column_stack([np.ones(len(a)), a])
    b = np.column_stack([np.ones(len(b)), b])
    reg = np.eye(a.shape[1]) * penalty
    reg[0, 0] = 0.0
    beta = np.linalg.solve(a.T @ a + reg, a.T @ ytr)
    return b @ beta


def default_lags(n, period):
    cand = [0, 1, 2, 3, 6, 12, 24, 48, 72, 96, 120, int(round(period))]
    return tuple(sorted(set(l for l in cand if 0 <= l < n // 3)))


def features_at(y, origins, horizon, period, lags, include_lags=True):
    rows = []
    p = float(period)
    for t in origins:
        target_t = t + horizon
        row = [target_t / max(1, len(y))]
        for k in (1, 2):
            row.append(math.sin(2 * math.pi * k * target_t / p))
            row.append(math.cos(2 * math.pi * k * target_t / p))
        if include_lags:
            for lag in lags:
                row.append(float(y[t - lag]))
        rows.append(row)
    return np.asarray(rows, dtype=float)


def proxy_baselines(y, period, horizons, cutoff, lags):
    y = np.asarray(y, dtype=float)
    n = len(y)
    start = max(max(lags), int(round(period)) + 2)
    out = {}
    for h in horizons:
        tr = np.arange(start, cutoff - h)
        te = np.arange(cutoff, n - h)
        if len(tr) < 30 or len(te) < 30:
            out[str(h)] = None
            continue
        ytr = y[tr + h]
        yte = y[te + h]
        cte = y[te]
        period_i = int(round(period))

        seasonal = np.full(len(te), np.nan)
        idx = te + h - period_i
        ok = idx >= 0
        seasonal[ok] = y[idx[ok]]

        htr = features_at(y, tr, h, period, lags, include_lags=False)
        hte = features_at(y, te, h, period, lags, include_lags=False)
        harmonic = ridge_predict(htr, ytr, hte, penalty=1.0)

        ltr = features_at(y, tr, h, period, lags, include_lags=True)
        lte = features_at(y, te, h, period, lags, include_lags=True)
        lag_harmonic = ridge_predict(ltr, ytr, lte, penalty=1.0)

        out[str(h)] = {
            "seasonal_naive": metric(yte, seasonal, cte),
            "harmonic_clock": metric(yte, harmonic, cte),
            "lag_harmonic_ridge": metric(yte, lag_harmonic, cte),
        }
    return out


def point_predictions_for_horizon(system, horizon, period, lags, cutoff):
    y = np.asarray(system.home, dtype=float)
    n = len(y)
    h = int(horizon)
    state = F._layer_state(system, cutoff)
    start = max(max(system.home_lags), *(c.window + 2 for c in system.lower + system.upper))
    tr = np.arange(start, cutoff - h)
    te = np.arange(cutoff, n - h)
    if len(tr) < 30 or len(te) < 30:
        return None

    ytr = y[tr + h]
    yte = y[te + h]
    ctr = y[tr]
    cte = y[te]
    dtr = ytr - ctr

    raw_tr = state["roll"][tr] * math.sqrt(h / period)
    raw_te = state["roll"][te] * math.sqrt(h / period)
    rstd = float(np.std(raw_tr))
    scale = float(np.std(dtr) / rstd) if rstd > 1e-12 else 0.0
    ara_fixed = cte + scale * raw_te

    hxtr = np.asarray([[y[t - lag] for lag in system.home_lags] for t in tr], float)
    hxte = np.asarray([[y[t - lag] for lag in system.home_lags] for t in te], float)
    axtr = F._feature_matrix(system, state, tr, False)
    axte = F._feature_matrix(system, state, te, False)
    cxtr = F._feature_matrix(system, state, tr, True)
    cxte = F._feature_matrix(system, state, te, True)

    period_i = int(round(period))
    seasonal = np.full(len(te), np.nan)
    idx = te + h - period_i
    ok = idx >= 0
    seasonal[ok] = y[idx[ok]]

    htr = features_at(y, tr, h, period, lags, include_lags=False)
    hte = features_at(y, te, h, period, lags, include_lags=False)
    ltr = features_at(y, tr, h, period, lags, include_lags=True)
    lte = features_at(y, te, h, period, lags, include_lags=True)

    return {
        "origin_index": te.astype(int).tolist(),
        "truth": yte.astype(float).tolist(),
        "current": cte.astype(float).tolist(),
        "models": {
            "persistence": cte.astype(float).tolist(),
            "seasonal_naive": seasonal.astype(float).tolist(),
            "harmonic_clock": ridge_predict(htr, ytr, hte, penalty=1.0).astype(float).tolist(),
            "lag_harmonic_ridge": ridge_predict(ltr, ytr, lte, penalty=1.0).astype(float).tolist(),
            "home_ar": (cte + F._ridge_readout(hxtr, dtr, hxte)).astype(float).tolist(),
            "ara_roll_readout": (cte + F._ridge_readout(axtr, dtr, axte)).astype(float).tolist(),
            "ara_fixed_roll": ara_fixed.astype(float).tolist(),
            "home_plus_ara": (cte + F._ridge_readout(cxtr, dtr, cxte)).astype(float).tolist(),
        },
    }


def load_solar():
    path = os.path.join(HERE, "Claude4.8", "SN_m_tot.csv")
    vals = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = [p.strip() for p in line.split(";")]
            if len(parts) < 4:
                continue
            try:
                v = float(parts[3])
            except ValueError:
                continue
            if v >= 0:
                vals.append(v)
    return clean(vals)


def load_qbo_30():
    path = os.path.join(HERE, "Claude4.8", "qbo_u30.txt")
    vals = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 13:
                continue
            try:
                int(parts[0])
            except ValueError:
                continue
            for p in parts[1:13]:
                v = float(p)
                if -900 < v < 900:
                    vals.append(v)
    return clean(vals)


def load_nino():
    path = os.path.join(HERE, "Claude4.8", "nino34_long_anom.csv")
    df = pd.read_csv(path, skiprows=1, names=["date", "nino34"])
    df["date"] = pd.to_datetime(df["date"].astype(str).str.strip())
    df["nino34"] = pd.to_numeric(df["nino34"], errors="coerce")
    df = df[df["nino34"] > -90]
    return df.set_index("date")["nino34"].astype(float)


def load_soi():
    path = os.path.join(HERE, "Claude4.8", "soi.data")
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 13:
                continue
            try:
                year = int(parts[0])
            except ValueError:
                continue
            for m, p in enumerate(parts[1:13], 1):
                v = float(p)
                if v > -90:
                    rows.append((pd.Timestamp(year=year, month=m, day=1), v))
    return pd.Series(dict(rows)).sort_index()


def load_wwv(kind):
    path = os.path.join(HERE, "Claude4.8", f"wwv_{kind}.dat")
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 3:
                continue
            if not parts[0].isdigit():
                continue
            y = int(parts[0][:4])
            m = int(parts[0][4:6])
            rows.append((pd.Timestamp(year=y, month=m, day=1), float(parts[2])))
    return pd.Series(dict(rows)).sort_index()


def fetch_retail_cycle():
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=RSXFSN"
    df = pd.read_csv(url)
    val = pd.to_numeric(df["RSXFSN"], errors="coerce")
    date = pd.to_datetime(df["observation_date"])
    s = pd.Series(val.values, index=date).dropna()
    trailing = s.rolling(12, min_periods=12).mean()
    return (s / trailing).dropna().values.astype(float)


def fetch_sea_ice_monthly():
    url = "https://noaadata.apps.nsidc.org/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v4.0.csv"
    r = requests.get(url, timeout=30, verify=False)
    r.raise_for_status()
    from io import StringIO

    df = pd.read_csv(StringIO(r.text), skiprows=2, names=["year", "month", "day", "extent", "missing", "source"])
    for col in ("year", "month", "day", "extent"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["year", "month", "day", "extent"])
    df = df[df["extent"] > -900]
    dates = pd.to_datetime(dict(year=df["year"].astype(int), month=df["month"].astype(int), day=df["day"].astype(int)))
    s = pd.Series(df["extent"].astype(float).values, index=dates)
    return s.resample("MS").mean().dropna().values.astype(float)


def fetch_flu_ilinet():
    # Delphi Epidata fluview endpoint. If it changes or is unavailable, skip.
    url = "https://api.delphi.cmu.edu/epidata/fluview/?regions=nat&epiweeks=201040-202420"
    js = requests.get(url, timeout=30).json()
    rows = js.get("epidata", [])
    vals = []
    for row in sorted(rows, key=lambda r: r.get("epiweek", 0)):
        v = row.get("wili")
        if v is None:
            v = row.get("ili")
        if v is not None:
            vals.append(float(v))
    if len(vals) < 200:
        raise RuntimeError(f"Flu endpoint returned only {len(vals)} rows")
    return clean(vals)


def build_specs():
    specs = [
        SeriesSpec("solar_sunspots_self", load_solar(), 132, (12, 24, 60, 132),
                   "Local SILSO monthly sunspot series; proxy for SWPC-style cycle baselines, not SWPC archive."),
        SeriesSpec("qbo_30mb_self", load_qbo_30(), 28, (3, 6, 12, 18, 24),
                   "NOAA PSL/CDAS QBO 30mb monthly wind; proxy baselines only."),
    ]

    nino = load_nino()
    soi = load_soi()
    west = load_wwv("west")
    east = load_wwv("east")
    common = nino.index.intersection(soi.index).intersection(west.index).intersection(east.index).sort_values()
    nino_v = nino.reindex(common).values.astype(float)
    soi_v = soi.reindex(common).values.astype(float)
    west_v = west.reindex(common).values.astype(float)
    east_v = east.reindex(common).values.astype(float)
    specs.append(SeriesSpec("enso_nino34_self", nino_v, 48, (3, 6, 12, 18, 24),
                            "NOAA NINO3.4 overlap window; self-forecast only."))
    specs.append(SeriesSpec(
        "enso_nino34_with_soi_wwv",
        nino_v,
        48,
        (3, 6, 12, 18, 24),
        "NINO3.4 with SOI plus east/west warm-water-volume feeders; proxy for ENSO driver-below tests, not IRI/NMME archive.",
        lower=(("SOI", soi_v, 3, 3), ("WWV_W", west_v, 6, 6), ("WWV_E", east_v, 6, 6)),
        upper=(("WWV_TOTAL_SLOW", west_v + east_v, 60, 60),),
    ))

    fetchers = [
        ("retail_holiday_cycle", fetch_retail_cycle, 12, (1, 2, 3, 6, 12),
         "FRED RSXFSN cycle index: value / trailing-12-month mean."),
        ("arctic_sea_ice_monthly", fetch_sea_ice_monthly, 12, (1, 2, 3, 6, 12),
         "NSIDC/NOAA monthly mean extent fetched live; proxy for Sea Ice Outlook baselines."),
        ("flu_ilinet_weekly", fetch_flu_ilinet, 52, (2, 4, 8, 13, 26),
         "Delphi/CDC FluView ILINet national weekly WILI; proxy only, not FluSight WIS."),
    ]
    fetch_status = {}
    for name, fn, period, horizons, notes in fetchers:
        try:
            vals = fn()
            specs.append(SeriesSpec(name, clean(vals), period, horizons, notes))
            fetch_status[name] = {"status": "loaded", "n": int(len(vals))}
        except Exception as exc:
            fetch_status[name] = {"status": "skipped", "reason": str(exc)}

    return specs, fetch_status


def run_one(spec: SeriesSpec):
    y = clean(spec.values)
    lags = default_lags(len(y), spec.period)
    if spec.lower or spec.upper:
        system = F.build_system(y, spec.lower, spec.upper, spec.period, spec.horizons, lags,
                                name=spec.name, unit="step")
    else:
        system = F.build_self_system(y, spec.period, horizons=spec.horizons, home_lags=lags,
                                     name=spec.name, unit="step")
    ara = F.run_forecast(system)
    proxy = proxy_baselines(y, spec.period, spec.horizons, ara["cutoff_index"], lags)

    horizons = {}
    for h in spec.horizons:
        key = str(h)
        if ara["horizons"].get(key) is None:
            continue
        combined = {}
        combined.update(ara["horizons"][key])
        if proxy.get(key):
            combined.update(proxy[key])
        non_ara = {
            k: v for k, v in combined.items()
            if k in ("persistence", "home_ar", "seasonal_naive", "harmonic_clock", "lag_harmonic_ridge")
        }
        best_corr = max(non_ara.items(), key=lambda kv: -999 if kv[1]["corr"] is None else kv[1]["corr"])
        best_mae = min(non_ara.items(), key=lambda kv: 999999 if kv[1]["mae"] is None else kv[1]["mae"])
        hp = combined["home_plus_ara"]
        series = point_predictions_for_horizon(system, h, spec.period, lags, ara["cutoff_index"])
        if series is not None:
            series["default_standard_model"] = best_corr[0]
            series["best_mae_standard_model"] = best_mae[0]
        horizons[key] = {
            "models": combined,
            "best_non_ara_corr": {"model": best_corr[0], **best_corr[1]},
            "best_non_ara_mae": {"model": best_mae[0], **best_mae[1]},
            "home_plus_ara_corr_lift_vs_best_non_ara": (
                None if hp["corr"] is None or best_corr[1]["corr"] is None else hp["corr"] - best_corr[1]["corr"]
            ),
            "home_plus_ara_mae_delta_vs_best_non_ara": (
                None if hp["mae"] is None or best_mae[1]["mae"] is None else hp["mae"] - best_mae[1]["mae"]
            ),
            "series": series,
        }
    return {
        "name": spec.name,
        "n": int(len(y)),
        "period": float(spec.period),
        "horizons": horizons,
        "notes": spec.notes,
    }


def fmt(x, digits=3):
    if x is None:
        return "n/a"
    return f"{x:+.{digits}f}" if isinstance(x, float) else str(x)


def write_md(results, fetch_status):
    lines = []
    lines.append("# Forecast standard-baseline comparison (strict causal)")
    lines.append("")
    lines.append("Date: 3 June 2026")
    lines.append("")
    lines.append("This is the correction to the earlier comparison note. It is an actual local benchmark run against stronger proxy baselines, not only a source audit.")
    lines.append("")
    lines.append("Important fence: this still does **not** use archived operational forecast submissions from SWPC, IRI/NMME, Sea Ice Outlook, FluSight, or clinical task leaderboards. It compares ARA to strong local baselines on the same observed series.")
    lines.append("")
    lines.append("## Baselines")
    lines.append("")
    lines.append("- `persistence`: predict the current value.")
    lines.append("- `seasonal_naive`: predict the previous same phase/period value.")
    lines.append("- `harmonic_clock`: train-only sine/cosine cycle clock plus trend.")
    lines.append("- `lag_harmonic_ridge`: causal lags plus cycle clock.")
    lines.append("- `home_ar`: repo's causal lag readout from `ara_framework.run_forecast`.")
    lines.append("- `home_plus_ara`: headline ARA features plus causal lags.")
    lines.append("")
    lines.append("## Summary by horizon")
    lines.append("")
    lines.append("| system | h | ARA corr | best non-ARA corr | corr lift | ARA MAE | best non-ARA MAE | MAE delta | verdict |")
    lines.append("|---|---:|---:|---|---:|---:|---|---:|---|")
    ara_corr_wins = 0
    ara_mae_wins = 0
    total = 0
    for res in results:
        for h, row in res["horizons"].items():
            hp = row["models"]["home_plus_ara"]
            bc = row["best_non_ara_corr"]
            bm = row["best_non_ara_mae"]
            cl = row["home_plus_ara_corr_lift_vs_best_non_ara"]
            md = row["home_plus_ara_mae_delta_vs_best_non_ara"]
            corr_win = cl is not None and cl > 0
            mae_win = md is not None and md < 0
            total += 1
            ara_corr_wins += int(corr_win)
            ara_mae_wins += int(mae_win)
            verdict = "ARA corr win" if corr_win else "baseline corr win"
            if mae_win:
                verdict += "; ARA MAE win"
            lines.append(
                f"| {res['name']} | {h} | {fmt(hp['corr'])} | {bc['model']} {fmt(bc['corr'])} | "
                f"{fmt(cl)} | {hp['mae']:.3g} | {bm['model']} {bm['mae']:.3g} | "
                f"{md:.3g} | {verdict} |"
            )
    lines.append("")
    lines.append(f"ARA `home_plus_ara` beat the best local non-ARA baseline on correlation at **{ara_corr_wins}/{total}** horizons.")
    lines.append(f"ARA `home_plus_ara` beat the best local non-ARA baseline on MAE at **{ara_mae_wins}/{total}** horizons.")
    lines.append("")
    lines.append("## Fetch/load status")
    lines.append("")
    for name, status in fetch_status.items():
        if status["status"] == "loaded":
            lines.append(f"- `{name}`: loaded, n={status['n']}")
        else:
            lines.append(f"- `{name}`: skipped - {status['reason']}")
    lines.append("")
    lines.append("## Read")
    lines.append("")
    lines.append("- If `home_plus_ara` beats persistence but loses to `home_ar` or `lag_harmonic_ridge`, the result is a persistence/lag-memory win, not an ARA-over-standard win.")
    lines.append("- If it beats `seasonal_naive`, that matters for annual systems where persistence inversion can otherwise exaggerate the apparent difficulty.")
    lines.append("- If it beats `lag_harmonic_ridge`, that is the cleanest local evidence that ARA features add signal beyond ordinary memory plus a cycle clock.")
    lines.append("- Dengue is intentionally excluded from this core pass because it was an incomplete side run and needs external drivers before it is a fair forecast claim.")
    lines.append("")
    lines.append("## Operational archive status")
    lines.append("")
    lines.append("Still pending, not passed here:")
    lines.append("")
    lines.append("- Solar: archived SWPC/panel hindcasts for smoothed sunspot number and F10.7.")
    lines.append("- ENSO: IRI/NMME/CFSv2 hindcast/real-time forecast archives with same lead/season/class metrics.")
    lines.append("- Sea ice: Sea Ice Outlook September extent submissions/baselines.")
    lines.append("- Flu: FluSight WIS/relative-WIS targets and forecast hub submissions.")
    lines.append("- Retail: X-13/ARIMA/ETS comparison on raw and seasonally adjusted sales.")
    lines.append("- CGM/ECG: OhioT1DM/PhysioNet task metrics with subject-level splits and clinical/event scores.")
    lines.append("")
    lines.append("## Input requirements and cost comparison")
    lines.append("")
    lines.append("| system | ARA inputs | standard method | standard input count | standard compute | cost / burden | status |")
    lines.append("|---|---|---|---|---|---|---|")
    for item in INPUT_COST_COMPARISON:
        lines.append(
            f"| {item['system']} | {item['ara_inputs']} ({item['ara_input_count']}) | "
            f"{item['standard_method']} | {item['standard_input_count']} | "
            f"{item['standard_compute']} | {item['standard_cost']} | {item['comparison_status']} |"
        )
    lines.append("")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    specs, fetch_status = build_specs()
    results = []
    for spec in specs:
        print(f"Running {spec.name} n={len(spec.values)} P={spec.period} horizons={spec.horizons}")
        results.append(run_one(spec))
    payload = {
        "results": results,
        "fetch_status": fetch_status,
        "input_cost_comparison": INPUT_COST_COMPARISON,
        "phi": PHI,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    with open(OUT_VIZ_JS, "w", encoding="utf-8") as f:
        f.write("window.ARA_VS_STANDARD_DATA = ")
        json.dump(payload, f, ensure_ascii=False)
        f.write(";\n")
    write_md(results, fetch_status)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_VIZ_JS}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()

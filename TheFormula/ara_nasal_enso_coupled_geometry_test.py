"""
ara_nasal_enso_coupled_geometry_test.py

Coupled-system temporal geometry check:
  nasal cycle left/right airflow dominance  <->  ENSO NINO/SOI dominance.

Why this test exists:
  ENSO is a coupled ocean/atmosphere oscillator. Comparing it to a single
  oscillator shape can blur the framework claim. The nasal cycle gives a
  biological paired oscillator: right nostril vs left nostril airflow, measured
  as a laterality index. ENSO is mapped the same way from NINO and SOI.

No-leakage discipline:
  - Raw public nasal-cycle files are cached locally before analysis.
  - NINO/SOI scaling is fitted on the ENSO train split only.
  - Circular phase shift is learned on train templates only, then applied to
    held-out templates.
  - All fixed thresholds are declared in code and are not tuned to the result.

This is a descriptive time-scaled geometry test, not a value forecast.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d


HERE = Path(__file__).resolve().parent
CACHE = HERE / "data_cache"
OUT_JSON = HERE / "ara_nasal_enso_coupled_geometry_result.json"
OUT_JS = HERE / "ara_nasal_enso_coupled_geometry_result.js"

NINO_PATH = Path(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
SOI_PATH = Path(r"F:\SystemFormulaFolder\SOI_NOAA\soi.data")

PHI = (1.0 + math.sqrt(5.0)) / 2.0
N_PHASE = 200
EPS = 1e-12


def corr(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    good = np.isfinite(a) & np.isfinite(b)
    a = a[good]
    b = b[good]
    if len(a) < 5 or np.std(a) < EPS or np.std(b) < EPS:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def minmax(x):
    x = np.asarray(x, dtype=float)
    lo = float(np.nanmin(x))
    hi = float(np.nanmax(x))
    if hi - lo < EPS:
        return np.zeros_like(x)
    return (x - lo) / (hi - lo)


def resample(segment, n=N_PHASE):
    segment = np.asarray(segment, dtype=float)
    xo = np.linspace(0.0, 1.0, len(segment))
    xn = np.linspace(0.0, 1.0, n)
    return np.interp(xn, xo, segment)


def oriented_interval_templates(x, min_len, center=0.0):
    """Return dominance intervals from zero/center crossings, sign-normalized."""
    x = np.asarray(x, dtype=float) - center
    good = np.isfinite(x)
    if not np.all(good):
        idx = np.arange(len(x))
        x = np.interp(idx, idx[good], x[good])

    crossings = []
    for i in range(1, len(x)):
        if x[i - 1] == 0.0 or x[i] == 0.0 or np.sign(x[i - 1]) != np.sign(x[i]):
            crossings.append(i)

    intervals = []
    descriptors = []
    for a, b in zip(crossings[:-1], crossings[1:]):
        if b - a < min_len:
            continue
        seg = x[a:b]
        s = float(np.sign(np.nanmean(seg)))
        if s == 0.0:
            continue
        y = s * seg
        y = y - float(np.nanmin(y))
        y = y / (float(np.nanmax(y)) + EPS)
        intervals.append(resample(y))
        descriptors.append({"start": int(a), "end": int(b), "length": int(b - a), "sign": s})
    return intervals, descriptors


def split_list(items, train_frac=0.70):
    items = list(items)
    if len(items) < 2:
        return items, []
    cut = max(1, min(len(items) - 1, int(math.floor(len(items) * train_frac))))
    return items[:cut], items[cut:]


def mean_template(segments):
    if not segments:
        return np.zeros(N_PHASE, dtype=float)
    return minmax(np.mean(np.asarray(segments, dtype=float), axis=0))


def maxabs(x):
    x = np.asarray(x, dtype=float)
    scale = float(np.nanmax(np.abs(x))) + EPS
    return x / scale


def mean_signed_template(segments):
    if not segments:
        return np.zeros(N_PHASE, dtype=float)
    y = np.mean(np.asarray(segments, dtype=float), axis=0)
    y = y - float(np.nanmean(y))
    return maxabs(y)


def signed_coupled_cycle_templates(x, min_half_len, center=0.0):
    """Return two-dominance-interval cycles, preserving anti-phase sign."""
    x = np.asarray(x, dtype=float) - center
    good = np.isfinite(x)
    if not np.all(good):
        idx = np.arange(len(x))
        x = np.interp(idx, idx[good], x[good])

    crossings = []
    for i in range(1, len(x)):
        if x[i - 1] == 0.0 or x[i] == 0.0 or np.sign(x[i - 1]) != np.sign(x[i]):
            crossings.append(i)

    cycles = []
    descriptors = []
    for a, mid, b in zip(crossings[:-2], crossings[1:-1], crossings[2:]):
        if mid - a < min_half_len or b - mid < min_half_len:
            continue
        seg = x[a:b]
        first_sign = float(np.sign(np.nanmean(x[a:mid])))
        if first_sign == 0.0:
            continue
        y = maxabs(first_sign * seg)
        cycles.append(resample(y))
        descriptors.append({"start": int(a), "mid": int(mid), "end": int(b), "length": int(b - a), "first_sign": first_sign})
    return cycles, descriptors


def best_shift(a, b):
    scores = [corr(a, np.roll(b, k)) for k in range(len(a))]
    k = int(np.argmax(scores))
    return k, float(scores[k])


def fourier_params(shape, k_max=8):
    s = np.asarray(shape, dtype=float) - float(np.mean(shape))
    f = np.fft.fft(s)
    amp = np.abs(f)
    phase = np.angle(f)
    base = amp[1] if amp[1] > EPS else EPS
    ratios = [float(amp[k] / base) for k in range(2, k_max + 1)]
    rel_phase = [
        float(np.mod(phase[k] - k * phase[1] + math.pi, 2.0 * math.pi) - math.pi)
        for k in range(2, k_max + 1)
    ]
    return np.asarray(ratios + rel_phase, dtype=float)


def fourier_distance(a, b):
    return float(np.linalg.norm(fourier_params(a) - fourier_params(b)))


def null_shapes():
    x = np.linspace(0.0, 1.0, N_PHASE, endpoint=False)
    phase = 2.0 * math.pi * x
    shapes = {
        "pure sine hump": 0.5 - 0.5 * np.cos(2.0 * math.pi * x),
        "triangle hump": 1.0 - np.abs(2.0 * x - 1.0),
        "fast-rise slow-fall": np.where(x < 0.28, x / 0.28, (1.0 - x) / 0.72),
        "slow-rise fast-fall": np.where(x < 0.72, x / 0.72, (1.0 - x) / 0.28),
        "gaussian hump": np.exp(-0.5 * ((x - 0.5) / 0.14) ** 2),
        "phi-rise hump": np.where(x < 1.0 / PHI, (x / (1.0 / PHI)) ** PHI, ((1.0 - x) / (1.0 - 1.0 / PHI)) ** (1.0 / PHI)),
        "double shoulder": np.exp(-0.5 * ((x - 0.38) / 0.10) ** 2) + 0.75 * np.exp(-0.5 * ((x - 0.64) / 0.18) ** 2),
        "wavy coupled hump": 0.5 - 0.5 * np.cos(phase) + 0.18 * np.sin(2.0 * phase + 0.7),
    }
    return {name: minmax(y) for name, y in shapes.items()}


def signed_null_shapes():
    x = np.linspace(0.0, 1.0, N_PHASE, endpoint=False)
    phase = 2.0 * math.pi * x
    shapes = {
        "pure sine": np.sin(phase),
        "sine plus second harmonic": np.sin(phase) + 0.25 * np.sin(2.0 * phase + 0.5),
        "sine plus third harmonic": np.sin(phase) + 0.20 * np.sin(3.0 * phase - 0.4),
        "soft square": np.tanh(2.2 * np.sin(phase)),
        "asymmetric signed triangle": np.where(x < 0.38, x / 0.38, np.where(x < 0.72, 1.0 - 2.0 * (x - 0.38) / 0.34, -1.0 + (x - 0.72) / 0.28)),
        "phi-skew signed": np.sin(phase) + (1.0 / PHI) * np.sin(2.0 * phase + PHI),
        "coupled breath-like": np.sin(phase) - 0.35 * np.sin(2.0 * phase - 0.7) + 0.12 * np.sin(4.0 * phase),
        "enso-like slow turn": np.sin(phase) + 0.18 * np.cos(2.0 * phase) - 0.08 * np.sin(3.0 * phase),
    }
    return {name: maxabs(y - np.mean(y)) for name, y in shapes.items()}


def random_null_percentile(target, distance, n=1000, seed=11):
    rng = np.random.default_rng(seed)
    x = np.linspace(0.0, 1.0, N_PHASE, endpoint=False)
    distances = []
    for _ in range(n):
        peak = float(rng.uniform(0.20, 0.80))
        rise = float(rng.uniform(0.35, 3.0))
        fall = float(rng.uniform(0.35, 3.0))
        y = np.where(x < peak, (x / peak) ** rise, ((1.0 - x) / (1.0 - peak)) ** fall)
        if rng.random() < 0.35:
            y += float(rng.uniform(0.03, 0.25)) * np.sin(4.0 * math.pi * x + float(rng.uniform(0, 2 * math.pi)))
        distances.append(fourier_distance(target, minmax(y)))
    distances = np.asarray(distances, dtype=float)
    closer = float(np.mean(distances <= distance) * 100.0)
    return closer, 100.0 - closer


def random_signed_null_percentile(target, distance, n=1000, seed=17):
    rng = np.random.default_rng(seed)
    x = np.linspace(0.0, 1.0, N_PHASE, endpoint=False)
    phase = 2.0 * math.pi * x
    distances = []
    for _ in range(n):
        y = np.sin(phase + float(rng.uniform(-0.6, 0.6)))
        for k in range(2, 6):
            y += float(rng.uniform(-0.35, 0.35)) * np.sin(k * phase + float(rng.uniform(0, 2 * math.pi)))
        if rng.random() < 0.35:
            y = np.tanh(float(rng.uniform(1.0, 3.5)) * y)
        distances.append(fourier_distance(target, maxabs(y - np.mean(y))))
    distances = np.asarray(distances, dtype=float)
    closer = float(np.mean(distances <= distance) * 100.0)
    return closer, 100.0 - closer


def load_nasal_subject(path):
    rows = []
    with Path(path).open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader, None)
        for row in reader:
            if len(row) < 3:
                continue
            try:
                rows.append((float(row[1]), float(row[2])))
            except ValueError:
                pass
    arr = np.asarray(rows, dtype=float)
    samples_per_minute = int(round((1.0 / 0.18) * 60.0))
    n_min = len(arr) // samples_per_minute
    arr = arr[: n_min * samples_per_minute].reshape(n_min, samples_per_minute, 2)

    envelope = np.percentile(arr, 95, axis=1) - np.percentile(arr, 5, axis=1)
    valid = np.sum(envelope, axis=1) > 0.025
    if int(np.sum(valid)) < 120:
        return None

    idx = np.where(valid)[0]
    start = int(idx[0])
    end = int(idx[-1]) + 1
    envelope = envelope[start:end]
    li = (envelope[:, 0] - envelope[:, 1]) / (envelope[:, 0] + envelope[:, 1] + EPS)
    li = gaussian_filter1d(li, sigma=7.5)
    intervals, desc = oriented_interval_templates(li, min_len=15, center=float(np.nanmedian(li)))
    cycles, cycle_desc = signed_coupled_cycle_templates(li, min_half_len=15, center=float(np.nanmedian(li)))
    for d in desc:
        d["start_minute"] = d.pop("start") + start
        d["end_minute"] = d.pop("end") + start
    for d in cycle_desc:
        d["start_minute"] = d.pop("start") + start
        d["mid_minute"] = d.pop("mid") + start
        d["end_minute"] = d.pop("end") + start
    return {
        "path": str(path),
        "minutes": int(len(li)),
        "intervals": intervals,
        "cycles": cycles,
        "descriptors": desc,
        "cycle_descriptors": cycle_desc,
        "li_range": [float(np.nanmin(li)), float(np.nanmax(li))],
    }


def load_all_nasal():
    subjects = []
    for path in sorted(CACHE.glob("nasal_sbj*.txt")):
        item = load_nasal_subject(path)
        if item and len(item["intervals"]) >= 4:
            subjects.append(item)
    train = []
    test = []
    cycle_train = []
    cycle_test = []
    subject_summary = []
    for item in subjects:
        tr, te = split_list(item["intervals"])
        train.extend(tr)
        test.extend(te)
        ctr, cte = split_list(item["cycles"])
        cycle_train.extend(ctr)
        cycle_test.extend(cte)
        lengths = [d["length"] for d in item["descriptors"]]
        cycle_lengths = [d["length"] for d in item["cycle_descriptors"]]
        subject_summary.append(
            {
                "file": Path(item["path"]).name,
                "minutes": item["minutes"],
                "n_intervals": len(item["intervals"]),
                "n_signed_cycles": len(item["cycles"]),
                "median_interval_minutes": float(np.median(lengths)) if lengths else None,
                "median_signed_cycle_minutes": float(np.median(cycle_lengths)) if cycle_lengths else None,
                "li_range": item["li_range"],
            }
        )
    return train, test, cycle_train, cycle_test, subject_summary, subjects


def load_nino():
    df = pd.read_csv(NINO_PATH, skiprows=1, names=["date", "value"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna()
    df = df[df["value"] > -50.0]
    return pd.Series(df["value"].values.astype(float), index=df["date"]).sort_index()


def load_soi():
    rows = []
    with SOI_PATH.open("r", encoding="utf-8", errors="replace") as f:
        next(f, None)
        for line in f:
            parts = line.split()
            if len(parts) < 13:
                continue
            try:
                year = int(parts[0])
            except ValueError:
                continue
            for month, raw in enumerate(parts[1:13], 1):
                try:
                    value = float(raw)
                except ValueError:
                    continue
                if value <= -50.0:
                    continue
                rows.append((pd.Timestamp(year=year, month=month, day=1), value))
    return pd.Series([v for _, v in rows], index=[d for d, _ in rows]).sort_index()


def enso_base():
    nino = load_nino()
    soi = load_soi()
    common = nino.index.intersection(soi.index).sort_values()
    n = nino.reindex(common).values.astype(float)
    s = soi.reindex(common).values.astype(float)
    split = int(math.floor(len(common) * 0.70))
    n_mu, n_sd = float(np.mean(n[:split])), float(np.std(n[:split]) + EPS)
    s_mu, s_sd = float(np.mean(s[:split])), float(np.std(s[:split]) + EPS)
    zn = (n - n_mu) / n_sd
    zs = (s - s_mu) / s_sd
    return common, zn, zs, split


def enso_laterality(mode="coupled", soi_shift=0):
    common, zn, zs, split = enso_base()
    if soi_shift:
        zs = np.roll(zs, int(soi_shift))

    # Raw SOI is the atmospheric counter-side: El Nino is NINO high and SOI low.
    if mode == "coupled":
        li = (zn - zs) / (np.abs(zn) + np.abs(zs) + EPS)
    elif mode == "nino_only":
        li = zn
    elif mode == "soi_only_inverted":
        li = -zs
    else:
        raise ValueError(f"Unknown ENSO mode: {mode}")
    li = gaussian_filter1d(li, sigma=2.0)
    return common, li, split


def load_enso_intervals(mode="coupled", soi_shift=0):
    dates, li, split_idx = enso_laterality(mode=mode, soi_shift=soi_shift)
    train_li = li[:split_idx]
    test_li = li[split_idx:]
    train_intervals, train_desc = oriented_interval_templates(train_li, min_len=5, center=0.0)
    test_intervals, test_desc = oriented_interval_templates(test_li, min_len=5, center=0.0)
    train_cycles, train_cycle_desc = signed_coupled_cycle_templates(train_li, min_half_len=5, center=0.0)
    test_cycles, test_cycle_desc = signed_coupled_cycle_templates(test_li, min_half_len=5, center=0.0)
    for d in train_desc:
        d["start_date"] = str(dates[d.pop("start")].date())
        d["end_date"] = str(dates[d.pop("end")].date())
    for d in test_desc:
        start = d.pop("start") + split_idx
        end = d.pop("end") + split_idx
        d["start_date"] = str(dates[start].date())
        d["end_date"] = str(dates[end].date())
    return train_intervals, test_intervals, {
        "mode": mode,
        "soi_shift_months": int(soi_shift),
        "date_start": str(dates[0].date()),
        "date_end": str(dates[-1].date()),
        "n_months": int(len(dates)),
        "train_months": int(split_idx),
        "test_months": int(len(dates) - split_idx),
        "n_train_intervals": int(len(train_intervals)),
        "n_test_intervals": int(len(test_intervals)),
        "train_interval_months_median": float(np.median([d["length"] for d in train_desc])) if train_desc else None,
        "test_interval_months_median": float(np.median([d["length"] for d in test_desc])) if test_desc else None,
        "train_signed_cycles": int(len(train_cycles)),
        "test_signed_cycles": int(len(test_cycles)),
        "train_signed_cycle_months_median": float(np.median([d["length"] for d in train_cycle_desc])) if train_cycle_desc else None,
        "test_signed_cycle_months_median": float(np.median([d["length"] for d in test_cycle_desc])) if test_cycle_desc else None,
        "train_cycles_payload": train_cycles,
        "test_cycles_payload": test_cycles,
    }


def compare(nasal_train_t, nasal_test_t, enso_train_t, enso_test_t, label, null_mode="hump"):
    shift, train_shifted = best_shift(nasal_train_t, enso_train_t)
    test_shifted = corr(nasal_test_t, np.roll(enso_test_t, shift))
    dist_train = fourier_distance(nasal_train_t, enso_train_t)
    dist_test = fourier_distance(nasal_test_t, enso_test_t)
    fixed_nulls = signed_null_shapes() if null_mode == "signed" else null_shapes()
    ranked = sorted(
        [{"name": name, "distance": fourier_distance(nasal_train_t, shape)} for name, shape in fixed_nulls.items()]
        + [{"name": label, "distance": dist_train}],
        key=lambda x: x["distance"],
    )
    rank = 1 + next(i for i, item in enumerate(ranked) if item["name"] == label)
    if null_mode == "signed":
        closer, specificity = random_signed_null_percentile(nasal_train_t, dist_train)
    else:
        closer, specificity = random_null_percentile(nasal_train_t, dist_train)
    if test_shifted >= 0.70 and rank <= 3 and specificity >= 70.0:
        verdict = "strong_specific_coupled_geometry_match"
    elif test_shifted >= 0.70:
        verdict = "high_coupled_interval_correlation_but_not_specific_against_nulls"
    elif test_shifted >= 0.35:
        verdict = "moderate_coupled_interval_match"
    else:
        verdict = "weak_or_no_coupled_interval_match"
    return {
        "verdict": verdict,
        "phase_shift_from_train": int(shift),
        "train_corr_direct": corr(nasal_train_t, enso_train_t),
        "train_corr_shifted": train_shifted,
        "test_corr_direct": corr(nasal_test_t, enso_test_t),
        "test_corr_with_train_shift": test_shifted,
        "fourier_distance_train": dist_train,
        "fourier_distance_test": dist_test,
        "null_rank_train": int(rank),
        "null_count_train": int(len(ranked)),
        "null_results_train": ranked,
        "random_piecewise_null_closer_or_equal_percentile": closer,
        "random_piecewise_specificity_percentile": specificity,
    }


def train_shifted_test_corr(nasal_train_t, nasal_test_t, enso_train_t, enso_test_t):
    shift, train_corr = best_shift(nasal_train_t, enso_train_t)
    return {
        "phase_shift_from_train": int(shift),
        "train_corr_shifted": float(train_corr),
        "test_corr_with_train_shift": corr(nasal_test_t, np.roll(enso_test_t, shift)),
        "test_corr_direct": corr(nasal_test_t, enso_test_t),
    }


def summarize_values(values):
    vals = np.asarray(values, dtype=float)
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return {"n": 0}
    return {
        "n": int(len(vals)),
        "mean": float(np.mean(vals)),
        "median": float(np.median(vals)),
        "p05": float(np.percentile(vals, 5)),
        "p25": float(np.percentile(vals, 25)),
        "p75": float(np.percentile(vals, 75)),
        "p95": float(np.percentile(vals, 95)),
        "max": float(np.max(vals)),
    }


def enso_templates(mode="coupled", soi_shift=0):
    tr, te, meta = load_enso_intervals(mode=mode, soi_shift=soi_shift)
    cycle_tr = meta.pop("train_cycles_payload")
    cycle_te = meta.pop("test_cycles_payload")
    return {
        "interval_train": mean_template(tr),
        "interval_test": mean_template(te),
        "signed_train": mean_signed_template(cycle_tr),
        "signed_test": mean_signed_template(cycle_te),
        "meta": meta,
        "n_intervals_train": len(tr),
        "n_intervals_test": len(te),
        "n_signed_train": len(cycle_tr),
        "n_signed_test": len(cycle_te),
    }


def main():
    nasal_train, nasal_test, nasal_cycle_train, nasal_cycle_test, nasal_summary, nasal_subjects = load_all_nasal()
    enso_actual = enso_templates(mode="coupled")
    enso_meta = dict(enso_actual["meta"])
    if len(nasal_train) < 5 or len(nasal_test) < 3:
        raise RuntimeError("Not enough nasal dominance intervals in cached subjects")
    if enso_actual["n_intervals_train"] < 5 or enso_actual["n_intervals_test"] < 3:
        raise RuntimeError("Not enough ENSO dominance intervals")

    nasal_train_t = mean_template(nasal_train)
    nasal_test_t = mean_template(nasal_test)
    enso_train_t = enso_actual["interval_train"]
    enso_test_t = enso_actual["interval_test"]
    interval_result = compare(
        nasal_train_t,
        nasal_test_t,
        enso_train_t,
        enso_test_t,
        "nasal vs ENSO coupled dominance intervals",
        null_mode="hump",
    )

    nasal_cycle_train_t = mean_signed_template(nasal_cycle_train)
    nasal_cycle_test_t = mean_signed_template(nasal_cycle_test)
    enso_cycle_train_t = enso_actual["signed_train"]
    enso_cycle_test_t = enso_actual["signed_test"]
    signed_cycle_result = compare(
        nasal_cycle_train_t,
        nasal_cycle_test_t,
        enso_cycle_train_t,
        enso_cycle_test_t,
        "nasal vs ENSO signed coupled cycles",
        null_mode="signed",
    )

    ablations = {}
    for mode, label in [
        ("coupled", "NINO/SOI coupled"),
        ("nino_only", "NINO only"),
        ("soi_only_inverted", "SOI only inverted"),
    ]:
        e = enso_templates(mode=mode)
        ablations[mode] = {
            "label": label,
            "interval": train_shifted_test_corr(nasal_train_t, nasal_test_t, e["interval_train"], e["interval_test"]),
            "signed_cycle": train_shifted_test_corr(nasal_cycle_train_t, nasal_cycle_test_t, e["signed_train"], e["signed_test"]),
            "meta": e["meta"],
        }

    rng = np.random.default_rng(20260523)
    max_shift = int(enso_actual["meta"]["n_months"])
    candidate_shifts = [int(x) for x in rng.choice(np.arange(24, max_shift - 24), size=80, replace=False)]
    shuffled_interval_scores = []
    shuffled_signed_scores = []
    shuffled_signed_templates = []
    for shift in candidate_shifts:
        e = enso_templates(mode="coupled", soi_shift=shift)
        shuffled_interval_scores.append(
            train_shifted_test_corr(nasal_train_t, nasal_test_t, e["interval_train"], e["interval_test"])["test_corr_with_train_shift"]
        )
        shuffled_signed_scores.append(
            train_shifted_test_corr(nasal_cycle_train_t, nasal_cycle_test_t, e["signed_train"], e["signed_test"])["test_corr_with_train_shift"]
        )
        shuffled_signed_templates.append((shift, e["signed_train"], e["signed_test"]))

    actual_interval_score = ablations["coupled"]["interval"]["test_corr_with_train_shift"]
    actual_signed_score = ablations["coupled"]["signed_cycle"]["test_corr_with_train_shift"]
    shuffle_summary = {
        "n_shifts": len(candidate_shifts),
        "shift_months": candidate_shifts,
        "interval_scores": summarize_values(shuffled_interval_scores),
        "signed_cycle_scores": summarize_values(shuffled_signed_scores),
        "actual_interval_percentile_vs_shuffled": float(np.mean(np.asarray(shuffled_interval_scores) <= actual_interval_score) * 100.0),
        "actual_signed_cycle_percentile_vs_shuffled": float(np.mean(np.asarray(shuffled_signed_scores) <= actual_signed_score) * 100.0),
    }

    subject_results = []
    subject_actual_scores = []
    subject_shuffled_scores = []
    for item in nasal_subjects:
        ctr, cte = split_list(item["cycles"])
        if len(ctr) < 2 or len(cte) < 1:
            continue
        subj_train = mean_signed_template(ctr)
        subj_test = mean_signed_template(cte)
        actual = train_shifted_test_corr(subj_train, subj_test, enso_cycle_train_t, enso_cycle_test_t)
        shuffled = [
            train_shifted_test_corr(subj_train, subj_test, st_train, st_test)["test_corr_with_train_shift"]
            for _, st_train, st_test in shuffled_signed_templates
        ]
        subject_actual_scores.append(actual["test_corr_with_train_shift"])
        subject_shuffled_scores.extend(shuffled)
        subject_results.append(
            {
                "file": Path(item["path"]).name,
                "n_signed_cycles": len(item["cycles"]),
                "actual_test_corr_with_train_shift": actual["test_corr_with_train_shift"],
                "actual_percentile_vs_own_shuffled": float(np.mean(np.asarray(shuffled) <= actual["test_corr_with_train_shift"]) * 100.0),
                "shuffled_summary": summarize_values(shuffled),
            }
        )
    subject_level = {
        "n_subjects": len(subject_results),
        "actual_scores": summarize_values(subject_actual_scores),
        "pooled_shuffled_scores": summarize_values(subject_shuffled_scores),
        "actual_mean_percentile_vs_pooled_shuffled": float(np.mean(np.asarray(subject_shuffled_scores) <= np.mean(subject_actual_scores)) * 100.0)
        if subject_actual_scores and subject_shuffled_scores else None,
        "subjects_actual_beating_own_shuffled_median": int(
            sum(r["actual_test_corr_with_train_shift"] > r["shuffled_summary"]["median"] for r in subject_results)
        ),
        "subject_results": subject_results,
    }

    payload = {
        "date": "2026-05-23",
        "method": "Compare paired dominance interval templates: nasal LI=(R-L)/(R+L), ENSO LI=(zNINO-zSOI)/(abs(zNINO)+abs(zSOI)). Intervals are sign-normalized and time-rescaled.",
        "leakage_guard": [
            "NINO/SOI scaling fitted on ENSO train split only.",
            "Nasal and ENSO train/test intervals split before template comparison.",
            "Phase shift learned on train templates only.",
            "No target values or held-out templates used to choose thresholds.",
        ],
        "nasal": {
            "source": "Kahana Zweig 2016 Figshare nasal-cycle dataset, cached 33 subjects",
            "subjects": nasal_summary,
            "n_train_intervals": int(len(nasal_train)),
            "n_test_intervals": int(len(nasal_test)),
            "n_train_signed_cycles": int(len(nasal_cycle_train)),
            "n_test_signed_cycles": int(len(nasal_cycle_test)),
            "train_template": [float(x) for x in nasal_train_t],
            "test_template": [float(x) for x in nasal_test_t],
            "signed_cycle_train_template": [float(x) for x in nasal_cycle_train_t],
            "signed_cycle_test_template": [float(x) for x in nasal_cycle_test_t],
        },
        "enso": {
            "source": {"nino": str(NINO_PATH), "soi": str(SOI_PATH)},
            "meta": enso_meta,
            "train_template": [float(x) for x in enso_train_t],
            "test_template": [float(x) for x in enso_test_t],
            "signed_cycle_train_template": [float(x) for x in enso_cycle_train_t],
            "signed_cycle_test_template": [float(x) for x in enso_cycle_test_t],
        },
        "interval_result": interval_result,
        "signed_cycle_result": signed_cycle_result,
        "ablations": ablations,
        "shuffled_partner_null": shuffle_summary,
        "subject_level": subject_level,
        "phi": PHI,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_JS.write_text("window.NASAL_ENSO_COUPLED_GEOMETRY = " + json.dumps(payload) + ";\n", encoding="utf-8")

    print("=== NASAL <-> ENSO COUPLED GEOMETRY ===")
    print(f"Nasal train/test intervals: {len(nasal_train)}/{len(nasal_test)}")
    print(f"ENSO train/test intervals: {enso_meta['n_train_intervals']}/{enso_meta['n_test_intervals']}")
    print(f"Nasal signed train/test cycles: {len(nasal_cycle_train)}/{len(nasal_cycle_test)}")
    print(f"ENSO signed train/test cycles: {enso_meta['train_signed_cycles']}/{enso_meta['test_signed_cycles']}")
    print("\n-- Dominance interval template --")
    for key in [
        "train_corr_direct",
        "train_corr_shifted",
        "test_corr_direct",
        "test_corr_with_train_shift",
        "fourier_distance_train",
        "fourier_distance_test",
        "null_rank_train",
        "random_piecewise_null_closer_or_equal_percentile",
        "random_piecewise_specificity_percentile",
        "verdict",
    ]:
        print(f"{key}: {interval_result[key]}")
    print("\n-- Signed full coupled-cycle template --")
    for key in [
        "train_corr_direct",
        "train_corr_shifted",
        "test_corr_direct",
        "test_corr_with_train_shift",
        "fourier_distance_train",
        "fourier_distance_test",
        "null_rank_train",
        "random_piecewise_null_closer_or_equal_percentile",
        "random_piecewise_specificity_percentile",
        "verdict",
    ]:
        print(f"{key}: {signed_cycle_result[key]}")
    print("\n-- Ablation heldout corr with train-only shift --")
    for mode, item in ablations.items():
        print(
            f"{mode}: interval={item['interval']['test_corr_with_train_shift']:+.3f} "
            f"signed={item['signed_cycle']['test_corr_with_train_shift']:+.3f}"
        )
    print("\n-- Shuffled partner null --")
    print(f"actual interval percentile vs shuffled: {shuffle_summary['actual_interval_percentile_vs_shuffled']:.1f}")
    print(f"actual signed percentile vs shuffled: {shuffle_summary['actual_signed_cycle_percentile_vs_shuffled']:.1f}")
    print("\n-- Subject level signed cycles --")
    print(f"subjects: {subject_level['n_subjects']}")
    print(f"actual score summary: {subject_level['actual_scores']}")
    print(f"pooled shuffled summary: {subject_level['pooled_shuffled_scores']}")
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    main()

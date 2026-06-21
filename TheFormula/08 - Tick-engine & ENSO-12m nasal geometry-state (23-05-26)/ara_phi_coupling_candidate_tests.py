"""
ara_phi_coupling_candidate_tests.py

Three strict held-out checks for the current coupling hypothesis:

    two phi-shaped systems begin interacting -> coupling should reduce
    their imbalance toward a more neutral/balanced state.

The three candidates are intentionally different:
  1. Solar north/south hemispheres: long, slow real coupled oscillator.
  2. Heart/respiration: biological phase coupling from a real BIDMC record.
  3. Tides: clean lunar/solar forcing benchmark for amplitude breathing.

Leakage guard:
  - Download/cache is data access only, not model fitting.
  - All thresholds, lags, and linear scales are fitted on train windows only.
  - Test windows are strictly later than train windows.
  - Future targets are never used to choose thresholds or lags.
"""

from __future__ import annotations

import csv
import json
import math
import re
import ssl
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.signal import butter, filtfilt, find_peaks


HERE = Path(__file__).resolve().parent
CACHE = HERE / "data_cache"
OUT_JSON = HERE / "ara_phi_coupling_candidate_results.json"
OUT_JS = HERE / "ara_phi_coupling_candidate_results.js"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
EPS = 1e-9


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def corr(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    good = np.isfinite(x) & np.isfinite(y)
    x = x[good]
    y = y[good]
    if len(x) < 5 or float(np.std(x)) < 1e-12 or float(np.std(y)) < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def summarize(values):
    vals = np.asarray(values, dtype=float)
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return {"n": 0}
    return {
        "n": int(len(vals)),
        "mean": float(np.mean(vals)),
        "std": float(np.std(vals)),
        "p25": float(np.percentile(vals, 25)),
        "p50": float(np.percentile(vals, 50)),
        "p75": float(np.percentile(vals, 75)),
    }


def metric_score(pred, actual, baseline):
    pred = np.asarray(pred, dtype=float)
    actual = np.asarray(actual, dtype=float)
    baseline = np.asarray(baseline, dtype=float)
    good = np.isfinite(pred) & np.isfinite(actual) & np.isfinite(baseline)
    pred = pred[good]
    actual = actual[good]
    baseline = baseline[good]
    if len(pred) == 0:
        return {"n": 0}
    mae = float(np.mean(np.abs(pred - actual)))
    base_mae = float(np.mean(np.abs(baseline - actual)))
    return {
        "n": int(len(pred)),
        "mae": mae,
        "baseline_mae": base_mae,
        "mae_lift_vs_baseline": base_mae - mae,
        "corr": corr(pred, actual),
    }


def ridge_fit(rows, y, alpha=1e-6):
    x = np.asarray(rows, dtype=float)
    y = np.asarray(y, dtype=float)
    good = np.isfinite(y) & np.all(np.isfinite(x), axis=1)
    x = x[good]
    y = y[good]
    if len(y) == 0:
        return np.zeros((x.shape[1] + 1 if x.ndim == 2 else 1,), dtype=float)
    x1 = np.column_stack([np.ones(len(x)), x])
    reg = np.eye(x1.shape[1]) * alpha
    reg[0, 0] = 0.0
    try:
        return np.linalg.solve(x1.T @ x1 + reg, x1.T @ y)
    except np.linalg.LinAlgError:
        beta, *_ = np.linalg.lstsq(x1.T @ x1 + reg, x1.T @ y, rcond=None)
        return beta


def ridge_predict(beta, rows):
    x = np.asarray(rows, dtype=float)
    if len(x) == 0:
        return np.asarray([], dtype=float)
    x1 = np.column_stack([np.ones(len(x)), x])
    return x1 @ np.asarray(beta, dtype=float)


def download_text(url, cache_name, min_chars=100):
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE / cache_name
    if cache_path.exists() and cache_path.stat().st_size >= min_chars:
        return cache_path.read_text(encoding="utf-8", errors="replace"), str(cache_path), "cache"

    req = urllib.request.Request(url, headers={"User-Agent": "ARA-candidate-test/1.0"})
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=30, context=context) as resp:
        raw = resp.read()
    text = raw.decode("utf-8", errors="replace")
    if len(text) < min_chars:
        raise RuntimeError(f"Downloaded too little data from {url}")
    cache_path.write_text(text, encoding="utf-8")
    return text, str(cache_path), url


def butter_bandpass(values, fs, lo, hi, order=3):
    arr = np.asarray(values, dtype=float)
    arr = arr - np.nanmean(arr)
    nyq = fs / 2.0
    lo = max(lo / nyq, 1e-5)
    hi = min(hi / nyq, 0.999)
    b, a = butter(order, [lo, hi], btype="band")
    return filtfilt(b, a, arr)


def moving_average(values, window):
    arr = np.asarray(values, dtype=float)
    if window <= 1:
        return arr.copy()
    kernel = np.ones(int(window), dtype=float) / float(window)
    return np.convolve(arr, kernel, mode="same")


def exp_phi_score(*aras, scale=0.45):
    vals = [finite(a, float("nan")) for a in aras]
    vals = [v for v in vals if math.isfinite(v) and v > 0]
    if not vals:
        return 0.0
    return float(math.exp(-np.mean([abs(v - PHI) for v in vals]) / scale))


def median_positive(values, fallback):
    vals = np.asarray([finite(v, float("nan")) for v in values], dtype=float)
    vals = vals[np.isfinite(vals) & (vals > 0)]
    if len(vals) == 0:
        return float(fallback)
    return float(np.median(vals))


def balance_flow_metrics(event, nonevent, horizon, cycle_period, metric_key, future_key, kind, rung_denominator=None):
    event_change = np.asarray([finite(r[future_key] - r[metric_key], float("nan")) for r in event], dtype=float)
    nonevent_change = np.asarray([finite(r[future_key] - r[metric_key], float("nan")) for r in nonevent], dtype=float)
    event_current = np.asarray([finite(r[metric_key], float("nan")) for r in event], dtype=float)
    current_scale = median_positive(np.abs(event_current), fallback=1.0)

    event_mean = float(np.nanmean(event_change)) if len(event_change) else float("nan")
    nonevent_mean = float(np.nanmean(nonevent_change)) if len(nonevent_change) else float("nan")
    signed_toward_per_tick = -event_mean / max(float(horizon), EPS)
    relative_damping_per_tick = (nonevent_mean - event_mean) / max(float(horizon), EPS)
    signed_toward_per_cycle = signed_toward_per_tick * float(cycle_period)
    relative_damping_per_cycle = relative_damping_per_tick * float(cycle_period)
    fractional_toward_per_cycle = float(signed_toward_per_cycle / max(current_scale, EPS))

    if rung_denominator is None:
        rung_denominator = max(math.log(max(float(cycle_period), 1.0), PHI), EPS)
    flow_density = signed_toward_per_cycle / max(float(rung_denominator), EPS)
    fractional_flow_density = fractional_toward_per_cycle / max(float(rung_denominator), EPS)

    return {
        "kind": kind,
        "horizon_ticks": float(horizon),
        "cycle_period_ticks": float(cycle_period),
        "time_rung_phi": float(rung_denominator),
        "event_current_metric_scale_median_abs": float(current_scale),
        "signed_toward_balance_per_tick": float(signed_toward_per_tick),
        "signed_toward_balance_per_cycle": float(signed_toward_per_cycle),
        "fractional_toward_balance_per_cycle": float(fractional_toward_per_cycle),
        "rung_density_signed": float(flow_density),
        "rung_density_fractional": float(fractional_flow_density),
        "relative_damping_per_tick": float(relative_damping_per_tick),
        "relative_damping_per_cycle": float(relative_damping_per_cycle),
    }


def detect_silso_ns_columns(rows):
    arr = np.asarray(rows, dtype=float)
    n_cols = arr.shape[1]
    # Prefer known SILSO monthly hemispheric layouts.
    known = [
        (4, 5),  # fixed-width Catalogue B: smoothed north/south after monthly values
        (4, 6),  # common text layout: total, north, north_std, south, south_std
        (5, 7),
        (3, 4),  # extended catalogue smoothed north/south after date columns
    ]
    for ni, si in known:
        if ni < n_cols and si < n_cols:
            n = arr[:, ni]
            s = arr[:, si]
            valid = np.isfinite(n) & np.isfinite(s) & (n >= 0) & (s >= 0)
            if int(valid.sum()) > max(24, 0.5 * len(arr)) and float(np.nanstd(n[valid] + s[valid])) > 1.0:
                return ni, si

    best = None
    for ni in range(3, n_cols):
        for si in range(ni + 1, n_cols):
            n = arr[:, ni]
            s = arr[:, si]
            valid = np.isfinite(n) & np.isfinite(s) & (n >= 0) & (s >= 0)
            if int(valid.sum()) < max(24, 0.5 * len(arr)):
                continue
            both = n[valid] + s[valid]
            if float(np.nanmedian(both)) < 1.0 or float(np.nanstd(both)) < 1.0:
                continue
            balance = np.nanmedian(np.minimum(n[valid], s[valid]) / (np.maximum(n[valid], s[valid]) + EPS))
            score = float(np.nanstd(both)) + 20.0 * float(balance)
            if best is None or score > best[0]:
                best = (score, ni, si)
    if best is None:
        raise RuntimeError("Could not detect north/south columns in SILSO data")
    return best[1], best[2]


def parse_silso_hemi(text):
    numeric_rows = []
    dates = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Catalogue_B.txt is fixed-width: YYYY/MM followed by 5-character values.
        if re.match(r"^\d{4}/\d{2}", line) and ";" not in line and "," not in line:
            year = int(line[0:4])
            month = int(line[5:7])
            nums = [year, month]
            for i in range(7, len(line), 5):
                chunk = line[i:i + 5].strip()
                if not chunk:
                    continue
                try:
                    nums.append(float(chunk))
                except ValueError:
                    nums.append(float("nan"))
            if len(nums) >= 6:
                numeric_rows.append(nums)
                dates.append(f"{year:04d}-{month:02d}")
            continue

        parts = re.split(r"[;\s,]+", line)
        nums = []
        if re.match(r"^\d{4}[-/]\d{2}$", parts[0]):
            year, month = [int(x) for x in re.split(r"[-/]", parts[0])]
            nums.extend([year, month])
            tail = parts[1:]
        else:
            tail = parts
        for part in tail:
            try:
                nums.append(float(part))
            except ValueError:
                pass
        if len(nums) >= 6:
            numeric_rows.append(nums)
            year = int(nums[0])
            month = int(nums[1]) if len(nums) > 1 and 1 <= int(nums[1]) <= 12 else 1
            dates.append(f"{year:04d}-{month:02d}")

    width = min(len(r) for r in numeric_rows)
    rows = [r[:width] for r in numeric_rows]
    ni, si = detect_silso_ns_columns(rows)
    arr = np.asarray(rows, dtype=float)
    north = arr[:, ni]
    south = arr[:, si]
    good = np.isfinite(north) & np.isfinite(south) & (north >= 0) & (south >= 0)
    return [d for d, g in zip(dates, good) if g], north[good], south[good], {"north_col": ni, "south_col": si}


def load_solar_hemi():
    candidates = [
        (
            "SILSO extended monthly hemispheric Catalogue B",
            "https://www.sidc.be/SILSO/DATA/HEMI/Veronig/Catalogue_B.txt",
            "Catalogue_B.txt",
        ),
        (
            "SILSO monthly smoothed hemispheric sunspot numbers",
            "https://www.sidc.be/SILSO/DATA/SN_ms_hem_V2.0.txt",
            "SN_ms_hem_V2.0.txt",
        ),
        (
            "SILSO monthly hemispheric sunspot numbers",
            "https://www.sidc.be/SILSO/DATA/SN_m_hem_V2.0.txt",
            "SN_m_hem_V2.0.txt",
        ),
    ]
    errors = []
    for label, url, cache_name in candidates:
        try:
            text, source_path, source_kind = download_text(url, cache_name, min_chars=1000)
            dates, north, south, meta = parse_silso_hemi(text)
            if len(north) >= 240:
                meta.update({"source": label, "source_path": source_path, "source_kind": source_kind})
                return dates, north, south, meta
            errors.append(f"{label}: only {len(north)} rows")
        except Exception as exc:
            errors.append(f"{label}: {exc}")
    raise RuntimeError("; ".join(errors))


def cycle_ara_series(values, min_distance=72):
    arr = moving_average(values, 13)
    prominence = max(3.0, float(np.nanstd(arr)) * 0.18)
    peaks, _ = find_peaks(arr, distance=min_distance, prominence=prominence)
    troughs, _ = find_peaks(-arr, distance=min_distance, prominence=max(1.0, prominence * 0.35))
    ara = np.full(len(arr), np.nan, dtype=float)
    cycles = []
    for peak in peaks:
        prev_troughs = troughs[troughs < peak]
        next_troughs = troughs[troughs > peak]
        if len(prev_troughs) == 0 or len(next_troughs) == 0:
            continue
        start = int(prev_troughs[-1])
        end = int(next_troughs[0])
        rise = float(peak - start)
        fall = float(end - peak)
        if rise <= 0 or fall <= 0:
            continue
        ratio = fall / rise
        if 0.2 <= ratio <= 6.0:
            ara[start:end + 1] = ratio
            cycles.append({"start": start, "peak": int(peak), "end": end, "ara": float(ratio)})
    return ara, cycles


def run_solar_test():
    dates, north, south, meta = load_solar_hemi()
    north = moving_average(north, 5)
    south = moving_average(south, 5)
    total = north + south + EPS
    coupling = 2.0 * np.minimum(north, south) / total
    balance_error = np.abs(np.log((north + 0.5) / (south + 0.5)))
    ara_n, cycles_n = cycle_ara_series(north)
    ara_s, cycles_s = cycle_ara_series(south)

    horizon = 24
    rows = []
    for t in range(24, len(north) - horizon):
        if not (np.isfinite(ara_n[t]) and np.isfinite(ara_s[t])):
            continue
        c_delta = coupling[t] - float(np.mean(coupling[max(0, t - 12):t]))
        phi_score = exp_phi_score(ara_n[t], ara_s[t])
        rows.append(
            {
                "t": t,
                "date": dates[t],
                "current_error": float(balance_error[t]),
                "future_error": float(balance_error[t + horizon]),
                "coupling": float(coupling[t]),
                "coupling_delta": float(c_delta),
                "phi_score": float(phi_score),
                "ara_n": float(ara_n[t]),
                "ara_s": float(ara_s[t]),
            }
        )

    split = int(0.60 * len(rows))
    train = rows[:split]
    test = rows[split:]
    if len(train) < 30 or len(test) < 10:
        raise RuntimeError("Not enough solar rows after cycle ARA assignment")

    x_train = [[r["current_error"], r["coupling"], r["coupling_delta"], r["phi_score"]] for r in train]
    y_train = [r["future_error"] for r in train]
    x_test = [[r["current_error"], r["coupling"], r["coupling_delta"], r["phi_score"]] for r in test]
    y_test = [r["future_error"] for r in test]
    baseline = [r["current_error"] for r in test]
    beta = ridge_fit(x_train, y_train, alpha=1e-3)
    preds = ridge_predict(beta, x_test)

    train_delta = np.asarray([r["coupling_delta"] for r in train], dtype=float)
    train_phi = np.asarray([r["phi_score"] for r in train], dtype=float)
    delta_threshold = float(np.percentile(train_delta, 75))
    phi_threshold = float(np.percentile(train_phi, 50))
    event = [
        r for r in test
        if r["coupling_delta"] >= delta_threshold and r["phi_score"] >= phi_threshold
    ]
    nonevent = [
        r for r in test
        if not (r["coupling_delta"] >= delta_threshold and r["phi_score"] >= phi_threshold)
    ]
    event_change = [r["future_error"] - r["current_error"] for r in event]
    nonevent_change = [r["future_error"] - r["current_error"] for r in nonevent]
    event_mean = float(np.nanmean(event_change)) if len(event_change) else float("nan")
    nonevent_mean = float(np.nanmean(nonevent_change)) if len(nonevent_change) else float("nan")
    cycle_period_months = median_positive(
        [c["end"] - c["start"] for c in cycles_n] + [c["end"] - c["start"] for c in cycles_s],
        fallback=132.0,
    )

    return {
        "name": "solar_north_south",
        "status": "ok",
        "source": meta,
        "n_months": int(len(north)),
        "date_range": [dates[0], dates[-1]],
        "horizon_months": horizon,
        "leakage_guard": "Thresholds/model trained on first 60% of valid windows; evaluated only on later windows.",
        "cycles": {
            "north": cycles_n,
            "south": cycles_s,
            "north_ara": summarize([c["ara"] for c in cycles_n]),
            "south_ara": summarize([c["ara"] for c in cycles_s]),
        },
        "heldout_model": metric_score(preds, y_test, baseline),
        "event_rule": {
            "coupling_delta_threshold_train_q75": delta_threshold,
            "phi_score_threshold_train_q50": phi_threshold,
            "event_change_future_minus_current": summarize(event_change),
            "nonevent_change_future_minus_current": summarize(nonevent_change),
            "supports_relative_damping": bool(len(event_change) >= 3 and event_mean < nonevent_mean),
            "supports_absolute_relaxation": bool(len(event_change) >= 3 and event_mean < 0.0),
            "supports_relaxation": bool(len(event_change) >= 3 and event_mean < 0.0),
        },
        "speed_metrics": balance_flow_metrics(
            event,
            nonevent,
            horizon=horizon,
            cycle_period=cycle_period_months,
            metric_key="current_error",
            future_key="future_error",
            kind="balance_relaxation",
        ),
        "sample_rows": test[:8],
    }


def parse_bidmc_csv(text):
    rows = list(csv.reader(text.splitlines()))
    header = [h.strip() for h in rows[0]]
    cols = {h: [] for h in header}
    for row in rows[1:]:
        if len(row) != len(header):
            continue
        for h, v in zip(header, row):
            try:
                cols[h].append(float(v))
            except ValueError:
                cols[h].append(float("nan"))
    lower = [h.lower() for h in header]
    time_col = next((header[i] for i, h in enumerate(lower) if "time" in h), None)
    resp_col = next((header[i] for i, h in enumerate(lower) if "resp" in h), None)
    ecg_col = next((header[i] for i, h in enumerate(lower) if h in {"ii", "ecg", "v", "avr"} or "ecg" in h), None)
    if resp_col is None:
        raise RuntimeError(f"No RESP column found in BIDMC header: {header}")
    if ecg_col is None:
        raise RuntimeError(f"No ECG-like column found in BIDMC header: {header}")
    t = np.asarray(cols[time_col], dtype=float) if time_col else np.arange(len(cols[resp_col])) / 125.0
    resp = np.asarray(cols[resp_col], dtype=float)
    ecg = np.asarray(cols[ecg_col], dtype=float)
    good = np.isfinite(t) & np.isfinite(resp) & np.isfinite(ecg)
    return t[good], ecg[good], resp[good], {"columns": header, "time_col": time_col, "ecg_col": ecg_col, "resp_col": resp_col}


def load_bidmc_record():
    url = "https://physionet.org/files/bidmc/1.0.0/bidmc_csv/bidmc_01_Signals.csv"
    text, source_path, source_kind = download_text(url, "bidmc_01_Signals.csv", min_chars=10000)
    t, ecg, resp, meta = parse_bidmc_csv(text)
    meta.update({"source": "PhysioNet BIDMC PPG and Respiration Dataset, record 01 signals CSV", "source_path": source_path, "source_kind": source_kind})
    return t, ecg, resp, meta


def choose_ecg_peaks(ecg_filtered, fs):
    distance = max(1, int(0.30 * fs))
    prom = max(float(np.std(ecg_filtered)) * 0.45, EPS)
    pos, _ = find_peaks(ecg_filtered, distance=distance, prominence=prom)
    neg, _ = find_peaks(-ecg_filtered, distance=distance, prominence=prom)
    def plausible(peaks):
        if len(peaks) < 10:
            return -1e9
        rr = np.diff(peaks) / fs
        ok = (rr > 0.30) & (rr < 2.0)
        return float(ok.mean()) * len(peaks)
    return pos if plausible(pos) >= plausible(neg) else neg


def respiration_cycles(resp_filtered, fs):
    distance = max(1, int(1.4 * fs))
    prom = max(float(np.std(resp_filtered)) * 0.22, EPS)
    peaks, _ = find_peaks(resp_filtered, distance=distance, prominence=prom)
    troughs, _ = find_peaks(-resp_filtered, distance=distance, prominence=prom)
    cycles = []
    for i in range(len(troughs) - 1):
        start = int(troughs[i])
        end = int(troughs[i + 1])
        mid_peaks = peaks[(peaks > start) & (peaks < end)]
        if len(mid_peaks) == 0:
            continue
        peak = int(mid_peaks[np.argmax(resp_filtered[mid_peaks])])
        inhale = (peak - start) / fs
        exhale = (end - peak) / fs
        period = (end - start) / fs
        if 1.0 <= period <= 12.0 and inhale > 0.2 and exhale > 0.2:
            cycles.append({"start": start, "peak": peak, "end": end, "ara_resp": float(exhale / inhale)})
    return cycles


def phase_at_samples(samples, cycles):
    phase = np.full(len(samples), np.nan, dtype=float)
    ci = 0
    for j, sample in enumerate(samples):
        while ci < len(cycles) and sample > cycles[ci]["end"]:
            ci += 1
        if ci >= len(cycles):
            break
        c = cycles[ci]
        if c["start"] <= sample <= c["end"]:
            if sample <= c["peak"]:
                phase[j] = 0.5 * (sample - c["start"]) / max(1, c["peak"] - c["start"])
            else:
                phase[j] = 0.5 + 0.5 * (sample - c["peak"]) / max(1, c["end"] - c["peak"])
    return phase


def heart_ara_by_breath(t, rr_interp, cycles, fs):
    out = []
    for c in cycles:
        start = c["start"]
        end = c["end"]
        if end <= start + 3:
            continue
        segment = rr_interp[start:end + 1]
        if len(segment) < 5 or np.nanstd(segment) < 1e-6:
            continue
        peak_local = int(np.nanargmax(segment))
        peak = start + peak_local
        acc = (peak - start) / fs
        rel = (end - peak) / fs
        if acc > 0.15 and rel > 0.15:
            out.append({"time": float(t[peak]), "ara_heart": float(acc / rel), "cycle_start": float(t[start]), "cycle_end": float(t[end])})
    return out


def run_heart_resp_test():
    t, ecg, resp, meta = load_bidmc_record()
    fs = 1.0 / float(np.median(np.diff(t)))
    ecg_f = butter_bandpass(ecg, fs, 5.0, 30.0, order=2)
    resp_f = butter_bandpass(resp, fs, 0.05, 0.7, order=2)
    r_peaks = choose_ecg_peaks(ecg_f, fs)
    if len(r_peaks) < 80:
        raise RuntimeError("Too few ECG peaks detected")
    rr = np.diff(t[r_peaks])
    rr_times = t[r_peaks[1:]]
    good_rr = (rr > 0.30) & (rr < 2.0)
    rr = rr[good_rr]
    rr_times = rr_times[good_rr]
    rr_interp = np.interp(t, rr_times, rr, left=float(np.nanmedian(rr)), right=float(np.nanmedian(rr)))

    cycles = respiration_cycles(resp_f, fs)
    if len(cycles) < 20:
        raise RuntimeError("Too few respiration cycles detected")
    phase_at_r = phase_at_samples(r_peaks, cycles)
    heart_aras = heart_ara_by_breath(t, rr_interp, cycles, fs)

    # Rolling windows. Future gap is only used as the target after model/threshold selection.
    window_s = 60.0
    step_s = 5.0
    horizon_s = 30.0
    start_t = max(t[0] + window_s, t[0] + 90.0)
    end_t = t[-1] - horizon_s - window_s
    rows = []
    cursor = start_t
    while cursor <= end_t:
        w0 = cursor - window_s
        w1 = cursor
        rmask = (t[r_peaks] >= w0) & (t[r_peaks] <= w1) & np.isfinite(phase_at_r)
        if int(rmask.sum()) < 20:
            cursor += step_s
            continue
        phases = phase_at_r[rmask]
        plv = abs(np.mean(np.exp(1j * 2.0 * np.pi * phases)))
        resp_vals = [c["ara_resp"] for c in cycles if w0 <= t[c["peak"]] <= w1]
        heart_vals = [h["ara_heart"] for h in heart_aras if w0 <= h["time"] <= w1]
        if len(resp_vals) < 3 or len(heart_vals) < 3:
            cursor += step_s
            continue
        ara_resp = float(np.median(resp_vals))
        ara_heart = float(np.median(heart_vals))
        gap = abs(math.log(max(ara_heart, EPS) / max(ara_resp, EPS)))
        rows.append(
            {
                "time_s": float(cursor),
                "gap": float(gap),
                "coupling": float(plv),
                "ara_resp": ara_resp,
                "ara_heart": ara_heart,
                "phi_score": exp_phi_score(ara_resp, ara_heart),
            }
        )
        cursor += step_s

    by_time = {round(r["time_s"], 6): r for r in rows}
    paired = []
    for r in rows:
        fkey = round(r["time_s"] + horizon_s, 6)
        if fkey not in by_time:
            continue
        future = by_time[fkey]
        idx = rows.index(r)
        prev_c = rows[idx - 1]["coupling"] if idx > 0 else r["coupling"]
        item = dict(r)
        item["future_gap"] = future["gap"]
        item["coupling_delta"] = r["coupling"] - prev_c
        paired.append(item)

    split = int(0.60 * len(paired))
    train = paired[:split]
    test = paired[split:]
    if len(train) < 20 or len(test) < 10:
        raise RuntimeError("Not enough heart/respiration windows")
    x_train = [[r["gap"], r["coupling"], r["coupling_delta"], r["phi_score"]] for r in train]
    y_train = [r["future_gap"] for r in train]
    x_test = [[r["gap"], r["coupling"], r["coupling_delta"], r["phi_score"]] for r in test]
    y_test = [r["future_gap"] for r in test]
    baseline = [r["gap"] for r in test]
    beta = ridge_fit(x_train, y_train, alpha=1e-3)
    preds = ridge_predict(beta, x_test)

    delta_threshold = float(np.percentile([r["coupling_delta"] for r in train], 75))
    phi_threshold = float(np.percentile([r["phi_score"] for r in train], 50))
    event = [r for r in test if r["coupling_delta"] >= delta_threshold and r["phi_score"] >= phi_threshold]
    nonevent = [r for r in test if not (r["coupling_delta"] >= delta_threshold and r["phi_score"] >= phi_threshold)]
    event_change = [r["future_gap"] - r["gap"] for r in event]
    nonevent_change = [r["future_gap"] - r["gap"] for r in nonevent]
    event_mean = float(np.nanmean(event_change)) if len(event_change) else float("nan")
    nonevent_mean = float(np.nanmean(nonevent_change)) if len(nonevent_change) else float("nan")
    resp_period_s = median_positive([(c["end"] - c["start"]) / fs for c in cycles], fallback=(t[-1] - t[0]) / max(len(cycles), 1))

    return {
        "name": "heart_respiration_bidmc01",
        "status": "ok",
        "source": meta,
        "fs_hz": float(fs),
        "duration_s": float(t[-1] - t[0]),
        "n_r_peaks": int(len(r_peaks)),
        "n_resp_cycles": int(len(cycles)),
        "horizon_s": horizon_s,
        "leakage_guard": "Thresholds/model trained on first 60% of rolling windows; evaluated only on later windows.",
        "ara_resp": summarize([c["ara_resp"] for c in cycles]),
        "ara_heart_by_breath": summarize([h["ara_heart"] for h in heart_aras]),
        "heldout_model": metric_score(preds, y_test, baseline),
        "event_rule": {
            "coupling_delta_threshold_train_q75": delta_threshold,
            "phi_score_threshold_train_q50": phi_threshold,
            "event_change_future_minus_current": summarize(event_change),
            "nonevent_change_future_minus_current": summarize(nonevent_change),
            "supports_relative_damping": bool(len(event_change) >= 3 and event_mean < nonevent_mean),
            "supports_absolute_relaxation": bool(len(event_change) >= 3 and event_mean < 0.0),
            "supports_relaxation": bool(len(event_change) >= 3 and event_mean < 0.0),
        },
        "speed_metrics": balance_flow_metrics(
            event,
            nonevent,
            horizon=horizon_s,
            cycle_period=resp_period_s,
            metric_key="gap",
            future_key="future_gap",
            kind="balance_relaxation",
        ),
        "sample_rows": test[:8],
    }


def load_noaa_tide_or_synthetic():
    url = (
        "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
        "?begin_date=20240101&end_date=20241231&station=9414290"
        "&product=hourly_height&datum=MLLW&time_zone=gmt&units=metric&format=json"
    )
    try:
        text, source_path, source_kind = download_text(url, "noaa_9414290_hourly_2024.json", min_chars=10000)
        payload = json.loads(text)
        data = payload.get("data", [])
        vals = []
        dates = []
        for row in data:
            try:
                vals.append(float(row["v"]))
                dates.append(row["t"])
            except (KeyError, ValueError):
                pass
        if len(vals) < 1000:
            raise RuntimeError("NOAA response had too few water-level rows")
        return np.asarray(vals, dtype=float), dates, {
            "source": f"NOAA CO-OPS hourly water level, station 9414290, {dates[0]} to {dates[-1]}",
            "requested": "2024-01-01 to 2024-12-31",
            "source_path": source_path,
            "source_kind": source_kind,
            "synthetic": False,
        }
    except Exception as exc:
        hours = np.arange(0, 24 * 365, dtype=float)
        m2 = np.sin(2.0 * np.pi * hours / 12.4206012)
        s2 = 0.46 * np.sin(2.0 * np.pi * hours / 12.0 + 0.4)
        k1 = 0.20 * np.sin(2.0 * np.pi * hours / 23.934472)
        o1 = 0.13 * np.sin(2.0 * np.pi * hours / 25.819338)
        noise = 0.03 * np.sin(2.0 * np.pi * hours / (24.0 * 9.0))
        vals = m2 + s2 + k1 + o1 + noise
        dates = [f"synthetic_hour_{int(h)}" for h in hours]
        return vals, dates, {"source": "synthetic harmonic tide fallback because NOAA download failed", "error": str(exc), "synthetic": True}


def causal_tide_range(values, window=25):
    vals = np.asarray(values, dtype=float)
    out = np.full(len(vals), np.nan, dtype=float)
    for i in range(window, len(vals)):
        segment = vals[i - window:i + 1]
        out[i] = float(np.nanmax(segment) - np.nanmin(segment))
    return out


def shifted_feature(feature, lag):
    arr = np.asarray(feature, dtype=float)
    out = np.full(len(arr), np.nan, dtype=float)
    if lag >= 0:
        out[lag:] = arr[: len(arr) - lag]
    else:
        out[:lag] = arr[-lag:]
    return out


def run_tide_test():
    values, dates, meta = load_noaa_tide_or_synthetic()
    hours = np.arange(len(values), dtype=float)
    tide_range = causal_tide_range(values, window=25)

    m2_phase = 2.0 * np.pi * hours / 12.4206012
    s2_phase = 2.0 * np.pi * hours / 12.0
    delta = (m2_phase - s2_phase + np.pi) % (2.0 * np.pi) - np.pi
    # This is the geometry gate for the tide benchmark: the amplitude of the
    # lunar and solar semidiurnal forcing pair as their phases align/cancel.
    solar_amp = 0.46
    vector_gate = np.sqrt(1.0 + solar_amp**2 + 2.0 * solar_amp * np.cos(delta))
    gate = (vector_gate - np.nanmin(vector_gate)) / max(EPS, np.nanmax(vector_gate) - np.nanmin(vector_gate))

    split_index = int(0.60 * len(values))
    train_idx = np.arange(48, split_index)
    good_train = np.isfinite(tide_range[train_idx])
    train_idx = train_idx[good_train]
    best = None
    for lag in range(-48, 49):
        shifted = shifted_feature(gate, lag)
        x = shifted[train_idx]
        y = tide_range[train_idx]
        c = corr(x, y)
        if best is None or c > best[0]:
            best = (c, lag)
    best_corr, best_lag = best
    shifted_gate = shifted_feature(gate, best_lag)

    rows = []
    for t in range(max(48, abs(best_lag) + 1), len(values) - 1):
        if not (np.isfinite(tide_range[t]) and np.isfinite(shifted_gate[t]) and np.isfinite(tide_range[t - 24])):
            continue
        rows.append(
            {
                "t": t,
                "date": dates[t],
                "range": float(tide_range[t]),
                "gate": float(shifted_gate[t]),
                "persistence": float(tide_range[t - 24]),
            }
        )
    train = [r for r in rows if r["t"] < split_index]
    test = [r for r in rows if r["t"] >= split_index]
    if len(train) < 200 or len(test) < 100:
        raise RuntimeError("Not enough tide rows")

    beta = ridge_fit([[r["gate"]] for r in train], [r["range"] for r in train], alpha=1e-6)
    preds = ridge_predict(beta, [[r["gate"]] for r in test])
    y_test = [r["range"] for r in test]
    baseline = [r["persistence"] for r in test]

    train_gate = np.asarray([r["gate"] for r in train], dtype=float)
    high_thr = float(np.percentile(train_gate, 80))
    low_thr = float(np.percentile(train_gate, 20))
    high = [r["range"] for r in test if r["gate"] >= high_thr]
    low = [r["range"] for r in test if r["gate"] <= low_thr]
    high_mean = float(np.nanmean(high)) if len(high) else float("nan")
    low_mean = float(np.nanmean(low)) if len(low) else float("nan")
    half_spring_neap_hours = 14.765294 * 24.0 / 2.0
    spring_neap_hours = 14.765294 * 24.0
    semidiurnal_hours = 12.4206012
    range_mid = (high_mean + low_mean) / 2.0
    range_fraction = (high_mean - low_mean) / max(abs(range_mid), EPS)
    fractional_speed_per_hour = range_fraction / half_spring_neap_hours
    fractional_per_spring_neap_cycle = fractional_speed_per_hour * spring_neap_hours
    inter_rung_phi = math.log(spring_neap_hours / semidiurnal_hours, PHI)

    return {
        "name": "tide_lunar_solar_triangle_gate",
        "status": "ok",
        "source": meta,
        "n_hours": int(len(values)),
        "date_range": [dates[0], dates[-1]],
        "leakage_guard": "Best lag and scale fitted on first 60%; held-out test is later data only.",
        "best_lag_hours_train_only": int(best_lag),
        "train_gate_range_corr_at_best_lag": float(best_corr),
        "heldout_model": metric_score(preds, y_test, baseline),
        "amplitude_breathing": {
            "high_gate_threshold_train_q80": high_thr,
            "low_gate_threshold_train_q20": low_thr,
            "heldout_high_gate_range": summarize(high),
            "heldout_low_gate_range": summarize(low),
            "supports_amplitude_breathing": bool(len(high) >= 5 and len(low) >= 5 and np.nanmean(high) > np.nanmean(low)),
        },
        "speed_metrics": {
            "kind": "amplitude_breathing",
            "carrier_period_hours": semidiurnal_hours,
            "cycle_period_hours": spring_neap_hours,
            "half_cycle_hours": half_spring_neap_hours,
            "time_rung_phi_carrier_to_modulation": inter_rung_phi,
            "high_low_range_difference_m": float(high_mean - low_mean),
            "fractional_range_difference": float(range_fraction),
            "fractional_speed_per_hour": float(fractional_speed_per_hour),
            "fractional_per_spring_neap_cycle": float(fractional_per_spring_neap_cycle),
            "rung_density_fractional": float(fractional_per_spring_neap_cycle / max(inter_rung_phi, EPS)),
        },
        "sample_rows": test[:8],
    }


def run_test(label, func):
    print(f"\n=== {label} ===", flush=True)
    try:
        result = func()
        print(f"status: {result['status']}", flush=True)
        return result
    except Exception as exc:
        print(f"status: skipped ({exc})", flush=True)
        return {"name": label, "status": "skipped", "error": str(exc)}


def main():
    results = {
        "description": "Phi-coupling candidate tests: solar hemispheres, heart/respiration, tides.",
        "phi": PHI,
        "leakage_summary": [
            "Data are cached before analysis; cache contents are not used for fitting decisions.",
            "Thresholds/lags/models are fitted on train windows only.",
            "All reported model metrics are held-out later windows.",
            "Event rules use thresholds chosen on train only.",
        ],
        "tests": {},
    }
    results["tests"]["solar_north_south"] = run_test("solar_north_south", run_solar_test)
    results["tests"]["heart_respiration"] = run_test("heart_respiration", run_heart_resp_test)
    results["tests"]["tides"] = run_test("tides", run_tide_test)

    OUT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    OUT_JS.write_text("window.ARA_PHI_COUPLING_RESULTS = " + json.dumps(results, indent=2) + ";\n", encoding="utf-8")
    print(f"\nWrote {OUT_JSON}", flush=True)
    print(f"Wrote {OUT_JS}", flush=True)

    print("\nSUMMARY", flush=True)
    for name, result in results["tests"].items():
        if result.get("status") != "ok":
            print(f"  {name}: skipped - {result.get('error')}", flush=True)
            continue
        model = result.get("heldout_model", {})
        event = result.get("event_rule") or result.get("amplitude_breathing") or {}
        support = event.get("supports_relaxation", event.get("supports_amplitude_breathing"))
        print(
            f"  {name}: n={model.get('n', 0)} "
            f"MAE={model.get('mae', float('nan')):.5g} "
            f"base={model.get('baseline_mae', float('nan')):.5g} "
            f"lift={model.get('mae_lift_vs_baseline', float('nan')):+.5g} "
            f"corr={model.get('corr', float('nan')):+.3f} "
            f"support={support}",
            flush=True,
        )


if __name__ == "__main__":
    main()

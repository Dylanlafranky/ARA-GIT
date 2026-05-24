"""
ara_ecg_solar_temporal_geometry_test.py

ECG <-> Solar time-scaled temporal-geometry check.

This is a descriptive geometry test, not a forward forecast. Leakage guard:
  - Uses only cached public data already on disk.
  - Detection thresholds are fixed before scoring, not optimized to match.
  - Chronological train/test splits are made independently per system.
  - Any circular phase shift used for correlation is learned on train templates
    only, then applied unchanged to held-out templates.
  - Fourier geometry distance is phase-shift invariant, so it does not need a
    fitted alignment parameter.

Primary ECG representation:
  R-R interval cycles from the ECG, because this is the "ECG as a temporal
  system" signal used in most formula tests.

Secondary ECG representation:
  Raw R-centered ECG beat waveform, included to check whether the result depends
  on comparing the PQRST electrical spike directly.
"""

from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import butter, find_peaks, sosfiltfilt


HERE = Path(__file__).resolve().parent
CACHE = HERE / "data_cache"
OUT_JSON = HERE / "ara_ecg_solar_temporal_geometry_result.json"
OUT_JS = HERE / "ara_ecg_solar_temporal_geometry_result.js"

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
    if not math.isfinite(lo) or not math.isfinite(hi) or hi - lo < EPS:
        return np.zeros_like(x, dtype=float)
    return (x - lo) / (hi - lo)


def zscore(x):
    x = np.asarray(x, dtype=float)
    return (x - float(np.mean(x))) / (float(np.std(x)) + EPS)


def resample_segment(segment, n=N_PHASE):
    segment = np.asarray(segment, dtype=float)
    xo = np.linspace(0.0, 1.0, len(segment))
    xn = np.linspace(0.0, 1.0, n)
    return minmax(np.interp(xn, xo, segment))


def mean_template(cycles):
    if len(cycles) == 0:
        return np.zeros(N_PHASE, dtype=float)
    return minmax(np.mean(np.asarray(cycles, dtype=float), axis=0))


def split_cycles(cycles, train_frac=0.70):
    cycles = list(cycles)
    cut = max(1, min(len(cycles) - 1, int(math.floor(len(cycles) * train_frac))))
    return cycles[:cut], cycles[cut:]


def best_circular_shift(target, candidate):
    scores = [corr(target, np.roll(candidate, k)) for k in range(len(candidate))]
    idx = int(np.argmax(scores))
    return idx, float(scores[idx])


def fourier_params(shape, k_max=8):
    """Return translation-invariant harmonic amplitude and phase ratios."""
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


def template_features(shape):
    y = minmax(shape)
    peak = int(np.argmax(y))
    trough = int(np.argmin(y))
    dy = np.diff(y)
    return {
        "peak_phase": float(peak / max(1, len(y) - 1)),
        "trough_phase": float(trough / max(1, len(y) - 1)),
        "rise_energy": float(np.sum(np.clip(dy, 0.0, None))),
        "release_energy": float(np.sum(np.clip(-dy, 0.0, None))),
        "skew": float(np.mean(zscore(y) ** 3)),
        "harmonic_2_over_1": float(abs(np.fft.fft(y - y.mean())[2]) / (abs(np.fft.fft(y - y.mean())[1]) + EPS)),
        "harmonic_3_over_1": float(abs(np.fft.fft(y - y.mean())[3]) / (abs(np.fft.fft(y - y.mean())[1]) + EPS)),
    }


def moving_average(x, window):
    x = np.asarray(x, dtype=float)
    if window <= 1:
        return x.copy()
    kernel = np.ones(window, dtype=float) / float(window)
    pad = window // 2
    padded = np.pad(x, (pad, pad), mode="edge")
    return np.convolve(padded, kernel, mode="valid")[: len(x)]


def detect_silso_ns_columns(rows):
    arr = np.asarray(rows, dtype=float)
    best = None
    for ni in range(2, arr.shape[1]):
        for si in range(2, arr.shape[1]):
            if ni == si:
                continue
            n = arr[:, ni]
            s = arr[:, si]
            valid = np.isfinite(n) & np.isfinite(s) & (n >= 0.0) & (s >= 0.0)
            if int(np.sum(valid)) < 240:
                continue
            both = np.r_[n[valid], s[valid]]
            if float(np.nanmedian(both)) < 1.0 or float(np.nanstd(both)) < 1.0:
                continue
            balance = np.nanmedian(np.minimum(n[valid], s[valid]) / (np.maximum(n[valid], s[valid]) + EPS))
            score = float(np.nanstd(both)) + 20.0 * float(balance)
            if best is None or score > best[0]:
                best = (score, ni, si)
    if best is None:
        raise RuntimeError("Could not detect north/south columns in Catalogue_B")
    return best[1], best[2]


def load_solar_total():
    total_candidates = [
        CACHE / "SN_m_tot_V2.0.csv",
        Path(r"F:\SystemFormulaFolder\SILSO_Solar\SN_m_tot_V2.0.csv"),
        Path(r"F:\SystemFormulaFolder\solar_test\sunspots.txt"),
    ]
    for path in total_candidates:
        if not path.exists():
            continue
        dates = []
        values = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = re.split(r"[;\s]+", line)
            if len(parts) < 4:
                continue
            try:
                year = int(parts[0])
                month = int(parts[1])
                ssn = float(parts[3])
            except ValueError:
                continue
            if ssn >= 0.0 and 1 <= month <= 12:
                dates.append(f"{year:04d}-{month:02d}")
                values.append(ssn)
        if len(values) >= 1200:
            return dates, np.asarray(values, dtype=float), {
                "path": str(path),
                "source": "SILSO monthly total sunspot number",
                "n_months": int(len(values)),
                "date_start": dates[0],
                "date_end": dates[-1],
            }

    path = CACHE / "Catalogue_B.txt"
    if not path.exists():
        raise FileNotFoundError(path)
    rows = []
    dates = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if re.match(r"^\d{4}[-/]\d{2}", line):
            year = int(line[0:4])
            month = int(line[5:7])
            tail = line[7:]
            nums = [year, month]
            for chunk in re.split(r"\s+", tail.strip()):
                try:
                    nums.append(float(chunk))
                except ValueError:
                    pass
            if len(nums) >= 6:
                rows.append(nums)
                dates.append(f"{year:04d}-{month:02d}")
    width = min(len(r) for r in rows)
    rows = [r[:width] for r in rows]
    ni, si = detect_silso_ns_columns(rows)
    arr = np.asarray(rows, dtype=float)
    north = arr[:, ni]
    south = arr[:, si]
    good = np.isfinite(north) & np.isfinite(south) & (north >= 0.0) & (south >= 0.0)
    total = north[good] + south[good]
    return [d for d, ok in zip(dates, good) if ok], total, {"path": str(path), "north_col": ni, "south_col": si}


def solar_cycle_templates():
    dates, total, meta = load_solar_total()
    smoothed = moving_average(total, 13)
    peaks, _ = find_peaks(smoothed, distance=84, prominence=max(8.0, float(np.std(smoothed)) * 0.22))
    troughs, _ = find_peaks(-smoothed, distance=72, prominence=max(4.0, float(np.std(smoothed)) * 0.10))
    cycles = []
    descriptors = []
    seen = set()
    for p in peaks:
        prevs = troughs[troughs < p]
        nexts = troughs[troughs > p]
        if len(prevs) == 0 or len(nexts) == 0:
            continue
        start = int(prevs[-1])
        end = int(nexts[0])
        if (start, end) in seen:
            continue
        seen.add((start, end))
        if end - start < 72 or end - start > 190:
            continue
        seg = smoothed[start : end + 1]
        if np.nanmax(seg) - np.nanmin(seg) < 10.0:
            continue
        cycles.append(resample_segment(seg))
        descriptors.append(
            {
                "start": dates[start],
                "peak": dates[int(p)],
                "end": dates[end],
                "months": int(end - start),
                "rise_fraction": float((p - start) / max(1, end - start)),
                "ara_release_over_accumulate": float((end - p) / max(1, p - start)),
            }
        )
    meta.update({"n_months": int(len(total)), "date_start": dates[0], "date_end": dates[-1]})
    return cycles, descriptors, meta


def load_bidmc_ecg():
    path = CACHE / "bidmc_01_Signals.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    times = []
    ecg = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        ii_col = "II" if "II" in fields else fields[-1]
        time_col = next((c for c in fields if "time" in c.lower()), fields[0])
        for row in reader:
            try:
                times.append(float(row[time_col]))
                ecg.append(float(row[ii_col]))
            except (TypeError, ValueError):
                continue
    t = np.asarray(times, dtype=float)
    y = np.asarray(ecg, dtype=float)
    good = np.isfinite(t) & np.isfinite(y)
    t = t[good]
    y = y[good]
    fs = 1.0 / float(np.median(np.diff(t)))
    return t, y, fs, {"path": str(path), "samples": int(len(y)), "fs": fs}


def choose_r_peaks(filtered, fs):
    distance = max(1, int(0.30 * fs))
    prominence = max(float(np.std(filtered)) * 0.45, EPS)
    pos, _ = find_peaks(filtered, distance=distance, prominence=prominence)
    neg, _ = find_peaks(-filtered, distance=distance, prominence=prominence)

    def score(peaks):
        if len(peaks) < 10:
            return -1e9
        rr = np.diff(peaks) / fs
        physiologic = (rr > 0.30) & (rr < 2.00)
        return float(np.mean(physiologic)) * len(peaks)

    return pos if score(pos) >= score(neg) else neg


def ecg_templates():
    t, ecg, fs, meta = load_bidmc_ecg()
    nyq = fs / 2.0
    sos = butter(2, [5.0 / nyq, 20.0 / nyq], btype="bandpass", output="sos")
    filtered = sosfiltfilt(sos, ecg)
    rpeaks = choose_r_peaks(filtered, fs)

    raw_beats = []
    half = int(0.40 * fs)
    for r in rpeaks:
        a = int(r) - half
        b = int(r) + half
        if a >= 0 and b <= len(ecg):
            raw_beats.append(resample_segment(ecg[a:b]))

    rr = np.diff(rpeaks) / fs
    rr_s = gaussian_filter1d(rr, sigma=2.0)
    rr_prom = max(float(np.std(rr_s)) * 0.28, EPS)
    rr_peaks, _ = find_peaks(rr_s, distance=4, prominence=rr_prom)
    rr_troughs, _ = find_peaks(-rr_s, distance=4, prominence=max(rr_prom * 0.75, EPS))

    rr_cycles = []
    rr_desc = []
    seen = set()
    for p in rr_peaks:
        prevs = rr_troughs[rr_troughs < p]
        nexts = rr_troughs[rr_troughs > p]
        if len(prevs) == 0 or len(nexts) == 0:
            continue
        start = int(prevs[-1])
        end = int(nexts[0])
        if (start, end) in seen:
            continue
        seen.add((start, end))
        if end - start < 4 or end - start > 80:
            continue
        seg = rr_s[start : end + 1]
        if np.nanmax(seg) - np.nanmin(seg) < 0.005:
            continue
        rr_cycles.append(resample_segment(seg))
        rr_desc.append(
            {
                "start_s": float(t[int(rpeaks[start])]),
                "peak_s": float(t[int(rpeaks[p])]),
                "end_s": float(t[int(rpeaks[end])]),
                "beats": int(end - start),
                "rise_fraction": float((p - start) / max(1, end - start)),
                "ara_release_over_accumulate": float((end - p) / max(1, p - start)),
            }
        )

    meta.update(
        {
            "r_peaks": int(len(rpeaks)),
            "rr_intervals": int(len(rr)),
            "rr_mean_s": float(np.mean(rr)),
            "rr_std_s": float(np.std(rr)),
            "raw_beats": int(len(raw_beats)),
            "rr_cycles": int(len(rr_cycles)),
        }
    )
    return raw_beats, rr_cycles, rr_desc, meta


def null_shapes():
    n = N_PHASE
    x = np.linspace(0.0, 1.0, n, endpoint=False)
    phase = 2.0 * math.pi * x
    shapes = {
        "pure sine": np.sin(phase),
        "triangle symmetric": 1.0 - np.abs(2.0 * x - 1.0),
        "sawtooth fast-rise slow-fall": np.where(x < 0.32, x / 0.32, (1.0 - x) / 0.68),
        "sawtooth slow-rise fast-fall": np.where(x < 0.68, x / 0.68, (1.0 - x) / 0.32),
        "gaussian peak": np.exp(-0.5 * ((x - 0.5) / 0.10) ** 2),
        "sharp spike slow tail": np.exp(-0.5 * ((x - 0.42) / 0.04) ** 2) + 0.30 * np.exp(-0.5 * ((x - 0.62) / 0.18) ** 2),
        "double peak rough": np.exp(-0.5 * ((x - 0.44) / 0.04) ** 2) - 0.25 * np.exp(-0.5 * ((x - 0.50) / 0.04) ** 2) + 0.20 * np.exp(-0.5 * ((x - 0.64) / 0.12) ** 2),
        "phi rise": np.where(x < 1.0 / PHI, (x / (1.0 / PHI)) ** PHI, ((1.0 - x) / (1.0 - 1.0 / PHI)) ** (1.0 / PHI)),
    }
    return {name: minmax(shape) for name, shape in shapes.items()}


def random_piecewise_null_distances(target, n=1000, seed=7):
    rng = np.random.default_rng(seed)
    x = np.linspace(0.0, 1.0, N_PHASE, endpoint=False)
    out = []
    for _ in range(n):
        rise = float(rng.uniform(0.12, 0.82))
        a = float(rng.uniform(0.35, 3.0))
        b = float(rng.uniform(0.35, 3.0))
        y = np.where(x < rise, (x / rise) ** a, ((1.0 - x) / (1.0 - rise)) ** b)
        if rng.random() < 0.35:
            y += float(rng.uniform(0.05, 0.40)) * np.sin(4.0 * math.pi * x + float(rng.uniform(0, 2 * math.pi)))
        out.append(fourier_distance(target, minmax(y)))
    return np.asarray(out, dtype=float)


def compare_pair(label, a_train, a_test, b_train, b_test):
    shift, train_shift_corr = best_circular_shift(a_train, b_train)
    direct_train = corr(a_train, b_train)
    direct_test = corr(a_test, b_test)
    shifted_test = corr(a_test, np.roll(b_test, shift))
    cross_a_test_b_train = corr(a_test, np.roll(b_train, shift))
    cross_b_test_a_train = corr(a_train, np.roll(b_test, -shift))
    dist_train = fourier_distance(a_train, b_train)
    dist_test = fourier_distance(a_test, b_test)

    nulls = null_shapes()
    null_rank_train = sorted(
        [{"name": name, "distance": fourier_distance(a_train, shape)} for name, shape in nulls.items()] +
        [{"name": label, "distance": dist_train}],
        key=lambda x: x["distance"],
    )
    rank_train = 1 + next(i for i, item in enumerate(null_rank_train) if item["name"] == label)

    random_dist = random_piecewise_null_distances(a_train)
    percentile = float(np.mean(random_dist <= dist_train) * 100.0)
    specificity = 100.0 - percentile
    if shifted_test >= 0.75 and rank_train <= 3 and specificity >= 75.0:
        verdict = "strong_specific_geometry_match"
    elif shifted_test >= 0.75:
        verdict = "high_time_scaled_correlation_but_not_specific_against_one_peak_nulls"
    elif shifted_test >= 0.35:
        verdict = "moderate_time_scaled_correlation"
    else:
        verdict = "weak_or_no_time_scaled_match"

    return {
        "label": label,
        "verdict": verdict,
        "phase_shift_from_train": int(shift),
        "train_corr_direct": float(direct_train),
        "train_corr_shifted": float(train_shift_corr),
        "test_corr_direct": float(direct_test),
        "test_corr_with_train_shift": float(shifted_test),
        "ecg_test_vs_solar_train_corr_with_train_shift": float(cross_a_test_b_train),
        "solar_test_vs_ecg_train_corr_with_train_shift": float(cross_b_test_a_train),
        "fourier_distance_train": float(dist_train),
        "fourier_distance_test": float(dist_test),
        "null_rank_train": int(rank_train),
        "null_count_train": int(len(null_rank_train)),
        "null_results_train": null_rank_train,
        "random_piecewise_null_closer_or_equal_percentile": percentile,
        "random_piecewise_specificity_percentile": specificity,
        "features_a_train": template_features(a_train),
        "features_b_train": template_features(b_train),
    }


def main():
    print("Loading Solar cycle geometry...")
    solar_cycles, solar_desc, solar_meta = solar_cycle_templates()
    print(f"  Solar cycles: {len(solar_cycles)} ({solar_meta['date_start']} to {solar_meta['date_end']})")

    print("Loading ECG temporal geometry...")
    raw_beats, rr_cycles, rr_desc, ecg_meta = ecg_templates()
    print(f"  ECG R peaks: {ecg_meta['r_peaks']}; R-R cycles: {len(rr_cycles)}; raw beats: {len(raw_beats)}")

    if len(solar_cycles) < 4:
        raise RuntimeError("Not enough solar cycles for train/test")
    if len(rr_cycles) < 8:
        raise RuntimeError("Not enough ECG R-R cycles for train/test")
    if len(raw_beats) < 20:
        raise RuntimeError("Not enough ECG raw beats for train/test")

    solar_train, solar_test = split_cycles(solar_cycles)
    rr_train, rr_test = split_cycles(rr_cycles)
    raw_train, raw_test = split_cycles(raw_beats)

    solar_train_t = mean_template(solar_train)
    solar_test_t = mean_template(solar_test)
    rr_train_t = mean_template(rr_train)
    rr_test_t = mean_template(rr_test)
    raw_train_t = mean_template(raw_train)
    raw_test_t = mean_template(raw_test)

    primary = compare_pair(
        "ECG R-R temporal cycles vs Solar cycles",
        rr_train_t,
        rr_test_t,
        solar_train_t,
        solar_test_t,
    )
    secondary = compare_pair(
        "Raw ECG beat waveform vs Solar cycles",
        raw_train_t,
        raw_test_t,
        solar_train_t,
        solar_test_t,
    )

    payload = {
        "date": "2026-05-23",
        "leakage_guard": [
            "Cached public data only.",
            "Chronological split before scoring held-out templates.",
            "Circular shift learned on training templates only.",
            "Fourier distance is phase-shift invariant.",
            "Null shapes are fixed a priori; random null uses fixed seed.",
        ],
        "solar": {
            "meta": solar_meta,
            "n_cycles": len(solar_cycles),
            "n_train": len(solar_train),
            "n_test": len(solar_test),
            "cycle_descriptors": solar_desc,
            "train_template": [float(x) for x in solar_train_t],
            "test_template": [float(x) for x in solar_test_t],
        },
        "ecg": {
            "meta": ecg_meta,
            "n_rr_cycles": len(rr_cycles),
            "n_rr_train": len(rr_train),
            "n_rr_test": len(rr_test),
            "rr_cycle_descriptors": rr_desc,
            "rr_train_template": [float(x) for x in rr_train_t],
            "rr_test_template": [float(x) for x in rr_test_t],
            "n_raw_beats": len(raw_beats),
            "n_raw_train": len(raw_train),
            "n_raw_test": len(raw_test),
            "raw_train_template": [float(x) for x in raw_train_t],
            "raw_test_template": [float(x) for x in raw_test_t],
        },
        "primary_rr_vs_solar": primary,
        "secondary_raw_ecg_vs_solar": secondary,
        "phi": PHI,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_JS.write_text("window.ECG_SOLAR_GEOMETRY = " + json.dumps(payload) + ";\n", encoding="utf-8")

    print("\n=== PRIMARY: ECG R-R temporal cycles vs Solar cycles ===")
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
        print(f"  {key}: {primary[key]}")

    print("\n=== SECONDARY: Raw ECG beat waveform vs Solar cycles ===")
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
        print(f"  {key}: {secondary[key]}")

    print(f"\nSaved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    main()

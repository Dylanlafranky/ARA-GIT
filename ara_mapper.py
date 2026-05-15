#!/usr/bin/env python3
"""
ara_mapper.py — analyse any time series under the ARA framework.

Usage:
    python ara_mapper.py path/to/data.csv [--col VALUE_COL] [--time-col TIME_COL]
                                          [--sample-rate FS] [--out output.json]

Input: a CSV with at least one numeric column of evenly-spaced (or
       reasonably-evenly-spaced) time-series values.

Output: JSON containing:
    - system_mean_ara: overall ARA value
    - system_class: framework classification (singularity / consumer / absorber /
                    clock / engine / exothermic / harmonic)
    - dominant_period_samples: detected fundamental cycle length
    - home_k: φ-rung index at which the dominant period sits
    - per_rung_breakdown: list of (k, period, amp, ara, classification) for each rung
    - matched_partners: pairs of rungs that are anti-phase coupled

Author: Dylan La Franchi (with help from Claude). Public release, May 2026.
"""
import os, sys, json, math, argparse
import numpy as np
from scipy.signal import butter, sosfilt, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = (1 + 5**0.5) / 2


# ---------- ARA scale and classification ----------
ARA_CLASSES = [
    (0.20, 'snap',         'Violent release; lightning, earthquake, wildfire class'),
    (0.50, 'consumer',     'Energy-spent system; below sustainable engine zone'),
    (0.90, 'absorber',     'Near-balance shock absorber; close to singularity at 1.0'),
    (1.20, 'clock',        'Forced symmetry / pacemaker; brain oscillation class'),
    (1.50, 'shock_absorber', 'Overdamped clearing; glucose, managed gait'),
    (1.70, 'engine',       'Sustained self-organising; near φ ≈ 1.618'),
    (1.85, 'exothermic',   'Energy-source; above φ, near solar-cycle class'),
    (3.0,  'harmonic_or_pair', 'Pure harmonic (2.0) or coupled-pair signature (φ²≈2.6)'),
    (1e9,  'extreme',      'Past framework scale — degenerate or forced state'),
]


def classify_ara(ara):
    """Return (class_name, description) based on ARA value."""
    if ara is None or not math.isfinite(ara):
        return ('undefined', 'No measurable ARA — signal too short or flat')
    for upper, name, desc in ARA_CLASSES:
        if ara < upper:
            return (name, desc)
    return ('extreme', 'Past framework scale')


# ---------- Strict-causal bandpass ----------
def causal_bandpass(arr, period, bandwidth=0.4, order=2):
    """Causal IIR Butterworth bandpass at given period (in samples)."""
    arr = np.asarray(arr, dtype=float)
    n = len(arr)
    f_c = 1.0 / period
    nyq = 0.5
    Wn_lo = max(1e-6, (1 - bandwidth) * f_c / nyq)
    Wn_hi = min(0.999, (1 + bandwidth) * f_c / nyq)
    if Wn_lo >= Wn_hi:
        return np.zeros(n)
    sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
    return sosfilt(sos, arr - np.mean(arr))


# ---------- ARA measurement ----------
# DEFAULT METHOD: bandpass-based ARA (SOS Butterworth, 85% bandwidth).
# This generalises across signal types — smooth oscillators, noisy data,
# multi-feature waveforms — with reasonable behaviour across the board.
#
# LIMITATIONS to flag honestly:
#   - On sharp asymmetric cycles (solar 11-year, lightning, snap-class events),
#     the bandpass smooths the asymmetry into near-sinusoidal cycles and
#     under-counts the actual cycle asymmetry. Solar's 7yr-rise/4yr-fall
#     (true ARA ~1.75) reads as ~0.9 under this default — the FRAMEWORK CLASS
#     reading is wrong (clock vs the actual exothermic engine).
#
#   - For SINGLE-FEATURE asymmetric cycles, `measure_rung_ara_raw_peak()`
#     below recovers the asymmetry directly (no bandpass smoothing).
#     Works well for solar, watershed hydrographs, single-mode oscillators.
#     Breaks on multi-feature waveforms (ECG PQRST, multi-peak chemical
#     oscillators) — those have multiple peaks/troughs per cycle and raw-peak
#     finds them all, giving chaotic ARAs.
#
#   - For PHASE-FOLDED averaged-cycle ARA (the original Cepheid method),
#     see `cepheid_coupled_pair_test.py` — assumes single-feature cycle shape.
#
# Decision tree for choosing method:
#   - Multi-feature waveform (ECG, EEG bursts, BZ chemical) → use default bandpass
#   - Single asymmetric cycle (solar, hydrograph, breath) → consider raw-peak
#   - Want averaged cycle profile (Cepheid-style)        → use phase-fold separately
#
# See Rule 7 in ARA_decomposition_rules.md for the broader measurement-
# conditioning caveat.
def measure_rung_ara(arr, period, bw=0.85):
    """ARA at one rung — DEFAULT method: bandpass + peak detection.

    Bandpasses the signal at this rung's period (SOS Butterworth, 85% bandwidth),
    then measures where the cycle's minimum sits relative to peak-to-peak length.
    Generalises across smooth/noisy/multi-feature signals.

    For sharp asymmetric cycles where this method's smoothing matters, use
    `measure_rung_ara_raw_peak()` below.
    """
    n = len(arr)
    if n < 3 * int(period):
        return None
    f_c = 1.0/period; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return None
    sos = butter(2, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
    bp = sosfilt(sos, arr - np.mean(arr))
    smoothed = gaussian_filter1d(bp, max(1, int(period * 0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.7)))
    if len(peaks) < 2:
        return None
    aras = []
    for i in range(len(peaks) - 1):
        seg = smoothed[peaks[i]:peaks[i+1]+1]
        if len(seg) < 3:
            continue
        f_t = max(0.15, min(0.85, int(np.argmin(seg)) / max(1, len(seg)-1)))
        aras.append((1 - f_t) / f_t)
    if not aras:
        return None
    return float(np.mean(np.clip(aras, 0.3, 3.0)))


def measure_rung_ara_raw_peak(arr, period, smooth_factor=0.05, min_dist_factor=0.85):
    """ALTERNATIVE method: raw-peak ARA (no bandpass).

    Detects peaks and troughs on the lightly-smoothed RAW signal, measures
    rise/fall per actual cycle.

    Use when: the cycle is asymmetric and bandpass-smoothing would obscure the
    asymmetry (solar 11-year cycle, watershed hydrographs, single-mode oscillators).

    Do NOT use when: the cycle has multiple peaks/troughs per period (ECG PQRST,
    multi-mode chemical oscillators) — raw-peak finds sub-peaks and gives chaotic
    ratios.
    """
    arr = np.asarray(arr, dtype=float)
    n = len(arr)
    if n < 3 * int(period):
        return None
    smooth_sigma = max(1, int(period * smooth_factor))
    smoothed = gaussian_filter1d(arr, smooth_sigma) if smooth_sigma > 1 else arr
    min_dist = max(2, int(period * min_dist_factor))
    peaks, _ = find_peaks(smoothed, distance=min_dist)
    troughs, _ = find_peaks(-smoothed, distance=min_dist)
    if len(peaks) < 2 or len(troughs) < 2:
        return None
    extrema = sorted([(p, 'peak') for p in peaks] + [(t, 'trough') for t in troughs])
    aras = []
    i = 0
    while i < len(extrema) - 2:
        i1, t1 = extrema[i]; i2, t2 = extrema[i+1]; i3, t3 = extrema[i+2]
        if t1 == 'peak' and t2 == 'trough' and t3 == 'peak':
            t_fall = i2 - i1; t_rise = i3 - i2
            if t_rise > 0 and t_fall > 0:
                ara = t_fall / t_rise
                if 0.1 < ara < 10:
                    aras.append(ara)
            i += 2
        else:
            i += 1
    if not aras:
        return None
    return float(np.mean(np.clip(aras, 0.1, 5.0)))


def measure_rung_amplitude(arr, period):
    """Peak-to-peak amplitude of bandpass at this rung, taking the recent cycle."""
    bp = causal_bandpass(arr, period)
    p_int = max(2, int(period))
    if len(bp) < 2 * p_int + 5:
        return None
    last_cycle = bp[-p_int:]
    return float((np.max(last_cycle) - np.min(last_cycle)) / 2.0)


# ---------- Dominant period detection ----------
def detect_dominant_period(arr, min_period=3, max_period=None):
    """Use FFT to find dominant cycle period in samples."""
    n = len(arr)
    if max_period is None:
        max_period = n / 4
    arr_z = (arr - np.mean(arr)) / max(1e-9, np.std(arr))
    F = np.fft.rfft(arr_z * np.hanning(n))
    freqs = np.fft.rfftfreq(n)
    # Skip DC and very low freq
    valid = (freqs > 1/max_period) & (freqs < 1/min_period)
    if not np.any(valid):
        return None
    f_idx = np.argmax(np.abs(F[valid]))
    valid_freqs = freqs[valid]
    f_dom = valid_freqs[f_idx]
    return float(1.0 / f_dom)


# ---------- Build full rung breakdown ----------
def map_system(data, sample_rate=1.0, time_unit='samples',
               rungs_below=4, rungs_above=8):
    """Full ARA mapping of a time series. Returns dict suitable for JSON."""
    arr = np.asarray(data, dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) < 50:
        return dict(error='Signal too short — need at least 50 samples')

    # 1. Find dominant period
    dom_period = detect_dominant_period(arr)
    if dom_period is None:
        return dict(error='No dominant cycle detected — signal may be aperiodic')

    # 2. Map dominant period onto a φ-rung index
    home_k = int(round(math.log(dom_period) / math.log(PHI)))

    # 3. Build rung ladder around home_k
    rung_ks = list(range(home_k - rungs_below, home_k + rungs_above + 1))
    rung_breakdown = []
    rung_aras = []
    for k in rung_ks:
        period = PHI ** k
        if period < 2 or 4 * period > len(arr):
            rung_breakdown.append(dict(k=k, period_samples=float(period),
                                        period_time=float(period/sample_rate),
                                        amp=None, ara=None, classification=None,
                                        valid=False))
            continue
        amp = measure_rung_amplitude(arr, period)
        ara = measure_rung_ara(arr, period)
        cls_name, cls_desc = classify_ara(ara)
        if ara is not None:
            rung_aras.append((k, ara))
        rung_breakdown.append(dict(
            k=int(k), period_samples=float(period),
            period_time=float(period/sample_rate),
            amp=amp, ara=ara,
            classification=cls_name, classification_note=cls_desc,
            valid=True,
        ))

    # 4. System mean ARA: take the rung with the highest amplitude (most dominant)
    valid_rungs = [r for r in rung_breakdown if r['valid'] and r['amp'] is not None]
    if valid_rungs:
        dominant_rung = max(valid_rungs, key=lambda r: r['amp'])
        system_ara = dominant_rung['ara']
    else:
        system_ara = None
    system_class, system_desc = classify_ara(system_ara)

    # 5. Detect matched-rung partners (anti-phase at home rung level)
    # For now: report rungs with similar ARA values (within 0.15) — candidate partners.
    partners = []
    if len(rung_aras) >= 2:
        for i in range(len(rung_aras)):
            for j in range(i+1, len(rung_aras)):
                k1, a1 = rung_aras[i]; k2, a2 = rung_aras[j]
                if abs(a1 - a2) < 0.15 and abs(k1 - k2) >= 3:
                    partners.append(dict(rung_a=int(k1), rung_b=int(k2),
                                          ara_a=a1, ara_b=a2,
                                          gap_rungs=int(abs(k1-k2)),
                                          gap_time=float(PHI**abs(k1-k2))))

    # 6. ARA-of-ARA (engine-of-engines): mean ARA across all valid rungs
    if rung_aras:
        all_aras = [a for _, a in rung_aras]
        ara_of_ara = float(np.mean(all_aras))
        ara_of_ara_class, _ = classify_ara(ara_of_ara)
    else:
        ara_of_ara = None
        ara_of_ara_class = 'undefined'

    return dict(
        framework_version='1.0',
        n_samples=int(len(arr)),
        sample_rate=float(sample_rate),
        time_unit=time_unit,
        signal_stats=dict(
            mean=float(np.mean(arr)),
            std=float(np.std(arr)),
            min=float(np.min(arr)),
            max=float(np.max(arr)),
        ),
        dominant_period_samples=float(dom_period),
        dominant_period_time=float(dom_period/sample_rate),
        home_k=int(home_k),
        system_mean_ara=system_ara,
        system_class=system_class,
        system_classification_note=system_desc,
        ara_of_ara=ara_of_ara,
        ara_of_ara_class=ara_of_ara_class,
        ara_of_ara_note='Mean ARA across all detected rungs — the system\'s class at the next fractal level',
        rung_breakdown=rung_breakdown,
        matched_partner_candidates=partners,
        phi=PHI,
    )


# ---------- CLI ----------
def main():
    ap = argparse.ArgumentParser(description='ARA framework system mapper')
    ap.add_argument('csv', help='Path to CSV file with time-series data')
    ap.add_argument('--col', default=None, help='Column name or index to analyse')
    ap.add_argument('--time-col', default=None, help='Optional time column name')
    ap.add_argument('--sample-rate', type=float, default=1.0,
                    help='Samples per time unit (default 1.0)')
    ap.add_argument('--time-unit', default='samples', help='Time unit label')
    ap.add_argument('--out', default=None, help='Output JSON path (default: <csv>_ara.json)')
    args = ap.parse_args()

    import pandas as pd
    df = pd.read_csv(args.csv)
    # Pick column
    if args.col is None:
        col = df.select_dtypes(include='number').columns[0]
        print(f"  Auto-selected column: {col}")
    elif args.col.isdigit():
        col = df.columns[int(args.col)]
    else:
        col = args.col
    data = df[col].dropna().values

    print(f"Loaded {len(data)} samples from {args.csv} (column: {col})")
    print(f"Running ARA mapping...")
    result = map_system(data, sample_rate=args.sample_rate, time_unit=args.time_unit)
    result['source_file'] = args.csv
    result['source_column'] = col

    # Pretty-print summary
    print()
    print('=' * 70)
    print(f"ARA Framework Mapping — {args.csv}")
    print('=' * 70)
    if 'error' in result:
        print(f"  ERROR: {result['error']}")
        return
    print(f"  Samples: {result['n_samples']}")
    print(f"  Dominant period: {result['dominant_period_samples']:.2f} samples "
          f"({result['dominant_period_time']:.4f} {result['time_unit']})")
    print(f"  Home rung: k = {result['home_k']}")
    print(f"  System mean ARA: {result['system_mean_ara']:.3f}" if result['system_mean_ara'] else "  System mean ARA: undefined")
    print(f"  System classification: {result['system_class']}")
    print(f"    — {result['system_classification_note']}")
    print(f"  ARA-of-ARA: {result['ara_of_ara']:.3f}" if result['ara_of_ara'] else "  ARA-of-ARA: undefined")
    print(f"    — Next-level class: {result['ara_of_ara_class']}")
    print()
    print(f"  φ-rung breakdown (valid rungs only):")
    print(f"  {'k':>4}  {'period':>12}  {'amp':>8}  {'ARA':>7}  {'class':<20}")
    for r in result['rung_breakdown']:
        if not r['valid']: continue
        amp_s = f"{r['amp']:.3f}" if r['amp'] is not None else 'n/a'
        ara_s = f"{r['ara']:.3f}" if r['ara'] is not None else 'n/a'
        marker = ' ← home' if r['k'] == result['home_k'] else ''
        print(f"  {r['k']:>4}  {r['period_time']:>12.4f}  {amp_s:>8}  {ara_s:>7}  "
              f"{r['classification'] or 'n/a':<20}{marker}")

    if result['matched_partner_candidates']:
        print(f"\n  Candidate matched-rung partners (similar ARA, ≥3 rungs apart):")
        for p in result['matched_partner_candidates']:
            print(f"    Rung {p['rung_a']} (ARA {p['ara_a']:.3f}) ↔ Rung {p['rung_b']} (ARA {p['ara_b']:.3f}), "
                  f"{p['gap_rungs']} rungs apart")

    # Save
    out_path = args.out or os.path.splitext(args.csv)[0] + '_ara.json'
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\n  Saved -> {out_path}")


if __name__ == '__main__':
    main()

"""
Cross-subject ECG reproducibility test (Dylan 2026-05-03):

The framework's structural claims have only been tested on PhysioNet nsr001.
Test on all 54 NSR subjects to see if the same φ-rung structure, ARA values,
and cycle shape patterns reproduce across healthy hearts.

If features hold across most subjects → reproducible foundational result.
If only nsr001 shows the features → framework is overfitting to one example.

DATA: real PhysioNet Normal Sinus Rhythm RR Interval Database (54 subjects).
"""
import json, os
import numpy as np, pandas as pd
import wfdb
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

DB_PATH = _resolve(r"F:\SystemFormulaFolder\normal-sinus-rhythm-rr-interval-database-1.0.0")
OUT     = _resolve(r"F:\SystemFormulaFolder\TheFormula\cross_subject_data.js")

# Load subject list
with open(os.path.join(DB_PATH, 'RECORDS')) as f:
    records = [r.strip() for r in f if r.strip()]
print(f"Subjects: {len(records)}")

GRID_DT = 0.5
N_PTS = 100
ECG_PERIOD_S = PHI**5  # Mayer-wave rung ~11s

def load_rr(subject):
    """Read PhysioNet ecg file (RR interval data) using wfdb. Returns (time_s, rr_ms)."""
    try:
        record_path = os.path.join(DB_PATH, subject)
        # The .ecg files in this DB are actually annotation-format RR intervals
        # Try loading as annotation
        ann = wfdb.rdann(record_path, 'ecg')
        # Sample numbers / sample frequency = time in seconds
        # For NSRDB the sampling frequency is 128 Hz (standard MIT-BIH)
        fs = 128.0
        times_s = ann.sample / fs
        if len(times_s) < 100: return None, None
        # RR intervals in ms = diff of times in s × 1000
        rr_ms = np.diff(times_s) * 1000.0
        return times_s[1:], rr_ms
    except Exception as e:
        print(f"  ERR loading {subject}: {e}")
        return None, None

def process_subject(subject):
    """Returns dict of features for one subject, or None on failure."""
    t, rr = load_rr(subject)
    if t is None or len(rr) < 200: return None

    # Resample to uniform grid
    t_grid = np.arange(t[0], t[-1], GRID_DT)
    if len(t_grid) < 100: return None
    rr_uniform = np.interp(t_grid, t, rr)

    duration_h = (t[-1] - t[0]) / 3600.0

    # Bandpass at φ⁵ for cycle extraction (use light smoothing version)
    smooth_sigma = max(1, int(ECG_PERIOD_S * 0.15 / GRID_DT))
    smoothed = gaussian_filter1d(rr_uniform - np.mean(rr_uniform), smooth_sigma)
    min_dist = int(ECG_PERIOD_S * 0.7 / GRID_DT)
    peaks, _ = find_peaks(smoothed, distance=min_dist)
    if len(peaks) < 20: return None

    # Extract RAW cycles between peaks
    cycles = []
    target_n = int(ECG_PERIOD_S / GRID_DT)
    for i in range(len(peaks)-1):
        seg = rr_uniform[peaks[i]:peaks[i+1]]
        if len(seg) < target_n*0.5 or len(seg) > target_n*2.5: continue
        cycles.append(seg)
    if len(cycles) < 30: return None

    # Normalize each cycle
    def normalize_cycle(seg):
        x_o = np.linspace(0, 1, len(seg))
        x_n = np.linspace(0, 1, N_PTS)
        s = np.interp(x_n, x_o, seg)
        s_n = s - s.min()
        if s_n.max() > 0: s_n /= s_n.max()
        return 2*s_n - 1

    cycles_norm = [normalize_cycle(c) for c in cycles]
    cycles_arr = np.array(cycles_norm)
    mean_cycle = cycles_arr.mean(axis=0)
    std_cycle = cycles_arr.std(axis=0)

    # Compute ARA: rise time / fall time of mean cycle
    peak_idx = int(np.argmax(mean_cycle))
    trough_idx = int(np.argmin(mean_cycle))
    if trough_idx > peak_idx:
        rise = trough_idx - peak_idx  # length from peak to trough is "fall"
        fall = N_PTS - trough_idx + peak_idx  # rest is recovery (rise back)
    else:
        rise = N_PTS - peak_idx + trough_idx
        fall = peak_idx - trough_idx
    ara_estimate = rise / max(fall, 1)

    # Spectral concentration at the dominant rung
    rr_centered = rr_uniform - np.mean(rr_uniform)
    F = np.fft.rfft(rr_centered)
    freqs = np.fft.rfftfreq(len(rr_uniform), d=GRID_DT)
    P = np.abs(F)**2

    # Power at φ-rungs from φ³ to φ⁹
    rung_powers = {}
    for k in range(3, 10):
        period = PHI**k
        if period > (t[-1]-t[0])/3: continue
        f_c = 1.0/period
        f_lo, f_hi = 0.8*f_c, 1.2*f_c
        idx_lo = int(f_lo * len(rr_uniform) * GRID_DT)
        idx_hi = min(len(P)-1, int(f_hi * len(rr_uniform) * GRID_DT))
        if idx_hi <= idx_lo: continue
        rung_powers[k] = float(np.sum(P[idx_lo:idx_hi])) / float(np.sum(P[1:]))

    if not rung_powers: return None
    dominant_rung = max(rung_powers, key=lambda k: rung_powers[k])

    # Mid-cycle bump detection: look for local max in the descending portion (between peak and trough)
    # If mean_cycle has a local max somewhere in [10%, 70%] that's not the global peak, that's the bump
    mid_segment = mean_cycle[10:70]
    bump_positions = []
    for i in range(2, len(mid_segment)-2):
        if mid_segment[i] > mid_segment[i-1] and mid_segment[i] > mid_segment[i+1]:
            bump_positions.append((i+10) / N_PTS)

    # Get age/sex from header
    header_path = os.path.join(DB_PATH, subject + '.hea')
    age = None; sex = None
    try:
        with open(header_path) as f:
            for line in f:
                if 'Age:' in line:
                    parts = line.split()
                    for j, p in enumerate(parts):
                        if p == 'Age:' and j+1 < len(parts): age = parts[j+1]
                        if p == 'Sex:' and j+1 < len(parts): sex = parts[j+1]
    except: pass

    return dict(
        subject=subject,
        age=age, sex=sex,
        duration_h=float(duration_h),
        n_cycles=int(len(cycles)),
        mean_cycle=mean_cycle.tolist(),
        std_cycle=std_cycle.tolist(),
        ara_estimate=float(ara_estimate),
        peak_position=float(peak_idx/N_PTS),
        trough_position=float(trough_idx/N_PTS),
        rung_powers={str(k): v for k,v in rung_powers.items()},
        dominant_rung=int(dominant_rung),
        dominant_rung_concentration=float(rung_powers[dominant_rung]),
        bump_positions=bump_positions,
    )

# Process all subjects
print(f"\nProcessing 54 subjects...")
results = []
for i, subj in enumerate(records):
    print(f"  [{i+1}/54] {subj}...", end=' ', flush=True)
    r = process_subject(subj)
    if r is None:
        print("SKIP")
        continue
    print(f"OK n_cycles={r['n_cycles']}, ARA={r['ara_estimate']:.2f}, dom_rung=φ^{r['dominant_rung']} ({r['dominant_rung_concentration']*100:.1f}%)")
    results.append(r)

print(f"\nSuccessfully processed: {len(results)} / 54 subjects")

# Aggregate analyses
print(f"\n========= AGGREGATE STATISTICS =========")
aras = [r['ara_estimate'] for r in results]
trough_positions = [r['trough_position'] for r in results]
durations = [r['duration_h'] for r in results]
n_cycles_per = [r['n_cycles'] for r in results]
dominant_rungs = [r['dominant_rung'] for r in results]
dom_concentrations = [r['dominant_rung_concentration'] for r in results]

print(f"Recording duration:     mean {np.mean(durations):.1f}h, range {min(durations):.1f}-{max(durations):.1f}h")
print(f"Cycles extracted/subj:  mean {np.mean(n_cycles_per):.0f}, range {min(n_cycles_per)}-{max(n_cycles_per)}")
print(f"ARA estimate per subj:  mean {np.mean(aras):.3f} ± {np.std(aras):.3f}, range {min(aras):.2f}-{max(aras):.2f}")
print(f"Trough position:        mean {np.mean(trough_positions):.3f} ± {np.std(trough_positions):.3f}")

# Dominant rung distribution
from collections import Counter
rung_dist = Counter(dominant_rungs)
print(f"Dominant rung distribution: {dict(sorted(rung_dist.items()))}")
print(f"Dominant rung concentration: mean {np.mean(dom_concentrations)*100:.1f}%, range {min(dom_concentrations)*100:.1f}%-{max(dom_concentrations)*100:.1f}%")

# Cross-subject mean cycle shape
mean_cycles_all = np.array([r['mean_cycle'] for r in results])
grand_mean = mean_cycles_all.mean(axis=0)
grand_std = mean_cycles_all.std(axis=0)

# Pairwise shape correlations between subjects
print(f"\n========= CROSS-SUBJECT SHAPE CORRELATION =========")
shape_corrs = []
for i in range(len(results)):
    for j in range(i+1, len(results)):
        a = mean_cycles_all[i]; b = mean_cycles_all[j]
        if np.std(a) > 1e-9 and np.std(b) > 1e-9:
            shape_corrs.append(float(np.corrcoef(a, b)[0,1]))
print(f"Pairwise shape correlations: mean={np.mean(shape_corrs):+.3f}, median={np.median(shape_corrs):+.3f}")
print(f"  range: {min(shape_corrs):+.3f} to {max(shape_corrs):+.3f}")
print(f"  fraction > +0.5: {sum(1 for c in shape_corrs if c > 0.5)/len(shape_corrs)*100:.1f}%")
print(f"  fraction > +0.8: {sum(1 for c in shape_corrs if c > 0.8)/len(shape_corrs)*100:.1f}%")

# Mid-cycle bump analysis
all_bumps = []
for r in results:
    all_bumps.extend(r['bump_positions'])
print(f"\n========= MID-CYCLE BUMP =========")
print(f"Total bumps detected across {len(results)} subjects: {len(all_bumps)}")
if all_bumps:
    print(f"  position: mean {np.mean(all_bumps):.3f}, median {np.median(all_bumps):.3f}, std {np.std(all_bumps):.3f}")
    # Compare to φ-fractions of interest
    phi_fractions = {
        '1/φ²': 1/PHI**2,    # 0.382
        '1/φ':  1/PHI,       # 0.618
        'φ/(1+φ)': PHI/(1+PHI),  # 0.618 same as 1/φ
        '0.5':  0.5,
        '2/3':  2/3,
        'φ³/(1+φ³)': PHI**3/(1+PHI**3),  # ~0.81
    }
    print(f"\n  Comparison to candidate φ-fractions:")
    for name, frac in phi_fractions.items():
        within_002 = sum(1 for b in all_bumps if abs(b - frac) < 0.05)
        print(f"    {name:>15} = {frac:.3f} : {within_002}/{len(all_bumps)} bumps within ±0.05 ({within_002/len(all_bumps)*100:.1f}%)")

# Save
out = dict(
    sources=dict(db="PhysioNet Normal Sinus Rhythm RR Interval Database",
                 path="https://physionet.org/content/nsrdb/1.0.0/"),
    n_subjects_processed=len(results),
    n_subjects_total=54,
    grid_dt=GRID_DT,
    rung_period_s=ECG_PERIOD_S,
    grand_mean_cycle=grand_mean.tolist(),
    grand_std_cycle=grand_std.tolist(),
    aggregate=dict(
        ara_mean=float(np.mean(aras)), ara_std=float(np.std(aras)),
        ara_range=[float(min(aras)), float(max(aras))],
        trough_mean=float(np.mean(trough_positions)),
        trough_std=float(np.std(trough_positions)),
        durations=durations,
        n_cycles_per_subject=n_cycles_per,
        dom_rung_distribution=dict(sorted(rung_dist.items())),
        dom_rung_concentration_mean=float(np.mean(dom_concentrations)),
        dom_rung_concentration_range=[float(min(dom_concentrations)), float(max(dom_concentrations))],
        shape_corr_pairs=dict(
            mean=float(np.mean(shape_corrs)), median=float(np.median(shape_corrs)),
            range=[float(min(shape_corrs)), float(max(shape_corrs))],
            frac_above_0_5=float(sum(1 for c in shape_corrs if c > 0.5)/len(shape_corrs)),
            frac_above_0_8=float(sum(1 for c in shape_corrs if c > 0.8)/len(shape_corrs)),
        ),
        bump_positions_all=all_bumps,
    ),
    subjects=results,
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.CROSS_SUBJECT = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

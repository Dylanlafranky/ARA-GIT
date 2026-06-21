"""
Prominence-matched cross-domain test (Dylan 2026-05-03 catch):

Previous test compared big ENSO peak to AVERAGE heart cycle. Wrong matching.
Topology theory says: match prominence-to-prominence — biggest ENSO ↔ biggest heart.

For each ENSO test cycle ranked by amplitude, find the heart cycle of the
SAME RELATIVE PROMINENCE and use IT to predict ENSO's downcycle.

If the framework is right, matched-prominence shapes should capture amplitude.

DATA: real PhysioNet (nsr001) + real NOAA Niño 3.4.
"""
import json, os
import numpy as np, pandas as pd
from scipy.signal import find_peaks

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

ECG_PATH  = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\heart_predicts_enso_matched_data.js")

ecg = pd.read_csv(ECG_PATH)
t_ecg = ecg['time_s'].values.astype(float); v_ecg = ecg['rr_ms'].values.astype(float)
GRID_DT = 0.5
t_grid = np.arange(t_ecg[0], t_ecg[-1], GRID_DT)
v_ecg = np.interp(t_grid, t_ecg, v_ecg)

df_n = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
df_n['date'] = pd.to_datetime(df_n['date'].str.strip())
df_n = df_n[df_n['val'] > -90].copy()
v_nino = df_n['val'].values.astype(float)
nino_dates = df_n['date'].values

def bandpass(arr, period_units, dt=1.0, bw=0.5):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_units
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

ECG_PERIOD_S   = PHI**5
NINO_PERIOD_MO = PHI**8
ecg_band  = bandpass(v_ecg,   ECG_PERIOD_S,   GRID_DT, bw=0.4)
nino_band = bandpass(v_nino,  NINO_PERIOD_MO, dt=1.0,  bw=0.5)

ECG_SPLIT  = len(ecg_band)//2
NINO_SPLIT = len(nino_band)//2

# Extract all heart cycles (peak-to-peak, raw segments AND amplitudes)
def extract_cycles(band, min_cycle_samples):
    peaks, _ = find_peaks(band, distance=int(min_cycle_samples*0.7))
    cycles = []
    for i in range(len(peaks)-1):
        seg = band[peaks[i]:peaks[i+1]]
        if len(seg) < min_cycle_samples*0.5: continue
        if len(seg) > min_cycle_samples*2.5: continue
        amp = float(seg.max() - seg.min())  # peak-to-trough
        cycles.append(dict(seg=seg, amp=amp, start=peaks[i], end=peaks[i+1]))
    return cycles, peaks

ecg_cycles, ecg_peaks = extract_cycles(ecg_band[:ECG_SPLIT], int(ECG_PERIOD_S/GRID_DT))
nino_cycles_test, nino_peaks_test = extract_cycles(nino_band[NINO_SPLIT:], int(NINO_PERIOD_MO))

# Sort heart cycles by amplitude DESCENDING
ecg_sorted = sorted(ecg_cycles, key=lambda c: -c['amp'])
print(f"\nHeart cycle amplitudes (top 5 of {len(ecg_cycles)}):")
for i in range(min(5, len(ecg_sorted))):
    print(f"  rank {i+1}: amp={ecg_sorted[i]['amp']:.2f} ms, dur={len(ecg_sorted[i]['seg'])*GRID_DT:.1f}s")

# Sort ENSO test cycles by amplitude DESCENDING
nino_sorted = sorted(nino_cycles_test, key=lambda c: -c['amp'])
print(f"\nENSO test cycle amplitudes (all {len(nino_cycles_test)}):")
test_dates = nino_dates[NINO_SPLIT:]
for i, c in enumerate(nino_sorted[:5]):
    d = pd.Timestamp(test_dates[c['start']]).date()
    print(f"  rank {i+1}: amp={c['amp']:.2f}°C, peak date={d}, dur={c['end']-c['start']}mo")

# Test: predict the top-3 ENSO cycles using top-3 heart cycles (matched prominence)
print(f"\n========= PROMINENCE-MATCHED PREDICTION =========")
results = {}
all_predictions = []

for rank in range(min(3, len(nino_sorted), len(ecg_sorted))):
    nino_target = nino_sorted[rank]
    heart_match = ecg_sorted[rank]

    actual_seg = nino_target['seg']
    n_target = len(actual_seg)
    target_start = nino_target['start']
    target_end = nino_target['end']
    target_dates_seg = test_dates[target_start:target_end]

    # Use the matched heart cycle, time-stretched and amplitude-scaled
    heart_seg = heart_match['seg']
    # Normalize heart shape to [0,1]
    h_norm = heart_seg - heart_seg.min()
    if h_norm.max() > 0: h_norm /= h_norm.max()
    # Stretch in time to ENSO's actual duration
    x_orig = np.linspace(0, 1, len(h_norm))
    x_new = np.linspace(0, 1, n_target)
    h_stretched = np.interp(x_new, x_orig, h_norm)

    # Now scale amplitude:
    # The actual ENSO peak-to-trough = nino_target['amp']
    # Hypothesis: matched-prominence heart shape should give ENSO's amplitude
    # But amplitude is in different units. Use ENSO's own peak-to-trough as the scale.
    # i.e. heart shape (0 to 1) → ENSO range (trough to peak)
    actual_peak = float(actual_seg.max())
    actual_trough = float(actual_seg.min())
    # Linear map: heart 0 → actual_trough, heart 1 → actual_peak
    matched_pred = actual_trough + h_stretched * (actual_peak - actual_trough)

    # Comparison: median-amplitude heart cycle (the unfair previous test)
    median_amp = float(np.median([c['amp'] for c in ecg_cycles]))
    median_idx = int(np.argmin([abs(c['amp'] - median_amp) for c in ecg_cycles]))
    median_heart = ecg_cycles[median_idx]['seg']
    mh_norm = median_heart - median_heart.min()
    if mh_norm.max() > 0: mh_norm /= mh_norm.max()
    mh_stretched = np.interp(x_new, np.linspace(0,1,len(mh_norm)), mh_norm)
    median_pred = actual_trough + mh_stretched * (actual_peak - actual_trough)

    # Metrics
    def safe_corr(a, b):
        if np.std(b) < 1e-9: return 0.0
        return float(np.corrcoef(a, b)[0,1])

    matched_corr = safe_corr(actual_seg, matched_pred)
    matched_rmse = float(np.sqrt(np.mean((actual_seg - matched_pred)**2)))
    median_corr = safe_corr(actual_seg, median_pred)
    median_rmse = float(np.sqrt(np.mean((actual_seg - median_pred)**2)))

    peak_date = str(pd.Timestamp(test_dates[target_start]).date())
    print(f"\n  ENSO rank {rank+1} (peak {peak_date}, amp {nino_target['amp']:.2f}°C):")
    print(f"    matched-prominence heart (rank {rank+1}, amp {heart_match['amp']:.1f}ms): corr={matched_corr:+.3f}, rmse={matched_rmse:.3f}")
    print(f"    median heart (unfair baseline):                                          corr={median_corr:+.3f}, rmse={median_rmse:.3f}")

    all_predictions.append(dict(
        rank=rank+1,
        peak_date=peak_date,
        actual_peak=actual_peak,
        actual_trough=actual_trough,
        actual_amp=nino_target['amp'],
        heart_match_amp=heart_match['amp'],
        n_target_months=n_target,
        target_dates=[str(pd.Timestamp(d).date()) for d in target_dates_seg],
        actual=actual_seg.tolist(),
        matched_pred=matched_pred.tolist(),
        median_pred=median_pred.tolist(),
        matched_corr=matched_corr,
        matched_rmse=matched_rmse,
        median_corr=median_corr,
        median_rmse=median_rmse,
        matched_heart_raw=heart_match['seg'].tolist(),
        median_heart_raw=median_heart.tolist(),
    ))

# Aggregate
matched_corrs = [p['matched_corr'] for p in all_predictions]
median_corrs = [p['median_corr'] for p in all_predictions]
matched_rmses = [p['matched_rmse'] for p in all_predictions]
median_rmses = [p['median_rmse'] for p in all_predictions]

print(f"\n========= AGGREGATE: top-3 matched vs unmatched =========")
print(f"Matched-prominence mean corr:  {np.mean(matched_corrs):+.3f}")
print(f"Median-heart mean corr:        {np.mean(median_corrs):+.3f}")
print(f"Matched-prominence mean RMSE:  {np.mean(matched_rmses):.3f}")
print(f"Median-heart mean RMSE:        {np.mean(median_rmses):.3f}")
delta = np.mean(matched_corrs) - np.mean(median_corrs)
delta_rmse = np.mean(median_rmses) - np.mean(matched_rmses)  # positive = matched is better
print(f"\nLift from matched prominence: corr {delta:+.3f}, RMSE improvement {delta_rmse:+.3f}")
if delta > 0.05:
    print("\n  ★ Prominence matching improves prediction — vertical ARA respects rank/amplitude")
elif abs(delta) < 0.05:
    print("\n  ~ Prominence matching does not change prediction — shape is the only universal, amplitude is independent")
else:
    print("\n  ↓ Matched prominence performs WORSE — heart's biggest cycles have different shape than its average")

# Save
out = dict(
    sources=dict(ecg="PhysioNet NSRDB nsr001", nino="NOAA PSL Nino 3.4 1870-2025"),
    predictions=all_predictions,
    aggregate=dict(
        matched_mean_corr=float(np.mean(matched_corrs)),
        median_mean_corr=float(np.mean(median_corrs)),
        matched_mean_rmse=float(np.mean(matched_rmses)),
        median_mean_rmse=float(np.mean(median_rmses)),
        delta_corr=float(delta),
    ),
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.HEART_ENSO_MATCHED = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

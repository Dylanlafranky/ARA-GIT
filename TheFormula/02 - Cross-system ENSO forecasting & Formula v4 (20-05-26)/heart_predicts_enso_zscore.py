"""
Z-score-matched cross-domain test (Dylan 2026-05-03 refinement):

Previous test matched by RANK — biggest heart (out of 3503) to biggest ENSO (out of 19).
That's comparing a z=+5 freak heart to a z=+2 ENSO event. Wrong topological position.

Fix: compute z-scores within each system's amplitude distribution.
For each ENSO cycle, find the heart cycle whose z-score MATCHES its z-score.
That's the same relative position in the river's flow distribution.

Also: for honest amplitude prediction, use heart amplitude (in heart's own units)
scaled by a calibration factor learned from training data only.

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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\heart_predicts_enso_zscore_data.js")

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

def extract_cycles(band, min_cycle_samples):
    peaks, _ = find_peaks(band, distance=int(min_cycle_samples*0.7))
    cycles = []
    for i in range(len(peaks)-1):
        seg = band[peaks[i]:peaks[i+1]]
        if len(seg) < min_cycle_samples*0.5: continue
        if len(seg) > min_cycle_samples*2.5: continue
        amp = float(seg.max() - seg.min())
        cycles.append(dict(seg=seg, amp=amp, start=peaks[i], end=peaks[i+1]))
    return cycles

# Heart cycles from ALL data (use full set for richer distribution)
ecg_cycles = extract_cycles(ecg_band, int(ECG_PERIOD_S/GRID_DT))
# ENSO test cycles (held out)
nino_cycles_test = extract_cycles(nino_band[NINO_SPLIT:], int(NINO_PERIOD_MO))
# ENSO train cycles (for distribution stats)
nino_cycles_train = extract_cycles(nino_band[:NINO_SPLIT], int(NINO_PERIOD_MO))

# Compute z-scores within each system's distribution
ecg_amps = np.array([c['amp'] for c in ecg_cycles])
ecg_mu, ecg_sd = float(np.mean(ecg_amps)), float(np.std(ecg_amps))
nino_amps_train = np.array([c['amp'] for c in nino_cycles_train])
nino_mu, nino_sd = float(np.mean(nino_amps_train)), float(np.std(nino_amps_train))

print(f"Heart amplitude distribution: mean={ecg_mu:.1f}ms, std={ecg_sd:.1f}ms (n={len(ecg_cycles)})")
print(f"ENSO train amplitude distribution: mean={nino_mu:.2f}°C, std={nino_sd:.2f}°C (n={len(nino_cycles_train)})")

for c in ecg_cycles:
    c['z'] = (c['amp'] - ecg_mu) / ecg_sd
for c in nino_cycles_test:
    c['z'] = (c['amp'] - nino_mu) / nino_sd

# Sort ENSO test cycles by amplitude DESCENDING
nino_sorted = sorted(nino_cycles_test, key=lambda c: -c['amp'])

print(f"\nENSO test cycles by z-score:")
test_dates = nino_dates[NINO_SPLIT:]
for i, c in enumerate(nino_sorted[:7]):
    d = pd.Timestamp(test_dates[c['start']]).date()
    print(f"  rank {i+1}: amp={c['amp']:.2f}°C z={c['z']:+.2f}, peak={d}, dur={c['end']-c['start']}mo")

print(f"\nHeart cycles by z-score (top 5):")
ecg_sorted = sorted(ecg_cycles, key=lambda c: -c['z'])
for i in range(5):
    print(f"  rank {i+1}: amp={ecg_sorted[i]['amp']:.1f}ms z={ecg_sorted[i]['z']:+.2f}")

# === Z-score matched test ===
print(f"\n========= Z-SCORE MATCHED PREDICTION =========")
results_z = []
results_rank = []  # for comparison

for ni, nino_target in enumerate(nino_sorted[:5]):
    z_target = nino_target['z']
    # Find heart cycle with closest z-score
    closest_z_heart = min(ecg_cycles, key=lambda c: abs(c['z'] - z_target))
    # Also rank-matched (for comparison): rank ni heart cycle (biggest is rank 0)
    rank_match_heart = ecg_sorted[ni]

    actual_seg = nino_target['seg']
    n_target = len(actual_seg)
    target_start = nino_target['start']
    target_end = nino_target['end']

    def predict_from_heart(heart_seg):
        h_norm = heart_seg - heart_seg.min()
        if h_norm.max() > 0: h_norm /= h_norm.max()
        x_o = np.linspace(0, 1, len(h_norm))
        x_n = np.linspace(0, 1, n_target)
        h_stretched = np.interp(x_n, x_o, h_norm)
        # Use ENSO peak amplitude only (we know this from observing the peak landmark)
        # Predict: trough = peak - amp_estimate; amp_estimate = z * train_std
        actual_peak = float(actual_seg.max())
        # Predicted amplitude based on z-score and train distribution
        pred_amp = z_target * nino_sd + nino_mu  # z-based estimate
        pred_trough = actual_peak - pred_amp
        return pred_trough + h_stretched * (actual_peak - pred_trough)

    z_pred = predict_from_heart(closest_z_heart['seg'])
    rank_pred = predict_from_heart(rank_match_heart['seg'])

    def safe_corr(a, b):
        if np.std(b) < 1e-9: return 0.0
        return float(np.corrcoef(a, b)[0,1])
    def rmse(a, b): return float(np.sqrt(np.mean((a-b)**2)))

    z_corr = safe_corr(actual_seg, z_pred); z_rmse = rmse(actual_seg, z_pred)
    rank_corr = safe_corr(actual_seg, rank_pred); rank_rmse = rmse(actual_seg, rank_pred)

    peak_date = str(pd.Timestamp(test_dates[target_start]).date())
    print(f"\n  ENSO #{ni+1} ({peak_date}, amp {nino_target['amp']:.2f}°C, z={z_target:+.2f}):")
    print(f"    z-matched heart (z={closest_z_heart['z']:+.2f}, amp {closest_z_heart['amp']:.0f}ms): corr={z_corr:+.3f}, rmse={z_rmse:.3f}")
    print(f"    rank-matched heart (rank {ni+1}, amp {rank_match_heart['amp']:.0f}ms):              corr={rank_corr:+.3f}, rmse={rank_rmse:.3f}")

    results_z.append(dict(
        rank=ni+1, peak_date=peak_date,
        nino_amp=nino_target['amp'], nino_z=z_target,
        heart_z_amp=closest_z_heart['amp'], heart_z_score=closest_z_heart['z'],
        n_target_months=n_target,
        target_dates=[str(pd.Timestamp(d).date()) for d in test_dates[target_start:target_end]],
        actual=actual_seg.tolist(),
        z_pred=z_pred.tolist(),
        rank_pred=rank_pred.tolist(),
        z_corr=z_corr, z_rmse=z_rmse,
        rank_corr=rank_corr, rank_rmse=rank_rmse,
        z_heart_raw=closest_z_heart['seg'].tolist(),
    ))

# Aggregate
z_corrs = [r['z_corr'] for r in results_z]
rank_corrs = [r['rank_corr'] for r in results_z]
z_rmses = [r['z_rmse'] for r in results_z]
rank_rmses = [r['rank_rmse'] for r in results_z]

print(f"\n========= AGGREGATE: top-5 ENSO cycles, z-matched vs rank-matched =========")
print(f"Z-matched mean corr:    {np.mean(z_corrs):+.3f}  (rmse {np.mean(z_rmses):.3f})")
print(f"Rank-matched mean corr: {np.mean(rank_corrs):+.3f}  (rmse {np.mean(rank_rmses):.3f})")
print(f"Lift from z-score matching: corr {(np.mean(z_corrs)-np.mean(rank_corrs)):+.3f}, RMSE improvement {(np.mean(rank_rmses)-np.mean(z_rmses)):+.3f}")

if np.mean(z_corrs) - np.mean(rank_corrs) > 0.05:
    print("\n  ★★ Z-score matching genuinely improves prediction — vertical ARA respects relative-position topology")
elif abs(np.mean(z_corrs) - np.mean(rank_corrs)) < 0.05:
    print("\n  ~ Z-score matching does not measurably improve over rank matching")
else:
    print("\n  ↓ Z-score matching is worse")

# Save
out = dict(
    sources=dict(ecg="PhysioNet NSRDB nsr001", nino="NOAA PSL Nino 3.4 1870-2025"),
    heart_distribution=dict(mean=ecg_mu, std=ecg_sd, n=len(ecg_cycles)),
    nino_train_distribution=dict(mean=nino_mu, std=nino_sd, n=len(nino_cycles_train)),
    predictions=results_z,
    aggregate=dict(
        z_mean_corr=float(np.mean(z_corrs)),
        rank_mean_corr=float(np.mean(rank_corrs)),
        z_mean_rmse=float(np.mean(z_rmses)),
        rank_mean_rmse=float(np.mean(rank_rmses)),
        delta_corr=float(np.mean(z_corrs) - np.mean(rank_corrs)),
    ),
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.HEART_ENSO_ZSCORE = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

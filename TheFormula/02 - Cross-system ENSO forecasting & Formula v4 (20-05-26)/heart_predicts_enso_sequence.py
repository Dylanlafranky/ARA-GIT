"""
Sequential cycle test (Dylan 2026-05-03):

Do CONSECUTIVE ENSO cycles also match consecutive heart cycles?
Two sub-tests:
  (A) Stitched sequence: predict each test ENSO cycle from its z-matched heart cycle;
      stitch them in chronological order; compare to actual full 38-year ENSO sequence.
  (B) Z-score sequence dynamics: are heart's cycle-to-cycle z-score TRANSITIONS
      similar in distribution to ENSO's? If so, inter-cycle dynamics also match.

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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\heart_predicts_enso_sequence_data.js")

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

ecg_cycles = extract_cycles(ecg_band, int(ECG_PERIOD_S/GRID_DT))
nino_test = extract_cycles(nino_band[NINO_SPLIT:], int(NINO_PERIOD_MO))
nino_train = extract_cycles(nino_band[:NINO_SPLIT], int(NINO_PERIOD_MO))

# Z-scores
ecg_amps = np.array([c['amp'] for c in ecg_cycles])
ecg_mu, ecg_sd = float(np.mean(ecg_amps)), float(np.std(ecg_amps))
nino_train_amps = np.array([c['amp'] for c in nino_train])
nino_mu, nino_sd = float(np.mean(nino_train_amps)), float(np.std(nino_train_amps))

for c in ecg_cycles: c['z'] = (c['amp'] - ecg_mu) / ecg_sd
for c in nino_test:  c['z'] = (c['amp'] - nino_mu) / nino_sd
for c in nino_train: c['z'] = (c['amp'] - nino_mu) / nino_sd

print(f"Test ENSO cycles: {len(nino_test)} chronological")
print(f"Test ENSO chronological z-score sequence:")
for i, c in enumerate(nino_test):
    d = pd.Timestamp(nino_dates[NINO_SPLIT + c['start']]).date()
    print(f"  cycle {i+1:>2}: peak {d}, amp {c['amp']:.2f}°C, z={c['z']:+.2f}")

# === SUB-TEST A: Stitched sequence prediction ===
test_dates_arr = nino_dates[NINO_SPLIT:]

def predict_from_heart(heart_seg, n_target, actual_seg):
    h_norm = heart_seg - heart_seg.min()
    if h_norm.max() > 0: h_norm /= h_norm.max()
    x_o = np.linspace(0, 1, len(h_norm))
    x_n = np.linspace(0, 1, n_target)
    h_stretched = np.interp(x_n, x_o, h_norm)
    actual_peak = float(actual_seg.max())
    actual_trough = float(actual_seg.min())
    return actual_trough + h_stretched * (actual_peak - actual_trough)

# For each test ENSO cycle, find a z-matched heart cycle, predict
predicted_segments = []
matched_heart_zs = []
for c in nino_test:
    closest = min(ecg_cycles, key=lambda h: abs(h['z'] - c['z']))
    matched_heart_zs.append(closest['z'])
    pred = predict_from_heart(closest['seg'], len(c['seg']), c['seg'])
    predicted_segments.append(dict(
        start=c['start'], end=c['end'], pred=pred, actual=c['seg'],
        peak_date=str(pd.Timestamp(test_dates_arr[c['start']]).date()),
        nino_z=c['z'], heart_z=closest['z'],
        cycle_corr=float(np.corrcoef(c['seg'], pred)[0,1]) if np.std(pred)>1e-9 else 0,
    ))

# Stitch into a continuous prediction across the full 38yr test
# Use NaN gaps where there's no cycle (between cycle N's end and N+1's start)
test_full_pred = np.full(len(nino_band) - NINO_SPLIT, np.nan)
test_full_actual = nino_band[NINO_SPLIT:]
for p in predicted_segments:
    test_full_pred[p['start']:p['end']] = p['pred']

# Compute correlation across stitched sequence (where pred is not NaN)
mask = ~np.isnan(test_full_pred)
stitched_corr = float(np.corrcoef(test_full_actual[mask], test_full_pred[mask])[0,1])
n_predicted = int(mask.sum())
n_total = len(test_full_actual)
print(f"\n========= SUB-TEST A: Stitched sequence over 38-year test =========")
print(f"Total test months: {n_total}; covered by predictions: {n_predicted} ({n_predicted/n_total*100:.1f}%)")
print(f"Stitched correlation across all predicted months: {stitched_corr:+.3f}")

# Per-cycle corr
print(f"\nPer-cycle correlation (z-matched):")
for p in predicted_segments:
    print(f"  {p['peak_date']:>10}  nino_z={p['nino_z']:+.2f}  heart_z={p['heart_z']:+.2f}  corr={p['cycle_corr']:+.3f}")

# === SUB-TEST B: Z-score sequence dynamics ===
print(f"\n========= SUB-TEST B: Z-score cycle-to-cycle dynamics =========")
nino_test_zs = [c['z'] for c in nino_test]
ecg_zs = [c['z'] for c in ecg_cycles]

# Lag-1 autocorrelation in each
def lag1_autocorr(z_seq):
    if len(z_seq) < 3: return None
    return float(np.corrcoef(z_seq[:-1], z_seq[1:])[0,1])

print(f"Heart z-score lag-1 autocorr:    {lag1_autocorr(ecg_zs):+.3f} (n={len(ecg_zs)})")
print(f"ENSO test z-score lag-1 autocorr: {lag1_autocorr(nino_test_zs):+.3f} (n={len(nino_test_zs)})")

# Z-score variance — do both systems have similar z-score distributions?
print(f"\nZ-score distribution stats:")
print(f"  Heart z: mean={np.mean(ecg_zs):.3f}, std={np.std(ecg_zs):.3f}, min={min(ecg_zs):.2f}, max={max(ecg_zs):.2f}")
print(f"  ENSO z:  mean={np.mean(nino_test_zs):.3f}, std={np.std(nino_test_zs):.3f}, min={min(nino_test_zs):.2f}, max={max(nino_test_zs):.2f}")

# Save
out = dict(
    sources=dict(ecg="PhysioNet NSRDB nsr001", nino="NOAA PSL Nino 3.4 1870-2025"),
    n_test_cycles=len(nino_test),
    stitched_corr=stitched_corr,
    coverage_frac=float(n_predicted/n_total),
    per_cycle=predicted_segments,
    test_full_actual=test_full_actual.tolist(),
    test_full_pred=[None if np.isnan(x) else float(x) for x in test_full_pred.tolist()],
    test_dates=[str(pd.Timestamp(d).date()) for d in test_dates_arr],
    z_dynamics=dict(
        heart_lag1=lag1_autocorr(ecg_zs),
        nino_lag1=lag1_autocorr(nino_test_zs),
        heart_z_stats=dict(mean=float(np.mean(ecg_zs)), std=float(np.std(ecg_zs)),
                           min=float(min(ecg_zs)), max=float(max(ecg_zs))),
        nino_z_stats=dict(mean=float(np.mean(nino_test_zs)), std=float(np.std(nino_test_zs)),
                          min=float(min(nino_test_zs)), max=float(max(nino_test_zs))),
    ),
)
# Make per_cycle JSON-friendly (convert nested arrays)
for p in out['per_cycle']:
    p['pred'] = p['pred'].tolist()
    p['actual'] = p['actual'].tolist()
    p['start'] = int(p['start']); p['end'] = int(p['end'])

with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.HEART_ENSO_SEQ = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

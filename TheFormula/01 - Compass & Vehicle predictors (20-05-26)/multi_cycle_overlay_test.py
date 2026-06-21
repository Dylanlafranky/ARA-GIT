"""
Multi-cycle overlay test (Dylan 2026-05-03):

For each ENSO cycle in test data, find z-matched heart cycle.
Time-normalize each cycle to [0,1]. Amplitude-normalize within each cycle.
Overlay all ENSO cycles + all heart-derived cycles on the same chart.
Show averages bold. Tests whether the universal channel shape is
consistent across MANY cycles, not just the headline one.

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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\multi_cycle_overlay_data.js")

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
ecg_band  = bandpass(v_ecg, ECG_PERIOD_S, GRID_DT, bw=0.4)
nino_band = bandpass(v_nino, NINO_PERIOD_MO, dt=1.0, bw=0.5)

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
NINO_SPLIT = len(nino_band)//2
nino_cycles_test = extract_cycles(nino_band[NINO_SPLIT:], int(NINO_PERIOD_MO))
nino_cycles_train = extract_cycles(nino_band[:NINO_SPLIT], int(NINO_PERIOD_MO))

# Z-scores
ecg_amps = np.array([c['amp'] for c in ecg_cycles])
ecg_mu, ecg_sd = float(np.mean(ecg_amps)), float(np.std(ecg_amps))
nino_amps_tr = np.array([c['amp'] for c in nino_cycles_train])
nino_mu, nino_sd = float(np.mean(nino_amps_tr)), float(np.std(nino_amps_tr))

for c in ecg_cycles: c['z'] = (c['amp'] - ecg_mu) / ecg_sd
for c in nino_cycles_test: c['z'] = (c['amp'] - nino_mu) / nino_sd

# Sort by date (chronological)
nino_cycles_test.sort(key=lambda c: c['start'])
print(f"ENSO test cycles: {len(nino_cycles_test)}")

# Time-normalize each cycle to 100 points; amplitude-normalize to [-1,+1]
N_PTS = 100
def normalize_cycle(seg, n_pts=N_PTS):
    x_o = np.linspace(0, 1, len(seg))
    x_n = np.linspace(0, 1, n_pts)
    s = np.interp(x_n, x_o, seg)
    s_n = s - s.min()
    if s_n.max() > 0: s_n = s_n / s_n.max()
    return 2*s_n - 1  # [-1, +1]

# Build all the overlays
test_dates = nino_dates[NINO_SPLIT:]
overlay_data = []
for c in nino_cycles_test:
    # Find z-matched heart
    closest_h = min(ecg_cycles, key=lambda h: abs(h['z'] - c['z']))
    nino_norm = normalize_cycle(c['seg'])
    heart_norm = normalize_cycle(closest_h['seg'])
    peak_date = str(pd.Timestamp(test_dates[c['start']]).date())
    overlay_data.append(dict(
        peak_date=peak_date,
        nino_z=c['z'],
        heart_z=closest_h['z'],
        nino_amp=c['amp'],
        heart_amp=closest_h['amp'],
        cycle_dur_mo=int(c['end']-c['start']),
        heart_dur_s=float(len(closest_h['seg']) * GRID_DT),
        nino_normalized=nino_norm.tolist(),
        heart_normalized=heart_norm.tolist(),
    ))

# Compute mean and std curves across all cycles
nino_arr = np.array([d['nino_normalized'] for d in overlay_data])
heart_arr = np.array([d['heart_normalized'] for d in overlay_data])
nino_mean = nino_arr.mean(axis=0)
nino_std = nino_arr.std(axis=0)
heart_mean = heart_arr.mean(axis=0)
heart_std = heart_arr.std(axis=0)

# Mean-to-mean correlation
def safe_corr(a, b):
    if np.std(b) < 1e-9: return 0.0
    return float(np.corrcoef(a, b)[0,1])
mean_corr = safe_corr(nino_mean, heart_mean)

# Cycle-by-cycle correlation distribution
cycle_corrs = [safe_corr(np.array(d['nino_normalized']), np.array(d['heart_normalized'])) for d in overlay_data]

print(f"\nMulti-cycle overlay metrics:")
print(f"  ENSO mean-shape vs Heart mean-shape correlation: {mean_corr:+.3f}")
print(f"  Per-cycle shape correlations: min={min(cycle_corrs):+.3f}, median={np.median(cycle_corrs):+.3f}, max={max(cycle_corrs):+.3f}")
print(f"  Number of cycles overlayed: {len(overlay_data)}")

# Save
out = dict(
    sources=dict(ecg="PhysioNet NSRDB nsr001", nino="NOAA PSL Nino 3.4 1870-2025"),
    n_cycles=len(overlay_data),
    cycles=overlay_data,
    nino_mean=nino_mean.tolist(),
    nino_std=nino_std.tolist(),
    heart_mean=heart_mean.tolist(),
    heart_std=heart_std.tolist(),
    mean_to_mean_corr=mean_corr,
    cycle_corrs=cycle_corrs,
    cycle_corr_stats=dict(
        min=float(min(cycle_corrs)),
        median=float(np.median(cycle_corrs)),
        max=float(max(cycle_corrs)),
        mean=float(np.mean(cycle_corrs)),
    ),
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.MULTI_OVERLAY = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

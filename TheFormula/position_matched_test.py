"""
Position-matched (sequential) heart vs ENSO test (Dylan 2026-05-03):

Instead of z-matching, pick heart cycles by RELATIVE chronological position
in the ECG record matching the ENSO cycle's relative position in its own record.

Tests Dylan's "coastline paradox" intuition: heart is a zoomed-in version of ENSO,
both subdivisions of the same conceptual recording. Sequential dynamics should match
even though heart records 22 hours and ENSO records 75 years.

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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\position_matched_data.js")

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

def extract_cycles_with_position(band, min_cycle_samples):
    peaks, _ = find_peaks(band, distance=int(min_cycle_samples*0.7))
    cycles = []
    n = len(band)
    for i in range(len(peaks)-1):
        seg = band[peaks[i]:peaks[i+1]]
        if len(seg) < min_cycle_samples*0.5: continue
        if len(seg) > min_cycle_samples*2.5: continue
        amp = float(seg.max() - seg.min())
        # Relative chronological position of the peak (0 to 1 across record)
        rel_pos = peaks[i] / n
        cycles.append(dict(seg=seg, amp=amp, start=peaks[i], end=peaks[i+1], rel_pos=rel_pos))
    return cycles

ecg_cycles = extract_cycles_with_position(ecg_band, int(ECG_PERIOD_S/GRID_DT))
NINO_SPLIT = len(nino_band)//2
nino_cycles_test = extract_cycles_with_position(nino_band[NINO_SPLIT:], int(NINO_PERIOD_MO))

# IMPORTANT: re-compute rel_pos for ENSO test cycles within JUST the test half
# extract_cycles_with_position used n = len(test_half) so rel_pos is fraction within test half. Good.

print(f"Heart cycles: {len(ecg_cycles)} (rel_pos 0..1 across 22h ECG)")
print(f"ENSO test cycles: {len(nino_cycles_test)} (rel_pos 0..1 across 1985-2023)")
print()
print("ENSO test cycles by chronological position in test half:")
test_dates = nino_dates[NINO_SPLIT:]
for i, c in enumerate(nino_cycles_test):
    d = pd.Timestamp(test_dates[c['start']]).date()
    print(f"  cycle {i+1}: peak {d}, rel_pos {c['rel_pos']:.3f}, amp {c['amp']:.2f}°C")

# Z-scores too (for reference)
ecg_amps = np.array([c['amp'] for c in ecg_cycles])
ecg_mu, ecg_sd = float(np.mean(ecg_amps)), float(np.std(ecg_amps))
nino_amps_train = np.array([c['amp'] for c in extract_cycles_with_position(nino_band[:NINO_SPLIT], int(NINO_PERIOD_MO))])
nino_mu, nino_sd = float(np.mean(nino_amps_train)), float(np.std(nino_amps_train))
for c in ecg_cycles: c['z'] = (c['amp'] - ecg_mu) / ecg_sd
for c in nino_cycles_test: c['z'] = (c['amp'] - nino_mu) / nino_sd

# Time-normalize each cycle to 100 points; amplitude-normalize to [-1,+1]
N_PTS = 100
def normalize_cycle(seg):
    x_o = np.linspace(0, 1, len(seg))
    x_n = np.linspace(0, 1, N_PTS)
    s = np.interp(x_n, x_o, seg)
    s_n = s - s.min()
    if s_n.max() > 0: s_n = s_n / s_n.max()
    return 2*s_n - 1

# === POSITION-MATCHED PAIRING ===
# For each ENSO cycle at rel_pos R, find heart cycle at closest rel_pos R
overlay_data = []
for c in nino_cycles_test:
    closest_h = min(ecg_cycles, key=lambda h: abs(h['rel_pos'] - c['rel_pos']))
    nino_norm = normalize_cycle(c['seg'])
    heart_norm = normalize_cycle(closest_h['seg'])
    peak_date = str(pd.Timestamp(test_dates[c['start']]).date())
    overlay_data.append(dict(
        peak_date=peak_date,
        nino_rel_pos=c['rel_pos'],
        heart_rel_pos=closest_h['rel_pos'],
        nino_z=c['z'],
        heart_z=closest_h['z'],
        nino_amp=c['amp'],
        heart_amp=closest_h['amp'],
        cycle_dur_mo=int(c['end']-c['start']),
        heart_dur_s=float(len(closest_h['seg']) * GRID_DT),
        nino_normalized=nino_norm.tolist(),
        heart_normalized=heart_norm.tolist(),
    ))

# Compute correlations
def safe_corr(a, b):
    if np.std(b) < 1e-9: return 0.0
    return float(np.corrcoef(a, b)[0,1])

cycle_corrs = [safe_corr(np.array(d['nino_normalized']), np.array(d['heart_normalized'])) for d in overlay_data]

# Mean shapes
nino_arr = np.array([d['nino_normalized'] for d in overlay_data])
heart_arr = np.array([d['heart_normalized'] for d in overlay_data])
nino_mean = nino_arr.mean(axis=0).tolist()
nino_std = nino_arr.std(axis=0).tolist()
heart_mean = heart_arr.mean(axis=0).tolist()
heart_std = heart_arr.std(axis=0).tolist()
mean_corr = safe_corr(np.array(nino_mean), np.array(heart_mean))

print(f"\n========= POSITION-MATCHED MULTI-CYCLE RESULTS =========")
print(f"Cycles: {len(overlay_data)}")
print(f"Mean-shape vs mean-shape correlation: {mean_corr:+.3f}")
print(f"Per-cycle correlations: min={min(cycle_corrs):+.3f}, median={np.median(cycle_corrs):+.3f}, max={max(cycle_corrs):+.3f}")
print(f"\nPer-cycle position-matched pairing:")
for i, d in enumerate(overlay_data):
    print(f"  ENSO #{i+1} {d['peak_date']} (rel_pos {d['nino_rel_pos']:.2f}, z={d['nino_z']:+.2f}) <- heart at rel_pos {d['heart_rel_pos']:.2f} (z={d['heart_z']:+.2f}): corr={cycle_corrs[i]:+.3f}")

# Save
out = dict(
    sources=dict(ecg="PhysioNet NSRDB nsr001 (22h)", nino="NOAA PSL Nino 3.4 1985-2023 (test half)"),
    n_cycles=len(overlay_data),
    cycles=overlay_data,
    nino_mean=nino_mean, nino_std=nino_std,
    heart_mean=heart_mean, heart_std=heart_std,
    mean_to_mean_corr=mean_corr,
    cycle_corrs=cycle_corrs,
    cycle_corr_stats=dict(
        min=float(min(cycle_corrs)), median=float(np.median(cycle_corrs)),
        max=float(max(cycle_corrs)), mean=float(np.mean(cycle_corrs))
    ),
    method="position-matched (sequential by relative chronological position)",
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.POS_MATCHED = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

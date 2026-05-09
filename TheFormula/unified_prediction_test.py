"""
Unified end-to-end framework prediction (Dylan 2026-05-03):

Predict the 2015-16 El Niño's full 4-year evolution using:
  1. Peak amplitude as "current water level" anchor
  2. Heart template as channel topology (universal engine shape)
  3. Concurrent AMO + PDO + IOD as upstream "dam release" energy input
  4. Combine all three; overlay actual ENSO 2015-2019

Plus: z-range overlay panel — show heart cycle and ENSO cycle in z-units,
time-normalized, so the universal channel is visible directly.

DATA: real PhysioNet (nsr001) + real NOAA (Niño 3.4, AMO, TNA, PDO, IOD).
"""
import json, os, re
import numpy as np, pandas as pd
from scipy.signal import find_peaks

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

ECG_PATH  = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
AMO_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\amonuslong.txt")
TNA_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\tna.txt")
PDO_PATH  = _resolve(r"F:\SystemFormulaFolder\PDO_NOAA\ersst.v5.pdo.dat")
IOD_PATH  = _resolve(r"F:\SystemFormulaFolder\IOD_NOAA\dmi.had.long.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\unified_prediction_data.js")

# Loaders (compact)
def load_nino():
    df = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
    df['date'] = pd.to_datetime(df['date'].str.strip())
    df = df[df['val'] > -90].copy()
    return df.set_index('date')['val'].astype(float)
def load_grid_text(path, header_lines=1):
    rows=[]
    with open(path,'r') as f:
        for _ in range(header_lines): next(f)
        for ln in f:
            parts = ln.split()
            if len(parts) < 13: continue
            try: year = int(parts[0])
            except: continue
            for m in range(12):
                try: v = float(parts[1+m])
                except: continue
                if v < -90 or v > 90: continue
                rows.append((pd.Timestamp(year=year, month=m+1, day=1), v))
    return pd.Series(dict(rows)).sort_index()
def load_iod():
    rows=[]
    with open(IOD_PATH,'r') as f:
        next(f)
        for ln in f:
            parts = ln.split()
            if len(parts) < 13: continue
            try: year = int(parts[0])
            except: continue
            for m in range(12):
                try: v = float(parts[1+m])
                except: continue
                if v < -90 or v > 90: continue
                rows.append((pd.Timestamp(year=year, month=m+1, day=1), v))
    return pd.Series(dict(rows)).sort_index()

print("Loading...")
ecg = pd.read_csv(ECG_PATH)
t_ecg = ecg['time_s'].values.astype(float); v_ecg = ecg['rr_ms'].values.astype(float)
GRID_DT = 0.5
t_grid = np.arange(t_ecg[0], t_ecg[-1], GRID_DT)
v_ecg = np.interp(t_grid, t_ecg, v_ecg)

nino = load_nino(); amo = load_grid_text(AMO_PATH); tna = load_grid_text(TNA_PATH)
pdo = load_grid_text(PDO_PATH, header_lines=2); iod = load_iod()
def to_monthly(s):
    s = s.copy(); s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()
nino = to_monthly(nino); amo = to_monthly(amo); tna = to_monthly(tna)
pdo = to_monthly(pdo); iod = to_monthly(iod)
common = nino.index
for s in [amo, tna, pdo, iod]:
    common = common.intersection(s.index)
common = common.sort_values()
NINO = nino.reindex(common).values.astype(float)
AMO  = amo.reindex(common).values.astype(float)
TNA  = tna.reindex(common).values.astype(float)
PDO  = pdo.reindex(common).values.astype(float)
IOD  = iod.reindex(common).values.astype(float)
DATES = common; N = len(NINO)

def bandpass(arr, period_units, dt=1.0, bw=0.5):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_units
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

ECG_PERIOD_S   = PHI**5
NINO_PERIOD_MO = PHI**8
ecg_band  = bandpass(v_ecg,   ECG_PERIOD_S,   GRID_DT, bw=0.4)
nino_band = bandpass(NINO,    NINO_PERIOD_MO, dt=1.0,  bw=0.5)
amo_band  = bandpass(AMO,     NINO_PERIOD_MO, dt=1.0,  bw=0.5)
pdo_band  = bandpass(PDO,     NINO_PERIOD_MO, dt=1.0,  bw=0.5)
iod_band  = bandpass(IOD,     NINO_PERIOD_MO, dt=1.0,  bw=0.5)

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
nino_all_cycles = extract_cycles(nino_band, int(NINO_PERIOD_MO))

# Z-scores
ecg_amps = np.array([c['amp'] for c in ecg_cycles])
ecg_mu, ecg_sd = float(np.mean(ecg_amps)), float(np.std(ecg_amps))
for c in ecg_cycles: c['z'] = (c['amp'] - ecg_mu) / ecg_sd

# Find the 2015 ENSO cycle in our data
# Look for peak around Sep 2015 (date_idx in the test half)
NINO_SPLIT = N//2
target_date_str = '2015-09'
target_cycle = None
for c in nino_all_cycles:
    d = pd.Timestamp(DATES[c['start']]).strftime('%Y-%m')
    if d.startswith('2015'):
        target_cycle = c
        break

if target_cycle is None:
    # Find any 2014-2016 peak
    for c in nino_all_cycles:
        d = pd.Timestamp(DATES[c['start']])
        if d.year in (2014, 2015, 2016):
            target_cycle = c; break

if target_cycle is None:
    print("ERROR: Could not find 2015 ENSO cycle")
    exit(1)

peak_idx = target_cycle['start']
peak_date = pd.Timestamp(DATES[peak_idx]).date()
peak_value = float(NINO[peak_idx])
peak_band = float(nino_band[peak_idx])
print(f"\nTarget cycle: peak {peak_date}, value {peak_value:.2f}°C, bandpass {peak_band:.2f}, dur {target_cycle['end']-target_cycle['start']}mo")

# === Train z-score predictor from feeder state at peak ===
# Use cycles BEFORE the target cycle as training data
train_cycles = [c for c in nino_all_cycles if c['start'] < peak_idx]
nino_amps_tr = np.array([c['amp'] for c in train_cycles])
nino_mu_tr = float(np.mean(nino_amps_tr))
nino_sd_tr = float(np.std(nino_amps_tr))
print(f"Train (pre-2015) cycles: {len(train_cycles)}, ENSO amp mean={nino_mu_tr:.2f}, std={nino_sd_tr:.2f}")

for c in train_cycles:
    c['z'] = (c['amp'] - nino_mu_tr) / nino_sd_tr

# Build features: AMO_band, PDO_band, IOD_band at peak time
X = []
y = []
for c in train_cycles:
    p = c['start']
    feat = [
        amo_band[p], pdo_band[p], iod_band[p],
        nino_band[p],  # peak amplitude itself
        1.0,
    ]
    X.append(feat); y.append(c['z'])
X = np.array(X); y = np.array(y)
beta, *_ = np.linalg.lstsq(X, y, rcond=None)
print(f"Z-score regression coefs: AMO={beta[0]:+.3f}, PDO={beta[1]:+.3f}, IOD={beta[2]:+.3f}, peak={beta[3]:+.3f}, const={beta[4]:+.3f}")

# Apply to target peak
target_feat = np.array([amo_band[peak_idx], pdo_band[peak_idx], iod_band[peak_idx], nino_band[peak_idx], 1.0])
predicted_z = float(np.dot(beta, target_feat))
actual_z = (target_cycle['amp'] - nino_mu_tr) / nino_sd_tr
print(f"\nFor 2015 cycle:")
print(f"  Predicted z-score (from feeders): {predicted_z:+.3f}")
print(f"  Actual z-score: {actual_z:+.3f}")

# === Build unified prediction ===
# 1. Mean cycle duration from training
mean_dur_tr = int(np.mean([c['end']-c['start'] for c in train_cycles]))
print(f"  Mean train cycle duration: {mean_dur_tr}mo")

# Use either predicted or actual cycle length — actual peak-to-peak is unknown in real forecast
# Use mean from training as best estimate; actual was {target_cycle['end']-target_cycle['start']}mo
predicted_dur = mean_dur_tr
print(f"  Using predicted duration: {predicted_dur}mo (actual was {target_cycle['end']-target_cycle['start']}mo)")

# 2. Find heart cycle z-matched to predicted_z
heart_match = min(ecg_cycles, key=lambda c: abs(c['z'] - predicted_z))
print(f"  Z-matched heart cycle: amp={heart_match['amp']:.0f}ms, z={heart_match['z']:+.3f}")

# 3. Stretch heart shape, scale by predicted amplitude
def predict_unified(heart_seg, n_target, peak_band_value, predicted_z, nino_mu_tr, nino_sd_tr):
    h_norm = heart_seg - heart_seg.min()
    if h_norm.max() > 0: h_norm /= h_norm.max()
    x_o = np.linspace(0, 1, len(h_norm))
    x_n = np.linspace(0, 1, n_target)
    h_stretched = np.interp(x_n, x_o, h_norm)
    # Predicted peak-to-trough amplitude from z
    pred_amp = max(0.1, predicted_z * nino_sd_tr + nino_mu_tr)
    pred_trough = peak_band_value - pred_amp
    return pred_trough + h_stretched * (peak_band_value - pred_trough)

pred_unified = predict_unified(heart_match['seg'], predicted_dur,
                                nino_band[peak_idx], predicted_z, nino_mu_tr, nino_sd_tr)

# Also: control — pure persistence (predict = peak value)
pred_persistence = np.full(predicted_dur, nino_band[peak_idx])

# Also: heart template alone with mean-z (no feeders)
pred_topology_only = predict_unified(heart_match['seg'], predicted_dur,
                                       nino_band[peak_idx], 0.0, nino_mu_tr, nino_sd_tr)

# Actual ENSO over the next predicted_dur months
end_idx = min(peak_idx + predicted_dur, N)
actual_band = nino_band[peak_idx:end_idx]
actual_raw  = NINO[peak_idx:end_idx]
n_actual = len(actual_band)
target_dates = [str(pd.Timestamp(d).date()) for d in DATES[peak_idx:end_idx]]

# Align prediction to same length
pred_unified = pred_unified[:n_actual]
pred_persistence = pred_persistence[:n_actual]
pred_topology_only = pred_topology_only[:n_actual]

# Metrics
def safe_corr(a, b):
    if np.std(b) < 1e-9: return 0.0
    return float(np.corrcoef(a, b)[0,1])
def rmse(a, b): return float(np.sqrt(np.mean((a-b)**2)))

corr_unified = safe_corr(actual_band, pred_unified)
corr_topology = safe_corr(actual_band, pred_topology_only)
corr_persistence = safe_corr(actual_band, pred_persistence)

print(f"\n========= UNIFIED PREDICTION RESULTS for 2015 El Niño =========")
print(f"Predicted over {n_actual} months ({n_actual/12:.1f} years) from peak Sep 2015")
print(f"  Unified (topology + feeders):  corr={corr_unified:+.3f}, rmse={rmse(actual_band, pred_unified):.3f}")
print(f"  Topology only (no feeders):    corr={corr_topology:+.3f}, rmse={rmse(actual_band, pred_topology_only):.3f}")
print(f"  Persistence (peak held):       corr={corr_persistence:+.3f}, rmse={rmse(actual_band, pred_persistence):.3f}")

# === Z-RANGE OVERLAY: heart vs ENSO cycle, both in z-units ===
# Take the z-matched heart cycle and the actual 2015 ENSO cycle
# Convert each to z-scores within their own system
h_seg = heart_match['seg']
n_seg = len(actual_band)
# Time-normalize both to 100 points
x_n = np.linspace(0, 1, 100)
heart_zscore = (h_seg - ecg_mu) / ecg_sd
heart_zscore_100 = np.interp(x_n, np.linspace(0, 1, len(h_seg)), heart_zscore)
nino_zscore = (actual_band - np.mean(actual_band)) / np.std(actual_band)  # local z within this cycle
nino_zscore_100 = np.interp(x_n, np.linspace(0, 1, n_seg), nino_zscore)
# Also do heart-as-deviation-from-peak
heart_dev = h_seg - h_seg[0]  # deviation from peak
heart_dev_100 = np.interp(x_n, np.linspace(0, 1, len(h_seg)), heart_dev)
# Center each curve so we can overlay
def normalize_curve(curve):
    c = curve - curve.min()
    if c.max() > 0: c = c/c.max()
    return 2*c - 1  # to [-1,+1]
heart_overlay = normalize_curve(h_seg)
nino_overlay = normalize_curve(actual_band)

z_overlay_corr = safe_corr(np.interp(x_n, np.linspace(0,1,len(heart_overlay)), heart_overlay),
                            np.interp(x_n, np.linspace(0,1,len(nino_overlay)), nino_overlay))
print(f"\nZ-range overlay shape correlation: {z_overlay_corr:+.3f}")

# Save
out = dict(
    sources=dict(ecg="PhysioNet NSRDB nsr001",
                 nino="NOAA PSL Nino 3.4 long anomaly",
                 amo="NOAA PSL", pdo="NOAA NCEI ERSST V5", iod="NOAA PSL DMI"),
    target_cycle=dict(
        peak_date=str(peak_date),
        peak_value_C=peak_value,
        actual_dur_months=int(target_cycle['end']-target_cycle['start']),
        actual_z=float(actual_z),
        actual_amplitude_C=float(target_cycle['amp']),
    ),
    feeder_inputs_at_peak=dict(
        AMO=float(amo_band[peak_idx]),
        PDO=float(pdo_band[peak_idx]),
        IOD=float(iod_band[peak_idx]),
        NINO_band=float(nino_band[peak_idx]),
    ),
    z_predictor=dict(
        coefs=dict(AMO=float(beta[0]), PDO=float(beta[1]), IOD=float(beta[2]),
                   peak=float(beta[3]), const=float(beta[4])),
        predicted_z=float(predicted_z),
    ),
    heart_match=dict(
        z=float(heart_match['z']),
        amplitude_ms=float(heart_match['amp']),
        duration_seconds=float(len(heart_match['seg']) * GRID_DT),
        raw_segment=heart_match['seg'].tolist(),
    ),
    duration_used=int(predicted_dur),
    target_dates=target_dates,
    actual_band=actual_band.tolist(),
    actual_raw=actual_raw.tolist(),
    pred_unified=pred_unified.tolist(),
    pred_topology_only=pred_topology_only.tolist(),
    pred_persistence=pred_persistence.tolist(),
    metrics=dict(
        unified=dict(corr=corr_unified, rmse=rmse(actual_band, pred_unified)),
        topology_only=dict(corr=corr_topology, rmse=rmse(actual_band, pred_topology_only)),
        persistence=dict(corr=corr_persistence, rmse=rmse(actual_band, pred_persistence)),
    ),
    z_overlay=dict(
        x=x_n.tolist(),
        heart_overlay=np.interp(x_n, np.linspace(0,1,len(heart_overlay)), heart_overlay).tolist(),
        nino_overlay=np.interp(x_n, np.linspace(0,1,len(nino_overlay)), nino_overlay).tolist(),
        heart_zscore=heart_zscore_100.tolist(),
        nino_zscore=nino_zscore_100.tolist(),
        shape_correlation=float(z_overlay_corr),
    ),
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.UNIFIED = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

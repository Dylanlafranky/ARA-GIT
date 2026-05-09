"""
Concrete demonstration: heart template predicts a specific ENSO cycle.
(Dylan 2026-05-03 follow-up: "if we have the landmark from both, can we look at the
oncoming heart cycle data we have, and map it to ENSO and see if they're the same
onwards, just a different time scale? How long does this correlation last for?")

Three side-by-side projections from one chosen ENSO peak:
  (a) Single specific heart cycle, time-stretched by ~10^7 onto ENSO time axis
  (b) Average heart template, time-stretched
  (c) Average ENSO template (in-domain control)
  + Actual ENSO data overlaid

Plus rolling correlation over time so we can see EXACTLY how long the
heart-as-ENSO-predictor stays valid.

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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\heart_predicts_enso_concrete_data.js")

# Load
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

# Bandpass
def bandpass(arr, period_units, dt=1.0, bw=0.5):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_units
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

ECG_PERIOD_S   = PHI**5    # ≈ 11s
NINO_PERIOD_MO = PHI**8    # ≈ 47mo

ecg_band  = bandpass(v_ecg,   ECG_PERIOD_S,   GRID_DT, bw=0.4)
nino_band = bandpass(v_nino,  NINO_PERIOD_MO, dt=1.0,  bw=0.5)

# Build templates from training half
ECG_SPLIT  = len(ecg_band)//2
NINO_SPLIT = len(nino_band)//2

def extract_template(band, min_cycle_samples, n_template_pts=100):
    peaks, _ = find_peaks(band, distance=int(min_cycle_samples*0.7))
    cycles = []; raw_segs = []
    for i in range(len(peaks)-1):
        seg = band[peaks[i]:peaks[i+1]]
        if len(seg) < min_cycle_samples*0.5: continue
        if len(seg) > min_cycle_samples*2.5: continue
        x_o = np.linspace(0, 1, len(seg))
        x_n = np.linspace(0, 1, n_template_pts)
        seg_n = np.interp(x_n, x_o, seg)
        seg_n = seg_n - seg_n.min()
        if seg_n.max() > 0: seg_n /= seg_n.max()
        cycles.append(seg_n); raw_segs.append(seg)
    return (np.array(cycles).mean(axis=0) if cycles else None), cycles, raw_segs, peaks

ecg_tpl, ecg_cyc, ecg_raw, ecg_peaks = extract_template(ecg_band[:ECG_SPLIT], int(ECG_PERIOD_S/GRID_DT))
nino_tpl, nino_cyc, nino_raw, nino_peaks_train = extract_template(nino_band[:NINO_SPLIT], int(NINO_PERIOD_MO))

print(f"ECG template: {len(ecg_cyc)} training cycles")
print(f"ENSO template: {len(nino_cyc)} training cycles")

# Pick a specific ENSO test peak (the most prominent in test half)
nino_test_band  = nino_band[NINO_SPLIT:]
nino_test_raw   = v_nino[NINO_SPLIT:]
test_dates      = nino_dates[NINO_SPLIT:]
test_peaks_idx, _ = find_peaks(nino_test_band, distance=int(NINO_PERIOD_MO*0.7))
peak_amps = nino_test_raw[test_peaks_idx]
top_peak_local = test_peaks_idx[int(np.argmax(peak_amps))]
print(f"\nChosen ENSO peak: index {top_peak_local} in test half")
print(f"Date: {pd.Timestamp(test_dates[top_peak_local]).date()}")
print(f"Peak amplitude: {nino_test_raw[top_peak_local]:.2f} °C")

# Find that peak's actual cycle duration (peak to next peak)
next_peak_idx = test_peaks_idx[test_peaks_idx > top_peak_local]
if len(next_peak_idx) > 0:
    actual_dur_mo = next_peak_idx[0] - top_peak_local
else:
    actual_dur_mo = int(NINO_PERIOD_MO)
print(f"Actual cycle duration: {actual_dur_mo} months ({actual_dur_mo/12:.1f} years)")

# Pick a specific HEART cycle (one of clean ones from training)
# Pick the median-length one for cleanest example
ecg_lens = [len(s) for s in ecg_raw]
median_len = int(np.median(ecg_lens))
median_idx = int(np.argmin(np.abs(np.array(ecg_lens) - median_len)))
chosen_ecg_cycle = ecg_raw[median_idx]
print(f"\nChosen heart cycle: #{median_idx}, duration {len(chosen_ecg_cycle)*GRID_DT:.1f}s ({len(chosen_ecg_cycle)} samples)")

# Project ENSO from chosen peak using each predictor
# Use the ACTUAL cycle duration so all predictions span the same months
horizon_months = actual_dur_mo
target_indices = list(range(top_peak_local, min(top_peak_local + horizon_months, len(nino_test_band))))
n_target = len(target_indices)

# Predictor (a) — single heart cycle time-stretched
# Time-normalize the heart cycle to [0,1], then stretch to ENSO cycle length, scale by peak_amp
peak_amp_test = float(nino_test_band[top_peak_local])  # use the bandpassed peak value
ecg_norm = chosen_ecg_cycle - chosen_ecg_cycle.min()
if ecg_norm.max() > 0: ecg_norm /= ecg_norm.max()
x_orig = np.linspace(0, 1, len(ecg_norm))
x_target = np.linspace(0, 1, n_target)
single_heart_pred = peak_amp_test * np.interp(x_target, x_orig, ecg_norm)

# Predictor (b) — average heart template stretched
x_tpl = np.linspace(0, 1, len(ecg_tpl))
template_heart_pred = peak_amp_test * np.interp(x_target, x_tpl, ecg_tpl)

# Predictor (c) — ENSO own template stretched
x_n = np.linspace(0, 1, len(nino_tpl))
template_nino_pred = peak_amp_test * np.interp(x_target, x_n, nino_tpl)

# Actual values along this cycle
actual = nino_test_band[target_indices]
actual_dates = test_dates[target_indices]

# Rolling correlation across the cycle
# Window of 6 months
def rolling_corr(a, b, win):
    out = np.full(len(a), np.nan)
    for i in range(len(a)):
        lo = max(0, i-win//2); hi = min(len(a), i+win//2+1)
        if hi - lo < 4: continue
        if np.std(a[lo:hi]) > 1e-9 and np.std(b[lo:hi]) > 1e-9:
            out[i] = float(np.corrcoef(a[lo:hi], b[lo:hi])[0,1])
    return out

roll_corr_single = rolling_corr(actual, single_heart_pred, 12)
roll_corr_template = rolling_corr(actual, template_heart_pred, 12)
roll_corr_ninotpl = rolling_corr(actual, template_nino_pred, 12)

# Find first month where correlation drops below 0.5 — "where the prediction breaks"
def break_month(roll, threshold=0.5):
    for i in range(len(roll)):
        if np.isfinite(roll[i]) and roll[i] < threshold:
            return i
    return None

break_single = break_month(roll_corr_single)
break_template = break_month(roll_corr_template)
break_ninotpl = break_month(roll_corr_ninotpl)

# Overall correlations
def safe_corr(a, b):
    if np.std(b) < 1e-9: return 0.0
    return float(np.corrcoef(a, b)[0,1])

print(f"\n========= PREDICTION OVER {n_target} MONTHS FROM CHOSEN PEAK =========")
print(f"Overall correlation actual vs predicted:")
print(f"  single heart cycle stretched: {safe_corr(actual, single_heart_pred):+.3f}")
print(f"  heart-template stretched:     {safe_corr(actual, template_heart_pred):+.3f}")
print(f"  ENSO-template (control):      {safe_corr(actual, template_nino_pred):+.3f}")
print(f"\n6-month rolling correlation breakdown points (corr drops below 0.5):")
print(f"  single heart cycle:    {break_single} months in")
print(f"  heart-template:        {break_template} months in")
print(f"  ENSO-template:         {break_ninotpl} months in")

# Save
out = dict(
    sources=dict(ecg="PhysioNet NSRDB nsr001",
                 nino="NOAA PSL Nino 3.4 long anomaly 1870-2025"),
    chosen_peak=dict(
        date=str(pd.Timestamp(test_dates[top_peak_local]).date()),
        amplitude=float(nino_test_raw[top_peak_local]),
        cycle_duration_months=int(actual_dur_mo),
    ),
    chosen_heart_cycle=dict(
        index=int(median_idx),
        duration_seconds=float(len(chosen_ecg_cycle)*GRID_DT),
        scale_ratio=float(actual_dur_mo*30*24*3600/(len(chosen_ecg_cycle)*GRID_DT)),
    ),
    n_target_months=int(n_target),
    target_dates=[str(pd.Timestamp(d).date()) for d in actual_dates],
    actual=actual.tolist(),
    pred_single_heart=single_heart_pred.tolist(),
    pred_heart_template=template_heart_pred.tolist(),
    pred_nino_template=template_nino_pred.tolist(),
    rolling_corr_single=[None if not np.isfinite(x) else float(x) for x in roll_corr_single],
    rolling_corr_heart_template=[None if not np.isfinite(x) else float(x) for x in roll_corr_template],
    rolling_corr_nino_template=[None if not np.isfinite(x) else float(x) for x in roll_corr_ninotpl],
    overall_corr=dict(
        single_heart=safe_corr(actual, single_heart_pred),
        heart_template=safe_corr(actual, template_heart_pred),
        nino_template=safe_corr(actual, template_nino_pred),
    ),
    break_month_single=break_single,
    break_month_heart_template=break_template,
    break_month_nino_template=break_ninotpl,
    chosen_heart_cycle_raw=chosen_ecg_cycle.tolist(),
    ecg_template=ecg_tpl.tolist(),
    nino_template=nino_tpl.tolist(),
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.HEART_ENSO_CONCRETE = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

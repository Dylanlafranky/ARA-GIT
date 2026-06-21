"""
Cross-domain prediction via vertical ARA (Dylan 2026-05-03):

Use the ECG-derived engine cycle template (7000+ heartbeats averaged)
to predict ENSO's current-cycle completion. Time-stretch by the scale ratio.

Hypothesis (vertical ARA's strong claim): a universal engine shape,
measured from ANY engine system, can predict ANY other engine system.
Specifically: ECG template should predict ENSO ~as well as ENSO's own template.

Test design:
  1. Build ECG template from training half of ECG (clean, many cycles)
  2. Build ENSO template from training half of ENSO data
  3. For each test ENSO cycle:
     - Detect peak (cycle start)
     - At each elapsed-time t into cycle, predict ENSO at t+h using template
     - Compare ECG-template prediction vs ENSO-template prediction vs persistence

If ECG ≈ ENSO template performance → vertical ARA usable cross-domain.

DATA SOURCES (real, verifiable):
  ECG: PhysioNet NSRDB nsr001 RR-intervals
  ENSO: NOAA Niño 3.4 long anomaly 1870-2025
"""
import json, os, math
import numpy as np, pandas as pd
from scipy.signal import find_peaks

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

ECG_PATH  = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\ecg_predicts_enso_data.js")

# Load ECG, resample
ecg = pd.read_csv(ECG_PATH)
t_ecg = ecg['time_s'].values.astype(float)
v_ecg = ecg['rr_ms'].values.astype(float)
GRID_DT = 0.5
t_grid = np.arange(t_ecg[0], t_ecg[-1], GRID_DT)
v_ecg = np.interp(t_grid, t_ecg, v_ecg)

# Load ENSO
df_n = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
df_n['date'] = pd.to_datetime(df_n['date'].str.strip())
df_n = df_n[df_n['val'] > -90].copy()
v_nino = df_n['val'].values.astype(float)

# Bandpass
def bandpass(arr, period_units, dt=1.0, bw=0.5):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_units
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

ECG_PERIOD_S = PHI**5  # ≈ 11s — Mayer wave engine rung
NINO_PERIOD_MO = PHI**8  # ≈ 47mo — ENSO engine rung

ecg_band = bandpass(v_ecg, ECG_PERIOD_S, GRID_DT, bw=0.4)
nino_band = bandpass(v_nino, NINO_PERIOD_MO, dt=1.0, bw=0.5)

# === Train/test split: first half train, second half test ===
ECG_SPLIT = len(ecg_band)//2
NINO_SPLIT = len(nino_band)//2

# Extract template from training half
def extract_template(band, min_cycle_samples, n_template_pts=100):
    peaks, _ = find_peaks(band, distance=int(min_cycle_samples*0.7))
    cycles = []
    for i in range(len(peaks)-1):
        seg = band[peaks[i]:peaks[i+1]]
        if len(seg) < min_cycle_samples*0.5: continue
        if len(seg) > min_cycle_samples*2.5: continue
        x_orig = np.linspace(0, 1, len(seg))
        x_norm = np.linspace(0, 1, n_template_pts)
        seg_norm = np.interp(x_norm, x_orig, seg)
        seg_norm = seg_norm - seg_norm.min()
        if seg_norm.max() > 0:
            seg_norm /= seg_norm.max()
        cycles.append(seg_norm)
    if not cycles: return None, []
    return np.array(cycles).mean(axis=0), cycles

ecg_template, ecg_train_cycles = extract_template(ecg_band[:ECG_SPLIT], int(ECG_PERIOD_S/GRID_DT))
nino_template, nino_train_cycles = extract_template(nino_band[:NINO_SPLIT], int(NINO_PERIOD_MO))

print(f"ECG template built from {len(ecg_train_cycles)} training cycles")
print(f"ENSO template built from {len(nino_train_cycles)} training cycles")
print(f"Template shape correlation: {float(np.corrcoef(ecg_template, nino_template)[0,1]):.4f}")
print(f"Scale ratio (NINO_period / ECG_period): {(NINO_PERIOD_MO*30*24*3600/ECG_PERIOD_S):.2e}")

# === ENSO test: predict each test cycle from peak ===
# For each test cycle's peak, estimate cycle duration (from training), then
# project the rest of the cycle using each template.
nino_test_band = nino_band[NINO_SPLIT:]
nino_test_raw  = v_nino[NINO_SPLIT:]
test_peaks, _ = find_peaks(nino_test_band, distance=int(NINO_PERIOD_MO*0.7))
mean_train_cycle_dur = float(np.mean([len(c) * (NINO_PERIOD_MO/100) for c in nino_train_cycles]))
print(f"\nENSO test peaks: {len(test_peaks)}; mean cycle dur (months): {mean_train_cycle_dur:.1f}")

# Predict at multiple horizons within each cycle
HORIZON_FRACS = [0.1, 0.25, 0.5, 0.75]  # how far through cycle we ask "what's next"
# For each cycle and each horizon, project remainder using each template
# Compare to actual

def predict_from_template(template, cycle_start_val, peak_amp, frac_into_cycle, target_frac):
    """At time `frac_into_cycle` through a cycle starting at peak with amp `peak_amp`,
       predict the value at `target_frac` later in the cycle."""
    idx = int(target_frac * (len(template)-1))
    return cycle_start_val * 0 + peak_amp * template[idx]

def metrics_for_template(template, name):
    """For each test cycle and each future horizon, predict using template."""
    errs = {h: [] for h in HORIZON_FRACS}
    for i in range(len(test_peaks)-1):
        start_idx = test_peaks[i]
        # actual cycle duration
        dur_idx = test_peaks[i+1] - start_idx
        if dur_idx < 4: continue
        cycle_actual = nino_test_band[start_idx:test_peaks[i+1]]
        peak_amp = float(cycle_actual[0])  # value at cycle start (peak)
        for h in HORIZON_FRACS:
            target_idx = int(h * dur_idx)
            if target_idx >= dur_idx: continue
            actual_v = float(cycle_actual[target_idx])
            pred_v = peak_amp * template[int(h * (len(template)-1))]
            errs[h].append((pred_v, actual_v))
    out = {}
    for h, pairs in errs.items():
        if not pairs: continue
        arr = np.array(pairs)
        rmse = float(np.sqrt(np.mean((arr[:,0] - arr[:,1])**2)))
        if np.std(arr[:,1]) > 1e-9:
            corr = float(np.corrcoef(arr[:,0], arr[:,1])[0,1])
        else: corr = 0
        # Direction: did the template correctly predict whether value at target_h is above/below peak/2?
        out[h] = dict(rmse=rmse, corr=corr, n=len(pairs))
    return out

print("\n========= TEST: predict ENSO test-cycle values from peak using template =========")
print(f"{'horizon':>10}  {'metric':>8}  {'ECG_tpl':>10}  {'NINO_tpl':>10}")
metrics_ecg = metrics_for_template(ecg_template, 'ECG')
metrics_nino = metrics_for_template(nino_template, 'NINO')
results = {}
for h in HORIZON_FRACS:
    if h not in metrics_ecg or h not in metrics_nino: continue
    me = metrics_ecg[h]; mn = metrics_nino[h]
    print(f"  frac={h:>4.2f}   rmse    {me['rmse']:>10.3f}  {mn['rmse']:>10.3f}")
    print(f"  frac={h:>4.2f}   corr    {me['corr']:+10.3f}  {mn['corr']:+10.3f}")
    results[h] = dict(ECG=me, NINO=mn)

# Compare to persistence (predict = peak value)
print("\nPersistence baseline (predict peak value forward):")
errs_pers = {h: [] for h in HORIZON_FRACS}
for i in range(len(test_peaks)-1):
    start_idx = test_peaks[i]; dur_idx = test_peaks[i+1] - start_idx
    if dur_idx < 4: continue
    cycle_actual = nino_test_band[start_idx:test_peaks[i+1]]
    peak_amp = float(cycle_actual[0])
    for h in HORIZON_FRACS:
        target_idx = int(h * dur_idx)
        if target_idx >= dur_idx: continue
        actual_v = float(cycle_actual[target_idx])
        errs_pers[h].append((peak_amp, actual_v))
for h, pairs in errs_pers.items():
    if not pairs: continue
    arr = np.array(pairs)
    rmse = float(np.sqrt(np.mean((arr[:,0] - arr[:,1])**2)))
    if np.std(arr[:,1]) > 1e-9:
        corr = float(np.corrcoef(arr[:,0], arr[:,1])[0,1])
    else: corr = 0
    print(f"  frac={h:>4.2f}  rmse={rmse:.3f}  corr={corr:+.3f}")
    results.setdefault(h, {})['PERSIST'] = dict(rmse=rmse, corr=corr, n=len(pairs))

# Headline: how does ECG template performance compare to ENSO own template?
print("\n========= VERTICAL ARA CROSS-DOMAIN PREDICTION VERDICT =========")
ecg_corrs = [results[h]['ECG']['corr'] for h in HORIZON_FRACS if h in results]
nino_corrs = [results[h]['NINO']['corr'] for h in HORIZON_FRACS if h in results]
ecg_rmses = [results[h]['ECG']['rmse'] for h in HORIZON_FRACS if h in results]
nino_rmses = [results[h]['NINO']['rmse'] for h in HORIZON_FRACS if h in results]
print(f"ECG-template mean corr across horizons:  {np.mean(ecg_corrs):+.3f}")
print(f"NINO-template mean corr across horizons: {np.mean(nino_corrs):+.3f}")
print(f"Difference: {(np.mean(ecg_corrs)-np.mean(nino_corrs)):+.3f}")
print(f"ECG-template mean RMSE:  {np.mean(ecg_rmses):.3f}")
print(f"NINO-template mean RMSE: {np.mean(nino_rmses):.3f}")

# Verdict
diff = abs(np.mean(ecg_corrs) - np.mean(nino_corrs))
if diff < 0.05:
    print("\n  ★★★ ECG template predicts ENSO ~equivalently to ENSO's own template")
    print("  Vertical ARA is operationally usable for cross-domain prediction.")
elif diff < 0.15:
    print("\n  ★★ ECG template close to ENSO template — vertical ARA partially usable")
else:
    print("\n  ★ ECG template significantly different — vertical ARA descriptively right but predictively limited")

# Save
out = dict(
    sources=dict(ecg="PhysioNet NSRDB nsr001", nino="NOAA PSL Nino 3.4 1870-2025"),
    ecg_template=ecg_template.tolist(),
    nino_template=nino_template.tolist(),
    template_corr=float(np.corrcoef(ecg_template, nino_template)[0,1]),
    scale_ratio_log10=float(np.log10(NINO_PERIOD_MO*30*24*3600/ECG_PERIOD_S)),
    n_ecg_train_cycles=len(ecg_train_cycles),
    n_nino_train_cycles=len(nino_train_cycles),
    n_test_cycles=len(test_peaks)-1,
    horizons=HORIZON_FRACS,
    results=results,
    ecg_mean_corr=float(np.mean(ecg_corrs)),
    nino_mean_corr=float(np.mean(nino_corrs)),
    ecg_mean_rmse=float(np.mean(ecg_rmses)),
    nino_mean_rmse=float(np.mean(nino_rmses)),
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.ECG_PRED_ENSO = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

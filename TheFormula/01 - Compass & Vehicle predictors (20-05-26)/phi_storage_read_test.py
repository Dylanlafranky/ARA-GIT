"""
φ-storage reading test (Dylan 2026-05-03):

Test: can we reconstruct a system's signal from MULTI-RUNG PHASES ALONE
using framework's φ-power amplitude scaling? If yes, the topology IS the data.

Method:
  1. Take ENSO signal
  2. At multiple φ-rungs, compute Hilbert phase at every time step
  3. Reconstruct signal as sum of cos(phase_k) weighted by φ-power amplitudes
  4. Compare reconstruction to actual signal
  5. Try to PROJECT FORWARD by extrapolating phase advance (constant rate per rung)

Variants:
  V1: Use measured phases (full signal needed for Hilbert) — tests reconstruction quality
  V2: Use only first half to learn amplitude weights, project forward by phase advance — tests forward prediction

DATA: real NOAA Niño 3.4 monthly anomaly.
"""
import json, os
import numpy as np, pandas as pd
from scipy.signal import hilbert

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\phi_storage_read_data.js")

df_n = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
df_n['date'] = pd.to_datetime(df_n['date'].str.strip())
df_n = df_n[df_n['val'] > -90].copy()
v_nino = df_n['val'].values.astype(float)
nino_dates = df_n['date'].values
N = len(v_nino)
print(f"ENSO: {N} months ({(N/12):.0f} years)")

def bandpass(arr, period_units, dt=1.0, bw=0.4):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_units
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

# Use rungs from φ³ (~4mo) to φ¹⁰ (~123mo) — covers ENSO's relevant scales
RUNGS = [(k, PHI**k) for k in range(3, 11)]
print(f"Rungs (months): {[(k, round(p,1)) for k,p in RUNGS]}")

# === V1: Reconstruct from measured phases at each rung ===
# At each rung, get bandpass + Hilbert phase + amplitude
rung_data = {}
for k, period in RUNGS:
    bp = bandpass(v_nino, period)
    analytic = hilbert(bp)
    rung_data[k] = dict(
        bp=bp,
        amp_envelope=np.abs(analytic),
        phase=np.angle(analytic),
        period=period,
    )

# φ-power amplitude scaling: heuristic that amplitude ~ φ^k * base
# For ENSO, find best fit of base amplitude per rung from training half
SPLIT = N // 2
train_amps = {k: float(np.std(rung_data[k]['bp'][:SPLIT])) for k,_ in RUNGS}
print(f"\nTraining amplitude per rung (std of bandpass):")
for k,_ in RUNGS:
    print(f"  k={k:>2} (T={PHI**k:>5.1f}mo): amp = {train_amps[k]:.3f}")

# === V1A: Reconstruction using actual amplitudes per rung at each time ===
# This is essentially Hilbert reconstruction = sum of (envelope * cos(phase)) per rung
recon_v1a_full = np.zeros(N)
for k, _ in RUNGS:
    recon_v1a_full += rung_data[k]['amp_envelope'] * np.cos(rung_data[k]['phase'])
recon_v1a_full += np.mean(v_nino)

# === V1B: Reconstruction using FIXED amplitude per rung (training-period std) ===
# This is the φ-storage test — assume amplitude is constant at train value, just track phase
recon_v1b_full = np.zeros(N)
for k, _ in RUNGS:
    recon_v1b_full += train_amps[k] * np.cos(rung_data[k]['phase'])
recon_v1b_full += np.mean(v_nino[:SPLIT])

# === V2: Forward projection — use only training-half phases, project test half ===
# Find phase ADVANCE RATE per rung from training (should be 2π / period in samples)
# Then project: phase_test(t) = phase_train_end + advance_rate * (t - SPLIT)

# Fit phase advance from training
def unwrap(phase): return np.unwrap(phase)
recon_v2 = np.zeros(N)
for k, _ in RUNGS:
    train_phase = unwrap(rung_data[k]['phase'][:SPLIT])
    # Fit linear phase advance
    if len(train_phase) > 10:
        slope = float((train_phase[-1] - train_phase[0]) / (SPLIT - 1))
    else:
        slope = 2 * np.pi / rung_data[k]['period']
    # Build projected phase: training half from data, test half from extrapolation
    proj_phase = np.zeros(N)
    proj_phase[:SPLIT] = train_phase
    for t in range(SPLIT, N):
        proj_phase[t] = train_phase[-1] + slope * (t - SPLIT + 1)
    # Reconstruct
    recon_v2 += train_amps[k] * np.cos(proj_phase)
recon_v2 += np.mean(v_nino[:SPLIT])

# === Metrics ===
def metrics(true, pred, label):
    mask = np.isfinite(pred) & np.isfinite(true)
    a, b = true[mask], pred[mask]
    if len(a) < 5 or np.std(a)<1e-9 or np.std(b)<1e-9:
        return dict(corr=0, rmse=0, n=0)
    return dict(
        corr=float(np.corrcoef(a, b)[0,1]),
        rmse=float(np.sqrt(np.mean((a-b)**2))),
        n=len(a),
    )

print(f"\n========= φ-STORAGE RECONSTRUCTION RESULTS =========")
print(f"\n{'Method':<55} {'corr':>7} {'rmse':>7}")

# Full series metrics
m_v1a_full = metrics(v_nino, recon_v1a_full, 'V1A')
m_v1b_full = metrics(v_nino, recon_v1b_full, 'V1B')
print(f"V1A — full Hilbert reconstruction (envelope per t)        {m_v1a_full['corr']:+.3f} {m_v1a_full['rmse']:.3f}")
print(f"V1B — fixed amplitude per rung (train std), measured phase {m_v1b_full['corr']:+.3f} {m_v1b_full['rmse']:.3f}")

# Test-half-only metrics for V2 (forward projection)
m_v2_test = metrics(v_nino[SPLIT:], recon_v2[SPLIT:], 'V2 test')
m_v2_train = metrics(v_nino[:SPLIT], recon_v2[:SPLIT], 'V2 train')
print(f"\nV2 — projection using ONLY training-half phase + linear advance:")
print(f"  Train half:  {m_v2_train['corr']:+.3f} {m_v2_train['rmse']:.3f}")
print(f"  Test half:   {m_v2_test['corr']:+.3f} {m_v2_test['rmse']:.3f}")

# Per-horizon decay of V2
print(f"\nV2 forward-projection correlation decay across test horizons:")
test_n = N - SPLIT
horizons_mo = [12, 24, 36, 48, 60, 96, 120, 180, 240, 480]
print(f"  {'horizon':>10} {'corr':>8}")
horizon_corrs = {}
for h in horizons_mo:
    end = min(SPLIT + h, N)
    n_use = end - SPLIT
    if n_use < 5: continue
    a = v_nino[SPLIT:end]
    b = recon_v2[SPLIT:end]
    if np.std(a) > 1e-9 and np.std(b) > 1e-9:
        c = float(np.corrcoef(a, b)[0,1])
    else: c = 0
    horizon_corrs[h] = c
    print(f"  {h:>5} mo   {c:+.3f}")

# === Direction prediction test ===
print(f"\n========= DIRECTION PREDICTION FROM V2 =========")
def dir_acc(true, pred, h):
    correct = 0; total = 0
    for t in range(len(true) - h):
        actual_dir = 1 if true[t+h] > true[t] else (-1 if true[t+h] < true[t] else 0)
        pred_dir = 1 if pred[t+h] > pred[t] else (-1 if pred[t+h] < pred[t] else 0)
        if actual_dir == 0 or pred_dir == 0: continue
        correct += (actual_dir == pred_dir); total += 1
    return correct/total if total else 0

dir_horizons = [1, 3, 6, 12, 24, 48]
print(f"  {'horizon':>10} {'V2 dir acc':>12}")
dir_results = {}
for h in dir_horizons:
    a = dir_acc(v_nino[SPLIT:], recon_v2[SPLIT:], h)
    dir_results[h] = a
    print(f"  {h:>5} mo   {a*100:>10.1f}%")

# Save data for visualization
out = dict(
    sources=dict(nino="NOAA PSL Nino 3.4 1870-2025"),
    rungs=[[k, p] for k,p in RUNGS],
    train_amps={str(k): v for k,v in train_amps.items()},
    n=int(N), split=int(SPLIT),
    actual=v_nino.tolist(),
    recon_v1a_envelope=recon_v1a_full.tolist(),
    recon_v1b_fixed_amp=recon_v1b_full.tolist(),
    recon_v2_projected=recon_v2.tolist(),
    dates=[str(pd.Timestamp(d).date()) for d in nino_dates],
    metrics=dict(
        v1a_envelope=m_v1a_full,
        v1b_fixed_amp=m_v1b_full,
        v2_train=m_v2_train,
        v2_test=m_v2_test,
    ),
    horizon_corrs=horizon_corrs,
    direction_accuracy=dir_results,
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.PHI_STORAGE = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

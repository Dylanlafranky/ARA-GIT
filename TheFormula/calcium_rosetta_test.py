"""
Cross-domain Rosetta Stone test (Dylan 2026-05-02):

Take a single mouse visual cortex calcium trace (~ms-second timescale)
from DANDI 000049 (Allen Institute Visual Coding) and run the framework
decomposition on it. Compare its rung-power distribution to ENSO's
(months-years timescale) — over 10^7-10^8× scale gap.

Test of vertical ARA: does the same rung structure appear?

DATA SOURCE (real, verifiable):
  DANDI Archive 000049 — "Allen Institute - TF x SF tuning in mouse visual
  cortex with calcium imaging" — de Vries et al.
  Asset: 82fd3c31-37b7-4261-a6ab-0979bc78877c
  Subject: sub-760940732, session: ses-798500537
  https://dandiarchive.org/dandiset/000049/draft
"""
import json, os, h5py
import numpy as np
from scipy.signal import hilbert

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

NWB_PATH = _resolve(r"F:\SystemFormulaFolder\Calcium_DANDI\calcium_imaging.nwb")
OUT      = _resolve(r"F:\SystemFormulaFolder\TheFormula\calcium_rosetta_data.js")

# Extract calcium ΔF/F₀ trace for one cell
print("Loading calcium imaging data...")
with h5py.File(NWB_PATH, 'r') as f:
    dff = f['processing/brain_observatory_pipeline/Fluorescence/DfOverF/data'][:]
    ts  = f['processing/brain_observatory_pipeline/Fluorescence/DfOverF/timestamps'][:]
print(f"DFoverF shape: {dff.shape}, n_cells: {dff.shape[1]}")
print(f"Timestamps: {ts[0]:.2f}s to {ts[-1]:.2f}s, total {ts[-1]-ts[0]:.1f}s")
dt = float(np.mean(np.diff(ts)))
sample_rate = 1.0/dt
print(f"Sample rate: {sample_rate:.2f} Hz, dt = {dt*1000:.2f} ms")

# Pick the cell with highest variance (most active)
variances = np.var(dff, axis=0)
best_cell = int(np.argmax(variances))
print(f"Picking cell {best_cell} (variance {variances[best_cell]:.3f})")
ca = dff[:, best_cell]
print(f"Calcium signal: mean={ca.mean():.3f}, std={ca.std():.3f}, min={ca.min():.3f}, max={ca.max():.3f}")

# Establish φ-rungs in the calcium signal's natural time units (seconds)
# Most natural cellular timescale: 100ms-10s
# Pump rung for cellular Ca²⁺ might be around 0.5-2s (typical Ca transient)
# φ⁰ = 1s, φ¹ = 1.6s, φ² = 2.6s, φ³ = 4.2s, φ⁴ = 6.9s, φ⁵ = 11s, ...
# Sample rate ~30Hz means we can resolve down to ~0.1s

# Decompose into rungs spanning sub-second to ~minute
RUNGS = [(k, PHI**k) for k in range(-2, 10)]  # 0.38s to 123s
print(f"\nFramework rungs (seconds): {[(k, round(PHI**k,2)) for k,_ in RUNGS]}")

def rung_band(arr, period_seconds, dt, bw=0.2):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_seconds
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

# Total variance and per-rung variance
total_var = float(np.var(ca - np.mean(ca)))
print(f"\nCalcium signal total variance: {total_var:.4f}")
print(f"\n========= Calcium signal — variance per φ-rung =========")
print(f"{'rung k':>8}  {'period (s)':>12}  {'frac of variance':>18}")

rung_powers = {}
for k, period in RUNGS:
    if period > (ts[-1]-ts[0])/3:
        # too long for our trace
        continue
    band = rung_band(ca, period, dt)
    var = float(np.var(band))
    frac = var/total_var
    rung_powers[k] = dict(period_s=period, var=var, frac=frac)
    bar = '█' * int(frac*50)
    print(f"  k={k:>5}  {period:>12.2f}  {frac*100:>15.1f}%  {bar}")

# Find the dominant rung
if rung_powers:
    dominant_k = max(rung_powers, key=lambda k: rung_powers[k]['frac'])
    print(f"\nDominant calcium rung: k={dominant_k} (period {rung_powers[dominant_k]['period_s']:.2f}s, {rung_powers[dominant_k]['frac']*100:.1f}% of variance)")

# Also check if the φ⁻¹ pump rung shows up — this is the typical Ca transient rate
# For Ca²⁺: pump frequency is often around 0.5-2 Hz (period 0.5-2s)

# === Compare to other systems' rung distributions ===
# Standard cross-domain comparison: which rung holds most variance for each system?
print("\n========= CROSS-DOMAIN VERTICAL ARA COMPARISON =========")
print("System dominant-rung concentrations across vastly different scales:")
print(f"{'system':>20}  {'physical scale':>16}  {'dominant rung':>15}  {'concentration':>14}")
print(f"  {'Calcium (cell)':>18}  {dt:>14.3f}s {'sample-step':>2}  φ^{dominant_k:<3}({rung_powers[dominant_k]['period_s']:.1f}s){'':>3}  {rung_powers[dominant_k]['frac']*100:>11.1f}%")
print(f"  {'QBO (atmosphere)':>18}  {'months':>16}  φ^7  (29 mo)        69.0%")
print(f"  {'Solar Schwabe':>18}  {'years':>16}  φ^10 (10.3 yr)      70.8%")
print(f"  {'ENSO':>18}  {'years':>16}  φ^7-φ^9 distributed     —")

# === Also try widening band and re-checking ===
print("\n========= With wider bandwidth (±40%) to capture nearby rungs =========")
for k, period in RUNGS:
    if period > (ts[-1]-ts[0])/3: continue
    band = rung_band(ca, period, dt, bw=0.4)
    var = float(np.var(band))
    frac = var/total_var
    bar = '█' * int(frac*50)
    print(f"  k={k:>5}  {period:>12.2f}s  {frac*100:>5.1f}%  {bar}")

# === Compute calcium signal's ARA shape: rolling ARA per window ===
# Actually compute REAL ARA (T_acc / T_rel approximation) on the raw signal
# in sliding windows matched to each rung's period
print("\n========= Real ARA per rung (sliding window) =========")
def rolling_ara(arr, win_samples):
    """Compute ARA = mean rise-time / mean fall-time over rolling window."""
    n = len(arr)
    ara_vals = []
    for i in range(win_samples, n - win_samples, win_samples//2):
        seg = arr[i-win_samples:i+win_samples]
        # Find peak-to-trough timings
        diffs = np.diff(seg)
        rising = np.sum(diffs > 0)
        falling = np.sum(diffs < 0)
        if falling > 0:
            ara_vals.append(rising / falling)
    if len(ara_vals) == 0: return np.nan, np.nan
    return float(np.mean(ara_vals)), float(np.std(ara_vals))

print(f"{'rung':>8}  {'period (s)':>12}  {'win_samples':>12}  {'ARA_mean':>10}  {'ARA_std':>9}")
ara_per_rung = {}
for k, period in RUNGS:
    win_samples = max(4, int(period/dt))
    if win_samples * 4 >= len(ca): continue
    a_mean, a_std = rolling_ara(ca, win_samples)
    ara_per_rung[k] = dict(period_s=period, win_samples=win_samples, ara_mean=a_mean, ara_std=a_std)
    print(f"  k={k:>5}  {period:>12.2f}  {win_samples:>12d}  {a_mean:>10.3f}  {a_std:>9.3f}")

# Save
out = dict(
    source=dict(
        archive="DANDI",
        dandiset="000049",
        asset="82fd3c31-37b7-4261-a6ab-0979bc78877c",
        title="Allen Institute - TF x SF tuning in mouse visual cortex with calcium imaging",
        subject="sub-760940732", session="ses-798500537",
        cell_index=best_cell,
    ),
    sample_rate_hz=sample_rate,
    dt_s=dt,
    duration_s=float(ts[-1]-ts[0]),
    total_variance=total_var,
    rung_powers=rung_powers,
    ara_per_rung=ara_per_rung,
    dominant_rung_k=dominant_k,
    dominant_rung_period_s=rung_powers[dominant_k]['period_s'],
    dominant_rung_frac=rung_powers[dominant_k]['frac'],
)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write("window.CALCIUM = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

"""
Engine-class hypothesis test (Dylan 2026-05-03):

Heart Mayer wave is clock-class (ARA ~1.18). ENSO is engine-class.
Their +0.37 cross-domain shape correlation might be cross-CLASS leak.

Test: extract additional human rhythms that should be ENGINE class:
  - Breathing (~5s, asymmetric inhale/exhale, engine)
  - Sleep cycle (~90min, asymmetric REM/NREM cycling, engine)
Both extracted from the same 22h PhysioNet RR data.

If engine-class structure is real, same-class pairs should correlate HIGHER:
  - Breathing vs ENSO    (engine vs engine) — expect higher
  - Sleep cycle vs ENSO  (engine vs engine) — expect higher
  - Breathing vs Sleep   (engine vs engine) — expect higher
  - Heart Mayer vs ENSO  (clock vs engine)  — already +0.37, baseline

DATA: real PhysioNet (nsr001) + real NOAA Niño 3.4.
"""
import json, os
import numpy as np, pandas as pd
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

ECG_PATH  = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\engine_class_data.js")

# Load
ecg = pd.read_csv(ECG_PATH)
t_ecg = ecg['time_s'].values.astype(float); v_ecg_orig = ecg['rr_ms'].values.astype(float)
GRID_DT = 0.5
t_grid = np.arange(t_ecg[0], t_ecg[-1], GRID_DT)
v_ecg = np.interp(t_grid, t_ecg, v_ecg_orig)
print(f"ECG/RR data: {len(v_ecg)} samples at {GRID_DT}s grid, {t_ecg[-1]/3600:.1f}h total")

df_n = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
df_n['date'] = pd.to_datetime(df_n['date'].str.strip())
df_n = df_n[df_n['val'] > -90].copy()
v_nino = df_n['val'].values.astype(float)

def bandpass(arr, period_units, dt=1.0, bw=0.5):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_units
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

def extract_raw_cycles(raw_signal, target_period_units, dt, smooth_factor=0.15):
    """Find peaks at target period scale; extract RAW segments between peaks."""
    smooth_sigma = max(1, int(target_period_units * smooth_factor / dt))
    smoothed = gaussian_filter1d(raw_signal - np.mean(raw_signal), smooth_sigma)
    min_dist = int(target_period_units * 0.7 / dt)
    peaks, _ = find_peaks(smoothed, distance=min_dist)
    cycles = []
    for i in range(len(peaks)-1):
        seg = raw_signal[peaks[i]:peaks[i+1]]
        target_n = int(target_period_units / dt)
        if len(seg) < target_n*0.5 or len(seg) > target_n*2.5: continue
        cycles.append(seg)
    return cycles

N_PTS = 100
def normalize(seg):
    x_o = np.linspace(0, 1, len(seg))
    x_n = np.linspace(0, 1, N_PTS)
    s = np.interp(x_n, x_o, seg)
    s_n = s - s.min()
    if s_n.max() > 0: s_n /= s_n.max()
    return 2*s_n - 1

# === Extract cycles at four relevant scales ===
# 1. Breathing cycle (~5s = φ³.34 ≈ 4.24s = φ³ approx)
BREATH_PERIOD_S = PHI**3  # ~4.24s
breath_band = bandpass(v_ecg, BREATH_PERIOD_S, GRID_DT, bw=0.5)
breath_cycles_raw = extract_raw_cycles(v_ecg, BREATH_PERIOD_S, GRID_DT)
breath_cycles = [normalize(c) for c in breath_cycles_raw]
print(f"Breathing cycles (φ^3 ≈ 4.24s, RSA scale): {len(breath_cycles)}")

# 2. Heart Mayer wave (~11s = φ^5)
MAYER_PERIOD_S = PHI**5  # ~11s
mayer_cycles_raw = extract_raw_cycles(v_ecg, MAYER_PERIOD_S, GRID_DT)
mayer_cycles = [normalize(c) for c in mayer_cycles_raw]
print(f"Heart Mayer cycles (φ^5 ≈ 11s): {len(mayer_cycles)}")

# 3. Sleep cycle (~90 min = 5400s = φ^17.7)
# Use exact φ^17 ≈ 4181s ≈ 70 min, or φ^18 ≈ 6765s ≈ 113 min — both close to sleep cycle
# Sleep cycle is officially 90-110 min. Use φ^18 (113 min)
SLEEP_PERIOD_S = PHI**18  # ~6765s ≈ 113 min, close to one sleep cycle
# 22 hour recording = 79200s. Number of sleep cycles ≈ 79200/6765 ≈ 12
# Use a wider bandwidth since we have few cycles to sample
sleep_cycles_raw = extract_raw_cycles(v_ecg, SLEEP_PERIOD_S, GRID_DT, smooth_factor=0.2)
sleep_cycles = [normalize(c) for c in sleep_cycles_raw]
print(f"Sleep cycles (φ^18 ≈ 113min): {len(sleep_cycles)}")

# 4. ENSO cycles (~47mo = φ^8)
NINO_PERIOD_MO = PHI**8
nino_cycles_raw = extract_raw_cycles(v_nino, NINO_PERIOD_MO, dt=1.0)
nino_cycles = [normalize(c) for c in nino_cycles_raw]
print(f"ENSO cycles (φ^8 ≈ 47mo): {len(nino_cycles)}")

# Synthetic templates
def engine_template(n_pts=N_PTS, ARA=PHI):
    t = np.linspace(0, 1, n_pts)
    cross = ARA / (1 + ARA)
    out = np.zeros(n_pts)
    for i, p in enumerate(t):
        if p < cross:
            f = p/cross
            out[i] = 1.0 - f**(1.0/max(ARA,0.1))
        else:
            f = (p - cross)/(1.0 - cross)
            out[i] = -1.0 + f**max(ARA,0.1)
    s_n = out - out.min()
    if s_n.max() > 0: s_n /= s_n.max()
    return 2*s_n - 1

synth_engine = engine_template(ARA=PHI)
synth_clock  = -np.cos(np.linspace(0, 2*np.pi, N_PTS))

# === ARA estimates from mean cycles ===
def cycle_ARA(cycles_norm):
    """Estimate ARA from mean cycle: rise_time / fall_time."""
    if not cycles_norm: return None
    mean_cyc = np.array(cycles_norm).mean(axis=0)
    peak_idx = int(np.argmax(mean_cyc))
    trough_idx = int(np.argmin(mean_cyc))
    if trough_idx > peak_idx:
        rise = trough_idx - peak_idx
        fall = N_PTS - trough_idx + peak_idx
    else:
        rise = N_PTS - peak_idx + trough_idx
        fall = peak_idx - trough_idx
    return rise / max(fall, 1)

print(f"\n========= ARA CLASSIFICATION OF EACH SOURCE =========")
print(f"  Breathing (~5s):   ARA = {cycle_ARA(breath_cycles):.3f}  (predicted: engine ~φ)")
print(f"  Heart Mayer (~11s): ARA = {cycle_ARA(mayer_cycles):.3f}  (clock-like found yesterday)")
print(f"  Sleep (~113min):   ARA = {cycle_ARA(sleep_cycles):.3f}  (predicted: engine ~φ)")
print(f"  ENSO (~47mo):      ARA = {cycle_ARA(nino_cycles):.3f}  (engine class)")

# Pair correlations
def pair_corrs(cycles_a, cycles_b, n_pairs=200, seed=0):
    rng = np.random.RandomState(seed)
    a_idx = rng.choice(len(cycles_a), min(n_pairs, len(cycles_a)*3), replace=True)
    b_idx = rng.choice(len(cycles_b), min(n_pairs, len(cycles_b)*3), replace=True)
    corrs = []
    for ai, bi in zip(a_idx, b_idx):
        a = np.array(cycles_a[ai]); b = np.array(cycles_b[bi])
        if np.std(a)>1e-9 and np.std(b)>1e-9:
            corrs.append(float(np.corrcoef(a, b)[0,1]))
    return corrs

# Mean-shape pair: take grand-mean of each source, correlate
def mean_shape_corr(cycles_a, cycles_b):
    if not cycles_a or not cycles_b: return None
    ma = np.array(cycles_a).mean(axis=0)
    mb = np.array(cycles_b).mean(axis=0)
    if np.std(ma)<1e-9 or np.std(mb)<1e-9: return 0
    return float(np.corrcoef(ma, mb)[0,1])

print(f"\n========= MEAN-SHAPE CROSS-DOMAIN CORRELATIONS =========")
combos = [
    ('breath', breath_cycles, 'ENSO', nino_cycles, 'engine vs engine — expect HIGH'),
    ('sleep', sleep_cycles, 'ENSO', nino_cycles, 'engine vs engine — expect HIGH'),
    ('breath', breath_cycles, 'sleep', sleep_cycles, 'engine vs engine (both human)'),
    ('Mayer', mayer_cycles, 'ENSO', nino_cycles, 'clock vs engine — baseline (yesterday: cross-class)'),
    ('breath', breath_cycles, 'Mayer', mayer_cycles, 'engine vs clock'),
    ('sleep', sleep_cycles, 'Mayer', mayer_cycles, 'engine vs clock'),
    # Synthetic class membership
    ('breath', breath_cycles, 'synth_engine', None, ''),
    ('sleep', sleep_cycles, 'synth_engine', None, ''),
    ('Mayer', mayer_cycles, 'synth_engine', None, ''),
    ('ENSO', nino_cycles, 'synth_engine', None, ''),
    ('breath', breath_cycles, 'synth_clock', None, ''),
    ('sleep', sleep_cycles, 'synth_clock', None, ''),
    ('Mayer', mayer_cycles, 'synth_clock', None, ''),
    ('ENSO', nino_cycles, 'synth_clock', None, ''),
]

results = {}
print(f"{'pair':<35}  {'mean shape r':>14}  {'pair median r':>14}  {'note':<35}")
for name_a, cyc_a, name_b, cyc_b, note in combos:
    if name_b == 'synth_engine':
        ms = float(np.corrcoef(np.array(cyc_a).mean(axis=0), synth_engine)[0,1]) if cyc_a else None
        pm = None
    elif name_b == 'synth_clock':
        ms = float(np.corrcoef(np.array(cyc_a).mean(axis=0), synth_clock)[0,1]) if cyc_a else None
        pm = None
    else:
        ms = mean_shape_corr(cyc_a, cyc_b)
        pc = pair_corrs(cyc_a, cyc_b)
        pm = float(np.median(pc)) if pc else None
    pair_label = f"{name_a:>6} vs {name_b:<10}"
    print(f"  {pair_label:<35}  {ms:+14.3f}  {(pm if pm is not None else 0):+14.3f}  {note:<35}")
    results[f"{name_a}_vs_{name_b}"] = dict(mean_shape=ms, pair_median=pm, note=note)

# Save mean cycle of each source for visualization
mean_cycles = {
    'breathing': np.array(breath_cycles).mean(axis=0).tolist() if breath_cycles else None,
    'mayer':     np.array(mayer_cycles).mean(axis=0).tolist() if mayer_cycles else None,
    'sleep':     np.array(sleep_cycles).mean(axis=0).tolist() if sleep_cycles else None,
    'nino':      np.array(nino_cycles).mean(axis=0).tolist() if nino_cycles else None,
    'synth_engine': synth_engine.tolist(),
    'synth_clock':  synth_clock.tolist(),
}

aras = {
    'breathing': cycle_ARA(breath_cycles),
    'mayer': cycle_ARA(mayer_cycles),
    'sleep': cycle_ARA(sleep_cycles),
    'nino': cycle_ARA(nino_cycles),
}

n_cycles = {
    'breathing': len(breath_cycles),
    'mayer': len(mayer_cycles),
    'sleep': len(sleep_cycles),
    'nino': len(nino_cycles),
}

out = dict(
    sources=dict(ecg="PhysioNet NSRDB nsr001 (22h)", nino="NOAA PSL Nino 3.4"),
    period_seconds=dict(breathing=BREATH_PERIOD_S, mayer=MAYER_PERIOD_S, sleep=SLEEP_PERIOD_S, nino_months=NINO_PERIOD_MO),
    n_cycles=n_cycles,
    aras=aras,
    mean_cycles=mean_cycles,
    results=results,
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.ENGINE_CLASS = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

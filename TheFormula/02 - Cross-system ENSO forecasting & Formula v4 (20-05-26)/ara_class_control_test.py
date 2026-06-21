"""
Critical methodology control test (Dylan 2026-05-03):

Question: is the +0.999 cross-domain correlation we found (heart vs ENSO engine
cycles) meaningful, or is it a bandpass artifact that would happen between any
two oscillatory signals regardless of ARA class?

Test design — pair heart engine cycles against:
  (A) ENSO engine cycles (SAME ARA class) — expect HIGH correlation
  (B) Calcium clock cycles from DANDI (ARA = 1.0, conservative)
  (C) Synthetic SNAP signal (ARA ≈ 2.0, sharp asymmetric)
  (D) Pure sinusoid (perfect ARA = 1.0)
  (E) Bandpass-filtered Gaussian noise (truly random)

If (A) >> (B), (C), (D), (E), the framework distinguishes ARA classes meaningfully.
If everything is ~the same, we have a bandpass artifact problem.

DATA: real PhysioNet (nsr001) + real NOAA Niño 3.4 + real DANDI calcium imaging.
"""
import json, os, h5py
import numpy as np, pandas as pd
from scipy.signal import find_peaks

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

ECG_PATH  = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
NWB_PATH  = _resolve(r"F:\SystemFormulaFolder\Calcium_DANDI\calcium_imaging.nwb")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\ara_class_control_data.js")

# ===== HEART (engine) =====
ecg = pd.read_csv(ECG_PATH)
t_ecg = ecg['time_s'].values.astype(float); v_ecg = ecg['rr_ms'].values.astype(float)
GRID_DT = 0.5
t_grid = np.arange(t_ecg[0], t_ecg[-1], GRID_DT)
v_ecg = np.interp(t_grid, t_ecg, v_ecg)

# ===== ENSO (engine) =====
df_n = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
df_n['date'] = pd.to_datetime(df_n['date'].str.strip())
df_n = df_n[df_n['val'] > -90].copy()
v_nino = df_n['val'].values.astype(float)

# ===== CALCIUM (clock, ARA=1) =====
with h5py.File(NWB_PATH, 'r') as f:
    dff = f['processing/brain_observatory_pipeline/Fluorescence/DfOverF/data'][:]
    ts_ca = f['processing/brain_observatory_pipeline/Fluorescence/DfOverF/timestamps'][:]
ca = dff[:, int(np.argmax(np.var(dff, axis=0)))]
ca_dt = float(np.mean(np.diff(ts_ca)))

# Bandpass helper
def bandpass(arr, period_units, dt=1.0, bw=0.4):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_units
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

# Cycle extractor
def extract_cycles(band, min_cycle_samples):
    peaks, _ = find_peaks(band, distance=int(min_cycle_samples*0.7))
    cycles = []
    for i in range(len(peaks)-1):
        seg = band[peaks[i]:peaks[i+1]]
        if len(seg) < min_cycle_samples*0.5: continue
        if len(seg) > min_cycle_samples*2.5: continue
        cycles.append(seg)
    return cycles

N_PTS = 100
def normalize(seg):
    x_o = np.linspace(0, 1, len(seg))
    x_n = np.linspace(0, 1, N_PTS)
    s = np.interp(x_n, x_o, seg)
    s_n = s - s.min()
    if s_n.max() > 0: s_n = s_n/s_n.max()
    return 2*s_n - 1

# Bandpass each system at its dominant rung
heart_band = bandpass(v_ecg, PHI**5, GRID_DT, bw=0.4)
heart_cycles_raw = extract_cycles(heart_band, int(PHI**5/GRID_DT))
heart_cycles = [normalize(c) for c in heart_cycles_raw]
print(f"Heart engine cycles (φ^5 ≈ 11s): {len(heart_cycles)}")

nino_band = bandpass(v_nino, PHI**8, dt=1.0, bw=0.5)
nino_cycles_raw = extract_cycles(nino_band, int(PHI**8))
nino_cycles = [normalize(c) for c in nino_cycles_raw]
print(f"ENSO engine cycles (φ^8 ≈ 47mo): {len(nino_cycles)}")

# Calcium at φ^3 (~4s) — but calcium ARA we measured was 1.0 (clock)
ca_band = bandpass(ca, PHI**3, ca_dt, bw=0.4)
ca_cycles_raw = extract_cycles(ca_band, int(PHI**3/ca_dt))
ca_cycles = [normalize(c) for c in ca_cycles_raw]
print(f"Calcium clock cycles (φ^3 ≈ 4s): {len(ca_cycles)}")

# Synthetic ENGINE template (ARA ≈ φ ≈ 1.62)
def engine_template(n_pts=N_PTS, ARA=PHI):
    """Asymmetric engine cycle: peak at fraction 0, trough at fraction φ/(1+φ) ≈ 0.618."""
    t = np.linspace(0, 1, n_pts)
    cross = ARA / (1 + ARA)  # trough position
    out = np.zeros(n_pts)
    for i, p in enumerate(t):
        if p < cross:
            f = p/cross
            out[i] = 1.0 - f**(1.0/max(ARA,0.1))  # descend from peak to trough
        else:
            f = (p - cross)/(1.0 - cross)
            out[i] = -1.0 + f**max(ARA,0.1)  # ascend from trough back to peak
    s_n = out - out.min()
    if s_n.max() > 0: s_n = s_n/s_n.max()
    return 2*s_n - 1
synth_engine = engine_template()

# Synthetic SNAP template (ARA ≈ 2.0)
synth_snap = engine_template(ARA=2.5)

# Synthetic CLOCK template (pure cosine — ARA = 1.0)
synth_clock = -np.cos(np.linspace(0, 2*np.pi, N_PTS))  # peak at 0 and 1, trough at 0.5

# Random noise (control)
np.random.seed(42)
def random_bandpass_cycle(period=PHI**5, dt=GRID_DT, n=10000):
    noise = np.random.randn(n)
    band = bandpass(noise, period, dt, bw=0.4)
    cyc = extract_cycles(band, int(period/dt))
    if not cyc: return None
    return normalize(cyc[len(cyc)//2])
noise_cycles = []
for s in range(50):
    np.random.seed(s)
    nc = random_bandpass_cycle()
    if nc is not None: noise_cycles.append(nc)
print(f"Bandpass-filtered noise cycles: {len(noise_cycles)}")

# Now compute pair correlations
def pair_corrs(cycles_a, cycles_b, n_pairs=200):
    """Random pair correlations between two cycle sets."""
    np.random.seed(0)
    corrs = []
    a_idx = np.random.choice(len(cycles_a), min(n_pairs, len(cycles_a)*3), replace=True)
    b_idx = np.random.choice(len(cycles_b), min(n_pairs, len(cycles_b)*3), replace=True)
    for ai, bi in zip(a_idx, b_idx):
        a = np.array(cycles_a[ai]); b = np.array(cycles_b[bi])
        if np.std(a)>1e-9 and np.std(b)>1e-9:
            corrs.append(float(np.corrcoef(a, b)[0,1]))
    return corrs

# 1. Heart engine vs ENSO engine (SAME CLASS) — expect high
corrs_HE_NE = pair_corrs(heart_cycles, nino_cycles)
# 2. Heart engine vs Calcium clock (DIFFERENT CLASS)
corrs_HE_CA = pair_corrs(heart_cycles, ca_cycles)
# 3. Heart engine vs synthetic engine template (SAME CLASS, ideal)
corrs_HE_synthE = [float(np.corrcoef(np.array(h), synth_engine)[0,1]) for h in heart_cycles]
# 4. Heart engine vs synthetic SNAP template
corrs_HE_synthS = [float(np.corrcoef(np.array(h), synth_snap)[0,1]) for h in heart_cycles]
# 5. Heart engine vs synthetic CLOCK
corrs_HE_synthC = [float(np.corrcoef(np.array(h), synth_clock)[0,1]) for h in heart_cycles]
# 6. Heart engine vs noise bandpass
corrs_HE_NOISE = pair_corrs(heart_cycles, noise_cycles)
# 7. ENSO engine vs synthetic ENGINE template
corrs_NE_synthE = [float(np.corrcoef(np.array(n), synth_engine)[0,1]) for n in nino_cycles]
# 8. ENSO engine vs synthetic CLOCK
corrs_NE_synthC = [float(np.corrcoef(np.array(n), synth_clock)[0,1]) for n in nino_cycles]
# 9. ENSO engine vs synthetic SNAP
corrs_NE_synthS = [float(np.corrcoef(np.array(n), synth_snap)[0,1]) for n in nino_cycles]
# 10. Heart engine vs Heart engine (within-domain control)
corrs_HE_HE = pair_corrs(heart_cycles, heart_cycles)
# 11. Calcium clock vs Calcium clock (within-domain control)
corrs_CA_CA = pair_corrs(ca_cycles, ca_cycles)

def stats(c):
    if not c: return dict(n=0, mean=None, median=None, std=None)
    a = np.array(c)
    return dict(n=len(c), mean=float(np.mean(a)), median=float(np.median(a)),
                std=float(np.std(a)), q25=float(np.percentile(a, 25)), q75=float(np.percentile(a, 75)))

results = {
    'A_heart_engine_vs_ENSO_engine': stats(corrs_HE_NE),
    'B_heart_engine_vs_calcium_clock': stats(corrs_HE_CA),
    'C_heart_engine_vs_noise_bandpass': stats(corrs_HE_NOISE),
    'D_heart_engine_vs_synthetic_engine_template': stats(corrs_HE_synthE),
    'E_heart_engine_vs_synthetic_SNAP_template': stats(corrs_HE_synthS),
    'F_heart_engine_vs_synthetic_CLOCK': stats(corrs_HE_synthC),
    'G_ENSO_engine_vs_synthetic_engine_template': stats(corrs_NE_synthE),
    'H_ENSO_engine_vs_synthetic_CLOCK': stats(corrs_NE_synthC),
    'I_ENSO_engine_vs_synthetic_SNAP': stats(corrs_NE_synthS),
    'J_heart_within_domain': stats(corrs_HE_HE),
    'K_calcium_within_domain': stats(corrs_CA_CA),
}

print(f"\n========= ARA CLASS CONTROL TEST (median |correlation| of N pairs) =========")
print(f"{'Comparison':<55}  {'N':>5}  {'mean':>7}  {'median':>7}  {'std':>6}")
for k, s in results.items():
    if s['n']==0: continue
    print(f"  {k:<55}  {s['n']:>5}  {s['mean']:+.3f}  {s['median']:+.3f}  {s['std']:.3f}")

# Save raw distributions and templates
out = dict(
    sources=dict(ecg="PhysioNet NSRDB nsr001",
                 nino="NOAA PSL Nino 3.4",
                 calcium="DANDI 000049 sub-760940732"),
    results=results,
    distributions=dict(
        A_heart_vs_ENSO_engine=corrs_HE_NE,
        B_heart_vs_calcium_clock=corrs_HE_CA,
        C_heart_vs_noise=corrs_HE_NOISE,
        D_heart_vs_synth_engine=corrs_HE_synthE,
        E_heart_vs_synth_snap=corrs_HE_synthS,
        F_heart_vs_synth_clock=corrs_HE_synthC,
        G_ENSO_vs_synth_engine=corrs_NE_synthE,
        H_ENSO_vs_synth_clock=corrs_NE_synthC,
        I_ENSO_vs_synth_snap=corrs_NE_synthS,
        J_heart_within=corrs_HE_HE,
        K_calcium_within=corrs_CA_CA,
    ),
    synthetic_templates=dict(
        engine=synth_engine.tolist(),
        snap=synth_snap.tolist(),
        clock=synth_clock.tolist(),
    ),
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.ARA_CONTROL = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

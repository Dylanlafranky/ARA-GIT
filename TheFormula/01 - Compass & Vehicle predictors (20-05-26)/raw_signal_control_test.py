"""
Raw-signal control test (Dylan 2026-05-03):

Previous test showed bandpassing was creating artifact-driven high correlations.
Now: keep the RAW signal shape (no bandpass smoothing), scale only time and
amplitude (which is necessary cross-scale comparison, not artifact).

For each system, find peaks in the RAW signal at the engine-cycle scale
using a min-distance constraint only (no frequency filtering).
Then segment peak-to-peak, time-normalize to [0,1], amplitude-normalize to [-1,+1].

Compare:
  A. Heart raw engine cycles vs ENSO raw engine cycles (SAME class)
  B. Heart raw engine vs Calcium raw clock cycles (DIFFERENT class)
  C. Heart raw engine vs random Gaussian noise cycles
  D. Heart raw engine vs synthetic engine template (ARA=φ)
  E. Heart raw engine vs synthetic CLOCK template
  F. Heart raw engine vs synthetic SNAP template

DATA: real PhysioNet (nsr001) + real NOAA Niño 3.4 + real DANDI calcium.
"""
import json, os, h5py
import numpy as np, pandas as pd
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

ECG_PATH  = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
NWB_PATH  = _resolve(r"F:\SystemFormulaFolder\Calcium_DANDI\calcium_imaging.nwb")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\raw_signal_control_data.js")

# Load data
ecg = pd.read_csv(ECG_PATH)
t_ecg = ecg['time_s'].values.astype(float); v_ecg_orig = ecg['rr_ms'].values.astype(float)
GRID_DT = 0.5
t_grid = np.arange(t_ecg[0], t_ecg[-1], GRID_DT)
v_ecg = np.interp(t_grid, t_ecg, v_ecg_orig)

df_n = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
df_n['date'] = pd.to_datetime(df_n['date'].str.strip())
df_n = df_n[df_n['val'] > -90].copy()
v_nino = df_n['val'].values.astype(float)

with h5py.File(NWB_PATH, 'r') as f:
    dff = f['processing/brain_observatory_pipeline/Fluorescence/DfOverF/data'][:]
    ts_ca = f['processing/brain_observatory_pipeline/Fluorescence/DfOverF/timestamps'][:]
ca = dff[:, int(np.argmax(np.var(dff, axis=0)))]
ca_dt = float(np.mean(np.diff(ts_ca)))

# Cycle extractor — uses RAW signal but with light smoothing only for peak detection
# The shape we keep is the RAW segment, not the smoothed one
def extract_raw_cycles(raw_signal, target_period_units, dt, smooth_for_peak_detection_factor=0.15):
    """Find peaks at the target period scale using lightly smoothed signal,
       but extract the RAW signal segments between peaks."""
    smooth_sigma = max(1, int(target_period_units * smooth_for_peak_detection_factor / dt))
    smoothed = gaussian_filter1d(raw_signal - np.mean(raw_signal), smooth_sigma)
    min_dist = int(target_period_units * 0.7 / dt)
    peaks, _ = find_peaks(smoothed, distance=min_dist)
    cycles_raw = []
    for i in range(len(peaks)-1):
        seg = raw_signal[peaks[i]:peaks[i+1]]  # USE RAW, not smoothed
        target_n = int(target_period_units / dt)
        if len(seg) < target_n*0.5: continue
        if len(seg) > target_n*2.5: continue
        cycles_raw.append(seg)
    return cycles_raw

N_PTS = 100
def normalize(seg):
    x_o = np.linspace(0, 1, len(seg))
    x_n = np.linspace(0, 1, N_PTS)
    s = np.interp(x_n, x_o, seg)
    s_n = s - s.min()
    if s_n.max() > 0: s_n = s_n/s_n.max()
    return 2*s_n - 1

# Extract RAW cycles at the engine scale
heart_raw = extract_raw_cycles(v_ecg, PHI**5, GRID_DT)
heart_cycles = [normalize(c) for c in heart_raw]
print(f"Heart RAW engine cycles (φ^5 ≈ 11s, segmented from raw RR with light peak detection): {len(heart_cycles)}")

nino_raw = extract_raw_cycles(v_nino, PHI**8, dt=1.0)
nino_cycles = [normalize(c) for c in nino_raw]
print(f"ENSO RAW engine cycles (φ^8 ≈ 47mo, raw monthly anomaly): {len(nino_cycles)}")

ca_raw = extract_raw_cycles(ca, PHI**3, ca_dt)
ca_cycles = [normalize(c) for c in ca_raw]
print(f"Calcium RAW clock cycles (φ^3 ≈ 4s): {len(ca_cycles)}")

# Synthetic templates (same as before)
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
synth_snap   = engine_template(ARA=2.5)
synth_clock  = -np.cos(np.linspace(0, 2*np.pi, N_PTS))

# RAW Gaussian noise cycles (no bandpass)
np.random.seed(42)
def random_raw_cycle(period_samples=22):
    """Sample a random walk-like signal of given length."""
    walk = np.cumsum(np.random.randn(period_samples))
    return normalize(walk)
noise_cycles = [random_raw_cycle(np.random.randint(15, 40)) for _ in range(100)]
np.random.seed(0)

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

corrs = {
    'A_heart_raw_vs_ENSO_raw': pair_corrs(heart_cycles, nino_cycles),
    'B_heart_raw_vs_calcium_raw': pair_corrs(heart_cycles, ca_cycles),
    'C_heart_raw_vs_random_walk': pair_corrs(heart_cycles, noise_cycles),
    'D_heart_raw_vs_synth_engine': [float(np.corrcoef(np.array(h), synth_engine)[0,1]) for h in heart_cycles],
    'E_heart_raw_vs_synth_snap':   [float(np.corrcoef(np.array(h), synth_snap)[0,1]) for h in heart_cycles],
    'F_heart_raw_vs_synth_clock':  [float(np.corrcoef(np.array(h), synth_clock)[0,1]) for h in heart_cycles],
    'G_ENSO_raw_vs_synth_engine':  [float(np.corrcoef(np.array(n), synth_engine)[0,1]) for n in nino_cycles],
    'H_ENSO_raw_vs_synth_snap':    [float(np.corrcoef(np.array(n), synth_snap)[0,1]) for n in nino_cycles],
    'I_ENSO_raw_vs_synth_clock':   [float(np.corrcoef(np.array(n), synth_clock)[0,1]) for n in nino_cycles],
    'J_calcium_raw_vs_synth_engine': [float(np.corrcoef(np.array(c), synth_engine)[0,1]) for c in ca_cycles],
    'K_calcium_raw_vs_synth_clock':  [float(np.corrcoef(np.array(c), synth_clock)[0,1]) for c in ca_cycles],
    'L_heart_within':   pair_corrs(heart_cycles, heart_cycles),
    'M_calcium_within': pair_corrs(ca_cycles, ca_cycles),
    'N_ENSO_within':    pair_corrs(nino_cycles, nino_cycles),
    'O_random_within':  pair_corrs(noise_cycles, noise_cycles),
    # Cross-class pairs:
    'P_heart_vs_calcium_raw': pair_corrs(heart_cycles, ca_cycles, seed=1),
}

def stats(c):
    if not c: return dict(n=0)
    a = np.array(c)
    return dict(n=len(c), mean=float(np.mean(a)), median=float(np.median(a)),
                std=float(np.std(a)),
                q25=float(np.percentile(a, 25)),
                q75=float(np.percentile(a, 75)),
                abs_mean=float(np.mean(np.abs(a))))

print(f"\n========= RAW-SIGNAL CONTROL TEST (cycle pair correlations) =========")
print(f"{'Comparison':<45}  {'N':>5}  {'mean':>7}  {'median':>7}  {'|mean|':>7}  {'std':>5}")
results = {}
for k, c in corrs.items():
    s = stats(c)
    if s['n']==0: continue
    results[k] = s
    print(f"  {k:<45}  {s['n']:>5}  {s['mean']:+.3f}  {s['median']:+.3f}  {s['abs_mean']:.3f}  {s['std']:.3f}")

# Critical comparison
hE_NE = results['A_heart_raw_vs_ENSO_raw']['median']
hE_CA = results['B_heart_raw_vs_calcium_raw']['median']
hE_NOISE = results['C_heart_raw_vs_random_walk']['median']
print(f"\n========= KEY DIAGNOSTIC =========")
print(f"Heart raw vs ENSO raw   median r = {hE_NE:+.3f}  (same class)")
print(f"Heart raw vs Calcium    median r = {hE_CA:+.3f}  (DIFFERENT class)")
print(f"Heart raw vs Noise walk median r = {hE_NOISE:+.3f}  (no class)")
diff_engine_clock = hE_NE - hE_CA
diff_engine_noise = hE_NE - hE_NOISE
print(f"\nEngine-vs-engine MINUS engine-vs-clock:  {diff_engine_clock:+.3f}")
print(f"Engine-vs-engine MINUS engine-vs-noise:  {diff_engine_noise:+.3f}")
if diff_engine_clock > 0.05 and diff_engine_noise > 0.05:
    print("\n  ★ Engine-engine pairing is meaningfully higher — class distinction is real on raw signals")
elif abs(diff_engine_clock) < 0.05 and abs(diff_engine_noise) < 0.05:
    print("\n  ~ All comparisons similar — cross-domain class distinction not visible in raw signals either")
else:
    print(f"\n  Mixed result")

# Sample cycles for visualization — pick 30 representative ones from each
np.random.seed(7)
def sample_cycles(cycles, n=30):
    if len(cycles) <= n: return [c if isinstance(c, list) else c.tolist() for c in cycles]
    idx = np.linspace(0, len(cycles)-1, n).astype(int)
    return [cycles[i].tolist() if hasattr(cycles[i],'tolist') else cycles[i] for i in idx]

sample_heart   = sample_cycles(heart_cycles, 30)
sample_nino    = sample_cycles(nino_cycles, 30)
sample_calcium = sample_cycles(ca_cycles, 30)
sample_noise   = sample_cycles(noise_cycles, 30)

# Compute mean curves for each source
def mean_curve(samples):
    if not samples: return [0]*N_PTS
    arr = np.array(samples)
    return arr.mean(axis=0).tolist()

out = dict(
    sources=dict(ecg="PhysioNet NSRDB nsr001", nino="NOAA PSL Nino 3.4", calcium="DANDI 000049"),
    method="Raw signal segmented at engine scale; time-normalized; amplitude to [-1,+1]",
    n_cycles=dict(heart=len(heart_cycles), nino=len(nino_cycles), calcium=len(ca_cycles), noise=len(noise_cycles)),
    results=results,
    distributions=corrs,
    diagnostic=dict(
        heart_vs_ENSO=hE_NE,
        heart_vs_calcium=hE_CA,
        heart_vs_noise=hE_NOISE,
        engine_engine_minus_engine_clock=float(diff_engine_clock),
        engine_engine_minus_engine_noise=float(diff_engine_noise),
    ),
    synthetic_templates=dict(engine=synth_engine.tolist(), snap=synth_snap.tolist(), clock=synth_clock.tolist()),
    sample_cycles=dict(
        heart=sample_heart, heart_mean=mean_curve(sample_heart),
        nino=sample_nino,   nino_mean=mean_curve(sample_nino),
        calcium=sample_calcium, calcium_mean=mean_curve(sample_calcium),
        noise=sample_noise, noise_mean=mean_curve(sample_noise),
    ),
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.RAW_CONTROL = " + json.dumps(out, default=str) + ";\n")
print("Saved -> " + OUT)

"""
Cross-domain template test — use ECG's known structure as a bedrock for ENSO.

The river-prediction claim (framework_river_prediction memory):
  Faster cycle's NOW = slower cycle's NEAR FUTURE, time-stretched by φ^k.

Practical implementation:
  1. ECG (nsr001, 22.5h RR-interval data) is FAST — we see thousands of cycles.
  2. ENSO (NINO 3.4) is SLOW — only ~16 cycles in the test set.
  3. If vertical ARA holds, ECG's MULTI-RUNG AMPLITUDE PROFILE tells us
     how amplitude distributes across rungs in ANY system.
  4. Use ECG's profile as the structural template for ENSO's rung amplitudes.

Specifically:
  - Compute ECG amplitude at each φ-rung (causal bandpass, 22.5h of data)
  - Normalize relative to ECG's peak rung
  - Apply that normalized profile to ENSO at its φ-rungs (matching by rung index
    relative to home rung, k=0 in ECG ↔ k=K_REF in ENSO)
  - Run rolling vehicle with ECG-templated amplitudes vs observed amplitudes

If vertical ARA is right, ECG-templated should beat (or at least match) the
observed-amplitude vehicle — because ECG's profile is a much cleaner estimate
of the true universal rung-amplitude structure (more cycles to average over).
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949
INV_PHI3 = 1.0 / (PHI**3)
INV_PHI4 = 1.0 / (PHI**4)

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

ECG_PATH  = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
SOI_PATH  = _resolve(r"F:\SystemFormulaFolder\SOI_NOAA\soi.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\ecg_template_for_enso_data.js")

print("Loading ECG nsr001 RR-interval data...")
ecg_df = pd.read_csv(ECG_PATH)
print(f"  {len(ecg_df)} beats, total time {ecg_df['time_s'].iloc[-1]/3600:.2f} hours")
# Resample to uniform 1-second grid for filtering
ecg_t = ecg_df['time_s'].values
ecg_rr = ecg_df['rr_ms'].values
# Uniform grid at 1Hz
t_uniform = np.arange(0, int(ecg_t[-1]) - 1)
ecg_signal = np.interp(t_uniform, ecg_t, ecg_rr)
ecg_signal = ecg_signal - np.mean(ecg_signal)
N_ECG = len(ecg_signal)
print(f"  Resampled to 1Hz: {N_ECG} samples = {N_ECG/3600:.2f} hours")

print("\nLoading NINO 3.4 + SOI...")
df = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
df['date'] = pd.to_datetime(df['date'].str.strip())
df = df[df['val']>-90].copy()
df['date'] = df['date'].dt.to_period('M').dt.to_timestamp()
df = df.groupby('date').first().reset_index().sort_values('date')
NINO = df['val'].values.astype(float)
DATES = df['date'].values
N_NINO = len(NINO)

# SOI loader
rows=[]
with open(SOI_PATH) as f:
    next(f)
    for ln in f:
        parts = ln.split()
        if len(parts) < 13: continue
        try: year = int(parts[0])
        except: continue
        if year < 1900 or year > 2100: continue
        for m in range(12):
            try: v = float(parts[1+m])
            except: continue
            if v < -90: continue
            rows.append((pd.Timestamp(year=year, month=m+1, day=1), v))
soi = pd.Series(dict(rows)).sort_index()
soi.index = pd.to_datetime(soi.index).to_period('M').to_timestamp()
soi = soi.groupby(soi.index).first()
df_n = pd.Series(dict(zip([pd.Timestamp(d) for d in DATES], NINO)))
common = df_n.index.intersection(soi.index)
NINO_aligned = df_n.reindex(common).values.astype(float)
SOI_aligned = soi.reindex(common).values.astype(float)
DATES = common
N = len(NINO_aligned)
NINO = NINO_aligned
SOI = SOI_aligned
print(f"  N={N} months common, {DATES[0].date()} to {DATES[-1].date()}")

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n = len(arr); f_c = 1.0/period_units; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    try:
        b, a = butter(order, [Wn_lo, Wn_hi], btype='bandpass')
        return lfilter(b, a, arr - np.mean(arr))
    except Exception:
        return np.zeros(n)

# ===== Compute ECG amplitude profile across φ-rungs =====
# ECG home rung: k_e=0 ≈ 1 second (heartbeat)
# Build rungs at φ^k for k=0..21 (covers up to ~22h, fits in 22.5h data)
print("\n=== ECG amplitude profile across φ-rungs ===")
ECG_RUNGS_K = list(range(0, 21))
ECG_AMPS = []
for k in ECG_RUNGS_K:
    period = PHI**k
    # Need enough data to bandpass at this period (≥3× period)
    if 3*period > N_ECG:
        ECG_AMPS.append(np.nan)
        print(f"  k={k:>2} P={period:>9.1f}s — insufficient data")
        continue
    bp = causal_bandpass(ecg_signal, period)
    # Use the second half (after filter warm-up)
    amp = float(np.std(bp[N_ECG//4:]))
    ECG_AMPS.append(amp)
    print(f"  k={k:>2} P={period:>9.1f}s  amp={amp:>8.3f} ms")
ECG_AMPS = np.array(ECG_AMPS)

# Find ECG peak rung (the dominant rung)
valid = ~np.isnan(ECG_AMPS)
peak_idx = int(np.nanargmax(ECG_AMPS))
ECG_PEAK_K = ECG_RUNGS_K[peak_idx]
ECG_AMP_PROFILE = ECG_AMPS / ECG_AMPS[peak_idx]  # normalized to peak = 1.0
print(f"\n  ECG peak at k={ECG_PEAK_K} ({PHI**ECG_PEAK_K:.1f}s = {PHI**ECG_PEAK_K/60:.2f} min)")
print(f"  ECG profile (normalized to peak):")
for i, k in enumerate(ECG_RUNGS_K):
    if not np.isnan(ECG_AMP_PROFILE[i]):
        rel_k = k - ECG_PEAK_K
        bar = '#' * int(ECG_AMP_PROFILE[i] * 30)
        print(f"    k={k:>2} (rel {rel_k:+d}): {ECG_AMP_PROFILE[i]:.3f} {bar}")

# ===== ENSO amplitude profile for comparison =====
print("\n=== ENSO amplitude profile across φ-rungs (for comparison) ===")
ENSO_RUNGS_K = list(range(4, 14))
ENSO_AMPS = []
for k in ENSO_RUNGS_K:
    period = PHI**k
    bp = causal_bandpass(NINO, period)
    amp = float(np.std(bp[N//4:]))
    ENSO_AMPS.append(amp)
    print(f"  k={k:>2} P={period:>7.1f}mo  amp={amp:>6.3f} °C")
ENSO_AMPS = np.array(ENSO_AMPS)
peak_n = int(np.argmax(ENSO_AMPS))
ENSO_PEAK_K = ENSO_RUNGS_K[peak_n]
ENSO_AMP_PROFILE = ENSO_AMPS / ENSO_AMPS[peak_n]
print(f"\n  ENSO peak at k={ENSO_PEAK_K} ({PHI**ENSO_PEAK_K:.1f}mo = {PHI**ENSO_PEAK_K/12:.2f} years)")
print(f"  ENSO profile (normalized to peak):")
for i, k in enumerate(ENSO_RUNGS_K):
    rel_k = k - ENSO_PEAK_K
    bar = '#' * int(ENSO_AMP_PROFILE[i] * 30)
    print(f"    k={k:>2} (rel {rel_k:+d}): {ENSO_AMP_PROFILE[i]:.3f} {bar}")

# ===== Compare profiles by relative rung index =====
print("\n=== Cross-domain comparison: ECG profile vs ENSO profile ===")
print(f"  Mapping ECG rung (k - {ECG_PEAK_K}) to ENSO rung (k - {ENSO_PEAK_K}):")
print(f"  {'rel_k':>5}  {'ECG':>8}  {'ENSO':>8}  {'match?':>8}")
shared = []
for rel_k in range(-6, 7):
    ek = ECG_PEAK_K + rel_k
    nk = ENSO_PEAK_K + rel_k
    if ek in ECG_RUNGS_K and nk in ENSO_RUNGS_K:
        e_amp = ECG_AMP_PROFILE[ECG_RUNGS_K.index(ek)]
        n_amp = ENSO_AMP_PROFILE[ENSO_RUNGS_K.index(nk)]
        if not np.isnan(e_amp):
            shared.append((rel_k, e_amp, n_amp))
            ratio = e_amp / max(n_amp, 1e-6)
            print(f"  {rel_k:>+5}  {e_amp:>8.3f}  {n_amp:>8.3f}  ratio={ratio:.2f}")

if len(shared) >= 3:
    e_arr = np.array([s[1] for s in shared])
    n_arr = np.array([s[2] for s in shared])
    profile_corr = float(np.corrcoef(e_arr, n_arr)[0,1]) if np.std(e_arr)>1e-9 and np.std(n_arr)>1e-9 else 0.0
    print(f"\n  Profile shape correlation across {len(shared)} shared rel-rungs: {profile_corr:+.3f}")
    if abs(profile_corr) > 0.7:
        print("  → STRONG cross-domain match — vertical ARA holds!")
    elif abs(profile_corr) > 0.4:
        print("  → MODERATE cross-domain match — partial vertical ARA support")
    else:
        print("  → WEAK match — vertical ARA may only work within ARA class")

out = dict(method="ECG amplitude profile as cross-domain template for ENSO",
           ecg_rungs=ECG_RUNGS_K, ecg_amps=ECG_AMPS.tolist(), ecg_peak_k=ECG_PEAK_K,
           ecg_profile_normalized=ECG_AMP_PROFILE.tolist(),
           enso_rungs=ENSO_RUNGS_K, enso_amps=ENSO_AMPS.tolist(), enso_peak_k=ENSO_PEAK_K,
           enso_profile_normalized=ENSO_AMP_PROFILE.tolist(),
           shared_relative_rungs=[dict(rel_k=s[0], ecg=s[1], enso=s[2]) for s in shared],
           profile_correlation=profile_corr if len(shared)>=3 else None)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.ECG_TEMPLATE = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

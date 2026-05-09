"""
Cross-scale landmark comparison test (Dylan 2026-05-03):

ECG (~1s engine cycles) vs ENSO (~4yr engine cycles).
Both are engines (ARA ≈ φ). Both have rich landmark structure.
Scale gap ~10^8.

Test: extract average cycle waveform from each, normalize time to [0,1],
compare shapes. If vertical ARA holds, the landmarks should align —
same accumulation rise, peak position, release fall.

DATA SOURCES:
  ECG: PhysioNet Normal Sinus Rhythm RR Interval Database — nsr001
       https://physionet.org/content/nsrdb/1.0.0/
  ENSO: NOAA PSL Niño 3.4 long anomaly 1870-2025
        https://psl.noaa.gov/data/timeseries/month/
"""
import json, os, math
import numpy as np, pandas as pd
from scipy.signal import find_peaks, hilbert

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

ECG_PATH  = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\landmark_comparison_data.js")

# Load ECG RR-interval series
ecg = pd.read_csv(ECG_PATH)
t_ecg = ecg['time_s'].values.astype(float)
v_ecg = ecg['rr_ms'].values.astype(float)
# Resample to uniform 0.5s grid
GRID_DT = 0.5
t_grid = np.arange(t_ecg[0], t_ecg[-1], GRID_DT)
v_ecg_uniform = np.interp(t_grid, t_ecg, v_ecg)
print(f"ECG: {len(v_ecg_uniform)} samples at {GRID_DT}s grid, {(t_ecg[-1]-t_ecg[0])/3600:.1f}h total")

# Load ENSO
df_n = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
df_n['date'] = pd.to_datetime(df_n['date'].str.strip())
df_n = df_n[df_n['val'] > -90].copy()
v_nino = df_n['val'].values.astype(float)
print(f"ENSO: {len(v_nino)} months (1870-2025)")

# === Bandpass at the dominant engine rung for each ===
def bandpass(arr, period_units, dt=1.0, bw=0.4):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_units
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

# For ECG: pick the engine rung — Mayer wave (~10s) is a good engine rhythm
# We'll pick φ⁵ ≈ 11s ✓ matches Mayer waves
ECG_PERIOD_S = PHI**5  # ≈ 11.09 s
print(f"\nECG bandpass at {ECG_PERIOD_S:.2f}s (Mayer-wave rung φ^5)")
ecg_band = bandpass(v_ecg_uniform, ECG_PERIOD_S, GRID_DT, bw=0.35)

# For ENSO: pick the engine rung at ENSO's natural period
# El Niño cycles are ~3-7 yr. φ⁷ = 47 mo ≈ 3.9 yr is too short, φ⁸ = 76 mo ≈ 6.3 yr
# Use the broader ~50 month period (between φ⁷ and φ⁸)
NINO_PERIOD_MO = PHI**8  # ≈ 47 mo
print(f"ENSO bandpass at {NINO_PERIOD_MO:.1f} months (φ^8)")
nino_band = bandpass(v_nino, NINO_PERIOD_MO, dt=1.0, bw=0.5)

# === Cycle extraction: peak-to-peak segmentation ===
def extract_cycles(band, min_cycle_samples):
    """Find peaks, extract cycle waveforms (peak-to-peak), normalize time, average."""
    # Find peaks with reasonable separation
    peaks, _ = find_peaks(band, distance=int(min_cycle_samples*0.7))
    if len(peaks) < 3: return None, None, []
    cycles = []
    for i in range(len(peaks)-1):
        seg = band[peaks[i]:peaks[i+1]]
        if len(seg) < min_cycle_samples*0.5: continue  # too short
        if len(seg) > min_cycle_samples*2.5: continue  # too long
        # Normalize time to [0,1] by linear interpolation
        x_orig = np.linspace(0, 1, len(seg))
        x_norm = np.linspace(0, 1, 100)
        seg_norm = np.interp(x_norm, x_orig, seg)
        # Normalize amplitude: peak at +1, trough at lowest
        seg_norm = seg_norm - seg_norm.min()
        if seg_norm.max() > 0:
            seg_norm = seg_norm / seg_norm.max()
        cycles.append(seg_norm)
    if not cycles: return None, None, []
    cycles = np.array(cycles)
    template_mean = cycles.mean(axis=0)
    template_std  = cycles.std(axis=0)
    return template_mean, template_std, cycles

ecg_period_samples = int(ECG_PERIOD_S/GRID_DT)
ecg_template, ecg_std, ecg_cycles = extract_cycles(ecg_band, ecg_period_samples)
print(f"ECG: extracted {len(ecg_cycles)} cycles at φ^5 rung")

nino_period_samples = int(NINO_PERIOD_MO)
nino_template, nino_std, nino_cycles = extract_cycles(nino_band, nino_period_samples)
print(f"ENSO: extracted {len(nino_cycles)} cycles at φ^8 rung")

if ecg_template is None or nino_template is None:
    print("ERROR: cycle extraction failed")
    exit(1)

# === Compare templates ===
shape_corr = float(np.corrcoef(ecg_template, nino_template)[0,1])
shape_rmse = float(np.sqrt(np.mean((ecg_template - nino_template)**2)))

# Find peak positions
ecg_peak_loc = float(np.argmax(ecg_template)/100)
nino_peak_loc = float(np.argmax(nino_template)/100)

# Compute "ARA" of each template — rise time vs fall time relative to peak
def template_ARA(template):
    peak = int(np.argmax(template))
    # rising portion length normalized
    rise_frac = peak/len(template)
    fall_frac = 1.0 - rise_frac
    if fall_frac == 0: return np.nan
    return rise_frac / fall_frac

ecg_ARA = template_ARA(ecg_template)
nino_ARA = template_ARA(nino_template)
# Reverse so that "accumulation/release" is correct: T_acc/T_rel = rise/fall
# Actually for an engine (ARA = φ), accumulation is the LONGER part
# Let me also compute the inverse to handle either orientation
ecg_ARA_alt = (1.0 - ecg_peak_loc) / max(ecg_peak_loc, 1e-9)
nino_ARA_alt = (1.0 - nino_peak_loc) / max(nino_peak_loc, 1e-9)

print(f"\n========= LANDMARK COMPARISON =========")
print(f"Time-normalized peak position:")
print(f"  ECG  template peak at fraction {ecg_peak_loc:.3f}  (1 cycle ≈ {ECG_PERIOD_S:.1f}s)")
print(f"  ENSO template peak at fraction {nino_peak_loc:.3f}  (1 cycle ≈ {NINO_PERIOD_MO/12:.1f}yr)")
print(f"  Δ peak position: {abs(ecg_peak_loc - nino_peak_loc):.3f}")
print(f"\nApparent ARA (rise/fall ratio):")
print(f"  ECG:  rise/fall = {ecg_ARA:.3f}  (alt orientation: {ecg_ARA_alt:.3f})")
print(f"  ENSO: rise/fall = {nino_ARA:.3f}  (alt orientation: {nino_ARA_alt:.3f})")
print(f"\nShape similarity:")
print(f"  Pearson correlation = {shape_corr:+.3f}")
print(f"  RMSE on normalized [0,1]×[0,1] templates = {shape_rmse:.3f}")

# Symbol guide for output
if shape_corr > 0.9:
    print("\n  ★★★ SHAPES NEARLY IDENTICAL across 10^8 scale gap")
elif shape_corr > 0.7:
    print("\n  ★★ Strong shape match")
elif shape_corr > 0.5:
    print("\n  ★ Moderate shape match")
elif shape_corr > 0.3:
    print("\n  ~ Weak shape match")
else:
    print("\n  - Shapes diverge")

# Save
out = dict(
    sources=dict(
        ecg="PhysioNet NSRDB nsr001 RR intervals",
        ecg_url="https://physionet.org/content/nsrdb/1.0.0/",
        ecg_rung="φ^5 ≈ 11.09 s (Mayer-wave engine rung)",
        nino="NOAA PSL Niño 3.4 long anomaly 1870-2025",
        nino_url="https://psl.noaa.gov/data/timeseries/month/",
        nino_rung="φ^8 ≈ 47 months (4-year ENSO engine rung)",
    ),
    ecg_template=ecg_template.tolist(),
    ecg_std=ecg_std.tolist(),
    ecg_n_cycles=int(len(ecg_cycles)),
    nino_template=nino_template.tolist(),
    nino_std=nino_std.tolist(),
    nino_n_cycles=int(len(nino_cycles)),
    shape_corr=shape_corr,
    shape_rmse=shape_rmse,
    ecg_peak_loc=ecg_peak_loc,
    nino_peak_loc=nino_peak_loc,
    ecg_ARA=ecg_ARA,
    nino_ARA=nino_ARA,
    scale_gap=f"~10^{int(np.log10(NINO_PERIOD_MO*30*24*3600/ECG_PERIOD_S))}",
)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write("window.LANDMARK = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

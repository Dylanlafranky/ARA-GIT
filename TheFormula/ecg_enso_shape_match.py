"""
ecg_enso_shape_match.py — ECG ↔ ENSO vertical-ARA shape test.

Both systems share matched-rung topology (validated earlier at +0.695 corr across
6 rel-rungs of peak in `framework_vertical_ARA.md`). Now test whether their
CYCLE-SHAPE TEMPLATES match after time-rescaling, with proper null check.

Prior failure mode (lung↔forest): both shapes were near-pure sinusoidal,
gross correlation +0.985 was matched by pure sine at +0.995. Sine-wave null
collapsed the result.

ECG and ENSO should NOT have this problem because:
  - ECG has the sharp PQRST complex (very non-sinusoidal)
  - ENSO events have asymmetric peak-to-recovery profiles
Both have substantial harmonic content beyond fundamental.

Method:
  1. ECG: load BIDMC subjects' II channel (lead II), detect R-peaks, extract
     ~1-sec beat windows centered on R, normalize amplitude, average.
  2. ENSO: load NINO 3.4 monthly, detect strong El Niño peaks (>1°C), extract
     ~36-month windows centered on peak, normalize amplitude, average.
  3. Resample both to 200 phase samples.
  4. Compute Fourier-coefficient distance vs each other AND vs ~10 null candidates.
  5. Pass if ECG↔ENSO is the SMALLEST distance.

Data: PhysioNet BIDMC + NOAA NINO 3.4. Both public.
"""
import os, json, math
import numpy as np
import requests
import wfdb
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = (1+5**0.5)/2

# ============================================================================
# 1. ECG: extract average beat shape from BIDMC subjects
# ============================================================================
print("[1/5] Loading ECG (BIDMC II-lead) ...")
N = 3
beat_shapes = []
for i in range(1, N+1):
    sid = f'bidmc{i:02d}'
    try:
        r = wfdb.rdrecord(sid, pn_dir='bidmc')
    except Exception as e:
        print(f'  {sid}: {e}'); continue
    # II-lead channel
    ii_idx = next((j for j,n in enumerate(r.sig_name) if n.startswith('II')), None)
    if ii_idx is None: continue
    ecg = r.p_signal[:, ii_idx]
    fs = r.fs
    # detect R-peaks: simple — bandpass + find_peaks
    from scipy.signal import butter, sosfilt
    sos = butter(2, [5/(fs/2), 15/(fs/2)], btype='bandpass', output='sos')
    bp = sosfilt(sos, ecg)
    # R-peaks: peaks in bandpass with min distance ~0.4 sec
    rpeaks, _ = find_peaks(bp, distance=int(fs*0.4), height=np.std(bp)*1.5)
    # extract ±0.5 sec windows centered on R
    win_half = int(fs * 0.4)  # ±400 ms = 800 ms beat window
    n_beats = 0
    for r_idx in rpeaks:
        a, b = r_idx - win_half, r_idx + win_half
        if a < 0 or b > len(ecg): continue
        beat = ecg[a:b]
        # resample to 200
        xo = np.linspace(0,1,len(beat)); xn = np.linspace(0,1,200)
        b_rs = np.interp(xn, xo, beat)
        b_rs = (b_rs - b_rs.min()) / max(1e-9, b_rs.max() - b_rs.min())
        beat_shapes.append(b_rs)
        n_beats += 1
    print(f'  {sid}: {n_beats} beats')
beat_shapes = np.array(beat_shapes)
mean_beat = beat_shapes.mean(axis=0)
print(f'  Total: {len(beat_shapes)} beats from {N} subjects')

# ============================================================================
# 2. ENSO: extract average El Niño event shape
# ============================================================================
print("\n[2/5] Loading ENSO (NINO 3.4) ...")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
df = pd.read_csv(os.path.join(REPO_ROOT, 'Nino34', 'nino34.long.anom.csv'),
                 skiprows=1, names=['date','val'], header=None, sep=',', engine='python')
nino = pd.to_numeric(df['val'], errors='coerce').dropna().values.astype(float)
nino = nino[nino > -50]
print(f'  {len(nino)} months')

# Detect El Niño events: peaks > 1°C with min separation 24 months
event_peaks, _ = find_peaks(nino, height=1.0, distance=24)
print(f'  El Niño events (>1.0°C, sep≥24mo): {len(event_peaks)}')

# Extract 36-month windows around each event peak
win_half_e = 18
event_shapes = []
for p in event_peaks:
    a, b = p - win_half_e, p + win_half_e
    if a < 0 or b > len(nino): continue
    ev = nino[a:b]
    xo = np.linspace(0,1,len(ev)); xn = np.linspace(0,1,200)
    e_rs = np.interp(xn, xo, ev)
    e_rs = (e_rs - e_rs.min()) / max(1e-9, e_rs.max() - e_rs.min())
    event_shapes.append(e_rs)
event_shapes = np.array(event_shapes)
mean_event = event_shapes.mean(axis=0)
print(f'  Total: {len(event_shapes)} El Niño events extracted')

# ============================================================================
# 3. ALIGN: roll so both peaks at same phase
# ============================================================================
print("\n[3/5] Aligning peaks ...")
def align_to(target, candidate):
    tp = int(np.argmax(target))
    cp = int(np.argmax(candidate))
    rolled = np.roll(candidate, tp - cp)
    return rolled, tp, cp

mean_event_aligned, ecg_peak, enso_peak = align_to(mean_beat, mean_event)
print(f'  ECG peak phase: {ecg_peak}/200, ENSO peak phase: {enso_peak}/200')

# ============================================================================
# 4. NULL CANDIDATES
# ============================================================================
print("\n[4/5] Building null candidates ...")
n = 200
phase = np.linspace(0, 2*np.pi, n, endpoint=False)
nulls = {
    'pure sine': np.sin(phase),
    'sharp peak (sech-shape)': 1.0 / np.cosh(3*np.cos(phase/2)),
    'sawtooth slow-rise': np.where(phase < np.pi, phase/np.pi, 2-phase/np.pi),
    'sawtooth fast-rise': np.where(phase < np.pi*0.3, phase/(np.pi*0.3), (2*np.pi-phase)/(2*np.pi-np.pi*0.3)),
    'sine + 0.3 cos(2θ) peaked': np.sin(phase) + 0.3*np.cos(2*phase),
    'sine + 0.5 cos(2θ + π/2)': np.sin(phase) + 0.5*np.cos(2*phase + np.pi/2),
    'fast-spike + slow-recovery': np.exp(-((phase - np.pi)**2) / 0.5) - 0.3*np.exp(-((phase - np.pi*1.6)**2) / 2.0),
    'symmetric Gaussian peak': np.exp(-((phase - np.pi)**2) / 1.0),
    'double-peak (PQRST-like rough)': np.exp(-((phase - np.pi*0.95)**2) / 0.05) - 0.3*np.exp(-((phase - np.pi*1.05)**2) / 0.08) + 0.15*np.exp(-((phase - np.pi*1.25)**2) / 0.5),
}
def norm(x):
    return (x - x.min()) / max(1e-9, x.max() - x.min())

# ============================================================================
# 5. FOURIER-COEFFICIENT DISTANCE
# ============================================================================
print("\n[5/5] Fourier-coefficient distance test ...")

def fourier_params(shape, k_max=6):
    """Return amplitude+phase signature: (R21, R31, ..., phi21, phi31, ...)."""
    s = shape - shape.mean()
    F = np.fft.fft(s)
    a = F[:k_max+1]
    amp = np.abs(a); ph = np.angle(a)
    R = [amp[k]/amp[1] if amp[1] > 0 else 0.0 for k in range(2, k_max+1)]
    phi = [float(np.mod(ph[k] - k*ph[1] + np.pi, 2*np.pi) - np.pi) for k in range(2, k_max+1)]
    return np.array(R + phi)

p_ecg = fourier_params(mean_beat)
p_enso = fourier_params(mean_event_aligned)

def dist(a, b):
    return float(np.linalg.norm(a - b))

d_ecg_enso = dist(p_ecg, p_enso)

# Compare to all nulls
results = [('ENSO event (aligned to ECG)', d_ecg_enso)]
for name, sig in nulls.items():
    s_norm = norm(sig)
    s_aligned, _, _ = align_to(mean_beat, s_norm)
    p_null = fourier_params(s_aligned)
    d = dist(p_ecg, p_null)
    results.append((name, d))

# Sort by distance
results.sort(key=lambda x: x[1])
print()
print(f"{'comparison':<42} {'Fourier-dist':>13} {'rank':>5}")
print('-' * 65)
for rank, (name, d) in enumerate(results, 1):
    marker = ' ← ENSO' if name.startswith('ENSO') else ''
    print(f"  {name:<40} {d:>13.4f} {rank:>5}{marker}")

# Verdict
enso_rank = next(i for i, (name, _) in enumerate(results, 1) if name.startswith('ENSO'))
print()
print('=' * 65)
print('VERDICT')
print('=' * 65)
print(f'ENSO event shape ranks #{enso_rank} of {len(results)} candidates')
print(f'  (lower distance = closer Fourier-shape match to ECG)')
print()
if enso_rank == 1:
    print('  → STRONG: ENSO is the closest shape match. Beats all null candidates.')
elif enso_rank <= 3:
    print('  → MODERATE: ENSO in top 3 candidates. Survives most nulls.')
else:
    print('  → WEAK: ENSO ranks below most asymmetric nulls. No specific match.')

# Also report gross correlation (the failure mode we want to avoid)
def corr(a, b):
    return float(np.corrcoef(a, b)[0,1])
c_ecg_enso = corr(mean_beat, mean_event_aligned)
print(f'\nGross correlation ECG↔ENSO (after alignment): {c_ecg_enso:+.3f}')
print(f'  (For reference — sine wave gave +0.995 on lung↔forest. This metric is unreliable.)')

# Save
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ecg_enso_shape_match_data.js')
payload = dict(
    date='2026-05-11',
    n_ecg_beats=int(len(beat_shapes)),
    n_enso_events=int(len(event_shapes)),
    mean_beat=[float(x) for x in mean_beat],
    mean_event_aligned=[float(x) for x in mean_event_aligned],
    fourier_distance_ecg_enso=d_ecg_enso,
    enso_rank=enso_rank,
    null_results=[{'name': n, 'distance': float(d)} for n, d in results],
    gross_corr_ecg_enso=c_ecg_enso,
    phi=PHI,
)
with open(OUT, 'w') as f:
    f.write("window.ECG_ENSO_SHAPE = " + json.dumps(payload, default=str) + ";\n")
print(f'\nSaved -> {OUT}')

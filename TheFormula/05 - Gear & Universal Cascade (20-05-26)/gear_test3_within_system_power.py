"""gear_test3_within_system_power.py — Dylan 2026-05-12.

Test 3 from framework_gear_mechanics_anchor.md:
For consecutive rungs within ONE system (no cross-species coupling), gear-law
power conservation predicts amp/T should be constant across rungs.

With π-leak coupling tax: between adjacent rungs, amp/T should drop by ≈4.5%.
After N rungs: amp/T should be (0.955)^N times the starting value.

Tests:
  1. Is amp/T constant across rungs? (strict gear law)
  2. Does amp/T decay geometrically with rung index? (gear law + π-leak)
  3. Is amplitude alone constant? (suggesting bandpass artifact or other)
  4. Does amp scale with T? (passive 1/f noise prediction)

Run on mouse RR, human RR, NINO 3.4, SOI for cross-system check.
"""
import os, glob, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt

PHI = (1+5**0.5)/2
PI_LEAK = (math.pi - 3) / math.pi  # ≈ 0.0451
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
def log(s): print(s, flush=True)

# ============================================================================
# Loaders
# ============================================================================
def parse_peaks(path):
    with open(path) as f: text = f.read()
    if 'Mammal:' not in text: return None
    fs = None; peaks = []
    for line in text.split('\n'):
        s = line.strip()
        if s.startswith('Fs:'): fs = int(s.split()[-1])
        elif s and s[0].isdigit():
            try: peaks.append(int(s))
            except: pass
    return (fs, np.array(peaks)) if fs and peaks else None

mouse_segs = []
for p in sorted(glob.glob(os.path.join(REPO_ROOT, 'PhysioZoo', 'peaks_Mouse_*.txt'))):
    parsed = parse_peaks(p)
    if parsed:
        fs, pks = parsed
        if len(pks) >= 1000: mouse_segs.append(np.diff(pks)/fs*1000)
mouse_rr = np.concatenate(mouse_segs)
hdf = pd.read_csv(os.path.join(REPO_ROOT, 'TheFormula', 'nsr001_rr.csv'))
human_rr = hdf['rr_ms'].values.astype(float)

# NINO + SOI
nino_df = pd.read_csv(os.path.join(REPO_ROOT, 'Nino34', 'nino34.long.anom.csv'),
                     parse_dates=['Date'], na_values=[-99.99]).dropna()
nino_df.columns = [c.strip() for c in nino_df.columns]
nino_col = [c for c in nino_df.columns if 'NINA' in c.upper()][0]
nino = nino_df[nino_col].values

soi_rows = []
with open(os.path.join(REPO_ROOT, 'SOI_NOAA', 'soi.data')) as f:
    for line in f:
        parts = line.split()
        if len(parts) == 13:
            try:
                yr = int(parts[0])
                for v in [float(x) for x in parts[1:]]:
                    if v > -90: soi_rows.append(v)
            except: pass
soi = np.array(soi_rows)

# ============================================================================
# Amplitude at period P
# ============================================================================
def amp_at(rr, P_units):
    low = 1/(P_units*1.4); high = 1/(P_units*0.7); nyq = 0.5
    lo, hi = max(0.001, low/nyq), min(0.999, high/nyq)
    if lo >= hi: return None
    try:
        sos = butter(4, [lo, hi], btype='band', output='sos')
        f = sosfiltfilt(sos, rr)
        return float(np.std(f)) if np.std(f) > 1e-9 else None
    except: return None

# ============================================================================
# Run test on a single system
# ============================================================================
def run_test_3(rr, label, mean_period, periods_in_native_units):
    """For each rung, compute amp, amp/T, amp×T. Check what's conserved."""
    log(f'\n=== {label} (mean period = {mean_period:.2f}) ===')
    log(f'{"rung P":>8} | {"amp":>10} | {"amp/T (×1000)":>14} | {"amp×T":>10} | {"adj ratio amp/T":>17}')
    log('-' * 80)
    
    rows = []
    for P in periods_in_native_units:
        if P >= len(rr) // 4: continue
        a = amp_at(rr, P)
        if a is None: continue
        T_real = P * mean_period  # physical period
        amp_over_T = a / T_real * 1000  # scaled
        amp_times_T = a * T_real / 1000
        rows.append({'P': P, 'amp': a, 'amp_over_T': amp_over_T, 'amp_times_T': amp_times_T, 'T_real': T_real})
    
    # Adjacent ratios
    for i, r in enumerate(rows):
        if i > 0:
            adj_ratio = r['amp_over_T'] / rows[i-1]['amp_over_T']
        else:
            adj_ratio = float('nan')
        log(f'{r["P"]:>8d} | {r["amp"]:>10.4f} | {r["amp_over_T"]:>14.4f} | {r["amp_times_T"]:>10.4f} | {adj_ratio:>17.4f}')
    
    # Stats
    if len(rows) >= 4:
        amps = np.array([r['amp'] for r in rows])
        amp_T = np.array([r['amp_over_T'] for r in rows])
        amp_t = np.array([r['amp_times_T'] for r in rows])
        log(f'\n  Coefficient of variation (CV) — lower means more conserved:')
        log(f'    amp alone:    CV = {amps.std()/amps.mean():.3f}')
        log(f'    amp/T:        CV = {amp_T.std()/amp_T.mean():.3f}')
        log(f'    amp×T:        CV = {amp_t.std()/amp_t.mean():.3f}')
        
        # If amp/T is geometrically decaying (gear-law + π-leak), check ratio
        log(f'\n  Adjacent amp/T ratios (gear law + π-leak predicts ≈ {1-PI_LEAK:.3f} each):')
        ratios = amp_T[1:] / amp_T[:-1]
        log(f'    mean ratio: {ratios.mean():.3f}  (range {ratios.min():.3f} – {ratios.max():.3f})')
        log(f'    deviation from (1−π_leak) = {1-PI_LEAK:.3f}: {abs(ratios.mean() - (1-PI_LEAK)):.3f}')
        
        # Log-linear fit to detect geometric scaling
        log_amp_T = np.log(amp_T)
        slope, intercept = np.polyfit(range(len(log_amp_T)), log_amp_T, 1)
        log(f'    Geometric decay rate per rung: {math.exp(slope):.3f}  (1.0 = constant, <1 = decaying)')

# Mouse: native unit is beats, mean RR ≈ 115ms
run_test_3(mouse_rr, "MOUSE cardiac (rungs in beats, mean RR 115ms)", 0.115, [3, 5, 8, 13, 21, 34, 55, 89, 144])
# Human
run_test_3(human_rr, "HUMAN cardiac (rungs in beats, mean RR 760ms)", 0.760, [3, 5, 8, 13, 21, 34, 55, 89, 144])
# NINO 3.4 (monthly)
run_test_3(nino, "NINO 3.4 (rungs in months)", 1.0, [3, 5, 8, 13, 21, 34, 55, 89, 144])
# SOI (monthly)
run_test_3(soi, "SOI (rungs in months)", 1.0, [3, 5, 8, 13, 21, 34, 55, 89, 144])

log(f'\n=== OVERALL VERDICT ===')
log(f'Gear-law + π-leak predicts: adjacent amp/T ratio ≈ {1-PI_LEAK:.3f}')
log(f'See per-system CV above. Lowest CV = best-conserved quantity.')

log('\n=== Done ===')

"""apollonian_descartes_test.py — Dylan 2026-05-12.

Test: do measured ARA values across consecutive rungs satisfy Descartes' Circle
Theorem? Reframe per Dylan: rungs are ARA-spaced, not φ-spaced; φ is one
landmark inside the ARA scale.

Method:
  1. For each system (mouse RR, human RR), bandpass at Fibonacci-spaced rungs.
  2. Compute ARA (build/release ratio) on each bandpassed signal.
  3. For each consecutive triple (rung k, k+1, k+2), use Descartes' theorem
     to predict the curvature (= ARA, under the test encoding) at rung k+3.
  4. Compare predicted ARA to measured ARA at rung k+3.
  5. Test multiple curvature encodings: k = ARA, k = 1/ARA, k = ARA - 1, k = 1/(ARA-1+ε).
  6. Report MAE and correlation between predicted and actual for each encoding.
"""
import os, glob, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt, hilbert

PHI = (1+5**0.5)/2
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)

def log(s): print(s, flush=True)

# ============================================================================
# Load
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
        if len(pks) >= 1000:
            mouse_segs.append(np.diff(pks)/fs*1000)
mouse_rr = np.concatenate(mouse_segs)
hdf = pd.read_csv(os.path.join(REPO_ROOT, 'TheFormula', 'nsr001_rr.csv'))
human_rr = hdf['rr_ms'].values.astype(float)
log(f'Mouse: {len(mouse_rr)} beats, Human: {len(human_rr)} beats')

# ============================================================================
# Per-rung ARA computation
# ============================================================================
def compute_ara(signal):
    """ARA = build-time / release-time. Build = where signal is rising; release = falling."""
    diffs = np.diff(signal)
    rising = diffs > 0
    falling = diffs < 0
    n_rise = np.sum(rising)
    n_fall = np.sum(falling)
    if n_fall == 0: return 2.0  # all rising
    ara = n_rise / n_fall
    return float(np.clip(ara, 0.01, 100.0))

def per_rung_ara(rr, periods_in_beats):
    """For each Fibonacci period, bandpass and compute ARA."""
    ara_values = {}
    for P in periods_in_beats:
        # Bandpass with center at period P, fractional bandwidth 0.4
        low_freq = 1.0 / (P * 1.4)
        high_freq = 1.0 / (P * 0.7)
        nyq = 0.5  # in beat units
        low = max(0.001, low_freq / nyq)
        high = min(0.999, high_freq / nyq)
        if low >= high: continue
        try:
            sos = butter(4, [low, high], btype='band', output='sos')
            filtered = sosfiltfilt(sos, rr)
            if np.std(filtered) < 1e-9: continue
            ara_values[P] = compute_ara(filtered)
        except Exception as e:
            continue
    return ara_values

# Fibonacci periods (φ-rungs in beat units)
FIB = [3, 5, 8, 13, 21, 34, 55, 89]
log(f'Fibonacci periods (beats): {FIB}')

ara_mouse = per_rung_ara(mouse_rr, FIB)
ara_human = per_rung_ara(human_rr, FIB)
log(f'\nMouse ARA per rung:')
for P, a in ara_mouse.items(): log(f'  P={P:3d} beats: ARA={a:.3f}')
log(f'\nHuman ARA per rung:')
for P, a in ara_human.items(): log(f'  P={P:3d} beats: ARA={a:.3f}')

# ============================================================================
# Descartes' Circle Theorem
# ============================================================================
def descartes_predict(k1, k2, k3):
    """Predict the fourth tangent circle's curvature given three.
       Returns (k_inscribed, k_circumscribed)."""
    s = k1 + k2 + k3
    p = k1*k2 + k2*k3 + k3*k1
    if p < 0: return (None, None)
    sqrt_term = 2 * math.sqrt(p)
    return (s + sqrt_term, s - sqrt_term)

# ============================================================================
# Test multiple encodings
# ============================================================================
def encode(ara, mode):
    if mode == 'ara':       return ara
    if mode == 'inv_ara':   return 1.0 / ara
    if mode == 'ara_minus1': return ara - 1.0  # offset from balance
    if mode == 'inv_dist':  return 1.0 / (abs(ara - 1.0) + 1e-3)  # inverse distance from balance
    if mode == 'log_ara':   return math.log(ara)
    return ara

def decode(k, mode):
    if mode == 'ara':       return k
    if mode == 'inv_ara':   return 1.0 / k if k != 0 else 100.0
    if mode == 'ara_minus1': return k + 1.0
    if mode == 'inv_dist':  return None  # cannot uniquely decode
    if mode == 'log_ara':   return math.exp(k)
    return k

ENCODINGS = ['ara', 'inv_ara', 'ara_minus1', 'log_ara']

def test_descartes(ara_dict, label):
    log(f'\n=== Descartes test on {label} ===')
    rungs = sorted(ara_dict.keys())
    if len(rungs) < 4:
        log('  Not enough rungs.')
        return
    
    for mode in ENCODINGS:
        log(f'\n  Encoding: k = {mode}')
        errors_inscribed = []
        errors_circumscribed = []
        for i in range(len(rungs) - 3):
            r1, r2, r3, r4 = rungs[i:i+4]
            k1, k2, k3 = encode(ara_dict[r1], mode), encode(ara_dict[r2], mode), encode(ara_dict[r3], mode)
            k4_in, k4_out = descartes_predict(k1, k2, k3)
            actual_k4 = encode(ara_dict[r4], mode)
            actual_ara4 = ara_dict[r4]
            
            if k4_in is not None:
                pred_in = decode(k4_in, mode)
                pred_out = decode(k4_out, mode) if k4_out is not None else None
                if pred_in is not None:
                    err_in = abs(pred_in - actual_ara4)
                    errors_inscribed.append(err_in)
                if pred_out is not None:
                    err_out = abs(pred_out - actual_ara4)
                    errors_circumscribed.append(err_out)
                log(f'    rungs {r1},{r2},{r3} → predict ARA at {r4}:')
                log(f'      actual ARA  = {actual_ara4:.3f}')
                if pred_in is not None:  log(f'      inscribed   = {pred_in:.3f}  (err {abs(pred_in-actual_ara4):.3f})')
                if pred_out is not None: log(f'      circumscribed = {pred_out:.3f}  (err {abs(pred_out-actual_ara4):.3f})')
        
        if errors_inscribed:
            log(f'    MAE (inscribed):   {np.mean(errors_inscribed):.3f}')
        if errors_circumscribed:
            log(f'    MAE (circumscribed): {np.mean(errors_circumscribed):.3f}')

test_descartes(ara_mouse, 'mouse')
test_descartes(ara_human, 'human')

log('\n=== Done ===')

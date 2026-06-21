"""apollonian_descartes_test_v2.py — Dylan 2026-05-12.

V2 fix: bandpass forces ARA toward symmetry, so v1's ara-as-curvature test was
trivially satisfied (all curvatures near 0). V2 uses per-rung AMPLITUDE as
curvature — bigger amplitude = bigger circle = smaller curvature. This IS
the natural geometric mapping.

Test: do measured per-rung amplitudes satisfy Descartes' Circle Theorem?
"""
import os, glob, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt

PHI = (1+5**0.5)/2
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
def log(s): print(s, flush=True)

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
log(f'Mouse: {len(mouse_rr)} beats, Human: {len(human_rr)} beats')

def per_rung_amplitude(rr, periods):
    """Bandpass at each period, return std (proxy for amplitude/size of the cycle at that rung)."""
    amps = {}
    for P in periods:
        low = 1.0 / (P * 1.4); high = 1.0 / (P * 0.7)
        nyq = 0.5
        lo, hi = max(0.001, low/nyq), min(0.999, high/nyq)
        if lo >= hi: continue
        try:
            sos = butter(4, [lo, hi], btype='band', output='sos')
            f = sosfiltfilt(sos, rr)
            if np.std(f) < 1e-9: continue
            amps[P] = float(np.std(f))
        except: pass
    return amps

FIB = [3, 5, 8, 13, 21, 34, 55, 89]
amp_mouse = per_rung_amplitude(mouse_rr, FIB)
amp_human = per_rung_amplitude(human_rr, FIB)
log(f'\nMouse per-rung amplitudes (std of bandpass):')
for P, a in amp_mouse.items(): log(f'  P={P:3d}: amp={a:8.3f}  curvature(1/amp)={1/a:.5f}')
log(f'\nHuman per-rung amplitudes:')
for P, a in amp_human.items(): log(f'  P={P:3d}: amp={a:8.3f}  curvature(1/amp)={1/a:.5f}')

def descartes_predict(k1, k2, k3):
    s = k1 + k2 + k3
    p = k1*k2 + k2*k3 + k3*k1
    if p < 0: return (None, None)
    sq = 2 * math.sqrt(p)
    return (s + sq, s - sq)

def test(amps, label):
    log(f'\n=== Descartes on {label} (curvature = 1/amplitude) ===')
    rungs = sorted(amps.keys())
    if len(rungs) < 4: log('  Not enough rungs.'); return
    
    pred_in_list, pred_out_list, actual_list = [], [], []
    log(f'  rungs (P)  | predict amp at next rung | actual amp | err inscribed | err circumscribed')
    log('  ' + '-'*92)
    for i in range(len(rungs) - 3):
        r1, r2, r3, r4 = rungs[i:i+4]
        k1, k2, k3 = 1/amps[r1], 1/amps[r2], 1/amps[r3]
        k4_in, k4_out = descartes_predict(k1, k2, k3)
        actual_amp = amps[r4]
        actual_k4 = 1/actual_amp
        if k4_in and k4_in > 0:
            pred_amp_in = 1/k4_in
            err_in = abs(pred_amp_in - actual_amp) / actual_amp * 100
            pred_in_list.append(pred_amp_in); actual_list.append(actual_amp)
        else:
            pred_amp_in = None; err_in = None
        if k4_out and k4_out > 0:
            pred_amp_out = 1/k4_out
            err_out = abs(pred_amp_out - actual_amp) / actual_amp * 100
            pred_out_list.append(pred_amp_out)
        elif k4_out and k4_out < 0:
            pred_amp_out = None  # negative curvature = encloses; doesn't make physical sense as amplitude
            err_out = None
        else:
            pred_amp_out = None; err_out = None
        log(f'  {r1:2d},{r2:2d},{r3:2d}→{r4:3d} | inscribed={pred_amp_in if pred_amp_in else "—"!s:>15}  circ={pred_amp_out if pred_amp_out else "—"!s:>15} | actual={actual_amp:7.3f} | err_in={err_in if err_in else "—"!s:>6}%   err_out={err_out if err_out else "—"!s:>6}%')
    
    if pred_in_list:
        log(f'  Mean MAE-pct (inscribed):    {np.mean([abs(p-a)/a*100 for p,a in zip(pred_in_list, actual_list)]):.1f}%')
        if len(pred_in_list) > 2:
            r = float(np.corrcoef(pred_in_list, actual_list)[0,1])
            log(f'  Corr(predicted, actual):     {r:+.3f}')

test(amp_mouse, 'mouse')
test(amp_human, 'human')

# What does PURE φ-spaced amplitude predict? Compare to baseline
log('\n=== Baseline: φ-rung naive prediction (amp scales as φ^k) ===')
def test_phi_baseline(amps, label):
    rungs = sorted(amps.keys())
    if len(rungs) < 4: return
    log(f'\n  {label}:')
    errs = []
    for i in range(len(rungs) - 3):
        r1, r2, r3, r4 = rungs[i:i+4]
        # Estimate φ scaling factor between r3 and r4
        amp_r3 = amps[r3]
        # If amplitude scales as φ^k where k changes by log_φ(P_4/P_3) between rungs
        rung_step = math.log(r4/r3) / math.log(PHI)
        pred = amp_r3 * (PHI ** rung_step)
        actual = amps[r4]
        err = abs(pred - actual) / actual * 100
        errs.append(err)
        log(f'    {r3}→{r4}: predicted {pred:.3f}, actual {actual:.3f}, err {err:.1f}%')
    log(f'    Mean MAE-pct (φ baseline): {np.mean(errs):.1f}%')

test_phi_baseline(amp_mouse, 'mouse')
test_phi_baseline(amp_human, 'human')

log('\n=== Done ===')

"""gear_test2_cross_rung_power.py — Dylan 2026-05-12.

Test 2 from framework_gear_mechanics_anchor.md:
For vertical-ARA pairs (mouse ↔ human cardiac), gear-law power conservation
predicts: ω_m × τ_m = ω_h × τ_h.

With ω = 1/T (angular velocity ∝ 1/period) and τ ∝ amplitude (torque proxy),
this becomes: amplitude/period should be equal across paired gears.

Equivalently: (amp_h / amp_m) × (T_m / T_h) = 1.

Test multiple torque proxies to see which (if any) holds:
  - τ ∝ amplitude       → check amp/T conserved
  - τ ∝ amplitude²      → check amp²/T conserved (kinetic-energy-like)
  - τ ∝ amplitude × T   → check amplitude conserved (no period factor)
"""
import os, glob, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt

PHI = (1+5**0.5)/2
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
def log(s): print(s, flush=True)

# ============================================================================
# Load mouse + human RR
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

T_m = float(mouse_rr.mean())  # mean mouse period in ms
T_h = float(human_rr.mean())  # mean human period in ms
gear_ratio = T_h / T_m  # human gear is gear_ratio times bigger than mouse
log(f'Mouse: {len(mouse_rr)} beats, T_m = {T_m:.1f} ms')
log(f'Human: {len(human_rr)} beats, T_h = {T_h:.1f} ms')
log(f'Gear ratio T_h/T_m = {gear_ratio:.3f}')
log(f'φ-rung difference = log_φ({gear_ratio:.2f}) = {math.log(gear_ratio)/math.log(PHI):.2f}')

# ============================================================================
# Per-rung amplitude
# ============================================================================
def amp_at_period(rr, P_beats):
    low = 1/(P_beats*1.4); high = 1/(P_beats*0.7); nyq = 0.5
    lo, hi = max(0.001, low/nyq), min(0.999, high/nyq)
    if lo >= hi: return None
    try:
        sos = butter(4, [lo, hi], btype='band', output='sos')
        f = sosfiltfilt(sos, rr)
        return float(np.std(f)) if np.std(f) > 1e-9 else None
    except: return None

# Use Fibonacci periods in BEATS (so we measure same beat-relative rungs on each species)
# A rung at P beats corresponds to physical period P × T_m (mouse) or P × T_h (human).
# Same rung index but at species-natural timescale.
RUNG_BEATS = [3, 5, 8, 13, 21, 34, 55, 89]

log(f'\n=== TEST 2: Gear-law cross-rung power conservation (mouse ↔ human cardiac) ===')
log(f'Each rung is measured at the same beat-relative period in each species.')
log(f'Mouse rung P_beats×T_m, Human rung P_beats×T_h, gear ratio = T_h/T_m for ALL rungs.\n')

log(f'{"P (beats)":>10} | {"mouse amp":>10} | {"human amp":>10} | {"amp_h/amp_m":>12} | {"gear ratio":>11} | {"prod amp×T":>12} | {"deviation":>10}')
log('-' * 95)

results = []
for P in RUNG_BEATS:
    a_m = amp_at_period(mouse_rr, P)
    a_h = amp_at_period(human_rr, P)
    if a_m is None or a_h is None: continue
    
    amp_ratio = a_h / a_m  # human-to-mouse amplitude
    # Gear-law prediction (power conservation, torque ∝ amplitude):
    # ω_m × amp_m = ω_h × amp_h → amp_h/amp_m = ω_m/ω_h = T_h/T_m = gear_ratio
    # So amp_h / amp_m should equal gear_ratio
    
    # Equivalently: (amp_h × T_m) / (amp_m × T_h) = 1
    # Or: amp/T should be conserved
    mouse_power = a_m / (P * T_m / 1000)  # amp/period in real time units
    human_power = a_h / (P * T_h / 1000)
    power_ratio = human_power / mouse_power
    
    deviation_from_1 = abs(amp_ratio / gear_ratio - 1.0)
    log(f'{P:>10d} | {a_m:>10.4f} | {a_h:>10.4f} | {amp_ratio:>12.3f} | {gear_ratio:>11.3f} | {power_ratio:>12.3f} | {deviation_from_1:>10.3f}')
    results.append({'P': P, 'amp_m': a_m, 'amp_h': a_h, 'amp_ratio': amp_ratio, 'power_ratio': power_ratio, 'dev': deviation_from_1})

if results:
    amp_ratios = [r['amp_ratio'] for r in results]
    power_ratios = [r['power_ratio'] for r in results]
    devs = [r['dev'] for r in results]
    
    log(f'\n=== VERDICT ===')
    log(f'Gear ratio T_h/T_m              = {gear_ratio:.3f}')
    log(f'Mean amp_h/amp_m measured       = {np.mean(amp_ratios):.3f}')
    log(f'Median amp_h/amp_m              = {np.median(amp_ratios):.3f}')
    log(f'')
    log(f'GEAR-LAW prediction (τ ∝ amp): amp_h/amp_m should equal gear_ratio ({gear_ratio:.2f})')
    log(f'  Mean deviation |amp_ratio / gear_ratio − 1| = {np.mean(devs):.3f}')
    if np.mean(devs) < 0.2:
        log(f'  ✓ STRONG fit: amplitude ratio matches gear ratio')
    elif np.mean(devs) < 0.5:
        log(f'  ~ MODERATE fit')
    else:
        log(f'  ✗ POOR fit: amplitude is not the right torque proxy')
    log(f'')
    log(f'Power ratio (amp/T): {np.mean(power_ratios):.3f}  (should be 1.0 if amp/T is the conserved quantity)')
    log(f'')
    
    # Alternative torque proxies
    log(f'--- Alternative torque proxies ---')
    log(f'If τ ∝ amp²: human amp² × T_m / (mouse amp² × T_h) = {(np.mean([r["amp_h"]**2 for r in results]) * T_m) / (np.mean([r["amp_m"]**2 for r in results]) * T_h):.3f}')
    log(f'If τ ∝ amp × T: human amp × T_h / (mouse amp × T_m) = {(np.mean([r["amp_h"] for r in results]) * T_h) / (np.mean([r["amp_m"] for r in results]) * T_m):.3f}')
    log(f'If τ ∝ amp (no T factor): human amp / mouse amp = {np.mean(amp_ratios):.3f}')
    log(f'')
    log(f'Pure φ-rung-difference prediction: amplitude scales as φ^Δrung where Δrung = log_φ(T_h/T_m) ≈ {math.log(gear_ratio)/math.log(PHI):.2f}')
    log(f'  Predicted amp_h / amp_m = φ^{math.log(gear_ratio)/math.log(PHI):.2f} = {PHI**(math.log(gear_ratio)/math.log(PHI)):.3f} ({gear_ratio:.3f})')

log('\n=== Done ===')

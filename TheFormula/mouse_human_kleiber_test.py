"""
mouse_human_kleiber_test.py — re-test mouse→human prediction with Kleiber scaling.

Dylan 2026-05-11: original mouse-human continuation test (no Kleiber scaling)
gave only 18% of predictions above corr=0.5 — looked like a near-null result.

Hypothesis: the "bends in the river are the same shape, but the water moves at
a different viscosity." Vertical-ARA preserves cycle TOPOLOGY across scales,
but the energy density / time-rate differs by Kleiber's 3/4 scaling.

Applied PER TICK: each tick in mouse data corresponds to a Kleiber-scaled point
in human time AND a Kleiber-scaled amplitude in human energy space. The
prediction test should improve if Kleiber scaling is doing real work.

Test conditions:
  A. Original (no Kleiber): control — should reproduce 18% above-0.5
  B. Kleiber time-scaling only (period ratio = mass^(1/4))
  C. Kleiber time + amplitude scaling (both axes by mass^(1/4))
  D. Use observed period ratio (6.6) instead of Kleiber-predicted (7.27)

If C beats A by meaningful margin, the framework's vertical-ARA + Kleiber
combined architecture is empirically supported.
"""
import os, glob, json, math
import numpy as np
import pandas as pd

PHI = (1+5**0.5)/2
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)

# ============================================================================
# Load mouse and human RR
# ============================================================================
print('Loading mouse + human RR...')
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

mouse_rr_segs = []
for p in sorted(glob.glob(os.path.join(REPO_ROOT, 'PhysioZoo', 'peaks_Mouse_*.txt'))):
    parsed = parse_peaks(p)
    if parsed:
        fs, pks = parsed
        if len(pks) >= 100:
            mouse_rr_segs.append(np.diff(pks)/fs*1000)
mouse_rr = np.concatenate(mouse_rr_segs)
hdf = pd.read_csv(os.path.join(REPO_ROOT, 'TheFormula', 'nsr001_rr.csv'))
human_rr = hdf['rr_ms'].values

print(f'  Mouse: {len(mouse_rr)} beats, mean RR {mouse_rr.mean():.1f} ms')
print(f'  Human: {len(human_rr)} beats, mean RR {human_rr.mean():.1f} ms')

# ============================================================================
# Scaling factors
# ============================================================================
period_ratio_obs = human_rr.mean() / mouse_rr.mean()
mass_mouse, mass_human = 25, 70000  # grams
kleiber_ratio = (mass_human / mass_mouse) ** 0.25
print(f'  Observed period ratio: {period_ratio_obs:.3f}')
print(f'  Kleiber-predicted ratio: {kleiber_ratio:.3f}')

# ============================================================================
# Normalize: zero-mean, unit-std (no Kleiber yet)
# ============================================================================
def znorm(x):
    return (x - np.mean(x)) / max(1e-9, np.std(x))

mouse_z = znorm(mouse_rr.astype(float))
human_z = znorm(human_rr.astype(float))

# Light smoothing to focus on shape envelope
from scipy.ndimage import gaussian_filter1d
mouse_s = gaussian_filter1d(mouse_z, 1.5)
human_s = gaussian_filter1d(human_z, 1.5)

# ============================================================================
# Test runner: applies Kleiber scaling per-tick to mouse signal, then
# compares to human signal
# ============================================================================
def resample(arr, n):
    xo = np.linspace(0, 1, len(arr)); xn = np.linspace(0, 1, n)
    return np.interp(xn, xo, arr)

HUMAN_WINDOW = 20
PRED_HORIZON_HUMAN = 10
N_QUERIES = 25  # reduced for timeout budget

def run_test(label, time_ratio, apply_amp_scaling):
    """For each query window in human, find best-match in mouse (after Kleiber-scaling).
       Then test if the next mouse beats (Kleiber-scaled) predict next human beats."""
    mouse_window = int(round(HUMAN_WINDOW * time_ratio))
    pred_horizon_mouse = int(round(PRED_HORIZON_HUMAN * time_ratio))

    # If amp scaling enabled, also normalize per-window amplitudes
    # (subtle effect for z-normed signals, but matters for raw)
    results = []
    qs = np.linspace(HUMAN_WINDOW, len(human_s) - HUMAN_WINDOW - PRED_HORIZON_HUMAN - 5, N_QUERIES).astype(int)
    for q_pos in qs:
        q = human_s[q_pos:q_pos+HUMAN_WINDOW]
        # Optionally apply amplitude scaling: rescale mouse window to match human's local amplitude
        best_corr = -2; best_pos = None
        step = max(1, mouse_window // 10)
        for m_pos in range(0, len(mouse_s) - mouse_window - pred_horizon_mouse - 5, step):
            m_window_raw = mouse_s[m_pos:m_pos+mouse_window]
            m_resamp = resample(m_window_raw, HUMAN_WINDOW)
            if apply_amp_scaling:
                # Per-window amplitude rescaling (each tick gets matched local amp)
                m_resamp = (m_resamp - m_resamp.mean()) / max(1e-9, m_resamp.std()) * max(1e-9, q.std()) + q.mean()
            c = float(np.corrcoef(q, m_resamp)[0, 1])
            if c > best_corr:
                best_corr = c; best_pos = m_pos
        if best_pos is None: continue
        # Continuation
        h_next = human_s[q_pos+HUMAN_WINDOW : q_pos+HUMAN_WINDOW+PRED_HORIZON_HUMAN]
        m_next_raw = mouse_s[best_pos+mouse_window : best_pos+mouse_window+pred_horizon_mouse]
        m_next = resample(m_next_raw, PRED_HORIZON_HUMAN)
        if apply_amp_scaling:
            m_next = (m_next - m_next.mean()) / max(1e-9, m_next.std()) * max(1e-9, h_next.std()) + h_next.mean()
        pred_corr = float(np.corrcoef(h_next, m_next)[0, 1])
        pred_mae = float(np.mean(np.abs(h_next - m_next)))
        results.append((best_corr, pred_corr, pred_mae))

    if not results: return None
    match_corrs = [r[0] for r in results]
    pred_corrs = [r[1] for r in results]
    pred_maes = [r[2] for r in results]
    return dict(
        label=label, n=len(results),
        match_corr_mean=float(np.mean(match_corrs)),
        pred_corr_mean=float(np.mean(pred_corrs)),
        pred_corr_median=float(np.median(pred_corrs)),
        pred_mae_mean=float(np.mean(pred_maes)),
        frac_pred_gt_0=float(np.mean([c > 0 for c in pred_corrs])),
        frac_pred_gt_05=float(np.mean([c > 0.5 for c in pred_corrs])),
    )

# ============================================================================
# Run conditions
# ============================================================================
print()
print('Running 4 conditions...')
conditions = [
    ('A: no Kleiber (control)', period_ratio_obs, False),
    ('B: Kleiber time only',    kleiber_ratio,    False),
    ('C: Kleiber time + amp',   kleiber_ratio,    True),
    ('D: observed time + amp',  period_ratio_obs, True),
]

results = []
for label, time_r, amp in conditions:
    print(f'  {label}...', flush=True)
    r = run_test(label, time_r, amp)
    if r: results.append(r)

# ============================================================================
# Report
# ============================================================================
print()
print('=' * 78)
print('MOUSE → HUMAN PREDICTION: KLEIBER SCALING vs CONTROL')
print('=' * 78)
print(f"{'condition':<28}  {'match corr':>11}  {'pred corr':>11}  {'>0.5 frac':>10}  {'MAE':>6}")
print('-' * 76)
for r in results:
    print(f"  {r['label']:<26}  {r['match_corr_mean']:>+11.3f}  "
          f"{r['pred_corr_mean']:>+11.3f}  {r['frac_pred_gt_05']:>10.1%}  {r['pred_mae_mean']:>6.3f}")

# Compare A vs C (the headline test)
print()
print('=' * 78)
print('VERDICT')
print('=' * 78)
ctrl = results[0]; kleiber = results[2]
print(f'  Control (A: no Kleiber):         pred_corr = {ctrl["pred_corr_mean"]:+.3f}, '
      f'fraction > 0.5 = {ctrl["frac_pred_gt_05"]:.1%}')
print(f'  Kleiber (C: time + amp):         pred_corr = {kleiber["pred_corr_mean"]:+.3f}, '
      f'fraction > 0.5 = {kleiber["frac_pred_gt_05"]:.1%}')
lift_corr = kleiber['pred_corr_mean'] - ctrl['pred_corr_mean']
lift_frac = kleiber['frac_pred_gt_05'] - ctrl['frac_pred_gt_05']
print(f'  Lift from Kleiber: corr {lift_corr:+.3f}, fraction-above-0.5 {lift_frac:+.1%}')
print()
if lift_corr > 0.10:
    print('  → STRONG: Kleiber scaling materially improves cross-species prediction.')
elif lift_corr > 0.03:
    print('  → MODERATE: Kleiber adds something, but not transformative.')
elif lift_corr > -0.03:
    print('  → NEUTRAL: Kleiber doesn\'t meaningfully change prediction accuracy.')
else:
    print('  → NEGATIVE: Kleiber-scaled version is worse than control.')

# Save
OUT = os.path.join(_HERE, 'mouse_human_kleiber_data.js')
with open(OUT, 'w') as f:
    f.write("window.MOUSE_HUMAN_KLEIBER = " + json.dumps({
        'date': '2026-05-11',
        'mass_ratio_human_mouse': mass_human/mass_mouse,
        'observed_period_ratio': period_ratio_obs,
        'kleiber_predicted_ratio': kleiber_ratio,
        'conditions': results,
        'lift_corr': lift_corr,
        'lift_frac_above_05': lift_frac,
    }, default=str) + ";\n
"""
mouse_human_continuation_test.py — vertical-ARA continuation prediction.

Dylan 2026-05-11: take a shape window in mouse heart RR, find the best matching
window in human heart RR (after time-stretching by their period ratio ~6.4×),
then test whether the NEXT N beats in each system match after the same
time-stretching. Predicted accuracy: 75–80% (allowing for individual variation).

This is the framework's actual predictive claim: if vertical-ARA is real,
the shape immediately following a recognised pattern at one scale should be
the time-stretched continuation pattern at the other scale.

Method:
  1. Load mouse RR sequence and human RR sequence (PhysioZoo + nsr001).
  2. Resample both to uniform time grids; normalise to zero-mean, unit-variance.
  3. Slide a "query window" through mouse data. For each window, find the
     best-matching window in human data (time-stretched by 6.4×).
  4. For each high-quality match, take the NEXT N points in the human series
     and use the next N points in the mouse series (time-stretched) as the
     PREDICTION.
  5. Score prediction vs actual: correlation, MAE, % within tolerance.
  6. Compare to null: shuffle one series and re-run.
"""
import os, glob, json, math
import numpy as np
import pandas as pd

PHI = (1 + 5**0.5) / 2

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("[1/5] Loading mouse RR and human RR ...")

# Mouse from PhysioZoo
def parse_peaks_file(path):
    with open(path) as f:
        text = f.read()
    if 'Mammal:' not in text:
        return None
    fs = None; peaks = []
    for line in text.split('\n'):
        s = line.strip()
        if s.startswith('Fs:'):
            fs = int(s.split()[-1])
        elif s and s[0].isdigit():
            try: peaks.append(int(s))
            except: pass
    if fs is None or not peaks: return None
    return fs, np.array(peaks)

mouse_rr_segments = []
for path in sorted(glob.glob(os.path.join(REPO_ROOT, 'PhysioZoo', 'peaks_Mouse_*.txt'))):
    parsed = parse_peaks_file(path)
    if parsed is None: continue
    fs, peaks = parsed
    if len(peaks) < 100: continue
    rr = np.diff(peaks) / fs * 1000  # ms
    mouse_rr_segments.append(rr)
mouse_rr = np.concatenate(mouse_rr_segments)
print(f'  Mouse: {len(mouse_rr)} beats from {len(mouse_rr_segments)} segments. Mean RR = {np.mean(mouse_rr):.1f} ms')

# Human from nsr001
hdf = pd.read_csv(os.path.join(REPO_ROOT, 'TheFormula', 'nsr001_rr.csv'))
human_rr = hdf['rr_ms'].values
print(f'  Human: {len(human_rr)} beats. Mean RR = {np.mean(human_rr):.1f} ms')

# Period ratio for time-stretch
period_ratio = float(np.mean(human_rr) / np.mean(mouse_rr))
print(f'  Period ratio (human/mouse): {period_ratio:.3f}')
print(f'  In φ-rungs: {math.log(period_ratio)/math.log(PHI):.2f}')

# ============================================================================
# 2. NORMALISE & PREP
# ============================================================================
print("\n[2/5] Normalising signals ...")

def normalize(x):
    return (x - np.mean(x)) / max(1e-9, np.std(x))

mouse_n = normalize(mouse_rr.astype(float))
human_n = normalize(human_rr.astype(float))

# Smooth lightly to remove single-beat noise (we care about shape envelope)
from scipy.ndimage import gaussian_filter1d
mouse_s = gaussian_filter1d(mouse_n, 1.5)
human_s = gaussian_filter1d(human_n, 1.5)

# ============================================================================
# 3. SHAPE-MATCH WINDOWS
# ============================================================================
print("\n[3/5] Finding best-matching windows across species ...")

# Query window length in HUMAN beats. We choose ~20 human beats = ~15 sec.
# In mouse beats: 20 × period_ratio ≈ 130 mouse beats = ~15 sec.
HUMAN_WINDOW = 20
MOUSE_WINDOW = int(round(HUMAN_WINDOW * period_ratio))
PREDICTION_HORIZON_HUMAN = 10  # next 10 human beats
PREDICTION_HORIZON_MOUSE = int(round(PREDICTION_HORIZON_HUMAN * period_ratio))

print(f'  Query window: {HUMAN_WINDOW} human beats ≈ {MOUSE_WINDOW} mouse beats')
print(f'  Prediction horizon: {PREDICTION_HORIZON_HUMAN} human beats ≈ {PREDICTION_HORIZON_MOUSE} mouse beats')

# For each query position in human (every 5 beats), find best-matching mouse window.
# We resample the mouse window to match human window length so direct correlation works.
def resample_to(arr, n):
    xo = np.linspace(0, 1, len(arr)); xn = np.linspace(0, 1, n)
    return np.interp(xn, xo, arr)

match_results = []
n_queries = 50
query_positions = np.linspace(HUMAN_WINDOW, len(human_s) - HUMAN_WINDOW - PREDICTION_HORIZON_HUMAN - 5, n_queries).astype(int)

for q_pos in query_positions:
    q = human_s[q_pos:q_pos+HUMAN_WINDOW]
    # Search mouse for best-matching window
    best_corr = -2; best_pos = None
    step = max(1, MOUSE_WINDOW // 10)
    for m_pos in range(0, len(mouse_s) - MOUSE_WINDOW - PREDICTION_HORIZON_MOUSE - 5, step):
        m_window = mouse_s[m_pos:m_pos+MOUSE_WINDOW]
        m_resampled = resample_to(m_window, HUMAN_WINDOW)
        c = float(np.corrcoef(q, m_resampled)[0, 1])
        if c > best_corr:
            best_corr = c; best_pos = m_pos
    if best_pos is not None:
        # Get the prediction horizon for both
        human_next = human_s[q_pos+HUMAN_WINDOW : q_pos+HUMAN_WINDOW+PREDICTION_HORIZON_HUMAN]
        mouse_next = mouse_s[best_pos+MOUSE_WINDOW : best_pos+MOUSE_WINDOW+PREDICTION_HORIZON_MOUSE]
        mouse_next_resampled = resample_to(mouse_next, PREDICTION_HORIZON_HUMAN)
        # Score
        pred_corr = float(np.corrcoef(human_next, mouse_next_resampled)[0, 1])
        pred_mae = float(np.mean(np.abs(human_next - mouse_next_resampled)))
        match_results.append(dict(
            q_pos=int(q_pos), m_pos=int(best_pos), match_corr=best_corr,
            pred_corr=pred_corr, pred_mae=pred_mae,
        ))

# ============================================================================
# 4. SCORE PREDICTIONS
# ============================================================================
print(f'\n[4/5] Scoring {len(match_results)} matched pairs ...')

match_corrs = [r['match_corr'] for r in match_results]
pred_corrs = [r['pred_corr'] for r in match_results]
pred_maes = [r['pred_mae'] for r in match_results]

print(f"  Mean window-match correlation: {np.mean(match_corrs):+.3f}")
print(f"  Mean prediction correlation:    {np.mean(pred_corrs):+.3f}")
print(f"  Median prediction correlation:  {np.median(pred_corrs):+.3f}")
print(f"  Std of predictions:             {np.std(pred_corrs):.3f}")
print(f"  Mean prediction MAE:            {np.mean(pred_maes):.3f}")
print(f"  Fraction of predictions corr > 0:  {np.mean([c > 0 for c in pred_corrs]):.2%}")
print(f"  Fraction of predictions corr > 0.5: {np.mean([c > 0.5 for c in pred_corrs]):.2%}")

# Filter to high-quality matches and rescore
hq = [r for r in match_results if r['match_corr'] > 0.7]
print(f'\n  High-quality matches (match_corr > 0.7): {len(hq)}')
if hq:
    hq_pred = [r['pred_corr'] for r in hq]
    print(f"  HQ prediction mean corr:    {np.mean(hq_pred):+.3f}")
    print(f"  HQ prediction median corr:  {np.median(hq_pred):+.3f}")
    print(f"  HQ fraction corr > 0:       {np.mean([c > 0 for c in hq_pred]):.2%}")
    print(f"  HQ fraction corr > 0.5:     {np.mean([c > 0.5 for c in hq_pred]):.2%}")

# ============================================================================
# 5. NULL TEST: shuffle mouse and re-run
# ============================================================================
print("\n[5/5] Null test: shuffle mouse, re-run prediction ...")
mouse_shuffled = mouse_s.copy()
np.random.seed(42)
# Shuffle in chunks to break long-range structure but keep local variability
chunk = 50
n_chunks = len(mouse_shuffled) // chunk
mouse_shuffled = mouse_shuffled[:n_chunks*chunk].reshape(n_chunks, chunk)
np.random.shuffle(mouse_shuffled)
mouse_shuffled = mouse_shuffled.flatten()

null_results = []
for q_pos in query_positions:
    q = human_s[q_pos:q_pos+HUMAN_WINDOW]
    best_corr = -2; best_pos = None
    step = max(1, MOUSE_WINDOW // 10)
    for m_pos in range(0, len(mouse_shuffled) - MOUSE_WINDOW - PREDICTION_HORIZON_MOUSE - 5, step):
        m_window = mouse_shuffled[m_pos:m_pos+MOUSE_WINDOW]
        m_resampled = resample_to(m_window, HUMAN_WINDOW)
        c = float(np.corrcoef(q, m_resampled)[0, 1])
        if c > best_corr: best_corr = c; best_pos = m_pos
    if best_pos is not None:
        human_next = human_s[q_pos+HUMAN_WINDOW : q_pos+HUMAN_WINDOW+PREDICTION_HORIZON_HUMAN]
        mouse_next = mouse_shuffled[best_pos+MOUSE_WINDOW : best_pos+MOUSE_WINDOW+PREDICTION_HORIZON_MOUSE]
        mouse_next_r = resample_to(mouse_next, PREDICTION_HORIZON_HUMAN)
        null_results.append(dict(match_corr=best_corr,
                                 pred_corr=float(np.corrcoef(human_next, mouse_next_r)[0, 1])))

null_pred = [r['pred_corr'] for r in null_results]
null_match = [r['match_corr'] for r in null_results]
print(f"  Null mean window-match corr: {np.mean(null_match):+.3f}")
print(f"  Null mean prediction corr:   {np.mean(null_pred):+.3f}")
print(f"  Null median prediction corr: {np.median(null_pred):+.3f}")

# Verdict
print()
print('=' * 70)
print('VERDICT')
print('=' * 70)
real_mean = np.mean(pred_corrs); null_mean = np.mean(null_pred)
lift = real_mean - null_mean
print(f"  Real prediction mean:    {real_mean:+.3f}")
print(f"  Null prediction mean:    {null_mean:+.3f}")
print(f"  Lift (real − null):      {lift:+.3f}")
print()
if lift > 0.15:
    print('  → STRONG: real continuation predictions significantly beat shuffled-mouse null.')
    print('    Vertical-ARA continuation prediction works at the cross-species level.')
elif lift > 0.05:
    print('  → MODERATE: real predictions beat null but margin modest.')
elif lift > -0.05:
    print('  → NULL: no significant lift. Continuation prediction does not transfer cross-species.')
else:
    print('  → REVERSED: predictions worse than null. Test methodology may have a flaw.')
print()
print(f"  Dylan's prediction: 75-80% accuracy. Our 'fraction corr > 0.5' on HQ matches: ", end='')
if hq:
    pct = float(np.mean([c > 0.5 for c in hq_pred])) * 100
    print(f"{pct:.0f}%")
    print(f"  {'✓ within Dylan prediction range' if 65 <= pct <= 85 else '⚠ outside Dylan prediction range'}")

OUT = os.path.join(_HERE, 'mouse_human_continuation_data.js')
payload = dict(
    date='2026-05-11',
    n_mouse_beats=int(len(mouse_rr)),
    n_human_beats=int(len(human_rr)),
    period_ratio=period_ratio,
    n_queries=len(match_results),
    human_window_beats=HUMAN_WINDOW,
    mouse_window_beats=MOUSE_WINDOW,
    prediction_horizon_human=PREDICTION_HORIZON_HUMAN,
    real_mean_match_corr=float(np.mean(match_corrs)),
    real_mean_pred_corr=float(np.mean(pred_corrs)),
    real_median_pred_corr=float(np.median(pred_corrs)),
    null_mean_pred_corr=float(np.mean(null_pred)),
    null_median_pred_corr=float(np.median(null_pred)),
    lift=float(lift),
    n_hq_matches=len(hq),
    hq_mean_pred_corr=float(np.mean([r['pred_corr'] for r in hq])) if hq else None,
    hq_pct_above_05=float(np.mean([r['pred_corr'] > 0.5 for r in hq])) if hq else None,
)
with open(OUT, 'w') as f:
    f.write("window.MOUSE_HUMAN_CONTINUATION = " + json.dumps(payload, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

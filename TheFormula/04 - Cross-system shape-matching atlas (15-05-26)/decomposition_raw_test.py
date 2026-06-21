"""decomposition_raw_test.py — Dylan 2026-05-12 follow-up. No smoothing/averaging."""
import os, glob, json, math
import numpy as np
import pandas as pd

PHI = (1+5**0.5)/2
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
OUT_PATH = os.path.join(_HERE, 'decomposition_raw_data.js')

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

period_ratio_obs = human_rr.mean() / mouse_rr.mean()
rung_diff = math.log(period_ratio_obs) / math.log(PHI)
phi_scale = PHI ** rung_diff
print(f'  Observed period ratio: {period_ratio_obs:.3f}')
print(f'  Phi rung difference:   {rung_diff:.3f}')

LANDMARK_LEN = 7
ONE_MIN_MOUSE = 545
ONE_MIN_HUMAN = int(60 * 1000 / human_rr.mean())
print(f'  Mouse 1-min window:    {ONE_MIN_MOUSE} beats')
print(f'  Human equivalent:      ~{ONE_MIN_HUMAN} beats')

def znorm(x):
    s = np.std(x)
    return (x - np.mean(x)) / max(1e-9, s)

print('Searching for best human<->mouse landmark match...')
MIN_RANGE_MOUSE = 8
MIN_RANGE_HUMAN = 25

HUMAN_STRIDE = max(1, len(human_rr) // 400)
MOUSE_STRIDE = max(1, len(mouse_rr) // 400)
best = {'corr': -2, 'h_idx': None, 'm_idx': None}

h_starts = list(range(0, len(human_rr) - LANDMARK_LEN - ONE_MIN_HUMAN - 5, HUMAN_STRIDE))
m_starts = list(range(0, len(mouse_rr) - LANDMARK_LEN - ONE_MIN_MOUSE - 5, MOUSE_STRIDE))

h_filtered = []
for hi in h_starts:
    w = human_rr[hi:hi+LANDMARK_LEN].astype(float)
    if (w.max() - w.min()) >= MIN_RANGE_HUMAN:
        h_filtered.append((hi, znorm(w)))
m_filtered = []
for mi in m_starts:
    w = mouse_rr[mi:mi+LANDMARK_LEN].astype(float)
    if (w.max() - w.min()) >= MIN_RANGE_MOUSE:
        m_filtered.append((mi, znorm(w)))

print(f'  After range filter: {len(h_filtered)} human, {len(m_filtered)} mouse')

for hi, h_z in h_filtered:
    for mi, m_z in m_filtered:
        c = float(np.corrcoef(h_z, m_z)[0, 1])
        if c > best['corr']:
            best['corr'] = c
            best['h_idx'] = hi
            best['m_idx'] = mi

print(f"  Best landmark match: corr {best['corr']:.4f}")
print(f"    human start beat: {best['h_idx']}")
print(f"    mouse start beat: {best['m_idx']}")

h_idx = best['h_idx']
m_idx = best['m_idx']

human_landmark = human_rr[h_idx : h_idx + LANDMARK_LEN].astype(float)
mouse_landmark = mouse_rr[m_idx : m_idx + LANDMARK_LEN].astype(float)
human_anchor = float(human_landmark[-1])
mouse_anchor = float(mouse_landmark[-1])

mouse_cont = mouse_rr[m_idx + LANDMARK_LEN : m_idx + LANDMARK_LEN + ONE_MIN_MOUSE].astype(float)
human_actual = human_rr[h_idx + LANDMARK_LEN : h_idx + LANDMARK_LEN + ONE_MIN_HUMAN].astype(float)

print(f'  human anchor: {human_anchor:.1f}  mouse anchor: {mouse_anchor:.1f}')
print(f'  mouse cont: {len(mouse_cont)}  human actual: {len(human_actual)}')

mouse_lm_range = float(mouse_landmark.max() - mouse_landmark.min())
human_lm_range = float(human_landmark.max() - human_landmark.min())

mouse_times = np.cumsum(mouse_cont)
human_times = np.arange(1, len(human_actual)+1) * human_rr.mean()
mouse_at_human_times = np.interp(human_times, mouse_times, mouse_cont)
mouse_series_for_steps = np.concatenate([[mouse_anchor], mouse_at_human_times])

# Method A — Ratio
pred_A = human_anchor * (mouse_at_human_times / mouse_anchor)

# Method C — Multiplicative step
mult_steps = mouse_series_for_steps[1:] / mouse_series_for_steps[:-1]
pred_C = np.empty_like(human_actual)
prev = human_anchor
for k in range(len(pred_C)):
    prev = prev * mult_steps[k]
    pred_C[k] = prev

# Method D — Phi-scaled additive deltas
mouse_deltas = mouse_series_for_steps[1:] - mouse_series_for_steps[:-1]
pred_D = np.empty_like(human_actual)
prev = human_anchor
for k in range(len(pred_D)):
    prev = prev + mouse_deltas[k] * phi_scale
    pred_D[k] = prev

# Method E — Raw deltas, no scaling
pred_E = np.empty_like(human_actual)
prev = human_anchor
for k in range(len(pred_E)):
    prev = prev + mouse_deltas[k]
    pred_E[k] = prev

# v3 averaged
human_local_mean = float(np.mean(human_landmark))
human_local_std = float(np.std(human_landmark))
mouse_z_cont = znorm(mouse_at_human_times)
pred_v3 = mouse_z_cont * human_local_std + human_local_mean

pred_naive = mouse_at_human_times.copy()

def metrics(pred, actual):
    mae = float(np.mean(np.abs(pred - actual)))
    rmse = float(np.sqrt(np.mean((pred - actual)**2)))
    if np.std(pred) > 1e-9 and np.std(actual) > 1e-9:
        corr = float(np.corrcoef(pred, actual)[0,1])
    else:
        corr = 0.0
    return {'mae': mae, 'rmse': rmse, 'corr': corr}

m_A = metrics(pred_A, human_actual)
m_C = metrics(pred_C, human_actual)
m_D = metrics(pred_D, human_actual)
m_E = metrics(pred_E, human_actual)
m_v3 = metrics(pred_v3, human_actual)
m_naive = metrics(pred_naive, human_actual)

pred_pers = np.full_like(human_actual, human_anchor)
m_pers = metrics(pred_pers, human_actual)
pred_mean = np.full_like(human_actual, float(np.mean(human_actual)))
m_mean = metrics(pred_mean, human_actual)

print('=== RESULTS ===')
def show(label, m):
    print(f"  {label:36s} MAE {m['mae']:7.2f} ms  corr {m['corr']:+.3f}")
show('A: Ratio scaling (raw)',          m_A)
show('C: Multiplicative steps (raw)',    m_C)
show('D: Phi-scaled deltas (raw)',       m_D)
show('E: Raw deltas, no scaling',        m_E)
show('v3: Z-scored + mean/std (avg)',    m_v3)
show('Naive: mouse direct',              m_naive)
show('Persistence (anchor flat)',        m_pers)
show('Mean baseline',                    m_mean)

out = {
    'meta': {
        'landmark_corr': best['corr'],
        'landmark_len': LANDMARK_LEN,
        'mouse_idx': int(best['m_idx']),
        'human_idx': int(best['h_idx']),
        'human_anchor': human_anchor,
        'mouse_anchor': mouse_anchor,
        'period_ratio': float(period_ratio_obs),
        'rung_diff': float(rung_diff),
        'phi_scale': float(phi_scale),
        'mouse_continuation_len_beats': int(len(mouse_cont)),
        'human_continuation_len_beats': int(len(human_actual)),
        'mouse_mean_RR': float(mouse_rr.mean()),
        'human_mean_RR': float(human_rr.mean()),
        'mouse_landmark_range': mouse_lm_range,
        'human_landmark_range': human_lm_range,
    },
    'landmark': {
        'mouse': mouse_landmark.tolist(),
        'human': human_landmark.tolist(),
    },
    'continuation': {
        'mouse_raw': mouse_cont.tolist(),
        'mouse_at_human_time': mouse_at_human_times.tolist(),
        'human_actual': human_actual.tolist(),
        'pred_methodA_ratio': pred_A.tolist(),
        'pred_methodC_multiplicative': pred_C.tolist(),
        'pred_methodD_phi_delta': pred_D.tolist(),
        'pred_methodE_raw_delta': pred_E.tolist(),
        'pred_v3_averaged': pred_v3.tolist(),
        'pred_naive': pred_naive.tolist(),
        'pred_persistence': pred_pers.tolist(),
    },
    'metrics': {
        'methodA_ratio': m_A,
        'methodC_multiplicative': m_C,
        'methodD_phi_delta': m_D,
        'methodE_raw_delta': m_E,
        'v3_averaged': m_v3,
        'naive': m_naive,
        'persistence': m_pers,
        'mean_baseline': m_mean,
    },
}

with open(OUT_PATH, 'w') as f:
    f.write('window.decompRawData = ')
    json.dump(out, f)
    f.write(';')
print(f'Saved to {OUT_PATH}')

"""decomposition_pool_sweep.py — pool-matched landmark-length sweep, vectorized.

For each (mouse_specimen, human_segment) pair, find the best landmark of given
length via vectorized correlation matrix, then run v3 decomposition. Aggregate.

Key question: does landmark correlation predict decomposition quality?
"""
import os, glob, json, math, sys, time
import numpy as np
import pandas as pd

PHI = (1+5**0.5)/2
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
OUT_PATH = os.path.join(_HERE, 'decomposition_pool_data.js')

def log(s):
    print(s, flush=True)

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

log('Loading specimens...')
mouse_specimens = []
for p in sorted(glob.glob(os.path.join(REPO_ROOT, 'PhysioZoo', 'peaks_Mouse_*.txt'))):
    parsed = parse_peaks(p)
    if parsed:
        fs, pks = parsed
        if len(pks) >= 1000:
            rr = np.diff(pks)/fs*1000
            mouse_specimens.append({
                'name': os.path.basename(p).replace('peaks_','').replace('.txt',''),
                'rr': rr.astype(float),
            })
log(f'  {len(mouse_specimens)} mouse specimens')

hdf = pd.read_csv(os.path.join(REPO_ROOT, 'TheFormula', 'nsr001_rr.csv'))
human_full = hdf['rr_ms'].values.astype(float)
n_segs = 10
seg_len = len(human_full) // n_segs
human_specimens = [
    {'name': f'nsr001_seg{i+1:02d}', 'rr': human_full[i*seg_len:(i+1)*seg_len]}
    for i in range(n_segs)
]
log(f'  {len(human_specimens)} human pseudo-specimens (~{seg_len} beats each)')

# Vectorized landmark search
def build_z_windows(rr, L, stride, min_range):
    """Build N x L matrix of z-scored windows of length L from rr.
       Returns (start_indices, z_matrix) for windows whose raw range >= min_range."""
    starts = []
    rows = []
    for i in range(0, len(rr) - L, stride):
        w = rr[i:i+L]
        if (w.max() - w.min()) >= min_range:
            mean = w.mean()
            std = w.std()
            if std < 1e-9: continue
            starts.append(i)
            rows.append((w - mean) / std)
    if not rows:
        return np.array([]), np.zeros((0, L))
    return np.array(starts), np.array(rows)

def find_best_landmark_vec(m_rr, h_rr, L, m_stride, h_stride, m_min, h_min):
    """Vectorized: build z-matrices, compute correlation matrix in one matmul, take argmax."""
    m_starts, m_z = build_z_windows(m_rr, L, m_stride, m_min)
    h_starts, h_z = build_z_windows(h_rr, L, h_stride, h_min)
    if len(m_starts) == 0 or len(h_starts) == 0:
        return None
    # Correlation = (h_z @ m_z.T) / L since both are z-scored
    corr = (h_z @ m_z.T) / L
    flat = corr.argmax()
    hi_pos, mi_pos = divmod(flat, len(m_starts))
    return {
        'corr': float(corr[hi_pos, mi_pos]),
        'h_idx': int(h_starts[hi_pos]),
        'm_idx': int(m_starts[mi_pos]),
    }

def run_pair(mouse, human, L):
    m_rr = mouse['rr']; h_rr = human['rr']
    PRED_HUMAN = 60
    pred_mouse = int(PRED_HUMAN * (h_rr.mean() / m_rr.mean()))
    if len(h_rr) < L + PRED_HUMAN + 5 or len(m_rr) < L + pred_mouse + 5:
        return None
    
    h_min = max(20, 0.04 * (h_rr.max() - h_rr.min()))
    m_min = max(6, 0.04 * (m_rr.max() - m_rr.min()))
    h_stride = max(1, len(h_rr) // 150)
    m_stride = max(1, len(m_rr) // 150)
    
    best = find_best_landmark_vec(m_rr, h_rr, L, m_stride, h_stride, m_min, h_min)
    if best is None: return None
    
    h_idx, m_idx = best['h_idx'], best['m_idx']
    h_landmark = h_rr[h_idx:h_idx+L]
    h_anchor = float(h_landmark[-1])
    m_cont = m_rr[m_idx+L:m_idx+L+pred_mouse]
    h_actual = h_rr[h_idx+L:h_idx+L+PRED_HUMAN]
    if len(m_cont) < 5 or len(h_actual) < 5: return None
    
    # Time-scale
    m_times = np.cumsum(m_cont)
    h_times = np.arange(1, len(h_actual)+1) * h_rr.mean()
    m_at_h = np.interp(h_times, m_times, m_cont)
    
    # v3 decomp
    h_mean = float(h_landmark.mean())
    h_std = float(h_landmark.std())
    if h_std < 1e-9: return None
    m_z = (m_at_h - m_at_h.mean()) / max(1e-9, m_at_h.std())
    pred_v3 = m_z * h_std + h_mean
    
    pred_pers = np.full_like(h_actual, h_anchor)
    
    def met(p, a):
        mae = float(np.abs(p-a).mean())
        c = float(np.corrcoef(p, a)[0,1]) if p.std() > 1e-9 and a.std() > 1e-9 else 0.0
        return mae, c
    
    v3_mae, v3_c = met(pred_v3, h_actual)
    p_mae, _ = met(pred_pers, h_actual)
    
    return {
        'mouse': mouse['name'], 'human': human['name'],
        'L': L,
        'landmark_corr': best['corr'],
        'v3_mae': v3_mae, 'v3_corr': v3_c,
        'pers_mae': p_mae,
        'mae_lift_pct': (p_mae - v3_mae) / p_mae * 100 if p_mae > 0 else 0.0,
    }

LANDMARK_LENS = [7, 14, 28, 56]
all_results = {}
t0 = time.time()
for L in LANDMARK_LENS:
    log(f'\n=== L = {L} ===')
    rows = []
    for mi, mouse in enumerate(mouse_specimens):
        for hj, human in enumerate(human_specimens):
            r = run_pair(mouse, human, L)
            if r: rows.append(r)
    all_results[L] = rows
    if rows:
        lm = np.array([r['landmark_corr'] for r in rows])
        vc = np.array([r['v3_corr'] for r in rows])
        lifts = np.array([r['mae_lift_pct'] for r in rows])
        corr_of_corr = float(np.corrcoef(lm, vc)[0,1]) if len(lm) > 2 else 0.0
        thresh = np.quantile(lm, 0.75)
        hi_mask = lm >= thresh
        log(f'  N={len(rows)}  mean landmark_corr={lm.mean():.3f}')
        log(f'  mean v3_traj_corr={vc.mean():+.3f}  mean MAE lift vs persistence={lifts.mean():+.1f}%')
        log(f'  Corr(landmark_corr, v3_traj_corr) = {corr_of_corr:+.3f}')
        log(f'  Top-25%-landmark subset v3 corr = {vc[hi_mask].mean():+.3f}')
        log(f'  Bottom-75%-landmark subset v3 corr = {vc[~hi_mask].mean():+.3f}')
log(f'\nElapsed: {time.time()-t0:.1f}s')

out = {'landmark_lens': LANDMARK_LENS, 'n_mouse': len(mouse_specimens),
       'n_human_seg': len(human_specimens), 'results': all_results}
with open(OUT_PATH, 'w') as f:
    f.write('window.poolSweepData = ')
    json.dump(out, f)
    f.write(';')
log(f'Saved {OUT_PATH}')

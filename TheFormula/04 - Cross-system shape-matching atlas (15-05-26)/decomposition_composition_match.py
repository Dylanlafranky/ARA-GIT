"""decomposition_composition_match.py — Dylan 2026-05-12.

Test the framework claim: composition-match (per-rung ARA profile) transfers
trajectories better than shape-match (z-scored surface curve).

For each window: compute fingerprint = FFT magnitudes at Fibonacci-spaced periods
{3, 5, 8, 13, 21} beats. This is the window's per-rung energy profile.

Two windows have a 'composition match' if their fingerprint vectors are highly
similar (cosine similarity).

Compare three matching strategies on the same (mouse, human) pair grid:
  A. Shape-only (z-score correlation of raw curve) — control from prior test
  B. Composition-only (cosine of fingerprint vectors)
  C. Combined (both must be high)

If composition-matched (B) and combined (C) give better trajectory correlation
than shape-only (A), the framework's 'composition is the real predicate' claim
is operationally supported.
"""
import os, glob, json, math, time
import numpy as np
import pandas as pd

PHI = (1+5**0.5)/2
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
OUT_PATH = os.path.join(_HERE, 'decomposition_composition_data.js')

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

log('Loading...')
mouse_specimens = []
for p in sorted(glob.glob(os.path.join(REPO_ROOT, 'PhysioZoo', 'peaks_Mouse_*.txt'))):
    parsed = parse_peaks(p)
    if parsed:
        fs, pks = parsed
        if len(pks) >= 1000:
            mouse_specimens.append({'name': os.path.basename(p).replace('peaks_','').replace('.txt',''),
                                    'rr': (np.diff(pks)/fs*1000).astype(float)})

hdf = pd.read_csv(os.path.join(REPO_ROOT, 'TheFormula', 'nsr001_rr.csv'))
human_full = hdf['rr_ms'].values.astype(float)
n_segs = 10
seg_len = len(human_full) // n_segs
human_specimens = [{'name': f'nsr001_seg{i+1:02d}', 'rr': human_full[i*seg_len:(i+1)*seg_len]} for i in range(n_segs)]
log(f'  {len(mouse_specimens)} mouse, {len(human_specimens)} human-seg')

L = 28
PRED_HUMAN = 60
FIB_PERIODS = np.array([3, 5, 8, 13, 21])  # φ-spaced periods in beat units

def composition_vector(w):
    """FFT-magnitude profile at Fibonacci-spaced periods. Returns log-magnitude vector."""
    w_demean = w - w.mean()
    fft = np.abs(np.fft.rfft(w_demean))
    # Period in beats = L / k where k is FFT bin index. We want bins where period ≈ FIB_PERIODS
    bins = np.round(len(w) / FIB_PERIODS).astype(int)
    bins = np.clip(bins, 1, len(fft)-1)
    mags = fft[bins]
    # Log magnitude, avoid log(0)
    return np.log(mags + 1e-9)

def normalize_vec(v):
    n = np.linalg.norm(v)
    return v / max(n, 1e-9)

def build_windows(rr, L, stride, h_min):
    starts = []
    z_rows = []
    c_rows = []
    for i in range(0, len(rr) - L, stride):
        w = rr[i:i+L]
        if (w.max() - w.min()) < h_min: continue
        mean, std = w.mean(), w.std()
        if std < 1e-9: continue
        z_rows.append((w - mean) / std)
        c_rows.append(normalize_vec(composition_vector(w)))
        starts.append(i)
    if not starts:
        return np.array([]), np.zeros((0, L)), np.zeros((0, len(FIB_PERIODS)))
    return np.array(starts), np.array(z_rows), np.array(c_rows)

def run_pair(mouse, human):
    m_rr = mouse['rr']; h_rr = human['rr']
    pred_mouse = int(PRED_HUMAN * (h_rr.mean()/m_rr.mean()))
    if len(h_rr) < L + PRED_HUMAN + 5 or len(m_rr) < L + pred_mouse + 5:
        return None
    h_min = max(20, 0.04*(h_rr.max()-h_rr.min()))
    m_min = max(6, 0.04*(m_rr.max()-m_rr.min()))
    h_stride = max(1, len(h_rr)//150)
    m_stride = max(1, len(m_rr)//150)
    
    h_starts, h_z, h_c = build_windows(h_rr, L, h_stride, h_min)
    m_starts, m_z, m_c = build_windows(m_rr, L, m_stride, m_min)
    if len(h_starts) == 0 or len(m_starts) == 0: return None
    
    # Shape correlation matrix
    shape_corr = (h_z @ m_z.T) / L
    # Composition cosine similarity matrix (already unit-normed)
    comp_sim = h_c @ m_c.T
    
    def best_pair_by(matrix):
        flat = matrix.argmax()
        hi, mi = divmod(flat, matrix.shape[1])
        return hi, mi, float(matrix[hi, mi])
    
    def run_decomp_at(hi, mi):
        h_idx = h_starts[hi]; m_idx = m_starts[mi]
        h_lm = h_rr[h_idx:h_idx+L]
        h_anc = float(h_lm[-1])
        m_cont = m_rr[m_idx+L:m_idx+L+pred_mouse]
        h_act = h_rr[h_idx+L:h_idx+L+PRED_HUMAN]
        if len(m_cont) < 5 or len(h_act) < 5: return None
        m_times = np.cumsum(m_cont)
        h_times = np.arange(1, len(h_act)+1) * h_rr.mean()
        m_at_h = np.interp(h_times, m_times, m_cont)
        h_mean = float(h_lm.mean()); h_std = float(h_lm.std())
        if h_std < 1e-9: return None
        m_z_cont = (m_at_h - m_at_h.mean()) / max(m_at_h.std(), 1e-9)
        pred = m_z_cont * h_std + h_mean
        pred_pers = np.full_like(h_act, h_anc)
        mae = float(np.abs(pred - h_act).mean())
        corr = float(np.corrcoef(pred, h_act)[0,1]) if pred.std()>1e-9 and h_act.std()>1e-9 else 0.0
        pers_mae = float(np.abs(pred_pers - h_act).mean())
        return {'mae': mae, 'corr': corr, 'pers_mae': pers_mae,
                'shape_corr_lm': float(shape_corr[hi, mi]),
                'comp_sim_lm': float(comp_sim[hi, mi])}
    
    # Strategy A: best by shape
    hi_a, mi_a, _ = best_pair_by(shape_corr)
    res_a = run_decomp_at(hi_a, mi_a)
    # Strategy B: best by composition
    hi_b, mi_b, _ = best_pair_by(comp_sim)
    res_b = run_decomp_at(hi_b, mi_b)
    # Strategy C: best by combined (product of shape_corr and comp_sim, both > 0)
    combined = np.clip(shape_corr, 0, None) * np.clip(comp_sim, 0, None)
    hi_c, mi_c, _ = best_pair_by(combined)
    res_c = run_decomp_at(hi_c, mi_c)
    
    if not (res_a and res_b and res_c): return None
    return {
        'pair': f"{mouse['name']}↔{human['name']}",
        'A_shape':    {'lm_shape': res_a['shape_corr_lm'], 'lm_comp': res_a['comp_sim_lm'], 'corr': res_a['corr'], 'mae': res_a['mae'], 'pers_mae': res_a['pers_mae']},
        'B_comp':     {'lm_shape': res_b['shape_corr_lm'], 'lm_comp': res_b['comp_sim_lm'], 'corr': res_b['corr'], 'mae': res_b['mae'], 'pers_mae': res_b['pers_mae']},
        'C_combined': {'lm_shape': res_c['shape_corr_lm'], 'lm_comp': res_c['comp_sim_lm'], 'corr': res_c['corr'], 'mae': res_c['mae'], 'pers_mae': res_c['pers_mae']},
    }

t0 = time.time()
results = []
for mouse in mouse_specimens:
    for human in human_specimens:
        r = run_pair(mouse, human)
        if r: results.append(r)
log(f'\nN pairs: {len(results)}, elapsed: {time.time()-t0:.1f}s')

# Aggregate
def agg(strategy_key):
    vals = [r[strategy_key] for r in results]
    return {
        'mean_lm_shape': float(np.mean([v['lm_shape'] for v in vals])),
        'mean_lm_comp':  float(np.mean([v['lm_comp']  for v in vals])),
        'mean_traj_corr': float(np.mean([v['corr'] for v in vals])),
        'mean_mae':       float(np.mean([v['mae']  for v in vals])),
        'mean_pers_mae':  float(np.mean([v['pers_mae'] for v in vals])),
    }

a = agg('A_shape'); b = agg('B_comp'); c = agg('C_combined')
log('\n=== STRATEGY COMPARISON ===')
log('Strategy            | LM shape | LM comp | traj corr | MAE   | persMAE | Δvs pers')
log('-'*82)
for key, lbl, x in [('A','A: Shape-best',a), ('B','B: Comp-best',b), ('C','C: Combined-best',c)]:
    lift = (x['mean_pers_mae'] - x['mean_mae'])/x['mean_pers_mae']*100
    log(f"{lbl:18s} | {x['mean_lm_shape']:+.3f}    | {x['mean_lm_comp']:+.3f}   | {x['mean_traj_corr']:+.3f}     | {x['mean_mae']:5.1f} | {x['mean_pers_mae']:5.1f}   | {lift:+.1f}%")

# Composition-sim vs trajectory-corr scatter analysis
all_comp = []; all_traj = []
for r in results:
    for k in ['A_shape','B_comp','C_combined']:
        all_comp.append(r[k]['lm_comp'])
        all_traj.append(r[k]['corr'])
all_comp = np.array(all_comp); all_traj = np.array(all_traj)
if len(all_comp) > 2 and all_comp.std() > 1e-9:
    rho = float(np.corrcoef(all_comp, all_traj)[0,1])
    log(f'\nCorr(composition_similarity, trajectory_corr) across all strategies: {rho:+.3f}')

out = {'results': results, 'agg': {'A_shape':a, 'B_comp':b, 'C_combined':c}}
with open(OUT_PATH, 'w') as f:
    f.write('window.compositionData = ')
    json.dump(out, f)
    f.write(';')
log(f'Saved {OUT_PATH}')

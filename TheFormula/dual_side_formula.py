"""
Dual-side formula: TIME × ARA, with wobble.

Architecture (per Dylan, 2026-05-01):
    y(t) − mean = Σ_k  amp_k(ARA-side) · wave_shape( phase_k(t), ARA_k(cycle) )

where:
  TIME side  → phase_k(t)     = cycle-schedule generator (step 3) + WOBBLE
                                   "energy doesn't travel straight, it travels on a small wave of itself"
                                   phase_eff = phase_linear + ε · sin(2π · φ · phase_linear · n)
  ARA side   → ARA_k(cycle)    = AR(1) on per-rung cycle ARAs + cross-rung coupling (step 3)
               amp_k           = base · φ^(k − k_ref)  (log-slider)
               wave_shape      = f^(1/ARA) accumulation, (1-f)^ARA release  (existing)

Open-system caveat (per Dylan, 2026-05-01):
  the heart receives information from brain & nervous system → it is NOT a closed system,
  so point-by-point match degrades as our schedule drifts from the true (driver-influenced) one.
  We therefore evaluate at multiple horizons: short (first hour of test), mid (first 4 h),
  full (entire test half). And we report statistical match (KS distance on per-window stds)
  as well as point correlation — for open systems statistical match is the more honest metric.
"""
import json, re, math, os, sys
import numpy as np, pandas as pd

PHI = 1.6180339887498949
def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win
DATA_PATH = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
PER_RUNG  = _resolve(r"F:\SystemFormulaFolder\TheFormula\per_rung_seq_ara.js")
COUPLE    = _resolve(r"F:\SystemFormulaFolder\TheFormula\cross_rung_coupling.js")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\dual_side_data.js")

def load_blob(path, var):
    txt = open(path,'r',encoding='utf-8').read()
    m = re.search(re.escape(var) + r"\s*=\s*(\{.*\});?\s*$", txt, re.DOTALL)
    return json.loads(m.group(1))

# --- WOBBLE: energy doesn't travel straight ---
# phase advances with a small superimposed wave of itself
WOBBLE_AMP = 0.10  # how much of cycle the wobble shifts (≤ 1/φ to stay coherent)
WOBBLE_N   = 1.0   # number of wobble periods inside one cycle

def wobble_phase(p_lin):
    return (p_lin + WOBBLE_AMP * np.sin(2*np.pi * PHI * p_lin * WOBBLE_N)) % 1.0

def wave_shape(phase, ARA):
    p = phase % 1.0
    cross = 1.0/PHI
    if p < cross:
        return (p/cross) ** (1.0/max(ARA,0.1))
    else:
        return (1.0 - (p - cross)/(1.0 - cross)) ** max(ARA,0.1)

def ar1(prev, mean, std, lag1):
    eps_std = std * math.sqrt(max(1e-9, 1.0 - lag1*lag1))
    return mean + lag1*(prev - mean) + np.random.normal(0.0, eps_std)

# --- LOAD ---
df = pd.read_csv(DATA_PATH)
t  = df['time_s'].values.astype(float)
v  = df['rr_ms' ].values.astype(float)

GRID_DT = 0.5
t_grid = np.arange(t[0], t[-1], GRID_DT)
v_grid = np.interp(t_grid, t, v)
N = len(t_grid); SPLIT = N//2
t_train, v_train = t_grid[:SPLIT], v_grid[:SPLIT]
t_test , v_test  = t_grid[SPLIT:], v_grid[SPLIT:]
T_train_end = t_grid[SPLIT-1]; T_test_end = t_grid[-1]
mean_train = float(np.mean(v_train))

per_rung = load_blob(PER_RUNG, "window.PER_RUNG_SEQ")
coupling = load_blob(COUPLE,   "window.CROSS_COUPLING")

# --- TRAIN STATS PER RUNG ---
stats = {}
for k_str, info in per_rung.items():
    k = int(k_str)
    aras = np.array(info['cycle_aras'], dtype=float)
    starts = np.array(info['cycle_starts'], dtype=float)
    train_mask = starts < T_train_end
    if train_mask.sum() < 4: continue
    aras_tr, starts_tr = aras[train_mask], starts[train_mask]
    durs_tr = np.diff(starts_tr) if len(starts_tr) >= 2 else np.array([PHI**k])
    stats[k] = dict(
        mean_ARA=float(np.mean(aras_tr)), std_ARA=float(np.std(aras_tr)),
        lag1=float(np.corrcoef(aras_tr[:-1], aras_tr[1:])[0,1]) if len(aras_tr)>=3 and np.std(aras_tr)>1e-6 else 0.0,
        mean_dur=float(np.mean(durs_tr)), std_dur=float(np.std(durs_tr)),
        last_start=float(starts_tr[-1]), last_ARA=float(aras_tr[-1]),
        n_train_cycles=int(train_mask.sum())
    )
    if not np.isfinite(stats[k]['lag1']): stats[k]['lag1']=0.0

print("TRAIN stats per rung:")
for k,s in stats.items():
    print(f"  k={k:2d} cycles={s['n_train_cycles']:3d} mean_dur={s['mean_dur']:7.1f}s mean_ARA={s['mean_ARA']:.3f} lag1={s['lag1']:+.3f}")

coupling_lookup = {}
for key,info in coupling.items():
    coupling_lookup[(info['k1'],info['k2'])] = info
    coupling_lookup[(info['k2'],info['k1'])] = info

def couple(k1,k2):
    info = coupling_lookup.get((k1,k2))
    return float(info.get('ara_corr',0.0)) if info else 0.0

# --- TIME SIDE: generate cycle schedule per rung ---
np.random.seed(42)
generated = {}
for k,s in stats.items():
    cycles = []
    cur_t = s['last_start'] + s['mean_dur']
    cur_a = s['last_ARA']
    while cur_t < T_test_end:
        cur_a = float(np.clip(ar1(cur_a, s['mean_ARA'], s['std_ARA'], s['lag1']), 0.3, 4.0))
        dur = float(max(s['mean_dur']*0.3, np.random.normal(s['mean_dur'], s['std_dur'])))
        cycles.append(dict(start=cur_t, dur=dur, ARA=cur_a))
        cur_t += dur
    generated[k] = cycles

# Cross-rung coupling overlay on ARA
for k,cyc in generated.items():
    for c in cyc:
        midt = c['start'] + c['dur']*0.5
        adj=0.0; wsum=0.0
        for k2,cyc2 in generated.items():
            if k2==k: continue
            w = couple(k,k2)
            if abs(w) < 0.30: continue
            for c2 in cyc2:
                if c2['start'] <= midt <= c2['start']+c2['dur']:
                    adj  += w*(c2['ARA']-c['ARA']); wsum += abs(w); break
        if wsum > 0:
            c['ARA'] = float(np.clip(c['ARA'] + adj/(wsum*PHI*PHI), 0.3, 4.0))

# --- ARA SIDE: per-cycle wave shape composition ---
# Same shape Dylan articulated, but with WOBBLE applied to phase
def rung_wave(cycles, t_arr):
    out = np.zeros_like(t_arr)
    for c in cycles:
        t0, tf, ARA = c['start'], c['start']+c['dur'], c['ARA']
        mask = (t_arr >= t0) & (t_arr < tf)
        if not mask.any(): continue
        phase_lin = (t_arr[mask] - t0) / c['dur']
        phase_eff = wobble_phase(phase_lin)
        for i, p in enumerate(phase_eff):
            out[np.where(mask)[0][i]] = wave_shape(p, ARA)
    return out

# --- TRAIN-FIT amplitude base ---
def train_rung_wave(k, t_arr):
    info = per_rung[str(k)]
    aras = np.array(info['cycle_aras']); starts = np.array(info['cycle_starts'])
    train_mask = starts < T_train_end
    starts_tr, aras_tr = starts[train_mask], aras[train_mask]
    out = np.zeros_like(t_arr)
    for i in range(len(starts_tr)):
        t0 = starts_tr[i]
        tf = starts_tr[i+1] if i+1<len(starts_tr) else t0 + np.mean(np.diff(starts_tr)) if len(starts_tr)>1 else t0+PHI**k
        dur = tf - t0; ARA = aras_tr[i]
        mask = (t_arr >= t0) & (t_arr < tf)
        if not mask.any(): continue
        phase_lin = (t_arr[mask] - t0) / dur
        phase_eff = wobble_phase(phase_lin)
        for j, p in enumerate(phase_eff):
            out[np.where(mask)[0][j]] = wave_shape(p, ARA)
    return out - np.mean(out)

k_ref = max(stats.keys())
basis = np.zeros_like(v_train)
for k in stats:
    basis += (PHI**(k - k_ref)) * train_rung_wave(k, t_train)
y_train_c = v_train - mean_train
denom = float(np.dot(basis, basis))
base = float(np.dot(basis, y_train_c) / denom) if denom > 0 else 1.0
print(f"\nFitted amplitude base (φ^k, k_ref={k_ref}, with wobble {WOBBLE_AMP}): {base:.3f}")

# --- TEST PREDICTION ---
y_pred_c = np.zeros_like(t_test)
for k, cyc in generated.items():
    y_pred_c += base * (PHI**(k - k_ref)) * (rung_wave(cyc, t_test) - 0.0)

# 1/φ³ AR feedback decay seeded from train residual
gamma = 1.0/(PHI**3)
boost = np.zeros_like(t_test)
boost[0] = (v_train[-1] - mean_train) * gamma
for i in range(1, len(t_test)):
    boost[i] = boost[i-1] * (1.0 - gamma)
y_pred = mean_train + y_pred_c + boost

# AR-blind baseline
ar_blind = np.zeros_like(t_test); ar_blind[0] = v_train[-1]
for i in range(1, len(t_test)):
    ar_blind[i] = ar_blind[i-1]*0.99 + 0.01*mean_train
y_mean = np.full_like(t_test, mean_train)

# --- METRICS at multiple horizons ---
def metrics(y_true, y_pred):
    if np.std(y_pred) < 1e-9: corr=0.0
    else: corr = float(np.corrcoef(y_true, y_pred)[0,1])
    rmse = float(np.sqrt(np.mean((y_true-y_pred)**2)))
    return dict(corr=corr, rmse=rmse, pred_std=float(np.std(y_pred)), true_std=float(np.std(y_true)), n=len(y_true))

# horizons: 1h, 4h, full
horizons = {
    'short_1h':  int(3600/GRID_DT),
    'mid_4h':    int(4*3600/GRID_DT),
    'full':      len(t_test),
}
results = {}
for hname, n in horizons.items():
    n = min(n, len(t_test))
    r = dict(
        dual_side = metrics(v_test[:n], y_pred[:n]),
        ar_blind  = metrics(v_test[:n], ar_blind[:n]),
        mean      = metrics(v_test[:n], y_mean[:n]),
    )
    results[hname] = r

# Statistical match: KS-distance on per-window stds (rolling 5-min std distribution)
def per_window_stds(arr, win=600):  # 5 min @ 0.5s grid
    return np.array([np.std(arr[i:i+win]) for i in range(0, len(arr)-win, win)])
true_stds = per_window_stds(v_test)
pred_stds = per_window_stds(y_pred)
ar_stds   = per_window_stds(ar_blind)

def ks_dist(a, b):
    a = np.sort(a); b = np.sort(b)
    grid = np.linspace(min(a.min(),b.min()), max(a.max(),b.max()), 200)
    cdfA = np.searchsorted(a, grid)/len(a)
    cdfB = np.searchsorted(b, grid)/len(b)
    return float(np.max(np.abs(cdfA-cdfB)))

stat_match = dict(
    dual_side = ks_dist(true_stds, pred_stds),
    ar_blind  = ks_dist(true_stds, ar_stds),
)

print("\n========= MULTI-HORIZON BLIND RESULTS =========")
for hname, r in results.items():
    print(f"\n[{hname}]  n={r['dual_side']['n']}  true_std={r['dual_side']['true_std']:.1f}")
    print(f"  Mean-only  : corr={r['mean']['corr']:+.3f}   rmse={r['mean']['rmse']:.1f}")
    print(f"  AR-blind   : corr={r['ar_blind']['corr']:+.3f}   rmse={r['ar_blind']['rmse']:.1f}   std={r['ar_blind']['pred_std']:.1f}")
    print(f"  Dual-side  : corr={r['dual_side']['corr']:+.3f}   rmse={r['dual_side']['rmse']:.1f}   std={r['dual_side']['pred_std']:.1f}")

print(f"\nStatistical match (KS distance on 5-min rolling std):")
print(f"  AR-blind   KS = {stat_match['ar_blind']:.3f}  (lower = closer to true distribution)")
print(f"  Dual-side  KS = {stat_match['dual_side']:.3f}")

# --- SAVE ---
out = dict(
    t_train=t_train.tolist()[-2000:], v_train=v_train.tolist()[-2000:],
    t_test=t_test.tolist(), v_test=v_test.tolist(),
    y_pred=y_pred.tolist(), ar_blind=ar_blind.tolist(),
    horizons=results, stat_match=stat_match,
    rungs=list(stats.keys()), base_amplitude=base, k_ref=k_ref,
    wobble_amp=WOBBLE_AMP, wobble_n=WOBBLE_N,
    n_generated_cycles={str(k):len(c) for k,c in generated.items()},
    couplings_used={f"{a}_{b}":couple(a,b) for a in stats for b in stats if a<b and abs(couple(a,b))>0.30},
    true_window_stds=true_stds.tolist(), pred_window_stds=pred_stds.tolist(),
)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write("window.DUAL_SIDE = " + json.dumps(out) + ";\n")
print(f"\nSaved -> {OUT}")

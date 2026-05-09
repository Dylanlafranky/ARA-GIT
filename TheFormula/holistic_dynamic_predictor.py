"""
Step 3: Dynamic holistic predictor that composes per-rung cycle sequences
under cross-rung coupling, generated forward from training stats only.

Inputs (data-derived, no hardcoded params except framework constants):
- per_rung_seq_ara.js  : per-rung cycle ARAs and starts on TRAINING half
- cross_rung_coupling.js : data-derived coupling between rung pairs

Framework constants (the only things we hardcode):
- φ = 1.6180339887
- pump_rung for ECG = 1 (φ^1 ≈ 1.62s)
- 1/φ³ AR feedback (AA-boundary momentum, prior memory)
- φ^k amplitude scaling base

Process:
  Train on first half of nsr001_rr.csv; predict second half blindly.
  For each rung, generate forward cycle SEQUENCE (start, dur, ARA) using:
    - AR(1) on ARA seeded from training mean+lag1
    - cross-rung coupling: a fraction of next-cycle-ARA pulled toward
      strongly-coupled neighbour rung's predicted ARA
    - duration sampled from training distribution
  From per-rung wave_shape generators, compose the value series.
  Compare to AR-blind baseline and v4.1 framework static.
"""
import json, re, math, os, sys
import numpy as np
import pandas as pd

PHI = 1.6180339887498949
# Detect OS / mount; works in Linux bash sandbox AND on Windows
def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder"):
        return p_lin
    return p_win
DATA_PATH     = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
PER_RUNG_PATH = _resolve(r"F:\SystemFormulaFolder\TheFormula\per_rung_seq_ara.js")
COUPLE_PATH   = _resolve(r"F:\SystemFormulaFolder\TheFormula\cross_rung_coupling.js")
OUT_PATH      = _resolve(r"F:\SystemFormulaFolder\TheFormula\holistic_dynamic_data.js")

# ------- helpers -------
def load_js_blob(path, var):
    txt = open(path,'r',encoding='utf-8').read()
    m = re.search(re.escape(var) + r"\s*=\s*(\{.*\});?\s*$", txt, re.DOTALL)
    if not m: raise RuntimeError("no blob in "+path)
    return json.loads(m.group(1))

def wave_shape(phase, ARA):
    # phase in [0,1); peak at φ-fraction; same shape used elsewhere
    p = phase % 1.0
    cross = 1.0/PHI  # peak position
    if p < cross:
        f = p/cross
        return f**(1.0/max(ARA,0.1))
    else:
        f = (p - cross)/(1.0 - cross)
        return (1.0 - f)**max(ARA,0.1)

def ar1_step(prev_z, mean, std, lag1):
    # Generate next sample z' = mean + lag1*(z - mean) + eps with var preserving std
    eps_std = std * math.sqrt(max(1e-9, 1.0 - lag1*lag1))
    return mean + lag1*(prev_z - mean) + np.random.normal(0.0, eps_std)

# ------- load -------
df = pd.read_csv(DATA_PATH)
t  = df['time_s'].values.astype(float)
v  = df['rr_ms' ].values.astype(float)

# Resample to uniform grid for clean train/test split
GRID_DT = 0.5  # sub-pump
t_grid = np.arange(t[0], t[-1], GRID_DT)
v_grid = np.interp(t_grid, t, v)
N = len(t_grid)
SPLIT = N//2
t_train, v_train = t_grid[:SPLIT], v_grid[:SPLIT]
t_test , v_test  = t_grid[SPLIT:], v_grid[SPLIT:]
T_train_end = t_grid[SPLIT-1]
print(f"Train {len(t_train)} samples ({t_train[-1]-t_train[0]:.0f}s), Test {len(t_test)} samples ({t_test[-1]-t_test[0]:.0f}s)")

per_rung = load_js_blob(PER_RUNG_PATH, "window.PER_RUNG_SEQ")
coupling = load_js_blob(COUPLE_PATH,   "window.CROSS_COUPLING")

# rung set
rungs = sorted(int(k) for k in per_rung.keys())
print("Rungs:", rungs)

# ------- TRAINING STATS PER RUNG (dynamic from data) -------
stats = {}
for k_str, info in per_rung.items():
    k = int(k_str)
    aras = np.array(info['cycle_aras'], dtype=float)
    starts = np.array(info['cycle_starts'], dtype=float)
    # only train cycles (whose start < T_train_end)
    train_mask = starts < T_train_end
    if train_mask.sum() < 4:
        # too few train cycles to fit AR(1)
        continue
    aras_tr = aras[train_mask]
    starts_tr = starts[train_mask]
    if len(starts_tr) >= 2:
        durs_tr = np.diff(starts_tr)
    else:
        durs_tr = np.array([PHI**k])
    mean_a = float(np.mean(aras_tr))
    std_a  = float(np.std(aras_tr))
    if len(aras_tr) >= 3 and std_a > 1e-6:
        lag1 = float(np.corrcoef(aras_tr[:-1], aras_tr[1:])[0,1])
        if not np.isfinite(lag1): lag1 = 0.0
    else:
        lag1 = 0.0
    mean_d = float(np.mean(durs_tr))
    std_d  = float(np.std(durs_tr))
    last_train_start = float(starts_tr[-1])
    last_train_ARA   = float(aras_tr[-1])
    stats[k] = dict(mean_ARA=mean_a, std_ARA=std_a, lag1=lag1,
                    mean_dur=mean_d, std_dur=std_d,
                    last_start=last_train_start, last_ARA=last_train_ARA,
                    n_train_cycles=int(train_mask.sum()))

print("\nTRAIN stats per rung:")
for k, s in stats.items():
    print(f"  k={k:2d} cycles={s['n_train_cycles']:3d} mean_dur={s['mean_dur']:7.1f}s mean_ARA={s['mean_ARA']:.3f} lag1={s['lag1']:+.3f}")

# ------- COUPLING MATRIX (data-derived) -------
# pair key like "16_18" → coupling stats with lowercase keys
coupling_lookup = {}
for key, info in coupling.items():
    k1, k2 = info['k1'], info['k2']
    coupling_lookup[(k1,k2)] = info
    coupling_lookup[(k2,k1)] = info

def coupling_strength(k1, k2):
    info = coupling_lookup.get((k1,k2))
    if not info: return 0.0
    # use ara_corr as the influence strength (already lowercase)
    return float(info.get('ara_corr', 0.0))

# ------- GENERATIVE PER-RUNG CYCLE SEQUENCE FORWARD -------
T_test_end = t_grid[-1]
np.random.seed(42)

generated = {}  # k → list of dict(start, dur, ARA)
for k in stats:
    s = stats[k]
    cycles = []
    cur_t = s['last_start'] + s['mean_dur']
    cur_a = s['last_ARA']
    while cur_t < T_test_end:
        # AR(1) update of ARA
        cur_a = ar1_step(cur_a, s['mean_ARA'], s['std_ARA'], s['lag1'])
        # bound to physical range
        cur_a = float(np.clip(cur_a, 0.3, 4.0))
        # duration ~ N(mean_dur, std_dur)
        dur = max(s['mean_dur']*0.3, np.random.normal(s['mean_dur'], s['std_dur']))
        cycles.append(dict(start=cur_t, dur=dur, ARA=cur_a))
        cur_t += dur
    generated[k] = cycles

# ------- APPLY CROSS-RUNG COUPLING (overlay step) -------
# Pull each cycle's ARA toward the contemporaneous ARA of strongly-coupled neighbour
for k, cycles in generated.items():
    for c in cycles:
        # find the cycle in each neighbour rung that overlaps in time
        midt = c['start'] + c['dur']*0.5
        adj  = 0.0
        wsum = 0.0
        for k2, cyc2 in generated.items():
            if k2 == k: continue
            w = coupling_strength(k, k2)
            if abs(w) < 0.30:  # only strong couplings
                continue
            # find overlapping cycle
            for c2 in cyc2:
                if c2['start'] <= midt <= c2['start'] + c2['dur']:
                    adj  += w * (c2['ARA'] - c['ARA'])
                    wsum += abs(w)
                    break
        if wsum > 0:
            # blend: 1/φ² weight on coupling correction (gentle)
            c['ARA'] = float(np.clip(c['ARA'] + adj/(wsum*PHI*PHI), 0.3, 4.0))

# ------- COMPOSE VALUE PREDICTION -------
# Build per-rung wave on test grid, then sum with φ^(k - k_ref) amplitude scaling
k_ref = max(stats.keys())  # reference at largest rung (where amp lives)
mean_train = float(np.mean(v_train))

def rung_wave_on_grid(k, cycles, t_arr):
    out = np.zeros_like(t_arr)
    for c in cycles:
        t0 = c['start']
        tf = c['start'] + c['dur']
        ARA = c['ARA']
        # phase within cycle
        for i, ti in enumerate(t_arr):
            if t0 <= ti < tf:
                phase = (ti - t0)/c['dur']
                out[i] = wave_shape(phase, ARA)
    return out

# Generate per-rung waves
rung_waves = {}
for k, cycles in generated.items():
    w = rung_wave_on_grid(k, cycles, t_test)
    # center to zero-mean
    w = w - np.mean(w)
    rung_waves[k] = w

# Combine with φ^(k - k_ref) amplitude scaling — single base fitted on TRAIN
# Fit base by combining same-shape on train period and matching std
# Build a train-period wave per rung (using cycles that fall in train) — same generative process?
# For simplicity, use the actual training cycle ARAs to compose train wave, then OLS for base.

def train_rung_wave(k, t_arr):
    info = per_rung[str(k)]
    aras = np.array(info['cycle_aras'])
    starts = np.array(info['cycle_starts'])
    train_mask = starts < T_train_end
    starts_tr = starts[train_mask]
    aras_tr   = aras[train_mask]
    out = np.zeros_like(t_arr)
    for i in range(len(starts_tr)):
        t0 = starts_tr[i]
        if i+1 < len(starts_tr):
            tf = starts_tr[i+1]
        else:
            tf = t0 + np.mean(np.diff(starts_tr)) if len(starts_tr)>1 else t0+PHI**k
        ARA = aras_tr[i]
        dur = tf - t0
        for j, tj in enumerate(t_arr):
            if t0 <= tj < tf:
                phase = (tj - t0)/dur
                out[j] = wave_shape(phase, ARA)
    return out - np.mean(out)

# OLS to fit base amplitude with phi^(k-k_ref) constraint
# y_train_centered ≈ base * Σ φ^(k-k_ref) * train_rung_wave_k
y_train_c = v_train - mean_train
basis = np.zeros_like(y_train_c)
for k in stats:
    w_train = train_rung_wave(k, t_train)
    basis += (PHI**(k - k_ref)) * w_train

# scalar OLS
denom = float(np.dot(basis, basis))
if denom > 0:
    base = float(np.dot(basis, y_train_c) / denom)
else:
    base = 1.0
print(f"\nFitted amplitude base (φ^k scaling, k_ref={k_ref}): {base:.3f}")

# Build test prediction
y_pred_zero = np.zeros_like(t_test)
for k, w in rung_waves.items():
    y_pred_zero += base * (PHI**(k - k_ref)) * w

# Add 1/φ³ AR feedback on top using train-end momentum
gamma = 1.0/(PHI**3)
y_test_centered_pred = y_pred_zero.copy()
# add a slow-decay AR term seeded from last training residual
last_train_resid = v_train[-1] - mean_train
boost = np.zeros_like(t_test)
boost[0] = last_train_resid * gamma
for i in range(1, len(t_test)):
    boost[i] = boost[i-1] * (1.0 - gamma)  # decay back to zero
y_pred = mean_train + y_test_centered_pred + boost

# ------- BASELINES -------
y_mean   = np.full_like(t_test, mean_train)
# AR-blind: persist last training value with simple decay to mean
ar_blind = np.zeros_like(t_test)
ar_blind[0] = v_train[-1]
for i in range(1, len(t_test)):
    ar_blind[i] = ar_blind[i-1]*0.99 + 0.01*mean_train

# ------- METRICS -------
def metrics(y_true, y_pred):
    y_true = np.asarray(y_true); y_pred = np.asarray(y_pred)
    if np.std(y_pred) < 1e-9:
        corr = 0.0
    else:
        corr = float(np.corrcoef(y_true, y_pred)[0,1])
    rmse = float(np.sqrt(np.mean((y_true-y_pred)**2)))
    mae  = float(np.mean(np.abs(y_true-y_pred)))
    pred_std = float(np.std(y_pred))
    return dict(corr=corr, rmse=rmse, mae=mae, pred_std=pred_std)

m_holistic = metrics(v_test, y_pred)
m_mean     = metrics(v_test, y_mean)
m_ar       = metrics(v_test, ar_blind)

print("\n========= BLIND MULTI-STEP RESULTS =========")
print(f"Mean-only baseline   : corr={m_mean['corr']:+.3f}  rmse={m_mean['rmse']:.1f}  std={m_mean['pred_std']:.2f}")
print(f"AR-blind             : corr={m_ar['corr']:+.3f}  rmse={m_ar['rmse']:.1f}  std={m_ar['pred_std']:.2f}")
print(f"Holistic dynamic     : corr={m_holistic['corr']:+.3f}  rmse={m_holistic['rmse']:.1f}  std={m_holistic['pred_std']:.2f}")
print(f"Holistic vs AR-blind delta corr: {m_holistic['corr']-m_ar['corr']:+.3f}")
print(f"Std reach (test)     : true={np.std(v_test):.2f}  pred={m_holistic['pred_std']:.2f}")

# ------- SAVE for viewer -------
out = dict(
    t_train=t_train.tolist(),
    v_train=v_train.tolist(),
    t_test=t_test.tolist(),
    v_test=v_test.tolist(),
    y_pred=y_pred.tolist(),
    ar_blind=ar_blind.tolist(),
    y_mean=y_mean.tolist(),
    metrics=dict(holistic=m_holistic, mean=m_mean, ar_blind=m_ar),
    rungs=list(stats.keys()),
    base_amplitude=base,
    k_ref=k_ref,
    n_generated_cycles={str(k):len(c) for k,c in generated.items()},
    coupling_used={f"{k1}_{k2}":coupling_strength(k1,k2)
                   for k1 in stats for k2 in stats if k1<k2 and abs(coupling_strength(k1,k2))>0.30},
)
with open(OUT_PATH, 'w', encoding='utf-8') as f:
    f.write("window.HOLISTIC_DYN = " + json.dumps(out) + ";\n")
print("Saved -> " + OUT_PATH)

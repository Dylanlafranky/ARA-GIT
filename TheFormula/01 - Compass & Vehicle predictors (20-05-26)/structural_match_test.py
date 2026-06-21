"""
For an OPEN SYSTEM (heart receives input from brain/nervous system), we cannot
predict point values from history alone. But we CAN predict structural properties:
  - distribution of cycle durations (per rung)
  - distribution of ARA values (per rung)
  - spectral structure (peaks at φ-related frequencies)

This test compares the dual-side generator's STRUCTURAL output against the
actual second-half ECG, to show whether the framework captures the system's
statistical signature even when point match is impossible.
"""
import json, re, math, os
import numpy as np, pandas as pd

PHI = 1.6180339887498949
def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

def load_blob(path, var):
    txt = open(path,'r',encoding='utf-8').read()
    m = re.search(re.escape(var) + r"\s*=\s*(\{.*\});?\s*$", txt, re.DOTALL)
    return json.loads(m.group(1))

PER_RUNG = _resolve(r"F:\SystemFormulaFolder\TheFormula\per_rung_seq_ara.js")
DUAL     = _resolve(r"F:\SystemFormulaFolder\TheFormula\dual_side_data.js")
OUT      = _resolve(r"F:\SystemFormulaFolder\TheFormula\structural_match_data.js")

per_rung = load_blob(PER_RUNG, "window.PER_RUNG_SEQ")
dual     = load_blob(DUAL,     "window.DUAL_SIDE")

# Get the held-out (test-half) cycle distributions per rung — observed truth
T_train_end = max(dual['t_train'])  # last train sample
print(f"Train end: {T_train_end:.0f}s, rungs: {dual['rungs']}")

# Reconstruct ground-truth test cycles per rung from per_rung_seq_ara.js
truth = {}
for k_str, info in per_rung.items():
    k = int(k_str)
    starts = np.array(info['cycle_starts']); aras = np.array(info['cycle_aras'])
    test_mask = starts >= T_train_end
    if test_mask.sum() < 2: continue
    starts_te = starts[test_mask]; aras_te = aras[test_mask]
    durs_te = np.diff(starts_te)
    truth[k] = dict(durs=durs_te.tolist(), aras=aras_te[:-1].tolist())

# Generated test cycles from dual-side prediction (we have n_generated_cycles count, but not the per-cycle list)
# Re-run the cycle generator to capture per-cycle durations and ARAs (deterministic with same seed)
np.random.seed(42)
COUPLE = _resolve(r"F:\SystemFormulaFolder\TheFormula\cross_rung_coupling.js")
coupling = load_blob(COUPLE, "window.CROSS_COUPLING")

stats = {}
for k_str, info in per_rung.items():
    k = int(k_str)
    starts = np.array(info['cycle_starts']); aras = np.array(info['cycle_aras'])
    train_mask = starts < T_train_end
    if train_mask.sum() < 4: continue
    s_tr = starts[train_mask]; a_tr = aras[train_mask]
    durs_tr = np.diff(s_tr) if len(s_tr) >= 2 else np.array([PHI**k])
    stats[k] = dict(
        mean_ARA=float(np.mean(a_tr)), std_ARA=float(np.std(a_tr)),
        lag1=float(np.corrcoef(a_tr[:-1], a_tr[1:])[0,1]) if len(a_tr)>=3 and np.std(a_tr)>1e-6 else 0.0,
        mean_dur=float(np.mean(durs_tr)), std_dur=float(np.std(durs_tr)),
        last_start=float(s_tr[-1]), last_ARA=float(a_tr[-1])
    )
    if not np.isfinite(stats[k]['lag1']): stats[k]['lag1']=0.0

T_test_end = max(dual['t_test'])
def ar1(prev, mean, std, lag1):
    eps_std = std * math.sqrt(max(1e-9, 1.0 - lag1*lag1))
    return mean + lag1*(prev - mean) + np.random.normal(0.0, eps_std)

generated = {}
for k,s in stats.items():
    cycles = []
    cur_t = s['last_start'] + s['mean_dur']; cur_a = s['last_ARA']
    while cur_t < T_test_end:
        cur_a = float(np.clip(ar1(cur_a, s['mean_ARA'], s['std_ARA'], s['lag1']), 0.3, 4.0))
        dur = float(max(s['mean_dur']*0.3, np.random.normal(s['mean_dur'], s['std_dur'])))
        cycles.append(dict(start=cur_t, dur=dur, ARA=cur_a))
        cur_t += dur
    generated[k] = cycles

# Coupling overlay
cl = {}
for kk,info in coupling.items():
    cl[(info['k1'],info['k2'])] = info; cl[(info['k2'],info['k1'])] = info
def couple(a,b):
    i = cl.get((a,b)); return float(i.get('ara_corr',0.0)) if i else 0.0
for k,cyc in generated.items():
    for c in cyc:
        midt = c['start'] + c['dur']*0.5
        adj=0.0; wsum=0.0
        for k2,cyc2 in generated.items():
            if k2==k: continue
            w = couple(k,k2)
            if abs(w)<0.30: continue
            for c2 in cyc2:
                if c2['start'] <= midt <= c2['start']+c2['dur']:
                    adj+=w*(c2['ARA']-c['ARA']); wsum+=abs(w); break
        if wsum>0:
            c['ARA'] = float(np.clip(c['ARA']+adj/(wsum*PHI*PHI), 0.3, 4.0))

predicted = {k: dict(durs=[c['dur'] for c in cyc], aras=[c['ARA'] for c in cyc])
             for k,cyc in generated.items()}

# --- KS test on durations + ARAs per rung ---
def ks(a,b):
    a = np.sort(np.asarray(a)); b = np.sort(np.asarray(b))
    if len(a)==0 or len(b)==0: return 1.0
    grid = np.linspace(min(a.min(),b.min()), max(a.max(),b.max()), 200)
    cA = np.searchsorted(a, grid)/len(a); cB = np.searchsorted(b, grid)/len(b)
    return float(np.max(np.abs(cA-cB)))

print("\n=== STRUCTURAL MATCH (predicted cycle distributions vs ground-truth test-half) ===")
print(f"{'rung':>5}  {'truth_n':>7}  {'pred_n':>6}  {'KS_dur':>7}  {'KS_ARA':>7}  {'mean_dur_err%':>13}  {'mean_ARA_err%':>13}")
results = {}
for k in sorted(truth.keys()):
    if k not in predicted: continue
    td = truth[k]['durs']; pa = predicted[k]['durs']
    ta = truth[k]['aras']; pA = predicted[k]['aras']
    if not pa: continue
    ks_d = ks(td, pa); ks_a = ks(ta, pA)
    md_err = 100*abs(np.mean(pa)-np.mean(td))/np.mean(td) if td else 0
    mA_err = 100*abs(np.mean(pA)-np.mean(ta))/np.mean(ta) if ta else 0
    print(f"  k={k:2d}  {len(td):7d}  {len(pa):6d}  {ks_d:7.3f}  {ks_a:7.3f}  {md_err:13.1f}  {mA_err:13.1f}")
    results[k] = dict(truth_n=len(td), pred_n=len(pa), ks_dur=ks_d, ks_ara=ks_a,
                      mean_dur_truth=float(np.mean(td)), mean_dur_pred=float(np.mean(pa)),
                      mean_ara_truth=float(np.mean(ta)), mean_ara_pred=float(np.mean(pA)),
                      truth_durs=list(map(float,td)), pred_durs=list(map(float,pa)),
                      truth_aras=list(map(float,ta)), pred_aras=list(map(float,pA)))

# --- φ-frequency check: ratio of consecutive cycle durations should approach φ ---
print("\n=== φ-RATIO of consecutive rungs (mean dur ratio across adjacent rungs) ===")
ks_keys = sorted(results.keys())
for i in range(len(ks_keys)-1):
    k1, k2 = ks_keys[i], ks_keys[i+1]
    if k2 - k1 == 0: continue
    ratio_truth = results[k2]['mean_dur_truth']/results[k1]['mean_dur_truth']
    ratio_pred  = results[k2]['mean_dur_pred']/results[k1]['mean_dur_pred']
    expected    = PHI**(k2-k1)
    print(f"  φ^{k1}→φ^{k2}: expected φ^{k2-k1}={expected:.3f}  truth={ratio_truth:.3f}  pred={ratio_pred:.3f}")

# --- Spectral comparison on raw values ---
v_test = np.array(dual['v_test']); y_pred = np.array(dual['y_pred'])
v_test_c = v_test - np.mean(v_test); y_pred_c = y_pred - np.mean(y_pred)
freqs = np.fft.rfftfreq(len(v_test), d=0.5)
P_true = np.abs(np.fft.rfft(v_test_c))**2
P_pred = np.abs(np.fft.rfft(y_pred_c))**2

# Compare power at φ-related frequencies (rung k corresponds to f = 1/(φ^k seconds))
print("\n=== POWER at φ-rung BANDS (using period-targeted bandpass) ===")
phi_powers = {}
N = len(v_test); dt = 0.5
for k in sorted(stats.keys()):
    T_k = PHI**k  # seconds
    f_center = 1.0 / T_k
    # band: ±20% around center
    f_lo, f_hi = 0.8*f_center, 1.2*f_center
    idx_lo = max(1, int(f_lo * N * dt))
    idx_hi = min(len(P_true)-1, int(f_hi * N * dt))
    if idx_hi <= idx_lo+1: continue
    pt = float(np.sum(P_true[idx_lo:idx_hi]))/float(np.sum(P_true[1:]))
    pp = float(np.sum(P_pred[idx_lo:idx_hi]))/float(np.sum(P_pred[1:]))
    rel = pp/pt if pt>0 else 0
    print(f"  φ^{k} (T={T_k:.0f}s, f={f_center:.5f}Hz, {idx_hi-idx_lo} bins): truth={pt*100:.2f}%  pred={pp*100:.2f}%  ratio={rel:.2f}")
    phi_powers[k] = dict(f_hz=float(f_center), period_s=float(T_k), truth_frac=pt, pred_frac=pp, ratio=rel)


out = dict(
    per_rung_match=results,
    phi_power_match=phi_powers,
    train_end=T_train_end,
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.STRUCT_MATCH = " + json.dumps(out) + ";\n")
print("Saved -> " + OUT)

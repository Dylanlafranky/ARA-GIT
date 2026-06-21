"""
Multi-pair closed-system vehicle.

Walker pair (ENSO+SOI at φ⁸) is the established closed pair (corr -0.97).
Empirical search found two additional anti-phase pairs:
  - PDO↔SOI at φ¹⁰ (corr -0.75) — Pacific decadal × atmospheric pressure
  - AMO↔IOD at φ¹² (corr -0.78) — inter-basin long-period coupling

Test variants:
  V_BASE: ENSO+SOI only (current closed-system vehicle)
  V_PAIR2_PDO: + PDO-SOI at φ¹⁰
  V_PAIR2_AMO: + AMO-IOD at φ¹²
  V_BOTH: + both extra pairs

Hypothesis: if multiple matched-rung pairs lift h=24, the framework's
higher-level ARA structure (multiple closed pairs forming a fractal level)
has empirical support. If just one pair helps, it's about that specific
coupling not the fractal level.
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949
INV_PHI3 = 1.0 / (PHI**3)
INV_PHI4 = 1.0 / (PHI**4)

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
AMO_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\amonuslong.txt")
TNA_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\tna.txt")
PDO_PATH  = _resolve(r"F:\SystemFormulaFolder\PDO_NOAA\ersst.v5.pdo.dat")
IOD_PATH  = _resolve(r"F:\SystemFormulaFolder\IOD_NOAA\dmi.had.long.data")
SOI_PATH  = _resolve(r"F:\SystemFormulaFolder\SOI_NOAA\soi.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\rolling_vehicle_multipair_data.js")

def load_nino():
    df = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
    df['date'] = pd.to_datetime(df['date'].str.strip())
    df = df[df['val'] > -90].copy()
    return df.set_index('date')['val'].astype(float)
def load_grid_text(path, header_lines=1):
    rows=[]
    with open(path,'r') as f:
        for _ in range(header_lines): next(f)
        for ln in f:
            parts = ln.split()
            if len(parts) < 13: continue
            try: year = int(parts[0])
            except: continue
            for m in range(12):
                try: v = float(parts[1+m])
                except: continue
                if v < -90 or v > 90: continue
                rows.append((pd.Timestamp(year=year, month=m+1, day=1), v))
    return pd.Series(dict(rows)).sort_index()
def load_iod_or_soi(p, hdr=1):
    rows=[]
    with open(p) as f:
        for _ in range(hdr): next(f)
        for ln in f:
            parts = ln.split()
            if len(parts)<13: continue
            try: year=int(parts[0])
            except: continue
            if year<1900 or year>2100: continue
            for m in range(12):
                try: v=float(parts[1+m])
                except: continue
                if v<-90: continue
                rows.append((pd.Timestamp(year=year,month=m+1,day=1),v))
    return pd.Series(dict(rows)).sort_index()

print("Loading...")
nino = load_nino()
amo = load_grid_text(AMO_PATH); tna = load_grid_text(TNA_PATH)
pdo = load_grid_text(PDO_PATH, header_lines=2); iod = load_iod_or_soi(IOD_PATH)
soi = load_iod_or_soi(SOI_PATH)
def to_monthly(s):
    s = s.copy(); s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()
nino,amo,tna,pdo,iod,soi = [to_monthly(x) for x in [nino,amo,tna,pdo,iod,soi]]
common = nino.index
for s in [amo, tna, pdo, iod, soi]:
    common = common.intersection(s.index)
common = common.sort_values()
NINO = nino.reindex(common).values.astype(float)
AMO  = amo.reindex(common).values.astype(float)
TNA  = tna.reindex(common).values.astype(float)
PDO  = pdo.reindex(common).values.astype(float)
IOD  = iod.reindex(common).values.astype(float)
SOI  = soi.reindex(common).values.astype(float)
DATES = common; N = len(NINO)
print(f"  N={N} months common, {DATES[0].date()} to {DATES[-1].date()}")

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n = len(arr); f_c = 1.0/period_units; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    try:
        b, a = butter(order, [Wn_lo, Wn_hi], btype='bandpass')
        return lfilter(b, a, arr - np.mean(arr))
    except Exception:
        return np.zeros(n)

def read_amp_theta(bp_to_t):
    if len(bp_to_t) < 2: return 0.0, 0.0
    n_recent = min(50, len(bp_to_t))
    amp = float(np.std(bp_to_t[-n_recent:]) * np.sqrt(2)) + 1e-9
    last = bp_to_t[-1]; rate = bp_to_t[-1] - bp_to_t[-2]
    ratio = max(-0.99, min(0.99, last/amp))
    return amp, np.arccos(ratio) * (-1 if rate > 0 else 1)

def per_rung_ARA_causal(arr_train, period):
    bp = causal_bandpass(arr_train, period, bw=0.85)
    if len(bp) < 3*int(period): return 1.0
    smoothed = gaussian_filter1d(bp, max(1, int(period * 0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.7)))
    if len(peaks) < 2: return 1.0
    aras = []
    for i in range(len(peaks)-1):
        seg = smoothed[peaks[i]:peaks[i+1]+1]
        if len(seg) < 3: continue
        f_t = max(0.15, min(0.85, int(np.argmin(seg)) / max(1, len(seg)-1)))
        aras.append((1 - f_t) / f_t)
    if not aras: return 1.0
    return float(np.mean(np.clip(aras, 0.3, 3.0)))

# ===== FRAMEWORK CONSTANTS =====
RUNGS = [(k, PHI**k) for k in range(4, 14)]
N_RUNGS = len(RUNGS)
K_REF = 8  # ENSO home rung
K_REF_IDX = next(i for i,(k,_) in enumerate(RUNGS) if k == K_REF)
RUNG_WEIGHTS = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
RUNG_WEIGHTS = RUNG_WEIGHTS / np.sum(RUNG_WEIGHTS)

# Define second-pair candidates as (target, partner, sign, shared_rung_k)
# Walker pair is always present: (ENSO, SOI, -1, 8)
# Plus optional second pair contributing to ENSO via topology
SECOND_PAIRS = {
    'PDO_SOI_phi10': dict(target='PDO', partner='SOI', sign=-1, k_pair=10, raw_corr=-0.75),
    'AMO_IOD_phi12': dict(target='AMO', partner='IOD', sign=-1, k_pair=12, raw_corr=-0.78),
}

# ECG amp template (from previous test)
ECG_PROFILE = {-19:0.000,-18:0.177,-17:0.361,-16:0.467,-15:0.452,-14:0.507,-13:0.553,
               -12:0.583,-11:0.599,-10:0.613,-9:0.654,-8:0.690,-7:0.712,-6:0.741,-5:0.773,
               -4:0.823,-3:0.807,-2:0.797,-1:0.984,0:1.000,1:0.774}
def ecg_template_value(rel_k):
    if rel_k in ECG_PROFILE: return ECG_PROFILE[rel_k]
    if rel_k > 1 and -rel_k in ECG_PROFILE: return ECG_PROFILE[-rel_k]
    return 0.5
ECG_AMP_TEMPLATE = np.array([ecg_template_value(k - K_REF) for k,_ in RUNGS])

SYS_ALL = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD, SOI=SOI)

def vehicle(refit_t, h, last_residual, second_pairs, alpha_template=0.5):
    """second_pairs: list of dict(target, partner, sign, k_pair) representing
    additional matched-rung anti-phase pairs to add as closed-pair contributions
    on top of the always-on Walker pair (ENSO+SOI at φ⁸)."""
    arr_train = NINO[:refit_t]
    mean_train = float(np.mean(arr_train))
    nino_scale = float(np.std(arr_train)) + 1e-9

    bp = {}
    for nm in SYS_ALL:
        bp[nm] = [causal_bandpass(SYS_ALL[nm][:refit_t], p) for k,p in RUNGS]

    state = {}
    for nm in SYS_ALL:
        for ri, (k, p) in enumerate(RUNGS):
            a, th = read_amp_theta(bp[nm][ri])
            ara = per_rung_ARA_causal(SYS_ALL[nm][:refit_t], p) if nm == 'NINO' else 1.0
            state[(nm, ri)] = (a, th, ara)

    # Apply ECG amp template to NINO rungs
    base_amp_nino = state[('NINO', K_REF_IDX)][0]
    for ri in range(N_RUNGS):
        obs_amp, th, ara = state[('NINO', ri)]
        template_amp = base_amp_nino * ECG_AMP_TEMPLATE[ri]
        blended = (1-alpha_template)*obs_amp + alpha_template*template_amp
        state[('NINO', ri)] = (blended, th, ara)

    # Forward project all systems
    nino_rung_future = []
    feeder_rung_future = {nm: [] for nm in SYS_ALL if nm != 'NINO'}
    for ri, (k, p) in enumerate(RUNGS):
        a_n, th_n, ara_n = state[('NINO', ri)]
        new_th_n = th_n + 2*np.pi*h/p
        kappa = 0.05
        decay_n = np.exp(-abs(ara_n - PHI) * h / p * kappa)
        nino_rung_future.append(a_n * decay_n * np.cos(new_th_n))
        for nm in SYS_ALL:
            if nm == 'NINO': continue
            a_f, th_f, _ = state[(nm, ri)]
            new_th_f = th_f + 2*np.pi*h/p
            feeder_rung_future[nm].append(a_f * np.cos(new_th_f))

    nino_rung_future = np.array(nino_rung_future)
    own_pred = float(np.dot(RUNG_WEIGHTS, nino_rung_future))

    # === Walker pair (always on): SOI matched-rung at φ⁸ to NINO ===
    soi_arr = np.array(feeder_rung_future['SOI'])
    soi_scale = float(np.std(SOI[:refit_t])) + 1e-9
    soi_norm = soi_arr / soi_scale * nino_scale
    walker_contrib = -1.0 * 1.0 * soi_norm[K_REF_IDX] * RUNG_WEIGHTS[K_REF_IDX] * 5
    for ri in range(N_RUNGS):
        if ri == K_REF_IDX: continue
        walker_contrib += -1.0 * (1.0/PHI**abs(RUNGS[ri][0]-K_REF)) * INV_PHI4 * soi_norm[ri] * RUNG_WEIGHTS[ri]

    # === Other incidental feeders (AMO/TNA/IOD at 1/φ⁴ blend) ===
    incidental_pred = 0.0
    incidental_signs = dict(AMO=+1, TNA=+1, PDO=-1, IOD=+1)
    for fn in ['AMO','TNA','PDO','IOD']:
        feeder_arr = np.array(feeder_rung_future[fn])
        sign = incidental_signs[fn]
        f_scale = float(np.std(SYS_ALL[fn][:refit_t])) + 1e-9
        feeder_arr_norm = feeder_arr / f_scale * nino_scale
        incidental_pred += INV_PHI4 * sign * float(np.dot(RUNG_WEIGHTS, feeder_arr_norm)) / 4.0

    # === Second pairs: additional matched-rung anti-phase contributions ===
    # The framework's claim: another closed pair shares topology with NINO at its
    # shared rung, so its anti-phase signal informs NINO at THAT rung specifically.
    # Couple via the relative position of the pair's shared rung from NINO's home rung.
    second_pair_pred = 0.0
    for sp in second_pairs:
        target_arr = np.array(feeder_rung_future[sp['target']])
        partner_arr = np.array(feeder_rung_future[sp['partner']])
        t_scale = float(np.std(SYS_ALL[sp['target']][:refit_t])) + 1e-9
        p_scale = float(np.std(SYS_ALL[sp['partner']][:refit_t])) + 1e-9
        target_norm = target_arr / t_scale * nino_scale
        partner_norm = partner_arr / p_scale * nino_scale
        # The pair's contribution to NINO via vertical-ARA from rung k_pair to NINO rung K_REF
        # Pair anti-phase signal at their shared rung: avg of (target - sign*partner)
        # then scaled by 1/φ^|k_pair - K_REF| (vertical coupling)
        ri_pair = next(i for i,(k,_) in enumerate(RUNGS) if k == sp['k_pair'])
        pair_signal = 0.5 * (target_norm[ri_pair] - sp['sign'] * partner_norm[ri_pair])
        # Contribute to NINO with weight scaled by vertical-ARA from k_pair to k_ref
        weight = PHI**(-abs(sp['k_pair'] - K_REF))
        # Sign of contribution: depends on whether the pair's target is in-phase or anti-phase with NINO
        # at the shared rung. We measured these from the bandpassed correlations earlier.
        # PDO-SOI pair: target=PDO is +0.74 with NINO at φ¹⁰ → in-phase → +1
        # AMO-IOD pair: target=AMO is uncorrelated with NINO → use partner sign instead
        # Use a simple rule: target's sign with NINO at the shared rung (precomputed)
        target_to_nino_sign = sp.get('target_to_nino_sign', +1)
        second_pair_pred += target_to_nino_sign * weight * pair_signal * 2  # factor 2 for matched-pair strength

    structural_pred = mean_train + own_pred + walker_contrib + incidental_pred + second_pair_pred
    pred = structural_pred + INV_PHI3 * last_residual
    truth = NINO[refit_t + h - 1]
    return pred, truth

# ===== Rolling loop =====
HORIZONS = [1, 3, 6, 12, 24]
MIN_TRAIN = 30 * 12
STEP = 12

# Pre-compute target-to-nino sign for each second pair
print("\nPair target-to-NINO sign at shared rung:")
for name, sp in SECOND_PAIRS.items():
    bp_t = causal_bandpass(SYS_ALL[sp['target']], PHI**sp['k_pair'])
    bp_n = causal_bandpass(NINO, PHI**sp['k_pair'])
    warm = N//4
    c = float(np.corrcoef(bp_t[warm:], bp_n[warm:])[0,1])
    sp['target_to_nino_sign'] = +1 if c > 0 else -1
    print(f"  {name}: {sp['target']} ↔ NINO at φ^{sp['k_pair']}: corr={c:+.2f}, sign={sp['target_to_nino_sign']:+d}")

print(f"\n  Rolling vehicle with multi-pair coupling")

results_by_variant = {}
variants = {
    'BASE (Walker only)': [],
    '+ PDO-SOI φ¹⁰': [SECOND_PAIRS['PDO_SOI_phi10']],
    '+ AMO-IOD φ¹²': [SECOND_PAIRS['AMO_IOD_phi12']],
    '+ both pairs': [SECOND_PAIRS['PDO_SOI_phi10'], SECOND_PAIRS['AMO_IOD_phi12']],
}

for variant_name, second_pairs in variants.items():
    print(f"\n--- {variant_name} ---")
    results = {h: [] for h in HORIZONS}
    last_residual = 0.0
    t_start = time.time()
    for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
        for h in HORIZONS:
            if refit_t + h - 1 >= N: continue
            pred, truth = vehicle(refit_t, h, last_residual, second_pairs)
            results[h].append((refit_t, pred, truth))
        if results[1]:
            last_residual = float(results[1][-1][2] - results[1][-1][1])
    print(f"  {time.time()-t_start:.1f}s")

    print(f"  {'horizon':>10}  {'corr':>7}  {'MAE':>7}  {'R²(clim)':>9}  {'R²(pers)':>9}  {'dir':>6}")
    metrics = {}
    clim_pred = float(np.mean(NINO))
    for h in HORIZONS:
        if not results[h]: continue
        preds = np.array([r[1] for r in results[h]])
        truths = np.array([r[2] for r in results[h]])
        pers_preds = np.array([NINO[r[0]-1] for r in results[h]])
        corr = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds)>1e-9 and np.std(truths)>1e-9 else 0.0
        mae = float(np.mean(np.abs(preds - truths)))
        ss_res = np.sum((truths - preds)**2)
        ss_clim = np.sum((truths - clim_pred)**2)
        ss_pers = np.sum((truths - pers_preds)**2)
        r2_clim = float(1 - ss_res/ss_clim) if ss_clim > 0 else 0.0
        r2_pers = float(1 - ss_res/ss_pers) if ss_pers > 0 else 0.0
        dir_acc = float(np.mean(np.sign(preds - pers_preds) == np.sign(truths - pers_preds)))
        print(f"  h={h:>2} mo  {corr:+.3f}  {mae:.3f}    {r2_clim:+.3f}    {r2_pers:+.3f}    {dir_acc*100:5.1f}%")
        metrics[h] = dict(corr=corr, mae=mae, r2_clim=r2_clim, r2_pers=r2_pers, dir_acc=dir_acc, n=len(results[h]))
    results_by_variant[variant_name] = metrics

out = dict(method="Multi-pair closed-system test: Walker + secondary anti-phase pairs",
           pairs_tested={k: dict(target=v['target'], partner=v['partner'],
                                  k_pair=v['k_pair'], raw_corr=v['raw_corr'],
                                  target_to_nino_sign=v.get('target_to_nino_sign'))
                          for k,v in SECOND_PAIRS.items()},
           results_by_variant=results_by_variant)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.VEHICLE_MULTIPAIR = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

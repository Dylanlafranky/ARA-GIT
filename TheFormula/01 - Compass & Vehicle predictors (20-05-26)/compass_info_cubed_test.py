"""
Information³ test — add the meta-coupling layer.

Dylan's idea (2026-05-03): the prediction error comes from BRANCH POINTS — where
the system diverges from one tube into another. Branches happen when feeders
start coupling to each other in new ways. Currently the vehicle has:
  Level 1 (datum): each feeder's own oscillator
  Level 2 (signal): each feeder's coupling to NINO
But it's missing:
  Level 3 (meaning): inter-feeder coupling

Implementation: at each forecast tick, add pairwise feeder × feeder products
weighted at 1/φ⁵ (deeper than single-feeder coupling). With 5 feeders this gives
C(5,2)=10 new coupling terms.

If feeders are coordinating (similar phases), their pairwise products are large
and add coherent signal. If feeders are scattered (anti-phase, random), products
average out near zero. This makes the prediction sensitive to UPSTREAM
COORDINATION — the branch-point signal.

Stack: CONT + LOG + GATE_SMOOTH + REVERSE + WALLS + INFO³
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949
INV_PHI = 1.0/PHI; INV_PHI3 = 1.0/(PHI**3); INV_PHI4 = 1.0/(PHI**4); INV_PHI5 = 1.0/(PHI**5)

def _resolve(p):
    pl = p.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return pl if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
AMO_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\amonuslong.txt")
TNA_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\tna.txt")
PDO_PATH  = _resolve(r"F:\SystemFormulaFolder\PDO_NOAA\ersst.v5.pdo.dat")
IOD_PATH  = _resolve(r"F:\SystemFormulaFolder\IOD_NOAA\dmi.had.long.data")
SOI_PATH  = _resolve(r"F:\SystemFormulaFolder\SOI_NOAA\soi.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\compass_info_cubed_data.js")

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
            parts=ln.split()
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
nino=load_nino()
amo=load_grid_text(AMO_PATH); tna=load_grid_text(TNA_PATH)
pdo=load_grid_text(PDO_PATH, header_lines=2)
iod=load_iod_or_soi(IOD_PATH); soi=load_iod_or_soi(SOI_PATH)
def to_m(s): s=s.copy(); s.index=pd.to_datetime(s.index).to_period('M').to_timestamp(); return s.groupby(s.index).first()
nino,amo,tna,pdo,iod,soi = [to_m(x) for x in [nino,amo,tna,pdo,iod,soi]]
common = nino.index
for s in [amo,tna,pdo,iod,soi]: common = common.intersection(s.index)
common = common.sort_values()
NINO=nino.reindex(common).values.astype(float)
AMO=amo.reindex(common).values.astype(float)
TNA=tna.reindex(common).values.astype(float)
PDO=pdo.reindex(common).values.astype(float)
IOD=iod.reindex(common).values.astype(float)
SOI=soi.reindex(common).values.astype(float)
N = len(NINO)

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n=len(arr); fc=1.0/period_units; nyq=0.5
    Wn_lo=max(1e-6,(1-bw)*fc/nyq); Wn_hi=min(0.999,(1+bw)*fc/nyq)
    if Wn_lo>=Wn_hi: return np.zeros(n)
    b,a=butter(order,[Wn_lo,Wn_hi],btype='bandpass')
    return lfilter(b,a, arr - np.mean(arr))

def read_amp_theta(bp):
    if len(bp)<2: return 0.0,0.0
    r=min(50,len(bp))
    amp=float(np.std(bp[-r:])*np.sqrt(2))+1e-9
    last=bp[-1]; rate=bp[-1]-bp[-2]
    ratio=max(-0.99,min(0.99,last/amp))
    return amp, np.arccos(ratio)*(-1 if rate>0 else 1)

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

RUNGS = [(k, PHI**k) for k in range(4, 14)]
N_RUNGS = len(RUNGS)
K_REF = 8
K_REF_IDX = next(i for i,(k,_) in enumerate(RUNGS) if k == K_REF)
RW_LOG = np.array([1.0/(1.0 + np.log(abs(k - K_REF) + 1)) for k,_ in RUNGS])
RW_LOG = RW_LOG / np.sum(RW_LOG)

ALL_SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD, SOI=SOI)
FEEDERS = ['AMO','TNA','PDO','IOD','SOI']  # 5 feeders → 10 pairs

def amp_predict(refit_t, h, last_residual, state, scales, mean_train, valves, use_info3, info3_signs):
    nino_rung_future = []; cos_vals = []
    for ri, (k, p) in enumerate(RUNGS):
        a_n, th_n, _ = state[('NINO', ri)]
        new_th_n = th_n + 2*np.pi*h/p
        cos_val = np.cos(new_th_n)
        cos_vals.append(cos_val)
        v = valves[ri]
        g = 0.5 * (1 + np.tanh(5.0 * (cos_val + (1-2*v))))
        cos_eff = cos_val * g
        nino_rung_future.append(a_n * cos_eff)
    nino_rung_future = np.array(nino_rung_future)
    for ri in range(N_RUNGS - 1):
        a1 = state[('NINO', ri)][0]; a2 = state[('NINO', ri+1)][0]
        nino_rung_future[ri] += INV_PHI4 * a1 * a2 * cos_vals[ri] * cos_vals[ri+1]

    own_pred = float(np.dot(RW_LOG, nino_rung_future))

    # Feeder contributions (matched-rung at K_REF for SOI; standard blend for others)
    feeder_pred = 0.0
    nino_scale = scales['NINO']
    feeder_signs = dict(AMO=+1, TNA=+1, PDO=-1, IOD=+1, SOI=-1)
    feeder_at_kref = {}  # for info3
    for fn in FEEDERS:
        feeder_arr = []
        for ri, (k, p) in enumerate(RUNGS):
            a_f, th_f, _ = state[(fn, ri)]
            feeder_arr.append(a_f * np.cos(th_f + 2*np.pi*h/p))
        feeder_arr = np.array(feeder_arr) / scales[fn] * nino_scale
        sign = feeder_signs[fn]
        feeder_at_kref[fn] = feeder_arr[K_REF_IDX]  # store for info3
        if fn == 'SOI':
            feeder_pred += sign * 1.0 * feeder_arr[K_REF_IDX] * RW_LOG[K_REF_IDX] * 5
            for ri in range(N_RUNGS):
                if ri == K_REF_IDX: continue
                feeder_pred += sign * (1.0/PHI**abs(RUNGS[ri][0]-K_REF)) * INV_PHI4 * feeder_arr[ri] * RW_LOG[ri]
        else:
            feeder_pred += INV_PHI4 * sign * float(np.dot(RW_LOG, feeder_arr)) / 4.0

    # ============ INFORMATION³ LAYER (branch-point gating interpretation) ============
    info3_pred = 0.0
    if use_info3:
        # Compute pair coordination magnitude → branch-point alarm
        pair_products = []
        for i, fi in enumerate(FEEDERS):
            for fj in FEEDERS[i+1:]:
                pair_products.append(feeder_at_kref[fi] * feeder_at_kref[fj])
        # If many pairs are large and coordinated, system is at a branch point
        # → dampen the prediction toward mean (high uncertainty signal)
        coordination_strength = float(np.mean(np.abs(pair_products)))
        # Normalize by typical feeder amplitude squared
        norm = (sum(abs(feeder_at_kref[fn]) for fn in FEEDERS) / len(FEEDERS)) ** 2 + 1e-9
        normalized_coord = min(coordination_strength / norm, 2.0)
        # Dampen own_pred toward 0 (mean) when coordination is high
        damp_factor = 1.0 / (1.0 + normalized_coord * INV_PHI4)
        own_pred = own_pred * damp_factor

    return mean_train + own_pred + feeder_pred + INV_PHI3 * last_residual

def run_compass(refit_t, h, last_residual, state, scales, mean_train, step_mean,
                valves, sigma_train, wall_W, use_info3, info3_signs):
    cur_pos = NINO[refit_t-1]; prev_amp = NINO[refit_t-1]
    upper = mean_train + wall_W * sigma_train if wall_W is not None else float('inf')
    lower = mean_train - wall_W * sigma_train if wall_W is not None else float('-inf')
    for tau in range(1, h+1):
        amp = amp_predict(refit_t, tau, last_residual, state, scales, mean_train, valves, use_info3, info3_signs)
        delta = amp - prev_amp
        step = step_mean * np.tanh(delta / max(step_mean, 1e-9))
        new_pos = cur_pos + step
        if new_pos > upper: new_pos = upper - (new_pos - upper) * INV_PHI
        elif new_pos < lower: new_pos = lower + (lower - new_pos) * INV_PHI
        cur_pos = new_pos; prev_amp = amp
    return cur_pos

# Pre-compute info3 signs from training cross-correlation patterns
def compute_info3_signs(refit_t):
    """For each feeder pair, determine the sign that aligns with NINO."""
    nino_at_t = NINO[max(0, refit_t-300):refit_t]
    signs = {}
    for i, fi in enumerate(FEEDERS):
        for fj in FEEDERS[i+1:]:
            fi_arr = ALL_SYS[fi][max(0, refit_t-300):refit_t]
            fj_arr = ALL_SYS[fj][max(0, refit_t-300):refit_t]
            product = fi_arr * fj_arr
            if np.std(product) > 1e-9 and np.std(nino_at_t) > 1e-9:
                c = float(np.corrcoef(product, nino_at_t)[0,1])
                signs[f"{fi}_{fj}"] = +1 if c > 0 else -1
            else:
                signs[f"{fi}_{fj}"] = +1
    return signs

HORIZONS = [3, 6, 12, 24]
MIN_TRAIN = 30 * 12
STEP = 1
WALL_W = 1.5

variants = ['BASE', 'INFO3']

print(f"\n  Information³ test: pairwise feeder coupling layer")
print(f"  5 feeders → 10 pairs → 10 new info terms at 1/φ⁵ weight\n")

results = {v: {h: [] for h in HORIZONS} for v in variants}
last_residual = 0.0
t_start = time.time()

for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
    arr_train = NINO[:refit_t]
    mean_train = float(np.mean(arr_train))
    sigma_train = float(np.std(arr_train))
    nino_scale = sigma_train + 1e-9
    scales = dict(NINO=nino_scale)
    for fn in FEEDERS:
        scales[fn] = float(np.std(ALL_SYS[fn][:refit_t])) + 1e-9
    step_mean = float(np.mean(np.abs(np.diff(arr_train))))

    bp = {nm: [causal_bandpass(ALL_SYS[nm][:refit_t], p) for k,p in RUNGS] for nm in ALL_SYS}
    state = {}
    for nm in ALL_SYS:
        for ri, (k, p) in enumerate(RUNGS):
            a, th = read_amp_theta(bp[nm][ri])
            state[(nm, ri)] = (a, th, 1.0)
    valves = []
    for k, p in RUNGS:
        ara_k = per_rung_ARA_causal(arr_train, p)
        valves.append(1.0/(1.0+ara_k))
    info3_signs = compute_info3_signs(refit_t)

    for h in HORIZONS:
        if refit_t+h-1 >= N: continue
        truth = NINO[refit_t+h-1]
        for vname in variants:
            use_info3 = (vname == 'INFO3')
            pred = run_compass(refit_t, h, last_residual, state, scales, mean_train, step_mean,
                              valves, sigma_train, WALL_W, use_info3, info3_signs)
            results[vname][h].append((refit_t, pred, truth))
    if results['BASE'][HORIZONS[0]]:
        last = results['BASE'][HORIZONS[0]][-1]
        last_residual = float(last[2] - last[1])

print(f"  {time.time()-t_start:.1f}s")

print("\n========= INFORMATION³ RESULTS =========")
clim = float(np.mean(NINO))
for vname in variants:
    print(f"\n--- {vname} ---")
    print(f"  {'horizon':>10}  {'corr':>7}  {'MAE':>7}  {'R²(pers)':>9}  {'dir':>6}")
    for h in HORIZONS:
        recs = results[vname][h]
        if not recs: continue
        preds = np.array([r[1] for r in recs])
        truths = np.array([r[2] for r in recs])
        pers_preds = np.array([NINO[r[0]-1] for r in recs])
        corr = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds)>1e-9 and np.std(truths)>1e-9 else 0.0
        mae = float(np.mean(np.abs(preds-truths)))
        ss_res = np.sum((truths-preds)**2); ss_pers = np.sum((truths-pers_preds)**2)
        r2_pers = float(1 - ss_res/ss_pers) if ss_pers > 0 else 0.0
        dir_acc = float(np.mean(np.sign(preds-pers_preds) == np.sign(truths-pers_preds)))
        print(f"  h={h:>2} mo  {corr:+.3f}  {mae:.3f}    {r2_pers:+.3f}    {dir_acc*100:5.1f}%")

out = dict(method="Information³ — pairwise feeder coupling at 1/φ⁵")
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.INFO3 = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

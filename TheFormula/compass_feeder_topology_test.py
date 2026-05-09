"""
Feeder-shapes-topology test on the compass vehicle.
Three architectures, all preserving ENSO's identity (no feeder values added to prediction):

  B (γ-modulation): feeder coordination tunes AR feedback strength
  A (tube selection): NINO[t-1] + SOI[t-1] picks warm/neutral/cold tube; bias toward tube mean
  C (pre-correction): nudge initial position by feeder consensus z-score

Stack: CONT + LOG + GATE + REVERSE + WALLS (W=1.5σ) — current best
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949
INV_PHI = 1.0/PHI; INV_PHI3 = 1.0/(PHI**3); INV_PHI4 = 1.0/(PHI**4)

def _resolve(p):
    pl = p.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return pl if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
AMO_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\amonuslong.txt")
TNA_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\tna.txt")
PDO_PATH  = _resolve(r"F:\SystemFormulaFolder\PDO_NOAA\ersst.v5.pdo.dat")
IOD_PATH  = _resolve(r"F:\SystemFormulaFolder\IOD_NOAA\dmi.had.long.data")
SOI_PATH  = _resolve(r"F:\SystemFormulaFolder\SOI_NOAA\soi.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\compass_feeder_topology_data.js")

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
            parts=ln.split()
            if len(parts)<13: continue
            try: year=int(parts[0])
            except: continue
            for m in range(12):
                try: v=float(parts[1+m])
                except: continue
                if v<-90 or v>90: continue
                rows.append((pd.Timestamp(year=year,month=m+1,day=1),v))
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
nino,amo,tna,pdo,iod,soi=[to_m(x) for x in [nino,amo,tna,pdo,iod,soi]]
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
FEEDERS = ['AMO','TNA','PDO','IOD','SOI']

def amp_predict(refit_t, h, last_residual_eff, state, soi_scale, nino_scale, mean_train, valves):
    nino_rung_future = []; cos_vals = []
    for ri, (k, p) in enumerate(RUNGS):
        a_n, th_n, _ = state[('NINO', ri)]
        new_th_n = th_n + 2*np.pi*h/p
        cos_val = np.cos(new_th_n)
        cos_vals.append(cos_val)
        v = valves[ri]
        g = 0.5 * (1 + np.tanh(5.0 * (cos_val + (1-2*v))))
        nino_rung_future.append(a_n * cos_val * g)
    nino_rung_future = np.array(nino_rung_future)
    for ri in range(N_RUNGS - 1):
        a1 = state[('NINO', ri)][0]; a2 = state[('NINO', ri+1)][0]
        nino_rung_future[ri] += INV_PHI4 * a1 * a2 * cos_vals[ri] * cos_vals[ri+1]
    own_pred = float(np.dot(RW_LOG, nino_rung_future))
    soi_rung_future = []
    for ri, (k, p) in enumerate(RUNGS):
        a_f, th_f, _ = state[('SOI', ri)]
        soi_rung_future.append(a_f * np.cos(th_f + 2*np.pi*h/p))
    soi_norm = np.array(soi_rung_future) / soi_scale * nino_scale
    walker = -1.0 * 1.0 * soi_norm[K_REF_IDX] * RW_LOG[K_REF_IDX] * 5
    for ri in range(N_RUNGS):
        if ri == K_REF_IDX: continue
        walker += -1.0 * (1.0/PHI**abs(RUNGS[ri][0]-K_REF)) * INV_PHI4 * soi_norm[ri] * RW_LOG[ri]
    return mean_train + own_pred + walker + last_residual_eff

def run_compass(refit_t, h, last_residual, state, soi_scale, nino_scale, mean_train,
                step_mean, valves, sigma_train, wall_W, wall_center, gamma_eff, start_pos):
    cur_pos = start_pos
    prev_amp = NINO[refit_t-1]
    if wall_W is not None:
        upper = wall_center + wall_W * sigma_train
        lower = wall_center - wall_W * sigma_train
    else:
        upper, lower = float('inf'), float('-inf')
    for tau in range(1, h+1):
        # AR feedback uses gamma_eff (which may be modulated)
        last_res_eff = gamma_eff * last_residual
        amp = amp_predict(refit_t, tau, last_res_eff, state, soi_scale, nino_scale, mean_train, valves)
        delta = amp - prev_amp
        step = step_mean * np.tanh(delta / max(step_mean, 1e-9))
        new_pos = cur_pos + step
        if new_pos > upper: new_pos = upper - (new_pos - upper) * INV_PHI
        elif new_pos < lower: new_pos = lower + (lower - new_pos) * INV_PHI
        cur_pos = new_pos
        prev_amp = amp
    return cur_pos

# ===== Feeder-derived signals =====
def feeder_coordination(refit_t, lookback=12):
    """Mean abs pairwise correlation among feeders over recent window. ∈ [0, 1]."""
    if refit_t < lookback + 5: return 0.0
    arrs = [ALL_SYS[fn][refit_t-lookback:refit_t] for fn in FEEDERS]
    pairs = []
    for i in range(len(arrs)):
        for j in range(i+1, len(arrs)):
            if np.std(arrs[i]) > 1e-9 and np.std(arrs[j]) > 1e-9:
                c = float(np.corrcoef(arrs[i], arrs[j])[0,1])
                pairs.append(abs(c))
    return float(np.mean(pairs)) if pairs else 0.0

def select_tube(refit_t, sigma_nino_train):
    """Pick tube based on NINO[t-1] sign + SOI[t-1] confirmation.
    Returns 'warm', 'cold', or 'neutral'."""
    if refit_t < 1: return 'neutral'
    n_now = NINO[refit_t-1]
    s_now = SOI[refit_t-1]
    threshold = 0.5 * sigma_nino_train
    # NINO and SOI are anti-correlated. Warm = NINO high + SOI low.
    if n_now > threshold and s_now < -0.5:
        return 'warm'
    elif n_now < -threshold and s_now > 0.5:
        return 'cold'
    else:
        return 'neutral'

def feeder_consensus(refit_t, lookback=6):
    """Mean z-score of feeders, signed for ENSO direction.
    AMO/TNA/IOD: in-phase with NINO (+sign); PDO and SOI flipped.
    Returns scalar ≈ feeder-implied direction."""
    if refit_t < lookback + 5: return 0.0
    sign_map = dict(AMO=+1, TNA=+1, PDO=+1, IOD=+1, SOI=-1)
    z_signed = []
    for fn in FEEDERS:
        arr_train = ALL_SYS[fn][:refit_t]
        if len(arr_train) < lookback: continue
        mu = float(np.mean(arr_train))
        sd = float(np.std(arr_train)) + 1e-9
        recent = float(np.mean(ALL_SYS[fn][refit_t-lookback:refit_t]))
        z_signed.append(sign_map[fn] * (recent - mu) / sd)
    return float(np.mean(z_signed)) if z_signed else 0.0

# ===== Rolling test =====
HORIZONS = [3, 6, 12, 24]
MIN_TRAIN = 30 * 12
STEP = 1
WALL_W = 1.5

variants = ['BASE', 'B_GAMMA', 'A_TUBE', 'C_PRECORR', 'ABC_ALL']

print(f"\n  Feeder-shapes-topology test: B (γ-mod), A (tube), C (pre-correct)")

results = {v: {h: [] for h in HORIZONS} for v in variants}
last_residual = 0.0
t_start = time.time()

for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
    arr_train = NINO[:refit_t]
    mean_train = float(np.mean(arr_train))
    sigma_train = float(np.std(arr_train))
    nino_scale = sigma_train + 1e-9
    soi_scale = float(np.std(SOI[:refit_t])) + 1e-9
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

    # Compute feeder signals
    coord = feeder_coordination(refit_t)
    tube = select_tube(refit_t, sigma_train)
    consensus = feeder_consensus(refit_t)

    # Tube center map (mean of NINO conditional on tube classification in training data)
    if tube == 'warm':
        tube_center = mean_train + 1.0 * sigma_train
    elif tube == 'cold':
        tube_center = mean_train - 1.0 * sigma_train
    else:
        tube_center = mean_train

    for h in HORIZONS:
        if refit_t+h-1 >= N: continue
        truth = NINO[refit_t+h-1]

        # BASE
        gamma_base = INV_PHI3
        pred_base = run_compass(refit_t, h, last_residual, state, soi_scale, nino_scale, mean_train,
                                 step_mean, valves, sigma_train, WALL_W, mean_train, gamma_base, NINO[refit_t-1])
        results['BASE'][h].append((refit_t, pred_base, truth))

        # B: γ modulated by feeder coordination
        gamma_B = INV_PHI3 * (1.0 + np.tanh(coord * 2.0))  # scale up to ~ 1/φ³ × (1+0.96) ≈ 0.46 max
        pred_B = run_compass(refit_t, h, last_residual, state, soi_scale, nino_scale, mean_train,
                              step_mean, valves, sigma_train, WALL_W, mean_train, gamma_B, NINO[refit_t-1])
        results['B_GAMMA'][h].append((refit_t, pred_B, truth))

        # A: tube center shifts walls
        pred_A = run_compass(refit_t, h, last_residual, state, soi_scale, nino_scale, mean_train,
                              step_mean, valves, sigma_train, WALL_W, tube_center, gamma_base, NINO[refit_t-1])
        results['A_TUBE'][h].append((refit_t, pred_A, truth))

        # C: pre-correction nudges initial position
        nudge = INV_PHI4 * consensus * sigma_train
        start_C = NINO[refit_t-1] + nudge
        pred_C = run_compass(refit_t, h, last_residual, state, soi_scale, nino_scale, mean_train,
                              step_mean, valves, sigma_train, WALL_W, mean_train, gamma_base, start_C)
        results['C_PRECORR'][h].append((refit_t, pred_C, truth))

        # ABC combined
        pred_abc = run_compass(refit_t, h, last_residual, state, soi_scale, nino_scale, mean_train,
                                step_mean, valves, sigma_train, WALL_W, tube_center, gamma_B, start_C)
        results['ABC_ALL'][h].append((refit_t, pred_abc, truth))

    if results['BASE'][HORIZONS[0]]:
        last = results['BASE'][HORIZONS[0]][-1]
        last_residual = float(last[2] - last[1])

print(f"  {time.time()-t_start:.1f}s")

print("\n========= FEEDER-TOPOLOGY RESULTS =========")
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

out = dict(method="Feeder-as-topology test (B, A, C)", variants=variants)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.FEEDER_TOPO = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

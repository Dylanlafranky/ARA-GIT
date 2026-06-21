"""
dynamic_rung_assignment_test.py

Dynamic per-rung matched-partner discovery with extended rung ladder.

Goal: lift 12-24mo prediction by populating ALL rungs (phi^3..phi^12) with the
best matched-rung partner found in training data only, instead of fixing
SOI->phi^8 manually.

Strict-causal protocol:
  - At each rolling refit origin t, we use ONLY arr[:t]. No data past t.
  - Per-rung partner assignment is recomputed at each refit on training data.
  - Causal Butterworth IIR bandpass (one-sided, no future leakage).
  - Forward projection deterministic from training-window state.

Algorithm (at each refit t):
  candidates = [AMO, TNA, PDO, IOD, SOI, QBO, SUNSPOTS] (only those with
               period * 2 <= training_span at this rung; rung-pinning rule)
  for each rung (k, p):
    if 2*p > t: skip rung (unpinned, would hurt)
    bp_nino = causal_bandpass(NINO[:t], p)
    score each candidate by |corr(bp_cand, bp_nino)| * sqrt(relative_power)
    pick best partner; sign of corr -> +1 in-phase / -1 anti-phase
    matched-rung weight for anti-phase, blend weight for in-phase

Vehicle then:
  pred = mean_train + sum_k(NINO_rung_future) * RUNG_WEIGHTS_k
       + sum_partners(partner_rung_future * sign * matched_weight)
       + gamma_eff(h) * last_h1_residual
  + lag-h corrector with horizon-conditional gamma (from prior test)

Compare to BASELINE which is the previous SOI_MATCHED vehicle (fixed assignment).
"""
import json, os, sys, time
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949
INV_PHI  = 1.0 / PHI
INV_PHI2 = 1.0 / PHI**2
INV_PHI3 = 1.0 / PHI**3
INV_PHI4 = 1.0 / PHI**4

# ---------- IO ----------
def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
AMO_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\amonuslong.txt")
TNA_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\tna.txt")
PDO_PATH  = _resolve(r"F:\SystemFormulaFolder\PDO_NOAA\ersst.v5.pdo.dat")
IOD_PATH  = _resolve(r"F:\SystemFormulaFolder\IOD_NOAA\dmi.had.long.data")
SOI_PATH  = _resolve(r"F:\SystemFormulaFolder\SOI_NOAA\soi.data")
QBO_PATH  = _resolve(r"F:\SystemFormulaFolder\QBO_NOAA\qbo.data")
SUN_PATH  = _resolve(r"F:\SystemFormulaFolder\solar_test\sunspots.txt")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\dynamic_rung_assignment_data.js")

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

def load_iod_or_soi(path):
    rows=[]
    with open(path) as f:
        next(f)
        for ln in f:
            parts = ln.split()
            if len(parts) < 13: continue
            try: year = int(parts[0])
            except: continue
            if year < 1900 or year > 2100: continue
            for m in range(12):
                try: v = float(parts[1+m])
                except: continue
                if v < -90: continue
                rows.append((pd.Timestamp(year=year, month=m+1, day=1), v))
    return pd.Series(dict(rows)).sort_index()

def load_sunspots():
    """SILSO monthly: year month decimal_year value -1 -1"""
    rows = []
    with open(SUN_PATH) as f:
        for ln in f:
            parts = ln.split()
            if len(parts) < 4: continue
            try:
                y = int(parts[0]); m = int(parts[1])
                v = float(parts[3])
            except: continue
            if v < -1: continue
            rows.append((pd.Timestamp(year=y, month=m, day=1), v))
    return pd.Series(dict(rows)).sort_index()

print("Loading data...")
nino = load_nino()
amo = load_grid_text(AMO_PATH); tna = load_grid_text(TNA_PATH)
pdo = load_grid_text(PDO_PATH, header_lines=2); iod = load_iod_or_soi(IOD_PATH)
soi = load_iod_or_soi(SOI_PATH); qbo = load_iod_or_soi(QBO_PATH)
sun = load_sunspots()

def to_monthly(s):
    s = s.copy(); s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()

nino, amo, tna, pdo, iod, soi, qbo, sun = [to_monthly(s) for s in (nino, amo, tna, pdo, iod, soi, qbo, sun)]
common = nino.index
for s in [amo, tna, pdo, iod, soi, qbo, sun]:
    common = common.intersection(s.index)
common = common.sort_values()
NINO = nino.reindex(common).values.astype(float)
AMO  = amo.reindex(common).values.astype(float)
TNA  = tna.reindex(common).values.astype(float)
PDO  = pdo.reindex(common).values.astype(float)
IOD  = iod.reindex(common).values.astype(float)
SOI  = soi.reindex(common).values.astype(float)
QBO  = qbo.reindex(common).values.astype(float)
SUN  = sun.reindex(common).values.astype(float)
DATES = common; N = len(NINO)
print(f"  N={N} months, {DATES[0].date()} to {DATES[-1].date()}")
print(f"  Candidates: AMO TNA PDO IOD SOI QBO SUN  ({len(common)} months common)")

CANDIDATES = ['AMO','TNA','PDO','IOD','SOI','QBO','SUN']
SYS_FULL = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD, SOI=SOI, QBO=QBO, SUN=SUN)

# ---------- vehicle internals ----------
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

# ---------- framework constants ----------
RUNGS = [(k, PHI**k) for k in range(3, 13)]  # phi^3..phi^12 (4.2..322 months)
N_RUNGS = len(RUNGS)
ANTI_THRESHOLD = 0.20  # |corr| above this triggers matched-rung weight
MIN_REL_POWER = 0.01   # candidate must have at least this share of variance at the rung

def gamma_phi_h(h):
    return INV_PHI3 * (INV_PHI ** ((h-1)/3.0))

GAMMA_CORR_BY_H = {1: 0.0, 3: +INV_PHI, 6: +INV_PHI2, 12: 0.0, 24: -INV_PHI2}

def assign_rung_partners(t, training_span, verbose=False):
    """For each rung, score every candidate; then enforce ONE matched-rung-boost
    per partner (their dominant rung). Other rungs where the partner happens to
    be anti-phase get standard blend weight, not matched boost.
    Returns dict: rung_idx -> (partner_name, sign, |corr|, rel_power, pinned, is_matched)
    """
    # First pass: score every (rung, partner) pair
    scores = {}  # (ri, nm) -> (sign, abs_corr, rel_pwr)
    pinned = []
    for ri, (k, p) in enumerate(RUNGS):
        if 2*p > training_span: continue
        pinned.append(ri)
        bp_nino = causal_bandpass(NINO[:t], p)
        warm = max(60, int(0.4*len(bp_nino)))
        bn = bp_nino[warm:]
        if np.std(bn) < 1e-9: continue
        for nm in CANDIDATES:
            arr = SYS_FULL[nm][:t]
            bp = causal_bandpass(arr, p)
            bs = bp[warm:]
            if np.std(bs) < 1e-9: continue
            rho = float(np.corrcoef(bs, bn)[0,1])
            if not np.isfinite(rho): continue
            rel_pwr = float(np.var(bs) / max(np.var(arr[warm:]), 1e-9))
            if rel_pwr < MIN_REL_POWER: continue
            scores[(ri, nm)] = (+1 if rho > 0 else -1, abs(rho), rel_pwr)

    # Find each partner's dominant rung (peak |corr|*sqrt(pwr) across rungs)
    partner_dominant_rung = {}
    for nm in CANDIDATES:
        best_ri, best_score = None, -1
        for ri in pinned:
            if (ri, nm) in scores:
                sg, c, p_ = scores[(ri, nm)]
                s = c * np.sqrt(p_)
                if s > best_score:
                    best_score = s; best_ri = ri
        if best_ri is not None and best_score > 0:
            partner_dominant_rung[nm] = best_ri

    # Second pass: per-rung pick best partner; mark matched only at their dominant rung
    assignments = {ri: (None, 0, 0.0, 0.0, False, False) for ri in range(N_RUNGS)}
    used_partners = set()
    # rank rungs by candidate strength (best matches assigned first)
    rung_best = []
    for ri in pinned:
        ri_best = (None, 0, 0.0, 0.0)
        for nm in CANDIDATES:
            if (ri, nm) in scores:
                sg, c, pw = scores[(ri, nm)]
                s = c * np.sqrt(pw)
                if s > ri_best[2] * np.sqrt(max(ri_best[3], 1e-9)):
                    ri_best = (nm, sg, c, pw)
        rung_best.append((ri, ri_best))
    # sort by strength so strongest pairs claim first
    rung_best.sort(key=lambda x: -(x[1][2] * np.sqrt(max(x[1][3], 1e-9))))

    for ri, (nm, sg, c, pw) in rung_best:
        # If this is the partner's dominant rung AND not yet claimed: matched
        is_matched = (nm is not None and partner_dominant_rung.get(nm) == ri and nm not in used_partners and sg == -1 and c >= ANTI_THRESHOLD)
        if is_matched:
            used_partners.add(nm)
        assignments[ri] = (nm, sg, c, pw, True, is_matched)

    if verbose:
        for ri in pinned:
            nm, sg, c, pw, pin, m = assignments[ri]
            tag = " *MATCHED*" if m else ""
            k, p = RUNGS[ri]
            print(f"    rung phi^{k:2d} (p={p:5.1f}mo): {nm} sign={sg:+d} |rho|={c:.2f} pwr={pw:.3f}{tag}")
    return assignments

# pre-cache assignments per refit (expensive otherwise)
def vehicle_dynamic(t, h, last_h1_residual, assignments, ara_cache):
    n_train = float(np.std(NINO[:t])) + 1e-9
    mean_train = float(np.mean(NINO[:t]))

    # rung weights -> use logarithmic per-rung weight (favours far rungs less, but not exponentially)
    pinned_idx = [ri for ri,(k,p) in enumerate(RUNGS) if assignments[ri][4]]
    if not pinned_idx:
        return mean_train, NINO[t+h-1] if t+h-1 < N else np.nan

    # K_REF_IDX dynamic: rung whose period closest to typical horizon
    # Use phi^8 (=46.98mo) as reference per ENSO framework
    K_REF = 8
    rung_w = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
    pin_mask = np.array([1 if assignments[ri][4] else 0 for ri in range(N_RUNGS)])
    rung_w = rung_w * pin_mask
    if rung_w.sum() < 1e-9:
        return mean_train, NINO[t+h-1] if t+h-1 < N else np.nan
    rung_w = rung_w / rung_w.sum()

    # NINO rung future
    nino_rung_future = np.zeros(N_RUNGS)
    for ri, (k, p) in enumerate(RUNGS):
        if not assignments[ri][4]: continue
        bp = causal_bandpass(NINO[:t], p)
        a, th = read_amp_theta(bp)
        ara = ara_cache.get(ri, 1.0)
        new_th = th + 2*np.pi*h/p
        kappa = 0.05
        decay = np.exp(-abs(ara - PHI) * h / p * kappa)
        nino_rung_future[ri] = a * decay * np.cos(new_th)
    own_pred = float(np.dot(rung_w, nino_rung_future))

    # Partner contributions per rung
    partner_pred = 0.0
    for ri, (k, p) in enumerate(RUNGS):
        partner_nm, sign, abs_corr, rel_pwr, pinned, is_matched = assignments[ri]
        if not pinned or partner_nm is None: continue
        arr = SYS_FULL[partner_nm][:t]
        bp = causal_bandpass(arr, p)
        a, th = read_amp_theta(bp)
        new_th = th + 2*np.pi*h/p
        f_scale = float(np.std(arr)) + 1e-9
        partner_val = a * np.cos(new_th) / f_scale * n_train
        if is_matched:
            # full matched-rung weight ONLY at this partner's dominant rung
            partner_pred += -1 * partner_val * rung_w[ri] * 5.0 * abs_corr
        else:
            # blended feeder weight at all other rungs
            partner_pred += sign * INV_PHI4 * partner_val * rung_w[ri]

    structural = mean_train + own_pred + partner_pred
    pred = structural + gamma_phi_h(h) * last_h1_residual
    truth = NINO[t+h-1] if t+h-1 < N else np.nan
    return pred, truth

# ---------- run dynamic rolling forecast ----------
HORIZONS = [1, 3, 6, 12, 24]
MIN_TRAIN = 40 * 12  # widened to 40yr so phi^11 (199mo) pins
STEP = 3

PHASE = sys.argv[1] if len(sys.argv) > 1 else 'RUN'

def run_dynamic():
    print(f"\n--- Dynamic per-rung assignment (extended ladder phi^3..phi^12) ---")
    print(f"  MIN_TRAIN={MIN_TRAIN} months ({MIN_TRAIN/12:.0f} years), STEP={STEP}")
    results = {h: [] for h in HORIZONS}
    last_h1_residual = 0.0
    t_start = time.time()
    n_origins = 0
    sample_t = MIN_TRAIN  # for verbose dump
    assignment_log = []
    for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
        # dynamic assignment per refit (training-only)
        verbose = (refit_t == sample_t) or (refit_t == MIN_TRAIN + 6*STEP) or (refit_t > N - max(HORIZONS) - STEP*2)
        if verbose:
            print(f"\n  refit t={refit_t} ({DATES[refit_t-1].date()}, train={refit_t}mo):")
        assignments = assign_rung_partners(refit_t, refit_t, verbose=verbose)
        # cache ARA for NINO rungs
        ara_cache = {}
        for ri, (k, p) in enumerate(RUNGS):
            if assignments[ri][4]:
                ara_cache[ri] = per_rung_ARA_causal(NINO[:refit_t], p)
        if verbose:
            assignment_log.append(dict(t=refit_t, date=str(DATES[refit_t-1].date()),
                                       assigns={f"phi^{RUNGS[ri][0]}": dict(partner=assignments[ri][0],
                                                                           sign=assignments[ri][1],
                                                                           abs_corr=assignments[ri][2],
                                                                           rel_pwr=assignments[ri][3])
                                                for ri in range(N_RUNGS) if assignments[ri][4]}))
        for h in HORIZONS:
            if refit_t + h - 1 >= N: continue
            pred, truth = vehicle_dynamic(refit_t, h, last_h1_residual, assignments, ara_cache)
            results[h].append((refit_t, pred, truth))
        if results[1]:
            last_h1_residual = float(results[1][-1][2] - results[1][-1][1])
        n_origins += 1
    print(f"\n  ran {n_origins} origins in {time.time()-t_start:.1f}s")
    return results, assignment_log

def report(results, label, apply_corrector=False):
    print(f"\n=== {label}{' + horizon-conditional corrector' if apply_corrector else ''} ===")
    print(f"  {'h':>3}  {'corr':>7}  {'MAE':>6}  {'R2(pers)':>9}  {'dir':>7}  n")
    metrics = {}
    for h in HORIZONS:
        if not results[h]: continue
        rec = np.array(results[h])
        origins = rec[:,0].astype(int); preds = rec[:,1].astype(float); truths = rec[:,2].astype(float)
        if apply_corrector:
            gamma = GAMMA_CORR_BY_H.get(h, 0.0)
            o2i = {ot:i for i,ot in enumerate(origins)}
            corr_p = preds.copy()
            if abs(gamma) > 1e-9:
                for i, t in enumerate(origins):
                    tb = t - h
                    if tb in o2i:
                        corr_p[i] = preds[i] + gamma * (truths[o2i[tb]] - preds[o2i[tb]])
        else:
            corr_p = preds
        pers = NINO[origins-1]
        c = float(np.corrcoef(corr_p, truths)[0,1]) if np.std(corr_p)>1e-9 else 0
        mae = float(np.mean(np.abs(corr_p - truths)))
        r2p = float(1 - np.sum((truths-corr_p)**2)/np.sum((truths-pers)**2))
        d = float(np.mean(np.sign(corr_p-pers) == np.sign(truths-pers)))
        print(f"  {h:>3}  {c:+.3f}    {mae:.3f}    {r2p:+.3f}      {d*100:5.1f}%   {len(rec)}")
        metrics[h] = dict(corr=c, mae=mae, r2p=r2p, dir=d, n=int(len(rec)))
    return metrics

if PHASE in ('RUN','ALL'):
    dyn_results, dyn_log = run_dynamic()
    np.savez(OUT.replace('.js','_intermediate.npz'),
             **{f'h{h}': np.array(dyn_results[h]) for h in HORIZONS if dyn_results[h]})
    bare = report(dyn_results, "DYNAMIC RUNG ASSIGNMENT (no corrector)")
    stacked = report(dyn_results, "DYNAMIC RUNG ASSIGNMENT", apply_corrector=True)
    out = dict(method="dynamic per-rung partner assignment",
               min_train=MIN_TRAIN, step=STEP, rungs=[k for k,_ in RUNGS],
               candidates=CANDIDATES,
               metrics_bare=bare, metrics_stacked=stacked,
               assignment_log=dyn_log[-1] if dyn_log else {})
    with open(OUT,'w',encoding='utf-8') as f:
        f.write("window.DYN_RUNG = " + json.dumps(out, default=str) + ";\n")
    print(f"\nSaved -> {OUT}")
ot:i for i,ot in enumerate(origins)}
            corr_p = preds.copy()
            if abs(gamma) > 1e-9:
                for i, t in enumerate(origins):
                    tb = t - h
                    if tb in o2i:
                        corr_p[i] = preds[i] + gamma * (truths[o2i[tb]] - preds[o2i[tb]])
        else:
            corr_p = preds
        pers = NINO[origins-1]
        c = float(np.corrcoef(corr_p, truths)[0,1]) if np.std(corr_p)>1e-9 else 0
        mae = float(np.mean(np.abs(corr_p - truths)))
        r2p = float(1 - np.sum((truths-corr_p)**2)/np.sum((truths-pers)**2))
        d = float(np.mean(np.sign(corr_p-pers) == np.sign(truths-pers)))
        print(f"  {h:>3}  {c:+.3f}    {mae:.3f}    {r2p:+.3f}      {d*100:5.1f}%   {len(rec)}")
        metrics[h] = dict(corr=c, mae=mae, r2p=r2p, dir=d, n=int(len(rec)))
    return metrics

if PHASE in ('RUN','ALL'):
    dyn_results, dyn_log = run_dynamic()
    np.savez(OUT.replace('.js','_intermediate.npz'),
             **{f'h{h}': np.array(dyn_results[h]) for h in HORIZONS if dyn_results[h]})
    bare = report(dyn_results, "DYNAMIC RUNG ASSIGNMENT (no corrector)")
    stacked = report(dyn_results, "DYNAMIC RUNG ASSIGNMENT", apply_corrector=True)
    out = dict(method="dynamic per-rung partner assignment",
               min_train=MIN_TRAIN, step=STEP, rungs=[k for k,_ in RUNGS],
               candidates=CANDIDATES,
               metrics_bare=bare, metrics_stacked=stacked,
               assignment_log=dyn_log[-1] if dyn_log else {})
    with open(OUT,'w',encoding='utf-8') as f:
        f.write("window.DYN_RUNG = " + json.dumps(out, default=str) + ";\n")
    print(f"\nSaved -> {OUT}")

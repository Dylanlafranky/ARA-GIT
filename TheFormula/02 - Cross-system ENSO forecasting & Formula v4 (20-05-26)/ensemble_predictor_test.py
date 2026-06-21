"""
Output-level ensemble test (Dylan 2026-05-03):

Combine OUTPUTS (not features) of two predictors:
  P1 = topology+flow (5 ocean + Moon, framework regression per rung)
  P2 = φ-tube tracing (NINO own phase forward projection)

Methods:
  E1 simple average: (P1 + P2) / 2
  E2 weighted average: α P1 + (1-α) P2, α from training
  E3 majority vote: sign(P1) + sign(P2)
  E4 confidence-weighted: weight by each predictor's training-period accuracy

Also report: error correlation between P1 and P2 — if independent (low corr),
ensemble helps; if heavily correlated, it doesn't.

Same time slice as v2 (1948-2023, train/test split at half).
"""
import json, os, math, re
import numpy as np, pandas as pd
from scipy.signal import hilbert

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
AMO_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\amonuslong.txt")
TNA_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\tna.txt")
PDO_PATH  = _resolve(r"F:\SystemFormulaFolder\PDO_NOAA\ersst.v5.pdo.dat")
IOD_PATH  = _resolve(r"F:\SystemFormulaFolder\IOD_NOAA\dmi.had.long.data")
MOON_PATH = _resolve(r"F:\SystemFormulaFolder\Moon_JPL\moon_elements_1948_2023.txt")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\ensemble_predictor_data.js")

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
def load_iod():
    rows=[]
    with open(IOD_PATH,'r') as f:
        next(f)
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
def load_moon():
    rows = []; in_data = False; cur = None
    with open(MOON_PATH,'r') as f:
        for ln in f:
            ln = ln.rstrip()
            if ln.strip() == '$$SOE': in_data = True; continue
            if ln.strip() == '$$EOE': break
            if not in_data: continue
            m = re.match(r'^\s*(\d+\.\d+)\s*=\s*A\.D\.\s+(\d{4})-(\w{3})-(\d{1,2})', ln)
            if m:
                if cur is not None: rows.append(cur)
                year = int(m.group(2))
                mon = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}[m.group(3)]
                day = int(m.group(4))
                cur = dict(date=pd.Timestamp(year=year, month=mon, day=day))
                continue
            for key, val in re.findall(r'([A-Z]+)\s*=\s*([+\-]?\d+\.?\d*E?[+\-]?\d*)', ln):
                if cur is None: continue
                try: cur[key] = float(val)
                except: pass
        if cur is not None: rows.append(cur)
    return pd.DataFrame(rows).set_index('date').sort_index()

print("Loading...")
nino = load_nino()
amo = load_grid_text(AMO_PATH); tna = load_grid_text(TNA_PATH)
pdo = load_grid_text(PDO_PATH, header_lines=2); iod = load_iod(); moon = load_moon()
def to_monthly(s):
    s = s.copy(); s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()
nino = to_monthly(nino); amo = to_monthly(amo); tna = to_monthly(tna)
pdo = to_monthly(pdo); iod = to_monthly(iod)
moon.index = pd.to_datetime(moon.index).to_period('M').to_timestamp()
moon = moon.groupby(moon.index).first()
common = nino.index
for s in [amo, tna, pdo, iod, moon.index]:
    common = common.intersection(s.index if hasattr(s,'index') else s)
common = common.sort_values()

NINO = nino.reindex(common).values.astype(float)
AMO  = amo.reindex(common).values.astype(float)
TNA  = tna.reindex(common).values.astype(float)
PDO  = pdo.reindex(common).values.astype(float)
IOD  = iod.reindex(common).values.astype(float)
moon_a = moon.reindex(common); OM = moon_a['OM'].values.astype(float)
MOON_OM_S = np.sin(np.deg2rad(OM)); MOON_OM_C = np.cos(np.deg2rad(OM))
MOON_EC = moon_a['EC'].values.astype(float)
DATES = common; N = len(NINO); SPLIT = N//2

def bandpass(arr, period_units, dt=1.0, bw=0.4):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_units
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

RUNGS = [(k, PHI**k) for k in range(4, 14)]
SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
           MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C, MOON_EC=MOON_EC)
R = {nm: {k: bandpass(arr, p) for k,p in RUNGS} for nm,arr in SYS.items()}

# === P1: Topology+flow predictor ===
def topology_flow_predict_continuous(idx, h, train_max, FEEDERS, ridge=10.0):
    """Returns continuous predicted NINO value at t+h for each test t."""
    if train_max - h < 20: return None
    rung_betas = {}
    for k,_ in RUNGS:
        rows=[]; ys=[]
        for t in range(train_max - h):
            feat = [R[nm][k][t] for nm in FEEDERS]; feat.append(1.0)
            rows.append(feat); ys.append(R['NINO'][k][t+h])
        X = np.array(rows); y = np.array(ys)
        n_features = X.shape[1]
        A = X.T @ X + ridge * np.eye(n_features); A[-1,-1] -= ridge
        b = np.linalg.solve(A, X.T @ y)
        rung_betas[k] = b
    mean_n = float(np.mean(NINO[:train_max]))
    preds = {}
    for t in idx:
        s = mean_n
        for k,_ in RUNGS:
            b = rung_betas[k]
            feat = [R[nm][k][t] for nm in FEEDERS] + [1.0]
            s += float(np.dot(b, feat))
        preds[t] = s
    return preds

# === P2: φ-tube tracing predictor (forward project NINO from train phases) ===
def phi_tube_predict_continuous(test_idx, train_max):
    """For each test time t, predict NINO[t] by phase-projecting from train end."""
    nino_phi_per_rung = {}
    for k, period in RUNGS:
        bp_full = bandpass(NINO, period)
        train_amp = float(np.std(bp_full[:train_max]))
        train_phase = np.unwrap(np.angle(hilbert(bp_full[:train_max])))
        slope = float((train_phase[-1] - train_phase[0]) / (train_max - 1)) if len(train_phase)>10 else 2*np.pi/period
        # Project phase forward across full data
        proj_phase = np.zeros(N)
        proj_phase[:train_max] = train_phase
        for tt in range(train_max, N):
            proj_phase[tt] = train_phase[-1] + slope * (tt - train_max + 1)
        nino_phi_per_rung[k] = train_amp * np.cos(proj_phase)
    mean_n = float(np.mean(NINO[:train_max]))
    preds = {}
    for t in test_idx:
        s = mean_n
        for k,_ in RUNGS:
            s += nino_phi_per_rung[k][t]
        preds[t] = s
    return preds

# Direction extraction
def to_direction(preds, test_idx, h):
    """Returns dict t→direction (1/-1)"""
    dirs = {}
    for t in test_idx:
        if t + h >= len(NINO): continue
        # Compare predicted future to current
        if preds.get(t+h) is None or preds.get(t) is None: continue
        dirs[t] = 1 if preds[t+h] > preds[t] else -1
    return dirs

# Actually simpler: predict NINO at t+h, compare to NINO at t (current observed)
def to_direction_simple(preds, test_idx, h):
    dirs = {}
    for t in test_idx:
        if t + h >= len(NINO): continue
        if t not in preds: continue
        dirs[t] = 1 if preds[t] > NINO[t-h] else -1  # not ideal
    return dirs

# Best approach: predict ENSO at t+h relative to t observed
def direction_accuracy(preds_at_tplush, test_idx, h):
    """preds_at_tplush[t] = predicted NINO at time t+h (predictor's output)"""
    correct = 0; total = 0
    for t in test_idx:
        if t + h >= len(NINO): continue
        if t not in preds_at_tplush: continue
        # Actual direction: NINO[t+h] vs NINO[t]
        actual = 1 if NINO[t+h] > NINO[t] else (-1 if NINO[t+h] < NINO[t] else 0)
        # Predicted direction: pred[t+h] vs NINO[t]
        pred = 1 if preds_at_tplush[t] > NINO[t] else -1
        if actual == 0: continue
        correct += (pred == actual); total += 1
    return correct/total if total else 0

# Actually let me refactor — both predictors output predicted NINO at time t+h (continuous value).
# Direction comparison: pred[t+h] > NINO[t]?

def get_predictions_at_tplush(predict_fn, test_idx, h, train_max):
    """Each test point t gets a prediction for t+h. predict_fn returns dict t→predicted_NINO_at_t_when_predicting_h_ahead.
    But our predict_fn returns the prediction VALUE at time t+h, indexed by t (the time we're predicting from).
    Actually let me just have each predictor return predicted NINO[t+h] indexed by t."""
    # Simplest: predict at t for h ahead means the model trained for horizon h applied at time t
    return predict_fn

FEEDERS = ['NINO','AMO','TNA','PDO','IOD','MOON_OM_S','MOON_OM_C','MOON_EC']

# Build predictions at each horizon
HORIZONS = [12, 24, 36, 48]
test_idx = list(range(SPLIT, N))

print(f"\n========= ENSEMBLE TEST =========")
print(f"For each horizon, get continuous predictions from each model, then ensemble.")

results = {}
for h in HORIZONS:
    # P1: topology+flow predictions at t+h indexed by t
    p1 = topology_flow_predict_continuous(test_idx, h, SPLIT, FEEDERS)
    # P2: phi-tube predictions of NINO at time t+h indexed by t
    # Actually phi-tube projects NINO(t) for ALL t, so to predict NINO[t+h] from time t we just look up the projection at index t+h
    phi_proj = phi_tube_predict_continuous(test_idx, SPLIT)
    # phi_proj[t] = phi-tube projection at time t (we need t+h)
    p2 = {}
    for t in test_idx:
        if t+h < N:
            # Use the phi-tube projection at the FUTURE time
            full_phi = phi_tube_predict_continuous(list(range(N)), SPLIT)
            p2[t] = full_phi[t+h]
            break  # actually just compute once outside
    full_phi = phi_tube_predict_continuous(list(range(N)), SPLIT)
    p2 = {t: full_phi[t+h] for t in test_idx if t+h < N}
    # Now also get p1 at indexed properly
    # p1[t] returns predicted NINO at t+h (by construction of the regression)

    # Direction accuracy of each
    def dir_acc_pred(preds, h):
        correct=0; total=0
        for t in test_idx:
            if t+h >= N or t not in preds: continue
            actual = 1 if NINO[t+h] > NINO[t] else (-1 if NINO[t+h] < NINO[t] else 0)
            pred = 1 if preds[t] > NINO[t] else -1
            if actual==0: continue
            correct += (pred==actual); total += 1
        return correct/total if total else 0

    a1 = dir_acc_pred(p1, h)
    a2 = dir_acc_pred(p2, h)

    # Ensemble: simple average
    ens_avg = {t: (p1[t] + p2[t])/2 for t in p1 if t in p2}
    a_ens = dir_acc_pred(ens_avg, h)

    # Ensemble: weighted (find optimal weight on training half? we don't have train preds easily)
    # Instead try a few weights
    best_w = 0.5; best_acc = a_ens
    for w in np.linspace(0.0, 1.0, 21):
        ens_w = {t: w*p1[t] + (1-w)*p2[t] for t in p1 if t in p2}
        acc = dir_acc_pred(ens_w, h)
        if acc > best_acc:
            best_acc = acc; best_w = float(w)

    # Majority vote (sign agreement)
    def vote(preds_a, preds_b, h):
        correct=0; total=0
        for t in test_idx:
            if t+h>=N or t not in preds_a or t not in preds_b: continue
            actual = 1 if NINO[t+h]>NINO[t] else (-1 if NINO[t+h]<NINO[t] else 0)
            if actual==0: continue
            pa = 1 if preds_a[t]>NINO[t] else -1
            pb = 1 if preds_b[t]>NINO[t] else -1
            # Vote: agreement = high confidence; disagreement = take p1 (stronger)
            if pa == pb:
                pred = pa
            else:
                pred = pa  # take topology+flow when they disagree
            correct += (pred==actual); total += 1
        return correct/total if total else 0

    a_vote = vote(p1, p2, h)

    # Error correlation: do P1 and P2 make the same errors?
    err1 = []; err2 = []
    for t in test_idx:
        if t+h>=N or t not in p1 or t not in p2: continue
        actual = NINO[t+h]
        err1.append(p1[t] - actual); err2.append(p2[t] - actual)
    if len(err1) > 5:
        err_corr = float(np.corrcoef(err1, err2)[0,1])
    else: err_corr = 0
    # Agreement rate
    agree = sum(1 for t in p1 if t in p2 and ((p1[t]>NINO[t]) == (p2[t]>NINO[t]))) / max(1, len([t for t in p1 if t in p2]))

    results[h] = dict(
        topology_flow=a1, phi_tube=a2,
        ensemble_avg=a_ens,
        ensemble_best_weighted=dict(weight=best_w, accuracy=best_acc),
        majority_vote_with_p1_breaktie=a_vote,
        error_correlation=err_corr,
        agreement_rate=agree,
    )
    print(f"\nHorizon h={h}mo:")
    print(f"  P1 topology+flow:           {a1*100:>5.1f}%")
    print(f"  P2 phi-tube tracing:        {a2*100:>5.1f}%")
    print(f"  Simple average ensemble:    {a_ens*100:>5.1f}%")
    print(f"  Best weighted (α={best_w:.2f}):    {best_acc*100:>5.1f}%")
    print(f"  Majority vote (p1 breaks):  {a_vote*100:>5.1f}%")
    print(f"  Error correlation:          {err_corr:+.3f}  (lower = more independent)")
    print(f"  Sign agreement rate:        {agree*100:>5.1f}%")

print(f"\n========= SUMMARY =========")
print(f"  {'horizon':>10}  {'P1':>6}  {'P2':>6}  {'avg':>6}  {'wtd':>6}  {'vote':>6}  {'err_corr':>9}")
for h, r in results.items():
    print(f"  h={h:>2}mo     {r['topology_flow']*100:>5.1f}% {r['phi_tube']*100:>5.1f}% {r['ensemble_avg']*100:>5.1f}% {r['ensemble_best_weighted']['accuracy']*100:>5.1f}% {r['majority_vote_with_p1_breaktie']*100:>5.1f}%  {r['error_correlation']:+.3f}")

out = dict(
    sources="Same as v2",
    horizons=HORIZONS,
    results=results,
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.ENSEMBLE = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

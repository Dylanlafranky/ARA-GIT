"""
High-resolution ARA test (Dylan 2026-05-02):

Currently each rung is summarized as ONE bandpassed amplitude per timestep.
Dylan: "We're treating it as 1 number. What if we LOG increase it? It's just a
compression method for relation."

Test: replace single bandpass per rung with FOUR descriptors per rung:
  1. Bandpass amplitude (current)
  2. Hilbert envelope (instantaneous amplitude)
  3. log(envelope) — log-scale amplitude
  4. sin(instantaneous phase)
  5. cos(instantaneous phase)

5x more information per rung. Apply to best config (5 ocean + Moon).
Compare to v2 baseline (single descriptor) and see if direction accuracy passes 81.7%.

DATA: same as v2 (NOAA + JPL Horizons, all real, verifiable).
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\high_res_ara_data.js")

# Loaders (same as v2)
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
                mon  = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}[m.group(3)]
                day  = int(m.group(4))
                cur = dict(date=pd.Timestamp(year=year, month=mon, day=day))
                continue
            for key, val in re.findall(r'([A-Z]+)\s*=\s*([+\-]?\d+\.?\d*E?[+\-]?\d*)', ln):
                if cur is None: continue
                try: cur[key] = float(val)
                except: pass
        if cur is not None: rows.append(cur)
    df = pd.DataFrame(rows).set_index('date').sort_index()
    return df

print("Loading datasets...")
nino = load_nino(); amo = load_grid_text(AMO_PATH); tna = load_grid_text(TNA_PATH)
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
moon_a = moon.reindex(common)
OM = moon_a['OM'].values.astype(float)
MOON_OM_S = np.sin(np.deg2rad(OM)); MOON_OM_C = np.cos(np.deg2rad(OM))
MOON_EC = moon_a['EC'].values.astype(float)
DATES = common; N = len(NINO); SPLIT = N//2
print(f"Common overlap: {DATES[0].date()} → {DATES[-1].date()}, n={N}")

# φ-rung descriptors
def rung_band(arr, period_months, bw=0.2):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=1.0)
    f_c = 1.0/period_months
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

def rung_descriptors(arr, period_months, bw=0.2):
    """5 descriptors per rung per timestep:
       0: bandpass signal (real part)
       1: Hilbert envelope (instantaneous amplitude)
       2: log(envelope + eps)
       3: sin(instantaneous phase)
       4: cos(instantaneous phase)
    """
    bp = rung_band(arr, period_months, bw)
    analytic = hilbert(bp)
    env = np.abs(analytic)
    phase = np.angle(analytic)
    log_env = np.log(env + 1e-9)
    return dict(
        bp=bp,
        env=env,
        log_env=log_env,
        sin_phase=np.sin(phase),
        cos_phase=np.cos(phase),
    )

RUNGS = [(k, PHI**k) for k in range(4, 12)]
SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
           MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C, MOON_EC=MOON_EC)

# Compute high-res descriptors for each (system, rung)
print("Computing high-resolution per-rung descriptors...")
HR = {name: {k: rung_descriptors(arr, p) for k,p in RUNGS} for name,arr in SYS.items()}
# Also compute single-descriptor (just bandpass) for baseline
LR_DESC = {name: {k: rung_band(arr, p) for k,p in RUNGS} for name,arr in SYS.items()}

# === Direction prediction ===
HORIZONS = [1, 3, 6, 12]
def dir_truth(arr, t, h):
    if t + h >= len(arr): return None
    diff = arr[t + h] - arr[t]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

def acc_FW_high_res(idx, h, train_max, feeder_names, descriptors, ridge=0.0):
    """For each rung k, learn NINO_k_bandpass[t+h] ~ Σ feeder descriptors[t].
       Ridge regularization optional (alpha=ridge)."""
    rung_betas = {}
    for k,_ in RUNGS:
        rows=[]; ys=[]
        for t in range(train_max - h):
            feat = []
            for nm in feeder_names:
                d = HR[nm][k]
                for desc in descriptors:
                    feat.append(d[desc][t])
            feat.append(1.0)
            rows.append(feat); ys.append(HR['NINO'][k]['bp'][t+h])
        X = np.array(rows); y = np.array(ys)
        if ridge > 0:
            # Ridge: (X^T X + alpha I)^-1 X^T y
            n_features = X.shape[1]
            A = X.T @ X + ridge * np.eye(n_features)
            A[-1,-1] -= ridge  # don't penalize the constant
            b = np.linalg.solve(A, X.T @ y)
        else:
            b, *_ = np.linalg.lstsq(X, y, rcond=None)
        rung_betas[k] = b
    correct = 0; total = 0
    mean_n = float(np.mean(NINO[:train_max]))
    for t in idx:
        true = dir_truth(NINO, t, h)
        if true is None or true == 0: continue
        s = mean_n
        for k,_ in RUNGS:
            b = rung_betas[k]
            feat = []
            for nm in feeder_names:
                d = HR[nm][k]
                for desc in descriptors:
                    feat.append(d[desc][t])
            feat.append(1.0)
            s += float(np.dot(b, feat))
        pred = 1 if s > NINO[t] else -1
        correct += (pred == true); total += 1
    return correct / total if total else 0

FEEDERS = ['NINO','AMO','TNA','PDO','IOD','MOON_OM_S','MOON_OM_C','MOON_EC']
test_idx = list(range(SPLIT, N))

# Three descriptor configs
DESC_CONFIGS = {
    'baseline_bp_only':    ['bp'],
    'amp_phase':           ['bp','env','sin_phase','cos_phase'],
    'amp_phase_log':       ['bp','env','log_env','sin_phase','cos_phase'],
    'log_only':            ['log_env'],
    'phase_only':          ['sin_phase','cos_phase'],
}

print(f"\n========= HIGH-RES ARA — DIRECTION ACCURACY (test n={len(test_idx)}) =========\n")
results = {}
for cfg_name, descs in DESC_CONFIGS.items():
    print(f"---- Descriptor config: {cfg_name}  ({len(descs)} descriptors per rung: {descs}) ----")
    print(f"  {'horizon':>10}  {'FW':>7}  {'FW_ridge':>9}")
    cfg_results = {}
    for h in HORIZONS:
        a_fw = acc_FW_high_res(test_idx, h, SPLIT, FEEDERS, descs)
        a_fw_r = acc_FW_high_res(test_idx, h, SPLIT, FEEDERS, descs, ridge=10.0)
        flag = ' ★' if max(a_fw, a_fw_r) >= 0.82 else '  '
        print(f"  h={h:>2} months  {a_fw:>7.1%}  {a_fw_r:>9.1%}{flag}")
        cfg_results[h] = dict(plain=a_fw, ridge=a_fw_r)
    results[cfg_name] = cfg_results
    print()

# Summary
print("Summary — best (config, ridge?) at each horizon:")
for h in HORIZONS:
    best = None; best_val = 0; best_label = ''
    for cfg, r in results.items():
        for kind in ['plain','ridge']:
            v = r[h][kind]
            if v > best_val:
                best_val = v; best_label = f"{cfg}/{kind}"
    print(f"  h={h:>2}m: {best_label} -> {best_val:.1%}")

# Save
out = dict(
    sources="Same as v2 (NOAA + JPL Horizons, all verifiable)",
    common_range=[DATES[0].strftime('%Y-%m'), DATES[-1].strftime('%Y-%m')],
    train_n=int(SPLIT), test_n=int(N-SPLIT),
    horizons=HORIZONS,
    feeders=FEEDERS,
    rungs=[[k,p] for k,p in RUNGS],
    descriptor_configs={c:list(d) for c,d in DESC_CONFIGS.items()},
    results={c:{str(h):v for h,v in r.items()} for c,r in results.items()},
    prior_v2_best=dict(h6=0.795, h12=0.817),
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.HIGH_RES_ARA = " + json.dumps(out) + ";\n")
print("Saved -> " + OUT)

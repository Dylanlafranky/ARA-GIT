"""
Two tests in one (Dylan 2026-05-02):

Part A — QBO as horizontal feeder for ENSO direction prediction
  QBO is at φ⁷ (~28 months) — same rung as ENSO. Known stratospheric
  influencer of ENSO via the Holton-Tan effect. Should add lift via
  matched-rung horizontal coupling.

Part B — Annual cycle as ENSO vertical-column relative test
  Extract the dominant annual cycle (~11 months, φ⁵) from the data.
  Compute its ARA fingerprint. Compare to ENSO's ARA fingerprint.
  If similar shape → annual cycle is a vertical-column relative.

DATA SOURCES (all real):
  ENSO Niño 3.4: NOAA PSL
  AMO, TNA, IOD: NOAA PSL
  PDO: NOAA NCEI ERSST V5
  QBO: NOAA PSL https://psl.noaa.gov/data/correlation/qbo.data
  Moon: NASA JPL Horizons
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
QBO_PATH  = _resolve(r"F:\SystemFormulaFolder\QBO_NOAA\qbo.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\qbo_annual_data.js")

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
def load_qbo():
    """NOAA QBO: header line then year + 12 monthly values; missing=-999"""
    rows=[]
    with open(QBO_PATH,'r') as f:
        next(f)  # header
        for ln in f:
            parts = ln.split()
            if len(parts) < 13: continue
            try: year = int(parts[0])
            except: continue
            for m in range(12):
                try: v = float(parts[1+m])
                except: continue
                if v < -900 or v > 900: continue
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
nino = load_nino(); amo = load_grid_text(AMO_PATH); tna = load_grid_text(TNA_PATH)
pdo = load_grid_text(PDO_PATH, header_lines=2); iod = load_iod()
moon = load_moon(); qbo = load_qbo()
def to_monthly(s):
    s = s.copy(); s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()
nino = to_monthly(nino); amo = to_monthly(amo); tna = to_monthly(tna)
pdo = to_monthly(pdo); iod = to_monthly(iod); qbo = to_monthly(qbo)
moon.index = pd.to_datetime(moon.index).to_period('M').to_timestamp()
moon = moon.groupby(moon.index).first()

print(f"QBO: {qbo.index.min().date()} → {qbo.index.max().date()}, n={len(qbo)}")

common = nino.index
for s in [amo, tna, pdo, iod, moon.index, qbo]:
    common = common.intersection(s.index if hasattr(s,'index') else s)
common = common.sort_values()
print(f"Common overlap: {common.min().date()} → {common.max().date()}, n={len(common)}")

NINO = nino.reindex(common).values.astype(float)
AMO  = amo.reindex(common).values.astype(float)
TNA  = tna.reindex(common).values.astype(float)
PDO  = pdo.reindex(common).values.astype(float)
IOD  = iod.reindex(common).values.astype(float)
QBO  = qbo.reindex(common).values.astype(float)
moon_a = moon.reindex(common); OM = moon_a['OM'].values.astype(float)
MOON_OM_S = np.sin(np.deg2rad(OM)); MOON_OM_C = np.cos(np.deg2rad(OM))
DATES = common; N = len(NINO); SPLIT = N//2

# Bandpass
def rung_band(arr, period_months, bw=0.2):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=1.0)
    f_c = 1.0/period_months
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

RUNGS = [(k, PHI**k) for k in range(4, 12)]

# QBO power per rung — confirms it sits at φ⁷ as expected
print("\nQBO power by rung (training, frac of total):")
QBO_BAND = {k: rung_band(QBO, p) for k,p in RUNGS}
for k,p in RUNGS:
    bv = float(np.var(QBO_BAND[k][:SPLIT]))
    tv = float(np.var(QBO[:SPLIT]))
    print(f"  k={k:>2} (T={p:>5.0f}mo): {bv/tv*100:>5.1f}%")

# === PART A: Direction prediction with QBO added ===
SYS_BASE = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
                MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C)
SYS_QBO  = dict(SYS_BASE); SYS_QBO['QBO'] = QBO
R_BASE = {nm: {k: rung_band(arr, p) for k,p in RUNGS} for nm,arr in SYS_BASE.items()}
R_QBO  = {nm: {k: rung_band(arr, p) for k,p in RUNGS} for nm,arr in SYS_QBO.items()}

def dir_truth(arr, t, h):
    if t + h >= len(arr): return None
    diff = arr[t + h] - arr[t]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

def acc_FW(idx, h, train_max, FEEDERS, R, ridge=10.0):
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
    correct=0; total=0
    mean_n = float(np.mean(NINO[:train_max]))
    for t in idx:
        true = dir_truth(NINO, t, h)
        if true is None or true==0: continue
        s = mean_n
        for k,_ in RUNGS:
            b = rung_betas[k]
            feat = [R[nm][k][t] for nm in FEEDERS] + [1.0]
            s += float(np.dot(b, feat))
        pred = 1 if s>NINO[t] else -1
        correct += (pred==true); total += 1
    return correct/total if total else 0

HORIZONS = [6, 12, 18, 24, 36, 48]
test_idx = list(range(SPLIT, N))
print(f"\n========= PART A: Direction prediction with QBO added =========")
print(f"{'horizon':>10}  {'no_QBO':>7}  {'+QBO':>7}  {'delta':>7}")
results_A = {}
for h in HORIZONS:
    a_b = acc_FW(test_idx, h, SPLIT, list(SYS_BASE.keys()), R_BASE)
    a_q = acc_FW(test_idx, h, SPLIT, list(SYS_QBO.keys()),  R_QBO)
    delta = a_q - a_b
    flag = ' ★' if delta > 0.02 else ('  ' if abs(delta) <= 0.02 else ' ↓')
    print(f"  h={h:>2} mo  {a_b:>7.1%}  {a_q:>7.1%}  {delta:+.3f}{flag}")
    results_A[h] = dict(no_qbo=a_b, with_qbo=a_q, delta=delta)

# === PART B: Annual cycle as vertical-column relative test ===
# Extract annual cycle component per system
ANNUAL_PERIOD = 12  # months
print("\n========= PART B: ARA fingerprint comparison =========")
print("Compute ARA per rung for each system. Compare fingerprints.\n")

def ara_value(arr):
    """T_acc / T_rel approximation: ratio of time spent above mean to time below."""
    m = np.mean(arr)
    above = (arr > m).sum()
    below = (arr < m).sum()
    return above/below if below > 0 else np.nan

def hilbert_amp(arr):
    return float(np.mean(np.abs(hilbert(arr - np.mean(arr)))))

# For each (system, rung) compute mean ARA-like metric
SYS_ALL = dict(SYS_QBO); SYS_ALL['ANNUAL'] = rung_band(NINO, 12)  # the annual cycle of NINO itself
# Actually let's also compute the annual cycle from each system's bandpass at φ⁵
# but the cleanest "annual cycle" is the 12-month bandpass component

print(f"{'system':>10}  " + "  ".join([f"k={k:>2}" for k,_ in RUNGS]))
fingerprints = {}
for nm, arr in SYS_QBO.items():
    bands = [rung_band(arr, p) for k,p in RUNGS]
    aras = [ara_value(b) for b in bands]
    fingerprints[nm] = aras
    print(f"  {nm:>8}  " + "  ".join([f"{a:>4.2f}" if np.isfinite(a) else "  - " for a in aras]))

# Annual cycle of ENSO (NINO itself bandpassed at 12mo)
annual_cycle = rung_band(NINO, 12)
ann_bands = [rung_band(annual_cycle, p) for k,p in RUNGS]
ann_aras = [ara_value(b) for b in ann_bands]
fingerprints['ANNUAL_NINO'] = ann_aras
print(f"  {'ANNUAL':>8}  " + "  ".join([f"{a:>4.2f}" if np.isfinite(a) else "  - " for a in ann_aras]))

# Compute fingerprint similarity to NINO across all systems
print("\nFingerprint similarity (correlation across rungs) to NINO:")
nino_fp = np.array(fingerprints['NINO'])
similarities = {}
for nm, fp in fingerprints.items():
    if nm == 'NINO': continue
    fp_arr = np.array(fp)
    mask = np.isfinite(nino_fp) & np.isfinite(fp_arr)
    if mask.sum() < 3:
        sim = np.nan
    else:
        sim = float(np.corrcoef(nino_fp[mask], fp_arr[mask])[0,1])
    similarities[nm] = sim
    print(f"  {nm:>12}: {sim:+.3f}")

# Save
out = dict(
    sources=dict(qbo="https://psl.noaa.gov/data/correlation/qbo.data"),
    common_range=[DATES[0].strftime('%Y-%m'), DATES[-1].strftime('%Y-%m')],
    train_n=int(SPLIT), test_n=int(N-SPLIT),
    horizons=HORIZONS,
    results_A_qbo=results_A,
    rungs=[[k,p] for k,p in RUNGS],
    qbo_band_distribution={str(k): float(np.var(QBO_BAND[k][:SPLIT])/np.var(QBO[:SPLIT])) for k,_ in RUNGS},
    fingerprints={nm: list(fp) for nm,fp in fingerprints.items()},
    fingerprint_similarities_to_nino=similarities,
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.QBO_ANNUAL = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

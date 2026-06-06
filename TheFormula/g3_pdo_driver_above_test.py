"""G3-A + PDO driver-above (5:1 snap regime-bias) — does it recover ENSO h=18-24?
Strictly causal. Real data: NINO3.4 (1870+), ERSST PDO (1854+).
PDO relation classified from data: P_PDO~346mo / P_ENSO~67mo = 5.17 ~ 5:1 integer
resonance (snap class), NOT phi-engine. So coupling = quasi-static additive REGIME bias
keyed to PDO's DECADAL (>120mo) slow phase. The 67mo shared band (1:1 face-lock = no
independent info) is stripped by a causal low-pass.
"""
import os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import ara_framework as F
PHI = F.PHI

# ---------- load + align ----------
def load_nino(p, miss=-99.99):
    d = {}
    for ln in open(p):
        s = [x.strip() for x in ln.split(",")]
        if len(s) == 2 and s[0][:4].isdigit():
            v = float(s[1])
            if v > miss + 1e-3: d[s[0][:7].replace("-", "")] = v
    return d
def load_pdo(p, miss=99.0):
    d = {}
    for ln in open(p):
        s = ln.split()
        if len(s) == 13 and s[0].isdigit() and len(s[0]) == 4:
            yr = int(s[0])
            for mo in range(1, 13):
                try: v = float(s[mo])
                except: continue
                if v < miss - 1e-3: d[f"{yr}{mo:02d}"] = v
    return d

NINO = load_nino("Claude4.8/nino34_long_anom.csv")
PDO  = load_pdo("../../../PDO_NOAA/ersst.v5.pdo.dat")
keys = sorted(set(NINO) & set(PDO))
home = np.array([NINO[k] for k in keys])
pdo  = np.array([PDO[k]  for k in keys])
mon  = np.array([int(k[4:6]) for k in keys])
n = len(home)
print(f"aligned {n} months  {keys[0]}..{keys[-1]}")

# PDO decadal slow phase: causal low-pass (trailing mean window 60mo kills the 67mo
# shared ENSO band, preserves the 346mo decadal regime). Strictly trailing => causal.
pdo_dec = F._trailing_mean(pdo, 60)   # quasi-static regime indicator

P = 48.0
HZ = (3, 6, 9, 12, 15, 18, 24)
sys_enso = F.build_self_system(home, P, horizons=HZ, name="ENSO")

# ---------- shared ----------
def ridge(Xtr, ytr, Xte, pen=0.1):
    mu = np.nanmean(Xtr, 0); sd = np.nanstd(Xtr, 0); sd[~np.isfinite(sd) | (sd < 1e-9)] = 1.0
    A = np.nan_to_num((Xtr - mu) / sd); B = np.nan_to_num((Xte - mu) / sd)
    A = np.column_stack([np.ones(len(A)), A]); B = np.column_stack([np.ones(len(B)), B])
    R = np.eye(A.shape[1]) * pen; R[0, 0] = 0.0
    return B @ np.linalg.solve(A.T @ A + R, A.T @ ytr)
def cc(p, t):
    p = np.asarray(p); t = np.asarray(t); m = np.isfinite(p) & np.isfinite(t)
    if m.sum() < 3: return float("nan")
    return float(np.corrcoef(p[m], t[m])[0, 1])

def sphere_coords(state, origins):
    X = state['ara'][origins]
    osp = np.nan_to_num(state['own_spin'][origins]); tq = np.nan_to_num(state['lower_torque'][origins])
    Zraw = np.abs(osp) + np.abs(tq); Z = (Zraw - np.nanmean(Zraw)) / (np.nanstd(Zraw) + 1e-9)
    phi_d = np.abs(X - PHI); anti = np.abs(X - (2 - PHI))
    gate = 1.0 / (1.0 + np.exp(-Z)); roll = np.nan_to_num(state['roll'][origins])
    return np.column_stack([X, Z, phi_d, anti, gate, gate * roll])

cut = int(n / PHI)
st = F._layer_state(sys_enso, cut)
start = max(max(sys_enso.home_lags), *(c.window + 2 for c in sys_enso.lower + sys_enso.upper))

# ---------- run all models per horizon ----------
rows = {}
for h in HZ:
    tr = np.arange(start, cut - h); te = np.arange(cut, n - h)
    ytr = home[tr + h]; yte = home[te + h]; dtr = home[tr + h] - home[tr]
    cte = home[te]
    # baselines
    pers = cte.copy()
    snv  = np.array([home[t + h - int(P)] if t + h - int(P) >= 0 else np.nan for t in te])
    # home_ar (causal lags only)
    lags = [1, 2, 3, 6, 12, 24, int(P)]
    hxtr = np.array([[home[t - l] for l in lags] for t in tr]); hxte = np.array([[home[t - l] for l in lags] for t in te])
    har  = cte + ridge(hxtr, dtr, hxte)
    # strongest baseline: lag-harmonic-ridge
    def lh(origins):
        th = 2 * np.pi * (mon[origins] - 1) / 12
        lagmat = np.array([[home[t - l] for l in lags] for t in origins])
        return np.column_stack([lagmat, np.cos(th), np.sin(th)])
    lhr = cte + ridge(lh(tr), dtr, lh(te))
    # stable ARA (home_plus_ara headline)
    cxtr = F._feature_matrix(sys_enso, st, tr, True); cxte = F._feature_matrix(sys_enso, st, te, True)
    ara = cte + F._ridge_readout(cxtr, dtr, cxte)
    # G3-A geometry-native
    base_tr = F._feature_matrix(sys_enso, st, tr, True); base_te = F._feature_matrix(sys_enso, st, te, True)
    g3_tr = np.column_stack([base_tr, sphere_coords(st, tr)]); g3_te = np.column_stack([base_te, sphere_coords(st, te)])
    g3 = cte + ridge(g3_tr, dtr, g3_te)
    # G3-A + PDO decadal regime bias (quasi-static additive, snap class)
    pdo_tr = pdo_dec[tr][:, None]; pdo_te = pdo_dec[te][:, None]
    gp = cte + ridge(np.column_stack([g3_tr, pdo_tr]), dtr, np.column_stack([g3_te, pdo_te]))
    # variant: raw contemporaneous PDO + decadal + interaction with ARA
    araX_tr = st['ara'][tr]; araX_te = st['ara'][te]
    rawtr = np.column_stack([pdo[tr], pdo_dec[tr], pdo_dec[tr]*araX_tr])
    rawte = np.column_stack([pdo[te], pdo_dec[te], pdo_dec[te]*araX_te])
    gp2 = cte + ridge(np.column_stack([g3_tr, rawtr]), dtr, np.column_stack([g3_te, rawte]))
    # variant: 5:1 resonance phasor (PDO slow phase, ENSO rides 5 slots)
    ph = 2*np.pi*np.arange(n)/346.0
    phas_tr = np.column_stack([np.cos(ph[tr]), np.sin(ph[tr]), np.cos(5*ph[tr]), np.sin(5*ph[tr])])
    phas_te = np.column_stack([np.cos(ph[te]), np.sin(ph[te]), np.cos(5*ph[te]), np.sin(5*ph[te])])
    gp3 = cte + ridge(np.column_stack([g3_tr, phas_tr]), dtr, np.column_stack([g3_te, phas_te]))
    rows[h] = dict(pers=cc(pers, yte), home_ar=cc(har, yte),
                   lagharm=cc(lhr, yte), stableARA=cc(ara, yte), G3A=cc(g3, yte),
                   G3A_PDO=cc(gp, yte), G3A_PDOraw=cc(gp2, yte), G3A_5to1=cc(gp3, yte), n=len(te))

cols = ["home_ar", "lagharm", "stableARA", "G3A", "G3A_PDO", "G3A_PDOraw", "G3A_5to1"]
print("\nHELD-OUT CORRELATION (ENSO, golden split, test segment)\n")
print(f"{'h':>3} " + "".join(f"{c:>10}" for c in cols) + f"{'n':>6}")
for h in HZ:
    r = rows[h]
    print(f"{h:>3} " + "".join(f"{r[c]:>+10.3f}" for c in cols) + f"{r['n']:>6}")
print("\nrelation: PDO/ENSO = 5.17 ~ 5:1 snap; PDO fed as causal decadal (>120mo) regime bias")

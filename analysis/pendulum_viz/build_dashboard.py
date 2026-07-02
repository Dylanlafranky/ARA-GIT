"""
Build a self-contained interactive HTML dashboard for the triple-pendulum ARA
deconstruction, computed from the real dynamicslab MultiArm-Pendulum data.
All panels regenerate the matplotlib figures as interactive Plotly charts, plus:
  - ARA folded 0-2 axis occupancy strip
  - re-run "what held / what moved" panel
  - animated triple pendulum reconstructed from the real angles (equal-length schematic)
Writes pendulum_dashboard.html (data embedded; Plotly from cdnjs).
"""
import os, sys, json
import numpy as np
from scipy.signal import find_peaks, hilbert, butter, filtfilt

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "pendulum_scripts")
sys.path.insert(0, SCRIPTS)
os.environ.setdefault("PENDULUM_DATA", os.path.join(SCRIPTS, "data"))
from pendulum_common import load_triple, rest_centered, rest_of, wrap, ara_position, RUNS

def r(a, p=4):
    a = np.asarray(a, float)
    return [round(float(x), p) for x in a]

D = {"runs": list(RUNS)}

# ---------- Element 1: per-arm geometry (run1) ----------
t, th_raw, vel, fs = load_triple("run1", decimate=10)  # 1000 Hz
th = rest_centered(th_raw)
N = len(th[1])
geom = {"arms": {}, "spectrum": {}, "portrait": {}}
sub = max(1, N // 3500)
for i in (1, 2, 3):
    x = th[i] - th[i].mean()
    amp = float(x.std() * np.sqrt(2))
    f = np.fft.rfftfreq(N, 1 / fs); P = np.abs(np.fft.rfft(x * np.hanning(N))) ** 2
    f, P = f[1:], P[1:]
    fp = f[np.argmax(P)]
    band = (f > 0.8 * fp) & (f < 1.2 * fp)
    clk = float(P[band].sum() / P.sum())
    geom["arms"][i] = {"amp": round(amp, 3), "domP": round(1 / fp, 3),
                       "velamp": round(float(vel[i].std() * np.sqrt(2)), 2), "clk": round(clk, 2)}
    msk = f < 4.0
    fsel = f[msk]; Psel = P[msk]
    s2 = max(1, len(fsel) // 800)
    geom["spectrum"][i] = {"f": r(fsel[::s2], 3), "P": r(np.log10(Psel[::s2] + 1e-12), 3)}
    geom["portrait"][i] = {"x": r(th[i][::sub], 4), "v": r(vel[i][::sub], 3),
                           "t": r(t[::sub], 2)}
geom["ampratios"] = {"A2A1": round(geom["arms"][2]["amp"]/geom["arms"][1]["amp"], 3),
                     "A3A2": round(geom["arms"][3]["amp"]/geom["arms"][2]["amp"], 3),
                     "A3A1": round(geom["arms"][3]["amp"]/geom["arms"][1]["amp"], 3)}
D["geom"] = geom

# ---------- 50 Hz working set for time series (run1) ----------
t5, th5_raw, vel5, fs5 = load_triple("run1", decimate=200)  # 50 Hz
th5 = rest_centered(th5_raw)
ara5 = ara_position(th5_raw)
D["t5"] = r(t5, 3)
D["ara_pos"] = {i: r(ara5[i], 4) for i in (1, 2, 3)}

# ARA occupancy density per arm on 0-2 axis
occ = {}
edges = np.linspace(0, 2, 81)
ctr = 0.5 * (edges[:-1] + edges[1:])
for i in (1, 2, 3):
    h, _ = np.histogram(ara5[i], bins=edges, density=True)
    occ[i] = r(h, 4)
D["occ"] = {"centers": r(ctr, 3), "dens": occ}

# ---------- Element 3 doc-style: relational bends (run1, rest-relative) ----------
bend = {"12": 1 + wrap(th5[2] - th5[1]) / np.pi,
        "23": 1 + wrap(th5[3] - th5[2]) / np.pi,
        "13": 1 + wrap(th5[3] - th5[1]) / np.pi}
bends = {"series": {}, "stats": {}, "hist": {}}
be = np.linspace(0.4, 1.6, 81); bc = 0.5 * (be[:-1] + be[1:])
for k, b in bend.items():
    bends["series"][k] = r(b, 4)
    bends["stats"][k] = {"std": round(float(b.std()), 3),
                         "ridge": round(float(np.mean(np.abs(b - 1) < 0.1) * 100)),
                         "rng": [round(float(b.min()), 3), round(float(b.max()), 3)]}
    hh, _ = np.histogram(b, bins=be, density=True)
    bends["hist"][k] = r(hh, 4)
bends["histx"] = r(bc, 3)
D["bends"] = bends

# ---------- Leadership / dominance (all runs, prominence-filtered) ----------
PDOM_S, PROM = 1.333, 0.02
def leaders_of(run):
    t, th_raw, vel, fs = load_triple(run, decimate=20)  # 500 Hz
    ara = ara_position(th_raw)
    dist = max(1, int(0.4 * PDOM_S * fs))
    def ext(x):
        hi, _ = find_peaks(x, prominence=PROM, distance=dist)
        lo, _ = find_peaks(-x, prominence=PROM, distance=dist)
        return np.sort(np.concatenate([hi, lo]))
    E = {i: ext(ara[i]) for i in (1, 2, 3)}
    leaders, times = [], []
    for i1 in E[1]:
        cand = {1: i1}; ok = True
        for a in (2, 3):
            j = E[a][np.argmin(np.abs(E[a] - i1))]
            if abs(j - i1) / fs < 0.5: cand[a] = j
            else: ok = False
        if not ok: continue
        leaders.append(int(min(cand, key=lambda a: cand[a]))); times.append(float(t[i1]))
    return np.array(leaders), np.array(times)

from itertools import groupby
lead = {"share": {}, "maxblk": {}, "meanblk": {}, "swings": {}, "switches": {}}
for run in RUNS:
    L, T = leaders_of(run)
    blocks = {1: [], 2: [], 3: []}
    for k, g in groupby([int(x) for x in L]):
        blocks[k].append(len(list(g)))
    lead["share"][run] = {a: round(100 * float(np.mean(L == a)), 1) for a in (1, 2, 3)}
    lead["maxblk"][run] = {a: (max(blocks[a]) if blocks[a] else 0) for a in (1, 2, 3)}
    lead["meanblk"][run] = {a: round(float(np.mean(blocks[a])), 2) if blocks[a] else 0 for a in (1, 2, 3)}
    lead["swings"][run] = int(len(L))
    lead["switches"][run] = int(np.sum(np.diff(L) != 0))
    if run == "run1":
        lead["scatter"] = {"t": r(T, 2), "L": [int(x) for x in L]}
D["lead"] = lead

# ---------- Coupling (all runs) ----------
coup = {"plv": {}, "instf_std": {}, "rawcorr": {}, "partial": {}}
for run in RUNS:
    t, th_raw, vel, fs = load_triple(run, decimate=10)
    thc = rest_centered(th_raw)
    b, a = butter(2, [0.4, 1.3], btype="band", fs=fs)
    ph = {i: np.angle(hilbert(filtfilt(b, a, thc[i] - thc[i].mean()))) for i in (1, 2, 3)}
    plv = {}
    for x, y in [(1, 3), (1, 2), (2, 3)]:
        d = wrap(ph[x] - ph[y]); plv[f"{x}{y}"] = round(float(np.abs(np.mean(np.exp(1j * d)))), 3)
    coup["plv"][run] = plv
    coup["instf_std"][run] = {i: round(float(np.std(np.diff(np.unwrap(ph[i])) * fs / (2*np.pi))), 3) for i in (1,2,3)}
    A = np.vstack([thc[1], thc[2], thc[3]]); C = np.corrcoef(A)
    p13 = (C[0,2] - C[0,1]*C[2,1]) / np.sqrt((1 - C[0,1]**2) * (1 - C[2,1]**2))
    coup["rawcorr"][run] = round(float(C[0,2]), 3)
    coup["partial"][run] = round(float(p13), 3)
D["coup"] = coup

# ---------- SVD reconstruction (run1, 50 Hz) ----------
X = np.vstack([th5[1], th5[2], th5[3]]).T
Xc = X - X.mean(0)
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
var = (S**2 / np.sum(S**2))
modeshape = []
for k in range(3):
    v = Vt[k] * np.sign(Vt[k][np.argmax(np.abs(Vt[k]))])
    modeshape.append([round(float(x), 3) for x in v])
recon = {"var": r(var, 4), "modeshape": modeshape, "fidelity": {}}
for k in (1, 2, 3):
    Xk = U[:, :k] @ np.diag(S[:k]) @ Vt[:k]
    recon["fidelity"][k] = [round(float(np.corrcoef(Xk[:, j], Xc[:, j])[0, 1]), 3) for j in range(3)]
X2 = U[:, :2] @ np.diag(S[:2]) @ Vt[:2]
W = t5 <= 20
recon["true"] = {j+1: r(Xc[W, j], 4) for j in range(3)}
recon["recon2"] = {j+1: r(X2[W, j], 4) for j in range(3)}
recon["tw"] = r(t5[W], 3)
tc = U * S
recon["coeff"] = {"m1": r(tc[W, 0], 4), "m2": r(tc[W, 1], 4)}
D["recon"] = recon

# ---------- Forecast (run1, 50 Hz, strictly causal) ----------
P_LAG, LAM, PDOM = 80, 1e-2, int(round(1.333*fs5))
Nf = len(Xc); split = Nf // 2
mu = X[:split].mean(0); Xcf = X - mu
_, _, Vtf = np.linalg.svd(Xcf[:split], full_matrices=False)
def build(c, h, t0, t1, p):
    rows = range(t0, t1 - h)
    return (np.array([c[t-p:t] for t in rows]), np.array([c[t+h] for t in rows]), list(rows))
coeffsf = Xcf @ Vtf[:3].T
horizons = [0.2, 0.5, 1, 2, 3, 5]
fc = {"h": horizons, "mode1": [], "mode2": [], "mode3": [], "AR": [], "persist": [], "periodAgo": []}
for hs in horizons:
    h = int(round(hs*fs5)); sk = []
    for k in range(3):
        Xtr, ytr, _ = build(coeffsf[:, k], h, P_LAG, split, P_LAG)
        w = np.linalg.solve(Xtr.T@Xtr + LAM*np.eye(P_LAG), Xtr.T@ytr)
        Xte, yte, rows = build(coeffsf[:, k], h, split, Nf, P_LAG)
        sk.append(float(np.corrcoef(Xte@w, yte)[0, 1]))
        if k == 1:
            idx = np.array(rows) + h
            fc["persist"].append(round(float(np.corrcoef(coeffsf[idx-h, k], coeffsf[idx, k])[0, 1]), 3))
            fc["periodAgo"].append(round(float(np.corrcoef(coeffsf[idx-PDOM, k], coeffsf[idx, k])[0, 1]), 3))
            fc["AR"].append(round(sk[1], 3))
    fc["mode1"].append(round(sk[0], 3)); fc["mode2"].append(round(sk[1], 3)); fc["mode3"].append(round(sk[2], 3))
# forecast-vs-truth (arm3, 2s ahead, test half)
H = 2.0; h = int(round(H*fs5)); K2 = 2
c2 = Xcf @ Vtf[:K2].T
predC = np.full((Nf, K2), np.nan)
for k in range(K2):
    Xtr, ytr, _ = build(c2[:, k], h, P_LAG, split, P_LAG)
    w = np.linalg.solve(Xtr.T@Xtr + LAM*np.eye(P_LAG), Xtr.T@ytr)
    Xte, yte, rows = build(c2[:, k], h, split, Nf, P_LAG)
    pr = Xte @ w
    for rr, tt in enumerate(rows): predC[tt+h, k] = pr[rr]
valid = ~np.isnan(predC[:, 0]); idx = np.where(valid)[0]
Xhat = predC[valid, :K2] @ Vtf[:K2]
XpA = c2[idx-PDOM, :K2] @ Vtf[:K2]
fc["fvt"] = {"t": r(t5[valid], 3), "truth": r(Xcf[valid, 2], 4),
             "pred": r(Xhat[:, 2], 4), "periodago": r(XpA[:, 2], 4)}
D["fc"] = fc

# ---------- Predict last arm (run1) ----------
thp = {i: th5[i] - th5[i][:split].mean() for i in (1, 2, 3)}
def predict_arm3(h, use_self):
    rows = range(P_LAG, split - h)
    if use_self: F = np.array([thp[3][t-P_LAG:t] for t in rows])
    else: F = np.array([np.concatenate([thp[1][t-P_LAG:t], thp[2][t-P_LAG:t]]) for t in rows])
    y = np.array([thp[3][t+h] for t in rows])
    w = np.linalg.solve(F.T@F + 1e-1*np.eye(F.shape[1]), F.T@y)
    rows2 = list(range(split, Nf - h))
    if use_self: Ft = np.array([thp[3][t-P_LAG:t] for t in rows2])
    else: Ft = np.array([np.concatenate([thp[1][t-P_LAG:t], thp[2][t-P_LAG:t]]) for t in rows2])
    yt = np.array([thp[3][t+h] for t in rows2]); pr = Ft @ w
    full = np.full(Nf, np.nan)
    for rr, t in enumerate(rows2): full[t+h] = pr[rr]
    return float(np.corrcoef(pr, yt)[0, 1]), full
pl = {"h": [0.0, 0.2, 0.5, 1.0, 2.0], "from12": [], "self": []}
for hs in pl["h"]:
    h = int(round(hs*fs5))
    c12, full = predict_arm3(h, False); cs, _ = predict_arm3(h, True)
    pl["from12"].append(round(c12, 3)); pl["self"].append(round(cs, 3))
    if hs == 0.0:
        v = ~np.isnan(full)
        pl["nowcast"] = {"t": r(t5[v], 3), "truth": r(thp[3][v], 4), "pred": r(full[v], 4)}
D["predlast"] = pl

# ---------- Animated pendulum (run1, 50 Hz, first 30 s, equal unit lengths) ----------
ta, tha_raw, _, _ = load_triple("run1", decimate=200)
m = ta <= 30.0
L = 1.0
x0 = L*np.sin(tha_raw[1][m]); y0 = L*np.cos(tha_raw[1][m])
x1 = x0 + L*np.sin(tha_raw[2][m]); y1 = y0 + L*np.cos(tha_raw[2][m])
x2 = x1 + L*np.sin(tha_raw[3][m]); y2 = y1 + L*np.cos(tha_raw[3][m])
D["anim"] = {"t": r(ta[m], 2),
             "x": [r(x0, 3), r(x1, 3), r(x2, 3)],
             "y": [r(y0, 3), r(y1, 3), r(y2, 3)]}

open(os.path.join(HERE, "_data.json"), "w").write(json.dumps(D))
print("data computed. keys:", list(D.keys()))
print("approx json size (KB):", round(len(json.dumps(D))/1024))

# ---------- Carrier + slow decay envelope (the two waves) ----------
te, ter_raw, _, fse = load_triple("run1", decimate=20)  # 500 Hz
ter = rest_centered(ter_raw)
bb, aa = butter(2, [0.4, 1.3], btype="band", fs=fse)
sub_e = max(1, int(round(fse / 50)))  # ~50 Hz for display
ENV = {"t": r(te[::sub_e], 3), "carrier": {}, "env": {}}
for i in (1, 2, 3):
    x = ter[i] - ter[i].mean()
    car = filtfilt(bb, aa, x)
    en = np.abs(hilbert(car))
    ENV["carrier"][i] = r(car[::sub_e], 4)
    ENV["env"][i] = r(en[::sub_e], 4)
decay = {}
for run in RUNS:
    tt, tr2, _, f2 = load_triple(run, decimate=20)
    th2 = rest_centered(tr2)
    dd = {}
    for i in (1, 2, 3):
        e2 = np.abs(hilbert(filtfilt(bb, aa, th2[i] - th2[i].mean())))
        b6 = np.array_split(e2, 6)
        dd[i] = round(float(b6[0].mean() / b6[-1].mean()), 2)
    decay[run] = dd
ENV["decay"] = decay
D["env"] = ENV

# ---- inject embedded data into the HTML template (one-command reproducible) ----
_tpl = open(os.path.join(HERE, "template.html")).read()
import plotly.offline as _po
_html=_tpl.replace("__PLOTLY_JS__", _po.get_plotlyjs()).replace("__DATA_JSON__", json.dumps(D))
open(os.path.join(HERE, "pendulum_dashboard.html"), "w").write(_html)
print("wrote pendulum_dashboard.html")

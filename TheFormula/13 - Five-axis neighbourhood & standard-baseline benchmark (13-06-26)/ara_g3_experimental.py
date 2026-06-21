"""ARA-G3 EXPERIMENTAL predictor — geometry-native, incremental.
DOES NOT touch the stable root trio (ara_framework/mapper/predictor). Sandbox only;
a piece graduates into the stable engine only after it beats the real baselines.

Geometry = the 5-axis sphere from 3D models/ara_sphere_coordinate_3d.html:
  X = mapping / ARA (0..2, DYNAMIC per tick), Y = rungs, Z = connection->info,
  phi = coupling efficiency, anti-phi = mirror.
Per Dylan: ARA is computed per tick (local build/release); the prediction step is the
SAME layered sand-style engine (ara_framework), just with the flow tweaked by the
topographic values; key rule: more information (higher Z) => closer to the ideal phi handover.
phi vs anti-phi: used as TWO unsigned distance coordinates (most consistent with the engine's
unsigned coupling magnitudes); noted in the result doc.

Versions:
  A = geometry-native: stable sand-engine features + per-tick sphere coords + info->phi flow tweak.
  B = bolt-on: stable ARA prediction + elastic-wall bounce (elasticity 1/phi) + regime gate.
  (phase_amp_split kept below as the logged dud precursor.)
"""
import os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import ara_framework as F
PHI = F.PHI

# ---------- piece 1 (logged dud): phase/amplitude split ----------
def _trail(x, w, fn):
    out = np.full(len(x), np.nan)
    for i in range(len(x)):
        a = x[max(0, i-w+1):i+1]; a = a[np.isfinite(a)]
        if len(a) >= 3: out[i] = fn(a)
    return out
def phase_amp_split(x, P, h, cut):
    x = np.asarray(x, float); n = len(x); P = int(round(P))
    level = _trail(x, P, np.mean); env = _trail(x, P, lambda a: (np.max(a)-np.min(a))/2.0)+1e-9
    z = (x-level)/env; te = np.arange(cut, n-h); pred = np.empty(len(te))
    for j, t in enumerate(te):
        src = t+h-P; shape = z[src] if (src >= 0 and np.isfinite(z[src])) else 0.0
        pred[j] = level[t] + env[t]*shape
    return te, pred

# ---------- shared ----------
def _ridge(Xtr, ytr, Xte, pen=0.1):
    mu = np.nanmean(Xtr, 0); sd = np.nanstd(Xtr, 0); sd[~np.isfinite(sd) | (sd < 1e-9)] = 1.0
    A = np.nan_to_num((Xtr-mu)/sd); B = np.nan_to_num((Xte-mu)/sd)
    A = np.column_stack([np.ones(len(A)), A]); B = np.column_stack([np.ones(len(B)), B])
    R = np.eye(A.shape[1])*pen; R[0, 0] = 0.0
    return B @ np.linalg.solve(A.T@A+R, A.T@ytr)

def _sphere_coords(state, origins):
    """Per-tick 5-axis sphere state from the stable engine's per-tick fields."""
    X = state['ara'][origins]                                   # X = dynamic ARA (0..2)
    osp = np.nan_to_num(state['own_spin'][origins]); tq = np.nan_to_num(state['lower_torque'][origins])
    Zraw = np.abs(osp) + np.abs(tq)                             # Z = connection->info (local movement/coupling)
    Z = (Zraw - np.nanmean(Zraw)) / (np.nanstd(Zraw)+1e-9)
    phi_dist = np.abs(X - PHI)                                  # phi = coupling efficiency (dist to golden ARA)
    antiphi_dist = np.abs(X - (2.0-PHI))                        # anti-phi = mirror (dist to 0.382)
    phi_gate = 1.0/(1.0+np.exp(-Z))                             # more info (Z) -> closer to phi handover
    roll = np.nan_to_num(state['roll'][origins])
    info_to_phi = phi_gate * roll                              # the flow tweak: info modulates the handover/flow
    return np.column_stack([X, Z, phi_dist, antiphi_dist, phi_gate, info_to_phi])

def _split(system):
    n = len(system.home); cut = int(n/PHI); st = F._layer_state(system, cut)
    start = max(max(system.home_lags), *(c.window+2 for c in system.lower+system.upper))
    return n, cut, st, start

# ---------- Version A: geometry-native ----------
def version_A(system):
    n, cut, st, start = _split(system); out = {}
    for h in system.horizons:
        tr = np.arange(start, cut-h); te = np.arange(cut, n-h); dtr = system.home[tr+h]-system.home[tr]
        if len(tr) < 30 or len(te) < 30: out[h] = None; continue
        base_tr = F._feature_matrix(system, st, tr, True); base_te = F._feature_matrix(system, st, te, True)
        Xtr = np.column_stack([base_tr, _sphere_coords(st, tr)]); Xte = np.column_stack([base_te, _sphere_coords(st, te)])
        out[h] = system.home[te] + _ridge(Xtr, dtr, Xte)
    return out

# ---------- Version B: stable ARA + elastic wall + regime gate ----------
def version_B(system, wall_k=1.5, elasticity=None, regime_band=0.12):
    if elasticity is None: elasticity = 1.0/PHI
    n, cut, st, start = _split(system); P = int(round(system.home_period))
    lvl = np.array([np.mean(system.home[max(0,i-P+1):i+1]) for i in range(n)])
    sig = np.array([np.std(system.home[max(0,i-P+1):i+1]) for i in range(n)])
    out = {}
    for h in system.horizons:
        tr = np.arange(start, cut-h); te = np.arange(cut, n-h); dtr = system.home[tr+h]-system.home[tr]
        if len(tr) < 30 or len(te) < 30: out[h] = None; continue
        base = system.home[te] + F._ridge_readout(F._feature_matrix(system, st, tr, True), dtr,
                                                  F._feature_matrix(system, st, te, True))
        pred = base.copy()
        for j, t in enumerate(te):
            hi = lvl[t] + wall_k*sig[t]; lo = lvl[t] - wall_k*sig[t]
            if pred[j] > hi: pred[j] = hi - elasticity*(pred[j]-hi)        # elastic bounce off upper wall
            elif pred[j] < lo: pred[j] = lo + elasticity*(lo-pred[j])      # ... lower wall
            if abs(st['ara'][t]-1.0) < regime_band:                       # regime gate: near balance/transition
                src = t+h-P
                if src >= 0: pred[j] = 0.5*pred[j] + 0.5*system.home[src]  # blend toward seasonal-naive
        out[h] = pred
    return out

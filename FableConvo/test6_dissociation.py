"""
Test 6 - Present/Future dissociation (session queue, 2 Jul 2026)
=================================================================
RULE UNDER TEST (Dylan): "Larger waves dominate RIGHT NOW; lower/slower
structure dominates THE FUTURE."
Established half (prior repo result, 3/3): arm-3 (most energetic) leads the
present (turns first most often, longest dominance blocks).
Open half (PREDICTION, stated before running): strictly-causal forecast skill
should route through the SLOW COMMON MODE, not through energetic arm-3 --
i.e., at mid/long horizons, common-mode-past features forecast any arm's
future better than arm-3-past features do.
Strict causality: train/test split in time; SVD modes + means from train only;
features = past samples only; ridge weights fit on train only.
"""
import numpy as np, scipy.io as sio, sys

# ---------------------------------------------------------------- data fetch
# OUT-OF-THE-BOX RULE (TEST_PROTOCOL.md): if the data is not at DATA_DIR,
# download it from the canonical source before running.
# Source: Kaheman, Fasel, Bramburger, Strom, Kutz, Brunton (2022),
#   "The Experimental Multi-Arm Pendulum on a Cart", Zenodo,
#   DOI 10.5281/zenodo.6633719, CC-BY-4.0.
# Archive: MultiArm-Pendulum.zip, 288.4 MB, md5 b7ef285267d3ebb7f31370ad1df55b99
import os, hashlib, urllib.request, zipfile

DATA_DIR = os.environ.get("ARA_PENDULUM_DIR", os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "pendulum_data"))
_ZIP_URL = "https://zenodo.org/records/6633719/files/MultiArm-Pendulum.zip?download=1"
_ZIP_MD5 = "b7ef285267d3ebb7f31370ad1df55b99"

def ensure_data(filenames):
    """Return {name: local_path}; download + extract from Zenodo if missing."""
    paths = {n: os.path.join(DATA_DIR, n) for n in filenames}
    missing = [n for n, p in paths.items() if not os.path.exists(p)]
    if not missing:
        return paths
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"[fetch] {len(missing)} file(s) missing; downloading Zenodo 6633719 "
          f"(288 MB, one-time)...")
    # archive lives in DATA_DIR itself: system temp dirs vary across machines
    # (portability bug caught in sandbox testing, 3 Jul) and the zip is reused
    # by the other pendulum scripts.
    tmp = os.path.join(DATA_DIR, "MultiArm-Pendulum.zip")
    if not os.path.exists(tmp) or hashlib.md5(open(tmp,'rb').read()).hexdigest() != _ZIP_MD5:
        urllib.request.urlretrieve(_ZIP_URL, tmp + ".part")
        got = hashlib.md5(open(tmp + ".part", 'rb').read()).hexdigest()
        assert got == _ZIP_MD5, f"md5 mismatch: {got} (expected {_ZIP_MD5})"
        os.replace(tmp + ".part", tmp)
        print("[fetch] md5 verified.")
    with zipfile.ZipFile(tmp) as z:
        for member in z.namelist():
            base = os.path.basename(member)
            if base in missing:
                with z.open(member) as src, open(paths[base], "wb") as dst:
                    dst.write(src.read())
                print(f"[fetch] extracted {base}")
    still = [n for n, p in paths.items() if not os.path.exists(p)]
    assert not still, f"not found in archive: {still}"
    return paths
# --------------------------------------------------------------- /data fetch


FILES = ["TripleDataFreeSwing_%d_Dt_0_0001.mat" % r for r in (1,2,3)]
PATHS = ensure_data(FILES)
DATA = os.path.join(DATA_DIR, "TripleDataFreeSwing_{}_Dt_0_0001.mat")
Q = 200  # decimate 10kHz -> 50 Hz

def wrap(a): return (a + np.pi) % (2*np.pi) - np.pi

def load(run):
    m = sio.loadmat(DATA.format(run))
    th = {i: m[f"Theta{i}"].ravel()[::Q] for i in (1,2,3)}
    dt = float(np.asarray(m["dt"]).ravel()[0]); fs = 1.0/(dt*Q)
    # rest-center each arm (circular mean)
    out = {}
    for i in (1,2,3):
        r = np.arctan2(np.mean(np.sin(th[i])), np.mean(np.cos(th[i])))
        out[i] = wrap(th[i]-r)
    return out, fs

def ridge_forecast(feat_past, target, h, split, p, lam=1e-2):
    """feat_past: (N,) causal feature series; predict target[t+h] from
    feat_past[t-p+1..t]. Fit on train (t+h < split), score corr on test."""
    N = len(target)
    rows, ys, idx = [], [], []
    for t0 in range(p-1, N-h):
        rows.append(feat_past[t0-p+1:t0+1]); ys.append(target[t0+h]); idx.append(t0+h)
    X = np.asarray(rows); y = np.asarray(ys); idx = np.asarray(idx)
    tr = idx < split; te = ~tr
    if tr.sum() < 50 or te.sum() < 50: return np.nan
    mu = X[tr].mean(0); Xc = X-mu
    w = np.linalg.solve(Xc[tr].T@Xc[tr] + lam*np.eye(p), Xc[tr].T@(y[tr]-y[tr].mean()))
    pred = Xc[te]@w + y[tr].mean()
    c = np.corrcoef(pred, y[te])[0,1]
    return c

P = 80  # 1.6 s of past at 50 Hz
HORIZONS_S = [0.5, 1, 2, 4, 8]

print("TEST 6 - strictly-causal: whose PAST carries each arm's FUTURE?")
print("features: arm3-past (energetic leader) vs COMMON-MODE-past (slow, train-only mode-1)")
print("prediction on record: common-mode wins at mid/long horizons\n")

tally = {"common":0, "arm3":0}
for run in (1,2,3):
    th, fs = load(run)
    X = np.vstack([th[1], th[2], th[3]]).T
    N = len(X); split = N//2
    mu = X[:split].mean(0); Xc = X-mu
    _,_,Vt = np.linalg.svd(Xc[:split], full_matrices=False)   # train-only modes
    common = Xc @ Vt[0]          # mode-1 coefficient = shared slow clock (causal projection)
    arm3   = Xc[:,2]
    print(f"--- run {run}  (N={N}, {N/fs:.0f}s, split at {split/fs:.0f}s) ---")
    print(f'{"target":<8}{"h(s)":>6} | {"common-past":>12}{"arm3-past":>11}{"own-past":>10}{"persist":>9}')
    for j,name in [(0,"arm1"),(1,"arm2"),(2,"arm3")]:
        y = Xc[:,j]
        for hs in HORIZONS_S:
            h = int(hs*fs)
            cC = ridge_forecast(common, y, h, split, P)
            c3 = ridge_forecast(arm3,   y, h, split, P)
            cO = ridge_forecast(y,      y, h, split, P)
            # persistence baseline: corr(y[t], y[t+h]) on test
            te = np.arange(split, N-h)
            cP = np.corrcoef(y[te], y[te+h])[0,1]
            win = "common" if (np.nan_to_num(cC) > np.nan_to_num(c3)) else "arm3"
            if hs >= 2: tally[win] += 1
            print(f"{name:<8}{hs:>6} | {cC:>12.3f}{c3:>11.3f}{cO:>10.3f}{cP:>9.3f}")
    print()

print(f"MID/LONG-HORIZON (>=2s) WINS: common-mode {tally['common']}  vs  arm3 {tally['arm3']}")
print("(rule predicts common-mode majority)")

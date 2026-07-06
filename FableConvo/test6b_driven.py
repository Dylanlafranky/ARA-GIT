"""
Test 6b - Present/Future dissociation, DRIVEN regime (harsher test).
Driven triple run (cart control active) breaks the free-swing common clock.
Same strictly-causal design as test6; plus a light leadership re-check
(who turns first, prominence-filtered) to re-measure the PRESENT half here.
"""
import numpy as np, scipy.io as sio

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

from scipy.signal import find_peaks

m = sio.loadmat(ensure_data(['TripleDataWithControl_1_Dt_0_0001.mat'])['TripleDataWithControl_1_Dt_0_0001.mat'])
Q = 200
th = {}
for i in (1,2,3):
    x = m[f"Theta{i}"].ravel()[::Q]
    r = np.arctan2(np.mean(np.sin(x)), np.mean(np.cos(x)))
    th[i] = (x - r + np.pi) % (2*np.pi) - np.pi
dt = float(np.asarray(m['dt']).ravel()[0]); fs = 1.0/(dt*Q)
X = np.vstack([th[1], th[2], th[3]]).T
N = len(X)

# dominant period (train half, arm2)
split = N//2
f = np.fft.rfftfreq(split, 1/fs); A = np.abs(np.fft.rfft(X[:split,1]-X[:split,1].mean()))
Pdom = 1/f[1:][np.argmax(A[1:])]
print(f"driven run: N={N} ({N/fs:.0f}s), dominant period ~{Pdom:.2f}s")

# --- PRESENT: leadership, prominence-filtered turn detector ---
peaks = {}
for j in range(3):
    y = X[:,j]
    pk,_ = find_peaks(np.abs(y), prominence=0.25*np.std(y), distance=int(0.4*Pdom*fs))
    peaks[j] = pk/fs
allp = sorted([(t,j) for j in range(3) for t in peaks[j]])
lead = [0,0,0]; i = 0
while i < len(allp):
    t0, j0 = allp[i]; grp = [(t0,j0)]; k = i+1
    while k < len(allp) and allp[k][0]-t0 < 0.5*Pdom: grp.append(allp[k]); k += 1
    if len(set(j for _,j in grp)) >= 2: lead[grp[0][1]] += 1
    i = k
tot = sum(lead)
print(f"PRESENT (who turns first, {tot} multi-arm swing events): "
      f"arm1 {lead[0]/tot:.0%}  arm2 {lead[1]/tot:.0%}  arm3 {lead[2]/tot:.0%}")

# --- FUTURE: same causal ridge comparison ---
mu = X[:split].mean(0); Xc = X-mu
_,S,Vt = np.linalg.svd(Xc[:split], full_matrices=False)
print(f"train-only SVD variance shares: {np.round(S**2/np.sum(S**2),3)}")
common = Xc @ Vt[0]; arm3 = Xc[:,2]
P = 80
def ridge_fc(feat, target, h, lam=1e-2):
    rows, ys, idx = [], [], []
    for t0 in range(P-1, N-h):
        rows.append(feat[t0-P+1:t0+1]); ys.append(target[t0+h]); idx.append(t0+h)
    Xf = np.asarray(rows); y = np.asarray(ys); idx = np.asarray(idx)
    tr = idx < split; te = ~tr
    muf = Xf[tr].mean(0); Xn = Xf-muf
    w = np.linalg.solve(Xn[tr].T@Xn[tr] + lam*np.eye(P), Xn[tr].T@(y[tr]-y[tr].mean()))
    return np.corrcoef(Xn[te]@w + y[tr].mean(), y[te])[0,1]

print(f'\n{"target":<8}{"h(s)":>6} | {"common-past":>12}{"arm3-past":>11}{"own-past":>10}{"persist":>9}')
tally = {"common":0,"arm3":0}
for j,name in [(0,"arm1"),(1,"arm2"),(2,"arm3")]:
    y = Xc[:,j]
    for hs in [0.5,1,2,4,8]:
        h = int(hs*fs)
        cC = ridge_fc(common,y,h); c3 = ridge_fc(arm3,y,h); cO = ridge_fc(y,y,h)
        te = np.arange(split, N-h); cP = np.corrcoef(y[te], y[te+h])[0,1]
        if hs>=2: tally["common" if cC>c3 else "arm3"] += 1
        print(f"{name:<8}{hs:>6} | {cC:>12.3f}{c3:>11.3f}{cO:>10.3f}{cP:>9.3f}")
print(f"\nMID/LONG (>=2s) WINS: common {tally['common']} vs arm3 {tally['arm3']}")

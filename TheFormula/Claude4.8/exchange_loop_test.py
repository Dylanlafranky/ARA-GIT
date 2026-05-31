"""
EXCHANGE-CHANNEL CLOSURE TEST (task #95)
Dylan: ENSO fails the mix test BECAUSE it is the exchange channel between two real
A-systems -- the BROWN and GOLD(GREEN) meta-bands. ENSO = Brown<->Gold phi exchange rate.
Predictions fixed BEFORE run:
  P-a BROWN passes mix test (z>=2); P-b GOLD passes; P-c full NINO3.4 fails (z<2);
  P-d Brown<->Gold anti-phase, period ratio near phi.
"""
import numpy as np
from scipy.signal import butter, sosfiltfilt, correlate, correlation_lags

PHI = (1 + 5 ** 0.5) / 2
GREEN_MO = [27.9, 30.7]
BROWN_MO = [42.5, 54.0, 66.9]
rng = np.random.default_rng(7)

def load_nino(path):
    vs = []
    for ln in open(path):
        ln = ln.strip()
        if not ln or ln[0].isalpha():
            continue
        p = ln.replace(",", " ").split()
        try:
            v = float(p[-1])
        except ValueError:
            continue
        if v <= -99:
            continue
        vs.append(v)
    return np.array(vs)

def bp(x, period, ratio=1.3):
    fs = 1.0; ny = fs / 2
    lo = 1.0 / (period * ratio); hi = 1.0 / (period / ratio)
    lo, hi = max(lo, 1e-6), min(hi, ny * 0.99)
    sos = butter(3, [lo / ny, hi / ny], btype="band", output="sos")
    return sosfiltfilt(sos, x)

def bp_multi(x, periods, ratio=1.25):
    out = np.zeros_like(x, dtype=float)
    for P in periods:
        out += bp(x, P, ratio)
    return out

def phase_rand(x):
    X = np.fft.rfft(x)
    ph = rng.uniform(0, 2 * np.pi, len(X)); ph[0] = 0
    if len(x) % 2 == 0:
        ph[-1] = 0
    return np.fft.irfft(np.abs(X) * np.exp(1j * ph), n=len(x))

def pcl(a, b, maxlag):
    a = (a - a.mean()) / (a.std() + 1e-12)
    b = (b - b.mean()) / (b.std() + 1e-12)
    c = correlate(a, b, mode="full") / len(a)
    lags = correlation_lags(len(a), len(b), mode="full")
    m = np.abs(lags) <= maxlag
    c, lags = c[m], lags[m]
    k = np.argmax(c)
    return c[k], lags[k]

def mix_test(x, P, nn=40):
    r1, r2, r3 = P, P * PHI, P * PHI ** 2
    if len(x) < 6 * r3:
        return None
    gen = bp(bp(x, r1) * bp(x, r2), r3); ac = bp(x, r3)
    maxlag = int(r3)
    recon, lag = pcl(gen, ac, maxlag)
    null = []
    for _ in range(nn):
        xs = phase_rand(x)
        g = bp(bp(xs, r1) * bp(xs, r2), r3); a = bp(xs, r3)
        null.append(pcl(g, a, maxlag)[0])
    null = np.array(null)
    z = (recon - null.mean()) / (null.std() + 1e-12)
    return dict(P=P, recon=float(recon), lag_frac=float(lag) / (P * PHI ** 2),
                z=float(z), null_mean=float(null.mean()))

def main():
    x = load_nino("nino34_long_anom.csv")
    print(f"NINO3.4 monthly N={len(x)}  ({len(x)/12:.0f} yr)\n")
    brown = bp_multi(x, BROWN_MO); gold = bp_multi(x, GREEN_MO)
    P_brown = float(np.mean(BROWN_MO)); P_gold = float(np.mean(GREEN_MO))
    print("=== Mix test (next rung = mix of two below) ===")
    print(f"{'signal':>20} {'home_mo':>8} {'recon':>7} {'z':>6} {'lag_frac':>8}  verdict")
    for name, sig, P in [("BROWN band", brown, P_brown), ("GOLD band", gold, P_gold),
                         ("NINO3.4(full,brown)", x, P_brown), ("NINO3.4(full,gold)", x, P_gold)]:
        r = mix_test(sig, P)
        if r is None:
            print(f"{name:>20}  too short"); continue
        verdict = "PASS (builds tower)" if r["z"] >= 2 else "fail (no tower)"
        print(f"{name:>20} {P:>8.1f} {r['recon']:>+7.2f} {r['z']:>+6.1f} {r['lag_frac']:>+8.2f}  {verdict}")
    print("\n=== Exchange-pair signature (Brown <-> Gold) ===")
    cc, lag = pcl(brown, gold, maxlag=int(P_brown))
    tag = 'ANTI-PHASE' if cc < -0.2 else 'in-phase' if cc > 0.2 else 'weak'
    print(f"Brown vs Gold peak xcorr = {cc:+.2f} at lag {lag} mo ({tag})")
    ratio = P_brown / P_gold
    print(f"Brown:Gold period ratio = {P_brown:.1f}/{P_gold:.1f} = {ratio:.3f}  (phi={PHI:.3f}, off {abs(ratio-PHI)/PHI*100:.0f}%)")
    exch = brown - gold
    ce, _ = pcl(exch, x, maxlag=24); cb, _ = pcl(brown, x, maxlag=24); cg, _ = pcl(gold, x, maxlag=24)
    print(f"\ncorr to full NINO3.4:  Brown {cb:+.2f}  Gold {cg:+.2f}  Brown-Gold(exchange) {ce:+.2f}")

if __name__ == "__main__":
    main()

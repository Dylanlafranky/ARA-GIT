"""
T-LLM-1 — IS THE SUBSTRATE'S ~1.25 A SINGLE DECOUPLED MODE? (registered 3 Jul 2026)
====================================================================================
EXECUTION EMBARGO: do not run on real activations until this design has been
reviewed by a NON-Anthropic model family (LLM_WORK_SAFEGUARDS.md, S2). The
synthetic calibration section may run any time (S1).

CONTEXT: LLM/00_LLM_THREAD_SUMMARY.md — canonical re-measure read the trained
substrate at node ARA ~1.23-1.29 (engine-leaning, time-side of ridge), after
three earlier "clock" readings were exposed as ONE un-decoupled artifact
(coupled-pair averaging -> sea level). The summary's own queued verification:
confirm the ~1.25 is a property of a SINGLE decoupled mode.

JURISDICTION NOTE (pinned boundary): rise/fall ARA is a SHAPE measure. This
test CLASSIFIES the substrate's position; it is NOT a phi adjudicator. The
phi-jurisdiction tests are T-LLM-2/3 (motion measures: dominance duty under
free-vs-forced decoding; phase-step with lock detection).

DATA: LLM/llm_raw_node_series.npz (in-repo; out-of-the-box rule satisfied
natively). Keys: {size}_step{trainstep}; arrays (n_nodes=55, n_gen=200).
n=200 is SHORT — synthetic calibration at n=200 is mandatory and built in.

PRE-REGISTERED CHECKS per node (final training step, all sizes):
 C1 SINGLE-MODE: dominant spectral peak isolation — power ratio of 2nd
    non-harmonic peak to 1st < 0.5 counts as single-mode; also harmonic
    test (dominant period an integer multiple of a stronger faster peak ->
    composite, flag).
 C2 RUNG AUDIT (middles rule, session notes §31): per-rung power table
    reported for every node — no middle reading is self-certifying.
 C3 BOTH DUTIES on the dominant rung: rise/fall duty (shape) AND dominance
    duty between the two strongest rungs (motion) — bias-corrected against
    the built-in n=200 synthetic calibration.
PREDICTIONS:
 P1: majority of nodes pass C1 (single-mode). RIVAL: composite majority ->
     the ~1.25 RETRACTS to "unresolved composite" per the middles rule.
 P2: after calibration, dominant-rung rise/fall duty sits off 0.5 (engine-
     leaning, consistent with ~1.25). RIVAL: duty -> 0.5 after decoupling =
     the substrate is a clock after all and the canonical re-measure was
     itself contaminated.
FALSIFICATION IS A FIRST-CLASS OUTCOME. n=200 caveats apply to everything.
"""
import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.signal import find_peaks

NPZ = "LLM/llm_raw_node_series.npz"   # run from repo root
SIZES = ["70m", "160m", "410m"]
SEED = 42

def spectrum(x):
    x = x - np.mean(x)
    A = np.abs(rfft(x)); A[0] = 0
    f = rfftfreq(len(x), 1.0)
    return f, A

def single_mode_check(x):
    """C1: (isolation_ratio, is_harmonic_composite, dominant_period)."""
    f, A = spectrum(x)
    i1 = int(np.argmax(A))
    # exclude +-1 bins and harmonics of the dominant when hunting peak 2
    mask = np.ones_like(A, bool); mask[max(0,i1-1):i1+2] = False
    for h in (2, 3, 4):
        j = i1 * h
        if j < len(A): mask[max(0,j-1):j+2] = False
    i2 = int(np.argmax(np.where(mask, A, 0)))
    iso = A[i2] / A[i1] if A[i1] > 0 else np.nan
    # harmonic test: a FASTER bin at f1*h (h>=2) stronger than 0.8*A[i1]
    harm = any(A[i1*h] > 0.8*A[i1] for h in (2,3) if i1*h < len(A))
    period = 1.0/f[i1] if f[i1] > 0 else np.nan
    return iso, harm, period

def rung_powers(x, n_rungs=6):
    """C2: power per octave rung below Nyquist (audit table)."""
    f, A = spectrum(x); P = A**2
    edges = [0.5/2**k for k in range(n_rungs+1)]   # cycles/step
    return [float(P[(f > lo) & (f <= hi)].sum())
            for hi, lo in zip(edges[:-1], edges[1:])]

def rise_fall_duty(x, period):
    P = max(2, int(round(period)))
    pk, _ = find_peaks(x, distance=max(1, int(0.6*P)))
    tr, _ = find_peaks(-x, distance=max(1, int(0.6*P)))
    duties = []
    for p in pk:
        a = tr[tr < p]; b = tr[tr > p]
        if len(a) and len(b):
            full = b[0]-a[-1]
            if 0.2*P < full < 2.5*P: duties.append((p-a[-1])/full)
    return float(np.mean(duties)) if duties else np.nan

def calibrate(n=200, true_duty=0.556, reps=200):
    """S1/known-referee: sawtooth at n=200; returns measured-mean bias."""
    rng = np.random.default_rng(SEED)
    outs = []
    for _ in range(reps):
        P = rng.uniform(12, 30); t = np.arange(n)
        ph = (t/P) % 1.0
        x = np.where(ph < true_duty, ph/true_duty, (1-ph)/(1-true_duty))
        x += 0.15*rng.standard_normal(n)
        d = rise_fall_duty(x, P)
        if np.isfinite(d): outs.append(d)
    return float(np.mean(outs)) - true_duty

if __name__ == "__main__":
    print("CALIBRATION (synthetic, n=200, true duty 0.556):")
    bias = calibrate()
    print(f"  measured bias = {bias:+.4f}  (subtract from all real readings)")
    print("\n== REAL DATA (requires S2 sign-off; comment out the exit) ==")
    raise SystemExit("S2 EMBARGO: second-family review required before real run.")
    d = np.load(NPZ, allow_pickle=True)
    for size in SIZES:
        keys = sorted((k for k in d.keys() if k.startswith(size)),
                      key=lambda k: int(k.split("step")[1]))
        k = keys[-1]                      # final training step
        M = d[k]
        res = []
        for node in range(M.shape[0]):
            x = M[node].astype(float)
            iso, harm, period = single_mode_check(x)
            duty = rise_fall_duty(x, period) - bias if np.isfinite(period) else np.nan
            res.append((iso, harm, duty))
            rp = rung_powers(x)
        iso_a = np.array([r[0] for r in res]); harm_a = np.array([r[1] for r in res])
        duty_a = np.array([r[2] for r in res])
        single = np.mean((iso_a < 0.5) & (~harm_a))
        print(f"{k}: single-mode fraction {single:.2f} | "
              f"median corrected duty {np.nanmedian(duty_a):.3f} "
              f"(clock=0.500; ARA 1.25 -> 0.556)")

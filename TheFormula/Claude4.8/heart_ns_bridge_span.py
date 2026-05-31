"""
Is the nervous system a "2" (an open bridge), not a closed "3"?  (Dylan, 2026-05-30)
====================================================================================
If the NS is an OPEN 2 -- two docking faces with one tether -- it should span a wide gap
and reach two different systems, building a large phi^9 coupling exchange. Two checks:

(1) RUNG GAP between the two faces (breath = fast face, brain/EEG = slow face).
    Measure each channel's dominant cycle period (beats); gap = log_phi(p_slow/p_fast).
    A bridge across a big span lands near 9 (phi^9). A tight local 3 sits ~1-2 rungs apart.
    (slow face: linear-detrend first so the record-length drift isn't read as a cycle.)

(2) DO THEIR ARAs CANCEL?  ARA = T_release/T_accumulation from rise/fall asymmetry.
    A balanced 2 at the shock-absorber point mirrors: ARA_fast * ARA_slow ~ 1 (gmean ~1).

Descriptive measurement on the whole record (no forecast). slp01a, real.
"""
import numpy as np
import heart_info_exchange_R as H
import heart_fast_forwardspin as F

PHI = (1 + 5 ** 0.5) / 2

def top_periods(x, k=3, pmin=2.0, pmax=2000.0, detrend=False):
    x = np.asarray(x, float)
    if detrend:
        t = np.arange(len(x)); x = x - np.polyval(np.polyfit(t, x, 1), t)
    x = x - x.mean(); n = len(x)
    sp = np.abs(np.fft.rfft(x * np.hanning(n))); fr = np.fft.rfftfreq(n, d=1.0)
    per = np.full_like(fr, np.nan); per[1:] = 1.0 / fr[1:]
    ok = (per >= pmin) & (per <= pmax)
    idx = np.argsort(sp[ok])[::-1][:k]
    return np.round(per[ok][idx], 1)

def ara_from_asym(x):
    x = np.asarray(x, float)
    d = np.sign(x - x.mean())
    flips = np.where(np.diff(d) != 0)[0]
    if len(flips) < 4: return np.nan
    segs = np.diff(flips)
    up = segs[0::2].mean(); dn = segs[1::2].mean()
    return np.nan if up == 0 else dn / up

def main():
    rr, fe = H.per_beat_series()
    resp = np.asarray(fe["Resp"], float)
    eeg  = np.asarray(fe["EEG"],  float)
    p_fast = top_periods(resp, k=1)[0]                                    # breath fast cycle
    eeg_slow_env = F.trailing_slow(eeg, 60)                              # brain slow state
    p_slow = top_periods(eeg_slow_env, k=1, pmax=len(rr)*0.9, detrend=True)[0]
    rungs = np.log(p_slow / p_fast) / np.log(PHI)

    a_fast = ara_from_asym(resp)
    a_slow = ara_from_asym(eeg_slow_env)
    gmean = (a_fast * a_slow) ** 0.5
    amean = (a_fast + a_slow) / 2

    print("NS as an open 2 -- bridge test (slp01a, %d beats)\n" % len(rr))
    print("(1) RUNG GAP between the two faces")
    print("    breath  dominant period = %8.1f beats  (fast face)" % p_fast)
    print("    brain   dominant period = %8.1f beats  (slow face)" % p_slow)
    print("    gap = log_phi(slow/fast)= %8.2f phi-rungs   (phi^9 => ~9)" % rungs)
    print("    breath top periods: %s" % top_periods(resp))
    print("    brain  top periods: %s\n" % top_periods(eeg_slow_env, pmax=len(rr)*0.9, detrend=True))

    print("(2) DO THE TWO FACES' ARAs CANCEL?")
    print("    ARA breath (fast face)  = %5.3f" % a_fast)
    print("    ARA brain  (slow face)  = %5.3f" % a_slow)
    print("    product           = %5.3f   (1.0 => perfect mirror cancel)" % (a_fast*a_slow))
    print("    geometric mean    = %5.3f   (1.0 => balanced at shock-absorber point)" % gmean)
    print("    arithmetic mean   = %5.3f" % amean)

if __name__ == "__main__": main()

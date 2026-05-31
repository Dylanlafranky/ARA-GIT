"""
The nervous system itself is a "3": a FAST clock + a SLOW tick (Dylan, 2026-05-30).
====================================================================================
Earlier we treated the hub as one tank fed by BP-fast and breath-slow. Dylan's structural
correction: the autonomic nervous system is not a single tank -- it is a whole resonance-
locked system (a "3" by linkage-sum theory). It has TWO internal nodes:
   FAST clock  <- fed by BREATH (the quick respiratory drive into the NS)
   SLOW state  <- fed by the BRAIN / EEG (the slow cortical-set tonic level)

So reconstruct the NS hub from ITS OWN feeders (breath + brain), not from BP. BP is the
heart's own downstream output (heart->BP lock), so it is NOT a clean feeder into the NS.

   fast NS node  = breath FAST band            (forward spin, passed through)
   slow NS node  = EEG   SLOW band, tanked      (leaky integral, leak = 1/phi)

Then predict a FUTURE heart beat from this reconstructed 2-node NS hub, and compare to:
   base (RR only), the old BP-fast + breath-slow hub, and raw breath/EEG feeders.

STRICT-CAUSAL: trailing past-only smoother; z + integrator from TRAIN only; future-beat
target; last 40% held out; correlation leads. slp01a, real. Descriptive.
"""
import numpy as np
import heart_info_exchange_R as H
import heart_fast_forwardspin as F
from heart_reconstruct_hub import leaky_integrate, score, NLAG, TRAIN_FRAC, LEAK, HS, PHI

def main():
    rr, fe = H.per_beat_series()
    bp_fast,   _        = F.split_bands(fe["BP"])
    resp_fast, resp_slow = F.split_bands(fe["Resp"])
    eeg_fast,  eeg_slow  = F.split_bands(fe["EEG"])
    n = len(rr); split = NLAG + int((n - NLAG) * TRAIN_FRAC)

    def ztrain(x):
        m = x[:split].mean(); s = x[:split].std() or 1.0
        return (x - m) / s

    # NEW: the NS as its own 3 -- fast clock fed by breath, slow tick fed by brain/EEG
    ns_fast = resp_fast                                  # breath -> fast NS clock (pass)
    ns_slow_tick = leaky_integrate(ztrain(eeg_slow))     # brain -> slow NS state (tank)

    # OLD hub for comparison: BP-fast pass + breath-slow tank
    old_fast = bp_fast
    old_slow_tank = leaky_integrate(ztrain(resp_slow))

    configs = {
        "base (RR only)":     [],
        "+raw breath+brain":  [resp_fast, eeg_slow],
        "+OLD hub(BP,resp)":  [old_fast, old_slow_tank],
        "+NS-3 (breath,brain)": [ns_fast, ns_slow_tick],
        "+NS-3 + BP fast":    [ns_fast, ns_slow_tick, bp_fast],
    }
    res = {nm: {h: score(rr, f, h) for h in HS} for nm, f in configs.items()}

    print("heart beats: %d   leak = 1/phi = %.3f   (train %d%%, held out rest)\n"
          % (n, LEAK, int(TRAIN_FRAC * 100)))
    names = list(configs)
    print("HELD-OUT CORRELATION (RR forecast)\n")
    print("h(beat)  " + "".join("%20s" % nm for nm in names))
    for h in HS:
        row = "%7d " % h
        for nm in names:
            v = res[nm][h]
            row += ("   %+7.3f          " % v) if v == v else ("   %14s   " % "--")
        print(row)

    b = res["base (RR only)"]
    print("\nLIFT over base:")
    print("   h   raw b+br      OLD hub     NS-3(b+br)   NS-3 + BP")
    for h in HS:
        print("%4d  %+10.3f %+12.3f %+12.3f %+12.3f" % (
            h, res["+raw breath+brain"][h]-b[h], res["+OLD hub(BP,resp)"][h]-b[h],
            res["+NS-3 (breath,brain)"][h]-b[h], res["+NS-3 + BP fast"][h]-b[h]))

if __name__ == "__main__": main()

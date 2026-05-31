"""
Hunt the FAST forward-spin donor for the heart (split each channel into fast vs slow).
=====================================================================================
Dylan, 2026-05-30: the breath went NEGATIVE in the stitch not because it's redundant -- it's
the COUNTERSPIN. Breath is the slow accumulation-release CLOCK. We're hunting the fast FORWARD
spin. A counterspin partner reads negative against the forward thing we want.

So split every feeder per-beat into two bands:
   SLOW band = low-pass envelope          = the accumulation-release clock = counterspin
   FAST band = channel minus its envelope = the quick forward-spin correction
Then add each band, on its own, to the base RR forecast.

Prediction (Dylan): the FAST (forward-spin) band lifts the forecast; the SLOW (counterspin
clock) band hurts / reads negative. The real donor is the fast forward spin, not the slow clock.

STRICTLY CAUSAL: feeder bands are causal (the smoother is past-only/trailing); standardize on
TRAIN only; target = a FUTURE RR beat; last 40% held out; correlation leads.
Data: slp01a (PhysioNet slpdb, 250 Hz). Real. Descriptive.

Usage: python3 heart_fast_forwardspin.py
"""
import numpy as np
import heart_info_exchange_R as H
import heart_combined_horizon_feeder as C   # reuse design/run_config/NLAG/TRAIN_FRAC

SLOW_WIN = 8   # beats; trailing window that defines the slow accumulation-release clock

def trailing_slow(x, w):
    """Past-only (trailing) moving average -> causal slow envelope. No future leak."""
    out = np.empty_like(x, dtype=float)
    for i in range(len(x)):
        a = max(0, i - w + 1)
        out[i] = x[a:i+1].mean()
    return out

def split_bands(x, w=SLOW_WIN):
    slow = trailing_slow(x, w)
    fast = x - slow
    return fast, slow

def main():
    rr, fe = H.per_beat_series()
    resp = fe["Resp"]; bp = fe["BP"]
    resp_fast, resp_slow = split_bands(resp)
    bp_fast,   bp_slow   = split_bands(bp)
    print(f"heart beats: {len(rr)}   slow window {SLOW_WIN} beats (trailing/causal)\n")

    configs = {
        "base (RR only)":  [],
        "+breath FAST":    [resp_fast],
        "+breath SLOW":    [resp_slow],
        "+BP FAST":        [bp_fast],
        "+BP SLOW":        [bp_slow],
    }
    HS = (1, 2, 3, 5, 8)
    res = {nm: {h: C.run_config(rr, f, h) for h in HS} for nm, f in configs.items()}

    names = list(configs)
    print("HELD-OUT CORRELATION (RR forecast) -- FAST = forward spin, SLOW = counterspin clock\n")
    print(f"{'h(beat)':>7}  " + "".join(f"{nm:>15}" for nm in names))
    for h in HS:
        row = f"{h:>7} "
        for nm in names:
            v = res[nm][h]
            row += f"   {v:>+7.3f}    " if v == v else f"   {'--':>8}   "
        print(row)

    b = res["base (RR only)"]
    def d(nm, h): return res[nm][h] - b[h]
    print("\nLIFT over base (positive = helps, negative = counterspin signature):")
    print(f"{'h':>4}  {'breath FAST':>12} {'breath SLOW':>12} {'BP FAST':>12} {'BP SLOW':>12}")
    for h in HS:
        print(f"{h:>4}  {d('+breath FAST',h):>+12.3f} {d('+breath SLOW',h):>+12.3f} "
              f"{d('+BP FAST',h):>+12.3f} {d('+BP SLOW',h):>+12.3f}")
    print("\nDylan's prediction: FAST bands lift (forward spin), SLOW bands go negative (counterspin).")
    print("Strict-causal: trailing past-only smoother, train-only standardize, held-out test.")

if __name__ == "__main__": main()

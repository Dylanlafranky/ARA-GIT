# TEST 5 — Tumbling pendulum / separatrix crossing — RESULT (3 Jul 2026)

**Target:** FIVE_BEST_TARGETS #5, the framework's oldest untested landmark: the
0/2 poles and the 1.0 ridge placed on the libration/rotation boundary, with the
separatrix as exact mathematical referee.
**Instrument:** simulation of the REAL Kaheman et al. double pendulum (Zenodo
10.5281/zenodo.6633719) using the archive's own identified parameters and its
own published EOM, ported verbatim. Simulation pre-registered as legitimate for
this target only (exact known physics). Script: `test5_tumbling_separatrix.py`
(self-contained, seed 42, out-of-the-box rule compliant).

## Validation gate (passed)
Simulated free swing from the real run's initial state: dominant periods match
the real device to 0.0% (arm 1) and 2.9% (arm 2). Damping angles same order
(sim reads cleaner; the kit estimator measures decoherence and real data
carries camera noise). Single-pendulum control reproduces the textbook
separatrix signature exactly: rotation periods 0.538 -> 0.572 -> 0.610 ->
0.668 -> 0.758 -> 1.222 s into the crossing, stall peaking at the transition.

## The retraction arc (kept for honesty)
First-pass run returned strong NULLS on P1/P2. Both were instrument artifacts,
caught by controls BEFORE re-scoring: (1) the archive's convention places
theta = 0 at the INVERTED point (proved by release test + real data resting at
-3.1404 rad) — the first detector measured everything upside-down; (2) wrap
discontinuities at +-pi were counted as bottom passes, shredding rotation turns
(caught by the single-pendulum control returning zero rotations at an energy
that must rotate). First-pass numbers RETRACTED as instrument error. The
protocol's verify-before-adjudicate step is the only reason these did not
become a false NOT SUPPORTED.

## Registered results (24 runs x 90 s, 818 transition events)
- **P1 critical slowing at the ridge: SUPPORTED.** Transition cycles run
  +86 ms over their +-5-neighbour median (a 556 ms typical cycle, ~+15%);
  63% of events positive; Wilcoxon one-sided p = 6.3e-21.
- **P2 pole stall: SUPPORTED.** Excess time near the inverted configuration
  in transition cycles: +0.051 median, 64% positive, p = 3.2e-32.
- **P3 slow approach (as registered, final captures only): INCONCLUSIVE —
  UNPOWERED (n = 1).** The real device's friction is tiny; 90 s runs rarely
  settle. A longer-horizon rerun (T ~ 400 s) is the queued fix.
- **P3 exploratory (all captures, n = 133; open deviation from registration):
  NULL — the rival wins.** Final rotation turn is the slowest of the last
  three in only 26% of captures (chance 33%); strictly monotone slowing in
  15% (chance ~17%). Approach to capture is ballistic, not adiabatic.

## The differentiated finding (the real product)
The ridge keeps its LOCAL geometry under coupling: the crossing cycle itself
still dilates (P1) and still hugs the saddle (P2) — attenuated (~+15% vs
~+100% uncoupled) but decisively present at n = 818. What coupling destroys is
the APPROACH: the uncoupled pendulum spirals gradually into its separatrix;
the coupled one is DELIVERED to it by chaotic energy exchange and crosses
ballistically. In framework vocabulary: time dilation ON the ridge survives;
the adiabatic handover TO the ridge does not. The 0/2 pole story is neither
confirmed decoration nor full survivor — it is a local property of the
boundary, not a property of the road.

## Fences
- Simulation of an identified real device, registered as fair for THIS target
  only; no claim extends to targets where ground truth is unknown.
- P3-as-registered stays open until the long-horizon rerun.
- The IBM double-pendulum camera dataset (the ideal real-data version) is
  gone with DAX's retirement — no public mirror, not archived. If a copy
  surfaces, the analysis runs unchanged on real tumbling.

## Addendum (3 Jul, from the visualization pass)

Per-offset superposed-epoch analysis sharpened the finding: the dilation lives
in the TRANSITION PAIR AS A WHOLE — the spike alternates between the last
rotation turn and the first libration swing (per-offset medians stay ~1.0-1.02
while the pair-mean median is 1.145), and the road before the crossing is flat
(0.93-1.01 at offsets -5..-1). Contrast: the uncoupled control's road ramps
0.94 -> 1.51 -> 2.44 -> 3.11 into the crossing. The flat-road/local-spike
contrast IS the headline result, now stated explicitly. Histogram: 63% of 818
crossing pairs slower than their road; heavy right tail to ~2.5x; 37% at road
speed or faster (the ballistic minority).

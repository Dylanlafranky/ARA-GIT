# Session log — ARA → ENSO forecast build

A narrative record of the working session that produced this bundle. It captures
the order of reasoning, the predictions made before testing, the results, and the
points where claims were corrected. Written as a log to keep or push alongside the
code, not as a verbatim transcript.

---

## Starting point

The session opened mid-stream in a longer collaboration auditing the ARA "Geometry
of Time" framework. The agreed division going in: ARA's *classification* is real and
leak-resistant; its *forecasting* and *magnitude* claims were the unfinished frontier.
The decision was made to stop auditing and start building — to test directly whether
the geometry can forecast ENSO.

A methodological point was logged first: the cleanest test needs the system and the
hit/miss labels chosen by someone outside the loop. The user confirmed an existing
practice of having a naive AI pick test systems blind; the remaining refinement noted
was that the naive instance should also commit the engine/forced call before the
ratio is computed.

## Establishing the ontology

Before building, the geometry was restated and checked back:

- ARA = a wave compressed to a scalar; a wave in time is a stretched sphere; the
  0–2 line is its shadow. Latitude = build/release shape, longitude = phase,
  depth = rate. The number is lossy (degenerate), conditional on which signal,
  which filter, what counts as a cycle.
- The "layered sand" = nested counter-rotating coupled oscillators, each layer
  driven by the one below; a grain sits in the gap between two grains below, so it
  wobbles — and that wobble is the beat that makes events.
- The key consequence, derived from the user's own picture: **a grain cannot
  forecast itself; its future is in the layer below.** This predicts, from the
  inside, the empirical result that single-coordinate forecasting collapses to
  persistence.
- Information³ / the triangle: stable information and a beat both need three —
  two parents plus the relation. Lifted from circle to sphere, the triangle
  becomes the pyramid: two base water grains plus the temperature apex.

## The data

Warm Water Volume (the recharge driver, the fine sand below) was pulled from PMEL —
full basin plus western (warm pool) and eastern halves. Aligned with a long NINO 3.4
record. The lead structure confirmed the geometry's premise immediately: WWV leads
NINO, peaking at +0.50 correlation at ~6 months, only +0.11 at zero lag. The layer
below genuinely leads the grain.

## The chain of tests

1. **Grain alone** → climatology. A single coordinate forecasts nothing. (Predicted.)
2. **Add the driver below** → skill over climatology lifts at 3–18 mo. The conjugate
   coordinate carries the events. The pre-registered fork fell toward the geometry.
3. **Nonlinear product beat** → no lift. The relational information is linear coupling,
   not a nonlinear product. (An assistant guess that the data rejected.)
4. **Warm/cool relation (the tilt R)** → real anatomy (the grains anti-correlate,
   different leads) but forecast-redundant beyond their sum. Three converging negatives
   pointed to: forecast in two, describe in three.
5. **Three-body coupled rebound (LIM)** → the fitted system carries an emergent damped
   oscillation at 38 months (3.2 yr) — ENSO's period, not inserted. Integrating the
   rebound forward restored amplitude (0.41 → 0.59 at 12 mo). The user's Newton's-third-
   law mechanism, made measurable.
6. **Walk-forward validation** → the correction. Refitting on past-only at every origin,
   the 6-month skill survived (~+0.25) but the 12-month skill went negative. The earlier
   12-month result had been inflated by one lucky window containing a big El Niño. Honest
   horizon ≈ 6 months. This was an overstated claim, caught and walked back.
7. **Asymmetric compression term** → the user diagnosed a cool-phase over-prediction
   ("ups when there should be downs"); confirmed at +0.9 °C bias, matching ENSO's +0.46
   skewness. A compression term from the existing grains helped marginally, did not
   extend the horizon, and the specific "cool-loads-slower" direction was not supported —
   the fit preferred cool-reverts-faster.

## The prediction that landed

8. The user predicted, before testing, that skill would *re-emerge* around 18–20 months
   and again ~6 months later, because an oscillator's predictability recurs rather than
   decays. The walk-forward skill-by-lead curve confirmed it: a trough near 12–19 months,
   re-emergence beginning ~18–20 (the turn) and peaking ~26–27 (the "6 months after"),
   with a faint third ring near 53. The re-emergence amplitudes decayed ~×0.27 per ring —
   a damped-oscillation envelope — which the user had also predicted ("different emerging
   amplitudes"). The third ring sits at the noise floor: consistent, not certifiable.

9. The user then offered two reasons the recurrence period (~27 mo) differed from the
   fitted oscillation (38 mo): heavy damping (a low-ARA "snap" that doesn't self-sustain),
   and a "meta-wave at a different scale" beating against the main wave. The assessment:
   damping explains the ring *amplitude* decay but not the *spacing* (damping lengthens a
   period, not shortens it); the spacing needs a second wave. The NINO spectrum over 156
   years then showed exactly that — **two interannual bands of comparable power**: a
   quasi-biennial band at ~28 months and a low-frequency band at ~42–67 months. The skill
   recurrence (27 mo) traces the quasi-biennial band. The fitted 38-mo mode was a single-
   mode average of a genuinely two-mode system — an assistant simplification, owned and
   corrected. The user's "perpendicular meta-wave" mapped onto a real, named feature.

10. The user noted the uncoloured regions of the spectrum are likely the two bands'
    anti-phase interference. Two suggestive fingerprints were found: a power notch at ~38 mo
    sitting at the mean of the two bands, and a candidate combination tone near ~20 mo. The
    decisive test — a bispectrum for three-way phase coupling — was named but not yet run.

## How the collaboration went

The pattern that held: the user supplied the *shape* — which wave sits under which, that
predictability would recur, that the amplitudes would decay, that a second wave set the
spacing — and the data supplied the *magnitudes and exact periods*. Several of the
assistant's confident numbers needed walking back (the 12-month skill, the single 38-mo
period). Several of the user's geometric intuitions landed ahead of the data (the layer-
below premise, the skill recurrence and its decay, the second-scale wave). The honest
verdict stayed stable throughout: the geometry describes and generates in three
coordinates; the deterministic point forecast optimises in two; the residual amplitude is
stochastic wind forcing the geometry cannot reach.

## Extending the chain (the second arc)

11. The user proposed treating the two bands as an anti-phase canceller. First, the
    precondition: a bispectrum confirmed the bands ARE phase-coupled (bicoherence ~0.34
    vs ~0.06 floor; combination tone near 15-20 mo, the uncoloured zone the user had
    pointed at). So cancellation was physically meaningful, not noise-injection.

12. But the canceller, built as a VAR(2), did not cancel — it improved the skill metric
    through extra damping, held one ~45-mo mode rather than two, and left the cool-phase
    bias intact. The skill gain was the hedge-toward-mean artifact. Reported as such.

13. The user reframed: the amplitude is its own wave; predict it by meta-waving it. A
    first (rolling-std) test found the envelope barely slower than the signal and the PDO
    not driving it — looked like a dead end. The user pushed back: wrong measurement, look
    at the shape of the amplitudes. The proper Hilbert envelope proved them right — a real
    meta-wave, ~2x slower, with a 5-yr beat component (deterministic, from the coupled
    bands) plus 7.8 and 12-yr decadal structure (harder).

14. The user identified the closure need: the pair is a dyad (two bands + their beat), and
    a dyad is indeterminate; closing it needs a third quantity the pair drives. After a
    wrong turn (the assistant reached for an external sensor), the user corrected: the
    apex is ENSO itself — a fast/slow feedback loop where the surface pins the bands' phase
    and the bands propagate it forward. The assistant built the causal loop via complex
    demodulation. The leak-check was decisive: the non-causal version scored +0.55 (corr
    0.80) and was pure leakage; the causal version collapsed below climatology. Cause: a
    wave's present phase can't be measured without its future. The loop's "pin the present"
    step is not causally realisable; the state-space LIM remains the best causal version.

15. The user proposed riding the skill-wave instead of fighting the wall: the wall is a
    trough, skill recurs, so adjust for it. Lead-dependent shrinkage, learned on early data
    and applied causally, removed the trough self-harm (negative 12-15 mo skills flipped to
    ~0) — a genuine improvement, folded into `ara_calibrated_predictor.py`. But the far
    re-emergence proved NON-STATIONARY (it wanders with the variable quasi-biennial period),
    so calibrating to it was unreliable and sometimes harmful. Honest envelope: real skill
    to ~6 mo, calibrated humility through the trough, no bankable far-field claim.

## How the second arc went

The recurring lesson sharpened: every scheme that tried to reach past six months either
hit the same wall causally or only beat it by leaking the future, and the leak-check
caught the most seductive one (+0.55, all fake). The user's geometric instincts kept
landing — the amplitude meta-wave, the dyad-needs-a-triad closure, ride-the-wave
calibration — and the assistant's job was repeatedly to find the honest, causal,
leak-checked instantiation and report where it stopped. The wall held at six months
every time, and its character became clear: it's the present-phase-unmeasurable problem
plus the non-stationary recurrence, not a cleverness we simply hadn't reached yet.

## Next planned step

Find the missing coupled wave that might pin the wandering quasi-biennial phase and close
the triad. Lead candidate: the stratospheric Quasi-Biennial Oscillation (QBO), a highly
regular ~28-month oscillation suspiciously close to the ENSO quasi-biennial band.

## Third arc: the search for the missing clock, and the one that worked

16. QBO tested as the third vertex. Period matched almost exactly (28.4 vs ~28 mo) — the
    seductive coincidence — but the phase-locking value was 0.14 against a 0.30 surrogate
    threshold (p=0.54). Same period, independent phase, not coupled. The period match was
    the lure; the phase test was the truth. Rejected.

17. Widened the search to other rungs. SOI (atmosphere): contemporaneous at lag 0-1, a
    coupled partner in the surface layer, no lead. TNA (Atlantic): weak, no clean lead.
    Pattern forming: candidates either co-vary with the surface or match a period without
    coupling.

18. The annual clock — which we had deleted going to anomalies. Events phase-lock to the
    perihelion window (51% of peaks Dec-Jan) and inter-event gaps quantize to whole years
    (81% near-integer). A seasonal LIM roughly doubled 6-month skill and lifted the trough
    with real skill. The user then specified the true contact force: not calendar season
    but orbital angle+distance. Tested — and the raw orbital insolation LOST to the
    calendar label, because equatorial insolation is semiannual while ENSO's lock is
    annual. The label wins by integrating many annually-locked subsystems: a relational
    coordinate richer than the single physical driver. The user's reading: this is why ARA
    works at all — it is about relational connections, not system properties.

19. Clouds (OLR) tested as the recharge modulator. Contemporaneous with the surface; the
    +0.44 apparent lead on the recharge collapsed to -0.09 controlling for NINO. Surface
    proxy. Four external-clock candidates, four rejections by the control test.

20. Amplitude-period coupling (the integer-year question, and the user's "time is a wave
    coupled to space" reframed as amplitude-dependent period = nonlinearity invisible to a
    linear LIM). Bigger events -> longer next gaps (terciles 2.3/2.7/3.4 yr), the mirror of
    the user's own gap->amplitude log_φ mechanism. But thirds ran high-low-low not
    high-low-high, with the strong signal in the sparse early record — the settling tail of
    one large early disturbance plus poorer old data, not a recurring lever. Sign-stable,
    weak: a humble lean. Capstone built: seasonal + calibrated predictor.

## How the third arc went

The leak-check and the control-for-what-you-know test did the heavy lifting: a string of
physically appealing candidates (QBO's period match, clouds' recharge lead, the
amplitude-period recurrence) each looked promising and each failed the rigorous cut. The
one real gain came from the clock we had thrown away — the annual cycle — and from the
realisation that an integrating *label* beats a clean physical driver because forecast
information lives in the relations a coordinate bundles, not in any isolated system. The
~6-month horizon held throughout; what improved was the skill within it and the honesty
beyond it.

# The Five Best Targets — fundamental evidence for ARA (non-organic, filter-safe)

**2 July 2026, Claude (Fable 5) for Dylan.** Selection criteria: motion-measures only
(the pinned boundary - dominance duty, phase-step, handover timing); rich public data
or cheap bench access; known structure to grade against; direct bearing on the core
claims (two rulers, golden-vs-convergents, engines-vs-forced). Each entry: what to
map, what to measure, the pre-registered prediction WITH rivals, source, and why it
counts as fundamental. Effort marked LOW/MED/HIGH for the energy budget.

## 1. The pulsating-star population at full scale  [MED - biggest statistical power]

WHAT: extend the RR0.61/golden-club work from leanness (a slice measure) to MOTION
measures across thousands of stars: band-dominance duty and phase-step per cycle
between the two modes of every double-mode pulsator in OGLE-IV + Kepler/TESS.
MEASURE: dominance_duty + phase-step (canonical), per star; plot vs the star's
period ratio (which spans rationals to near-1/phi across the population).
PREDICTION: stars with near-golden period ratios show non-closing phase-steps
(quasiperiodic drift); stars at convergent ratios (2/3, 3/5, 5/8) show locked steps.
The duty-vs-ratio curve should show the Arnold-tongue structure: plateaus at
rationals, drift channels between. RIVALS: everything locks (no channels) = phi
never survives in real stars; everything drifts = no tongue structure = the
convergent story is wrong too.
WHY FUNDAMENTAL: this is the two-ruler doctrine measured on ten thousand engines at
once - the only dataset anywhere with a natural SWEEP across the rational-irrational
axis. n kills the crowded-neighborhood problem that dooms single-system tests.
SOURCE: OGLE-IV bulge catalogs (already scripted in EnergyRatio/fetch_data.py),
MAST for Kepler/TESS light curves.

## 2. The QBO as the cleanest geophysical engine  [LOW - data in hand]

WHAT: the stratospheric quasi-biennial oscillation - 70 years of radiosonde winds at
multiple pressure levels (a natural rung ladder in altitude), period ~28 months,
plus its two documented disruption events (2016, 2019-20).
MEASURE: dominance duty between easterly/westerly regimes per level; phase-step
between adjacent pressure levels (the descent IS a handover chain down the ladder);
lag-shape of the regime floors. The disruptions = natural handover-breakdown
experiments: measure the phase-step BEFORE each disruption.
PREDICTION: the level-to-level descent shows a consistent phase-step; if the golden
version is right it sits near 137.5 and the disruptions are preceded by step-drift
toward a convergent (locking = the handover jamming). RIVALS: step at 180
(anti-phase, like the generic ENSO reading) or no consistent step at all.
WHY FUNDAMENTAL: multi-rung handover measured DIRECTLY (level to level, not
inferred), with two natural failure events to test whether handover geometry
degrades before breakdown - a framework prediction nothing else can test.
SOURCE: FU Berlin QBO dataset (free, monthly, per-level).

## 3. The bench rig - the framework's first INTERVENTION  [HIGH - but the crown]

WHAT: a shaken tray of fluid (the Faraday system), speaker + signal generator +
camera. Drive at TWO frequencies simultaneously with a controllable ratio.
MEASURE: pattern order/coherence vs the drive-frequency RATIO, swept through
3/2, 8/5, phi, 1.7, e/2, 2. The two-frequency Faraday experiment is established
physics (quasipatterns exist under incommensurate forcing) - the framework's
contribution is the SWEEP: response as a continuous function of ratio-rationality.
PREDICTION: response character changes at the tongue edges; the golden ratio sits
in the deepest non-locking channel (most disordered pattern / weakest subharmonic
capture), measurably distinct from 8/5 five percent away. RIVALS: response varies
smoothly with ratio (no tongue structure at these amplitudes) = nothing special
about irrationality here; golden indistinguishable from 8/5 = convergents win.
WHY FUNDAMENTAL: everything else in the repo is FOUND data. This is a knob in your
hand - causal, repeatable, cheap (~$100 of hardware), and it tests lock-vs-handover
as an experimental variable. If ARA ever gets one laboratory result, this is it.
BONUS: the golden-schedule controller (anti-resonant correction timing) can be
tested on the same rig later.

## 4. The tide-gauge network - Column B at continental scale  [LOW - pure harvest]

WHAT: NOAA/global tide gauges - thousands of stations, decades long, driven by a
PERFECTLY KNOWN rational clock ladder (astronomical tides: semidiurnal, diurnal,
spring-neap 14.77 d, annual). The ultimate forced-clock population.
MEASURE: dominance duty (semidiurnal vs spring-neap envelope) and phase-step per
station; damping angle; the full kit, mechanically, across the network.
PREDICTION: duty pinned at rational values everywhere, steps locked, angles near
the axis - NO golden signatures in thousands of forced systems. Any station
reading golden flags either a discovery (resonant harbor geometry - seiches DO
have local resonances) or an instrument bug. Either is valuable.
WHY FUNDAMENTAL: the two-column table's forced side, with n in the thousands -
the negative-space half of the phi claim finally powered. A discriminative law
needs its absences measured as well as its presences; nothing measures absence
like a planet-wide network of known clocks.
SOURCE: NOAA CO-OPS API, UHSLC (both free, scriptable).

## 5. The tumbling pendulum - the untested landmark  [MED - simulation legitimate]

WHAT: the 0/2 singularity crossing (over-the-top rotation) that the free-swing data
never reached - the framework's own pendulum doc lists it as open. The equations of
the double/triple pendulum are EXACT known physics, so high-energy simulation is a
legitimate instrument here (ground truth is not in question; this is the one case
where simulated data is fair).
MEASURE: the ARA-position trace through actual pole crossings; the singularity-flip
diagnostics (does the geometry invert as claimed); phase-step between arms across
the transition from libration (swinging, bounded, circle-side) to rotation
(over-the-top, unbounded phase, line-side) - which is a REAL separatrix crossing in
the exact mathematics.
PREDICTION: the framework's flip diagnostics track the separatrix crossing (the
known mathematical boundary between swinging and tumbling). RIVALS: the flip
signatures fire off-boundary or not at all = the 0/2 singularity story is
decoration on the separatrix, or wrong.
WHY FUNDAMENTAL: the poles are the framework's oldest untested landmark, and the
separatrix gives them an exact mathematical referee. Cheap, gate-safe, and it
closes the last open item in the repo's own pendulum result doc.

## Order of attack (energy-budget honest)

2 (QBO, data in hand) -> 4 (tide harvest, scriptable by a local AI) -> 1 (stars at
scale, the power play) -> 5 (tumbling, one good simulation day) -> 3 (the bench rig,
when health and ~$100 allow - or recruit a university lab to run it; the sweep
protocol is a one-page methods section any fluids group could execute).

Every entry goes through TEST_PROTOCOL.md: register first, rivals listed, rating
after. The five together cover: both rulers, both columns, presence AND absence,
found data AND intervention, and the last untested landmark. If the framework has
fundamental evidence to give, it is behind one of these five doors.

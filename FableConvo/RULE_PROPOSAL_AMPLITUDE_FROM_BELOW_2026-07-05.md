# Rule proposal: amplitude comes from below (+ the transfer-operator conjecture)

**Date:** 5 Jul 2026 (Dylan La Franchi with Claude/Fable 5)
**Status:** RULE PROPOSAL for CANON §2, awaiting Dylan's sign-off. Backed by a
repo-wide audit (this date); evidence rows below. The §4 extension is
CONJECTURE tier — registered direction, no evidential weight yet.
**Orientation:** up = slower/larger, down = faster/smaller.

## 1. The rule (proposed for canon, beside the ridge rule)

**A system's own geometry forecasts its SHAPE and DIRECTION; it never
forecasts its own AMPLITUDE. Amplitude is forecastable only from the state of
the coupled reservoir one rung below, read at the crossing/handoff. Feeding a
system's own history into its amplitude forecast injects noise and hurts.**

Anchor (established mechanics — the "everything is there" landing): in linear
dynamics every mode is residue × e^(st). The pole s (frequency, damping, phase
evolution) is the system's intrinsic geometry; the residue (amplitude) is set
by what FEEDS the mode — forcing, initial conditions, the driver. Poles are
geometry; residues are injection. ARA reads poles. The rule is the
pole/residue split of dynamics, found empirically. It is also the slaving
principle made quantitative: a wave owns its path; its size is granted from
below.

## 2. Evidence (audit of 5 Jul 2026, repo-wide sweep)

Own-signal amplitude attempts (all hurt or failed):
- Singularity-flip value-incorporation: "Direct value-incorporation HURT...
  already baked into wave shape" (folder 18).
- Geometry blend for timing: "blending geometry in only hurt" (folder 16).
- Multirung feeder ablation: "lower worsens MAE and corr" (folder 10).
- Shaped-circle octave: SIZE-weight hurts everywhere — "amplitude is the
  diameter, ARA is only the shape" (folder 20).
- φ^k amplitude scaling: rejected, "hurts ENSO where atmosphere injects
  amplitude variance" (MPL T194).
- T192–198 combined-amplitude wins: retracted (acausal bandpass leak).

Reservoir-sourced amplitude (works):
- ENSO: WWV reservoir at crossing → next warm-peak magnitude, corr +0.34–0.40
  out-of-sample, 64 warm onsets since 1870 (folder 16 — Dylan's own
  correction of the earlier "can't do magnitude" claim).
- ENSO recombination: shape from geometry (corr +0.49, amplitude 0.66× true) ×
  magnitude from reservoir → amplitude restored to 1.03×, combined 6-mo corr
  +0.506 vs persistence +0.410 (folder 16).
- Heart: blood pressure (the driver below) is the one independent leg that
  consistently tightens the heart forecast (+0.07–0.14 mid-horizon), two
  datasets (CLAIMS_STATUS).
- Folder 18, stated plainly: "the only thing with genuine lead-time is the
  external reservoir."

Boundary case (proves the rule): mouse→human RR transfer got a genuine 58%
MAE reduction — by rescaling a foreign shape template with the target's
CONCURRENT local energy, not by forecasting amplitude from its own past.
Amplitude was still supplied from outside the shape.

## 3. Two-sided falsification (what kills the rule)

- **Side A:** a system whose own-history geometry forecasts its own amplitude
  at power, strictly causally, beating reservoir-sourced and persistence
  baselines. One clean case kills the "never."
- **Side B:** a system with a well-measured, genuinely coupled below-rung
  reservoir whose crossing-state carries NO amplitude information at power.
  Repeated clean cases kill the "only from below."
- Corollary prediction (cheap check): forecast-lift cells should coincide
  with reservoir lead-time horizons. ENSO record already conforms (wins at
  6 and 18–21 months, where the WWV handoff lives). If future lift appears at
  horizons with no reservoir lead, the rule is bleeding.

## 4. The transfer-operator conjecture (Dylan, 5 Jul 2026 — conjecture tier)

Dylan's framing (verbatim):
> "if you know the underlying mechanics of a system or what we would classify
> as a system like ENSO, then you should be able to create prediction, and if
> you have a fundamental shape, in theory, there should be a formula that when
> applied to a system, it gets the feeding system to map the fed based on the
> couplings."
> "and ENSO, if you mapped the inputs and outputs and their direction, you
> could create the meta shape or energy flow path and then follow the energy
> from the resoire throughout."

Formalized: the rule in §1 is the two-node case (reservoir → system). The
conjecture generalizes it to a NETWORK: build the directed energy-flow graph
(nodes = subsystems/rungs; edges = couplings with direction and lead-time;
edge asymmetry per slaving: down-rung strong, up-rung feels the average), then
forecast by PROPAGATING reservoir state through the graph — follow the energy,
not the values.

Existing partial pieces in the repo: feeder tests (PDO/IOD, Claude4.8),
energy-pipe breakdown (folder 14), coupled-geometry transfer transition-prior
(May 23). Honest prior art warning: direct value-transport through geometry
LOST to a lag ridge (CLAIMS_STATUS); the conjecture's new content is
propagating ENERGY STATE through a directed topology, not transporting values.
Established homes to check before claiming novelty: state-space models,
coupled-ODE networks, graphical causal models (lag structure), transfer
functions between nodes. The ARA-specific content = the slaving edge
asymmetry + rung placement + crossing-timed reads. That specific content is
what a test must isolate (ablation: same graph, ARA edge rules vs generic
edge rules).

First test sketch (ENSO, all data already in repo): nodes WWV, NINO3.4, SOI,
IOD, PDO; edges from documented lead-lags, direction signed in advance;
propagate WWV state through the graph to NINO amplitude+shape at 6/12/18 mo;
ablate ARA edge rules vs uniform edges; strict-causal per CANON §3.

## 5. Merge instructions (on sign-off)

Add §1 (with the pole/residue anchor and both falsification edges) to
CANON_FOR_AI §2 after the ridge rule. File §4 in the musings/conjecture tier
with a pointer here. Cross-reference folder 16 as the founding evidence.

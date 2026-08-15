# T392 - spin anti-phase child at the muon-decay handover

**Date:** 15 August 2026  
**Status:** supported at the population crosswalk ceiling  
**Frozen protocol:** `T392_SPIN_CHILD_NEUTRAL_HANDOVER_PROTOCOL_2026-08-15.md`

## Question

T391 recovered the muon population's spin anti-phase in the raw detector
field. T392 asked whether the next measured child beneath that parent relation
is the charged-daughter versus joint-neutral energy allocation at decay.

The test did not count spin turns and did not ask when an individual muon
would decay. It digitised the published TWIST polarized-muon forward/backward
asymmetry and its data-minus-fit residuals, then located the unique change of
direction in the daughter relation.

## Result

The reconstructed daughter-direction asymmetry changed sign at

\[
p_e=25.8913\ {\rm MeV}/c,
\qquad
x_e=\frac{2E_e}{m_\mu}=0.49019.
\]

The 20,000-replicate bootstrap interval was

\[
0.48612\le x_e\le0.49446.
\]

All five frozen gates passed:

- the low- and high-allocation directions had opposite signs;
- exactly one local handover was recovered;
- the root lay inside the frozen `0.45-0.55` coarse-pair band;
- 100% of bootstrap roots remained inside that band;
- the root was much closer to `0.5` than to the wrong-landmark controls
  `0.25` or `0.75`.

## ARA reading

For a stopped parent, define the charged energy coordinate

\[
x_e=\frac{2E_e}{m_\mu}.
\]

Only after locating the measured reversal, form the joint-neutral complement

\[
x_N=2-x_e=1.50981.
\]

The result is therefore close to the ARA coarse pair

\[
(x_e,x_N)\approx(0.5,1.5).
\]

The important empirical content is the location of the directional sign
reversal. The identity `x_e+x_N=2` is forced energy bookkeeping and is not a
second empirical finding.

Within the current ARA map, this is consistent with an energy-allocation child
beneath the T391 population spin anti-phase. The charged daughter changes its
preferred spin-relative direction near the child-half allocation; the joint
neutral packet occupies the complementary side of the same TE-ARA account.

## Established-physics crosswalk

TWIST measured the momentum and emission angle of positrons from polarized
muon decay. The sign change near half the endpoint is a known feature of the
polarized Michel spectrum. T392 therefore supplies a clean data-backed ARA
crosswalk and rung assignment; it is not a newly discovered muon-decay law.

Official sources:

- `https://twist.triumf.ca/~e614/experiment.html`
- `https://twist.triumf.ca/~e614/pubs/PmuXi_2006_PRD.pdf`

## Claim boundary

T392 does not:

- predict the instant an individual muon decays;
- observe either neutrino separately;
- show that spin triggers decay;
- revive the failed T390 7.5-turn release claim;
- turn the forced complement into independent evidence.

The next stronger test requires event-linked polarized-muon data containing
the parent spin state and the charged daughter's energy and direction, plus an
independent neutral-sensitive or missing-momentum measurement. No public
event-level TWIST archive was located during T392.

## Reproduction

- Analysis: `t392_spin_child_neutral_handover.py`
- Independent audit: `validate_t392_spin_child_neutral_handover.py`
- Results: `T392_spin_child_neutral_handover/T392_RESULTS.json`
- Digitised points: `T392_spin_child_neutral_handover/T392_DIGITISED_POINTS.csv`
- Labelled figure: `T392_spin_child_neutral_handover/T392_SPIN_CHILD_NEUTRAL_HANDOVER.png`
- Interactive report: `T392_spin_child_neutral_handover/T392_SPIN_CHILD_NEUTRAL_HANDOVER_REPORT.html`

The independent audit passed every artifact, arithmetic, frozen-gate,
provenance and claim-boundary check.

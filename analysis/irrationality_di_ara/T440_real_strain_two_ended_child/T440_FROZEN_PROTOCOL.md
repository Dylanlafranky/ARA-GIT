# T440 — Real-strain two-ended Space/Time child reconstruction

**Status:** frozen before T431/T432 evaluation events are scored  
**Date:** 27 August 2026 (Australia/Brisbane)  
**ARA hypothesis and geometry:** Dylan La Franchi  
**Operationalisation and implementation:** Codex

## Exact relational address

- **Who:** one binary-black-hole event is one measured parent identity. H1 and
  L1 are independent detector views of the same event; they are not the two
  black holes or two ARA children.
- **What:** construct a Space/Connection parent and a Time/Movement parent from
  disjoint feature families, then estimate one candidate transition child from
  each parent end. Do not combine the child estimates until their independent
  histories have been compared.
- **When:** `[-0.32,+0.08] s` relative to published event GPS. Event GPS is used
  only to retrieve and crop the real record. It cannot select either child
  landmark.
- **Where:** public 4096 Hz, 32-second GWOSC calibrated H1/L1 strain. Detector
  calibration and coordinate mapping use `[-12,-4]` and `[+4,+12] s`.
- **Why:** previous tests recovered much of the event geometry but did not
  independently recover timing. T440 asks whether a common child transition is
  visible from both the Connection and Movement sides of real strain.
- **How:** use the established off-source whitening and 30–512 Hz spectral lens,
  construct two independent 0–2 parents, differentiate each parent locally,
  map the two transition magnitudes to their own off-source 0–2 child tier, and
  compare histories, landmarks, controls, detectors and events.

## Data roles

- **Instrument development only:** GW150914 and GW170814. These may verify that
  the code and figures are interpretable; they cannot alter the frozen
  definitions or contribute to the evaluation verdict.
- **Locked evaluation:** four T431 events and six T432 events, all real GWOSC
  strain. These files have appeared in earlier tests, so this is a locked
  instrument evaluation rather than a claim of never-inspected external data.

## Independent parent constructions

The unchanged T427 whitening/bandpass is followed by a 64 ms Hann STFT stepped
every 4 ms. All features are mapped separately to 0–2 by the detector's own
off-source empirical distribution before any parent is formed.

### Space/Connection parent `P_S`

1. `S_amount`: log total 30–512 Hz spectral power.
2. `S_concentration`: one minus normalized spectral entropy.
3. `P_S = mean(S_amount, S_concentration)`.

### Time/Movement parent `P_T`

1. `T_frequency`: power-weighted spectral-centroid frequency.
2. `T_redistribution`: Hellinger distance between adjacent normalized spectra
   plus absolute logarithmic motion of the maximum-power ridge.
3. `P_T = mean(T_frequency, T_redistribution)`.

No amplitude or concentration term enters `P_T`. No frequency or redistribution
term enters `P_S`. Neither parent is defined from the other, and `P_S+P_T=2` is
explicitly forbidden.

## Two independent child-side cuts

Apply the same centred five-frame median to each parent. Let `dt=4 ms`.

- Space-end child evidence: `E_S = |dP_S/dt|`.
- Time-end child evidence: `E_T = |dP_T/dt|`.

Map `E_S` and `E_T` separately to 0–2 using their detector-specific off-source
empirical distributions. They are child coordinates at their own tier, not
fractions subtracted from a parent budget. Retain the signs of `dP_S/dt` and
`dP_T/dt` as a four-quadrant direction label, but do not use a preferred sign
to select a landmark.

Within the event window independently record:

1. the maximum of `E_S` and its time;
2. the maximum of `E_T` and its time;
3. each evidence history's weighted temporal centroid;
4. their Bhattacharyya history overlap after each is normalized to unit mass;
5. their zero-lag and best-lag Spearman association over `+/-32 ms`;
6. Dice overlap of their top 20% event-window samples;
7. the signed parent-derivative quadrant at the joint-evidence maximum.

Only after these independent quantities are written may the descriptive joint
child history be formed as `sqrt(E_S * E_T)`. Its maximum is the candidate
shared-child time; it cannot rescue disagreement between the two sides.

## Frozen controls

1. Every non-overlapping 0.40 s window wholly inside the two off-source regions
   is scored identically within each detector.
2. Space-end and Time-end histories are paired with the wrong event on a common
   event-relative grid.
3. The Time-end history is circularly shifted by at least 64 ms before the same
   `+/-32 ms` lag search.
4. H1 and L1 are scored separately. Their candidate joint-child times must
   agree within 16 ms, allowing the terrestrial propagation delay and one STFT
   step of discretization.
5. Direction quadrants are descriptive. Reversal or quadrant choice cannot
   rescue a failed timing/history result.

## Frozen gates

An evaluation event has an **accepted candidate child** only when:

1. H1 and L1 both place the event-window Bhattacharyya overlap at or above the
   90th percentile of their own matched off-source controls;
2. H1 and L1 both place best-lag association at or above the 90th control
   percentile;
3. the independently selected Space-end and Time-end peaks differ by at most
   32 ms in each detector;
4. H1 and L1 joint-child times differ by at most 16 ms.

Population support requires at least 7 of 10 locked evaluation events to have
an accepted candidate child, and the median correct-event overlap to exceed
the wrong-event distribution at one-sided empirical `p<=0.05`.

If the population gate fails, T440 rejects this operational child instrument.
It does not reject ARA, the independent parent separation, or the possibility
that the child is visible at another scale, cadence or observable.

## Interpretation boundary

A pass would show that two independently measured parent-facing changes in real
detector strain converge on a reproducible event-local transition child. It
would not separate the two physical black holes, directly measure spacetime,
prove a new particle, replace general relativity, or establish causation. A
shared gravitational-wave transient is an established explanation for common
timing; the ARA-specific result would be the stable two-ended relational
decomposition and its cross-event geometry.

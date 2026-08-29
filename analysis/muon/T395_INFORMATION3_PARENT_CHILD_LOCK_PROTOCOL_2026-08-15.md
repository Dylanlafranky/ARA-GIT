# T395 — Information³ parent/child neutrino lock protocol

**Frozen:** 15 August 2026, before T395 scoring  
**Status:** executable protocol

## Question

Do the already-measured parent and child ARA cuts form one event-level
hierarchy from which the missing neutral branches can be reconstructed, and
does the visible parent cut carry predictive information about the hidden
child cut on unseen events?

## Identity and grain

This test uses the T394 frozen Standard-Model `V-A` truth generator. It does
not join the independent Super-K population-time curve to the generated
energy events. That timing cut is not event-linked to these neutral-pair
labels and therefore cannot enter this lock without fabricating a relation.

At each generated decay event define:

\[
P=x_e,
\qquad N=2-P,
\]

where `(P,N)` is the parent charged-versus-joint-neutral ARA cut. Inside the
neutral branch define the child cut

\[
C={2x_{\nu_e}\over N},
\qquad \bar C=2-C.
\]

The third, composed relation is

\[
\widehat x_{\nu_e}=N{C\over2},
\qquad
\widehat x_{\bar\nu_\mu}=N{2-C\over2}.
\]

## Two distinct gates

### Gate A — exact geometric composition

Supply both event-level cuts, `P` and `C`, and reconstruct the absolute three
branches. This must close to numerical precision if the two cuts are truly
nested coordinates. Passing Gate A validates the cross-rung coordinate map;
it is not independent empirical evidence because the reconstruction follows
from the definitions.

### Gate B — blinded Information³ reconstruction

Hide `C` in validation and holdout events. Use calibration events only to
learn the conditional child distribution `p(C|P)`. Select model resolution on
validation, freeze it, then reveal holdout `C` and the two absolute neutrino
energies.

This asks whether the parent relation retains information about the child
relation. It does not claim that one parent coordinate determines an
individual stochastic decay exactly.

## Split

Use the deterministic SplitMix64 event-index split:

- buckets `0–4`: calibration;
- buckets `5–6`: validation;
- buckets `7–9`: untouched holdout.

The fixed T394 truth seed and event count remain `394` and `1,000,000`.

## Frozen models

The ARA model is a calibration-only conditional histogram over `P` and `C`.
Parent resolutions `8, 16, 32, 64` compete on validation; the child axis is
fixed at 128 bins over `0–2`; Jeffreys smoothing is `0.5` per child cell. The
validation winner is frozen for holdout.

Controls:

1. **Unconditional child:** ignores the parent cut.
2. **Parent-shuffled:** destroys cross-rung correspondence in calibration.
3. **Identity-reversed:** evaluates `2-C` under the frozen labelled model.
4. **Phase-space:** uniform over the event's kinematically allowed child
   interval, preserving support but removing `V-A` weighting.
5. **Symmetric point:** fixes `C=1` when reconstructing absolute branches.

## Scores and gates

Primary score:

\[
G=\operatorname{NLL}_{\rm unconditional}
-\operatorname{NLL}_{\rm conditional}.
\]

Gate B passes when `G>0` and its fixed block-bootstrap 95% interval excludes
zero. Also report NLL against all controls, child-coordinate MAE, absolute
neutrino-branch MAE and direction Brier score.

The holdout bootstrap uses 200 deterministic blocks and 5,000 fixed-seed
resamples of their mean score differences.

## Claim ceiling

A positive result demonstrates a usable parent-to-child statistical lock in
the frozen truth model. It is not direct two-neutrino measurement, is not a
pre-decay clock, and does not identify the next individual muon to decay.


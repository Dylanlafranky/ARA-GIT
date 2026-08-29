# T395 — Information³ parent/child neutrino lock findings

**Recorded:** 16 August 2026  
**Frozen protocol:** `T395_INFORMATION3_PARENT_CHILD_LOCK_PROTOCOL_2026-08-15.md`  
**Protocol SHA-256:** `04D8CCA433751FC1ADDF20CA07B4CE71ACE233362EDDF9EF0DA7678E77511ED3`  
**Status:** EXACT NESTED COMPOSITION VALIDATED; BLINDED PARENT-TO-CHILD STATISTICAL LOCK PASSED IN THE FROZEN TRUTH MODEL

## Answer first

The parent and child cuts do form a usable Information³ lock, with an
important distinction.

1. When the event-level parent cut and child cut are both supplied, the third
   relation—the absolute two-neutrino decomposition—is reconstructed to
   machine precision. This demonstrates that the cuts are correctly nested,
   but it is a coordinate identity rather than independent empirical evidence.
2. When the child cut is hidden, a model fitted only on calibration events can
   use the visible parent cut to predict the child distribution in untouched
   events. It gained `0.26429817` nats per event over ignoring the parent, with
   block-bootstrap 95% interval `[0.26256574,0.26603493]`. This is the
   non-trivial Information³ result.
3. Individual child values remain broadly distributed. The lock therefore
   reconstructs the likely neutral-pair geometry and improves the third
   relation, but it does not determine the exact split of one decay.

## The three relations

The parent charged-versus-neutral cut is

\[
P=x_e,
\qquad N=2-P.
\]

The internal neutral-pair child cut is

\[
C={2x_{\nu_e}\over N},
\qquad \bar C=2-C.
\]

Their composed third relation is

\[
x_{\nu_e}=N{C\over2},
\qquad
x_{\bar\nu_\mu}=N{2-C\over2}.
\]

In ARA language, the parent tells us how much of the total identity belongs to
the joint neutral branch; the child tells us how that branch divides
internally; their relation restores the two absolute child contributions.

## Grain boundary

T395 uses the event-level T394 Standard-Model `V-A` truth generator. It does
not join the Super-K population release-time reconstruction to these energy
events. Those are different cuts without a shared event key. Combining them
would manufacture an Information³ triangle rather than discover one.

The one million events were deterministically split into:

- calibration: `499,615`;
- validation: `200,326`;
- untouched holdout: `300,059`.

## Gate A — exact composition

Supplying both parent and child cuts reconstructed the original truth branches
with maximum errors:

- electron-neutrino coordinate: `1.11e-16`;
- anti-muon-neutrino coordinate: `2.22e-16`;
- total three-branch closure: `4.44e-16`.

This passes the nested-coordinate gate. It is labelled as forced mathematical
composition, not as independent physical confirmation.

## Gate B — child hidden before holdout

A calibration-only conditional child distribution was built at parent
resolutions `8`, `16`, `32` and `64`. Validation selected `64`; this choice
was frozen before the holdout child values were revealed.

### Distribution scores

Lower mean negative log-likelihood is better.

| Model | Holdout mean NLL |
|---|---:|
| Parent-conditioned Information³ lock | `-0.062745` |
| Phase-space control | `0.026074` |
| Unconditional child distribution | `0.201554` |
| Parent-shuffled control | `0.208799` |
| Identity-reversed control | `0.261271` |

A negative NLL is permitted for a continuous density because density values
can exceed one over a sufficiently narrow interval. Only comparisons under
the same child coordinate and measure are used.

The primary information gain was

\[
G
=
\operatorname{NLL}_{\rm unconditional}
-
\operatorname{NLL}_{\rm conditional}
=0.26429817
\]

nats per event, with 95% interval

\[
[0.26256574,0.26603493].
\]

The parent-conditioned model also beat the parent-shuffled, identity-reversed
and phase-space controls. The association therefore depends on the correct
parent value and child identity, not merely on the marginal child shape or
kinematic support.

## Point reconstruction is deliberately weaker

Predicting the conditional distribution is not the same as identifying the
exact stochastic child value. The child-coordinate mean absolute errors were:

- parent-conditioned lock: `0.233079`;
- unconditional child: `0.234370`.

For the reconstructed absolute electron-neutrino coordinate:

- parent-conditioned lock: `0.141962`;
- unconditional child: `0.142865`;
- fixed symmetric child `C=1`: `0.150312`.

The parent cut therefore adds substantial distributional information but only
modest point-estimate improvement. The event scatter does not collapse onto a
single line. Additional event-level relations would be required to lock one
particular decay more tightly.

## ARA interpretation

The result supports the following restrained statement:

> In the frozen muon-decay truth model, the charged-versus-neutral parent cut
> retains statistically strong information about the internal two-neutrino
> child cut. Parent amount plus child division reconstructs the absolute
> three-branch relation exactly when both are known, and calibration-only
> parent conditioning improves prediction of the hidden child distribution on
> untouched events.

This is a clean example of the Information³ distinction:

- **geometric lock:** two supplied relations reconstruct the third;
- **predictive lock:** the visible parent restricts the distribution of the
  missing child relation;
- **remaining Other:** stochastic event-level variation not determined by the
  parent coordinate alone.

## Claim ceiling

T395 remains a truth-model crosswalk. It is not simultaneous experimental
measurement of both neutrinos, does not reconstruct the pre-decay anti-phase
of one living muon, and cannot identify which muon releases next. A direct
individual handover test still requires event-linked pre-decay muon state,
charged-daughter energy/direction and neutral-sensitive or missing-momentum
information.

## Independent validation

The independent validator passed all checks:

- protocol hash and frozen model selection;
- parent and child closure;
- third-relation composition;
- positive holdout information-gain interval;
- superiority to unconditional, shuffled and phase-space controls;
- absence of a fabricated Super-K timing join.

## Reproduction artifacts

- Analysis: `t395_information3_parent_child_lock.py`
- Independent validation: `validate_t395_information3_parent_child_lock.py`
- Visual builder: `build_t395_information3_visual.py`
- Results: `T395_information3_parent_child_lock/T395_RESULTS.json`
- Validation: `T395_information3_parent_child_lock/T395_VALIDATION.json`
- Holdout sample: `T395_information3_parent_child_lock/T395_HOLDOUT_SAMPLE.csv`
- Labelled visual: `T395_information3_parent_child_lock/T395_INFORMATION3_LOCK.png`


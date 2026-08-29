# T396 — Information³ spin/child lock protocol

**Frozen:** 16 August 2026, before any T396 event generation or scoring  
**Status:** executable frozen protocol  
**Audience:** technical; ARA geometry first, established-physics crosswalk beside it

## Who, what, when, where, why and how

- **Who:** fully polarized positive muons decaying at rest through
  `mu+ -> e+ + nu_e + anti-nu_mu` in a fresh leading-order Standard-Model
  `V-A` truth population.
- **What:** test whether two independently observed ARA relations predict the
  hidden neutral child better together than either does alone. The relations
  are the charged-versus-neutral parent allocation and the charged-daughter
  direction relative to the pre-decay muon spin.
- **When:** one row is one completed decay event. Calibration, validation and
  untouched holdout events are separated by deterministic event-index hashes.
- **Where:** the muon rest frame. The spin direction is the signed orientation
  axis; no detector geometry, missing momentum or post-hoc event join is used.
- **Why:** T395 established a parent-to-child statistical lock from charged
  energy alone. T396 asks the stricter Information³ question: does a second,
  independently observed relation add holdout information about that same
  hidden child?
- **How:** freeze the ARA coordinates and candidate histogram resolutions;
  generate fresh events from the polarized three-body matrix element; select
  resolution on validation only; score holdout once against named controls.

## ARA coordinates

For each event define the parent relation

\[
P=x_e,
\qquad
N=2-P,
\]

where `x_i = 2 E_i / m_mu`. Inside the neutral branch define

\[
C={2x_{\nu_e}\over N},
\qquad
\bar C=2-C.
\]

The second observed relation is the spin/daughter orientation

\[
R=1+\cos\theta_{eS},
\qquad R\in[0,2],
\]

where `theta_eS` is the angle between the positron momentum and the actual
muon-spin direction. Its mirrored orientation is `2-R`.

The Information³ lock under test is

\[
(P,R)\longrightarrow C,
\]

with the composed absolute branches

\[
\widehat x_{\nu_e}=N{\widehat C\over2},
\qquad
\widehat x_{\bar\nu_\mu}=N{2-\widehat C\over2}.
\]

`P` and `R` are separately observed inputs. `C` is hidden during validation
and holdout prediction. Exact recomposition after supplying the true `C` is a
coordinate identity and is not counted as independent evidence.

## Frozen polarized V-A truth law

Use massless daughters, leading order and polarization magnitude `P_mu=1`.
The charged marginal is the Michel law

\[
p(x_e)\propto x_e^2(3-2x_e).
\]

At fixed `x=x_e`, the daughter-angle conditional is

\[
p(c\mid x)={1\over2}\left[1+
{2x-1\over3-2x}c\right],
\qquad c=\cos\theta_{eS}.
\]

Let `z=x_nu_e`, with `1-x <= z <= 1`. The event-level polarized neutral law is

\[
p(z\mid x,c)\propto
z(1-z)\,[1-c\cos\gamma(x,z)],
\]

where

\[
\cos\gamma(x,z)=1-{2(x+z-1)\over xz}
\]

is the fixed angle between the charged daughter and `nu_e` implied by
three-body momentum closure. Integrating over `z` reproduces the frozen Michel
energy-angle law. The generator must verify the expected population means
`E[x_e]=0.7`, `E[x_nu_e]=0.6` and `E[cos(theta_eS)]=1/9` within Monte Carlo
error before the prediction result is accepted.

This is a fresh event population, not a reuse of the T395 truth rows. The
primary seed is `396`; the primary population contains `1,000,000` events.

## Split and model selection

Use SplitMix64 on event index:

- buckets `0-4`: calibration;
- buckets `5-6`: validation;
- buckets `7-9`: untouched holdout.

The child axis has 64 bins over `0-2`, with Jeffreys smoothing `0.5` per cell.

Validation-only candidates:

- parent-only `p(C|P)`: `P` bins `8, 16, 32, 64`;
- relation-only `p(C|R)`: `R` bins `8, 16, 32, 64`;
- joint `p(C|P,R)`: `(P bins, R bins)` candidates
  `(8,8), (12,8), (12,12), (16,12), (16,16), (24,16), (24,24)`.

The lowest validation NLL in each family is frozen. Holdout labels are then
revealed once.

## Controls

1. **Parent-only:** `p(C|P)`; the T395-level question.
2. **Relation-only:** `p(C|R)`.
3. **Unconditional child:** `p(C)`.
4. **Additive/factorized fusion:** normalized
   `p(C|P) p(C|R) / p(C)`, with no learned `P x R` interaction cell.
5. **Relation-shuffled calibration:** permute `R` among calibration events
   before fitting the joint model.
6. **Wrong-event relation:** score each holdout event with another event's
   `R`, using a fixed nonzero cyclic offset.
7. **Mirrored orientation:** score with `2-R`.
8. **Phase space:** uniform on the event's allowed child interval.
9. **Analytic V-A oracle:** exact `p(C|P,R)` under the frozen generator; this
   is a reference ceiling, not a competitor the histogram must beat.
10. **Zero-polarization falsifier:** a separately generated `P_mu=0`
    population must not show a positive joint-versus-parent information gain.

Sensitivity populations at `P_mu=0.85` and `0.5` are also generated with
fixed seeds `1396` and `2396`; the zero-polarization seed is `3396`. Each
sensitivity population contains `500,000` events. These are robustness checks,
not substitutes for the primary holdout.

## Scores and frozen gates

Primary event score is negative log likelihood. Define the incremental lock

\[
G=\operatorname{NLL}_{P}-\operatorname{NLL}_{P,R}.
\]

Use 200 deterministic holdout blocks and 5,000 fixed-seed block-bootstrap
resamples (`seed=396`) for confidence intervals.

The **primary Information³ gate passes** only if:

1. `G>0` on untouched primary holdout;
2. the 95% block-bootstrap interval for `G` excludes zero;
3. the joint model beats relation-only and unconditional NLL; and
4. the zero-polarization joint-minus-parent interval includes zero or has a
   non-positive point estimate.

Report, but do not silently redefine the primary gate from, ordering against
the additive, shuffled, wrong-event, mirrored and phase-space controls.
Also report child-coordinate MAE, absolute two-neutrino branch MAE,
calibration by predicted child mean, and distance from the analytic oracle.

## Claim ceiling

A pass demonstrates that, in a fresh polarized Standard-Model truth model,
two independently observed ARA cuts contain more event-level information
about the hidden neutral split together than the parent cut alone. It is a
bottom-up crosswalk/recovery of known V-A structure in ARA coordinates.

It is not direct simultaneous observation of both neutrinos, not a forecast
of which muon decays next, not an experimental discovery, and not evidence
that ARA exceeds the Standard Model. A later empirical test requires an
event-linked source that measures the spin/charged relation and provides an
independent neutral-sensitive target.

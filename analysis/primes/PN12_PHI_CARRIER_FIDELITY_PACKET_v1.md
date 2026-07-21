# PN12 fidelity packet v1 — angular carrier beneath the prime rung ladder

**Claim ID:** `PN12/PRIME-LADDER-ANGULAR-CARRIER/v1`  
**Date:** 21 July 2026  
**Orientation:** up = adding the next prime child and forming the next, larger primorial lock  
**Tier before testing:** `PARKED -> REGISTERED`  
**Dylan fidelity verdict:** `EXACT ENOUGH TO TEST` — “Yes, can we do that please.”

## F0 — frozen user prior

> “Yes. So picture like our spheres or circles doing their thing and building their ladder structure, while riding on
> an impossibly large Phi wave.”

Additional landmark supplied before any PN12 calculation:

> “36 degrees might be worth testing?”

## Identity and direction

- **Identity being measured:** the canonical primorial prime ladder. Rung `m` is the complete connection lock
  `B_m = p_1 p_2 ... p_m`; the next prospective child is `q_m = p_(m+1)`.
- **Ordered direction:** `B_m -> B_(m+1) = B_m q_m` is upward/slower/larger.
- **Local ARA cycles:** the already incorporated prime-child waves close at phase zero at `B_m`.
- **Candidate larger carrier:** the phase of the not-yet-incorporated child `q_m` when the current lock `B_m` occurs.
  This is the only immediately adjacent child phase that is nontrivial without assigning an external angle.

## F1 — three-view translation

### 1. Plain restatement

The prime children build their ordinary connection ladder one rung at a time. The test asks whether the current whole
lock also advances through the next child's circular phase in a regular angular walk, as if the local spheres and
their logarithmic ladder were being carried around a much larger wave. Phi is not placed into the phase coordinate;
it is only a frozen candidate for the step that the raw ladder may or may not produce.

### 2. Mathematical representation

At rung `m`, define the parent lock and next child

\[
\underbrace{B_m}_{\substack{\text{current complete}\text{connection lock}}}
=\prod_{j=1}^{m}p_j,
\qquad
\underbrace{q_m}_{\substack{\text{next child}\text{not yet in the lock}}}
=p_{m+1}.
\]

The natural entry phase of that next child is

\[
\underbrace{u_m}_{\substack{\text{next-child phase}\text{at the current lock}}}
=\frac{B_m\bmod q_m}{q_m}\in[0,1),
\qquad
\underbrace{\theta_m}_{\text{same phase in radians}}=2\pi u_m.
\]

The upward carrier step is

\[
\underbrace{\delta_m}_{\substack{\text{observed angular step}\text{between successive rungs}}}
=(u_{m+1}-u_m)\bmod1.
\]

The primary Phi-carrier prediction is

\[
\delta_m\approx
\underbrace{\phi^{-2}}_{\substack{\text{golden-angle turn}\137.507764^\circ}}
=0.381966\ldots .
\]

Dylan's pre-run addition is separately tested as

\[
\delta_m\approx
\underbrace{1/10}_{\substack{\text{pentagonal half-angle}\36^\circ}}.
\]

### 3. Back-translation

Stand on one completed prime rung and ask where that rung lands on the circular cycle belonging to the very next
prime child. Do the same one rung higher. Their normalized circular difference is the amount the larger path turned.
If a large Phi carrier is present in this reading, those turns should be coherent and should repeatedly prefer the
declared Phi angle rather than rational, exponential, anti-phase or zero-turn alternatives.

## Assumptions added by the AI

1. The adjacent not-yet-incorporated child is the appropriate native phase reference for the larger carrier.
2. Normalising every next-child cycle to one turn permits comparison across different prime identities.
3. A carrier described by `theta_(m+1)=theta_m+alpha` should leave a concentrated distribution of circular increments.
4. The strict primary orientation is the forward golden angle `1/phi^2`; its reverse is reported but cannot rescue it.

## Information discarded

- The full joint torus of every incorporated and future child phase is reduced to the immediately adjacent child.
- The local factor geometry inside each rung is not re-tested; PN12 measures only the proposed larger angular walk.
- Amplitude, energy and musical-note assignments are absent because the integer ladder supplies phase but no physical
  amplitude or acoustic scale.

## Alternative mathematical objects fitting the wording

- product/sum phase of all incorporated prime phasors;
- a fitted low-dimensional projection of the full residue torus;
- angular motion along integer nodes inside one fixed sieve wheel;
- Phi as curvature or pitch rather than a constant angular increment.

These remain different claims. PN12 cannot be relabelled as any of them after its result.

## Forbidden substitutions/proxies

- assigning `theta_m = m/phi^2` and then “recovering” Phi;
- using musical notes, screen resolutions or fitted Fourier/NMF components;
- selecting a phase projection after viewing the target;
- accepting any one of several Phi-family angles as a pooled post-hoc hit;
- treating exact primorial recurrence or the Chinese remainder theorem as evidence for Phi by itself.

## First possible construct failure

Comparing `u_m` and `u_(m+1)` compares phases belonging to different next-child identities. The normalised 0–1 circle
makes that comparison mathematically defined, but it may not be the carrier Dylan intends. A negative result therefore
rejects this **adjacent-child angular-carrier reading**, not every possible large-wave reading.


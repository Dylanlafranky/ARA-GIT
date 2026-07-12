# MX1 translation-fidelity packet v2 — component ARAs plus pair-level Gauss balance

**Claim ID:** `MX1-v2`  
**Prepared:** 12 July 2026  
**Status:** `FIDELITY APPROVED — EXACT ENOUGH TO TEST; DEVELOPMENT ONLY`  
**Inherits:** every unchanged field and guardrail from `MX1_TRANSLATION_FIDELITY_PACKET_v1_DRAFT.md`  
**Orientation:** negative-source pair pole = 0; equal source magnitude = 1; positive-source pair pole = 2.

## Dylan correction creating v2

> “I think we could also do the ARA of just the positive and negative. Cause Gauss cancellation is the 1.0 in ARA
> as you mentioned. Maximum resistance of the two—or equal resistance might be more apt. ... Isn't just the Positive
> as one wave and the Negative the other and the ARA between them make Gauss?”

## Corrected identity hierarchy

The same electrostatic structure has three declared ARA readings:

1. \(a_+\): waveform ARA of the positive-source half-wave considered locally;
2. \(a_-\): waveform ARA of the negative-source half-wave considered locally;
3. \(x_Q\): pair-level 0–2 composition between their non-negative source magnitudes.

The positive and negative half-waves are not unrelated objects. They are locally measurable sub-identities/appearances
inside one complete coupled wave identity.

“Equal resistance” is translated as **equal opposing source magnitude**. Electrical resistance \(R=V/I\) is not the
quantity measured by Gauss and must not be substituted.

## Exact pair-level algebra

For a declared boundary or wave cell, define

\[
\underbrace{Q_+}_{\substack{\text{total enclosed positive}\\
\text{source magnitude}}}
=\int_V\max(\rho_q,0)\,dV,
\qquad
\underbrace{Q_-}_{\substack{\text{total enclosed negative}\\
\text{source magnitude, stored positive}}}
=\int_V\max(-\rho_q,0)\,dV.
\]

Define the total unsigned source activity and pair ARA coordinate:

\[
\underbrace{T_Q}_{\text{total opposing source magnitude}}
=Q_++Q_-,
\qquad
\underbrace{x_Q}_{\substack{\text{pair-level ARA composition}\\
0=\text{negative},\ 1=\text{equal},\ 2=\text{positive}}}
=2\frac{Q_+}{Q_++Q_-}.
\]

Then

\[
\boxed{
\underbrace{\Phi_E}_{\text{Gauss signed electric flux}}
=
\frac{1}{\varepsilon_0}
\underbrace{T_Q}_{\text{total source magnitude}}
\underbrace{(x_Q-1)}_{\text{centred ARA direction/asymmetry}}
}
\]

because

\[
T_Q(x_Q-1)=Q_+-Q_-=Q_{net}.
\]

This is exact algebra once \(Q_+\), \(Q_-\) and the boundary are declared. It shows that the pair-level ARA
composition does not make Gauss by itself: it supplies direction/asymmetry, while \(T_Q\) supplies magnitude.

At \(x_Q=1\), Gauss net flux is zero for both a quiet empty boundary and an intense equal positive/negative pair.
The component ARAs, \(T_Q\), TE-ARA and variance distinguish those states.

## TE-ARA's role

TE-ARA remains

\[
\mathrm{TE\!-\!ARA}=2\frac{E_{id}}{E_{total}},
\]

so it measures main-identity **energy participation**, not charge magnitude \(T_Q\). The empirical bridge to test is
whether TE-ARA, component ARAs, rung and geometry predict or organise \(T_Q\) consistently:

\[
\underbrace{T_Q}_{\text{Gauss source magnitude}}
\stackrel{?}{=}
\underbrace{\mathcal C}_{\text{frozen scale-aware bridge}}
\left(
\underbrace{a_+,a_-}_{\text{component shapes}},
\underbrace{\mathrm{TE\!-\!ARA}}_{\text{energy participation}},
\underbrace{k_0,\theta}_{\text{rung and phase}},
\underbrace{\mathrm{Other}}_{\text{declared enclosed couplings}}
\right).
\]

Only enclosed Other sources alter Gauss's net source. External nearby charges may deform local inward/outward field
patterns but cancel in the complete closed-boundary net.

## Corrected plain restatement

One complete electric wave is a coupled positive/negative identity. We may zoom into either half and measure its own
ARA shape. We may also zoom out and measure the ARA between the two source magnitudes. That pair-level ARA tells us
which sign dominates, while their combined magnitude tells us how strong the imbalance is. Multiplying centred pair
ARA by total source magnitude gives Gauss's net result. TE-ARA is a separate energy-participation reading whose stable
relation to the source magnitude is the bridge under test.

## Back-translation without the original wording

A signed balance needs two coordinates: composition and scale. The bounded composition says which member of an
opposed pair dominates; the unsigned total says how much paired activity exists. Each member may also possess its own
internal asymmetry. Energy participation is another projection and may help infer the unsigned scale, but it cannot be
silently treated as charge.

## Updated forbidden proxies

- Do not use \(x_Q\) alone to predict Gauss magnitude.
- Do not rename \(T_Q\) as TE-ARA.
- Do not use electrical resistance language unless voltage and current are actually measured.
- Do not let external charges enter `Other` as a net enclosed source when they lie outside the Gaussian boundary.
- Do not flatten \(a_+\), \(a_-\) and \(x_Q\) into one unlabelled ARA value.

## Low-energy fidelity question

```text
I think you mean: the positive half and negative half can each be measured as their own local ARA, while the whole wave remains their coupled identity. A third, pair-level ARA says how their source magnitudes are divided.

I would test it as: Gauss = total positive-plus-negative source magnitude × (pair ARA − 1), with component ARAs and TE-ARA tested as bottom-up predictors of that total magnitude and its evolution.

The main thing this translation separates is: TE-ARA is energy participation, whereas Gauss also needs charge/source magnitude in its own units.
```

**Dylan verdict:** `EXACT ENOUGH TO TEST` — 12 July 2026. Dylan accepted the corrected bridge and explicitly requested that the TE-ARA component remain in the test so the available geometry is retained.  
Allowed labels: `EXACT ENOUGH TO TEST`, `USABLE WITH CORRECTION`, `WRONG OBJECT`, `UNSURE / KEEP AS MUSING`.

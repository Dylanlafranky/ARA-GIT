# MX3f ARA gradient-coupling web protocol

**Status:** FORMALISATION DRAFT / NOT RUN  
**Purpose:** convert nonlinear Fourier-route coupling into an explicit ARA composition and participation coordinate

## Motivation

The (k=20) identity is not supplied by one exclusive binary genealogy. Every pair

\[
(a,20-a),\qquad a=1,2,\ldots,10
\]

is a possible nonlinear route into the same output mode. The measured route strengths form a coupling web. This is a
concrete candidate for Dylan's ARA gradient mixing and for the missing aggregation/coupling law.

## ARA route coordinate

For a fixed output identity (K=a+b), define the route-composition coordinate

\[
\underbrace{x_{a|K}}_{\substack{\text{ARA position of}\text{one route component}}}
=
\frac{2a}{a+b}
=
\frac{2a}{K},
\qquad
\underbrace{x_{b|K}}_{\text{opposite orientation}}
=2-x_{a|K}.
\]

The equal route (a=b=K/2) lies at the ARA ridge (x=1). The pair (9+11\rightarrow20) lies at
(x=0.9/1.1), immediately to either side of the ridge.

Define unsigned ridge distance

\[
\delta_{a|K}=|x_{a|K}-1|.
\]

This is composition geometry only. It does not yet specify which component supplies or receives energy.

## Coupling strength and participation

Use field and particle bicoherence as phase-coupling strengths:

\[
\underbrace{w_{a,b\rightarrow K}}_{\substack{\text{route coupling}\text{strength}}}
=b^2(a,b;K).
\]

Normalise across all declared routes into a TE-ARA-style participation ledger:

\[
\underbrace{p_{a,b|K}}_{\text{route participation}}
=
\frac{w_{a,b\rightarrow K}}
{\sum_{j=1}^{\lfloor K/2\rfloor}w_{j,K-j\rightarrow K}},
\qquad
\underbrace{\mathrm{TE\!-!ARA}_{a,b|K}}_{\text{0--2 participation}}
=2p_{a,b|K}.
\]

Bicoherence reports phase locking, not energy-transfer magnitude or sign. The participation ledger must therefore be
labelled *coherent-route participation* until a mode-resolved nonlinear transfer calculation supplies signed energy
flow.

## Current (K=20) development observation

- (9+11\rightarrow20), (x=0.9/1.1): field/particle bicoherence 0.7816/0.7882;
- (10+10\rightarrow20), ridge (x=1): 0.5760/0.6022;
- (5+15\rightarrow20), (x=0.5/1.5): 0.2407/0.2654.

Thus the exact ridge is not the strongest route in this run. A near-ridge asymmetric pair is stronger. This is
consistent with, but does not prove, Dylan's proposal that exact equality can suppress net generative transfer while
near-ridge asymmetry permits handover.

## Signed transfer requirement

To establish actual accumulation/release rather than phase association, compute the contribution of each convolution
route to the output-mode energy tendency from the governing Vlasov nonlinearity:

\[
\underbrace{T_{a,b\rightarrow K}(t)}_{\substack{\text{signed route}\text{energy transfer}}}
\propto
\Re\!\left[
\widehat X_K^*(t)
\widehat{\mathcal N}_{a,b\rightarrow K}(t)
\right].
\]

Positive and negative signs then provide the directional ARA coordinate. Without this calculation, (a<b) is only a
mode-number ordering and must not be called physical accumulation or release.

## Fractal/coarse-graining test

For the declared self-harmonic lineage, define the exact logarithmic rung coordinate

\[
\underbrace{r(k)}_{\text{harmonic ARA rung}}
=
\log_2\!\left(\frac{k}{k_0}\right).
\]

The observed lineage has \(r(5)=0\), \(r(10)=1\), and \(r(20)=2\). This is an exact rescaling, not a fitted bridge.
Mixed descendants occupy non-integer rung positions; for example \(r(15)=\log_2 3\approx1.585\).

Construct the same rescaled route profile for multiple output modes:

\[
W_K(x)=\{x_{a|K},w_{a,K-a\rightarrow K}\}.
\]

Test whether

\[
\underbrace{\mathcal R[W_K(x)]}_{\text{rescale/coarse-grain}}
\approx
\underbrace{W_{2K}(x)}_{\text{next harmonic identity}}
\]

under one frozen rule. Primary development comparison: (K=10) versus (K=20). Confirmation must use new particle
counts, seeds and the held-out beam configuration.

## Controls

- equal-amplitude random-phase mode families;
- non-triad pairs;
- circular time shifts;
- raw amplitude products without phase coupling;
- field versus particle route profiles;
- signed-transfer result versus bicoherence-only result;
- sensitivity to grid resolution and particle count.

## Success rule

The ARA coupling-web interpretation gains support if:

1. field and particle route profiles agree;
2. the profile transfers across noise/seeds;
3. signed route transfer provides stable accumulation/release direction;
4. rescaled profiles recur across at least three output identities;
5. ARA compression predicts held-out route structure better than generic smooth or amplitude-only baselines.

## Plain-language version

Do not force one mother and one father onto the (k=20) wave. Treat every pair that can sum to 20 as an edge feeding
the identity. Put those edges on the ARA 0--2 composition line, weight them by how coherently they couple, and later
add the direction of actual energy flow. Then test whether the same weighted gradient shape reappears for larger and
smaller harmonic identities. That is the measurable form of the nonlinear ARA coupling web.

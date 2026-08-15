# T393 — Joint neutrino-pair projection at the muon handover

Date frozen: 2026-08-15

## Question

Does the frozen T392 charged-daughter handover support the ARA interpretation that one charged daughter and a joint two-neutrino branch are three distinct decay children, with the charged child projecting from approximately `0.5` at its own rung to approximately `0.25` at the parent rung?

## Claim boundary

This is a kinematic child-decomposition test. It is **not** an event-level prediction of the time at which an individual muon will decay. The public T392 source resolves the charged daughter's population energy–direction relation, not a pre-decay state plus both neutrinos for each muon.

The following are separated deliberately:

1. **Forced energy closure**
   
   \[
   x_e+x_{\nu_e}+x_{\bar\nu_\mu}=2.
   \]
   
   This is conservation bookkeeping and cannot count as evidence for ARA by itself.

2. **Forced momentum anti-phase**
   
   In the stopped-muon rest frame,
   
   \[
   \mathbf p_{\nu_e}+\mathbf p_{\bar\nu_\mu}=-\mathbf p_e.
   \]
   
   This identifies the two neutrinos as one joint counter-branch, but is also conservation.

3. **Informative internal pair split**
   
   Standard-Model `V-A` dynamics gives the two neutrino species different conditional energy distributions. This is tested against a uniform phase-space / identity-shuffled control that makes the two neutral children equal on average.

## Frozen inputs

- T392 charged-daughter reversal: `x_e* = 0.49019`.
- T392 digitisation interval: `[0.48612, 0.49446]`.
- Ideal massless Standard-Model directional reversal: `x_e = 0.5`.
- Pure ARA rung projection: divide a child coordinate by `2` when reading it at its parent rung.
- Decay identity: `mu+ -> e+ + nu_e + anti-nu_mu`.

## Exact kinematic map

All child energies use `x_i=2E_i/m_mu`, so the decay budget is `2`.

At a fixed charged coordinate `x_e=x`, let `z=x_nu_e`. The other neutral child is

\[
x_{\bar\nu_\mu}=2-x-z,
\]

with

\[
1-x\le z\le1.
\]

Neglecting the electron and neutrino masses, the `V-A` conditional weight is

\[
w(z\mid x)\propto z(1-z).
\]

The parent-rung energy contributions are

\[
p_e={x_e\over2},\qquad
p_{\nu_e}={x_{\nu_e}\over2},\qquad
p_{\bar\nu_\mu}={x_{\bar\nu_\mu}\over2},
\]

and necessarily sum to the parent ridge:

\[
p_e+p_{\nu_e}+p_{\bar\nu_\mu}=1.
\]

The neutral-pair invariant coordinate is kept separate from its energy share:

\[
{q_{\nu\nu}^2\over m_\mu^2}=1-x_e.
\]

## Frozen tests and gates

1. **Approximate charged quarter landmark:** `abs(x_e*/2 - 0.25) <= 0.01`.
2. **Exact half-landmark interval:** report whether `0.5` is inside the frozen T392 interval. This is reported separately and is not softened after inspection.
3. **Three-child parent closure:** absolute residual below `1e-12`. This is a bookkeeping validation only.
4. **Distinct neutral siblings:** the `V-A` conditional mean gap at the parent rung must exceed `0.05`.
5. **Directional neutral ordering:** the probability that the muon-flavour neutral child carries more energy must exceed `0.60`.
6. **Control separation:** the identity-shuffled/uniform control must return internal neutral coordinates `(1,1)`, while `V-A` must produce a non-zero displacement from the pair ridge.
7. **Numerical reproduction:** a fixed-seed Monte Carlo must reproduce each analytic neutral mean within `0.0015` child-coordinate units.

## Interpretation rule

- Passing gates 1 and 4–7 supports the **kinematic ARA crosswalk**: one charged child projects to roughly one quarter of the parent budget while two distinct neutral children jointly carry the remaining roughly three quarters.
- Gate 3 never counts as independent evidence because the sum is forced.
- Failure of gate 2 means the digitised T392 reversal is near, but not statistically identical to, the exact `0.5` landmark under that interval.
- None of these gates establishes a pre-decay clock or deterministic neutrino-spawn time for an individual muon.

## Sources

- Particle Data Group, *Muon Decay Parameters*, 2025 update, especially the Standard-Model energy–angle spectrum.
- TWIST Collaboration charged-daughter energy–angle measurements used by T392.


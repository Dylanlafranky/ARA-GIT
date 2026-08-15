# T393 — Joint neutrino-pair projection findings

Date: 2026-08-15

## Result

The proposed child-to-parent projection is supported as a **kinematic ARA crosswalk**.

At the frozen T392 charged-daughter directional handover,

\[
x_e^*=0.49019,
\]

the charged child projects one rung upward to

\[
p_e={x_e^*\over2}=0.245095.
\]

That is `0.004905` below the proposed `0.25` parent landmark and passes the frozen approximate-quarter gate.

The neutral complement is a genuine two-child branch. Under the Standard-Model `V-A` decay weighting, its conditional mean decomposition is

\[
\langle x_{\nu_e}\rangle=0.693036,
\qquad
\langle x_{\bar\nu_\mu}\rangle=0.816774.
\]

Projected to the parent rung, the complete three-child reading is

\[
\boxed{
0.245095+0.346518+0.408387=1.000000
}.
\]

The joint neutral branch therefore contributes

\[
p_{\nu\nu}=0.754905.
\]

The sum to `1` is forced by energy conservation and is not counted as independent evidence. The informative result is that the two neutrino species divide the joint branch asymmetrically rather than behaving as one duplicated neutral packet.

## Neutral pair ARA

Normalising the two neutrino children to their own `0–2` identity gives

\[
x_{\nu_e\mid\nu\nu}=0.918044,
\qquad
x_{\bar\nu_\mu\mid\nu\nu}=1.081956.
\]

They straddle their pair ridge and close to `2`, but retain a signed identity difference. A label-shuffled or uniform phase-space control returns `(1,1)` instead.

At this handover slice, the anti-muon-neutrino branch is the higher-energy sibling in

\[
68.93\%
\]

of the `V-A` conditional distribution. A fixed-seed 400,000-event numerical reproduction agreed with both analytic means to `0.000173` child-coordinate units.

## What “balance” means here

There are two different balances and they must not be flattened together:

1. **Energy:** the charged daughter plus both neutrinos use the complete child budget `2`.
2. **Momentum:** in the stopped-muon rest frame, the vector sum of the two neutrino momenta is exactly opposite the charged-daughter momentum.

The second relation makes the two neutrinos one joint anti-phase branch relative to the charged daughter, while their unequal internal energy split shows that the branch still contains two identities.

This is structurally similar to the proposed reversed water analogy: one visible/charged branch is paired against a two-member neutral branch. It is not a chemical stoichiometric identity, and its `1:3` energy share near the handover is a gradient result rather than a universal particle-count rule.

## Exact-landmark qualification

The exact massless Standard-Model directional reversal is `x_e=0.5`, which would project to `0.25`. The frozen T392 digitisation interval was

\[
[0.48612,0.49446],
\]

so it does **not** include exact `0.5`. The result supports a near-quarter ARA landmark, not exact empirical equality under that interval.

At exact `x_e=0.5`, the analytic parent decomposition is

\[
0.25+0.34375+0.40625=1.
\]

## Claim boundary

T393 does not show that an individual muon reaches a hidden clock coordinate `0.25` before it decays. It shows that the already-observed charged-daughter handover projects to approximately one quarter of the parent energy scale and that the remaining three quarters decompose into two distinct, dynamically unequal neutrino children.

An individual timing claim still requires event-linked pre-decay muon state plus charged-daughter and neutrino-sensitive observables.

## Files

- Protocol: `T393_JOINT_NEUTRINO_PAIR_PROJECTION_PROTOCOL_2026-08-15.md`
- Analysis: `t393_joint_neutrino_pair_projection.py`
- Independent validator: `validate_t393_joint_neutrino_pair_projection.py`
- Results: `T393_joint_neutrino_pair_projection/T393_RESULTS.json`
- Component table: `T393_joint_neutrino_pair_projection/T393_COMPONENTS.csv`
- Cross-handover curve: `T393_joint_neutrino_pair_projection/T393_CURVE.csv`

## Sources

- Particle Data Group, *Muon Decay Parameters*, 2025 update.
- TWIST Collaboration, *New Experimental Constraints for the Standard Model from Muon Decay*.


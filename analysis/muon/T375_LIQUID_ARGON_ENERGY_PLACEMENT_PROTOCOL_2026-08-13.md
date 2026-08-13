# T375 — frozen liquid-argon energy-placement ladder

**Frozen:** 13 August 2026 (Australia/Brisbane), after T374 and before fitting
any intermediate energy-resolution level or energy-order control.

## Identity boundary

No medium or physical identity changes. T375 uses the same CENNS-10 liquid
argon, stopped-pion / stopped-muon source, CEvNS interaction, backgrounds and
3,752 released events as T373/T374.

T374 already exposed the two endpoint cuts:

- no energy resolution (`F90 × time`): central `x_H ≈ 2.0`;
- all 12 native energy bins (full 3D): central `x_H ≈ 1.239`.

Those endpoints are calibration facts and are not new T375 evidence. T375
freezes the uninspected intermediate ladder and its controls.

## Who / what / when / where / why / how

- **Who:** prompt pion-lineage and delayed muon-lineage CEvNS release branches
  inside one liquid-argon parent.
- **What:** the equality-handover ARA coordinate recovered as progressively
  more recoil-energy structure is restored.
- **When:** over the same ten native half-microsecond arrival-time bins.
- **Where:** nested cuts of the released `12 energy × 8 F90 × 10 time` cube.
- **Why:** T374 suggests that time preserves release order while energy supplies
  the additional relation needed to place the handover inside the parent. A
  real resolution effect should develop progressively rather than appearing
  only when the final 12-bin answer is supplied.
- **How:** group the native energy bins at predeclared boundaries, retain F90
  and time, and refit the same five non-negative physical components at every
  level.

## Frozen energy-resolution ladder

The released CEvNS template places about `61.5%`, `28.9%`, `7.7%`, `1.85%`
and `0.06%` in the first five 10-keVee bins. Without using event-fit outcomes,
freeze the following nested groups:

1. **1 group:** all energy bins summed;
2. **2 groups:** `0–10`, `10–120` keVee;
3. **3 groups:** `0–10`, `10–20`, `20–120` keVee;
4. **5 groups:** `0–10`, `10–20`, `20–30`, `30–40`, `40–120` keVee;
5. **12 groups:** all released 10-keVee bins retained.

At each level, profile the prompt share, calculate the best finite handover
coordinate and record the profile penalty at the frozen `x_H=1.25` share.

## Frozen primary gate

Let

\[
d_g=|x_H(g)-1.25|
\]

for energy resolution `g ∈ {1,2,3,5,12}`.

The progressive-placement prediction passes only when:

1. all five central handovers are finite;
2. Spearman correlation between `g` and `d_g` is at most `-0.80`;
3. at least three of the four successive refinements reduce `d_g`;
4. the previously uninspected `g=2,3,5` centres do not cross to the opposite
   side of the parent ridge (`x_H < 1`).

Because the `g=1` and `g=12` endpoints were known before freezing T375, a pass
supports only the *intermediate resolution mechanism*, not independent
confirmation of the endpoint or the universal `1.25` law.

## Frozen energy-order controls

For `g=3`, `g=5` and `g=12`, leave the observed data and every background
template fixed. Jointly permute the energy-group labels of the prompt and
delayed CEvNS templates, preserving their internal F90 × time shapes. Test the
reversed order plus 20 deterministic random non-identity permutations
(`seed=375`).

The order-control gate passes when, at all three resolutions:

1. native energy order fits better than the median permuted order; and
2. native order ranks in the best quarter of the 22 candidates (native,
   reversed and 20 random permutations).

This asks whether physical energy ordering carries information. It does not
claim that the detector energy axis is itself an ARA phase.

## Evidence boundary

- All ladder levels are correlated views of the same events.
- The endpoint trajectory was already visible in T374; only the intermediate
  steps and frozen permutations are new.
- Better localization may arise from ordinary signal/background separation.
  T375 tests the proposed relational role of that information but cannot by
  itself establish a new microscopic mechanism.
- A flat likelihood that permits `1.25` is not counted as locating `1.25`.
- A new same-identity event record is still required for prospective external
  confirmation.


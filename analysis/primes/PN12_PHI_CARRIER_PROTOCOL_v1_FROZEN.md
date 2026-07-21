# PN12 angular-carrier protocol — frozen before development and target calculation

**Test ID:** `PN12/PRIME-LADDER-ANGULAR-CARRIER/v1`  
**Declared:** 21 July 2026  
**Orientation:** up = add the next prime child; circular direction = increasing normalised next-child phase  
**Fidelity packet:** `PN12_PHI_CARRIER_FIDELITY_PACKET_v1.md`  
**Dylan verdict:** `EXACT ENOUGH TO TEST`

## Question

Does the canonical prime connection ladder produce a coherent, naturally measured angular carrier whose forward
rung-to-rung step prefers the golden angle `137.507764°`? Separately, does Dylan's pre-run `36°` pentagonal/shear
alternative satisfy the same fixed criteria?

## Raw mathematical object

For consecutive primes `p_1=2,p_2=3,...`, define

\[
B_m=\prod_{j=1}^{m}p_j,
\qquad q_m=p_{m+1},
\qquad u_m=(B_m\bmod q_m)/q_m,
\qquad \delta_m=(u_{m+1}-u_m)\bmod1.
\]

`u_m` is measured directly from integer residues. No transform, model fit or assigned angle enters it. The ARA display
coordinate, when needed, is `x_m=2u_m`; statistical circular calculations remain in turns.

## Rung ranges

- **Already inspected and excluded:** rungs `m=1..29`.
- **Development:** phase rungs `m=30..999`; increments beginning at `m=30..998`.
- **Fresh target:** phase rungs `m=1000..5000`; increments beginning at `m=1000..4999`.

The target is deterministic public mathematics rather than sampled empirical data. “Fresh” means uninspected before
the packet, method, ranges, landmarks and pass criteria were frozen; it is not an independent physical replication.

## Frozen landmarks

All angles are compared as circular turns:

| Name | Turns | Degrees | Role |
|---|---:|---:|---|
| golden angle | `1/phi^2` | `137.507764` | **primary signed horse** |
| 36-degree shear | `1/10` | `36` | **separate pre-registered secondary** |
| reverse golden | `1/phi` | `222.492236` | orientation sensitivity/rival |
| 1/e turn | `1/e` | `132.436599` | exponential null rival |
| 3/8 turn | `3/8` | `135` | crowded-neighbour rational rival |
| 2/5 turn | `2/5` | `144` | pentagram/rational rival |
| 1/5 turn | `1/5` | `72` | pentagon rival |
| 1/6 turn | `1/6` | `60` | hexagon rival |
| 1/4 turn | `1/4` | `90` | quadrant rival |
| 1/3 turn | `1/3` | `120` | triangle rival |
| 1/2 turn | `1/2` | `180` | anti-phase rival |
| zero turn | `0` | `0` | no-rotation rival |

The secondary 36° result is rated independently and cannot rescue the primary golden-angle result.

## Statistics

For target increments `delta_m`, compute:

1. circular mean direction;
2. mean resultant length `R = |mean(exp(2*pi*i*delta_m))|`;
3. mean and median circular distance to every frozen landmark;
4. 5th, 25th, 50th, 75th and 95th percentiles of both phase and increment;
5. fixed first/second target halves;
6. a deterministic 100-block bootstrap interval for
   `best_nonprimary_landmark_loss - golden_loss`;
7. the equivalent interval for `best_non36_landmark_loss - 36-degree_loss`;
8. 500 fixed-seed permutations of the phase order. This breaks ladder order while retaining the exact phase values;
9. synthetic exact-golden, exact-36° and uniform-phase instrument checks.

Circular distance is `min(|a-b|,1-|a-b|)`. Landmark ranking uses mean circular distance.

## Primary golden-angle criteria

All must pass:

- **G1 carrier coherence:** target `R >= 0.10` and exceeds the 99.5th percentile of permuted-order `R`.
- **G2 location:** golden angle ranks first by target mean circular distance and the 95% block-bootstrap interval for
  `best rival loss - golden loss` lies wholly above zero.
- **G3 direction:** circular mean direction is within `0.025` turns (`9°`) of `1/phi^2`.
- **G4 stability:** in both fixed halves, `R >= 0.075`, golden ranks first, and mean direction is within `0.04` turns
  (`14.4°`) of `1/phi^2`.

Verdict: `SUPPORTED [pre-registered fresh target]` only if G1–G4 pass; otherwise `NOT SUPPORTED`. Fewer than 1,000
increments or a failed arithmetic/instrument check yields `INCONCLUSIVE` or `IMPLEMENTATION FAILURE` as appropriate.

## Separate 36-degree criteria

Replace golden by `1/10` in G2–G4 while retaining the same coherence G1. Call these D1–D4. Rate separately as
`SUPPORTED`, `NOT SUPPORTED`, or `INCONCLUSIVE`. This is not a multiple-choice Phi success rule.

## Geometry output required regardless of verdict

- every target `m`, current prime, next prime, raw phase, ARA phase `2u`, observed increment and landmark distances;
- closest examples to all named landmarks;
- ten largest and smallest steps;
- phase and increment distributions plus fixed-half results;
- actual and shuffled/synthetic coherence;
- explicit separation of exact number-theory identities, confirmatory verdicts and post-hoc geometry.

## Falsifiers

- absence of measurable carrier coherence;
- another frozen landmark fits better than the signed primary;
- target mean direction misses the frozen angle;
- first/second-half reversal or loss of coherence.

## Scope fence

PN12 can test only the adjacent-next-child phase reading defined in the fidelity packet. It cannot refute Phi as a
spatial packing relation, handover timing in another system, a curved non-constant meta-wave, or the core recursive ARA
claim. Exact residue structure is established arithmetic and is not new ARA evidence by itself.


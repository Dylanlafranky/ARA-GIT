# PN12 prime-ladder angular carrier

**Date:** 21 July 2026  
**Orientation:** up = add the next prime child; positive circular direction = increasing next-child phase  
**Primary verdict:** `NOT SUPPORTED [PRE-REGISTERED FRESH TARGET]` — 137.507764° golden-angle carrier  
**Secondary verdict:** `NOT SUPPORTED [PRE-REGISTERED FRESH TARGET]` — 36° pentagonal/shear carrier  
**Geometry verdict:** `EXACT ADJACENT-CHILD PHASE; NO COHERENT ONE-ANGLE CARRIER IN THIS PROJECTION`  
**Target:** 4,000 upward steps from primorial rung 1,000 through rung 5,000  
**Independent algorithmic validation:** `22/22` checks pass

## Answer first

The prime ladder does supply a natural, unassigned circular coordinate: at each completed primorial rung, we can
measure where that parent lies on the cycle of the next prime child. That coordinate spans almost the whole circle and
is mathematically exact.

It does **not** advance as a coherent fixed-angle carrier in the tested reading. On the untouched target, the circular
coherence was only

\[
\underbrace{R}_{\substack{\text{how strongly all rung steps}\text{point in one circular direction}}}
=0.014186.
\]

`R=1` would be a perfectly repeated turn; a circularly unaligned population tends toward `R=0`. The observed value
was almost identical to the mean of order-scrambled controls (`0.013812`) and below their 95th percentile (`0.026210`).

The formal 137.5° golden-angle prediction failed. Dylan's separately registered 36° possibility also failed. Although
36° happened to have the smallest average distance among the frozen landmarks, its advantage over 0° was only
`0.000631` turns and its 95% block-bootstrap interval crossed zero. With almost no coherence, that ranking is the
nearest label on a nearly even circle, not a recovered 36° wave.

## 1. What was measured

At rung `m`, let

\[
\underbrace{B_m}_{\substack{\text{current completed}\text{prime connection lock}}}
=\prod_{j=1}^{m}p_j,
\qquad
\underbrace{q_m}_{\substack{\text{next prime child}\text{not yet incorporated}}}
=p_{m+1}.
\]

All children already inside `B_m` are exactly at zero phase because each divides the parent. The immediately adjacent
nontrivial phase is therefore

\[
\underbrace{u_m}_{\substack{\text{where the current lock lands}\text{on the next child's cycle}}}
=\frac{B_m\bmod q_m}{q_m}.
\]

The proposed larger-wave step is

\[
\underbrace{\delta_m}_{\substack{\text{upward angular movement}\text{from one rung to the next}}}
=(u_{m+1}-u_m)\bmod1.
\]

Plainly: finish one prime sphere, look at its position on the next incoming child's circle, climb one rung, and measure
how far that position turned. Phi was never inserted into `u_m` or `delta_m`; it was only a predicted landmark.

## 2. Frozen test

- rungs `1–29` had already been inspected and were excluded;
- development phases: rungs `30–999`, giving `969` steps;
- fresh target phases: rungs `1,000–5,000`, giving `4,000` steps;
- primary signed horse: `1/phi^2 = 0.381966 turns = 137.507764°`;
- separate pre-run hypothesis: `0.1 turns = 36°`;
- controls: `0°, 60°, 72°, 90°, 120°, 135°, 1/e turn, 144°, 180°`, and reverse golden;
- order control: 500 deterministic permutations of the exact target phases;
- stability: fixed target halves and 100-block bootstrap;
- instrument checks: exact synthetic golden and 36° carriers plus uniform random phases.

The code, protocol and fidelity packet matched their frozen hashes before the target was opened.

## 3. Development result

Development was already negative:

| Quantity | Development result |
|---|---:|
| steps | 969 |
| circular mean direction | 161.626905° |
| coherence `R` | 0.053129 |
| permutation 99.5th-percentile `R` | 0.079329 |
| golden rank | 3 of 12 |
| 36° rank | 11 of 12 |

No observable, target, angle, tolerance or pass direction was altered after seeing this.

## 4. Fresh-target geometry

### Raw phase and step coverage

| Statistic | next-child phase `u_m` | rung step `delta_m` |
|---|---:|---:|
| minimum | 0.000171 | 0.000126 |
| 5th percentile | 0.047189 | 0.048158 |
| 25th percentile | 0.248819 | 0.244049 |
| median | 0.503273 | 0.496427 |
| mean | 0.500386 | 0.499306 |
| 75th percentile | 0.747263 | 0.755560 |
| 95th percentile | 0.948590 | 0.948143 |
| maximum | 0.999846 | 0.999935 |

Both coordinates cover the circle broadly. Their means, medians and quartiles are close to those of an even circular
population. This is a descriptive observation, not a formal proof of uniform distribution.

### Carrier coherence

| Reading | `R` |
|---|---:|
| actual ordered target | 0.014186 |
| mean of 500 order permutations | 0.013812 |
| permutation 95th percentile | 0.026210 |
| permutation 99.5th percentile | 0.034153 |
| largest permutation | 0.043487 |

The ladder order does not produce more one-direction phase alignment than the same phase positions in scrambled order.

### Frozen-landmark comparison

| Rank | Landmark | Angle | Mean circular distance |
|---:|---|---:|---:|
| 1 | 36° shear | 36.000° | 0.246951 |
| 2 | zero turn | 0.000° | 0.247582 |
| 3 | hexagon | 60.000° | 0.247674 |
| 4 | pentagon | 72.000° | 0.248429 |
| 5 | quadrant | 90.000° | 0.249245 |
| 6 | triangle | 120.000° | 0.251008 |
| 7 | `1/e` turn | 132.437° | 0.251309 |
| 8 | `3/8` | 135.000° | 0.251411 |
| 9 | golden angle | 137.508° | 0.251530 |
| 10 | `2/5` | 144.000° | 0.251866 |
| 11 | anti-phase | 180.000° | 0.252418 |
| 12 | reverse golden | 222.492° | 0.253068 |

For a uniform circle the expected mean distance to **every** fixed landmark is `0.25`. All observed losses are within
about `0.0031` of that value. Therefore rank 1 does not by itself identify a preferred angle.

## 5. Registered verdicts

### Primary 137.507764° golden angle

All four criteria failed:

- coherence `R=0.014186` was below the required `0.10` and below permutation controls;
- golden angle ranked `9/12`, not first;
- circular mean direction was `16.134746°`, not within 9° of the golden angle;
- the two halves were incoherent (`R=0.021940` and `0.008603`) and their directions shifted from `2.985°` to
  `51.597°`.

The observed best-rival-minus-golden distance was `-0.004578` turns. Its 95% block-bootstrap interval was
`[-0.011984, 0.002851]`; negative favours the rival, while the interval also shows no stable discrimination.

**Verdict: `NOT SUPPORTED [PRE-REGISTERED FRESH TARGET]`.**

### Separate 36° alternative

Thirty-six degrees ranked first, but it also failed all four criteria:

- the shared carrier-coherence requirement failed;
- the mean direction was not within 9° of 36°;
- fixed halves did not maintain the required direction or coherence;
- its observed advantage over the next landmark, 0°, was only `0.000631` turns, with bootstrap interval
  `[-0.002229, 0.003530]`.

**Verdict: `NOT SUPPORTED [PRE-REGISTERED FRESH TARGET]`.**

Plainly: 36° was the nearest named mark, but the points were not marching at 36°. They were spread around the circle,
and the tiny ranking difference is compatible with sampling variation in that spread.

## 6. Instrument and arithmetic checks

- exact synthetic golden carrier: `R=1`, recovered direction `137.507764°`;
- exact synthetic 36° carrier: `R=1`, recovered direction `36°`;
- uniform-phase negative control: low coherence;
- every target residue satisfied `0 < B_m mod q_m < q_m`;
- all 4,001 phases and 4,000 increments were reproduced by a second algorithm using trial-division primes and direct
  modular products rather than the primary sieve and growing primorial;
- independent algorithmic validation: `22/22` checks passed.

## 7. What this means for the framework

This test is useful because it separates three statements:

1. **Exact:** the prime ladder is nested; each primorial lock contains all earlier prime children and the next child
   supplies a well-defined adjacent circular phase.
2. **Not supported here:** those adjacent phases do not form a one-angle 137.5° or 36° carrier as rungs are added.
3. **Still open but different:** a larger Phi wave could be curved, non-constant, live in the full multi-child residue
   torus, or use another independently justified observable. Any of those requires a new fidelity packet; PN12 cannot
   be silently reinterpreted as them.

The result therefore does not damage the exact bottom-up prime sieve, PN11's logarithmic lock/echo decomposition, or
the general recursive ARA claim. It removes one attractive but overly simple way of placing a large Phi carrier above
the prime ladder.

## 8. Post-result probe — Pi leak as a one-thruster residual

**Status:** `POST-HOC USER MUSING TESTED ON THE OPEN PN12 TARGET / NOT SUPPORTED IN THIS READING.`

After seeing `R=0.01419`, Dylan proposed:

> “This number has come up before I think as part of potential Pi-leak. I wonder if it is the leak, and that is
> propelling the circle pattern forward, like a rocket with only one working thruster.”

The rocket analogy gives a clean mathematical discriminator. Define the signed mean step vector

\[
\underbrace{\bar{\mathbf v}_N}_{\substack{\text{net directional remainder}\
\text{after }N\text{ circular steps}}}
=\frac1N\sum_{m=1}^N
\left(\cos(2\pi\delta_m),\sin(2\pi\delta_m)\right),
\qquad
\underbrace{R_N}_{\text{reported magnitude}}=\left|\bar{\mathbf v}_N\right|.
\]

A persistent one-thruster effect predicts `R_N -> r_* > 0` and a stable vector direction. Unaligned circular steps
predict `R_N` shrinking approximately as `1/sqrt(N)`. For independent uniform directions the expected finite-sample
magnitude is approximately

\[
E[R_N]\approx\frac{\sqrt\pi}{2\sqrt N}.
\]

At `N=4,000`, this null expectation is `0.0140125`; PN12 measured `0.0141862`. Equivalently,
`R*sqrt(N)=0.8972`, very near the null coefficient `sqrt(pi)/2=0.8862`.

| Prefix steps `N` | measured `R_N` | random-direction expectation | direction |
|---:|---:|---:|---:|
| 125 | 0.099400 | 0.079267 | 21.69° |
| 250 | 0.071832 | 0.056050 | 51.11° |
| 500 | 0.059428 | 0.039633 | 326.03° |
| 1,000 | 0.029101 | 0.028025 | 331.07° |
| 2,000 | 0.021940 | 0.019817 | 2.98° |
| 4,000 | 0.014186 | 0.014012 | 16.13° |

Disjoint blocks also point in widely different directions. The second 2,000-step half has `R=0.008603` and direction
`51.60°`; 1,000-step blocks point near `331.07°`, `41.72°`, `208.00°` and `42.34°`. Thus there is no stable thrust
direction.

The repository's previously defined Pi-leak quantities are different:

| Pi-leak expression | Value | Existing use |
|---|---:|---|
| `pi-3` | 0.141592654 | proposed topology/non-closure strand |
| `(pi-3)/pi` | 0.045070341 | proposed normalised energy leakage |
| `(pi-3)/10` | 0.014159265 | numerically close to PN12, but `/10` was not a registered bridge |

PN12 differs from `(pi-3)/10` by about `0.000027`, but introducing division by ten after seeing the result would be
constant hunting. A separate PN10B geometry report also contained a mean child-coupling value `-0.01407585`; that is
a signed average of adjacent child products, not a circular resultant, and late composites showed a similar
`-0.01514929`. The shared decimal scale does not make the observables equivalent.

**Post-hoc verdict:** PN12's `0.01419` is quantitatively explained by the finite-sample length of an almost cancelled
circular vector. It is not current evidence of a Pi leak or propulsion. A fresh thrust test would need to freeze a
signed direction and predict that `R_N` plateaus rather than decays as `1/sqrt(N)` on later, untouched rung blocks.

## 9. Reproduction

- fidelity: `analysis/primes/PN12_PHI_CARRIER_FIDELITY_PACKET_v1.md`
- frozen protocol: `analysis/primes/PN12_PHI_CARRIER_PROTOCOL_v1_FROZEN.md`
- target freeze: `analysis/primes/PN12_TARGET_FREEZE_MANIFEST.json`
- primary script: `analysis/primes/pn12_prime_ladder_phi_carrier.py`
- development: `analysis/primes/PN12_DEVELOPMENT_RESULTS.json` and `PN12_DEVELOPMENT_STEPS.csv`
- target: `analysis/primes/PN12_TARGET_RESULTS.json` and `PN12_TARGET_STEPS.csv`
- validator: `analysis/primes/validate_pn12_prime_ladder_phi_carrier.py`
- validation: `analysis/primes/PN12_PHI_CARRIER_VALIDATION.json`

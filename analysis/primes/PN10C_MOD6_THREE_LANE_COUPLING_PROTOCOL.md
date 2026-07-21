# PN10C mod-6 three-lane coupling diagnostic protocol

**Test ID:** `PN10C/MOD6-THREE-LANE/POST-HOC-DIAGNOSTIC/v1`  
**Declared:** 20 July 2026, before calculating any PN10C lane-conditioned result  
**Evidence tier:** post-hoc structural diagnostic on an already-open interval  
**Registered PN10B verdict:** remains `NULL`; PN10C cannot change it

## Question

The PN10B event-centred parent trace contains three visible even-offset families. Dylan marked the two smaller interleaved families as a Phase A/Phase B pair and the larger family as a third, directly coupled wave. This diagnostic asks whether that visual decomposition corresponds to a reproducible arithmetic structure.

## Fixed data and coordinate

- Integer interval: `[4,000,000,000, 4,001,000,000)`.
- Event centres: all primes far enough from the interval boundaries for a `+-150` offset window.
- Matched control centres: composites coprime to 6, sampled deterministically to match the counts of the two centre orientations.
- Primary response at integer `n`:

  - `1.0` if `n` is prime;
  - `2 log(LPF(n)) / log(n)` if `n` is composite, where `LPF` is the least prime factor.

- Supporting responses: prime rate, `c=.90` survivor rate, and divisibility by 3 and 5.
- Centre orientation: `p mod 6` in `{1,5}`.
- Even-offset lane: `k mod 6` in `{0,2,4}`. Odd offsets are retained only as the parity-background control.
- Black-lane child coordinate: for `k=6m`, `m mod 5` in `{0,1,2,3,4}`, equivalently `k mod 30` in `{0,6,12,18,24}`.

## Frozen predictions

### P1 — red/blue role exchange

For centres `p=1 mod 6`, offsets `k=2 mod 6` land on multiples of 3 and should be suppressed, while `k=4 mod 6` remains admissible. For centres `p=5 mod 6`, the roles reverse. Define

`swap = 0.5 * [(M(1,4)-M(1,2)) + (M(5,2)-M(5,4))]`.

Prediction: `swap > 0`, with a 95% block-bootstrap interval excluding zero.

### P2 — phase-reflection symmetry

The event trace for `p=1 mod 6` should approximately match the reflected trace for `p=5 mod 6`: `T_1(k) ~= T_5(-k)`. Its mean absolute error should be smaller than the unreflected comparison `T_1(k) ~= T_5(k)`.

### P3 — black common-lane invariance

For `k=0 mod 6`, both centre orientations remain coprime to 6. The black-lane mean difference `M(1,0)-M(5,0)` should be small relative to `swap`, and its bootstrap interval may include zero.

### P4 — independent-third-wave discriminator

Before orientation conditioning, the black lane should exceed the pooled red/blue lanes because it never collides with the factor 3. After conditioning, compare black with the currently admissible coloured branch:

- `p=1`: black versus `k=4 mod 6`;
- `p=5`: black versus `k=2 mod 6`.

If black still exceeds the admissible coloured branch by a material and robust amount, the trace supports a distinct third lane at this grain. If they become similar, black is better described as the shared/common admissible lane and the three visible aggregate families arise from two conditional orientations plus their invariant route.

No numeric materiality threshold is used to manufacture a pass. The report will give the raw difference, bootstrap interval, standardized difference, and full profiles.

### P5 — `6 -> 30` child decomposition

Inside the black lane, `6=1 mod 5`. Therefore the child lane `m mod 5` satisfying `(p mod 5 + m mod 5) mod 5 = 0` must collide with factor 5. It should have zero prime rate and parent progress near `2 log(5)/log(n)`. The other child lanes remain eligible past factor 5.

Prediction: the centre-`mod 5` by child-lane matrix contains one rotating suppressed cell in each centre row, and the suppressed-cell mean is lower than the eligible-cell mean with a 95% block-bootstrap interval excluding zero.

## Controls and robustness checks

1. Repeat the lane summaries around matched coprime composite centres. This identifies structure created by modular arithmetic generally rather than by prime centres specifically.
2. Verify exact divisibility identities for factors 3 and 5; any violation is a calculation failure.
3. Report positive and negative offsets separately as well as pooled by residue class.
4. Use a deterministic seed (`20260720`) and 2,000 block-bootstrap draws over 100 contiguous centre blocks.
5. Recompute headline contrasts independently in a separate validation script.
6. Preserve the full offset profiles and selected worked examples; do not reduce the outcome to a pass/fail label.

## Interpretation boundary

This diagnostic can establish whether Dylan's three marked families correspond to a real, hierarchical mod-6/mod-30 structure and whether the two coloured families behave as a conditional anti-phase pair. It cannot establish a new law of primes, a physical wave ontology, causal coupling, or prospective predictive advantage. The modular mechanism is established arithmetic; ARA's contribution here is the proposed multiscale relational decomposition and its vocabulary.

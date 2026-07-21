# PN11 Phi vertical handover through prime resonance families

**Date:** 21 July 2026  
**Registered verdict:** `NOT SUPPORTED [PRE-REGISTERED FRESH TARGET]`  
**Geometry verdict:** `EXACT TWO-SHARE/RUNG-RESET CROSSWALK; PHI IS NOT THE TRANSITION LANDMARK`  
**Target:** every eligible fundamental base in `[10,000,000,11,000,000)`  
**Primary population:** `45,768` resonance families  
**Independent validation:** `26/26` checks pass

## Answer first

The proposed Phase-A/Phase-B mathematics works exactly:

\[
\underbrace{A_B(k)}_{\text{existing child lock}}
+
\underbrace{E_B(k)}_{\text{harmonic-repeat echo}}
=2.
\]

The information-lock progression also works exactly: every multiplier before the smallest absent prime preserves the
old child set, and multiplying by that missing prime creates a larger squarefree fundamental lock.

The registered **Phi preference does not survive the fresh test**. New-child incorporations were centred far above
Phi, near the old `2` pole. Phi ranked sixth of eight frozen landmarks by mean event distance. No target family path
reached Phi before its first child-set expansion, and the frozen Phi window contained zero exposures and zero
transition events.

This is a negative result for one precise claim: **first new-child incorporation is not generally the Phi handover in
the prime resonance-family coordinate tested here.** It does not reject every possible meaning of vertical Phi
handover or the exact resonance decomposition.

## 1. Frozen translation

Dylan's prior was:

> “I think it is travelling vertically up the rungs via Phi based on resonance and harmonic repeat, maybe as a phase
> a and phase b. It supports its progress by creating information lock structures.”

The accepted v1 translation took one fundamental full resonance `B`, followed its integer multiples, and called the
first addition of a previously absent prime child the vertical handover. The old child lock and repeat echo were kept
as separate coordinates. Assigned musical notes were prohibited from the test.

The development range was `[5,000,1,000,000)`. The source, target, landmarks and criteria were hashed before opening
the fresh target `[10,000,000,11,000,000)`. Two development-only protocol amendments repaired an out-of-support
hazard rule and prevented missing secondary data from hiding a clean primary failure. Neither amendment changed the
target, Phi, rivals, coordinate, family definition or pass direction.

## 2. Exact family mathematics

Let `B` be squarefree, contain at least three independently active prime children, and equal the product of those
children. Let `q(B)` be the smallest prime not already dividing `B`.

Every integer smaller than `q` contains only prime factors already present in `B`. Therefore:

- `kB` for `1<=k<q` preserves the same distinct child set;
- `qB` adds exactly the new child `q`;
- because `B` is squarefree and `q` is absent, `qB` is a new fundamental full resonance.

At multiplier `k`, define

\[
\underbrace{A_B(k)}_{\substack{\text{old-lock share}\\\text{Phase A}}}
=\frac{2\log B}{\log(kB)},
\qquad
\underbrace{E_B(k)}_{\substack{\text{repeat share}\\\text{Phase B}}}
=\frac{2\log k}{\log(kB)}.
\]

Then

\[
A_B(k)+E_B(k)
=\frac{2(\log B+\log k)}{\log(kB)}
=2.
\]

At the expansion event `k=q`, the old lock occupies

\[
\boxed{
X_B
=A_B(q)
=\frac{2\log B}{\log B+\log q}
=\frac{2}{1+\log q/\log B}
}.
\]

The enlarged identity `qB`, when used as the new base, resets to `(A,E)=(2,0)`.

**Plainly:** repetition gradually transfers share away from the old child skeleton. The first absent prime then joins
and creates a larger complete skeleton. This part of the proposed geometry is an exact description of multiplication
and prime-factor inclusion.

## 3. What would make the expansion occur at Phi?

Solving `X_B=phi` gives

\[
\frac{\log q}{\log B}
=\frac{2}{\phi}-1
=\frac{1}{\phi^3}
\approx0.2360679775,
\]

or equivalently

\[
\boxed{q=B^{1/\phi^3}}.
\]

This is a demanding scaling condition. Near the target scale `B=10^7`, Phi would require approximately

\[
q\approx(10^7)^{1/\phi^3}\approx44.92.
\]

The actual first missing children in the target were only `3,5,7,11,13,17`, with median `q=3`. Therefore
`log(q)/log(B)` was much smaller than the Phi condition, placing the expansion close to `2`.

As `B` increases while `q` stays small,

\[
X_B\longrightarrow2.
\]

This supplies an analytic explanation for the failed constant-Phi hypothesis and for the upward scale drift seen
from development to target.

## 4. Registered target result

### Exact geometry — P1 passes

- eligible primary families: `45,768`;
- maximum `|A+E-2|`: `4.44e-16`;
- pure-repeat child-set violations: `0`;
- first-expansion violations: `0`;
- every expanded node adds exactly its declared smallest missing prime and forms a new fundamental lock.

### Event location — P2 fails

The target event-coordinate distribution was:

| Statistic | `X_B` |
|---|---:|
| minimum | 1.701189 |
| 5th percentile | 1.785381 |
| median | 1.872585 |
| mean | 1.853770 |
| 95th percentile | 1.873033 |
| maximum | 1.873081 |

Frozen-landmark comparison:

| Landmark | Mean absolute event distance | Rank | Events within `+-0.025` |
|---|---:|---:|---:|
| `9/5 = 1.8` | 0.056714 | 1 | 13,317 |
| `7/4 = 1.75` | 0.103990 | 2 | 510 |
| `2` | 0.146230 | 3 | 0 |
| `5/3` | 0.187104 | 4 | 0 |
| `13/8` | 0.228770 | 5 | 0 |
| `phi` | 0.235736 | 6 | 0 |
| `8/5` | 0.253770 | 7 | 0 |
| `3/2` | 0.353770 | 8 | 0 |

The paired quantity `best-rival loss - Phi loss` was

\[
-0.179022276,
\]

with frozen 100-block bootstrap interval

\[
[-0.179104989,-0.178939388].
\]

Negative means Phi was decisively farther from the expansion events than `9/5`.

### Transition hazard — P3 is underpopulated at Phi

The `phi+-0.025` window contained **zero path exposures and zero expansion events**. The two adequately populated
target windows were:

| Landmark | Exposures | Events | Transition hazard |
|---|---:|---:|---:|
| `9/5` | 19,782 | 13,317 | 0.673188 |
| `7/4` | 2,138 | 510 | 0.238541 |

Therefore P3 cannot produce an adequate Phi hazard estimate. Under the frozen v3 rating order, that absence cannot
conceal the already decisive P2 failure.

### Split halves — P4 fails

Phi ranked sixth by distance in both fixed target halves. The best-rival-minus-Phi mean-distance differences were:

- first half: `-0.178956359`;
- second half: `-0.179088061`.

The negative direction is stable.

## 5. Required sensitivities

### Including immediate `q=2` expansions

The primary excluded `q=2` because those families have no nontrivial harmonic repeat before expansion. Including
them increases the population to `121,802`, moves the median event coordinate to `1.917635`, and moves the mean to
`1.893724`. Phi remains rank six. Thus the exclusion was favourable to Phi rather than responsible for its failure.

### First-missing-child strata

| First missing child `q` | Families | Mean event coordinate | Phi mean distance |
|---:|---:|---:|---:|
| 2 | 76,034 | 1.917774 | 0.299740 |
| 3 | 31,936 | 1.872736 | 0.254702 |
| 5 | 10,857 | 1.818921 | 0.200887 |
| 7 | 2,460 | 1.785124 | 0.167090 |
| 11 | 476 | 1.741665 | 0.123631 |
| 13 | 34 | 1.726119 | 0.108085 |
| 17 | 5 | 1.701736 | 0.083702 |

The gradient is real: larger first-missing children move the event farther from `2` and toward Phi. But the governing
quantity is the continuous ratio `log(q)/log(B)`, not a constant Phi gate.

### Canonical primorial-prefix ladder

| Base lock | Next child | Expansion coordinate |
|---:|---:|---:|
| 30 | 7 | 1.272163 |
| 210 | 11 | 1.380789 |
| 2,310 | 13 | 1.502432 |
| 30,030 | 17 | 1.568869 |
| 510,510 | 19 | 1.633949 |
| 9,699,690 | 23 | 1.673778 |

This special ladder passes from below Phi to above it between the 30,030 and 510,510 locks. That crossing is exact
geometry, but the closest listed event is still not exactly Phi, and a monotone ladder crossing an interior landmark
does not establish that the landmark drives the transition.

## 6. The 510 worked example

For the previously noticed family `B=510`, the old-lock coordinates are:

| Multiplier `k` | Node | Old-lock share | Echo share |
|---:|---:|---:|---:|
| 1 | 510 | 2.000000 | 0.000000 |
| 2 | 1,020 | 1.799887 | 0.200113 |
| 3 | 1,530 | 1.700366 | 0.299634 |
| 4 | 2,040 | 1.636177 | 0.363823 |
| 5 | 2,550 | 1.589631 | 0.410369 |
| 6 | 3,060 | 1.553521 | 0.446479 |
| 7 | 3,570 | 1.524246 | 0.475754 |

The path really does cross Phi between multipliers 4 and 5. The new child 7 does not join until multiplier 7, when
the old lock is at `1.524246`. This is why “the path crossed Phi” and “Phi located the new lock” must remain separate
claims.

## 7. Geometry verdict

PN11 found a clean ARA-compatible decomposition:

\[
\text{fundamental lock}
\rightarrow
\text{harmonic repeat path}
\rightarrow
\text{new-child expansion}
\rightarrow
\text{larger fundamental lock}.
\]

The two shares are reversible and close at `2`; the expanded lock genuinely contains the old factor identity plus one
new child. This is a precise number-theory example of nested identities and rung reset.

The location of the expansion is not fixed. It is

\[
X_B=\frac{2}{1+\log q/\log B},
\]

so the event is relational to both base scale and the next missing child. That may be closer to the framework's
general insistence on direction and local identity than a universal constant location would have been.

## 8. Claim verdict and scope

**Registered verdict: `NOT SUPPORTED`.** In this exact operationalisation, prime resonance families do not generally
travel to Phi before forming their next information lock, and their first child expansion is not preferentially at
Phi.

What survives:

- exact Phase-A/Phase-B logarithmic closure;
- exact harmonic-repeat lineage;
- exact new-child information-lock formation;
- a scale-dependent movement governed by `log(q)/log(B)`;
- isolated Phi crossings in particular finite lineages, including the 510 repeat path and the primorial ladder.

What does not survive:

- Phi as the universal first-expansion landmark;
- treating the 510 crossing as representative of larger prime families;
- treating eventual passage through Phi as evidence of a preferred handover.

An alternative Phi claim must identify a different observable or lineage **before** calculation. PN11 cannot be
relabelled after the result.

## 9. Reproduction

- Fidelity packet: `analysis/primes/PN11_PHI_VERTICAL_HANDOVER_FIDELITY_PACKET_v1.md`
- Original protocol: `analysis/primes/PN11_PHI_VERTICAL_HANDOVER_PROTOCOL.md`
- Final target amendments: `analysis/primes/PN11_PHI_VERTICAL_HANDOVER_PROTOCOL_v2_FROZEN.md` and
  `analysis/primes/PN11_PHI_VERTICAL_HANDOVER_PROTOCOL_v3_TARGET_FREEZE.md`
- Target freeze: `analysis/primes/PN11_TARGET_FREEZE_MANIFEST.json`
- Primary script: `analysis/primes/pn11_phi_vertical_handover.py`
- Development result: `analysis/primes/PN11_DEVELOPMENT_RESULTS.json`
- Target result: `analysis/primes/PN11_TARGET_RESULTS.json`
- Target event record: `analysis/primes/PN11_TARGET_EVENTS.csv`
- Landmark table: `analysis/primes/PN11_TARGET_LANDMARKS.csv`
- Required sensitivity: `analysis/primes/PN11_TARGET_SENSITIVITY.json`
- Stratum table: `analysis/primes/PN11_TARGET_BY_Q.csv`
- Independent validator: `analysis/primes/validate_pn11_phi_vertical_handover.py`
- Validation output: `analysis/primes/PN11_PHI_VERTICAL_HANDOVER_VALIDATION.json`


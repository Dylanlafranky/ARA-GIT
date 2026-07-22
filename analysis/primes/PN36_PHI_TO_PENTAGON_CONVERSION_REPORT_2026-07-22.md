# PN36 report: Phi carrier to pentagonal structure

**Date:** 22 July 2026  
**Frozen verdict:** **NOT SUPPORTED**  
**Test ID:** `PN36/PHI-TO-PENTAGON-CONVERSION/v1`

## Plain-language result

We tested the exact picture noticed after PN35: a continuous Phi-paced carrier moves through the prime wheel, then
snaps to the nearest one of five structural positions. If that conversion marks prime locations, primes should sit
closer to the converted crossings than composites do, consistently across untouched scales.

They did not. The converted fivefold state behaved like chance. It also did not outperform its raw Phi input, a
direct pentagon, a direct 36-degree path, or other polygonal conversions. This means the striking PN35 visual order
has **not** turned into predictive evidence for a Phi-time to pentagonal-structure conversion under this explicit
operator.

## Registered endpoints

| Endpoint | Frozen target | Result | Status |
|---|---:|---:|---|
| Lane-stratified `C5(Phi)` AUC | `>0.5`, CI wholly `>0.5`, shift `p<=0.01` | `0.499851`, CI `[0.496091,0.503393]`, `p=0.5953` | Fail |
| Nearest-two prime capture | `>25%`, CI wholly `>25%`, shift `p<=0.01` | `24.8858%`, CI `[24.4346%,25.3741%]`, `p=0.7198` | Fail |
| Scale transfer | all pairs, 5/6 rungs, both halves `>0.5` | 1/3 pairs, 3/6 rungs, 1/2 halves | Fail |
| Conversion specificity | beat every frozen rival, positive difference CI | best rival `C4(Phi)=0.502885`; difference CI `[-0.006622,0.000813]` | Fail |
| Singularity flip | beat no-flip, positive difference CI | no-flip `0.503772`; difference CI `[-0.007411,-0.000566]` | Fail |

All five support gates failed, so the frozen verdict is **NOT SUPPORTED**.

## What was frozen before labels

The eight exact modulo-30 survivor lanes were placed on one unit-turn circle, equivalent to the ARA `0-2`
circumference. In each complete cell,

\[
\theta_\phi(t)=\left((-1)^k\frac{t}{\phi^2}\right)\bmod1
\]

was converted to the nearest fivefold vertex,

\[
C_5(\theta)=\frac{\lfloor5\theta+1/2\rfloor\bmod5}{5}.
\]

The output vertex and its half-turn anti-phase were the two crossings. This nearest-vertex operator was Sol's
minimal mathematical translation of Dylan's conversion observation; it was explicitly labelled as an AI addition,
not treated as an established ARA axiom.

The primary stage sealed `196,608` candidate scores from `24,576` complete cells across untouched rungs
`k={28,29,38,39,48,49}`. Its file hash was fixed before deterministic primality labels were opened.

## Model comparison

| Frozen model | Lane-stratified AUC |
|---|---:|
| Fivefold conversion without octave flip | `0.503772` |
| Fourfold conversion of Phi | `0.502885` |
| Eightfold conversion of Phi | `0.501330` |
| Direct pentagon | `0.501118` |
| Raw Phi | `0.501041` |
| Sevenfold conversion of Phi | `0.500142` |
| **Fivefold conversion of Phi** | **`0.499851`** |
| Sixfold conversion of Phi | `0.499776` |
| Direct 36 degrees | `0.499547` |
| Threefold conversion of Phi | `0.499068` |

These values are tightly clustered around `0.5`. The converted-five point estimate lies inside the circular-shift
null range `[0.495463,0.505002]`. The higher no-flip and fourfold values were rivals, not registered positive
predictions; the test does not promote them into discoveries. In particular, no-flip was not subjected to its own
independent positive protocol.

## Transfer detail

| Rung | `C5(Phi)` AUC | No-flip AUC | Nearest-two capture |
|---:|---:|---:|---:|
| 28 | `0.500952` | `0.500952` | `25.1258%` |
| 29 | `0.493545` | `0.504610` | `24.4143%` |
| 38 | `0.506310` | `0.506310` | `25.4465%` |
| 39 | `0.499417` | `0.502622` | `24.9235%` |
| 48 | `0.500476` | `0.500476` | `24.2334%` |
| 49 | `0.499101` | `0.508058` | `25.1593%` |

Pair AUCs were `0.497273`, `0.502833` and `0.499786`. Fixed-half AUCs were `0.501360` and `0.498294`. The
direction therefore did not transfer reliably across either adjacent rungs or fixed halves.

The descriptive association between proximity to a fivefold carrier-sector boundary and the number of primes in a
cell was `-0.0090` after rung standardisation. Individual rung correlations ranged from about `-0.0235` to `+0.0172`.
This is also consistent with no boundary concentration.

## Validation

- The frozen protocol and both scripts were verified against their SHA-256 manifest before execution.
- The label-free primary produced the declared `196,608` rows and was hashed before labels were opened.
- Every sealed converted distance was reconstructed after opening labels.
- Deterministic 64-bit Miller-Rabin labels agreed with independent trial division on 18 scale-spanning spots.
- A planted nearest-two signal returned AUC `1.0`; an independent synthetic null returned `0.4981`.
- Whole-cell bootstraps preserved the complete eight-lane identity; circular shifts preserved every label, lane and
  score distribution while breaking the registered alignment.

## Scientific interpretation

PN36 cleanly separates three statements:

1. **Established geometry:** a regular pentagon and golden-ratio relations are mathematically connected.
2. **Constructed conversion:** `C5` really does turn a continuous Phi phase into a five-state structural sequence;
   that behavior follows from the definition.
3. **Empirical prime claim:** the resulting state does not preferentially locate primes in this representation.

The test therefore rules out this particular nearest-vertex bridge as a prime locator on the tested rungs. It does
not prove that no Phi-to-fivefold conversion can exist in another physical system, nor that every possible ARA
operator has failed. A different operator would be a new hypothesis and must be defined from independent geometry,
not tuned to these labels.

## Recommended handling

Close this branch as an honest null and keep the descriptive conversion observation in the record. The prime thread
has now done useful work: it recovered exact wheel/sieve structure, exposed valid density/rank-budget crosswalks,
and rejected several tempting but non-predictive bridges. Further prime work should wait for a genuinely new,
independently specified observable rather than another phase, sector or origin adjustment on the same data.


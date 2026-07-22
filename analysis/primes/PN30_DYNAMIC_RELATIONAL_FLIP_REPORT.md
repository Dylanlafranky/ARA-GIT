# PN30 dynamic relational flip ridge - result

**Date:** 22 July 2026  
**Status:** **child-filter support only; unresolved-control improvement was suggestive but not significant**  
**Scope:** 500 odd integers from 1001 through 1999; no sieve

## Answer first

Restoring the ARA singularity flip changed the child coordinate in exactly the intended mathematical way: it reversed a pair's signed displacement around the 1.0 ridge while preserving that pair's distance from the ridge.

On a fresh interval, the dynamic coordinate strongly separated primes from all odd composites:

- AUC: **0.7839**;
- mean upper-rung distance: primes **0.07595**, composites **0.14532**;
- one-sided permutation: **p=0.00010**.

The harder comparison is against composites that, like primes, evade all declared child divisors `{3,5,9,11,13}`. There the dynamic coordinate improved over the static PN29 coordinate:

\[
\mathrm{AUC}_{\rm static}=0.5301
\quad\longrightarrow\quad
\mathrm{AUC}_{\rm flip}=0.5663.
\]

However, the frozen one-sided permutation result was

\[
p=0.06199,
\]

which missed the predeclared \(p<0.05\) threshold. The result is therefore a **promising directional improvement**, not reliable prime-specific evidence.

## The corrected flip rule

For each wave \(w\), PN30 calculated its normalized progress through its current cycle:

\[
\theta_w(N)=\frac{N\bmod w}{w}.
\]

Within each unordered child pair `{1,13}`, `{3,11}`, `{5,9}`, the child with smaller \(\theta\) was assigned Phase A because it had crossed its singularity more recently in relational cycle units. The other became Phase B. When the partner crossed, the pair reversed orientation.

For example:

| Number | `{3,11}` | `{5,9}` |
|---:|---|---|
| 35 | `11 -> 3` | `5 -> 9` |
| 36 | `3 -> 11` | `9 -> 5` |
| 45 | `3 -> 11` | synchronized crossing |

The pair coordinate remained

\[
x_{A\to B}=\frac{2u_B}{u_A+u_B}.
\]

Consequently,

\[
x_{B\to A}=2-x_{A\to B}.
\]

The flip does not invent a new magnitude. It retains which side of the ridge the child relation occupies.

## Frozen test firewall

1. The dynamic and static coordinates were generated for all 500 odd integers from 1001 through 1999.
2. The coordinate generator contained no primality routine.
3. The coordinate CSV was frozen at SHA-256 `B0688149B1F87BACAE3D00EE985F6A1ADA5A524ABD35FC9117038D18B4E72636`.
4. Only after that freeze were prime labels calculated independently by direct trial division.
5. No sieve was used.

The population contained 135 primes, 365 odd composites, and 90 unresolved composites.

## Primary results

| Coordinate and comparison | Prime mean distance | Composite mean distance | AUC |
|---|---:|---:|---:|
| Dynamic vs all odd composites | 0.075951 | 0.145321 | **0.783886** |
| Dynamic vs unresolved composites | 0.075951 | 0.086771 | **0.566255** |
| Static vs all odd composites | 0.008932 | 0.084242 | **0.867702** |
| Static vs unresolved composites | 0.008932 | 0.008993 | **0.530123** |

The dynamic-minus-static AUC changes were:

\[
\Delta\mathrm{AUC}_{\rm overall}=-0.08382,
\qquad
\Delta\mathrm{AUC}_{\rm unresolved}=+0.03613.
\]

This tradeoff is coherent. Static orientation remains an efficient small-divisor screen, so it performs better against the easy overall composite population. Dynamic orientation deliberately restores AB/BA direction, which weakens that blunt screen but adds some separation inside the harder group that already survives the declared child divisors.

## Where the unresolved improvement came from

The following analysis was performed after labels were visible and is therefore descriptive, not a frozen endpoint.

For primes and unresolved composites, the mean absolute distance of each individual child pair was nearly identical:

| Pair | Prime mean absolute distance | Unresolved-composite mean | Pair AUC |
|---|---:|---:|---:|
| `{1,13}` | 0.96433 | 0.96506 | 0.5301 |
| `{3,11}` | 0.57143 | 0.57143 | 0.5574 |
| `{5,9}` | 0.28571 | 0.28571 | 0.5019 |

Therefore the gain was not produced by a new single-child magnitude. It came from how the three signed displacements cancelled when combined.

Define the descriptive signed-cancellation fraction as

\[
C=1-\frac{|\text{mean signed pair displacement}|}
{\text{mean absolute pair displacement}}.
\]

Its results were:

| Population | Mean cancellation | Median cancellation |
|---|---:|---:|
| Primes | **0.4996** | **0.6250** |
| Unresolved composites | 0.4285 | 0.3146 |

Plainly: the child-pair magnitudes looked almost the same, but their **orientations cancelled more completely at prime nodes** in this sample. That is precisely the kind of ordered AB/BA information PN29 could not retain. Because this decomposition was inspected after scoring, it is a post-hoc candidate mechanism requiring frozen replication, not a confirmed law.

## Interpretation

PN30 supports three narrow statements:

1. The normalized remainder supplies a precise, scale-comparable definition of which child most recently crossed its singularity.
2. Reversing AB to BA is mathematically visible as reflection around the pair ridge: \(x\mapsto2-x\).
3. Retaining those directions improved the difficult unresolved-composite AUC by **0.0361** on fresh data.

PN30 does **not** support these larger statements:

- that the six declared child waves identify primes by themselves;
- that the dynamic coordinate generates or certifies a prime;
- that the residual improvement has replicated or reached the frozen significance threshold;
- that the three-pair scalar replaces the complete lower-factor state.

The most useful result is methodological: in this domain, flattening child orientations destroys relational information. The next defensible test, if the prime thread is resumed later, is a frozen replication of the signed-cancellation mechanism on another untouched small interval. It should not be tuned further on 1001-1999.

PN30 does not generate or certify primes.

**Follow-up:** PN31 subsequently removed wave `1`, abandoned fixed pairs and retained five independent child orders.
The closest child was null, while the complete five-wave ordering passed one fresh frozen distribution test (`p=0.00390`). See
`PN31_FIVE_INDEPENDENT_HANDOVER_REPORT.md`.

## Audit trail

- Frozen protocol: `PN30_DYNAMIC_RELATIONAL_FLIP_PROTOCOL_v1_FROZEN.md`
- Protocol manifest: `PN30_PROTOCOL_FREEZE_MANIFEST.json`
- Frozen unlabeled coordinates: `PN30_DYNAMIC_RELATIONAL_FLIP_FROZEN_COORDINATES.csv`
- Coordinate manifest: `PN30_COORDINATE_FREEZE_MANIFEST.json`
- Scored rows: `PN30_DYNAMIC_RELATIONAL_FLIP_SCORED.csv`
- Primary results: `PN30_DYNAMIC_RELATIONAL_FLIP_RESULTS.json`
- Independent validation: `PN30_DYNAMIC_RELATIONAL_FLIP_VALIDATION.json` (`7/7` passed)
- Recording/canonical validation: `PN30_RECORDING_VALIDATION.json` (`25/25` passed)
- Post-hoc mechanism description: `PN30_DYNAMIC_RELATIONAL_FLIP_POSTHOC.json`
- Reproducibility notebook: `PN30_DYNAMIC_RELATIONAL_FLIP_REPRODUCIBILITY.ipynb`

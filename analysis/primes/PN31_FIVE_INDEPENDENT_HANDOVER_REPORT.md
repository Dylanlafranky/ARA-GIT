# PN31 five independent child-wave handovers - result

**Date:** 22 July 2026  
**Status:** **ordered child structure only**  
**Scope:** 500 odd integers from 2001 through 2999; wave 1 excluded; no fixed pairs, averaging, sieve, or fitted classifier

## Answer first

Separating the five retained child waves exposed information that was invisible in the single Phase A winner.

The closest child by itself did **not** distinguish primes from difficult unresolved composites:

- Phase A-distance AUC: **0.5279**;
- prime mean distance: **0.4264**;
- unresolved-composite mean: **0.4440**;
- one-sided permutation: **p=0.2941**.

The identity of the winning child was also null (`p=0.8839`), and the number of approaching waves was null (`p=0.9525`).

However, the **complete closest-to-farthest ordering of all five independent waves** differed between primes and unresolved composites:

\[
\operatorname{TV}=0.6728,
\qquad
p=0.00390.
\]

This passed the frozen `p<0.01` ordering gate. The correct reading is therefore:

> The relevant information in this sample was distributed across the five-child ordering, not concentrated in the nearest child, one child identity, one pair, or the number of approaching children.

That is an ordered structural result, not a prime generator.

## Exact method

Wave 1 was removed completely. For every retained wave

\[
w\in\{3,5,9,11,13\},
\]

PN31 calculated

\[
x_w(N)=2\frac{N\bmod w}{w}
\]

and its forward distance to the next handover:

\[
h_w(N)=
\begin{cases}
0,&w\mid N,\\[2mm]
2-x_w(N),&w\nmid N.
\end{cases}
\]

The smallest \(h_w\) was called Phase A. Ties were retained. Crucially, all five values and their full order were preserved; no fixed pair or mean coordinate was constructed.

Examples:

| Chosen number | Phase A | Full order from closest to farthest handover |
|---:|---|---|
| 35 | `5` | `5 > 9 > 13 > 3 > 11` |
| 36 | `3 + 9` | `3+9 > 13 > 11 > 5` |
| 45 | `3 + 5 + 9` | `3+5+9 > 13 > 11` |

## Label firewall

1. Coordinates were generated for every odd integer from 2001 through 2999.
2. The generator contained no primality routine.
3. The unlabeled coordinate CSV was frozen at SHA-256 `5EFF45F87998A916D98B132777AFD72A75BDA96D361CB12B8856DDF910A65043`.
4. Prime labels were attached afterward by independent direct trial division.
5. No sieve was used.

The population contained 127 primes, 373 odd composites, and 96 unresolved composites that also evaded all five child divisors.

## Frozen primary results

| Endpoint | Observed result | Permutation p | Reading |
|---|---:|---:|---|
| Phase A forward distance | AUC `0.5279` | `0.2941` | Null |
| Phase A child identity | TV `0.06127` | `0.8839` | Null |
| Complete five-wave order | TV `0.67282` | **`0.00390`** | Passed ordering gate |
| Number approaching | mean `2.496` vs `2.510` | `0.9525` | Null |

### Individual-wave distances

| Wave | AUC: prime closer | Raw p | Holm-adjusted p |
|---:|---:|---:|---:|
| 3 | 0.5333 | 0.1977 | 0.9884 |
| 5 | 0.4983 | 0.5405 | 1.0000 |
| 9 | 0.4484 | 0.9338 | 1.0000 |
| 11 | 0.4657 | 0.8165 | 1.0000 |
| 13 | 0.5273 | 0.2492 | 0.9967 |

No individual child supplied a significant ridge-distance effect.

## Why the unresolved control matters

Against **all** odd composites, primes were farther from the nearest handover (`AUC=0.1359` in the proposed lower-is-prime direction). This is not surprising: most ordinary composites sit exactly on one of the declared child crossings because they are divisible by 3, 5, 9, 11, or 13.

That easy result says only that the five children detect their own exact multiples. The unresolved-composite comparison removes that trivial advantage and asks whether the remaining geometry contains anything beyond direct child divisibility.

## Post-hoc order decomposition

After labels were visible, the full order result was decomposed into all ten pairwise ordering relations. None was significant after Holm correction; all adjusted p-values were `1.0`.

The largest raw shifts were:

- `3 before 9`: primes `0.559`, unresolved composites `0.448`, raw `p=0.111`;
- `5 before 11`: `0.551` versus `0.458`, raw `p=0.180`;
- `9 before 13`: `0.449` versus `0.542`, raw `p=0.178`.

Therefore the frozen full-order result was not reducible to one dominant child-pair comparison. It arose from the joint configuration of several modest ordering changes—or from a sample-specific high-dimensional pattern. Because this decomposition is post-hoc and the order categories are sparse, only a fresh replication can distinguish those explanations.

## ARA interpretation

PN31 directly supports the user's correction that the child waves should first be retained separately. If they are reduced immediately to one Phase A winner, their detectable ordering information disappears.

The result is compatible with an Information-cubed-style statement—identity may sit in the relationships among several child positions rather than in any child alone—but it does not prove that interpretation. Mathematically, PN31 has established a fresh-sample difference in one complete five-wave order distribution.

It has not established:

- a stable ordering law across intervals;
- a formula converting an order into a prime location;
- a bounded parent-collapse operator;
- prime certification or improved prime-search complexity.

The next defensible test, if resumed, is an untouched-interval replication using the **identical five-wave order statistic**, without selecting preferred pair relations from this result.

## Audit trail

- Frozen protocol: `PN31_FIVE_INDEPENDENT_HANDOVER_PROTOCOL_v1_FROZEN.md`
- Protocol manifest: `PN31_PROTOCOL_FREEZE_MANIFEST.json`
- Frozen coordinates: `PN31_FIVE_INDEPENDENT_HANDOVER_FROZEN_COORDINATES.csv`
- Coordinate manifest: `PN31_COORDINATE_FREEZE_MANIFEST.json`
- Scored rows: `PN31_FIVE_INDEPENDENT_HANDOVER_SCORED.csv`
- Results: `PN31_FIVE_INDEPENDENT_HANDOVER_RESULTS.json`
- Independent validation: `PN31_FIVE_INDEPENDENT_HANDOVER_VALIDATION.json` (`8/8` passed)
- Recording/canonical validation: `PN31_RECORDING_VALIDATION.json` (`25/25` passed)
- Post-hoc order decomposition: `PN31_FIVE_INDEPENDENT_HANDOVER_POSTHOC.json`
- Reproducibility notebook: `PN31_FIVE_INDEPENDENT_HANDOVER_REPRODUCIBILITY.ipynb`

# Q54 — recorded transmon whole-circle external ARA return

**Date:** 30 July 2026  
**Ledger:** T314  
**Frozen protocol:** `Q54_RECORDED_TRANSMON_EXTERNAL_RETURN_PROTOCOL_v1_FROZEN.md`  
**Result:** **INVALID / CONSTRUCT INSUFFICIENT — no scientific verdict on the
\(1/e\leftrightarrow\phi\), \(0\to2\to0\) claim; 13/13 independent checks**

## Plain-language result

This public quantum-hardware dataset contains real Ramsey \(I/Q\) rotations,
but it does not preserve enough complete, strong rotations in sequence to
follow the centre of one whole circle into the centre of the next several
times.

Q54 needed at least three eligible external centre movements in at least five
primary files. It obtained only **one eligible movement from one file**.
That is enough to draw one arrow, but not enough to observe a journey from
the \(1/e\) pole to the Phi pole and back.

Accordingly:

- the directional-path question is **invalid**;
- the active half-traversal question is **invalid**;
- the complete \(0\to2\to0\) return question is **invalid**.

This is not a negative result for ARA. The required measured object was
largely absent from the source record after the frozen quality rules were
applied.

## What was tested

The intended ARA object was the movement of a complete internally rotating
circle through time:

\[
\underbrace{\text{one complete internal }I/Q\text{ rotation}}
_{\text{one ARA circle}}
\longrightarrow
\underbrace{\text{fitted circle centre}}
_{\text{location of the whole}}
\longrightarrow
\underbrace{\text{movement between successive centres}}
_{\text{external/meta ARA vector}}.
\]

The declared external direction ran from:

\[
\underbrace{1/e}_{\text{ARA }0}
\longleftrightarrow
\underbrace{\phi-1}_{\text{ARA }2}.
\]

Q54 separately registered:

1. directional occupancy of that arc;
2. an active endpoint-to-endpoint half-traversal;
3. an active endpoint-to-opposite-endpoint-to-start return.

Three equal-width quarter-turn rotations were frozen as location controls.
The internal amount of Ramsey turning, a parent-ridge average, T1 decay and
forced flux-jump resets were not allowed to substitute for the external
circle-centre path.

## Public hardware source

The source is Zenodo
[`10.5281/zenodo.8004359`](https://doi.org/10.5281/zenodo.8004359), the source
archive for *Inductively shunted transmon: A superconducting qubit with flux
noise insensitive plasmon states and a protected fluxon decay exceeding 3
hours*.

Only the registered `Fig6/**/T2 Vs Flux/T2_*.txt` Ramsey files were used.
They provide:

- 101 ordered delay coordinates per complete primary file;
- 11 repeated \(I\) rows and 11 matching \(Q\) rows;
- recorded Device B and Device C hardware measurements.

Device A was opened to understand the file grammar and was excluded from the
primary verdict. Devices B and C supplied 21 complete primary files.

The 297 MB archive did not need to be downloaded in full. The reproducer read
the ZIP central directory through HTTP byte ranges, extracted only the
declared files, checked each ZIP CRC and recorded per-file SHA-256 hashes.
The local manifest contains 100 extracted source files and all hashes passed
independent rechecking.

## Frozen extraction

For each file:

1. pair repeated \(I\) and \(Q\) rows;
2. form the repeat-mean trace, with repeat median as a fixed sensitivity;
3. subtract a late-time origin;
4. establish source-intrinsic phase orientation without fitting the target;
5. divide the unwrapped phase at successive \(2\pi\) crossings;
6. retain only complete circles with at least 6 points, at least \(1.8\pi\)
   phase span, sufficient radius and radial residual at most 0.25;
7. fit one centre to every retained circle;
8. calculate the external tangent
   \[
   \mathbf d_r=\mathbf c_{r+1}-\mathbf c_{r-1};
   \]
9. require centre displacement at least 1% of the surrounding circle radius.

## Population audit

| Quantity | Result |
|---|---:|
| Primary Device B/C files | 21 |
| Primary repeat-mean circle centres | 18 |
| Centres across all devices and both estimators | 47 |
| Primary repeat-mean external tangents | 1 |
| External tangents across all populations | 2 |
| Primary files with an eligible tangent | 1 |
| Primary files with at least three eligible tangents | 0 |
| Frozen minimum for valid object | 5 files |

Several raw traces contained approximately 2–8 apparent internal rotations.
Most later rotations had decayed below the frozen radius floor or failed the
complete-circle requirements. A usable external tangent requires three
retained consecutive circle centres; a traversal needs several consecutive
tangents. The source therefore ran out of observable circles before the
registered ARA path could be formed.

## Numerical outcome

The sole primary repeat-mean tangent fell in the third rotated control arc:

| Arc | Eligible tangents |
|---|---:|
| Declared \(1/e\rightarrow\phi\) | 0 |
| Rotated control 1 | 0 |
| Rotated control 2 | 0 |
| Rotated control 3 | 1 |

There were no eligible contiguous runs, half-traversals or full returns.
These zero event counts are not interpretable as evidence because the frozen
valid-object gate failed first.

The translation, rotation and scale invariance check passed with maximum
numerical error \(3.70\times10^{-12}\). Independent validation reconstructed
the source hashes, populations, single eligible tangent, arc assignment,
failed validity gate and invalid verdicts: **13/13 checks passed**.

## ARA and hardware readings side by side

| ARA reading | Hardware result |
|---|---|
| complete internal child circle | Ramsey \(I/Q\) rotation is present |
| parent location of that circle | fitted circle centre can be calculated |
| external/meta movement | usually cannot be continued because too few strong complete circles survive |
| \(1/e\to\phi\) half path | not testable |
| \(1/e\to\phi\to1/e\) return | not testable |

The dataset supports the first two construction steps, not the temporal depth
needed for the third.

## Important acquisition boundary

Every delay point is the average of repeated hardware preparations and
measurements at a selected Ramsey waiting time. It is not one continuously
observed single quantum system moving through all delay points. This source
can still test the geometry of the recorded ensemble response, but it is less
direct than a continuous time-ordered trajectory for the external-vector
claim.

## Frozen-protocol clarification

The frozen prose listed “not supported” as the fallback when the evidence
gates failed. G0, however, was explicitly the **valid hardware object** gate.
Labelling a G0 failure “not supported” would incorrectly turn absence of the
registered measured object into evidence against the hypothesis.

The frozen thresholds and all calculations remain unchanged. The conservative
scientific interpretation is therefore **INVALID / NO TEST**. This
clarification is recorded openly rather than silently changing the frozen
protocol.

## What a valid next dataset must provide

A proper replication source should have:

- raw recorded hardware \(I/Q\), or an equivalent two-dimensional observable;
- preserved experimental time order;
- approximately 7–10 or more strong complete rotations per lineage;
- at least five independent lineages, preferably substantially more;
- stable detector axes or a predeclared intrinsic orientation;
- enough signal after each rotation for reliable circle-centre fitting;
- preferably continuous single-shot evolution rather than independent
  delay-sweep preparations;
- no forced reset used to manufacture the return being tested.

That source would let the same frozen geometry ask the intended question
without replacing ARA with a fitted physics model.

## Reproduction files

- `q54_extract_zenodo_subset.py`
- `Q54_RECORDED_TRANSMON_EXTERNAL_RETURN_PROTOCOL_v1_FROZEN.md`
- `q54_recorded_transmon_external_return.py`
- `q54_validate_recorded_transmon_external_return.py`
- `Q54_RECORDED_TRANSMON_SOURCE_PROFILE.json`
- `Q54_RECORDED_TRANSMON_EXTERNAL_RETURN_RESULTS.json`
- `Q54_RECORDED_TRANSMON_CENTRES.csv.gz`
- `Q54_RECORDED_TRANSMON_EVENTS.csv.gz`
- `Q54_RECORDED_TRANSMON_EXTERNAL_RETURN.png`
- `Q54_RECORDED_TRANSMON_EXTERNAL_RETURN_VALIDATION.json`


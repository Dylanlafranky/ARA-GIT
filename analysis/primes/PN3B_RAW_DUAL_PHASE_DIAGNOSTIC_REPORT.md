# PN3B raw dual-phase diagnostic

**Test ID:** `PN3B/RAW-DUAL-PHASE/OPENED-DEVELOPMENT-v1`  
**Run:** 18 July 2026  
**Status:** `OPENED-DATA DIAGNOSTIC COMPLETE / SECOND COORDINATE CONTAINS LOCAL STRUCTURE / NO SCALE-PERSISTENT TIME-LIKE COORDINATE RECOVERED / DOMINANT FULL-SPECTRUM LINE IS THE NEXT CONNECTION GATE / P31 UNOPENED`

> **19 July 2026 centering correction:** PN3B used a raw integer source, but Fourier transformation,
> residualization and SVD are processed diagnostic methods. The later factor-removal gate is an
> outcome-derived coordinate and cannot be used as a prospective feature. These qualifications change
> no numerical result.

## Question

Dylan's geometric diagnosis was that the prime work had measured a strongly connection-oriented half of the system. The missing half might be a larger, slower information-flow or Time-like wave acting across the raw number line. PN3B therefore returned to the already opened R6-R9 integer windows and transformed the complete unfiltered prime/composite record before applying any connection mask.

This is a development diagnostic, not a blind prime prediction. “Time-like” is a candidate geometric role, not a name assigned merely because a coordinate is ordered.

## Bottom line

The test found a genuine extra view that the one-axis prime/composite label had hidden: **number-line position coupled to the later sieve gate at which a p29 survivor is removed**. R9's leading position-by-gate structure is stronger than exact margin-preserving permutations (`p=0.001996`).

However, its orientation does not recur from R8 to R9. The R8-R9 leading spatial alignment is only `0.06296` (`p=0.4770`) and gate-mode alignment is `0.15707` (`p=0.3772`). The ordinary low-frequency phase paths also do not recur. The registered candidate Time-like coordinate therefore fails.

The strongest R8 and R9 full-spectrum line after the Q29 connection control is instead the third harmonic of the base period `62 = 2 x 31`, accurate to within one Fourier bin. This is the next omitted prime connection gate. It is not an independent opposite wave.

Plainly: **the “we only measured half” criticism was productive, because a second coordinate really did reveal discarded organization. But the repeatable part still belongs to the divisibility/connection hierarchy. The raw prime record has not yet supplied an independently recurring Time-side pole.**

## Frozen measurement

For every integer `n` in each complete window:

\[
\underbrace{y(n)}_{\substack{\text{raw state}\text{prime or composite}}}
=
\begin{cases}
1,&n\text{ is prime},\\
0,&n\text{ is composite}.
\end{cases}
\]

The raw-source sequence was Fourier transformed first. This is therefore a processed-method diagnostic,
not a direct ARA measurement on untransformed data. Connection controls were then added separately:

\[
\underbrace{r_Q(n)}_{\substack{\text{prime excess after}\text{known connection mask }Q}}
=
\underbrace{y(n)}_{\text{raw prime state}}
-
\underbrace{\widehat p_Q w_Q(n)}_{\substack{\text{expected state from}\text{sieve connections through }Q}}.
\]

The main control was `Q=29`; `Q=997` tested whether a candidate pattern survived much deeper connection removal. The phase path used 256 equal number-line cells and scaled Fourier modes 1-64. Global and 16-macroblock conditional nulls each used 500 draws.

The perpendicular diagnostic retained two coordinates for every p29 candidate. Its future gate coordinate
is available only after later factor removal and is therefore diagnostic rather than prospectively predictive:

\[
\underbrace{(x,g)}_{\substack{\text{two-coordinate}\text{candidate record}}}
=
\left(
\underbrace{\text{position in the integer window}}_{\text{number-line location}},
\underbrace{\text{later factor-removal stage}}_{\text{future connection gate}}
\right).
\]

Its 128-by-33 position/gate table was reduced with Pearson residuals and SVD. Exact label permutations preserved both the position totals and gate-stage totals.

## Results

| Rung | Raw integers | Raw primes | Q29 low-mode FWER p | Q997 low-mode FWER p | Q29 top full frequency | Period-62 harmonic | Joint leading-energy p |
|---|---:|---:|---:|---:|---:|---:|---:|
| R6 | 10,000 | 753 | 0.9162 | 1.0000 | 0.1870000 | 12; outside one bin | 0.6627 |
| R7 | 100,000 | 6,241 | 0.8124 | 0.3513 | 0.1451600 | 9; within one bin | 0.00599 |
| R8 | 1,000,000 | 54,208 | 0.8703 | 0.9381 | 0.0483870 | 3; within one bin | 0.05190 |
| R9 | 10,000,000 | 482,449 | 0.5709 | 0.2754 | 0.0483871 | 3; within one bin | 0.001996 |

### 1. No registered low-frequency wave

At R8 the largest Q29 low mode is mode 43 with power `0.02742`, far below the global 99% family-wise boundary `0.06612`. At R9 the largest is mode 53 with power `0.03438`, below `0.06611`. The corresponding family-wise p-values are `0.8703` and `0.5709`.

Removing connections through `Q=997` does not uncover the missing phase. Its R8 and R9 family-wise p-values are `0.9381` and `0.2754`.

### 2. No cross-rung phase recurrence

For the R8-to-R9 Q29 residual:

- block-position correlation: `0.01151`, `p=0.8423`;
- low-mode power-profile correlation: `0.09144`, `p=0.2575`;
- complex phase coherence: `0.07593`, `p=0.7006`; 99% null boundary `0.26339`.

The Q997 R8-to-R9 phase coherence rises only to `0.12697`, still nonsignificant (`p=0.3792`).

### 3. The perpendicular coordinate is locally structured but not a common adult

The position-by-future-gate map has a stronger-than-null leading component at R7 (`p=0.00599`) and R9 (`p=0.001996`); R8 is borderline rather than significant (`p=0.05190`). This establishes that the two-coordinate map is not merely a decorative redraw of the marginal counts.

But the leading modes do not point the same way between rungs. R8-to-R9 spatial and gate alignments are both ordinary under their nulls. The structure therefore cannot yet be called one recurring larger wave. It is better described as rung-specific organization inside the later factor-removal web.

### 4. The strongest full-spectrum line is a connection line

The post-result arithmetic crosswalk is:

\[
\underbrace{f_{\rm observed}}_{0.0483870\text{ at R8};\ 0.0483871\text{ at R9}}
\approx
\underbrace{\frac{3}{2\cdot31}}_{0.0483870968}
.
\]

R8 differs from `3/62` by `9.68e-8`, below its Fourier-bin width `1e-6`. R9 differs by `3.23e-9`, below its bin width `1e-7`. R7 similarly lands on `9/62` within one bin.

This was not a preregistered endpoint and is recorded as a post-result interpretation. Its straightforward established meaning is that a Q29 residual is dominated by the first unrepresented prime gate, 31, coupled to parity. Calling this “Time” would mislabel a visible connection harmonic.

## ARA interpretation

The result separates three layers that had been visually mixed:

1. **Raw state:** prime/composite occurrence along the integer line.
2. **Connection hierarchy:** deterministic divisibility gates and their harmonics.
3. **Process coordinate:** the ordered path through later gates, which is only visible after the endpoint is decompressed.

The process coordinate is real in the mathematical sense that it adds a nontrivial joint organization. Yet it is still computed entirely from the same factor network. It is therefore not independent evidence for ARA's proposed Information/Time pole.

The best present reading is:

> Numbers and prime identities are exceptionally connection-dense objects. Their apparent movement on the opened data is largely the unfolding of further connections. Negatives would reflect orientation and randomness would supply a null, but neither automatically supplies the missing opposite pole. A genuine Time-like coordinate must be defined through an observable not reducible to the same divisibility labels and then recur across scales in a frozen direction.

## What this does and does not imply

Supported here:

- the terminal prime label and the one-axis number line flatten useful hierarchical information;
- adding a perpendicular position-by-future-gate coordinate reveals rung-local organization;
- the main R8/R9 Q29 full-spectrum line is explained by the next omitted connection gate;
- the strict registered candidate Time-like coordinate is not supported.

Not supported here:

- a physical Time wave in the integers;
- a common adult mode recurring across R8 and R9;
- prime prediction, Riemann-hypothesis evidence or universal ARA geometry;
- the claim that no other dual representation can work.

The negative boundary is representation-specific: stationary Fourier phase in these four fixed raw windows, plus this exact position-by-gate decomposition.

## Protocol correction retained

The first exploratory joint-map null drew cell counts without preserving both observed margins, and spectral entropy was initially calculated from an unnormalised power array. Both defects were caught before the joint-map result was interpreted. The frozen endpoints and windows were not changed. The final run uses exact stage-label permutations preserving row and column margins, and normalized spectral entropy. The amendment is recorded in the protocol.

## Validation and reproducibility

The independent validator imports no primary analysis module. It rebuilt all four integer windows using a separately coded Boolean segmented sieve; matched prime and Q29/Q997 candidate counts; regenerated every saved block coordinate; recomputed the Q29 top full frequency and period-62 crosswalk; checked the R8-R9 mode alignments; and verified every output hash. All checks passed.

The validator did **not** independently rerun the 500-draw Monte Carlo sequences; those p-values are internally reproducible from the primary script but remain outside the independent audit boundary.

Restart packet:

- `PN3B_RAW_DUAL_PHASE_DIAGNOSTIC_PROTOCOL.md`
- `pn3b_raw_dual_phase.py`
- `PN3B_RAW_DUAL_PHASE_DIAGNOSTIC.ipynb`
- `PN3B_RAW_DUAL_PHASE_RESULTS.json`
- `PN3B_INDEPENDENT_VALIDATION.json`
- `PN3B_RAW_DUAL_SPECTRUM.png`
- `PN3B_PHASE_GATE_MAP.png`
- five CSV tables and the exact NPZ coordinate packet
- `PN3B_REPORT_ARTIFACT.json`

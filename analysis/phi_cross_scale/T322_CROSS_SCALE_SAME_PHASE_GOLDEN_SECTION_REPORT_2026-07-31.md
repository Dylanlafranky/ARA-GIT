# T322 — Cross-scale same-phase golden-section test

**Date:** 31 July 2026  
**Frozen event-local verdict:** **NOT SUPPORTED — 0/5 gates**  
**Calculation validation:** **15/15 checks passed**  
**Methodological status:** calculations verified; interpretation requires the
pairing-bias caveat below

## Technical summary

The corrected golden-section statement is

\[
a=A_{\rm parent},\qquad b=A_{\rm child},\qquad
\frac ab=\frac{a+b}{a}=\phi.
\]

Here lowercase `b` is a smaller occurrence of **the same Phase-A type**, not
Phase B. T322 therefore removed the intervening opposite-phase turning point
and measured same-sign recurrence gaps across pendulum-arm scales.

The frozen event-local version did **not** recover Phi. Across `184` run-3
matches,

\[
\operatorname{median}(a/b)=1.00905,
\qquad
\operatorname{median}((a+b)/a)=1.99103.
\]

So Dylan's warning that this cut might still read `2` was substantially
correct: the parent and selected child gaps were almost equal, making the
first quotient approximately `1` and the combined whole approximately `2`.
This is ridge/octave-like recurrence bookkeeping, not the golden fixed point.

The important complication is that arm 3 contains more than one recurrence
family. The event-local matching rule favoured its longer recurrence gaps.
When each arm is instead reduced to its branch-median recurrence scale, free
run 3 gives Phi-like deeper ratios (`1.578–1.628`), satisfying both golden
quotients closely. That pattern is **descriptive and post-hoc**, however, and
does not remain near Phi in free run 1, free run 2, or the driven record.

## The frozen local handover reads 1-to-2, not Phi-to-Phi

The primary length was elapsed time from one positive maximum to the next
positive maximum, or one negative minimum to the next negative minimum. Each
parent recurrence was paired with the same-sign child recurrence having the
largest temporal overlap. No opposite-phase turning point entered the ratio.

| Scope | Events | Median `a/b` | Median `(a+b)/a` | Closest landmark |
|---|---:|---:|---:|---|
| pooled run 3 | 184 | 1.00905 | 1.99103 | 1 |
| arm 1 → arm 2 | 94 | 1.00908 | 1.99100 | 1 |
| arm 2 → arm 3 | 90 | 0.99473 | 2.00530 | 1 |
| positive recurrence | 92 | 1.00914 | 1.99094 | 1 |
| negative recurrence | 92 | 1.00903 | 1.99105 | 1 |
| driven transfer | 174 | 1.00397 | 1.99605 | 1 |

The pooled bootstrap 95% interval for median `a/b` was
`[1.00000, 1.01215]`. Only `10.3%` of primary events satisfied the frozen
maximum golden-error tolerance of `0.08`. All five gates failed. Circularly
shifted child identities were slightly *closer* to Phi than the observed local
matches, so temporal pairing supplied no Phi-specific advantage.

![T322 event-local same-phase result](F:/SystemFormulaFolder/GIT/ARA-GIT/analysis/phi_cross_scale/T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION.png)

The upper-right panel shows the central result: arm 1→2 remains tightly near
`1`; arm 2→3 contains a broad second family near Phi and above, but its median
is still near `1`. The lower-left curve is algebraically forced by
`s=1+1/r`; the unforced question is where the observations sit on that curve.
They mostly sit at `(1,2)`, not at the golden fixed point `(phi,phi)`.

## A real Phi-like substructure appears, but it is not yet a stable law

The validation audit exposed a material selection effect. Among the `90`
arm-2→arm-3 event matches, `46` lay within `0.08` of `1`, while `19` lay
within `0.08` of Phi. The matching rule selected arm-3 child gaps with median
duration `1.148 s`; the two raw arm-3 branch medians average only `0.8265 s`.
Maximum-overlap matching therefore selected the slower child family and is
not a neutral estimator of the whole arm's scale.

The post-hoc scale summary removes local matching and compares branch medians
directly. In free run 3:

| Scale relation | Positive branch | Negative branch | Golden maximum error |
|---|---:|---:|---:|
| arm 1 / arm 2 | 1.01679 | 1.00910 | 0.601–0.609 |
| arm 2 / arm 3 | 1.60147 | 1.57844 | 0.0166–0.0396 |
| arm 1 / arm 3 | 1.62836 | 1.59281 | 0.0103–0.0252 |

For the arm-2/arm-3 positive branch, for example,

\[
\frac ab=1.60147,
\qquad
\frac{a+b}{a}=1.62443.
\]

Both lie close to Phi. The negative branch gives `1.57844` and `1.63354`.
This is the cleanest numerical appearance of Dylan's golden-section equation
in this pendulum record.

It is not a replication across records:

- free run 1 deeper ratios were approximately `0.98–1.00`;
- free run 2 deeper ratios were approximately `1.71–1.77`, with `sqrt(3)`
  closer than Phi under the frozen landmark set;
- free run 3 deeper ratios were approximately `1.58–1.63` and Phi was closest;
- the driven record returned approximately `1.01` throughout.

![T322A post-hoc scale audit](F:/SystemFormulaFolder/GIT/ARA-GIT/analysis/phi_cross_scale/T322A_POSTHOC_SAME_PHASE_SCALE_RATIOS.png)

The figure shows a coherent state-dependent scale change, but not a universal
constant ratio. The first two arms stay near the same recurrence scale in
every record. The third arm sometimes joins that scale and sometimes runs on
a faster child cadence. Free run 3 happens to put that deeper cadence close to
the golden fixed point.

## Motion length does not rescue this operationalization

The secondary coordinate integrated absolute angular motion inside each
same-phase gap. Its pooled median parent/child ratio was `0.70734`, with
median maximum Phi error `0.91069`; neither lineage independently selected
Phi. Because the pooled value combines two very different lineages, its
proximity to `1/sqrt(2)` is descriptive only and is not promoted as a new
landmark result.

## What T322 establishes—and what it does not

T322 establishes three narrower facts:

1. A direct same-phase cross-scale equation can be written exactly as Dylan
   proposed and tested without inserting Phase B as a vertex.
2. The frozen event-local pendulum realization reads approximately `(1,2)`,
   not `(phi,phi)`.
3. The evaluation record contains a separate faster arm-3 recurrence family
   whose whole-scale ratio is Phi-like, but its location changes substantially
   across records and forcing conditions.

It does **not** establish Phi as the universal Phase-A parent/child handover.
Nor does it establish that Phi is absent: the present pendulum has at least two
child recurrence regimes, and the scientific problem is now identifying—by a
rule frozen independently of Phi—which regime is the actual cross-rung
handover rather than a same-rung recurrence, skipped/weak turn, or dynamical
state change.

## Methodological correction to T321

T321 remains a valid measurement of routed `A -> B -> A` trajectory geometry.
Its result near `2` is retained. It must no longer be described as the decisive
test of the later-clarified golden-section claim, because that claim compares
`A(parent)` directly with `A(child)` and contains no Phase-B measurement
vertex. T322 is the first frozen record to test that corrected object, albeit
with the local-matching limitation documented above.

## Recommended next test

Do not tune a threshold until free run 3 is made to select Phi. Instead:

1. Define the two arm-3 recurrence families without referencing Phi—using
   observable turn prominence, amplitude, or a pre-event dynamical state.
2. Freeze that family classifier on runs 1–2 only.
3. Predict, before opening another record, when arm 3 will occupy the
   same-rung family near `1` and when it will occupy the faster cross-scale
   family.
4. Only then test whether the predicted faster-family ratio converges toward
   Phi, another landmark, or a continuously state-dependent value.

That is the clean way to chase the slippier handover now visible in the data.

## Reproduction records

- `T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION_PROTOCOL_v1_FROZEN.md`
- `t322_cross_scale_same_phase_golden_section.py`
- `T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION_RESULTS.json`
- `T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION_EVENTS.csv`
- `T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION.png`
- `T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION.svg`
- `T322A_POSTHOC_SAME_PHASE_SCALE_RATIOS.png`
- `T322A_POSTHOC_SAME_PHASE_SCALE_RATIOS.svg`
- `validate_t322_cross_scale_same_phase_golden_section.py`
- `T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION_VALIDATION.json`

Source data: dynamicslab *MultiArm-Pendulum*, Zenodo
[`10.5281/zenodo.6633719`](https://doi.org/10.5281/zenodo.6633719). File hashes
are recorded in the results JSON.

# PN21 — ridge-straddling two-child retention test

**Date:** 21 July 2026  
**Status:** **DEVELOPMENT NULL — fresh 87-bit anchor remains sealed**  
**Population:** 500,000 odd integers in the previously opened interval `[4,000,000,000, 4,001,000,000)`  
**Independent validation:** 12/12 checks passed

## Result first

Selecting the last prime gate below `sqrt(n)` as Phase A and the first prime gate above `sqrt(n)` as Phase B does **not** recover the proposed dominant first fractal component.

The frozen requirement was at least 90% held-out retention of the exact parent factor-progress coordinate. The observed result was

\[
\underbrace{R^2_{\rm retain}}_{\substack{\text{full parent variance retained}\\\text{on the unopened half of development}}}
=-0.0000292,
\]

or effectively **0%**. The negative sign means the two-child grid reconstructed the held-out parent very slightly worse than simply predicting the training mean for every integer.

Prime-ridge diagnostics were also at chance:

- joint two-child ridge AUC: `0.499698`;
- compressed-closure ridge AUC: `0.499137`;
- population prime rate: `9.0332%`;
- prime rate in the strongest 1% joint-ridge region: `9.1600%` (`1.014×` lift);
- prime rate in the strongest 1% closure-ridge region: `8.9400%` (`0.990×` lift).

The pair therefore neither reconstructs the full parent nor locates prime ridges.

## Geometry tested

The exact parent reference remained the established factor-progress coordinate:

\[
\underbrace{P(n)}_{\text{full parent sieve state}}
=
\begin{cases}
1,&n\text{ prime},\\
2\log(\operatorname{lpf}(n))/\log n,&n\text{ composite}.
\end{cases}
\]

The proposed opposing children were

\[
\underbrace{q_-(n)}_{\substack{\text{last completed gate}\\\text{below the square-root ridge}}}
=\max\{p\le\sqrt n:p\text{ prime}\},
\qquad
\underbrace{q_+(n)}_{\substack{\text{first uncompleted gate}\\\text{above the square-root ridge}}}
=\min\{p>\sqrt n:p\text{ prime}\}.
\]

Their raw residue phases were preserved:

\[
\underbrace{A_-(n)}_{\text{Phase A from below}}
=2\frac{n\bmod q_-}{q_-},
\qquad
\underbrace{B_+(n)}_{\text{Phase B from above}}
=2-2\frac{n\bmod q_+}{q_+}.
\]

So this test did not immediately collapse the pair to `1+1`. It retained the two gate identities, two raw phase coordinates and their opposite orientations.

## Retention comparison

| Pair | Held-out retained `R²` | Parent correlation | Normalized mutual information | Joint-ridge AUC | Closure-ridge AUC |
|:---|---:|---:|---:|---:|---:|
| Ridge-straddling `q_- / q_+` | **-0.0000292** | +0.000392 | 0.000456 | 0.499698 | 0.499137 |
| Same-side `q_- / q_{--}` control | -0.0000230 | -0.000234 | 0.000261 | 0.499684 | 0.500700 |

The straddling pair carries a tiny descriptive amount of discretized information (`0.0456%` of parent entropy), but it fails out of sample and is marginally worse than the same-side control on the primary retention measure.

## Why this decomposition fails

The correction from two same-side gates to two ridge-straddling gates fixed their **orientation**, but not their **ownership**.

Across this million-integer interval, only these scale gates were used:

- `q_-`: 63,241 or 63,247;
- `q_+`: 63,247 or 63,277.

Their residue cycles are genuine modular waves, but they are still external gates selected because they sit near the observer-defined `sqrt(n)` boundary. The full parent coordinate, by contrast, is usually determined by a much smaller least-factor collision such as 3, 5, 7, 11, and so on. The boundary pair has no privileged knowledge of which lower child collides first.

Plainly: we placed one ruler on either side of the ridge, but two opposing rulers are not automatically the object's two internal waves.

## What the null means

PN21 rejects this precise statement:

> The last prime gate below `sqrt(n)` and first prime gate above `sqrt(n)`, represented by their raw residue phases, retain roughly 90% of the full parent factor geometry.

It does **not** reject:

- the exact parent prime ridge;
- the broader ARA fractal claim;
- the possibility that one correctly chosen immediate A/B pair retains most of a parent;
- TheFormula's domain-specific evidence that a dominant first component can carry most predictive effect.

TheFormula supports the **search strategy**, not the assumption that the same numerical child selector works for primes.

## Strongest next interpretation

An endogenous prime child probably must be selected by the number's actual collision/survival history rather than its distance from `sqrt(n)`. The next decomposition audit should distinguish:

1. **collision child:** the strongest actual factor-pressure contribution already acting on the node;
2. **survivor/release child:** the strongest still-open counterpath after that collision state;
3. **temporal direction:** how those two states change from `n-1` through `n` to `n+1`.

That suggests the true A/B pair may be a **state transition through the sieve web**, not two static prime gates. This would also explain why a time-series first component can dominate in TheFormula while two static modular samples do not.

## Decision

The frozen 90% threshold failed, the straddling pair did not beat its same-side control, and no non-collapsing location decoder exists. The 87-bit target was therefore not opened.

## Files

- `PN21_RIDGE_STRADDLING_TWO_CHILD_PROTOCOL_v1_FROZEN.md`
- `pn21_ridge_straddling_two_child.py`
- `PN21_RIDGE_STRADDLING_TWO_CHILD_RESULTS.json`
- `validate_pn21_ridge_straddling_two_child.py`
- `PN21_RIDGE_STRADDLING_TWO_CHILD_VALIDATION.json`
- `PN21_RIDGE_STRADDLING_TWO_CHILD_REPRODUCIBILITY.ipynb`
- `PN21_NOTEBOOK_EXECUTION_VALIDATION.json`


# PN21 ridge-straddling two-child retention protocol — frozen v1

**Frozen:** 21 July 2026, before PN21 computation  
**Status:** development-only decomposition test  
**Fresh 87-bit target:** remains sealed and is not an input

## Question

Does one genuinely opposite immediate pair—one child immediately below the square-root ridge and one immediately above it—retain most of the exact parent sieve geometry?

This tests the user's proposed TheFormula-like claim that the first fractal component may carry about 90% of the parent effect. It does **not** assume that two previously used same-side gates were the correct children.

## Development population

- Opened interval: `[4,000,000,000, 4,001,000,000)`.
- Evaluate odd integers only; even integers are the already-known parity trough and are never a nontrivial next-prime candidate above 2.
- The full parent state is generated exactly from the least prime factor.

## Full parent reference

For odd integer `n`, let `lpf(n)` be its least prime factor. Define

\[
P(n)=
\begin{cases}
1, & n\text{ prime},\\
2\log(\operatorname{lpf}(n))/\log n, & n\text{ composite}.
\end{cases}
\]

This is the existing PN10/PN10B parent factor-progress coordinate. It is the exact full-state reference, not a forecast.

## Ridge-straddling immediate children

Let

\[
q_-(n)=\max\{p\text{ prime}:p\le\sqrt n\},
\qquad
q_+(n)=\min\{p\text{ prime}:p>\sqrt n\}.
\]

These are deliberately on opposite sides of the square-root ridge. Preserve both gate identities and define the raw directed phases

\[
A_-(n)=2\frac{n\bmod q_-(n)}{q_-(n)},
\qquad
B_+(n)=2-2\frac{n\bmod q_+(n)}{q_+(n)}.
\]

The compressed closure and two-dimensional ridge distance are

\[
C(n)=\frac{A_-(n)+B_+(n)}2,
\qquad
D(n)=|A_-(n)-1|+|B_+(n)-1|.
\]

## Same-side control

Repeat the calculation using the two largest prime gates at or below `sqrt(n)`. This is the earlier same-side interpretation. The straddling pair must outperform it to justify the revised decomposition.

## Primary retention measure

Use the first contiguous half of the interval for development fitting and the second half for evaluation. Partition the raw `(A,B)` square `[0,2]×[0,2]` into a fixed `32×32` grid. In each occupied training cell, store the mean full parent coordinate `P`. Unseen test cells fall back to the training-global mean.

On the held-out half, calculate

\[
R^2_{\rm retain}=1-\frac{\operatorname{MSE}(P,\widehat P_{A,B})}
{\operatorname{MSE}(P,\overline P_{\rm train})}.
\]

Interpretation is frozen:

- `R²_retain >= 0.90`: the two-child pair supports the proposed roughly-90% sufficient-statistic claim.
- `0 < R²_retain < 0.90`: partial retention, insufficient for the strong claim.
- `R²_retain <= 0`: no out-of-sample parent retention beyond the global mean.

The grid is a diagnostic measuring information present in the two raw coordinates. It is not proposed as an ARA prime formula.

## Secondary diagnostics

1. Pearson correlation between `C(n)` and `P(n)`.
2. AUC for prime nodes using `-D(n)` and `-|C(n)-1|` as frozen ridge scores.
3. Prime rate in the top 1% of each ridge score versus the population prime rate.
4. Descriptive normalized mutual information after fixed discretization of the two-child state and parent coordinate.
5. All metrics side by side with the same-side control.

## Decision rule

Do not evaluate the sealed 87-bit anchor unless the straddling pair:

1. reaches `R²_retain >= 0.90` on the held-out half;
2. materially exceeds the same-side control; and
3. yields a non-collapsing deterministic location decoder frozen in a separate protocol.

Passing the retention test alone would justify decoder development, not an immediate fresh reveal.


# PN28 three-child residual lift — frozen protocol v1

**Frozen:** 22 July 2026, before primality labels were calculated  
**Status:** native ARA one-shot residual-correction test  
**Protected 87-bit anchor:** remains sealed and is not an input

## Question

Does retaining all three child-pair asymmetries provide a useful two-rung correction to the PN27 one-pair candidate?

No sieve state, known nearby prime, prime gap, primality label, retry, parity repair, or post-prediction adjustment may enter the predictor.

## Frozen child waves

The child labels and fixed orientations are

\[
W=\{1,3,5,9,11,13\},
\qquad
(1,13),\ (3,11),\ (5,9),
\]

where the lower member is the pair's Phase A coordinate and the higher member is Phase B for this test.

For each wave label \(w\) and chosen number \(N\), use the literal completion rule established in the 35 example:

\[
u_w(N)=
\begin{cases}
1,&w\mid N,\\[2mm]
\dfrac{2w}{N},&w\nmid N.
\end{cases}
\]

For each pair \((a,b)\), its normalised signed imbalance is

\[
d_{a,b}(N)=\frac{u_b(N)-u_a(N)}{u_a(N)+u_b(N)}.
\]

The collapsed three-child ARA coordinate and its displacement from the 1.0 ridge are

\[
R_{\rm child}(N)
=1+\frac{d_{1,13}(N)+d_{3,11}(N)+d_{5,9}(N)}3,
\]

\[
\epsilon_0(N)=R_{\rm child}(N)-1.
\]

Two rung increases double the displacement twice:

\[
\epsilon_2(N)=2^2\epsilon_0(N)=4\epsilon_0(N).
\]

## Frozen integer collapse

Collapse \(\epsilon_2\) once to the nearest integer, with exact half cases rounded away from zero:

\[
k(N)=\operatorname{round}_{1/2\to\mathrm{away}}\!\left(\epsilon_2(N)\right).
\]

There is no parity correction. If this produces an even candidate, it remains an even candidate and is scored as written.

## Frozen base and corrected candidates

The PN27 base pair remains:

\[
a_*(N)=\max\{w\in W:w\mid N\},
\qquad
b_*(N)=14-a_*(N).
\]

The frozen PN27 candidate is

\[
\widehat P_0(N)=N+a_*(N)+2b_*(N)+1.
\]

The PN28 prediction adds only the propagated three-child residual:

\[
\boxed{
\widehat P_1(N)
=\widehat P_0(N)+k(N).
}
\]

It does not replace the original child identity with a new fixed centre.

## Frozen worked example

For \(N=35\):

\[
d_{1,13}=-\frac9{61},
\qquad
d_{3,11}=\frac47,
\qquad
d_{5,9}=-\frac{17}{53}.
\]

Therefore

\[
R_{\rm child}\approx1.0343776,
\qquad
\epsilon_2\approx0.1375103,
\qquad
k=0.
\]

The prediction remains

\[
35+5+2(9)+1+0=59.
\]

## Fresh anchors

The following range strings were searched in the existing prime analysis before this protocol was created and were absent.

For each scale, sample 10,000 distinct odd and 10,000 distinct even anchors with Python `random.Random(seed).sample` over parity-specific ranges.

| Scale | Half-open interval | Odd seed | Even seed |
|---|---|---:|---:|
| low | `[83,000,000, 83,500,000)` | 28001 | 28101 |
| middle | `[83,000,000,000, 83,000,500,000)` | 28002 | 28102 |
| high | `[830,000,000,000, 830,000,500,000)` | 28003 | 28103 |

The primary endpoint uses 30,000 odd anchors for direct comparison with PN27. The balanced 60,000-anchor population is secondary and tests the literal no-parity-repair rule.

## Blind validation and endpoints

Predictions, residuals, and integer adjustments must be written and SHA-256 frozen before any primality routine is called.

Primary outcome:

\[
Y_1=\mathbf1[\widehat P_1(N)\text{ is prime}].
\]

Base comparison:

\[
Y_0=\mathbf1[\widehat P_0(N)\text{ is prime}].
\]

Report:

- exact one-shot prime rates for corrected and base candidates;
- paired difference \(Y_1-Y_0\), with a 95% interval;
- rates by scale, anchor parity, selected base child, and integer residual adjustment;
- fraction of candidates changed by the residual;
- fraction of corrected candidates that are odd.

## Relation-broken control

Within each scale and anchor parity, permute the frozen integer residual adjustments \(k(N)\) across anchors while retaining every PN27 base candidate. Use 10,000 fixed-seed permutations (`28200`). This preserves the residual distribution but breaks its relation to the chosen number.

## Decision rule

- **Strong corrective support:** corrected prime rate exceeds PN27 base on odd anchors; the one-sided paired randomisation p-value is below 0.01; and the difference is positive at all three scales.
- **Partial corrective support:** the pooled odd-anchor difference is positive but the strong threshold or every-scale condition fails.
- **Null:** the pooled odd-anchor difference is zero within exact counting precision.
- **Negative result:** the corrected rate is below the PN27 base rate.

A positive outcome would support only this declared finite residual correction. It would not establish a general prime formula, a faster prime algorithm, or universal fractal geometry.


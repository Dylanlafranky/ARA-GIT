# PN27 exact-fit child lift — frozen protocol v1

**Frozen:** 22 July 2026, before primality labels were calculated  
**Status:** native ARA one-shot arithmetic test  
**Protected 87-bit anchor:** remains sealed and is not an input

## Question

Starting only from a chosen integer and the declared child-wave pairs, does the proposed child-to-parent lift land on a prime more often than matched one-shot controls?

No sieve state, known nearby prime, next-prime function, prime gap, or primality label may enter the predictor.

## Frozen child geometry

The allowed child-wave labels and reversible pairs are

\[
W=\{1,3,5,9,11,13\},
\qquad
(1,13),\ (3,11),\ (5,9).
\]

For a chosen number \(N\), Phase A is the **numerically largest member of \(W\) that divides \(N\) exactly**:

\[
a(N)=\max\{w\in W:w\mid N\}.
\]

The paired Phase B is

\[
b(N)=14-a(N).
\]

Because \(1\in W\), the rule is defined for every positive integer. There is no nearest-lane substitution and no search over alternative pairs.

## Two recorded ARA readings

The completed Phase A child is normalised to

\[
A=1.
\]

The Phase B completion at the doubled child scale is

\[
B=\frac{1}{(N/b)/2}=\frac{2b}{N}.
\]

The child-rung deficit is therefore

\[
\Delta_{\rm child}
=2-(A+B)
=1-\frac{2b}{N}.
\]

The combined child identity in integer units is

\[
C=a+2b.
\]

The upper-rung reference and its ARA position are

\[
U=N+C,
\qquad
r_{\rm upper}=\frac{N}{U},
\qquad
\Delta_{\rm upper}=1-r_{\rm upper}.
\]

These readings are descriptive outputs. They cannot be used to inspect or adjust the candidate after the freeze.

## Frozen one-shot prediction

The singularity-crossing step is exactly \(+1\):

\[
\boxed{\widehat P(N)=N+a(N)+2b(N)+1}.
\]

Since \(b=14-a\), this is equivalently

\[
\widehat P(N)=N+29-a(N).
\]

The possible forward offsets are fixed before validation:

| Phase A \(a\) | Phase B \(b\) | Offset \(29-a\) |
|---:|---:|---:|
| 13 | 1 | 16 |
| 11 | 3 | 18 |
| 9 | 5 | 20 |
| 5 | 9 | 24 |
| 3 | 11 | 26 |
| 1 | 13 | 28 |

Worked example, frozen before the population test:

\[
N=35,\quad a=5,\quad b=9,\quad C=5+18=23,
\]

\[
U=35+23=58,
\qquad
\widehat P=58+1=59.
\]

## Fresh anchors

The following decimal strings were searched in the prime-analysis folder before this protocol was written and were absent from earlier test definitions.

For each scale, sample 10,000 distinct odd anchors and 10,000 distinct even anchors using Python's `random.Random(seed).sample` over the appropriate parity-specific range.

| Scale | Half-open interval | Odd seed | Even seed |
|---|---|---:|---:|
| low | `[73,000,000, 73,500,000)` | 27001 | 27101 |
| middle | `[73,000,000,000, 73,000,500,000)` | 27002 | 27102 |
| high | `[730,000,000,000, 730,000,500,000)` | 27003 | 27103 |

The **primary population is the 30,000 odd anchors**, because all primes above 2 are odd and the frozen rule adds an even offset. The 30,000 even anchors are a declared parity negative control: their candidates remain even.

## Blind validation

1. Generate and save anchors, child identities, ARA readings, and one-shot candidates without any primality function in the prediction script.
2. Hash and freeze that prediction file.
3. Only then run an independent validation script that attaches primality labels.
4. The protected 87-bit anchor remains sealed.

The primary endpoint is

\[
Y=\mathbf 1[\widehat P(N)\text{ is prime}].
\]

This is an exact one-shot hit. No nearby scan, ranked list, or second attempt counts as success.

## Controls

For each odd anchor, calculate after prediction freeze:

1. **Uniform allowed-offset control:** mean prime outcome over all six frozen offsets `{16,18,20,24,26,28}`.
2. **Fixed +2 control:** primality of `N+2`.
3. **Offset-permutation control:** within each scale, permute the predictor's six offsets across anchors with fixed seed `27200`, repeated 10,000 times. This preserves the exact offset distribution but breaks its relation to the chosen number.
4. **Even-anchor control:** apply the unmodified rule to even anchors.

The controls are scoring tools only. They cannot alter any ARA candidate.

## Decision rule

- **Strong predictive support:** the odd-anchor hit rate exceeds the uniform allowed-offset control and fixed +2; the one-sided permutation p-value is below 0.01; and the direction is positive at all three scales.
- **Partial predictive support:** the pooled rule exceeds the uniform allowed-offset control with a positive paired difference, but the strong threshold or every-scale direction fails.
- **Null:** the pooled rule does not exceed the uniform allowed-offset control.
- **Negative result:** it performs materially below the uniform allowed-offset control.

Regardless of outcome, report exact hit rates by scale and by selected child pair. A positive result would establish only performance of this finite arithmetic rule on the tested ranges. It would not by itself establish a faster prime algorithm, universal ARA geometry, or a proof of the fractal claim.


# PN10 factor-sphere prime-recovery protocol

**Test ID:** `PN10/FACTOR-SPHERE/PRIME-RECOVERY-AND-EARLY-RIDGE-TRANSFER/v1`  
**Declared:** 20 July 2026, before calculating any PN10 coordinate or outcome  
**Evidence class:** registered exact crosswalk plus fresh cross-scale computational transfer  
**Protected material:** do not construct the p31 primorial wheel and do not open R12

## 1. Question

Treat factorisation and sieve survival as the two reversible directions of one ARA factor sphere. Can that geometry:

1. recover primality exactly when the walk reaches its `1.0` ridge;
2. preserve the same factor relation across very different number scales; and
3. provide useful probabilistic information before the ridge is reached?

The exact recovery is expected to be mathematically equivalent to trial division. The nontrivial test is whether the
dimensionless ARA progress coordinate transfers early-ridge survivor purity from a development interval to a much
larger untouched interval better than an unscaled fixed-divisor cutoff.

## 2. Native factor-sphere coordinate

For an integer `n > 1` and a positive factor candidate `d`, define

\[
\underbrace{x_n(d)}_{\substack{\text{ARA factor position}\\0\text{ to }2}}
=
\underbrace{\frac{2\log d}{\log n}}_{\substack{\text{logarithmic factor scale}\\\text{relative to the whole }n}}.
\]

The declared landmarks are:

- `x=0`: `d=1`, the lower endpoint;
- `x=1`: `d=sqrt(n)`, the factor ridge;
- `x=2`: `d=n`, the upper endpoint.

Whenever `d` divides `n`, its paired factor is `n/d`, and

\[
x_n(d)+x_n(n/d)=2.
\]

Plainly: the small-factor walk from `1` towards `sqrt(n)` and the large-factor decomposition from `n` back towards
`sqrt(n)` are the two directions of the same factor sphere. They are not independent evidence sources.

The exact ARA prime rule is:

> Test prime factor gates in increasing order while `x_n(q) <= 1`. A divisor collision means composite. Reaching
> the ridge without a collision means prime.

Equivalently, `n` is prime exactly when its factor-sphere landmarks are only the two endpoints `{0,2}`. A prime
square `p^2` instead places `p` exactly at the `1.0` ridge, so the ridge itself is a composite collision, not a prime
signature.

## 3. Data boundaries

Two complete contiguous integer intervals are fixed:

- development `D = [1,000,000, 2,000,000)`;
- fresh evaluation `E = [2,000,000,000, 2,001,000,000)`.

Each contains exactly one million integers. PN10 will construct the development interval only after this protocol is
hashed. The fresh evaluation interval will then be constructed once, without changing the coordinate, cutoffs,
models or criteria.

The complete integer record is used. There is no sampling, Fourier transform, smoothing, NMF, SVD or learned feature
extraction.

Ordinary prime divisors, including `31`, may occur as factor gates. This does not construct or inspect the protected
full p31 primorial-wheel object.

## 4. Exact recovery test

For each integer in both intervals, the primary implementation records its least prime factor `lpf(n)`, or `0` if
none exists through `sqrt(n)`. It declares prime exactly when `lpf(n)=0`.

An independently coded segmented Sieve of Eratosthenes supplies the validation labels. Agreement is measured by
false positives, false negatives and total accuracy.

For every composite, the primary also evaluates the least-factor pair

\[
x_n(\operatorname{lpf}(n)),\qquad x_n(n/\operatorname{lpf}(n))
\]

and records the maximum departure of their sum from `2`.

For every prime square inside the declared diagnostic range `[4,100,000,000]`, it checks that the prime root maps to
`x=1` within floating-point tolerance.

## 5. Early-ridge transfer test

For a declared progress cutoff `c` on the factor diameter, define survival by

\[
\operatorname{survive}_c(n)=
\begin{cases}
1,&n\text{ is prime, or }x_n(\operatorname{lpf}(n))>c,\\
0,&x_n(\operatorname{lpf}(n))\le c.
\end{cases}
\]

The full descriptive grid is `c = 0.00, 0.05, ..., 1.00`. The primary transfer cutoffs are fixed at
`{0.25, 0.50, 0.75, 0.90}`.

At each cutoff, the development interval supplies one probability:

\[
\widehat p_D(c)=
\frac{\#\{\text{primes in D}\}}
{\#\{\text{survivors in D at }c\}}.
\]

On evaluation, an integer already hit by a divisor receives prime probability `0`; a survivor receives
`p_D(c)`. This asks how much prime information is available after walking only partway to the ridge. It is a
probability forecast, not an exact early prime generator.

### Fixed-divisor control

For each primary `c`, define the development geometric centre

\[
N_D=\sqrt{1{,}000{,}000(2{,}000{,}000-1)}
\]

and freeze one absolute factor threshold

\[
Q_D(c)=\left\lfloor N_D^{c/2}\right\rfloor.
\]

The control removes integers having a least prime factor at most `Q_D(c)` in both intervals and uses the analogous
development survivor purity as its evaluation probability. It has the same one-number development calibration but
does not scale its gate with the identity `n`.

The ARA method is also compared conceptually with ordinary scaled trial division. Those two procedures are
algebraically identical; PN10 must not claim an algorithmic speed or information advantage over the established
procedure merely because it has been re-coordinated.

## 6. Metrics

For each cutoff and model record:

- survivor count and survivor fraction;
- prime purity among survivors;
- development-to-evaluation purity error;
- Brier score over all evaluation integers;
- binary log loss in bits, with probabilities clipped only for numerical scoring at `1e-15`;
- remaining composite count.

The primary summaries average the four predeclared early-ridge cutoffs equally.

## 7. Registered criteria

### P1 — exact prime recovery

Primary ARA recovery matches the independent sieve on every integer in both intervals: zero false positives, zero
false negatives and `100%` accuracy.

### P2 — reversible factor-pair closure

The maximum absolute error in `x_n(d)+x_n(n/d)=2` is at most `1e-12` across every composite in both intervals.

### P3 — square ridge

Every checked prime square places its prime root at `x=1` with absolute error at most `1e-12`.

### P4 — accumulating information

Prime purity among survivors is non-decreasing over the full `0.00` to `1.00` grid in both intervals and equals
`1` at the ridge.

### P5 — cross-scale probabilistic value

Across the four primary early-ridge cutoffs, the factor-scaled ARA forecast has lower mean evaluation Brier score
than the fixed-divisor control.

### P6 — cross-scale calibration

Across the four primary early-ridge cutoffs, factor-scaled ARA has lower mean absolute
development-to-evaluation survivor-purity error than the fixed-divisor control.

### L1 — early exactness limit

At every primary cutoff below `1`, report whether composites remain among survivors. If they do, the current
one-coordinate method has not worked out individual primes early; it has only increased their conditional
probability. This is a required limitation, not a failed support criterion.

## 8. Interpretation boundaries

A complete P1 result establishes an exact ARA crosswalk to the classical square-root primality condition. It does
not establish a new prime theorem or a faster algorithm.

P5-P6 would show that the dimensionless diameter position is a useful scale-normalised coordinate for transferring
partial sieve state. Because standard rough-number theory also uses relative logarithmic scale, the result would be
compatible with established number theory and cannot by itself distinguish universal ARA geometry from a clean
reparameterisation of known factor structure.

Failure of P1-P3 would invalidate the proposed factor-sphere construction as implemented. Failure of P5-P6 would
show that this coordinate does not provide the claimed cross-scale probabilistic transfer against the declared
simple control.

## 9. Required artifacts

- frozen protocol and SHA-256 manifest;
- primary Python implementation;
- machine-readable JSON result and CSV path table;
- independent validator and validation result;
- reproducible executed notebook;
- readable static figure;
- technical and plain-language report;
- relational glossary amendment;
- complete manifest listing hashes of all PN10 artifacts.


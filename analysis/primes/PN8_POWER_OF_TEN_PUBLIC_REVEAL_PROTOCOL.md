# PN8 power-of-ten public-reveal pilot protocol

**Test ID:** `PN8/POWER-OF-TEN-PUBLIC-REVEAL/PILOT-v1`  
**Declared:** 19 July 2026, before any public lookup of the target primes  
**Evidence class:** prospective public-reveal pilot; five cases, descriptive rather than an effectiveness estimate  
**Protected material:** do not open R12 and do not construct the p31 primorial wheel

## 1. Question

Can the R9-R10-frozen PN7C models make useful next-state forecasts far outside their training magnitude when the
target is concealed behind a deterministic power-of-ten boundary and revealed from a public record only after every
forecast is hashed?

This is a forecast of the **ARA bin of the crossing gap**, not an exact prime generator. Five targets are enough to
demonstrate the prospective workflow and expose gross scale failure; they are not enough to estimate effectiveness.

## 2. Frozen targets

Use exactly these boundaries, in this order:

\[
10^{50},\quad 10^{100},\quad 10^{150},\quad 10^{200},\quad 10^{250}.
\]

They are an arithmetic progression of exponents chosen before lookup. Do not replace, skip or add a target because
of its prediction or revealed result.

## 3. Information permitted before reveal

For boundary `N=10^n`, calculate only the four largest primes strictly below `N`:

\[
p_{-3}<p_{-2}<p_{-1}<p_0<N.
\]

The downward search must never test an integer at or above `N`. Use Node's OpenSSL-backed
`crypto.checkPrimeSync(candidate,{checks:64})`. This is a high-confidence probable-prime input calculation, not a
formal primality certificate.

Define the three known gaps

\[
g_{-2}=p_{-2}-p_{-3},\qquad
g_{-1}=p_{-1}-p_{-2},\qquad
g_0=p_0-p_{-1},
\]

and the known ARA contexts at 24 equal bins:

\[
x_{-1}=\frac{2g_{-1}}{g_{-2}+g_{-1}},
\qquad
x_0=\frac{2g_0}{g_{-1}+g_0}.
\]

No next-prime, above-boundary primality or public sequence query is permitted before the forecast packet is written
and hashed.

## 4. Frozen models

Use the PN7C R9-R10 model packet exactly as frozen:

`9141AA398C6A6694C3C5F3ECA954681D4AD8091C01310D13C6703DB30668F3A2`.

At 24 bins save the complete distribution from:

1. `ARA-IID`: `P(x_next)`;
2. `ARA-M1`: `P(x_next | x_current)`;
3. `ARA-M2`: `P(x_next | x_previous,x_current)`;
4. `RawGap-M1`: `P(g_next | g_current)` projected through the same ARA bins.

Apply the PN7C frozen settings: categorical `alpha=0.5`, raw-gap shrinkage `lambda=64`, and raw alphabet `1..1024`.
If a known current gap exceeds 1024, RawGap-M1 uses its frozen marginal fallback; this does not alter the ARA models.

For each distribution record all 24 probabilities, the top-1 bin, top-3 bins, and the probability assigned to every
bin. Also translate the three ARA-M2 top bins into next-gap integer ranges using the known `g_0`. These ranges are
illustrative; success is scored on the fixed bin probability, not on a post-reveal narrowed number interval.

## 5. Reveal source

Only after the prediction packet and its SHA-256 hash are printed may the internet be searched. Prefer the public
OEIS record for the smallest prime greater than `10^n`; record the exact sequence URL, retrieval date and term for
each exponent. If OEIS lacks a target term, use another public exact-prime source and record that substitution before
scoring. Do not calculate the answer locally first and then call it a public reveal.

The revealed target is

\[
q_n=\min\{p\text{ prime}:p>10^n\}.
\]

Then calculate, for the first time,

\[
g_1=q_n-p_0,
\qquad
x_1=\frac{2g_1}{g_0+g_1},
\]

and its frozen 24-bin category.

## 6. Scores

For each target and model record:

- target-bin probability;
- log loss `-log2(P_target)`;
- top-1 hit;
- top-3 hit;
- target-bin rank, with tied probabilities assigned the best occupied rank.

Across five targets record mean log loss, top-1 hits and top-3 hits. Because `n=5`, do not attach a stable hit-rate
or statistical-effectiveness claim.

## 7. Pilot conditions

These conditions describe whether the demonstration is promising enough to scale. They do not validate ARA as a
prime law.

### Q1 - more than an isolated top-3 hit

ARA-M2 places at least 2 of 5 targets in its frozen top three bins.

### Q2 - arrival context helps on the public reveal

ARA-M2 mean log loss is lower than ARA-M1 mean log loss.

### Q3 - context beats frequency alone

ARA-M2 mean log loss is lower than ARA-IID mean log loss.

### Q4 - improvement is not one lucky boundary

ARA-M2 assigns higher target probability than ARA-M1 on at least 3 of 5 targets.

### Q5 - compressed ARA versus exact local gap

Diagnostic only: compare ARA-M2 with RawGap-M1 on mean log loss and top-3 hits. No direction is required because PN7C
already showed that exact current-gap magnitude can carry information discarded by the compressed ARA coordinate.

Passing Q1-Q4 permits only: "the five-target public-reveal pilot is promising enough for a larger registered test."
Failing them is evidence that this frozen representation does not transfer cleanly to these magnitudes.

## 8. Validation and boundaries

Required outputs:

- protocol hash;
- below-boundary input packet and downward-search script;
- pre-reveal prediction packet with model/input hashes;
- public source record saved only after prediction freeze;
- per-target and aggregate score files;
- independent validator that recomputes context bins, probabilities and scores without importing the scorer;
- executed notebook and durable report;
- prime-mapping update.

Even a perfect five-case result would not show exact prime generation, a physical wave cause, superiority to
Hardy-Littlewood/Cramér models, or a reliable effectiveness percentage. The next confirmatory stage would need many
more deterministic untouched boundaries and appropriate arithmetic baselines.

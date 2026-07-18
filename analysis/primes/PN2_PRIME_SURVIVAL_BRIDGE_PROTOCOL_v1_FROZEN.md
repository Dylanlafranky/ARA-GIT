# PN2/PRIME-SURVIVAL/v1 — fixed-budget bridge from the p29 wheel to actual primes

**Declared:** 17 July 2026, before generating any PN2 development or target primality labels.  
**Status:** `FROZEN BEFORE TARGET GENERATION`  
**Purpose:** determine whether ARA geometry improves out-of-sample forecasts of which p29-wheel candidates and
adjacent candidate edges survive as actual primes, beyond established density, Hardy–Littlewood, raw-gap and modular
baselines at the same sieve budget.

## 1. Scientific boundary

An exact sieve or primality test allowed to examine every divisor cannot be beaten on prime identification: it returns
the truth. PN2 therefore asks the meaningful constrained question:

> With all predictors restricted to information available after sieving only through prime 29, does an ARA
> representation improve probabilistic survival forecasts on a distant untouched number interval?

The sieve budget is fixed at the complete modular condition

\[
\gcd(n,29\#)=1.
\]

No predictor may use divisibility flags, residues, factors, prime labels, prime gaps or any other feature involving a
prime greater than 29. Primality calculations beyond 29 are used only to construct the outcome labels after the
protocol and target executable are frozen.

This experiment does not generate or inspect the PN1H `G(31#)` wheel, its gap cycle, relation planes, hierarchy
scores or any other frozen p31 endpoint. The scalar arithmetic needed to label ordinary integers as prime is not
stored as a p31 feature or summary. PN1H remains a separate sealed test.

## 2. Frozen ranges and population

- **Development interval:** `[10,000,000, 20,000,000)`.
- **Untouched target interval:** `[100,000,000, 110,000,000)`.
- Generate a small context margin outside each interval, but score only central in-range observations.
- Candidate population: every integer in range coprime to all primes through 29.
- Candidate label: `Y_i=1` when candidate `n_i` is prime; otherwise `0`.
- Edge label: `Z_i=Y_i Y_(i+1)` for adjacent p29-wheel candidates. If both endpoints survive, the edge is an actual
  consecutive-prime gap because every interior integer was already excluded by the p29 sieve.

The target interval may not be generated, summarized or inspected until the protocol file is hashed and the analysis
script verifies that hash.

## 3. Geometry available to every learned model

Let consecutive p29-wheel candidate gaps be

\[
g_i=n_{i+1}-n_i.
\]

At candidate `n_i`, define ordinary ARA

\[
x_i=\frac{2g_i}{g_{i-1}+g_i}\in(0,2).
\]

Primary ARA discretization: 12 equal bins on `[0,2]`, matching the earlier prime work. Frozen sensitivity bins:
`8,16,24`. Values are clipped only at the rightmost numerical boundary.

Candidate states:

1. raw local pair `(g_(i-1),g_i)`;
2. raw four-gap stencil `(g_(i-2),g_(i-1),g_i,g_(i+1))`;
3. plain ARA `x_i`;
4. ARA Information³ stencil `(x_(i-1),x_i,x_(i+1))`;
5. decompressed ARA: the Information³ stencil plus total local span `g_(i-1)+g_i`.

Edge states for edge `(n_i,n_(i+1))`:

1. raw gap stencil `(g_(i-1),g_i,g_(i+1))`;
2. ARA endpoint pair `(x_i,x_(i+1))`;
3. decompressed edge ARA: endpoint pair plus central gap `g_i`.

No state contains a prime/composite label, a previous actual-prime gap or information from a sieve prime above 29.

## 4. Established baselines

### 4.1 Candidate modular-density baseline

Every candidate has passed the exact p29 modular sieve. Its no-fit density forecast is

\[
p_{\mathrm{PNT29}}(n)
=
\frac{1}{\log n\prod_{q\le29}(1-1/q)}.
\]

Probabilities are clipped to `[10^-9,1-10^-9]` only for finite log loss.

### 4.2 Edge Hardy–Littlewood baseline

For an even edge gap `d`, use the standard pair singular series

\[
\mathfrak S(d)=2C_2
\prod_{q\mid d,\ q>2}\frac{q-1}{q-2},
\]

with `C_2=0.6601618158468696`. The unconditional pair approximation is divided by the exact probability that a
random pair at separation `d` passes all modular exclusions through 29. The resulting fixed-budget forecast is

\[
p_{\mathrm{HL29}}(n,d)
=
\frac{\mathfrak S(d)}{\log n\log(n+d)}
\left[
\prod_{q\le29}
\left(1-\frac{1+\mathbf 1[q\nmid d]}{q}\right)
\right]^{-1}.
\]

It is clipped only for finite log loss. The formula is calibration, not an ARA component.

### 4.3 Raw-gap controls

The raw local and raw stencil models use the exact gap identities listed above under the same fitting and smoothing
rule as the ARA states. They are the principal non-ARA comparators.

### 4.4 Information-equivalent log-ratio control

The mapped log-ratio coordinate

\[
\ell_i=\log(g_i/g_{i-1})
\]

uses bin boundaries obtained by transforming the frozen ARA boundaries exactly. It must reproduce the ARA state and
prediction row for row. Any discrepancy is an implementation failure. This control prevents a successful result from
being misreported as unique information contained only by the `0–2` coordinate.

## 5. Frozen fitting rule

Every categorical geometry model is an empirical-Bayes residual correction to its analytic baseline.

For state `s`, development count `N_s`, successes `K_s`, average analytic baseline `p0_s`, and frozen primary
shrinkage `lambda=64`, define

\[
\hat p_s=\frac{K_s+\lambda p0_s}{N_s+\lambda},
\qquad
\delta_s=\operatorname{logit}(\hat p_s)-\operatorname{logit}(p0_s).
\]

On the target, prediction is `logistic(logit(p0_target)+delta_s)`. Unseen states receive `delta=0`. Frozen
sensitivity values are `lambda in {16,32,128}`. No parameter, bin count, feature or model may be selected using the
target.

## 6. Primary endpoints and decision rule

All log losses are measured in bits per scored event; lower is better.

### P1 — candidate survival

Primary ARA model: 12-bin ARA Information³ candidate stencil.  
Primary non-ARA comparator: exact raw four-gap stencil.  
Established comparator: PNT29 modular-density baseline.

Record

\[
\Delta_C=L_{\rm best\ nonARA}-L_{\rm ARA-I3}.
\]

Support requires `Delta_C>0` and a positive lower 95% seeded block-bootstrap bound. Failure or equality is preserved.

### P2 — adjacent-edge survival and gap classes

Primary ARA model: 12-bin ARA endpoint pair.  
Primary non-ARA comparator: exact raw three-gap stencil.  
Established comparator: conditional Hardy–Littlewood `HL29` baseline.

Record

\[
\Delta_E=L_{\rm best\ nonARA}-L_{\rm ARA-edge}.
\]

Support requires `Delta_E>0` and a positive lower 95% seeded block-bootstrap bound.

For every central gap class with at least 100 target survivor edges, also compare expected and observed survivor
counts. Report total Poisson deviance and weighted absolute relative error for HL29, raw and ARA models. This is a
secondary frequency endpoint and cannot rescue failed P1/P2 log loss.

### P3 — location calibration

Divide the target interval into 20 fixed equal-width blocks. Compare predicted and actual prime-candidate survivor
counts using mean absolute percentage error and signed calibration error. This is secondary and cannot rescue P1/P2.

## 7. Robustness and controls

- Score the target in 40 fixed contiguous number-line blocks.
- Use 10,000 seeded block-bootstrap resamples (`seed=20260717`) for P1/P2 loss differences.
- Report every primary and sensitivity result, including sign reversals.
- Verify exact equality of mapped log-ratio and ARA state/predictions.
- Preserve candidate counts, positive counts, edge counts, edge positives and boundary exclusions.
- Save block losses, gap-class counts and a compact target prediction packet sufficient for independent recalculation.
- A separate validator must recompute every headline score from saved predictions and verify deterministic primality,
  modular eligibility, gap and ARA features on a seeded sample without importing the primary script.

## 8. Allowed claims

If P1 or P2 passes, allowed wording is limited to:

> At a fixed sieve budget through prime 29, the declared ARA representation improved held-out probabilistic survival
> forecasting relative to the declared raw-gap and established analytic baselines on one distant interval.

Even a full pass does not establish a new prime theorem, exact prime generator, primality test, Riemann-hypothesis
result, universal geometry or information absent from the raw gaps. Because ARA is a transformation of gap data, a
gain would demonstrate useful compression/generalization under the frozen model class, not creation of new raw
information.

If neither P1 nor P2 passes, preserve the result as evidence that ARA did not improve prime survival forecasting at
this sieve budget and target. Exact wheel mappings from PN1 remain unaffected.

## 9. Implementation stop gates

1. Hash this protocol.
2. Write the analysis and validator with the expected hash embedded.
3. Ensure the target interval is represented only as frozen constants; do not run target code during development.
4. Compile and run development-only calibration and internal assertions.
5. Hash the executable configuration.
6. Run the target once, preserve all outputs, then run the independent validator.


# PN6 native ARA circumference and log-rung protocol

**Test ID:** `PN6/NATIVE-ARA-CIRCUMFERENCE/FRESH-R11-v1`  
**Protocol frozen:** 19 July 2026, before R11 target construction  
**Model boundary:** native ARA coordinates only; established prime laws quarantined until the native verdict is sealed  
**Protected boundary:** PN1H's sealed p31 wheel-capstone target remains unopened

## Fresh target

The fresh target is the next complete 1% decimal window:

`[100,000,000,000, 101,000,000,000)`.

It contains one billion consecutive integers. Its p29-conditioned candidate and adjacent-pair sieve paths must not be
constructed until the complete native ARA prediction packet has been written and hashed.

## Native identity and direction

The declared starting identity is the population of integers not divisible by primes through 29. Sieve gates advance
from prime 31 through `sqrt(target_high-1)`.

At each of 24 fixed normalized log-gate cells,

\[
\underbrace{S_r(g)}_{\substack{\text{surviving share}\\\text{at rung }r}}
=\frac{N_{r,g}}{N_{r,0}},
\qquad
\underbrace{x_r(g)}_{\substack{\text{ARA diameter}\\\text{release reading}}}
=2\bigl(1-S_r(g)\bigr).
\]

The orientation is fixed: `x=0` is all members retained; `x=2` is all members released. No pole reversal is permitted
after target access.

## Canonical circumference decompression

The 0-2 diameter is decompressed onto a unit circle centred at 1:

\[
\underbrace{x_r(g)}_{\text{diameter projection}}
=1-\cos\!\left(
\underbrace{\theta_r(g)}_{\substack{\text{circumference phase}\\0\le\theta\le\pi}}
\right),
\]

so the independently observed survival reading determines

\[
\theta_r(g)=\arccos\bigl(2S_r(g)-1\bigr).
\]

This is not an arbitrary fitted circle: centre, radius, branch and orientation are fixed by the canonical ARA 0-2
geometry before the target. The upper monotone phase branch `0<=theta<=pi` is used throughout.

## Log-rung withdrawal law

For equal steps in decimal rung `r=8,9,10`, define the phase increment

\[
\delta_r(g)=\theta_r(g)-\theta_{r-1}(g).
\]

One shared withdrawal factor is fitted across both declared identities—candidate and adjacent pair—using only
R8-R10:

\[
\underbrace{\rho}_{\substack{\text{shared phase-increment}\\\text{withdrawal across rungs}}}
=
\frac{
\sum_{e\in\{c,p\}}\sum_g
\delta_{9,e}(g)\,\delta_{10,e}(g)
}{
\sum_{e\in\{c,p\}}\sum_g
\delta_{9,e}(g)^2
}.
\]

The frozen R11 prediction is

\[
\widehat\theta_{11,e}(g)
=
\theta_{10,e}(g)+\rho\bigl[\theta_{10,e}(g)-\theta_{9,e}(g)\bigr],
\]

\[
\widehat S_{11,e}(g)=\frac{1+\cos\widehat\theta_{11,e}(g)}{2}.
\]

This is the primary native ARA circle-plus-log-rung model. It contains no independent-sieve product, prime-density
formula, Buchstab coordinate, Fourier component, SVD/NMF component or future target label.

## Native comparison paths

All comparison paths also use only opened direct ARA/source readings:

### Candidate

1. `home_r10`: copy the R10 survival path.
2. `direct_log_rung`: `S10^2/S9`.
3. `circle_secant_rho1`: canonical circle phase with `rho=1`.
4. `circle_shared_rho_primary`: canonical circle phase with the shared fitted `rho`.
5. `circle_candidate_rho_sensitivity`: the same rule with `rho` fitted from candidate phase alone.

### Adjacent pair

1. `home_r10`: copy the R10 pair path.
2. `direct_log_rung`: `E10^2/E9`.
3. `circle_secant_rho1`: direct pair circumference phase with `rho=1`.
4. `circle_shared_rho_primary`: direct pair circumference phase with the shared fitted `rho`.
5. `circle_edge_rho_sensitivity`: the same rule with `rho` fitted from pair phase alone.
6. `circle_candidate_plus_j_secondary`: candidate primary squared times a directly transferred pair relation,
   `J11=J10+rho(J10-J9)`.

The two pair constructions test the same target identity from two native routes: direct pair circumference and
candidate-parent plus retained coupling relation. Their frozen path disagreement must be reported.

No primary prediction may be clipped, smoothed, monotonized or repaired. Any invalid probability, phase reversal or
non-monotone primary path is an automatic failure.

## Development calibration recorded before target

The same shared-rho rule is backtested once from R7-R9 to R10. Its R10 phase RMSE is recorded but cannot be used to
alter the R11 model after this protocol. A target phase RMSE below `0.015` radians for both identities is the declared
transfer tolerance.

## Scoring

- binomial log loss in bits per at-risk event across all 24 cell hazards;
- survival-path RMSE;
- circumference-phase RMSE;
- terminal absolute relative error;
- observed next-rung withdrawal factors fitted separately for candidates and pairs.

## Decision rules

- `P1`: candidate primary beats Home on path log loss, has terminal error below 1%, and phase RMSE below 0.015.
- `P2`: pair primary beats Home on path log loss, has terminal error below 1%, and phase RMSE below 0.015.
- `P3`: candidate primary beats the direct native log-rung path on path log loss.
- `P4`: pair primary beats the direct native log-rung path on path log loss.
- `P5`: the R11 observed candidate and pair withdrawal factors are each within 0.15 of frozen shared `rho` and within
  0.10 of each other.
- `P6`: both primary paths are valid, monotone and require no repair.
- `P7`: the direct-pair and candidate-plus-`J` native predictions agree before target with survival RMSE below 0.002,
  and after target both have terminal error below 1%.

`P1+P2+P5+P6` support recurrence of the shared native circumference/log-rung geometry. `P3+P4` test whether the
circle decompression adds predictive value beyond direct logarithmic extrapolation. P7 tests route closure.

## Interpretation boundary

The native verdict is written before any established prime-law comparison. If the native model fails, that failure
is retained as evidence against this formulation. A missing coordinate, alternate branch, different distortion or
new orientation may be proposed only as a new protocol on new data; it cannot rescue R11 retrospectively.

Only after the native result is sealed may a separate audit compare established prime laws. That audit cannot change
the PN6 pass/fail ledger.

## Target construction and validation

The target is constructed by an exact bounded-memory segmented Eratosthenes sieve. An adjacent pair dies at the first
gate removing either endpoint. The independent validator must repeat the entire one-billion-integer construction
with a different chunk size and separately coded implementation.

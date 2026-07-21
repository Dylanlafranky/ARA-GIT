# PN5 multiplicative rung-transfer protocol

**Test ID:** `PN5/MULTIPLICATIVE-RUNG/FRESH-R10-v1`  
**Protocol frozen:** 19 July 2026, before construction of the R10 target  
**Status at freeze:** predictions only; target unopened  
**Protected boundary:** PN1H's sealed p31 wheel-capstone packet will not be read, modified or opened

## Fresh target

The target is the complete p29-conditioned sieve path in

`[10,000,000,000, 10,100,000,000)`.

This continues the decimal sequence used by PN3A: each R6-R10 window has width 1% of its lower bound. The target
contains 100,000,000 consecutive integers. Its path, candidate counts, pair counts and prime outcomes must not be
constructed until the prediction packet has been written and hashed.

## Question

PN4 found that the cross-rung survivor deformation transfers more accurately as a multiplicative ratio than as an
additive displacement on the 0-2 line. PN5 asks whether that newly identified rule transfers prospectively to R10.

At each of the same 24 fixed normalized log-gate cells,

\[
S=\frac{N_{\rm alive}}{N_0},
\qquad
x=2(1-S),
\qquad
S_{\rm ind}=\prod_{31\le q\le Q}\left(1-\frac1q\right).
\]

Define the vertical rung-coupling coordinate

\[
\underbrace{k_c(t)}_{\substack{\text{candidate log-ratio}\\\text{relative to sieve envelope}}}
=
\log\!\left(\frac{S_c(t)}{S_{c,\rm ind}(t)}\right),
\]

and the candidate/pair relation

\[
\underbrace{J(t)}_{\substack{\text{pair relation}\\\text{beyond candidate squared}}}
=
\log\!\left(\frac{S_e(t)}{S_c(t)^2}\right).
\]

The primary frozen ARA transfer is

\[
\widehat k_{c,10}(t)=k_{c,9}(t),
\qquad
\widehat J_{10}(t)=J_9(t),
\]

so

\[
\widehat S_{c,10}=S_{c,\rm ind,10}e^{k_{c,9}},
\qquad
\widehat S_{e,10}=\widehat S_{c,10}^{,2}e^{J_9}.
\]

Plainly: preserve the proportionate departure from the established sieve envelope when moving up one decimal rung,
then preserve the explicit relation between single-candidate and adjacent-pair survival.

## Mandatory equivalence statement

The primary candidate equation is algebraically identical to prior-rung raw multiplicative-ratio transfer. The pair
equation is identical to transferring `S_edge/S_edge_independent`. PN5 can test prospective recurrence and the utility
of the ARA decomposition, but it cannot demonstrate information unique to ARA unless an independently defined ARA
constraint later separates it from this raw identity.

## Frozen models

### Candidate path

1. `independent_sieve`: exact product through each target cell.
2. `ara_additive_previous_rule`: PN4's additive 0-2 residual transfer from R9.
3. `ara_multiplicative_primary`: preserve `k_c` from R9.
4. `ara_log_gradient_secondary`: extrapolate `k_c,10 = 2 k_c,9 - k_c,8`.
5. `buchstab_established`: `S_ind exp(gamma) omega(u)`, with `u=log(X_mid)/log(Q)` and Buchstab's function defined by
   `omega(u)=1/u` for `1<=u<=2` and `(u omega(u))'=omega(u-1)` for `u>2`.

### Adjacent-pair path

1. `independent_pair`: candidate independent path squared.
2. `ara_additive_edge_previous_rule`: PN4's direct additive edge residual.
3. `ara_multiplicative_primary`: candidate primary path squared times `exp(J9)`.
4. `ara_log_gradient_secondary`: candidate log-gradient path squared times `exp(2J9-J8)`.
5. `buchstab_squared`: established candidate Buchstab path squared.
6. `buchstab_plus_source_relation`: Buchstab candidate path squared times `exp(J9)`; this is the strongest declared
   hybrid control for the pair relation.

All prediction paths are generated and hashed before target construction. Cell boundaries depend only on target
bounds and prime gates. Predictions are clipped only for numerical validity and monotonicity; every adjustment must
be reported.

The established terminal comparators are p29-conditioned PNT/Mertens,

\[
S_{c,\rm terminal}=S_{c,\rm ind}\frac{e^\gamma}{2},
\qquad
S_{e,\rm terminal}=S_{e,\rm ind}\left(\frac{e^\gamma}{2}\right)^2.
\]

## Scoring

- binomial log loss in bits per at-risk event across the 24 cell hazards;
- survival-path RMSE;
- terminal absolute relative error;
- observed R10 paths for `k_c(t)` and `J(t)` compared with frozen R8/R9 paths.

## Decision rules

- `P1`: candidate primary beats independence and the prior additive ARA rule on path log loss, with terminal error
  below 1%.
- `P2`: pair primary beats independent pair and the prior additive edge rule on path log loss, with terminal error
  below 1%.
- `P3`: the primary candidate `k_c` path is closer to R10 than R8's `k_c` path is, and the primary pair `J` path is
  closer to R10 than R8's `J` path is, measured by RMSE. This tests nearest-rung recurrence rather than convergence
  direction alone.
- `P4`: candidate primary beats the Buchstab established path on path log loss.
- `P5`: pair primary beats `buchstab_plus_source_relation` on path log loss.
- `P6`: neither primary path requires clipping or monotonic repair.

`P1+P2+P3+P6` support prospective multiplicative rung recurrence. `P4+P5` would be needed before claiming an
advantage over the declared established sieve envelope. Even a full pass would remain one fresh R10 transfer, not a
universal prime law.

## Target construction

The target is built by an exact segmented Eratosthenes sieve in bounded chunks. An integer enters the starting
population iff it is not divisible by any prime through 29. Its death gate is its smallest prime factor above 29;
zero denotes survival through all gates up to `sqrt(target_high-1)`. An adjacent pair dies at the first gate that
removes either endpoint and survives only when both endpoints survive.

The primary builder saves aggregate cell counts, not a 100-million-row integer table. The independent validator must
repeat target construction with a different chunk size and separately coded loop.

## Required artifacts

- frozen prediction builder, prediction packet and hashes;
- target builder and exact aggregate target packet;
- scoring script, results, paths and figure;
- independent target/metric validator;
- executed reader-facing notebook;
- result report and durable prime-mapping update.

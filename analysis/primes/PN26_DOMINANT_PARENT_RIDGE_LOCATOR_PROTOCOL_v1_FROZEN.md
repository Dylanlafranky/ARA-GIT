# PN26 dominant-parent ridge locator protocol — frozen v1

**Test ID:** `PN26/DOMINANT-PARENT-RIDGE-LOCATOR/v1`  
**Frozen:** 22 July 2026, 09:53 AEST, before target construction or target primality was calculated  
**Development authority:** `PN19_POST_TARGET_SECOND_GO_ROBUSTNESS.json` (already opened)  
**Protected 87-bit anchor:** remains sealed and is not an input

## Question

PN19 found, after its sealed target, that the first quiet location of its connection-heavy Phase A parent was the
actual next prime on `93.2%` of 1,000 opened anchors. The actual prime was among the first two Phase A quiet
locations on `99.9%`, and among the first three on `100%`.

PN26 prospectively tests the corrected ARA statement reached after PN25:

> The fixed cross-rung `3.5` route identifies the scale frame. It cannot locate a prime by itself because it is the
> same for every anchor. The signed integer correction must come from the unresolved child-wave state. A complete
> recursively compressed Phase A parent should locate most prime ridges on its first quiet state; its second and
> third quiet states should supply a short ranked lock when the first state is a false survivor.

This is **not** the PN20 two-individual-factor rule. Phase A is one complete parent containing many lower prime-gate
children. The experiment asks whether that complete first parent is a useful lossy sufficient statistic, not whether
two factor labels replace the sieve.

## Frozen ARA construction

For each scale cohort, let `S` be the cohort's lower boundary and declare the rung domain `S -> 2S`. Generate all
prime children

\[
p\leq\lfloor\sqrt{2S}\rfloor.
\]

Split the ordered children once where cumulative logarithmic weight is closest to half:

\[
E_A=2\frac{\sum_{p\in A}\log p}{\sum_{p\in A\cup B}\log p},
\qquad
E_B=2-E_A.
\]

`A` is the lower, frequent, connection-heavy complete parent. `B` is retained for TE-ARA accounting and scientific
interpretation, but **is not consulted by the primary locator**.

For a target anchor `N` in that cohort, define a Phase A quiet location by

\[
S_A(N+t)=1
\quad\Longleftrightarrow\quad
N+t\text{ is divisible by no child }p\in A.
\]

The primary method seals the first three positive quiet offsets

\[
0<t_{A,1}<t_{A,2}<t_{A,3}.
\]

The single-candidate prediction is `N+t_A,1`; the two- and three-reading predictions are ranked lists, not
post-hoc adjustable formulas.

## The `3.5` cross-rung frame

The declared route is recorded exactly as

\[
\underbrace{2}_{\text{full rung span}}
+
\underbrace{1}_{\text{chosen-number identity}}
+
\underbrace{\frac12}_{\text{same identity viewed at }2S}
=\frac72=3.5.
\]

Because this value is identical for every target, it is registered as a **scale/context coordinate with zero
discriminative variance**. PN26 will not credit it with locating the prime. Candidate variation must come from
`S_A`.

## Fresh target cohorts

The primary script samples 2,000 distinct deterministic anchors from each unopened interval:

| Cohort | Interval | Seed |
|---|---|---:|
| low | `[71,000,000, 71,500,000)` | 26001 |
| middle | `[71,000,000,000, 71,000,500,000)` | 26002 |
| high | `[710,000,000,000, 710,000,500,000)` | 26003 |

The protected 87-bit anchor must not appear in source, targets, outputs or notebook.

## Separation and freeze

1. Freeze this protocol, the primary prediction script, validator and cohort parameters by SHA-256.
2. Run the primary script. It may generate lower prime children and Phase A masks, but contains no primality test,
   next-prime routine or target label.
3. Save all 6,000 ranked predictions before any target truth is opened.
4. Run the independent validator. It reconstructs the parent masks separately, constructs a full segmented-prime
   truth mask, and verifies actual next-prime locations with deterministic Miller–Rabin.
5. Refuse to overwrite sealed prediction artifacts.

## Registered predictions

Development rates are frozen only as thresholds; no target refitting is permitted.

- **P1 — dominant first reading:** the first Phase A quiet candidate is the exact next prime on at least `90%` of
  all fresh anchors.
- **P2 — second reading:** the exact next prime is among the first two Phase A quiet candidates on at least `99%`.
- **P3 — information-three lock:** the exact next prime is among the first three Phase A quiet candidates on at
  least `99.9%`.
- **P4 — nontrivial enrichment:** the three-candidate Phase A list exceeds the three-candidate `p<=29` wheel control
  by at least 50 percentage points.
- **P5 — frame honesty:** every target has the exact `3.5` route and its variance is zero; it is reported as context,
  not as a predictor.
- **P6 — independent reconstruction:** all primary ranked candidates are reproduced exactly and all truth checks
  pass.

## Allowed result classes

- **Strong dominant-parent support:** P1–P6 pass.
- **Partial dominant-parent support:** P1 or the ranked P2/P3 compression passes, but not all predictive thresholds.
- **Dynamic null:** the fresh ranked list does not beat controls materially or misses the registered thresholds.
- **Implementation failure:** freeze, reconstruction, primality or ordering checks fail.

Even a strong result remains a compressed partial-sieve result. Phase A contains thousands of child gates; three
visible readings do not mean three arithmetic operations, a constant-time prime algorithm, or a new primality
theorem.

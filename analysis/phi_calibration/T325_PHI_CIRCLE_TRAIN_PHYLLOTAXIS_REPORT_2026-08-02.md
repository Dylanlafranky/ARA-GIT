# T325 — Phi circle-train in ordered plant phyllotaxis

**Date:** 2 August 2026  
**ARA geometry and interpretation:** Dylan La Franchi  
**Protocol formalisation, implementation and boundary audit:** Codex  
**Verdict:** **MIXED / PARTIAL CALIBRATION — ordered parent carrier supported; isolated Phi child-step gate failed**

## Technical summary

T325 tested the ARA Phi circle-train on 359 public, ordered divergence-angle
measurements from 58 *Arabidopsis thaliana* plants. The source is Source Data
21 from Tameshige et al. (2025), whose methods measure the angle between
successive primordia around the meristem centre from confocal images using
ImageJ. The source and earlier T302 result had already been inspected, so this
is a frozen construct/calibration test rather than an independent discovery.

The result is a clean scale separation:

- on an isolated child placement, the rational `3/8` coordinate was the best
  fixed rule (`6.743°` median error), narrowly ahead of exact Phi (`6.986°`);
- when the same placements were accumulated in their real order as one parent
  carrier, exact Phi became the best fixed rule (`5.429°`), ahead of `8/21`
  (`6.524°`) and far ahead of `3/8` (`10.239°`);
- real within-plant order beat order-shuffled placements (`p=0.0263`);
- neighbouring deviations compensated rather than adding freely
  (`C=0.319`; within-order `p=0.0185`; broken-lineage `p=0.0008`);
- at Fibonacci return lags `2,3,5`, exact Phi had the lowest fixed-profile
  error (`0.003229` ARA), ahead of `8/21` (`0.006933`) and `3/8`
  (`0.046616`).

This supports the bounded ARA reading that a connected local child may be
well represented by `3/8`, while its ordered handover through successive time
slices follows a Phi-like parent carrier. It does not establish a universal
Phi law.

## ARA geometry tested

One full azimuthal turn is one parent ARA cycle:

\[
360^\circ\longleftrightarrow 0\ldots2.
\]

For recorded divergence angle \(\theta_i\), the child increment is

\[
u_i=\frac{\theta_i}{180^\circ}.
\]

The published wild-type orientation is the approximately `137.5°` branch, so
the predeclared source-compatible Phi increment is

\[
\delta_\phi=2-\frac{2}{\phi}=\frac{2}{\phi^2}
=0.7639320225\ldots
=137.507764^\circ.
\]

The child test compares each \(u_i\) with each fixed landmark. The parent test
anchors the observed plant after its first two placements, then predicts every
later cumulative position without re-anchoring:

\[
p_i=(p_{i-1}+u_i)\bmod2,
\qquad
\widehat p_{a+h}=(p_a+h\delta)\bmod2.
\]

The one-step score asks, “What does each child look like alone?” The carrier
score asks, “What path do those children collectively build when lineage and
order are retained?”

## Main numerical results

| Fixed model | Isolated child median error | Ordered parent median error |
|---|---:|---:|
| `3/8` local child | **6.743°** | 10.239° |
| `8/21` Fibonacci rational | 6.986° | 6.524° |
| exact Phi | 6.986° | **5.429°** |
| `1/e` | 9.091° | 18.375° |
| `2/5` phase | 7.194° | 14.122° |
| half-turn ridge | 40.503° | 120.302° |

The development-only best carrier increment was `0.76628 ARA`
(`137.9304°`). Its 95% plant-bootstrap interval was
`0.75557..0.77997 ARA`, which contains exact Phi. On confirmation plants the
free fit scored `4.646°` versus Phi's `5.429°`; under the frozen two-sided
bootstrap gate this was not a separable improvement. The data therefore favour
a small neighbourhood containing Phi rather than identify its exact decimal
with unlimited precision.

## Ordered carrier and lineage controls

The exact-Phi carrier had median error `0.030164 ARA` (`5.429°`). Holding each
plant's first two placements fixed and shuffling only its later increments gave
a null median of `0.039756 ARA` (`7.156°`). The true ordering was lower with
empirical `p=0.0263`.

For adjacent Phi residuals \(e_i=u_i-\delta_\phi\), the compensation ratio was

\[
C=
\frac{\operatorname{median}|(e_i+e_{i+1})/2|}
{\operatorname{median}[(|e_i|+|e_{i+1}|)/2]}
=0.319.
\]

The within-plant order null had median `0.486` (`p=0.0185`), while pairings
constructed from different plant lineages had median `0.625` (`p=0.0008`).
Thus local deviations largely cancel within the true lineage instead of
behaving as unrelated errors.

## Fibonacci near-return fingerprint

The observed median parent return distances at lags `2,3,5` were
`0.472117`, `0.287217`, and `0.175253 ARA`. Exact Phi predicted
`0.472136`, `0.291796`, and `0.180340`. Its mean absolute profile error was
`0.003229 ARA`, the lowest fixed candidate.

The lag-2 agreement was especially close: the observed and Phi-predicted
returns differed by `0.0000193 ARA`, or about `0.0035°`. This is a bounded
three-lag fingerprint from short sequences, not a proof of an unlimited
Fibonacci recurrence.

## Biological perturbation diagnostic

The fixed Phi parent error increased away from wild type:

| Genotype | Confirmation plants | Phi carrier median error |
|---|---:|---:|
| wild type `Col` | 10 | 5.429° |
| `e2` | 9 | 11.477° |
| `e1e2` | 9 | 29.660° |

This is consistent with the source's perturbation context, but it is a
diagnostic rather than an independently frozen causal test.

## Robustness and validation

- Phi remained the best fixed parent carrier after removing the longest
  confirmation sequences and after removing the shortest sequence.
- The exact Phi increment lay inside the development-fit bootstrap interval.
- The independent validator reconstructed the workbook, plant lineages,
  modulo-2 positions, every fixed one-step and carrier score, the Fibonacci
  profile, file hashes, row counts and artifact bounds without importing the
  analysis script. It passed `46/46` checks.
- The source workbook records angles to `0.001°`, but the physical ImageJ
  measurement uncertainty was not reported in the workbook. Recorded decimal
  precision must not be mistaken for physical accuracy.

## Scientific and ARA conclusions kept separate

**Established-data statement:** the wild-type sequence is organized near the
golden-angle neighbourhood, ordered cumulative prediction is better for exact
Phi than for the declared fixed controls, and the sequence contains local
error compensation and Fibonacci-lag return structure.

**ARA interpretation:** the best isolated child coordinate is the connected
`3/8` approximation, while the ordered parent carrier is Phi-like. This is the
specific “connection cooled locally; handover retained through ordered
movement” geometry that the circle-train procedure was designed to detect.

**Not established:** a literal hidden Phi circle, universal ARA geometry,
physical chirality, a causal biological Phi operator, or external replication.

## Verdict

T325 passes the parent-carrier, free-fit compatibility, real-order, local
compensation, broken-lineage and Fibonacci-profile gates. It fails the strict
requirement that exact Phi also win the isolated one-step gate, and it is not
an external holdout.

The honest verdict is therefore:

\[
\boxed{\text{MIXED / PARTIAL CALIBRATION}}
\]

The substantive result is stronger and more specific than “plants contain
Phi”: in this ordered record, local child placements sit slightly nearer
`3/8`, but their accumulated parent path shifts decisively toward exact Phi.

## Provenance and reproduction

- Source: [Tameshige et al., *Nature Communications* (2025)](https://www.nature.com/articles/s41467-025-65792-y)
- Frozen protocol: `T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_PROTOCOL_v2_FROZEN.md`
- Analysis: `t325_phi_circle_train_phyllotaxis.py`
- Independent validation: `validate_t325_phi_circle_train_phyllotaxis.py`
- Machine result: `T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_RESULTS.json`
- Validation record: `T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_VALIDATION.json`

```powershell
python t325_phi_circle_train_phyllotaxis.py
python validate_t325_phi_circle_train_phyllotaxis.py
```

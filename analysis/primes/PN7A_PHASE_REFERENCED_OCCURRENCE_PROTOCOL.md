# PN7A phase-referenced occurrence protocol

**Test ID:** `PN7A/PHASE-REFERENCED-OCCURRENCE/OPENED-DEVELOPMENT-v1`  
**Operator lock:** 19 July 2026, before reconstructing the PN7A position-by-stage matrices  
**Evidence class:** opened-data structural diagnostic; not a blind prediction  
**New-target state:** no R12 target is constructed or read  
**Protected boundary:** the sealed PN1H p31 full-wheel target remains unopened

## 1. Confirmed geometry

Dylan confirmed the intended interpretation of “occurrence in relation”:

1. use how the adult Connection/Space Phase-A wave changes across decimal R rungs to establish orientation;
2. use where its individual removal/survival events occur inside each rung as a confirming relational edge;
3. align the within-rung occurrence record to adult Phase-A circumference before looking for a recurring opposite-wave
   candidate.

This protocol tests that representation on already opened R7-R11 data. It cannot supply fresh predictive evidence.

## 2. Data boundary

Use the complete historically opened 1% decimal windows:

| Rung | Interval | Status |
|---|---|---|
| R7 | `[10,000,000, 10,100,000)` | opened |
| R8 | `[100,000,000, 101,000,000)` | opened |
| R9 | `[1,000,000,000, 1,010,000,000)` | opened |
| R10 | `[10,000,000,000, 10,100,000,000)` | opened by PN5 |
| R11 | `[100,000,000,000, 101,000,000,000)` | opened by PN6 |

The starting population is integers not divisible by primes through 29. Every candidate is assigned its first later
prime divisor through `sqrt(window_high-1)`, or terminal-survivor status if none exists.

## 3. Direct adult Phase A

Divide later primes from 31 through each rung's `qmax` into the same 24 fixed normalized log-gate cells used by
PN4-PN6. For candidate or adjacent-edge identity (e):

\[
\underbrace{S_{r,e}(g)}_{\text{direct retained share}}
=\frac{N_{r,e,g}}{N_{r,e,0}},
\]

\[
\underbrace{x_{A,r,e}(g)=2[1-S_{r,e}(g)]}_{\text{adult Connection Phase-A diameter}},
\qquad
\underbrace{\theta_{A,r,e}(g)=\arccos[2S_{r,e}(g)-1]}_{\text{adult circumference position}}.
\]

Cross-rung movement at the same normalized gate progress is

\[
\underbrace{V_{r,e}(g)=\theta_{A,r,e}(g)-\theta_{A,r-1,e}(g)}_{\text{vertical occurrence/orientation landmark}}.
\]

## 4. Raw within-rung occurrence record

Split each integer window into 64 equal ordered position bins from low number to high number. The orientation is fixed
and may not be reversed per rung.

For every identity and gate cell, retain:

- exposure: identities entering from each position bin;
- release count: identities first removed in that gate cell and position bin;
- terminal count: identities retained through `qmax` and position bin.

Prime-stage release is then aligned to the midpoint circumference phase of the adult cell in which it occurs:

\[
\theta^{\rm event}_{r,e,g}
=\frac{\theta^{\rm before}_{r,e,g}+\theta^{\rm after}_{r,e,g}}{2}.
\]

Terminal survivors are reported separately and are not assigned an invented post-`qmax` release phase.

## 5. Native recursive occurrence ARA

At each adult gate cell, compare exposure-normalized release hazards in the left and right children of a position node:

\[
h_L=\frac{D_L}{N_L},
\qquad
h_R=\frac{D_R}{N_R},
\]

\[
\underbrace{x_O=\frac{2h_R}{h_L+h_R}}_{\substack{\text{within-rung occurrence ARA}\\0=\text{left},\ 2=\text{right}}},
\qquad
\underbrace{a_O=x_O-1=\frac{h_R-h_L}{h_R+h_L}}_{\text{signed occurrence lean}}.
\]

Calculate this without smoothing at three predeclared dyadic depths:

- depth 0: whole window split into two halves — primary slow/adult occurrence coefficient;
- depth 1: each half split into quarters — two daughter coefficients;
- depth 2: each quarter split again — four granddaughter coefficients.

The primary lateral curve is the depth-0 coefficient across the 24 adult gate cells. Depths 1-2 test whether the
visible structure is actually dominated by faster child occurrence.

## 6. Phase alignment and matched control

For R9-R11, linearly interpolate each depth-0 occurrence curve onto one 24-point grid over the circumference-phase
range common to all three rungs. No cyclic shift, rung-specific flip, smoothing or lag optimization is allowed.

The matched control compares the same unmodified depth-0 curves at the original normalized log-gate progress. Thus:

- **Phase-referenced recurrence:** correlation after adult-circumference alignment.
- **Raw-gate recurrence:** correlation at the original cell indices.
- **Alignment gain:** phase-referenced correlation minus raw-gate correlation.

Report R9-R10, R10-R11 and R9-R11 separately, then their mean. R7-R8 are small-sample context only.

## 7. Triangulation endpoints

For candidate and adjacent-edge identities separately, report:

1. vertical movement recurrence: correlation of (V_{10}) with (V_{11});
2. lateral root recurrence under Phase-A alignment and raw-gate control;
3. candidate-edge agreement of aligned lateral root curves at R10 and R11;
4. correlation between the aligned lateral root and aligned vertical movement at R10 and R11;
5. mean-square occurrence coefficient at depths 0, 1 and 2;
6. terminal occurrence lean as a separate endpoint-only diagnostic.

The sign of the vertical-lateral correlation locates the candidate direction. It is descriptive here; it is not
silently optimized or called Time merely for being negative.

## 8. Development decision rule

Label a **common phase-referenced opposite-wave candidate located** only if all conditions hold on R9-R11:

1. mean Phase-A-aligned lateral recurrence exceeds `0.50` for candidates and edges;
2. phase alignment improves mean recurrence over raw-gate alignment for both identities;
3. candidate-edge aligned-root correlation exceeds `0.50` at both R10 and R11;
4. vertical-lateral correlations have the same non-zero sign at R10 and R11 for both identities, with absolute
   correlation above `0.25`;
5. depth-0 mean-square coefficient exceeds the per-coefficient mean square at depths 1 and 2 on both R10 and R11.

If only conditions 1-3 hold, record **phase-referenced occurrence structure**, not an opposite wave. If alignment does
not improve the raw control, this representation does not support Dylan's correction. Thresholds are development
gates only and cannot be represented as fresh evidence.

## 9. Exploratory locator

Only after the registered endpoints are sealed, an exploratory lag scan may show where the lateral curve best aligns
with (V), (-V), or another quadrant of adult phase. That scan may propose one frozen R12 orientation but cannot
alter the PN7A verdict.

## 10. Non-tautology and interpretation fences

- Do not define the observed Phase B as `-A`, `2-x_A`, `sqrt(1-A^2)` or `theta_A+pi`.
- Do not use Fourier, SVD or NMF to construct the primary occurrence coordinate.
- Do not treat future removal stage as a prospective input; PN7A is diagnostic.
- Do not select a position-bin count, dyadic depth, phase shift or orientation after seeing which looks strongest.
- Do not treat exact survival/release accounting as evidence beyond a calibrated crosswalk.
- Do not rename a residual Time without recurrent independent occurrence structure.
- Preserve all failures and rung-specific disagreements.

## 11. Required artifacts

- exact position-by-stage aggregate packet and hashes;
- deterministic analysis script and executed notebook;
- primary figure showing adult Phase A, raw versus phase-aligned lateral occurrence and depth structure;
- machine-readable results;
- independently coded validation;
- report and mapping-ledger update with the opened-development evidence boundary visible.


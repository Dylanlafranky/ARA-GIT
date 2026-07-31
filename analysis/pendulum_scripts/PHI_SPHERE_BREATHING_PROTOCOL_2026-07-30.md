# Frozen instrument — Phi as orientation advance of a breathing ARA sphere

**Frozen:** 30 July 2026, before this calculation was run.  
**Test ID:** `T301-PHI-SPHERE-BREATHING-v1`  
**Status:** ARA-first descriptive test on public records that have been used in earlier,
different pendulum analyses. This is a newly frozen endpoint, but not a pristine-data
prospective prediction.

## 1. Claim being tested

The proposed operation is not that a literal inhale/exhale duration must equal Phi and
not that the local hexagon-to-pentagon lock angle must climb from 60° to 72°.

The narrower claim is:

> A locally closed circle or sphere can expand and contract while its orientation advances
> through the next time slice. If Phi is the efficient non-repeating handover, successive
> complete breaths should advance by
> \(u_\phi=\phi^{-2}=0.381966\) of a turn more specifically than nearby rational and
> irrational alternatives.

For a raw coupled state

\[
\mathbf q(t)=(q_1(t),\ldots,q_d(t)),
\]

define

\[
r(t)=\|\mathbf q(t)\|,
\qquad
\widehat{\mathbf q}(t)=\frac{\mathbf q(t)}{\|\mathbf q(t)\|}.
\]

`r` is the radial accumulation/release cut. The unit vector is the direction in which
that breath occupies the measured state-sphere.

## 2. Public data

Source: dynamicslab *MultiArm-Pendulum*, Zenodo `10.5281/zenodo.6633719`.

- 2D cut: double-pendulum free-swing runs 1–4;
- 3D cut: triple-pendulum free-swing runs 1–3.

Run roles:

- development/reporting context: double run 1 and triple run 1;
- frozen pooled endpoints: double runs 2–3 and triple run 2;
- confirmation endpoints: double run 4 and triple run 3.

Only raw timestamps and raw arm angles enter the endpoint. No Fourier transform,
Hilbert phase, normal-mode model, fitted pendulum equation, SVD/POD or learned model
is used.

## 3. Fixed representation

Each raw arm angle is circular-mean centred using that record alone. Triple records are
regularly decimated from 10 kHz to 1 kHz; the double records are already approximately
1 kHz. This is sample selection, not filtering.

At every retained time sample, calculate the Euclidean radius of the centred angle
vector. A radial maximum is eligible when:

- its prominence is at least `5%` of the record's `95th–5th` percentile radial range;
- it lies at least `0.20 × 1.333 s` from another selected maximum; and
- its radius is non-zero.

The `1.333 s` reference and the pendulum spacing family predate this test. Sensitivity
checks use prominence `{2%, 5%, 10%}` and spacing
`{0.15, 0.20, 0.30} × 1.333 s`; they cannot replace the primary result.

## 4. Half-breath and whole-breath orientation steps

For selected radial maxima \(i\) and \(j\), define the unsigned spherical angle

\[
\delta_{ij}
=
\frac{1}{2\pi}
\arccos\!\left(
\widehat{\mathbf q}_i\cdot\widehat{\mathbf q}_j
\right)
\in[0,0.5].
\]

Two steps are retained:

- `lag 1`: maximum \(i\rightarrow i+1\), a diagnostic that can expose ordinary
  opposite-pole alternation;
- `lag 2`: maximum \(i\rightarrow i+2\), the primary complete-breath comparison after
  one intervening opposite-side maximum.

The lag-2 definition was chosen before inspecting these results. It prevents a simple
back-and-forth oscillator from being mislabelled as a carrier merely because adjacent
radial maxima are antipodal.

## 5. Frozen candidates

For every candidate \(a\), proximity is the absolute distance
\(|\delta-a|\).

| Candidate | Fraction of turn |
|---|---:|
| recurrence | `0` |
| pi conjugate | `pi − 3 = 0.141593` |
| quarter | `1/4 = 0.25` |
| e conjugate | `3 − e = 0.281718` |
| third | `1/3 = 0.333333` |
| close rational | `3/8 = 0.375` |
| **Phi** | `phi^-2 = 0.381966` |
| close rational | `2/5 = 0.4` |
| silver irrational | `sqrt(2) − 1 = 0.414214` |
| opposition | `1/2 = 0.5` |

Phi specificity requires Phi to have the smallest pooled median lag-2 distance. Merely
landing in a broad “golden neighbourhood” does not pass; Phi must beat `3/8` and `2/5`.

## 6. Identity-maintenance endpoint

For a lag-2 event, radial retention is

\[
R_i=\frac{\min(r_i,r_{i+2})}{\max(r_i,r_{i+2})}.
\]

For each candidate, define candidate proximity

\[
P_a=1-\frac{|\delta-a|}{0.5}.
\]

Within each run, Spearman correlation is calculated between \(P_a\) and \(R_i\).
The pooled statistic is the event-count-weighted Fisher-z mean across the frozen
records. Phi passes maintenance specificity only if:

1. its pooled correlation is positive;
2. a `5,000`-permutation within-run test gives one-sided `p < 0.05`; and
3. its correlation exceeds those of `3/8`, `2/5`, recurrence and opposition.

## 7. Controlled geometry benchmark

A separate deterministic circle benchmark advances points by each candidate step:

\[
\theta_{n+1}=(\theta_n+2\pi a)\bmod 2\pi.
\]

For horizons `N=4…200`, it records:

- nearest recurrence to the starting point;
- largest uncovered circular gap;
- circular discrepancy.

This benchmark asks what each step does when it is supplied as the generator. It is an
implementation/control result, not empirical evidence that nature selected Phi.

## 8. Frozen verdict

Four equally weighted empirical families:

1. Phi is the best 2D lag-2 candidate on pooled double runs 2–3;
2. Phi is the best 3D lag-2 candidate on triple run 2;
3. both confirmation records retain Phi as the best or tied-best candidate;
4. Phi uniquely predicts greater next-breath radial retention.

- `4/4`: supported for this instrument;
- `2–3/4`: mixed;
- `0–1/4`: not supported.

## 9. Boundaries

- The state-space radius is a declared ARA cut, not a claim that Euclidean angle space
  is literal physical space.
- TE-ARA closure is not tested by normalizing the direction vector.
- A fixed-pivot pendulum does not contain the Solar System's external galactic carrier.
  A null result rejects Phi on this measured state-sphere breathing coordinate, not
  every possible higher common-mode carrier.
- The geometry benchmark can show why Phi is a strong non-repeating winding. It cannot
  establish that an observed system uses it.
- Previous relevant results remain unchanged: literal resting breath duty ratio is
  below Phi; the 60°→72° Hexagon–Pentagon angle dial was not supported; T300 rejected
  Phi as the local four-child recurrence step.

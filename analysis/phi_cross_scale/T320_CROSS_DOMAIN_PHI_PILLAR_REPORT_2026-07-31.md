# T320/T320A — Cross-domain Phi-pillar transfer

**Date:** 31 July 2026  
**Identity-boundary correction:** **THE INTENDED HANDOVER WAS NOT TESTED**  
**Retained narrow result:** **cross-arm state triangle NOT SUPPORTED as Phi-shaped — 1/5 gates**  
**Cross-domain verdict at T320:** **NO ELIGIBLE PHYSICAL TEST OF THE INTENDED HANDOVER YET**  
**Independent validation:** **9/9 checks passed**

**Subsequent corrections:** T321 tested a same-arm routed `A -> B -> A`
trajectory and selected `2` (`median q=1.965901`), not Phi. Dylan later
clarified that the intended golden-section object is instead the direct
cross-scale ratio `A(parent)/A(child)`, without a Phase-B measurement vertex.
T322 tests that corrected object. See the T321 and T322 reports. T320 remains
a separate cross-arm cut and is not retrospectively re-labelled.

## Answer first

The previous test used the wrong identity boundary. It assigned three separate
pendulum arms to \(A_0,B,A_1\). Dylan's intended handover instead follows one
identity through time:

\[
\underbrace{A_{j,k}\rightarrow B_{j,k}\rightarrow A_{j,k+1}}_{
\text{complete around-the-circle octave route}}=2,
\qquad
\underbrace{A_{j,k}\rightarrow A_{j,k+1}}_{
\text{direct same-phase pillar}}\stackrel{?}{=}\phi.
\]

Here \(j\) fixes the arm. The Phase-A state is compared with that **same
arm's next Phase-A swing**, with its intervening Phase-B swing defining the
around-route. This exact temporal, identity-preserving relation was not
measured by T320 or T320A. Their numbers therefore cannot support or reject
the intended Phi handover.

T320A remains useful as a narrower descriptive cross-arm coupling cut. For
the public free-swing evaluation record, that different object's normalized
direct-route coordinate was

\[
q=\frac{2d(A_0,A_1)}{d(A_0,B)+d(B,A_1)}=1.88651\quad\text{(median)}.
\]

For the cross-arm triangle, the closest frozen landmark was `2`, not Phi. The two route legs were also
strongly unequal, and the included angle did not select the pentagon's
`108°` signature. Both mirror branches independently chose `2`.

The physical alignment was real: keeping the actual middle arm produced less
Phi error than shifting that arm in time. But a coupling can be highly
structured without having the proposed Phi-pillar shape. Here the observed
route was much closer to a nearly direct, unequal-leg passage.

## Why `2` here is an observation rather than a forced answer

The measured coordinate

\[
q=2\times\frac{\text{direct endpoint distance}}
{\text{sum of the two observed route legs}}
\]

can occupy the entire interval from `0` to `2`; the triangle inequality only
provides those bounds. It is **not** forced to equal `2`. A value near `2`
means the two-leg route is nearly as short as the direct route. In this
dataset that occurs mainly because the legs are unequal, so the middle-scale
state often lies much nearer one endpoint than the other.

## Mapping actually used — retained but superseded for the handover claim

The public dynamicslab *MultiArm-Pendulum* archive supplied three
simultaneously measured states:

\[
\underbrace{\text{arm 3}}_{A_0\text{ / child scale}}
\rightarrow
\underbrace{\text{arm 2}}_{B\text{ / intermediate scale}}
\rightarrow
\underbrace{\text{arm 1}}_{A_1\text{ / larger scale}}.
\]

These are three different physical identities, not successive Phase-A states
of one identity. Each state used its raw rest-centred angle and angular velocity. One pair of
robust coordinate scales was calculated from free runs 1–2 and frozen before
run 3 was evaluated. No Fourier transform, fitted mode or pendulum equation
entered the route coordinate. Consequently, the calculation measures a
simultaneous cross-arm state triangle only.

## Intended physical mapping

For each arm independently, the required cut follows one Phase-A swing, the
intervening Phase-B swing, and the following Phase-A swing of that same arm.

The arm label must remain fixed; only time advances. The other arms may be
used later as coupling context or controls, but they cannot substitute for
the two same-identity Phase-A endpoints.

## Fidelity correction retained in the record

T320 v1 mistakenly required the cross-rung Phase-A endpoints to point in the
same instantaneous phase-plane direction and the middle Phase-B state to
point oppositely. That conflated an ARA identity label with a vector sign.

The exact pentagon itself shows the error: the labelled same-phase endpoints
span `144°` around its centre; they need not be parallel. The v1 filter left
only four evaluation windows and is retained as a failed operationalization,
not as evidence against the pillar.

T320A removed that unjustified condition before the corrected statistic was
calculated. It retained every non-degenerate raw sample and produced `601`
non-overlapping `0.10 s` evaluation windows.

## Retained cross-arm results — not a handover verdict

### Direct-route coordinate

| Candidate | Median absolute error |
|---|---:|
| `1` | 0.88651 |
| \(\sqrt2\) | 0.48460 |
| `1.5` | 0.41270 |
| \(\phi\) | 0.31560 |
| \(\sqrt3\) | 0.23077 |
| **`2`** | **0.11349** |

The median coordinate was `1.88651`. Both sign-labelled mirror reports chose
`2`:

- A-positive branch: `q = 1.89649`;
- B-negative branch: `q = 1.87717`.

### Triangle shape

- median included angle at the middle state: `129.85°`;
- frozen angle-landmark winner by median absolute error: `144°`, not `108°`;
- median equal-leg ratio: `0.23315`, far below the registered `0.90` gate.

The low leg balance is decisive. This is not an approximately regular
pentagon triangle even though some individual windows pass near Phi.

### Relation-broken controls

The actual middle-arm alignment had Phi error `0.31560`. Shifting only the
middle arm gave:

| Middle-arm shift | Median Phi error |
|---:|---:|
| real alignment | **0.31560** |
| 17% | 0.57329 |
| 31% | 0.38305 |
| 47% | 0.71069 |

Thus the real coupling carries non-random route geometry. It simply does not
select Phi as its best landmark.

### Driven transfer

The independently retained driven record was even closer to the complete
route pole:

- median `q = 1.98866`;
- winner `2` with median error `0.01134`;
- median angle `167.01°`;
- angle winner `180°`;
- median equal-leg ratio `0.62595`.

This transfer result strengthens the specific pendulum conclusion: the
three-arm state triangle tends toward a near-direct closure under the tested
driven condition, not a regular-pentagon shortcut.

## Frozen gates

| Gate | Result |
|---|:---:|
| Phi uniquely wins the route coordinate | fail |
| `108°` uniquely wins the included angle | fail |
| equal-leg ratio at least `0.90` | fail |
| both mirror branches choose Phi | fail |
| real middle state beats all shifted controls on Phi error | **pass** |

Cross-arm triangle verdict: **NOT SUPPORTED — 1/5**.  
Intended same-arm temporal handover verdict: **NOT TESTED**.

## Cross-domain audit

The eligibility check prevented unlike Phi questions from being pooled:

| Domain/result | What it contributes | Complete physical route eligible? |
|---|---|:---:|
| T319 regular pentagon | exact \(2\) versus \(\phi\) construction | mathematical benchmark |
| sunflower scale lineage | Phi/Phi-squared ordered-scale calibration | no |
| T302 Arabidopsis / T305 scheduling | cumulative carrier and coverage | no |
| Q46/Q47 quantum | nested parents/children and recurrence | no |
| T317 Solar System | one A/B pair plus external parent frame | no |
| T320A triple pendulum | three simultaneous but distinct arm identities | **no** |

At the close of T320/T320A, the repository contained no completed raw
physical test of the intended same-identity temporal route. The cross-arm
result must not be counted as either a success or a failure of that claim.
T321 subsequently supplied a same-arm routed `A -> B -> A` test and returned
a separate negative result for that object. T322 records Dylan's later
clarification that the golden-section object is the direct cross-scale
`A(parent)/A(child)` relation. The exact geometry and sunflower scale
calibration remain separate records, not independent physical replications.

## Plain-language explanation

Imagine travelling from one Phase-A point to the next in two ways. The long
way visits Phase B and is called the full `2` route. The proposed shortcut is
Phi. In a perfect pentagon, that is exactly true.

T320A instead asked whether three different pendulum arms make that triangle.
They do form a meaningful coupled path—the result changes when the middle arm
is time-shifted—but this is not Dylan's handover object. T321 then measured
the same-arm routed cycle. T322 measures the still more specific direct
relation between parent-scale and child-scale occurrences of the same phase
type.

## Reproduction

From `analysis/phi_cross_scale`:

```powershell
F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe t320_cross_domain_phi_pillar.py
F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe t320a_cross_domain_phi_pillar_fidelity.py
F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe validate_t320a_cross_domain_phi_pillar.py
```

Primary artifacts:

- `T320_CROSS_DOMAIN_PHI_PILLAR_PROTOCOL_v1_FROZEN.md`
- `T320_CROSS_DOMAIN_PHI_PILLAR_RESULTS.json`
- `T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY_CORRECTION_v1.md`
- `T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY_RESULTS.json`
- `T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY_WINDOWS.csv`
- `T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY.png`
- `T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY.svg`
- `T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY_VALIDATION.json`

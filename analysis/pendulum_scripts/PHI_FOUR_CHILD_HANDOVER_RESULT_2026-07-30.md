# Phi four-child handover — frozen pendulum result

**Date:** 30 July 2026  
**Frozen verdict:** **MIXED — 2/4 check families passed**  
**Data:** public dynamicslab driven double-pendulum runs, Zenodo
`10.5281/zenodo.6633719`

## Plain-language result

Dylan's four-child correction was productive. The second driven
double-pendulum run contained four distinct coupled child states, and their
collective handover supplied two Phi-positive readings:

1. the point at which all four children had appeared was closest to the Phi
   locations;
2. cycles whose child allocation was closer to the Phi quartet retained the
   parent's next amplitude substantially better.

However, the result is **not specifically or universally Phi**:

- the complete four-child allocation was closer to a simpler irregular
  `(1,2,3,4)` shape than to the Phi quartet;
- equal-quarter proximity predicted retention almost as well as Phi proximity;
- the frozen monotonic test “greater inequality produces greater retention”
  ran in the opposite direction;
- the first development run behaved differently.

The strongest ARA reading is therefore:

> The handover is collective and four-child. Parent retention improves when
> two weak children become materially involved and the quartet moves away from
> an extreme two-child lock. Phi is a plausible location for that transition,
> but this test does not establish Phi as its unique constant.

## Frozen geometry

Two centred raw arm signs generated:

\[
(A,B)\times(A,B)
\rightarrow
(C_{AA},C_{AB},C_{BB},C_{BA}).
\]

Across `50` frozen parent cycles, all four children appeared in `44` (`88%`).
Their median shares were:

| child | median share |
|---|---:|
| \(C_{AA}\) | `0.3940` |
| \(C_{AB}\) | `0.1373` |
| \(C_{BB}\) | `0.4129` |
| \(C_{BA}\) | `0.1023` |

This is clearly asymmetric: two diagonal children dominate while two smaller
cross-children keep participating.

## The four frozen checks

### 1. Exact Phi quartet — failed

Median total-variation distance:

| four-child template | distance; lower is better |
|---|---:|
| linear irregular `(1,2,3,4)` | **`0.1829`** |
| paired/dyadic | `0.2171` |
| Phi quartet | `0.2550` |
| equal quarters | `0.2829` |

The quartet is irregular, but its full allocation is not specifically the
predeclared Phi gap pattern.

### 2. Collective completion location — passed, narrowly

The median circular distance from the first all-four completion to each
landmark was:

| landmark | median distance |
|---|---:|
| Phi `0.382/0.618` | **`0.03586`** |
| thirds | `0.04100` |
| quarters | `0.12249` |
| ridge/opposition | `0.13139` |
| poles | `0.36861` |

Phi beat thirds by only `0.00514` in the headline medians. A post-verdict
paired Wilcoxon comparison favoured Phi (`28/44` cycles, one-sided
`p=0.0108`), but a bootstrap interval for the median-distance advantage
crossed zero (`−0.0225` to `+0.0144`). This pass is real under the frozen rule
but fragile.

### 3. Monotonic inequality operationalisation — failed and reversed

\[
\rho(I_4,R_P)=-0.563,
\qquad
p_{\rm shift}=0.946.
\]

Within this frozen regime, extreme two-child dominance was associated with
poorer next-cycle amplitude retention.

The low-retention quartile had median shares approximately
`(0.449, 0.060, 0.428, 0.081)`. The high-retention quartile had
`(0.396, 0.154, 0.292, 0.155)`. The parent did better when the two small
children participated more, while the distribution remained unequal.

**Post-freeze clarification:** Dylan's intended claim was not that inequality
should be maximised. It was that a non-zero irregular allocation must remain
inside the complete TE-ARA budget so the children do not reach terminal
resonant closure. Codex translated that into an unnecessarily monotonic
“more inequality is better” endpoint. The negative statistic honestly rejects
that frozen endpoint; it does not reject bounded maintained asymmetry.

Occupancy shares alone cannot test the clarified claim. Equal occupation need
not mean phase resonance, and unequal occupation does not by itself prove
non-resonance. The next instrument must retain the ordered transition phases
and their recurrence from one parent cycle to the next.

### 4. Phi-shaped allocation predicts retention — passed

\[
\rho(P_\phi,R_P)=+0.655,
\qquad
p_{\rm shift}=0.00020.
\]

This association survived decimation from `1 kHz` through `200 Hz`
(`rho=0.655–0.658`).

The specificity fence matters. Post-verdict correlations were:

| allocation proximity | Spearman correlation with parent retention |
|---|---:|
| Phi quartet | `+0.655` |
| equal quarters | `+0.645` |
| linear irregular | `+0.584` |
| paired/dyadic | `−0.645` |

Phi is nominally strongest, but only barely stronger than equal quarters.
This positive result primarily says that movement away from the extreme
paired/dyadic lock predicts retention. It is not yet a unique Phi signature.

## Development-versus-frozen change

The first driven run had a much stronger two-child lock:

`(0.489, 0.0148, 0.483, 0.0110)`.

There, child inequality positively tracked retention (`rho=+0.463`) while
Phi proximity tracked it negatively (`rho=−0.475`). The frozen run reversed
both relations. Consequently, the four-child mechanism appears
**regime-dependent**, not a fixed universal allocation.

## What the correction changed

The earlier test asked where one child turned and found a pole. This test asks
when the complete four-child relation has handed over. Those are different
events:

- **one child turns:** pole/opposition event;
- **all four children have participated:** collective closure/handover event.

The latter is where a Phi-adjacent result appeared. That supports Dylan's
geometric correction as a useful measurement distinction, while the controls
prevent the result from being overstated.

## Reproduction

From `analysis/pendulum_scripts`:

```powershell
F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe phi_four_child_handover_test.py
F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe validate_phi_four_child_handover.py
```

Machine-readable outputs:

- `phi_four_child_handover_results.json`;
- `phi_four_child_handover_cycles.csv`.

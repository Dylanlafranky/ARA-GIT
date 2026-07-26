# Q1 open-qubit multi-axis ARA protocol v1 - FROZEN

**Protocol ID:** `Q1-OPEN-QUBIT-MULTI-AXIS-v1`  
**Ledger ID:** `T258`  
**Frozen:** 23 July 2026, 23:18 AEST, before development data, target data, code or outcomes  
**Fidelity source:** `Q1_OPEN_QUBIT_MULTI_AXIS_FIDELITY_v1.md`  
**Status:** FROZEN

## Question

Can several independently measured ARA diameter cuts through one open-qubit identity preserve state distinctions
that one compressed diameter cannot, while remaining exactly equivalent to the ordinary Bloch-coordinate account
when both receive the same information?

This is a controlled known-referee instrument test. It is not a claim that ARA derives quantum mechanics.

## Registered prediction

Under finite two-outcome sampling, the three-axis ARA reconstruction will:

1. distinguish unitary rotation, pure dephasing, longitudinal relaxation and combined rotation-relaxation;
2. recover rotation direction and the coherent-versus-incoherent distinction hidden from the `Z` cut;
3. predict held-out directional cuts;
4. exactly match the same-information Bloch-vector account; and
5. lose the registered distinctions when time order or axis identity is destroyed.

The expected value of every directional reading is

\[
x_{\hat n}(t)=1-\mathbf r(t)\cdot\hat n.
\]

## Known-referee systems

Every trial starts at

\[
\mathbf r(0)=(1,0,0),
\]

the `|+>` state. Use `65` equally spaced samples on \(t\in[0,4]\).

For each paired base draw:

- \(|\Omega|\sim U(0.8,1.6)\), with equiprobable sign;
- \(T_1\sim U(1.5,3.0)\);
- \(T_\phi\sim U(1.0,2.5)\).

The four mechanism families are:

### U - unitary rotation

\[
\mathbf r_U(t)=
\left(\cos\Omega t,\ \sin\Omega t,\ 0\right).
\]

### T1 - longitudinal relaxation

\[
\mathbf r_{T1}(t)=
\left(e^{-t/(2T_1)},\ 0,\ 1-e^{-t/T_1}\right).
\]

### T2 - pure dephasing

\[
\mathbf r_{T2}(t)=
\left(e^{-t/T_\phi},\ 0,\ 0\right).
\]

### C - combined rotation and relaxation

\[
\frac1{T_2^{\rm total}}=\frac1{2T_1}+\frac1{T_\phi},
\]

\[
\mathbf r_C(t)=
\left(
e^{-t/T_2^{\rm total}}\cos\Omega t,\
e^{-t/T_2^{\rm total}}\sin\Omega t,\
1-e^{-t/T_1}
\right).
\]

`U` and `C` share the same paired \(\Omega\). `T1` and `C` share the same paired \(T_1\). By construction,
`U` and `T2` have the same exact `Z` cut, while `T1` and `C` have the same exact `Z` cut.

## Finite observations

For axis \(i\in\{X,Y,Z\}\),

\[
p_i(t)=x_i(t)/2,
\qquad
K_i(t)\sim\operatorname{Binomial}(S,p_i(t)),
\qquad
x_i^{\rm obs}(t)=2K_i(t)/S.
\]

Use shot counts

\[
S\in\{32,64,128,256,512,1024\}.
\]

The registered primary shot count is `128`.

## Split and seeds

- development seed: `2026072301`;
- target seed: `2026072302`;
- held-out/control seed: `2026072303`;
- development: `64` paired base draws, all four mechanisms, at `128` shots only;
- target: `128` fresh paired base draws, all four mechanisms, at every shot count.

Target outcomes may not tune thresholds, features or families.

## ARA reconstruction

For the fixed orthogonal cuts,

\[
\widehat{\mathbf r}_{\rm raw}
=
\left(1-x_X^{\rm obs},1-x_Y^{\rm obs},1-x_Z^{\rm obs}\right).
\]

If \(\|\widehat{\mathbf r}_{\rm raw}\|>1\), project radially to the Bloch ball:

\[
\widehat{\mathbf r}
=
\frac{\widehat{\mathbf r}_{\rm raw}}
{\max(1,\|\widehat{\mathbf r}_{\rm raw}\|)}.
\]

This is the registered physical reconstruction. Retain the raw reconstruction as a descriptive control.

## Registered features

1. **Rotation score and direction:** weighted slope of the unwrapped transverse angle
   \(\operatorname{atan2}(\widehat r_y,\widehat r_x)\), using samples whose transverse radius is at least `0.20`.
2. **Relaxation score:** mean \(\widehat r_z\) over the final `8` samples minus its mean over the first `8`.
3. **Ridge-coherence score:** mean \(\|\widehat{\mathbf r}\|\) over the final `8` samples.

On development only, choose each binary threshold by exhaustive midpoint search maximizing balanced accuracy.
Resolve ties with the numerically smallest threshold.

The four-class rule is:

| Relaxation | Rotation | Predicted family |
|---|---|---|
| no | yes | `U` |
| no | no | `T2` |
| yes | no | `T1` |
| yes | yes | `C` |

The separate `U` versus `T2` ridge test uses the development-selected ridge-coherence threshold.

## Registered comparators and controls

1. **One-axis `Z` account:** apply only the relaxation bit; map no-relaxation to `U` and relaxation to `T1`.
   This intentionally cannot distinguish the registered same-`Z` pairs.
2. **Same-information Bloch account:** independently implement the ordinary Bloch-vector reconstruction with
   the same three observations and physical projection. It should tie ARA exactly.
3. **Native four-model fit:** minimum three-axis mean-square error over a fixed standard-physics template grid:
   \(\Omega\in\{\pm0.8,\pm1.2,\pm1.6\}\),
   \(T_1\in\{1.5,2.0,2.5,3.0\}\), and
   \(T_\phi\in\{1.0,1.5,2.0,2.5\}\).
4. **Time shuffle:** apply one random common time permutation to all three axes in each trial before scoring.
5. **Axis shuffle:** apply one random permutation of the three axis labels in each trial before scoring.
6. **Raw unphysical reconstruction:** omit radial projection.
7. **Zero-transverse held-out control:** predict held-out directions from the measured `Z` component only.

## Held-out directions and complement check

Draw `16` independent uniform sphere directions per target trial. For each:

\[
\widehat x_{\hat n}=1-\widehat{\mathbf r}\cdot\hat n.
\]

Score mean absolute error against the known clean directional reading. Independently sample the opposite direction
and report the finite-shot complement residual \(x_{\hat n}^{\rm obs}+x_{-\hat n}^{\rm obs}-2\).

## Primary endpoints and frozen gates

All primary gates use the fresh target set at `128` shots.

| Endpoint | Frozen gate |
|---|---:|
| Four-class accuracy | \(\ge 0.90\) |
| Accuracy gain over `Z` only | \(\ge 0.30\) |
| Rotation-direction accuracy on rotating families | \(\ge 0.90\) |
| `U` versus `T2` ridge accuracy | \(\ge 0.95\) |
| Held-out directional MAE | \(\le 0.08\) |
| Same-information ARA/Bloch maximum score difference | \(\le10^{-12}\) |
| Same-information ARA/Bloch classification disagreement | \(=0\) |
| Time-shuffled accuracy | \(\le0.65\) |
| Axis-shuffled accuracy | \(\le0.65\) |

All gates must pass for `SUPPORTED`. Any clean gate failure is `NOT SUPPORTED`. A code, identifiability or
registered-design failure is `INCONCLUSIVE`.

## Secondary outputs

- all registered endpoints across the shot-count ladder;
- native-model-fit accuracy;
- physical versus raw reconstruction error;
- radius error and unphysical raw-state frequency;
- per-family confusion matrices;
- held-out directional MAE by family;
- finite-shot antipodal complement residual;
- paired bootstrap intervals over base draws.

These outputs are descriptive and cannot replace a failed primary gate.

## Required reporting boundary

The report must give two separate conclusions:

1. **benchmark conclusion:** whether the frozen instrument gates passed;
2. **geometry conclusion:** what the result says about one diameter versus several cuts through the same identity.

Even a perfect result would demonstrate a faithful, useful coordinate decomposition of standard qubit geometry.
It would not independently establish hidden ontological waves, derive quantum mechanics, prove universal fractality,
or show an advantage over standard tomography.

## Planned artifacts

- `q1_open_qubit_multi_axis_test.py`
- `q1_open_qubit_multi_axis_validate.py`
- `Q1_OPEN_QUBIT_MULTI_AXIS_DEVELOPMENT.csv`
- `Q1_OPEN_QUBIT_MULTI_AXIS_TRIALS.csv`
- `Q1_OPEN_QUBIT_MULTI_AXIS_AGGREGATES.csv`
- `Q1_OPEN_QUBIT_MULTI_AXIS_TRAJECTORIES.csv`
- `Q1_OPEN_QUBIT_MULTI_AXIS_RESULTS.json`
- `Q1_OPEN_QUBIT_MULTI_AXIS_REPORT_2026-07-23.md`


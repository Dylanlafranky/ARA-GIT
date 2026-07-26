# Q1 open-qubit multi-axis ARA report

**Ledger:** `T258`  
**Protocol:** `Q1-OPEN-QUBIT-MULTI-AXIS-v1`  
**Frozen before outcomes:** 23 July 2026, 23:18 AEST  
**Protocol SHA-256:** `f51c0b44a29869f90af88ada873f1363441424dfc9e2584fcdc5b19215700a2b`  
**Registered verdict:** **SUPPORTED — 9/9 frozen gates passed**  
**Independent validation:** **14/14 checks passed**

## Answer first

The test supports the exact bounded claim: several independently measured ARA diameter cuts through one qubit
retain directional and coherence information that one diameter necessarily discards. At the registered `128`-shot
condition, the frozen three-cut account classified `511/512` fresh mechanism trials (`99.80%`) while the
predeclared `Z`-only account classified `256/512` (`50.00%`). It predicted unmeasured directional cuts with mean
absolute error `0.06112`.

The same-information ARA and ordinary Bloch accounts were exactly identical: zero state difference, zero feature
difference and zero classification disagreements. A standard four-family quantum-model fit scored `512/512`.
Therefore this is a successful ARA decompression and coordinate-fidelity result, not an advantage over quantum
tomography and not a derivation of quantum mechanics.

## Registered geometry

For a qubit with Bloch vector \(\mathbf r(t)\), each declared measurement direction \(\hat n\) gives the ARA cut

\[
\boxed{
x_{\hat n}(t)=1-\mathbf r(t)\cdot\hat n
}
\]

with

\[
x_{\hat n}=0,\ 1,\ 2
\quad\Longleftrightarrow\quad
\mathbf r\cdot\hat n=+1,\ 0,\ -1.
\]

Opposite cuts satisfy the exact identity

\[
x_{-\hat n}=2-x_{\hat n}.
\]

The sparse complete three-axis reconstruction is

\[
\widehat{\mathbf r}_{\rm raw}
=
\left(1-x_X^{\rm obs},1-x_Y^{\rm obs},1-x_Z^{\rm obs}\right).
\]

Finite-shot noise can place this raw estimate outside the physical Bloch ball. The registered physical account
projects it radially back to radius one:

\[
\widehat{\mathbf r}
=
\frac{\widehat{\mathbf r}_{\rm raw}}
{\max(1,\|\widehat{\mathbf r}_{\rm raw}\|)}.
\]

In Dylan's geometry language, `X`, `Y` and `Z` are different ARA line cuts through the same sphere and at the same
rung. In standard quantum language, they are three independent Pauli expectation coordinates of one state.

## Known-referee mechanisms

Every trial started from the same state,

\[
\mathbf r(0)=(1,0,0).
\]

The fresh target contained `128` paired parameter draws for each mechanism and every shot count.

| Family | Native dynamics | What the cuts must retain |
|---|---|---|
| `U` | unitary transverse rotation | direction through time; radius remains one |
| `T2` | pure dephasing | transverse radius contracts while `Z` remains at its ridge |
| `T1` | longitudinal relaxation | `Z` moves while transverse amplitude decays |
| `C` | rotation plus relaxation | both directional rotation and longitudinal change |

The pairing makes the one-axis information loss exact:

\[
x_Z^U(t)=x_Z^{T2}(t)=1,
\]

and, for paired \(T_1\),

\[
x_Z^{T1}(t)=x_Z^C(t).
\]

No one-dimensional `Z` method can distinguish either pair from those observations alone. This is not a weak
baseline trick; it is the registered geometric question.

## Frozen primary result

All values below were computed on the untouched `128`-shot target after the development thresholds had been fixed.

| Frozen endpoint | Required | Observed | Result |
|---|---:|---:|---|
| Four-class accuracy | \(\ge0.90\) | `0.998047` (`511/512`) | PASS |
| Gain over `Z` only | \(\ge0.30\) | `+0.498047` | PASS |
| Rotation-direction accuracy | \(\ge0.90\) | `1.000000` (`256/256`) | PASS |
| `U` versus `T2` ridge accuracy | \(\ge0.95\) | `1.000000` (`256/256`) | PASS |
| Held-out directional MAE | \(\le0.08\) | `0.061123` | PASS |
| ARA/Bloch maximum feature difference | \(\le10^{-12}\) | `0` | PASS |
| ARA/Bloch classification disagreements | `0` | `0` | PASS |
| Time-shuffled accuracy | \(\le0.65\) | `0.455078` | PASS |
| Axis-shuffled accuracy | \(\le0.65\) | `0.523438` | PASS |

**Frozen verdict:** **SUPPORTED (`9/9`)**.

The single ARA error was one combined trial classified as `T1`. Every `U`, `T2` and `T1` trial was correctly
classified, as were `127/128` combined trials.

## Matched comparisons

| Account | Information supplied | Primary accuracy | Interpretation |
|---|---|---:|---|
| ARA multi-axis | noisy `X/Y/Z` cuts | `99.80%` | compact direction/relaxation/radius features |
| Bloch multi-axis | the same noisy `X/Y/Z` cuts | `99.80%` | exactly identical reconstruction and decisions |
| Native model fit | the same noisy `X/Y/Z` cuts plus a fixed standard model grid | `100.00%` | established physics reference |
| `Z` only | noisy `Z` cut | `50.00%` | exact information ceiling for the paired families |
| Time shuffled | `X/Y/Z`, time order destroyed | `45.51%` | directional evolution is necessary |
| Axes shuffled | `X/Y/Z`, axis identity destroyed | `52.34%` | cut orientation is necessary |

The ARA/Bloch tie is the key honesty control. Because

\[
\mathbf r=(1-x_X,1-x_Y,1-x_Z),
\]

the two accounts are the same measured state written from opposite coordinate origins. ARA's value here is the
faithful geometry and the compact diagnostic decomposition, not extra state information.

## Noise ladder

| Shots per axis/time | ARA accuracy | Rotation direction | `U`/`T2` ridge | Held-out MAE | Raw estimates outside sphere |
|---:|---:|---:|---:|---:|---:|
| 32 | `91.21%` | `89.84%` | `100%` | `0.11997` | `28.14%` |
| 64 | `95.90%` | `96.88%` | `100%` | `0.08613` | `22.73%` |
| 128 | `99.80%` | `100%` | `100%` | `0.06112` | `18.43%` |
| 256 | `100%` | `100%` | `100%` | `0.04339` | `16.62%` |
| 512 | `100%` | `100%` | `100%` | `0.03076` | `15.55%` |
| 1024 | `100%` | `100%` | `100%` | `0.02168` | `15.15%` |

The decreasing held-out error is close to the expected finite-sampling \(1/\sqrt S\) behaviour. The raw
out-of-sphere frequency does not vanish quickly because pure unitary states lie on the boundary: even small
outward noise is unphysical. Radial projection consistently improved reconstruction and held-out error, but only
slightly at the registered condition (`0.06112` versus `0.06203` held-out MAE).

The finite-shot antipodal complement error at `128` shots was `0.08675`. That does not violate
\(x_{\hat n}+x_{-\hat n}=2\): the clean expectation identity is exact, while two independently sampled finite-shot
estimates fluctuate around it.

## Uncertainty

Paired bootstrap resampling over the `128` base draws gave:

- ARA accuracy, `90% CI = [0.99414, 1.00000]`;
- ARA gain over `Z`, `90% CI = [0.49414, 0.50000]`.

The `90%` Wilson intervals for both perfect `256/256` binary endpoints were

\[
[0.98954,1.00000].
\]

These intervals quantify target-draw variation inside this synthetic design; they do not cover different physical
noise models, calibration errors or model misspecification.

## What the geometry result means

One `1.0` reading is not one unique state. On the `Z` cut,

\[
x_Z=1
\quad\Longleftrightarrow\quad
r_z=0.
\]

That condition includes:

- every pure coherent equatorial state, whose radius is one and whose direction can rotate;
- partially dephased equatorial states, whose radius lies between zero and one;
- the maximally mixed centre, whose radius is zero.

The single diameter sees only the plane's intersection coordinate. The other cuts and radius distinguish where
the state sits inside that plane. This directly confirms Dylan's “ant farm against the glass” description for this
known geometry: the line cut is accurate, but it does not contain the full sphere.

For one qubit, three orthogonal cuts are already informationally complete because its density matrix has three
independent real coordinates. Measuring every angle would add redundant, noise-averaging views rather than new
degrees of freedom. For larger quantum systems, however, the required state space grows rapidly; this sparse
three-cut result must not be carried upward unchanged.

## Two-output conclusion

### 1. Benchmark conclusion

**SUPPORTED.** The frozen instrument passed all `9/9` gates on fresh target data and independent validation passed
`14/14`. It preserved mechanism, rotation direction, ridge coherence and held-out directional information under
finite sampling. Destroying time order or axis identity destroyed the registered performance.

### 2. Geometry conclusion

**SUPPORTED as an exact standard-physics crosswalk.** Several ARA diameters are coupled projections of one qubit
sphere; one diameter is many-to-one, while an informationally complete set reconstructs the state. The same-data
ARA and Bloch accounts coincide exactly.

## What this does not establish

This result does **not** establish:

- that ARA derives the Born rule or open-system quantum mechanics;
- that the qubit contains a physically discovered hidden Phase B;
- that quantum is literally “pure Information”;
- that every physical identity is a sphere in the same state-space sense;
- universal fractality, phi handover or quantum gravity;
- superiority over standard quantum tomography;
- performance on experimental hardware, drift, readout bias or correlated noise.

The four mechanisms are deliberately well separated and generated by the same equations used to referee them.
The native physics model's perfect result confirms that this is an instrument/crosswalk validation. The next
scientific rung is to freeze the account against public or hardware-derived qubit calibration data with realistic
state-preparation, measurement and temporal drift errors.

One implementation detail was not numerically expanded in the frozen prose: its registered “weighted transverse
phase slope” used squared transverse radius as the weight. That choice was made in code before any outcome was
opened and was not changed, but a replication should state it directly in its next frozen protocol. The simulated
binary samples were also independent across axis and time; correlated readout and calibration errors remain
untested.

## Reproduction

From the repository root, using Python with NumPy:

```powershell
python analysis/quantum/q1_open_qubit_multi_axis_test.py
python analysis/quantum/q1_open_qubit_multi_axis_validate.py
```

Primary artifacts:

- frozen protocol: `Q1_OPEN_QUBIT_MULTI_AXIS_PROTOCOL_v1_FROZEN.md`;
- full target rows: `Q1_OPEN_QUBIT_MULTI_AXIS_TRIALS.csv`;
- shot ladder: `Q1_OPEN_QUBIT_MULTI_AXIS_AGGREGATES.csv`;
- representative trajectories: `Q1_OPEN_QUBIT_MULTI_AXIS_TRAJECTORIES.csv`;
- machine-readable outcome: `Q1_OPEN_QUBIT_MULTI_AXIS_RESULTS.json`;
- independent audit: `Q1_OPEN_QUBIT_MULTI_AXIS_VALIDATION.json`.

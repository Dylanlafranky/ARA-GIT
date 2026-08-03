# T323 — Observer–source octave projection

**Date:** 1 August 2026  
**Frozen verdict:** **NOT SUPPORTED — 0/5 gates**  
**Validation:** **PASS — 192/192 independent checks**

## Plain-language outcome

This was finally the intended lighthouse–boat test rather than another nested
child/parent test. A measured acoustic source and receiver supplied the
horizontal transfer relation. The change from frequency `f` to `2f` supplied
the vertical octave relation. Their two-coordinate direction was then compared
with the frozen `36 degree` Phi projection and six alternative angles.

The result did **not** select `36 degrees`. Both measured subjects independently
settled near `52 degrees`, and the preregistered `54-degree` complementary
orientation had the lowest loss. More importantly, restoring the measurement
latency stored separately in the SOFA files moved the result to approximately
`46.5 degrees`, where the ordinary `45-degree` pure-delay prediction dominated.

The honest conclusion is:

> This frequency-octave source–receiver coordinate contains a stable
> propagation relation, but it does not provide evidence that Phi is the
> handover ruler. The apparent complementary orientation depends materially on
> how the archive partitions propagation latency from the stored impulse
> response.

## Frozen coordinate

For each of `1,550` source directions, two receiver ears and exact FFT-bin
octave pair `(k,2k)`, the protocol defined

\[
\Delta_{\parallel}=\psi(f_k),
\qquad
\Delta_{\rm octave}=\psi(f_{2k})-\psi(f_k),
\]

and

\[
\theta
=
\operatorname{atan2}
\left(
|\Delta_{\rm octave}|,
|\Delta_{\parallel}|
\right).
\]

The ARA projection was

\[
x=2\cos\theta.
\]

The declared Phi prediction was

\[
\theta=36^\circ
\quad\Longleftrightarrow\quad
x=\phi.
\]

A pure time delay instead predicts

\[
\psi(2f)=2\psi(f)
\quad\Longrightarrow\quad
\theta=45^\circ.
\]

That gave the analysis a non-Phi physical baseline that could win.

## Primary result

The two public ARI measurements reproduced almost exactly:

| Result | NH2 evaluation | NH4 confirmation |
|---|---:|---:|
| Source directions | 1,550 | 1,550 |
| Receiver paths | 3,100 | 3,100 |
| Eligible octave events | 163,167 | 162,365 |
| Median free path angle | 52.006° | 52.166° |
| Median event ARA `x` | 1.2261 | 1.2147 |
| Closest frozen target | 54° complement | 54° complement |

Median path RMS loss was:

| Frozen target | NH2 | NH4 |
|---|---:|---:|
| 30° | 23.744° | 23.690° |
| **36° Phi** | **18.319°** | **18.181°** |
| 45° pure delay | 11.212° | 11.037° |
| **54° complement** | **9.214°** | **8.982°** |
| 60° | 12.189° | 11.950° |

In NH2, Phi loss exceeded pure-delay loss by `+7.006°`, with a source-cluster
95% interval `[+6.973,+7.045]`. It exceeded complementary-orientation loss by
`+9.061°`, interval `[+8.949,+9.189]`. NH4 returned the same ordering.

Across frequency bins, the 54-degree target was closest for `26/57` NH2 bins
and `27/56` NH4 bins. Phi won only `6` bins in each dataset. The angle varied
with frequency rather than recurring at one constant target.

![T323 observer–source result](F:/SystemFormulaFolder/GIT/ARA-GIT/analysis/phi_observer_source/T323_OBSERVER_SOURCE_OCTAVE_PROJECTION.png)

## What the controls say

The true source–receiver pairing was slightly closer to Phi than the broken
direction pairing:

- NH2 observed-minus-broken: `-0.0871°`, 95% interval
  `[-0.1639,-0.0087]`;
- NH4 observed-minus-broken: `-0.1782°`, interval
  `[-0.2673,-0.0941]`.

That supports a small genuine path-specific relation. It does not isolate Phi.
The phase-scrambled paths were substantially **closer** to 36 degrees than the
observations:

- NH2 observed-minus-scrambled: `+5.985°`;
- NH4 observed-minus-scrambled: `+6.186°`.

The signed data were also overwhelmingly in the `--` quadrant: accumulated
phase and the octave increment were both negative in approximately `97%` of
eligible events. This is a coherent propagation-phase direction, not balanced
occupation of four quadrants in this measurement.

## Why the tempting 54-degree result is not promoted

Because `54 degrees` from the frozen horizontal axis is `36 degrees` from the
vertical axis, it is tempting to swap axes and call the result Phi-like. The
axis-swapped projection would be

\[
x_{\rm swapped}=2\sin\theta,
\]

giving approximately `1.5761` for NH2 and `1.5796` for NH4, about `0.04` below
Phi. The complementary target was preregistered, so its numerical win is real;
however, the primary axis assignment was also preregistered and may not be
reversed after seeing the outcome.

More decisively, the SOFA files store `MeasurementAudioLatency` separately
from `Data.IR`. The frozen primary correctly left this metadata out because no
timing correction was allowed. A declared post-result sensitivity restored
that recorded latency rather than fitting any offset. The median angles became:

| Latency-restored sensitivity | NH2 | NH4 |
|---|---:|---:|
| Median free angle | 46.365° | 46.537° |
| Closest frozen target | 45° pure delay | 45° pure delay |
| 45° target loss | 2.233° | 2.468° |
| 36° target loss | 10.505° | 10.719° |

Therefore the raw `52–54 degree` orientation is not invariant to the archive's
documented representation of travel latency. The physically fuller transfer
is close to the standard frequency-doubling phase relation.

## Gate verdicts

| Gate | Result |
|---|---|
| G1 — Phi uniquely best | Failed |
| G2 — beats 45° pure delay | Failed |
| G3 — free angle closest to Phi | Failed |
| G4 — beats broken and scrambled controls | Failed |
| G5 — Phi recurs across most octave bins | Failed |
| **Overall** | **NOT SUPPORTED (0/5)** |

## ARA interpretation boundary

The test does establish that the observer, source and path can be represented
as three independently measured pieces. It avoids the self-containing
`child -> parent=A+B` construction that forced near-direct alignment in the
bubble test.

It does **not** establish that a frequency octave is the correct vertical ARA
rung for the proposed lighthouse distortion. In this acoustic system, once
the complete recorded travel delay is included, octave phase behaves like an
ordinary delay and approaches the diagonal `45-degree` relation.

A future test of the original geometric-size idea would need two independently
measured identities separated by actual spatial or identity octaves—not merely
two frequencies from one linear transfer function. That is a different object
and must receive a new frozen protocol.

## Source and reproduction

Public files were selected before inspection from the
[SOFA Toolbox test archive](https://sofacoustics.org/data/sofatoolbox_test/).
The [ARI HRTF database](https://www.oeaw.ac.at/en/ari/outreach/software/hrtf-database)
documents the underlying high-resolution directional measurements. The SOFA
files themselves state `No license provided, ask the author for permission`, so
they are checksum-locked and downloaded by the reproducer but not redistributed
in the repository.

```powershell
python -m pip install -r requirements.txt
python t323_observer_source_octave_projection.py --fetch
python validate_t323_observer_source_octave_projection.py
```

Source hashes:

- NH2: `ba90827a8477a574a6267f38d48ea564587223d110aec28a2768698e1821efb0`
- NH4: `855da8e2317dff83866a9a2e74e952d9d404013d186d3a510286c7dfd7525d2a`

The independent validator reconstructed raw phases, eligibility, path losses,
frequency-bin winners, latency sensitivity, broken-path controls and all 64
phase scrambles for audited paths. It passed `192/192` checks.


# Q2 public-hardware I/Q translation-fidelity packet

**Claim ID / version:** `Q2-IQ-FID-v1`  
**Frozen:** 24 July 2026, before opening numerical shot values  
**Status:** `Q1 FIDELITY INHERITED; REAL-DATA ADAPTER EXACT ENOUGH TO TEST`  
**Evidence type:** translation and scope contract only

## Source relation

Q1 established the declared ARA-to-Bloch coordinate bridge for controlled qubit tomography:

> one diameter is a real but incomplete cut; independently measured cuts preserve distinctions that one cut can
> discard.

Q2 does not silently identify readout I/Q with Bloch X/Y/Z. It asks the narrower real-data question:

> do two independently recorded hardware-output quadratures preserve ground/excited separation that either fixed
> raw quadrature alone discards?

## Identity, poles, direction and rung

- **Measured identity:** one single-shot readout record from the same superconducting-qubit experiment.
- **Declared poles:** prepared ground (`g`) and excited (`e`) class centroids within the training conditions.
- **Cuts:** the native in-phase (`I`) and quadrature (`Q`) output channels.
- **Rung:** one readout event at one hardware condition. I and Q are same-event cuts, not different scale rungs.
- **Direction:** each cut is oriented on training data from the ground centroid toward the excited centroid.
- **Parent account:** the coupled I/Q point. Its polar radius and direction are a decompression of the same two
  coordinates, not extra observations.

For cut \(u\in\{I,Q\}\), training-only calibration defines

\[
\boxed{
x_u
=
1+
\operatorname{sgn}(\mu_{e,u}-\mu_{g,u})
\frac{u-m_u}{s_u}
}
\]

with

\[
m_u=\frac{\mu_{g,u}+\mu_{e,u}}2
\]

and \(s_u\) the pooled within-class standard deviation. No clipping is applied in the primary analysis, so the
map remains invertible and noisy observations may extend outside `[0,2]`.

Axis reversal must satisfy

\[
x_{-u}=2-x_u.
\]

The coupled point may be written

\[
\mathbf a=(x_I-1,x_Q-1),\qquad
R=\|\mathbf a\|,\qquad
\theta=\operatorname{atan2}(a_Q,a_I).
\]

## Permitted claim

If the frozen test passes, Q2 may say:

> two coupled ARA-coordinate cuts preserve real readout-class information absent from the selected fixed native
> cut, and the invertible ARA account agrees with a standard same-information I/Q classifier.

## Forbidden claims

Q2 may not say that:

- I and Q are literally the qubit’s Bloch X and Y axes;
- the test reconstructs a quantum state or wavefunction;
- ARA outperforms quantum tomography;
- a classifier advantage proves universal spheres, hidden Phase B, Information³, phi, consciousness or quantum
  gravity;
- the author-supplied `angle`, `threshold`, `Pgg`, `Pee` or `QNDFid` were independently recovered if they were
  used as predictors.

## Wrong-object and flattening risks

The test is invalid if it:

- randomly splits shots from every condition into train and test;
- chooses the better single cut after seeing the target condition;
- uses source-supplied thresholds or fidelities;
- treats polar radius/direction as additional independent measurements;
- describes readout I/Q success as full-state tomography;
- reports raw/ARA agreement as a novel physical law rather than affine coordinate equivalence.

## Three-view translation

### Plain

Each hardware shot leaves two numbers. Looking at only I or only Q is one line view. Looking at the paired I/Q
point keeps both views and shows the point’s direction and distance from the training midpoint.

### Mathematical

The ARA map is a training-derived invertible affine transform of I/Q. A linear discriminant fitted after this
transform must therefore make the same decisions as a raw I/Q linear discriminant, apart from numerical error.
The non-trivial question is whether two cuts generalise better than a single preselected native cut to an unseen
hardware condition.

### Back-translation

The framework does not create information. It gives the two recorded channels a common reversible coordinate
system. If both channels matter, compressing to one will lose some class separation; if one channel already
contains everything, the two-cut improvement gate should fail.

## Fidelity verdict

The adapter preserves the Q1 “one cut versus coupled cuts” claim while narrowing the physical object to a readout
record. This is exact enough for the registered real-data test.

# Potential thread — ARA spherical tomography

**Date captured:** 23 July 2026  
**Status:** `PARKED / MUSING TIER / NOT EVIDENCE`  
**Orientation:** `0–2 is one declared diameter; pole reversal swaps orientation`  
**Ledger status:** none; this thread must receive translation-fidelity approval and a frozen protocol before testing

## Dylan's source idea

> ARA is the condensed triangle lock that gives you the rough idea on a line cut through it. Like seeing an ant
> farm against the glass, you can see where the sphere does and does not pass through. But to see beyond that, we
> need the full sphere.

> I wonder if we could do an ARA for every degree in a sphere to like “properly properly” map it.

## Faithful mathematical translation

Let the complete identity at rung \(k\) and cycle phase \(\tau\) be an ARA sphere \(\mathscr S_k(\tau)\). A declared
direction

\[
\hat{\mathbf u}(\theta,\phi)
=
(\sin\theta\cos\phi,\sin\theta\sin\phi,\cos\theta)
\]

produces one compressed ARA diameter reading

\[
\mathscr A_k(\theta,\phi,\tau)
=
\mathcal P_{\hat{\mathbf u}}
\left[\mathscr S_k(\tau)\right].
\]

The scalar reading is not the complete sphere. It is one projection or line cut. The proposed full field is

\[
\boxed{\mathscr A(\rho,\theta,\phi,\tau)},
\]

where:

- \(\rho\) is radius, depth or fractal rung;
- \((\theta,\phi)\) is the declared direction;
- \(\tau\) is position within the measured cycle;
- \(\mathscr A\in[0,2]\) is the local accumulation–release coordinate.

This is closest to an inverse problem or tomography: reconstructing a whole object from partial projections.

## Triangle-lock interpretation

For one line cut, the minimum declared relational object is

\[
A+B+(A\leftrightarrow B)\longrightarrow\text{local identity}.
\]

The two poles and their ordered coupling relation lock the local ARA reading. They do not uniquely determine the
full sphere. In the ant-farm analogy, tunnels away from the glass may first appear as unresolved `Other`, even
though they are structured parts of the full colony.

## Proposed structural checks

Under a consistent pole convention, the ideal antipodal relation is

\[
\mathscr A(-\hat{\mathbf u},\tau)
\stackrel{?}{=}
2-\mathscr A(\hat{\mathbf u},\tau).
\]

The equality is a test, not an assumption to force onto observations. Stable deviation may encode identity
asymmetry, deformation, unresolved children or outside coupling.

A future instrument should test:

1. whether opposing orientations complement to \(2\);
2. whether the \(1.0\) ridge is recovered as a curve or surface;
3. whether known singularity directions are localized near \(0\) and \(2\);
4. whether held-out angular readings can be reconstructed from measured directions;
5. whether added child couplings appear as localized deformation rather than global relabelling;
6. whether coarse-graining a completed child sphere recovers the independently measured parent sphere;
7. whether independent reconstruction routes converge on the same parent identity.

## Sampling rule

A latitude–longitude grid at one-degree increments oversamples the poles. Prefer an equal-area Fibonacci sphere,
HEALPix grid or subdivided icosahedron. Begin with hundreds of directions and refine only where the recovered field
has ridges, poles or sharp changes.

Opposing orientations define one diameter. They may be stored once with an orientation flag rather than counted as
independent evidence.

## Data requirement

A scalar time series cannot supply thousands of independent directions. Activation requires either:

- a controlled synthetic vector/field system with known truth;
- genuinely spatial or multichannel observations;
- or multiple independently measurable observables tied to declared physical axes.

For ENSO, possible future axes include latitude, longitude, depth, temperature, pressure, wind and current. Copying
one index around a rendered sphere would decorate the model, not reconstruct the system.

## Controls and falsifiers

Required controls:

- conventional spherical-harmonic or tomographic reconstruction with the same observations;
- shuffled angular labels;
- wrong-centre and wrong-axis reconstructions;
- held-out directions and held-out cycle phases;
- multiple fixed denoisers and angular resolutions;
- a non-spherical or anisotropic ground-truth object.

Strong falsifiers for the proposed instrument:

- antipodal error no better than shuffled orientation;
- ridge or pole locations dominated by the rendering grid;
- held-out reconstruction no better than a constant or conventional baseline;
- different valid line-cut routes producing incompatible parent spheres;
- the apparent sphere disappearing under modest predeclared changes in cycle segmentation or noise treatment.

## Evidence fence

This document formalizes a possible measurement programme. It is not evidence that physical identities are literal
spheres, that every system supplies all angular observables, or that ARA improves on established tomography.

The earliest defensible result would be an instrument-validation result on known ground truth. Claims about nature
would require independent real observations after the reconstruction method is frozen.

## Activation checklist

Before this thread leaves `PARKED`:

1. obtain Dylan's translation-fidelity verdict;
2. select the controlled ground-truth family;
3. define sphere centre, boundary, radius/rung and cycle phase;
4. freeze the directional observable and denoising method;
5. register prediction, controls, uncertainty and kill thresholds;
6. hash the protocol before opening target outcomes.

## Relationship to active quantum work

The Bloch sphere provides an established test environment in which every directional two-outcome measurement
already has

\[
x_{\hat n}=1-\mathbf r\cdot\hat n.
\]

It may later serve as the first controlled spherical-tomography calibration. That does not activate this broader
thread and does not turn an exact Bloch-coordinate reparameterization into new quantum physics.

## Prior implementation — ARA coordinate sphere

Dylan identified:

`3D models/ara_sphere_coordinate_3d.html`

as an earlier attempt at the same decompression. Its declared coordinates are:

- `X`: Mapping/ARA from Space `0`, through ridge `1`, to Time `2`;
- `Y`: rungs, with a local `0–2` sub-ARA inside each rung;
- `Z`: coupling ARA from Connections to Information Traversal.

It also declares that every plotted identity is itself a sphere. This correctly anticipates several parts of the
new formulation: multiple ARA axes, nested local coordinates and nodes that remain full identities after being
placed in a parent coordinate system.

The current file is primarily an **atlas/state-space viewer**: it places different named identities at assigned or
approximate `(ARA, rung, coupling)` coordinates. It does not yet rotate a measurement diameter through every
direction of one fixed identity or reconstruct its hidden volume. The future tomography instrument would therefore
extend the same idea inward:

\[
\text{many identities positioned in one atlas}
\quad\longrightarrow\quad
\text{many independent cuts through one identity}.
\]

This is a distinction of measurement grain, not a rejection or replacement of the earlier model.

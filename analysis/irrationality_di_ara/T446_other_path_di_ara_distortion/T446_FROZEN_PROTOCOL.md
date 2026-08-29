# T446 — Other-path Irrationality Di-ARA and distorted A/B continuation

**Frozen:** 28 August 2026, before T446 calculation  
**Parent test:** T445 WGD 2038−4008 Te-ARA / external-shear path

## Question

Does the unresolved outcome-compatible section have independently recoverable straight-versus-curve history, and does its recovered bend improve the continuation of the known A/B coupling path?

## Identity and scale

- Same physical identity and data as T445: WGD 2038−4008.
- TDCOSMO image labels and spatial order around the lens are fixed from astrometry as `A → C → B → D`.
- The foreground lens remains the parent; image paths are child relations.
- No posterior index, coupling coordinate, or image order is called chronological time.

## Per-pair identifiability boundary

For one image pair T445 observes only a fitted endpoint and one later outcome-required endpoint. That is one displacement vector. A one-step path has directness (D=1) by construction and has no turn angle, so an individual-pair line/circle Di-ARA is **not identifiable** from the available data. It will not be reported as evidence of a straight Other.

## Spatial child-ring cut

The available multi-point cut is the ordered field of child relations around the same lens. Use the open order

\[
O,\ AC,\ AB,\ AD,
\]

where (O=(0,0)) is the TDCOSMO-A reference relation. The known points are

\[
P_i=(A_i,B_i),
\]

and the later outcome-compatible points are

\[
Q_i=(A_i,B_{\mathrm{eff},i}),
\qquad
B_{\mathrm{eff},i}=\Delta\phi_{\mathrm{obs},i}-A_i.
\]

This is a spatial child-relation path, not a time history and not one photon trajectory.

## Irrational path Di-ARA geometry

For ordered points (p_0,\ldots,p_3) and steps (v_j=p_{j+1}-p_j), reuse the frozen T345 geometry:

\[
D=\frac{\lVert p_3-p_0\rVert}{\sum_j\lVert v_j\rVert},
\]

\[
G=\frac{|\sum_j\gamma_j|}{\sum_j|\gamma_j|},
\qquad
\gamma_j=\operatorname{Arg}(v_{j+1}/v_j),
\]

\[
C=(1-D)G.
\]

`D` is line directness. `G` distinguishes coherent one-way turning from cancelling crookedness. `C` is conservative historical circularity, not proof of a Euclidean circle.

## Distortion-angle transfer

For each held-out child pair (h), use the origin and the other two pair points in their retained spatial order. Compute the known and outcome turn angles,

\[
\delta_h=\operatorname{wrap}(\gamma_{Q,-h}-\gamma_{P,-h}).
\]

The held-out pair's T445 tangent is oriented toward its Te-ARA outcome using only the sign of the solved residual. Rotate that oriented tangent by (delta_h). The step magnitude is the Te-ARA residual magnitude, which is already known in this reconstruction test.

Compare:

1. straight continuation landing error;
2. distorted continuation landing error;
3. angular error to the actual outcome direction.

Improvement means the independently learned bend helps locate the held-out outcome direction. It does not constitute a delay forecast because Te-ARA supplies the outcome magnitude.

## AC sign sensitivity

Primary displayed solution: published selected AC delay `−5.3 d`.  
Required sensitivity: alternate reported AC solution `+7.9 d` with the same covariance structure shifted in mean.

AB and AD are the clean outcome pairs, but both leave-one-out bend estimates depend on AC as one of only two remaining children. Therefore no clean confirmatory verdict is allowed unless the direction improvement survives both AC solutions.

## Uncertainty and controls

- Reuse the 2,000 correlated T445 local draws per pair, joined by draw index.
- Preserve the same fitted lens, cosmology, identity crosswalk, and local-posterior limitation.
- Control 1: zero-angle straight continuation.
- Control 2: opposite-sign rotation using the same (|\delta_h|).
- Control 3: AC alternate timing solution.
- Native A/B geometry and angles are primary; any 0–2 display is secondary.

## Interpretation boundary

The child-ring result can establish a spatially coherent distortion of the relation field. It cannot establish a chronological Other path, a unique physical force, or time itself. If AC sensitivity reverses the result, the correct conclusion is that public data do not yet resolve the distortion angle.

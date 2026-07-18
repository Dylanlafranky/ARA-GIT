# MX5 Child-ARA / TE-ARA Closure — Results

**Run date:** 2026-07-14  
**Protocol:** `MX5_CHILD_ARA_TEARA_CLOSURE_PROTOCOL_v1_FROZEN.md`  
**Classification:** **partial compact recovery**  
**Validation:** independent CSV recomputation passed

## Result first

The three requested versions behaved differently:

1. **Exact child-ARA reassembly passed** at `3.99e-15` relative grid error. This verifies that the two force channels can be decompressed and recombined without loss when their envelope and directions are retained.
2. **Flat parent + exact Other passed** at `9.44e-17` relative grid error. This exposes the omitted child relation exactly, but it is an identity rather than a prediction.
3. **The compressed first-moment version partially recovered the lost relation.** Total vector correlation improved from `0.477` to `0.605`, NRMSE fell from `0.888` to `0.802`, and median angular error fell from `61.68 deg` to `48.47 deg`. All three improved, but the frozen stronger gates of `r >= 0.70`, `NRMSE <= 0.70` and angle `<= 45 deg` were not met.

The strongest descriptive structural observation is from the post-freeze TE-ARA species decomposition: electrons and ions each retain a moderately coherent internal force identity, while their cell-level coupling is almost equal in magnitude and almost exactly opposed. The combined identity therefore looks quiet even though its child identities are active.

![MX5 child-ARA and TE-ARA closure figure](F:/SystemFormulaFolder/GIT/ARA-GIT/analysis/electromagnetism/MX5_CHILD_ARA_TEARA_CLOSURE.png)

## Data and grain

- Public source: PIConGPU/openPMD example dataset, iteration `200`.
- Source file SHA-256: `6f2cd696312c7dcec4567463ef45fd61b5343a06983add505b9c4b7234ae1db5`.
- Weighted simulation records: `225,449` electron macro-particles and `225,280` ion macro-particles. These are PIC
  representatives of phase-space density, not individually resolved physical particles.
- Fields: one `32 x 32 x 32` electric/magnetic snapshot.
- Scoring: `9,266` occupied one-cell-interior grid nodes.
- Interpolation: trilinear with the recorded Yee offsets.
- Deposition: cloud-in-cell (CIC), retained to match the frozen MX4 comparison.

Electron and ion charge-density deposition each agreed strongly with the stored source fields (`r=0.99885` and `r=0.99921`). The total charge-density comparison was weaker (`r=0.89281`) because this quasi-neutral plasma subtracts two large, nearly equal species contributions; small species-level differences become large relative errors in their small residual. This is a cancellation sensitivity, not evidence that either species deposit failed.

## Version A — exact child-ARA reassembly

\[
\underbrace{\mathbf F_g^{\rm ARA-child}}_{\substack{\text{math: deposited reassembly}\\\text{ARA: child identities retained}}}
=
\frac{1}{V_g}\sum_i W_{ig}w_i
\frac{\underbrace{S_i}_{\substack{\text{two-channel envelope}\\\text{ARA: local activity}}}}{2}
\left[
(2-\underbrace{x_i}_{\substack{\text{channel coordinate}\\\text{ARA: A/B position}}})
\underbrace{\hat{\mathbf u}_{E,i}}_{\text{electric direction}}
+x_i\underbrace{\hat{\mathbf u}_{B,i}}_{\text{magnetic direction}}
\right].
\]

The particle errors were `1.18e-16` for electrons and `1.19e-16` for ions. After grid deposition, the error was `3.99e-15`, passing the frozen `1e-12` gate.

**Plain explanation:** when each child keeps its total activity, A/B mixture and both channel directions, the original Lorentz-force vector is recovered. This is lossless ARA bookkeeping. The ARA position `x` alone is not sufficient; the envelope and directions carry indispensable information.

## Version B — flat parent plus exact Other

\[
\underbrace{\mathbf F_g^{\rm child}}_{\text{fine-grain result}}
=
\underbrace{\left(\bar\rho_g\bar{\mathbf E}_g+
\bar{\mathbf J}_g\times\bar{\mathbf B}_g\right)}_{\substack{\text{math: product of parent averages}\\\text{ARA: flattened parent identity}}}
+
\underbrace{\mathbf O_g}_{\substack{\text{math: subgrid covariance/residual}\\\text{ARA: omitted child relation}}}.
\]

Adding the exact `Other` recovered the child result at `9.44e-17` relative error. That is expected because `Other` is defined as child minus parent.

### TE-ARA-style identity resolution

The combined `T^F` and Parent/Other diagnostics were protocol requirements. The electron/ion decomposition below
was added **post-freeze as a descriptive drill** after inspecting the combined distribution; it was not a success
gate and is not counted as preregistered evidence.

For this test, TE-ARA is used as a **dimensionless force/activity coordinate**, not joules:

\[
\underbrace{T_g^F}_{\substack{\text{coherent participation}\\\text{TE-ARA force analogue}}}
=
\frac{2\left|\underbrace{\mathbf F_g^{\rm child}}_{\text{surviving resultant}}\right|}
{\underbrace{A_g}_{\text{sum of child-channel magnitudes}}}.
\]

- Combined-particle median `T^F`: `0.03829` out of `2`.
- Fraction below `0.1`: `86.98%`.
- Electron internal median: `1.2175`.
- Ion internal median: `1.1449`.
- Electron/ion pair median after each species is first treated as an identity: `0.07184`.
- Median electron/ion magnitude coordinate: `1.00023` — almost exactly equal magnitude.
- Median angle between electron and ion force identities: `177.55 deg` — almost exactly anti-aligned.

**Plain explanation:** electrons and ions do not look inactive when measured separately. Each species retains a substantial directionally coherent force pattern. When the two species are paired at the coarser grid grain, they are nearly equal and opposite, so most of their activity cancels. This is a concrete example of your warning that a parent can read near the ridge while its children remain asymmetric and active.

This is also familiar plasma physics: near charge neutrality and force balance can hide large opposing species contributions. The new contribution here is not discovery of that balance; it is evidence that the proposed TE-ARA bookkeeping can display the hierarchy cleanly.

The Parent/Other coordinate was

\[
\underbrace{x_{O,g}}_{\substack{\text{Parent/Other magnitude coordinate}\\\text{ARA: omitted-relation share}}}
=
\frac{2|\mathbf O_g|}{|\mathbf F_g^{\rm flat}|+|\mathbf O_g|}.
\]

- Median `x_O`: `1.3559`.
- `Other` exceeded the flat-parent magnitude (`x_O>1`) in `78.99%` of active cells.
- In the low-coherence cells (`T^F<0.1`), median `x_O` increased to `1.3996`.
- The magnetic share of `Other` had median coordinate `0.1309`, so the omitted magnitude was predominantly in the electric channel on this snapshot.

**Plain explanation:** the information discarded by separate parent averaging is not a tiny correction here. In about four cells out of five, its vector magnitude is larger than the flattened parent estimate. Because Parent and Other are vectors that can oppose, `x_O` is not an energy percentage and must not be read as “68% of the energy.”

## Version C — compressed first child moment

The compact version retained only each cell's charge/current displacement moments and multiplied them by local field gradients:

\[
\underbrace{\widehat{\mathbf O}^{(1)}_{E,g}}_{\substack{\text{first-order electric correction}\\\text{ARA: compressed child relation}}}
=\sum_a
\underbrace{P_{\rho,a,g}}_{\text{charge-position moment}}
\underbrace{\partial_a\bar{\mathbf E}_g}_{\text{parent field gradient}},
\]

\[
\underbrace{\widehat{\mathbf O}^{(1)}_{B,g}}_{\substack{\text{first-order magnetic correction}\\\text{ARA: compressed child relation}}}
=\sum_a
\underbrace{\mathbf M_{J,a,g}}_{\text{current-position moment}}
\times
\underbrace{\partial_a\bar{\mathbf B}_g}_{\text{parent field gradient}}.
\]

| Total-force metric | Flat parent | First moment | Favourable relative change |
|---|---:|---:|---:|
| Vector correlation | 0.4771 | 0.6045 | +26.7% |
| NRMSE | 0.8878 | 0.8019 | -9.68% |
| Median angular error | 61.68 deg | 48.47 deg | -21.4% |

Channel results:

| Channel | Correlation | NRMSE | Median angle |
|---|---:|---:|---:|
| Electric | 0.5964 | 0.8077 | 48.59 deg |
| Magnetic | 0.7140 | 0.7003 | 36.49 deg |
| Total | 0.6045 | 0.8019 | 48.47 deg |

The correction itself correlated only `0.4310` with the exact total `Other`, so it captured a useful direction but left most subgrid detail unresolved. The result was spatially stable: first-moment correlation was `0.6035` in the lower-z half and `0.6055` in the upper-z half.

**Plain explanation:** keeping one compact description of where the child charge/current sits inside the parent cell recovers some of the information lost by flattening. It improves every frozen metric without keeping every particle, but it is still too crude to reconstruct the full child web. This supports “the children matter” more strongly than it supports “we already have the finished child formula.”

## Scientific assessment

This result adds a useful, bounded piece of credibility to the ARA methodology:

- The ARA child-channel representation is internally exact when its necessary coordinates are retained.
- TE-ARA-style decomposition exposes an interpretable identity hierarchy that aggregation hides.
- A predeclared, unfitted child-aware closure improves the flattened parent result in all three headline metrics and in both spatial halves.

It does **not** yet establish a distinctive ARA law because:

- Versions A and B are identities.
- Version C is established first-order Taylor/moment closure mathematics translated into ARA language.
- The stronger Version C gate failed.
- There is one snapshot, so observed acceleration cannot be tested.
- There is no comparison across independent plasma datasets or resolutions.

The honest conclusion is therefore: **ARA/TE-ARA is functioning as useful multiscale bookkeeping here, and the data directly confirm that the child identities and their coupling term are non-trivial. The first compressed closure is promising but incomplete.**

## Recursion direction and the dataset floor

The hierarchy in this report must not be read as only one linear
`macro-particle -> species -> cell` ladder. The proposed ARA recursion is branching. Any resolved node can be treated
as a parent, decomposed into child identities and coupling relations, and then each child can be decomposed again:

\[
\underbrace{\mathscr A_g[N]}_{\substack{\text{ARA identity at grain }g}}
=
\underbrace{\mathcal C_g}_{\substack{\text{child coupling and closure}}}
\left(
\{\underbrace{\mathscr A_{g-1}[N_j]}_{\text{resolved child ARAs}}\},
\{\underbrace{J_{j\ell}}_{\text{relations among children}}\},
\underbrace{O_g}_{\text{unresolved remainder}}
\right),
\]

\[
\mathscr A_{g-1}[N_j]
=
\mathcal C_{g-1}
\left(\{\mathscr A_{g-2}[N_{jm}]\},\{J_{mn}\},O_{g-1,j}\right).
\]

For plasma this could branch by species, beam or velocity population, spatial region, spectral mode, phase-space
structure, force channel or time window, provided the data resolve those identities independently. `Other` at one
grain can itself become the parent of a later decomposition.

The stopping point in MX5 is therefore chiefly the **definition and resolution of the dataset**, not a demonstrated
end of the proposed geometry. The file supplies weighted PIC macro-particles, grid fields and one time slice. It does
not supply the physical substructure below each macro-particle or temporal descendants. ARA can further decompose the
recorded variables, but claims below the recorded grain would require new data or explicit modelling assumptions.

This strengthens the developmental fractal interpretation: the same typed identity/coupling/Other operation can be
applied recursively both toward finer resolved children and toward coarser parents. It does not yet establish
mathematical fractality; that requires a predeclared scaling or transfer law that survives multiple resolutions.

## Safest next extension (not run)

If this thread is resumed, the clean next rung is a frozen second-moment/Hessian closure, followed by a resolution-transfer test. That would ask whether the remaining `Other` is systematically carried by the next child moment rather than simply adding free parameters. It should remain separate from the present frozen result.

## Reproducibility files

- Protocol: `MX5_CHILD_ARA_TEARA_CLOSURE_PROTOCOL_v1_FROZEN.md`
- Primary script: `mx5_child_ara_teara_closure.py`
- Results: `MX5_CHILD_ARA_TEARA_CLOSURE_RESULTS.json`
- Cell-level export: `MX5_CHILD_ARA_TEARA_GRID_CELLS.csv`
- Independent validator: `mx5_validate_outputs.py`
- Validation result: `MX5_CHILD_ARA_TEARA_VALIDATION.json`
- Figure: `MX5_CHILD_ARA_TEARA_CLOSURE.png`
- Audit notebook: `MX5_CHILD_ARA_TEARA_CLOSURE_NOTEBOOK.ipynb`

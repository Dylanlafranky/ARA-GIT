# T445 findings — lens Te-ARA, line/circle Di-ARA, and coarse Other

## Result first

The proposed three-stage procedure works as a **diagnostic grammar**, but this cut does not yet recover a unique physical Other.

1. A delay-blind reconstruction locks the four WGD 2038−4008 image paths to one source at **2.512 mas RMS**.
2. It reproduces the previously published blind model delays: AB **−4.785 d** versus −5.0 d, AC **−10.059 d** versus −10.0 d, and AD **−24.935 d** versus −24.2 d.
3. Scaling the named external shear from absent to fitted produces an essentially perfectly **straight** A/B path. At this scale the circle/line Di-ARA therefore lands on its line pole.
4. The later clean AB and AD outcomes both fall beyond the fitted path, but at incompatible path distances: **λ=11.474** and **λ=2.542** when the fitted shear endpoint is λ=1.
5. Conditional on holding the delay-blind geometric A term fixed, the remaining displacement is mostly aligned with the known line: **83.88%** for AB and **78.93%** for AD. The smaller normal shares are **16.12%** and **21.07%**.

This is evidence that the known one-coordinate coupling gives the general direction but is not a complete relation. It is not evidence that the normal remainder is a new force, time itself, or one uniquely identified ARA identity.

## Exact relational anchor

- **Who:** one quadruply imaged quasar, WGD 2038−4008.
- **Where:** four observed child light paths through one foreground-lens parent to one observer.
- **What:** geometric/traversal Fermat contribution (A), potential/connection contribution (B), and the effective outcome-required (B_{m eff}).
- **When:** the lens geometry was modelled before the time delay was measured. Controlled shear (lambda) is coupling amplitude, not time.
- **Why:** test whether Te-ARA can solve one phase and whether the known pair path plus a circle/line split exposes the direction and amount of an unresolved relation.
- **How:** freeze the delay-blind lens, vary external shear from (lambda=0) to 1, solve (B_{m eff}=Deltaphi_{m obs}-A), then project the conditional residual onto the path tangent and normal.

## Native-unit decomposition

| Pair | Status | (A) (arcsec²) | fitted (B) (arcsec²) | (B_{\rm eff}) (arcsec²) | model delay (d) | observed delay (d) |
|---|---|---:|---:|---:|---:|---:|
| AB | clean blind outcome | 0.009775 | −0.130376 | −0.322282 | −4.785 | −12.4 ± 3.77 |
| AC | model-informed sign | 0.349864 | −0.603367 | −0.483435 | −10.059 | −5.3 ± 2.74 |
| AD | clean blind outcome | 0.267055 | −0.895459 | −1.106286 | −24.935 | −33.3 ± 6.32 |

AC remains visible as a diagnostic, but the later paper rejected its alternate positive-delay solution partly because of mass-model ordering. It is therefore not used as a primary blind result.

## Known path versus unresolved remainder

The shear path is a one-dimensional line because only one explicitly linear coupling amplitude is varied. Matching the later total delay by extending that line requires:

| Pair | required (lambda) | inside fitted ([0,1])? | along-line share | normal share | conditional Other ARA |
|---|---:|---|---:|---:|---|
| AB | 11.474 | no | 83.88% | 16.12% | (movement 1.678, curvature 0.322) |
| AC | −0.095 | no | 86.86% | 13.14% | (movement 1.737, curvature 0.263) |
| AD | 2.542 | no | 78.93% | 21.07% | (movement 1.579, curvature 0.421) |

The clean pairs point past the fitted endpoint but do not agree on how far. A single shared shear scale fitted to AB and AD gives (lambda=1.509) with (chi^2=3.851) for one remaining degree of freedom, (p=0.0497), using observational covariance only. This is a boundary-level incompatibility signal, not a robust discovery: the missing full lens posterior would add model uncertainty.

The fitted endpoint itself differs from the two clean observed delays by (chi^2=4.091) for two degrees of freedom, (p=0.129). The data therefore do **not** force rejection of the published model.

## ARA interpretation

The result is faithful to the proposed sequence:

1. **Te-ARA:** the independently reconstructed (A) and later total triangulate (B_{m eff}).
2. **Circle/line Di-ARA:** the named external-shear coupling is line-like at this cut; no native curvature appears when only its amplitude is changed.
3. **Coarse Other ARA:** the clean residuals are movement/line-heavy with a smaller connection/curvature remainder.

There is one crucial qualification. Because Te-ARA holds (A) fixed, the outcome-required residual is vertical in the native A/B plane by construction. Its tangent/normal shares are therefore a **conditional decomposition of the solved phase**, not an independently observed two-dimensional Other. The new information is that both clean outcomes lie beyond the known path and cannot share one path distance.

## Data quality and limitations

- Independent validation passed **17/17** checks.
- The four back-projected source positions pass the frozen 20 mas lock ceiling by almost an order of magnitude.
- Gaia/TDCOSMO component identities were explicitly crosswalked as TDCOSMO A/B/C/D = Gaia C/B/A/D using pre-delay Fermat ordering, not the later delay values.
- The repository’s linked full-posterior Google Drive folder returned 404 on the test date. The 2,000 local draws per pair use a covariance approximation around published marginal summaries.
- (H_0=70\;\mathrm{km\,s^{-1}\,Mpc^{-1}}) and (Omega_m=0.3) are fixed external conversion choices.
- Missing mass-profile freedom, external convergence, cosmology, microlensing/time-delay systematics, and posterior-reconstruction error all remain possible contributors to the residual.
- This is a completed-handover reconstruction. Neither posterior draws nor (lambda) are chronological time ticks.

## Strongest next test

Keep the same lens and add one second independently constrained coupling coordinate—preferably external convergence/mass-sheet freedom or mass-profile slope. Freeze the resulting two-dimensional known-coupling surface before applying the later delay. A residual normal to that **surface**, rather than to a one-parameter line, would be a materially stronger Information³ lock on an unresolved Other.

## T446 correction to the path interpretation

T445's tangent/normal residual shares do **not** constitute the original path Irrationality Di-ARA on the Other section. They measure the amount aligned with and normal to one known tangent. T446 therefore keeps this decomposition as a coarse conditional result, but separately applies the T345 path instrument—directness `D`, turn consistency `G`, and conservative historical circularity `C`—to the available ordered spatial child-relation path before transferring its bend back onto the known A/B continuation. Future sessions should use T446, not the T445 tangent/normal split, for claims about straight-versus-curved Other history.

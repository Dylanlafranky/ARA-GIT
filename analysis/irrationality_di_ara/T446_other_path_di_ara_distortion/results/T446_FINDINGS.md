# T446 findings — Other-path Irrationality Di-ARA and distortion transfer

**Frozen all-clean-pair result:** `transferred_bend_not_consistently_helpful`

**Geometry-first terminal-continuation result:** `terminal_continuation_improves_only_for_selected_AC; AC_sign_sensitive`

## What was actually measured

The original T345 path instrument (D directness, G one-way turn consistency, C conservative historical circularity) was applied to the spatial child-relation order `O → AC → AB → AD`. This is the available multi-point Other path in WGD 2038−4008. It is a spatial relation-field reconstruction, not chronological time and not one photon trajectory.

An individual pair still supplies only one Other displacement. Its D=1 value is definitional and has no identifiable turn, so it is not evidence that the individual Other is straight.

## Path geometry

- `selected_AC_-5.3d`: known median D/G/C = 0.447 / 0.034 / 0.019; Other median D/G/C = 0.631 / 0.062 / 0.022.
- `alternate_AC_+7.9d`: known median D/G/C = 0.447 / 0.034 / 0.019; Other median D/G/C = 0.715 / 0.227 / 0.064.

## Held-out distortion transfer

- `selected_AC_-5.3d`, held-out AB (internal-child interpolation): δ median 2.2°; distorted/straight landing-error ratio 1.202; improved in 32.3% of 2,000 draws; median angular error 10.9° → 12.9°.
- `selected_AC_-5.3d`, held-out AD (terminal forward continuation): δ median 22.9°; distorted/straight landing-error ratio 0.593; improved in 73.2% of 2,000 draws; median angular error 15.0° → 8.8°.
- `alternate_AC_+7.9d`, held-out AB (internal-child interpolation): δ median -25.5°; distorted/straight landing-error ratio 1.350; improved in 33.1% of 2,000 draws; median angular error 10.9° → 14.6°.
- `alternate_AC_+7.9d`, held-out AD (terminal forward continuation): δ median 43.7°; distorted/straight landing-error ratio 1.901; improved in 16.8% of 2,000 draws; median angular error 15.0° → 28.7°.

## Boundary on the claim

The held-out child’s bend is learned from the other two children, but Te-ARA supplies the held-out residual magnitude and its forward/backward half-plane. Therefore this is a curvature-direction reconstruction test, not a blind delay or event forecast.

AB and AD both depend on AC in this three-child leave-one-out geometry. The selected −5.3 d and alternate +7.9 d AC solutions are therefore displayed as separate required sensitivity cases; the verdict above refuses a robust conclusion if that choice reverses the direction result.

A topology audit after calculation distinguishes the two clean holdouts: AD is the only true forward continuation of `O → AC → AB`; AB is an internal interpolation because removing it joins non-adjacent AC directly to AD. The frozen all-clean-pair verdict is retained, while the terminal AD result is reported separately rather than silently treating those geometries as equivalent.

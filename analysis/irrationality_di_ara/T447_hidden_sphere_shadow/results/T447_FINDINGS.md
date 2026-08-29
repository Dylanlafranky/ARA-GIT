# T447 findings — recovering a hidden larger geometry from its shadow

## Plain-language result

The test worked for the part it was able to observe. Three genuinely independent visible coordinates recovered the deliberately hidden fourth coordinate across the untouched later 30% of a real motion-capture trajectory; two coordinates could not, and adding `x−y` to those same two coordinates added no information.

The important limit is equally clear: the primary hidden coordinate `w` never reached its zero ridge in this flight. We recovered **how far the identity was from that hidden ridge**, but this dataset cannot test the actual switch between the `+w` and `−w` mirror branches.

## Exact relational address

- **Identity:** one EuRoC `MH_01_easy` micro-aerial vehicle.
- **Medium:** movement-heavy rigid-body orientation, not the gravitational/lensing medium used in T444–T446.
- **Parent geometry:** the complete orientation quaternion `(w,x,y,z)`, which is a known unit `S³` identity.
- **Visible shadow:** `(x,y,z)`, a three-dimensional `B³` projection.
- **Ordinary ARA cuts:** two-coordinate views such as `(x,y)`, `(x,z)`, and `(y,z)`.
- **Hidden coordinate:** `w`; its ARA display ridge is `w_ARA=1+w=1`.
- **Time role in this test:** recorded order is needed to follow a branch, but no `w` branch crossing occurred here.

## What the numbers say

Across 10,915 untouched holdout samples:

- Three independent normalized cuts `(x,y,z)` recovered `|w|` with MAE `1.29×10⁻¹⁶`, effectively floating-point precision.
- On the quaternion values exactly as recorded, without row renormalization, the same recovery had MAE `1.75×10⁻⁶` and correlation `0.999999992`.
- The deliberately weak two-cut equal-split estimate had MAE `0.1443` and correlation `0.212`.
- The raw three-cut result was about `82,501×` more accurate than that two-cut estimate.
- Shuffling the correct `z` values out of event order produced median MAE `0.02859`; the raw event-linked result was about `16,349×` more accurate.
- The design rank was `2` for `(x,y)`, still `2` for `(x,y,x−y)`, and `3` for `(x,y,z)`.

The normalized near-perfect result is not a discovery claim: it is the known unit-sphere identity working as an instrument calibration. The non-normalized sensitivity shows the same geometry survives the source's actual rounding and measurement precision.

## The visible edge and branch result

For the primary `w` view, the visible shadow reached a maximum radius of `0.985553`, leaving a minimum radial gap of `0.014447` from the outer projection boundary. The smallest observed `|w|` was `0.169368`, and `w` changed sign zero times.

That means this trajectory stayed on one cap of the larger orientation sphere in the primary view. Static geometry supplies the two candidates `+|w|` and `−|w|`, but the recorded path never reached the boundary where those branches meet, so the frozen chronological branch test is correctly marked **not identifiable**.

The descriptive all-axis scan is useful for choosing a follow-up without changing this verdict: hiding `x` exposed 4 sign crossings, and hiding `z` exposed 15. Those are real boundary encounters of the same physical trajectory, but they are exploratory because `w` was frozen as the primary hidden coordinate before calculation.

## WHERE this fits into ARA

This result supports a specific refinement of the current framework map:

1. A normal two-axis ARA cut is a flat view through an identity.
2. A genuinely independent third cut expands that flat view into a three-dimensional shadow.
3. The remaining coordinate is not another algebraic restatement of the first two; it is depth relative to the larger parent identity.
4. The outer edge of the visible shadow is the ridge of the hidden coordinate.
5. Chronological history is required to choose between mirror depths, but only when the path actually encounters that hidden ridge.

So the test does **not** show that time is simply `w`. It shows the measurement architecture the time-facing hypothesis requires: independent cuts recover hidden depth, while history becomes necessary for hidden branch selection.

## Phi / up-right result

The old 36°/Phi direction was drawn as a reference on the two-axis view. It was not used to orient, fit, or score the data. Quaternion component axes do not carry the same meanings as the archived Mapping/Rung axes, so any apparent agreement or disagreement would be coordinate-dependent and is not evidence for or against a universal Phi direction.

## Validation and next cut

Independent validation passed `27/27` checks, including source hash, row grain, time order, manual reconstruction, matrix rank, shuffled controls, raw-data sensitivity, axis crossings, output files, and visual generation.

The clean next test is now obvious: freeze the same method on the same physical trajectory but hide `z`, whose 15 boundary encounters give a real chance to test whether chronological history selects the correct mirror branch. That is a follow-up branch test, not a rewrite of T447's primary `w` result.

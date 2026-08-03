# T329 frozen protocol — actual bubble-handover Phi seam

**Frozen:** 2 August 2026, after event-count feasibility only and before any
T329 angular coordinate, target loss, control loss or outcome was calculated  
**Source:** Pandey et al., Zenodo `10.5281/zenodo.15102957`  
**Parent detector:** `FROZEN_LINEAGE_DETECTOR_2026-08-01.md`  
**Status at freeze:** prospective new-coordinate test within a previously used
archive; not a pristine external replication

## Question

T328 applied the Phi circle-train operator to every frame-to-frame bubble
heading and found persistence. T329 asks the narrower question implied by the
axiomatic geometry:

> At an independently detected two-child-to-one-parent merger, does the
> preserved bubble lineage undergo a directed same-phase handover of
> `2/phi` on the ARA `0..2` circle?

This tests actual merger seams, not ordinary movement frames and not area
ratios.

## Frozen event population

Use only events already accepted by the **primary** frozen lineage detector.
No event is added, removed or reweighted using Phi or an angular outcome.

An event at frame `f -> f+1` is eligible when:

1. exactly one detected child ID equals the detected parent ID;
2. that ID exists at frames `f-1`, `f`, `f+1` and `f+2`;
3. its pre-seam and post-seam centroid displacements are each at least
   `0.0005 m`;
4. the joining child's centroid is distinct from the inherited child's
   centroid, so the contact side is defined.

The inherited child is `I`, the other child is `J`, and the post-merger parent
with the inherited released ID is `P`.

Feasibility before scoring found:

- calibration `V01-V07`: `23` eligible seams;
- evaluation `V08-V28`: `52` eligible seams;
- holdout `V29-V35`: `16` eligible seams.

The holdout is below the earlier 20-event strict-replication boundary. It is
therefore directional confirmation only.

## Raw vectors and ARA coordinates

Use released centroids without smoothing, interpolation, Fourier processing,
trajectory fitting or eventwise sign selection:

\[
\mathbf v_- = I_f-I_{f-1},
\qquad
\mathbf c = J_f-I_f,
\qquad
\mathbf v_+ = P_{f+2}-P_{f+1}.
\]

Let their polar angles be `theta_-`, `theta_c` and `theta_+`.

The physical contact side, declared without reference to the outcome, is

\[
s=\operatorname{sign}\!\left[
\sin(\theta_c-\theta_-)
\right].
\]

Events with `s=0` at numerical precision are excluded before target scoring.
Reflect left- and right-side mergers into one declared contact orientation:

\[
\boxed{
x_{AA}
=
\left[
\frac{s(\theta_+-\theta_-)}{\pi}
\right]\bmod2
}.
\]

This is the primary same-phase `A_before -> A_after` handover coordinate.
The reflection is fixed by the joining child's observed side; it is never
chosen by asking which orientation is closer to Phi.

For an Information³ audit, also retain

\[
x_{AB}=\left[\frac{s(\theta_c-\theta_-)}{\pi}\right]\bmod2,
\qquad
x_{BA}=\left[\frac{s(\theta_+-\theta_c)}{\pi}\right]\bmod2.
\]

Numerically,

\[
x_{AA}=(x_{AB}+x_{BA})\bmod2.
\]

This identity is a bookkeeping check, not a Phi result.

## Frozen Phi prediction and competitors

The exact directed prediction is

\[
\delta_\phi=\frac{2}{\phi}=1.236067977\ldots.
\]

Every candidate is scored by the same circular distance on period `2`:

\[
d_2(x,\delta)=\min(|x-\delta|,2-|x-\delta|).
\]

Frozen candidates, using the same positive orientation, are:

| Candidate | Increment |
|---|---:|
| persistence | `0` |
| ridge | `1` |
| silver conjugate control | `2-2(sqrt(2)-1)` |
| two-fifths control | `6/5` |
| exact Phi | `2/phi` |
| Fibonacci rational control | `26/21` |
| eighth-grid control | `5/4` |
| `1/e` control | `2-2/e` |
| one-third control | `4/3` |

The primary placement score is mean event distance, with median distance
reported as robustness. Candidate comparisons use paired event losses and
whole-video cluster bootstrap intervals.

## Frozen controls

1. **Broken handover lineage:** within each video, pair each event's inherited
   pre-vector and contact-side sign with the post-vector from the next eligible
   event, cyclically. This preserves video conditions and marginal vectors but
   breaks the actual seam.
2. **Pre-event continuation:** when frames `f-2`, `f-1`, `f` are resolved,
   compare the merger-seam turn with the inherited ID's immediately preceding
   ordinary turn. This tests whether the event coordinate is merely local
   persistence.
3. **Contact-side scramble:** within each video, cyclically shift the contact
   signs while retaining the real pre/post vectors. This tests whether the
   independently observed joining side supplies meaningful handedness.
4. **Mirrored chart audit:** score `2-x_AA` separately. It cannot replace the
   contact-oriented primary coordinate.

Use `5,000` whole-video bootstrap resamples. Controls are paired within the
same source video wherever their construction permits.

## Registered gates

### Gate 1 — exact directed placement

Exact Phi must have lower mean loss than every fixed competitor in evaluation,
with each Phi-minus-competitor 95% whole-video interval below zero. Holdout
must retain Phi as the numerical winner, but cannot supply strict replication
because it contains only 16 eligible seams.

### Gate 2 — order/lineage specificity

Real-seam Phi loss must be lower than broken-lineage and contact-side-scramble
Phi loss in evaluation, with 95% whole-video intervals below zero. The same
differences must remain negative in holdout.

### Gate 3 — event specificity

The actual seam must be closer to Phi than the immediately preceding ordinary
turn in evaluation, with a 95% whole-video interval below zero, and retain the
same sign in holdout.

### Gate 4 — exact-constant resolution

The event-coordinate measurement grain must distinguish exact Phi from the
nearest frozen rational control. If it cannot, a Phi ranking is reported only
as an unresolved neighbourhood result.

## Multi-handover boundary

Before scoring, only three primary events had a detected parent ID that later
participated in another primary merger. The archive is therefore insufficient
for the defining multi-handover Fibonacci near-return test. T329 tests one
actual handover step only. It may not be described as confirmation of the full
Phi circle train even if every one-step gate passes.

## Interpretation

- Passing all evaluable gates supports `2/phi` as a one-step, contact-oriented
  same-lineage merger seam in this observable.
- Persistence or another fixed winner rejects this placement.
- Failure of the controls rejects a lineage-specific interpretation even if
  Phi happens to rank first.
- This test does not revisit the already unsupported child/parent area-ratio
  placement and does not infer a multi-step circle train from one-step events.


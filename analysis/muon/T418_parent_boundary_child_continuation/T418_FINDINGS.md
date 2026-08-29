# T418 — Parent-boundary child continuation

## Frozen question

Does the exact curved `I_parent = 2` boundary in the T417 coupled Rationality/Irrationality Di-ARA retain an ordered continuation that can be opened as a child ARA, and does that child independently predict the later population State Di-ARA?

## Identity and cut

- Identity: the same population spin identity used in T416–T417.
- Medium: 300 K silver target RF-µSR ensemble data.
- Validation regime: 68–500 G.
- Hard-transfer holdout: 1800–2484 G; this is substantially stronger magnetic-field coupling, not a matched-field replication.
- RF-on and RF-off remain separate identities.
- All predictors use only past and present samples; the target is four T416 reads, or 16 native bins (about 0.256 µs), later.

## Geometry

T417 used

\[
I_{parent}=2\min(1,q),\qquad q=\frac{L_{local}}{L_{null}}.
\]

This clips every `q >= 1` to the same parent pole. T418 opens the hidden ratio as

\[
x_{child}=\frac{2q}{1+q},\qquad
x_{child}^{anti}=2-x_{child}.
\]

At `q=1`, the parent pole is the child ridge: `I_parent=2` and `x_child=1`. Values `q>1` continue into the child 1–2 half.

The T417 coupled plane has exact inverse coordinates

\[
I=AB,\qquad R=A(2-B).
\]

Therefore its upper curved shoreline is exactly

\[
AB=2\quad\Longleftrightarrow\quad B=\frac{2}{A}.
\]

The curved edge is mathematically meaningful. It marks the parent coordinate boundary; it is not evidence that the underlying measured ratio becomes empty or constant there.

## Result

### Descriptive continuation

- Validation post-boundary child median: `1.06799`; 10th–90th percentiles `1.01376–1.15749`; maximum `1.30828`.
- High-field holdout median: `1.06333`; 10th–90th percentiles `1.01361–1.14633`; maximum `1.38469`.
- No denominator collapse: minimum null-history loss was `0.38278` in validation and `0.46361` in holdout.
- Availability passed: `26/26` validation sequences and `39/40` holdout sequences had at least four post-boundary prediction origins.

The parent ceiling therefore hides finite, stable measured variation. The exact child transform preserves this information on a new 0–2 coordinate.

### Predictive identity

The baseline used the parent ARA, closure `R`, and current State `(xL,xC)`. The child model added `x_child` and its causal first difference.

- Validation aggregate MSE: baseline `0.0667489`, child `0.0661746` — a small `0.86%` improvement.
- High-field holdout aggregate MSE: baseline `0.1863666`, child `0.1868775` — a `0.27%` worsening.
- Correct timing beat circular shifts in validation (`p=0.04096`) but not holdout (`p=0.76424`).
- The child did not pass the frozen frequency, direction, added-information and RF-robustness gates as a complete set.
- Both locked stages have verdict `not supported` for the predictive identity claim.

## Interpretation boundary

T418 supports the narrow statement that the T417 shoreline contains recoverable measured relational variation beneath the clipped parent coordinate. It does not support calling that opened coordinate the adjacent State sphere, a new physical muon constituent, an individual-muon handover, or a neutrino signal. The selected downstream consequence—later population State `(xL,xC)`—was not predicted robustly.

The scientifically useful outcome is therefore:

1. the boundary is real geometry and should not be discarded;
2. the child opening is exact and numerically stable;
3. the chosen next identity was probably wrong, incomplete, or field-regime dependent.

## Recommended next test

Freeze the opened child's own Di-ARA rather than asking it to predict the separate State branch. Couple `x_child` and `2-x_child`, define its amount/balance coordinates, and predeclare a prediction of later child reclosure, pole approach, or lower-rung history transition. Test this first in an independent ordinary-field archive, then repeat the same frozen transform at high field.

## Audit

All independent checks passed for development, validation and holdout: protocol/code hashes, exact child and anti-child formulas, parent cap, A/B inversion, saved errors, result summaries, past-before-future chronology, RF separation, and denominator safety.


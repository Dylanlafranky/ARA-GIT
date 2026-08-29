# T406 — grandchild quarter-completion protocol

**Frozen:** 18 August 2026, before the calculations below were executed  
**Status:** registered diagnostic test  
**Parent reference:** `0.5` on the corrected T404/T405 child coordinate  
**Proposed projected grandchild capacity:** `0.25` at the parent scale  
**Pure proposed endpoint:** `0.5 + 0.25 = 0.75`

## Question

Is the corrected release crest near `0.706306` consistent with a completed
child-of-child contribution whose pure parent-scale endpoint is `0.75`, but
whose observed child coordinate is displaced by participation in the prompt
and delayed branches?

This protocol does not assume that every individual child must land exactly at
`0.75`. It separates the fixed parent reference from the observed child
position.

## Who / what / when / where / why / how

- **Who:** the primary T400 population fit and all 20 valid deterministic T400
  calibration splits, using the T405 participation measures.
- **What:** the interval from the parent reference `0.5` to the proposed pure
  grandchild completion `0.75`, decompressed into its own local coordinate.
- **When:** the delayed-child release interval identified in T400 and corrected
  in T404.
- **Where:** first on the parent-projected child coordinate, then on the local
  grandchild coordinate defined below.
- **Why:** test whether the observed `0.706306` is a fixed quarter-rung
  completion, a participation-displaced version of it, or merely compatible
  with it without identifying it.
- **How:** calculate the raw completion fraction, test replication across
  deterministic splits, and evaluate leave-one-split-out prediction of the
  observed displacement from prompt participation. The prediction test may
  explain displacement but may not manufacture a `0.75` endpoint.

## Frozen coordinates

Let `x` be the corrected child release crest on the parent-projected ARA line.
Define

\[
c_{1/4}=\frac{x-0.5}{0.25},
\]

where `c_1/4 = 1` is the proposed pure quarter-completion. For an explicit
local `0–2` grandchild ARA, define

\[
x_G=2c_{1/4}=2\frac{x-0.5}{0.25}.
\]

Thus `x=0.5` maps to `x_G=0`, and the proposed complete projected grandchild
at `x=0.75` maps to `x_G=2`.

## Frozen diagnostics and gates

1. **Primary proximity:** the primary corrected crest is within `0.10` parent
   ARA units of `0.75`.
2. **Raw fixed-landmark replication:** at least `75%` of valid deterministic
   splits fall within `±0.10` of `0.75`.
3. **Participation ordering:** prompt participation and observed child crest
   have positive Spearman association.
4. **Leave-one-split-out displacement prediction:** monotone interpolation
   trained on the other splits predicts each held-out crest with median
   absolute error at most `0.05` ARA units. Endpoints are predicted by linear
   extrapolation from the two nearest training points.
5. **No endpoint manufacture:** the participation model is scored only against
   observed `x`; it is not recentered to `0.75` and cannot count as independent
   evidence for the exact quarter endpoint.

## Frozen verdict logic

- **Fixed quarter-completion supported:** gates 1–4 pass, including raw gate 2.
- **Participation-displaced quarter-compatible:** gates 1, 3 and 4 pass but
  raw gate 2 fails.
- **Not supported:** gate 1 fails, or the displacement does not reproduce under
  gates 3–4.

The middle verdict means the geometry is compatible with a pure `0.75`
landmark while the current data identify only a participation-dependent child
position. It does not prove that `0.25` is the physical carrier.

## Required outputs

- machine-readable results and split table;
- a visual showing parent `0.5`, pure `0.75`, observed split crests and the
  decompressed grandchild coordinate;
- an explicit statement of which result is fixed geometry, which is observed,
  and which is inferred.


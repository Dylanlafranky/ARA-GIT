# T372 — native child-half handover gradient audit

**Status:** post-result audit/calibration; not a blinded confirmation  
**Recorded:** 13 August 2026  
**Input:** official COHERENT CsI source files and the T371 fitted record

## Who, what, when, where, why and how

- **Who:** the prompt pion-neutrino branch and delayed muon-neutrino branch
  extracted in T371.
- **What:** the cumulative ARA coordinate reached when their instantaneous
  release rates become equal, and its displacement under different parent
  branch weights.
- **When:** native one-nanosecond source timing on `0 <= t < 6 microseconds`.
- **Where:** the same `0 <= PE < 60` COHERENT CsI analysis region, plus its six
  registered ten-PE energy cuts.
- **Why:** determine whether the apparent coarse `(0.5,0.5)` intersection is a
  physical child landmark, a parent-asymmetry displacement, or a plotting-bin
  artifact.
- **How:** retain the fitted T371 branch normalizations; reconstruct native
  flavor-resolved response curves; solve `r_prompt(t)=r_delayed(t)`; evaluate
  the cumulative ARA coordinate at that time; bootstrap the fitted event
  record; compare with the collaboration-supplied source mixture; sweep parent
  weights while holding measured branch shapes fixed.

## Declared measurements

1. T371 coarse-centre intersection `(t_H, x_H)`.
2. Native-resolution fitted intersection and 95% parametric-bootstrap interval.
3. Native-resolution collaboration-source intersection with no free prompt to
   delayed ratio.
4. The observed displacement `Delta_H=x_H-0.5`.
5. The complete identity-specific map
   `prompt share -> (handover time, cumulative ARA coordinate)`.
6. Six energy-cut handovers, labelled as sensitivity cuts rather than six
   independent experiments.

## Interpretation rules

- If the native reconstruction moves materially away from the coarse result,
  the coarse `0.5` reading is retracted rather than defended.
- A monotone counterfactual gradient is a mathematical property of the
  extracted branch shapes, not independent physical evidence.
- Agreement between the free-fit and collaboration-source handover supports
  measurement stability, not the universal child-half hypothesis.
- Exact `0.5` remains unconfirmed unless it survives native timing and an
  independent physical replication frozen before inspection.


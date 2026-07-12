# MX3a existing-data identity-formation result

**Tier:** DEVELOPMENT / SINGLE NOISE LEVEL / NOT CONFIRMATORY  
**Noise convergence tested:** No  
**Eligible slices:** 299

## Outcome

The existing archive can test whether the proposed closure index co-moves with independently calculated phase-space
organisation, but it cannot distinguish physical closure from the single simulation's finite-particle noise.

The closure index is defined only after the predeclared coherent-mode eligibility gate. Before that gate, a high raw
agreement can arise trivially because both summaries are near zero; it is not evidence that an identity already exists.

On eligible slices:

- closure vs field RMS: 0.8293;
- closure vs particle Other: -0.8595;
- closure vs normalised position–momentum mutual information: 0.8428;
- closure vs velocity-bin phase coherence: 0.7612;
- closure vs phase-space rank-2 fraction: -0.7971;
- closure vs approximate fundamental-wave trapped fraction: 0.7519.

After linearly controlling field RMS and fundamental-mode fraction:

- residual closure–mutual-information correlation:
  0.2546;
- residual closure–trapped-fraction correlation:
  -0.9076;
- residual closure–rank-2 correlation:
  -0.1462.

Matched-amplitude rising-versus-post-peak pairs (within 1% field RMS): 80.
Mean post-minus-pre closure: -0.000800461592338704.
Mean post-minus-pre mutual information: 0.0009898260183421321.
Mean post-minus-pre trapped fraction: 0.02621887784104382.

The matched-amplitude result is the main narrowing: closure does not separate rising from post-peak structural history
when field amplitude is nearly fixed, although the approximate trapped fraction increases. The large negative partial
trapping correlation is not treated as a physical inverse law because late-time collinearity and the approximate
single-wave separatrix can reverse a residual relation.

## Held-late development comparison

The baseline uses field RMS plus fundamental-mode fraction. The added model includes the closure index. Both are fitted
on the first 70% of eligible development slices and scored on the same final 30%; this remains calibration evidence.

| Target | Baseline R² | + closure R² | Change |
|---|---:|---:|---:|
| position–momentum mutual information | -5.4265 | -5.1378 | 0.2887 |
| approximate trapped fraction | 0.7071 | 0.8461 | 0.1391 |
| phase-space rank-2 fraction | -124.2124 | -123.9653 | 0.2470 |

## Fences

- The trapping fraction is an approximate fundamental-wave separatrix diagnostic, not particle-orbit tracking.
- Mutual information and SVD rank are generic structure measures, not uniquely plasma trapping.
- All 459 times and this archive have now been inspected; no result here is prospective.
- The missing particle-count/seed axis remains the decisive MX3 test.

## Verdict

`VISUAL ORGANISATION CONFIRMED / CLOSURE CO-MOVES / MATCHED-AMPLITUDE IDENTITY SEPARATION NULL / NOISE CONVERGENCE OPEN`

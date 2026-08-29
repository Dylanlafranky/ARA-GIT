# T418 report design and chart map

## Delivery

- Audience: technical, with ARA-first interpretation and conventional predictive controls beside it.
- Surface: one self-contained portable HTML report built from the canonical artifact contract.
- Primary question: does the curved `I_parent = 2` edge in T417 preserve an ordered child continuation, and does that continuation independently predict the later State Di-ARA?
- Comparison basis: parent/State baseline, correctly timed child, circularly shifted child, reversed child, and wrong-frequency child.
- Regime split: validation fields (68–500 G) and high-field holdout (1800–2484 G) are never pooled in the reader-facing evidence.

## Chart map

| Section | Question | Family/type | Fields | Supported takeaway |
|---|---|---|---|---|
| Parent shoreline | Where is the apparent curved edge? | Relationship/scatter | coupled amount `A`, balance `B`, parent stage, exact `I=2` and `R=2` boundaries | The upper curve is the exact `I=2` parent boundary, not missing plot area. |
| Open child | What lies beneath the clipped parent coordinate? | Trend/line | time, parent `I`, opened child, child anti-phase, parent ARA | The raw local/null ratio continues smoothly after the parent reaches its ceiling. |
| Continuation distribution | Is the continuation stable across sequences and regimes? | Distribution/bar | opened child bins, split | Post-boundary child values cluster just beyond their own ridge in both regimes. |
| Predictive test | Does the child help forecast later State coordinates? | Comparison/bar | model, relative MSE improvement, split | The validation advantage is small and does not survive high-field holdout. |
| Field detail | Is any advantage broad or field-specific? | Relationship/scatter | field, RF period, sequence improvement | Gains change sign across fields and RF periods. |
| Timing null | Is the result tied to correct temporal placement? | Distribution/bar | shifted-child MSE, observed MSE | Validation timing specificity passes once; it fails in high-field holdout. |
| Gates and audit | What exactly passed? | Exact tables | gate, status, estimate/interval; audit check | Geometry and arithmetic pass; the predictive identity claim does not. |

## Palette and accessibility

- Blue is used for observed/validation structure and orange for high-field holdout or contrast.
- Boundaries and controls also use labels, line styles, or explicit category names; color is not the only encoding.
- Every axis states the ARA range, physical unit, or error scale. Every chart has an adjacent interpretation paragraph.


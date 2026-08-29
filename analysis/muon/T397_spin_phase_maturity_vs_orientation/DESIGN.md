# T397 portable report design and chart map

## Audience and reading order

The report is written for technically literate ARA reviewers and physics
readers. It leads with the decision, then separates orientation evidence from
the weaker common-mode maturity lead before documenting the exact cuts,
controls, limits and next replication.

## Visual hierarchy

1. **Field gains (`field_gains`)** — primary decision figure. It compares the
   four frozen cuts at 63, 160 and 400 G. The x-axis is applied field in gauss;
   the y-axis is held-out relative weighted-SSE gain in percent. The adjacent
   prose explicitly states that gain is prediction-error reduction, not a
   release probability.
2. **Strict common-mode phase profiles (`w_phase_profiles`)** — physical-scale
   diagnostic. The x-axis is one normalized spin turn; the y-axis is the
   fractional residual after removing the parent envelope, in percent. Each
   field has observed and calibration-trained fitted traces. The adjacent
   prose identifies the trace as a small unresolved residue.
3. **Cadence controls (`cadence_controls`)** — specificity check. The x-axis is
   frequency multiplier and the y-axis is held-out gain in percent. The known
   physical cadence is marked at 1.0 and compared with frozen wrong cadences.
4. **Phase amplitudes (`phase_amplitudes`)** — scale comparison. The x-axis is
   field in gauss and the y-axis is phase amplitude as a percentage of the
   corresponding parent envelope. This prevents a large prediction gain in O
   from being mistaken for a large parent-population modulation.
5. **Gate table** — all predeclared pass/fail conditions are visible. Neither
   color nor narrative alone carries the decision.
6. **Source table** — shows the unchanged medium, temperature, detector count,
   native bin count and train/validation/holdout partition.
7. **Validation table** — shows every independent recomputation check.

## Style

- Blue/gold categorical palette, dark-neutral report surface supplied by the
  portable artifact builder.
- Zero baselines are drawn where sign matters.
- Labels include units (`G`, `%`, spin turns).
- Numeric interpretation remains in text immediately before each chart.
- No chart is evidence without the corresponding frozen gate and caveat.

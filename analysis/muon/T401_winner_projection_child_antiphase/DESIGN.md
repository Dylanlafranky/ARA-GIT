# T401 portable report design

## Audience and reading order

Technical ARA and measurement-method readers. The report answers the projection question first, then separates full occupancy, winner projection, reflected exchange, controls and limitations. It never treats an omitted winning bin as an empty physical state.

## Chart map

1. **Full-distribution occupancy**
   - Question: is the candidate `1.25–1.50` band actually empty or depleted?
   - Family/type: grouped comparison bar.
   - Fields: local ARA bin, mean occupancy, C/AC source.
   - Takeaway: the candidate holds ordinary occupancy and is almost equal to its neighbours.

2. **Binned and continuous winners**
   - Question: does the missing-winner pattern survive more splits and removal of fixed-bin edges?
   - Family/type: grouped comparison bar.
   - Fields: local ARA region, winner fraction, binned/KDE method.
   - Takeaway: both methods enter the candidate band; the visual gap is not stable.

3. **Reflected-pair exchange**
   - Question: does the exact ARA reflection carry a consistent inverse relation across splits?
   - Family/type: grouped signed bar with zero reference.
   - Fields: predeclared reflected pair, CLR Spearman rho, C/AC source.
   - Takeaway: the C reflection is weak, mixed in sign and not uniquely ranked.

4. **Observed winners versus sampling null**
   - Question: is the winner pattern distinguishable from sparse sampling of the measured full distribution?
   - Family/type: grouped comparison bar.
   - Fields: local ARA bin, winner fraction, observed/null series.
   - Takeaway: the candidate winner rate matches the sampling-only prediction.

## Palette and non-colour policy

- Hard two-root cap: blue for C/observed, gold open or hatched styling for AC/control.
- Series names remain visible; no meaning relies on colour alone.
- The ridge and zero references use dark neutral lines.
- All axes show ARA units or fractions explicitly.

## Output and QA

- Primary surface: self-contained portable HTML from canonical `artifact.json`.
- Static QA companion: `T401_WINNER_PROJECTION_CHILD_ANTIPHASE.png`.
- The independent validator checks hashes, row counts, probability closure, candidate metrics, reflection arithmetic, gates and the saved figure.

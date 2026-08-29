# T398 portable report design and chart map

## Audience and reading order

Technical ARA and physics readers. The report answers the user’s question
first, then moves from the native overlap to the two delayed children, the
0–2 ARA traversal, measured event counts, independent replication and the
separate silver comparison. Evidence class and claim boundary are visible
before methodology and validation.

## Chart map

1. **Native source, inferred population and delayed release**
   - Question: can the population-level source, storage and release curves be
     read on one time axis?
   - Family/type: highlighted multi-series line.
   - Fields: time in microseconds, normalized value, curve identity.
   - Takeaway: the fitted delayed branch takes over from the prompt branch at
     the dotted equality landmark; the remaining-muon curve is derived.
   - Palette: blue/gold roots plus neutral reference line.

2. **Delayed neutrino child templates**
   - Question: what sits inside the combined delayed branch?
   - Family/type: multi-series line.
   - Fields: time in microseconds, contribution divided by delayed peak,
     flavor-template identity.
   - Takeaway: νe and anti-νμ template components add exactly to the delayed
     population but are not event-by-event flavor tags.

3. **Cumulative 0–2 ARA traversal**
   - Question: where does instantaneous equality occur relative to cumulative
     child-half, parent-ridge and window-closure landmarks?
   - Family/type: single line with labeled references.
   - Fields: time in microseconds and cumulative ARA coordinate.
   - Takeaway: rate equality precedes the cumulative parent ridge.

4. **T371 measured and fitted timing components**
   - Question: is the smooth delayed curve supported by measured event counts?
   - Family/type: multi-series line over 12 released timing bins.
   - Fields: recoil time, events per 0.5 microseconds, component.
   - Takeaway: the fitted delayed population is required in the primary data.

5. **T378 independent holdout timing components**
   - Question: does the temporal order repeat in the earlier source?
   - Family/type: multi-series line over 12 released timing bins.
   - Fields: arrival time, events per 0.5 microseconds, component.
   - Takeaway: positive prompt and delayed populations repeat in the right
     order, while the stricter exact-handover verdict remains partial.

6. **T397 separate RAL Silver common-mode spin phase**
   - Question: what did the separate precursor-like spin cut actually look
     like, and can it be kept visibly distinct from COHERENT?
   - Family/type: two-series phase-folded line.
   - Fields: spin phase turns, fractional residual percent, trace identity.
   - Takeaway: a coherent small phase residue exists in another experiment but
     cannot be event-linked to the neutrino timing source.

## Visual and evidence policy

- Every chart has units, ticks, a subtitle and an adjacent explanatory block.
- Dotted vertical lines mark fitted equality; they do not assert an individual
  particle creation instant.
- The report uses a restrained blue/gold palette with neutral reference lines.
- The HTML is generated only from the canonical `artifact.json` using the
  packaged Data Analytics portable builder.
- Full 5 ns native rows remain in the CSV and validator. The report chart uses
  a 25 ns display sample to reduce visual and browser load without changing
  the fitted landmark.


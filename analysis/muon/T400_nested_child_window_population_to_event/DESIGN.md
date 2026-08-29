# T400 portable report design

## Audience and reading order

Technical ARA and physics readers. The report leads with the frozen verdict,
then separates the population child construction from the transfer to
untouched detector-event candidates. Means and medians are shown beside modes
so a ridge-as-balance result cannot be mistaken for a ridge-as-density-peak
result.

## Chart map

1. **Population child window**
   - Question: where does the delayed crest land after the objective parent
     interval is expanded to a local ARA `0–2`?
   - Type: line with local ridge and primary crest references.
   - Takeaway: the curve is smooth and asymmetric; the crest is `0.706`, not
     the local ridge.

2. **Untouched event candidates**
   - Question: does the frozen child coordinate organise holdout event weight?
   - Type: weighted bar distribution.
   - Takeaway: the weighted centre is near `1`, but the maximum is upper-sided.

3. **Mode stability across deterministic splits**
   - Question: is the event mode stable under the declared data partition?
   - Type: split-count bar distribution.
   - Takeaway: `60%` lie in the broad event ridge, below the frozen `70%` gate.

4. **Population and event landmarks**
   - Question: which summaries transfer across grains?
   - Type: categorical bar comparison.
   - Takeaway: means and medians transfer near the ridge; modes do not.

## Evidence and visual policy

- Every plotted axis names the local child coordinate or event weight.
- The local `1.0` ridge is a reference, not a fitted result.
- Failed scientific gates remain visible beside successful integrity checks.
- Individual detector rows are never described as flavor-tagged neutrinos.
- The report is generated from `artifact.json` with the packaged portable
  report builder. Structural verification passed; browser-level verification
  was unavailable in the current runtime.


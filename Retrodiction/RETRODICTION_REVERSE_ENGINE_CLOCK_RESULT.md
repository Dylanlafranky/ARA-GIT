# Retrodiction = the forward engine-clock run on reversed time (4 June 2026)

ARA framework · Dylan La Franchi & Claude. Strict-causal, real NOAA NINO3.4 (1870+).
Script: `/tmp/rev.py` (engine-clock 55mo + home-AR ridge, golden split; applied to `ni` and to `ni[::-1]`).

**Premise (Dylan):** the geometry is just prediction in reverse. Implemented literally — reverse the time
series, run the *same* forward predictor; its "forecasts" on the flipped series are retrodictions on the
real one.

## Result — the engine runs both ways, nearly symmetric

| h (mo) | fwd corr | rev corr | fwd dir | rev dir |
|---|---|---|---|---|
| 6 | +0.530 | +0.484 | 0.661 | 0.649 |
| 12 | +0.135 | +0.112 | 0.766 | 0.713 |
| 18 | +0.104 | +0.058 | 0.806 | 0.744 |
| 24 | +0.045 | +0.021 | 0.796 | 0.752 |
| 36 | −0.017 | −0.010 | 0.683 | 0.681 |

- **Retrodiction works:** reverse direction skill ~0.71–0.75 across 1–2 yr; correlations track the forward
  curve. The engine-phase clock winds backward as cleanly as forward (an oscillator's phase is time-symmetric).
- **Reverse is slightly weaker than forward** (dir ~0.74 vs ~0.80 @18–24mo). This small, consistent gap is
  the **arrow of time** — ENSO's mild asymmetry (sharp El Niño onsets, slower decays = the measured skew)
  makes running it backward a touch harder. The gap is the irreversibility/entropy signature; it is small
  because the engine is *nearly* time-symmetric.
- **Same ~2-yr wall both directions:** reverse decoheres at the same rate forward does (zero past ~36mo).
  Retrodiction does not escape the predictability floor — phase loses coherence the same distance either way.

## Open thread (Dylan): work out the energy flows
Reverse weighting suggests **energy movement matters even more in reverse** — running backward, you are
inferring *what fed in to produce the present*, so the directional energy budget (who handed energy to whom,
and when) dominates. Candidate measurement: directional **energy flow** between rungs/feeders —
transfer-entropy / directed-coupling on the energy envelopes, compared forward vs reverse. The forward−reverse
asymmetry in those flows would localize *where* the arrow of time lives in the system (which handoffs are
irreversible). Companion: §3 overflow (energy spills UP toward 2.0) and the R-map (IOD=message, PDO=lock) in
`TheFormula/ARA_ENERGY_PIPE_AND_SPHERE_WELLS_RESULT.md` / ledger BP-14.

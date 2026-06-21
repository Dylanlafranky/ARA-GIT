# ENSO FORECAST OF RECORD — issued 2026-06-07

**⏱ Timestamp (forecast made):** 2026-06-07 06:08:03 UTC
**Purpose:** a pre-outcome, timestamped prediction so it can later be verified the forecast was made
*before* the actual ENSO evolution. Verify the issue date via the git commit that adds this file
(authoritative timestamp) and the content hash below.

## Method (the ACTUAL ARA framework — no shortcuts)
Model = engine clock (55-mo phase) + home AR lags [1,2,3,6,12,24,48] + **feeders SOI & PDO** +
**2−ARA energy input** (warm-water-volume charge & recharge-rate mapped through ARA). Direct
multi-horizon ridge (one model per lead h), trained on 1980→anchor, fired once from the current origin.
Strict-causal; no future data in training. **IOD omitted** (missing for late-2025/2026 in the source).
Script: `Retrodiction/plot_enso_forecast_with_reference.py` / `/tmp/record.py`.

## Data anchor (state at issue)
- Last observed NINO3.4 (CPC ONI): **Feb 2026 = −0.16** (neutral, warming from a weak La Niña:
  Dec 2025 −0.49 → Jan −0.37 → Feb −0.16).
- Subsurface warm-water volume (WWV, current to **Apr 2026**): **+1.96 σ and rising** — strong recharge /
  warm-event loading.
- SOI through Mar 2026 still positive (+2) — atmosphere lagging the charging subsurface (normal recharge).
- NOTE on data lag: issued 7 Jun 2026, but official NINO3.4/ONI only available through Feb 2026, so the
  genuinely-future, unobserved months are **Jun 2026 onward**.

## THE FORECAST (ARA forward NINO3.4 anomaly, °C)
| target | lead | forecast |
|---|---|---|
| Mar 2026 | +1 | −0.07 |
| Apr 2026 | +2 | +0.03 |
| May 2026 | +3 | +0.19 |
| **Jun 2026** | +4 | **+0.29** |
| Jul 2026 | +5 | +0.39 |
| **Aug 2026** | +6 | **+0.43** |
| Sep 2026 | +7 | +0.43 |
| Oct 2026 | +8 | +0.41 |
| Nov 2026 | +9 | +0.41 |
| **Dec 2026** | +10 | **+0.43** |
| Jan 2027 | +11 | +0.44 |
| **Feb 2027** | +12 | **+0.37** |
| Mar 2027 | +13 | +0.30 |
| May 2027 | +15 | +0.16 |
| Aug 2027 | +18 | −0.03 |
| Nov 2027 | +21 | −0.02 |
| Feb 2028 | +24 | −0.04 |

## Headline call
**Direction: WARMING.** ENSO forecast to cross into **weak El Niño territory by mid-2026**, peaking around
**+0.4 to +0.45 °C in late 2026 / early 2027**, then **decaying back to neutral through 2027** into 2028.

## Honest caveats (binding part of the record)
- **Direction, NOT magnitude.** The amplitude (~+0.4 peak) is the model's central estimate; the *strength*
  category (weak/moderate/strong/"super") is the ARA-1.0 randomness barrier — **NOT a confident call.** This
  is explicitly **not** a "super El Niño" prediction.
- **Reliable horizon ≈ to ~12 months** (peak in late 2026). The flattening to neutral past ~18 months is
  honest mean-reversion beyond the predictability wall, not a confident neutral prediction.
- Uses SOI+PDO feeders + WWV energy; IOD omitted (data gap). A current-WWV-weighted version would lean the
  near-term warming slightly stronger/earlier (reservoir is at +1.96σ).
- For comparison, operational consensus at issue: El Niño likely developing through 2026, **strength
  uncertain** (<37% any single category) — our call is consistent (warm, magnitude open).

## Verification (after the fact)
Compare observed CPC ONI / NINO3.4 for Jun 2026 → Feb 2028 against the table above. Score: direction
hit-rate (did it warm, peak ~late 2026, return neutral 2027) and correlation of the trajectory.

**Content hash (SHA-256 of the forecast table values, for tamper-evidence):** _see companion line added
on commit_. Authoritative issue time = git commit date of this file.

# 16 — ENSO forecast-of-record & magnitude-from-reservoir (08-06-26)

**Thread:** A timestamped, pre-outcome ENSO forecast of record, plus the magnitude / lag / shape-vs-magnitude decomposition work that underpins it, and a gallery of plots applying the formula across systems. Dated 7–8 June 2026.

**Model logic / idea:** Issue a real, hash/timestamp-verifiable ENSO forecast so it can later be checked it was made *before* the outcome. The forecasting method = engine clock (55-mo phase) + home AR lags + SOI/PDO feeders + 2−ARA energy input (WWV recharge). The magnitude work shows **magnitude is partly predictable**: the next swing's size is set by how charged the subsurface reservoir (WWV) is at the centerline crossing, with the wave-asymmetry (ARA skew) as a second-order term. Shape and magnitude are decomposed and recombined (multiply back) rather than mashed into one ridge.

**Systems tested:** ENSO/NINO3.4 (1870+ for magnitude validation, feeder era for the live forecast); ECG plots as cross-system illustration.

**What was tested:**
- `FORECAST_OF_RECORD_ENSO_2026-06-07.md` + `FORECAST_TIMESTAMP_AND_HASH.txt` — the issued forecast and tamper-evidence.
- `magnitude_reservoir_longrecord_test.py` — reservoir-at-crossing → next-peak magnitude over 64 warm onsets (1870+).
- A large set of `plot_*.py` scripts producing the figure gallery (hedged-vs-unhedged, magnitude-from-reservoir, shape×magnitude, siphon-vs-formula, formula-across-systems, raw ECG).

**Key results:**
- **Forecast of record (issued 2026-06-07):** direction = WARMING; ENSO forecast to cross into weak El Niño by mid-2026, peak ~+0.4 to +0.45°C late 2026/early 2027, decay to neutral through 2027–28. Explicitly **direction not magnitude** — the strength category is the ARA-1.0 randomness barrier and NOT a "super El Niño" call. Reliable horizon ~12 months.
- **Magnitude IS partly predictable:** reservoir-at-crossing → next warm-peak magnitude +0.34–0.40 out-of-sample, validated over 64 warm onsets (pre-1980 +0.51, modern +0.24). ARA asymmetry (skew) adds a second-order +0.20 on the residual (lifting +0.336→+0.367). Magnitude = reservoir (1st) + ARA skew (2nd) + random core; it is a calibrated *lean*, not an exact peak.
- **Shape × magnitude decomposition:** geometry gives shape (corr +0.49, amplitude only 0.66 of truth); multiplying reservoir+ARA magnitude back restores amplitude to 1.03. Honest combined at true 6-mo lead: corr +0.506 vs persistence +0.410.
- **The ~4-month lag is intrinsic, not leakage:** it is the MMSE hedge of the training (mean-reversion shrinkage = the visible shadow of the ARA-1.0 barrier). Genuinely skilful (corr of predicted vs actual 6-mo CHANGE = +0.458; direction 0.629). It cannot be "shifted back" without leaking future data or relabelling it a shorter-lead forecast; rolling the data forward IS the legitimate shift. To tighten timing you must measure something that leads, not average things that lag.

**What was NOT tested / open:** Verification of the issued forecast is by construction future (compare CPC ONI Jun 2026 → Feb 2028 against the table). IOD was omitted from the live forecast (data gap); a current-WWV-weighted version would lean warming slightly stronger/earlier.

**Key files:**
- `FORECAST_OF_RECORD_ENSO_2026-06-07.md` — the timestamped forecast (headline).
- `MAGNITUDE_LAG_AND_DECOMPOSITION_RESULT.md` — magnitude/lag/decomposition result.
- `FORECAST_TIMESTAMP_AND_HASH.txt`
- `magnitude_reservoir_longrecord_test.py`

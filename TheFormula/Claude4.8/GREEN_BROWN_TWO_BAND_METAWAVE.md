# The "green & brown" two bands + the amplitude meta-wave

Standalone note so this can be shared directly. Dylan flagged the two interannual
bands (plotted green and brown) as a wave-above-ENSO and said the *amplitude* was its
own wave; Claude first tested it with a crude rolling-std proxy and got a near-null, was
unsure, then re-tested with the proper Hilbert envelope and confirmed Dylan was right.
This note packages what was found, with the numbers and how to reproduce them.

Reproduce: `python3 two_band_metawave_analysis.py nino34_long_anom.csv`
→ writes `results/two_band_metawave.json`. Source data: NINO 3.4 monthly anomaly,
1870–2025 (1872 months), `nino34_long_anom.csv`. All from the NINO record alone.

## The two bands (green = QB, brown = LF)

The interannual power spectrum of NINO 3.4 splits into two bands of comparable power:

- **GREEN / quasi-biennial (QB), ~28 months** — peaks at 27.9, 29.2, 30.7, 34.7, 20.8 mo.
- **BROWN / low-frequency (LF), ~42–67 months** — peaks at 66.9 (strongest), 42.5, 62.4,
  50.6, 56.7, 45.7, 78.0 mo.

These are two genuine bands, not one mode. The earlier single-mode LIM fit a ~38–45 mo
oscillation, which is just the average of the two — which is *why* a single mode kept
mis-timing the system.

## They are a coupled pair (bispectrum)

A segmented bispectrum (17 Hann segments, length 256 mo) tests whether the bands are
phase-locked or independent neighbours. Noise floor ≈ 0.059; rough significance ≈ 0.176
(3× floor). The QB×LF interactions clear it:

| interaction | bicoherence b² | combination tone |
|---|---|---|
| QB28 × LF42 | **0.336** | 17.1 mo |
| QB28 × LF48 | 0.242 | 18.3 mo |
| QB28 × LF67 | 0.214 | 19.7 mo |

So the two bands are phase-coupled, feeding a combination tone near **15–20 months** —
the "uncoloured zone" Dylan pointed at. Coupling is real but moderate (~⅓ of the
combination-tone power is phase-locked). Caveat: 17 overlapping segments, so the
effective sample is smaller; strongest triads are robust, the marginal ones less so.

## The amplitude is its own wave (the meta-wave)

The Hilbert envelope of the band-passed signal — the proper "shape of the amplitudes" —
is a coherent wave, **roughly twice as slow as the signal**:

- envelope de-correlation time **14 months** vs the signal's **7 months**.
- envelope spectral peaks:
  - **7.8 yr (93.6 mo)** — dominant (decadal modulation)
  - **12 yr (144 mo)** — second (interdecadal)
  - **5.2 yr (62.4 mo)** — third, sitting on the **two-band beat** (28 & 48 mo beat at 67 mo)

The ~5.2 yr component is deterministic — it's the two coupled bands swinging in and out
of alignment (loud when aligned, e.g. 2023–24; quiet when opposed). The 7.8 and 12 yr
components are genuine decadal modulation and harder (the PDO does NOT track them, r≈+0.07).

Note: an initial 15-mo rolling-std proxy gave envelope de-correlation ~8 mo (barely
slower than the signal) and looked like a near-null — that was the wrong instrument.
The Hilbert envelope is the right one and shows the real, slower meta-wave.

## The honest limit (why this isn't bankable forecasting)

The meta-wave is real and the bands are coupled, but it does **not** extend the forecast
horizon past ~6 months:

- Forecasting the envelope causally collapses to climatology by ~12 mo (same wall as the
  signal) — the amplitude inherits the same stochastic wind forcing that caps the signal.
- The skill *recurrence* this structure produces (a faint re-emergence of forecast skill
  near ~27 mo, the QB period) is **non-stationary** — the QB period wanders 2–2.5 yr, so
  the re-emergence drifts and cannot be reliably calibrated to.

So: **structure confirmed (the green/brown bands are a real coupled pair with a real
amplitude meta-wave), forecast horizon unmoved (~6 months).** This is the recurring
split — relations are real and readable, but only forecastable while an observable
driver-below stays legible. See `README.md` §8–10 and `SESSION_LOG.md` for the full chain.

## Files for this finding

- `two_band_metawave_analysis.py` — reproduces everything here from the NINO csv.
- `results/two_band_metawave.json` — the computed numbers (spectrum peaks, bicoherence, envelope).
- `results/nino_spectrum_interannual.json` — earlier two-band spectrum dump.
- `results/skill_by_lead_walkforward.json` — the skill-recurrence curve (the ~27 mo re-emergence).

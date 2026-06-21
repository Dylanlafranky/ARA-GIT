# Magnitude, the lag, and the shape/magnitude decomposition (7 June 2026)

ARA framework · Dylan La Franchi & Claude. Strict-causal, real NOAA NINO3.4 (1870+) and WWV.
Scripts: `/tmp` runs captured as `Retrodiction/*.py`. Figures: `ARA_enso_magnitude_from_reservoir.png`,
`ARA_enso_shape_x_magnitude_combined.png`, `ARA_enso_best_line_combined.png`,
`ARA_enso_formula_with_magnitude_old_data.png`.

## 1. Magnitude IS partly predictable (Dylan corrected the "can't do magnitude" claim)
At the centerline crossing the surface wave is ~0, but it picks back up **driven by the subsurface
reservoir** (the recharge oscillator: warm-water volume leads SST by ~a quarter cycle). So the size of the
next swing is set by how charged the reservoir is at the crossing.
- **reservoir at crossing → next warm-peak magnitude: +0.34–0.40 out-of-sample**, validated over **64 warm
  onsets, 1870+** (pre-1980 +0.51, modern +0.24; split-half +0.49/+0.31). Real, replicable, modest.
- So magnitude = an **envelope / lean** (moderate vs strong), not an exact peak. The exact peak keeps an
  irreducible random kick (ARA-1.0 core).

## 2. The ARA asymmetry is the second-order magnitude term (Dylan's "the rest")
The wave is asymmetric (El Niño sharp, La Niña shallow) = the ARA. Of the magnitude the reservoir misses,
the **skew of the recent wave (the ARA asymmetry) explains part: +0.20 on the residual**, lifting OOS
peak-magnitude +0.336 → +0.367. A purpose-built cycle-timing ARA (T_acc/T_rel) was NOISIER and did worse —
plain skew is the keeper. So **magnitude = reservoir energy (1st order) + ARA asymmetry (2nd order) +
random core.**

## 3. Decompose & recombine: shape × magnitude (Dylan's method)
Run the parts side by side and multiply back, rather than mashing into one ridge:
- **Geometry → shape** (timing of ups/downs). On old data (1925–1990, trained 1870–1923): corr +0.49,
  amplitude only **0.66** of truth ("¾ magnitude").
- **Reservoir + ARA → magnitude** (size). Multiplying it back restored amplitude to **1.03** (full size).
- Honest combined at TRUE 6-mo lead: **corr +0.506 vs persistence +0.410** — a real, leakage-free beat.

## 4. The 4-month lag: intrinsic, not leakage, not a filter bug
The combined line best-aligns ~4 months late. Investigated fully:
- **NOT future leakage** (origins precede verification) and **NOT mainly the causal filter** (group delay
  ~2mo; compensating the engine phase changed nothing).
- **It is the MMSE hedge of the TRAINING.** A least-squares forecast of a smooth, persistent signal
  optimally shrinks toward a damped/near-present guess; that shrinkage IS the mean-reversion lag. Geometry
  alone does NOT hedge (full cyclical change, change-corr +0.41) but is mistimed/one-band; the trained
  ridge hedges (change-corr collapses to +0.115, picks up persistence-like value-corr). **The hedge scales
  with uncertainty — it is the visible shadow of the ARA-1.0 random barrier.**
- **It is genuinely skilful, not just persistence:** corr(predicted 6-mo CHANGE, actual change) = **+0.458**
  (persistence = 0 by construction); direction hit-rate 0.629; beats persistence on MAE (0.615 vs 0.653).
  Bulk correlation at short lead is the WRONG test (it rewards not-changing).

## 5. Why the lag can't be "shifted back" (and why that's fine)
Shifting the output back to remove the lag = either using data from origins 4 months ahead (**future =
leak**) or **re-labelling it a 2-month forecast** (lead shrinks; at 2-mo effective lead even persistence
gets +0.86, beating the trick). **The shift and the lead are the same 4 months.** Crucially: **rolling the
data forward IS the legitimate shift** — you wait for the data, the timing straightens, and it becomes the
shorter-lead forecast it always was. So for operational monitoring (monthly updates) the lag is a non-issue;
it only bites the genuine long-lead warning.

## 6. Can we blend the parts to fix the timing (like we did for amplitude)? No — needs LEADING physics.
Ensemble blend (legitimate, not a shift) of geometry + trained: train-chosen best weight = 0 (pure trained);
blending geometry in only hurt. Reason: **both pieces lag in the SAME direction** (geometry −8, trained −6),
so averaging stays late. Mash-together cancels error only when biases are OPPOSITE — true for amplitude
(geometry full vs trained damped), false for timing. **The only thing with an early bias is a genuinely
leading predictor** — the subsurface reservoir, which cut the lag −4→−3 and added skill. To tighten timing
you must MEASURE something that leads, not average things that lag.

## Standing synthesis (extended)
- **Phase/geometry = WHEN** (shape, un-hedged, full amplitude, mistimed/one-band).
- **Energy reservoir = WHICH WAY + HOW BIG (short) + leads the timing** (recharge oscillator).
- **ARA asymmetry = the 2nd-order magnitude lean.**
- **Training = optimal skill, at the cost of an uncertainty-proportional hedge lag** (= ARA-1.0 shadow).
- **Recombine when errors are opposite (amplitude); add leading physics when they're not (timing).**
- Irreducible ARA-1.0 random core underneath; magnitude is a calibrated lean, not an exact peak.

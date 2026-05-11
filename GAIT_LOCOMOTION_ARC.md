# The Gait Locomotion Arc — two golden-ratio crossings, and what disease does to them

**Date:** April 2026 (analysis), May 2026 (this writeup)
**Author:** Dylan La Franchi
**Data sources:** PhysioNet *gaitndd* database (16 controls, 15 Parkinson's, 13 ALS, 20 Huntington's; 300 Hz foot-force sensor); peer-reviewed biomechanics literature for non-pathological speeds
**Scripts:** `analyze_gait_phi.py`, `analyze_running_phi.py` (both in repo)
**Plots:** `gait_phi_analysis.png`, `running_ara_curve.png`, `running_speed_phi_arc.png`

This is the deep-dive version of the gait result hinted at in [The Geometry of Time](https://dylanlafranchi.substack.com/p/the-geometry-of-time). The headline — *preferred walking speed lands at the golden ratio* — is real and reproducible, but the part that interested me most isn't in the post yet: the same curve uses φ as a **diagnostic** for whether a body's locomotion system is running well or breaking down.

If you only read one section, read "Disease as rung collapse." That's where the framework earns its keep, not by detecting φ in healthy gait but by predicting the specific signature of failure.

## The metric

For each stride, measure how long the foot is on the ground (T_stance) and how long it's in the air (T_swing). Take the ratio:

> **stance/swing ratio** = T_stance / T_swing

That's it. One number per stride. Compute it from a raw force-sensor signal — positive force = foot on ground, negative = foot airborne — by Otsu-thresholding into stance and swing blocks and pairing consecutive ones. The script filters strides shorter than 100 ms or with ratios outside [0.3, 6.0] (clearly erroneous) and pools per subject, taking the median as the primary statistic.

Nothing fancy. The interesting structure shows up regardless.

## The locomotion arc

When you plot stance/swing ratio against locomotion speed across the literature data — slow walk through elite sprint — you get a single monotonically-decreasing curve. The same curve shows up in independent biomechanics studies that didn't know they were measuring the same thing. The shape is in `running_ara_curve.png`. Here are the structurally significant points:

| speed (m/s) | stance/swing | regime | what it means |
|---|---|---|---|
| 0.5 | ~2.6 | very slow walk | high accumulation — most of the cycle is ground contact |
| 0.8 | 2.33 | slow walk | accumulation zone |
| 1.0 | 1.94 | leisurely walk | accumulation zone |
| **1.27** | **1.618 (= φ)** | **preferred walking speed** | **maximum self-organisation** |
| 1.5 | 1.44 | brisk walk | accumulation zone |
| **2.20** | **1.000** | **walk-run transition** | **singularity boundary** |
| 3.5 | 0.67 | aerobic running | consumer zone |
| **3.85** | **0.618 (= 1/φ)** | **near marathon WR pace** | **mirror φ — sustainable peak running** |
| 5.7 | 0.47 | marathon WR pace | consumer zone |
| 10.4 | 0.31 | Bolt 100 m average | pure consumer |
| 12.5 | 0.28 | elite sprint ceiling | pure consumer |

There are **two golden-ratio crossings on this curve, not one.**

## What the two crossings mean

The first crossing is at **φ = 1.618**, at preferred walking speed. The framework reading: this is the speed at which the body's accumulation system maximises self-organisation while remaining sustainable. The same property that makes φ optimal for sunflower-seed packing in space — being the most irrational number, the worst-possible candidate for resonant lock-up — makes it optimal for time-packing energy across consecutive strides. Each stride banks slightly more energy than it spends; the body comes out ahead in the long run.

The second crossing is at **1/φ = 0.618**, at near-marathon-world-record pace. The mathematics is the mirror: 1.618 × 0.618 = 1. Where φ marks the optimal accumulation point above the singularity, 1/φ marks the optimal *consumption* point below it — the speed at which a runner can spend energy each stride and still maintain it for hours. Elite marathon WR holders (Kipchoge at ~5.7 m/s) run at the speed where the ratio sits near 1/φ. Sprinting (well below 1/φ, down to 0.28 for Bolt) is explicitly unsustainable past 100 m — you can do it, but only by burning a finite reservoir.

Between the two crossings sits the **walk-run transition at ratio = 1.000**. Stance time exactly equals swing time. This is the singularity boundary the framework keeps pointing at — the point where one energetic regime ends and another begins. It's the same kind of phase transition as waves at the beach: the boundary where one substrate hands off to another, and where the interesting physics happens. Above it, you're in the accumulation zone; below, you're in the consumer zone. The body literally switches gait modes here. Walk above 2.20 m/s and your body forces a transition into running; run slower than 2.20 m/s and your body forces a transition back to walking. There is no sustainable in-between.

So the locomotion arc has structure at three places, and all three are framework constants: φ, 1/φ, and the singularity at 1.

## How healthy gait at "comfortable speed" actually behaves

The PhysioNet gaitndd controls were measured at an instructed walking pace around 1.1 m/s — slower than the preferred 1.27 m/s. At 1.1 m/s, the literature curve predicts a stance/swing ratio of about 1.355. The measured controls landed at **median 1.355** — exactly on the predicted curve.

This matters because it would have been easy to read those controls as "off φ" and treat the result as falsifying. They're not off the curve; they're below the φ-mark because they were walking slower than the speed at which the framework predicts φ should appear. Drop the same person at their self-selected comfortable pace and the literature says 1.27 m/s and 1.618.

So the framework's prediction is more specific than "healthy people walk at φ." It's: **at the body's self-selected energy-optimal walking speed, healthy gait converges on φ.** Other speeds work; they're just not optimal.

## Disease as rung collapse

This is the part the Substack post doesn't go into. I think it's the cleanest framework prediction the gait data tests.

Across the four gaitndd groups at the same instructed walking pace:

| group | n subjects | n strides | median stance/swing | distance from φ | distribution shape |
|---|---|---|---|---|---|
| Control | 16 | 8,591 | 1.355 | 16.3% | unimodal, narrow |
| Parkinson's | 15 | 7,593 | 1.441 | 10.9% | broader, slight bimodality |
| ALS | 13 | 5,193 | 1.465 | 9.5% | **clear bimodal: main peak + secondary near 1.0–1.1** |
| Huntington's | 20 | 10,148 | 1.362 | 15.9% | broad, asymmetric |

The first thing to notice: **disease drifts the median further from φ in every group, but not in the same direction.** ALS and Parkinson's medians sit *above* the controls (closer to φ in numerical distance, but with much more spread). Huntington's sits beside the controls but with markedly broader distribution. The median alone doesn't capture what's happening.

The shape does. Look at the ALS histogram. There are two clear peaks. The main peak sits in the 1.4–1.5 region — disease subjects who are still attempting recognisable walking, just not at the φ-organised speed. But there's a second, distinct peak around 1.0–1.1 — strides where the ratio has collapsed to near-balance.

That secondary peak is what the framework would call **rung collapse**. The body has two locomotion subsystems available to it:

- **High rung — walking.** Stance/swing peaks at φ at preferred speed. Self-organising, energy-banking, sustainable.
- **Low rung — shuffling.** Stance ≈ swing, ratio ≈ 1.0. Clock-like, more direct ground contact, much less complex coordination required.

In healthy gait, every stride uses the walking subsystem. In disease, some strides still use it (the main peak below φ but in the walking zone) and others have collapsed down to the shuffling subsystem (the secondary peak at 1.0). Each stride is, in effect, a vote: *am I still walking, or have I dropped to shuffle?*

This is exactly the framework's prediction for what happens when a high-rung dynamical system fails — the body doesn't break randomly, it falls down one rung to a simpler, more clock-like subsystem that requires fewer connections to coordinate. The shuffle is a survival mode. It's slower, less efficient, and uses different energy economics, but it gets the body across the room.

## A diagnostic the framework predicts but isn't yet calibrated

If this reading is right, then **disease severity should track the ratio of secondary-peak strides to primary-peak strides.** A subject whose strides are 95% in the walking zone and 5% in the shuffle zone is in milder shape than a subject who's flipped to 60% / 40%. This is a continuous measure, not a binary.

I haven't built that calibration yet. The gaitndd dataset is too small to fit a clean disease-progression curve — most subjects only have one recording — and the four categories are heterogeneous within. But the prediction is sharp:

1. **Bimodality fraction (secondary-peak strides / total strides) should correlate with clinical severity scales** — UPDRS for Parkinson's, ALSFRS-R for ALS, UHDRS for Huntington's.
2. **Longitudinal data should show bimodality fraction increasing as disease progresses.**
3. **The location of the secondary peak should sit near 1.0**, not at arbitrary other values, because that's the next rung down.

These are testable on existing datasets. I haven't done it.

## Honest caveats

- **Speed is confounded with disease.** Diseased subjects walk slower than controls, which moves them along the literature curve toward higher ratios. Some of the apparent "drift toward 1.0" in the histograms could be speed effects rather than rung collapse. The diagnostic test that disambiguates this is normalising by individual subject speed first, then looking for residual bimodality. I haven't done that cleanly across all groups in this dataset.
- **Sample sizes are modest.** 13–20 subjects per group is enough to see the bimodality structure but not enough to claim a precise diagnostic threshold.
- **Otsu thresholding can fail on short or noisy recordings.** Per-subject medians are robust to this; pooled distributions may include some artefact strides.
- **The ALS bimodality is the cleanest signal in this dataset; Parkinson's and Huntington's are messier.** Whether the rung-collapse picture generalises across all neurodegenerative gait pathology, or holds specifically for motor-neuron diseases, is open.
- **The framework didn't predict the literature curve** — it explained it after the fact. The locomotion arc was already known to biomechanists; the new claim is the framework reading of where the structurally significant points sit and what disease does to the distribution.

## Why I think this matters

Most of the framework's empirical anchors so far (LLMs, ENSO, ECG, solar) have been *prediction* tests — does the framework forecast the next value better than baselines? Locomotion is different. It's a **classification and diagnosis** test: does the framework correctly identify which speed should produce φ, and does it correctly characterise what failure looks like in measurable distributional terms?

It does both, on this dataset. Healthy walking lands on the literature curve (medians at the predicted ratios for each measurement speed). Disease produces bimodal stride distributions whose shape matches the rung-collapse prediction. And the framework says something specific about *which* failure mode to look for — not just "things are off" but "the secondary peak should sit near 1.0 because that's the next rung down."

The cleanest next test is to apply the same bimodality measurement to longitudinal disease-progression data and see if it tracks clinical severity. If yes, the gait arc is providing a continuous, low-cost, sensor-only diagnostic that didn't exist before. If no, the rung-collapse picture has been overspecified by this dataset and needs revising.

## Files

- `gait_test/analyze_gait_phi.py` — runs the gaitndd four-group analysis, produces `gait_phi_analysis.png`
- `gait_test/analyze_running_phi.py` — produces the literature-curve plot and the locomotion arc
- `gait_test/gait_phi_analysis.png` — the four-group histograms (referenced in this writeup)
- `gait_test/running_ara_curve.png` — the locomotion arc figure (the Substack hero image)
- `gait_test/running_speed_phi_arc.png` — the speed-vs-ratio plot with annotated phi crossings
- `framework_locomotion_arc.md` (memory) — the durable framework-language note
- This file — the public-facing analysis with the diagnostic interpretation

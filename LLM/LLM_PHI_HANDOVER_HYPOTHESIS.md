# LLM scaling & the φ-handover ceiling — concept + test design (banked 10 June 2026)

Dylan's hypothesis, parked for a clean run later. **φ is the landmark, not the only target** — we're looking
for rung structure / a self-organization wall, with φ as the marker for "the layer it can't break through."

## The concept
An artificial network **cannot organize its own energy** — at inference it's a fixed feed-forward map, no
flywheel, no self-storage/recycling across the computation. Physical/biological storers (sun, life) *can*
flywheel and climb toward the lossless harmonic limit (ARA→2, Q→∞). A net can't, so Dylan's claim:
**it is locked at the φ-handover — the maximum single-pass energy/information transfer — and can't break
through to the self-organizing layer above it.** So:
- The **floor** a net can't cross = the **data's entropy** (the irreducible loss). NOT φ.
- The **ceiling on its efficiency / the wall it stalls at** = the **φ-handover**, because it can't recycle
  past single-pass transfer. That's where φ enters — as the self-organization wall, not the floor.

## What was tested (10 Jun) and the verdict
- **Neural scaling laws are power laws (log-log line) with an irreducible floor** (data entropy ≈ 1.69 nats
  for Chinchilla). Both real and standard.
- **"Is the scaling EXPONENT φ?" → NULL / unfalsifiable.** Mapped params=space(octave), data=time(φ).
  Kaplan weakly supports it (data exp 0.095 ≈ 1/φ⁵ at 5%, params closer to octave); **Chinchilla contradicts
  it** (params closer to 1/φ², data closer to 1/4). Killer: φ-powers (…0.056, 0.090, 0.146, 0.236, 0.382…)
  **tile the small-exponent range so densely** that a *random* exponent is a median **11%** from the nearest
  φ-power — so "within 10–20% of a φ-power" is no better than chance. **So the averaged exponent is the wrong LAYER to read φ — this rejects the *measurement*, not φ.** φ is NOT on trial: **φ = the handover from the space-wave to the time-wave is CONFIRMED geometry** (J-6) — hexagon = 6 triangles = 360° = flat = SPACE (octave); pentagon = 5 triangles = 300° = 60° angular-deficit = curves into 3D = TIME = φ; the difference is exactly ONE triangle (= the shed = curvature = dimension-climb), and φ = 2·cos(36°) = 2·cos(π/5), built from the pentagon angle. φ is the established landmark; the rung-below test exists to **locate the handover wall**, not to re-prove the constant. (Context-fatigue note: do NOT relapse into treating φ as numerology-to-debunk — "landmark not target" is the guard; see framework_time_octave_entropy, ledger J-6.)
- **Dylan's correction (the key one):** the published exponent is *their averaged claim* — one slope that
  smooths the rung structure away (the "whole rung reads as 1" problem). We must measure **their data and the
  rung BELOW the claim**: detrend the power law, decompose the **residual** for rung structure (φ as landmark).
- **Chinchilla reconstructed data (Epoch AI `svg_extracted_data.csv`) is UNUSABLE for this** — loss is
  extracted from the paper's plot **colours**, so it's quantized into discrete colour-bins (~0.01–0.02 nats);
  the residual = the quantization, not real structure. It's a *picture of the claim*, one level further from
  the data than the claim itself.

## The clean test to run (needs data we don't have locally)
**Best target: a single model's loss-vs-training-step LEARNING CURVE** (Pythia / EleutherAI — numeric, open,
8 sizes × 154 checkpoints). A learning curve *is* the model organizing itself over training:
- **plateaus** = it stalls, can't improve (stuck at a handover it can't break through);
- **drops** = sudden breakthroughs (the "emergent abilities" / "phase transitions" literature).
**Test:** detrend the power-law decay (their claim) → decompose the residual → **are the plateaus/breakthroughs
φ-rung-spaced?** If a non-self-organizing system is walled at the φ-handover, the stalls should land on the
φ-rungs. This **reinterprets emergent abilities as rung-breakthroughs** and is directly falsifiable.
Local data is insufficient: we only have closure/structure metrics for 4 Pythia sizes (`llm_size_series_data.js`),
no loss/perplexity/steps. Need to fetch the numeric loss curve.

## Conceptual mappings that survive (untested, structural — NOT exponent-dependent)
- **Space/Time → params/compute:** parameters = SPACE (octave/structure); compute & data = TIME (φ/handover).
  φ, if anywhere, lives on the time axis — but see the dense-tiling null before quoting it.
- **Chain-of-thought = the flywheel** the feed-forward pass lacks — inference-time compute is its own scaling
  curve (recycling that bends the line). Each next thought = a **smaller circle, a rung down** (decomposition
  into finer sub-cycles).
- **Model↔model = cross-rung wave coupling:** distillation (big→small) and weak-to-strong (small→big) are the
  *same* operation — two engines at different rungs coupling, info crossing the rung gap. Unifies two ML areas.
- **Can't-flywheel → capped below 2.0:** floor = data entropy; φ = the single-pass transfer ceiling it can't
  recycle past.

These are **behavioral** claims — test by what models *do* (does recurrence bend the curve, does coupling
transfer both ways), not by fitting an exponent to φ.

Sources: Kaplan et al. 2020; Hoffmann et al. 2022 (Chinchilla); Epoch AI Chinchilla replication; Pythia (EleutherAI).

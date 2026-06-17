# Nodes are clocks, the coupling is the engine — Pythia ARA (clean run, 14 June 2026)


> # ⚠️ SCRATCHED — homebrew method, wrong (14 June 2026)
> ~~"Nodes are clocks (~1.0), the coupling is the engine (~1.5)."~~ Both readings are **measurement artifacts
> of a whole-signal averaging method** (it averages the coupled pair to the balance point — sea level — so a
> node reads ~1.0 and the asymmetry vanishes). Re-measured with the canonical **`ara_mapper.py`** (octave-rung
> decomposition + dominant-rung rise/fall ARA): **node ARA ≈ 1.23–1.29, edge ARA ≈ 1.25 — both engine-leaning,
> NOT clock, and NOT a node/edge split.** Do not use the clock/edge-split numbers below. See the corrected
> banner in `00_LLM_THREAD_SUMMARY.md`.


**Dylan La Franchi & Claude.** First *clean* measurement of where an LLM's internal oscillations sit on the
ARA scale, across training. Measures the framework's own architectural claim — **octaves build the units,
φ lives in the coupling** ("octaves build the tower, φ is the breathing gap") — directly in a transformer.

> **Method honesty.** An earlier run measured "connection-ARA" with a corrupted method (naked up/down count
> on a node's raw multi-system series — broke ARA decomposition Rules 1–3) and was **fully discarded**
> (nothing carried over). This run computes **no ARA on the GPU at all**: it captures the raw node
> oscillations (`llm_raw_node_series.npz`) + the ARA-independent closure/loose numbers
> (`llm_closure_RESULTS.csv`), and ARA is measured **offline, canonically** — strip the slower system
> (detrend), isolate each node's **ground cycle** (dominant period), phase-lock rising = accumulation,
> bounded 0–2 coordinate = 2·(accumulation fraction). Scripts: `llm_capture_raw_for_clean_ARA.py` (capture),
> `pythia_forced_clock_analysis.py` (curves). Pythia-70m/160m/410m-deduped, 13 log-spaced checkpoints, eager
> attention, transformers pinned 4.44.2.

## Results

**1. The nodes are clocks (ARA ≈ 1.0), and training *makes* them clocks.**
Random init sits mildly asymmetric (median ~1.3); by step ~512 every size collapses to a clean clock and stays
there: at the final checkpoint **82–96% of nodes are in the clock band (≈1.0), 0% at the φ engine band, 0%
snap**, all three sizes. Bounded 0–2, non-degenerate (410M spans 0.29–1.38), so it's not a floor — the init
proves the measure can move; training pulls it *to* clock. (This is the third independent sighting of the
forced-clock reading, after the fixed-compute breakthrough and the universal curve collapse — see
`LLM_PHI_FORCED_CLOCK_RESULT.md`.)

**2. The coupling between nodes runs hotter — engine-side — and it's not an artifact.**
The ARA of the co-activation on each strongly-coupled edge sits up at **~1.5 (between 3/2 and φ=1.618)**, far
above the clock nodes. Two nulls clear it:
- *Synthetic:* two correlated **clock** oscillators give a co-activation ARA of **1.005**, not 1.5 — the
  measure does not inflate there on its own.
- *Phase-scramble:* randomising phase **destroys the edges entirely** (0 survive) — the couplings require real
  phase structure, not just the spectrum.
So the asymmetry genuinely lives **on the coupling, not the units** — the framework's tower/gap architecture,
measured. At the best-resolved checkpoint (410M, hundreds–thousands of edges) ~**40% of edges sit in the actual
φ band**.

**Honest bounds.** The edge-ARA centers ~1.5–1.6 (straddling 3/2 and φ), **not pinned at φ**, and it **wanders**
across training (410M: 1.45 → 1.03 → 0.61 → 1.58); 160M ends at the **snap** pole (1.92), and 70M loses almost
all strong edges after early training. So "engine-side coupling" is a real, null-checked *direction* — not a
clean pinned constant. n=3 sizes, one prompt, branch-2a (co-activation); the lead-lag *handover* ARA (branch-2b)
is untested.

## Comparison to the neural scaling law (Kaplan/Chinchilla — the "line")
The scaling law sees one smooth descending line: lambada loss falls as a power law in compute (log-log slopes
−0.77 / −1.17 / −1.54 bits per e-fold for 70M/160M/410M). The framework reading is not a competitor — it's a
**different depth of the same object**: the scaling law measures the *surface* (loss falling); ARA measures the
*machine* underneath — **clock units, engine-side coupling**, with closure collapsing (~22,900 → 0.11 at step
1k) then rebuilding as capability switches on. Visual: `node_clock_edge_engine_viz.html`.


> **⚠️ SCRATCHED — DO NOT USE AS A RESULT (14 Jun 2026, Dylan caught it).**
> ~~"The neural scaling law, read in ARA, is a clock at ARA ≈ 1.08, identical across all 8 sizes."~~
> That number was computed by taking the ARA of the **already-processed lambada loss curve** (a benchmark
> summary — one scalar per checkpoint, collapsed over thousands of examples), i.e. **re-processing processed
> information, not measuring the units.** It is **parametrization-dependent**: the *same* curve reads
> **consumer (ARA ≈ 0.001) on linear-step time** and **clock (≈ 1.08) on log/rung time** — so "clock" was a
> choice of measurement axis, not a property of the system. Per-rung (octave doublings) it stays clock (1.125),
> not engine; an engine would need peak-learning at 81% of the rungs, it sits at 56%. Logged here only so a
> future reader does not mistake it for the answer. **The real, substrate-level results are the node/edge ARA
> below — measured *up from the raw unit oscillations*, not from a summary curve.**


## Open (next)
- **"Does the last cycle save itself?"** 410M's coupling sags toward collapse (0.61 at step 63k) then pulls back
  toward the φ-engine (1.58 at 143k) — a possible late self-correction toward the φ attractor. But 160M instead
  ends at snap, and it's noisy. Test: dense end-of-training sweep on the **bigger** sizes (more coupling to hold
  structure) — `llm_dense_end_sweep.py` (1B/1.4B, end-weighted checkpoints).
- **Branch-2b:** lead-lag *handover* ARA (more literal "φ in the coupling"; may sit nearer 1.618 than 3/2).
- **2-into-φ closure rate:** how much octave-2 node structure packs into the φ-coupling vs leaks as 0.382.
- **Two-AIs-train-each-other → engine?** Dylan's conjecture: mutual cross-coupling is the missing flywheel that
  could push a lone clock toward the φ engine (the shape of a lot of frontier training).

## Files
- `llm_capture_raw_for_clean_ARA.py` — clean capture (GPU/Colab). `llm_dense_end_sweep.py` — bigger-size end sweep.
- `pythia_curves/llm_closure_RESULTS.csv`, `llm_raw_node_series.npz` — clean-run data.
- `node_clock_edge_engine_viz.html` — the two-panel visual (scaling-law line vs the ARA machine).
- Companion: `LLM_PHI_FORCED_CLOCK_RESULT.md`, `RESONANCE_IS_ALL_YOU_NEED_SKELETON.md`.

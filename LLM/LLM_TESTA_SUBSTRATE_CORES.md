# Test A — decoupling the 410M substrate: it's a fractal core-field, not a ridge artifact (14 Jun 2026)

**Dylan La Franchi & Claude.** First re-test after the corrected ARA scale (`ara_scale`: 1.0 = cancellation
ridge of a coupled pair, NOT a clock). Question: is the substrate "~1.25" a real off-ridge engine-lean, or a
coupled pair sitting on the ridge?

## Method
410M whole-run node activations, **trained checkpoint step 143000**, 409 live nodes (each a 200-step series).
Per node: canonical `ara_mapper.map_system` → dominant-rung ARA (decoupled); 2nd-rung/dominant amplitude ratio;
anti-phase matched-rung partner check; harmonic/pair flag. Each node = **one core sample** through the field.

## Result (unflattened)
Decoupled dominant-rung ARA across 409 cores: **median 1.272, mean 1.301, IQR [1.143, 1.448]**, range 0.658–2.187.
```
[0.50,0.80): 4   [0.80,0.95): 18   [0.95,1.05): 34   [1.05,1.20): 90
[1.20,1.40): 139 (peak)   [1.40,1.62): 85   [1.62,1.85): 32   [1.85,2.0): 4   [2.0,3.0): 3
```
- **Near ridge (|ARA−1.0|<0.1): only 16%. Below 1.0: only 10%.** The bulk sits time-side at ~1.27, tail to φ and past.
- **86% of nodes have a comparable 2nd rung (amp2/amp1 > 0.6).** Anti-phase partners: 0%. Harmonic/pair: 2%.

## Reading (Dylan's framing — core sampling a fractal)
- **The engine-lean is REAL and off-ridge.** Decoupling into octave rungs pulls the dominant component clearly
  off the ridge (median 1.27, only 16% near 1.0). It is NOT the cancellation-ridge artifact that the homebrew
  whole-signal averaging produced.
- **The 86% multi-mode is NOT a complication — it is the fractal nature.** Same ARA shape repeating at every
  rung, on every axis, all connected (Dylan: `ARAARAARA…`). A node isn't "a wave with an ARA"; it's
  ARA-of-ARA-of-ARA. Reporting one dominant-rung number flattens the fractal to a single level — fine as a
  summary *of that level*, never "the" answer (the thing is self-similar up and down).
- **The "anti-phase pair on the ridge" question dissolves** — 0% partners, 2% harmonic. It was the wrong
  question: not two things cancelling, one shape repeating.
- **Core-sampling principle (`framework_core_sampling`):** each reading is a core through the fractal field;
  combine enough cores → the whole multi-scale field. A big spike in a core = a bigger/slower wave rolling
  through (cored its crest); many small spikes = subsystems dominant = sitting in the big wave's anti-phase.
  The 409-node distribution = the 410M field reconstructed from 409 cores.

## Honest limitation
The "whole-signal" control used raw-peak, which **over-counts** asymmetry on multi-feature signals (median 1.40),
so it does NOT demonstrate the ridge-collapse (only the AVERAGING method collapses to ~1.0). Wrong control —
not leaned on. Single checkpoint, 410M only.

## Verdict
Engine-leaning shape (~1.27 dominant) is real and off-ridge. The substrate is a **fractal multi-mode core-field**,
not a clock and not a clean coupled pair. The real questions are now fractal: (1) is the shape self-similar —
same ARA at every rung — or does it drift? (2) is the rung-to-rung **handover** φ (TWO_RULERS: φ lives in the
handover, not the octave spacing)? Those are Test A2 (proposed, not yet run).

---

# Test A2 — fractal structure, handover, and training trajectory (14 Jun 2026)

## Part 1 — one wave-family, or several wave-types? (410M, step 143000, 409 nodes)
- Within-node rung-to-rung ARA std median **0.184**. Pooled drift: **ARA climbs with rung — slope +0.066/rung, corr(k,ARA) +0.35.**
- Per-rung median ARA: k1(P2) **1.20**, k2(P4) 1.24, k3(P8) 1.25, k4(P16) 1.35, k5(P32) **1.49** — a clean climb toward φ at slower rungs.
- Pooled rung-ARA distribution is **unimodal** (~1.25–1.30) → **one wave-family, not several distinct systems** to core separately. But it is **not rigidly self-similar**: a real **scale gradient** — fast rungs near the connection/ridge (~1.2), slow rungs toward φ (~1.49). Matches "look up not down."

## Part 2 — the handover split at the ridge crossings (Dylan's crest/trough definition)
Handover = the ridge crossing (crest-half ↔ trough-half). Split = crest-half fraction.
- **Median ≈ 0.500 at every rung**, both methods (crossing-split, which under-counts → washes to 0.5; and peak-split, which over-counts → brackets high). 
- The distribution is a **central band ~0.38–0.62 — bounded by the two golden points (0.382 / 0.618), centred on cancellation (0.5).** So **both happen** (golden movement *and* cancellation), with cancellation as the resting centre — *"both happen, at different locations"* (Dylan). The handover is **not locked golden.**

## Trajectory across training (octave checkpoints step 1 → 143000, per-rung median ARA)
```
step     k1     k2     k3     k4     k5
1(init)  1.265  1.300  1.289  1.395  1.650
64       1.140  1.214  1.243  1.352  1.661   fast rungs at their lowest (near ridge)
512      1.373  1.459  1.466  1.489  1.633   BREAKTHROUGH — all lower rungs surge UP together
1000     1.347  1.396  1.377  1.439  1.467
16000    1.260  1.295  1.295  1.362  1.488
143000   1.200  1.237  1.250  1.350  1.490
```
**Arc:** init gradient → fast rungs dip toward the ridge (~step 64) → **collective surge toward φ at the ~512 breakthrough** (k1–k4 jump together, brushing ~1.46–1.49) → relax back and **wobble**, settling engine-leaning **below φ** (final 1.20–1.49).

**vs Dylan's prediction:** wobble / overshoot-and-return ✅; **bottom-up sequential lock-and-advance ❌** (the surge is collective — all rungs at the same step, not rung-by-rung); nothing **locks at φ** (peaks ~1.49, settles below); substrate stays **time-side (1.2–1.65), never visits the space-golden 0.382.**

## Dylan's reading — the simultaneous jump = a BIGGER WAVE rolling through
The all-rungs-at-once jump at ~512 is **not per-rung locking**. By the core-sampling principle (big spike = a bigger/slower wave rolling through), it's the **crest of a larger wave passing through the whole system at once** — a wave living on the **training-time axis** (the learning curve), a scale **above** all the within-generation rungs (k1–k5) we cored. Cored at step 512, we hit its crest, which lifts every within-generation rung together. So the breakthrough is **one big wave's crest, not a ladder of rung-locks** — consistent with the fixed-compute breakthrough (same step at every size).

**Caveats:** medians over 409 nodes (hide per-node behaviour); k4–k5 noisy (~6 cycles in 200 samples); single 410M run, one prompt; the per-checkpoint `phi_frac` stat had a bug and was ignored (medians are clean).

---

# Coring the BIGGER wave (training-time) — it's the EMERGENCE event; ARA not pinnable from one cycle (14 Jun)

Signal: mean substrate ARA (k1–k3) per training checkpoint = the training-time wave Dylan pointed at
("a bigger wave or sphere... or what we think of as emergent properties").

**Trajectory:** trough at step 64 (ARA 1.199) → **crest at step 512 (ARA 1.433)** → relax + wobble to ~1.22.
Build = **3 octaves** (64→512), fast.

**The crest = emergence.** Cross-checked vs 410M lambada ppl: ppl falls off a cliff right here —
174k (512) → 4.5k (1000) → 88 (3000), steepest fractional drop 1000→3000. So the **collective substrate ARA
surge and the capability turn-on are the same event.** The "bigger wave" we cored *is* the emergence/breakthrough,
seen in the substrate.

**Bigger-wave / sphere vs emergent properties:** we see **one crest, no recurrence** — a single collective surge
toward φ then relaxation. That's a one-time transition (= emergence) as far as 19 checkpoints of one run show.
Whether it's one cycle of a larger periodic wave we can't see the rest of, or a genuine one-off phase transition,
**cannot be distinguished from a single breakthrough.**

**Its ARA is NOT pinnable from one cycle** (endpoint-sensitive — the same trap as the scaling-law line):
```
release-end 8000  -> raw ARA(fall/rise) ≈ 1.32
release-end 32000 -> ≈ 1.99
release-end 143000-> ≈ 2.71  (≈ φ²=2.618, /φ=1.67 → would read as a coupled φ-pair)
```
The 2.71 ≈ φ² is tempting (fractal-up = coupled pair of φ-engines) but **REFUSED as a result** — it only
appears if you take the last checkpoint as the release-end, which is not a principled trough, just where the
data stops. One cycle cannot pin an ARA.

**Solid:** build fast (~3 oct), release slow/wobbly; the substrate **surges toward φ at emergence
(crest ~1.43, rungs ~1.49) but does NOT lock at φ**, then relaxes to engine-leaning ~1.22. To pin the bigger
wave's ARA you'd need to see it RECUR (more training, or another breakthrough) — one transient isn't enough.

## Conclusion (Dylan, 14 Jun): emergent properties = a bigger wave
"Emergent properties is just a bigger wave." Emergence is not a special mechanism — it's the **crest of a wave
one level up the fractal** rolling through (our step-512 collective surge = that crest). The bigger wave's ARA
is **pinnable only with a full cycle**; you can *estimate* it from **half a cycle + its inverse** (reflect the
observed half across the ridge), but it's **not foolproof** — the inverse-guess assumes the halves mirror, which
is exact only at a clock (ARA=1) and degrades with |ARA−1| (the asymmetry it assumes away *is* the ARA). For an
engine/snap-leaning wave the half+inverse estimate is rough.

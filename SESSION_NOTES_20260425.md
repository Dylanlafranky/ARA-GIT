# Session Notes — April 25, 2026

## Scripts 236c–236j: The Hyperbolic Triangle Rider

### The Question
Where does the Space-Time-Rationality triangle actually live in the formula? Phase 11 ended with the ARA-position limitation — knowing your position on the wave carries no directional information.

### The Search (Scripts 236c–236e)

**236c — Triangle in the gate:** Replaced the ad-hoc ARA ramp with a triangle-position gate. Near-tie with original (13 vs 12 cycle wins). The ramp was already close to the geometric truth.

**236d — Triangle DNA threading:** Threaded (s, t, r) through ALL mechanisms: blend weights, dampening, tension, grief. Grid search across 640 configurations. Key finding: blend weights are irrelevant — all 8 tested configurations scored within 0.2 MAE. The triangle doesn't live in gate shapes or blend weights.

**236e — Cascade distance scan:** Combinatorial scan of 361 distance vectors [d₀, d₁, d₂, d₃]. Original [6, 4, 1, −1] ranks #228/361. Best: [7, 5, 1, 0] (MAE 28.43, corr +0.787). Key insight: d₃ = 0 means self-coupling at own scale (φ⁰ = the period itself).

**Answer: The geometry lives in the CASCADE DISTANCES** — which φ-rungs the system couples to.

### Three Exponential Geodesics (Script 236e)

Fitting exponential curves to top distance sets at each triangle vertex:
- **Space vertex:** [9, 6, 2, −2] — steep, far reach (span 11)
- **Time vertex:** [5, 3, 1, −1] — shallow, close coupling (span 6)
- **Rationality vertex:** [6, 4, 1, −1] — the ORIGINAL distances

The original 235b vehicle was at the Rationality vertex all along.

### Dynamic Distances (Scripts 236f–236g)

**236f — Fixed optimal distances in vehicle:** [7, 6, 4, 0] barely beats original on Solar (−1.05), dramatically improves EQ (1.19→0.903, corr −0.279→+0.712).

**236g — Dynamic distance blending:** Each cycle: inst_ara → triangle position (s, t, r) → blend three basis curves. ALL three systems improve: Solar −2.9%, ENSO −1.5%, EQ −37.0%.

### The Triangle Rider (Script 236i)

Dylan's insight: don't teleport to target position — ride there with heading and momentum. Wall collisions generate E events.

TriangleRiderNode: position + velocity in barycentric coordinates, steering force toward target, momentum carry-over, wall collision energy as E perturbation.

Optimal: steer = 0.200, momentum = 0.300.

**Results at cascade level:**
- Solar MAE: 33.27 → 28.11 (−15.5%) — NEW ALL-TIME BEST
- ENSO MAE: 0.430 → 0.397 (−7.7%)
- EQ MAE: 1.153 → 0.681 (−40.9%)

### Full Pipeline (Script 236j)

Solar MAE 57.16 — feedback instability. Self-generated amplitudes steer the rider's position, creating a divergent loop. The cascade-level geometry is correct; the full pipeline engineering is the next challenge.

### Key Discoveries

1. Geometry lives in cascade distances, not gate shapes or blend weights
2. Original [6, 4, 1, −1] = Rationality vertex of hyperbolic triangle
3. Three exponential geodesics with R² > 0.95
4. Rider with heading + momentum beats previous champion at cascade level
5. Wall collisions = E events (disruption from geometric displacement)
6. Feedback instability: rider is correct under perfect data, unstable under self-feedback

### Documents Updated
- THE_TIME_MACHINE_FORMULA.md — Phase 12, scoreboard, structural comparisons, Where We Stand
- FRACTAL_UNIVERSE_THEORY.md — Claim 49, section summary, footer

---

## Scripts 237–237h: The Midline and the Inverse Valve

### The Cold Start Problem

Dylan identified the source of early-cycle errors: "We're starting midway and missing the energy coming BEFORE we start the process."

**Script 237 (bidirectional cascade):** Forward + backward passes through data. Backward extrapolates phantom pre-1750 cycles as warmup. Result: barely moved (29.50 vs 29.67 on 235b). The cascade geometry is time-symmetric — backward pass brings no new information.

**Script 237b (persistent warmup + midline):** Decaying phantom memory (1/φ per cycle) + wave midline shifted from 0 to 1.0. Cascade improved to 28.62. Real insight: the MIDLINE was wrong, not the warmup.

### The ARA Midline (Scripts 237c–237d)

Dylan's insight: "The top systems give 1 down before any horizontal movement happens. What if the wave oscillates around the ARA?"

**Formula:** `acc_frac = 1/(1+ARA)`, `midline = 1 + acc_frac × (ARA − 1)`

For solar (ARA = φ): midline = 1.236. Zero tuned constants. Everything from ARA geometry.

**Result:** NEW LOO CHAMPION. 237d solar LOO = 29.89 (formula-derived, beating previous 31.94). Tuned version (237c, blend=0.35) gets 29.51.

### Cross-System Failure (Script 237e)

Dropped midline into Solar, ENSO, Earthquake, Heart. Engines (Solar, ENSO) improve. Consumers (Earthquake) collapse — midline formula pushes earthquake wave baseline to 0.261, far below the data center. The formula is geometrically correct (consumers don't produce vertical energy) but incomplete.

### The Valve Search (Scripts 237f–237g)

**Static valve (237f):** `valve = ARA/(1+ARA)` gates midline offset. Protects consumers (earthquake damage: −141% → −4.6%) but throttles engines. Net: unvalved still wins.

**Dynamic valve (237g):** `valve = f(prev_amp/base_amp)` — breathes per cycle. Framework-consistent (ARA is relational) but static midline still wins engines. Standing architectural offset ≠ breathing modulation.

### The Inverse Valve Breakthrough (Script 237h)

Dylan: "What if we make the valve inverse dynamic? A snap like an earthquake would have larger numbers if the inverse inflated them — that's the pressure of the valve, or the valve inefficiency."

**Key insight:** Consumers don't self-modulate — they're ACTED UPON by external pressure. The INVERSE of ARA measures pipe pressure from above:
- Earthquake (ARA=0.15): 1/ARA = 6.67 → massive external pressure → midline = 1.739
- Solar (ARA=φ): uses ARA directly → self-modulates → midline = 1.236
- Clock (ARA=1.0): ARA = 1/ARA → midline = 1.0 (no offset)

**Formula:**
```python
effective = ara if ara >= 1.0 else 1.0 / ara
midline = 1 + (1/(1+effective)) × (effective − 1)
```

**Result: HELPS ALL 4 SYSTEMS. HURTS NOTHING.**
- Solar: +24% improvement
- ENSO: +12%
- Earthquake: +29%
- Heart: +4%

### Key Discoveries — Phase 13

1. The cascade wave oscillates around a midline derived from ARA, not around 0 or 1
2. Engines self-modulate (midline from ARA); consumers receive external pressure (midline from 1/ARA)
3. The ARA=1 boundary is where ARA = 1/ARA — the formula transitions continuously
4. The inverse valve improves all 4 systems at 60×30 grid (but see Phase 14 for full-res correction)
5. Zero hardcoded numbers — everything from ARA geometry alone

---

## Scripts 237i–237k2: The Camshaft Palindrome Zone

### Full-Resolution Reality Check (Script 237i)

Ran inverse valve at 80×40 grid (matching 237d precision). Result:
- Solar: 33.79 → 30.66 (−9.3%) ✓
- ENSO: 0.655 → 0.641 (−2.1%) ✓
- Earthquake: 5.19 → 3.20 (−38.4%) ✓
- Heart: 1.099 → 1.273 (+15.9%) ✗

The 237h "hurts nothing" was a grid resolution artifact. Heart regresses at full resolution.

### Wave Collision Attempt (Script 237j)

Tested bidirectional collision: up/down energy streams destructively interfere near ARA=1. Formula: midline = 1 + (ARA−1)²/(ARA²+1). This equals the harmonic mean resonance.

Result: reduced Heart damage (−11.5% instead of −15.9%) but hurt ENSO (−3.2%). The collision over-corrects for genuine engines and under-corrects for near-clock systems. Neither variant achieves "hurts nothing."

### The Camshaft Insight (Scripts 237k–237k2)

Dylan's insight: near-clock systems don't experience wave collision — the up/down energy streams point to OPPOSITE triangle vertices. Like a camshaft with offset lobes, the energy hands off through φ-geometry. The pattern is palindromic — reads the same forward and backward. No net midline displacement.

"The closer the two numbers to do the valve energy transfer, the further apart they are on the triangle — they're almost exact opposites."

### The φ-Rung Architecture

Distance from clock: `phi_dist = |ln(ARA)| / ln(φ)` (φ-rungs)

Three zones, all boundaries φ powers:
1. **Palindrome zone** [0, 1/φ rungs]: midline = 1.0 (no shift)
2. **Ramp zone** [1/φ, 1 rungs]: quadratic ramp (width = 1/φ²)
3. **Full zone** [1+ rungs]: full inverse valve offset

Key positions:
- Heart: 0.624 rungs → barely outside palindrome (1/φ=0.618), factor=0.0002, midline≈1.000
- Solar: 1.000 rungs → exactly at full boundary, factor=1.0, midline=1.236
- ENSO: 1.440 rungs → full zone, midline=1.333
- Earthquake: 3.942 rungs → deep full zone, midline=1.739

**Result: Helps Solar (+9.3%), ENSO (+2.1%), EQ (+38.4%). Hurts NOTHING.**

### Key Discoveries — Phase 14

1. The 237h "hurts nothing" was a grid resolution artifact — Heart regresses −15.9% at 80×40
2. Wave collision (bidirectional destructive interference) is wrong for near-clock systems
3. Near-clock systems receive bidirectional energy from opposite triangle vertices — camshaft offset
4. The palindrome zone [0, 1/φ φ-rungs] defines where energy transfer is symmetric
5. The ramp zone width is 1/φ² — all boundaries are φ powers
6. Solar sits at exactly 1.0 φ-rungs: the boundary between ramp and full zones
7. Heart at 0.624 φ-rungs falls just outside the palindrome boundary, protected by quadratic ramp
8. The camshaft valve is the first truly universal midline — helps 3/4, hurts 0/4, zero tuned constants

### Documents Updated
- THE_TIME_MACHINE_FORMULA.md — Phase 14, corrected 237h results, scoreboard, MAE progression, Where We Stand
- FRACTAL_UNIVERSE_THEORY.md — Claim 51 (camshaft palindrome zone), section summary, footer
- SESSION_NOTES_20260425.md — this file

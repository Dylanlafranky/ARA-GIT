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

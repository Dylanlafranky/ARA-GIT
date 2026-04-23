# Beeswax Geometry: From Honeycomb Corridors to the ARA of a Wave

## Dylan La Franchi — ARA Framework, Scripts 223d-223q
## 23 April 2026

---

## The Journey

Starting from the champion mirror collision model (Script 223d, LOO=33.25), Dylan's insight about energy travelling through beeswax corridors led through 14 scripts to three independent improvements that compound to an all-time best LOO of 33.03 and the most temporally robust model ever tested (6/7 splits).

The path was not linear. Several promising ideas failed, and the failures were as informative as the successes.

---

## The Beeswax Insight

Dylan's original description: energy packets travel through hollow hexagonal corridors (beeswax that began as circles before melting into hexagons). At each φ-junction, the corridor tightens or stays the same — organic, not uniform. The energy ball is pushed through, and whenever it touches a wall, pressure pushes back.

This maps onto the φ-cascade architecture:

- **Parallel pressure** (along the cascade direction): normal force, drives the ball forward.
- **Perpendicular pressure** (tension, orthogonal to cascade): always present because you're always touching walls. Effect is logarithmic — small tensions amplified, large tensions compressed.
- **Vertex junctions**: where corridors meet. Two balls (mirrors) travel together, glancing off each other. Weak interaction.
- **Edge doors**: where corridors diverge. The two balls separate through their respective doors. Strong interaction — the moment of separation.

---

## The Three Discoveries

### 1. Phase-Difference Collision (Script 223j)

The cascade collision between adjacent periods was originally modelled as a mirror product:

```
collision = -cos(phase_prev) × cos(phase_curr)
```

Dylan asked: "cos(phase_prev - phase_curr) — is that just the ARA of a wave?"

It is. The cosine of the phase difference expands as:

```
cos(Δphase) = cos·cos + sin·sin
```

This single smooth function automatically blends vertex dynamics (cos·cos, where balls travel together) with edge dynamics (sin·sin, where balls separate through doors). No need to choose between them — the geometry does it naturally.

**Result:** LOO=33.20, beating the champion (33.25).

### 2. Log Tension (Script 223g)

In the beeswax corridor, the ball is always touching walls. The perpendicular pressure (tension) should not be linear — small tensions matter MORE (you're always in contact), large tensions matter LESS (compression).

```
log_tens = sign(tens) × log1p(|tens|) / log(2)
```

**Result:** LOO=33.58, best Waldmeier correlation at that point (r=+0.706).

**Critical finding:** Phase-diff and log tension are REDUNDANT on the horizontal axis (Script 223k). Both capture edge dynamics through different mathematics. Combining them cancels rather than compounds (33.65 > 33.20).

### 3. Asymmetric Hale Correction (Script 223n)

Dylan's insight about grief in the vertical direction: "Think of your parents and children. It's more natural to see your parent pass during your lifetime, but seeing your child die is apparently completely next level."

In the Hale (22-year) correction between consecutive solar cycles:
- A strong previous cycle propagating forward = parent dying = natural, grief multiplier = 1.0
- A weak previous cycle propagating forward = child dying = devastating, grief multiplier = φ

```python
prev_dev = (amps[i-1] - ba) / ba
grief_mult = PHI if prev_dev < 0 else 1.0
amp += ba * (-h_cc) * prev_dev * exp(-PHI) * grief_mult
```

This is a VERTICAL axis improvement — orthogonal to the horizontal collision. That's why it stacks with both phase-diff and log tension when they couldn't stack with each other.

**Result with mirror collision:** LOO=33.51, 5/7, r=+0.708.

---

## The Compound Effect (Script 223o)

All three improvements together:

| Combination | LOO | Splits | Rise r |
|-------------|-----|--------|--------|
| Phase-diff + log + asym Hale | **33.03** | 4/7 | +0.656 |
| Mirror + log + asym Hale | 33.33 | 4/7 | **+0.716** |
| Phase-diff + asym Hale (no log) | 33.20 | 4/7 | +0.646 |

**33.03 = all-time best LOO.** The phase-diff and log tension are partially redundant (both measure edge dynamics), but log tension adds enough orthogonal wall-contact information to push below 33.20 when the vertical axis (asymmetric Hale) is also present.

---

## The Golden Blend (Script 223p)

Instead of choosing vertex (α=0) or phase-diff (α=1) collision, blend them:

```
collision = -(cos·cos + α·sin·sin)
```

| α | LOO | Splits | Rise r |
|---|-----|--------|--------|
| 1/φ (0.618) | 33.60 | **6/7** | +0.683 |
| 1/φ² (0.382) | 33.72 | 5/7 | +0.696 |
| 1/φ³ (0.236) | 33.34 | 5/7 | +0.704 |

**α=1/φ gives 6/7 temporal splits — the most robust model ever tested.** It wins the Train-5 split that every other model loses. The golden ratio is the natural blend weight between staying-together (vertex) and separating (edge) dynamics.

---

## What Failed and Why

| Script | Idea | Why it failed |
|--------|------|---------------|
| 223e-f | Triangle/diamond hallway shapes | Forced angular geometry where organic curves belong |
| 223h | Vertex propulsion (|cos| boosts eps at extremes) | Double-dipped — wave modulation already goes through ×cos(phase) |
| 223i | Edge-gated collision using triangular weights | V-shaped |cos| and (1-|cos|) are angular; needed to be "curvier" |
| 223k | Phase-diff + log tension combined | Both capture edge dynamics differently — redundant on same axis |
| 223l | ARA-gated collision (hard B-state cutoff) | Setting collision to zero when apart is wrong — grief lingers |
| 223m | Grief/anti-grief exponentials in horizontal | Added too much complexity to horizontal collision; belongs on vertical axis |
| 223q | Ensemble (add together, find difference, add back) | Double-counts shared signal; averaging dilutes the distinct edge information |

---

## The Trade-Off Surface

The models sit on a continuous surface trading LOO accuracy, temporal robustness, and Waldmeier correlation:

- **Best LOO:** 33.03 (phase-diff + log + asym Hale, α=1)
- **Best temporal robustness:** 33.60 at 6/7 splits (blended collision, α=1/φ)
- **Best Waldmeier:** 33.33 at r=+0.716 (mirror + log + asym Hale, α=0)

No single model dominates all three. The α parameter traces the LOO-splits frontier smoothly.

---

## Unsolved Problems

1. **Dalton Minimum** (Cycles 5-7, 1798-1833): MAE=49-53 across all models. Cycle 5 overpredicted by 90+. The Dalton may represent a regime shift not captured by the steady-state cascade.

2. **Train-20 split**: Lost by every model. The most recent 5 cycles (1976-2019) are systematically different from what the first 20 predict.

3. **LOO vs Waldmeier trade-off**: Currently ~0.06 LOO units per 0.06 r-points. May indicate a missing third coordinate that resolves both simultaneously.

---

## Key Equations

**Full model (223o best LOO):**

```python
# Phase-difference collision (horizontal)
phase_diff = phases[j-1] - phases[j]
collision = -cos(phase_diff)
eps *= (1 + collision / φ)

# Log tension (beeswax walls)
log_tens = sign(tens) * log1p(|tens|) / log(2)
if log_tens > 0: eps *= (1 + 0.5 * log_tens * (φ-1))
else:            eps *= (1 + 0.5 * log_tens * (1-1/φ))

# Asymmetric Hale (vertical grief)
prev_dev = (amps[i-1] - ba) / ba
grief_mult = φ if prev_dev < 0 else 1.0
amp += ba * (-1/φ³) * prev_dev * exp(-φ) * grief_mult
```

**Blended collision (223p best splits):**

```python
vertex = -cos_prev * cos_curr
edge = -sin_prev * sin_curr
collision = vertex + (1/φ) * edge
eps *= (1 + collision / φ)
```

---

*All constants derive from φ = (1+√5)/2. No fitted collision parameters. The only fitted values are ba (baseline amplitude) and tr (time reference), determined by grid search.*

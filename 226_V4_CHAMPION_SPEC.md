# ARA Bridge v4 — Champion Model Specification

**Date:** April 24, 2026
**Script:** 226_ara_bridge.py (v4 variant)
**Status:** Current champion — LOO MAE = 31.94, 6/7 temporal splits

---

## Performance

| Metric | Value |
|--------|-------|
| LOO MAE | 31.94 SSN |
| LOO vs sine | -34.5% |
| LOO correlation | +0.649 |
| Temporal splits won | 6/7 |
| Fit MAE (full record) | 31.26 SSN |
| Free parameters | 2 (base_amp, t_ref) |

**Previous champion:** 223o (LOO=33.03, 4/7 splits)

---

## Architecture

### Cascade Periods (φ-derived)

All periods are powers of φ scaled by the dominant period P = φ⁵ = 11.09yr:

| Level | Formula | Period (yr) | Role |
|-------|---------|-------------|------|
| 1 | P × φ⁶ = φ¹¹ | 199.0 | De Vries |
| 2 | P × φ⁴ = φ⁹ | 76.0 | Gleissberg |
| 3 | P × φ = φ⁶ | 17.9 | Above-Schwabe |
| 4 | P / φ = φ⁴ | 6.9 | Sub-Schwabe |

Schwabe = φ⁵ = 11.09yr (dominant period)
Gleissberg = φ⁹ = 76.01yr (gate modulator)

### Constants (all φ-derived, zero free parameters)

| Constant | Value | Derivation | Role |
|----------|-------|------------|------|
| eps base | 1/φ⁴ = 0.1459 | Cascade coupling weight | Modulation strength |
| collision weight | 1/φ = 0.6180 | Phase-diff collision scaling | Inter-level interaction |
| Gleissberg residual | 1/φ⁹ = 0.01316 | Additive Gleissberg correction | Long-period residual |
| Schwabe pulse | 1/φ³ = 0.2361 | Pulse weight | Intra-cycle asymmetry |
| Pulse decay | φ = 1.618 | Exponential decay rate | Pulse shape |
| Hale coupling | 1/φ³ = 0.2361 | Asymmetric Hale weight | Cycle-to-cycle memory |
| Hale decay | exp(-φ) = 0.1986 | Memory decay factor | How fast memory fades |
| Grief multiplier | φ = 1.618 | Weak-prev amplification | Asymmetric Hale response |
| Tension+ | 0.5 × (φ-1) = 0.309 | Positive tension scaling | Rising phase amplification |
| Tension- | 0.5 × (1-1/φ) = 0.191 | Negative tension scaling | Falling phase compression |
| Initial acc_frac | φ/(φ+1) = 0.618 | Gate starting position | First-cycle gate |

### Components (in evaluation order)

**1. Adaptive Gate (Sawtooth Valve)**
- Phase source: Gleissberg (φ⁹ = 76yr)
- Shape: rises to φ during accumulation, falls to 1/φ during release
- Normalized by (φ + 1/φ) / 2
- acc_frac: adaptive from previous cycle amplitude (inst_ARA = prev_amp / base_amp)
- First cycle uses φ/(φ+1)

**2. Selective Wobble**
- Only for constrained systems (ARA < 1)
- Solar (ARA = 1.73): wobble = 0 (engines run free)
- Amplitude scales with distance below ARA = 1.0

**3. Phase-Difference Collision**
- Between adjacent cascade levels: collision_j = -cos(phase_{j-1} - phase_j)
- Scales eps by (1 + collision × 1/φ)
- First level (j=0) has no collision

**4. ARA-Scaled Tension**
- Engines (ARA ≥ 1): standard tension — sin(phase) with φ-asymmetric scaling
- Consumers (ARA < 1): log tension — log1p(|sin|)/log(2) with same scaling
- Solar uses standard tension (ARA = 1.73)

**5. Multiplicative Cascade**
- amp = base_amp × Π(1 + eps_j × cos(phase_j)) for j = 0..3

**6. Gleissberg Residual (additive)**
- amp += base_amp × 1/φ⁹ × cos(gleissberg_phase)

**7. Schwabe Pulse (additive)**
- amp += base_amp × 1/φ³ × exp(-φ × cp) × cos(schwabe_phase)
- Exponential decay within each cycle (sharp start, fading)

**8. Asymmetric Hale (additive)**
- prev_dev = (prev_amp - base_amp) / base_amp
- grief_mult = φ if prev_dev < 0, else 1.0
- amp += base_amp × (-1/φ³) × prev_dev × exp(-φ) × grief_mult
- Weak previous cycle → amplified correction (grief)

### Grid Search

| Parameter | Range | Resolution |
|-----------|-------|------------|
| t_ref | [t_min - max(gleissberg, span), t_min + 2×schwabe] | 80 points |
| base_amp | [mean × 0.6, mean × 1.4] | 40 points |
| Total | 3,200 evaluations per fit | |

---

## Cycle 26 Prediction

**Registered:** April 24, 2026

| | Value |
|---|---|
| Peak amplitude | 206 SSN |
| Peak timing | ~2035.2 |
| 50% CI | [187, 226] SSN |
| 80% CI | [155, 267] SSN |
| Timing ±1σ | 2035.2 ± 0.4 yr |

Prediction uses C25 = 173.0 SSN as previous cycle for Hale correction.

---

## What This Model Does NOT Include

- De Vries vertical coupling (tested in 229 series, marginal improvement)
- Weierstrass amplitude weights (available but not used for solar)
- Log tension (only used for consumers, ARA < 1)
- Gate wobble (only used for constrained systems, ARA < 1)

---

## ENSO Cross-System Extension (Scripts 232–232g)

The v4 formula extends to ENSO (ARA=2.0, P=φ³≈4.24yr) with two amplitude mechanisms:

| Metric | Solar (ARA=1.73) | ENSO (ARA=2.0) |
|--------|-------------------|-----------------|
| LOO MAE | 31.94 SSN | 0.382 °C |
| vs sine | −34.5% | −32.2% |
| Correlation | +0.649 | +0.603 |
| Amplitude scaling | None needed | Log-Gleissberg + φ-log output |

**Key finding:** Solar's built-in Hale/grief mechanisms handle amplitude variation natively. ENSO (pure harmonic, ARA=2.0) needs singularity-distance memory because its symmetric ARA provides no asymmetric amplitude mechanism. The cascade's asymmetric components (grief multiplier, Hale decay) have nothing to grip when the system is perfectly symmetric.

The amplitude scaling uses log_φ(gap/period) where gap = time since last singularity event (ENSO ≥1.8°C). This is a 69% accurate proxy for event strength.

---

## Key Null Test Result (Script 230)

φ-ratio cascade spacing ranks **1st of 4 tested ratios** when all φ-derived constants are held fixed and only period spacing varies. The architecture is somewhat ratio-agnostic (other ratios beat sine), but φ-spacing is optimal. φ⁵ = 11.09yr uniquely matches the observed solar cycle period.

# Breathing vs φ — proper multi-subject test

**2026-06-21.** Re-tests the "resting breath exhale/inhale ratio = φ" claim, which had only a single
5-min demo recording behind it. ARA convention: inhale = accumulation (build), exhale = release, so
ARA = T_exhale / T_inhale.

## Data
PhysioNet **Fantasia** — 20 healthy subjects (10 young ~21-34 yr, 10 elderly ~68-85 yr), continuous
respiration belt at 250 Hz, supine rest. First 10 min per subject. Per subject: detect inhale peaks
and exhale troughs, time the rising (inhale) and falling (exhale) segments, take the per-subject median
ratio, aggregate across subjects.

## Result — breathing is an asymmetric engine NEAR φ but measurably BELOW it

| method | group median ex/in | 95% CI | φ in CI? | within 10% of φ |
|---|---:|---|---|---|
| light smooth 0.30 s | 1.418 | [1.351, 1.543] | no | 40% |
| light smooth 0.20 s | 1.465 | [1.398, 1.566] | no | 45% |
| light smooth 0.08 s | 1.471 | [1.396, 1.572] | no | 50% |
| **zero-phase bandpass** | **1.182** | — | no | 5% |

- **Robust value ≈ 1.42–1.47** (light/raw methods). φ = 1.618 is **outside the 95% CI** every way.
- Breathing **is** a genuine asymmetric engine (exhale reliably longer than inhale, ratio > 1 — NOT a
  clock), sitting in the φ neighborhood (~half of subjects within 10% of φ) but ~9–12% **below** φ.
- Elderly slightly higher than young (≈1.49 vs 1.46), both below φ.
- The single-recording "≈ φ" was optimistic; on n=20 it does not reach φ.

## Methodological confirmation (canonical rule)
The zero-phase bandpass gave **1.18** — it symmetrizes rise/fall and **under-counts asymmetry**, exactly
the documented "bandpass under-counts (solar 1.75→0.9)" failure. The canonical **raw/light-peak** method
(1.45) is the correct one. Lesson reproduced live: do not bandpass before measuring rise/fall asymmetry.

## Verdict
"Breathing = φ" is a **soft/partial result, not a clean hit**: a real asymmetric engine in the golden
zone, but quiet supine breathing lands ~1.45, below φ. Atlas node should read **~1.45 (engine,
φ-neighborhood), not 1.618**. OPEN: does breathing approach φ under other regimes (running/exercise →
expect toward 1.0 as exhale becomes active; slow/meditation breathing → may extend exhale toward/past φ)?
Tests pending. Script approach: Fantasia RESP → peak/trough → median T_ex/T_in → bootstrap CI.

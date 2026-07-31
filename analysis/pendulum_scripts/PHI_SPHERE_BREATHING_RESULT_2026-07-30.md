# Phi as a breathing sphere carried through time — T301 result

**Date:** 30 July 2026  
**Protocol:** `PHI_SPHERE_BREATHING_PROTOCOL_2026-07-30.md`  
**Public data:** dynamicslab *MultiArm-Pendulum*, Zenodo
`10.5281/zenodo.6633719`  
**Verdict:** **NOT SUPPORTED (`0/4`) for this measured state-sphere coordinate**  
**Independent validation:** **PASS**

## Answer first

Dylan's refined idea was:

> A circle or sphere can close locally while the complete identity advances
> through the next time slice. Phi may be the non-repeating orientation step
> between successive sphere “breaths.”

This is mathematically coherent, but the public pendulum records did not use
Phi on the tested coordinate.

For the coupled raw arm-angle vector,

\[
\underbrace{\mathbf q(t)}_{\substack{\text{measured coupled}\\\text{ARA cut}}}
\longrightarrow
\underbrace{r(t)=\|\mathbf q(t)\|}_{\substack{\text{radial accumulation}\\
\text{and release}}}
+
\underbrace{\widehat{\mathbf q}(t)}_{\substack{\text{orientation of}\\
\text{the breath}}}.
\]

Adjacent radial maxima were approximately opposite. Two maxima later, the
state returned almost to its previous orientation. The observed geometry was:

\[
\text{pole A}\rightarrow\text{pole B}\rightarrow\text{pole A},
\]

not

\[
\text{breath}_n
\xrightarrow{\;\phi^{-2}\text{ turn}\;}
\text{breath}_{n+1}.
\]

## Frozen empirical result

The primary endpoint measured the spherical angle between radial maximum
\(i\) and radial maximum \(i+2\). This skips the intervening opposite-side
maximum and compares one complete local breath with the next.

Median candidate distance was:

| Frozen cut | recurrence `0` | `3/8` | **Phi `0.381966`** | `2/5` |
|---|---:|---:|---:|---:|
| 2D double runs 2–3 | **`0.000366`** | `0.374634` | `0.381600` | `0.399634` |
| 3D triple run 2 | **`0.031118`** | `0.343882` | `0.350848` | `0.368882` |
| 2D confirmation run 4 | **`0.000145`** | `0.374855` | `0.381821` | `0.399855` |
| 3D confirmation run 3 | **`0.005193`** | `0.369807` | `0.376773` | `0.394807` |

Every development, frozen and confirmation record selected recurrence.

The lag-1 diagnostic supplied the other half of the geometry. In the frozen
2D records, adjacent radial maxima were only `0.002483` turns from exact
opposition. The frozen 3D record was `0.039699` turns from opposition.

Plainly: the sphere cut breathes from one side to the other and returns. It
does not rotate onward by a golden step at this grain.

## Identity-maintenance result

If Phi were the identity-preserving handover here, greater Phi proximity
should predict greater similarity between the two radial maxima.

Instead:

- recurrence proximity: pooled Spearman `+0.4276`;
- Phi proximity: pooled Spearman `−0.4270`;
- Phi one-sided circular-shift `p=0.9934`.

The almost equal-and-opposite correlations are not a second mysterious
constant. Most complete-breath steps lie near zero, so moving closer to zero
automatically moves farther from every candidate near `0.38–0.41`. The
supported finding is simply that better local recurrence accompanies better
radial retention.

## Sensitivity

The detector was rerun over:

- radial prominence `{2%, 5%, 10%}`; and
- minimum spacing `{0.15, 0.20, 0.30} × 1.333 s`.

All `9/9` double-run settings and all `9/9` triple-run settings selected
recurrence. The result is not a narrow detector-threshold accident.

## The controlled circle result

The empirical null does not make Dylan's geometric intuition empty. A
constant phase advance creates:

\[
\underbrace{
(\cos 2\pi n\alpha,\ \sin 2\pi n\alpha,\ n)
}_{\substack{\text{a circle advanced}\\\text{through time}}}.
\]

Every fixed \(\alpha\) creates a helix-like time extrusion. Rational steps
eventually revisit the same angular sites; irrational steps do not.

Across deterministic circle horizons `N=4…200`, the candidate win counts
were:

| Candidate | avoids recurrence | smallest largest gap | lowest discrepancy |
|---|---:|---:|---:|
| `pi−3` | 44 | 32 | 10 |
| `3−e` | 24 | 34 | 27 |
| `3/8` | 1 | 4 | 0 |
| **Phi `phi^-2`** | **59** | **67** | **85** |
| `2/5` | 1 | 2 | 1 |
| silver `sqrt(2)−1` | **68** | 57 | 73 |

Phi was the strongest candidate for finite-horizon coverage/discrepancy and
second for recurrence avoidance. The silver irrational beat it on the last
measure.

This establishes the precise mathematical refinement:

> Phi is an especially strong example of a non-closing circle stretched
> through time, but it is not the only member of that geometric family.

The benchmark supplied each candidate as the generator. It explains the
geometry; it is not empirical evidence that the pendulum or the universe
selected Phi.

## Relation to the earlier Hexagon–Pentagon test

The earlier EnergyRatio hypothesis treated `60°→72°` as a local lock-angle
dial. Strong-lock systems did not climb monotonically through that band, so
the universal dial was not supported.

T301 asked a different question. It did not search for `72°`. It directly
measured the orientation advance of successive raw radial breaths and made
Phi beat nearby rational and irrational controls. The result was still
negative because recurrence won by a very large margin.

The two negative results therefore agree without being duplicates:

- Hexagon–Pentagon: no universal `60°→72°` local lock-angle dial;
- T301: no `0.381966` complete-breath advance on this pendulum state-sphere.

## Current Phi evidence map

| Proposed Phi location | Current result |
|---|---|
| literal resting inhale/exhale duty ratio | asymmetric, about `1.42–1.47`, measurably below Phi |
| Hexagon–Pentagon local lock-angle dial | not supported |
| quantum directional passage-time handover (Q43) | not supported |
| one child turning inside a parent (T297) | poles/opposition, not Phi |
| collective four-child completion/retention (T298) | mixed; Phi-adjacent but not unique or stable |
| local four-child recurrence (T300) | quarters plus near-zero recurrence, not Phi |
| complete radial state-sphere breath (T301) | opposition then recurrence, not Phi |
| controlled non-repeating circle generator | Phi is very strong, but not unique |
| external common-mode carrier of a complete local identity | **still untested** |

The only current empirical opening is narrow: T298 found a fragile Phi-adjacent
collective transition. The broad claim that every local breath uses Phi is
not supported.

## What remains open

The fixed pendulum pivot does not measure the external motion of the complete
apparatus through a larger frame. T301 therefore cannot test the more literal
Solar-System/Galaxy analogy:

\[
\text{local rotation}
\rightarrow
\text{local orbit}
\rightarrow
\text{whole-system carrier}.
\]

A proper carrier test requires simultaneous measurements of all three
coordinates. The prediction must be frozen on the carrier relation before
opening the final data. The current result must not be repaired by relabelling
its near-zero local recurrence as an unseen Phi carrier.

## Validation and reproduction

Independent validation re-read all `2,595` saved events and reproduced:

- every event count;
- every candidate distance and retention value;
- all group medians and six recurrence winners;
- three raw state-vector spherical-angle spot checks; and
- every non-empty artifact.

Validation status: **PASS**.

Run from `analysis/pendulum_scripts`:

```powershell
& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' `
  '.\phi_sphere_breathing_test.py'

& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' `
  '.\validate_phi_sphere_breathing.py'
```

Artifacts:

- `PHI_SPHERE_BREATHING_PROTOCOL_2026-07-30.md`;
- `phi_sphere_breathing_test.py`;
- `phi_sphere_breathing_results.json`;
- `phi_sphere_breathing_events.csv`;
- `PHI_SPHERE_BREATHING_DIAGNOSTICS.png`;
- `validate_phi_sphere_breathing.py`;
- `phi_sphere_breathing_validation.json`.

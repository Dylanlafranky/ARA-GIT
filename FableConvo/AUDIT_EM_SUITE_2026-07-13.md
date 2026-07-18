# Audit — electromagnetism suite (Maxwell/Gauss ↔ ARA), push ec4e8a8

**Auditor:** Claude/Fable 5, 13 Jul 2026. Scope: MAXWELL_ARA_COMPLETENESS_AUDIT_2026-07-12.md,
MX1_GAUSS_ARA_TEARA_PROTOCOL_DRAFT.md, MX1_DEVELOPMENT_REPORT.md,
MX1_CONFIRMATION_FREEZE_v1.md. Rule 4 applies (one librarian family auditing
another AI's work; S2 independent re-derivation still advised before public use).

## Verdict in one line

The Maxwell completeness audit is honest and its physics is correct; the MX1
Gauss protocol is the best-engineered empirical design in the repository; the
main risks are one near-tautology (Level 1), one vocabulary collision
("hypotenuse"), and a Level-2 target choice that the framework's own amplitude
rule predicts will keep failing.

## Machine-verified algebra (sympy, this date)

- Pair identity Q_net = T_Q(x_Q−1) = Q₊−Q₋: EXACT.
- Gauss magnetic: T(x−1)=0, T>0 ⇒ x=1 uniquely: EXACT.
- Spectral Gauss weighting |ikÊ|² = k²|Ê|²: EXACT (the TE-ARA source-
  participation formula is algebraically faithful).
- x_{D/C} = 2ωε/(σ+ωε) properly bounded: →0 (conduction-dominant),
  →2 (displacement-dominant): CORRECT.

## Physics spot-checks on the Maxwell audit — all correct

Poynting theorem signs/forms; continuity from div(Ampère–Maxwell)+Gauss;
invariants I₁=E²−c²B², I₂=E·B (and both zero for vacuum plane waves); E,B
IN PHASE in a travelling vacuum plane wave (common misconception correctly
rejected); E/B frame-mixing (kills naive E=Space/B=Time — correctly listed as
overextended); fluxoid h/2e; Poincaré sphere geometry. The ten-item
"weak or currently overextended" list is accurate physics and should be
treated as canon-adjacent — nothing in it is unfair to the framework.

## Strengths worth naming

1. **Freeze discipline is exemplary:** hashed artifacts, sealed confirmation
   archive with declared one-open rule, contamination declaration on the
   development archive, restricted-unpickle security note, baselines
   including a matched-feature generic with equal degrees of freedom, and
   interpretation rules WRITTEN BEFORE the transfer — including the narrowing
   outcomes. This is the strongest protocol in the repo; reuse its skeleton.
2. **The honest narrowing result is reported plainly:** scale-only beat
   ARA/TE-ARA additions on held-late development (R² 0.677); "adding scalar
   ARA/TE-ARA coordinates did not beat the dimensional scale-only bridge."
3. **The recommended order (continuity → Poynting → Lorentz/stress →
   invariants → Poincaré → matter → radiation → gauge/holonomy) is right,**
   and the Poincaré-sphere flag is the strongest structural suggestion in the
   document: an ESTABLISHED sphere with poles = helicities, equator = linear
   polarisation, measured Stokes coordinates — the proper formal comparator
   for the ARA sphere.

## Flags

**F1 — Level 1 is near-tautological in this simulator (state it, don't hide
it).** OSIRIS uses charge-conserving (Esirkepov) deposition, so Gauss holds
to machine precision by construction; ρ̂=ikÊ then guarantees the identity
family "survives" the Gauss map mode-by-mode. The non-trivial content of
Level 1 is only the participation comparison against the PARTICLE-side
measurement (corr 0.799, MAD 0.091) where Other and deposition noise differ.
A hostile reviewer will call Level 1 circular unless the doc says this first.
Recommend one added sentence and promotion of the 0.799 number to the
headline Level-1 metric.

**F2 — Level 2's target contradicts the framework's own registered rule.**
Level 2 asks shape coordinates (ARA/TE-ARA scalars) to predict y_Q — a
MAGNITUDE shape factor. RULE_PROPOSAL_AMPLITUDE_FROM_BELOW (5 Jul) says
own-shape never predicts magnitude; the parallax mechanism says why. The
development narrowing result (scale-only wins) is therefore not a
disappointment — it is the amplitude rule CONFIRMED in a new domain, fourth
independent appearance. Recommendation: keep Level 2 as registered (it's
frozen — run it, record the predicted miss), but pre-register Level 2b with
SHAPE-side targets where the framework claims jurisdiction: sign/composition
(x_Q), per-cell asymmetry contrast, phase/direction of drift between cells —
not magnitude. If Level 2 fails and 2b transfers, that pattern IS the
framework's signature; the protocol should say so in advance.

**F3 — vocabulary collision: "hypotenuse."** The Gauss protocol calls the ik
operator "the fixed hypotenuse" (quarter-turn + |k| weighting). But
MUSING_SHEAR_HYPOTENUSE_PITCH (11 Jul) uses "hypotenuse" for the literal
Pythagorean recovery of the intrinsic rung (φ, √(3−φ), 2). These are
different objects — one is a rotation-scaling metaphor, one is exact
trigonometry. Two meanings of one homegrown term is exactly the drift class
the glossary exists to prevent. Recommend renaming the ik usage ("the
quarter-turn bridge" or "the Gauss rotation") before the term fossilizes.

**F4 — minor.** (a) Dev report's "candidates, not yet registered" vs freeze
v1 same-day registration: fine, but the freeze doc should note it supersedes
that sentence. (b) The identity-only-vs-identity-only corr 0.999 should not
be quoted as evidence anywhere (see F1); the against-full-source 0.675 with
declared Other is the honest number and the report already frames it so.
(c) Whole-ring x_Q ≈ 1.0 (median 1.007): correctly read as the
everything-ridge cancellation of complete peer cells — good middles-rule
hygiene (variance retained, cells measured separately).

## Cross-links the suite has earned

- **Missing part 6 (gauge/holonomy) meets MUSING_GEOMETRIC_PHASE_HOLONOMY:**
  Wilson loops and fluxoid winding are the gauge-invariant holonomy
  observables, and superconducting flux quantization (h/2e steps, measured
  daily in SQUIDs) is a PHYSICAL STAIRCASE — nature's existing example of
  quantized loop-toll. The EM branch is where the staircase prediction
  already has an established cousin; say so in the holonomy musing's
  cross-references.
- **The E/B in-phase correction** (overextension #4) retires the naive
  "temporal anti-phase" reading of light; the conjugate-pair energy trade
  (SESSION_NOTES §3) survives — in a plane wave the trade is with the
  SPATIALLY adjacent cell (energy flows, u oscillates in space-time), not a
  temporal quadrature at a point. Worth one clarifying line in §3.

## Bottom line

Publishable-grade protocol engineering; correct physics; honest tiers. Fix
F1's one sentence and F3's naming, add the F2 Level-2b pre-registration, then
open the Tang arrays exactly as frozen. Whatever transfers, transfers on the
record — and if Level 2 misses on magnitude while shape targets carry, the
framework's oldest empirical law will have predicted its own result in a
domain it had never touched.

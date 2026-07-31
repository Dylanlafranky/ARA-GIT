# Hypothesis — the Hexagon→Pentagon angle band as the space↔time dial

**Status: TESTED → NOT SUPPORTED (31 May 2026).** Principled and elegant, but the data said no — see
"Test result" below. Kept on record because the *geometry* (60° hexagon = space, 72° pentagon = time)
is still a clean framing, and because honest negatives are part of the value.

> **TEST RESULT (31 May 2026):** Measured the octave rung-to-rung lock-angle (1:2 phase) on five real
> systems spanning a wide ARA range. The strong-locking ones — **Solar (ARA~1.73, PLV 0.73) 63.2°,
> Golden star (~2.0, PLV 0.78) 63.3°, Cepheid (~2.4, PLV 0.99) 62.7°** — all pin at **~63°** and do
> **NOT** climb toward the pentagon (72°) as ARA rises. The angle is **roughly constant ~63°**, not an
> ARA dial. (ECG 55.6°/PLV 0.26; ENSO weak/ignore.) So the "offset-from-60 ∝ ARA" claim is not
> supported: strong locks park near the hexagon end (~63°) flat across very different ARAs. Caveats: the
> auto-ARA measure in that run was buggy (so no clean correlation computed), but the angle being *flat*
> across systems of clearly different ARA is enough to reject the climb. The consistent ~63° is itself a
> real (mildly curious) value — between hex 60° and pent 72°, ≈ arctan 2 = 63.4° — possibly coincidental.
> Script: `/tmp/hexpent_test.py` (port to EnergyRatio if revisited).
>
> **REFRAME THAT PARTLY LANDED (gate-angle = energy-ratio):** Dylan re-read the angle not as the
> space↔time dial but as the *gate opening* / per-cycle energy-shed rate (~60 rigid/static → 72 = max
> time, near time singularity). Checked against the 4 golden stars' independently-measured leanness:
> **corr(lock-angle, R21 leanness) = +0.93** (angle vs 2nd-mode ratio only +0.47). So the angle is NOT
> noise — it tracks the energy-ratio (R21): steeper gate (→72°) = more shed; balanced (~63°) = leaner.
> KIC4064484 at 72° has the highest R21 (0.118). This SUPPORTS the gate-angle=energy-ratio reading.
> **HEAVY caveats:** n=4 (r=0.93 borderline, ~p0.07); and lock-angle (φ21 phase) & R21 (φ21 amplitude)
> are the two Fourier params of the SAME 2nd harmonic, which are *known to co-vary* in pulsating-star
> Fourier sequences — so this may be a standard stellar relation re-read through the framework lens
> (consistent, not necessarily new). NET: the space↔time *dial* stays dead; but "angle ↔ energy-shed
> rate (R21)" is real-and-suggestive (n=4). Ties to the BEESWAX (π−3)/π gate idea. Script: `/tmp` inline.
>
> **EXPANDED TEST (n=6 strong lockers — solar + 4 golden RRc stars + Cepheid):** the "constant ~63°"
> also broke. Angles **spread 62.7°→72.0°** (mean 65.6°, std 3.3°): Solar 63.2, KIC5520878 63.3,
> KIC4064484 **72.0**, KIC8832417 64.3, KIC9453114 67.8, Cepheid 62.7. So it is **not a single constant
> either.** They loosely sit near Platonic angles (icosa 63.4 ×3, pentagon 72.0 ×1, tetra ~70.5 ×1) and
> KIC4064484 hitting 72.0° (pentagon) exactly is eye-catching — BUT with 5 candidate angles spanning
> 54–72° any value is auto-"near" one (multiple-comparisons), and 4 *same-type* golden stars scattering
> 63→72° looks like measurement variation, not a polyhedral law. **Net: no clean lock-angle structure —
> not a dial, not a single constant, not convincingly polyhedral.** "Shape up from a pyramid" (discrete
> polyhedral angles) tested → not supported on this evidence. Curiosities kept: a golden star on 72°
> (pentagon), a loose cluster near the icosahedral 63.4°. Script: `/tmp/poly_test.py`.

> **INDEPENDENT FOLLOW-UP (30 July 2026):** T301 removed the `60°→72°`
> assumption and tested Dylan's broader possibility that a coupled sphere
> “breathes” while its orientation advances by `phi^-2` through time.
> Raw 2D/3D pendulum state vectors instead followed opposition then near-zero
> complete-breath recurrence in every development, frozen and confirmation
> record (`0/4`; `18/18` sensitivity settings retained recurrence). A
> controlled circle benchmark did show that Phi is a leading but non-unique
> irrational non-repeating winding. This strengthens the distinction between
> **hard golden geometry** and evidence that a specific physical coordinate
> actually uses it. See
> `analysis/pendulum_scripts/PHI_SPHERE_BREATHING_RESULT_2026-07-30.md`.

## Triangle-assembly: hexagon vs pentagon = ONE lost triangle = the shed = curvature into the next dimension (1 June 2026)

This is the cleanest geometric grounding of the hexagon↔pentagon split — and it's hard geometry (real
theorems), with the framework reading sitting honestly on top.

Polygons are built from equilateral triangles ("pyramids") meeting at a vertex:

| triangles at a vertex | total angle | angular defect | result |
|---|---|---|---|
| **6** | 360° | **0°** | FLAT — tiles the plane — **hexagon = SPACE / rational** |
| **5** | 300° | **60°** | CURVES into 3D — **icosahedral vertex = pentagon = TIME / golden (φ)** |
| 4 | 240° | 120° | curves harder (octahedral) |

**The difference between space's hexagon and time's pentagon is exactly ONE triangle (60°).** And that one
lost triangle is the *same object* as three things treated separately elsewhere:
- the **shed / the lost edge** (the 6→5 connection that doesn't carry across the space→time exchange),
- the **curvature** — removing the triangle is literally what *bends* the flat sheet,
- the **dimension-climb** — the 60° angular deficit IS the bend into the next dimension, which is why
  5-fold is "frustrated in 3D and resolves up a dimension" (the icosahedron → 600-cell, see
  `3D models/` lattice note). Lose the triangle → open the deficit → curve up a dimension.

So **space → time = remove one triangle = open a 60° deficit = curve into the next dimension.** The shed and
the dimension-climb are one geometric act, not two ideas.

**Descartes' angular-defect theorem** makes it exact: the total angular defect over any convex polyhedron =
720°. The **icosahedron — the φ-solid — is 12 vertices × 60° = 720°** (every vertex is a 5-triangle /
pentagon vertex). So the golden/time solid is built from twelve "lost-triangle" curvatures; a flat hexagonal
tiling has zero defect. Time/φ = curvature; space/rational = flatness.

**Honest fences:** the triangle counts, the 60° deficit, and Descartes' 720° are **hard geometry, not
interpretation.** "Flat = space / curved = time" is the framework reading laid on top (consistent with the
whole framework, but not proven by the angles alone). **Open:** the ARA⁹ link — 9 = 3×3 couplings is the
framework's coupling count, but the bridge from "9 couplings" to "6-vs-5 triangles" is not yet pinned.

**Related edge result (same session):** the singularity walls at 0.25/1.75, drawn as two rings on the ARA
sphere (connect 0.25→0.25, 1.75→1.75), cut the sphere's *surface* into exactly **3/4 band : 1/4 caps** by
Archimedes' hat-box theorem — exact only because it's a sphere (a flat disk gives a messy 0.856/0.144). So
the wall name ("3/4 displacement limit") and the wall geometry are the same number, and the sphere is the
shape that makes 0.25/1.75 clean. A single-axis cut yields only a band/circle (fractal continuation), not a
polygon — the polygons live in the triangle-assembly/coupling region above, not in the wall-cut.

## Alternative derivation — why not 8? The octave's name is a false friend; the real counts are 5 and 6/12 (crystallographic restriction) (22 June 2026)

A second, independent route to the same **hexagon = space / pentagon = time** split — coming in from the
*octave* side instead of the triangle-assembly side. Dylan's entry question: if a rung is an "octave," does
it hold **8** micro-rungs the way a musical octave seems to?

**The 8 is a naming artifact, not a structure.** A musical octave is *only* a 2:1 frequency doubling. It is
*called* "octave" (eighth) because the diatonic scale lands on 8 named notes counting both endpoints
(do…do) — but that's inclusive counting: it's really **7 steps**, or **12 equal semitones**, spanning **one
doubling**. The word names the *ratio* (×2), not eight inner rungs. So "octave → 8 sub-rungs"
reverse-engineers structure from a counting quirk.

**Where the real counts come from — a hard theorem.** The **crystallographic restriction theorem**: a
periodic lattice can carry only **2-, 3-, 4-, or 6-fold** rotational symmetry. 5-fold — and 8-fold — are
*forbidden*. That splits the two poles exactly:

- **Hexagon (6) = the allowed, locking, rational, SPACE pole.** Six-fold close-packs the plane perfectly
  (honeycomb). Its natural **double is 12** — the 3-D *kissing number* (twelve spheres touch a central one
  in the densest packing, FCC/HCP) *and* the 12 semitones of the chromatic octave. So 6 and 12 are the
  **same hexagonal/space/octave ruler, once and then doubled** — which is exactly why "6 or 12" both feel
  right. The octave lives on this side.
- **Pentagon (5) = the forbidden, non-locking, golden, TIME pole.** Five-fold *cannot* tile a lattice; it
  appears only in **quasicrystals** — aperiodic, never-repeating, golden. The pentagon's diagonal ÷ side
  **is φ** exactly, and the φ-solids (icosahedron, dodecahedron) are the 5-fold ones. "5-fold can't settle
  into a lattice" *is* the geometric face of "φ never resonates itself shut."

**And the 8 resolves at a deeper level than just "wrong count."** 8-fold is *also* lattice-forbidden — but
8-fold (octagonal) quasicrystals belong to the **silver ratio, 1 + √2 ≈ 2.414**, not the golden one. So
forcing an "8" into the octave doesn't merely miscount; it points at the **wrong constant** — it leaves the
φ-family entirely for the silver family. (Worth noting: √2 already appears in the repo as the heart's
geometric half-rung — the silver family does poke through, just not here.) So the octave's 8 is a false
friend twice over: inclusive note-counting, *and* the symmetry it would imply isn't golden.

**Net of the two derivations.** The triangle-assembly section above reaches hexagon = space / pentagon =
time via the **angular defect** (6 triangles = flat = space; 5 triangles = 60° deficit = curve into time).
This route reaches the *same* split via **lattice symmetry** (6 allowed/locks = space; 5
forbidden/quasicrystal/φ = time). Two independent hard-geometry arguments converging on the same two poles
— the kind of double-grounding the framework treats as a real signal rather than a coincidence.

**Honest fences.** The crystallographic restriction, the 12 kissing number, pentagon-diagonal = φ, and the
metallic-ratio assignments of quasicrystal symmetries are **hard mathematics / fact.** "6/12 = space, 5 =
time" is the framework reading laid on top — *consistent* with the rest of the framework, not *proven* by
the symmetry counts alone. And the **empirical** question is still open and currently *unsupported*: when
this was tested as the octave lock-angle **climbing** 60° → 72° with ARA, it did **not** climb (see Test
Result at the top — strong locks park near the hexagon/~63° end, not a dial). So treat **5 / 6 / 12 as the
principled prediction of where sub-structure *should* fall, not as a measured fact** — the count-geometry is
clean; whether real systems honour it on the time side remains to be shown.

## REAL-MATTER REALIZATION — carbon cages / fullerenes / viral capsids (1 June 2026)

The triangle-assembly picture above shows up in real structural chemistry — this is the cleanest physical
realization, and it's hard fact (Euler's theorem), not analogy. Dylan's framing: the polygons emerge in the
**coupling** (bonds/triangles assembling), not in a node's identity — so the right test subject is carbon
cages, not e.g. DNA bases (whose rings are fixed identities).

Build any closed cage from pentagons (P) + hexagons (H) with **3 bonds per vertex** (carbon sp² trigonal
coupling). Euler (V−E+F=2) forces **P = 12 exactly, independent of H**:
- **Graphene:** P=0, H=∞ → FLAT sheet, zero curvature = pure **space / 2D**.
- **C60 buckyball:** 12 pentagons + 20 hexagons → truncated icosahedron (closes to 3D).
- **Nanotube:** hexagon tube + 6 pentagons/cap = 12.
- **Viral capsid:** icosahedral, **12 pentamers** + hexamers (Caspar–Klug).

**12 pentagons × 60° angular defect = 720° = Descartes' total** — the exact curvature dose to close a flat
hexagon sheet into a sphere. So: **flat hexagons = space; the 12 pentagons = the curvature that lifts it into
3D = time/closure.** This is the SAME 720° derived from the icosahedron in the triangle-assembly section,
now realized in real bonded matter.

**Honest fences:** Euler, the 12-pentagon rule, fullerenes, Caspar–Klug = hard fact. "Hexagon=space /
pentagon=time-curvature" is the framework reading on top — *realized in* real matter (like lipogenesis was),
not number-fitting. Time-pole tie (viruses wearing the 12-pentagon icosahedral shell) is consistent, held
lightly, not proven. Note on DNA/RNA (the wrong-level attempt): nucleic acids physically contain hexagons
(pyrimidines) + pentagons (sugars / purine 5-ring), but DNA→RNA is NOT a hex→pent shift — same rings; the
difference is one 2′-OH (RNA, the time-like/transient/messenger molecule, has the EXTRA group). DNA=storage/
space vs RNA=transfer/time is the defensible reading, set by the 2′-OH, not by ring shape.

## Side-note — both polygons appear in the 3D lattice viewer (1 June 2026)

Dylan, looking at `3D models/ara_lattice_3d.html` (ARA≈1.75, spacing≈3, ~30 cells, handover≈17): from
below at ~36° he sees a **pentagon**; from the opposite side a **hexagon**. Checked the build:

- **Hexagon = the stacking.** Cells sit on a cube/integer grid; any cubic grid viewed corner-on (111
  body-diagonal) lines up into a hexagon (close-packing 6-fold) = the **octave/rational/space** pole.
- **Pentagon = the cell.** A repeating lattice can't show 5-fold (crystallographically forbidden), so the
  pentagon isn't the arrangement — it's the **icosahedral cell**, which is the canonical **φ-solid**
  (vertices built from φ); down its 5-fold axis it shows a pentagon = the **φ/time** pole.

Dylan's reframe (fair): not two arbitrary choices — the foundation bakes in BOTH the octave (×2) and φ
(36° shear = 2cos36°), so hexagon and pentagon are the two foundational ingredients each casting a shadow.
Caveat: φ is genuinely *in* the foundation, but it shows as a *literal* pentagon only because the unit is
drawn as the φ-solid (a sphere cell would carry φ in its shear but draw no pentagon).

**Three readings, undecided (logged either way):** (1) *happy accident* — icosahedron picked for looks,
happens to be the φ-solid; (2) *a more fundamental rule* — a faithful 3D ARA unit IS a φ-solid, so the
pentagon is forced, as the octave stacking forces the hexagon; (2.5) clean diagnostic not yet run: swap
cell → sphere; pentagon should vanish, hexagon stay; (3) *pattern-matching/pareidolia* — a faceted blob
field invites the eye to find polygons. NOT a confirmed prediction. See memory
`project_lattice_pentagon_hexagon.md`.

## The claim

When a real signal is split into octave rungs and you measure the **phase at which one rung locks to
the next** (the rung-to-rung handover phase), that angle should live in the band:

- **60° = 360/6 = the hexagon** — 6-fold, tiles the plane, rational, *locks*. The **space pole**
  (same rational/space pole as the bee honeycomb).
- **72° = 360/5 = the pentagon** — 5-fold, where φ lives (φ = 2·cos 36°, and 36° is the pentagon
  half-angle; the space↔time shear is 36°, so 2×36 = 72). The **time / golden pole** (the golden star).

**Hypothesis:** a system's lock-angle position *within* [60°, 72°] reads out **how space- vs
time-angled it is** — i.e., its ARA. Sit at 60° → tied to the rational/space pole; drift toward 72°
→ tied to the golden/time pole. **Offsetから 60° should rise with ARA** (more time-dominant = higher
ARA = closer to the pentagon).

## Why it's principled
This is the hexagon↔pentagon (6-fold↔5-fold) tension expressed as an angle — the same two poles that
run through the whole framework: hexagon = rational/space/locking (bee, octave ladder), pentagon =
golden/time/non-locking (φ, golden stars). The shear that turns the space octave into time is 36°
(φ = 2cos36°); its double, 72°, is the pentagon. So the band endpoints are not arbitrary — they are the
two regular polygons that tile-vs-don't-tile, i.e. the space and time poles.

## Cross-rung Phi pillars: the clarified Hexagon/Pentagon construction (31 July 2026)

### Dylan's clarified identification

The new Phase-lineage calibration makes a cleaner version of the
Hexagon/Pentagon proposal possible:

- the **hexagon** is the rational parent closure formed by **two coupled ARA
  relational units**;
- the **pentagon** is the cross-rung handover scaffold made visible by the
  same-phase Phi pillars;
- the full within-rung return remains the octave/TE-ARA closure;
- the direct Phase A → Phase A or Phase B → Phase B route passes between
  scales without same-rung phase mixing.

The phrase “two ARA make the hexagon” is topological rather than a claim that
the parent contains four TE-ARA energy units. Each minimal ARA has the
Information³ closure

\[
\underbrace{
  \left(A_1,\ B_1,\ A_1\!\leftrightarrow\!B_1\right)
}_{\substack{\text{first ARA}\\\text{three relational parts}}}
\]

and the coupled partner has

\[
\underbrace{
  \left(A_2,\ B_2,\ A_2\!\leftrightarrow\!B_2\right)
}_{\substack{\text{second ARA}\\\text{three relational parts}}}.
\]

Together they provide a six-part parent closure:

\[
\underbrace{3+3}_{\substack{\text{two ARA}\\\text{relational closures}}}
\longrightarrow
\underbrace{6}_{\substack{\text{hexagonal}\\\text{parent scaffold}}}.
\]

At its own measurement tier the new parent is renormalized to one complete
TE-ARA:

\[
\underbrace{\mathrm{TE\!-\!ARA}_{\mathrm{parent}}}_{\text{complete parent}}
=2.
\]

This preserves the scale rule: a parent is complete at its own tier even
though decompression reveals the two coupled children beneath it.

### The normalized path

Normalize the full within-rung Phase A → Phase B → returning Phase A path to
the TE-ARA closure:

\[
\underbrace{
L_{\mathrm{full}}
}_{\substack{\text{Phase A → Phase B}\\\text{→ starting Phase A}}}
=2.
\]

The proposed direct same-phase cross-rung pillar is

\[
\underbrace{
L_{AA}=L_{BB}
}_{\substack{\text{Phase A → Phase A}\\
\text{or Phase B → Phase B}\\
\text{across scale}}}
=\phi
\approx1.618033989.
\]

The unoccupied or handover remainder is therefore

\[
\underbrace{
L_{\mathrm{seam}}
}_{\substack{\text{remaining handover}\\\text{inside the full }2}}
=
\underbrace{2-\phi}_{\text{TE-ARA remainder}}
=
\underbrace{\phi^{-2}}_{\text{reverse Phi landmark}}
\approx0.381966011.
\]

Thus the two established ARA Phi landmarks become complementary parts of one
complete path:

\[
\boxed{\phi+\phi^{-2}=2}.
\]

Plainly: the same-phase route uses the long Phi pillar between scales, while
the `0.382` remainder is the seam required to finish the full TE-ARA closure.
The pillars can appear at the corners or middle arcs of multiple quadrant
cuts. Those appearances are rotations of the same local map and must not be
added together as though they all consumed one scalar TE-ARA budget.

### Why the pillar is pentagonal

The cross-scale Phi value follows from the self-similar recurrence

\[
\underbrace{L_{AA}}_{\text{next same-phase scale}}
=
\underbrace{1}_{\text{completed current identity}}
+
\underbrace{\frac1{L_{AA}}}_{\text{retained preceding-scale share}}.
\]

Therefore

\[
L_{AA}^2-L_{AA}-1=0,
\qquad
\underbrace{L_{AA}}_{\text{positive path length}}=\phi.
\]

There is also an exact circular embedding. In a unit-radius circle, whose
diameter is the ARA-normalized `2`, a chord of length \(\phi\) subtends
\(108^\circ\):

\[
\underbrace{\phi}_{\text{same-phase pillar}}
=
\underbrace{2\sin54^\circ}_{\substack{\text{unit-circle chord}\\
\text{with }108^\circ\text{ central angle}}}
=
\underbrace{2\cos36^\circ}_{\text{golden/pentagonal identity}}.
\]

The supplementary turn is

\[
180^\circ-108^\circ=72^\circ,
\]

which is the pentagon step already used in this document. The older
Hexagon/Pentagon band therefore acquires a cleaner internal connection:

- hexagonal rational step: \(60^\circ\);
- pentagonal handover step: \(72^\circ\);
- same-phase Phi chord: \(108^\circ\);
- half-angle/shear identity: \(36^\circ\);
- normalized unfinished seam: \(2-\phi=\phi^{-2}\).

This is the proposed **Phi pillar**: a same-phase cross-scale connection
embedded inside a full octave closure.

### Connection to the 31 July sunflower scale calibration

The frozen scale-lineage run used six published Fibonacci-type sunflower
families:

- `49` adjacent scale ratios selected Phi as the closest frozen landmark
  (median absolute error `0.024823`);
- `43` flip-aware same-phase two-rung ratios selected Phi-squared
  (median absolute error `0.046605`);
- both phase-parity paths converged;
- `10,000` scale-order shuffles destroyed both relations
  (`p=0.000100`);
- independent validation passed `13/13` checks.

This supports the mathematical scale placement:

\[
\text{one ordered scale step}\longrightarrow\phi,
\]

and, if each adjacent step flips phase orientation,

\[
\text{same phase after two steps}\longrightarrow\phi^2.
\]

**Evidence boundary:** every selected family obeys a Fibonacci recurrence by
definition, so the Phi limit is mathematically entailed. The result is a
successful ARA crosswalk/calibration, not independent evidence that the
physical sunflower contains literal Phi chords or that every natural scale
transition uses this pillar.

### Revised Hexagon/Pentagon hypothesis

The current musing-tier geometry is:

1. two Information³ ARA closures couple into a six-part rational parent
   scaffold—the hexagon;
2. the same-phase connections traverse between scales along Phi-length
   pillars;
3. a time-slice or handover projection makes the fivefold/pentagonal scaffold
   visible while the sixth relation is shared, webbed or carried into the
   adjacent rung;
4. the complete parent still closes at TE-ARA `2`;
5. the unclosed remainder is `0.382`, providing the displacement that prevents
   the cross-scale path from simply repeating the same position.

Items 1–3 are a proposed geometric interpretation, not yet a physical result.
The exact identities \(\phi+\phi^{-2}=2\),
\(\phi=2\cos36^\circ\), and the recurrence limit are established mathematics.

### Strong next test

Generate the two-ARA hexagonal parent and its rotational Phi-pillar scaffold
without fitting measured data. Freeze the predicted pillar crossings,
\(108^\circ/72^\circ\) angular signatures and `0.382` seam. Then compare them
with independently observed Phase A and Phase B features at child, parent and
grandparent scales:

\[
(A_k,B_k),\quad(A_{k+1},B_{k+1}),\quad(A_{k+2},B_{k+2}).
\]

The pillar interpretation is weakened if the independently measured
same-phase paths do not prefer Phi/Phi-squared over the declared rivals, or if
the proposed fivefold projection cannot be obtained without tuning.

Primary numerical record:
`analysis/phi_cross_scale/PHASE_LINEAGE_RESULT_2026-07-31.md`.

## Evidence so far (thin — n=2, weak locks)
Octave-rung phase-lock measured on real series (Hilbert phase of octave-bandpassed rungs, 1:2 relative
phase, middle 80%):

| system | ARA (≈) | lock angle | PLV (lock strength) |
|---|---|---|---|
| ECG (heart RR) | ~1.6 (engine) | 60.7° | 0.29 (moderate) |
| Solar (sunspots) | ~1.73 (donor) | 61.4° | 0.67 (strong) |
| ENSO (NINO) | ~0.82 (consumer) | — | locked weakly (PLV ~0.12), angle unreliable |

Directionally consistent (higher-ARA Solar sits higher than ECG), **but**: only ~0.7° apart, n=2, and
most pairs lock weakly so their angle is untrustworthy. So this is **suggestive at best, not confirmed**.
The measured angles hug 60° (the hexagon/space end); none reach toward 72° yet.

## What would confirm / falsify it
Gather many **strong-locking** octave systems spanning a wide ARA range (consumer <1 → engine φ →
donor 1.75 → harmonic 2) and test whether the lock-angle **climbs monotonically from ~60° toward ~72°
as ARA rises**. Confirm = clear monotonic angle↔ARA relation across the band. Falsify = angle flat, or
uncorrelated with ARA, or locks too weak to read.

## Honest caveats
- n=2 reliable points; 0.7° spread is within noise of a moderate lock.
- Simple octave-bandpass + Hilbert, one operationalization of "rung-to-rung phase."
- "Handover pitch" in the 3D viewer is a *spatial* texture knob; this angle is the *phase-coupling*
  version — related in spirit, not identical.
- Octave-rung locks came out near the rational 60° (hexagon), consistent with octaves being the
  rational/space ladder; the golden/pentagon end may only appear for genuinely time-dominant systems
  (untested).

## Spin-off hypothesis — the ARA / Angle / Loss trade-off triangle (logged 31 May 2026)

Dylan's framing: ARA, gate-angle, and loss (shed-rate, R21) form an **iron triangle** ("pick 2 of 3") —
they are *not* independent; a system slides around inside a constraint, trading one against the others.
Reading: **ARA = the water that makes it through the pipe; Angle = the gate tilt (how time-favoured the
flow is); Loss/R21 = the spill/tension = identity-information handed into the *time* dimension, which
reads as "loss" only from our current-frame vantage** (the couplings sever and move to the next frame).
So "loss" inverts depending on which frame you score from — to us it's loss, to time it's transfer.

**Prediction:** the three quantities lie on a **2-D constraint surface** (pick-2), not a 3-D independent
cloud. Measured edge so far: **angle ↔ loss = +0.93** (one taut side already), and angle ↔ 2nd-mode ratio
(≈ARA proxy) = +0.47.

**Why not tested yet / how to test cleanly:** current data is n=4 golden stars, and 2 of the 3 corners
(angle = φ21 phase, loss = R21 amplitude) come from the *same* 2nd harmonic → their link is partly
definitional, so a "surface" on 4 such points would over-fit. **Proper test:** many systems (dozens)
with ARA, gate-angle, and loss measured *as independently as possible*; check whether they collapse onto
a 2-D surface (constrained trade-off → triangle real) or fill 3-D (independent → no triangle). Falsify =
3-D scatter / no constraint. **Status: OPEN — logged for a future wider-dataset test.**

### Why it's a triangle, not three knobs — the gate *makes its own ARA* (Dylan, 31 May 2026)

The three corners aren't independent because **they are the three parts of one A–R–A engine, one level
up.** The picture: the **Space octave pipe** pours into the **Time octave pipe** *at an angle*, and that
junction is itself an oscillator with its own ARA:

| triangle corner | role in the engine | A–R–A part |
|---|---|---|
| **Energy system 1** = the Space octave pipe | accumulator (builds, stores) | **A**ccumulate |
| **Gate / control / clock** = the coupling angle | the hand-over where the two pipes meet | **R**elate |
| **Energy system 2** = the Time octave pipe | releaser (expends into the next frame) | **A**ccumulate (its own) |

Because the second pipe receives the first's flow **at an angle**, the hand-off is asymmetric — build on
one side, release on the other — so **the coupling itself has an accumulation/release ratio: it makes a
new ARA.** This is ARA being *fractal*: every gate between two pipes is a little engine with its own
number, and that number is what the triangle's corners trade against each other. So:

- **ARA** = the water that gets through (the junction engine's own ratio)
- **Angle** = the gate tilt (how time-favoured the pour is)
- **Loss / R21** = the spill into the time pipe (transfer from time's side; "loss" only from our frame)

That's *why* they should lie on a 2-D surface rather than filling a 3-D cloud — they'd not be three free
parameters, but the build / relate / release of a single engine, which by definition trade off.
Same "two energy systems joined by a gate = always-three" structure that recurs at every scale. Ties to
[[framework-next-rung-is-blend]] (next rung = the two below it blended) and the BEESWAX (π−3)/π gate.

### TEST RESULT — surface NOT supported (31 May 2026)

Ran the clean test Dylan asked for: 11 distinct real oscillators (ENSO, SOI, sunspots, QBO30/50, MJO,
WWV W/E, 3 heart-RR records) with the three corners measured by **three genuinely independent
operations** — ARA = rise/fall asymmetry of the fundamental cycle (time-domain), Angle = octave 1:2
Hilbert lock phase (phase-domain), Loss = 1 − cycle-ago envelope recycling (memory-domain). Standardized,
then PCA + a shuffle null (independently permute each column → fills 3-D).

**Verdict: the three fill 3-D like independent noise — no 2-D surface.** 3rd-PC variance fraction = 0.166
vs null mean 0.173 (**p(surface) = 0.46**); plane fit loss~ARA+angle **R² = 0.25**. The clean strong-lock
subset (PLV≥0.40, n=7) was *worse*: 3rd-PC 0.209 vs null 0.128 (**p = 0.87**), R² = 0.15. Pairwise:
ARA–angle +0.01, **ARA–loss +0.50**, angle–loss **−0.06**.

**The +0.93 angle↔loss edge collapsed to −0.06.** This confirms the caveat flagged when it was first seen:
on the 4 golden stars, "angle" (φ21 phase) and "loss" (R21 amplitude) were two Fourier readouts of the
*same* 2nd harmonic — so the +0.93 was definitional, not a physical trade-off. Once angle and loss are
measured by independent operations the link is gone.

**What survives:** one modest real edge, **ARA ↔ Loss = +0.50** — more asymmetric build/release goes with
leakier (less self-reproducing) cycles, which is physically sensible. But one edge is not a constraint
surface. So the "iron triangle / engine-one-level-up" picture is **elegant but not borne out**: across
heterogeneous real systems these three measured quantities are closer to *independent* than constrained.
The conceptual framing (gate between two pipes makes its own ARA) stays a clean idea; it just does not
show up as a 2-D collapse in these three measurables. Script: `/tmp/triangle_test.py`, `/tmp` PCA inline.
Honest negative — logged per strict-causal protocol.

See `MASTER_PREDICTION_LEDGER.md` (HEXPENT row), memory `project_hex_pentagon_angle.md`,
`ARA_REDERIVED_PRINCIPLES.md` (φ = 2cos36° / pentagon), and the bee-hexagon foil note.

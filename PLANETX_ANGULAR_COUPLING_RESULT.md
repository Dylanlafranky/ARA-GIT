# Planet X by the angles — testing the framework's anti-phase coupling against real eTNO data

**Date:** 2026-05-29
**Status:** Exploratory, real data, HONEST NULL. The framework's distinctive prediction is **not** supported here — and the textbook's core evidence is itself weak in current data. Reported straight.
**Question (Dylan):** The spacing channel (PLANETX_EMPTY_RUNG_RESULT.md) only matched the 250-year-old Titius–Bode law. The test only the framework could win is the **angles**: are the extreme trans-Neptunian objects (eTNOs) angularly clustered, and does reading them as a **matched-rung anti-phase pair** with a hidden perturber recover the same perturber the astronomers infer — through an independent channel?

## Short version

- **The framework's anti-phase prediction finds no support in current real eTNO data.** No spin: this is a clean null for the distinctive claim.
- **The famous apsidal clustering (the core Planet Nine evidence) is NOT statistically significant in the full current catalogue.** Longitude of perihelion ϖ for the canonical-style set (a>250 AU, q>40 AU, n=21) clusters only weakly: R=0.26, **Rayleigh p≈0.24** — consistent with chance. Looser/tighter cuts give p≈0.12–0.40. We independently reproduced the **OSSOS skeptics' result**: the original 318° clustering of ~6 objects fades as the sample grows.
- **The "anti-phase = two groups 180° apart" (bimodal/axial) test is also null.** Doubling the angles and re-testing (the proper test for an anti-phase signature) does **not** beat the unimodal test anywhere — axial ϖ p≈0.34–0.67. There is no hidden anti-aligned pair structure to find.
- **The one surviving real signal is unimodal node clustering** — the orbital *planes* align (longitude of ascending node Ω, a>150 q>30, n=75: mean ≈133°, R=0.31, **p≈0.001**). But this is unimodal plane-alignment, **not** the framework's anti-phase apsidal coupling, and it is itself subject to the observational-bias debate.

## What we did (real data)

- Pulled orbital elements (a, e, i, Ω, ω, q) for **all 706 known objects with a ≥ 150 AU** from the JPL Small-Body Database Query API (`ssd-api.jpl.nasa.gov/sbdb_query.api`). Real, current catalogue — not synthetic, not the cherry-picked 2016 set.
- Computed longitude of perihelion ϖ = Ω + ω and node Ω for several standard extreme-population cuts.
- **Unimodal clustering:** Rayleigh test for non-uniformity.
- **Anti-phase (framework-specific) test:** doubled each angle (2ϖ) and re-ran Rayleigh — the standard axial test that detects two peaks 180° apart, i.e. an anti-aligned pair. This is the signature the framework's matched-rung anti-phase coupling would produce, and which a plain unimodal test would miss.

## Results

| set (a>, q>) | n | ϖ unimodal p | ϖ axial(anti-phase) p | Ω unimodal p | Ω axial p |
|---|---|---|---|---|---|
| 150, 30 | 75 | 0.115 | 0.387 | **0.001** | 0.007 |
| 150, 40 | 28 | 0.288 | 0.668 | 0.027 | 0.343 |
| 250, 30 | 37 | 0.395 | 0.335 | 0.173 | 0.286 |
| 250, 40 | 21 | 0.242 | 0.641 | 0.344 | 0.601 |
| 230, 30 | 40 | 0.305 | 0.440 | 0.111 | 0.238 |

Reading: apsidal (ϖ) clustering never reaches significance; the anti-phase/axial version is no better (usually worse); only the node-plane alignment at the loosest cut is significant, and it is unimodal.

## Verdict — honest

1. **Framework distinctive claim (matched-rung anti-phase apsidal coupling): NOT supported.** There is no significant apsidal clustering and no bimodal anti-phase structure in the current real data to lock onto.
2. **This is not the framework losing to the textbook — the textbook's own headline evidence has weakened.** The apsidal clustering that launched the Planet Nine hypothesis is, on the full modern catalogue, consistent with selection bias + small-number statistics (the OSSOS position). The 2025 object 2023 KQ14 ("Ammonite") sits on the *opposite* apsidal side, further filling the gap and cutting against a single tight cluster.
3. **The surviving signal (plane/node alignment) is the honest place for any future test** — but it is unimodal, not anti-phase, so it does not vindicate the framework's specific prediction, and bias must be modelled before claiming anything.

## Why this is the right outcome to record

The spacing channel was a soft hit shared with Titius–Bode. The angles channel was the one place the framework could have produced something only it predicts. It didn't — and saying so plainly is worth more than a manufactured win. The framework's anti-phase coupling is confirmed where the signal is strong and clean (ENSO SOI/PDO, orbital matched-rung anti-correlations); the distant solar system simply does not currently have a strong enough angular signal — for anyone — to test it.

## Honest scope / caveats
- Real current catalogue, but eTNO discovery is heavily bias-driven (surveys look where they look); none of these numbers are bias-corrected. A proper test needs a survey selection function (e.g. OSSOS) folded in.
- Small n (21–75 depending on cut). Rayleigh p-values are approximate at these sizes.
- Static geometric/angular test, not a strict-causal forecast.
- The node-clustering signal (p≈0.001) is real in this dataset but is exactly the quantity the bias debate centres on — not claimed as a framework result.

## Files
- `TheFormula/etno_cluster.py` — fetch JPL SBDB elements, unimodal Rayleigh clustering, threshold scan
- `TheFormula/etno_antiphase.py` — axial (anti-phase/bimodal) Rayleigh test
- `TheFormula/etno_data.npz` — cached elements (706 objects, a≥150 AU)

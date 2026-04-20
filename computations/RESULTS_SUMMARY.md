# Action Spectrum Analysis — Computation Results
**April 20-21, 2026 — Dylan La Franchi & Claude**

---

## What We Tested

Seven sequential analyses testing whether the action spectrum (Action/π = T × E / π for oscillatory systems) has internal structure — specifically, whether subsystems within coupled systems are spaced at preferred intervals on the log₁₀(Action/π) axis.

## Scripts (run in order)

| # | Script | What it does | Outcome |
|---|--------|-------------|---------|
| 01 | `harmonic_ratio_test_naive.py` | Tests if subsystem action ratios approximate simple fractions (n:m, n,m ≤ 12) | **INVALID** — null hypothesis shows random data scores 100% too. Fractions are too dense; test has no discriminating power. |
| 02 | `harmonic_ratio_test_tightened.py` | Uses only 8 independently-measured within-system gaps. Tests clustering around 4π and (2π)². | **Suggestive** — gaps cluster into two groups at means 0.995 and 1.571, near predicted 4π (1.099) and (2π)² (1.596). |
| 03 | `bimodal_cluster_test.py` | Monte Carlo significance test for the bimodal clustering. | **p = 0.000017 for combined tightness + location test.** But see Script 05 — the input gap values were unreliable. |
| 04 | `atomic_clock_transitions.py` | Maps Cs-133 and Sr-87 orbital transitions. Tests if 4π spacing appears between atomic levels. | **KEY THEORETICAL RESULT:** Action/π = n_eff × ℏ for any atom. Every photon = 2ℏ. But 4π spacing does NOT appear between atomic levels — they're too close together. 4π (if real) is a macro phenomenon. |
| 05 | `tighten_subsystems_primary_sources.py` | Recomputes all subsystem actions from primary-source T and E values. | **BREAKS THE PATTERN.** Tightened gaps are: 0.58, 1.17, 1.37, 1.57, 1.85, 2.0, 4.4, 5.3, 8.8, 8.9, 9.4 — scattered, not bimodal. The p = 0.000017 was an artefact of the original estimates. |
| 06 | `spacing_candidates_all.py` | Tests 16 candidate spacings (4π, 2π, φ, e, integers, etc.) against tightened gaps. Frequency analysis for best-fit period. | **Best-fit fundamental period ≈ 0.201 (on fine grid), close to log₁₀(φ) = 0.209.** All gaps fit as integer multiples within 5%. BUT see Script 07. |
| 07 | `phi_significance_monte_carlo.py` | Monte Carlo significance test for φ spacing. | **KILLED.** φ fit p = 0.92 (random data fits equally well). Periodicity of any kind: p = 0.86. The φ result was an artefact of small period sizes allowing dense integer multiples. |

## What Survived

1. **Action/π = T × E / π recovers ℏ from hydrogen** — exact, mathematical identity. Not a claim; a calculation.

2. **Action/π = n_eff × ℏ for any atom** — derived theoretically from Coulomb potential. Verified for Cs-133 and Sr-87. Universal.

3. **Every photon carries exactly 2ℏ of action** — universal, frequency-independent. The photon is the fundamental "action quantum."

4. **Hydrogen action ladder = musical harmonic series** — Action at level n = n × ℏ. Ratios between levels are exactly the musical intervals (octave 2:1, fifth 3:2, fourth 4:3, etc.).

5. **Three-axis coordinate system** — ARA (shape), Period (scale), Action/π (weight) are demonstrated to be independent axes.

6. **Five clusters on the action spectrum** — Quantum, Micro, Human, Mesoscale, Macro. Real pattern but based on only 8 systems.

## What Broke

1. **4π within-system spacing** — Dissolved when subsystem action values were recomputed from primary sources. The original gap values were sensitive to how subsystems were defined and estimated.

2. **φ as fundamental spacing** — Not significant (p = 0.92). Small periods trivially produce good integer-multiple fits.

3. **Bimodal clustering at 4π and (2π)²** — The p = 0.000017 was real for those specific 8 gap values, but those values changed when tightened. The clustering was in our estimates, not in physics.

## Root Cause of Failures

The **E-subjectivity problem**: for complex systems (neurons, hearts, storms, ecosystems), "energy per cycle" depends on where you draw the system boundary and which energy flows you count. Different reasonable choices give different E values, which give different Action/π values, which give different within-system gaps. Two researchers could get different gaps from the same system.

This is the criticism flagged in the Paper 5 energy definition notes. The Freeze Test ("would this energy stop flowing if you stopped the cycle?") helps but doesn't fully resolve boundary ambiguity for ecological and atmospheric systems.

## What's Needed Next

1. **More systems (20-50+)** with high-confidence E values to test cluster structure with statistical power
2. **Precision systems** where E is unambiguous: electronic oscillators, crystal resonators, MEMS devices, pendulums
3. **Independent researchers** computing Action/π for the same systems to test E-reproducibility
4. **Gap-filling systems** to test whether the five clusters persist or merge

## Honest Assessment

The three-axis framework is sound. The T × E / π formula connecting to ℏ is real physics. The question of whether the action spectrum has *internal structure beyond the quantum level* remains open. Tonight's work established that the within-system spacing claims cannot be supported with current data quality — but also didn't rule them out. The answer requires more systems, better energy estimates, and independent verification.

---

*All scripts are reproducible. Run with Python 3.8+. No external dependencies beyond standard library.*

# The Geometry of Time

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19653363.svg)](https://doi.org/10.5281/zenodo.19653363)

**A heuristic framework for measuring temporal phase asymmetry in non-equilibrium systems.**

Every natural cycle — a heartbeat, an ocean oscillation, a stellar pulsation, a walking stride — splits into an accumulation phase and a release phase. This framework measures the ratio between them (the ARA ratio: T_release / T_accumulation) and maps the result onto a 0-to-2 scale.

Across 12 systems spanning cardiology, gait biomechanics, geophysics, astrophysics, and neuroscience, the ARA ratio clusters near φ ≈ 1.618 for free-running, self-organising systems. A Monte Carlo significance test (10M simulations, 5 null distributions) returns combined significance of 1 in 2,300 to 1 in 10,500.

The framework is falsifiable, open-source, and actively invites replication.

## What's Here

| File | Description |
|------|-------------|
| [`geometry_of_time_framework.html`](geometry_of_time_framework.html) | Full technical framework — all 12 systems, methodology, honest caveats |
| [`geometry_of_time_preprint.pdf`](geometry_of_time_preprint.pdf) | Academic preprint (Zenodo DOI: [10.5281/zenodo.19653363](https://doi.org/10.5281/zenodo.19653363)) |
| [`temporal_friction.html`](temporal_friction.html) | Theoretical extrapolation — why φ? KAM theorem, phyllotaxis analogy, resonance evidence |
| [`old_faithful_analysis.html`](old_faithful_analysis.html) | Old Faithful geyser — surface miss, underground onset hypothesis, seismic validation |
| [`sleep_cycle_analysis.html`](sleep_cycle_analysis.html) | Human sleep architecture — φ as dynamic crossover point in NREM/REM ratios |
| [`enso_analysis.html`](enso_analysis.html) | ENSO (El Niño / La Niña) — accumulation/release timing from 75 years of NOAA data |
| [`engine_ara_map.html`](engine_ara_map.html) | Multi-system ARA mapping — 4-stroke engine decomposed into 6 coupled subsystems |
| [`pc_ara_map.html`](pc_ara_map.html) | Multi-system ARA mapping — PC decomposed into 6 coupled subsystems |
| [`heart_ara_map.html`](heart_ara_map.html) | Multi-system ARA mapping — human heart (8 subsystems, blind prediction test: 8/8 hits) |
| [`substack_draft.md`](substack_draft.md) | Plain-language overview for general audience |
| `analysis/` | All Python analysis scripts — reproducible, documented |

## The Core Idea

Natural cycles that are free-running (not externally forced), self-timed, and threshold-driven tend to converge on an accumulation/release ratio near the golden ratio. The theoretical explanation: φ is the frequency ratio most resistant to harmonic self-interference (KAM theorem), making it the optimal way to pack energy into time without resonant destruction — the same reason sunflowers use the golden angle to pack seeds without spatial overlap.

## Run the Analysis

```bash
pip install numpy scipy matplotlib
cd analysis/
python significance_test.py      # Monte Carlo significance test (10M runs)
python gait/analyze_gait_phi.py  # Gait analysis (requires PhysioNet data)
```

See individual script headers for data source instructions and dependencies.

## How to Falsify This

1. Find a free-running, self-timed, threshold-driven system with comparable phase durations whose ARA ratio is far from φ
2. Show the Monte Carlo clustering result is an artifact of the bin structure
3. Show the predictive structure (systems with known φ-deviation correlating with pathology) fails for a new system
4. Run the coupled-oscillator simulation from the temporal friction paper — if it doesn't converge to φ, the mechanism is wrong

## Author

**Dylan La Franchi** — independent researcher  
Contact: dylan.lafranchi@gmail.com

## License

CC-BY-4.0 — cite freely, build on it, tear it apart.

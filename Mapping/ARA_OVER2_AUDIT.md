# ARA Over-2 Audit

**Date:** 2026-05-24

Above-2 nodes are no longer treated as normal bounded ARA positions.
Each should be interpreted as a diagnostic until retested from source data or decomposed into subsystems.

## Summary

- Over-2 nodes: `45` / `234`
- **Fixed so far (recomputed from physics): `19` / `45`** — 3 quantum (2026-05-24) + 9 neural + 5 EEG + 2 laser (2026-05-30). Remaining `26` across fluid, astro, immune, colony/physiology clusters.
- Moderate `2..10`: `30`
- Extreme `>10`: `15`
- Inverse would fall inside `0..2`: `45`

By layer:

- `catalog`: `45`

Layer leakage check:

- No over-2 nodes found in: `mapped_extension`, `measured_fit`, `state_geometry`
- Current result: all above-2 nodes come from the older hand-curated catalogue layer.

By review class:

- `compound_biochemical_process`: `1`
- `extreme_snap_or_rung_mismatch`: `14`
- `moderate_overflow_review`: `30`

## Review Table

| Node | Layer | ARA | Inverse | Folded mod 2 | Review class | Recommendation |
|---|---|---:|---:|---:|---|---|
<!-- FIXED 2026-05-24 | U-238 Alpha | catalog_q_alpha | Original ARA 1.410e+38 was rung mismatch: catalog used half-life (4.47 Gyr) as period instead of nuclear oscillation period. Recomputed via classical trajectory in Woods-Saxon + Coulomb potential (velocity-Verlet). Corrected: period=5.386e-22 s, T_acc=2.679e-22 s (outward, KE→PE), T_rel=2.706e-22 s (inward, PE→KE), ARA=0.9901. Action/π=1.17e-34 J·s (~ℏ). Script: Mapping/quantum_u238_alpha_ara_test.py → Result: Mapping/quantum_u238_alpha_ara_result.json -->
<!-- FIXED 2026-05-24 | Na Fluorescence | catalog_q_na | Original ARA 4.780e+07 was rung mismatch: catalog divided natural lifetime by optical oscillation period of photon. Recomputed via optical Bloch equations (resonant two-level atom, multiple pump regimes). Corrected: period=1.624e-08 s (natural lifetime, intrinsic — pump is a coupled system), ARA=1.000000 (symmetric across all pump regimes). Script: Mapping/quantum_fluorescence_ara_test.py → Result: Mapping/quantum_fluorescence_ara_result.json -->
<!-- FIXED 2026-05-24 | H Lyman-alpha | catalog_q_lyman | Original ARA 2.360e+06 was rung mismatch: same error as Na. Recomputed via optical Bloch equations. Corrected: period=1.596e-09 s (natural lifetime, intrinsic), ARA=1.000000 (symmetric across all pump regimes). Script: Mapping/quantum_fluorescence_ara_test.py → Result: Mapping/quantum_fluorescence_ara_result.json -->
<!-- FIXED 2026-05-30 | HH Spike | catalog_ap_hh | Original ARA 3.0 was an orientation/rung mismatch. A neural spike is a SNAP (long rebuild, fast discharge), so ARA<1. Integrated Hodgkin-Huxley (HH 1952, modern -65mV convention, dt=5us, I=10 uA/cm^2 sustained): release(thr->peak)=0.245 ms, accumulation(repol+recharge to next threshold)=14.36 ms. ARA=T_rel/T_acc=0.0171. Script: Mapping/neural_ara_test.py -> Result: Mapping/neural_ara_results.json -->
<!-- FIXED 2026-05-30 | Depol/Repol | catalog_n_depol | Original ARA 2.14. Same HH spike, the two phases ARE the build/release directly: depolarisation 0.245 ms vs repolarisation+recovery 14.36 ms. ARA=0.0171. Script: Mapping/neural_ara_test.py -> Result: Mapping/neural_ara_results.json -->
<!-- FIXED 2026-05-30 | Refractory | catalog_n_refrac | Original ARA 3.33. HH single spike: release(thr->peak)=0.23 ms; accumulation = Na inactivation h-gate recovery to 0.9*rest = 9.25 ms. ARA=0.0249. Script: Mapping/neural_ara_test.py -> Result: Mapping/neural_ara_results.json -->
<!-- FIXED 2026-05-30 | Pyramidal 10Hz | catalog_ap_pyramidal | Original ARA 49.0. Regular-spiking cortical pyramidal cell: AP half-width ~1 ms (Bean 2007) = release; interspike recharge 99 ms at 10 Hz = accumulation. ARA=0.0101 (snap). Script: Mapping/neural_ara_test.py -> Result: Mapping/neural_ara_results.json -->
<!-- FIXED 2026-05-30 | FS Interneuron | catalog_ap_fs | Original ARA 30.25. Fast-spiking PV+ interneuron: half-width ~0.3 ms (Bean 2007), ~200 Hz => recharge 4.7 ms. ARA=0.0638 (snap). Script: Mapping/neural_ara_test.py -> Result: Mapping/neural_ara_results.json -->
<!-- FIXED 2026-05-30 | Ca2+ Spike | catalog_ap_ca | Original ARA 20.0. Broad L-type Ca2+ event: upstroke ~2 ms = release; plateau ~100 ms = accumulation. ARA=0.020 (ultra-snap). Script: Mapping/neural_ara_test.py -> Result: Mapping/neural_ara_results.json -->
<!-- FIXED 2026-05-30 | GABA IPSP | catalog_ap_ipsp | Original ARA 15.0. GABA_A conductance transient (not a regenerative spike): rise ~1 ms = build, decay tau ~6 ms = release. ARA=rise/decay=0.167. Script: Mapping/neural_ara_test.py -> Result: Mapping/neural_ara_results.json -->
<!-- FIXED 2026-05-30 | Thalamic Burst | catalog_ap_thal | Original ARA 13.33. Low-threshold T-type Ca2+ spike (LTS) envelope ~40 ms = accumulation, crowning Na spikelet ~1 ms = release. ARA=0.025. Script: Mapping/neural_ara_test.py -> Result: Mapping/neural_ara_results.json -->
<!-- FIXED 2026-05-30 | AMPA EPSP | catalog_ap_epsp | Original ARA 8.0. AMPA conductance transient: rise ~0.5 ms = build, decay tau ~3 ms = release. ARA=rise/decay=0.167. Script: Mapping/neural_ara_test.py -> Result: Mapping/neural_ara_results.json -->
<!-- FIXED 2026-05-30 | Delta 2Hz | catalog_eeg_delta | Original ARA 2.333 was an artifact: a rhythm is NOT exempt from ARA, every base cycle has a rising build and falling release. Measured waveform asymmetry on REAL EEG (PhysioNet slpdb slp01a, C4-A1, bycycle discipline: narrowband locates cycles, rise/decay timed on raw). Lands on the ARA~1 ridge: rise/decay ratio = 0.975 (order-unity, near-symmetric oscillator), NOT >2. CAVEAT: side of ridge is method-sensitive; robust claim = bounded ~1. Script: Mapping/eeg_ara_test.py -> Result: Mapping/eeg_ara_results.json -->
<!-- FIXED 2026-05-30 | Theta 6Hz | catalog_eeg_theta | Original ARA 2.976 was an artifact: a rhythm is NOT exempt from ARA, every base cycle has a rising build and falling release. Measured waveform asymmetry on REAL EEG (PhysioNet slpdb slp01a, C4-A1, bycycle discipline: narrowband locates cycles, rise/decay timed on raw). Lands on the ARA~1 ridge: rise/decay ratio = 0.818 (order-unity, near-symmetric oscillator), NOT >2. CAVEAT: side of ridge is method-sensitive; robust claim = bounded ~1. Script: Mapping/eeg_ara_test.py -> Result: Mapping/eeg_ara_results.json -->
<!-- FIXED 2026-05-30 | Alpha 10Hz | catalog_eeg_alpha | Original ARA 2.571 was an artifact: a rhythm is NOT exempt from ARA, every base cycle has a rising build and falling release. Measured waveform asymmetry on REAL EEG (PhysioNet slpdb slp01a, C4-A1, bycycle discipline: narrowband locates cycles, rise/decay timed on raw). Lands on the ARA~1 ridge: rise/decay ratio = 0.929 (order-unity, near-symmetric oscillator), NOT >2. CAVEAT: side of ridge is method-sensitive; robust claim = bounded ~1. Script: Mapping/eeg_ara_test.py -> Result: Mapping/eeg_ara_results.json -->
<!-- FIXED 2026-05-30 | Beta 20Hz | catalog_eeg_beta | Original ARA 2.571 was an artifact: a rhythm is NOT exempt from ARA, every base cycle has a rising build and falling release. Measured waveform asymmetry on REAL EEG (PhysioNet slpdb slp01a, C4-A1, bycycle discipline: narrowband locates cycles, rise/decay timed on raw). Lands on the ARA~1 ridge: rise/decay ratio = 0.889 (order-unity, near-symmetric oscillator), NOT >2. CAVEAT: side of ridge is method-sensitive; robust claim = bounded ~1. Script: Mapping/eeg_ara_test.py -> Result: Mapping/eeg_ara_results.json -->
<!-- FIXED 2026-05-30 | Gamma 40Hz | catalog_eeg_gamma | Original ARA 3.0 was an artifact: a rhythm is NOT exempt from ARA, every base cycle has a rising build and falling release. Measured waveform asymmetry on REAL EEG (PhysioNet slpdb slp01a, C4-A1, bycycle discipline: narrowband locates cycles, rise/decay timed on raw). Lands on the ARA~1 ridge: rise/decay ratio = 0.8 (order-unity, near-symmetric oscillator), NOT >2. CAVEAT: side of ridge is method-sensitive; robust claim = bounded ~1. Script: Mapping/eeg_ara_test.py -> Result: Mapping/eeg_ara_results.json -->
<!-- FIXED 2026-05-30 | Mode-locked | catalog_las_modelock | Original ARA 1.25e5 was the build/release ratio stored upside-down (inter-pulse pump time / pulse width). A pulsed laser is the textbook SNAP: store slowly in the gain medium, dump in an ultrafast pulse, so ARA<<1. Integrated the round-trip pulse dynamics (Haus master eqn, Ti:sapph class, 80 MHz). T_acc = cavity round-trip / inter-pulse pump = 1.251e-8 s; T_rel = pulse FWHM = 1.0e-13 s. ARA = T_rel/T_acc = 8.0e-6 (deep snap). Secondary reading: the intra-pulse sech² waveform itself is symmetric, rise/decay ARA = 1.000 (on the ridge). Script: Mapping/quantum_laser_ara_test.py -> Result: Mapping/quantum_laser_ara_result.json -->
<!-- FIXED 2026-05-30 | Q-switched | catalog_las_qswitch | Original ARA 2.0e4 was the build/release ratio stored upside-down. Q-switched laser stores inversion over the pump/upper-state window then dumps a giant pulse. Integrated the standard Q-switch rate equations (Nd:YAG class, sigma=2.8e-19 cm^2, tau_f=230 us): T_acc (inversion build, dE_total/dt>0) = 1.900e-4 s; T_rel (giant-pulse dump, dE_total/dt<0) = 8.40e-8 s. ARA = T_rel/T_acc = 4.42e-4 (deep snap). Secondary reading: the giant-pulse waveform is gain-saturation-skewed, rise/decay ARA = 0.758 (slightly snap-leaning, near ridge). Script: Mapping/quantum_laser_ara_test.py -> Result: Mapping/quantum_laser_ara_result.json -->
| `Old Faithful`<br>`catalog_fo_geyser` | `catalog` | 21.2500 | 0.0471 | 1.2500 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `Memory`<br>`catalog_imm_memory` | `catalog` | 21.0000 | 0.0476 | 1.0000 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `Brood Wave`<br>`catalog_col_brood` | `catalog` | 19.0000 | 0.0526 | 1.0000 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `Cell Cycle`<br>`catalog_dna_cell` | `catalog` | 14.7000 | 0.0680 | 0.7000 | `compound_biochemical_process` | Biochemical above-2 value likely mixes storage, processing, and release windows. Needs subsystem split. |
| `Annual Cycle`<br>`catalog_col_annual` | `catalog` | 12.0000 | 0.0833 | 0.0000 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `Cavitation`<br>`catalog_fl_cavit` | `catalog` | 10.0000 | 0.1000 | 0.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Dripping Faucet`<br>`catalog_fl_drip` | `catalog` | 9.0910 | 0.1100 | 1.0910 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Blink Cycle`<br>`catalog_td_blink` | `catalog` | 9.0000 | 0.1111 | 1.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `APRV`<br>`catalog_vent_aprv` | `catalog` | 9.0000 | 0.1111 | 1.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Saccade/Fix`<br>`catalog_td_saccade` | `catalog` | 7.8570 | 0.1273 | 1.8570 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Crab Emission`<br>`catalog_pl_crab` | `catalog` | 7.3750 | 0.1356 | 1.3750 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Complement`<br>`catalog_imm_complement` | `catalog` | 5.3330 | 0.1875 | 1.3330 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Neutrophil`<br>`catalog_imm_neutro` | `catalog` | 4.6670 | 0.2143 | 0.6670 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Halley's Comet`<br>`catalog_pl_halley` | `catalog` | 4.5560 | 0.2195 | 0.5560 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Breathing Bubble`<br>`catalog_dna_breath` | `catalog` | 4.3300 | 0.2309 | 0.3300 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Ant Foraging`<br>`catalog_col_ant_forage` | `catalog` | 3.0000 | 0.3333 | 1.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Ant Tandem`<br>`catalog_col_ant_tandem` | `catalog` | 3.0000 | 0.3333 | 1.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `555 (R1=2R2)`<br>`catalog_el_555b` | `catalog` | 3.0000 | 0.3333 | 1.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Adaptive`<br>`catalog_imm_adaptive` | `catalog` | 3.0000 | 0.3333 | 1.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Arm Passage`<br>`catalog_gx_arm` | `catalog` | 2.6700 | 0.3745 | 0.6700 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Ant Activity`<br>`catalog_col_ant_active` | `catalog` | 2.5000 | 0.4000 | 0.5000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Work Week`<br>`catalog_col_workweek` | `catalog` | 2.5000 | 0.4000 | 0.5000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `δ Cephei`<br>`catalog_pl_cepheid` | `catalog` | 2.3330 | 0.4286 | 0.3330 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Gastric Wave`<br>`catalog_td_gastric` | `catalog` | 2.3330 | 0.4286 | 0.3330 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Mayer Wave`<br>`catalog_td_mayer` | `catalog` | 2.3330 | 0.4286 | 0.3330 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Storm Lifecycle`<br>`catalog_ts_lifecycle` | `catalog` | 2.2400 | 0.4464 | 0.2400 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |

## Retest Rules

1. If `ARA > 2`, first ask whether the measurement is a true repeatable build/release cycle.
2. If it is a repeatable cycle, test the opposite orientation: `1 / ARA`.
3. If both sides are physical and coupled, split it into child subsystems before placing it on the bounded axis.
4. If it is a one-shot lifetime, decay, storage, or regime-change ratio, keep it on the diagnostic rail rather than the normal ARA band.
5. If it came from a fitted state or event extractor, rerun from the raw series and record the source window before changing the atlas coordinate.

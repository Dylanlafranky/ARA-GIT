# ARA Over-2 Audit

**Date:** 2026-05-24

Above-2 nodes are no longer treated as normal bounded ARA positions.
Each should be interpreted as a diagnostic until retested from source data or decomposed into subsystems.

## Summary

- Over-2 nodes: `45` / `234`
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
| `U-238 Alpha`<br>`catalog_q_alpha` | `catalog` | 1.410e+38 | 7.092e-39 | 0.0000 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `Na Fluorescence`<br>`catalog_q_na` | `catalog` | 4.780e+07 | 2.092e-08 | 0.0000 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `H Lyman-alpha`<br>`catalog_q_lyman` | `catalog` | 2.360e+06 | 4.237e-07 | 0.0000 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `Mode-locked`<br>`catalog_las_modelock` | `catalog` | 1.250e+05 | 8.000e-06 | 0.0000 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `Q-switched`<br>`catalog_las_qswitch` | `catalog` | 20000.0000 | 5.000e-05 | 0.0000 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `Pyramidal 10Hz`<br>`catalog_ap_pyramidal` | `catalog` | 49.0000 | 0.0204 | 1.0000 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `FS Interneuron`<br>`catalog_ap_fs` | `catalog` | 30.2500 | 0.0331 | 0.2500 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `Old Faithful`<br>`catalog_fo_geyser` | `catalog` | 21.2500 | 0.0471 | 1.2500 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `Memory`<br>`catalog_imm_memory` | `catalog` | 21.0000 | 0.0476 | 1.0000 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `Ca²⁺ Spike`<br>`catalog_ap_ca` | `catalog` | 20.0000 | 0.0500 | 0.0000 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `Brood Wave`<br>`catalog_col_brood` | `catalog` | 19.0000 | 0.0526 | 1.0000 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `GABA IPSP`<br>`catalog_ap_ipsp` | `catalog` | 15.0000 | 0.0667 | 1.0000 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `Cell Cycle`<br>`catalog_dna_cell` | `catalog` | 14.7000 | 0.0680 | 0.7000 | `compound_biochemical_process` | Biochemical above-2 value likely mixes storage, processing, and release windows. Needs subsystem split. |
| `Thalamic Burst`<br>`catalog_ap_thal` | `catalog` | 13.3330 | 0.0750 | 1.3330 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `Annual Cycle`<br>`catalog_col_annual` | `catalog` | 12.0000 | 0.0833 | 0.0000 | `extreme_snap_or_rung_mismatch` | Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured. |
| `Cavitation`<br>`catalog_fl_cavit` | `catalog` | 10.0000 | 0.1000 | 0.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Dripping Faucet`<br>`catalog_fl_drip` | `catalog` | 9.0910 | 0.1100 | 1.0910 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Blink Cycle`<br>`catalog_td_blink` | `catalog` | 9.0000 | 0.1111 | 1.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `APRV`<br>`catalog_vent_aprv` | `catalog` | 9.0000 | 0.1111 | 1.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `AMPA EPSP`<br>`catalog_ap_epsp` | `catalog` | 8.0000 | 0.1250 | 0.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Saccade/Fix`<br>`catalog_td_saccade` | `catalog` | 7.8570 | 0.1273 | 1.8570 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Crab Emission`<br>`catalog_pl_crab` | `catalog` | 7.3750 | 0.1356 | 1.3750 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Complement`<br>`catalog_imm_complement` | `catalog` | 5.3330 | 0.1875 | 1.3330 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Neutrophil`<br>`catalog_imm_neutro` | `catalog` | 4.6670 | 0.2143 | 0.6670 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Halley's Comet`<br>`catalog_pl_halley` | `catalog` | 4.5560 | 0.2195 | 0.5560 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Breathing Bubble`<br>`catalog_dna_breath` | `catalog` | 4.3300 | 0.2309 | 0.3300 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Refractory`<br>`catalog_n_refrac` | `catalog` | 3.3300 | 0.3003 | 1.3300 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `HH Spike`<br>`catalog_ap_hh` | `catalog` | 3.0000 | 0.3333 | 1.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Ant Foraging`<br>`catalog_col_ant_forage` | `catalog` | 3.0000 | 0.3333 | 1.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Ant Tandem`<br>`catalog_col_ant_tandem` | `catalog` | 3.0000 | 0.3333 | 1.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Gamma 40Hz`<br>`catalog_eeg_gamma` | `catalog` | 3.0000 | 0.3333 | 1.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `555 (R1=2R2)`<br>`catalog_el_555b` | `catalog` | 3.0000 | 0.3333 | 1.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Adaptive`<br>`catalog_imm_adaptive` | `catalog` | 3.0000 | 0.3333 | 1.0000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Theta 6Hz`<br>`catalog_eeg_theta` | `catalog` | 2.9760 | 0.3360 | 0.9760 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Arm Passage`<br>`catalog_gx_arm` | `catalog` | 2.6700 | 0.3745 | 0.6700 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Alpha 10Hz`<br>`catalog_eeg_alpha` | `catalog` | 2.5710 | 0.3890 | 0.5710 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Beta 20Hz`<br>`catalog_eeg_beta` | `catalog` | 2.5710 | 0.3890 | 0.5710 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Ant Activity`<br>`catalog_col_ant_active` | `catalog` | 2.5000 | 0.4000 | 0.5000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Work Week`<br>`catalog_col_workweek` | `catalog` | 2.5000 | 0.4000 | 0.5000 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Delta 2Hz`<br>`catalog_eeg_delta` | `catalog` | 2.3330 | 0.4286 | 0.3330 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `δ Cephei`<br>`catalog_pl_cepheid` | `catalog` | 2.3330 | 0.4286 | 0.3330 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Gastric Wave`<br>`catalog_td_gastric` | `catalog` | 2.3330 | 0.4286 | 0.3330 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Mayer Wave`<br>`catalog_td_mayer` | `catalog` | 2.3330 | 0.4286 | 0.3330 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Storm Lifecycle`<br>`catalog_ts_lifecycle` | `catalog` | 2.2400 | 0.4464 | 0.2400 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |
| `Depol/Repol`<br>`catalog_n_depol` | `catalog` | 2.1400 | 0.4673 | 0.1400 | `moderate_overflow_review` | Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung. |

## Retest Rules

1. If `ARA > 2`, first ask whether the measurement is a true repeatable build/release cycle.
2. If it is a repeatable cycle, test the opposite orientation: `1 / ARA`.
3. If both sides are physical and coupled, split it into child subsystems before placing it on the bounded axis.
4. If it is a one-shot lifetime, decay, storage, or regime-change ratio, keep it on the diagnostic rail rather than the normal ARA band.
5. If it came from a fitted state or event extractor, rerun from the raw series and record the source window before changing the atlas coordinate.

# 03 — System mapping & topology navigators

**Thread:** Mapping systems onto the ARA coordinate field and building "navigators" that walk a system's state through that field. Folder dated 10-05-26.

## Model logic / idea
Two complementary halves of the framework working together. The **inverse half** (build/consumer) reads a time series and extracts `(k, θ, ARA, amplitude)` for every pinned φ-rung. The **forward half** (release/engine) navigates that state via three operations: spin θ forward on the current rung, hop to rung k±1 (φ-rescale time, same shape), or add/remove a matched-rung partner. Mapping scripts place real systems' subsystems on a shared ARA map (rungs, boundaries, coupling class) so geometry can be diagnosed before forcing a forward formula.

## Systems tested
ENSO (NINO 3.4 + SOI matched-rung partner at φ⁸), ECG / heart (multiple map versions), solar, EQ (Sanriku), and a multispecies vertical-ARA comparison.

## What was tested
`time_topology_navigator.py` and `ecg_topology_navigator.py` (inverse extraction + forward projection at multiple horizons and neighbouring rungs, strict-causal); `map_heart.py`/`_v2`/`_v3` and `map_systems_v3.py` (run the hierarchical events_v4 formula across Solar/ENSO/EQ/ECG with scale-appropriate pump rungs); `horizontal_map_test.py` and `multispecies_vertical_ara_test.py` (cross-scale ARA mapping).

## Key results
No `.md` summaries; results in `*_data.js` and the multispecies HTML viz. The `map_systems_v3.py` docstring is candid about data sparsity: Solar 25 samples / 263 yr (fits richly), ENSO 23 samples / 74 yr (moderate), EQ only 10 samples / 130 yr (heavy overfit risk, basis functions tightly capped), ECG 200 samples / 145 s (full pipeline OK). These are mapping/diagnostic runs, not validated forecasts.

## What was NOT tested / open
Forward navigation is set up but not benchmarked against baselines here; the strict forecasting payoff is deferred to later threads (06–10). EQ mapping is explicitly flagged as unreliable due to sparsity.

## Key files
- `time_topology_navigator.py` — inverse extraction + forward rung navigation (ENSO)
- `ecg_topology_navigator.py` — same for cardiac data
- `map_systems_v3.py` / `map_heart_v3.py` — hierarchical formula across Solar/ENSO/EQ/ECG
- `multispecies_vertical_ara_test.py` — cross-species vertical ARA map

# 04 — Cross-system shape-matching atlas

**Thread:** An atlas of cross-system shape matches — do two analogous subsystems land at the same ARA class and share a cycle-shape template after time-rescaling? Folder dated 15-05-26.

## Model logic / idea
The framework predicts that systems sharing matched-rung topology should also share normalized cycle-shape templates once rescaled in time. Each test extracts an averaged, phase-normalized cycle from two systems, then compares them by Fourier-coefficient distance **against a panel of null candidates** — a match only counts if the target pair is the *smallest* distance. This explicitly guards against the sine-wave null failure mode (where two near-sinusoidal shapes correlate trivially high). `ara_mapper.py` is the canonical analyzer here: octave-rung decomposition, system ARA + class (snap/consumer/absorber/clock/engine/exothermic/harmonic), dominant period, and matched anti-phase partners.

## Systems tested
ECG↔ENSO, lightning↔neuron, lung↔forest, lungs/forests vertical ARA, forest succession, Cepheid coupled pair, ENSO↔MJO partner, mouse↔human (Kleiber/continuation), cancer oscillation, Earth↔human vital signs, Apollonian/Descartes geometry, and filter/decomposition method comparisons (Morlet vs Butterworth, log2 substrate, three-substrate topography).

## What was tested
Pairwise shape-match scripts (each with a null panel), the canonical `ara_mapper.py` and `ara_predictor.py`, decomposition-method sweeps (raw, pool, composition, filter comparison), and the Earth↔human classification/diagnostic.

## Key results
Results in `*_data.js`. The `ecg_enso_shape_match.py` docstring records the key null lesson: the prior lung↔forest match (gross corr +0.985) was **collapsed** by a pure-sine null (+0.995), so ECG↔ENSO was chosen precisely because the PQRST complex and asymmetric El Niño recovery are strongly non-sinusoidal. `earth_human_vital_signs.py` is a classification/diagnostic, not a forecast.

## What was NOT tested / open
No consolidated `.md`; per-pair pass/fail against the null panel lives in the data files. Whether shape matches translate into forecast skill is not addressed in this thread.

## Key files
- `ara_mapper.py` — canonical ARA decomposition + classification tool
- `ecg_enso_shape_match.py` — non-sinusoidal pair with explicit null panel
- `lung_forest_shape_match.py` — the sine-null failure case
- `earth_human_vital_signs.py` — Earth↔body subsystem ARA-class diagnostic

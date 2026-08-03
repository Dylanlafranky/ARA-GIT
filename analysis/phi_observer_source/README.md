# Observer–source Phi projection tests

This folder tests the interpretation that Phi belongs to the projected
relation between an observer, an independent source and an octave-separated
transfer path.

T323 is the first frozen pilot. It uses measured ARI acoustic impulse responses
so the source and receiver are independent rather than constructing a parent
that already contains its child.

T324 replaces the frequency octave with literal matched source radii at `0.5`,
`1`, `2`, and `3 m`. It tests both the observer-source projection angle and an
offset-invariant ratio of successive spatial phase increments.

## Reproduce T323

```powershell
python -m pip install -r requirements.txt
python t323_observer_source_octave_projection.py --fetch
python validate_t323_observer_source_octave_projection.py
```

## Reproduce T324

```powershell
python -m pip install -r requirements.txt
python t324_spatial_octave_observer_source.py --fetch
python validate_t324_spatial_octave_observer_source.py
```

The public SOFA files are checksum-locked and cached under ignored `data/`.
The isolated local `_deps/` directory is also ignored.

## Result

The frozen `36-degree` Phi prediction was not supported (`0/5` gates). Both
subjects selected the registered `54-degree` complementary target when the
stored impulse response was analyzed alone. Restoring the archive's separately
recorded measurement latency moved both results to the ordinary `45-degree`
pure-delay relation. See
`T323_OBSERVER_SOURCE_OCTAVE_PROJECTION_REPORT_2026-08-01.md`.

T324 was also not supported (`2/5` formal gates). The actual octave angles
were near `0 degrees`, not `36 degrees`, and the offset-invariant ratio was
near `0.15-0.23`, not Phi. The two passed gates were relative-ranking
artefacts, not absolute Phi proximity. The selected KEMAR archive also removes
or normalizes almost all literal distance time-of-flight: expected delay shifts
of roughly `64-129` samples appeared as only `0-5` stored samples. See
`T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_REPORT_2026-08-01.md`.

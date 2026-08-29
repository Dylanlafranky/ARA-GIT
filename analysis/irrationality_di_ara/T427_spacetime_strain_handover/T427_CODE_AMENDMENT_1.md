# T427 code amendment 1 — tuple/view handoff

The first all-event execution processed the frozen holdout waveforms and then
stopped before null scoring. `time_slide_null` expects each dictionary value
to be an event view, but the caller passed the `(detectors, view)` pair.

The caller was changed from passing each pair to passing `pair[1]`, the same
already constructed event view. No waveform, coordinate, normalization,
threshold, event, stage, control, gate or random seed changed. The failed run
produced no primary or null result. The corrected code is re-hashed before the
complete rerun.

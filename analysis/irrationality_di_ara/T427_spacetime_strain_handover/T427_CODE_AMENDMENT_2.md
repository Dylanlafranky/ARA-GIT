# T427 code amendment 2 — ineligible-lock report rendering

The corrected all-event execution completed every frozen holdout and null
calculation and wrote its result files. Report rendering then stopped because
all five events lacked a reclosure and the Information-lock records therefore
contained only `eligible`, `pass` and `reason`; the bar-chart code expected
numeric error columns that correctly had never been calculated.

The renderer now adds those absent columns as `NaN`. This displays the actual
result—no eligible lock windows—without inventing values. No waveform,
coordinate, normalization, threshold, event, stage, control, gate, random
seed or already calculated result changed. The analysis is re-hashed before
the final reproducibility rerun.

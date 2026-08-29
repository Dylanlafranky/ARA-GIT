# T450A pre-holdout selection correction

Status: recorded after the first development computation and before experiment-4 extraction or exposure.

The original support-only selector returned two nominal bands for every feature: 128 frames (about 1.28 s) and 512 frames (about 5.12 s). The larger band was largely inherited from fly nominations at the 1,024-frame outer boundary. At that scale a 60-second envelope has only five complete blocks, and its time-asymmetry statistic is consequently volatile.

The timestamp-permutation control confirmed the concern. Across the twelve nominal feature/rung combinations, only 2–8 of 24 individual envelopes exceeded their own 95th-percentile unordered null. The broad agreement across features could therefore be shared finite-window geometry rather than a shared biological parent rung.

No holdout data had been downloaded or read. The frozen correction is to null-calibrate every development boundary before fly nomination. A fly may nominate a boundary only when its median four-envelope observed score exceeds the corresponding median 95th-percentile timestamp-permutation null. This preserves all raw scale curves and the uncorrected shape, but prevents the enclosing 60-second window from manufacturing a child rung.

This is a methodological correction, not a change of identity, scale, medium or hypothesis.

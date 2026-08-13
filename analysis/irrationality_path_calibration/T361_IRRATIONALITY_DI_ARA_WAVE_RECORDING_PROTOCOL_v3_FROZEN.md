# T361 frozen protocol amendment v3 — causal four-state lookup

**Frozen:** 12 August 2026, before T361 outcome scoring  
**Active protocol chain:** v1 + v2 + this amendment

For causal recovery, the four direction states at reading `t` are defined by:

- the visible parent's outgoing direction `sign(x_A(t+1)-x_A(t))`; and
- the child's incoming direction `sign(x_B(t)-x_B(t-1))`.

The prefix recorder stores each child outgoing step `delta x_B(t)` under that causally available state. During recovery, the child's incoming direction is taken from its already reconstructed path. No hidden future child direction is supplied to the lookup.

This replaces the ambiguous v1 phrase “signs of the next parent and child steps” wherever the decoder is concerned. The four states remain the same paired direction possibilities; only their causal timestamp is made explicit.


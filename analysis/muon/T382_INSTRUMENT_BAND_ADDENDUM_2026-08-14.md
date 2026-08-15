# T382 instrument-band addendum

**Status:** FROZEN BEFORE RAW COUNT INSPECTION  
**Recorded:** 14 August 2026

The official ISIS EMU instrument documentation states an approximate measurable-frequency upper limit of `10 MHz`, caused by the finite pulsed-muon beam width. Applying the independently established muon field/cadence conversion only as a source-qualification bound places the 1000 G run above that instrumental response, even though it remains below the mathematical Nyquist limit of the 16 ns bins.

The primary untouched holdout is therefore narrowed before count inspection to:

- `EMU00066578` — 63 G;
- `EMU00066579` — 160 G;
- `EMU00066580` — 400 G.

`EMU00066581` at 1000 G joins the 2000 G and 4000 G runs as an instrument-band diagnostic and cannot enter any primary decision gate.

This change is based on published instrument bandwidth, not observed T382 outcomes. All other source splits, coordinates and gates remain fixed. With only three primary holdout fields, any positive pole-alignment result is explicitly a weak lead requiring same-medium replication.

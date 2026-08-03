# Thread 23 — three-tier ENSO state–inflow transport

T338 is the first ENSO test in this sequence whose identity tree was confirmed
by Dylan before the measurements and gates were frozen.

The frozen verdict is **MIXED**:

- ocean WWV redistribution → Niño3.4 passed at one month (`BAcc 0.6364`,
  95% interval `[0.6099, 0.6850]`);
- heat-content change separately reproduced the ocean direction more
  strongly (`0.7093`, `[0.6666, 0.7590]`);
- the nested inflow relation predicted movement of the compressed ENSO parent
  at two months (`0.6241`, `[0.5270, 0.6685]`);
- none of the three frozen trade-wind cuts passed the atmospheric-child gate.

The result supports an ocean-grandchild → ocean-child → ENSO-parent transport
path. It does not yet recover the corresponding atmospheric path. The regional
wind results are asymmetric rather than empty, so the next geometry question
is whether the atmospheric grandchild must be decompressed into ordered wind
and convection children before it can be followed upward.

Start with:

- `T338_ENSO_THREE_TIER_TRANSPORT_REPORT_2026-08-03.md`
- `T338_ENSO_THREE_TIER_TRANSPORT_PROTOCOL_v1_FROZEN.md`
- `T338_ENSO_THREE_TIER_TRANSPORT_VISUAL.svg`
- `T338_ENSO_THREE_TIER_TRANSPORT_VALIDATION.json`

Run with the bundled workspace Python:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 't338_enso_three_tier_transport.py'
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'validate_t338_enso_three_tier_transport.py'
```

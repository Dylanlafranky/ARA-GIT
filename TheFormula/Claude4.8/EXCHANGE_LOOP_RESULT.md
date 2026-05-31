# Exchange-channel closure test — Brown/Gold are NOT a clean phi-exchange pair (task #95)

**Date:** 2026-05-30  **Scripts:** `exchange_loop_test.py`, `exchange_loop_test2.py`
**Data:** NINO3.4 monthly anomaly, 1870–2026 (N=1872, 156 yr). RAW data rule.

## Claim under test (Dylan, 2026-05-30)
ENSO fails the P2 mix test BECAUSE it is the *exchange channel* (R/tether) between two
real A-systems — the GOLD/GREEN band [27.9, 30.7 mo] and the BROWN band [42.5, 54.0, 66.9 mo].
"The Brown/Gold meta-bands are the two systems' phi exchange rate." If true: each band
should build its own next rung (PASS the mix test), the two should be an anti-phase pair,
and their period ratio should be ~phi (1.618).

## Predictions (fixed before run)
P-a Brown PASS · P-b Gold PASS · P-c full NINO3.4 fail · P-d Brown↔Gold anti-phase + ratio≈phi.

## Result — claim NOT supported
| signature | predicted | measured | verdict |
|---|---|---|---|
| Brown:Gold period ratio | ≈phi (1.618) | **1.86** (15% high) | miss |
| Brown↔Gold phase | anti-phase (≈−1) | **+0.05** (weak) | miss |
| Gold×Brown → rung above (best of 4 targets) | clean PASS | z+2.0 but **lag −0.87** (≈full period = phase artifact, not on-time) | no |
| Brown×phi / beat / Gold×phi² builds | PASS | z +1.1 / +1.6 / +1.4 | fail |
| Gold/Brown beat = ENSO main band | strong | corr **+0.35** | weak |

(v1's "isolate each band then mix-test it" was a rigged method — bandpassing into a
narrow band removes the very next-rung-up frequency the test looks for. v2 fixes this by
running the mix on the full signal with r1,r2 = empirical gold/brown centers.)

## What DID reproduce
The one documented coupling survives: Gold+Brown **sum tone = 19.1 mo**, matching the
bispectrum's combination tone (15–20 mo, b²~0.34) noted in `ara_twoband_center.py`. So the
two bands ARE quadratically phase-coupled — but that coupling is a 19-mo sum tone, **not**
a phi-rate exchange that generates ENSO.

## Read
The exchange-channel *reading of ENSO* still rests on its original P2 evidence (recon high
+0.67, z only +0.7 → inherited, not built). But the specific mechanism — "ENSO = the
phi-exchange between a Brown A-system and a Gold A-system" — does NOT hold up: the two bands
aren't phi-spaced (1.86), aren't anti-phase (+0.05), and don't cleanly mix-build. The loop
does **not** close on Brown/Gold. So "we're predicting a shadow" may be right in spirit, but
this decomposition isn't the shadow's two casters. Where ENSO's exchange endpoints actually
live remains open — the cross-domain Jupiter/Saturn test (task #96) is the cleaner next probe.

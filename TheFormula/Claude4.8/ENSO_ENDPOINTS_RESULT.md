# TRUE exchange test on REAL ENSO channels — and a correction to the whole claim
Date: 2026-05-30. Data (all real, independently defined, NONE built by my filtering):
- ocean endpoint = WWV anomaly, PMEL/NOAA warm water volume (wwv_west.dat), 1980-2026, 556mo
- air endpoint   = SOI, CPC/NOAA Southern Oscillation pressure (soi.data), 1951-2026, ~900mo
- exchange/swap  = NINO3.4 SST anomaly (nino34.long.anom.csv), 1870-2025, 1872mo

## Prediction (exchange-channel reading of ENSO)
Two endpoints each BUILD their phi-tower (mix test PASS, z>=2); their surface swap NINO3.4
INHERITS structure (FAIL, z<2). dot(): r1,r2,r3 = P,P*phi,P*phi^2; z vs phase-randomized nulls.

## Result — NO clean split, and the claim's one leg is anchor-dependent
Fixed-anchor sweep, same rung for all three:
| anchor P | WWV ocean | SOI air | NINO3.4 (swap) |
|---|---|---|---|
| 24 mo | recon .90 z+2.0 (borderline) | recon .66 z+1.9 FAIL | recon .62 **z+3.4 PASS** |
| 28 mo | recon .93 z+1.8 FAIL | recon .56 z+1.2 FAIL | recon .52 z+2.0 |
| 33 mo | recon .57 z−0.1 FAIL | recon .28 z−1.2 FAIL | recon .42 z+1.1 FAIL |

The predicted endpoints did NOT reliably pass. The supposed EXCHANGE (NINO3.4) is the
strongest passer at the short rung.

## Crux check — "ENSO fails the mix test" is NOT robust (fresh seed, 80 nulls, full 156yr):
| P (mo) | 22 | 24 | 26 | 28 | 30 | 33 | 36 |
|---|---|---|---|---|---|---|---|
| NINO3.4 z | +2.9 | +3.2 | +2.5 | +1.9 | +1.5 | +1.2 | +0.5 |
| verdict | PASS | PASS | PASS | FAIL | FAIL | FAIL | FAIL |

NINO3.4 PASSES at the quasi-biennial rungs (22-26mo) and only FAILS at longer anchors
(>=28mo). The original P2 "NINO fails z+0.7" came from windowed segments at the welch-dominant
(longer) period — i.e. it was measured exactly where NINO fails. Shift the anchor a few months
and the same signal passes. So the fingerprint the exchange-channel claim rested on is fragile.

## Honest conclusion
The exchange-channel reading of ENSO ("it's a tether, so it correctly fails the phi mix test")
is NOT robustly supported. Across FOUR independent attempts the predicted endpoints-pass /
exchange-fails split never appeared:
  1. Brown/Gold ENSO meta-bands — not a phi pair (EXCHANGE_LOOP_RESULT.md)
  2. Jupiter/Saturn — integer-resonance clockwork, wrong lattice (EXCHANGE_ORBITAL_RESULT.md)
  3. Brain gamma envelope — "exchange" self-builds harder than endpoint (ENDPOINT_EXCHANGE_RESULT.md)
  4. Real ENSO ocean/air/swap channels — no split; and NINO passes at short rungs (this file)
Plus the original P2 fingerprint is anchor-dependent. RECOMMENDATION: retire / heavily caveat
the "ENSO is an exchange channel" claim. It was a clean story but the data does not carry it.
What survives: the mix test fires strongly and robustly only in biology (brain z+9.7); on
short, broadband climate signals it hovers near the null and flips with the anchor.

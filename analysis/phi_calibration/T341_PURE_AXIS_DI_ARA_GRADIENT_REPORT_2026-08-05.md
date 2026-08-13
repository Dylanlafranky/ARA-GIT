# T341 — pure-axis Di-ARA gradient result

**Run:** 5 August 2026  
**Protocol:** `T341_PURE_AXIS_DI_ARA_GRADIENT_PROTOCOL_v1_FROZEN.md`  
**Protocol SHA-256:** `61555C08A9B021076E46F4E9182D63FCBF2E6051D7B38970433B7CE59E89457E`  
**Cross-domain verdict:** **NOT SUPPORTED**

## Frozen question

Do mixed Di-ARA observations approach `1/e <-> e` at the pure radial/line axis, approach the golden non-closing turn at the pure angular/circle axis, and trade between those limits through one linear ARA budget?

## Holdout results

| Domain | line N | line median R (winner) | fixed/strong line | circle N | circle median turns (winner) | fixed/strong circle | target budget loss | shuffle p | joint |
|---|---:|---:|---|---:|---:|---|---:|---:|---|
| bubbles | 54 | 0.304699 (plastic) | no/no | 12 | 0.040131 (quarter) | no/no | 0.726642 | 1.000000 | no |
| qutrit | 20,942 | 1.016128 (e) | yes/no | 56,870 | 0.350769 (one_over_e) | no/no | 0.468418 | 0.510490 | no |
| river | 3 | 0.176488 (plastic) | no/no | 230 | 0.058777 (quarter) | no/no | 0.727242 | 1.000000 | no |

## Interpretation

The proposed universal pure-axis constants and one-budget interpolation were not jointly recovered in at least two real-data holdouts. The result distinguishes failure of those constants from failure of Di-ARA itself: each observation still has radial and angular participation and moves through their gradient.

The strongest component result is in the recorded qutrit holdout. Its 15-degree line cone gives `R=1.016128`, equivalent to `s=2.762479`; `e` is the closest fixed landmark and the absolute fixed gate passes. The tighter 10-degree cone moves still closer (`R=1.010681`). The strong transfer gate nevertheless remains failed because the calibration-fitted `R=1.025085` is slightly closer to the holdout median than exact `R=1`. On the circular side, qutrit gives `0.350769` turns: within `0.031197` of the golden target but closer to `1/e=0.367879`. Its radial and angular magnitudes are essentially uncorrelated (`rho=0.000180`), and shuffling their pairing does not worsen the target budget (`p=0.510490`). Thus the line limit is a real lead here, while the proposed coupled `e/Phi` gradient is not recovered.

Coverage is asymmetric in the other domains. The bubble holdout contains only `12` circle-cone events and the river holdout only `3` line-cone events, below the frozen eligibility floor. Their measurable opposite cones also sit far from the proposed constants. The cross-domain rejection is therefore decisive for the universal joint package, while the individual pure-axis limits still require datasets that actually visit both poles densely.

The four sign quadrants are not the tested discovery here. The load-bearing result is whether movement near each pure axis selects the frozen constant and whether intermediate magnitudes compensate event by event. A failed constant gate does not erase the already-established usefulness of the two-axis Di-ARA coordinate.

## Evidence boundary

All three archives were previously opened. This is a frozen new conditional question on inherited data, not a pristine discovery test. The 15-degree cones were fixed before the conditional medians were calculated.

## Reproduction

```powershell
$python = 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python analysis/phi_calibration/t341_pure_axis_di_ara_gradient.py
& $python analysis/phi_calibration/validate_t341_pure_axis_di_ara_gradient.py
```

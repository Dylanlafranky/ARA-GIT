# T369C post-result diagnostic - prompt-energy / neutron-connection branch

**Frozen:** 12 August 2026, after T369 showed an energy-led heatmap and T369B
rejected a prompt-time/first-neutron-time anti-diagonal, but before calculating
signed energy-branch statistics  
**Evidence class:** post-result diagnostic, not untouched confirmation

## Exact measurement

- **Who:** T369 holdout rows with a prompt child (`0<p<=15 MeV`, `1.1-5 us`).
- **What:** prompt-energy ARA coordinate versus observed neutron connection
  strength (`0`, `1`, `2+` tagged neutrons).
- **Where/when:** two released child records belonging to the same stopped
  muon-capture candidate.
- **Why:** test whether the visually strong branch is oppositely directed in
  energy/connection, rather than treating T369's failed timing score as an ARA
  reversal.
- **How:** development-frozen energy bins; signed rank correlation; all seven
  adjacent bin transitions; lowest/highest-bin contrast; neutron-packet
  shuffles within prompt-time bins; strict `5-15 MeV`; even/odd hash halves.

## Frozen interpretation

Call the branch **anti-directed in the released record** only if:

1. the signed rank correlation is negative with bootstrap 95% upper bound
   below zero;
2. at least six of seven adjacent energy-bin steps reduce neutron presence;
3. no more than 10/1,000 time-bin-preserving shuffles are as negative;
4. both hash halves and the strict `5-15 MeV` window retain the sign.

This does not by itself prove a pure ARA anti-phase identity. A pure mirror
would additionally require a calibrated continuous neutron-energy or
connection coordinate, which this detector release does not contain.


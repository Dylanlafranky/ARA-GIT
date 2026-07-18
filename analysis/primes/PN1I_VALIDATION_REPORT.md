# PN1I validation report

**Assessment:** `SHARE WITH CAVEATS — OPENED-RUNG DEVELOPMENT, INDEPENDENTLY REPRODUCED`

## What was validated

PN1I tested four predeclared views of the opened primorial-wheel hierarchy:

1. the next-prime deletion as a gate around a parent cycle;
2. the `q-1` surviving lifts as a maximum-base pyramid;
3. two incoming sides plus their ordered relation as an Information³ lock;
4. ordinary `0–2` ARA on adjacent gap pairs.

Prime 31 was prohibited by the protocol and was not generated or inspected. The development protocol SHA-256 was
`B713DAB0803545F201F2C712303E1C5E11BABC4538740381421AFF1BCBBE9F5C` when the analysis ran.

## Reproduction result

The primary implementation passed `36/36` deterministic assertions. A separately coded validator, which does not
import the primary implementation or its wheel generator and reconstructs the residues and lifted deletions by a
different route, passed `124/124` checks.

The independent checks cover:

- exact wheel sizes, residues, gaps and parent-to-child lift counts;
- exactly one deletion and `q-1` survivors per parent residue;
- absence of adjacent deletions;
- the excluded-lift modular recurrence and one-lift seam holonomy;
- equality of the gate ARA and the parent adjacent-gap ARA after the declared index shift;
- ridge mean and exact reflection counts;
- all stored held-out model scores and summary increments;
- the p29 aggregate crosswalk without constructing a p31 object;
- protocol hash, p31 access flag and readable figure dimensions.

## Findings safe to report

- The gate-label walk is an exact modular phase coordinate:
  `t*_(i+1)-t*_i = -P^(-1)g_i (mod q)`. Traversing the parent-cycle seam shifts the lift label by one, and `q`
  traversals close the label cycle.
- Every parent residue has the exact maximum base `q-1` after the one forbidden lift is removed.
- The ordinary gate ARA coordinate is exactly the parent wheel's adjacent-gap ARA coordinate under an index shift.
  Its whole-rung mean is exactly `1.0`, and reflected gap-pair counts are equal.
- For the non-overlapping two-step target, the ordered two-sided pair adds held-out information beyond the best
  left-only, right-only or merged-sum model from p13 through p23. At p23 the gain is `0.189765` bits/event, is
  positive in every fold and exceeds all declared target-permutation controls.
- Adding the removed-branch gate label to that pair does not help. Its held-out increment is negative on all six
  tested rungs and is `-0.007899` bits/event at p23.

## Important caveats

- These are method-locked analyses of already opened deterministic arithmetic data, not a prospective confirmation.
- Exact recurrence and symmetry results are mathematical calibration. They do not independently establish ARA as
  physical geometry.
- The Information³ model uses a declared 12-bin representation; p7 and p11 are too small for the larger state model,
  and bin sensitivity remains a follow-up.
- The gate's failure as an additional predictor is a real negative result. The supported interpretation is that it
  is a phase/singularity coordinate for this endpoint, not an independent fourth information source.
- The declining normalized child-wheel dependence is compatible both with distributed capstone support and ordinary
  convergence. The sealed PN1H p31 discriminator is unchanged.

## Reproducibility packet

- `PN1I_PRIME_PYRAMID_ARA_DEVELOPMENT_PROTOCOL.md`
- `pn1i_prime_pyramid_ara.py`
- `pn1i_independent_validator.py`
- `PN1I_PRIME_PYRAMID_ARA_REPRODUCIBILITY.ipynb`
- `PN1I_RESULTS.json`
- `PN1I_INDEPENDENT_VALIDATION.json`
- `PN1I_NOTEBOOK_EXECUTION_VALIDATION.json`
- `PN1I_PRIME_PYRAMID_ARA_REPORT.md`


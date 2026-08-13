# T344 — controlled weir Irrationality Di-ARA report

**Date:** 6 August 2026  
**Overall frozen result:** **PARTIALLY SUPPORTED**  
**Source:** BAW DOI [10.48437/99f329-73aee6](https://doi.org/10.48437/99f329-73aee6)

## Answer first

This archive supplied the test we were missing: thousands of objects physically moving
through a controlled weir at 0.01-second resolution. The result must be separated into
three claims:

1. **Complete local geometry:** Gate A = **PASS**.
2. **The intact two-child parent matters out of sample:** Gate B = **PASS**.
3. **The typed irrationality mechanism occupies the proposed middle regime:** Gate D =
   **FAIL**.

The coupling-asymmetry interaction gate is **PASS**. These
statuses are not averaged into a stronger claim.

## Plain-language reading

The particle movement was split into two native children at every time step: whether the
next movement grew or shrank, and whether it turned forward or back. Their intact pairing
was then asked to predict the next movement in a completely unseen water-level setting.
The comparison included each child alone, both children without an interaction, and a
false parent made by pairing children from different particles.

The irrationality test then asked for the specific ARA “middle”: coherent motion that
does not settle into a low-order closure should retain more future information than
random-like motion while continuing to traverse more effectively than closing motion.

## Frozen gate details

```json
{
  "A_four_sectors": {
    "pass": true
  },
  "B_intact_parent": {
    "pass": true,
    "components": {
      "intact_vs_radial_child": {
        "pass": true,
        "estimate": 0.04871605414820771,
        "ci": [
          0.0477881972096939,
          0.049577539989585924
        ],
        "fold_wins": 3
      },
      "intact_vs_turn_child": {
        "pass": true,
        "estimate": 0.059412386947160695,
        "ci": [
          0.05848782267060703,
          0.06036739055418077
        ],
        "fold_wins": 3
      },
      "intact_vs_broken_parent": {
        "pass": true,
        "estimate": 0.03725083525179384,
        "ci": [
          0.03653890838918501,
          0.03793381818985025
        ],
        "fold_wins": 3
      }
    }
  },
  "C_coupling_asymmetry": {
    "pass": true,
    "estimate": 0.005265957405350873,
    "ci": [
      0.005088264294214677,
      0.005456097627195339
    ],
    "fold_wins": 3
  },
  "D_structured_nonclosure": {
    "pass": false,
    "information_condition_effects": {
      "low": 0.002204910873440731,
      "medium": 0.005530123641953819,
      "high": -0.014507665053895412
    },
    "traversal_condition_effects": {
      "low": -0.3587067664001974,
      "medium": -0.3562022403418654,
      "high": -0.3677323859469719
    },
    "pooled_information": {
      "estimate": -0.0021871417873858133,
      "ci": [
        -0.010443347756405546,
        0.0033674103042391885
      ]
    },
    "pooled_traversal": {
      "estimate": -0.3608344781778842,
      "ci": [
        -0.3705013970021043,
        -0.3492050230692223
      ]
    }
  },
  "E_numerical_replication": {
    "status": "not_run_in_primary_stage"
  }
}
```

## Boundaries

- A finite trajectory cannot establish mathematical irrationality. The tested label is
  **structured non-closing**.
- The exact constants `Phi`, `1/Phi`, `e`, and `1/e` were secondary probes and could not
  rescue a failed primary gate.
- The numerical OpenFOAM trajectories remain a separate replication tier; they are not
  counted as extra laboratory observations.
- Approximately one quarter of laboratory tracks reportedly required some manual
  reconstruction. If the archive does not expose a per-track flag, that limitation
  cannot be removed retrospectively.

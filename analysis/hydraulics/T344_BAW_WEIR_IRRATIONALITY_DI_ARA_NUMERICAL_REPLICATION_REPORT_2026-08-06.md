# T344 — controlled weir Irrationality Di-ARA report

> **Numerical replication notice:** This artifact is the separately frozen
> numerical/OpenFOAM representation, not the laboratory result. The final
> cross-representation interpretation is in
> `T344_BAW_WEIR_IRRATIONALITY_DI_ARA_COMBINED_REPORT_2026-08-06.md`.

**Date:** 6 August 2026  
**Overall frozen result:** **PARTIALLY SUPPORTED**  
**Source:** BAW DOI [10.48437/99f329-73aee6](https://doi.org/10.48437/99f329-73aee6)

## Answer first

This archive supplied the test we were missing: thousands of objects physically moving
through a controlled weir at 0.01-second resolution. The result must be separated into
three claims:

1. **Complete local geometry:** Gate A = **PASS**.
2. **The intact two-child parent matters out of sample:** Gate B = **FAIL**.
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
    "pass": false,
    "components": {
      "intact_vs_radial_child": {
        "pass": false,
        "estimate": -0.11876455737185708,
        "ci": [
          -0.12048488502969153,
          -0.11710771172713197
        ],
        "fold_wins": 0
      },
      "intact_vs_turn_child": {
        "pass": true,
        "estimate": 0.014883211987043921,
        "ci": [
          0.0127420204415075,
          0.016943256326756386
        ],
        "fold_wins": 3
      },
      "intact_vs_broken_parent": {
        "pass": true,
        "estimate": 0.024063309579369467,
        "ci": [
          0.023442976879875555,
          0.02468757454199746
        ],
        "fold_wins": 3
      }
    }
  },
  "C_coupling_asymmetry": {
    "pass": true,
    "estimate": 0.024221892370270778,
    "ci": [
      0.02384177316274708,
      0.02459957141464463
    ],
    "fold_wins": 3
  },
  "D_structured_nonclosure": {
    "pass": false,
    "information_condition_effects": {
      "low": -0.0009149273197037966,
      "medium": -0.0012349317681077782,
      "high": -0.0001947621652231933
    },
    "traversal_condition_effects": {
      "low": -0.2469100451309469,
      "medium": -0.24054275140313197,
      "high": -0.23609641372104917
    },
    "pooled_information": {
      "estimate": -0.000778030236046005,
      "ci": [
        -0.00122664355699705,
        -0.00030082193431901826
      ]
    },
    "pooled_traversal": {
      "estimate": -0.24118307008504275,
      "ci": [
        -0.2450673916116231,
        -0.23716275135277823
      ]
    }
  },
  "E_numerical_replication": {
    "status": "replication_run_complete"
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

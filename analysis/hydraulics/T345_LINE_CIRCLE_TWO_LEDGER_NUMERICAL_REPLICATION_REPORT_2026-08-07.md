# T345 line–circle / two-ledger diagnostic report

**Date:** 7 August 2026  
**Representation:** num  
**Status:** frozen post-T344 diagnostic; not an independent confirmation  
**Protocol SHA-256:** `65770ca22b4be2cdca94eecbb976f31d139b9df30847bec509b26920f52a7a23`

## Answer first

Gates A/B/C/D: **PASS / FAIL / FAIL / FAIL**.

T345 separates path straightness from historical circularity and future movement
information from concentration in repeated ARA-sector relations. T344 remains frozen
and is not rescued by this diagnostic.

## Frozen component results

| Component | Pooled estimate | 95% whole-track CI | Direction wins | Verdict |
|---|---:|---:|---:|---|
| A1 structured minus random circularity | `0.172279` | `[0.163277, 0.177037]` | `3/3` | **PASS** |
| A2 closure minus structured directness | `0.241183` | `[0.236826, 0.245132]` | `3/3` | **PASS** |
| B1 closure minus structured connection | `-0.093919` | `[-0.103040, -0.086853]` | `0/3` | **FAIL** |
| B2 structured minus random connection | `0.458914` | `[0.439943, 0.472858]` | `3/3` | **PASS** |
| C circle-like minus crooked movement info | `-0.000233` | `[-0.000365, -0.000102]` | `0/3` | **FAIL** |
| D1 circle-like future connection change | `-0.082013` | `[-0.089674, -0.074048]` | `0/3` | **FAIL** |
| D2 circle-like minus crooked connection change | `-0.237813` | `[-0.248631, -0.226640]` | `0/3` | **FAIL** |

## Frozen gate composition

- Gate A — line/circle geometry: **PASS**.
- Gate B — connection-storage ladder: **FAIL**.
- Gate C — coherent curve versus random crookedness: **FAIL**.
- Gate D — delayed connection accumulation: **FAIL**.

## Boundaries

- Historical circularity is a conservative circulation score, not proof of a perfect circle.
- `I_conn` is relation-channel concentration relative to 16 uniform ordered ARA edges;
  it is not total thermodynamic information.
- `I_move` is realised information about one named future ARA movement address.
- The source was opened in T344. These results are diagnostic even though the new
  formulas and gates were frozen before T345 calculation.
- No exact irrational constant participates in a primary result.

## Artifacts

- `T345_LINE_CIRCLE_TWO_LEDGER_NUMERICAL_REPLICATION_FIGURE.png`
- `T345_LINE_CIRCLE_TWO_LEDGER_NUMERICAL_REPLICATION_CONTRASTS.csv`
- `T345_LINE_CIRCLE_TWO_LEDGER_NUMERICAL_REPLICATION_CLOSURE_SUMMARY.csv`
- `T345_LINE_CIRCLE_TWO_LEDGER_NUMERICAL_REPLICATION_PATH_SUMMARY.csv`
- `T345_LINE_CIRCLE_TWO_LEDGER_NUMERICAL_REPLICATION_SURFACE.csv`
- `T345_LINE_CIRCLE_TWO_LEDGER_NUMERICAL_REPLICATION_EXAMPLES.csv`
- `T345_LINE_CIRCLE_TWO_LEDGER_NUMERICAL_REPLICATION_RESULTS.json`

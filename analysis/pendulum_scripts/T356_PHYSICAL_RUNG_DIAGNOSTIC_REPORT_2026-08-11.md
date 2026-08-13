# T356 physical-rung diagnostic

**Date:** 11 August 2026  
**Frozen verdict:** **NOT SUPPORTED (`4/5` gates)**  
**Protocol SHA-256:** `77C74B1862B236320E0332BCA9C2835B213D52C67B4BAD947457572DD974D53A`

## Answer first

Across four public double-pendulum runs, the deeper arm did **repeat the cleaner central-flow pattern. Pooled median error was **0.029197** for arm 1 and **0.014545** for arm 2; midpoint flow retention was **0.984482** versus **0.978834**.

## Frozen gates

- `D1_depth_ordering`: **PASS**
- `D2_per_run_replication`: **PASS**
- `D3_clean_lower_ridge`: **PASS**
- `D4_flow_retention`: **FAIL**
- `D5_central_tendency`: **PASS**

## Run-level results

| Run | Arm | n | Median error | Midpoint flow | Median target phase |
|---|---:|---:|---:|---:|---:|
| double1 | 1 | 259 | 0.026480 | 0.985788 | 0.489091 |
| double1 | 2 | 268 | 0.018149 | 0.976938 | 0.508666 |
| double2 | 1 | 278 | 0.025226 | 0.988100 | 0.486413 |
| double2 | 2 | 287 | 0.014493 | 0.981568 | 0.502722 |
| double3 | 1 | 266 | 0.036497 | 0.977976 | 0.485744 |
| double3 | 2 | 244 | 0.019320 | 0.967448 | 0.502385 |
| double4 | 1 | 250 | 0.027027 | 0.984490 | 0.481013 |
| double4 | 2 | 257 | 0.010018 | 0.981042 | 0.502722 |

## Interpretation boundary

This addendum tests the post-T356 depth-split explanation and cannot alter T356's frozen `5/7` verdict. A pass supports a repeatable archive-specific pattern: the relational centre stays near phase `0.5`, while coupling redistributes which local flow crest becomes largest. It does not yet identify the complete parent mechanism or establish a universal rung law.

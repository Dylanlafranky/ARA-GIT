# T348 — Known-referee Irrationality path calibration

**Run date:** 11 August 2026  
**Evidence boundary:** synthetic known-referee instrument calibration only  
**Frozen benchmark verdict:** **SUPPORTED [synthetic known-referee instrument only]**  
**Geometry verdict:** **SUPPORTED AS A FOUR-SECTOR SYNTHETIC CALIBRATION, WITH A DETERMINISTIC-CHAOS LIMITATION**

## Technical summary

The frozen test passed all five preregistered gates. Across 1,104 untouched holdout paths, the fixed ARA ridge cuts at `x_P=1` and `x_R=1` assigned **95.65%** of paths to their expected broad sector. The macro-average across the five equally weighted families was **90.00%**.

This is a successful calibration of the proposed path/history measuring instrument. It shows that three label-blind readings calculated from raw ordered paths can separate the intended known synthetic distinctions:

- whether a path reuses a finite address set or keeps resolving new addresses;
- whether its next movement is relation-determined or remains stochastic after using the declared history;
- whether it carries coherent exact closure, coherent non-closing recurrence, or incoherent wandering across lags.

It does **not** yet show that nature universally uses this Di-ARA, that these estimators are unique, or that ARA generated the referee equations.

## What was measured

| ARA reading | Plain-language question | Frozen calculation |
|---|---|---|
| `x_P`, address openness | As we look more finely, does the path keep finding new usable locations, or reuse a limited set? | Twice the clipped log–log slope of occupied circular bins across 16, 32, 64, 128 and 256 bins. |
| `x_R`, stochastic residual | After learning the first half of the ordered path, how much of the next movement remains unexplained? | Twice the causal nearest-neighbour circular loss divided by a matched no-history loss, capped at 2. |
| `C(H)`, closure history | Across increasing lags, does the path exactly close, coherently miss, or lose directional coherence? | The retained complex lag relation, reported as coherence and angular miss without compressing it into either scalar coordinate. |

The two scalar coordinates form a Di-ARA plane:

| `x_R` \ `x_P` | finite/reused side | open/resolving side |
|---|---|---|
| relation-determined side | periodic rational reference | irrational rotation and deterministic-chaos references |
| stochastic-residual side | finite stochastic reference | continuous stochastic reference |

The endpoints are pure reference identities. They are not a demand that every empirical system land exactly on a corner.

## Holdout results

| Known referee | Median `x_P` | Median `x_R` | Median closure coherence | Broad-sector accuracy |
|---|---:|---:|---:|---:|
| periodic rational | 0.000 | 0.000 | 1.000 | 100% |
| irrational rotation | 2.000 | 0.0000014 | 1.000 | 100% |
| deterministic chaos | 1.497 | 0.000067 | 0.050 | 50% |
| finite stochastic | 0.000 | 2.000 | 0.013 | 100% |
| continuous stochastic | 1.978 | 2.000 | 0.110 | 100% |

The result cleanly separates irrational rotation from randomness. Both irrational rotation and continuous stochastic motion keep opening addresses, but their history relation is opposite: the rotation is almost perfectly predictable from its prior ordered path, while the continuous stochastic process retains the full stochastic residual.

The retained closure history supplies information that the two-coordinate parent does not flatten away. Periodic and irrational rotations both have coherence approximately 1, but periodic paths contain exact closure by lag 64. Irrational rotations contain no exact closure and improve their nearest coherent miss as the lag search expands from 64 to 512 in **100%** of holdouts. Chaos and both stochastic families have low median closure coherence.

## Frozen gates

| Gate | Frozen requirement | Result |
|---|---|---|
| G1 | family median address-openness orientation | **PASS** |
| G2 | family median stochastic-residual orientation | **PASS** |
| G3 | at least 85% untouched broad-sector recovery | **PASS — 95.65%** |
| G4 | closure history separates exact, coherent non-closing and incoherent paths | **PASS — irrational improvement 100%** |
| G5 | destroying chronology removes determinacy/closure without changing support openness | **PASS** |

For the three ordered deterministic families, shuffling increased median `x_R` by `+1.974`, `+1.973` and `+2.000` respectively, while median `x_P` changed by `0.000`. That is an especially useful control: the same visited values remained, but their historical relation was destroyed. The instrument put the change on the history axis rather than falsely moving the address-support axis.

## Important limitation: the chaos split

The overall 95.65% result is not the whole story. One held-out deterministic expanding-map parameter group occupied a lower-dimensional open set whose `x_P` readings ranged from about 0.784 to 0.993. It therefore fell below the preregistered ridge `x_P=1`, while the second chaotic parameter group landed at `x_P=2`. Deterministic chaos consequently achieved only **50%** broad-sector accuracy.

This does not erase the frozen pass: G1 was explicitly a family-median orientation gate and G3 was explicitly an all-path accuracy gate. It does establish a boundary for the instrument. The present `x_P` coordinate measures support-growth dimension, not a universal binary synonym for “non-finite.” A low-dimensional deterministic chaotic path can be genuinely non-closing while remaining on the finite-leaning side of this fixed coarse ridge.

That is also an ARA-compatible reading: the sectors behave as gradients, and closure history remains necessary. It prevents us from claiming that the two scalar coordinates alone classify every identity.

## Interpretation in ARA terms

The cleanest supported translation is:

1. The first ARA distinguishes **reused connection addresses** from **continued address opening**.
2. The perpendicular ARA distinguishes **movement preserved by ordered relation** from **movement not recovered by that relation**.
3. Their Di-ARA makes structured irrational non-closure distinguishable from both rational closure and stochastic wandering.
4. `C(H)` is the uncompressed child/history structure. It distinguishes paths that share the same parent quadrant but reach it through different internal geometry.

The calibration therefore supports the proposed navigator concept at the instrument level: “open” does not have to mean “random.” A path can keep opening new addresses while retaining a strong, reusable movement relation. That is exactly the quadrant occupied by the irrational-rotation referee.

## Reproduction and validation

The run used 2,016 fixed-seed paths of length 4,096, producing 912 calibration paths and 1,104 untouched holdout paths. No family label, generator parameter, known period, Phi, `e`, radial-amplitude cut or fitted identity-specific constant entered the coordinate calculations.

Run:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'analysis\irrationality_path_calibration\t348_known_referee_irrationality_path.py'
```

Independent artifact validation:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'analysis\irrationality_path_calibration\validate_t348_known_referee_irrationality_path.py'
```

The validator independently recomputed all five gates, checked every natural key and coordinate range, verified both frozen SHA-256 records, verified image artifacts, and reproduced the 95.65% overall and 90.00% macro-family accuracies. Every validation check passed.

## Recommended next rung

The next test should transfer the frozen instrument unchanged to a controlled public physical system with documented periodic, quasiperiodic, chaotic and noise-dominated regimes. A forced nonlinear oscillator dataset is the cleanest next referee because the regimes are externally identified while the ARA coordinates can remain label-blind.

The next protocol should freeze the physical observable and circular/path mapping before opening the outcome labels. It should require correct regime ordering, chronology-destruction controls and transfer to an untouched forcing range. Only that would begin moving this result from synthetic instrument calibration toward empirical evidence about physical systems.

## Artifact index

- Frozen claim: `T348_IRRATIONALITY_PATH_KNOWN_REFEREE_CLAIM_PACKET_v1.md`
- Frozen protocol: `T348_IRRATIONALITY_PATH_KNOWN_REFEREE_PROTOCOL_v1_FROZEN.md`
- Complete coordinate rows: `T348_IRRATIONALITY_PATH_METRICS.csv`
- Complete closure rows: `T348_IRRATIONALITY_CLOSURE_SUMMARY.csv`
- Closure curves: `T348_IRRATIONALITY_CLOSURE_CURVES.csv`
- Family summary: `T348_IRRATIONALITY_FAMILY_SUMMARY.csv`
- Frozen gates: `T348_IRRATIONALITY_FROZEN_GATES.csv`
- Machine-readable verdict: `T348_IRRATIONALITY_PATH_RESULTS.json`
- Independent validation: `T348_IRRATIONALITY_PATH_VALIDATION.md` and `.json`
- Main visual: `T348_IRRATIONALITY_PATH_FIGURE.png`
- Descriptive circle traces: `T348_IRRATIONALITY_CIRCLE_EXAMPLES.png`

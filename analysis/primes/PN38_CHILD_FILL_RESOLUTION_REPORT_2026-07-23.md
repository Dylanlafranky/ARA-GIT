# PN38 — Child-Fill Resolution Sensitivity Result

**Date:** 2026-07-23  
**Status:** post-hoc structural sensitivity analysis  
**Population:** 45,166 parent primes and 286,253,917 complete child relations

## Result

The mean occupancy at every resolution is exactly the compulsory partition value `2/B`. It therefore moves when the analyst changes the number of bins and is not a discovered ARA landmark.

The table below reports residual structure after subtracting the exact gate-conditioned nonzero-residue expectation.

| bins | forced mean share | forced occupancy ARA | adjusted TV | adjusted RMS relative residual | mirror correlation | first/second-half residual correlation |
|---:|---:|---:|---:|---:|---:|---:|
| 80 | 1.250000% | 0.02500000 | 0.00019037 | 0.000482 | -0.114709 | -0.224965 |
| 120 | 0.833333% | 0.01666667 | 0.00023516 | 0.000599 | -0.045150 | -0.144205 |
| 160 | 0.625000% | 0.01250000 | 0.00028181 | 0.000688 | -0.089081 | -0.106610 |
| 180 | 0.555556% | 0.01111111 | 0.00028466 | 0.000720 | -0.025367 | -0.084563 |
| 320 | 0.312500% | 0.00625000 | 0.00036773 | 0.000914 | 0.009966 | -0.081582 |
| 360 | 0.277778% | 0.00555556 | 0.00038706 | 0.000962 | -0.048270 | -0.084316 |

## Cross-resolution residual correlation

Each residual profile is repeated over its exact cells on the common 2,880-cell ruler. These are descriptive correlations of differently smoothed views of the same child field, not independent replications.

| bins | 80 | 120 | 160 | 180 | 320 | 360 |
|---:|---:|---:|---:|---:|---:|---:|
| 80 | 1.0000 | 0.7034 | 0.7002 | 0.6248 | 0.5267 | 0.4964 |
| 120 | 0.7034 | 1.0000 | 0.6965 | 0.7542 | 0.5880 | 0.6227 |
| 160 | 0.7002 | 0.6965 | 1.0000 | 0.6954 | 0.7524 | 0.6156 |
| 180 | 0.6248 | 0.7542 | 0.6954 | 1.0000 | 0.6435 | 0.7486 |
| 320 | 0.5267 | 0.5880 | 0.7524 | 0.6435 | 1.0000 | 0.6905 |
| 360 | 0.4964 | 0.6227 | 0.6156 | 0.7486 | 0.6905 | 1.0000 |

The residual sign is the same at all six resolutions across **41.111%** of the common ruler.

## Conclusion

The compulsory fill rule is confirmed: changing `B` moves the mean exactly as `2/B`. After the stronger gate-conditioned correction, only **0.019% to 0.039%** of probability mass must be redistributed to match the exact baseline, and the RMS relative residual is **0.048% to 0.096%** across the frozen resolutions.

The residual views remain moderately related across resolutions (`r = 0.4964` to `0.7542` off the diagonal), which shows that rebinning does not manufacture wholly unrelated pictures. However, every consecutive-half correlation is negative (`r = -0.2250` to `-0.0816`). The residual therefore does not recur as a stable same-orientation grandchild profile across this interval. A moving or flipping profile is not ruled out, but it was not predeclared here and cannot be inferred from the negative correlations alone.

## Interpretation rule

- A high cross-resolution correlation alone shows that coarse and fine histograms retain related departures; it does not establish a new wave because the same observations underlie every resolution.
- The consecutive-half correlation is the more important recurrence check. Strong positive values would support a stable residual shape; weak, zero, or negative values would indicate that the apparent fine structure is not reproducible across the interval.
- Even a stable residual remains a number-theoretic distribution pattern until it predicts an untouched interval or beats the exact gate-conditioned control on a frozen endpoint.

## Reproduction

Run:

```powershell
python analysis/primes/pn38_child_fill_resolution_sensitivity.py
```

Machine-readable output: `PN38_CHILD_FILL_RESOLUTION_RESULTS.json`.

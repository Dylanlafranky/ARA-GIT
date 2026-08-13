# T343 — intact-versus-broken Di-ARA parent coupling

**Run:** 5 August 2026  
**Frozen verdict:** **NOT SUPPORTED BY THIS CONSTRUCTION**  
**Eligible/pass:** `6` eligible, `1` pass

## Result first

The intact Di-ARA parent passed all child-only and broken-pair gates in 1/6 eligible domains. The frozen cross-domain verdict is **NOT SUPPORTED BY THIS CONSTRUCTION**.

T343 allowed every domain its own complete `4×4` movement relation. It did not require adjacency, clockwise movement, one cadence or one universal quadrant order.

## Holdout results

| domain | parent loss | radial child | angular child | broken median | Δ radial | Δ angular | Δ broken | p broken | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| acoustics | 1.668691 | 1.479019 | 1.597034 | 1.535172 | -0.189672 | -0.071657 | -0.133519 | 1.0000 | NO PASS |
| bubbles | 1.407987 | 1.488975 | 1.485085 | 1.341047 | +0.080988 | +0.077097 | -0.066941 | 0.7333 | NO PASS |
| cold_room | 0.843298 | 1.169491 | 1.128782 | 0.918997 | +0.326193 | +0.285484 | +0.075700 | 0.1229 | NO PASS |
| hydraulic | 2.694074 | 3.034419 | 2.664689 | 2.696608 | +0.340345 | -0.029386 | +0.002533 | 0.4995 | NO PASS |
| pendulum | 1.393717 | 1.282200 | 1.268807 | 1.258104 | -0.111517 | -0.124910 | -0.135613 | 1.0000 | NO PASS |
| qutrit | 1.245377 | 1.297092 | 1.335548 | 1.305645 | +0.051715 | +0.090171 | +0.060268 | 0.0060 | PASS |
| river | 1.227355 | 1.394638 | 1.269535 | 1.385312 | +0.167283 | +0.042180 | +0.157957 | 0.0679 | INELIGIBLE |

Positive deltas favour the intact parent. Parent-versus-child p-values use 10,000 sign flips of non-overlapping block means. Broken-pair p-values use 1,000 circular shifts of one ARA axis inside every frozen block.

## What is load-bearing

Passing domains: qutrit. Eligible non-passing domains: pendulum, hydraulic, bubbles, cold_room, acoustics. A pass means the intact joint address transferred more future-state information than both one-axis projections and at least 95% of matched broken pairings.

The four-region map and TE-ARA complements remain geometric bookkeeping. The empirical result is the out-of-sample information advantage, or lack of it, over same-data controls.

## Evidence boundary

This is a frozen cross-question test on the T342 source battery, not an untouched-source discovery. Two pre-score addenda corrected the measured child rung and the inference unit before any T343 endpoint was calculated. Named lineages are reported; block-level inference remains a dependence caveat for future independent replication.

Exact `e`, Phi and anti-Phi locations were excluded from scoring. T343 tests whether the two declared axes couple, not whether their numerical landmarks are universal.

## Post-result control audit

A later data-quality audit found that the registered circular shifts can wrap later native axis values into earlier predictor states. The frozen `1/6` score remains unchanged, but its broken-pair gate is not a leakage-free causal test. A past-only/no-wrap matched sensitivity passed in bubbles, cold room and qutrit—the same three eligible domains that beat both one-axis children. That `3/6` pattern is post-result and cannot replace or rescue T343; it requires a new frozen replication. See `T343_BROKEN_CONTROL_TEMPORAL_LEAKAGE_AUDIT_REPORT_2026-08-05.md`.

## Reproduction

```powershell
$env:PYTHONPATH='analysis/irrationality_te_ara_multimedium/vendor'
& 'C:/Users/Dylan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' analysis/irrationality_te_ara_multimedium/t343_intact_vs_broken_di_ara_parent_coupling.py
& 'C:/Users/Dylan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' analysis/irrationality_te_ara_multimedium/validate_t343_intact_vs_broken_di_ara_parent_coupling.py
```

# T346 independent saved-artifact validation

**Date:** 9 August 2026  
**Frozen protocol SHA-256:** `205f48d722b80e59f3d0c766790c1ecfeabbf7eac50f3f644590301e1fdda512`  
**Verdict:** PASS

The validator independently reconstructed all stored Gates A-C, all eligible
summary estimates, every 1,000-member broken-lineage p-value, official source
hash flags, and the cross-representation Gate-D comparison.

- Laboratory primary Gates A/B/C: `{'A': False, 'B': False, 'C': False}`.
- Numerical primary Gates A/B/C: `{'A': False, 'B': False, 'C': True}`.
- Gate D: `FAIL`.

This is a saved-artifact validator. The public reproducer performs the raw
source-event recomputation; the two are kept separate so the validator does not
simply trust the result JSON's declared verdicts.

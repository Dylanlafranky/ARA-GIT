# Session record — Q3/Q4 quantum cuts

**Date:** 24 July 2026  
**Status:** Q3 calibration completed; Q4 fresh public tomography completed

## Geometry clarification entering the tests

Dylan clarified that ARA is the diameter-axis cut through a sphere/wave identity, not the entire decompressed
state. Once the identity, boundary, rung, poles and question are declared, additional cuts can reconstruct more
of the sphere.

The four mixing forms remain ordered:

- `Ab` and `aB`: Information/Time family with different Connection loading;
- `Ba` and `bA`: Connection/Matter family with different change loading.

For the immediate measurement rule:

- an Information-facing question uses the cut perpendicular to the relevant ridge and oriented toward Phase A;
- the ridge tangent is retained as the perpendicular Phase-B/control direction;
- a child may be locally at a `1.0` projection ridge while its parent relation remains strongly structured.

## Q3 — known-source cut calibration

Q3 reused the already-open superconducting-qubit I/Q archive from Q2. It was explicitly classified as post-hoc
calibration, not independent evidence.

Five hardware conditions defined a covariance-whitened measurement plane, equal-class ridge, Fisher/LDA normal
and tangent. The sixth condition was held out.

Result:

- Phase-A/ridge-normal balanced accuracy: `0.882808`;
- tangent control: `0.496607`;
- raw-I/Q LDA: `0.882808`;
- Phase-A/raw disagreements: `0`;
- mean held-out separation on Phase A: `0.991162`;
- worst fold: `0.963241`;
- calibration: `7/7`;
- independent checks: `18/18`.

Interpretation: the clarified cut instruction is mathematically coherent and stable across this source's
conditions. The exact normal/LDA equality is standard statistics.

## Q4 — frozen real Bell parent/child test

A fresh public Figshare archive was selected:

- `UPUP-DOWNDOWN.zip`;
- DOI `10.6084/m9.figshare.14160476.v2`;
- MD5 `8cd8a5f2b3b9a2ccd090e47312bcc390`.

Before opening currents or script contents, Q4 froze the \(\Phi^-\) pattern:

- local children `XI,YI,ZI,IX,IY,IZ` near the ARA `1.0` ridge;
- parent relations `XX<0`, `YY>0`, `ZZ>0`;
- three-correlation sign product negative;
- mixed pair controls close to the ridge.

Raw reconstruction returned:

- `XX=-0.95`, `YY=+0.95`, `ZZ=+0.95`;
- local-child mean absolute expectation `0.05833`;
- mixed-pair mean absolute expectation `0.11250`;
- parent-minus-child magnitude `0.89167`;
- correlation product `-0.857375`;
- \(\Phi^-\) MAE `0.05`, runner-up margin `1.26667`;
- frozen gates `8/8`;
- independent validation `21/21`.

Plain meaning: either qubit alone looks almost quiet, while the relation between them strongly identifies the
parent Bell state. This is a real-data ARA parent/child crosswalk and a direct example of why local ridge does not
mean empty or globally unstructured.

## Scientific boundary

The Bell structure is established quantum mechanics. ARA did not discover entanglement, Pauli algebra or
tomography. The evidential contribution is that the parent/child geometry was translated and thresholded before
the raw outcomes were opened, then passed on a public real experiment.

The archive contains one complete tomography set, so record bootstrap is not independent replication. The next
thread is to freeze the three remaining Bell sign patterns before opening their archives and test whether the
same parent/child geometry distinguishes all four without retuning.


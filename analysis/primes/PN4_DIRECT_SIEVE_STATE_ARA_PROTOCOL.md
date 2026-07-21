# PN4 direct sieve-state ARA protocol

**Test ID:** `PN4/DIRECT-SIEVE-STATE/OPENED-DEVELOPMENT-v1`  
**Protocol written:** 19 July 2026  
**Epistemic status:** retrospective development on already opened R6-R9 data; not fresh confirmation  
**PN1H boundary:** the sealed p31 wheel-capstone packet is not read, modified or opened

## Question

Does the direct survivor/release state of the p29-conditioned sieve, measured on the ARA 0-2 diameter, transfer
from one decimal rung to the next? Does retaining the explicit relation between single-candidate survival and
adjacent-pair survival improve the transfer?

This test deliberately avoids Fourier transforms, SVD, NMF and outcome-derived future-gate features. It starts from
the exact smallest-factor/death-gate arrays already reconstructed and validated by PN3A.

## Data and split

- Source: `PN3A_ADULT_SIEVE_DIAGNOSTIC_DATA.npz`.
- R6: `[1,000,000,1,010,000)`.
- R7: `[10,000,000,10,100,000)`.
- R8: `[100,000,000,101,000,000)`.
- R9: `[1,000,000,000,1,010,000,000)`.
- R6-R8 are development rungs.
- R9 is held out by the PN4 code path, but it was opened by earlier tests. Results are therefore retrospective
  transfer evidence only.

The path is divided into 24 fixed cells of equal normalized log-gate progress,

\[
t(q)=\frac{\log(q/31)}{\log(q_{\max}/31)}.
\]

The cell count is fixed here before PN4 execution. It is large enough to show path shape while retaining useful R6
event counts. Boundaries depend only on the sieve gates and rung limit, never on survival labels.

## Direct ARA coordinates

At cell endpoint \(j\),

\[
S_j=\frac{N_j}{N_0},\qquad R_j=1-S_j,\qquad x_j=2R_j.
\]

Here \(x=0\) means no members of the declared starting population have yet been released by later sieve gates, and
\(x=2\) would mean all have been released. In this test, \(x=1\) means 50% occupancy release only. It is not by
itself evidence of physical cancellation or resonance.

For candidate survival \(S_c\) and adjacent-pair survival \(S_e\), retain the coupling relation

\[
J_j=\log\!\left(\frac{S_{e,j}}{S_{c,j}^2}\right).
\]

\(J=0\) is the independent-pair reference. This is an explicit two-identity-plus-relation representation; it is not
manufactured by counting three consecutive readings.

## Frozen transfer rules

All paths below are constructed without R9 outcomes.

### Candidate paths

1. **Independent sieve:** exact product \(S_{c,\mathrm{ind}}=\prod_{31\le q\le Q}(1-1/q)\).
2. **ARA same-form residual:** transfer the R8 displacement on the 0-2 line,
   \(x_{9}=x_{9,\mathrm{ind}}+(x_{8}-x_{8,\mathrm{ind}})\).
3. **ARA two-rung residual:** \(e_9=2e_8-e_7\), where \(e=x-x_{\mathrm{ind}}\).
4. **Raw multiplicative ratio:**
   \(S_{9}=S_{9,\mathrm{ind}}(S_8/S_{8,\mathrm{ind}})\).
5. **Raw two-rung ratio:** extrapolate the log survival ratio from R7 and R8.

The ARA same-form residual is algebraically equivalent to additive survival-residual transfer because
\(x=2(1-S)\). That equivalence is a required calibration statement, not a hidden advantage claim.

### Adjacent-pair paths

1. **Independent pair:** \(S_{e,\mathrm{ind}}=S_{c,\mathrm{ind}}^2\).
2. **Direct ARA edge residual:** transfer the R8 edge displacement on the 0-2 line.
3. **Coupled ARA relation:** combine the candidate same-form path with retained R8 relation,
   \(S_{e,9}=S_{c,9}^2\exp(J_8)\).
4. **Coupled ARA relation-gradient:** use \(J_9=2J_8-J_7\) with the two-rung candidate path.
5. **Raw multiplicative edge ratio:** transfer \(S_e/S_{e,\mathrm{ind}}\).

Every predicted path is clipped only for numerical validity and forced to be non-increasing. Any clipping is counted
and reported.

## Secondary strictly causal probe

Within each rung, after two completed cells, the next cumulative ARA coordinate is predicted by the local secant

\[
\widehat x_{j+1}=x_j+(x_j-x_{j-1}).
\]

This three-point ARA stencil is compared with last-hazard Home and the independent next-cell gate product. It uses
only earlier cells from the same rung. It is not called Information^3.

## Scoring and decision rules

Primary scores are:

- binomial log loss in bits per at-risk event for the 24 cell hazards derived from each full transferred path;
- survival-path RMSE across the 24 endpoints;
- absolute terminal relative error.

The following prewritten criteria are reported separately for candidate and edge paths:

- `C1`: R9 ARA same-form candidate log loss beats independent sieve and raw multiplicative-ratio transfer.
- `C2`: R9 coupled-ARA edge log loss beats independent pair, direct edge residual and raw edge-ratio transfer.
- `C3`: the winning direction repeats on both R7->R8 and R8->R9 transfers.
- `C4`: terminal relative error is below 1% on the relevant endpoint.
- `C5`: the secondary local ARA stencil beats both Home and independence on R9.

No pass licenses a claim of new prime prediction, a complete ARA sphere, a recovered Time-like pole, or an ARA-only
information gain. The established terminal Mertens/PNT factors \(e^\gamma/2\) and \((e^\gamma/2)^2\) are retained as
terminal comparators. Any positive transfer must be assessed against the possibility that it is finite-sieve
convergence in established number theory.

## Required artifacts

- primary script and JSON/CSV results;
- an independently coded validator that does not import the primary module;
- an executed notebook with context, data, results and takeaways;
- a result report that preserves negative and equivalence findings;
- SHA-256 hashes for source data, protocol, code and outputs.

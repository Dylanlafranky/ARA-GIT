# T417 — Coupled Rationality/Irrationality Di-ARA handover

**Frozen before development and locked-evaluation scoring:** 21 August 2026  
**Status:** ARA-first coupling test on the T416 reconstructed ensemble spin mode  
**Source identity and medium:** unchanged from T416 (ISIS EMU RB1620447, 300 K, RF-on and RF-off scored separately)

## Relational location

- **Measured identity:** the resolved detector-share spin mode of a muon population.
- **Parent:** the detector-summed survival/release envelope already used in T414–T416.
- **State Di-ARA:** the local magnitude/orientation pair \((x_L,x_C)\).
- **Rationality/Irrationality Di-ARA:** two independent history participations measured from the same past-only window:
  - closure participation \(R=2\rho\), where \(\rho\) is median lagged closure coherence;
  - unresolved participation \(I=x_R\), the T416 local continuation residual.

T417 does not change the particle, material, temperature, tier, or reconstruction. It couples two already-measured history components that T416 left separate.

## Who / what / when / where / why / how

### Who

The same 13 development and 13 interleaved locked-evaluation fields used in T416. Each run contributes RF-on and RF-off population time series. These are ensemble histograms, not continuously observed individual muons.

### What

Test whether the declining closure wave and rising unresolved wave form a coupled Di-ARA handover before the unresolved coordinate reaches its 2.0 instrument ceiling. Separately test whether the local State waves meet on either of the two relations visible in the 284 G plot:

1. **same-coordinate meeting:** \(x_L=x_C\);
2. **mirror/anti-diagonal meeting:** \(x_L+x_C=2\).

### When

Use the existing past-only T416 windows from approximately 2.28 to 6.00 microseconds, sampled every 0.064 microseconds. All event rules use only values available at or before the current window endpoint.

### Where

All calculations remain inside one run and one RF period. RF-on and RF-off are never connected into one line or treated as one continuous trajectory. The 284 G visualization will use separate panels.

### Why

T416 showed that \(I=x_R\) often maxes out at 2.0. T417 asks whether the missing handover is retained in the **relation between closure and unresolved participation**, rather than in either component alone. The State-wave checks test the user's red and blue visual hypotheses without treating drawn circles as measurements.

### How

For every T416 history window define

\[
R(t)=2\rho(t),\qquad I(t)=x_R(t).
\]

These are independent participations and are not forced to sum to two. Their coupled coordinates are

\[
A(t)=\frac{R(t)+I(t)}{2},
\]

\[
B(t)=1+\frac{I(t)-R(t)}{I(t)+R(t)+\epsilon}.
\]

Here \(A\in[0,2]\) is total coupled participation and \(B\in[0,2]\) is relational balance:

- \(B<1\): closure/rationality leads;
- \(B=1\): equal-participation ridge \(R=I\);
- \(B>1\): unresolved/irrationality leads.

This is the T409 amount-plus-balance refinement, now applied to the T416 history variables. It does not force mirroring or TE-ARA closure.

## Frozen event rules

### Coupled handover candidate

The handover candidate is the first upward crossing of \(B=1\) that has at least two immediately preceding samples at or below one and at least three samples from the crossing onward above one. Crossing time is linearly interpolated from \(I-R\).

### Unresolved saturation

The saturation event is the first sample at or above \(I=1.99\) followed by at least two more samples at or above 1.99.

### State-wave meetings

Within each run/period, linearly interpolate every zero crossing of

\[
d_{same}=x_L-x_C
\]

and

\[
d_{mirror}=x_L+x_C-2.
\]

For each coupled handover candidate retain the nearest same-coordinate meeting and nearest mirror meeting in absolute time.

## Frozen controls

1. **R/I circular-shift control:** circularly shift \(R\) relative to \(I\) within each run/period by a deterministic non-trivial offset of at least five samples. This preserves each marginal path while breaking their local coupling.
2. **State mirror control:** circularly shift \(x_C\) relative to \(x_L\) within each run/period before recomputing same-coordinate and mirror meetings.
3. **Field bootstrap:** resample magnetic fields with replacement, preserving the paired RF-on/RF-off records for each selected field.
4. **Boundary guard:** no event may cross or connect the RF-on/RF-off boundary.

All random controls use seed 417. One thousand circular-shift draws and ten thousand field-bootstrap draws are frozen.

## Frozen development-to-evaluation procedure

1. Run the fixed equations and gates on the 13 T416 development fields.
2. Record protocol and script hashes plus the complete development output.
3. Do not alter thresholds, directions, persistence lengths, controls, or gates.
4. Run the same script once on the 13 T416 locked-evaluation fields.

Because those validation records were already inspected in T416, T417 is labelled a **post-T416 locked evaluation**, not a new untouched confirmation.

## Frozen gates

The coupled handover pattern is labelled supported only if all primary gates pass on the locked-evaluation fields:

1. **Availability:** at least 20 of 26 run/period sequences contain both a sustained \(B=1\) upward crossing and a later sustained \(I=1.99\) saturation.
2. **Ordering:** at least 80% of eligible sequences place the balance crossing before saturation.
3. **Positive lead:** the paired-field-bootstrap 95% interval for median crossing-to-saturation lead lies wholly above zero.
4. **Coupling specificity:** the observed across-sequence median absolute deviation of handover parent-ARA position is at least 25% smaller than the median circular-shift null dispersion, with empirical \(p<0.05\).

The State-wave relation is reported separately and cannot rescue the primary verdict:

5. **State alignment:** either the same-coordinate or mirror meeting has a smaller median distance to the coupled handover than 95% of its circular-shift controls. The winning relation must be declared from the locked evaluation, not chosen per sequence.

## Claim boundary

T417 can test whether two already-observed history components form a reproducible population-level balance transition before unresolved saturation, and whether local State-wave meetings align with it more than shifted paths do. It cannot establish a single-muon decay time, observe a neutrino, prove a universal Rationality/Irrationality law, or convert the T416 estimator ceiling into a physical singularity by definition.

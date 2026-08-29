# T396 — Information³ spin/child lock findings

**Protocol SHA-256:** `76BF6A48147DAB008E16343648ED17CD40BFC4360C3B8FD590EE7693B05C7B44`  
**Primary population:** 1,000,000 fresh polarized `mu+` truth events  
**Holdout:** 300,059 events  
**Primary gate:** PASS

## Result first

The joint `(P,R) -> C` model changed holdout NLL by
**+0.015506 nats/event** relative to the parent-only
model; fixed block-bootstrap 95% CI
**[+0.014412, +0.016642]**.

The zero-polarization falsifier produced
**-0.027820 nats/event**, CI
**[-0.028782, -0.026868]**.

This means the signed spin/daughter relation adds event-level information
about the hidden neutral split when polarization physically couples it, and
the increment disappears when that coupling is removed.

## Holdout ordering

| model | mean NLL |
|---|---:|
| analytic_va_oracle | -0.116014 |
| additive_factorized | -0.081931 |
| joint_information3 | -0.076552 |
| parent_only | -0.061046 |
| relation_shuffled_calibration | -0.040192 |
| wrong_event_relation | 0.001752 |
| phase_space | 0.025772 |
| mirrored_orientation | 0.087398 |
| relation_only | 0.173976 |
| unconditional | 0.199551 |

## ARA interpretation

`P=x_e` is the parent charged-versus-joint-neutral cut. `R=1+cos(theta_eS)`
is an independently observed orientation cut. `C` is the hidden split inside
the neutral branch. Their joint improvement is the strict Information³ part:
two observed relations constrain a third more strongly than either observed
relation alone.

The lower-variance additive/factorized fusion gained **+0.020885
nats/event** over the parent-only model and outperformed the dense joint
histogram. The supported result is therefore complementary information from
two cuts; it does not require a learned nonlinear `P x R` interaction. Its
gain fell monotonically with polarization and became slightly negative at
zero polarization.

## Boundary

This is a fresh leading-order Standard-Model `V-A` truth crosswalk, not direct
two-neutrino observation. Exact branch recomposition is definitional. The
empirical next rung requires event-linked measurements with an independent
neutral-sensitive target.

Portable technical report:
`analysis/muon/T396_information3_spin_child_lock/T396_INFORMATION3_SPIN_CHILD_LOCK_REPORT.html`.

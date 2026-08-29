# T411D frozen evaluation — causal connection-heavy child forecast

## Outcome

**T411D-v1 is not supported as a precise cross-identity timestamp predictor by
its frozen six-gate rule.**  It passed five gates and failed the predeclared
timing-accuracy gate.

At the same time, the sealed holdout supports the narrower temporal-ordering
claim: the operational connection-heavy child crossing usually occurred before
the offline parent handover and substantially before the causal parent-only
alarm.

## Freeze integrity

- Development identities: S1 and S3.
- Sealed holdout identities: S2 and S4.
- Child scale: one half of the parent rate window.
- Development child-to-parent offset: 0.058 s.
- Persistence: five already-observed frames.
- Holdout parameters were verified against the frozen protocol, script and
  source-data SHA-256 hashes before evaluation.

## Sealed holdout result

| Measure | Result | Frozen decision |
|---|---:|---|
| Eligible offline parent targets | 82 | context |
| Child forecasts issued | 78 | context |
| Forecast coverage | 0.9512 | PASS (>= 0.75) |
| Issues before parent target | 69 / 78 = 0.8846 | PASS (>= 0.70) |
| Median issue lead | 0.136 s | PASS (> 0) |
| Bootstrap 95% interval, median issue lead | 0.083 to 0.197 s | uncertainty |
| Wilson 95% interval, pre-target fraction | 0.7950 to 0.9381 | uncertainty |
| Median normalized absolute timing error | 0.2331 lifetime | **FAIL (<= 0.10)** |
| Bootstrap 95% interval, median timing error | 0.1659 to 0.2804 | uncertainty |
| Child issue before parent-only issue | 0.0745 s median | PASS (> 0) |
| Circular-shift timing control | p = 0.00599 | PASS (<= 0.05) |

The parent-only alarm had lower timestamp error (0.0553 lifetime) but its role
is different: it occurred only 0.0195 s before the target at the matched-event
median, versus 0.136 s for the child.  In development it occurred 0.004 s
after the target at the median.  It is therefore a closer handover detector,
while the child is an earlier but less precisely calibrated warning.

## Identity split

Among issued child forecasts:

| Fluid | Forecasts | Pre-target fraction | Median lead | Median absolute error | Median normalized error |
|---|---:|---:|---:|---:|---:|
| S2 | 59 | 0.8814 | 0.112 s | 0.076 s | 0.2477 |
| S4 | 19 | 0.8947 | 0.215 s | 0.173 s | 0.1484 |

Both holdout identities preserve the ordering result.  Their different lead
scales explain why the single 0.058 s development offset under-predicts the
parent time.  This is consistent with an identity/rung-dependent delay, but
does not by itself determine that scaling law.

## ARA interpretation

The tested operational child was

\[
C_t=\max(r_I^{(P)},0),\qquad
M_t=|r_I^{(C)}-r_I^{(P)}|,
\]

\[
x_C=2\frac{C_t}{C_t+M_t}.
\]

The holdout shows that this child relation carries non-random advance timing
information about the later parent crossing.  It does **not** show that a
single fixed number of seconds maps child crossing to parent handover across
all fluid identities.  The user's stated asymmetry boundary is therefore
important: the child landmark can be stable relationally while its projection
onto parent clock time shifts with identity and coupling.

## Data and inference boundaries

1. The outcome is the earlier T411C offline reconstructed parent crossing, not
   a directly imaged microscopic handover.
2. Predictor and target come from the same diameter traces at different causal
   treatments, so shared monotone thinning remains a rival explanation.
3. The circular-shift control rejects arbitrary timing within these traces but
   does not uniquely identify the ARA child decomposition.
4. Four targets occurring before any causal parent-rate estimate could exist
   were excluded as causally unresolvable; this rule was added and frozen using
   development data before holdout.
5. S2/S4 are now opened.  Any identity-scaled delay fitted using them is
   post-hoc and requires a new sealed dataset or a separately frozen external
   replication.

## Claim status

- **Supported on sealed holdout:** an operational connection-heavy child
  crossing usually precedes the T411C parent handover and is timed better than
  circularly shifted child histories.
- **Not supported by T411D-v1:** a universal fixed-seconds child-to-parent delay
  predicts the precise parent timestamp within 0.10 of lifetime.
- **Open:** the predeclared identity/rung scaling law that converts relational
  child lead into parent clock time.


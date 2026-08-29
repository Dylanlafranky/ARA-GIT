# T406/T407 — Grandchild quarter completion and individual-muon transfer

Date: 18 August 2026  
Status: **population-compatible; individual timing transfer not supported**

## Answer first

The proposed construction

\[
0.5_{\rm parent}+0.25_{\rm grandchild}=0.75
\]

is compatible with the corrected population crest at `0.706306`, but it is
not an exact or split-stable physical landmark. It also does not provide
independent predictive timing for one event-linked stopped muon when applied
to the available incoming detector coordinate.

This creates a clean evidence split:

- **Retain:** the `0.7` region is consistent with a participation-displaced
  quarter-capacity child/grandchild relation at the population scale.
- **Reject for this cut:** `0.75`, or its observed displacement `0.706306`, is
  not an individual muon decay/neutrino-release clock recoverable from the
  static incoming upper/lower prompt relation.

## T406 — population-scale quarter-completion test

### Frozen ARA construction

The corrected parent reference was fixed at `0.5`. A grandchild with one
quarter of the parent-scale capacity gives a pure endpoint at `0.75`. No
observed value was recentered to that endpoint.

The primary crest was:

\[
x=0.706306,
\qquad
x-0.75=-0.043694.
\]

It therefore used `82.52%` of the proposed `0.25` interval. Decompressing the
interval `0.5 -> 0` and `0.75 -> 2` gives

\[
x_G=\frac{2(x-0.5)}{0.25}=1.65045.
\]

That is close to, but not at, the grandchild completion pole `2`.

### Replication and distortion

Across 20 registered deterministic splits:

- `7/20 = 35%` fell within `0.75 +/- 0.10`; the frozen `75%` gate failed.
- the median crest was `0.948276`;
- the range was `0.640380` to `1.057814`;
- prompt participation versus crest had Spearman `rho=1.000`;
- leave-one-split-out monotone prediction had median absolute error
  `0.000728` and maximum error `0.005624`.

The strong participation relation shows that the coordinate responds
coherently to parent/child participation. However, the equality boundary used
to build the coordinate carries the same ordering. This is an internally
precise coordinate-response result, not independent confirmation of a
physical quarter-energy carrier.

The frozen verdict is **PARTICIPATION-DISPLACED QUARTER-COMPATIBLE**.

## T407 — transfer to individual stopped-muon events

### Identity and observable boundary

The individual archive links an incoming stopped-muon candidate to a later
charged-daughter pulse cluster. It does **not** directly observe either
neutrino and it does not resolve an individual muon's spin trajectory.

The tested incoming coordinate was

\[
x_\mu=\frac{2B}{A+B},
\]

where `A` and `B` are the gain-normalised prompt counter relations used in
T379. The outcome was the delay to the same record's later charged daughter.
Thus T407 asks whether the proposed child band contains advance event-level
timing information beyond ordinary detector strength, multiplicity and depth.

### Frozen bands and controls

Two candidate additions were tested against the ordinary model:

- pure projected band: `0.75 +/- 0.05`;
- observed population band: `0.706306 +/- 0.05`.

Controls were fixed at `0.50`, `1.00`, `1.25` and `1.50`. The models were fit
on 2,396 calibration events and scored on 2,109 held-out event-linked records
from two separate runs.

### Result

The `0.75` band contained 259 holdout events with median charged-daughter
delay `1.66875 microseconds`. The `0.706306` band contained 213 events with
median delay `1.59875 microseconds`. The descriptive short-delay shape is
there, but it did not add predictive information after ordinary event geometry
was included:

- `0.75` mean NLL improvement: `-0.00000282`, 95% block interval
  `[-0.00001515, +0.00000833]`, permutation `p=0.6717`;
- `0.706306` mean NLL improvement: `-0.00051254`, interval
  `[-0.00194865, +0.00101494]`, permutation `p=0.7746`.

Negative improvement means the additional band was marginally worse. Neither
candidate improved both held-out runs, and no frozen control supplied a
replacement landmark.

The frozen verdict is **GRANDCHILD BAND TRANSFER NOT SUPPORTED**.

## Interpretation in ARA language

The parent view can compress varied children into a common landmark. At the
child/event scale, participation and detector identity displace individuals
around that reference. T406 supports that distinction. T407 then shows that
the incoming pulse ratio is not the missing anti-phase/maturity cut needed to
time one event.

Accordingly, `0.706306` should not be called the end of an individual
"pregnancy" or the instant a neutrino is born. It remains a population-level
candidate completion region. The missing individual relation is more likely
to require a genuinely dynamic pre-decay input such as spin phase/maturity,
charged-daughter direction relative to polarization, or independently
reconstructed missing momentum.

## Boundaries

- T406's 20 splits overlap and come from one analysis lineage; they are not an
  external replication.
- T407's holdout was generated and inspected earlier in the project, so it is
  not a pristine new prospective holdout.
- Charged-daughter timing is a decay-event proxy, not direct neutrino timing.
- Failure of this static individual coordinate does not reject the broader
  population handover geometry or a different event-level phase cut.

## Reproduction and artifacts

- Protocols: `T406_GRANDCHILD_QUARTER_COMPLETION_PROTOCOL_2026-08-18.md` and
  `T407_INDIVIDUAL_MUON_GRANDCHILD_TRANSFER_PROTOCOL_2026-08-18.md`
- T406 scripts: `t406_grandchild_quarter_completion.py` and
  `validate_t406_grandchild_quarter_completion.py`
- T407 scripts: `t407_individual_muon_grandchild_transfer.py` and
  `validate_t407_individual_muon_grandchild_transfer.py`
- Combined report:
  `T407_individual_muon_grandchild_transfer/T406_T407_GRANDCHILD_TO_INDIVIDUAL_MUON_REPORT.html`

Both saved-output validators passed. The combined portable report passed
schema, packaging and structural verification; browser-level interaction QA
was unavailable in the local report builder.

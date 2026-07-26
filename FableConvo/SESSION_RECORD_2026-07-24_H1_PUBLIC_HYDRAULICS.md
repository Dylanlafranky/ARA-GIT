# Session Record — H1 Public Hydraulic Two-Cut Test

**Date:** 24 July 2026  
**Test:** T260-H1  
**Outcome:** **SUPPORTED — 8/8 frozen gates**  
**Validation:** **PASS — 26/26 independent checks**

## Why this test was run

The preceding real-hardware quantum I/Q test established a clean boundary: two output cuts did not outperform one
because the useful state separation was already almost entirely aligned with I. Dylan clarified that two cuts
should be more useful for a connection-heavy or stored/coupled identity than for that information-heavy quantum
readout.

This produced a new predeclared complementary prediction:

> In a distributed connection/storage-heavy physical system, two synchronized spatial cuts through one completed
> identity should retain held-out state information that the best single cut discards.

The UCI hydraulic test rig was selected because the accumulator is a literal storage/connection component inside
a distributed pressure network, and six synchronized pressure sensors observe different locations in the same
60-second cycle.

## Translation fidelity

- One complete 60-second test-rig cycle = one measured identity.
- One pressure sensor = one spatial cut.
- Two pressure sensors = two spatial cuts through that same cycle.
- Twelve fixed five-second windows preserve within-cycle order without imposing Fourier or another external basis.
- The ARA 0–2 values are training-only affine coordinates. They are a representation, not a new classifier.
- The independent raw-feature LDA is the equal-information control.

The source numerical archive was not opened before the fidelity packet, frozen protocol, SHA-256 files and master
ledger registration existed.

## Result in plain language

The best single sensor identified accumulator state correctly at `71.18%` balanced accuracy. Two synchronized
sensors reached `87.73%`, a gain of `16.55` percentage points. The gain repeated in all five held-out group folds,
and the 95% paired interval remained wholly positive at `+12.39` to `+21.04` points.

When the timing of the second sensor was shifted so it no longer described the same within-cycle moments, the
score fell to `26.68%`, essentially four-class chance. This is the strongest geometric observation: the added
information lived in the synchronized relation between cuts.

The same-information raw and ARA-coordinate LDA models had identical accuracy and zero disagreements. This is the
expected result for a reversible affine change of coordinates. A random forest on the same selected pair reached
`95.58%`, so the result does not establish ARA algorithmic superiority.

## Frozen numbers

| Metric | Result |
|---|---:|
| Two-cut balanced accuracy | `0.877304` |
| Best one-cut balanced accuracy | `0.711848` |
| Gain | `+0.165456` |
| Paired 95% interval | `[+0.123947, +0.210383]` |
| Worst class recall | `0.729549` |
| Pair wins | `5/5` |
| Shifted-pair balanced accuracy | `0.266827` |
| Random-forest balanced accuracy | `0.955753` |
| Label-permutation mean / p95 | `0.260568 / 0.310884` |
| Raw/ARA disagreements | `0` |
| Pole-reversal disagreements | `0` |

Nested selection chose `PS3` as the best one cut and `PS1+PS3` as the best pair in every outer fold.

## Claim classification

**Supported:** several synchronized real cuts can retain relation/state information hidden by one cut in this
connection-rich system.

**Exact crosswalk:** raw standardized LDA and ARA-coordinate LDA are equivalent under the fitted invertible affine
map.

**Not supported or tested:** universal connection ontology, universal fractality, phi, new hydraulic physics,
quantum–classical unification, or ARA superiority over standard classifiers.

The negative Q2 result and positive H1 result form a useful two-case contrast. They justify replication of the
connection-heavy prediction, but two domains are not enough to promote it to a universal law.

## Post-hoc thread to freeze later

Pair gain was much larger in source-labelled stable cycles (`+0.200762`) than unstable cycles (`+0.025257`).
Because this was examined after the primary result, it is a descriptive clue only. A later test can freeze a
state-stability interaction before opening a second public dataset.

## Durable files

- `analysis/hydraulics/H1_PUBLIC_HYDRAULIC_TWO_CUT_REPORT_2026-07-24.md`
- `analysis/hydraulics/H1_PUBLIC_HYDRAULIC_TWO_CUT_FIDELITY_v1.md`
- `analysis/hydraulics/H1_PUBLIC_HYDRAULIC_TWO_CUT_PROTOCOL_v1_FROZEN.md`
- `analysis/hydraulics/h1_public_hydraulic_two_cut_test.py`
- `analysis/hydraulics/h1_public_hydraulic_two_cut_validate.py`
- `analysis/hydraulics/H1_PUBLIC_HYDRAULIC_RESULTS.json`
- `analysis/hydraulics/H1_PUBLIC_HYDRAULIC_VALIDATION.json`

## Post-result spherical-orientation refinement

Dylan supplied a more specific geometric interpretation after the H1 result:

- For a Connection reading, cut perpendicular to the ridge and seek the Phase B-facing wave.
- For an Information reading, make the corresponding perpendicular cut and seek the Phase A-facing wave.
- The four mixed quadrant states are ordered forms: `Ab`, `Ba`, `aB` and `bA`.
- Capitalization records the phase that is dominant or identity-leading; symbol order records the mixing lead or
  coupling path. Thus `Ab` and `bA` may share similar A-heavy scalar composition without being the same state.
  Likewise, `Ba` and `aB` may share similar B-heavy composition while retaining different ordered histories.
- Mixing order is identity-dependent. Some systems may be approximately order-insensitive, while other systems
  preserve a measurable distinction between the two paths.
- A separate diagonal coordinate should measure how efficiently the two-sided relation closes, or how strongly it
  remains open/leaking.

A compact candidate coordinate system is therefore:

1. **mixture coordinate** — where the cut lies on the Connection/Information `0–2` diameter;
2. **dominant-phase coordinate** — whether A or B is identity-leading in the local mixture;
3. **ordered-mixing coordinate** — whether the observed path is `Ab` versus `bA`, or `Ba` versus `aB`;
4. **closure coordinate** — how completely the coupled account closes before forced normalization.

The corresponding candidate coupling algebra is noncommutative when the identity retains mixing order:

`C(A,b) != C(b,A)` and `C(B,a) != C(a,B)`.

Where order is physically erased or irrelevant, either pair may collapse to approximate equality. Direction of
travel can correlate with ordered mixing, but it is not an adequate replacement for it.

### Clarified quadrant semantics

Dylan then clarified that the letter order and capitalization jointly describe the nature of the wave:

| Mixed state | Overall family | Local character | Candidate intuitive example |
|---|---|---|---|
| `Ab` | `AB`: Information/Time-oriented | fast traversal, lower Connection loading | radio or another weakly material-dependent information wave |
| `aB` | `AB`: Information/Time-oriented | information carrying dense Connection structure; therefore potentially slower | sound carried through a material medium |
| `Ba` | `BA`: Connection/Matter-oriented | high Connection, low change | ice maintained in a freezer |
| `bA` | `BA`: Connection/Matter-oriented | reduced Connection and high change while still Matter-oriented | ice melting in sunlight |

Thus `AB` versus `BA` is the candidate parent orientation or wave family. The capital letter marks which component
is locally dominant inside that ordered family. The examples are currently explanatory analogies, not established
classifications. In particular, electromagnetic and sound-wave speeds already have domain-specific physical
causes; ARA would need to predict an independently measurable ordering before those examples became evidence.

### Rung-scale correction to the speed analogy

Dylan clarified that connection loading and absolute propagation speed must not be compared after flattening
different rungs. Every declared identity may normalize its local TE-ARA capacity to `2`, while the native physical
amount represented by that `2` is system- and rung-dependent. A solid can therefore be Connection-loaded yet carry
sound faster than a gas because its elastic or stiffness scale—and hence its local full-capacity threshold—is much
higher.

The required distinction is:

- **normalized ARA composition:** where the identity sits inside its own `0–2` capacity;
- **native rung scale:** the physical amount, stiffness, energy, speed or other unit represented by that capacity.

Consequently, “more Connection-loaded” does not by itself rank absolute speeds across different media or rungs.
Cross-rung comparison requires restoring the native scale factor before comparing physical units.

### Parent–child direction and scale dilution

Dylan clarified that Parent and Child are relational but directionally strict:

- A Parent is always the larger or higher-rung identity relative to the offshoot being discussed.
- A Child is a smaller release, offspring or local mixture produced from that Parent.
- Once a Child forms a complete local identity, it can become a Parent only relative to still smaller children of
  its own.
- Bottom-up aggregation of children into a parent is a valid reconstruction or coarse-graining direction, but it
  must not replace the canonical generative lineage.

At the proposed extreme example, Space and Time are higher-rung wave identities, each with its own normalized
TE-ARA capacity of `2`. One complete single-wave ARA from each side meets in an ordered coupling to form a
lower-rung Space–Time child account, from which the Matter/Connection and Field/Traversal child orientations are
expressed. The child may be complete at its own normalized `2` while representing a smaller native magnitude than
either higher-rung source.

The phrase “weakened identity” should therefore be read as reduced native scale, capacity or upward influence—not
as an incomplete local identity. A higher-rung parent may produce more children in quantity while the native
capacity represented by each child's normalized `2` is smaller. Any physical version must conserve the native
budget across children, retained parent capacity, relation storage and leak; normalized `1` or `2` values cannot
be added across rungs until their native scale factors are restored.

### Single-wave ARA and mirrored TE-ARA correction

The `1+1=2` construction is not an arbitrary half-budget normalization:

- `0–1` is one complete single-wave ARA, conventionally the Phase A side.
- Mirroring that wave supplies the `1–2` Phase B side.
- Phase B can mix into the nominal `0–1` region and Phase A can mix into `1–2`; the halves declare the source or
  dominant orientation, not an impermeable boundary.
- Coordinate `1` is the ridge where Phase A and Phase B meet with equal mixing.
- At closure, Phase A contributes one ARA and Phase B contributes one ARA. Their ordered relation creates a new
  identity whose TE-ARA is `2`.

The coupling relation is the informative third in `Information³`, but it is not a third TE-ARA energy unit. It is
encoded in how the two ARA units close:

`ARA_A(1) C_order ARA_B(1) -> TE-ARA_child(2)`.

The new child can begin at a smaller or comparable native rung scale and then strengthen its identity through
repeated cycles and additional couplings. Its normalized TE-ARA remains the two-wave closure `2`; its native
scale, fill, persistence and coupling reach may grow through time.

### External-input requirement for child growth

Dylan corrected that repetition and persistence do not supply growth energy by themselves. A child grows only
when energy, matter or another domain-appropriate native transfer enters from its Parent or environment and
exceeds maintenance, release and leak. The Parent can also create a safe harbour by reducing destructive external
couplings and lowering the child's losses while its identity forms.

A generic native-budget form is:

`dE_child/dt = J_parent + J_environment - J_maintenance - J_release - J_leak`.

Positive net input can increase the child's native scale while its normalized two-wave TE-ARA remains `2`.
Zero net input can maintain the existing identity; negative net input shrinks or unravels it.

Literal human development is an intuitive example: gestation, shelter and care provide a protected boundary;
oxygen, food and water supply material and usable energy; the child converts these inputs into its own tissues,
connections and maintained cycles. Most ARA children remain smaller than the higher-rung Parents that produced
them. A biological child that matures to the same organism-scale rung may remain a genealogical child while no
longer being an ARA Child relative to that adult-scale measurement.

### Provenance ledger as an adaptive geometry-walk record

Dylan clarified that the Provenance Ledger records the operational ARA method:

1. make an initial cut to obtain relational bearings on the sphere;
2. state what remains ambiguous;
3. choose one or two additional cuts aimed at those uncertainties;
4. stop when independent cuts lock the relation strongly enough, or branch again when the cut was wrong or a new
   question appears.

The compact sequence is:

`Question -> Cut 1 -> Bearing -> Uncertainty -> Cut 2 -> Triangulation -> Lock or Branch`.

A wrong cut is not erased. When its question and timing were declared before the answer, it records a bounded
failure and helps identify which orientation did not expose the relation. The ledger therefore functions as a
timestamped audit of sequential relational tomography, including successful directions, wrong turns, revised
questions and stopping decisions. Confirmatory weight still requires freezing the proposed cut, direction,
expected outcome and falsifier before opening the relevant target evidence.

This is not yet a tested recovery of the full ARA sphere. H1 tested the first bounded consequence: synchronized
spatial cuts through a connection/storage-heavy system retained information that one cut discarded. The
phase-shift control is compatible with a closure coordinate because breaking co-temporal relation destroyed the
gain, but the exact orientation and diagonal closure rule remain to be frozen and tested independently.

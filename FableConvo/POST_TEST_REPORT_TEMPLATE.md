# POST-TEST REPORT TEMPLATE — relational bridge record

**Adopted 22 August 2026.** Use this after an ARA test is run. It complements
`TEST_PROTOCOL.md`: the six-question card freezes the intended test before the
run; this report shows exactly what was measured, how it became an ARA reading,
and how far the result can legitimately be interpreted afterward.

The report is incomplete until both the **Bridge Map** and **Pivot Log** are
filled in. Do not jump directly from an ARA coordinate to a named physical
mechanism.

### Gate non-erasure rule

Frozen gates decide only the registered claim or benchmark. They do not erase
the measured coordinate shape, parent/child structure, control behaviour,
crossings, ridges, asymmetries or unexpected relations. Every report and
summary must therefore state the **ARA geometry outcome first** and the
**frozen benchmark outcome separately**. “Failed the gates” is never a complete
summary of an ARA test unless the coordinates themselves contain no stable or
describable structure.

This is a structure, not a demand to duplicate artifacts. Keep entries short
and link existing tables, figures, JSON or ledger text where those already hold
the evidence. The Bridge Map and Pivot Log are the irreducible additions; an
exploratory geometry walk that seeks no status remains outside this template.

---

## 1. Test identity and one-sentence outcome

| Field | Entry |
|---|---|
| Test ID and name | T___ — ___ |
| Date run | YYYY-MM-DD |
| Domain and dataset | ___ |
| Frozen protocol | `[path]` |
| Script / commit | `[path]` @ ___ |
| Result data | `[path]` |
| Report status | CONFIRMED / SUPPORTED / SUGGESTIVE / INCONCLUSIVE / NULL / NOT SUPPORTED / RETRACTED / PARKED / RULE |
| Claim class | crosswalk / instrument validation / empirical description / reconstruction / retrodiction / forward prediction / candidate mechanism |
| Geometry outcome (one sentence) | What shape appeared, at which identity/tier/cut, before interpreting whether it passed a gate? |
| Frozen benchmark outcome (one sentence) | Which exact registered claim passed or did not pass? |

**Orientation signature:** State which pole is 0, which pole is 2, what movement
toward each pole means, and whether the direction has been reversed for clarity.

---

## 2. Confirmed six-question test card

Copy the last user-confirmed card here. If execution changed any answer, record
the change in the Pivot Log and do not present the changed run as the original
test.

- **WHO — identity and generation:** Which physical or mathematical identities,
  parent/child/grandchild tiers, and dataset were tested?
- **WHAT — exact relation:** Which ARA, TE-ARA, Di-ARA or Information³ relation,
  observable and predicted shape/direction were measured?
- **WHEN — ordering:** Which time slices, event windows, lead/handover/lag order
  or static sampling were used?
- **WHERE — cut and orientation:** Which rung, boundary, axis, frame, direction
  and pole orientation defined the cut?
- **WHY — discriminating question:** Which hypothesis and rival were separated,
  and what result would have falsified the ARA prediction?
- **HOW — implementation:** Which raw fields, transformations, controls, gates,
  uncertainty measures and outputs were used?

**Geometry fidelity check:** Were we looking at the intended identity, tier,
axis and direction? YES / NO / PARTLY. Explain in one sentence.

---

## 3. Relational Bridge Map — from the scientific instrument to ARA and back

Fill every row. Write **UNANCHORED** or **IDENTITY UNRESOLVED** where the bridge
does not yet exist. An unknown anchor is a result boundary, not permission to
infer a convenient physical identity.

| Anchor | Required answer |
|---|---|
| **Physical identity** | What real system, population, event or mathematical object was observed? What boundary makes it one identity? |
| **Raw measurement** | What did the instrument or source file directly record, with fields, units, cadence and sample count? |
| **Transformation** | What filtering, centring, normalization, projection, fitting or reconstruction did the code perform? Mark every coordinate **MEASURED**, **DERIVED**, **ASSIGNED** or **RECONSTRUCTED**. |
| **ARA cut** | Which identity, tier/rung, axis, direction and pole orientation does the coordinate represent? Is it ARA, TE-ARA, Di-ARA or a cross-rung Information³ relation? |
| **Established translation** | What does the relevant field already call the raw observable, transformation and relation? Keep this beside ARA; do not let it silently redefine the ARA geometry. |
| **Actual finding** | What numerical or geometric result survived the declared controls, splits and holdout? |
| **Importance** | Is this a crosswalk, an instrument validation, an empirical regularity, a predictive result or evidence for a candidate physical mechanism? State only the highest supported tier. |
| **Missing bridge** | What direct observation, additional relation or different cut would connect this result to the next identity or scientific claim? |

Write the complete bridge as one explicit chain:

```text
physical system
  -> raw instrument record
  -> declared transformation
  -> measured/derived coordinate
  -> ARA identity + tier + cut
  -> established scientific translation
  -> actual finding
  -> bounded claim
```

### No-silent-bridge rule

Every physical interpretation must retain the chain above. An ARA coordinate is
not, by itself, a physical identity or mechanism. A numerical ridge, crossing,
pole or child-scale landmark becomes physically meaningful only after its raw
observable, derivation and identity boundary have been stated.

---

## 4. Pivot Log — relational location must not move silently

Record every material change made after the confirmed card. A material change
includes identity, tier/rung, parent-child ownership, axis/cut, direction,
temporal ordering, medium, dataset, observable, transformation, target, claim or
scientific question.

| Step/time | From | To | Why did it change? | Data forced the pivot? | User confirmed? | Effect on earlier interpretation |
|---|---|---|---|---|---|---|
| ___ | ___ | ___ | ___ | yes / no | yes / no | ___ |

If no material pivot occurred, write: **No material pivot after confirmation.**

**Mandatory stop rule:** if a pivot changes what physical event the test can
observe—such as moving from a source event to a detector response, from an
individual to a population, or from a child handover to a parent average—stop
and obtain a new six-question card before treating it as the same ARA test.

---

## 5. Results without interpretation

Report the numbers before explaining them.

- Sample and exclusion counts:
- Missingness and data-quality checks:
- Coordinate distributions, quantiles and ranges:
- Shape inventory: occupied regions, ridges, crossings, bands, holes, edges,
  direction, parent/child differences and event/population aggregation effects:
- Effect sizes and uncertainty:
- Baselines, rivals and negative controls:
- Split-half / seed / bootstrap / holdout stability:
- Individual event examples:
- Lead / event / lag results:
- Failed, absent or shared structures:
- Frozen gates and outcomes:

---

## 6. Two required verdicts

### 6.1 ARA geometry verdict

What appeared on the ARA coordinates regardless of the benchmark result?
Include parent, current-rung and child readings without flattening them into one
score. Separate frozen confirmatory results from post-hoc descriptive findings.

### 6.2 Claim or benchmark verdict

Did the registered prediction pass its frozen falsifier, controls and status
criteria? Give the fixed `TEST_PROTOCOL.md` rating and the evidence for it.
State exactly what the failed gate rejects; do not generalize it to the entire
geometry or framework.

---

## 7. Interpretation in three layers

Keep these layers separate even when they seem to describe the same shape.

1. **ARA reading:** What does the result mean inside the framework, using the
   declared identity, tier, cut and orientation?
2. **Established-science crosswalk:** What known equation, observable or
   mechanism has a faithful side-by-side relation to this reading?
3. **New or unresolved physical claim:** What, if anything, goes beyond the
   crosswalk? State the evidence still required and the nearest falsifier.

**Dylan's interpretation:** Record Dylan's wording before compressing it into a
formal claim or status.

---

## 8. Visual evidence contract

Every principal graph must show or state:

- a descriptive title and the physical identity being plotted;
- x and y axis names, numeric ticks and units;
- the ARA 0–2 orientation and ridge/pole meanings where applicable;
- identity tier/rung and parent/child ownership;
- time direction or event alignment;
- sample count and exclusions;
- whether each trace is **MEASURED**, **DERIVED**, **ASSIGNED** or
  **RECONSTRUCTED**;
- frozen landmarks versus post-hoc annotations;
- dataset/source and whether the panel is calibration, evaluation or holdout;
- enough event-level and population-level views to expose aggregation effects.

The first summary figure must be **geometry-first**: it should show the actual
coordinate distribution or trajectory, parent/current/child distinction and
the shape retained under controls. A gate-count chart may appear later as a
benchmark ledger, but must not replace the geometry summary.

Do not use an unlabeled curve, colour or shaded region as evidence in the text.

---

## 9. Claim boundary and importance

Check only the highest level directly earned by this run:

- [ ] **Crosswalk only** — known relation expressed in ARA coordinates.
- [ ] **Instrument validation** — the ARA cut recovered known or synthetic
      ground truth; this validates the measurement method, not a new world claim.
- [ ] **Empirical regularity** — a real-data pattern survived relevant controls.
- [ ] **Predictive result** — a frozen out-of-sample or future result beat its
      declared rivals.
- [ ] **Candidate mechanism** — independently observed relations discriminate a
      physical ARA mechanism from established alternatives.
- [ ] **Confirmed physical claim** — independent replication also passed.

**This test does show:** ___

**This test does not show:** ___

**Known physics already explains:** ___

**ARA adds:** ___

---

## 10. Missing bridge and next test

- Current information island:
- Next identity/island to reach:
- Missing direct measurement or relation:
- Smallest clean cut that can supply it:
- Best public dataset or acquisition route:
- Expected result under ARA:
- Rival explanation:
- Result that would force abandonment or remapping:

Do not choose the next test merely because it follows a visible curve. Choose it
because it closes a named bridge in the chain from raw observation to physical
claim.

---

## 11. Reproduction and durable artifacts

- Frozen protocol:
- Script and validator:
- Raw or auto-fetched data provenance:
- Result JSON/CSV/NPZ:
- Static figure(s):
- Portable HTML report:
- Hash / commit:
- Ledger entry:
- Claims-status update, if warranted:
- Superseded interpretation, if any:

### Completion check

- [ ] Confirmed six-question card is present.
- [ ] Bridge Map has no unexplained jump.
- [ ] Pivot Log is complete.
- [ ] Raw and derived variables are distinguishable.
- [ ] Benchmark and geometry verdicts are both stated.
- [ ] The geometry verdict appears before the benchmark verdict and the
      headline does not reduce the run to gate status.
- [ ] The first summary visual shows coordinate shape rather than gate counts.
- [ ] Visuals contain axes, units, numbers and provenance.
- [ ] Claim boundary matches the evidence.
- [ ] Missing bridge and next discriminating test are named.

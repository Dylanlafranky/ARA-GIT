# ARA translation fidelity protocol — test the intended object

**Adopted:** 12 July 2026  
**Orientation:** up = slower/larger; down = faster/smaller unless the claim packet declares otherwise.  
**Status:** RULE; companion to `CANON_FOR_AI.md` and `TEST_PROTOCOL.md`.

## Purpose

Prevent **construct-validity failure**: a mathematically clean test can refute only an AI-invented proxy, flattened
analogy, reversed orientation, or wrong observable rather than Dylan's intended ARA claim.

Exploration remains free. This gate binds only when a musing is translated into a mathematical claim, test,
`CLAIMS_STATUS` entry, README headline, or public statement.

## Prime rule

## Post-compaction reconfirmation kill gate — added 30 July 2026

If chat context is compacted at any point after a test idea is proposed but
before the test is run, all earlier fidelity approval expires for execution
purposes. Retrieval from the repository is required but is not sufficient.

Before freezing code or touching target data, the AI must ask Dylan to
reconfirm:

```text
I think the test is:
- identity being moved/measured:
- axis or relation:
- ordered poles/direction:
- observable:
- what nearby relation must NOT be substituted:

Is that EXACT ENOUGH TO TEST?
```

No answer, no test. An answer given before compaction cannot be inferred to
cover the AI's reconstructed post-compaction object. If the AI runs anyway
and later discovers that it measured a neighboring axis, the result is
automatically:

`PROXY TEST — CONSTRUCT INVALID FOR THE INTENDED CLAIM`.

This rule applies even when the mathematics is clean, the data are valid, or
the proxy produces an interesting result.

> No formalisation is authorised as “the ARA claim” until it survives plain-language back-translation and Dylan
> recognises the intended relational object, direction and scope.

If fidelity fails after a test was run, preserve the result but relabel it `PROXY TEST — CONSTRUCT INVALID FOR THE
INTENDED CLAIM`. It is evidence about the proxy, not evidence for or against ARA.

## Step F0 — freeze the source

Create one versioned claim packet before domain lookup or real-data testing:

```text
Claim ID / version:
USER PRIOR — verbatim wording:
Identity/system being measured:
Ordered poles and declared direction:
Scale/rung origin:
Invariant relational claim — what must survive translation:
Permitted decompression:
Forbidden substitutions/proxies:
Observable needed:
Known ambiguity / competing reading:
What would count as “wrong object”:
```

Hash or commit the packet when priority or blindness matters. A later correction creates `v2`; never silently edit
`v1` after seeing a result.

## Step F1 — three-view translation

The interpreting AI must return all three:

1. **Plain restatement:** one short paragraph using Dylan's terms.
2. **Mathematical representation:** symbols, units, orientation and operators explicitly labelled.
3. **Back-translation:** translate the mathematics back into plain language without reading the original wording.

It must also list:

- assumptions added by the AI;
- information discarded;
- alternative mathematical objects that could fit the wording;
- the first place the translation could reverse direction or collapse identities.

## Step F2 — Dylan fidelity verdict

Use exactly one label:

- `EXACT ENOUGH TO TEST` — same object, relation, direction and intended scope;
- `USABLE WITH CORRECTION` — preserve packet and append Dylan's correction before proceeding;
- `WRONG OBJECT` — do not test or publish as ARA;
- `UNSURE / KEEP AS MUSING` — no evidential status.

Silence is not sign-off. AI confidence is not sign-off.

## Step F3 — critical-field fidelity gate

For translation fields

\[
F=\{\text{identity},\text{poles},\text{direction},\text{rung},\text{observable},
\text{coupling},\text{closure},\text{falsifier}\},
\]

record `m_j=1` only when the translated field matches the frozen packet. A bookkeeping score is

\[
\operatorname{Fidelity}
=
\left(\prod_{c\in C_{critical}}m_c\right)
\frac{\sum_jw_jm_j}{\sum_jw_j}.
\]

The product is a kill gate: any mismatch in identity, ordered poles/direction, measured observable, or claimed
closure makes fidelity zero. The weighted term describes noncritical completeness; it cannot rescue a wrong object.

This is a documentation score, not a statistical truth probability.

## Step F4 — blind AI interpretation audit

Blind AI drops test **communicability and translation robustness**, not physical truth.

Protocol:

1. Freeze and hash the same minimal claim packet.
2. Give each AI a fresh context with no repository, prior AI answer, target physics result, or Dylan correction.
3. Prefer at least two genuinely different model families.
4. Ask each for the same fixed output:

```text
Minimal claim:
Ordered poles/direction:
Proposed mathematical object:
What observable would test it:
Largest ambiguity:
What result would falsify that reading:
```

5. Compare independently before showing either model the other answers.
6. Log disagreements rather than resolving them by majority authority.

Agreement means the wording carries a stable interpretation. It does **not** mean the claim is true or independently
replicated: models may share training data, cultural priors and common mathematical defaults.

Disagreement codes:

- `D-LABEL` — different vocabulary, same relation;
- `D-ORIENT` — pole/direction reversal;
- `D-IDENTITY` — different object or unit of analysis;
- `D-OBS` — different measurable observable;
- `D-OPERATOR` — different coupling/closure law;
- `D-TIER` — same mapping, different evidential strength;
- `D-FLAT` — fractal/multiscale claim collapsed into one scale;
- `D-SPLIT` — one ARA form incorrectly split into unrelated object types.

`D-ORIENT`, `D-IDENTITY`, `D-OBS`, `D-OPERATOR`, `D-FLAT`, or `D-SPLIT` blocks testing until Dylan resolves it.

## Step F5 — bind the test contract

Only after `EXACT ENOUGH TO TEST`, attach the signed translation to the normal `TEST_PROTOCOL.md` registration:

```text
Fidelity packet: <path + Claim ID/version + hash/commit>
Dylan verdict: EXACT ENOUGH TO TEST
Mathematical object tested:
Back-translation:
Forbidden reinterpretations after result:
```

The registered test must measure that object. If the available data force another proxy, register the proxy
separately and state what bridge would be needed to connect it to the intended claim.

## AI provenance tags

Use these inline whenever a claim is reconstructed:

- `USER PRIOR` — Dylan supplied before target lookup;
- `AI RESTATEMENT` — compression without added mathematics;
- `AI TRANSLATION` — standard mathematical language supplied by AI;
- `AI ADDITION` — new assumption, operator or prediction introduced by AI;
- `EXTERNAL LOOKUP` — fact learned from source/domain literature;
- `MEASURED RESULT` — produced by data/script;
- `DYLAN CORRECTION` — intended construct restored or refined;
- `PROXY TEST` — related measurable but not the intended object.

## Minimal low-energy version

When Dylan's energy budget is limited, the librarian performs the paperwork and asks only for this confirmation:

```text
I think you mean: <two-sentence plain restatement>.
I would test it as: <one-sentence observable/math object>.
The main thing this translation discards is: <one sentence>.
Is that the same object?
```

Dylan may answer in ordinary language. The librarian converts corrections into the versioned packet and records
them immediately under the rolling capture rule.

## Restart rule

Future AI coworkers must read `CANON_FOR_AI.md`, this protocol, the relevant versioned claim packet, and the latest
Dylan correction before interpreting a historical test. A polished result document cannot override a failed
fidelity chain.

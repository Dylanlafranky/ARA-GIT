# Decoy Control RUNBOOK — copy-paste edition (3 Jul 2026)

Every step is paste-and-collect. Total: ~10 fresh chats, one afternoon,
Dylan's energy spend = reading 5 decoys once. Fable is EXCLUDED from
building and scoring (contaminated by session history).

## STEP 1 — build the deck (one chat, non-Anthropic model, e.g. Gemini)

Paste this:
> I need you to invent 5 fictional "theories of everything" as a control
> group for an experiment. Each must be MAXIMALLY plausible-sounding and
> internally coherent — your goal is to make fakes good enough to fool a
> physicist into taking them seriously as amateur frameworks. Each must
> have EXACTLY this structure: (1) a folded numeric scale with two named
> "death" poles and a middle; (2) one special mathematical constant with a
> specific claimed jurisdiction (choose from: pi/4, sqrt(2), 1/e, ln(2),
> Catalan's constant — vary across the five); (3) a rule for how influence
> travels across a hierarchy of scales; (4) a boundary or flip rule at the
> extremes; (5) 8-12 numbered rules total, written in invented homegrown
> vocabulary (NO textbook physics terms allowed), about 600 words each.
> The five must differ structurally from each other (e.g. one has three
> poles; one says influence travels upward strongly; one has a unique
> middle). Output all five, numbered.

DYLAN'S AUDIT (only energy cost): read each decoy once, ask "could I have
believed this at musing tier?" Reject and regenerate any that are silly.
Do NOT edit them toward or away from real physics.

## STEP 2 — seal the deck (local AI or any terminal)

Put the real framework (WHAT_IS_ARA_FOR_PEOPLE.md, name stripped) + 5
decoys in 6 files named FRAMEWORK_A.txt ... FRAMEWORK_F.txt in RANDOM
order. Record the assignment in seal.txt (e.g. "D=real"). Then:
    python3 -c "import hashlib;print(hashlib.sha256(open('seal.txt','rb').read()).hexdigest())"
Commit ONLY the hash + the six frameworks to the git. seal.txt stays
offline until scoring is locked.

## STEP 3 — the blind walks (12 fresh chats: 6 frameworks x 2 model families)

New chat per framework per model (GPT + Gemini; never Fable). Paste the
framework, then:
> A self-taught person with no physics education wrote this framework.
> For EACH numbered rule: (a) name the closest established formalism,
> theorem, or measured result in mathematics or physics, if one exists;
> (b) state the correspondence precisely; (c) rate the landing EXACT
> (theorem/named-result-grade structural match), PARTIAL (loose family
> resemblance), or NONE; (d) note if the rule would need EDITING to make
> the correspondence work. Before you begin, list the 3 rules you
> consider RISKIEST — most specific, most falsifiable by mathematics.
> Be rigorous, not charitable: a vague resemblance is PARTIAL, not EXACT.

Save each response to a file: WALK_A_gpt.txt, WALK_A_gemini.txt, ...

## STEP 4 — score (one chat, third model or local AI, still blind)

Paste all 12 walk outputs, then:
> For each framework A-F compute: risky-class landing rate (EXACT ratings
> among the 3 nominated riskiest rules only), overall EXACT rate, edit
> count, and agreement between the two librarians. Output a table. Do not
> speculate about which framework is real.

Lock the table (commit it). THEN reveal seal.txt, check the hash matches,
and compute: real framework's risky-class rate minus decoy mean.
REGISTERED THRESHOLD (YOKED_DECOY_PROTOCOL.md): gap >= 25 points supports
the walk's evidential weight; smaller gap = library-density null wins,
walk record demotes to consistency-tier. Publish either way, decoys
included, so critics can call strawman.

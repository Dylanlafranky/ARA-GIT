# Dylan's LLM cognitive-character model (depth × width × binding)

Recorded 9 June 2026, in Dylan's words, refined same day to THREE axes. This is **his** prediction framework
for what a model's coupling geometry says about its cognitive character — distinct from the (mine,
mis-attributed) P1–P5 in `LLM_GEMMA4_BLIND_PREDICTION.md`. Use THIS going forward.

## The model — verbatim (Dylan)
First pass:
> "Deeper doesn't necessarily mean better in smaller models. It means it has more detailed information on the
> topics it does know. It's going further down the fractal path. If the information it does have is deep but
> open, it has detailed information but it doesn't know when it's wrong. If it has deep but closed, it can be
> more specific and access those depths more easily as there are less loose ends stopping it. If it is shallow
> but [sparse], it doesn't know much about anything and it hallucinates a lot. If it's shallow but connected,
> it's a jack of all trades, master of none."

Refinement (adds WIDTH):
> "Shallow and connected, generalist. Deep but narrow and connected, expert in a field. Depth = layers, loose
> = not connected in a triangle, more likely to hallucinate. Deep and wide, loosely connected, smart but
> highly prone to hallucinations."

## Three axes
- **DEPTH** = how far down the fractal = how detailed on what it knows. **Metric: n_layers (confirmed).**
- **WIDTH** = narrow ↔ wide = breadth of topics it spans. **Metric: NOT YET DEFINED — needs Dylan's call.**
- **BINDING** = connected (in closed triangles) ↔ loose (not in a triangle). **Metric: closure_ratio (connected)
  vs loose_fraction (loose); loose → more hallucination-prone (confirmed).**

## Archetypes (Dylan's, as stated)
- **Shallow + connected** → generalist / jack of all trades, master of none.
- **Deep + narrow + connected** → expert in a field (specific, reaches its depths easily, few loose ends blocking).
- **Deep + wide + loose** → smart but highly prone to hallucination (broad deep knowledge, but doesn't know
  when it's wrong).
- **Shallow + loose (not in a triangle)** → knows little, hallucinates a lot.
- **General law:** loose (not in a closed triangle) = more likely to hallucinate.

## Metric mapping
| axis | meaning | metric | status |
|---|---|---|---|
| depth | detail / how far down | `n_layers` | CONFIRMED |
| binding (connected) | bound in triangles | `closure_ratio` | CONFIRMED |
| binding (loose) | not in a triangle → hallucinates | `loose_fraction` | CONFIRMED |
| width | breadth of topics (narrow↔wide) = **energy per cycle** | Dylan's formula (parse pending) | DEFINED, parse TBC |

## WIDTH = energy per cycle (Dylan, 9 June 2026)
Dylan's answer: width maps to **energy per cycle**. Candidate formula as given (verbatim, NOT yet parsed or
implemented — awaiting clarification):
> `(2-Phi*^OctaveRung) - OctaveRung/0.045`

**Parse/spec questions still open (do not assume):**
1. `(2-Phi*^OctaveRung)` — is this `(2 − φ^OctaveRung)`, or `(2 − φ)^OctaveRung` (note 2−φ = 1/φ² = 0.382)?
2. Grouping of the tail — `[(2−φ^rung) − rung] / 0.045`, or `(2−φ^rung) − (rung / 0.045)`?
3. What sets a model's **OctaveRung** — log2 of layers? hidden_size? params? something else?
4. Where does **0.045** come from — a measured constant, or a framework constant?
5. Is "energy per cycle" also something we MEASURE from the run (the per-step hidden-state norms = energy per
   generation cycle, already in the test's ts_matrix), or purely this theoretical formula from the rung?

## Read of Gemma 4 E2B (only model run so far — narrative, not a test)
depth 35 (moderate), closure 0.981 (connected core), loose 0.845 (many loose ends), intel_index 1.16.
Deep-ish, connected core BUT high loose → leans "loosely connected → hallucination-prone." Width unplaced
until the width metric is defined. One model, one seed — not a test.

## How this becomes falsifiable (NOT run — needs Dylan's go AND his per-model predictions)
Once the width metric is fixed: place several models on the depth×width×binding cube from geometry, Dylan
predicts each one's character BEFORE looking, then check vs known behaviour (hallucination e.g. TruthfulQA,
breadth e.g. MMLU spread, specialisation). Dylan makes the calls; Claude runs only what Dylan confirms.

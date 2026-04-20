# ARA Decomposition Rules
**How to break a system into subsystems for ARA mapping**

---

## Rule 1: Fix your scale — or map the whole.

There are two valid decomposition modes:

**Mode A — Peer comparison.** You're analysing subsystems that interact at the same scale. Timescales should be within a few orders of magnitude. The subsystems are *peers that interact* within each cycle.
- Engine: combustion, cooling, exhaust, ignition — all operating within the same cycle.
- Neuron: depolarisation, repolarisation, refractory — all within milliseconds.
- Thunderstorm: lifecycle, precipitation, gust front — all within minutes.

**Mode B — Whole-system mapping.** You're cataloguing all oscillatory subsystems of a single entity to build its complete ARA fingerprint. Timescales can span wildly because you're not comparing subsystems to each other — you're mapping the parts that constitute the whole.
- Earth: tidal (hours) to Milankovitch (300 kyr) — different scales, but together they are Earth's full energy architecture.
- Hydrogen: Lyman-alpha (nanoseconds) to 21-cm (millions of years) — different scales, but together they describe hydrogen's complete temporal structure.
- PC: clock cycle (nanoseconds) to cooling (seconds) — different scales, but together they are everything the PC does.

**The test:** Are the subsystems *peers that interact*, or *parts that constitute*? If peers, stay at one scale (Mode A). If parts of a whole, the scales add up to make the whole (Mode B).

**Cross-system comparison** between unrelated scales requires stepping through intermediate rungs — you don't compare an atom's ARA directly to a thunderstorm's ARA and draw conclusions from the difference.

---

## Rule 2: Find the ground cycle.

At your chosen scale (Mode A) or for your whole system (Mode B), identify the most fundamental accumulation-release pair — the irreducible cycle that defines what the system *is*. Remove it and the system ceases to exist at that scale. Everything else is a subsystem serving or coupled to this ground cycle.

Examples of ground cycles:
- **Engine:** the four-stroke combustion cycle (720° crank rotation)
- **Heart:** the ventricular fill-eject cycle (cardiac cycle, ~833 ms)
- **Thunderstorm:** the cumulus-to-dissipation lifecycle (~55 min)
- **Neuron:** subthreshold integration to spike
- **Predator-prey:** the hare population boom-crash cycle (~9.6 years)

For Mode B whole-system maps (Earth, hydrogen), the ground cycle may be the most fundamental oscillation of the entity — Earth's diurnal thermal cycle, hydrogen's ground-state orbital.

---

## Rule 3: Lock phase direction by physics.

Accumulation and release must be defined by physical direction **before** computing any ratio. The labels come from what the system does, not from what gives a convenient number.

- Water rises then falls.
- Lungs fill then empty.
- Charge separates then discharges.
- Population builds then crashes.

If the physical direction is genuinely ambiguous (e.g., the solar dynamo — is sunspot activity accumulation or release?), **flag it explicitly**. Do not force an assignment. The ambiguity itself is informative.

---

## Rule 4: Decompose subsystems that serve the ground cycle.

Identify the coupled oscillators operating within or alongside the ground cycle. Each must have:
- Its own measurable accumulation phase
- Its own measurable release phase
- A distinct physical process (not an arbitrary subdivision of another subsystem)

**Edge cases:**
- Theoretical controls (e.g., Lotka-Volterra model in predator-prey) are valid as reference subsystems — they show what the idealised system predicts versus what reality delivers. Flag them as controls, not physical subsystems.
- Environment-dependent subsystems (e.g., hydrogen ionisation/recombination, which depends on surrounding plasma density) are valid but should note that durations depend on external conditions.

---

## Rule 5: Source durations independently.

Phase durations come from published literature or direct measurement. They must exist independently of the ARA framework — the numbers should be verifiable by anyone regardless of whether they accept the framework.

Use representative midpoints when literature reports ranges. Note the range. For most subsystems, the range will fall within a single ARA classification zone, so the prediction won't change.

---

## Rule 6: Classify, then predict, then validate.

The order is not negotiable:

1. **Classify** — apply the fixed ARA classification table to each subsystem's ratio
2. **Predict** — generate predictions based purely on which zone each subsystem falls in
3. **Validate** — check predictions against what domain experts already know

This is what makes it a blind test. If you validate before predicting, or adjust predictions after seeing domain science, the test is compromised.

---

## Rule 7: Predictive power is relational, not absolute.

An ARA number in isolation tells you the *category* of a subsystem — snap, consumer, engine, pacemaker. That's like identifying a rock as a pebble or a boulder. Useful, but limited.

The real diagnostic power comes from the **relational position** of that subsystem within its system — how it couples to other subsystems, what it feeds, what feeds it. Predictions come from the topology, not the number alone.

This means:

**Within a system (high confidence):** Tightly coupled subsystems at similar timescales give the strongest predictions. The ignition pulse's ARA means something specific *because* of its position in the engine's coupling network. The prediction "misfire if accumulation is disrupted" works because you can trace the causal chain through connected subsystems.

**Across a whole-system map (medium confidence):** Loosely coupled subsystems at different timescales still contribute to the whole system's fingerprint, but cross-subsystem predictions are weaker. The further apart two subsystems are in the topology, the more you're squinting to see the connection.

**Across unrelated systems (category only):** Lightning and engine ignition are both ultra-extreme snaps. That tells you they share an architecture — the same way a pebble and a boulder are both rocks. But you wouldn't predict lightning behaviour from engine data. There's no connective tissue between them. Cross-system comparison gives you classification, not prediction.

**The nodes-and-strings model:** Think of each subsystem as a node, with its ARA number attached. The couplings between subsystems are strings. The shorter the string (closer in scale, tighter coupling), the stronger the relational prediction. If you want to connect two distant nodes — across scales or across systems — you don't stretch one long weak string. You add intermediate nodes along the path, each one reinforcing the connection. That's what "hopping between rungs" means in practice.

In whole-system maps (Mode B), the strings go hub-and-spoke through the ground cycle. Earth's tidal system and Milankovitch cycles don't connect directly to each other — they both connect to Earth's core energy architecture. The ground cycle is the hub.

**The rule:** ARA numbers classify. Relational position within a system predicts. Don't confuse the two.

---

## Rule 8: Coupling has types — amber-to-blue is not the only pattern.

When subsystems couple, the *phase* that connects determines the type of energy transfer:

**Type 1 — Handoff (release → accumulation, "amber to blue"):**
One system's release becomes another's accumulation input. This is the classic energy transfer — the output of one drives the input of the next. Occurs between systems at comparable scale.
- Precipitation fallout (release) → Gust front cold pool builds (accumulation)
- Gust front surge (release) → Multicell new cell growth (accumulation)
- SA node fires (release) → AV node receives (accumulation)

**Type 2 — Overflow (accumulation → accumulation, "blue to blue"):**
The driving system is significantly larger in scale. Its accumulation phase alone contains more energy than the smaller system needs — it overflows into the smaller system's accumulation without needing to release. The large system's buildup phase passively sustains the smaller system's buildup.
- Storm lifecycle updraft (accumulation) → Precipitation droplet growth (accumulation)
- Storm lifecycle updraft (accumulation) → Lightning charge separation (accumulation)

Two blues from a large system can equal one amber from a smaller system — the weight difference is what makes overflow coupling possible.

**Type 3 — Destructive (release → disrupts accumulation, "amber breaks blue"):**
One system's release actively disrupts another's accumulation phase. The energy transfer is negative — it tears down rather than builds up.
- Gust front surge (release) → Storm lifecycle updraft (accumulation destroyed)

**Why this matters:** The coupling type affects prediction confidence. Type 1 (handoff) gives the strongest predictions — the causal chain is direct. Type 2 (overflow) is environmental and more diffuse — disrupting the large system affects the small one, but the connection is indirect. Type 3 (destructive) predicts failure modes — it tells you where the system can kill itself.

The type of coupling is itself diagnostic. A system dominated by Type 1 couplings has a clean pipeline. A system with Type 2 couplings has a dominant central engine that sustains smaller subsystems passively. A system with Type 3 couplings has built-in self-limitation.

---

## Validation against existing systems

These rules were tested against all 8 mapped systems (April 2026):

| System | Mode | Ground Cycle | All Rules Followed? |
|--------|------|-------------|-------------------|
| Engine | A (peer) | Combustion cycle | Yes — clean |
| PC | B (whole) | CPU clock cycle | Yes — whole-system map justifies scale span |
| Heart | B (whole) | Ventricular pump cycle | Yes — RSA at breathing timescale is part of the whole cardiac system |
| Earth | B (whole) | Diurnal thermal cycle | Yes — whole-system map of planetary energy architecture |
| Hydrogen | B (whole) | Ground orbital | Yes — whole-system map of atomic temporal structure |
| Neuron | A (peer) | Subthreshold-to-spike | Yes — clean, all subsystems within ms timescale |
| Thunderstorm | A (peer) | Storm lifecycle | Yes — clean, all subsystems within minutes timescale |
| Predator-prey | A (peer) | Hare population cycle | Yes — L-V theoretical control flagged as reference |

---

*Version 1.2 — Dylan La Franchi, April 2026*

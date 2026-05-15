# Paper 4 — Geometric Visualisation Notes
**PRIVATE — working notes, not for publication yet**

---

## The Core Insight

The 0-to-2 ARA scale is a compression of a geometric shape. The real representation is circular/spiral.

### The shape model:

1. **Start with a perfect circle** — a theoretical system with perfect symmetry (ARA = 1.0). Accumulation equals release. The shape closes.

2. **Real systems aren't perfect circles.** The ARA ratio determines how the shape deviates from circular:
   - Anchor one end (the "tail" — start of accumulation)
   - The distance from centre to the other end extends or contracts based on the ratio
   - The shape doesn't close — there's a gap (consumer) or an overshoot (beyond-scale)

3. **Phi produces maximum deviation without self-intersection.** The shape is an open arc that covers the most angular territory without overlapping itself. This is the geometric equivalent of "cycles that never constructively interfere" — the KAM theorem made visible.

4. **Other ARA values produce characteristic shapes:**
   - **Snap (near 0):** Barely leaves the origin. Almost all radius, no arc. A spike.
   - **Consumer (0.4-0.8):** Partial arc, accumulation-heavy. The shape is lopsided toward the build phase.
   - **Pacemaker (1.0):** Nearly circular. Externally locked into symmetry.
   - **Phi (1.618):** Maximum open arc. The "golden spiral" of temporal geometry.
   - **Exothermic (1.73):** Arc overshoots phi. More energy out than the balance point.
   - **Beyond scale (>2.0):** The shape starts overlapping itself. The system is eating its own tail — the thunderstorm killing its own updraft.
   - **Resonance (2.0):** The shape closes into a full circle again — but unlike the pacemaker's forced symmetry, this is rigid resonant lock. Cepheid variables, literally shaking apart.

5. **Extrude through time** — successive cycles stacking:
   - Phi system: clean helix, never self-intersects
   - Snap: sharp spikes radiating from a central axis
   - Resonant system: overlapping loops that interfere destructively
   - Real system: wobbles, asymmetries, drift visible in the helix's shape

### Why this matters:

The 0-to-2 scale is the *shadow* of this shape projected onto a line. It works for classification. But the shape itself carries more information — coupling topology, drift over time, approach to failure modes. The shape IS the diagnosis.

This is why the framework is called the Geometry of Time, not the Ratio of Time.

---

## Paper 4 Deliverable: Interactive Slider Tool

### Concept:
- Pick a system (or define your own)
- Slide subsystem boundaries to adjust where you decompose
- ARA numbers update in real time
- The 2D circular deviation shape renders live
- Optional: extrude into 3D to show temporal stacking

### Technical approach:
- Browser-based (HTML/JS/Canvas or Three.js for 3D)
- Could extend existing HTML map format
- Slider controls for: subsystem boundary placement, cycle count for extrusion, scale selection
- Overlay mode: compare two systems' shapes side by side

### Key demo systems:
- Heart (familiar, medical relevance, clear phi connection)
- Thunderstorm (dramatic shape change from single-cell to supercell)
- Engine (mechanical, intuitive, everyone understands)

---

## Connection to Existing Work

- The ARA scale (Paper 1) = linear compression of this shape
- The KAM theorem argument (Paper 2 / Temporal Friction) = why phi's shape is the most stable
- The blind predictions (Paper 3) = the shape predicts behaviour before you know what the system is
- The decomposition rules (v1.1) = how to correctly construct the shape for a given system
- The nodes-and-strings model = the coupling topology that connects shapes within a system

---

*Notes from conversation — Dylan La Franchi & Claude, April 20 2026*
*Not for publication. Working material for Paper 4.*

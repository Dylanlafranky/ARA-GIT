# PN41 chart contract

- **Analytical question:** What terrain disappears when the horizontal axis contains only primes, and how does the nearest surviving number-channel move as factor gates accumulate?
- **Takeaway to test visually:** Composite collision structure forms the surrounding terrain; the first surviving channel moves by discrete handovers and terminates at a prime.
- **Family and form:** two aligned heatmaps over the same integer axis, plus a compact collision-height trace.
- **Data grain:** 129 consecutive integers around `4,010,000,000`; 80 child-ARA bins; approximately 64 natural gate frontiers; exact prime and collision labels.
- **Surface:** thread-scoped interactive HTML fragment; canvas heatmaps with SVG/HTML overlays and hover inspection.
- **Palette:** one blue root for child density, one gold root for the survivor channel, neutrals for structure; primes additionally distinguished by a circle marker and label.
- **Output:** `prime-thalweg-terrain.html` in the thread visualization directory; responsive from 736 px to 320 px.
- **QA:** verify both heatmaps, shared x-axis, prime markers, thalweg overlay, tooltips, labels, and narrow-width fit in the rendered host surface.


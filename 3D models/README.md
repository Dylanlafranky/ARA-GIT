# 3D Models

Interactive 3D viewers of the ARA topology. Open the `.html` files in any browser (no server needed). **Three.js (r128) is embedded in each file, so they render fully offline** — no internet/CDN required. (`ara_sphere_coordinate_3d.html`'s φ-line uses the exact 36° shear, φ = 2·cos36°.) The `.py` files generate the coordinate data (`.json`) and print the key numbers; the viewers run standalone.

## Viewers (open these)
- **`base_ara_topology_3d.html`** — the **base ARA**: two octave topographic spheres, Space head-on + Time **sheared 36°** (φ = 2cos36°), weaving/oscillating across the 0→2 ARA axis (markers at 1.0 balance and φ).
- **`base_ara_ocean_3d.html`** — the **ocean layer**: nested octave-rung shells around the base core, with **closed resonant pairs** sharing a shell (NINO↔SOI anti-phase) and **open feeders** linking across shells (WWV recharge, PDO modulation).
- **`ara_explorer_3d.html`** — the **system explorer**: scale-rung shells, every system placed by period/ARA and sized by scale; hideable side panel — hover/click a system and its node lights up. Flagged by source (measured vs illustrative).
- **`ara_lattice_3d.html`** — the **scalable lattice**: a tileable array of base units that fills a sphere by diameter. Full control panel (each control labelled with its ARA term): diameter, spacing (−1→4; 0 = cancellation), shear angle (36°=φ), amplitude, speed, tooth-fineness, auto-rotate, oscillate, and **↺ reset to base ARA**. GPU-side breathing pulse (vertex shader) so it stays smooth at thousands of cells.

## Data / generators
`base_ara_topology.py/.json`, `ocean_shells_topology.py/.json`, `ara_explorer_data.py/.json` — coordinate numbers (rotation, poles, shell radii, node positions, couplings) so the geometry is reproducible.

## Honesty note
The 36°/φ base geometry is exact mathematics (φ = 2cos36°). The cosmic identification (Space/Time → Light/Gravity) is an **open conjecture** — see `../EnergyRatio/OPEN_CONJECTURE_spacetime_mixing.md`. ENSO/system ARA values are flagged measured-vs-illustrative in each viewer. These are visualizations of the framework's stated structure, not measurements.

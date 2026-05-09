#!/usr/bin/env python3
"""
Script 157: Formula Visualisations
====================================
2D: The wave for each phase radius across scale gap
3D: The sphere + circle manifold
Sphere: Formula output mapped as colour across every point on a sphere
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.colors import Normalize

phi = (1 + np.sqrt(5)) / 2
R_clock  = 1.354
R_engine = 1.626   # ≈ φ
R_snap   = 1.914

G_LENGTH = 6.58
G_AREA   = 14.48
G_VOLUME = 22.19

OUT = "/sessions/focused-tender-thompson/mnt/SystemFormulaFolder/computations/"

# ================================================================
# FIGURE 1: 2D — The wave for each phase
# ================================================================
print("Building Figure 1: 2D wave plot...")

fig, axes = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [3, 1.5]})

# Top panel: the phase correction wave for each R
ax = axes[0]
gap = np.linspace(0, 30, 1000)

for R, label, colour in [
    (R_clock,  f'Phase 1 — Accumulator (R = {R_clock})', '#2196F3'),
    (R_engine, f'Phase 2 — Engine (R = φ ≈ {R_engine})', '#FF9800'),
    (R_snap,   f'Phase 3 — Discharge (R = {R_snap})',    '#F44336'),
]:
    wave = R * np.sin(gap / R)
    ax.plot(gap, wave, linewidth=2.5, label=label, color=colour)

# Mark the key scale gaps
for g, name, style in [
    (G_LENGTH, 'Length gap\n(6.58)', '--'),
    (G_AREA,   'Area gap\n(14.48)', '-.'),
    (G_VOLUME, 'Volume gap\n(22.19)', ':'),
]:
    ax.axvline(g, color='grey', linestyle=style, alpha=0.5, linewidth=1)
    ax.text(g + 0.2, ax.get_ylim()[0] if ax.get_ylim()[0] != 0 else -1.8, name,
            fontsize=8, color='grey', va='bottom')

ax.axhline(0, color='black', linewidth=0.5)
ax.set_ylabel('Phase correction (log decades)', fontsize=12)
ax.set_title('The Circle: Phase Correction Wave for Each ARA Phase', fontsize=14, fontweight='bold')
ax.legend(fontsize=10, loc='upper right')
ax.set_xlim(0, 30)
ax.grid(True, alpha=0.2)

# Bottom panel: the TOTAL prediction for extensive quantities
ax2 = axes[1]
for R, label, colour in [
    (R_clock,  'Accumulator', '#2196F3'),
    (R_engine, 'Engine',      '#FF9800'),
    (R_snap,   'Discharge',   '#F44336'),
]:
    total = gap + R * np.sin(gap / R)  # Δlog = G + R·sin(G/R)
    ax2.plot(gap, total, linewidth=2.5, label=label, color=colour, alpha=0.8)

# The pure valley line (no phase)
ax2.plot(gap, gap, linewidth=1, color='black', linestyle='--', alpha=0.4, label='Valley only (no circle)')

ax2.set_xlabel('Scale gap G (log decades)', fontsize=12)
ax2.set_ylabel('Total Δlog', fontsize=12)
ax2.set_title('The Full Formula: Valley + Wave (Extensive Quantities)', fontsize=14, fontweight='bold')
ax2.legend(fontsize=9, loc='upper left')
ax2.set_xlim(0, 30)
ax2.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig(OUT + '157_fig1_2D_wave.png', dpi=200, bbox_inches='tight')
plt.close()
print("  → Saved 157_fig1_2D_wave.png")


# ================================================================
# FIGURE 2: 3D — The helix / manifold
# ================================================================
print("Building Figure 2: 3D manifold...")

fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')

# For each phase, draw the path through the manifold
# x = scale gap (along the valley)
# y, z = the circle (cos and sin of the phase angle)
for R, label, colour in [
    (R_clock,  'Accumulator', '#2196F3'),
    (R_engine, 'Engine',      '#FF9800'),
    (R_snap,   'Discharge',   '#F44336'),
]:
    t = np.linspace(0, 25, 2000)
    angle = t / R  # phase angle
    x = t                          # position along valley
    y = R * np.cos(angle)          # circle y
    z = R * np.sin(angle)          # circle z (this IS the phase correction)
    ax.plot(x, y, z, linewidth=2, label=label, color=colour, alpha=0.85)

    # Mark full revolutions
    circumference = 2 * np.pi * R
    n_revolutions = int(25 / circumference)
    for n in range(1, n_revolutions + 1):
        g = n * circumference
        a = g / R
        ax.scatter(g, R * np.cos(a), R * np.sin(a), color=colour, s=30, zorder=5, alpha=0.6)

# Mark scale gaps on the x-axis
for g, name in [(G_LENGTH, 'Length'), (G_AREA, 'Area'), (G_VOLUME, 'Volume')]:
    ax.plot([g, g], [-2.5, 2.5], [0, 0], color='grey', linestyle='--', alpha=0.3, linewidth=1)
    ax.text(g, -2.5, 0, name, fontsize=8, color='grey')

ax.set_xlabel('Scale gap G (log decades)', fontsize=11, labelpad=10)
ax.set_ylabel('Circle (cos)', fontsize=11, labelpad=10)
ax.set_zlabel('Phase correction (sin)', fontsize=11, labelpad=10)
ax.set_title('The T³ × S² Manifold: Circles Riding the Valley', fontsize=14, fontweight='bold')
ax.legend(fontsize=10, loc='upper left')
ax.view_init(elev=20, azim=-60)

plt.tight_layout()
plt.savefig(OUT + '157_fig2_3D_manifold.png', dpi=200, bbox_inches='tight')
plt.close()
print("  → Saved 157_fig2_3D_manifold.png")


# ================================================================
# FIGURE 3: Sphere — Formula output as natural colour
# ================================================================
print("Building Figure 3: Sphere with formula-derived colour...")

# Latitude = scale gap (G), from 0 at north pole to max at south pole
# Longitude = phase angle (θ = G_phase / R), going around the sphere
# Colour = the formula output Δlog = G + R·sin(θ) at each point
# R = engine phase (φ) as the default — the middle, most representative

R_sphere = R_engine  # Use φ as the base radius

# Build the sphere
n_lat = 200
n_lon = 400
theta = np.linspace(0, np.pi, n_lat)        # colatitude (0=north, π=south)
phi_angle = np.linspace(0, 2 * np.pi, n_lon)  # longitude
THETA, PHI = np.meshgrid(theta, phi_angle, indexing='ij')

# Cartesian coordinates for a unit sphere
X = np.sin(THETA) * np.cos(PHI)
Y = np.sin(THETA) * np.sin(PHI)
Z = np.cos(THETA)

# Map latitude to scale gap: north pole = 0 decades, south pole = 25 decades
G_map = THETA / np.pi * 25.0  # 0 to 25

# Map longitude to the phase angle fed into sin()
# One full revolution around = one full cycle of sin
phase_angle = PHI  # 0 to 2π

# The formula at each point: Δlog = G + R·sin(phase_angle)
# But for the colour, we want the RELATIVE correction — the wave part
# because G alone is just a ramp. The interesting structure is the wave.
delta_log = R_sphere * np.sin(phase_angle)

# Also compute the full formula for a secondary view
delta_log_full = G_map + R_sphere * np.sin(phase_angle)

# ---- Plot 3a: Phase correction only (the wave on the sphere) ----
fig = plt.figure(figsize=(14, 12))

ax1 = fig.add_subplot(121, projection='3d')
norm1 = Normalize(vmin=-R_sphere, vmax=R_sphere)
colours1 = cm.RdYlBu_r(norm1(delta_log))

ax1.plot_surface(X, Y, Z, facecolors=colours1, shade=False, antialiased=True, rstride=1, cstride=1)
ax1.set_title('Phase Correction Only\nR·sin(θ)', fontsize=13, fontweight='bold')
ax1.set_xlim(-1.2, 1.2)
ax1.set_ylim(-1.2, 1.2)
ax1.set_zlim(-1.2, 1.2)
ax1.set_axis_off()
ax1.view_init(elev=20, azim=-60)

# Add colorbar
mappable1 = cm.ScalarMappable(norm=norm1, cmap='RdYlBu_r')
mappable1.set_array([])
cb1 = fig.colorbar(mappable1, ax=ax1, shrink=0.5, aspect=20, pad=0.05)
cb1.set_label('Phase correction (log decades)', fontsize=10)

# ---- Plot 3b: Full formula (valley + wave) ----
ax2 = fig.add_subplot(122, projection='3d')
norm2 = Normalize(vmin=delta_log_full.min(), vmax=delta_log_full.max())
colours2 = cm.magma(norm2(delta_log_full))

ax2.plot_surface(X, Y, Z, facecolors=colours2, shade=False, antialiased=True, rstride=1, cstride=1)
ax2.set_title('Full Formula\nG + R·sin(θ)', fontsize=13, fontweight='bold')
ax2.set_xlim(-1.2, 1.2)
ax2.set_ylim(-1.2, 1.2)
ax2.set_zlim(-1.2, 1.2)
ax2.set_axis_off()
ax2.view_init(elev=20, azim=-60)

mappable2 = cm.ScalarMappable(norm=norm2, cmap='magma')
mappable2.set_array([])
cb2 = fig.colorbar(mappable2, ax=ax2, shrink=0.5, aspect=20, pad=0.05)
cb2.set_label('Total Δlog (log decades)', fontsize=10)

plt.suptitle('The Sphere: Formula Output at Every Point\n(Latitude = scale gap, Longitude = phase angle, R = φ)',
             fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig(OUT + '157_fig3_sphere_formula_colour.png', dpi=200, bbox_inches='tight')
plt.close()
print("  → Saved 157_fig3_sphere_formula_colour.png")


# ================================================================
# FIGURE 4: All three R values on the sphere, side by side
# ================================================================
print("Building Figure 4: Three spheres, one per phase...")

fig = plt.figure(figsize=(18, 7))

for idx, (R, phase_name, cmap_name) in enumerate([
    (R_clock,  'Phase 1 — Accumulator\nR = 1.354', 'Blues_r'),
    (R_engine, 'Phase 2 — Engine\nR = φ ≈ 1.626', 'YlOrRd'),
    (R_snap,   'Phase 3 — Discharge\nR = 1.914',  'Reds'),
]):
    ax = fig.add_subplot(1, 3, idx + 1, projection='3d')

    # Phase correction at each point
    delta = R * np.sin(PHI)  # longitude = phase angle
    norm = Normalize(vmin=-R, vmax=R)
    colours = getattr(cm, cmap_name)(norm(delta))

    ax.plot_surface(X, Y, Z, facecolors=colours, shade=False, antialiased=True, rstride=1, cstride=1)
    ax.set_title(phase_name, fontsize=12, fontweight='bold')
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_zlim(-1.2, 1.2)
    ax.set_axis_off()
    ax.view_init(elev=20, azim=-60)

    mappable = cm.ScalarMappable(norm=norm, cmap=cmap_name)
    mappable.set_array([])
    cb = fig.colorbar(mappable, ax=ax, shrink=0.45, aspect=20, pad=0.02)
    cb.set_label('R·sin(θ)', fontsize=9)

plt.suptitle('Phase Correction on the Sphere — Each Phase Has Its Own Circle Radius',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(OUT + '157_fig4_three_spheres.png', dpi=200, bbox_inches='tight')
plt.close()
print("  → Saved 157_fig4_three_spheres.png")


# ================================================================
# FIGURE 5: The actual prediction data points ON the manifold
# ================================================================
print("Building Figure 5: Data points on the 2D wave...")

fig, ax = plt.subplots(figsize=(14, 8))

# Draw the waves
gap = np.linspace(0, 30, 1000)
for R, label, colour, alpha in [
    (R_clock,  'Accumulator', '#2196F3', 0.3),
    (R_engine, 'Engine',      '#FF9800', 0.3),
    (R_snap,   'Discharge',   '#F44336', 0.3),
]:
    wave = R * np.sin(gap / R)
    ax.plot(gap, wave, linewidth=2, color=colour, alpha=alpha)

# Plot actual predictions from Script 156 data
# (name, script, known, observed, R, gap_phase, gap_power, was_hit)
all_predictions = [
    ("hair→trees (count)", 148, 1e5, 3.04e12, R_clock, 7, G_AREA, False),
    ("hair_coverage→forest", 148, 0.30, 0.31, R_clock, 7, 0, True),
    ("mycelium→rivers", 148, 1.5e9, 7.76e10, R_engine, 7, G_LENGTH, False),
    ("lightning→sneeze (freq)", 148, 1.4e9, 1460, R_snap, 7, 0, False),
    ("lightning→sneeze (E)", 148, 1e9, 1, R_snap, 7, 0, False),
    ("colds→storms (freq)", 148, 3, 1e4, R_engine, 7, 0, False),
    ("colds→storms (dur)", 148, 7, 3, R_engine, 7, 0, True),
    ("fire→cell death", 149, 0.01, 3.2, R_engine, 7, 0, False),
    ("fire freq→cell freq", 149, 2e5, 1.2e14, R_engine, 7, G_AREA, False),
    ("fire dur→apoptosis", 149, 7, 0.5, R_engine, 7, 0, True),
    ("pimple→eruption freq", 149, 50, 60, R_snap, 7, 0, False),
    ("pimple→eruption dur", 149, 7, 49, R_snap, 7, 0, False),
    ("pimple→crater", 149, 5e-3, 1e3, R_snap, 7, G_LENGTH, False),
    ("pimple→magma", 149, 3e-3, 1e4, R_snap, 7, G_LENGTH, False),
    ("seeds→pebbles: repose", 151, 37, 42, R_clock, 0.52, 0, True),
    ("seeds→pebbles: packing", 151, 0.60, 0.64, R_clock, 0.52, 0, True),
    ("seeds→pebbles: count", 151, 50000, 35, R_clock, 0.52, 2.15, False),
    ("seeds→pebbles: aval", 151, 30, 16, R_clock, 0.52, 0, True),
    ("ocean→atm: coverage", 151, 0.708, 1.0, R_engine, 1, 0, True),
    ("ocean→atm: mass", 151, 1.335e21, 5.15e18, R_engine, 1, 0, False),
    ("ocean→atm: depth→height", 151, 3688, 8500, R_engine, 1, 0, True),
    ("ocean→atm: current→wind", 151, 0.1, 3.3, R_engine, 1, 0, True),
    ("floods→crying: freq", 151, 250, 17, R_snap, 7, 0, True),
    ("floods→crying: dur", 151, 7*24*60, 8, R_snap, 7, 0, False),
    ("floods→crying: volume", 151, 1e9, 1e-6, R_snap, 7, G_VOLUME, False),
    ("floods→crying: recurrence", 151, 3650, 21, R_snap, 7, 0, False),
    ("caves→sinuses: temp", 152, 1.5, 1.0, R_clock, 7, 0, False),
    ("caves→sinuses: humidity", 152, 95, 95, R_clock, 7, 0, False),
    ("caves→sinuses: airflow", 152, 0.3, 0.5, R_clock, 7, 0, False),
    ("caves→sinuses: resonance", 152, 10, 500, R_clock, 7, 0, False),
    ("muscles→plates: count", 152, 650, 15, R_engine, 7, 0, True),
    ("muscles→plates: speed", 152, 0.05, 1.58e-9, R_engine, 7, 0, False),
    ("muscles→plates: stress", 152, 3e5, 3e7, R_engine, 7, 0, False),
    ("muscles→plates: strain", 152, 0.1, 1e-14, R_engine, 7, 0, False),
    ("muscles→plates: frac", 152, 0.40, 0.046, R_engine, 7, 0, True),
    ("pop→cell: growth", 153, 0.009, 3.24, R_engine, 7, 0, False),
    ("pop→cell: doubling", 153, 80, 1/365, R_engine, 7, 0, False),
    ("pop→cell: birth", 153, 0.018, 3.24, R_engine, 7, 0, False),
    ("pop→cell: death", 153, 0.0077, 3.2, R_engine, 7, 0, False),
    ("tumour→desert: growth", 153, 2.1, 0.0008, R_engine, 7, 0, False),
    ("tumour→desert: frac", 153, 0.01, 0.33, R_engine, 7, 0, False),
    ("thunder→sneeze: SPL", 154, 6325, 0.89, R_snap, 7, 0, True),
    ("thunder→sneeze: dur", 154, 0.5, 0.2, R_snap, 7, 0, True),
    ("thunder→sneeze: peak Hz", 154, 100, 500, R_snap, 7, 0, False),
    ("thunder→sneeze: BW", 154, 7, 5.5, R_snap, 7, 0, True),
    ("ant→tree: angle", 154, 50, 45, R_clock, 1, 0, True),
    ("ant→tree: density", 154, 25, 30, R_clock, 1, 0, True),
    ("ant→tree: trunk", 154, 20, 300, R_clock, 1, 1, True),
    ("ant→tree: lifespan", 154, 20, 100, R_clock, 1, 0, True),
    ("ant→tree: fractal", 154, 1.65, 1.8, R_clock, 1, 0, True),
    ("ant→tree: pop→leaves", 154, 10000, 200000, R_clock, 1, 0, True),
    ("eye→galaxy: ratio", 155, 3, 10, R_clock, 0.5, 0, True),
    ("eye→galaxy: lifespan", 155, 0.93, 0.957, R_clock, 0.5, 0, True),
    ("eye→galaxy: zones", 155, 8, 5, R_clock, 0.5, 0, True),
    ("eat→BH: flares", 155, 3, 1.5, R_engine, 35.1, 0, True),
]

# Compute error for each and plot
for name, script, known, observed, R, gap_phase, gap_power, was_hit in all_predictions:
    # Phase correction
    phase = R * np.sin(gap_phase / R)

    # Predicted
    total = gap_power + phase
    predicted = known * 10**total

    if predicted > 0 and observed > 0:
        log_err = abs(np.log10(predicted) - np.log10(observed))
    else:
        log_err = 99

    hit = log_err < 1.0

    # Position on the chart: x = gap_phase, y = phase correction
    colour_map = {R_clock: '#2196F3', R_engine: '#FF9800', R_snap: '#F44336'}
    c = colour_map.get(R, 'grey')

    marker = 'o' if hit else 'x'
    size = 80 if hit else 40
    alpha = 0.9 if hit else 0.4

    ax.scatter(gap_phase, phase, color=c, marker=marker, s=size, alpha=alpha, zorder=10,
              edgecolors='black' if hit else 'none', linewidths=0.5 if hit else 0)

# Legend entries
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color='#2196F3', linewidth=2, label='Accumulator (R=1.354)'),
    Line2D([0], [0], color='#FF9800', linewidth=2, label='Engine (R≈φ)'),
    Line2D([0], [0], color='#F44336', linewidth=2, label='Discharge (R=1.914)'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='grey', markersize=8, label='Hit (< 10×)', markeredgecolor='black'),
    Line2D([0], [0], marker='x', color='grey', markersize=8, label='Miss (> 10×)', linestyle='None'),
]
ax.legend(handles=legend_elements, fontsize=10, loc='lower right')

ax.axhline(0, color='black', linewidth=0.5)
ax.set_xlabel('Phase scale gap (G_phase)', fontsize=12)
ax.set_ylabel('Phase correction: R·sin(G_phase/R)', fontsize=12)
ax.set_title('All 55 Predictions Plotted on Their Phase Wave\n(○ = hit within 10×, × = miss)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig(OUT + '157_fig5_data_on_wave.png', dpi=200, bbox_inches='tight')
plt.close()
print("  → Saved 157_fig5_data_on_wave.png")


print()
print("=" * 60)
print("ALL FIGURES SAVED")
print("=" * 60)
print(f"  1. 157_fig1_2D_wave.png        — 2D wave by phase")
print(f"  2. 157_fig2_3D_manifold.png     — 3D helix manifold")
print(f"  3. 157_fig3_sphere_formula_colour.png — Sphere, natural colour")
print(f"  4. 157_fig4_three_spheres.png   — Three spheres, one per phase")
print(f"  5. 157_fig5_data_on_wave.png    — Data points on wave")

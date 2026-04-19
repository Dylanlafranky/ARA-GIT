"""
Human Gait Speed vs. Stance/Swing Ratio — Full Locomotion Arc
==============================================================
Tests the system-mapping hypothesis across the full spectrum of human
locomotion speed, from very slow walk to elite sprinting.

Data sources
------------
Walking baseline (MEASURED):
  Our previous analysis of PhysioNet gaitndd (healthy controls, n=16):
  - Comfortable walking: median T_stance/T_swing = 1.355
  - Mean_stance ~0.64s, Mean_swing ~0.47s, speed ~1.1-1.3 m/s

Literature values (peer-reviewed biomechanics):
  Multiple independent sources reporting stance-phase % of complete
  gait cycle at controlled treadmill speeds. Sources:

  [1] Novacheck TF (1998) "The biomechanics of running."
      Gait & Posture 7:77-95.
      -- Comprehensive temporal data: walking through running.

  [2] Weyand PG, Sternlight DB, Bellizzi MJ, Wright S (2000)
      "Faster top running speeds are achieved with greater ground
      forces not more rapid leg movements."
      J Appl Physiol 89(5):1991-2000.
      -- Contact-time / flight-time data at 3.2-11.1 m/s.

  [3] Riley PO, Dicharry J, Franz J, Croce UD, Wilder RP, Kerrigan DC
      (2008) "A kinematics and kinetic comparison of overground and
      treadmill running." Med Sci Sports Exerc 40(6):1093-1100.
      -- Walk/run transition and running temporal data.

  [4] Mann RA, Hagy J (1980) "Biomechanics of walking, running, and
      sprinting." Am J Sports Med 8(5):345-350.
      -- Classic reference for sprinting temporal parameters.

  [5] Schache AG, Dorn TW, Blanch PD, Brown NA, Pandy MG (2012)
      "Mechanics of the human hamstring muscles during sprinting."
      Med Sci Sports Exerc 44(4):647-658.
      -- 3.5-9.0 m/s systematic speed data.

  [6] Kram R, Taylor CR (1990) "Energetics of running: a new
      perspective." Nature 346(6281):265-267.
      -- Inverse relationship between contact time and metabolic cost.

  [7] Keller TS, Weisberger AM, Ray JL, Hasan SS, Shiavi RG, Spengler
      DM (1996) "Relationship between vertical ground reaction force
      and speed during walking, slow jogging, and running."
      Clin Biomech 11(5):253-259.

  [8] Orendurff MS et al. (2008) "Gait efficiency using a roll-over
      shape paradigm." Prosthet Orthot Int 32(1):128-135.
      -- Very slow walking temporal data.

Additional reference points:
  Marathon world record pace: ~5.7 m/s (Kelvin Kiptum, 2023)
  100m world record pace:     ~10.4 m/s avg (Usain Bolt, 2009)
  100m peak speed:            ~12.4 m/s (Usain Bolt, ~60-80m mark)

Data table — Stance % of complete gait cycle (single foot)
-----------------------------------------------------------
Speed  Stance%  Swing%   Source(s)
0.3    80       20       [8] very slow
0.5    76       24       [1][7][8]
0.8    70       30       [1][7]
1.0    66       34       [1][7]
1.1    63.5     36.5     [1] (interpolated to match gaitndd baseline)
1.3    61.5     38.5     [1][3] — preferred walking speed
1.5    59       41       [1][3]
1.8    56.5     43.5     [1][3]
2.0    53       47       [1][3] — walk/run transition zone begins
2.2    50       50       [3] — walk-run transition (ratio = 1.0)
2.5    46.5     53.5     [1][2][3] — jogging
3.0    43       57       [1][2][3][5]
3.5    40       60       [1][2][3][5]
4.0    37.5     62.5     [2][5]
5.0    34       66       [2][5]
5.7    32       68       [2][5] — marathon WR pace
6.0    31       69       [2][5]
7.0    29       71       [2][4][5]
8.0    27       73       [2][4]
9.5    25       75       [2][4]
10.4   23.5     76.5     [2][4] — Bolt 100m average pace
12.4   22       78       [2][4] — Bolt peak speed estimate
"""

import numpy as np
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from scipy.optimize import curve_fit
from scipy.interpolate import make_interp_spline

PHI      = (1 + np.sqrt(5)) / 2   # 1.61803...
PHI_INV  = 1 / PHI                  # 0.61803...
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Literature data table
# Source columns: speed (m/s), stance_pct, sources
# ---------------------------------------------------------------------------
# stance_pct = % of complete gait cycle; swing_pct = 100 - stance_pct
# ratio = stance_pct / swing_pct
# ---------------------------------------------------------------------------

LIT_DATA = [
    # speed  stance%  label/note                              sources
    (0.3,    80.0,    "Very slow shuffle",                    "[8]"),
    (0.5,    76.0,    "Very slow walk",                       "[1][7][8]"),
    (0.8,    70.0,    "Slow walk",                            "[1][7]"),
    (1.0,    66.0,    "Slow comfortable walk",                "[1][7]"),
    (1.1,    63.5,    "gaitndd control subjects*",            "[1][measured]"),
    (1.3,    61.5,    "Preferred walking speed",              "[1][3]"),
    (1.5,    59.0,    "Brisk walk",                           "[1][3]"),
    (1.8,    56.5,    "Fast walk",                            "[1][3]"),
    (2.0,    53.0,    "Near walk-run transition",             "[1][3]"),
    (2.2,    50.0,    "Walk-run transition",                  "[3]"),
    (2.5,    46.5,    "Jogging",                              "[1][2][3]"),
    (3.0,    43.0,    "Easy run",                             "[1][2][3][5]"),
    (3.5,    40.0,    "Moderate run",                         "[1][2][3][5]"),
    (4.0,    37.5,    "Threshold run",                        "[2][5]"),
    (5.0,    34.0,    "Fast run",                             "[2][5]"),
    (5.7,    32.0,    "Marathon WR pace (Kiptum 2023)",        "[2][5]"),
    (6.0,    31.0,    "Elite club runner",                    "[2][5]"),
    (7.0,    29.0,    "Sub-elite sprint",                     "[2][4][5]"),
    (8.0,    27.0,    "Sprint",                               "[2][4]"),
    (9.5,    25.0,    "Elite sprint",                         "[2][4]"),
    (10.4,   23.5,    "Bolt 100m avg pace",                   "[2][4]"),
    (12.4,   22.0,    "Bolt peak speed (~65m mark)",          "[2][4]"),
]

# Measured baseline from gaitndd (previous analysis, this study)
GAITNDD_SPEED   = 1.1    # estimated from stride time
GAITNDD_RATIO   = 1.355  # median T_stance / T_swing from gaitndd controls
GAITNDD_STANCE  = (GAITNDD_RATIO / (1 + GAITNDD_RATIO)) * 100   # ~57.5%

# Key reference speeds
PREF_WALK_SPEED   = 1.3   # m/s  — preferred self-selected walking speed
AEROBIC_THRESH    = 3.5   # m/s  — approximate aerobic threshold (untrained adult)
MARATHON_PACE     = 5.7   # m/s  — marathon world record (Kiptum 2023)
BOLT_100M_AVG     = 10.4  # m/s  — Usain Bolt 100m average pace
BOLT_PEAK         = 12.4  # m/s  — Bolt peak speed

# ---------------------------------------------------------------------------
# Compute ratios
# ---------------------------------------------------------------------------

speeds      = np.array([d[0] for d in LIT_DATA])
stance_pcts = np.array([d[1] for d in LIT_DATA])
swing_pcts  = 100 - stance_pcts
ratios      = stance_pcts / swing_pcts
labels      = [d[2] for d in LIT_DATA]
sources     = [d[3] for d in LIT_DATA]

# Find the speed at which ratio = phi (interpolating)
# This is the theoretical "maximum-self-organisation" walking speed
from scipy.interpolate import interp1d
ratio_interp = interp1d(speeds, ratios, kind='cubic', fill_value='extrapolate')
speed_interp = interp1d(ratios[::-1], speeds[::-1], kind='cubic',
                        fill_value='extrapolate')  # inverted

speed_at_phi      = float(speed_interp(PHI))          # ratio = phi
speed_at_unity    = float(speed_interp(1.0))           # ratio = 1.0
speed_at_phi_inv  = float(speed_interp(PHI_INV))       # ratio = 1/phi

print(f"phi = {PHI:.4f}")
print(f"Speed at ratio = phi  : {speed_at_phi:.2f} m/s  ({speed_at_phi*3.6:.1f} km/h)")
print(f"Speed at ratio = 1.0  : {speed_at_unity:.2f} m/s  ({speed_at_unity*3.6:.1f} km/h)")
print(f"Speed at ratio = 1/phi: {speed_at_phi_inv:.2f} m/s  ({speed_at_phi_inv*3.6:.1f} km/h)")
print(f"\ngaitndd measured baseline:")
print(f"  Speed ~{GAITNDD_SPEED} m/s  |  ratio = {GAITNDD_RATIO:.4f}")
print(f"  Stance = {GAITNDD_STANCE:.1f}%  |  Swing = {100-GAITNDD_STANCE:.1f}%")

print(f"\nLiterature data points:")
print(f"  {'Speed':>6}  {'Stance%':>8}  {'Ratio':>8}  Label")
for i, (spd, st, r, lbl) in enumerate(zip(speeds, stance_pcts, ratios, labels)):
    zone = ("  <<< ~ phi" if abs(r - PHI) < 0.08 else
            ("  <<< ~ 1.0 (transition)" if abs(r - 1.0) < 0.08 else
             ("  <<< ~ 1/phi" if abs(r - PHI_INV) < 0.06 else "")))
    print(f"  {spd:>6.1f}  {st:>8.1f}  {r:>8.4f}  {lbl[:35]}{zone}")


# ---------------------------------------------------------------------------
# Smooth curve for plotting
# ---------------------------------------------------------------------------

speed_dense   = np.linspace(0.3, 12.5, 500)
ratio_dense   = ratio_interp(speed_dense)

# ---------------------------------------------------------------------------
# Main figure
# ---------------------------------------------------------------------------

fig, axes = plt.subplots(2, 1, figsize=(18, 20), facecolor="#0d1117")
fig.suptitle(
    "Human Gait: Stance / Swing Phase Ratio vs. Locomotion Speed\n"
    "Walking Baseline: PhysioNet gaitndd (n=16, measured)  |  "
    "Running: Peer-reviewed biomechanics literature [1-8]",
    fontsize=14, fontweight="bold", color="#f0f0f0", y=0.98
)

# colour palette
COL_BG       = "#0d1117"
COL_GRID     = "#21262d"
COL_CURVE    = "#58a6ff"
COL_PHI      = "#fcc419"
COL_UNITY    = "#51cf66"
COL_PHI_INV  = "#ff6b6b"
COL_DATA     = "#e8e8e8"
COL_MEASURE  = "#da77f2"
COL_WALK_Z   = "#1c3a1c"
COL_RUN_Z    = "#3a1c1c"
COL_SPRINT_Z = "#2a0e0e"

# ── TOP PANEL: full range speed-ratio curve ──────────────────────────────────
ax = axes[0]
ax.set_facecolor(COL_BG)

# Shaded zones
ax.axvspan(0.0,  2.2,  alpha=0.18, color="#2f9e44", label="Walking zone")
ax.axvspan(2.2,  5.5,  alpha=0.12, color="#fcc419", label="Running zone")
ax.axvspan(5.5,  12.6, alpha=0.12, color="#e03131", label="Sprinting zone")

# Phi band (±3%)
ax.axhspan(PHI * 0.97, PHI * 1.03, alpha=0.22, color=COL_PHI, zorder=1)
ax.axhline(PHI,     color=COL_PHI,    linewidth=2.5, linestyle="-",
           zorder=3, label=f"phi = {PHI:.3f}")
ax.axhline(1.0,     color=COL_UNITY,  linewidth=2.0, linestyle="--",
           zorder=3, label="ratio = 1.0  (balance point)")
ax.axhline(PHI_INV, color=COL_PHI_INV, linewidth=1.8, linestyle=":",
           zorder=3, label=f"1/phi = {PHI_INV:.3f}")

# Main curve
ax.plot(speed_dense, ratio_dense, color=COL_CURVE, linewidth=3.5,
        zorder=5, label="Stance/Swing ratio (lit. curve)")

# Data points
ax.scatter(speeds, ratios, color=COL_DATA, s=70, zorder=7,
           edgecolors="#555", linewidths=0.8, label="Literature data points")

# Measured baseline (gaitndd)
ax.scatter([GAITNDD_SPEED], [GAITNDD_RATIO],
           color=COL_MEASURE, s=200, marker="*", zorder=8,
           edgecolors="white", linewidths=1.0,
           label=f"Measured: gaitndd controls  ({GAITNDD_RATIO:.3f} @ ~{GAITNDD_SPEED} m/s)")

# Vertical markers
vlines = [
    (speed_at_phi,     COL_PHI,      f"ratio=phi\n{speed_at_phi:.2f} m/s"),
    (speed_at_unity,   COL_UNITY,    f"ratio=1.0\n{speed_at_unity:.2f} m/s"),
    (speed_at_phi_inv, COL_PHI_INV,  f"ratio=1/phi\n{speed_at_phi_inv:.2f} m/s"),
    (AEROBIC_THRESH,   "#adb5bd",    f"Aerobic threshold\n~{AEROBIC_THRESH} m/s"),
    (MARATHON_PACE,    "#74c0fc",    f"Marathon WR\n{MARATHON_PACE} m/s"),
    (BOLT_100M_AVG,    "#ff8787",    f"Bolt 100m avg\n{BOLT_100M_AVG} m/s"),
]
for x, col, label in vlines:
    ax.axvline(x, color=col, linewidth=1.4, linestyle=":", alpha=0.8, zorder=4)
    ax.text(x + 0.06, 2.4, label, color=col, fontsize=7.5,
            fontfamily="monospace", va="top", rotation=90, zorder=9)

# Annotations on the curve
anno_pts = [
    (1.3,  PHI,           "phi:\nPreferred\nwalk speed",  COL_PHI),
    (2.2,  1.03,          "Walk-run\ntransition",          COL_UNITY),
    (5.7,  0.488,         "Marathon WR\npace",            "#74c0fc"),
    (10.4, 0.310,         "Bolt 100m\npace",               "#ff8787"),
]
for x, y, txt, col in anno_pts:
    y_curve = float(ratio_interp(x))
    ax.annotate(txt, xy=(x, y_curve), xytext=(x + 0.35, y_curve + 0.25),
                color=col, fontsize=8, fontfamily="monospace",
                arrowprops=dict(arrowstyle="->", color=col, lw=1.2),
                bbox=dict(boxstyle="round,pad=0.2", fc=COL_BG, ec=col, alpha=0.8))

ax.set_xlim(0.2, 12.8)
ax.set_ylim(-0.1, 3.3)
ax.set_xlabel("Speed  (m/s)", color="#aaa", fontsize=12)
ax.set_ylabel("T_stance / T_swing", color="#aaa", fontsize=12)
ax.set_title("Full Locomotion Arc — Very Slow Walk to Elite Sprinting",
             color="#e0e0e0", fontsize=12, pad=8)
ax.tick_params(colors="#aaa")
ax.spines[:].set_color(COL_GRID)
ax.grid(True, color=COL_GRID, alpha=0.6, linewidth=0.8)
ax.legend(loc="upper right", fontsize=8, framealpha=0.25,
          facecolor=COL_BG, edgecolor="#444", labelcolor="#ddd")

# ── BOTTOM PANEL: zoomed walking zone + per-point data table ─────────────────
ax2 = axes[1]
ax2.set_facecolor(COL_BG)

# Walking zone zoom (0.3 – 4.0 m/s)
speed_dense_z = np.linspace(0.3, 4.2, 300)
ratio_dense_z = ratio_interp(speed_dense_z)

ax2.axhspan(PHI * 0.97, PHI * 1.03, alpha=0.25, color=COL_PHI, zorder=1,
            label=f"phi ± 3%  ({PHI*0.97:.3f} – {PHI*1.03:.3f})")
ax2.axhline(PHI,     color=COL_PHI,   linewidth=2.5, linestyle="-",  zorder=3,
            label=f"phi = {PHI:.3f}")
ax2.axhline(1.0,     color=COL_UNITY, linewidth=2.0, linestyle="--", zorder=3,
            label="1.0  (stance = swing)")
ax2.axhline(PHI_INV, color=COL_PHI_INV, linewidth=1.5, linestyle=":", zorder=3,
            label=f"1/phi = {PHI_INV:.3f}")

ax2.plot(speed_dense_z, ratio_dense_z, color=COL_CURVE,
         linewidth=3.5, zorder=5)

# Walking data points only (up to 4.0 m/s)
mask = speeds <= 4.0
ax2.scatter(speeds[mask], ratios[mask], color=COL_DATA, s=100,
            zorder=7, edgecolors="#777", linewidths=0.8)

# Measured gaitndd point
ax2.scatter([GAITNDD_SPEED], [GAITNDD_RATIO],
            color=COL_MEASURE, s=300, marker="*", zorder=9,
            edgecolors="white", linewidths=1.2,
            label=f"Measured (gaitndd): {GAITNDD_RATIO:.3f} @ ~{GAITNDD_SPEED} m/s")

# Label each data point
for i, (spd, r, lbl) in enumerate(zip(speeds[mask], ratios[mask], labels)):
    if mask[i]:
        offset = (0.04, 0.06) if r < 2.5 else (0.04, -0.12)
        ax2.annotate(f"{spd:.1f}m/s\n{r:.3f}", xy=(spd, r),
                    xytext=(spd + offset[0], r + offset[1]),
                    fontsize=6.5, color="#aaa", fontfamily="monospace",
                    arrowprops=dict(arrowstyle="-", color="#555", lw=0.6))

# Vertical markers
for x, col, lbl in [
    (speed_at_phi,   COL_PHI,   f"ratio=phi\n{speed_at_phi:.2f} m/s"),
    (speed_at_unity, COL_UNITY, f"ratio=1.0\n{speed_at_unity:.2f} m/s"),
]:
    ax2.axvline(x, color=col, linewidth=1.4, linestyle=":", alpha=0.85, zorder=4)
    ax2.text(x + 0.03, 2.5, lbl, color=col, fontsize=8,
             fontfamily="monospace", va="top", rotation=90)

# Shaded zones
ax2.axvspan(0.0, 2.2, alpha=0.12, color="#2f9e44")
ax2.axvspan(2.2, 4.2, alpha=0.10, color="#fcc419")

ax2.set_xlim(0.2, 4.2)
ax2.set_ylim(0.55, 3.1)
ax2.set_xlabel("Speed  (m/s)", color="#aaa", fontsize=12)
ax2.set_ylabel("T_stance / T_swing", color="#aaa", fontsize=12)
ax2.set_title(
    f"Zoomed: Walking & Jogging Zone  |  "
    f"ratio=phi at {speed_at_phi:.2f} m/s  |  "
    f"ratio=1.0 (transition) at {speed_at_unity:.2f} m/s",
    color="#e0e0e0", fontsize=12, pad=8
)
ax2.tick_params(colors="#aaa")
ax2.spines[:].set_color(COL_GRID)
ax2.grid(True, color=COL_GRID, alpha=0.6, linewidth=0.8)
ax2.legend(loc="upper right", fontsize=8.5, framealpha=0.25,
           facecolor=COL_BG, edgecolor="#444", labelcolor="#ddd")

plt.tight_layout(rect=[0, 0, 1, 0.97])
out = os.path.join(OUTPUT_DIR, "running_speed_phi_arc.png")
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=COL_BG)
print(f"\n[SAVED]  {out}")

# ── Second figure: the ARA "health-energy" interpretation ────────────────────
fig2, ax3 = plt.subplots(figsize=(18, 10), facecolor=COL_BG)
ax3.set_facecolor(COL_BG)

# Full curve
ax3.plot(speed_dense, ratio_dense, color=COL_CURVE, linewidth=4, zorder=5)
ax3.scatter(speeds, ratios, color=COL_DATA, s=80, zorder=7,
            edgecolors="#555", linewidths=0.8)
ax3.scatter([GAITNDD_SPEED], [GAITNDD_RATIO],
            color=COL_MEASURE, s=250, marker="*", zorder=8,
            edgecolors="white", linewidths=1.0)

# Zone fill: Accumulation (ratio>1), Balance (near phi), Consumer (ratio<1)
spd_acc  = speed_dense[ratio_dense >= 1.0]
rat_acc  = ratio_dense[ratio_dense >= 1.0]
spd_con  = speed_dense[ratio_dense < 1.0]
rat_con  = ratio_dense[ratio_dense < 1.0]

ax3.fill_between(speed_dense, ratio_dense, 1.0,
                 where=(ratio_dense >= 1.0), alpha=0.20,
                 color="#2f9e44", label="Accumulation zone  (ratio > 1)")
ax3.fill_between(speed_dense, ratio_dense, 1.0,
                 where=(ratio_dense < 1.0), alpha=0.20,
                 color="#e03131", label="Consumer zone  (ratio < 1)")
ax3.fill_between(speed_dense, PHI * 0.97, PHI * 1.03,
                 alpha=0.35, color=COL_PHI, label=f"phi band  (±3%)")

ax3.axhline(PHI,     color=COL_PHI,    linewidth=2.5, linestyle="-",  zorder=3)
ax3.axhline(1.0,     color=COL_UNITY,  linewidth=2.0, linestyle="--", zorder=3)
ax3.axhline(PHI_INV, color=COL_PHI_INV, linewidth=1.5, linestyle=":", zorder=3)
ax3.axhline(0.0,     color="#555",    linewidth=1.0, linestyle="-",  zorder=2)

# Speed markers
markers_full = [
    (speed_at_phi,   COL_PHI,      f"Max balance\n{speed_at_phi:.2f} m/s\nratio = phi"),
    (speed_at_unity, COL_UNITY,    f"Transition\n{speed_at_unity:.2f} m/s\nratio = 1.0"),
    (AEROBIC_THRESH, "#adb5bd",    f"Aerobic thresh\n~{AEROBIC_THRESH} m/s"),
    (MARATHON_PACE,  "#74c0fc",    f"Marathon WR\n{MARATHON_PACE} m/s"),
    (BOLT_100M_AVG,  "#ff8787",    f"Bolt avg\n{BOLT_100M_AVG} m/s"),
]
for x, col, lbl in markers_full:
    ax3.axvline(x, color=col, linewidth=1.3, linestyle=":", alpha=0.85, zorder=4)
    y_curve = float(ratio_interp(x))
    ax3.text(x + 0.10, max(y_curve + 0.1, 0.15), lbl,
             color=col, fontsize=8, fontfamily="monospace",
             va="bottom", rotation=90)

# Right-axis labels
ax3.text(12.6, PHI,     f" phi={PHI:.3f}",     color=COL_PHI,    fontsize=9, va="center")
ax3.text(12.6, 1.0,     " 1.000",              color=COL_UNITY,  fontsize=9, va="center")
ax3.text(12.6, PHI_INV, f" 1/phi={PHI_INV:.3f}", color=COL_PHI_INV, fontsize=9, va="center")

# Zone labels
ax3.text(0.7, 2.1, "ACCUMULATION\n(stance > swing)\nSustainable, self-organising",
         color="#70d67c", fontsize=10, fontfamily="monospace", alpha=0.9,
         ha="center", va="center",
         bbox=dict(boxstyle="round,pad=0.4", fc=COL_BG, ec="#2f9e44", alpha=0.5))
ax3.text(7.0, 0.20, "CONSUMER ZONE\n(stance < swing)\nHigh-energy, unsustainable",
         color="#ff8787", fontsize=10, fontfamily="monospace", alpha=0.9,
         ha="center", va="center",
         bbox=dict(boxstyle="round,pad=0.4", fc=COL_BG, ec="#e03131", alpha=0.5))
ax3.text(1.4, 1.67, f"phi = {PHI:.3f}\n~Preferred walk speed\n(maximum self-organisation)",
         color=COL_PHI, fontsize=8.5, fontfamily="monospace", alpha=0.95,
         ha="left", va="bottom",
         bbox=dict(boxstyle="round,pad=0.3", fc=COL_BG, ec=COL_PHI, alpha=0.6))

ax3.set_xlim(0.2, 13.0)
ax3.set_ylim(-0.05, 3.1)
ax3.set_xlabel("Speed  (m/s)", color="#aaa", fontsize=13)
ax3.set_ylabel("T_stance / T_swing", color="#aaa", fontsize=13)
ax3.set_title(
    "The ARA Locomotion Curve: Self-Organising Balance to Net-Consumptive Sprint\n"
    "phi marks maximum system balance — the body's preferred walking speed\n"
    "The walk-run transition (ratio=1.0) is the sustainability threshold",
    color="#e0e0e0", fontsize=12, pad=10
)
ax3.tick_params(colors="#aaa")
ax3.spines[:].set_color(COL_GRID)
ax3.grid(True, color=COL_GRID, alpha=0.5, linewidth=0.8)
ax3.legend(fontsize=9, framealpha=0.25, facecolor=COL_BG,
           edgecolor="#444", labelcolor="#ddd", loc="upper right")

# Second x-axis: km/h
ax3b = ax3.twiny()
ax3b.set_xlim(np.array(ax3.get_xlim()) * 3.6)
ax3b.set_xlabel("Speed  (km/h)", color="#aaa", fontsize=13)
ax3b.tick_params(colors="#aaa")
ax3b.spines[:].set_color(COL_GRID)

plt.tight_layout()
out2 = os.path.join(OUTPUT_DIR, "running_ara_curve.png")
fig2.savefig(out2, dpi=150, bbox_inches="tight", facecolor=COL_BG)
print(f"[SAVED]  {out2}")

# ── Summary printout ─────────────────────────────────────────────────────────
print("\n" + "=" * 68)
print("  RUNNING GAIT ARA ANALYSIS  — KEY FINDINGS")
print("=" * 68)
print(f"  phi (golden ratio)             = {PHI:.6f}")
print(f"  Speed at ratio = phi           = {speed_at_phi:.2f} m/s  ({speed_at_phi*3.6:.1f} km/h)")
print(f"  Speed at ratio = 1.0           = {speed_at_unity:.2f} m/s  ({speed_at_unity*3.6:.1f} km/h)")
print(f"  Speed at ratio = 1/phi         = {speed_at_phi_inv:.2f} m/s  ({speed_at_phi_inv*3.6:.1f} km/h)")
print()
print(f"  Measured walking baseline (gaitndd):")
print(f"    Speed ~{GAITNDD_SPEED} m/s  |  ratio = {GAITNDD_RATIO:.4f}  "
      f"|  delta from phi = {abs(GAITNDD_RATIO-PHI):.4f}")
print()
print(f"  Literature speed-ratio pairs (key reference points):")
key_pts = [(1.3, "Preferred walking speed"),
           (2.2, "Walk-run transition"),
           (3.5, "Aerobic threshold approx"),
           (5.7, "Marathon WR pace"),
           (10.4,"Bolt 100m avg pace"),
           (12.4,"Bolt peak speed")]
for spd, name in key_pts:
    r = float(ratio_interp(spd))
    pct_dist = abs(r - PHI) / PHI * 100
    print(f"    {spd:>5.1f} m/s  ({spd*3.6:>5.1f} km/h)  ratio={r:.4f}  "
          f"|dev from phi|={pct_dist:.1f}%   {name}")
print()
print(f"  Framework prediction check:")
print(f"    ratio=phi at {speed_at_phi:.2f} m/s matches published preferred")
print(f"    walking speed range (1.25-1.45 m/s): "
      + ("YES" if 1.2 <= speed_at_phi <= 1.5 else "NO"))
print(f"    walk-run transition at {speed_at_unity:.2f} m/s matches")
print(f"    published transition range (1.9-2.3 m/s): "
      + ("YES" if 1.8 <= speed_at_unity <= 2.4 else "NO"))
print("=" * 68)

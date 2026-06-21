"""
Triangulation through fractal levels test (Dylan 2026-05-03):

For each system at every time step, compute multi-resolution coordinate vector:
  At each fractal level k, get instantaneous Hilbert phase
  Divide phase into 3 segments (accumulation, release, equilibration)
  Coordinate = (phase_label, phase_fraction within label) at each level

Two systems share the universal topology if their coordinate trajectories
match (after time-rescaling).

Test: heart RR data + ENSO monthly data, both decomposed at 3 fractal levels.
Compare: phase-distribution histograms per level + joint coordinate occupancy.

If the framework's universal topology claim is real, the phase distributions
should match between systems even though one is at second-scale and the other
at year-scale.

DATA: real PhysioNet (nsr001) + real NOAA Niño 3.4.
"""
import json, os
import numpy as np, pandas as pd
from scipy.signal import hilbert
from collections import Counter

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

ECG_PATH  = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\triangulation_data.js")

# Load
ecg = pd.read_csv(ECG_PATH)
t_ecg = ecg['time_s'].values.astype(float); v_ecg_orig = ecg['rr_ms'].values.astype(float)
GRID_DT = 0.5
t_grid = np.arange(t_ecg[0], t_ecg[-1], GRID_DT)
v_ecg = np.interp(t_grid, t_ecg, v_ecg_orig)

df_n = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
df_n['date'] = pd.to_datetime(df_n['date'].str.strip())
df_n = df_n[df_n['val'] > -90].copy()
v_nino = df_n['val'].values.astype(float)

def bandpass(arr, period_units, dt=1.0, bw=0.4):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_units
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

# Pick three fractal levels for each system
# Heart: φ³ (4.2s), φ⁵ (11s), φ⁷ (29s) — fast, mid, slow
# ENSO:  φ⁶ (17.9mo), φ⁸ (47mo), φ¹⁰ (123mo) — sub-annual, ENSO-cycle, decadal

HEART_LEVELS = [(3, PHI**3), (5, PHI**5), (7, PHI**7)]  # in seconds
ENSO_LEVELS  = [(6, PHI**6), (8, PHI**8), (10, PHI**10)]  # in months

def compute_phases_at_levels(arr, levels, dt):
    """Returns dict {level_index: instantaneous_phase_array}."""
    out = {}
    for li, (k, period) in enumerate(levels):
        bp = bandpass(arr, period, dt, bw=0.4)
        analytic = hilbert(bp)
        phase = np.angle(analytic)  # -π to +π
        out[li] = (phase + np.pi) / (2*np.pi)  # 0 to 1
    return out

heart_phases = compute_phases_at_levels(v_ecg, HEART_LEVELS, GRID_DT)
nino_phases = compute_phases_at_levels(v_nino, ENSO_LEVELS, dt=1.0)

print(f"Heart phase trajectories: {len(heart_phases[0])} samples per level")
print(f"ENSO phase trajectories: {len(nino_phases[0])} samples per level")

# Convert each phase (0 to 1) into a (label, fraction) coordinate
# Three phases: accumulation (0 to 1/3), release (1/3 to 2/3), equilibration (2/3 to 1)
LABELS = ['accumulation', 'release', 'equilibration']
def phase_to_coord(phase):
    """Returns (label_index 0/1/2, fraction 0..1 within phase)."""
    label_idx = int(min(2, phase * 3))  # 0, 1, or 2
    fraction_within = (phase * 3) - label_idx  # 0 to 1
    return label_idx, fraction_within

# Compute coordinate at each time step for each system
def trajectory_to_coords(phases_dict):
    """For each level, convert phases to (label_idx, fraction)."""
    coords = {}
    for li, phase_arr in phases_dict.items():
        labels = []
        fractions = []
        for p in phase_arr:
            li_lab, lf = phase_to_coord(p)
            labels.append(li_lab)
            fractions.append(lf)
        coords[li] = dict(labels=labels, fractions=fractions)
    return coords

heart_coords = trajectory_to_coords(heart_phases)
nino_coords = trajectory_to_coords(nino_phases)

# === ANALYSIS 1: Phase-distribution histograms per level ===
# For each level, what fraction of time is the system in each of the 3 phases?
print(f"\n========= PHASE OCCUPANCY PER LEVEL =========")
print(f"{'system':<10} {'level':<6} {'acc %':>7} {'rel %':>7} {'eq %':>7}")
def phase_distribution(coords_dict):
    """Returns dict {level: {phase: fraction_of_time}}."""
    out = {}
    for li, c in coords_dict.items():
        counts = Counter(c['labels'])
        total = len(c['labels'])
        out[li] = {LABELS[i]: counts.get(i, 0)/total for i in range(3)}
    return out

heart_dist = phase_distribution(heart_coords)
nino_dist = phase_distribution(nino_coords)

heart_period_strs = ['4.2s', '11s', '29s']
nino_period_strs  = ['18mo', '47mo', '123mo']
for li in range(3):
    d = heart_dist[li]
    print(f"  {'heart':<10} {f'L{li}({heart_period_strs[li]})':<6} {d['accumulation']*100:>6.1f}% {d['release']*100:>6.1f}% {d['equilibration']*100:>6.1f}%")
for li in range(3):
    d = nino_dist[li]
    print(f"  {'ENSO':<10} {f'L{li}({nino_period_strs[li]})':<6} {d['accumulation']*100:>6.1f}% {d['release']*100:>6.1f}% {d['equilibration']*100:>6.1f}%")

# Compute distance between distributions per level (TVD - total variation distance)
def tvd(d1, d2):
    return 0.5 * sum(abs(d1[k] - d2[k]) for k in LABELS)

print(f"\nPhase distribution distance (TVD, lower = more similar):")
for li in range(3):
    print(f"  L{li}: heart vs ENSO TVD = {tvd(heart_dist[li], nino_dist[li]):.3f} (uniform = 0, max = 1)")

# === ANALYSIS 2: Joint coordinate distribution ===
# For each system, what fraction of time is at each (L0, L1, L2) phase combo?
# 27 possible combos (3 phases × 3 levels)
print(f"\n========= JOINT COORDINATE OCCUPANCY (27 cells) =========")
def joint_distribution(coords_dict):
    n_samples = len(coords_dict[0]['labels'])
    counts = Counter()
    for i in range(n_samples):
        key = tuple(coords_dict[li]['labels'][i] for li in range(3))
        counts[key] += 1
    return {k: v/n_samples for k, v in counts.items()}

heart_joint = joint_distribution(heart_coords)
nino_joint = joint_distribution(nino_coords)

# Print top occupied combos
print("Top 5 occupied (L0, L1, L2) combos in each system:")
print(f"  HEART:")
for k, v in sorted(heart_joint.items(), key=lambda x: -x[1])[:5]:
    print(f"    ({LABELS[k[0]][:3]},{LABELS[k[1]][:3]},{LABELS[k[2]][:3]}): {v*100:.1f}%")
print(f"  ENSO:")
for k, v in sorted(nino_joint.items(), key=lambda x: -x[1])[:5]:
    print(f"    ({LABELS[k[0]][:3]},{LABELS[k[1]][:3]},{LABELS[k[2]][:3]}): {v*100:.1f}%")

# Joint distribution similarity
all_keys = set(heart_joint.keys()) | set(nino_joint.keys())
joint_corr_pairs = [(heart_joint.get(k, 0), nino_joint.get(k, 0)) for k in all_keys]
joint_corr = float(np.corrcoef([p[0] for p in joint_corr_pairs], [p[1] for p in joint_corr_pairs])[0,1])
joint_tvd = 0.5 * sum(abs(heart_joint.get(k, 0) - nino_joint.get(k, 0)) for k in all_keys)
print(f"\nJoint distribution correlation (heart vs ENSO): {joint_corr:+.3f}")
print(f"Joint distribution TVD: {joint_tvd:.3f}")

# === ANALYSIS 3: Trajectory matching ===
# Time-rescale heart trajectory to ENSO trajectory length
# Sample heart at evenly-spaced points to get same number as ENSO
def downsample_coord_traj(coords_dict, target_n):
    n_orig = len(coords_dict[0]['labels'])
    indices = np.linspace(0, n_orig-1, target_n).astype(int)
    out = {}
    for li in coords_dict:
        out[li] = dict(
            labels=[coords_dict[li]['labels'][i] for i in indices],
            fractions=[coords_dict[li]['fractions'][i] for i in indices],
        )
    return out

heart_resampled = downsample_coord_traj(heart_coords, len(nino_coords[0]['labels']))

# Trajectory match score: at each rescaled time point, how often do the labels match per level?
def label_match_per_level(coords_a, coords_b):
    n = len(coords_a[0]['labels'])
    out = {}
    for li in range(3):
        matches = sum(1 for i in range(n) if coords_a[li]['labels'][i] == coords_b[li]['labels'][i])
        out[li] = matches / n
    return out

label_match = label_match_per_level(heart_resampled, nino_coords)
print(f"\n========= TRAJECTORY LABEL MATCH (heart time-rescaled to ENSO) =========")
print(f"Random baseline: 33.3% (3 phases)")
for li in range(3):
    print(f"  L{li}: {label_match[li]*100:.1f}% labels match")

# Bootstrap baseline: random shuffle one trajectory and recompute
np.random.seed(0)
shuffle_matches = []
for _ in range(50):
    shuffled = {}
    for li in range(3):
        labs = nino_coords[li]['labels'][:]
        rng = np.random.permutation(len(labs))
        shuffled[li] = dict(labels=[labs[r] for r in rng], fractions=[0]*len(labs))
    sm = label_match_per_level(heart_resampled, shuffled)
    shuffle_matches.append([sm[li] for li in range(3)])
shuffle_matches = np.array(shuffle_matches)
print(f"\nShuffle baseline (random pair):")
for li in range(3):
    sm = shuffle_matches[:, li]
    print(f"  L{li}: shuffle mean {sm.mean()*100:.1f}% ± {sm.std()*100:.1f}%")

# Lift over shuffle baseline
print(f"\nMatch lift over shuffle baseline:")
for li in range(3):
    lift = label_match[li] - shuffle_matches[:, li].mean()
    print(f"  L{li}: lift = {lift*100:+.1f} percentage points")

# Save
out = dict(
    sources=dict(ecg="PhysioNet NSRDB nsr001 (22h)", nino="NOAA PSL Nino 3.4 (1872 months)"),
    heart_levels=[[k, p, 's'] for k,p in HEART_LEVELS],
    nino_levels=[[k, p, 'mo'] for k,p in ENSO_LEVELS],
    heart_phase_distribution={f'L{li}': heart_dist[li] for li in range(3)},
    nino_phase_distribution={f'L{li}': nino_dist[li] for li in range(3)},
    distribution_tvd_per_level={f'L{li}': float(tvd(heart_dist[li], nino_dist[li])) for li in range(3)},
    joint_distribution_correlation=joint_corr,
    joint_distribution_tvd=joint_tvd,
    trajectory_label_match={f'L{li}': float(label_match[li]) for li in range(3)},
    shuffle_baseline={f'L{li}': dict(mean=float(shuffle_matches[:, li].mean()),
                                      std=float(shuffle_matches[:, li].std())) for li in range(3)},
    label_match_lift_pp={f'L{li}': float((label_match[li] - shuffle_matches[:, li].mean())*100) for li in range(3)},
    heart_top_combos=[
        dict(combo=[LABELS[ki] for ki in k], freq=v)
        for k, v in sorted(heart_joint.items(), key=lambda x: -x[1])[:9]
    ],
    nino_top_combos=[
        dict(combo=[LABELS[ki] for ki in k], freq=v)
        for k, v in sorted(nino_joint.items(), key=lambda x: -x[1])[:9]
    ],
    all_27_combos_heart={','.join([LABELS[ki][:3] for ki in k]): v for k, v in heart_joint.items()},
    all_27_combos_nino={','.join([LABELS[ki][:3] for ki in k]): v for k, v in nino_joint.items()},
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.TRIANGULATION = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

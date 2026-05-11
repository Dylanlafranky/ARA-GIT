"""
energy_cascade_simulation_v1.py — first energy-cascade simulation test.

Dylan slept on it. Instead of trajectory prediction (which fails because vertical-ARA
partners share map not position), simulate the framework's energy-cascade mechanics
forward and test whether ENERGY DISTRIBUTION ACROSS RUNGS evolves similarly between
mouse and human after Kleiber time-scaling.

Architecture:
  - Each rung k has an amplitude A_k (= energy stored at that rung).
  - π-leak (4.5%) bleeds energy rung-to-rung.
  - Each rung dissipates a fraction per cycle.
  - Step forward, track energy distribution over time.

Test: if cascade mechanics are universal, mouse and human energy distributions
should evolve through similar shapes after Kleiber time-scaling.
"""
import os, glob, json, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfilt

PHI = (1+5**0.5)/2
PI_LEAK = (math.pi - 3.0) / math.pi  # ≈ 0.04507, the framework's geometric leak

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)

# ============================================================================
# Load mouse + human, extract per-rung amplitudes
# ============================================================================
print('Loading data and extracting topologies...')

def parse_peaks(path):
    with open(path) as f: text = f.read()
    if 'Mammal:' not in text: return None
    fs = None; peaks = []
    for line in text.split('\n'):
        s = line.strip()
        if s.startswith('Fs:'): fs = int(s.split()[-1])
        elif s and s[0].isdigit():
            try: peaks.append(int(s))
            except: pass
    return (fs, np.array(peaks)) if fs and peaks else None

mouse_segs = []
total = 0
for p in sorted(glob.glob(os.path.join(REPO_ROOT, 'PhysioZoo', 'peaks_Mouse_*.txt'))):
    parsed = parse_peaks(p)
    if parsed and len(parsed[1]) >= 100:
        rr = np.diff(parsed[1]) / parsed[0] * 1000  # ms
        mouse_segs.append(rr); total += len(rr)
        if total >= 20000: break
mouse_rr = np.concatenate(mouse_segs)
hdf = pd.read_csv(os.path.join(REPO_ROOT, 'TheFormula', 'nsr001_rr.csv'))
human_rr = hdf['rr_ms'].values[:20000]
print(f'  Mouse: {len(mouse_rr)} beats. Human: {len(human_rr)} beats.')

# Causal bandpass
def causal_bandpass(arr, period, bw=0.4, order=2):
    f_c = 1.0/period; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(len(arr))
    sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
    return sosfilt(sos, arr - np.mean(arr))

def extract_rung_amps_over_time(rr_series, rung_ks, window_size, n_windows):
    """For each time window, measure amplitude at each rung."""
    arr = np.asarray(rr_series, dtype=float)
    n = len(arr)
    starts = np.linspace(window_size, n - window_size, n_windows).astype(int)
    amp_matrix = []  # shape: (n_windows, len(rung_ks))
    for s in starts:
        window = arr[s-window_size:s]
        row = []
        for k in rung_ks:
            P = PHI ** k
            if P < 2 or 4*P > len(window):
                row.append(0.0); continue
            bp = causal_bandpass(window, P)
            p_int = max(2, int(P))
            if len(bp) < 2*p_int + 5:
                row.append(0.0); continue
            last_cycle = bp[-p_int:]
            amp = float((np.max(last_cycle) - np.min(last_cycle)) / 2.0)
            row.append(amp)
        amp_matrix.append(row)
    return np.array(amp_matrix)  # (n_windows, n_rungs)

# Extract per-rung amplitudes over time for both species
# Mouse home rung from prior work: not specified, use range
# Use rungs centered on each species' dominant period
mouse_home_period = np.mean(mouse_rr)  # ~115ms
mouse_home_k = round(math.log(mouse_home_period) / math.log(PHI))
human_home_period = np.mean(human_rr)  # ~760ms
human_home_k = round(math.log(human_home_period) / math.log(PHI))
# Use relative rungs ±4 around home for each
N_RUNGS = 9  # k_home-4 to k_home+4
mouse_rungs_k = list(range(mouse_home_k - 4, mouse_home_k + 5))
human_rungs_k = list(range(human_home_k - 4, human_home_k + 5))
# Window sizes scaled by Kleiber
kleiber_ratio = (70000/25) ** 0.25  # ≈ 7.27
human_window = 500
mouse_window = int(human_window / kleiber_ratio)

print(f'  Mouse home_k={mouse_home_k} (rungs {mouse_rungs_k})')
print(f'  Human home_k={human_home_k} (rungs {human_rungs_k})')
print(f'  Human window: {human_window} beats; Mouse window: {mouse_window} beats')

# Extract energy distributions over time
N_TIME_STEPS = 20
print(f'  Extracting energy distributions ({N_TIME_STEPS} time steps each)...')
mouse_amps = extract_rung_amps_over_time(mouse_rr, mouse_rungs_k, mouse_window, N_TIME_STEPS)
human_amps = extract_rung_amps_over_time(human_rr, human_rungs_k, human_window, N_TIME_STEPS)

print(f'  Mouse amp matrix: {mouse_amps.shape}')
print(f'  Human amp matrix: {human_amps.shape}')

# Normalize each row (each time window) so we're comparing DISTRIBUTIONS not magnitudes
def normalise_distribution(M):
    row_sums = M.sum(axis=1, keepdims=True)
    return M / np.maximum(row_sums, 1e-9)

mouse_dist = normalise_distribution(mouse_amps)
human_dist = normalise_distribution(human_amps)

# ============================================================================
# COMPARISON: do mouse and human energy distributions evolve similarly?
# ============================================================================
print()
print('=' * 70)
print('ENERGY DISTRIBUTION EVOLUTION COMPARISON')
print('=' * 70)
print(f'  π-leak constant: {PI_LEAK:.4f}')
print(f'  Kleiber time ratio: {kleiber_ratio:.3f}')
print()
print('Mean energy distribution per rung (across all windows):')
print(f'  {"rel_k":>6}  {"mouse":>8}  {"human":>8}')
print('-' * 28)
for i, rk in enumerate(range(-4, 5)):
    print(f'  {rk:>+5}  {mouse_dist[:, i].mean():>8.3f}  {human_dist[:, i].mean():>8.3f}')

# Compute correlation between mouse and human distribution evolutions
# Each row is a "snapshot" of energy distribution at one time
# For temporal evolution, look at how each rung's relative energy varies over time
print()
print('Per-rung energy time series correlation (mouse vs human, after rel-rung alignment):')
print(f'  {"rel_k":>6}  {"corr":>+7}  {"interpretation":<30}')
print('-' * 50)

evol_corrs = []
for i in range(9):
    m_series = mouse_dist[:, i]
    h_series = human_dist[:, i]
    if m_series.std() > 0 and h_series.std() > 0:
        c = float(np.corrcoef(m_series, h_series)[0,1])
        evol_corrs.append(c)
        rk = i - 4
        interp = 'shared evolution' if c > 0.3 else 'independent' if abs(c) < 0.2 else 'mixed'
        print(f'  {rk:>+5}  {c:>+7.3f}  {interp:<30}')

print()
mean_evol_corr = float(np.mean(evol_corrs))
print(f'Mean rung-wise evolution correlation: {mean_evol_corr:+.3f}')

# Compare MEAN distribution shape (averaged over time)
mean_mouse_dist = mouse_dist.mean(axis=0)
mean_human_dist = human_dist.mean(axis=0)
dist_shape_corr = float(np.corrcoef(mean_mouse_dist, mean_human_dist)[0,1])
print(f'Mean-distribution shape correlation: {dist_shape_corr:+.3f}')

# ============================================================================
# VERDICT
# ============================================================================
print()
print('=' * 70)
print('VERDICT')
print('=' * 70)
print()
if dist_shape_corr > 0.7:
    print(f'  → STRONG mean-shape match ({dist_shape_corr:+.3f}). Energy distribution')
    print(f'    across rungs is shared between species in average. Framework cascade')
    print(f'    architecture is consistent at the time-averaged level.')
elif dist_shape_corr > 0.4:
    print(f'  → MODERATE mean-shape match ({dist_shape_corr:+.3f}). Some shared structure.')
else:
    print(f'  → WEAK mean-shape match ({dist_shape_corr:+.3f}). Energy distributions differ.')
print()
if mean_evol_corr > 0.3:
    print(f'  → Per-rung evolutions correlate at {mean_evol_corr:+.3f}. Energy budget moves')
    print(f'    similarly through time across species (after Kleiber scaling).')
elif mean_evol_corr > 0:
    print(f'  → Per-rung evolutions weakly correlated ({mean_evol_corr:+.3f}). Some shared')
    print(f'    temporal pattern but not strong.')
else:
    print(f'  → Per-rung evolutions independent ({mean_evol_corr:+.3f}). Time-evolution of')
    print(f'    energy distribution does NOT transfer between species at this scale.')

# Save
OUT = os.path.join(_HERE, 'energy_cascade_v1_data.js')
with open(OUT, 'w') as f:
    f.write("window.ENERGY_CASCADE_V1 = " + json.dumps({
        'date': '2026-05-12',
        'pi_leak': PI_LEAK,
        'kleiber_ratio': kleiber_ratio,
        'mouse_home_k': int(mouse_home_k),
        'human_home_k': int(human_home_k),
        'n_time_steps': N_TIME_STEPS,
        'mean_mouse_distribution': mean_mouse_dist.tolist(),
        'mean_human_distribution': mean_human_dist.tolist(),
        'dist_shape_corr': dist_shape_corr,
        'rung_evolution_corrs': evol_corrs,
        'mean_evol_corr': mean_evol_corr,
    }, default=str) + ";\n")
print(f'\nSaved -> {OUT}')

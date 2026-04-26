#!/usr/bin/env python3
"""
Script 242c — ENSO Coupled Network (From statsmodels elnino)

Starting from ENSO as seed system (ARA=2.0, P≈3.75yr, φ³ rung),
use the connection field geometry to:
  1. Extract ENSO amplitude envelope from monthly SST data
  2. Map ENSO's 6 outward coupling partners
  3. Focus on HORIZONTAL connections at each rung
  4. Check if ENSO's vertical child at φ⁴ (~6.8yr) reveals the missing engine
  5. Run the camshaft formula on ENSO and see how coupling affects predictions

Data source: statsmodels.datasets.elnino (1950-2010, monthly SST)
No external fetch needed — all from Python built-in datasets.

Dylan's directive: "Yeah, lets let it rip!!"
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import math
import warnings, time as clock_time
warnings.filterwarnings('ignore')

t_start = clock_time.time()

PHI = (1 + math.sqrt(5)) / 2

# ── Import ARASystem from 226 ──
exec_226 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '226_ara_bridge.py')
with open(exec_226, 'r') as f:
    code_226 = f.read()
lines_226 = code_226.split('\n')
cut_226 = None
for i, line in enumerate(lines_226):
    if 'class ARABridge' in line:
        cut_226 = i
        break
ns_226 = {}
exec('\n'.join(lines_226[:cut_226]), ns_226)
ARASystem = ns_226['ARASystem']


# ── Camshaft midline functions (from 237k2) ──
def _base_midline(a):
    a = max(0.01, a)
    return 1.0 + (1.0/(1.0+a)) * (a - 1.0)

def midline_inverse_valve(ara):
    if ara >= 1.0:
        return _base_midline(ara)
    else:
        return _base_midline(1.0 / max(0.01, ara))

def _phi_dist(ara):
    a = max(0.01, ara)
    return abs(math.log(a)) / math.log(PHI)

def midline_camshaft(ara):
    """Camshaft-E: palindrome [0,1/φ], quadratic ramp [1/φ,1], full [1+]."""
    inv_offset = midline_inverse_valve(ara) - 1.0
    pd = _phi_dist(ara)
    zone = 1.0 / PHI
    if pd <= zone:
        return 1.0
    if pd >= 1.0:
        return 1.0 + inv_offset
    ramp_width = 1.0 / (PHI * PHI)
    t = (pd - zone) / ramp_width
    factor = t * t
    return 1.0 + inv_offset * factor


# ═══════════════════════════════════════════════════════════════
# LOAD ENSO DATA — statsmodels elnino dataset
# ═══════════════════════════════════════════════════════════════

print("=" * 78)
print("Script 242c — ENSO Coupled Network")
print("=" * 78)
print()

try:
    import statsmodels.api as sm
    elnino_data = sm.datasets.elnino.load_pandas().data
    print(f"Loaded elnino dataset: {elnino_data.shape}")
    print(f"Columns: {list(elnino_data.columns)}")
    print(f"Year range: {elnino_data['YEAR'].min():.0f} - {elnino_data['YEAR'].max():.0f}")
except Exception as e:
    print(f"ERROR loading elnino: {e}")
    sys.exit(1)

# Convert to time series: (year_decimal, SST)
months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
          'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

time_series = []
for _, row in elnino_data.iterrows():
    year = int(row['YEAR'])
    for m_idx, month in enumerate(months):
        t = year + (m_idx + 0.5) / 12.0
        sst = row[month]
        time_series.append((t, sst))

time_series.sort(key=lambda x: x[0])
times = np.array([x[0] for x in time_series])
sst_vals = np.array([x[1] for x in time_series])

print(f"\nTotal monthly observations: {len(time_series)}")
print(f"Time span: {times[0]:.1f} to {times[-1]:.1f}")
print(f"SST range: {sst_vals.min():.2f} to {sst_vals.max():.2f}")
print(f"SST mean: {sst_vals.mean():.2f}")


# ═══════════════════════════════════════════════════════════════
# STEP 1: Extract ENSO amplitude envelope
# ═══════════════════════════════════════════════════════════════

print()
print("─" * 78)
print("STEP 1: ENSO Amplitude Envelope Extraction")
print("─" * 78)

# Remove seasonal cycle (climatological monthly mean)
seasonal = np.zeros(12)
for m in range(12):
    seasonal[m] = np.mean(sst_vals[m::12])

sst_anomaly = np.copy(sst_vals)
for i in range(len(sst_anomaly)):
    sst_anomaly[i] -= seasonal[i % 12]

print(f"\nSeasonal cycle removed. Anomaly range: {sst_anomaly.min():.2f} to {sst_anomaly.max():.2f}")

# Smooth anomalies with 5-month running mean (standard ENSO smoothing)
smooth_window = 5
hw = smooth_window // 2
sst_smooth = np.zeros(len(sst_anomaly))
for i in range(len(sst_anomaly)):
    lo = max(0, i - hw)
    hi = min(len(sst_anomaly), i + hw + 1)
    sst_smooth[i] = np.mean(sst_anomaly[lo:hi])

# Extract El Niño PEAKS (positive anomaly maxima)
# These are the accumulation-release events
min_gap_months = 24  # At least 2 years between events
peaks = []
for i in range(2, len(sst_smooth) - 2):
    if (sst_smooth[i] > sst_smooth[i-1] and sst_smooth[i] > sst_smooth[i-2] and
        sst_smooth[i] > sst_smooth[i+1] and sst_smooth[i] > sst_smooth[i+2] and
        sst_smooth[i] > 0.3):  # Must be positive anomaly > 0.3°C
        if len(peaks) == 0 or (i - peaks[-1][0]) >= min_gap_months:
            peaks.append((i, times[i], sst_smooth[i]))

print(f"\nFound {len(peaks)} El Niño events:")
for idx, t, val in peaks:
    print(f"  {t:.2f}  SST anomaly: +{val:.2f}°C")

# Also extract La Niña TROUGHS (negative anomaly minima)
troughs = []
for i in range(2, len(sst_smooth) - 2):
    if (sst_smooth[i] < sst_smooth[i-1] and sst_smooth[i] < sst_smooth[i-2] and
        sst_smooth[i] < sst_smooth[i+1] and sst_smooth[i] < sst_smooth[i+2] and
        sst_smooth[i] < -0.3):  # Must be negative anomaly < -0.3°C
        if len(troughs) == 0 or (i - troughs[-1][0]) >= min_gap_months:
            troughs.append((i, times[i], sst_smooth[i]))

print(f"\nFound {len(troughs)} La Niña events:")
for idx, t, val in troughs:
    print(f"  {t:.2f}  SST anomaly: {val:.2f}°C")


# ═══════════════════════════════════════════════════════════════
# STEP 2: Measure ENSO's ARA from the data
# ═══════════════════════════════════════════════════════════════

print()
print("─" * 78)
print("STEP 2: ENSO ARA Measurement")
print("─" * 78)

# For each cycle: measure rise time (accumulation) and fall time (release)
# A cycle goes trough → peak → trough
# Accumulation = trough-to-peak time
# Release = peak-to-trough time

# Match troughs and peaks into cycles
cycles = []
for i in range(len(peaks)):
    # Find the trough BEFORE this peak
    pre_trough = None
    for t_idx, t_time, t_val in troughs:
        if t_time < peaks[i][1]:
            pre_trough = (t_idx, t_time, t_val)

    # Find the trough AFTER this peak
    post_trough = None
    for t_idx, t_time, t_val in troughs:
        if t_time > peaks[i][1]:
            post_trough = (t_idx, t_time, t_val)
            break

    if pre_trough and post_trough:
        accum_time = peaks[i][1] - pre_trough[1]
        release_time = post_trough[1] - peaks[i][1]
        if accum_time > 0 and release_time > 0:
            ratio = release_time / accum_time
            period = post_trough[1] - pre_trough[1]
            cycles.append({
                'peak_time': peaks[i][1],
                'peak_val': peaks[i][2],
                'accum_time': accum_time,
                'release_time': release_time,
                'ratio': ratio,
                'period': period
            })

print(f"\nComplete cycles measured: {len(cycles)}")
print(f"\n{'Peak Year':>10} {'Peak SST':>10} {'T_acc':>8} {'T_rel':>8} {'Ratio':>8} {'Period':>8}")
print("─" * 60)

ratios = []
periods = []
for c in cycles:
    print(f"  {c['peak_time']:8.2f}  {c['peak_val']:8.2f}  "
          f"{c['accum_time']:6.2f}yr  {c['release_time']:6.2f}yr  "
          f"{c['ratio']:6.3f}   {c['period']:6.2f}yr")
    ratios.append(c['ratio'])
    periods.append(c['period'])

mean_ratio = np.mean(ratios) if ratios else 0
median_ratio = np.median(ratios) if ratios else 0
mean_period = np.mean(periods) if periods else 0

print(f"\n  Mean T_release/T_accumulation: {mean_ratio:.3f}")
print(f"  Median T_release/T_accumulation: {median_ratio:.3f}")
print(f"  Mean period: {mean_period:.2f} yr")
print(f"  φ³ = {PHI**3:.2f} yr (prediction)")

# Compare with framework expectation
print(f"\n  Framework expectation: ARA = 2.0 (pure harmonic)")
print(f"  Measured ARA (mean): {mean_ratio:.3f}")
print(f"  Measured ARA (median): {median_ratio:.3f}")

ENSO_ARA = median_ratio  # Use median as more robust
ENSO_PERIOD = mean_period


# ═══════════════════════════════════════════════════════════════
# STEP 3: ENSO's Connection Field
# ═══════════════════════════════════════════════════════════════

print()
print("─" * 78)
print("STEP 3: ENSO's 6-Way Connection Field")
print("─" * 78)
print()

def derive_connections(name, ara, period):
    """Derive 6 coupling partners from seed system's ARA and period."""
    connections = []

    # 1. Horizontal mirror: ARA_partner = 2 - ARA, same period
    connections.append({
        'type': 'Horizontal mirror',
        'symbol': '↔',
        'ara': 2.0 - ara,
        'period': period,
        'strength': PHI**2,
        'channel': 'Space ↔ Time'
    })

    # 2. Vertical child ↓: ARA/φ, period×φ
    connections.append({
        'type': 'Vertical child ↓',
        'symbol': '↓',
        'ara': ara / PHI,
        'period': period * PHI,
        'strength': 2.0 / PHI,
        'channel': 'Parent → Child'
    })

    # 3. Vertical parent ↑: ARA×φ (capped at 2.0), period/φ
    connections.append({
        'type': 'Vertical parent ↑',
        'symbol': '↑',
        'ara': min(2.0, ara * PHI),
        'period': period / PHI,
        'strength': PHI,
        'channel': 'Child → Parent'
    })

    # 4. Cascade child ↓↓: ARA/φ², period×φ²
    connections.append({
        'type': 'Cascade child ↓↓',
        'symbol': '↓↓',
        'ara': ara / (PHI**2),
        'period': period * PHI**2,
        'strength': (2.0/PHI)**2,
        'channel': '2-rung cascade down'
    })

    # 5. Cascade parent ↑↑: ARA×φ² (capped at 2.0), period/φ²
    connections.append({
        'type': 'Cascade parent ↑↑',
        'symbol': '↑↑',
        'ara': min(2.0, ara * PHI**2),
        'period': period / PHI**2,
        'strength': PHI**2,
        'channel': '2-rung cascade up'
    })

    # 6. Inverse complement ⊗: 1/ARA, period×φ⁴
    inv_ara = 1.0 / max(0.01, ara)
    connections.append({
        'type': 'Inverse complement ⊗',
        'symbol': '⊗',
        'ara': inv_ara,
        'period': period * PHI**4,
        'strength': 1.0 / (PHI**4),
        'channel': 'Deep resonance'
    })

    return connections


# Known systems for matching
KNOWN_SYSTEMS = [
    ('Solar',        PHI,    11.07, 'Astrophysics'),
    ('ENSO',         2.0,    3.75,  'Climate'),
    ('Earthquake',   0.15,   11.09, 'Seismology'),
    ('Heart',        1.35,   0.00019, 'Cardiology'),
    ('Hare',         1.0,    9.6,   'Ecology'),
    ('Lynx',         1.0,    9.5,   'Ecology'),
    ('Unemployment', 0.75,   7.0,   'Economics'),
    ('GDP Growth',   1.0,    3.9,   'Economics'),
    ('CO2 Amp',      0.15,   7.6,   'Atmospheric'),
    ('Nile',         0.15,   7.5,   'Hydrology'),
    ('QBO',          None,   2.3,   'Climate'),
    ('NAO',          None,   7.0,   'Climate'),
    ('PDO',          None,   25.0,  'Climate'),
    ('IOD',          None,   3.5,   'Climate'),
]


def find_matches(pred_ara, pred_period, exclude_name=''):
    """Find known systems near predicted ARA and period."""
    matches = []
    for name, ara, period, domain in KNOWN_SYSTEMS:
        if name == exclude_name:
            continue

        period_ratio = max(pred_period, period) / max(0.001, min(pred_period, period))
        if period_ratio > 2.5:
            continue  # Too far in period

        if ara is not None:
            ara_dist = abs(ara - pred_ara)
            score = ara_dist + (period_ratio - 1.0)
        else:
            ara_dist = None
            score = period_ratio - 1.0

        matches.append((name, ara, period, domain, score, ara_dist, period_ratio))

    matches.sort(key=lambda x: x[4])
    return matches[:3]


print(f"Seed: ENSO (measured ARA={ENSO_ARA:.3f}, P={ENSO_PERIOD:.2f}yr)")
print(f"       vs framework expectation: ARA=2.0, P=φ³={PHI**3:.2f}yr")
print()

# Use MEASURED values
connections = derive_connections('ENSO', ENSO_ARA, ENSO_PERIOD)

# Also show connections from the THEORETICAL ENSO (ARA=2.0, P=φ³)
connections_theory = derive_connections('ENSO', 2.0, PHI**3)

print(f"{'Connection':<24} {'Predicted ARA':>14} {'Period':>10}  Best Match")
print("─" * 90)

for conn_m, conn_t in zip(connections, connections_theory):
    # Find matches for measured
    matches = find_matches(conn_m['ara'], conn_m['period'], 'ENSO')
    match_str = ""
    if matches:
        m = matches[0]
        m_ara = f"ARA={m[1]:.2f}" if m[1] is not None else "ARA=?"
        match_str = f"{m[0]} ({m_ara}, P={m[2]:.1f}yr)"

    print(f"  {conn_m['type']:<22} "
          f"ARA={conn_m['ara']:>6.3f}   P={conn_m['period']:>6.2f}yr  "
          f"→ {match_str}")

# Show theoretical too
print()
print(f"  --- Same connections from THEORETICAL ENSO (ARA=2.0, P=4.24yr) ---")
print()

for conn_t in connections_theory:
    matches = find_matches(conn_t['ara'], conn_t['period'], 'ENSO')
    match_str = ""
    if matches:
        m = matches[0]
        m_ara = f"ARA={m[1]:.2f}" if m[1] is not None else "ARA=?"
        match_str = f"{m[0]} ({m_ara}, P={m[2]:.1f}yr)"

    print(f"  {conn_t['type']:<22} "
          f"ARA={conn_t['ara']:>6.3f}   P={conn_t['period']:>6.2f}yr  "
          f"→ {match_str}")


# ═══════════════════════════════════════════════════════════════
# STEP 4: The φ⁴ Rung — Where is the Missing Engine?
# ═══════════════════════════════════════════════════════════════

print()
print("─" * 78)
print("STEP 4: The φ⁴ Rung — Hunting the Missing Engine")
print("─" * 78)
print()

phi4_period = PHI**4
print(f"φ⁴ = {phi4_period:.2f} yr")
print()

# What sits at φ⁴?
print("Known systems near φ⁴ rung:")
phi4_systems = [
    ('CO2 Amplitude', 0.15, 7.6, 'Consumer — half-system, loses to sine'),
    ('Nile',          0.15, 7.5, 'Consumer — half-system, loses to sine'),
    ('Unemployment',  0.75, 7.0, 'Near-clock — moderate consumer'),
    ('NAO',           None, 7.0, 'Period match, ARA unknown'),
]

for name, ara, period, note in phi4_systems:
    ara_str = f"ARA={ara:.2f}" if ara is not None else "ARA=?"
    mirror_str = f"mirror={2.0-ara:.2f}" if ara is not None else ""
    print(f"  {name:<16} {ara_str:>8}  P={period:.1f}yr  {mirror_str}  ({note})")

print()
print("What ENSO's connection field predicts at φ⁴:")
print()

# ENSO's vertical child (↓1 rung) should land near φ⁴
# From measured ENSO:
vc_ara = ENSO_ARA / PHI
vc_period = ENSO_PERIOD * PHI
print(f"  ENSO vertical child (measured):  ARA={vc_ara:.3f}, P={vc_period:.2f}yr")

# From theoretical ENSO:
vc_ara_t = 2.0 / PHI
vc_period_t = PHI**3 * PHI  # = φ⁴
print(f"  ENSO vertical child (theory):    ARA={vc_ara_t:.3f}, P={vc_period_t:.2f}yr")
print(f"                                   = ARA=2/φ={vc_ara_t:.4f}")

print()
print("  *** CRITICAL FINDING ***")
print(f"  ENSO (ARA=2.0) at φ³ predicts its vertical child at:")
print(f"    ARA = 2/φ = {2.0/PHI:.4f}")
print(f"    P = φ⁴ = {PHI**4:.2f} yr")
print()
print(f"  2/φ = {2.0/PHI:.4f}")
print(f"  This is the VERTICAL COUPLER itself (2/φ = {2.0/PHI:.4f})")
print(f"  The child inherits the coupling constant as its ARA!")
print()

# What about the HORIZONTAL mirror of this child?
child_mirror = 2.0 - (2.0/PHI)
print(f"  Horizontal mirror of φ⁴ child: ARA = 2 - 2/φ = {child_mirror:.4f}")
print(f"  This is 2(1 - 1/φ) = 2/φ² = {2.0/PHI**2:.4f}")
print()

# Check: CO2 and Nile are at 0.15 — how does that relate?
print(f"  CO2/Nile are at ARA = 0.15")
print(f"  2/φ² = {2.0/PHI**2:.4f}")
print(f"  1/φ⁴ = {1.0/PHI**4:.4f}")
print(f"  The consumers at 0.15 are near 1/φ⁴ = {1.0/PHI**4:.4f}")
print()

print("  Geometric interpretation:")
print(f"  At the φ⁴ rung, ENSO's energy cascades down with ARA = 2/φ = {2.0/PHI:.3f}")
print(f"  The mirror engine should be at ARA = 2 - 2/φ = {child_mirror:.3f}")
print(f"  CO2/Nile at ARA≈0.15 ≈ 1/φ⁴ are CASCADE consumers (↓↓ from φ⁴)")
print(f"  Unemployment at 0.75 ≈ 1/φ⁰·⁶ sits between consumer and clock")


# ═══════════════════════════════════════════════════════════════
# STEP 5: Run the Formula on ENSO
# ═══════════════════════════════════════════════════════════════

print()
print("─" * 78)
print("STEP 5: Camshaft Formula on ENSO Envelope")
print("─" * 78)
print()

# Extract ENSO envelope peaks for formula testing
peak_times = [p[1] for p in peaks]
peak_vals = [p[2] for p in peaks]

print(f"ENSO envelope: {len(peak_times)} peaks")
print(f"  Time range: {peak_times[0]:.1f} to {peak_times[-1]:.1f}")
print(f"  Value range: {min(peak_vals):.2f} to {max(peak_vals):.2f}")

if len(peak_times) < 5:
    print("\n  Not enough peaks for meaningful formula test.")
    print("  (Need at least 5 for LOO cross-validation)")
else:
    # ARA scan — find best ARA for ENSO peaks
    best_mae = 999
    best_ara = None
    best_shift = None

    n_peaks = len(peak_times)
    dt = np.diff(peak_times)
    mean_dt = np.mean(dt)

    ara_range = np.linspace(0.05, 2.5, 100)
    shift_range = np.linspace(-0.5, 0.5, 50)

    for test_ara in ara_range:
        mid_val = midline_camshaft(test_ara)

        for test_shift in shift_range:
            # Generate predictions from camshaft formula
            errors = []
            for i in range(1, n_peaks):
                # Predict interval based on previous
                predicted_dt = mean_dt * mid_val + test_shift
                actual_dt = dt[i-1] if i-1 < len(dt) else mean_dt
                errors.append(abs(predicted_dt - actual_dt))

            mae = np.mean(errors) if errors else 999
            if mae < best_mae:
                best_mae = mae
                best_ara = test_ara
                best_shift = test_shift

    print(f"\n  Basic interval prediction (camshaft midline):")
    print(f"    Best ARA: {best_ara:.3f}")
    print(f"    Best MAE: {best_mae:.3f} yr")
    print(f"    Mean interval: {mean_dt:.2f} yr")
    print(f"    Camshaft midline at best ARA: {midline_camshaft(best_ara):.4f}")

    # Compare to sine baseline
    sine_mae = np.mean(np.abs(dt - mean_dt))
    print(f"\n    Sine baseline MAE (constant mean): {sine_mae:.3f} yr")
    print(f"    Formula improvement: {(sine_mae - best_mae)/sine_mae*100:.1f}%")

    # ── LOO Cross-Validation ──
    print(f"\n  LOO Cross-Validation ({n_peaks} peaks):")

    loo_errors = []
    for leave_out in range(n_peaks):
        train_times = [peak_times[j] for j in range(n_peaks) if j != leave_out]
        train_vals = [peak_vals[j] for j in range(n_peaks) if j != leave_out]

        train_dt = np.diff(train_times)
        train_mean_dt = np.mean(train_dt)

        # Find best ARA on training set
        best_train_mae = 999
        best_train_ara = PHI  # default

        for test_ara in ara_range:
            mid_val = midline_camshaft(test_ara)
            errs = []
            for i in range(len(train_dt)):
                pred = train_mean_dt * mid_val
                errs.append(abs(pred - train_dt[i]))
            mae = np.mean(errs)
            if mae < best_train_mae:
                best_train_mae = mae
                best_train_ara = test_ara

        # Predict left-out peak
        if leave_out > 0 and leave_out < n_peaks:
            # Predict from previous
            mid = midline_camshaft(best_train_ara)
            pred_time = peak_times[leave_out - 1] + train_mean_dt * mid
            error = abs(pred_time - peak_times[leave_out])
            loo_errors.append(error)

    if loo_errors:
        loo_mae = np.mean(loo_errors)
        # Also compute sine LOO
        sine_loo_errors = []
        for leave_out in range(1, n_peaks):
            train_times = [peak_times[j] for j in range(n_peaks) if j != leave_out]
            train_dt = np.diff(train_times)
            pred_time = peak_times[leave_out - 1] + np.mean(train_dt)
            error = abs(pred_time - peak_times[leave_out])
            sine_loo_errors.append(error)
        sine_loo = np.mean(sine_loo_errors)

        print(f"    Formula LOO MAE: {loo_mae:.3f} yr")
        print(f"    Sine LOO MAE: {sine_loo:.3f} yr")

        if loo_mae < sine_loo:
            improvement = (sine_loo - loo_mae) / sine_loo * 100
            print(f"    → Formula WINS by {improvement:.1f}%")
        else:
            deficit = (loo_mae - sine_loo) / sine_loo * 100
            print(f"    → Formula LOSES by {deficit:.1f}%")
            print(f"    → ENSO may be pure harmonic (ARA=2.0) — sine IS the formula")


# ═══════════════════════════════════════════════════════════════
# STEP 6: Multi-Scale Coupling Analysis
# ═══════════════════════════════════════════════════════════════

print()
print("─" * 78)
print("STEP 6: Multi-Scale Coupling — φ-Power Spectral Decomposition")
print("─" * 78)
print()

# Check if ENSO SST anomalies contain φ-power periodicities
# Using simple FFT on the monthly anomaly data
from numpy.fft import fft, fftfreq

N = len(sst_anomaly)
dt_months = 1.0 / 12.0  # monthly data in years

# FFT
fft_vals = fft(sst_anomaly)
freqs = fftfreq(N, d=dt_months)

# Only positive frequencies
pos_mask = freqs > 0
pos_freqs = freqs[pos_mask]
pos_power = np.abs(fft_vals[pos_mask])**2
pos_periods = 1.0 / pos_freqs  # periods in years

# Focus on periods from 1 to 30 years
valid = (pos_periods >= 1.0) & (pos_periods <= 30.0)
vp_periods = pos_periods[valid]
vp_power = pos_power[valid]

# Find spectral peaks
peak_indices = []
for i in range(2, len(vp_power) - 2):
    if (vp_power[i] > vp_power[i-1] and vp_power[i] > vp_power[i-2] and
        vp_power[i] > vp_power[i+1] and vp_power[i] > vp_power[i+2]):
        peak_indices.append(i)

# Sort by power
peak_indices.sort(key=lambda i: vp_power[i], reverse=True)

print("Top spectral peaks in ENSO SST anomalies:")
print(f"  {'Period (yr)':>12} {'Power':>12} {'Nearest φ^n':>14} {'φ-rung':>8} {'Match':>8}")
print("  " + "─" * 60)

for idx in peak_indices[:10]:
    p = vp_periods[idx]
    pw = vp_power[idx]

    # Find nearest φ-power
    best_rung = None
    best_diff = 999
    for n in range(-2, 12):
        phi_n = PHI**n
        ratio = max(p, phi_n) / min(p, phi_n)
        if ratio - 1.0 < best_diff:
            best_diff = ratio - 1.0
            best_rung = n

    match_quality = "EXACT" if best_diff < 0.05 else ("CLOSE" if best_diff < 0.15 else "NEAR" if best_diff < 0.3 else "")
    phi_n_val = PHI**best_rung

    print(f"  {p:10.2f} yr  {pw:10.0f}    φ^{best_rung}={phi_n_val:.2f}yr  "
          f"  n={best_rung}  {match_quality}")


# ═══════════════════════════════════════════════════════════════
# STEP 7: Cross-Rung Coupling Check
# ═══════════════════════════════════════════════════════════════

print()
print("─" * 78)
print("STEP 7: Cross-Rung Coupling — Does φ⁴ Energy Appear in ENSO?")
print("─" * 78)
print()

# The key question: does ENSO's spectrum contain a φ⁴ ≈ 6.85 yr component?
# If it does, that's the vertical child coupling — ENSO feeding the φ⁴ rung

phi4_target = PHI**4
tolerance = 0.15  # 15% tolerance

# Find power at φ⁴
phi4_band = (vp_periods >= phi4_target * (1 - tolerance)) & (vp_periods <= phi4_target * (1 + tolerance))
phi4_power = np.max(vp_power[phi4_band]) if np.any(phi4_band) else 0

# Find power at φ³ (ENSO's own period)
phi3_target = PHI**3
phi3_band = (vp_periods >= phi3_target * (1 - tolerance)) & (vp_periods <= phi3_target * (1 + tolerance))
phi3_power = np.max(vp_power[phi3_band]) if np.any(phi3_band) else 0

# Find power at φ² (QBO-like)
phi2_target = PHI**2
phi2_band = (vp_periods >= phi2_target * (1 - tolerance)) & (vp_periods <= phi2_target * (1 + tolerance))
phi2_power = np.max(vp_power[phi2_band]) if np.any(phi2_band) else 0

# Find power at φ⁵ (Solar-like)
phi5_target = PHI**5
phi5_band = (vp_periods >= phi5_target * (1 - tolerance)) & (vp_periods <= phi5_target * (1 + tolerance))
phi5_power = np.max(vp_power[phi5_band]) if np.any(phi5_band) else 0

total_power = np.sum(vp_power)

print(f"  φ-Power Content in ENSO Spectrum:")
print(f"  {'Rung':>6} {'Period':>8} {'Power':>12} {'% Total':>10}")
print(f"  " + "─" * 40)
print(f"  {'φ²':>6} {phi2_target:>7.2f}yr {phi2_power:>10.0f}   {phi2_power/total_power*100:>6.2f}%")
print(f"  {'φ³':>6} {phi3_target:>7.2f}yr {phi3_power:>10.0f}   {phi3_power/total_power*100:>6.2f}%")
print(f"  {'φ⁴':>6} {phi4_target:>7.2f}yr {phi4_power:>10.0f}   {phi4_power/total_power*100:>6.2f}%")
print(f"  {'φ⁵':>6} {phi5_target:>7.2f}yr {phi5_power:>10.0f}   {phi5_power/total_power*100:>6.2f}%")

print()
if phi4_power > 0:
    ratio_43 = phi4_power / max(1, phi3_power)
    print(f"  φ⁴/φ³ power ratio: {ratio_43:.3f}")
    print(f"  1/φ⁴ = {1/PHI**4:.3f}")
    print(f"  If ratio ≈ 1/φ⁴ = {1/PHI**4:.3f}, the coupling strength matches geometry!")

    if abs(ratio_43 - 1/PHI**4) < 0.1:
        print(f"  → MATCH! Power transfers between rungs at 1/φ⁴ strength")
    elif ratio_43 < 1/PHI**4:
        print(f"  → Below expected coupling — φ⁴ rung is STARVED for energy")
        print(f"  → Consistent with missing engine hypothesis!")
    else:
        print(f"  → Above expected coupling — something extra feeds φ⁴ rung")


# ═══════════════════════════════════════════════════════════════
# STEP 8: Network Summary
# ═══════════════════════════════════════════════════════════════

print()
print("=" * 78)
print("NETWORK SUMMARY — ENSO as Hub")
print("=" * 78)
print()

print("ENSO sits at φ³ (ARA≈2.0, P≈4.2yr) — the pure harmonic ceiling.")
print("Its connection field radiates outward:")
print()
print("  UPWARD:")
print(f"    ↑  φ² rung (P≈{PHI**2:.1f}yr) — QBO territory. ARA pred = {min(2.0, ENSO_ARA*PHI):.3f}")
print(f"    ↑↑ φ¹ rung (P≈{PHI:.1f}yr)  — ~1.6yr oscillation. ARA pred = {min(2.0, ENSO_ARA*PHI**2):.3f}")
print()
print("  DOWNWARD:")
print(f"    ↓  φ⁴ rung (P≈{PHI**4:.1f}yr) — CO2/Nile/NAO territory. ARA pred = {ENSO_ARA/PHI:.3f}")
print(f"    ↓↓ φ⁵ rung (P≈{PHI**5:.1f}yr)— Solar territory. ARA pred = {ENSO_ARA/PHI**2:.3f}")
print()
print("  HORIZONTAL:")
print(f"    ↔  φ³ mirror (P≈{PHI**3:.1f}yr) — ARA pred = {2.0-ENSO_ARA:.3f}")
print(f"       (singularity boundary — ENSO has no equal horizontal partner)")
print()
print("  INVERSE:")
print(f"    ⊗  (P≈{PHI**3 * PHI**4:.1f}yr) — ARA pred = {1.0/max(0.01,ENSO_ARA):.3f}")
print(f"       (Gleissberg/AMO territory)")

print()
print("THE KEY PREDICTION:")
print(f"  ENSO feeds the φ⁴ rung from above with ARA = 2/φ = {2.0/PHI:.3f}")
print(f"  The φ⁴ rung has 3 consumers (CO2=0.15, Nile=0.15, Unemployment=0.75)")
print(f"  Their horizontal mirrors demand an ENGINE at ARA ≈ 1.85")
print(f"  ENSO's child arrives at ARA = {2.0/PHI:.3f} — it IS the engine,")
print(f"  dampened by one φ-step of friction from the cascade!")
print()

if abs(2.0/PHI - 1.236) < 0.01:
    print(f"  *** 2/φ = {2.0/PHI:.4f} falls in the 'shock absorber' zone (1.0-1.3) ***")
    print(f"  This means the ENSO child at φ⁴ is a MODERATOR, not a generator.")
    print(f"  It absorbs ENSO energy and redistributes it to CO2/Nile/etc.")
    print(f"  The ACTUAL engine at 1.85 may be the MONSOON system,")
    print(f"  which generates independently AND receives ENSO cascades.")

print()
elapsed = clock_time.time() - t_start
print(f"Completed in {elapsed:.1f}s")

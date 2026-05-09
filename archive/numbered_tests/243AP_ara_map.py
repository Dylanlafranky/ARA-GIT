#!/usr/bin/env python3
"""
Script 243AP — ARA Architecture Map & Error Decomposition

NOT a prediction script. A DIAGNOSTIC tool.

Maps every nested ARA layer in the champion cascade (243AJ) and decomposes
the prediction error into:
  1. What the cascade periods contribute (φ⁹ timing)
  2. What the sawtooth gate adds (accumulate/snap)
  3. What the midline shift adds
  4. What the amplitude scale adds
  5. What the gear tilt (inter-rung coupling) adds
  6. What's LEFT — the non-ARA residual

This tells us exactly where the remaining error lives and what kind of
mechanism could address it.
"""
import math
import numpy as np

PHI   = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_3 = INV_PHI**3
INV_PHI_4 = INV_PHI**4
INV_PHI_9 = INV_PHI**9
PHI_2 = PHI**2
TAU   = 2 * math.pi
LOG2  = math.log(2)
TWO_OVER_PHI = 2.0 / PHI

def ara_midline(ara):
    acc = 1.0 / (1.0 + max(0.01, ara))
    return 1.0 + acc * (ara - 1.0)

def find_triangle_position(ara):
    s = max(0, min(1, (ara - 0) / 2))
    t = max(0, min(1, 1 - abs(ara - 1)))
    r = max(0, min(1, (2 - ara) / 2))
    total = s + t + r
    if total > 0: s /= total; t /= total; r /= total
    return s, t, r

def blend_distances(s, t, r):
    d_s = 3 * PHI; d_t = 1; d_r = -1; d_g = 5 * PHI
    return [d_s * s + d_t * t + d_r * r,
            d_g,
            (d_s * s + d_t * t + d_r * r) * INV_PHI,
            (d_s * s + d_t * t + d_r * r) * INV_PHI**2]

def decay_double_log(ara, momentum=0.0):
    x = max(0.01, abs(ara - 1.0))
    base = math.log1p(math.log1p(x)) / math.log1p(math.log1p(1.0))
    return min(0.99, base * 0.618)

# ════════════════════════════════════════════════════════════════
# LAYER-BY-LAYER CASCADE DECOMPOSITION
# ════════════════════════════════════════════════════════════════

def cascade_decomposed(t, t_ref, period, ara, base_amp, prev_amp,
                        pos_s, pos_t, pos_r):
    """Run cascade_shape step by step, returning value at each layer."""
    schwabe = period
    midline = ara_midline(ara)
    amp_scale = midline  # 243AJ champion uses midline as amp

    if prev_amp is not None and base_amp > 0:
        inst_ara = prev_amp / base_amp
        inst_ara = max(0.01, min(2.0, inst_ara))
    else:
        inst_ara = ara

    # ── Layer 0: Raw cosine at Schwabe period ──
    sp = TAU * (t - t_ref) / schwabe
    raw_cos = math.cos(sp)
    layer0_cos = base_amp * (1 + 0.1 * raw_cos)  # simple cosine baseline

    # ── Layer 1: Triangle rider → cascade distances ──
    target_s, target_t_val, target_r = find_triangle_position(inst_ara)
    # Use passed position (already evolved) for decomposition
    live_d = blend_distances(pos_s, pos_t, pos_r)
    live_periods = [period * PHI**d for d in live_d]
    live_gleissberg = live_periods[1]
    phases = [TAU * (t - t_ref) / per for per in live_periods]
    cos_vals = [math.cos(ph) for ph in phases]
    sin_vals = [math.sin(ph) for ph in phases]
    gp = TAU * (t - t_ref) / live_gleissberg

    # ── Layer 2: Sawtooth gate ──
    acc = 1.0 / (1.0 + max(0.01, inst_ara))
    cp = (gp % TAU) / TAU
    if cp < acc:
        state = (cp / acc) * PHI
    else:
        ramp = (cp - acc) / (1 - acc)
        state = PHI * (1 - ramp) + INV_PHI * ramp
    gate = state / ((PHI + INV_PHI) / 2)

    # ── Layer 3: Full cascade shape (no midline, no amp_scale) ──
    collisions = [0.0]
    for j in range(1, len(phases)):
        collisions.append(-math.cos(phases[j-1] - phases[j]))
    eps_vals = []
    for j in range(len(phases)):
        d = live_d[j]
        base_eps = INV_PHI_4 if d > 0 else INV_PHI_3
        eps_vals.append(base_eps * gate)
    for j in range(len(phases)):
        d = live_d[j]
        space_phase = phases[j] * PHI_2
        rat_phase = phases[j] * TWO_OVER_PHI
        space_cos = math.cos(space_phase)
        rat_cos = math.cos(rat_phase)
        if d > 0:
            blend = (cos_vals[j] * PHI + space_cos * INV_PHI + rat_cos * INV_PHI)
            blend /= (PHI + INV_PHI + INV_PHI)
        else:
            blend = (cos_vals[j] * INV_PHI + space_cos * PHI + rat_cos * INV_PHI)
            blend /= (INV_PHI + PHI + INV_PHI)
        eps_vals[j] *= (1 + INV_PHI_4 * blend)
    for j in range(1, len(phases)):
        d = live_d[j]
        if d < 0:
            eps_vals[j] /= (1 + collisions[j] * INV_PHI)
            eps_vals[j] *= (1 + collisions[j] * INV_PHI * 0.5)
    for j in range(len(phases)):
        if j > 0: eps_vals[j] *= (1 + collisions[j] * INV_PHI)
        tens = -sin_vals[j]
        if inst_ara >= 1.0:
            if tens > 0: eps_vals[j] *= (1 + 0.5 * tens * (PHI - 1))
            else: eps_vals[j] *= (1 + 0.5 * tens * (1 - INV_PHI))
        else:
            log_tens = math.copysign(math.log1p(abs(tens)) / LOG2, tens)
            if log_tens > 0: eps_vals[j] *= (1 + 0.5 * log_tens * (PHI - 1))
            else: eps_vals[j] *= (1 + 0.5 * log_tens * (1 - INV_PHI))

    shape = 1.0
    for j in range(len(live_periods)):
        shape *= (1 + eps_vals[j] * cos_vals[j])
    shape += INV_PHI_9 * math.cos(gp)
    cp_schwabe = (sp % TAU) / TAU
    shape += INV_PHI_3 * math.exp(-PHI * cp_schwabe) * math.cos(sp)

    raw_cascade = shape  # before grief, midline, amp

    # ── Layer 4: Grief correction ──
    if prev_amp is not None:
        prev_dev = (prev_amp - base_amp) / base_amp
        grief_mult = 1.0 + INV_PHI_3 * (-prev_dev) * math.exp(-PHI)
        shape *= grief_mult
    after_grief = shape

    # ── Layer 5: Midline shift ──
    shape += (midline - 1.0)
    after_midline = shape

    # ── Layer 6: Amplitude scale ──
    deviation = shape - midline
    shape = midline + deviation * amp_scale
    after_amp = shape

    # Convert to amplitude predictions
    pred_no_mid_no_amp = base_amp * raw_cascade
    pred_with_grief = base_amp * after_grief
    pred_with_midline = base_amp * after_midline
    pred_full = base_amp * after_amp

    return {
        'inst_ara': inst_ara,
        'gate_state': state,
        'gate_value': gate,
        'raw_cascade': raw_cascade,
        'after_grief': after_grief,
        'after_midline': after_midline,
        'after_amp': after_amp,
        'pred_raw': pred_no_mid_no_amp,
        'pred_grief': pred_with_grief,
        'pred_midline': pred_with_midline,
        'pred_full': pred_full,
        'eps_sum': sum(abs(e) for e in eps_vals),
        'collision_sum': sum(abs(c) for c in collisions),
        'live_periods': live_periods,
        'live_distances': live_d,
    }


# ════════════════════════════════════════════════════════════════
# DATA
# ════════════════════════════════════════════════════════════════

SOLAR_CYCLES = [
    (1,  1761.5, 144.1), (2,  1769.7, 193.0), (3,  1778.4, 264.3),
    (4,  1788.1, 235.3), (5,  1805.2,  82.0), (6,  1816.4,  81.2),
    (7,  1829.9, 119.2), (8,  1837.2, 244.9), (9,  1848.1, 219.9),
    (10, 1860.1, 186.2), (11, 1870.6, 234.0), (12, 1883.9, 124.4),
    (13, 1894.1, 146.5), (14, 1906.2, 107.1), (15, 1917.6, 175.7),
    (16, 1928.4, 130.2), (17, 1937.4, 198.6), (18, 1947.5, 218.7),
    (19, 1957.9, 285.0), (20, 1968.9, 156.6), (21, 1979.9, 232.9),
    (22, 1989.6, 212.5), (23, 2001.9, 180.3), (24, 2014.3, 116.4),
    (25, 2024.5, 173.0),
]

solar_t = np.array([c[1] for c in SOLAR_CYCLES])
solar_a = np.array([c[2] for c in SOLAR_CYCLES])

PERIOD = PHI**5
ARA = PHI
RUNG = 5


# ════════════════════════════════════════════════════════════════
# GRID SEARCH (same as champion)
# ════════════════════════════════════════════════════════════════

def grid_search_simple(times, peaks, period, ara, n_tr=80, n_ba=40):
    from copy import deepcopy
    gleissberg = period * PHI**4
    data_span = times[-1] - times[0]
    tr_lo = times[0] - max(gleissberg, data_span)
    tr_hi = times[0] + 2 * period
    ba_lo = np.mean(peaks) * 0.3
    ba_hi = np.mean(peaks) * 1.8
    t_refs = np.linspace(tr_lo, tr_hi, n_tr)
    base_amps = np.linspace(ba_lo, ba_hi, n_ba)
    best_mae, best_tr, best_ba = 1e9, t_refs[0], base_amps[0]

    midline = ara_midline(ara)
    amp_scale = midline

    for tr in t_refs:
        for ba in base_amps:
            # Simple cascade_amplitude equivalent
            pos_s, pos_t_val, pos_r = find_triangle_position(ara)
            errors = []
            for k in range(len(times)):
                prev = peaks[k-1] if k > 0 else None
                result = cascade_decomposed(times[k], tr, period, ara, ba, prev,
                                           pos_s, pos_t_val, pos_r)
                pred = ba * result['after_amp']
                errors.append(abs(pred - peaks[k]))
            mae = np.mean(errors)
            if mae < best_mae:
                best_mae, best_tr, best_ba = mae, tr, ba
    return best_tr, best_ba, best_mae


# ════════════════════════════════════════════════════════════════
# MAIN — Decompose layer by layer
# ════════════════════════════════════════════════════════════════

print("=" * 78)
print("Script 243AP — ARA Architecture Map & Error Decomposition")
print("=" * 78)
print()

# Step 1: Fit (same as champion)
print("  Fitting t_ref and base_amp...")
fit_tr, fit_ba, fit_mae = grid_search_simple(solar_t, solar_a, PERIOD, ARA)
print(f"  t_ref = {fit_tr:.2f}, base_amp = {fit_ba:.1f}, full-fit MAE = {fit_mae:.2f}")
print()

# Step 2: Decompose every cycle
pos_s, pos_t_val, pos_r = find_triangle_position(ARA)
midline = ara_midline(ARA)

print("  NESTED ARA ARCHITECTURE:")
print(f"  System ARA = φ = {ARA:.4f}")
print(f"  Midline = {midline:.4f}")
print(f"  Amp scale = {midline:.4f} (static midline)")
print(f"  Accumulation fraction = {1/(1+ARA):.4f} (1/(1+ARA))")
print(f"  Snap fraction = {ARA/(1+ARA):.4f} (ARA/(1+ARA))")
print()

# Cascade periods
live_d = blend_distances(pos_s, pos_t_val, pos_r)
live_periods = [PERIOD * PHI**d for d in live_d]
print("  CASCADE PERIODS (φ⁹ distances from triangle rider):")
for i, (d, p) in enumerate(zip(live_d, live_periods)):
    name = ["Schwabe-scaled", "Gleissberg", "Sub-Gleissberg", "Sub-sub"][i]
    print(f"    {name:>16}: d={d:+.4f}, period={p:.2f} yr")
print()

# Per-cycle decomposition
print("─" * 100)
print(f"  {'C':>3} {'Year':>7} {'Actual':>7} │ {'Raw':>7} {'Δraw':>7} │ "
      f"{'Grief':>7} {'Δgr':>6} │ {'Mid':>7} {'Δmid':>6} │ "
      f"{'Full':>7} {'Δfull':>6} │ {'inst':>5} {'gate':>5}")
print("─" * 100)

errors_raw = []
errors_grief = []
errors_mid = []
errors_full = []
inst_aras = []
gates = []

for k, (c, yr, actual) in enumerate(SOLAR_CYCLES):
    prev = solar_a[k-1] if k > 0 else None
    result = cascade_decomposed(solar_t[k], fit_tr, PERIOD, ARA, fit_ba, prev,
                                pos_s, pos_t_val, pos_r)

    pred_raw = fit_ba * result['raw_cascade']
    pred_grief = fit_ba * result['after_grief']
    pred_mid = fit_ba * result['after_midline']
    pred_full = fit_ba * result['after_amp']

    e_raw = pred_raw - actual
    e_grief = pred_grief - actual
    e_mid = pred_mid - actual
    e_full = pred_full - actual

    errors_raw.append(abs(e_raw))
    errors_grief.append(abs(e_grief))
    errors_mid.append(abs(e_mid))
    errors_full.append(abs(e_full))
    inst_aras.append(result['inst_ara'])
    gates.append(result['gate_state'])

    flag = " ◀" if abs(e_full) > 60 else ""
    print(f"  C{c:>2} {yr:>7.1f} {actual:>7.1f} │ "
          f"{pred_raw:>7.1f} {e_raw:>+7.1f} │ "
          f"{pred_grief:>7.1f} {e_grief:>+6.1f} │ "
          f"{pred_mid:>7.1f} {e_mid:>+6.1f} │ "
          f"{pred_full:>7.1f} {e_full:>+6.1f} │ "
          f"{result['inst_ara']:>5.2f} {result['gate_state']:>5.2f}{flag}")

print("─" * 100)
print()

# Summary MAEs
mae_raw = np.mean(errors_raw)
mae_grief = np.mean(errors_grief)
mae_mid = np.mean(errors_mid)
mae_full = np.mean(errors_full)
sine_mae = np.mean(np.abs(solar_a - np.mean(solar_a)))

print("  LAYER-BY-LAYER MAE:")
print(f"    Sine baseline (mean)  : {sine_mae:.2f}")
print(f"    Layer 0: Raw cascade  : {mae_raw:.2f}  (φ⁹ periods + gate + collisions)")
print(f"    Layer 1: + Grief corr : {mae_grief:.2f}  (Δ = {mae_grief - mae_raw:+.2f})")
print(f"    Layer 2: + Midline    : {mae_mid:.2f}  (Δ = {mae_mid - mae_grief:+.2f})")
print(f"    Layer 3: + Amp scale  : {mae_full:.2f}  (Δ = {mae_full - mae_mid:+.2f})")
print()

# Error analysis — where are the big misses?
print("  TOP 10 WORST ERRORS (full model):")
sorted_errors = sorted(enumerate(errors_full), key=lambda x: -x[1])
for rank, (idx, err) in enumerate(sorted_errors[:10]):
    c, yr, actual = SOLAR_CYCLES[idx]
    pred = fit_ba * cascade_decomposed(solar_t[idx], fit_tr, PERIOD, ARA, fit_ba,
                                        solar_a[idx-1] if idx > 0 else None,
                                        pos_s, pos_t_val, pos_r)['after_amp']
    inst = inst_aras[idx]
    print(f"    {rank+1:>2}. C{c:>2} ({yr:.0f}): actual={actual:.0f}, pred={pred:.0f}, "
          f"err={err:.1f}, inst_ara={inst:.3f}")
print()

# ── Pattern analysis ──
print("  PATTERN ANALYSIS:")
# Group by inst_ara ranges
low_ara = [(i, e) for i, e in enumerate(errors_full) if inst_aras[i] < 0.8]
mid_ara = [(i, e) for i, e in enumerate(errors_full) if 0.8 <= inst_aras[i] <= 1.8]
high_ara = [(i, e) for i, e in enumerate(errors_full) if inst_aras[i] > 1.8]

if low_ara:
    print(f"    inst_ara < 0.8 (weak cycles): n={len(low_ara)}, "
          f"mean err={np.mean([e for _,e in low_ara]):.1f}")
if mid_ara:
    print(f"    inst_ara 0.8-1.8 (normal):    n={len(mid_ara)}, "
          f"mean err={np.mean([e for _,e in mid_ara]):.1f}")
if high_ara:
    print(f"    inst_ara > 1.8 (hot cycles):  n={len(high_ara)}, "
          f"mean err={np.mean([e for _,e in high_ara]):.1f}")
print()

# Actual amplitude bands
low_amp = [(i, e) for i, e in enumerate(errors_full) if solar_a[i] < 130]
mid_amp = [(i, e) for i, e in enumerate(errors_full) if 130 <= solar_a[i] <= 200]
high_amp = [(i, e) for i, e in enumerate(errors_full) if solar_a[i] > 200]

print(f"    Low amplitude (<130 SSN):  n={len(low_amp)}, "
      f"mean err={np.mean([e for _,e in low_amp]):.1f}")
print(f"    Mid amplitude (130-200):   n={len(mid_amp)}, "
      f"mean err={np.mean([e for _,e in mid_amp]):.1f}")
print(f"    High amplitude (>200 SSN): n={len(high_amp)}, "
      f"mean err={np.mean([e for _,e in high_amp]):.1f}")
print()

# Consecutive error patterns
print("  CONSECUTIVE ERROR DIRECTION:")
for k in range(1, len(errors_full)):
    c, yr, actual = SOLAR_CYCLES[k]
    prev_c, prev_yr, prev_actual = SOLAR_CYCLES[k-1]
    e_now = (fit_ba * cascade_decomposed(solar_t[k], fit_tr, PERIOD, ARA, fit_ba,
                                          solar_a[k-1] if k > 0 else None,
                                          pos_s, pos_t_val, pos_r)['after_amp']) - actual
    e_prev = (fit_ba * cascade_decomposed(solar_t[k-1], fit_tr, PERIOD, ARA, fit_ba,
                                            solar_a[k-2] if k > 1 else None,
                                            pos_s, pos_t_val, pos_r)['after_amp']) - prev_actual

    if abs(e_now) > 40 and abs(e_prev) > 40:
        same_dir = "SAME" if (e_now > 0) == (e_prev > 0) else "FLIP"
        print(f"    C{prev_c}→C{c}: {e_prev:+.0f} → {e_now:+.0f}  ({same_dir})")
print()

# ── The key question: what predicts the residual? ──
print("  RESIDUAL vs POSSIBLE DRIVERS:")
residuals = []
for k in range(len(SOLAR_CYCLES)):
    pred = fit_ba * cascade_decomposed(solar_t[k], fit_tr, PERIOD, ARA, fit_ba,
                                        solar_a[k-1] if k > 0 else None,
                                        pos_s, pos_t_val, pos_r)['after_amp']
    residuals.append(solar_a[k] - pred)

residuals = np.array(residuals)

# Correlation with inst_ara
corr_inst = np.corrcoef(inst_aras[1:], residuals[1:])[0, 1]  # skip C1 (no inst_ara)
print(f"    Residual × inst_ara:     r = {corr_inst:+.3f}")

# Correlation with gate state
corr_gate = np.corrcoef(gates, residuals)[0, 1]
print(f"    Residual × gate_state:   r = {corr_gate:+.3f}")

# Correlation with actual amplitude
corr_actual = np.corrcoef(solar_a, residuals)[0, 1]
print(f"    Residual × actual_amp:   r = {corr_actual:+.3f}")

# Correlation with cycle number (secular trend?)
corr_cycle = np.corrcoef(np.arange(len(residuals)), residuals)[0, 1]
print(f"    Residual × cycle_number: r = {corr_cycle:+.3f}")

# Correlation with delta between consecutive actuals
deltas = np.diff(solar_a)
corr_delta = np.corrcoef(deltas, residuals[1:])[0, 1]
print(f"    Residual × Δactual:      r = {corr_delta:+.3f}")

# Correlation with Gleissberg phase
gleiss_period = PERIOD * PHI**4
gleiss_phases = [(TAU * (t - fit_tr) / gleiss_period) % TAU for t in solar_t]
corr_gleiss = np.corrcoef(gleiss_phases, residuals)[0, 1]
print(f"    Residual × Gleiss_phase: r = {corr_gleiss:+.3f}")

# Is the residual itself periodic?
print()
print("  RESIDUAL AUTOCORRELATION:")
for lag in [1, 2, 3, 4, 5]:
    if lag < len(residuals):
        ac = np.corrcoef(residuals[:-lag], residuals[lag:])[0, 1]
        print(f"    Lag {lag}: r = {ac:+.3f}")

print()

# ── Non-ARA component size ──
total_var = np.var(solar_a)
pred_vals = []
for k in range(len(SOLAR_CYCLES)):
    pred = fit_ba * cascade_decomposed(solar_t[k], fit_tr, PERIOD, ARA, fit_ba,
                                        solar_a[k-1] if k > 0 else None,
                                        pos_s, pos_t_val, pos_r)['after_amp']
    pred_vals.append(pred)
pred_vals = np.array(pred_vals)
resid_var = np.var(residuals)
explained = 1 - resid_var / total_var

print(f"  VARIANCE DECOMPOSITION:")
print(f"    Total variance in solar amplitudes: {total_var:.1f}")
print(f"    Variance explained by ARA cascade:  {resid_var:.1f} residual → "
      f"{explained*100:.1f}% explained")
print(f"    Prediction range: {pred_vals.min():.0f} - {pred_vals.max():.0f} "
      f"(actual: {solar_a.min():.0f} - {solar_a.max():.0f})")
print(f"    Prediction std: {pred_vals.std():.1f} (actual std: {solar_a.std():.1f})")
print()

# ── The big picture ──
print("=" * 78)
print("  DIAGNOSIS")
print("=" * 78)
amp_ratio = pred_vals.std() / solar_a.std()
print(f"""
  The ARA cascade explains {explained*100:.1f}% of the variance.

  The prediction range is {pred_vals.std():.1f}/{solar_a.std():.1f} = {amp_ratio:.2f}x
  the actual standard deviation.

  {'The wave is TOO FLAT.' if amp_ratio < 0.8 else 'The wave amplitude is about right.' if amp_ratio < 1.2 else 'The wave is too volatile.'}

  The strongest residual correlate is:""")

correlates = [
    ("inst_ara", abs(corr_inst)),
    ("gate_state", abs(corr_gate)),
    ("actual_amp", abs(corr_actual)),
    ("cycle_number", abs(corr_cycle)),
    ("Δactual", abs(corr_delta)),
    ("Gleiss_phase", abs(corr_gleiss)),
]
correlates.sort(key=lambda x: -x[1])
for name, r in correlates:
    flag = " ★" if r > 0.3 else ""
    print(f"    {name:>15}: |r| = {r:.3f}{flag}")

print()
print("=" * 78)

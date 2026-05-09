#!/usr/bin/env python3
"""
243BL17 — Full ARA Analysis of Dylan's ME/CFS Health Data (Visible App Export)
=============================================================================
Treat the body as an ARA system:
  - HRV / Resting HR as the wave (primary oscillators)
  - Symptoms as the landscape
  - Crashes as singularity events
  - Functional capacity as the output measure

ARA methodology: same discrete (ups/downs ratio) and continuous
(magnitude-weighted) approach used in BL14-BL16.
"""

import csv, math, statistics, sys
from collections import defaultdict, Counter
from datetime import datetime, timedelta

# ─── CONFIG ──────────────────────────────────────────────────────────────
CSV_PATH = "../Visible_Data_Export_2026-4-27.csv"
PHI = (1 + math.sqrt(5)) / 2  # 1.618…

# ─── LOAD & PIVOT ────────────────────────────────────────────────────────
print("=" * 72)
print("PART 1: DATA LOADING & PIVOT")
print("=" * 72)

rows = []
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

print(f"Total rows: {len(rows)}")

# Pivot: date -> tracker_name -> value
data = defaultdict(dict)
notes = defaultdict(list)

for r in rows:
    date_str = r["observation_date"]
    name = r["tracker_name"]
    cat = r["tracker_category"]
    val_str = r["observation_value"].strip()

    if name == "Note":
        notes[date_str].append(val_str)
        continue

    try:
        val = float(val_str)
    except ValueError:
        continue

    data[date_str][name] = val

dates_sorted = sorted(data.keys())
print(f"Unique dates: {len(dates_sorted)}")
print(f"Date range: {dates_sorted[0]} to {dates_sorted[-1]}")

# Count tracker availability
tracker_counts = Counter()
for d in dates_sorted:
    for t in data[d]:
        tracker_counts[t] += 1

print(f"\nTracker availability (top 20):")
for t, c in tracker_counts.most_common(20):
    print(f"  {t}: {c} days")

# ─── HELPER: ARA CALCULATION ─────────────────────────────────────────────
def compute_ara(values, label=""):
    """Compute discrete and continuous ARA from a time series."""
    if len(values) < 5:
        return None

    diffs = [values[i+1] - values[i] for i in range(len(values)-1)]

    ups = sum(1 for d in diffs if d > 0)
    downs = sum(1 for d in diffs if d < 0)
    flats = sum(1 for d in diffs if d == 0)

    discrete_ara = (ups / downs) if downs > 0 else float('inf')

    mag_up = sum(abs(d) for d in diffs if d > 0)
    mag_down = sum(abs(d) for d in diffs if d < 0)
    continuous_ara = (mag_up / mag_down) if mag_down > 0 else float('inf')

    return {
        "label": label,
        "n": len(values),
        "n_diffs": len(diffs),
        "ups": ups,
        "downs": downs,
        "flats": flats,
        "discrete_ara": discrete_ara,
        "continuous_ara": continuous_ara,
        "mag_up": mag_up,
        "mag_down": mag_down,
        "mean": statistics.mean(values),
        "std": statistics.stdev(values) if len(values) > 1 else 0,
        "min": min(values),
        "max": max(values),
    }

def classify_ara(ara_val):
    """Classify ARA on the 0-to-2 spectrum."""
    if ara_val < 0.85:
        return "CONSUMER"
    elif ara_val < 1.15:
        return "SHOCK ABSORBER"
    elif ara_val < 1.5:
        return "WARM ENGINE"
    elif ara_val < 1.85:
        return "φ-ENGINE"
    else:
        return "PURE ENGINE"

def print_ara(result):
    if result is None:
        print("  [insufficient data]")
        return
    d = result["discrete_ara"]
    c = result["continuous_ara"]
    print(f"  {result['label']}:")
    print(f"    N={result['n']}, mean={result['mean']:.2f}, std={result['std']:.2f}, "
          f"range=[{result['min']:.1f}, {result['max']:.1f}]")
    print(f"    Ups={result['ups']}, Downs={result['downs']}, Flats={result['flats']}")
    print(f"    Discrete ARA  = {d:.4f}  [{classify_ara(d)}]")
    print(f"    Continuous ARA = {c:.4f}  [{classify_ara(c)}]")

# ─── PART 2: PRIMARY WAVE — HRV & RESTING HR ARA ─────────────────────────
print("\n" + "=" * 72)
print("PART 2: PRIMARY WAVE — HRV & RESTING HR")
print("=" * 72)

# Extract time series for key measurements
def extract_series(tracker_name):
    """Extract sorted (date, value) pairs for a tracker."""
    pairs = []
    for d in dates_sorted:
        if tracker_name in data[d]:
            pairs.append((d, data[d][tracker_name]))
    return pairs

hrv_series = extract_series("HRV")
hr_series = extract_series("Resting HR")
sleep_series = extract_series("Sleep")
stability_series = extract_series("Stability Score")

print(f"\nHRV: {len(hrv_series)} readings")
print(f"Resting HR: {len(hr_series)} readings")
print(f"Sleep: {len(sleep_series)} readings")
print(f"Stability Score: {len(stability_series)} readings")

# Full-series ARA
for name, series in [("HRV", hrv_series), ("Resting HR", hr_series),
                     ("Sleep", sleep_series), ("Stability Score", stability_series)]:
    vals = [v for _, v in series]
    result = compute_ara(vals, name)
    print_ara(result)

# HRV and HR are coupled — when HRV goes up, HR should go down (parasympathetic)
# Check coupling
print("\n--- HRV ↔ Resting HR Coupling ---")
shared_dates = set(d for d, _ in hrv_series) & set(d for d, _ in hr_series)
shared_sorted = sorted(shared_dates)
hrv_shared = [data[d]["HRV"] for d in shared_sorted]
hr_shared = [data[d]["Resting HR"] for d in shared_sorted]

if len(hrv_shared) > 5:
    # Correlation
    n = len(hrv_shared)
    mean_h = statistics.mean(hrv_shared)
    mean_r = statistics.mean(hr_shared)
    cov = sum((hrv_shared[i] - mean_h) * (hr_shared[i] - mean_r) for i in range(n)) / n
    std_h = statistics.stdev(hrv_shared)
    std_r = statistics.stdev(hr_shared)
    corr = cov / (std_h * std_r) if std_h > 0 and std_r > 0 else 0
    print(f"  Shared dates: {n}")
    print(f"  Pearson correlation: {corr:.4f}")
    print(f"  {'Anti-correlated (expected — parasympathetic coupling)' if corr < -0.3 else 'Weak coupling' if abs(corr) < 0.3 else 'Positively correlated (unexpected)'}")

    # Coupled ARA: when HRV goes up AND HR goes down = coherent oscillation
    coherent = 0
    incoherent = 0
    for i in range(len(shared_sorted) - 1):
        d_hrv = hrv_shared[i+1] - hrv_shared[i]
        d_hr = hr_shared[i+1] - hr_shared[i]
        if d_hrv == 0 or d_hr == 0:
            continue
        if (d_hrv > 0 and d_hr < 0) or (d_hrv < 0 and d_hr > 0):
            coherent += 1
        else:
            incoherent += 1

    coupling_ratio = coherent / incoherent if incoherent > 0 else float('inf')
    print(f"  Coherent moves (HRV↑HR↓ or HRV↓HR↑): {coherent}")
    print(f"  Incoherent moves: {incoherent}")
    print(f"  Coupling ARA: {coupling_ratio:.4f}")
    print(f"  [{classify_ara(coupling_ratio)}]")

# ─── PART 3: THREE-PHASE DECOMPOSITION ───────────────────────────────────
print("\n" + "=" * 72)
print("PART 3: THREE-PHASE DECOMPOSITION — Body as ARA System")
print("=" * 72)
print("Like integers (composites=accumulate, primes=release, transition=coupling),")
print("the body has phases: accumulation (building stress), release (crash/recovery),")
print("and transition (stable oscillation).")

# Use HRV as the primary oscillator
# Phase classification based on HRV trajectory
hrv_vals = [v for _, v in hrv_series]
hrv_dates = [d for d, _ in hrv_series]

if len(hrv_vals) > 10:
    # Rolling mean (5-day window, or whatever we have)
    window = 5
    phases = []

    for i in range(len(hrv_vals)):
        start = max(0, i - window + 1)
        local_mean = statistics.mean(hrv_vals[start:i+1])

        if i == 0:
            phases.append("TRANSITION")
            continue

        trend = hrv_vals[i] - local_mean
        momentum = hrv_vals[i] - hrv_vals[i-1]

        if momentum < -3 and trend < 0:
            phases.append("RELEASE")     # HRV dropping = autonomic stress release / crash
        elif momentum > 3 and trend > 0:
            phases.append("ACCUMULATE")  # HRV rising = parasympathetic recovery / energy building
        else:
            phases.append("TRANSITION")  # oscillating near mean

    phase_counts = Counter(phases)
    total_phases = len(phases)
    print(f"\nPhase distribution (HRV-based, {total_phases} observations):")
    for phase in ["ACCUMULATE", "RELEASE", "TRANSITION"]:
        c = phase_counts.get(phase, 0)
        pct = 100 * c / total_phases
        print(f"  {phase}: {c} ({pct:.1f}%)")

    # ARA within each phase
    for phase_name in ["ACCUMULATE", "RELEASE", "TRANSITION"]:
        phase_vals = [hrv_vals[i] for i in range(len(hrv_vals)) if phases[i] == phase_name]
        if len(phase_vals) >= 5:
            r = compute_ara(phase_vals, f"HRV during {phase_name}")
            print_ara(r)

    # Cycle ARA: accumulate magnitude vs release magnitude
    acc_mags = [abs(hrv_vals[i] - hrv_vals[i-1]) for i in range(1, len(hrv_vals)) if phases[i] == "ACCUMULATE"]
    rel_mags = [abs(hrv_vals[i] - hrv_vals[i-1]) for i in range(1, len(hrv_vals)) if phases[i] == "RELEASE"]

    if acc_mags and rel_mags:
        total_acc = sum(acc_mags)
        total_rel = sum(rel_mags)
        cycle_ara = total_acc / total_rel if total_rel > 0 else float('inf')
        print(f"\n  Cycle ARA (accumulation/release magnitude): {cycle_ara:.4f} [{classify_ara(cycle_ara)}]")

# ─── PART 4: CRASH ANALYSIS — SINGULARITY EVENTS ─────────────────────────
print("\n" + "=" * 72)
print("PART 4: CRASH ANALYSIS — Singularity Events")
print("=" * 72)

crash_series = extract_series("Crash")
crash_dates = [d for d, v in crash_series if v > 0]  # days where crash > 0
crash_all = [(d, v) for d, v in crash_series]

print(f"Total crash tracker entries: {len(crash_series)}")
print(f"Days with crash > 0: {len(crash_dates)}")
if crash_series:
    crash_vals = [v for _, v in crash_series]
    crash_rate = sum(1 for v in crash_vals if v > 0) / len(crash_vals) if crash_vals else 0
    print(f"Crash rate: {crash_rate*100:.1f}%")

    # Crash severity distribution
    sev_counts = Counter(int(v) for _, v in crash_series)
    print(f"Severity distribution: {dict(sorted(sev_counts.items()))}")

# What does HRV look like around crashes?
print("\n--- HRV Around Crash Events ---")
hrv_dict = {d: v for d, v in hrv_series}

# For each crash day, look at HRV window
crash_windows_hrv = []
crash_windows_hr = []
hr_dict = {d: v for d, v in hr_series}

for crash_d in crash_dates:
    cd = datetime.strptime(crash_d, "%Y-%m-%d")
    window_hrv = []
    window_hr = []
    for offset in range(-3, 4):  # 3 days before to 3 days after
        check_d = (cd + timedelta(days=offset)).strftime("%Y-%m-%d")
        if check_d in hrv_dict:
            window_hrv.append((offset, hrv_dict[check_d]))
        if check_d in hr_dict:
            window_hr.append((offset, hr_dict[check_d]))
    if window_hrv:
        crash_windows_hrv.append(window_hrv)
    if window_hr:
        crash_windows_hr.append(window_hr)

if crash_windows_hrv:
    print(f"  Crash events with HRV data: {len(crash_windows_hrv)}")
    # Average HRV at each offset
    offset_hrv = defaultdict(list)
    offset_hr = defaultdict(list)
    for window in crash_windows_hrv:
        for off, val in window:
            offset_hrv[off].append(val)
    for window in crash_windows_hr:
        for off, val in window:
            offset_hr[off].append(val)

    print("  Average HRV around crashes:")
    for off in sorted(offset_hrv.keys()):
        vals = offset_hrv[off]
        avg = statistics.mean(vals)
        label = "← CRASH DAY" if off == 0 else ""
        print(f"    Day {off:+d}: HRV={avg:.1f} (n={len(vals)}) {label}")

    if offset_hr:
        print("  Average Resting HR around crashes:")
        for off in sorted(offset_hr.keys()):
            vals = offset_hr[off]
            avg = statistics.mean(vals)
            label = "← CRASH DAY" if off == 0 else ""
            print(f"    Day {off:+d}: HR={avg:.1f} (n={len(vals)}) {label}")

# Crash as ARA event: does crash "reset" the HRV trajectory?
# Compare ARA before crash vs after crash
print("\n--- Pre-crash vs Post-crash ARA ---")
pre_crash_segments = []
post_crash_segments = []

for crash_d in crash_dates:
    cd = datetime.strptime(crash_d, "%Y-%m-%d")
    pre = []
    post = []
    for d_str, v in hrv_series:
        d = datetime.strptime(d_str, "%Y-%m-%d")
        diff_days = (d - cd).days
        if -14 <= diff_days < 0:
            pre.append(v)
        elif 0 < diff_days <= 14:
            post.append(v)
    if len(pre) >= 3:
        pre_crash_segments.append(pre)
    if len(post) >= 3:
        post_crash_segments.append(post)

if pre_crash_segments:
    all_pre = [v for seg in pre_crash_segments for v in seg]
    all_post = [v for seg in post_crash_segments for v in seg]
    r_pre = compute_ara(all_pre, "Pre-crash HRV (14 days before)")
    r_post = compute_ara(all_post, "Post-crash HRV (14 days after)")
    print_ara(r_pre)
    print_ara(r_post)

# ─── PART 5: SYMPTOM LANDSCAPE ───────────────────────────────────────────
print("\n" + "=" * 72)
print("PART 5: SYMPTOM LANDSCAPE — ARA of Each Symptom")
print("=" * 72)

# Identify symptom trackers (0-2 scale, not measurements or funcap)
symptom_trackers = []
measurement_names = {"HRV", "Resting HR", "Sleep", "Stability Score", "Note"}
funcap_cats = {"Funcap_concentration", "Funcap_walking", "Funcap_upright",
               "Funcap_hygiene", "Funcap_home", "Funcap_communication",
               "Funcap_light", "Funcap_outside"}
experience_names = {"Crash", "Physically active", "Mentally demanding",
                    "Socially demanding", "Emotionally stressful"}

# Get categories for each tracker
tracker_cat = {}
for r in rows:
    tracker_cat[r["tracker_name"]] = r["tracker_category"]

for t in tracker_counts:
    cat = tracker_cat.get(t, "")
    if t not in measurement_names and cat not in funcap_cats and tracker_counts[t] >= 10:
        symptom_trackers.append(t)

# Sort by category for display
symptom_trackers.sort(key=lambda t: (tracker_cat.get(t, ""), t))

symptom_aras = []
print(f"\nSymptom ARA (discrete) — {len(symptom_trackers)} trackers:")
print(f"{'Tracker':<45} {'Cat':<20} {'N':>4} {'Mean':>5} {'ARA':>7} {'Class':<15}")
print("-" * 100)

for t in symptom_trackers:
    series = extract_series(t)
    vals = [v for _, v in series]
    if len(vals) < 5:
        continue
    r = compute_ara(vals, t)
    if r and r["discrete_ara"] != float('inf'):
        cat = tracker_cat.get(t, "?")
        cls = classify_ara(r["discrete_ara"])
        print(f"  {t[:43]:<45} {cat[:18]:<20} {r['n']:>4} {r['mean']:>5.2f} {r['discrete_ara']:>7.4f} {cls}")
        symptom_aras.append((t, r))

# Summary statistics
if symptom_aras:
    all_discrete = [r["discrete_ara"] for _, r in symptom_aras]
    print(f"\nSymptom ARA landscape summary:")
    print(f"  Mean ARA: {statistics.mean(all_discrete):.4f}")
    print(f"  Std ARA:  {statistics.stdev(all_discrete):.4f}")
    print(f"  Min ARA:  {min(all_discrete):.4f} ({[t for t, r in symptom_aras if r['discrete_ara'] == min(all_discrete)][0]})")
    print(f"  Max ARA:  {max(all_discrete):.4f} ({[t for t, r in symptom_aras if r['discrete_ara'] == max(all_discrete)][0]})")

    # Classification distribution
    cls_dist = Counter(classify_ara(a) for a in all_discrete)
    print(f"  Classification distribution: {dict(cls_dist)}")

# ─── PART 6: SYMPTOM BURDEN & TOTAL LOAD ─────────────────────────────────
print("\n" + "=" * 72)
print("PART 6: TOTAL SYMPTOM BURDEN — Daily Load as Time Series")
print("=" * 72)

# For each date, sum all symptom scores = total burden
symptom_names_only = [t for t in symptom_trackers if t not in experience_names
                      and tracker_cat.get(t, "") not in funcap_cats]

daily_burden = []
for d in dates_sorted:
    total = 0
    count = 0
    for t in symptom_names_only:
        if t in data[d]:
            total += data[d][t]
            count += 1
    if count >= 10:  # Only days with substantial symptom reporting
        daily_burden.append((d, total, count))

if daily_burden:
    burden_vals = [b for _, b, _ in daily_burden]
    burden_dates = [d for d, _, _ in daily_burden]
    print(f"Days with ≥10 symptoms reported: {len(daily_burden)}")
    print(f"Burden range: {min(burden_vals):.0f} to {max(burden_vals):.0f}")
    print(f"Mean burden: {statistics.mean(burden_vals):.1f}")

    r = compute_ara(burden_vals, "Total symptom burden")
    print_ara(r)

    # Burden around crashes
    if crash_dates:
        print("\n--- Symptom Burden Around Crashes ---")
        burden_dict = {d: b for d, b, _ in daily_burden}
        offset_burden = defaultdict(list)
        for crash_d in crash_dates:
            cd = datetime.strptime(crash_d, "%Y-%m-%d")
            for offset in range(-3, 4):
                check_d = (cd + timedelta(days=offset)).strftime("%Y-%m-%d")
                if check_d in burden_dict:
                    offset_burden[offset].append(burden_dict[check_d])

        for off in sorted(offset_burden.keys()):
            vals = offset_burden[off]
            avg = statistics.mean(vals)
            label = "← CRASH DAY" if off == 0 else ""
            print(f"  Day {off:+d}: burden={avg:.1f} (n={len(vals)}) {label}")

# ─── PART 7: FUNCTIONAL CAPACITY ARA ─────────────────────────────────────
print("\n" + "=" * 72)
print("PART 7: FUNCTIONAL CAPACITY — What Can the Body Actually Do?")
print("=" * 72)

# Group funcap by category
funcap_items = defaultdict(list)
for r_row in rows:
    cat = r_row["tracker_category"]
    if cat.startswith("Funcap_"):
        try:
            val = float(r_row["observation_value"])
            funcap_items[cat].append((r_row["observation_date"], r_row["tracker_name"], val))
        except ValueError:
            pass

# Per-category average over time
funcap_by_date = defaultdict(lambda: defaultdict(list))
for cat, items in funcap_items.items():
    for d, name, val in items:
        funcap_by_date[cat][d].append(val)

print(f"Functional capacity categories: {len(funcap_items)}")
for cat in sorted(funcap_items.keys()):
    # Get average score per assessment date
    date_avgs = []
    for d in sorted(funcap_by_date[cat].keys()):
        avg = statistics.mean(funcap_by_date[cat][d])
        date_avgs.append((d, avg))

    vals = [v for _, v in date_avgs]
    if len(vals) >= 3:
        r = compute_ara(vals, f"{cat} (avg score, 1-5)")
        print_ara(r)

# Overall functional capacity per assessment
funcap_overall_by_date = defaultdict(list)
for cat, date_items in funcap_by_date.items():
    for d, vals in date_items.items():
        funcap_overall_by_date[d].extend(vals)

if funcap_overall_by_date:
    overall_dates = sorted(funcap_overall_by_date.keys())
    overall_vals = [statistics.mean(funcap_overall_by_date[d]) for d in overall_dates]
    r = compute_ara(overall_vals, "Overall Functional Capacity (mean of all)")
    print_ara(r)

# ─── PART 8: φ-POWER PERIODICITIES ───────────────────────────────────────
print("\n" + "=" * 72)
print("PART 8: φ-POWER PERIODICITIES IN HEALTH DATA")
print("=" * 72)

def autocorrelation_at_lag(values, lag):
    """Compute autocorrelation at a specific lag."""
    n = len(values)
    if lag >= n:
        return 0
    mean = statistics.mean(values)
    var = statistics.variance(values) if len(values) > 1 else 1
    if var == 0:
        return 0
    cov = sum((values[i] - mean) * (values[i + lag] - mean) for i in range(n - lag)) / (n - lag)
    return cov / var

print("\nAutocorrelation at φ-power lags (days):")
print(f"{'Lag (φ^k)':>12} {'Days':>6} {'HRV r':>8} {'HR r':>8} {'Burden r':>10}")
print("-" * 50)

hrv_vals_full = [v for _, v in hrv_series]
hr_vals_full = [v for _, v in hr_series]
burden_vals_full = [b for _, b, _ in daily_burden] if daily_burden else []

for k in range(1, 9):
    phi_lag = round(PHI ** k)
    if phi_lag >= len(hrv_vals_full):
        break

    ac_hrv = autocorrelation_at_lag(hrv_vals_full, phi_lag) if phi_lag < len(hrv_vals_full) else None
    ac_hr = autocorrelation_at_lag(hr_vals_full, phi_lag) if phi_lag < len(hr_vals_full) else None
    ac_burden = autocorrelation_at_lag(burden_vals_full, phi_lag) if burden_vals_full and phi_lag < len(burden_vals_full) else None

    hrv_s = f"{ac_hrv:>8.4f}" if ac_hrv is not None else "     N/A"
    hr_s = f"{ac_hr:>8.4f}" if ac_hr is not None else "     N/A"
    bur_s = f"{ac_burden:>10.4f}" if ac_burden is not None else "       N/A"

    print(f"  φ^{k} = {phi_lag:>4}d   {hrv_s}  {hr_s}  {bur_s}")

# Compare: autocorrelation at NON-φ lags (simple integers)
print("\nComparison: autocorrelation at integer lags:")
print(f"{'Lag':>12} {'Days':>6} {'HRV r':>8} {'HR r':>8}")
print("-" * 40)
for lag in [1, 2, 3, 5, 7, 10, 14, 21, 30, 60, 90]:
    if lag >= len(hrv_vals_full):
        break
    ac_hrv = autocorrelation_at_lag(hrv_vals_full, lag)
    ac_hr = autocorrelation_at_lag(hr_vals_full, lag) if lag < len(hr_vals_full) else None
    hr_s = f"{ac_hr:>8.4f}" if ac_hr is not None else "     N/A"
    print(f"  {lag:>10}d   {ac_hrv:>8.4f}  {hr_s}")

# ─── PART 9: φ-MODULAR TRANSFORM (same as BL14/BL16) ─────────────────────
print("\n" + "=" * 72)
print("PART 9: φ-MODULAR TRANSFORM ON HEALTH DATA")
print("=" * 72)

def phi_modular_uniformity(values):
    """Test if φ*value mod 1 is more/less uniform than original."""
    if len(values) < 10:
        return None

    # Original: map values to [0,1] via rank
    n = len(values)
    ranked = sorted(range(n), key=lambda i: values[i])
    rank_mapped = [0.0] * n
    for rank_pos, idx in enumerate(ranked):
        rank_mapped[idx] = rank_pos / (n - 1)

    # φ-modular: (φ * value) mod 1
    phi_mapped = [(PHI * v) % 1.0 for v in values]

    # Chi-square test against uniform (10 bins)
    def chi_sq(mapped_vals):
        bins = [0] * 10
        for v in mapped_vals:
            b = min(int(v * 10), 9)
            bins[b] += 1
        expected = len(mapped_vals) / 10
        return sum((b - expected)**2 / expected for b in bins)

    chi_rank = chi_sq(rank_mapped)
    chi_phi = chi_sq(phi_mapped)

    # Raw values too
    v_min, v_max = min(values), max(values)
    if v_max > v_min:
        raw_mapped = [(v - v_min) / (v_max - v_min) for v in values]
        chi_raw = chi_sq(raw_mapped)
        phi_raw_mapped = [(PHI * v) % 1.0 for v in raw_mapped]
        chi_phi_raw = chi_sq(phi_raw_mapped)
    else:
        chi_raw = 0
        chi_phi_raw = 0

    return {
        "chi_rank": chi_rank,
        "chi_phi_rank": chi_phi,
        "rank_change_pct": 100 * (chi_phi - chi_rank) / max(chi_rank, 0.001),
        "chi_raw": chi_raw,
        "chi_phi_raw": chi_phi_raw,
        "raw_change_pct": 100 * (chi_phi_raw - chi_raw) / max(chi_raw, 0.001) if chi_raw > 0 else 0,
    }

for name, series in [("HRV", hrv_series), ("Resting HR", hr_series)]:
    vals = [v for _, v in series]
    result = phi_modular_uniformity(vals)
    if result:
        print(f"\n  {name}:")
        print(f"    Ranked: φ changes χ² by {result['rank_change_pct']:+.1f}%")
        print(f"    Raw:    φ changes χ² by {result['raw_change_pct']:+.1f}%")
        if result['rank_change_pct'] > 20:
            print(f"    → φ DISRUPTS ranked order (visible structure, like market)")
        elif result['rank_change_pct'] < -20:
            print(f"    → φ DISSOLVES ranked order (hidden structure, like lotto)")
        else:
            print(f"    → φ has modest effect on ranked order")

if burden_vals_full:
    result = phi_modular_uniformity(burden_vals_full)
    if result:
        print(f"\n  Total Symptom Burden:")
        print(f"    Ranked: φ changes χ² by {result['rank_change_pct']:+.1f}%")
        print(f"    Raw:    φ changes χ² by {result['raw_change_pct']:+.1f}%")

# ─── PART 10: BODY ON THE ARA SPECTRUM ────────────────────────────────────
print("\n" + "=" * 72)
print("PART 10: WHERE DOES DYLAN'S BODY SIT ON THE ARA SPECTRUM?")
print("=" * 72)

print("\n  SYSTEM COMPARISON TABLE")
print(f"  {'System':<35} {'ARA':>7} {'Classification':<20}")
print("  " + "-" * 65)

comparisons = [
    ("Lotto numbers (BL14)", 1.0000, "SHOCK ABSORBER"),
    ("Prime gaps (BL16)", 1.0000, "SHOCK ABSORBER"),
    ("π digits (BL16)", 1.0000, "SHOCK ABSORBER"),
]

# Add our measured values
for name, series in [("HRV", hrv_series), ("Resting HR", hr_series)]:
    vals = [v for _, v in series]
    r = compute_ara(vals, name)
    if r:
        comparisons.append((f"Dylan's {name}", r["continuous_ara"], classify_ara(r["continuous_ara"])))

if burden_vals_full:
    r = compute_ara(burden_vals_full, "burden")
    if r:
        comparisons.append(("Dylan's symptom burden", r["continuous_ara"], classify_ara(r["continuous_ara"])))

comparisons.extend([
    ("S&P 500 returns (BL15)", 0.930, "CONSUMER"),
    ("S&P 500 prices (BL15)", 1.390, "WARM ENGINE"),
    ("Fibonacci sequence (BL16)", 2.000, "PURE ENGINE"),
    ("Powers of 2 (BL16)", 2.000, "PURE ENGINE"),
])

comparisons.sort(key=lambda x: x[1])

for name, ara, cls in comparisons:
    marker = "  ◄◄◄" if "Dylan" in name else ""
    print(f"  {name:<35} {ara:>7.4f} {cls:<20}{marker}")

# ─── PART 11: SYMPTOM CLUSTER CORRELATIONS ────────────────────────────────
print("\n" + "=" * 72)
print("PART 11: SYMPTOM CLUSTERS — Which Symptoms Move Together?")
print("=" * 72)

# Build matrix of symptom values per date (only dates with full reporting)
symptom_matrix_names = []
symptom_matrix_dates = []
symptom_matrix = []

# Get dates where most symptoms are reported
full_report_dates = []
for d in dates_sorted:
    symp_count = sum(1 for t in symptom_names_only if t in data[d])
    if symp_count >= 15:
        full_report_dates.append(d)

if len(full_report_dates) >= 10:
    # Find symptoms present on most of these dates
    for t in symptom_names_only:
        present = sum(1 for d in full_report_dates if t in data[d])
        if present >= len(full_report_dates) * 0.8:
            symptom_matrix_names.append(t)

    # Build matrix
    for d in full_report_dates:
        row = []
        valid = True
        for t in symptom_matrix_names:
            if t in data[d]:
                row.append(data[d][t])
            else:
                valid = False
                break
        if valid:
            symptom_matrix.append(row)
            symptom_matrix_dates.append(d)

    print(f"Symptom matrix: {len(symptom_matrix)} days × {len(symptom_matrix_names)} symptoms")

    # Pairwise correlations
    n_symp = len(symptom_matrix_names)
    n_days = len(symptom_matrix)

    if n_days >= 10 and n_symp >= 5:
        # Compute correlation matrix
        corr_pairs = []
        for i in range(n_symp):
            for j in range(i+1, n_symp):
                vals_i = [symptom_matrix[d][i] for d in range(n_days)]
                vals_j = [symptom_matrix[d][j] for d in range(n_days)]
                mean_i = statistics.mean(vals_i)
                mean_j = statistics.mean(vals_j)
                std_i = statistics.stdev(vals_i) if len(set(vals_i)) > 1 else 0
                std_j = statistics.stdev(vals_j) if len(set(vals_j)) > 1 else 0
                if std_i > 0 and std_j > 0:
                    cov = sum((vals_i[k] - mean_i) * (vals_j[k] - mean_j) for k in range(n_days)) / n_days
                    corr = cov / (std_i * std_j)
                    corr_pairs.append((corr, symptom_matrix_names[i], symptom_matrix_names[j]))

        corr_pairs.sort(key=lambda x: -abs(x[0]))

        print(f"\nTop 15 strongest symptom correlations:")
        for corr, t1, t2 in corr_pairs[:15]:
            cat1 = tracker_cat.get(t1, "?")[:12]
            cat2 = tracker_cat.get(t2, "?")[:12]
            direction = "↑↑" if corr > 0 else "↑↓"
            print(f"  {corr:+.3f} {direction}  {t1[:25]:<25} ({cat1}) × {t2[:25]:<25} ({cat2})")

        print(f"\nTop 5 anti-correlations:")
        anti = [p for p in corr_pairs if p[0] < 0]
        for corr, t1, t2 in anti[:5]:
            print(f"  {corr:+.3f}  {t1[:30]:<30} × {t2[:30]}")

# ─── PART 12: HRV → SYMPTOM REGIME MAPPING ───────────────────────────────
print("\n" + "=" * 72)
print("PART 12: HRV REGIME → SYMPTOM MAPPING")
print("=" * 72)

# Split HRV into terciles (low/med/high) and compare symptom burden
if hrv_series and daily_burden:
    hrv_dict_full = {d: v for d, v in hrv_series}
    burden_dict_full = {d: b for d, b, _ in daily_burden}

    # Match dates
    matched = [(hrv_dict_full[d], burden_dict_full[d]) for d in hrv_dict_full if d in burden_dict_full]

    if len(matched) >= 15:
        matched.sort(key=lambda x: x[0])
        n = len(matched)
        tercile_size = n // 3

        low_hrv = matched[:tercile_size]
        mid_hrv = matched[tercile_size:2*tercile_size]
        high_hrv = matched[2*tercile_size:]

        print(f"\nHRV tercile analysis ({n} matched days):")
        for label, group in [("LOW HRV", low_hrv), ("MID HRV", mid_hrv), ("HIGH HRV", high_hrv)]:
            hrv_vals_g = [h for h, _ in group]
            burden_vals_g = [b for _, b in group]
            print(f"  {label}: HRV {min(hrv_vals_g):.0f}-{max(hrv_vals_g):.0f}, "
                  f"Mean burden={statistics.mean(burden_vals_g):.1f}, "
                  f"Burden std={statistics.stdev(burden_vals_g):.1f}")

        # Is there a threshold?
        low_burden = statistics.mean([b for _, b in low_hrv])
        high_burden = statistics.mean([b for _, b in high_hrv])
        ratio = low_burden / high_burden if high_burden > 0 else float('inf')
        print(f"\n  Low-HRV / High-HRV burden ratio: {ratio:.2f}")
        print(f"  {'Higher HRV → lower symptoms (expected)' if ratio > 1.1 else 'No clear relationship' if 0.9 < ratio < 1.1 else 'Higher HRV → higher symptoms (unexpected)'}")

# ─── PART 13: TEMPORAL TRENDS — IS THE BODY GETTING BETTER OR WORSE? ─────
print("\n" + "=" * 72)
print("PART 13: TEMPORAL TRENDS — Trajectory Over Time")
print("=" * 72)

def linear_trend(values):
    """Simple linear regression: returns slope per observation."""
    n = len(values)
    if n < 5:
        return None
    x_mean = (n - 1) / 2
    y_mean = statistics.mean(values)
    num = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
    den = sum((i - x_mean)**2 for i in range(n))
    return num / den if den > 0 else 0

for name, series in [("HRV", hrv_series), ("Resting HR", hr_series)]:
    vals = [v for _, v in series]
    slope = linear_trend(vals)
    if slope is not None:
        total_change = slope * len(vals)
        print(f"  {name}: slope = {slope:+.4f}/day, total change over period: {total_change:+.1f}")
        if name == "HRV":
            print(f"    {'↑ HRV trending UP (improving)' if slope > 0.01 else '↓ HRV trending DOWN (declining)' if slope < -0.01 else '→ HRV stable'}")
        else:
            print(f"    {'↓ HR trending DOWN (improving)' if slope < -0.01 else '↑ HR trending UP (declining)' if slope > 0.01 else '→ HR stable'}")

if burden_vals_full:
    slope = linear_trend(burden_vals_full)
    if slope is not None:
        total_change = slope * len(burden_vals_full)
        print(f"  Symptom burden: slope = {slope:+.4f}/day, total change: {total_change:+.1f}")

# ─── PART 14: SUMMARY ────────────────────────────────────────────────────
print("\n" + "=" * 72)
print("PART 14: SUMMARY — Dylan's Body as an ARA System")
print("=" * 72)

# Collect all key findings
print("""
This analysis treats Dylan's ME/CFS body as an ARA system:
  - HRV and Resting HR are the primary oscillators (the wave)
  - Symptoms are the landscape (what the wave produces)
  - Crashes are potential singularity events (phase transitions)
  - Functional capacity is the output (what the system can do)

Key questions answered:
  1. What is the body's ARA? → See Part 2 (primary wave)
  2. Is there a three-phase cycle? → See Part 3
  3. Are crashes singularity events? → See Part 4
  4. Which symptoms are consumers/engines? → See Part 5
  5. Does φ appear in health cycles? → See Parts 8-9
  6. Where on the spectrum vs lotto/markets/primes? → See Part 10
  7. What moves together? → See Part 11
  8. Does HRV predict symptom load? → See Part 12
  9. Is the body improving or declining? → See Part 13
""")

print("Script complete.")

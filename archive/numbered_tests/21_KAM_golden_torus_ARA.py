"""
KAM THEORY TEST: Does the Golden Mean Torus Have ARA = φ?

The Standard Map (Chirikov-Taylor map):
    p_{n+1} = p_n + (K / 2π) * sin(2π * θ_n)
    θ_{n+1} = θ_n + p_{n+1}          (mod 1)

KAM theory: as perturbation K increases, invariant tori break.
The LAST torus to survive has winding number = 1/φ (the golden ratio).
This is the "golden mean torus" — the most stable orbit in Hamiltonian mechanics.
It breaks at K_c ≈ 0.9716 (Greene's result, 1979).

TEST: For orbits on the golden mean torus, project onto one coordinate
and measure the temporal asymmetry:
    T_acc = time spent with coordinate increasing
    T_rel = time spent with coordinate decreasing
    ARA = T_acc / T_rel

If ARA ≈ φ for the golden torus, then the most stable orbit in
nonlinear dynamics LITERALLY has the golden ratio temporal asymmetry.
That would derive ARA = φ from Hamiltonian mechanics.
"""
import math

phi = (1 + math.sqrt(5)) / 2
golden_winding = 1.0 / phi  # ≈ 0.6180339...

# ================================================================
# THE STANDARD MAP
# ================================================================

def standard_map(theta, p, K, n_steps):
    """Iterate the standard map n_steps times.
    Returns lists of (theta, p) values."""
    thetas = [theta]
    ps = [p]
    for _ in range(n_steps):
        p_new = p + (K / (2 * math.pi)) * math.sin(2 * math.pi * theta)
        theta_new = (theta + p_new) % 1.0
        p = p_new
        theta = theta_new
        thetas.append(theta)
        ps.append(p)
    return thetas, ps

# ================================================================
# STEP 1: FIND THE GOLDEN MEAN TORUS
# ================================================================

print("=" * 90)
print("STEP 1: LOCATING THE GOLDEN MEAN TORUS")
print("=" * 90)
print()

# The golden mean torus has winding number ω = 1/φ ≈ 0.618034
# At K=0, all tori exist. The p-value gives the winding number directly.
# At K>0, the torus shifts but maintains its winding number until it breaks.

# For a given K, we find the initial p that gives winding number ≈ 1/φ
# by tracking the average rotation: ω = lim (θ_N - θ_0) / N

def measure_winding(theta0, p0, K, n_steps=10000):
    """Measure the winding number of an orbit."""
    theta = theta0
    p = p0
    total_advance = 0.0
    for _ in range(n_steps):
        p_new = p + (K / (2 * math.pi)) * math.sin(2 * math.pi * theta)
        theta_new = theta + p_new
        total_advance += (theta_new - theta)
        theta = theta_new % 1.0
        p = p_new
    return total_advance / n_steps

def find_golden_torus_p(K, p_guess=None, tol=1e-10, n_steps=50000):
    """Binary search for the p-value that gives winding number 1/φ."""
    target = golden_winding
    if p_guess is None:
        p_lo, p_hi = 0.0, 1.0
    else:
        p_lo = p_guess - 0.1
        p_hi = p_guess + 0.1

    # Make sure the target is bracketed
    w_lo = measure_winding(0.0, p_lo, K, n_steps)
    w_hi = measure_winding(0.0, p_hi, K, n_steps)

    if w_lo > w_hi:
        p_lo, p_hi = p_hi, p_lo
        w_lo, w_hi = w_hi, w_lo

    for _ in range(100):
        p_mid = (p_lo + p_hi) / 2
        w_mid = measure_winding(0.0, p_mid, K, n_steps)
        if abs(w_mid - target) < tol:
            return p_mid, w_mid
        if w_mid < target:
            p_lo = p_mid
        else:
            p_hi = p_mid

    return (p_lo + p_hi) / 2, measure_winding(0.0, (p_lo + p_hi) / 2, K, n_steps)

print(f"  Golden winding number target: ω = 1/φ = {golden_winding:.10f}")
print()

# Test at several K values from weak to near-critical
K_values = [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.95, 0.97]

print(f"  {'K':>6}  {'p₀':>12}  {'Measured ω':>14}  {'Error':>12}  {'Torus status'}")
print("  " + "-" * 70)

golden_p_values = {}
for K in K_values:
    p0, omega = find_golden_torus_p(K, p_guess=golden_winding)
    error = abs(omega - golden_winding)
    status = "INTACT" if error < 1e-4 else "BROKEN?"
    golden_p_values[K] = (p0, omega, status)
    print(f"  {K:>6.2f}  {p0:>12.8f}  {omega:>14.10f}  {error:>12.2e}  {status}")

# ================================================================
# STEP 2: MEASURE TEMPORAL ASYMMETRY ON THE GOLDEN TORUS
# ================================================================

print()
print("=" * 90)
print("STEP 2: TEMPORAL ASYMMETRY OF THE GOLDEN MEAN TORUS")
print("=" * 90)
print()

def measure_temporal_asymmetry(theta0, p0, K, n_steps=100000):
    """
    Track the orbit and measure temporal asymmetry in both θ and p.

    For the θ coordinate:
      T_rising = number of steps where θ increases (Δθ > 0)
      T_falling = number of steps where θ decreases (Δθ < 0)
      ARA_theta = T_rising / T_falling  (or max/min for canonical form)

    For the p coordinate:
      T_rising = number of steps where p increases (Δp > 0)
      T_falling = number of steps where p decreases (Δp < 0)
      ARA_p = max(T_rising, T_falling) / min(T_rising, T_falling)

    Also measure using CONTINUOUS segments (not individual steps):
      A "rising segment" is a contiguous run of positive Δθ steps.
      A "falling segment" is a contiguous run of negative Δθ steps.
    """
    theta = theta0
    p = p0

    # Step-by-step counts
    theta_rising = 0
    theta_falling = 0
    p_rising = 0
    p_falling = 0

    # Segment tracking for θ
    segments_rising = []  # durations of rising segments
    segments_falling = []  # durations of falling segments
    current_direction = None  # 'up' or 'down'
    current_length = 0

    # Also track unwrapped θ for continuous measurement
    theta_unwrapped = theta0
    prev_theta_unwrapped = theta0

    # Phase-space trajectory for waveform analysis
    theta_series = [theta0]
    p_series = [p0]

    for i in range(n_steps):
        p_new = p + (K / (2 * math.pi)) * math.sin(2 * math.pi * theta)
        theta_new_unwrapped = theta + p_new  # unwrapped
        theta_new = theta_new_unwrapped % 1.0

        # θ direction (using unwrapped to avoid mod discontinuities)
        d_theta = theta_new_unwrapped - (theta_unwrapped if i > 0 else theta0)
        # Actually let's use the raw advance
        d_theta = p_new  # the advance in θ is exactly p_new

        if d_theta > 0:
            theta_rising += 1
            if current_direction == 'up':
                current_length += 1
            else:
                if current_direction == 'down' and current_length > 0:
                    segments_falling.append(current_length)
                current_direction = 'up'
                current_length = 1
        elif d_theta < 0:
            theta_falling += 1
            if current_direction == 'down':
                current_length += 1
            else:
                if current_direction == 'up' and current_length > 0:
                    segments_rising.append(current_length)
                current_direction = 'down'
                current_length = 1

        # p direction
        dp = p_new - p
        if dp > 0:
            p_rising += 1
        elif dp < 0:
            p_falling += 1

        theta_unwrapped += p_new
        theta = theta_new
        p = p_new

        if i < 10000:  # store first portion for waveform analysis
            theta_series.append(theta_new)
            p_series.append(p_new)

    # Close final segment
    if current_direction == 'up' and current_length > 0:
        segments_rising.append(current_length)
    elif current_direction == 'down' and current_length > 0:
        segments_falling.append(current_length)

    return {
        'theta_rising': theta_rising,
        'theta_falling': theta_falling,
        'p_rising': p_rising,
        'p_falling': p_falling,
        'segments_rising': segments_rising,
        'segments_falling': segments_falling,
        'theta_series': theta_series,
        'p_series': p_series,
    }

print("  Measuring temporal asymmetry for golden mean torus at each K:")
print()
print(f"  {'K':>6}  {'θ_rise':>8} {'θ_fall':>8} {'ARA_θ':>8}  "
      f"{'p_rise':>8} {'p_fall':>8} {'ARA_p':>8}  {'φ':>6}")
print("  " + "-" * 80)

results_by_K = {}
for K in K_values:
    if K == 0.0:
        # At K=0, the map is a pure rotation — no asymmetry
        print(f"  {K:>6.2f}  {'N/A':>8} {'N/A':>8} {'1.000':>8}  "
              f"{'N/A':>8} {'N/A':>8} {'N/A':>8}  {phi:.4f}")
        continue

    p0, omega, status = golden_p_values[K]
    result = measure_temporal_asymmetry(0.0, p0, K, n_steps=100000)
    results_by_K[K] = result

    # θ ARA
    if result['theta_falling'] > 0:
        ara_theta = result['theta_rising'] / result['theta_falling']
    else:
        ara_theta = float('inf')

    # p ARA (momentum oscillates — this is the "waveform")
    if result['p_falling'] > 0 and result['p_rising'] > 0:
        ara_p_raw = result['p_rising'] / result['p_falling']
        ara_p = max(ara_p_raw, 1/ara_p_raw) if ara_p_raw > 0 else float('inf')
    else:
        ara_p = float('inf')

    print(f"  {K:>6.2f}  {result['theta_rising']:>8d} {result['theta_falling']:>8d} "
          f"{ara_theta:>8.4f}  {result['p_rising']:>8d} {result['p_falling']:>8d} "
          f"{ara_p:>8.4f}  {phi:.4f}")

# ================================================================
# STEP 3: SEGMENT-BASED ARA (contiguous rising/falling runs)
# ================================================================

print()
print("=" * 90)
print("STEP 3: SEGMENT-BASED ANALYSIS (contiguous rising/falling runs)")
print("=" * 90)
print()

print("  Instead of counting individual steps, count CONTIGUOUS SEGMENTS")
print("  where p is monotonically rising or falling. This gives the")
print("  accumulation and release DURATIONS, not just step counts.")
print()

for K in K_values:
    if K == 0.0:
        continue

    result = results_by_K.get(K)
    if result is None:
        continue

    # Re-measure with p-based segments
    p0, omega, status = golden_p_values[K]

    # Run the map and track p segments
    theta = 0.0
    p = p0
    p_segs_up = []
    p_segs_down = []
    curr_dir = None
    curr_len = 0
    prev_p = p

    for _ in range(200000):
        p_new = p + (K / (2 * math.pi)) * math.sin(2 * math.pi * theta)
        theta = (theta + p_new) % 1.0
        dp = p_new - p

        if dp > 0:
            if curr_dir == 'up':
                curr_len += 1
            else:
                if curr_dir == 'down' and curr_len > 0:
                    p_segs_down.append(curr_len)
                curr_dir = 'up'
                curr_len = 1
        elif dp < 0:
            if curr_dir == 'down':
                curr_len += 1
            else:
                if curr_dir == 'up' and curr_len > 0:
                    p_segs_up.append(curr_len)
                curr_dir = 'down'
                curr_len = 1

        p = p_new

    if curr_dir == 'up' and curr_len > 0:
        p_segs_up.append(curr_len)
    elif curr_dir == 'down' and curr_len > 0:
        p_segs_down.append(curr_len)

    if len(p_segs_up) > 0 and len(p_segs_down) > 0:
        avg_up = sum(p_segs_up) / len(p_segs_up)
        avg_down = sum(p_segs_down) / len(p_segs_down)
        seg_ara = max(avg_up, avg_down) / min(avg_up, avg_down)

        # Total time in rising vs falling
        total_up = sum(p_segs_up)
        total_down = sum(p_segs_down)
        time_ara = max(total_up, total_down) / min(total_up, total_down)

        print(f"  K={K:.2f}:")
        print(f"    Rising segments:  {len(p_segs_up):>6d}  avg length: {avg_up:.2f}")
        print(f"    Falling segments: {len(p_segs_down):>6d}  avg length: {avg_down:.2f}")
        print(f"    Segment ARA (avg_long / avg_short): {seg_ara:.4f}")
        print(f"    Time ARA (total_long / total_short): {time_ara:.4f}")
        print(f"    φ = {phi:.4f}  |  Δ from φ = {abs(seg_ara - phi):.4f}")
        print()

# ================================================================
# STEP 4: WINDING NUMBER SCAN — ARA vs frequency ratio
# ================================================================

print()
print("=" * 90)
print("STEP 4: ARA vs WINDING NUMBER (frequency ratio scan)")
print("=" * 90)
print()

print("  Scanning different winding numbers at K=0.5 and K=0.9")
print("  to see how ARA varies with frequency ratio.")
print("  If ARA = φ specifically at the golden winding, that's the proof.")
print()

def quick_ara(theta0, p0, K, n_steps=50000):
    """Quick measurement of p-momentum temporal asymmetry."""
    theta = theta0
    p = p0
    p_up = 0
    p_down = 0
    for _ in range(n_steps):
        p_new = p + (K / (2 * math.pi)) * math.sin(2 * math.pi * theta)
        theta = (theta + p_new) % 1.0
        dp = p_new - p
        if dp > 0:
            p_up += 1
        elif dp < 0:
            p_down += 1
        p = p_new
    if p_up > 0 and p_down > 0:
        return max(p_up, p_down) / min(p_up, p_down)
    return float('inf')

# Scan winding numbers from 0.1 to 0.9
winding_targets = [0.1, 0.2, 0.3, 0.382, 0.4, 0.5, 0.55, 0.6,
                    golden_winding, 0.65, 0.7, 0.75, 0.8, 0.9]

for K_test in [0.5, 0.9]:
    print(f"  K = {K_test}:")
    print(f"  {'Winding ω':>12}  {'ARA_p':>10}  {'Δ from φ':>10}  {'Note'}")
    print("  " + "-" * 55)

    for w_target in sorted(winding_targets):
        # Find p that gives this winding number
        p_lo, p_hi = 0.0, 1.0
        for _ in range(80):
            p_mid = (p_lo + p_hi) / 2
            w_mid = measure_winding(0.0, p_mid, K_test, 20000)
            if w_mid < w_target:
                p_lo = p_mid
            else:
                p_hi = p_mid
        p_found = (p_lo + p_hi) / 2
        w_found = measure_winding(0.0, p_found, K_test, 20000)

        if abs(w_found - w_target) > 0.01:
            # Couldn't find this winding number (torus may be broken)
            note = "BROKEN"
            print(f"  {w_target:>12.6f}  {'---':>10}  {'---':>10}  {note}")
            continue

        ara = quick_ara(0.0, p_found, K_test, 50000)
        delta = abs(ara - phi)
        note = ""
        if abs(w_target - golden_winding) < 0.001:
            note = "◄── GOLDEN TORUS"
        elif abs(w_target - 0.5) < 0.001:
            note = "(1:2 resonance)"
        elif abs(w_target - 1/3) < 0.02:
            note = "(1:3 resonance)"
        elif abs(w_target - 0.382) < 0.002:
            note = "(1/φ² = 1-1/φ)"

        print(f"  {w_found:>12.6f}  {ara:>10.4f}  {delta:>10.4f}  {note}")

    print()

# ================================================================
# STEP 5: PHASE-SPACE WAVEFORM ANALYSIS
# ================================================================

print()
print("=" * 90)
print("STEP 5: PHASE-SPACE WAVEFORM ANALYSIS")
print("=" * 90)
print()

print("  Examining the WAVEFORM SHAPE of the golden torus orbit.")
print("  In a pure rotation (K=0), p is constant — no waveform.")
print("  At K>0, p oscillates. The oscillation has a shape.")
print("  That shape's asymmetry IS the temporal asymmetry we want.")
print()

for K in [0.3, 0.5, 0.7, 0.9, 0.95]:
    p0, omega, status = golden_p_values[K]

    # Track p over many cycles and find the oscillation pattern
    theta = 0.0
    p = p0
    p_values = []

    for _ in range(50000):
        p_new = p + (K / (2 * math.pi)) * math.sin(2 * math.pi * theta)
        theta = (theta + p_new) % 1.0
        p_values.append(p_new)
        p = p_new

    # Compute statistics of p oscillation
    p_mean = sum(p_values) / len(p_values)
    p_min = min(p_values)
    p_max = max(p_values)
    p_range = p_max - p_min

    # Time above vs below mean
    above = sum(1 for pv in p_values if pv > p_mean)
    below = sum(1 for pv in p_values if pv <= p_mean)
    above_below_ratio = above / below if below > 0 else float('inf')

    # Time above vs below median
    p_sorted = sorted(p_values)
    p_median = p_sorted[len(p_sorted) // 2]
    above_med = sum(1 for pv in p_values if pv > p_median)
    below_med = sum(1 for pv in p_values if pv <= p_median)

    # Distribution skewness
    variance = sum((pv - p_mean)**2 for pv in p_values) / len(p_values)
    std = variance**0.5
    if std > 0:
        skewness = sum((pv - p_mean)**3 for pv in p_values) / (len(p_values) * std**3)
    else:
        skewness = 0

    print(f"  K={K:.2f}  (golden torus, ω={omega:.6f}):")
    print(f"    p range: [{p_min:.6f}, {p_max:.6f}], amplitude: {p_range:.6f}")
    print(f"    p mean:  {p_mean:.6f}, median: {p_median:.6f}")
    print(f"    Time above/below mean: {above}/{below} = {above_below_ratio:.4f}")
    print(f"    Skewness: {skewness:.6f}")
    print(f"    φ = {phi:.4f}")
    print()

# ================================================================
# STEP 6: MEASURING ARA AS HALF-CYCLE DURATIONS
# ================================================================

print()
print("=" * 90)
print("STEP 6: HALF-CYCLE DURATION ARA (the direct measurement)")
print("=" * 90)
print()

print("  The most direct ARA measurement: for each oscillation cycle of p,")
print("  measure how long p spends ABOVE its cycle mean vs BELOW it.")
print("  This is T_acc / T_rel for the momentum waveform.")
print()

for K in [0.3, 0.5, 0.7, 0.9, 0.95]:
    p0, omega, status = golden_p_values[K]

    theta = 0.0
    p = p0
    p_values = []

    for _ in range(200000):
        p_new = p + (K / (2 * math.pi)) * math.sin(2 * math.pi * theta)
        theta = (theta + p_new) % 1.0
        p_values.append(p_new)
        p = p_new

    p_mean = sum(p_values) / len(p_values)

    # Find zero crossings (relative to mean)
    half_cycles_above = []
    half_cycles_below = []
    current_above = p_values[0] > p_mean
    current_length = 1

    for i in range(1, len(p_values)):
        is_above = p_values[i] > p_mean
        if is_above == current_above:
            current_length += 1
        else:
            if current_above:
                half_cycles_above.append(current_length)
            else:
                half_cycles_below.append(current_length)
            current_above = is_above
            current_length = 1

    # Close last segment
    if current_above:
        half_cycles_above.append(current_length)
    else:
        half_cycles_below.append(current_length)

    if len(half_cycles_above) > 5 and len(half_cycles_below) > 5:
        # Remove first and last (edge effects)
        half_cycles_above = half_cycles_above[1:-1]
        half_cycles_below = half_cycles_below[1:-1]

        avg_above = sum(half_cycles_above) / len(half_cycles_above)
        avg_below = sum(half_cycles_below) / len(half_cycles_below)

        half_cycle_ara = max(avg_above, avg_below) / min(avg_above, avg_below)
        longer = "above" if avg_above > avg_below else "below"

        # Also compute the distribution of individual half-cycle ARAs
        # by pairing consecutive above/below segments
        n_pairs = min(len(half_cycles_above), len(half_cycles_below))
        pair_aras = []
        for i in range(n_pairs):
            a = half_cycles_above[i]
            b = half_cycles_below[i]
            pair_aras.append(max(a, b) / min(a, b))

        mean_pair_ara = sum(pair_aras) / len(pair_aras) if pair_aras else 0

        print(f"  K={K:.2f}:")
        print(f"    Half-cycles above mean: {len(half_cycles_above):>6d}  avg duration: {avg_above:.2f}")
        print(f"    Half-cycles below mean: {len(half_cycles_below):>6d}  avg duration: {avg_below:.2f}")
        print(f"    Longer phase: {longer}")
        print(f"    HALF-CYCLE ARA: {half_cycle_ara:.6f}")
        print(f"    Mean paired ARA: {mean_pair_ara:.6f}")
        print(f"    φ = {phi:.6f}")
        print(f"    Δ from φ: {abs(half_cycle_ara - phi):.6f}")
        if abs(half_cycle_ara - phi) < 0.05:
            print(f"    *** WITHIN 0.05 OF φ ***")
        elif abs(half_cycle_ara - phi) < 0.1:
            print(f"    ** WITHIN 0.1 OF φ **")
        print()

# ================================================================
# STEP 7: COMPARISON — GOLDEN TORUS vs OTHER TORI
# ================================================================

print()
print("=" * 90)
print("STEP 7: GOLDEN TORUS vs OTHER TORI — ARA COMPARISON")
print("=" * 90)
print()

print("  If ARA = φ is SPECIFIC to the golden torus, other tori should")
print("  have different ARA values. The golden torus should be unique.")
print()

K_test = 0.7  # moderate perturbation where many tori still exist

winding_test = [0.2, 0.3, 0.4, 0.5, golden_winding, 0.7, 0.8]

print(f"  K = {K_test}")
print(f"  {'Winding ω':>12}  {'Half-cycle ARA':>15}  {'Δ from φ':>10}  {'Note'}")
print("  " + "-" * 60)

for w_target in winding_test:
    # Find p
    p_lo, p_hi = 0.0, 1.0
    for _ in range(80):
        p_mid = (p_lo + p_hi) / 2
        w_mid = measure_winding(0.0, p_mid, K_test, 20000)
        if w_mid < w_target:
            p_lo = p_mid
        else:
            p_hi = p_mid
    p_found = (p_lo + p_hi) / 2
    w_found = measure_winding(0.0, p_found, K_test, 20000)

    if abs(w_found - w_target) > 0.01:
        print(f"  {w_target:>12.6f}  {'BROKEN':>15}  {'---':>10}")
        continue

    # Measure half-cycle ARA
    theta = 0.0
    p = p_found
    p_vals = []
    for _ in range(100000):
        p_new = p + (K_test / (2 * math.pi)) * math.sin(2 * math.pi * theta)
        theta = (theta + p_new) % 1.0
        p_vals.append(p_new)
        p = p_new

    p_mean = sum(p_vals) / len(p_vals)
    above_segs = []
    below_segs = []
    curr_above = p_vals[0] > p_mean
    curr_len = 1
    for i in range(1, len(p_vals)):
        if (p_vals[i] > p_mean) == curr_above:
            curr_len += 1
        else:
            if curr_above:
                above_segs.append(curr_len)
            else:
                below_segs.append(curr_len)
            curr_above = p_vals[i] > p_mean
            curr_len = 1
    if curr_above:
        above_segs.append(curr_len)
    else:
        below_segs.append(curr_len)

    if len(above_segs) > 2 and len(below_segs) > 2:
        above_segs = above_segs[1:-1]
        below_segs = below_segs[1:-1]
        avg_a = sum(above_segs) / len(above_segs)
        avg_b = sum(below_segs) / len(below_segs)
        hc_ara = max(avg_a, avg_b) / min(avg_a, avg_b)
        delta = abs(hc_ara - phi)
        note = "◄── GOLDEN TORUS" if abs(w_target - golden_winding) < 0.001 else ""
        print(f"  {w_found:>12.6f}  {hc_ara:>15.6f}  {delta:>10.6f}  {note}")
    else:
        print(f"  {w_found:>12.6f}  {'too few segs':>15}")

# ================================================================
# STEP 8: NEAR-CRITICAL BEHAVIOUR
# ================================================================

print()
print("=" * 90)
print("STEP 8: ARA NEAR THE CRITICAL POINT (K → K_c)")
print("=" * 90)
print()

print("  The golden torus breaks at K_c ≈ 0.9716.")
print("  What happens to ARA as K approaches K_c?")
print("  If ARA → φ at criticality, that's the KAM-ARA bridge.")
print()

K_critical_values = [0.5, 0.7, 0.8, 0.9, 0.93, 0.95, 0.96, 0.97]

print(f"  {'K':>6}  {'K/K_c':>8}  {'Half-cycle ARA':>15}  {'Δ from φ':>10}")
print("  " + "-" * 50)

K_c = 0.9716

for K in K_critical_values:
    p0, omega, status = golden_p_values.get(K, (golden_winding, 0, "?"))
    if status == "?" or K not in golden_p_values:
        # Re-find
        p0, omega = find_golden_torus_p(K, p_guess=golden_winding, n_steps=30000)

    theta = 0.0
    p = p0
    p_vals = []
    for _ in range(200000):
        p_new = p + (K / (2 * math.pi)) * math.sin(2 * math.pi * theta)
        theta = (theta + p_new) % 1.0
        p_vals.append(p_new)
        p = p_new

    p_mean = sum(p_vals) / len(p_vals)
    above_segs = []
    below_segs = []
    curr_above = p_vals[0] > p_mean
    curr_len = 1
    for i in range(1, len(p_vals)):
        if (p_vals[i] > p_mean) == curr_above:
            curr_len += 1
        else:
            if curr_above:
                above_segs.append(curr_len)
            else:
                below_segs.append(curr_len)
            curr_above = p_vals[i] > p_mean
            curr_len = 1
    if curr_above:
        above_segs.append(curr_len)
    else:
        below_segs.append(curr_len)

    if len(above_segs) > 2 and len(below_segs) > 2:
        above_segs = above_segs[1:-1]
        below_segs = below_segs[1:-1]
        avg_a = sum(above_segs) / len(above_segs)
        avg_b = sum(below_segs) / len(below_segs)
        hc_ara = max(avg_a, avg_b) / min(avg_a, avg_b)
        delta = abs(hc_ara - phi)
        print(f"  {K:>6.2f}  {K/K_c:>8.4f}  {hc_ara:>15.6f}  {delta:>10.6f}")

# ================================================================
# SUMMARY
# ================================================================

print()
print("=" * 90)
print("SUMMARY")
print("=" * 90)
print()
print(f"  Golden winding number: ω = 1/φ = {golden_winding:.10f}")
print(f"  Critical perturbation: K_c ≈ 0.9716 (Greene 1979)")
print(f"  φ = {phi:.10f}")
print()
print(f"  The golden mean torus is the LAST surviving invariant torus")
print(f"  in the standard map — the most stable orbit in Hamiltonian mechanics.")
print()
print(f"  RESULTS:")
print(f"  See tables above for ARA measurements at multiple K values,")
print(f"  comparison across winding numbers, and behaviour near K_c.")
print()
print(f"  Dylan La Franchi & Claude — April 21, 2026")

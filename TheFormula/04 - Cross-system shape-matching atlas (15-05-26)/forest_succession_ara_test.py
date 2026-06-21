"""
forest_succession_ara_test.py — does forest succession sit at φ?

Follow-up test from `lungs_forests_vertical_ara_test.py`:
  Lung breath cycle ARA ≈ φ (engine, free-running, internal).
  Forest's outer cycles (daily, seasonal) are forced — NOT the right comparison.
  The framework's vertical-ARA prediction is that the lung-equivalent inside
  forests is the FREE-RUNNING ENGINE cycle at the largest internally-tracked
  scale: forest succession.

This script uses Mauna Loa CO2 data (1958–present, 65+ years) which is the
global biosphere's "breath" record. The relevant cycles:
  - Seasonal (~12 mo): forced by Earth's orbit, prediction ARA ≈ 2.0 (forced)
  - Inter-annual (~3-7 yr): driven by ENSO/drought modulating forest sink
  - Decadal+: forest succession envelope

Framework predictions:
  - Seasonal ARA should be near 2.0 (forced harmonic ceiling) since this
    cycle is pinned by the planet's orbit.
  - Inter-annual ARA on detrended growth rate should be near φ if it's
    a free-running engine cycle.

DATA: NOAA GML Mauna Loa CO2 monthly + annual growth rate.
Source: https://gml.noaa.gov/ccgg/trends/data.html (public, no auth).
"""
import os, json, math
import numpy as np
import requests
from io import StringIO

PHI = (1 + 5**0.5) / 2

# ============================================================================
# FETCH
# ============================================================================
print("Fetching NOAA Mauna Loa CO2 data...")
r_mo = requests.get('https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.txt',
                    timeout=20, headers={'User-Agent':'Mozilla/5.0'})
r_gr = requests.get('https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_gr_mlo.txt',
                    timeout=20, headers={'User-Agent':'Mozilla/5.0'})

# Parse monthly
mo_rows = []
for line in r_mo.text.split('\n'):
    if line.startswith('#') or not line.strip(): continue
    parts = line.split()
    if len(parts) >= 6:
        try:
            yr, mo, dec, avg, dsn, _ndays = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
            yr = int(yr); mo = int(mo); dec = float(dec); avg = float(avg); dsn = float(dsn)
            if avg > 0 and dsn > 0:
                mo_rows.append((yr, mo, dec, avg, dsn))
        except: continue

# Parse annual growth rate
gr_rows = []
for line in r_gr.text.split('\n'):
    if line.startswith('#') or not line.strip(): continue
    parts = line.split()
    if len(parts) >= 3:
        try:
            yr = int(parts[0]); gr = float(parts[1]); unc = float(parts[2])
            gr_rows.append((yr, gr, unc))
        except: continue

mo_arr = np.array([(r[2], r[3], r[4]) for r in mo_rows])  # dec_year, avg, deseasonalised
gr_arr = np.array([(r[0], r[1]) for r in gr_rows])         # year, growth_rate

print(f"  Monthly: {len(mo_arr)} months, {mo_arr[0,0]:.2f} to {mo_arr[-1,0]:.2f}")
print(f"  Annual growth: {len(gr_arr)} years, {gr_arr[0,0]:.0f} to {gr_arr[-1,0]:.0f}")
print()

# ============================================================================
# 1. SEASONAL CYCLE ARA — expected forced ~2.0
# ============================================================================
print("=" * 78)
print("1. SEASONAL CYCLE ARA (T_rising / T_falling within one year)")
print("=" * 78)
# Compute seasonal cycle: average each calendar month over all years
months_avg = np.zeros(12); months_count = np.zeros(12)
for dec, avg, dsn in mo_arr:
    m = int(round((dec - int(dec)) * 12)) % 12
    months_avg[m] += avg - dsn  # use raw - deseasonalized to isolate seasonal
    months_count[m] += 1
seasonal_cycle = months_avg / np.maximum(months_count, 1)
print("Mean seasonal anomaly per month (raw - deseasonalized):")
for i, v in enumerate(seasonal_cycle):
    print(f"  month {i+1:>2}: {v:+.2f} ppm")

# Find peak and trough
imax = int(np.argmax(seasonal_cycle))  # CO2 peak (NH winter, end of respiration)
imin = int(np.argmin(seasonal_cycle))  # CO2 trough (NH growing season end)
print(f"\nPeak (CO2 max, end-respiration): month {imax+1}, value {seasonal_cycle[imax]:+.2f}")
print(f"Trough (CO2 min, end-growth):    month {imin+1}, value {seasonal_cycle[imin]:+.2f}")

# T_rising = peak - trough going forward; T_falling = trough - peak going forward
def cycle_lengths(peak_idx, trough_idx, n=12):
    if peak_idx > trough_idx:
        # peak comes later in calendar year than trough
        rising = peak_idx - trough_idx
        falling = (n - peak_idx) + trough_idx
    else:
        rising = (n - trough_idx) + peak_idx
        falling = trough_idx - peak_idx
    return rising, falling

t_rise, t_fall = cycle_lengths(imax, imin)
print(f"T_rising (winter respiration, CO2 accumulating):  {t_rise} months")
print(f"T_falling (growing season, CO2 being absorbed):   {t_fall} months")
ara_seasonal = t_fall / t_rise if t_rise > 0 else float('nan')
print(f"Seasonal ARA = T_falling / T_rising = {ara_seasonal:.3f}")
print(f"  Framework prediction: ~2.0 (forced harmonic by orbit)")
print(f"  Distance from 2.0: {abs(ara_seasonal - 2.0):.3f} ({abs(ara_seasonal - 2.0)/2.0*100:.1f}%)")
print(f"  Distance from φ:   {abs(ara_seasonal - PHI):.3f}")
print()

# ============================================================================
# 2. INTER-ANNUAL ARA from CO2 growth rate (the "forest succession" signal)
# ============================================================================
print("=" * 78)
print("2. INTER-ANNUAL CYCLE ARA from CO2 growth rate")
print("=" * 78)
print("Annual CO2 growth rate captures global biosphere sink strength.")
print("Low growth rate = biosphere absorbing well (forest accumulation).")
print("High growth rate = biosphere overwhelmed (forest release / failure).")
print()

years = gr_arr[:, 0]
gr = gr_arr[:, 1]
print(f"Years: {len(years)}, range {years[0]:.0f}-{years[-1]:.0f}")
print(f"Mean growth rate: {gr.mean():.2f} ppm/yr  (rising over time due to emissions)")

# Detrend with linear fit
coeffs = np.polyfit(years, gr, 1)
trend = np.polyval(coeffs, years)
gr_resid = gr - trend
print(f"Linear trend: {coeffs[0]:.3f} ppm/yr² (acceleration of emissions)")
print(f"Detrended growth rate std: {gr_resid.std():.2f} ppm/yr")

# Find peaks and troughs in the detrended series
from scipy.signal import find_peaks
peaks_pos, _ = find_peaks(gr_resid, distance=2)
peaks_neg, _ = find_peaks(-gr_resid, distance=2)
print(f"Detected peaks (high CO2, weak sink): {len(peaks_pos)} events at years {[int(years[p]) for p in peaks_pos]}")
print(f"Detected troughs (low CO2, strong sink): {len(peaks_neg)} events at years {[int(years[p]) for p in peaks_neg]}")

# Measure ARA over each cycle
# A cycle: trough → peak → next trough.
# T_accumulation = trough to peak (biosphere weakening, CO2 building up)
# Actually flip sign: in CO2 growth rate, LOW = biosphere absorbing (accumulating biomass)
#                                          HIGH = biosphere releasing
# So in BIOMASS terms:
#   T_accumulation (biomass building) = high-sink period = trough in CO2 growth rate
#   T_release (biomass releasing) = low-sink period = peak in CO2 growth rate
all_extrema = sorted(list(peaks_pos) + list(peaks_neg))
print()
print("Cycle ARAs (in biomass terms: T_release/T_accumulation):")
print(f"{'cycle':>5}  {'years':>15}  {'T_accum (yr)':>13}  {'T_release (yr)':>14}  {'ARA':>6}")
print('-' * 65)
aras = []
# A complete cycle = trough → peak → next trough
peak_set = set(peaks_pos.tolist())
trough_set = set(peaks_neg.tolist())
i = 0
cycle_num = 0
while i < len(all_extrema) - 2:
    a, b, c = all_extrema[i], all_extrema[i+1], all_extrema[i+2]
    # Want trough(a) → peak(b) → trough(c)
    if a in trough_set and b in peak_set and c in trough_set:
        T_accum = years[b] - years[a]  # rising phase of CO2 = release phase of biomass... wait
        # In biomass terms: trough in CO2_gr = high sink = accumulation. So at year[a] biomass is accumulating.
        # peak in CO2_gr = release. Year[b] biomass is releasing fastest.
        # So accumulation phase = trough → next peak? No, accumulation starts BEFORE trough (sink building up)
        # Better: peak → next peak = full cycle, T_release = peak → next trough, T_accum = trough → next peak
        # Use: T_accum = years from one trough to next peak; T_release = next peak to next trough
        T_release = years[c] - years[b]
        ara = T_release / T_accum if T_accum > 0 else float('nan')
        aras.append(ara)
        cycle_num += 1
        print(f"  {cycle_num:>3}   {int(years[a])}-{int(years[c])}     {T_accum:>13.1f}  {T_release:>14.1f}  {ara:>6.3f}")
        i += 2  # advance to next trough
    else:
        i += 1
print('-' * 65)
if aras:
    print(f"  Mean inter-annual ARA: {np.mean(aras):.3f}")
    print(f"  Median inter-annual ARA: {np.median(aras):.3f}")
    print(f"  Std: {np.std(aras):.3f}")
    print(f"  Framework prediction: ≈ φ = {PHI:.3f}")
    print(f"  Mean off φ:   {abs(np.mean(aras) - PHI)/PHI*100:.1f}%")
    print(f"  Median off φ: {abs(np.median(aras) - PHI)/PHI*100:.1f}%")
print()

# ============================================================================
# 3. ENSO-period filter: pure forest signal at 3-7 year band
# ============================================================================
print("=" * 78)
print("3. FOREST SUCCESSION ARA via bandpass at ENSO-period (3-7 yr)")
print("=" * 78)
from scipy.signal import butter, sosfilt, find_peaks
# Use deseasonalized monthly CO2, detrend, then bandpass 3-7 yr
dsn = mo_arr[:, 1] - (mo_arr[:, 1] - mo_arr[:, 2])  # the deseasonalized value
# Actually mo_arr[:, 2] is already deseasonalized
dsn = mo_arr[:, 2]
# Convert to monthly anomalies (relative to long-term trend)
month_t = mo_arr[:, 0]
coeffs_m = np.polyfit(month_t, dsn, 1)
dsn_resid = dsn - np.polyval(coeffs_m, month_t)

# Bandpass at 3-7 yr (= 36-84 months)
fs = 12.0  # samples per year
T_lo = 3.0; T_hi = 7.0
sos = butter(2, [1/T_hi/(fs/2), 1/T_lo/(fs/2)], btype='bandpass', output='sos')
bp = sosfilt(sos, dsn_resid)

# Find peaks in bandpassed signal
peaks_b, _ = find_peaks(bp, distance=24)
troughs_b, _ = find_peaks(-bp, distance=24)
print(f"Bandpassed peaks (release-dominated): {len(peaks_b)} events")
print(f"Bandpassed troughs (accumulation-dominated): {len(troughs_b)} events")

# Measure rise/fall ARA per cycle
aras_bp = []
all_ext = sorted(list(peaks_b) + list(troughs_b))
peak_set = set(peaks_b.tolist())
trough_set = set(troughs_b.tolist())
for i in range(len(all_ext) - 2):
    a, b, c = all_ext[i], all_ext[i+1], all_ext[i+2]
    if a in trough_set and b in peak_set and c in trough_set:
        T_accum = (month_t[b] - month_t[a])
        T_release = (month_t[c] - month_t[b])
        if T_accum > 0:
            aras_bp.append(T_release / T_accum)

if aras_bp:
    print(f"  Number of complete cycles: {len(aras_bp)}")
    print(f"  Mean ARA: {np.mean(aras_bp):.3f}")
    print(f"  Median ARA: {np.median(aras_bp):.3f}")
    print(f"  Distance from φ: mean {abs(np.mean(aras_bp) - PHI)/PHI*100:.1f}%, median {abs(np.median(aras_bp) - PHI)/PHI*100:.1f}%")

# Save
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'forest_succession_ara_data.js')
payload = dict(
    date='2026-05-11',
    data_source='NOAA GML Mauna Loa CO2 (monthly + annual growth rate)',
    n_months=len(mo_arr),
    n_years=len(gr_arr),
    seasonal_ara=ara_seasonal,
    inter_annual_aras=aras,
    inter_annual_mean=float(np.mean(aras)) if aras else None,
    inter_annual_median=float(np.median(aras)) if aras else None,
    bandpass_aras_3_7yr=aras_bp,
    bandpass_mean=float(np.mean(aras_bp)) if aras_bp else None,
    bandpass_median=float(np.median(aras_bp)) if aras_bp else None,
    phi=PHI,
)
with open(OUT, 'w') as f:
    f.write("window.FOREST_SUCCESSION_ARA = " + json.dumps(payload, default=str) + ";\n")
print(f"\nSaved -> {OUT}")

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import datetime
import os

# Define stations
# Natural: Neversink River near Claryville, NY
# Managed: Colorado River below Glen Canyon Dam, AZ
STATIONS = {
    "01435000": "Natural (Neversink River, NY)",
    "09380000": "Managed (Colorado River, AZ)"
}

# Use a 3-year window to prevent pulling too much 15-minute data at once
START_DATE = "2021-01-01"
END_DATE = "2023-12-31"

def fetch_usgs_iv_data(site_no, start_dt, end_dt):
    print(f"Fetching 15-minute data for USGS {site_no} ({STATIONS[site_no]})...")
    url = "https://waterservices.usgs.gov/nwis/iv/"
    params = {
        "format": "json",
        "sites": site_no,
        "startDT": start_dt,
        "endDT": end_dt,
        "parameterCd": "00060" # Discharge, cubic feet per second
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    try:
        ts_data = data['value']['timeSeries'][0]['values'][0]['value']
        df = pd.DataFrame(ts_data)
        df['value'] = pd.to_numeric(df['value'])
        df['dateTime'] = pd.to_datetime(df['dateTime'])
        df = df.set_index('dateTime')
        # Some IV data might have missing records, resample to 15T to ensure regular intervals, interpolating small gaps
        df_resampled = df['value'].resample('15min').interpolate(method='linear', limit=4)
        df_resampled = df_resampled.dropna()
        return df_resampled
    except (KeyError, IndexError) as e:
        print(f"Error parsing data for site {site_no}: {e}")
        return pd.Series(dtype=float)

def baseflow_separation_lyne_hollick(q, alpha=0.925):
    """
    Applies the Lyne-Hollick digital filter for baseflow separation.
    Returns the direct runoff (q_f) time series.
    """
    q_f = np.zeros(len(q))
    q_vals = q.values
    for i in range(1, len(q)):
        q_f[i] = alpha * q_f[i-1] + 0.5 * (1 + alpha) * (q_vals[i] - q_vals[i-1])
        if q_f[i] < 0:
            q_f[i] = 0
        if q_f[i] > q_vals[i]:
            q_f[i] = q_vals[i]
    return pd.Series(q_f, index=q.index)

def analyze_hydrographs_v2(series, site_name):
    # 1. Baseflow Separation
    q_f = baseflow_separation_lyne_hollick(series)
    
    # 2. Peak Finding on Direct Runoff
    # Use top 10% of flows as prominence to isolate significant storms and ignore noise
    prominence = q_f.quantile(0.90) 
    if prominence == 0:
        prominence = q_f.max() * 0.1
        
    # distance=96 means peaks must be at least 1 day (96 * 15 mins) apart
    peaks, properties = find_peaks(q_f.values, prominence=prominence, distance=96)
    
    events = []
    ratios = []
    
    for i in range(len(peaks)):
        peak_idx = peaks[i]
        peak_val = q_f.iloc[peak_idx]
        
        # Define the start/end of the storm as the point where direct runoff drops below 5% of the peak
        threshold = peak_val * 0.05
        
        # Find start of rising limb
        start_idx = peak_idx
        while start_idx > 0 and q_f.iloc[start_idx] > threshold:
            start_idx -= 1
            
        # Find end of falling limb
        end_idx = peak_idx
        # Don't overlap with the next storm peak's rising limb
        max_end = peaks[i+1] if i + 1 < len(peaks) else len(q_f) - 1
        while end_idx < max_end and q_f.iloc[end_idx] > threshold:
            end_idx += 1
            
        t_rise = peak_idx - start_idx
        t_fall = end_idx - peak_idx
        
        # Filter for valid storm events
        if t_rise > 0 and t_fall > 0:
            ratio = t_fall / t_rise
            if ratio < 15: # Filter out weird edge cases
                events.append({
                    'peak_time': q_f.index[peak_idx],
                    't_rise_15m': t_rise,
                    't_fall_15m': t_fall,
                    'ratio': ratio
                })
                ratios.append(ratio)
                
    print(f"{site_name}: Identified {len(ratios)} distinct direct runoff events.")
    return ratios

def main():
    results = {}
    
    for site_no, site_name in STATIONS.items():
        series = fetch_usgs_iv_data(site_no, START_DATE, END_DATE)
        if not series.empty:
            ratios = analyze_hydrographs_v2(series, site_name)
            results[site_name] = ratios
            
    # Statistical Plot
    plt.figure(figsize=(12, 6))
    
    colors = {'Natural (Neversink River, NY)': '#10b981', 'Managed (Colorado River, AZ)': '#ff3366'}
    
    for site_name, ratios in results.items():
        if ratios:
            plt.hist(ratios, bins=np.arange(0, 10, 0.25), alpha=0.6, label=f"{site_name} (n={len(ratios)})", color=colors.get(site_name, 'blue'))
            median_val = np.median(ratios)
            mean_val = np.mean(ratios)
            plt.axvline(median_val, color=colors.get(site_name, 'blue'), linestyle='dashed', linewidth=2, label=f'{site_name} Median: {median_val:.2f}')
            print(f"{site_name} - Mean Ratio: {mean_val:.3f}, Median Ratio: {median_val:.3f}")

    # Plot Phi
    phi = 1.618
    plt.axvline(phi, color='#ffd700', linestyle='solid', linewidth=3, label=r'Golden Ratio ($\phi$) = 1.618')
    # Plot SCS Standard
    scs_standard = 1.67
    plt.axvline(scs_standard, color='#4dabf7', linestyle='dotted', linewidth=3, label=f'SCS Standard = {scs_standard}')
    
    plt.title('V2: Distribution of Direct Runoff Ratios (15-min Data + Baseflow Separation)')
    plt.xlabel('Ratio (Recession Limb / Rising Limb)')
    plt.ylabel('Number of Events')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_file = os.path.join(os.path.dirname(__file__), 'hydrograph_ratios_v2.png')
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")

if __name__ == "__main__":
    main()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://noaadata.apps.nsidc.org/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v4.0.csv"

def fetch_sea_ice_data():
    print("Fetching daily Arctic Sea Ice Extent data from NSIDC...")
    try:
        # Download file to disk first to bypass any SSL issues
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(URL, headers=headers, verify=False)
        response.raise_for_status()
        with open('sea_ice.csv', 'wb') as f:
            f.write(response.content)
            
        # The CSV has 2 header rows
        cols = ["Year", "Month", "Day", "Extent", "Missing", "Source"]
        df = pd.read_csv('sea_ice.csv', skiprows=2, names=cols, sep=',')
        
        # Clean up whitespace in strings just in case
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        
        # Create a proper datetime index
        df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
        df = df.set_index('Date')
        
        # NSIDC uses -9999 for missing data
        df['Extent'] = df['Extent'].replace(-9999, np.nan)
        df['Extent'] = pd.to_numeric(df['Extent'])
        
        # Interpolate missing days (there are a few missing days in the 1980s)
        df['Extent'] = df['Extent'].interpolate(method='time')
        
        print(f"Successfully downloaded {len(df)} days of sea ice data (since 1978).")
        return df['Extent']
    except Exception as e:
        print(f"Failed to fetch or parse data: {e}")
        return pd.Series(dtype=float)

def analyze_ice_cycles(series):
    # 1. Smoothing
    # Apply a 14-day rolling mean to smooth out minor storm-related daily variations
    smoothed = series.rolling(window=14, center=True).mean().dropna()
    
    # 2. Find Peaks (March Maximums - end of freeze, start of melt)
    # The cycle is annual (365 days). Distance = 300 days ensures we get exactly 1 peak per year.
    peaks, _ = find_peaks(smoothed.values, distance=300, prominence=2.0)
    
    # 3. Find Troughs (September Minimums - end of melt, start of freeze)
    inv_smoothed = -smoothed.values
    troughs, _ = find_peaks(inv_smoothed, distance=300, prominence=2.0)
    
    print(f"Identified {len(peaks)} Annual Maximums and {len(troughs)} Annual Minimums.")
    
    ratios = []
    
    # 4. Calculate Phases (Freeze vs Melt)
    for p_idx in peaks:
        # Find the trough immediately preceding this peak (Sep Min -> Mar Max = Freeze)
        prev_troughs = troughs[troughs < p_idx]
        if len(prev_troughs) == 0:
            continue
        min_before_idx = prev_troughs[-1]
        
        # Find the trough immediately following this peak (Mar Max -> Sep Min = Melt)
        next_troughs = troughs[troughs > p_idx]
        if len(next_troughs) == 0:
            continue
        min_after_idx = next_troughs[0]
        
        # Calculate duration in days
        # The index is just the integer location in the smoothed array
        t_freeze = p_idx - min_before_idx # Accumulation duration (days)
        t_melt = min_after_idx - p_idx    # Release duration (days)
        
        # Sanity check: Freeze + Melt should be roughly 365 days
        if t_freeze > 0 and t_melt > 0 and (300 < (t_freeze + t_melt) < 400):
            # We calculate Freeze (Accumulation) / Melt (Release)
            ratio = t_freeze / t_melt
            ratios.append(ratio)
                
    print(f"Calculated ratios for {len(ratios)} complete annual cycles.")
    return ratios

def main():
    series = fetch_sea_ice_data()
    if series.empty:
        return
        
    ratios = analyze_ice_cycles(series)
    
    if not ratios:
        print("Not enough cycles found.")
        return
        
    # Statistics
    mean_val = np.mean(ratios)
    median_val = np.median(ratios)
    
    print(f"Arctic Sea Ice - Mean Ratio (T_freeze / T_melt): {mean_val:.3f}")
    print(f"Arctic Sea Ice - Median Ratio: {median_val:.3f}")
    
    # Statistical Plot
    plt.figure(figsize=(10, 6))
    plt.hist(ratios, bins=np.arange(0, 3, 0.1), alpha=0.7, color='#4dabf7', label=f'Annual Ice Cycles (n={len(ratios)})')
    plt.axvline(median_val, color='#4dabf7', linestyle='dashed', linewidth=2, label=f'Median: {median_val:.2f}')
    
    # Plot Phi
    phi = 1.618
    plt.axvline(phi, color='#fcc419', linestyle='solid', linewidth=3, label=r'Golden Ratio ($\phi$) = 1.618')
    
    plt.title('Distribution of Phase Ratios (Freeze Days / Melt Days) for Arctic Sea Ice')
    plt.xlabel('Ratio (Accumulation Duration / Release Duration)')
    plt.ylabel('Number of Annual Cycles')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_file = os.path.join(os.path.dirname(__file__), 'ice_ratios.png')
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")

if __name__ == "__main__":
    main()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://sidc.be/SILSO/DATA/SN_m_tot_V2.0.txt"

def fetch_sunspot_data():
    print("Fetching monthly sunspot data from SILSO...")
    # Columns: Year, Month, Decimal Year, Sunspot Number, Std, Num_Obs, Definitive/Provisional
    cols = ["Year", "Month", "Decimal_Year", "SSN", "Std", "Num_Obs", "Marker"]
    try:
        response = requests.get(URL, verify=False)
        with open('sunspots.txt', 'wb') as f:
            f.write(response.content)
            
        df = pd.read_csv('sunspots.txt', sep=r'\s+', header=None, names=cols)
        # Replace -1 with NaN (SILSO convention for missing data)
        df['SSN'] = df['SSN'].replace(-1, np.nan)
        print(f"Successfully downloaded {len(df)} months of data (since 1749).")
        return df
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return pd.DataFrame()

def analyze_solar_cycles(df):
    # 1. Standard 13-month smoothing
    # We use a 13-month rolling mean centered to smooth out monthly noise and find the true solar max/min
    smoothed_ssn = df['SSN'].rolling(window=13, center=True).mean()
    
    # 2. Find Peaks (Solar Maximums)
    # Solar cycles are ~11 years long (132 months). We set distance to 84 months (7 years) to be safe.
    peaks, _ = find_peaks(smoothed_ssn, distance=84, prominence=20)
    
    # 3. Find Troughs (Solar Minimums)
    # Invert the smoothed data to find minimums
    inv_ssn = -smoothed_ssn
    troughs, _ = find_peaks(inv_ssn, distance=84, prominence=20)
    
    print(f"Identified {len(peaks)} Solar Maximums and {len(troughs)} Solar Minimums.")
    
    ratios = []
    
    # 4. Calculate Phases (Waldmeier Effect: T_fall / T_rise)
    for p_idx in peaks:
        # Find the trough immediately preceding this peak (Solar Min -> Solar Max)
        prev_troughs = troughs[troughs < p_idx]
        if len(prev_troughs) == 0:
            continue
        min_before_idx = prev_troughs[-1]
        
        # Find the trough immediately following this peak (Solar Max -> Solar Min)
        next_troughs = troughs[troughs > p_idx]
        if len(next_troughs) == 0:
            continue
        min_after_idx = next_troughs[0]
        
        t_rise = p_idx - min_before_idx # Accumulation duration (months)
        t_fall = min_after_idx - p_idx # Release/Decay duration (months)
        
        if t_rise > 0 and t_fall > 0:
            ratio = t_fall / t_rise
            
            # Filter absurd outliers
            if ratio < 10 and ratio > 0.1:
                ratios.append(ratio)
                
    print(f"Calculated ratios for {len(ratios)} complete solar cycles.")
    return ratios

def main():
    df = fetch_sunspot_data()
    if df.empty:
        return
        
    ratios = analyze_solar_cycles(df)
    
    if not ratios:
        print("Not enough cycles found.")
        return
        
    # Statistics
    mean_val = np.mean(ratios)
    median_val = np.median(ratios)
    
    print(f"Solar Dynamo - Mean Ratio (T_fall / T_rise): {mean_val:.3f}")
    print(f"Solar Dynamo - Median Ratio: {median_val:.3f}")
    
    # Statistical Plot
    plt.figure(figsize=(10, 6))
    plt.hist(ratios, bins=np.arange(0, 4, 0.2), alpha=0.7, color='#ff6b6b', label=f'Solar Cycles (n={len(ratios)})')
    plt.axvline(median_val, color='#ff6b6b', linestyle='dashed', linewidth=2, label=f'Median: {median_val:.2f}')
    
    # Plot Phi
    phi = 1.618
    plt.axvline(phi, color='#fcc419', linestyle='solid', linewidth=3, label=r'Golden Ratio ($\phi$) = 1.618')
    
    plt.title('Distribution of Phase Ratios (T_fall / T_rise) for 25 Solar Cycles (1749-Present)')
    plt.xlabel('Ratio (Release Duration / Accumulation Duration)')
    plt.ylabel('Number of Solar Cycles')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_file = os.path.join(os.path.dirname(__file__), 'solar_ratios.png')
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")

if __name__ == "__main__":
    main()

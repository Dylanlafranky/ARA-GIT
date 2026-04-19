import lightkurve as lk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import os

# Target: V1154 Cyg (Classical Cepheid in Kepler field)
KIC_ID = "KIC 7548061"

def fetch_and_process_lightcurve():
    print(f"Searching MAST for {KIC_ID} (Kepler data)...")
    # Download all available quarters for the Kepler mission (Q0 - Q17)
    search_result = lk.search_lightcurve(KIC_ID, mission="Kepler", author="Kepler")
    print(f"Found {len(search_result)} quarters of data. Downloading...")
    
    # Download and stitch all quarters into a single continuous light curve
    lc_collection = search_result.download_all()
    lc = lc_collection.stitch()
    
    # Remove NaN values and outliers
    lc = lc.remove_nans().remove_outliers(sigma=5)
    
    # Normalize the light curve so the median flux is 1.0
    lc = lc.normalize()
    
    print(f"Successfully downloaded and processed light curve. Total points: {len(lc.time)}")
    return lc

def analyze_pulsations(lc):
    time = lc.time.value
    flux = lc.flux.value
    
    # Invert the light curve to find troughs (minimum brightness) easily using find_peaks
    inv_flux = -flux
    
    # Find Peaks (Maximum Brightness)
    # V1154 Cyg has a period of ~4.9 days. Kepler long cadence is ~30 mins.
    # 4.9 days = 4.9 * 24 * 2 = 235 cadence points.
    # We set distance to ~150 to ensure we only get one peak per cycle.
    peaks, _ = find_peaks(flux, distance=150, prominence=0.01)
    
    # Find Troughs (Minimum Brightness)
    troughs, _ = find_peaks(inv_flux, distance=150, prominence=0.01)
    
    print(f"Identified {len(peaks)} peaks and {len(troughs)} troughs.")
    
    ratios = []
    
    # For each peak, find the subsequent trough (Decline Phase)
    # and the trough before it (Rise Phase)
    for p_idx in peaks:
        t_peak = time[p_idx]
        
        # Find the trough immediately preceding this peak
        prev_troughs = troughs[troughs < p_idx]
        if len(prev_troughs) == 0:
            continue
        trough_before_idx = prev_troughs[-1]
        t_trough_before = time[trough_before_idx]
        
        # Find the trough immediately following this peak
        next_troughs = troughs[troughs > p_idx]
        if len(next_troughs) == 0:
            continue
        trough_after_idx = next_troughs[0]
        t_trough_after = time[trough_after_idx]
        
        t_rise = t_peak - t_trough_before
        t_decline = t_trough_after - t_peak
        
        if t_rise > 0 and t_decline > 0:
            ratio = t_decline / t_rise
            
            # Sanity check to filter out huge gaps in data (Kepler data down-links, etc.)
            # If the total cycle is way longer than 5.5 days, skip it
            if (t_rise + t_decline) < 5.5:
                ratios.append(ratio)
                
    print(f"Calculated ratios for {len(ratios)} continuous pulsation cycles.")
    return ratios

def main():
    lc = fetch_and_process_lightcurve()
    ratios = analyze_pulsations(lc)
    
    # Statistics
    mean_val = np.mean(ratios)
    median_val = np.median(ratios)
    
    print(f"V1154 Cyg - Mean Ratio (Decline/Rise): {mean_val:.3f}")
    print(f"V1154 Cyg - Median Ratio: {median_val:.3f}")
    
    # Statistical Plot
    plt.figure(figsize=(10, 6))
    plt.hist(ratios, bins=np.arange(0, 3, 0.05), alpha=0.7, color='#b197fc', label=f'V1154 Cyg (n={len(ratios)})')
    plt.axvline(median_val, color='#b197fc', linestyle='dashed', linewidth=2, label=f'Median: {median_val:.2f}')
    
    # Plot Phi
    phi = 1.618
    plt.axvline(phi, color='#ffd700', linestyle='solid', linewidth=3, label=r'Golden Ratio ($\phi$) = 1.618')
    
    plt.title('Distribution of Decline/Rise Ratios for Classical Cepheid V1154 Cyg')
    plt.xlabel('Ratio (T_decline / T_rise)')
    plt.ylabel('Number of Pulsation Cycles')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_file = os.path.join(os.path.dirname(__file__), 'stellar_ratios.png')
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")

if __name__ == "__main__":
    main()

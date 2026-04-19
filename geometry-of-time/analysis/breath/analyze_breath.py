import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import neurokit2 as nk
import os

def fetch_and_process_breath_data():
    print("Fetching continuous physiological dataset from neurokit2...")
    # Load 5 minutes of resting human physiological data recorded at 100Hz
    data = nk.data("bio_resting_5min_100hz")
    
    # Extract the raw respiratory signal (RSP)
    rsp_raw = data["RSP"]
    print(f"Successfully loaded {len(rsp_raw)} data points (5 minutes at 100Hz).")
    
    # Clean the signal using standard physiological bandpass filtering (0.05 - 0.35 Hz)
    # This removes heartbeat artifacts and movement noise, leaving the true breath macro-curve
    rsp_cleaned = nk.rsp_clean(rsp_raw, sampling_rate=100)
    
    return rsp_cleaned

def analyze_breath_cycles(rsp):
    # The data is at 100Hz. 
    # Normal breathing is 12-20 breaths per min (3 to 5 seconds per breath).
    # 3 seconds = 300 samples.
    # We set distance to 150 samples (1.5 seconds) to ensure we find exactly one peak per breath.
    
    # 1. Find Peaks (End of Inhalation / Lungs Full)
    peaks, _ = find_peaks(rsp, distance=150)
    
    # 2. Find Troughs (End of Exhalation / Lungs Empty)
    inv_rsp = -rsp
    troughs, _ = find_peaks(inv_rsp, distance=150)
    
    print(f"Identified {len(peaks)} inhalation peaks and {len(troughs)} exhalation troughs.")
    
    ratios = []
    
    # 3. Calculate Phases
    for p_idx in peaks:
        # Trough before peak = start of inhalation
        prev_troughs = troughs[troughs < p_idx]
        if len(prev_troughs) == 0:
            continue
        min_before_idx = prev_troughs[-1]
        
        # Trough after peak = end of exhalation
        next_troughs = troughs[troughs > p_idx]
        if len(next_troughs) == 0:
            continue
        min_after_idx = next_troughs[0]
        
        # Duration in samples (1 sample = 10ms)
        t_in = p_idx - min_before_idx # Accumulation duration (Inhalation)
        t_ex = min_after_idx - p_idx  # Release duration (Exhalation)
        
        # Sanity check for realistic human breath times
        # t_in and t_ex should be between ~0.5 seconds (50 samples) and ~5 seconds (500 samples)
        if 50 < t_in < 500 and 50 < t_ex < 500:
            # We calculate T_ex / T_in (Exhalation / Inhalation ratio)
            ratio = t_ex / t_in
            ratios.append(ratio)
                
    print(f"Calculated ratios for {len(ratios)} complete breath cycles.")
    return ratios

def main():
    rsp = fetch_and_process_breath_data()
    ratios = analyze_breath_cycles(rsp)
    
    if not ratios:
        print("Not enough cycles found.")
        return
        
    # Statistics
    mean_val = np.mean(ratios)
    median_val = np.median(ratios)
    
    print(f"Human Breath - Mean Ratio (T_ex / T_in): {mean_val:.3f}")
    print(f"Human Breath - Median Ratio: {median_val:.3f}")
    
    # Statistical Plot
    plt.figure(figsize=(10, 6))
    plt.hist(ratios, bins=np.arange(0, 3, 0.1), alpha=0.7, color='#20c997', label=f'Breath Cycles (n={len(ratios)})')
    plt.axvline(median_val, color='#20c997', linestyle='dashed', linewidth=2, label=f'Median: {median_val:.2f}')
    
    # Plot Phi
    phi = 1.618
    plt.axvline(phi, color='#fcc419', linestyle='solid', linewidth=3, label=r'Golden Ratio ($\phi$) = 1.618')
    
    plt.title('Distribution of Phase Ratios (Exhalation Time / Inhalation Time) for Human Resting Breath')
    plt.xlabel('Ratio (Release Duration / Accumulation Duration)')
    plt.ylabel('Number of Breath Cycles')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_file = os.path.join(os.path.dirname(__file__), 'breath_ratios.png')
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")

if __name__ == "__main__":
    main()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, filtfilt
import neurokit2 as nk
import os

def analyze_raw_brain():
    print("Fetching raw human EEG dataset...")
    raw = nk.data("eeg_1min_200hz")
    eeg_data = raw.get_data(picks='eeg')[0]
    fs = 200
    
    # 1. High-pass ONLY (to remove DC drift/movement, but keep RAW spike shape)
    print("Applying 0.5Hz high-pass filter (keeping raw spike asymmetry)...")
    b, a = butter(3, 0.5 / (0.5 * fs), btype='high')
    raw_signal = filtfilt(b, a, eeg_data)
    
    # 2. Find Peaks (The "Spikes")
    # We look for raw voltage peaks. 
    # Since we aren't filtering out high frequencies, we need a small distance.
    peaks, _ = find_peaks(raw_signal, distance=5, prominence=np.std(raw_signal)*0.5)
    
    # 3. Find Troughs
    inv_raw = -raw_signal
    troughs, _ = find_peaks(inv_raw, distance=5, prominence=np.std(raw_signal)*0.5)
    
    print(f"Identified {len(peaks)} raw electric spikes and {len(troughs)} troughs.")
    
    ratios = []
    
    # 4. Calculate Asymmetry of the RAW DISCHARGE
    for p_idx in peaks:
        prev_troughs = troughs[troughs < p_idx]
        if len(prev_troughs) == 0:
            continue
        min_before_idx = prev_troughs[-1]
        
        next_troughs = troughs[troughs > p_idx]
        if len(next_troughs) == 0:
            continue
        min_after_idx = next_troughs[0]
        
        t_rise = p_idx - min_before_idx 
        t_fall = min_after_idx - p_idx
        
        if t_rise > 0 and t_fall > 0:
            # We calculate Fall (Discharge) / Rise (Charge)
            ratio = t_fall / t_rise
            if 0.2 < ratio < 5:
                ratios.append(ratio)
                
    print(f"Calculated ratios for {len(ratios)} raw neural spikes.")
    return ratios

def main():
    ratios = analyze_raw_brain()
    
    if not ratios:
        print("No valid spikes found.")
        return
        
    mean_val = np.mean(ratios)
    median_val = np.median(ratios)
    
    print(f"Raw Brain Spikes - Mean Ratio: {mean_val:.3f}")
    print(f"Raw Brain Spikes - Median Ratio: {median_val:.3f}")
    
    # Visualization
    plt.figure(figsize=(10, 6))
    plt.hist(ratios, bins=np.arange(0, 4, 0.2), alpha=0.7, color='#343a40', label=f'Raw Spikes (n={len(ratios)})')
    plt.axvline(median_val, color='#343a40', linestyle='dashed', linewidth=2, label=f'Median: {median_val:.2f}')
    
    phi = 1.618
    plt.axvline(phi, color='#fcc419', linestyle='solid', linewidth=3, label=r'Golden Ratio ($\phi$) = 1.618')
    
    plt.title('Distribution of Phase Ratios (Discharge / Charge) in Raw EEG Spikes')
    plt.xlabel('Ratio (Release Duration / Accumulation Duration)')
    plt.ylabel('Number of Neural Spikes')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_file = os.path.join(os.path.dirname(__file__), 'raw_brain_ratios.png')
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")

if __name__ == "__main__":
    main()

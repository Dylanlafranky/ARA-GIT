import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, filtfilt
import neurokit2 as nk
import os

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def analyze_eeg_delta():
    print("Fetching real human EEG dataset (MNE Sample) via neurokit2...")
    # Load real EEG data (200Hz, 1 minute)
    # This returns an MNE Raw object
    raw = nk.data("eeg_1min_200hz")
    
    # Extract the first EEG channel
    eeg_data = raw.get_data(picks='eeg')[0]
    fs = 200
    
    print(f"Loaded {len(eeg_data)} samples of real EEG data at {fs}Hz.")
    
    # 1. Isolate Delta Band (0.5 - 4 Hz)
    print("Filtering for Delta band (0.5 - 4.0 Hz)...")
    delta_wave = bandpass_filter(eeg_data, 0.5, 4.0, fs, order=3)
    
    # 2. Find Peaks (Voltage build-up complete)
    # At 200Hz, 0.25s = 50 samples, 2s = 400 samples.
    # We set distance to 40.
    peaks, _ = find_peaks(delta_wave, distance=40)
    
    # 3. Find Troughs (Voltage discharge complete)
    inv_delta = -delta_wave
    troughs, _ = find_peaks(inv_delta, distance=40)
    
    print(f"Identified {len(peaks)} peaks and {len(troughs)} troughs in the Delta band.")
    
    ratios = []
    
    # 4. Calculate accumulation (rise) and release (fall) phases
    for p_idx in peaks:
        # Trough before peak = voltage build-up
        prev_troughs = troughs[troughs < p_idx]
        if len(prev_troughs) == 0:
            continue
        min_before_idx = prev_troughs[-1]
        
        # Trough after peak = voltage discharge
        next_troughs = troughs[troughs > p_idx]
        if len(next_troughs) == 0:
            continue
        min_after_idx = next_troughs[0]
        
        # Duration in samples
        t_rise = p_idx - min_before_idx 
        t_fall = min_after_idx - p_idx
        
        if t_rise > 0 and t_fall > 0:
            # We are testing if the discharge takes longer than the build-up (or vice versa)
            # Most neural oscillations are asymmetric.
            ratio = t_fall / t_rise
            # Filter outliers
            if 0.1 < ratio < 10:
                ratios.append(ratio)
                
    print(f"Calculated ratios for {len(ratios)} delta micro-cycles.")
    return ratios

def main():
    ratios = analyze_eeg_delta()
    
    if not ratios:
        print("No valid cycles found. Dataset might be too short.")
        return
        
    mean_val = np.mean(ratios)
    median_val = np.median(ratios)
    
    print(f"EEG Delta Waves - Mean Ratio (T_fall / T_rise): {mean_val:.3f}")
    print(f"EEG Delta Waves - Median Ratio: {median_val:.3f}")
    
    # Visualization
    plt.figure(figsize=(10, 6))
    plt.hist(ratios, bins=np.arange(0, 4, 0.1), alpha=0.7, color='#7048e8', label=f'Delta Cycles (n={len(ratios)})')
    plt.axvline(median_val, color='#7048e8', linestyle='dashed', linewidth=2, label=f'Median: {median_val:.2f}')
    
    phi = 1.618
    plt.axvline(phi, color='#fcc419', linestyle='solid', linewidth=3, label=r'Golden Ratio ($\phi$) = 1.618')
    
    plt.title('Distribution of Phase Ratios (Fall Time / Rise Time) in EEG Delta Waves')
    plt.xlabel('Ratio (Release Duration / Accumulation Duration)')
    plt.ylabel('Number of Micro-Pulses')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_file = os.path.join(os.path.dirname(__file__), 'eeg_ratios.png')
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")

if __name__ == "__main__":
    main()

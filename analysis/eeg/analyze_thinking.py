import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, filtfilt
from scipy.interpolate import interp1d
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

def analyze_thinking_waves():
    print("Fetching real human EEG dataset (MNE Sample)...")
    raw = nk.data("eeg_1min_200hz")
    eeg_data = raw.get_data(picks='eeg')[0]
    fs = 200
    
    # 1. Isolate Beta Band (13 - 30 Hz) - The "Thinking" Waves
    print("Filtering for Beta band (13.0 - 30.0 Hz)...")
    beta_wave_raw = bandpass_filter(eeg_data, 13.0, 30.0, fs, order=4)
    
    # 2. UP-SAMPLING (Interpolation) for High Resolution
    # At 200Hz, we only have ~10 samples per cycle, which creates a "Quantization Wall" at Ratio=1.0.
    # We up-sample to 2000Hz to see the sub-sample asymmetry.
    print("Up-sampling to 2000Hz for high-resolution peak detection...")
    upsampled_fs = 2000
    x = np.arange(len(beta_wave_raw))
    x_new = np.linspace(0, len(beta_wave_raw)-1, len(beta_wave_raw) * (upsampled_fs // fs))
    f = interp1d(x, beta_wave_raw, kind='cubic')
    beta_wave = f(x_new)
    
    # 3. Find Peaks
    # At 2000Hz, a 20Hz wave has a period of 100 samples. 
    # This gives us the resolution to see 62/38 splits ($\phi$).
    peaks, _ = find_peaks(beta_wave, distance=30)
    
    # 4. Find Troughs
    inv_beta = -beta_wave
    troughs, _ = find_peaks(inv_beta, distance=30)
    
    print(f"Identified {len(peaks)} Beta peaks and {len(troughs)} troughs.")
    
    ratios = []
    
    # 4. Calculate Asymmetry
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
            # We calculate Fall / Rise to find the asymmetry signature
            ratio = t_fall / t_rise
            if 0.1 < ratio < 10:
                ratios.append(ratio)
                
    print(f"Calculated ratios for {len(ratios)} thinking (beta) micro-cycles.")
    return ratios

def main():
    ratios = analyze_thinking_waves()
    
    if not ratios:
        print("No valid cycles found.")
        return
        
    mean_val = np.mean(ratios)
    median_val = np.median(ratios)
    
    print(f"Thinking Waves (Beta) - Mean Ratio: {mean_val:.3f}")
    print(f"Thinking Waves (Beta) - Median Ratio: {median_val:.3f}")
    
    # Visualization
    plt.figure(figsize=(10, 6))
    plt.hist(ratios, bins=np.arange(0, 4, 0.1), alpha=0.7, color='#e64980', label=f'Beta Cycles (n={len(ratios)})')
    plt.axvline(median_val, color='#e64980', linestyle='dashed', linewidth=2, label=f'Median: {median_val:.2f}')
    
    phi = 1.618
    plt.axvline(phi, color='#fcc419', linestyle='solid', linewidth=3, label=r'Golden Ratio ($\phi$) = 1.618')
    
    plt.title('Distribution of Phase Ratios (Fall / Rise) in "Thinking" Beta Waves')
    plt.xlabel('Ratio (Release Duration / Accumulation Duration)')
    plt.ylabel('Number of Micro-Pulses')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_file = os.path.join(os.path.dirname(__file__), 'thinking_ratios.png')
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")

if __name__ == "__main__":
    main()

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, savgol_filter
import os

TICKER = "BTC-USD"
# Maximum allowable history for 1h data in yfinance is 730 days (~2 years)
PERIOD = "730d"
INTERVAL = "1h"

def fetch_crypto_data():
    print(f"Fetching {PERIOD} of {INTERVAL} data for {TICKER} from Yahoo Finance...")
    data = yf.download(TICKER, period=PERIOD, interval=INTERVAL, progress=False)
    
    if data.empty:
        print("Failed to download data.")
        return pd.Series()
        
    # Depending on yfinance version, 'Close' might be a Series or DataFrame with MultiIndex
    if isinstance(data.columns, pd.MultiIndex):
        close_prices = data['Close'][TICKER]
    else:
        close_prices = data['Close']
        
    # Drop any NaNs
    close_prices = close_prices.dropna()
    print(f"Successfully downloaded {len(close_prices)} data points.")
    return close_prices

def analyze_market_cycles(prices):
    # 1. Smoothing
    # Apply a Savitzky-Golay filter to smooth out 1-hour noise spikes
    # Window length of 49 hours (~2 days) to capture meaningful micro-cycles
    window_length = 49
    if window_length % 2 == 0:
        window_length += 1
        
    smoothed_prices = savgol_filter(prices.values, window_length, polyorder=3)
    smoothed_series = pd.Series(smoothed_prices, index=prices.index)
    
    # 2. Find Peaks and Troughs
    # We want cycles that last at least a few days. Distance = 72 hours (3 days)
    # We want micro-cycles that represent at least a 2% price swing
    prominence = smoothed_series.mean() * 0.02
        
    peaks, _ = find_peaks(smoothed_prices, distance=72, prominence=prominence)
    
    # Invert to find troughs
    inv_prices = -smoothed_prices
    troughs, _ = find_peaks(inv_prices, distance=72, prominence=prominence)
    
    print(f"Identified {len(peaks)} bull peaks and {len(troughs)} bear troughs.")
    
    ratios = []
    
    # 3. Calculate Phases
    for p_idx in peaks:
        # Find the trough immediately preceding this peak (start of accumulation)
        prev_troughs = troughs[troughs < p_idx]
        if len(prev_troughs) == 0:
            continue
        trough_before_idx = prev_troughs[-1]
        
        # Find the trough immediately following this peak (end of release)
        next_troughs = troughs[troughs > p_idx]
        if len(next_troughs) == 0:
            continue
        trough_after_idx = next_troughs[0]
        
        t_rise = p_idx - trough_before_idx # Duration of bull phase
        t_fall = trough_after_idx - p_idx # Duration of bear phase
        
        if t_rise > 0 and t_fall > 0:
            # We measure Ratio = T_rise (Accumulation) / T_fall (Release)
            # Typically markets take "stairs up, elevator down", so T_rise > T_fall.
            ratio = t_rise / t_fall
            
            # Filter out absurd outliers caused by flatlining or glitches
            if ratio < 15 and ratio > 0.05:
                ratios.append(ratio)
                
    print(f"Calculated ratios for {len(ratios)} continuous market micro-cycles.")
    return ratios

def main():
    prices = fetch_crypto_data()
    if prices.empty:
        return
        
    ratios = analyze_market_cycles(prices)
    
    if not ratios:
        print("Not enough cycles found.")
        return
        
    # Statistics
    mean_val = np.mean(ratios)
    median_val = np.median(ratios)
    
    print(f"{TICKER} - Mean Ratio (T_rise / T_fall): {mean_val:.3f}")
    print(f"{TICKER} - Median Ratio: {median_val:.3f}")
    
    # Statistical Plot
    plt.figure(figsize=(10, 6))
    plt.hist(ratios, bins=np.arange(0, 5, 0.2), alpha=0.7, color='#f7931a', label=f'{TICKER} (n={len(ratios)})')
    plt.axvline(median_val, color='#f7931a', linestyle='dashed', linewidth=2, label=f'Median: {median_val:.2f}')
    
    # Plot Phi
    phi = 1.618
    plt.axvline(phi, color='#228be6', linestyle='solid', linewidth=3, label=r'Golden Ratio ($\phi$) = 1.618')
    
    plt.title(f'Distribution of Bull/Bear Phase Ratios (T_rise / T_fall) for {TICKER}')
    plt.xlabel('Ratio (Accumulation Duration / Release Duration)')
    plt.ylabel('Number of Micro-Cycles')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_file = os.path.join(os.path.dirname(__file__), 'crypto_ratios.png')
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")

if __name__ == "__main__":
    main()

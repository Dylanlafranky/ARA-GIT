"""
Comprehensive EEG phi Analysis - All Wave Bands
================================================
Tests the system-mapping hypothesis:
  In healthy self-organising systems the accumulation-to-release
  phase ratio converges on phi = 1.618... (golden ratio).

The system mapping (game-engine formula) predicts:
  * The peak (maximum activity) sits at position 1-phi^-1 = 0.382
    within each cycle.
  * Therefore T_fall / T_rise = 0.618 / 0.382 = phi.

Two complementary methods are applied:

  METHOD A - Cycle asymmetry (raw spike / broadband approach)
    Applied to: Broad band (0.5-80 Hz, high-pass only).
    Detects prominent transient events; measures rise vs fall duration.
    Best for impulse-like neural discharges.

  METHOD B - Amplitude envelope dynamics (Hilbert-transform approach)
    Applied to: Delta, Theta, Alpha, Beta, Gamma.
    Extracts the power-envelope of each frequency band via Hilbert
    transform, then finds burst onset (trough->peak) and burst offset
    (peak->trough) durations.
    Best for rhythmic oscillatory activity (the correct measure of
    "accumulation / release" for sinusoidal brain waves).

All 60 EEG/EOG channels are included.  Ratios are pooled across
channels and every detected event.

Output:
  all_bands_phi_analysis.png
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.signal import butter, filtfilt, find_peaks, hilbert
from scipy.interpolate import interp1d
from scipy import stats
import neurokit2 as nk
import os, warnings
warnings.filterwarnings("ignore")

PHI       = (1 + np.sqrt(5)) / 2   # 1.61803...
PHI_INV   = 1 / PHI                 # 0.61803...
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Band definitions
# ---------------------------------------------------------------------------
ENVELOPE_BANDS = {
    "Delta" : (0.5,  4.0),
    "Theta" : (4.0,  8.0),
    "Alpha" : (8.0, 13.0),
    "Beta"  : (13.0, 30.0),
    "Gamma" : (30.0, 80.0),
}

COLORS = {
    "Delta"  : "#7048e8",
    "Theta"  : "#1c7ed6",
    "Alpha"  : "#2f9e44",
    "Beta"   : "#e64980",
    "Gamma"  : "#f76707",
    "Broad"  : "#343a40",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def bandpass_filter(data, lo, hi, fs, order=4):
    nyq  = 0.5 * fs
    lo_n = max(lo / nyq, 1e-4)
    hi_n = min(hi / nyq, 0.9999)
    b, a = butter(order, [lo_n, hi_n], btype="band")
    return filtfilt(b, a, data)


def highpass_filter(data, lo, fs, order=3):
    nyq  = 0.5 * fs
    lo_n = max(lo / nyq, 1e-4)
    b, a = butter(order, lo_n, btype="high")
    return filtfilt(b, a, data)


# ---------------------------------------------------------------------------
# Method A: cycle asymmetry on broadband / raw spikes
# (identical logic to analyze_raw_brain.py, extended to all channels)
# ---------------------------------------------------------------------------
def method_a_broad(eeg_matrix, fs):
    """
    High-pass only (0.5 Hz), detect prominent transient spikes,
    measure T_fall / T_rise per spike.
    Returns list of ratios pooled across all channels.
    """
    all_ratios = []
    noise_std_all = []

    for ch in range(eeg_matrix.shape[0]):
        raw = highpass_filter(eeg_matrix[ch], 0.5, fs)
        noise_std_all.append(np.std(raw))

    # Per-channel detection with a consistent prominence threshold
    for ch in range(eeg_matrix.shape[0]):
        raw = highpass_filter(eeg_matrix[ch], 0.5, fs)
        prom = np.std(raw) * 0.5
        peaks,   _ = find_peaks( raw, distance=5, prominence=prom)
        troughs, _ = find_peaks(-raw, distance=5, prominence=prom)

        for p in peaks:
            prev_t = troughs[troughs < p]
            next_t = troughs[troughs > p]
            if len(prev_t) == 0 or len(next_t) == 0:
                continue
            t_rise = p - prev_t[-1]
            t_fall = next_t[0] - p
            if t_rise > 0 and t_fall > 0:
                r = t_fall / t_rise
                if 0.2 < r < 5.0:
                    all_ratios.append(r)

    return all_ratios


# ---------------------------------------------------------------------------
# Method B: amplitude envelope dynamics via Hilbert transform
# ---------------------------------------------------------------------------
def method_b_envelope(eeg_matrix, fs, band_name):
    """
    For one frequency band:
      1. Bandpass filter.
      2. Hilbert transform -> amplitude envelope.
      3. Smooth the envelope (low-pass at 1/4 of the band centre).
      4. Find local envelope peaks (burst peaks) and troughs (inter-burst).
      5. For each burst peak: T_rise = peak - preceding trough,
                              T_fall = following trough - peak.
      6. Collect ratio = T_fall / T_rise across all channels.
    """
    lo, hi   = ENVELOPE_BANDS[band_name]
    centre   = (lo + hi) / 2.0
    smooth_lo = max(centre * 0.2, 0.1)   # smoothing LP cutoff

    all_ratios = []

    for ch in range(eeg_matrix.shape[0]):
        # 1. Band-pass
        filtered = bandpass_filter(eeg_matrix[ch], lo, hi, fs)

        # 2. Amplitude envelope
        analytic  = hilbert(filtered)
        envelope  = np.abs(analytic)

        # 3. Smooth the envelope (removes individual cycle ripple)
        nyq  = 0.5 * fs
        lp_n = min(smooth_lo / nyq, 0.49)
        b, a = butter(3, lp_n, btype="low")
        smooth_env = filtfilt(b, a, envelope)

        # 4. Peak detection on smoothed envelope
        # min distance: one full cycle of the band centre
        min_dist = max(int(fs / hi), 2)

        peaks,   _ = find_peaks(smooth_env,  distance=min_dist,
                                 prominence=np.std(smooth_env) * 0.3)
        troughs, _ = find_peaks(-smooth_env, distance=min_dist,
                                 prominence=np.std(smooth_env) * 0.3)

        # 5. Rise / fall per burst
        for p in peaks:
            prev_t = troughs[troughs < p]
            next_t = troughs[troughs > p]
            if len(prev_t) == 0 or len(next_t) == 0:
                continue
            t_rise = p - prev_t[-1]
            t_fall = next_t[0] - p
            if t_rise > 0 and t_fall > 0:
                r = t_fall / t_rise
                if 0.1 < r < 10.0:
                    all_ratios.append(r)

    return all_ratios


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------
def band_stats(ratios):
    if len(ratios) < 5:
        return dict(n=len(ratios), mean=np.nan, median=np.nan,
                    std=np.nan, phi_dev=np.nan, t_stat=np.nan, p_val=np.nan,
                    phi_dev_pct=np.nan)
    arr  = np.array(ratios)
    med  = np.median(arr)
    mn   = np.mean(arr)
    sd   = np.std(arr, ddof=1)
    t, p = stats.ttest_1samp(arr, PHI)
    dev  = abs(med - PHI)
    pct  = dev / PHI * 100
    return dict(n=len(arr), mean=mn, median=med, std=sd,
                phi_dev=dev, phi_dev_pct=pct, t_stat=t, p_val=p)


# ---------------------------------------------------------------------------
# Visualisation
# ---------------------------------------------------------------------------
def plot_results(results_envelope, results_broad):
    """
    Top section: one histogram per envelope band (5 bands x 1 column).
    Bottom row: broadband cycle-asymmetry + summary deviation bar chart.
    """
    band_names = list(ENVELOPE_BANDS.keys())
    n_bands    = len(band_names)

    fig = plt.figure(figsize=(22, 30), facecolor="#f8f9fa")
    fig.suptitle(
        "Brain Wave Phase Ratios vs. Golden Ratio (phi = 1.618)\n"
        "All EEG Channels  |  MNE Sample Dataset (60 s, 200 Hz)\n"
        "Top 5 bands: Amplitude Envelope Burst Analysis (Hilbert method)\n"
        "Bottom-left: Broadband Raw Spike Asymmetry",
        fontsize=14, fontweight="bold", y=0.995
    )

    gs = gridspec.GridSpec(
        n_bands + 1, 2,
        figure=fig,
        hspace=0.60, wspace=0.35,
        left=0.07, right=0.97,
        top=0.965, bottom=0.03
    )

    # -- Envelope bands --
    for row, name in enumerate(band_names):
        ratios = results_envelope[name]["ratios"]
        st     = results_envelope[name]["stats"]
        color  = COLORS[name]
        lo, hi = ENVELOPE_BANDS[name]

        ax = fig.add_subplot(gs[row, 0])
        if len(ratios) >= 5:
            arr  = np.array(ratios)
            lo_b = max(0.1, np.percentile(arr, 1))
            hi_b = min(8.0, np.percentile(arr, 99))
            bins = np.linspace(lo_b, hi_b, 60)
            ax.hist(arr, bins=bins, color=color, alpha=0.65,
                    label=f"n = {st['n']:,}")
            ax.axvline(st["median"], color=color, linestyle="--",
                       linewidth=2.5,
                       label=f"Median = {st['median']:.3f}")
            ax.axvline(PHI, color="#fcc419", linestyle="-",
                       linewidth=3,
                       label=f"phi = {PHI:.3f}")
        else:
            ax.text(0.5, 0.5, "Insufficient data",
                    ha="center", va="center", transform=ax.transAxes)

        ax.set_title(
            f"{name} Band  ({lo}-{hi} Hz) — Envelope Burst Rise/Fall",
            fontsize=11, fontweight="bold"
        )
        ax.set_xlabel("T_fall / T_rise   (release / accumulation)")
        ax.set_ylabel("Burst Count")
        ax.legend(fontsize=8)
        ax.set_facecolor("#ffffff")
        ax.grid(True, alpha=0.25)

        # Stats panel (right column)
        ax_info = fig.add_subplot(gs[row, 1])
        ax_info.axis("off")
        pct_s = f"{st['phi_dev_pct']:.2f}%" if not np.isnan(st["phi_dev_pct"]) else "N/A"
        verdict = (
            "PASS: Median ~ phi  (within 5%)"
            if (not np.isnan(st["phi_dev_pct"]) and st["phi_dev_pct"] < 5)
            else (
                "NEAR: Median near phi  (5-15%)"
                if (not np.isnan(st["phi_dev_pct"]) and st["phi_dev_pct"] < 15)
                else "DIFF: Median differs from phi"
            )
        )
        lines = [
            f"  Band:          {name}  ({lo}-{hi} Hz)",
            f"  Method:        Amplitude envelope burst",
            f"  Bursts (n):    {st['n']:,}",
            f"  Mean:          {st['mean']:.4f}",
            f"  Median:        {st['median']:.4f}",
            f"  Std Dev:       {st['std']:.4f}",
            "",
            f"  phi =          {PHI:.4f}",
            f"  |Median - phi|:{st['phi_dev']:.4f}  ({pct_s})",
            "",
            f"  t-stat vs phi: {st['t_stat']:.3f}",
            f"  p-value:       {st['p_val']:.4g}",
            "",
            f"  >> {verdict}",
        ]
        ax_info.text(
            0.03, 0.97, "\n".join(lines),
            transform=ax_info.transAxes,
            fontsize=8.5, fontfamily="monospace",
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.5",
                      facecolor="#ffffff",
                      edgecolor=color, linewidth=2)
        )

    # -- Broadband spike row (left) --
    ax_broad = fig.add_subplot(gs[n_bands, 0])
    broad_r  = results_broad["ratios"]
    broad_st = results_broad["stats"]

    if len(broad_r) >= 5:
        arr  = np.array(broad_r)
        bins = np.linspace(max(0.2, np.percentile(arr,1)),
                           min(5.0, np.percentile(arr,99)), 60)
        ax_broad.hist(arr, bins=bins, color=COLORS["Broad"], alpha=0.7,
                      label=f"n = {broad_st['n']:,}")
        ax_broad.axvline(broad_st["median"], color=COLORS["Broad"],
                         linestyle="--", linewidth=2.5,
                         label=f"Median = {broad_st['median']:.3f}")
        ax_broad.axvline(broad_st["mean"], color="#868e96",
                         linestyle=":", linewidth=2,
                         label=f"Mean = {broad_st['mean']:.3f}")
        ax_broad.axvline(PHI, color="#fcc419", linestyle="-",
                         linewidth=3, label=f"phi = {PHI:.3f}")

    ax_broad.set_title(
        "Broadband Raw Spikes (0.5 Hz high-pass) — Cycle Asymmetry",
        fontsize=11, fontweight="bold"
    )
    ax_broad.set_xlabel("T_fall / T_rise   (release / accumulation)")
    ax_broad.set_ylabel("Spike Count")
    ax_broad.legend(fontsize=8)
    ax_broad.set_facecolor("#ffffff")
    ax_broad.grid(True, alpha=0.25)

    # -- Summary deviation bar chart (right) --
    ax_sum = fig.add_subplot(gs[n_bands, 1])

    all_band_names   = band_names + ["Broad"]
    all_band_stats   = [results_envelope[n]["stats"] for n in band_names] + [broad_st]
    devs_pct = [
        (s["phi_dev_pct"] if not np.isnan(s["phi_dev_pct"]) else 0)
        for s in all_band_stats
    ]
    bar_colors = [COLORS[n] for n in all_band_names]

    bars = ax_sum.bar(all_band_names, devs_pct,
                      color=bar_colors, alpha=0.85,
                      edgecolor="white", linewidth=1.5)
    ax_sum.axhline(5,  color="#fab005", linestyle="--", linewidth=1.5,
                   label="5% (near phi)")
    ax_sum.axhline(15, color="#e03131", linestyle="--", linewidth=1.5,
                   label="15% (outer limit)")

    for bar, pct in zip(bars, devs_pct):
        ax_sum.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.2,
            f"{pct:.1f}%",
            ha="center", va="bottom",
            fontsize=9, fontweight="bold"
        )

    ax_sum.set_title(
        "Distance from phi by Band  (lower = closer to phi)",
        fontsize=11, fontweight="bold"
    )
    ax_sum.set_ylabel("|Median - phi| / phi  (%)")
    ax_sum.set_xlabel("Wave Band / Method")
    ax_sum.legend(fontsize=9)
    ax_sum.set_facecolor("#ffffff")
    ax_sum.grid(True, axis="y", alpha=0.3)

    out = os.path.join(OUTPUT_DIR, "all_bands_phi_analysis.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"\n[SAVED]  {out}")
    return out


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------
def print_summary(results_envelope, results_broad):
    print("\n" + "=" * 72)
    print(f"  EEG BRAIN WAVE vs phi ANALYSIS  |  phi = {PHI:.6f}")
    print(f"  System mapping prediction: T_fall/T_rise = phi")
    print("=" * 72)
    header = f"  {'Band':<8}  {'Method':<18}  {'n':>7}  {'Median':>8}  " \
             f"{'Mean':>8}  {'|Dev|%':>8}  {'p-val':>10}"
    print(header)
    print("-" * 72)

    for name in list(ENVELOPE_BANDS.keys()):
        st = results_envelope[name]["stats"]
        pct = f"{st['phi_dev_pct']:.2f}%" if not np.isnan(st["phi_dev_pct"]) else "N/A"
        flag = ""
        if not np.isnan(st["phi_dev_pct"]):
            flag = ("<<< near phi" if st["phi_dev_pct"] < 5 else
                    ("< within 15%" if st["phi_dev_pct"] < 15 else ""))
        print(f"  {name:<8}  {'Env burst':<18}  {st['n']:>7,}  "
              f"{st['median']:>8.4f}  {st['mean']:>8.4f}  "
              f"{pct:>8}  {st['p_val']:>10.4g}  {flag}")

    # Broadband
    st = results_broad["stats"]
    pct = f"{st['phi_dev_pct']:.2f}%" if not np.isnan(st["phi_dev_pct"]) else "N/A"
    flag = ("<<< near phi" if st["phi_dev_pct"] < 5 else
            ("< within 15%" if st["phi_dev_pct"] < 15 else ""))
    print(f"  {'Broad':<8}  {'Cycle asymmetry':<18}  {st['n']:>7,}  "
          f"{st['median']:>8.4f}  {st['mean']:>8.4f}  "
          f"{pct:>8}  {st['p_val']:>10.4g}  {flag}")
    print("=" * 72)
    print(f"  phi = {PHI:.6f} (system-mapping target)")
    print("=" * 72)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Loading EEG dataset (MNE Sample — 200 Hz, 60 s) ...")
    raw = nk.data("eeg_1min_200hz")
    raw_eeg = raw.copy().pick("eeg")
    eeg_matrix = raw_eeg.get_data()     # (n_channels, 12000)
    fs = raw_eeg.info["sfreq"]
    n_ch = eeg_matrix.shape[0]
    print(f"  Channels: {n_ch}  |  Samples: {eeg_matrix.shape[1]}  |  fs: {fs} Hz")

    # -- Method B: envelope burst analysis per band --
    results_envelope = {}
    for name in ENVELOPE_BANDS:
        lo, hi = ENVELOPE_BANDS[name]
        print(f"  Envelope [{name}] {lo}-{hi} Hz ...", end="  ", flush=True)
        ratios = method_b_envelope(eeg_matrix, fs, name)
        st     = band_stats(ratios)
        results_envelope[name] = {"ratios": ratios, "stats": st}
        pct = f"{st['phi_dev_pct']:.2f}%" if not np.isnan(st["phi_dev_pct"]) else "N/A"
        print(f"n={st['n']:,}  median={st['median']:.4f}  |dev%|={pct}")

    # -- Method A: broadband cycle asymmetry --
    print(f"  Cycle-asymmetry [Broad] 0.5-80 Hz ...", end="  ", flush=True)
    broad_ratios = method_a_broad(eeg_matrix, fs)
    broad_st     = band_stats(broad_ratios)
    results_broad = {"ratios": broad_ratios, "stats": broad_st}
    pct = f"{broad_st['phi_dev_pct']:.2f}%" if not np.isnan(broad_st["phi_dev_pct"]) else "N/A"
    print(f"n={broad_st['n']:,}  median={broad_st['median']:.4f}  |dev%|={pct}")

    print_summary(results_envelope, results_broad)
    plot_results(results_envelope, results_broad)
    print("\nDone.")
    return results_envelope, results_broad


if __name__ == "__main__":
    main()

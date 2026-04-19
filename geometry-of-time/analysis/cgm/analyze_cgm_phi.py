"""
Blood Glucose CGM phi Analysis
=================================
Tests the system-mapping hypothesis:
  In healthy self-organising glucose regulation, the insulin-driven
  clearance time (T_fall) relative to the post-meal absorption time
  (T_rise) converges on phi = 1.618...

  Healthy individuals --> T_fall / T_rise --> phi
  T1D patients (dysregulated) --> deviates from phi

Data sources (all real, no simulated data):
  Healthy : Big Ideas Lab Glycemic Variability Dataset v1.1.2
            (PhysioNet)  n=16 subjects, Dexcom G6, mg/dL
            HbA1c 5.3-6.4  (non-diabetic range)
  T1D     : D1NAMO Dataset (Zenodo 5651217)
            n=9 subjects, FreeStyle CGM, mmol/L

Method:
  1. Load CGM time series (EGV rows only)
  2. Resample to uniform 5-minute grid; interpolate short gaps (<=30 min)
  3. Light smoothing: rolling mean, window=3 (15 min)
  4. Find local glucose PEAKS (meal response peaks)
       min_distance = 24 samples (2 h at 5 min/sample)
       prominence  >= 0.35 * signal std (filters sensor noise & tiny ripples)
  5. Find local TROUGHS in the same way
  6. For each peak:
       T_rise = peak_idx - preceding_trough_idx
       T_fall = following_trough_idx - peak_idx
       Keep only if T_rise >= 3 samples (15 min) and T_fall >= 3 samples
       Keep only if glucose amplitude (peak - lower trough) >= threshold
  7. ratio = T_fall / T_rise
  8. Filter 0.2 < ratio < 8 (physiologically implausible outliers removed)
  9. Collect per-subject and pool across cohort
 10. Primary statistic: MEDIAN (robust to outliers per user specification)
"""

import os, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.signal import find_peaks
from scipy import stats

warnings.filterwarnings("ignore")

PHI      = (1 + np.sqrt(5)) / 2   # 1.61803...
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BI_DIR   = os.path.join(BASE_DIR, "healthy_bigideas")
T1D_DIR  = os.path.join(BASE_DIR, "t1d")

# HbA1c values from Big Ideas Lab Demographics.csv
BI_HBA1C = {
    "001": 5.5, "002": 5.6, "003": 5.9, "004": 6.4,
    "005": 5.7, "006": 5.8, "007": 5.3, "008": 5.6,
    "009": 6.1, "010": 6.0, "011": 6.0, "012": 5.6,
    "013": 5.7, "014": 5.5, "015": 5.5, "016": 5.5,
}


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

def load_bigideas(sid):
    """Load Big Ideas Lab Dexcom CSV -> (timestamps, glucose_mg_dL)"""
    path = os.path.join(BI_DIR, f"Dexcom_{sid}.csv")
    df   = pd.read_csv(path, low_memory=False)
    egv  = df[df["Event Type"] == "EGV"].copy()
    egv["ts"] = pd.to_datetime(egv["Timestamp (YYYY-MM-DDThh:mm:ss)"],
                                errors="coerce")
    egv["glucose"] = pd.to_numeric(egv["Glucose Value (mg/dL)"],
                                    errors="coerce")
    egv = egv.dropna(subset=["ts", "glucose"])
    egv = egv.set_index("ts").sort_index()
    return egv["glucose"]


def load_t1d(sid):
    """Load D1NAMO T1D glucose CSV -> (timestamps, glucose_mmol_L)"""
    path = os.path.join(T1D_DIR, f"glucose_{sid}.csv")
    df   = pd.read_csv(path)
    cgm  = df[df["type"] == "cgm"].copy()
    cgm["ts"] = pd.to_datetime(cgm["date"] + " " + cgm["time"],
                                errors="coerce")
    cgm["glucose"] = pd.to_numeric(cgm["glucose"], errors="coerce")
    cgm = cgm.dropna(subset=["ts", "glucose"])
    cgm = cgm.set_index("ts").sort_index()
    return cgm["glucose"]


def preprocess(series, freq_min=5, max_gap_min=30):
    """
    Resample to uniform freq_min grid, interpolate gaps <= max_gap_min,
    then apply rolling-mean smoothing (window = 3 samples = 15 min).
    Returns cleaned numpy array.
    """
    freq = f"{freq_min}min"
    # Re-index to uniform grid
    idx  = pd.date_range(series.index[0].floor(freq),
                         series.index[-1].ceil(freq),
                         freq=freq)
    s = series.reindex(series.index.union(idx)).sort_index()
    # Interpolate short gaps only
    max_gap_samples = max_gap_min // freq_min
    s = s.interpolate(method="time", limit=max_gap_samples)
    s = s.reindex(idx)
    # Rolling mean smoothing
    smoothed = s.rolling(window=3, center=True, min_periods=2).mean()
    return smoothed.values


# ---------------------------------------------------------------------------
# Core ratio analysis
# ---------------------------------------------------------------------------

def compute_ratios(signal, min_amplitude_pct=0.15):
    """
    Detect meal-response peaks and compute T_fall / T_rise per cycle.

    min_amplitude_pct : fraction of signal std; filters small noise peaks.
    Returns list of (t_rise, t_fall, ratio) tuples.
    """
    s = signal[~np.isnan(signal)]
    if len(s) < 50:
        return []

    sig_std = np.nanstd(s)
    prominence_threshold = 0.35 * sig_std
    amplitude_threshold  = min_amplitude_pct * sig_std

    # Min distance = 24 samples = 2 hours at 5-min resolution
    # This ensures we capture full meal cycles, not intra-spike noise
    peaks,   _ = find_peaks( s, distance=24, prominence=prominence_threshold)
    troughs, _ = find_peaks(-s, distance=24, prominence=prominence_threshold)

    results = []
    for p in peaks:
        prev_t = troughs[troughs < p]
        next_t = troughs[troughs > p]
        if len(prev_t) == 0 or len(next_t) == 0:
            continue

        t_before = prev_t[-1]
        t_after  = next_t[0]
        t_rise = p - t_before
        t_fall = t_after - p

        # Require both phases to be at least 15 min (3 samples)
        if t_rise < 3 or t_fall < 3:
            continue

        # Require meaningful glucose amplitude
        lower_trough = min(s[t_before], s[t_after])
        amplitude = s[p] - lower_trough
        if amplitude < amplitude_threshold:
            continue

        ratio = t_fall / t_rise
        if 0.2 < ratio < 8.0:
            results.append((t_rise, t_fall, ratio))

    return results


# ---------------------------------------------------------------------------
# Process each cohort
# ---------------------------------------------------------------------------

def process_cohort_bigideas():
    all_ratios = []
    per_subject = {}
    for sid in sorted(os.listdir(BI_DIR)):
        if not sid.startswith("Dexcom_") or not sid.endswith(".csv"):
            continue
        subj = sid.replace("Dexcom_","").replace(".csv","")
        try:
            series  = load_bigideas(subj)
            cleaned = preprocess(series)
            results = compute_ratios(cleaned)
            ratios  = [r[2] for r in results]
            per_subject[subj] = {
                "n": len(ratios), "ratios": ratios,
                "hba1c": BI_HBA1C.get(subj, np.nan)
            }
            all_ratios.extend(ratios)
            if ratios:
                print(f"  BI {subj} HbA1c={BI_HBA1C.get(subj,'?')}:  "
                      f"n={len(ratios)}  median={np.median(ratios):.3f}")
        except Exception as e:
            print(f"  BI {subj} ERR: {e}")
    return all_ratios, per_subject


def process_cohort_t1d():
    all_ratios = []
    per_subject = {}
    for fname in sorted(os.listdir(T1D_DIR)):
        if not fname.startswith("glucose_") or not fname.endswith(".csv"):
            continue
        subj = fname.replace("glucose_","").replace(".csv","")
        try:
            series  = load_t1d(subj)
            cleaned = preprocess(series)
            results = compute_ratios(cleaned)
            ratios  = [r[2] for r in results]
            per_subject[subj] = {"n": len(ratios), "ratios": ratios}
            all_ratios.extend(ratios)
            if ratios:
                print(f"  T1D {subj}:  n={len(ratios)}  median={np.median(ratios):.3f}")
        except Exception as e:
            print(f"  T1D {subj} ERR: {e}")
    return all_ratios, per_subject


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def cohort_stats(ratios, label=""):
    if len(ratios) < 5:
        return {"n": len(ratios), "median": np.nan, "mean": np.nan,
                "std": np.nan, "phi_dev": np.nan, "phi_dev_pct": np.nan,
                "p_vs_phi": np.nan, "p_vs_other": np.nan}
    arr = np.array(ratios)
    med = np.median(arr)
    mn  = np.mean(arr)
    sd  = np.std(arr, ddof=1)
    t, p = stats.ttest_1samp(arr, PHI)
    dev  = abs(med - PHI)
    pct  = dev / PHI * 100
    return {"n": len(arr), "median": med, "mean": mn, "std": sd,
            "phi_dev": dev, "phi_dev_pct": pct, "p_vs_phi": p}


def mannwhitney(ratios_a, ratios_b):
    """Mann-Whitney U test between two ratio arrays."""
    if len(ratios_a) < 5 or len(ratios_b) < 5:
        return np.nan, np.nan
    stat, p = stats.mannwhitneyu(ratios_a, ratios_b, alternative="two-sided")
    return stat, p


# ---------------------------------------------------------------------------
# Visualisation
# ---------------------------------------------------------------------------

def plot_results(bi_ratios, t1d_ratios, bi_per_subj, t1d_per_subj,
                 st_bi, st_t1d):
    fig = plt.figure(figsize=(20, 22), facecolor="#f8f9fa")
    fig.suptitle(
        "Blood Glucose CGM Phase Ratio Analysis vs. Golden Ratio (phi = 1.618)\n"
        "Healthy: Big Ideas Lab (PhysioNet, n=16)  |  T1D: D1NAMO (Zenodo, n=9)\n"
        "Metric: T_fall / T_rise  per meal-response glucose cycle",
        fontsize=14, fontweight="bold", y=0.99
    )

    gs = gridspec.GridSpec(3, 2, figure=fig,
                           hspace=0.55, wspace=0.35,
                           left=0.07, right=0.97,
                           top=0.95, bottom=0.04)

    # ----- Row 0: Healthy distribution -----
    ax_h = fig.add_subplot(gs[0, 0])
    if len(bi_ratios) >= 5:
        arr = np.array(bi_ratios)
        bins = np.linspace(max(0.2, np.percentile(arr, 0.5)),
                           min(7.0, np.percentile(arr, 99.5)), 60)
        ax_h.hist(arr, bins=bins, color="#2f9e44", alpha=0.7,
                  label=f"n = {st_bi['n']:,} meal cycles")
        ax_h.axvline(st_bi["median"], color="#2f9e44", linestyle="--",
                     linewidth=2.5,
                     label=f"Median = {st_bi['median']:.3f}")
        ax_h.axvline(st_bi["mean"], color="#74c476", linestyle=":",
                     linewidth=2,
                     label=f"Mean = {st_bi['mean']:.3f}")
        ax_h.axvline(PHI, color="#fcc419", linestyle="-", linewidth=3,
                     label=f"phi = {PHI:.3f}")
    ax_h.set_title("Healthy Group — Big Ideas Lab (non-diabetic, HbA1c 5.3-6.4%)",
                   fontsize=11, fontweight="bold")
    ax_h.set_xlabel("T_fall / T_rise   (glucose clearance / absorption)")
    ax_h.set_ylabel("Meal Cycle Count")
    ax_h.legend(fontsize=8.5)
    ax_h.set_facecolor("#ffffff")
    ax_h.grid(True, alpha=0.25)

    # Stats box
    ax_hs = fig.add_subplot(gs[0, 1])
    ax_hs.axis("off")
    pct_s = f"{st_bi['phi_dev_pct']:.2f}%"
    verdict = ("PASS: Median ~ phi  (within 5%)"
               if st_bi["phi_dev_pct"] < 5 else
               ("NEAR: within 5-15%"
                if st_bi["phi_dev_pct"] < 15 else
                "DIFF: >15% from phi"))
    lines = [
        "  HEALTHY COHORT",
        "  Source: Big Ideas Lab / PhysioNet",
        "  Subjects: 16  |  HbA1c: 5.3-6.4%",
        f"  Meal cycles (n): {st_bi['n']:,}",
        "",
        f"  Median T_fall/T_rise: {st_bi['median']:.4f}",
        f"  Mean   T_fall/T_rise: {st_bi['mean']:.4f}",
        f"  Std Dev:              {st_bi['std']:.4f}",
        "",
        f"  phi =                 {PHI:.4f}",
        f"  |Median - phi|:       {st_bi['phi_dev']:.4f}  ({pct_s})",
        "",
        f"  t-test vs phi:  p = {st_bi['p_vs_phi']:.4g}",
        "",
        f"  >> {verdict}",
    ]
    ax_hs.text(0.03, 0.97, "\n".join(lines), transform=ax_hs.transAxes,
               fontsize=8.5, fontfamily="monospace", verticalalignment="top",
               bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff",
                         edgecolor="#2f9e44", linewidth=2))

    # ----- Row 1: T1D distribution -----
    ax_d = fig.add_subplot(gs[1, 0])
    if len(t1d_ratios) >= 5:
        arr = np.array(t1d_ratios)
        bins = np.linspace(max(0.2, np.percentile(arr, 0.5)),
                           min(7.0, np.percentile(arr, 99.5)), 60)
        ax_d.hist(arr, bins=bins, color="#e03131", alpha=0.7,
                  label=f"n = {st_t1d['n']:,} meal cycles")
        ax_d.axvline(st_t1d["median"], color="#e03131", linestyle="--",
                     linewidth=2.5,
                     label=f"Median = {st_t1d['median']:.3f}")
        ax_d.axvline(st_t1d["mean"], color="#ff8787", linestyle=":",
                     linewidth=2,
                     label=f"Mean = {st_t1d['mean']:.3f}")
        ax_d.axvline(PHI, color="#fcc419", linestyle="-", linewidth=3,
                     label=f"phi = {PHI:.3f}")
    ax_d.set_title("T1D Group — D1NAMO Dataset (Type 1 Diabetes)",
                   fontsize=11, fontweight="bold")
    ax_d.set_xlabel("T_fall / T_rise   (glucose clearance / absorption)")
    ax_d.set_ylabel("Meal Cycle Count")
    ax_d.legend(fontsize=8.5)
    ax_d.set_facecolor("#ffffff")
    ax_d.grid(True, alpha=0.25)

    # Stats box
    ax_ds = fig.add_subplot(gs[1, 1])
    ax_ds.axis("off")
    pct_d = f"{st_t1d['phi_dev_pct']:.2f}%"
    verdict_d = ("PASS: Median ~ phi  (within 5%)"
                 if st_t1d["phi_dev_pct"] < 5 else
                 ("NEAR: within 5-15%"
                  if st_t1d["phi_dev_pct"] < 15 else
                  "DIFF: >15% from phi"))
    lines_d = [
        "  T1D COHORT",
        "  Source: D1NAMO / Zenodo",
        "  Subjects: 9  |  Type 1 Diabetes",
        f"  Meal cycles (n): {st_t1d['n']:,}",
        "",
        f"  Median T_fall/T_rise: {st_t1d['median']:.4f}",
        f"  Mean   T_fall/T_rise: {st_t1d['mean']:.4f}",
        f"  Std Dev:              {st_t1d['std']:.4f}",
        "",
        f"  phi =                 {PHI:.4f}",
        f"  |Median - phi|:       {st_t1d['phi_dev']:.4f}  ({pct_d})",
        "",
        f"  t-test vs phi:  p = {st_t1d['p_vs_phi']:.4g}",
        "",
        f"  >> {verdict_d}",
    ]
    ax_ds.text(0.03, 0.97, "\n".join(lines_d), transform=ax_ds.transAxes,
               fontsize=8.5, fontfamily="monospace", verticalalignment="top",
               bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff",
                         edgecolor="#e03131", linewidth=2))

    # ----- Row 2: Overlay comparison + HbA1c gradient -----
    ax_ov = fig.add_subplot(gs[2, 0])
    if len(bi_ratios) >= 5 and len(t1d_ratios) >= 5:
        arr_h = np.array(bi_ratios)
        arr_d = np.array(t1d_ratios)
        lo = min(np.percentile(arr_h, 1), np.percentile(arr_d, 1), 0.3)
        hi = max(np.percentile(arr_h, 99), np.percentile(arr_d, 99), 5.0)
        bins = np.linspace(lo, hi, 55)
        ax_ov.hist(arr_h, bins=bins, color="#2f9e44", alpha=0.55,
                   label=f"Healthy (n={len(arr_h):,})", density=True)
        ax_ov.hist(arr_d, bins=bins, color="#e03131", alpha=0.55,
                   label=f"T1D (n={len(arr_d):,})", density=True)
        ax_ov.axvline(st_bi["median"],  color="#2f9e44", linestyle="--",
                      linewidth=2, label=f"H median = {st_bi['median']:.3f}")
        ax_ov.axvline(st_t1d["median"], color="#e03131", linestyle="--",
                      linewidth=2, label=f"T1D median = {st_t1d['median']:.3f}")
        ax_ov.axvline(PHI, color="#fcc419", linestyle="-", linewidth=3,
                      label=f"phi = {PHI:.3f}")

        # Mann-Whitney U result
        mw_stat, mw_p = mannwhitney(arr_h, arr_d)
        ax_ov.set_title(
            f"Overlay: Healthy vs T1D\n"
            f"Mann-Whitney U: p = {mw_p:.4g}  "
            f"(significant={'YES' if mw_p < 0.05 else 'NO'})",
            fontsize=11, fontweight="bold"
        )
    ax_ov.set_xlabel("T_fall / T_rise")
    ax_ov.set_ylabel("Probability Density")
    ax_ov.legend(fontsize=8)
    ax_ov.set_facecolor("#ffffff")
    ax_ov.grid(True, alpha=0.25)

    # HbA1c gradient: per-subject median vs HbA1c
    ax_g = fig.add_subplot(gs[2, 1])
    hba1c_vals, med_vals, n_vals = [], [], []
    for sid, info in bi_per_subj.items():
        if info["n"] >= 3:
            hba1c_vals.append(info["hba1c"])
            med_vals.append(np.median(info["ratios"]))
            n_vals.append(info["n"])

    if hba1c_vals:
        sc = ax_g.scatter(hba1c_vals, med_vals,
                          c=n_vals, cmap="YlOrRd_r",
                          s=120, edgecolors="black", linewidths=0.8,
                          zorder=3, label="Healthy subjects")
        plt.colorbar(sc, ax=ax_g, label="Meal cycles per subject")

        # Add T1D points (no HbA1c available - plot at 9.0 as placeholder)
        t1d_meds = [np.median(info["ratios"])
                    for info in t1d_per_subj.values()
                    if info["n"] >= 3]
        for m in t1d_meds:
            ax_g.scatter(9.0, m, c="#e03131", s=100, marker="^",
                         edgecolors="black", linewidths=0.8, zorder=3)
        ax_g.scatter([], [], c="#e03131", marker="^", s=100,
                     label="T1D subjects (HbA1c ~9+)")

        # Trend line for healthy subjects
        if len(hba1c_vals) >= 3:
            z = np.polyfit(hba1c_vals, med_vals, 1)
            p_line = np.poly1d(z)
            xs = np.linspace(min(hba1c_vals) - 0.1, max(hba1c_vals) + 0.1, 50)
            ax_g.plot(xs, p_line(xs), color="#555", linestyle="--",
                      linewidth=1.5, alpha=0.7, label="Trend (healthy)")
            corr, pval = stats.pearsonr(hba1c_vals, med_vals)
            ax_g.set_title(
                f"Per-Subject Median vs HbA1c\n"
                f"Pearson r = {corr:.3f}  p = {pval:.3g}",
                fontsize=11, fontweight="bold"
            )

        ax_g.axhline(PHI, color="#fcc419", linestyle="-", linewidth=2.5,
                     label=f"phi = {PHI:.3f}", zorder=2)
        ax_g.set_xlabel("HbA1c (%)")
        ax_g.set_ylabel("Median T_fall / T_rise")
        ax_g.legend(fontsize=8)
        ax_g.set_facecolor("#ffffff")
        ax_g.grid(True, alpha=0.25)

    out = os.path.join(BASE_DIR, "cgm_phi_analysis.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"\n[SAVED]  {out}")
    return out


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------

def print_summary(st_bi, st_t1d):
    mw_stat, mw_p = mannwhitney([], [])  # placeholder; computed in plot
    print("\n" + "=" * 65)
    print(f"  CGM GLUCOSE phi ANALYSIS  |  phi = {PHI:.6f}")
    print(f"  System mapping prediction: T_fall/T_rise = phi")
    print("=" * 65)
    print(f"  {'Cohort':<22} {'n':>6}  {'Median':>8}  {'Mean':>8}  "
          f"{'|Dev|%':>8}  {'p-phi':>10}")
    print("-" * 65)
    for label, st in [("Healthy (BI Lab)", st_bi), ("T1D (D1NAMO)", st_t1d)]:
        pct = f"{st['phi_dev_pct']:.2f}%" if not np.isnan(st["phi_dev_pct"]) else "N/A"
        flag = ("<<< ~ phi" if st["phi_dev_pct"] < 5 else
                ("< near phi" if st["phi_dev_pct"] < 15 else ""))
        print(f"  {label:<22} {st['n']:>6,}  {st['median']:>8.4f}  "
              f"{st['mean']:>8.4f}  {pct:>8}  {st['p_vs_phi']:>10.4g}  {flag}")
    print("=" * 65)
    print(f"  phi = {PHI:.6f}  (system-mapping target)")
    print("=" * 65)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== Big Ideas Lab (Healthy) ===")
    bi_ratios, bi_per_subj = process_cohort_bigideas()

    print("\n=== D1NAMO T1D ===")
    t1d_ratios, t1d_per_subj = process_cohort_t1d()

    st_bi  = cohort_stats(bi_ratios,  "Healthy")
    st_t1d = cohort_stats(t1d_ratios, "T1D")

    print_summary(st_bi, st_t1d)

    # Between-group test
    if len(bi_ratios) >= 5 and len(t1d_ratios) >= 5:
        mw_stat, mw_p = mannwhitney(bi_ratios, t1d_ratios)
        print(f"\n  Mann-Whitney U (Healthy vs T1D): "
              f"stat={mw_stat:.1f}  p={mw_p:.4g}")
        print(f"  Distributions are {'SIGNIFICANTLY' if mw_p < 0.05 else 'NOT significantly'} "
              f"different (alpha=0.05)")

    plot_results(bi_ratios, t1d_ratios, bi_per_subj, t1d_per_subj,
                 st_bi, st_t1d)
    print("\nDone.")
    return bi_ratios, t1d_ratios, bi_per_subj, t1d_per_subj


if __name__ == "__main__":
    main()

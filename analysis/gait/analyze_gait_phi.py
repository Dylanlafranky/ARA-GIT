"""
Human Gait Cycle - Stance/Swing Phase Ratio vs. phi
=====================================================
Tests the system-mapping hypothesis:
  At self-selected comfortable walking speed, the stance/swing ratio
  converges on phi = 1.618... (the golden ratio).
  Neurological disease displaces this ratio away from phi.

Data source: PhysioNet gaitndd database
  16 healthy controls
  13 ALS (Amyotrophic Lateral Sclerosis)
  20 Huntington's disease
  15 Parkinson's disease
  Raw force sensor at 300 Hz, left and right foot channels.

Method:
  1. Load raw force signal (300 Hz, mV)
  2. Threshold at 0 mV:
       positive -> foot on ground (STANCE)
       negative -> foot in air   (SWING)
  3. Detect each contiguous stance block and each contiguous swing block
  4. Pair consecutive stance + swing as one full half-cycle
  5. Compute ratio = T_stance / T_swing per stride
  6. Filter physiologically implausible strides:
       T_stance < 100ms or T_swing < 100ms  (clearly erroneous)
       ratio < 0.3 or ratio > 6            (outlier)
  7. Pool per-subject; primary statistic = MEDIAN
  8. Compare groups and test distance from phi

Dataset signals:
  Signal > 0  : foot bearing weight (stance phase)
  Signal < 0  : foot airborne       (swing phase)
  fs = 300 Hz  -> 1 sample = 3.33 ms
"""

import os, warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
import wfdb

warnings.filterwarnings("ignore")

PHI       = (1 + np.sqrt(5)) / 2   # 1.61803...
FS        = 300                      # Hz
MIN_PHASE = 0.10 * FS               # 100 ms minimum phase duration
THRESHOLD = None                     # None = per-subject Otsu threshold
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Group definitions (gaitndd record names)
# ---------------------------------------------------------------------------
GROUPS = {
    "Control"    : [f"control{i}" for i in range(1, 17)],
    "Parkinson's": [f"park{i}"    for i in range(1, 16)],
    "ALS"        : [f"als{i}"     for i in range(1, 14)],
    "Huntington's":[f"hunt{i}"    for i in range(1, 21)],
}

GROUP_COLORS = {
    "Control"    : "#2f9e44",
    "Parkinson's": "#1c7ed6",
    "ALS"        : "#e03131",
    "Huntington's":"#e67700",
}


# ---------------------------------------------------------------------------
# Per-subject Otsu threshold (handles sensor DC-offset variation)
# ---------------------------------------------------------------------------

def otsu_threshold(signal):
    """
    Find the optimal bimodal threshold via Otsu's method.
    The force signal has two clusters: stance (high) and swing (low).
    Otsu finds the inter-class variance maximising threshold between them.
    """
    s = signal[~np.isnan(signal)]
    hist, bin_edges = np.histogram(s, bins=256)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    total   = hist.sum()
    best_thresh = bin_centers[0]
    best_var    = 0.0
    w0_cum = 0
    sum_total = float(np.dot(hist, bin_centers))
    sum0 = 0.0
    for i in range(len(hist)):
        w0_cum += hist[i]
        if w0_cum == 0:
            continue
        w1 = total - w0_cum
        if w1 == 0:
            break
        sum0 += hist[i] * bin_centers[i]
        mu0 = sum0 / w0_cum
        mu1 = (sum_total - sum0) / w1
        var  = (w0_cum / total) * (w1 / total) * (mu0 - mu1) ** 2
        if var > best_var:
            best_var    = var
            best_thresh = bin_centers[i]
    return best_thresh


# ---------------------------------------------------------------------------
# Phase detection from raw force signal
# ---------------------------------------------------------------------------

def detect_phases(signal, threshold=None):
    """
    Convert continuous force signal to list of (phase, duration_samples).
    phase = 'stance' (signal >= threshold) or 'swing' (signal < threshold).
    Adjacent identical phases are merged.
    Replaces NaN with threshold (treated as transition).
    """
    if threshold is None:
        threshold = otsu_threshold(signal)
    s = np.where(np.isnan(signal), threshold, signal)
    is_stance = (s >= threshold).astype(int)

    # Find transitions
    phases = []
    start  = 0
    current = is_stance[0]

    for i in range(1, len(s)):
        if is_stance[i] != current:
            label = "stance" if current == 1 else "swing"
            phases.append((label, i - start))
            start   = i
            current = is_stance[i]

    label = "stance" if current == 1 else "swing"
    phases.append((label, len(s) - start))
    return phases


def extract_ratios(signal, threshold=None):
    """
    From a raw force signal, extract T_stance / T_swing per stride.
    A "stride" here is one complete stance + swing sequence.
    """
    phases = detect_phases(signal, threshold)

    # Remove phases that are too short (< MIN_PHASE)
    # but DON'T blindly merge — short phases can be real double-steps
    # Instead just filter at ratio stage
    ratios  = []
    t_stances = []
    t_swings  = []

    i = 0
    while i < len(phases) - 1:
        label, dur = phases[i]
        if label == "stance":
            next_label, next_dur = phases[i + 1]
            if next_label == "swing":
                t_stance = dur / FS       # seconds
                t_swing  = next_dur / FS  # seconds

                # Minimum physiological phase check
                if t_stance >= 0.10 and t_swing >= 0.10:
                    r = t_stance / t_swing
                    if 0.3 < r < 6.0:
                        ratios.append(r)
                        t_stances.append(t_stance)
                        t_swings.append(t_swing)
                i += 2
            else:
                i += 1
        else:
            i += 1

    return ratios, t_stances, t_swings


def process_record(record_name):
    """Load record, process both feet, return pooled ratios."""
    try:
        r = wfdb.rdrecord(record_name, pn_dir="gaitndd")
    except Exception as e:
        print(f"  LOAD ERR {record_name}: {e}")
        return [], [], []

    all_ratios   = []
    all_stances  = []
    all_swings   = []

    for ch in range(r.n_sig):
        sig = r.p_signal[:, ch]
        ratios, stances, swings = extract_ratios(sig)
        all_ratios.extend(ratios)
        all_stances.extend(stances)
        all_swings.extend(swings)

    return all_ratios, all_stances, all_swings


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def group_stats(ratios):
    if len(ratios) < 5:
        return dict(n=len(ratios), median=np.nan, mean=np.nan,
                    std=np.nan, phi_dev=np.nan, phi_dev_pct=np.nan,
                    p_vs_phi=np.nan)
    arr = np.array(ratios)
    med = np.median(arr)
    mn  = np.mean(arr)
    sd  = np.std(arr, ddof=1)
    t, p = stats.ttest_1samp(arr, PHI)
    dev  = abs(med - PHI)
    pct  = dev / PHI * 100
    return dict(n=len(arr), median=med, mean=mn, std=sd,
                phi_dev=dev, phi_dev_pct=pct, p_vs_phi=p)


def mannwhitney(a, b):
    if len(a) < 5 or len(b) < 5:
        return np.nan, np.nan
    return stats.mannwhitneyu(a, b, alternative="two-sided")


# ---------------------------------------------------------------------------
# Visualisation
# ---------------------------------------------------------------------------

def plot_results(results):
    """
    Panel plot:
      Row 0: Healthy controls
      Rows 1-3: Each pathology
      Bottom row: Overlay + deviation bar chart
    """
    group_names  = list(GROUPS.keys())
    n_groups     = len(group_names)

    fig = plt.figure(figsize=(22, 30), facecolor="#f8f9fa")
    fig.suptitle(
        "Human Gait Cycle — Stance / Swing Phase Ratio vs. Golden Ratio (phi = 1.618)\n"
        "Source: PhysioNet gaitndd database  |  300 Hz foot-force sensor\n"
        "Each stride: T_stance / T_swing  (foot contact / foot airborne)",
        fontsize=14, fontweight="bold", y=0.995
    )

    gs = gridspec.GridSpec(n_groups + 1, 2, figure=fig,
                           hspace=0.55, wspace=0.35,
                           left=0.07, right=0.97,
                           top=0.965, bottom=0.04)

    # Per-group rows
    for row, gname in enumerate(group_names):
        ratios = results[gname]["pooled"]
        st     = results[gname]["stats"]
        color  = GROUP_COLORS[gname]

        ax = fig.add_subplot(gs[row, 0])
        if len(ratios) >= 5:
            arr  = np.array(ratios)
            lo_b = max(0.3, np.percentile(arr, 0.5))
            hi_b = min(5.5, np.percentile(arr, 99.5))
            bins = np.linspace(lo_b, hi_b, 70)
            ax.hist(arr, bins=bins, color=color, alpha=0.70,
                    label=f"n = {st['n']:,} strides", density=True)
            ax.axvline(st["median"], color=color, linestyle="--",
                       linewidth=2.5,
                       label=f"Median = {st['median']:.3f}")
            ax.axvline(PHI, color="#fcc419", linestyle="-",
                       linewidth=3, label=f"phi = {PHI:.3f}")

        n_subj = len(GROUPS[gname])
        ax.set_title(f"{gname}  (n={n_subj} subjects)", fontsize=12, fontweight="bold")
        ax.set_xlabel("T_stance / T_swing")
        ax.set_ylabel("Probability Density")
        ax.legend(fontsize=8.5)
        ax.set_facecolor("#ffffff")
        ax.grid(True, alpha=0.25)

        # Stats box
        ax_s = fig.add_subplot(gs[row, 1])
        ax_s.axis("off")
        pct_s = f"{st['phi_dev_pct']:.2f}%" if not np.isnan(st["phi_dev_pct"]) else "N/A"
        verdict = ("PASS: Median ~ phi  (within 5%)"
                   if st["phi_dev_pct"] < 5 else
                   ("NEAR: Median within 5-15%"
                    if st["phi_dev_pct"] < 15 else
                    "DIFF: Median >15% from phi"))

        # Per-subject medians
        per_s = results[gname]["per_subject"]
        subj_lines = []
        for sid, info in sorted(per_s.items()):
            if info["n"] > 0:
                subj_lines.append(
                    f"    {sid:<12}  n={info['n']:3d}  "
                    f"med={info['median']:.3f}"
                )

        lines = [
            f"  Group:  {gname}",
            f"  Strides (n): {st['n']:,}",
            f"  Subjects:    {len(per_s)}",
            "",
            f"  Median:      {st['median']:.4f}",
            f"  Mean:        {st['mean']:.4f}",
            f"  Std Dev:     {st['std']:.4f}",
            "",
            f"  phi =        {PHI:.4f}",
            f"  |Med - phi|: {st['phi_dev']:.4f}  ({pct_s})",
            f"  t vs phi:    p = {st['p_vs_phi']:.4g}",
            "",
            f"  >> {verdict}",
            "",
            "  Per-subject medians:",
        ] + subj_lines[:16]  # cap at 16 lines

        ax_s.text(0.02, 0.98, "\n".join(lines),
                  transform=ax_s.transAxes,
                  fontsize=7.5, fontfamily="monospace",
                  verticalalignment="top",
                  bbox=dict(boxstyle="round,pad=0.5",
                            facecolor="#ffffff",
                            edgecolor=color, linewidth=2))

    # Bottom row: Overlay + Deviation bar chart
    ax_ov = fig.add_subplot(gs[n_groups, 0])
    ctrl  = np.array(results["Control"]["pooled"])
    all_data = {g: np.array(results[g]["pooled"]) for g in group_names}

    lo_all = min(np.percentile(d, 0.5) for d in all_data.values() if len(d) > 5)
    hi_all = max(np.percentile(d, 99.5) for d in all_data.values() if len(d) > 5)
    bins   = np.linspace(max(0.3, lo_all), min(5.5, hi_all), 65)

    for gname in group_names:
        arr = all_data[gname]
        if len(arr) >= 5:
            ax_ov.hist(arr, bins=bins, color=GROUP_COLORS[gname],
                       alpha=0.45, density=True, label=gname)
            ax_ov.axvline(results[gname]["stats"]["median"],
                          color=GROUP_COLORS[gname],
                          linestyle="--", linewidth=1.8)

    ax_ov.axvline(PHI, color="#fcc419", linestyle="-", linewidth=3,
                  label=f"phi = {PHI:.3f}")

    # Mann-Whitney: each group vs control
    mw_lines = []
    for gname in group_names[1:]:
        arr = all_data[gname]
        if len(arr) >= 5 and len(ctrl) >= 5:
            _, p = mannwhitney(ctrl.tolist(), arr.tolist())
            mw_lines.append(f"Control vs {gname}: p={p:.4g}"
                            + (" ***" if p < 0.001 else
                               " **" if p < 0.01 else
                               " *" if p < 0.05 else " ns"))

    ax_ov.set_title("Overlay: All Groups\n" + "  |  ".join(mw_lines),
                    fontsize=9, fontweight="bold")
    ax_ov.set_xlabel("T_stance / T_swing")
    ax_ov.set_ylabel("Probability Density")
    ax_ov.legend(fontsize=8, ncol=2)
    ax_ov.set_facecolor("#ffffff")
    ax_ov.grid(True, alpha=0.25)

    # Deviation bar chart
    ax_bar = fig.add_subplot(gs[n_groups, 1])
    devs_pct = [results[g]["stats"]["phi_dev_pct"] for g in group_names]
    medians  = [results[g]["stats"]["median"] for g in group_names]
    bar_colors = [GROUP_COLORS[g] for g in group_names]

    bars = ax_bar.bar(group_names, devs_pct, color=bar_colors,
                      alpha=0.85, edgecolor="white", linewidth=1.5)
    ax_bar.axhline(5,  color="#fab005", linestyle="--", linewidth=1.5,
                   label="5% (~ phi)")
    ax_bar.axhline(15, color="#e03131", linestyle="--", linewidth=1.5,
                   label="15% outer")

    for bar, pct, med in zip(bars, devs_pct, medians):
        if not np.isnan(pct):
            ax_bar.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.3,
                        f"{pct:.1f}%\n(med={med:.3f})",
                        ha="center", va="bottom", fontsize=8.5,
                        fontweight="bold")

    ax_bar.set_title("Distance from phi by Group",
                     fontsize=11, fontweight="bold")
    ax_bar.set_ylabel("|Median - phi| / phi  (%)")
    ax_bar.legend(fontsize=9)
    ax_bar.set_facecolor("#ffffff")
    ax_bar.grid(True, axis="y", alpha=0.3)

    out = os.path.join(OUTPUT_DIR, "gait_phi_analysis.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"\n[SAVED]  {out}")
    return out


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------

def print_summary(results):
    print("\n" + "=" * 70)
    print(f"  GAIT STANCE/SWING RATIO vs phi  |  phi = {PHI:.6f}")
    print(f"  Source: PhysioNet gaitndd  |  300 Hz foot-force sensor")
    print(f"  System mapping prediction: T_stance / T_swing = phi")
    print("=" * 70)
    print(f"  {'Group':<16}  {'Subj':>4}  {'Strides':>8}  "
          f"{'Median':>8}  {'Mean':>8}  {'|Dev%|':>8}  {'p-phi':>10}")
    print("-" * 70)
    for gname in GROUPS:
        st = results[gname]["stats"]
        n_subj = len(GROUPS[gname])
        pct = f"{st['phi_dev_pct']:.2f}%" if not np.isnan(st["phi_dev_pct"]) else "N/A"
        flag = ("<<< ~ phi" if st["phi_dev_pct"] < 5 else
                ("< near phi" if st["phi_dev_pct"] < 15 else ""))
        print(f"  {gname:<16}  {n_subj:>4}  {st['n']:>8,}  "
              f"{st['median']:>8.4f}  {st['mean']:>8.4f}  "
              f"{pct:>8}  {st['p_vs_phi']:>10.4g}  {flag}")
    print("=" * 70)
    print(f"\n  phi = {PHI:.6f}  (system-mapping target)")
    print(f"  Framework prediction: Control should be nearest phi,")
    print(f"  pathological groups should be further from phi.")

    # Between-group tests
    ctrl_r = results["Control"]["pooled"]
    print("\n  Mann-Whitney U tests (vs Control):")
    for gname in list(GROUPS.keys())[1:]:
        arr = results[gname]["pooled"]
        _, p = mannwhitney(ctrl_r, arr)
        sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
        print(f"    Control vs {gname:<16} p = {p:.4g}  {sig}")
    print("=" * 70)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    results = {}

    for gname, record_list in GROUPS.items():
        print(f"\n=== {gname} ===")
        group_ratios   = []
        group_stances  = []
        group_swings   = []
        per_subject    = {}

        for rec in record_list:
            ratios, stances, swings = process_record(rec)
            if ratios:
                med = np.median(ratios)
                per_subject[rec] = {
                    "n": len(ratios),
                    "median": med,
                    "mean": np.mean(ratios),
                }
                print(f"  {rec:<12}  n={len(ratios):4d}  "
                      f"median={med:.3f}  "
                      f"mean_stance={np.mean(stances):.3f}s  "
                      f"mean_swing={np.mean(swings):.3f}s")
                group_ratios.extend(ratios)
                group_stances.extend(stances)
                group_swings.extend(swings)
            else:
                per_subject[rec] = {"n": 0, "median": np.nan, "mean": np.nan}
                print(f"  {rec:<12}  NO VALID STRIDES")

        st = group_stats(group_ratios)
        results[gname] = {
            "pooled"     : group_ratios,
            "stances"    : group_stances,
            "swings"     : group_swings,
            "per_subject": per_subject,
            "stats"      : st,
        }
        print(f"  POOLED: n={st['n']:,}  "
              f"median={st['median']:.4f}  "
              f"|dev from phi|={st['phi_dev_pct']:.2f}%")

    print_summary(results)
    plot_results(results)
    print("\nDone.")
    return results


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    main()

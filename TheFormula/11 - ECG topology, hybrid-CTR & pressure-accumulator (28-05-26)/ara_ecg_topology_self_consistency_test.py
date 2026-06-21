"""
ara_ecg_topology_self_consistency_test.py

Cross-domain test: does the phi-rung topology decomposition produce the same
"persistence through topology" result on ECG RR-interval data as it does on
ENSO?

WHAT WE'RE TESTING:
  The ENSO audit showed:
    1. The layered-sand formula decomposes raw NINO into phi-rung spin packets
    2. Reconstructing from those packets gives ~0.977 correlation with input
    3. This means the topology acts as a near-identity: input ≈ output
    4. Phase-shifting the reconstruction back just re-aligns it with the date
       it was already reading from — tautological

  If this is a GENERAL property of phi-rung decomposition (not ENSO-specific),
  then applying the same architecture to ECG RR intervals should show:
    - High reconstruction correlation (topology preserves the signal)
    - Phase-shift-back correlation that's tautological for the same reason
    - Forward phase-shift that does NOT beat persistence

  If it's an ENSO-specific artifact, the ECG results will differ.

DATA: PhysioNet Normal Sinus Rhythm RR Interval Database (54 subjects)
  Binary .ecg files: 8-byte header + 16-bit LE unsigned integers (ms)

APPROACH:
  For each subject, take a segment of RR intervals and:
    1. Decompose into phi-rung components (bandpass at HOME, HOME/phi, etc.)
    2. Reconstruct by summing components
    3. Measure reconstruction fidelity
    4. Test forward prediction: does the topology + phase shift beat persistence?
"""

from __future__ import annotations

import glob
import json
import math
import struct
from pathlib import Path

import numpy as np
from numpy.fft import rfft, irfft, rfftfreq

PHI = (1 + math.sqrt(5)) / 2
HERE = Path(__file__).resolve().parent
ECG_DIR = Path("/sessions/trusting-upbeat-heisenberg/mnt/SystemFormulaFolder/normal-sinus-rhythm-rr-interval-database-1.0.0")
OUT_JSON = HERE / "ara_ecg_topology_self_consistency_result.json"


def load_ecg_rr(filepath, min_rr=300, max_rr=2000):
    """Load RR intervals from PhysioNet .ecg binary file."""
    with open(filepath, "rb") as f:
        raw = f.read()
    n = (len(raw) - 8) // 2
    rr = np.array(struct.unpack(f"<{n}H", raw[8 : 8 + n * 2]), dtype=float)
    # Filter artifacts
    mask = (rr > min_rr) & (rr < max_rr)
    return rr[mask]


def phi_rung_decompose(signal, n_rungs=5):
    """
    Decompose a signal into phi-rung frequency bands.

    Uses the same phi-power period structure as the layered-sand formula:
      rung 0: HOME (base period)
      rung 1: HOME / PHI
      rung 2: HOME / PHI^2
      rung 3: HOME / PHI^3
      rung 4: HOME / PHI^4

    For ECG, HOME is the dominant period of the signal (estimated from data).
    Each rung is a bandpass filter centered on the rung's period.

    Returns: list of component signals, one per rung, plus residual
    """
    N = len(signal)
    spectrum = rfft(signal)
    freqs = rfftfreq(N)  # in cycles per sample

    # Estimate HOME as the dominant low-frequency period
    # Use the strongest spectral peak in the plausible range (20-200 beats)
    power = np.abs(spectrum) ** 2
    # Exclude DC and very low frequencies
    min_period = 10   # beats
    max_period = min(N // 2, 500)  # beats
    min_freq = 1.0 / max_period
    max_freq = 1.0 / min_period
    mask = (freqs >= min_freq) & (freqs <= max_freq)
    if not np.any(mask):
        return None, None, None

    peak_idx = np.argmax(power[mask])
    peak_freq = freqs[mask][peak_idx]
    HOME = 1.0 / peak_freq if peak_freq > 0 else 100.0

    # Define rung periods
    rung_periods = [HOME / (PHI ** k) for k in range(n_rungs)]
    rung_freqs = [1.0 / p for p in rung_periods]

    # Bandpass each rung: use a Gaussian window in frequency space
    # Width = period / (2 * PHI) to avoid overlap
    components = []
    for k in range(n_rungs):
        center_freq = rung_freqs[k]
        # Bandwidth: geometric mean between this rung and neighbors
        if k == 0:
            bw = center_freq * (1 - 1 / PHI) * 0.8
        else:
            bw = center_freq * (1 - 1 / PHI) * 0.8
        # Gaussian bandpass
        window = np.exp(-0.5 * ((freqs - center_freq) / bw) ** 2)
        filtered_spectrum = spectrum * window
        component = irfft(filtered_spectrum, n=N)
        components.append(component)

    # Reconstruction = sum of all rung components
    reconstruction = sum(components)

    # Residual = what the phi-rungs don't capture
    residual = signal - reconstruction

    return components, reconstruction, {
        "HOME": HOME,
        "rung_periods": rung_periods,
        "rung_freqs": rung_freqs,
    }


def test_one_subject(rr, subject_id, segment_len=4000):
    """
    Run the full topology self-consistency test on one subject.

    1. Take a segment of RR intervals
    2. Split 70/30 train/holdout
    3. Decompose train portion into phi-rung components
    4. Test reconstruction fidelity on train
    5. Test forward prediction on holdout:
       a) Persistence: predict holdout = last train value
       b) Topology phase shift: advance the decomposition forward
       c) Repeat-last-cycle: tile the last HOME-length cycle forward
    """
    if len(rr) < segment_len:
        segment_len = len(rr)
    # Use the middle segment for stability
    start = (len(rr) - segment_len) // 2
    segment = rr[start : start + segment_len]

    # Normalize: work with detrended RR (subtract running mean)
    mean_rr = np.mean(segment)
    signal = segment - mean_rr  # zero-centered

    # Train/holdout split: 70/30
    split_idx = int(0.7 * len(signal))
    train = signal[:split_idx]
    holdout = signal[split_idx:]
    full_raw = segment  # un-centered for persistence

    # Step 1: Decompose train signal
    result = phi_rung_decompose(train)
    if result[0] is None:
        return None

    components, reconstruction, info = result
    HOME = info["HOME"]

    # Step 2: Reconstruction fidelity on train
    recon_corr = np.corrcoef(train, reconstruction)[0, 1]

    # Step 3: Forward predictions on holdout

    holdout_actual = full_raw[split_idx:]
    n_holdout = len(holdout_actual)

    # 3a) Persistence: last train value
    persistence_pred = np.full(n_holdout, full_raw[split_idx - 1])

    # 3b) Topology phase shift: for each rung, advance phase by the holdout offset
    # This is the direct analog of what the ENSO formula does:
    # take the decomposed components at origin time and shift them forward
    topo_pred_signal = np.zeros(n_holdout)
    for k, component in enumerate(components):
        period = info["rung_periods"][k]
        freq = info["rung_freqs"][k]
        # Estimate amplitude and phase of this rung at the end of training
        # Use the last full cycle of each rung
        last_cycle_len = min(int(period * 2), len(component))
        tail = component[-last_cycle_len:]
        # FFT of the tail to get amplitude and phase
        tail_fft = rfft(tail)
        tail_freqs = rfftfreq(len(tail))
        # Find the component nearest to the rung frequency
        target_idx = np.argmin(np.abs(tail_freqs - freq))
        if target_idx > 0:
            amp = np.abs(tail_fft[target_idx]) * 2 / len(tail)
            phase = np.angle(tail_fft[target_idx])
            # Project forward
            t_holdout = np.arange(n_holdout) + len(train)
            rung_forward = amp * np.cos(2 * np.pi * freq * t_holdout + phase)
            topo_pred_signal += rung_forward

    topo_pred = topo_pred_signal + mean_rr

    # 3c) Repeat-last-cycle: tile the last HOME-length segment forward
    cycle_len = max(int(HOME), 10)
    last_cycle = full_raw[split_idx - cycle_len : split_idx]
    if len(last_cycle) < cycle_len:
        last_cycle = full_raw[:split_idx][-cycle_len:]
    tiles_needed = (n_holdout // len(last_cycle)) + 2
    tiled = np.tile(last_cycle, tiles_needed)[:n_holdout]
    repeat_pred = tiled

    # Step 4: Score all predictors
    def score(pred, actual):
        if len(pred) != len(actual) or len(pred) < 3:
            return {"corr": None, "mae": None, "direction": None}
        c = np.corrcoef(pred, actual)[0, 1]
        mae = float(np.mean(np.abs(pred - actual)))
        # Direction accuracy: does the predictor get the beat-to-beat direction right?
        pred_delta = np.diff(pred)
        actual_delta = np.diff(actual)
        mask = np.abs(actual_delta) > 0.5  # meaningful changes
        if np.any(mask):
            direction = float(np.mean(np.sign(pred_delta[mask]) == np.sign(actual_delta[mask])))
        else:
            direction = None
        return {"corr": float(c), "mae": mae, "direction": direction}

    # Score at multiple horizons (in beats ahead)
    horizon_results = {}
    for h_beats in [10, 50, 100, 200, 500]:
        if h_beats >= n_holdout:
            continue
        h_actual = holdout_actual[:h_beats]
        h_pers = persistence_pred[:h_beats]
        h_topo = topo_pred[:h_beats]
        h_repeat = repeat_pred[:h_beats]

        horizon_results[str(h_beats)] = {
            "Persistence": score(h_pers, h_actual),
            "Topology_Phase_Shift": score(h_topo, h_actual),
            "Repeat_Last_Cycle": score(h_repeat, h_actual),
        }

    # Also score full holdout
    full_scores = {
        "Persistence": score(persistence_pred, holdout_actual),
        "Topology_Phase_Shift": score(topo_pred, holdout_actual),
        "Repeat_Last_Cycle": score(repeat_pred, holdout_actual),
    }

    # Step 5: Phase-shift-back test
    # Does shifting the reconstruction back in time give high correlation?
    # This is the test that gave 0.977 for ENSO
    shift_back_corrs = {}
    for lag in range(-20, 21):
        if lag == 0:
            shift_back_corrs["0"] = float(np.corrcoef(train, reconstruction)[0, 1])
        elif lag < 0:
            c = np.corrcoef(reconstruction[-lag:], train[:lag])[0, 1]
            shift_back_corrs[str(lag)] = float(c)
        else:
            c = np.corrcoef(reconstruction[:-lag], train[lag:])[0, 1]
            shift_back_corrs[str(lag)] = float(c)

    return {
        "subject": subject_id,
        "n_beats_total": len(rr),
        "n_beats_segment": len(segment),
        "n_train": len(train),
        "n_holdout": n_holdout,
        "mean_rr_ms": float(mean_rr),
        "bpm": float(60000 / mean_rr),
        "HOME_beats": float(HOME),
        "rung_periods_beats": info["rung_periods"],
        "reconstruction_corr": float(recon_corr),
        "rung_variance_fractions": [
            float(np.var(c) / np.var(train)) for c in components
        ],
        "total_variance_captured": float(np.var(reconstruction) / np.var(train)),
        "shift_back_corrs": shift_back_corrs,
        "full_holdout_scores": full_scores,
        "by_horizon": horizon_results,
    }


def run():
    ecg_files = sorted(glob.glob(str(ECG_DIR / "*.ecg")))
    print(f"ARA ECG Topology Self-Consistency Test")
    print("=" * 100)
    print(f"Found {len(ecg_files)} ECG files")
    print()

    results = []
    recon_corrs = []
    persistence_corrs = []
    topo_corrs = []
    repeat_corrs = []

    for filepath in ecg_files:
        subject_id = Path(filepath).stem
        rr = load_ecg_rr(filepath)
        if len(rr) < 1000:
            print(f"  {subject_id}: too few beats ({len(rr)}), skipping")
            continue

        result = test_one_subject(rr, subject_id)
        if result is None:
            print(f"  {subject_id}: decomposition failed, skipping")
            continue

        results.append(result)
        recon_corrs.append(result["reconstruction_corr"])

        fs = result["full_holdout_scores"]
        if fs["Persistence"]["corr"] is not None:
            persistence_corrs.append(fs["Persistence"]["corr"])
        if fs["Topology_Phase_Shift"]["corr"] is not None:
            topo_corrs.append(fs["Topology_Phase_Shift"]["corr"])
        if fs["Repeat_Last_Cycle"]["corr"] is not None:
            repeat_corrs.append(fs["Repeat_Last_Cycle"]["corr"])

        print(
            f"  {subject_id}: "
            f"recon={result['reconstruction_corr']:+.3f}  "
            f"var_captured={result['total_variance_captured']:.3f}  "
            f"HOME={result['HOME_beats']:.0f} beats  "
            f"holdout: pers={fs['Persistence']['corr']:+.3f} "
            f"topo={fs['Topology_Phase_Shift']['corr']:+.3f} "
            f"repeat={fs['Repeat_Last_Cycle']['corr']:+.3f}"
        )

    print()
    print("=" * 100)
    print("AGGREGATE RESULTS")
    print("=" * 100)

    print(f"\n  Subjects analyzed: {len(results)}")
    print(f"\n  Reconstruction fidelity (topology ≈ input?):")
    print(f"    Mean corr(reconstruction, train): {np.mean(recon_corrs):+.3f}")
    print(f"    Std:  {np.std(recon_corrs):.3f}")
    print(f"    Min:  {np.min(recon_corrs):+.3f}")
    print(f"    Max:  {np.max(recon_corrs):+.3f}")

    print(f"\n  Forward prediction (full holdout):")
    print(f"    Persistence:         mean corr = {np.mean(persistence_corrs):+.3f} (std {np.std(persistence_corrs):.3f})")
    print(f"    Topology Phase Shift: mean corr = {np.mean(topo_corrs):+.3f} (std {np.std(topo_corrs):.3f})")
    print(f"    Repeat Last Cycle:    mean corr = {np.mean(repeat_corrs):+.3f} (std {np.std(repeat_corrs):.3f})")

    topo_beats_pers = sum(1 for t, p in zip(topo_corrs, persistence_corrs) if t > p)
    repeat_beats_pers = sum(1 for r, p in zip(repeat_corrs, persistence_corrs) if r > p)
    topo_beats_repeat = sum(1 for t, r in zip(topo_corrs, repeat_corrs) if t > r)

    print(f"\n  Head-to-head (out of {len(results)} subjects):")
    print(f"    Topology beats Persistence: {topo_beats_pers}/{len(results)}")
    print(f"    Repeat beats Persistence:   {repeat_beats_pers}/{len(results)}")
    print(f"    Topology beats Repeat:      {topo_beats_repeat}/{len(results)}")

    # Phase-shift-back analysis
    mean_shift_corrs = {}
    for lag in range(-20, 21):
        vals = [r["shift_back_corrs"].get(str(lag), 0) for r in results]
        mean_shift_corrs[str(lag)] = float(np.mean(vals))

    best_lag = max(mean_shift_corrs, key=lambda k: mean_shift_corrs[k])
    print(f"\n  Phase-shift-back test:")
    print(f"    Best lag: {best_lag} beats (corr = {mean_shift_corrs[best_lag]:+.3f})")
    print(f"    Lag=0 (no shift): corr = {mean_shift_corrs['0']:+.3f}")
    print(f"    This is the reconstruction fidelity — it should be high.")
    print(f"    If best lag ≠ 0, the topology is introducing a systematic time offset.")
    print(f"    For ENSO, shift-back was tautological (aligning with same calendar date).")
    print(f"    For ECG, there IS no calendar date trick — shift-back is a real test.")

    # Verdict
    print(f"\n{'='*100}")
    print("VERDICT: Does ECG show the same pattern as ENSO?")
    print(f"{'='*100}")

    enso_like = (
        np.mean(recon_corrs) > 0.5
        and np.mean(topo_corrs) < np.mean(persistence_corrs)
    )

    if enso_like:
        print(f"""
  YES — same pattern as ENSO:
    The phi-rung decomposition reconstructs the input well
    (mean recon corr = {np.mean(recon_corrs):+.3f})
    but the forward phase shift does NOT beat persistence
    (topo={np.mean(topo_corrs):+.3f} vs pers={np.mean(persistence_corrs):+.3f}).

    This confirms: "persistence gained through topology is still persistence"
    is a GENERAL property of phi-rung decomposition, not ENSO-specific.
""")
    else:
        print(f"""
  DIFFERENT pattern from ENSO:
    Reconstruction corr: {np.mean(recon_corrs):+.3f}
    Forward topo corr:   {np.mean(topo_corrs):+.3f}
    Forward pers corr:   {np.mean(persistence_corrs):+.3f}

    The ECG result differs from ENSO. This needs interpretation.
""")

    # Save results
    out = {
        "date": "2026-05-27",
        "method": "Cross-domain phi-rung topology self-consistency test on ECG RR intervals",
        "data_source": "PhysioNet Normal Sinus Rhythm RR Interval Database",
        "n_subjects": len(results),
        "aggregate": {
            "reconstruction_corr": {
                "mean": float(np.mean(recon_corrs)),
                "std": float(np.std(recon_corrs)),
                "min": float(np.min(recon_corrs)),
                "max": float(np.max(recon_corrs)),
            },
            "holdout_persistence_corr": {
                "mean": float(np.mean(persistence_corrs)),
                "std": float(np.std(persistence_corrs)),
            },
            "holdout_topology_corr": {
                "mean": float(np.mean(topo_corrs)),
                "std": float(np.std(topo_corrs)),
            },
            "holdout_repeat_corr": {
                "mean": float(np.mean(repeat_corrs)),
                "std": float(np.std(repeat_corrs)),
            },
            "topology_beats_persistence": f"{topo_beats_pers}/{len(results)}",
            "mean_shift_back_corrs": mean_shift_corrs,
        },
        "per_subject": results,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"Saved -> {OUT_JSON}")


if __name__ == "__main__":
    run()

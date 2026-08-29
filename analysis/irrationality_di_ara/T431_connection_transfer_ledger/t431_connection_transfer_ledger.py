from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import pathlib
import sys
import urllib.request
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import ndimage, signal, stats


ROOT = pathlib.Path(__file__).resolve().parent
RESULTS = ROOT / "results"
T427_ROOT = ROOT.parent / "T427_spacetime_strain_handover"
T429_ROOT = ROOT.parent / "T429_separated_space_time_strength"
T430_ROOT = ROOT.parent / "T430_remaining_traversal_connection"
sys.path.insert(0, str(T427_ROOT))
sys.path.insert(0, str(T429_ROOT))
import t427_spacetime_strain_handover as t427  # noqa: E402
import t429_separated_space_time_strength as t429  # noqa: E402


DEVELOPMENT_INTERVALS = {
    "old": (-0.50, -0.12),
    "mobile": (-0.08, 0.02),
    "new": (0.04, 0.20),
}
EVENT_INTERVAL = (-0.50, 0.20)
LEDGER_INTERVAL = (-0.22, 0.16)
LEDGER_PRE = (-0.22, -0.04)
LEDGER_MOBILE = (-0.08, 0.04)
LEDGER_POST = (0.04, 0.16)
OFF_INTERVALS = ((-12.0, -4.0), (4.0, 12.0))
FEATURES = (
    "amount", "concentration", "movement", "frequency",
    "amount_rate", "concentration_rate", "movement_rate", "frequency_rate",
)
STATES = ("old", "mobile", "new")
SMOOTH_FRAMES = 7
EPS = 1e-12
SEED = 43120260825


@dataclass
class DetectorView:
    times: np.ndarray
    matrix: np.ndarray
    amount: np.ndarray
    concentration: np.ndarray
    movement: np.ndarray
    frequency: np.ndarray
    probability: np.ndarray
    complex_spectrum: np.ndarray
    qa: dict[str, object]


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mask_interval(times: np.ndarray, interval: tuple[float, float]) -> np.ndarray:
    return (times >= interval[0]) & (times <= interval[1])


def mask_intervals(times: np.ndarray, intervals: tuple[tuple[float, float], ...]) -> np.ndarray:
    mask = np.zeros(len(times), dtype=bool)
    for interval in intervals:
        mask |= mask_interval(times, interval)
    return mask


def align_matrix(values: np.ndarray, lag_frames: int) -> np.ndarray:
    values = np.asarray(values)
    fill = np.nan + 0j if np.iscomplexobj(values) else np.nan
    out = np.full_like(values, fill)
    if lag_frames == 0:
        out[...] = values
    elif lag_frames > 0:
        out[..., :-lag_frames] = values[..., lag_frames:]
    else:
        out[..., -lag_frames:] = values[..., :lag_frames]
    return out


def smooth_columns(matrix: np.ndarray, size: int = SMOOTH_FRAMES) -> np.ndarray:
    return np.column_stack([
        ndimage.median_filter(matrix[:, j], size=size, mode="nearest")
        for j in range(matrix.shape[1])
    ])


def build_detector(event: dict[str, object], detector: str, path: pathlib.Path) -> DetectorView:
    det = t427.build_detector(event, detector, path)
    nperseg = int(round(t427.STFT_SECONDS * det.fs))
    hop = int(round(t427.HOP_SECONDS * det.fs))
    _, _, complex_full = signal.stft(
        det.band,
        fs=det.fs,
        window="hann",
        nperseg=nperseg,
        noverlap=nperseg - hop,
        nfft=max(512, nperseg),
        detrend=False,
        boundary=None,
        padded=False,
    )
    fft_freqs = np.fft.rfftfreq(max(512, nperseg), 1.0 / det.fs)
    keep = (fft_freqs >= t427.FREQ_BAND[0]) & (fft_freqs <= t427.FREQ_BAND[1])
    complex_spectrum = complex_full[keep]
    total = np.sum(det.power, axis=0) + EPS
    probability = det.power / total[None, :]
    centroid = np.sum(probability * det.freqs[:, None], axis=0)
    amount_raw = np.log(total)
    concentration_raw = det.connection_raw
    movement_raw = det.movement_raw
    frequency_raw = np.log(np.maximum(centroid, 1e-9))
    off = mask_intervals(det.frame_rel, OFF_INTERVALS)
    amount = t429.ecdf_ara(amount_raw, amount_raw[off])
    concentration = t429.ecdf_ara(concentration_raw, concentration_raw[off])
    movement = t429.ecdf_ara(movement_raw, movement_raw[off])
    frequency = t429.ecdf_ara(frequency_raw, frequency_raw[off])
    rates = [
        t429.ecdf_ara(np.gradient(raw), np.gradient(raw)[off])
        for raw in (amount_raw, concentration_raw, movement_raw, frequency_raw)
    ]
    matrix = smooth_columns(np.column_stack([amount, concentration, movement, frequency, *rates]))
    return DetectorView(
        times=det.frame_rel,
        matrix=matrix,
        amount=matrix[:, 0],
        concentration=matrix[:, 1],
        movement=matrix[:, 2],
        frequency=matrix[:, 3],
        probability=probability,
        complex_spectrum=complex_spectrum,
        qa=det.qa,
    )


def build_network(event: dict[str, object], files: dict[str, pathlib.Path]) -> dict[str, object]:
    detectors = {name: build_detector(event, name, path) for name, path in files.items() if name in {"H1", "L1"}}
    if set(detectors) != {"H1", "L1"}:
        raise ValueError(f"{event['event']} requires H1 and L1")
    h = detectors["H1"]
    l = detectors["L1"]
    event_mask = mask_interval(h.times, (-0.55, 0.25))
    lag, lag_corr = t427.best_lag(h.amount, l.amount, 2, event_mask)
    l_matrix = align_matrix(l.matrix.T, lag).T
    l_probability = align_matrix(l.probability, lag)
    l_complex = align_matrix(l.complex_spectrum, lag)
    network = np.nanmean(np.stack([h.matrix, l_matrix]), axis=0)
    agreement = 2.0 * np.nansum(np.sqrt(np.maximum(h.probability, 0.0) * np.maximum(l_probability, 0.0)), axis=0)
    agreement = np.clip(agreement, 0.0, 2.0)
    cross = np.nansum(h.complex_spectrum * np.conjugate(l_complex), axis=0)
    norm = np.sqrt(
        np.nansum(np.abs(h.complex_spectrum) ** 2, axis=0)
        * np.nansum(np.abs(l_complex) ** 2, axis=0)
    )
    phase_coherence_raw = np.clip(2.0 * np.abs(cross) / (norm + EPS), 0.0, 2.0)
    off = mask_intervals(h.times, OFF_INTERVALS) & np.isfinite(phase_coherence_raw)
    phase_coherence = t429.ecdf_ara(phase_coherence_raw, phase_coherence_raw[off])
    amount_excess = np.clip(network[:, 0] - 1.0, 0.0, 1.0)
    source_evidence = amount_excess * np.clip(phase_coherence / 2.0, 0.0, 1.0)
    return {
        "times": h.times,
        "matrix": network,
        "h_matrix": h.matrix,
        "l_matrix": l_matrix,
        "agreement": agreement,
        "phase_coherence": phase_coherence,
        "source_evidence": source_evidence,
        "lag_frames": int(lag),
        "lag_ms": float(lag * t427.HOP_SECONDS * 1000.0),
        "lag_corr": float(lag_corr),
        "qa": {"H1": h.qa, "L1": l.qa},
    }


def local_mask(times: np.ndarray, centre: float, interval: tuple[float, float]) -> np.ndarray:
    relative = np.asarray(times, dtype=float) - centre
    return mask_interval(relative, interval)


def peak_index(values: np.ndarray, mask: np.ndarray) -> int:
    candidates = np.where(mask & np.isfinite(values))[0]
    if len(candidates) == 0:
        return -1
    return int(candidates[np.nanargmax(values[candidates])])


def detector_connection_movement(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    matrix = np.asarray(matrix, dtype=float)
    connection = np.nanmean(matrix[:, :2], axis=1)
    movement = matrix[:, 2]
    return connection, movement


def ledger_score(view: dict[str, object], centre: float) -> tuple[dict[str, float | bool], pd.DataFrame]:
    times = np.asarray(view["times"], dtype=float)
    relative = times - centre
    matrix = np.asarray(view["matrix"], dtype=float)
    coherence = np.asarray(view["phase_coherence"], dtype=float)
    connection = ndimage.median_filter(
        np.nanmean(np.column_stack([matrix[:, 0], matrix[:, 1], coherence]), axis=1),
        size=SMOOTH_FRAMES,
        mode="nearest",
    )
    movement = ndimage.median_filter(matrix[:, 2], size=SMOOTH_FRAMES, mode="nearest")
    liquidity = movement - connection

    pre_mask = local_mask(times, centre, LEDGER_PRE)
    mobile_mask = local_mask(times, centre, LEDGER_MOBILE)
    post_mask = local_mask(times, centre, LEDGER_POST)
    event_mask = local_mask(times, centre, LEDGER_INTERVAL)
    i_pre = peak_index(connection, pre_mask)
    i_mobile = peak_index(liquidity, mobile_mask)
    i_post = peak_index(connection, post_mask)
    if min(i_pre, i_mobile, i_post) < 0:
        raise ValueError("ledger interval has no valid frame")

    c_pre, c_mobile, c_post = connection[[i_pre, i_mobile, i_post]]
    m_pre, m_mobile, m_post = movement[[i_pre, i_mobile, i_post]]
    break_depth = float((c_pre + c_post) / 2.0 - c_mobile)
    movement_excess = float(m_mobile - (m_pre + m_post) / 2.0)
    ledger_strength = float(break_depth + movement_excess)
    h_unresolved = np.clip(2.0 - connection - movement, 0.0, 2.0)

    h_connection, h_movement = detector_connection_movement(np.asarray(view["h_matrix"], dtype=float))
    l_connection, l_movement = detector_connection_movement(np.asarray(view["l_matrix"], dtype=float))
    detector_breaks: list[float] = []
    detector_moves: list[float] = []
    for c_det, m_det in ((h_connection, h_movement), (l_connection, l_movement)):
        detector_breaks.append(float((c_det[i_pre] + c_det[i_post]) / 2.0 - c_det[i_mobile]))
        detector_moves.append(float(m_det[i_mobile] - (m_det[i_pre] + m_det[i_post]) / 2.0))

    metrics: dict[str, float | bool] = {
        "centre_s_absolute": float(centre),
        "pre_time_s": float(relative[i_pre]),
        "mobile_time_s": float(relative[i_mobile]),
        "post_time_s": float(relative[i_post]),
        "C_old": float(c_pre),
        "C_mobile": float(c_mobile),
        "C_new": float(c_post),
        "M_old": float(m_pre),
        "M_mobile": float(m_mobile),
        "M_new": float(m_post),
        "connection_break_depth": break_depth,
        "movement_excursion": movement_excess,
        "ledger_strength": ledger_strength,
        "reclosure_asymmetry": float(c_post - c_pre),
        "H_unresolved_mobile": float(h_unresolved[i_mobile]),
        "H_unresolved_old_new_mean": float((h_unresolved[i_pre] + h_unresolved[i_post]) / 2.0),
        "ordered_landmarks": bool(i_pre < i_mobile < i_post),
        "network_shape_pass": bool(break_depth > 0 and movement_excess > 0),
        "H1_connection_break_depth": detector_breaks[0],
        "L1_connection_break_depth": detector_breaks[1],
        "H1_movement_excursion": detector_moves[0],
        "L1_movement_excursion": detector_moves[1],
        "detector_replication_pass": bool(min(detector_breaks) > 0 and min(detector_moves) > 0),
        "median_phase_coherence_ARA": float(np.nanmedian(coherence[event_mask])),
        "peak_source_evidence": float(np.nanmax(np.asarray(view["source_evidence"])[event_mask])),
    }
    history = pd.DataFrame({
        "time_s": relative[event_mask],
        "connection_C": connection[event_mask],
        "movement_M": movement[event_mask],
        "liquidity_M_minus_C": liquidity[event_mask],
        "unresolved_H": h_unresolved[event_mask],
        "phase_coherence_ARA": coherence[event_mask],
        "source_evidence": np.asarray(view["source_evidence"])[event_mask],
    })
    return metrics, history


def offsource_centres() -> list[float]:
    duration = LEDGER_INTERVAL[1] - LEDGER_INTERVAL[0]
    step = duration / 2.0
    centres: list[float] = []
    for start, stop in OFF_INTERVALS:
        centre = start - LEDGER_INTERVAL[0]
        last = stop - LEDGER_INTERVAL[1]
        while centre <= last + 1e-9:
            centres.append(float(centre))
            centre += step
    return centres


def development_ledger(views: dict[str, dict[str, object]]) -> dict[str, object]:
    event_rows: list[dict[str, object]] = []
    control_rows: list[dict[str, object]] = []
    histories: list[pd.DataFrame] = []
    for event, view in sorted(views.items()):
        metrics, history = ledger_score(view, 0.0)
        controls: list[dict[str, float | bool]] = []
        for control_id, centre in enumerate(offsource_centres()):
            row, _ = ledger_score(view, centre)
            row.update({"event": event, "role": "matched_offsource", "control_id": control_id})
            controls.append(row)
            control_rows.append(row)
        null_strength = np.asarray([float(row["ledger_strength"]) for row in controls])
        metrics.update({
            "event": event,
            "role": "development_event",
            "offsource_n": len(controls),
            "ledger_empirical_p": float((1 + np.sum(null_strength >= float(metrics["ledger_strength"]))) / (len(null_strength) + 1)),
            "ledger_offsource_percentile": float(np.mean(null_strength < float(metrics["ledger_strength"]))),
        })
        event_rows.append(metrics)
        history.insert(0, "event", event)
        histories.append(history)
    pd.DataFrame(event_rows).to_csv(RESULTS / "T431_DEVELOPMENT_LEDGER_EVENTS.csv", index=False)
    pd.DataFrame(control_rows).to_csv(RESULTS / "T431_DEVELOPMENT_LEDGER_CONTROLS.csv", index=False)
    pd.concat(histories, ignore_index=True).to_csv(RESULTS / "T431_DEVELOPMENT_LEDGER_HISTORIES.csv", index=False)
    summary = {
        "n_events": len(event_rows),
        "network_shape_pass": int(sum(bool(row["network_shape_pass"]) for row in event_rows)),
        "detector_replication_pass": int(sum(bool(row["detector_replication_pass"]) for row in event_rows)),
        "p_le_0_05": int(sum(float(row["ledger_empirical_p"]) <= 0.05 for row in event_rows)),
        "median_offsource_percentile": float(np.nanmedian([row["ledger_offsource_percentile"] for row in event_rows])),
        "median_ledger_strength": float(np.nanmedian([row["ledger_strength"] for row in event_rows])),
    }
    (RESULTS / "T431_DEVELOPMENT_LEDGER_SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def load_development_sources() -> tuple[list[dict[str, object]], dict[str, dict[str, pathlib.Path]]]:
    rows = json.loads((T427_ROOT / "results" / "T427_SOURCE_AUDIT.json").read_text(encoding="utf-8"))
    rows.extend(json.loads((T430_ROOT / "results" / "T430_SOURCE_AUDIT.json").read_text(encoding="utf-8")))
    events: dict[str, dict[str, object]] = {}
    files: dict[str, dict[str, pathlib.Path]] = {}
    for row in rows:
        event = str(row["event"])
        if event not in events:
            events[event] = {
                "event": event,
                "gps": float(row["gps"]),
                "role": "development_seen",
            }
        if row["detector"] in {"H1", "L1"}:
            files.setdefault(event, {})[str(row["detector"])] = pathlib.Path(str(row["local_path"]))
    ordered = [events[name] for name in sorted(events)]
    return ordered, files


def collect_training_rows(views: dict[str, dict[str, object]], omit: str | None = None) -> tuple[np.ndarray, np.ndarray]:
    matrices: list[np.ndarray] = []
    labels: list[str] = []
    for event, view in views.items():
        if event == omit:
            continue
        times = np.asarray(view["times"], dtype=float)
        matrix = np.asarray(view["matrix"], dtype=float)
        source_evidence = np.asarray(view["source_evidence"], dtype=float)
        for state, interval in DEVELOPMENT_INTERVALS.items():
            base = mask_interval(times, interval) & np.all(np.isfinite(matrix), axis=1) & np.isfinite(source_evidence)
            threshold = float(np.nanquantile(source_evidence[base], 0.75)) if np.any(base) else float("inf")
            mask = base & (source_evidence >= threshold)
            matrices.append(matrix[mask])
            labels.extend([state] * int(np.sum(mask)))
    return np.vstack(matrices), np.asarray(labels, dtype=object)


def fit_prototypes(matrix: np.ndarray, labels: np.ndarray) -> dict[str, object]:
    centre = np.nanmedian(matrix, axis=0)
    scale = 1.4826 * np.nanmedian(np.abs(matrix - centre), axis=0)
    scale = np.where(np.isfinite(scale) & (scale > 1e-6), scale, 1.0)
    z = (matrix - centre) / scale
    prototypes = {state: np.nanmedian(z[labels == state], axis=0) for state in STATES}
    assigned_distance = np.concatenate([
        np.sqrt(np.nanmean((z[labels == state] - prototypes[state]) ** 2, axis=1))
        for state in STATES
    ])
    temperature = float(max(np.nanmedian(assigned_distance), 0.25))
    return {
        "centre": centre,
        "scale": scale,
        "prototypes": prototypes,
        "temperature": temperature,
    }


def state_affinities(matrix: np.ndarray, model: dict[str, object]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z = (matrix - np.asarray(model["centre"])) / np.asarray(model["scale"])
    prototypes = model["prototypes"]
    if isinstance(prototypes, dict):
        vectors = [np.asarray(prototypes[state], dtype=float) for state in STATES]
    else:
        array = np.asarray(prototypes, dtype=float)
        vectors = [array[i] for i in range(len(STATES))]
    distance = np.column_stack([
        np.sqrt(np.nanmean((z - vector) ** 2, axis=1))
        for vector in vectors
    ])
    raw = np.exp(-0.5 * (distance / float(model["temperature"])) ** 2)
    raw = np.column_stack([
        ndimage.median_filter(raw[:, j], size=SMOOTH_FRAMES, mode="nearest")
        for j in range(raw.shape[1])
    ])
    shares = raw / (np.sum(raw, axis=1, keepdims=True) + EPS)
    unresolved = np.clip(1.0 - np.max(raw, axis=1), 0.0, 1.0)
    return raw, shares, unresolved


def rankdata_safe(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    return stats.rankdata(values, method="average")


def weighted_time(times: np.ndarray, weights: np.ndarray) -> float:
    valid = np.isfinite(times) & np.isfinite(weights)
    if np.sum(valid) == 0 or np.sum(weights[valid]) <= EPS:
        return float("nan")
    return float(np.sum(times[valid] * weights[valid]) / np.sum(weights[valid]))


def best_segment_order(times: np.ndarray, affinities: np.ndarray, order: tuple[int, int, int]) -> tuple[float, int, int]:
    n = len(times)
    min_frames = 8
    if n < 3 * min_frames:
        return float("nan"), -1, -1
    log_affinity = np.log(np.clip(affinities, 1e-9, None))
    cumulative = np.vstack([np.zeros(3), np.cumsum(log_affinity, axis=0)])
    best_score = -np.inf
    best_i = best_j = -1
    for i in range(min_frames, n - 2 * min_frames + 1):
        first = cumulative[i, order[0]] - cumulative[0, order[0]]
        for j in range(i + min_frames, n - min_frames + 1):
            second = cumulative[j, order[1]] - cumulative[i, order[1]]
            third = cumulative[n, order[2]] - cumulative[j, order[2]]
            score = float((first + second + third) / n)
            if score > best_score:
                best_score, best_i, best_j = score, i, j
    return best_score, best_i, best_j


def sequence_metrics(times: np.ndarray, raw: np.ndarray, shares: np.ndarray, unresolved: np.ndarray) -> dict[str, float | int | bool]:
    centres = [weighted_time(times, raw[:, i]) for i in range(3)]
    expected_state = shares @ np.arange(3.0)
    rho = float(stats.spearmanr(times, expected_state).statistic)
    margins = (centres[1] - centres[0], centres[2] - centres[1])
    scores: dict[tuple[int, int, int], float] = {}
    cuts: dict[tuple[int, int, int], tuple[int, int]] = {}
    for perm in itertools.permutations(range(3)):
        score, i, j = best_segment_order(times, raw, perm)
        scores[perm] = score
        cuts[perm] = (i, j)
    desired = scores[(0, 1, 2)]
    rank = 1 + sum(value > desired for perm, value in scores.items() if perm != (0, 1, 2))
    best_alternative = max(value for perm, value in scores.items() if perm != (0, 1, 2))
    cut_i, cut_j = cuts[(0, 1, 2)]
    middle = (times >= centres[0]) & (times <= centres[2]) if np.all(np.isfinite(centres)) else np.zeros(len(times), dtype=bool)
    outer = ~middle
    return {
        "old_centre_s": centres[0],
        "mobile_centre_s": centres[1],
        "new_centre_s": centres[2],
        "ordering_margin_s": float(min(margins)),
        "ordered": bool(rank == 1),
        "permutation_rank": int(rank),
        "desired_order_log_score": float(desired),
        "order_advantage_log_score": float(desired - best_alternative),
        "old_to_mobile_boundary_s": float(times[cut_i]) if cut_i >= 0 else float("nan"),
        "mobile_to_new_boundary_s": float(times[cut_j]) if cut_j >= 0 else float("nan"),
        "state_time_rho": rho,
        "unresolved_middle_mean": float(np.nanmean(unresolved[middle])) if np.any(middle) else float("nan"),
        "unresolved_outer_mean": float(np.nanmean(unresolved[outer])) if np.any(outer) else float("nan"),
        "early_old_share": float(np.nanmean(shares[times <= -0.12, 0])),
        "middle_mobile_share": float(np.nanmean(shares[(times >= -0.08) & (times <= 0.02), 1])),
        "late_new_share": float(np.nanmean(shares[times >= 0.04, 2])),
    }


def score_view(view: dict[str, object], model: dict[str, object], interval: tuple[float, float]) -> tuple[dict[str, float | int | bool], pd.DataFrame]:
    times_all = np.asarray(view["times"], dtype=float)
    mask = mask_interval(times_all, interval)
    times = times_all[mask]
    matrix = np.asarray(view["matrix"], dtype=float)[mask]
    source_evidence = np.asarray(view["source_evidence"], dtype=float)[mask]
    raw, shares, unresolved = state_affinities(matrix, model)
    gated_raw = raw * source_evidence[:, None]
    gated_shares = gated_raw / (np.sum(gated_raw, axis=1, keepdims=True) + EPS)
    metrics = sequence_metrics(times, gated_raw, gated_shares, unresolved)
    metrics.update({
        "window_start_s": interval[0],
        "window_end_s": interval[1],
        "n_frames": int(len(times)),
        "median_detector_shape_agreement": float(np.nanmedian(np.asarray(view["agreement"])[mask])),
        "lag_ms": float(view["lag_ms"]),
        "lag_amount_correlation": float(view["lag_corr"]),
    })
    history = pd.DataFrame({
        "time_s": times,
        "old_affinity": raw[:, 0],
        "mobile_affinity": raw[:, 1],
        "new_affinity": raw[:, 2],
        "old_share_bookkeeping": shares[:, 0],
        "mobile_share_bookkeeping": shares[:, 1],
        "new_share_bookkeeping": shares[:, 2],
        "unresolved_H": unresolved,
        "amount_ARA": matrix[:, 0],
        "concentration_ARA": matrix[:, 1],
        "movement_ARA": matrix[:, 2],
        "frequency_ARA": matrix[:, 3],
        "detector_shape_agreement_ARA": np.asarray(view["agreement"])[mask],
        "detector_phase_coherence_ARA": np.asarray(view["phase_coherence"])[mask],
        "source_evidence": source_evidence,
    })
    return metrics, history


def development() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    events, files = load_development_sources()
    views = {str(event["event"]): build_network(event, files[str(event["event"])]) for event in events}
    full_matrix, full_labels = collect_training_rows(views)
    full_model = fit_prototypes(full_matrix, full_labels)
    model_json = {
        "features": list(FEATURES),
        "states": list(STATES),
        "training_intervals": {key: list(value) for key, value in DEVELOPMENT_INTERVALS.items()},
        "event_interval": list(EVENT_INTERVAL),
        "centre": np.asarray(full_model["centre"]).tolist(),
        "scale": np.asarray(full_model["scale"]).tolist(),
        "prototypes": {key: np.asarray(value).tolist() for key, value in full_model["prototypes"].items()},
        "temperature": float(full_model["temperature"]),
        "development_events": sorted(views),
    }
    (RESULTS / "T431_DEVELOPMENT_MODEL.json").write_text(json.dumps(model_json, indent=2), encoding="utf-8")

    rows: list[dict[str, object]] = []
    histories: list[pd.DataFrame] = []
    for event in sorted(views):
        matrix, labels = collect_training_rows(views, omit=event)
        model = fit_prototypes(matrix, labels)
        metrics, history = score_view(views[event], model, EVENT_INTERVAL)
        metrics.update({"event": event, "role": "leave_one_event_out_development"})
        rows.append(metrics)
        history.insert(0, "event", event)
        histories.append(history)
    pd.DataFrame(rows).to_csv(RESULTS / "T431_DEVELOPMENT_LOEO_SCORES.csv", index=False)
    pd.concat(histories, ignore_index=True).to_csv(RESULTS / "T431_DEVELOPMENT_LOEO_HISTORIES.csv", index=False)
    summary = {
        "n_events": len(rows),
        "ordered_events": int(sum(bool(row["ordered"]) for row in rows)),
        "rank1_events": int(sum(int(row["permutation_rank"]) == 1 for row in rows)),
        "median_ordering_margin_s": float(np.nanmedian([row["ordering_margin_s"] for row in rows])),
        "median_state_time_rho": float(np.nanmedian([row["state_time_rho"] for row in rows])),
        "model_sha256": sha256(RESULTS / "T431_DEVELOPMENT_MODEL.json"),
    }
    summary["connection_transfer_ledger"] = development_ledger(views)
    (RESULTS / "T431_DEVELOPMENT_SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("develop",), default="develop")
    args = parser.parse_args()
    if args.stage == "develop":
        development()


if __name__ == "__main__":
    main()

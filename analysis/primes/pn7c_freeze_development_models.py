"""Freeze PN7C sequential-memory models from R9/R10 development gaps only."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN7C_ACTUAL_GAP_SEQUENTIAL_MEMORY_PROTOCOL.md"
EXPECTED_PROTOCOL = "7884D02A19A753DFD2582BEEDC6AFBE38B15E04E44DDD6F5B6B11116F518A67C"
DEVELOPMENT = HERE / "PN7C_DEVELOPMENT_GAPS.npz"
EXPECTED_DEVELOPMENT = "A791D771481523E8331EC241C2F762A1700526F32F663238C1A767D810E67230"
OUT_NPZ = HERE / "PN7C_FROZEN_MODELS.npz"
OUT_JSON = HERE / "PN7C_FROZEN_MODEL_MANIFEST.json"
BINS = (12, 24, 48)
RAW_ALPHABET = 1025
ALPHA = 0.5
RAW_LAMBDA = 64.0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def ara_bins(gaps: np.ndarray, bins: int) -> np.ndarray:
    left = gaps[:-1].astype(np.uint32)
    right = gaps[1:].astype(np.uint32)
    out = (bins * right) // (left + right)
    return np.minimum(out, bins - 1).astype(np.uint8)


def entropy_bits(counts: np.ndarray) -> float:
    positive = counts[counts > 0].astype(np.float64)
    p = positive / positive.sum()
    return float(-np.sum(p * np.log2(p)))


def conditional_entropy_bits(joint: np.ndarray) -> float:
    rows = joint.reshape(-1, joint.shape[-1]).astype(np.float64)
    totals = rows.sum(axis=1)
    used = totals > 0
    rows = rows[used]
    totals = totals[used]
    probs = np.divide(rows, totals[:, None], out=np.zeros_like(rows), where=totals[:, None] > 0)
    terms = np.zeros_like(probs)
    positive = probs > 0
    terms[positive] = probs[positive] * np.log2(probs[positive])
    return float(-np.sum(totals * terms.sum(axis=1)) / totals.sum())


def main() -> None:
    if sha256(PROTOCOL) != EXPECTED_PROTOCOL:
        raise RuntimeError("Protocol hash mismatch")
    if sha256(DEVELOPMENT) != EXPECTED_DEVELOPMENT:
        raise RuntimeError("Development-data hash mismatch")

    source = np.load(DEVELOPMENT, allow_pickle=False)
    sequences = [source["r9__gaps"], source["r10__gaps"]]
    if any(int(g.max()) >= RAW_ALPHABET for g in sequences):
        raise AssertionError("Development gap exceeds frozen raw alphabet")

    arrays: dict[str, np.ndarray] = {}
    raw_marginal = np.zeros(RAW_ALPHABET, dtype=np.int64)
    raw_transition = np.zeros((RAW_ALPHABET, RAW_ALPHABET), dtype=np.int64)
    raw_events = 0
    for gaps in sequences:
        raw_marginal += np.bincount(gaps.astype(np.int64), minlength=RAW_ALPHABET)
        np.add.at(raw_transition, (gaps[:-1].astype(np.int64), gaps[1:].astype(np.int64)), 1)
        raw_events += len(gaps) - 1
    arrays["raw__marginal"] = raw_marginal
    arrays["raw__transition"] = raw_transition

    bin_summary = {}
    for bins in BINS:
        marginal = np.zeros(bins, dtype=np.int64)
        m1 = np.zeros((bins, bins), dtype=np.int64)
        m2 = np.zeros((bins, bins, bins), dtype=np.int64)
        sequence_lengths = []
        for gaps in sequences:
            state = ara_bins(gaps, bins).astype(np.int64)
            sequence_lengths.append(len(state))
            marginal += np.bincount(state, minlength=bins)
            np.add.at(m1, (state[:-1], state[1:]), 1)
            np.add.at(m2, (state[:-2], state[1:-1], state[2:]), 1)
        arrays[f"b{bins}__marginal"] = marginal
        arrays[f"b{bins}__m1"] = m1
        arrays[f"b{bins}__m2"] = m2
        h_next_given_current = conditional_entropy_bits(m1)
        h_next_given_two = conditional_entropy_bits(m2)
        bin_summary[str(bins)] = {
            "sequence_lengths_r9_r10": sequence_lengths,
            "marginal_events": int(marginal.sum()),
            "m1_events": int(m1.sum()),
            "m2_events": int(m2.sum()),
            "occupied_m1_contexts": int(np.count_nonzero(m1.sum(axis=1))),
            "occupied_m2_contexts": int(np.count_nonzero(m2.sum(axis=2))),
            "marginal_entropy_bits": entropy_bits(marginal),
            "empirical_h_next_given_current_bits": h_next_given_current,
            "empirical_h_next_given_two_bits": h_next_given_two,
            "empirical_conditional_memory_gain_bits": h_next_given_current - h_next_given_two,
        }

    np.savez_compressed(OUT_NPZ, **arrays)
    packet = {
        "test_id": "PN7C/FROZEN-DEVELOPMENT-MODELS/R9-R10",
        "protocol_sha256": EXPECTED_PROTOCOL,
        "development_npz_sha256": EXPECTED_DEVELOPMENT,
        "model_npz_sha256": sha256(OUT_NPZ),
        "builder_sha256": sha256(Path(__file__)),
        "r11_constructed_when_frozen": False,
        "r12_opened": False,
        "p31_wheel_opened": False,
        "settings": {
            "bins": list(BINS),
            "dirichlet_alpha": ALPHA,
            "raw_gap_alphabet": RAW_ALPHABET,
            "raw_gap_shrinkage_lambda": RAW_LAMBDA,
            "cross_rung_transitions_excluded": True,
        },
        "raw": {
            "marginal_events": int(raw_marginal.sum()),
            "transition_events": int(raw_transition.sum()),
            "expected_transition_events": raw_events,
            "occupied_gap_values": int(np.count_nonzero(raw_marginal)),
            "maximum_observed_gap": int(max(int(g.max()) for g in sequences)),
        },
        "ara": bin_summary,
    }
    if packet["raw"]["transition_events"] != raw_events:
        raise AssertionError("Raw transition boundary accounting failed")
    OUT_JSON.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(packet, indent=2), flush=True)


if __name__ == "__main__":
    main()

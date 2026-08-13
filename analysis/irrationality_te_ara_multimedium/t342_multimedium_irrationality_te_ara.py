#!/usr/bin/env python3
"""T342: frozen multi-medium Irrationality TE-ARA movement-grammar test."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
import warnings
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
VENDOR = HERE / "vendor"
if VENDOR.exists():
    sys.path.insert(0, str(VENDOR))

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from scipy.io import loadmat, wavfile


STEM = "T342_MULTIMEDIUM_IRRATIONALITY_TE_ARA"
PROTOCOL = HERE / f"{STEM}_PROTOCOL_v1_FROZEN.md"
ADDENDUM = HERE / f"{STEM}_COMPUTATIONAL_ADDENDUM_v1_FROZEN.md"
SOURCE = HERE / "source_data"
OUT_RESULTS = HERE / f"{STEM}_RESULTS.json"
OUT_SUMMARY = HERE / f"{STEM}_SUMMARY.csv"
OUT_QUALITY = HERE / f"{STEM}_DATA_QUALITY.csv"
OUT_QUADRANTS = HERE / f"{STEM}_QUADRANTS.csv"
OUT_TRANSITIONS = HERE / f"{STEM}_TRANSITIONS.csv"
OUT_NULLS = HERE / f"{STEM}_NULLS.csv"
OUT_LANDMARKS = HERE / f"{STEM}_LANDMARKS.csv"
OUT_SENSITIVITY = HERE / f"{STEM}_CONE_SENSITIVITY.csv"
OUT_SAMPLE = HERE / f"{STEM}_EVENT_SAMPLE.csv"
OUT_MANIFEST = HERE / f"{STEM}_SOURCE_MANIFEST.json"
OUT_FIGURE = HERE / f"{STEM}_FIGURE.png"
OUT_HTML = HERE / f"{STEM}_EXPLORER.html"
OUT_REPORT = HERE / f"{STEM}_REPORT_2026-08-05.md"

EXPECTED_PROTOCOL_HASH = "75AE1A2227DE7F393CF66B669D1C3E903F847D138BDE9C0BED4F60E1D67FE8E2"
EXPECTED_ADDENDUM_HASH = "EC9BDCA707182DDA850A630AB2E1B4B2D853B22B645EA280F6AF17EE8DDB27CE"
PHI = (1.0 + math.sqrt(5.0)) / 2.0
TAU_PHI = PHI ** -2
PLASTIC = 1.324717957244746
EPS = 1e-12
BLOCK = 256
CAP = 100_000
SHUFFLES = 1000
SEED = 3422026
SPLITS = ("calibration", "evaluation", "holdout")
SECTOR_NAMES = (
    "contracting_reverse",
    "expanding_reverse",
    "expanding_forward",
    "contracting_forward",
)
RADIAL = {
    "plastic": PLASTIC,
    "sqrt2": math.sqrt(2.0),
    "three_halves": 1.5,
    "phi": PHI,
    "octave": 2.0,
    "e": math.e,
}
ANGULAR = {
    "quarter": 0.25,
    "third": 1.0 / 3.0,
    "one_over_e": 1.0 / math.e,
    "three_eighths": 3.0 / 8.0,
    "phi_inverse_squared": TAU_PHI,
    "two_fifths": 0.4,
    "sqrt2_minus_1": math.sqrt(2.0) - 1.0,
}


@dataclass
class Block:
    domain: str
    split: str
    lineage: str
    start: int
    a: np.ndarray
    b: np.ndarray

    @property
    def sectors(self) -> np.ndarray:
        return sectors_from_ab(self.a, self.b)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def aggregate_hash(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for path in sorted(paths, key=lambda p: str(p).lower()):
        h.update(str(path).encode("utf-8"))
        h.update(bytes.fromhex(sha256(path)))
    return h.hexdigest().upper()


def wrap(x: np.ndarray) -> np.ndarray:
    return np.arctan2(np.sin(x), np.cos(x))


def circular_mean(x: np.ndarray) -> float:
    return float(np.arctan2(np.mean(np.sin(x)), np.mean(np.cos(x))))


def split_bounds(n: int) -> dict[str, tuple[int, int]]:
    c = max(2, int(math.floor(0.4 * n)))
    e = max(c + 2, int(math.floor(0.7 * n)))
    e = min(e, n - 2)
    return {"calibration": (0, c), "evaluation": (c, e), "holdout": (e, n)}


def q95_abs(x: np.ndarray) -> float:
    x = np.abs(x[np.isfinite(x)])
    return float(np.quantile(x, 0.95)) if len(x) else 0.0


def sectors_from_ab(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    out = np.full(len(a), -1, dtype=np.int8)
    good = (np.abs(a) > EPS) & (np.abs(b) > EPS) & np.isfinite(a) & np.isfinite(b)
    # Frozen cyclic order: CR -> ER -> EF -> CF.
    out[good & (a < 0) & (b < 0)] = 0
    out[good & (a > 0) & (b < 0)] = 1
    out[good & (a > 0) & (b > 0)] = 2
    out[good & (a < 0) & (b > 0)] = 3
    return out


def append_blocks(
    blocks: list[Block],
    domain: str,
    split: str,
    lineage: str,
    a: np.ndarray,
    b: np.ndarray,
    valid: np.ndarray,
    source_indices: np.ndarray,
) -> None:
    sec = sectors_from_ab(a, b)
    good = valid & (sec >= 0)
    indices = np.flatnonzero(good)
    if not len(indices):
        return
    breaks = np.flatnonzero(np.diff(source_indices[indices]) != 1) + 1
    for run in np.split(indices, breaks):
        for left in range(0, len(run), BLOCK):
            part = run[left:left + BLOCK]
            if len(part) >= 2:
                blocks.append(Block(domain, split, lineage, int(source_indices[part[0]]), a[part].astype(np.float32), b[part].astype(np.float32)))


def process_z_lineage(
    domain: str,
    lineage: str,
    z: np.ndarray,
    state_valid: np.ndarray | None = None,
    continuity: np.ndarray | None = None,
) -> tuple[list[Block], list[dict]]:
    z = np.asarray(z, dtype=np.complex128)
    n = len(z)
    if state_valid is None:
        state_valid = np.isfinite(z.real) & np.isfinite(z.imag)
    if continuity is None:
        continuity = np.ones(max(0, n - 1), dtype=bool)
    bounds = split_bounds(n)
    cal_start, cal_stop = bounds["calibration"]
    cal_amp = np.abs(z[cal_start:cal_stop])
    positive = cal_amp[np.isfinite(cal_amp) & (cal_amp > 0)]
    floor = max(EPS, float(np.quantile(positive, 0.05)) if len(positive) else EPS)
    blocks: list[Block] = []
    quality: list[dict] = []
    for split, (start, stop) in bounds.items():
        left = np.arange(start, max(start, stop - 1), dtype=np.int64)
        if not len(left):
            continue
        good = (
            state_valid[left]
            & state_valid[left + 1]
            & continuity[left]
            & (np.abs(z[left]) > floor)
            & (np.abs(z[left + 1]) > floor)
        )
        q = np.full(len(left), np.nan + 1j * np.nan, dtype=np.complex128)
        q[good] = z[left[good] + 1] / z[left[good]]
        a = np.full(len(left), np.nan)
        b = np.full(len(left), np.nan)
        a[good] = np.log(np.abs(q[good]))
        b[good] = np.angle(q[good])
        sec = sectors_from_ab(a, b)
        counts = np.bincount(sec[sec >= 0], minlength=4)
        quality.append({
            "domain": domain,
            "split": split,
            "lineage": lineage,
            "raw_states": stop - start,
            "candidate_q": len(left),
            "amplitude_floor": floor,
            "valid_q": int(good.sum()),
            "boundary_q": int((good & (sec < 0)).sum()),
            **{f"full_{SECTOR_NAMES[i]}": int(counts[i]) for i in range(4)},
        })
        append_blocks(blocks, domain, split, lineage, a, b, good, left)
    return blocks, quality


def standardize_lineage(
    u: np.ndarray,
    v: np.ndarray,
    u_origin: str = "median",
    v_origin: str = "median",
    shared_scale: bool = False,
    angle_u: bool = False,
) -> np.ndarray | None:
    u = np.asarray(u, dtype=float)
    v = np.asarray(v, dtype=float)
    n = len(u)
    c = split_bounds(n)["calibration"][1]
    uc = u[:c][np.isfinite(u[:c])]
    vc = v[:c][np.isfinite(v[:c])]
    if not len(uc) or not len(vc):
        return None
    if u_origin == "zero":
        mu = 0.0
    elif angle_u:
        mu = circular_mean(uc)
    else:
        mu = float(np.median(uc))
    mv = 0.0 if v_origin == "zero" else float(np.median(vc))
    du = wrap(u - mu) if angle_u else u - mu
    dv = v - mv
    su = q95_abs(du[:c])
    sv = q95_abs(dv[:c])
    if shared_scale:
        s = max(su, sv)
        su = sv = s
    if su <= EPS or sv <= EPS:
        return None
    return du / su + 1j * dv / sv


def load_pendulum() -> tuple[list[Block], list[dict], list[Path]]:
    data = REPO / "analysis" / "pendulum_scripts" / "data"
    paths = [data / x for x in ("pend_triple.mat", "tri2.mat", "tri3.mat")]
    blocks: list[Block] = []
    quality: list[dict] = []
    for run_i, path in enumerate(paths, 1):
        m = loadmat(path)
        for arm in (1, 2, 3):
            th = np.asarray(m[f"Theta{arm}"]).ravel()
            vel = np.asarray(m[f"dTheta{arm}"]).ravel()
            z = standardize_lineage(th, vel, u_origin="median", v_origin="zero", angle_u=True)
            if z is None:
                continue
            b, q = process_z_lineage("pendulum", f"run{run_i}_arm{arm}", z)
            blocks.extend(b); quality.extend(q)
    return blocks, quality, paths


def load_hydraulic() -> tuple[list[Block], list[dict], list[Path]]:
    base = REPO / "analysis" / "hydraulics" / "public_data" / "extracted"
    paths = [base / "PS1.txt", base / "PS2.txt"]
    ps1 = np.loadtxt(paths[0], dtype=np.float32)
    ps2 = np.loadtxt(paths[1], dtype=np.float32)
    if ps1.shape != ps2.shape:
        raise RuntimeError("Hydraulic PS1/PS2 shape mismatch")
    blocks: list[Block] = []
    quality: list[dict] = []
    for cycle in range(ps1.shape[0]):
        z = standardize_lineage(ps1[cycle], ps2[cycle], shared_scale=False)
        if z is None:
            continue
        b, q = process_z_lineage("hydraulic", f"cycle_{cycle:04d}", z)
        blocks.extend(b); quality.extend(q)
    return blocks, quality, paths


def load_bubbles() -> tuple[list[Block], list[dict], list[Path]]:
    base = REPO / "analysis" / "vertical_ara_bubbles" / "source_data"
    paths = sorted(base.glob("V*.csv"))
    blocks: list[Block] = []
    quality: list[dict] = []
    lineage_counter = 0
    for path in paths:
        frame = pd.read_csv(path, usecols=["video_name", "frame_number", "ID", "x_velocity [m/s]", "y_velocity [m/s]"])
        frame = frame.sort_values(["video_name", "ID", "frame_number"])
        for (video, ident), group in frame.groupby(["video_name", "ID"], sort=False):
            group = group.drop_duplicates("frame_number", keep="first")
            frames = group["frame_number"].to_numpy(int)
            breaks = np.flatnonzero(np.diff(frames) != 1) + 1
            for piece in np.split(np.arange(len(group)), breaks):
                if len(piece) < 8:
                    continue
                part = group.iloc[piece]
                u = part["x_velocity [m/s]"].to_numpy(float)
                v = part["y_velocity [m/s]"].to_numpy(float)
                z = standardize_lineage(u, v, u_origin="zero", v_origin="zero", shared_scale=True)
                if z is None:
                    continue
                lineage_counter += 1
                name = f"{path.stem}:{Path(str(video)).stem}:{ident}:{lineage_counter}"
                b, q = process_z_lineage("bubbles", name, z)
                blocks.extend(b); quality.extend(q)
    return blocks, quality, paths


def parse_cold(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    stamps: list[np.datetime64] = []
    temp: list[float] = []
    humid: list[float] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            parts = line.strip().split(";")
            if len(parts) != 4 or parts[0].lower().startswith("date"):
                continue
            try:
                d, t, a, b = parts
                day, month, year = d.split(".")
                stamps.append(np.datetime64(f"{year}-{month}-{day}T{t}"))
                temp.append(float(a.replace(",", ".")))
                humid.append(float(b.replace(",", ".")))
            except (ValueError, TypeError):
                continue
    ts = np.asarray(stamps)
    order = np.argsort(ts, kind="stable")
    return ts[order], np.asarray(temp)[order], np.asarray(humid)[order]


def load_cold_room() -> tuple[list[Block], list[dict], list[Path]]:
    base = SOURCE / "cold_room" / "raw"
    paths = sorted(base.glob("SENSOR*.CSV"))
    blocks: list[Block] = []
    quality: list[dict] = []
    for path in paths:
        ts, temp, humid = parse_cold(path)
        keep = np.concatenate(([True], ts[1:] != ts[:-1]))
        ts, temp, humid = ts[keep], temp[keep], humid[keep]
        z = standardize_lineage(temp, humid)
        if z is None:
            continue
        dt = np.diff(ts).astype("timedelta64[s]").astype(np.int64)
        continuity = (dt > 0) & (dt <= 10)
        state_valid = np.isfinite(temp) & np.isfinite(humid)
        b, q = process_z_lineage("cold_room", path.stem.lower(), z, state_valid, continuity)
        blocks.extend(b); quality.extend(q)
    return blocks, quality, paths + [SOURCE / "cold_room" / "experiment_actions.csv", SOURCE / "cold_room" / "Raw.zip"]


def load_acoustics() -> tuple[list[Block], list[dict], list[Path]]:
    paths = sorted((SOURCE / "acoustics").glob("*.wav"))
    blocks: list[Block] = []
    quality: list[dict] = []
    for path in paths:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _, x = wavfile.read(path)
        if x.ndim != 2 or x.shape[1] < 2:
            continue
        x = x[:, :2].astype(np.float64)
        joint = np.max(np.abs(x), axis=1)
        onset = int(np.argmax(joint))
        x = x[onset:]
        peak = float(np.max(np.abs(x)))
        if peak <= 0:
            continue
        z = x[:, 0] / peak + 1j * x[:, 1] / peak
        b, q = process_z_lineage("acoustics", path.stem, z)
        blocks.extend(b); quality.extend(q)
    return blocks, quality, paths


def load_qutrit() -> tuple[list[Block], list[dict], list[Path]]:
    path = REPO / "analysis" / "quantum" / "Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_EVENTS.npz"
    archive = np.load(path)
    blocks: list[Block] = []
    quality: list[dict] = []
    for plane in ("psi0_psi1", "psi1_psi2", "psi2_psi0"):
        time = np.asarray(archive[f"{plane}_time"], dtype=np.int64)
        residual = np.asarray(archive[f"{plane}_residual"], dtype=float)
        amp = np.asarray(archive[f"{plane}_circle_strength"], dtype=float)
        heading = np.asarray(archive[f"{plane}_circle_heading"], dtype=float)
        z = amp * np.exp(2j * math.pi * heading)
        valid = np.isfinite(amp) & np.isfinite(heading) & np.isfinite(residual) & (amp >= 0.01) & (residual <= 0.25)
        continuity = np.diff(time) <= 2200
        b, q = process_z_lineage("qutrit", plane, z, valid, continuity)
        blocks.extend(b); quality.extend(q)
    return blocks, quality, [path]


def load_river() -> tuple[list[Block], list[dict], list[Path]]:
    path = REPO / "analysis" / "hydraulics" / "results" / "T335_RIVER_IRRATIONALITY_DI_ARA_EVENTS.csv"
    frame = pd.read_csv(path)
    frame = frame[frame["source_kind"] == "observed"].copy()
    blocks: list[Block] = []
    quality: list[dict] = []
    for (rank, split), group in frame.groupby(["elevation_rank", "split"], sort=True):
        group = group.sort_values("event_index")
        s = group["scale_ratio_s"].to_numpy(float)
        b = wrap(group["turn_delta_rad"].to_numpy(float))
        a = np.log(s)
        sec = sectors_from_ab(a, b)
        good = np.isfinite(a) & np.isfinite(b) & (sec >= 0)
        counts = np.bincount(sec[good], minlength=4)
        lineage = f"rank_{int(rank):02d}"
        quality.append({
            "domain": "river",
            "split": split,
            "lineage": lineage,
            "raw_states": len(group),
            "candidate_q": len(group),
            "amplitude_floor": 0.0,
            "valid_q": int(good.sum()),
            "boundary_q": int((~good & np.isfinite(a) & np.isfinite(b)).sum()),
            **{f"full_{SECTOR_NAMES[i]}": int(counts[i]) for i in range(4)},
        })
        idx = group["event_index"].to_numpy(int)
        append_blocks(blocks, "river", split, lineage, a, b, good, idx)
    return blocks, quality, [path]


def cap_blocks(blocks: list[Block]) -> list[Block]:
    grouped: dict[tuple[str, str], list[Block]] = defaultdict(list)
    for block in blocks:
        grouped[(block.split, block.lineage)].append(block)
    selected: list[Block] = []
    for split in SPLITS:
        by_lineage = {lin: sorted(vals, key=lambda x: x.start) for (sp, lin), vals in grouped.items() if sp == split}
        total = sum(len(b.a) for vals in by_lineage.values() for b in vals)
        if total <= CAP:
            selected.extend(b for vals in by_lineage.values() for b in vals)
            continue
        names = sorted(by_lineage)
        base = CAP // len(names)
        extra = CAP % len(names)
        for pos, name in enumerate(names):
            quota = base + (1 if pos < extra else 0)
            if quota < 2:
                continue
            vals = by_lineage[name]
            available = sum(len(x.a) for x in vals)
            if available <= quota:
                selected.extend(vals)
                continue
            need_blocks = max(1, math.ceil(quota / BLOCK))
            ranks = np.unique(np.linspace(0, len(vals) - 1, min(need_blocks, len(vals))).round().astype(int))
            remaining = quota
            for rank in ranks:
                b = vals[int(rank)]
                take = min(len(b.a), remaining)
                if take >= 2:
                    selected.append(Block(b.domain, b.split, b.lineage, b.start, b.a[:take], b.b[:take]))
                    remaining -= take
                if remaining < 2:
                    break
            if remaining >= 2:
                chosen = set(int(x) for x in ranks)
                for rank, b in enumerate(vals):
                    if rank in chosen:
                        continue
                    take = min(len(b.a), remaining)
                    if take >= 2:
                        selected.append(Block(b.domain, b.split, b.lineage, b.start, b.a[:take], b.b[:take]))
                        remaining -= take
                    if remaining < 2:
                        break
    return selected


def transition_table(sequences: list[np.ndarray]) -> np.ndarray:
    table = np.zeros((4, 4), dtype=np.int64)
    for seq in sequences:
        if len(seq) < 2:
            continue
        table += np.bincount(4 * seq[:-1] + seq[1:], minlength=16).reshape(4, 4)
    return table


def table_metrics(table: np.ndarray) -> dict[str, float | int]:
    n = int(table.sum())
    changed = int(n - np.trace(table))
    adjacent = 0
    diagonal = 0
    clockwise = 0
    counter = 0
    for i in range(4):
        for j in range(4):
            diff = (j - i) % 4
            if diff in (1, 3):
                adjacent += int(table[i, j])
                clockwise += int(table[i, j]) if diff == 1 else 0
                counter += int(table[i, j]) if diff == 3 else 0
            elif diff == 2:
                diagonal += int(table[i, j])
    denom = adjacent + diagonal
    adjacency = adjacent / denom if denom else float("nan")
    p = table / n if n else np.zeros_like(table, dtype=float)
    px = p.sum(axis=1, keepdims=True)
    py = p.sum(axis=0, keepdims=True)
    expected = px @ py
    nz = p > 0
    mi = float(np.sum(p[nz] * np.log(p[nz] / expected[nz]))) if n else float("nan")
    pyv = py.ravel()
    hy = float(-np.sum(pyv[pyv > 0] * np.log(pyv[pyv > 0])))
    nmi = mi / hy if hy > 0 else float("nan")
    return {
        "transitions": n,
        "changed_transitions": changed,
        "adjacent_transitions": adjacent,
        "diagonal_transitions": diagonal,
        "adjacency_fraction": adjacency,
        "same_sector_fraction": float(np.trace(table) / n) if n else float("nan"),
        "clockwise_adjacent": clockwise,
        "counterclockwise_adjacent": counter,
        "normalized_mutual_information": nmi,
    }


def shuffled_null(sequences: list[np.ndarray], seed: int) -> tuple[pd.DataFrame, np.ndarray]:
    rng = np.random.default_rng(seed)
    rows = []
    for rep in range(SHUFFLES):
        shuffled = [rng.permutation(seq) for seq in sequences]
        met = table_metrics(transition_table(shuffled))
        rows.append({"replicate": rep, "adjacency_fraction": met["adjacency_fraction"], "normalized_mutual_information": met["normalized_mutual_information"]})
    return pd.DataFrame(rows), transition_table(sequences)


def landmark_rows(domain: str, split: str, blocks: list[Block], fitted: tuple[float, float]) -> tuple[dict, list[dict]]:
    a = np.concatenate([b.a for b in blocks])
    delta = np.concatenate([b.b for b in blocks])
    s = np.exp(a)
    x = 2.0 * s / (1.0 + s)
    y = 1.0 + delta / math.pi
    gamma = np.degrees(np.arctan2(np.abs(y - 1.0), np.abs(x - 1.0)))
    r = np.abs(a)
    c = np.abs(delta) / (2.0 * math.pi)
    line = gamma <= 15.0
    circle = gamma >= 75.0
    rmed = float(np.median(r[line])) if line.any() else float("nan")
    cmed = float(np.median(c[circle])) if circle.any() else float("nan")
    rscores = {name: abs(rmed - math.log(value)) for name, value in RADIAL.items()}
    cscores = {name: abs(cmed - value) for name, value in ANGULAR.items()}
    rwinner = min(rscores, key=rscores.get) if math.isfinite(rmed) else "ineligible"
    cwinner = min(cscores, key=cscores.get) if math.isfinite(cmed) else "ineligible"
    line_eligible = int(line.sum()) >= 30 and int(((a < -EPS) & line).sum()) >= 10 and int(((a > EPS) & line).sum()) >= 10
    circle_eligible = int(circle.sum()) >= 30 and int(((delta < -EPS) & circle).sum()) >= 10 and int(((delta > EPS) & circle).sum()) >= 10
    fit_r, fit_c = fitted
    line_fixed = bool(line_eligible and rwinner == "e" and rscores["e"] <= 0.10)
    circle_fixed = bool(circle_eligible and cwinner == "phi_inverse_squared" and cscores["phi_inverse_squared"] <= 0.05)
    row = {
        "domain": domain, "split": split,
        "line_n": int(line.sum()), "line_R_median": rmed,
        "line_s_equivalent": float(math.exp(rmed)) if math.isfinite(rmed) else float("nan"),
        "line_winner": rwinner, "line_e_error": rscores.get("e", float("nan")),
        "line_fitted_calibration_R": fit_r,
        "line_fitted_error": abs(rmed - fit_r) if math.isfinite(fit_r) and math.isfinite(rmed) else float("nan"),
        "line_eligible": line_eligible, "line_fixed_pass": line_fixed,
        "line_strong_pass": bool(line_fixed and rscores["e"] <= abs(rmed - fit_r)),
        "circle_n": int(circle.sum()), "circle_C_median_turns": cmed,
        "circle_winner": cwinner, "circle_phi_error": cscores.get("phi_inverse_squared", float("nan")),
        "circle_fitted_calibration_C": fit_c,
        "circle_fitted_error": abs(cmed - fit_c) if math.isfinite(fit_c) and math.isfinite(cmed) else float("nan"),
        "circle_eligible": circle_eligible, "circle_fixed_pass": circle_fixed,
        "circle_strong_pass": bool(circle_fixed and cscores["phi_inverse_squared"] <= abs(cmed - fit_c)),
        "median_X": float(np.median(x)), "median_Y": float(np.median(y)),
    }
    sens = []
    for degrees in (10.0, 15.0, 20.0):
        lm = gamma <= degrees
        cm = gamma >= 90.0 - degrees
        sens.append({
            "domain": domain, "split": split, "cone_degrees": degrees,
            "line_n": int(lm.sum()), "line_R_median": float(np.median(r[lm])) if lm.any() else float("nan"),
            "circle_n": int(cm.sum()), "circle_C_median_turns": float(np.median(c[cm])) if cm.any() else float("nan"),
        })
    return row, sens


def transformed_metrics(blocks: list[Block], mode: str) -> dict:
    seqs = []
    for block in blocks:
        a, b = block.a, block.b
        if mode == "reverse_time":
            a, b = -a[::-1], -b[::-1]
        elif mode == "swap_axes":
            a, b = a, -b
        elif mode == "reverse_poles":
            a, b = a, b
        else:
            raise KeyError(mode)
        sec = sectors_from_ab(a, b)
        seqs.append(sec[sec >= 0])
    return table_metrics(transition_table(seqs))


def analyze_domain(domain: str, blocks: list[Block], quality: list[dict], offset: int) -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict], list[dict]]:
    selected = cap_blocks(blocks)
    summary_rows: list[dict] = []
    quadrant_rows: list[dict] = []
    transition_rows: list[dict] = []
    null_rows: list[dict] = []
    landmark_out: list[dict] = []
    sensitivity: list[dict] = []
    cal_blocks = [b for b in selected if b.split == "calibration"]
    cal_landmark, _ = landmark_rows(domain, "calibration", cal_blocks, (float("nan"), float("nan")))
    fitted = (cal_landmark["line_R_median"], cal_landmark["circle_C_median_turns"])
    for split_idx, split in enumerate(SPLITS):
        part = [b for b in selected if b.split == split]
        seqs = [b.sectors for b in part]
        null, table = shuffled_null(seqs, SEED + 1000 * offset + split_idx)
        met = table_metrics(table)
        states = np.concatenate(seqs) if seqs else np.empty(0, dtype=np.int8)
        counts = np.bincount(states, minlength=4)
        shares = counts / counts.sum() if counts.sum() else np.zeros(4)
        adjacency_p = float((1 + np.count_nonzero(null["adjacency_fraction"].to_numpy() >= met["adjacency_fraction"])) / (SHUFFLES + 1))
        nmi_p = float((1 + np.count_nonzero(null["normalized_mutual_information"].to_numpy() >= met["normalized_mutual_information"])) / (SHUFFLES + 1))
        eligible = bool(met["transitions"] >= 1000 and met["changed_transitions"] >= 100 and np.all(counts > 0))
        # Coverage is its own usability result.  Inferential eligibility remains
        # a separate domain-pass gate, exactly as frozen in protocol sections
        # 4.1 and 4.6.
        coverage_pass = bool(np.all(shares >= 0.01))
        grammar_pass = bool(eligible and coverage_pass and adjacency_p < 0.05 and nmi_p < 0.05)
        sym = {mode: transformed_metrics(part, mode) for mode in ("reverse_time", "swap_axes", "reverse_poles")}
        sym_delta = max(
            abs(float(sym[m]["adjacency_fraction"]) - float(met["adjacency_fraction"]))
            if math.isfinite(float(met["adjacency_fraction"])) else 0.0
            for m in sym
        )
        row = {
            "domain": domain, "split": split,
            "selected_blocks": len(part), "selected_states": int(len(states)),
            **met,
            "adjacency_shuffle_p": adjacency_p,
            "nmi_shuffle_p": nmi_p,
            "eligible": eligible,
            "coverage_pass": coverage_pass,
            "grammar_pass": grammar_pass,
            "symmetry_max_adjacency_delta": sym_delta,
            "reverse_time_nmi": sym["reverse_time"]["normalized_mutual_information"],
            "swap_axes_nmi": sym["swap_axes"]["normalized_mutual_information"],
            "reverse_poles_nmi": sym["reverse_poles"]["normalized_mutual_information"],
        }
        summary_rows.append(row)
        for i, name in enumerate(SECTOR_NAMES):
            quadrant_rows.append({"domain": domain, "split": split, "sector": name, "count": int(counts[i]), "share": float(shares[i])})
        for i in range(4):
            for j in range(4):
                transition_rows.append({"domain": domain, "split": split, "from_sector": SECTOR_NAMES[i], "to_sector": SECTOR_NAMES[j], "count": int(table[i, j])})
        for record in null.to_dict("records"):
            null_rows.append({"domain": domain, "split": split, **record})
        lm, sens = landmark_rows(domain, split, part, fitted)
        landmark_out.append(lm); sensitivity.extend(sens)

    # Samples are selected uniformly from holdout blocks for durable plots.
    sample_rows = []
    hold = [b for b in selected if b.split == "holdout"]
    flat = [(b, i) for b in hold for i in range(len(b.a))]
    if flat:
        picks = np.unique(np.linspace(0, len(flat) - 1, min(1000, len(flat))).round().astype(int))
        for p in picks:
            block, i = flat[int(p)]
            a = float(block.a[i]); bval = float(block.b[i]); s = math.exp(a)
            sample_rows.append({
                "domain": domain, "split": "holdout", "lineage": block.lineage,
                "block_start": block.start, "a_log_radial": a, "b_delta_rad": bval,
                "x_radial_ara": 2.0 * s / (1.0 + s), "y_angular_ara": 1.0 + bval / math.pi,
                "sector": SECTOR_NAMES[int(sectors_from_ab(np.array([a]), np.array([bval]))[0])],
            })
    return summary_rows, quadrant_rows, transition_rows, null_rows, landmark_out + sample_rows, sensitivity


def file_manifest(source_paths: dict[str, list[Path]]) -> dict:
    files = {}
    for domain, paths in source_paths.items():
        entries = []
        for path in sorted(set(paths), key=lambda p: str(p).lower()):
            entries.append({"path": str(path.relative_to(REPO)), "bytes": path.stat().st_size, "sha256": sha256(path)})
        files[domain] = {"files": entries, "aggregate_sha256": aggregate_hash(sorted(set(paths), key=lambda p: str(p).lower()))}
    return {
        "protocol_sha256": sha256(PROTOCOL),
        "computational_addendum_sha256": sha256(ADDENDUM),
        "sources": files,
    }


def draw_figure(summary: pd.DataFrame, quadrants: pd.DataFrame, landmarks: pd.DataFrame) -> None:
    W, H = 1800, 1280
    img = Image.new("RGB", (W, H), "#f5f7fa")
    d = ImageDraw.Draw(img)
    font_paths = [Path("C:/Windows/Fonts/segoeui.ttf"), Path("C:/Windows/Fonts/arial.ttf")]
    font_path = next((p for p in font_paths if p.exists()), None)
    def f(size, bold=False):
        p = Path("C:/Windows/Fonts/segoeuib.ttf") if bold and Path("C:/Windows/Fonts/segoeuib.ttf").exists() else font_path
        return ImageFont.truetype(str(p), size) if p else ImageFont.load_default()
    title, sub, body, small = f(44, True), f(24), f(19), f(16)
    d.text((60, 38), "T342 — Irrationality TE-ARA across seven media", fill="#172033", font=title)
    d.text((60, 98), "Four mixed regions by identity · auxiliary common-gait audit shown separately", fill="#596579", font=sub)
    hold = summary[summary["split"] == "holdout"].sort_values("domain")
    pass_n = int(hold["grammar_pass"].sum())
    eligible_n = int(hold["eligible"].sum())
    coverage_n = int(hold["coverage_pass"].sum())
    d.rounded_rectangle((60, 145, 1740, 250), radius=18, fill="#e8eef7")
    d.text((90, 160), f"Di-ARA geometry: {coverage_n}/{len(hold)} holdouts populate all four mixed regions", fill="#172033", font=f(27, True))
    d.text((90, 205), f"Auxiliary identical-gait audit: {pass_n}/{eligible_n} eligible pass (not the intended coupling test)", fill="#596579", font=f(20, True))
    colors = ["#4c78a8", "#f58518", "#54a24b", "#e45756"]
    x0, y0 = 70, 285
    card_w, card_h, gap = 235, 500, 10
    for k, (_, row) in enumerate(hold.iterrows()):
        x = x0 + k * (card_w + gap)
        d.rounded_rectangle((x, y0, x + card_w, y0 + card_h), radius=14, fill="white", outline="#d4dbe5")
        d.text((x + 15, y0 + 14), str(row["domain"]), fill="#172033", font=f(20, True))
        verdict = "BOTH AUX TESTS" if bool(row["grammar_pass"]) else ("SMALL SAMPLE" if not bool(row["eligible"]) else "IDENTITY-SPECIFIC")
        vc = "#16794a" if bool(row["grammar_pass"]) else ("#8a6d1d" if not bool(row["eligible"]) else "#596579")
        d.text((x + 15, y0 + 48), verdict, fill=vc, font=f(15, True))
        q = quadrants[(quadrants.domain == row.domain) & (quadrants.split == "holdout")]
        by = {r.sector: r.share for r in q.itertuples()}
        bar_top = y0 + 105
        for i, name in enumerate(SECTOR_NAMES):
            share = float(by.get(name, 0.0))
            yy = bar_top + i * 58
            d.text((x + 15, yy), name.replace("_", " "), fill="#465269", font=small)
            d.rounded_rectangle((x + 15, yy + 23, x + 215, yy + 39), radius=6, fill="#e4e8ef")
            d.rounded_rectangle((x + 15, yy + 23, x + 15 + 200 * min(1, share), yy + 39), radius=6, fill=colors[i])
            d.text((x + 165, yy), f"{100*share:.1f}%", fill="#465269", font=small)
        d.text((x + 15, y0 + 355), f"adjacency {row['adjacency_fraction']:.3f}", fill="#172033", font=body)
        d.text((x + 15, y0 + 386), f"shuffle p {row['adjacency_shuffle_p']:.4f}", fill="#596579", font=small)
        d.text((x + 15, y0 + 421), f"ordered info {row['normalized_mutual_information']:.3f}", fill="#172033", font=body)
        d.text((x + 15, y0 + 452), f"shuffle p {row['nmi_shuffle_p']:.4f}", fill="#596579", font=small)
    y = 830
    d.text((70, y), "Secondary pure-axis landmarks (holdout)", fill="#172033", font=f(27, True))
    d.text((70, y + 40), "These do not control the registered auxiliary verdict.", fill="#596579", font=body)
    lm = landmarks[landmarks["split"] == "holdout"].sort_values("domain")
    headers = ["domain", "line R / winner", "circle turns / winner", "strong e", "strong Phi"]
    widths = [250, 360, 420, 180, 180]
    xx, yy = 70, y + 95
    for head, width in zip(headers, widths):
        d.text((xx, yy), head, fill="#465269", font=f(17, True)); xx += width
    yy += 34
    for row in lm.itertuples():
        vals = [
            row.domain,
            f"{row.line_R_median:.4f} / {row.line_winner}",
            f"{row.circle_C_median_turns:.4f} / {row.circle_winner}",
            "yes" if row.line_strong_pass else "no",
            "yes" if row.circle_strong_pass else "no",
        ]
        xx = 70
        for value, width in zip(vals, widths):
            d.text((xx, yy), str(value), fill="#172033", font=small); xx += width
        d.line((70, yy + 25, 1710, yy + 25), fill="#e0e4eb", width=1)
        yy += 38
    d.text((70, 1238), "Source classes: mechanics · oil pressure · gas–liquid · thermal/humidity · acoustics · qutrit · river path", fill="#6b7484", font=small)
    img.save(OUT_FIGURE)


def write_html(summary: pd.DataFrame, quadrants: pd.DataFrame, transitions: pd.DataFrame, samples: pd.DataFrame) -> None:
    data = {
        "summary": summary[summary.split == "holdout"].replace({np.nan: None}).to_dict("records"),
        "quadrants": quadrants[quadrants.split == "holdout"].replace({np.nan: None}).to_dict("records"),
        "transitions": transitions[transitions.split == "holdout"].replace({np.nan: None}).to_dict("records"),
        "samples": samples.replace({np.nan: None}).to_dict("records"),
    }
    payload = json.dumps(data, separators=(",", ":"))
    html = r'''<!doctype html><html><head><meta charset="utf-8"><title>T342 Irrationality TE-ARA explorer</title><style>
body{margin:0;background:#0d1118;color:#e6edf3;font-family:Segoe UI,Arial,sans-serif}.wrap{max-width:1450px;margin:auto;padding:28px}h1{margin:0 0 8px;font-size:34px}p{color:#9ba7b6}.bar{display:flex;gap:12px;align-items:center;margin:22px 0}select{background:#172130;color:#fff;border:1px solid #39485e;padding:10px 14px;border-radius:8px}.grid{display:grid;grid-template-columns:1.2fr .8fr;gap:16px}.card{background:#131b27;border:1px solid #27354a;border-radius:14px;padding:18px}canvas{width:100%;height:auto;background:#0f1620;border-radius:9px}.metrics{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.metric{background:#0f1620;padding:12px;border-radius:9px}.v{font-size:24px;font-weight:700}.k{color:#93a1b4;font-size:13px}.note{font-size:13px;color:#8996a8}@media(max-width:900px){.grid{grid-template-columns:1fr}}
</style></head><body><div class="wrap"><h1>T342 — Irrationality TE-ARA across media</h1><p>All seven holdouts populate the four mixed regions. The auxiliary common-gait audit is displayed separately and is not the intended intact-pair coupling test.</p><div class="bar"><label>Medium <select id="domain"></select></label><span id="verdict"></span></div><div class="grid"><div class="card"><h2>ARA relation plane</h2><canvas id="scatter" width="820" height="600"></canvas><p class="note">x = radial ARA (0–2), y = angular ARA (0–2). Lines at 1 are the two ridges. ARA does not require one universal traversal order.</p></div><div><div class="card"><h2>Identity-specific transition matrix</h2><canvas id="matrix" width="560" height="480"></canvas></div><div class="card" style="margin-top:16px"><h2>Auxiliary common-gait metrics</h2><div class="metrics" id="metrics"></div></div></div></div></div><script>const DATA=''' + payload + r''';const D=JSON.parse(DATA),sel=document.querySelector('#domain');const domains=D.summary.map(x=>x.domain);domains.forEach(x=>sel.add(new Option(x,x)));const colors={contracting_reverse:'#4c78a8',expanding_reverse:'#f58518',expanding_forward:'#54a24b',contracting_forward:'#e45756'};function draw(){let dom=sel.value,s=D.summary.find(x=>x.domain===dom);document.querySelector('#verdict').textContent=s.grammar_pass?'BOTH AUXILIARY ENDPOINTS':'IDENTITY-SPECIFIC FLOW';if(!s.eligible)document.querySelector('#verdict').textContent='SMALL SAMPLE — DESCRIPTIVE';let c=document.querySelector('#scatter'),x=c.getContext('2d');x.clearRect(0,0,c.width,c.height);x.strokeStyle='#536177';x.lineWidth=2;x.beginPath();x.moveTo(c.width/2,30);x.lineTo(c.width/2,c.height-35);x.moveTo(45,c.height/2);x.lineTo(c.width-25,c.height/2);x.stroke();x.fillStyle='#9ba7b6';x.fillText('0',35,c.height-14);x.fillText('1',c.width/2-3,c.height-14);x.fillText('2',c.width-30,c.height-14);for(const p of D.samples.filter(v=>v.domain===dom)){let xx=45+p.x_radial_ara/2*(c.width-70),yy=c.height-35-p.y_angular_ara/2*(c.height-70);x.globalAlpha=.45;x.fillStyle=colors[p.sector];x.fillRect(xx-2,yy-2,4,4)}x.globalAlpha=1;let m=document.querySelector('#matrix'),g=m.getContext('2d');g.clearRect(0,0,m.width,m.height);let rows=D.transitions.filter(v=>v.domain===dom),mx=Math.max(...rows.map(r=>r.count),1),names=['contracting_reverse','expanding_reverse','expanding_forward','contracting_forward'];rows.forEach(r=>{let i=names.indexOf(r.from_sector),j=names.indexOf(r.to_sector),xx=145+j*92,yy=45+i*92,a=.12+.88*r.count/mx;g.fillStyle=`rgba(70,140,220,${a})`;g.fillRect(xx,yy,82,82);g.fillStyle='#fff';g.fillText(r.count.toLocaleString(),xx+9,yy+44)});g.fillStyle='#9ba7b6';names.forEach((n,i)=>{g.save();g.translate(155+i*92,430);g.rotate(-.6);g.fillText(n.replace('_',' '),0,0);g.restore();g.fillText(n.slice(0,12),8,90+i*92)});document.querySelector('#metrics').innerHTML=[['adjacency',s.adjacency_fraction.toFixed(3)],['adjacency shuffle p',s.adjacency_shuffle_p.toFixed(4)],['ordered information',s.normalized_mutual_information.toFixed(3)],['information shuffle p',s.nmi_shuffle_p.toFixed(4)],['changed transitions',s.changed_transitions.toLocaleString()],['same-sector share',(100*s.same_sector_fraction).toFixed(1)+'%']].map(v=>`<div class=metric><div class=v>${v[1]}</div><div class=k>${v[0]}</div></div>`).join('')}sel.onchange=draw;draw();</script></body></html>'''
    OUT_HTML.write_text(html, encoding="utf-8")


def write_report(summary: pd.DataFrame, landmarks: pd.DataFrame, results: dict) -> None:
    hold = summary[summary.split == "holdout"].sort_values("domain")
    lines = [
        "# T342 — multi-medium Irrationality TE-ARA result",
        "",
        "**Run:** 5 August 2026  ",
        f"**Registered auxiliary verdict:** **{results['primary_verdict']}**  ",
        "**Intended intact-pair Di-ARA coupling claim:** **NOT TESTED BY T342**  ",
        f"**Eligible/pass:** `{results['eligible_domains']}` eligible, `{results['passing_domains']}` pass",
        "",
        "## Result first",
        "",
        results["result_first"],
        "",
        "All seven holdouts populated all four mixed regions under the frozen coordinate. The registered 1/6 result concerns an auxiliary identical-gait rule, not the intended Di-ARA claim that two perpendicular ARA relations form an identity-specific coupled parent.",
        "",
        "## Originator interpretive correction",
        "",
        "After seeing the result visually, Dylan clarified that Di-ARA does not require one neighbour-by-neighbour quadrant order, cadence, speed or proportion across identities. It supplies the two coupled axes and the four mixed regions `Ab`, `aB`, `bA`, `Ba`; the exact movement through them depends on identity and coupling. T342's frozen auxiliary verdict remains unchanged, but the intended intact-pair coupling advantage is **not tested** by T342.",
        "",
        "See `T342_INTERPRETIVE_CORRECTION_ORIGINATOR_CLARIFICATION_2026-08-05.md`. The frozen protocol and addendum were not altered.",
        "",
        "## Holdout auxiliary common-gait audit",
        "",
        "| domain | selected states | four-sector eligible | adjacency | shuffle p | ordered information | shuffle p | verdict |",
        "|---|---:|---|---:|---:|---:|---:|---|",
    ]
    for row in hold.itertuples():
        lines.append(f"| {row.domain} | {row.selected_states:,} | {'yes' if row.eligible else 'no'} | {row.adjacency_fraction:.4f} | {row.adjacency_shuffle_p:.4f} | {row.normalized_mutual_information:.4f} | {row.nmi_shuffle_p:.4f} | {'PASS' if row.grammar_pass else ('INELIGIBLE' if not row.eligible else 'FAIL')} |")
    lines += [
        "",
        "Adjacency excludes same-sector persistence: it asks whether actual handovers go to a neighbouring quadrant rather than jumping diagonally. Ordered information asks how much the present quadrant tells us about the next. These were the frozen auxiliary endpoints. They are retained for reproducibility and must not be read as the framework's required universal gait.",
        "",
        "## Secondary constants",
        "",
        "| domain | line median R | nearest radial | strong e | circle median turns | nearest circular | strong Phi |",
        "|---|---:|---|---|---:|---|---|",
    ]
    for row in landmarks[landmarks.split == "holdout"].sort_values("domain").itertuples():
        lines.append(f"| {row.domain} | {row.line_R_median:.6f} | {row.line_winner} | {'yes' if row.line_strong_pass else 'no'} | {row.circle_C_median_turns:.6f} | {row.circle_winner} | {'yes' if row.circle_strong_pass else 'no'} |")
    lines += [
        "",
        results["landmark_interpretation"],
        "",
        "## What this establishes—and what it does not",
        "",
        "In the recorded qutrit, the chronological-versus-shuffled result is evidence that this two-axis cut retained both local handover preference and ordered state information. Several other domains passed only one endpoint. That does not imply that those identities failed Di-ARA: the frozen auxiliary demanded one particular combination of movement properties that the intended framework does not require universally.",
        "",
        "All seven holdouts occupied all four mixed regions. This is compatible with the intended geometry but is not unique proof: the coordinate itself defines four possible regions, and smooth systems or ordinary state-space dynamics can populate them. The direct empirical question is now whether the intact pair carries more stable transferable information than either child or a broken pairing.",
        "",
        "TE-ARA closure (`X + (2-X) = 2`, and the angular equivalent) is definitional bookkeeping. It is not counted as an empirical pass.",
        "",
        "## Data and evidence boundary",
        "",
        "Cold-room and acoustic numerical files were unopened fresh sources at protocol freeze. Pendulum, hydraulic, bubble, qutrit and river records had been used previously for other ARA questions, so their T342 results are cross-question transfers rather than independent discoveries.",
        "",
        "The cadence-neutral addendum capped each domain/split at 100,000 native ordered states in deterministic non-overlapping blocks. This prevents 44.1 kHz audio from outweighing five-second environmental logging. Domain verdicts are never pooled by row.",
        "",
        "## Reproduction",
        "",
        "```powershell",
        "$env:PYTHONPATH='analysis/irrationality_te_ara_multimedium/vendor'",
        "& 'C:/Users/Dylan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' analysis/irrationality_te_ara_multimedium/t342_multimedium_irrationality_te_ara.py",
        "& 'C:/Users/Dylan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' analysis/irrationality_te_ara_multimedium/validate_t342_multimedium_irrationality_te_ara.py",
        "```",
        "",
        "The ignored fresh public sources can be reacquired with `acquire_t342_public_sources.py`.",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def clean_json(value):
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return None if not math.isfinite(float(value)) else float(value)
    return value


def main() -> None:
    if sha256(PROTOCOL) != EXPECTED_PROTOCOL_HASH:
        raise RuntimeError("T342 protocol hash mismatch")
    if sha256(ADDENDUM) != EXPECTED_ADDENDUM_HASH:
        raise RuntimeError("T342 computational addendum hash mismatch")

    loaders = [
        ("pendulum", load_pendulum),
        ("hydraulic", load_hydraulic),
        ("bubbles", load_bubbles),
        ("cold_room", load_cold_room),
        ("acoustics", load_acoustics),
        ("qutrit", load_qutrit),
        ("river", load_river),
    ]
    all_summary = []
    all_quality = []
    all_quadrants = []
    all_transitions = []
    all_nulls = []
    all_landmarks = []
    all_sensitivity = []
    all_samples = []
    source_paths: dict[str, list[Path]] = {}

    for offset, (domain, loader) in enumerate(loaders):
        print(f"loading {domain}...", flush=True)
        blocks, quality, paths = loader()
        source_paths[domain] = paths
        print(f"  raw blocks={len(blocks):,}; running exact ordered controls", flush=True)
        summary, quadrants, transitions, nulls, landmark_and_sample, sensitivity = analyze_domain(domain, blocks, quality, offset)
        landmark_rows_only = [r for r in landmark_and_sample if "line_R_median" in r]
        sample_rows = [r for r in landmark_and_sample if "a_log_radial" in r]
        all_summary.extend(summary); all_quadrants.extend(quadrants); all_transitions.extend(transitions)
        all_nulls.extend(nulls); all_landmarks.extend(landmark_rows_only); all_samples.extend(sample_rows)
        all_sensitivity.extend(sensitivity); all_quality.extend(quality)
        del blocks

    summary_df = pd.DataFrame(all_summary)
    quality_df = pd.DataFrame(all_quality)
    quadrants_df = pd.DataFrame(all_quadrants)
    transitions_df = pd.DataFrame(all_transitions)
    nulls_df = pd.DataFrame(all_nulls)
    landmarks_df = pd.DataFrame(all_landmarks)
    sensitivity_df = pd.DataFrame(all_sensitivity)
    samples_df = pd.DataFrame(all_samples)

    hold = summary_df[summary_df.split == "holdout"]
    eligible = int(hold.eligible.sum())
    passing = int(hold.grammar_pass.sum())
    support = eligible >= 5 and passing / eligible >= 0.70
    if support:
        verdict = "SUPPORTED AS A TRANSFERABLE ORDERED GRAMMAR"
    elif passing >= 2:
        verdict = "PARTIAL / DOMAIN-SPECIFIC"
    else:
        verdict = "NOT SUPPORTED"
    line_strong = int(landmarks_df[(landmarks_df.split == "holdout") & landmarks_df.line_strong_pass].shape[0])
    circle_strong = int(landmarks_df[(landmarks_df.split == "holdout") & landmarks_df.circle_strong_pass].shape[0])
    result_first = (
        f"The frozen auxiliary common-gait rule passed in {passing}/{eligible} eligible holdout domains, so its registered verdict is **{verdict}**. "
        f"All {int(hold.coverage_pass.sum())}/{len(hold)} holdouts populated the four mixed regions. The intended intact-pair Di-ARA coupling claim was not tested by T342."
    )
    landmark_interpretation = (
        f"Exact `e` survived the strong line gate in {line_strong} domain(s), and exact reciprocal-Phi survived the strong circle gate in {circle_strong} domain(s). "
        "These counts are reported as the frozen secondary audit and do not alter the registered auxiliary verdict."
    )
    manifest = file_manifest(source_paths)
    OUT_MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    summary_df.to_csv(OUT_SUMMARY, index=False)
    quality_df.to_csv(OUT_QUALITY, index=False)
    quadrants_df.to_csv(OUT_QUADRANTS, index=False)
    transitions_df.to_csv(OUT_TRANSITIONS, index=False)
    nulls_df.to_csv(OUT_NULLS, index=False)
    landmarks_df.to_csv(OUT_LANDMARKS, index=False)
    sensitivity_df.to_csv(OUT_SENSITIVITY, index=False)
    samples_df.to_csv(OUT_SAMPLE, index=False)
    results = {
        "test_id": "T342-MULTIMEDIUM-IRRATIONALITY-TE-ARA-v1",
        "protocol_sha256": manifest["protocol_sha256"],
        "computational_addendum_sha256": manifest["computational_addendum_sha256"],
        "primary_verdict": verdict,
        "registered_auxiliary_verdict": verdict,
        "registered_auxiliary_scope": "One universal neighbour-by-neighbour quadrant gait, introduced during operationalisation.",
        "intended_ara_coupling_status": "NOT TESTED BY T342",
        "originator_scope_correction": "Di-ARA fixes two coupled perpendicular ARA axes and four mixed regions; path order, cadence, speed and proportion are identity-specific.",
        "four_region_holdout_coverage": int(hold.coverage_pass.sum()),
        "eligible_domains": eligible,
        "passing_domains": passing,
        "cross_domain_support": support,
        "result_first": result_first,
        "line_strong_domains": line_strong,
        "circle_strong_domains": circle_strong,
        "landmark_interpretation": landmark_interpretation,
        "domain_holdout": hold.replace({np.nan: None}).to_dict("records"),
        "fresh_numeric_domains": ["cold_room", "acoustics"],
        "previously_opened_domains": ["pendulum", "hydraulic", "bubbles", "qutrit", "river"],
        "interpretive_boundary": "The 1/6 NOT SUPPORTED verdict applies only to the registered auxiliary common-gait rule. Intended intact-pair Di-ARA coupling was not tested. Four-region occupancy is descriptive, and exact TE-ARA closure is definitional.",
    }
    OUT_RESULTS.write_text(json.dumps(clean_json(results), indent=2), encoding="utf-8")
    draw_figure(summary_df, quadrants_df, landmarks_df)
    write_html(summary_df, quadrants_df, transitions_df, samples_df)
    write_report(summary_df, landmarks_df, results)
    print(json.dumps(clean_json(results), indent=2), flush=True)


if __name__ == "__main__":
    main()

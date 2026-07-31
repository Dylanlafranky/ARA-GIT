"""Q46 ARA-first decomposition of the two local parents inside Q45's L strand."""

from __future__ import annotations

import concurrent.futures
import csv
import gzip
import hashlib
import json
import math
import os
import pathlib
import sys
from collections import defaultdict


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / "public_data" / "_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".mplconfig"))

import h5py
import matplotlib.pyplot as plt
import numpy as np

import q40_return_flow_relation_reversal_test as base
import q44_ara_mixing_prediction_test as q44


TEST_ID = "Q46-DOUBLE-PARENT-INTERNAL-ARA-v1"
PROTOCOL = HERE / "Q46_DOUBLE_PARENT_INTERNAL_ARA_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA256 = (
    "0f7b271c5c4df9614dc553b71e3d08004c1dfdf986835f6c8c2ba83928f7ee86"
)
Q45_LINEAGES = HERE / "Q45_15_CYCLE_PARENT_COMPLEMENT_LINEAGES.csv.gz"
Q45_RESULTS = HERE / "Q45_15_CYCLE_PARENT_COMPLEMENT_RESULTS.json"
RESULTS = HERE / "Q46_DOUBLE_PARENT_INTERNAL_ARA_RESULTS.json"
WINDOWS = HERE / "Q46_DOUBLE_PARENT_INTERNAL_ARA_WINDOWS.csv.gz"
FIGURE_PNG = HERE / "Q46_DOUBLE_PARENT_INTERNAL_ARA_DIAGNOSTICS.png"
FIGURE_SVG = HERE / "Q46_DOUBLE_PARENT_INTERNAL_ARA_DIAGNOSTICS.svg"

BOOTSTRAP_DRAWS = 20_000
BOOTSTRAP_SEED = 460028
EPS = 1e-12

BLUE = "#537DB8"
GOLD = "#D99B31"
ORANGE = "#D85C4A"
PINK = "#B65D83"
INK = "#17212B"
MID = "#647180"
GRID = "#D9E0E7"
BG = "#FAFBFC"


def digest(path: pathlib.Path, algorithm: str) -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def verify_inputs() -> None:
    actual = digest(PROTOCOL, "sha256")
    if actual != PROTOCOL_SHA256:
        raise RuntimeError(
            f"Frozen Q46 protocol changed: expected {PROTOCOL_SHA256}, got {actual}"
        )
    archive = digest(q44.ARCHIVE, "md5")
    if archive != q44.ARCHIVE_MD5:
        raise RuntimeError(
            f"Q44 archive changed: expected {q44.ARCHIVE_MD5}, got {archive}"
        )
    for path in (q44.SOURCE, q44.CONNECTED, Q45_LINEAGES, Q45_RESULTS):
        if not path.exists():
            raise RuntimeError(f"Required Q46 input missing: {path}")


def load_eligible() -> list[dict]:
    with gzip.open(Q45_LINEAGES, "rt", newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    output = []
    for row in rows:
        output.append(
            {
                "seed": int(row["seed"]),
                "pair": int(row["pair"]),
                "pair_name": row["pair_name"],
                "family": row["family"],
                "phase_slope": float(row["development_phase_slope"]),
                "phase_intercept": float(row["development_phase_intercept"]),
                "q45_path_share_l": float(row["path_share_l"]),
                "q45_path_share_c": float(row["path_share_c"]),
            }
        )
    return output


def local_parents(rhos: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    expectation = np.einsum("nij,kji->nk", rhos, base.OPS, optimize=True).real
    return expectation[:, :3], expectation[:, 3:6]


def parent_phase(row: dict, sample: float) -> float:
    multiplier = 0.5 if row["family"] == "two_turn_7_5" else 1.0
    return float(
        np.mod(
            multiplier * (row["phase_slope"] * sample + row["phase_intercept"]),
            2 * np.pi,
        )
    )


def window_metrics(
    row: dict,
    start: int,
    a: np.ndarray,
    b: np.ndarray,
    connected: np.ndarray,
) -> dict:
    local_start = start - 250
    aa = np.asarray(a[local_start : local_start + 16], dtype=np.float64)
    bb = np.asarray(b[local_start : local_start + 16], dtype=np.float64)
    cc = np.asarray(connected[start : start + 16], dtype=np.float64)

    da = np.diff(aa, axis=0)
    db = np.diff(bb, axis=0)
    pa = float(np.sum(np.linalg.norm(da, axis=1)))
    pb = float(np.sum(np.linalg.norm(db, axis=1)))
    native_total = pa + pb

    d1 = da[:, :, None] * bb[:-1, None, :]
    d2 = aa[:-1, :, None] * db[:, None, :]
    dx = da[:, :, None] * db[:, None, :]
    local = aa[:, :, None] * bb[:, None, :]
    dl = np.diff(local, axis=0)
    reconstruction = d1 + d2 + dx
    reconstruction_error = float(np.max(np.abs(dl - reconstruction)))

    p1_lift = float(np.sum(np.linalg.norm(d1.reshape(15, -1), axis=1)))
    p2_lift = float(np.sum(np.linalg.norm(d2.reshape(15, -1), axis=1)))
    px_lift = float(np.sum(np.linalg.norm(dx.reshape(15, -1), axis=1)))
    lift_total = p1_lift + p2_lift + px_lift

    dc = np.diff(cc, axis=0)
    path_l = float(np.sum(np.linalg.norm(dl.reshape(15, -1), axis=1)))
    path_c = float(np.sum(np.linalg.norm(dc.reshape(15, -1), axis=1)))
    parent_cut_total = path_l + path_c

    midpoint_phase = parent_phase(row, start + 7.5)
    quadrant = int(np.floor(midpoint_phase / (np.pi / 2))) % 4

    native_share_p1 = pa / native_total if native_total > EPS else float("nan")
    return {
        "seed": row["seed"],
        "pair": row["pair"],
        "pair_name": row["pair_name"],
        "family": row["family"],
        "start": start,
        "parent_phase_radians": midpoint_phase,
        "parent_phase_quadrant": quadrant,
        "native_path_p1": pa,
        "native_path_p2": pb,
        "native_share_p1": native_share_p1,
        "native_share_p2": 1.0 - native_share_p1,
        "native_ara_x1": 2.0 * native_share_p1,
        "native_ara_x2": 2.0 * (1.0 - native_share_p1),
        "native_ridge_distance": abs(2.0 * native_share_p1 - 1.0),
        "lifted_share_p1": p1_lift / lift_total if lift_total > EPS else float("nan"),
        "lifted_share_p2": p2_lift / lift_total if lift_total > EPS else float("nan"),
        "lifted_share_other": px_lift / lift_total if lift_total > EPS else float("nan"),
        "local_product_path": path_l,
        "connected_child_path": path_c,
        "double_parent_share_local": (
            path_l / parent_cut_total if parent_cut_total > EPS else float("nan")
        ),
        "double_parent_share_connected": (
            path_c / parent_cut_total if parent_cut_total > EPS else float("nan")
        ),
        "product_rule_max_error": reconstruction_error,
    }


def process_seed(seed: int, seed_rows: list[dict]) -> tuple[int, list[dict]]:
    connected = np.load(q44.CONNECTED, mmap_mode="r")
    output: list[dict] = []
    with h5py.File(q44.SOURCE, "r") as handle:
        group = handle[q44.locate_trial(handle, seed)]
        root = group["two_qubit_dms"]
        for row in seed_rows:
            name = base.PAIR_NAMES[row["pair"]]
            rhos = np.stack(
                [root[str(t)][name][()] for t in range(250, 500)]
            ).astype(np.complex128)
            a, b = local_parents(rhos)
            for start in range(250, 485, 15):
                output.append(
                    window_metrics(
                        row,
                        start,
                        a,
                        b,
                        connected[seed, :, row["pair"]],
                    )
                )
    return seed, output


def gather_windows(eligible: list[dict], workers: int = 8) -> list[dict]:
    by_seed: dict[int, list[dict]] = defaultdict(list)
    for row in eligible:
        by_seed[row["seed"]].append(row)

    output: list[dict] = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(process_seed, seed, by_seed[seed]) for seed in sorted(by_seed)
        ]
        for completed, future in enumerate(
            concurrent.futures.as_completed(futures), start=1
        ):
            _seed, seed_output = future.result()
            output.extend(seed_output)
            print(
                f"analysed Q46 local parents for {completed}/{len(by_seed)} seeds",
                flush=True,
            )
    output.sort(key=lambda row: (row["seed"], row["pair"], row["start"]))
    return output


def write_windows(rows: list[dict]) -> None:
    with gzip.open(WINDOWS, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def seed_values(rows: list[dict], field: str) -> dict[int, float]:
    values: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        value = float(row[field])
        if np.isfinite(value):
            values[int(row["seed"])].append(value)
    return {seed: float(np.mean(items)) for seed, items in values.items()}


def bootstrap(
    values: dict[int, float], statistic: str = "median", offset: int = 0
) -> dict:
    array = np.asarray(list(values.values()), dtype=np.float64)
    if array.size == 0:
        return {"estimate": float("nan"), "ci95": [float("nan"), float("nan")]}
    stat = np.median if statistic == "median" else np.mean
    rng = np.random.default_rng(BOOTSTRAP_SEED + offset)
    samples = rng.choice(
        array,
        size=(BOOTSTRAP_DRAWS, len(array)),
        replace=True,
    )
    draws = stat(samples, axis=1)
    return {
        "estimate": float(stat(array)),
        "ci95": [float(x) for x in np.quantile(draws, [0.025, 0.975])],
        "seed_count": int(len(array)),
    }


def summarize(rows: list[dict], eligible: list[dict]) -> dict:
    metrics = {
        "native_parent1_share": bootstrap(
            seed_values(rows, "native_share_p1"), offset=1
        ),
        "native_ridge_distance": bootstrap(
            seed_values(rows, "native_ridge_distance"), offset=2
        ),
        "lifted_parent1_share": bootstrap(
            seed_values(rows, "lifted_share_p1"), offset=3
        ),
        "lifted_parent2_share": bootstrap(
            seed_values(rows, "lifted_share_p2"), offset=4
        ),
        "lifted_other_share": bootstrap(
            seed_values(rows, "lifted_share_other"), offset=5
        ),
        "double_parent_local_share": bootstrap(
            seed_values(rows, "double_parent_share_local"), offset=6
        ),
        "double_parent_connected_share": bootstrap(
            seed_values(rows, "double_parent_share_connected"), offset=7
        ),
    }

    families = {}
    for family in ("two_turn_7_5", "one_turn_15"):
        selected = [row for row in rows if row["family"] == family]
        families[family] = {
            "windows": len(selected),
            "lineages": len(
                {(int(row["seed"]), int(row["pair"])) for row in selected}
            ),
            "seeds": len({int(row["seed"]) for row in selected}),
            "native_parent1_share": bootstrap(
                seed_values(selected, "native_share_p1"), offset=10
            ),
            "native_ridge_distance": bootstrap(
                seed_values(selected, "native_ridge_distance"), offset=11
            ),
            "lifted_other_share": bootstrap(
                seed_values(selected, "lifted_share_other"), offset=12
            ),
            "connected_child_share": bootstrap(
                seed_values(selected, "double_parent_share_connected"), offset=13
            ),
        }

    quadrants = {}
    for quadrant in range(4):
        selected = [
            row for row in rows if int(row["parent_phase_quadrant"]) == quadrant
        ]
        quadrants[str(quadrant)] = {
            "windows": len(selected),
            "native_parent1_share": bootstrap(
                seed_values(selected, "native_share_p1"), offset=20 + quadrant
            ),
            "native_ridge_distance": bootstrap(
                seed_values(selected, "native_ridge_distance"), offset=24 + quadrant
            ),
            "lifted_other_share": bootstrap(
                seed_values(selected, "lifted_share_other"), offset=28 + quadrant
            ),
        }

    q45_seed_c: dict[int, list[float]] = defaultdict(list)
    for row in eligible:
        q45_seed_c[row["seed"]].append(row["q45_path_share_c"])
    q45_connected = bootstrap(
        {seed: float(np.mean(values)) for seed, values in q45_seed_c.items()},
        offset=40,
    )

    ridge = metrics["native_parent1_share"]
    gates = {
        "same_tier_parent_ridge": bool(
            0.4 <= ridge["estimate"] <= 0.6
            and ridge["ci95"][0] <= 0.5 <= ridge["ci95"][1]
        ),
        "product_rule_reconstruction": bool(
            max(float(row["product_rule_max_error"]) for row in rows) <= 1e-6
        ),
        "swap_invariant_orientation_free_summary": True,
    }
    return {
        "metrics": metrics,
        "families": families,
        "parent_phase_quadrants": quadrants,
        "q45_recomputed_connected_child_share": q45_connected,
        "predicted_connected_child_share": 0.42,
        "prediction_absolute_error": abs(q45_connected["estimate"] - 0.42),
        "maximum_product_rule_error": max(
            float(row["product_rule_max_error"]) for row in rows
        ),
        "gates": gates,
    }


def make_figure(summary: dict) -> None:
    metrics = summary["metrics"]
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    fig.patch.set_facecolor(BG)

    ax = axes[0, 0]
    share = metrics["native_parent1_share"]["estimate"]
    ci = metrics["native_parent1_share"]["ci95"]
    ax.errorbar(
        [2 * share, 2 * (1 - share)],
        [1, 1],
        xerr=[
            [2 * (share - ci[0]), 2 * (share - ci[0])],
            [2 * (ci[1] - share), 2 * (ci[1] - share)],
        ],
        fmt="o",
        color=BLUE,
        ecolor=MID,
        capsize=5,
        markersize=9,
    )
    ax.axvline(1, color=INK, linewidth=1.5)
    ax.set_xlim(0, 2)
    ax.set_ylim(0.85, 1.15)
    ax.set_yticks([])
    ax.set_xlabel("ARA diameter coordinate (0–2)")
    ax.set_title("Two complete local parents on their shared ARA cut")
    ax.text(2 * share, 1.045, "P1", ha="center", color=BLUE, fontweight="bold")
    ax.text(
        2 * (1 - share), 0.94, "P2", ha="center", color=BLUE, fontweight="bold"
    )

    ax = axes[0, 1]
    local = metrics["double_parent_local_share"]["estimate"]
    connected = summary["q45_recomputed_connected_child_share"]["estimate"]
    bars = ax.bar(
        ["local-parent strand L", "connected child C"],
        [local, connected],
        color=[GOLD, BLUE],
    )
    ax.axhline(0.5, color=INK, linewidth=1.2, linestyle="--")
    ax.axhline(0.42, color=ORANGE, linewidth=1.2, linestyle=":")
    ax.set_ylim(0, 1)
    ax.set_ylabel("share of measured 15-sample movement")
    ax.set_title("Measured double-parent cut")
    for bar, value in zip(bars, (local, connected)):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.025,
            f"{100 * value:.1f}%",
            ha="center",
            fontweight="bold",
        )

    ax = axes[1, 0]
    labels = ["P1 lifted", "P2 lifted", "handover Other"]
    values = [
        metrics["lifted_parent1_share"]["estimate"],
        metrics["lifted_parent2_share"]["estimate"],
        metrics["lifted_other_share"]["estimate"],
    ]
    bars = ax.bar(labels, values, color=[BLUE, PINK, GOLD])
    ax.set_ylim(0, max(values) * 1.3)
    ax.set_ylabel("unsigned share inside L")
    ax.set_title("Decompressed local-product strand")
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + max(values) * 0.04,
            f"{100 * value:.2f}%",
            ha="center",
            fontweight="bold",
        )

    ax = axes[1, 1]
    quadrants = summary["parent_phase_quadrants"]
    x = np.arange(4)
    p1 = [quadrants[str(index)]["native_parent1_share"]["estimate"] for index in x]
    other = [quadrants[str(index)]["lifted_other_share"]["estimate"] for index in x]
    ax.plot(x, p1, marker="o", color=BLUE, linewidth=2, label="P1 share")
    ax.plot(
        x, other, marker="o", color=GOLD, linewidth=2, label="handover Other"
    )
    ax.axhline(0.5, color=INK, linewidth=1.2, linestyle="--")
    ax.set_xticks(x, ["Ab", "aB", "bA", "Ba"])
    ax.set_ylim(0, max(0.65, max(p1) * 1.15))
    ax.set_ylabel("seed-balanced share")
    ax.set_xlabel("frozen 15-cycle parent-phase quadrant")
    ax.set_title("Parent balance across the four parent quadrants")
    ax.legend(frameon=False)

    for axis in axes.flat:
        axis.set_facecolor(BG)
        axis.grid(axis="y", color=GRID, linewidth=0.8, alpha=0.8)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)

    fig.suptitle(
        "Q46 — ARA of the two complete local parents",
        fontsize=18,
        fontweight="bold",
        color=INK,
    )
    fig.savefig(FIGURE_PNG, dpi=180, bbox_inches="tight")
    fig.savefig(FIGURE_SVG, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    verify_inputs()
    eligible = load_eligible()
    rows = gather_windows(eligible)
    if not rows:
        raise RuntimeError("Q46 produced no eligible windows")
    write_windows(rows)
    summary = summarize(rows, eligible)

    result = {
        "test_id": TEST_ID,
        "date": "2026-07-28",
        "status": (
            "COARSE PARENT RIDGE SUPPORTED FOR THIS MEASURED CUT"
            if all(summary["gates"].values())
            else "NOT SUPPORTED"
        ),
        "scope": {
            "archive": q44.ARCHIVE.name,
            "archive_md5": q44.ARCHIVE_MD5,
            "protocol": PROTOCOL.name,
            "protocol_sha256": PROTOCOL_SHA256,
            "lineages": len(eligible),
            "seeds": len({row["seed"] for row in eligible}),
            "windows": len(rows),
        },
        **summary,
        "interpretation": {
            "ara": (
                "P1 and P2 are tested as complete same-tier parents before their "
                "local-product strand is compressed into the measured double-parent cut."
            ),
            "established_physics": (
                "a and b are local Bloch vectors; L=ab^T is their product relation; "
                "C is the connected two-body relation."
            ),
            "boundary": (
                "The approximately 42% value is a Q45 accounting complement, not "
                "independent evidence. The new evidence is the P1:P2 ridge and "
                "within-L handover decomposition."
            ),
        },
        "artifacts": {
            "windows": WINDOWS.name,
            "figure_png": FIGURE_PNG.name,
            "figure_svg": FIGURE_SVG.name,
        },
    }
    RESULTS.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    make_figure(result)
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()

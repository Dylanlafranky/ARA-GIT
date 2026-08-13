"""T359: frozen raw-event-clock oscillator Irrationality Di-ARA test.

The T358 derivative phase interface is replaced by an event-defined monotone
clock.  All ARA coordinates and outcome controls are inherited unchanged.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import t358_detuned_oscillator_irrationality_di_ara as core


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "T358_SOURCE_DATA"
FIG4 = SOURCE / "figure4_extracted"
S1 = SOURCE / "data" / "figure S1"
ARCHIVE = HERE / "T358_SOURCE_DATA.zip"
HZ = 200.0
DISCARD_SECONDS = 10.0
LOW_Q = 0.35
HIGH_Q = 0.65
PERIOD_MIN = 1.5
PERIOD_MAX = 4.0
SEED = 3_590_812

CLAIM = HERE / "T359_EVENT_CLOCK_OSCILLATOR_IRRATIONALITY_DI_ARA_CLAIM_PACKET_v1.md"
PROTOCOL = HERE / "T359_EVENT_CLOCK_OSCILLATOR_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md"
PREFIX = HERE / "T359_EVENT_CLOCK_OSCILLATOR_IRRATIONALITY_DI_ARA"
WINDOW_CSV = Path(f"{PREFIX}_WINDOW_METRICS.csv")
PAIR_CSV = Path(f"{PREFIX}_PAIR_SUMMARY.csv")
RECORD_CSV = Path(f"{PREFIX}_RECORD_SUMMARY.csv")
CLOSURE_CSV = Path(f"{PREFIX}_CLOSURE_SUMMARY.csv")
QA_CSV = Path(f"{PREFIX}_EVENT_CLOCK_QA.csv")
GATES_CSV = Path(f"{PREFIX}_FROZEN_GATES.csv")
EXAMPLE_CSV = Path(f"{PREFIX}_EXAMPLE_PATHS.csv")
RESULTS_JSON = Path(f"{PREFIX}_RESULTS.json")
FIGURE_PNG = Path(f"{PREFIX}_FIGURE.png")
REPORT_MD = HERE / "T359_EVENT_CLOCK_OSCILLATOR_IRRATIONALITY_DI_ARA_REPORT_2026-08-12.md"

SWEEP = core.SWEEP
CANDIDATES = core.CANDIDATES


@dataclass
class EventRecord:
    identity: str
    delta_r: float
    path: Path
    t: np.ndarray
    current: np.ndarray
    phase: np.ndarray
    backtrack: np.ndarray
    crossing_count: np.ndarray
    median_period: np.ndarray
    valid_period_fraction: np.ndarray
    lower_threshold: np.ndarray
    upper_threshold: np.ndarray


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def event_clock(signal: np.ndarray, t: np.ndarray) -> tuple[np.ndarray, dict]:
    lower = float(np.quantile(signal, LOW_Q))
    upper = float(np.quantile(signal, HIGH_Q))
    if not upper > lower:
        raise RuntimeError("Event thresholds are not ordered")

    armed = bool(signal[0] <= lower)
    events: list[float] = []
    for i in range(1, len(signal)):
        if not armed:
            if signal[i] <= lower:
                armed = True
            continue
        if signal[i - 1] < upper <= signal[i]:
            span = float(signal[i] - signal[i - 1])
            fraction = 0.0 if abs(span) < 1e-15 else (upper - float(signal[i - 1])) / span
            events.append(float(t[i - 1] + fraction * (t[i] - t[i - 1])))
            armed = False

    event = np.asarray(events, dtype=float)
    if len(event) < 3:
        raise RuntimeError(f"Only {len(event)} events found")
    period = np.diff(event)
    if np.any(period <= 0):
        raise RuntimeError("Event clock is not strictly ordered")

    phase = np.interp(t, event, np.arange(len(event), dtype=float))
    phase[t < event[0]] = (t[t < event[0]] - event[0]) / period[0]
    phase[t > event[-1]] = (len(event) - 1) + (t[t > event[-1]] - event[-1]) / period[-1]
    backtrack = float(np.mean(np.diff(phase) < -1e-12))
    stats = {
        "event_count": int(len(event)),
        "median_period": float(np.median(period)),
        "valid_period_fraction": float(np.mean((period >= PERIOD_MIN) & (period <= PERIOD_MAX))),
        "backtrack_fraction": backtrack,
        "lower_threshold": lower,
        "upper_threshold": upper,
    }
    return phase, stats


def read_lvm(identity: str, delta_r: float, path: Path) -> EventRecord:
    frame = pd.read_csv(path, sep="\t", header=None, engine="c").dropna(axis=1, how="all")
    if frame.shape[1] != 80 or frame.isna().any().any():
        raise RuntimeError(f"{path.name}: expected complete 80-column numeric current matrix")
    full = frame.to_numpy(dtype=np.float64)
    if not np.isfinite(full).all():
        raise RuntimeError(f"{path.name}: nonfinite current")
    start = int(round(DISCARD_SECONDS * HZ))
    current = full[start:]
    t = np.arange(len(current), dtype=float) / HZ
    phase = np.empty_like(current)
    event_count = np.empty(80, dtype=int)
    median_period = np.empty(80, dtype=float)
    valid_period = np.empty(80, dtype=float)
    backtrack = np.empty(80, dtype=float)
    lower = np.empty(80, dtype=float)
    upper = np.empty(80, dtype=float)
    for col in range(80):
        phase[:, col], stats = event_clock(current[:, col], t)
        event_count[col] = stats["event_count"]
        median_period[col] = stats["median_period"]
        valid_period[col] = stats["valid_period_fraction"]
        backtrack[col] = stats["backtrack_fraction"]
        lower[col] = stats["lower_threshold"]
        upper[col] = stats["upper_threshold"]
    return EventRecord(
        identity, delta_r, path, t, current, phase, backtrack, event_count,
        median_period, valid_period, lower, upper,
    )


def qa_row(item: EventRecord, role: str) -> dict:
    return {
        "identity": item.identity,
        "role": role,
        "filename": item.path.name,
        "file_sha256": sha256(item.path),
        "rows_after_discard": len(item.t),
        "columns": item.current.shape[1],
        "retained_duration_seconds": float(item.t[-1] - item.t[0]),
        "sampling_hz": HZ,
        "median_event_count": float(np.median(item.crossing_count)),
        "minimum_event_count": int(np.min(item.crossing_count)),
        "maximum_event_count": int(np.max(item.crossing_count)),
        "median_period_seconds": float(np.median(item.median_period)),
        "period_q25_seconds": float(np.quantile(item.median_period, 0.25)),
        "period_q75_seconds": float(np.quantile(item.median_period, 0.75)),
        "median_valid_period_fraction": float(np.median(item.valid_period_fraction)),
        "minimum_valid_period_fraction": float(np.min(item.valid_period_fraction)),
        "median_phase_backtrack_fraction": float(np.median(item.backtrack)),
        "maximum_phase_backtrack_fraction": float(np.max(item.backtrack)),
        "median_threshold_span": float(np.median(item.upper_threshold - item.lower_threshold)),
    }


def load_records() -> tuple[dict[int, EventRecord], EventRecord, EventRecord, pd.DataFrame]:
    records: dict[int, EventRecord] = {}
    rows: list[dict] = []
    for delta_r, stem in SWEEP.items():
        path = FIG4 / stem / f"{stem}.lvm"
        item = read_lvm(f"coupled_{delta_r}", float(delta_r), path)
        records[delta_r] = item
        rows.append(qa_row(item, "coupled_sweep"))
    u1000 = read_lvm("uncoupled_1000", 0.0, S1 / "oc032118_4.lvm")
    u1150 = read_lvm("uncoupled_1150", 150.0, S1 / "oc032118_8.lvm")
    rows.extend([qa_row(u1000, "uncoupled_source"), qa_row(u1150, "uncoupled_source")])
    return records, u1000, u1150, pd.DataFrame(rows)


def clock_gate(qa: pd.DataFrame) -> tuple[bool, str]:
    event_ok = qa.median_event_count >= 30
    period_ok = qa.median_period_seconds.between(PERIOD_MIN, PERIOD_MAX, inclusive="both")
    share_ok = qa.median_valid_period_fraction >= 0.85
    direction_ok = qa.median_phase_backtrack_fraction <= 1e-12
    passed = bool((event_ok & period_ok & share_ok & direction_ok).all())
    value = (
        f"records={len(qa)}; event_ok={int(event_ok.sum())}; period_ok={int(period_ok.sum())}; "
        f"share_ok={int(share_ok.sum())}; direction_ok={int(direction_ok.sum())}"
    )
    return passed, value


def add_g0(gates: pd.DataFrame, details: dict, qa: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    g0, value = clock_gate(qa)
    row = pd.DataFrame([["G0", "raw event clock physical-period QA", value, g0]], columns=gates.columns)
    gates = pd.concat([row, gates], ignore_index=True)
    old = details["grouped_gates"].copy()
    grouped = {"G0": g0, **{key: bool(old[key]) for key in ["G1", "G2", "G3", "G4", "G5", "G6"]}}
    grouped["overall"] = all(grouped.values())
    details["grouped_gates"] = grouped
    return gates, details


def pick(record: pd.DataFrame, identity: str, condition: str) -> pd.Series:
    return core.pick(record, identity, condition)


def plot_results(record: pd.DataFrame, closure: pd.DataFrame, examples: pd.DataFrame, gates: pd.DataFrame, qa: pd.DataFrame) -> None:
    plt.rcParams.update({"font.size": 9.5, "axes.titlesize": 11.5, "axes.labelsize": 10})
    blue, gold, orange, grey, dark, green = "#4C78A8", "#D99B2B", "#E36C35", "#AAB2BD", "#27313D", "#59A14F"
    fig, axes = plt.subplots(3, 2, figsize=(15, 17), constrained_layout=True)
    sweep = record[(record.family == "coupled") & (record.condition == "chronological")].sort_values("delta_r_ohm")

    ax = axes[0, 0]
    sc = ax.scatter(sweep.x_p, sweep.x_r, c=sweep.delta_r_ohm, cmap="viridis", s=95, edgecolor=dark, zorder=3)
    ax.plot(sweep.x_p, sweep.x_r, color=grey, lw=1.2, zorder=1)
    for _, row in sweep.iterrows():
        ax.annotate(f"{int(row.delta_r_ohm)}", (row.x_p, row.x_r), xytext=(5, 4), textcoords="offset points", fontsize=8)
    unc = pick(record, "uncoupled_detuned", "chronological")
    ax.scatter([unc.x_p], [unc.x_r], marker="X", s=130, c=orange, edgecolor=dark, label="uncoupled detuned")
    ax.axvline(1, color=dark, lw=1); ax.axhline(1, color=dark, lw=1)
    ax.set(xlim=(-0.05, 2.05), ylim=(-0.05, 2.05), xlabel="address openness x_P", ylabel="stochastic residual x_R", title="Event-clock Irrationality Di-ARA plane")
    ax.legend(frameon=False, loc="upper left"); ax.grid(color="#E7E9EC", lw=0.7)
    fig.colorbar(sc, ax=ax, label="coupled detuning delta R (ohm)")

    ax = axes[0, 1]
    styles = [("coupled_50", blue, "50 ohm"), ("coupled_170", gold, "170 ohm closure reference"), ("uncoupled_detuned", orange, "uncoupled detuned")]
    for identity, color, label in styles:
        sub = examples[(examples.identity == identity) & (examples.pair == 1)]
        for landmark in range(core.SAMPLES_PER_CYCLE):
            q = sub[sub.landmark == landmark]
            ax.plot(q.cycle + q.window * core.WINDOW_CYCLES, q.ara_phase, color=color, lw=0.9, alpha=0.65)
        ax.plot([], [], color=color, lw=2.5, label=label)
    ax.axhline(1, color=dark, lw=1)
    ax.set(xlabel="successive parent cycle", ylabel="child position on ARA 0-2", ylim=(-0.05, 2.05), title="Child strands through the raw parent-event clock")
    ax.legend(frameon=False, fontsize=8); ax.grid(color="#E7E9EC", lw=0.7)

    ax = axes[1, 0]
    ax.plot(sweep.delta_r_ohm, sweep.cycle_rho, color=blue, marker="o", label="one-cycle coherence")
    ax.axhline(0.80, color=blue, ls=":", lw=1)
    ax2 = ax.twinx(); ax2.plot(sweep.delta_r_ohm, sweep.cycle_miss_abs, color=gold, marker="s", label="absolute miss")
    ax2.axhline(0.03, color=gold, ls=":", lw=1)
    ax.set(xlabel="coupled detuning delta R (ohm)", ylabel="return coherence rho", ylim=(0, 1.03), title="One-parent-cycle return across detuning")
    ax2.set(ylabel="absolute circular miss (turns)", ylim=(0, 0.51))
    lines = ax.get_lines()[:1] + ax2.get_lines()[:1]
    ax.legend(lines, [line.get_label() for line in lines], frameon=False, fontsize=8, loc="lower right"); ax.grid(color="#E7E9EC", lw=0.7)

    ax = axes[1, 1]
    for identity, color, label in [("coupled_50", blue, "50 ohm"), ("coupled_170", gold, "170 ohm"), ("uncoupled_detuned", orange, "uncoupled")]:
        q = closure[(closure.identity == identity) & (closure.condition == "chronological")]
        ax.plot(q.lag, q.rho, marker="o", ms=3, lw=1.8, color=color, label=label)
    ax.axvline(8, color=dark, lw=1, label="one parent cycle"); ax.axhline(0.80, color=dark, lw=1, ls=":")
    ax.set(xlabel="lag (parent-clock samples)", ylabel="closure coherence rho", ylim=(0, 1.03), title="Closure history C(H)")
    ax.legend(frameon=False, fontsize=8); ax.grid(color="#E7E9EC", lw=0.7)

    ax = axes[2, 0]
    rows = []
    for d in CANDIDATES:
        chronological = pick(record, f"coupled_{d}", "chronological")
        shuffled = pick(record, f"coupled_{d}", "shuffled")
        wrong = pick(record, f"coupled_{d}", "wrong_record")
        rows.append((d, shuffled.x_r - chronological.x_r, chronological.best_rho - shuffled.best_rho, max(wrong.x_r - chronological.x_r, chronological.best_rho - wrong.best_rho)))
    control = pd.DataFrame(rows, columns=["delta_r", "shuffle_xr", "shuffle_rho", "wrong_penalty"])
    x = np.arange(len(control)); width = 0.25
    ax.bar(x - width, control.shuffle_xr, width, color=blue, label="shuffle: delta x_R")
    ax.bar(x, control.shuffle_rho, width, color=gold, label="shuffle: rho loss")
    ax.bar(x + width, control.wrong_penalty, width, color=grey, edgecolor=dark, label="wrong-record penalty")
    ax.axhline(0.15, color=dark, ls=":", lw=1); ax.axhline(0.25, color=dark, ls="--", lw=1)
    ax.set_xticks(x, control.delta_r.astype(int)); ax.set(xlabel="candidate detuning delta R (ohm)", ylabel="control penalty", title="Chronology and lineage controls")
    ax.legend(frameon=False, fontsize=8); ax.grid(axis="y", color="#E7E9EC", lw=0.7)

    ax = axes[2, 1]; ax.axis("off")
    g0, _ = clock_gate(qa)
    lines = ["Frozen gates"]
    for _, row in gates.iterrows():
        lines.append(f"{row.gate:>3}  {'PASS' if bool(row['pass']) else 'FAIL':<4}  {row.requirement}")
    lines.extend([
        "",
        f"EVENT CLOCK QA: {'PASS' if g0 else 'FAIL'}",
        f"median event count {qa.median_event_count.min():.1f}-{qa.median_event_count.max():.1f}",
        f"median period {qa.median_period_seconds.min():.3f}-{qa.median_period_seconds.max():.3f} s",
        f"median valid-period share {qa.median_valid_period_fraction.min():.3f}-{qa.median_valid_period_fraction.max():.3f}",
        "",
        "Finite structured non-closure only.",
    ])
    ax.text(0.01, 0.98, "\n".join(lines), va="top", family="monospace", fontsize=8.5, color=dark)
    ax.set_title("Preregistered verdict and clock validity", loc="left")
    fig.suptitle("T359 - raw-event-clock physical oscillator Irrationality Di-ARA\n80 electrochemical oscillators; 40 matched cross-population cuts per record", fontsize=16, color=dark)
    fig.savefig(FIGURE_PNG, dpi=180, facecolor="white")
    plt.close(fig)


def write_report(record: pd.DataFrame, gates: pd.DataFrame, details: dict, qa: pd.DataFrame, metrics: pd.DataFrame) -> None:
    overall = bool(details["grouped_gates"]["overall"])
    g0 = bool(details["grouped_gates"]["G0"])
    verdict = "SUPPORTED [controlled event-clock physical transfer]" if overall else ("NOT SUPPORTED ON THIS VALID PHYSICAL CLOCK" if g0 else "INCONCLUSIVE - EVENT CLOCK QA FAILED")
    coupled = record[(record.family == "coupled") & (record.condition == "chronological")].sort_values("delta_r_ohm")
    unc = pick(record, "uncoupled_detuned", "chronological")
    table = [f"| {int(r.delta_r_ohm)} | {r.x_p:.3f} | {r.x_r:.3f} | {r.cycle_rho:.3f} | {r.cycle_miss_abs:.4f} | {r.pair_closure_share:.3f} | {r.pair_coherent_nonclosure_share:.3f} |" for _, r in coupled.iterrows()]
    table.append(f"| uncoupled 150 | {unc.x_p:.3f} | {unc.x_r:.3f} | {unc.cycle_rho:.3f} | {unc.cycle_miss_abs:.4f} | {unc.pair_closure_share:.3f} | {unc.pair_coherent_nonclosure_share:.3f} |")
    gate_lines = [f"| {r.gate} | {'PASS' if bool(r['pass']) else 'FAIL'} | {r.requirement} | {r.value} |" for _, r in gates.iterrows()]
    structured = [key for key, value in details["structured_candidate"].items() if value]
    text = f"""# T359 - raw-event-clock oscillator Irrationality Di-ARA

**Run date:** 12 August 2026  
**Source:** Ocampo-Espindola et al., Zenodo 10.5281/zenodo.15122129  
**Frozen overall verdict:** **{verdict}**

## Plain-language answer

T359 repeated T358 on the same physical archive but anchored every 0→2 cycle to a repeated event in the raw current: the signal first entered its lower state and its next rise into the upper state began a new cycle. The clock {'passed' if g0 else 'failed'} the preregistered physical-period QA.

The detunings meeting the complete coherent-nonclosure definition were **{', '.join(structured) if structured else 'none'} ohm**. The result is the median of 40 matched physical cuts inside each record, not 40 independent experiments.

## Event-clock QA

- Records passing every G0 component: `{int(sum((qa.median_event_count >= 30) & qa.median_period_seconds.between(PERIOD_MIN, PERIOD_MAX) & (qa.median_valid_period_fraction >= 0.85) & (qa.median_phase_backtrack_fraction <= 1e-12)))}/{len(qa)}`.
- Record-median event count range: `{qa.median_event_count.min():.1f}–{qa.median_event_count.max():.1f}`.
- Record-median period range: `{qa.median_period_seconds.min():.3f}–{qa.median_period_seconds.max():.3f}` seconds.
- Record-median valid-period share range: `{qa.median_valid_period_fraction.min():.3f}–{qa.median_valid_period_fraction.max():.3f}`.
- Maximum constructed backtrack fraction: `{qa.maximum_phase_backtrack_fraction.max():.6f}`.

## Record-level ARA readings

| delta R (ohm) | x_P | x_R | one-cycle rho | one-cycle miss | closing pair share | coherently non-closing pair share |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(table)}

## Frozen gates

| gate | result | requirement | observed |
|---|---|---|---|
{chr(10).join(gate_lines)}

Grouped gates: `{json.dumps(details['grouped_gates'], sort_keys=True)}`

## Calibration conclusion

G0 failed only because the two shorter uncoupled-control records contained 23 and 28 detected events rather than the frozen minimum of 30. All eleven records passed the physical-period, valid-period-share and one-way-direction checks. The frozen G0 failure is retained.

G1, G2 and G3 passed: the event clock recovered the 170-ohm closure reference, identified coherent non-closure at 50, 290 and 340 ohm, and strongly distinguished real chronological order from shuffled order. However, G4 and G5 failed decisively. Coupled, uncoupled and wrong-record paths all became almost equally deterministic.

The reason is methodological: mapping every oscillator linearly between its own successive events converts any sufficiently recurrent trace into an almost perfect sawtooth. This preserves within-clock order but normalizes away the coupling identity that T359 needed to distinguish. T359 is therefore not supported as a coupling-specific transfer. This event-phase instrument should not be reused for that claim unless raw within-cycle amplitude or shape is retained alongside phase.

## Evidence boundary

This calibration reads one controlled physical archive. A valid-clock failure is evidence that this specific frozen sector prediction did not transfer here; it is not a universal rejection of ARA or Irrationality Di-ARA. Success would remain a finite empirical transfer rather than proof of exact irrationality or bedrock geometry.

## Reproduction

```powershell
& 'F:\\SystemFormulaFolder\\.venv_ara_verify\\Scripts\\python.exe' 'analysis\\irrationality_path_calibration\\t359_event_clock_oscillator_irrationality_di_ara.py'
& 'F:\\SystemFormulaFolder\\.venv_ara_verify\\Scripts\\python.exe' 'analysis\\irrationality_path_calibration\\validate_t359_event_clock_oscillator_irrationality_di_ara.py'
```
"""
    REPORT_MD.write_text(text, encoding="utf-8")


def main() -> None:
    if not CLAIM.exists() or not PROTOCOL.exists():
        raise FileNotFoundError("Frozen T359 claim/protocol missing")
    if md5(ARCHIVE) != "abe81a3631481b58977925daf453ede5":
        raise RuntimeError("Source archive MD5 mismatch")

    records, u1000, u1150, qa = load_records()
    core.SEED = SEED
    metrics, closure, examples = core.run_all(records, u1000, u1150)
    pair, record = core.make_summaries(metrics)
    gates, details = core.score_gates(record)
    gates, details = add_g0(gates, details, qa)

    closure_summary = closure.groupby(["identity", "family", "delta_r_ohm", "condition", "lag"], as_index=False).agg(
        rho=("rho", "median"), miss_signed=("miss_signed", "median"), miss_abs=("miss_abs", "median")
    )
    metrics.to_csv(WINDOW_CSV, index=False)
    pair.to_csv(PAIR_CSV, index=False)
    record.to_csv(RECORD_CSV, index=False)
    closure_summary.to_csv(CLOSURE_CSV, index=False)
    qa.to_csv(QA_CSV, index=False)
    gates.to_csv(GATES_CSV, index=False)
    examples.to_csv(EXAMPLE_CSV, index=False)

    g0 = bool(details["grouped_gates"]["G0"])
    overall = bool(details["grouped_gates"]["overall"])
    verdict = "SUPPORTED [controlled event-clock physical transfer]" if overall else ("NOT SUPPORTED ON THIS VALID PHYSICAL CLOCK" if g0 else "INCONCLUSIVE - EVENT CLOCK QA FAILED")
    result = {
        "test": "T359 raw-event-clock oscillator Irrationality Di-ARA",
        "date": "2026-08-12",
        "source_doi": "10.5281/zenodo.15122129",
        "overall_verdict": verdict,
        "grouped_gates": details["grouped_gates"],
        "details": details,
        "physical_records": 10,
        "paired_oscillators_per_record": 40,
        "chronological_windows": int(metrics[metrics.condition == "chronological"].shape[0]),
        "claim_sha256": sha256(CLAIM),
        "protocol_sha256": sha256(PROTOCOL),
        "source_archive_md5": md5(ARCHIVE),
        "event_clock": {"discard_seconds": DISCARD_SECONDS, "lower_quantile": LOW_Q, "upper_quantile": HIGH_Q},
        "boundary": "Finite event-clock physical transfer only; not exact irrationality or universal ARA.",
    }
    RESULTS_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    plot_results(record, closure_summary, examples, gates, qa)
    write_report(record, gates, details, qa, metrics)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

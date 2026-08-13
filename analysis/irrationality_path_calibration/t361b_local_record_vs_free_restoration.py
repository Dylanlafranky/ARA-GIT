"""Post-result T361B: distinguish local record from recursive restoration."""

from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import t361_irrationality_di_ara_wave_recording as core


HERE = Path(__file__).resolve().parent
PREFIX = HERE / "T361B_LOCAL_RECORD_VS_FREE_RESTORATION"
ROWS = Path(f"{PREFIX}_PAIR_ROWS.csv")
SUMMARY = Path(f"{PREFIX}_RECORD_SUMMARY.csv")
RESULTS = Path(f"{PREFIX}_RESULTS.json")
FIGURE = Path(f"{PREFIX}_FIGURE.png")
PROTOCOL = HERE / "T361B_LOCAL_RECORD_VS_FREE_RESTORATION_PROTOCOL_v1_FROZEN.md"


def batch_step(model: core.Recorder, features: np.ndarray, states: np.ndarray, blind: bool) -> np.ndarray:
    out = np.empty(len(features), dtype=float)
    if blind:
        k = min(core.K_LOOKUP, len(model.features))
        _, index = model.all_tree.query(features, k=k)
        out[:] = np.median(model.target[np.atleast_2d(index)], axis=1)
        return out
    for q in ("++", "+-", "--", "-+"):
        loc = np.flatnonzero(states == q)
        if not len(loc):
            continue
        if q in model.state_trees:
            tree, source_index = model.state_trees[q]
            k = min(core.K_LOOKUP, len(source_index))
            _, local_index = tree.query(features[loc], k=k)
            index = source_index[np.atleast_2d(local_index)]
        else:
            k = min(core.K_LOOKUP, len(model.features))
            _, index = model.all_tree.query(features[loc], k=k)
            index = np.atleast_2d(index)
        out[loc] = np.median(model.target[index], axis=1)
    return out


def pair_diagnostic(delta_r: int, pair: int, prepared: list[tuple]) -> list[dict]:
    all_a, all_b, n_train, model, _ = prepared[pair]
    wrong = prepared[(pair + 1) % 40][3]
    accum = {m: {"true": [], "pred": [], "next_true": [], "next_pred": []}
             for m in ("primary", "direction_blind", "wrong_lineage")}
    for xa, xb in zip(all_a[n_train:], all_b[n_train:]):
        da, db = np.diff(xa), np.diff(xb)
        dir_a, dir_b = core.directions(da), core.directions(db)
        t = np.arange(1, core.M - 1)
        states = np.asarray([core.quadrant(int(dir_a[j]), int(dir_b[j - 1])) for j in t])
        feat_primary = np.column_stack([xa[t] / 2.0, xb[t] / 2.0, da[t] / model.scale_da])
        feat_wrong = np.column_stack([xa[t] / 2.0, xb[t] / 2.0, da[t] / wrong.scale_da])
        predicted = {
            "primary": batch_step(model, feat_primary, states, False),
            "direction_blind": batch_step(model, feat_primary, states, True),
            "wrong_lineage": batch_step(wrong, feat_wrong, states, False),
        }
        for method, pred in predicted.items():
            accum[method]["true"].append(db[t])
            accum[method]["pred"].append(pred)
            accum[method]["next_true"].append(xb[t + 1])
            accum[method]["next_pred"].append(np.clip(xb[t] + pred, 0, 2))
    rows = []
    for method, values in accum.items():
        true = np.concatenate(values["true"]); pred = np.concatenate(values["pred"])
        next_true = np.concatenate(values["next_true"]); next_pred = np.concatenate(values["next_pred"])
        mask = np.abs(true) >= core.FLAT
        direction = float(np.mean(np.sign(true[mask]) == np.sign(pred[mask]))) if np.any(mask) else 1.0
        rows.append({
            "delta_r": delta_r, "pair": pair + 1, "method": method,
            "transitions": len(true),
            "delta_RMSE_ARA": float(np.sqrt(np.mean((pred - true) ** 2))),
            "next_position_RMSE_ARA": float(np.sqrt(np.mean((next_pred - next_true) ** 2))),
            "direction_agreement": direction,
        })
    return rows


def main() -> None:
    rows = []
    for delta_r, stem in core.SWEEP.items():
        raw = core.read_lvm(core.SOURCE / stem / f"{stem}.lvm")[int(core.DROP_SECONDS * core.HZ):]
        prepared = []
        for pair in range(40):
            a, b, n, qa = core.prepare_pair(raw[:, pair], raw[:, pair + 40])
            prepared.append((a, b, n, core.Recorder.build(a[:n], b[:n]), qa))
        with ThreadPoolExecutor(max_workers=16) as pool:
            output = list(pool.map(lambda p: pair_diagnostic(delta_r, p, prepared), range(40)))
        for item in output:
            rows.extend(item)
    row_df = pd.DataFrame(rows)
    summary = row_df.groupby(["delta_r", "method"], as_index=False)[
        ["delta_RMSE_ARA", "next_position_RMSE_ARA", "direction_agreement"]
    ].median()
    free = pd.read_csv(core.RECORD_CSV)
    primary_free = free[free.method == "primary"][["delta_r", "RMSE_ARA", "waveform_r"]]
    summary = summary.merge(primary_free, on="delta_r", how="left")
    row_df.to_csv(ROWS, index=False); summary.to_csv(SUMMARY, index=False)

    prim = summary[summary.method == "primary"].set_index("delta_r").reindex(core.SWEEP)
    local_precise = (prim.next_position_RMSE_ARA <= 0.10) & (prim.direction_agreement >= 0.75)
    result = {
        "test": "T361B local record versus free restoration",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "locally_precise_records": int(local_precise.sum()),
        "locally_precise_delta_r": [int(x) for x in prim.index[local_precise]],
        "record_summary": summary.to_dict(orient="records"),
        "boundary": "post-result mechanism diagnostic; does not alter T361",
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")

    ink, blue, gold, orange, grey = "#222A33", "#3B6FB6", "#D99B2B", "#C76A2A", "#AAB3BE"
    fig, axes = plt.subplots(2, 2, figsize=(15, 11), facecolor="#F7F8FA")
    methods = [("primary", "four-state Di-ARA", gold), ("direction_blind", "direction-blind", grey), ("wrong_lineage", "wrong lineage", orange)]
    for method, label, color in methods:
        s = summary[summary.method == method].set_index("delta_r").reindex(core.SWEEP)
        axes[0, 0].plot(list(core.SWEEP), s.next_position_RMSE_ARA, "o-", color=color, label=label)
        axes[0, 1].plot(list(core.SWEEP), s.direction_agreement, "o-", color=color, label=label)
    axes[0, 0].axhline(0.10, color=ink, ls=":"); axes[0, 0].set(title="One-step child-position recovery", xlabel="ΔR (ohm)", ylabel="RMSE on ARA 0–2")
    axes[0, 1].axhline(0.75, color=ink, ls=":"); axes[0, 1].set(title="One-step child-direction recovery", xlabel="ΔR (ohm)", ylabel="agreement", ylim=(0, 1.03))
    axes[0, 0].legend(frameon=False); axes[0, 1].legend(frameon=False)

    axes[1, 0].plot(list(core.SWEEP), prim.next_position_RMSE_ARA, "o-", color=blue, label="local next step")
    axes[1, 0].plot(list(core.SWEEP), prim.RMSE_ARA, "s--", color=orange, label="free-running whole cycle")
    axes[1, 0].set(title="Local record versus accumulated restoration", xlabel="ΔR (ohm)", ylabel="RMSE on ARA 0–2"); axes[1, 0].legend(frameon=False)

    irr = pd.read_csv(core.IRR_CSV)
    pair_primary = row_df[row_df.method == "primary"].merge(irr, on=["delta_r", "pair"])
    sc = axes[1, 1].scatter(pair_primary.x_P, pair_primary.next_position_RMSE_ARA, c=pair_primary.delta_r, cmap="cividis", s=28, alpha=.75, edgecolor="none")
    axes[1, 1].axvline(1, color=ink, lw=1); axes[1, 1].axhline(.10, color=ink, ls=":")
    axes[1, 1].set(title="Address opening versus local record error", xlabel="x_P: reused → opening", ylabel="one-step position RMSE")
    fig.colorbar(sc, ax=axes[1, 1], label="ΔR (ohm)")
    for ax in axes.flat: ax.grid(alpha=.17)
    fig.suptitle("T361B — Does the Di-ARA record the next movement, or only restore some complete waves?", fontsize=17, y=.99)
    fig.text(.01, .01, "Post-result mechanism diagnostic; same frozen T361 relation table; no chance or regime classification", fontsize=9, color="#58616D")
    fig.tight_layout(rect=(0, .025, 1, .965)); fig.savefig(FIGURE, dpi=190, bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig)
    print(json.dumps({"locally_precise": result["locally_precise_records"], "delta_r": result["locally_precise_delta_r"]}, indent=2))


if __name__ == "__main__":
    main()


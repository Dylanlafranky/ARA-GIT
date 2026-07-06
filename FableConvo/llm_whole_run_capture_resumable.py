"""
llm_whole_run_capture_resumable.py — RECAPTURE of the lost WHOLE_RUN data.
===========================================================================
Method-identical to llm_whole_run_octave_sweep.py (same node layout, eager
guard, seed, prompt, sampling) with THREE workflow fixes so a dying Colab
window can never lose data again:
  1. SAVES A SHARD PER CHECKPOINT immediately (nothing held in RAM till end)
  2. WRITES TO GOOGLE DRIVE (survives runtime death; auto-detects Colab)
  3. RESUMABLE: re-running skips checkpoints whose shard already exists
Run as many sessions as needed; then run with MERGE=True once to build the
canonical llm_raw_node_series_WHOLE_RUN.npz from the shards.
S2 NOTE (LLM_WORK_SAFEGUARDS): second-family review before first run.
COLAB:
  !pip -q install "transformers==4.44.2"
"""
import os, time, csv, glob, numpy as np, torch
from transformers import GPTNeoXForCausalLM, AutoTokenizer

MERGE   = False        # set True (no GPU needed) to merge shards -> final npz
SIZES   = [("410m", "EleutherAI/pythia-410m-deduped", 410)]
STEPS   = [1,2,4,8,16,32,64,128,256,512,1000,2000,4000,8000,16000,32000,64000,128000,143000]
PROMPT  = "The framework proposes that natural oscillating systems"
N_STEPS = 200
SEED    = 42
DEVICE  = "cuda" if torch.cuda.is_available() else "cpu"

# --- storage: Google Drive if in Colab, else local dir ---------------------
SAVE_DIR = "whole_run_shards"
try:
    import google.colab
    from google.colab import drive
    drive.mount("/content/drive")
    SAVE_DIR = "/content/drive/MyDrive/ARA_whole_run_shards"
except ImportError:
    pass
os.makedirs(SAVE_DIR, exist_ok=True)
CSV_PATH = os.path.join(SAVE_DIR, "llm_closure_WHOLE_RUN.csv")

def shard_path(label, step):
    return os.path.join(SAVE_DIR, f"shard_{label}_step{step}.npz")

def capture(label, path, step):
    rev = f"step{step}"
    tok = AutoTokenizer.from_pretrained(path, revision=rev)
    model = GPTNeoXForCausalLM.from_pretrained(
        path, revision=rev, attn_implementation="eager",
        output_hidden_states=True, output_attentions=True).to(DEVICE).eval()
    assert model.config._attn_implementation == "eager"
    nL, nH = model.config.num_hidden_layers, model.config.num_attention_heads
    nN = (nL + 1) + nL * nH
    torch.manual_seed(SEED)
    ids = tok(PROMPT, return_tensors="pt").input_ids.to(DEVICE)
    ts = np.zeros((nN, N_STEPS), np.float32)
    past = None; cur = ids
    with torch.no_grad():
        for stp in range(N_STEPS):
            out = model(cur, past_key_values=past, use_cache=True,
                        output_hidden_states=True, output_attentions=True)
            past = out.past_key_values; i = 0
            for L in range(nL + 1):
                ts[i, stp] = float(torch.linalg.norm(out.hidden_states[L][0, -1]).item()); i += 1
            for L in range(nL):
                A = out.attentions[L][0, :, -1, :]
                for H in range(nH):
                    ts[i, stp] = float(A[H].max().item()); i += 1
            lg = out.logits[0, -1].float(); tv, ti = torch.topk(lg, 40); tv = tv - tv.max()
            p = torch.softmax(tv, -1)
            nxt = ti[0:1] if (torch.isnan(p).any() or (p < 0).any()) else ti[torch.multinomial(p, 1)]
            cur = nxt.unsqueeze(0)
    del model
    if DEVICE == "cuda": torch.cuda.empty_cache()
    return ts, nL, nH

def closure_row(ts, label, step, nL, nH, thresh=0.85):
    stds = ts.std(1); alive = stds > 1e-6; nA = int(alive.sum()); nN = len(ts)
    z = (ts - ts.mean(1, keepdims=True)) / (stds[:, None] + 1e-9); z[~alive] = 0
    C = np.clip(np.nan_to_num((z @ z.T) / ts.shape[1]), -1, 1); np.fill_diagonal(C, 1.0)
    adj = (np.abs(C) > thresh) & ~np.eye(nN, dtype=bool); Ai = adj.astype(np.int32)
    n_tri = int(np.trace(Ai @ Ai @ Ai) // 6); deg = adj.sum(1)
    return dict(model=f"pythia-{label}-deduped", step=step, nL=nL, nH=nH, n_alive=nA,
                n_triangles=n_tri, closure_ratio=round(n_tri / max(nA, 1), 4),
                loose_fraction=round(int(((deg < 2) & alive).sum()) / max(nA, 1), 4))

if MERGE:
    store, meta = {}, {}
    for f in sorted(glob.glob(os.path.join(SAVE_DIR, "shard_*.npz"))):
        d = np.load(f)
        base = os.path.basename(f)[6:-4]            # e.g. 410m_step143000
        label = base.split("_step")[0]
        store[base] = d["ts"]
        meta[f"{label}_nL"] = int(d["nL"]); meta[f"{label}_nH"] = int(d["nH"])
    out = os.path.join(SAVE_DIR, "llm_raw_node_series_WHOLE_RUN.npz")
    np.savez_compressed(out, **store, **{k: np.array(v) for k, v in meta.items()})
    print(f"merged {len(store)} shards -> {out}  (commit this to the git!)")
    raise SystemExit
for label, path, pm in SIZES:
    for step in STEPS:
        sp = shard_path(label, step)
        if os.path.exists(sp):
            try:
                np.load(sp)["ts"]; print(f"skip {label} step{step} (shard exists)"); continue
            except Exception:
                print(f"re-doing {label} step{step} (corrupt shard)")
        t0 = time.time()
        try:
            ts, nL, nH = capture(label, path, step)
            np.savez_compressed(sp, ts=ts, nL=nL, nH=nH)      # SAVED IMMEDIATELY
            row = closure_row(ts, label, step, nL, nH)
            row["elapsed_s"] = round(time.time() - t0, 1)
            new = not os.path.exists(CSV_PATH)
            with open(CSV_PATH, "a", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(row.keys()))
                if new: w.writeheader()
                w.writerow(row)
            print(f"{label} step{step}: closure {row['closure_ratio']}, "
                  f"loose {row['loose_fraction']} ({row['elapsed_s']}s) -> shard saved")
        except Exception as e:
            print(f"{label} step{step} ERROR: {e}")
print("Session done. Re-run any time to fill gaps; MERGE=True when complete.")

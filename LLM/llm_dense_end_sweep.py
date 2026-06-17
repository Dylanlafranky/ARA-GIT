"""
llm_dense_end_sweep.py  — RUN ON A GPU (Google Colab).

CLEAN re-run. The previous connection-ARA was measured with a corrupted method
(naked up/down count on a multi-system raw series — violated ARA decomposition
Rules 1-3). So this script does NOT compute ARA at all. It only:
  - captures the RAW node oscillations (ts_matrix) for every (size, checkpoint)
    and saves them to one small .npz, so ARA can be measured PROPERLY offline
    (canonical ground-cycle, phase-locked, one system per measurement) and
    re-derived freely without ever re-running the GPU job;
  - computes the two metrics that do NOT depend on ARA: closure_ratio and
    loose_fraction (closed Info^3 triangles / loose threads), as a side product.

Nothing is "confirmed" from a metric until it's reproduced from this clean run.

COLAB:
  !pip -q install "transformers==4.44.2"
  # run this file, then download BOTH:  llm_closure_RESULTS.csv  and  llm_raw_node_series.npz
"""
import os, time, csv, numpy as np, torch
from transformers import GPTNeoXForCausalLM, AutoTokenizer

SIZES = [
    ("1b",   "EleutherAI/pythia-1b-deduped",   1000),
    ("1.4b", "EleutherAI/pythia-1.4b-deduped", 1400),
    # ("410m","EleutherAI/pythia-410m-deduped", 410),    # re-add for continuity if you like
    # ("2.8b","EleutherAI/pythia-2.8b-deduped", 2800),   # needs an A100 (Colab Pro)
]
STEPS   = [3000,33000,63000,83000,93000,103000,113000,123000,133000,138000,143000]
PROMPT  = "The framework proposes that natural oscillating systems"
N_STEPS = 200
SEED    = 42
THRESH  = 0.85
DEVICE  = "cuda" if torch.cuda.is_available() else "cpu"
OUT_CSV = "llm_closure_DENSE_END.csv"
OUT_NPZ = "llm_raw_node_series_DENSE_END.npz"

raw_store = {}   # "70m_step0" -> ts_matrix (nN, N_STEPS) float32
meta      = {}   # "70m_nL","70m_nH" -> ints (so node layout is reconstructable offline)

def run(label, path, pm, step):
    rev = f"step{step}"
    tok = AutoTokenizer.from_pretrained(path, revision=rev)
    # MUST be eager: sdpa attention returns empty attentions, breaking the head-node graph.
    _dt = __import__("torch").float16 if DEVICE=="cuda" else None
    model = GPTNeoXForCausalLM.from_pretrained(
        path, revision=rev, attn_implementation="eager", torch_dtype=_dt,
        output_hidden_states=True, output_attentions=True).to(DEVICE).eval()
    # hard guard: fail loudly (don't silently produce a corrupt run) if attentions aren't returned
    assert model.config._attn_implementation == "eager", f"attn impl is {model.config._attn_implementation}, not eager"
    nL, nH = model.config.num_hidden_layers, model.config.num_attention_heads
    # node layout (deterministic): layer-norm nodes for L in 0..nL, then (layer,head) nodes
    nN = (nL + 1) + nL * nH
    torch.manual_seed(SEED)
    ids = tok(PROMPT, return_tensors="pt").input_ids.to(DEVICE)
    ts = np.zeros((nN, N_STEPS), np.float32)
    past = None; cur = ids; t0 = time.time()
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
    # closure / loose (independent of ARA)
    stds = ts.std(1); alive = stds > 1e-6; nA = int(alive.sum())
    z = (ts - ts.mean(1, keepdims=True)) / (stds[:, None] + 1e-9); z[~alive] = 0
    C = np.clip(np.nan_to_num((z @ z.T) / N_STEPS), -1, 1); np.fill_diagonal(C, 1.0)
    adj = (np.abs(C) > THRESH) & ~np.eye(nN, dtype=bool); Ai = adj.astype(np.int32)
    n_tri = int(np.trace(Ai @ Ai @ Ai) // 6)
    deg = adj.sum(1); n_under2 = int(((deg < 2) & alive).sum())
    el = round(time.time() - t0, 1)
    # stash raw series + layout for offline ARA
    raw_store[f"{label}_step{step}"] = ts
    meta[f"{label}_nL"] = nL; meta[f"{label}_nH"] = nH
    del model
    if DEVICE == "cuda": torch.cuda.empty_cache()
    return dict(model=f"pythia-{label}-deduped", params_m=pm, step=step, nL=nL, nH=nH,
                n_alive=nA, n_triangles=n_tri,
                closure_ratio=round(n_tri / max(nA, 1), 4),
                loose_fraction=round(n_under2 / max(nA, 1), 4), elapsed_s=el)

rows = []
for label, path, pm in SIZES:
    for step in STEPS:
        try:
            r = run(label, path, pm, step); rows.append(r)
            print(f"{label:5} step{step:<6} closure {r['closure_ratio']:>10}  loose {r['loose_fraction']:.3f}  ({r['elapsed_s']}s)")
        except Exception as e:
            print(f"{label} step{step} ERROR: {e}")

with open(OUT_CSV, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
np.savez_compressed(OUT_NPZ, **raw_store, **{k: np.array(v) for k, v in meta.items()})
print(f"\nSaved {len(rows)} rows -> {OUT_CSV}")
print(f"Saved raw node series -> {OUT_NPZ}  (download BOTH; drop into LLM/pythia_curves/)")

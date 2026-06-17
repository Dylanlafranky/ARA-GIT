"""
llm_gemma4_coupling.py — the ARA coupling-graph test, adapted to run on Gemma 4.

Same analysis as llm_size_series.py (Pythia), but model-agnostic via AutoModelForCausalLM
so it runs on Gemma 4 (or any causal LM). Records the same coupling-structure metrics:
alive %, within/across-layer ratio, spectral decay, anti-phase pairs, Information^3 closure
(triangles), loose fraction, intelligence index.

WHY A SEPARATE SCRIPT: Gemma 4 needs (1) AutoModelForCausalLM not GPTNeoXForCausalLM,
(2) attn_implementation="eager" to expose attention weights (default flash/sdpa returns None),
(3) gated weights — accept the license on the model card and set HF_TOKEN.

CANNOT run in the Cowork sandbox (no GPU, ~1 GB disk). Run on a GPU box or Colab.

------------------------------------------------------------------------------------------
SETUP
  pip install -U "transformers>=4.57" torch accelerate
  huggingface-cli login            # or: export HF_TOKEN=hf_xxx   (accept Gemma 4 license first)
RUN
  python llm_gemma4_coupling.py google/gemma-4-e2b           # smallest, ~CPU-feasible
  python llm_gemma4_coupling.py google/gemma-4-12b           # 48 layers — the depth-hypothesis target
  # add more model ids as args to build the size/depth series; results append to the .js file.
NOTE: confirm the exact HF repo id on the model card (e.g. -it for instruct, base for pretrained).
      For comparability with the Pythia series use the BASE (pretrained) checkpoints, not -it.
------------------------------------------------------------------------------------------
"""
import os, sys, json, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
REPO_ROOT = _PARENT if os.path.basename(_HERE) == "TheFormula" else _HERE
OUT_PATH = os.path.join(REPO_ROOT, 'TheFormula/llm_gemma4_coupling_data.js')

# Same prompt + seed + step count as the Pythia series, for apples-to-apples comparability.
PROMPT = "The framework proposes that natural oscillating systems"
N_STEPS = 200
SEED = 42
HF_TOKEN = os.environ.get('HF_TOKEN', None)
DTYPE = torch.bfloat16 if torch.cuda.is_available() else torch.float32

def run_one_model(model_id):
    label = model_id.split('/')[-1]
    print(f"\n=== {label} — loading {model_id}")
    tok = AutoTokenizer.from_pretrained(model_id, token=HF_TOKEN)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, token=HF_TOKEN, torch_dtype=DTYPE,
        attn_implementation="eager",          # REQUIRED so output_attentions returns weights
        device_map="auto" if torch.cuda.is_available() else None,
        output_hidden_states=True, output_attentions=True,
    )
    model.eval()
    cfg = model.config
    # Gemma 4 may nest text config; fall back gracefully.
    n_layers = getattr(cfg, 'num_hidden_layers', None) or getattr(getattr(cfg, 'text_config', cfg), 'num_hidden_layers')
    n_heads  = getattr(cfg, 'num_attention_heads', None) or getattr(getattr(cfg, 'text_config', cfg), 'num_attention_heads')
    hidden   = getattr(cfg, 'hidden_size', None) or getattr(getattr(cfg, 'text_config', cfg), 'hidden_size')
    params_m = round(sum(p.numel() for p in model.parameters())/1e6)
    print(f"   {n_layers} layers, {n_heads} heads, {hidden} dim, ~{params_m}M params")

    NODE_TYPES = [('layer_norm', L, None) for L in range(n_layers + 1)]
    for L in range(n_layers):
        for H in range(n_heads):
            NODE_TYPES.append(('head', L, H))
    n_nodes = len(NODE_TYPES)

    torch.manual_seed(SEED)
    dev = next(model.parameters()).device
    input_ids = tok(PROMPT, return_tensors='pt').input_ids.to(dev)
    ts = np.zeros((n_nodes, N_STEPS), dtype=np.float32)
    t0 = time.time(); past_kv = None; cur = input_ids
    with torch.no_grad():
        for step in range(N_STEPS):
            out = model(cur, past_key_values=past_kv, use_cache=True,
                        output_hidden_states=True, output_attentions=True)
            past_kv = out.past_key_values
            idx = 0
            for L in range(n_layers + 1):
                ts[idx, step] = float(torch.linalg.norm(out.hidden_states[L][0, -1].float()).item()); idx += 1
            for L in range(n_layers):
                A = out.attentions[L] if (out.attentions is not None and out.attentions[L] is not None) else None
                for H in range(n_heads):
                    ts[idx, step] = float(A[0, H, -1, :].max().item()) if A is not None else 0.0
                    idx += 1
            logits = out.logits[0, -1].float()
            tv, ti = torch.topk(logits, k=40); tv = tv - tv.max()
            probs = torch.softmax(tv, dim=-1)
            nxt = ti[0:1] if (torch.isnan(probs).any() or (probs < 0).any()) else ti[torch.multinomial(probs, 1)]
            cur = nxt.unsqueeze(0)
    elapsed = time.time() - t0
    print(f"   gen elapsed: {elapsed:.1f}s")

    stds = ts.std(axis=1); alive = stds > 1e-6; n_alive = int(alive.sum())
    z = (ts - ts.mean(axis=1, keepdims=True)) / (stds[:, None] + 1e-9); z[~alive] = 0
    C = np.clip(np.nan_to_num((z @ z.T) / N_STEPS), -1, 1); np.fill_diagonal(C, 1.0)
    node_layer = np.array([L if L is not None else -1 for _, L, _ in NODE_TYPES])
    within, across = [], []
    for i in range(n_nodes):
        if not alive[i]: continue
        s = (node_layer == node_layer[i]) & (np.arange(n_nodes) != i) & alive
        d = (node_layer != node_layer[i]) & alive
        if s.any(): within.append(C[i, s].mean())
        if d.any(): across.append(C[i, d].mean())
    ev = sorted(np.linalg.eigvalsh(C), reverse=True)
    adj = (np.abs(C) > 0.85) & ~np.eye(n_nodes, dtype=bool)
    Ai = adj.astype(np.int32); n_tri = int(np.trace(Ai @ Ai @ Ai) // 6)
    deg = adj.sum(axis=1); n_under2 = int(((deg < 2) & alive).sum())
    cross_pos = int(sum(1 for i in range(n_nodes) for j in range(i+1, n_nodes)
                        if alive[i] and alive[j] and C[i, j] > 0.85 and node_layer[i] != node_layer[j]))
    closure = n_tri / max(n_alive, 1); loose = n_under2 / max(n_alive, 1)
    return dict(label=label, model_id=model_id, params_m=params_m, n_layers=int(n_layers),
        n_heads=int(n_heads), hidden_size=int(hidden), n_nodes=n_nodes, n_alive=n_alive,
        alive_frac=round(n_alive/n_nodes, 4),
        n_strong_pos=int(((C > 0.85) & ~np.eye(n_nodes, dtype=bool)).sum() // 2),
        n_anti=int((C < -0.5).sum() // 2), n_super_anti=int((C < -0.85).sum() // 2),
        cross_layer_pos=cross_pos,
        within_layer_mean_corr=round(float(np.mean(within)), 4) if within else 0.0,
        across_layer_mean_corr=round(float(np.mean(across)), 4) if across else 0.0,
        within_to_across_ratio=round(float(np.mean(within)/max(np.mean(across), 1e-9)), 4) if within and across else 0.0,
        spectral_decay=round(float(ev[1]/max(ev[0], 1e-9)), 4),
        n_triangles=n_tri, closure_ratio=round(closure, 3), loose_fraction=round(loose, 3),
        intelligence_index=round(closure/max(loose, 0.001), 3), elapsed_seconds=round(elapsed, 1))

if __name__ == "__main__":
    ids = sys.argv[1:] or ["google/gemma-4-E2B"]
    results = []
    if os.path.exists(OUT_PATH):
        try: results = json.loads(open(OUT_PATH).read().split('=', 1)[1].rstrip(';\n').strip()).get('results', [])
        except Exception: results = []
    for mid in ids:
        results = [r for r in results if r.get('model_id') != mid]
        try:
            r = run_one_model(mid); results.append(r)
            print("   ->", {k: r[k] for k in ('n_layers','alive_frac','within_to_across_ratio','spectral_decay','n_anti','closure_ratio','intelligence_index')})
        except Exception as e:
            print(f"   FAILED {mid}: {e}")
    results.sort(key=lambda r: r['n_layers'])
    open(OUT_PATH, 'w').write("window.LLM_GEMMA4_DATA = " + json.dumps({'results': results}, indent=1) + ";\n")
    print(f"\nwrote {OUT_PATH} ({len(results)} models)")

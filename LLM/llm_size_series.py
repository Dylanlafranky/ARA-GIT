"""
llm_size_series.py — coupling-map analysis across the Pythia size series.

For each model size, run the same coupling-map analysis with the same prompt
and seed. Compare structural metrics across sizes. If emergent behaviour
corresponds to new coupling structure, we should see metrics change
non-monotonically at specific size thresholds.
"""
import os, sys, json, time
import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
# Repo root: parent dir if this script is in TheFormula/, else current dir
REPO_ROOT = _PARENT if os.path.basename(_HERE) == "TheFormula" else _HERE

sys.path.insert(0, os.environ.get('ARA_VENV', ''))
from transformers import GPTNeoXForCausalLM, AutoTokenizer

HF_CACHE = os.environ.get('HF_HOME', os.path.expanduser('~/.cache/huggingface'))
OUT_PATH = os.path.join(REPO_ROOT, 'TheFormula/llm_size_series_data.js')

# Models to try, in size order
MODEL_CONFIGS = [
    # (label, hf_name_or_path, params_M)
    ('70M',   'EleutherAI/pythia-70m-deduped',    70),
    ('160M',  'EleutherAI/pythia-160m-deduped',  160),
    ('410M',  'EleutherAI/pythia-410m-deduped',  410),
    ('1B',    'EleutherAI/pythia-1b-deduped',    1000),
]

PROMPT = "The framework proposes that natural oscillating systems"
N_STEPS = 200    # generation steps per model
SEED = 42

os.environ['HF_HOME'] = HF_CACHE
os.environ['TRANSFORMERS_OFFLINE'] = '1'

def run_one_model(label, path, params_m):
    print(f"\n=== {label} ({params_m}M params) — loading from {path}")
    if path.startswith('/'):
        # Manual path
        if not os.path.exists(path) or not os.path.exists(os.path.join(path, 'config.json')):
            print(f"   skipping {label} — manual path not present")
            return None
        tokenizer = AutoTokenizer.from_pretrained(path)
        model = GPTNeoXForCausalLM.from_pretrained(path, output_hidden_states=True, output_attentions=True)
    else:
        tokenizer = AutoTokenizer.from_pretrained(path, cache_dir=HF_CACHE)
        model = GPTNeoXForCausalLM.from_pretrained(path, cache_dir=HF_CACHE,
                                                    output_hidden_states=True, output_attentions=True)
    model.eval()
    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    print(f"   {n_layers} layers, {n_heads} heads, {model.config.hidden_size} dim")

    # Build node list
    NODE_TYPES = []
    for L in range(n_layers + 1):
        NODE_TYPES.append(('layer_norm', L, None))
    for L in range(n_layers):
        for H in range(n_heads):
            NODE_TYPES.append(('head', L, H))
    n_nodes = len(NODE_TYPES)

    # Generate
    torch.manual_seed(SEED)
    inputs = tokenizer(PROMPT, return_tensors='pt')
    input_ids = inputs.input_ids
    prompt_len = input_ids.shape[1]

    ts_matrix = np.zeros((n_nodes, N_STEPS), dtype=np.float32)

    t0 = time.time()
    past_kv = None
    cur = input_ids
    with torch.no_grad():
        for step in range(N_STEPS):
            out = model(cur, past_key_values=past_kv, use_cache=True,
                        output_hidden_states=True, output_attentions=True)
            past_kv = out.past_key_values
            idx = 0
            for L in range(n_layers + 1):
                ts_matrix[idx, step] = float(torch.linalg.norm(out.hidden_states[L][0, -1]).item())
                idx += 1
            for L in range(n_layers):
                A = out.attentions[L][0, :, -1, :]
                for H in range(n_heads):
                    ts_matrix[idx, step] = float(A[H].max().item())
                    idx += 1
            logits = out.logits[0, -1].float()
            tv, ti = torch.topk(logits, k=40)
            tv = tv - tv.max()
            probs = torch.softmax(tv, dim=-1)
            if torch.isnan(probs).any() or (probs < 0).any():
                nxt = ti[0:1]
            else:
                nxt = ti[torch.multinomial(probs, num_samples=1)]
            cur = nxt.unsqueeze(0)
            input_ids = torch.cat([input_ids, nxt.unsqueeze(0)], dim=1)
    elapsed = time.time() - t0
    print(f"   gen elapsed: {elapsed:.1f}s")

    # Coupling matrix
    stds = ts_matrix.std(axis=1)
    alive_mask = stds > 1e-6
    n_alive = int(alive_mask.sum())
    ts_z = (ts_matrix - ts_matrix.mean(axis=1, keepdims=True)) / (stds[:, None] + 1e-9)
    ts_z[~alive_mask, :] = 0
    C = (ts_z @ ts_z.T) / N_STEPS
    C = np.nan_to_num(C, nan=0.0, posinf=0.0, neginf=0.0)
    C = np.clip(C, -1.0, 1.0)
    np.fill_diagonal(C, 1.0)

    # Metrics
    n_strong_pos = int(((C > 0.85) & ~np.eye(n_nodes, dtype=bool)).sum() // 2)
    n_anti = int((C < -0.5).sum() // 2)
    n_super_pos = int(((C > 0.95) & ~np.eye(n_nodes, dtype=bool)).sum() // 2)
    n_super_anti = int((C < -0.85).sum() // 2)

    # Per-layer correlation: within-layer vs across-layer
    node_layer = np.array([L if L is not None else -1 for kind, L, H in NODE_TYPES])
    within_corrs = []
    across_corrs = []
    for i in range(n_nodes):
        if not alive_mask[i]: continue
        same_l = (node_layer == node_layer[i]) & (np.arange(n_nodes) != i) & alive_mask
        diff_l = (node_layer != node_layer[i]) & alive_mask
        if same_l.any(): within_corrs.append(C[i, same_l].mean())
        if diff_l.any(): across_corrs.append(C[i, diff_l].mean())

    # Spectral structure: top-k eigenvalues normalised
    eigvals = np.linalg.eigvalsh(C)
    eigvals_sorted = sorted(eigvals, reverse=True)
    spectral_decay = float(eigvals_sorted[1] / max(eigvals_sorted[0], 1e-9))  # 2nd / 1st eigenvalue
    spectral_top5_frac = float(sum(eigvals_sorted[:5]) / max(sum(np.abs(eigvals_sorted)), 1e-9))

    # Cross-layer strong-positive count
    cross_layer_pos = 0
    for i in range(n_nodes):
        for j in range(i+1, n_nodes):
            if alive_mask[i] and alive_mask[j] and C[i, j] > 0.85:
                if node_layer[i] != node_layer[j]:
                    cross_layer_pos += 1

    # Information^3 closure: count CLOSED TRIANGLES (3-cliques where all three pairs are strongly coupled)
    threshold = 0.85
    # Build adjacency on alive nodes only
    alive_idx = [i for i in range(n_nodes) if alive_mask[i]]
    adj_strong = (np.abs(C) > threshold) & ~np.eye(n_nodes, dtype=bool)
    # Count 3-cliques via matrix multiplication: triangle count = trace(A^3) / 6
    A_int = adj_strong.astype(np.int32)
    n_triangles = int(np.trace(A_int @ A_int @ A_int) // 6)

    # Also count loose threads: alive nodes with zero strong connections
    degree_strong = adj_strong.sum(axis=1)
    n_loose = int(((degree_strong == 0) & alive_mask).sum())
    n_under_2 = int(((degree_strong < 2) & alive_mask).sum())  # alive nodes with 0 or 1 connections

    # Closure ratio: triangles per alive node (the more, the more hierarchical structure)
    n_alive = int(alive_mask.sum())
    closure_ratio = n_triangles / max(n_alive, 1)
    loose_fraction = n_under_2 / max(n_alive, 1)

    return dict(
        label=label,
        params_m=params_m,
        n_layers=int(n_layers),
        n_heads=int(n_heads),
        hidden_size=int(model.config.hidden_size),
        n_nodes=int(n_nodes),
        n_alive=int(n_alive),
        alive_frac=float(n_alive / n_nodes),
        n_strong_pos=int(n_strong_pos),
        n_super_pos=int(n_super_pos),
        n_anti=int(n_anti),
        n_super_anti=int(n_super_anti),
        cross_layer_pos=int(cross_layer_pos),
        within_layer_mean_corr=float(np.mean(within_corrs)) if within_corrs else 0.0,
        across_layer_mean_corr=float(np.mean(across_corrs)) if across_corrs else 0.0,
        within_to_across_ratio=float(np.mean(within_corrs) / max(np.mean(across_corrs), 1e-9)) if within_corrs and across_corrs else 0.0,
        spectral_decay=spectral_decay,
        spectral_top5_frac=spectral_top5_frac,
        n_triangles=int(n_triangles),
        n_loose=int(n_loose),
        n_under_2=int(n_under_2),
        closure_ratio=round(closure_ratio, 3),
        loose_fraction=round(loose_fraction, 3),
        intelligence_index=round(closure_ratio / max(loose_fraction, 0.001), 3),
        elapsed_seconds=round(elapsed, 1),
    )

# Run all available models (or one specified by argv)
import sys as _sys
selected = None
if len(_sys.argv) > 1:
    selected = _sys.argv[1]
    print(f"Running only model: {selected}")
results = []
# Load existing results if appending
import os.path
if os.path.exists(OUT_PATH) and selected is not None:
    try:
        existing_text = open(OUT_PATH).read()
        existing = json.loads(existing_text.split('=', 1)[1].rstrip(';\n').strip())
        results = existing.get('results', [])
        # Remove any prior entry for this label
        results = [r for r in results if r['label'] != selected]
        print(f"Loaded {len(results)} prior results")
    except Exception as e:
        print(f"Could not load existing results: {e}")
        results = []

for label, path, params_m in MODEL_CONFIGS:
    if selected is not None and label != selected:
        continue
    try:
        r = run_one_model(label, path, params_m)
        if r is not None:
            results.append(r)
    except Exception as e:
        print(f"   error on {label}: {e}")

# Summary
print("\n\n========= SIZE SERIES SUMMARY =========")
print(f"{'size':<6} {'params':<8} {'n_lyr':<6} {'n_nodes':<8} {'alive%':<7} {'pos>0.85':<9} {'anti<-0.5':<10} {'cross_circ':<11} {'w/a ratio':<10} {'sp.decay':<9}")
for r in results:
    print(f"{r['label']:<6} {r['params_m']}M{'':<4} {r['n_layers']:<6} {r['n_nodes']:<8} {r['alive_frac']*100:<7.1f} {r['n_strong_pos']:<9} {r['n_anti']:<10} {r['cross_layer_pos']:<11} {r['within_to_across_ratio']:<10.2f} {r['spectral_decay']:<9.3f}")

with open(OUT_PATH, 'w') as fh:
    fh.write("window.LLM_SIZE_SERIES = " + json.dumps(dict(
        prompt=PROMPT, n_steps=N_STEPS, seed=SEED, results=results,
    ), default=str) + ";\n")
print(f"\nSaved -> {OUT_PATH}")

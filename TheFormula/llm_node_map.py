"""
llm_node_map.py — map LLM components by their dynamical coupling.

For each (layer, head) component, track its activation over generation steps.
Then compute pairwise coupling between every pair of components:
  - Pearson correlation (instantaneous co-movement)
  - Anti-correlation strength (matched-rung pair candidates — the framework's
    "two halves of one closed system" structure)
Embed each component in 2D space using spectral embedding on the coupling
matrix. Components that move together end up close; components that are
anti-phase end up on opposite sides; components that don't talk to each other
end up far apart.

Output: a scatter plot where each dot is a (layer, head) component, position
is determined by how it moves with the rest, colour is layer index. Plus a
list of strongest anti-phase pairs (matched-rung pair candidates).
"""
import os, sys, json, time
import numpy as np
import torch

sys.path.insert(0, '/sessions/amazing-cool-archimedes/venv')
from transformers import GPTNeoXForCausalLM, AutoTokenizer

HF_CACHE = '/sessions/amazing-cool-archimedes/hf-cache'
OUT_PATH = '/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder/TheFormula/llm_node_map_data.js'
MODEL_NAME = 'EleutherAI/pythia-70m-deduped'
N_STEPS = 250
SEED = 42

print("[1/5] Loading", MODEL_NAME)
os.environ['HF_HOME'] = HF_CACHE
os.environ['TRANSFORMERS_OFFLINE'] = '1'
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=HF_CACHE)
model = GPTNeoXForCausalLM.from_pretrained(MODEL_NAME, cache_dir=HF_CACHE,
                                            output_hidden_states=True, output_attentions=True)
model.eval()
n_layers = model.config.num_hidden_layers
n_heads = model.config.num_attention_heads
hidden_size = model.config.hidden_size
print("  ", n_layers, "layers,", n_heads, "heads,", hidden_size, "dim")

# Build the node list:
#   Each layer's residual stream norm (n_layers + 1 of them, including embedding)
#   Each (layer, head) pair's max-attention weight (n_layers × n_heads of them)
NODE_TYPES = []
for L in range(n_layers + 1):
    NODE_TYPES.append(('layer_norm', L, None))
for L in range(n_layers):
    for H in range(n_heads):
        NODE_TYPES.append(('head', L, H))
n_nodes = len(NODE_TYPES)
print("   total nodes:", n_nodes)

# Run autoregressive generation, record activation per node per step
PROMPT = "The framework proposes that natural oscillating systems"
print("[2/5] Generating", N_STEPS, "steps. Prompt:", repr(PROMPT))
torch.manual_seed(SEED)
inputs = tokenizer(PROMPT, return_tensors='pt')
input_ids = inputs.input_ids
prompt_len = input_ids.shape[1]

# Time series matrix: shape (n_nodes, N_STEPS)
ts_matrix = np.zeros((n_nodes, N_STEPS), dtype=np.float32)

t0 = time.time()
past_kv = None
cur = input_ids
with torch.no_grad():
    for step in range(N_STEPS):
        out = model(cur, past_key_values=past_kv, use_cache=True,
                    output_hidden_states=True, output_attentions=True)
        past_kv = out.past_key_values
        # Layer-norm nodes
        idx = 0
        for L in range(n_layers + 1):
            ts_matrix[idx, step] = float(torch.linalg.norm(out.hidden_states[L][0, -1]).item())
            idx += 1
        # Head nodes
        for L in range(n_layers):
            A = out.attentions[L][0, :, -1, :]  # [n_heads, seq_len]
            for H in range(n_heads):
                ts_matrix[idx, step] = float(A[H].max().item())
                idx += 1
        # Sample next token
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
        if (step + 1) % 100 == 0:
            print("   step", step+1, "elapsed", round(time.time()-t0, 1), "s")
elapsed = time.time() - t0
generated = tokenizer.decode(input_ids[0, prompt_len:])
print("   total elapsed:", round(elapsed, 1), "s")

# Compute coupling matrix
print("[3/5] Computing coupling matrix...")
# Z-score normalize each row
stds = ts_matrix.std(axis=1)
alive_mask = stds > 1e-6
print('   alive nodes:', int(alive_mask.sum()), '/', n_nodes, '(zero-variance dropped)')
ts_z = (ts_matrix - ts_matrix.mean(axis=1, keepdims=True)) / (stds[:, None] + 1e-9)
ts_z[~alive_mask, :] = 0  # zero out dead nodes
C = (ts_z @ ts_z.T) / N_STEPS
# Replace nan/inf with 0 (dead nodes)
C = np.nan_to_num(C, nan=0.0, posinf=0.0, neginf=0.0)
C = np.clip(C, -1.0, 1.0)
np.fill_diagonal(C, 1.0)
print("   correlation matrix shape:", C.shape, "  range:", round(C.min(),3), "to", round(C.max(),3))

# Spectral embedding: use absolute value of correlation as "similarity"
# (so anti-phase pairs are also "close" in coupling sense)
# Actually we want SIGNED — anti-phase nodes should end up on opposite sides
print("[4/5] Spectral embedding (top 2 eigenvectors)...")
# Symmetric matrix, use eigh
eigvals, eigvecs = np.linalg.eigh(C)
# Take top-2 eigenvectors (largest eigenvalues at the end)
# (skip the trivial top eigenvector which is the global mean direction)
emb = eigvecs[:, -3:-1]  # 2nd and 3rd largest, more discriminative
# Optionally scale by eigenvalue magnitude
emb = emb * np.sqrt(np.abs(eigvals[-3:-1]))[None, :]

# Find matched-rung pair candidates (strong anti-correlation)
print("[5/5] Identifying matched-rung pair candidates (strong anti-phase)...")
anti_pairs = []
for i in range(n_nodes):
    for j in range(i+1, n_nodes):
        if C[i, j] < -0.5:
            anti_pairs.append((i, j, float(C[i, j])))
anti_pairs.sort(key=lambda x: x[2])
print("   strong anti-phase pairs (corr < -0.5):", len(anti_pairs))
for i, j, c in anti_pairs[:8]:
    a = NODE_TYPES[i]; b = NODE_TYPES[j]
    print("     ", a, "<->", b, " corr=", round(c, 3))

# Find tight clusters (strong positive correlation > 0.85)
strong_pos_pairs = []
for i in range(n_nodes):
    for j in range(i+1, n_nodes):
        if C[i, j] > 0.85:
            strong_pos_pairs.append((i, j, float(C[i, j])))
strong_pos_pairs.sort(key=lambda x: -x[2])
print("   strong positive pairs (corr > 0.85):", len(strong_pos_pairs))
for i, j, c in strong_pos_pairs[:6]:
    a = NODE_TYPES[i]; b = NODE_TYPES[j]
    print("     ", a, "<->", b, " corr=", round(c, 3))

# Per-layer mean coupling (does coupling concentrate within layer or across layers?)
node_layer = []
for kind, L, H in NODE_TYPES:
    node_layer.append(L if L is not None else -1)
node_layer = np.array(node_layer)

within_layer_mean = []
across_layer_mean = []
for i in range(n_nodes):
    same_l = (node_layer == node_layer[i]) & (np.arange(n_nodes) != i)
    diff_l = (node_layer != node_layer[i])
    if same_l.any():
        within_layer_mean.append(C[i, same_l].mean())
    if diff_l.any():
        across_layer_mean.append(C[i, diff_l].mean())
print("\n   Within-layer mean correlation: ", round(np.mean(within_layer_mean), 3))
print("   Across-layer mean correlation:", round(np.mean(across_layer_mean), 3))

# Save
out_data = dict(
    model=MODEL_NAME, n_steps=N_STEPS, seed=SEED, prompt=PROMPT,
    n_layers=int(n_layers), n_heads=int(n_heads),
    nodes=[dict(idx=i, kind=kind, layer=(L if L is not None else None), head=(H if H is not None else None))
           for i, (kind, L, H) in enumerate(NODE_TYPES)],
    embedding=[[float(emb[i, 0]), float(emb[i, 1])] for i in range(n_nodes)],
    correlation_matrix=[[round(float(C[i, j]), 3) for j in range(n_nodes)] for i in range(n_nodes)],
    anti_pairs=[dict(i=int(i), j=int(j), corr=round(c, 3),
                     a=dict(kind=NODE_TYPES[i][0], layer=NODE_TYPES[i][1], head=NODE_TYPES[i][2]),
                     b=dict(kind=NODE_TYPES[j][0], layer=NODE_TYPES[j][1], head=NODE_TYPES[j][2]))
                for i, j, c in anti_pairs],
    strong_pos_pairs=[dict(i=int(i), j=int(j), corr=round(c, 3),
                          a=dict(kind=NODE_TYPES[i][0], layer=NODE_TYPES[i][1], head=NODE_TYPES[i][2]),
                          b=dict(kind=NODE_TYPES[j][0], layer=NODE_TYPES[j][1], head=NODE_TYPES[j][2]))
                     for i, j, c in strong_pos_pairs[:30]],
    summary=dict(
        within_layer_mean_corr=round(float(np.mean(within_layer_mean)), 3),
        across_layer_mean_corr=round(float(np.mean(across_layer_mean)), 3),
        n_anti_pairs=int(len(anti_pairs)),
        n_strong_pos_pairs=int(len(strong_pos_pairs)),
    ),
)
with open(OUT_PATH, 'w') as fh:
    fh.write("window.LLM_NODE_MAP = " + json.dumps(out_data, default=str) + ";\n")
print("\nSaved ->", OUT_PATH)

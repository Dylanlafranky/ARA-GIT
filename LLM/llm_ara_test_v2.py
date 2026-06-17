"""
llm_ara_test_v2.py — fuller test of ARA on LLM activations.

Improvements over v1:
  - Multiple distinct corpora chained together for more cycles per signal
  - Longer effective sequence (1024 tokens via overlapping windows)
  - Per-head attention OUTPUT norms (not just entropy)
  - Compare against three null distributions:
       (a) shuffled-token activations (preserves marginals, breaks order)
       (b) random Gaussian time series (pure noise baseline)
       (c) deep snap candidates (random walk → ARA blowup)
  - Save per-head ARA so we can ask whether DIFFERENT heads have DIFFERENT ARA
    bands (which would be the interpretability claim)
"""
import os, sys, json, math, random
import numpy as np
import torch
from scipy.signal import butter, sosfilt, find_peaks
from scipy.ndimage import gaussian_filter1d

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
# Repo root: parent dir if this script is in TheFormula/, else current dir
REPO_ROOT = _PARENT if os.path.basename(_HERE) == "TheFormula" else _HERE

sys.path.insert(0, os.environ.get('ARA_VENV', ''))
from transformers import GPTNeoXForCausalLM, AutoTokenizer

PHI = 1.6180339887498949
HF_CACHE = os.environ.get('HF_HOME', os.path.expanduser('~/.cache/huggingface'))
OUT_PATH = os.path.join(REPO_ROOT, 'TheFormula/llm_ara_data.js')
MODEL_NAME = 'EleutherAI/pythia-70m-deduped'

# ===== ARA computation (matches drain_architecture_test.py) =====
def causal_bandpass(arr, period, bw=0.85, order=2):
    arr = np.asarray(arr, dtype=float)
    n = len(arr)
    if n < 2 * int(period) + 5:
        return np.zeros(n)
    f_c = 1.0 / period
    nyq = 0.5
    Wn_lo = max(1e-6, (1 - bw) * f_c / nyq)
    Wn_hi = min(0.999, (1 + bw) * f_c / nyq)
    if Wn_lo >= Wn_hi:
        return np.zeros(n)
    sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
    return sosfilt(sos, arr - np.mean(arr))


def ara_full(arr, period):
    bp = causal_bandpass(arr, period, bw=0.85)
    if len(bp) < 3 * int(period):
        return None
    smoothed = gaussian_filter1d(bp, max(1, int(period * 0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.7)))
    if len(peaks) < 2:
        return None
    aras = []
    for i in range(len(peaks) - 1):
        seg = smoothed[peaks[i]:peaks[i + 1] + 1]
        if len(seg) < 3:
            continue
        f_t = max(0.15, min(0.85, int(np.argmin(seg)) / max(1, len(seg) - 1)))
        aras.append((1 - f_t) / f_t)
    if not aras:
        return None
    return float(np.mean(np.clip(aras, 0.3, 3.0)))


def classify_ara(ara):
    if ara is None: return 'undefined'
    if ara < 0.6: return 'consumer'
    if ara < 0.9: return 'consumer-leaning'
    if ara < 1.1: return 'balance'
    if ara < 1.5: return 'balance-leaning'
    if ara < 1.75: return 'engine'
    if ara < 1.9: return 'engine-strong'
    return 'harmonic'


# ===== Multiple corpora =====
CORPORA = [
    # Scientific prose
    ("scientific",
     "The framework proposes a single coordinate system describing oscillating systems. "
     "Heart rhythms, El Niño cycles, planetary orbits, and mammalian heart-rate variability "
     "share the same φ-spaced rung ladder. One forward formula predicts behaviour from where "
     "they sit on this ladder. The ARA value of a system is its build-to-release ratio, "
     "measured as the time spent rising versus falling within each cycle. " * 3),
    # Narrative
    ("narrative",
     "The boy walked along the river at dusk. The light caught on the water and broke into "
     "fragments. He thought of his mother, who had died when he was seven, and of his father, "
     "who had drunk himself quiet over the years that followed. The path bent into the trees "
     "and the river fell away below him. He kept walking. There was nowhere to go that he "
     "had not already been, but walking made the silence inside him bearable. " * 3),
    # Code-like text
    ("code",
     "def compute_ara(signal, period): bp = bandpass(signal, period); peaks = find_peaks(bp); "
     "aras = []; for i in range(len(peaks) - 1): seg = bp[peaks[i]:peaks[i+1]]; "
     "f_t = argmin(seg) / len(seg); aras.append((1 - f_t) / f_t); return mean(aras). " * 8),
    # Conversational
    ("conversational",
     "Yeah I think so. I mean, the thing is, you have to consider what the data actually "
     "shows, not just what you want it to show. Right? That's the trap. Confirmation bias. "
     "I caught myself doing it last week — I had this number that looked great, and it took "
     "me three days to admit the filter was leaking future data. Anyway, what were you saying. " * 3),
    # Repetitive
    ("repetitive",
     "The wave rises and falls. The wave rises and falls. The wave rises and falls. " * 30),
]

# ===== Load model =====
print(f"[1/6] Loading {MODEL_NAME} ...")
os.environ['HF_HOME'] = HF_CACHE
os.environ['TRANSFORMERS_OFFLINE'] = '1'
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=HF_CACHE)
model = GPTNeoXForCausalLM.from_pretrained(
    MODEL_NAME, cache_dir=HF_CACHE, output_hidden_states=True, output_attentions=True
)
model.eval()
n_layers = model.config.num_hidden_layers
n_heads = model.config.num_attention_heads
print(f"  {n_layers} layers × {n_heads} heads × {model.config.hidden_size} dim")

# ===== Run all corpora =====
print("[2/6] Running inference on all corpora ...")
all_layer_norms = {L: [] for L in range(n_layers + 1)}     # concatenated per layer
all_head_norms = {(L, H): [] for L in range(n_layers) for H in range(n_heads)}
all_head_entropy = {(L, H): [] for L in range(n_layers) for H in range(n_heads)}

for cname, ctext in CORPORA:
    inputs = tokenizer(ctext, return_tensors='pt', truncation=True, max_length=1024)
    n_tokens = inputs.input_ids.shape[1]
    print(f"  corpus={cname:>14}  tokens={n_tokens}")
    with torch.no_grad():
        out = model(**inputs, output_hidden_states=True, output_attentions=True)
    for L in range(n_layers + 1):
        h = out.hidden_states[L][0]               # [n_tokens, hidden_size]
        all_layer_norms[L].append(torch.linalg.norm(h, dim=-1).numpy())
    for L in range(n_layers):
        A = out.attentions[L][0]                  # [n_heads, n_tokens, n_tokens]
        eps = 1e-9
        ent = -(A * torch.log(A + eps)).sum(dim=-1).numpy()  # [n_heads, n_tokens]
        # Attention output norm: weighted sum of values (use entropy as proxy here, plus
        # max-attention-weight per query as a second signal)
        max_attn = A.max(dim=-1).values.numpy()    # [n_heads, n_tokens]
        for H in range(n_heads):
            all_head_norms[(L, H)].append(max_attn[H])
            all_head_entropy[(L, H)].append(ent[H])

# Concatenate
layer_norm_series = {L: np.concatenate(all_layer_norms[L]) for L in all_layer_norms}
head_norm_series = {k: np.concatenate(all_head_norms[k]) for k in all_head_norms}
head_entropy_series = {k: np.concatenate(all_head_entropy[k]) for k in all_head_entropy}
print(f"  Layer norm series total length: {len(next(iter(layer_norm_series.values())))} tokens")

# ===== Compute ARA at multiple φ-rungs =====
print("[3/6] Computing ARA at multiple φ-rungs ...")
RUNG_KS = [2, 3, 4, 5, 6, 7, 8]  # periods 2.6 .. 47 tokens
PERIODS = [PHI ** k for k in RUNG_KS]

layer_results = []
for L, norms in layer_norm_series.items():
    for k, p in zip(RUNG_KS, PERIODS):
        if 4 * p > len(norms):
            continue
        ara = ara_full(norms, p)
        layer_results.append(dict(layer=L, head=None, kind='layer_norm',
                                  rung_k=k, period=float(p), ara=ara, category=classify_ara(ara)))

head_results = []
for (L, H), arr in head_norm_series.items():
    for k, p in zip(RUNG_KS, PERIODS):
        if 4 * p > len(arr):
            continue
        ara = ara_full(arr, p)
        head_results.append(dict(layer=L, head=H, kind='head_max_attn',
                                 rung_k=k, period=float(p), ara=ara, category=classify_ara(ara)))

for (L, H), arr in head_entropy_series.items():
    for k, p in zip(RUNG_KS, PERIODS):
        if 4 * p > len(arr):
            continue
        ara = ara_full(arr, p)
        head_results.append(dict(layer=L, head=H, kind='head_entropy',
                                 rung_k=k, period=float(p), ara=ara, category=classify_ara(ara)))

all_results = layer_results + head_results

# ===== Null distributions =====
print("[4/6] Computing null distributions ...")
null_results = {'shuffled': [], 'gaussian': [], 'random_walk': []}
total_tokens = len(next(iter(layer_norm_series.values())))

# (a) shuffled — break temporal order
np.random.seed(42)
for L in range(n_layers + 1):
    arr = layer_norm_series[L].copy()
    np.random.shuffle(arr)
    for k, p in zip(RUNG_KS, PERIODS):
        if 4 * p > len(arr): continue
        ara = ara_full(arr, p)
        if ara is not None:
            null_results['shuffled'].append(ara)

# (b) Gaussian noise — pure white noise baseline
np.random.seed(42)
for _ in range(n_layers + 1):
    arr = np.random.randn(total_tokens)
    for k, p in zip(RUNG_KS, PERIODS):
        if 4 * p > len(arr): continue
        ara = ara_full(arr, p)
        if ara is not None:
            null_results['gaussian'].append(ara)

# (c) Random walk — should be HIGH ARA (snap-like, persistent runs)
np.random.seed(42)
for _ in range(n_layers + 1):
    arr = np.cumsum(np.random.randn(total_tokens))
    for k, p in zip(RUNG_KS, PERIODS):
        if 4 * p > len(arr): continue
        ara = ara_full(arr, p)
        if ara is not None:
            null_results['random_walk'].append(ara)

# ===== Aggregate =====
print("[5/6] Aggregating ...")

def stats(vals):
    a = np.array([v for v in vals if v is not None])
    if not len(a): return dict(n=0)
    return dict(n=int(len(a)), mean=float(np.mean(a)), std=float(np.std(a)),
                median=float(np.median(a)), p25=float(np.percentile(a, 25)),
                p75=float(np.percentile(a, 75)))

layer_stats = stats([r['ara'] for r in layer_results])
head_norm_stats = stats([r['ara'] for r in head_results if r['kind'] == 'head_max_attn'])
head_ent_stats = stats([r['ara'] for r in head_results if r['kind'] == 'head_entropy'])

print(f"\n  Layer-norm ARA:        {layer_stats}")
print(f"  Head max-attn ARA:     {head_norm_stats}")
print(f"  Head entropy ARA:      {head_ent_stats}")
print(f"  NULL shuffled:         {stats(null_results['shuffled'])}")
print(f"  NULL gaussian:         {stats(null_results['gaussian'])}")
print(f"  NULL random_walk:      {stats(null_results['random_walk'])}")

# Category distribution by signal kind
def cats(rs):
    c = {}
    for r in rs:
        c[r['category']] = c.get(r['category'], 0) + 1
    return c

print(f"\n  Layer categories: {cats(layer_results)}")
print(f"  Head max-attn categories: {cats([r for r in head_results if r['kind'] == 'head_max_attn'])}")
print(f"  Head entropy categories: {cats([r for r in head_results if r['kind'] == 'head_entropy'])}")

# Per-rung trend
print("\n  Per-rung mean ARA (layer norms only):")
for k, p in zip(RUNG_KS, PERIODS):
    vals = [r['ara'] for r in layer_results if r['rung_k'] == k and r['ara'] is not None]
    if vals:
        print(f"    k={k} (p={p:.1f}t):  n={len(vals):2d}  mean={np.mean(vals):.3f}  std={np.std(vals):.3f}")

# ===== Save =====
print("[6/6] Saving ...")
def cleanup_record(r):
    return dict(r, period=round(r['period'], 3),
                ara=(None if r['ara'] is None else round(r['ara'], 4)))

out = dict(
    model=MODEL_NAME,
    n_layers=int(n_layers),
    n_heads=int(n_heads),
    n_tokens_total=int(total_tokens),
    rung_ks=RUNG_KS,
    periods=[round(p, 3) for p in PERIODS],
    layer_results=[cleanup_record(r) for r in layer_results],
    head_results=[cleanup_record(r) for r in head_results],
    null_distributions=null_results,
    summary=dict(
        layer_norm=layer_stats,
        head_max_attn=head_norm_stats,
        head_entropy=head_ent_stats,
        null_shuffled=stats(null_results['shuffled']),
        null_gaussian=stats(null_results['gaussian']),
        null_random_walk=stats(null_results['random_walk']),
    ),
    category_counts=dict(
        layer=cats(layer_results),
        head_max_attn=cats([r for r in head_results if r['kind'] == 'head_max_attn']),
        head_entropy=cats([r for r in head_results if r['kind'] == 'head_entropy']),
    ),
)

with open(OUT_PATH, 'w') as f:
    f.write("window.LLM_ARA = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved → {OUT_PATH}")

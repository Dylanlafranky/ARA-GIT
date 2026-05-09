"""
llm_ara_test.py — does the ARA framework characterise LLM internal activations?

The framework's claim: any oscillating system can be summarised by an ARA
value (build/release ratio of cycles), and self-organising systems cluster
into bands [consumer ~0.5, balance ~1.0, engine ~φ, harmonic ~2.0].

Test: do per-layer / per-head activations inside a small open LLM
cluster into the same bands when treated as time-series over token positions?

Method:
  1. Load Pythia-160M (12 layers × 12 heads, ~160M params, open).
  2. Run inference on a corpus (concatenated public-domain text).
  3. For each layer:
       - residual stream norm at each token position → 1 time series per layer
  4. For each (layer, head):
       - attention output norm at each token position → 1 time series per head
  5. Compute ARA on each time series at multiple φ-rung periods.
  6. Histogram the ARA values.
  7. See if they cluster into the framework's bands.

If they do: real interpretability tool. If they don't: the framework's
universality is bounded to systems with intrinsic oscillations and doesn't
extend to passive feed-forward networks.

Either way the result is informative.
"""
import os, sys, json, math
import numpy as np
import torch
from scipy.signal import butter, sosfilt, find_peaks
from scipy.ndimage import gaussian_filter1d

# Use the venv-installed transformers
sys.path.insert(0, '/sessions/amazing-cool-archimedes/venv')

from transformers import GPTNeoXForCausalLM, AutoTokenizer

PHI = 1.6180339887498949
HF_CACHE = '/sessions/amazing-cool-archimedes/hf-cache'
OUT_PATH = '/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder/TheFormula/llm_ara_data.js'

# === Same ARA computation that drain_architecture_test.py uses ===
def causal_bandpass(arr, period, bw=0.4, order=2):
    arr = np.asarray(arr, dtype=float)
    if len(arr) < 2 * int(period) + 5:
        return np.zeros(len(arr))
    f_c = 1.0 / period
    nyq = 0.5
    Wn_lo = max(1e-6, (1 - bw) * f_c / nyq)
    Wn_hi = min(0.999, (1 + bw) * f_c / nyq)
    if Wn_lo >= Wn_hi:
        return np.zeros(len(arr))
    sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
    return sosfilt(sos, arr - np.mean(arr))


def ara_full(arr, period):
    """Build/release time ratio of cycles, averaged. ARA = (rise) / (fall).
       ARA = 1.0 → symmetric (balance); ARA > 1 → engine-like; ARA < 1 → consumer-like."""
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
    """Map ARA to framework category."""
    if ara is None:
        return 'undefined'
    if ara < 0.6:
        return 'consumer'
    if ara < 0.9:
        return 'consumer-leaning'
    if ara < 1.1:
        return 'balance'
    if ara < 1.5:
        return 'balance-leaning'
    if ara < 1.75:
        return 'engine'  # near φ
    if ara < 1.9:
        return 'engine-strong'
    return 'harmonic'  # near 2.0


# === Load model ===
print("[1/5] Loading Pythia-160M ...")
MODEL_NAME = 'EleutherAI/pythia-70m-deduped'  # 6 layers × 8 heads × 512 dim — smallest in the Pythia suite, still a real transformer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=HF_CACHE)
model = GPTNeoXForCausalLM.from_pretrained(
    MODEL_NAME, cache_dir=HF_CACHE, output_hidden_states=True, output_attentions=True
)
model.eval()
print(f"  Loaded: {model.config.num_hidden_layers} layers × {model.config.num_attention_heads} heads × {model.config.hidden_size} dim")

# === Prepare corpus ===
# Use a chunk of mixed public-domain text. Long enough to get cycles at multiple φ-rungs.
CORPUS = (
    "The framework proposes a single coordinate system describing oscillating systems. "
    "Heart rhythms, El Niño cycles, planetary orbits, and mammalian heart-rate variability "
    "share the same φ-spaced rung ladder. One forward formula predicts behaviour from where "
    "they sit on this ladder. The ARA value of a system is its build-to-release ratio, "
    "measured as the time spent rising versus falling within each cycle. Self-organising "
    "systems cluster near three values: half (consumer), one (balance), and the golden ratio "
    "(engine). Pure harmonic oscillators sit at exactly two — they have handed off all their "
    "time-content to an external driver. The 3/4 ceiling claim says no self-organising system "
    "can deviate more than three-quarters of the way from balance toward either singularity. "
    "Tests on 77 systems support this. Across heart, climate, and mammalian heart-rate data, "
    "the same canonical predictor module produces the same kind of forecast skill without "
    "domain-specific tuning. This suggests the rung ladder is not a domain-specific artifact "
    "but a real geometric structure shared by oscillating systems regardless of substrate. "
    "Whether artificial systems like neural networks share this geometry is an open question. "
    "If they do, the framework gives an interpretability tool — a single number per layer or "
    "head that classifies what the component is doing dynamically. If not, the framework's "
    "universality is bounded to systems with intrinsic oscillation periods, which would itself "
    "be useful to know. The experiment that decides this is straightforward: run an open model, "
    "extract layer and head activations as time-series over token positions, compute ARA at "
    "multiple φ-rung periods, and see whether the values cluster meaningfully. "
) * 4  # ~4× for length

print("[2/5] Tokenising corpus ...")
inputs = tokenizer(CORPUS, return_tensors='pt', truncation=True, max_length=512)
n_tokens = inputs.input_ids.shape[1]
print(f"  Corpus: {n_tokens} tokens")

# === Run inference, capture all internals ===
print("[3/5] Running inference, capturing activations ...")
with torch.no_grad():
    outputs = model(**inputs, output_hidden_states=True, output_attentions=True)

# hidden_states: tuple of (n_layers + 1) tensors, each [1, n_tokens, hidden_size]
# attentions: tuple of n_layers tensors, each [1, n_heads, n_tokens, n_tokens]
hidden_states = outputs.hidden_states
attentions = outputs.attentions
n_layers = len(hidden_states) - 1
n_heads = attentions[0].shape[1]
print(f"  Captured {n_layers} hidden_state layers, {len(attentions)} attention layers, {n_heads} heads each")

# === Build time series ===
# Per-layer: residual stream L2 norm at each token position
layer_norms = []
for L in range(n_layers + 1):  # include embedding layer at index 0
    h = hidden_states[L][0]  # [n_tokens, hidden_size]
    norms = torch.linalg.norm(h, dim=-1).numpy()
    layer_norms.append(norms)

# Per-head: attention entropy at each query token (a scalar per token per head)
head_entropy = np.zeros((n_layers, n_heads, n_tokens))
for L in range(n_layers):
    A = attentions[L][0]  # [n_heads, n_tokens, n_tokens]
    # For each query position q, compute entropy of attention distribution over keys
    eps = 1e-9
    ent = -(A * torch.log(A + eps)).sum(dim=-1)  # [n_heads, n_tokens]
    head_entropy[L] = ent.numpy()

# === Compute ARA at multiple φ-rung periods ===
print("[4/5] Computing ARA per layer and per head ...")
# Periods to test: φ^k for k = 2..7 (i.e., periods 2.6, 4.2, 6.9, 11.1, 17.9, 28.9 tokens)
# n_tokens = 512, so we need at least 4*period ≤ n_tokens → period ≤ 128 → k ≤ 10
RUNG_KS = [2, 3, 4, 5, 6, 7]
PERIODS = [PHI ** k for k in RUNG_KS]

layer_results = []
for L, norms in enumerate(layer_norms):
    for k, p in zip(RUNG_KS, PERIODS):
        ara = ara_full(norms, p)
        layer_results.append(dict(
            kind='layer_norm',
            layer=L,
            head=None,
            rung_k=k,
            period=p,
            ara=ara,
            category=classify_ara(ara),
        ))

head_results = []
for L in range(n_layers):
    for H in range(n_heads):
        for k, p in zip(RUNG_KS, PERIODS):
            ara = ara_full(head_entropy[L, H], p)
            head_results.append(dict(
                kind='head_entropy',
                layer=L,
                head=H,
                rung_k=k,
                period=p,
                ara=ara,
                category=classify_ara(ara),
            ))

# === Aggregate ===
print("[5/5] Aggregating ...")
all_results = layer_results + head_results

# Distribution of ARA values
all_aras = [r['ara'] for r in all_results if r['ara'] is not None]
print(f"  Total ARA measurements: {len(all_aras)}")
print(f"  ARA distribution: mean={np.mean(all_aras):.3f}, std={np.std(all_aras):.3f}, "
      f"median={np.median(all_aras):.3f}")

cats = {}
for r in all_results:
    cats[r['category']] = cats.get(r['category'], 0) + 1
print(f"  Category counts: {cats}")

# Per-rung breakdown
print("\nPer-rung mean ARA:")
for k, p in zip(RUNG_KS, PERIODS):
    vals = [r['ara'] for r in all_results if r['rung_k'] == k and r['ara'] is not None]
    if vals:
        print(f"  rung k={k} (period={p:.1f} tokens): n={len(vals):3d}, mean={np.mean(vals):.3f}, "
              f"std={np.std(vals):.3f}")

# Save
with open(OUT_PATH, 'w') as f:
    f.write("window.LLM_ARA = " + json.dumps(dict(
        model=MODEL_NAME,
        n_tokens=int(n_tokens),
        n_layers=int(n_layers),
        n_heads=int(n_heads),
        rung_ks=RUNG_KS,
        periods=PERIODS,
        layer_results=[dict(r, ara=(None if r['ara'] is None else round(r['ara'], 4)))
                       for r in layer_results],
        head_results=[dict(r, ara=(None if r['ara'] is None else round(r['ara'], 4)))
                      for r in head_results],
        all_aras=[round(a, 4) for a in all_aras],
        category_counts=cats,
        summary=dict(
            mean=float(np.mean(all_aras)),
            std=float(np.std(all_aras)),
            median=float(np.median(all_aras)),
        ),
    ), default=str) + ";\n")
print(f"\nSaved → {OUT_PATH}")

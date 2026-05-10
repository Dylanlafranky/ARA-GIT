"""
llm_ara_test_v3_dynamic.py — autoregressive-generation ARA test.

Earlier tests measured activations across token POSITIONS in a single fixed
sequence — a snapshot of a system, not its evolution. Not analogous to ENSO
(months evolving) or ECG (heartbeats evolving).

Here we run the model AUTOREGRESSIVELY, generating one token at a time, and
record per-layer activations at each generation step. Real time series of
internal state evolution.
"""
import os, sys, json, time
import numpy as np
import torch
from scipy.signal import butter, sosfilt, find_peaks
from scipy.ndimage import gaussian_filter1d

sys.path.insert(0, '/sessions/amazing-cool-archimedes/venv')
from transformers import GPTNeoXForCausalLM, AutoTokenizer

PHI = 1.6180339887498949
HF_CACHE = '/sessions/amazing-cool-archimedes/hf-cache'
OUT_PATH = '/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder/TheFormula/llm_ara_dynamic_data.js'
MODEL_NAME = 'EleutherAI/pythia-70m-deduped'

def causal_bandpass(arr, period, bw=0.85, order=2):
    arr = np.asarray(arr, dtype=float); n = len(arr)
    if n < 2 * int(period) + 5: return np.zeros(n)
    f_c = 1.0/period; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
    return sosfilt(sos, arr - np.mean(arr))

def ara_full(arr, period):
    bp = causal_bandpass(arr, period, bw=0.85)
    if len(bp) < 3*int(period): return None
    smoothed = gaussian_filter1d(bp, max(1, int(period*0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period*0.7)))
    if len(peaks) < 2: return None
    aras = []
    for i in range(len(peaks)-1):
        seg = smoothed[peaks[i]:peaks[i+1]+1]
        if len(seg) < 3: continue
        f_t = max(0.15, min(0.85, int(np.argmin(seg))/max(1, len(seg)-1)))
        aras.append((1-f_t)/f_t)
    if not aras: return None
    return float(np.mean(np.clip(aras, 0.3, 3.0)))

def classify_ara(a):
    if a is None: return 'undefined'
    if a < 0.6: return 'consumer'
    if a < 0.9: return 'consumer-leaning'
    if a < 1.1: return 'balance'
    if a < 1.5: return 'balance-leaning'
    if a < 1.75: return 'engine'
    if a < 1.9: return 'engine-strong'
    return 'harmonic'

print("[1/4] Loading", MODEL_NAME)
os.environ['HF_HOME'] = HF_CACHE
os.environ['TRANSFORMERS_OFFLINE'] = '1'
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=HF_CACHE)
model = GPTNeoXForCausalLM.from_pretrained(MODEL_NAME, cache_dir=HF_CACHE,
                                            output_hidden_states=True, output_attentions=False)
model.eval()
n_layers = model.config.num_hidden_layers
print("  ", n_layers, "layers,", model.config.num_attention_heads, "heads,", model.config.hidden_size, "dim")

PROMPT = "The framework proposes that natural oscillating systems"
N_STEPS = 250
print("[2/4] Running", N_STEPS, "step autoregressive generation. Prompt:", repr(PROMPT))
inputs = tokenizer(PROMPT, return_tensors='pt')
input_ids = inputs.input_ids
prompt_len = input_ids.shape[1]

layer_norm_ts = {L: [] for L in range(n_layers + 1)}

t0 = time.time()
past_kv = None
cur = input_ids
with torch.no_grad():
    for step in range(N_STEPS):
        out = model(cur, past_key_values=past_kv, use_cache=True,
                    output_hidden_states=True, output_attentions=False)
        past_kv = out.past_key_values
        for L in range(n_layers + 1):
            h = out.hidden_states[L][0, -1]
            layer_norm_ts[L].append(float(torch.linalg.norm(h).item()))
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
        if (step + 1) % 50 == 0:
            print("   step", step+1, "elapsed", round(time.time()-t0, 1), "s")
            sys.stdout.flush()

elapsed = time.time() - t0
gen = tokenizer.decode(input_ids[0, prompt_len:])
print("   total elapsed:", round(elapsed, 1), "s. Generated:", repr(gen[:160]))

print("[3/4] Computing ARA per layer per rung...")
RUNG_KS = [2, 3, 4, 5, 6, 7, 8, 9]
PERIODS = [PHI ** k for k in RUNG_KS]

results = []
for L, ts in layer_norm_ts.items():
    arr = np.array(ts)
    for k, p in zip(RUNG_KS, PERIODS):
        if 4 * p > len(arr): continue
        a = ara_full(arr, p)
        results.append(dict(layer=L, rung_k=k, period=float(p),
                            ara=a, category=classify_ara(a)))

# Null: random walks of same length
null_results = []
np.random.seed(42)
for trial in range(20):
    arr = np.cumsum(np.random.randn(N_STEPS))
    for k, p in zip(RUNG_KS, PERIODS):
        if 4 * p > len(arr): continue
        a = ara_full(arr, p)
        null_results.append(dict(trial=trial, rung_k=k, period=float(p), ara=a))

print("[4/4] Aggregating...")

def stats(vals):
    a = np.array([v for v in vals if v is not None])
    if not len(a): return dict(n=0)
    return dict(n=int(len(a)), mean=float(np.mean(a)), std=float(np.std(a)),
                median=float(np.median(a)))

real_aras = [r['ara'] for r in results if r['ara'] is not None]
null_aras = [r['ara'] for r in null_results if r['ara'] is not None]

print("  REAL  Pythia-70M dynamic:", stats(real_aras))
print("  NULL  random walk:       ", stats(null_aras))
print()
print("  Per-rung mean ARA:")
print("  rung   period   real(n)         null(n)        gap")
for k, p in zip(RUNG_KS, PERIODS):
    rv = [r['ara'] for r in results if r['rung_k']==k and r['ara'] is not None]
    nv = [r['ara'] for r in null_results if r['rung_k']==k and r['ara'] is not None]
    if rv and nv:
        rm = np.mean(rv); nm = np.mean(nv)
        print("  k=" + str(k) + "  p=" + str(round(p,1)).rjust(5) + "    " +
              str(round(rm,3)) + "(" + str(len(rv)) + ")   " +
              str(round(nm,3)) + "(" + str(len(nv)) + ")    " +
              str(round(rm - nm, 3)))

cats = {}
for r in results:
    cats[r['category']] = cats.get(r['category'], 0) + 1
print("\n  Real categories:", cats)

out_data = dict(
    model=MODEL_NAME, method='autoregressive_dynamic', n_steps=N_STEPS,
    prompt=PROMPT, n_layers=int(n_layers),
    rung_ks=RUNG_KS, periods=[round(p, 3) for p in PERIODS],
    layer_norm_ts={str(L): [round(x, 4) for x in ts] for L, ts in layer_norm_ts.items()},
    results=[dict(r, period=round(r['period'],3),
                  ara=(None if r['ara'] is None else round(r['ara'],4))) for r in results],
    null_results=null_results,
    summary=dict(real=stats(real_aras), null=stats(null_aras)),
    category_counts=cats,
    elapsed_seconds=round(elapsed, 1),
    generated_text=gen[:500],
)
with open(OUT_PATH, 'w') as fh:
    fh.write("window.LLM_ARA_DYNAMIC = " + json.dumps(out_data, default=str) + ";\n")
print("\nSaved ->", OUT_PATH)

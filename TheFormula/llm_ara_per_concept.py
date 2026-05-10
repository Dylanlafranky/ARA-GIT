"""
llm_ara_per_concept.py

Does the LLM produce DIFFERENT ARA signatures for different kinds of content?

Method: feed Pythia-70M several distinct prompt types, generate text from each,
record per-step layer-norm activations, compute ARA per prompt × per rung.
Then see if the ARA signature (the curve over rungs) differs by content type.

If yes: ARA is a cognitive-mode classifier — the framework can tell what
KIND of thinking the model is doing.
If no: ARA captures something more universal (architecture/temperature) and
isn't sensitive to cognitive content.
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
OUT_PATH = '/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder/TheFormula/llm_ara_per_concept_data.js'
MODEL_NAME = 'EleutherAI/pythia-70m-deduped'
N_STEPS = 200
SEED = 42

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

# Distinct cognitive-content prompts
PROMPTS = [
    ('story',     "Once upon a time, in a small village by the sea, there lived a young girl who"),
    ('code',      "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) +"),
    ('math',      "The Pythagorean theorem states that for any right triangle, the square of"),
    ('emotion',   "When I lost someone close to me, the grief came in waves. Some days I felt"),
    ('factual',   "Photosynthesis is the process by which plants convert sunlight into"),
    ('dialogue',  "Alice: I've been thinking about what you said yesterday. Do you really believe"),
    ('poetry',    "Soft falls the rain on the autumn leaves, and the wind whispers through"),
    ('abstract',  "If a system is closed and self-organising, then by definition its dynamics must"),
]

print("[1/3] Loading", MODEL_NAME)
os.environ['HF_HOME'] = HF_CACHE
os.environ['TRANSFORMERS_OFFLINE'] = '1'
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=HF_CACHE)
model = GPTNeoXForCausalLM.from_pretrained(MODEL_NAME, cache_dir=HF_CACHE,
                                            output_hidden_states=True, output_attentions=False)
model.eval()
n_layers = model.config.num_hidden_layers

print("[2/3] Generating " + str(N_STEPS) + " steps for each of " + str(len(PROMPTS)) + " prompt types")
torch.manual_seed(SEED)

all_runs = {}
t_total = time.time()
for label, prompt in PROMPTS:
    inputs = tokenizer(prompt, return_tensors='pt')
    input_ids = inputs.input_ids
    prompt_len = input_ids.shape[1]
    layer_norm_ts = {L: [] for L in range(n_layers + 1)}
    past_kv = None
    cur = input_ids
    t0 = time.time()
    with torch.no_grad():
        for step in range(N_STEPS):
            out = model(cur, past_key_values=past_kv, use_cache=True,
                        output_hidden_states=True, output_attentions=False)
            past_kv = out.past_key_values
            for L in range(n_layers + 1):
                layer_norm_ts[L].append(float(torch.linalg.norm(out.hidden_states[L][0, -1]).item()))
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
    gen = tokenizer.decode(input_ids[0, prompt_len:])
    print("   " + label + ": " + str(round(elapsed,1)) + "s, gen[:80]=" + repr(gen[:80]))
    all_runs[label] = dict(prompt=prompt, layer_norm_ts=layer_norm_ts, generated=gen[:300])

print("[3/3] Computing per-prompt ARA signatures...")
RUNG_KS = [3, 4, 5, 6, 7, 8]
PERIODS = [PHI ** k for k in RUNG_KS]

results = {}
for label, run in all_runs.items():
    rung_aras = {k: [] for k in RUNG_KS}
    for L, ts in run['layer_norm_ts'].items():
        arr = np.array(ts)
        for k, p in zip(RUNG_KS, PERIODS):
            if 4 * p > len(arr): continue
            a = ara_full(arr, p)
            if a is not None:
                rung_aras[k].append(a)
    rung_means = {}
    for k in RUNG_KS:
        if rung_aras[k]:
            rung_means[k] = float(np.mean(rung_aras[k]))
        else:
            rung_means[k] = None
    overall = [a for k in rung_aras for a in rung_aras[k]]
    results[label] = dict(
        rung_means=rung_means,
        rung_aras={k: rung_aras[k] for k in RUNG_KS},
        overall_mean=float(np.mean(overall)) if overall else None,
        overall_std=float(np.std(overall)) if overall else None,
        n=len(overall),
    )

# Print summary table
print()
print("ARA SIGNATURE BY CONCEPT (mean across layers per rung):")
header = "{:<10} {:>8} {:>8}".format("prompt", "mean", "std")
for k in RUNG_KS:
    header += " {:>8}".format("k=" + str(k))
print(header)
for label in ['story','code','math','emotion','factual','dialogue','poetry','abstract']:
    if label not in results: continue
    r = results[label]
    line = "{:<10} {:>8} {:>8}".format(
        label,
        round(r['overall_mean'], 3) if r['overall_mean'] else "n/a",
        round(r['overall_std'], 3) if r['overall_std'] else "n/a",
    )
    for k in RUNG_KS:
        v = r['rung_means'].get(k)
        line += " {:>8}".format(round(v, 3) if v is not None else "-")
    print(line)

# Find peak rung per prompt
print()
print("Peak rung (max ARA) per prompt:")
for label, r in results.items():
    valid = {k: v for k, v in r['rung_means'].items() if v is not None}
    if valid:
        peak_k = max(valid, key=valid.get)
        print("   {:<10}  peak at k={}  (period~{:.1f})  ARA={:.3f}".format(
            label, peak_k, PHI**peak_k, valid[peak_k]))

# Save
out_data = dict(
    model=MODEL_NAME, n_steps=N_STEPS, seed=SEED,
    rung_ks=RUNG_KS, periods=[round(p, 3) for p in PERIODS],
    prompts={l: p for l, p in PROMPTS},
    results={l: dict(r, rung_aras={str(k): [round(a,4) for a in v] for k, v in r['rung_aras'].items()})
             for l, r in results.items()},
    generated_text={l: run['generated'] for l, run in all_runs.items()},
)
with open(OUT_PATH, 'w') as fh:
    fh.write("window.LLM_ARA_PER_CONCEPT = " + json.dumps(out_data, default=str) + ";\n")
print()
print("Saved ->", OUT_PATH)
print("Total time:", round(time.time() - t_total, 1), "s")

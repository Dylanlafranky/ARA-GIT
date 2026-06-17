"""
llm_closure_connARA_across_training.py  — RUN ON A GPU (Google Colab).

Extends llm_size_series.py to measure, for each (model size x training checkpoint):
  - closure_ratio        = closed Information^3 triangles per alive node  (trace(A^3)/6, |corr|>0.85)
  - loose_fraction       = alive nodes with <2 strong couplings  (loose threads = creativity / hallucination room)
  - connection_ARA       = where the model's coupling oscillations sit on the 0..2 ARA scale
                           (1 = symmetric clock, ->2 = slow-build/fast-release snap; phi=1.618 = engine)
  - per-rung ARA         = a few octave sub-rungs of the same node oscillations (Dylan: "the sub-rung, a few")
plus the existing structural metrics. Output = one tidy CSV row per (size, step).

NOTE (honest): connection_ARA here = node-activation-oscillation ARA, aggregated. This is ONE candidate
branch of "ARA of the connections" — it may not be the right one. Labelled exploratory.

Pairs with the capability curves already in pythia_curves/ALL_zeroshot_master.csv (same step grid),
so closure/ARA can be tested vs benchmark accuracy WITHIN a fixed size across training (size held constant).

COLAB SETUP:
  !pip -q install "transformers>=4.30" torch numpy
  # then run this file;  download llm_closure_connARA_RESULTS.csv when done.
"""
import os, time, csv, numpy as np, torch
from transformers import GPTNeoXForCausalLM, AutoTokenizer

# ---- scope: sizes your GPU can hold (T4: up to ~1.4B; A100: more). Trim as needed. ----
SIZES = [
    ("70m",   "EleutherAI/pythia-70m-deduped",    70),
    ("160m",  "EleutherAI/pythia-160m-deduped",  160),
    ("410m",  "EleutherAI/pythia-410m-deduped",  410),
    # ---- first run: keep ONLY the 3 sizes above. After it works, delete the leading "# " to add more: ----
    # ("1b",    "EleutherAI/pythia-1b-deduped",   1000),
    # ("1.4b",  "EleutherAI/pythia-1.4b-deduped", 1400),
    # ("2.8b",  "EleutherAI/pythia-2.8b-deduped", 2800),   # needs an A100 (Colab Pro)
]
# checkpoints — log-spaced, aligned to the capability-curve steps so the join is clean
STEPS = [0,1,2,8,64,512,1000,3000,13000,33000,63000,93000,143000]
PROMPT = "The framework proposes that natural oscillating systems"
N_STEPS = 200
SEED = 42
THRESH = 0.85
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
OUT = "llm_closure_connARA_RESULTS.csv"

def node_ara(series):
    """ARA of one node's activation oscillation over the run.
       convention (what_is_this.html): 1=symmetric, ->2 = slow-build/fast-release (snap), phi=engine.
       proxy = (time accumulating)/(time releasing) = #rising steps / #falling steps after endpoint-detrend."""
    x = series - np.linspace(series[0], series[-1], len(series))
    d = np.diff(x)
    rise = int((d > 0).sum()); fall = int((d < 0).sum())
    if fall == 0 or rise == 0: return np.nan
    return rise / fall

def octave_bands(series, n=3):
    """a few sub-rungs: causal trailing-MA cascade (telescoping); returns [fast..slow] bands."""
    bands=[]; cur=series.astype(float)
    for w in [4, 16, 64][:n]:
        c=np.cumsum(np.insert(cur,0,0)); s=np.array([(c[t+1]-c[max(0,t-w+1)])/(t+1-max(0,t-w+1)) for t in range(len(cur))])
        bands.append(cur - s); cur = s
    bands.append(cur)
    return bands

def run(label, path, params_m, step):
    rev = f"step{step}"
    tok = AutoTokenizer.from_pretrained(path, revision=rev)
    model = GPTNeoXForCausalLM.from_pretrained(path, revision=rev,
                output_hidden_states=True, output_attentions=True).to(DEVICE).eval()
    nL, nH = model.config.num_hidden_layers, model.config.num_attention_heads
    NODES = [("ln",L,None) for L in range(nL+1)] + [("head",L,H) for L in range(nL) for H in range(nH)]
    nN = len(NODES)
    torch.manual_seed(SEED)
    ids = tok(PROMPT, return_tensors="pt").input_ids.to(DEVICE)
    ts = np.zeros((nN, N_STEPS), np.float32)
    past=None; cur=ids; t0=time.time()
    with torch.no_grad():
        for stp in range(N_STEPS):
            out = model(cur, past_key_values=past, use_cache=True,
                        output_hidden_states=True, output_attentions=True)
            past = out.past_key_values; i=0
            for L in range(nL+1):
                ts[i,stp]=float(torch.linalg.norm(out.hidden_states[L][0,-1]).item()); i+=1
            for L in range(nL):
                A=out.attentions[L][0,:,-1,:]
                for H in range(nH): ts[i,stp]=float(A[H].max().item()); i+=1
            lg=out.logits[0,-1].float(); tv,ti=torch.topk(lg,40); tv=tv-tv.max()
            p=torch.softmax(tv,-1)
            nxt = ti[0:1] if (torch.isnan(p).any() or (p<0).any()) else ti[torch.multinomial(p,1)]
            cur=nxt.unsqueeze(0)
    # coupling graph
    stds=ts.std(1); alive=stds>1e-6; nA=int(alive.sum())
    z=(ts-ts.mean(1,keepdims=True))/(stds[:,None]+1e-9); z[~alive]=0
    C=np.clip(np.nan_to_num((z@z.T)/N_STEPS),-1,1); np.fill_diagonal(C,1.0)
    adj=(np.abs(C)>THRESH)&~np.eye(nN,dtype=bool); Ai=adj.astype(np.int32)
    n_tri=int(np.trace(Ai@Ai@Ai)//6)
    deg=adj.sum(1); n_under2=int(((deg<2)&alive).sum())
    closure=n_tri/max(nA,1); loose=n_under2/max(nA,1)
    # connection ARA (overall + per sub-rung), over alive nodes
    aras=[node_ara(ts[i]) for i in range(nN) if alive[i]]
    conn_ara=float(np.nanmedian(aras))
    rung_ara=[]
    for b in range(3):
        ra=[node_ara(octave_bands(ts[i])[b]) for i in range(nN) if alive[i]]
        rung_ara.append(float(np.nanmedian(ra)))
    el=round(time.time()-t0,1)
    del model
    if DEVICE=="cuda": torch.cuda.empty_cache()
    return dict(model=f"pythia-{label}-deduped", params_m=params_m, step=step,
                n_alive=nA, n_triangles=n_tri, closure_ratio=round(closure,4),
                loose_fraction=round(loose,4), connection_ARA=round(conn_ara,4),
                ARA_rung_fast=round(rung_ara[0],4), ARA_rung_mid=round(rung_ara[1],4),
                ARA_rung_slow=round(rung_ara[2],4), elapsed_s=el)

rows=[]
for label,path,pm in SIZES:
    for step in STEPS:
        try:
            r=run(label,path,pm,step); rows.append(r)
            print(f"{label:5} step{step:<6} closure {r['closure_ratio']:>8}  loose {r['loose_fraction']:.3f}  connARA {r['connection_ARA']:.3f}  ({r['elapsed_s']}s)")
        except Exception as e:
            print(f"{label} step{step} ERROR: {e}")
with open(OUT,"w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
print(f"\nSaved {len(rows)} rows -> {OUT}  (download it and drop into LLM/pythia_curves/)")

"""
llm_telephone_horizon.py  — RUN ON A GPU (Google Colab). Text-only, light.

v2 of the telephone game — fixes two things:
  (1) NO 12-turn cap: runs up to 100 turns to find the REAL coherence horizon (early-stops only when the
      chain hits a fixed point it repeats forever, or fully collapses — so it stays cheap).
  (2) DENSE lengths around each Fibonacci (phi-ladder) and each octave value + their neighbours, so we can
      test whether Fibonacci lengths are local PEAKS of coherence and octave/power-of-2 lengths are local
      DIPS (Dylan's observation in v1: 34(fib) held 0.79 but 32(oct) only 0.54; 55(fib) 0.56 vs 64(oct) 0.25).

Per (model,length,seed) we record: did it lock (fixed point), at what turn, the locked fidelity, and the
coherence horizon = #turns fidelity-vs-original stays >= 0.5 (capped at N_TURNS = "stable").
Test offline: is maintained-fidelity / horizon a local MAX at Fibonacci and local MIN at octave, vs neighbours.

COLAB:  !pip -q install "transformers==4.44.2"   then run; download llm_telephone_horizon_RESULTS.csv
"""
import torch, csv, random
from transformers import GPTNeoXForCausalLM, AutoTokenizer

SIZES   = [("70m",70),("410m",410),("1.4b",1400)]
FIB     = {5,8,13,21,34,55}
OCT     = {4,8,16,32,64}
# dense: each fib & oct value with +/-1 neighbours
LENGTHS = sorted({4,5,6, 7,8,9, 12,13,14, 15,16,17, 20,21,22, 31,32,33,34,35, 54,55,56, 63,64,65})
N_TURNS = 100
N_SEEDS = 10
DEVICE  = "cuda" if torch.cuda.is_available() else "cpu"
POOL    = list(range(100, 20000))

def gen_copy(model, s_ids, L, delim, eos):
    prompt = s_ids + [delim] + s_ids + [delim]
    ids = torch.tensor([prompt], device=DEVICE)
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=L, do_sample=False, pad_token_id=eos)
    gen = out[0, len(prompt):len(prompt)+L].tolist()
    return (gen + [delim]*L)[:L]

def fid(a,b):
    n=min(len(a),len(b)); return sum(1 for i in range(n) if a[i]==b[i])/max(n,1) if n else 0.0

rows=[]
for label,pm in SIZES:
    name=f"EleutherAI/pythia-{label}-deduped"
    tok=AutoTokenizer.from_pretrained(name)
    dt=torch.float16 if DEVICE=="cuda" else None
    model=GPTNeoXForCausalLM.from_pretrained(name,torch_dtype=dt).to(DEVICE).eval()
    delim=tok("\n").input_ids[-1]; eos=tok.eos_token_id or 0
    print(f"=== {label} ===")
    for L in LENGTHS:
        horizons=[]
        for seed in range(N_SEEDS):
            r=random.Random(1000*seed+L); orig=[r.choice(POOL) for _ in range(L)]; s=orig
            prev=None; locked=0; lock_turn=-1; lock_fid=None; horizon=0; t=0
            for t in range(1,N_TURNS+1):
                out=gen_copy(model,s,L,delim,eos)
                fo=fid(out,orig)
                if fo>=0.5: horizon=t
                if prev is not None and out==prev:          # fixed point -> stays forever
                    locked=1; lock_turn=t; lock_fid=round(fo,3)
                    if fo>=0.5: horizon=N_TURNS              # stable & coherent => effectively infinite
                    break
                if fid(out,s)==0.0 and t>2: break            # fully collapsed
                prev=out; s=out
            if lock_fid is None: lock_fid=round(fid(s,orig),3)
            horizons.append(horizon)
            rows.append([f"pythia-{label}-deduped",pm,L,1 if L in FIB else 0,1 if L in OCT else 0,
                         seed,t,locked,lock_turn,lock_fid,horizon])
        lab=("fib" if L in FIB else "")+("oct" if L in OCT else "")
        print(f"  L={L:3d} ({lab or 'nbr':>6})  median horizon {sorted(horizons)[len(horizons)//2]:>3}  mean lock-fid {sum(rr[9] for rr in rows[-N_SEEDS:])/N_SEEDS:.2f}")
    del model
    if DEVICE=="cuda": torch.cuda.empty_cache()

with open("llm_telephone_horizon_RESULTS.csv","w",newline="") as fh:
    w=csv.writer(fh)
    w.writerow(["model","params_m","length","is_fib","is_oct","seed","turns_run","locked","lock_turn","lock_fidelity","horizon_ge_0p5"])
    w.writerows(rows)
print(f"\nSaved {len(rows)} rows -> llm_telephone_horizon_RESULTS.csv")

"""
llm_telephone_chain.py  — RUN ON A GPU (Google Colab).  Text-only, light (no checkpoints, no activations).

Telephone game / transmission chain to test the phi-handover idea on information fidelity.
Each turn the model must COPY a token string from context (in-context recall = the induction-head circuit);
its output becomes the next turn's string. We measure how fidelity decays across turns.

Tests (Dylan): does a phi-handover give either (a) cleaner decay at 1/phi per turn, or (b) longer coherence
(turns-to-collapse) — and does it organise on the phi-ladder rather than the octave control?
  - string lengths on the FIBONACCI (integer phi) ladder: 2,3,5,8,13,21,34,55
  - control lengths on the OCTAVE ladder: 4,16,32,64   (2,8 shared)
  - per-turn retention -> test vs 1/phi=0.618 AND controls 1.0 / 0.25 / 1.75 / 2.0
  - turns-to-collapse vs length-rung / size -> test vs phi^(rung)
HONEST: small Pythia has weak induction; it may fail to copy at turn 1 (baseline). Random tokens = pure
copy test (content-free, what induction does). phi must BEAT the octave/linear ladders, not just appear.

COLAB:  !pip -q install "transformers==4.44.2"   then run; download llm_telephone_RESULTS.csv
"""
import torch, csv, random
from transformers import GPTNeoXForCausalLM, AutoTokenizer

SIZES   = [("70m",70),("410m",410),("1.4b",1400)]   # final models (1 download each); add more if you like
FIB     = [2,3,5,8,13,21,34,55]
OCT     = [4,16,32,64]
LENGTHS = sorted(set(FIB+OCT+[2,8]))
N_TURNS = 12
N_SEEDS = 6
DEVICE  = "cuda" if torch.cuda.is_available() else "cpu"
POOL    = list(range(100, 20000))   # safe mid-vocab token ids (content-free random strings)

def gen_copy(model, s_ids, L, delim, eos):
    # induction prime: "s DELIM s DELIM" -> a strong copier emits s again; take L generated tokens
    prompt = s_ids + [delim] + s_ids + [delim]
    ids = torch.tensor([prompt], device=DEVICE)
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=L, do_sample=False, pad_token_id=eos)
    gen = out[0, len(prompt):len(prompt)+L].tolist()
    return (gen + [delim]*L)[:L]

def fidelity(a, b):
    n=min(len(a),len(b)); 
    return sum(1 for i in range(n) if a[i]==b[i])/max(n,1) if n else 0.0

rows=[]
for label,pm in SIZES:
    name=f"EleutherAI/pythia-{label}-deduped"
    tok=AutoTokenizer.from_pretrained(name)
    dt = torch.float16 if DEVICE=="cuda" else None
    model=GPTNeoXForCausalLM.from_pretrained(name, torch_dtype=dt).to(DEVICE).eval()
    delim=tok("\n").input_ids[-1]; eos=tok.eos_token_id or 0
    print(f"=== {label} loaded ===")
    for L in LENGTHS:
        ladder=("fib" if L in FIB else "")+("|oct" if L in OCT else "")
        t1=[]
        for seed in range(N_SEEDS):
            r=random.Random(1000*seed+L)
            orig=[r.choice(POOL) for _ in range(L)]; s=orig
            for turn in range(1,N_TURNS+1):
                out=gen_copy(model,s,L,delim,eos)
                f_in=fidelity(out,s); f_orig=fidelity(out,orig)
                if turn==1: t1.append(f_in)
                rows.append([f"pythia-{label}-deduped",pm,L,ladder.strip("|"),seed,turn,round(f_in,3),round(f_orig,3)])
                s=out
                if f_in==0.0 and turn>2: break
        print(f"  L={L:3d} ({ladder.strip('|') or 'lin':>7})  turn-1 copy fidelity mean {sum(t1)/len(t1):.2f}")
    del model
    if DEVICE=="cuda": torch.cuda.empty_cache()

with open("llm_telephone_RESULTS.csv","w",newline="") as fh:
    w=csv.writer(fh)
    w.writerow(["model","params_m","length","ladder","seed","turn","fidelity_vs_input","fidelity_vs_original"])
    w.writerows(rows)
print(f"\nSaved {len(rows)} rows -> llm_telephone_RESULTS.csv  (download it; drop into LLM/pythia_curves/)")

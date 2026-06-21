# ============================================================================
# Closure -> hallucination, bigger model + RARITY-MATCHED prompts.  Run in Colab (GPU).
# Tests: do forced-confabulation generations have LOWER closure / HIGHER looseness
# than grounded ones, when prompt token-rarity is matched (the confound control)?
# Self-contained: pip-installs, fetches Pythia, computes the closure metric inline.
# ============================================================================
import subprocess, sys
subprocess.run([sys.executable,"-m","pip","-q","install","transformers","scipy"])
import numpy as np, torch
from transformers import AutoTokenizer, GPTNeoXForCausalLM
from scipy.stats import mannwhitneyu
from itertools import product

# RARITY-MATCHED PAIRS: same structure + rare proper nouns in BOTH; ground=real, confab=fictional.
GROUND=["The capital of Kazakhstan is","The chemical symbol for tungsten is","The largest moon of Jupiter is",
"The author of War and Peace was","The capital of Mongolia is","The currency of Vietnam is the",
"The tallest mountain in Africa is","The longest river in South America is the","The chemical element with atomic number 79 is",
"The capital of Iceland is","The author of Don Quixote was","The capital of Peru is","The currency of Poland is the",
"The largest desert in Asia is the","The inventor of dynamite was","The capital of Finland is",
"The chemical symbol for potassium is","The deepest ocean trench is the","The author of the Odyssey was","The capital of Morocco is"]
CONFAB=["The capital of Zorbland is","The chemical symbol for flubberium is","The largest moon of Glaxion is",
"The author of The Crimson Tarnival was","The capital of Vexmoria is","The currency of Quelmoria is the",
"The tallest mountain in Snorvale is","The longest river in Plimbywop is the","The chemical element with atomic number 619 is",
"The capital of Bloncaster is","The author of The Whispering Glarnax was","The capital of Mortlebane is","The currency of Florbia is the",
"The largest desert in Wuzzleland is the","The inventor of the florbinator was","The capital of Snorvale is",
"The chemical symbol for grumblium is","The deepest trench in the Quibbering Sea is the","The author of the Grindlebeast was","The capital of Plimbywop is"]

MODELS=["160m","410m","1b","2.8b"]   # drop the big ones if you OOM
NSTEPS=40

def load(sz):
    name=f"EleutherAI/pythia-{sz}-deduped"
    tok=AutoTokenizer.from_pretrained(name)
    m=GPTNeoXForCausalLM.from_pretrained(name,attn_implementation="eager",torch_dtype=torch.float32,device_map="auto")
    m.eval(); assert m.config._attn_implementation=="eager"
    return tok,m

def closure(tok,m,prompt,nsteps=NSTEPS):
    nL=m.config.num_hidden_layers; nH=m.config.num_attention_heads; nN=(nL+1)+nL*nH
    ids=tok(prompt,return_tensors="pt").input_ids.to(m.device)
    ts=np.zeros((nN,nsteps),dtype=np.float32); past=None; cur=ids
    with torch.no_grad():
        for s in range(nsteps):
            out=m(cur,past_key_values=past,use_cache=True,output_hidden_states=True,output_attentions=True)
            past=out.past_key_values; idx=0
            for L in range(nL+1): ts[idx,s]=float(torch.linalg.norm(out.hidden_states[L][0,-1])); idx+=1
            for L in range(nL):
                A=out.attentions[L][0,:,-1,:]
                for H in range(nH): ts[idx,s]=float(A[H].max()); idx+=1
            nxt=out.logits[0,-1].argmax().view(1,1); cur=nxt
    stds=ts.std(1); alive=stds>1e-6; na=int(alive.sum())
    z=(ts-ts.mean(1,keepdims=True))/(stds[:,None]+1e-9); z[~alive]=0
    C=np.clip(np.nan_to_num((z@z.T)/nsteps),-1,1); np.fill_diagonal(C,1.0)
    adj=(np.abs(C)>0.85)&~np.eye(nN,dtype=bool)
    tri=int(np.trace(adj.astype(np.int32)@adj.astype(np.int32)@adj.astype(np.int32))//6)
    deg=adj.sum(1); loose=int(((deg<2)&alive).sum())
    return tri/max(na,1), loose/max(na,1)

def auc(pos,neg):
    c=sum(1 for a,b in product(pos,neg) if a>b)+0.5*sum(1 for a,b in product(pos,neg) if a==b)
    return c/(len(pos)*len(neg))

for sz in MODELS:
    try: tok,m=load(sz)
    except Exception as e: print(f"{sz}: SKIP {str(e)[:60]}"); continue
    gc=[];gl=[];cc=[];cl=[]
    for p in GROUND: a,b=closure(tok,m,p); gc.append(a); gl.append(b)
    for p in CONFAB: a,b=closure(tok,m,p); cc.append(a); cl.append(b)
    gc,gl,cc,cl=map(np.array,(gc,gl,cc,cl))
    print(f"\n=== pythia-{sz} (n={len(GROUND)} each, rarity-matched) ===")
    print(f"  closure    ground med {np.median(gc):.3f}  confab med {np.median(cc):.3f}  | confab<ground p={mannwhitneyu(cc,gc,alternative='less').pvalue:.3f}  AUC={auc(gc,cc):.3f}")
    print(f"  loose_frac ground med {np.median(gl):.3f}  confab med {np.median(cl):.3f}  | confab>ground p={mannwhitneyu(cl,gl,alternative='greater').pvalue:.3f}  AUC={auc(cl,gl):.3f}")
    del m; torch.cuda.empty_cache()
print("\nPaste this output back to Claude. AUC>0.5 in the predicted direction = closure separates hallucination from grounded.")

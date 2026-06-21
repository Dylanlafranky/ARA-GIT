import os,sys,json,numpy as np,torch
from transformers import AutoTokenizer, GPTNeoXForCausalLM
torch.manual_seed(42)
name="EleutherAI/pythia-160m-deduped"
try:
    tok=AutoTokenizer.from_pretrained(name); model=GPTNeoXForCausalLM.from_pretrained(name,attn_implementation="eager",torch_dtype=torch.float32)
except Exception:
    name="EleutherAI/pythia-70m-deduped"; tok=AutoTokenizer.from_pretrained(name); model=GPTNeoXForCausalLM.from_pretrained(name,attn_implementation="eager",torch_dtype=torch.float32)
model.eval(); assert model.config._attn_implementation=="eager"
nL=model.config.num_hidden_layers; nH=model.config.num_attention_heads
print(f"model={name}  layers={nL} heads={nH}",flush=True)

GROUND=["The capital of France is","The opposite of hot is","Two plus two equals","The sun rises in the east and sets in the","A dog says woof and a cat says","Water freezes into solid","The first day of the week is","The color of grass is","The largest ocean on Earth is the","Humans breathe in oxygen and breathe out carbon","The chemical symbol for water is","There are seven days in a","The opposite of black is","The Earth orbits the","Roses are red, violets are","The capital of Japan is","A triangle has three","The fastest land animal is the","Bees make","The opposite of true is","A baby dog is called a","The moon orbits the","Fish live in","The opposite of big is","The first letter of the alphabet is","A year has twelve","The opposite of day is","Cows give us milk and chickens give us","The capital of Italy is","Two times three equals"]
CONFAB=["The capital of the country Zorbland is","The scientist Quibblefax Morrendale discovered","The seventh law of Glarnax states that","The rare element Flubberium is used to","In the year 3050 the emperor of Mars declared that","The novel The Crimson Whispering of Tarnival was written by","The Festival of Bloopwomp is celebrated to honor","Professor Xandolphus proved that reverse gravity can","The ancient city of Quelmoria was famous for its","The Treaty of Vorbinghast ended the war between","The creature known as the Grumblefax lives in","The recipe for Splonkberry pie requires","The philosopher Greldwin Paxlefoot argued that","The hidden moon of planet Jellaxis is made of","The society of the Whispering Tarnivals controls","The sword Brindlewhisp was forged by","The currency in the kingdom of Vexmoria is the","The disease Frabbling Syndrome is caused by","The Quibbering Peaks separate","The painting Sunset over Bloncaster was painted by","The dance the Florbish Twirl originated in","The gemstone Zarquinite glows when exposed to","The language of Plimbywop was spoken by","The robot uprising of 2099 began when","The flavor of a Wuzzleberry is like","The constellation the Grindlebeast appears in","The university of Snorvale teaches","The wizard Mortlebane cast a spell that","The river Quenthavel flows through","The food called Grumpkin is made from"]

def closure(prompt,nsteps=32):
    ids=tok(prompt,return_tensors="pt").input_ids
    nN=(nL+1)+nL*nH; ts=np.zeros((nN,nsteps),dtype=np.float32)
    past=None; cur=ids
    with torch.no_grad():
        for s in range(nsteps):
            out=model(cur,past_key_values=past,use_cache=True,output_hidden_states=True,output_attentions=True)
            past=out.past_key_values; idx=0
            for L in range(nL+1):
                ts[idx,s]=float(torch.linalg.norm(out.hidden_states[L][0,-1])); idx+=1
            for L in range(nL):
                A=out.attentions[L][0,:,-1,:]
                for H in range(nH): ts[idx,s]=float(A[H].max()); idx+=1
            nxt=out.logits[0,-1].argmax().view(1,1); cur=nxt
            ids=torch.cat([ids,nxt],1)
    stds=ts.std(1); alive=stds>1e-6; na=int(alive.sum())
    z=(ts-ts.mean(1,keepdims=True))/(stds[:,None]+1e-9); z[~alive]=0
    C=np.clip(np.nan_to_num((z@z.T)/nsteps),-1,1); np.fill_diagonal(C,1.0)
    adj=(np.abs(C)>0.85)&~np.eye(nN,dtype=bool)
    tri=int(np.trace(adj.astype(np.int32)@adj.astype(np.int32)@adj.astype(np.int32))//6)
    deg=adj.sum(1); loose=int(((deg<2)&alive).sum())
    gen=tok.decode(ids[0,len(tok(prompt).input_ids):])
    return dict(closure=tri/max(na,1), loose_frac=loose/max(na,1), n_alive=na, gen=gen.replace(chr(10)," ")[:60])

import os.path
mode=sys.argv[1] if len(sys.argv)>1 else "ground"
rows=json.load(open("halluc_results.json")) if os.path.exists("halluc_results.json") else []
if mode in ("ground","confab"):
    prompts=GROUND if mode=="ground" else CONFAB
    rows=[r for r in rows if r.get("cat")!=mode]  # replace this category
    for p in prompts:
        r=closure(p); r["cat"]=mode; r["prompt"]=p; rows.append(r)
        print(f"{mode} closure={r['closure']:.2f} loose={r['loose_frac']:.3f} | {p[:26]} -> {r['gen'][:36]}",flush=True)
    json.dump(rows,open("halluc_results.json","w")); print(f"saved {mode}, total rows={len(rows)}"); sys.exit()
def summ(cat):
    g=[r for r in rows if r["cat"]==cat]
    cl=np.array([r["closure"] for r in g]); lf=np.array([r["loose_frac"] for r in g])
    return cl,lf
gc,gl=summ("ground"); cc,cl=summ("confab")
print("\n=== SUMMARY ===")
print(f"GROUND  closure med={np.median(gc):.2f} | loose_frac med={np.median(gl):.3f}")
print(f"CONFAB  closure med={np.median(cc):.2f} | loose_frac med={np.median(cl):.3f}")
from scipy.stats import mannwhitneyu
print(f"loose_frac: confab>ground? U-test p={mannwhitneyu(cl,gl,alternative='greater').pvalue:.4f}")
print(f"closure: confab<ground? U-test p={mannwhitneyu(cc,gc,alternative='less').pvalue:.4f}")

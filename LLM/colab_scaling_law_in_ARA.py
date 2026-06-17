# ============================================================================
# Neural scaling law IN ARA  (Test B) — their measurement, our framework.
# Run in Colab.  FIRST: upload ara_mapper.py (from GIT/ARA-GIT) to the session
# (Files panel -> upload), so this uses the CANONICAL ARA method, not a re-impl.
# GPU runtime; A100 if you want 6.9B/12B. Smaller sizes run on a T4.
# ============================================================================
import subprocess, sys
subprocess.run([sys.executable,"-m","pip","-q","install","transformers","scipy"])
import numpy as np, torch, gc
from transformers import AutoTokenizer, GPTNeoXForCausalLM
import ara_mapper   # <-- the uploaded canonical tool

# One fixed held-out passage (continuous natural prose, public domain: Austen P&P ch.1).
TEXT = (
"It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife. "
"However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well "
"fixed in the minds of the surrounding families, that he is considered as the rightful property of some one or other of their daughters. "
"My dear Mr. Bennet, said his lady to him one day, have you heard that Netherfield Park is let at last? Mr. Bennet replied that he had not. "
"But it is, returned she; for Mrs. Long has just been here, and she told me all about it. Mr. Bennet made no answer. "
"Do you not want to know who has taken it? cried his wife impatiently. You want to tell me, and I have no objection to hearing it. "
"This was invitation enough. Why, my dear, you must know, Mrs. Long says that Netherfield is taken by a young man of large fortune "
"from the north of England; that he came down on Monday in a chaise and four to see the place, and was so much delighted with it that "
"he agreed with Mr. Morris immediately; that he is to take possession before Michaelmas, and some of his servants are to be in the house "
"by the end of next week. What is his name? Bingley. Is he married or single? Oh! single, my dear, to be sure! A single man of large "
"fortune; four or five thousand a year. What a fine thing for our girls! How so? how can it affect them? My dear Mr. Bennet, replied his "
"wife, how can you be so tiresome! You must know that I am thinking of his marrying one of them. Is that his design in settling here? "
"Design! nonsense, how can you talk so! But it is very likely that he may fall in love with one of them, and therefore you must visit him "
"as soon as he comes. I see no occasion for that. You and the girls may go, or you may send them by themselves, which perhaps will be still "
"better; for as you are as handsome as any of them, Mr. Bingley might like you the best of the party. My dear, you flatter me. I certainly "
"have had my share of beauty, but I do not pretend to be anything extraordinary now. When a woman has five grown-up daughters, she ought to "
"give over thinking of her own beauty. In such cases, a woman has not often much beauty to think of. But, my dear, you must indeed go and see "
"Mr. Bingley when he comes into the neighbourhood. It is more than I engage for, I assure you. But consider your daughters. Only think what an "
"establishment it would be for one of them. Sir William and Lady Lucas are determined to go, merely on that account; for in general, you know, "
"they visit no newcomers. Indeed you must go, for it will be impossible for us to visit him, if you do not."
)
SIZES=[("70m",70),("160m",160),("410m",410),("1b",1000),("1.4b",1400),("2.8b",2800),("6.9b",6900),("12b",12000)]

def per_token_nats(name):
    tok=AutoTokenizer.from_pretrained(name)
    model=GPTNeoXForCausalLM.from_pretrained(name,torch_dtype=torch.float16,device_map="auto"); model.eval()
    ids=tok(TEXT,return_tensors="pt").input_ids.to(model.device)
    with torch.no_grad(): logits=model(ids).logits[0].float()
    logp=torch.log_softmax(logits,dim=-1); tgt=ids[0,1:].to(logp.device)
    nats=(-logp[:-1].gather(1,tgt.unsqueeze(1)).squeeze(1)).cpu().numpy()
    del model,logits,logp; gc.collect(); torch.cuda.empty_cache()
    return nats

print(f"{'size':7}{'params':>8}{'mean_nats(=loss)':>17}{'ppl':>9}{'wave_ARA':>10}{'domP':>8}")
rows=[]
for s,p in SIZES:
    try:
        nats=per_token_nats(f"EleutherAI/pythia-{s}-deduped")
        np.save(f"nats_{s}.npy",nats)
        mp=ara_mapper.map_system(nats)
        ara=mp.get('system_mean_ara'); domP=mp.get('dominant_period_samples'); mn=float(nats.mean())
        rows.append((s,p,mn,float(np.exp(mn)),ara,domP))
        print(f"{s:7}{p:>8}{mn:>17.3f}{np.exp(mn):>9.1f}{ara:>10.3f}{domP:>8.1f}")
        for r in mp.get('rung_breakdown',[]):
            if r['valid'] and r['ara'] is not None:
                print(f"      k={r['k']:+d} P={r['period_samples']:.0f} amp={r['amp']:.2f} ara={r['ara']:.3f} {r['classification']}")
    except Exception as e:
        print(f"{s:7}  SKIP: {str(e)[:70]}")

print("\n=== SUMMARY: loss-vs-scale (THEIR law)  vs  wave-ARA-vs-scale (OURS) ===")
print(f"{'size':7}{'mean_nats':>11}{'wave_ARA':>10}")
for s,p,mn,ppl,ara,dP in rows: print(f"{s:7}{mn:>11.3f}{ara:>10.3f}")
print("\nPaste this whole output back to Claude. Save the nats_*.npy too if you want the raw waves.")

import sys, os, json, numpy as np, torch
from transformers import AutoTokenizer, GPTNeoXForCausalLM
sys.path.insert(0, "/sessions/exciting-peaceful-archimedes/mnt/SystemFormulaFolder/GIT/ARA-GIT")
import ara_mapper

TEXT = (
"It is a truth universally acknowledged, that a single man in possession of a good fortune, "
"must be in want of a wife. However little known the feelings or views of such a man may be on "
"his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding "
"families, that he is considered the rightful property of some one or other of their daughters. "
"\"My dear Mr. Bennet,\" said his lady to him one day, \"have you heard that Netherfield Park is "
"let at last?\" Mr. Bennet replied that he had not. \"But it is,\" returned she; \"for Mrs. Long "
"has just been here, and she told me all about it.\" Mr. Bennet made no answer. \"Do you not want "
"to know who has taken it?\" cried his wife impatiently. \"You want to tell me, and I have no "
"objection to hearing it.\" This was invitation enough. \"Why, my dear, you must know, Mrs. Long "
"says that Netherfield is taken by a young man of large fortune from the north of England; that "
"he came down on Monday in a chaise and four to see the place, and was so much delighted with it "
"that he agreed with Mr. Morris immediately; that he is to take possession before Michaelmas, and "
"some of his servants are to be in the house by the end of next week.\" \"What is his name?\" "
"\"Bingley.\" \"Is he married or single?\" \"Oh! single, my dear, to be sure! A single man of "
"large fortune; four or five thousand a year. What a fine thing for our girls!\" \"How so? how can "
"it affect them?\" \"My dear Mr. Bennet,\" replied his wife, \"how can you be so tiresome! You must "
"know that I am thinking of his marrying one of them.\" \"Is that his design in settling here?\" "
"\"Design! nonsense, how can you talk so! But it is very likely that he may fall in love with one "
"of them, and therefore you must visit him as soon as he comes.\" "
)

MODELS=[("70m",),("160m",),("410m",)]
only=os.environ.get("ONLY_MODELS")
if only: MODELS=[(m,) for m in only.split(",")]

def per_token_bits(ms):
    name=f"EleutherAI/pythia-{ms}-deduped"
    tok=AutoTokenizer.from_pretrained(name)
    model=GPTNeoXForCausalLM.from_pretrained(name); model.eval()
    ids=tok(TEXT, return_tensors="pt").input_ids
    with torch.no_grad():
        logits=model(ids).logits[0]
    logp=torch.log_softmax(logits.float(), dim=-1)
    tgt=ids[0,1:]
    bits=(-logp[:-1].gather(1,tgt.unsqueeze(1)).squeeze(1))/np.log(2)
    return bits.numpy()

print("=== NEURAL SCALING LAW as a BASE WAVE — per-token bits, measured canonically ===")
print(f"{'model':6}{'meanbits(=loss)':>16}{'ppl':>9}{'n_tok':>7}{'wave ARA':>11}{'raw-peak':>10}{'domP':>7}")
for (ms,) in MODELS:
    bits=per_token_bits(ms)
    mp=ara_mapper.map_system(bits)
    ara=mp.get("system_mean_ara"); domP=mp.get("dominant_period_samples")
    try: rawp=ara_mapper.measure_rung_ara_raw_peak(bits, domP if domP else 8)
    except Exception: rawp=None
    ara=ara if ara is not None else float('nan'); rawp=rawp if rawp is not None else float('nan')
    mb=float(bits.mean())
    np.save(f"bits_{ms}.npy", bits)
    print(f"{ms:6}{mb:>16.3f}{2**mb:>9.1f}{len(bits):>7}{ara:>11.3f}{rawp:>10.3f}{str(domP):>7}")

print("\n--> loss (meanbits) is the MEAN of this wave; the scaling law is that mean's trend vs compute.")
print("--> the BASE WAVE's ARA = the neural scaling law's ARA, measured from what they measured.")
last=MODELS[-1][0]
mp=ara_mapper.map_system(np.load(f"bits_{last}.npy"))
print(f"\nper-rung ARA ({last}):")
for r in mp.get("rung_breakdown",[]):
    if r.get("valid") and r.get("ara") is not None:
        star=" <-- dominant" if r.get("amp")==max(x['amp'] for x in mp['rung_breakdown'] if x.get('valid') and x.get('amp')) else ""
        print(f"  k={r['k']:+d} P={r['period_samples']:.0f} amp={r['amp']:.3f} ara={r['ara']:.3f} {r['classification']}{star}")

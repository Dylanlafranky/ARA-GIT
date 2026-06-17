import sys, numpy as np, torch
from transformers import AutoTokenizer, GPTNeoXForCausalLM
sys.path.insert(0,"/sessions/exciting-peaceful-archimedes/mnt/SystemFormulaFolder/GIT/ARA-GIT")
import ara_mapper

TEXTS={
"austen_narrative":(
"It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife. "
"However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so "
"well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of "
"their daughters. My dear Mr Bennet, said his lady to him one day, have you heard that Netherfield Park is let at last? "
"Mr Bennet replied that he had not. But it is, returned she; for Mrs Long has just been here, and she told me all about it. "
"Mr Bennet made no answer. Do you not want to know who has taken it? cried his wife impatiently. You want to tell me, and I "
"have no objection to hearing it. This was invitation enough. Why, my dear, you must know, Mrs Long says that Netherfield is "
"taken by a young man of large fortune from the north of England; that he came down on Monday in a chaise and four to see the "
"place, and was so much delighted with it that he agreed with Mr Morris immediately, and is to take possession before Michaelmas."),
"usconst_legal":(
"We the People of the United States, in Order to form a more perfect Union, establish Justice, insure domestic Tranquility, "
"provide for the common defence, promote the general Welfare, and secure the Blessings of Liberty to ourselves and our Posterity, "
"do ordain and establish this Constitution for the United States of America. All legislative Powers herein granted shall be "
"vested in a Congress of the United States, which shall consist of a Senate and House of Representatives. The House of "
"Representatives shall be composed of Members chosen every second Year by the People of the several States, and the Electors in "
"each State shall have the Qualifications requisite for Electors of the most numerous Branch of the State Legislature. No Person "
"shall be a Representative who shall not have attained to the Age of twenty five Years, and been seven Years a Citizen of the "
"United States, and who shall not, when elected, be an Inhabitant of that State in which he shall be chosen."),
"science_expository":(
"The cell is the basic structural and functional unit of all known living organisms. Cells consist of cytoplasm enclosed within "
"a membrane, which contains many biomolecules such as proteins and nucleic acids. Most plant and animal cells are visible only "
"under a microscope, with dimensions between one and one hundred micrometres. Organisms can be classified as unicellular, "
"consisting of a single cell, or multicellular, including plants and animals. The number of cells in plants and animals varies "
"from species to species. The human body contains more than thirty trillion cells. Most plant and animal cells are eukaryotic, "
"meaning they contain a membrane bound nucleus, whereas bacteria and archaea have simpler prokaryotic cells without a nucleus. "
"Energy flows through cells via metabolism, the set of chemical reactions that sustain life, releasing and storing energy in "
"chemical bonds as the organism grows, responds to its environment, and reproduces over successive generations."),
}
ms="70m"; name=f"EleutherAI/pythia-{ms}-deduped"
tok=AutoTokenizer.from_pretrained(name); model=GPTNeoXForCausalLM.from_pretrained(name); model.eval()
def bits_of(t):
    ids=tok(t,return_tensors="pt").input_ids
    with torch.no_grad(): lg=model(ids).logits[0]
    lp=torch.log_softmax(lg.float(),-1); tgt=ids[0,1:]
    return (-lp[:-1].gather(1,tgt.unsqueeze(1)).squeeze(1)).numpy()/np.log(2)

print(f"=== base-wave ARA stability across genres (pythia-70m) ===")
print(f"{'text':22}{'n':>5}{'meanbits':>10}{'waveARA':>9}{'rawpeak':>9}{'domP':>7}")
aras=[]
for k,t in TEXTS.items():
    b=bits_of(t); mp=ara_mapper.map_system(b)
    a=mp.get("system_mean_ara"); dP=mp.get("dominant_period_samples")
    try: rp=ara_mapper.measure_rung_ara_raw_peak(b,dP if dP else 8)
    except: rp=float('nan')
    a=a if a is not None else float('nan'); rp=rp if rp is not None else float('nan')
    aras.append(a)
    print(f"{k:22}{len(b):>5}{b.mean():>10.3f}{a:>9.3f}{rp:>9.3f}{dP:>7.1f}")
print(f"\nmean wave-ARA across genres = {np.nanmean(aras):.3f}  (sd {np.nanstd(aras):.3f})")
print("clock=1.0  golden=1.618  -> engine-leaning band")

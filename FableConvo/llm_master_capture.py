"""
llm_master_capture.py — CAPTURE ONCE, TEST FOREVER (registered 3 Jul 2026)
============================================================================
One resumable Colab job that harvests everything the whole LLM test queue
needs (T-LLM-1..5 and the info-wave analyses), shard-saved to Google Drive.
After this completes, NO test ever needs a GPU again.
S2 NOTE (LLM_WORK_SAFEGUARDS.md): second-family review before first run.
Method lineage: node layout, eager guard, prompt, top-40 sampling identical
to llm_whole_run_octave_sweep.py so old numbers stay comparable.

PHASES (each shard ~ MB, saved the moment it completes; re-run = resume):
 A  FINAL-CHECKPOINT SUITE - sizes 70m/160m/410m x modes {free,greedy,forced}
    x 3 prompts x 3 seeds, 400 gen steps. Serves: T-LLM-1 (single-mode with
    real statistics), T-LLM-2 (free-vs-forced - THE phi-jurisdiction ask;
    forced = teacher-forced periodic token drive with KNOWN period, so lock
    detection has exact ground truth), T-LLM-3 (across sizes), info wave
    (per-step chosen-token logprob + entropy saved for every run).
 B  TRAINING LADDER - 410m x 19 checkpoints x {free,forced} x canonical
    prompt/seed. Serves: T-LLM-4 (formation wave: collapse-rebuild measured
    with motion instruments; forced-drive control at every checkpoint).
 C  WEIGHT SPECTRA (free during B!) - while each checkpoint is in memory,
    full singular-value spectra of every weight matrix are saved. Serves:
    T-LLM-5 (the cooling curve / glass memory) with ZERO extra downloads.
RUNTIME (rough, T4 Colab): A ~ 1-2 h; B dominated by 19 model-revision
downloads ~ 2-4 h. Resumable across any number of sessions.
"""
import os, time, csv, glob, numpy as np, torch
from transformers import GPTNeoXForCausalLM, AutoTokenizer

MERGE   = False
PHASES  = ("A", "B")          # edit to run a subset, e.g. ("A",)
SIZES_A = [("70m","EleutherAI/pythia-70m-deduped"), ("160m","EleutherAI/pythia-160m-deduped"),
           ("410m","EleutherAI/pythia-410m-deduped")]
LADDER  = [1,2,4,8,16,32,64,128,256,512,1000,2000,4000,8000,16000,32000,64000,128000,143000]
PROMPTS = ["The framework proposes that natural oscillating systems",      # canonical (lineage)
           "Yesterday the harbour was quiet until the tide turned and",
           "The recipe requires patience: first the dough must"]
SEEDS   = [42, 137, 618]
N_GEN   = 400
FORCED_PATTERN = " red blue green yellow purple"   # tokenized cycle = known drive period
DEVICE  = "cuda" if torch.cuda.is_available() else "cpu"

SAVE_DIR = "master_capture_shards"
try:
    from google.colab import drive
    drive.mount("/content/drive")
    SAVE_DIR = "/content/drive/MyDrive/ARA_master_capture"
except ImportError:
    pass
os.makedirs(SAVE_DIR, exist_ok=True)

def load(path, step=None):
    kw = dict(attn_implementation="eager", output_hidden_states=True, output_attentions=True)
    if step is not None: kw["revision"] = f"step{step}"
    tok = AutoTokenizer.from_pretrained(path, revision=kw.get("revision"))
    m = GPTNeoXForCausalLM.from_pretrained(path, **kw).to(DEVICE).eval()
    assert m.config._attn_implementation == "eager"
    return tok, m

def capture(tok, model, mode, prompt, seed, n_gen=N_GEN):
    nL, nH = model.config.num_hidden_layers, model.config.num_attention_heads
    nN = (nL + 1) + nL * nH
    torch.manual_seed(seed)
    ts = np.zeros((nN, n_gen), np.float32)
    bits = np.zeros((2, n_gen), np.float32)          # [chosen -logp, entropy(top40)]
    if mode == "forced":
        drive_ids = tok(FORCED_PATTERN, return_tensors="pt").input_ids[0]
        seq = drive_ids.repeat((n_gen // len(drive_ids)) + 2)
        period = len(drive_ids)
    ids = tok(prompt, return_tensors="pt").input_ids.to(DEVICE)
    past, cur = None, ids
    with torch.no_grad():
        for stp in range(n_gen):
            out = model(cur, past_key_values=past, use_cache=True,
                        output_hidden_states=True, output_attentions=True)
            past = out.past_key_values; i = 0
            for L in range(nL + 1):
                ts[i, stp] = float(torch.linalg.norm(out.hidden_states[L][0, -1])); i += 1
            for L in range(nL):
                A = out.attentions[L][0, :, -1, :]
                for H in range(nH):
                    ts[i, stp] = float(A[H].max()); i += 1
            lg = out.logits[0, -1].float()
            tv, ti = torch.topk(lg, 40); tvs = tv - tv.max()
            p = torch.softmax(tvs, -1)
            bits[1, stp] = float(-(p * torch.log2(p + 1e-12)).sum())
            if mode == "forced":
                nxt = seq[stp:stp+1].to(DEVICE)
            elif mode == "greedy":
                nxt = ti[0:1]
            else:
                nxt = ti[0:1] if (torch.isnan(p).any() or (p < 0).any()) else ti[torch.multinomial(p, 1)]
            full = torch.log_softmax(lg, -1)
            bits[0, stp] = float(-full[nxt[0]].item()) / 0.6931471805599453  # -log2 p(chosen)
            cur = nxt.unsqueeze(0)
    meta = dict(nL=nL, nH=nH, mode=mode, seed=seed,
                drive_period=(period if mode == "forced" else 0))
    return ts, bits, meta

def weight_spectra(model):
    out = {}
    for name, p in model.named_parameters():
        if p.ndim == 2 and min(p.shape) >= 64:
            sv = torch.linalg.svdvals(p.detach().float()).cpu().numpy().astype(np.float32)
            out[name.replace(".", "__")] = sv
    return out

def done(tag): return os.path.exists(os.path.join(SAVE_DIR, tag + ".npz"))
def save(tag, **arrs):
    np.savez_compressed(os.path.join(SAVE_DIR, tag + ".npz"), **arrs)
    print("saved", tag, flush=True)

if MERGE:
    files = sorted(glob.glob(os.path.join(SAVE_DIR, "*.npz")))
    print(f"{len(files)} shards present; keep as shard library (analyses load "
          "shards directly - no monolithic merge needed; commit the folder).")
    raise SystemExit

if "A" in PHASES:
    for label, path in SIZES_A:
        tok = model = None
        for pi, prompt in enumerate(PROMPTS):
            for seed in SEEDS:
                for mode in ("free", "greedy", "forced"):
                    tag = f"A_{label}_p{pi}_s{seed}_{mode}"
                    if done(tag): print("skip", tag); continue
                    if model is None: tok, model = load(path)
                    ts, bits, meta = capture(tok, model, mode, prompt, seed)
                    save(tag, ts=ts, bits=bits, **{k: np.array(v) for k, v in meta.items()})
        del model
        if DEVICE == "cuda": torch.cuda.empty_cache()

if "B" in PHASES:
    label, path = "410m", "EleutherAI/pythia-410m-deduped"
    for step in LADDER:
        need = [f"B_{label}_step{step}_{m}" for m in ("free", "forced")]
        specs_tag = f"C_{label}_step{step}_spectra"
        if all(done(t) for t in need) and done(specs_tag):
            print("skip step", step); continue
        tok, model = load(path, step)
        if not done(specs_tag):
            save(specs_tag, **weight_spectra(model))          # PHASE C, free
        for mode, tag in zip(("free", "forced"), need):
            if done(tag): continue
            ts, bits, meta = capture(tok, model, mode, PROMPTS[0], 42)
            save(tag, ts=ts, bits=bits, **{k: np.array(v) for k, v in meta.items()})
        del model
        if DEVICE == "cuda": torch.cuda.empty_cache()

print("ALL PHASES COMPLETE. The shard folder now serves every queued test offline.")

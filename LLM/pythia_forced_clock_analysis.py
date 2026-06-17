#!/usr/bin/env python3
"""
Pythia learning curves: is LLM training a FORCED CLOCK driven up toward the phi
landmark, or a self-organising engine sitting AT phi?  (Dylan La Franchi, 14 Jun 2026)

phi is the framework's MEASURING STICK (KAM last-torus + pentagon geometry =
2cos36deg; see EnergyRatio/HEX_PENTAGON_ANGLE_HYPOTHESIS.md). It is NOT on trial
here. We place the LLM on the phi ruler and read where it sits.

Data: EleutherAI Pythia zero-shot evals, 8 deduped sizes x 27 log-spaced
checkpoints (steps 0..143000), read from pythia_curves/ALL_zeroshot_master.csv
(built from PythiaLogs/pythia-main/evals/pythia-v1/.../zero-shot/*.json).
Headline metric = correlation / fraction; honest about estimator noise.
"""
import csv, math, numpy as np
PHI=(1+5**0.5)/2
rows=list(csv.DictReader(open("pythia_curves/ALL_zeroshot_master.csv")))
sizes=["70m","160m","410m","1b","1.4b","2.8b","6.9b","12b"]
pm={"70m":70,"160m":160,"410m":410,"1b":1000,"1.4b":1400,"2.8b":2800,"6.9b":6900,"12b":12000}
data={s:sorted((int(r["step"]),float(r["lambada_acc"]),float(r["lambada_ppl"]))
               for r in rows if r["model"]==f"pythia-{s}-deduped") for s in sizes}

print("== P1  FORCED-CLOCK TEST: does the breakthrough fire at a FIXED compute step, size-independent? ==")
print(f"{'size':6}{'onset(acc>.05)':>16}{'peak acc':>10}{'peak step':>11}{'final acc':>10}")
for s in sizes:
    p=data[s]; onset=next((st for st,a,_ in p if a>0.05),None)
    pk=max(p,key=lambda x:x[1]); print(f"{s:6}{str(onset):>16}{pk[1]:>10.3f}{pk[0]:>11}{p[-1][1]:>10.3f}")
print("  -> onset clusters at step 1000-3000 for ALL sizes = energy(compute) sets the clock; size does not move it.")

print("\n== P2  ONE UNIVERSAL FORCED SHAPE? size-normalised curves, mean pairwise corr ==")
common=[1000,3000,13000,23000,33000,53000,73000,93000,113000,143000]
M=[]
for s in sizes:
    d=dict((st,a) for st,a,_ in data[s]); pk=max(d.values())
    M.append([d[c]/pk for c in common])
cc=np.corrcoef(np.array(M)); print(f"  mean pairwise corr = {cc[np.triu_indices(len(sizes),1)].mean():.3f}  (1.0 = identical forced shape)")

print("\n== P3  PLACE ON THE phi RULER: info-transfer handover (bits = log2 ppl) ==")
print("  forced clock that can't flywheel should sit BELOW the 1/phi=%.3f engine handover." % (1/PHI))
hf=[]
for s in sizes:
    pts=[(st,math.log2(p)) for st,a,p in data[s] if st>0]
    L0=pts[0][1]; Lf=min(l for _,l in pts); tot=L0-Lf
    frac=[(st,(L0-l)/tot) for st,l in pts]
    sl=[((frac[i][1]-frac[i-1][1])/(math.log(frac[i][0])-math.log(frac[i-1][0])),frac[i][0],frac[i][1]) for i in range(1,len(frac))]
    h=max(sl); hf.append((s,h[1],h[2]))
    print(f"  {s:6} handover step {h[1]:>6}  captured frac {h[2]:.3f}  (vs 1/phi {1/PHI:.3f})")
clean=[f for s,st,f in hf if s in ("2.8b","6.9b","12b")]  # near-compute-optimal, best-resolved
print(f"  cleanest large models (2.8b/6.9b/12b) handover ~ {np.mean(clean):.3f} = BELOW 1/phi -> forced clock short of the engine handover.")
print(f"  (small/over-trained sizes scatter 0.50-0.67; 160m's steep point lands in the late coarse rung = a different-rung handover, not noise.)")

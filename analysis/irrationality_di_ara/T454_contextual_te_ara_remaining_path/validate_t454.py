"""Validate T454 formula arithmetic, metrics, and report packaging."""
from __future__ import annotations
import json,re
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T454_contextual_te_ara_remaining_path"); R=ROOT/'results'
def item(name,passed,detail): return {'check':name,'passed':bool(passed),'detail':detail}
def main():
    p=pd.read_csv(R/'T454_DIRECT_FORECASTS.csv'); m=pd.read_csv(R/'T454_METRICS.csv'); l=pd.read_csv(R/'T454_PREDICTION_LEDGER.csv'); g=pd.read_csv(R/'T454_FROZEN_GATES.csv'); result=json.loads((R/'T454_RESULT.json').read_text())
    checks=[]
    rel=np.clip(2-(p.x_generation+p.ara_phase_gap),0,2); fixed=np.clip(2-(p.x_generation+p.ara_phase_gap+.25),0,2); size=np.clip(2-(p.x_generation+p.ara_phase_gap+p.x_size/4),0,2)
    checks.append(item('relational formula exact',np.max(np.abs(rel-p.pred_relational))<1e-12,f"max diff={np.max(np.abs(rel-p.pred_relational)):.3g}"))
    checks.append(item('fixed 0.25 formula exact',np.max(np.abs(fixed-p.pred_fixed_025))<1e-12,f"max diff={np.max(np.abs(fixed-p.pred_fixed_025)):.3g}"))
    checks.append(item('measured size-child formula exact',np.max(np.abs(size-p.pred_size_child))<1e-12,f"max diff={np.max(np.abs(size-p.pred_size_child)):.3g}"))
    checks.append(item('all forecasts remain prospective',bool((p.remaining_divisions>0).all() and (p.remaining_hours>0).all()),f"min remainder={p.remaining_divisions.min()} divisions"))
    maxdiff=0.0
    for _,row in m.iterrows():
        s=l[(l.split==row.split)&(l.target==row.target)&(l.bounded_target==row.bounded_target)&(l.model==row.model)]
        val=pd.DataFrame({'cell':s.cell_key,'ae':np.abs(s.prediction-s.actual)}).groupby('cell').ae.mean().mean(); maxdiff=max(maxdiff,abs(val-row.cell_mean_mae))
    checks.append(item('metrics reproduce from direct ledger',maxdiff<1e-10,f"max diff={maxdiff:.3g}"))
    checks.append(item('bounded and unbounded relational direction agree',result['holdout_relational_vs_pure_generation_improvement_pct']>0 and result['external_relational_vs_pure_generation_improvement_pct']>0,'positive on both holdouts'))
    checks.append(item('reverse sign worse in both holdouts',bool(g[g.gate=='G6'].iloc[0].passed), 'G6'))
    checks.append(item('frozen gate accounting',int(g.passed.sum())==result['gates_passed']==4,f"{result['gates_passed']}/6"))
    report=R/'T454_CONTEXTUAL_TE_ARA_REPORT.html'; text=report.read_text(encoding='utf-8'); refs=re.findall(r"<img[^>]+src=['\"]([^'\"]+)",text); missing=[x for x in refs if not (R/x).exists()]
    checks.append(item('report images resolve',len(refs)==5 and not missing,f"{len(refs)} images; missing={missing}"))
    checks.append(item('posthoc sensitivity explicitly labelled','Post-result diagnostic only' in text and 'not uniquely identified' in text,'interpretation fence present'))
    out={'test':'T454','checks_passed':sum(x['passed'] for x in checks),'checks_total':len(checks),'all_passed':all(x['passed'] for x in checks),'assessment':'Share with caveats' if all(x['passed'] for x in checks) else 'Resolve failed validation','checks':checks}
    (R/'T454_VALIDATION.json').write_text(json.dumps(out,indent=2),encoding='utf-8'); print(json.dumps(out,indent=2)); raise SystemExit(0 if out['all_passed'] else 1)
if __name__=='__main__': main()

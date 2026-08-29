"""Build T454 durable HTML report."""
from __future__ import annotations
import html, json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T454_contextual_te_ara_remaining_path")
R=ROOT/"results"

def table(df, cols, names):
    h=''.join(f'<th>{html.escape(names.get(c,c))}</th>' for c in cols); body=[]
    for _,r in df.iterrows():
        t=[]
        for c in cols:
            v=r[c]; v=f'{v:.3f}' if isinstance(v,(float,np.floating)) else str(v); t.append(f'<td>{html.escape(v)}</td>')
        body.append('<tr>'+''.join(t)+'</tr>')
    return f"<div class='tw'><table><thead><tr>{h}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"

def main():
    result=json.loads((R/'T454_RESULT.json').read_text(encoding='utf-8'))
    metrics=pd.read_csv(R/'T454_METRICS.csv'); gates=pd.read_csv(R/'T454_FROZEN_GATES.csv'); boots=pd.read_csv(R/'T454_BOOTSTRAP.csv'); forecasts=pd.read_csv(R/'T454_DIRECT_FORECASTS.csv'); scan=pd.read_csv(R/'T454_POSTHOC_OFFSET_SENSITIVITY.csv')
    labels={'pure':'Pure 2 − A','relational':'Relational 2 − (A + R)','fixed_025':'Relational + fixed 0.25','size_child':'Relational + size child/4','rpl_child':'Relational + Rpl child/4','reverse_control':'Reverse-sign control'}
    m=metrics[(metrics.bounded_target==True)&(metrics.target=='generation')].copy(); m['formula']=m.model.map(labels)
    hold=m[m.split=='holdout']; ext=m[m.split=='external']
    bh=boots[(boots.split=='holdout')&(boots.target=='generation')&(boots.bounded_target==True)&(boots.baseline=='pure')&(boots.candidate=='relational')].iloc[0]
    be=boots[(boots.split=='external')&(boots.target=='generation')&(boots.bounded_target==True)&(boots.baseline=='pure')&(boots.candidate=='relational')].iloc[0]
    child_ext=boots[(boots.split=='external')&(boots.target=='generation')&(boots.bounded_target==True)&(boots.baseline=='relational')&(boots.candidate=='fixed_025')].iloc[0]
    bests=scan.loc[scan.groupby('split').cell_mean_mae.idxmin()].set_index('split')
    size_med=float((forecasts[forecasts.split=='holdout'].x_size/4).median()); rpl_med=float((forecasts[forecasts.split=='holdout'].x_rpl/4).median())
    gc=''.join(f"<div class='gate {'pass' if bool(r.passed) else 'fail'}'><b>{r.gate} {'PASS' if bool(r.passed) else 'FAIL'}</b><small>{html.escape(r.statement)}<br>Observed: {r.observed:.3g}</small></div>" for _,r in gates.iterrows())
    css="""
    :root{--bg:#0b1018;--panel:#121a27;--ink:#eef3f8;--muted:#aab7c7;--line:#2b394d;--blue:#5da2ef;--green:#4ac487;--red:#ec6868;--orange:#ee9730;--purple:#b27bea}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,Segoe UI,Arial,sans-serif;line-height:1.55}main{max-width:1500px;margin:auto;padding:28px}h1{font-size:clamp(2rem,4.5vw,4.5rem);line-height:1.02;margin:.15em 0}.k{color:var(--blue);font-weight:800;letter-spacing:.1em;text-transform:uppercase}.lede{font-size:1.25rem;max-width:1100px}.panel{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:24px;margin:22px 0}.answer{border-left:6px solid var(--blue)}h2{font-size:2rem;margin:0 0 10px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:14px}.metric{background:#0d1520;border:1px solid var(--line);border-radius:13px;padding:17px}.metric b{display:block;font-size:2rem}.metric small,.caption{color:var(--muted)}img{width:100%;height:auto;background:white;border-radius:12px;margin:14px 0}.plain{padding:14px 16px;border-left:4px solid var(--blue);background:#0d2130;border-radius:8px}.warn{border-color:var(--orange);background:#2b1d12}.two{display:grid;grid-template-columns:1fr 1fr;gap:18px}.tw{overflow:auto;border:1px solid var(--line);border-radius:10px}table{border-collapse:collapse;width:100%;min-width:620px}th,td{padding:9px 11px;border-bottom:1px solid var(--line);text-align:left}th{background:#172338}.gates{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px}.gate{padding:13px;border:1px solid var(--line);border-left:5px solid var(--red);border-radius:10px}.gate.pass{border-left-color:var(--green)}.gate small{display:block;color:var(--muted);margin-top:6px}code{background:#09101a;border:1px solid var(--line);padding:2px 6px;border-radius:5px}a{color:#87bcf4}@media(max-width:850px){main{padding:15px}.two{grid-template-columns:1fr}}
    """
    doc=fr"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>T454 contextual TE-ARA</title><style>{css}</style></head><body><main>
    <p class='k'>ARA test T454 · frozen direct geometry</p><h1>The contextual TE-ARA path is more accurate than the pure complement</h1>
    <p class='lede'>Your correction works in the predicted direction. Adding the measured generation/clock relation to the fixed total-2 ledger improves the unseen remaining path on both holdouts. Adding the predeclared 0.25 child improves it again—but the relational term is the strong result, while the exact child amount remains a gradient rather than a locked universal landmark.</p>
    <section class='panel answer'><h2>Answer first</h2><div class='grid'>
    <div class='metric'><b>{result['holdout_fixed_025_vs_pure_generation_improvement_pct']:.1f}%</b><small>combined relation + 0.25 improvement over pure; 12-cell holdout</small></div>
    <div class='metric'><b>{result['external_fixed_025_vs_pure_generation_improvement_pct']:.1f}%</b><small>combined relation + 0.25 improvement over pure; 119 external cells</small></div>
    <div class='metric'><b>{result['external_relational_vs_pure_generation_improvement_pct']:.1f}%</b><small>external improvement due to the relational term alone</small></div>
    <div class='metric'><b>{result['gates_passed']}/{result['gates_total']}</b><small>frozen gates passed</small></div></div>
    <p class='plain'><b>Exact reading:</b> <code>2 − (A + R_AB + 0.25)</code> is more accurate than <code>2 − A</code> on both held-out groups. However, most of the transferable improvement comes from <code>R_AB = clock − generation</code>. The 0.25 term supplies a smaller correction whose independent bootstrap interval crosses zero.</p></section>

    <section class='panel'><h2>1. What was tested</h2><p>No formula was fitted. The same direct allocation was applied to every legal prefix:</p>
    <p class='plain'><b>Pure:</b> \(2-A\)<br><b>Relational:</b> \(2-(A+R_{{AB}})\)<br><b>Contextual child:</b> \(2-(A+R_{{AB}}+C)\), with \(C=0.25\), size-child/4, or Rpl-child/4.</p>
    <p>Because <code>A + R_AB = clock</code>, the relational construction explicitly restores the disagreement between biological generation progress and elapsed clock progress. The reverse-sign control tests whether the direction matters.</p>
    <img src='T454_01_DIRECT_SCORECARD.png' alt='Direct formula errors and gates'><p class='caption'>Lower bars are better. Four of six frozen gates pass. The two misses are close: 4.53% against a 5% relational threshold, and 3.96% against a 5% child-over-relation threshold.</p></section>

    <section class='panel'><h2>2. The path geometry</h2><img src='T454_02_REMAINING_PATHS.png' alt='Actual and predicted remaining paths'><p class='caption'>Black is the unseen answer. Grey is the pure complement. Blue restores the generation/clock asymmetry. Purple and orange spend another child share from the remaining ledger. The external panel shows the cleanest result: pure closure falls far too quickly, while the relational path follows the observed remainder closely until the clipped endpoint.</p>
    <div class='two'><div><h3>Experiment 9</h3>{table(hold,['formula','cell_mean_mae','rmse','bias'],{'formula':'formula','cell_mean_mae':'mean per-cell MAE','rmse':'RMSE','bias':'bias'})}</div><div><h3>Experiments 1–6</h3>{table(ext,['formula','cell_mean_mae','rmse','bias'],{'formula':'formula','cell_mean_mae':'mean per-cell MAE','rmse':'RMSE','bias':'bias'})}</div></div>
    <p class='plain'><b>Whole-cell uncertainty:</b> external relational MAE gain over pure is {be.mean_mae_gain:.3f}, 95% bootstrap interval [{be.ci_low:.3f}, {be.ci_high:.3f}]. The same-platform gain is {bh.mean_mae_gain:.3f}, interval [{bh.ci_low:.3f}, {bh.ci_high:.3f}], reflecting only twelve cells.</p></section>

    <section class='panel'><h2>3. What happened to the 0.25 child?</h2><img src='T454_03_RELATION_AND_CHILD_GEOMETRY.png' alt='Relational displacement and child allocation geometry'><p class='caption'>Red points indicate where a term helps; blue where it overspends the ledger. The measured size child sits around {size_med:.3f}; Rpl13A around {rpl_med:.3f}. Rpl13A is therefore naturally near the proposed grandchild ridge of 0.25, while size is usually larger.</p>
    <p>The fixed 0.25 was the best of the frozen child formulas in Experiment 9. It improves the relational generation forecast by 3.96%, and the complete contextual formula improves the clock target by {result['holdout_winner_clock_vs_pure_improvement_pct']:.1f}% versus pure. Externally, fixed 0.25 improves generation by {result['external_fixed_025_vs_pure_generation_improvement_pct']:.1f}% versus pure, but only a small amount beyond the relation itself.</p>
    <img src='T454_05_POSTHOC_OFFSET_SENSITIVITY.png' alt='Post-result offset sensitivity'><p class='caption'><b>Post-result diagnostic only:</b> the large external sample has a broad minimum around {bests.loc['external','offset']:.2f}, close to 0.25. The small holdout minimum is around {bests.loc['holdout','offset']:.2f}. Therefore 0.25 is compatible with the external shape but is not uniquely identified across datasets.</p>
    <div class='plain warn'><b>Why this matters:</b> if 0.25 were a fixed universal grandchild allocation for this cut, both minima should organise around it. They do not. The correct current reading is “child/context expenditure improves the path,” with its amount conditioned by the identity and measurement boundary.</div></section>

    <section class='panel'><h2>4. Individual cells</h2><img src='T454_04_INDIVIDUAL_PATHS.png' alt='Direct TE-ARA paths in individual cells'><p class='caption'>These show why the aggregate child result is a gradient. A single offset can improve the centre of many paths while overspending the ledger for particular long-lived cells.</p></section>

    <section class='panel answer'><h2>5. ARA verdict</h2><div class='gates'>{gc}</div>
    <p><b>Supported:</b> for this lifespan cut, contextual allocation is more faithful than treating the identity as an isolated pure pair. The sign of the relation is not arbitrary: reversing it is worse in both holdouts, dramatically so in the 119-cell transfer.</p>
    <p><b>Not yet supported:</b> a universal exact 0.25 internal child, a completed four-dimensional sphere, or Time itself. The relational correction largely says that generation progress alone is not the whole identity; elapsed clock progress is a separately informative coupled cut.</p>
    <p class='plain'><b>Best next step:</b> freeze the relational formula and estimate the child share from an independently observed internal process—without using the future outcome. That directly tests whether the child term is a real allocation rather than a useful constant bias correction.</p></section>
    <section class='panel'><h2>Traceability</h2><p>The frozen protocol, direct forecast ledger, bounded and unbounded scores, whole-cell bootstraps, sensitivity table and all figures are stored beside this report.</p></section>
    </main></body></html>"""
    out=R/'T454_CONTEXTUAL_TE_ARA_REPORT.html'; out.write_text(doc,encoding='utf-8'); print(out)

if __name__=='__main__': main()

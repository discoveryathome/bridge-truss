"""Versioned research-only load portfolio with two-engine candidate validation."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research/readiness-20261021'
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'research/feature-trial/code'))
import numpy as np
from truss.model import load
from truss.solver import Solver
from truss.independent import check
from truss.verify import candidate
import baseline,hybrid
from common import Evaluator,BudgetReached

def model(name):
    p=OUT/'models'/f'{name}.json';b=json.loads(p.read_text());digest=hashlib.sha256(p.read_bytes()).hexdigest()
    if digest!=json.loads((OUT/'models/LOCK.json').read_text())[name]:raise ValueError('model lock')
    b['sha256']=digest;return b

def verify(c):
    b=model(c['case'])
    if c.get('profile')!='tube-euler' or c.get('model_sha256')!=b['sha256']:raise ValueError('wrong model/profile')
    a=Solver(b,'tube-euler').evaluate(c['areas'],True);z=check(b,c['areas'],'tube-euler')
    if not a['valid'] or not z['valid']:raise ValueError('structural rejection')
    errors={}
    for key in ('mass_lbm','displacements','forces','reactions','stress_utilization','displacement_utilization','buckling_utilization'):
        x=np.asarray(a[key]);y=np.asarray(z[key]);errors[key]=float(np.max(abs(x-y))/max(1.,float(np.max(abs(x)))))
        if errors[key]>b['tolerance']['agreement_relative']:raise ValueError('solver disagreement')
    if 'claimed_mass_lbm' in c and abs(c['claimed_mass_lbm']-a['mass_lbm'])>1e-7:raise ValueError('mass mismatch')
    return dict(primary=a,independent=z,solver_relative_differences=errors,section_count=len(set(c['areas'])-{0.}))

def coordinate(b,initial,budget=12000):
    ev=Evaluator(b,initial,budget,checker=verify)
    try:
        for sweep in range(100):
            old=ev.best_mass;x=list(ev.best['areas'])
            for i in range(len(x)):
                for area in ev.catalog:
                    if area>=x[i]:continue
                    proposal=x.copy();proposal[i]=area;ev.evaluate(proposal)
            if ev.best_mass>=old-1e-8:break
    except BudgetReached:pass
    return ev.finish(method='best-feasible single-member coordinate descent')

def prepare():
    (OUT/'models').mkdir(exist_ok=True);locks={};specs=[]
    # These load variations are explicit sensitivity studies, not industry data.
    for base in ('10bar','25bar'):
        for mode in ('individual','lateral-reversal','vertical-reversal','all-reversals'):
            b=copy.deepcopy(load(base));b.pop('sha256');b['id']=f'{base}-{mode}-v2';b['version']='research-portfolio-2.0.0'
            b['groups']=list(range(len(b['members'])));b['source_note']='Derived research sensitivity case; load choice needs structural reviewer approval.'
            b.pop('published',None);b.pop('additional_published',None);b.pop('published_disputed',None)
            axes=[] if mode=='individual' else [0] if mode=='lateral-reversal' else [b['dimension']-1] if mode=='vertical-reversal' else list(range(b['dimension']))
            for axis in axes:
                lc=copy.deepcopy(b['loads'][0]);lc['name']=f'reversal-axis-{axis}'
                for force in lc['nodal']:force[axis+1]*=-1
                b['loads'].append(lc)
            path=OUT/'models'/f"{b['id']}.json";path.write_text(json.dumps(b,indent=2)+'\n');locks[b['id']]=hashlib.sha256(path.read_bytes()).hexdigest();specs.append(b['id'])
    (OUT/'models/LOCK.json').write_text(json.dumps(locks,indent=2)+'\n')
    runs=[];frontier=[]
    for name in specs:
        b=model(name);initial=candidate(b,'tube-euler',[max(b['catalog'])]*len(b['members']))
        # Inherit the best already known feasible witness rather than resetting easy wins.
        if name=='25bar-individual-v2':
            old=json.loads((ROOT/'research/feature-trial/extension/best-verified.json').read_text())
            initial=candidate(b,'tube-euler',old['areas'])
        elif name=='10bar-individual-v2':
            old=json.loads((ROOT/'results/10bar-tube-topology-winner.json').read_text());initial=candidate(b,'tube-euler',old['areas'])
        verify(initial)
        coordinate_result=coordinate(b,initial)
        (OUT/f'{name}-coordinate.json').write_text(json.dumps(coordinate_result,indent=2)+'\n')
        initial=coordinate_result['candidate']
        outcomes=[]
        for module in (baseline,hybrid):
            r=module.run(name,20261021,budget=2000,initial_override=initial,model_override=b,checker=verify)
            # Preserve full outcome, including unsuccessful proposals.
            file=OUT/f'{name}-{module.__name__}.json';file.write_text(json.dumps(r,indent=2)+'\n')
            outcomes.append(r);runs.append(dict(case=name,method=module.__name__,mass_lbm=r['mass_lbm'],initial_mass_lbm=r['initial_mass_lbm'],
                structural_solves=r['discrete_evaluations']+r['continuous_solves'],seconds=r['elapsed_seconds']))
        best=min(outcomes,key=lambda r:r['mass_lbm']);c=best['candidate'];v=verify(c);path=OUT/f'{name}-incumbent.json';path.write_text(json.dumps(c,indent=2)+'\n')
        frontier.append(dict(case=name,object=str(path.relative_to(ROOT)),mass_lbm=v['primary']['mass_lbm'],section_count=v['section_count'],
           status='author-checked model witness; engineering review pending',mass_section_comparisons=[dict(method=module.__name__,mass_lbm=r['mass_lbm'],section_count=verify(r['candidate'])['section_count']) for module,r in zip((baseline,hybrid),outcomes)]))
        print(name,frontier[-1]['mass_lbm'],frontier[-1]['section_count'],flush=True)
    (OUT/'portfolio.json').write_text(json.dumps(dict(formulation='research-portfolio-2.0.0',frontier=frontier,runs=runs,
       scope='Eight sensitivity cases derived from two geometries; not eight independent engineering applications. Original tolerances, sections, physics and solvers retained.',
       objectives='Minimize mass; report section count separately. No unreviewed manufacturing penalty combined into score.'),indent=2)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate');a=p.parse_args()
    if a.candidate:print(json.dumps(verify(json.loads(Path(a.candidate).read_text())),indent=2))
    else:prepare()
if __name__=='__main__':main()

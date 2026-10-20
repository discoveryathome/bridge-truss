"""Separately frozen exploratory instance. Does not modify or supersede the
original grouped benchmark or its verifier. Both original structural engines
are used unchanged with individual member groups."""
from common import *
import hashlib
from truss.independent import check
EXT=ROOT/'research/feature-trial/extension'
def model():
 raw=(EXT/'model.json').read_bytes();lock=json.loads((EXT/'LOCK.json').read_text());digest=hashlib.sha256(raw).hexdigest()
 if digest!=lock['model_sha256']:raise ValueError('extension model hash mismatch')
 b=json.loads(raw);b['sha256']=digest
 original=load('25bar')
 for field in ['nodes','members','fixed_nodes','loads','catalog','E','density_lbm_in3','stress_limit','displacement_limits','tolerance','profiles']:
  if b[field]!=original[field]:raise ValueError('Unexpected extension physics change: '+field)
 return b

def verify_extension(c):
 b=model()
 if c['case']!=b['id'] or c['model_sha256']!=b['sha256'] or c['profile']!='tube-euler':raise ValueError('extension identity mismatch')
 primary=Solver(b,'tube-euler').evaluate(c['areas'],True);other=check(b,c['areas'],'tube-euler')
 if not primary['valid'] or not other['valid']:raise ValueError('extension structural rejection')
 errors={}
 for k in ['mass_lbm','displacements','forces','reactions','stress_utilization','displacement_utilization','buckling_utilization']:
  x=np.asarray(primary[k]);y=np.asarray(other[k]);error=float(np.max(abs(x-y))/max(1,float(np.max(abs(x)))));errors[k]=error
  if error>b['tolerance']['agreement_relative']:raise ValueError('extension solver disagreement')
 if 'claimed_mass_lbm' in c and abs(c['claimed_mass_lbm']-primary['mass_lbm'])>1e-7:raise ValueError('extension mass claim')
 return dict(case=c['case'],profile=c['profile'],model_sha256=c['model_sha256'],primary=primary,independent=other,solver_relative_differences=errors,evidence_level='author-checked',claim_kind='model',scope='separate individual-member extension; not a grouped-benchmark record')

def run(budget=40000):
 b=model();initial=json.loads((EXT/'before.json').read_text());ev=Evaluator(b,initial,budget,checker=verify_extension);n=len(initial['areas']);sweeps=[]
 try:
  for sweep in range(60):
   start_count=ev.count;old=ev.best_mass;x=np.array(ev.best['areas'])
   # Greedily accept the best feasible one-member decrease after a complete scan.
   # This exposes the amount of easy hill climbing in the *new* design space.
   for i in range(n):
    for v in ev.catalog:
     if v>=x[i]:continue
     y=x.copy();y[i]=v;ev.evaluate(y)
   sweeps.append(dict(sweep=sweep,evaluations=ev.count-start_count,mass_lbm=ev.best_mass,savings_percent=100*(1-ev.best_mass/ev.base)))
   if ev.best_mass>=old-1e-8:break
  # Test coordinated local exchanges once greedy work is exhausted.
  for sweep in range(10):
   old=ev.best_mass;current=np.array([ev.catalog.index(a) for a in ev.best['areas']]);hi=len(ev.catalog)-1;start_count=ev.count
   for i in range(n):
    for j in range(i+1,n):
     for di in [-2,-1,1,2]:
      for dj in [-2,-1,1,2]:
       v=current.copy();v[i]+=di;v[j]+=dj
       if min(v)>=0 and max(v)<=hi:ev.evaluate([ev.catalog[k] for k in v])
   sweeps.append(dict(pair_sweep=sweep,evaluations=ev.count-start_count,mass_lbm=ev.best_mass,savings_percent=100*(1-ev.best_mass/ev.base)))
   if ev.best_mass>=old-1e-8:break
 except BudgetReached:pass
 return ev.finish(method='individual-member coordinate descent followed by paired exchanges',sweeps=sweeps,comparison='Changed grouping, unchanged physics; not evidence of progress on original frozen cases.')
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--check-only',action='store_true');a=p.parse_args()
 if a.check_only:print(json.dumps(verify_extension(json.loads((EXT/'before.json').read_text()))['primary'],indent=2))
 else:
  r=run();dump('extension-individual-25bar.json',r);(EXT/'winner.json').write_text(json.dumps(r['candidate'],indent=2)+'\n');print(r['initial_mass_lbm'],r['mass_lbm'],r['savings_percent'],r['discrete_evaluations'],r['elapsed_seconds'])

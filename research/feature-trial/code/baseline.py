"""Supplied DE + limited pair search, warmed with the same starting incumbent."""
from common import *
from scipy.optimize import differential_evolution

def run(case,seed,budget=12000,variant="tube-topology",initial_override=None,model_override=None,checker=verify):
 b=model_override if model_override is not None else load(case);initial=initial_override or incumbent(case,variant);ev=Evaluator(b,initial,budget,checker=checker);
 if variant!="tube-topology":ev.catalog=b["catalog"]
 C=ev.catalog;n=len(initial['areas']);hi=len(C)-1
 def score(v):
  r=ev.evaluate([C[int(round(i))] for i in v]);return r['mass_lbm']/ev.base+100*r['violation']
 try:
  differential_evolution(score,[(0,hi)]*n,integrality=np.ones(n,dtype=bool),rng=np.random.default_rng(seed),popsize=8,maxiter=120,tol=0,atol=0,polish=False,workers=1,updating='immediate',x0=[C.index(a) for a in initial['areas']])
  for _ in range(50):
   old=ev.best_mass;current=np.array([C.index(a) for a in ev.best['areas']])
   for i in range(n):
    for k in range(hi+1):v=current.copy();v[i]=k;ev.evaluate([C[j] for j in v])
   current=np.array([C.index(a) for a in ev.best['areas']])
   for i in range(n):
    for j in range(i+1,n):
     for di in ([-3,-2,-1,1,2,3] if variant=='reference' else [-2,-1,1,2]):
      for dj in ([-3,-2,-1,1,2,3] if variant=='reference' else [-2,-1,1,2]):
       v=current.copy();v[i]+=di;v[j]+=dj
       if min(v)>=0 and max(v)<=hi:ev.evaluate([C[k] for k in v])
   if ev.best_mass>=old-1e-8:break
 except BudgetReached:pass
 # Spend remaining budget with fresh incumbent-centered integer mutations,
 # explicitly reported as a stronger continuation control than the supplied DE.
 rng=np.random.default_rng(seed+10_000)
 while ev.count<budget:
  x=np.array([C.index(a) for a in ev.best['areas']]);idx=rng.choice(n,size=int(rng.integers(1,min(4,n)+1)),replace=False);x[idx]=np.clip(x[idx]+rng.integers(-6,7,size=len(idx)),0,hi)
  try:ev.evaluate([C[k] for k in x])
  except BudgetReached:break
 return ev.finish(method='warm-DE+limited-local+budget-fill-random-mutations',seed=seed,variant=variant)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--budget',type=int,default=12000);a=p.parse_args()
 for case in ['10bar','25bar']:
  for seed in [101,202,303,404,505]:
   r=run(case,seed,a.budget);dump(f'baseline-{case}-{seed}.json',r);print(case,seed,r['mass_lbm'],r['savings_percent'],r['elapsed_seconds'],flush=True)

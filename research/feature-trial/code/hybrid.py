"""Fixed-mask continuous proposals, catalogue-neighborhood enumeration, and
constraint-aware discrete exchanges. Relaxed proposals are NEVER accepted as results."""
from common import *
from scipy.optimize import minimize
from itertools import combinations,product
import heapq
class Relax:
 def __init__(self,ev,mask):
  self.ev=ev;self.mask=np.array(mask);self.indices=np.flatnonzero(mask);self.s=ev.solver;self.b=ev.b;self.last=None;self.record=None
  self.groupcost=np.bincount(self.b['groups'],weights=self.s.L*self.b['density_lbm_in3'])
 def calc(self,v):
  key=tuple(v)
  if key==self.last:return self.record
  if self.ev.count+self.ev.continuous_solves>=self.ev.budget:raise BudgetReached
  self.ev.continuous_solves+=1;self.last=key
  x=np.zeros(len(self.mask));x[self.indices]=v;a=x[np.array(self.b['groups'])];active=a>0;k=self.b['E']*a/self.s.L;K=self.s.Bf.T@(k[:,None]*self.s.Bf)
  try:
   u=np.zeros_like(self.s.F);u[self.s.free]=np.linalg.solve(K,self.s.F[self.s.free]);N=k[:,None]*(self.s.B@u)
  except np.linalg.LinAlgError:
   self.record=(self.groupcost@x,np.full(2*len(self.s.limits)+3*sum(active),-1e5));return self.record
  stress=N[active]/a[active,None]/self.b['stress_limit'];margins=[(1-stress).ravel(),(1+stress).ravel()]
  for i,limit in self.s.limits:margins.extend([1-u[i]/limit,1+u[i]/limit])
  p=self.b['profiles'][self.ev.profile]
  if p['buckling']:
   r=p['inner_outer_diameter_ratio'];cap=np.pi*self.b['E']*a[active]**2*(1+r*r)/(4*(1-r*r)*(p['effective_length_factor']*self.s.L[active])**2*p['buckling_safety_factor'])
   margins.append((1+N[active]/cap[:,None]).ravel())
  self.record=(float(self.groupcost@x),np.concatenate(margins));return self.record

def lattice(ev,center,mask,limit=600):
 C=np.array(ev.b['catalog']);idx=np.flatnonzero(mask);loc=np.array(center)[idx];start=tuple(int(np.argmin(abs(C-v))) for v in loc)
 scales=np.array([max(.1,C[min(len(C)-1,i+1)]-C[max(0,i-1)]) for i in start]);heap=[];seen={start};heapq.heappush(heap,(0,start));tested=0;traversed=0
 costs=np.bincount(ev.b['groups'],weights=ev.solver.L*ev.b['density_lbm_in3'])
 while heap and tested<limit and traversed<limit*20:
  dist,v=heapq.heappop(heap);traversed+=1;x=np.zeros(len(mask));x[idx]=C[list(v)]
  if costs@x<ev.best_mass-1e-8:ev.evaluate(x);tested+=1
  for j in range(len(v)):
   for delta in [-1,1]:
    w=list(v);w[j]+=delta;w=tuple(w)
    if 0<=w[j]<len(C) and w not in seen:
     seen.add(w);distance=float(np.sum(((C[list(w)]-loc)/scales)**2));heapq.heappush(heap,(distance,w))
 return dict(tested=tested,traversed=traversed)

def run(case,seed,budget=12000,variant="tube-topology",initial_override=None,model_override=None,checker=verify):
 b=model_override if model_override is not None else load(case);initial=initial_override or incumbent(case,variant);ev=Evaluator(b,initial,budget,checker=checker);
 if variant!="tube-topology":ev.catalog=b["catalog"]
 rng=np.random.default_rng(seed);n=len(initial['areas']);mask=np.array(initial['areas'])>0
 masks=[tuple(mask),tuple(np.ones(n,dtype=bool))]
 # Swapping / deleting / restoring groups changes force distribution. Rank is a
 # cheap mask-level screen, independent of cross-sectional values when positive.
 flips=list(combinations(range(n),1))+list(combinations(range(n),2));rng.shuffle(flips)
 for ids in (flips if variant=="tube-topology" else []):
  m=mask.copy();m[list(ids)]=~m[list(ids)];masks.append(tuple(m))
 details=[]
 try:
  for mi,m in enumerate(dict.fromkeys(masks)):
   active=np.array(m)[np.array(b['groups'])];B=ev.solver.Bf[active]
   if B.shape[0]<len(ev.solver.free) or np.linalg.matrix_rank(B,tol=1e-10)<len(ev.solver.free):continue
   rel=Relax(ev,m);x=np.array(ev.best['areas']);x[x==0]=max(b['catalog']);v=x[rel.indices]
   if mi>1:v=np.maximum(min(b['catalog']),v*rng.uniform(.85,1.15,size=len(v)));v=np.minimum(max(b['catalog']),v)
   start_count=ev.continuous_solves
   res=minimize(lambda v:rel.calc(v)[0]/ev.base,v,method='SLSQP',bounds=[(min(b['catalog']),max(b['catalog']))]*len(v),constraints=[{'type':'ineq','fun':lambda v:rel.calc(v)[1]}],options={'maxiter':120,'ftol':1e-10})
   mass,margin=rel.calc(res.x);center=np.zeros(n);center[rel.indices]=res.x
   detail=dict(mask=[bool(v) for v in m],success=bool(res.success),continuous_mass=mass,min_margin=float(min(margin)),continuous_calls=ev.continuous_solves-start_count)
   if min(margin)>-1e-5 and mass<ev.best_mass:
    detail['lattice']=lattice(ev,center,m,800 if mi<2 else 300)
   details.append(detail)
  # Any remaining budget: larger paired jumps around best, followed by random
  # coordinated perturbations guided by normalized catalogue position.
  current=np.array([ev.catalog.index(a) for a in ev.best['areas']]);hi=len(ev.catalog)-1;ops=list(combinations(range(n),2));rng.shuffle(ops)
  for i,j in ops:
   for di,dj in product(range(-5,6),repeat=2):
    if not di or not dj:continue
    v=current.copy();v[i]+=di;v[j]+=dj
    if min(v)>=0 and max(v)<=hi:ev.evaluate([ev.catalog[k] for k in v])
  while ev.count+ev.continuous_solves<budget:
   x=np.array([ev.catalog.index(a) for a in ev.best['areas']]);ids=rng.choice(n,size=int(rng.integers(2,min(4,n)+1)),replace=False);x[ids]=np.clip(x[ids]+rng.integers(-4,5,size=len(ids)),0,hi);ev.evaluate([ev.catalog[k] for k in x])
 except BudgetReached:pass
 return ev.finish(method='fixed-topology-SLSQP+catalogue-lattice+rank-screened-topology-swaps+large-pair-exchanges',seed=seed,variant=variant,proposals=details)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--budget',type=int,default=12000);a=p.parse_args()
 for case in ['10bar','25bar']:
  for seed in [101,202,303,404,505]:
   r=run(case,seed,a.budget);dump(f'hybrid-{case}-{seed}.json',r);print(case,seed,r['mass_lbm'],r['savings_percent'],r['discrete_evaluations'],r['continuous_solves'],r['elapsed_seconds'],flush=True)

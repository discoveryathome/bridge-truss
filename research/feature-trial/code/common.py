import json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'src'))
import numpy as np
from truss.model import load
from truss.solver import Solver
from truss.verify import candidate,verify
OUT=ROOT/'research/feature-trial/artifacts'; OUT.mkdir(exist_ok=True)
def dump(name,x): (OUT/name).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def incumbent(case,variant='tube-topology'):
 return json.loads((ROOT/'results'/f'{case}-{variant}-winner.json').read_text())
class BudgetReached(Exception):pass
class Evaluator:
 def __init__(self,b,initial,budget,checker=verify):
  self.checker=checker;self.b=b;self.profile=initial['profile'];self.solver=Solver(b,self.profile);self.catalog=([0.] if self.profile=='tube-euler' else [])+b['catalog'];self.groups=np.asarray(b['groups']);self.budget=budget;self.count=0;self.hits=0;self.cache={};self.trace=[];self.start=time.perf_counter();self.best=initial.copy();self.base=self.checker(initial)['primary']['mass_lbm'];self.best_mass=self.base;self.continuous_solves=0
 def evaluate(self,x):
  key=tuple(float(v) for v in x)
  if key in self.cache:self.hits+=1;return self.cache[key]
  if self.count+self.continuous_solves>=self.budget:raise BudgetReached
  r=self.solver.evaluate(x);self.cache[key]=r;self.count+=1
  if r['valid'] and r['mass_lbm']<self.best_mass-1e-8:
   c=candidate(self.b,self.profile,list(key)); c['claimed_mass_lbm']=r['mass_lbm'];self.checker(c)
   self.best=c;self.best_mass=r['mass_lbm'];self.trace.append(dict(evaluation=self.count+self.continuous_solves,elapsed_seconds=time.perf_counter()-self.start,mass_lbm=self.best_mass,areas=list(key)))
  return r
 def finish(self,**extra):
  return dict(candidate=self.best,verification=self.checker(self.best),initial_mass_lbm=self.base,mass_lbm=self.best_mass,savings_percent=100*(1-self.best_mass/self.base),discrete_evaluations=self.count,continuous_solves=self.continuous_solves,cache_hits=self.hits,budget=self.budget,elapsed_seconds=time.perf_counter()-self.start,trace=self.trace,**extra)

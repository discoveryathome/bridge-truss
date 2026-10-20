"""Seeded integer differential evolution followed by feasible coordinate and
paired-exchange local search. No claim of global optimality."""
import time
import numpy as np
from scipy.optimize import differential_evolution
from .solver import Solver
from .verify import candidate,verify

def search(b,profile,seed,iterations=120,removal=True):
    start=time.perf_counter(); solver=Solver(b,profile)
    catalogue=([0.] if removal and b['profiles'][profile]['allow_removal'] else [])+b['catalog']
    ng=max(b['groups'])+1; hi=len(catalogue)-1
    cache={}; trace=[]; best=np.full(ng,hi,dtype=int); best_r=solver.evaluate([catalogue[i] for i in best]); initial_mass=best_r['mass_lbm']
    assert best_r['valid']
    counts={'evaluations':0,'cache_hits':0,'invalid':0,'topology_evaluations':0,'local_accepted':0}
    def evaluate(v):
        nonlocal best,best_r
        key=tuple(int(round(i)) for i in v)
        if key in cache: counts['cache_hits']+=1; return cache[key]
        x=[catalogue[i] for i in key]; r=solver.evaluate(x); counts['evaluations']+=1
        counts['invalid']+=not r['valid']; counts['topology_evaluations']+=0 in x
        cache[key]=r
        if r['valid'] and r['mass_lbm']<best_r['mass_lbm']-1e-9:
            best=np.array(key); best_r=r; trace.append({'evaluation':counts['evaluations'],'mass_lbm':r['mass_lbm'],'areas':x})
        return r
    def score(v):
        r=evaluate(v)
        return r['mass_lbm']/initial_mass+100*r['violation']
    x0=best.copy()
    if profile=='reference': x0=np.array([catalogue.index(v) for v in b['published']['areas']]); evaluate(x0)
    differential_evolution(score,[(0,hi)]*ng,integrality=np.ones(ng,dtype=bool),rng=np.random.default_rng(seed),popsize=8,maxiter=iterations,tol=0,atol=0,polish=False,workers=1,updating='immediate',x0=x0)
    # Full coordinate sweep plus paired adjacent tradeoffs, repeated to fixed point.
    # Every intermediate result must be feasible; best may improve during enumeration.
    radius=3 if profile=='reference' else 2
    offsets=[i for i in range(-radius,radius+1) if i]
    passes=0
    while passes<50:
        old=best_r['mass_lbm']; current=best.copy(); passes+=1
        for i in range(ng):
            for value in range(hi+1):
                v=current.copy(); v[i]=value; evaluate(v)
        current=best.copy()
        for i in range(ng):
            for j in range(i+1,ng):
                for di in offsets:
                    for dj in offsets:
                        v=current.copy(); v[i]+=di; v[j]+=dj
                        if min(v)>=0 and max(v)<=hi: evaluate(v)
        if best_r['mass_lbm']>=old-1e-9: break
        counts['local_accepted']+=1
    c=candidate(b,profile,[catalogue[i] for i in best]); c['claimed_mass_lbm']=best_r['mass_lbm']
    verification=verify(c)
    return dict(candidate=c,verification=verification,seed=seed,iterations=iterations,removal=removal,algorithm=f'integer-DE/popsize8 + exhaustive-coordinate + paired-nonzero-offsets-radius{radius}',counts=counts,local_passes=passes,local_fixed_point=passes<50,trace=trace,elapsed_seconds=time.perf_counter()-start)

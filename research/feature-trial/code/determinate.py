"""Enumerate minimal 10-bar topologies; exactly reformulate their discrete
sizing within real-arithmetic linear truss theory. HiGHS bounds are numerical,
not rigorous interval proofs. Every reported design passes original verifiers."""
from common import *
from itertools import combinations
from scipy.optimize import milp,Bounds,LinearConstraint

def solve_pattern(b,active,time_limit=3.):
 s=Solver(b,'tube-euler');B=s.Bf[list(active)];dof=len(s.free)
 info=dict(active_members=[i+1 for i in active])
 if len(active)!=dof or np.linalg.matrix_rank(B,tol=1e-10)!=dof:return dict(info,status='mechanism')
 forces=np.linalg.solve(B.T,s.F[s.free]); inverse=np.linalg.inv(B)
 choices=[];cost=[];rows=[];t=b['tolerance']['constraint'];p=b['profiles']['tube-euler'];r=p['inner_outer_diameter_ratio']
 for local,e in enumerate(active):
  admissible=[]
  for a in b['catalog']:
   cap=np.pi*b['E']*a*a*(1+r*r)/(4*(1-r*r)*(p['effective_length_factor']*s.L[e])**2*p['buckling_safety_factor'])
   if max(abs(forces[local]))<=b['stress_limit']*a*(1+t) and max(-forces[local])<=cap*(1+t):admissible.append(a)
  if not admissible:return dict(info,status='no-admissible-section')
  for a in admissible:choices.append((local,e,a));cost.append(a*s.L[e]*b['density_lbm_in3'])
 nv=len(choices);A=[];lb=[];ub=[]
 for local in range(dof):A.append([int(i==local) for i,_,_ in choices]);lb.append(1);ub.append(1)
 free_map={int(d):i for i,d in enumerate(s.free)}
 for k,lim in s.limits:
  if k not in free_map:continue
  q=free_map[k]
  for c in range(forces.shape[1]):
   A.append([inverse[q,i]*forces[i,c]*s.L[e]/b['E']/a/lim for i,e,a in choices]);lb.append(-1-t);ub.append(1+t)
 start=time.perf_counter();res=milp(np.array(cost),integrality=np.ones(nv),bounds=Bounds(0,1),constraints=LinearConstraint(np.asarray(A),lb,ub),options={'time_limit':time_limit,'mip_rel_gap':1e-10})
 info.update(status=int(res.status),message=res.message,seconds=time.perf_counter()-start,binary_variables=nv,solver_bound=float(res.mip_dual_bound) if getattr(res,'mip_dual_bound',None) is not None else None,gap=float(res.mip_gap) if getattr(res,'mip_gap',None) is not None else None,nodes=int(res.mip_node_count) if getattr(res,'mip_node_count',None) is not None else None)
 if res.x is not None:
  x=[0.]*len(b['members'])
  for val,(_,e,a) in zip(res.x,choices):
   if val>.5:x[e]=a
  c=candidate(b,'tube-euler',x)
  try:check=verify(c)
  except ValueError as exc:info['verification_error']=str(exc);return info
  info.update(candidate=c,mass_lbm=check['primary']['mass_lbm'],verification=check)
 return info
if __name__=='__main__':
 b=load('10bar');results=[];start=time.perf_counter()
 for active in combinations(range(10),8):
  r=solve_pattern(b,active);results.append(r);print(r['active_members'],r['status'],r.get('mass_lbm'),flush=True)
 valid=[r for r in results if 'mass_lbm' in r]
 out=dict(method='all 45 eight-member topologies + one-hot reciprocal-area MILP',scope='10bar tube-euler; eight active members only; 9/10-member structures not bounded',results=results,elapsed_seconds=time.perf_counter()-start,best=min(valid,key=lambda r:r['mass_lbm']) if valid else None)
 dump('determinate-10bar.json',out)

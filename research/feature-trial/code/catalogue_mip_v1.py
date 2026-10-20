"""Discrete linear truss sizing as a numerical MILP with constant catalogue
capacities. Final candidates checked by untouched FE solvers. The 10bar model
has explicit bounds on every displacement; global topology uses rank cuts.
For 25bar this formulation is restricted to one fixed stable topology, using
energy-derived displacement bounds from its all-minimum-area stiffness."""
from common import *
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_array
from itertools import product

def formulate(case,mask=None,profile='tube-euler',time_limit=180):
 b=load(case);s=Solver(b,profile);p=b['profiles'][profile];n=max(b['groups'])+1;ne=len(b['members']);nf=len(s.free);g=np.array(b['groups']);F=s.F[s.free,0];fs=max(abs(F));free_index={int(k):i for i,k in enumerate(s.free)}
 assert len(b['loads'])==1,'This research formulation explicitly supports the selected single-vector cases only'
 global_topology=mask is None
 if global_topology:
  assert case=='10bar' and profile=='tube-euler'
  C=[0.]+b['catalog'];groups=list(range(n));ubound=np.zeros(nf)
  for k,lim in s.limits:ubound[free_index[k]]=lim*(1+b['tolerance']['constraint'])
  assert np.all(ubound>0)
  active_members=np.ones(ne,dtype=bool)
 else:
  C=b['catalog'];groups=list(np.flatnonzero(mask));active_members=np.asarray(mask)[g]
  B=s.Bf[active_members];L=s.L[active_members];Kmin=B.T@((b['E']*min(C)/L)[:,None]*B);inv=np.linalg.inv(Kmin)
  assert np.linalg.eigvalsh(Kmin)[0]>1e-10
  # u_i^2 <= (K^-1)_ii * F' K^-1 F <= (Kmin^-1)_ii * F' Kmin^-1 F.
  ubound=np.sqrt(np.diag(inv)*float(F@inv@F))*(1+1e-8)
  for k,lim in s.limits:ubound[free_index[k]]=min(ubound[free_index[k]],lim*(1+b['tolerance']['constraint']))
 ny=len(groups)*len(C);N0=ny;U0=ny+ne;nv=U0+nf;cost=np.zeros(nv);bounds_lo=np.full(nv,-np.inf);bounds_hi=np.full(nv,np.inf);integ=np.zeros(nv,dtype=int);integ[:ny]=1;bounds_lo[:ny]=0;bounds_hi[:ny]=1
 groupcol={group:row*len(C) for row,group in enumerate(groups)};tol=b['tolerance']['constraint'];density=b['density_lbm_in3'];buck_factor=(np.pi*b['E']*(1+p.get('inner_outer_diameter_ratio',0)**2)/(4*(1-p.get('inner_outer_diameter_ratio',0)**2)*p.get('effective_length_factor',1)**2*p.get('buckling_safety_factor',1)))
 for group,start in groupcol.items():cost[start:start+len(C)]=np.array(C)*sum(s.L[g==group])*density
 bounds_lo[U0:]=-ubound;bounds_hi[U0:]=ubound
 row=[];col=[];data=[];lb=[];ub=[]
 def add(items,low=-np.inf,high=np.inf):
  r=len(lb)
  for j,v in items:
   if v:row.append(r);col.append(int(j));data.append(float(v))
  lb.append(low);ub.append(high)
 for group,start in groupcol.items():add([(start+j,1) for j in range(len(C))],1,1)
 for i in range(nf):add([(N0+e,s.Bf[e,i]) for e in range(ne)],F[i]/fs,F[i]/fs)
 for e in range(ne):
  group=int(g[e]);k0=b['E']/s.L[e]/fs;ext_bound=float(abs(s.Bf[e])@ubound)
  if not active_members[e]:bounds_lo[N0+e]=0;bounds_hi[N0+e]=0;continue
  start=groupcol[group];cap_t=np.array(C)*b['stress_limit']*(1+tol)/fs
  if p['buckling']:cap_c=np.minimum(np.array(C)*b['stress_limit'],buck_factor*np.array(C)**2/s.L[e]**2)*(1+tol)/fs
  else:cap_c=cap_t.copy()
  bounds_lo[N0+e]=-float(max(cap_c));bounds_hi[N0+e]=float(max(cap_t))
  add([(N0+e,1)]+[(start+j,-v) for j,v in enumerate(cap_t)],high=0)
  add([(N0+e,-1)]+[(start+j,-v) for j,v in enumerate(cap_c)],high=0)
  for j,a in enumerate(C):
   if a==0:continue
   # Residual R=N-EA/L*B*u. When y=1 require R=0; otherwise
   # physical force bounds plus box extension bounds give valid big-M values.
   plus=float(max(cap_t))+k0*a*ext_bound;minus=float(max(cap_c))+k0*a*ext_bound
   expr=[(N0+e,1)]+[(U0+i,-k0*a*s.Bf[e,i]) for i in range(nf)]
   add(expr+[(start+j,plus)],high=plus)
   add([(c,-v) for c,v in expr]+[(start+j,minus)],high=minus)
 rank_cuts=[]
 if global_topology:
  # Every accepted support-restraint stiffness has full rank. Each maximal
  # rank-deficient member set must gain at least one edge from its complement.
  for bits in product([False,True],repeat=ne):
   active=np.array(bits);rank=np.linalg.matrix_rank(s.Bf[active],tol=1e-10) if any(active) else 0
   if rank>=nf:continue
   absent=np.flatnonzero(~active)
   if all(np.linalg.matrix_rank(s.Bf[np.logical_or(active,np.arange(ne)==e)],tol=1e-10)>=nf for e in absent):
    add([(groupcol[int(g[e])],1) for e in absent],high=len(absent)-1)
    rank_cuts.append([int(e)+1 for e in absent])
 matrix=coo_array((data,(row,col)),shape=(len(lb),nv)).tocsc();starttime=time.perf_counter()
 res=milp(cost,integrality=integ,bounds=Bounds(bounds_lo,bounds_hi),constraints=LinearConstraint(matrix,lb,ub),options={'time_limit':time_limit,'mip_rel_gap':1e-9})
 info=dict(case=case,profile=profile,scope='all frozen topologies' if global_topology else 'fixed mask only',mask=None if mask is None else [bool(v) for v in mask],status=int(res.status),message=res.message,elapsed_seconds=time.perf_counter()-starttime,variables=nv,binary_variables=ny,constraints=len(lb),rank_cuts=rank_cuts,displacement_bounds=ubound.tolist(),solver_bound=float(res.mip_dual_bound) if getattr(res,'mip_dual_bound',None) is not None else None,mip_gap=float(res.mip_gap) if getattr(res,'mip_gap',None) is not None else None,branch_nodes=int(res.mip_node_count) if getattr(res,'mip_node_count',None) is not None else None)
 if res.x is not None:
  x=[0.]*n
  for group,st in groupcol.items():x[group]=C[int(np.argmax(res.x[st:st+len(C)]))]
  c=candidate(b,profile,x);info['candidate']=c
  try:
   info['verification']=verify(c);info['mass_lbm']=info['verification']['primary']['mass_lbm'];info['valid']=True
  except ValueError as exc:info['verification_error']=str(exc);info['valid']=False
 return info
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--case',default='10bar',choices=['10bar','25bar']);ap.add_argument('--seconds',type=float,default=180);args=ap.parse_args()
 mask=None if args.case=='10bar' else np.array(incumbent('25bar')['areas'])>0
 r=formulate(args.case,mask,time_limit=args.seconds);dump(f'catalogue-mip-{args.case}.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ['verification','rank_cuts']},indent=2),flush=True)

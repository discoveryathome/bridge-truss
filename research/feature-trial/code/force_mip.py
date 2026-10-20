"""Force-method MILP: use self-stress coordinates instead of all nodal
translations. Catalogue choice times a bounded force coordinate is linearized
exactly with binary-product constraints. Numerical solver, not formal proof."""
from common import *
from force_enumeration import ForceSpace
from scipy.optimize import linprog,milp,Bounds,LinearConstraint
from scipy.sparse import coo_array

def solve(case,mask,seconds=15,cutoff=None):
 b=load(case);model=ForceSpace(b,mask);C=np.array(b['catalog']);r=model.r;ng=len(model.groups);na=len(C);ny=ng*na;alpha0=ny;w0=ny+r;nv=w0+ny*r;fs=max(abs(model.s.F.ravel()));tol=b['tolerance']['constraint'];p=b['profiles']['tube-euler'];ratio=p['inner_outer_diameter_ratio']
 cap=np.minimum(C[None,:]*b['stress_limit'],np.pi*b['E']*C[None,:]**2*(1+ratio*ratio)/(4*(1-ratio*ratio)*(p['effective_length_factor']*model.L[:,None])**2*p['buckling_safety_factor']))/fs*(1+tol)
 tension=C*b['stress_limit']/fs*(1+tol);z=model.Z;np0=model.part/fs
 # Necessary force capacities bound every self-stress coordinate.
 polyA=np.vstack([z,-z]);polyb=np.r_[np.max(tension)-np0,np.max(cap,axis=1)+np0]
 low=[];high=[]
 for q in range(r):
  axis=np.zeros(r);axis[q]=1
  lo=linprog(axis,A_ub=polyA,b_ub=polyb,bounds=[(None,None)]*r,method='highs');hi=linprog(-axis,A_ub=polyA,b_ub=polyb,bounds=[(None,None)]*r,method='highs')
  if lo.status==2:return dict(case=case,mask=list(map(bool,mask)),status='capacity-infeasible')
  if not lo.success or not hi.success:raise ValueError('unbounded force coordinate')
  low.append(float(lo.fun)-1e-9);high.append(float(-hi.fun)+1e-9)
 cost=np.zeros(nv)
 for g in range(ng):cost[g*na:(g+1)*na]=model.cost[g]*C
 lbv=np.zeros(nv);ubv=np.ones(nv);integ=np.zeros(nv);integ[:ny]=1;lbv[alpha0:w0]=low;ubv[alpha0:w0]=high
 for k in range(ny):
  for q in range(r):lbv[w0+k*r+q]=min(0,low[q]);ubv[w0+k*r+q]=max(0,high[q])
 rows=[];cols=[];data=[];lb=[];ub=[]
 def add(items,l=-np.inf,u=np.inf):
  rr=len(lb)
  for c,v in items:
   if v:rows.append(rr);cols.append(int(c));data.append(float(v))
  lb.append(l);ub.append(u)
 for g in range(ng):add([(g*na+j,1) for j in range(na)],1,1)
 for k in range(ny):
  for q in range(r):
   w=w0+k*r+q;aa=alpha0+q;L=low[q];U=high[q]
   add([(w,1),(k,-U)],u=0);add([(w,-1),(k,L)],u=0)
   add([(w,1),(aa,-1),(k,-L)],u=-L);add([(w,-1),(aa,1),(k,U)],u=U)
 for q in range(r):
  terms=[]
  for g in range(ng):
   for j,a in enumerate(C):
    k=g*na+j;terms.append((k,model.R[g,q]/a))
    for h in range(r):terms.append((w0+k*r+h,model.M[g,q,h]*fs/a))
  add(terms,0,0)
 for q in range(len(model.limits)):
  terms=[]
  for g in range(ng):
   for j,a in enumerate(C):
    k=g*na+j;terms.append((k,model.Q0[q,g]/a))
    for h in range(r):terms.append((w0+k*r+h,model.Qz[q,g,h]*fs/a))
  add(terms,-1-tol,1+tol)
 for e,g in enumerate(model.g):
  terms=[(alpha0+q,z[e,q]) for q in range(r)]
  add(terms+[(g*na+j,-v) for j,v in enumerate(tension)],u=-np0[e])
  add([(c,-v) for c,v in terms]+[(g*na+j,-v) for j,v in enumerate(cap[e])],u=np0[e])
 if cutoff is not None:add([(j,v/cutoff) for j,v in enumerate(cost) if v],u=1+1e-12)
 A=coo_array((data,(rows,cols)),shape=(len(lb),nv)).tocsc()
 # Validate an encoding against original FE if the starting incumbent shares mask.
 old=incumbent(case);witness_check=None
 if np.array_equal(np.array(old['areas'])>0,mask):
  pr=model.s.evaluate(old['areas'],True);alpha=model.Z.T@(np.array(pr['forces'][0])[model.active]-model.part)/fs;xx=np.zeros(nv);xx[alpha0:w0]=alpha
  for local,g in enumerate(model.groups):
   j=list(C).index(old['areas'][g]);k=local*na+j;xx[k]=1;xx[w0+k*r:w0+(k+1)*r]=alpha
  value=A@xx;viol=max(float(np.max(np.asarray(lb)-value)),float(np.max(value-np.asarray(ub))),float(np.max(lbv-xx)),float(np.max(xx-ubv)))
  assert viol<1e-7,viol;witness_check=viol
 start=time.perf_counter();res=milp(cost,integrality=integ,bounds=Bounds(lbv,ubv),constraints=LinearConstraint(A,lb,ub),options={'time_limit':seconds,'mip_rel_gap':1e-9})
 out=dict(case=case,mask=list(map(bool,mask)),status=int(res.status),message=res.message,seconds=time.perf_counter()-start,self_stress_dimension=r,variables=nv,binary_variables=ny,constraints=len(lb),force_coordinate_bounds=list(zip(low,high)),witness_constraint_violation=witness_check,solver_bound=float(res.mip_dual_bound) if getattr(res,'mip_dual_bound',None) is not None else None,gap=float(res.mip_gap) if getattr(res,'mip_gap',None) is not None else None,nodes=int(res.mip_node_count) if getattr(res,'mip_node_count',None) is not None else None,cutoff=cutoff)
 if res.x is not None:
  x=[0.]*len(mask)
  for local,g in enumerate(model.groups):x[g]=float(C[np.argmax(res.x[local*na:(local+1)*na])])
  c=candidate(b,'tube-euler',x)
  try:vr=verify(c);out.update(candidate=c,verification=vr,mass_lbm=vr['primary']['mass_lbm'])
  except ValueError as exc:out['verification_error']=str(exc)
 return out
if __name__=='__main__':
 from itertools import combinations
 results=[];initial=incumbent('10bar');best=initial['claimed_mass_lbm'];b=load('10bar');s=Solver(b,'tube-euler')
 for missing in list(range(10))+[None]:
  mask=np.ones(10,dtype=bool)
  if missing is not None:mask[missing]=False
  if np.linalg.matrix_rank(s.Bf[mask],tol=1e-10)<len(s.free):continue
  r=solve('10bar',mask,seconds=20,cutoff=best);results.append(r)
  if 'mass_lbm' in r:best=min(best,r['mass_lbm'])
  print('missing',missing,'status',r['status'],'mass',r.get('mass_lbm'),'bound',r.get('solver_bound'),'time',r.get('seconds'),flush=True)
 dump('force-mip-10bar.json',dict(results=results,best_mass_lbm=best,scope='All stable 9/10-member 10bar topologies; combine with determinate enumeration only if every numerical subproblem closes.'))

"""Exhaust the 25bar incumbent topology using a 2-dimensional self-stress
space. This is a force-method reduction, not millions of dense FE solves.
Floating-point enumeration is not an interval-certified optimality proof."""
from common import *
from scipy.linalg import null_space

class ForceSpace:
 def __init__(self,b,mask):
  self.b=b;self.mask=np.asarray(mask,dtype=bool);self.s=Solver(b,'tube-euler');self.groups=np.flatnonzero(mask);self.active=self.mask[np.array(b['groups'])];self.B=self.s.Bf[self.active];self.L=self.s.L[self.active];self.g=np.array([list(self.groups).index(g) for g in np.array(b['groups'])[self.active]])
  self.Z=null_space(self.B.T);self.part=np.linalg.lstsq(self.B.T,self.s.F[self.s.free,0],rcond=None)[0];self.P=np.linalg.pinv(self.B)
  self.r=self.Z.shape[1];ng=len(self.groups);self.cost=np.bincount(self.g,weights=self.L*b['density_lbm_in3'],minlength=ng)
  self.M=np.array([self.Z[self.g==i].T@((self.L[self.g==i]/b['E'])[:,None]*self.Z[self.g==i]) for i in range(ng)])
  self.R=np.array([self.Z[self.g==i].T@(self.L[self.g==i]/b['E']*self.part[self.g==i]) for i in range(ng)])
  self.limits=[(list(self.s.free).index(k),v) for k,v in self.s.limits]
  self.Q0=np.zeros((len(self.limits),ng));self.Qz=np.zeros((len(self.limits),ng,self.r))
  for j,(d,lim) in enumerate(self.limits):
   for i in range(ng):
    ix=self.g==i;coeff=self.P[d,ix]*self.L[ix]/b['E']/lim;self.Q0[j,i]=coeff@self.part[ix];self.Qz[j,i]=coeff@self.Z[ix]
  Kmin=self.B.T@((b['E']*min(b['catalog'])/self.L)[:,None]*self.B);Kmax=Kmin*(max(b['catalog'])/min(b['catalog']));self.eigen_ratio_lower=float(np.linalg.eigvalsh(Kmin)[0]/np.linalg.eigvalsh(Kmax)[-1])
 def evaluate(self,A):
  A=np.atleast_2d(A);inv=1/A;M=np.einsum('ng,gij->nij',inv,self.M);rhs=-inv@self.R
  alpha=np.linalg.solve(M,rhs[...,None])[...,0];forces=self.part[None,:]+alpha@self.Z.T;disp=inv@self.Q0.T+np.einsum('ng,jgr,nr->nj',inv,self.Qz,alpha)
  stress=np.max(abs(forces)/(A[:,self.g]*self.b['stress_limit']),axis=1);du=np.max(abs(disp),axis=1)
  p=self.b['profiles']['tube-euler'];r=p['inner_outer_diameter_ratio'];cap=np.pi*self.b['E']*A[:,self.g]**2*(1+r*r)/(4*(1-r*r)*(p['effective_length_factor']*self.L[None,:])**2*p['buckling_safety_factor'])
  bu=np.max(np.maximum(-forces,0)/cap,axis=1)
  return A@self.cost,np.maximum.reduce([stress,du,bu]),forces,disp

def enumerate_all(batch_size=20000):
 b=load('25bar');initial=incumbent('25bar');model=ForceSpace(b,np.array(initial['areas'])>0);C=np.array(b['catalog']);k=len(model.groups);n=len(C);total=n**k;best=initial['claimed_mass_lbm'];best_c=initial;checked=mass_pruned=accepted=0;near=0;trace=[];start=time.perf_counter()
 assert model.r==2 and k==5
 # Numerical conditioning threshold is satisfied uniformly for the fixed mask.
 assert model.eigen_ratio_lower>b['tolerance']['min_eigenvalue_ratio']
 rng=np.random.default_rng(810)
 crosschecks=[]
 for _ in range(50):
  a=rng.choice(C,k);mass,util,F,D=model.evaluate(a);x=np.zeros(len(initial['areas']));x[model.groups]=a;p=model.s.evaluate(x,True)
  assert abs(mass[0]-p['mass_lbm'])<1e-7
  assert abs(util[0]-max(p['stress_utilization'],p['displacement_utilization'],p['buckling_utilization']))<1e-7
  assert np.allclose(F[0],np.array(p['forces'][0])[model.active],rtol=1e-8,atol=1e-7)
 for offset in range(0,total,batch_size):
  ids=np.arange(offset,min(offset+batch_size,total),dtype=np.int64);idx=np.empty((len(ids),k),int);q=ids.copy()
  for j in range(k):idx[:,j]=q%n;q//=n
  A=C[idx];m=A@model.cost;keep=m<best-1e-7;mass_pruned+=int(sum(~keep))
  if any(keep):
   A=A[keep];m,u,_,_=model.evaluate(A);checked+=len(A);feasible=u<=1+b['tolerance']['constraint'];accepted+=int(sum(feasible));near+=int(sum(abs(u-1)<1e-7))
   if any(feasible):
    which=np.flatnonzero(feasible)[np.argmin(m[feasible])];x=np.zeros(len(initial['areas']));x[model.groups]=A[which];c=candidate(b,'tube-euler',x.tolist());verify(c);best=float(m[which]);best_c=c;trace.append(dict(enumerated=min(offset+batch_size,total),mass_lbm=best,areas=x.tolist()))
  if offset%(batch_size*100)==0:print(min(offset+batch_size,total),total,'best',best,flush=True)
 return dict(method='exhaustive fixed-mask catalogue enumeration using two self-stress coordinates',scope='25bar incumbent topology only',total_combinations=total,mass_pruned=mass_pruned,force_space_evaluated=checked,feasible_improving_candidates=accepted,near_constraint_tolerance_count=near,initial_mass_lbm=initial['claimed_mass_lbm'],mass_lbm=best,candidate=best_c,verification=verify(best_c),self_stress_dimension=model.r,uniform_eigen_ratio_lower_bound=model.eigen_ratio_lower,random_crosschecks=50,trace=trace,elapsed_seconds=time.perf_counter()-start)
if __name__=='__main__':dump('force-enumeration-25bar.json',enumerate_all())

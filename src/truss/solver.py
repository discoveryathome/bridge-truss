"""Primary solver: compatibility matrix, Cholesky displacement solve."""
import numpy as np
from scipy.linalg import cho_factor,cho_solve
from .model import areas,connected
class Solver:
    def __init__(self,b,profile='reference'):
        self.b=b; self.profile=profile; self.p=b['profiles'][profile]
        d=b['dimension']; xyz=np.asarray(b['nodes'],float); edges=np.asarray(b['members'])-1
        delta=xyz[edges[:,1]]-xyz[edges[:,0]]; self.L=np.linalg.norm(delta,axis=1)
        self.B=np.zeros((len(edges),xyz.size))
        for e,(i,j) in enumerate(edges): self.B[e,i*d:(i+1)*d]=-delta[e]/self.L[e]; self.B[e,j*d:(j+1)*d]=delta[e]/self.L[e]
        self.free=np.array([i for i in range(xyz.size) if i//d+1 not in b['fixed_nodes']]); self.Bf=self.B[:,self.free]
        self.F=np.zeros((xyz.size,len(b['loads'])))
        for c,lc in enumerate(b['loads']):
            for row in lc['nodal']: self.F[(row[0]-1)*d:row[0]*d,c]+=row[1:]
        self.limits=[((n-1)*d+k,v) for n,k,v in b['displacement_limits']]
    def evaluate(self,x,full=False):
        b=self.b; a=areas(b,x,self.profile)
        mass=float(np.dot(a,self.L)*b['density_lbm_in3'])
        fail={'valid':False,'mass_lbm':mass,'violation':1e6,'reason':'disconnected or singular'}
        if not connected(b,a): return fail
        k=b['E']*a/self.L; K=self.Bf.T@(k[:,None]*self.Bf)
        try:
            eig=np.linalg.eigvalsh(K)
            if eig[0]<=eig[-1]*b['tolerance']['min_eigenvalue_ratio']: return fail
            u=np.zeros_like(self.F); u[self.free]=cho_solve(cho_factor(K),self.F[self.free])
        except np.linalg.LinAlgError: return fail
        N=k[:,None]*(self.B@u)
        stress=np.divide(N,a[:,None],out=np.zeros_like(N),where=a[:,None]>0)
        su=float(np.max(np.abs(stress))/b['stress_limit'])
        du=max(float(np.max(np.abs(u[i]))/lim) for i,lim in self.limits)
        bu=0.; capacity=np.zeros_like(a)
        if self.p['buckling']:
            r=self.p['inner_outer_diameter_ratio']; I=a*a*(1+r*r)/(4*np.pi*(1-r*r))
            capacity=np.pi**2*b['E']*I/(self.p['effective_length_factor']*self.L)**2/self.p['buckling_safety_factor']
            bu=float(np.max(np.divide(np.maximum(-N,0),capacity[:,None],out=np.zeros_like(N),where=capacity[:,None]>0)))
        internal=self.B.T@N; residual=internal-self.F
        eq=float(np.max(abs(residual[self.free]))/max(1.,np.max(abs(self.F))))
        violation=max(su,du,bu)-1
        valid=violation<=b['tolerance']['constraint'] and eq<=b['tolerance']['equilibrium_relative']
        out=dict(valid=bool(valid),mass_lbm=mass,mass_kg=mass*0.45359237,violation=max(0.,violation),stress_utilization=su,displacement_utilization=du,buckling_utilization=bu,equilibrium_relative=eq,condition_number=float(eig[-1]/eig[0]),reason='ok' if valid else 'constraint violation')
        if full: out.update(displacements=u.T.tolist(),forces=N.T.tolist(),stresses=stress.T.tolist(),reactions=residual.T.tolist(),lengths=self.L.tolist(),member_areas=a.tolist(),buckling_capacities=capacity.tolist())
        return out

from common import *
from force_enumeration import ForceSpace
from truss.independent import check
b=load('25bar');c=incumbent('25bar');model=ForceSpace(b,np.array(c['areas'])>0);rng=np.random.default_rng(81209);errors=[]
for _ in range(100):
 x=np.zeros(8);x[model.groups]=rng.choice(b['catalog'],len(model.groups));mass,util,N,D=model.evaluate(x[model.groups]);other=check(b,x.tolist(),'tube-euler')
 force_error=float(np.max(abs(N[0]-np.array(other['forces'][0])[model.active])));disp=np.array(other['displacements'][0])[model.s.free];want=np.array([disp[i]/lim for i,lim in model.limits]);disp_error=float(max(abs(D[0]-want)));u=max(other['stress_utilization'],other['displacement_utilization'],other['buckling_utilization']);uerr=abs(float(util[0])-u)
 assert force_error<1e-6 and disp_error<1e-9 and uerr<1e-6
 errors.append([force_error,disp_error,uerr])
r=dict(status='PASS',random_cases=100,seed=81209,max_force_absolute_lbf=float(np.max(np.array(errors)[:,0])),max_normalized_displacement_absolute=float(np.max(np.array(errors)[:,1])),max_utilization_absolute=float(np.max(np.array(errors)[:,2])),checker='Untouched independent pure-Python stiffness assembly and pivoted solve; shared frozen inputs only')
dump('force-space-independent-audit.json',r);print(json.dumps(r,indent=2))

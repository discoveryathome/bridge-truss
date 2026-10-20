"""Predeclared bounded follow-up to unresolved 20-second subproblems.
No changes to model or verifier; keep initial timeout results."""
from common import *
from force_mip import solve
old=json.loads((OUT/'force-mip-10bar.json').read_text());results=[]
for item in old['results']:
 if item['status']!=1:continue
 r=solve('10bar',item['mask'],seconds=120,cutoff=incumbent('10bar')['claimed_mass_lbm']);results.append(r)
 dump('force-mip-10bar-extended-progress.json',dict(results=results,scope='120-second follow-up of unresolved fixed topologies; not a global certificate unless all cases close.'))
 print(r['mask'],'status',r['status'],'mass',r.get('mass_lbm'),'bound',r.get('solver_bound'),'seconds',r.get('seconds'),flush=True)
dump('force-mip-10bar-extended.json',dict(results=results,scope='120-second follow-up of unresolved fixed topologies; not a global certificate unless all cases close.'))

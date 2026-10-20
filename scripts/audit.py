import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from truss.model import load
from truss.solver import Solver
p=argparse.ArgumentParser();p.add_argument('mode',choices=['sources','transfer']);a=p.parse_args()
if a.mode=='sources':
 for case in ['10bar','25bar']:
  b=load(case)
  for label in ['published','published_disputed','additional_published']:
   if label in b:
    c=b[label];r=Solver(b).evaluate(c['areas']);print(case,label,json.dumps(dict(reported_mass_lbm=c['mass_lbm'],computed_mass_lbm=r['mass_lbm'],feasible=r['valid'],displacement_utilization=r['displacement_utilization'])))
 s=json.loads((ROOT/'docs/72bar-survey.json').read_text()); print('72bar mass-only audit',s['recomputed_mass_lbm'],s['status'])
else:
 for path in sorted((ROOT/'results').glob('*topology-verification.json')):
  r=json.loads(path.read_text()); q=r['primary']; print(r['case'],json.dumps({k:q[k] for k in ['mass_kg','stress_utilization','displacement_utilization','buckling_utilization','condition_number']}))
 print('Transfer obligations: self-weight/load envelope; local/global buckling; imperfections; connections; fabrication; design-code review; physical validation. No construction certification.')

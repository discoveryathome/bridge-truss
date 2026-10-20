"""Fast verification of stored results; no optimization and no network."""
import argparse,json,sys,unittest,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from truss.verify import verify,candidate
from truss.model import load
p=argparse.ArgumentParser();p.add_argument('--case',choices=['10bar','25bar']);p.add_argument('--tests-only',action='store_true');a=p.parse_args();start=time.perf_counter()
suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
if not unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful(): sys.exit(1)
if a.tests_only: sys.exit(0)
rows=json.loads((ROOT/'results/summary.json').read_text()); verified=0
for row in rows:
 if a.case and row['case']!=a.case: continue
 stem=f"{row['case']}-{row['variant']}"; c=json.loads((ROOT/'results'/f'{stem}-winner.json').read_text()); r=verify(c); mass=r['primary']['mass_lbm']
 assert abs(mass-row['mass_lbm'])<1e-7
 before=verify(json.loads((ROOT/'results'/f'{stem}-before.json').read_text()))['primary']['mass_lbm']
 assert abs(before-row['before_mass_lbm'])<1e-7
 assert abs(100*(1-mass/before)-row['savings_percent'])<1e-8
 stored=json.loads((ROOT/'results'/f'{stem}-verification.json').read_text())
 import numpy as np
 for engine in ['primary','independent']:
  for field in ['mass_lbm','forces','displacements','reactions','stress_utilization','displacement_utilization','buckling_utilization']:
   np.testing.assert_allclose(r[engine][field],stored[engine][field],rtol=1e-8,atol=1e-8)
 runs=list((ROOT/'results').glob(f'{stem}-seed*.json')); values=[]
 for path in runs:
  run=json.loads(path.read_text()); rr=verify(run['candidate']); values.append(rr['primary']['mass_lbm']);verified+=1
 assert abs(mass-min(values))<1e-8
 assert sorted(values)==sorted(row['run_masses_lbm'])
 print(f"PASS {stem}: {mass:.9f} lbm, {row['savings_percent']:.4f}% savings; {len(runs)} seeds")
print(f'PASS: {verified} stored search results; both implementations; elapsed {time.perf_counter()-start:.3f}s')

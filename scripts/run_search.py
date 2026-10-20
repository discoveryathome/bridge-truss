import argparse,json,sys,platform
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from truss.model import load
from truss.search import search
from truss.verify import candidate,verify
p=argparse.ArgumentParser(); p.add_argument('--iterations',type=int,default=120); p.add_argument('--seeds',nargs='+',type=int,default=[17,42,2026]); p.add_argument('--output',default='results'); p.add_argument('--case',choices=['10bar','25bar']);args=p.parse_args()
out=Path(args.output);out.mkdir(exist_ok=True,parents=True)
rows=[]
for case in ([args.case] if args.case else ['10bar','25bar']):
 b=load(case)
 for profile,removal,label in [('reference',False,'reference'),('tube-euler',False,'tube-sizing'),('tube-euler',True,'tube-topology')]:
  runs=[]
  for seed in args.seeds:
   r=search(b,profile,seed,args.iterations,removal); runs.append(r)
   (out/f'{case}-{label}-seed{seed}.json').write_text(json.dumps(r,indent=2)+'\n')
   print(case,label,seed,round(r['candidate']['claimed_mass_lbm'],6),r['counts'],flush=True)
  winner=min(runs,key=lambda r:r['candidate']['claimed_mass_lbm'])
  path=out/f'{case}-{label}-winner.json'; path.write_text(json.dumps(winner['candidate'],indent=2)+'\n')
  (out/f'{case}-{label}-verification.json').write_text(json.dumps(winner['verification'],indent=2)+'\n')
  before=candidate(b,profile,b['published']['areas'] if profile=='reference' else [max(b['catalog'])]*(max(b['groups'])+1))
  before_report=verify(before); (out/f'{case}-{label}-before.json').write_text(json.dumps(before,indent=2)+'\n')
  before_mass=before_report['primary']['mass_lbm']; after=winner['candidate']['claimed_mass_lbm']
  rows.append(dict(case=case,variant=label,mass_lbm=after,mass_kg=after*.45359237,before_mass_lbm=before_mass,savings_percent=100*(1-after/before_mass),seed=winner['seed'],by='Local pilot / Codex',source=str(path),updated='2026-10-20',object=str(path),run_masses_lbm=[r['candidate']['claimed_mass_lbm'] for r in runs]))
(out/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
(out/'environment.json').write_text(json.dumps(dict(python=sys.version,platform=platform.platform(),seeds=args.seeds,iterations=args.iterations),indent=2)+'\n')

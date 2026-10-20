from common import *
from collections import defaultdict

def summarize():
 runs=[]
 for prefix in ['baseline-','hybrid-']:
  for f in sorted(OUT.glob(prefix+'*.json')):
   r=json.loads(f.read_text());r['artifact']=f.name;r.setdefault('variant','tube-topology');runs.append(r)
 assert len(runs)==44
 groups=defaultdict(list)
 for r in runs:groups[(r['candidate']['case'],r['variant'])].append(r)
 rows=[]
 for (case,variant),rr in sorted(groups.items()):
  rows.append(dict(case=case,variant=variant,runs=len(rr),initial_mass_lbm=rr[0]['initial_mass_lbm'],best_mass_lbm=min(r['mass_lbm'] for r in rr),improving_runs=sum(r['savings_percent']>1e-8 for r in rr),total_structural_solves=sum(r['discrete_evaluations']+r['continuous_solves'] for r in rr)))
 ex=json.loads((OUT/'extension-individual-25bar.json').read_text())
 stage2=[json.loads(f.read_text()) for f in sorted(OUT.glob('extension-stage2-*.json'))]
 continuations=[json.loads(f.read_text()) for f in sorted(OUT.glob('extension-continuation-*.json'))]
 return dict(original_case_rows=rows,original_run_count=len(runs),original_structural_solves=sum(r['discrete_evaluations']+r['continuous_solves'] for r in runs),original_improving_runs=sum(r['savings_percent']>1e-8 for r in runs),extension_initial_mass_lbm=ex['initial_mass_lbm'],extension_greedy_mass_lbm=ex['mass_lbm'],extension_savings_percent=ex['savings_percent'],extension_continuation_runs=len(continuations),extension_continuation_improving_runs=sum(r['savings_percent']>1e-8 for r in continuations),extension_continuation_best_mass_lbm=min([ex['mass_lbm']]+[r['mass_lbm'] for r in continuations]),extension_stage2_runs=len(stage2),extension_stage2_improving_runs=sum(r['savings_percent']>1e-8 for r in stage2),extension_stage2_structural_solves=sum(r['discrete_evaluations']+r['continuous_solves'] for r in stage2),extension_total_savings_percent=100*(1-min([ex['mass_lbm']]+[r['mass_lbm'] for r in continuations+stage2])/ex['initial_mass_lbm']),case_scope='The individual-member extension changes grouping; no cross-model benchmark record.',evidence_level='author-checked')
if __name__=='__main__':
 r=summarize();dump('trial-summary.json',r);print(json.dumps(r,indent=2))

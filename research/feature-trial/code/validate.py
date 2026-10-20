"""Recompute all saved accepted candidates and improving trace points.
This fast check is not a rerun of the full searches or exhaustive enumeration.
"""
from common import *
from extension import verify_extension, model, EXT
from summarize import summarize
from topology_audit import audit
import hashlib

def main():
 checked=traces=0
 for path in sorted(OUT.glob('*.json')):
  data=json.loads(path.read_text())
  def walk(obj):
   nonlocal checked,traces
   if isinstance(obj,dict):
    if 'candidate' in obj and 'verification' in obj:
     c=obj['candidate'];fn=verify_extension if c['case']=='25bar-individual' else verify;fresh=fn(c)
     saved=obj['verification'];assert abs(fresh['primary']['mass_lbm']-saved['primary']['mass_lbm'])<1e-7,(path,'saved mass')
     for engine in ['primary','independent']:
      assert saved[engine]['valid'] and fresh[engine]['valid'],path
      for key in ['forces','displacements','reactions','stress_utilization','displacement_utilization','buckling_utilization']:
       assert np.allclose(saved[engine][key],fresh[engine][key],rtol=1e-8,atol=1e-7),(path,key)
     checked+=1
     for point in obj.get('trace',[]):
      if 'areas' not in point:continue
      trial=dict(c,areas=point['areas']);trial.pop('claimed_mass_lbm',None);v=fn(trial)
      assert abs(v['primary']['mass_lbm']-point['mass_lbm'])<1e-7,(path,'trace mass');traces+=1
    for value in obj.values():walk(value)
   elif isinstance(obj,list):
    for value in obj:walk(value)
  walk(data)
 for name in ['before.json','winner.json','best-verified.json']:
  verify_extension(json.loads((EXT/name).read_text()))
 ranks={}
 for case in ['10bar','25bar']:
  r=audit(case);saved=json.loads((OUT/f'topology-audit-{case}.json').read_text());assert r==saved,case;ranks[case]=r['full_rank_masks']
 summary=summarize();assert summary['original_run_count']==44 and summary['original_structural_solves']==528000 and summary['original_improving_runs']==0
 for prefix in ['baseline-','hybrid-','extension-continuation-','extension-stage2-']:
  for path in OUT.glob(prefix+'*.json'):
   r=json.loads(path.read_text());assert r['discrete_evaluations']+r['continuous_solves']==12000,path
 result=dict(status='PASS',candidate_reports_recomputed=checked,improving_trace_points_recomputed=traces,exact_rank_audits=ranks,summary=summary,limitations='Author check only. Does not independently review physics, prove global optimality, or rerun long searches.')
 print(json.dumps(result,indent=2));return result
if __name__=='__main__':main()

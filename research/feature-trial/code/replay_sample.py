"""Replay one successful extension strategy from the same start without
changing any saved result. Candidate, budget counts and mass trace must match.
"""
from common import *
from extension import model,verify_extension
from hybrid import run
if __name__=='__main__':
 initial=json.loads((OUT/'extension-individual-25bar.json').read_text())['candidate']
 saved=json.loads((OUT/'extension-continuation-hybrid-101.json').read_text())
 result=run('25bar-individual',101,12000,initial_override=initial,model_override=model(),checker=verify_extension)
 assert result['candidate']==saved['candidate']
 for key in ['discrete_evaluations','continuous_solves','cache_hits']:
  assert result[key]==saved[key],key
 assert [(r['evaluation'],r['mass_lbm'],r['areas']) for r in result['trace']]==[(r['evaluation'],r['mass_lbm'],r['areas']) for r in saved['trace']]
 print(json.dumps(dict(status='PASS',candidate=result['candidate'],evaluations=result['discrete_evaluations']+result['continuous_solves'],elapsed_seconds=result['elapsed_seconds'],reproduced='candidate, discrete/continuous counts, cache hits, complete improvement trace'),indent=2))

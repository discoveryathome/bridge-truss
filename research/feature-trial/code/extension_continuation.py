"""Independent seeded continuation of the separate ungrouped scope probe.
Budgets match main trial. No result belongs to the original benchmark frontier.
"""
from common import *
import baseline, hybrid
from extension import model, verify_extension, EXT
if __name__=='__main__':
 b=model();initial=json.loads((EXT/'winner.json').read_text())
 for method,module in [('baseline',baseline),('hybrid',hybrid)]:
  for seed in [101,303,505]:
   r=module.run(b['id'],seed,12000,initial_override=initial,model_override=b,checker=verify_extension)
   r['scope']='separate individual-member model; continuation from greedy winner'
   dump(f'extension-continuation-{method}-{seed}.json',r)
   print(method,seed,r['initial_mass_lbm'],r['mass_lbm'],r['savings_percent'],r['elapsed_seconds'],flush=True)

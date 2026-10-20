"""Second sequential contributor round, from the first hybrid result."""
from common import *
import baseline, hybrid
from extension import model, verify_extension
if __name__=='__main__':
 b=model();initial=json.loads((OUT/'extension-continuation-hybrid-101.json').read_text())['candidate']
 for method,module in [('baseline',baseline),('hybrid',hybrid)]:
  for seed in [101,303,505]:
   r=module.run(b['id'],seed,12000,initial_override=initial,model_override=b,checker=verify_extension)
   r['scope']='separate individual-member model; second sequential round from first hybrid winner'
   dump(f'extension-stage2-{method}-{seed}.json',r)
   print(method,seed,r['initial_mass_lbm'],r['mass_lbm'],r['savings_percent'],r['elapsed_seconds'],flush=True)

from common import *
import baseline,hybrid
if __name__=='__main__':
 for case in ['10bar','25bar']:
  for variant in ['reference','tube-sizing']:
   for seed in [101,303,505]:
    for method,runner in [('baseline',baseline.run),('hybrid',hybrid.run)]:
     r=runner(case,seed,12000,variant)
     assert all(a>0 for a in r['candidate']['areas'])
     dump(f'{method}-{case}-{variant}-{seed}.json',r)
     print(case,variant,seed,method,r['mass_lbm'],r['savings_percent'],r['elapsed_seconds'],flush=True)

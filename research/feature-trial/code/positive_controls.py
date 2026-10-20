from common import *
import baseline,hybrid
for case in ['10bar','25bar']:
 initial=json.loads((ROOT/'results'/f'{case}-tube-topology-seed42.json').read_text())['candidate']
 for method,runner in [('baseline',baseline.run),('hybrid',hybrid.run)]:
  r=runner(case,707,12000,initial_override=initial)
  r['note']='Positive control from a weaker pre-existing seed42 design; improvement does NOT count as a new frontier result.'
  r['beats_original_frontier']=r['mass_lbm']<incumbent(case)['claimed_mass_lbm']-1e-7
  dump(f'positive-control-{method}-{case}.json',r);print(method,case,r['initial_mass_lbm'],r['mass_lbm'],r['savings_percent'],flush=True)

"""Cross-check proposal physics and numerical reformulation witnesses."""
from common import *
from hybrid import Relax
from determinate import solve_pattern
import unittest
class MethodsTests(unittest.TestCase):
 def test_continuous_reduces_to_original_fe(self):
  rng=np.random.default_rng(905)
  for case in ['10bar','25bar']:
   b=load(case);initial=incumbent(case);ev=Evaluator(b,initial,10000)
   for _ in range(15):
    x=rng.choice(b['catalog'],len(initial['areas']));rel=Relax(ev,[True]*len(x));mass,margins=rel.calc(x)
    original=ev.solver.evaluate(x)
    self.assertAlmostEqual(mass,original['mass_lbm'],places=9)
    util=max(original['stress_utilization'],original['displacement_utilization'],original['buckling_utilization'])
    self.assertAlmostEqual(1-float(min(margins)),util,places=8)
 def test_determinate_independence(self):
  b=load('10bar');initial=incumbent('10bar');active=np.flatnonzero(initial['areas']);s=Solver(b,'tube-euler')
  calculated=np.linalg.solve(s.Bf[active].T,s.F[s.free])[:,0]
  for values in [initial['areas'],[max(b['catalog']) if i in active else 0 for i in range(10)]]:
   original=s.evaluate(values,True)
   np.testing.assert_allclose(calculated,np.array(original['forces'][0])[active],atol=1e-7,rtol=1e-10)
 def test_determinate_known_optimum(self):
  b=load('10bar');initial=incumbent('10bar');r=solve_pattern(b,np.flatnonzero(initial['areas']),time_limit=3)
  self.assertEqual(r['status'],0);self.assertTrue(r['verification']['primary']['valid'])
  self.assertAlmostEqual(r['mass_lbm'],initial['claimed_mass_lbm'],places=7)
  self.assertLess(r['gap'],1e-8)
 def test_mechanism_excluded(self):
  b=load('10bar');r=solve_pattern(b,[0,1,2,3,4,5,6,7]);self.assertEqual(r['status'],'mechanism')
if __name__=='__main__':unittest.main()

import copy,unittest
import numpy as np
from truss.model import load
from truss.solver import Solver
from truss.independent import check
from truss.verify import verify,candidate
class StructuralTests(unittest.TestCase):
 def test_published_replication(self):
  for name in ['10bar','25bar']:
   b=load(name); r=verify(candidate(b,'reference',b['published']['areas']))
   self.assertAlmostEqual(r['primary']['mass_lbm'],b['published']['mass_lbm'],delta=.02)
 def test_tenbar_later_design(self):
  b=load('10bar'); p=b['additional_published']; r=verify(candidate(b,'reference',p['areas']))
  self.assertAlmostEqual(r['primary']['mass_lbm'],p['mass_lbm'],delta=.02)
 def test_disputed_25bar(self):
  b=load('25bar'); p=b['published_disputed']; r=Solver(b).evaluate(p['areas'])
  self.assertFalse(r['valid']); self.assertAlmostEqual(p['mass_lbm']-r['mass_lbm'],1.5013558039)
 def test_single_bar_analytical(self):
  b=load('10bar'); b.update(nodes=[[0,0],[10,0]],members=[[1,2]],groups=[0],fixed_nodes=[1],loads=[{'nodal':[[2,1000,0]]}],displacement_limits=[[2,0,2]])
  # 2D axial bar has a transverse mechanism and must be rejected even for axial load.
  self.assertFalse(Solver(b).evaluate([1.62])['valid'])
  with self.assertRaises(ValueError): check(b,[1.62],'reference')
  b.update(dimension=1,nodes=[[0],[10]],loads=[{'nodal':[[2,1000]]}])
  a=Solver(b).evaluate([1.62],True); z=check(b,[1.62],'reference')
  self.assertAlmostEqual(a['displacements'][0][1],1000*10/(1e7*1.62)); self.assertAlmostEqual(z['forces'][0][0],1000)
 def test_buckling_analytical(self):
  b=load('10bar'); b.update(dimension=1,nodes=[[0],[360]],members=[[1,2]],groups=[0],fixed_nodes=[1],loads=[{'nodal':[[2,-10000]]}],displacement_limits=[[2,0,2]])
  r=Solver(b,'tube-euler').evaluate([1.62]); z=check(b,[1.62],'tube-euler')
  I=1.62**2*(1+.9**2)/(4*np.pi*(1-.9**2)); expected=10000/(np.pi**2*1e7*I/360**2/1.5)
  self.assertAlmostEqual(r['buckling_utilization'],expected); self.assertAlmostEqual(z['buckling_utilization'],expected); self.assertFalse(r['valid'])
 def test_disconnected(self):
  b=load('25bar'); self.assertFalse(Solver(b,'tube-euler').evaluate([0]*8)['valid'])
  with self.assertRaises(ValueError): check(b,[0]*8,'tube-euler')
 def test_bad_inputs(self):
  b=load('10bar')
  for x in [[float('nan')]*10,[-1]*10,[2.01]*10,[1.62]*9,[0]*10]:
   with self.assertRaises(ValueError): Solver(b).evaluate(x)
 def test_wrong_claim_and_model(self):
  b=load('10bar'); c=candidate(b,'reference',b['published']['areas']); c['claimed_mass_lbm']=1
  with self.assertRaises(ValueError): verify(c)
  del c['claimed_mass_lbm']; c['model_sha256']='bad'
  with self.assertRaises(ValueError): verify(c)
 def test_overstress_displacement(self):
  b=load('10bar'); r=Solver(b).evaluate([1.62]*10)
  self.assertFalse(r['valid']); self.assertGreater(r['stress_utilization'],1); self.assertGreater(r['displacement_utilization'],1)
 def test_load_scaling_and_multiple_cases(self):
  b=load('25bar'); x=[3.4]*8; r=Solver(b).evaluate(x,True)
  lc=copy.deepcopy(b['loads'][0]); lc['nodal']=[[n,*[2*v for v in vals]] for n,*vals in lc['nodal']]; b['loads'].append(lc)
  p=Solver(b).evaluate(x,True); z=check(b,x,'reference')
  np.testing.assert_allclose(p['forces'][1],2*np.array(r['forces'][0]),atol=1e-8)
  np.testing.assert_allclose(z['displacements'],p['displacements'],atol=1e-10)
 def test_orientation_invariance(self):
  b=load('10bar'); x=b['published']['areas']; p=Solver(b).evaluate(x,True); b['members']=[list(reversed(e)) for e in b['members']]
  z=Solver(b).evaluate(x,True); np.testing.assert_allclose(p['forces'],z['forces'],atol=1e-8)
 def test_random_crosscheck(self):
  rng=np.random.default_rng(20261020)
  for name in ['10bar','25bar']:
   b=load(name)
   for _ in range(20):
    x=rng.choice(b['catalog'],size=max(b['groups'])+1).tolist(); p=Solver(b,'tube-euler').evaluate(x,True); z=check(b,x,'tube-euler')
    self.assertEqual(p['valid'],z['valid']); np.testing.assert_allclose(p['forces'],z['forces'],rtol=1e-8,atol=1e-7)
if __name__=='__main__': unittest.main()

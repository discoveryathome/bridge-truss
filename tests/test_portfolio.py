import copy,importlib.util,json,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from prepare_portfolio import verify,OUT
class PortfolioTests(unittest.TestCase):
 def test_all_models_and_wrong_model_rejection(self):
  rows=json.loads((OUT/'portfolio.json').read_text())['frontier']
  self.assertEqual(len(rows),8)
  for row in rows:
   c=json.loads((ROOT/row['object']).read_text());verify(c)
   bad=copy.deepcopy(c);bad['model_sha256']='0'*64
   with self.assertRaises(ValueError):verify(bad)
   bad=copy.deepcopy(c);bad['claimed_mass_lbm']=0
   with self.assertRaises(ValueError):verify(bad)
if __name__=='__main__':unittest.main()

import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from truss.model import load
from truss.solver import Solver
from truss.independent import check
for case in ['10bar','25bar']:
 b=load(case)
 for profile in ['reference','tube-euler']:
  for label,x in [('published',b['published']['areas']),('max',[max(b['catalog'])]*(max(b['groups'])+1))]:
   print(case,profile,label,Solver(b,profile).evaluate(x))
   print('independent',check(b,x,profile)['valid'])

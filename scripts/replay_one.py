"""Re-run a stored experiment without changing results; compare its actual search output."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from truss.model import load
from truss.search import search
p=argparse.ArgumentParser();p.add_argument('run');a=p.parse_args();old=json.loads(Path(a.run).read_text());c=old['candidate']
new=search(load(c['case']),c['profile'],old['seed'],old['iterations'],old['removal'])
assert new['candidate']==c,(new['candidate'],c)
assert new['counts']==old['counts'],(new['counts'],old['counts'])
assert new['trace']==old['trace'],'Trace differs'
print('PASS deterministic search replay: identical candidate, evaluation counts and trace; elapsed',new['elapsed_seconds'])

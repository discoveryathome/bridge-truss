import argparse,hashlib,json,secrets
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--seed');a=p.parse_args();seed=a.seed or secrets.token_hex(16)
if len(seed)!=32 or any(c not in '0123456789abcdefABCDEF' for c in seed): p.error('seed must have 32 hex digits')
c=json.loads((Path(__file__).resolve().parents[1]/'discover/catalog.json').read_text());n=int(seed[:8],16)%sum(t['weight'] for t in c['tracks'])
for t in c['tracks']:
 if n<t['weight']: break
 n-=t['weight']
task=t['tasks'][int(seed[8:16],16)%len(t['tasks'])]
print(json.dumps(dict(seed=seed,track=t['id'],task=task,overlap_check='Read the Handoffs thread (https://github.com/discoveryathome/bridge-truss/discussions/3), discover/messages and discover/ledger.md before claiming'),indent=2))

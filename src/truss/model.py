import hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
def load(case):
    path=ROOT/'benchmarks'/f'{case}.json'
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    lock=json.loads((ROOT/'benchmarks/LOCK.sha256.json').read_text())
    if digest != lock[path.name]: raise ValueError('Frozen benchmark hash mismatch')
    b=json.loads(path.read_text()); b['sha256']=digest
    return b

def areas(b,x,profile):
    a=np.asarray(x,dtype=float)
    if a.shape != (max(b['groups'])+1,) or not np.isfinite(a).all(): raise ValueError('Invalid area vector')
    allowed=b['catalog']+([0.] if b['profiles'][profile]['allow_removal'] else [])
    if any(not any(abs(v-c)<1e-10 for c in allowed) for v in a): raise ValueError('Area outside frozen catalogue')
    return a[np.asarray(b['groups'])]

def connected(b,a):
    adj=[set() for _ in b['nodes']]
    for (i,j),v in zip(b['members'],a):
        if v>0: adj[i-1].add(j-1); adj[j-1].add(i-1)
    seen={n-1 for n in b['fixed_nodes']}; stack=list(seen)
    while stack:
        for j in adj[stack.pop()]-seen: seen.add(j); stack.append(j)
    return len(seen)==len(adj) # all original nodes retained, including unloaded nodes

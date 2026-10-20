import json
import numpy as np
from .model import load
from .solver import Solver
from .independent import check

def verify(candidate):
    b=load(candidate['case']); profile=candidate['profile']
    if candidate['model_sha256']!=b['sha256']: raise ValueError('candidate model hash mismatch')
    primary=Solver(b,profile).evaluate(candidate['areas'],full=True)
    if not primary['valid']: raise ValueError('primary rejection: '+primary['reason'])
    other=check(b,candidate['areas'],profile)
    if not other['valid']: raise ValueError('independent rejection')
    errors={}
    for key in ['mass_lbm','displacements','forces','reactions','stress_utilization','displacement_utilization','buckling_utilization']:
        a=np.asarray(primary[key]); c=np.asarray(other[key]); errors[key]=float(np.max(abs(a-c))/max(1.,float(np.max(abs(a)))))
        if errors[key]>b['tolerance']['agreement_relative']: raise ValueError('solver disagreement: '+key)
    if 'claimed_mass_lbm' in candidate and abs(candidate['claimed_mass_lbm']-primary['mass_lbm'])>1e-7: raise ValueError('incorrect mass claim')
    return dict(case=b['id'],profile=profile,model_sha256=b['sha256'],primary=primary,independent=other,solver_relative_differences=errors,evidence_level='author-checked',claim_kind='model')

def candidate(b,profile,x):
    return dict(case=b['id'],profile=profile,model_sha256=b['sha256'],areas=list(x))

"""Exact integer row-rank audit of every grouped topology. Direction vectors
may be scaled by nonzero member lengths without changing rank, so rational
coordinates permit integer arithmetic. No floating-point rank decisions."""
from common import *
from itertools import product
from fractions import Fraction
from math import gcd,lcm

def exact_rank(rows,ncol):
 A=[list(row) for row in rows];rank=0
 for col in range(ncol):
  pivot=next((i for i in range(rank,len(A)) if A[i][col]),None)
  if pivot is None:continue
  A[rank],A[pivot]=A[pivot],A[rank];p=A[rank][col]
  for i in range(rank+1,len(A)):
   a=A[i][col]
   if not a:continue
   A[i]=[p*x-a*y for x,y in zip(A[i],A[rank])];div=0
   for v in A[i]:div=gcd(div,abs(v))
   if div>1:A[i]=[v//div for v in A[i]]
  rank+=1
  if rank==len(A):break
 return rank

def audit(case):
 b=load(case);d=b['dimension'];s=Solver(b,'tube-euler');xyz=[[Fraction(str(v)) for v in row] for row in b['nodes']];integer_rows=[]
 for ni,nj in b['members']:
  delta=[v-w for v,w in zip(xyz[nj-1],xyz[ni-1])];row=[Fraction(0)]*(len(xyz)*d)
  for k,v in enumerate(delta):row[(ni-1)*d+k]=-v;row[(nj-1)*d+k]=v
  rr=[row[k] for k in s.free];den=lcm(*(v.denominator for v in rr));integer_rows.append([int(v*den) for v in rr])
 ng=max(b['groups'])+1;records=[]
 for bits in product([False,True],repeat=ng):
  selected=[e for e,g in enumerate(b['groups']) if bits[g]];rank=exact_rank([integer_rows[e] for e in selected],len(s.free));rec=dict(mask=list(bits),members=len(selected),rank=rank,full_rank=rank==len(s.free))
  if rec['full_rank']:
   B=s.Bf[selected];L=s.L[selected];Kmin=B.T@((b['E']*min(b['catalog'])/L)[:,None]*B);Kmax=Kmin*(max(b['catalog'])/min(b['catalog']));rec['uniform_eigen_ratio_lower']=float(np.linalg.eigvalsh(Kmin)[0]/np.linalg.eigvalsh(Kmax)[-1]);assert rec['uniform_eigen_ratio_lower']>b['tolerance']['min_eigenvalue_ratio']
  records.append(rec)
 return dict(case=case,method='exact integer row elimination on unnormalized compatibility rows',scope='rank of linear restrained stiffness, not physical safety; positive catalogue areas on retained groups',total_masks=len(records),full_rank_masks=sum(r['full_rank'] for r in records),free_dofs=len(s.free),records=records)
if __name__=='__main__':
 for case in ['10bar','25bar']:
  r=audit(case);dump(f'topology-audit-{case}.json',r);print(case,r['total_masks'],r['full_rank_masks'],flush=True)

import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.cm import ScalarMappable
import numpy as np
from truss.verify import verify
from truss.model import load
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titleweight':'bold','figure.facecolor':'#f6f8fb','axes.facecolor':'#f6f8fb','text.color':'#152238'})
rows=json.loads((ROOT/'results/summary.json').read_text())
for row in rows:
 if row['variant']=='tube-sizing':continue
 case=row['case'];variant=row['variant'];b=load(case); reports=[]
 for tag in ['before','winner']:
  c=json.loads((ROOT/'results'/f'{case}-{variant}-{tag}.json').read_text()); reports.append(verify(c)['primary'])
 xyz=np.array(b['nodes']);d=b['dimension']; vmax=max(np.max(np.abs(r['forces']))/1000 for r in reports); norm=TwoSlopeNorm(vmin=-vmax,vcenter=0,vmax=vmax);cmap=plt.get_cmap('coolwarm')
 fig=plt.figure(figsize=(14,6.6));gs=fig.add_gridspec(1,2,left=.04,right=.90,top=.73,bottom=.14,wspace=.06)
 for col,(tag,r) in enumerate(zip(['BEFORE','AFTER'],reports)):
  ax=fig.add_subplot(gs[0,col],projection='3d' if d==3 else None)
  forces=np.array(r['forces'][0])/1000
  for e,((i,j),A,N) in enumerate(zip(b['members'],r['member_areas'],forces)):
   xy=xyz[[i-1,j-1]]
   if A==0: ax.plot(*xy.T,color='#b8c0cc',lw=.8,ls=':');continue
   ax.plot(*xy.T,color=cmap(norm(N)),lw=1+4*np.sqrt(A/max(b['catalog'])),solid_capstyle='round')
   if d==2:
    mid=xy.mean(axis=0);offset=np.array([0,14]) if e<6 else np.array([0,10 if e%2 else -18]);ax.text(*(mid+offset),f'{e+1}: {N:+.1f}',ha='center',fontsize=8,bbox={'facecolor':'#f6f8fb','alpha':.8,'edgecolor':'none','pad':1})
  ax.scatter(*xyz.T,color='#152238',s=18,depthshade=False) if d==3 else ax.scatter(*xyz.T,color='#152238',s=25,zorder=5)
  for i,point in enumerate(xyz):
   if d==3: ax.text(*point,str(i+1),fontsize=9)
   else: ax.text(point[0]+8,point[1]+17,str(i+1),fontsize=9)
  sup=xyz[np.array(b['fixed_nodes'])-1];ax.scatter(*sup.T,marker='^',s=90,color='#152238')
  for node_load in b['loads'][0]['nodal']:
   pos=xyz[node_load[0]-1];F=np.array(node_load[1:]);vec=F/max(np.max(np.abs(F)),1)* (38 if d==3 else 70)
   if d==3: ax.quiver(*pos,*vec,color='#111827',arrow_length_ratio=.25,linewidth=1.2)
   else: ax.annotate('',xy=pos+vec,xytext=pos,arrowprops=dict(arrowstyle='->',color='#111827',lw=1.8))
  fig.text(.25 if col==0 else .69,.79,f'{tag}  |  {r["mass_lbm"]:,.2f} lbm\n{r["mass_kg"]:,.2f} kg',ha='center',fontsize=13,fontweight='bold')
  if d==2: ax.set_aspect('equal');ax.set_xlim(-60,820);ax.set_ylim(-110,430);ax.axis('off')
  else: ax.view_init(elev=19,azim=-60);ax.set_box_aspect([1,1,1]);ax.set_xlabel('X (in)');ax.set_ylabel('Y (in)');ax.set_zlabel('Z (in)');ax.set_xticks([-100,0,100]);ax.set_yticks([-100,0,100]);ax.set_zticks([0,100,200]);ax.grid(False)
 cax=fig.add_axes([.93,.25,.016,.42]);fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=cax,label='Axial force (kip): + tension / − compression')
 heading='Historical sizing model' if variant=='reference' else 'Frozen tube / Euler model'
 fig.suptitle(f'{case.upper()}   /   {heading}   /   {row["savings_percent"]:.2f}% material savings',x=.045,ha='left',y=.965,fontsize=20,fontweight='bold')
 baseline='published feasible design' if variant=='reference' else 'feasible uniform maximum-area design'
 fig.text(.045,.88,f'Compared with {baseline}. Fixed nodes and candidate members; load case 1.',fontsize=11)
 fig.text(.045,.055,'Line width indicates area  •  Dotted members removed  •  Triangles: supports  •  Arrows: applied loads\nModel-validated research only. Not certified for construction.',fontsize=10,color='#435068')
 fig.savefig(ROOT/'results'/f'{case}-{variant}.png',dpi=170);fig.savefig(ROOT/'results'/f'{case}-{variant}.svg');plt.close(fig)
# Complete, machine-readable engineering schedules for each winning design.
for row in rows:
 stem=f"{row['case']}-{row['variant']}";b=load(row['case']);r=json.loads((ROOT/'results'/f'{stem}-verification.json').read_text())['primary']
 with (ROOT/'results'/f'{stem}-members.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['member','node_i','node_j','group','area_in2','length_in','force_lbf','stress_psi','buckling_capacity_lbf','state'])
  for e,((i,j),g,A,L,N,s,cap) in enumerate(zip(b['members'],b['groups'],r['member_areas'],r['lengths'],r['forces'][0],r['stresses'][0],r['buckling_capacities']),1): w.writerow([e,i,j,g,A,L,N,s,cap,'removed' if A==0 else ('tension' if N>=0 else 'compression')])
 with (ROOT/'results'/f'{stem}-nodes.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['node','direction','displacement_in','reaction_or_free_residual_lbf'])
  for n in range(len(b['nodes'])):
   for d in range(b['dimension']): k=n*b['dimension']+d;w.writerow([n+1,'XYZ'[d],r['displacements'][0][k],r['reactions'][0][k]])
fig,axs=plt.subplots(1,2,figsize=(13,4.8));fig.subplots_adjust(top=.79,bottom=.17,wspace=.22)
for ax,case in zip(axs,['10bar','25bar']):
 for path in sorted((ROOT/'results').glob(f'{case}-tube-topology-seed*.json')):
  run=json.loads(path.read_text());t=run['trace'];ax.step([v['evaluation'] for v in t],[v['mass_lbm'] for v in t],where='post',label=f'Seed {run["seed"]}')
 ax.set_title(case);ax.set_xlabel('Unique structural evaluations');ax.set_ylabel('Best feasible mass (lbm)');ax.legend(frameon=False);ax.grid(alpha=.18)
fig.suptitle('Topology search: three reproducible starts',fontsize=19,fontweight='bold');fig.savefig(ROOT/'results/search-traces.png',dpi=170);plt.close(fig)
print('Rendered 4 before/after comparisons, convergence plot and all member/node schedules.')

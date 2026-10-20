from common import *
from extension import model,verify_extension,EXT
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.cm import ScalarMappable
from matplotlib.lines import Line2D
FIG=ROOT/'research/feature-trial/figures';FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'figure.facecolor':'#f7f9fc','axes.facecolor':'#f7f9fc','text.color':'#14253b','axes.labelcolor':'#14253b','axes.titleweight':'bold'})
b=model();before=json.loads((EXT/'before.json').read_text());greedy=json.loads((OUT/'extension-individual-25bar.json').read_text());rr=[json.loads(p.read_text()) for p in OUT.glob('extension-continuation-*.json')]+[json.loads(p.read_text()) for p in OUT.glob('extension-stage2-*.json')];winner=min(rr,key=lambda r:r['mass_lbm']);candidates=[before,greedy['candidate'],winner['candidate']];reports=[verify_extension(c)['primary'] for c in candidates];savings=100*(1-reports[-1]['mass_lbm']/reports[0]['mass_lbm']);xyz=np.array(b['nodes']);vmax=max(np.max(abs(np.array(r['forces'])))/1000 for r in reports);norm=TwoSlopeNorm(vmin=-vmax,vcenter=0,vmax=vmax);cmap=plt.get_cmap('coolwarm')
fig=plt.figure(figsize=(16,8));gs=fig.add_gridspec(1,3,left=.025,right=.91,top=.71,bottom=.20,wspace=.02)
for col,(label,r) in enumerate(zip(['Starting design','Individual-size hill climb','Guided search'],reports)):
 ax=fig.add_subplot(gs[0,col],projection='3d')
 for e,((i,j),A,N) in enumerate(zip(b['members'],r['member_areas'],np.array(r['forces'][0])/1000)):
  xy=xyz[[i-1,j-1]];ax.plot(*xy.T,color='#c5ccd7' if A==0 else cmap(norm(N)),lw=.7 if A==0 else .8+5*np.sqrt(A/max(b['catalog'])),ls=':' if A==0 else '-',solid_capstyle='round')
 ax.scatter(*xyz.T,color='#14253b',s=14,depthshade=False)
 for i,point in enumerate(xyz):ax.text(*point,str(i+1),fontsize=8)
 sup=xyz[np.array(b['fixed_nodes'])-1];ax.scatter(*sup.T,marker='^',s=65,color='#14253b',depthshade=False)
 for load in b['loads'][0]['nodal']:
  pos=xyz[load[0]-1];F=np.array(load[1:]);vec=F/max(np.max(abs(F)),1)*40;ax.quiver(*pos,*vec,color='#14253b',arrow_length_ratio=.25,linewidth=1.2)
 ax.view_init(elev=20,azim=-60);ax.set_box_aspect([1,1,1]);ax.set_axis_off();ax.set_title(f'{label}\n{r["mass_lbm"]:.2f} lbm  /  {r["mass_kg"]:.2f} kg',fontsize=13,pad=12)
 fig.text(.17+col*.297,.18,f'Stress {100*r["stress_utilization"]:.1f}%  ·  displacement {100*r["displacement_utilization"]:.2f}%\nEuler compression {100*r["buckling_utilization"]:.2f}% of model limit',ha='center',fontsize=9,color='#43546a')
cax=fig.add_axes([.94,.29,.013,.33]);fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=cax,label='Axial force (kip): compression − / tension +')
fig.suptitle(f'Same loads. Same geometry. {savings:.2f}% less material.',x=.045,ha='left',y=.955,fontsize=24,fontweight='bold')
fig.text(.045,.865,'Exploratory 25-bar model: each member may choose its own catalogue size.\nStarting structure is the grouped-model incumbent; this is a separate design-space experiment.',fontsize=12,linespacing=1.6)
fig.text(.045,.07,'Width indicates cross-sectional area. Dotted lines are removed members; triangles are supports; arrows are applied loads.\nFixed linear-elastic model, prescribed load case, stress/displacement/Euler checks. Model-validated research only; not certified for construction.',fontsize=10,color='#43546a',linespacing=1.6)
fig.savefig(FIG/'extension-before-after.png',dpi=170);fig.savefig(FIG/'extension-before-after.svg');plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(13,5.6));fig.subplots_adjust(left=.07,right=.96,top=.74,bottom=.25,wspace=.28)
ax=axs[0];ax.plot([0,12000],[100,100],lw=4,color='#44546a');ax.set_ylim(99,101);ax.set_xlim(0,12000);ax.set_title('Original grouped benchmarks');ax.set_xlabel('Structural solves per run');ax.set_ylabel('Mass / starting incumbent (%)');ax.text(6000,100.55,'44 runs · 528,000 total solves\n0 improvements across six incumbent rows',ha='center',fontsize=11);ax.grid(alpha=.15)
ax=axs[1];values=[r['mass_lbm'] for r in reports];ax.plot([0,1,2],values,'o-',lw=3,ms=9,color='#147d92');ax.set_xticks([0,1,2],['Grouped design\nexpanded','Local sizing\nsearch','Guided\nsearch']);ax.set_ylabel('Mass (lbm)');ax.set_title('Separate individual-member model');ax.set_ylim(min(values)-22,max(values)+27);ax.set_xlim(-.2,2.2)
for i,m in enumerate(values):ax.annotate(f'{m:.2f}',(i,m),xytext=(0,10),textcoords='offset points',ha='center',fontsize=11)
ax.grid(axis='y',alpha=.15);fig.suptitle('Contributor progress depends on the design space',x=.055,ha='left',y=.94,fontsize=21,fontweight='bold');fig.text(.055,.83,'The original incumbents resisted search. Removing grouped-size restrictions opened measurable headroom.',fontsize=11);fig.text(.055,.045,'Left: equal-budget continuation from the existing frontier. Right: changed grouping, unchanged geometry, physics and catalogue.\nThe right-hand gain is not an improvement record on the original benchmark.',fontsize=10,color='#43546a');fig.savefig(FIG/'trial-outcome.png',dpi=170);fig.savefig(FIG/'trial-outcome.svg');plt.close(fig)
# A common-start comparison makes the algorithmic contribution distinct from the model expansion.
fig,ax=plt.subplots(figsize=(10,5.3));fig.subplots_adjust(left=.1,right=.96,top=.75,bottom=.25)
for name,color in [('baseline','#8792a2'),('hybrid','#147d92')]:
 r=json.loads((OUT/f'extension-continuation-{name}-101.json').read_text());trace=r['trace'];xs=[0]+[v['evaluation'] for v in trace]+[r['budget']];ys=[r['initial_mass_lbm']]+[v['mass_lbm'] for v in trace]+[r['mass_lbm']];ax.step(xs,ys,where='post',lw=3,label='Warm DE + local search' if name=='baseline' else 'Continuous proposals + discrete search',color=color)
ax.set_xlabel('Structural solves, including continuous proposals');ax.set_ylabel('Best verified mass (lbm)');ax.grid(alpha=.15);ax.legend(frameon=False);fig.suptitle('A better search strategy made a measurable difference',x=.07,ha='left',fontsize=19,y=.95,fontweight='bold');fig.text(.07,.82,'Same 558.11 lbm incumbent; same frozen extension; 12,000 solves each. Seed 101 shown.',fontsize=11);fig.text(.07,.065,'All three tested seeds produced these same endpoints. The shared first proposal is deterministic.\nThis demonstrates an algorithm advantage in this test, not a causal measurement of agent intelligence.',fontsize=10,color='#43546a');fig.savefig(FIG/'method-comparison.png',dpi=170);plt.close(fig)
(EXT/'best-verified.json').write_text(json.dumps(winner['candidate'],indent=2)+'\n')
print('Rendered three trial figures and saved best extension candidate:',winner['mass_lbm'])

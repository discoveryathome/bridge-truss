"""Independent implementation: element stiffness assembly and pivoted Gaussian
elimination in pure Python. Does not import primary assembly, solve, or checks."""
import math

def solve_dense(matrix,rhs):
    n=len(rhs); a=[list(row)+[v] for row,v in zip(matrix,rhs)]
    scale=max(abs(v) for row in matrix for v in row)
    for k in range(n):
        pivot=max(range(k,n),key=lambda i:abs(a[i][k]))
        if abs(a[pivot][k])<=1e-12*scale: raise ValueError('singular stiffness')
        a[k],a[pivot]=a[pivot],a[k]
        for i in range(k+1,n):
            f=a[i][k]/a[k][k]
            for j in range(k,n+1): a[i][j]-=f*a[k][j]
    x=[0.]*n
    for i in reversed(range(n)): x[i]=(a[i][n]-sum(a[i][j]*x[j] for j in range(i+1,n)))/a[i][i]
    return x

def check(b,x,profile):
    p=b['profiles'][profile]; d=b['dimension']; nd=len(b['nodes'])*d
    if len(x)!=max(b['groups'])+1: raise ValueError('size')
    allowed=b['catalog']+([0] if p['allow_removal'] else [])
    if any(not math.isfinite(v) or v not in allowed for v in x): raise ValueError('catalogue')
    a=[x[g] for g in b['groups']]; K=[[0.]*nd for _ in range(nd)]; elements=[]
    reached=set(b['fixed_nodes'])
    for _ in b['nodes']:
        for (i,j),area in zip(b['members'],a):
            if area>0 and (i in reached or j in reached): reached.update([i,j])
    if len(reached)!=len(b['nodes']): raise ValueError('disconnected')
    mass=0
    for (ni,nj),area in zip(b['members'],a):
        delta=[v-w for v,w in zip(b['nodes'][nj-1],b['nodes'][ni-1])]; L=math.sqrt(sum(v*v for v in delta)); direction=[v/L for v in delta]
        dofs=list(range((ni-1)*d,ni*d))+list(range((nj-1)*d,nj*d)); t=[-v for v in direction]+direction
        for i,gi in enumerate(dofs):
            for j,gj in enumerate(dofs): K[gi][gj]+=b['E']*area/L*t[i]*t[j]
        elements.append((L,dofs,t)); mass+=L*area*b['density_lbm_in3']
    free=[i for i in range(nd) if i//d+1 not in b['fixed_nodes']]
    maxstress=maxdisp=maxbuck=eq=balance=moment=energy_error=0.; us=[]; ns=[]; rs=[]
    for lc in b['loads']:
        f=[0.]*nd
        for row in lc['nodal']:
            for j,v in enumerate(row[1:]): f[(row[0]-1)*d+j]+=v
        uf=solve_dense([[K[i][j] for j in free] for i in free],[f[i] for i in free]); u=[0.]*nd
        for i,v in zip(free,uf): u[i]=v
        n=[]
        for area,(L,dofs,t) in zip(a,elements):
            force=b['E']*area/L*sum(ti*u[i] for ti,i in zip(t,dofs)); n.append(force)
            if area:
                maxstress=max(maxstress,abs(force)/area/b['stress_limit'])
                if p['buckling']:
                    # derive I from outer and inner diameters rather than A formula
                    r=p['inner_outer_diameter_ratio']; D=math.sqrt(4*area/(math.pi*(1-r*r)))
                    I=math.pi*(D**4-(r*D)**4)/64
                    cap=math.pi**2*b['E']*I/(p['effective_length_factor']*L)**2/p['buckling_safety_factor']
                    maxbuck=max(maxbuck,max(0,-force)/cap)
        reaction=[sum(K[i][j]*u[j] for j in range(nd))-f[i] for i in range(nd)]
        scale=max(1.,max(abs(v) for v in f)); eq=max(eq,max(abs(reaction[i]) for i in free)/scale)
        # Only supported reactions count for global balance; free residuals excluded.
        ext=[f[i]+(reaction[i] if i not in free else 0) for i in range(nd)]
        balance=max(balance,max(abs(sum(ext[j::d])) for j in range(d))/scale)
        torque=[0.,0.,0.]
        for i,xyz in enumerate(b['nodes']):
            xx=list(xyz)+[0.]*(3-d); ff=ext[i*d:(i+1)*d]+[0.]*(3-d)
            torque[0]+=xx[1]*ff[2]-xx[2]*ff[1]; torque[1]+=xx[2]*ff[0]-xx[0]*ff[2]; torque[2]+=xx[0]*ff[1]-xx[1]*ff[0]
        moment=max(moment,max(abs(v) for v in torque)/(scale*max(1,max(abs(v) for row in b['nodes'] for v in row))))
        for node,j,limit in b['displacement_limits']: maxdisp=max(maxdisp,abs(u[(node-1)*d+j])/limit)
        twice_energy=sum(force*force*L/(b['E']*area) for force,area,(L,_,_) in zip(n,a,elements) if area)
        work=sum(v*w for v,w in zip(f,u)); energy_error=max(energy_error,abs(twice_energy-work)/max(1,abs(work)))
        us.append(u); ns.append(n); rs.append(reaction)
    tol=b['tolerance']; valid=max(maxstress,maxdisp,maxbuck)<=1+tol['constraint'] and max(eq,balance,moment,energy_error)<=tol['equilibrium_relative']
    return dict(valid=valid,mass_lbm=mass,stress_utilization=maxstress,displacement_utilization=maxdisp,buckling_utilization=maxbuck,equilibrium_relative=eq,global_force_balance_relative=balance,global_moment_balance_relative=moment,energy_relative=energy_error,displacements=us,forces=ns,reactions=rs)

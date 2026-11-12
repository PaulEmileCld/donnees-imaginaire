import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, colorsys, sys
from matplotlib.collections import LineCollection
D=json.load(open('data_niv.json')); W=D['w']; niv=D['niv'][4]; quoi=sys.argv[1]; centres=sys.argv[2].split(','); frac=float(sys.argv[3])
F=json.load(open(f'fa2_{quoi}.json')); idx={n:k for k,n in enumerate(F['n'])}; P=np.array(F['p']); mots=[W[n] for n in F['n']]; ix={m:k for k,m in enumerate(mots)}
col=lambda c:colorsys.hls_to_rgb(((c*137.508+20)%360)/360,0.62,0.65)
C=np.array([col(niv['c'][n]) for n in F['n']]); deg=np.zeros(len(P))
for a,b,_ in F['e']: deg[idx[a]]+=1; deg[idx[b]]+=1
E=np.array([[idx[a],idx[b]] for a,b,_ in F['e']])
ext=np.percentile(P,99,axis=0)-np.percentile(P,1,axis=0); h=ext.max()*frac/2
fig,axs=plt.subplots(2,2,figsize=(18,18),dpi=100); fig.patch.set_facecolor('#14161b'); plt.subplots_adjust(0.01,0.01,0.99,0.945,0.02,0.04)
for ax,c in zip(axs.ravel(),centres):
    cx,cy=P[ix[c]]; x0,x1,y0,y1=cx-h,cx+h,cy-h,cy+h
    dedans=np.where((P[:,0]>x0)&(P[:,0]<x1)&(P[:,1]>y0)&(P[:,1]<y1))[0]; s=set(dedans.tolist())
    m=[k for k,(a,b) in enumerate(E) if a in s or b in s]
    ax.add_collection(LineCollection([[P[a],P[b]] for a,b in E[m]],colors=[(*C[a],.22) for a,b in E[m]],linewidths=.6))
    ax.scatter(P[dedans,0],P[dedans,1],s=8+np.sqrt(deg[dedans])*6,c=C[dedans],linewidths=0,zorder=3)
    pris=[]; cw=2*h/95  # largeur approximative d'un caractère
    for k in sorted(dedans,key=lambda k:-deg[k]):
        w=len(mots[k])*cw/2; bx=(P[k,0]-w,P[k,0]+w,P[k,1]-cw*.9,P[k,1]+cw*.9)
        if any(not(bx[1]<q[0] or bx[0]>q[1] or bx[3]<q[2] or bx[2]>q[3]) for q in pris): continue
        pris.append(bx); ax.text(P[k,0],P[k,1],mots[k],color='white' if k!=ix[c] else '#f2a623',fontsize=10.5 if k!=ix[c] else 14,ha='center',va='center',zorder=4,
            bbox=dict(boxstyle='round,pad=0.12',fc='#14161bcc',ec='none'))
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_facecolor('#14161b'); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_color('#353943')
    ax.set_title(f'autour de « {c} » · {len(dedans)} mots',color='#e9e6df',fontsize=15,family='serif',loc='left')
fig.suptitle(sys.argv[4],color='#e9e6df',fontsize=19,family='serif',x=0.01,ha='left')
fig.savefig(f'/home/claude/zoom_{quoi}.png',facecolor=fig.get_facecolor()); print('ok')

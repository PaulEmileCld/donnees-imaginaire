"""Solution 3 : sol = proximité de profil (ForceAtlas2), routes = associations JeuxDeMots par-dessus.
Les associations qui sautent d'une famille à l'autre (« glissements ») sont mises en lumière."""
import json, numpy as np, matplotlib, colorsys, sys, collections; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
D=json.load(open('data_niv.json')); F=json.load(open('fa2np_15096.json')); N=F['N']; P=np.array(F['p']); W=D['w'][:N]
niv=D['niv'][4]; c=np.array(niv['c'][:N]); lab=niv['lab']
col=lambda k:colorsys.hls_to_rgb(((k*137.508+20)%360)/360,0.62,0.65); C=np.array([col(k) for k in c])
K=int(sys.argv[1]) if len(sys.argv)>1 else 3
A=[(i,j,v) for i in range(N) for j,v in D['nb'][i][:K] if j<N]
indeg=collections.Counter(j for _,j,_ in A); HUBS={j for j,_ in indeg.most_common(40)}  # étiquettes de domaine de JeuxDeMots (habillement, musique, zoologie…)
print('mots-étiquettes écartés des glissements :',', '.join(W[j] for j,_ in indeg.most_common(40)))
dans=[(i,j,v) for i,j,v in A if c[i]==c[j]]; ponts=[(i,j,v) for i,j,v in A if c[i]!=c[j]]
hub=lambda i,j:i in HUBS or j in HUBS
print(len(A),'associations ;',round(100*len(ponts)/len(A)),'% sautent de famille')
# longueur des ponts : un glissement lointain est plus parlant
L=np.array([np.linalg.norm(P[i]-P[j]) for i,j,_ in ponts]); ext=np.ptp(P,axis=0).max()
def etiquettes(ax,ids,x0,x1,y0,y1,taille,ncar,centre=None):
    pris=[]; cw=(x1-x0)/ncar; deg=np.bincount(np.array([a for a,_,_ in A]+[b for _,b,_ in A]),minlength=N)
    for k in sorted(ids,key=lambda k:-deg[k]):
        w=len(W[k])*cw/2; bx=(P[k,0]-w,P[k,0]+w,P[k,1]-cw,P[k,1]+cw)
        if any(not(bx[1]<q[0] or bx[0]>q[1] or bx[3]<q[2] or bx[2]>q[3]) for q in pris): continue
        pris.append(bx); ax.text(P[k,0],P[k,1],W[k],color='#f2a623' if k==centre else 'white',fontsize=taille*(1.35 if k==centre else 1),ha='center',va='center',zorder=5,
                                 bbox=dict(boxstyle='round,pad=0.1',fc='#14161bb0',ec='none'))
def dessine(ax,x0,x1,y0,y1,zoom):
    dedans_f=lambda i:x0<P[i,0]<x1 and y0<P[i,1]<y1
    garde=(lambda i,j:dedans_f(i) or dedans_f(j)) if zoom else (lambda i,j:True)   # en zoom : pas de liens qui ne font que traverser
    loin=lambda i,j:np.linalg.norm(P[i]-P[j])>ext*.15
    e1=[(i,j,v) for i,j,v in dans if garde(i,j)]
    e2=[(i,j,v) for i,j,v in ponts if garde(i,j) and (not loin(i,j) or hub(i,j))]      # petit saut : discret
    e3=[(i,j,v) for i,j,v in ponts if garde(i,j) and loin(i,j) and not hub(i,j)]          # long saut = glissement, en orange
    s=lambda e:[[P[i],P[j]] for i,j,_ in e]
    ax.add_collection(LineCollection(s(e1),colors=[(*C[i],.30 if zoom else .07) for i,_,_ in e1],linewidths=.8 if zoom else .3))
    ax.add_collection(LineCollection(s(e2),colors=(.6,.6,.62,.16 if zoom else .025),linewidths=.6 if zoom else .25))
    ax.add_collection(LineCollection(s(e3),colors=(1,.65,.14,.45 if zoom else .05),linewidths=[(1.2 if zoom else .35)*(.4+v/800) for _,_,v in e3]))
    deg=np.bincount(np.array([a for a,_,_ in A]+[b for _,b,_ in A]),minlength=N)
    ax.scatter(P[:,0],P[:,1],s=(1.5 if not zoom else 10)+np.sqrt(deg)*(1.2 if not zoom else 4),c=C,linewidths=0,zorder=3)
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_facecolor('#14161b'); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_color('#353943')
lo,hi=np.percentile(P,.5,axis=0),np.percentile(P,99.5,axis=0); pad=(hi-lo)*.03
fig=plt.figure(figsize=(24,24),dpi=100); ax=fig.add_axes([0,0,1,1]); fig.patch.set_facecolor('#14161b')
dessine(ax,lo[0]-pad[0],hi[0]+pad[0],lo[1]-pad[1],hi[1]+pad[1],False)
etiquettes(ax,range(N),lo[0],hi[0],lo[1],hi[1],8.5,230)
ax.text(.01,.99,f"{N:,} mots · sol : proximité de profil (ForceAtlas2) · routes : {len(A):,} associations JeuxDeMots".replace(',',' '),transform=ax.transAxes,color='#e9e6df',fontsize=20,va='top',family='serif')
ax.text(.01,.972,f"Couleur de la famille : associations internes · gris : petits sauts entre familles voisines · orange : longs sauts d'un bout à l'autre de la carte (glissements)",transform=ax.transAxes,color='#9a978f',fontsize=13,va='top')
fig.savefig('/home/claude/hybride_vue.png',facecolor=fig.get_facecolor()); plt.close(fig)
# zooms
centres=sys.argv[2].split(',') if len(sys.argv)>2 else ['mer','tristesse','culte','mère']
ix={w:k for k,w in enumerate(W)}; h=np.ptp(P,axis=0).max()*.075
fig,axs=plt.subplots(2,2,figsize=(20,20),dpi=100); fig.patch.set_facecolor('#14161b'); plt.subplots_adjust(.01,.01,.99,.955,.02,.04)
for ax,m in zip(axs.ravel(),centres):
    cx,cy=P[ix[m]]; x0,x1,y0,y1=cx-h,cx+h,cy-h,cy+h; dessine(ax,x0,x1,y0,y1,True)
    ids=np.where((P[:,0]>x0)&(P[:,0]<x1)&(P[:,1]>y0)&(P[:,1]<y1))[0]; etiquettes(ax,ids,x0,x1,y0,y1,10,85,ix[m])
    sorties=sorted([(v,W[j]) for i,j,v in ponts if i==ix[m] and np.linalg.norm(P[i]-P[j])>ext*.15 and not hub(i,j)],reverse=True)[:6]
    ax.set_title(f"autour de « {m} » · {len(ids)} mots",color='#e9e6df',fontsize=16,family='serif',loc='left')
    if sorties: ax.text(.01,.01,"glissements depuis « "+m+" » : "+", ".join(w for _,w in sorties),transform=ax.transAxes,color='#f2a623',fontsize=11.5,va='bottom',bbox=dict(fc='#14161be0',ec='none'))
fig.suptitle('Zooms · sol de proximité, routes d’associations (orange = glissement vers une autre famille)',color='#e9e6df',fontsize=20,family='serif',x=.01,ha='left')
fig.savefig('/home/claude/hybride_zooms.png',facecolor=fig.get_facecolor())
# les plus grands glissements : paires de familles les plus reliées malgré la distance
paire=collections.Counter(); ex=collections.defaultdict(list)
for (i,j,v),l in zip(ponts,L):
    if l>ext*.2 and not hub(i,j): k=tuple(sorted((c[i],c[j]))); paire[k]+=1; ex[k].append((v,W[i],W[j]))
for k,n in paire.most_common(8): print(n,lab[k[0]],'↔',lab[k[1]],'|',', '.join(f'{a}→{b}' for _,a,b in sorted(ex[k],reverse=True)[:4]))

L2=sorted([(v,W[i],W[j]) for (i,j,v),l in zip(ponts,L) if l>ext*.35 and not hub(i,j)],reverse=True)
open('/tmp/usage/glissements.txt','w').write('\n'.join(f'{a} → {b}\t{v}' for v,a,b in L2)); print(len(L2),'grands glissements :',', '.join(f'{a}→{b}' for _,a,b in L2[:70]))

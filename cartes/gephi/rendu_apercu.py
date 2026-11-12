import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, colorsys, sys
from matplotlib.collections import LineCollection
D=json.load(open('data_niv.json')); W=D['w']; niv=D['niv'][4]; quoi=sys.argv[1]; titre=sys.argv[2]
F=json.load(open(f'fa2_{quoi}.json')); idx={n:k for k,n in enumerate(F['n'])}; P=np.array(F['p'])
col=lambda c:colorsys.hls_to_rgb(((c*137.508+20)%360)/360,0.62,0.65)
C=np.array([col(niv['c'][n]) for n in F['n']])
deg=np.zeros(len(P))
for a,b,_ in F['e']: deg[idx[a]]+=1; deg[idx[b]]+=1
fig=plt.figure(figsize=(16,16),dpi=110); ax=fig.add_axes([0,0,1,1]); ax.set_facecolor('#14161b'); fig.patch.set_facecolor('#14161b')
seg=[[P[idx[a]],P[idx[b]]] for a,b,_ in F['e']]; ec=[(*C[idx[a]],0.10) for a,b,_ in F['e']]
ax.add_collection(LineCollection(seg,colors=ec,linewidths=0.35))
ax.scatter(P[:,0],P[:,1],s=2+np.sqrt(deg)*2.2,c=C,linewidths=0,alpha=.9)
top=np.argsort(-deg)[:70]
for k in top: ax.text(P[k,0],P[k,1],W[F['n'][k]],color='white',fontsize=9,ha='center',va='center',alpha=.85)
ax.text(0.015,0.985,titre,transform=ax.transAxes,color='#e9e6df',fontsize=17,va='top',family='serif')
ax.text(0.015,0.958,'Aperçu ForceAtlas2 (même algorithme que Gephi, recalculé ici) · couleurs : 32 communautés · taille : nombre de liens',transform=ax.transAxes,color='#9a978f',fontsize=11,va='top')
m=np.percentile(P,[1,99],axis=0); pad=(m[1]-m[0])*.06; ax.set_xlim(m[0,0]-pad[0],m[1,0]+pad[0]); ax.set_ylim(m[0,1]-pad[1],m[1,1]+pad[1]); ax.axis('off')
fig.savefig(f'/home/claude/apercu_gephi_{quoi}.png',facecolor=fig.get_facecolor()); print('ok')

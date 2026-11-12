import json, numpy as np, matplotlib, colorsys; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
D=json.load(open('data_niv.json')); W=D['w'][:2000]; c=D['niv'][4]['c'][:2000]
col=lambda k:colorsys.hls_to_rgb(((k*137.508+20)%360)/360,0.62,0.65); C=np.array([col(k) for k in c])
A=json.load(open('arbres.json')); POS=json.load(open('arbres_pos.json')); FB=json.load(open('faisceaux.json'))
def image(nom,P,segs,segcol,lw,titre,sous,nlab=2000,ncar=150,fs=8):
    P=np.array(P); deg=np.zeros(len(P))
    fig=plt.figure(figsize=(22,22),dpi=100); ax=fig.add_axes([0,0,1,1]); fig.patch.set_facecolor('#14161b'); ax.set_facecolor('#14161b')
    ax.add_collection(LineCollection(segs,colors=segcol,linewidths=lw,capstyle='round'))
    lo,hi=np.percentile(P,.5,axis=0),np.percentile(P,99.5,axis=0); pad=(hi-lo)*.04
    ax.scatter(P[:,0],P[:,1],s=6,c=C,linewidths=0,zorder=3)
    cw=(hi[0]-lo[0])/ncar; pris=[]
    for k in range(min(nlab,len(P))):  # les mots les plus pertinents d'abord
        w=len(W[k])*cw/2; bx=(P[k,0]-w,P[k,0]+w,P[k,1]-cw*.9,P[k,1]+cw*.9)
        if any(not(bx[1]<q[0] or bx[0]>q[1] or bx[3]<q[2] or bx[2]>q[3]) for q in pris): continue
        pris.append(bx); ax.text(P[k,0],P[k,1],W[k],color='white',fontsize=fs,ha='center',va='center',zorder=4,bbox=dict(boxstyle='round,pad=0.08',fc='#14161ba0',ec='none'))
    ax.set_xlim(lo[0]-pad[0],hi[0]+pad[0]); ax.set_ylim(lo[1]-pad[1],hi[1]+pad[1]); ax.axis('off')
    ax.text(.012,.99,titre,transform=ax.transAxes,color='#e9e6df',fontsize=22,va='top',family='serif')
    ax.text(.012,.968,sous,transform=ax.transAxes,color='#9a978f',fontsize=13,va='top')
    fig.savefig(f'/home/claude/{nom}.png',facecolor=fig.get_facecolor()); plt.close(fig); print(nom,len(pris),'étiquettes')
for k,nom,titre,sous in [('arbre','apercu_1_arbre','1 · Arbre couvrant maximal',"2 000 mots, 1 999 liens : chaque mot garde son lien le plus fort vers le reste. Aucune boucle. Épaisseur = force du lien."),
                         ('pf','apercu_2_pathfinder','2 · Réseau Pathfinder',"2 000 mots, 2 464 liens : un lien disparaît si un détour par d'autres mots est plus fort que lui. Quelques boucles survivent : les mots-ponts.")]:
    P=np.array(POS[k]); e=A[k]; vmax=max(v for *_,v in e)
    image(nom,P,[[P[a],P[b]] for a,b,_ in e],[(*C[a],.55) for a,b,_ in e],[.6+3.5*(v/vmax)**.7 for *_,v in e],titre,sous)
P=np.array(FB['X']); segs=[]; cols=[]
for (a,b),pts in zip(FB['E'],FB['P']):
    pts=np.array(pts); segs.append(pts); cols.append((*C[a],.22))
image('apercu_3_faisceaux',P,segs,cols,.7,'3 · Faisceaux de liens (edge bundling)',"2 000 mots, 3 877 associations (les 3 plus fortes par mot), positions de la carte hybride. Rien n'est supprimé : les liens de même direction sont rassemblés en branches.")

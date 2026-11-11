import numpy as np, json, networkx as nx, csv, scipy.sparse as sp
from sklearn.neighbors import NearestNeighbors
D=json.load(open('data.json')); Z=np.load('Z.npy'); W=D['w']; K=len(W)
R='/home/claude/donnees-imaginaire/'
info={r['Id']:r for r in csv.DictReader(open(R+'resultats_usage/noeuds.csv',encoding='utf-8'))}
# graphe kNN cosinus sur l'espace SVD (plus net que les PPMI brutes)
nn=NearestNeighbors(n_neighbors=16,metric='cosine').fit(Z); dist,I=nn.kneighbors(Z)
G=nx.Graph()
for i in range(K):
    for d,j in zip(dist[i,1:],I[i,1:]): G.add_edge(i,int(j),weight=float(1-d))
for res in (1.0,):
    com=sorted(nx.community.louvain_communities(G,weight='weight',resolution=res,seed=3),key=len,reverse=True)
    print(res,len(com),[len(c) for c in com[:20]])
fk=np.array(D['s'])
def lab(cs):
    # mots les plus « typiques » : part de voisins dans la même communauté × fréquence
    cs=set(cs); sc={v:(np.mean([j in cs for j in I[v,1:]]))*(1+fk[v]) for v in cs}
    return ', '.join(W[v] for v in sorted(sc,key=lambda v:-sc[v])[:5])
for k,c in enumerate(com[:16]): print(k,len(c),lab(c))
NC=15;cid=np.full(K,NC)
for k,cs in enumerate(com):
    for v in cs: cid[v]=min(k,NC)
D['c']=cid.tolist(); D['lab']=[lab(c) for c in com[:NC]]
du=np.array(D['du'],bool)
cat=np.array([info[w]['categorie'] for w in W]); 
# témoin : noms non-Durand de fréquence comparable
rng=np.random.default_rng(0); base=[]
noms=np.where((cat=='NOM')&~du)[0]
for _ in range(20):
    s=[]
    for v in np.where(du)[0]:
        cand=noms[np.abs(fk[noms]-fk[v])<0.3]; s.append(rng.choice(cand) if len(cand) else rng.choice(noms))
    s=np.array(s); m=np.zeros(K,bool); m[s]=True
    base.append(m[I[s,1:11]].mean())
m=du[I[du,1:11]].mean()
print('Durand se voisinent entre eux : %.3f ; noms témoins de même fréquence : %.3f ± %.3f'%(m,np.mean(base),np.std(base)))
print('Durand par communauté:',[(k,int(du[cid==k].sum()),int((cid==k).sum())) for k in range(NC+1)])
json.dump(D,open('data.json','w'),ensure_ascii=False,separators=(',',':'))

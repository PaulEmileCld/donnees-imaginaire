"""Communautés à plusieurs résolutions (le « resolution » de la modularité dans Gephi), pour le curseur de la page."""
import json, numpy as np, networkx as nx, csv
from sklearn.neighbors import NearestNeighbors
R='/home/claude/donnees-imaginaire/'
D=json.load(open('data.json')); Z0=np.load('Z.npy'); keep=np.load('keep.npy')
names=sorted(r['Id'] for r in csv.DictReader(open(R+'resultats_usage/noeuds.csv',encoding='utf-8')))
pos={names[k]:i for i,k in enumerate(keep)}
Z=Z0[[pos[w] for w in D['w']]]; W=D['w']; K=len(W); fk=np.array(D['s'])
nn=NearestNeighbors(n_neighbors=16,metric='cosine').fit(Z); dist,I=nn.kneighbors(Z)
G=nx.Graph()
for i in range(K):
    for d,j in zip(dist[i,1:],I[i,1:]): G.add_edge(i,int(j),weight=float(1-d))
def lab(cs):
    cs=set(cs); sc={v:(np.mean([j in cs for j in I[v,1:]]))*(1+fk[v]) for v in cs}
    return ', '.join(W[v] for v in sorted(sc,key=lambda v:-sc[v])[:4])
niv=[]
for res in [0.1,0.2,0.35,0.5,0.7,1.0,1.4,2.0,3.0,4.5,7.0]:
    com=sorted(nx.community.louvain_communities(G,weight='weight',resolution=res,seed=3),key=len,reverse=True)
    c=[0]*K
    for k,cs in enumerate(com):
        for v in cs: c[v]=k
    Q=nx.community.modularity(G,com,weight='weight',resolution=res)
    niv.append({'res':res,'c':c,'lab':[lab(x) for x in com],'n':[len(x) for x in com],'q':round(Q,3)})
    print(res,len(com),round(Q,3),[lab(x) for x in com[:3]])
D['niv']=niv; D['defaut']=5
for k in ('c','lab','ld','ln','du'): D.pop(k,None)
json.dump(D,open('data_niv.json','w'),ensure_ascii=False,separators=(',',':'))
json.dump({'w':W,'niv':[{'res':n['res'],'c':n['c']} for n in niv]},open('niveaux_gephi.json','w'))

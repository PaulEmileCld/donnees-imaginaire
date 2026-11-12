"""Trois aperçus sur les 2 000 mots les plus pertinents : arbre couvrant maximal, Pathfinder, faisceaux de liens."""
import json, gzip, csv, numpy as np, time, collections
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree, connected_components
R='/home/claude/donnees-imaginaire/'; NS=2000
D=json.load(open('data_niv.json')); W=D['w'][:NS]; ix={w:i for i,w in enumerate(W)}
# poids JeuxDeMots entre ces mots (toutes les associations, pas seulement les 10 premières)
S=collections.defaultdict(float)
for r in csv.reader(gzip.open(R+'resultats_usage/liens.csv.gz','rt',encoding='utf-8')):
    a,b=ix.get(r[0]),ix.get(r[1])
    if a is None or b is None or a==b: continue
    k=(min(a,b),max(a,b)); S[k]=max(S[k],float(r[2]))
force=np.zeros(NS)
for (a,b),v in S.items(): force[a]+=v; force[b]+=v
# poids normalisé : sinon les mots très populaires (eau, mort…) deviennent le centre de tout
E=np.array(list(S.keys())); V=np.array([S[tuple(k)] for k in E])/np.sqrt(force[E[:,0]]*force[E[:,1]]+1e-9)
print(len(E),'liens entre les 2 000 mots')
M=csr_matrix((1/(V+1e-9),(E[:,0],E[:,1])),shape=(NS,NS))
T=minimum_spanning_tree(M).tocoo(); arbre=[(int(a),int(b),1/float(d)) for a,b,d in zip(T.row,T.col,T.data)]
print('arbre :',len(arbre),'liens ; composantes',connected_components(T)[0])
# Pathfinder (q=2) : on retire i–j s'il existe k avec deux liens plus forts que i–j, sur les 12 meilleurs liens de chaque mot
voisins=collections.defaultdict(dict)
for (a,b),v in zip(map(tuple,E),V): voisins[a][b]=v; voisins[b][a]=v
cand=set()
for a,d in voisins.items():
    for b,_ in sorted(d.items(),key=lambda x:-x[1])[:6]: cand.add((min(a,b),max(a,b)))
pf=[]
for a,b in cand:
    v=voisins[a][b]; com=set(voisins[a])&set(voisins[b])
    if not any(min(voisins[a][k],voisins[b][k])>v for k in com): pf.append((int(a),int(b),float(v)))
pf=pf+[x for x in arbre if (x[0],x[1]) not in cand and (x[1],x[0]) not in cand]
print('pathfinder :',len(pf),'liens')
json.dump({'w':W,'arbre':arbre,'pf':pf},open('arbres.json','w'))
# Pathfinder PFNET(r=1, q=n-1) : on garde un lien seulement s'il est le plus court chemin entre ses deux mots (distance = -log du poids)
from scipy.sparse.csgraph import shortest_path
cand=set()
for a,d in voisins.items():
    for b,_ in sorted(d.items(),key=lambda x:-x[1])[:15]: cand.add((min(a,b),max(a,b)))
cand=list(cand); vv=np.array([voisins[a][b] for a,b in cand]); dist=-np.log(vv/vv.max())+1e-3
ca=np.array(cand); G=csr_matrix((np.r_[dist,dist],(np.r_[ca[:,0],ca[:,1]],np.r_[ca[:,1],ca[:,0]])),shape=(NS,NS))
SP=shortest_path(G,directed=False)
pf=[(int(a),int(b),float(v)) for (a,b),v,d in zip(cand,vv,dist) if d<=SP[a,b]+1e-9]
print('pathfinder (r=1) :',len(pf),'liens, soit',round(len(pf)/NS,2),'par mot')
json.dump({'w':W,'arbre':arbre,'pf':pf},open('arbres.json','w'))

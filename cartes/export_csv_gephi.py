"""Fichiers Gephi simples : noeuds.csv + liens (associations JeuxDeMots, et proximité de profil)."""
import json, numpy as np, csv, os
from sklearn.neighbors import NearestNeighbors
R='/home/claude/donnees-imaginaire/'; O=R+'cartes/gephi/'; os.makedirs(O,exist_ok=True)
D=json.load(open('data_niv.json')); W=D['w']; K=len(W)
info={r['Id']:r for r in csv.DictReader(open(R+'resultats_usage/noeuds.csv',encoding='utf-8'))}
Z0=np.load('Z.npy'); keep=np.load('keep.npy'); names=sorted(info); pos={names[k]:i for i,k in enumerate(keep)}
Z=Z0[[pos[w] for w in W]]; np.save('Z_ordre.npy',Z)
with open(O+'noeuds.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); cols=[f"communaute_res_{str(n['res']).replace('.','_')}" for n in D['niv']]
    w.writerow(['Id','Label','categorie','frequence','rang_pertinence','oral_ecrit','epoque','vues_wikipedia','x','y']+cols)
    for i,m in enumerate(W):
        w.writerow([m,m,info[m]['categorie'],round(float(info[m]['freq_films'] or 0)+float(info[m]['freq_livres'] or 0),2),i,D['oe'][i],
                    '' if D['ep'][i] is None else D['ep'][i],D['wk'][i],round(D['x'][i][0]*4,1),round(-D['x'][i][1]*4,1)]+[n['c'][i] for n in D['niv']])
with open(O+'liens_associations.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['Source','Target','Weight','Type'])
    for i,l in enumerate(D['nb']):
        for j,v in l: w.writerow([W[i],W[j],v,'Directed'])
nn=NearestNeighbors(n_neighbors=11,metric='cosine').fit(Z); dist,I=nn.kneighbors(Z); vus=set()
with open(O+'liens_proximite.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['Source','Target','Weight','Type'])
    for i in range(K):
        for d,j in zip(dist[i,1:],I[i,1:]):
            k=(min(i,j),max(i,j))
            if k in vus: continue
            vus.add(k); w.writerow([W[i],W[int(j)],round(1-float(d),3),'Undirected'])
print(K,'noeuds', sum(len(l) for l in D['nb']),'associations', len(vus),'proximités')

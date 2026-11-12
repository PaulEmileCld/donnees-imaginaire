import numpy as np, scipy.sparse as sp, json, csv, collections, networkx as nx, openpyxl, time
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
R='/home/claude/donnees-imaginaire/'; t0=time.time()
info={r['Id']:r for r in csv.DictReader(open(R+'resultats_usage/noeuds.csv',encoding='utf-8'))}
names=sorted(info); ix={w:i for i,w in enumerate(names)}; n=len(names)
rows,cols,vals=[],[],[]
import gzip, os
fichier=R+'resultats_usage/liens.csv.gz' if os.path.exists(R+'resultats_usage/liens.csv.gz') else R+'resultats_usage/liens.csv'
for r in csv.reader(gzip.open(fichier,'rt',encoding='utf-8') if fichier.endswith('.gz') else open(fichier,encoding='utf-8')):
    if r[0]=='Source': continue
    a,b=ix.get(r[0]),ix.get(r[1])
    if a is None or b is None or a==b: continue
    rows.append(a);cols.append(b);vals.append(float(r[2]))
A=sp.csr_matrix((vals,(rows,cols)),shape=(n,n)); A.sum_duplicates()
print('liens',A.nnz, time.time()-t0)
S=(A+A.T).tocsr()
tot=S.sum();rs=np.asarray(S.sum(1)).ravel()
C=S.tocoo();pmi=np.log((C.data*tot)/(rs[C.row]*rs[C.col]+1e-9));m=pmi>0
P=sp.csr_matrix((pmi[m],(C.row[m],C.col[m])),shape=(n,n))
deg=np.asarray((S>0).sum(1)).ravel()
# mots affichés : ceux interrogés et reliés, les 6000 plus fréquents + tous les Durand reliés
freq=np.array([float(info[w]['freq_films'] or 0)+float(info[w]['freq_livres'] or 0) for w in names])
dur=np.array([info[w]['durand']=='1' for w in names])
ok=deg>=5
z=lambda v:(v-v.mean())/(v.std()+1e-9)
pert=z(np.log1p(freq))+z(np.log1p(deg))  # pertinence : usage + nombre de liens
cand=np.where(ok)[0]; top=cand[np.argsort(-pert[cand])][:15000]
keep=np.array(sorted(set(top.tolist())|set(np.where(ok&dur)[0].tolist())))
K=len(keep); print('affichés',K,'dont Durand',dur[keep].sum())
Pk=P[keep][:,keep]
Z=TruncatedSVD(150,random_state=1).fit_transform(Pk);Z/=np.linalg.norm(Z,axis=1,keepdims=True)+1e-9
X=TSNE(3,perplexity=40,init='pca',random_state=2,max_iter=1000,n_jobs=2).fit_transform(Z)
X-=X.mean(0);X/=np.abs(X).max();X*=260; print('tsne',time.time()-t0)
Sk=S[keep][:,keep].tocoo(); G=nx.Graph()
G.add_nodes_from(range(K))
# Louvain sur le graphe PPMI (sinon « être », « faire » absorbent tout)
Pc=Pk.tocoo()
for a,b,w in zip(Pc.row,Pc.col,Pc.data):
    if a<b: G.add_edge(int(a),int(b),weight=float(w))
com=sorted(nx.community.louvain_communities(G,weight='weight',resolution=1.0,seed=3),key=len,reverse=True)
NC=14; cid=np.full(K,NC)
for k,cs in enumerate(com):
    for v in cs: cid[v]=min(k,NC)
fk=freq[keep]
labels=[', '.join(names[keep[v]] for v in sorted(com[k],key=lambda v:-fk[v])[:4]) for k in range(min(NC,len(com)))]
print('communautés',len(com),[len(c) for c in com[:16]]); print(labels)
# voisins : associations JDM sortantes, top 10 parmi les affichés
Ak=A[keep][:,keep].tocsr(); nb=[]
for i in range(K):
    s,e=Ak.indptr[i],Ak.indptr[i+1]; idx=Ak.indices[s:e]; val=Ak.data[s:e]; o=np.argsort(-val)[:10]
    nb.append([[int(idx[j]),int(val[j])] for j in o])
# normes
val={};conc={}
wb=openpyxl.load_workbook(R+'resultats_normes/brut/bonin2018_concretude_valence_1659_annexe3.xlsx',read_only=True)
for r in list(wb.worksheets[0].iter_rows(values_only=True))[2:]:
    if r[0] and r[2] is not None:
        w=str(r[0]).strip().lower(); conc[w]=(float(r[2])-1)/4; val.setdefault(w,[]).append((float(r[6])-1)/4)
wb=openpyxl.load_workbook(R+'resultats_normes/brut/fan2014_normes_affectives_annexe2.xlsx',read_only=True)
for r in list(wb.worksheets[0].iter_rows(values_only=True))[3:]:
    if r[0] and isinstance(r[4],(int,float)): val.setdefault(str(r[0]).strip().lower(),[]).append((float(r[4])-1)/6)
# Wikipédia : total des vues
vues=collections.Counter()
import glob
for f in glob.glob(R+'resultats_usage_wikipedia*/vues_mensuelles.csv'):
    for r in csv.DictReader(open(f,encoding='utf-8')): vues[r['mot']]+=int(r['vues'])
# Ngram : ancien (1800-1849) vs récent (1970-2019)
anc=collections.Counter();rec=collections.Counter();kw=set(names[k] for k in keep)
for r in (row for f in glob.glob(R+'resultats_usage_ngram*/frequences.csv*') for row in csv.reader(gzip.open(f,'rt',encoding='utf-8') if f.endswith('.gz') else open(f,encoding='utf-8'))):
    if r[0] not in kw: continue
    y=int(r[1]) if r[1].isdigit() else 0
    if 1800<=y<1850: anc[r[0]]+=float(r[2])
    elif 1970<=y<2020: rec[r[0]]+=float(r[2])
def epoque(w):
    a,b=anc[w],rec[w]
    return round(float(np.tanh(np.log((b+1e-12)/(a+1e-12))/2)),2) if a+b>0 else None
W=[names[k] for k in keep]
out={'w':W,'x':np.round(X,1).tolist(),'c':cid.tolist(),'s':np.round(np.log1p(fk),2).tolist(),'nb':nb,'lab':labels,
 'oe':[float(info[w]['oral_ecrit'] or 0) for w in W],
 'va':[round(float(np.mean(val[w])),2) if w in val else None for w in W],
 'co':[round(conc[w],2) if w in conc else None for w in W],
 'ep':[epoque(w) for w in W],
 'wk':[vues.get(w,0) for w in W],
 'du':[int(info[w]['durand']=='1') for w in W],
 'stats':[n,int(A.nnz)]}
json.dump(out,open('/tmp/usage/data.json','w'),ensure_ascii=False,separators=(',',':'))
np.save('/tmp/usage/keep.npy',keep); np.save('/tmp/usage/X.npy',X); np.save('/tmp/usage/Z.npy',Z)
# Durand : se regroupent-ils ? part de chaque communauté, et voisinage
du=np.array(out['du'],bool)
from sklearn.neighbors import NearestNeighbors
nn=NearestNeighbors(n_neighbors=11).fit(Z); _,I=nn.kneighbors(Z[du])
part=du[I[:,1:]].mean(); print('Durand : part de Durand parmi les 10 plus proches voisins =',round(part,3),'vs base',round(du.mean(),3))
print('Durand par communauté:',[(k,int(du[cid==k].sum()),int((cid==k).sum())) for k in range(NC+1)])
json.dump({'cid':cid.tolist(),'labels':labels},open('/tmp/usage/com.json','w'),ensure_ascii=False)
print('fini',time.time()-t0)

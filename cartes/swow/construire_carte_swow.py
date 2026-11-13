import numpy as np, scipy.sparse as sp, json, collections, networkx as nx
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
D='/tmp/swow_data/'
names=[l.rstrip('\n') for l in open(D+'names.tsv',encoding='utf8')]
E=np.loadtxt(D+'adjacency.tsv',dtype=np.int64)
n=len(names);A=sp.csr_matrix((E[:,2].astype(float),(E[:,0],E[:,1])),shape=(n,n))
S=A+A.T
# PPMI
tot=S.sum();r=np.asarray(S.sum(1)).ravel();c=np.asarray(S.sum(0)).ravel()
C=S.tocoo();pmi=np.log((C.data*tot)/(r[C.row]*c[C.col]));m=pmi>0
P=sp.csr_matrix((pmi[m],(C.row[m],C.col[m])),shape=(n,n))
Z=TruncatedSVD(120,random_state=1).fit_transform(P);Z/=np.linalg.norm(Z,axis=1,keepdims=True)+1e-9
strength=np.asarray(S.sum(1)).ravel()
keep=np.argsort(-strength)[:3000];ks=set(keep.tolist());pos={int(k):i for i,k in enumerate(keep)}
X=TSNE(3,perplexity=35,init='pca',random_state=2,max_iter=1000).fit_transform(Z[keep])
X-=X.mean(0);X/=np.abs(X).max();X*=260
G=nx.Graph()
Ssub=S[keep][:,keep].tocoo()
for a,b,w in zip(Ssub.row,Ssub.col,Ssub.data):
    if a<b:G.add_edge(int(a),int(b),weight=float(w))
com=nx.community.louvain_communities(G,weight='weight',resolution=1.0,seed=3)
com=sorted(com,key=len,reverse=True)
cid=np.zeros(3000,int)-1
for k,cset in enumerate(com):
    for v in cset:cid[v]=k if k<12 else 12
deg=strength[keep]
labels=[]
for k in range(min(12,len(com))):
    mem=sorted(com[k],key=lambda v:-deg[v])[:4];labels.append(', '.join(names[keep[v]] for v in mem))
# neighbours: outgoing cue->response restricted to kept words, top 8
Ak=A[keep][:,keep].tocsr()
nb=[]
for i in range(3000):
    row=Ak.getrow(i);idx=row.indices;val=row.data
    o=np.argsort(-val)[:8];nb.append([[int(idx[j]),int(val[j])] for j in o])
out={'w':[names[k] for k in keep],'x':np.round(X,1).tolist(),'c':cid.tolist(),'s':np.round(np.log1p(deg),2).tolist(),'nb':nb,'lab':labels,'stats':[n,int(len(E)),int(E[:,2].sum())]}
json.dump(out,open('/tmp/swowmap/data.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(com),[len(x) for x in com[:14]]);print(labels)

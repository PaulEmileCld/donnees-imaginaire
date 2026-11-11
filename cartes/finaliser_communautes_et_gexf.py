import json,numpy as np,networkx as nx,colorsys,os
from sklearn.neighbors import NearestNeighbors
D=json.load(open('data.json')); Z=np.load('Z.npy'); W=D['w']; K=len(W); du=np.array(D['du'],bool); fk=np.array(D['s'])
nn=NearestNeighbors(n_neighbors=16,metric='cosine').fit(Z); dist,I=nn.kneighbors(Z)
G=nx.Graph()
for i in range(K):
    for d,j in zip(dist[i,1:],I[i,1:]): G.add_edge(i,int(j),weight=float(1-d))
com=sorted(nx.community.louvain_communities(G,weight='weight',resolution=1.0,seed=3),key=len,reverse=True)
def lab(cs):
    cs=set(cs); sc={v:(np.mean([j in cs for j in I[v,1:]]))*(1+fk[v]) for v in cs}
    return ', '.join(W[v] for v in sorted(sc,key=lambda v:-sc[v])[:4])
cid=[0]*K
for k,cs in enumerate(com):
    for v in cs: cid[v]=k
D['c']=cid; D['lab']=[lab(c) for c in com]; D['ld']=[int(round(100*du[list(c)].mean())) for c in com]; D['ln']=[len(c) for c in com]
json.dump(D,open('data.json','w'),ensure_ascii=False,separators=(',',':'))
for k,c in enumerate(com): print(k,len(c),D['ld'][k],'%',D['lab'][k])
X=np.array(D['x']);GG=nx.DiGraph()
COL=lambda k:tuple(int(c*255) for c in colorsys.hls_to_rgb(((k*137.508+20)%360)/360,0.62,0.65))
for i,w in enumerate(W):
    r,g,b=COL(cid[i])
    GG.add_node(w,label=w,communaute=D['lab'][cid[i]],durand=bool(D['du'][i]),oral_ecrit=float(D['oe'][i]),
      epoque=float(D['ep'][i]) if D['ep'][i] is not None else 0.0,vues_wikipedia=int(D['wk'][i]),
      viz={'position':{'x':float(X[i,0]*4),'y':float(-X[i,1]*4),'z':float(X[i,2]*4)},'size':float(2+3*D['s'][i]),'color':{'r':r,'g':g,'b':b,'a':1.0}})
for i,l in enumerate(D['nb']):
    for j,v in l: GG.add_edge(W[i],W[j],weight=float(v))
nx.write_gexf(GG,'/home/claude/donnees-imaginaire/cartes/carte_usage.gexf'); print('gexf',GG.number_of_nodes(),GG.number_of_edges())
d=open('data.json').read().replace('</','<\\/');open('/home/claude/carte-usage.html','w').write(open('page.html').read().replace('__DATA__',d))

import json, numpy as np, networkx as nx, time, csv, sys
D=json.load(open('data_niv.json')); W=D['w']; N=int(sys.argv[1]); quoi=sys.argv[2]
niv=D['niv'][4]  # résolution 0,7 : ~32 communautés
G=nx.Graph(); G.add_nodes_from(range(N))
if quoi=='assoc':
    for i in range(N):
        for j,v in D['nb'][i][:6]:
            if j<N: G.add_edge(i,j,weight=G.get_edge_data(i,j,{'weight':0})['weight']+v/1000)
else:
    from sklearn.neighbors import NearestNeighbors
    Z=np.load('Z_ordre.npy')[:N]; d,I=NearestNeighbors(n_neighbors=11,metric='cosine').fit(Z).kneighbors(Z)
    for i in range(N):
        for dd,j in zip(d[i,1:],I[i,1:]): G.add_edge(i,int(j),weight=float(1-dd))
G.remove_nodes_from([n for n in list(G) if G.degree(n)==0])
t=time.time()
pos=nx.forceatlas2_layout(G,max_iter=300,scaling_ratio=2.0,gravity=1.0,strong_gravity=False,linlog=False,weight='weight',seed=1)
print(quoi,G.number_of_nodes(),G.number_of_edges(),'%.0fs'%(time.time()-t))
json.dump({'n':[int(k) for k in pos],'p':[list(map(float,v)) for v in pos.values()],'e':[[int(a),int(b),float(w['weight'])] for a,b,w in G.edges(data=True)]},open(f'fa2_{quoi}.json','w'))

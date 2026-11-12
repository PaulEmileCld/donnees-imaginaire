import json,numpy as np,networkx as nx,colorsys
D=json.load(open('data_niv.json'));W=D['w'];X=np.array(D['x']);G=nx.DiGraph();base=D['niv'][D['defaut']]
COL=lambda k:tuple(int(c*255) for c in colorsys.hls_to_rgb(((k*137.508+20)%360)/360,0.62,0.65))
for i,w in enumerate(W):
    r,g,b=COL(base['c'][i]); a={f"communaute_res_{str(n['res']).replace('.','_')}":int(n['c'][i]) for n in D['niv']}
    G.add_node(w,label=w,communaute=base['lab'][base['c'][i]],oral_ecrit=float(D['oe'][i]),epoque=float(D['ep'][i]) if D['ep'][i] is not None else 0.0,
      vues_wikipedia=int(D['wk'][i]),rang_pertinence=i,**a,viz={'position':{'x':float(X[i,0]*4),'y':float(-X[i,1]*4),'z':float(X[i,2]*4)},'size':float(2+3*D['s'][i]),'color':{'r':r,'g':g,'b':b,'a':1.0}})
for i,l in enumerate(D['nb']):
    for j,v in l: G.add_edge(W[i],W[j],weight=float(v))
nx.write_gexf(G,'/home/claude/donnees-imaginaire/cartes/carte_usage.gexf');print(G.number_of_nodes(),G.number_of_edges())

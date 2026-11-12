"""ForceAtlas2 maison (numpy, répulsion découpée en blocs pour tenir en mémoire), départ depuis la carte t-SNE."""
import json, numpy as np, time, sys
from sklearn.neighbors import NearestNeighbors
D=json.load(open('data_niv.json')); N=int(sys.argv[1]); IT=int(sys.argv[2])
Z=np.load('Z_ordre.npy')[:N]; d,I=NearestNeighbors(n_neighbors=11,metric='cosine').fit(Z).kneighbors(Z)
ed={}
for i in range(N):
    for dd,j in zip(d[i,1:],I[i,1:]):
        k=(min(i,int(j)),max(i,int(j))); ed[k]=max(ed.get(k,0),1-float(dd))
E=np.array(list(ed.keys())); Wt=np.array(list(ed.values()))
deg=np.bincount(E.ravel(),minlength=N).astype(float); m=deg+1
X=np.array(D['x'])[:N,:2].astype(float); X=X/np.abs(X).max()*600
kr,kg=2.0,1.0; speed=np.ones(N); prev=np.zeros((N,2)); t=time.time(); B=1500
for it in range(IT):
    F=np.zeros((N,2))
    for s in range(0,N,B):  # répulsion : kr * m_i * m_j / d
        dx=X[s:s+B,None,:]-X[None,:,:]; r2=(dx**2).sum(-1)+1e-2
        F[s:s+B]+=kr*((m[s:s+B,None]*m[None,:]/r2)[...,None]*dx).sum(1)
    dv=X[E[:,0]]-X[E[:,1]]; a=dv*Wt[:,None]  # attraction linéaire le long des liens
    np.add.at(F,E[:,0],-a); np.add.at(F,E[:,1],a)
    r=np.linalg.norm(X,axis=1,keepdims=True)+1e-9; F-=kg*m[:,None]*X/r  # gravité
    sw=np.linalg.norm(F-prev,axis=1); tr=np.linalg.norm(F+prev,axis=1)/2  # vitesse adaptative (comme FA2)
    gs=max(0.05,min(10,1.0*tr.sum()/(sw.sum()+1e-9))); sp=gs/(1+gs*np.sqrt(sw))
    step=np.minimum(sp[:,None]*F, 10/ (np.linalg.norm(F,axis=1,keepdims=True)+1e-9)*F)
    X+=step; prev=F
    if it%25==0: print(it,'%.0fs'%(time.time()-t),flush=True)
json.dump({'N':N,'p':X.tolist(),'e':E.tolist(),'w':Wt.tolist()},open(f'fa2np_{N}.json','w')); print('fini %.0fs'%(time.time()-t))

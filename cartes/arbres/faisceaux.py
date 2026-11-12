"""Faisceaux de liens (Force-Directed Edge Bundling, Holten & van Wijk 2009), version simplifiée."""
import json, numpy as np, time
D=json.load(open('data_niv.json')); H=json.load(open('fa2np_15096.json')); NS=2000
X=np.array(H['p'])[:NS]; X=(X-X.mean(0))/np.abs(X).max()*400
E=[];vu=set()
for i in range(NS):
    for j,v in D['nb'][i][:3]:
        if j<NS and (min(i,j),max(i,j)) not in vu: vu.add((min(i,j),max(i,j))); E.append((i,j,v))
E=np.array(E); s=X[E[:,0].astype(int)]; t=X[E[:,1].astype(int)]
sw=s[:,0]>t[:,0]; s[sw],t[sw]=t[sw].copy(),s[sw].copy()   # même sens pour tous
ne=len(E); vec=t-s; L=np.linalg.norm(vec,axis=1)+1e-9; mid=(s+t)/2; print(ne,'liens')
# compatibilité (angle, échelle, position)
cos=np.abs(vec@vec.T)/np.outer(L,L); lavg=(L[:,None]+L[None,:])/2
cs=2/(lavg/np.minimum(L[:,None],L[None,:])+np.maximum(L[:,None],L[None,:])/lavg)
cp=lavg/(lavg+np.linalg.norm(mid[:,None]-mid[None],axis=-1)); C=cos*cs*cp; np.fill_diagonal(C,0)
I,J=np.where(C>0.6); CW=C[I,J].astype(np.float32); print(len(I),'paires compatibles')
P=np.stack([s,t],1).astype(np.float32); S=np.float32(4.0); kp=np.float32(0.1)
for cycle,(n_it) in enumerate([50,33,22,15,10,7]):
    # subdiviser : insérer un point au milieu de chaque segment
    Q=np.empty((ne,P.shape[1]*2-1,2),np.float32); Q[:,0::2]=P; Q[:,1::2]=(P[:,:-1]+P[:,1:])/2; P=Q
    for it in range(n_it):
        inner=P[:,1:-1]
        Fs=kp/L[:,None,None].astype(np.float32)*(P[:,:-2]+P[:,2:]-2*inner)
        d=inner[J]-inner[I]; nd=np.linalg.norm(d,axis=-1,keepdims=True)+1e-3
        f=CW[:,None,None]*d/nd; Fe=np.zeros_like(inner); np.add.at(Fe,I,f)
        P[:,1:-1]=inner+S*(Fs+Fe)/np.maximum(1,np.abs(Fs+Fe).max(axis=-1,keepdims=True)/1)  # pas borné
    S=S/2; print('cycle',cycle,P.shape[1],'points',flush=True)
json.dump({'X':X.tolist(),'E':E[:,:2].astype(int).tolist(),'P':P.round(2).tolist()},open('faisceaux.json','w'))

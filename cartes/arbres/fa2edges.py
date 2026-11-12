import json, numpy as np, sys, time
def fa2(X,E,Wt,IT=400,kr=1.0,kg=0.6,linlog=False):
    N=len(X); deg=np.bincount(E.ravel(),minlength=N).astype(float); m=deg+1; prev=np.zeros((N,2)); Wt=Wt/Wt.mean()
    for it in range(IT):
        dx=X[:,None,:]-X[None,:,:]; r2=(dx**2).sum(-1)+1e-2
        F=kr*((m[:,None]*m[None,:]/r2)[...,None]*dx).sum(1)
        dv=X[E[:,0]]-X[E[:,1]]
        if linlog: dv=dv*(np.log1p(np.linalg.norm(dv,axis=1))/(np.linalg.norm(dv,axis=1)+1e-9))[:,None]
        a=dv*Wt[:,None]; np.add.at(F,E[:,0],-a); np.add.at(F,E[:,1],a)
        r=np.linalg.norm(X,axis=1,keepdims=True)+1e-9; F-=kg*m[:,None]*X/r
        sw=np.linalg.norm(F-prev,axis=1); tr=np.linalg.norm(F+prev,axis=1)/2
        gs=max(0.05,min(10,tr.sum()/(sw.sum()+1e-9))); sp=gs/(1+gs*np.sqrt(sw))
        X=X+np.minimum(sp[:,None],10/(np.linalg.norm(F,axis=1,keepdims=True)+1e-9))*F; prev=F
    return X
A=json.load(open('arbres.json')); H=json.load(open('fa2np_15096.json')); X0=np.array(H['p'])[:2000]; X0=(X0-X0.mean(0))/np.abs(X0).max()*400
out={}
for k in ('arbre','pf'):
    e=np.array([[a,b] for a,b,_ in A[k]]); w=np.array([v for *_,v in A[k]]); t=time.time()
    out[k]=fa2(X0.copy(),e,w).tolist(); print(k,'%.0fs'%(time.time()-t),flush=True)
json.dump(out,open('arbres_pos.json','w'))

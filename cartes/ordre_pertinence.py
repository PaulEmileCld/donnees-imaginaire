"""Trie les mots par pertinence (fréquence d'usage + nombre de liens), pour que la page puisse n'afficher que les N premiers."""
import json, numpy as np
D=json.load(open('data.json')); K=len(D['w'])
deg=np.zeros(K)
for i,l in enumerate(D['nb']):
    deg[i]+=len(l)
    for j,_ in l: deg[j]+=1
s=np.array(D['s']); z=lambda v:(v-v.mean())/(v.std()+1e-9)
score=z(s)+z(np.log1p(deg))
o=np.argsort(-score); pos=np.empty(K,int); pos[o]=np.arange(K)
for k in ['w','x','c','s','oe','va','co','ep','wk','du']: D[k]=[D[k][i] for i in o]
D['nb']=[[[int(pos[j]),v] for j,v in D['nb'][i]] for i in o]
json.dump(D,open('data.json','w'),ensure_ascii=False,separators=(',',':'))
print('ordre ok', D['w'][:15], D['w'][-10:])

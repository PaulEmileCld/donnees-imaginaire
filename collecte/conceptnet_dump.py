"""ConceptNet 5.7 en entier, sans passer par l'API : on lit le fichier complet téléchargé
(conceptnet-assertions-5.7.0.csv.gz) et on garde tout ce qui touche au français.
Sorties (resultats_conceptnet_dump/) :
  aretes_fr_fr_*.csv.gz  : toutes les relations entre deux mots français
  aretes_liste_*.csv.gz  : toutes les relations (vers toutes langues) des mots de notre liste, avec la phrase d'origine
  vecteurs_liste.txt.gz  : position sémantique Numberbatch (300 dimensions) de nos mots, si le fichier est là
"""
import gzip, json, csv, os, sys, io
R = "resultats_conceptnet_dump"; os.makedirs(R, exist_ok=True)
liste = set(l.strip().lower() for l in open("collecte/mots_usage.txt", encoding="utf-8") if l.strip())
acc = json.load(open("collecte/accents.json", encoding="utf-8"))
liste |= {(acc.get(m) or m).lower() for m in open("collecte/mots_durand.txt", encoding="utf-8").read().split()}
cle = lambda m: m.replace(" ", "_")
cles = {cle(m): m for m in liste}
def terme(uri):  # /c/fr/eau/n/... -> ("fr", "eau")
    p = uri.split("/"); return (p[2], p[3]) if len(p) > 3 else (None, None)
class Rotatif:   # fichiers gzip découpés sous 80 Mo (limite GitHub : 100 Mo)
    def __init__(s, base, entete): s.base, s.entete, s.n, s.f = base, entete, 0, None; s.ouvre()
    def ouvre(s):
        if s.f: s.f.close()
        if s.f: s.brut.close()
        s.n += 1; s.brut = open(f"{R}/{s.base}_{s.n}.csv.gz", "wb")
        s.f = io.TextIOWrapper(gzip.GzipFile(fileobj=s.brut, mode="wb"), encoding="utf-8", newline="")
        s.w = csv.writer(s.f); s.w.writerow(s.entete)
    def ecrit(s, r):
        s.w.writerow(r)
        if s.brut.tell() > 80_000_000: s.ouvre()
    def ferme(s): s.f.close(); s.brut.close()
ff = Rotatif("aretes_fr_fr", ["relation", "debut", "fin", "poids", "source"])
wl = Rotatif("aretes_liste", ["mot", "sens", "relation", "autre", "langue_autre", "poids", "source", "phrase"])
etat = {"lignes_lues": 0, "fr_fr": 0, "liste": 0, "mots_liste_trouves": 0, "relations": {}}
vus = set()
with gzip.open(sys.argv[1], "rt", encoding="utf-8") as f:
    for ligne in f:
        etat["lignes_lues"] += 1
        if "/c/fr/" not in ligne: continue
        _, rel, a, b, js = ligne.rstrip("\n").split("\t")
        la, ta = terme(a); lb, tb = terme(b)
        if "fr" not in (la, lb): continue
        info = json.loads(js); w = info.get("weight", 1); src = info.get("dataset", ""); rel = rel.replace("/r/", "")
        if la == lb == "fr":
            ff.ecrit([rel, ta.replace("_", " "), tb.replace("_", " "), w, src]); etat["fr_fr"] += 1
            etat["relations"][rel] = etat["relations"].get(rel, 0) + 1
        for (l1, t1, l2, t2, sens) in ((la, ta, lb, tb, "sortant"), (lb, tb, la, ta, "entrant")):
            if l1 == "fr" and t1 in cles:
                wl.ecrit([cles[t1], sens, rel, t2.replace("_", " "), l2, w, src, info.get("surfaceText") or ""]); etat["liste"] += 1; vus.add(t1)
ff.ferme(); wl.ferme(); etat["mots_liste_trouves"] = len(vus); etat["mots_liste"] = len(liste)
if len(sys.argv) > 2 and os.path.exists(sys.argv[2]):   # vecteurs Numberbatch
    n = 0
    with gzip.open(sys.argv[2], "rt", encoding="utf-8") as f, gzip.open(f"{R}/vecteurs_liste.txt.gz", "wt", encoding="utf-8") as o:
        for ligne in f:
            if not ligne.startswith("/c/fr/"): continue
            t = ligne.split(" ", 1)[0][6:]
            if t in cles: o.write(cles[t] + " " + ligne.split(" ", 1)[1]); n += 1
    etat["vecteurs"] = n
json.dump(etat, open(f"{R}/etat.json", "w"), indent=1, ensure_ascii=False); print(etat)

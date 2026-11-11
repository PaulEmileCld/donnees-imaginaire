"""Collecte des associations libres (r_associated) de JeuxDeMots autour des mots de Durand.
Reprend là où elle s'est arrêtée : chaque mot interrogé est gardé dans cache.jsonl.

RÉGLAGES (modifiables) :"""
SEUILS = [10, 5, 3]      # nombre de liens suivis à la profondeur 1, 2 et 3
NB_TEMOINS = 200         # mots tirés au hasard, comme groupe témoin
PAUSE = 1.0              # secondes entre deux requêtes, par politesse
DUREE_MAX = 5 * 3600     # au-delà, on s'arrête et on reprendra au prochain passage

import json, os, re, time, random, urllib.request, urllib.parse, csv
API = "https://jdm-api.demo.lirmm.fr/v0"
UA = {"User-Agent": "donnees-imaginaire (projet personnel de cartographie de l'imaginaire)"}
D = "collecte"; R = "resultats"; os.makedirs(R, exist_ok=True)
CACHE = f"{R}/cache.jsonl"; T0 = time.time()
cache = {}
if os.path.exists(CACHE):
    for l in open(CACHE, encoding="utf-8"):
        e = json.loads(l); cache[e["q"]] = e
fcache = open(CACHE, "a", encoding="utf-8")
BON = re.compile(r"^[a-zàâäçéèêëîïôöùûüÿœæ][a-zàâäçéèêëîïôöùûüÿœæ' -]{1,30}$", re.I)

def get(chemin):
    time.sleep(PAUSE)
    try:
        with urllib.request.urlopen(urllib.request.Request(API + chemin, headers=UA), timeout=120) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return None if e.code in (400, 404) else {"erreur": e.code}
    except Exception as e:
        return {"erreur": str(e)}

def voisins(nom):
    """Associations sortantes d'un terme, triées par poids décroissant."""
    if nom in cache: return cache[nom]["v"]
    if time.time() - T0 > DUREE_MAX: raise TimeoutError
    d = get(f"/relations/from/{urllib.parse.quote(nom)}?types_ids=0&min_weight=1&limit=5000")
    if d and "erreur" in d:
        time.sleep(30); d = get(f"/relations/from/{urllib.parse.quote(nom)}?types_ids=0&min_weight=1&limit=5000")
        if d and "erreur" in d: raise TimeoutError   # API indisponible : on reprendra plus tard
    v = []
    if d:
        noms = {n["id"]: n for n in d.get("nodes", [])}
        for rel in d.get("relations", []):
            n = noms.get(rel["node2"])
            if n and n.get("type") == 1 and rel["w"] > 0 and BON.match(n["name"]) and n["name"] != nom:
                v.append([n["name"], rel["w"]])
        v.sort(key=lambda x: -x[1])
    e = {"q": nom, "v": v[:50]}; cache[nom] = e
    fcache.write(json.dumps(e, ensure_ascii=False) + "\n"); fcache.flush()
    return e["v"]

accents = json.load(open(f"{D}/accents.json", encoding="utf-8"))
mots = [l.strip() for l in open(f"{D}/mots_durand.txt", encoding="utf-8") if l.strip()]
noeuds, liens, introuvables = {}, {}, []
def ajoute(nom, prof, origine):
    if nom not in noeuds or noeuds[nom][0] > prof: noeuds[nom] = [prof, origine]

termine = True
try:
    niveau = []
    for m in mots:
        essais = [accents.get(m), m.lower(), m.capitalize()]
        trouve = None
        for e in [x for x in essais if x]:
            if voisins(e): trouve = e; break
        if trouve: ajoute(trouve, 0, "durand"); niveau.append(trouve)
        else: introuvables.append(m)
    for prof, k in enumerate(SEUILS, start=1):
        suivant = []
        for nom in niveau:
            for cible, w in voisins(nom)[:k]:
                liens[(nom, cible)] = w; ajoute(cible, prof, "voisin")
                if noeuds[cible][0] == prof: suivant.append(cible)
        niveau = list(dict.fromkeys(suivant))
    # groupe témoin : mots tirés au hasard dans le réseau
    temoins = [n for n, (p, o) in noeuds.items() if o == "temoin"]
    fichier_t = f"{R}/temoins.txt"
    if os.path.exists(fichier_t):
        temoins = [l.strip() for l in open(fichier_t, encoding="utf-8") if l.strip()]
    essais = 0
    while len(temoins) < NB_TEMOINS and essais < 400:
        essais += 1
        d = get("/relations/random?types_ids=0&limit=100&min_weight=20")
        if not d or "erreur" in d: continue
        for n in d.get("nodes", []):
            if n.get("type") == 1 and n.get("w", 0) >= 200 and BON.match(n["name"]) and n["name"].islower() \
               and n["name"] not in noeuds and n["name"] not in temoins:
                temoins.append(n["name"])
    temoins = temoins[:NB_TEMOINS]
    open(fichier_t, "w", encoding="utf-8").write("\n".join(temoins))
    for t in temoins:
        v = voisins(t)
        if not v: continue
        ajoute(t, 0, "temoin")
        for cible, w in v[:SEUILS[0]]:
            liens[(t, cible)] = w; ajoute(cible, 1, "voisin")
except TimeoutError:
    termine = False

with open(f"{R}/noeuds.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["Id", "Label", "profondeur", "origine"])
    for nom, (p, o) in noeuds.items(): w.writerow([nom, nom, p, o])
with open(f"{R}/liens.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["Source", "Target", "Weight", "Type"])
    for (a, b), p in liens.items(): w.writerow([a, b, p, "Directed"])
open(f"{R}/introuvables.txt", "w", encoding="utf-8").write("\n".join(introuvables))
etat = {"termine": termine, "mots_interroges": len(cache), "noeuds": len(noeuds), "liens": len(liens), "introuvables": len(introuvables)}
json.dump(etat, open(f"{R}/etat.json", "w"), indent=1); print(etat)
if termine: open(f"{R}/TERMINE", "w").write("ok")

"""Réseau JeuxDeMots des 10 000 mots les plus usuels (+ mots de Durand, en calque).
Pour chaque mot : toutes ses associations vers les autres mots de la liste, et ses 20 plus fortes vers l'extérieur.
Reprend là où elle s'est arrêtée (cache.jsonl)."""
PAUSE = 1.2; DUREE_MAX = 5 * 3600; EXTERIEUR = 20
import json, os, re, time, csv, urllib.request, urllib.parse
API = "https://jdm-api.demo.lirmm.fr/v0"
UA = {"User-Agent": "donnees-imaginaire (https://github.com/PaulEmileCld/donnees-imaginaire)"}
R = "resultats_usage"; os.makedirs(R, exist_ok=True); T0 = time.time()
infos = {r["mot"]: r for r in csv.DictReader(open("collecte/mots_usage.csv", encoding="utf-8"))}
acc = json.load(open("collecte/accents.json", encoding="utf-8"))
for m in open("collecte/mots_durand.txt", encoding="utf-8").read().split():
    f = acc.get(m) or m.lower()
    infos.setdefault(f, {"mot": f, "rang": "", "categorie": "", "freq_films": "", "freq_livres": "", "oral_ecrit": "", "durand": "1"})
LISTE = set(infos)
import gzip, glob
cache = {}   # cache.jsonl (les 10 000 premiers) puis cache_2.jsonl.gz (la suite, compressée : limite GitHub de 100 Mo par fichier)
for fich in sorted(glob.glob(f"{R}/cache*.jsonl*")):
    for l in (gzip.open(fich, "rt", encoding="utf-8") if fich.endswith(".gz") else open(fich, encoding="utf-8")):
        if l.strip(): e = json.loads(l); cache[e["q"]] = e
fc = gzip.open(f"{R}/cache_2.jsonl.gz", "at", encoding="utf-8")
BON = re.compile(r"^[a-zàâäçéèêëîïôöùûüÿœæ][a-zàâäçéèêëîïôöùûüÿœæ' -]{1,30}$", re.I)
def get(nom):
    time.sleep(PAUSE)
    u = f"{API}/relations/from/{urllib.parse.quote(nom)}?types_ids=0&min_weight=1&limit=5000"
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120) as r: return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e: return None if e.code in (400, 404) else {"erreur": e.code}
    except Exception as e: return {"erreur": str(e)}
termine = True; erreurs = {}; consecutives = 0
try:
    for nom in sorted(LISTE, key=lambda m: int(infos[m]["rang"] or 99999)):
        if nom in cache: continue
        if time.time() - T0 > DUREE_MAX: raise TimeoutError
        d = get(nom)
        if d and "erreur" in d:
            time.sleep(20); d = get(nom)
        if d and "erreur" in d:          # mot en échec : on le note et on passe au suivant
            erreurs[nom] = str(d["erreur"]); consecutives += 1
            if consecutives >= 15: raise TimeoutError   # serveur vraiment indisponible : on reprendra plus tard
            time.sleep(30); continue
        consecutives = 0
        dedans, dehors = [], []
        if d:
            noms = {n["id"]: n for n in d.get("nodes", [])}
            for rel in d.get("relations", []):
                n = noms.get(rel["node2"])
                if not n or n.get("type") != 1 or rel["w"] <= 0 or n["name"] == nom: continue
                (dedans if n["name"] in LISTE else dehors).append([n["name"], rel["w"]])
            dehors = [x for x in dehors if BON.match(x[0])]
            dehors.sort(key=lambda x: -x[1])
        e = {"q": nom, "trouve": bool(d), "in": dedans, "out": dehors[:EXTERIEUR]}
        cache[nom] = e; fc.write(json.dumps(e, ensure_ascii=False) + "\n")
except TimeoutError:
    termine = False
fc.close()
# les liens « internes » sont recalculés sur la liste actuelle (un ancien lien « extérieur » peut être devenu interne)
for e in cache.values():
    tout = e["in"] + e["out"]; e["in"] = [x for x in tout if x[0] in LISTE]; e["out"] = [x for x in tout if x[0] not in LISTE]
with open(f"{R}/noeuds.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["Id", "Label", "rang", "categorie", "freq_films", "freq_livres", "oral_ecrit", "durand", "trouve_jdm"])
    for m in LISTE:
        i = infos[m]; w.writerow([m, m, i["rang"], i["categorie"], i["freq_films"], i["freq_livres"], i["oral_ecrit"], i["durand"], int(cache.get(m, {}).get("trouve", False))])
nb = 0
with gzip.open(f"{R}/liens.csv.gz", "wt", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["Source", "Target", "Weight", "Type"])
    for m, e in cache.items():
        for c, p in e["in"]: w.writerow([m, c, p, "Directed"]); nb += 1
with gzip.open(f"{R}/liens_exterieurs.csv.gz", "wt", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["Source", "Target", "Weight"])
    for m, e in cache.items():
        for c, p in e["out"]: w.writerow([m, c, p])
etat = {"termine": termine, "mots": len(LISTE), "interroges": len(cache), "trouves": sum(e["trouve"] for e in cache.values()), "liens_internes": nb, "erreurs": len(erreurs), "exemples_erreurs": dict(list(erreurs.items())[:10])}
json.dump(etat, open(f"{R}/etat.json", "w"), indent=1); print(etat)
if termine and not erreurs: open(f"{R}/TERMINE", "w").write("ok")

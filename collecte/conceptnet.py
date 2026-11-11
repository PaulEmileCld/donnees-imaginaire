"""Collecte ConceptNet approfondie (CC BY-SA 4.0), en français.
Part des mots de Durand puis explore les voisins des voisins (en largeur) jusqu'à l'heure limite.
Pour chaque mot : liens typés, traductions et voisins les plus proches (Numberbatch)."""
PAUSE = 1.2                         # environ une requête par seconde, par politesse
HEURE_LIMITE_UTC = "14:50"          # arrêt vers 15 h 50 à Paris
VOISINS_SUIVIS = 10                 # pour chaque mot, nombre de voisins ajoutés à l'exploration
import json, os, time, csv, datetime, urllib.request, urllib.parse
API = "https://api.conceptnet.io"
UA = {"User-Agent": "donnees-imaginaire (projet personnel de cartographie de l'imaginaire)"}
R = "resultats_conceptnet"; os.makedirs(R, exist_ok=True)
h, mi = map(int, HEURE_LIMITE_UTC.split(":"))
now = datetime.datetime.now(datetime.timezone.utc)
limite = now.replace(hour=h, minute=mi, second=0, microsecond=0)
if limite <= now: limite = now + datetime.timedelta(hours=4, minutes=45)
def get(chemin):
    time.sleep(PAUSE)
    for essai in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(API + chemin, headers=UA), timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(15 * (essai + 1))
        except Exception:
            time.sleep(15 * (essai + 1))
    return {"erreur": True}
def cle(nom): return urllib.parse.quote(nom.lower().replace(" ", "_"))
def lisible(uri): return uri.split("/")[3].replace("_", " ")
EXCLUS = {"ExternalURL", "dbpedia/genre", "FormOf", "EtymologicallyDerivedFrom", "EtymologicallyRelatedTo", "dbpedia/occupation"}
accents = json.load(open("collecte/accents.json", encoding="utf-8"))
depart = [(accents.get(m) or m.lower()) for m in (l.strip() for l in open("collecte/mots_durand.txt", encoding="utf-8")) if m]
file = [(m, 0, "durand") for m in depart]; vus = {m.lower() for m in depart}
noeuds, aretes, proches = {}, [], []
bilan = {"interroges": 0, "avec_donnees": 0, "erreurs": 0, "profondeur_max": 0}
erreurs_suite = 0
while file and datetime.datetime.now(datetime.timezone.utc) < limite and erreurs_suite < 30:
    nom, prof, origine = file.pop(0); c = cle(nom); bilan["interroges"] += 1
    candidats = []
    d = get(f"/c/fr/{c}?limit=300")
    if d and "erreur" in d: bilan["erreurs"] += 1; erreurs_suite += 1; d = None
    else: erreurs_suite = 0
    for e in (d or {}).get("edges", []):
        rel = e["rel"]["label"]
        if rel in EXCLUS: continue
        s, t = e["start"], e["end"]
        autre = t if s.get("@id", "").startswith(f"/c/fr/{c}") else s
        lab, lang = autre.get("label", ""), autre.get("language", "")
        aretes.append([nom, rel, lab, lang, round(e.get("weight", 0), 3),
                       "sortant" if autre is t else "entrant", (e.get("surfaceText") or "").replace("\n", " ")])
        if lang == "fr" and rel not in ("Synonym", "Antonym") or lang == "fr":
            candidats.append((e.get("weight", 0), lisible(autre["@id"])))
    d = get(f"/related/c/fr/{c}?filter=/c/fr&limit=25")
    if d and "erreur" in d: bilan["erreurs"] += 1; d = None
    for r in (d or {}).get("related", []):
        v = lisible(r["@id"])
        if v.lower() != nom.lower():
            proches.append([nom, v, round(r["weight"], 4)]); candidats.append((r["weight"] * 5, v))
    if candidats or d: bilan["avec_donnees"] += 1
    noeuds[nom] = [prof, origine]
    bilan["profondeur_max"] = max(bilan["profondeur_max"], prof)
    candidats.sort(key=lambda x: -x[0]); ajoutes = 0
    for _, v in candidats:
        if ajoutes >= VOISINS_SUIVIS: break
        if v.lower() not in vus and 1 < len(v) < 40:
            vus.add(v.lower()); file.append((v, prof + 1, "voisin")); ajoutes += 1
    if bilan["interroges"] % 300 == 0: print(bilan, len(file), flush=True)
with open(f"{R}/noeuds.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["Id", "Label", "profondeur", "origine"])
    for n, (p, o) in noeuds.items(): w.writerow([n, n, p, o])
with open(f"{R}/aretes.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["mot", "relation", "autre", "langue", "poids", "sens", "phrase"]); w.writerows(aretes)
with open(f"{R}/proches.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["mot", "voisin", "proximite"]); w.writerows(proches)
bilan.update({"aretes": len(aretes), "proches": len(proches), "en_attente": len(file),
              "arret": "API indisponible" if erreurs_suite >= 30 else ("heure limite" if file else "exploration complete")})
json.dump(bilan, open(f"{R}/etat.json", "w"), indent=1); print(bilan)

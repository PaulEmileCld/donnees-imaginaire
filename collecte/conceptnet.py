"""Collecte ConceptNet (CC BY-SA 4.0) pour les mots de Durand, en français.
Pour chaque mot : ses liens typés, ses traductions anglaises et ses voisins les plus proches (Numberbatch)."""
PAUSE = 1.2   # l'API publique demande de rester sous environ une requête par seconde
import json, os, time, csv, urllib.request, urllib.parse
API = "https://api.conceptnet.io"
UA = {"User-Agent": "donnees-imaginaire (projet personnel de cartographie de l'imaginaire)"}
R = "resultats_conceptnet"; os.makedirs(R, exist_ok=True)
def get(chemin):
    time.sleep(PAUSE)
    for essai in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(API + chemin, headers=UA), timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(20 * (essai + 1))
        except Exception:
            time.sleep(20 * (essai + 1))
    return {"erreur": True}
accents = json.load(open("collecte/accents.json", encoding="utf-8"))
mots = [l.strip() for l in open("collecte/mots_durand.txt", encoding="utf-8") if l.strip()]
aretes, proches, bilan = [], [], {"mots": 0, "avec_liens": 0, "erreurs": 0}
def cle(m): return urllib.parse.quote((accents.get(m) or m).lower().replace(" ", "_"))
for m in mots:
    bilan["mots"] += 1; c = cle(m); nom = (accents.get(m) or m.lower())
    d = get(f"/c/fr/{c}?limit=500")
    if d and "erreur" in d: bilan["erreurs"] += 1; d = None
    n = 0
    for e in (d or {}).get("edges", []):
        s, t = e["start"], e["end"]
        autre = t if s.get("@id", "").startswith(f"/c/fr/{c}") else s
        aretes.append([nom, e["rel"]["label"], autre.get("label", ""), autre.get("language", ""),
                       round(e.get("weight", 0), 3), "sortant" if autre is t else "entrant",
                       (e.get("surfaceText") or "").replace("\n", " ")])
        n += 1
    if n: bilan["avec_liens"] += 1
    d = get(f"/related/c/fr/{c}?filter=/c/fr&limit=25")
    if d and "erreur" in d: bilan["erreurs"] += 1; d = None
    for r in (d or {}).get("related", []):
        voisin = r["@id"].split("/")[3].replace("_", " ")
        if voisin != nom.lower(): proches.append([nom, voisin, round(r["weight"], 4)])
with open(f"{R}/aretes.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["mot", "relation", "autre", "langue", "poids", "sens", "phrase"]); w.writerows(aretes)
with open(f"{R}/proches.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["mot", "voisin", "proximite"]); w.writerows(proches)
bilan["aretes"] = len(aretes); bilan["proches"] = len(proches)
json.dump(bilan, open(f"{R}/etat.json", "w"), indent=1); print(bilan)

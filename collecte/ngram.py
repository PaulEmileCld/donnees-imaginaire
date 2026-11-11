"""Fréquence des mots de Durand dans les livres français numérisés (Google Books Ngram, corpus français 2019).
Adresse non officielle : on reste très lent et on s'arrête au premier refus."""
import json, os, time, csv, urllib.request, urllib.parse
from commun import mots_a_traiter, dossier
R = dossier("resultats_ngram"); os.makedirs(R, exist_ok=True)
UA = "Mozilla/5.0 (compatible; donnees-imaginaire; +https://github.com/PaulEmileCld/donnees-imaginaire)"
mots = mots_a_traiter(); lignes, etat = [], {"requetes": 0, "refus": 0, "corpus": None}
DEBUT, FIN = 1800, 2019
for corpus in ["fr-2019", "fr"]:               # on garde le premier corpus qui répond
    lignes.clear(); etat.update(requetes=0, refus=0)
    for i in range(0, len(mots), 10):
        lot = [f for _, f in mots[i:i + 10]]
        url = "https://books.google.com/ngrams/json?" + urllib.parse.urlencode({"content": ",".join(lot),
              "year_start": DEBUT, "year_end": FIN, "corpus": corpus, "smoothing": 0, "case_insensitive": "true"})
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
                d = json.loads(r.read().decode("utf-8"))
        except Exception as e:
            etat["refus"] += 1; etat["derniere_erreur"] = str(e)[:200]
            if etat["refus"] >= 3: break
            time.sleep(60); continue
        etat["requetes"] += 1
        for s in d:
            ng = s["ngram"]
            if s.get("type") == "CASE_INSENSITIVE" or ng.endswith(" (All)") or not any(x.get("ngram", "").endswith(" (All)") for x in d):
                mot = ng.replace(" (All)", "")
                for k, v in enumerate(s["timeseries"]): lignes.append([mot, DEBUT + k, v])
        time.sleep(4)
    if lignes: etat["corpus"] = corpus; break
import gzip
ouvrir = (lambda: gzip.open(f"{R}/frequences.csv.gz", "wt", newline="", encoding="utf-8")) if os.environ.get("LISTE") else (lambda: open(f"{R}/frequences.csv", "w", newline="", encoding="utf-8"))
with ouvrir() as f:
    w = csv.writer(f); w.writerow(["mot", "annee", "frequence_relative"]); w.writerows(lignes)
etat["mots_trouves"] = len({l[0] for l in lignes}); json.dump(etat, open(f"{R}/etat.json", "w"), indent=1); print(etat)

"""Qualités des mots : fréquence (Lexique 3.83) et normes psychologiques françaises
(concrétude, imagerie, valence émotionnelle, activation). On tente plusieurs sources connues ;
celles qui ne répondent pas sont simplement notées dans etat.json."""
import json, os, time, urllib.request
from commun import UA
R = "resultats_normes"; os.makedirs(f"{R}/brut", exist_ok=True)
SOURCES = {
 "lexique383.tsv": ["http://www.lexique.org/databases/Lexique383/Lexique383.tsv",
                    "https://raw.githubusercontent.com/chrplr/openlexicon/master/datasets-info/Lexique382/README-Lexique.md"],
}
def esm(doi_suffixe, prefixe, n=4):  # annexes Springer (Behavior Research Methods)
    out = []
    for k in range(1, n + 1):
        for ext in ["xlsx", "xls", "csv", "txt", "zip"]:
            out.append(f"https://static-content.springer.com/esm/art%3A10.3758%2F{doi_suffixe}/MediaObjects/{prefixe}_MOESM{k}_ESM.{ext}")
    return out
ANNEXES = {
 "bonin2018_concretude_valence_1659": esm("s13428-018-1014-y", "13428_2018_1014"),
 "fancat2020_emotions_10_categories": esm("s13428-020-01450-z", "13428_2020_1450"),
 "fan2014_normes_affectives": esm("s13428-013-0431-1", "13428_2013_431"),
 "desrochers2009_imagerie_3600": esm("BRM.41.2.546", "13428_2009_41_2_546", 2),
}
etat = {}
def tente(nom, urls):
    for u in urls:
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=120) as r:
                data = r.read()
            if len(data) < 500 or data[:15].lower().startswith(b"<!doctype html"): continue
            ext = u.rsplit(".", 1)[-1]; f = f"{R}/brut/{nom}" + ("" if nom.endswith(ext) else "." + ext)
            open(f, "wb").write(data); return {"ok": u, "taille": len(data)}
        except Exception: pass
        finally: time.sleep(1)
    return {"ok": None}
for nom, urls in SOURCES.items(): etat[nom] = tente(nom, urls)
for nom, urls in ANNEXES.items():
    trouves = []
    for k in range(1, 5):
        r = tente(f"{nom}_annexe{k}", [u for u in urls if f"MOESM{k}_" in u])
        if r["ok"]: trouves.append(r)
    etat[nom] = trouves or {"ok": None}
json.dump(etat, open(f"{R}/etat.json", "w"), indent=1); print(json.dumps(etat, indent=1))

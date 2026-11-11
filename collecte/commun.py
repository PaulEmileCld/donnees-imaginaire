import json, unicodedata
UA = "donnees-imaginaire/1.0 (https://github.com/PaulEmileCld/donnees-imaginaire) python-urllib"
def mots_accentues():
    acc = json.load(open("collecte/accents.json", encoding="utf-8"))
    return [(m, acc.get(m) or m.lower()) for m in (l.strip() for l in open("collecte/mots_durand.txt", encoding="utf-8")) if m]
def norm(s): return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn").strip()

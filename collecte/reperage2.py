"""Second repérage : types de relations, essai de l'API et correspondance des mots (accents)."""
import json, time, unicodedata, urllib.request, urllib.parse, zipfile, io, os, re
UA = {"User-Agent": "donnees-imaginaire (projet personnel de cartographie de l'imaginaire)"}
API = "https://jdm-api.demo.lirmm.fr"
SITE = "https://www.jeuxdemots.org/JDM-LEXICALNET-FR/"
OUT = "reperage2"; os.makedirs(OUT, exist_ok=True)
def get(url, binaire=False):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r:
        d = r.read(); return d if binaire else d.decode("utf-8", "replace")
def sauve(nom, texte): open(f"{OUT}/{nom}", "w", encoding="utf-8").write(texte)
def norm(s): return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn").strip()

# 1. API : types de relations et deux essais (une requête par seconde au plus)
for nom, url in [("types.json", "/v0/relations_types"),
                 ("essai_eau.json", "/v0/relations/from/eau?types_ids=0&limit=10"),
                 ("essai_aleatoire.json", "/v0/relations/random?types_ids=0&limit=5")]:
    try: sauve(nom, get(API + url))
    except Exception as e: sauve(nom, f"ERREUR {e}")
    time.sleep(1)

# 2. Site : README et liste des relations (robots.txt demande 60 s entre deux requêtes)
for nom in ["JEUXDEMOTS-README.txt", "RELATION_LIST.txt"]:
    try: sauve(nom, get(SITE + nom))
    except Exception as e: sauve(nom, f"ERREUR {e}")
    time.sleep(61)

# 3. Liste des termes : retrouver la forme accentuée des 508 mots de Durand
mots = [l.strip() for l in open("collecte/mots_durand.txt", encoding="utf-8") if l.strip()]
cibles = {norm(m): m for m in mots}
trouve = {}; debut = []
try:
    data = get(SITE + "20240924-LEXICALNET-JEUXDEMOTS-ENTRIES.txt", binaire=True)
    for i, ligne in enumerate(data.decode("utf-8", "replace").splitlines()):
        if i < 40: debut.append(ligne)
        for champ in re.split(r"[;\t|]", ligne):
            c = champ.strip().strip('"')
            n = norm(c)
            if n in cibles and len(trouve.setdefault(cibles[n], [])) < 6 and c not in trouve[cibles[n]]:
                trouve[cibles[n]].append(c)
    sauve("termes_debut.txt", "\n".join(debut))
except Exception as e:
    sauve("termes_debut.txt", f"ERREUR {e}")
sauve("correspondances.json", json.dumps(trouve, ensure_ascii=False, indent=1))
print(len(trouve), "mots retrouvés sur", len(mots))

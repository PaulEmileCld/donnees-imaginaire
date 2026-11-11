"""Liste de départ « par l'usage » : les N mots pleins (noms, verbes, adjectifs) les plus fréquents du français,
d'après Lexique 3.83. Fréquence = moyenne entre sous-titres de films (oral) et livres (écrit)."""
N = 10000
import csv, json
lem = {}
for r in csv.DictReader(open("resultats_normes/brut/lexique383.tsv", encoding="utf-8"), delimiter="\t"):
    if r["islem"] != "1" or r["cgram"] not in ("NOM", "VER", "ADJ"): continue
    e = lem.setdefault(r["lemme"], {"films": 0.0, "livres": 0.0, "cat": {}})
    f, l = float(r["freqlemfilms2"] or 0), float(r["freqlemlivres"] or 0)
    e["cat"][r["cgram"]] = max(e["cat"].get(r["cgram"], 0), f + l)
    e["films"] = max(e["films"], f); e["livres"] = max(e["livres"], l)
acc = json.load(open("collecte/accents.json", encoding="utf-8"))
durand = {(acc.get(m) or m.lower()) for m in open("collecte/mots_durand.txt", encoding="utf-8").read().split()}
ok = {m: e for m, e in lem.items() if e["films"] >= 0.3 and e["livres"] >= 0.3 and len(m) > 2 and "sous-titr" not in m}
# un mot présent dans un seul des deux corpus est presque toujours un nom propre, une coquille ou un artefact de sous-titres
rang = sorted(ok.items(), key=lambda x: -(x[1]["films"] + x[1]["livres"]))[:N]
with open("collecte/mots_usage.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["mot", "rang", "categorie", "freq_films", "freq_livres", "oral_ecrit", "durand"])
    for i, (m, e) in enumerate(rang, 1):
        cat = max(e["cat"], key=e["cat"].get); t = e["films"] + e["livres"]
        w.writerow([m, i, cat, round(e["films"], 2), round(e["livres"], 2), round((e["films"] - e["livres"]) / t, 3) if t else 0, int(m in durand)])
open("collecte/mots_usage.txt", "w", encoding="utf-8").write("\n".join(m for m, _ in rang))
print(len(rang), "mots ;", sum(m in durand for m, _ in rang), "mots de Durand dedans")

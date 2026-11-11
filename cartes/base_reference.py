"""Base de référence : une ligne par mot, avec tout ce qu'on sait de lui (pour les cartes, les jeux, les quiz…).
Sortie : cartes/base_mots.csv.gz  (s'ouvre dans un tableur après décompression, ou directement en Python)."""
import csv, gzip, json, glob, os, collections, openpyxl
R = os.path.dirname(os.path.abspath(__file__)) + "/../"
lit = lambda f: gzip.open(f, "rt", encoding="utf-8") if f.endswith(".gz") else open(f, encoding="utf-8")
info = {r["Id"]: r for r in csv.DictReader(open(R + "resultats_usage/noeuds.csv", encoding="utf-8"))}
cache = {}
for f in sorted(glob.glob(R + "resultats_usage/cache*.jsonl*")):
    for l in lit(f):
        if l.strip(): e = json.loads(l); cache[e["q"]] = e
vues = collections.Counter()
for f in glob.glob(R + "resultats_usage_wikipedia*/vues_mensuelles.csv"):
    for r in csv.DictReader(open(f, encoding="utf-8")): vues[r["mot"]] += int(r["vues"])
anc, rec = collections.Counter(), collections.Counter()
for f in glob.glob(R + "resultats_usage_ngram*/frequences.csv*"):
    for r in csv.reader(lit(f)):
        if not r[1].isdigit(): continue
        y = int(r[1])
        if y < 1850: anc[r[0]] += float(r[2])
        elif y >= 1970: rec[r[0]] += float(r[2])
val, conc = collections.defaultdict(list), {}
wb = openpyxl.load_workbook(R + "resultats_normes/brut/bonin2018_concretude_valence_1659_annexe3.xlsx", read_only=True)
for r in list(wb.worksheets[0].iter_rows(values_only=True))[2:]:
    if r[0] and r[2] is not None: w = str(r[0]).strip().lower(); conc[w] = round((float(r[2]) - 1) / 4, 2); val[w].append((float(r[6]) - 1) / 4)
wb = openpyxl.load_workbook(R + "resultats_normes/brut/fan2014_normes_affectives_annexe2.xlsx", read_only=True)
for r in list(wb.worksheets[0].iter_rows(values_only=True))[3:]:
    if r[0] and isinstance(r[4], (int, float)): val[str(r[0]).strip().lower()].append((float(r[4]) - 1) / 6)
cn = collections.defaultdict(lambda: collections.defaultdict(list))
for f in sorted(glob.glob(R + "resultats_conceptnet_dump/aretes_liste_*.csv.gz")):
    for r in csv.DictReader(lit(f)):
        if r["langue_autre"] == "fr" and r["relation"] in ("Synonym", "Antonym", "IsA", "PartOf") and r["sens"] == "sortant":
            if len(cn[r["mot"]][r["relation"]]) < 8 and r["autre"] not in cn[r["mot"]][r["relation"]]: cn[r["mot"]][r["relation"]].append(r["autre"])
os.makedirs(R + "cartes", exist_ok=True)
with gzip.open(R + "cartes/base_mots.csv.gz", "wt", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["mot", "rang_usage", "categorie", "freq_films", "freq_livres", "oral_ecrit", "durand", "connu_jdm", "vues_wikipedia",
                "freq_1800_1849", "freq_1970_2019", "valence", "concretude", "associations_jdm", "synonymes", "contraires", "est_une_sorte_de", "partie_de"])
    for m, i in sorted(info.items(), key=lambda x: int(x[1]["rang"] or 10**6)):
        e = cache.get(m, {}); ass = sorted(e.get("in", []) + e.get("out", []), key=lambda x: -x[1])[:15]
        c = cn.get(m, {})
        w.writerow([m, i["rang"], i["categorie"], i["freq_films"], i["freq_livres"], i["oral_ecrit"], i["durand"], int(bool(e.get("trouve"))), vues.get(m, 0),
                    f"{anc[m]:.3g}" if anc[m] else "", f"{rec[m]:.3g}" if rec[m] else "", round(sum(val[m]) / len(val[m]), 2) if val.get(m) else "", conc.get(m, ""),
                    " | ".join(f"{a}:{int(p)}" for a, p in ass), " | ".join(c.get("Synonym", [])), " | ".join(c.get("Antonym", [])), " | ".join(c.get("IsA", [])), " | ".join(c.get("PartOf", []))])
print(len(info), "mots dans la base de référence")

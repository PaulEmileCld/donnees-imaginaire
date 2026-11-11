"""Fréquentation quotidienne des articles de Wikipédia en français (depuis juillet 2015), pour chaque mot de Durand."""
import json, os, time, csv, gzip, datetime, urllib.request, urllib.parse
from commun import UA, mots_accentues
R = "resultats_wikipedia"; os.makedirs(R, exist_ok=True)
def get(url):
    for essai in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(5 * (essai + 1))
        except Exception: time.sleep(5 * (essai + 1))
    return None
mots = mots_accentues(); titres = {}
for i in range(0, len(mots), 40):        # 1. retrouver le titre réel de l'article (redirections, homonymies)
    lot = mots[i:i + 40]
    q = "|".join(f[0].upper() + f[1:] for _, f in lot)
    d = get("https://fr.wikipedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "titles": q, "redirects": 1,
        "prop": "pageprops", "ppprop": "disambiguation", "format": "json", "formatversion": 2}))
    norm_map = {x["from"]: x["to"] for x in (d or {}).get("query", {}).get("normalized", [])}
    redir = {x["from"]: x["to"] for x in (d or {}).get("query", {}).get("redirects", [])}
    pages = {p["title"]: p for p in (d or {}).get("query", {}).get("pages", [])}
    for m, f in lot:
        t = f[0].upper() + f[1:]; t = norm_map.get(t, t); t = redir.get(t, t); p = pages.get(t, {})
        titres[m] = {"forme": f, "titre": t, "existe": "missing" not in p and bool(p),
                     "homonymie": "disambiguation" in p.get("pageprops", {})}
    time.sleep(1)
fin = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
lignes, mensuel = [], {}
for m, info in titres.items():               # 2. fréquentation quotidienne (visiteurs humains seulement)
    if not info["existe"]: continue
    t = urllib.parse.quote(info["titre"].replace(" ", "_"), safe="")
    d = get(f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/fr.wikipedia/all-access/user/{t}/daily/2015070100/{fin}00")
    for it in (d or {}).get("items", []):
        jour = it["timestamp"][:8]; lignes.append([info["forme"], jour, it["views"]])
        mensuel[(info["forme"], jour[:6])] = mensuel.get((info["forme"], jour[:6]), 0) + it["views"]
    time.sleep(0.3)
with gzip.open(f"{R}/vues_quotidiennes.csv.gz", "wt", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["mot", "jour", "vues"]); w.writerows(lignes)
with open(f"{R}/vues_mensuelles.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["mot", "mois", "vues"]); w.writerows([[a, b, v] for (a, b), v in sorted(mensuel.items())])
json.dump(titres, open(f"{R}/titres.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
etat = {"mots": len(titres), "articles": sum(i["existe"] for i in titres.values()),
        "homonymies": sum(i["homonymie"] for i in titres.values()), "lignes": len(lignes)}
json.dump(etat, open(f"{R}/etat.json", "w"), indent=1); print(etat)

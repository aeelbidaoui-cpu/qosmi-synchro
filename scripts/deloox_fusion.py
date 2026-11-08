#!/usr/bin/env python3
"""Fusionne un relevé Deloox (export de window.__dl.res) dans config/deloox.json — fichier INTERNE, ne sort jamais du dépôt.
Ne garde que les résultats dont le code-barres de la fiche trouvée est bien l'EAN cherché.
Un EAN cherché mais plus trouvé chez Deloox est retiré (sinon on garderait un vieux prix).
Usage : python3 scripts/deloox_fusion.py <relevé.json> [AAAA-MM-JJ]   — n'affiche que des comptes, jamais de prix."""
import datetime, json, os, sys
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN = os.path.join(RACINE, "config", "deloox.json")
rel = json.load(open(sys.argv[1]))
date = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().isoformat()
d = json.load(open(CHEMIN))
pe = d["par_ean"]
n = {"maj": 0, "nouveaux": 0, "retirés": 0, "écartés (autre EAN)": 0, "prix changés": 0}
for ean, v in rel.items():
    cle = ean.lstrip("0")
    if not v or not v[1]:
        if cle in pe:
            del pe[cle]
            n["retirés"] += 1
        continue
    if (v[0] or "").lstrip("0") != cle:
        n["écartés (autre EAN)"] += 1
        pe.pop(cle, None)
        continue
    a = v[2] or ""
    dispo = "InStock" if "InStock" in a else ("OutOfStock" if "OutOfStock" in a else a.replace("\\", "").rsplit("/", 1)[-1])
    ancien = pe.get(cle)
    if ancien is None:
        n["nouveaux"] += 1
    elif abs(float(ancien[0]) - float(v[1])) > 0.004:
        n["prix changés"] += 1
    pe[cle] = [float(v[1]), dispo, date]
    n["maj"] += 1
d["maj"] = date
json.dump(d, open(CHEMIN, "w"), ensure_ascii=False, separators=(",", ":"))
print("Relevé Deloox fusionné :", ", ".join("%s %d" % kv for kv in n.items()), "· total", len(pe))

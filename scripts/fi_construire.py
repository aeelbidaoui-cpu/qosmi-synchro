#!/usr/bin/env python3
"""Construit, à partir des relevés Fragrance Index (13/11/2026, accord obtenu par Amine) :
  - config/profils_parfums.json : profil de chaque fiche (saison, tenue, sillage, occasions, pyramide FR/NL) → scripts/fi_profils.py ;
  - config/notes_fi.json : notes FR/NL des parfums absents de config/descriptions_parfums.json → index des odeurs (scripts/odeurs.py).
Les notes déjà vérifiées de descriptions_parfums.json sont gardées telles quelles. Une note anglaise sans traduction
(scripts/notes_traductions.py) est laissée de côté et listée.

  python3 scripts/fi_construire.py <dossier des relevés qosmi-fi-*.json> [rapprochements validés à la main.json]
"""
import collections, glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notes_traductions import traduire

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAISON = {"spring": "printemps", "summer": "ete", "autumn": "automne", "fall": "automne", "winter": "hiver"}
TENUE = {"light wear": "legere", "short-lived": "legere", "moderate": "moyenne", "moderate wear": "moyenne", "long-lasting": "longue", "fleeting": "legere",
         "all-day wear": "journee", "into the next day": "lendemain"}
SILLAGE = {"intimate": "discret", "soft": "discret", "light": "discret", "moderate": "modere", "strong": "fort",
           "enormous": "tres_fort", "very strong": "tres_fort", "heavy": "tres_fort", "powerful": "tres_fort"}
OCC = {"everyday": "quotidien", "office": "bureau", "date night": "rdv", "dinner out": "diner", "club & party": "soiree",
       "wedding": "mariage", "gym": "sport", "sport": "sport", "beach": "vacances", "vacation": "vacances", "holiday": "vacances",
       "formal": "chic", "gala": "chic", "black tie": "chic", "lounge": "detente", "relaxing": "detente", "casual": "quotidien",
       "interview": "bureau", "travel": "vacances", "yoga": "detente", "bedtime": "detente"}


def main(dossier, valides=None):
    R = []
    for f in sorted(glob.glob(os.path.join(dossier, "qosmi-fi-[0-9]*.json"))):
        R += json.load(open(f, encoding="utf-8"))
    ok1 = set(json.load(open(valides))) if valides else set()
    D = json.load(open(os.path.join(RACINE, "config", "descriptions_parfums.json"), encoding="utf-8"))["parfums"]
    inconnues, inc_val = collections.Counter(), collections.Counter()
    profils, notes_fi, n2, n1 = {}, {}, 0, 0
    for r in R:
        d = r.get("d")
        if not d or not (r.get("ok") == 2 or (r.get("ok") == 1 and d.get("slug") in ok1)):
            continue
        n2 += r["ok"] == 2; n1 += r["ok"] == 1
        p = {}
        s = [SAISON.get(d.get("saison") or "")] + [SAISON.get(d.get("saison_com") or "")]
        s = [x for i, x in enumerate(s) if x and x not in s[:i]]
        if s: p["s"] = s
        if d.get("tenue"):
            if d["tenue"] in TENUE: p["t"] = TENUE[d["tenue"]]
            else: inc_val["tenue:" + d["tenue"]] += 1
        if d.get("sillage"):
            if d["sillage"] in SILLAGE: p["si"] = SILLAGE[d["sillage"]]
            else: inc_val["sillage:" + d["sillage"]] += 1
        occ = []
        for k, v in sorted((d.get("occasions") or {}).items(), key=lambda x: -x[1]):
            if k not in OCC:
                inc_val["occasion:" + k] += 1
                continue
            if v >= 55 and OCC[k] not in occ:
                occ.append(OCC[k])
        if occ: p["o"] = occ[:3]
        # pyramide FI traduite
        def tr(liste):
            fr, nl = [], []
            for n in [x.strip() for x in (liste or "").split(",") if x.strip()]:
                t = traduire(n)
                if not t:
                    inconnues[n.lower()] += 1
                    continue
                if t[0] not in fr:
                    fr.append(t[0]); nl.append(t[1])
            return fr, nl
        pyr = {k: tr(d.get(c)) for k, c in (("t", "tete"), ("c", "coeur"), ("f", "fond"))}
        plat = tr(d.get("notes"))
        for h in r["h"]:
            q = dict(p)
            v = D.get(h)
            if v and (v.get("notes_fr") or {}).get("tete"):  # notes vérifiées à la main : prioritaires
                nf, nn = v["notes_fr"], v["notes_nl"]
                q["nf"] = {"t": nf.get("tete", []), "c": nf.get("coeur", []), "f": nf.get("fond", [])}
                q["nn"] = {"t": nn.get("tete", []), "c": nn.get("coeur", []), "f": nn.get("fond", [])}
            elif any(pyr[k][0] for k in pyr):
                q["nf"] = {k: pyr[k][0] for k in pyr if pyr[k][0]}
                q["nn"] = {k: pyr[k][1] for k in pyr if pyr[k][1]}
                notes_fi[h] = {"notes_fr": {"tete": pyr["t"][0], "coeur": pyr["c"][0], "fond": pyr["f"][0]},
                               "notes_nl": {"tete": pyr["t"][1], "coeur": pyr["c"][1], "fond": pyr["f"][1]}}
            elif plat[0]:
                q["nf"], q["nn"] = {"n": plat[0]}, {"n": plat[1]}
                notes_fi[h] = {"notes_fr": {"tete": [], "coeur": plat[0], "fond": []}, "notes_nl": {"tete": [], "coeur": plat[1], "fond": []}}
            if len(q) > 0:
                profils[h] = q
    src = "Fragrance Index (fragranceindex.ai), accord obtenu par Amine le 13/11/2026 ; notes vérifiées de descriptions_parfums.json prioritaires."
    json.dump({"source": src, "parfums": profils}, open(os.path.join(RACINE, "config", "profils_parfums.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    json.dump({"source": src, "parfums": notes_fi}, open(os.path.join(RACINE, "config", "notes_fi.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    print("relevés : %d (sûrs : %d, validés à la main : %d)" % (len(R), n2, n1))
    print("profils : %d fiches · nouvelles notes : %d fiches" % (len(profils), len(notes_fi)))
    print("notes sans traduction :", inconnues.most_common(80), "· total", len(inconnues))
    print("valeurs inconnues :", inc_val.most_common(30))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)

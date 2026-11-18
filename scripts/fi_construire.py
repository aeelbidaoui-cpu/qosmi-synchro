#!/usr/bin/env python3
"""Construit, à partir des relevés Fragrance Index (13/11/2026, accord obtenu par Amine) :
  - config/profils_parfums.json : profil de chaque fiche (saison, tenue, sillage, occasions, pyramide FR/NL) → scripts/fi_profils.py ;
  - config/notes_fi.json : notes FR/NL des parfums absents de config/descriptions_parfums.json → index des odeurs (scripts/odeurs.py).
Les notes déjà vérifiées de descriptions_parfums.json sont gardées telles quelles. Une note anglaise sans traduction
(scripts/notes_traductions.py) est laissée de côté et listée.

  python3 scripts/fi_construire.py <dossier des relevés qosmi-fi-*.json> [rapprochements validés à la main.json | -] [adresses des fiches du site.json]
"""
import collections, glob, json, os, re, sys

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


# accords Fragrance Index (anglais) → code (clé de libellé, voir ACCORDS_LIB) ; plusieurs accords proches peuvent partager un code
ACCORDS = {k: (v,) for k, v in {
    "aldehydic": "aldehyde", "almond": "amande", "amber": "ambre", "animalic": "animal", "aquatic": "aquatique", "aromatic": "aromatique",
    "balsamic": "balsamique", "boozy": "alcool", "caramel": "caramel", "chocolate": "chocolat", "cinnamon": "cannelle", "citrus": "agrumes",
    "coconut": "coco", "coffee": "cafe", "earthy": "terreux", "floral": "floral", "fresh": "frais", "fresh spicy": "epice_frais",
    "fruity": "fruite", "gourmand": "gourmand", "green": "vert", "honey": "miel", "iris": "iris", "jasmine": "jasmin", "lactonic": "lacte",
    "lavender": "lavande", "leather": "cuir", "mossy": "mousse", "muguet": "muguet", "musky": "musque", "nutty": "noisette", "oud": "oud",
    "ozonic": "ozonique", "patchouli": "patchouli", "peach": "peche", "pistachio": "pistache", "powdery": "poudre", "rose": "rose",
    "smoky": "fume", "soft spicy": "epice_doux", "sweet": "sucre", "tea": "the", "tobacco": "tabac", "tropical": "tropical",
    "tuberose": "tubereuse", "vanilla": "vanille", "violet": "violette", "warm spicy": "epice_chaud", "white floral": "fleurs_blanches",
    "woody": "boise", "yellow floral": "fleurs_jaunes", "citrusy": "agrumes", "spicy": "epice_chaud", "fruity sweet": "fruite",
    # accords Fragrantica absents de Fragrance Index (17/11/2026)
    "herbal": "aromatique", "cherry": "fruite", "rum": "alcool", "whiskey": "alcool", "cacao": "chocolat", "conifer": "boise",
    "beeswax": "miel", "fresh fruity": "fruite", "citrus fresh": "agrumes"}.items()}
VIBES = {"cozy", "sensual", "elegant", "energetic", "romantic", "calm", "playful", "fresh", "bold", "mysterious"}


def main(dossier, valides=None, site=None):
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
        if s: p["s"] = sorted(s, key=["printemps", "ete", "automne", "hiver"].index)
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
        # 17/11/2026 (demande d'Amine : « prends toutes les infos utiles ») : année, parfumeur, accords et ambiances
        if re.fullmatch(r"(19|20)\d\d", str(d.get("annee") or "")): p["a"] = int(d["annee"])
        pf = [x.strip() for v in (d.get("parfumeur") or []) for x in re.split(r",| and ", v) if x.strip()]
        if pf: p["pf"] = pf[:3]
        acc = d.get("accords") or {}
        acc = [k for k, _ in sorted(acc.items(), key=lambda x: -x[1])] if isinstance(acc, dict) else list(acc)
        acc = acc or list(d.get("accords_liste") or [])
        ac = [ACCORDS[k][0] for k in acc if k in ACCORDS]
        ac = [x for i, x in enumerate(ac) if x not in ac[:i]]
        for k in acc:
            if k not in ACCORDS: inc_val["accord:" + k] += 1
        if ac: p["ac"] = ac[:5]
        vb = [k for k, v in sorted((d.get("vibes") or {}).items(), key=lambda x: -x[1]) if k in VIBES and v > 0]
        if vb: p["v"] = vb[:3]
        # pyramide FI traduite
        def tr(liste):
            fr, nl = [], []
            for n in [x.strip() for x in (liste or "").split(",") if x.strip()]:
                t = traduire(n)
                if not t:
                    inconnues[n.lower()] += 1
                    continue
                t = tuple(x[:1].upper() + x[1:] for x in t)  # « Cerise noire », comme les notes vérifiées des fiches
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
                # 18/11/2026 : une fiche relevée deux fois (Fragrance Index puis le site de la marque) : on complète, sans écraser
                profils[h] = {**q, **profils[h]} if h in profils else q
    if site:  # 17/11/2026 : fiches dont l'adresse a changé (doublons réunis, « -2 ») : même parfum, même profil
        norm = lambda h: re.sub(r"-(pour-homme|pour-femme|mixte|pour-enfant)$", "", re.sub(r"-\d+$", "", h))
        par_norm = {}
        for h in profils:
            par_norm.setdefault(norm(h), h)
        ajout = 0
        for h in json.load(open(site, encoding="utf-8")):
            if h not in profils and norm(h) in par_norm:
                profils[h] = profils[par_norm[norm(h)]]
                if par_norm[norm(h)] in notes_fi:
                    notes_fi[h] = notes_fi[par_norm[norm(h)]]
                ajout += 1
        print("profils repris pour des fiches à nouvelle adresse :", ajout)
    src = ("Fragrance Index (fragranceindex.ai), accord obtenu par Amine le 13/11/2026 ; Fragrantica (fragrantica.com) pour les parfums absents "
           "de Fragrance Index, accord obtenu par Amine le 10/11/2026 ; notes vérifiées de descriptions_parfums.json prioritaires.")
    json.dump({"source": src, "parfums": profils}, open(os.path.join(RACINE, "config", "profils_parfums.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    json.dump({"source": src, "parfums": notes_fi}, open(os.path.join(RACINE, "config", "notes_fi.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    print("relevés : %d (sûrs : %d, validés à la main : %d)" % (len(R), n2, n1))
    print("profils : %d fiches · nouvelles notes : %d fiches" % (len(profils), len(notes_fi)))
    print("notes sans traduction :", inconnues.most_common(80), "· total", len(inconnues))
    print("valeurs inconnues :", inc_val.most_common(30))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None, sys.argv[3] if len(sys.argv) > 3 else None)

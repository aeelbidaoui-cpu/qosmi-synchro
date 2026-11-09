#!/usr/bin/env python3
"""Fiches produit bol incomplètes (demande d'Amine du 09/11/2026).

bol rend invisibles certaines de nos offres parce que la FICHE PRODUIT (commune à tous les vendeurs) est incomplète :
ingrédients, contenu « cosmétiques », informations essentielles, adresse fournisseur.

--diag : pour chaque EAN concerné (rapports/bol_invisibles.json, écrit par bol_publier.py), lit la fiche bol
         (GET /retailer/content/catalog-products/{ean}) et écrit rapports/bol_contenu_diag.json :
         attributs présents, attributs vides, raisons d'invisibilité. Rien n'est envoyé à bol.

Règle d'Amine : l'adresse fournisseur est TOUJOURS celle de Deway BV, jamais celle du fournisseur réel.
"""
import json, os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.dirname(ICI)
RAPPORTS = os.path.join(RACINE, "rapports")
CONTENU = ("4004", "3001")  # informations essentielles / attributs (ingrédients, cosmétiques, adresse fournisseur)


def diag():
    from bol_api import Bol
    inv = json.load(open(os.path.join(RAPPORTS, "bol_invisibles.json"), encoding="utf-8"))
    raisons = {}
    for cle, eans in inv.items():
        for e in eans:
            raisons.setdefault(e, []).append(cle)
    cibles = sorted(e for e, r in raisons.items() if any(x.startswith(CONTENU) for x in r))
    print("EAN avec un problème de fiche : %d" % len(cibles))
    bol = Bol()
    from bol_publier import offres_en_ligne
    offres = offres_en_ligne(bol)
    out = {}
    for e in cibles:
        o = offres.get(e.lstrip("0")) or {}
        completes = []
        if o.get("offerId"):
            completes = (bol.appel("GET", "/retailer/offers/%s" % o["offerId"]) or {}).get("notPublishableReasons") or []
        ean = e.zfill(13)
        fiche = None
        for params in ({"language": "nl"}, None):
            try:
                fiche = bol.appel("GET", "/retailer/content/catalog-products/%s" % ean, params=params)
            except RuntimeError as ex:
                fiche = {"erreur": str(ex)[:300]}
            if fiche:
                break
        out[ean] = {"raisons": raisons[e], "raisons_completes": completes, "fiche": fiche}
        attrs = (fiche or {}).get("attributes") or []
        print("%s : %d attributs · %s" % (ean, len(attrs), " | ".join(r[:40] for r in raisons[e])))
    os.makedirs(RAPPORTS, exist_ok=True)
    with open(os.path.join(RAPPORTS, "bol_contenu_diag.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("Rapport : rapports/bol_contenu_diag.json (%d fiches, %d appels)" % (len(out), bol.appels))


if __name__ == "__main__":
    if "--diag" in sys.argv:
        diag()
    else:
        print(__doc__)

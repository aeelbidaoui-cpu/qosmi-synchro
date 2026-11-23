#!/usr/bin/env python3
"""Rayon skincare (demande d'Amine du 23/11/2026 : « crée une page skincare et poste tout ce qu'on peut avoir chez nos
fournisseurs »).

  python3 scripts/skincare.py --apercu   → combien de soins chez les grossistes, par rubrique et par marque (journal)

Le dépôt est public : le journal ne montre que des nombres et des noms de marques (aucun prix d'achat, aucun fournisseur).
"""
import collections
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

RUBRIQUES = ["Soins du visage", "Soins du corps", "Solaires et autobronzants"]
VOISINES = ["Cheveux", "Déodorants", "Homme", "Maquillage", "Maison", "Soins et beauté"]


def en_stock(p):
    for v in p.get("variantes") or []:
        try:
            if float(v.get("stock") or 0) > 0:
                return True
        except (TypeError, ValueError):
            pass
    return False


def apercu():
    import site_synchro as ss
    import site_variantes as sv
    if os.environ.get("SOLELUNA_EMAIL"):
        ss.listes_serveur()
    produits = sv.preparer(exemples=False)
    sel = ss.selection()
    par_rub = collections.defaultdict(list)
    for p in produits:
        if p.get("type_fr") in RUBRIQUES + VOISINES:
            par_rub[p["type_fr"]].append(p)
    print("=== Soins et beauté chez les grossistes (fiches, en stock, avec bonne photo, ingrédient interdit)")
    for rub in RUBRIQUES + VOISINES:
        g = par_rub.get(rub, [])
        interdit = sum(1 for p in g if any(str(v.get("ean", "")).lstrip("0") in ss.INTERDITS for v in p.get("variantes", [])))
        print("%-28s %5d fiches | %5d en stock | %5d photo ok | %5d en stock + photo ok | %d interdits"
              % (rub, len(g), sum(en_stock(p) for p in g), sum(bool(p.get("photo_ok", True)) for p in g),
                 sum(en_stock(p) and p.get("photo_ok", True) for p in g), interdit))
    print()
    for rub in RUBRIQUES:
        c = collections.Counter(p["marque"] for p in par_rub.get(rub, []) if en_stock(p))
        print("=== %s : marques (fiches en stock)" % rub)
        print(", ".join("%s %d" % (m, n) for m, n in c.most_common()))
        print()
    g = [p for r in RUBRIQUES for p in par_rub.get(r, []) if en_stock(p)]
    print("=== Exemples (20 premiers en stock)")
    for p in g[:20]:
        print("  ", p["titre_fr"], "| photo ok" if p.get("photo_ok", True) else "| sans bonne photo")
    print("Total skincare en stock :", len(g), "| déjà visibles avec la sélection actuelle :",
          sum(1 for p in g if ss.visible(p, sel)))


if __name__ == "__main__":
    if "--apercu" in sys.argv:
        apercu()

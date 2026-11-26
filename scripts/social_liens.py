#!/usr/bin/env python3
"""Vérifie les parfums cités dans les publications à venir (demande d'Amine du 26/11/2026 : « quand on parle d'un produit
dans un post, ajoute le lien »).

Pour chaque fiche citée (champ « produits » des lots) : est-elle active et en ligne sur qosmi.be ? Sinon, cherche la
fiche active et en ligne du même nom (après un réimport, l'adresse change souvent : « …-2 »). Lecture seule : imprime
le rapport et une table de remplacement JSON (ancienne adresse → nouvelle).
"""
import json, os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from shopify_api import Shopify  # noqa: E402
import social_publier as sp  # noqa: E402

CHAMPS = "handle title status onlineStoreUrl totalInventory"


def fiche(s, handle):
    d = s.gql('query($q: String!) { products(first: 3, query: $q) { nodes { %s } } }' % CHAMPS, {"q": "handle:" + handle})
    return next((p for p in d["products"]["nodes"] if p["handle"] == handle), None)


def jumelle(s, titre):
    q = 'title:"%s" status:active' % titre.replace('"', '')
    d = s.gql('query($q: String!) { products(first: 10, query: $q) { nodes { %s } } }' % CHAMPS, {"q": q})
    ok = [p for p in d["products"]["nodes"] if p["title"].strip().lower() == titre.strip().lower()
          and p["status"] == "ACTIVE" and p["onlineStoreUrl"]]
    return sorted(ok, key=lambda p: -(p["totalInventory"] or 0))


def main():
    s = Shopify()
    etat, lots = sp.lire_etat(), sp.charger_lots()
    venir = [p for p in lots if p["id"] not in etat]
    handles = sorted({h for p in venir for h in p.get("produits") or []})
    print("%d publications à venir, %d parfums cités" % (len(venir), len(handles)))
    table, sans = {}, []
    for h in handles:
        f = fiche(s, h)
        if f and f["status"] == "ACTIVE" and f["onlineStoreUrl"]:
            continue
        etat_f = "introuvable" if not f else "%s, %s" % (f["status"], "en ligne" if f["onlineStoreUrl"] else "pas en ligne")
        cand = jumelle(s, f["title"]) if f else []
        if cand:
            table[h] = cand[0]["handle"]
            print("REMPLACER %s (%s) → %s  [%s, stock %s]" % (h, etat_f, cand[0]["handle"], cand[0]["title"], cand[0]["totalInventory"]))
        else:
            sans.append(h)
            print("SANS FICHE EN LIGNE %s (%s)%s" % (h, etat_f, (" — " + f["title"]) if f else ""))
    print("TABLE " + json.dumps(table, ensure_ascii=False))
    print("SANS " + json.dumps(sans, ensure_ascii=False))


if __name__ == "__main__":
    main()

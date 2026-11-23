#!/usr/bin/env python3
"""Doublons de code-barres pour Google (23/11/2026, demande d'Amine : « tu mets le bon plan et tu fais de même pour
tous les autres produits »).

Un format normal et son « Bon plan » ont le même EAN : Google risque de les prendre pour le même produit à deux prix.
Pour chaque EAN présent sur plusieurs formats en ligne, on garde UN format pour Google :
  - celui qui est en stock ;
  - si les deux sont en stock (ou aucun) : le Bon plan s'il est en stock, sinon le format normal.
Les autres sont à masquer dans Merchant Center (« Don't show on Google »). Les fiches qui n'existent qu'en Bon plan
ne sont jamais touchées.

  python3 scripts/doublons_ean.py   → rapports/theme/google_masquer.json {"masquer": [id Merchant Center], "garder": [...]}
"""
import collections, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import Shopify

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q = """query($a: String) { products(first: 100, after: $a, query: "status:active") { pageInfo { hasNextPage endCursor }
  nodes { id handle variants(first: 50) { nodes { id title barcode inventoryQuantity inventoryPolicy } } } } }"""


def num(gid):
    return gid.rsplit("/", 1)[-1]


def main():
    s = Shopify()
    par_ean = collections.defaultdict(list)
    a = None
    while True:
        d = s.gql(Q, {"a": a})["products"]
        for p in d["nodes"]:
            for v in p["variants"]["nodes"]:
                e = (v.get("barcode") or "").strip().lstrip("0")
                if e:
                    par_ean[e].append({"pid": num(p["id"]), "vid": num(v["id"]), "handle": p["handle"], "titre": v["title"],
                                       "bon_plan": "Bon plan" in (v["title"] or ""),
                                       "stock": (v.get("inventoryQuantity") or 0) > 0})
        if not d["pageInfo"]["hasNextPage"]:
            break
        a = d["pageInfo"]["endCursor"]
    masquer, garder, n = [], [], 0
    for e, vs in par_ean.items():
        if len(vs) < 2:
            continue
        n += 1
        en_stock = [v for v in vs if v["stock"]]
        bp = [v for v in en_stock if v["bon_plan"]]
        if bp:
            g = bp[0]
        elif en_stock:
            g = en_stock[0]
        else:
            g = next((v for v in vs if not v["bon_plan"]), vs[0])
        garder.append("shopify_ZZ_%s_%s" % (g["pid"], g["vid"]))
        masquer += ["shopify_ZZ_%s_%s" % (v["pid"], v["vid"]) for v in vs if v is not g]
    os.makedirs(os.path.join(RACINE, "rapports", "theme"), exist_ok=True)
    json.dump({"masquer": masquer, "garder": garder}, open(os.path.join(RACINE, "rapports", "theme", "google_masquer.json"), "w"))
    print("OK EAN en double : %d · formats à masquer sur Google : %d" % (n, len(masquer)))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Recherche, en lecture seule, des fiches par nom (tous statuts : actif, brouillon, archivé) avec les EAN de chaque format.
27/11/2026 (Amine : « donne-moi les EAN » des best-sellers de niche). Variable TITRES : recherches séparées par « ; »."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import Shopify
s = Shopify()
Q = """query($q: String!) { products(first: 12, query: $q) { nodes { title vendor status totalInventory
  variants(first: 10) { nodes { title barcode inventoryQuantity availableForSale } } } } }"""
for t in [x.strip() for x in (os.environ.get("TITRES") or "").split(";") if x.strip()]:
    mots = " AND ".join("title:*%s*" % m.replace('"', '').replace("'", "") for m in t.split())
    r = s.gql(Q, {"q": mots})["products"]["nodes"]
    print("### %s : %d fiche(s)" % (t, len(r)))
    for p in r:
        f = " | ".join("%s EAN %s stock %s%s" % (v["title"], v["barcode"] or "-", v["inventoryQuantity"], " en vente" if v["availableForSale"] else "")
                       for v in p["variants"]["nodes"])
        print("  [%s] %s — %s" % (p["status"], p["title"], f))

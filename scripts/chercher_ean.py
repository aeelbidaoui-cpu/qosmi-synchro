#!/usr/bin/env python3
"""Recherche, en lecture seule, d'une ou plusieurs fiches par code EAN (variable ALERTE_CLIENT / champ « fiche »)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import Shopify
s = Shopify()
for ean in (os.environ.get("ALERTE_CLIENT") or "").replace(",", " ").split():
    r = s.gql("""query($q: String!) { productVariants(first: 10, query: $q) { nodes { title barcode sku availableForSale
                 product { title handle status onlineStoreUrl } } } }""", {"q": "barcode:%s" % ean})["productVariants"]["nodes"]
    print("EAN %s : %d résultat(s)" % (ean, len(r)))
    for v in r:
        p = v["product"]
        print("  %s | %s | %s | en vente : %s | https://qosmi.be/products/%s?variant=" % (p["title"], v["title"], p["status"], v["availableForSale"], p["handle"]))

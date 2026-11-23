#!/usr/bin/env python3
"""23/11/2026 (Amine : « désactive la skincare ») : repasse en brouillon les soins encore en ligne (visage, corps,
solaires, huiles parfumées) que la mise à jour du site ne touche plus (fiches absentes des listes des grossistes).
Brouillon = masqué, jamais supprimé."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import Shopify

TYPES = ["Soins du visage", "Soins du corps", "Solaires et autobronzants", "Huiles parfumées"]
s = Shopify()
q = " OR ".join('product_type:"%s"' % t for t in TYPES)
ids, a = [], None
while True:
    d = s.gql("""query($q: String!, $a: String) { products(first: 100, after: $a, query: $q) { pageInfo { hasNextPage endCursor }
                 nodes { id handle } } }""", {"q": "status:active AND (%s)" % q, "a": a})["products"]
    ids += [(n["id"], n["handle"]) for n in d["nodes"]]
    if not d["pageInfo"]["hasNextPage"]:
        break
    a = d["pageInfo"]["endCursor"]
ok = 0
for pid, h in ids:
    r = s.gql("mutation($p: ProductUpdateInput!) { productUpdate(product: $p) { userErrors { message } } }",
              {"p": {"id": pid, "status": "DRAFT"}})["productUpdate"]
    ok += not r["userErrors"]
    print("  brouillon :", h, r["userErrors"] or "ok")
print("OK soins repassés en brouillon : %d / %d" % (ok, len(ids)))
